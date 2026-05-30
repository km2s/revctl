import pytest
from unittest.mock import patch, MagicMock
from cli_review import git

SAMPLE_DIFF = "diff --git a/foo.py b/foo.py\n+print('hello')\n"


def _mock_run(output: str, returncode: int = 0):
    mock = MagicMock()
    mock.stdout = output
    mock.stderr = ""
    mock.returncode = returncode
    return mock


class TestGetStagedDiff:
    def test_returns_staged_diff_when_present(self):
        with patch("subprocess.run", return_value=_mock_run(SAMPLE_DIFF)) as mock:
            result = git.get_staged_diff()
        assert result.diff == SAMPLE_DIFF
        assert result.is_empty is False
        mock.assert_called_once()

    def test_falls_back_to_unstaged_when_staged_empty(self):
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return _mock_run(SAMPLE_DIFF if call_count == 2 else "")

        with patch("subprocess.run", side_effect=side_effect):
            result = git.get_staged_diff()

        assert result.diff == SAMPLE_DIFF
        assert call_count == 2

    def test_empty_when_no_changes(self):
        with patch("subprocess.run", return_value=_mock_run("")):
            result = git.get_staged_diff()
        assert result.is_empty is True

    def test_raises_on_git_error(self):
        with patch("subprocess.run", return_value=_mock_run("", returncode=128)):
            with pytest.raises(RuntimeError):
                git.get_staged_diff()


class TestGetCommitDiff:
    def test_returns_diff_for_commit(self):
        with patch("subprocess.run", return_value=_mock_run(SAMPLE_DIFF)):
            result = git.get_commit_diff("abc1234")
        assert result.diff == SAMPLE_DIFF
        assert "abc1234" in result.source

    def test_source_shows_short_hash(self):
        with patch("subprocess.run", return_value=_mock_run(SAMPLE_DIFF)):
            result = git.get_commit_diff("abc12345678")
        assert "abc12345" in result.source

    def test_raises_on_invalid_hash(self):
        with patch("subprocess.run", return_value=_mock_run("bad object", returncode=128)):
            with pytest.raises(RuntimeError):
                git.get_commit_diff("notahash")


class TestGetBranchDiff:
    def test_returns_diff_between_branches(self):
        responses = [
            _mock_run("deadbeef\n"),
            _mock_run(SAMPLE_DIFF),
        ]
        with patch("subprocess.run", side_effect=responses):
            result = git.get_branch_diff("feature/x", "main")
        assert result.diff == SAMPLE_DIFF
        assert "feature/x" in result.source
        assert "main" in result.source

    def test_raises_when_merge_base_fails(self):
        with patch("subprocess.run", return_value=_mock_run("", returncode=128)):
            with pytest.raises(RuntimeError):
                git.get_branch_diff("feature/x", "main")


class TestIsGitRepo:
    def test_returns_true_inside_repo(self):
        with patch("subprocess.run", return_value=_mock_run("true\n")):
            assert git.is_git_repo() is True

    def test_returns_false_outside_repo(self):
        with patch("subprocess.run", return_value=_mock_run("", returncode=128)):
            assert git.is_git_repo() is False
