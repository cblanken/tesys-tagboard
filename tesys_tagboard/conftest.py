import pytest
from django.contrib.auth.models import Permission

from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.users.models import User
from tesys_tagboard.users.tests.factories import UserFactory


# Set faker testing seed for consistent randomized fake data
@pytest.fixture(autouse=True, scope="session")
def faker_seed():
    return 12345


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def user_with_add_post(db) -> User:
    return UserFactory().with_permissions([Permission.objects.get(codename="add_post")])


@pytest.fixture
def user_with_add_tag(db) -> User:
    return UserFactory().with_permissions([Permission.objects.get(codename="add_tag")])


@pytest.fixture
def user_with_add_tagalias(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="add_tagalias")]
    )


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        User.objects.bulk_create(
            [
                User(username="user1", password="user1user1"),  # noqa: S106
                User(username="user2", password="user2user2"),  # noqa: S106
                User(username="user3", password="user3user3"),  # noqa: S106
                User(username="mod1", password="mod1mod1"),  # noqa: S106
                User(username="mod2", password="mod2mod2"),  # noqa: S106
                User(username="mod3", password="mod3mod3"),  # noqa: S106
            ]
        )

        Tag.objects.bulk_create(
            [
                Tag(name="alabaster", category=TagCategory.BASIC.value.shortcode),
                Tag(name="amaranth pink", category=TagCategory.BASIC.value.shortcode),
                Tag(name="amaranth purple", category=TagCategory.BASIC.value.shortcode),
                Tag(name="amaranth", category=TagCategory.BASIC.value.shortcode),
                Tag(name="amber", category=TagCategory.BASIC.value.shortcode),
                Tag(name="arctic white", category=TagCategory.BASIC.value.shortcode),
                Tag(name="beige", category=TagCategory.BASIC.value.shortcode),
                Tag(name="black", category=TagCategory.BASIC.value.shortcode),
                Tag(name="blue jeans", category=TagCategory.BASIC.value.shortcode),
                Tag(name="blue", category=TagCategory.BASIC.value.shortcode),
                Tag(name="blue-gray", category=TagCategory.BASIC.value.shortcode),
                Tag(name="blueberry", category=TagCategory.BASIC.value.shortcode),
                Tag(name="brown", category=TagCategory.BASIC.value.shortcode),
                Tag(name="crimson", category=TagCategory.BASIC.value.shortcode),
                Tag(name="evergreen", category=TagCategory.BASIC.value.shortcode),
                Tag(name="green", category=TagCategory.BASIC.value.shortcode),
                Tag(name="grey", category=TagCategory.BASIC.value.shortcode),
                Tag(name="indigo", category=TagCategory.BASIC.value.shortcode),
                Tag(name="lime green", category=TagCategory.BASIC.value.shortcode),
                Tag(name="orange", category=TagCategory.BASIC.value.shortcode),
                Tag(name="purple", category=TagCategory.BASIC.value.shortcode),
                Tag(name="red", category=TagCategory.BASIC.value.shortcode),
                Tag(name="red vs. blue", category=TagCategory.BASIC.value.shortcode),
                Tag(name="sky blue", category=TagCategory.BASIC.value.shortcode),
                Tag(name="violet", category=TagCategory.BASIC.value.shortcode),
                Tag(name="violet hyacinth", category=TagCategory.BASIC.value.shortcode),
                Tag(name="white", category=TagCategory.BASIC.value.shortcode),
                Tag(name="white rapids", category=TagCategory.BASIC.value.shortcode),
                Tag(name="yellow", category=TagCategory.BASIC.value.shortcode),
                Tag(name="yellow flowers", category=TagCategory.BASIC.value.shortcode),
                Tag(
                    name="Avery Luis Stein", category=TagCategory.ARTIST.value.shortcode
                ),
                Tag(name="Elif", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Garbold Loop", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Justin Knope", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Solomon Steven", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Terry Toller", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Warren Witt", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Yura Yebolsky", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="Zammy Zolan", category=TagCategory.ARTIST.value.shortcode),
                Tag(name="CC-BY", category=TagCategory.COPYRIGHT.value.shortcode),
                Tag(name="MIT", category=TagCategory.COPYRIGHT.value.shortcode),
                Tag(
                    name="Public Domain", category=TagCategory.COPYRIGHT.value.shortcode
                ),
                Tag(name="Unlicense", category=TagCategory.COPYRIGHT.value.shortcode),
            ]
        )

        TagAlias.objects.bulk_create(
            [
                TagAlias(name="arctic", tag=Tag.objects.get(name="arctic white")),
                TagAlias(name="gray", tag=Tag.objects.get(name="grey")),
                TagAlias(name="r v. b", tag=Tag.objects.get(name="red vs. blue")),
                TagAlias(name="r vs. b", tag=Tag.objects.get(name="red vs. blue")),
                TagAlias(name="red v. blue", tag=Tag.objects.get(name="red vs. blue")),
                TagAlias(name="red vs blue", tag=Tag.objects.get(name="red vs. blue")),
                TagAlias(name="red x blue", tag=Tag.objects.get(name="red vs. blue")),
                TagAlias(name="blue-berry", tag=Tag.objects.get(name="blueberry")),
                TagAlias(name="gray-blue", tag=Tag.objects.get(name="blue-gray")),
                TagAlias(name="bluejeans", tag=Tag.objects.get(name="blue jeans")),
                TagAlias(name="Justin K", tag=Tag.objects.get(name="Justin Knope")),
                TagAlias(name="Solomon S", tag=Tag.objects.get(name="Solomon Steven")),
                TagAlias(name="Z. Zolan", tag=Tag.objects.get(name="Zammy Zolan")),
            ]
        )
