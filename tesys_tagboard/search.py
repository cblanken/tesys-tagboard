import re
from array import array
from dataclasses import dataclass
from dataclasses import field
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
from .validators import positive_int_validator
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


class UnsupportedSearchOperatorError(Exception):
    def __init__(
        self,
        operator: str,
        token: NamedToken,
        *args,
        **kwargs,
    ):
        msg = f'The provided search operator: "{operator}" is not supported for the token: "{token}"'  # noqa: E501
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
class SearchTokenBase:
    """A base class for modeling search tokens"""

    name: str
    desc: str
    aliases: tuple[str, ...]
    arg_validator: validators.RegexValidator
    allow_wildcard: bool
    allowed_arg_relations: tuple[TokenArgRelation, ...]


class SimpleSearchToken(SearchTokenBase):
    """A dataclass for simple search tokens accepting just the equal (=) operator
    and no wildcards"""

    name: str
    aliases: tuple[str, ...] = ()
    arg_validator: validators.RegexValidator
    allow_wildcard: bool = False
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (TokenArgRelation.EQUAL,)


@dataclass
class ComparisonSearchToken(SearchTokenBase):
    """A dataclass for search tokens that allow the following comparison operations
    of the token argument (>, <, and =)"""

    allow_wildcard: bool = False
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (
        TokenArgRelation.EQUAL,
        TokenArgRelation.LESS_THAN,
        TokenArgRelation.GREATER_THAN,
    )


@dataclass
class WildcardSearchToken(SearchTokenBase):
    """A dataclass for search tokens that accepts wildcards (*) in its token argument"""

    allow_wildcard: bool = True
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (TokenArgRelation.EQUAL,)


