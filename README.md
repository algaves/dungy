# dungy

A small, dependency-free dungeon generator written in Python.

`DungeonGenerator` builds a rectangular level of non-overlapping rooms
connected by corridors, then paints walls around the floor tiles and renders
the result as ASCII text.

## Requirements

- CPython 3.8 or newer, or PyPy 3.8 or newer.
- The package is pure Python and has no runtime dependencies.

The vendored `dungeon.py` is a CC0 implementation by James Spencer; keep its
license header intact. The machine-readable citation lives in `references.bib`
and is shipped with the package distribution.

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
from dungy.dungeon import DungeonGenerator

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
uv run mypy src         # type-check against Python 3.8
uv run pytest           # unit tests
uv run mkdocs serve     # preview docs at http://127.0.0.1:8000
```

Build the static documentation site with `uv run mkdocs build` (output in
`site/`).

### Testing on PyPy 3.8

```bash
uv venv --python pypy@3.8 .venv-pypy
uv pip install --python .venv-pypy/bin/python -e . pytest
.venv-pypy/bin/python -m pytest
```

## References

The level-generation algorithm in `src/dungy/dungeon.py` is adapted from
James Spencer's CC0-licensed dungeon generator:

> James Spencer, "A simple dungeon generator for Python 2 or 3", RogueBasin,
> 2017-09-02.
> https://www.roguebasin.com/index.php/A_Simple_Dungeon_Generator_for_Python_2_or_3

The BibTeX entry is in `references.bib` at the repository root; the package
ships it in the distribution.

## License

The dungeon generator is released under CC0. See the header in
`src/dungy/dungeon.py`.
