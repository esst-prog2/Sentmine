## Why

The pages follow the system's light or dark setting, but the reader could not see that dark mode exists and had no way to choose it inside the app. On a wide screen the text panel was also wider than its text, leaving an empty strip beside the text and less room for the cards.

## What Changes

- A button in the header of both pages switches between light and dark. The choice is remembered in the browser and applies to both pages. Until the reader chooses, the pages follow the system as before.
- The text panel is no wider than its text (about 70 characters a line, at most 60% of the window); the cards panel takes the rest.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `page-design`: the reader can choose light or dark; the text panel fits its text.

## Impact

- `src/sentmine/web/index.html` and `src/sentmine/web/cards.html` only. Nothing is sent to the server; the choice is kept in the browser's local storage.
