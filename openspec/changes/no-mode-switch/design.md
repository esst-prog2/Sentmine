## Context

`web/index.html` keeps `mode` ("word" or "definition"). In Word mode a `click` on a word span posts `/api/word`. In Definition mode a `mouseup` with a selection inside the text sets `term`, and the next one posts `/api/definition` with `term` and the selection as the passage.

## Goals / Non-Goals

**Goals:** both kinds of card without a switch; no change on the server.

**Non-Goals:** keyboard picking; a passage-first order; guessing the term from a passage.

## Decisions

**One `mouseup` handler decides.** `mouseup` fires before `click`, and the drag handler clears the selection, so a separate `click` handler would see an empty selection and also make a word card after every drag inside one word. One handler on the document looks at the selection: text selected inside the reading panel is a drag; no selection on a word span is a click. It listens on the document because a drag may end outside the text.

**Double- and triple-clicks are clicks.** The browser selects a word on double-click and a paragraph on triple-click. A `mouseup` with `event.detail >= 2` clears the selection and does nothing more, so a double-click behaves like the single click it starts with (one word card), and an accidental triple-click does not choose a paragraph as a term. A one-word term is chosen by dragging across the word.

**A click cancels a waiting term.** If a term is waiting and the reader clicks a word, the word card is made and the term is dropped. Keeping the term while also making a word card would leave two things in progress, and the status line can show only one message.

**Esc and Cancel drop the term.** The status line already names the term with a Cancel button; Esc does the same.

## Risks / Trade-offs

- [A drag meant only to select or copy text now chooses a term] -> The status line names it at once with Cancel, and Esc cancels; nothing is made until a second drag.
- [A one-word term needs a drag, not a click] -> Said in the hint on the page.
- [Touch screens] -> Untested; a tap is a click, and a long-press selection may or may not end with `mouseup`. The page was not built for touch before either.
