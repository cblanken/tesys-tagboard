from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django_components import Component
from django_components import register

from tesys_tagboard.search import PostSearchTokenCategory

if TYPE_CHECKING:
    from django.utils.safestring import SafeString

    from tesys_tagboard.models import Tag


@dataclass
class Action:
    name: str
    display: str
    desc: str
    tag: Tag | None = None
    arg: str = ""

    def render(
        self, template_name: str = "tags/tag_actions/tag_action.html", **kwargs
    ) -> SafeString:
        return render_to_string(template_name, context={"action": self, **kwargs})


@register("tag")
class TagComponent(Component):
    template_file = "tag.html"
    js_file = "tag.js"

    def get_template_data(self, args, kwargs, slots, context):
        tag = kwargs.get("tag")
        alias = kwargs.get("alias")
        tag = alias.tag if alias else kwargs.get("tag")
        if tag is None and alias is None:
            return {}
        size = kwargs.get("size")
        category = tag.category
        extra_actions = kwargs.get("actions", [])
        search_query = (
            f"{reverse('posts')}?q={PostSearchTokenCategory.TAG_ID.value.name}={tag.pk}"
        )
        search_action = Action(
            "search",
            display=_("Search"),
            desc=_("Search for posts with this tag"),
            tag=tag,
            arg=search_query,
        )

        delete_action = Action(
            "delete",
            display=_("Delete"),
            desc=_("Delete this tag from all posts"),
            tag=tag,
        )

        actions = [search_action, delete_action, *extra_actions]
        return {
            "tag": tag,
            "tag_search_query": search_query,
            "size": size,
            "category": category,
            "actions": actions,
            "alias": alias,
        }
