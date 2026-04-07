"""
build.py — one-command build script.

Steps
-----
1. Read the version from src/version.py
2. Generate the tray icon (assets/icon.png + assets/icon.ico)
3. Run PyInstaller to create dist/WindowsQR/
4. Run Inno Setup (ISCC) to create Output/WindowsQR-Setup-<version>.exe

Usage
-----
    python build.py
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def read_version() -> str:
    version_file = os.path.join(ROOT, "src", "version.py")
    with open(version_file) as fh:
        content = fh.read()
    m = re.search(r'APP_VERSION\s*=\s*["\'](.+?)["\']', content)
    if not m:
        raise RuntimeError("Could not read APP_VERSION from src/version.py")
    return m.group(1)


def run(cmd: list, **kwargs) -> None:
    print(">>", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kwargs)


def main() -> None:
    os.chdir(ROOT)
    version = read_version()
    print(f"Building WindowsQR v{version}\n")

    # 1. Generate icon
    run([sys.executable, "generate_icon.py"])

    # 2. PyInstaller
    run([sys.executable, "-m", "PyInstaller", "WindowsQR.spec", "--clean", "--noconfirm"])

    # 3. Inno Setup
    iscc_candidates = [
        r"C:\Users\Rich\AppData\Local\Programs\Inno Setup 6\ISCC.exe",  # winget user install
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        "ISCC.exe",   # if on PATH (e.g. CI via Chocolatey)
        "iscc",       # Linux/Wine
    ]
    for iscc in iscc_candidates:
        try:
            # Use PowerShell to handle paths with spaces reliably on Windows
            import platform
            if platform.system() == "Windows":
                run([
                    "powershell.exe", "-Command",
                    f"& '{iscc}' '/DAppVersion={version}' "
                    f"'{os.path.join(ROOT, \"WindowsQR.iss\")}'"
                ])
            else:
                run([iscc, f"/DAppVersion={version}", "WindowsQR.iss"])
            print(f"\nInstaller created: Output/WindowsQR-Setup-{version}.exe")
            break
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            if isinstance(exc, subprocess.CalledProcessError):
                raise
            # iscc not found at this path — try next
    else:
        print(
            "\nInno Setup (ISCC) not found — skipping installer step.\n"
            "Install Inno Setup 6 from https://jrsoftware.org/isdl.php"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
