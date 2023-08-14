const gramFeatures = {
  'Animacy': ['Anim', 'Inan'],
  'Aspect': ['AspectImp', 'Perf',],
  'Case': ['Acc', 'Dat', 'Gen', 'Ins', 'Loc', 'Nom', 'Par', 'Voc',],
  'Degree': ['Cmp', 'Pos', 'Sup',],
  'Foreign': ['ForeignYes',],
  'Gender': ['Fem', 'Masc', 'Neut',],
  'Hyph': ['HyphYes',],
  'Mood': ['Cnd', 'MoodImp', 'Ind',],
  'Number': ['Plur', 'Sing',],
  'Person': ['1', '2', '3',],
  'Polarity': ['Neg',],
  'Tense': ['Fut', 'Past', 'Pres',],
  'Variant': ['Short',],
  'VerbForm': ['Conv', 'Fin', 'Inf', 'Part',],
  'Voice': ['Act', 'Mid', 'Pass',],
};

function generateGramCheckboxes(block_id) {
  const container = $(`#gramFeaturesContainer-${block_id}`);
  container.empty();

  const row = $('<div>').addClass('row');
  const columns = [];

  for (const [column, features] of Object.entries(gramFeatures)) {
    const col = $('<div>').addClass('col');
    const header = $('<h6>').text(column).addClass('gram-link');
    col.append(header);

    const checkboxes = [];

    for (const feature of features) {
      const id = `gramFeature${feature}-${block_id}`;

      const input = $('<input>', {
        class: 'form-check-input', type: 'checkbox', id, value: feature
      });

      const label = $('<label>', {
        class: 'form-check-label', text: feature, for: id
      });

      const formCheck = $('<div>').addClass('form-check');
      formCheck.append(input, label);

      col.append(formCheck);
      checkboxes.push(input);
    }

    columns.push(checkboxes);
    row.append(col);
  }

  container.append(row);

  // Add click event listener to each header to check corresponding checkboxes
  container.find('h6.gram-link').click(function() {
    const columnIndex = container.find('h6.gram-link').index(this);
    const columnCheckboxes = columns[columnIndex];
    columnCheckboxes.forEach(checkbox => checkbox.prop('checked', true));
  });
}


function selectGramFeatures(block_id) {
  const selectedFeatures = $(`#gramModal-${block_id} input[type="checkbox"]:checked`).map((_, input) => input.value).get();

  let gramInput = '';
  if (selectedFeatures.length === 1) {
    gramInput = selectedFeatures[0];
  } else if (selectedFeatures.length > 1) {
    gramInput = `(${selectedFeatures.join('|')})`;
  }

  $(`#gram-${block_id}`).val(gramInput);

  $(`#gramModal-${block_id}`).modal('hide');
}

function clearGramFeatures(block_id) {
  $(`#gramModal-${block_id} input[type="checkbox"]`).prop('checked', false);
}
