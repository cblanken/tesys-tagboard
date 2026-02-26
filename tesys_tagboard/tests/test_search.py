import contextlib
from itertools import chain

import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.enums import RatingLevel
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
from tesys_tagboard.search import PostSearch
from tesys_tagboard.search import PostSearchTokenCategory
from tesys_tagboard.search import TokenArgRelation
from tesys_tagboard.search import autocomplete_tag_aliases
from tesys_tagboard.search import autocomplete_tags

from .factories import CommentFactory
from .factories import FavoriteFactory
from .factories import ImageFactory
from .factories import PostFactory
from .factories import TagFactory
from .factories import UserFactory


class TestSearchTokenCategories:
    def test_no_duplicate_aliases(self):
        """Ensure available TokenCategory types don't have any duplicate aliases"""
        token_aliases = list(
            chain(*[tok.value.aliases for tok in PostSearchTokenCategory])
        )
        assert len(token_aliases) == len(set(token_aliases))


@pytest.mark.django_db
class TestTagAutocomplete:
    def test_autocomplete_included_by_name_partial(self, db):
        tags = autocomplete_tags(Tag.objects.all(), "blue")
        tag_names = [tag.name for tag in tags]
        assert "blue-jeans" in tag_names
        assert "blue" in tag_names
        assert "blue-gray" in tag_names
        assert "blueberry" in tag_names
        assert "red_vs._blue" in tag_names
        assert "sky-blue" in tag_names
        assert len(tag_names) == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        tags = autocomplete_tags(Tag.objects.all(), exclude_partial="blue")
        tag_names = [tag.name for tag in tags]
        assert "blue-jeans" not in tag_names
        assert "blue" not in tag_names
        assert "blue-gray" not in tag_names
        assert "blueberry" not in tag_names
        assert "sky-blue" not in tag_names

    def test_autocomplete_excluded_by_tag_name(self, db):
        tags = autocomplete_tags(
            Tag.objects.all(), exclude_tag_names=["violet", "white", "yellow"]
        )
        tag_names = [tag.name for tag in tags]
        assert "violet" not in tag_names
        assert "white" not in tag_names
        assert "yellow" not in tag_names
        assert "white-rapids" in tag_names
        assert "yellow-flowers" in tag_names
        assert "violet-hyacinth" in tag_names

    def test_autocomplete_excluded_by_tag(self, db):
        copyright_category = TagCategory.objects.get(name="copyright")
        exclude_tags = Tag.objects.filter(category=copyright_category)
        tag_items = autocomplete_tags(Tag.objects.all(), exclude_tags=exclude_tags)
        for item in tag_items:
            assert item.name not in [tag.name for tag in exclude_tags]


