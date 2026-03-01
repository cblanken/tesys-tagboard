/* Project specific Javascript goes here. */
const messages = document.querySelectorAll(".django-message");
const back_to_top_btn = document.querySelector("#back-to-top-btn");
const bottom_screen_threshold = (document.querySelector("#bottom-of-screen-threshold"));

messages.forEach(m => {
  const close_btn = m.querySelector(".btn-close");
  close_btn.addEventListener("click", e => {
    m.remove();
  });
});
