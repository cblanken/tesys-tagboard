import re
from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import TYPE_CHECKING

from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import QuerySet
from more_itertools import take

from .models import Post
from .models import Tag
from .models import TagAlias
from .models import TagCategory
from .validators import tag_name_validator
from .validators import username_validator


class SearchTokenNameError(Exception):
    def __init__(
        self,
        msg="The provided name does not match an existing TokenCategory",
        *args,
        **kwargs,
    ):
        super().__init__(msg, *args, **kwargs)


if TYPE_CHECKING:
    from collections.abc import Iterable


def tag_autocomplete(
    tags: QuerySet[Tag],
    include_partial: str | None = None,
    exclude_partial: str | None = None,
    exclude_tag_names: Iterable[str] | None = None,
    exclude_tags: QuerySet[Tag] | None = None,
) -> QuerySet[Tag]:
    if include_partial is not None:
        tags = tags.filter(name__icontains=include_partial)
    if exclude_partial is not None:
        tags = tags.exclude(name__contains=exclude_partial)
    if exclude_tag_names is not None:
        tags = tags.exclude(name__in=exclude_tag_names)
    if exclude_tags is not None:
        tags = tags.exclude(pk__in=exclude_tags)

    return tags


def tag_alias_autocomplete(
    aliases: QuerySet[TagAlias],
    include_partial: str | None = None,
    exclude_partial: str | None = None,
    exclude_alias_names: Iterable[str] | None = None,
    exclude_aliases: QuerySet[TagAlias] | None = None,
) -> QuerySet[TagAlias]:
    if include_partial is not None:
        aliases = TagAlias.objects.filter(name__icontains=include_partial)
    if exclude_partial is not None:
        aliases = TagAlias.objects.exclude(name__icontains=exclude_partial)
    if exclude_alias_names is not None:
        aliases = aliases.exclude(name__in=exclude_alias_names)
    if exclude_aliases is not None:
        aliases = aliases.exclude(pk__in=exclude_aliases)

    return aliases


class TokenArgRelation(Enum):
    """Enum for identifying how a token's arg should be interpreted"""

    EQUAL = "="
    LESS_THAN = "<"
    GREATER_THAN = ">"


@dataclass
class TokenType:
    name: str
    aliases: tuple[str, ...] = ()
    arg_validator: validators.RegexValidator | None = None
    allow_wildcard: bool = False
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (TokenArgRelation.EQUAL,)
    desc: str = ""


class ComparisonTokenType(TokenType):
    """A TokenType that accepts comparison arguments (>, <, and =)"""

    allowed_arg_relations = (
        TokenArgRelation.EQUAL,
        TokenArgRelation.LESS_THAN,
        TokenArgRelation.GREATER_THAN,
    )


class WildcardTokenType(TokenType):
    """A TokenType that accepts wildcards (*) in it's argument"""

    allow_wildcard = True


