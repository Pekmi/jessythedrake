import cv2
import mss
import time
import win32gui
import numpy as np
import pygetwindow as gw


def capture_screen(region=None):
    """
    Retourne une capture d'écran de la région spécifiée.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        if region:
            monitor = {
                "left": region[0],
                "top": region[1],
                "width": region[2],
                "height": region[3]
            }
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def get_window_region(window_name):
    """
    Retourne la région de la fenêtre spécifiée si elle est active.
    """
    try:
        window = gw.getWindowsWithTitle(window_name)[0]
        active_hwnd = win32gui.GetForegroundWindow()

        # if window._hWnd != active_hwnd:
        #     print(f"Window '{window_name}' is not the active window.", end='\r', flush=True)
        #     return None
        print(f"Window '{window_name}' is active.", end='\r', flush=True)
        return (window.left, window.top, window.width, window.height)
    except IndexError:
        print(f"Window '{window_name}' not found.", end='\r', flush=True)
        return None
    