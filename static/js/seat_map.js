document.addEventListener("DOMContentLoaded", function () {
  var grid = document.querySelector(".seat-grid");
  if (!grid) return;

  var confirmBtn = document.getElementById("proceed-btn");
  var selectedLabel = document.getElementById("selected-seat-label");

  grid.addEventListener("click", function (e) {
    var seat = e.target.closest(".seat");
    if (!seat || !seat.classList.contains("available")) return;

    // Deselect any previously selected seat
    var prev = grid.querySelector(".seat.selected");
    if (prev && prev !== seat) prev.classList.remove("selected");

    var nowSelected = seat.classList.toggle("selected");

    if (nowSelected) {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.setAttribute("href", seat.dataset.bookUrl);
      }
      if (selectedLabel) {
        selectedLabel.textContent = seat.dataset.seatNumber + " · " + seat.dataset.seatClass + " · " + seat.dataset.price;
      }
    } else {
      if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.removeAttribute("href");
      }
      if (selectedLabel) selectedLabel.textContent = "No seat selected";
    }
  });
});
