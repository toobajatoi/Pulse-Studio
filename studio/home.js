const spaces = [
  ["Rides", "12"],
  ["Food", "9"],
  ["Pay", "6"],
  ["Quik", "4"],
  ["Plus", "3"],
  ["Delivery", "5"],
];

document.getElementById("spaces").innerHTML = spaces
  .map(([name], i) => `<button class="space ${i === 0 ? "on" : ""}" type="button">${name}</button>`)
  .join("");

document.getElementById("spaces").addEventListener("click", (e) => {
  const btn = e.target.closest(".space");
  if (!btn) return;
  document.querySelectorAll(".space").forEach((el) => el.classList.toggle("on", el === btn));
});
