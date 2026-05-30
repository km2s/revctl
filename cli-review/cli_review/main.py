from typing import Annotated, Optional
import typer
from . import git, ollama, prompt, output

app = typer.Typer(
    name="revctl",
    help="Local AI code reviewer. Runs entirely on your machine via Ollama.",
    no_args_is_help=True,
)

DEFAULT_MODEL = "qwen2.5-coder:7b"
FocusOption = Annotated[
    Optional[str],
    typer.Option("--focus", "-f", help="Focus area: security | performance | style"),
]
ModelOption = Annotated[
    str,
    typer.Option("--model", "-m", help="Ollama model to use"),
]


def _preflight(model: str) -> None:
    if not ollama.is_running():
        output.print_error("Ollama is not running. Start it with: ollama serve")
        raise typer.Exit(1)

    available = ollama.list_models()
    if model not in available:
        output.print_warning(f"Model '{model}' not found locally.")
        output.print_warning(f"Pull it with: ollama pull {model}")
        if available:
            output.console.print(f"[dim]Available: {', '.join(available)}[/dim]")
        raise typer.Exit(1)


def _run_review(diff_result: git.DiffResult, model: str, focus: str | None) -> None:
    if diff_result.is_empty:
        output.print_warning("No changes found to review.")
        raise typer.Exit(0)

    _preflight(model)
    output.print_header(diff_result.source, model)

    p = prompt.build_review_prompt(diff_result.diff, diff_result.source, focus)
    tokens = ollama.stream_review(model, p)
    review_text = output.stream_markdown(tokens)
    output.print_done(len(review_text))


@app.command()
def diff(
    model: ModelOption = DEFAULT_MODEL,
    focus: FocusOption = None,
) -> None:
    """Review staged changes (falls back to unstaged if nothing is staged)."""
    if not git.is_git_repo():
        output.print_error("Not inside a git repository.")
        raise typer.Exit(1)
    try:
        result = git.get_staged_diff()
    except RuntimeError as e:
        output.print_error(str(e))
        raise typer.Exit(1)
    _run_review(result, model, focus)


@app.command()
def commit(
    hash: Annotated[str, typer.Argument(help="Commit hash to review")],
    model: ModelOption = DEFAULT_MODEL,
    focus: FocusOption = None,
) -> None:
    """Review a specific commit by its hash."""
    if not git.is_git_repo():
        output.print_error("Not inside a git repository.")
        raise typer.Exit(1)
    try:
        result = git.get_commit_diff(hash)
    except RuntimeError as e:
        output.print_error(str(e))
        raise typer.Exit(1)
    _run_review(result, model, focus)


@app.command()
def branch(
    head: Annotated[str, typer.Argument(help="Branch to review (your feature branch)")],
    base: Annotated[str, typer.Argument(help="Base branch to compare against")] = "main",
    model: ModelOption = DEFAULT_MODEL,
    focus: FocusOption = None,
) -> None:
    """Review all changes between two branches (like a local PR review)."""
    if not git.is_git_repo():
        output.print_error("Not inside a git repository.")
        raise typer.Exit(1)
    try:
        result = git.get_branch_diff(head, base)
    except RuntimeError as e:
        output.print_error(str(e))
        raise typer.Exit(1)
    _run_review(result, model, focus)


@app.command()
def models() -> None:
    """List all Ollama models available on this machine."""
    if not ollama.is_running():
        output.print_error("Ollama is not running. Start it with: ollama serve")
        raise typer.Exit(1)
    available = ollama.list_models()
    if not available:
        output.print_warning("No models found. Pull one with: ollama pull qwen2.5-coder:7b")
        return
    output.console.print("[bold]Available models:[/bold]")
    for m in available:
        marker = " [green]← default[/green]" if m == DEFAULT_MODEL else ""
        output.console.print(f"  {m}{marker}")
