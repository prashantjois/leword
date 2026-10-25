# Candidate-word generation

The project builds a filtered list of five-letter candidate words and orders
them by frequency.

## Inputs

- `data/subtlexus-frequency.txt` — raw SUBTLEX-US frequency data
- A broad English word list, such as an ESDB/SCOWL-derived list
- `data/inappropriate-words.txt` — excluded profanity and sexual terms
- `data/proper-names.txt` — excluded common names
- `data/excluded-candidate-words.txt` — audit exclusions for proper names,
  places, brands, contractions, abbreviations, non-words, and other
  incompatible entries

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
  --exclude-file data/excluded-candidate-words.txt \
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

## Dictionary type audit and pruning

See `data/candidate-word-types.md` for dictionary classification and the explicit
word-by-word decisions in `data/candidate-word-review.json`. Parts of speech and
frequency do not determine eligibility. After rebuilding candidates, review any
new words, regenerate their type mapping
and run `scripts/prune_candidate_words.py`. New removals are added to
`data/excluded-candidate-words.txt`, with reasons preserved in
`data/candidate-word-pruning.json`. The active type mapping always covers the
remaining candidates exactly.

Plural-only noun forms are excluded; valid independent uses remain eligible.
After classifying a rebuilt list, run
`python3 scripts/remove_candidate_plurals.py --wordnet-zip /tmp/leword-wordnet.zip`
to identify additional plurals. Singular mappings are preserved in
`data/candidate-word-plurals.json`, while retained mixed-use forms are recorded
in `data/candidate-word-ambiguous-forms.json`. The decisions remain in effect
during subsequent regeneration. See `data/candidate-word-types.md` for details.
