#!/usr/bin/env python3
"""
Genereer taalversies vanuit templates + JSON-vertalingen.

Gebruik:
  python3 build.py                    # bouwt alles
  python3 build.py wellness           # alleen wellness template
  python3 build.py feedback           # alleen feedback template
  python3 build.py wellness nl        # wellness, alleen NL
"""

import json, os, re, sys

base = os.path.dirname(os.path.abspath(__file__))

TEMPLATES = {
    'wellness': {
        'template': 'wellness-arr-c.template.html',
        'langs': {
            'nl': ('wellness-arrangement.html',    'translations/nl.json'),
            'en': ('wellness-arrangement-en.html', 'translations/en.json'),
            'de': ('wellness-arrangement-de.html', 'translations/de.json'),
        },
    },
    'feedback': {
        'template': 'feedback.template.html',
        'langs': {
            'nl': ('feedback.html',    'translations/feedback-nl.json'),
            'en': ('feedback-en.html', 'translations/feedback-en.json'),
            'de': ('feedback-de.html', 'translations/feedback-de.json'),
        },
    },
    'happy-summer': {
        'template': 'happy-summer.template.html',
        'langs': {
            'nl': ('happy-summer-arrangement.html',    'translations/happy-summer-nl.json'),
            'en': ('happy-summer-arrangement-en.html', 'translations/happy-summer-en.json'),
            'de': ('happy-summer-arrangement-de.html', 'translations/happy-summer-de.json'),
        },
    },
    'najaar': {
        'template': 'najaar.template.html',
        'langs': {
            'nl': ('najaarsarrangement.html',    'translations/najaar-nl.json'),
            'en': ('najaarsarrangement-en.html', 'translations/najaar-en.json'),
            'de': ('najaarsarrangement-de.html', 'translations/najaar-de.json'),
        },
    },
    'welkom': {
        'template': 'welkom.template.html',
        'langs': {
            'nl': ('welkom.html',    'translations/welkom-nl.json'),
            'en': ('welkom-en.html', 'translations/welkom-en.json'),
            'de': ('welkom-de.html', 'translations/welkom-de.json'),
        },
    },
}

def add_mews_language(html, lang):
    """Voeg &language=<code> toe aan alle Mews-deeplink-URL's. Alleen EN/DE;
    NL blijft byte-identiek. Dekt statische hrefs, JS-deeplinks met/zonder
    voucher en de openBooking params-array."""
    code = {'en': 'en-US', 'de': 'de-DE'}.get(lang)
    if not code:
        return html
    q = '&language=' + code
    # 1. Statische voucher-URL (href/string met inline code): ?mewsVoucherCode=CODE
    html = re.sub(r'(mewsVoucherCode=[A-Za-z0-9_-]+)', r'\1' + q, html)
    # 2. JS-deeplink MET voucher (arrangementen): '?mewsVoucherCode=' + VOUCHER
    html = html.replace(
        "+ '?mewsVoucherCode=' + VOUCHER",
        "+ '?mewsVoucherCode=' + VOUCHER + '" + q + "'")
    # 3. JS-deeplink ZONDER voucher (kamers): MEWS_BASE + '?mewsStart=' + toYMD(checkin)
    html = html.replace(
        "MEWS_BASE + '?mewsStart=' + toYMD(checkin)",
        "MEWS_BASE + '?mewsStart=' + toYMD(checkin) + '" + q + "'")
    # 4. openBooking params-array (kamers): var params = [];
    html = html.replace(
        "var params = [];",
        "var params = ['language=" + code + "'];")
    # 5. Inline Mews-widget: de Distributor-config negeert 'language:', dus taal
    #    via de API-methode zetten zodra de widget klaar is (dit is wat de
    #    boekingsmodule daadwerkelijk in de juiste taal opent).
    html = html.replace(
        "window.mewsApi=api;",
        "window.mewsApi=api;if(api.setLanguageCode)api.setLanguageCode('" + code + "');")
    return html


