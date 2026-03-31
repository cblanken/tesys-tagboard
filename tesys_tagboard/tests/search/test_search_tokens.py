from itertools import chain
from typing import TYPE_CHECKING

from tesys_tagboard.search import PostSearchTokenCategory

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
