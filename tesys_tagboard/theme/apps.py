from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ThemeConfig(AppConfig):
    name = "tesys_tagboard.theme"
    verbose_name = _("Theme")