@pytest.mark.django_db
class TestTagAliasAutocomplete:
    def test_autocomplete_included_by_name_partial(self, db):
        aliases = autocomplete_tag_aliases(TagAlias.objects.all(), "blue")
        alias_names = [alias.alias for alias in aliases]
        assert "bluejeans" in alias_names
        assert "gray-blue" in alias_names
        assert "blue-berry" in alias_names
        assert "red_v._blue" in alias_names
        assert "red_vs_blue" in alias_names
        assert "red_x_blue" in alias_names
        assert len(alias_names) == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        aliases = autocomplete_tag_aliases(
            TagAlias.objects.all(), exclude_partial="red"
        )
        alias_names = [alias.alias for alias in aliases]
        assert "red_v._blue" not in alias_names
        assert "red_vs_blue" not in alias_names
        assert "red_x_blue" not in alias_names
        assert "r_v._b" in alias_names
        assert "r_vs._b" in alias_names

    def test_autocomplete_excluded_by_alias_name(self, db):
        aliases = autocomplete_tag_aliases(
            TagAlias.objects.all(),
            exclude_alias_names=["Justin K", "Solomon S", "Z. Zolan"],
        )
        alias_names = [alias.alias for alias in aliases]
        assert "Justin K" not in alias_names
        assert "Solomon S" not in alias_names
        assert "Z. Zolan" not in alias_names

    def test_autocomplete_excluded_by_alias(self, db):
        copyright_category = TagCategory.objects.get(name="copyright")
        exclude_aliases = TagAlias.objects.filter(tag__category=copyright_category)
        aliases = autocomplete_tag_aliases(
            TagAlias.objects.all(), exclude_aliases=exclude_aliases
        )

        for alias_item in aliases:
            assert alias_item.alias not in [alias.name for alias in exclude_aliases]


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
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert not ps.tokens[0].negate

    def test_parse_single_negated_tag(self):
        ps = PostSearch("-tag1")
        assert len(ps.tokens) == 1
        assert ps.tokens[0].name == "tag1"
        assert ps.tokens[0].category == PostSearchTokenCategory.TAG
        assert ps.tokens[0].negate

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

    @pytest.mark.parametrize("arg_relation", list(TokenArgRelation))
    def test_parse_filter_token_with_multiple_arg_relations(self, arg_relation):
        arg_relation_char = arg_relation.value
        query = f"id{arg_relation_char}100{arg_relation_char}200"
        with pytest.raises(ValidationError):
            PostSearch(query)


@pytest.mark.django_db
class TestPostAdvancedSearchAutocomplete:
    def test_exclude_already_mentioned_tags(self):
        ps = PostSearch("amber amaranth")
        items = ps.autocomplete("am")
        item_names = [x.name for x in items]
        assert "amaranth-pink" in item_names
        assert "amaranth-purple" in item_names
        assert "amaranth" not in item_names
        assert "amber" not in item_names

    def test_include_tags_and_aliases(self):
        ps = PostSearch("red")
        items = list(ps.autocomplete())

        # Tags
        tag_names = [
            item.name
            for item in items
            if item.token_category == PostSearchTokenCategory.TAG
        ]
        assert "red" in tag_names
        assert "red_vs._blue" in tag_names

        # Aliases
        alias_names = [
            item.alias
            for item in items
            if item.token_category == PostSearchTokenCategory.TAG_ALIAS
        ]
        assert "red_v._blue" in alias_names
        assert "red_vs_blue" in alias_names
        assert "red_x_blue" in alias_names

    def test_exclude_negated_mentioned_tags(self):
        ps = PostSearch("-green")
        items = ps.autocomplete("gree")
        item_names = [x.name for x in items]
        assert "evergreen" in item_names
        assert "lime-green" in item_names
        assert "green" not in item_names

    def test_yes_filters(self):
        ps = PostSearch("")
        items = list(ps.autocomplete(show_filters=True))
        item_categories = {item.token_category for item in items}
        for tc in PostSearchTokenCategory:
            assert tc in item_categories

    def test_no_filters(self):
        ps = PostSearch("")
        items = ps.autocomplete(show_filters=False)
        item_categories = {item.token_category for item in items}
        item_categories.remove(PostSearchTokenCategory.TAG)
        item_categories.remove(PostSearchTokenCategory.TAG_ALIAS)
        for tc in PostSearchTokenCategory:
            assert tc not in item_categories

    def test_complete_with_leading_negation(self):
        ps = PostSearch("blue -blu")
        items = ps.autocomplete("-blu")
        item_names = [x.name for x in items]
        assert "blue-jeans" in item_names
        assert "blue-gray" in item_names
        assert "blueberry" in item_names
        assert "sky-blue" in item_names


