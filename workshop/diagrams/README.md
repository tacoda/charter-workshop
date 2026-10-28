# Diagrams

The three sequence diagrams in `workshop/index.html` are **pre-rendered PNGs on
white**, inlined into the page as data URIs. The page makes no network request,
which is what the workshop promises the room.

`*.mmd` is the source. To change a diagram, edit the `.mmd`, then:

    node render.mjs .                     # render to PNG on white
    pngquant --quality 70-95 --force --ext .png *.png
    python3 inline.py                     # rewrite the data URIs in index.html

`render.mjs` needs Playwright and a Chromium binary; point `CHROME` at one.
Mermaid is fetched from a CDN **at render time only**, never by the page.

## The note-width rule

Mermaid sizes a note box to the participants it spans, and it does not wrap or
clip overflow: long lines simply run past the yellow. So every `Note over` line
is hand-broken with `<br/>` and capped:

- **32 characters** for a note spanning two adjacent participants
- **44 characters** for a note spanning the full diagram

`inline.py` enforces those caps and refuses to run if a line is over.
