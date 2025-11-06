from django.core import validators

valid_md5 = validators.RegexValidator(r"^[0-9A-Z]{32}$")
valid_phash = validators.RegexValidator(r"^[0-9a-z]{16}$")
valid_dhash = validators.RegexValidator(r"^[0-9a-z]{16}$")
