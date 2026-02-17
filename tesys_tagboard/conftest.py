import pytest
from django.contrib.auth.models import Permission

from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
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


@pytest.fixture
def user_with_delete_post(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="delete_post")]
    )


@pytest.fixture
def user_with_change_post(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="change_post")]
    )


@pytest.fixture
def user_with_lock_comments(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="lock_comments")]
    )


@pytest.fixture
def user_with_add_comment(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="add_comment")]
    )


@pytest.fixture
def user_with_change_comment(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="change_comment")]
    )


@pytest.fixture
def user_with_delete_comment(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="delete_comment")]
    )


@pytest.fixture
def user_with_add_collection(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="add_collection")]
    )


@pytest.fixture
def user_with_delete_collection(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="delete_collection")]
    )


@pytest.fixture
def user_with_add_favorite(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="add_favorite")]
    )


@pytest.fixture
def user_with_delete_favorite(db) -> User:
    return UserFactory().with_permissions(
        [Permission.objects.get(codename="delete_favorite")]
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

        artist_category = TagCategory.objects.get(name__icontains="artist")
        copyright_category = TagCategory.objects.get(name__icontains="copyright")

        Tag.objects.bulk_create(
            [
                Tag(name="alabaster"),
                Tag(name="amaranth pink"),
                Tag(name="amaranth purple"),
                Tag(name="amaranth"),
                Tag(name="amber"),
                Tag(name="arctic white"),
                Tag(name="beige"),
                Tag(name="black"),
                Tag(name="blue jeans"),
                Tag(name="blue"),
                Tag(name="blue-gray"),
                Tag(name="blueberry"),
                Tag(name="brown"),
                Tag(name="crimson"),
                Tag(name="evergreen"),
                Tag(name="green"),
                Tag(name="grey"),
                Tag(name="indigo"),
                Tag(name="lime green"),
                Tag(name="orange"),
                Tag(name="purple"),
                Tag(name="red"),
                Tag(name="red vs. blue"),
                Tag(name="sky blue"),
                Tag(name="violet"),
                Tag(name="violet hyacinth"),
                Tag(name="white"),
                Tag(name="white rapids"),
                Tag(name="yellow"),
                Tag(name="yellow flowers"),
                # Tags in the artist category
                Tag(name="Avery Luis Stein", category=artist_category),
                Tag(name="Elif", category=artist_category),
                Tag(name="Garbold Loop", category=artist_category),
                Tag(name="Justin Knope", category=artist_category),
                Tag(name="Solomon Steven", category=artist_category),
                Tag(name="Terry Toller", category=artist_category),
                Tag(name="Warren Witt", category=artist_category),
                Tag(name="Yura Yebolsky", category=artist_category),
                Tag(name="Zammy Zolan", category=artist_category),
                # Tags in the copyright category
                Tag(name="CC-BY", category=copyright_category),
                Tag(name="MIT", category=copyright_category),
                Tag(name="Public Domain", category=copyright_category),
                Tag(name="Unlicense", category=copyright_category),
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
