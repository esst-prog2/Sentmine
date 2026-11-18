"""Pictures of one window drawn by the window itself (Windows' PrintWindow, full content), not copied from the
screen: it works when the window is covered. Saved as BMP files. Import grab(title) or run: python winshot.py <title> <out.bmp>"""
import ctypes
import ctypes.wintypes as w
import struct
import sys

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
user32.SetProcessDPIAware()


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", w.DWORD), ("biWidth", w.LONG), ("biHeight", w.LONG), ("biPlanes", w.WORD), ("biBitCount", w.WORD),
                ("biCompression", w.DWORD), ("biSizeImage", w.DWORD), ("biXPelsPerMeter", w.LONG), ("biYPelsPerMeter", w.LONG),
                ("biClrUsed", w.DWORD), ("biClrImportant", w.DWORD)]


def window(title):
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        raise SystemExit("window not found: " + title)
    return hwnd


def grab(hwnd):
    """(width, height, BGRA bytes top-down) of the window as it draws itself."""
    r = w.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    width, height = r.right - r.left, r.bottom - r.top
    screen = user32.GetDC(0)
    dc = gdi32.CreateCompatibleDC(screen)
    bmp = gdi32.CreateCompatibleBitmap(screen, width, height)
    gdi32.SelectObject(dc, bmp)
    user32.PrintWindow(hwnd, dc, 2)   # PW_RENDERFULLCONTENT
    header = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
    pixels = ctypes.create_string_buffer(width * height * 4)
    gdi32.GetDIBits(dc, bmp, 0, height, pixels, ctypes.byref(header), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(dc)
    user32.ReleaseDC(0, screen)
    return width, height, pixels.raw


def save_bmp(path, width, height, data):
    size = 54 + len(data)
    with open(path, "wb") as f:
        f.write(b"BM" + struct.pack("<IHHI", size, 0, 0, 54))
        f.write(struct.pack("<IiiHHIIiiII", 40, width, -height, 1, 32, 0, len(data), 2835, 2835, 0, 0))
        f.write(data)


if __name__ == "__main__":
    width, height, data = grab(window(sys.argv[1]))
    save_bmp(sys.argv[2], width, height, data)
    print(width, height)
