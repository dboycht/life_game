# -*- coding: utf-8 -*-
"""生命游戏引擎：环面棋盘、标准康威规则（B3/S23）、整代同步更新。

坐标口径：x 向右、y 向下，均从 0 起；出界按取模绕回对侧（环面）。
邻域口径：8 邻域存活数，**不含自身**（修正旧版 get_per_sum 含自身的偏移）。
"""

import random


class Grid:
    """生命棋盘。cells[y][x] ∈ {0, 1}，0 为死、1 为生。"""

    def __init__(self, width: int, height: int):
        if int(width) <= 0 or int(height) <= 0:
            raise ValueError("棋盘横纵长度必须为正整数")
        self.width = int(width)
        self.height = int(height)
        self.cells = [[0] * self.width for _ in range(self.height)]

    # ---- 基础读写 ------------------------------------------------------

    def get(self, x: int, y: int) -> int:
        """取格子值，坐标按环面取模。"""
        return self.cells[y % self.height][x % self.width]

    def set(self, x: int, y: int, value: int = 1) -> None:
        """置格子值，坐标按环面取模。"""
        self.cells[y % self.height][x % self.width] = 1 if value else 0

    def alive_coords(self):
        """全部存活坐标 [(x, y), ...]。"""
        return [(x, y) for y in range(self.height) for x in range(self.width) if self.cells[y][x]]

    def alive_count(self) -> int:
        return sum(sum(row) for row in self.cells)

    def clear(self) -> None:
        for row in self.cells:
            for x in range(self.width):
                row[x] = 0

    # ---- 规则 ----------------------------------------------------------

    def neighbors(self, x: int, y: int) -> int:
        """(x, y) 的 8 邻域存活数；环面取模，不含自身。"""
        total = 0
        for dy in (-1, 0, 1):
            row = self.cells[(y + dy) % self.height]
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                total += row[(x + dx) % self.width]
        return total

    def step(self) -> None:
        """演化一代：新一代全部由旧代算出（整代同步，不边算边改）。"""
        h, w = self.height, self.width
        cells = self.cells
        new = []
        for y in range(h):
            up = cells[(y - 1) % h]
            row = cells[y]
            down = cells[(y + 1) % h]
            new_row = [0] * w
            for x in range(w):
                left = (x - 1) % w
                right = (x + 1) % w
                n = (up[left] + up[x] + up[right] +
                     row[left] + row[right] +
                     down[left] + down[x] + down[right])
                if row[x]:
                    new_row[x] = 1 if n in (2, 3) else 0
                elif n == 3:
                    new_row[x] = 1
            new.append(new_row)
        self.cells = new

    # ---- 布阵 ----------------------------------------------------------

    def place(self, coords, ox: int = 0, oy: int = 0) -> None:
        """按坐标布阵，出界自动绕回对侧（环面）。"""
        for px, py in coords:
            self.set(ox + px, oy + py, 1)

    def randomize(self, count: int) -> None:
        """随机播种：不放回抽样，生命数精确等于 count、坐标不重叠。"""
        total = self.width * self.height
        count = int(count)
        if count < 0 or count > total:
            raise ValueError(f"生命个数须在 0 ~ {total} 之间")
        self.clear()
        for flat in random.sample(range(total), count):
            self.set(flat % self.width, flat // self.width, 1)
