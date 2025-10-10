"""Core orchestration functions for the image cleanup process."""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from .utils import get_file_size

console = Console()


def remove_unreferenced_images(unreferenced_images: list[Path], dry_run: bool = False) -> int:
    """Remove images that are not referenced in any markdown file.

    Args:
        unreferenced_images: List of unreferenced image paths
        dry_run: If True, only show what would be done

    Returns:
        Number of images removed (or would be removed in dry-run mode)
    """
    console.print()
    console.print(Panel("📋 STEP 1: Removing unreferenced images", style="magenta bold"))

    if not unreferenced_images:
        console.print("[green]✓ No unreferenced images found - all images are being used![/green]")
        return 0

    console.print(f"[yellow]Found {len(unreferenced_images)} unreferenced image(s)[/yellow]\n")

    total_size = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Removing images...", total=len(unreferenced_images))

        for img_path in unreferenced_images:
            size = get_file_size(img_path)
            total_size += size
            size_kb = size / 1024

            if dry_run:
                console.print(
                    f"  [yellow]Would remove:[/yellow] {img_path.name} ({size_kb:.1f} KB) - "
                    "Reason: Not referenced in any markdown file"
                )
            else:
                img_path.unlink()
                console.print(
                    f"  [red]Removed:[/red] {img_path.name} ({size_kb:.1f} KB) - "
                    "Reason: Not referenced in any markdown file"
                )

            progress.advance(task)

    total_mb = total_size / (1024 * 1024)
    if dry_run:
        console.print(f"\n[yellow]Would free up: {total_mb:.1f} MB[/yellow]")
    else:
        console.print(f"\n[green]✓ Freed up: {total_mb:.1f} MB[/green]")

    return len(unreferenced_images)
