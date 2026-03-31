import contextlib

import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.search import TAG_CATEGORY_DELIMITER
from tesys_tagboard.search import PostSearch
from tesys_tagboard.search import PostSearchTokenCategory
from tesys_tagboard.search import TokenArgRelation


class TestTagTokens:
    def test_parse_empty_query(self):
        tokens = PostSearch.parse_query("")
        assert len(tokens) == 0

    def test_parse_single_tag(self):
        tokens = PostSearch.parse_query("tag1")
        assert len(tokens) == 1
        assert tokens[0].name == "tag1"
        assert tokens[0].category == PostSearchTokenCategory.TAG
        assert not tokens[0].negate

    def test_parse_single_negated_tag(self):
        tokens = PostSearch.parse_query("-tag1")
        assert len(tokens) == 1
        assert tokens[0].name == "tag1"
        assert tokens[0].category == PostSearchTokenCategory.TAG
        assert tokens[0].negate

    def test_parse_tag_with_category(self):
        tokens = PostSearch.parse_query("category1:tag1")
        assert len(tokens) == 1
        token = tokens[0]
        assert token.name == "category1:tag1"
        assert token.category == PostSearchTokenCategory.TAG
        assert not token.negate

    def test_parse_negated_tag_with_category(self):
        tokens = PostSearch.parse_query("-category1:tag1")
        assert len(tokens) == 1
        token = tokens[0]
        assert token.name == "category1:tag1"
        assert token.category == PostSearchTokenCategory.TAG
        assert token.negate

    def test_parse_tag_with_multiple_categories(self):
        query = TAG_CATEGORY_DELIMITER.join(["root", "parent1", "parent2", "tag"])
        tokens = PostSearch.parse_query(query)
        assert len(tokens) == 1
        token = tokens[0]
        assert token.name == query
        assert token.category == PostSearchTokenCategory.TAG
        assert not token.negate

    def test_parse_negated_tag_with_nested_categories(self):
        query = TAG_CATEGORY_DELIMITER.join(["root", "parent1", "parent2", "tag"])
        negated_query = "-" + query
        tokens = PostSearch.parse_query(negated_query)
        assert len(tokens) == 1
        token = tokens[0]
        assert token.name == query
        assert token.category == PostSearchTokenCategory.TAG
        assert token.negate

    def test_parse_single_tag_with_wildcard(self):
        tokens = PostSearch.parse_query("tag1*")
        assert len(tokens) == 1
        assert tokens[0].name == "tag1*"
        assert tokens[0].category == PostSearchTokenCategory.TAG
        assert not tokens[0].negate

    def test_parse_single_negated_tag_with_wildcard(self):
        tokens = PostSearch.parse_query("-*negated_tag1")
        assert len(tokens) == 1
        assert tokens[0].name == "*negated_tag1"
        assert tokens[0].category == PostSearchTokenCategory.TAG
        assert tokens[0].negate

    def test_parse_multiple_tags(self):
        tokens = PostSearch.parse_query("tag1 tag2 tag3")
        assert len(tokens) == 3
        assert {tok.name for tok in tokens} == {"tag1", "tag2", "tag3"}
        for tok in tokens:
            assert tok.category == PostSearchTokenCategory.TAG
            assert not tok.negate

    def test_parse_multiple_negated_tags(self):
        tokens = PostSearch.parse_query("-tag1 -tag2 -tag3")
        assert len(tokens) == 3
        assert {tok.name for tok in tokens} == {"tag1", "tag2", "tag3"}
        for tok in tokens:
            assert tok.category == PostSearchTokenCategory.TAG
            assert tok.negate

    def test_parse_negated_and_non_negated_tags(self):
        tokens = PostSearch.parse_query("tag1 tag2 -tag3")
        assert len(tokens) == 3
        assert {tok.name for tok in tokens} == {"tag1", "tag2", "tag3"}

        assert tokens[0].category == PostSearchTokenCategory.TAG
        assert not tokens[0].negate

        assert tokens[1].category == PostSearchTokenCategory.TAG
        assert not tokens[1].negate

        # Last tag is negated
        assert tokens[2].category == PostSearchTokenCategory.TAG
        assert tokens[2].negate

    def test_parse_extra_space_between_tokens(self):
        tokens = PostSearch.parse_query("tag1\t tag2   -tag3")
        assert len(tokens) == 3
        assert {tok.name for tok in tokens} == {"tag1", "tag2", "tag3"}
        for tok in tokens:
            assert tok.category == PostSearchTokenCategory.TAG

    def test_parse_extra_space_start_and_end(self):
        tokens = PostSearch.parse_query("    -tag1 tag2 -tag3\t ")
        assert len(tokens) == 3
        assert {tok.name for tok in tokens} == {"tag1", "tag2", "tag3"}
        for tok in tokens:
            assert tok.category == PostSearchTokenCategory.TAG


class TestTokenCategories:
    @pytest.mark.parametrize("token_category", list(PostSearchTokenCategory))
    def test_correctly_identify_tag_categories_by_name(
        self, token_category: PostSearchTokenCategory
    ):
        if token_category.value.name:
            # This test does not test validation, only token identification
            with contextlib.suppress(ValidationError):
                tokens = PostSearch.parse_query(f"{token_category.value.name}=100")
                assert tokens[0].category == token_category

    @pytest.mark.parametrize("token_category", list(PostSearchTokenCategory))
    def test_correctly_identify_tag_categories_by_alias(
        self, token_category: PostSearchTokenCategory
    ):
        for alias in token_category.value.aliases:
            # This test does not test validation, only token identification
            with contextlib.suppress(ValidationError):
                tokens = PostSearch.parse_query(f"{alias}=100")
                assert tokens[0].category == token_category


class TestTokenArguments:
    @pytest.mark.parametrize("arg_relation", list(TokenArgRelation))
    def test_parse_filter_token_with_multiple_arg_relations(self, arg_relation):
        arg_relation_char = arg_relation.value
        query = f"id{arg_relation_char}100{arg_relation_char}200"
        with pytest.raises(ValidationError):
            PostSearch.parse_query(query)
