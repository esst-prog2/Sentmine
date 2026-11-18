# sentmine

Promo page: https://esst-prog2.github.io/Sentmine/

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
front:  simultaneously
back:   Two fair coins are flipped simultaneously to determine the
        payoffs of two players in the town’s casino.
        (simultaneously in bold)
```

I press **Suggest meaning** on the card. The small model `gpt-5-nano` gets
the word and its sentence, and puts the meaning under the sentence:

```
back:   Two fair coins are flipped simultaneously to determine the
        payoffs of two players in the town’s casino.

        At the same time; the two coin flips occur together, not one
        after the other.
```

The model also names the few words of the sentence that show that meaning,
and the card underlines them (here, for example, `flipped simultaneously to
determine`). sentmine underlines only words that really are in the sentence;
when the model names none, the card simply has no underline.

On page 5 I want to remember a term. I drag over `Simpson’s reversal`;
the words turn blue as I drag, and the card is made at once, with the
sentence the term is in as its passage. Every card has the same shape: the
term on the front, the passage on the back with the term in bold. (Had the
explanation gone on in the next sentence, I would press **Edit** on the card
and click that sentence to put it in.) Because the term is inside the
passage, I press **Make it cloze**, which hides the term:

```
front:  Strangely, the experimental data revealed a [...]: Although the
        drug proved beneficial to the population as a whole, drug takers
        were less likely to recover than nontakers, among both lollipop
        receivers and lollipop nonreceivers.
back:   the same sentence, with Simpson’s reversal in bold
```

**Make it term → passage** would turn it back; I keep the cloze.

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

These sections describe the app as it is now (November 2026). The plan
from September is in the git history.

```
in         a PDF that contains text, shown as its own pages; a .txt file;
           a pasted text; or, with the browser extension, the PDF or
           article in a browser tab, or a sentence or definition I select
           on a web page
out        cards for Anki, two kinds:
             word card        front = the sentence with the word in bold,
                              back = the word with its base form, and a
                              meaning if I ask for one
             definition card  front = the term, back = the passage I
                              marked; or a cloze card, the term hidden in
                              its own passage
           sent straight into my Anki deck (AnkiConnect), or downloaded
           as a deck file (.apkg)
on screen  Read: the text or the PDF's pages; a click on a word makes a
           card, a second click removes it; a drag over a term, then over
           its definition, makes a definition card; the same with the
           keyboard; the Cards panel shows each card to edit, delete,
           make cloze or give a suggested meaning; a word I already have
           a card for has a blue line, and pointing at it shows my card.
           My cards: every card I kept, searchable, with my progress.
           Beside a web page: a side panel for the parts I selected
on disk    the card memory, one SQLite file in my user folder, holds the
           cards I sent or downloaded and where I met them again; the
           text I read is not saved
network    the app runs only on my own computer, and the text stays
           there, except that Suggest meaning sends the word and its
           sentence to OpenAI (only with my own key); Send to Anki talks
           to Anki on this computer
