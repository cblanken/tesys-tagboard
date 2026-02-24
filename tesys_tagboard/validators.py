from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

from .enums import RatingLevel
from .enums import SupportedMediaType

rgb_validator = validators.RegexValidator(r"^#[0-9A-F]{6}$")
md5_validator = validators.RegexValidator(r"^[0-9A-Z]{32}$")
phash_validator = validators.RegexValidator(r"^[0-9a-z]{16}$")
dhash_validator = validators.RegexValidator(r"^[0-9a-z]{16}$")
tag_name_validator = validators.RegexValidator(
    _lazy_re_compile(r"^[a-zA-Z\d\:-_]+$"), message=_("Enter a valid tag name.")
)
tagset_name_validator = validators.RegexValidator(r"^[a-z\d\-_]+$")
username_validator = validators.RegexValidator(
    _lazy_re_compile(r"^[a-zA-Z\d_\-]+\Z"),
    message=_("Enter a valid username."),
)
positive_int_validator = validators.RegexValidator(
    _lazy_re_compile(r"^\d+$"),
    message=_("Enter a positive integer."),
)
wildcard_url_validator = validators.RegexValidator(
    # For allowing URLs with wildcards and without requiring
    # a protocol specifier or other URL validation
    r"[ A-Za-z0-9-.,_~:\/#@!$&';%=\*\+\(\)\?\[\]]",
    message=_("Enter a valid URL with wildcards"),
)
mimetype_validator = validators.RegexValidator(
    _lazy_re_compile(r"^[a-z]+[/][a-z]+[+]?[a-z]*$"),
    message=_("Enter a valid MIME type (e.g. image/jpeg)"),
)


def tagset_validator(tag_ids: list):
    """Validates a tagset. A Sequence of positive integers."""
    msg = _("A tagset may only contain positive integers")
    try:
        for tag_id in tag_ids:
            if int(tag_id) < 0:
                raise ValidationError(msg)

    except (ValueError, TypeError) as e:
        raise ValidationError(msg) from e


def media_file_supported_validator(file):
    if not SupportedMediaType.find(file.content_type):
        msg = f"File with a content type of {file.content_type} is not supported"
        raise ValidationError(msg)


def media_file_type_matches_ext_validator(file):
    # TODO
    return


def rating_label_validator(value: str):
    value = value.lower()
    rating_labels = [x.name.lower() for x in RatingLevel]
    if value not in rating_labels:
        label_names = ", ".join(rating_labels)
        msg = f"Rating label must be one of: {label_names}"
        raise ValidationError(msg)


def rating_level_validator(value):
    rating_levels = [x.value for x in RatingLevel]
    if value not in rating_levels:
        msg = f"Rating levels must be one of {rating_levels}"
        raise ValidationError(msg)
