#!/usr/bin/env python3
"""Spiegel van de Effecty-staging (asteria.staging.effectytools.com) op visit.asteria.nl.

Gebruik (in de repo-root):
  python3 scripts/staging_spiegel.py            # alles opnieuw ophalen en schrijven
  python3 scripts/staging_spiegel.py --droog    # alleen ophalen en loggen, niets schrijven

Wat het doet (herhaalbaar; draai het opnieuw en alles wordt ververst):
- haalt de NL-pagina's uit translations/spiegel-links.json ("spiegel") op; de staging is statische HTML
  (site-build.js), dus gewone HTTP-requests geven de volledig gerenderde pagina;
- zet alle assets (CSS, JS, fonts, afbeeldingen, video's; ook url() in CSS, srcset, poster, data-photo) onder
  nieuw-assets/ (staging /assets/x -> /nieuw-assets/x, /base.css -> /nieuw-assets/base.css; ?v= weg). Is een asset
  byte-gelijk aan een bestand dat al in fotos/, videos/ of fonts/ staat, dan wijst de pagina daarnaar (geen dubbel);
  bestanden in nieuw-assets/ die niet meer gebruikt worden, gaan weg;
- herschrijft de HTML: noindex, follow + canonical/og:url op het eigen visit-adres, staging-robots/hreflang/
  nav-engine-kop weg, GA4 + Google Ads zoals hotel-venray-v2, cookiemelding, spiegel.css/spiegel.js;
  links via de linkset (paginas, arrangementen, weg), /bookingEngine/ en #boeking -> Mews (data-mews-open, kamer
  via data-room), taalkeuze weg, formulieren naar /api/nieuwsbrief (nieuwsbrief) of mailto (contact);
- page-interactions.js: MEWS_ENTRY '/bookingEngine' -> de Mews-distributor (terugval; spiegel.js opent de widget);
- logt per pagina wat er is gedaan en schrijft het log naar qa/staging-spiegel-log.json (qa/ staat niet in git).
Inhoud wordt niet herschreven. Stopt met een fout als er nog een staging-link, Formspree-actie of href="#" overblijft.
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup, Comment

BASIS = 'https://asteria.staging.effectytools.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETMAP = 'nieuw-assets'
VISIT = 'https://visit.asteria.nl'
MEWS_CONFIG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
MEWS_URL = 'https://app.mews.com/distributor/' + MEWS_CONFIG
KAMER_MEWS = {   # gelijk aan build.py KAMER_MEWS / build_kamers.py CATEGORY
    'comfort': '98900f3b-e5e2-49c9-9776-af1d00ffc315', 'comfort-3': '85ca19d7-eea5-41c8-8b93-af1d00ffc315',
    'mindervalide': 'fa5b6540-7234-49ce-beb1-af1d00ffc315', 'royale': 'a8fd7310-0d61-422f-89e6-af1d00ffc315',
    'deluxe': 'c737de50-e41e-4c8d-a818-af1d00ffc315', 'junior-suite': '27ea8deb-ded5-4856-8fdd-af1d00ffc315',
    'suite': '4a642b66-68e6-444c-beeb-af1d00ffc315', 'bruidssuite': 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'}
# kamernaam (data-suite, kaartkop) -> sleutel; langste eerst zodat 'junior suite' niet als 'suite' telt
KAMER_NAAM = [('comfort 3-persoons', 'comfort-3'), ('comfort kamer 3', 'comfort-3'), ('3-persoons', 'comfort-3'),
              ('junior suite', 'junior-suite'), ('bruidssuite', 'bruidssuite'), ('mindervalide', 'mindervalide'),
              ('comfort', 'comfort'), ('royale', 'royale'), ('deluxe', 'deluxe'), ('suite', 'suite')]
# kaartkop precies gelijk aan een kamernaam -> sleutel (boekknop in een kamerkaart krijgt die kamer)
KAMER_KOP = {'comfort kamer': 'comfort', 'comfort 3-persoons': 'comfort-3', 'royale kamer': 'royale', 'deluxe kamer': 'deluxe',
             'junior suite': 'junior-suite', 'suite': 'suite', 'bruidssuite': 'bruidssuite', 'mindervalide kamer': 'mindervalide'}
# kamer -> sleutel van de detailpagina in de linkset (Comfort/Deluxe = spiegelpagina, de andere vijf = eigen kamer-w1-pagina's
# onder /kamers/, build.py kamers/<slug>). Junior Suite heeft geen detailpagina: die knoppen blijven Mews met de kamer.
KAMER_DETAIL = {'comfort': 'kamer-comfort', 'deluxe': 'kamer-deluxe', 'comfort-3': 'kamer-comfort-3',
                'mindervalide': 'kamer-mindervalide', 'royale': 'kamer-royale', 'suite': 'kamer-suite', 'bruidssuite': 'kamer-bruidssuite'}
# staging-pad -> sleutel van de linkset
PAD_SLEUTEL = {'/': 'home', '/kamers/': 'kamers', '/kamers/comfort-kamer/': 'kamer-comfort',
               '/kamers/deluxe-kamer/': 'kamer-deluxe', '/arrangementen/': 'arrangementen', '/faciliteiten/': 'faciliteiten',
               '/wellness/': 'wellness', '/restaurant/': 'restaurant', '/vergaderen/': 'vergaderen', '/omgeving/': 'omgeving',
               '/over-ons/': 'over-ons', '/contact/': 'contact', '/bookingEngine/': 'boeken', '/bookingEngine': 'boeken'}
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) asteria-spiegel/1.0'}

GA_TAGS = """
  <!-- GA4 + Google Ads (zoals hotel-venray-v2) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DPCP945DCG"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-DPCP945DCG', { linker: { domains: ['asteria.nl', 'visit.asteria.nl'] } });
    gtag('config', 'AW-998609513');
    gtag('set', 'linker', { accept_incoming: true });
    window.GA_ADS_LABEL = 'AW-998609513/t8vbCLm6i7IcEOmkltwD';
  </script>
