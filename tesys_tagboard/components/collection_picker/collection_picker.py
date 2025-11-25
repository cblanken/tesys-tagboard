from django_components import Component
from django_components import register

from tesys_tagboard.models import Collection


@register("collection_picker")
class CollectionPickerComponent(Component):
    template_file = "collection_picker.html"
    js_file = "collection_picker.js"

    def get_template_data(self, args, kwargs, slots, context):
        post = kwargs.get("post")
        user = self.request.user
        collections = (
            Collection.objects.filter(user=user) if user.is_authenticated else None
        )

        return {"collections": collections, "post": post}
