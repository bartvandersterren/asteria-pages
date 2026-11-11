#!/usr/bin/env python3
"""Routes uit het Asteria OS (omgevingsscherm) voor de routepagina's /fietsen-rond-venray-v2 en /wandelen-rond-venray-v2.

Schrijft content/routes/fiets.json en content/routes/wandel.json (gecommit). build.py leest ALLEEN die twee
bestanden; tijdens het bouwen is er geen netwerk nodig. Opnieuw draaien zonder wijziging in het OS geeft
byte-gelijke bestanden (geen tijdstempel in de uitvoer).

Bron (alleen lezen, de enige schrijvende aanvraag is de login):
  1. POST /api/auth/sign-in/email  (OS_LIVE_URL / OS_LIVE_EMAIL / OS_LIVE_PASSWORD uit ~/.asteria-os-live.env,
     of uit de omgeving; Origin-header verplicht, sessiecookie)
  2. GET  /api/omgevingsscherm/instellingen  -> link.token van het omgevingsscherm (wordt nergens bewaard of getoond)
  3. GET  /api/omgeving/<token>/routes        -> de volledige routes (lijn, start, tijden, foto's, credits)

Selectie en volgorde (plan wondrous-foraging-mccarthy, besluit Stijn 11 nov 2026):
  fiets  = eerst de 7 Fietsknoop-routes vanaf het hotel (OS nr 12-18), dan routiq 115051 (op de pagina
           "Rondje Venray via Vierlingsbeek"), 185810 en 133681 ("Door de Peel bij Horst"). De andere 8 vervallen.
  wandel = eerst de eigen gebieden uit content/routes/wandel-eigen.json (onderzoek, niet uit het OS), dan de vier
           OS-routes buiten Horst (1308151, 670670, 1488500, 598041). De drie Horst-routes vervallen.

Per route: slug, nr (eigen volgorde 1..n), naam{nl,de,en}, afstand_km, duur_min, kcal, hoogte_m (optioneel), rondje,
start_plaats, start [lat,lng], tijd {auto, fiets}, lijn (Douglas-Peucker, max 120 punten, 5 decimalen; null = speld
op het startpunt), lengteklasse (kort|middel|lang), balk (afstand / langste route van de pagina, "57.9%"), bron
(fietsknoop|routiq|eigen), url, url_label (alleen eigen), knooppunten (alleen Fietsknoop), fotos (Commons-foto's
uit het OS met naamsvermelding, gedownload naar fotos/l26-route-os-<id>.webp; eigen gebieden: hun Commons-foto's
naar fotos/l26-route-<slug>-<n>.webp).

Lengteklassen: fiets tot 30 / 30-50 / vanaf 50 km (als Parkhotel). Wandel: zie WANDEL_GRENS.

  python3 scripts/routes_os.py            # ophalen + schrijven
  python3 scripts/routes_os.py --droog    # alleen tonen wat er zou komen
"""
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
import http.cookiejar

WORTEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UIT = os.path.join(WORTEL, 'content', 'routes')
EIGEN = os.path.join(UIT, 'wandel-eigen.json')
ENV = os.path.expanduser('~/.asteria-os-live.env')
HOTEL = [51.5478, 5.9972]
MAX_PUNTEN = 120

