# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Promo page: plain static HTML and CSS in `docs/`, served by GitHub Pages from `main`, folder `/docs`. The app itself is a local Flask server with plain HTML pages (`src/sentmine/web/`).

## Users

Students who read English course books in a language they are still learning, such as the author reading statistics and causal-inference books for an ELTE course. While reading they meet words and terms they want to remember, and they review with Anki. Before sentmine they copied sentences into Anki by hand, which was slow, so most words never became cards.

## Product Purpose

sentmine is a reading app that runs on the reader's own computer. The reader opens a PDF (shown as its real pages) or pastes a text, clicks a word to get a card made from its sentence, or drags over a term and then its definition to get a definition card, which becomes a cloze card when the term is inside its definition. Cards go to Anki with one click (AnkiConnect) or as a downloaded deck. Success means the words and terms from the reader's own reading end up remembered.

## Positioning

The cards come back into the reading. In the next text, words and terms the reader already has cards for are underlined; pointing at one shows the reader's own card, and each card counts how many texts it was met again in. The reader-to-Anki tools found in a web search on 2026-11-14 (Pick2anki, Vocabsieve, browser add-ons) were not described as doing this; they were not tried by hand, so claims about them stay worded as what that search found.

## Operating Context

The reader works on a desktop computer with course PDFs, Anki open with the AnkiConnect add-on, and sentmine running locally in the browser. The app is part of a course project (Advanced Programming, ELTE), demonstrated on 1 and 8 December 2026.

## Capabilities and Constraints

- Runs only on the reader's computer (`127.0.0.1`). The text stays there, except that Suggest meaning sends the word and its sentence to OpenAI (`gpt-5-nano`), only with the reader's own key (`OPENAI_API_KEY`, or `.env` in sentmine's user folder).
- Installed from the repository with Python 3.10 or newer (`pip install .`); there is no online version and no package release.
- Anki with AnkiConnect is optional: Download writes an `.apkg` deck instead.
- Scanned PDFs cannot be read yet; there is no browser extension yet (planned after the demos).

## Brand Commitments

The name is `sentmine`, written in lower case. No author name on the promo page: it says "a project for Advanced Programming at ELTE" and links the repository.

## Evidence on Hand

- Six screenshots from one real run on the course book's solution manual, cropped: `docs/img/1-click-a-word.png` to `docs/img/6-cards-come-back.png`. The manual is copyrighted: only small parts appear, with a caption naming it.
- Measurements, each in `PLANNING_LOG.md`: 10 cards, Download and import 30 s against Send to Anki 5 s (one timing by hand, 2026-11-03); 99.9 to 100% of words found on four real PDFs (2026-11-06); the first design's 103 cards, of which 4 were really new (Homework 4).
- 555 automated tests (pytest, 2026-11-14).
- No users besides the author, no testimonials, no download counts: none may be invented.

## Product Principles

- Read the real thing: the book as it looks, not a copy pasted somewhere else.
- The reader chooses what becomes a card; the app never guesses.
- Every claim is measured or sourced, and every screenshot comes from a real run.
- Local first: nothing leaves the computer unless the reader asks for a meaning.
