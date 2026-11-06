"""Turn a document into the plain text the reading page works on.

clean_pages() holds the rules and knows nothing about PDFs; read_pdf() only gets the
text of each page out of the file. The rules are in openspec/specs/document-reader.
"""

import re
import statistics
import threading
from collections import Counter
from pathlib import Path

import pypdfium2

MOST_BYTES = 50 * 1024 * 1024
EDGE_LINES = 3  # how many lines at the top and bottom of a page may be running heads
REPEATS_ON_PAGES = 3  # a line on this many pages is a running head
SHORT_LINE = 0.85  # a line this much shorter than usual can end a paragraph

_ENDS_A_SENTENCE = re.compile(r"[.!?:][\"'”’)\]»]*$")
_BROKEN_WORD = re.compile(r"[^\W\d_]-$")
_DIGITS = re.compile(r"\d+")

SOFT_HYPHEN = "\x02"  # how pypdfium2 marks a word it found broken at a line end
PDFIUM = threading.Lock()  # pdfium must not be used by two requests at once; every use of it holds this


class DocumentProblem(ValueError):
    """The file cannot be read; the message says why, in plain words."""


def _edge_key(line: str) -> str:
    return " ".join(_DIGITS.sub("", line).lower().split())


def _edges(lines: list[str]) -> list[str]:
    return lines[:EDGE_LINES] + lines[-EDGE_LINES:]


def _without_running_heads(pages: list[list[str]]) -> list[list[str]]:
    seen = Counter()
    for lines in pages:
        seen.update({_edge_key(line) for line in _edges(lines)})
    repeated = {key for key, count in seen.items() if count >= REPEATS_ON_PAGES and key}
    cleaned = []
    for lines in pages:
        last = len(lines) - EDGE_LINES
        cleaned.append([
            line for number, line in enumerate(lines)
            if not ((number < EDGE_LINES or number >= last) and (_edge_key(line) in repeated or line.isdigit()))
        ])
    return cleaned


def _join_page(lines: list[str]) -> str:
    """One page: broken words rejoined, a blank line after a short line that ends a sentence."""
    usual = statistics.median(len(line) for line in lines)
    text = ""
    for number, line in enumerate(lines):
        following = lines[number + 1] if number + 1 < len(lines) else ""
        if _BROKEN_WORD.search(line) and following[:1].islower():
            text += line[:-1]  # no space: the word goes on at the start of the next line
            continue
        short = len(line) < SHORT_LINE * usual
        text += line + ("\n\n" if short and _ENDS_A_SENTENCE.search(line) and following else "\n")
    return text.rstrip("\n")


def clean_pages(pages: list[str]) -> str:
    """The text of a document, from the text of its pages."""
    pages = [page.replace(SOFT_HYPHEN, "") for page in pages]
    split = [[line.strip() for line in page.splitlines() if line.strip()] for page in pages]
    kept = split
    while True:  # removing marks can bring a running head into the top lines, so go on until nothing changes
        fewer = _without_running_heads(kept)
        if fewer == kept:
            break
        kept = fewer
    kept = [lines for lines in kept if lines] or [lines for lines in split if lines]  # identical pages keep their text
    text = ""
    for lines in kept:
        page = _join_page(lines)
        if not text:
            text = page
        elif _ENDS_A_SENTENCE.search(text):
            text += "\n\n" + page
        elif _BROKEN_WORD.search(text) and page[:1].islower():
            text = text[:-1] + page  # a word broken across the page break
        else:
            text += "\n" + page  # the sentence goes on: a single line break becomes a space
    return text


def _pages_of(data: bytes) -> list[str]:
    """The text of each page of a PDF. pypdfium2 also opens PDFs locked with an empty password."""
    with PDFIUM:
        return _pages_locked(data)


def _pages_locked(data: bytes) -> list[str]:
    try:
        document = pypdfium2.PdfDocument(data)
    except pypdfium2.PdfiumError as error:
        if "password" in str(error).lower():
            raise DocumentProblem("This PDF is locked with a password, so it cannot be read.") from None
        raise DocumentProblem("The file could not be read as a PDF. It may be damaged.") from None
    try:
        pages = []
        for page in document:
            text_page = page.get_textpage()
            pages.append(text_page.get_text_bounded())
            text_page.close()
            page.close()
        return pages
    except pypdfium2.PdfiumError:
        raise DocumentProblem("The file could not be read as a PDF. It may be damaged.") from None
    finally:
        document.close()


def read_pdf(data: bytes) -> tuple[str, int, int]:
    """The clean text of a PDF, how many pages it has, and how many of them have no text."""
    pages = _pages_of(data)
    empty = sum(1 for page in pages if not page.strip())
    text = clean_pages(pages)
    if not text.strip():
        raise DocumentProblem("This PDF has no text in it. It seems to be scanned, which sentmine cannot read yet.")
    return text, len(pages), empty


def read_file(name: str, data: bytes) -> tuple[str, str]:
    """The text of an uploaded file, and a message saying what was read."""
    if not data:
        raise DocumentProblem("The file is empty.")
    kind = Path(name).suffix.lower()
    if kind == ".pdf":
        text, pages, empty = read_pdf(data)
        read = f"Read {pages} page{'' if pages == 1 else 's'}."
        return text, read + (f" {empty} had no text." if empty else "")
    if kind == ".txt":
        try:
            return data.decode("utf-8-sig"), "Read the text file."
        except UnicodeDecodeError:
            raise DocumentProblem("This text file is not in UTF-8, so it cannot be read.") from None
    raise DocumentProblem("Only PDF and text (.txt) files can be read.")
