#!/usr/bin/env python3
"""Playwright-test voor de spiegel van de Effecty-staging (scripts/staging_spiegel.py).

Gebruik:
  python3 -m http.server 8781 --directory .       # in de repo-root, in een tweede terminal
  python3 scripts/test_staging_spiegel.py [--basis http://localhost:8781] [--schermafdruk map] [--zonder-staging]
  python3 scripts/test_staging_spiegel.py --basis https://<tak>.asteria-pages.pages.dev   # preview: nette adressen

Per pagina uit translations/spiegel-links.json ("spiegel"), op 390 en 1440:
- pixelverschil staging vs. spiegel (volledige pagina, prefers-reduced-motion, video's op frame 0, cookiemelding
  weggeklikt; verschil = pixels met een kanaalverschil > 32, over de grootste van de twee hoogtes) + schermafdrukken
  naast elkaar (<map>/<pagina>-<breedte>.png) als --schermafdruk is gegeven; zonder --zonder-staging;
- geen 4xx/5xx of mislukte requests op het eigen domein (alle assets lokaal), geen consolefouten van eigen code
  (alleen fouten van de pagina zelf, niet van gtag/Mews);
- geen horizontale scroll;
- kop: robots noindex, follow; canonical en og:url = eigen visit-adres; GA4 G-DPCP945DCG + AW-998609513 + linker;
  niet in sitemap.xml; geen enkele verwijzing naar de staging;
- links: alleen spiegeladressen, andere visit.asteria.nl-pagina's (bestand in de repo, of het arrangementenoverzicht uit
  de linkset), Mews (config 6dc9094c), tel/mailto, juridische asteria.nl-links (privacy, algemene voorwaarden, menukaart-
  pdf's in /upload/files/), Google Maps/zoeken en social; geen Zalen & feesten/Vergaderen in het menu;
- menu: 1440 = submenu Hotel opent bij hover; 390 = hamburger opent de drawer, submenu klapt uit, sluitknop sluit;
- boeken: Boek nu (kop) opent de Mews-widget (gestubd), kamerknoppen met data-room geven showRates(kamer);
- nieuwsbrief in de voet post naar /api/nieuwsbrief (gemockt) en toont een bevestiging; contactformulier (contact)
  maakt een mailto naar info@asteria.nl.
"""
import json
import os
import re
import sys
import urllib.parse

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGING = 'https://asteria.staging.effectytools.com'
MEWS = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556'

args = sys.argv[1:]
def optie(naam, standaard=None):
    if naam in args:
        i = args.index(naam); w = args[i + 1]; del args[i:i + 2]; return w
    return standaard
BASIS = optie('--basis', 'http://localhost:8781').rstrip('/')
SHOT = optie('--schermafdruk')
ZONDER_STAGING = '--zonder-staging' in args
PRIJZEN_ECHT = '--prijzen-echt' in args   # kamerprijzen: echte /api/kamer-vanaf (preview) i.p.v. de mock
ALLEEN_PRIJZEN = '--alleen-prijzen' in args
MOCK_PRIJZEN = {'comfort': {'euro': 133, 'datum': '2026-11-08'}, 'comfort-3': {'euro': 142, 'datum': '2026-11-08'},
                'mindervalide': {'euro': 133, 'datum': '2026-11-08'}, 'royale': {'euro': 142, 'datum': '2026-11-08'},
                'deluxe': {'euro': 151, 'datum': '2026-11-08'}, 'junior-suite': {'euro': 160, 'datum': '2026-11-08'},
                'suite': {'euro': 169, 'datum': '2026-11-08'}, 'bruidssuite': None}
LOKAAL = re.match(r'https?://(localhost|127\.0\.0\.1)', BASIS) is not None
links = json.load(open(os.path.join(ROOT, 'translations', 'spiegel-links.json'), encoding='utf-8'))
SPIEGELADRESSEN = {links['paginas'][v['sleutel']] for v in links['spiegel'].values()}
resultaten = []

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def url_van(info):
    return BASIS + ('/' + info['bestand'] if LOKAAL else links['paginas'][info['sleutel']])

