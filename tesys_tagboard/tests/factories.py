from datetime import datetime

from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker.providers import BaseProvider

from tesys_tagboard.enums import RatingLevel
from tesys_tagboard.enums import SupportedMediaTypes
from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.users.tests.factories import UserFactory


# Add TT-specific providers
class TagCategoryProvider(BaseProvider):
    tag_categories = [tc.value.shortcode for tc in TagCategory]

    def tag_category(self):
        return self.random_element(self.tag_categories)


class SupportedMediaTypeProvider(BaseProvider):
    supported_media_types = [smt.name for smt in SupportedMediaTypes]

    def supported_media_type(self):
        return self.random_element(self.supported_media_types)


Faker.add_provider(TagCategoryProvider)
Faker.add_provider(SupportedMediaTypeProvider)


class TagFactory(DjangoModelFactory[Tag]):
    name = Faker("name")
    category = Faker("tag_category")
    rating_level = Faker("enum", enum_cls=RatingLevel)

    class Meta:
        model = Tag
        django_get_or_create = ["name", "category"]


class TagAliasFactory(DjangoModelFactory[TagAlias]):
    name = Faker("name")
    tag = SubFactory(TagFactory)

    class Meta:
        model = TagAlias
        django_get_or_create = ["name", "tag"]


class PostFactory(DjangoModelFactory[Post]):
    title = Faker("text", max_nb_chars=50)
    uploader = SubFactory(UserFactory)
    post_date = Faker(
        "date_between_dates",
        date_start=datetime(1999, 1, 1).astimezone(),
        date_end=datetime(2050, 12, 31).astimezone(),
    )
    edit_date = Faker(
        "date_between_dates",
        date_start=datetime.now().astimezone(),
        date_end=datetime(2050, 12, 31).astimezone(),
    )

    rating_level = Faker("enum", enum_cls=RatingLevel)
    src_url = Faker("uri", schemes=["http", "https"])
    locked_comments = Faker("boolean")

    type = Faker("supported_media_type")

    class Meta:
        model = Post
