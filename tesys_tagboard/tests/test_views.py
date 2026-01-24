from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Tag
from tesys_tagboard.users.models import User
from tesys_tagboard.users.tests.factories import UserFactory


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
