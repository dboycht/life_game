# -*- coding: utf-8 -*-
"""终端版入口：python3 cli.py。"""

import time

import engine
import patterns
from version import VERSION_TAG


def ask_int(prompt: str, lo: int, hi: int) -> int:
    """循环读入整数，直到落在 [lo, hi]。"""
    while True:
        raw = input(f"{prompt} [{lo}~{hi}]: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("  请输入整数，重试。")
            continue
        if lo <= value <= hi:
            return value
        print("  超出范围，重试。")


def ask_float(prompt: str, lo: float, hi: float, default: float) -> float:
    """循环读入浮点数，直到落在 [lo, hi]；空回车取 default。"""
    while True:
        raw = input(f"{prompt} [{lo}~{hi}，回车默认 {default}]: ").strip()
        if raw == "":
            return default
        try:
            value = float(raw)
        except ValueError:
            print("  请输入数字，重试。")
            continue
        if lo <= value <= hi:
            return value
        print("  超出范围，重试。")


def manual_coords(grid: engine.Grid, width: int, height: int) -> None:
    """手动录入生命坐标（1 起，空回车结束）。"""
    print(f"输入生命坐标（横 1~{width}，纵 1~{height}），直接按回车结束录入")
    while True:
        raw_x = input("横着数第几个-?>").strip()
        if raw_x == "":
            break
        try:
            x = int(raw_x) - 1
            y = int(input("竖着数第几个-?>").strip()) - 1
        except ValueError:
            print("  请输入整数，重试。")
            continue
        if not (0 <= x < width and 0 <= y < height):
            print(f"  坐标越界（横 1~{width}，纵 1~{height}），重试。")
            continue
        grid.set(x, y, 1)


def preset_placement(grid: engine.Grid, width: int, height: int) -> bool:
    """选择预设图案并放置在棋盘中央；放不下返回 False。"""
    catalog = patterns.names()
    print("可选图案：")
    for i, name in enumerate(catalog, 1):
        _, pw, ph = patterns.coords_of(name)
        print(f"  {i}. {name}（{pw}×{ph}）")
    idx = ask_int("选择图案编号", 1, len(catalog))
    coords, pw, ph = patterns.coords_of(catalog[idx - 1])
    if pw > width or ph > height:
        print(f"  图案 {pw}×{ph} 超出棋盘 {width}×{height}，请改用更大的棋盘。")
        return False
    grid.place(coords, (width - pw) // 2, (height - ph) // 2)
    return True


def render(grid: engine.Grid, gen: int) -> None:
    """打印棋盘：■ 为生，□ 为死。"""
    print(f"\n当前迭代数: 第{gen}次  存活: {grid.alive_count()}")
    for row in grid.cells:
        print("".join("■" if v else "□" for v in row))


def run() -> None:
    print(f"康威生命游戏 {VERSION_TAG}（终端版）")
    print("规则与原版（康威生命游戏）相同；棋盘为环面：出界绕回对侧。\n")
    width = ask_int("横向长度", 5, 200)
    height = ask_int("纵向长度", 5, 120)
    interval = ask_float("刷新间隔（秒）", 0.01, 5.0, 0.1)
    circle = ask_int("迭代次数", 1, 100000)
    mode = (input("赋予生命的模式（A 手动坐标 / B 随机 / C 预设图案，回车默认 B）: ")
            .strip().upper() or "B")

    grid = engine.Grid(width, height)
    if mode == "A":
        manual_coords(grid, width, height)
    elif mode == "C":
        if not preset_placement(grid, width, height):
            total = width * height
            grid.randomize(ask_int(f"改用随机，生命个数（≤{total}）", 0, total))
    else:
        total = width * height
        grid.randomize(ask_int(f"随机生命个数（≤{total}）", 0, total))

    print("\n开始演化（Ctrl+C 随时退出）")
    for gen in range(1, circle + 1):
        time.sleep(interval)
        render(grid, gen)
        grid.step()
    print("\n循环结束。")
    input("按回车退出")


def main() -> None:
    try:
        run()
    except KeyboardInterrupt:
        print("\n已中断，退出。")
    except EOFError:
        print()


if __name__ == "__main__":
    main()
