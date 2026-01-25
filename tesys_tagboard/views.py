from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from .components.add_tagset.add_tagset import AddTagsetComponent
from .components.comment.comment import CommentComponent
from .components.favorite_toggle.favorite_toggle import FavoriteToggleComponent
from .decorators import require
from .enums import MediaCategory
from .enums import RatingLevel
from .enums import SupportedMediaTypes
from .enums import TagCategory
from .forms import AddCommentForm
from .forms import CreateCollectionForm
from .forms import CreateTagAliasForm
from .forms import CreateTagForm
from .forms import EditCommentForm
from .forms import PostForm
from .forms import PostSearchForm
from .forms import TagsetForm
from .forms import tagset_to_array
from .models import Audio
from .models import Collection
from .models import Comment
from .models import Favorite
from .models import Image
from .models import Post
from .models import Tag
from .models import TagAlias
from .models import Video
from .models import csv_to_tag_ids
from .search import PostSearch
from .search import tag_autocomplete
from .validators import validate_media_file_is_supported
from .validators import validate_media_file_type_matches_ext
from .validators import validate_tagset

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from django.core.files.uploadedfile import UploadedFile
    from django.db.models import QuerySet
    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


User = get_user_model()


@dataclass
class Link:
    text: str
    href: str


@require(["GET"], login=False)
def home(request: HttpRequest) -> TemplateResponse:
    links = [Link(link[0], link[1]) for link in settings.HOMEPAGE_LINKS]

    try:
        markdown_path = Path("tesys_tagboard/home.md")
        with Path.open(markdown_path, encoding="utf-8") as fp:
            markdown_content = fp.read()
    except OSError:
        markdown_content = "The `home.md` file could not be found!"

    md = markdown.Markdown(extensions=["sane_lists"])
    context = {
        "links": links,
        "markdown_html": SafeString(md.convert(markdown_content)),
        "post_count": Post.objects.count(),
    }
    return TemplateResponse(request, "pages/home.html", context)


@require(["GET"], login=False)
def post(request: HtmxHttpRequest, post_id: int) -> TemplateResponse | HttpResponse:
    # GET request
    all_posts = Post.objects.order_by("post_date").values("pk", "post_date")
    previous_post = None
    next_post = None
    for i, post in enumerate(all_posts):
        if post.get("pk") == post_id:
            previous_post = all_posts[i - 1] if i > 0 else None
            next_post = all_posts[i + 1] if i < len(all_posts) - 1 else None

    posts = Post.objects.filter(pk=post_id).select_related("uploader")
    if request.user.is_authenticated:
        favorites = Favorite.objects.for_user(request.user)
        posts = posts.annotate_favorites(favorites)
    post = get_object_or_404(posts.prefetch_related("posttaghistory_set"))
    comments = post.comment_set.order_by("-post_date").select_related("user")

    comments_pager = Paginator(comments, 10, 5)
    comments_page_num = request.GET.get("page", 1)
    comments_page = comments_pager.get_page(comments_page_num)
    tags = Tag.objects.for_post(post)

    post_tag_snapshots = post.posttaghistory_set.order_by("mod_time")
    post_tag_history_tag_ids = [
        csv_to_tag_ids(tags_snapshot.tags) if tags_snapshot.tags.strip() != "" else []
        for tags_snapshot in post_tag_snapshots
    ]
    tag_history_unique_ids = set(chain(*post_tag_history_tag_ids))

    # Collect tag_history tags in a single DB call
    history_tags_by_id = {
        tag.pk: tag for tag in Tag.objects.filter(pk__in=tag_history_unique_ids)
    }

    tag_history = [
        [history_tags_by_id[int(tag_id)] for tag_id in tag_ids]
        for tag_ids in post_tag_history_tag_ids
    ]

    tag_history = post.posttaghistory_set.order_by("-mod_time")
    for tag_snapshot in tag_history:
        tag_snapshot.tag_objects = [
            history_tags_by_id[int(tag_id)]
            for tag_id in csv_to_tag_ids(tag_snapshot.tags)
        ]

    source_history = post.sourcehistory_set.order_by("-mod_time")

    context = {
        "post": post,
        "previous_post": previous_post,
        "next_post": next_post,
        "rating_levels": list(RatingLevel),
        "tags": tags,
        "meta_tag_names": " ".join(tag.name for tag in tags),
        "comments_pager": comments_pager,
        "comments_page": comments_page,
        "tag_history": tag_history,
        "source_history": source_history,
        "child_posts": Post.objects.filter(parent=post).with_gallery_data(request.user),
    }

    return TemplateResponse(request, "pages/post.html", context)


