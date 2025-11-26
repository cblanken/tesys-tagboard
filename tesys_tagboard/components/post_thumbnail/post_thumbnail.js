(function () { // Self invoking function to avoid variable clashing
  function show_thumbnail(container, img) {
    img.classList.add(`animate-pop-in-fast`);
    img.classList.add(`motion-reduce:animate-fade-in-fast`);
    img.classList.remove(`invisible`);
    container.classList.remove("skeleton")
  }

  document.querySelectorAll(`.post-thumbnail`).forEach((thumbnail) => {
    const img = thumbnail.querySelector(`img`);

    thumbnail.querySelectorAll(".dropdown").forEach(ele => {
      ele.addEventListener("click", (e) => {
        e.preventDefault();
      })
    });

    if (img.complete) {
      show_thumbnail(thumbnail, img);
    } else {
      img.onload = function() {
        show_thumbnail(thumbnail, img);
      }
    }
  });
})();
