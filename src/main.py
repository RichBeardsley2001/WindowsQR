"""
WindowsQR — main entry point.

Architecture
------------
* tkinter hidden root   → main thread (event dispatcher for all dialogs)
* pystray               → background thread via run_detached()
* pynput GlobalHotKeys  → background thread via .start()
* scanner / updater     → ad-hoc daemon threads

Hotkeys
-------
  Alt + Ctrl + Q   → scan screen for QR code
  Ctrl + Shift + Q → open accessible menu dialog
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox

# Ensure src/ is on the path when running from the project root
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import pystray
from PIL import Image

from version import APP_NAME, APP_VERSION
from speech import speak
from scanner import scan
from updater import check_for_updates
from menu_dialog import MenuDialog

# ---------------------------------------------------------------------------
# Single-instance mutex (Windows)
# ---------------------------------------------------------------------------
_mutex = None

def _acquire_single_instance() -> bool:
    """Return True if we are the only running instance."""
    global _mutex
    try:
        import win32event
        import win32api
        import winerror

        _mutex = win32event.CreateMutex(None, True, "WindowsQR_SingleInstance")
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            return False
    except Exception:
        pass  # If pywin32 is unavailable, allow multiple instances
    return True


# ---------------------------------------------------------------------------
# Tray icon image (generated at runtime)
# ---------------------------------------------------------------------------

def _build_icon_image() -> Image.Image:
    """Load assets/icon.png if available, otherwise generate a fallback."""
    icon_path = os.path.join(os.path.dirname(_here), "assets", "icon.png")
    if os.path.exists(icon_path):
        return Image.open(icon_path).convert("RGBA")

    # Programmatic QR-corner icon (64×64)
    from PIL import ImageDraw

    size = 64
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    s = size // 8  # cell size

    def corner(ox, oy):
        draw.rectangle([ox, oy, ox + 7 * s - 1, oy + 7 * s - 1], fill=(0, 0, 0, 255))
        draw.rectangle(
            [ox + s, oy + s, ox + 6 * s - 1, oy + 6 * s - 1],
            fill=(255, 255, 255, 255),
        )
        draw.rectangle(
            [ox + 2 * s, oy + 2 * s, ox + 5 * s - 1, oy + 5 * s - 1],
            fill=(0, 0, 0, 255),
        )

    corner(0, 0)
    corner(size - 7 * s, 0)
    corner(0, size - 7 * s)

    # Decorative data dots
    import random
    rng = random.Random(42)
    for row in range(9, size // s - 1):
        for col in range(9, size // s - 1):
            if rng.random() > 0.55:
                x, y = col * s, row * s
                draw.rectangle([x, y, x + s - 2, y + s - 2], fill=(0, 0, 0, 255))

    return img


# ---------------------------------------------------------------------------
# Application class
# ---------------------------------------------------------------------------

class WindowsQRApp:
    def __init__(self):
        # Hidden tkinter root — all dialogs live on this thread
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title(APP_NAME)

        self._menu_dialog = MenuDialog(
            self._root,
            on_help=self._show_help,
            on_check_updates=self._check_updates_bg,
            on_quit=self._quit,
        )

        # Build tray icon
        icon_image = _build_icon_image()
        tray_menu = pystray.Menu(
            pystray.MenuItem(
                "Help",
                lambda _icon, _item: self._root.after(0, self._show_help),
            ),
            pystray.MenuItem(
                "Check for Updates",
                lambda _icon, _item: self._check_updates_bg(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Quit",
                lambda _icon, _item: self._root.after(0, self._quit),
            ),
        )
        self._icon = pystray.Icon(
            APP_NAME,
            icon_image,
            f"{APP_NAME}  •  Alt+Ctrl+Q to scan",
            menu=tray_menu,
        )

        self._hotkey_listener = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        # Start pystray in background
        self._icon.run_detached()

        # Register global hotkeys
        self._start_hotkeys()

        # Background startup update check (silent)
        threading.Thread(
            target=check_for_updates, kwargs={"silent": True}, daemon=True
        ).start()

        speak(
            f"{APP_NAME} started. "
            "Press Alt Control Q to scan. "
            "Press Control Shift Q for the menu."
        )

        try:
            self._root.mainloop()
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        try:
            self._icon.stop()
        except Exception:
            pass
        try:
            if self._hotkey_listener:
                self._hotkey_listener.stop()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Hotkeys (pynput)
    # ------------------------------------------------------------------

    def _start_hotkeys(self) -> None:
        from pynput import keyboard

        def _scan():
            threading.Thread(target=scan, daemon=True).start()

        def _menu():
            self._root.after(0, self._menu_dialog.show)

        self._hotkey_listener = keyboard.GlobalHotKeys(
            {
                "<ctrl>+<alt>+q": _scan,
                "<ctrl>+<shift>+q": _menu,
            }
        )
        self._hotkey_listener.start()

    # ------------------------------------------------------------------
    # Menu actions (always called on tkinter main thread)
    # ------------------------------------------------------------------

    def _show_help(self) -> None:
        messagebox.showinfo(
            f"{APP_NAME} Help",
            f"{APP_NAME} — Screen QR Code Scanner\n\n"
            "Keyboard shortcuts:\n"
            "  Alt + Ctrl + Q   — Scan screen for a QR code\n"
            "  Ctrl + Shift + Q — Open application menu\n\n"
            "The application runs in the system tray.\n"
            "Right-click the tray icon for additional options.\n\n"
            f"Version: {APP_VERSION}\n"
            "https://github.com/RichBeardsley2001/WindowsQR",
        )

    def _check_updates_bg(self) -> None:
        threading.Thread(
            target=check_for_updates, kwargs={"silent": False}, daemon=True
        ).start()

    def _quit(self) -> None:
        speak("Quitting WindowsQR.")
        self._root.after(200, self._do_quit)

    def _do_quit(self) -> None:
        self._cleanup()
        self._root.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not _acquire_single_instance():
        # Another instance is already running — just exit silently
        sys.exit(0)

    app = WindowsQRApp()
    app.run()


if __name__ == "__main__":
    main()
