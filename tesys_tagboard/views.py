from typing import TYPE_CHECKING
from typing import Any

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse

from .components.add_tagset.add_tagset import AddTagsetComponent
from .components.comment.comment import CommentComponent
from .components.favorite_toggle.favorite_toggle import FavoriteToggleComponent
from .decorators import require
from .enums import SupportedMediaTypes
from .enums import TagCategory
from .forms import AddCommentForm
from .forms import CreateCollectionForm
from .forms import CreateTagAliasForm
from .forms import CreateTagForm
from .forms import EditCommentForm
from .forms import EditPostForm
from .forms import PostForm
from .forms import PostSearchForm
from .forms import TagsetForm
from .models import Collection
from .models import Comment
from .models import Favorite
from .models import Image
from .models import Media
from .models import Post
from .models import Tag
from .models import TagAlias
from .search import PostSearch
from .search import tag_autocomplete

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models import QuerySet
    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@require(["GET"], login=False)
def home(request: HttpRequest) -> TemplateResponse:
    context = {}
    return TemplateResponse(request, "pages/home.html", context)


@require(["GET", "POST"], login=False)
def post(request: HtmxHttpRequest, post_id: int) -> TemplateResponse:
    posts = Post.objects.filter(pk=post_id).select_related("uploader")
    if request.user.is_authenticated:
        favorites = Favorite.objects.for_user(request.user)
        posts = posts.annotate_favorites(favorites)
    post = get_object_or_404(posts)
    comments = post.comment_set.order_by("-post_date").select_related("user")

    comments_pager = Paginator(comments, 10, 5)
    comments_page_num = request.GET.get("page", 1)
    comments_page = comments_pager.get_page(comments_page_num)
    tags = Tag.objects.for_post(post)
    post_edit_url = reverse("post-edit", args=[post.pk])
    context = {
        "post": post,
        "tags": tags,
        "comments_pager": comments_pager,
        "comments_page": comments_page,
        "post_edit_url": post_edit_url,
    }
    return TemplateResponse(request, "pages/post.html", context)


@require(["POST"])
def edit_post(
    request: HtmxHttpRequest, post_id: int
) -> TemplateResponse | HttpResponse:
    post = get_object_or_404(Post.objects.filter(pk=post_id))
    data: dict[str, str | list[Any] | None] = {
        key: request.POST.get(key) for key in request.POST
    }
    data["tagset"] = request.POST.getlist("tagset")

    form = EditPostForm(data)
    if form.is_valid():
        if title := form.cleaned_data.get("title"):
            post.title = title
            post.save()
            return HttpResponse(post.title, status=200)

        if src_url := form.cleaned_data.get("src_url"):
            post.media.src_url = src_url
            post.media.save()
            return HttpResponse(post.media.src_url, status=200)

        if rating_level := form.cleaned_data.get("rating_level"):
            post.rating_level = rating_level
            post.save()
            return HttpResponse(post.rating_level, status=200)

        if tagset := form.cleaned_data.get("tagset"):
            tags = Tag.objects.in_tagset(tagset)
            post.tags.set(tags)
            post.save()
            kwargs = {
                "size": "small",
                "tags": tags,
                "add_tag_enabled": True,
                "post": post,
            }

            return AddTagsetComponent.render_to_response(request=request, kwargs=kwargs)

        return HttpResponse(status=200)
    return HttpResponse(status=422)


@require(["DELETE"])
def delete_post(
    request: HtmxHttpRequest, post_id: int
) -> TemplateResponse | HttpResponse:
    try:
        post = Post.objects.get(pk=post_id, uploader=request.user)
        post.delete()
        return redirect(reverse("posts"))

    except Post.DoesNotExist:
        return HttpResponseNotFound("That post doesn't exist")


