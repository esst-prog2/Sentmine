"""The product tour, book and web, recorded from one real run of sentmine in three continuous takes at 3×:
  A  the book: click "simultaneously", Suggest meaning (the real model; only its wait is shortened);
  B  the web: Wikipedia's "Simpson's paradox" selected with the mouse and clipped as the extension clips it
     (selection and its paragraph, to /clip/api/text), the card arriving in sentmine's side-panel view beside it,
     "Make it cloze" clicked in the panel; web and panel are recorded side by side, at the same moments;
  C  the book again: Send to Anki (both cards), a smooth scroll to page 48, where the Wikipedia card comes back.
Each take is one MP4 and a log of where each thing happens, for the video's camera.
python record_tour3.py <port> <out folder> <deck>"""
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
WIKI = "https://en.wikipedia.org/wiki/Simpson%27s_paradox"
DPR = 3.0
os.makedirs(out, exist_ok=True)

POINTER = """(() => { if (document.getElementById('tour-pointer')) return;
  const p = document.createElement('div'); p.id = 'tour-pointer';
  p.innerHTML = '<svg width="22" height="29" viewBox="0 0 26 34"><path d="M2 2 L2 27 L8.5 21 L13 31.5 L17.5 29.5 L13 19.5 L22 19.5 Z" fill="#23201b" stroke="#fbf8f2" stroke-width="2" stroke-linejoin="round"/></svg>';
  p.style.cssText = 'position:fixed;left:-40px;top:-40px;z-index:2147483647;pointer-events:none;transform:translate(-2px,-2px)';
  document.documentElement.appendChild(p);
  const ring = document.createElement('div');
  ring.style.cssText = 'position:fixed;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #c98a0b;z-index:2147483646;pointer-events:none;opacity:0';
  document.documentElement.appendChild(ring);
  addEventListener('mousemove', e => { p.style.left = e.clientX + 'px'; p.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', e => { ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px';
    ring.animate([{opacity: .9, transform: 'scale(.5)'}, {opacity: 0, transform: 'scale(1.4)'}], {duration: 450, easing: 'ease-out'}); }, true);
})()"""


