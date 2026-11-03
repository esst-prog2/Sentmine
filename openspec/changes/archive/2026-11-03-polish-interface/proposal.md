## Why

The app works, but its two pages still look like a first draft. Going through them with the design guidance of Impeccable (pbakaus/impeccable, shown in session 7) found these problems:
- In dark mode the Download button has white text on light blue, at a contrast of about 2.4:1, where 4.5:1 is the minimum for reading.
- Buttons and text boxes do not change on hover, show no ring when reached with the keyboard, and do not look different while disabled.
- Download and "Read this text" give no sign that they are working.
- Cards are boxes inside a box, labelled with small upper-case words.
- The two pages have different headers.

The demos on 1 and 8 December show these pages, so they should look finished.

## What Changes

- Colours are checked for contrast in both light and dark mode, and the dark-mode main button gets dark text.
- Every button, link and text box gets hover, keyboard-focus and disabled looks. Download and "Read this text" say they are busy and cannot be pressed twice while waiting.
- The browser's own parts follow the theme: text selection, the file button, scroll bars and check marks.
- Cards are listed with a line between them instead of boxes inside a box. The kind of card is a plain word, not an upper-case label.
- Both pages share one header, with Read and My cards as links and the current page marked.
- The line "No text yet." is hidden while the paste box is open, because the box already says what to do.
- Small changes (150 ms) on hover only, and none for readers who ask the system for reduced motion.

This is a refinement, not a redesign. Behaviour, the server and the wording of messages are unchanged.

## Capabilities

### New Capabilities
- `page-design`: contrast in both themes, the states every control shows, the shared header, and the narrowest width the pages work at.

### Modified Capabilities

None.

## Impact

- `src/sentmine/web/index.html` and `src/sentmine/web/cards.html`, style and script only.
- No change to Python code or its tests.
