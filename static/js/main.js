document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav toggle (public navbar — passengers/guests)
  var navToggle = document.querySelector(".navbar-toggle");
  var navLinks = document.querySelector(".navbar-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      navLinks.classList.toggle("open");
    });
  }

  // Sidebar toggle (admin layout)
  var sidebarToggle = document.querySelector(".sidebar-toggle");
  var sidebar = document.querySelector(".sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  // Dismiss Django messages
  document.querySelectorAll(".alert [data-dismiss]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      btn.closest(".alert").remove();
    });
  });

  // Auto-uppercase IATA code / booking reference inputs
  document.querySelectorAll("[data-uppercase]").forEach(function (input) {
    input.addEventListener("input", function () {
      var pos = input.selectionStart;
      input.value = input.value.toUpperCase();
      input.setSelectionRange(pos, pos);
    });
  });
});