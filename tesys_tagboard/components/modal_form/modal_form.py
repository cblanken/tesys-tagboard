from django_components import Component
from django_components import register


@register("modal_form")
class ModalFormComponent(Component):
    template_file = "modal_form.html"
    js_file = "modal_form.js"

    def get_template_data(self, args, kwargs, slots, context):
        title = kwargs.get("title", "Form")
        form = kwargs.get("form")
        submit_btn_text = kwargs.get("submit_btn_text")
        action_url = kwargs.get("action_url", "")
        method = kwargs.get("method", "post")
        return {
            "form": form,
            "title": title,
            "submit_btn_text": submit_btn_text,
            "action_url": action_url,
            "method": method,
        }