@pytest.mark.django_db
class TestPostAdvancedSearchTags:
    def test_empty_query(self):
        PostFactory.create_batch(10)
        ps = PostSearch("")
        posts = ps.get_posts()
        assert len(posts.difference(Post.objects.all())) == 0

    def test_only_include_tags(self):
        common_tag = TagFactory.create()

        included_posts = PostFactory.create_batch(10)
        included_tag = TagFactory.create()
        for post in included_posts:
            post.tags.add(included_tag)
            post.tags.add(common_tag)

        not_included_posts = PostFactory.create_batch(10)
        not_included_tag = TagFactory.create()
        for post in not_included_posts:
            post.tags.add(not_included_tag)
            post.tags.add(common_tag)

        ps = PostSearch(f"{included_tag.name}")
        posts = ps.get_posts()
        assert len(posts.difference(Post.objects.filter(tags__in=[included_tag]))) == 0
        assert len(
            posts.difference(Post.objects.filter(tags__in=[not_included_tag]))
        ) == len(not_included_posts)

    def test_include_tag_with_wildcard(self):  # noqa: PLR0915
        wild = TagFactory.create(name="wild")
        wilder = TagFactory.create(name="wilder")
        wilderness = TagFactory.create(name="wilderness")
        ness = TagFactory.create(name="ness")
        dress = TagFactory.create(name="dress")
        bless = TagFactory.create(name="bless")

        just_wild_post = PostFactory.create()
        just_wild_post.tags.add(wild)

        all_wild_post = PostFactory.create()
        all_wild_post.tags.add(wild, wilder, wilderness)

        all_wilder_post = PostFactory.create()
        all_wilder_post.tags.add(wilder, wilderness)

        just_wilderness_post = PostFactory.create()
        just_wilderness_post.tags.add(wilderness)

        ess_post = PostFactory.create()
        ess_post.tags.add(ness, dress, bless)

        ness_post = PostFactory.create()
        ness_post.tags.add(wilderness, ness)

        bless_post = PostFactory.create()
        bless_post.tags.add(bless)

        wild_ps = PostSearch("wild*")
        wild_posts = wild_ps.get_posts()
        assert just_wild_post in wild_posts
        assert all_wild_post in wild_posts
        assert all_wilder_post in wild_posts
        assert just_wilderness_post in wild_posts
        assert ness_post in wild_posts
        assert ess_post not in wild_posts

        wilder_ps = PostSearch("wilder*")
        wilder_posts = wilder_ps.get_posts()
        assert all_wild_post in wilder_posts
        assert all_wilder_post in wilder_posts
        assert just_wilderness_post in wilder_posts
        assert ness_post in wilder_posts
        assert just_wild_post not in wilder_posts

        wilderness_ps = PostSearch("wilderness*")
        wilderness_posts = wilderness_ps.get_posts()
        assert all_wild_post in wilderness_posts
        assert all_wilder_post in wilderness_posts
        assert just_wilderness_post in wilderness_posts
        assert ness_post in wilderness_posts
        assert just_wild_post not in wilderness_posts

        ess_ps = PostSearch("*ess")
        ess_posts = ess_ps.get_posts()
        assert ess_post in ess_posts
        assert ness_post in ess_posts
        assert bless_post in ess_posts
        assert just_wilderness_post in ess_posts
        assert just_wild_post not in ess_posts

        ness_ps = PostSearch("*ness")
        ness_posts = ness_ps.get_posts()
        assert ess_post in ness_posts
        assert ness_post in ness_posts
        assert just_wilderness_post in ness_posts
        assert bless_post not in ness_posts
        assert just_wild_post not in ness_posts

    def test_only_exclude_tags(self):
        tags = TagFactory.create_batch(5)
        test_posts = PostFactory.create_batch(5)

        for i, post in enumerate(test_posts):
            post.tags.add(tags[i])

        posts = PostSearch(f"-{tags[0].name} -{tags[1].name}").get_posts()
        assert test_posts[0] not in posts
        assert test_posts[1] not in posts
        assert test_posts[2] in posts
        assert test_posts[3] in posts
        assert test_posts[4] in posts

    def test_exclude_tag_with_wildcard(self):
        common_tag = TagFactory.create(name="mighty")
        tags = TagFactory.create_batch(5)
        test_posts = PostFactory.create_batch(5)

        for i, post in enumerate(test_posts):
            post.tags.add(common_tag, tags[i])

        wildcard_tag = TagFactory.create(name="mire")
        test_posts[0].tags.add(wildcard_tag)
        test_posts[1].tags.add(wildcard_tag)
        test_posts[2].tags.add(wildcard_tag)

        posts = PostSearch("-mir*").get_posts()
        assert test_posts[0] not in posts
        assert test_posts[1] not in posts
        assert test_posts[2] not in posts
        assert test_posts[3] in posts
        assert test_posts[4] in posts

    def test_include_and_exclude_tags_with_wildcards(self):
        common_tag = TagFactory.create(name="mighty")
        tags = TagFactory.create_batch(5)
        test_posts = PostFactory.create_batch(5)

        for i, post in enumerate(test_posts):
            post.tags.add(common_tag, tags[i])

        wildcard_tag = TagFactory.create(name="mire")
        test_posts[0].tags.add(wildcard_tag)
        test_posts[1].tags.add(wildcard_tag)
        test_posts[2].tags.add(wildcard_tag)

        special_tag = TagFactory.create(name="special")
        speciality_tag = TagFactory.create(name="speciality")

        test_posts[4].tags.add(special_tag, speciality_tag)

        posts = PostSearch("-mir* speci*").get_posts()
        assert test_posts[0] not in posts
        assert test_posts[1] not in posts
        assert test_posts[2] not in posts
        assert test_posts[3] not in posts
        assert test_posts[4] in posts


