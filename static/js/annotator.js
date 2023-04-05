function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return decodeURI(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

const CREATE_ANNOT = 0;
const UPDATE_ANNOT = 1;
const DELETE_ANNOT = 2;

function updateModel(annotation, action) {
    // create a new XMLHttpRequest object
    const xhr = new XMLHttpRequest();
    // set the POST URL and headers
    xhr.open('POST', '/update_model/');
    xhr.setRequestHeader('Content-Type', 'application/json');
    // add the CSRF token to the request header
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    annotation.action = action;
    annotation.document_id = document_id;
    annotation.user_id = user_id;
    // set the data to send as a JSON object
    const data = JSON.stringify(annotation)
    // set the callback function
    let response = {};
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // handle the response
            response = JSON.parse(xhr.responseText);
            if (response.success) {
                alert(response.message);
            } else {
                alert('Error: ' + response.message);
            }
        }
    };
    // send the request with the JSON object as a string
    xhr.send(data);
    return response.id;
}


// Инициализация объекта аннотатора
var r = Recogito.init({
    content: document.getElementById('document-annot-text'),
    readOnly: false,
    showTooltip: true,
    selectors: [{type: 'TextQuoteSelector'}],
});

// Загрузка аннотаций из базы данных по url
r.loadAnnotations('/get_annotations/' + document_id);

// TODO сделать overrideId
// Подписка на событие создания аннотации
r.on('createAnnotation', function (annotation) {
    updateModel(annotation, CREATE_ANNOT);
});

// Подписка на событие обновления аннотации
r.on('updateAnnotation', function (annotation) {
    updateModel(annotation, UPDATE_ANNOT);
});

// Подписка на событие удаления аннотации
r.on('deleteAnnotation', function (annotation) {
    updateModel(annotation, DELETE_ANNOT);
});