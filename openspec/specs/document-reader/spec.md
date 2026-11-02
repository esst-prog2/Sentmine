# document-reader Specification

## Purpose
TBD - created by archiving change document-reader. Update Purpose after archive.

## Requirements

### Requirement: Loading a file
The reading page SHALL let the reader choose a `.pdf` or `.txt` file. Its text SHALL replace the current text and cards, as pasting a text does, and the page SHALL ask first if there are cards that would be lost. A `.txt` file SHALL be read as UTF-8. The file SHALL be read on the reader's computer; it SHALL NOT be stored or sent to any other machine. After loading, the page SHALL say how many pages were read and, if any had no text, how many.

#### Scenario: A PDF with text
- **WHEN** the reader chooses a PDF of three pages that all contain text
- **THEN** the text appears on the page, every word can be picked, and the message says 3 pages were read

#### Scenario: A text file
- **WHEN** the reader chooses a `.txt` file
- **THEN** its text appears on the page as if it had been pasted

### Requirement: Cleaning the text of a PDF
The app SHALL clean the text of a PDF by these rules, and SHALL NOT change the words in any other way:
- A line among the first or last three lines of a page SHALL be removed if the same line, ignoring digits, is among the first or last three lines of at least three pages. This removes running heads and page numbers. The rule SHALL be applied again until it removes nothing more, because removing marks can bring a running head into the top lines. In a PDF of fewer than three pages no line is removed by this rule.
- A line consisting only of digits among those lines SHALL be removed.
- A word broken by a hyphen at the end of a line SHALL be joined when the next line starts with a lower-case letter.
- A line that ends a sentence and is clearly shorter than the usual line of its page SHALL end a paragraph.
- The end of a page SHALL end a paragraph only if the page's last line ends a sentence; otherwise the sentence continues on the next page.

#### Scenario: A running head
- **WHEN** each of ten pages starts with `Preliminaries: Statistical and Causal Models` followed by its page number
- **THEN** that line does not appear in the text

#### Scenario: A hyphenated word
- **WHEN** one line ends with `signifi-` and the next begins `cantly more likely`
- **THEN** the text reads `significantly more likely`

#### Scenario: A real capitalised continuation
- **WHEN** one line ends with `post-` and the next begins `Brexit`
- **THEN** the hyphen is kept and the text reads `post- Brexit`

#### Scenario: A sentence across two pages
- **WHEN** a page ends in the middle of a sentence and the next page goes on with it
- **THEN** the card for a word in it shows the whole sentence

#### Scenario: Paragraphs
- **WHEN** a short line ending in a full stop is followed by more text
- **THEN** that text starts a new paragraph

### Requirement: Files that cannot be read
The app SHALL refuse the file with a message saying what is wrong, and SHALL leave the current text and cards as they are, when: the file is not a PDF or text file; the PDF is damaged; the PDF is locked with a password; no page of the PDF has any text, as with a scan; a text file is not valid UTF-8; or the file is empty or larger than 50 MB.

#### Scenario: A scan
- **WHEN** no page of a PDF has any text
- **THEN** the message says the PDF seems to be scanned, and the current text and cards stay

#### Scenario: Not a PDF
- **WHEN** a file named `.pdf` is not a PDF
- **THEN** the message says the file could not be read as a PDF

#### Scenario: Another kind of file
- **WHEN** the reader chooses a `.docx` file
- **THEN** the message says only PDF and text files can be read
