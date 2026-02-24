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
from django.http import QueryDict
from more_itertools import take

from .enums import RatingLevel
from .enums import SupportedMediaType
from .models import Post
from .models import Tag
from .models import TagAlias
from .models import TagCategory
from .validators import mimetype_validator
from .validators import positive_int_validator
from .validators import rating_label_validator
from .validators import tag_name_validator
from .validators import username_validator
from .validators import wildcard_url_validator

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Generator
    from collections.abc import Iterable

    from colorfield.validators import RegexValidator

    from tesys_tagboard.users.models import User


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


class InvalidRatingLabelError(Exception):
    def __init__(
        self,
        msg="The provided rating label does not match an existing RatingLevel",
        *args,
        **kwargs,
    ):
        super().__init__(msg, *args, **kwargs)


class InvalidMimetypeError(Exception):
    mimetypes = ", ".join([smt.value.get_mimetype() for smt in SupportedMediaType])

    def __init__(
        self,
        msg=f"The provided mimetype does not match any of the supported mimetypes: {mimetypes}",  # noqa: E501
        *args,
        **kwargs,
    ):
        super().__init__(msg, *args, **kwargs)


def autocomplete_tags(
    tags: QuerySet[Tag],
    include_partial: str | None = None,
    exclude_partial: str | None = None,
    exclude_tag_names: Iterable[str] | None = None,
    exclude_tags: QuerySet[Tag] | None = None,
) -> Generator[AutocompleteItem]:
    if include_partial is not None:
        tags = tags.filter(name__icontains=include_partial)
    if exclude_partial is not None:
        tags = tags.exclude(name__contains=exclude_partial)
    if exclude_tag_names is not None:
        tags = tags.exclude(name__in=exclude_tag_names)
    if exclude_tags is not None:
        tags = tags.exclude(pk__in=exclude_tags)

    return (
        AutocompleteItem(
            TokenCategory.TAG,
            tag.name,
            tag.category,
            tag.pk,
            extra=tag.post_count,
        )
        for tag in tags
    )


def autocomplete_tag_aliases(
    aliases: QuerySet[TagAlias],
    include_partial: str | None = None,
    exclude_partial: str | None = None,
    exclude_alias_names: Iterable[str] | None = None,
    exclude_aliases: QuerySet[TagAlias] | None = None,
) -> Generator[AutocompleteItem]:
    if include_partial is not None:
        aliases = TagAlias.objects.filter(name__icontains=include_partial)
    if exclude_partial is not None:
        aliases = TagAlias.objects.exclude(name__icontains=exclude_partial)
    if exclude_alias_names is not None:
        aliases = aliases.exclude(name__in=exclude_alias_names)
    if exclude_aliases is not None:
        aliases = aliases.exclude(pk__in=exclude_aliases)

    return (
        AutocompleteItem(
            TokenCategory.TAG_ALIAS,
            alias.tag.name,
            alias.tag.category,
            alias.tag.pk,
            alias=alias.name,
            extra=alias.tag.post_count,
        )
        for alias in aliases
    )


class TokenArgRelation(Enum):
    """Enum for identifying how a token's arg should be interpreted"""

    EQUAL = "="
    LESS_THAN = "<"
    GREATER_THAN = ">"


@dataclass(kw_only=True)
class SearchTokenBase:
    """A base class for modeling search tokens"""

    name: str
    desc: str
    aliases: tuple[str, ...]
    arg_validator: validators.RegexValidator | Callable
    allow_wildcard: bool
    allowed_arg_relations: tuple[TokenArgRelation, ...]


@dataclass(kw_only=True)
class SimpleSearchToken(SearchTokenBase):
    """A dataclass for simple search tokens accepting just the equal (=) operator
    and no wildcards. No aliases are included by default."""

    aliases: tuple[str, ...] = ()
    allow_wildcard: bool = False
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (TokenArgRelation.EQUAL,)


@dataclass(kw_only=True)
class ComparisonSearchToken(SearchTokenBase):
    """A dataclass for search tokens that allow the following comparison operations
    of the token argument (>, <, and =)"""

    aliases: tuple[str, ...] = ()
    allow_wildcard: bool = False
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (
        TokenArgRelation.EQUAL,
        TokenArgRelation.LESS_THAN,
        TokenArgRelation.GREATER_THAN,
    )


@dataclass(kw_only=True)
class WildcardSearchToken(SearchTokenBase):
    """A dataclass for search tokens that accepts wildcards (*) in its token argument"""

    aliases: tuple[str, ...] = ()
    allow_wildcard: bool = True
    allowed_arg_relations: tuple[TokenArgRelation, ...] = (TokenArgRelation.EQUAL,)
    wildcard_arg_validator: RegexValidator | Callable | None = None

    def __post_init__(self):
        if self.wildcard_arg_validator is None:
            self.wildcard_arg_validator = self.arg_validator


