"""CLI entry point for notes-cli."""

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import remove_unreferenced_images
from .image_processor import optimize_images, remove_original_images
from .markdown_updater import categorize_images, update_markdown_files
from .utils import find_all_images, find_all_markdown_files

console = Console()


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description=(
            "Cleanup and optimize images: remove unreferenced images, optimize referenced "
            "ones, update markdown files, and remove originals"
        )
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="uploads",
        help="Directory containing images (default: uploads)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--keep-originals",
        action="store_true",
        help="Keep original images after optimization",
    )

    args = parser.parse_args()

    # Print header
    console.print()
    console.print(Panel("🧹 Image Cleanup and Optimization Script", style="bold cyan"))

    if args.dry_run:
        console.print("[bold yellow]--- DRY RUN MODE (no changes will be made) ---[/bold yellow]")
        console.print()

    # Check if directory exists
    uploads_dir = Path(args.directory)
    if not uploads_dir.exists():
        console.print(f"[bold red]Error: Directory '{uploads_dir}' does not exist[/bold red]")
        return

    # Find all images and markdown files
    console.print("[cyan]Scanning for images and markdown files...[/cyan]")
    image_files = find_all_images(uploads_dir)
    markdown_files = find_all_markdown_files()

    console.print(f"[cyan]📁 Found {len(image_files)} images in {uploads_dir}[/cyan]")
    console.print(f"[cyan]📄 Found {len(markdown_files)} markdown files[/cyan]")

    # Categorize images
    referenced_images, unreferenced_images = categorize_images(image_files, markdown_files)

    # Step 1: Remove unreferenced images
    unreferenced_count = remove_unreferenced_images(unreferenced_images, args.dry_run)

    # Step 2: Optimize referenced images (named after markdown files)
    optimized_mapping = optimize_images(referenced_images, uploads_dir, args.dry_run)

    # Step 3: Update markdown files
    updated_files, updated_refs = update_markdown_files(optimized_mapping, args.dry_run)

    # Step 4: Remove original images
    removed_count, _ = remove_original_images(optimized_mapping, args.keep_originals, args.dry_run)

    # Final summary
    console.print()
    console.print(Panel("📊 FINAL SUMMARY", style="bold cyan"))

    # Create summary table
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan", width=30)
    summary_table.add_column("Count", justify="right", style="green")

    summary_table.add_row("Total images found", str(len(image_files)))
    summary_table.add_row("Unreferenced images removed", str(unreferenced_count))
    summary_table.add_row("Referenced images optimized", str(len(optimized_mapping)))

    if not args.dry_run:
        summary_table.add_row("Markdown files updated", str(updated_files))
        summary_table.add_row("Markdown references updated", str(updated_refs))
        if not args.keep_originals:
            summary_table.add_row("Original images removed", str(removed_count))

    console.print(summary_table)
    console.print()

    if args.dry_run:
        console.print(
            "[bold yellow]💡 This was a dry run. "
            "Run without --dry-run to apply changes.[/bold yellow]"
        )
    else:
        console.print("[bold green]✅ Image cleanup and optimization complete![/bold green]")


if __name__ == "__main__":
    main()
