const populateFeaturesTextBox = (block_id, modalType) => {
  const checkboxes = document.querySelectorAll(`#${modalType}Modal-${block_id} input[type="checkbox"]:checked`);
  const selectedFeatures = Array.from(checkboxes).map((input) => input.value);

  let inputStr = "";
  if (selectedFeatures.length >= 1) {
    inputStr = selectedFeatures.length === 1 ? selectedFeatures[0] : `(${selectedFeatures.join("|")})`;
  }

  document.querySelector(`#${modalType}-${block_id}`).value = inputStr;
  hideBSModal(`#${modalType}Modal-${block_id}`);
};

const clearFeatures = (block_id, modalType) => {
  const checkboxes = document.querySelectorAll(`#${modalType}Modal-${block_id} input[type="checkbox"]`);
  checkboxes.forEach((input) => (input.checked = false));
};
