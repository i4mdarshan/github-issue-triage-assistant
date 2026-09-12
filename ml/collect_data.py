"""Collect labeled issues from the Kubernetes GitHub repository."""

import os
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
import requests


REPOSITORY = "kubernetes/kubernetes"
TARGET_PER_CLASS = 150
MAX_PAGES = 3

LABEL_MAP = {
    "bug": "kind/bug",
    "feature": "kind/feature",
    "documentation": "kind/documentation",
    "question": "kind/support",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "github_issues.csv"
load_dotenv(PROJECT_ROOT / ".env")


def build_headers() -> dict[str, str]:
    """Create GitHub API headers with an optional access token."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def fetch_category(category: str, github_label: str) -> list[dict]:
    """Fetch issues carrying one GitHub label."""
    url = f"https://api.github.com/repos/{REPOSITORY}/issues"
    collected = []

    for page in range(1, MAX_PAGES + 1):
        response = requests.get(
            url,
            headers=build_headers(),
            params={
                "state": "all",
                "labels": github_label,
                "per_page": 100,
                "page": page,
            },
            timeout=30,
        )

        if response.status_code == 403:
            raise RuntimeError(
                "GitHub API rate limit reached. "
                "Wait before retrying or provide a GITHUB_TOKEN."
            )

        response.raise_for_status()
        results = response.json()

        if not results:
            break

        for issue in results:
            # GitHub's issue endpoint also returns pull requests.
            if "pull_request" in issue:
                continue

            title = (issue.get("title") or "").strip()
            body = (issue.get("body") or "").strip()

            if len(f"{title} {body}") < 30:
                continue

            collected.append(
                {
                    "title": title,
                    "body": body,
                    "label": category,
                    "url": issue["html_url"],
                }
            )

            if len(collected) >= TARGET_PER_CLASS:
                return collected

    return collected


def main() -> None:
    """Collect, balance, and save the dataset."""
    all_issues = []

    for category, github_label in LABEL_MAP.items():
        print(f"Collecting {category} issues using '{github_label}'...")
        issues = fetch_category(category, github_label)
        all_issues.extend(issues)
        print(f"Collected {len(issues)} {category} issues.")

    dataset = pd.DataFrame(all_issues)

    # Remove issues appearing in more than one target category.
    dataset = dataset.drop_duplicates(subset=["url"], keep=False)

    counts = (
        dataset["label"]
        .value_counts()
        .reindex(LABEL_MAP.keys(), fill_value=0)
    )

    print("\nAvailable examples:")
    print(counts.to_string())

    smallest_class = int(counts.min())

    if smallest_class < 40:
        raise RuntimeError(
            "Not enough examples were collected for every category."
        )

    sample_size = min(smallest_class, TARGET_PER_CLASS)

    balanced_parts = [
        group.sample(n=sample_size, random_state=42)
        for _, group in dataset.groupby("label")
    ]

    balanced_dataset = (
        pd.concat(balanced_parts, ignore_index=True)
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    balanced_dataset.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved {len(balanced_dataset)} issues to {OUTPUT_PATH}")
    print("\nFinal class distribution:")
    print(balanced_dataset["label"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()