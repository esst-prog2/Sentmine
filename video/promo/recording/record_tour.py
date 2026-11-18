"""The product tour, recorded from one real run of sentmine: headless Edge's own screen frames (Page.startScreencast)
while a script moves a visible pointer and clicks. Each beat becomes an MP4 clip. Waiting for the model is shortened
(holds over 0.8 s cut to 0.8 s) only in the meaning beat, and the page says so.
python record_tour.py <port> <out folder>"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

import websocket

from cdp import Browser

port, out = sys.argv[1], sys.argv[2]
BASE = f"http://127.0.0.1:{port}"
PDF = "C:/Users/User/Downloads/Causal Inference in Statistics_ Solution M - Judea Pearl.pdf"
FFMPEG = "ffmpeg"
os.makedirs(out, exist_ok=True)
W, H = 1280, 720


class Recorder(Browser):
    frames = None   # [(timestamp, path)] while recording

    def handle(self, m):
        if m.get("method") == "Page.screencastFrame":
            p = m["params"]
            self.n += 1
            self.ws.send(json.dumps({"id": self.n, "method": "Page.screencastFrameAck", "params": {"sessionId": p["sessionId"]}}))
            if self.frames is not None:
                path = os.path.join(self.dir, f"{len(self.frames):05}.jpg")
                open(path, "wb").write(base64.b64decode(p["data"]))
                self.frames.append((p["metadata"]["timestamp"], path))

    def cdp(self, method, **params):
        self.n += 1
        mine = self.n
        self.ws.send(json.dumps({"id": mine, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mine:
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})
            self.handle(m)

    def pump(self, seconds):
        """Wait, taking in frames meanwhile."""
        end = time.time() + seconds
        self.ws.settimeout(0.05)
        try:
            while time.time() < end:
                try:
                    self.handle(json.loads(self.ws.recv()))
                except websocket.WebSocketTimeoutException:
                    pass
        finally:
            self.ws.settimeout(None)

    def start(self, name):
        self.dir = os.path.join(out, name)
        os.makedirs(self.dir, exist_ok=True)
        for f in os.listdir(self.dir):
            os.remove(os.path.join(self.dir, f))
        self.frames = []
        self.name = name
        self.cdp("Page.startScreencast", format="jpeg", quality=88, maxWidth=1920, maxHeight=1080, everyNthFrame=1)
        self.t0 = time.time()
        self.pump(0.4)

    def stop(self, cap=None):
        self.pump(0.3)
        self.cdp("Page.stopScreencast")
        frames, self.frames = self.frames, None
        end = frames[-1][0] + 0.3
        lines = []
        for i, (t, path) in enumerate(frames):
            hold = (frames[i + 1][0] if i + 1 < len(frames) else end) - t
            if cap:
                hold = min(hold, cap)
            lines.append(f"file '{os.path.basename(path)}'\nduration {max(hold, 0.001):.4f}")
        lines.append(f"file '{os.path.basename(frames[-1][1])}'")
        listing = os.path.join(self.dir, "list.txt")
        open(listing, "w").write("\n".join(lines) + "\n")
        clip = os.path.join(out, self.name + ".mp4")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                        "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18",
                        "-preset", "slow", "-an", clip], check=True)
        length = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
                                      capture_output=True, text=True).stdout)
        print(f"{self.name}: {len(frames)} frames, {length:.2f} s", flush=True)


b = Recorder(W, H)
b.cdp("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1.5, mobile=False)
b.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
pointer = [W * 0.8, H * 0.8]

POINTER = """(() => { if (document.getElementById('tour-pointer')) return;
  const p = document.createElement('div'); p.id = 'tour-pointer';
  p.innerHTML = '<svg width="26" height="34" viewBox="0 0 26 34"><path d="M2 2 L2 27 L8.5 21 L13 31.5 L17.5 29.5 L13 19.5 L22 19.5 Z" fill="#23201b" stroke="#fbf8f2" stroke-width="2" stroke-linejoin="round"/></svg>';
  p.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;transform:translate(-2px,-2px);transition:none';
  document.documentElement.appendChild(p);
  const ring = document.createElement('div'); ring.id = 'tour-ring';
  ring.style.cssText = 'position:fixed;width:36px;height:36px;margin:-18px 0 0 -18px;border-radius:50%;border:3px solid #c98a0b;z-index:2147483646;pointer-events:none;opacity:0';
  document.documentElement.appendChild(ring);
  addEventListener('mousemove', e => { p.style.left = e.clientX + 'px'; p.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', e => { ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px';
    ring.animate([{opacity: .9, transform: 'scale(.5)'}, {opacity: 0, transform: 'scale(1.4)'}], {duration: 450, easing: 'ease-out'}); }, true);
})()"""


def move(x, y, seconds=0.7, buttons=0):
    """The pointer glides there, easing in and out."""
    x0, y0 = pointer
    began = time.time()
    while True:   # paced by the clock: a slow page only means fewer steps, never a slower pointer
        t = min(1.0, (time.time() - began) / seconds)
        e = t * t * (3 - 2 * t)
        b.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=x0 + (x - x0) * e, y=y0 + (y - y0) * e,
              button="left" if buttons else "none", buttons=buttons)
        if t >= 1:
            break
        b.pump(1 / 30)
    pointer[:] = [x, y]


def click(x, y, glide=0.7):
    move(x, y, glide)
    b.pump(0.15)
    b.mouse("mousePressed", x, y)
    b.pump(0.08)
    b.mouse("mouseReleased", x, y)


def state():
    return json.loads(urllib.request.urlopen(BASE + "/api/state").read())


def open_pdf():
    subprocess.run(["curl", "-s", "-o", "NUL", "-F", f"file=@{PDF}", BASE + "/api/file"], check=True)
    b.cdp("Page.navigate", url=BASE + "/")
    b.wait("document.querySelectorAll('.pdf-page').length > 0")
    b.js(POINTER)
    b.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=pointer[0], y=pointer[1], buttons=0)


def find(text_part):
    for paragraph in state()["paragraphs"]:
        for drawn in paragraph:
            if text_part in "".join(piece["text"] for piece in drawn["pieces"]):
                return drawn
    raise SystemExit("not found: " + text_part)


def word_number(drawn, text):
    return next(p["word"] for p in drawn["pieces"] if p.get("text") == text)


def page_of(drawn):
    for i in range(75):
        b.js(f"document.querySelectorAll('.pdf-page')[{i}].scrollIntoView()")
        b.wait(f"document.querySelectorAll('.pdf-page')[{i}].querySelectorAll('.w').length > 0", 40)
        if b.js(f"!!document.querySelectorAll('.pdf-page')[{i}].querySelector('.w[data-sentence=\"{drawn['sentence']}\"]')"):
            return i
    raise SystemExit("page not found")


def show(index, sentence, at=0.42):
    b.js(f"document.querySelectorAll('.pdf-page')[{index}].scrollIntoView()")
    b.wait(f"document.querySelectorAll('.pdf-page')[{index}].querySelectorAll('.w').length > 20 && document.querySelectorAll('.pdf-page')[{index}].querySelector('img').complete")
    b.js(f"""(() => {{ const w = document.querySelectorAll('.pdf-page')[{index}].querySelector('.w[data-sentence="{sentence}"]');
        window.scrollBy(0, w.getBoundingClientRect().top - innerHeight * {at}); }})()""")
    b.pump(0.8)


def word_box(index, sentence, word, end=False):
    return b.js(f"""(() => {{ const w = document.querySelectorAll('.pdf-page')[{index}].querySelector('.w[data-sentence="{sentence}"][data-word="{word}"]');
        const r = w.getBoundingClientRect(); return [{'r.right - 2' if end else 'r.left + 3'}, r.top + r.height / 2]; }})()""")


def centre(expression):
    return b.js(f"(() => {{ const r = ({expression}).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")


def card_button(card, text):
    return f"[...document.querySelectorAll('#cards .card')[{card}].querySelectorAll('button')].find(e => e.textContent === {json.dumps(text)})"


# --- 1. a word on page 13: click it, a card ---------------------------------------------------------------------
open_pdf()
b.js("document.getElementById('deck-name').value = 'sentmine demo'")
coins = find("Two fair coins are flipped simultaneously")
show(12, coins["sentence"], 0.40)
x, y = word_box(12, coins["sentence"], word_number(coins, "simultaneously"))
b.start("1-click")
b.pump(1.0)
click(x + 30, y, 1.1)
b.wait("document.querySelectorAll('#cards .card').length >= 1", 100)
b.pump(1.8)
b.stop()

# --- 2. Suggest meaning (the real model; the wait shortened) ----------------------------------------------------
b.start("2-meaning")
b.pump(0.3)
click(*centre(card_button(0, "Suggest meaning")), 0.8)
for _ in range(300):
    b.pump(0.2)
    if b.js("[...document.querySelectorAll('#cards .back')].some(e => e.textContent.length > 140)"):
        break
b.pump(2.0)
b.stop(cap=0.8)
print("meaning:", repr(state()["cards"][0]["back"][-120:]))

# --- 3. a term: drag over it, a card at once; Make it cloze -----------------------------------------------------
simpson = find("Strangely, the experimental data revealed")
s = simpson["sentence"]
first_term = next(p["word"] for p in simpson["pieces"] if "word" in p and p["text"].startswith("Simpson"))
show(4, s, 0.45)
start = word_box(4, s, first_term)
end = word_box(4, s, word_number(simpson, "reversal"), end=True)
b.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=start[0] - 140, y=start[1] + 120, buttons=0)
pointer[:] = [start[0] - 140, start[1] + 120]
b.start("3-term")
b.pump(0.6)
move(*start, 0.8)
b.pump(0.15)
b.mouse("mousePressed", *start)
move(*end, 1.0, buttons=1)
b.mouse("mouseReleased", *end)
b.wait("document.querySelectorAll('#cards .card').length >= 2", 100)
b.pump(1.0)
b.js("document.querySelectorAll('#cards .card')[1].scrollIntoView({block: 'nearest'})")
click(*centre(card_button(1, "Make it cloze")), 0.9)
b.pump(1.8)
b.stop()

# --- 4. Send to Anki ---------------------------------------------------------------------------------------------
b.start("4-send")
b.pump(0.4)
click(*centre("document.getElementById('send')"), 0.9)
b.wait("/Sent|added|Anki/.test(document.getElementById('status').textContent) && !document.getElementById('send').disabled", 150)
b.pump(2.2)
b.stop()
print("send:", b.js("document.getElementById('status').textContent")[:120])

# --- 5. twelve pages later: the word is underlined; pointing at it shows its card -------------------------------
open_pdf()
again = find("simultaneously makes it uncomfortable")
page = page_of(again)
show(page, again["sentence"], 0.45)
known = f"document.querySelectorAll('.pdf-page')[{page}].querySelector('.w.known[data-sentence=\"{again['sentence']}\"]')"
print("underlined:", b.js(f"!!{known}"))
b.start("5-back")
b.pump(1.2)
move(*centre(known), 1.2)
b.wait("!document.getElementById('known-card').hidden", 30)
b.pump(2.6)
b.stop()
print("page", page + 1, "| card:", b.js("document.getElementById('known-card').textContent")[:100])
b.close()
