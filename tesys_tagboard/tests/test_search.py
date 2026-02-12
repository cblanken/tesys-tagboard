import contextlib

import pytest
from django.core.exceptions import ValidationError

from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import TagCategory
from tesys_tagboard.search import PostSearch
from tesys_tagboard.search import TokenArgRelation
from tesys_tagboard.search import TokenCategory
from tesys_tagboard.search import tag_alias_autocomplete
from tesys_tagboard.search import tag_autocomplete

from .factories import CommentFactory
from .factories import FavoriteFactory
from .factories import PostFactory
from .factories import TagFactory
from .factories import UserFactory


@pytest.mark.django_db
class TestTagAutocomplete:
    def test_autocomplete_included_by_name_partial(self, db):
        tags = tag_autocomplete(Tag.objects.all(), "blue")
        tag_names = [tag.name for tag in tags]
        assert "blue-jeans" in tag_names
        assert "blue" in tag_names
        assert "blue-gray" in tag_names
        assert "blueberry" in tag_names
        assert "red_vs._blue" in tag_names
        assert "sky-blue" in tag_names
        assert tags.count() == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        tags = tag_autocomplete(Tag.objects.all(), exclude_partial="blue")
        tag_names = [tag.name for tag in tags]
        assert "blue-jeans" not in tag_names
        assert "blue" not in tag_names
        assert "blue-gray" not in tag_names
        assert "blueberry" not in tag_names
        assert "sky-blue" not in tag_names

    def test_autocomplete_excluded_by_tag_name(self, db):
        tags = tag_autocomplete(
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
        assert "red_v._blue" in alias_names
        assert "red_vs_blue" in alias_names
        assert "red_x_blue" in alias_names
        assert aliases.count() == 6

    def test_autocomplete_excluded_by_name_partial(self, db):
        aliases = tag_alias_autocomplete(TagAlias.objects.all(), exclude_partial="red")
        alias_names = [alias.name for alias in aliases]
        assert "red_v._blue" not in alias_names
        assert "red_vs_blue" not in alias_names
        assert "red_x_blue" not in alias_names
        assert "r_v._b" in alias_names
        assert "r_vs._b" in alias_names

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
            # This test does not test validation, only token identification
            with contextlib.suppress(ValidationError):
                ps = PostSearch(f"{token_category.value.name}=100")
                assert ps.tokens[0].category == token_category

    @pytest.mark.parametrize("token_category", list(TokenCategory))
    def test_correctly_identify_tag_categories_by_alias(
        self, token_category: TokenCategory
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
            item.name for item in items if item.token_category == TokenCategory.TAG
        ]
        assert "red" in tag_names
        assert "red_vs._blue" in tag_names

        # Aliases
        alias_names = [
            item.alias
            for item in items
            if item.token_category == TokenCategory.TAG_ALIAS
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
        for tc in TokenCategory:
            assert tc in item_categories

    def test_no_filters(self):
        ps = PostSearch("")
        items = ps.autocomplete(show_filters=False)
        item_categories = {item.token_category for item in items}
        item_categories.remove(TokenCategory.TAG)
        item_categories.remove(TokenCategory.TAG_ALIAS)
        for tc in TokenCategory:
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


@pytest.mark.django_db
class TestPostAdvancedSearchID:
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


@pytest.mark.django_db(transaction=True)
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
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchMimetype:
    def test_mimetype(self):
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchHeight:
    def test_height_equal(self):
        pass

    def test_height_greater_than(self):
        pass

    def test_height_less_than(self):
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchWeight:
    def test_weight_equal(self):
        pass

    def test_weight_greater_than(self):
        pass

    def test_weight_less_than(self):
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchRating:
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


@pytest.mark.django_db
class TestPostAdvancedSearchSource:
    def test_src_url(self):
        pass

    def test_src_url_with_wildcard(self):
        pass


@pytest.mark.django_db
class TestPostAdvancedSearchUploadedBy:
    def test_uploaded_by(self):
        pass
