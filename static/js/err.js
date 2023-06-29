function generateErrCheckboxes(block_id) {
    const container = document.getElementById(`errFeaturesContainer-${block_id}`);
    container.innerHTML = '';

    const row = document.createElement('div');
    row.className = 'row';

    for (const section in errFeatures) {
      const col = document.createElement('div');
      col.className = 'col';

      const header = document.createElement('h6');
      header.innerText = section;
      col.appendChild(header);

      const subsectionList = document.createElement('ul');

      for (const subsection in errFeatures[section]) {
        const subsectionItem = document.createElement('li');
        subsectionItem.className = 'form-check';

        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.id = `errFeature${subsection}`;
        checkbox.value = subsection;
        subsectionItem.appendChild(checkbox);

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `errFeature${subsection}`;
        label.innerText = subsection;
        subsectionItem.appendChild(label);

        const tooltipLink = document.createElement('a');
        tooltipLink.href = '#';
        tooltipLink.className = 'ms-1';
        tooltipLink.dataset.toggle = 'tooltip';
        tooltipLink.title = errFeatures[section][subsection];
        tooltipLink.innerHTML = '<i class="fas fa-question"></i>';
        subsectionItem.appendChild(tooltipLink);

        subsectionList.appendChild(subsectionItem);
      }

      col.appendChild(subsectionList);
      row.appendChild(col);
    }

    container.appendChild(row);

    // Initialize tooltips
    const tooltips = container.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach((tooltip) => {
      new bootstrap.Tooltip(tooltip);
    });
  }

  function selectErrFeatures(block_id) {
    const selectedFeatures = Array.from(document.getElementById(`errModal-${block_id}`).querySelectorAll('input[type="checkbox"]:checked')).map(input => input.value);

    let errInput = '';
    if (selectedFeatures.length === 1) {
      errInput = selectedFeatures[0];
    } else if (selectedFeatures.length > 1) {
      errInput = `(${selectedFeatures.join('|')})`;
    }

    $(`#err-${block_id}`).val(errInput);

    $(`#errModal-${block_id}`).modal('hide');
  }

  function clearErrFeatures() {
    const modal = $(`#errModal-${block_id}`);
    modal.find('input[type="checkbox"]').prop('checked', false);
  }