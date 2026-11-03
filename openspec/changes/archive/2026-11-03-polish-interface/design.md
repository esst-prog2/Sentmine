## Context

The pages are two hand-written HTML files with their own CSS and no build step. They were looked at as screenshots from headless Edge at 1400 px wide, at 390 px wide in a frame (the narrowest common phone), and with an empty and a filled session. The guidance followed is Impeccable's "Operate" mode for app screens, read from its public repository (commit 9fadc41, Apache 2.0); the plugin itself was not installed.

## Goals / Non-Goals

**Goals:** the pages read well in both themes and on a phone; every control shows what it is doing; the two pages look like one app.

**Non-Goals:** new features; a new colour scheme, logo or font; a CSS file shared between the pages; changing any message.

## Decisions

**Keep the colours, fix the pairs that fail.** Every text and background pair is checked with the WCAG contrast formula by a small script; a pair below 4.5:1 is changed. A new colour `--on-accent` is used for text on the accent colour: white in light mode, near-black in dark mode.

**One focus ring for everything.** `:focus-visible` draws a 2 px accent outline 2 px outside the control. It is shown for the keyboard and not for mouse clicks, so it does not get in the way when clicking words.

**Busy controls are disabled and say so.** While a request is waiting, the button that sent it is disabled and its text changes ("Making the deck…", "Reading…"). It goes back when the answer comes, whether or not the request worked. "Suggest meaning" already did this.

**A list, not nested boxes.** The panel is already a box, so a card inside it is separated by a line instead of its own border. Impeccable lists nested cards among its things to avoid.

**The kind of card in plain words.** "Word" or "Definition" is shown in sentence case next to the card's buttons, and on My cards next to the date. Upper-case, spaced-out labels above content are another thing Impeccable avoids.

**The CSS stays in each page.** A shared stylesheet would need another route and package file for about 40 shared lines. The colour variables are kept the same in both files by hand.

## Risks / Trade-offs

- [The two pages' CSS can drift apart] -> Both are short; the colour variables are copied together.
- [Headless screenshots are not a real browser] -> The reader tries both pages in their own browser before the change is archived.