# Fietsknoop-id's (fietsknoop.nl/fietsroute/<id>/<slug>) staan in de OS-url; de knooppuntenreeks staat aan het eind
# van de NL-omschrijving ("Knooppunten: 65, 15, ..."), zie parkhotel-os scripts/omgevingsscherm-routes-fietsknoop.mjs.
FIETS = [
    # (OS-slug, eigen slug op de pagina, naam-overschrijving of None, startplaats)
    ('asteria-rondje-venray', 'rondje-venray', None, 'Oostrum'),
    ('asteria-rondje-over-het-pontje', 'rondje-over-het-pontje', None, 'Oostrum'),
    ('asteria-langs-de-maas', 'langs-de-maas', None, 'Oostrum'),
    ('asteria-van-venray-naar-de-peel', 'van-venray-naar-de-peel', None, 'Oostrum'),
    ('asteria-rondje-horst-aan-de-maas', 'rondje-horst-aan-de-maas', None, 'Oostrum'),
    ('asteria-maasduinen-en-arcen', 'maasduinen-en-arcen', None, 'Oostrum'),
    ('asteria-ballonzuilbossen-en-overloon', 'ballonzuilbossen-en-overloon', None, 'Venray'),
    ('rondje-venray', 'rondje-venray-via-vierlingsbeek',
     {'nl': 'Rondje Venray via Vierlingsbeek', 'de': 'Runde um Venray über Vierlingsbeek', 'en': 'Venray loop via Vierlingsbeek'},
     'Overloon'),
    ('meterik-venray-horst', 'meterik-venray-horst', {'nl': 'Meterik, Venray, Horst', 'de': 'Meterik, Venray, Horst', 'en': 'Meterik, Venray, Horst'}, 'Meterik'),
    ('peel-bij-horst', 'door-de-peel-bij-horst',
     {'nl': 'Door de Peel bij Horst', 'de': 'Durch die Peel bei Horst', 'en': 'Through the Peel near Horst'},
     'Meterik'),
]
WANDEL_OS = [
    ('maasduinen-bij-bergen', 'maasduinen-bij-bergen', {'nl': 'Maasduinen bij Bergen', 'de': 'Maasduinen bei Bergen', 'en': 'Maasduinen near Bergen'}, 'Bergen'),
    ('lekkerbekkenroute', 'lekkerbekkenroute', {'nl': 'Lekkerbekkenroute Maasduinen', 'de': 'Lekkerbekkenroute Maasduinen',
                                                'en': 'Lekkerbekken route, Maasduinen'}, 'Arcen'),
    ('rondje-mariaveen', 'rondje-mariaveen', None, 'Helenaveen'),
    ('mariapeel', 'wandelen-door-de-mariapeel', None, 'Helenaveen'),
]
FIETS_GRENS = (30, 50)
# Wandel: NIET de Parkhotel-grenzen 11/15 (dan valt 'lang' leeg en 'kort' bijna; de eigen gebieden zijn 4-8 km).
# Gekozen: tot 6 / 6-12 / vanaf 12 km, zodat elke klasse minstens een route heeft (vastgelegd in qa/routes/FEITEN-wandelen.md).
WANDEL_GRENS = (6, 12)
# Commons-foto's van de eigen gebieden die niet op de pagina horen (deel van de url): de kasteelruine van Geijsteren
# ligt niet op de lus (FEITEN-wandelen.md).
FOTO_WEG = ('kasteelru',)
UA = 'asteria-pages-routes/1.0 (routepagina visit.asteria.nl; python urllib)'

LICENTIE_URL = {
    'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/',
    'Public domain': 'https://en.wikipedia.org/wiki/Public_domain',
    'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0/',
    'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0/',
    'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/',
    'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0/',
    'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/',
    'CC BY-SA 3.0 nl': 'https://creativecommons.org/licenses/by-sa/3.0/nl/',
    'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
}


# ------------------------------------------------------------------ OS
def lees_env():
    env = dict(os.environ)
    if os.path.exists(ENV):
        for regel in open(ENV, encoding='utf-8'):
            m = re.match(r'\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*?)\s*$', regel)
            if m:
                w = m.group(2)
                if re.match(r'^([\'"]).*\1$', w):
                    w = w[1:-1]
                env.setdefault(m.group(1), w)
    for k in ('OS_LIVE_URL', 'OS_LIVE_EMAIL', 'OS_LIVE_PASSWORD'):
        if not env.get(k):
            sys.exit(f'routes_os: {k} ontbreekt ({ENV} of omgeving)')
    return env


