#!/usr/bin/env python

# Adapted from James Spencer's "generator-1.py" (see references.bib).

# generator-1.py, a simple python dungeon generator by
# James Spencer <jamessp [at] gmail.com>.

# To the extent possible under law, the person who associated CC0 with
# pathfinder.py has waived all copyright and related or neighboring rights
# to pathfinder.py.

# You should have received a copy of the CC0 legalcode along with this
# work. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from __future__ import annotations

import random
from typing import TYPE_CHECKING, NamedTuple, NoReturn

CHARACTER_TILES: dict[str, str] = {"stone": " ", "floor": ".", "wall": "#"}

if TYPE_CHECKING:
    from typing import List, Tuple

    Point = Tuple[int, int]
    Corridor = List[Point]


class Room(NamedTuple):
    x: int
    y: int
    w: int
    h: int


def _validate_room_size(
    width: int,
    height: int,
    min_room_xy: int,
    max_room_xy: int,
) -> None:
    if min_room_xy < 1:
        message = "min_room_xy must be >= 1"
        raise ValueError(message)
    if max_room_xy < min_room_xy:
        message = "max_room_xy must be >= min_room_xy"
        raise ValueError(message)
    if width < max_room_xy + 2 or height < max_room_xy + 2:
        message = "width and height must be >= max_room_xy + 2 so rooms fit inside the border"
        raise ValueError(message)


def _validate_config(
    width: int,
    height: int,
    max_rooms: int,
    min_room_xy: int,
    max_room_xy: int,
    random_connections: int,
    random_spurs: int,
) -> None:
    _validate_room_size(width, height, min_room_xy, max_room_xy)
    if max_rooms < 1:
        message = "max_rooms must be >= 1"
        raise ValueError(message)
    if random_connections < 0:
        message = "random_connections must be >= 0"
        raise ValueError(message)
    if random_spurs < 0:
        message = "random_spurs must be >= 0"
        raise ValueError(message)
    if random_spurs > 0 and (width < 4 or height < 4):
        message = "random spurs need width and height >= 4"
        raise ValueError(message)


def _unknown_join_type(join_type: str) -> NoReturn:
    message = f"unknown join_type: {join_type!r}"
    raise ValueError(message)


def create_level(width: int, height: int) -> list[list[str]]:
    return [["stone"] * width for _ in range(height)]


def room_overlapping(room: Room, room_list: list[Room]) -> bool:
    x, y, w, h = room
    return any(
        x < (current_room.x + current_room.w)
        and current_room.x < (x + w)
        and y < (current_room.y + current_room.h)
        and current_room.y < (y + h)
        for current_room in room_list
    )


def generate_room(
    rng: random.Random,
    width: int,
    height: int,
    min_room_xy: int,
    max_room_xy: int,
) -> Room:
    _validate_room_size(width, height, min_room_xy, max_room_xy)
    w = rng.randint(min_room_xy, max_room_xy)
    h = rng.randint(min_room_xy, max_room_xy)
    x = rng.randint(1, width - w - 1)
    y = rng.randint(1, height - h - 1)
    return Room(x, y, w, h)


def corridor_between_points(
    rng: random.Random,
    width: int,
    height: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    join_type: str = "either",
) -> Corridor:
    if x1 == x2 or y1 == y2:
        return [(x1, y1), (x2, y2)]

    if join_type == "either":
        if {0, 1}.intersection({x1, x2, y1, y2}):
            join = "bottom"
        elif {width - 1, width - 2}.intersection({x1, x2}) or {
            height - 1,
            height - 2,
        }.intersection({y1, y2}):
            join = "top"
        else:
            join = rng.choice(["top", "bottom"])
    else:
        join = join_type

    if join == "top":
        return [(x1, y1), (x1, y2), (x2, y2)]
    if join == "bottom":
        return [(x1, y1), (x2, y1), (x2, y2)]

    _unknown_join_type(join_type)


