function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function createAnnotation(documentId, sentenceId, userId, guid, alt, body) {
  const url = '/api/annotations/create/';
  const data = {
    document: documentId, sentence: sentenceId, user: userId, guid: guid, alt: alt, body,
  };
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(data)
  });

  if (response.ok) {
    const jsonData = await response.json();
    console.log('Annotation created:', jsonData);
  } else {
    console.error('Error creating annotation:', response.statusText);
  }
}

async function updateAnnotation(documentId, sentenceId, userId, guid, alt, body) {
  const url = '/api/annotations/update/';
  const data = {
    document: documentId, sentence: sentenceId, user: userId, guid: guid, body
  };
  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(data)
  });

  if (response.ok) {
    const jsonData = await response.json();
    console.log('Annotation updated:', jsonData);
  } else {
    console.error('Error updating annotation:', response.statusText);
  }
}

async function deleteAnnotation(guid) {
  const url = '/api/annotations/delete/';
  const data = {guid: guid};
  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(data)
  });

  if (response.ok) {
    const jsonData = await response.json();
    console.log('Annotation deleted:', jsonData);
  } else {
    console.error('Error deleting annotation:', response.statusText);
  }
}

function getCSRFToken() {
  return getCookie('csrftoken');
}

var CheckboxWidget = function (args) {

  // 1. Find a current check status in the annotation, if any
  var currentCheckBody = args.annotation ?
    args.annotation.bodies.find(function (b) {
      return b.purpose == 'highlighting';
    }) : null;

  // 2. Keep the value in a variable
  var currentCheckValue = currentCheckBody ? currentCheckBody.value : false;

  // 3. Triggers callbacks on user action
  var toggleCheck = function (evt) {
    if (currentCheckBody) {
      args.onUpdateBody(currentCheckBody, {
        type: 'TextualBody',
        purpose: 'highlighting',
        value: evt.target.checked
      });
    } else {
      args.onAppendBody({
        type: 'TextualBody',
        purpose: 'highlighting',
        value: evt.target.checked
      });
    }
  }

  // 4. This part renders the UI elements
  var createCheckbox = function (checked) {
    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = checked;
    checkbox.addEventListener('change', toggleCheck);
    return checkbox;
  }
  var createLabel = function () {
    var label = document.createElement('label');
    label.textContent = 'Дополнительная аннотация';

    return label;
  }

  var container = document.createElement('div');
  container.className = 'checkbox-widget';

  var checkbox = createCheckbox(currentCheckValue);
  var label = createLabel();

  container.appendChild(checkbox);
  container.appendChild(label);

  return container;
}

var ColorFormatter = function (annotation) {
  var highlightBody = annotation.bodies.find(function (b) {
    return b.purpose == 'highlighting';
  });

  if (highlightBody)
    return highlightBody.value;
}

function submitCorrectedSentence(sentenceId) {
  const originalSentence = $(`#sentence-${sentenceId}`).text();
  const correctedSentence = $(`#corrected-sentence-input-${sentenceId}`).val();

  // API request to auto_annotate
  $.ajax({
    url: '/api/auto_annotate/',
    type: 'post',
    data: {
      original_sentence: originalSentence,
      corrected_sentence: correctedSentence,
      csrfmiddlewaretoken: getCSRFToken(),
    },
    success: function (response) {
      // Create new annotations
      response.annotations.forEach((annotation) => {
        const sentence = document.getElementById(`sentence-${sentenceId}`);
        const guid = annotation.guid;
        const documentId = sentence.dataset.documentId;
        const userId = sentence.dataset.userId;
        const alt = false;
        const body = annotation.body;
        createAnnotation(documentId, sentenceId, userId, guid, alt, body);
        console.log('Annotation created:', annotation);
      });
      // refresh the page
      window.location.reload(true);
    },
    error: function (error) {
      console.error('Error fetching auto annotations:', error);
    },
  });
}


function initRecogito(canAnnotate, isLoggedIn) {
  console.log(`canAnnotate: ${canAnnotate}, isLoggedIn: ${isLoggedIn}`);
  if (!isLoggedIn) {
    setupRecogito(canAnnotate);
    return;
  }
  // Fetch user info from /api/get_user_info/ using AJAX
  $.ajax({
    url: '/api/get_user_info/',
    type: 'GET',
    success: function (data) {
      setupRecogito(canAnnotate, data);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      setupRecogito(canAnnotate);
    }
  });
}

function setupRecogito(canAnnotate, data = null) {
  // Get all the elements with the class 'sentence'
  const sentences = document.querySelectorAll('.sentence');

  // Initialize Recogito for each sentence with the fetched user info
  sentences.forEach((sentence) => {
    // Create a unique ID for each sentence element
    // Initialize a RecogitoJS instance for the sentence element
    const r = Recogito.init({
      allowEmpty: true,
      content: document.getElementById(sentence.id),
      readOnly: !canAnnotate,
      showTooltip: true,
      selectors: [{type: 'TextQuoteSelector'}],
      locale: 'ru',
      widgets: [
        CheckboxWidget,
        'COMMENT',
        {
          widget: 'TAG',
          vocabulary: ['Graph', 'Hyphen', 'Space', 'Ortho', 'Translit', 'Misspell', 'Deriv', 'Infl', 'Num', 'Gender', 'Morph', 'Asp', 'ArgStr', 'Passive', 'Refl', 'AgrNum', 'AgrCase', 'AgrGender', 'AgrPers', 'AgrGerund', 'Gov', 'Ref', 'Conj', 'WO', 'Neg', 'Aux', 'Brev', 'Syntax', 'Constr', 'Lex', 'CS', 'Par', 'Idiom', 'Transfer', 'Not-clear', 'Del', 'Insert', 'Transp', 'Subst', 'Altern', 'Tense', 'Mode']
        },
      ],
      mode: 'html',
      formatter: ColorFormatter
    });

    // Set user info for the Recogito instance
    if (data) {
      r.setAuthInfo(data);
    }

    if (sentence.dataset.alt === 'true') {
      r.loadAnnotations(`/api/annotations/get/alt/${sentence.dataset.sentenceId}/`);
    } else {
      r.loadAnnotations(`/api/annotations/get/${sentence.dataset.sentenceId}/`);
    }

    r.on('createAnnotation', async (annotation, overrideId) => {
      // TODO проверять, что аннотации не залезают друг на друга
      // Посылаем POST-запрос на сервер для сохранения аннотации
      await createAnnotation(
        sentence.dataset.documentId,
        sentence.dataset.sentenceId,
        sentence.dataset.userId,
        annotation.id,
        sentence.dataset.alt,
        annotation
      );
      console.log('Stored annotation:', annotation);
      refreshCorrections();
    });
    r.on('updateAnnotation', async (annotation, previous) => {
      // Посылаем POST-запрос на сервер для сохранения аннотации
      await updateAnnotation(
        sentence.dataset.documentId,
        sentence.dataset.sentenceId,
        sentence.dataset.userId,
        annotation.id,
        sentence.dataset.alt,
        annotation
      );
      console.log('Stored annotation:', annotation);
      refreshCorrections();
    });
    r.on('deleteAnnotation', async (annotation) => {
      // Посылаем POST-запрос на сервер для удаления аннотации
      await deleteAnnotation(annotation.id);
      console.log('Deleted annotation:', annotation);
      refreshCorrections();
    });
  });
}