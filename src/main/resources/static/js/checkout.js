/**
 * CINEBOOK - Checkout & Polymorphic Payment Form Toggle
 */

document.addEventListener("DOMContentLoaded", () => {
  const methodInputs = document.querySelectorAll('input[name="payment_method"]');
  const upiFields = document.getElementById("upi-fields");
  const cardFields = document.getElementById("card-fields");
  const cashFields = document.getElementById("cash-fields");

  function togglePaymentFields() {
    const selected = document.querySelector('input[name="payment_method"]:checked').value;

    if (upiFields) upiFields.style.display = selected === "UPI" ? "block" : "none";
    if (cardFields) cardFields.style.display = selected === "CARD" ? "block" : "none";
    if (cashFields) cashFields.style.display = selected === "CASH" ? "block" : "none";
  }

  methodInputs.forEach(input => {
    input.addEventListener("change", togglePaymentFields);
  });

  togglePaymentFields();
});
