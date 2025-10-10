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

# run django tests
test *args: sync
    uv run coverage run manage.py test {{ args }}
    uv run coverage report

# install all dependencies
sync:
    uv sync --all-groups

# upgrade all dependencies
upgrade:
    uv sync --all-groups -U

# run ruff and mypy (with --fix)
lint: sync mypy ruff-format (ruff-check "--fix")