class TokenCategory(Enum):
    """Enum for categorizing tokens in Post search queries
    Note that these prefixes (besides the default `tag`)
    will be shadowed by any conflicting Tag prefixes since
    Tags take precendence when searching.
    """

    TAG = WildcardSearchToken(
        name="",
        desc="The default (un-named) token. Used for searching tags.",
        arg_validator=tag_name_validator,
    )

    TAG_ID = SimpleSearchToken(
        name="tag_id",
        desc="The ID of a tag.",
        arg_validator=positive_int_validator,
    )

    POST_ID = ComparisonSearchToken(
        name="id",
        desc="The ID of a Post",
        arg_validator=positive_int_validator,
    )

    TAG_ALIAS = WildcardSearchToken(
        name="alias",
        desc="The name of a TagAlias. Allows wildcards.",
        aliases=("tag_alias",),
        arg_validator=tag_name_validator,
    )

    TAG_COUNT = ComparisonSearchToken(
        name="tag_count",
        desc="The number of tags on a Post. Accepts comparison operators =, <, >",
        aliases=("tc",),
        arg_validator=positive_int_validator,
    )

    COMMENT_BY = WildcardSearchToken(
        name="comment_by",
        desc="The username of a user",
        aliases=("comment", "cb"),
        arg_validator=username_validator,
    )

    COMMENT_COUNT = ComparisonSearchToken(
        name="comment_count",
        desc="The number of comments on a Post. Accepts comparison operators =, <, >",
        aliases=("cc",),
        arg_validator=positive_int_validator,
    )

    FAV_COUNT = ComparisonSearchToken(
        name="favorite_count",
        desc="The number of favorites recieved by a Post. Accepts comparison operators =, <, >",  # noqa: E501
        aliases=("fav_count", "fc"),
        arg_validator=positive_int_validator,
    )

    HEIGHT = ComparisonSearchToken(
        name="height",
        desc="The height of a Post (only applies to Images and Videos). Accepts comparison operators =, <, >",  # noqa: E501
        aliases=("h",),
        arg_validator=validators.integer_validator,
    )

    WIDTH = ComparisonSearchToken(
        name="width",
        desc="The width of a Post (only applies to Images and Videos.  Accepts comparison operators =, <, >",  # noqa: E501
        aliases=("w",),
        arg_validator=validators.integer_validator,
    )

    RATING_LABEL = SimpleSearchToken(
        name="rating_label",
        desc="The rating of a Post. Accepts any current rating level label",
        aliases=("rate", "r"),
        arg_validator=rating_label_validator,
    )

    RATING_NUM = ComparisonSearchToken(
        name="rating_num",
        desc="The rating level of a Post. Accepts equality comparison operators.",
        arg_validator=validators.integer_validator,
    )

    SOURCE = WildcardSearchToken(
        name="source",
        desc="The source url of a Post. Allows wildcards.",
        aliases=("src",),
        arg_validator=validators.URLValidator(),
        wildcard_arg_validator=wildcard_url_validator,
    )

    UPLOADED_BY = WildcardSearchToken(
        name="uploaded_by",
        desc="The username of the uploader of a Post. Allows wildcards.",
        aliases=("up",),
        arg_validator=username_validator,
        wildcard_arg_validator=username_validator,
    )

    MIMETYPE = SimpleSearchToken(
        name="mimetype",
        desc="The MIME type of the post's file",
        aliases=("mime",),
        arg_validator=mimetype_validator,
    )

    @classmethod
    def select(cls, name: str) -> TokenCategory:
        """Select token category by name or one of its aliases

        Raises: `SearchTokenNameError`
        """
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
    arg_relation_str: str = TokenArgRelation.EQUAL.value
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

        Note: Most WildcardSearchToken(s) will use the same validator for the wildcard
        and non-wildcard variants, but some may need to provide a more permissive
        validator to allow for incomplete arguments (e.g. URLs) which is why the
        WildcardSearchToken may override the base `arg_validator` on an as-needed basis.

        Raises: `ValidationError`
        """
        if isinstance(self.category.value, WildcardSearchToken):
            validator = self.category.value.wildcard_arg_validator
        else:
            validator = self.category.value.arg_validator

        if self.arg:
            validator(self.arg)

    def arg_with_wildcards(self):
        """Reconstructs original `arg` with wildcards from `wildcard_positions`"""

        arg = self.arg
        for pos in self.wildcard_positions:
            arg = arg[:pos] + "%" + arg[pos:]

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
    token should be inverted. For example a token of `-uploaded_by=pablo` would exclude
    any posts uploaded by the user "pablo" in the results.
    """

    valid_arg_relations = "".join([x.value for x in TokenArgRelation])
    filter_split_pattern = re.compile(r"([" + valid_arg_relations + r"])")

    def __init__(
        self,
        query: str | QueryDict,
        *,
        exclude_tags: QuerySet[Tag] | None = None,
        max_tags: int = 20,
        max_aliases: int = 20,
    ):
        self.query = query
        self.max_tags = max_tags
        self.max_aliases = max_aliases
        self.exclude_tags = exclude_tags
        self.partial: str = ""
        if isinstance(self.query, QueryDict):
            self.tokens = self.parse_querydict(self.query)
        elif isinstance(self.query, str):
            query_split = re.split(r"\s+", self.query)
            if len(query_split) > 0:
                self.partial = query_split[-1]

            self.tokens: list[NamedToken] = self.parse_query(self.query)

    def parse_token(self, token: str) -> NamedToken | None:
        """Parses and validates a query token

        Raises: `ValidationError`
        """
        # Empty string
        if token == "":
            return None

        # Parse named tokens and simple tags
        token_name, *rest = self.filter_split_pattern.split(token, maxsplit=1)
        negate: bool = token_name[0] == "-"

        if negate:
            token_name = token_name[1:]

        if len(rest) == 0:
            # Anonymous token i.e. tag
            return NamedToken(TokenCategory.TAG, token_name, token_name, negate=negate)

        if len(rest) == 1:
            msg = "An invalid query split occurred"
            raise ValidationError(msg)

        if len(rest) == 2:
            arg_relation = rest[0]
            token_arg = rest[1]

            if self.filter_split_pattern.search(token_arg):
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

            return NamedToken(
                token_category,
                name=token_name,
                arg=token_arg,
                arg_relation_str=arg_relation,
                negate=negate,
            )

        # Invalid token
        msg = f'The query token "{token}" is invalid'
        raise ValidationError(msg)

    def parse_querydict(self, querydict: QueryDict) -> list[NamedToken]:
        """Parses a post search query submitted via form instead of a query string.

        Each parameter should match an existing `TokenCategory` with the exception of
        tags which are submitted as a list of tag IDs in the `tagset` parameter.

        Raises: `ValidationError`
        """

        parsed_tokens: list[NamedToken] = []

        # Parse tag tokens
        tagset = querydict.getlist("tagset")
        for tag_id in tagset:
            tag_token = NamedToken(
                TokenCategory.TAG_ID, TokenCategory.TAG_ID.value.name, tag_id
            )

            tag_token.is_arg_valid()
            parsed_tokens.append(tag_token)

        # Parse other tokens
        for key, value in querydict.items():
            try:
                token_category = TokenCategory.select(key)

                arg_relation = querydict.get(
                    f"{key}_relation", token_category.value.allowed_arg_relations[0]
                )

                if arg_relation not in [
                    x.value for x in token_category.value.allowed_arg_relations
                ]:
                    msg = f'The {token_category.value.name} filter does not accept the "{arg_relation}" operator'  # noqa: E501
                    raise ValidationError(msg)

                negate = bool(querydict.get(f"{key}_negate", False))

                named_token = NamedToken(
                    token_category,
                    name=key,
                    arg=str(value),
                    arg_relation_str=str(arg_relation),
                    negate=negate,
                )

                named_token.is_arg_valid()
                parsed_tokens.append(named_token)

            except SearchTokenNameError:
                # Bad tokens are ignored
                pass

        return parsed_tokens

    def parse_query(self, query: str) -> list[NamedToken]:
        """Parses a post search query into named tokens.

        Arguments:
            query: str, a query string containing space-delimited search tokens

        Raises:
            `ValidationError`
        """
        if query == "":
            return []
        tokens = re.split(r"\s+", query)
        parsed_tokens: list[NamedToken] = []
        for token in tokens:
            if named_token := self.parse_token(token):
                named_token.is_arg_valid()
                parsed_tokens.append(named_token)

        return parsed_tokens

    def get_search_conditions(self) -> list[Q] | None:  # noqa: C901, PLR0912, PLR0915
        """Builds a Post filter expression based on the provided `tokens`

        Note: tokens are validated when parsing the query string, so
        all token arguments are assumed to be safe here.

        Args:
            tokens: parsed tokens from a query string
        """
        if self.exclude_tags is not None:
            search_conditions = [~Q(tags__in=self.exclude_tags)]
        else:
            search_conditions: list[Q] = []
        for token in self.tokens:
            match token.category:
                case TokenCategory.TAG:
                    if token.wildcard_positions:
                        token_expr = Q(tags__name__like=token.arg_with_wildcards())
                    else:
                        token_expr = Q(tags__name=token.arg)
                case TokenCategory.TAG_ID:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(tags__pk=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.POST_ID:
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
                case TokenCategory.FAV_COUNT:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(fav_count__lt=int(token.arg))
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(fav_count=int(token.arg))
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(fav_count__gt=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.TAG_COUNT:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(tag_count__lt=int(token.arg))
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(tag_count=int(token.arg))
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(tag_count__gt=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.RATING_NUM:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(rating_level__lt=int(token.arg))
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(rating_level=int(token.arg))
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(rating_level__gt=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.RATING_LABEL:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            rating = RatingLevel.select(token.arg)
                            if rating is None:
                                raise InvalidRatingLabelError
                            token_expr = Q(rating_level=rating.value)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.SOURCE:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            if token.wildcard_positions:
                                token_expr = Q(src_url__like=token.arg_with_wildcards())
                            else:
                                token_expr = Q(src_url=token.arg)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.UPLOADED_BY:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            if token.wildcard_positions:
                                token_expr = Q(
                                    uploader__username__like=token.arg_with_wildcards()
                                )
                            else:
                                token_expr = Q(uploader__username=token.arg)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.HEIGHT:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(image__height__lt=int(token.arg))
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(image__height=int(token.arg))
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(image__height__gt=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.WIDTH:
                    match token.arg_relation:
                        case TokenArgRelation.LESS_THAN:
                            token_expr = Q(image__width__lt=int(token.arg))
                        case TokenArgRelation.EQUAL:
                            token_expr = Q(image__width=int(token.arg))
                        case TokenArgRelation.GREATER_THAN:
                            token_expr = Q(image__width__gt=int(token.arg))
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case TokenCategory.MIMETYPE:
                    match token.arg_relation:
                        case TokenArgRelation.EQUAL:
                            smt = SupportedMediaType.find(token.arg)
                            if smt is None:
                                raise InvalidMimetypeError
                            token_expr = Q(type=smt.name)
                        case _:
                            raise UnsupportedSearchOperatorError(
                                token.arg_relation_str, token
                            )
                case _:
                    continue

            if token.negate:
                token_expr = ~token_expr

            search_conditions.append(token_expr)

        return search_conditions

    def get_posts(self) -> QuerySet[Post]:
        token_categories = [x.category for x in self.tokens]
        posts = Post.objects.all()
        if TokenCategory.COMMENT_COUNT in token_categories:
            posts = posts.annotate_comment_count()
        if TokenCategory.FAV_COUNT in token_categories:
            posts = posts.annotate_fav_count()
        if TokenCategory.TAG_COUNT in token_categories:
            posts = posts.annotate_tag_count()
        if search_conditions := self.get_search_conditions():
            for condition in search_conditions:
                posts = posts.filter(condition)
            return posts.distinct()
        return Post.objects.all()

    def autocomplete(
        self,
        partial: str | None = None,
        exclude_tags: QuerySet[Tag] | None = None,
        user: User | None = None,
        *,
        show_filters: bool = True,
    ) -> chain[AutocompleteItem]:
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

        if user:
            tag_autocompletions = autocomplete_tags(
                Tag.objects.for_user(user), partial, exclude_tag_names=tag_token_names
            )
            tag_alias_autocompletions = autocomplete_tag_aliases(
                TagAlias.objects.for_user(user),
                partial,
                exclude_alias_names=tag_token_names,
            )
        else:
            tag_autocompletions = autocomplete_tags(
                Tag.objects.all(), partial, exclude_tag_names=tag_token_names
            )

            tag_alias_autocompletions = autocomplete_tag_aliases(
                TagAlias.objects.all(), partial, exclude_alias_names=tag_token_names
            )

        tag_autocompletions = take(self.max_tags, tag_autocompletions)
        tag_alias_autocompletions = take(self.max_aliases, tag_alias_autocompletions)
        autocomplete_items = chain(tag_autocompletions, tag_alias_autocompletions)

        if show_filters:
            # Add search filters to autocomplete items
            autocomplete_items = chain(
                (
                    AutocompleteItem(category, category.value.name)
                    for category in TokenCategory.__members__.values()
                    if partial in category.value.name
                ),
                autocomplete_items,
            )

        return autocomplete_items
