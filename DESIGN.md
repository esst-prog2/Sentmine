---
name: sentmine promo page
description: One static page that shows sentmine at work, dressed in sentmine's own reading-app interface.
colors:
  paper: "#f6f5f1"
  panel: "#ffffff"
  ink: "#1f2328"
  soft-ink: "#5c6470"
  hairline: "#d9d6cd"
  hover-wash: "#ecebe5"
  action-blue: "#1a5fd0"
  action-blue-deep: "#154fae"
  on-accent: "#ffffff"
  picked-yellow: "#ffe27a"
  selection-blue: "#c8dafc"
typography:
  display:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "clamp(1.75rem, 3.4vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "clamp(1.35rem, 2.2vw, 1.75rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  title:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  lede:
    fontFamily: "system-ui, \"Segoe UI\", -apple-system, sans-serif"
    fontSize: "1.12rem"
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
  book-display:
    fontFamily: "Georgia, \"Times New Roman\", serif"
    fontSize: "clamp(1.7rem, 4.2vw, 2.6rem)"
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  book-line:
    fontFamily: "Georgia, \"Times New Roman\", serif"
    fontSize: "1.15rem"
    fontWeight: 400
    lineHeight: 1.6
  code:
    fontFamily: "ui-monospace, Consolas, \"Cascadia Mono\", monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  word: "3px"
  control: "6px"
  frame: "8px"
  panel: "10px"
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
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.control}"
    padding: "7px 14px"
  button-main-hover:
    backgroundColor: "{colors.action-blue-deep}"
    textColor: "{colors.on-accent}"
  app-header:
    backgroundColor: "{colors.panel}"
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
    rounded: "{rounded.control}"
    padding: "clamp(20px, 2.5vw, 32px) clamp(18px, 5vw, 64px)"
  word-pick-picked:
    backgroundColor: "{colors.picked-yellow}"
    textColor: "{colors.ink}"
    rounded: "{rounded.word}"
  known-card:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    rounded: "{rounded.frame}"
    padding: "10px 14px"
  step-shot:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.frame}"
  code-block:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.frame}"
    padding: "16px 18px"
---

# Design System: sentmine promo page

Source of truth: `docs/index.html` (one file; all CSS inline in its `<style>` block, tokens as custom properties on `:root`). The tokens are the light set of sentmine's own app pages (`src/sentmine/web/index.html`, `cards.html`), copied value for value. The promo page is light only (`color-scheme: light`); the app's dark set is not part of this page.

## Overview

**Creative North Star: "The Page Is the Reader"**

The promo page wears sentmine's working interface instead of a marketing skin: a white app header with a hairline under it, paper-coloured ground, white panels with warm grey hairlines, one blue for actions, one yellow for the picked word, and a dotted blue underline for a word that comes back. Interface text is the system UI face; anything that comes from the book is Georgia, usually italic. The visitor meets the product's own objects (a clickable sentence, a card, the card returning on a later page) before any claim.

Density is calm and document-like: single column of prose at 60 to 72ch, generous section padding, two-column splits only where two objects belong side by side (sentence card and its return; steps and their deck). Nothing is decorative: every image is a real screenshot, every number links to its source, and the one animation marks a card that just changed.

**Key Characteristics:**
- The app's own tokens, unchanged: paper, white panel, hairline, ink, soft ink, action blue, picked yellow.
- Two voices of type: system UI for interface, Georgia for the book.
- Flat panels with hairline borders; shadow only on things that float or are pictures of a screen.
- One continuous object (a card) carried through the page, never a row of feature tiles.
- Real rasters only, each with provenance.

## Colors

A warm neutral paper interface with one cool blue for action and one yellow that means "this word is picked".

### Primary
- **Action Blue** (`action-blue`): links, the main Install button, the opening's "Click any word" hint, focus outlines, the cloze gap `[...]`, and the dotted underline on known words. Hover deepens to **Action Blue Deep** (`action-blue-deep`). White text on it uses `on-accent`.

### Secondary
- **Picked Yellow** (`picked-yellow`): only the word the reader has picked (`aria-pressed="true"` in the opening sentence), as in the app. It is a state colour, not a highlight colour for emphasis.

