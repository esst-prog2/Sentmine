## MODIFIED Requirements

### Requirement: Readable in light and dark
The pages SHALL follow the system's light or dark setting until the reader chooses one with a button in the header. The choice SHALL apply to both pages and SHALL be remembered by the browser; if the browser cannot remember it, the pages SHALL still work and follow the system. In both themes, all text and the label of every button SHALL have a contrast of at least 4.5:1 with what is behind it. The browser's own parts SHALL follow the theme: selected text, the file button, scroll bars and form controls.

#### Scenario: The main button in dark mode
- **WHEN** the system is set to dark mode
- **THEN** the Download button's label has a contrast of at least 4.5:1 with the button

#### Scenario: Choosing dark on a light system
- **WHEN** the system is light and the reader presses the theme button
- **THEN** both pages turn dark, and stay dark after a reload

## ADDED Requirements

### Requirement: The text panel fits its text
On a wide window the text panel SHALL be no wider than its text needs at about 70 characters a line, and at most 60% of the window; the cards panel SHALL take the rest.

#### Scenario: A wide window
- **WHEN** the reading page is shown 1920 pixels wide
- **THEN** there is no empty strip beside the text inside the text panel, and the cards panel is wider than at 60%
