---
name: sentmine promo page
description: One static page that shows sentmine at work, dressed in sentmine's own reading-app interface (warm paper, Newsreader, the wordmark).
colors:
  paper: "#f3eee4"
  panel: "#fbf8f2"
  ink: "#23201b"
  soft-ink: "#645d52"
  hairline: "#e2dbcc"
  hover-wash: "#ebe4d5"
  link-blue: "#2d6f8e"
  link-blue-deep: "#235a74"
  on-accent: "#ffffff"
  ink-button: "#1f232a"
  ink-button-hover: "#343a44"
  on-ink-button: "#fbf8f2"
  picked-yellow: "#f8df7a"
  marker: "#f6d84e"
  pick-amber: "#c98a0b"
  cloze: "#a63a12"
  cloze-wash: "#fbe2d4"
  selection: "#f5e6a3"
typography:
  display:
    fontFamily: "Newsreader, Georgia, \"Times New Roman\", serif"
    fontSize: "clamp(2rem, 4.6vw, 3.5rem)"
    fontWeight: 500
    lineHeight: 1.08
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Newsreader, Georgia, \"Times New Roman\", serif"
    fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Newsreader, Georgia, \"Times New Roman\", serif"
    fontSize: "1.45rem"
    fontWeight: 500
    lineHeight: 1.25
  card-front:
    fontFamily: "Newsreader, Georgia, \"Times New Roman\", serif"
    fontSize: "1.6rem"
    fontWeight: 400
    lineHeight: 1.2
  card-back:
    fontFamily: "Newsreader, Georgia, \"Times New Roman\", serif"
    fontSize: "1.12rem"
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 400
    lineHeight: 1.5
  tag:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "0.6875rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.08em"
  source-line:
    fontFamily: "ui-monospace, \"Cascadia Mono\", Consolas, monospace"
    fontSize: "0.8rem"
    fontWeight: 400
    lineHeight: 1.5
  code:
    fontFamily: "ui-monospace, Consolas, \"Cascadia Mono\", monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  word: "3px"
  focus: "4px"
  tag: "6px"
  code: "8px"
  control: "10px"
  popover: "12px"
  shot: "14px"
  panel: "16px"
spacing:
  gutter: "clamp(16px, 4vw, 48px)"
  stack: "16px"
  column-gap: "40px"
  section-y: "clamp(48px, 7vw, 88px)"
components:
  button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "7px 14px"
  button-hover:
    backgroundColor: "{colors.hover-wash}"
    textColor: "{colors.ink}"
  button-main:
    backgroundColor: "{colors.ink-button}"
    textColor: "{colors.on-ink-button}"
    rounded: "{rounded.control}"
    padding: "7px 14px"
  button-main-hover:
    backgroundColor: "{colors.ink-button-hover}"
    textColor: "{colors.on-ink-button}"
  app-header:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "12px clamp(16px, 4vw, 48px)"
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "18px 22px"
  page-line:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "clamp(20px, 2.5vw, 32px) clamp(18px, 5vw, 64px)"
  word-pick-picked:
    backgroundColor: "{colors.picked-yellow}"
    textColor: "{colors.ink}"
    rounded: "{rounded.word}"
  cloze-tag:
    backgroundColor: "{colors.cloze-wash}"
    textColor: "{colors.cloze}"
    rounded: "{rounded.tag}"
    padding: "5px 7px"
  known-card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.popover}"
    padding: "12px 16px"
  step-shot:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.shot}"
  code-block:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.code}"
    padding: "16px 18px"
---

# Design System: sentmine promo page

Source of truth: `docs/index.html` (one file; all CSS inline in its `<style>` block, tokens as custom properties on `:root`). The tokens are the light set of sentmine's own app pages (`src/sentmine/web/index.html`, `cards.html`), with the same names and values. The promo page is light only; the app's warm dark set (`--page #15120e`, `--panel #1f1a15`, `--ink #ede4d4`, `--pick #f0c24a`) is not part of this page.