def haal_os():
    env = lees_env()
    basis = env['OS_LIVE_URL'].rstrip('/')
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def api(pad, data=None):
        req = urllib.request.Request(basis + pad, data=json.dumps(data).encode() if data is not None else None, method='POST' if data is not None else 'GET',
                                     headers={'Origin': basis, 'Content-Type': 'application/json', 'User-Agent': 'asteria-pages routes_os'})
        try:
            with op.open(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            sys.exit(f'routes_os: {req.get_method()} {pad.split("/api/omgeving/")[0] or pad} gaf {e.code}')

    api('/api/auth/sign-in/email', {'email': env['OS_LIVE_EMAIL'], 'password': env['OS_LIVE_PASSWORD']})
    link = (api('/api/omgevingsscherm/instellingen') or {}).get('link') or {}
    token = link.get('token')
    if not token:
        sys.exit('routes_os: het OS geeft geen token van het omgevingsscherm')
    data = api(f'/api/omgeving/{token}/routes')
    print(f'OS {basis}: {len(data.get("routes", []))} routes opgehaald')
    return data


# ------------------------------------------------------------------ geometrie
def meters(p, lat0):
    return (p[1] * 111320 * math.cos(math.radians(lat0)), p[0] * 110540)


def dp(pts, eps, lat0):
    if len(pts) < 3:
        return pts
    a, b = meters(pts[0], lat0), meters(pts[-1], lat0)
    dx, dy = b[0] - a[0], b[1] - a[1]
    lng = math.hypot(dx, dy)
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        p = meters(pts[i], lat0)
        d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / lng if lng else math.hypot(p[0] - a[0], p[1] - a[1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps, lat0)[:-1] + dp(pts[idx:], eps, lat0)
    return [pts[0], pts[-1]]


def vereenvoudig(lijn):
    if not lijn or len(lijn) < 2:
        return None
    lat0 = lijn[0][0]
    eps, uit = 2.0, dp(lijn, 2.0, lat0)
    while len(uit) > MAX_PUNTEN:
        eps *= 1.25
        uit = dp(lijn, eps, lat0)
    return [[round(p[0], 5), round(p[1], 5)] for p in uit]


def klasse(afstand, grens):
    return 'kort' if afstand <= grens[0] else ('middel' if afstand <= grens[1] else 'lang')


# ------------------------------------------------------------------ foto's
def webp_van(url, doel, breed=1000):
    if os.path.exists(doel):
        return True
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit('routes_os: Pillow nodig voor de foto-omzetting')
    import time
    m = re.match(r'(https://upload\.wikimedia\.org/wikipedia/commons/)([0-9a-f]/[0-9a-f]{2}/)([^/]+)$', url)
    if m:   # Wikimedia wil thumbnails in een standaardmaat (anders 429): /thumb/<pad>/1280px-<naam>
        url = f'{m.group(1)}thumb/{m.group(2)}{m.group(3)}/1280px-{m.group(3)}'
    ruw = None
    for poging in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                ruw = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and poging < 3:
                time.sleep(10 * (poging + 1))   # Wikimedia remt: rustig opnieuw
                continue
            print(f'  WAARSCHUWING: foto niet opgehaald ({url}): {e}')
            return False
        except Exception as e:  # noqa: BLE001
            print(f'  WAARSCHUWING: foto niet opgehaald ({url}): {e}')
            return False
    if 'wikimedia' in url:
        time.sleep(2)
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(ruw))).convert('RGB')
    if im.width > breed:
        im = im.resize((breed, round(im.height * breed / im.width)), Image.LANCZOS)
    im.save(doel, 'WEBP', quality=78, method=6)
    print(f'  foto: {os.path.relpath(doel, WORTEL)}')
    return True


def credit_delen(tekst):
    naam, _, lic = (tekst or '').rpartition(', ')
    if not naam:
        return tekst, ''
    return naam, lic


