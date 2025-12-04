(function () { // Self invoking function to avoid variable clashing
  const setup_edit_field = (form) => {
    const field_display = form.querySelector(".field-display");
    const field_text_input = form.querySelector("input[type='text']");
    const edit_btn = form.querySelector("label.edit-btn");
    const field_submit_btn = form.querySelector("button[type='submit']");
    const field_edit_toggle_btn = form.querySelector("label[role='button']");

    // Set cursor to last position
    field_text_input.setSelectionRange(field_text_input.textContent.length-1, field_text_input.textContent.length-1);

    // Swap readonly comment text for editable field
    function toggle_edit_field(editing) {
      const edit_edit_btn = edit_btn.querySelector(".edit-btn_edit");
      const edit_cancel_btn = edit_btn.querySelector(".edit-btn_cancel");
      if (editing) {
        edit_edit_btn.classList.add("hidden")
        edit_cancel_btn.classList.remove("hidden")

        field_text_input.classList.remove("hidden");
        field_submit_btn.classList.remove("hidden");
        field_display.classList.add("hidden");
        field_text_input.focus();
      } else {
        edit_cancel_btn.classList.add("hidden")
        edit_edit_btn.classList.remove("hidden")

        field_text_input.classList.add("hidden");
        field_submit_btn.classList.add("hidden");
        field_display.classList.remove("hidden");
      }
    }

    const checkbox = form.querySelector("input[name='edit-enabled']");

    // Toggle comment editable textarea
    checkbox.addEventListener("change", e => {
      toggle_edit_field(checkbox.checked);
    });

    // The label is styled as a button, but doesn't propgate change event
    // of the related input without manually dispatching the event.
    edit_btn.addEventListener("click", e => {
      checkbox.dispatchEvent(new Event("change"));
    });

    field_submit_btn.addEventListener("htmx:afterRequest", e => {
      if (e.detail.target = field_display) {
        toggle_edit_field(false);
      }
    });
  };

  const setup = (forms) => {
    forms.forEach(form => {
      setup_edit_field(form);
    });
  };

  const get_edit_text_forms = () => {
    return document.querySelectorAll(".text-field-edit-form");
  }

  let forms = get_edit_text_forms();
  setup(forms);
})()