## Overview

**Creative North Star: "The Page Is the Reader"**

The promo page wears sentmine's working interface instead of a marketing skin: warm paper, a light header with the wordmark, cream panels with warm hairlines, the book and the cards in Newsreader, one yellow for the picked word, and a solid blue underline for a word that comes back. Interface text is the system UI face; the book, the cards and the headings are Newsreader. Behind everything, a few faint card outlines drift slowly down the page, as if on their way to the deck. The visitor meets the product's own objects (a clickable sentence, a card, the card returning on a later page) before any claim.

Density is calm and document-like: single column of prose at 60 to 72ch, generous section padding, two-column splits only where two objects belong side by side (sentence card and its return; steps and their deck; a picture card and its explanation). Every image is a real screenshot, every number links to its source.

**Key Characteristics:**
- The app's own tokens: paper, cream panel, warm hairline, ink, soft ink, link blue, picked yellow, cloze rust.
- Two voices of type: Newsreader for the book, the cards and headings; system UI for interface text.
- Cards and pictures of screens lift softly; panels stay flat.
- One continuous object (a card) carried through the page, never a row of feature tiles.
- Real rasters only, each with provenance.

## Colors

Warm paper with ink, one muted blue for links and the return line, one yellow that means "this word is picked", and one rust that means "cloze".

### Primary
- **Ink Button** (`ink-button`): the main Install button, near-black with paper text (`on-ink-button`); hover lightens to `ink-button-hover`. The same dark button the app uses for Send to Anki.
- **Link Blue** (`link-blue`): links, the opening's "Click any word" hint, focus outlines, and the solid underline on known words. Hover deepens to **Link Blue Deep**.

### Secondary
- **Picked Yellow** (`picked-yellow`): the word the reader has picked (`aria-pressed="true"`), and the word marked inside its sentence on a card's back, as in the app.
- **Marker** (`marker`) and **Pick Amber** (`pick-amber`): only inside the wordmark: the marker stroke under *sent* and the pickaxe head on the i.
- **Cloze** (`cloze`) on **Cloze Wash** (`cloze-wash`): the CLOZE tag on a cloze card and the term marked in its sentence. 4.9:1.

### Neutral
- **Paper** (`paper`): page ground (on `html`, so the falling cards sit between it and the content), the header (92% with a blur), default buttons, text in code blocks.
- **Panel** (`panel`): panels, the book-sentence frame, the popover, screenshot frames.
- **Ink** (`ink`): body text and headings; also the code-block background.
- **Soft Ink** (`soft-ink`): leads, captions, metadata, nav links at rest, sources in the facts list.
- **Hairline** (`hairline`): every 1px border and divider.
- **Hover Wash** (`hover-wash`): hover fill on buttons, nav links and clickable words.
- **Selection** (`selection`): text selection, with ink text.

Supporting tokens: `--code-head` `#2b2620` (install-block header), `--code-selection` `#5c4b17`, `--picked-soft` `#fdf3c9` (settle flash), `--scrollbar` `#cfc6b4`, `--falling` `rgba(120, 92, 40, 0.11)` (falling card outlines), `--lift` (card shadow, below). Every colour in the CSS is a token on `:root`.

### Named Rules
**The Borrowed Palette Rule.** The page uses the app's colour tokens with the app's names and values. A new colour enters the page only if it first exists in the app. (The cloze colour was darkened to `#a63a12` in both on 2026-11-18 for AA contrast.)

**The Yellow Means Picked Rule.** Picked Yellow marks the word chosen to become a card, and that word inside its card. Never a callout, badge or emphasis fill. The wordmark's Marker is a different, brighter yellow and appears nowhere else.

**The Return Line Rule.** A 2px solid Link Blue underline, offset 4px, means "you already have a card for this word" and nothing else.

## Typography

