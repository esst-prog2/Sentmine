# sentmine

A small reading app that runs on my own computer. I open a PDF or paste a
text I am reading and turn parts of it into Anki flashcards as I go: a new
word inside its real sentence, or a term with the passage that defines it.

## 1. The demo

I type `sentmine` in a terminal and the reading page opens in my browser.
I open the solution manual of our course book, *Causal Inference in
Statistics: A Primer* (a 75-page PDF; it is copyrighted, so it stays on my
computer and is not in this repository). The status line says
`Read 75 pages. 2 had no text.` and the left panel shows the real pages,
with their formulas and tables as printed. The cards panel stays on the
right while I scroll.

On page 13 I do not know the word `simultaneously`, so I click it. It
turns yellow on the page and a card appears:

```
front:  Two fair coins are flipped simultaneously to determine the
        payoffs of two players in the town’s casino.
        (simultaneously in bold)
back:   simultaneously
```

I press **Suggest meaning** on the card. The small model `gpt-5-nano` gets
the word and its sentence, and the back becomes:

```
back:   simultaneously
        At the same time; the two coin flips occur together, not one
        after the other.
```

On page 5 I want to remember a term. I drag over `Simpson’s reversal`;
the words turn blue as I drag, and the status line says
`Term: Simpson’s reversal Now drag over its definition.` I drag over the
sentence that explains it. Because the term is inside that sentence,
sentmine makes a cloze card, which hides the term:

```
front:  Strangely, the experimental data revealed a [...]: Although the
        drug proved beneficial to the population as a whole, drug takers
        were less likely to recover than nontakers, among both lollipop
        receivers and lollipop nonreceivers.
back:   the same sentence, with Simpson’s reversal in bold
```

The button **Make it term → passage** would turn it into a card with the
term on the front instead; I keep the cloze.

I name the deck `causal` and press **Send to Anki**. Anki is open with
the AnkiConnect add-on, so the cards go straight in, and the status line
says `Sent to the deck 'causal' in Anki: 2 cards added. Now in My cards
too.` (When Anki is closed, **Download** gives me `causal.apkg` to import
instead. Measured on ten cards: download and import took me 30 seconds,
Send to Anki 5.)

A week later, in Study question 1.5.2, I meet `simultaneously` again and
click it. No new card is made. The page shows my earlier card with its
date, `'simultaneously' already has a card from 2026-11-07.`, and asks
whether to **Skip** or **Make it anyway**. I skip; I learn it once.

The **My cards** page lists every card I have sent or downloaded, newest
first, with the day I made it, and I can search them.

Why this replaced the first design: the earlier version guessed my new
words from a list of words I know. I measured it on a real Guardian
article (see `spike/`): of 103 cards it made, 4 were really new to me, 64
were words I knew and 35 were names or junk. I still had to sort them by
hand, so now I choose what becomes a card myself, while reading.

## 2. The shape

```
in         a text, pasted into the page (plain text, any length)
out        new.apkg   an Anki-importable deck with two kinds of card:
                      word card        front = the sentence with the word
                                       in bold, back = the word
                      definition card  front = the term, back = the
                                       passage I marked, of any length
on screen  the text on the left; in Word mode a click picks a word and a
           second click unpicks it; in Definition mode I select a term,
           then drag over its definition; the header counts the cards;
           the preview on the right shows each card and lets me edit or
           delete it; Download writes the deck
on disk    nothing is saved until I press Download; the app runs only on
           my own computer and sends the text nowhere
```

## 3. The size

**First useful version**

- start the app with one command and open the reading page in the browser
- paste a text; tidy it with simple rules (join lines broken inside a
  sentence, remove extra spaces and blank lines)
- Word mode: click a word to make a card from its sentence; click again
  to remove it
- Definition mode: select a term of one or more words, then mark the
  passage that defines it - one sentence, several, or a whole paragraph;
  line breaks inside the passage are kept
- one card per word or term: picking the same one again tells me so and
  makes no second card
- a preview of every card, where I can edit the front and the back or
  delete the card
- a count of the cards so far
- download a valid `.apkg` deck of the cards as they appear in the preview

**Not this term** (the first four are the planned next changes, in order)

- loading a PDF that contains text, such as lecture slides
- suggesting with AI the meaning of a word, or the passage that defines a
  term, to accept or edit in the preview
