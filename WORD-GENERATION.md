# Candidate-word generation

The project builds a filtered list of five-letter candidate words and orders
them by frequency.

## Inputs

- `data/subtlexus-frequency.txt` — raw SUBTLEX-US frequency data
- A broad English word list, such as an ESDB/SCOWL-derived list
- `data/inappropriate-words.txt` — excluded profanity and sexual terms
- `data/proper-names.txt` — excluded common names

## Download frequency data

```bash
python scripts/download_subtlex.py \
  --output data/subtlexus-frequency.txt
```

## Generate the candidate list

```bash
python scripts/build_candidate_words.py \
  --word-list path/to/english-word-list.txt \
  --frequency-file data/subtlexus-frequency.txt \
  --exclude-file data/inappropriate-words.txt \
  --exclude-file data/proper-names.txt \
  --output data/candidate-words.txt
```

The generator:

1. Keeps lowercase alphabetic words of the requested length.
2. Removes words listed in the exclusion files.
3. Matches words to frequency scores.
4. Sorts candidates from most frequent to least frequent.
5. Writes one candidate word per line.

Useful options:

```text
--min-length N       Minimum word length (default: 5)
--max-length N       Maximum word length (default: 5)
--exclude-file PATH  Exclude one word per line; repeatable
--output PATH        Output path
```

## Output

The final list is:

`data/candidate-words.txt`