@require(["GET", "POST"], login=False)
def posts(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    posts = Post.objects.with_gallery_data()
    if request.user.is_authenticated:
        favorites = Favorite.objects.for_user(request.user)
        posts = posts.annotate_favorites(favorites)
    tags: QuerySet[Tag] | None = None

    if request.GET:
        if tag := request.GET.get("tag"):
            tags = Tag.objects.in_tagset([tag])
            posts = posts.has_tags(tags)

    elif request.POST:
        data: dict[str, str | list[Any] | None] = {
            key: request.POST.get(key) for key in request.POST
        }
        data["tagset"] = request.POST.getlist("tagset")
        form = PostSearchForm(data) if request.method == "POST" else PostForm()
        if form.is_valid():
            tagset = form.cleaned_data.get("tagset")
            tags = Tag.objects.in_tagset(tagset)
            posts = posts.has_tags(tags)

    pager = Paginator(posts, 32, 4)
    page_num = request.GET.get("page", 1)
    page = pager.get_page(page_num)
    context = {
        "posts": posts,
        "pager": pager,
        "page": page,
        "tags": tags,
    }
    return TemplateResponse(request, "pages/posts.html", context)


@require(["GET"], login=False)
def tags(request: HtmxHttpRequest) -> TemplateResponse:
    categories = TagCategory.__members__.values()
    tag_query = request.GET.get("q", "")
    tags_by_cat = {
        cat: Tag.objects.filter(category=cat.value.shortcode, name__icontains=tag_query)
        for cat in categories
    }

    aliases = TagAlias.objects.filter(name__icontains=tag_query).select_related("tag")

    context = {
        "tags": Tag.objects.order_by("name"),
        "tags_by_cat": tags_by_cat,
        "tag_name": tag_query,
        "aliases": aliases,
        "categories": categories,
    }

    if request.htmx:
        return TemplateResponse(request, "tags/tags_by_category.html", context)

    return TemplateResponse(request, "pages/tags.html", context)


@require(["POST"])
def create_tag(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    create_tag_form = CreateTagForm(request.POST)
    if create_tag_form.is_valid():
        create_tag_form.save()

    return redirect(reverse("tags"))


@require(["POST"])
def create_tag_alias(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    form = CreateTagAliasForm(request.POST)
    if form.is_valid():
        form.save()

    return redirect(reverse("tags"))


@require(["GET"], login=False)
def collections(request: HttpRequest) -> TemplateResponse:
    collections = Collection.objects.public()
    pager = Paginator(collections, 25, 5)
    page_num = request.GET.get("page", 1)
    page = pager.get_page(page_num)
    context = {
        "user": request.user,
        "collections": collections,
        "pager": pager,
        "page": page,
    }
    return TemplateResponse(request, "pages/collections.html", context)


@require(["GET"], login=False)
def collection(
    request: HtmxHttpRequest, collection_id: int
) -> TemplateResponse | HttpResponse:
    user = request.user
    collection = get_object_or_404(Collection.objects.filter(pk=collection_id))
    if user == collection.user or collection.public is True:
        posts = Post.objects.with_gallery_data().filter(
            pk__in=collection.posts.values_list("pk", flat=True)
        )
        pager = Paginator(posts, 25, 5)
        page_num = request.GET.get("page", 1)
        page = pager.get_page(page_num)
        context = {
            "user": request.user,
            "collection": collection,
            "pager": pager,
            "page": page,
        }
    else:
        raise PermissionDenied

    return TemplateResponse(request, "pages/collection.html", context)


@require(["POST"])
def create_collection(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    create_collection_form = CreateCollectionForm(request.POST)
    if create_collection_form.is_valid():
        create_collection_form.instance.user = request.user
        create_collection_form.save()

    user_url = reverse("users:detail", args=[request.user.get_username()])
    return redirect(f"{user_url}?tab=collections")


@require(["DELETE"])
def delete_collection(
    request: HtmxHttpRequest, collection_id: int
) -> TemplateResponse | HttpResponse:
    if request.htmx:
        try:
            collection = Collection.objects.get(user=request.user, pk=collection_id)
            collection.delete()
            collections = request.user.collection_set.with_gallery_data()
            context = {"collections": collections}

            return TemplateResponse(
                request, "users/user_detail.html#collection-gallery", context
            )
        except Collection.DoesNotExist:
            return HttpResponseNotFound("That collection doesn't exist")

    return redirect(reverse("collections"))


@require(["PUT"])
def add_favorite(request: HtmxHttpRequest, post_id: int) -> HttpResponse:
    try:
        post = Post.objects.get(pk=post_id)
        favorite = Favorite.objects.create(post=post, user=request.user)
        favorite.save()

        post.favorited = True
        kwargs = {"post": post}
        return FavoriteToggleComponent.render_to_response(
            request=request, kwargs=kwargs
        )
    except Post.DoesNotExist, Favorite.DoesNotExist:
        return HttpResponse(status=404)
    return HttpResponse("Not allowed", status=403)


@require(["DELETE"])
def remove_favorite(request: HtmxHttpRequest, post_id: int) -> HttpResponse:
    try:
        post = Post.objects.get(pk=post_id)
        Favorite.objects.get(post=post, user=request.user).delete()

        kwargs = {"post": post}
        return FavoriteToggleComponent.render_to_response(
            request=request, kwargs=kwargs
        )
    except Post.DoesNotExist, Favorite.DoesNotExist:
        return HttpResponse(status=404)
    return HttpResponse("Not allowed", status=403)


@require(["POST"])
def add_post_to_collection(
    request: HtmxHttpRequest, collection_id: int
) -> HttpResponse:
    if request.htmx:
        try:
            collection = Collection.objects.get(user=request.user, pk=collection_id)
            post = Post.objects.get(pk=request.POST.get("post"))
            collection.posts.add(post)
            collection.save()

            return render(
                request,
                "collections/picker_item.html",
                context={"collection": collection, "post": post, "checked": True},
                status=200,
            )
        except Post.DoesNotExist, Collection.DoesNotExist:
            return HttpResponse(status=404)
    return HttpResponse("Not allowed", status=403)


@require(["POST"])
def remove_post_from_collection(
    request: HtmxHttpRequest, collection_id: int
) -> HttpResponse:
    if request.htmx:
        try:
            collection = Collection.objects.get(user=request.user, pk=collection_id)
            post = Post.objects.get(pk=request.POST.get("post"))
            collection.posts.remove(post)
            collection.save()

            return render(
                request,
                "collections/picker_item.html",
                context={"collection": collection, "post": post, "checked": False},
                status=200,
            )
        except Post.DoesNotExist, Collection.DoesNotExist:
            return HttpResponse(status=404)
    return HttpResponse("Not allowed", status=403)


@require(["POST"])
def add_comment(
    request: HtmxHttpRequest, post_id: int
) -> TemplateResponse | HttpResponse:
    post = get_object_or_404(Post.objects.filter(pk=post_id))

    data = AddCommentForm(request.POST)
    if data.is_valid():
        comment = Comment(
            post=post, text=data.cleaned_data.get("text"), user=request.user
        )

        comment.save()
        comments = Comment.objects.for_post(post.pk)
        comments_pager = Paginator(comments, 10, 5)
        comments_page_num = request.GET.get("page", 1)
        comments_page = comments_pager.get_page(comments_page_num)
        context = {
            "post": post,
            "comments": comments,
            "comments_pager": comments_pager,
            "comments_page": comments_page,
        }
        return render(request, "posts/comments.html", context=context)
    return HttpResponse(status=422)


@require(["POST"])
def edit_comment(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    data = EditCommentForm(request.POST)
    if data.is_valid():
        comment_id = data.cleaned_data.get("comment_id")
        comment = Comment.objects.get(pk=comment_id, user=request.user)
        comment.text = data.cleaned_data.get("text")
        comment.save()
        kwargs = {"comment": comment}
        return CommentComponent.render_to_response(request=request, kwargs=kwargs)
    return HttpResponse(status=422)


@require(["DELETE"])
def delete_comment(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    comment_id = request.POST.get("comment_id")
    try:
        comment = Comment.objects.get(user=request.user, pk=comment_id)
        post = comment.post
        comment.delete()
        comments = Comment.objects.for_post(post.pk)
        context = {"post": post, "comments": comments}
        return render(request, "posts/comments.html", context=context)
    except Comment.DoesNotExist:
        return HttpResponseNotFound(
            "That comment doesn't exist under the logged in user"
        )


@require(["GET"], login=False)
def post_search_autocomplete(
    request: HtmxHttpRequest,
) -> TemplateResponse | HttpResponse:
    if request.method == "GET" and request.htmx:
        tag_prefixes = [cat.name.lower() for cat in TagCategory]
        query = request.GET.get("q", "")
        ps = PostSearch(query, tag_prefixes)
        partial = request.GET.get("partial", "")
        items = ps.autocomplete(partial)

        context = {"items": items}
        return TemplateResponse(request, "posts/search_autocomplete.html", context)

    return HttpResponseNotAllowed(["GET"])


@require(["GET"], login=False)
def tag_search_autocomplete(
    request: HtmxHttpRequest,
) -> TemplateResponse | HttpResponseNotAllowed:
    if request.method == "GET":
        partial = request.GET.get("partial", "")
        tags = tag_autocomplete(partial)
        context = {"tags": tags}
        return TemplateResponse(request, "tags/search_autocomplete.html", context)

    return HttpResponseNotAllowed(["GET"])


def handle_media_upload(file: UploadedFile | None, src_url: str | None) -> Media:
    """Detects media type and creates a new Media derivative"""
    if file is None:
        msg = "A file must be provided to upload"
        raise ValueError(msg)

    if file.content_type:
        if smt := SupportedMediaTypes.find(file.content_type):
            media = Media(orig_name=file.name, type=smt.name, src_url=src_url)
            media.save()

            # TODO: match on media type (image, video, audio)...
            img = Image(file=file, meta=media)
            img.save()

            return media

        msg = "That file extension is not supported"
        raise ValueError(msg)

    msg = "Provided file doesn't have a content type"
    raise ValueError(msg)


@require(["GET", "POST"])
def upload(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    if request.htmx:
        # Confirming tagset
        data: dict[str, str | list[Any] | None] = {
            key: request.POST.get(key) for key in request.POST
        }
        data["tagset"] = request.POST.getlist("tagset")
        form = (
            TagsetForm(data, request.FILES)
            if request.method == "POST"
            else TagsetForm()
        )

        if form.is_valid():
            tagset = form.cleaned_data.get("tagset")
            tags = Tag.objects.in_tagset(tagset)

            kwargs = {"tags": tags, "add_tag_enabled": True, "post_url": "upload"}

            return AddTagsetComponent.render_to_response(request=request, kwargs=kwargs)

    data: dict[str, str | list[Any] | None] = {
        key: request.POST.get(key) for key in request.POST
    }
    data["tagset"] = request.POST.getlist("tagset")
    form = PostForm(data, request.FILES) if request.method == "POST" else PostForm()

    if form.is_valid():
        media = handle_media_upload(
            form.cleaned_data.get("file"), form.cleaned_data.get("src_url")
        )

        tagset = form.cleaned_data.get("tagset")
        rating_level = form.cleaned_data.get("rating_level")
        tags = Tag.objects.in_tagset(tagset)
        post = Post(uploader=request.user, media=media, rating_level=rating_level)
        post.tags.set(tags)
        post.save()

    context = {"form": form, "rating_levels": Post.RatingLevel.choices}
    return TemplateResponse(request, "pages/upload.html", context)


@require(["GET"], login=False)
def search_help(request: HtmxHttpRequest) -> TemplateResponse:
    context = {}
    return TemplateResponse(request, "pages/help.html", context)
