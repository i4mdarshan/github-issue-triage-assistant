# GitHub Issue Triage Assistant

An ML-powered web application that automatically classifies GitHub issues into categories such as **bug**, **feature request**, **documentation**, and **question**.

The project demonstrates an end-to-end machine learning workflow, including data preparation, model training, evaluation, API development, frontend integration, and deployment.

## Project Status

🚧 Currently under development.

## Planned Features

- Classify an issue from its title and description
- Display the predicted category and confidence score
- Compare multiple category probabilities
- Provide predictions through a REST API
- Offer a responsive HTML, CSS, and JavaScript interface
- Deploy the complete application as a live demo

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

## Running the Project
Local installation and usage instructions will be added as the application is developed.

### Collect the dataset

```bash
python -m ml.collect_data
```

### Train the model
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


## Author
### Darshan Mahajan