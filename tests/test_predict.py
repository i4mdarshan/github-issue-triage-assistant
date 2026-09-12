import pytest

from ml.predict import IssueClassifier


@pytest.fixture(scope="module")
def classifier() -> IssueClassifier:
    return IssueClassifier()


def test_prediction_contains_expected_fields(
    classifier: IssueClassifier,
) -> None:
    result = classifier.predict(
        title="Application crashes when configuration is missing",
        body=(
            "The server exits unexpectedly instead of displaying "
            "a validation error."
        ),
    )

    assert set(result) == {
        "label",
        "confidence",
        "probabilities",
    }

    assert result["label"] in {
        "bug",
        "feature",
        "documentation",
        "question",
    }

    assert 0 <= result["confidence"] <= 1
    assert result["label"] == max(
        result["probabilities"],
        key=result["probabilities"].get,
    )

    assert sum(result["probabilities"].values()) == pytest.approx(
        1.0,
        abs=0.001,
    )


def test_rejects_input_that_is_too_short(
    classifier: IssueClassifier,
) -> None:
    with pytest.raises(ValueError):
        classifier.predict(title="Help", body="")