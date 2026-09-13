import random

import pytest

from dungy.dungeon import (
    CHARACTER_TILES,
    DungeonGenerator,
    build_rooms,
    connect_rooms,
    corridor_between_points,
    create_level,
    generate_room,
    join_rooms,
    paint_corridors,
    paint_rooms,
    paint_walls,
    render_level,
    room_overlapping,
)


@pytest.fixture
def rng():
    return random.Random(0)


@pytest.fixture
def gen(rng):
    return DungeonGenerator(width=32, height=24, max_rooms=5, rng=rng)


def test_character_tiles():
    assert CHARACTER_TILES == {"stone": " ", "floor": ".", "wall": "#"}


def test_create_level_dimensions():
    level = create_level(32, 24)

    assert len(level) == 24
    assert all(len(row) == 32 for row in level)
    assert all(tile == "stone" for row in level for tile in row)


def test_generate_room_stays_in_bounds(rng):
    for _ in range(50):
        x, y, w, h = generate_room(rng, 32, 24, 5, 10)

        assert 5 <= w <= 10
        assert 5 <= h <= 10
        assert 1 <= x and x + w <= 31
        assert 1 <= y and y + h <= 23


def test_room_overlapping_true():
    assert room_overlapping([2, 2, 4, 4], [[1, 1, 5, 5]]) is True


def test_room_overlapping_false():
    assert room_overlapping([10, 10, 2, 2], [[1, 1, 3, 3]]) is False


def test_corridor_between_points_straight():
    assert corridor_between_points(random.Random(0), 32, 24, 1, 1, 5, 1) == [
        (1, 1),
        (5, 1),
    ]


def test_corridor_between_points_unknown_join_type():
    with pytest.raises(ValueError, match="unknown join_type"):
        corridor_between_points(random.Random(0), 32, 24, 1, 1, 5, 3, join_type="diagonal")


def test_join_rooms_returns_corridor(rng):
    corridor = join_rooms(rng, 32, 24, [1, 1, 4, 4], [10, 1, 4, 4])

    assert len(corridor) >= 2


def test_build_rooms_returns_bounded_room_list(rng):
    room_list = build_rooms(rng, 32, 24, 5, 5, 10)

    assert 1 <= len(room_list) <= 5


def test_connect_rooms_returns_corridors(rng):
    room_list = build_rooms(rng, 32, 24, 5, 5, 10)
    corridor_list = connect_rooms(rng, 32, 24, room_list, 1, 3)

    assert len(corridor_list) >= 1


def test_painting_makes_floor_and_wall(rng):
    level = create_level(32, 24)
    room_list = build_rooms(rng, 32, 24, 5, 5, 10)
    corridor_list = connect_rooms(rng, 32, 24, room_list, 1, 3)

    paint_rooms(level, room_list)
    paint_corridors(level, corridor_list)
    paint_walls(level)

    tiles = [tile for row in level for tile in row]
    assert "floor" in tiles
    assert "wall" in tiles


def test_render_level_maps_tiles():
    rows = render_level([["floor", "wall"], ["stone", "floor"]])

    assert rows == [".#", " ."]


def test_generate_dimensions(gen):
    level = gen.generate()

    assert len(level) == 24
    assert all(len(row) == 32 for row in level)


def test_generate_draws_floor_and_wall(gen):
    gen.generate()

    tiles = [tile for row in gen.level for tile in row]
    assert "floor" in tiles
    assert "wall" in tiles


def test_generate_twice_resets_level(gen):
    gen.generate()
    first_level = gen.level

    gen.generate()

    assert len(gen.level) == 24
    assert gen.level is not first_level


def test_render_returns_rows(gen):
    gen.generate()
    rows = gen.render()

    assert len(rows) == 24
    assert all(len(row) == 32 for row in rows)
    assert set("".join(rows)) <= set(CHARACTER_TILES.values())
    assert gen.tiles_level is rows


def test_render_does_not_print(gen, capsys):
    gen.generate()
    gen.render()

    assert capsys.readouterr().out == ""


def test_dungeon_generator_custom_tiles(gen):
    gen.generate()
    rows = gen.render(tiles={"stone": "s", "floor": "f", "wall": "w"})

    assert set("".join(rows)) <= {"s", "f", "w"}