**Book and Card Font:** Newsreader (SIL Open Font License, subset WOFF files in `docs/fonts/`, roman and italic, weights 200 to 800, `font-display: swap`), falling back to Georgia.
**Interface Font:** system-ui (with "Segoe UI", -apple-system, sans-serif)
**Mono:** ui-monospace (with "Cascadia Mono", Consolas, monospace) for code and for a card's source line.

**Character:** Newsreader carries everything that is reading: the book, the cards, and the page's own headings, so the page reads like a well-set book. The interface speaks in the reader's operating-system face, like the app's buttons. Anything retyped from the book is Newsreader italic.

### Hierarchy
- **Display** (500, `clamp(2rem, 4.6vw, 3.5rem)`, 1.08, -0.015em, balanced): the opening headline only.
- **Book display** (Newsreader italic 400, `clamp(1.7rem, 4.2vw, 2.6rem)`, 1.45rem below 640px; 1.3): the retyped study question, every word a button.
- **Headline** (500, `clamp(1.6rem, 2.6vw, 2.1rem)`, 1.15): section headings.
- **Title** (500, 1.45rem, 1.25): step headings. Panel titles are Newsreader 500 at 1.35rem.
- **Card front** (Newsreader 400, 1.6rem; 1.35rem in the deck): the term. **Card back** (Newsreader, 1.12rem; 1.02rem in the deck): the sentence with the term marked, then the meaning.
- **Body** (system UI 400, 17px, 1.6): all prose, measure 60 to 68ch.
- **Label** (0.85rem, soft ink) and **Caption** (0.82rem / 1.5, max 68ch).
- **Tag** (system UI 600, 0.6875rem, uppercase, 0.08em): CLOZE.
- **Source line** (mono 0.8rem, soft ink): a card's origin, as in the app.

### Named Rules
**The Reading Voice Rule.** Newsreader is reading (book, cards, headings); system UI is operating (buttons, nav, prose about the app). Never set a button in Newsreader.

**The One Webfont Rule.** Newsreader is the only downloaded font, served from the repo itself with its licence; nothing loads from a font service.

## Layout

Full-bleed bands with a fluid side gutter (`gutter`, 16 to 48px); sections separated by a 1px hairline top border and `section-y` vertical padding. Content is left-aligned; prose is held to a measure.

- **Section order as shipped:** opening; video (the tour); One card, five steps; Your cards come back while you read; Formulas and graphs on the card; Why I built it; Measured, with sources; Try it; footer.
- **Opening:** headline and one line, then the book-sentence frame full width, then two equal columns (the card it made; the same word twelve pages later), then a caption.
- **How it works:** steps `minmax(0, 1fr)` beside a sticky deck `minmax(0, 24rem)`. The deck is sticky at `top: var(--below-bar)`.
- **Comes back / Formulas:** the picture's column as wide as the picture (`fit-content(62%)`), the text beside it from its top.
- **Anchors:** `scroll-padding-top: var(--below-bar)`; `--below-bar` is `--bar-height` (66px) plus 24px.

**Breakpoints.** At 900px and below every two-column grid becomes one column, the deck stops being sticky and shows its final state. At 640px and below the header keeps only the wordmark and Install.

## Elevation & Depth

Depth is tonal (cream panels on paper) and drawn with hairlines; cards and pictures lift softly.

### Shadow Vocabulary
- **Lift** (`--lift: 0 1px 2px rgba(70, 52, 20, 0.06), 0 10px 26px rgba(70, 52, 20, 0.08)`): the book-sentence frame and the step screenshots. A warm, low shadow, the same as the app's cards.
- **Popover** (`0 10px 28px rgba(31, 35, 40, 0.16), 0 1px 3px rgba(31, 35, 40, 0.14)`): the known-card under a word you already have a card for, with a rotated-square pointer aimed at the word by script.

### Named Rules
**The Cards Lift Rule.** Things that are a card or a picture of a screen lift; panels, buttons and the header stay flat. Never a card inside a lifted card.

