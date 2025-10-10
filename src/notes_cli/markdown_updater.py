"""Markdown file update functions."""

import re
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

console = Console()


def find_referencing_files(image_name: str, markdown_files: list[Path]) -> list[Path]:
    """Find all markdown files that reference this image.

    Args:
        image_name: Name of the image file
        markdown_files: List of markdown file paths to search

    Returns:
        List of markdown files that reference the image
    """
    referencing_files: list[Path] = []
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            if image_name in content:
                referencing_files.append(md_file)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {md_file}: {e}[/yellow]")
    return referencing_files


def categorize_images(
    image_files: list[Path], markdown_files: list[Path]
) -> tuple[list[tuple[Path, list[Path]]], list[Path]]:
    """Categorize images into referenced and unreferenced with their referencing files.

    Args:
        image_files: List of image file paths
        markdown_files: List of markdown file paths

    Returns:
        Tuple of (referenced, unreferenced) where:
        - referenced is a list of (image_path, referencing_files) tuples
        - unreferenced is a list of image paths
    """
    referenced: list[tuple[Path, list[Path]]] = []
    unreferenced: list[Path] = []

    for image_path in image_files:
        image_name = image_path.name
        referencing_files = find_referencing_files(image_name, markdown_files)

        if referencing_files:
            referenced.append((image_path, referencing_files))
        else:
            unreferenced.append(image_path)

    return referenced, unreferenced


def update_markdown_files(
    optimized_mapping: list[tuple[Path, Path, list[Path]]], dry_run: bool = False
) -> tuple[int, int]:
    """Update markdown files to reference optimized images.

    Args:
        optimized_mapping: List of (original_path, optimized_path, referencing_files) tuples
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (updated_files_count, updated_references_count)
    """
    from rich.panel import Panel

    console.print()
    console.print(Panel("📋 STEP 3: Updating markdown files", style="magenta bold"))

    if not optimized_mapping:
        console.print("[yellow]No images to update in markdown files[/yellow]")
        return 0, 0

    updated_files_set: set[Path] = set()
    updated_references = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Updating markdown files...", total=len(optimized_mapping))

        for original_path, optimized_path, referencing_files in optimized_mapping:
            original_name = original_path.name
            optimized_name = optimized_path.name

            # Skip if names are the same (already optimized, no markdown update needed)
            if original_name == optimized_name:
                progress.advance(task)
                continue

            for md_file in referencing_files:
                try:
                    content = md_file.read_text(encoding="utf-8")

                    # Check if this file references the image
                    if original_name not in content:
                        continue

                    new_content = content
                    changes_made = False

                    # Replace all occurrences of the image reference
                    # Handle various markdown image reference patterns

                    # 1. Patterns that already include uploads/
                    simple_patterns = [
                        (f"uploads/{original_name}", f"uploads/{optimized_name}"),
                        (f"./uploads/{original_name}", f"uploads/{optimized_name}"),
                        (f"/uploads/{original_name}", f"/uploads/{optimized_name}"),
                    ]

                    for old_pattern, new_pattern in simple_patterns:
                        if old_pattern in new_content:
                            new_content = new_content.replace(old_pattern, new_pattern)
                            changes_made = True

                    # 2. Wiki-style links with display names: [[link|name]] or ![[link|name]]
                    # Match ![[original_name|...]] or [[original_name|...]]
                    # and preserve the display name
                    wiki_with_name_pattern = (
                        r"(!?\[\[)" + re.escape(original_name) + r"\|([^\]]+)\]\]"
                    )
                    wiki_with_name_replacement = r"\1uploads/" + optimized_name + r"|\2]]"
                    if re.search(wiki_with_name_pattern, new_content):
                        new_content = re.sub(
                            wiki_with_name_pattern, wiki_with_name_replacement, new_content
                        )
                        changes_made = True

                    # 3. Obsidian wiki-style links without display names: ![[link]] or [[link]]
                    wiki_pattern = r"(!?\[\[)" + re.escape(original_name) + r"\]\]"
                    wiki_replacement = r"\1uploads/" + optimized_name + "]]"
                    if re.search(wiki_pattern, new_content):
                        new_content = re.sub(wiki_pattern, wiki_replacement, new_content)
                        changes_made = True

                    # 4. Standard markdown images without uploads/ prefix
                    if f"]({original_name})" in new_content:
                        new_content = new_content.replace(
                            f"]({original_name})", f"](uploads/{optimized_name})"
                        )
                        changes_made = True

                    if changes_made:
                        if dry_run:
                            console.print(
                                f"  [yellow]Would update:[/yellow] {md_file.name} "
                                f"({original_name} -> {optimized_name})"
                            )
                            updated_references += 1
                        else:
                            md_file.write_text(new_content, encoding="utf-8")
                            console.print(
                                f"  [green]Updated:[/green] {md_file.name} "
                                f"({original_name} -> {optimized_name})"
                            )
                            updated_references += 1
                            updated_files_set.add(md_file)

                except Exception as e:
                    console.print(f"  [red]✗[/red] Error updating {md_file}: {e}")

            progress.advance(task)

    console.print(
        f"\n[green]✓ Updated {updated_references} reference(s) in "
        f"{len(updated_files_set)} file(s)[/green]"
    )
    return len(updated_files_set), updated_references
