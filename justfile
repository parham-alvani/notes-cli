default:
    @just --list

# run mypy
[group('lint')]
[private]
mypy:
    uv run mypy .

# run ruff format
[group('lint')]
[private]
ruff-format *args:
    uv run ruff format {{ args }}

# run ruff check
[group('lint')]
[private]
ruff-check *args:
    uv run ruff check --preview {{ args }}

# run tests
test *args: sync
    uv run pytest {{ args }}

# install all dependencies
sync:
    uv sync --all-groups

# upgrade all dependencies
upgrade:
    uv sync --all-groups -U

# run ruff and mypy (with --fix)
lint: sync mypy ruff-format (ruff-check "--fix")
