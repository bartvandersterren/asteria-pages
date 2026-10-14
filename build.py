#!/usr/bin/env python3
"""
Genereer taalversies vanuit templates + JSON-vertalingen.

Gebruik:
  python3 build.py                    # bouwt alles
  python3 build.py wellness           # alleen wellness template
  python3 build.py feedback           # alleen feedback template
  python3 build.py verblijfsverjaardag-v2   # lander W1 (reviewmuur uit content/)
  python3 build.py verblijfsverjaardag-v3   # zelfde sjabloon, blok 'zijkaart' -> verblijfsverjaardag.html (live sinds 14 okt 2026; oude lander -> verblijfsverjaardag-oud.html)
  python3 build.py herfst lente zomer winter   # seizoenslanders (visit.asteria.nl/<seizoen>)
  python3 build.py bedankt welkom-terug gemist verjaardag   # flow-landers op lander-w1 met zijkaart (zoals verblijfsverjaardag-v3)
  python3 build.py welkom-v2           # welkomstlander (code WELKOM) op lander-w1 met zijkaart -> welkom.html (live /welkom; oude NL -> welkom-oud.html)
  python3 build.py najaarsarrangement-v2   # arrangementsjabloon: lander-w1 met blokken zijkaart + arrangement
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
            'nl': ('welkom-oud.html', 'translations/welkom-nl.json'),   # oude NL-lander; /welkom = welkom-v2 (sinds 14 okt 2026)
            'en': ('welkom-en.html', 'translations/welkom-en.json'),
            'de': ('welkom-de.html', 'translations/welkom-de.json'),
        },
    },
    'augustus-actie': {
        'template': 'augustus-actie.template.html',
        'langs': {
            'nl': ('augustus-actie.html',    'translations/augustus-actie-nl.json'),
            'en': ('augustus-actie-en.html', 'translations/augustus-actie-en.json'),
            'de': ('augustus-actie-de.html', 'translations/augustus-actie-de.json'),
        },
        # De cadeau-/kamersecties staan letterlijk (NL) in de template; voor EN/DE
        # worden die na de {{KEY}}-pass vertaald via een geordende NL→taal-lijst.
        'literals': {
            'en': 'translations/augustus-actie-literals-en.json',
            'de': 'translations/augustus-actie-literals-de.json',
        },
    },
    # Lander-sjabloon 2026 (nieuwe huisstijl asteria.nl): alleen NL, noindex.
    # Andere flow-landers = zelfde template + eigen JSON + eigen fotos/l26-*.
    'verblijfsverjaardag': {
        'template': 'lander-2026.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag-oud.html', 'translations/verblijfsverjaardag-nl.json'),
        },
    },
    # Lander-sjabloon W1 Thuiskomst (blokkenkiezer 1a-2a-3a-4b-5a-6c-7a): alleen NL, noindex.
    # Reviewmuur wordt gevuld uit content/reviews-google-asteria.json (zie inject_reviews).
    'verblijfsverjaardag-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag-v2.html', 'translations/verblijfsverjaardag-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
    },
    # Variant v3 van dezelfde lander: zelfde sjabloon, blok 'zijkaart' aan = tegels, attentie en
    # kamerslider in een linker kolom met rechts een meelopende (sticky) boekkaart, zonder uitklaptab.
    'verblijfsverjaardag-v3': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag.html', 'translations/verblijfsverjaardag-v3-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    },
    # Flow-landers op hetzelfde sjabloon als verblijfsverjaardag-v3 (blok 'zijkaart'), alleen NL, noindex,
    # niet in sitemap. Per lander eigen translations/<slug>-nl.json + fotos/l26-<slug>-*.webp.
    # bedankt = BEDANKT (upgrade), welkom-terug = WELKOMTERUG (eerste ontbijt), gemist = GEMIST (upgrade),
    # verjaardag = VERJAARDAG (fles bubbels).
    **{s: {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    } for s in ('bedankt', 'welkom-terug', 'gemist', 'verjaardag')},
    # Welkomstlander (welkomstflow na nieuwsbriefaanmelding) op lander-w1 met zijkaart: code WELKOM,
    # welkomstgeschenk (bubbels, badjas, badlaken) bij het eerste verblijf. Alleen NL, noindex.
    # Blok 3a is het cadeaublok (variant 'cadeau', aan via CADEAU_ITEMS in de JSON, render_cadeau).
    # Sinds 14 okt 2026 de live /welkom (welkom.html); oude NL-lander -> welkom-oud.html (entry 'welkom'),
    # EN/DE blijven welkom-en/-de. /welkom-v2 -> 301 naar /welkom in _redirects.
    'welkom-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('welkom.html', 'translations/welkom-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    },
    # Arrangementen op lander-w1 (blokken 'zijkaart' + 'arrangement'; arrangement.css/.js): alleen NL, noindex, niet in sitemap.
    # Nieuw arrangement = translations/<slug>-nl.json (kopie van najaarsarrangement-v2-nl.json) + slug in deze lijst.
    # Opbouw en velden: zie CLAUDE.md (Arrangementen op lander-w1) en apply_arrangement(). Schakelaars in de JSON:
    # ZV_TOON (zondagvoordeel), WAAROM_TOON (Waarom Asteria, standaard aan), ANDERE_TOON (+ lijst '_andere').
    # Keys met een '_' vooraan en niet-tekstwaarden gaan niet de {{KEY}}-pass in.
    **{s: {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True, 'arrangement': True},
    } for s in ('najaarsarrangement-v2', 'wellness-arrangement-v3', 'oorlogsmuseum-arrangement-v2', 'limburg-arrangement-v2', 'weekend-aanbieding-v2', 'golfarrangement-v2')},
    # Seizoenslanders (blokkenkiezer 1c-2d-3a-4a-5c-6i-7b-8b): alleen NL, noindex, niet in sitemap.
    # Eén sjabloon (seizoen.template.html + seizoen.css + seizoen.js); alle seizoensinhoud in de JSON.
    # Per seizoen een entry met eigen translations/<seizoen>-nl.json. Reviewmuur zoals lander-w1.
    **{s: {
        'template': 'seizoen.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
    } for s in ('herfst', 'lente', 'zomer', 'winter')},
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
        '-oud': ('happy-summer-arrangement.html',   'WELKOM'),   # oude NL-lander (welkom-oud.html)
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


def inject_reviews(html, reviews_file, max_kaarten=24, max_tekens=260, voorkeur=None):
    """Vul de reviewmuur (lander-w1, blok 5a) uit een Google-reviews-JSON
    (formaat zoals zaalzeven-pages/content/reviews-google.json). Vervangt
    <!-- REVIEWS --> door maximaal 24 kaarten en vult {{GOOGLE_PROFIEL}} /
    {{GOOGLE_REVIEW_URL}} met profiel_url / review_url uit de JSON als de
    vertalings-JSON ze niet al gaf. Lange teksten worden op een woordgrens
    afgekapt (ongeveer 260 tekens) met een beletselteken.
    Arrangementen: 'voorkeur' = woorden (bijv. sauna, diner, ontbijt); reviews die er een noemen komen eerst
    (verder de volgorde van de JSON). {{REVIEWS_AANTAL}} wordt het aantal Google-reviews uit de JSON (2.280)."""
    from html import escape
    with open(os.path.join(base, reviews_file), encoding='utf-8') as f:
        data = json.load(f)
    ster = ('<svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 '
            '17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>')
    kaarten = []
    reviews = list(data.get('reviews') or [])
    if voorkeur:
        noemt = lambda r: any(w in (r.get('tekst') or '').lower() for w in voorkeur)
        reviews = [r for r in reviews if noemt(r)] + [r for r in reviews if not noemt(r)]
    for r in reviews[:max_kaarten]:
        tekst = ' '.join((r.get('tekst') or '').split())
        if len(tekst) > max_tekens:
            tekst = tekst[:max_tekens].rsplit(' ', 1)[0].rstrip(' ,.;:!?') + ' \u2026'
        n = max(1, min(5, int(r.get('sterren') or 5)))
        datum = (r.get('datum') or '').strip()
        meta = (escape(datum) + ' &middot; Google') if datum else 'Google'
        kaarten.append(
            '      <article class="kaart b5a-kaart">\n'
            f'        <span class="b5a-k-sterren" role="img" aria-label="{n} van 5 sterren">{ster * n}</span>\n'
            f'        <p>\u201c{escape(tekst, quote=False)}\u201d</p>\n'
            f'        <p class="b5a-naam">{escape(r.get("naam") or "Gast", quote=False)}<span>{meta}</span></p>\n'
            '      </article>')
    if not kaarten:
        print(f'  WARNING: geen reviews in {reviews_file}')
    html = html.replace('<!-- REVIEWS -->', '\n'.join(kaarten))
    profiel = data.get('profiel_url') or 'https://www.google.com/maps/search/?api=1&query=Hotel+Asteria+Venray'
    schrijf = data.get('review_url') or profiel
    if data.get('aantal'):
        html = html.replace('{{REVIEWS_AANTAL}}', f"{int(data['aantal']):,}".replace(',', '.'))
    html = html.replace('{{GOOGLE_PROFIEL}}', escape(profiel)).replace('{{GOOGLE_REVIEW_URL}}', escape(schrijf))
    return html


LADDER_ICOON = {
    'm2': '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
    'bed': '<path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8M2 16h20M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/>',
    'personen': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    'sauna': '<path d="M14 14.8V4a2 2 0 0 0-4 0v10.8a4 4 0 1 0 4 0z"/>',
    'bad': '<path d="M12 2.7l5.7 5.7a8 8 0 1 1-11.3 0z"/>',
    'zit': '<path d="M5 11V8a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v3M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM6 19v2M18 19v2"/>',
}


def render_ladder(cfg):
    """Upgradeblok 'A · Ladder-slider' (blok 3a-variant 'ladder') uit UPGRADE_LADDER in de vertalings-JSON:
    per stap twee kamerkaarten 'Je boekt' -> 'Upgrade' met een pijl, de winstregel eronder; teller,
    streepjes en vorige/volgende-knoppen erboven, één vaste voetregel. Eén stap per keer, geen lus,
    geen boekknop, geen prijzen. Vervangt <!-- UPGRADE_LADDER --> in lander-w1.template.html."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')
    ic = lambda pad, kl='as-icoon': f'<svg class="{kl}" viewBox="0 0 24 24" aria-hidden="true">{pad}</svg>'
    lab = cfg.get('labels', {})
    kamers, stappen = cfg['kamers'], cfg['stappen']
    n = len(stappen)

    def kaart(sleutel, upgrade):
        k = kamers[sleutel]
        specs = ''.join(f'<li><span class="b3l-ic">{ic(LADDER_ICOON[s[0]])}</span>{e(s[1])}</li>' for s in k['specs'])
        pil = (f'<span class="b3l-pil b3l-pil--up">{ic(LADDER_PIJL["op"])}{e(lab.get("upgrade", "Upgrade"))}</span>'
               if upgrade else f'<span class="b3l-pil">{e(lab.get("boekt", "Je boekt"))}</span>')
        return (f'<article class="b3l-kaart{" b3l-kaart--up" if upgrade else ""}">'
                f'<div class="b3l-foto"><img src="{a(k["foto"])}" alt="{a(k["alt"])}" width="1400" height="933" loading="lazy">{pil}</div>'
                f'<div class="b3l-inhoud">{pil}<h3>{e(k["naam"])}</h3><ul class="b3l-specs">{specs}</ul></div></article>')

    blokken = []
    for i, s in enumerate(stappen):
        van, naar = kamers[s['van']]['naam'], kamers[s['naar']]['naam']
        blokken.append(
            f'        <div class="b3l-stap" role="group" aria-roledescription="stap" aria-label="Stap {i + 1} van {n}: {a(van)} naar {a(naar)}"'
            + ('' if i == 0 else ' aria-hidden="true"') + '>\n'
            f'          <div class="b3l-route">{kaart(s["van"], False)}<span class="b3l-pijl" aria-hidden="true">'
            f'{ic(LADDER_PIJL["rechts"], "as-icoon b3l-pijl-r")}{ic(LADDER_PIJL["omlaag"], "as-icoon b3l-pijl-o")}</span>{kaart(s["naar"], True)}</div>\n'
            f'          <p class="b3l-winst"><span class="b3l-vink">{ic(LADDER_PIJL["vink"])}</span><span><b>{e(lab.get("erbij", "Je krijgt erbij:"))}</b> {e(s["winst"])}</span></p>\n'
            '        </div>')
    dots = ''.join(
        f'<button type="button" class="b3l-dot{" is-active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
        f'aria-label="Stap {i + 1}: {a(kamers[s["van"]]["naam"])} naar {a(kamers[s["naar"]]["naam"])}"></button>'
        for i, s in enumerate(stappen))
    nav = (f'      <div class="b3l-nav"><span class="b3l-tel" aria-live="polite"><b class="b3l-nu">1</b> van <b>{n}</b></span>'
           f'<div class="b3l-dots" role="tablist" aria-label="Upgradestappen">{dots}</div>'
           f'<div class="b3l-pijlen"><button type="button" class="as-pijl b3l-vorige" aria-label="Vorige stap" aria-disabled="true">{ic(LADDER_PIJL["links"])}</button>'
           f'<button type="button" class="as-pijl b3l-volgende" aria-label="Volgende stap">{ic(LADDER_PIJL["chev-r"])}</button></div></div>\n')
    return ('<div class="b3l" aria-roledescription="carrousel" aria-label="Zo ziet je upgrade eruit">\n' + nav
            + '      <div class="b3l-spoor strook-scroll" tabindex="0" aria-label="Upgradestappen, schuif of gebruik de pijltjestoetsen">\n'
            + '\n'.join(blokken) + '\n      </div>\n'
            + f'      <p class="b3l-voet">{e(cfg.get("voet"))}</p>\n    </div>')


