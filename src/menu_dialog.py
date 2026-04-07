"""
Accessible menu dialog — opened via Ctrl+Shift+Q or left-click on the tray icon.
Uses standard tkinter controls so all screen readers can interact with it.
"""
import tkinter as tk
from tkinter import ttk

from version import APP_NAME, APP_VERSION


class MenuDialog:
    """A small, keyboard-accessible popup with Help / Check for Updates / Quit."""

    def __init__(self, root: tk.Tk, on_help, on_check_updates, on_quit):
        self._root = root
        self._on_help = on_help
        self._on_check_updates = on_check_updates
        self._on_quit = on_quit
        self._window: tk.Toplevel | None = None

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show(self) -> None:
        """Show (or raise) the menu dialog."""
        if self._window and self._window.winfo_exists():
            self._window.lift()
            self._window.focus_force()
            return

        win = tk.Toplevel(self._root)
        win.title(APP_NAME)
        win.resizable(False, False)
        win.attributes("-topmost", True)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        # Accessible label
        ttk.Label(frame, text=f"{APP_NAME} — version {APP_VERSION}").pack(
            anchor="w", pady=(0, 8)
        )

        btn_help = ttk.Button(frame, text="Help", command=self._help, width=22)
        btn_help.pack(fill=tk.X, pady=2)

        btn_updates = ttk.Button(
            frame,
            text="Check for Updates",
            command=self._check_updates,
            width=22,
        )
        btn_updates.pack(fill=tk.X, pady=2)

        ttk.Separator(frame).pack(fill=tk.X, pady=6)

        btn_quit = ttk.Button(frame, text="Quit", command=self._quit, width=22)
        btn_quit.pack(fill=tk.X, pady=2)

        # Keyboard: Escape closes, Tab cycles naturally
        win.bind("<Escape>", lambda _e: win.destroy())

        # Position near bottom-right (close to tray)
        win.update_idletasks()
        w = win.winfo_reqwidth()
        h = win.winfo_reqheight()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"+{sw - w - 24}+{sh - h - 60}")

        self._window = win
        btn_help.focus_set()
        win.grab_set()

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _close(self) -> None:
        if self._window and self._window.winfo_exists():
            self._window.destroy()

    def _help(self) -> None:
        self._close()
        self._on_help()

    def _check_updates(self) -> None:
        self._close()
        self._on_check_updates()

    def _quit(self) -> None:
        self._close()
        self._on_quit()
