#!/usr/bin/env python3
"""Map candidate words to WordNet 3.0 parts of speech without dependencies."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from candidate_word_policy import (
    ALLOWED_DEMONYMS, ALLOWED_HISTORICAL_TERMS, ALLOWED_MEDICAL_TERMS, TYPE_OVERRIDES,
)


GRAMMATICAL_TYPES = {
    "pronoun": "these those which whose other there where what who whom them their they yours our ours hers his its itself myself yourself ourselves himself herself themselves something anything nothing everyone someone anyone nobody everybody thine whoso",
    "determiner": "these those which whose other every either neither some any each both much many few little fewer more most least less all enough such another this that",
    "preposition": "about above after along among below under until since round past near behind before beyond across against within without through toward towards upon into onto over off than worth except despite during per via amid circa versus plus minus like",
    "conjunction": "while until since where when after before though although whether because unless and but or nor yet for so than that hence once",
    "interjection": "hello hullo howdy adieu bravo cheers thank thanks bless sorry alas oops ouch phew shush whoop whops whups mercy wow hey ah oh huh hmm",
    "numeral": "three seven eight forty fifty first third fifth sixth tenth ninth sixty dozen score hundred thousand million zero one two four five six nine ten eleven twelve twenty thirty second fourth eighth last next",
    "article": "a an the",
    "auxiliary verb": "would could shall should might ought must can may will do does did have has had am is are was were been being",
    "adverb": "there where hence thence whence never ever often again still very quite rather almost today early later now then here why how also even only just too away together apart aside ahead forth twice thrice least most more less",
}

# WordNet's standard morphological substitutions, applied once and checked
# against the dictionary. Exception files cover forms such as went -> go.
RULES = {
    "noun": [("s", ""), ("ses", "s"), ("ves", "f"), ("xes", "x"),
             ("zes", "z"), ("ches", "ch"), ("shes", "sh"), ("men", "man"), ("ies", "y")],
    "verb": [("s", ""), ("ies", "y"), ("es", "e"), ("es", ""),
             ("ed", "e"), ("ed", ""), ("ing", "e"), ("ing", "")],
    "adj": [("er", ""), ("est", ""), ("er", "e"), ("est", "e")],
    "adv": [],
}
LABELS = {"noun": "regular noun", "verb": "verb", "adj": "adjective", "adv": "adverb"}


def load_dictionary(archive):
    entries = {pos: defaultdict(set) for pos in RULES}
    exceptions = {pos: {} for pos in RULES}
    with ZipFile(archive) as corpus:
        for pos in RULES:
            for line in corpus.read(f"wordnet/data.{pos}").decode().splitlines():
                if not line or not line[0].isdigit():
                    continue
                fields = line.split("|", 1)[0].split()
                count = int(fields[3], 16)
                pointer_start = 4 + 2 * count
                pointer_count = int(fields[pointer_start])
                instance = any(fields[pointer_start + 1 + 4 * i] == "@i"
                               for i in range(pointer_count))
                for i in range(count):
                    lemma = fields[4 + 2 * i]
                    for suffix in ("(a)", "(p)", "(ip)"):
                        lemma = lemma.removesuffix(suffix)
                    label = LABELS[pos]
                    if pos == "noun" and (instance or any(c.isupper() for c in lemma)):
                        label = "proper noun"
                    entries[pos][lemma.lower()].add(label)
            for line in corpus.read(f"wordnet/{pos}.exc").decode().splitlines():
                word, *bases = line.split()
                exceptions[pos][word] = bases
    return entries, exceptions


def classify(word, entries, exceptions):
    types, bases, sources = set(), set(), set()
    for pos in RULES:
        forms = {word}
        if word in exceptions[pos]:
            forms.update(exceptions[pos][word])
        # Verb exceptions may describe only one sense: taxis is also taxis
        # from taxi. Noun exceptions remain authoritative so genus is not
        # mistaken for a plural of the anatomical noun genu.
        if pos == 'verb' or word not in exceptions[pos]:
            for ending, replacement in RULES[pos]:
                if word.endswith(ending):
                    forms.add(word[:-len(ending)] + replacement)
        for form in sorted(forms):
            if form in entries[pos]:
                types.update(entries[pos][form])
                bases.add(form)
                sources.add("WordNet 3.0")
    for label, words in GRAMMATICAL_TYPES.items():
        if word in words.split():
            types.add(label)
            sources.add("grammatical supplement")
    if word in TYPE_OVERRIDES:
        types = set(TYPE_OVERRIDES[word])
        sources.add("reviewed lexical override")
    if word in ALLOWED_DEMONYMS:
        types.add("demonym")
        sources.add("reviewed nationality/demonym")
    if word in ALLOWED_MEDICAL_TERMS:
        types.add("medical term")
        sources.add("reviewed medical vocabulary")
    if word in ALLOWED_HISTORICAL_TERMS:
        types.add("historical term")
        sources.add("reviewed historical vocabulary")
    return {
        "types": sorted(types) if types else ["unknown"],
        "base_forms": sorted(bases),
        "sources": sorted(sources),
        "needs_review": not bool(types),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wordnet-zip", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, default=Path("data/candidate-words.txt"))
    parser.add_argument("--output", type=Path, default=Path("data/candidate-word-types.json"))
    args = parser.parse_args()
    words = args.candidates.read_text().split()
    entries, exceptions = load_dictionary(args.wordnet_zip)
    results = {word: classify(word, entries, exceptions) for word in words}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    counts = Counter(label for result in results.values() for label in result["types"])
    print(f"Mapped {len(results)} words to {args.output}")
    print(json.dumps(dict(sorted(counts.items())), indent=2))
    print("Needs review:", sum(item["needs_review"] for item in results.values()))


if __name__ == "__main__":
    main()