### Neutral
- **Paper** (`paper`): page ground, the default button fill, and the text colour inside code blocks.
- **Panel White** (`panel`): header, panels, the book-sentence frame, the known-card popover, screenshot frames, and the Try it section's ground.
- **Ink** (`ink`): body text and headings; also the code-block background.
- **Soft Ink** (`soft-ink`): leads, captions, metadata, nav links at rest, sources in the facts list. Measured about 5.5:1 on paper.
- **Hairline** (`hairline`): every 1px border and divider, the dashed rule between a card's front and back.
- **Hover Wash** (`hover-wash`): hover fill on buttons and on clickable words.
- **Selection Blue** (`selection-blue`): text selection, with ink text.

Supporting tokens: `--code-head` `#2b3036` (install-block header), `--code-selection` `#2d4a7a` (selection inside code), `--picked-soft` `#fff8d6` (settle flash), `--scrollbar` `#c4c0b5` (scrollbar thumb). Every colour in the CSS is a token on `:root`; no hex value appears outside it.

### Named Rules
**The Borrowed Palette Rule.** The page uses the app's colour tokens with the app's names and values. A new colour enters the page only if it first exists in the app.

**The Yellow Means Picked Rule.** Picked Yellow marks exactly one thing: the word currently chosen to become a card. Never a callout, badge or emphasis fill.

**The Dotted Return Rule.** A 2px dotted Action Blue underline, offset 4px, means "you already have a card for this word" and nothing else. It is one CSS rule, shared by `.known`, `.back-again span` and `.underline-demo`.

## Typography

**Interface Font:** system-ui (with "Segoe UI", -apple-system, sans-serif)
**Book Font:** Georgia (with "Times New Roman", serif)
**Code Font:** ui-monospace (with Consolas, "Cascadia Mono", monospace)

**Character:** The interface speaks in the reader's own operating-system face, so the page feels like the app on their machine; the book speaks in Georgia italic, so anything retyped from the text reads as quoted material, not as the page's own voice.

### Hierarchy
- **Display** (700, `clamp(1.75rem, 3.4vw, 2.75rem)` = 44px at 1440 wide, 28px at 390; line-height 1.08; -0.02em; max 24em; balanced): the opening headline only, larger than every section heading.
- **Book display** (Georgia italic 400, `clamp(1.7rem, 4.2vw, 2.6rem)`, 1.45rem below 640px; line-height 1.3; -0.01em): the retyped study question in the opening, every word a button.
- **Headline** (700, `clamp(1.35rem, 2.2vw, 1.75rem)`, line-height 1.2, -0.015em, max 22em, balanced): section headings.
- **Title** (700, 1.3rem, 1.3): step headings. Panel titles are body size at 700.
- **Body** (400, 17px, 1.6): all prose, measure 60 to 68ch; `text-wrap: pretty` on paragraphs and list items.
- **Lede** (1.12rem, soft ink, max 62ch): the paragraph under a section heading. The opening's line under the headline is 1.05rem, max 72ch.
- **Book line** (Georgia italic, 1.15rem, 1.6): the page-25 return sentence. The study-question label above the opening sentence is Georgia 700 at 1.1rem in soft ink.
- **Label** (0.85 to 0.9rem, soft ink): card metadata, deck state, facts sources. Captions are 0.82rem / 1.5, max 68ch.
- **Code** (0.875rem in install blocks, 0.95rem elsewhere, line-height 1.7); inline code is 0.9em.

### Named Rules
**The Two Voices Rule.** System UI is the page and the app talking; Georgia is the book. Never set interface copy in Georgia or book text in the system face.

**The No Webfont Rule.** No downloaded fonts: the page loads in the faces already on the reader's computer, as the app does.

## Layout

Full-bleed bands with a fluid side gutter (`gutter`, 16 to 48px); sections separated by a 1px hairline top border and `section-y` vertical padding. Content is left-aligned, not centred; prose is held to a measure (`max-width: 68ch`).

