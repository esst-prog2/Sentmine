## MODIFIED Requirements

### Requirement: The app runs on the reader's own computer
The reading app SHALL be a web page served only on the reader's own computer (address `127.0.0.1`). It SHALL NOT send the text or the cards to any other machine, with one exception: when the reader presses Suggest meaning, the word and its sentence are sent as the `ai-meanings` capability describes. It SHALL NOT need an account or an external service for anything else. It SHALL keep one text and its cards in memory. It SHALL write only two kinds of file: the deck the browser downloads, and the history of downloaded cards described by the `card-history` capability.

#### Scenario: Offline
- **WHEN** the machine has no network connection
- **THEN** the page opens and every feature works except suggesting a meaning, which says OpenAI could not be reached
