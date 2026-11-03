## 1. Theme

- [x] 1.1 Dark colours apply to `data-theme="dark"` as well as to a dark system without a choice; the contrast script still finds no pair below 4.5:1
- [x] 1.2 A theme button in both headers, remembered in local storage and set before the page is drawn; verify both scripts pass `node --check` and screenshots show both themes with the matching button label (the themes were set through the browser; pressing the button is task 3.2)

## 2. Width

- [x] 2.1 The text column is at most `min(50rem, 60%)`; verify in screenshots at 1920 and 1400 px

## 3. Wrap-up

- [x] 3.1 Run the whole suite and `openspec validate theme-switch --strict`
- [x] 3.2 Try the button on both pages in the browser (needs the reader)
