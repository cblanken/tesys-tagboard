from django.contrib import admin

from .models import Artist
from .models import Audio
from .models import Comment
from .models import Favorite
from .models import Image
from .models import Media
from .models import Pool
from .models import Post
from .models import Tag
from .models import TagAlias
from .models import Video


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "category"]
    search_fields = ["name", "category"]
    list_filter = ["category"]


@admin.register(TagAlias)
class TagAliasAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "tag__name",
        "tag__category",
        "tag__rating_level",
        "tag__description",
    ]
    search_fields = ["name", "tag__name", "tag__category"]
    list_filter = ["tag__category", "tag__rating_level"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["user", "tag", "bio"]
    search_fields = ["user__name", "tag__name"]
    autocomplete_fields = ["user", "tag"]
    ordering = ["user"]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ["orig_name", "type", "src_url", "upload_date", "edit_date"]
    search_fields = ["orig_name", "type"]
    list_filter = ["type"]

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form:
            form.base_fields["src_url"].required = False
        return form


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "file",
        "meta__id",
        "meta__orig_name",
        "meta__type",
        "md5",
        "phash",
        "dhash",
    ]
    autocomplete_fields = ["meta"]
    search_fields = ["meta__type", "og_name", "source"]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    autocomplete_fields = ["meta"]
    search_fields = ["meta__type", "og_name", "source"]


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    autocomplete_fields = ["meta"]
    search_fields = ["meta__type", "og_name", "source"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "text"]
    list_filter = ["user"]
    autocomplete_fields = ["user"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "uploader",
        "post_date",
        "rating_level",
        "media__orig_name",
        "media__src_url",
    ]
    search_fields = ["media__orig_name, source__url"]
    autocomplete_fields = ["media"]
    list_filter = ["rating_level", "uploader"]


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user", "posts"]
    search_fields = ["user", "name", "desc"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user", "post"]
    search_fields = ["user"]
