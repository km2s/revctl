import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from cli_review.main import app
from cli_review.git import DiffResult

runner = CliRunner()

SAMPLE_DIFF = "diff --git a/foo.py b/foo.py\n+x = 1\n"


def _mock_stream(tokens=("Good code.", )):
    return iter(tokens)


class TestDiffCommand:
    def test_exits_1_outside_git_repo(self):
        with patch("cli_review.git.is_git_repo", return_value=False):
            result = runner.invoke(app, ["diff"])
        assert result.exit_code == 1
        assert "git repository" in result.output

    def test_exits_0_with_no_changes(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_staged_diff", return_value=DiffResult("", "staged", True)),
        ):
            result = runner.invoke(app, ["diff"])
        assert result.exit_code == 0
        assert "No changes" in result.output

    def test_exits_1_when_ollama_not_running(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_staged_diff", return_value=DiffResult(SAMPLE_DIFF, "staged changes", False)),
            patch("cli_review.ollama.is_running", return_value=False),
        ):
            result = runner.invoke(app, ["diff"])
        assert result.exit_code == 1
        assert "Ollama" in result.output

    def test_exits_1_when_model_not_available(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_staged_diff", return_value=DiffResult(SAMPLE_DIFF, "staged changes", False)),
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=["other-model:7b"]),
        ):
            result = runner.invoke(app, ["diff"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_runs_review_successfully(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_staged_diff", return_value=DiffResult(SAMPLE_DIFF, "staged changes", False)),
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=["qwen2.5-coder:7b"]),
            patch("cli_review.ollama.stream_review", return_value=_mock_stream()),
            patch("cli_review.output.stream_markdown", return_value="Good code."),
        ):
            result = runner.invoke(app, ["diff"])
        assert result.exit_code == 0


class TestCommitCommand:
    def test_requires_hash_argument(self):
        result = runner.invoke(app, ["commit"])
        assert result.exit_code != 0

    def test_exits_1_on_invalid_hash(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_commit_diff", side_effect=RuntimeError("bad object")),
        ):
            result = runner.invoke(app, ["commit", "notahash"])
        assert result.exit_code == 1
        assert "bad object" in result.output


class TestBranchCommand:
    def test_uses_main_as_default_base(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_branch_diff", return_value=DiffResult(SAMPLE_DIFF, "feat vs main", False)) as mock_branch,
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=["qwen2.5-coder:7b"]),
            patch("cli_review.ollama.stream_review", return_value=_mock_stream()),
            patch("cli_review.output.stream_markdown", return_value="ok"),
        ):
            runner.invoke(app, ["branch", "feat/x"])
        mock_branch.assert_called_once_with("feat/x", "main")

    def test_accepts_custom_base(self):
        with (
            patch("cli_review.git.is_git_repo", return_value=True),
            patch("cli_review.git.get_branch_diff", return_value=DiffResult(SAMPLE_DIFF, "feat vs dev", False)) as mock_branch,
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=["qwen2.5-coder:7b"]),
            patch("cli_review.ollama.stream_review", return_value=_mock_stream()),
            patch("cli_review.output.stream_markdown", return_value="ok"),
        ):
            runner.invoke(app, ["branch", "feat/x", "dev"])
        mock_branch.assert_called_once_with("feat/x", "dev")


class TestModelsCommand:
    def test_exits_1_when_ollama_not_running(self):
        with patch("cli_review.ollama.is_running", return_value=False):
            result = runner.invoke(app, ["models"])
        assert result.exit_code == 1

    def test_lists_available_models(self):
        with (
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=["qwen2.5-coder:7b", "codellama:7b"]),
        ):
            result = runner.invoke(app, ["models"])
        assert "qwen2.5-coder:7b" in result.output
        assert "codellama:7b" in result.output

    def test_warns_when_no_models(self):
        with (
            patch("cli_review.ollama.is_running", return_value=True),
            patch("cli_review.ollama.list_models", return_value=[]),
        ):
            result = runner.invoke(app, ["models"])
        assert "No models" in result.output
