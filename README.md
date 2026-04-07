# WindowsQR

Windows system-tray application that scans QR codes from your screen and opens them in your browser.

All status messages are spoken through your active screen reader (NVDA, JAWS) or Microsoft SAPI — no extra popups.

## Features

- **Screen scan** — grabs all monitors, decodes the first QR code found
- **Speaks via screen reader or SAPI** — no visual announcement when snapping
- **System tray** — minimal footprint, always available
- **Auto-update** — checks GitHub Releases on startup; downloads and installs silently
- **Accessible menu** — full keyboard control, works with all screen readers
- **Optional auto-start** — checkbox during install

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| **Alt + Ctrl + Q** | Scan screen for QR code |
| **Ctrl + Shift + Q** | Open application menu |

## Install

Download the latest `WindowsQR-Setup-x.x.x.exe` from the [Releases](https://github.com/RichBeardsley2001/WindowsQR/releases) page and run it.

During setup you can tick **"Start WindowsQR automatically when Windows starts"**.

## Build from source

**Requirements:** Python 3.11+, [Inno Setup 6](https://jrsoftware.org/isdl.php)

```
pip install -r requirements.txt
pip install pyinstaller
python build.py
```

The finished installer will be at `Output\WindowsQR-Setup-<version>.exe`.

## Release a new version

1. Bump `APP_VERSION` in `src/version.py`
2. Commit and tag: `git tag v1.2.3 && git push origin v1.2.3`
3. GitHub Actions builds and publishes the installer automatically

## Accessibility notes

- NVDA and JAWS are detected via their controller-client interface; no extra configuration needed
- When neither is running, Microsoft SAPI is used
- The Ctrl+Shift+Q menu dialog uses standard Windows controls — fully navigable by keyboard and compatible with all screen readers
- The Inno Setup installer uses the default Modern wizard style which is screen-reader accessible
