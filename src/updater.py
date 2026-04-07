"""
Auto-update via GitHub Releases.
Compares the running version against the latest published release,
downloads the installer, and launches it silently with /CLOSEAPPLICATIONS.
"""
import os
import sys
import subprocess
import tempfile
import threading

import requests

from version import APP_VERSION, GITHUB_OWNER, GITHUB_REPO
from speech import speak


_RELEASES_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)


def _parse_version(v: str):
    """Return a tuple of ints for comparison, e.g. '1.2.3' → (1, 2, 3)."""
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except Exception:
        return (0,)


def check_for_updates(silent: bool = False) -> None:
    """Check GitHub Releases for a newer version.

    Parameters
    ----------
    silent : bool
        When True, do not speak if already up-to-date.
    """
    try:
        resp = requests.get(_RELEASES_URL, timeout=10)
        resp.raise_for_status()
        release = resp.json()
    except Exception as exc:
        if not silent:
            speak(f"Update check failed: {exc}")
        return

    latest_tag = release.get("tag_name", "")
    latest_ver = latest_tag.lstrip("v")
    if not latest_ver:
        if not silent:
            speak("Could not read latest version from GitHub.")
        return

    if _parse_version(latest_ver) <= _parse_version(APP_VERSION):
        if not silent:
            speak("WindowsQR is up to date.")
        return

    # Newer version available — find the installer asset
    installer_url = None
    installer_name = None
    for asset in release.get("assets", []):
        name: str = asset.get("name", "")
        if name.lower().endswith(".exe"):
            installer_url = asset["browser_download_url"]
            installer_name = name
            break

    if not installer_url:
        speak(
            f"Update available: version {latest_ver}, "
            "but no installer found in the release."
        )
        return

    speak(
        f"Update available: version {latest_ver}. "
        "A dialog will open asking whether to install."
    )
    threading.Thread(
        target=_prompt_and_install,
        args=(installer_url, installer_name, latest_ver, release.get("name", "")),
        daemon=True,
    ).start()


def _prompt_and_install(
    url: str, filename: str, version: str, release_name: str
) -> None:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    answer = messagebox.askyesno(
        "WindowsQR Update Available",
        f"A new version is available:\n\n"
        f"  {release_name or ('Version ' + version)}\n\n"
        "Download and install now?\n"
        "(The application will restart automatically.)",
        parent=root,
    )
    root.destroy()

    if not answer:
        speak("Update cancelled.")
        return

    speak("Downloading update. Please wait.")

    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(
            suffix=".exe", prefix="WindowsQR_update_", delete=False
        ) as fh:
            for chunk in resp.iter_content(chunk_size=65536):
                fh.write(chunk)
            installer_path = fh.name

    except Exception as exc:
        speak(f"Download failed: {exc}")
        return

    speak("Update downloaded. Installing now. The application will restart.")
    subprocess.Popen(
        [installer_path, "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"],
        close_fds=True,
    )
