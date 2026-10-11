## Context

`split_sentences` walks through each paragraph, looks at every `.`, `!` or `?` followed by whitespace, and ends a sentence there unless it is an abbreviation or is followed by a lowercase word. It knew nothing about quotation marks except that a closing one right after the end mark belongs to the sentence. A quote of two sentences was therefore cut in two, and the second half kept a closing mark with no opening one.

## Goals / Non-Goals

**Goals:**
- A card from quoted speech shows the whole quote with its introduction, as the reader decided (planning log, 2026-10-11).
- No change for text without quotation marks.

**Non-Goals:**
- Shortening a long quote automatically.
- Single quotation marks, and quotes that continue over several paragraphs.

## Decisions

**Count the marks in the sentence so far.** Before ending a sentence at a mark, look at the text from the start of the sentence up to and including the mark and any closing marks after it. If it has more opening than closing curly double marks or guillemets, or an odd number of straight double marks, the quotation is still open and the sentence goes on.
- Alternative: cut the quote out and give the card only the quoted words (option B). Not chosen by the reader; it loses who is speaking and needs a second rule.
- Alternative: drop the unmatched mark and keep one sentence. Not chosen by the reader.

**Single marks are not counted.** The closing single mark is the same character as the apostrophe in `don't`, so counting it would glue ordinary sentences together.

**A paragraph is the limit.** The count starts again in every paragraph, so a quotation that is never closed cannot swallow the rest of the text.

## Risks / Trade-offs

- [A long quote makes a long card: the `constituents` card is four sentences] -> Chosen knowingly; the reader can shorten any card in the preview.
- [A stray straight double mark, such as an inch sign, keeps a paragraph in one sentence] -> Limited to that paragraph and visible in the page.
- [Newspapers open every paragraph of a long quote and close only the last] -> Each such paragraph becomes one sentence; accepted for now.
