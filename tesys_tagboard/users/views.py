from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from tesys_tagboard.components.add_tagset.add_tagset import AddTagsetComponent
from tesys_tagboard.decorators import require
from tesys_tagboard.forms import EditUserSettingsForm
from tesys_tagboard.models import Collection
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag

from .models import User

if TYPE_CHECKING:
    from typing import Any

    from django.db.models import QuerySet
    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@require(["GET", "POST"], login=False)
def user_detail_view(request: HttpRequest, username: str) -> TemplateResponse:
    user = get_object_or_404(User, username=username)

    context = {
        "user": user,
        "tab": request.GET.get("tab"),
    }
    if request.user == user:
        # This user's page
        collections = user.collection_set.with_gallery_data()
        favorited_posts = [f.post for f in user.favorite_set.with_gallery_data()]
        for post in favorited_posts:
            post.favorited = True

        favorites_pager = Paginator(favorited_posts, 20, 5)
        favorites_page_num = request.GET.get("fav_page", 1)
        favorites_page = favorites_pager.get_page(favorites_page_num)
        context |= {
            "favorites_pager": favorites_pager,
            "favorites_page": favorites_page,
            "collections": collections,
            "blur_rating_levels": Post.RatingLevel,
        }
    else:
        # Other users' pages
        public_collections = Collection.objects.filter(user=user, public=True)
        context |= {
            "collections": public_collections,
        }

    return TemplateResponse(request, "users/user_detail.html", context)


@require(["POST"])
def user_edit_settings(
    request: HtmxHttpRequest, username: str
) -> TemplateResponse | HttpResponse:
    user = User.objects.get(username=username)

    if user != request.user:
        return HttpResponseForbidden()

    data: dict[str, str | list[Any] | None] = {
        key: request.POST.get(key) for key in request.POST
    }
    data["filter_tags"] = request.POST.getlist("filter_tags")
    data["blur_tags"] = request.POST.getlist("blur_tags")

    form = EditUserSettingsForm(data)
    if form.is_valid():
        if blur_rating_level := form.cleaned_data.get("blur_rating_level"):
            user.blur_rating_level = blur_rating_level
            user.save()
            return HttpResponse(user.blur_rating_level, status=200)

        if filter_tagset := form.cleaned_data.get("filter_tags"):
            tags = Tag.objects.in_tagset(filter_tagset)
            user.filter_tags.set(tags)
            user.save()
            kwargs = {
                "tags": user.filter_tags.all(),
                "add_tag_enabled": True,
                "post_url": "users:edit-settings",
                "post_args": [user.username],
            }

            return AddTagsetComponent.render_to_response(request=request, kwargs=kwargs)

        if blur_tagset := form.cleaned_data.get("blur_tags"):
            tags = Tag.objects.in_tagset(blur_tagset)
            user.blur_tags.set(tags)
            user.save()
            kwargs = {
                "tags": user.blur_tags.all(),
                "add_tag_enabled": True,
                "post_url": "users:edit-settings",
                "post_args": [user.username],
            }

            return AddTagsetComponent.render_to_response(request=request, kwargs=kwargs)

        return HttpResponse(status=200)
    return HttpResponse(status=422)


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