class Recorder(Browser):
    """A browser whose screen frames are kept while a take runs, with a log of where things happen."""

    def __init__(self, w, h):
        super().__init__(w, h)
        self.cdp("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=DPR, mobile=False)
        self.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        self.size = (int(w * DPR), int(h * DPR))
        self.frames, self.events, self.shorten, self.pointer = None, [], [], [w * 0.75, h * 0.8]

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

    def now(self):
        return self.js("Date.now() / 1000")

    def mark(self, name, expression):
        rect = self.js(f"(() => {{ const r = ({expression}).getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }})()")
        self.events.append((self.now(), name, rect))
        return rect

    def start(self, name):
        self.dir = os.path.join(out, name)
        os.makedirs(self.dir, exist_ok=True)
        for f in os.listdir(self.dir):
            os.remove(os.path.join(self.dir, f))
        self.name, self.frames, self.events, self.shorten = name, [], [], []
        self.cdp("Page.startScreencast", format="jpeg", quality=82, maxWidth=self.size[0], maxHeight=self.size[1], everyNthFrame=1)
        self.began = self.now()
        self.pump(0.4)

    def stop(self, hold=0.0):
        """The take as one MP4 (holds in `shorten` cut to 0.6 s) and its log, in the clip's own time."""
        self.pump(0.2)
        ended = self.now() + hold
        self.cdp("Page.stopScreencast")
        frames, self.frames = self.frames, None
        lines, mapping, clip_t = [], [], 0.0
        for i, (ts, path) in enumerate(frames):
            hold_ = (frames[i + 1][0] if i + 1 < len(frames) else ended) - ts
            if any(a <= ts <= z for a, z in self.shorten):
                hold_ = min(hold_, 0.6)
            hold_ = max(hold_, 0.001)
            mapping.append((ts, clip_t, hold_))
            lines.append(f"file '{os.path.basename(path)}'\nduration {hold_:.4f}")
            clip_t += hold_
        lines.append(f"file '{os.path.basename(frames[-1][1])}'")
        listing = os.path.join(self.dir, "list.txt")
        open(listing, "w").write("\n".join(lines) + "\n")
        clip = os.path.join(out, self.name + ".mp4")
        w, h = self.size
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                        "-vf", f"scale={w}:{h}:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                        "-an", clip], check=True)

        def at(moment):
            shown = [m for m in mapping if m[0] <= moment]
            if not shown:
                return round(max(0.0, moment - frames[0][0]), 3)
            ts0, c0, h0 = shown[-1]
            return round(c0 + min(moment - ts0, h0), 3)
        log = {"length": round(clip_t, 3), "css_size": [self.size[0] / DPR, self.size[1] / DPR], "began": self.began,
               "events": [{"t": at(t), "wall": t, "name": n, "rect": r} for t, n, r in self.events]}
        json.dump(log, open(os.path.join(out, self.name + ".json"), "w"), indent=1)
        print(f"{self.name}: {len(frames)} frames, {clip_t:.2f} s", flush=True)
        for e in log["events"]:
            print(f"   {e['t']:6.2f}  {e['name']:14} {[round(v) for v in e['rect']]}", flush=True)
        return log

    def move(self, x, y, seconds=0.7, buttons=0):
        x0, y0 = self.pointer
        began = time.time()
        while True:
            t = min(1.0, (time.time() - began) / seconds)
            e = t * t * (3 - 2 * t)
            self.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=x0 + (x - x0) * e, y=y0 + (y - y0) * e,
                     button="left" if buttons else "none", buttons=buttons)
            if t >= 1:
                break
            self.pump(1 / 30)
        self.pointer = [x, y]

    def click(self, x, y, glide=0.7):
        self.move(x, y, glide)
        self.pump(0.15)
        self.mouse("mousePressed", x, y)
        self.pump(0.08)
        self.mouse("mouseReleased", x, y)

    def until(self, expression, seconds=20):
        end = time.time() + seconds
        while time.time() < end:
            if self.js(expression):
                return True
            self.pump(0.1)
        return False

    def centre(self, expression):
        return self.js(f"(() => {{ const r = ({expression}).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")

    def glide_scroll(self, to_y, seconds=1.6):
        y0 = self.js("scrollY")
        began = time.time()
        while True:
            t = min(1.0, (time.time() - began) / seconds)
            e = t * t * (3 - 2 * t)
            self.js(f"window.scrollTo(0, {y0 + (to_y - y0) * e})")
            if t >= 1:
                break
            self.pump(1 / 40)


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


def card_button(card, text):
    return f"[...document.querySelectorAll('#cards .card')[{card}].querySelectorAll('button')].find(e => e.textContent === {json.dumps(text)})"


# --- the book, ready: pages 13 and 48 drawn ---------------------------------------------------------------------------
book = Recorder(1280, 720)
subprocess.run(["curl", "-s", "-o", "NUL", "-F", f"file=@{PDF}", BASE + "/api/file"], check=True)
book.cdp("Page.navigate", url=BASE + "/")
book.wait("document.querySelectorAll('.pdf-page').length > 0")
book.js(POINTER)
book.js(f"document.getElementById('deck-name').value = {json.dumps(DECK)}")
coins = find("Two fair coins are flipped simultaneously")
paradox = find("Simpson’s paradox")
page_paradox = None
for i in range(75):
    book.js(f"{page_el(i)}.scrollIntoView()")
    book.wait(f"{page_el(i)}.querySelectorAll('.w').length > 0", 40)
    if book.js(f"!!{page_el(i)}.querySelector('.w[data-sentence=\"{paradox['sentence']}\"]')"):
        page_paradox = i
        break
for i in (12, page_paradox):
    book.js(f"{page_el(i)}.scrollIntoView()")
    book.wait(f"{page_el(i)}.querySelectorAll('.w').length > 20 && {page_el(i)}.querySelector('img').complete", 60)


