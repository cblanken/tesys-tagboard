(function () { // Self invoking function to avoid variable clashing

  const setup = () => {
    let tagAction = (action, tag_id) => {
      return new CustomEvent("tagAction", {
        bubbles: true,
        detail: { action: action, tag_id: tag_id}
      });
    }

    const tag_containers = document.querySelectorAll(".tag-container");
    tag_containers.forEach(tag => {
      tag.addEventListener("tagAction", e => {
        if (e.detail.action == "remove") {
          tag.remove();
        }
      });
    });

    tag_containers.forEach(tag_container => {
      tag_container.querySelectorAll(".tag-actions button").forEach(btn => {
        htmx.on(btn, "click", (e) => {
          const action = btn.dataset?.action;
          const tag_id = btn.datset?.tag_id;

          if (action == "remove") {
            let form = htmx.closest(htmx.find('form'), 'form');
            form.dispatchEvent(new Event("confirmed-change"))
          }
          btn.dispatchEvent(tagAction(action, tag_id));
        });
      });
    });
  };

  setup();
  document.addEventListener("htmx:afterSwap", e => {
    setup();
  });
})();
