
const pageMap = {
  "hill view hospital": "hospital/hospital.html",
  "santevita hospital": "santevita.html",
  "rajendra institute of medical sciences(rims)": "rims.html"
};

// Given data
const data = [
  "Hill View Hospital",
  "Santevita Hospital",
  "Rajendra Institute of Medical Sciences(RIMS)"
];

function toggleSearch() {
  const box = document.getElementById("searchBox");
  box.style.display = box.style.display === "block" ? "none" : "block";
  document.getElementById("searchInput").focus();
}

function filterData() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const dropdown = document.getElementById("dropdown");
  dropdown.innerHTML = "";

  if (input === "") return;

  const filtered = data.filter(item =>
    item.toLowerCase().includes(input)
  );

  filtered.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    li.onclick = () => {
      window.location.href = pageMap[item.toLowerCase()];
    };

    dropdown.appendChild(li);
  });
}

function goToPage() {
  const query = document
    .getElementById("searchInput")
    .value
    .trim()
    .toLowerCase();

  if (pageMap[query]) {
    window.location.href = pageMap[query];
  } else {
    alert("No page found for this search");
  }
}