class TokenCategory(Enum):
    """Enum for categorizing tokens in Post search queries
    Note that these prefixes (besides the default `tag`)
    will be shadowed by any conflicting Tag prefixes since
    Tags take precendence when searching.
    """

    TAG = WildcardTokenType(
        "",
        (),
        tag_name_validator,
        desc="The default (un-named) token. Used for searching tags.",
    )

    ID = TokenType("id", (), validators.integer_validator, desc="The ID of a Post")

    TAG_ALIAS = WildcardTokenType(
        "alias",
        ("tag_alias",),
        tag_name_validator,
        desc="The name of a TagAlias. Allows wildcards.",
    )

    COMMENT_BY = WildcardTokenType(
        "comment_by",
        ("comment", "cb"),
        username_validator,
        desc="The username of a user",
    )

    COMMENT_COUNT = ComparisonTokenType(
        "comment_count",
        ("cc",),
        validators.integer_validator,
        desc="The number of comments on a Post. Accepts equality comparison operators =, <, >, <=, ) >=, and == which is equivalent to =.",  # noqa: E501
    )

    FAV = WildcardTokenType(
        "favorited_by",
        ("fav", "f"),
        username_validator,
        desc="The username of a user who has favorited a Post",
    )

    FAV_COUNT = ComparisonTokenType(
        "favorite_count",
        ("fav_count", "fc"),
        validators.integer_validator,
        desc="The number of favorites received by a Post. Accepts equality comparison operators =,) <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
    )

    HEIGHT = ComparisonTokenType(
        "height",
        ("h",),
        validators.integer_validator,
        desc="The height of a Post (only applies to Images and Videos. Accepts equality comparison operators =, <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
    )

    WIDTH = ComparisonTokenType(
        "width",
        ("w",),
        validators.integer_validator,
        desc="The width of a Post (only applies to Images and Videos. Accepts equa) lity comparison operators =, <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
    )

    RATING = ComparisonTokenType(
        "rating",
        ("rate", "r"),
        validators.integer_validator,
        desc="The rating level of a Post. Accepts equality comparison operators =, <, >, <=) , >=, and == which is equivalent to =.",  # noqa: E501
    )

    RATING_NUM = ComparisonTokenType(
        "rating_num",
        (),
        validators.integer_validator,
        desc="The rating level of a Post. Accepts equality comparison operators =, <, >,) <=, >=, and == which is equivalent to =.",  # noqa: E501
    )

    SOURCE = WildcardTokenType(
        "source",
        ("src",),
        validators.URLValidator(),
        desc="The source url of a Post. Allows wildcards.",
    )

    UPLOADER = WildcardTokenType(
        "uploaded_by",
        ("up",),
        username_validator,
        desc="The username of the uploader of a Post. Allows wildcards",
    )

    @classmethod
    def select(cls, name: str) -> TokenCategory:
        """Select token category by name or one of its aliases"""
        for tc, name_and_aliases in [
            (tc, [tc.value.name, *tc.value.aliases])
            for tc in TokenCategory.__members__.values()
        ]:
            if name in name_and_aliases:
                return tc

        raise SearchTokenNameError

    def is_valid(self) -> bool:
        if validator := self.value.arg_validator:
            try:
                validator(self.value)
            except ValidationError:
                return False
        return True


@dataclass
class NamedToken:
    """A parsed token for Post search

    Attributes:
        category: TokenCategory
        name: str, the name of a tag or filter category
        arg: str,  an argument value for filter tokens
        arg_relation: str, a character defining the relationship between the argument
            and its value e.g. an exact match (=), less than (<), or greater than (>).
        negate: bool, Posts matching this token should NOT be returned
    """

    category: TokenCategory
    name: str
    arg: str = ""
    arg_relation: str = ""
    negate: bool = False


@dataclass
class AutocompleteItem:
    token_category: TokenCategory
    name: str
    tag_category: TagCategory | None = None
    tag_id: int | None = None
    alias: str = ""
    extra: str = ""


