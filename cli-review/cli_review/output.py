from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text

console = Console()


def print_header(source: str, model: str) -> None:
    console.print(
        Panel(
            f"[bold cyan]Reviewing:[/bold cyan] {source}\n"
            f"[bold cyan]Model:[/bold cyan]    {model}  [dim](local · no data sent)[/dim]",
            title="[bold]cli-review[/bold]",
            border_style="cyan",
        )
    )


def print_error(message: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def stream_markdown(token_iterator) -> str:
    collected = []
    with Live(console=console, refresh_per_second=15) as live:
        for token in token_iterator:
            collected.append(token)
            text = "".join(collected)
            live.update(Markdown(text))
    return "".join(collected)


def print_done(char_count: int) -> None:
    console.print(f"\n[dim]Review complete · {char_count} chars[/dim]")


def spinner(message: str) -> Live:
    return Live(
        Text.assemble(Spinner("dots").render(0), " ", message),
        console=console,
        refresh_per_second=10,
    )