@require(["POST"], login=True)
def edit_post(
    request: HtmxHttpRequest, post_id: int
) -> TemplateResponse | HttpResponse:
    user: User | AnonymousUser = request.user
    post = get_object_or_404(Post.objects.filter(pk=post_id))
    if not (user.is_authenticated or user.has_perm("edit", post)):
        return HttpResponseForbidden(
            f'The user "{user.get_username()}" is not allowed to edit this post'
        )

    data: dict[str, str | list[Any] | None] = {
        key: request.POST.get(key) for key in request.POST
    }
    data["tagset"] = request.POST.getlist("tagset")

    form = PostForm(data)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid form data")

    if title := form.cleaned_data.get("title"):
        post.title = title

    if src_url := form.cleaned_data.get("src_url"):
        post.save_with_src_history(request.user, src_url)

    if rating_level := form.cleaned_data.get("rating_level"):
        post.rating_level = rating_level

    if tagset := form.cleaned_data.get("tagset"):
        tags = Tag.objects.in_tagset(tagset)
        post.save_with_tag_history(request.user, tags)

    post.save()
    return redirect(reverse("post", args=[post.pk]))


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


@require(["POST"])
def confirm_tagset(request: HtmxHttpRequest):
    if request.htmx:
        form = TagsetForm(request.POST)
        if form.is_valid():
            size = form.cleaned_data.get("size")
            tagset_name = form.cleaned_data.get("tagset_name")
            tagset = tagset_to_array(request.POST.getlist(tagset_name, None))

            # Confirm tagset for target tagset_name exists and is valid
            try:
                validate_tagset(tagset)
                if tagset:
                    tags = Tag.objects.in_tagset(tagset)
                    kwargs = {
                        "size": size,
                        "tags": tags,
                        "tagset_name": tagset_name,
                        "add_tag_enabled": True,
                    }
                    return AddTagsetComponent.render_to_response(
                        request=request, kwargs=kwargs
                    )
            except ValidationError:
                return HttpResponseBadRequest("Invalid tags provided")

    return HttpResponseBadRequest("Invalid request")


@require(["POST"])
@permission_required("edit_post", "lock_comments")
def toggle_comment_lock(
    request: HtmxHttpRequest, post_id: int
) -> TemplateResponse | HttpResponse:
    try:
        post = Post.objects.get(pk=post_id)
        post.locked_comments = not post.locked_comments
        post.save()
        return TemplateResponse(
            request, "pages/post.html#add-comments", context={"post": post}
        )

    except Post.DoesNotExist:
        return HttpResponseNotFound("That post doesn't exist")


