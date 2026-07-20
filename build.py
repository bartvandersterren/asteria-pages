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
    'augustus-actie': {
        'template': 'augustus-actie.template.html',
        'langs': {
            'nl': ('augustus-actie.html', 'translations/augustus-actie-nl.json'),
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


# Detailpagina-media per kamer (bron van waarheid: kamerdetailpagina's /
# build_kamers.slides_for). Video eerst, dan foto's in detailvolgorde.
DETAIL_MEDIA = {
    'comfort':      ('videos/comfort.mp4',      ['fotos/kamer-comfort-a.webp', 'fotos/kamer-comfort-b.webp', 'fotos/kamer-comfort-c.webp', 'fotos/kamer-comfort-d.webp']),
    'comfort-3':    ('videos/comfort-3.mp4',    ['fotos/room-comfort-3-1.webp', 'fotos/room-comfort-3-2.webp', 'fotos/room-comfort-3-3.webp', 'fotos/room-comfort-3-4.webp']),
    'mindervalide': ('videos/mindervalide.mp4', ['fotos/room-mindervalide-1.webp', 'fotos/room-mindervalide-2.webp', 'fotos/room-mindervalide-3.webp', 'fotos/room-mindervalide-4.webp']),
    'royale':       ('videos/royale.mp4',       ['fotos/room-royale-1.webp', 'fotos/room-royale-2.webp', 'fotos/room-royale-3.webp', 'fotos/room-royale-4.webp']),
    'deluxe':       ('videos/deluxe.mp4',       ['fotos/room-deluxe-1.webp', 'fotos/room-deluxe-2.webp', 'fotos/room-deluxe-3.webp', 'fotos/room-deluxe-4.webp']),
    'junior-suite': (None,                       ['fotos/kamer-junior-suite.webp', 'fotos/kamer-junior-suite-2.webp']),
    'suite':        ('videos/suite.mp4',        ['fotos/room-suite-1.webp', 'fotos/room-suite-2.webp', 'fotos/room-suite-3.webp', 'fotos/room-suite-4.webp']),
    'bruidssuite':  ('videos/bruidssuite.mp4',  ['fotos/room-bruidssuite-1.webp', 'fotos/room-bruidssuite-2.webp', 'fotos/room-bruidssuite-3.webp', 'fotos/room-bruidssuite-4.webp']),
}


def fix_room_media(html):
    """Zet in alle ROOMS-objecten de kamer-media gelijk aan de detailpagina's
    (video + volledige fotoset in detailvolgorde). Alleen objecten met 'imgs:'
    (de room-datasets) worden aangeraakt."""
    for key, (video, imgs) in DETAIL_MEDIA.items():
        imgs_js = '[' + ', '.join("'" + s + "'" for s in imgs) + ']'
        vid_js = ("'" + video + "'") if video else 'null'
        for q in ("'", '"'):
            marker = q + key + q + ':'
            pos = 0
            while True:
                p = html.find(marker, pos)
                if p == -1:
                    break
                b = html.find('{', p)
                if b == -1 or b - (p + len(marker)) > 3:
                    pos = p + len(marker); continue
                depth = 0; j = b
                while j < len(html):
                    if html[j] == '{': depth += 1
                    elif html[j] == '}':
                        depth -= 1
                        if depth == 0: break
                    j += 1
                obj = html[b:j + 1]
                if 'imgs:' not in obj:
                    pos = j + 1; continue
                new_obj = re.sub(r"imgs:\s*\[[^\]]*\]", "imgs: " + imgs_js, obj, count=1)
                if re.search(r"video:\s*('[^']*'|null|None)", new_obj):
                    new_obj = re.sub(r"video:\s*('[^']*'|null|None)", "video: " + vid_js, new_obj, count=1)
                else:
                    new_obj = '{ video: ' + vid_js + ',' + new_obj[1:]
                html = html[:b] + new_obj + html[j + 1:]
                pos = b + len(new_obj)
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

        # Meerprijzen (upgrade-labels als '+€10 p.n.') uit de kamerkeuze-stap
        # halen: welkom is een algemeen welkomstaanbod, niet arrangement-specifiek.
        # De echte beschikbaarheidsprijs (priceLabel) blijft staan.
        bk_js = re.sub(r"upgrade:\s*'[^']*'", "upgrade: ''", bk_js)

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


def inject_actie_booking():
    """Geef de augustus-actie-pagina dezelfde 3-staps boekingsmodule als de
    arrangementen (zie inject_welkom_booking), maar met een DYNAMISCHE
    vouchercode: de cadeau-kiezer op de pagina zet window.ACTIE_VOUCHER en
    roept window.setActieVoucher() aan, zodat de popup en de deeplink-fallback
    altijd met de code van het gekozen cadeau boeken.
    Idempotent via <!--ACTIE-BK--> markers; draait als post-stap."""
    actie_path = os.path.join(base, 'augustus-actie.html')
    arr_path = os.path.join(base, 'happy-summer-arrangement.html')
    if not (os.path.exists(actie_path) and os.path.exists(arr_path)):
        print('  [actie-booking] overgeslagen (bron ontbreekt)')
        return
    arr = open(arr_path, encoding='utf-8').read()
    w = open(actie_path, encoding='utf-8').read()

    START, END = '<!--ACTIE-BK-START-->', '<!--ACTIE-BK-END-->'

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

    # Dynamische vouchercode: init vanaf de cadeau-kiezer, setter voor wissels
    bk_js = re.sub(
        r"var VOUCHER\s*=\s*'[^']*';",
        "var VOUCHER = window.ACTIE_VOUCHER || 'DINER';\n"
        "  window.setActieVoucher = function (v) { VOUCHER = v; };",
        bk_js, count=1)

    # Meerprijzen (upgrade-labels) uit de kamerkeuze-stap halen: de actie is
    # een algemeen cadeau-aanbod, niet arrangement-specifiek.
    bk_js = re.sub(r"upgrade:\s*'[^']*'", "upgrade: ''", bk_js)

    # Oude injectie verwijderen (idempotent)
    w = re.sub(re.escape(START) + '.*?' + re.escape(END), '', w, flags=re.S)

    head_block = ('\n' + START + '\n' + mews_head + '\n<style>\n' + bk_css
                  + '\n</style>\n' + END + '\n')
    w = w.replace('</head>', head_block + '</head>', 1)

    body_block = ('\n' + START + '\n' + bk_markup + '\n' + dp_js + '\n'
                  + bk_js + '\n' + END + '\n')
    w = w.replace('</body>', body_block + '</body>', 1)

    # CTA's: Mews-deeplinks vervangen door de popup-trigger
    w = re.sub(r'href="https://app\.mews\.com/distributor/[^"]*"',
               'href="#" onclick="window.openBookingPopup();return false;"', w)

    with open(actie_path, 'w', encoding='utf-8') as f:
        f.write(w)
    print('  [actie-booking] geinjecteerd (dynamische cadeaucode, default DINER)')


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

    # Kamer-media in ROOMS gelijk aan de detailpagina's (video + volledige fotoset)
    html = fix_room_media(html)

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

# Augustus-actie krijgt dezelfde boekingsmodule, met dynamische cadeaucode.
if 'augustus-actie' in templates_to_build:
    print('Injecting actie booking module...')
    inject_actie_booking()

print('Done.')
