## ADDED Requirements

### Requirement: The PDF's links work
Each link in the PDF SHALL be clickable where it is on the page. A link inside the PDF SHALL show the page it points to, at the place on it when the PDF gives one; a link to a website SHALL open in a new tab, and only http, https and mailto addresses SHALL be used. Following a link SHALL make no card.

#### Scenario: A reference to another page
- **WHEN** the reader clicks a reference to a study question on another page
- **THEN** that page is shown, and no card is made

#### Scenario: An unsafe address
- **WHEN** a PDF has a link to a `javascript:` address
- **THEN** sentmine leaves that link out

### Requirement: Jumping through a PDF
While a PDF is open, a page bar SHALL show the page in view and SHALL let the reader type a page number to go to it. When the PDF has bookmarks, the bar SHALL offer them as Contents, each going to its page.

#### Scenario: A page number
- **WHEN** the reader types 40 in the page bar
- **THEN** page 40 is shown

#### Scenario: Contents
- **WHEN** the PDF has bookmarks and the reader chooses one in Contents
- **THEN** its page is shown
