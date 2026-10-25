#!/usr/bin/env python3
"""Download the full SUBTLEX-US word-frequency text file."""

import argparse
import io
from pathlib import Path
from urllib.request import Request, urlopen
import zipfile


DEFAULT_URL = "https://www.ugent.be/plone_portal/pp/experimentele-psychologie/en/research/documents/subtlexus/subtlexus2.zip"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="SUBTLEX-US ZIP URL")
    parser.add_argument("--output", type=Path, default=Path("subtlexus-frequency.txt"))
    args = parser.parse_args()

    request = Request(args.url, headers={"User-Agent": "leword2-wordlist-downloader/1.0"})
    with urlopen(request, timeout=60) as response:
        archive = response.read()

    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        candidates = [
            info for info in zipped.infolist()
            if not info.is_dir() and info.filename.lower().endswith(".txt")
        ]
        if len(candidates) != 1:
            raise RuntimeError("could not identify a single text file in the SUBTLEX-US archive")
        data = zipped.read(candidates[0])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"Downloaded {len(data):,} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
