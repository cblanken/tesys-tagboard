(function () { // Self invoking function to avoid variable clashing
  const root = document.querySelector(".search-container");
  const search_input = root.querySelector("input[type='search']");
  const result_container = root.querySelector(".result-container");
  let autocomplete_items = [];
  let active_autocomplete_index = -1;

  const reset_active_autocomplete_index = () => { active_autocomplete_index = -1 };

  const get_search_results = () => {
    return result_container.querySelector("ul");
  }

  const get_search_result_items = () => {
    try {
      return get_search_results().querySelectorAll("li");
    } catch (TypeError) {
      return null
    }
  }

  let remove_results = () => {
    let search_results_ul = get_search_results();
    if (search_results_ul) {
      try {
        htmx.remove(search_results_ul)
      } catch (NotFoundError) {
        console.error(`Couldn't find search results ul`)
      }
    }
    reset_active_autocomplete_index()
  }

  function focus_autocomplete_item(index) {
    let items = get_search_result_items()
    if (items) {
      items = Array.from(items);
      if (index >= 0 && index < items.length) {
        items[index].focus();
        active_autocomplete_index = index
      }
    }
  }

  document.addEventListener("keydown", (e) => {
    if (root.contains(document.activeElement)) {
      switch (e.code) {
        case "ArrowDown":
          e.preventDefault();
          focus_autocomplete_item(active_autocomplete_index + 1);
          break;
        case "ArrowUp":
          e.preventDefault();
          focus_autocomplete_item(active_autocomplete_index - 1);
          break;
        case "Enter":
          e.preventDefault();
          remove_results();
        default:
      }
    }
  });


  htmx.on(search_input, "blur", (e) => {
    if (!result_container.contains(e.relatedTarget)) {
      remove_results();
    }
  });

  htmx.on(result_container, "htmx:afterSwap", (e) => {
    reset_active_autocomplete_index();
  });

  htmx.on(search_input, "change", (e) => {
    result_container.querySelectorAll("li").forEach(li => {
      htmx.on(li, "focus", (e) => {
        // Focus correct autocomplete item
      });

      htmx.on(li, "blur", (e) => {
        if (!result_container.contains(e.relatedTarget)) {
          remove_results();
        }
      });
    });
  });
})();
