function generateErrCheckboxes(block_id) {
  const container = $(`#errFeaturesContainer-${block_id}`);
  container.empty();

  const row = $('<div>').addClass('row');

  for (const [section, subsections] of Object.entries(errFeatures)) {
    const col = $('<div>').addClass('col');
    const header = $('<h6>').text(section);
    col.append(header);

    const subsectionList = $('<ul>');

    for (const [subsection, tooltipText] of Object.entries(subsections)) {
      const id = `errFeature${subsection}`;

      const checkbox = $('<input>', {
        class: 'form-check-input', type: 'checkbox', id, value: subsection
      });

      const label = $('<label>', {
        class: 'form-check-label', text: subsection, for: id
      });

      const tooltipLink = $('<a>', {
        href: '#', class: 'ms-1', 'data-toggle': 'tooltip', title: tooltipText
      }).html('<i class="fas fa-question"></i>');

      const subsectionItem = $('<li>').addClass('form-check');
      subsectionItem.append(checkbox, label, tooltipLink);

      subsectionList.append(subsectionItem);
    }

    col.append(subsectionList);
    row.append(col);
  }

  container.append(row);

  // Initialize tooltips
  container.find('[data-toggle="tooltip"]').each(function () {
    new bootstrap.Tooltip(this);
  });
}

function selectErrFeatures(block_id) {
  const selectedFeatures = $(`#errModal-${block_id} input[type="checkbox"]:checked`).map((_, input) => input.value).get();

  let errInput = '';
  if (selectedFeatures.length === 1) {
    errInput = selectedFeatures[0];
  } else if (selectedFeatures.length > 1) {
    errInput = `(${selectedFeatures.join('|')})`;
  }

  $(`#err-${block_id}`).val(errInput);

  $(`#errModal-${block_id}`).modal('hide');
}

function clearErrFeatures(block_id) {
  $(`#errModal-${block_id} input[type="checkbox"]`).prop('checked', false);
}
