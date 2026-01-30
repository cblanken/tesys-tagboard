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

  const post_full_screen_dialog = document.querySelector("#post_full_screen");
  const dialog_img = post_full_screen_dialog.querySelector("img");
  const post_zoom_slider_container = document.querySelector("#zoom-slider-container");
  const post_zoom_slider = document.querySelector("#media-zoom");
  const zoom_toggle_btn = document.querySelector("button#zoom-toggle")
  const zoom_in_btn = document.querySelector("button#media-zoom-in")
  const zoom_out_btn = document.querySelector("button#media-zoom-out")

  const contain_img_classes = ["max-h-[94svh]", "max-w-[94svw]"];
  const zoom_img_classes = ["max-w-fit"];
  let showing_zoom_slider = false;
  const img_default_scale = parseInt(post_zoom_slider.value);

  const reset_img_scale = () => {
    post_zoom_slider.value = img_default_scale;
    post_zoom_slider.dispatchEvent(new Event('change'));
  };

  zoom_toggle_btn.addEventListener("click", e => {
    if (showing_zoom_slider) {
      dialog_img.classList.add(...contain_img_classes);
      dialog_img.classList.remove(...zoom_img_classes);
      post_zoom_slider_container.classList.add("hidden");
      reset_img_scale();
    } else {
      dialog_img.classList.remove(...contain_img_classes);
      dialog_img.classList.add(...zoom_img_classes);
      post_zoom_slider_container.classList.remove("hidden")
    }
    showing_zoom_slider = !showing_zoom_slider;
  });

  post_zoom_slider.addEventListener("change", e => {
    dialog_img.classList.remove("max-h-full");
    dialog_img.style.zoom = e.target.value / 100;
  });
  zoom_in_btn.addEventListener("click", e => {
    post_zoom_slider.value = parseInt(post_zoom_slider.value) + parseInt(post_zoom_slider.step);
    post_zoom_slider.dispatchEvent(new Event('change'));

  });
  zoom_out_btn.addEventListener("click", e => {
    post_zoom_slider.value = parseInt(post_zoom_slider.value) - parseInt(post_zoom_slider.step);
    post_zoom_slider.dispatchEvent(new Event('change'));
  });
})()
