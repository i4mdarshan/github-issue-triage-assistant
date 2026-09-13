const form = document.querySelector("#issue-form");
const titleInput = document.querySelector("#issue-title");
const bodyInput = document.querySelector("#issue-body");
const titleCount = document.querySelector("#title-count");
const bodyCount = document.querySelector("#body-count");
const submitButton = document.querySelector("#submit-button");
const buttonLabel = document.querySelector(".button-label");
const formError = document.querySelector("#form-error");

const emptyState = document.querySelector("#empty-state");
const loadingState = document.querySelector("#loading-state");
const predictionResult = document.querySelector("#prediction-result");
const predictedLabel = document.querySelector("#predicted-label");
const confidenceValue = document.querySelector("#confidence-value");
const probabilityList = document.querySelector("#probability-list");

const examples = {
  bug: {
    title: "Kubelet crashes when deleting a pod with an invalid volume mount",
    body:
      "What happened: the kubelet crashes with a nil pointer exception and " +
      "stops running. Steps to reproduce: create a pod with an invalid volume " +
      "mount and then delete it. Expected behavior: the kubelet should reject " +
      "the pod and continue running. Actual behavior: the kubelet terminates " +
      "every time. This is a regression in the latest release.",
  },
  feature: {
    title: "Add support for exporting results as JSON",
    body:
      "It would be useful to download the classification results as a JSON " +
      "file so they can be used in other developer tools.",
  },
  documentation: {
    title: "Document how to configure authentication",
    body:
      "The setup guide does not explain how environment variables should be " +
      "configured for authenticated API requests. Please add an example.",
  },
  question: {
    title: "How can I change the default server port?",
    body:
      "I am running another service on the default port. Is there a supported " +
      "way to configure the application to use a different port?",
  },
};

function updateCharacterCounts() {
  titleCount.textContent = `${titleInput.value.length} / 300`;
  bodyCount.textContent =
    `${bodyInput.value.length.toLocaleString()} / 20,000`;
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  form.setAttribute("aria-busy", String(isLoading));

  if (isLoading) {
    buttonLabel.textContent = "Analyzing...";
    emptyState.hidden = true;
    predictionResult.hidden = true;
    loadingState.hidden = false;
  } else {
    buttonLabel.textContent = "Analyze issue";
    loadingState.hidden = true;
  }
}

function showError(message) {
  formError.textContent = message;
  formError.hidden = false;
  emptyState.hidden = false;
  predictionResult.hidden = true;
}

function clearError() {
  formError.textContent = "";
  formError.hidden = true;
}

function formatApiError(payload) {
  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((error) => error.msg)
      .join(" ");
  }

  return "The issue could not be analyzed. Please try again.";
}

function renderPrediction(result) {
  predictedLabel.textContent = result.label;
  predictedLabel.dataset.label = result.label;

  confidenceValue.textContent =
    `${(result.confidence * 100).toFixed(1)}%`;

  const reviewStatus = document.querySelector("#review-status");
  reviewStatus.dataset.review = String(result.requires_review);
  reviewStatus.textContent = result.requires_review
    ? "Low confidence - maintainer review recommended"
    : "Prediction is sufficiently distinct";
  probabilityList.replaceChildren();

  const probabilities = Object.entries(result.probabilities).sort(
    ([, firstProbability], [, secondProbability]) =>
      secondProbability - firstProbability,
  );

  for (const [label, probability] of probabilities) {
    const percentage = probability * 100;

    const row = document.createElement("div");
    row.className = "probability-row";

    const heading = document.createElement("div");
    heading.className = "probability-heading";

    const name = document.createElement("span");
    name.textContent = label;

    const value = document.createElement("span");
    value.textContent = `${percentage.toFixed(1)}%`;

    heading.append(name, value);

    const track = document.createElement("div");
    track.className = "probability-track";
    track.setAttribute("role", "progressbar");
    track.setAttribute("aria-label", `${label} probability`);
    track.setAttribute("aria-valuemin", "0");
    track.setAttribute("aria-valuemax", "100");
    track.setAttribute("aria-valuenow", percentage.toFixed(1));

    const fill = document.createElement("div");
    fill.className = "probability-fill";

    track.append(fill);
    row.append(heading, track);
    probabilityList.append(row);

    requestAnimationFrame(() => {
      fill.style.width = `${percentage}%`;
    });
  }

  emptyState.hidden = true;
  predictionResult.hidden = false;
}

async function handleSubmit(event) {
  event.preventDefault();
  clearError();

  const title = titleInput.value.trim();
  const body = bodyInput.value.trim();

  if (`${title} ${body}`.trim().length < 10) {
    showError(
      "Please provide a more descriptive issue title or description.",
    );
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title, body }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(formatApiError(payload));
    }

    renderPrediction(payload);
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "The API could not be reached.";

    showError(message);
  } finally {
    setLoading(false);
  }
}

function loadExample(category) {
  const example = examples[category];

  if (!example) {
    return;
  }

  titleInput.value = example.title;
  bodyInput.value = example.body;

  updateCharacterCounts();
  clearError();
  titleInput.focus();
}

titleInput.addEventListener("input", updateCharacterCounts);
bodyInput.addEventListener("input", updateCharacterCounts);
form.addEventListener("submit", handleSubmit);

document.querySelectorAll(".example-button").forEach((button) => {
  button.addEventListener("click", () => {
    loadExample(button.dataset.example);
  });
});

updateCharacterCounts();