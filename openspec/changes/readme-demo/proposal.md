## Why

Section 1 of the README still shows the first reading app: a pasted paragraph, a Word / Definition switch, and Download as the only way out. Since then sentmine reads PDFs as their own pages, drags without a mode switch, suggests meanings, makes cloze cards, sends cards straight to Anki, and remembers earlier cards. Homework 8 asks for the demo section to show the project as it is now.

## What Changes

- The opening lines and section 1 of the README are rewritten as one session with a real course PDF: open it, click a word, Suggest meaning, drag a term and its definition into a cloze card, Send to Anki, meet the word again a week later, look at My cards.
- Every card and message in the demo is what the app makes; a test pastes the demo's two sentences into the app and checks the README against what comes out.
- The PDF is the solution manual of the course book. It is copyrighted, so it is named and quoted in two sentences, not put in the repository.

Not in this change: sections 2 to 6 of the README, which still describe the first reading app in places (the modes, "nothing is saved"); they are brought up to date in a later change.

## Capabilities

### New Capabilities
- `project-readme`: the README's demo shows what the app does, and stays checked against it.

### Modified Capabilities

None.

## Impact

- `README.md`: the opening lines and section 1.
- New `tests/test_readme_demo.py`.
- No change to the app.
