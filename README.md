<div align="center">
   <h1>Notes CLI</h1>
   <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/parham-alvani/notes-cli/test.yaml?style=for-the-badge&logo=github">
</div>

## Introduction

A command-line tool for cleaning up and optimizing images in markdown notes.

## Features

- **Remove Unreferenced Images**: Automatically deletes images in the `uploads` folder that are not referenced in any markdown file
- **Optimize Images**: Converts images to JPG format and compresses them to be under `1MB` while maintaining quality
- **Update References**: Automatically updates markdown files to reference the optimized images
- **Smart Naming**: Names optimized images based on the markdown file that references them, with content-based hashing to prevent collisions
- **Dry Run Mode**: Preview changes before applying them

## Installation

Using `uv`:

```bash
uv sync
```

For development (includes `mypy` and `ruff`):

```bash
uv sync --all-groups
```

## Usage

Basic usage (processes images in `uploads/` directory):

```bash
notes-cli
```

Specify a different directory:

```bash
notes-cli path/to/images
```

Preview changes without applying them:

```bash
notes-cli --dry-run
```

Keep original images after optimization:

```bash
notes-cli --keep-originals
```

## How It Works

1. **Step 1**: Scans for unreferenced images and removes them (saves disk space)
2. **Step 2**: Optimizes referenced images:
   - Converts to JPG format
   - Compresses to under `1MB`
   - Renames based on referencing markdown file with content hash
3. **Step 3**: Updates markdown files to use the optimized image names
4. **Step 4**: Removes original images (unless `--keep-originals` is specified)

## Development

### Type Checking

Run `mypy` for type checking:

```bash
mypy src/notes_cli
```

### Linting

Run ruff for linting:

```bash
ruff check src/notes_cli
```

### Formatting

Format code with ruff:

```bash
ruff format src/notes_cli
```
