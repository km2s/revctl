import subprocess
from dataclasses import dataclass


@dataclass
class DiffResult:
    diff: str
    source: str
    is_empty: bool


def _run(args: list[str]) -> str:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def get_staged_diff() -> DiffResult:
    diff = _run(["diff", "--cached"])
    if not diff.strip():
        diff = _run(["diff"])
    source = "staged changes" if diff.strip() else "working tree"
    return DiffResult(diff=diff, source=source, is_empty=not diff.strip())


def get_commit_diff(commit_hash: str) -> DiffResult:
    diff = _run(["show", "--format=", commit_hash])
    return DiffResult(diff=diff, source=f"commit {commit_hash[:8]}", is_empty=not diff.strip())


def get_branch_diff(head: str, base: str) -> DiffResult:
    merge_base = _run(["merge-base", base, head]).strip()
    diff = _run(["diff", merge_base, head])
    return DiffResult(diff=diff, source=f"{head} vs {base}", is_empty=not diff.strip())


def is_git_repo() -> bool:
    try:
        _run(["rev-parse", "--is-inside-work-tree"])
        return True
    except RuntimeError:
        return False
