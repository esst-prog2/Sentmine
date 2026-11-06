## ADDED Requirements

### Requirement: The demo shows what the app does
Section 1 of the README SHALL show one reading session as the app runs it now. Every card front, card back and message it quotes SHALL be what the app makes from the same text, except a suggested meaning, which is the model's answer on the day it was asked and SHALL be said to come from the model. A copyrighted source SHALL be named and briefly quoted, not added to the repository.

#### Scenario: The word card
- **WHEN** the demo's sentence `Two fair coins are flipped simultaneously to determine the payoffs of two players in the town’s casino.` is pasted into the app and `simultaneously` is clicked
- **THEN** the card's front and back are the ones the README shows

#### Scenario: The cloze card
- **WHEN** the demo's sentence about `Simpson’s reversal` is pasted and marked as the definition of `Simpson’s reversal`
- **THEN** the card is a cloze card and its front is the one the README shows

#### Scenario: The messages
- **WHEN** two cards are sent to the deck `causal`, and a word with a card from 2026-11-07 is clicked again
- **THEN** the messages are the ones the README quotes

#### Scenario: The README drifts from the app
- **WHEN** a card or message in section 1 is changed so that it no longer matches the app
- **THEN** `tests/test_readme_demo.py` fails
