# command-line Specification

## Purpose

Defines how the `sentmine` command is run, what it prints, when it succeeds or fails, and what it promises never to touch.

## Requirements

### Requirement: Command and options
The tool SHALL be run as `sentmine PASSAGE [--known FILE] [--deck FILE] [--min-len N] [--force]`. `PASSAGE` is required and is a plain-text file. `--known` is optional. `--deck` is optional and defaults to the passage file name with the extension `.apkg`, in the current folder (`passage.txt` gives `passage.apkg`). `--min-len` is optional, defaults to 3, and SHALL be a whole number of at least 1. `--force` allows replacing an existing deck file. The tool SHALL have no `--report` option in this version.

#### Scenario: Default deck name
- **WHEN** `sentmine passage.txt` is run without `--deck`
- **THEN** the deck is written to `passage.apkg` in the current folder

#### Scenario: Invalid minimum length
- **WHEN** `--min-len abc` is given
- **THEN** the run exits with code 2, prints a message naming the problem, and writes nothing

### Requirement: Summary
On a run that finds at least one new word the tool SHALL print a summary to standard output with, in this order: the number of sentences and words read; the number of common words ignored; the number of already-known words skipped; the number of repeats collapsed; the number of cards written, the deck path, and the words that got cards in order of first appearance. Singular and plural SHALL agree with the counts.

#### Scenario: Demo summary
- **WHEN** the demo passage is processed with `--known known.txt --deck new.apkg`
- **THEN** the output says it read 3 sentences and 19 words, ignored 8 common words, skipped 5 already-known, collapsed 1 repeat, and wrote 5 new cards to `new.apkg`: stubborn, refused, sighed, resilient, equally

### Requirement: Exit codes
The tool SHALL exit with 0 when at least one card is written. It SHALL exit with 2, print a message naming the problem to standard error, and write no deck file when: the passage file is missing or unreadable; the `--known` file is given but missing or unreadable; no new word remains; the deck file exists and `--force` was not given; the deck file cannot be written; or the arguments are invalid.

#### Scenario: Success
- **WHEN** the passage contains at least one new word
- **THEN** the exit code is 0 and the deck is written

#### Scenario: Missing passage
- **WHEN** the passage file does not exist
- **THEN** the exit code is 2, the message names the missing file, and nothing is written

#### Scenario: Missing known file
- **WHEN** `--known` names a file that does not exist
- **THEN** the exit code is 2 and nothing is written

#### Scenario: No new word
- **WHEN** every word is common or known, or the passage is empty
- **THEN** the exit code is 2, no deck is written, the message says no new word remains, and the counts part of the summary is still printed to standard output

#### Scenario: Deck already exists
- **WHEN** the deck file exists and `--force` is not given
- **THEN** the exit code is 2 and the existing file is unchanged

#### Scenario: Replacing with force
- **WHEN** the deck file exists and `--force` is given
- **THEN** the deck is replaced and the exit code is 0

#### Scenario: Deck cannot be written
- **WHEN** the `--deck` path is in a folder that does not exist
- **THEN** the exit code is 2 and a message names the problem

### Requirement: Input files are never modified
The tool SHALL NOT modify the passage file or the known-words file in any case, including when a run fails.

#### Scenario: Files unchanged
- **WHEN** the tool runs, whether it succeeds or exits with 2
- **THEN** the passage and known files are byte-for-byte the same as before

### Requirement: Local only
The tool SHALL read and write only local files and SHALL NOT use the network, an account, or an external service.

#### Scenario: Offline
- **WHEN** the machine has no network connection
- **THEN** the tool works exactly as it does online
