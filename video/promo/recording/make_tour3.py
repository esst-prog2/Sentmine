"""The tour composition: a designed title card, then the one continuous take with a camera that follows the logged
places, then the end card. Times are the take's (tk), turned into the film's: the take is trimmed 0.9 s, played
1.12× and starts at 2.2 s. python make_tour3.py <scratchpad> <out index.html>"""
import sys

S, OUT = sys.argv[1], sys.argv[2]
common = open(S + "/common_head.html", encoding="utf-8").read()
wordmark = open(S + "/look3/wordmark5.png.svg", encoding="utf-8").read()
TRIM, SPEED, START = 0.9, 1.12, 2.2
TAKE = 27.533


def t(tk):
    return round(START + (tk - TRIM) / SPEED, 3)


END = round(START + TAKE, 3)          # the take's last frame in the film
TOTAL = round(END + 2.1, 1)           # the end card holds after it

# the camera: (take time, x, y in the 1920×1080 picture, scale, move length in take seconds)
SHOTS = [
    (3.35, 1016, 430, 1.2, 0.9),     # the word and its new card
    (4.6, 1531, 470, 1.5, 0.9),      # Suggest meaning, then the meaning
    (10.4, 960, 540, 1.12, 1.4),     # wider while the page scrolls to page 5
    (12.0, 659, 494, 1.7, 0.9),      # the drag over Simpson's reversal
    (14.6, 1090, 660, 1.15, 1.1),    # the term and its card
    (17.2, 1520, 829, 1.45, 0.9),    # Make it cloze
    (20.9, 1500, 100, 1.35, 0.9),    # Send to Anki
    (23.1, 711, 118, 1.35, 0.9),     # its status line
    (25.3, 960, 540, 1.12, 1.3),     # wider while the page scrolls to page 25
    (27.3, 817, 580, 1.6, 1.1),      # the underlined word and its card
]
CAPTIONS = [
    ("c1", "Click it: a card, with its sentence.", 2.0, 5.0),
    ("c2", "Ask what it means. You check it.", 5.0, 10.5),
    ("c3", "A term? Drag over it.", 11.8, 16.6),
    ("c4", "Or hide it: a cloze card.", 16.9, 21.2),
    ("c5", "One click puts them in Anki.", 21.4, 25.4),
    ("c6", "Twelve pages later, <b>your card comes back</b>.", 26.6, 31.6),
]
camera = "\n".join(f"      camera({t(tk)}, {x}, {y}, {s}, {round(d / SPEED, 2)});" for tk, x, y, s, d in SHOTS)
says = "\n".join(f'      say("#{i}", {t(a)}, {min(t(z), END - 0.1)});' for i, _, a, z in CAPTIONS)
caption_html = "\n".join(f'        <div class="caption" id="{i}">{text}</div>' for i, text, _, _ in CAPTIONS)

html = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
{common}
      /* The product tour: a title card with a real crop of page 13, then ONE continuous take recorded on 2026-11-18
         from a real run of sentmine at 3840×2160, with a camera that follows the places the recorder logged
         (assets/tour/tour.json). The take is trimmed 0.9 s at its start and played 1.12× faster; the wait for the AI
         meaning was already shortened in the recording; the caption under the video on the page says so. */
      #take {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; object-fit: fill; z-index: 0; }}
      .caption {{ z-index: 2; }}
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
      #s-title .credit {{ position: absolute; left: 160px; top: 930px; font: 28px/1.3 var(--ui); color: var(--soft); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">

      <video id="take" class="clip" src="assets/tour/tour.mp4" muted playsinline data-start="{START}" data-duration="{TAKE}" data-track-index="1"></video>

      <div id="s-title" class="clip" data-start="0" data-duration="{START + 0.5}" data-track-index="2">
        <div class="outline" style="left: 1500px; top: 70px; width: 300px; height: 192px; transform: rotate(9deg);"></div>
        <div class="kicker">Page 13 of your course book</div>
        <div class="ask">A word you don’t know: <i>simultaneously</i>?</div>
        <div class="page"><img src="assets/tour/page13-sentence.png" alt="Study question 1.3.7 on page 13, as sentmine shows the PDF"><div class="mark"></div></div>
        <div class="credit">The solution manual to Pearl, Glymour and Jewell, <i>Causal Inference in Statistics: A Primer</i>, in sentmine.</div>
      </div>

      <div id="captions" class="clip" data-start="{START}" data-duration="{TAKE}" data-track-index="0">
{caption_html}
      </div>

      <div id="s-end" class="clip" data-start="{round(END - 0.6, 2)}" data-duration="{round(TOTAL - END + 0.6, 2)}" data-track-index="3" style="background: var(--paper); z-index: 4;">
        <div class="outline" style="left: 160px; top: 640px; width: 300px; height: 192px; transform: rotate(8deg);"></div>
        <div class="outline" style="left: 1480px; top: 140px; width: 320px; height: 205px; transform: rotate(-10deg);"></div>
        <div class="end-mark">{wordmark}</div>
        <div class="end-line">Click a word, get an Anki card.</div>
        <div class="end-address">esst-prog2.github.io/Sentmine</div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const ease = "power3.out";

      // the title card: on screen from the first frame; the page's word marked as it will be clicked
      tl.fromTo("#s-title .mark", {{ opacity: 0, scaleX: 0.2, transformOrigin: "0 50%" }}, {{ opacity: 1, scaleX: 1, duration: 0.5, ease }}, 0.5);
      tl.to("#s-title .outline", {{ y: 50, rotation: "+=4", duration: {START + 0.5}, ease: "none" }}, 0);
      // a dip through paper, not a double exposure: the title goes, then the take comes in on the same sentence
      tl.to("#s-title .kicker, #s-title .ask, #s-title .page, #s-title .credit", {{ opacity: 0, duration: 0.3, ease: "sine.in" }}, {START - 0.3});
      tl.fromTo("#take", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "sine.out" }}, {START + 0.05});
      tl.set("#s-title", {{ opacity: 0 }}, {START + 0.05});

      // the camera: frame a point at a scale, never showing past the picture's edge
      function shot(x, y, s) {{
        const clamp = (v, lo) => Math.min(0, Math.max(lo, v));
        return {{ scale: s, x: clamp(960 - x * s, 1920 - 1920 * s), y: clamp(540 - y * s, 1080 - 1080 * s) }};
      }}
      function camera(at, x, y, s, length) {{
        tl.to("#take", Object.assign(shot(x, y, s), {{ duration: length, ease: "sine.inOut" }}), at);
      }}
      tl.set("#take", shot(501, 440, 1.6), 0);   // the take opens on the same sentence as the title card
{camera}

      function say(selector, from, to) {{
        tl.fromTo(selector, {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.4, ease }}, from);
        tl.to(selector, {{ opacity: 0, duration: 0.25 }}, to - 0.25);
      }}
{says}

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
print("total", TOTAL, "take ends", END)
