"""Build skill/words.json, the word lists for skill/agentverbs.py, from WordNet 3.0 and VerbNet 3.

A noun is animate when its most frequent sense is a person or an animal, or when its second sense is
and SemCor tags it as a person or an animal at least half the time: `type` (7 of 143) is not. An agent
noun made from a verb, such as `solver` or `selector`, is animate only when it has at least one
SemCor tag in WordNet as a person or an animal. In code prose an untagged agent noun is the name of
a program, and a tagged one such as `teacher` or `owner` is the name of a person. A verb counts as
mental when its most frequent sense is cognition, communication or perception. A verb is an agent
verb when VerbNet puts its most frequent WordNet sense in a class in which each frame has an animate
subject: `send`, `steer`, `warn`. A verb is stative when its most frequent sense is a state or a
relation, such as `exist` or `depend`, and the review list of agentverbs.py leaves it out. The verb
list has every verb, so a sentence-initial imperative is
not read as a subject. agentverbs.py adds and removes words by hand on top of these lists, which
come from the WordNet and VerbNet classes alone.

The VerbNet directory has the class files, such as `send-11.1.xml`, and the VerbNet 3.0 license as
`LICENSE`, from https://verbs.colorado.edu/~mpalmer/projects/verbnet/license.3.0.txt. The NLTK
package of VerbNet 3 has no license file.

Usage:
    $ python3 build_words.py ~/nltk_data/corpora/wordnet ~/nltk_data/corpora/verbnet3 ../../../skill/words.json
    animate nouns: 14324, mind verbs: 1919, agent verbs: 1484, stative verbs: 426
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ANIMATE_CLASSES = frozenset({'noun.person', 'noun.animal'})
MIND_CLASSES = frozenset({'verb.cognition', 'verb.communication', 'verb.perception'})
STATIVE_CLASS = 'verb.stative'
# a role restricted to one of these is a role only a person or a group of people fills
ANIMATE_RESTRICTIONS = frozenset({'animate', 'organization', 'human'})
# `-ant` and `-ent` are left out: they make `student` (from `stud`) and `parent` (from `par`) into programs
AGENT_SUFFIXES = ('er', 'or')


def main() -> None:
    """Write words.json from the WordNet and VerbNet directories given on the command line."""
    wordnet_dir, verbnet_dir, words_json_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    class_names = (wordnet_dir / 'lexnames').read_text(encoding='utf-8').splitlines()
    noun_classes = readSynsetClasses(wordnet_dir / 'data.noun', class_names)
    verb_classes = readSynsetClasses(wordnet_dir / 'data.verb', class_names)

    verb_entries = readIndex(wordnet_dir / 'index.verb')
    mind = sorted(entry.lemma for entry in verb_entries if verb_classes[entry.offsets[0]] in MIND_CLASSES)
    verbs = sorted(entry.lemma for entry in verb_entries)
    stative = sorted(entry.lemma for entry in verb_entries if verb_classes[entry.offsets[0]] == STATIVE_CLASS)
    first_senses = readFirstSenseKeys(wordnet_dir / 'index.sense')
    animate_subject_senses = readAnimateSubjectSenses(verbnet_dir)
    agent = sorted(lemma for lemma in verbs if first_senses.get(lemma) in animate_subject_senses)
    tags = readNounTagCounts(wordnet_dir / 'index.sense', noun_classes)
    animate = sorted(
        entry.lemma
        for entry in readIndex(wordnet_dir / 'index.noun')
        if isAnimateNoun(entry, noun_classes, tags.get(entry.lemma, NounTags(0, 0)), verbs=frozenset(verbs))
    )

    notices = [(directory / 'LICENSE').read_text(encoding='utf-8') for directory in (wordnet_dir, verbnet_dir)]
    words = {
        'source': 'WordNet 3.0, VerbNet 3',
        'license': '\n\n'.join(notices),
        'animate_nouns': animate,
        'mind_verbs': mind,
        'agent_verbs': agent,
        'stative_verbs': stative,
        'verbs': verbs,
    }
    words_json_path.write_text(json.dumps(words, indent=0) + '\n', encoding='utf-8')
    print(f'animate nouns: {len(animate)}, mind verbs: {len(mind)}, ', end='')
    print(f'agent verbs: {len(agent)}, stative verbs: {len(stative)}')


def isAgentNoun(lemma: str, verbs: frozenset[str]) -> bool:
    """Tell whether a noun is a verb plus `-er` or `-or`: `solver`, `selector`, `compiler`, `scheduler`.

    Returns:
        True when the noun, without its suffix, is a verb, with or without a final `e` or a doubled
        last consonant.
    """
    suffix = next((suffix for suffix in AGENT_SUFFIXES if lemma.endswith(suffix)), None)
    if suffix is None:
        return False
    stem = lemma[: -len(suffix)]
    undoubled = stem[:-1] if len(stem) > 2 and stem[-1] == stem[-2] else stem
    return bool({stem, stem + 'e', undoubled} & verbs)


def isAnimateNoun(entry: IndexEntry, noun_classes: dict[str, str], tags: NounTags, *, verbs: frozenset[str]) -> bool:
    """Tell whether a noun is the name of a person or an animal in code prose.

    Returns:
        True when its first sense is a person or an animal, or its second sense is and at least half
        its SemCor tags are, and it is not an untagged agent noun made from a verb.
    """
    classes = [noun_classes[offset] for offset in entry.offsets[:2]]
    if classes[0] in ANIMATE_CLASSES:
        animate_sense = True
    else:
        animate_sense = classes[1:] != [] and classes[1] in ANIMATE_CLASSES and 0 < tags.total <= 2 * tags.animate
    return animate_sense and (tags.animate > 0 or not isAgentNoun(entry.lemma, verbs))


def readNounTagCounts(sense_index_path: Path, noun_classes: dict[str, str]) -> dict[str, NounTags]:
    """Count the SemCor tags of each noun: as a person or an animal, and in all.

    Returns:
        Lemma to its tag counts.
    """
    counts: dict[str, NounTags] = {}
    for line in sense_index_path.read_text(encoding='utf-8').splitlines():
        key, offset, _, tag_count = line.split()
        lemma, _, lexical = key.partition('%')
        if lexical.startswith('1:'):
            known = counts.get(lemma, NounTags(0, 0))
            animate = int(tag_count) if noun_classes[offset] in ANIMATE_CLASSES else 0
            counts[lemma] = NounTags(known.animate + animate, known.total + int(tag_count))
    return counts


def readFirstSenseKeys(sense_index_path: Path) -> dict[str, str]:
    """Map each verb to the sense key of its most frequent sense, such as `send%2:38:00`.

    Returns:
        Lemma to sense key, without the empty head-word fields that end a key in WordNet.
    """
    first: dict[str, str] = {}
    for line in sense_index_path.read_text(encoding='utf-8').splitlines():
        key, _, sense_number, _ = line.split()
        lemma, _, lexical = key.partition('%')
        if lexical.startswith('2:') and sense_number == '1':
            first[lemma] = key.rstrip(':')
    return first


def readAnimateSubjectSenses(verbnet_dir: Path) -> set[str]:
    """Collect the WordNet sense keys of every VerbNet class in which each frame has an animate subject.

    A subclass has the roles and frames of its class, plus the ones listed under it.

    Returns:
        Sense keys, such as `send%2:38:00`.
    """
    senses: set[str] = set()
    for class_path in sorted(verbnet_dir.glob('*.xml')):
        pending = [(ET.parse(class_path).getroot(), dict[str, bool](), list[ET.Element]())]
        while pending:
            node, inherited_roles, inherited_frames = pending.pop()
            roles = inherited_roles | {
                role.get('type', ''): needsAnimate(role.find('SELRESTRS'))
                for role in node.findall('THEMROLES/THEMROLE')
            }
            frames = inherited_frames + node.findall('FRAMES/FRAME')
            subjects = [roles.get(role, False) for role in map(subjectRole, frames) if role is not None]
            if subjects and all(subjects):
                for member in node.findall('MEMBERS/MEMBER'):
                    senses.update(key.lstrip('?') for key in (member.get('wn') or '').split())
            pending.extend((subclass, roles, frames) for subclass in node.findall('SUBCLASSES/VNSUBCLASS'))
    return senses


def needsAnimate(restrictions: ET.Element | None) -> bool:
    """Tell whether a VerbNet role's selectional restrictions admit only a person or a group of people.

    `[+animate | +organization]` does. `[+animate | +machine]` and a role with no restriction do not.

    Returns:
        True when every alternative of an `or`, or any condition of an `and`, is animate.
    """
    if restrictions is None:
        return False
    conditions = [child for child in restrictions if child.tag == 'SELRESTR']
    animate = [child for child in conditions if child.get('Value') == '+' and child.get('type') in ANIMATE_RESTRICTIONS]
    if restrictions.get('logic') == 'or':
        return bool(conditions) and len(animate) == len(restrictions)
    return bool(animate)


def subjectRole(frame: ET.Element) -> str | None:
    """Find the thematic role of the noun phrase before the verb in a VerbNet frame.

    Returns:
        The role, such as `Agent`, or None when nothing stands before the verb.
    """
    syntax = frame.find('SYNTAX')
    for part in syntax if syntax is not None else []:
        if part.tag == 'VERB':
            return None
        if part.tag == 'NP':
            return part.get('value')
    return None


def readSynsetClasses(data_path: Path, class_names: list[str]) -> dict[str, str]:
    """Map each synset offset in a WordNet data file to its lexicographer class, such as noun.person.

    Returns:
        Offset to class name.
    """
    classes: dict[str, str] = {}
    for line in data_path.read_text(encoding='utf-8').splitlines():
        if line.startswith(' '):
            continue
        offset, class_number = line.split(' ', 2)[:2]
        classes[offset] = class_names[int(class_number)].split()[1]
    return classes


def readIndex(index_path: Path) -> list[IndexEntry]:
    """Read a WordNet index file: each lemma with its synset offsets, most frequent sense first.

    Returns:
        One entry per single-word lemma. The check reads one token at a time, so a multi-word lemma
        never matches.
    """
    entries: list[IndexEntry] = []
    for line in index_path.read_text(encoding='utf-8').splitlines():
        if line.startswith(' '):
            continue
        fields = line.split()
        if '_' in fields[0]:
            continue
        pointer_count = int(fields[3])
        offsets = fields[4 + pointer_count + 2 :]
        entries.append(IndexEntry(fields[0], offsets))
    return entries


### vocabulary #########################################################################################


@dataclass(frozen=True)
class NounTags:
    animate: int
    total: int


@dataclass(frozen=True)
class IndexEntry:
    lemma: str
    offsets: list[str]


main()
