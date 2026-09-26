#!/usr/bin/env python3
"""
Checks the translations of Axiris before they reach the app.

Run it from anywhere:  python translations/check.py
It compares every values-xx/strings.xml with the English source in values/strings.xml and fails
(exit code 1) on anything that would break the build or the app:

- the file is not valid XML;
- a key that does not exist in English, or a key of a different type (string, plurals, array...);
- a placeholder (%1$s, %d, ...) missing, added or changed;
- an apostrophe or a double quote without its backslash (write \\' and \\");
- an em dash, which Axiris never uses (use a comma or a middle dot instead).

Missing strings are not errors: they are listed, and the app shows them in English meanwhile.
The same checks run on every pull request (see .github/workflows).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = ('string', 'plurals', 'string-array', 'integer', 'bool')
# Not words but grammar: how the word clock counts in a language. Only the languages that need them
# write them (see translations/README.md), so they are never counted as missing
OPTIONAL = {'fuzzy_next_from', 'fuzzy_cases', 'fuzzy_hours_past', 'fuzzy_hours_to'}
PLACEHOLDER = re.compile(r'%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?[sdfxXeEgGc%]')


def read(path):
    """The resources of one file, by name: (type, [texts]). Raises ValueError on broken XML."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        raise ValueError('not valid XML: %s' % e)
    items = {}
    for el in root:
        if el.tag not in TYPES:
            continue
        name = el.get('name')
        if el.tag in ('plurals', 'string-array'):
            texts = [(item.get('quantity'), ''.join(item.itertext())) for item in el]
        else:
            texts = [(None, ''.join(el.itertext()))]
        items[name] = (el.tag, texts, el.get('translatable') == 'false')
    return items


def raw_texts(path):
    """The text of every element as written, escapes included, to see what the parser hides."""
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    out = []
    # Followed by a space or '>', so that <string-array> is not taken for a <string>
    for m in re.finditer(r'<(string|item)(?=[\s>])[^>]*>(.*?)</\1>', raw, re.S):
        line = raw.count('\n', 0, m.start()) + 1
        out.append((line, m.group(2)))
    return out


def placeholders(text):
    return sorted(p for p in PLACEHOLDER.findall(text) if p != '%%')


def check_language(base, folder):
    path = os.path.join(HERE, folder, 'strings.xml')
    errors, warnings = [], []
    try:
        items = read(path)
    except ValueError as e:
        return [str(e)], [], set()
    for line, text in raw_texts(path):
        if re.search(r"(?<!\\)'", text):
            errors.append("line %d: apostrophe without backslash, write \\'" % line)
        if re.search(r'(?<!\\)"', text):
            errors.append('line %d: double quote without backslash, write \\"' % line)
        if '—' in text:
            errors.append('line %d: em dash, use a comma or a middle dot instead' % line)
    for name, (kind, texts, untranslatable) in items.items():
        if name not in base:
            warnings.append('%s: not in the English file, it will be ignored' % name)
            continue
        base_kind, base_texts, base_untranslatable = base[name]
        if base_untranslatable or untranslatable:
            warnings.append('%s: not translatable, it will be ignored' % name)
            continue
        if kind != base_kind:
            errors.append('%s: is a %s in English, not a %s' % (name, base_kind, kind))
            continue
        if kind == 'plurals':
            # A language may drop the number in a quantity ("one day"), never add a new one
            allowed = set()
            for _, t in base_texts:
                allowed.update(placeholders(t))
            for quantity, t in texts:
                extra = set(placeholders(t)) - allowed
                if extra:
                    errors.append('%s (%s): placeholder %s is not in English' % (name, quantity, ', '.join(sorted(extra))))
        elif kind == 'string-array':
            if len(texts) != len(base_texts):
                errors.append('%s: %d items, English has %d' % (name, len(texts), len(base_texts)))
            else:
                for i, ((_, t), (_, b)) in enumerate(zip(texts, base_texts)):
                    if placeholders(t) != placeholders(b):
                        errors.append('%s, item %d: placeholders %s, English has %s' % (name, i + 1, placeholders(t), placeholders(b)))
        elif kind == 'string':
            if placeholders(texts[0][1]) != placeholders(base_texts[0][1]):
                errors.append('%s: placeholders %s, English has %s' % (name, placeholders(texts[0][1]), placeholders(base_texts[0][1])))
    return errors, warnings, set(items)


def main():
    base = read(os.path.join(HERE, 'values', 'strings.xml'))
    wanted = {k for k, v in base.items() if not v[2] and k not in OPTIONAL}
    folders = sorted(d for d in os.listdir(HERE) if d.startswith('values-') and os.path.isdir(os.path.join(HERE, d)))
    failed = False
    for folder in folders:
        errors, warnings, present = check_language(base, folder)
        missing = wanted - present
        done = len(wanted) - len(missing)
        print('%s: %d/%d translated' % (folder, done, len(wanted)))
        for w in warnings:
            print('  warning: ' + w)
        for e in errors:
            print('  ERROR: ' + e)
        if errors:
            failed = True
    if failed:
        print('\nSome translations have errors: fix the lines above and run the check again.')
        sys.exit(1)
    print('\nAll good!')


if __name__ == '__main__':
    main()
