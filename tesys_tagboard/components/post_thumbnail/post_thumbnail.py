from django_components import Component
from django_components import register

from tesys_tagboard.models import Tag


@register("post_thumbnail")
class PostThumbnailComponent(Component):
    template_file = "post_thumbnail.html"
    css_file = "post_thumbnail.css"
    js_file = "post_thumbnail.js"

    def get_template_data(self, args, kwargs, slots, context):
        post = kwargs.get("post")
        max_tags = kwargs.get("max_tags", 15)
        tags = Tag.objects.filter(post=post).order_by("category", "-post_count")
        post_ids_by_collection = {}

        # TODO: optimize these queries, they might need to be lifted out
        # of the component
        collection_posts = post.collection_set.through.objects.values(
            "post", "collection"
        )
        for item in collection_posts:
            post_id = item.get("post")
            collection_id = item.get("collection")
            post_ids = [*post_ids_by_collection.get(collection_id, []), post_id]
            post_ids_by_collection.update({collection_id: post_ids})

        return {
            "post": post,
            "tags": tags,
            "max_tags": max_tags,
            "post_ids_by_collection": post_ids_by_collection,
        }
