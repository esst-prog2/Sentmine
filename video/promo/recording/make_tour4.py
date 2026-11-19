"""The tour, book and web: a title card, then three takes from one real run (A the book, B the web page beside the
side panel, C the book again), each with a camera that follows the places the recorder logged, joined by a dip
through paper, then the end card. Times are each take's own (tk), turned into the film's: every take is played
1.15× faster after a trim at its start. python make_tour4.py <scratchpad> <out index.html>"""
import sys

S, OUT = sys.argv[1], sys.argv[2]
common = open(S + "/common_head.html", encoding="utf-8").read()
wordmark = open(S + "/look3/wordmark5.png.svg", encoding="utf-8").read()
SP = 1.15
TAKES = {   # name: (film start, trim at the take's start, length in the film)
    "a": (2.2, 0.9, 8.9),
    "b": (11.1, 0.9, 9.23),     # each take starts as the one before has gone: a dip, not a double exposure
    "c": (20.33, 0.4, 9.6),
}
END = round(TAKES["c"][0] + TAKES["c"][2], 2)
TOTAL = round(END + 2.0, 1)
PANEL_LAG = 0.419   # the panel's take began this much after the web page's


def t(take, tk):
    start, trim, _ = TAKES[take]
    return round(start + (tk - trim) / SP, 3)


# the camera, per take: (take time, x, y in the 1920×1080 picture, scale, move length in take seconds)
SHOTS = {
    "a": [(3.5, 1016, 430, 1.2, 0.9), (4.8, 1531, 463, 1.5, 0.9)],
    "b": [(1.0, 146, 340, 1.5, 0.9),                       # the term on Wikipedia
          (5.0 + PANEL_LAG, 1608, 820, 1.35, 1.0),          # the card arriving in the panel
          (6.7 + PANEL_LAG, 1608, 740, 1.6, 0.8)],          # Make it cloze
    "c": [(0.5, 1500, 100, 1.35, 0.8), (2.8, 420, 118, 1.35, 0.8),
          (4.6, 960, 540, 1.12, 1.3), (6.6, 828, 597, 1.6, 1.1)],
}
OPEN = {"a": (501, 440, 1.6), "b": (660, 540, 1.0), "c": (1300, 380, 1.1)}   # where each take opens
CAPTIONS = [
    ("c1", "a", "Click a word: a card, with its sentence.", 1.4, 4.7),
    ("c2", "a", "Ask what it means. You check it.", 4.8, 10.2),
    ("c3", "b", "On the web, select a term,", 1.0, 3.9),
    ("c4", "b", "right-click: <i>Make a card from this</i>.", 3.9, 6.6),
    ("c5", "b", "Make it cloze, right in the panel.", 6.8, 10.6),
    ("c6", "c", "Both go to Anki in one click.", 0.6, 4.6),
    ("c7", "c", "Pages later, <b>your card from the web</b> comes back.", 5.6, 11.4),
]
TAGS = [("tag-a", "a", "In your book"), ("tag-b", "b", "On the web"), ("tag-c", "c", "Back in your book")]

cameras = []
for take, shots in SHOTS.items():
    x, y, s = OPEN[take]
    cameras.append(f'      tl.set("#take-{take}", shot({x}, {y}, {s}), 0);')
    for tk, x, y, s, d in shots:
        cameras.append(f'      camera("#take-{take}", {t(take, tk)}, {x}, {y}, {s}, {round(d / SP, 2)});')
says = []
for cid, take, _, a, z in CAPTIONS:
    end = min(t(take, z), TAKES[take][0] + TAKES[take][2] - 0.35)
    says.append(f'      say("#{cid}", {t(take, a)}, {round(end, 3)});')
for tid, take, _ in TAGS:
    start, _, length = TAKES[take]
    says.append(f'      say("#{tid}", {round(start + 0.35, 2)}, {round(start + length - 0.3, 2)});')
dips = []
for take, (start, _, length) in TAKES.items():
    dips.append(f'      tl.fromTo("#take-{take}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "sine.out" }}, {start + 0.05});')
    dips.append(f'      tl.to("#take-{take}", {{ opacity: 0, duration: 0.3, ease: "sine.in" }}, {round(start + length - 0.3, 2)});')

