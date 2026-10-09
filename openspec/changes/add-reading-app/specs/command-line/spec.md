## MODIFIED Requirements

### Requirement: Command and options
The tool SHALL be run as `sentmine [PASSAGE] [--known FILE] [--deck FILE] [--min-len N] [--force]`. Run with no arguments at all, `sentmine` SHALL start the reading app, print its address, and open it in the browser; it SHALL use port 8000, or the next free port up to 8010. With `PASSAGE`, a plain-text file, it SHALL run as the command-line tool. `--known` is optional. `--deck` is optional and defaults to the passage file name with the extension `.apkg`, in the current folder (`passage.txt` gives `passage.apkg`). `--min-len` is optional, defaults to 3, and SHALL be a whole number of at least 1. `--force` allows replacing an existing deck file. An option given without `PASSAGE` SHALL be an invalid argument. The tool SHALL have no `--report` option in this version.

#### Scenario: Default deck name
- **WHEN** `sentmine passage.txt` is run without `--deck`
- **THEN** the deck is written to `passage.apkg` in the current folder

#### Scenario: Invalid minimum length
- **WHEN** `--min-len abc` is given
- **THEN** the run exits with code 2, prints a message naming the problem, and writes nothing

#### Scenario: No arguments
- **WHEN** `sentmine` is run with no arguments
- **THEN** the reading app starts and its address is printed

#### Scenario: Options without a passage
- **WHEN** `sentmine --force` is run
- **THEN** the run exits with code 2 and the reading app does not start
