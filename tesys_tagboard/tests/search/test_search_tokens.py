import contextlib
from itertools import chain
from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.search import TAG_CATEGORY_DELIMITER
from tesys_tagboard.search import PostSearch
from tesys_tagboard.search import PostSearchTokenCategory
from tesys_tagboard.search import TokenArgRelation

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise


class TestSearchTokenCategories:
    def test_no_duplicate_aliases(self):
        """Ensure available TokenCategory types don't have any duplicate aliases"""
        token_aliases = list(
            chain(*[tok.value.aliases for tok in PostSearchTokenCategory])
        )
        assert len(token_aliases) == len(set(token_aliases))


class TestTokenCategory:
    def test_select_no_duplicate_names_or_aliases(self):
        """The TokenCategory enum should not have any ambigious names or aliases"""
        token_names: list[StrOrPromise] = []
        for token_category in PostSearchTokenCategory:
            assert token_category.value.name not in token_names
            assert token_category.value.name not in token_category.value.aliases
            for alias in token_category.value.aliases:
                assert alias not in token_names

            token_names.extend(
                [token_category.value.name, *token_category.value.aliases]
            )


class TestTagTokens:
    def test_parse_empty_query(self):
        ps = PostSearch("")
        assert len(ps.tokens) == 0

    def test_parse_single_tag(self):
        ps = PostSearch("tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1"
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert not ps.tokens[0].negate

    def test_parse_single_negated_tag(self):
        ps = PostSearch("-tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1"
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert ps.tokens[0].negate

    def test_parse_tag_with_category(self):
        ps = PostSearch("category1:tag1")
        assert len(ps.tokens) == 1
        token = ps.tokens[0]
        assert token.name == "category1:tag1"
        assert token.category == PostSearchTokenCategory.TAG
        assert not token.negate

    def test_parse_negated_tag_with_category(self):
        ps = PostSearch("-category1:tag1")
        assert len(ps.tokens) == 1
        token = ps.tokens[0]
        assert token.name == "category1:tag1"
        assert token.category == PostSearchTokenCategory.TAG
        assert token.negate

    def test_parse_tag_with_multiple_categories(self):
        query = TAG_CATEGORY_DELIMITER.join(["root", "parent1", "parent2", "tag"])
        ps = PostSearch(query)
        assert len(ps.tokens) == 1
        token = ps.tokens[0]
        assert token.name == query
        assert token.category == PostSearchTokenCategory.TAG
        assert not token.negate

    def test_parse_negated_tag_with_nested_categories(self):
        query = TAG_CATEGORY_DELIMITER.join(["root", "parent1", "parent2", "tag"])
        negated_query = "-" + query
        ps = PostSearch(negated_query)
        assert len(ps.tokens) == 1
        token = ps.tokens[0]
        assert token.name == query
        assert token.category == PostSearchTokenCategory.TAG
        assert token.negate

    def test_parse_single_tag_with_wildcard(self):
        ps = PostSearch("tag1*")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1*"
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert not ps.tokens[0].negate

    def test_parse_single_negated_tag_with_wildcard(self):
        ps = PostSearch("-*negated_tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "*negated_tag1"
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert ps.tokens[0].negate

    def test_parse_multiple_tags(self):
        ps = PostSearch("tag1 tag2 tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == PostSearchTokenCategory.TAG
            assert not tok.negate

    def test_parse_multiple_negated_tags(self):
        ps = PostSearch("-tag1 -tag2 -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == PostSearchTokenCategory.TAG
            assert tok.negate

    def test_parse_negated_and_non_negated_tags(self):
        ps = PostSearch("tag1 tag2 -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}

        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert not ps.tokens[0].negate

        assert ps.tokens[1].category == PostSearchTokenCategory.TAG
        assert not ps.tokens[1].negate

        # Last tag is negated
        assert ps.tokens[2].category == PostSearchTokenCategory.TAG
        assert ps.tokens[2].negate

    def test_parse_extra_space_between_tokens(self):
        ps = PostSearch("tag1\t tag2   -tag3")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == PostSearchTokenCategory.TAG

    def test_parse_extra_space_start_and_end(self):
        ps = PostSearch("    -tag1 tag2 -tag3\t ")
        assert len(ps.tokens) == 3
        assert {tok.name for tok in ps.tokens} == {"tag1", "tag2", "tag3"}
        for tok in ps.tokens:
            assert tok.category == PostSearchTokenCategory.TAG


class TestTokenCategories:
    @pytest.mark.parametrize("token_category", list(PostSearchTokenCategory))
    def test_correctly_identify_tag_categories_by_name(
        self, token_category: PostSearchTokenCategory
    ):
        if token_category.value.name:
            # This test does not test validation, only token identification
            with contextlib.suppress(ValidationError):
                ps = PostSearch(f"{token_category.value.name}=100")
                assert ps.tokens[0].category == token_category

    @pytest.mark.parametrize("token_category", list(PostSearchTokenCategory))
    def test_correctly_identify_tag_categories_by_alias(
        self, token_category: PostSearchTokenCategory
    ):
        for alias in token_category.value.aliases:
            # This test does not test validation, only token identification
            with contextlib.suppress(ValidationError):
                ps = PostSearch(f"{alias}=100")
                assert ps.tokens[0].category == token_category


class TestTokenArguments:
    @pytest.mark.parametrize("arg_relation", list(TokenArgRelation))
    def test_parse_filter_token_with_multiple_arg_relations(self, arg_relation):
        arg_relation_char = arg_relation.value
        query = f"id{arg_relation_char}100{arg_relation_char}200"
        with pytest.raises(ValidationError):
            PostSearch(query)
