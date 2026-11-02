## ADDED Requirements

### Requirement: Suggesting a meaning
When an API key is available, each word card in the preview SHALL have a Suggest meaning button. Pressing it SHALL ask the model `gpt-5-nano` for a short plain English explanation of the word as it is used in the card's sentence. The explanation SHALL go on the back of the card, on its own line under the word. Pressing the button again SHALL replace it with a new explanation. Definition cards SHALL NOT have the button.

#### Scenario: A meaning for a word
- **WHEN** the card for `skew` has the front `Outliers can skew it considerably.` and the reader presses Suggest meaning
- **THEN** the back of the card shows `skew`, and on the next line the explanation

#### Scenario: Pressing it again
- **WHEN** the card already has a suggested meaning and the reader presses Suggest meaning again
- **THEN** the back shows the word and only the new explanation

#### Scenario: A definition card
- **WHEN** the card is a definition card
- **THEN** it has no Suggest meaning button

### Requirement: The reader stays in charge of the meaning
The suggested meaning SHALL be shown in the preview before anything is saved, and SHALL be editable there like any other text on the card. The deck and the card memory SHALL hold the back as the preview shows it. No meaning SHALL be requested unless the reader presses the button.

#### Scenario: Editing a suggestion
- **WHEN** the reader changes a suggested meaning and downloads the deck
- **THEN** the deck and the memory hold the changed text

### Requirement: What leaves the computer
A request SHALL send only the word and the sentence on the card, with fixed instructions. It SHALL NOT send the rest of the text, other cards, or the card memory.

#### Scenario: One press
- **WHEN** the reader presses Suggest meaning on one card of a long text
- **THEN** the request contains that word and that sentence, and no other part of the text

### Requirement: The API key
The app SHALL use the key in the variable `OPENAI_API_KEY`, or else the line `OPENAI_API_KEY=` in the file `.env` in the reader's user folder (on Windows `%APPDATA%\sentmine\`, elsewhere `~/.local/share/sentmine/`). The key SHALL NOT be stored in the repository, printed, or sent to the page. Without a key the button SHALL NOT be shown and every other feature SHALL work as before.

#### Scenario: No key
- **WHEN** no key is available
- **THEN** the page shows no Suggest meaning button, and words, definitions, the preview, the download and My cards all work

### Requirement: When a request fails
If a request fails, the card SHALL stay as it was and the page SHALL say what went wrong in plain words: no network, a refused key, no credit or too many requests, or an empty answer.

#### Scenario: No network
- **WHEN** the reader presses Suggest meaning and OpenAI cannot be reached
- **THEN** the card is unchanged and a message says OpenAI could not be reached

#### Scenario: A refused key
- **WHEN** OpenAI refuses the key
- **THEN** the card is unchanged and a message says the key was refused
