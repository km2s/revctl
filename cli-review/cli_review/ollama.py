from typing import Iterator
import httpx

OLLAMA_URL = "http://localhost:11434"


def is_running() -> bool:
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_models() -> list[str]:
    r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]


def stream_review(model: str, prompt: str) -> Iterator[str]:
    with httpx.stream(
        "POST",
        f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": True},
        timeout=None,
    ) as response:
        response.raise_for_status()
        import json
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if token := chunk.get("response"):
                    yield token
                if chunk.get("done"):
                    break
