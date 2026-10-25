# Candidate word types

`candidate-word-types.json` maps every word currently in `candidate-words.txt`
to its dictionary parts of speech. A word may have several types, for example
`regular noun`, `verb`, and `adjective`. The mapping is reference data; the game
does not import it or use it to select or reject words.

Each word has these fields:

- `types`: all supported classifications, or `unknown` if no match was found.
- `base_forms`: dictionary lemmas, including roots for inflected forms.
- `sources`: WordNet 3.0, the grammatical supplement, and/or reviewed overrides.
- `needs_review`: true when no supported classification was found.

WordNet covers nouns, verbs, adjectives, and adverbs. The generator adds common
pronouns, determiners, prepositions, conjunctions, interjections, numerals,
articles, and auxiliary verbs. For noun senses, WordNet instance relationships
and capitalized dictionary lemmas identify likely proper nouns. This is an
automatic dictionary classification, not a complete lexical or suitability audit.
Capitalization can be ambiguous; proper-noun tags and unfamiliar entries should
be reviewed before making exclusions. `needs_review: false` means a match was
found, not that every possible use has been checked. Missing dictionary entries
are not proof that a word is invalid. Proper nouns and regular nouns can both
apply to the same spelling.

Regenerate after changing the candidate list (Python 3.9+; no dependencies):

```bash
curl -fL https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip -o /tmp/leword-wordnet.zip
python3 scripts/classify_candidate_words.py --wordnet-zip /tmp/leword-wordnet.zip
```

Dictionary source: [Princeton WordNet](https://wordnet.princeton.edu/),
distributed as WordNet 3.0 in the [NLTK data repository](https://github.com/nltk/nltk_data).
The downloaded ZIP includes its license and is not bundled in this repository.

## Pruning the answer list

`scripts/candidate_word_policy.py` supplies reviewed type overrides for ordinary
words that WordNet misses or mislabels.
An override replaces the inferred types and adds `reviewed lexical override` to
the sources. Several types may still apply to one word.

`candidate-word-review.json` records an explicit keep/exclude decision and reason
for every entry considered in the review, including retained
words. Decisions reflect ordinary standalone usage and fairness as an answer.
Common adverbs, pronouns, auxiliaries, regional words, and established informal
words are eligible. A proper-name sense does not exclude a familiar common use.
Nationalities and demonyms, including regional and people/nation names, are
eligible even when normally capitalized. `ALLOWED_DEMONYMS` in the lexical
policy lists the reviewed entries and adds `demonym` to their type mappings.
Medical vocabulary, including conditions, clinical anatomy, treatments, and
related biomedical terms, is also eligible. `ALLOWED_MEDICAL_TERMS` lists the
reviewed entries and adds `medical term` to their mappings. Sexual medical
terms, genital/reproductive anatomy, and sexual fluids are excluded by gameplay
policy even when clinically valid. `SEXUAL_MEDICAL_TERMS` records these explicit
exceptions and is subtracted from the allowed medical vocabulary. Other medical
conditions, anatomy, and treatments remain eligible. Unrelated slang, personal
names, and brands still follow their individual review decisions.
Recognizable historical words, titles, and familiar older literary expressions
are eligible too. Being old or historical is not an exclusion reason by itself.
`ALLOWED_HISTORICAL_TERMS` records reviewed examples such as `reich`, `pasha`,
and `quoth`, with `historical term` added to the type mapping. Remaining unusual
variants and specialist expressions are judged individually for recognizability;
the historical exception does not automatically admit personal or place names.
There is no part-of-speech restriction or frequency threshold. Dictionary gaps
and low frequency never automatically disqualify a word. These are editorial
decisions and can be amended when a better case for a particular word emerges.

Plural-only noun forms are excluded, including regular plurals (`miles` →
`mile`) and irregular plurals (`women` → `woman`). A plural noun use does not
disqualify a word with a valid independent use as a verb, adjective, adverb,
another grammatical type, or an explicitly reviewed singular or collective noun.
This preserves `wants`, `knows`, `means`, `times`, `calls`, and `works`.
It also preserves `books` in "books a room" and `trees` as the verb meaning to
drive an animal up a tree. Noun-only plurals such as `women`, `teeth`, and `miles`
remain excluded. Invariant singular forms (`sheep`, `moose`, `corps`) and singular
words ending in s (`glass`, `virus`, `lupus`, `genus`) remain eligible.

`candidate-word-plurals.json` records excluded plural-only forms and their
singular noun matches. `candidate-word-ambiguous-forms.json` records eligible
mixed-use forms, their singular noun matches, and their independent uses.
`scripts/remove_candidate_plurals.py` uses WordNet morphology and irregular-noun
exceptions, reviewed noun pairs, grammatical classifications, and reviewed
singular/collective noun senses. An exact noun dictionary entry alone is not
evidence of singular usage, since dictionaries also list plural-only nouns.
Lexical overrides cover newer verbs such as `texts`, `shims`, and `vlogs`.
The script reconsiders exclusions from the superseded plural policy and restores
mixed-use forms automatically; unrelated exclusions remain authoritative.
Both histories are preserved on repeated runs. Review and pruning data preserve
the reasons and singular forms so ordinary pruning produces the same results.

After adding or rebuilding candidates and regenerating their types, run:

```bash
python3 scripts/remove_candidate_plurals.py --wordnet-zip /tmp/leword-wordnet.zip
```

`candidate-word-pruning.json` preserves the excluded entries, their reviewed
reasons, and their dictionary types. The type mapping is descriptive; it is not
the authority for eligibility.

Run from the repository root, after generating the type mapping above:

```bash
python3 scripts/prune_candidate_words.py
```

Pruning updates the candidate list, audit exclusion list, active type mapping,
and removal report together. Existing exclusion files still apply when building
a candidate list from a broad dictionary. Regenerate types and prune again after
rebuilding the candidates. The report persists across repeated runs. Newly added
words must receive an explicit review decision before pruning; the script
reports missing decisions instead of silently rejecting them. For a change from
exclude to keep, also remove that word from the exclusion file and regenerate
the candidate list from its original source.
