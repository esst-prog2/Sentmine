"""A PDF shown as its own pages: each page as a picture, and where each word of the text is on it.

The text the reading page works on comes from document.read_pdf, which drops running heads,
rejoins broken words and joins lines. locate() finds each word of that text again among the
characters on the pages, by matching runs of letters in order. The rules are in
openspec/specs/pdf-pages.
"""

import re
import unicodedata
import zlib
from dataclasses import dataclass
from difflib import SequenceMatcher

import pypdfium2
import pypdfium2.raw as pdfium_c

from sentmine.document import PDFIUM
from sentmine.reading import clickable_words

PICTURE_WIDTH = 1600  # pixels; sharp enough for a wide panel on a high-density screen
CHUNK = 1500  # runs of letters matched at a time, so a long book does not take long
_LETTERS = re.compile(r"[^\W\d_]+")

Place = tuple[int, int]  # (page, character index on the page)
Box = tuple[int, int, float, float, float, float]  # (sentence, word, left, top, width, height), fractions of the page


@dataclass
class Pages:
    document: pypdfium2.PdfDocument  # kept open to draw its pages; used only while holding PDFIUM
    sizes: list[tuple[float, float]]  # each page's width and height, in points
    boxes: list[list[Box]]  # each page's word boxes


def _letters(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def _characters(text_page) -> list[str]:
    """Each character of a page by its index; the two halves of a pair such as 𝑋 both get the whole character."""
    codes = [pdfium_c.FPDFText_GetUnicode(text_page.raw, index) for index in range(text_page.count_chars())]
    characters = []
    for index, code in enumerate(codes):
        if 0xD800 <= code < 0xDC00 and index + 1 < len(codes) and 0xDC00 <= codes[index + 1] < 0xE000:
            characters.append(chr(0x10000 + ((code - 0xD800) << 10) + (codes[index + 1] - 0xDC00)))
        elif 0xDC00 <= code < 0xE000:
            characters.append("")  # read with the first half
        else:
            characters.append(chr(code))
    return characters


def _page_runs(document) -> tuple[list[str], list[list[Place]], list[list[tuple]], list[tuple]]:
    """The runs of letters on all pages, where each letter is, every character's box, and each page's frame."""
    runs, places, boxes, frames = [], [], [], []
    for number, page in enumerate(document):
        frames.append(page.get_bbox())  # (left, bottom, right, top): the part of the page that is shown
        text_page = page.get_textpage()
        page_boxes = []
        run, run_places = "", []
        for index, character in enumerate(_characters(text_page)):
            page_boxes.append(text_page.get_charbox(index, loose=True))
            letters = [letter for letter in _letters(character) if letter.isalpha()]  # "ﬁ" is two letters
            if letters:
                run += "".join(letters)
                run_places += [(number, index)] * len(letters)
            elif character:
                if run:
                    runs.append(run)
                    places.append(run_places)
                run, run_places = "", []
        if run:
            runs.append(run)
            places.append(run_places)
        boxes.append(page_boxes)
        text_page.close()
        page.close()
    return runs, places, boxes, frames


def _match(text: list[str], page: list[str], places: list[list[Place]]) -> dict[int, list[Place]]:
    """For each run of letters of the text, where its letters are on the pages, if found."""
    found: dict[int, list[Place]] = {}
    start, page_start = 0, 0
    while start < len(text):
        end = min(len(text), start + CHUNK)
        page_end = min(len(page), page_start + 2 * CHUNK + 200)
        matcher = SequenceMatcher(None, text[start:end], page[page_start:page_end], autojunk=False)
        moved = page_start
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    found[start + i1 + k] = places[page_start + j1 + k]
                if i2 - i1 >= 3:  # a lone short match may be far away by chance; do not follow it
                    moved = page_start + j2
            elif tag == "replace" and "".join(text[start + i1 : start + i2]) == "".join(page[page_start + j1 : page_start + j2]):
                # the same letters cut differently: a word broken at a line end, or "doesn't" against "doesn" "t"
                letters = [place for j in range(page_start + j1, page_start + j2) for place in places[j]]
                at = 0
                for i in range(start + i1, start + i2):
                    found[i] = letters[at : at + len(text[i])]
                    at += len(text[i])
        page_start = moved
        start = end
    return found


def _rectangles(places: list[Place], boxes: list[list[tuple]]) -> list[tuple[int, float, float, float, float]]:
    """The letters of one word as one rectangle per line, in points: (page, left, bottom, right, top)."""
    out: list[list] = []
    for page, index in places:
        left, bottom, right, top = boxes[page][index]
        last = out[-1] if out else None
        if last and last[0] == page and bottom < last[4] and top > last[2] and left >= last[1] - 1:
            last[1], last[2], last[3], last[4] = min(last[1], left), min(last[2], bottom), max(last[3], right), max(last[4], top)
        else:
            out.append([page, left, bottom, right, top])
    return [tuple(rectangle) for rectangle in out]


def locate(data: bytes, sentences: list[str]) -> Pages:
    """The pages of a PDF, with a box for each word of `sentences` (the text read from it) found on them."""
    with PDFIUM:
        document = pypdfium2.PdfDocument(data)
        page_runs, places, char_boxes, frames = _page_runs(document)

    text_runs, owners = [], []
    for number, sentence in enumerate(sentences):
        for index, word in enumerate(clickable_words(sentence)):
            for run in _LETTERS.findall(_letters(word.text)):
                text_runs.append(run)
                owners.append((number, index))

    letters_of: dict[tuple[int, int], list[Place]] = {}
    for run, run_places in _match(text_runs, page_runs, places).items():
        letters_of.setdefault(owners[run], []).extend(run_places)

    sizes = [(right - left, top - bottom) for left, bottom, right, top in frames]
    boxes: list[list[Box]] = [[] for _ in frames]
    for (sentence, word), word_places in letters_of.items():
        for page, left, bottom, right, top in _rectangles(word_places, char_boxes):
            frame_left, frame_bottom, frame_right, frame_top = frames[page]
            width, height = frame_right - frame_left, frame_top - frame_bottom
            boxes[page].append((
                sentence, word,
                round((left - frame_left) / width, 5), round((frame_top - top) / height, 5),
                round((right - left) / width, 5), round((top - bottom) / height, 5),
            ))
    for page_boxes in boxes:
        page_boxes.sort(key=lambda box: (box[0], box[1]))  # reading order, so a drag selects in order
    return Pages(document, sizes, boxes)


def _png(width: int, height: int, rows: bytes) -> bytes:
    def chunk(kind: bytes, body: bytes) -> bytes:
        return len(body).to_bytes(4, "big") + kind + body + zlib.crc32(kind + body).to_bytes(4, "big")

    header = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])  # 8-bit RGB
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 6)) + chunk(b"IEND", b"")


def picture(pages: Pages, number: int, width: int = PICTURE_WIDTH) -> bytes:
    """Page `number` (from 0) drawn as a PNG about `width` pixels wide."""
    with PDFIUM:
        page = pages.document[number]
        bitmap = page.render(scale=width / page.get_width(), rev_byteorder=True)  # RGB, no alpha
        stride, drawn_width, drawn_height = bitmap.stride, bitmap.width, bitmap.height
        buffer = bytes(bitmap.buffer)
        bitmap.close()
        page.close()
    row = drawn_width * 3
    rows = b"".join(b"\x00" + buffer[y * stride : y * stride + row] for y in range(drawn_height))
    return _png(drawn_width, drawn_height, rows)
