function getCategoryErrCheckboxes(category, block_id) {
  const container = document.getElementById(`errFeaturesContainer-${block_id}`);
  const catErrors = Array.from(errFeatures.get(category).keys());
  return Array.from(container.querySelectorAll("input[type='checkbox']")).filter((checkbox) =>
    catErrors.some((feature) => checkbox.id === `errFeature${feature}-${block_id}`),
  );
}

function generateErrCheckboxes(block_id) {
  const container = document.getElementById(`errFeaturesContainer-${block_id}`);
  container.innerHTML = "";

  let firstCat = ["Syntax", "Additional tags"];
  let secondCat = Array.from(errFeatures.keys()).filter(
    (feature) => feature !== "Syntax" && feature !== "Additional tags",
  );

  [firstCat, secondCat].forEach((categories) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "err-group mb-2";

    const row = document.createElement("div");
    row.className = "row";

    categories.forEach((category) => {
      const catErrors = errFeatures.get(category);

      const features = Array.from(catErrors.keys());
      const errors = Array.from(catErrors.entries());

      // If the category is 'Syntax', split into three columns
      if (category === "Syntax") {
        const colSize = Math.ceil(features.length / 3);
        const col1 = createColumn(errors.slice(0, colSize), block_id, "Syntax");
        row.appendChild(col1);
        for (let i = 1; i < 3; i++) {
          const col = createColumn(errors.slice(i * colSize, (i + 1) * colSize), block_id, "Syntax", true);
          row.appendChild(col);
        }
      } else {
        const col = createColumn(errors, block_id, category);
        row.appendChild(col);
      }
    });

    groupDiv.appendChild(row);
    container.appendChild(groupDiv);
  });

  function createColumn(errors, block_id, category, hideHeader = false) {
    const col = document.createElement("div");
    col.className = "col";

    const header = document.createElement("h6");
    header.textContent = category;
    if (hideHeader) {
      header.style.visibility = "hidden";
    }
    col.appendChild(header);

    errors.forEach(([feature, description]) => {
      const id = `errFeature${feature}-${block_id}`;
      const checkboxDiv = document.createElement("div");
      checkboxDiv.className = "form-check";

      const input = document.createElement("input");
      input.className = "form-check-input";
      input.type = "checkbox";
      input.id = id;
      input.value = feature;

      const label = document.createElement("label");
      label.className = "form-check-label";
      label.setAttribute("for", id);
      label.textContent = feature;

      const space = document.createTextNode(" ");

      const tooltip = document.createElement("i");
      tooltip.classList.add("bi", "bi-question-circle");
      tooltip.setAttribute("data-bs-toggle", "tooltip");
      tooltip.setAttribute("title", description);

      checkboxDiv.appendChild(input);
      checkboxDiv.appendChild(label);
      checkboxDiv.appendChild(space);
      checkboxDiv.appendChild(tooltip);
      new bootstrap.Tooltip(tooltip);
      col.appendChild(checkboxDiv);
    });

    return col;
  }

  container.querySelectorAll("h6").forEach((header) => {
    header.addEventListener("click", () => {
      const category = header.textContent;
      const checkboxes = getCategoryErrCheckboxes(category, block_id);
      checkboxes.forEach((checkbox) => (checkbox.checked = true));
    });
  });
}
