from __future__ import annotations

import os
import socketserver
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("AIWORLD_PORT", "8000"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.address_string()}] {format % args}")


def main() -> None:
    with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"AI World project landing page is running at http://localhost:{PORT}")
        print(f"Universal API link: http://localhost:{os.environ.get('UNIVERSAL_API_PORT', '8080')}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
