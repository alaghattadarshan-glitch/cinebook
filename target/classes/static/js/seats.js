/**
 * CINEBOOK - Interactive Seating Script
 * Handles real-time selection, automatic price tally, and locking API call.
 */

document.addEventListener("DOMContentLoaded", () => {
  const seats = document.querySelectorAll(".seat.available, .seat.selected");
  const selectedListSpan = document.getElementById("selected-seats-list");
  const totalPriceSpan = document.getElementById("total-price-display");
  const checkoutBtn = document.getElementById("checkout-btn");
  const showIdInput = document.getElementById("current-show-id");

  let selectedSeats = [];

  function updateSummary() {
    if (selectedSeats.length === 0) {
      selectedListSpan.textContent = "None";
      totalPriceSpan.textContent = "0.00";
      checkoutBtn.disabled = true;
      checkoutBtn.style.opacity = "0.5";
      return;
    }

    const codes = selectedSeats.map(s => s.code).join(", ");
    const total = selectedSeats.reduce((sum, s) => sum + s.price, 0);

    selectedListSpan.textContent = codes;
    totalPriceSpan.textContent = total.toFixed(2);
    checkoutBtn.disabled = false;
    checkoutBtn.style.opacity = "1";
  }

  seats.forEach(seat => {
    // If pre-selected by session
    if (seat.classList.contains("selected")) {
      selectedSeats.push({
        id: parseInt(seat.dataset.seatId),
        code: seat.dataset.seatCode,
        price: parseFloat(seat.dataset.seatPrice)
      });
    }

    seat.addEventListener("click", () => {
      const seatId = parseInt(seat.dataset.seatId);
      const code = seat.dataset.seatCode;
      const price = parseFloat(seat.dataset.seatPrice);

      const existingIndex = selectedSeats.findIndex(s => s.id === seatId);

      if (existingIndex >= 0) {
        // Deselect
        selectedSeats.splice(existingIndex, 1);
        seat.classList.remove("selected");
        seat.classList.add("available");
      } else {
        // Max 10 seats per booking
        if (selectedSeats.length >= 10) {
          alert("You can select up to 10 seats per booking.");
          return;
        }
        selectedSeats.push({ id: seatId, code: code, price: price });
        seat.classList.add("selected");
        seat.classList.remove("available");
      }

      updateSummary();
    });
  });

  updateSummary();

  // Handle Checkout submission with seat locking
  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", async () => {
      if (selectedSeats.length === 0) return;

      checkoutBtn.disabled = true;
      checkoutBtn.textContent = "Locking seats...";

      const showId = parseInt(showIdInput.value);
      const seatIds = selectedSeats.map(s => s.id);

      try {
        const response = await fetch("/book/api/lock-seats", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ show_id: showId, seat_ids: seatIds })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          window.location.href = data.redirect_url;
        } else {
          alert(data.message || "Failed to reserve selected seats. Please reselect.");
          window.location.reload();
        }
      } catch (err) {
        console.error("Locking error:", err);
        alert("An error occurred while locking seats. Please try again.");
        checkoutBtn.disabled = false;
        checkoutBtn.textContent = "Proceed to Checkout";
      }
    });
  }
});