@pytest.mark.django_db
class TestPostAdvancedTagID:
    def test_id_equal(self):
        post = PostFactory.create()
        tag = TagFactory.create()
        post.tags.add(tag)
        ps = PostSearch(f"tag_id={tag.pk}")
        posts = ps.get_posts()
        assert len(posts) == 1
        assert posts[0].pk == post.pk


@pytest.mark.django_db
class TestPostAdvancedSearchTagAliases:
    def test_include_tag_alias(self):
        pass

    def test_include_tag_alias_with_wildcard(self):
        pass

    def test_exclude_tag_alias_with_wildcard(self):
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchPostID:
    def test_id_equal(self):
        post = PostFactory.create()
        ps = PostSearch(f"id={post.pk}")
        posts = ps.get_posts()
        assert len(posts) == 1
        assert posts[0].pk == post.pk

    def test_id_less_than(self):
        post1 = PostFactory.create(id=1)
        post2 = PostFactory.create(id=2)
        post3 = PostFactory.create(id=3)
        post4 = PostFactory.create(id=4)
        post5 = PostFactory.create(id=5)
        ps = PostSearch(f"id<{post3.pk}")
        posts = ps.get_posts()
        post_ids = set(posts.values_list("pk", flat=True))
        assert post_ids == {post1.pk, post2.pk}
        assert post4.pk not in post_ids
        assert post5.pk not in post_ids

    def test_id_greater_than(self):
        post1 = PostFactory.create(id=1)
        post2 = PostFactory.create(id=2)
        post3 = PostFactory.create(id=3)
        post4 = PostFactory.create(id=4)
        post5 = PostFactory.create(id=5)
        ps = PostSearch(f"id>{post3.pk}")
        posts = ps.get_posts()
        post_ids = set(posts.values_list("pk", flat=True))
        assert post_ids == {post4.pk, post5.pk}
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids

    def test_negative_arg(self):
        post = PostFactory.create()
        with pytest.raises(ValidationError):
            PostSearch(f"id=-{post.pk}")


