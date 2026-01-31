
const pageMap = {
  "hill view hospital": "/static/hospital/hospital.html",
  "santevita hospital": "/static/hospital/hospital.html",
  "rajendra institute of medical sciences(rims)": "/static/hospital/hospital.html"
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
      const key = item.toLowerCase();
      if (pageMap[key]) {
        window.location.href = pageMap[key];
      }
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

function handleSearch() {
  const box = document.getElementById("searchBox");
  const input = document.getElementById("searchInput");

  // If search box is hidden → just open it
  if (box.style.display !== "block") {
    box.style.display = "block";
    input.focus();
    return;
  }

  const query = input.value.trim().toLowerCase();

  if (!query) {
    alert("Please type or select a name");
    return;
  }

  if (pageMap[query]) {
    window.location.href = pageMap[query];
  } else {
    alert("No page found for this search");
  }
}