def toegestaan(href):
    """Link-allowlist."""
    if href.startswith(('tel:', 'mailto:')) or href.startswith('#'):
        return True
    u = urllib.parse.urlsplit(href)
    host = u.netloc
    if host in ('', 'visit.asteria.nl') or href.startswith(BASIS):
        pad = u.path
        if LOKAAL and pad.endswith('.html'):
            pad = pad[:-5]
        if pad in SPIEGELADRESSEN or pad == links['arrangementenoverzicht'] or pad == links['paginas']['home']:
            return True
        return os.path.exists(os.path.join(ROOT, pad.lstrip('/') + '.html'))
    if href.startswith(MEWS):
        return True
    if host == 'www.asteria.nl':
        return u.path in ('/privacy', '/algemene-voorwaarden') or u.path.startswith('/upload/files/')
    if host in ('maps.google.com', 'www.google.com', 'search.google.com', 'www.facebook.com', 'www.instagram.com', 'www.linkedin.com'):
        return True
    return False

MEWS_STUB = """
window.__mews = [];
window.Mews = { Distributor: function (cfg, cb) {
  window.__mewsCfg = cfg;
  var api = {}; ['open','showRates','showRooms','setStartDate','setEndDate','setAdultCount','setLanguageCode','setVoucherCode'].forEach(function (m) {
    api[m] = function (x) { window.__mews.push(m + (x === undefined ? '' : ':' + (x instanceof Date ? x.toISOString().slice(0,10) : x))); };
  });
  cb(api);
} };
"""

def stil_maken(pg):
    """Lazy-afbeeldingen laden, reveals afspelen, video's op frame 0."""
    pg.evaluate("""async () => {
      const h = () => document.documentElement.scrollHeight;
      for (let y = 0; y < h(); y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
      document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager');
      await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 5000); })));
      document.querySelectorAll('video').forEach(v => { try { v.pause(); v.currentTime = 0; } catch (e) {} });
      document.querySelectorAll('.arrangement-card').forEach(c => c.classList.add('is-visible'));
      await new Promise(r => setTimeout(r, 400));
    }""")

def verschil(a, b):
    ia, ib = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    w = min(ia.width, ib.width); h = min(ia.height, ib.height); hmax = max(ia.height, ib.height)
    d = ImageChops.difference(ia.crop((0, 0, w, h)), ib.crop((0, 0, w, h))).convert('L').point(lambda v: 255 if v > 32 else 0)
    anders = d.histogram()[255] + (hmax - h) * w
    return 100.0 * anders / (w * hmax), ia.height, ib.height