- reading scanned PDF pages with AI
- loading an article from a web link
- sending cards straight into Anki (AnkiConnect), without the download
- a browser extension for picking words on the original website
- remembering between sessions which cards I already made
- highlighting words that are probably new to me, from a known-words list
  (the first design's filter)
- languages written without spaces between words, such as Chinese or
  Japanese
- audio, images, formulas, or a phone app

## 4. How we would know it works

- Given the paragraph above, clicking `skew` in Word mode makes a card
  whose front is exactly `Outliers can skew it considerably.` with `skew`
  in bold, and whose back is `skew`.
- Given the term `standard deviation` selected and the first two
  sentences marked, the card's front is `standard deviation` and its back
  is exactly those two sentences, joined across the line break.
- Given a marked passage that spans two paragraphs, the back keeps the
  break between them.
- Given a word or term that already has a card, picking it again makes no
  new card and the count stays the same.
- Given a picked word, clicking it again removes its card and the count
  goes down by one.
- Given a card edited in the preview, the downloaded deck contains the
  edited text, not the original.
- Given no cards, Download writes no file and says why.
- Given the downloaded `.apkg`, importing it into Anki succeeds and the
  number of cards matches the header.

## 5. What could stop this

Pasted text is messy. Text copied from slides or a website brings titles,
page numbers and broken lines with it, and a damaged sentence makes a
damaged card. The simple tidy-up rules will not catch everything. The
preview is the defence: I see every card before it is saved and can fix
it. Formulas and tables do not survive copying at all, so a definition
that depends on one will be incomplete.

It may not be faster than making cards by hand. The claim is that a click
or a drag beats copying text into Anki, but pasting the text first is an
extra step. I will measure it: ten cards made by hand against ten made in
the app, from the same text.

Two kinds of card in one page could make both awkward. If switching
between Word and Definition mode gets in the way of reading, the first
version keeps Definition mode and Word mode moves to a later change.

Similar tools exist for vocabulary: Readlang lets a reader click a word
to save a flashcard. It is built around translating foreign words. Mine
also makes cards from the definitions in my own course material, stays on
my computer, and puts everything in the Anki deck I already use.

A web page is new ground for this project. The first version was a
command-line tool; the sentence splitting and the deck writing carry over
and are already tested, but the page itself is new work.

The first version needs no network, account or API, and handles no
personal data. Course material may be copyrighted, so the demo uses a
short text I wrote myself. The planned AI features will need an API key
and will send text to an outside service, so they stay switched off
unless a key is present, and the app must work fully without them.

## 6. Install and run

Needs Python 3.10 or newer.

```
pip install .        # installs sentmine with genanki and Flask
sentmine             # starts the reading app and opens it in the browser
```

The page is at http://127.0.0.1:8000 and is served only to this computer.
Stop the app with Ctrl+C in the terminal. The text and cards on the page
are not kept between runs, so download the deck before closing.

Every card you download is remembered in your card memory, a SQLite
database in your own user folder (on Windows `%APPDATA%\sentmine\cards.db`;
the terminal prints where it is). When you pick a word or term that already
has a card, the page shows the earlier card and lets you skip it or make
it anyway. Different forms of a word count as the same word (`ran` and
`run`). The **My cards** page lists every remembered card, searches them,
shows your progress, and lets you forget a card. To use another database,
set `SENTMINE_DATABASE` to its path. A backup is a copy of that one file.

Instead of pasting, you can open a PDF that contains text, or a `.txt` file.
Running heads and page numbers are removed and hyphenated words rejoined;
formulas and tables come out as they are, and scanned PDFs cannot be read yet.

With an OpenAI API key, each word card gets a **Suggest meaning** button: it
sends that word and its sentence to the small model `gpt-5-nano` and puts a
short English explanation on the back, for you to check and edit. Put the key
in `.env` in the same user folder, as the line `OPENAI_API_KEY=...`, or in the
variable of that name. Without a key the button is not shown and everything
else works. Keep the key out of this repository and out of OneDrive.

The first design, a command-line tool that picks the words from a
known-words list, still works: `sentmine passage.txt --known known.txt
--deck new.apkg`.

To work on it and run the tests: `pip install -e ".[dev]"`, then `pytest`.