```

## 3. The size

**What it does now**

- start with one command (`sentmine`); the page opens in the browser
- open a PDF with text and read it as its real pages, or open a `.txt`
  file, or paste a text (tidied: broken lines joined, extra spaces gone)
- word cards by clicking, definition cards by dragging over a term and
  then its definition, with the mouse or the keyboard
- one deck for everything: cards from the PDF and from web pages are listed
  together, in Read and in the browser's side panel
- one card per word or term: picking one I already have shows my earlier
  card, and I can skip it or make it anyway
- edit, delete, switch a definition card to cloze, or ask for a suggested
  meaning (with my own OpenAI key)
- add a formula, graph or picture to a card, from a PDF page (drag a box) or
  a web page (right-click an image), under the answer
- send the cards to Anki in one click, or download a deck
- the cards I keep are remembered; in the next text the words and terms I
  have cards for are marked, and each card counts the texts it came back in
- every card keeps its source (the PDF's name and page, or the web page's
  title and address): on the Anki card, and in My cards
- My cards: search, progress, the sources most cards came from, delete
- my place in the text is kept when I switch to My cards and back
- a PDF's own links work (to its pages, or to websites in a new tab); a page
  bar jumps to a page or, when the PDF has bookmarks, to a chapter
- a browser extension: open the current tab in sentmine, or right-click a
  selected sentence or definition and make its card in a side panel

**Not yet**

- formulas from web pages as real formulas (they come as pictures now)
- scanned PDFs (there is no text to read in them)
- marking the words I have cards for on the web page itself
- reading my Anki review results back into the app
- languages written without spaces between words, such as Chinese or
  Japanese
- audio, or a phone app

## 4. How we would know it works

The checks are automated: `pip install -e ".[dev]"`, then `pytest` (579
tests on 14 November 2026). Some of them:

- Given the text `Outliers can skew it considerably.`, clicking `skew`
  makes a card whose front is exactly that sentence with `skew` in bold,
  and whose back is `skew`.
- Given a word or term that already has a card, picking it again makes no
  new card, and the count stays the same.
- Given a picked word, clicking it again removes its card.
- Given a card edited in the preview, the deck contains the edited text.
- Given no cards, Download writes no file and says why.
- Given a card for `run` in the memory, `ran` in a new text is marked as
  a word I already have a card for.
- Given a PDF, each word is found on its page where it is printed; on
  four real PDFs of 10 to 166 pages, 99.9 to 100% of the words were found
  (planning log, 6 November 2026).
- Given a clip from a web page, the text and cards in Read do not change.
- Given a request from another website, the app refuses to change
  anything.

## 5. What could stop this

A PDF's text is not always clean. Scanned pages have no text at all, and
formulas and tables come out of the text layer as they are, so a card
from a sentence with a formula can be incomplete. The page itself is
shown as a picture, so what I read is right even when the text behind it
is not.

Web pages are messy too: menus, boxes and line breaks cut sentences. That
is why the extension does not guess sentences on a web page; I select
what I want and right-click it.

The base form comes from a word list and is not always right (`least`
gives `less`). The card shows it, so I can edit it.

Speed was measured, not assumed: ten cards by hand took about 3 minutes,
ten in the app about 1 minute (9 October 2026); ten cards into Anki took
about 30 seconds by downloading and importing the deck and about 5
seconds with Send to Anki (4 November 2026). Each was one timing by hand.

Similar tools exist: a web search on 14 November 2026 found Pick2anki (a
plugin for Zotero's PDF reader), Vocabsieve and browser add-ons that send
a word with its sentence to Anki. sentmine also makes cards from the
definitions in my own course book, on its real pages, and brings my
cards back while I read.

Course material is copyrighted, so the demo and the promo page show only
small parts of it, with the book named. Suggest meaning needs an API key
and sends text to an outside service, so it stays off without a key, and
everything else works without it. The app was built and tested on
Windows.

## 6. Install and run

Needs Python 3.10 or newer.

```
pip install .        # installs sentmine with genanki and Flask
sentmine             # starts the reading app and opens it in the browser
```

The page is at http://127.0.0.1:8000 and is served only to this computer.
Stop the app with Ctrl+C in the terminal. The text on the page and the
cards not yet sent or downloaded are not kept between runs, so send or
download them before closing; the cards you send or download are kept in
your card memory (below).

Every card you download is remembered in your card memory, a SQLite
database in your own user folder (on Windows `%APPDATA%\sentmine\cards.db`;
the terminal prints where it is). When you pick a word or term that already
has a card, the page shows the earlier card and lets you skip it or make
it anyway. Different forms of a word count as the same word (`ran` and
`run`). The **My cards** page lists every remembered card, searches them,
shows your progress, and lets you forget a card. To use another database,
set `SENTMINE_DATABASE` to its path. A backup is a copy of that one file.

Everything works from the keyboard too: Tab into the text, move from word
to word with the arrow keys, and press Enter for a card (Enter again removes
it). Shift and the arrow keys mark several words, as a drag does: Enter makes
them a term's card, with their sentence. A word you already have a card for
shows that card when the keyboard reaches it.

A card's passage is the sentence its word or term is in. A drag over more
than eight words is not taken as a term: drag over the term, then change the
passage in **Edit**.

**Edit** is the one place to change a card. Press it, and both sides become
small documents of text and pictures: the Term on the front, the Passage on
the back. Click where you want something, in either side, and then
everything you add goes in there:

- **click a sentence** in the text (in Read or the side panel), and the
  whole sentence goes in; no new card is made while you edit;
- on a PDF, **drag a box** on the page around a formula or a graph: that
  part of the page goes in as a picture, cut from the PDF itself so it stays
  sharp (Esc cancels the box);
- **paste a picture** with Ctrl+V: a copied image or a screenshot
  (Win+Shift+S);
- on a web page, **right-click** text and choose *Make a card from this*, or
  right-click an image and choose *Add this picture to the card you last
  made or edited*: it goes in there too.

When you click away from the card, a thin line shows where the next thing
will go. Type around it as usual; to remove a picture, click it and press
Delete; to take out a sentence, delete it like any text. **Save** ends it;
**Cancel** puts the card back as it was, pictures included. Pictures go into
the deck file and into Anki where you put them (on a cloze card, a picture
on the front is shown after the answer).

Instead of pasting, you can open a PDF that contains text, or a `.txt` file.
Running heads and page numbers are removed and hyphenated words rejoined;
formulas and tables come out as they are, and scanned PDFs cannot be read yet.

With an OpenAI API key, each word card gets a **Suggest meaning** button: it
sends that word and its sentence to the small model `gpt-5-nano` and puts a
short English explanation on the back, for you to check and edit. Put the key
in `.env` in the same user folder, as the line `OPENAI_API_KEY=...`, or in the
variable of that name. Without a key the button is not shown and everything
else works. Keep the key out of this repository and out of OneDrive.

**Open in sentmine, a browser button (optional).** The `extension/` folder is
an extension for Edge and Chrome. In `edge://extensions` (or
`chrome://extensions`) switch on Developer mode, choose Load unpacked and pick
the `extension` folder. With sentmine running, press the button and choose *Open
this page in sentmine* on a PDF or a web page: the PDF, or the page's text (only the selected part if you selected
some; otherwise the article without the site's menus), opens in sentmine's Read page. It reads a tab only when you press the
button, and sends it nowhere but sentmine on this computer. On Canvas's page about
a file it sends the file behind the Download link; for files on your computer,
use Open a file. The article is found with Mozilla's Readability
(`extension/vendor`, Apache 2.0).