@require(["GET", "POST"], login=False)
def posts(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    user: User | AnonymousUser = request.user
    posts = Post.objects.with_gallery_data(user)
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
    page_num = int(request.GET.get("page", 1))
    page = pager.get_page(page_num)

    context = {
        "pager": pager,
        "page": page,
        "tags": tags,
    }
    return TemplateResponse(request, "pages/posts.html", context)


@require(["GET", "POST"], login=False)
def tags(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    categories = TagCategory.__members__.values()

    try:
        tag_query = request.GET.get("q", "")
        tags_by_cat = {
            cat: Tag.objects.filter(
                category=cat.value.shortcode, name__icontains=tag_query
            )
            for cat in categories
        }

        alias_query = request.GET.get("aliases", "")
        aliases = (
            TagAlias.objects.filter(name__icontains=alias_query)
            .select_related("tag")
            .order_by("tag__category")
        )
    except ValidationError:
        return HttpResponseBadRequest("Invalid tag name or alias provided")

    context = {
        "tags": Tag.objects.order_by("name"),
        "tags_by_cat": tags_by_cat,
        "tag_name": tag_query,
        "aliases": aliases,
        "categories": categories,
    }

    if request.htmx:
        if request.GET.get("q") is not None:
            return TemplateResponse(request, "pages/tags.html#tag-categories", context)
        if request.GET.get("aliases") is not None:
            return TemplateResponse(request, "pages/tags.html#aliases", context)
        return HttpResponseBadRequest("No search queries provided")

    return TemplateResponse(request, "pages/tags.html", context)


@require(["POST"])
def create_tag(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    user = request.user
    if user.has_perm("tesys_tagboard.add_tag"):
        create_tag_form = CreateTagForm(request.POST)
        if create_tag_form.is_valid():
            create_tag_form.save()
        else:
            msg = "The tag inputs were invalid."
            messages.add_message(request, messages.WARNING, msg)
    else:
        msg = f"You ({user.username}) don't have permission to create tags."
        messages.add_message(request, messages.WARNING, msg)

    return redirect(reverse("tags"))


@require(["POST"])
def create_tag_alias(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    user = request.user
    if user.has_perm("tesys_tagboard.add_tagalias"):
        form = CreateTagAliasForm(request.POST)
        if form.is_valid():
            form.save()
            msg = f"The tag alias, {form.cleaned_data.get('name')}, was created!"
            messages.add_message(request, messages.WARNING, msg)
        else:
            msg = "The tag alias inputs were invalid."
            messages.add_message(request, messages.WARNING, msg)
    else:
        msg = f"You ({user.username}) don't have permission to create tag aliases."
        messages.add_message(request, messages.WARNING, msg)

    return redirect(reverse("tags"))


@require(["GET"], login=False)
def collections(request: HttpRequest) -> TemplateResponse:
    collections = Collection.objects.public().with_gallery_data()
    pager = Paginator(collections, 36, 4)
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
        posts = Post.objects.with_gallery_data(request.user).filter(
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
    if post.locked_comments:
        return HttpResponseForbidden("The comments for this post are locked")

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
        tags = tag_autocomplete(Tag.objects.all(), partial)
        context = {"tags": tags}
        return TemplateResponse(request, "tags/search_autocomplete.html", context)

    return HttpResponseNotAllowed(["GET"])


def find_duplicate_media_file(media_file):
    media_file_model = None
    match media_file.category():
        case MediaCategory.AUDIO:
            media_file_model = Audio
        case MediaCategory.IMAGE:
            media_file_model = Image
        case MediaCategory.VIDEO:
            media_file_model = Video

    if media_file_model:
        if found_file := media_file_model.objects.filter(md5=media_file.md5).first():
            return found_file
    return None


def handle_media_upload(file: UploadedFile | None, src_url: str | None) -> tuple:
    """Detects media type and creates a new Media derivative"""

    if file is None:
        msg = "The uploaded file cannot be empty"
        raise ValidationError(msg)

    validators = [
        validate_media_file_is_supported,
        validate_media_file_type_matches_ext,
    ]
    for validator in validators:
        validator(file)

    if file.content_type is None:
        msg = "File missing content type"
        raise ValidationError(msg)
    if smt := SupportedMediaTypes.find(file.content_type):
        media_file = None
        match smt.value.category:
            case MediaCategory.AUDIO:
                media_file = Audio(file=file)
            case MediaCategory.IMAGE:
                media_file = Image(file=file)
            case MediaCategory.VIDEO:
                media_file = Video(file=file)

        duplicate_file = find_duplicate_media_file(media_file)
        return (duplicate_file, media_file)

    msg = "The uploaded file could not be validated"
    raise ValidationError(msg)


@require(["GET", "POST"])
def upload(request: HtmxHttpRequest) -> TemplateResponse | HttpResponse:
    context = {"rating_levels": list(RatingLevel)}
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

    if request.method == "POST":
        data: dict[str, str | list[Any] | None] = {
            key: request.POST.get(key) for key in request.POST
        }
        data["tagset"] = request.POST.getlist("tagset")
        form = PostForm(data, request.FILES) if request.method == "POST" else PostForm()
        context |= {"form": form}
        if form.is_valid():
            try:
                duplicate, media_file = handle_media_upload(
                    form.files.get("file"), form.cleaned_data.get("src_url")
                )
            except ValidationError:
                msg = "Failed to validate uploaded media file"
                messages.add_message(request, messages.INFO, msg)
                return TemplateResponse(request, "pages/upload.html", context=context)
            else:
                if duplicate:
                    post_url = reverse("post", args=[duplicate.meta.post.pk])
                    msg = mark_safe(  # noqa: S308
                        f"The uploaded file was a duplicate of an existing post which can be found <a href='{post_url}'>here</a>"  # noqa: E501
                    )
                    media_file.delete()
                    messages.add_message(request, messages.WARNING, msg)
                    return TemplateResponse(
                        request, "pages/upload.html", context=context
                    )

            tagset = form.cleaned_data.get("tagset")
            rating_level = form.cleaned_data.get("rating_level")
            if rating_level not in list(RatingLevel):
                rating_level = RatingLevel.UNRATED
            tags = Tag.objects.in_tagset(tagset)
            if media_type := SupportedMediaTypes.find(
                media_file.file.file.content_type
            ):
                post = Post(
                    uploader=request.user,
                    rating_level=rating_level,
                    type=media_type.value.get_template(),
                )
                post.save()
                media_file.post = post
                media_file.save()
                post.save_with_tag_history(post.uploader, tags)
                msg = mark_safe(  # noqa: S308
                    f"Your post was create successfully, Check it out <a href='{reverse('post', args=[post.pk])}'>here</a>"  # noqa: E501
                )
                messages.add_message(request, messages.INFO, msg)
            else:
                msg = "The filetype of the uploaded file is not supported."
                messages.add_message(request, messages.ERROR, msg)

    return TemplateResponse(request, "pages/upload.html", context=context)


@require(["GET"], login=False)
def search_help(request: HtmxHttpRequest) -> TemplateResponse:
    context = {}
    return TemplateResponse(request, "pages/help.html", context)
