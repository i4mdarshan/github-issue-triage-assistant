# GitHub Issue Triage Assistant

An ML-powered web application that automatically classifies GitHub issues into categories such as **bug**, **feature request**, **documentation**, and **question**.

The project demonstrates an end-to-end machine learning workflow, including data preparation, model training, evaluation, API development, frontend integration, and deployment.

## Features

- Collects labeled public issues through the GitHub REST API
- Cleans issue templates and removes label leakage
- Classifies issues as bug, feature, documentation, or question
- Returns confidence scores and all category probabilities
- Exposes predictions through a documented FastAPI endpoint
- Includes automated preprocessing, prediction, and API tests
- Provides a responsive vanilla HTML, CSS, and JavaScript interface with examples
- Includes example issues, loading and error states, and probability bars
- Visualizes every category probability
- Flags ambiguous predictions for human review
- Includes an SVG favicon and mobile-friendly styling
- Runs as a reproducible, non-root Docker container
- Exposes a container health check for deployment platforms

### In Progress

- Public live demo

## Running Locally

### Install the application

```bash
git clone git@github.com:i4mdarshan/github-issue-triage-assistant.git
cd github-issue-triage-assistant

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local development and automated tests, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Running with Docker

Build the production image:

```bash
docker build -t github-issue-triage-assistant .
```

Start the container:

```bash
docker run --rm \
  --name issue-triage-app \
  -p 7860:7860 \
  github-issue-triage-assistant
```

Open the application at:
```text
http://127.0.0.1:7860
````

The container includes the trained model, runs as a non-root user, and exposes a health check at /api/health.

The trained model is included in the repository, so dataset collection and training are not required to run the application.

### Start the API

```bash
uvicorn backend.main:app --reload
```

Open the web application:

```text
http://127.0.0.1:8000
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

### Collect the dataset

```bash
python -m ml.collect_data
```

### Retrain the model

```bash
python -m ml.train
```

Retraining creates:

- `models/issue_classifier.joblib`
- `models/metrics.json`


## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check API and model availability |
| `POST` | `/api/predict` | Classify an issue |

Example prediction request:

```json
{
  "title": "Application crashes during startup",
  "body": "The server exits when the configuration file is missing."
}
```

Example response:

```json
{
  "label": "bug",
  "confidence": 0.294,
  "confidence_margin": 0.037,
  "requires_review": true,
  "probabilities": {
    "bug": 0.294,
    "documentation": 0.257,
    "feature": 0.24,
    "question": 0.209
  }
}
```

## Machine Learning Approach

The initial model will use:

- TF-IDF text features
- Logistic Regression classification
- Accuracy, precision, recall, and F1-score evaluation

A lightweight baseline model keeps inference fast while providing interpretable class probabilities.

## Technology Stack

- Python
- scikit-learn
- pandas
- FastAPI
- HTML
- CSS
- JavaScript
- Docker
- Hugging Face Spaces or Render

## Project Structure

```text
github-issue-triage-assistant/
├── backend/       # FastAPI application
├── data/          # Training and evaluation data
├── frontend/      # HTML, CSS, and JavaScript interface
├── ml/            # Model training and prediction code
├── models/        # Generated model artifacts
├── tests/         # Automated tests
├── requirements.txt
└── README.md
```

## Collect the dataset

```bash
python -m ml.collect_data
```

## Train the model
```bash
python -m ml.train
```

Training creates:
- models/issue_classifier.joblib - serialized preprocessing and classification pipeline
- models/metrics.json - evaluation metrics and confusion matrix


Expand **Model Limitations** with:

```markdown
The current training data comes from one open-source repository, so writing conventions from that repository may influence predictions. Performance on issues from unrelated projects may be lower than the reported evaluation scores.

The dataset is relatively small, and the question category currently produces more false positives than the other categories. Future versions could use multiple repositories, additional labeled examples, and transformer-based embeddings.
```

## Environment Variables

GitHub authentication is optional but recommended when collecting the dataset because authenticated requests receive a higher API rate limit.

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ````
2. Create a fine-grained GitHub personal access token with public repository read access.
3. Add the token to .env


## Dataset

The training dataset is collected from public issues in the
[`kubernetes/kubernetes`](https://github.com/kubernetes/kubernetes) repository using the GitHub REST API.

GitHub labels are mapped to the application's categories:

| GitHub label | Application category |
|---|---|
| `kind/bug` | Bug |
| `kind/feature` | Feature |
| `kind/documentation` | Documentation |
| `kind/support` | Question |

The current dataset contains **580 issues**, with **145 examples per category**. Duplicate and multi-category issues are removed to prevent conflicting labels.

The generated CSV is intentionally excluded from Git. This keeps the repository small and allows the dataset to be reproduced from its original source.

### Collecting the Dataset

After configuring the optional `GITHUB_TOKEN`, run:

```bash
python -m ml.collect_data
````

### Text Preprocessing

The same reusable preprocessing function will be used during training and inference to prevent training-serving skew. It:

- Combines the issue title and description
- Removes GitHub issue-template HTML comments
- Removes explicit `/kind` commands to prevent label leakage
- Removes URLs and normalizes whitespace
- Limits unusually long issue text
- Handles missing descriptions safely

Preprocessing behavior is verified with automated tests.

### Baseline Model Results

The model was evaluated using a stratified 80/20 train-test split and five-fold cross-validation.

| Metric | Score |
|---|---:|
| Test accuracy | 82.76% |
| Test macro F1 | 83.02% |
| Cross-validation macro F1 | 75.28% ± 1.65% |

The feature category achieved the highest test F1 score at 91.23%. Question classification currently has the lowest precision and represents the primary area for future improvement.

### Uncertainty Handling

A prediction is marked for human review when:

- Its highest probability is below 35%, or
- The margin between its two highest probabilities is below five percentage points

This prevents ambiguous predictions from being presented as definitive automated decisions.


## Author
### Darshan Mahajan