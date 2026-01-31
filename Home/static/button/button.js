
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
          document.getElementById("searchInput").value = item;
          dropdown.innerHTML = "";
        };
        dropdown.appendChild(li);
      });
    }