def naast_elkaar(a, b, uit):
    ia, ib = Image.open(a), Image.open(b)
    c = Image.new('RGB', (ia.width + ib.width + 20, max(ia.height, ib.height)), (255, 0, 255))
    c.paste(ia, (0, 0)); c.paste(ib, (ia.width + 20, 0))
    if c.height > 16000:   # handzaam houden
        c = c.resize((c.width * 16000 // c.height, 16000))
    c.save(uit)

tabel = []

PRIJS_JS = """() => [...document.querySelectorAll('[data-kamer-vanaf]')].map(e => {
  const r = e.getBoundingClientRect(), k = e.closest('article, li, aside, .boekbalk') || e.parentElement;
  return {k: e.dataset.kamerVanaf, zicht: getComputedStyle(e).visibility === 'visible', tekst: e.innerText.replace(/\\s+/g, ' ').trim(),
          h: Math.round(r.height), kh: Math.round(k.getBoundingClientRect().height)}; })"""

def prijzen_test(b):
    """Kamerprijzen op de spiegel: gemockte API (prijs verschijnt, null = verborgen), falende API (alles verborgen, zelfde
    hoogte = geen verspringen); met --prijzen-echt de echte /api/kamer-vanaf."""
    for staging_pad, info in links['spiegel'].items():
        bron = open(os.path.join(ROOT, info['bestand']), encoding='utf-8').read()
        if 'data-kamer-vanaf=' not in bron:
            continue
        adres = links['paginas'][info['sleutel']]
        for w, h, mob in ((390, 844, True), (1440, 900, False)):
            tag = f'[{adres} {w} prijzen]'
            uitkomst = {}
            for stand in (('echt',) if PRIJZEN_ECHT else ()) + ('mock', 'fout'):
                ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob, device_scale_factor=1, reduced_motion='reduce')
                ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
                ctx.route('**/www.googletagmanager.com/**', lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))
                if stand == 'mock':
                    ctx.route('**/api/kamer-vanaf*', lambda r: r.fulfill(status=200, content_type='application/json',
                              body=json.dumps({'ok': True, 'van': '2026-11-03', 'tot': '2026-12-28', 'prijzen': MOCK_PRIJZEN})))
                elif stand == 'fout':
                    ctx.route('**/api/kamer-vanaf*', lambda r: r.fulfill(status=500, content_type='application/json', body='{"ok":false}'))
                pg = ctx.new_page()
                pg.goto(url_van(info), wait_until='domcontentloaded')
                vroeg = pg.evaluate("[...document.querySelectorAll('[data-kamer-vanaf]')].filter(e => getComputedStyle(e).visibility === 'visible' && /…/.test(e.innerText)).length")
                pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(stand == 'echt' and 1500 or 300)
                r = pg.evaluate(PRIJS_JS)
                uitkomst[stand] = r
                if stand == 'mock':
                    goed = all((e['zicht'] and re.search('€\\s' + str(MOCK_PRIJZEN[e['k']]['euro']) + r'\b', e['tekst']) and 'per nacht' in e['tekst'].lower())
                               if MOCK_PRIJZEN.get(e['k']) else not e['zicht'] for e in r)
                    check(f'{tag} gemockte API: {len(r)} prijzen gevuld (vanaf € X per nacht), kamer zonder prijs verborgen, nooit "€ …" zichtbaar',
                          r and goed and vroeg == 0, str([(e['k'], e['zicht'], e['tekst']) for e in r])[:300])
                    if True:   # schermafdruk met prijzen
                        d = SHOT or os.path.join(ROOT, 'qa', 'spiegel')
                        os.makedirs(d, exist_ok=True)
                        el = pg.locator('[data-kamer-vanaf]').first
                        el.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
                        pg.screenshot(path=os.path.join(d, f"prijzen-{adres.strip('/').replace('/', '_')}-{w}.png"), full_page=(adres == '/kamers'))
                elif stand == 'fout':
                    check(f'{tag} falende API: alle prijsregels verborgen, geen "€ …" zichtbaar', r and not any(e['zicht'] for e in r), str(r)[:200])
                    m = uitkomst.get('mock') or []
                    check(f'{tag} geen verspringen: zelfde hoogte prijsregel en kaart met en zonder prijs',
                          [(e['h'], e['kh']) for e in r] == [(e['h'], e['kh']) for e in m], str([(e['h'], e['kh']) for e in r])[:200] + ' / ' + str([(e['h'], e['kh']) for e in m])[:200])
                else:
                    zicht = [e for e in r if e['zicht']]
                    check(f'{tag} echte API: {len(zicht)}/{len(r)} prijzen gevuld', zicht and all(_re_euro(e['tekst']) for e in zicht),
                          str([(e['k'], e['tekst']) for e in zicht])[:300])
                ctx.close()

def _re_euro(t):
    return re.search(r'€\s?\d+', t) is not None

