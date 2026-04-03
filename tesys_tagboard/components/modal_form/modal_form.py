from django_components import Component
from django_components import register


@register("modal_form")
class ModalFormComponent(Component):
    template_file = "modal_form.html"
    js_file = "modal_form.js"

    def get_template_data(self, args, kwargs, slots, context):
        title = kwargs.get("title", "Form")
        form = kwargs.get("form")
        return {"form": form, "title": title}
