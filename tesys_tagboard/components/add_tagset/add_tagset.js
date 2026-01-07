(function () { // Self invoking function to avoid variable clashing
  const setup_tagset = (root) => {
    const search_input = root.querySelector("input[type='search']");
    let tagset_name = root.dataset?.tagsetName;

    const get_tagset = () => {
      return root.querySelector(".tagset");
    }

    const get_search_results = () => {
      return root.querySelector(".result-container ul");
    }

    const get_tagset_ids = (tagset) => {
      return Array.from(tagset.querySelectorAll(`input[name='${tagset_name}']`)).map((input) => input.value)
    }

    const add_tag_btn = root.querySelector("button.add-tag-btn");
    const cancel_tag_btn = root.querySelector("button.cancel-tag-btn");
    const confirm_tag_btn = root.querySelector("button.confirm-tag-btn");
    const search_bar = root.querySelector(".search-container");
    const search_bar_input = search_bar.querySelector("input[type='search']");
    const show_tag_search = () => {
      add_tag_btn.classList.add("hidden");
      search_bar.classList.remove("hidden");
      cancel_tag_btn.classList.remove("hidden");
      confirm_tag_btn.classList.remove("hidden");
      search_bar_input.focus();
    }
    const hide_tag_search = () => {
      search_bar.classList.add("hidden");
      cancel_tag_btn.classList.add("hidden");
      confirm_tag_btn.classList.add("hidden");
      add_tag_btn.classList.remove("hidden");
    }
    const delete_uncommitted_tags = () => {
      const tagset = get_tagset();
      tagset.querySelectorAll(":scope > div[data-new]").forEach(uncommitted_tag => {
        uncommitted_tag.remove();
      });
    }

    add_tag_btn.addEventListener("click", e => {
      e.preventDefault()
      show_tag_search();
    });

    cancel_tag_btn.addEventListener("click", e => {
      e.preventDefault()
      hide_tag_search();
      delete_uncommitted_tags();
    });

    confirm_tag_btn.addEventListener("click", e => {
      hide_tag_search();
    });

    const add_tag_to_set_handler = (e) => {
      e.preventDefault();
      e.stopPropagation();
      const tagset = get_tagset();
      let autocomplete_item = e.currentTarget;
      const tag_id = autocomplete_item.dataset['id'];
      let tagset_ids = get_tagset_ids(tagset);
      if (tagset_ids.includes(tag_id)) {
        console.warn("Duplicate tag/search items may not be added to a tagset.")
      } else {
        const tag_name = autocomplete_item.dataset['name'];
        const tag_div = document.createElement("div");
        tag_div.classList.add("p-3", "py-1", "border-2", "border-dashed", "rounded-md", "opacity-60");
        tag_div.textContent = `+ ${tag_name}`;
        tag_div.setAttribute("data-new", true);

        let tag_input = document.createElement("input");
        tag_input.setAttribute("id", `tag-${tag_id}`);
        tag_input.setAttribute("type", "hidden");
        tag_input.setAttribute("name", tagset_name);
        tag_input.setAttribute("value", tag_id);

        tag_div.appendChild(tag_input);
        tagset.appendChild(tag_div);
      }

      search_input.value = "";
      search_input.focus();
    }


    root.addEventListener("tagAction", e => {
      // Update tags when a tag is removed
      if (e.detail.action == "remove") {
        htmx.trigger(confirm_tag_btn, "click");
      };
    });

    htmx.on(root.querySelector(".result-container"), "htmx:afterSettle", (e) => {
      let search_results = get_search_results();
      if (search_results) {
        Array.from(search_results.children).forEach(autocomplete_item => {
          htmx.on(autocomplete_item, "click", add_tag_to_set_handler);
          htmx.on(autocomplete_item, "keydown", (e) => {
            switch (e.code) {
              case "Enter":
                e.preventDefault();
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
                e.preventDefault();
            }
          });
        });
      }
    });
  };

  const setup = () => {
    tagset_containers = document.querySelectorAll(".add-tagset-container");
    tagset_containers.forEach(container => {
      setup_tagset(container);
    });
  }

  document.addEventListener("DOMContentLoaded", e => {
    setup();
  });

  document.addEventListener("htmx:afterSwap", e => {
    if (Array.from(e.detail.elt.classList).includes("add-tagset-container")) {
      setup_tagset(e.detail.elt);
    }
  });
})();
