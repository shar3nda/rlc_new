$(document).ready(function () {
  $('.lexgram-form').on('submit', function (e) {
    e.preventDefault();

    var formData = {};
    $(this).serializeArray().map(function (item) {
      var value = item.value;
      if (item.name in ['errors[]', 'grammar[]', 'lex[]']) {
        value = value.split('|');
      }
      if (item.name.endsWith('[]')) {
        if (!(item.name in formData)) {
          formData[item.name] = [];
        }
        formData[item.name].push(value);
      } else {
        formData[item.name] = value;
      }
    });

    // encode formData as GET parameters
    var queryString = Object.keys(formData).map(function (key) {
      return encodeURIComponent(key) + '=' + encodeURIComponent(formData[key]);
    }).join('&');

    // go to the URL
    window.location.href = `/corpus/search_results/?${queryString}`;
  });
});
