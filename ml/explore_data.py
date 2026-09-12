"""Inspect the collected GitHub issue dataset before model training."""

import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "github_issues.csv"

KIND_COMMAND_PATTERN = re.compile(
    r"(?im)^\s*/kind(?:/|\s+)"
    r"(?:bug|feature|documentation|support)\s*$"
)


def main() -> None:
    """Print data-quality and text-distribution statistics."""
    dataset = pd.read_csv(DATA_PATH)

    required_columns = {"title", "body", "label", "url"}
    missing_columns = required_columns - set(dataset.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns: {sorted(missing_columns)}"
        )

    print(f"Dataset shape: {dataset.shape}\n")

    print("Class distribution:")
    print(dataset["label"].value_counts().sort_index())
    print()

    print("Missing values:")
    print(dataset[list(required_columns)].isna().sum())
    print()

    dataset["title"] = dataset["title"].fillna("")
    dataset["body"] = dataset["body"].fillna("")
    dataset["text"] = (
        dataset["title"].str.strip()
        + " "
        + dataset["body"].str.strip()
    ).str.strip()

    dataset["normalized_text"] = (
        dataset["text"]
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    duplicate_count = int(
        dataset["normalized_text"].duplicated(keep=False).sum()
    )
    print(f"Duplicate issue texts: {duplicate_count}")

    dataset["word_count"] = dataset["text"].str.split().str.len()

    print("\nWord-count statistics by category:")
    print(
        dataset.groupby("label")["word_count"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(1)
    )

    dataset["contains_kind_command"] = dataset["text"].str.contains(
        KIND_COMMAND_PATTERN,
        regex=True,
        na=False,
    )

    print("\nIssues containing an explicit /kind label command:")
    print(
        dataset.groupby("label")["contains_kind_command"]
        .sum()
        .sort_index()
    )

    print("\nExample titles:")
    for label, group in dataset.groupby("label"):
        print(f"\n{label.upper()}")
        for title in group["title"].head(2):
            print(f"- {title}")


if __name__ == "__main__":
    main()