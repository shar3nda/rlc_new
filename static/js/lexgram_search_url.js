$(document).ready(function () {
  const processForms = formSelectors => {
    const formData = {};

    formSelectors.forEach(formSelector => {
      $(formSelector).serializeArray().forEach(item => {
        let {name, value} = item;
        const isSpecialField = ['errors[]', 'grammar[]', 'lex[]'].includes(name);
        const isArrayField = name.endsWith('[]');

        if (isSpecialField) {
          value = value.split('|');
        }
        if (isArrayField) {
          formData[name] = formData[name] || [];
          formData[name].push(value);
        } else {
          formData[name] = value;
        }
      });
    });

    return formData;
  };

  const generateQueryString = formData => {
    return Object.keys(formData)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(formData[key])}`)
      .join('&');
  };

  const handleFormSubmit = (event, formSelectors, targetUrl) => {
    event.preventDefault();
    const formData = processForms(formSelectors);
    const queryString = generateQueryString(formData);
    window.location.href = `${targetUrl}?${queryString}`;
  };

  $('#lexgram-form').on('submit', function (e) {
    handleFormSubmit(e, ['#lexgram-form', '#subcorpus-form'], '/corpus/search_results/');
  });

  $('#exact-search-form').on('submit', function (e) {
    handleFormSubmit(e, ['#exact-search-form', '#subcorpus-form'], '/corpus/exact_search_results/');
  });
});
