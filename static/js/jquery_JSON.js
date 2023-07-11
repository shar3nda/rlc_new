$(document).ready(function() {
    $('.lexgram-form').on('submit', function(e) {
        e.preventDefault();

        var formData = {};
        $(this).serializeArray().map(function(item) {
            var value = item.value;
            if (item.name.endsWith('[]')) {
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

        console.log(JSON.stringify(formData));
    });
});
