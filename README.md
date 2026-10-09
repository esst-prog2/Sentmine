# sentmine

A small reading app that runs on my own computer. I paste a text I am
reading and turn parts of it into Anki flashcards as I go: a new word
inside its real sentence, or a term with its definition.

## 1. The demo

I type `sentmine` in a terminal and the reading page opens in my browser.
I paste a paragraph from this week's statistics notes:

```
The standard deviation measures how spread out a set of values is.
It is the square root of the variance. Outliers can skew it
considerably.
```

The text appears as a page I can read. I need to learn the term, so I
switch to Definition, select `standard deviation`, and drag over the
first two sentences. A card appears in the preview on the right:

```
front:  standard deviation
back:   The standard deviation measures how spread out a set of values
        is. It is the square root of the variance.
```

I do not know the English word `skew`, so I switch to Word and click it.
It turns yellow and a second card appears:

```
front:  Outliers can skew it considerably.   (skew in bold)
back:   skew
```

The header says `2 cards`. In the preview I shorten the back of the first
card. I click `skew` again by mistake and its card disappears, so I click
it once more. Then I press Download and get `new.apkg` with two cards. I
import it into Anki and both are there, in the words of the text I read.

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

The reading page is not built yet. Until it is, the repository contains
the first design, a command-line tool. Needs Python 3.10 or newer.

```
pip install .                        # installs sentmine and genanki
sentmine passage.txt --known known.txt --deck new.apkg
```

To work on it and run the tests: `pip install -e ".[dev]"`, then `pytest`.
