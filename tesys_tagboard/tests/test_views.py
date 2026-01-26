from http import HTTPStatus
from mimetypes import types_map
from pathlib import Path

import pytest
from django.contrib.auth.models import Permission
from django.core.files.storage import storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from tesys_tagboard.enums import MediaCategory
from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.users.models import User
from tesys_tagboard.users.tests.factories import UserFactory

from .factories import TagAliasFactory
from .factories import TagFactory


@pytest.mark.django_db
class TestHomeView:
    url = reverse("home")

    def test_home(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, "pages/home.html")

    def test_max_query_count(self, client):
        client.get(self.url)


@pytest.mark.django_db
class TestTagsView:
    url = reverse("tags")

    def test_tags(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK

    def test_max_query_count(self, client, django_assert_max_num_queries):
        with django_assert_max_num_queries(30):
            client.get(self.url)


@pytest.mark.django_db(transaction=True)
class TestCreateTagView:
    url = reverse("create-tag")

    def test_create_basic_tag_without_perm(self, client):
        """An user without the add_tag permission should not
        be able to create a tag"""
        user = UserFactory()
        client.force_login(user)
        tag_name = "test_tag_1"
        data = {
            "name": tag_name,
            "category": TagCategory.BASIC.value.shortcode,
            "rating_level": "0",
        }
        client.post(self.url, data)

        with pytest.raises(Tag.DoesNotExist):
            Tag.objects.get(name=tag_name)

    def test_create_basic_tag_with_perm(self, client):
        """The user must have the add_tag permission to create tags"""
        user = UserFactory()
        add_tag_perm = Permission.objects.get(codename="add_tag")
        user.user_permissions.add(add_tag_perm)
        client.force_login(user)

        tag_count = Tag.objects.all().count()
        tag_name = "test_tag"
        data = {
            "name": tag_name,
            "category": TagCategory.BASIC.value.shortcode,
            "rating_level": "0",
        }

        response = client.post(self.url, data)
        assert response.status_code == HTTPStatus.FOUND
        tag = Tag.objects.get(name=tag_name)
        assert tag.name == tag_name
        assert tag.category == TagCategory.BASIC.value.shortcode
        assert tag.rating_level == 0
        new_count = Tag.objects.all().count()
        assert new_count == tag_count + 1

    def test_create_basic_tag_defaults(self, client):
        """Tags created without a category should be assigned
        the BASIC category and rating_level of 0 by default"""
        user = UserFactory()
        add_tag_perm = Permission.objects.get(codename="add_tag")
        user.user_permissions.add(add_tag_perm)
        client.force_login(user)

        tag_name = "test_tag"
        data = {"name": tag_name}

        client.post(self.url, data)
        tag = Tag.objects.get(name=tag_name)
        assert tag.name == tag_name
        assert tag.category == TagCategory.BASIC.value.shortcode
        assert tag.rating_level == 0

    def test_create_tag_with_invalid_category(self, client):
        """A tag should not be created with an invalid category value"""
        user = UserFactory()
        add_tag_perm = Permission.objects.get(codename="add_tag")
        user.user_permissions.add(add_tag_perm)
        client.force_login(user)

        tag_name = "test_tag"
        data = {"name": tag_name, "category": "ZZ"}
        client.post(self.url, data)

        with pytest.raises(Tag.DoesNotExist):
            Tag.objects.get(name=tag_name)

    def test_create_tag_with_too_large_rating_level(self, client):
        """A tag should not be created with an invalid category value"""
        user = UserFactory()
        add_tag_perm = Permission.objects.get(codename="add_tag")
        user.user_permissions.add(add_tag_perm)
        client.force_login(user)

        tag_name = "test_tag"
        data = {"name": tag_name, "rating_level": "999999"}
        client.post(self.url, data)

        with pytest.raises(Tag.DoesNotExist):
            Tag.objects.get(name=tag_name)

    def test_create_tag_with_negative_rating_level(self, client):
        """A tag should not be created with an invalid category value"""
        user = UserFactory()
        add_tag_perm = Permission.objects.get(codename="add_tag")
        user.user_permissions.add(add_tag_perm)
        client.force_login(user)

        tag_name = "test_tag"
        data = {"name": tag_name, "rating_level": "-1"}
        client.post(self.url, data)

        with pytest.raises(Tag.DoesNotExist):
            Tag.objects.get(name=tag_name)


@pytest.mark.django_db(transaction=True)
class TestCreateTagAliasView:
    url = reverse("create-tag-alias")

    def test_create_basic_tag_alias_without_perm(self, client):
        """A user without the add_tagalias permission should not
        be able to create a tag"""
        user = UserFactory.create()
        client.force_login(user)
        alias_name = "test_alias_1"
        data = {"name": alias_name, "tag": TagFactory.build()}
        client.post(self.url, data)

        with pytest.raises(Tag.DoesNotExist):
            Tag.objects.get(name=alias_name)

    def test_create_basic_tag_alias_with_perm(self, client):
        """A user with the add_tagalias permission should be able to create a
        tag alias"""
        user = UserFactory()
        add_tag_alias_perm = Permission.objects.get(codename="add_tagalias")
        user.user_permissions.add(add_tag_alias_perm)
        user.save()
        client.force_login(user)

        alias_name = "test_alias_1"
        tag = TagFactory.create()
        data = {"name": alias_name, "tag": str(tag.pk)}
        client.post(self.url, data)

        alias = TagAlias.objects.get(name=alias_name)
        assert alias.name == alias_name
        assert alias.tag == tag

    def test_cannot_create_tag_alias_with_dup_name(self, client):
        """TagAliases must have a unique name"""
        user = UserFactory()
        add_tag_alias_perm = Permission.objects.get(codename="add_tagalias")
        user.user_permissions.add(add_tag_alias_perm)
        user.save()
        client.force_login(user)

        duped_alias = TagAliasFactory.create()
        data = {"name": duped_alias.name, "tag": duped_alias.tag.pk}
        client.post(self.url, data)

        assert TagAlias.objects.filter(name=duped_alias.name).count() == 1

    def test_tag_alias_create_cannot_edit_alias(self, client):
        """The create-tagalias endpoint should not be able to edit an existing alias"""
        user = UserFactory()
        add_tag_alias_perm = Permission.objects.get(codename="add_tagalias")
        user.user_permissions.add(add_tag_alias_perm)
        user.save()
        client.force_login(user)

        existing_alias = TagAliasFactory.create()
        before_alias = TagAlias.objects.get(name=existing_alias.name)
        other_tag = TagFactory.create()
        data = {"name": existing_alias.name, "tag": other_tag.pk}
        client.post(self.url, data)

        after_alias = TagAlias.objects.get(name=existing_alias.name)
        assert before_alias.tag == after_alias.tag


@pytest.mark.django_db
class TestPostsView:
    url = reverse("posts")

    def test_posts(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, "pages/posts.html")

    def test_max_query_count(self, client, django_assert_max_num_queries):
        with django_assert_max_num_queries(20):
            client.get(self.url)

    def test_max_logged_in_query_count(self, client, django_assert_max_num_queries):
        user = User.objects.get(username="user1")
        client.force_login(user)
        with django_assert_max_num_queries(25):
            client.get(self.url)


def get_uploaded_test_media_file(
    filename: str, ext: str, *, cat: MediaCategory = MediaCategory.IMAGE
):
    ext = f".{ext}" if ext[0] != "." else ext
    store = storages["test-media"]
    match cat:
        case MediaCategory.IMAGE:
            file = Path(store.path(f"images/{filename}{ext}"))
        case MediaCategory.AUDIO:
            file = Path(store.path(f"audios/{filename}{ext}"))
        case MediaCategory.VIDEO:
            file = Path(store.path(f"videos/{filename}{ext}"))

    if content_type := types_map.get(ext):
        return SimpleUploadedFile(
            filename,
            file.read_bytes(),
            content_type=content_type,
        )
    msg = "Invalid file or extension provided."
    raise ValueError(msg)


@pytest.mark.django_db
class TestUploadView:
    url = reverse("upload")

    def test_upload(self, client):
        response = client.get(self.url, follow=True)
        assert response.redirect_chain[0][0] == "/accounts/login/?next=/upload/"
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, "account/login.html")

    def test_max_query_count(self, client, django_assert_max_num_queries):
        with django_assert_max_num_queries(20):
            client.get(self.url)

    def test_user_without_add_post_perm(self, client):
        """User's without the 'add_post' permission cannot make posts"""
        user = UserFactory()
        user.save()
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "png")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts

    def test_create_png_img_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        user.save()
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "png")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_jpg_img_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "jpeg")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_webp_img_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "webp")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_tiff_img_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "tif")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_gif_img_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        img_file = get_uploaded_test_media_file("1x1", "gif")
        data = {"file": img_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_mp3_audio_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        audio_file = get_uploaded_test_media_file("1s", "mp3", cat=MediaCategory.AUDIO)
        data = {"file": audio_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_wav_audio_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        audio_file = get_uploaded_test_media_file("1s", "wav", cat=MediaCategory.AUDIO)
        data = {"file": audio_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_webm_video_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        video_file = get_uploaded_test_media_file("1s", "webm", cat=MediaCategory.VIDEO)
        data = {"file": video_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1

    def test_create_mpeg_video_post(self, client):
        user = UserFactory()
        add_post_perm = Permission.objects.get(codename="add_post")
        user.user_permissions.add(add_post_perm)
        client.force_login(user)

        video_file = get_uploaded_test_media_file("1s", "mpg", cat=MediaCategory.VIDEO)
        data = {"file": video_file}

        before_posts = Post.objects.all().count()
        client.post(self.url, data)
        after_posts = Post.objects.all().count()

        assert after_posts == before_posts + 1


@pytest.mark.django_db
class TestCollectionsView:
    url = reverse("collections")

    def test_collections(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, "pages/collections.html")

    def test_max_query_count(self, client, django_assert_max_num_queries):
        with django_assert_max_num_queries(20):
            client.get(self.url)


@pytest.mark.django_db
class TestHelpView:
    url = reverse("help")

    def test_help(self, client):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(response, "pages/help.html")

    def test_max_query_count(self, client, django_assert_max_num_queries):
        with django_assert_max_num_queries(20):
            client.get(self.url)
