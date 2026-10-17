# Review 9: what should not be in git

Session 6, slide 22. Looking for large raw data files, keys, `.env` files and real people's data in the repository.

## How

- Every tracked file by size: `git ls-files -z | xargs -0 du -k | sort -rn`.
- Secrets: `git grep -i -E "api[_-]?key|secret|password|token|BEGIN (RSA|OPENSSH)"` and `git ls-files | grep -i -E "\.env|\.pem|\.key|credential|token"`.
- Personal data: email addresses (`git grep -E "...@..."`) and local paths (`git grep -F -e 'C:\Users' -e AppData`).
- `.gitignore` read in full.

## Found

1. **No keys, passwords, tokens or `.env` files.** The only hits for "secret" and "password" are ordinary words in the article and in the B1 word list.
2. **No email addresses** in the tracked files (commits use the GitHub no-reply address).
3. **Local paths in four test outputs.** `hw5/red_run.txt`, `green_run.txt`, `red_run_quotes.txt` and `green_run_quotes.txt` contain pytest's `rootdir: C:\Users\User\OneDrive - elte.hu\...`. It names the university and a generic Windows user, nothing private.
4. **About 2.9 MB of third-party files**, out of 4.5 MB in `spike/`: the Guardian page, four PDFs from Oxford and Cambridge, and four pages from Pattern Based Writing. They are someone else's copyrighted material in a public repository. But the Homework 4 brief asked for exactly this ("commit the raw response"), `spike/count_to_20.py` and `tests/test_real_article.py` read the article, and the professor reruns them.
5. **`.gitignore` had no rule for secrets.** Nothing secret exists yet, but the planned AI features (suggested meanings, reading PDF pages) will need an API key, and the obvious place for it, a `.env` file, would have been committed by `git add -A`.

## Done

- Added `.env`, `.env.*` and `*.key` to `.gitignore`, before any key exists. Checked: a new `.env` file does not show up in `git status`.
- Added `spike/SOURCES.md`, giving for each third-party file its source URL, owner and download date, and saying it is kept only as the evidence of the spike.
- Kept the third-party files and the local paths. As the slide says, `git rm` would not remove them from the history, and rewriting the history with `git filter-repo` would break the merges of pull requests #4 to #7, which the professor reads with `git log --merges`. The test outputs are evidence and stay exactly as they were produced.
