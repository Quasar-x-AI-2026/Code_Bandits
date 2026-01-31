
  const data = [
    "Diabetes",
    "Hypertension",
    "Asthma",
    "Heart Disease",
    "Migraine",
    "Anemia"
  ];

  function toggleSearch() {
    const box = document.getElementById("searchBox");
    box.style.display = box.style.display === "block" ? "none" : "block";
    document.getElementById("searchInput").focus();
  }

  function searchData() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const dropdown = document.getElementById("dropdown");
    dropdown.innerHTML = "";

    if (!input) return;

    const results = data.filter(item =>
      item.toLowerCase().includes(input)
    );

    if (results.length === 0) {
      const li = document.createElement("li");
      li.textContent = "No results found";
      dropdown.appendChild(li);
      return;
    }

    results.forEach(item => {
      const li = document.createElement("li");
      li.textContent = item;
      li.onclick = () => {
        document.getElementById("searchInput").value = item;
        dropdown.innerHTML = "";
      };
      dropdown.appendChild(li);
    });
  }