class PostSearch:
    """Class to model a Post search query
    Models a post search query. Validates query arguments and retrieves autocompletion
    and post search results.

    Post search queries parse a space delimited string which is split into tokens
    corresponding to any of the values in the `TokenCategory` Enum.

    Tag categories may be searched by delimiting them with forward slashes. For example,
    a token of `Locations/Countries/Chile` has a top-level category of "Locations" a
    sub-category of "Countries" and a tag name of "Chile".

    Beyond simple tags, there are also many filtering options all of which are delimited
    by a =, <, or > symbol. For example, a token of `uploaded_by=pablo` has a token
    category of "uploaded_by" with an argument of "pablo" which can be a user's
    username. Some filters may also include wildcards, so following the previous
    example, `uploaded_by=pablo*` would return any posts uploaded by a user with the
    username prefix of "pablo". Similarly wildcards may appear at the beginning or in
    the middle of the arg. For example, `uploaded_by=*pablo` or `uploaded_by=pa*blo`

    All tags and filters may be prefixed with a "-" sign to indicate the search for that
    token should be inverted. For example a token of `-uploaded_by=pablo` would return
    any posts NOT uploaded by the user "pablo".
    """

    def __init__(self, query: str, max_tags: int = 20, max_aliases: int = 20):
        self.query = query
        self.tokens: list[NamedToken] = self.parse_query(query)
        self.max_tags = max_tags
        self.max_aliases = max_aliases
        self.exclude_tags: QuerySet[Tag] | None = None
        self.partial: str = ""
        query_split = re.split(r"\s+", self.query)
        if len(query_split) > 0:
            self.partial = query_split[-1]

    @staticmethod
    def parse_query(query: str) -> list[NamedToken]:
        """Parses a post search query string into named tokens

        Arguments:
            query: str, a query string containing space-delimited search tokens

        Raises:
            `ValidationError`
        """
        if query == "":
            return []
        tokens = re.split(r"\s+", query)
        valid_arg_relations = "".join([x.value for x in TokenArgRelation])
        filter_split_pattern = re.compile(r"([" + valid_arg_relations + r"])")
        parsed_tokens: list[NamedToken] = []
        for token in tokens:
            # Empty string
            if token == "":
                continue

            # Parse named tokens and simple tags
            token_name, *rest = filter_split_pattern.split(token, maxsplit=1)

            negate: bool = token_name[0] == "-"
            if negate:
                token_name = token_name[1:]
            if len(rest) == 0:
                # Anonymous token i.e. tag
                named_token = NamedToken(TokenCategory.TAG, token_name, negate=negate)
            elif len(rest) == 1:
                msg = "An invalid query split occurred"
                raise ValidationError(msg)
            elif len(rest) == 2:
                arg_relation = rest[0]
                token_arg = rest[1]

                if filter_split_pattern.search(token_arg):
                    msg = "Search query tokens may only have a single relation operator"
                    raise ValidationError(msg)
                try:
                    # NamedToken filter with an argument
                    token_category = TokenCategory.select(token_name)
                except SearchTokenNameError as err:
                    msg = f'The token name: "{token_name}" is not a valid filter'
                    raise ValidationError(msg) from err

                named_token = NamedToken(
                    token_category,
                    name=token_name,
                    arg=token_arg,
                    arg_relation=arg_relation,
                    negate=negate,
                )
            else:
                # Invalid query
                msg = f'The query token "{token}" is invalid.'
                raise ValidationError(msg)

            named_token.category.is_valid()
            parsed_tokens.append(named_token)

        return parsed_tokens

    def get_search_expr(self) -> Q:
        """Builds a Post filter expression based on the provided `tokens`

        Note: tokens are validated when parsing the query string, so
        all token arguments are assumed to be safe here.

        Args:
            tokens: parsed tokens from a query string
        """
        search_filter_expr = ~Q(tags__in=self.exclude_tags)
        for token in self.tokens:
            match token.category:
                case TokenCategory.TAG:
                    token_expr = Q(tags__in=[token.name])
                case TokenCategory.ID:
                    token_expr = Q(pk=token.arg)
                case TokenCategory.COMMENT_BY:
                    token_expr = Q(pk=token.arg)

                case _:
                    token_expr = None
                    continue

            if token.name:
                token_expr = ~token_expr

            search_filter_expr = search_filter_expr & token_expr

        return search_filter_expr

    def autocomplete(
        self,
        partial: str | None = None,
        exclude_tags: QuerySet[Tag] | None = None,
        *,
        show_filters: bool = True,
    ) -> Iterable[AutocompleteItem]:
        """Return autocomplete matches based on the existing search query and
        the provided `partial`"""
        if partial is None:
            partial = self.partial

        tag_token_names = [
            tok.name for tok in self.tokens if tok.category is TokenCategory.TAG
        ]
        tags = tag_autocomplete(
            Tag.objects.all(), partial, exclude_tag_names=tag_token_names
        )
        tags = take(self.max_tags, tags)
        tag_aliases = tag_alias_autocomplete(
            TagAlias.objects.all(), partial, exclude_alias_names=tag_token_names
        )
        tag_aliases = take(self.max_aliases, tag_aliases)

        autocomplete_items = chain(
            (
                AutocompleteItem(
                    TokenCategory.TAG,
                    tag.name,
                    tag.category,
                    tag.pk,
                    extra=tag.post_count,
                )
                for tag in tags
            ),
            (
                AutocompleteItem(
                    TokenCategory.TAG_ALIAS,
                    alias.tag.name,
                    alias.tag.category,
                    alias.tag.pk,
                    alias=alias.name,
                    extra=alias.tag.post_count,
                )
                for alias in tag_aliases
            ),
        )

        if show_filters:
            autocomplete_items = chain(
                (
                    AutocompleteItem(category, category.value.name)
                    for category in TokenCategory.__members__.values()
                    if partial in category.value.name
                ),
                autocomplete_items,
            )

        return autocomplete_items

    def get_posts(self):
        search_expr = self.get_search_expr()
        return Post.objects.filter(search_expr)
