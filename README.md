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

## Author
### Darshan Mahajan