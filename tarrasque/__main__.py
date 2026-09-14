"""Run the service against a seeded in-memory database.

    python -m tarrasque            # serve on 8099
    python -m tarrasque --port N
"""

from __future__ import annotations

import argparse
from wsgiref.simple_server import make_server

from tarrasque import seed
from tarrasque.http import application


def main() -> None:
    parser = argparse.ArgumentParser(prog="tarrasque")
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()

    connection = seed.build()
    with make_server("127.0.0.1", args.port, application(connection)) as server:
        print(f"tarrasque listening on http://127.0.0.1:{args.port}")
        print("  try: curl -H 'Authorization: Bearer tk_live_mira_0001' \\")
        print(f"       http://127.0.0.1:{args.port}/v2/encounters/enc_ashfall_001")
        server.serve_forever()


if __name__ == "__main__":
    main()
