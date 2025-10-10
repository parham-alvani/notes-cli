"""Utility functions for file operations and hash calculations."""

import hashlib
import os
from pathlib import Path

# Supported image formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".tif"}

# Target size in bytes (1MB)
TARGET_SIZE = 1 * 1024 * 1024


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes.

    Args:
        filepath: Path to the file

    Returns:
        File size in bytes
    """
    return os.path.getsize(filepath)


def calculate_image_hash(filepath: Path, hash_length: int = 8) -> str:
    """Calculate hash of image file content.

    Args:
        filepath: Path to the image file
        hash_length: Number of characters to use from hash (default: 8)

    Returns:
        String with first hash_length characters of MD5 hash
    """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()[:hash_length]


def find_all_images(directory: Path) -> list[Path]:
    """Find all image files in the directory.

    Args:
        directory: Directory to search for images

    Returns:
        Sorted list of image file paths
    """
    image_files: list[Path] = []

    for ext in SUPPORTED_FORMATS:
        image_files.extend(directory.glob(f"*{ext}"))
        image_files.extend(directory.glob(f"*{ext.upper()}"))

    return sorted(image_files)


def find_all_markdown_files(root_dir: Path = Path(".")) -> list[Path]:
    """Find all markdown files in the directory tree.

    Args:
        root_dir: Root directory to search (default: current directory)

    Returns:
        List of markdown file paths
    """
    root_path = Path(root_dir)
    return list(root_path.rglob("*.md"))
