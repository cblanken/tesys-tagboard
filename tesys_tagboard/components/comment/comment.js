(function () { // Self invoking function to avoid variable clashing

  const setup_comment = (comment) => {
    const comment_text = comment.querySelector(".comment-text");
    const comment_edit_form = comment.querySelector(".comment-edit-form");
    const comment_edit_mode_form = comment.querySelector(".comment-edit-mode-form");
    const comment_edit_form_textarea = comment_edit_form.querySelector("textarea");

    // Set textarea cursor to last position
    comment_edit_form_textarea.selectionStart = comment_edit_form_textarea.textContent.length
    comment_edit_form_textarea.selectionEnd = comment_edit_form_textarea.textContent.length

    // Swap readonly comment text for editable field
    function swapCommentEditField(enable) {
      if (enable) {
        comment_edit_form.classList.remove("hidden");
        comment_text.classList.add("hidden");
        comment_edit_form_textarea.focus();
      } else {
        comment_edit_form.classList.add("hidden");
        comment_text.classList.remove("hidden");
      }
    }


    if (comment_edit_mode_form) {
      const comment_edit_cancel_btn = comment_edit_form.querySelector(".btn.comment-edit-cancel");
      const checkbox = comment_edit_mode_form.querySelector("input[type='checkbox']");

      comment_edit_cancel_btn.addEventListener("click", e => {
        checkbox.checked = false;
        swapCommentEditField(false)
      });

      // Toggle comment editable textarea
      checkbox.addEventListener("change", e => {
        swapCommentEditField(checkbox.checked);
      });

      // The label is styled as a button, but doesn't propgate change event
      // of the related input without manually dispatching the event.
      comment_edit_mode_form.querySelector("label").addEventListener("click", e => {
        checkbox.dispatchEvent(new Event("change"));
      });
    }
  };

  const setup = (comments) => {
    comments.forEach(comment => {
      setup_comment(comment);
    });
  };

  const get_comments = () => {
    return document.querySelectorAll("[data-comment]");
  }

  let comments = get_comments();
  setup(comments);

  document.addEventListener("htmx:afterRequest", e => {
    // Re-setup comment event listeners when an edit is made
    // TODO: target only edited comment instead of running setup over all comments
    let comments = get_comments();
    setup(comments);
  });
})();