"""
COOKIE = """
<!-- ══ COOKIE BANNER (zoals hotel-venray-v2) ══ -->
<div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookiemelding">
  <span>Deze website gebruikt cookies voor een optimale ervaring. <a href="https://www.asteria.nl/privacy" target="_blank" rel="noopener">Meer info</a></span>
  <button type="button" id="cookieAccept">Akkoord</button>
</div>
"""


def haal(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


class Assets:
    """Download + plaats assets; staging-pad (zonder query) -> publiek pad op visit.asteria.nl."""

    def __init__(self, droog):
        self.droog = droog
        self.kaart = {}        # staging-pad -> publiek pad
        self.bytes = {}        # publiek pad -> grootte (alleen nieuw-assets)
        self.hergebruik = {}   # staging-pad -> repo-pad
        self.fouten = []
        self.repo = None

    def repo_index(self):
        if self.repo is None:
            self.repo = {}
            for d in ('fotos', 'videos', 'fonts'):
                for dp, _, fs in os.walk(os.path.join(ROOT, d)):
                    for f in fs:
                        p = os.path.join(dp, f)
                        self.repo.setdefault(os.path.getsize(p), []).append(p)
        return self.repo

    def zelfde_in_repo(self, data):
        kandidaten = self.repo_index().get(len(data), [])
        if not kandidaten:
            return None
        h = hashlib.sha256(data).hexdigest()
        for p in kandidaten:
            with open(p, 'rb') as f:
                if hashlib.sha256(f.read()).hexdigest() == h:
                    return '/' + os.path.relpath(p, ROOT)
        return None

    @staticmethod
    def doelpad(pad):
        rest = pad[len('/assets/'):] if pad.startswith('/assets/') else pad.lstrip('/')
        return '/' + ASSETMAP + '/' + rest

    def pak(self, url):
        """Absolute of site-relatieve staging-URL -> publiek pad (downloadt de eerste keer)."""
        u = urllib.parse.urlsplit(urllib.parse.urljoin(BASIS + '/', url))
        if u.netloc and u.netloc != urllib.parse.urlsplit(BASIS).netloc:
            return None
        pad = urllib.parse.unquote(u.path)
        if pad in self.kaart:
            return self.kaart[pad]
        self.kaart[pad] = None
        try:
            status, data = haal(BASIS + urllib.parse.quote(pad))
        except Exception as e:   # noqa: BLE001
            self.fouten.append(f'{pad}: {e}')
            print(f'  ASSET FOUT {pad}: {e}')
            return None
        doel = self.doelpad(pad)
        if pad.endswith('.css'):
            data = self.css(data.decode('utf-8'), pad).encode('utf-8')
        elif pad.endswith('.js'):
            data = self.js(data.decode('utf-8'), pad).encode('utf-8')
        else:
            gelijk = self.zelfde_in_repo(data)
            if gelijk:
                self.hergebruik[pad] = gelijk
                self.kaart[pad] = gelijk
                return gelijk
        self.kaart[pad] = doel
        self.bytes[doel] = len(data)
        if not self.droog:
            p = os.path.join(ROOT, doel.lstrip('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as f:
                f.write(data)
        return doel

    def css(self, tekst, pad):
        def url_vervang(m):
            ruw = m.group(2).strip()
            if ruw.startswith(('data:', '#', 'http://', 'https://')) and BASIS not in ruw:
                return m.group(0)
            nieuw = self.pak(urllib.parse.urljoin(BASIS + pad, ruw))
            return f'url({m.group(1)}{nieuw}{m.group(1)})' if nieuw else m.group(0)
        tekst = re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', url_vervang, tekst)
        tekst = re.sub(r'@import\s+([\'"])([^\'"]+)\1',
                       lambda m: f'@import {m.group(1)}{self.pak(urllib.parse.urljoin(BASIS + pad, m.group(2))) or m.group(2)}{m.group(1)}', tekst)
        return tekst

    def js(self, tekst, pad):
        if pad.endswith('page-interactions.js'):
            oud = "const MEWS_ENTRY = '/bookingEngine';"
            if oud in tekst:
                tekst = tekst.replace(oud, f"const MEWS_ENTRY = '{MEWS_URL}';   /* spiegel visit.asteria.nl: Mews-distributor i.p.v. /bookingEngine */")
            else:
                self.fouten.append('page-interactions.js: MEWS_ENTRY niet gevonden')
                print('  LET OP: MEWS_ENTRY niet gevonden in page-interactions.js')
        for m in re.findall(r'[\'"`](/assets/[^\'"`]+)[\'"`]', tekst):
            nieuw = self.pak(m)
            if nieuw:
                tekst = tekst.replace(m, nieuw)
        return tekst


def tekst_van(el):
    return ' '.join(el.get_text(' ').split())


def kop_bij(a, maxniveau=6):
    """Kop van de kaart/sectie waar de link in staat: de laatste h1-h4 vóór de link binnen het dichtstbijzijnde
    voorouder-element dat een kop heeft."""
    el = a
    for _ in range(maxniveau):
        el = el.parent
        if el is None or el.name in ('body', 'main'):
            return ''
        koppen = el.find_all(re.compile('^h[1-4]$'))
        voor = [h for h in koppen if a in h.find_all_next('a')]
        if voor:
            return tekst_van(voor[-1])
    return ''


def kamer_uit(tekst):
    t = (tekst or '').lower()
    for naam, sleutel in KAMER_NAAM:
        if naam in t:
            return sleutel
    return None


def mews_href(kamer=None):
    return MEWS_URL + (f'?mewsRoom={KAMER_MEWS[kamer]}&mewsRoute=rooms' if kamer else '')


def maak_mews(a, kamer=None):
    a['href'] = mews_href(kamer)
    a['data-mews-open'] = ''
    if kamer:
        a['data-room'] = KAMER_MEWS[kamer]
    for k in ('data-suite', 'data-scroll-to-booking', 'data-link-todo', 'aria-disabled', 'tabindex', 'target'):
        if k in a.attrs:
            del a[k]


def zet_link(a, href):
    a['href'] = href
    for k in ('data-link-todo', 'aria-disabled', 'tabindex'):
        if k in a.attrs:
            del a[k]


def verwijder(a, log):
    """Link naar een pagina die er niet is (linkset 'weg'): menu-item/voetlink/knop/tegel weg; in lopende tekst
    blijft de tekst staan."""
    t = tekst_van(a)
    ouder = a.parent
    if ouder.name == 'p' and tekst_van(ouder) != t:
        a.unwrap()
        log.append(('tekstlink zonder link', t))
        return
    if ouder.name == 'li':
        ul = ouder.parent
        ouder.decompose()
        log.append(('menu-item weg', t))
        if ul is not None and not ul.find('li'):
            sub = ul.parent
            if sub is not None and sub.name == 'li' and 'has-sub' in (sub.get('class') or []):
                naam = tekst_van(sub.find(['button', 'a'])) if sub.find(['button', 'a']) else ''
                sub.decompose()
                log.append(('submenu weg', naam))
        return
    a.decompose()
    log.append(('link/knop/tegel weg', t[:80]))
    if ouder is not None and not ouder.find(True) and not tekst_van(ouder) and ouder.name in ('div', 'p'):
        ouder.decompose()


def verwerk_links(soup, links, eigen_pad, heeft_boeking, log, pagina_kamer=None):
    paginas = links['paginas']
    overzicht = links['arrangementenoverzicht']
    weg = set(links['weg'])
    spiegelpad = {k: v['sleutel'] for k, v in links['spiegel'].items()}
    for a in list(soup.find_all('a')):
        if a.decomposed if hasattr(a, 'decomposed') else False:
            continue
        if a.parent is None:
            continue
        href = a.get('href')
        if href is None:
            continue
        dl = a.get('data-link', '')
        t = tekst_van(a)
        # staging- en asteria.nl-adressen naar een pad
        u = urllib.parse.urlsplit(href)
        pad = None
        if not u.scheme and href.startswith('/'):
            pad = u.path
        elif u.netloc in ('asteria.staging.effectytools.com', 'www.asteria.nl', 'asteria.nl') and not u.path.startswith('/upload/'):
            pad = u.path or '/'
            if u.path in ('/privacy', '/algemene-voorwaarden'):
                continue
        if pad is not None and (pad.startswith('/en/') or pad.startswith('/de/') or pad in ('/en', '/de')):
            log.append(('taallink weg', f'{t} ({href})'))
            a.decompose()
            continue

        sleutel = None
        if href == '#' and a.has_attr('data-link-todo'):
            sleutel = dl
        elif pad is not None:
            sleutel = PAD_SLEUTEL.get(pad if pad.endswith('/') or pad == '/bookingEngine' else pad + '/')
            if sleutel is None:
                raise SystemExit(f'onbekend staging-pad {href!r} ({t!r}) op {eigen_pad}')
            # kamerkaart waarvan de staging naar een andere kamerpagina linkt (Comfort 3-persoons -> /kamers/comfort-kamer/):
            # de kamer van de kaartkop wint als die een eigen detailpagina heeft
            kk = KAMER_DETAIL.get(KAMER_KOP.get(kop_bij(a).lower()))
            if sleutel.startswith('kamer-') and kk and kk != sleutel:
                log.append(('kamerkaart -> eigen detailpagina', f'{t} {kop_bij(a)}: {sleutel} -> {kk}'))
                sleutel = kk
        elif href == '#boeking':
            sleutel = 'boeking'
        else:
            continue   # tel:, mailto:, #anker, extern

        if sleutel in weg:
            verwijder(a, log)
            continue
        if sleutel == 'boeken':
            # kamerkaart (kop = kamernaam) -> die kamer; op een kamerdetailpagina verder de kamer van de pagina
            kamer = KAMER_KOP.get(kop_bij(a).lower()) or pagina_kamer
            maak_mews(a, kamer)
            log.append(('Mews', f'{t}' + (f' [kamer {kamer}]' if kamer else '')))
            continue
        if sleutel == 'boeking':
            suite = a.get('data-suite')
            kamer = kamer_uit(suite) if suite else None
            if heeft_boeking and not suite and not a.has_attr('data-scroll-to-booking') \
                    and 'nav-cta' not in (a.get('class') or []) and not a.find_parent(class_='nav-drawer') \
                    and not a.find_parent('footer'):
                continue   # anker naar de boekkaart op dezelfde pagina blijft
            if suite and re.match(r'bekijk', t, re.I) or (suite and a.find_parent('footer')):
                doel = KAMER_DETAIL.get(kamer)
                if doel:
                    zet_link(a, paginas[doel])
                    for k in ('data-suite', 'data-scroll-to-booking'):
                        if k in a.attrs:
                            del a[k]
                    log.append(('kamer -> spiegelpagina', f'{t} {suite} -> {paginas[doel]}'))
                    continue
            maak_mews(a, kamer)
            log.append(('#boeking -> Mews', f'{t}' + (f' [kamer {kamer}]' if kamer else '')))
            continue
        if sleutel.startswith('kamer-') and sleutel not in paginas:
            kamer = sleutel[len('kamer-'):]
            if kamer not in KAMER_MEWS:
                raise SystemExit(f'onbekende kamer {sleutel!r} op {eigen_pad}')
            maak_mews(a, kamer)
            log.append(('kamerdetail zonder spiegel -> Mews met kamer', f'{t} [{kamer}]'))
            continue
        if sleutel == 'arrangementen' or sleutel.startswith('arrangement-'):
            doel = overzicht
            if sleutel.startswith('arrangement-') or re.match(r'(meer informatie|bekijk het .*arrangement)', t, re.I):
                naam = (t + ' ' + kop_bij(a) + ' ' + sleutel).lower()
                for woord, url in links['arrangementen']:
                    if woord in naam:
                        doel = url
                        break
                log.append(('arrangement', f'{t} / {kop_bij(a)} -> {doel}'))
            zet_link(a, doel)
            continue
        if sleutel in paginas:
            zet_link(a, paginas[sleutel])
            if sleutel in ('privacy', 'algemene-voorwaarden', 'beoordelingen'):
                a['target'] = '_blank'
                a['rel'] = 'noopener'
                log.append(('niet-gebouwd -> extern', f'{t} -> {paginas[sleutel]}'))
            continue
        raise SystemExit(f'geen doel voor sleutel {sleutel!r} ({t!r}) op {eigen_pad}')


# Prijselementen van de staging (plaatshouder "€ …" of "Bekijk actuele prijzen") -> live vanaf-prijs via /api/kamer-vanaf.
# Element krijgt data-kamer-vanaf="<sleutel>", het bedrag data-kamer-vanaf-bedrag; spiegel.css verbergt het element
# (visibility, ruimte blijft) tot spiegel.js het gevuld heeft; geen prijs = blijft verborgen.
PRIJS_SELECTOR = {'.suite-price': '.amount', '.overhangkaart__prijs': '.overhangkaart__bedrag', '.boekbalk__prijs': '.boekbalk__bedrag'}


def markeer_prijzen(soup, pagina_kamer, log):
    kamer_van_id = {v: k for k, v in KAMER_MEWS.items()}
    for sel, bedrag_sel in PRIJS_SELECTOR.items():
        for el in soup.select(sel):
            kaart = el.find_parent(['article', 'li']) or el.parent
            kop = kaart.find(re.compile('^h[1-4]$')) if kaart else None
            sleutel = KAMER_KOP.get(tekst_van(kop).lower()) if kop else None
            if not sleutel and kaart:
                knop = kaart.find('a', attrs={'data-room': True})
                sleutel = kamer_van_id.get(knop['data-room']) if knop else None
            sleutel = sleutel or pagina_kamer
            bedrag = el.select_one(bedrag_sel)
            if not sleutel or bedrag is None:
                raise SystemExit(f'prijselement zonder kamer of bedrag: {str(el)[:160]}')
            el['data-kamer-vanaf'] = sleutel
            bedrag['data-kamer-vanaf-bedrag'] = ''
            # verborgen plaatshouder zo lang als een echt bedrag, zodat de ruimte gelijk blijft (home: "Bekijk actuele prijzen")
            bedrag.string = '€ …'
            if 'data-plaatshouder' in el.attrs:
                del el['data-plaatshouder']
            log.append(('kamerprijs live (/api/kamer-vanaf)', f'{sel} [{sleutel}]'))


def herschrijf_assets(soup, assets):
    def map_waarde(v):
        if v.startswith(BASIS):
            v = v[len(BASIS):]
        if not v.startswith('/') or v.startswith('//'):
            return None
        pad = urllib.parse.urlsplit(v).path
        if pad.startswith('/assets/') or re.search(r'\.(css|js|webp|jpe?g|png|svg|gif|mp4|webm|woff2?|ico)$', pad):
            return assets.pak(v)
        return None
    for el in soup.find_all(True):
        for attr, waarde in list(el.attrs.items()):
            if not isinstance(waarde, str):
                continue
            if attr == 'srcset' or attr.endswith('srcset'):
                delen = []
                for d in waarde.split(','):
                    d = d.strip().split()
                    if d:
                        n = map_waarde(d[0])
                        delen.append(' '.join([n or d[0]] + d[1:]))
                el[attr] = ', '.join(delen)
            elif attr == 'style' and 'url(' in waarde:
                el[attr] = re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)',
                                  lambda m: f'url({m.group(1)}{map_waarde(m.group(2)) or m.group(2)}{m.group(1)})', waarde)
            elif attr != 'href' or el.name == 'link':
                n = map_waarde(waarde)
                if n:
                    el[attr] = n


# Wellness: de 2D-plattegrond van de staging (blok plattegrond-interactief, 600x400) vervangen door de 3D-render van
# wellnessasteria.nl (static/assets/wellness-floorplan-v2.webp, 1920x1433). Eigen bestanden in nieuw-assets/ (blijven bij het
# opruimen staan, zie EIGEN_ASSETS); stippen in de volgorde van de lijst op de staging, (naam, x %, y %) op de 3D-afbeelding.
PLATTEGROND_3D = {'src': '/nieuw-assets/wellness-plattegrond-3d-1200.webp', 'groot': '/nieuw-assets/wellness-plattegrond-3d-1920.webp',
                  'breed': 1200, 'hoog': 896}
PLATTEGROND_PLEKKEN = [('Entree en kleedruimte', 15, 24), ('Stoomcabine', 42, 49), ('Twee baden', 45, 34), ('Belevenisdouches', 59, 47),
                       ('Infraroodcabine', 53, 17), ('Voetenbaden', 65, 32), ('Boscabine', 73, 15), ('Zoutsteensauna', 88, 15),
                       ('Notenhouten sauna', 88, 33), ('Relaxruimte', 78, 70), ('Fitness', 21, 70)]
EIGEN_ASSETS = {PLATTEGROND_3D['src'].lstrip('/'), PLATTEGROND_3D['groot'].lstrip('/')}


def plattegrond_3d(soup, log):
    """Blok plattegrond-interactief (alleen /wellness): img -> 3D-render (src 1200, srcset 1200/1920, width/height), de --x/--y
    van de plekken uit PLATTEGROND_PLEKKEN. Stopt als de staging andere plekken of een andere volgorde heeft."""
    for blok in soup.select('.plattegrond-interactief'):
        img = blok.select_one('img.plattegrond-interactief__img')
        plekken = blok.select('li.plattegrond__plek')
        namen = [tekst_van(li.select_one('.plattegrond__plek-naam')) for li in plekken]
        if img is None or namen != [n for n, _, _ in PLATTEGROND_PLEKKEN]:
            raise SystemExit(f'plattegrond: andere plekken op de staging dan PLATTEGROND_PLEKKEN: {namen}')
        img['src'] = PLATTEGROND_3D['src']
        img['srcset'] = f'{PLATTEGROND_3D["src"]} 1200w, {PLATTEGROND_3D["groot"]} 1920w'
        img['sizes'] = '(min-width: 1024px) 66vw, 100vw'
        img['width'] = str(PLATTEGROND_3D['breed'])
        img['height'] = str(PLATTEGROND_3D['hoog'])
        for k in ('data-media-source', 'data-media-score'):
            if k in img.attrs:
                del img[k]
        for li, (_, x, y) in zip(plekken, PLATTEGROND_PLEKKEN):
            li['style'] = f'--x: {x}%; --y: {y}%'
        log.append(('plattegrond', f'3D-render wellnessasteria.nl, {len(plekken)} stippen'))


def spiegel_pagina(staging_pad, info, links, assets, droog):
    log = []
    status, data = haal(BASIS + staging_pad)
    if status != 200:
        raise SystemExit(f'{staging_pad}: status {status}')
    html = data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    herschrijf_assets(soup, assets)   # vóór de eigen toevoegingen (spiegel.css/js, favicon)
    eigen = links['paginas'][info['sleutel']]
    canon = VISIT + eigen

    head = soup.head
    for m in head.find_all('meta', attrs={'name': 'robots'}):
        m.decompose()
    for l in head.find_all('link', rel=lambda r: r and ('canonical' in r or 'alternate' in r)):
        l.decompose()
    for c in head.find_all(string=lambda s: isinstance(s, Comment) and 'nav-engine' in s):
        c.extract()
    for s in head.find_all('script', type='application/ld+json'):
        try:
            j = json.loads(s.string)
            if isinstance(j, dict) and 'url' in j:
                j['url'] = canon
                s.string = json.dumps(j, ensure_ascii=False)
        except Exception:   # noqa: BLE001
            pass
    vp = head.find('meta', attrs={'name': 'viewport'})
    titel = tekst_van(head.title) if head.title else ''
    nieuw = BeautifulSoup(
        '<meta name="robots" content="noindex, follow">'
        f'<link rel="canonical" href="{canon}">'
        f'<meta property="og:url" content="{canon}">'
        f'<meta property="og:title" content="{titel.replace(chr(34), "&quot;")}">'
        '<meta property="og:site_name" content="Hotel Asteria Venray">'
        '<link rel="icon" href="/favicon.ico">', 'html.parser')
    plek = vp
    for el in list(nieuw.contents):
        plek.insert_after('\n')
        plek = plek.next_sibling
        plek.insert_after(el)
        plek = el
    laatste_css = head.find_all('link', rel='stylesheet')[-1]
    laatste_css.insert_after(BeautifulSoup('\n<link rel="stylesheet" href="/spiegel.css">\n<script src="/spiegel.js" defer></script>', 'html.parser'))
    head.append(BeautifulSoup(GA_TAGS, 'html.parser'))
    log.append(('kop', f'noindex, follow; canonical/og:url {canon}; GA4 + Ads; spiegel.css/js; staging-robots/hreflang weg'))

    # taalkeuze weg (alleen NL)
    for ls in soup.select('[data-langswitch], .langswitch'):
        ls.decompose()
        log.append(('taalkeuze weg', ''))

    heeft_boeking = soup.find(id='boeking') is not None
    pagina_kamer = info['sleutel'][len('kamer-'):] if info['sleutel'].startswith('kamer-') else None
    verwerk_links(soup, links, staging_pad, heeft_boeking, log, pagina_kamer)
    markeer_prijzen(soup, pagina_kamer, log)
    plattegrond_3d(soup, log)

    # formulieren
    for f in soup.find_all('form'):
        actie = f.get('action', '')
        cls = f.get('class') or []
        if 'formspree' in actie:
            if 'newsletter__form' in cls or 'footer__newsletter-form' in cls or f.has_attr('data-newsletter-form'):
                f['action'] = '/api/nieuwsbrief'
                f['data-spiegel-nieuwsbrief'] = ''
                log.append(('formulier', 'nieuwsbrief -> /api/nieuwsbrief (Klaviyo, spiegel.js)'))
            elif 'formblock__form' in cls:
                f['action'] = 'mailto:info@asteria.nl'
                f['enctype'] = 'text/plain'
                log.append(('formulier', 'contactformulier -> e-mail aan info@asteria.nl (spiegel.js)'))
            else:
                raise SystemExit(f'onbekend Formspree-formulier op {staging_pad}: {cls}')

    body = soup.body
    body.append(BeautifulSoup(COOKIE, 'html.parser'))

    uit = str(soup)
    # controles
    rest = re.findall(r'(?:href|src|action)="([^"]*(?:effectytools|formspree|bookingEngine)[^"]*)"', uit)
    if rest:
        raise SystemExit(f'{staging_pad}: nog staging-/Formspree-/bookingEngine-verwijzingen: {rest[:5]}')
    if re.search(r'href="#"', uit):
        raise SystemExit(f'{staging_pad}: nog href="#" (niet-gebouwde link): ' + ', '.join(re.findall(r'<a [^>]*href="#"[^>]*>', uit)[:3]))
    if [m for m in re.findall(r'<[a-z]+[^>]*>€ …', uit) if 'data-kamer-vanaf-bedrag' not in m]:
        raise SystemExit(f'{staging_pad}: nog een prijsplaatshouder zonder data-kamer-vanaf')
    if re.search(r'"/assets/', uit):
        raise SystemExit(f'{staging_pad}: nog /assets/-verwijzingen')
    kop = '<!--\n  Spiegel van de Effecty-staging-pagina ' + staging_pad + ' (nieuwe asteria.nl-huisstijl).\n' \
          '  NIET met de hand bewerken: python3 scripts/staging_spiegel.py haalt de pagina opnieuw op en schrijft dit bestand.\n' \
          '  Linkset: translations/spiegel-links.json. Eigen gedrag: spiegel.js / spiegel.css.\n-->\n'
    uit = re.sub(r'^(<!DOCTYPE html>|<!doctype html>)\s*', lambda m: m.group(1) + '\n' + kop, uit, count=1)
    if not droog:
        p = os.path.join(ROOT, info['bestand'])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(uit)
    return eigen, log, len(uit)


def main():
    droog = '--droog' in sys.argv
    with open(os.path.join(ROOT, 'translations', 'spiegel-links.json'), encoding='utf-8') as f:
        links = json.load(f)
    assets = Assets(droog)
    alles = {}
    for staging_pad, info in links['spiegel'].items():
        print(f'== {staging_pad} -> {info["bestand"]}')
        eigen, log, n = spiegel_pagina(staging_pad, info, links, assets, droog)
        samengevat = {}
        for soort, wat in log:
            samengevat.setdefault(soort, []).append(wat)
        for soort, lijst in samengevat.items():
            if soort in ('Mews', '#boeking -> Mews'):
                print(f'   {soort}: {len(lijst)}x' + (' (' + '; '.join(x for x in lijst if '[' in x) + ')' if any('[' in x for x in lijst) else ''))
            else:
                for wat in lijst:
                    print(f'   {soort}: {wat}')
        print(f'   -> {eigen} ({n} tekens)')
        alles[staging_pad] = {'adres': eigen, 'bestand': info['bestand'], 'log': log}
    # opruimen: bestanden in nieuw-assets/ die niet meer gebruikt worden
    gebruikt = {p.lstrip('/') for p in assets.bytes} | EIGEN_ASSETS
    for p in EIGEN_ASSETS:
        if not os.path.exists(os.path.join(ROOT, p)):
            raise SystemExit(f'eigen asset ontbreekt: {p}')
    weg = []
    if not droog:
        for dp, _, fs in os.walk(os.path.join(ROOT, ASSETMAP)):
            for fn in fs:
                rel = os.path.relpath(os.path.join(dp, fn), ROOT)
                if rel not in gebruikt:
                    os.remove(os.path.join(ROOT, rel))
                    weg.append(rel)
    totaal = sum(assets.bytes.values())
    print(f'== assets: {len(assets.bytes)} bestanden in {ASSETMAP}/, {totaal / 1e6:.1f} MB; '
          f'{len(assets.hergebruik)} hergebruikt uit de repo ({", ".join(sorted(set(assets.hergebruik.values())))}); '
          f'{len(weg)} oude weg; {len(assets.fouten)} fouten')
    for f in assets.fouten:
        print('   FOUT', f)
    os.makedirs(os.path.join(ROOT, 'qa'), exist_ok=True)
    with open(os.path.join(ROOT, 'qa', 'staging-spiegel-log.json'), 'w', encoding='utf-8') as f:
        json.dump({'paginas': alles, 'assets': {'aantal': len(assets.bytes), 'bytes': totaal, 'hergebruik': assets.hergebruik,
                   'fouten': assets.fouten}}, f, ensure_ascii=False, indent=1)
    if assets.fouten:
        sys.exit(1)


if __name__ == '__main__':
    main()
