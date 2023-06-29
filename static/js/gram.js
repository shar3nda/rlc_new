const gramFeatures = {
  'Animacy': ['Anim', 'Inan'],
  'Aspect': ['Imp', 'Perf',],
  'Case': ['Acc', 'Dat', 'Gen', 'Ins', 'Loc', 'Nom', 'Par', 'Voc',],
  'Degree': ['Cmp', 'Pos', 'Sup',],
  'Foreign': ['Foreign',],
  'Gender': ['Fem', 'Masc', 'Neut',],
  'Hyph': ['Hyphen',],
  'Mood': ['Cnd', 'Imp', 'Ind',],
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

  for (const [column, features] of Object.entries(gramFeatures)) {
    const col = $('<div>').addClass('col');
    const header = $('<h6>').text(column);
    col.append(header);

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
    }

    row.append(col);
  }

  container.append(row);
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
