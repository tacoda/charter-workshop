#!/usr/bin/env python3
"""Inline diagrams/*.png into workshop/index.html as data URIs.

Refuses to run if a note line would overflow its box, because mermaid does not
clip: it just draws the text past the yellow and nobody notices until print.
"""
import base64, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
PAGE = HERE.parent / "index.html"
CAP_SPAN, CAP_WIDE = 32, 44

def check():
    bad = []
    for f in sorted(HERE.glob("*.mmd")):
        for ln in f.read_text().splitlines():
            m = re.match(r"\s*Note over ([^:]+):\s*(.*)", ln)
            if not m:
                continue
            span = [x.strip() for x in m.group(1).split(",")]
            cap = CAP_WIDE if len(span) > 1 and span[0] in ("You", "O") else CAP_SPAN
            for seg in m.group(2).split("<br/>"):
                if len(seg) > cap:
                    bad.append(f"{f.name}: {len(seg)}>{cap}  {seg}")
    return bad

def main():
    bad = check()
    if bad:
        print("note lines over cap, fix these before rendering:")
        print("\n".join("  " + b for b in bad))
        return 1
    html = PAGE.read_text()
    for name in ("turn-with-charter", "turn-bare", "rungs-above"):
        png = HERE / f"{name}.png"
        uri = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
        pat = re.compile(rf'(<img class="diagram-img" data-diagram="{name}"[^>]*?src=")[^"]*(")')
        html, n = pat.subn(lambda m: m.group(1) + uri + m.group(2), html)
        if n != 1:
            print(f"expected 1 img for {name}, found {n}")
            return 1
        print(f"{name}: {png.stat().st_size:,} bytes inlined")
    PAGE.write_text(html)
    return 0

if __name__ == "__main__":
    sys.exit(main())
