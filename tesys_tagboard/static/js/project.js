/* Project specific Javascript goes here. */
const messages = document.querySelectorAll(".django-message");
const back_to_top_btn = document.querySelector("#back-to-top-btn");
const bottom_screen_threshold = (document.querySelector("#bottom-of-screen-threshold"));

messages.forEach(m => {
  const close_btn = m.querySelector(".btn-close");
  close_btn.addEventListener("click", e => {
    m.remove();
  });
});

// Show "back to top" button when scrolled past threshold
if (
  "IntersectionObserver" in window &&
  "IntersectionObserverEntry" in window &&
  "intersectionRatio" in window.IntersectionObserverEntry.prototype
) {

  const options = {
    root: null,
    rootMargin: "0px",
    threshold: [1.0],
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.intersectionRatio > 0) {
        back_to_top_btn.classList.add("hidden", "animate-fade-in-very-fast");
      } else {
        back_to_top_btn.classList.remove("hidden");
      }
    }, options);
  });

  observer.observe(bottom_screen_threshold);
};
