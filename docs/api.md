# API

## `dungy.dungeon.DungeonGenerator`

```python
DungeonGenerator(
    width=64,
    height=64,
    max_rooms=15,
    min_room_xy=5,
    max_room_xy=10,
    rooms_overlap=False,
    random_connections=1,
    random_spurs=3,
    tiles=CHARACTER_TILES,
    rng=None,
)
```

| Method | Description |
| --- | --- |
| `generate()` | Build rooms, corridors, floors and walls; returns the raw grid and stores it in `level`. |
| `render(tiles=None)` | Convert `level` to displayable strings using `tiles` (default `CHARACTER_TILES`); returns them and stores them in `tiles_level`. |

After `generate()` the raw grid is in `gen.level` (`stone`/`floor`/`wall`) and
the room/corridor geometry in `gen.room_list` / `gen.corridor_list`;
`render()` writes displayable strings to `gen.tiles_level`.

`generate()` and `render()` never print — rendering to the console is the
caller's job.

## Module-level functions

`dungy.dungeon` also exposes the reusable building blocks behind the class:

| Function | Description |
| --- | --- |
| `create_level(width, height)` | A fresh `stone`-filled grid. |
| `room_overlapping(room, room_list)` | Detect overlap against existing rooms. |
| `generate_room(rng, width, height, min_room_xy, max_room_xy)` | Pick a random room rectangle `[x, y, w, h]`. |
| `corridor_between_points(rng, width, height, x1, y1, x2, y2, join_type='either')` | Corridor path between two points. |
| `join_rooms(rng, width, height, room_1, room_2, join_type='either')` | Connect two rooms; returns the corridor. |
| `build_rooms(rng, width, height, max_rooms, min_room_xy, max_room_xy, rooms_overlap=False)` | Build a list of non-overlapping rooms. |
| `connect_rooms(rng, width, height, room_list, random_connections, random_spurs)` | Build the corridors joining all rooms. |
| `paint_rooms(level, room_list)` | Paint room floors onto the grid. |
| `paint_corridors(level, corridor_list)` | Paint corridor floors onto the grid. |
| `paint_walls(level)` | Surround floors with walls. |
| `render_level(level, tiles=CHARACTER_TILES)` | Render the raw grid to displayable strings. |

## Reproducibility

The class and every `rng`-taking function accept a `random.Random` instance.
Pass a seeded one for reproducible output:

```python
import random
from dungy.dungeon import DungeonGenerator

gen = DungeonGenerator(width=64, height=64, max_rooms=15, rng=random.Random(0))
gen.generate()
print(*gen.render(), sep="\n")
```

Without one, the generator creates its own unseeded `random.Random`, so output
is nondeterministic.