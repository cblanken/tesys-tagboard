(function () { // Self invoking function to avoid variable clashing

  const edit_post_form = document.querySelector("#edit-post-form");
  const edit_post_submit_btn = edit_post_form.querySelector("#save-post-btn");
  const post_rating_field = edit_post_form.querySelector("#post-rating-field");

  edit_post_form.addEventListener("confirmed-change", (e) => {
    edit_post_submit_btn.removeAttribute("disabled");
  });

  post_rating_field.addEventListener("change", e => {
    edit_post_form.dispatchEvent(new Event('confirmed-change'));
  });

})()
