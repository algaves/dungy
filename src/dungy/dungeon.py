#!/usr/bin/env python

# generator-1.py, a simple python dungeon generator by
# James Spencer <jamessp [at] gmail.com>.

# To the extent possible under law, the person who associated CC0 with
# pathfinder.py has waived all copyright and related or neighboring rights
# to pathfinder.py.

# You should have received a copy of the CC0 legalcode along with this
# work. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from __future__ import annotations

import random

CHARACTER_TILES: dict[str, str] = {"stone": " ", "floor": ".", "wall": "#"}


def create_level(width: int, height: int) -> list[list[str]]:
    return [["stone"] * width for _ in range(height)]


def room_overlapping(room: list[int], room_list: list[list[int]]) -> bool:
    x, y, w, h = room
    return any(
        x < (current_room[0] + current_room[2])
        and current_room[0] < (x + w)
        and y < (current_room[1] + current_room[3])
        and current_room[1] < (y + h)
        for current_room in room_list
    )


def generate_room(
    rng: random.Random,
    width: int,
    height: int,
    min_room_xy: int,
    max_room_xy: int,
) -> list[int]:
    w = rng.randint(min_room_xy, max_room_xy)
    h = rng.randint(min_room_xy, max_room_xy)
    x = rng.randint(1, width - w - 1)
    y = rng.randint(1, height - h - 1)
    return [x, y, w, h]


def corridor_between_points(
    rng: random.Random,
    width: int,
    height: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    join_type: str = "either",
) -> list[tuple[int, int]]:
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

    message = f"unknown join_type: {join_type!r}"
    raise ValueError(message)


def join_rooms(
    rng: random.Random,
    width: int,
    height: int,
    room_1: list[int],
    room_2: list[int],
    join_type: str = "either",
) -> list[tuple[int, int]]:
    sorted_rooms = [room_1, room_2]
    sorted_rooms.sort(key=lambda room: room[0])

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

    message = f"unknown join_type: {join_type!r}"
    raise ValueError(message)


def build_rooms(
    rng: random.Random,
    width: int,
    height: int,
    max_rooms: int,
    min_room_xy: int,
    max_room_xy: int,
    rooms_overlap: bool = False,
) -> list[list[int]]:
    room_list: list[list[int]] = []
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
    room_list: list[list[int]],
    random_connections: int,
    random_spurs: int,
) -> list[list[tuple[int, int]]]:
    corridor_list: list[list[tuple[int, int]]] = [
        join_rooms(rng, width, height, room_list[a], room_list[a + 1])
        for a in range(len(room_list) - 1)
    ]

    for _ in range(random_connections):
        room_1 = rng.choice(room_list)
        room_2 = rng.choice(room_list)
        corridor_list.append(join_rooms(rng, width, height, room_1, room_2))

    for _ in range(random_spurs):
        spur = [rng.randint(2, width - 2), rng.randint(2, height - 2), 1, 1]
        target = rng.choice(room_list)
        corridor_list.append(join_rooms(rng, width, height, spur, target))

    return corridor_list


def paint_rooms(level: list[list[str]], room_list: list[list[int]]) -> None:
    for room in room_list:
        for width in range(room[2]):
            for height in range(room[3]):
                level[room[1] + height][room[0] + width] = "floor"


def paint_corridors(
    level: list[list[str]],
    corridor_list: list[list[tuple[int, int]]],
) -> None:
    for corridor in corridor_list:
        x1, y1 = corridor[0]
        x2, y2 = corridor[1]
        for width in range(abs(x1 - x2) + 1):
            for height in range(abs(y1 - y2) + 1):
                level[min(y1, y2) + height][min(x1, x2) + width] = "floor"

        if len(corridor) == 3:
            x3, y3 = corridor[2]
            for width in range(abs(x2 - x3) + 1):
                for height in range(abs(y2 - y3) + 1):
                    level[min(y2, y3) + height][min(x2, x3) + width] = "floor"


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
        self.width: int = width
        self.height: int = height
        self.max_rooms: int = max_rooms
        self.min_room_xy: int = min_room_xy
        self.max_room_xy: int = max_room_xy
        self.rooms_overlap: bool = rooms_overlap
        self.random_connections: int = random_connections
        self.random_spurs: int = random_spurs
        self.tiles: dict[str, str] = tiles
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.level: list[list[str]] = []
        self.room_list: list[list[int]] = []
        self.corridor_list: list[list[tuple[int, int]]] = []
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