@pytest.mark.django_db
class TestPostAdvancedSearchCommentCount:
    def test_comment_count_equal(self):
        post1 = PostFactory.create()
        post2 = PostFactory.create()
        post3 = PostFactory.create()

        comment_count = 10
        CommentFactory.create_batch(comment_count, post=post3)

        ps = PostSearch(f"comment_count={comment_count}")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids
        assert post3.pk in post_ids

    def test_comment_count_less_than(self):
        post1 = PostFactory.create()
        post2 = PostFactory.create()
        post3 = PostFactory.create()
        CommentFactory.create_batch(5, post=post2)
        CommentFactory.create_batch(10, post=post3)

        ps = PostSearch("comment_count<10")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk in post_ids
        assert post2.pk in post_ids
        assert post3.pk not in post_ids

    def test_comment_count_greater_than(self):
        post1 = PostFactory.create()
        post2 = PostFactory.create()
        post3 = PostFactory.create()
        CommentFactory.create_batch(1, post=post1)
        CommentFactory.create_batch(5, post=post2)
        CommentFactory.create_batch(10, post=post3)

        ps = PostSearch("comment_count>1")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk not in post_ids
        assert post2.pk in post_ids
        assert post3.pk in post_ids

    def test_negative_arg(self):
        PostFactory.create()
        with pytest.raises(ValidationError):
            PostSearch("comment_count>-5")


@pytest.mark.django_db
class TestPostAdvancedSearchCommentedBy:
    def test_commented_by_user(self):
        post1 = PostFactory.create()
        post2 = PostFactory.create()
        post3 = PostFactory.create()
        commenter = UserFactory.create()
        other = UserFactory.create()
        CommentFactory.create(post=post1, user=commenter)
        CommentFactory.create(post=post2, user=commenter)
        CommentFactory.create(post=post3, user=other)

        ps = PostSearch(f"comment_by={commenter.username}")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk in post_ids
        assert post2.pk in post_ids
        assert post3.pk not in post_ids

    def test_commented_by_user_with_wildcard(self):
        post1 = PostFactory.create()
        post2 = PostFactory.create()
        post3 = PostFactory.create()
        commenter1 = UserFactory.create(username="tom123")
        commenter2 = UserFactory.create(username="tommy")
        commenter3 = UserFactory.create(username="angela")
        CommentFactory.create(post=post1, user=commenter1)
        CommentFactory.create(post=post2, user=commenter2)
        CommentFactory.create(post=post3, user=commenter3)

        ps = PostSearch("comment_by=tom*")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk in post_ids
        assert post2.pk in post_ids
        assert post3.pk not in post_ids


@pytest.mark.django_db
class TestPostAdvancedSearchFavoritedCount:
    def test_favorited_equal(self):
        post1, post2, post3, post4 = PostFactory.create_batch(4)

        FavoriteFactory.create_batch(5, post=post2)
        FavoriteFactory.create_batch(10, post=post3)
        FavoriteFactory.create_batch(50, post=post4)

        ps = PostSearch("favorite_count=10")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids
        assert post3.pk in post_ids
        assert post4.pk not in post_ids

    def test_favorited_greater_than(self):
        post1, post2, post3, post4, post5 = PostFactory.create_batch(5)

        FavoriteFactory.create_batch(5, post=post2)
        FavoriteFactory.create_batch(10, post=post3)
        FavoriteFactory.create_batch(50, post=post4)
        FavoriteFactory.create_batch(100, post=post5)

        ps = PostSearch("favorite_count>10")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids
        assert post4.pk in post_ids
        assert post5.pk in post_ids

    def test_favorited_less_than(self):
        post1, post2, post3, post4, post5 = PostFactory.create_batch(5)

        FavoriteFactory.create_batch(5, post=post2)
        FavoriteFactory.create_batch(10, post=post3)
        FavoriteFactory.create_batch(50, post=post4)
        FavoriteFactory.create_batch(100, post=post5)

        ps = PostSearch("favorite_count<11")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post1.pk in post_ids
        assert post2.pk in post_ids
        assert post3.pk in post_ids
        assert post4.pk not in post_ids
        assert post5.pk not in post_ids


