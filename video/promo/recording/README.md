# Recording the tour

The five clips in `../assets/tour/` were recorded from one real run of sentmine on 2026-11-18:
headless Edge's own screen frames (DevTools `Page.startScreencast`) while `record_tour.py`
moves a drawn pointer and clicks. The app ran with an empty card memory and Suggest meaning on;
Anki was open with AnkiConnect.

    python record_tour.py <port of a running sentmine> <out folder>

Needs `websocket-client`, Microsoft Edge and FFmpeg. Only the wait for the AI meaning is
shortened (holds over 0.8 s cut to 0.8 s); the video says so. The PDF path at the top is the
solution manual to Pearl, Glymour and Jewell, which is not in the repo (copyrighted).
