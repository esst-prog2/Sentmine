## ADDED Requirements

### Requirement: One shape for every card
Every card SHALL have the term on the front and the passage on the back, with every whole-word place of the term in the passage in bold. A card made from one word SHALL have the word, lower-cased and followed by its base form in brackets when that differs, on the front, and the sentence the word is in on the back, with the word in bold as written. The card SHALL keep whether it was made from one word, so that it is found again by its base form, as before.

#### Scenario: A word and a term look the same
- **WHEN** the reader makes a card from the word `skew` in `Outliers can skew the mean considerably.` and a card from the term `confounder` with the passage `A confounder is a variable.`
- **THEN** the first card shows `skew` on the front and `Outliers can **skew** the mean considerably.` on the back, and the second shows `confounder` and `A **confounder** is a variable.`

### Requirement: A rough selection is taken as whole sentences
A passage selected on a web page, or dragged in Read for a definition, SHALL be taken as the whole sentences it touches, with the sentences found in the text around it. A passage that is not found in the text SHALL be kept as it is.

#### Scenario: A selection that starts inside a word
- **WHEN** the reader selects `ers. Outliers can` in `The median resists outliers. Outliers can skew the mean. Next.`
- **THEN** the passage is `The median resists outliers. Outliers can skew the mean.`

### Requirement: Cards remembered in the earlier shape
A word card remembered before this change, with its sentence on the front and the word on the back, SHALL be shown as it was made, and SHALL NOT be offered as a cloze card.

#### Scenario: An old card in My cards
- **WHEN** the memory holds a word card with the front `Its owner sighed.` and the back `sighed (sigh)`
- **THEN** My cards shows `Its owner **sighed**.` on its front and `sighed (sigh)` on its back

### Requirement: Suggest meaning under the passage
*Suggest meaning* on a card made from one word SHALL ask with the word and its sentence and put the meaning under the passage, replacing the meaning it put there before when that is still there. The same request SHALL ask for the few words of the sentence that show the meaning; the card SHALL underline them on its back only when they are a part of the sentence, of at most eight words and not the whole sentence, and SHALL keep the meaning without an underline otherwise. The underline SHALL NOT be part of the text the reader edits, and an edit that changes those words SHALL drop it.

#### Scenario: Pressing it twice
- **WHEN** the reader presses Suggest meaning on the card for `skew`, then again
- **THEN** the back is the sentence and, under it, only the second meaning

#### Scenario: The words that show the meaning
- **WHEN** the model answers the meaning of `simultaneously` with the key `flipped simultaneously to determine`
- **THEN** the back shows those words of the sentence underlined, with `simultaneously` still in bold

#### Scenario: Words that are not in the sentence
- **WHEN** the model names words that are not in the sentence, or the whole sentence
- **THEN** the meaning is put on the card and nothing is underlined
