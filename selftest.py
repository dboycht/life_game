# -*- coding: utf-8 -*-
"""引擎自测：python3 selftest.py。全部 PASS 退出码 0，任一 FAIL 退出码 1。"""

import sys

import engine
import patterns


def cells_of(grid):
    return set(grid.alive_coords())


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        print(f"[FAIL] {name}: {exc}")
        return False
    print(f"[PASS] {name}")
    return True


def t_neighbors_excludes_self():
    g = engine.Grid(5, 5)
    g.set(2, 2)
    assert g.neighbors(2, 2) == 0, "自身不计入邻域"
    assert g.neighbors(1, 1) == 1


def t_neighbors_torus():
    g = engine.Grid(5, 5)
    for x, y in [(4, 4), (1, 1), (4, 0), (0, 4)]:
        g.set(x, y)
    assert g.neighbors(0, 0) == 4, f"环面四角绕回应为 4: {g.neighbors(0, 0)}"


def t_block_still_life():
    g = engine.Grid(6, 6)
    g.place([(1, 1), (2, 1), (1, 2), (2, 2)])
    before = cells_of(g)
    g.step()
    assert cells_of(g) == before, "块状静止物不应变化"


def t_blinker_period2():
    g = engine.Grid(7, 7)
    g.place([(1, 2), (2, 2), (3, 2)])
    g.step()
    assert cells_of(g) == {(2, 1), (2, 2), (2, 3)}, f"闪变应转为竖排: {sorted(cells_of(g))}"
    g.step()
    assert cells_of(g) == {(1, 2), (2, 2), (3, 2)}, "闪变第 2 代应回到横排"


def t_glider_moves():
    coords, _, _ = patterns.coords_of("滑翔机")
    g = engine.Grid(20, 20)
    g.place(coords, 5, 5)
    for _ in range(4):
        g.step()
    got = {(x - 5, y - 5) for x, y in cells_of(g)}
    expect = {(x + 1, y + 1) for x, y in coords}
    assert got == expect, f"滑翔机 4 代后应位移 (1,1): {sorted(got)}"


def t_lwss_moves():
    coords, _, _ = patterns.coords_of("轻型飞船 LWSS")
    g = engine.Grid(30, 20)
    g.place(coords, 10, 8)
    for _ in range(4):
        g.step()
    got = sorted((x - 10, y - 8) for x, y in cells_of(g))
    assert len(got) == len(coords), f"LWSS 细胞数应保持 {len(coords)}: {len(got)}"
    for dx in (2, -2):
        if got == sorted((x + dx, y) for x, y in coords):
            break
    else:
        raise AssertionError(f"LWSS 4 代后应平移 ±2 格: {got}")


def t_pulsar_period3():
    coords, _, _ = patterns.coords_of("脉冲星")
    g = engine.Grid(25, 25)
    g.place(coords, 6, 6)
    base = cells_of(g)
    g.step()
    s1 = cells_of(g)
    g.step()
    s2 = cells_of(g)
    g.step()
    assert cells_of(g) == base, "脉冲星第 3 代应回到初始"
    assert s1 != base and s2 != base, "脉冲星第 1、2 代应有变化"


def t_gun_emits_gliders():
    coords, w, h = patterns.coords_of("高斯帕滑翔机枪")
    assert (w, h) == (36, 9), f"枪应为 36×9: {w}×{h}"
    assert len(coords) == 36, f"枪初始应为 36 个细胞: {len(coords)}"
    g = engine.Grid(80, 60)
    g.place(coords, 2, 2)
    start = g.alive_count()
    for _ in range(40):
        g.step()
    assert g.alive_count() > start, "枪应持续吐出滑翔机使总数增加"


def t_randomize_exact_and_unique():
    g = engine.Grid(40, 30)
    g.randomize(120)
    assert g.alive_count() == 120, f"生命数应精确为 120: {g.alive_count()}"
    assert len(cells_of(g)) == 120, "随机播种坐标不得重叠"
    g.randomize(0)
    assert g.alive_count() == 0


def t_place_wraps():
    g = engine.Grid(10, 10)
    g.place([(0, 0), (-1, -1), (10, 5)])
    assert g.get(0, 0) == 1 and g.get(9, 9) == 1 and g.get(0, 5) == 1, "出界坐标应绕回对侧"


def t_patterns_in_bounds():
    for name in patterns.names():
        coords, w, h = patterns.coords_of(name)
        assert all(0 <= x < w and 0 <= y < h for x, y in coords), f"{name} 坐标越界"


CASES = [
    ("邻域不含自身", t_neighbors_excludes_self),
    ("邻域环面绕回", t_neighbors_torus),
    ("块状静止物", t_block_still_life),
    ("闪变周期 2", t_blinker_period2),
    ("滑翔机位移 (1,1)/4代", t_glider_moves),
    ("LWSS 平移 ±2/4代", t_lwss_moves),
    ("脉冲星周期 3", t_pulsar_period3),
    ("高斯帕枪持续吐滑翔机", t_gun_emits_gliders),
    ("随机播种精确且不重叠", t_randomize_exact_and_unique),
    ("布阵出界绕回", t_place_wraps),
    ("图案定义合法", t_patterns_in_bounds),
]


def main() -> None:
    results = [check(name, fn) for name, fn in CASES]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} 通过")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
