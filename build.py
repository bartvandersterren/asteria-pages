#!/usr/bin/env python3
"""
Genereer de 3 taalversies vanuit template + JSON-vertalingen.

Gebruik:
  python3 build.py          # bouwt alle 3 talen
  python3 build.py nl       # alleen NL
  python3 build.py en de    # EN + DE
"""

import json, os, sys

base = os.path.dirname(os.path.abspath(__file__))

LANGS = {
    'nl': ('wellness-arr-c.html',    'translations/nl.json'),
    'en': ('wellness-arr-c-en.html', 'translations/en.json'),
    'de': ('wellness-arr-c-de.html', 'translations/de.json'),
}

def build(lang):
    output_file, json_file = LANGS[lang]

    template_path = os.path.join(base, 'wellness-arr-c.template.html')
    json_path     = os.path.join(base, json_file)
    output_path   = os.path.join(base, output_file)

    with open(template_path, encoding='utf-8') as f:
        html = f.read()

    with open(json_path, encoding='utf-8') as f:
        translations = json.load(f)

    for key, value in translations.items():
        html = html.replace('{{' + key + '}}', value)

    # Sanity check: no unreplaced markers
    import re
    remaining = re.findall(r'\{\{[A-Z_]+\}\}', html)
    if remaining:
        print(f'  WARNING [{lang}]: unreplaced markers: {remaining}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  [{lang}] → {output_file}  ({len(html)} chars)')

langs_to_build = sys.argv[1:] if len(sys.argv) > 1 else list(LANGS.keys())

print(f'Building {langs_to_build}...')
for lang in langs_to_build:
    if lang not in LANGS:
        print(f'Unknown lang: {lang}')
        sys.exit(1)
    build(lang)
print('Done.')
