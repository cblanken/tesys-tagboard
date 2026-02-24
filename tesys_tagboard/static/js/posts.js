const simple_search_form = document.querySelector("form#simple-post-search");
const advanced_search_form = document.querySelector("form#advanced-post-search");
const edit_advanced_search_btn = document.querySelector("button#edit-advanced-search-btn");
const edit_advanced_search_btn_text = document.querySelector("#edit-advanced-search-btn-text");
const search_submit_btn = document.querySelector("#search-submit-btn");

let advanced_search_hidden = true;
const toggle_advanced_search_off_form_classes = ["hidden"];
const toggle_simple_search_off_form_classes = ["hidden"];
const toggle_advanced_search_off_btn_classes = [];
const toggle_advanced_search = () => {
  if (advanced_search_hidden) {
    // Enable advanced search mode
    simple_search_form.classList.add(...toggle_simple_search_off_form_classes);
    advanced_search_form.classList.remove(...toggle_advanced_search_off_form_classes);
    edit_advanced_search_btn.classList.add(...toggle_advanced_search_off_btn_classes);
    edit_advanced_search_btn_text.textContent = "SIMPLE"
  } else {
    // Enable simple search mode (default)
    simple_search_form.classList.remove(...toggle_simple_search_off_form_classes);
    advanced_search_form.classList.add(...toggle_advanced_search_off_form_classes);
    edit_advanced_search_btn.classList.remove(...toggle_advanced_search_off_btn_classes)
    edit_advanced_search_btn_text.textContent = "ADVANCED";
  }

  advanced_search_hidden = !advanced_search_hidden;
}

edit_advanced_search_btn.addEventListener("click", e => {
  e.preventDefault();
  toggle_advanced_search();
});
