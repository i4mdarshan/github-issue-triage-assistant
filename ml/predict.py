"""Reusable prediction interface for the issue classifier."""

from pathlib import Path
from typing import Any

import joblib

from ml.preprocessing import combine_issue_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "issue_classifier.joblib"
REVIEW_CONFIDENCE_THRESHOLD = 0.35
REVIEW_MARGIN_THRESHOLD = 0.05


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

        raw_probability_by_label = {
            str(label): float(probability)
            for label, probability in zip(
                class_names,
                probabilities,
                strict=True,
            )
        }

        predicted_label = max(
            raw_probability_by_label,
            key=raw_probability_by_label.get,
        )

        ranked_probabilities = sorted(
            raw_probability_by_label.values(),
            reverse=True,
        )

        confidence = ranked_probabilities[0]
        confidence_margin = (
            ranked_probabilities[0] - ranked_probabilities[1]
        )

        requires_review = (
            confidence < REVIEW_CONFIDENCE_THRESHOLD
            or confidence_margin < REVIEW_MARGIN_THRESHOLD
        )

        probability_by_label = {
            label: round(probability, 4)
            for label, probability in raw_probability_by_label.items()
        }

        return {
            "label": predicted_label,
            "confidence": round(confidence, 4),
            "confidence_margin": round(confidence_margin, 4),
            "requires_review": requires_review,
            "probabilities": probability_by_label,
        }