class TokenCategory(Enum):
    """Enum for categorizing tokens in Post search queries
    Note that these prefixes (besides the default `tag`)
    will be shadowed by any conflicting Tag prefixes since
    Tags take precendence when searching.
    """

    TAG = WildcardSearchToken(
        "",
        "The default (un-named) token. Used for searching tags.",
        (),
        tag_name_validator,
    )

    ID = ComparisonSearchToken("id", "The ID of a Post", (), positive_int_validator)

    TAG_ALIAS = WildcardSearchToken(
        "alias",
        "The name of a TagAlias. Allows wildcards.",
        ("tag_alias",),
        tag_name_validator,
    )

    COMMENT_BY = WildcardSearchToken(
        "comment_by",
        "The username of a user",
        ("comment", "cb"),
        username_validator,
    )

    COMMENT_COUNT = ComparisonSearchToken(
        "comment_count",
        "The number of comments on a Post. Accepts equality comparison operators =, <, >, <=, ) >=, and == which is equivalent to =.",  # noqa: E501
        ("cc",),
        positive_int_validator,
    )

    FAV = WildcardSearchToken(
        "favorited_by",
        "The username of a user who has favorited a Post",
        ("fav", "f"),
        username_validator,
    )

    FAV_COUNT = ComparisonSearchToken(
        "favorite_count",
        "The number of favorites received by a Post. Accepts equality comparison operators =,) <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
        ("fav_count", "fc"),
        validators.integer_validator,
    )

    HEIGHT = ComparisonSearchToken(
        "height",
        "The height of a Post (only applies to Images and Videos. Accepts equality comparison operators =, <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
        ("h",),
        validators.integer_validator,
    )

    WIDTH = ComparisonSearchToken(
        "width",
        "The width of a Post (only applies to Images and Videos. Accepts equa) lity comparison operators =, <, >, <=, >=, and == which is equivalent to =.",  # noqa: E501
        ("w",),
        validators.integer_validator,
    )

    RATING = ComparisonSearchToken(
        "rating",
        "The rating level of a Post. Accepts equality comparison operators =, <, >, <=) , >=, and == which is equivalent to =.",  # noqa: E501
        ("rate", "r"),
        validators.integer_validator,
    )

    RATING_NUM = ComparisonSearchToken(
        "rating_num",
        "The rating level of a Post. Accepts equality comparison operators =, <, >,) <=, >=, and == which is equivalent to =.",  # noqa: E501
        (),
        validators.integer_validator,
    )

    SOURCE = WildcardSearchToken(
        "source",
        "The source url of a Post. Allows wildcards.",
        ("src",),
        validators.URLValidator(),
    )

    UPLOADER = WildcardSearchToken(
        "uploaded_by",
        "The username of the uploader of a Post. Allows wildcards",
        ("up",),
        username_validator,
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


@dataclass
class NamedToken:
    """A parsed token for Post search

    Note that wildcards (*) are parsed out of the `arg` field into an array of
    index/positions. This facilitates validation of NamedTokens immediately
    after creation, since `arg` values can't allow the "*" character as part of the base
    value since it's reserved for wildcard usage. When the full arg with wildcards is
    needed it can simply be reconstructed from the `wildcard_positions`. This way
    the `NamedToken` initializes with a clean `arg` value.

    Attributes:
        category: TokenCategory
        name: str, the name of a tag or filter category
        arg: str,  an argument value for filter tokens
        arg_relation_str: str, a character defining the relationship between the arg
            and its value e.g. an exact match (=), less than (<), or greater than (>).
        arg_relation: TokenArgRelation, the parsed version of `arg_relation_str` which
            is used for matching against an allowed set of search operators
        wildcard_positions: array[int], an array of wild positions from the original
            arg input
        negate: bool, Posts matching this token should NOT be returned
    """

    category: TokenCategory
    name: str
    arg: str = ""
    arg_relation_str: str = ""
    arg_relation: TokenArgRelation | None = field(init=False)
    wildcard_positions: array[int] = field(init=False)
    negate: bool = False

    def __post_init__(self):
        self.arg_relation = (
            TokenArgRelation(self.arg_relation_str) if self.arg_relation_str else None
        )

        self.arg = self.arg.strip()
        wildcard_split = list(re.finditer(r"\*", self.arg))
        if len(wildcard_split) > 4:
            msg = "This token's argument has too many wildcards"
            raise ValidationError(msg)

        if len(wildcard_split) > 0:
            self.wildcard_positions = array(
                "I", [m.span()[0] for m in re.finditer(r"\*", self.arg)]
            )
        else:
            self.wildcard_positions = array("I", [])
        self.arg = self.arg.replace("*", "")

    def is_arg_valid(self):
        """Checks the validity of a Token's argument (arg) value

        Raises: ValidationError
        """
        validator = self.category.value.arg_validator
        if self.arg:
            validator(self.arg)

    def arg_with_wildcards(self):
        """Reconstructs original `arg` with wildcards from `wildcard_positions`"""

        arg = self.arg
        for pos in self.wildcard_positions:
            arg = self.arg[:pos] + "%" + self.arg[pos:]

        return arg


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

    def __init__(
        self,
        query: str,
        *,
        exclude_tags: QuerySet[Tag] | None = None,
        max_tags: int = 20,
        max_aliases: int = 20,
    ):
        self.query = query
        self.tokens: list[NamedToken] = self.parse_query(query)
        self.max_tags = max_tags
        self.max_aliases = max_aliases
        self.exclude_tags = exclude_tags
        self.partial: str = ""
        query_split = re.split(r"\s+", self.query)
        if len(query_split) > 0:
            self.partial = query_split[-1]

    @staticmethod
    def parse_query(query: str) -> list[NamedToken]:  # noqa: C901, PLR0912
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

            try:
                negate: bool = token_name[0] == "-"
            except IndexError:
                negate = False

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
                    msg = "Search query filters may only have one operator"
                    raise ValidationError(msg)
                try:
                    # NamedToken filter with an argument
                    token_category = TokenCategory.select(token_name)
                except SearchTokenNameError as err:
                    msg = f'The name "{token_name}" is not a valid filter'
                    raise ValidationError(msg) from err
                else:
                    if arg_relation not in [
                        x.value for x in token_category.value.allowed_arg_relations
                    ]:
                        msg = f'The {token_category.value.name} filter does not accept the "{arg_relation}" operator'  # noqa: E501
                        raise ValidationError(msg)

                named_token = NamedToken(
                    token_category,
                    name=token_name,
                    arg=token_arg,
                    arg_relation_str=arg_relation,
                    negate=negate,
                )
            else:
                # Invalid query
                msg = f'The query token "{token}" is invalid'
                raise ValidationError(msg)

            named_token.is_arg_valid()
            parsed_tokens.append(named_token)

        return parsed_tokens

    def get_search_expr(self) -> Q | None:  # noqa: C901, PLR0912
        """Builds a Post filter expression based on the provided `tokens`

        Note: tokens are validated when parsing the query string, so
        all token arguments are assumed to be safe here.

        Args:
            tokens: parsed tokens from a query string
        """
        if self.exclude_tags is not None:
            search_filter_expr = ~Q(tags__in=self.exclude_tags)
        else:
            search_filter_expr = Q()
        for token in self.tokens:
            token.is_arg_valid()
            match token.category:
                case TokenCategory.TAG:
                    token_expr = Q(tags__name=token.name)
                case TokenCategory.ID:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(pk__lt=token.arg)
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(pk=token.arg)
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(pk__gt=token.arg)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.COMMENT_COUNT:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(comment_count__lt=token.arg)
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(comment_count=token.arg)
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(comment_count__gt=token.arg)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.COMMENT_BY:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            if token.wildcard_positions:
                                token_expr = Q(
                                    comment__user__username__like=token.arg_with_wildcards()
                                )
                            else:
                                token_expr = Q(comment__user__username=token.arg)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case _:
                    continue

            if token.negate:
                token_expr = ~token_expr

            search_filter_expr = search_filter_expr & token_expr

        return search_filter_expr

    def get_posts(self) -> QuerySet[Post]:
        token_categories = [x.category for x in self.tokens]
        posts = Post.objects.all()
        if TokenCategory.COMMENT_COUNT in token_categories:
            posts = posts.annotate_comment_count()
        if search_expr := self.get_search_expr():
            return posts.filter(search_expr)
        return Post.objects.all()

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

        # Trim "-" from negated partial
        if len(partial) > 0 and partial[0] == "-":
            partial = partial[1:]

        # Don't yield autocompletion for duplicate filter or tag
        if len(list(filter(lambda tok: tok.name == partial, self.tokens))) > 1:
            tag_token_names = [
                tok.name for tok in self.tokens if tok.category is TokenCategory.TAG
            ]
        else:
            tag_token_names = [
                tok.name
                for tok in self.tokens
                # Yield autocomplete item if name matches partial exactly
                if tok.category is TokenCategory.TAG and tok.name != partial
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
