from ml.preprocessing import MAX_TEXT_LENGTH, combine_issue_text


def test_removes_label_commands_comments_and_urls() -> None:
    text = combine_issue_text(
        "API crashes during startup",
        """
        <!-- Select the correct issue type. -->
        /kind bug

        Steps to reproduce: visit https://example.com/log
        and start the application.
        """,
    )

    assert "API crashes during startup" in text
    assert "Steps to reproduce" in text
    assert "/kind bug" not in text.lower()
    assert "select the correct issue type" not in text.lower()
    assert "https://" not in text


def test_handles_missing_body() -> None:
    text = combine_issue_text("Documentation needs an example", None)

    assert text == "Documentation needs an example"


def test_limits_document_length() -> None:
    text = combine_issue_text("Long issue", "word " * 5_000)

    assert len(text) == MAX_TEXT_LENGTH