# dungy

A small, dependency-free dungeon generator written in Python.

`DungeonGenerator` builds a rectangular level of non-overlapping rooms
connected by corridors, then paints walls around the floor tiles and renders
the result as ASCII text.

## Requirements

- CPython 3.8 or newer, or PyPy 3.8 or newer.
- The package is pure Python and has no runtime dependencies.

## Setup

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync            # create the venv and install the package + dev tools
```

Without uv:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Usage

Run the bundled demo, which prints the room/corridor lists and the level map:

```bash
uv run python src/dungy/dungeon.py
```

Use it as a library:

```python
from dungy import DungeonGenerator

gen = DungeonGenerator(width=64, height=64, max_rooms=15)
gen.generate()
for row in gen.render():
    print(row)
```

Output is nondeterministic by default; pass a seeded `random.Random` to the
constructor for reproducible levels (`DungeonGenerator(rng=random.Random(0))`).

## Development

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy src         # type-check
uv run pytest           # tests
uv run mkdocs serve     # preview docs at http://127.0.0.1:8000
```

Build the static docs site with `uv run mkdocs build` (output in `site/`).

### Testing on PyPy 3.8

```bash
uv venv --python pypy@3.8 .venv-pypy
uv pip install --python .venv-pypy/bin/python -e . pytest
.venv-pypy/bin/python -m pytest
```

## License

The dungeon generator is released under CC0. See the header in
`src/dungy/dungeon.py`.
