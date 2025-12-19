(function () { // Self invoking function to avoid variable clashing
  let theme_picker = document.querySelector("#theme-picker");

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
    li.addEventListener("click", e => {
      let theme = li.querySelector("input").value;
      document.querySelector("html").setAttribute("data-theme", theme);
      window.localStorage.setItem("theme", theme);
      highlight_current_theme();
    });
  });
})();
