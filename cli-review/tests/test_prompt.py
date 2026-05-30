from cli_review.prompt import build_review_prompt, MAX_DIFF_CHARS

SAMPLE_DIFF = """\
diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -1,5 +1,8 @@
+import os
+
 def get_user(id):
-    return db.query(f"SELECT * FROM users WHERE id={id}")
+    query = "SELECT * FROM users WHERE id = %s"
+    return db.query(query, (id,))
"""


def test_prompt_contains_diff():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", None)
    assert SAMPLE_DIFF in result


def test_prompt_contains_source():
    result = build_review_prompt(SAMPLE_DIFF, "commit abc1234", None)
    assert "commit abc1234" in result


def test_prompt_security_focus():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", "security")
    assert "security" in result.lower()


def test_prompt_performance_focus():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", "performance")
    assert "performance" in result.lower()


def test_prompt_style_focus():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", "style")
    assert "style" in result.lower()


def test_prompt_no_focus_has_no_focus_instruction():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", None)
    assert "Focus especially" not in result


def test_prompt_truncates_large_diff():
    large_diff = "+" + "x" * (MAX_DIFF_CHARS + 500)
    result = build_review_prompt(large_diff, "staged changes", None)
    assert "truncated" in result
    assert len(result) < len(large_diff) + 1000


def test_prompt_no_truncation_note_for_small_diff():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", None)
    assert "truncated" not in result


def test_prompt_has_required_sections():
    result = build_review_prompt(SAMPLE_DIFF, "staged changes", None)
    for section in ["## Summary", "## Issues", "## Security", "## Suggestions", "## Verdict"]:
        assert section in result
