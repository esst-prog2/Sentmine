## ADDED Requirements

### Requirement: The place in the text is kept
The reading page SHALL remember, for the browser tab, where the reader is in the text being read: on a PDF, the page and how far down it; on a text, how far down the page. When the reading page is opened again in that tab and the same text is being read, it SHALL show that place. Reading a text, from the paste box or a file, SHALL start at the top. If the browser does not allow the page to store anything, the page SHALL work as before and start at the top.

#### Scenario: Back from My cards on a PDF
- **WHEN** the reader is on page 40 of a PDF, opens My cards, and comes back with the Read link
- **THEN** the page shows page 40 again

#### Scenario: A reload
- **WHEN** the reader is on page 12 of a PDF and reloads the page
- **THEN** the page shows page 12 again

#### Scenario: Another text
- **WHEN** the reader was on page 40 of one PDF, then opens a different PDF
- **THEN** the new PDF starts at page 1