### Falling cards
A fixed layer (`.falling`, `aria-hidden`, `z-index: -1`, no pointer events) holds 14 empty card outlines (1.5px `--falling` border, 12px radius, card proportion 1:0.64, 110 to 190px wide) at random places from a fixed seed. Each falls the height of the screen in 38 to 70 s, linear, turning a few degrees, on an endless loop with a negative start delay so the page opens mid-fall. They are outlines only, faint enough that text over them stays fully readable. Under reduced motion they lie still where they are.

## Shapes

Soft corners: 3px on a word's highlight, 4px on focus outlines, 6px on the CLOZE tag, 8px on code blocks, 10px on buttons and nav links, 12px on the popover and falling cards, 14px on screenshot frames, 16px on panels and the sentence frame. Focus outlines are 2px Link Blue with a 3px offset.

## Components

### Wordmark
An inline SVG (paths, no font needed): *sent* in Newsreader italic on a tilted Marker stroke, *mine* upright, and the i of mine drawn as a pickaxe: an ink handle leaning towards *sent* and a Pick Amber head. It uses `currentColor`, so it follows the ink. 38px high in the header, with the link labelled "sentmine, to the top".

### Buttons
- **Default:** paper fill, hairline border, ink text, 10px corners (GitHub, Copy). Hover: hover-wash.
- **Main:** Ink Button fill, paper text, 600 weight (Install). Hover: Ink Button Hover.

### App Header
Sticky, paper at 92% with a 6px backdrop blur, hairline below. The wordmark, then section links (soft ink, 10px rounded hover wash), a spacer, GitHub and Install.