def os_fotos(r, data):
    uit = []
    adressen = data.get('fotos') or {}
    for i, fid in enumerate(r.get('fotos') or []):
        cr = (r.get('credits') or [None] * 99)[i] if r.get('credits') else None
        if not cr:
            continue   # zonder naamsvermelding = routiq-/hotelfoto: niet op de pagina
        a = adressen.get(str(fid)) or {}
        url = a.get('groot') or a.get('klein')
        if not url:
            continue
        pad = f'fotos/l26-route-os-{fid}.webp'
        if not webp_van(url, os.path.join(WORTEL, pad)):
            continue
        naam, lic = credit_delen(cr)
        uit.append({'bestand': pad, 'credit': naam, 'licentie': lic, 'licentie_url': LICENTIE_URL.get(lic, ''), 'bron_url': ''})
    return uit


# ------------------------------------------------------------------ opbouw
def route_uit_os(r, slug, naam, plaats, bron, data):
    url = r.get('url') or ''
    knoop = None
    if bron == 'fietsknoop':
        m = re.search(r'Knooppunten:\s*([\d,\s]+)', (r.get('omschrijving') or {}).get('nl') or '')
        if not m:
            sys.exit(f'routes_os: geen knooppuntenreeks in de omschrijving van {r["slug"]}')
        knoop = [int(x) for x in re.findall(r'\d+', m.group(1))]
    return {
        'slug': slug,
        'os_slug': r['slug'],
        'naam': {t: (naam or r['naam']).get(t) or r['naam']['nl'] for t in ('nl', 'de', 'en')},
        'afstand_km': r['afstand_km'],
        'duur_min': r['duur_min'],
        'kcal': r.get('kcal'),
        'hoogte_m': r.get('hoogte_m'),
        'rondje': bool(r.get('rondje')),
        'start_plaats': plaats,
        'start': r.get('start'),
        'tijd': r.get('tijd') or {'auto': None, 'fiets': None},
        'lijn': vereenvoudig(r.get('lijn')),
        'bron': bron,
        'url': url,
        'url_label': 'Fietsknoop' if bron == 'fietsknoop' else 'routiq',
        'knooppunten': knoop,
        'fotos': os_fotos(r, data),
    }


def osrm_tijd(start, oud):
    """Reistijden vanaf het hotel naar het startpunt zoals het OS ze rekent (seed-lib reistijden): OSRM-autoroute,
    auto = duur in minuten, fiets = afstand / 16 km/u (null boven 60 min). Lukt OSRM niet, dan blijft de schatting staan."""
    url = (f'https://router.project-osrm.org/route/v1/driving/{HOTEL[1]},{HOTEL[0]};{start[1]},{start[0]}?overview=false')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
            rt = json.load(r)['routes'][0]
    except Exception as e:  # noqa: BLE001
        print(f'  WAARSCHUWING: OSRM gaf geen route ({e}); schatting uit wandel-eigen.json blijft')
        return oud
    fiets = round(rt['distance'] / 1000 / 16 * 60)
    return {'auto': max(1, round(rt['duration'] / 60)), 'fiets': max(1, fiets) if fiets <= 60 else None}


def route_uit_eigen(e):
    fotos = []
    for i, f in enumerate([f for f in e.get('fotos') or [] if not any(w in f['url'] for w in FOTO_WEG)], 1):
        pad = f'fotos/l26-route-{e["slug"]}-{i}.webp'
        if not webp_van(f['url'], os.path.join(WORTEL, pad)):
            continue
        fotos.append({'bestand': pad, 'credit': f.get('credit', ''), 'licentie': f.get('licentie', ''),
                      'licentie_url': f.get('licentie_url', ''), 'bron_url': f.get('bron_url', ''), 'alt': f.get('alt')})
    return {
        'slug': e['slug'],
        'os_slug': None,
        'naam': e['naam'],
        'afstand_km': e['afstand_km'],
        'duur_min': e['duur_min'],
        'kcal': None,
        'hoogte_m': None,
        'rondje': bool(e.get('rondje')),
        'start_plaats': e.get('start_plaats') or '',
        'start_naam': e.get('start_naam') or '',
        'gebied': e.get('gebied') or '',
        'beheerder': e.get('beheerder') or '',
        'start': e.get('start'),
        'tijd': osrm_tijd(e['start'], e.get('tijd') or {'auto': None, 'fiets': None}),
        'lijn': vereenvoudig(e.get('lijn')) if e.get('lijn') else None,
        'bron': 'eigen',
        'url': e.get('url') or '',
        'url_label': e.get('url_label') or '',
        'knooppunten': None,
        'fotos': fotos,
    }


