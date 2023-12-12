const lexFeatures = [
  "ADJ",
  "ADP",
  "ADV",
  "AUX",
  "CCONJ",
  "DET",
  "INTJ",
  "NOUN",
  "NUM",
  "PART",
  "PRON",
  "PROPN",
  "PUNCT",
  "SCONJ",
  "SYM",
  "VERB",
  "X",
];

function generateLexCheckboxes(block_id) {
  const container = document.getElementById(`lexFeaturesContainer-${block_id}`);
  container.innerHTML = "";

  const header = document.createElement("h6");
  header.textContent = "Part of speech";
  header.className = "lex-link";
  container.appendChild(header);

  header.addEventListener("click", () => {
    container.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      checkbox.checked = true;
    });
  });

  const numColumns = 4;
  const columnSize = Math.ceil(lexFeatures.length / numColumns);

  const row = document.createElement("div");
  row.className = "row";

  for (let i = 0; i < numColumns; i++) {
    const col = document.createElement("div");
    col.className = "col";

    lexFeatures.slice(i * columnSize, (i + 1) * columnSize).forEach((feature) => {
      const id = `lexFeature${feature}-${block_id}`;

      const input = document.createElement("input");
      input.className = "form-check-input";
      input.type = "checkbox";
      input.id = id;
      input.value = feature;

      const label = document.createElement("label");
      label.className = "form-check-label";
      label.setAttribute("for", id);
      label.textContent = feature;

      const formCheck = document.createElement("div");
      formCheck.className = "form-check";
      formCheck.appendChild(input);
      formCheck.appendChild(label);

      col.appendChild(formCheck);
    });

    row.appendChild(col);
  }

  container.appendChild(row);
}
