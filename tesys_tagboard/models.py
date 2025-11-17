"""Models for Tesys's Tagboard"""

import uuid
from hashlib import md5

import imagehash
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from PIL import Image as PIL_Image

from config.settings.base import AUTH_USER_MODEL

from .enums import SupportedMediaTypes
from .enums import TagCategory
from .validators import valid_dhash
from .validators import valid_md5
from .validators import valid_phash


class Tag(models.Model):
    """Tags for Media objects"""

    category_choices = [(s.value.shortcode, s.value.display_name) for s in TagCategory]

    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=2,
        choices=category_choices,
        default=TagCategory.BASIC.value.shortcode,
    )
    description = models.TextField(max_length=255, blank=True, default="")
    post_count = models.PositiveIntegerField(default=0)

    """Rating levels to filter content. This field allows any tag to apply a rating
    """
    rating_level = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "category"], name="unique_tag_name_cat"
            ),
        ]

    def __str__(self) -> str:
        return f"<Tag - {self.name}, category: {self.category}>"


class TagAlias(models.Model):
    """Aliases for Tags"""

    name = models.CharField(max_length=100, unique=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "tag aliases"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "tag"], name="unique_tagalias_name_tag"
            ),
        ]

    def __str__(self) -> str:
        return f"<TagAlias - {self.name}, tag: {self.tag}>"


class Artist(models.Model):
    """Model for Artists to identify all artwork from a particular source"""

    tag = models.OneToOneField(Tag, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(blank=True, default="")
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"<Artist - {self.tag}, bio: {self.bio}>"


def media_upload_path(instance, filename: str) -> str:
    """Generate a unique upload path for a Media file"""
    filename = str(uuid.uuid4())
    now = timezone.now()
    return f"uploads/{now.year}/{now.month}/{now.day}/{filename}"


def unique_filename(instance, filename: str) -> str:
    """Generate a unique (UUID) filename"""
    filename_split = filename.split(".")
    new_name = uuid.uuid4()
    if len(filename_split) > 1:
        extension = filename_split[-1]
        return f"{new_name}.{extension}"
    return f"{new_name}"


class Media(models.Model):
    """Media file metadata"""

    media_choices = (
        (x.name, x.value.desc) for x in SupportedMediaTypes.__members__.values()
    )

    orig_name = models.TextField()
    type = models.CharField(max_length=20, choices=media_choices)
    upload_date = models.DateTimeField(default=now, editable=False)
    edit_date = models.DateTimeField(auto_now=True)
    src_url = models.URLField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name_plural = "media"

    def __str__(self) -> str:
        return f"<Media - orig_file: {self.orig_name}, source: {self.src_url[:30]}...>"


class Image(models.Model):
    """Media linked to static image files"""

    meta = models.OneToOneField(Media, on_delete=models.CASCADE, primary_key=True)
    file = models.ImageField(upload_to=media_upload_path, unique=True)

    """MD5 hash"""
    md5 = models.CharField(validators=[valid_md5])

    """Perceptual (DCT) hash"""
    phash = models.CharField(validators=[valid_phash])

    """Difference hash"""
    dhash = models.CharField(validators=[valid_dhash])

    # TODO: add duplicate detection
    # See https://github.com/JohannesBuchner/imagehash/issues/127 for

    def __str__(self) -> str:
        return f"<Image - meta: {self.meta}, file: {self.file}>"

    def save(self, *args, **kwargs):
        self.md5 = md5(self.file.open().read()).hexdigest()  # noqa: S324
        self.phash = str(imagehash.phash(PIL_Image.open(self.file)))
        self.dhash = str(imagehash.dhash(PIL_Image.open(self.file)))
        super().save(*args, **kwargs)


class Video(models.Model):
    """Media linked to static video files"""

    meta = models.OneToOneField(Media, on_delete=models.CASCADE, primary_key=True)
    file = models.FileField(upload_to=media_upload_path, unique=True)

    """MD5 hash"""
    md5 = models.CharField(validators=[valid_md5])

    def __str__(self) -> str:
        return f"<Video - meta: {self.meta}, file: {self.file}>"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.md5 = md5(self.file.file).hexdigest()  # noqa: S324


class Audio(models.Model):
    """Media linked to static audio files"""

    meta = models.OneToOneField(Media, on_delete=models.CASCADE, primary_key=True)
    file = models.FileField(upload_to=media_upload_path, unique=True)

    """MD5 hash"""
    md5 = models.CharField(validators=[valid_md5])

    def __str__(self) -> str:
        return f"<Audio - meta: {self.meta}, file: {self.file}>"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.md5 = md5(self.file.file).hexdigest()  # noqa: S324


def update_tag_post_counts():
    tcounts = (
        Tag.post_set.through.objects.values("tag")
        .annotate(
            post_count=models.Count("post"),
            name=models.F("tag__name"),
            category=models.F("tag__category"),
            pk=models.F("tag"),
        )
        .order_by("tag__category")
    )

    tcount_tags = [Tag(pk=tc["pk"], post_count=tc["post_count"]) for tc in tcounts]
    Tag.objects.bulk_update(tcount_tags, fields=["post_count"])


class Post(models.Model):
    """Posts made by users with attached media"""

    class RatingLevel(models.IntegerChoices):
        """Rating levels for posts
        Default: UNRATED

        These levels are ordered such that SAFE < UNRATED < QUESTIONABLE < EXPLICIT
        This enabled a simple integer comparison to be made on the RatingLevel value
        to show only the desired posts
        """

        SAFE = 0
        UNRATED = 1
        QUESTIONABLE = 50
        EXPLICIT = 100

    uploader = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_date = models.DateTimeField(default=now, editable=False)
    tags = models.ManyToManyField(Tag)
    media = models.OneToOneField(Media, on_delete=models.CASCADE, primary_key=True)
    rating_level = models.PositiveSmallIntegerField(
        default=RatingLevel.UNRATED, choices=RatingLevel.choices
    )

    class Meta:
        ordering = ["post_date"]

    def __str__(self) -> str:
        return f"<Post - uploader: {self.uploader.name}, posted: {self.post_date}>"

    # TODO: also override update() to update post counts
    def save(self, **kwargs):
        super().save(**kwargs)
        update_tag_post_counts()


class Pool(models.Model):
    """Collections of posts saved by users"""

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    desc = models.TextField(max_length=1024)
    posts = models.ManyToManyField(Post)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_pool_name_user"
            )
        ]

    def __str__(self) -> str:
        return f"<Pool - name: {self.name}, user: {self.user}, desc: {self.desc}>"


class Comment(models.Model):
    """User comments"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    text = models.TextField(editable=True, max_length=500)

    def __str__(self) -> str:
        return f'<Comment: user: {self.user}, text: "{self.text}">'


class Favorite(models.Model):
    """Favorited posts by users"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_favorite"),
        ]

    def __str__(self) -> str:
        return f"<Favorite - post: {self.post}, user: {self.user}>"