def scroll_target(i, sentence, at):
    return book.js(f"(() => {{ const w = {page_el(i)}.querySelector('.w[data-sentence=\"{sentence}\"]'); return scrollY + w.getBoundingClientRect().top - innerHeight * {at}; }})()")


book.js(f"window.scrollTo(0, {scroll_target(12, coins['sentence'], 0.40)})")
book.pump(1.0)
book.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=book.pointer[0], y=book.pointer[1], buttons=0)

# --- A: the book: a word, its card, its meaning ------------------------------------------------------------------------
book.start("a-book")
book.pump(0.8)
word = f"{page_el(12)}.querySelector('.w[data-sentence=\"{coins['sentence']}\"][data-word=\"{word_number(coins, 'simultaneously')}\"]')"
book.mark("word", word)
book.click(*book.centre(word), 1.0)
book.until("document.querySelectorAll('#cards .card').length >= 1", 20)
book.pump(0.3)
book.mark("card", "document.querySelectorAll('#cards .card')[0]")
book.pump(1.3)
book.mark("meaning-button", card_button(0, "Suggest meaning"))
book.click(*book.centre(card_button(0, "Suggest meaning")), 0.8)
wait_from = book.now()
book.until("[...document.querySelectorAll('#cards .back')].some(e => e.textContent.length > 140)", 60)
book.shorten.append((wait_from + 0.5, book.now()))
book.pump(0.3)
book.mark("meaning", "document.querySelectorAll('#cards .card')[0]")
book.pump(1.8)
log_a = book.stop()

# --- B: the web page and the side panel, side by side, recorded at the same moments ---------------------------------
web = Recorder(880, 720)
web.cdp("Page.navigate", url=WIKI)
web.wait("document.querySelectorAll('.mw-parser-output p').length > 3", 100)
time.sleep(1.5)
web.js(POINTER)
title = web.js("document.title")
first_p = "[...document.querySelectorAll('.mw-parser-output p')].find(p => p.textContent.trim().length > 80)"
web.js(f"{first_p}.scrollIntoView({{block: 'center'}})")
web.pump(0.6)
x0, y0, x1, y1 = web.js(f"""(() => {{ const b = {first_p}.querySelector('b'); const r = document.createRange(); r.selectNodeContents(b);
    const rs = r.getClientRects(); const a = rs[0], z = rs[rs.length - 1]; return [a.left + 1, a.top + a.height / 2, z.right - 1, z.top + z.height / 2]; }})()""")
paragraph = web.js(f"(() => {{ const c = {first_p}.cloneNode(true); c.querySelectorAll('style, sup.reference').forEach(e => e.remove()); return c.textContent.trim(); }})()")
panel = Recorder(400, 720)
panel.cdp("Page.navigate", url=BASE + "/clip")
panel.wait("document.readyState === 'complete'", 50)
time.sleep(1.2)
panel.js(POINTER)
panel.pointer = [330, 650]
web.pointer = [x0 + 260, y0 + 160]
web.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=web.pointer[0], y=web.pointer[1], buttons=0)
# the panel's drawn pointer starts off-screen (left: -40px) until it moves: the pointer starts on the web page

web.start("b-web")
panel.start("b-panel")
offset = panel.now() - web.now()   # the panel's clock against the web page's: one machine, so about 0
web.pump(0.6)
web.mark("term", f"{first_p}.querySelector('b')")
web.move(x0, y0, 0.9)
web.pump(0.15)
web.mouse("mousePressed", x0, y0)
web.move(x1, y1, 0.8, buttons=1)
web.mouse("mouseReleased", x1, y1)
selected = web.js("getSelection().toString()").strip()
web.pump(0.5)
at = paragraph.find(selected)
body = {"text": selected, "before": paragraph[max(0, at - 1200):at], "after": paragraph[at + len(selected):at + len(selected) + 1200],
        "source": {"title": title, "url": WIKI}}
