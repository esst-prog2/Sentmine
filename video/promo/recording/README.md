# Recording the tour

The five clips in `../assets/tour/` were recorded from one real run of sentmine on 2026-11-18:
headless Edge's own screen frames (DevTools `Page.startScreencast`) while `record_tour.py`
moves a drawn pointer and clicks. The app ran with an empty card memory and Suggest meaning on;
Anki was open with AnkiConnect.

    python record_tour.py <port of a running sentmine> <out folder>

Needs `websocket-client`, Microsoft Edge and FFmpeg. Only the wait for the AI meaning is
shortened (holds over 0.8 s cut to 0.8 s); the video says so. The PDF path at the top is the
solution manual to Pearl, Glymour and Jewell, which is not in the repo (copyrighted).

## The two other videos (`../../story`, `../../web`)

- `record_web.py` records "your book and the web, one deck": Wikipedia's *Simpson's paradox* selected with the
  mouse and clipped as the extension clips it, sentmine's side-panel view as the card arrives, a drag in the book,
  Send to Anki, and the Wikipedia card coming back on page 48. Headless Edge cannot show its own right-click menu,
  so the video names it in a caption.
- `record_anki.py` records Anki asking a card, through AnkiConnect, with `winshot.py`: Windows' PrintWindow, so
  the window draws itself (copying the screen gave only the lock screen). The card is reset to new, moved into a
  deck of its own for the review, and moved back.