### Clickable Sentence (signature)
The study question retyped large in Newsreader italic inside a lifted frame. Every word is a `<button>` with `aria-pressed`; the picked word gets Picked Yellow. One tab stop (roving tabindex). Picking rebuilds the card beside it: the word with its base form on the front, the sentence with the word marked on the back, and no meaning yet, as in the app. Its **Suggest meaning** button shows "Asking…" for 0.6 s, then the meaning `gpt-5-nano` gave for that word in its sentence (asked ahead on 2026-11-18 through sentmine's own code, kept in the page, not corrected), with the words the model named underlined in Link Blue; the source line says it was asked ahead and not corrected.

### Card
As in the app: the term in Newsreader on the front; on the back the whole sentence with the term in Picked Yellow, the meaning below, and a mono source line ("p. 13 · ..."). A cloze card carries the CLOZE tag beside its term and marks the term in Cloze on Cloze Wash.

### Return Panel with Popover
"Page 25, twelve pages later": the later sentence in Newsreader italic with the word under the return line, and the known-card popover ("Your card from 2026-11-18", the term, the sentence).

### Sticky Deck
A panel beside the five steps that holds the cards through them; meaning, cloze card, "Sent to the deck" and the return line appear as each step crosses the middle of the viewport.

### Step Shots
A title, one paragraph, and a cropped real screenshot in a lifted frame that links to the full screenshot. Explicit width and height, descriptive alt text, lazy-loaded after the first.

### Facts, Install, Footer
Facts: a panel with claim and dated source per row. Install: two slabs, a dark header with Copy over an ink code block. Footer: what comes next, the course attribution, the source link.

### Videos
One 30-second film, the tour, no sound, in a two-column `.film` block under its own heading near the top (video 2fr, caption and the lines it says 1fr). The `<video>` has `preload="none"` and a poster that is the film's own opening card (designed, never a frame from the middle), so the page stays light and looks finished before play. Homework 10 asks for one video; two more films were made ("One word, one week" and "Your book and the web") and kept in the repo, not on the page. The films use the page's look: paper, Newsreader captions on a paper card low in the frame, a yellow day or place tag, the wordmark and the address at the end. Its source is the HyperFrames project in `video/promo`; the other two are in `video/story` and `video/web`, their films in `docs/video/`.

### Motion
The falling cards (above); **settle** (`.5s cubic-bezier(.16, 1, .3, 1)`), a fade from `--picked-soft` on the deck card that just changed; .15s colour transitions on hover. Under `prefers-reduced-motion: reduce` all of it stops and scrolling is instant.

## Do's and Don'ts

### Do:
- **Do** take every colour, radius and border from the app's tokens; check `src/sentmine/web/index.html` before adding one.
- **Do** set anything quoted from a book in Newsreader italic and caption it with the book's title.
- **Do** use only real screenshots from a real run, captured untouched; crop copyrighted pages small and link the crop to its full screenshot.
- **Do** record each shipping raster's provenance (below) when adding one.
- **Do** link every number to its source and date.
- **Do** write "sentmine" in lower case everywhere.
- **Do** keep keyboard parity, explicit image sizes and alt text, and respect `prefers-reduced-motion`.

### Don't:
- **Don't** put an author name anywhere on the page or in `docs/`; attribute to "a project for Advanced Programming at ELTE".
- **Don't** invent users, testimonials, download counts or numbers.
- **Don't** use generated, stock or AI-made images.
- **Don't** use Picked Yellow, the return underline or the Cloze colour for anything but their app meanings.
- **Don't** lift panels or put a lifted card inside one.
- **Don't** make the falling cards filled, bright or fast: they are a watermark, not a feature.
- **Don't** break the story into a split hero over a row of feature cards; carry one card through.

### Raster provenance
- `docs/img/1-click-a-word.png`, `2-suggest-meaning.png`, `5-already-has-a-card.png`, `8-formula-in-edit.png`: full screenshots from one real run of sentmine on 2026-11-18 in its new look, with an empty card memory and a real `gpt-5-nano` key, on the solution manual to Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer*; captured with headless Edge, untouched. The meaning on card 2 is the model's real answer.
- `docs/img/step-1-click.png`, `step-2-meaning.png`, `step-5-again.png`, `step-8-formula.png`: crops of those, cut small because the book is copyrighted; each is captioned with the book's title and links to its full screenshot.
- `docs/img/3-web-clip.png` and its crop `step-3-web.png`: the last frames of the tour's web take on 2026-11-19, Wikipedia's *Simpson's paradox* (CC BY-SA 4.0) at 880 px and sentmine's side-panel view at 400 px set side by side as Edge shows them, the card made cloze in the panel; in the crop the panel side starts at that card.
- `docs/img/4-send-to-anki.png` and its crop `step-4-send.png`: a frame of the tour's recording on 2026-11-19 (a real run with Anki open; the pointer in it is the recorder's drawn pointer), right after Send to Anki.
- `docs/img/6-cards-come-back-full.png` and its crop `6-cards-come-back.png`: a frame of the same recording, page 48 of the book with the card made from Wikipedia shown on pointing.
- `docs/video/sentmine-tour.mp4`: one continuous take of a real run of sentmine on 2026-11-18, recorded at 3840×2160 in headless Edge with a drawn pointer, trimmed 0.9 s and played 1.12× faster; only the wait for the AI meaning is shortened (said in its caption). It opens on a title card with a real crop of page 13 (`video/promo/assets/tour/page13-sentence.png`), which is also its poster.
- `docs/video/sentmine-story.mp4` (not on the page): real screens recorded on 2026-11-18: sentmine in headless Edge, and Anki's own window asking the card, recorded with Windows' PrintWindow; the days in it are the story's (said in the film and its caption).
- `docs/video/sentmine-web.mp4` (not on the page): real screens recorded on 2026-11-18: Wikipedia's *Simpson's paradox* (CC BY-SA 4.0) in headless Edge beside sentmine's side-panel view, and the book in sentmine; the browser's right-click menu is named in a caption, not shown.
- The opening card's meanings: gpt-5-nano's answers through sentmine's Suggest meaning on 2026-11-18, uncorrected.
- `docs/img/extension-icon.svg`: the browser extension's own icon (`extension/icons/sentmine.svg`), shown beside step 3's line about the extension and in Try it.
- `docs/fonts/`: Newsreader by Production Type, SIL Open Font License (`OFL.txt` beside it), subset to WOFF.
- No generated, stock or AI-made images.