def afronden(routes, grens):
    langste = max(r['afstand_km'] for r in routes) or 1
    for i, r in enumerate(routes, 1):
        r['nr'] = i
        r['lengteklasse'] = klasse(r['afstand_km'], grens)
        r['balk'] = f'{r["afstand_km"] / langste * 100:.1f}%'
    # vaste veldvolgorde
    volg = ['nr', 'slug', 'os_slug', 'naam', 'bron', 'afstand_km', 'duur_min', 'kcal', 'hoogte_m', 'rondje', 'lengteklasse', 'balk',
            'start_plaats', 'start_naam', 'gebied', 'beheerder', 'start', 'tijd', 'url', 'url_label', 'knooppunten', 'fotos', 'lijn']
    return [{k: r[k] for k in volg if k in r} for r in routes]


def schrijf(soort, routes, grens, droog):
    data = {'_uitleg': f'NIET met de hand bewerken: scripts/routes_os.py schrijft dit bestand ({soort}routes, bron Asteria OS'
                       + (' + content/routes/wandel-eigen.json' if soort == 'wandel' else '') + ').',
            'soort': soort, 'hotel': HOTEL, 'grens': list(grens), 'routes': routes}
    tekst = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    pad = os.path.join(UIT, f'{soort}.json')
    for r in routes:
        print(f'  {soort} {r["nr"]:>2} {r["slug"]:<34} {r["afstand_km"]:>6} km {r["lengteklasse"]:<6} {r["bron"]:<10} '
              f'lijn {len(r["lijn"]) if r["lijn"] else "-":>3}  fotos {len(r["fotos"])}')
    if droog:
        return
    os.makedirs(UIT, exist_ok=True)
    with open(pad, 'w', encoding='utf-8') as f:
        f.write(tekst)
    print(f'-> {os.path.relpath(pad, WORTEL)}')


def main():
    droog = '--droog' in sys.argv
    data = haal_os()
    per_slug = {r['slug']: r for r in data['routes']}

    def os_route(sl):
        if sl not in per_slug:
            sys.exit(f'routes_os: route {sl} staat niet (actief) in het OS')
        return per_slug[sl]

    fiets = []
    for sl, eigen, naam, plaats in FIETS:
        r = os_route(sl)
        bron = 'fietsknoop' if 'fietsknoop.nl' in (r.get('url') or '') else 'routiq'
        fiets.append(route_uit_os(r, eigen, naam, plaats, bron, data))
    schrijf('fiets', afronden(fiets, FIETS_GRENS), FIETS_GRENS, droog)

    wandel = []
    if os.path.exists(EIGEN):
        with open(EIGEN, encoding='utf-8') as f:
            for e in json.load(f):
                wandel.append(route_uit_eigen(e))
    else:
        print(f'  WAARSCHUWING: {os.path.relpath(EIGEN, WORTEL)} ontbreekt, alleen de OS-wandelroutes')
    for sl, eigen, naam, plaats in WANDEL_OS:
        wandel.append(route_uit_os(os_route(sl), eigen, naam, plaats, 'routiq', data))
    wandel = afronden(wandel, WANDEL_GRENS)
    leeg = [k for k in ('kort', 'middel', 'lang') if not any(r['lengteklasse'] == k for r in wandel)]
    if leeg:
        print(f'  WAARSCHUWING: wandel-klasse zonder route: {leeg} (grenzen {WANDEL_GRENS})')
    schrijf('wandel', wandel, WANDEL_GRENS, droog)


if __name__ == '__main__':
    main()