def join_rooms(
    rng: random.Random,
    width: int,
    height: int,
    room_1: Room,
    room_2: Room,
    join_type: str = "either",
) -> Corridor:
    sorted_rooms = [room_1, room_2]
    sorted_rooms.sort(key=lambda room: room.x)

    x1, y1, w1, h1 = sorted_rooms[0]
    x1_2 = x1 + w1 - 1
    y1_2 = y1 + h1 - 1

    x2, y2, w2, h2 = sorted_rooms[1]
    x2_2 = x2 + w2 - 1
    y2_2 = y2 + h2 - 1

    if x1 < (x2 + w2) and x2 < (x1 + w1):
        jx1 = rng.randint(x2, x1_2)
        jx2 = jx1
        tmp_y = [y1, y2, y1_2, y2_2]
        tmp_y.sort()
        jy1 = tmp_y[1] + 1
        jy2 = tmp_y[2] - 1
        return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2)

    if y1 < (y2 + h2) and y2 < (y1 + h1):
        if y2 > y1:
            jy1 = rng.randint(y2, y1_2)
            jy2 = jy1
        else:
            jy1 = rng.randint(y1, y2_2)
            jy2 = jy1
        tmp_x = [x1, x2, x1_2, x2_2]
        tmp_x.sort()
        jx1 = tmp_x[1] + 1
        jx2 = tmp_x[2] - 1
        return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2)

    join = rng.choice(["top", "bottom"]) if join_type == "either" else join_type

    if join == "top":
        if y2 > y1:
            jx1 = x1_2 + 1
            jy1 = rng.randint(y1, y1_2)
            jx2 = rng.randint(x2, x2_2)
            jy2 = y2 - 1
            return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2, "bottom")
        jx1 = rng.randint(x1, x1_2)
        jy1 = y1 - 1
        jx2 = x2 - 1
        jy2 = rng.randint(y2, y2_2)
        return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2, "top")

    if join == "bottom":
        if y2 > y1:
            jx1 = rng.randint(x1, x1_2)
            jy1 = y1_2 + 1
            jx2 = x2 - 1
            jy2 = rng.randint(y2, y2_2)
            return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2, "top")
        jx1 = x1_2 + 1
        jy1 = rng.randint(y1, y1_2)
        jx2 = rng.randint(x2, x2_2)
        jy2 = y2_2 + 1
        return corridor_between_points(rng, width, height, jx1, jy1, jx2, jy2, "bottom")

    _unknown_join_type(join_type)


def build_rooms(
    rng: random.Random,
    width: int,
    height: int,
    max_rooms: int,
    min_room_xy: int,
    max_room_xy: int,
    rooms_overlap: bool = False,
) -> list[Room]:
    room_list: list[Room] = []
    max_iters = max_rooms * 5

    for _ in range(max_iters):
        tmp_room = generate_room(rng, width, height, min_room_xy, max_room_xy)

        if rooms_overlap or not room_list:
            room_list.append(tmp_room)
        else:
            tmp_room = generate_room(rng, width, height, min_room_xy, max_room_xy)
            if not room_overlapping(tmp_room, room_list):
                room_list.append(tmp_room)

        if len(room_list) >= max_rooms:
            break

    return room_list


def connect_rooms(
    rng: random.Random,
    width: int,
    height: int,
    room_list: list[Room],
    random_connections: int,
    random_spurs: int,
) -> list[Corridor]:
    if not room_list:
        return []

    corridor_list: list[Corridor] = [
        join_rooms(rng, width, height, room_list[a], room_list[a + 1])
        for a in range(len(room_list) - 1)
    ]

    for _ in range(random_connections):
        room_1 = rng.choice(room_list)
        room_2 = rng.choice(room_list)
        corridor_list.append(join_rooms(rng, width, height, room_1, room_2))

    for _ in range(random_spurs):
        spur = Room(rng.randint(2, width - 2), rng.randint(2, height - 2), 1, 1)
        target = rng.choice(room_list)
        corridor_list.append(join_rooms(rng, width, height, spur, target))

    return corridor_list


def paint_rooms(level: list[list[str]], room_list: list[Room]) -> None:
    for room in room_list:
        for dx in range(room.w):
            for dy in range(room.h):
                level[room.y + dy][room.x + dx] = "floor"


