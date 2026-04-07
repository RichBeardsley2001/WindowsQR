"""
QR code scanner — grabs the full screen (all monitors) and decodes QR codes.
Speech only; no visual popup when announcing a scan in progress.
"""
import webbrowser
import threading

import numpy as np
from PIL import ImageGrab

from speech import speak


def scan() -> None:
    """Take a full-screen grab and open the first QR code found."""
    # Announce silently (no window shown)
    speak("Scanning")

    try:
        screenshot = ImageGrab.grab(all_screens=True)
    except TypeError:
        # Older Pillow that doesn't support all_screens
        screenshot = ImageGrab.grab()

    results = _detect_all(screenshot)

    if not results:
        speak("No QR code found")
        return

    if len(results) == 1:
        _handle(results[0])
    else:
        speak(f"Found {len(results)} QR codes, opening first")
        _handle(results[0])


# ---------------------------------------------------------------------------
# QR detection helpers
# ---------------------------------------------------------------------------

def _detect_all(img) -> list:
    """Return a list of decoded QR code strings from *img*."""
    img_array = np.array(img)
    results = _detect_opencv(img_array)
    return results


def _detect_opencv(img_array) -> list:
    """Detect QR codes with OpenCV (no external DLL needed)."""
    try:
        import cv2
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        results = []

        # Multi-detect (OpenCV 4.5.2+)
        try:
            detector = cv2.QRCodeDetector()
            ok, decoded_info, *_ = detector.detectAndDecodeMulti(img_bgr)
            if ok:
                for info in decoded_info:
                    if info:
                        results.append(info)
        except Exception:
            pass

        if not results:
            # ArUco-based detector (opencv-contrib, more robust)
            try:
                detector = cv2.QRCodeDetectorAruco()
                data, *_ = detector.detectAndDecode(img_bgr)
                if data:
                    results.append(data)
            except AttributeError:
                pass

        if not results:
            # Plain single-QR fallback
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img_bgr)
            if data:
                results.append(data)

        return results
    except Exception:
        return []


# ---------------------------------------------------------------------------
# QR data handler
# ---------------------------------------------------------------------------

def _handle(data: str) -> None:
    """Speak the result and act on the QR code content."""
    data = data.strip()

    if data.startswith(("http://", "https://", "ftp://")):
        speak("QR code found, opening URL in browser")
        webbrowser.open(data)
    elif data.startswith("tel:"):
        number = data[4:]
        speak(f"QR code contains phone number: {number}")
    elif data.startswith("mailto:"):
        email = data[7:].split("?")[0]
        speak(f"QR code contains email: {email}")
        webbrowser.open(data)
    elif data.startswith("wifi:"):
        speak("QR code contains Wi-Fi network information")
    elif len(data) <= 80:
        speak(f"QR code contains: {data}")
        webbrowser.open(data)
    else:
        speak("QR code decoded, opening content")
        webbrowser.open(data)
