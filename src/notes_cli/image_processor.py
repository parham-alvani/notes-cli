"""Image processing and optimization functions."""

from pathlib import Path

from PIL import Image
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from .utils import TARGET_SIZE, calculate_image_hash, get_file_size

console = Console()


def is_already_optimized(image_path: Path) -> bool:
    """Check if an image is already optimized.

    An optimized image must be:
    - JPG format
    - Under 1MB
    - Has correct hash-based name

    Args:
        image_path: Path to the image file

    Returns:
        True if already optimized, False otherwise
    """
    # Must be a JPG file
    if image_path.suffix.lower() not in [".jpg", ".jpeg"]:
        return False

    # Must be under target size
    if get_file_size(image_path) > TARGET_SIZE:
        return False

    # Must follow the optimized naming pattern: {name}_{8-char-hex}.jpg
    name_parts = image_path.stem.split("_")
    if len(name_parts) < 2:
        return False

    # Extract the hash portion (last part after underscore)
    filename_hash = name_parts[-1]

    # Check if it looks like a hash (8 hexadecimal characters)
    if len(filename_hash) != 8 or not all(c in "0123456789abcdef" for c in filename_hash.lower()):
        return False

    # Calculate actual hash and verify it matches the filename
    actual_hash = calculate_image_hash(image_path)
    return actual_hash.lower() == filename_hash.lower()


def generate_optimized_name(image_path: Path, referencing_files: list[Path]) -> str:
    """Generate optimized image name based on the markdown file that references it.

    Uses content hash for deterministic, collision-free naming.

    Args:
        image_path: Path to the original image
        referencing_files: List of markdown files that reference this image

    Returns:
        String with the new optimized filename
    """
    if not referencing_files:
        # Fallback naming if no references found
        base_name = "optimized"
    else:
        # Use the first referencing file's name
        md_file = referencing_files[0]
        md_stem = md_file.stem
        # Remove whitespace
        base_name = md_stem.replace(" ", "")

    # Calculate content hash for unique identification
    content_hash = calculate_image_hash(image_path)

    return f"{base_name}_{content_hash}.jpg"