def paint_corridors(
    level: list[list[str]],
    corridor_list: list[Corridor],
) -> None:
    for corridor in corridor_list:
        x1, y1 = corridor[0]
        x2, y2 = corridor[1]
        for dx in range(abs(x1 - x2) + 1):
            for dy in range(abs(y1 - y2) + 1):
                level[min(y1, y2) + dy][min(x1, x2) + dx] = "floor"

        if len(corridor) == 3:
            x3, y3 = corridor[2]
            for dx in range(abs(x2 - x3) + 1):
                for dy in range(abs(y2 - y3) + 1):
                    level[min(y2, y3) + dy][min(x2, x3) + dx] = "floor"


def paint_walls(level: list[list[str]]) -> None:
    for row in range(1, len(level) - 1):
        for col in range(1, len(level[row]) - 1):
            if level[row][col] == "floor":
                if level[row - 1][col - 1] == "stone":
                    level[row - 1][col - 1] = "wall"
                if level[row - 1][col] == "stone":
                    level[row - 1][col] = "wall"
                if level[row - 1][col + 1] == "stone":
                    level[row - 1][col + 1] = "wall"
                if level[row][col - 1] == "stone":
                    level[row][col - 1] = "wall"
                if level[row][col + 1] == "stone":
                    level[row][col + 1] = "wall"
                if level[row + 1][col - 1] == "stone":
                    level[row + 1][col - 1] = "wall"
                if level[row + 1][col] == "stone":
                    level[row + 1][col] = "wall"
                if level[row + 1][col + 1] == "stone":
                    level[row + 1][col + 1] = "wall"


def render_level(
    level: list[list[str]],
    tiles: dict[str, str] = CHARACTER_TILES,
) -> list[str]:
    return ["".join(tiles[tile] for tile in row) for row in level]


class DungeonGenerator:
    def __init__(
        self,
        width: int = 64,
        height: int = 64,
        max_rooms: int = 15,
        min_room_xy: int = 5,
        max_room_xy: int = 10,
        rooms_overlap: bool = False,
        random_connections: int = 1,
        random_spurs: int = 3,
        tiles: dict[str, str] = CHARACTER_TILES,
        rng: random.Random | None = None,
    ) -> None:
        _validate_config(
            width,
            height,
            max_rooms,
            min_room_xy,
            max_room_xy,
            random_connections,
            random_spurs,
        )
        self.width: int = width
        self.height: int = height
        self.max_rooms: int = max_rooms
        self.min_room_xy: int = min_room_xy
        self.max_room_xy: int = max_room_xy
        self.rooms_overlap: bool = rooms_overlap
        self.random_connections: int = random_connections
        self.random_spurs: int = random_spurs
        self.tiles: dict[str, str] = dict(tiles)
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.level: list[list[str]] = []
        self.room_list: list[Room] = []
        self.corridor_list: list[Corridor] = []
        self.tiles_level: list[str] = []

    def generate(self) -> list[list[str]]:
        self.level = create_level(self.width, self.height)
        self.room_list = build_rooms(
            self.rng,
            self.width,
            self.height,
            self.max_rooms,
            self.min_room_xy,
            self.max_room_xy,
            self.rooms_overlap,
        )
        self.corridor_list = connect_rooms(
            self.rng,
            self.width,
            self.height,
            self.room_list,
            self.random_connections,
            self.random_spurs,
        )
        paint_rooms(self.level, self.room_list)
        paint_corridors(self.level, self.corridor_list)
        paint_walls(self.level)
        return self.level

    def render(self, tiles: dict[str, str] | None = None) -> list[str]:
        self.tiles_level = render_level(self.level, tiles if tiles is not None else self.tiles)
        return self.tiles_level


if __name__ == "__main__":
    generator = DungeonGenerator()
    generator.generate()
    generator.render()
    print("Room List: ", generator.room_list)
    print("\nCorridor List: ", generator.corridor_list)
    for row in generator.tiles_level:
        print(row)
