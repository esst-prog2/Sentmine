## Context

A definition card is a `Flashcard` with the term as `front` and the passage as `back`. `deck.write_notes` and `anki.send_notes` take (front, back) pairs and always use the one sentmine note type. Anki cloze cards need a note type of the cloze kind, whose first field holds text with `{{c1::...}}` around the hidden part.

## Goals / Non-Goals

**Goals:** cloze cards from the definitions the reader already marks; the same cards by Download and by Send; no change to the memory.

**Non-Goals:** several gaps per card; cloze from word cards; letting the reader choose what to hide other than the term.

## Decisions

**A flag, not a new kind.** A cloze card keeps `kind = definition`, with `cloze = True`. The memory, the earlier-card check and My cards see a definition with its term and passage, as before. Only how the card is shown and written changes.

**The term is found as a whole word, ignoring case.** `(?<!\w)term(?!\w)` with the term escaped, so "variance" matches "Variance" but not "covariance". Every match is hidden, all as `c1`, so one card asks for the term once.

**The default follows the passage.** A new card is cloze if the term is in the passage; otherwise there is nothing to hide. Turning cloze on for a card whose term is not in the passage is refused with a message. An edit that removes the term turns cloze off.

**A second note type with a fixed id.** "sentmine: cloze", id 1766200418, fields Text and Back Extra, with the template `{{cloze:Text}}` and `{{cloze:Text}}<br>{{Back Extra}}`. Back Extra is left empty. Like the first note type, its id never changes, so imports land in the same type.

**`deck.Note` says which type a note is.** `Note(fields, cloze=False)`. `write_notes` and `send_notes` still accept (front, back) pairs, so the first design's command line and older tests are unchanged.

**Duplicates across both types.** `send_notes` reads the first field of the sentmine notes of both types in the deck, and skips a note whose first field is exactly the same. A cloze card and a term → passage card for the same term differ, so switching and sending again adds the other kind. That is wanted: the reader changed the card.

**The preview shows the card as Anki will.** Front: the passage with `[...]` for the term; back: the passage with the term in bold.

## Risks / Trade-offs

- [A passage containing `}}` could confuse Anki's cloze markup] -> Rare in prose; it would show wrongly in Anki, and the reader can switch the card to term → passage.
- [A term written differently in the passage, such as a plural] -> It is not found, so the card starts as term → passage; the reader can edit the passage or the term.
