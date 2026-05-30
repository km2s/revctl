MAX_DIFF_CHARS = 12_000


def build_review_prompt(diff: str, source: str, focus: str | None) -> str:
    diff_preview = diff[:MAX_DIFF_CHARS]
    truncated = len(diff) > MAX_DIFF_CHARS

    focus_instruction = ""
    if focus == "security":
        focus_instruction = "Focus especially on security vulnerabilities (injections, auth issues, exposed secrets, etc.)."
    elif focus == "performance":
        focus_instruction = "Focus especially on performance bottlenecks, unnecessary loops, or inefficient data structures."
    elif focus == "style":
        focus_instruction = "Focus especially on code style, naming conventions, readability, and maintainability."

    truncation_note = "\n[NOTE: diff was truncated to fit context window]" if truncated else ""

    return f"""You are an expert code reviewer. Analyze the following git diff and provide a structured review.

Source: {source}{truncation_note}
{focus_instruction}

Respond with these sections (skip any section that has nothing to report):

## Summary
One or two sentences describing what this change does.

## Issues
List bugs, logic errors, or broken behavior. Be specific — include the relevant line or function name.

## Security
List any security concerns (exposed secrets, injection risks, missing validation, etc.).

## Suggestions
List improvements for readability, performance, or maintainability. These are non-blocking.

## Verdict
One of: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
Followed by one sentence explaining why.

---
DIFF:
```
{diff_preview}
```
"""
