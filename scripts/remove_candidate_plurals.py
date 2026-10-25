#!/usr/bin/env python3
"""Exclude plural-only forms, preserving words with valid nonplural uses."""

import argparse
import json
from pathlib import Path

from build_candidate_words import read_frequency_file
from classify_candidate_words import RULES, classify, load_dictionary


# Reviewed noun pairs missing from the older WordNet vocabulary. These are
# explicit lexical pairs; ordinary verb endings are not enough to remove a word.
REVIEWED_NOUN_PAIRS = dict(zip(
    'carbs burbs coeds mages frags zines fests karts ankhs faves joeys jiffs '
    'noirs perps ragas rotis stims updos vapes veeps vlogs wikis banns eaves '
    'syncs faffs favas slogs bakes'.split(),
    'carb burb coed mage frag zine fest kart ankh fave joey jiff '
    'noir perp raga roti stim updo vape veep vlog wiki bann eave '
    'sync faff fava slog bake'.split(),
))

# Corps has the same spelling in singular and plural; it is not a plural of
# corp (corporation). Invariant singulars such as sheep/moose remain eligible.
INVARIANT_NOUNS = {'corps', 'sheep', 'moose', 'bison', 'swiss'}
OLD_REASON = 'plural noun form; excluded even when also used as a verb'
REASON = 'plural noun form with no reviewed independent nonplural use'
KEEP_REASON = 'valid independent nonplural use; a plural noun use does not disqualify the word'
NONPLURAL_TYPES = {
    'verb', 'adjective', 'adverb', 'auxiliary verb', 'pronoun', 'determiner',
    'preposition', 'conjunction', 'interjection', 'numeral', 'article',
}
# Exact noun entries alone do not establish a singular use: WordNet lists
# plural-only nouns such as jeans. These are reviewed independent noun senses.
INDEPENDENT_NOUN_USES = {
    'means': 'singular noun (a means to an end)',
    'media': 'collective/mass noun (communication media)',
    'fives': 'singular noun (the ball game)',
    'gents': 'singular noun (a public restroom)',
}


def nonplural_uses(word, classification):
    uses = set(classification['types']) & NONPLURAL_TYPES
    if word in INDEPENDENT_NOUN_USES:
        uses.add(INDEPENDENT_NOUN_USES[word])
    return sorted(uses)


def find_plurals(words, entries, exceptions):
    nouns = entries['noun']
    results = {}
    for word in words:
        if word in INVARIANT_NOUNS:
            continue
        if word in exceptions['noun']:
            roots = {base for base in exceptions['noun'][word]
                     if base != word and base in nouns}
        else:
            roots = {word[:-len(ending)] + replacement
                     for ending, replacement in RULES['noun']
                     if word.endswith(ending)
                     and word[:-len(ending)] + replacement != word
                     and word[:-len(ending)] + replacement in nouns}
        if word in REVIEWED_NOUN_PAIRS:
            roots.add(REVIEWED_NOUN_PAIRS[word])
        if roots:
            results[word] = sorted(roots)
    return dict(sorted(results.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wordnet-zip', type=Path, required=True)
    parser.add_argument('--data-dir', type=Path, default=Path('data'))
    parser.add_argument('--frequency-file', type=Path)
    args = parser.parse_args()
    data = args.data_dir
    words = (data/'candidate-words.txt').read_text().split()
    types = json.loads((data/'candidate-word-types.json').read_text())
    review = json.loads((data/'candidate-word-review.json').read_text())
    report = json.loads((data/'candidate-word-pruning.json').read_text())
    if set(words) != set(types) or not set(words) <= set(review):
        parser.error('Candidate, type, and review data must be consistent before removing plurals.')
    history_file = data/'candidate-word-plurals.json'
    history = json.loads(history_file.read_text()) if history_file.exists() else {}
    ambiguous_file = data/'candidate-word-ambiguous-forms.json'
    ambiguous = json.loads(ambiguous_file.read_text()) if ambiguous_file.exists() else {}
    # Reconsider only exclusions caused by the plural policy. Other exclusion
    # decisions (names, profanity, sexual medical terms) retain their authority.
    reconsider = {word for word in history
                  if review.get(word, {}).get('action') == 'exclude'
                  and review[word]['reason'] in {OLD_REASON, REASON}}
    pool = set(words) | reconsider
    entries, exceptions = load_dictionary(args.wordnet_zip)
    classifications = {word: classify(word, entries, exceptions) for word in sorted(pool)}
    possible = find_plurals(sorted(pool), entries, exceptions)
    plurals, restored = {}, set()
    for word, singulars in possible.items():
        uses = nonplural_uses(word, classifications[word])
        if uses:
            ambiguous[word] = {'singular_forms': singulars, 'nonplural_uses': uses}
            review[word] = {'action': 'keep', 'reason': KEEP_REASON,
                            'singular_forms': singulars, 'nonplural_uses': uses}
            report.pop(word, None)
            history.pop(word, None)
            if word not in words:
                restored.add(word)
        else:
            plurals[word] = singulars
            history[word] = singulars
            ambiguous.pop(word, None)
    for word, singulars in plurals.items():
        review[word] = {'action': 'exclude', 'reason': REASON, 'singular_forms': singulars}
        report[word] = {'reason': REASON, 'types': classifications[word]['types'], 'singular_forms': singulars}
    # A prior ambiguous morphology match can disappear after a dictionary fix.
    # It is safe to restore it only when a supported nonplural use is found.
    for word in reconsider - set(possible):
        uses = nonplural_uses(word, classifications[word])
        if uses:
            review[word] = {'action': 'keep', 'reason': KEEP_REASON, 'nonplural_uses': uses}
            report.pop(word, None)
            history.pop(word, None)
            restored.add(word)
    kept_pool = (set(words) | restored) - set(plurals)
    scores = read_frequency_file(args.frequency_file or data/'subtlexus-frequency.txt')
    kept = sorted(kept_pool, key=lambda word: (word not in scores, -scores.get(word, 0), word))
    exclusion_file = data/'excluded-candidate-words.txt'
    existing = exclusion_file.read_text()
    existing = '\n'.join(line for line in existing.splitlines()
                         if line.split('#', 1)[0].strip() not in restored) + '\n'
    excluded = {line.split('#', 1)[0].strip() for line in existing.splitlines()}
    additions = sorted(set(plurals) - excluded)
    if additions:
        existing = existing.rstrip() + \
            '\n\n# Plural-only noun forms; singulars are recorded in candidate-word-plurals.json.\n' + \
            '\n'.join(additions) + '\n'
    exclusion_file.write_text(existing)
    (data/'candidate-words.txt').write_text('\n'.join(kept) + '\n')
    (data/'candidate-word-types.json').write_text(json.dumps({w: classifications[w] for w in kept}, indent=2) + '\n')
    (data/'candidate-word-review.json').write_text(json.dumps(dict(sorted(review.items())), indent=2) + '\n')
    (data/'candidate-word-pruning.json').write_text(json.dumps(dict(sorted(report.items())), indent=2) + '\n')
    history_file.write_text(json.dumps(dict(sorted(history.items())), indent=2) + '\n')
    ambiguous_file.write_text(json.dumps(dict(sorted(ambiguous.items())), indent=2) + '\n')
    print(f'Restored {len(restored)} mixed-use words; excluded {len(history)} plural-only forms; kept {len(kept)} candidates.')


if __name__ == '__main__':
    main()
