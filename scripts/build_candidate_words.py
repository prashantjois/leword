#!/usr/bin/env python3
"""Build a filtered, frequency-ranked list of five-letter candidate words."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


WORD_RE = re.compile(r"^[a-z]+$")


def read_word_list(path: Path, min_length: int, max_length: int) -> set[str]:
    words: set[str] = set()
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith(("#", ";")):
                continue
            if ": " in line and re.match(r"^\d+\b", line):
                line = line.split(": ", 1)[1]
            word = re.split(r"\s+|\s*[<{(]", line, maxsplit=1)[0].lower()
            if min_length <= len(word) <= max_length and WORD_RE.fullmatch(word):
                words.add(word)
    return words


def read_exclude_file(path: Path) -> set[str]:
    excluded: set[str] = set()
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            word = line.split("#", 1)[0].strip().lower()
            if word:
                excluded.add(word)
    return excluded


def read_frequency_file(path: Path) -> dict[str, float]:
    scores: dict[str, float] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
            rows = csv.reader(handle, dialect)
        except csv.Error:
            rows = (line.split() for line in handle)

        for row in rows:
            fields = [field.strip() for field in row if field.strip()]
            word_index = next(
                (index for index, field in enumerate(fields) if WORD_RE.fullmatch(field.lower())),
                None,
            )
            if word_index is None:
                continue
            word = fields[word_index].lower()
            for field in fields[word_index + 1:]:
                try:
                    scores[word] = float(field.replace(",", ""))
                    break
                except ValueError:
                    continue
    return scores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word-list", type=Path, required=True)
    parser.add_argument("--frequency-file", type=Path, required=True)
    parser.add_argument("--exclude-file", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, default=Path("candidate-words.tsv"))
    parser.add_argument("--min-length", type=int, default=5)
    parser.add_argument("--max-length", type=int, default=5)
    args = parser.parse_args()

    for path in [args.word_list, args.frequency_file, *args.exclude_file]:
        if not path.is_file():
            parser.error(f"file does not exist: {path}")

    words = read_word_list(args.word_list, args.min_length, args.max_length)
    for path in args.exclude_file:
        words -= read_exclude_file(path)
    scores = read_frequency_file(args.frequency_file)
    rows = sorted(
        ((word, scores.get(word)) for word in words),
        key=lambda item: (item[1] is None, -(item[1] or 0), item[0]),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        for word, score in rows:
            handle.write(f"{word}\n")

    print(f"Wrote {len(rows):,} five-letter candidate words to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
