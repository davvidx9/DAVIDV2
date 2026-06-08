const header = document.getElementById("header");
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
const menuFilters = document.getElementById("menuFilters");
const menuGrid = document.getElementById("menuGrid");
const contactForm = document.getElementById("contactForm");
const toast = document.getElementById("toast");

window.addEventListener("scroll", () => {
  header.classList.toggle("scrolled", window.scrollY > 50);
});

navToggle.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");
  navToggle.classList.toggle("active", isOpen);
  navToggle.setAttribute("aria-expanded", isOpen);
});

navLinks.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
    navToggle.classList.remove("active");
    navToggle.setAttribute("aria-expanded", "false");
  });
});

menuFilters.addEventListener("click", (e) => {
  const btn = e.target.closest(".filter-btn");
  if (!btn) return;

  menuFilters.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");

  const filter = btn.dataset.filter;
  menuGrid.querySelectorAll(".menu-card").forEach((card) => {
    const category = card.dataset.category;
    card.classList.toggle("hidden", filter !== "all" && category !== filter);
  });
});

menuGrid.addEventListener("click", (e) => {
  const btn = e.target.closest(".add-to-cart");
  if (!btn) return;

  const dish = btn.closest(".menu-card").querySelector("h3").textContent;
  showToast(`${dish} added to your order!`);
});

contactForm.addEventListener("submit", (e) => {
  e.preventDefault();
  showToast("Thank you! We'll get back to you soon.");
  contactForm.reset();
});

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => toast.classList.remove("show"), 3000);
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  },
  { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
);

document.querySelectorAll(".menu-card, .about-content, .gallery-grid img, .contact-info, .contact-form").forEach((el) => {
  el.style.opacity = "0";
  el.style.transform = "translateY(24px)";
  el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
  observer.observe(el);
});