- **Section order as shipped:** opening; One card, five steps; Your cards come back while you read; Why I built it; Measured, with sources; Try it; footer.
- **Opening:** headline and one line, then a stage (single column, `stack` gap): the book-sentence frame full width, then a two-column grid of equal columns (the card it made; the same word twelve pages later), then a one-line caption.
- **How it works:** two columns, steps `minmax(0, 1fr)` and deck `minmax(0, 24rem)`, `column-gap` between. Each step is followed by `clamp(48px, 7vw, 80px)`. The deck is sticky at `top: var(--below-bar)` (86px).
- **Comes back:** two columns at 1.25fr / 1fr, vertically centred.
- **Facts:** each row a grid of claim and a 15rem source column.
- **Install:** `repeat(auto-fit, minmax(min(100%, 26rem), 1fr))`, max 64rem.
- **Anchors:** `scroll-padding-top: var(--below-bar)` clears the sticky header; `--below-bar` is `--bar-height` (62px) plus 24px, shared with the deck's sticky top; smooth scrolling unless reduced motion is requested.

**Breakpoints.** At 900px and below every two-column grid becomes one column, the deck stops being sticky and shows its final state (step 5) after the steps, and facts rows stack. At 640px and below the header drops its section nav and the GitHub button (Install stays), the sentence frame padding becomes 20px 18px and the book display drops to 1.45rem.

## Elevation & Depth

Flat by default: depth is tonal (white panels on paper) and drawn with 1px hairlines. Shadows exist in exactly two places.

### Shadow Vocabulary
- **Popover** (`box-shadow: 0 10px 28px rgba(31, 35, 40, 0.16), 0 1px 3px rgba(31, 35, 40, 0.14)`): the known-card that floats under a word you already have a card for, with a rotated-square pointer (`-1px -1px 1px rgba(31, 35, 40, 0.08)`) aimed at the word by script. It is the app's own hover card, shown open.
- **Screenshot frame** (`box-shadow: 0 2px 10px rgba(31, 35, 40, 0.06)`): the faint lift on step screenshots, so a picture of a screen reads as a picture, not as live UI.

### Named Rules
**The Only Floating Things Rule.** A shadow means the element floats over the page (the popover) or is a photograph of a screen (the step shots). Panels, cards and buttons stay flat.

## Shapes

Soft, small corners and hairline borders throughout: 3px on a clickable word's highlight, 6px on buttons and the book-sentence frame, 8px on screenshot frames, code blocks and the popover, 10px on panels. Focus outlines are 2px Action Blue with a 4px radius and 3px offset (1px offset on words). The install block joins a dark header (top corners 8px) to its code (bottom corners 8px) as one rounded slab. Inside a card, a dashed hairline separates front from back; between cards in the deck, a solid hairline.

## Components

### Buttons
- **Shape:** gently rounded (6px), 1px hairline border, 500 weight at 0.95rem, padding 7px 14px.
- **Default:** paper fill, ink text (GitHub, Copy). Hover: hover-wash fill, border darkens to soft ink.
- **Main:** Action Blue fill and border, white text, 600 weight (Install). Hover: Action Blue Deep.
- **Copy:** the default button made smaller (padding 2px 12px, 0.85rem) in the install-block header; its label reads "Copied" for 2s, or "Select and copy" if the clipboard refuses.
- **Transition:** background and border colour, .15s.

### App Header (Navigation)
The app's own header: sticky at the top, white, hairline below, padding 12px by gutter. Brand "sentmine" at 700 / 1.15rem in ink; section links in soft ink with a 2px transparent bottom border that becomes hairline on hover; a spacer; then GitHub (default button) and Install (main button). Below 640px only brand and Install remain.

### Opening Status
Sentmine's status line carries the headline: Display headline, one soft-ink line beneath, no border under it in the opening.

### Clickable Sentence (signature)
The study question retyped large in Georgia italic inside a white frame (hairline, 6px). Above it, the study-question label (left) and a blue hint "Click any word in the sentence." (right). Every word is a `<button>` with `aria-pressed`; hover gives hover-wash, the picked word gets Picked Yellow. The group is one tab stop (roving tabindex): Arrow Left/Right, Home and End move and pick. Picking rebuilds the card beside it, the word in bold in its sentence and the base form on the back. A caption names the book and says the sentence is retyped.

