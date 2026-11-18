"""Video 3, "the book and the web, one deck", recorded from one real run: Wikipedia's Simpson's paradox selected
with the mouse and clipped as the extension clips it (its selection and the paragraph around it, to /clip/api/text);
sentmine's side-panel view (/clip) as the card arrives; in the book a drag over Simpson's reversal; Send to Anki; and
pages later the Wikipedia card coming back in the PDF. Uses record_tour.py's recorder.
python record_web.py <port> <out folder>"""
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "record_tour.py"), encoding="utf-8").read().split("# --- 1.")[0])   # Recorder, helpers, b

WIKI = "https://en.wikipedia.org/wiki/Simpson%27s_paradox"
DECK = "sentmine video"
book = b   # 1280×720 at 1.5×: the reading app

# --- the web page (1320×1080 in the frame) and the side panel (600×1080) ------------------------------------------
web = Recorder(880, 720)
web.cdp("Emulation.setDeviceMetricsOverride", width=880, height=720, deviceScaleFactor=1.5, mobile=False)
web.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
web.cdp("Page.navigate", url=WIKI)
web.wait("document.querySelectorAll('.mw-parser-output p').length > 3", 100)
time.sleep(1.5)
web.js(POINTER)
title = web.js("document.title")
first_p = "[...document.querySelectorAll('.mw-parser-output p')].find(p => p.textContent.trim().length > 80)"
web.js(f"{first_p}.scrollIntoView({{block: 'center'}})")
time.sleep(0.6)
x0, y0, x1, y1 = web.js(f"""(() => {{ const b = {first_p}.querySelector('b'); const r = document.createRange(); r.selectNodeContents(b);
    const rs = r.getClientRects(); const a = rs[0], z = rs[rs.length - 1]; return [a.left + 1, a.top + a.height / 2, z.right - 1, z.top + z.height / 2]; }})()""")
paragraph = web.js(f"(() => {{ const c = {first_p}.cloneNode(true); c.querySelectorAll('style, sup.reference').forEach(e => e.remove()); return c.textContent.trim(); }})()")

b = web
pointer[:] = [x0 + 260, y0 + 160]
web.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=pointer[0], y=pointer[1], buttons=0)
web.start("w1-web")
web.pump(0.6)
move(x0, y0, 0.9)
web.pump(0.15)
web.mouse("mousePressed", x0, y0)
move(x1, y1, 0.8, buttons=1)
web.mouse("mouseReleased", x1, y1)
selected = web.js("getSelection().toString()")
web.pump(2.6)
web.stop()
print("selected:", repr(selected), "| title:", title)

panel = Recorder(400, 720)
panel.cdp("Emulation.setDeviceMetricsOverride", width=400, height=720, deviceScaleFactor=1.5, mobile=False)
panel.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
panel.cdp("Page.navigate", url=BASE + "/clip")
panel.wait("document.readyState === 'complete'", 50)
time.sleep(1.2)
term = selected.strip()
at = paragraph.find(term)
body = {"text": term, "before": paragraph[max(0, at - 1200):at], "after": paragraph[at + len(term):at + len(term) + 1200],
        "source": {"title": title, "url": WIKI}}
panel.start("w2-panel")
panel.pump(0.8)
request = urllib.request.Request(BASE + "/clip/api/text", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(request).read()
panel.js("refreshIfChanged()")   # what the extension's "sentmine:refresh" message does right after a clip
for _ in range(40):
    panel.pump(0.1)
    if panel.js("document.querySelectorAll('#cards .card').length >= 1"):
        break
panel.pump(2.4)
panel.stop()
print("panel card:", [(c["front"], c["back"][:70]) for c in state()["cards"]])
web.close()
panel.close()

# --- the book: a drag over Simpson's reversal; the deck already holds the web card ---------------------------------
b = book
pointer[:] = [W * 0.8, H * 0.8]
open_pdf()
b.js(f"document.getElementById('deck-name').value = {json.dumps(DECK)}")
simpson = find("Strangely, the experimental data revealed")
s = simpson["sentence"]
first_term = next(p["word"] for p in simpson["pieces"] if "word" in p and p["text"].startswith("Simpson"))
show(4, s, 0.45)
start = word_box(4, s, first_term)
end = word_box(4, s, word_number(simpson, "reversal"), end=True)
b.cdp("Input.dispatchMouseEvent", type="mouseMoved", x=start[0] - 140, y=start[1] + 120, buttons=0)
pointer[:] = [start[0] - 140, start[1] + 120]
b.start("w3-book")
b.pump(0.6)
move(*start, 0.8)
b.pump(0.15)
b.mouse("mousePressed", *start)
move(*end, 1.0, buttons=1)
b.mouse("mouseReleased", *end)
b.wait("document.querySelectorAll('#cards .card').length >= 2", 100)
b.pump(0.6)
b.js("document.querySelector('#cards').lastElementChild.scrollIntoView({block: 'nearest'})")
b.pump(2.0)
b.stop()
print("book cards:", [c["front"] for c in state()["cards"]])

# --- both to Anki -------------------------------------------------------------------------------------------------
b.start("w4-send")
b.pump(0.4)
click(*centre("document.getElementById('send')"), 0.9)
b.wait("/Sent|added|Anki/.test(document.getElementById('status').textContent) && !document.getElementById('send').disabled", 150)
b.pump(2.4)
b.stop()
print("send:", b.js("document.getElementById('status').textContent")[:140])

# --- pages later in the book: the Wikipedia card comes back ----------------------------------------------------------
open_pdf()
again = find("Simpson’s paradox")
page = page_of(again)
show(page, again["sentence"], 0.40)
known = f"document.querySelectorAll('.pdf-page')[{page}].querySelector('.w.known[data-sentence=\"{again['sentence']}\"]')"
print("underlined:", b.js(f"!!{known}"), "page", page + 1)
b.start("w5-back")
b.pump(1.2)
move(*centre(known), 1.2)
b.wait("!document.getElementById('known-card').hidden", 30)
b.pump(3.2)
b.stop()
print("card:", b.js("document.getElementById('known-card').textContent")[:160])
b.close()