def convert_and_optimize(
    input_path: Path,
    output_path: Path,
    target_size: int = TARGET_SIZE,
    initial_quality: int = 95,
) -> bool:
    """Convert image to JPG and optimize to be under target size.

    Args:
        input_path: Path to input image
        output_path: Path to save optimized image
        target_size: Maximum file size in bytes
        initial_quality: Starting quality value (1-100)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open image
        with Image.open(input_path) as img:
            # Convert to RGB (required for JPG)
            if img.mode in ("RGBA", "LA", "P"):
                # Create white background for transparency
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Start with initial quality
            quality = initial_quality

            # Save with progressively lower quality until size is acceptable
            while quality > 10:
                img.save(output_path, "JPEG", quality=quality, optimize=True)

                current_size = get_file_size(output_path)

                if current_size <= target_size:
                    console.print(
                        f"  [green]✓[/green] Optimized: {input_path.name} -> "
                        f"{output_path.name} "
                        f"(Quality: {quality}, Size: {current_size / 1024:.1f} KB)"
                    )
                    return True

                # Reduce quality more aggressively as we get closer
                if current_size > target_size * 2:
                    quality -= 10
                elif current_size > target_size * 1.5:
                    quality -= 5
                else:
                    quality -= 3

            # Last attempt with minimum quality
            img.save(output_path, "JPEG", quality=10, optimize=True)
            final_size = get_file_size(output_path)

            if final_size <= target_size:
                console.print(
                    f"  [green]✓[/green] Optimized: {input_path.name} -> "
                    f"{output_path.name} "
                    f"(Quality: 10, Size: {final_size / 1024:.1f} KB)"
                )
            else:
                console.print(
                    f"  [yellow]⚠[/yellow] Warning: Could not reduce "
                    f"{input_path.name} below 1MB "
                    f"(Final size: {final_size / 1024:.1f} KB)"
                )
            return True

    except Exception as e:
        console.print(f"  [red]✗[/red] Error processing {input_path}: {e}")
        return False


def optimize_images(
    referenced_images_with_refs: list[tuple[Path, list[Path]]],
    uploads_dir: Path,
    dry_run: bool = False,
) -> list[tuple[Path, Path, list[Path]]]:
    """Optimize all referenced images, naming them after the markdown files.

    Args:
        referenced_images_with_refs: List of (image_path, referencing_files) tuples
        uploads_dir: Path to the uploads directory
        dry_run: If True, only show what would be done

    Returns:
        List of (original_path, optimized_path, referencing_files) tuples
    """
    from rich.panel import Panel

    console.print()
    console.print(Panel("📋 STEP 2: Optimizing referenced images", style="magenta bold"))

    if not referenced_images_with_refs:
        console.print("[yellow]No referenced images to optimize[/yellow]")
        return []

    console.print(f"[cyan]Processing {len(referenced_images_with_refs)} image(s)...[/cyan]\n")

    optimized_mapping: list[tuple[Path, Path, list[Path]]] = []
    skipped_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Processing images...", total=len(referenced_images_with_refs))

        for image_path, referencing_files in referenced_images_with_refs:
            # Show which markdown file(s) reference this image
            ref_names = [f.stem for f in referencing_files]
            ref_info = f"referenced by: {', '.join(ref_names)}"

            # FIRST: Check if already fully optimized (JPG + under 1MB + proper naming)
            if is_already_optimized(image_path):
                console.print(f"  [blue]✓ Already optimized:[/blue] {image_path.name} - skipping")
                # No mapping needed since the file is already in final state
                optimized_mapping.append((image_path, image_path, referencing_files))
                skipped_count += 1
                progress.advance(task)
                continue

            # Generate optimized filename based on referencing markdown file
            optimized_name = generate_optimized_name(image_path, referencing_files)
            optimized_path = image_path.parent / optimized_name

            # Get current size for reporting
            current_size = get_file_size(image_path)
            size_kb = current_size / 1024

            # Check if image is already under 1MB
            if current_size <= TARGET_SIZE:
                # Still need to convert to JPG for consistency
                if image_path.suffix.lower() not in [".jpg", ".jpeg"]:
                    if dry_run:
                        console.print(
                            f"  [yellow]Would convert:[/yellow] {image_path.name} -> "
                            f"{optimized_name} ({size_kb:.1f} KB, converting to JPG)"
                        )
                        optimized_mapping.append((image_path, optimized_path, referencing_files))
                    else:
                        console.print(
                            f"  Processing: {image_path.name} "
                            f"([cyan]{ref_info}[/cyan]) - converting to JPG"
                        )
                        if convert_and_optimize(image_path, optimized_path, initial_quality=95):
                            optimized_mapping.append(
                                (image_path, optimized_path, referencing_files)
                            )
                else:
                    # Already JPG and under 1MB, just needs proper naming
                    if image_path.name != optimized_name:
                        if dry_run:
                            console.print(
                                f"  [yellow]Would rename:[/yellow] {image_path.name} -> "
                                f"{optimized_name} ({size_kb:.1f} KB)"
                            )
                            optimized_mapping.append(
                                (image_path, optimized_path, referencing_files)
                            )
                        else:
                            image_path.rename(optimized_path)
                            console.print(
                                f"  [blue]Renamed:[/blue] {image_path.name} -> "
                                f"{optimized_name} ({size_kb:.1f} KB)"
                            )
                            optimized_mapping.append(
                                (image_path, optimized_path, referencing_files)
                            )
                    else:
                        # Perfect as-is
                        console.print(
                            f"  [blue]✓ No changes needed:[/blue] {image_path.name} "
                            f"({size_kb:.1f} KB)"
                        )
                        optimized_mapping.append((image_path, image_path, referencing_files))

                progress.advance(task)
                continue

            # Image is over 1MB - needs optimization
            if dry_run:
                console.print(
                    f"  [yellow]Would optimize:[/yellow] {image_path.name} -> "
                    f"{optimized_name} ({size_kb:.1f} KB)"
                )
                console.print(f"    [cyan]{ref_info}[/cyan]")
                optimized_mapping.append((image_path, optimized_path, referencing_files))
            else:
                console.print(f"  Processing: {image_path.name} ([cyan]{ref_info}[/cyan])")
                if convert_and_optimize(image_path, optimized_path):
                    optimized_mapping.append((image_path, optimized_path, referencing_files))

            progress.advance(task)

    if skipped_count > 0:
        console.print(f"\n[blue]↺ Skipped {skipped_count} already-optimized image(s)[/blue]")
    console.print(f"[green]✓ Processed {len(optimized_mapping)} image(s) total[/green]")
    return optimized_mapping


def remove_original_images(
    optimized_mapping: list[tuple[Path, Path, list[Path]]],
    keep_originals: bool = False,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Remove original images after optimization.

    Args:
        optimized_mapping: List of (original_path, optimized_path, referencing_files) tuples
        keep_originals: If True, keep original images
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (removed_count, freed_space)
    """
    from rich.panel import Panel

    console.print()
    console.print(Panel("📋 STEP 4: Removing original images", style="magenta bold"))

    if keep_originals:
        console.print("[yellow]Keeping original images (--keep-originals flag set)[/yellow]")
        return 0, 0

    removed_count = 0
    freed_space = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Removing original images...", total=len(optimized_mapping))

        for original_path, optimized_path, _ in optimized_mapping:
            # Only remove if original is different from optimized and both exist
            # (Don't remove if they're the same file - meaning it was already optimized)
            if (
                original_path != optimized_path
                and original_path.exists()
                and optimized_path.exists()
            ):
                size = get_file_size(original_path)
                freed_space += size

                if dry_run:
                    console.print(f"  [yellow]Would remove:[/yellow] {original_path.name}")
                else:
                    original_path.unlink()
                    console.print(f"  [red]Removed:[/red] {original_path.name}")
                    removed_count += 1

            progress.advance(task)

    freed_mb = freed_space / (1024 * 1024)

    if dry_run:
        console.print(
            f"\n[yellow]Would remove {len(optimized_mapping)} original image(s), "
            f"freeing ~{freed_mb:.1f} MB[/yellow]"
        )
    else:
        console.print(
            f"\n[green]✓ Removed {removed_count} original image(s), "
            f"freed ~{freed_mb:.1f} MB[/green]"
        )

    return removed_count, freed_space
