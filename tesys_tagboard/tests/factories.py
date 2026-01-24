from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker.providers import BaseProvider

from tesys_tagboard.enums import RatingLevel
from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias


# Add TT-specific providers
class TagCategoryProvider(BaseProvider):
    tag_categories = [tc.value.shortcode for tc in TagCategory]

    def tag_category(self):
        return self.random_element(self.tag_categories)


class RatingLevelProvider(BaseProvider):
    rating_levels = list(RatingLevel)

    def rating_level(self):
        return self.random_element(self.rating_levels)


Faker.add_provider(TagCategoryProvider)
Faker.add_provider(RatingLevelProvider)


class TagFactory(DjangoModelFactory[Tag]):
    name = Faker("name")
    category = Faker("tag_category")
    rating_level = Faker("rating_level")

    class Meta:
        model = Tag
        django_get_or_create = ["name", "category"]


class TagAliasFactory(DjangoModelFactory[TagAlias]):
    name = Faker("name")
    tag = SubFactory(TagFactory)

    class Meta:
        model = TagAlias
        django_get_or_create = ["name", "tag"]