def inject_welkom_booking():
    """Geef de welkom-pagina's dezelfde 3-staps boekingsmodule als de
    arrangementen (inline Mews-widget + datepicker-overlay), met de welkom-
    voucher. Bron per taal = de al-gebouwde, gelokaliseerde arrangementpagina.
    Idempotent via <!--WELKOM-BK--> markers; CTA-deeplinks worden herbedraad
    naar window.openBookingPopup(). Draait als post-stap na build('welkom')."""
    SRC = {
        '':    ('happy-summer-arrangement.html',    'WELKOM'),
        '-en': ('happy-summer-arrangement-en.html', 'WELCOME'),
        '-de': ('happy-summer-arrangement-de.html', 'WILLKOMMEN'),
    }
    START, END = '<!--WELKOM-BK-START-->', '<!--WELKOM-BK-END-->'
    for suffix, (arr_file, voucher) in SRC.items():
        welkom_path = os.path.join(base, 'welkom' + suffix + '.html')
        arr_path = os.path.join(base, arr_file)
        if not (os.path.exists(welkom_path) and os.path.exists(arr_path)):
            print(f'  [welkom-booking/{suffix or "nl"}] overgeslagen (bron ontbreekt)')
            continue
        arr = open(arr_path, encoding='utf-8').read()
        w = open(welkom_path, encoding='utf-8').read()

        def between(a, b, inclusive_end=True):
            i = arr.index(a); j = arr.index(b, i)
            return arr[i:(j + len(b)) if inclusive_end else j]

        def enclosing_script(keyword):
            k = arr.index(keyword)
            s = arr.rindex('<script', 0, k)
            e = arr.index('</script>', k) + len('</script>')
            return arr[s:e]

        mews_head = between('<!-- Mews BookingEngine -->', '<!-- End Mews BookingEngine -->')
        cs = arr.rindex('/*', 0, arr.index('.bk-overlay {'))
        ce = arr.rindex('/*', 0, arr.index('.ec-overlay {'))
        bk_css = arr[cs:ce].rstrip()
        bk_markup = between('<div class="bk-overlay"', '<!-- ══ DINER', inclusive_end=False).rstrip()
        dp_js = enclosing_script('MONTH_NAMES')
        bk_js = enclosing_script('/* ══ BOOKING POPUP')

        # Welkom-voucher in de booking-JS zetten (arrangement had z'n eigen code)
        bk_js = re.sub(r"var VOUCHER\s*=\s*'[^']*';",
                       "var VOUCHER = '" + voucher + "';", bk_js, count=1)

        # Oude injectie verwijderen (idempotent)
        w = re.sub(re.escape(START) + '.*?' + re.escape(END), '', w, flags=re.S)

        # In <head>: widget-script + overlay-CSS
        head_block = ('\n' + START + '\n' + mews_head + '\n<style>\n' + bk_css
                      + '\n</style>\n' + END + '\n')
        w = w.replace('</head>', head_block + '</head>', 1)

        # Vóór </body>: overlay-markup + datepicker-JS + booking-JS
        body_block = ('\n' + START + '\n' + bk_markup + '\n' + dp_js + '\n'
                      + bk_js + '\n' + END + '\n')
        w = w.replace('</body>', body_block + '</body>', 1)

        # CTA's: Mews-deeplinks vervangen door de popup-trigger
        w = re.sub(r'href="https://app\.mews\.com/distributor/[^"]*"',
                   'href="#" onclick="window.openBookingPopup();return false;"', w)

        with open(welkom_path, 'w', encoding='utf-8') as f:
            f.write(w)
        print(f'  [welkom-booking/{suffix or "nl"}] geinjecteerd (voucher {voucher})')


def build(template_name, lang):
    config = TEMPLATES[template_name]
    output_file, json_file = config['langs'][lang]

    template_path = os.path.join(base, config['template'])
    json_path     = os.path.join(base, json_file)
    output_path   = os.path.join(base, output_file)

    with open(template_path, encoding='utf-8') as f:
        html = f.read()

    with open(json_path, encoding='utf-8') as f:
        translations = json.load(f)

    for key, value in translations.items():
        html = html.replace('{{' + key + '}}', value)

    # Mews-boekingslinks in de juiste taal openen (alleen EN/DE)
    html = add_mews_language(html, lang)

    # Sanity check: no unreplaced markers
    remaining = re.findall(r'\{\{[A-Z_]+\}\}', html)
    if remaining:
        print(f'  WARNING [{template_name}/{lang}]: unreplaced markers: {remaining}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  [{template_name}/{lang}] → {output_file}  ({len(html)} chars)')

# Parse args: optional template name + optional lang codes
args = sys.argv[1:]
templates_to_build = []
langs_filter = []

for arg in args:
    if arg in TEMPLATES:
        templates_to_build.append(arg)
    else:
        langs_filter.append(arg)

if not templates_to_build:
    templates_to_build = list(TEMPLATES.keys())

for tpl in templates_to_build:
    config = TEMPLATES[tpl]
    langs = langs_filter if langs_filter else list(config['langs'].keys())
    print(f'Building {tpl} [{", ".join(langs)}]...')
    for lang in langs:
        if lang not in config['langs']:
            print(f'  Unknown lang for {tpl}: {lang}')
            sys.exit(1)
        build(tpl, lang)

# Welkom krijgt dezelfde boekingsmodule als de arrangementen (post-stap,
# na build zodat de gelokaliseerde arrangement-bronnen bestaan).
if 'welkom' in templates_to_build:
    print('Injecting welkom booking module...')
    inject_welkom_booking()

print('Done.')