caption_html = "\n".join(f'        <div class="caption" id="{c}">{text}</div>' for c, _, text, _, _ in CAPTIONS)
tag_html = "\n".join(f'        <div class="tag" id="{i}">{text}</div>' for i, _, text in TAGS)
a0, _, al = TAKES["a"]
b0, _, bl = TAKES["b"]
c0, _, cl = TAKES["c"]

html = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
{common}
      /* The product tour, book and web: a title card with a real crop of page 13, then three takes from one real run of
         sentmine recorded on 2026-11-19 at 3× (A the book; B Wikipedia's "Simpson's paradox", CC BY-SA 4.0, beside
         sentmine's side panel; C the book again), with a camera that follows the places the recorder logged
         (assets/tour/*.json). Each take is played 1.15× faster; the wait for the AI meaning was shortened in the
         recording; the browser's right-click menu cannot be recorded headless, so a caption names it. */
      /* a take's frame: not timed itself (its videos are), so the camera can move the web page and the panel as one */
      .take {{ opacity: 0; position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; z-index: 0; overflow: hidden; }}
      .take video {{ position: absolute; top: 0; height: 1080px; object-fit: fill; }}
      #take-a video, #take-c video {{ left: 0; width: 1920px; }}
      #web {{ left: 0; width: 1320px; }}
      #panel {{ left: 1320px; width: 600px; border-left: 3px solid var(--line); }}
      .caption {{ z-index: 2; }}
      .tag {{ z-index: 2; }}
      #tag-b {{ left: auto; right: 640px; }}   /* on the web: top right of the page, clear of its title */
      .credit {{ position: absolute; left: 36px; bottom: 22px; font: 28px/1 var(--ui); color: var(--soft); z-index: 2; opacity: 0; }}
      #s-title {{ background: var(--paper); z-index: 3; }}
      #s-title .kicker {{ position: absolute; left: 160px; top: 190px; font: 700 30px/1 var(--ui); letter-spacing: 0.12em;
        text-transform: uppercase; color: var(--soft); }}
      #s-title .ask {{ position: absolute; left: 160px; top: 250px; font: 500 128px/1.02 var(--serif); letter-spacing: -0.02em; }}
      #s-title .ask i {{ font-style: italic; background: var(--picked); border-radius: 12px; padding: 0 16px; }}
      #s-title .page {{ position: absolute; left: 160px; top: 560px; width: 1600px; background: #fff; border: 2px solid var(--line);
        border-radius: 20px; padding: 34px 42px; box-shadow: 0 2px 4px rgba(70, 52, 20, .08), 0 24px 60px rgba(70, 52, 20, .16); }}
      #s-title .page img {{ display: block; width: 1516px; height: auto; }}
      #s-title .page .mark {{ position: absolute; left: calc(42px + 1516px * 0.285); top: calc(34px + 1516px * 0.0465); width: calc(1516px * 0.152);
        height: calc(1516px * 0.026); background: rgba(248, 223, 122, 0.55); border-radius: 6px; mix-blend-mode: multiply; }}
      #s-title .credit2 {{ position: absolute; left: 160px; top: 930px; font: 28px/1.3 var(--ui); color: var(--soft); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">

      <div id="take-a" class="take">
        <video id="video-a" class="clip" src="assets/tour/a-book.mp4" muted playsinline data-start="{a0}" data-duration="{al}"></video>
      </div>
      <div id="take-b" class="take">
        <video id="web" class="clip" src="assets/tour/b-web.mp4" muted playsinline data-start="{b0}" data-duration="{bl}"></video>
        <video id="panel" class="clip" src="assets/tour/b-panel.mp4" muted playsinline data-start="{b0}" data-duration="{bl}"></video>
      </div>
      <div id="take-c" class="take">
        <video id="video-c" class="clip" src="assets/tour/c-book.mp4" muted playsinline data-start="{c0}" data-duration="{cl}"></video>
      </div>

      <div id="s-title" class="clip" data-start="0" data-duration="{a0 + 0.5}" data-track-index="2">
        <div class="outline" style="left: 1500px; top: 70px; width: 300px; height: 192px; transform: rotate(9deg);"></div>
        <div class="kicker">Page 13 of your course book</div>
        <div class="ask">A word you don’t know: <i>simultaneously</i>?</div>
        <div class="page"><img src="assets/tour/page13-sentence.png" alt="Study question 1.3.7 on page 13, as sentmine shows the PDF"><div class="mark"></div></div>
        <div class="credit2">The solution manual to Pearl, Glymour and Jewell, <i>Causal Inference in Statistics: A Primer</i>, in sentmine.</div>
      </div>

      <div id="words" class="clip" data-start="{a0}" data-duration="{round(END - a0, 2)}" data-track-index="0">
{caption_html}
{tag_html}
        <div class="credit" id="credit">Wikipedia, “Simpson’s paradox” (CC BY-SA 4.0) · beside it, sentmine’s side panel</div>
      </div>

      <div id="s-end" class="clip" data-start="{round(END - 0.6, 2)}" data-duration="{round(TOTAL - END + 0.6, 2)}" data-track-index="3" style="background: var(--paper); z-index: 4;">
        <div class="outline" style="left: 160px; top: 640px; width: 300px; height: 192px; transform: rotate(8deg);"></div>
        <div class="outline" style="left: 1480px; top: 140px; width: 320px; height: 205px; transform: rotate(-10deg);"></div>
        <div class="end-mark">{wordmark}</div>
        <div class="end-line">Your book and the web. One deck.</div>
        <div class="end-address">esst-prog2.github.io/Sentmine</div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const ease = "power3.out";

      tl.fromTo("#s-title .mark", {{ opacity: 0, scaleX: 0.2, transformOrigin: "0 50%" }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease }}, 0.5);
      tl.to("#s-title .outline", {{ y: 50, rotation: "+=4", duration: {a0 + 0.5}, ease: "none" }}, 0);
      tl.to("#s-title .kicker, #s-title .ask, #s-title .page, #s-title .credit2", {{ opacity: 0, duration: 0.3, ease: "sine.in" }}, {a0 - 0.3});
      tl.set("#s-title", {{ opacity: 0 }}, {a0 + 0.05});

      // a dip through paper between the takes: one goes, the next comes in
{chr(10).join(dips)}

      // the camera: frame a point at a scale, never showing past the picture's edge
      function shot(x, y, s) {{
        const clamp = (v, lo) => Math.min(0, Math.max(lo, v));
        return {{ scale: s, x: clamp(960 - x * s, 1920 - 1920 * s), y: clamp(540 - y * s, 1080 - 1080 * s) }};
      }}
      function camera(take, at, x, y, s, length) {{
        tl.to(take, Object.assign(shot(x, y, s), {{ duration: length, ease: "sine.inOut" }}), at);
      }}
{chr(10).join(cameras)}

      function say(selector, from, to) {{
        tl.fromTo(selector, {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.4, ease }}, from);
        tl.to(selector, {{ opacity: 0, duration: 0.25 }}, to - 0.25);
      }}
{chr(10).join(says)}
      tl.fromTo("#credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {b0 + 0.4});
      tl.to("#credit", {{ opacity: 0, duration: 0.25 }}, {round(b0 + bl - 0.35, 2)});

      tl.fromTo("#s-end", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "sine.out" }}, {round(END - 0.6, 2)});
      tl.fromTo("#s-end .end-mark", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.6, ease }}, {round(END - 0.45, 2)});
      tl.fromTo("#s-end .end-line", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease }}, {round(END - 0.3, 2)});
      tl.fromTo("#s-end .end-address", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease }}, {round(END - 0.15, 2)});
      tl.to("#s-end .outline", {{ y: 40, rotation: "+=3", duration: {round(TOTAL - END + 0.6, 2)}, ease: "none" }}, {round(END - 0.6, 2)});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
open(OUT, "w", encoding="utf-8", newline="\n").write(html)
print("total", TOTAL, "| takes", TAKES)