**Cards from a web page, in a side panel.** Select something on a web page,
right-click it and choose *Make a card from this*. The selection can be
rough: sentmine takes the whole sentences it touches. A panel opens beside
the page:

- one word selected (a double-click): its card is made at once, with the
  word on the front and its sentence on the back;
- a few words (up to eight) inside one sentence, such as a name: their card
  is made at once, with that sentence, as a drag over a term in Read does;
- a selection with a term in **bold** in it, as Wikipedia and course books
  mark the term they define: the card for that term is made at once, with
  the sentences as its passage;
- anything else waits in the panel as a clip: click a word for its card, or
  drag over the term it explains.

Every card has the same shape: the term on the front, the passage on the
back with the term in bold; **Make it cloze** hides the term instead.
Clips are kept apart from the text in Read; *Remove* takes a clip away, and
its cards stay until you send or download them. The button's *Show my clips
beside the page* opens the panel without a new clip. The right-click lets
the extension read that one tab, only then: it takes the paragraph around
the selection (to find whole sentences) and any bold phrase in it, and sends
them nowhere but sentmine on this computer.

The first design, a command-line tool that picks the words from a
known-words list, still works: `sentmine passage.txt --known known.txt
--deck new.apkg`.

To work on it and run the tests: `pip install -e ".[dev]"`, then `pytest`.
