import pytest

from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
from tesys_tagboard.search import tag_alias_autocomplete
from tesys_tagboard.search import tag_autocomplete


@pytest.mark.django_db
class TestTagAutocomplete:
    def test_autocomplete_included_by_name_partial(self, db):
        tags = tag_autocomplete(Tag.objects.all(), "blue")
        tag_names = [tag.name for tag in tags]
        assert "blue jeans" in tag_names
        assert "blue" in tag_names
        assert "blue-gray" in tag_names
        assert "blueberry" in tag_names
        assert "red vs. blue" in tag_names
        assert "sky blue" in tag_names
        assert tags.count() == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        tags = tag_autocomplete(Tag.objects.all(), exclude_partial="blue")
        tag_names = [tag.name for tag in tags]
        assert "blue jeans" not in tag_names
        assert "blue" not in tag_names
        assert "blue-gray" not in tag_names
        assert "blueberry" not in tag_names
        assert "sky blue" not in tag_names

    def test_autocomplete_excluded_by_tag_name(self, db):
        tags = tag_autocomplete(
            Tag.objects.all(), exclude_tag_names=["violet", "white", "yellow"]
        )
        tag_names = [tag.name for tag in tags]
        assert "violet" not in tag_names
        assert "white" not in tag_names
        assert "yellow" not in tag_names
        assert "white rapids" in tag_names
        assert "yellow flowers" in tag_names
        assert "violet hyacinth" in tag_names

    def test_autocomplete_excluded_by_tag(self, db):
        copyright_category = TagCategory.objects.get(name="copyright")
        exclude_tags = Tag.objects.filter(category=copyright_category)
        tags = tag_autocomplete(Tag.objects.all(), exclude_tags=exclude_tags)
        assert len(tags.intersection(exclude_tags)) == 0


@pytest.mark.django_db
class TestTagAliasAutocomplete:
    def test_autocomplete_included_by_name_partial(self, db):
        aliases = tag_alias_autocomplete(TagAlias.objects.all(), "blue")
        alias_names = [alias.name for alias in aliases]
        assert "bluejeans" in alias_names
        assert "gray-blue" in alias_names
        assert "blue-berry" in alias_names
        assert "red v. blue" in alias_names
        assert "red vs blue" in alias_names
        assert "red x blue" in alias_names
        assert aliases.count() == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        aliases = tag_alias_autocomplete(TagAlias.objects.all(), exclude_partial="red")
        alias_names = [alias.name for alias in aliases]
        assert "red v. blue" not in alias_names
        assert "red vs blue" not in alias_names
        assert "red x blue" not in alias_names
        assert "r v. b" in alias_names
        assert "r vs. b" in alias_names

    def test_autocomplete_excluded_by_alias_name(self, db):
        aliases = tag_alias_autocomplete(
            TagAlias.objects.all(),
            exclude_alias_names=["Justin K", "Solomon S", "Z. Zolan"],
        )
        alias_names = [alias.name for alias in aliases]
        assert "Justin K" not in alias_names
        assert "Solomon S" not in alias_names
        assert "Z. Zolan" not in alias_names

    def test_autocomplete_excluded_by_alias(self, db):
        copyright_category = TagCategory.objects.get(name="copyright")
        exclude_aliases = TagAlias.objects.filter(tag__category=copyright_category)
        aliases = tag_alias_autocomplete(
            TagAlias.objects.all(), exclude_aliases=exclude_aliases
        )
        assert len(aliases.intersection(exclude_aliases)) == 0


@pytest.mark.django_db
class TestPostAdvancedSearch:
    def test_empty_query(self):
        # TODO
        pass

    def test_query_only_tags(self):
        # TODO
        pass

    def test_exclude_tags(self):
        # TODO
        pass

    def test_comment_count(self):
        # TODO
        pass

    def test_commented_by_user(self):
        # TODO
        pass

    def test_favorited_once(self):
        # TODO
        pass

    def test_favorited_more_than_once(self):
        # TODO
        pass

    def test_favorited_by_user(self):
        # TODO
        pass

    def test_filetype_extension(self):
        # TODO
        pass
