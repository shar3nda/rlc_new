$(document).ready(function () {
  $('.lexgram-form').on('submit', function (e) {
    e.preventDefault();

    var formData = {};
    $(this).serializeArray().map(function (item) {
      var value = item.value;
      if (!(item.name in ['language[]', 'level[]', 'generallevel[]']) && item.name.endsWith('[]')) {
        value = item.value.split('|');
      }
      if (formData[item.name]) {
        if (Array.isArray(formData[item.name])) {
          formData[item.name].push(value);
        } else {
          formData[item.name] = [formData[item.name], value];
        }
      } else {
        formData[item.name] = value;
      }
    });

    var $form = $('<form/>', {
      'action': this.action,
      'method': 'post',
      'style': 'display:none;'
    });

    $.each(formData, function(name, value) {
      $form.append($('<input/>', {
        'type': 'hidden',
        'name': name,
        'value': value
      }));
    });

    $('body').append($form);
    $form.submit();
  });
});
