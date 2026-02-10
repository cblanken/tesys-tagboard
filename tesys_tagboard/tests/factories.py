import factory
from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker.providers import BaseProvider

from tesys_tagboard.enums import RatingLevel
from tesys_tagboard.enums import SupportedMediaTypes
from tesys_tagboard.models import Collection
from tesys_tagboard.models import Comment
from tesys_tagboard.models import Favorite
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
from tesys_tagboard.users.tests.factories import UserFactory


# Add TT-specific providers
class SupportedMediaTypeProvider(BaseProvider):
    supported_media_types = [smt.name for smt in SupportedMediaTypes]

    def supported_media_type(self):
        return self.random_element(self.supported_media_types)


Faker.add_provider(SupportedMediaTypeProvider)


class TagCategoryFactory(DjangoModelFactory[TagCategory]):
    name = Faker("name")

    class Meta:
        model = TagCategory
        django_get_or_create = ["name"]


class TagFactory(DjangoModelFactory[Tag]):
    name = Faker("word")
    category = None
    rating_level = Faker("enum", enum_cls=RatingLevel)

    class Meta:
        model = Tag
        django_get_or_create = ["name", "category"]


class TagAliasFactory(DjangoModelFactory[TagAlias]):
    name = Faker("word")
    tag = SubFactory(TagFactory)

    class Meta:
        model = TagAlias
        django_get_or_create = ["name", "tag"]


class PostFactory(DjangoModelFactory[Post]):
    title = Faker("text", max_nb_chars=50)
    uploader = SubFactory(UserFactory)

    rating_level = Faker("enum", enum_cls=RatingLevel)
    src_url = Faker("uri", schemes=["http", "https"])
    locked_comments = False

    type = Faker("supported_media_type")

    class Meta:
        model = Post


class CommentFactory(DjangoModelFactory[Comment]):
    text = Faker("text", max_nb_chars=500)
    post = SubFactory(PostFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = Comment


class CollectionFactory(DjangoModelFactory[Collection]):
    user = SubFactory(UserFactory)
    name = Faker("text", max_nb_chars=50)
    desc = Faker("text", max_nb_chars=200)

    class Meta:
        model = Collection

    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of groups using bulk addition
        self.posts.add(*extracted)


class FavoriteFactory(DjangoModelFactory[Favorite]):
    post = SubFactory(PostFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = Favorite