@pytest.mark.django_db
class TestPostAdvancedSearchTagCount:
    def test_tag_count_equal(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        tags1 = TagFactory.create_batch(5, post=post1)
        tags2 = TagFactory.create_batch(10, post=post2)
        tags3 = TagFactory.create_batch(25, post=post3)

        post1.tags.set(tags1)
        post2.tags.set(tags2)
        post3.tags.set(tags3)

        ps = PostSearch("tag_count=10")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk not in post_ids
        assert post1.pk not in post_ids
        assert post2.pk in post_ids
        assert post3.pk not in post_ids

    def test_tag_count_greater_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        tags1 = TagFactory.create_batch(5, post=post1)
        tags2 = TagFactory.create_batch(10, post=post2)
        tags3 = TagFactory.create_batch(25, post=post3)

        post1.tags.set(tags1)
        post2.tags.set(tags2)
        post3.tags.set(tags3)

        ps = PostSearch("tag_count>5")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk not in post_ids
        assert post1.pk not in post_ids
        assert post2.pk in post_ids
        assert post3.pk in post_ids

    def test_tag_count_less_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        tags1 = TagFactory.create_batch(5, post=post1)
        tags2 = TagFactory.create_batch(10, post=post2)
        tags3 = TagFactory.create_batch(25, post=post3)

        post1.tags.set(tags1)
        post2.tags.set(tags2)
        post3.tags.set(tags3)

        ps = PostSearch("tag_count<10")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk in post_ids
        assert post1.pk in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids


@pytest.mark.django_db
class TestPostAdvancedSearchFiletype:
    def test_filetype_extension(self):
        # TODO
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchMimetype:
    def test_supported_mimetype(self):
        # TODO
        pass

    def test_invalid_mimetype(self):
        # TODO
        pass

    def test_valid_but_unsupported_mimetype(self):
        # TODO
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchHeight:
    def test_image_height_equal(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, height=1000)
        ImageFactory(post=post1, height=2000)
        ImageFactory(post=post2, height=3000)
        ImageFactory(post=post3, height=4000)

        ps = PostSearch("height=1000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk in post_ids
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids

    def test_image_height_greater_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, height=1000)
        ImageFactory(post=post1, height=2000)
        ImageFactory(post=post2, height=3000)
        ImageFactory(post=post3, height=4000)

        ps = PostSearch("height>2000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk not in post_ids
        assert post1.pk not in post_ids
        assert post2.pk in post_ids
        assert post3.pk in post_ids

    def test_image_height_less_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, height=1000)
        ImageFactory(post=post1, height=2000)
        ImageFactory(post=post2, height=3000)
        ImageFactory(post=post3, height=4000)

        ps = PostSearch("height<3000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk in post_ids
        assert post1.pk in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids


@pytest.mark.django_db
class TestPostAdvancedSearchWidth:
    def test_image_width_equal(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, width=1000)
        ImageFactory(post=post1, width=2000)
        ImageFactory(post=post2, width=3000)
        ImageFactory(post=post3, width=4000)

        ps = PostSearch("width=1000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk in post_ids
        assert post1.pk not in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids

    def test_image_width_greater_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, width=1000)
        ImageFactory(post=post1, width=2000)
        ImageFactory(post=post2, width=3000)
        ImageFactory(post=post3, width=4000)

        ps = PostSearch("width>2000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk not in post_ids
        assert post1.pk not in post_ids
        assert post2.pk in post_ids
        assert post3.pk in post_ids

    def test_image_width_less_than(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ImageFactory(post=post0, width=1000)
        ImageFactory(post=post1, width=2000)
        ImageFactory(post=post2, width=3000)
        ImageFactory(post=post3, width=4000)

        ps = PostSearch("width<3000")
        posts = ps.get_posts()

        post_ids = set(posts.values_list("pk", flat=True))
        assert post0.pk in post_ids
        assert post1.pk in post_ids
        assert post2.pk not in post_ids
        assert post3.pk not in post_ids


@pytest.mark.django_db
class TestPostAdvancedSearchRatingLabel:
    @pytest.mark.parametrize("rating_level", list(RatingLevel))
    def test_rating_valid_rating_labels(self, rating_level):
        PostFactory.create_batch(10, rating_level=RatingLevel.SAFE)
        PostFactory.create_batch(10, rating_level=RatingLevel.UNRATED)
        PostFactory.create_batch(10, rating_level=RatingLevel.QUESTIONABLE)
        PostFactory.create_batch(10, rating_level=RatingLevel.EXPLICIT)

        ps = PostSearch(f"rating_label={rating_level.name.lower()}")
        posts = ps.get_posts()

        assert not posts.difference(
            Post.objects.filter(rating_level=rating_level.value)
        )

    def test_rating_bad_label(self):
        with pytest.raises(ValidationError):
            PostSearch("rating_label=not_a_label")


@pytest.mark.django_db
class TestPostAdvancedSearchRatingNumber:
    @pytest.mark.parametrize("rating_level", [r.value for r in RatingLevel])
    def test_rating_num_equal(self, rating_level):
        PostFactory.create_batch(10, rating_level=RatingLevel.SAFE)
        PostFactory.create_batch(10, rating_level=RatingLevel.UNRATED)
        PostFactory.create_batch(10, rating_level=RatingLevel.QUESTIONABLE)
        PostFactory.create_batch(10, rating_level=RatingLevel.EXPLICIT)

        ps = PostSearch(f"rating_num={rating_level}")
        posts = ps.get_posts()

        assert not posts.difference(Post.objects.filter(rating_level=rating_level))

    @pytest.mark.parametrize("rating_level", [r.value for r in RatingLevel])
    def test_rating_num_greater_than(self, rating_level):
        PostFactory.create_batch(10, rating_level=RatingLevel.SAFE)
        PostFactory.create_batch(10, rating_level=RatingLevel.UNRATED)
        PostFactory.create_batch(10, rating_level=RatingLevel.QUESTIONABLE)
        PostFactory.create_batch(10, rating_level=RatingLevel.EXPLICIT)

        ps = PostSearch(f"rating_num>{rating_level}")
        posts = ps.get_posts()

        assert not posts.difference(Post.objects.filter(rating_level__gt=rating_level))

    @pytest.mark.parametrize("rating_level", [r.value for r in RatingLevel])
    def test_rating_num_less_than(self, rating_level):
        PostFactory.create_batch(10, rating_level=RatingLevel.SAFE)
        PostFactory.create_batch(10, rating_level=RatingLevel.UNRATED)
        PostFactory.create_batch(10, rating_level=RatingLevel.QUESTIONABLE)
        PostFactory.create_batch(10, rating_level=RatingLevel.EXPLICIT)

        ps = PostSearch(f"rating_num<{rating_level}")
        posts = ps.get_posts()

        assert not posts.difference(Post.objects.filter(rating_level__lt=rating_level))


@pytest.mark.django_db
class TestPostAdvancedSearchSource:
    def test_src_url_exact(self):
        post1 = PostFactory.create(src_url="https://test1.example.com")
        post2 = PostFactory.create(src_url="https://test2.example.com")
        post3 = PostFactory.create(src_url="https://test3.example.com")

        ps = PostSearch("source=https://test1.example.com")
        posts = ps.get_posts()

        assert post1 in posts
        assert post2 not in posts
        assert post3 not in posts

    def test_src_url_with_wildcard(self):
        post1 = PostFactory.create(src_url="https://test1.example.com")
        post2 = PostFactory.create(src_url="https://test2.example.com")
        post3 = PostFactory.create(src_url="https://test3.example.com")
        post4 = PostFactory.create(src_url="https://test.example.org")

        ps = PostSearch("source=https://test*.example.com")
        posts = ps.get_posts()

        assert post1 in posts
        assert post2 in posts
        assert post3 in posts
        assert post4 not in posts

    def test_src_url_with_start_and_end_wildcard(self):
        post1 = PostFactory.create(src_url="https://test1.example.com")
        post2 = PostFactory.create(src_url="https://test2.example.com")
        post3 = PostFactory.create(src_url="https://test3.example.com")

        post4 = PostFactory.create(src_url="https://test1.example.org")

        ps = PostSearch("source=*test1.example.*")
        posts = ps.get_posts()

        assert post1 in posts
        assert post2 not in posts
        assert post3 not in posts
        assert post4 in posts

    def test_src_url_with_multipart_wildcard(self):
        post1 = PostFactory.create(src_url="http://test.exam.com")
        post2 = PostFactory.create(src_url="http://test.example.wow")
        post3 = PostFactory.create(src_url="https://test.examine.com")
        post4 = PostFactory.create(src_url="https://test.mine.org")

        ps = PostSearch("source=http*test.exam*e.*")
        posts = ps.get_posts()

        assert post1 not in posts
        assert post2 in posts
        assert post3 in posts
        assert post4 not in posts


@pytest.mark.django_db
class TestPostAdvancedSearchPostedBy:
    def test_uploaded_by_exact(self):
        post0, post1, post2, post3 = PostFactory.create_batch(4)

        ps = PostSearch(f"uploaded_by={post0.uploader.username}")
        posts = ps.get_posts()

        assert post0 in posts
        assert post1 not in posts
        assert post2 not in posts
        assert post3 not in posts

    def test_uploaded_by_with_wildcard(self):
        user1 = UserFactory.create(username="user1")
        user2 = UserFactory.create(username="user2")
        nobody = UserFactory.create(username="nobody")
        u1_posts = PostFactory.create_batch(4, uploader=user1)
        u2_posts = PostFactory.create_batch(4, uploader=user2)
        nb_posts = PostFactory.create_batch(4, uploader=nobody)

        ps = PostSearch("uploaded_by=user*")
        posts = ps.get_posts()

        for post in u1_posts + u2_posts:
            assert post in posts

        for post in nb_posts:
            assert post not in posts

    def test_uploaded_by_with_multi_part_wildcard(self):
        user1 = UserFactory.create(username="i_am_user1")
        user2 = UserFactory.create(username="i_am_user2")
        nobody = UserFactory.create(username="i_am_nobody")
        somebody = UserFactory.create(username="i_am_user_somebody")

        u1_post = PostFactory.create(uploader=user1)
        u2_post = PostFactory.create(uploader=user2)
        nb_post = PostFactory.create(uploader=nobody)
        sb_post = PostFactory.create(uploader=somebody)

        ps = PostSearch("uploaded_by=*am*body")
        posts = ps.get_posts()

        assert u1_post not in posts
        assert u2_post not in posts
        assert nb_post in posts
        assert sb_post in posts


@pytest.mark.django_db
class TestPostAdvancedSearchPostedOn:
    def test_date_exact(self):
        # TODO
        pass

    def test_date_before(self):
        # TODO
        pass

    def test_date_after(self):
        # TODO
        pass

    def test_valid_format_invalid_date(self):
        # TODO
        pass

    def test_invalid_date_format(self):
        # TODO
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchCollections:
    def test_exact_id(self):
        # TODO
        pass

    def test_exact_id_multiple(self):
        # Search returns posts in _both_ collections when using multiple
        # collection_id tokens
        # TODO
        pass

    def test_posts_in_a_collection(self):
        # TODO
        pass

    def test_posts_not_in_a_collection(self):
        # TODO
        pass

    def test_name(self):
        # TODO
        pass

    def test_name_with_wildcard(self):
        # TODO
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchParent:
    def test_parent_exists(self):
        # TODO
        pass

    def test_parent_id(self):
        # TODO
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchChildren:
    def test_child_exists(self):
        # TODO
        pass

    def test_children_ids(self):
        # TODO
        pass
