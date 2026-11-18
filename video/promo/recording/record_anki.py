"""Video 2's Anki beat: Anki asks the card for simultaneously (made in sentmine), shows the answer, and it is
answered Good, recorded from Anki's own window with FFmpeg (gdigrab). The card is moved into a deck of its own for
the review and back afterwards. python record_anki.py <card id> <out.mp4>"""
import ctypes
import json
import subprocess
import sys
import time
import urllib.request

CARD, OUT = int(sys.argv[1]), sys.argv[2]
TITLE = "User 1 - Anki"
STORY, HOME = "sentmine story", "sentmine demo"


def anki(action, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode()
    answer = json.loads(urllib.request.urlopen(urllib.request.Request("http://localhost:8765", data=body)).read())
    if answer.get("error"):
        raise SystemExit(f"{action}: {answer['error']}")
    return answer["result"]


user32 = ctypes.windll.user32
window = user32.FindWindowW(None, TITLE)
if not window:
    raise SystemExit("Anki's window was not found")

anki("forgetCards", cards=[CARD])   # new again, so Anki asks it now
anki("createDeck", deck=STORY)
anki("changeDeck", cards=[CARD], deck=STORY)
try:
    anki("guiDeckOverview", name=STORY)
    user32.ShowWindow(window, 9)          # restore if minimised
    user32.keybd_event(0x12, 0, 0, 0)     # a tap of Alt lets this process bring a window forward
    user32.SetForegroundWindow(window)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.8)
    import threading
    from winshot import grab
    width, height, _ = grab(window)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{width}x{height}",
                           "-r", "15", "-i", "-", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-c:v", "libx264", "-crf", "16", OUT],
                          stdin=subprocess.PIPE)
    running = [True]

    def film():   # 15 frames a second, paced by the clock
        began, n = time.time(), 0
        while running[0]:
            w_, h_, data = grab(window)
            if (w_, h_) == (width, height):
                last = data
            due = int((time.time() - began) * 15) + 1
            while n < due:
                ff.stdin.write(last)
                n += 1
            time.sleep(max(0, began + n / 15 - time.time()))

    camera = threading.Thread(target=film)
    camera.start()
    time.sleep(1.2)
    anki("guiDeckReview", name=STORY)       # Anki asks: the front
    time.sleep(3.0)
    anki("guiShowAnswer")                   # the back: the sentence and the meaning
    time.sleep(3.6)
    print("answered:", anki("guiAnswerCard", ease=3))   # Good
    time.sleep(1.6)
    running[0] = False
    camera.join()
    ff.stdin.close()
    ff.wait(timeout=60)
finally:
    anki("changeDeck", cards=[CARD], deck=HOME)
    if not anki("findCards", query=f'"deck:{STORY}"'):   # empty: the card is back home
        anki("deleteDecks", decks=[STORY], cardsToo=True)
    anki("guiDeckBrowser")
print("ok:", OUT)