def render_cadeau(items, voet):
    """Cadeaublok (blok 3a-variant 'cadeau') uit CADEAU_ITEMS in de vertalings-JSON: drie fotokaarten naast
    elkaar in de kaartstijl van het upgradeblok (b3l-kaart) met badge (standaard 'Gratis'), naam en één regel,
    daaronder één voetregel (CADEAU_VOET). Geen boekknop, geen prijzen. Telefoon: kaarten onder elkaar, foto
    links. Vervangt <!-- CADEAU_ITEMS --> in lander-w1.template.html; de intro is de tekst-key CADEAU_INTRO."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')

    def kaart(it):
        pil = f'<span class="b3l-pil b3l-pil--up">{e(it.get("badge", "Gratis"))}</span>'
        return (f'        <article class="b3l-kaart b3c-kaart" role="listitem">'
                f'<div class="b3l-foto"><img src="{a(it["foto"])}" alt="{a(it["alt"])}" width="1200" height="800" loading="lazy">{pil}</div>'
                f'<div class="b3l-inhoud">{pil}<h3>{e(it["naam"])}</h3><p class="b3c-regel">{e(it["regel"])}</p></div></article>')

    return ('<div class="b3c">\n      <div class="b3c-rij" role="list">\n'
            + '\n'.join(kaart(it) for it in items) + '\n      </div>\n'
            + f'      <p class="b3l-voet b3c-voet">{e(voet)}</p>\n    </div>')


LADDER_PIJL = {
    'links': '<path d="M15 18l-6-6 6-6"/>',
    'chev-r': '<path d="M9 18l6-6-6-6"/>',
    'rechts': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'omlaag': '<path d="M12 5v14M6 13l6 6 6-6"/>',
    'op': '<path d="M12 19V5M5 12l7-7 7 7"/>',
    'vink': '<path d="M20 6L9 17l-5-5"/>',
}


ATTENTIE_ICOON_STANDAARD = {
    'PUNT_TWEE_ICOON': '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
    'PUNT_DRIE_ICOON': '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    'PUNT_VIJF_ICOON': '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M9 16l2 2 4-4"/>',
}


def apply_blokken(html, aan):
    """Varianten binnen een sjabloon zonder template-taal. Een blok staat tussen
    <!--[naam[--> en <!--]naam]-->; <!--[!naam[--> ... <!--]!naam]--> is het omgekeerde.
    'aan' = de namen die in de build-config op True staan. Staat een blok aan, dan
    verdwijnen alleen de markers; staat hij uit, dan verdwijnt het hele blok. Een marker
    die alleen op zijn regel staat, neemt die regel mee (uitvoer zonder blok blijft dus
    byte-gelijk aan het sjabloon zonder markers)."""
    namen = set(re.findall(r'<!--\[(!?[a-z0-9-]+)\[-->', html))
    for naam in namen:
        kaal = naam.lstrip('!')
        houden = (kaal in aan) != naam.startswith('!')
        n = re.escape(naam)
        if houden:
            html = re.sub(r'(?m)^[ \t]*<!--[\[\]]' + n + r'[\[\]]-->[ \t]*\n', '', html)
            html = re.sub(r'<!--[\[\]]' + n + r'[\[\]]-->', '', html)
        else:
            html = re.sub(r'(?ms)^[ \t]*<!--\[' + n + r'\[-->.*?<!--\]' + n + r'\]-->[ \t]*\n', '', html)
            html = re.sub(r'(?s)<!--\[' + n + r'\[-->.*?<!--\]' + n + r'\]-->', '', html)
    return html


# Pil-iconen per soort in de kamerslider van een arrangement (blok 4b)
PIL_ICOON = {
    'inbegrepen': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>',
    'upgrade': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
    'toeslag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
}


VINK_SVG = ('<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/>'
            '<path d="M8 12.5l2.5 2.5 5.5-6"/></svg>')


def icoon(paden, cls='as-icoon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{paden}</svg>'


def apply_arrangement(html, data):
    """Arrangementblokken uit de lijsten in de JSON (alleen met blok 'arrangement'):
    - '_kamers': welke kamers (blok 4b), in welke volgorde, met pil en prijsregel per kaart, bijv.
      {"deluxe": {"pil": "Inbegrepen", "soort": "inbegrepen", "prijs_label": "vanaf", "prijs": "€ 128,50 p.p."},
       "suite": {"pil": "Upgrade", "soort": "upgrade", "prijs": "Upgrade mogelijk"}}.
      Sleutels = data-kamer in het sjabloon (comfort, comfort-3, royale, deluxe, junior-suite, suite, bruidssuite,
      mindervalide); soort inbegrepen (terracotta rand), upgrade of toeslag. 1 of 2 kamers: raster zonder
      slider, teller en lus (.ar-kamers; telefoon veegbaar met peek). Vanaf 3: de brede slider met lus zoals /bedankt,
      teller en streepjes volgen het aantal.
    - '_chips' (hero), '_inbegrepen' ({titel, regel, icoon}; vakje met lijnicoon, 2 kolommen),
      '_inbegrepen_fotos' ({img, alt, pos?}; fotoslider in het inbegrepen-blok, 4 tot 6), '_tijden' ({tekst, icoon}), '_faq' ({q, a}; eerste open;
      "zondag": true = alleen met ZV_TOON), '_andere' ({naam, url, img, alt, prijs?}).
    - 'ARR_NACHTEN' (getal, standaard 1): vast aantal nachten. Bij meer dan 1 krijgen de boekbalken
      data-nachten; arrangement.js zet het vertrek dan op aankomst + N (balk, widget en URL-fallback).
    - '_fotowolk': 12 foto's ({img, pos?} of een pad) die de vaste foto's van de fotowolk (blok 7a)
      in volgorde vervangen; SLOT_FOTO_A/B blijven staan. Zonder lijst blijft de vaste set."""
    from html import escape
    kamers = data.get('_kamers')
    if kamers:
        s = html.index('<div class="b4b-strook')
        voet = html.index('<div class="b4b-voet">', s)
        start = html.index('<article class="b4b-kaart">', s)
        eind = html.rindex('</article>', s, voet) + len('</article>')
        kaarten = {}
        for m in re.finditer(r'<article class="b4b-kaart">.*?</article>', html[start:eind], re.S):
            kaarten[re.search(r'data-kamer="([^"]+)"', m.group(0)).group(1)] = m.group(0)
        nieuw = []
        for key, cfg in kamers.items():
            if key not in kaarten:
                sys.exit(f'apply_arrangement: onbekende kamer {key!r} (kies uit {", ".join(kaarten)})')
            soort = cfg.get('soort', 'inbegrepen')
            pil = f'<span class="b4b-pil b4b-pil--{soort}">{PIL_ICOON[soort]}{escape(cfg["pil"], quote=False)}</span>'
            k = re.sub(r'<span class="b4b-pil">.*?</span>', lambda _: pil, kaarten[key], count=1, flags=re.S)
            if cfg.get('prijs'):
                lab = f'<span>{escape(cfg["prijs_label"], quote=False)}</span>' if cfg.get('prijs_label') else ''
                regel = f'<div class="ar-kprijs ar-kprijs--{soort}">{lab}<b>{escape(cfg["prijs"], quote=False)}</b></div>\n          '
                k = k.replace('<div class="b4b-knoppen">', regel + '<div class="b4b-knoppen">', 1)
            if soort == 'inbegrepen':
                k = k.replace('<article class="b4b-kaart">', '<article class="b4b-kaart ar-kaart-inbegrepen">', 1)
            nieuw.append(k)
        html = html[:start] + '\n        '.join(nieuw) + html[eind:]
        n = len(nieuw)
        if n <= 2:
            # raster: geen teller/streepjes/pijlen, geen .b4b-strook (dan laat lander-w1.js lus() hem met rust)
            html = re.sub(r'<div class="b4b-teller">.*?</button></div></div>', '', html, count=1, flags=re.S)
            html = html.replace('<div class="b4b-strook strook-scroll" tabindex="0" aria-label="Kamers, schuif voor meer">',
                                f'<div class="ar-kamers strook-scroll" data-n="{n}" aria-label="Kamers">', 1)
        else:
            html = html.replace('van <b>8</b></span>', f'van <b>{n}</b></span>', 1)
            stippen = ''.join(
                f'<button type="button" class="b4b-dot{" is-active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-label="Kamer {i + 1}"></button>'
                for i in range(n))
            html = re.sub(r'(<div class="b4b-dots"[^>]*>).*?(</div>)', lambda m: m.group(1) + stippen + m.group(2), html, count=1, flags=re.S)

    chips = ''.join(f'<li>{VINK_SVG}<span>{c}</span></li>' for c in data.get('_chips', []))
    html = html.replace('<!-- ARR_CHIPS -->', chips)
    inb = '\n'.join(
        f'            <li class="ar-inb-punt"><span class="ar-vak">{icoon(p.get("icoon", ""))}</span>'
        f'<span class="ar-inb-tekst"><b>{p["titel"]}</b><span>{p.get("regel", "")}</span></span></li>'
        for p in data.get('_inbegrepen', []))
    html = html.replace('<!-- ARR_INBEGREPEN -->', inb)
    fotos = data.get('_inbegrepen_fotos', [])
    if '<!-- ARR_INB_FOTOS -->' in html and not 4 <= len(fotos) <= 6:
        sys.exit(f'_inbegrepen_fotos: 4 tot 6 foto\'s nodig, niet {len(fotos)}')
    html = html.replace('<!-- ARR_INB_FOTOS -->', '\n'.join(
        f'            <figure class="ar-fs-dia"><img src="{escape(f["img"])}" alt="{escape(f.get("alt", ""))}"'
        + (f' style="object-position:{escape(f["pos"])}"' if f.get('pos') else '')
        + (' loading="lazy"' if i else '') + '></figure>'
        for i, f in enumerate(fotos)))
    html = html.replace('<!-- ARR_INB_BOLLEN -->', ''.join(
        f'<button type="button" class="ar-fs-bol{" is-aan" if i == 0 else ""}" data-fs-naar="{i}" aria-label="Foto {i + 1}"'
        + (' aria-current="true"' if i == 0 else '') + '></button>'
        for i in range(len(fotos))))
    tijden = ''.join(f'<li>{icoon(p.get("icoon", ""))}<span>{p["tekst"]}</span></li>' for p in data.get('_tijden', []))
    html = html.replace('<!-- ARR_TIJDEN -->', tijden)
    faq = [f for f in data.get('_faq', []) if data.get('ZV_TOON') or not f.get('zondag')]
    html = html.replace('<!-- ARR_FAQ -->', '\n'.join(
        f'          <details class="as-accordeon__item"{" open" if i == 0 else ""}><summary class="as-accordeon__kop">{f["q"]}</summary>'
        f'<div class="as-accordeon__paneel"><p>{f["a"]}</p></div></details>'
        for i, f in enumerate(faq)))
    pijl = '<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    html = html.replace('<!-- ARR_ANDERE -->', '\n'.join(
        f'        <a class="ar-ander" href="{escape(a["url"])}">'
        f'<span class="ar-ander-foto"><img src="{escape(a["img"])}" alt="{escape(a.get("alt", ""))}" loading="lazy"></span>'
        f'<span class="ar-ander-tekst"><b class="ar-ander-naam">{a["naam"]}</b>'
        + (f'<span class="ar-ander-prijs">{re.sub(r"(€\s?[0-9.,]+)", r"<b>\1</b>", a["prijs"])}</span>' if a.get('prijs') else '')
        + f'<span class="ar-ander-rond">{pijl}</span></span></a>'
        for a in data.get('_andere', [])))

    nachten = data.get('ARR_NACHTEN', 1)
    if not isinstance(nachten, int) or nachten < 1:
        sys.exit(f'ARR_NACHTEN moet een heel getal van 1 of meer zijn, niet {nachten!r}')
    if nachten > 1:
        html = html.replace(' data-boekbalk ', f' data-boekbalk data-nachten="{nachten}" ')

    wolk = data.get('_fotowolk')
    if wolk:
        s = html.index('<section class="sec b7a"')
        e = html.index('<div class="b7a-inhoud">', s)
        vast = [m for m in re.finditer(r'<img class="b7a-foto[^"]*" data-h="[^"]+" src="[^"]+" alt="" loading="lazy">', html[s:e])]
        if len(wolk) != len(vast):
            sys.exit(f'_fotowolk: precies {len(vast)} foto\'s nodig, niet {len(wolk)}')
        stuk = html[s:e]
        for m, f in reversed(list(zip(vast, wolk))):
            f = {'img': f} if isinstance(f, str) else f
            if not os.path.exists(os.path.join(base, f['img'])):
                sys.exit(f'_fotowolk: {f["img"]} bestaat niet')
            tag = re.sub(r'src="[^"]+"', lambda _: f'src="{escape(f["img"])}"', m.group(0), count=1)
            if f.get('pos'):
                tag = tag[:-1] + f' style="object-position:{escape(f["pos"])}">'
            stuk = stuk[:m.start()] + tag + stuk[m.end():]
        html = html[:s] + stuk + html[e:]
    return html


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

    # Optioneel upgradeblok (ladder) staat aan zodra de JSON een UPGRADE_LADDER heeft (geen tekst-key)
    ladder = translations.pop('UPGRADE_LADDER', None)
    # Optioneel cadeaublok (cadeau) staat aan zodra de JSON CADEAU_ITEMS heeft (lijst; CADEAU_VOET hoort erbij)
    cadeau = translations.pop('CADEAU_ITEMS', None)
    cadeau_voet = translations.pop('CADEAU_VOET', '') if cadeau else None
    # Ster-split (blok 3a): iconen van punt 2, 3 en 5 zijn per JSON te kiezen (standaard sleutel, label, kalender);
    # de knop onder het blok volgt ATTENTIE_KNOP (ontbreekt = tekst van CTA, leeg = geen knop).
    for k, v in ATTENTIE_ICOON_STANDAARD.items():
        translations.setdefault(k, v)
    translations.setdefault('ATTENTIE_KNOP', translations.get('CTA', ''))
    aan = ({k for k, v in config.get('blokken', {}).items() if v} | ({'ladder'} if ladder else set())
           | ({'cadeau'} if cadeau else set()) | ({'attentie-knop'} if translations['ATTENTIE_KNOP'] else set()))

    if 'arrangement' in aan:
        # arrangementblokken aan/uit per arrangement in de JSON
        if translations.get('ZV_TOON'): aan.add('zondag')
        if translations.get('WAAROM_TOON', True): aan.add('waarom')
        if translations.get('ANDERE_TOON') and translations.get('_andere'): aan.add('andere')

    # Variantblokken (bijv. zijkaart, ladder, cadeau, arrangement) vóór de {{KEY}}-pass
    html = apply_blokken(html, aan)
    if ladder:
        html = html.replace('<!-- UPGRADE_LADDER -->', render_ladder(ladder))
    if cadeau:
        html = html.replace('<!-- CADEAU_ITEMS -->', render_cadeau(cadeau, cadeau_voet))

    for key, value in translations.items():
        if isinstance(value, str) and not key.startswith('_'):
            html = html.replace('{{' + key + '}}', value)

    # Arrangement: kamers + pillen uit '_kamers' (alleen met blok 'arrangement')
    if 'arrangement' in aan:
        html = apply_arrangement(html, translations)

    # Letterlijke (hardcoded) NL-strings vertalen, in lijstvolgorde: langste/
    # meest specifieke strings staan vooraan zodat substrings niet half raken.
    literals_file = config.get('literals', {}).get(lang)
    if literals_file:
        with open(os.path.join(base, literals_file), encoding='utf-8') as f:
            for source, target in json.load(f):
                html = html.replace(source, target)

    # Reviewmuur uit de Google-reviews-JSON (alleen templates met 'reviews')
    if config.get('reviews'):
        if 'arrangement' in aan:
            n = translations.get('_reviews_aantal', 12)
            if n not in (8, 12):
                sys.exit(f'_reviews_aantal moet 8 of 12 zijn, niet {n!r}')
            html = inject_reviews(html, config['reviews'], max_kaarten=n, voorkeur=translations.get('_reviews_voorkeur'))
        else:
            html = inject_reviews(html, config['reviews'])

    # Mews-boekingslinks in de juiste taal openen (alleen EN/DE)
    html = add_mews_language(html, lang)

    # Kamer-media in ROOMS gelijk aan de detailpagina's (video + volledige fotoset)
    html = fix_room_media(html)

    # Sanity check: no unreplaced markers
    remaining = re.findall(r'\{\{[A-Z_0-9]+\}\}', html)
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
