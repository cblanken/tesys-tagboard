(function () { // Self invoking function to avoid variable clashing
  const setup_search_bar = (root) => {
    const search_input = root.querySelector("input[type='search']");
    const partial_input = root.querySelector("input[name='partial']");
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

    search_input.addEventListener("input", (e) => {
      let partial = get_query_active_token_selection().partial;
      partial_input.value = partial;
      let event = new Event("search_input_changed")
      dispatchEvent(event);
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

    const split_re = /\s+/i;
    function get_query_active_token_selection() {
      // Identifies the token actively being edited and parses it to provide a partial selection
      // for the autocomplete. For example if a user is writing a query: `abc 123^ def 456` where
      // the cursor is at the position of "^". The autocomplete will be based on the the nearest
      // previous token, so 123 in this example which will be provided as the partial argument to
      // the autocomplete endpoint.
      let query = search_input.value;

      // Find end of token index or default to end of query
      i = search_input.selectionStart
      let token_end = query.indexOf(" ", i)
      if (token_end === -1) {
        token_end = query.length
      }

      // Find start of token index
      let token_start = 0;
      let token_start_index_offset = query.slice(0, i).split("").reverse().indexOf(" ")
      if (token_start_index_offset !== -1) {
        token_start = i - token_start_index_offset;
      }

      const partial = query.slice(token_start, token_end)
      return { start: token_start, end: token_end, partial: partial };
    }

    const add_autocomplete_item_to_input = (e) => {
      e.preventDefault();
      e.stopPropagation();
      let active_token = get_query_active_token_selection();
      let query = String(search_input.value)

      const autocompleted_name = e.currentTarget?.dataset.search_token
      if (autocompleted_name == undefined) {
        console.error("Search autocomplete failed to parse the provided query.");
        return
      }

      let new_query = `${query.slice(0, active_token.start)}${autocompleted_name}${query.slice(active_token.end)}`;
      search_input.value = new_query;

      search_input.focus();
    }

    htmx.on(root.querySelector(".result-container"), "htmx:afterSettle", (e) => {
      let search_results = get_search_results();
      if (search_results) {
        Array.from(search_results.children).forEach(autocomplete_item => {
          htmx.on(autocomplete_item, "click", add_autocomplete_item_to_input);
          htmx.on(autocomplete_item, "keydown", (e) => {
            e.preventDefault();
            switch (e.code) {
              case "Enter":
                add_autocomplete_item_to_input(e)
                break;
              case "Escape":
                search_input.focus();
                break;
              case "ArrowLeft":
                search_input.focus();
                break;
              case "ArrowRight":
                search_input.focus();
                break;
              default:
                // Do nothing
            }
          });
        });
      }
    });

  }

  const setup = (search_bars) => {
    search_bars.forEach(search_bar => {
      setup_search_bar(search_bar);
    });
  };

  const get_search_bars = () => {
    return document.querySelectorAll(".search-container");
  }

  let search_bars = get_search_bars();
  setup(search_bars);
  })();
