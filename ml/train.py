"""Train and evaluate the GitHub issue classification model."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline

from ml.preprocessing import combine_issue_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "github_issues.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "issue_classifier.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

RANDOM_STATE = 42


def load_and_prepare_data() -> tuple[pd.Series, pd.Series]:
    """Load, clean, and deduplicate issue text."""
    dataset = pd.read_csv(DATA_PATH)

    dataset["text"] = [
        combine_issue_text(title, body)
        for title, body in zip(
            dataset["title"],
            dataset["body"],
            strict=True,
        )
    ]

    initial_size = len(dataset)

    dataset = dataset[dataset["text"].str.len() >= 20]
    dataset = dataset.drop_duplicates(subset=["text"]).reset_index(drop=True)

    removed_count = initial_size - len(dataset)
    print(f"Removed {removed_count} empty or duplicate issues.")
    print(f"Training dataset size: {len(dataset)}")

    return dataset["text"], dataset["label"]


def build_pipeline() -> Pipeline:
    """Create the complete text-classification pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    max_features=25_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    solver="lbfgs",
                    max_iter=1_000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def main() -> None:
    """Train, evaluate, and serialize the model pipeline."""
    features, labels = load_and_prepare_data()

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    pipeline = build_pipeline()

    cross_validation = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    cv_scores = cross_val_score(
        pipeline,
        x_train,
        y_train,
        cv=cross_validation,
        scoring="f1_macro",
        n_jobs=-1,
    )

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    class_names = sorted(labels.unique())
    accuracy = accuracy_score(y_test, predictions)
    macro_f1 = f1_score(y_test, predictions, average="macro")

    report = classification_report(
        y_test,
        predictions,
        labels=class_names,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=class_names,
    )

    print(f"\nTest accuracy: {accuracy:.3f}")
    print(f"Test macro F1: {macro_f1:.3f}")
    print(
        "Cross-validation macro F1: "
        f"{cv_scores.mean():.3f} ± {cv_scores.std():.3f}"
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=class_names,
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(
        pd.DataFrame(
            matrix,
            index=class_names,
            columns=class_names,
        )
    )

    metrics = {
        "dataset_size": int(len(features)),
        "training_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "accuracy": round(float(accuracy), 4),
        "macro_f1": round(float(macro_f1), 4),
        "cross_validation_macro_f1_mean": round(
            float(cv_scores.mean()),
            4,
        ),
        "cross_validation_macro_f1_std": round(
            float(cv_scores.std()),
            4,
        ),
        "labels": class_names,
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    with METRICS_PATH.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)

    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()