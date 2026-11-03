# page-design Specification

## Purpose
TBD - created by archiving change polish-interface. Update Purpose after archive.

## Requirements

### Requirement: Readable in light and dark
The pages SHALL follow the system's light or dark setting until the reader chooses one with a button in the header. The choice SHALL apply to both pages and SHALL be remembered by the browser; if the browser cannot remember it, the pages SHALL still work and follow the system. In both themes, all text and the label of every button SHALL have a contrast of at least 4.5:1 with what is behind it. The browser's own parts SHALL follow the theme: selected text, the file button, scroll bars and form controls.

#### Scenario: The main button in dark mode
- **WHEN** the system is set to dark mode
- **THEN** the Download button's label has a contrast of at least 4.5:1 with the button

#### Scenario: Choosing dark on a light system
- **WHEN** the system is light and the reader presses the theme button
- **THEN** both pages turn dark, and stay dark after a reload

### Requirement: Controls show their state
Every button, link and text box SHALL look different when the pointer is over it and when it is reached with the keyboard, and a disabled button SHALL look disabled. A button whose request is waiting for the app SHALL be disabled and SHALL say that it is busy until the answer comes. Movement SHALL last at most 250 ms and SHALL be turned off when the system asks for reduced motion.

#### Scenario: Reaching a button with the keyboard
- **WHEN** the reader presses Tab until Download is reached
- **THEN** Download has a visible ring around it

#### Scenario: Downloading
- **WHEN** the reader presses Download
- **THEN** the button cannot be pressed again and says it is making the deck, until the file is given or a message says why not

### Requirement: One header on both pages
The reading page and My cards SHALL have the same header: the name sentmine, then links Read and My cards, with the current page marked.

#### Scenario: On My cards
- **WHEN** the reader opens My cards
- **THEN** the header shows Read as a link and My cards marked as the current page

### Requirement: Works on a phone
Both pages SHALL be usable at 390 pixels wide without scrolling sideways.

#### Scenario: A narrow window
- **WHEN** the reading page is shown 390 pixels wide with a text and two cards
- **THEN** the text and the cards are one below the other and nothing is cut off at the right

### Requirement: The text panel fits its text
On a wide window the text panel SHALL be no wider than its text needs at about 70 characters a line, and at most 60% of the window; the cards panel SHALL take the rest.

#### Scenario: A wide window
- **WHEN** the reading page is shown 1920 pixels wide
- **THEN** there is no empty strip beside the text inside the text panel, and the cards panel is wider than at 60%
