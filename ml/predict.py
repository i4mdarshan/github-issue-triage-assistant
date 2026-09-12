"""Reusable prediction interface for the issue classifier."""

from pathlib import Path
from typing import Any

import joblib

from ml.preprocessing import combine_issue_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "issue_classifier.joblib"


class IssueClassifier:
    """Load the trained pipeline and classify GitHub issues."""

    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model was not found at {model_path}. "
                "Run `python -m ml.train` first."
            )

        self.pipeline = joblib.load(model_path)

    def predict(self, title: str, body: str = "") -> dict[str, Any]:
        """Predict an issue category and its probability distribution."""
        text = combine_issue_text(title, body)

        if len(text) < 10:
            raise ValueError(
                "The issue title and description are too short."
            )

        probabilities = self.pipeline.predict_proba([text])[0]
        class_names = self.pipeline.named_steps["classifier"].classes_

        probability_by_label = {
            str(label): round(float(probability), 4)
            for label, probability in zip(
                class_names,
                probabilities,
                strict=True,
            )
        }

        predicted_label = max(
            probability_by_label,
            key=probability_by_label.get,
        )

        return {
            "label": predicted_label,
            "confidence": probability_by_label[predicted_label],
            "probabilities": probability_by_label,
        }