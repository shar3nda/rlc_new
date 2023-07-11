$(document).ready(function() {
    $('.lexgram-form').on('submit', function(e) {
        e.preventDefault();

        var formData = {};
        $(this).serializeArray().map(function(item) {
            if (formData[item.name]) {
                if (typeof(formData[item.name]) === "string") {
                    formData[item.name] = [formData[item.name]];
                }
                formData[item.name].push(item.value);
            } else {
                formData[item.name] = item.value;
            }
        });

        console.log(JSON.stringify(formData));
    });
});
