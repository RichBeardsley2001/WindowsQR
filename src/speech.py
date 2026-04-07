"""
Text-to-speech module.
Priority: NVDA → JAWS → SAPI (via accessible_output2 or direct win32com).
"""
import threading
import ctypes
import os
import sys

_ao = None
_ao_lock = threading.Lock()


def _get_ao():
    """Lazy-init accessible_output2 Auto speaker."""
    global _ao
    with _ao_lock:
        if _ao is None:
            try:
                from accessible_output2.outputs.auto import Auto
                _ao = Auto()
            except Exception:
                _ao = False  # sentinel: tried and failed
    return _ao if _ao else None


def _speak_nvda_direct(text: str) -> bool:
    """Speak via NVDA controller client DLL (bundled by accessible_output2 or located on disk)."""
    search_dirs = []
    # Bundled alongside our frozen exe
    if getattr(sys, "frozen", False):
        search_dirs.append(os.path.dirname(sys.executable))
    else:
        search_dirs.append(os.path.dirname(os.path.abspath(__file__)))

    # accessible_output2 bundles the DLL
    try:
        import accessible_output2
        search_dirs.append(os.path.join(os.path.dirname(accessible_output2.__file__), "lib"))
        search_dirs.append(os.path.join(os.path.dirname(accessible_output2.__file__), "lib", "x64"))
    except Exception:
        pass

    search_dirs += [
        r"C:\Program Files (x86)\NVDA",
        r"C:\Program Files\NVDA",
    ]

    for directory in search_dirs:
        for dll_name in ("nvdaControllerClient64.dll", "nvdaControllerClient32.dll"):
            dll_path = os.path.join(directory, dll_name)
            if os.path.exists(dll_path):
                try:
                    lib = ctypes.WinDLL(dll_path)
                    lib.nvdaController_testIfRunning.restype = ctypes.c_uint
                    lib.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
                    lib.nvdaController_speakText.restype = ctypes.c_uint
                    lib.nvdaController_cancelSpeech.restype = ctypes.c_uint
                    if lib.nvdaController_testIfRunning() == 0:  # 0 = NVDA running
                        lib.nvdaController_cancelSpeech()
                        lib.nvdaController_speakText(text)
                        return True
                except Exception:
                    pass
    return False


def _speak_jaws(text: str) -> bool:
    """Speak via JAWS COM interface."""
    try:
        import win32com.client
        jaws = win32com.client.Dispatch("FreedomSci.JawsApi")
        return bool(jaws.SayString(text, True))
    except Exception:
        return False


def _speak_sapi(text: str) -> None:
    """Speak via Microsoft SAPI — always available on Windows."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
        import win32com.client
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        # SVSFlagsAsync(1) | SVSFPurgeBeforeSpeak(2) = 3
        sapi.Speak(text, 3)
    except Exception:
        pass


def speak(text: str) -> None:
    """Speak *text* through the best available method (non-blocking)."""
    if not text:
        return

    ao = _get_ao()
    if ao is not None:
        try:
            ao.speak(text, interrupt=True)
            return
        except Exception:
            pass

    # Manual fallbacks
    if _speak_nvda_direct(text):
        return
    if _speak_jaws(text):
        return
    _speak_sapi(text)
