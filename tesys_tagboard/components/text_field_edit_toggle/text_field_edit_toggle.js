(function () { // Self invoking function to avoid variable clashing
  const setup_edit_field = (form) => {
    const field_display = form.querySelector(".field-display > span, .field-display > a");
    const field_text_input = form.querySelector("input.hidden");
    const edit_btn = form.querySelector("label.edit-btn");
    const field_confirm_btn = form.querySelector("button[type='button']");

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
        field_confirm_btn.classList.remove("hidden");
        field_display.classList.add("hidden");
        field_text_input.focus();
      } else {
        edit_cancel_btn.classList.add("hidden")
        edit_edit_btn.classList.remove("hidden")

        field_text_input.classList.add("hidden");
        field_confirm_btn.classList.add("hidden");
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

    field_confirm_btn.addEventListener("click", e => {
      field_display.textContent = field_text_input.value;
      if (field_display.nodeName === "a") {
        field_display.href = field_text_input.value;
      }
      toggle_edit_field(false);
      form.dispatchEvent(new Event("confirmed-change", { bubbles: true }))
    });

    // Only passthrough tagset change event when confirmed
    form.addEventListener("change", e => {
      if (e.target === form) {
        // root.dispatchEvent(new Event("confirmed-change", { bubbles: true }))
      } else {
        e.preventDefault();
        e.stopPropagation();
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
