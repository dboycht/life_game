# -*- coding: utf-8 -*-
"""预设图案库。ASCII 定义：'O' 为生、'.' 为死。"""

PATTERNS = {
    "滑翔机": """\
.O.
..O
OOO
""",
    "轻型飞船 LWSS": """\
.O..O
O....
O...O
OOOO.
""",
    "脉冲星": """\
..OOO...OOO..
.............
O....O.O....O
O....O.O....O
O....O.O....O
..OOO...OOO..
.............
..OOO...OOO..
O....O.O....O
O....O.O....O
O....O.O....O
.............
..OOO...OOO..
""",
    "R-五连块": """\
.OO
OO.
.O.
""",
    "高斯帕滑翔机枪": """\
........................O...........
......................O.O...........
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO..............
OO........O...O.OO....O.O...........
..........O.....O.......O...........
...........O...O....................
............OO......................
""",
}


def parse(text: str):
    """ASCII 图案 → ([(x, y), ...], 宽, 高)，坐标从图案左上角 (0, 0) 起。"""
    rows = [line for line in text.splitlines() if line.strip()]
    coords = []
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            if ch == "O":
                coords.append((x, y))
    return coords, max(len(r) for r in rows), len(rows)


def names():
    """全部图案名，按定义顺序。"""
    return list(PATTERNS)


def coords_of(name: str):
    """取指定图案 → ([(x, y), ...], 宽, 高)。"""
    return parse(PATTERNS[name])