request = urllib.request.Request(BASE + "/clip/api/text", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(request).read()
panel.js("refreshIfChanged()")   # what the extension's "sentmine:refresh" message does right after a clip
panel.until("document.querySelectorAll('#cards .card').length >= 2", 10)   # the deck: the book's card, then the new one
panel.js(f"(() => {{ const c = [...document.querySelectorAll('#cards .card')].filter(c => /Simpson/.test(c.textContent)).pop(); c.scrollIntoView({{block: 'nearest'}}); }})()")
panel.pump(0.6)
new_card = "[...document.querySelectorAll('#cards .card')].filter(c => /Simpson/.test(c.textContent)).pop()"
panel.mark("panel-card", new_card)
web.pump(0.05)
panel.pump(1.0)
# the pointer leaves the web page and goes to the panel's Make it cloze
web.move(879, web.pointer[1], 0.35)   # to the web page's right edge, then on in the panel
web.js("document.getElementById('tour-pointer').style.left = '-40px'")
cloze = f"[...({new_card}).querySelectorAll('button')].find(e => e.textContent === 'Make it cloze')"
panel.js("refreshIfChanged()")   # awaited: the panel has drawn its cards for this deck, and will not redraw them under the click
panel.js(f"({new_card}).scrollIntoView({{block: 'start'}})")   # its buttons clear of the panel's bottom bar (Send to Anki)
panel.pump(0.3)
cx, cy = panel.centre(cloze)   # measured now, the card standing still
under = panel.js(f"(() => {{ const e = document.elementFromPoint({cx}, {cy}); return e ? e.textContent : ''; }})()")
assert under == "Make it cloze", f"not clicking: under the pointer is {under!r}"   # never a stray click (it once pressed Send)
panel.pointer = [0, cy - 60]
panel.mark("cloze-button", cloze)
panel.click(cx, cy, 0.7)
panel.until(f"({new_card}).classList.contains('is-cloze')", 10)
panel.pump(0.3)
panel.mark("cloze-card", new_card)
assert panel.js(f"({new_card}).classList.contains('is-cloze')") and not panel.js("[...document.querySelectorAll('#cards .card')].filter(c => /simultaneously/.test(c.textContent) && !/Simpson/.test(c.textContent))[0].classList.contains('is-cloze')"), "the wrong card became cloze"
panel.pump(1.8)
log_web = web.stop(hold=0.0)
log_panel = panel.stop(hold=0.0)
print("web/panel start offset:", round(log_panel["began"] - log_web["began"] - offset, 3), "| selected:", repr(selected))
web.close()
panel.close()

# --- C: the book again: send both, then pages later the card from the web comes back --------------------------------------
book.js("refreshIfChanged()")
book.until("document.querySelectorAll('#cards .card').length >= 2", 10)
book.pump(0.5)
book.js("document.querySelector('#cards').scrollTop = 0")
book.start("c-book")
book.pump(0.5)
book.mark("cards", "document.querySelector('#cards')")
book.mark("send", "document.getElementById('send')")
book.click(*book.centre("document.getElementById('send')"), 0.9)
book.until("/Sent|added|Anki/.test(document.getElementById('status').textContent) && !document.getElementById('send').disabled", 30)
book.pump(0.2)
book.mark("status", "document.getElementById('status')")
book.pump(1.8)
print("send:", book.js("document.getElementById('status').textContent")[:140], flush=True)
book.mark("scroll", "document.querySelector('main')")
book.glide_scroll(scroll_target(page_paradox, paradox["sentence"], 0.40), 1.8)
book.pump(0.5)
known = f"{page_el(page_paradox)}.querySelector('.w.known[data-sentence=\"{paradox['sentence']}\"]')"
print("underlined:", book.js(f"!!{known}"), "page", page_paradox + 1, flush=True)
book.mark("known", known)
book.move(*book.centre(known), 1.2)
book.until("!document.getElementById('known-card').hidden", 5)
book.pump(0.3)
book.mark("popup", "document.getElementById('known-card')")
book.pump(3.0)
log_c = book.stop(hold=0.0)
print("popup says:", book.js("document.getElementById('known-card').textContent")[:160])
book.close()
