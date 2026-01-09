from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

validate_md5 = validators.RegexValidator(r"^[0-9A-Z]{32}$")
validate_phash = validators.RegexValidator(r"^[0-9a-z]{16}$")
validate_dhash = validators.RegexValidator(r"^[0-9a-z]{16}$")
validate_tag_name = validators.RegexValidator(r"^[0-9a-zA-Z:-_]+$")


def validate_tagset(value):
    if value is None:
        return None

    for tag_id in value:
        if tag_id < 0:
            msg = _("A tagset may only contain positive integers")
            raise ValidationError(msg)
    return value
