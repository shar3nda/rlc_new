const gramFeatures = {
  'Animacy': [
    'Anim',
    'Inan'
  ],
  'Aspect': [
    'Imp',
    'Perf',
  ],
  'Case': [
    'Acc',
    'Dat',
    'Gen',
    'Ins',
    'Loc',
    'Nom',
    'Par',
    'Voc',
  ],
  'Degree': [
    'Cmp',
    'Pos',
    'Sup',
  ],
  'Foreign': [
    'Foreign',
  ],
  'Gender': [
    'Fem',
    'Masc',
    'Neut',
  ],
  'Hyph': [
    'Hyphen',
  ],
  'Mood': [
    'Cnd',
    'Imp',
    'Ind',
  ],
  'Number': [
    'Plur',
    'Sing',
  ],
  'Person': [
    '1',
    '2',
    '3',
  ],
  'Polarity': [
    'Neg',
  ],
  'Tense': [
    'Fut',
    'Past',
    'Pres',
  ],
  'Variant': [
    'Short',
  ],
  'VerbForm': [
    'Conv',
    'Fin',
    'Inf',
    'Part',
  ],
  'Voice': [
    'Act',
    'Mid',
    'Pass',
  ],
};

function generateGramCheckboxes(block_id) {
  const container = document.getElementById(`gramFeaturesContainer-${block_id}`);
  container.innerHTML = '';

  const row = document.createElement('div');
  row.className = 'row';

  for (const column in gramFeatures) {
    const col = document.createElement('div');
    col.className = 'col';

    const header = document.createElement('h6');
    header.innerText = column;
    col.appendChild(header);

    for (const feature of gramFeatures[column]) {
      const formCheck = document.createElement('div');
      formCheck.className = 'form-check';

      const input = document.createElement('input');
      input.className = 'form-check-input';
      input.type = 'checkbox';
      input.id = `gramFeature${feature}-${block_id}`;
      input.value = feature;
      formCheck.appendChild(input);

      const label = document.createElement('label');
      label.className = 'form-check-label';
      label.innerText = feature;
      label.htmlFor = `gramFeature${feature}-${block_id}`;
      formCheck.appendChild(label);

      col.appendChild(formCheck);
    }

    row.appendChild(col);
  }

  container.appendChild(row);
}

function selectGramFeatures(block_id) {
  const selectedFeatures = Array.from(document.getElementById(`gramModal-${block_id}`).querySelectorAll('input[type="checkbox"]:checked')).map(input => input.value);

  let gramInput = '';
  if (selectedFeatures.length === 1) {
    gramInput = selectedFeatures[0];
  } else if (selectedFeatures.length > 1) {
    gramInput = `(${selectedFeatures.join('|')})`;
  }

  $(`#gram-${block_id}`).val(gramInput);

  $(`#gramModal-${block_id}`).modal('hide');
}

function clearGramFeatures() {
  const modal = $(`#gramModal-${block_id}`);
  modal.find('input[type="checkbox"]').prop('checked', false);
}