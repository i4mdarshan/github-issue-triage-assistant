"""Reusable text preprocessing for training and inference."""

import re


MAX_TEXT_LENGTH = 12_000

HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
KIND_COMMAND_PATTERN = re.compile(
    r"(?im)^\s*/kind(?:/|\s+)"
    r"(?:bug|feature|documentation|support)\s*$"
)
URL_PATTERN = re.compile(r"https?://\S+")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_value(value: object) -> str:
    """Convert a potentially missing dataframe value into text."""
    return value if isinstance(value, str) else ""


def combine_issue_text(title: object, body: object) -> str:
    """Combine and clean a GitHub issue title and body."""
    title_text = clean_value(title).strip()
    body_text = clean_value(body).strip()
    combined = f"{title_text}\n{body_text}"

    combined = HTML_COMMENT_PATTERN.sub(" ", combined)
    combined = KIND_COMMAND_PATTERN.sub(" ", combined)
    combined = URL_PATTERN.sub(" ", combined)
    combined = WHITESPACE_PATTERN.sub(" ", combined).strip()

    return combined[:MAX_TEXT_LENGTH]