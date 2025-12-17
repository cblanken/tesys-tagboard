from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from tesys_tagboard.users.models import User

from .models import Collection
from .models import Image
from .models import Post
from .models import Tag
from .models import TagAlias


class UploadImage(forms.ModelForm):
    src_url = forms.URLField(label=_("Source"), required=False, assume_scheme="https")

    class Meta:
        model = Image
        fields = ["file"]


class CreateTagForm(forms.ModelForm):
    rating_level = forms.IntegerField(initial=0, required=False)

    class Meta:
        model = Tag
        fields = ["name", "category", "rating_level"]

    def clean_rating_level(self):
        if not self.cleaned_data.get("rating_level"):
            return self.fields["rating_level"].initial
        return self.cleaned_data["rating_level"]


class CreateTagAliasForm(forms.ModelForm):
    class Meta:
        model = TagAlias
        fields = ["name", "tag"]


class CreateCollectionForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), required=False)
    public = forms.BooleanField(required=False, initial=True)
    desc = forms.CharField(required=False)

    class Meta:
        model = Collection
        fields = ["name", "desc", "public", "user"]


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
    rating_level = forms.ChoiceField(choices=Post.RatingLevel.choices, required=False)
    tagset = TagsetField(required=False, widget=forms.HiddenInput)


class TagsetForm(forms.Form):
    tagset = TagsetField(required=False, widget=forms.HiddenInput)


class EditPostForm(forms.Form):
    """Form for editing Post metadata"""

    title = forms.CharField(max_length=200, label=_("Title"), required=False)
    src_url = forms.URLField(label=_("Source"), required=False, assume_scheme="https")
    rating_level = forms.ChoiceField(choices=Post.RatingLevel.choices, required=False)
    tagset = TagsetField(required=False, widget=forms.HiddenInput)


class AddCommentForm(forms.Form):
    """Form for adding Comments"""

    text = forms.CharField(widget=forms.Textarea, required=True)


class EditCommentForm(forms.Form):
    """Form for editing Comments"""

    comment_id = forms.IntegerField(required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)
