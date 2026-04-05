(function () { // Self invoking function to avoid variable clashing
  let theme_picker = document.querySelector("#theme-picker");
  const csrf_token = theme_picker.querySelector("input[name='csrfmiddlewaretoken']")?.value;

  const highlight_current_theme = () => {
    const active_theme = window.localStorage.getItem("theme");

    if (active_theme) {
      theme_picker.querySelectorAll("li").forEach(li => {
        const highlight_classes = ["bg-primary", "text-primary-content", "underline"];
        const input = li.querySelector("input[type='radio']");
        if (active_theme === input.value) {
          input.classList.add(...highlight_classes);
        } else {
          input.classList.remove(...highlight_classes);
        }
      });
    }
  }

  highlight_current_theme();
  theme_picker.querySelectorAll("li").forEach(li => {
    li.addEventListener("click", async (e) => {
      let theme = li.querySelector("input").value;
      document.querySelector("html").setAttribute("data-theme", theme);
      window.localStorage.setItem("theme", theme);
      await fetch("/set-theme/", {
        headers: {
          "X-CSRFToken": csrf_token,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        method: "POST",
        body: new URLSearchParams({"theme": theme}),
      })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to change the user's theme setting ${response.status}`);
        }
      });
      highlight_current_theme();
      window.location.reload();
    });
  });
})();
