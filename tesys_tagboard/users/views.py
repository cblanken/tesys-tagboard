from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.db.models import Value
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from tesys_tagboard.decorators import require
from tesys_tagboard.models import Collection
from tesys_tagboard.models import Post
from tesys_tagboard.users.models import User

if TYPE_CHECKING:
    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@require(["GET", "POST"], login=False)
def user_detail_view(request: HttpRequest, username: str) -> TemplateResponse:
    user = get_object_or_404(User, username=username)

    context = {"user": user, "tab": request.GET.get("tab")}
    if request.user == user:
        # This user's page
        collections = Collection.objects.filter(user=user)
        favorited_posts = (
            Post.objects.with_gallery_data()
            .filter(
                pk__in=user.favorite_set.prefetch_related("post").values_list("post")
            )
            .annotate(favorited=Value(value=True))
        )

        favorites_pager = Paginator(favorited_posts, 20, 5)
        favorites_page_num = request.GET.get("fav_page", 1)
        favorites_page = favorites_pager.get_page(favorites_page_num)
        context |= {
            "favorites_pager": favorites_pager,
            "favorites_page": favorites_page,
            "collections": collections,
        }
    else:
        # Other users' pages
        public_collections = Collection.objects.filter(user=user, public=True)
        context |= {
            "collections": public_collections,
        }

    return TemplateResponse(request, "users/user_detail.html", context)


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