with sync_playwright() as p:
    b = p.chromium.launch()
    prijzen_test(b)
    if ALLEEN_PRIJZEN:
        links['spiegel'] = {}
    sitemap = ''
    try:
        sitemap = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    except OSError:
        pass
    # eigen pagina's met de spiegel-kop/voet (geen staging-tegenhanger: geen pixelvergelijking): arrangementenoverzicht
    EIGEN = [] if ALLEEN_PRIJZEN else [('(eigen)', {'bestand': 'arrangementen-v2.html', 'adres': links['arrangementenoverzicht'], 'eigen': True})]
    for staging_pad, info in list(links['spiegel'].items()) + EIGEN:
        adres = info.get('adres') or links['paginas'][info['sleutel']]
        eigen_pg = info.get('eigen', False)
        url = BASIS + ('/' + info['bestand'] if LOKAAL else adres)
        print(f'\n== {staging_pad} -> {adres}  ({url})')
        rij = {'pagina': staging_pad, 'adres': adres}
        for w, h, mob in ((390, 844, True), (1440, 900, False)):
            tag = f'[{adres} {w}]'
            ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob,
                                device_scale_factor=1, reduced_motion='reduce')
            ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
            ctx.route('https://app.mews.com/distributor/distributor.min.js',
                      lambda r: r.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB))
            ctx.route('**/www.googletagmanager.com/**', lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))
            ctx.route('**/api/kamer-vanaf*', lambda r: r.fulfill(status=200, content_type='application/json',
                      body=json.dumps({'ok': True, 'van': '2026-11-03', 'tot': '2026-12-28', 'prijzen': MOCK_PRIJZEN})))
            nb = []
            ctx.route('**/api/nieuwsbrief', lambda r: (nb.append(r.request.post_data), r.fulfill(status=200, content_type='application/json', body='{"ok":true}')))
            pg = ctx.new_page()
            netfout, console = [], []
            eigen_host = urllib.parse.urlsplit(BASIS).netloc
            pg.on('response', lambda r: netfout.append(f'{r.status} {r.url}') if r.status >= 400 and urllib.parse.urlsplit(r.url).netloc == eigen_host else None)
            pg.on('requestfailed', lambda r: netfout.append(f'mislukt {r.url} {r.failure}') if urllib.parse.urlsplit(r.url).netloc == eigen_host else None)
            pg.on('console', lambda m: console.append(m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: console.append('pageerror ' + str(e)))
            pg.goto(url, wait_until='load', timeout=90000); pg.wait_for_timeout(1000)
            stil_maken(pg)
            check(f'{tag} geen 4xx/5xx/mislukte requests op het eigen domein', not netfout, '; '.join(netfout[:5]))
            check(f'{tag} geen consolefouten', not console, '; '.join(console[:3]))
            ov = pg.evaluate('document.documentElement.scrollWidth - window.innerWidth')
            check(f'{tag} geen horizontale scroll', ov <= 0, f'{ov}px')

            if w == 1440:
                kop = pg.evaluate("""() => ({
                  robots: document.querySelector('meta[name=robots]')?.content,
                  canon: document.querySelector('link[rel=canonical]')?.href,
                  og: document.querySelector('meta[property="og:url"]')?.content,
                  html: document.documentElement.outerHTML })""")
                eigen = 'https://visit.asteria.nl' + adres
                check(f'{tag} robots noindex, follow', kop['robots'] == 'noindex, follow', kop['robots'])
                check(f'{tag} canonical + og:url = eigen adres', kop['canon'] == eigen and kop['og'] == eigen, f"{kop['canon']} {kop['og']}")
                bron = open(os.path.join(ROOT, info['bestand']), encoding='utf-8').read()
                check(f'{tag} GA4 + Google Ads + linker' + ('' if eigen_pg else ' zoals hotel-venray-v2'),
                      all(s in bron for s in ("gtag/js?id=G-DPCP945DCG", "gtag('config', 'G-DPCP945DCG', { linker: { domains: ['asteria.nl', 'visit.asteria.nl'] } })",
                                              "gtag('config', 'AW-998609513')", "AW-998609513/t8vbCLm6i7IcEOmkltwD") + (() if eigen_pg else ("accept_incoming: true",))))
                check(f'{tag} geen verwijzing naar de staging of Formspree', 'effectytools' not in bron and 'formspree' not in bron)
                check(f'{tag} niet in sitemap.xml', adres not in re.findall(r'<loc>https://visit\.asteria\.nl([^<]*)</loc>', sitemap))
                hrefs = pg.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
                # arrangementenoverzicht: de feestdagkaarten (Kerst, Oud & Nieuw) linken naar hun pagina op asteria.nl (er is geen eigen pagina)
                fout = sorted({x for x in hrefs if not toegestaan(x) and not (eigen_pg and x.startswith('https://www.asteria.nl/arrangementen/'))})
                check(f'{tag} alle links op de allowlist ({len(hrefs)} links)', not fout, ', '.join(fout[:8]))
                menu = pg.evaluate("[...document.querySelectorAll('.top-stack, #nav-drawer, footer')].map(e => e.innerText).join(' ')")
                check(f'{tag} geen Zalen & feesten / Vergaderen in kop, drawer en voet', not re.search(r'zalen|vergader|feesten', menu, re.I))
                mews = pg.evaluate("[...document.querySelectorAll('[data-mews-open], a.mews-open')].map(a => a.getAttribute('href'))")
                kopvoet = pg.evaluate("[...document.querySelectorAll('.top-stack a[href], #nav-drawer a[href], footer a[href]')].map(a => a.getAttribute('href'))")
                buiten = [x for x in kopvoet if 'asteria.nl' in x and not x.startswith('mailto:') and 'visit.asteria.nl' not in x and x not in ('https://www.asteria.nl/privacy', 'https://www.asteria.nl/algemene-voorwaarden')]
                check(f'{tag} kop/drawer/voet: geen asteria.nl behalve privacy en voorwaarden', not buiten, str(buiten))
                check(f'{tag} {len(mews)} boekknoppen, alle naar Mews 6dc9094c', mews and all(m.startswith(MEWS) for m in mews))
                # submenu Hotel bij hover
                sub = pg.locator('.main-nav .has-sub').first
                sub.hover(); pg.wait_for_timeout(400)
                zichtbaar = pg.evaluate("getComputedStyle(document.querySelector('.main-nav .has-sub .nav-sub')).visibility")
                check(f'{tag} submenu opent bij hover', zichtbaar == 'visible', zichtbaar)
                pg.mouse.move(5, 600)
            else:
                pg.click('.nav-hamburger'); pg.wait_for_timeout(500)
                open_ = pg.evaluate("document.getElementById('nav-drawer').classList.contains('is-open')")
                pg.click('#nav-drawer .drawer-parent'); pg.wait_for_timeout(300)
                uit = pg.evaluate("document.querySelector('#nav-drawer .has-sub').classList.contains('is-open') || document.querySelector('#nav-drawer .drawer-parent').getAttribute('aria-expanded') === 'true'")
                pg.click('#nav-drawer [data-close-drawer], #nav-drawer .nav-drawer__close'); pg.wait_for_timeout(400)
                dicht = not pg.evaluate("document.getElementById('nav-drawer').classList.contains('is-open')")
                check(f'{tag} hamburger opent drawer, submenu klapt uit, sluitknop sluit', open_ and uit and dicht, f'{open_} {uit} {dicht}')

            # boeken: Boek nu in de kop (390: onderin de drawer of de kop-knop als die zichtbaar is)
            pg.evaluate('window.__mews = []')
            knop = pg.locator('.nav-cta:visible').first if pg.locator('.nav-cta:visible').count() else None
            if knop is None:
                pg.click('.nav-hamburger'); pg.wait_for_timeout(400)
                knop = pg.locator('#nav-drawer [data-mews-open], #nav-drawer a.mews-open').first
            knop.click(); pg.wait_for_timeout(700)
            calls = pg.evaluate('window.__mews || []')
            check(f'{tag} Boek nu opent de Mews-widget', 'open' in calls and (pg.evaluate('window.__mewsCfg && window.__mewsCfg.configurationIds[0]') or '').startswith('6dc9094c'), str(calls))
            kamerknop = pg.locator('[data-mews-open][data-room], a.mews-open[data-room]')
            if kamerknop.count():
                pg.evaluate('window.__mews = []')
                k = kamerknop.first
                room = k.get_attribute('data-room')
                k.scroll_into_view_if_needed()
                pg.evaluate('el => el.click()', k.element_handle())
                pg.wait_for_timeout(300)
                calls = pg.evaluate('window.__mews || []')
                check(f'{tag} kamerknop geeft showRates(kamer) + open', f'showRates:{room}' in calls and 'open' in calls, str(calls))
                pg.keyboard.press('Escape')

            if w == 1440:
                # nieuwsbrief in de voet (bureaublad-variant of de mobiele: de eerste zichtbare)
                f = pg.locator('form[data-spiegel-nieuwsbrief]:visible').first
                if f.count():
                    f.locator('input[type=email]').fill('test@voorbeeld.nl')
                    f.locator('button[type=submit]').click(); pg.wait_for_timeout(800)
                    body = json.loads(nb[-1]) if nb else {}
                    melding = pg.evaluate("[...document.querySelectorAll('.spiegel-melding, [data-newsletter-success].is-visible')].map(e => e.innerText).join(' ')")
                    check(f'{tag} nieuwsbrief -> /api/nieuwsbrief (nl) + bevestiging', body.get('email') == 'test@voorbeeld.nl' and body.get('taal') == 'nl' and 'aangemeld' in melding.lower() or 'bedankt' in melding.lower(), f'{body} {melding[:60]}')
                if pg.locator('.formblock__form').count():
                    pg.fill('#fb-naam', 'Test Persoon'); pg.fill('#fb-mail', 'test@voorbeeld.nl'); pg.fill('#fb-bericht', 'Testbericht')
                    pg.evaluate("document.querySelector('.formblock__form').requestSubmit()"); pg.wait_for_timeout(300)
                    mt = pg.evaluate('window.spiegelContact || ""')
                    check(f'{tag} contactformulier -> mailto info@asteria.nl', mt.startswith('mailto:info@asteria.nl?subject=') and 'Testbericht' in urllib.parse.unquote(mt), mt[:80])

            # wellness: 3D-plattegrond van wellnessasteria.nl met 11 stippen binnen de tekening; klik op stip 7 = Boscabine
            if pg.locator('[data-plattegrond]').count():
                pg.locator('.plattegrond-interactief__kaart').scroll_into_view_if_needed(); pg.wait_for_timeout(500)
                pl = pg.evaluate("""(()=>{const i=document.querySelector('.plattegrond-interactief__img'),r=i.getBoundingClientRect();
                    const st=[...document.querySelectorAll('.plattegrond__stip')].map(s=>{const q=s.getBoundingClientRect();
                      return [(q.left+q.width/2-r.left)/r.width,(q.top+q.height/2-r.top)/r.height]});
                    return {src:i.currentSrc, w:i.naturalWidth, h:i.naturalHeight, st}})()""")
                binnen = all(0.05 < x < 0.95 and 0.05 < y < 0.95 for x, y in pl['st'])
                check(f'{tag} plattegrond: 3D-render, 11 stippen binnen de tekening',
                      'wellness-plattegrond-3d-' in pl['src'] and len(pl['st']) == 11 and binnen, str(pl)[:200])
                pg.locator('.plattegrond__stip').nth(6).click(); pg.wait_for_timeout(300)
                act = pg.evaluate("(document.querySelector('.plattegrond__plek.is-actief .plattegrond__plek-naam')||{}).textContent||''")
                check(f'{tag} plattegrond: klik op stip 7 toont Boscabine', 'Boscabine' in act, act)

            # pixelvergelijking met de staging
            if not ZONDER_STAGING and not eigen_pg:
                pg.goto(url, wait_until='load', timeout=90000); pg.wait_for_timeout(1000); stil_maken(pg)
                d = SHOT or os.path.join(ROOT, 'qa', 'spiegel')
                os.makedirs(d, exist_ok=True)
                naam = adres.strip('/').replace('/', '_') or 'home'
                a_ = os.path.join(d, f'{naam}-{w}-spiegel.png'); s_ = os.path.join(d, f'{naam}-{w}-staging.png')
                pg.screenshot(path=a_, full_page=True, timeout=120000)
                sp = ctx.new_page()
                for poging in range(3):   # de staging is soms traag (networkidle > 30 s)
                    try:
                        sp.goto(STAGING + staging_pad, wait_until='load', timeout=90000); sp.wait_for_timeout(1500); break
                    except Exception as e:   # noqa: BLE001
                        if poging == 2: raise
                        print(f'   staging opnieuw ({e.__class__.__name__})')
                stil_maken(sp)
                sp.screenshot(path=s_, full_page=True, timeout=120000)
                pct, hs, ha = verschil(s_, a_)
                rij[w] = f'{pct:.1f} % (hoogte {hs} -> {ha})'
                print(f'   pixelverschil {w}: {pct:.1f} %  (staging {hs} px, spiegel {ha} px)')
                naast_elkaar(s_, a_, os.path.join(d, f'{naam}-{w}.png'))
                sp.close()
            ctx.close()
        tabel.append(rij)
    b.close()

print('\n| pagina | spiegeladres | 390 | 1440 |\n|---|---|---|---|')
for r in tabel:
    print(f"| {r['pagina']} | {r['adres']} | {r.get(390, '-')} | {r.get(1440, '-')} |")
fouten = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(fouten)}/{len(resultaten)} checks OK')
sys.exit(1 if fouten else 0)
