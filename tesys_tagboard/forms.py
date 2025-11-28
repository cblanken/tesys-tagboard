from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Image
from .models import Tag
from .models import TagAlias


class UploadImage(forms.ModelForm):
    src_url = forms.URLField(label=_("Source"), required=False, assume_scheme="https")

    class Meta:
        model = Image
        fields = ["file"]


class MakeTag(forms.Form):
    class Meta:
        model = Tag
        fields = ["name", "category"]


class MakeTagAlias(forms.ModelForm):
    class Meta:
        model = TagAlias
        fields = ["name", "tag"]


class TagsetField(forms.Field):
    """A Field representing a set of Tag IDs"""

    def to_python(self, value) -> set[int]:
        if value is None:
            return set()
        try:
            return {int(x) for x in value if len(x) > 0}
        except ValueError as e:
            msg = "A tagset may only contain integers"
            raise ValidationError(msg) from e

    def validate(self, value):
        for tag_id in value:
            if tag_id <= 0:
                msg = "A tagset may only contain positive integers"
                raise ValidationError(msg)
        return value


class PostSearchForm(forms.Form):
    """Form for searching Posts
    tagset: an array of tag IDs
    funcset: an array of search function IDs
    """

    tagset = TagsetField(required=False, widget=forms.HiddenInput)
    funcset = TagsetField(required=False, widget=forms.HiddenInput)


class PostForm(forms.Form):
    """Form for media posts
    src_url = a URL linking to the source of the media
    file = a file object representing the Media
    tags: an array of tag IDs"""

    src_url = forms.URLField(label=_("Source"), required=False, assume_scheme="https")
    file = forms.FileField(label="File", required=True)
    tagset = TagsetField(required=False, widget=forms.HiddenInput)


class CommentForm(forms.Form):
    """Form for adding and editing Comments"""

    text = forms.CharField(widget=forms.Textarea, required=True)
