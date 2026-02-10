from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

from .enums import RatingLevel
from .enums import SupportedMediaTypes

rgb_validator = validators.RegexValidator(r"^#[0-9A-F]{6}$")
md5_validator = validators.RegexValidator(r"^[0-9A-Z]{32}$")
phash_validator = validators.RegexValidator(r"^[0-9a-z]{16}$")
dhash_validator = validators.RegexValidator(r"^[0-9a-z]{16}$")
tag_name_validator = validators.RegexValidator(r"^[a-zA-Z\d\:-_]+$")
tagset_name_validator = validators.RegexValidator(r"^[a-z\d\-_]+$")
username_validator = validators.RegexValidator(
    _lazy_re_compile(r"^-?[a-zA-Z_]]\Z"),
    message=_("Enter a valid username."),
)


def tagset_validator(tag_ids: list):
    msg = _("A tagset may only contain positive integers")
    try:
        for tag_id in tag_ids:
            if int(tag_id) < 0:
                raise ValidationError(msg)

    except (ValueError, TypeError) as e:
        raise ValidationError(msg) from e


def media_file_supported_validator(file):
    if not SupportedMediaTypes.find(file.content_type):
        msg = f"File with a content type of {file.content_type} is not supported"
        raise ValidationError(msg)


def media_file_type_matches_ext_validator(file):
    # TODO
    return


def rating_level_validator(value):
    levels = [x.value for x in RatingLevel]
    if value not in levels:
        msg = f"Rating levels must be one of {levels}"
        raise ValidationError(msg)
