import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
from tesys_tagboard.search import PostSearch
from tesys_tagboard.search import TokenArgRelation
from tesys_tagboard.search import TokenCategory
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


class TestTokenCategory:
    def test_select_no_duplicate_names_or_aliases(self):
        """The TokenCategory enum should not have any ambigious names or aliases"""
        # TODO: test category select


class TestPostAdvancedSearchQueryParsing:
    def test_parse_empty_query(self):
        ps = PostSearch("")
        assert len(ps.tokens) == 0

    def test_parse_single_tag(self):
        ps = PostSearch("tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1"
        assert ps.tokens[0].category == TokenCategory.TAG
        assert not ps.tokens[0].negate

    def test_parse_single_negated_tag(self):
        ps = PostSearch("-tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1"
        assert ps.tokens[0].category == TokenCategory.TAG
        assert ps.tokens[0].negate

    def test_parse_single_tag_with_wildcard(self):
        ps = PostSearch("tag1*")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1*"
        assert ps.tokens[0].category == TokenCategory.TAG
        assert not ps.tokens[0].negate

    def test_parse_single_negated_tag_with_wildcard(self):
        ps = PostSearch("-*negated_tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "*negated_tag1"
        assert ps.tokens[0].category == TokenCategory.TAG
        assert ps.tokens[0].negate

    def test_parse_multiple_tags(self):
        ps = PostSearch("tag1 tag2 tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == TokenCategory.TAG
            assert not tok.negate

    def test_parse_multiple_negated_tags(self):
        ps = PostSearch("-tag1 -tag2 -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == TokenCategory.TAG
            assert tok.negate

    def test_parse_negated_and_non_negated_tags(self):
        ps = PostSearch("tag1 tag2 -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}

        assert ps.tokens[0].category == TokenCategory.TAG
        assert not ps.tokens[0].negate

        assert ps.tokens[1].category == TokenCategory.TAG
        assert not ps.tokens[1].negate

        # Last tag is negated
        assert ps.tokens[2].category == TokenCategory.TAG
        assert ps.tokens[2].negate

    def test_parse_extra_space_between_tokens(self):
        ps = PostSearch("tag1\t tag2   -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == TokenCategory.TAG

    def test_parse_extra_space_start_and_end(self):
        ps = PostSearch("    -tag1 tag2 -tag3\t ")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == TokenCategory.TAG

    @pytest.mark.parametrize("token_category", list(TokenCategory))
    def test_correctly_identify_tag_categories_by_name(
        self, token_category: TokenCategory
    ):
        if token_category.value.name:
            ps = PostSearch(f"{token_category.value.name}=100")
            assert ps.tokens[0].category == token_category

    @pytest.mark.parametrize("token_category", list(TokenCategory))
    def test_correctly_identify_tag_categories_by_alias(
        self, token_category: TokenCategory
    ):
        for alias in token_category.value.aliases:
            ps = PostSearch(f"{alias}=100")
            assert ps.tokens[0].category == token_category

    @pytest.mark.parametrize("arg_relation", list(TokenArgRelation))
    def test_parse_filter_token_with_multiple_arg_relations(self, arg_relation):
        arg_relation_char = arg_relation.value
        query = f"id{arg_relation_char}100{arg_relation_char}200"
        with pytest.raises(ValidationError):
            PostSearch(query)


@pytest.mark.django_db
class TestPostAdvancedSearchAutocomplete:
    pass


@pytest.mark.django_db
class TestPostAdvancedSearch:
    def test_empty_query(self):
        pass

    def test_only_include_tags(self):
        pass

    def test_include_tag_with_wildcard(self):
        pass

    def test_only_exclude_tags(self):
        pass

    def test_exclude_tag_with_wildcard(self):
        pass

    def test_include_and_exclude_tags(self):
        pass

    def test_include_tag_alias(self):
        pass

    def test_include_tag_alias_with_wildcard(self):
        pass

    def test_exclude_tag_alias_with_wildcard(self):
        pass

    def test_commented_by_user(self):
        pass

    def test_favorited_equal(self):
        pass

    def test_favorited_greater_than(self):
        pass

    def test_favorited_less_than(self):
        pass

    def test_favorited_by_user(self):
        pass

    def test_filetype_extension(self):
        pass

    def test_mimetype(self):
        pass

    def test_tag_count_equal(self):
        pass

    def test_tag_count_greater_than(self):
        pass

    def test_height_equal(self):
        pass

    def test_height_greater_than(self):
        pass

    def test_height_less_than(self):
        pass

    def test_weight_equal(self):
        pass

    def test_weight_greater_than(self):
        pass

    def test_weight_less_than(self):
        pass

    def test_rating_label_equal(self):
        pass

    def test_rating_label_greater_than(self):
        pass

    def test_rating_label_less_than(self):
        pass

    def test_rating_num_equal(self):
        pass

    def test_rating_num_greater_than(self):
        pass

    def test_rating_num_less_than(self):
        pass

    def test_src_url(self):
        pass

    def test_src_url_with_wildcard(self):
        pass

    def test_uploaded_by(self):
        pass
