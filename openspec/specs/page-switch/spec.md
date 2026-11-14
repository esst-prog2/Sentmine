# page-switch Specification

## Purpose
Let the reader go between Read and My cards without an empty page or a jump: pages open with their content, the switch fades softly, and page words are cached.

## Requirements

### Requirement: Pages open with their content
The Read page and the My cards page SHALL each arrive with the data they first show (the reading state; the first list of cards with the search empty), so that they are drawn complete when they first appear. When that data is missing or cannot be read, the page SHALL ask the app for it as before. The data in the page SHALL be the same the app gives at `/api/state` and `/api/memory`, and SHALL NOT be able to end the script element that holds it.

#### Scenario: Back to Read on a PDF
- **WHEN** the reader is on page 40 of a PDF, opens My cards, and comes back with the Read link
- **THEN** the first frame of the Read page that shows the text shows page 40, with no frame of an empty reading area before it

#### Scenario: My cards
- **WHEN** the reader opens My cards
- **THEN** the cards are on the page in its first frame

#### Scenario: Text that looks like markup
- **WHEN** the text being read contains `</script>`
- **THEN** the page still opens and shows that text as text

### Requirement: A soft switch
In browsers that support view transitions between pages, going between Read and My cards SHALL fade the content while the header stays in place, for no longer than 0.2 s. When the system asks for reduced motion there SHALL be no fade.

#### Scenario: Reduced motion
- **WHEN** the system asks for reduced motion
- **THEN** the pages switch without a fade

### Requirement: Page words are cached with the PDF's version
The words of a PDF page SHALL be cacheable by the browser when asked for with the version of the PDF being read, and SHALL NOT be cached when asked for without it or with another version.

#### Scenario: Another PDF
- **WHEN** the reader opens a different PDF
- **THEN** its pages ask for their words under the new version, never getting the words of the old PDF
