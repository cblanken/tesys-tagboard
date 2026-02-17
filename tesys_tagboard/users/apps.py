import contextlib
from typing import TYPE_CHECKING

from allauth.account.signals import user_signed_up
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from users.models import User


def add_default_user_group(request, user: User, **kwargs):
    user.add_to_group("Users")


class UsersConfig(AppConfig):
    name = "tesys_tagboard.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import tesys_tagboard.users.signals  # noqa: F401, PLC0415

        # Apply the default group to new users
        user_signed_up.connect(
            add_default_user_group, dispatch_uid="signup_add_default_user_group"
        )
