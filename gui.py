# -*- coding: utf-8 -*-
"""tkinter 图形界面：预设图案、暂停/单步、鼠标绘制、代数与存活统计、速度与尺寸调节。"""

import tkinter as tk
from tkinter import messagebox, simpledialog

import engine
import patterns
from version import VERSION_TAG

CELL = 14            # 单元格边长（像素）
DEFAULT_W = 60
DEFAULT_H = 40
MIN_W, MAX_W = 5, 160
MIN_H, MAX_H = 5, 100

COLOR_BG = "#0f141a"
COLOR_GRID = "#232b36"
COLOR_ALIVE = "#3ddc84"
COLOR_TEXT = "#c9d4e0"
COLOR_HINT = "#7a8699"


class LifeGUI:
    """主窗口。棋盘数据在 self.grid（engine.Grid），画布只负责显示。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"康威生命游戏 {VERSION_TAG}")
        self.interval_ms = tk.IntVar(value=120)
        self.running = False
        self.generation = 0
        self._after_id = None
        self.grid = engine.Grid(DEFAULT_W, DEFAULT_H)
        self._build_ui()
        self.draw_all()
        self._fit_window()

    # ---- 界面搭建 ------------------------------------------------------

    def _build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=4)

        self.btn_run = tk.Button(top, text="开始", width=8, command=self.toggle_run)
        self.btn_run.pack(side=tk.LEFT)
        tk.Button(top, text="单步", width=6, command=self.step_once).pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(top, text="清空", width=6, command=self.clear_board).pack(side=tk.LEFT, padx=(4, 0))
        tk.Button(top, text="随机", width=6, command=self.random_fill).pack(side=tk.LEFT, padx=(4, 0))

        tk.Label(top, text="预设:").pack(side=tk.LEFT, padx=(12, 2))
        catalog = patterns.names()
        self.preset_var = tk.StringVar(value=catalog[0])
        tk.OptionMenu(top, self.preset_var, *catalog).pack(side=tk.LEFT)
        tk.Button(top, text="放置", command=self.place_preset).pack(side=tk.LEFT, padx=(2, 0))

        tk.Label(top, text="速度(ms):").pack(side=tk.LEFT, padx=(12, 2))
        self.speed_var = tk.StringVar(value=str(self.interval_ms.get()))
        self.ent_speed = tk.Entry(top, width=6, textvariable=self.speed_var,
                                  justify=tk.CENTER)
        self.ent_speed.pack(side=tk.LEFT)
        self.ent_speed.bind("<Return>", self._apply_speed)
        self.ent_speed.bind("<FocusOut>", self._apply_speed)
        self.scale = tk.Scale(top, from_=10, to=500, orient=tk.HORIZONTAL,
                              showvalue=False, command=self._on_scale, length=110)
        self.scale.pack(side=tk.LEFT)
        self.scale.set(self.interval_ms.get())
        self.interval_ms.trace_add("write", self._sync_speed_text)

        tk.Button(top, text="关于", width=6, command=self.show_about).pack(side=tk.RIGHT)

        bottom = tk.Frame(self.root)
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)
        tk.Label(bottom, text="横:").pack(side=tk.LEFT)
        self.ent_w = tk.Entry(bottom, width=5)
        self.ent_w.insert(0, str(DEFAULT_W))
        self.ent_w.pack(side=tk.LEFT)
        tk.Label(bottom, text="纵:").pack(side=tk.LEFT, padx=(6, 0))
        self.ent_h = tk.Entry(bottom, width=5)
        self.ent_h.insert(0, str(DEFAULT_H))
        self.ent_h.pack(side=tk.LEFT)
        tk.Button(bottom, text="应用尺寸", command=self.apply_size).pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(bottom, text="左键画 / 右键擦", fg=COLOR_HINT).pack(side=tk.LEFT, padx=(16, 0))
        self.status = tk.Label(bottom, text="", anchor="e", fg=COLOR_TEXT)
        self.status.pack(side=tk.RIGHT)

        holder = tk.Frame(self.root)
        holder.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(holder, bg=COLOR_BG, highlightthickness=0)
        vs = tk.Scrollbar(holder, orient=tk.VERTICAL, command=self.canvas.yview)
        hs = tk.Scrollbar(holder, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # macOS 的 Tk 对右键编号在不同构建里可能是 Button-2 或 Button-3，两个都绑
        self.canvas.bind("<Button-1>", self._on_paint)
        self.canvas.bind("<B1-Motion>", self._on_paint)
        for seq in ("<Button-2>", "<Button-3>", "<B2-Motion>", "<B3-Motion>"):
            self.canvas.bind(seq, self._on_erase)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---- 窗口自适应 ------------------------------------------------------

    def _fit_window(self) -> None:
        """画布视口设为棋盘像素尺寸，窗口交给 WM 按内容自适应——
        打开/应用尺寸后整幅棋盘恰好可见；超出屏幕由系统钳制，滚动条兜底。"""
        self.canvas.configure(width=self.grid.width * CELL,
                              height=self.grid.height * CELL)
        self.root.update_idletasks()
        self.root.geometry("")

    # ---- 绘制 ----------------------------------------------------------

    def draw_all(self) -> None:
        """整幅重画：网格线 + 细胞。改尺寸后调用。"""
        w = self.grid.width * CELL
        h = self.grid.height * CELL
        self.canvas.configure(scrollregion=(0, 0, w, h))
        self.canvas.delete("all")
        for gx in range(self.grid.width + 1):
            self.canvas.create_line(gx * CELL, 0, gx * CELL, h, fill=COLOR_GRID)
        for gy in range(self.grid.height + 1):
            self.canvas.create_line(0, gy * CELL, w, gy * CELL, fill=COLOR_GRID)
        self.draw_cells()

    def draw_cells(self) -> None:
        """只重画细胞层。"""
        self.canvas.delete("cells")
        pad = 1
        for x, y in self.grid.alive_coords():
            x0, y0 = x * CELL + pad, y * CELL + pad
            self.canvas.create_rectangle(x0, y0, x0 + CELL - 2 * pad, y0 + CELL - 2 * pad,
                                         fill=COLOR_ALIVE, outline="", tags="cells")
        self.update_status()

    def update_status(self) -> None:
        self.status.config(
            text=f"第 {self.generation} 代 · 存活 {self.grid.alive_count()} · "
                 f"{int(self.interval_ms.get())}ms")

    # ---- 鼠标 ----------------------------------------------------------

    def _cell_from_event(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return int(cx // CELL), int(cy // CELL)

    def _on_paint(self, event) -> None:
        x, y = self._cell_from_event(event)
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            self.grid.set(x, y, 1)
            self.draw_cells()

    def _on_erase(self, event) -> None:
        x, y = self._cell_from_event(event)
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            self.grid.set(x, y, 0)
            self.draw_cells()

    # ---- 控制 ----------------------------------------------------------

    def toggle_run(self) -> None:
        self.running = not self.running
        self.btn_run.config(text="暂停" if self.running else "开始")
        if self.running:
            self._tick()

    def _tick(self) -> None:
        if not self.running:
            return
        self.step_once()
        self._after_id = self.root.after(int(self.interval_ms.get()), self._tick)

    def step_once(self) -> None:
        self.grid.step()
        self.generation += 1
        self.draw_cells()

    def clear_board(self) -> None:
        self.running = False
        self.btn_run.config(text="开始")
        self.grid.clear()
        self.generation = 0
        self.draw_cells()

    def random_fill(self) -> None:
        total = self.grid.width * self.grid.height
        count = simpledialog.askinteger(
            "随机填充", f"生命个数（0 ~ {total}）", parent=self.root,
            initialvalue=max(1, total // 8), minvalue=0, maxvalue=total)
        if count is None:
            return
        self.grid.randomize(count)
        self.generation = 0
        self.draw_cells()

    def place_preset(self) -> None:
        name = self.preset_var.get()
        coords, pw, ph = patterns.coords_of(name)
        if pw > self.grid.width or ph > self.grid.height:
            messagebox.showwarning(
                "放不下", f"图案 {name}（{pw}×{ph}）超出棋盘 "
                f"{self.grid.width}×{self.grid.height}，请调大棋盘。")
            return
        self.grid.place(coords, (self.grid.width - pw) // 2, (self.grid.height - ph) // 2)
        self.draw_cells()

    def apply_size(self) -> None:
        try:
            w = int(self.ent_w.get().strip())
            h = int(self.ent_h.get().strip())
        except ValueError:
            messagebox.showwarning("输入无效", "横纵长度须为整数。")
            return
        if not (MIN_W <= w <= MAX_W and MIN_H <= h <= MAX_H):
            messagebox.showwarning("超出范围", f"横 {MIN_W}~{MAX_W}，纵 {MIN_H}~{MAX_H}。")
            return
        self.running = False
        self.btn_run.config(text="开始")
        self.grid = engine.Grid(w, h)
        self.generation = 0
        self.draw_all()
        self._fit_window()

    # ---- 速度输入（输入框与滑块双向同步） ---------------------------------

    def _sync_speed_text(self, *_args) -> None:
        """滑块或程序侧改了刷新间隔，输入框跟着显示同值。"""
        self.speed_var.set(str(self.interval_ms.get()))

    def _on_scale(self, raw: str) -> None:
        """滑块拖动 → 更新刷新间隔（trace 再同步输入框）。"""
        self.interval_ms.set(int(float(raw)))

    def _apply_speed(self, _event=None) -> None:
        """输入框回车/失焦时生效；非法输入标红提示后回落当前值。"""
        try:
            value = int(self.speed_var.get().strip())
        except ValueError:
            value = None
        if value is None or not 1 <= value <= 10000:
            self.ent_speed.config(fg="#ff6b6b")
            self.root.after(700, self._restore_speed_color)
            self.speed_var.set(str(self.interval_ms.get()))
            return
        # 先动滑块（command 回调会写一次钳位值），后设真实间隔，最终以输入为准；
        # 超出滑块范围时滑块停在端点，实际间隔不受限。
        self.scale.set(value)
        self.interval_ms.set(value)
        self.speed_var.set(str(value))
        self.update_status()

    def _restore_speed_color(self) -> None:
        if self.ent_speed.winfo_exists():
            self.ent_speed.config(fg=COLOR_TEXT)

    def show_about(self) -> None:
        messagebox.showinfo(
            "关于 康威生命游戏",
            f"康威生命游戏 life_game {VERSION_TAG}\n"
            "\n"
            "标准康威规则（B3/S23），棋盘为环面\n"
            "仅用 Python 标准库，零第三方依赖\n"
            "\n"
            "作者: Toki Mizuki\n"
            "Email: dboycht@qq.com\n"
            "Github: github.com/dboycht/life_game",
            parent=self.root)

    def on_close(self) -> None:
        self.running = False
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
        self.root.destroy()
