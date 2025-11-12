(function () { // Self invoking function to avoid variable clashing
  let theme_picker = document.querySelector("#theme-picker");

  theme_picker.querySelectorAll("li").forEach(li => {
    li.addEventListener("click", e => {
      console.log(li);
      let theme = li.querySelector("input").value;
      document.querySelector("html").setAttribute("data-theme", theme);
      window.localStorage.setItem("theme", theme);
    });
  });
})();
