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
  const container = $(`#lexFeaturesContainer-${block_id}`);
  container.empty();

  const header = $("<h6>").text("Part of speech").addClass("lex-link");
  container.append(header);

  header.click(function () {
    // Iterate over all columns in the current container and check all the checkboxes
    $(`#lexFeaturesContainer-${block_id} input[type="checkbox"]`).prop("checked", true);
  });

  const numColumns = 4;
  const columnSize = Math.ceil(lexFeatures.length / numColumns);

  const row = $("<div>").addClass("row");

  Array(numColumns)
    .fill()
    .forEach((_, i) => {
      const col = $("<div>").addClass("col");

      lexFeatures.slice(i * columnSize, (i + 1) * columnSize).forEach((feature) => {
        const id = `lexFeature${feature}-${block_id}`;

        const input = $("<input>", {
          class: "form-check-input",
          type: "checkbox",
          id,
          value: feature,
        });

        const label = $("<label>", {
          class: "form-check-label",
          text: feature,
          for: id,
        });

        const formCheck = $("<div>").addClass("form-check");
        formCheck.append(input, label);

        col.append(formCheck);
      });

      row.append(col);
    });

  container.append(row);
}

function selectLexFeatures(block_id) {
  const selectedFeatures = $(`#lexModal-${block_id} input[type="checkbox"]:checked`)
    .map((_, input) => input.value)
    .get();

  let lexInput = "";
  if (selectedFeatures.length === 1) {
    lexInput = selectedFeatures[0];
  } else if (selectedFeatures.length > 1) {
    lexInput = `(${selectedFeatures.join("|")})`;
  }

  $(`#lex-${block_id}`).val(lexInput);

  $(`#lexModal-${block_id}`).modal("hide");
}

function clearLexFeatures(block_id) {
  $(`#lexModal-${block_id} input[type="checkbox"]`).prop("checked", false);
}
