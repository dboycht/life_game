# -*- coding: utf-8 -*-
"""GUI 入口：python3 main.py。终端版请跑 cli.py。"""

import tkinter as tk

from gui import LifeGUI


def main() -> None:
    root = tk.Tk()
    LifeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
