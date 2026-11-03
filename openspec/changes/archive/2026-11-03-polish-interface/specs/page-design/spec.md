## ADDED Requirements

### Requirement: Readable in light and dark
The pages SHALL follow the system's light or dark setting. In both, all text and the label of every button SHALL have a contrast of at least 4.5:1 with what is behind it. The browser's own parts SHALL follow the theme: selected text, the file button, scroll bars and form controls.

#### Scenario: The main button in dark mode
- **WHEN** the system is set to dark mode
- **THEN** the Download button's label has a contrast of at least 4.5:1 with the button

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
