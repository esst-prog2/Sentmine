"""The product tour as ONE continuous take from a real run of sentmine, sharp enough to push in on: headless Edge's
own frames at 2560×1440 (1280×720 drawn at 2×), a drawn pointer, pages scrolled smoothly (no cuts). It logs
where each thing happens (the word, the card, the buttons, the popup) so the video's camera can follow it.
Only the wait for the AI meaning is shortened (holds over 0.6 s cut to 0.6 s there).
python record_tour2.py <port> <out folder> <deck>"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

import websocket

from cdp import Browser

port, out, DECK = sys.argv[1], sys.argv[2], sys.argv[3]
BASE = f"http://127.0.0.1:{port}"
PDF = "C:/Users/User/Downloads/Causal Inference in Statistics_ Solution M - Judea Pearl.pdf"
W, H, DPR = 1280, 720, 2.0
os.makedirs(out, exist_ok=True)
frames_dir = os.path.join(out, "frames")
os.makedirs(frames_dir, exist_ok=True)
for f in os.listdir(frames_dir):
    os.remove(os.path.join(frames_dir, f))


class Recorder(Browser):
    frames = None

    def handle(self, m):
        if m.get("method") == "Page.screencastFrame":
            p = m["params"]
            self.n += 1
            self.ws.send(json.dumps({"id": self.n, "method": "Page.screencastFrameAck", "params": {"sessionId": p["sessionId"]}}))
            if self.frames is not None:
                path = os.path.join(frames_dir, f"{len(self.frames):05}.jpg")
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
        end = time.time() + seconds
        self.ws.settimeout(0.03)
        try:
            while time.time() < end:
                try:
                    self.handle(json.loads(self.ws.recv()))
                except websocket.WebSocketTimeoutException:
                    pass
        finally:
            self.ws.settimeout(None)


b = Recorder(W, H)
b.cdp("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=DPR, mobile=False)
b.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
pointer = [W * 0.75, H * 0.8]
events = []   # (wall time, name, rect [x, y, w, h] in CSS px of the viewport)
shorten = []  # wall-time windows where holds are cut (the AI wait)

POINTER = """(() => { if (document.getElementById('tour-pointer')) return;
  const p = document.createElement('div'); p.id = 'tour-pointer';
  p.innerHTML = '<svg width="22" height="29" viewBox="0 0 26 34"><path d="M2 2 L2 27 L8.5 21 L13 31.5 L17.5 29.5 L13 19.5 L22 19.5 Z" fill="#23201b" stroke="#fbf8f2" stroke-width="2" stroke-linejoin="round"/></svg>';
  p.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;transform:translate(-2px,-2px)';
  document.documentElement.appendChild(p);
  const ring = document.createElement('div');
  ring.style.cssText = 'position:fixed;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #c98a0b;z-index:2147483646;pointer-events:none;opacity:0';
  document.documentElement.appendChild(ring);
  addEventListener('mousemove', e => { p.style.left = e.clientX + 'px'; p.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', e => { ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px';
    ring.animate([{opacity: .9, transform: 'scale(.5)'}, {opacity: 0, transform: 'scale(1.4)'}], {duration: 450, easing: 'ease-out'}); }, true);
})()"""


def mark(name, expression):
    rect = b.js(f"(() => {{ const r = ({expression}).getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }})()")
    events.append((b.js("Date.now() / 1000"), name, rect))   # the browser's clock, the clock its frames carry
    return rect


def move(x, y, seconds=0.7, buttons=0):
    x0, y0 = pointer
    began = time.time()
    while True:
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


def until(expression, seconds=20):
    end = time.time() + seconds
    while time.time() < end:
        if b.js(expression):
            return True
        b.pump(0.1)
    return False


def glide_scroll(to_y, seconds=1.4):
    """Scroll the page smoothly to `to_y`, frame by frame, so the video needs no cut."""
    y0 = b.js("scrollY")
    began = time.time()
    while True:
        t = min(1.0, (time.time() - began) / seconds)
        e = t * t * (3 - 2 * t)
        b.js(f"window.scrollTo(0, {y0 + (to_y - y0) * e})")
        if t >= 1:
            break
        b.pump(1 / 40)


def state():
    return json.loads(urllib.request.urlopen(BASE + "/api/state").read())


def find(text_part):
    for paragraph in state()["paragraphs"]:
        for drawn in paragraph:
            if text_part in "".join(piece["text"] for piece in drawn["pieces"]):
                return drawn
    raise SystemExit("not found: " + text_part)


def word_number(drawn, text):
    return next(p["word"] for p in drawn["pieces"] if p.get("text") == text)


def page_el(i):
    return f"document.querySelectorAll('.pdf-page')[{i}]"


def word_el(i, sentence, word):
    return f"{page_el(i)}.querySelector('.w[data-sentence=\"{sentence}\"][data-word=\"{word}\"]')"


def scroll_target(i, sentence, at):
    return b.js(f"(() => {{ const w = {page_el(i)}.querySelector('.w[data-sentence=\"{sentence}\"]'); return scrollY + w.getBoundingClientRect().top - innerHeight * {at}; }})()")


def centre(expression):
    return b.js(f"(() => {{ const r = ({expression}).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")


def card_button(card, text):
    return f"[...document.querySelectorAll('#cards .card')[{card}].querySelectorAll('button')].find(e => e.textContent === {json.dumps(text)})"


# --- set up: open the book, find the three places, let their pages draw ---------------------------------------
subprocess.run(["curl", "-s", "-o", "NUL", "-F", f"file=@{PDF}", BASE + "/api/file"], check=True)
b.cdp("Page.navigate", url=BASE + "/")
b.wait("document.querySelectorAll('.pdf-page').length > 0")
b.js(POINTER)
b.js(f"document.getElementById('deck-name').value = {json.dumps(DECK)}")
coins = find("Two fair coins are flipped simultaneously")
simpson = find("Strangely, the experimental data revealed")
again = find("simultaneously makes it uncomfortable")
page_again = None
for i in range(75):
    b.js(f"{page_el(i)}.scrollIntoView()")
    b.wait(f"{page_el(i)}.querySelectorAll('.w').length > 0", 40)
    if b.js(f"!!{page_el(i)}.querySelector('.w[data-sentence=\"{again['sentence']}\"]')"):
        page_again = i
        break
for i in (4, 12, page_again):   # draw the three pages now, so scrolling to them later shows them at once
    b.js(f"{page_el(i)}.scrollIntoView()")
    b.wait(f"{page_el(i)}.querySelectorAll('.w').length > 20 && {page_el(i)}.querySelector('img').complete", 60)
b.js(f"window.scrollTo(0, {scroll_target(12, coins['sentence'], 0.40)})")
b.pump(1.0)
b.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=pointer[0], y=pointer[1], buttons=0)

# --- the take -----------------------------------------------------------------------------------------------------
b.frames = []
b.cdp("Page.startScreencast", format="jpeg", quality=80, maxWidth=2560, maxHeight=1440, everyNthFrame=1)
take_start = time.time()
b.pump(0.6)
mark("overview", "document.querySelector('main')")
b.pump(0.9)

# 1. click a word: a card
word = word_el(12, coins["sentence"], word_number(coins, "simultaneously"))
mark("word", word)
x, y = centre(word)
click(x, y, 1.0)
until("document.querySelectorAll('#cards .card').length >= 1", 20)
b.pump(0.3)
mark("card", "document.querySelectorAll('#cards .card')[0]")
mark("word+card", "document.querySelector('main')")
b.pump(1.4)

# 2. Suggest meaning (the real model; the wait shortened)
mark("meaning-button", card_button(0, "Suggest meaning"))
click(*centre(card_button(0, "Suggest meaning")), 0.8)
wait_from = b.js("Date.now() / 1000")
until("[...document.querySelectorAll('#cards .back')].some(e => e.textContent.length > 140)", 60)
shorten.append((wait_from + 0.5, b.js("Date.now() / 1000")))
b.pump(0.3)
mark("meaning", "document.querySelectorAll('#cards .card')[0]")
b.pump(1.8)

# 3. to page 5, smoothly; drag over a term; Make it cloze
mark("scroll", "document.querySelector('main')")
glide_scroll(scroll_target(4, simpson["sentence"], 0.45), 1.6)
b.pump(0.4)
s = simpson["sentence"]
first_term = next(p["word"] for p in simpson["pieces"] if "word" in p and p["text"].startswith("Simpson"))
start_el, end_el = word_el(4, s, first_term), word_el(4, s, word_number(simpson, "reversal"))
r0, r1 = mark("term", start_el), mark("term-end", end_el)
start = [r0[0] + 2, r0[1] + r0[3] / 2]
end = [r1[0] + r1[2] - 2, r1[1] + r1[3] / 2]
move(*start, 0.9)
b.pump(0.15)
b.mouse("mousePressed", *start)
move(*end, 1.0, buttons=1)
b.mouse("mouseReleased", *end)
until("document.querySelectorAll('#cards .card').length >= 2", 20)
b.pump(0.3)
b.js("document.querySelectorAll('#cards .card')[1].scrollIntoView({block: 'nearest', behavior: 'smooth'})")
b.pump(0.9)
mark("term-card", "document.querySelectorAll('#cards .card')[1]")
b.pump(0.8)
mark("cloze-button", card_button(1, "Make it cloze"))
click(*centre(card_button(1, "Make it cloze")), 0.8)
until("!!document.querySelector('#cards .card.is-cloze')", 10)
b.pump(0.3)
mark("cloze-card", "document.querySelectorAll('#cards .card')[1]")
b.pump(1.6)

# 4. Send to Anki
mark("send", "document.getElementById('send')")
click(*centre("document.getElementById('send')"), 0.9)
until("/Sent|added|Anki/.test(document.getElementById('status').textContent) && !document.getElementById('send').disabled", 30)
b.pump(0.2)
mark("status", "document.getElementById('status')")
b.pump(2.0)
print("send:", b.js("document.getElementById('status').textContent")[:140], flush=True)

# 5. twelve pages on, smoothly: the word is underlined; pointing shows its card
mark("scroll2", "document.querySelector('main')")
glide_scroll(scroll_target(page_again, again["sentence"], 0.40), 1.8)
b.pump(0.5)
known = f"{page_el(page_again)}.querySelector('.w.known[data-sentence=\"{again['sentence']}\"]')"
print("underlined:", b.js(f"!!{known}"), "page", page_again + 1, flush=True)
mark("known", known)
move(*centre(known), 1.2)
until("!document.getElementById('known-card').hidden", 5)
b.pump(0.3)
mark("popup", "document.getElementById('known-card')")
b.pump(3.0)
mark("end", "document.querySelector('main')")
b.pump(0.3)
b.cdp("Page.stopScreencast")
frames = b.frames
b.close()

# --- one clip; holds inside the AI wait shortened; event times mapped onto the clip's own time -----------------------
offset = frames[0][0] - take_start   # Chrome's frame times against this script's clock (both wall clocks)
end_ts = frames[-1][0] + 0.3
lines, mapping, clip_t = [], [], 0.0
for i, (ts, path) in enumerate(frames):
    hold = (frames[i + 1][0] if i + 1 < len(frames) else end_ts) - ts
    if any(a <= ts <= z for a, z in shorten):
        hold = min(hold, 0.6)
    mapping.append((ts, clip_t, hold))
    lines.append(f"file '{os.path.basename(path)}'\nduration {max(hold, 0.001):.4f}")
    clip_t += max(hold, 0.001)
lines.append(f"file '{os.path.basename(frames[-1][1])}'")
listing = os.path.join(frames_dir, "list.txt")
open(listing, "w").write("\n".join(lines) + "\n")
clip = os.path.join(out, "tour.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                "-vf", "scale=2560:1440:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                "-an", clip], check=True)


def clip_time(at):
    """Where a moment of the take lands in the clip: its frame's place plus how far into that frame's hold."""
    shown = [m for m in mapping if m[0] <= at]
    if not shown:
        return 0.0
    ts0, c0, hold0 = shown[-1]
    return c0 + min(at - ts0, hold0)


log = [{"t": round(clip_time(t), 3), "name": name, "rect": [round(v * 1.5, 1) for v in rect]} for t, name, rect in events]
json.dump({"length": round(clip_t, 3), "events": log}, open(os.path.join(out, "tour.json"), "w"), indent=1)
print(f"tour: {len(frames)} frames, {clip_t:.2f} s", flush=True)
for e in log:
    print(f"  {e['t']:6.2f}  {e['name']:15} {e['rect']}")