### Card Panel
A panel titled "Cards": the front is the sentence with the word in bold, a dashed hairline, the back with the word and its meaning, then label-size metadata. It is `aria-live="polite"` so a new pick is announced.

### Return Panel with Popover
A panel titled "Page 25, twelve pages later": the later sentence in Georgia italic with the word under the dotted blue underline, and below it the known-card popover (see Elevation) showing "Your card from 2026-11-14" and the original card front, its pointer kept on the word by script on resize. The word is `aria-describedby` the popover.

### Sticky Deck
A panel beside the five steps that holds one card through them. A soft-ink state line names the step; meaning, cloze card, "Sent to the deck" line and the page-25 return line appear cumulatively as each step crosses the middle of the viewport (IntersectionObserver, root margin -40% / -50%). Without JavaScript or below 900px it shows a fixed state.

### Step Shots
Each step is a title, one paragraph, and a cropped real screenshot in a white frame (hairline, 8px, faint shadow, clipped) that links to the full screenshot with a zoom-in cursor. Every image has explicit width and height and descriptive alt text; all but the first are lazy-loaded.

### Facts Panel
A panel (padding 4px 24px, max 60em) holding a plain list: each row is the claim and, in a 15rem soft-ink column, the linked source with its date. Rows are separated by hairlines.

### Install Blocks
Two side-by-side slabs: a dark header (`--code-head`, paper text, the system name and a Copy button) over an ink code block in paper text. A `<details>` "Optional: Anki and AI meanings" follows, its summary in 600 weight with a soft-ink marker.

### Footer
Hairline above, soft ink at 0.95rem, a wrapping row: what comes next, the course attribution, the source link.

### Motion
One animation: **settle** (`.5s cubic-bezier(.16, 1, .3, 1)`), a fade from `--picked-soft` to transparent on the deck card that just changed. Otherwise only .15s colour transitions on hover. Under `prefers-reduced-motion: reduce` all animations and transitions are off and scrolling is instant.

## Do's and Don'ts

### Do:
- **Do** take every colour, radius and border from the app's tokens; check `src/sentmine/web/index.html` before adding one.
- **Do** set anything quoted from a book in Georgia italic and caption it with the book's title.
- **Do** use only real screenshots from a real run, captured untouched; crop copyrighted pages small around the word or card and link the crop to its full screenshot.
- **Do** record each shipping raster's provenance (below) when adding one.
- **Do** link every number to its source and date.
- **Do** write "sentmine" in lower case everywhere, including at the start of a sentence.
- **Do** keep keyboard parity: visible 2px blue focus outline, one tab stop per word group, explicit image sizes and alt text.
- **Do** respect `prefers-reduced-motion`.

### Don't:
- **Don't** put an author name anywhere on the page or in `docs/` (it is published); attribute to "a project for Advanced Programming at ELTE".
- **Don't** invent users, testimonials, download counts or numbers.
- **Don't** state what other tools can or cannot do; the page names none now, and any future mention is worded as what a web search found, with the month.
- **Don't** use generated, stock or AI-made images.
- **Don't** use Picked Yellow or the dotted blue underline for anything but their app meanings.
- **Don't** add shadows to panels, cards or buttons; only the popover and screenshot frames lift.
- **Don't** break the story into a split hero over a row of feature cards; carry one card through.
- **Don't** load webfonts.

### Raster provenance
- `docs/img/1-click-a-word.png` to `docs/img/6-cards-come-back.png`: full screenshots from one real run of sentmine on 2026-11-14 on the solution manual to Pearl, Glymour and Jewell, *Causal Inference in Statistics: A Primer*, with Anki open; captured with headless Edge, untouched.
- `docs/img/step-1-click.png`, `step-2-meaning.png`, `step-3-cloze.png`, `step-4-send.png`, `step-5-again.png`: crops of those screenshots, cut small around the word or card because the book is copyrighted; each is captioned on the page with the book's title and links to its full screenshot.
- No generated, stock or AI-made images.
