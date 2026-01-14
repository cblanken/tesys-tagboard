from http import HTTPStatus

from django.test import Client
from django.test import TestCase
from django.urls import reverse


class TestHomeView(TestCase):
    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_home(self):
        client = Client()
        response = client.get(reverse("home"))
        assert response.status_code == HTTPStatus.OK


class TestTagsView(TestCase):
    def test_tags(self):
        client = Client()
        response = client.get(reverse("tags"))
        assert response.status_code == HTTPStatus.OK

class TestPostsView(TestCase):
    def test_posts(self):
        client = Client()
        response = client.get(reverse("posts"))
        assert response.status_code == HTTPStatus.OK

class TestUploadView(TestCase):
    def test_upload(self):
        client = Client()
        response = client.get("/upload/", follow=True)
        assert response.redirect_chain[0][0] == "/accounts/login/?next=/upload/"
        assert response.status_code == HTTPStatus.OK

class TestCollectionsView(TestCase):
    def test_collections(self):
        client = Client()
        response = client.get(reverse("collections"))
        assert response.status_code == HTTPStatus.OK

class TestHelpView(TestCase):
    def test_help(self):
        client = Client()
        response = client.get(reverse("help"))
        assert response.status_code == HTTPStatus.OK
