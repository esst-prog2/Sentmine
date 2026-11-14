## ADDED Requirements

### Requirement: Open the current tab in sentmine
The browser extension SHALL have one button that, when pressed, sends the content of the current tab to the sentmine app running on this computer and then shows sentmine's Read page. A PDF SHALL be sent as a file; a web page SHALL be sent as text, the selected text when there is a selection, otherwise the article without the site's menus, boxes, picture captions and reference marks. On Canvas's page about a file, the file behind its Download link SHALL be sent, downloaded with the reader's own login. The Read page SHALL show the new text from its top.

#### Scenario: A PDF in the browser
- **WHEN** the reader has a PDF open in a tab and presses the button
- **THEN** sentmine's Read page shows that PDF's pages

#### Scenario: A web page with a selection
- **WHEN** the reader has selected two paragraphs of an article and presses the button
- **THEN** sentmine reads those two paragraphs

#### Scenario: A Wikipedia article
- **WHEN** the reader presses the button on a Wikipedia article
- **THEN** sentmine's text starts with the article's title and first sentence, without the menus, the info box or `[1]` marks

#### Scenario: Canvas's page about a file
- **WHEN** the reader presses the button on the Canvas page of a PDF that has a Download link
- **THEN** sentmine's Read page shows that PDF's pages

#### Scenario: sentmine is not running
- **WHEN** no sentmine answers on ports 8000 to 8010
- **THEN** the button says that sentmine is not running and to start it with `sentmine` in a terminal, and nothing is sent

#### Scenario: A tab it cannot read
- **WHEN** the tab is a browser page or a local file
- **THEN** the button says what to do instead, and nothing is sent

### Requirement: Finding sentmine
The app SHALL answer `GET /api/hello` with its name, so the extension can tell sentmine from another program on the same port. The extension SHALL send nothing to a port that does not answer as sentmine.

#### Scenario: Another program on port 8000
- **WHEN** another program listens on port 8000 and sentmine on 8001
- **THEN** the extension sends to port 8001

### Requirement: Only the reader's own pages change the app
The app SHALL refuse a request that changes something (any method other than GET) when it carries an `Origin` header that is neither the app's own address nor a browser extension, answering 403 and changing nothing. Requests without an `Origin` (the command line, the tests) SHALL work as before.

#### Scenario: Another website sends a file
- **WHEN** a page on another website makes the browser post a file to sentmine
- **THEN** sentmine answers 403 and the text being read stays the same

#### Scenario: The extension sends a page
- **WHEN** the extension posts a text from its own `chrome-extension://` origin
- **THEN** sentmine reads it

### Requirement: The extension asks for little
The extension SHALL ask only for access to the tab the reader pressed the button on and to sentmine's address on this computer, and SHALL send the tab's content nowhere but there.

#### Scenario: Installing it
- **WHEN** the reader loads the extension
- **THEN** it does not ask to read all websites
