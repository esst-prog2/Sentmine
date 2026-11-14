## 1. Content in the page

- [x] 1.1 `/` and `/cards` put the first data into the page, escaped so it cannot end the script; tests with the test client, including a text with `</script>`
- [x] 1.2 Read and My cards draw from it in the first frame, and ask the app if it is missing; verify frame by frame in headless Edge

## 2. The switch and the words

- [x] 2.1 The fade between pages, header still, none under reduced motion
- [x] 2.2 Words cached under the PDF's version; a test that another version is not cached

## 3. Wrap-up

- [x] 3.1 Rerun the place, click and drag checks; the whole suite; `openspec validate smooth-switch --strict`
