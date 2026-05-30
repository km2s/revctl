import pytest
import json
from unittest.mock import patch, MagicMock
from cli_review import ollama


class TestIsRunning:
    def test_returns_true_when_ollama_responds(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("httpx.get", return_value=mock_resp):
            assert ollama.is_running() is True

    def test_returns_false_when_connection_refused(self):
        with patch("httpx.get", side_effect=Exception("connection refused")):
            assert ollama.is_running() is False

    def test_returns_false_on_non_200(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        with patch("httpx.get", return_value=mock_resp):
            assert ollama.is_running() is False


class TestListModels:
    def test_returns_model_names(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [
                {"name": "qwen2.5-coder:7b"},
                {"name": "codellama:7b"},
            ]
        }
        mock_resp.raise_for_status = MagicMock()
        with patch("httpx.get", return_value=mock_resp):
            result = ollama.list_models()
        assert result == ["qwen2.5-coder:7b", "codellama:7b"]

    def test_returns_empty_list_when_no_models(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"models": []}
        mock_resp.raise_for_status = MagicMock()
        with patch("httpx.get", return_value=mock_resp):
            result = ollama.list_models()
        assert result == []


class TestStreamReview:
    def test_yields_tokens_from_stream(self):
        lines = [
            json.dumps({"response": "Hello", "done": False}),
            json.dumps({"response": " world", "done": False}),
            json.dumps({"response": "!", "done": True}),
        ]

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_stream = MagicMock(return_value=mock_response)

        with patch("httpx.stream", mock_stream):
            tokens = list(ollama.stream_review("qwen2.5-coder:7b", "review this"))

        assert tokens == ["Hello", " world", "!"]

    def test_stops_at_done_token(self):
        lines = [
            json.dumps({"response": "first", "done": False}),
            json.dumps({"response": "", "done": True}),
            json.dumps({"response": "should not appear", "done": False}),
        ]

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("httpx.stream", MagicMock(return_value=mock_response)):
            tokens = list(ollama.stream_review("qwen2.5-coder:7b", "review this"))

        assert "should not appear" not in tokens
