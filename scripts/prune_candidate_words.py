#!/usr/bin/env python3
"""Apply explicit word-by-word editorial decisions to the candidate list."""

import argparse
import json
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', type=Path, default=Path('data/candidate-words.txt'))
    parser.add_argument('--types', type=Path, default=Path('data/candidate-word-types.json'))
    parser.add_argument('--review', type=Path, default=Path('data/candidate-word-review.json'))
    parser.add_argument('--exclusions', type=Path, default=Path('data/excluded-candidate-words.txt'))
    parser.add_argument('--report', type=Path, default=Path('data/candidate-word-pruning.json'))
    args = parser.parse_args()
    words = args.candidates.read_text().split()
    types = json.loads(args.types.read_text())
    review = json.loads(args.review.read_text())
    if set(words) != set(types):
        parser.error('Regenerate the type mapping to exactly cover the current candidates first.')
    missing = sorted(set(words) - set(review))
    if missing:
        parser.error('Words need individual review before pruning: ' + ', '.join(missing))
    if any(row.get('action') not in {'keep', 'exclude'} or not row.get('reason')
           for row in review.values()):
        parser.error('Every reviewed word needs a keep/exclude action and an explanation.')

    kept = [word for word in words if review[word]['action'] == 'keep']
    removed = [word for word in words if review[word]['action'] == 'exclude']
    previous = json.loads(args.report.read_text()) if args.report.exists() else {}
    report = {}
    for word, decision in sorted(review.items()):
        if decision['action'] == 'exclude':
            entry = types.get(word, previous.get(word, {}))
            report[word] = {'reason': decision['reason'], 'types': entry.get('types', ['unknown'])}

    existing = args.exclusions.read_text()
    excluded = {line.split('#', 1)[0].strip() for line in existing.splitlines()}
    conflict = set(kept) & excluded
    if conflict:
        parser.error('Reviewed keeps still appear in exclusions: ' + ', '.join(sorted(conflict)))
    additions = sorted(set(report) - excluded)
    if additions:
        args.exclusions.write_text(existing.rstrip() +
            '\n\n# Individually reviewed exclusions; reasons in candidate-word-review.json.\n' +
            '\n'.join(additions) + '\n')
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    args.candidates.write_text('\n'.join(kept) + '\n')
    args.types.write_text(json.dumps({word: types[word] for word in kept}, indent=2) + '\n')
    print(f'Removed {len(removed)}; kept {len(kept)} candidates using individual review decisions.')
    print(json.dumps(dict(Counter(row['reason'] for row in report.values())), indent=2))


if __name__ == '__main__':
    main()
