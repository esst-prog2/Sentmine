# Review 3: patched where it broke, not where it's wrong

Session 6, slide 17. Looking for a rule that was fixed one symptom at a time, so that nobody can state the rule any more.

## How

- `git log -- src/` for the history of every source file, and `git log --oneline | grep -i -E "fix|patch|edge case"` for fix-on-fix commits (none by that name).
- Followed the two places where a rule grew in steps, through the commits and `PLANNING_LOG.md`.

## Found

**1. Sentence splitting grew three exceptions in three steps.**

| Step | Why | Commit / log |
|---|---|---|
| Base rule: end at `.` `!` `?` followed by whitespace; an abbreviation list | MVP explore | log 2026-09-26, `f53c6f2` |
| A `!` or `?` followed by a lowercase word does not end a sentence | a spec scenario (`"Stop!" she said.`) contradicted the rule, found while building | log 2026-09-26, `f53c6f2` |
| A sentence does not end inside an open quotation | a real card (`restoke`) showed half a quote | log 2026-10-11, `e61e720` |

Each step was a decision about the rule, written into the spec with tests, not a patch for one input; the third replaced a symptom ("a lone closing mark on the card") with a rule ("quotes stay whole"). The three exceptions do not overlap: the third does not make the second unnecessary, because in `"Stop!" she said.` the quote is already closed at the `!`. But the code only showed the rule in pieces, spread over three helper functions, so it was hard to state it from the code.

**2. The common-word list was patched for one symptom.** In Homework 4 `could`, `would` and `however` showed up as cards, and 30 modal verbs and conjunctive adverbs were added to the list (`4c4612b`). That is the slide's pattern: the rule underneath ("function words are not vocabulary") was never written down, and the next missing function word would get its own patch. Since the change of direction, this list is used only by the first design's command-line tool; the reading app does not filter words at all, so the patching has stopped by itself.

## Done

- The whole splitting rule is now stated in one place, the docstring of `src/sentmine/sentences.py`, in the same order as the spec.
- No code change to the common-word list: it belongs to the first design, which the reading app replaced. Logged as a known weakness, not fixed.
