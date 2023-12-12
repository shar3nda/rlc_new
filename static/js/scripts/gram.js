const gramFeatures = {
  Gender: ["Fem", "Masc", "Neut"],
  Animacy: ["Anim", "Inan"],
  Number: ["Plur", "Sing"],
  Case: ["Acc", "Dat", "Gen", "Ins", "Loc", "Nom", "Par", "Voc"],
  Degree: ["Cmp", "Pos", "Sup"],
  Polarity: ["Neg"],
  Variant: ["Short"],
  Aspect: ["AspectImp", "Perf"],
  Mood: ["Cnd", "MoodImp", "Ind"],
  Tense: ["Fut", "Past", "Pres"],
  Voice: ["Act", "Mid", "Pass"],
  Person: ["1", "2", "3"],
  Foreign: ["ForeignYes"],
  Hyph: ["HyphYes"],
};

const udGroups = {
  "Nominal Features": ["Gender", "Animacy", "Number", "Case"],
  "Degree and Polarity": ["Degree", "Polarity", "Variant"],
  "Verbal Features": ["Aspect", "Mood", "Tense", "Voice"],
  "Pronouns, Determiners, Quantifiers": ["Person"],
  "Other Features": ["Foreign", "Hyph"],
};

function generateGramCheckboxes(block_id) {
  const container = document.getElementById(`gramFeaturesContainer-${block_id}`);
  container.innerHTML = "";

  Object.entries(udGroups).forEach(([group, categories]) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "gram-group mb-2";

    const groupHeader = document.createElement("h5");
    groupHeader.textContent = group;
    groupHeader.className = "gram-group-header";
    groupDiv.appendChild(groupHeader);

    const row = document.createElement("div");
    row.className = "row";

    categories.forEach((category) => {
      const features = gramFeatures[category];

      // If the category is 'Case', split into two columns
      if (category === "Case") {
        const colSize = Math.ceil(features.length / 2);
        const col1 = createColumn(features.slice(0, colSize), block_id, "Case");
        const col2 = createColumn(features.slice(colSize), block_id, "Case", true);
        row.appendChild(col1);
        row.appendChild(col2);
      } else {
        const col = createColumn(features, block_id, category);
        row.appendChild(col);
      }
    });

    groupDiv.appendChild(row);
    container.appendChild(groupDiv);
  });

  function createColumn(features, block_id, category, hideHeader = false) {
    const col = document.createElement("div");
    col.className = "col";

    const header = document.createElement("h6");
    header.textContent = category;
    if (hideHeader) {
      header.style.visibility = "hidden";
    }
    col.appendChild(header);

    features.forEach((feature) => {
      const id = `gramFeature${feature}-${block_id}`;
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

      checkboxDiv.appendChild(input);
      checkboxDiv.appendChild(label);
      col.appendChild(checkboxDiv);
    });

    return col;
  }

  container.querySelectorAll("h6").forEach((header) => {
    header.addEventListener("click", () => {
      const category = header.textContent;
      const checkboxes = container.querySelectorAll(`input[type="checkbox"]`);
      let catCheckboxes = Array.from(checkboxes).filter((checkbox) =>
        gramFeatures[category].some((feature) => checkbox.id === `gramFeature${feature}-${block_id}`),
      );
      catCheckboxes.forEach((checkbox) => {
        checkbox.checked = true;
      });
    });
  });
}
