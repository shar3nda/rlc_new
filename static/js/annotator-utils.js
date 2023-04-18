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

async function createAnnotation(documentId, sentenceId, userId, guid, body) {
  const url = '/api/annotations/create/';
  const data = {
    document: documentId, sentence: sentenceId, user: userId, guid: guid, body
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

async function updateAnnotation(documentId, sentenceId, userId, guid, body) {
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

function initRecogito() {
  // Get all the elements with the class 'sentence'
  const sentences = document.querySelectorAll('.sentence');

  // Loop through each sentence and initialize RecogitoJS
  sentences.forEach((sentence) => {
    // Create a unique ID for each sentence element
    // Initialize a RecogitoJS instance for the sentence element
    console.log(`Initializing RecogitoJS for sentence ${sentence.id}`);
    const r = Recogito.init({
      allowEmpty: false,
      content: document.getElementById(sentence.id), readOnly: false,
      showTooltip: true,
      selectors: [{type: 'TextQuoteSelector'}],
      locale: 'ru',
      widgets: [
        'COMMENT',
        {
          widget: 'TAG',
          vocabulary: ['Graph', 'Hyphen', 'Space', 'Ortho', 'Translit', 'Misspell', 'Deriv', 'Infl', 'Num', 'Gender', 'Morph', 'Asp', 'ArgStr', 'Passive', 'Refl', 'AgrNum', 'AgrCase', 'AgrGender', 'AgrPers', 'AgrGerund', 'Gov', 'Ref', 'Conj', 'WO', 'Neg', 'Aux', 'Brev', 'Syntax', 'Constr', 'Lex', 'CS', 'Par', 'Idiom', 'Transfer', 'Not-clear', 'Del', 'Insert', 'Transp', 'Subst', 'Altern', 'Tense', 'Mode']
        },
      ],
    });
    r.loadAnnotations(`/api/annotations/get/${sentence.dataset.sentenceId}/`);
    r.on('createAnnotation', async (annotation, overrideId) => {
      // TODO проверять, что аннотации не залезают друг на друга
      // Посылаем POST-запрос на сервер для сохранения аннотации
      await createAnnotation(
        sentence.dataset.documentId,
        sentence.dataset.sentenceId,
        sentence.dataset.userId,
        annotation.id,
        annotation
      );
      console.log('Stored annotation:', annotation);
    });
    r.on('updateAnnotation', async (annotation, previous) => {
      // Посылаем POST-запрос на сервер для сохранения аннотации
      await updateAnnotation(
        sentence.dataset.documentId,
        sentence.dataset.sentenceId,
        sentence.dataset.userId,
        annotation.id,
        annotation
      );
      console.log('Stored annotation:', annotation);
    });
    r.on('deleteAnnotation', async (annotation) => {
      // Посылаем POST-запрос на сервер для удаления аннотации
      await deleteAnnotation(annotation.id);
      console.log('Deleted annotation:', annotation);
    });
  });
}
