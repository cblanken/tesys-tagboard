(function () { // Self invoking function to avoid variable clashing
  const root = document.querySelector(".add-tagset-container");
  const search_input = root.querySelector("input[type='search']")

  const get_search_results = () => {
    return root.querySelector(".result-container ul");
  }

  const get_tagset_ids = (tagset) => {
    return Array.from(tagset.querySelectorAll("input[name='tagset']")).map((input) => input.value)
  }


  const add_tag_to_set_handler = (e) => {
    let autocomplete_item = e.currentTarget;
    const tagset = htmx.find(".tagset");
    const tag_id = autocomplete_item.dataset['id'];
    let tagset_ids = get_tagset_ids(tagset);
    if (!tagset_ids.includes(tag_id)) {
      const tag_name = autocomplete_item.dataset['name'];
      const tag_div = document.createElement("div");
      tag_div.classList.add("rounded-md", "bg-secondary", "text-secondary-content", "h-8", "px-2", "py-1");
      tag_div.textContent = tag_name;

      let tag_input = document.createElement("input");
      tag_input.setAttribute("id", `tag-${tag_id}`);
      tag_input.setAttribute("type", "hidden");
      tag_input.setAttribute("name", "tagset");
      tag_input.setAttribute("value", tag_id);

      tag_div.appendChild(tag_input);
      tagset.appendChild(tag_div);
    } else {
      console.warn("Duplicate tag/search items may not be added to a tagset.")
    }

    search_input.value = "";
    search_input.focus();
  }


  htmx.on(root.querySelector(".result-container"), "htmx:afterSettle", (e) => {
    let search_results = get_search_results();
    if (search_results) {
      Array.from(search_results.children).forEach(autocomplete_item => {
        htmx.on(autocomplete_item, "click", add_tag_to_set_handler);
        htmx.on(autocomplete_item, "keydown", (e) => {
          switch (e.code) {
            case "Enter":
              add_tag_to_set_handler(e);
              break;
            case "Escape":
              e.preventDefault();
              search_input.focus();
              break;
            case "ArrowLeft":
              e.preventDefault();
              search_input.focus();
              break;
            case "ArrowRight":
              e.preventDefault();
              search_input.focus();
              break;
            default:
              // Do nothing
          }
        });
      });
    }
  });
})();
