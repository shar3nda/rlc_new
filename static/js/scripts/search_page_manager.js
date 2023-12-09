const parseFormData = (formData) => {
  const object = {};
  formData.forEach((value, key) => {
    if (key.endsWith("[]")) {
      object[key] = object[key] || [];
      object[key].push(value.trim());
    } else {
      object[key] = value.trim();
    }
  });
  return object;
};

let documentIds = new Set();

const performSearch = (endpoint, data, loadMore = false) => {
  const loadMoreButton = document.querySelector("#load-more-button");

  if (!loadMore) {
    document.querySelector("#search-results-container").innerHTML = `
      <div class="d-flex justify-content-center" style="display: none;" id="spinner-container">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>`;
  } else {
    loadMoreButton.setAttribute("disabled", "disabled");
    loadMoreButton.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span role="status">${loadMoreButton.innerHTML}</span>`;
  }

  let chunk_start = 0;
  if (loadMore) {
    chunk_start = parseInt(loadMoreButton.dataset.chunkStart);
  }

  const payload = {
    ...data,
    chunk_start: chunk_start,
    settings: parseFormData(new FormData(document.querySelector("#subcorpus-form"))),
    page_size: document.querySelector("#page-size-selector").value,
  };

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(payload),
  })
    .then((res) => res.text())
    .then((data) => {
      displaySearchResults(data, loadMore);
    })
    .catch((error) => {
      console.error("Error:", error);
      document.querySelector("#search-results-container").innerHTML = "<p>Something went wrong.</p>";
    });
};

const updateStats = (container) => {
  const { ids: chunkDocumentsIds } = container.querySelector(".chunk-documents-ids").dataset;
  const { count: chunkSentencesCountStr } = container.querySelector(".chunk-sentences-count").dataset;

  const chunkDocumentsIdsArray = chunkDocumentsIds.split(",").filter(Boolean).map(Number);
  const chunkSentencesCount = parseInt(chunkSentencesCountStr, 10);

  const documentStats = document.querySelector("#found-documents-count");
  const sentenceStats = document.querySelector("#found-sentences-count");

  documentIds = new Set([...documentIds, ...chunkDocumentsIdsArray]);
  documentStats.innerText = documentIds.size;
  sentenceStats.innerText = parseInt(sentenceStats.innerText, 10) + chunkSentencesCount;
};

const displaySearchResults = (data, loadMore = false) => {
  const searchResultsContainer = document.querySelector("#search-results-container");
  const sentencesContainer = document.querySelector("#sentences-container");

  if (!loadMore) {
    searchResultsContainer.innerHTML = data;
    const initialIdsSelector = searchResultsContainer.querySelector("#found-documents-ids-initial");
    const initialIds = initialIdsSelector.dataset.foundDocumentsIds.split(",").filter(Boolean).map(Number);
    documentIds = new Set(initialIds);
    initialIdsSelector.remove();

    const foundDocumentsCountEl = document.getElementById("found-documents-count");
    foundDocumentsCountEl && (foundDocumentsCountEl.innerHTML = documentIds.size);
  } else {
    document.querySelectorAll(".chunk-stats").forEach((el) => el.remove());
    document.querySelector("#load-more-button")?.remove();
    sentencesContainer.insertAdjacentHTML("beforeend", data);
    updateStats(sentencesContainer);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  const searchResultsContainer = document.querySelector("#search-results-container");
  const exactSearchForm = document.querySelector("#exact-search-form");
  const lexgramForm = document.querySelector("#lexgram-form");

  searchResultsContainer.addEventListener("show.bs.modal", (event) => {
    if (event.target.id === "context-modal") {
      fetchContext(event.relatedTarget.dataset.sentenceId);
    }
  });

  exactSearchForm.addEventListener("submit", (e) => handleSearchSubmit(e, "exact"));
  lexgramForm.addEventListener("submit", (e) => handleSearchSubmit(e, "lexgram"));

  searchResultsContainer.addEventListener("click", (event) => {
    if (event.target.id === "load-more-button") {
      handleLoadMore(event.target.dataset.searchType);
    }
  });
});

function fetchContext(sentenceId) {
  fetch(`/api/get_sentence_context?sentence_id=${sentenceId}`)
    .then((response) => response.json())
    .then((data) => updateContextModal(data))
    .catch((error) => console.error("Error:", error));
}

function updateContextModal(data) {
  document.getElementById("context-modal-body").innerHTML = `${
    data.previous ? `${data.previous}<br><br>` : ""
  }<strong>${data.current}</strong>${data.next ? `<br><br>${data.next}` : ""}`;
  document.getElementById("context-modal-label").innerText = data.document_title;
}

function handleSearchSubmit(event, searchType) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const queryData =
    searchType === "exact" ? { query: formData.get("exact_forms").trim() } : { tokens: parseFormData(formData) };
  performSearch(`/corpus/${searchType}_search_results/`, queryData);
}

function handleLoadMore(searchType) {
  const queryData =
    searchType === "exact"
      ? { query: document.querySelector("#exact-search-input").value.trim() }
      : { tokens: parseFormData(new FormData(document.querySelector("#lexgram-form"))) };
  performSearch(`/corpus/${searchType}_search_results/`, queryData, true);
}
