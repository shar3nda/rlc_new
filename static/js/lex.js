const lexFeatures = [
    'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART',
    'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X'
  ];

  function generateLexCheckboxes(block_id) {
    const container = document.getElementById(`lexFeaturesContainer-${block_id}`);
    container.innerHTML = '';

    const numColumns = 4;
    const columnSize = Math.ceil(lexFeatures.length / numColumns);

    const row = document.createElement('div');
    row.className = 'row';

    for (let i = 0; i < numColumns; i++) {
      const column = document.createElement('div');
      column.className = 'col';

      for (let j = i * columnSize; j < (i + 1) * columnSize && j < lexFeatures.length; j++) {
        const feature = lexFeatures[j];

        const div = document.createElement('div');
        div.className = 'form-check';

        const input = document.createElement('input');
        input.className = 'form-check-input';
        input.type = 'checkbox';
        input.id = `lexFeature${feature}-{{ block_id }}`;
        input.value = feature;

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `lexFeature${feature}-{{ block_id }}`;
        label.textContent = feature;

        div.appendChild(input);
        div.appendChild(label);
        column.appendChild(div);
      }

      row.appendChild(column);
    }

    container.appendChild(row);
  }

  function selectLexFeatures(block_id) {
    const selectedFeatures = Array.from(document.getElementById(`lexModal-${block_id}`).querySelectorAll('input[type="checkbox"]:checked')).map(input => input.value);

    let lexInput = '';
    if (selectedFeatures.length === 1) {
      lexInput = selectedFeatures[0];
    } else if (selectedFeatures.length > 1) {
      lexInput = `(${selectedFeatures.join('|')})`;
    }

    document.getElementById(`lex-${block_id}`).value = lexInput;
    $(`#lexModal-${block_id}`).modal('hide');
  }

  function clearLexFeatures(block_id) {
    // uncheck all checkboxes in modal
    const modal = $(`#lexModal-${block_id}`);
    modal.find('input[type="checkbox"]').prop('checked', false);
  }