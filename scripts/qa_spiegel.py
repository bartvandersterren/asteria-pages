#!/usr/bin/env python3
"""Functionele QA (Playwright, Chromium) van de spiegelpagina's, de kamer-w1-pagina's, /hotel-venray-v2 en /arrangementen-v2.

Gebruik:
  python3 scripts/qa_spiegel.py --lokaal [--poort 8790]          # start zelf een server met nette adressen (zoals Pages)
  python3 scripts/qa_spiegel.py --basis https://visit.asteria.nl  # live
  opties: --pagina /wellness (meer keren mag), --breedte 390|1440, --schermafdruk map, --zonder-links, --json uit.json

Lokaal: /api/kamer-vanaf, /api/arr-vanaf en /api/arr-kalender gaan door naar visit.asteria.nl (echte prijzen);
/api/nieuwsbrief is altijd gemockt (er wordt niemand aangemeld), Mews-distributor is altijd gestubd (geen echte widget).
De bestaande scripts/test_staging_spiegel.py (pixelvergelijking met de staging) blijft daarnaast bestaan.

Per pagina, op 1440 en 390:
- consolefouten, mislukte requests en 4xx/5xx (eigen domein en derden apart), gebroken afbeeldingen (naturalWidth 0 na
  scrollen), video's die niet spelen (autoplay-video's in beeld);
- kop: title/canonical/og:url/robots, geen "staging"/effectytools; geen horizontale overloop;
- links: intern 200 (na redirects), extern geen 404/410, geen staging-, lege of href="#"-links, geen www.asteria.nl-links
  naar een pagina die als spiegel bestaat; tel:-links geldig;
- live prijzen [data-kamer-vanaf]/[data-arr-vanaf] gevuld (geen "€ …") na networkidle;
- cookiemelding: verschijnt, Akkoord sluit, blijft weg na herladen;
- elk zichtbaar knopje (button, [role=button], summary, a[href^="#"], a[data-mews-open]): klik en kijk of er iets gebeurt
  (DOM, scroll, slider, Mews-aanroep, navigatie). Opent er een laag (dialog/lightbox/drawer/pop-up), dan: video in de laag
  speelt, sluiten via Escape, anders via de sluitknop, en body-scroll is daarna hersteld;
- lightbox: elke vergrootknop/galerijtegel toont een foto (naturalWidth > 0, geen icoon), bijschrift, volgende wisselt,
  Escape/kruisje/achtergrond sluiten, body-scroll hersteld;
- Mews: elke [data-mews-open] geeft open/showRates, met data-room de juiste kamer;
- nieuwsbrief: lege/ongeldige invoer post niet, geldig adres post (gemockt) en toont bevestiging; contactformulier -> mailto;
- menu: 1440 submenu opent, 390 hamburger -> drawer -> sluiten, body-scroll hersteld;
- overlap: midden van elk klikbaar element (na scrollIntoView center) is niet bedekt door iets anders (sticky balk e.d.);
- /hotel-venray-v2 op 390: scratchcard-pop-up verschijnt (45% scroll), sluit, body-scroll hersteld.
Uitvoer: rapport per pagina (FOUT / LET OP / OK-tellingen), exit 1 bij een FOUT.
"""
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import time
import urllib.parse

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = 'https://visit.asteria.nl'
MEWS_CFG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'

args = sys.argv[1:]


def optie(naam, standaard=None, meer=False):
    uit = []
    while naam in args:
        i = args.index(naam)
        uit.append(args[i + 1])
        del args[i:i + 2]
    return uit if meer else (uit[-1] if uit else standaard)


LOKAAL = '--lokaal' in args
POORT = int(optie('--poort', '8790'))
BASIS = (f'http://127.0.0.1:{POORT}' if LOKAAL else optie('--basis', LIVE)).rstrip('/')
PAGINAS_ARG = optie('--pagina', meer=True)
BREEDTES = [int(b) for b in optie('--breedte', meer=True)] or [1440, 390]
SHOT = optie('--schermafdruk')
ZONDER_LINKS = '--zonder-links' in args
JSON_UIT = optie('--json')

links = json.load(open(os.path.join(ROOT, 'translations', 'spiegel-links.json'), encoding='utf-8'))
SPIEGEL = [links['paginas'][v['sleutel']] for v in links['spiegel'].values()]
KAMER_W1 = ['/kamers/royale-kamer', '/kamers/suite', '/kamers/bruidssuite', '/kamers/comfort-kamer-3-personen', '/kamers/mindervalide-kamer']
PAGINAS = PAGINAS_ARG or (SPIEGEL + KAMER_W1 + ['/hotel-venray-v2', '/arrangementen-v2'])
# oude asteria.nl-paden waarvoor een spiegelpagina bestaat
OUD_MET_SPIEGEL = {'/kamers', '/faciliteiten', '/wellness', '/restaurant', '/omgeving', '/over-ons', '/contact', '/arrangementen'}

LINKS_EXTRA = {}
SOFT404 = '<h1>Welkom bij Asteria</h1>'
rapport = {}   # pagina -> list of (niveau, breedte, tekst)


def meld(pagina, niveau, breedte, tekst):
    rapport.setdefault(pagina, []).append((niveau, breedte, tekst))


# ── lokale server met nette adressen (zoals Cloudflare Pages) ──
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass

    def send_head(self):
        pad = urllib.parse.urlsplit(self.path).path
        echt = os.path.join(ROOT, urllib.parse.unquote(pad).lstrip('/'))
        if not os.path.splitext(pad)[1] and not os.path.isdir(echt):
            for k in (echt.rstrip('/') + '.html', os.path.join(echt, 'index.html')):
                if os.path.isfile(k):
                    self.path = '/' + os.path.relpath(k, ROOT) + ('?' + urllib.parse.urlsplit(self.path).query if '?' in self.path else '')
                    break
        elif os.path.isdir(echt) and os.path.isfile(echt.rstrip('/') + '.html'):
            self.path = '/' + os.path.relpath(echt.rstrip('/') + '.html', ROOT)
        return super().send_head()


def start_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', POORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


MEWS_STUB = """
window.__mews = window.__mews || [];
window.Mews = { Distributor: function (cfg, cb) {
  window.__mewsCfg = cfg;
  var api = {}; ['open','showRates','showRooms','setStartDate','setEndDate','setAdultCount','setChildCount','setLanguageCode','setVoucherCode','setCurrencyCode','setIds'].forEach(function (m) {
    api[m] = function (x) { window.__mews.push(m + (x === undefined ? '' : ':' + (x instanceof Date ? x.toISOString().slice(0,10) : x))); return api; };
  });
  cb(api); return api;
} };
"""

# ── JS-hulpjes in de pagina ──
JS_SIG = """() => {
  const h = document.body.innerHTML; let x = 0; for (let i = 0; i < h.length; i += 3) x = (x * 31 + h.charCodeAt(i)) | 0;
  let sl = 0; document.querySelectorAll('*').forEach(e => { if (e.scrollLeft) sl += Math.round(e.scrollLeft); if (e.scrollTop && e !== document.documentElement && e !== document.body) sl += Math.round(e.scrollTop); });
  return [x, Math.round(scrollY), sl, (window.__mews || []).length, location.href].join('|');
}"""

# zichtbare overlagen: fixed/absolute-in-fixed, groot (>= 25% van het scherm), zichtbaar
JS_LAGEN = """() => {
  const uit = [];
  const vw = innerWidth, vh = innerHeight;
  document.querySelectorAll('body *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' || cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.05) return;
    if (el.closest('#cookieBanner')) return;
    const r = el.getBoundingClientRect();
    const w = Math.min(r.right, vw) - Math.max(r.left, 0), h = Math.min(r.bottom, vh) - Math.max(r.top, 0);
    if (w <= 0 || h <= 0 || w * h < 0.25 * vw * vh) return;
    let p = el.parentElement, binnen = false;
    while (p && p !== document.body) { if (getComputedStyle(p).position === 'fixed') { binnen = true; break; } p = p.parentElement; }
    if (binnen) return;
    if (!el.dataset.qaId) el.dataset.qaId = 'l' + Math.random().toString(36).slice(2, 8);
    uit.push(el.dataset.qaId);
  });
  return uit;
}"""

JS_KNOPPEN = """() => {
  const sel = 'button, [role=button], summary, a[href^="#"], a[data-mews-open], [data-carrousel-next], [data-carrousel-prev]';
  const uit = [];
  document.querySelectorAll(sel).forEach((el, i) => {
    if (el.closest('#cookieBanner, form, [data-qa-skip], [aria-hidden="true"]')) return;
    if (el.type === 'submit' || el.disabled) return;
    // al actief (eerste plattegrondstip, actief tabblad): een klik verandert terecht niets
    if (el.classList.contains('is-actief') || el.classList.contains('is-active') || el.getAttribute('aria-pressed') === 'true' || el.getAttribute('aria-selected') === 'true' || el.getAttribute('aria-current')) return;
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    if (r.width < 2 || r.height < 2 || cs.visibility === 'hidden' || cs.display === 'none') return;
    let p = el; let verborgen = false;
    while (p) { const c = getComputedStyle(p); if (c.display === 'none' || c.visibility === 'hidden' || p.hidden) { verborgen = true; break; } p = p.parentElement; }
    if (verborgen) return;
    el.dataset.qaKnop = 'k' + i;
    const tekst = (el.getAttribute('aria-label') || el.innerText || el.getAttribute('title') || el.className || '').trim().replace(/\\s+/g, ' ').slice(0, 60);
    uit.push({ id: 'k' + i, tekst, tag: el.tagName.toLowerCase(), cls: String(el.className || '').slice(0, 60),
               href: el.getAttribute('href'), room: el.getAttribute('data-room'), mews: el.hasAttribute('data-mews-open') });
  });
  return uit;
}"""

JS_BODY_SCROLL = """() => { const b = getComputedStyle(document.body), h = getComputedStyle(document.documentElement);
  return { body: document.body.style.overflow + '|' + b.overflowY + '|' + b.position, html: h.overflowY,
           klassen: document.body.className + ' ' + document.documentElement.className }; }"""


def body_vast(pg):
    s = pg.evaluate(JS_BODY_SCROLL)
    return ('hidden' in s['body'].split('|')[1] or s['body'].split('|')[2] == 'fixed' or s['html'] == 'hidden'
            or re.search(r'(no-scroll|noscroll|lock|is-locked|modal-open|overflow-hidden)', s['klassen']) is not None), s


def sluit_lagen(pg, voor):
    """Sluit lagen die niet in `voor` stonden: Escape, dan een sluitknop. Geeft (lagen, via) terug."""
    nieuw = [l for l in pg.evaluate(JS_LAGEN) if l not in voor]
    if not nieuw:
        return [], None
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(450)
    over = [l for l in pg.evaluate(JS_LAGEN) if l in nieuw]
    if not over:
        return nieuw, 'Escape'
    for l in over:
        knop = pg.locator(f'[data-qa-id="{l}"]').locator(
            '[aria-label*="luit" i], [aria-label*="close" i], [class*="close" i], [class*="sluit" i], [data-close], [data-close-drawer]').first
        try:
            if knop.count():
                knop.click(timeout=1500)
        except Exception:   # noqa: BLE001
            try:
                knop.evaluate('k => k.click()')
            except Exception:   # noqa: BLE001
                pass
    pg.wait_for_timeout(450)
    over2 = [l for l in pg.evaluate(JS_LAGEN) if l in nieuw]
    return nieuw, ('sluitknop' if not over2 else 'NIET')


def laag_info(pg, l):
    return pg.locator(f'[data-qa-id="{l}"]').evaluate("""el => {
      const v = [...el.querySelectorAll('video')].find(x => x.getBoundingClientRect().width > 10); const img = [...el.querySelectorAll('img')].find(i => i.getBoundingClientRect().width > 50);
      return { cls: String(el.className).slice(0, 60), id: el.id, video: !!v,
               speelt: v ? (!v.paused && v.readyState >= 2) || v.currentTime > 0 : null, vsrc: v ? (v.currentSrc || '') : '',
               img: img ? img.naturalWidth : null, imgsrc: img ? (img.currentSrc || img.src) : '',
               svgGroot: [...el.querySelectorAll('svg')].some(s => !s.closest('.lightbox__plan') && s.getBoundingClientRect().width > 200) }; }""")


def nieuwe_context(br, breedte, cookie_ok=True, popup_uit=True):
    mobiel = breedte < 800
    ctx = br.new_context(viewport={'width': breedte, 'height': 844 if mobiel else 900}, is_mobile=mobiel, has_touch=mobiel,
                         device_scale_factor=1, locale='nl-NL',
                         user_agent=('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                                     'Version/17.0 Mobile/15E148 Safari/604.1 asteria-qa') if mobiel else None)
    init = ''
    if cookie_ok:
        init += "try{localStorage.setItem('cookie-consent','1')}catch(e){}"
    if popup_uit:
        init += "try{sessionStorage.setItem('ec_shown','1')}catch(e){}"
    if init:
        ctx.add_init_script(init)
    ctx.route(re.compile(r'https://app\.mews\.com/distributor/.*\.js.*'),
              lambda r: r.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB))
    nb = []
    ctx.route('**/api/nieuwsbrief*', lambda r: (nb.append(r.request.post_data), r.fulfill(
        status=200, content_type='application/json', body='{"ok":true}')))
    if LOKAAL:
        def door(r):
            u = urllib.parse.urlsplit(r.request.url)
            try:
                resp = r.fetch(url=LIVE + u.path + ('?' + u.query if u.query else ''), timeout=90000)
                r.fulfill(response=resp)
            except Exception:   # noqa: BLE001
                r.abort()
        ctx.route(re.compile(r'.*/api/(kamer-vanaf|arr-vanaf|arr-kalender|google-reviews|bb-price).*'), door)
        ctx.route(re.compile(r'.*/api/(track|stats|session).*'), lambda r: r.fulfill(status=204, body=''))
    ctx.__nb = nb
    return ctx


def eigen_host(url):
    h = urllib.parse.urlsplit(url).netloc
    return h == urllib.parse.urlsplit(BASIS).netloc


def qa_pagina(br, pad, breedte, linkset):
    url = BASIS + pad
    ctx = nieuwe_context(br, breedte)
    pg = ctx.new_page()
    console, mislukt = [], []
    pg.on('console', lambda m: console.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: console.append('pageerror: ' + str(e)))
    pg.on('requestfailed', lambda r: mislukt.append(f'{r.url} ({r.failure})'))
    pg.on('response', lambda r: mislukt.append(f'{r.status} {r.url}') if r.status >= 400 else None)
    m = lambda niveau, tekst: meld(pad, niveau, breedte, tekst)   # noqa: E731
    resp = pg.goto(url, wait_until='domcontentloaded', timeout=60000)
    if not resp or resp.status != 200:
        m('FOUT', f'pagina geeft {resp.status if resp else "geen antwoord"}')
        ctx.close()
        return
    try:
        pg.wait_for_load_state('networkidle', timeout=45000)
    except Exception:   # noqa: BLE001
        m('LET OP', 'networkidle niet gehaald binnen 45 s')

    # kop
    kop = pg.evaluate("""() => ({ title: document.title, canon: (document.querySelector('link[rel=canonical]') || {}).href || '',
        og: (document.querySelector('meta[property="og:url"]') || {}).content || '',
        ogt: (document.querySelector('meta[property="og:title"]') || {}).content || '',
        robots: (document.querySelector('meta[name=robots]') || {}).content || '',
        h1: [...document.querySelectorAll('h1')].map(h => h.innerText.trim()).filter(Boolean) })""")
    verwacht = LIVE + pad
    if kop['canon'] != verwacht:
        m('FOUT', f'canonical {kop["canon"]!r} != {verwacht}')
    if kop['og'] and kop['og'] != verwacht:
        m('FOUT', f'og:url {kop["og"]!r} != {verwacht}')
    if re.search(r'staging|effecty', ' '.join([kop['title'], kop['canon'], kop['og'], kop['ogt']]), re.I):
        m('FOUT', f'staging in title/canonical/og: {kop}')
    if 'noindex' not in kop['robots']:
        m('LET OP', f'robots = {kop["robots"]!r}')
    if len(kop['h1']) != 1:
        m('LET OP', f'{len(kop["h1"])} h1-koppen: {kop["h1"][:3]}')
    if breedte == 1440:
        m('INFO', f'title: {kop["title"]!r}')

    # scrollen (lazy laden), dan afbeeldingen/video's
    pg.evaluate("""async () => { const h = () => document.documentElement.scrollHeight;
      for (let y = 0; y < h(); y += 500) { scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 80)); } scrollTo({ top: 0, behavior: 'instant' }); }""")
    pg.wait_for_timeout(1200)
    try:
        pg.wait_for_load_state('networkidle', timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    kapot = pg.evaluate("""() => [...document.images].filter(i => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.getAttribute('src')))
        .map(i => i.currentSrc || i.getAttribute('src'))""")
    for k in sorted(set(kapot)):
        m('FOUT', f'gebroken afbeelding: {k}')
    nietgeladen = pg.evaluate("""() => [...document.images].filter(i => !i.complete && i.loading !== 'lazy').map(i => i.currentSrc || i.src)""")
    for k in nietgeladen[:5]:
        m('LET OP', f'afbeelding niet geladen: {k}')
    videos = pg.evaluate("""async () => { const uit = [];
      for (const v of document.querySelectorAll('video')) {
        const r = v.getBoundingClientRect(); if (r.width < 10) continue;
        v.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' }); await new Promise(r => setTimeout(r, 1500));
        uit.push({ src: v.currentSrc || (v.querySelector('source') || {}).src || '', autoplay: v.autoplay, paused: v.paused,
                   t: v.currentTime, rs: v.readyState, err: v.error ? v.error.code : null }); }
      scrollTo({ top: 0, behavior: 'instant' }); return uit; }""")
    for v in videos:
        if v['err'] or (v['autoplay'] and (v['paused'] or v['t'] == 0)):
            m('FOUT', f'video speelt niet: {v}')
    if videos:
        m('OK', f'{len(videos)} video(s) in beeld spelen' if all(not v['err'] and (not v['autoplay'] or v['t'] > 0) for v in videos) else 'video-check')

    # overloop
    ov = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if ov > 0:
        breed = pg.evaluate("""() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1
            && !e.closest('[class*=carrousel],[class*=scroll],[class*=strip],[class*=slider],[class*=track]'))
            .slice(0, 4).map(e => e.tagName + '.' + String(e.className).slice(0, 40))""")
        m('FOUT', f'horizontale overloop {ov}px: {breed}')

    # prijzen
    prijs = pg.evaluate("""() => [...document.querySelectorAll('[data-kamer-vanaf], [data-arr-vanaf]')].map(e => {
        const r = e.getBoundingClientRect(); return { k: e.getAttribute('data-kamer-vanaf') || e.getAttribute('data-arr-vanaf'),
        t: e.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40), vis: getComputedStyle(e).visibility, zichtbaar: r.width > 0,
        gevuld: e.classList.contains('is-gevuld') || e.hasAttribute('data-gevuld') || getComputedStyle(e).visibility === 'visible' }; })""")
    leeg = [p for p in prijs if p['zichtbaar'] and ('…' in p['t'] or not re.search(r'\d', p['t']) or not p['gevuld'])]
    if prijs:
        if leeg:
            m('FOUT', f'{len(leeg)}/{len(prijs)} prijzen niet gevuld: ' + '; '.join(f"{p['k']}={p['t']!r}/{p['vis']}" for p in leeg[:6]))
        else:
            m('OK', f'{len(prijs)} live prijzen gevuld (' + ', '.join(sorted({f"{p['k']} {p['t']}" for p in prijs if p['zichtbaar']}))[:160] + ')')

    # links verzamelen
    alle = pg.evaluate("""() => [...document.querySelectorAll('a')].map(a => ({ href: a.getAttribute('href'), abs: a.href,
        t: (a.innerText || a.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 50) }))""")
    for a in alle:
        h = a['href']
        if h is None or h.strip() == '':
            m('FOUT', f'link zonder href: {a["t"]!r}')
            continue
        if h == '#':
            m('FOUT', f'href="#": {a["t"]!r}')
            continue
        if 'effectytools' in h:
            m('FOUT', f'staging-link: {h}')
        if h.startswith('#'):
            if not pg.evaluate('(id) => !!document.getElementById(id)', h[1:]):
                m('FOUT', f'anker {h} bestaat niet ({a["t"]!r})')
            continue
        if h.startswith('tel:'):
            if not re.fullmatch(r'tel:\+?[0-9]{9,13}', h.replace(' ', '')):
                m('FOUT', f'ongeldige tel-link {h}')
            continue
        if h.startswith('mailto:'):
            continue
        u = urllib.parse.urlsplit(a['abs'])
        if u.netloc in ('www.asteria.nl', 'asteria.nl') and u.path.rstrip('/') in OUD_MET_SPIEGEL:
            m('FOUT', f'link naar oude asteria.nl terwijl er een spiegel is: {h} ({a["t"]!r})')
        if u.scheme in ('http', 'https'):
            linkset.setdefault(a['abs'].split('#')[0], set()).add(pad)

    # cookiemelding: nieuwe context zonder akkoord
    c2 = nieuwe_context(br, breedte, cookie_ok=False)
    p2 = c2.new_page()
    p2.goto(url, wait_until='domcontentloaded', timeout=60000)
    p2.wait_for_timeout(1500)
    zicht = p2.locator('#cookieBanner').is_visible() if p2.locator('#cookieBanner').count() else False
    if not zicht:
        m('FOUT', 'cookiemelding verschijnt niet')
    else:
        try:
            p2.locator('#cookieAccept').click(timeout=3000)
            p2.wait_for_timeout(600)
            weg = not p2.locator('#cookieBanner').is_visible()
            p2.reload(wait_until='domcontentloaded')
            p2.wait_for_timeout(1500)
            blijft = not p2.locator('#cookieBanner').is_visible()
            if weg and blijft:
                m('OK', 'cookiemelding verschijnt, Akkoord sluit, blijft weg na herladen')
            else:
                m('FOUT', f'cookiemelding: weg na Akkoord={weg}, weg na herladen={blijft}')
        except Exception as e:   # noqa: BLE001
            m('FOUT', f'cookiemelding Akkoord niet klikbaar: {str(e)[:120]}')
    c2.close()

    # menu
    if breedte >= 1024:
        sub = pg.locator('.nav .has-sub, nav .has-sub, .main-nav .has-sub').first
        if sub.count():
            try:
                sub.hover()
                pg.wait_for_timeout(400)
                open_ = pg.evaluate("""() => [...document.querySelectorAll('.has-sub')].some(li => [...li.querySelectorAll('ul, .dropdown, .submenu')]
                    .some(u => { const r = u.getBoundingClientRect(); return r.height > 20 && getComputedStyle(u).visibility !== 'hidden' && +getComputedStyle(u).opacity > 0.5; }))""")
                m('OK' if open_ else 'FOUT', 'submenu opent bij hover' if open_ else 'submenu opent niet bij hover')
                pg.mouse.move(5, 600)
            except Exception as e:   # noqa: BLE001
                m('FOUT', f'submenu hover: {str(e)[:100]}')
    else:
        ham = pg.locator('[data-open-drawer], .nav-toggle, .hamburger, [aria-controls="nav-drawer"]').first
        if ham.count() and ham.is_visible():
            ham.click()
            pg.wait_for_timeout(600)
            drawer_open = pg.evaluate("""() => { const d = document.querySelector('#nav-drawer, .nav-drawer, .drawer');
                if (!d) return false; const r = d.getBoundingClientRect(); return r.width > 100 && r.right > 50 && r.left < innerWidth - 50 && getComputedStyle(d).visibility !== 'hidden'; }""")
            if not drawer_open:
                m('FOUT', 'hamburger opent geen drawer')
            else:
                vast, _ = body_vast(pg)
                # submenu in de drawer
                pt = pg.locator('#nav-drawer button[aria-expanded], .nav-drawer button[aria-expanded]').first
                sub_ok = None
                if pt.count() and pt.is_visible():
                    pt.click()
                    pg.wait_for_timeout(400)
                    sub_ok = pt.get_attribute('aria-expanded') == 'true'
                sl = pg.locator('#nav-drawer [data-close-drawer], .nav-drawer [data-close-drawer], #nav-drawer [aria-label*="luit"]').first
                if sl.count() and sl.is_visible():
                    sl.click()
                else:
                    pg.keyboard.press('Escape')
                pg.wait_for_timeout(600)
                dicht = pg.evaluate("""() => { const d = document.querySelector('#nav-drawer, .nav-drawer, .drawer'); const r = d.getBoundingClientRect();
                    return !(r.width > 100 && r.right > 50 && r.left < innerWidth - 50 && getComputedStyle(d).visibility !== 'hidden'); }""")
                vast2, s2 = body_vast(pg)
                tekst = f'drawer open (body vast={vast}), submenu klapt uit={sub_ok}, sluit={dicht}, body-scroll hersteld={not vast2}'
                m('OK' if dicht and not vast2 and sub_ok is not False else 'FOUT', tekst)
        else:
            m('LET OP', 'geen hamburger gevonden op 390')

    # lightbox
    lb_knoppen = pg.evaluate("""() => [...document.querySelectorAll('.galerij__item, [data-lightbox-item], [data-galerij-alle]')].map((k, i) => {
        k.dataset.qaLb = 'b' + i; return { id: 'b' + i, cls: String(k.className).slice(0, 50), plan: k.classList.contains('galerij__item--plan') }; })""")
    if lb_knoppen:
        fout = []
        for kn in lb_knoppen:
            pg.locator(f'[data-qa-lb="{kn["id"]}"]').evaluate("""k => { const pos = k.closest('[data-pos]');
                if (pos && pos.dataset.pos !== '0') pos.click();   // cflow: zijkaart eerst naar het midden (zo werkt een echte klik ook)
                k.click(); }""")
            pg.wait_for_timeout(350)
            st = pg.evaluate("""() => { const b = [...document.querySelectorAll('.lightbox')].find(x => !x.hidden); if (!b) return null;
                const im = b.querySelector('.lightbox__beeld'), pl = b.querySelector('.lightbox__plan');
                return { img: im && !im.hidden ? im.naturalWidth : 0, src: im ? im.getAttribute('src') : '', plan: pl && !pl.hidden,
                         cap: (b.querySelector('.lightbox__bijschrift') || {}).textContent || '' }; }""")
            if st is None:
                fout.append(f'{kn["cls"]}: lightbox opent niet')
            elif kn['plan']:
                if not st['plan']:
                    fout.append(f'{kn["cls"]}: plattegrond niet getoond')
            elif st['plan'] or not st['img']:
                pg.wait_for_timeout(800)
                st2 = pg.evaluate("() => { const b = [...document.querySelectorAll('.lightbox')].find(x => !x.hidden); const im = b.querySelector('.lightbox__beeld'); return im && !im.hidden ? im.naturalWidth : 0; }")
                if st['plan'] or not st2:
                    fout.append(f'{kn["cls"]}: geen foto (plan/svg={st["plan"]}, img={st["img"]}, src={st["src"]!r})')
            if st is not None and not st['cap'].strip() and not kn['plan']:
                fout.append(f'{kn["cls"]}: leeg bijschrift')
            pg.keyboard.press('Escape')
            pg.wait_for_timeout(200)
        # navigatie + sluiten op de eerste zichtbare knop (echte klik)
        eerste = pg.locator('.galerij__item, [data-lightbox-item]').filter(has_not=pg.locator('.galerij__item--plan'))
        zichtbaar = None
        for i in range(eerste.count()):
            if eerste.nth(i).is_visible() and eerste.nth(i).evaluate('k => !k.closest(\'[aria-hidden="true"]\')'):
                zichtbaar = eerste.nth(i)
                break
        if zichtbaar is not None:
            zichtbaar.evaluate('el => el.scrollIntoView({ block: "center", inline: "nearest", behavior: "instant" })')
            pg.wait_for_timeout(300)
            zichtbaar.click()
            pg.wait_for_timeout(400)
            src1 = pg.evaluate("() => (document.querySelector('.lightbox:not([hidden]) .lightbox__beeld') || {}).src || ''")
            vol = pg.locator('.lightbox:not([hidden]) .lightbox__nav--volgende')
            if vol.count():
                vol.click()
                pg.wait_for_timeout(400)
                src2 = pg.evaluate("() => (document.querySelector('.lightbox:not([hidden]) .lightbox__beeld') || {}).src || ''")
                if len(lb_knoppen) > 1 and src2 == src1:
                    fout.append('volgende wisselt de foto niet')
                pg.locator('.lightbox:not([hidden]) .lightbox__nav--vorige').click()
                pg.wait_for_timeout(300)
            if SHOT and pad == '/wellness':
                os.makedirs(SHOT, exist_ok=True)
                pg.screenshot(path=os.path.join(SHOT, f'wellness-lightbox-{breedte}.png'))
            pg.locator('.lightbox:not([hidden]) .lightbox__sluit').click()
            pg.wait_for_timeout(300)
            if pg.locator('.lightbox:not([hidden])').count():
                fout.append('kruisje sluit niet')
            zichtbaar.click()
            pg.wait_for_timeout(300)
            pg.mouse.click(8, 300)   # achtergrond
            pg.wait_for_timeout(300)
            if pg.locator('.lightbox:not([hidden])').count():
                fout.append('klik op de achtergrond sluit niet')
                pg.keyboard.press('Escape')
            vast, s = body_vast(pg)
            if vast:
                fout.append(f'body-scroll niet hersteld na sluiten ({s})')
        if fout:
            for f in sorted(set(fout)):
                m('FOUT', f'lightbox: {f}')
        else:
            m('OK', f'lightbox: {len(lb_knoppen)} knoppen tonen foto/plattegrond + bijschrift, vorige/volgende, sluiten (Escape/kruisje/achtergrond), body-scroll hersteld')

    # elk knopje
    pg.evaluate("scrollTo({ top: 0, behavior: 'instant' })")
    pg.wait_for_timeout(300)
    knoppen = pg.evaluate(JS_KNOPPEN)
    dood, ok_n, lagen_ok, mews_fout = [], 0, [], []
    for kn in knoppen:
        loc = pg.locator(f'[data-qa-knop="{kn["id"]}"]')
        try:
            if not loc.count() or not loc.is_visible() or loc.is_disabled():
                continue   # o.a. een pijl die na een eerdere klik aan het eind van de rij uit staat
            loc.evaluate('el => el.scrollIntoView({ block: "center", inline: "nearest", behavior: "instant" })')
            pg.wait_for_timeout(200)
            voor_lagen = pg.evaluate(JS_LAGEN)
            pg.evaluate('window.__mews = []')
            sig = pg.evaluate(JS_SIG)
            url_voor = pg.url
            try:
                loc.click(timeout=2500)
            except Exception:   # noqa: BLE001
                # bedekt? dan melden en via JS klikken
                pg.wait_for_timeout(600)   # bewegende carrousel (cflow) of balk die nog inschuift: na even wachten opnieuw meten
                bedekt = loc.evaluate("""el => { if (el.closest('[data-pos]')) return null;
                    el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
                    const r = el.getBoundingClientRect(); const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
                    return t && !el.contains(t) && !t.contains(el) ? (t.tagName + '.' + String(t.className).slice(0, 40)) : null; }""")
                if bedekt:
                    meld(pad, 'FOUT', breedte, f'knop {kn["tekst"]!r} is bedekt door {bedekt}')
                loc.evaluate('el => el.click()')
            pg.wait_for_timeout(650)
            calls = pg.evaluate('window.__mews || []')
            if pg.url != url_voor and pg.url.split('#')[0] != url_voor.split('#')[0]:
                ok_n += 1
                pg.go_back(wait_until='domcontentloaded')
                pg.wait_for_timeout(800)
                continue
            if kn['mews']:
                if not any(c.startswith(('open', 'showRates', 'showRooms')) for c in calls):
                    mews_fout.append(f'{kn["tekst"]!r}: geen Mews-aanroep ({calls})')
                elif kn['room'] and f'showRates:{kn["room"]}' not in calls and not any(kn['room'] in c for c in calls):
                    mews_fout.append(f'{kn["tekst"]!r}: kamer {kn["room"]} niet voorgeselecteerd ({calls})')
                else:
                    ok_n += 1
                continue
            nieuw, via = sluit_lagen(pg, voor_lagen)
            if nieuw:
                info = None
                # info vóór het sluiten kan niet meer; opnieuw openen voor de video-check als er een video in zat
                if via == 'NIET':
                    meld(pad, 'FOUT', breedte, f'laag na {kn["tekst"]!r} sluit niet met Escape of sluitknop')
                    pg.reload(wait_until='domcontentloaded')
                    pg.wait_for_timeout(1200)
                    knoppen_n = pg.evaluate(JS_KNOPPEN)   # ids opnieuw toekennen (zelfde volgorde)
                    continue
                vast, s = body_vast(pg)
                if vast:
                    meld(pad, 'FOUT', breedte, f'body-scroll niet hersteld na sluiten van laag van {kn["tekst"]!r} ({s})')
                lagen_ok.append(f'{kn["tekst"][:30]} ({via})')
                ok_n += 1
                continue
            if pg.evaluate(JS_SIG) == sig and not calls and re.search(r'vorige|prev|zur', kn['tekst'] + kn['cls'], re.I):
                # vorige-knop aan het begin van een rij: eerst de volgende-knop in dezelfde sectie, dan nog eens vorige
                loc.evaluate("""el => { const s = el.closest('section') || el.parentElement;
                    const n = [...s.querySelectorAll('button, [role=button]')].find(b => /volgende|next|weiter/i.test((b.getAttribute('aria-label') || '') + b.className) && b.getBoundingClientRect().width > 0);
                    if (n) n.click(); }""")
                pg.wait_for_timeout(700)
                sig = pg.evaluate(JS_SIG)
                loc.evaluate('el => el.click()')
                pg.wait_for_timeout(700)
            if pg.evaluate(JS_SIG) == sig and not calls:
                dood.append(kn)
            else:
                ok_n += 1
        except Exception as e:   # noqa: BLE001
            meld(pad, 'LET OP', breedte, f'knop {kn["tekst"]!r} niet te testen: {str(e)[:100]}')
    for d in dood:
        m('FOUT', f'knop doet niets: {d["tekst"]!r} <{d["tag"]} class="{d["cls"]}"' + (f' href="{d["href"]}"' if d['href'] else '') + '>')
    for f in mews_fout:
        m('FOUT', 'Mews: ' + f)
    m('OK', f'{ok_n}/{len(knoppen)} knoppen reageren' + (f'; lagen open+dicht: {", ".join(lagen_ok[:12])}' if lagen_ok else ''))

    # video in pop-ups (faciliteit-pop-ups e.d.): open laagknoppen opnieuw en kijk naar video/img
    pg.reload(wait_until='domcontentloaded')
    try:
        pg.wait_for_load_state('networkidle', timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    knoppen = pg.evaluate(JS_KNOPPEN)
    gezien = 0
    for kn in knoppen:
        if kn['mews'] or (kn['href'] or '').startswith('#') or gezien > 25:
            continue
        loc = pg.locator(f'[data-qa-knop="{kn["id"]}"]')
        try:
            if not loc.is_visible():
                continue
            voor = pg.evaluate(JS_LAGEN)
            loc.evaluate('el => el.click()')
            pg.wait_for_timeout(1500)
            nieuw = [l for l in pg.evaluate(JS_LAGEN) if l not in voor]
            for l in nieuw:
                gezien += 1
                inf = laag_info(pg, l)
                if inf['video'] and not inf['speelt']:
                    m('FOUT', f'video in pop-up van {kn["tekst"]!r} speelt niet ({inf["vsrc"]})')
                if inf['img'] == 0:
                    m('FOUT', f'afbeelding in pop-up van {kn["tekst"]!r} niet geladen ({inf["imgsrc"]})')
                if inf['svgGroot'] and 'lightbox' in inf['cls'] and not inf['img']:
                    m('FOUT', f'pop-up van {kn["tekst"]!r} toont een groot svg-icoon i.p.v. een foto')
            if nieuw:
                sluit_lagen(pg, voor)
        except Exception:   # noqa: BLE001
            pass

    # overlap: midden van klikbare elementen niet bedekt (na scrollIntoView center)
    bedekt = pg.evaluate("""async () => { const uit = [], verdacht = [];
      const els = [...document.querySelectorAll('a[href], button, [role=button], input, select, textarea, summary')].filter(el => {
        const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
        if (r.width < 8 || r.height < 8 || cs.visibility === 'hidden' || el.closest('#cookieBanner, [aria-hidden="true"], .formblock__trap') || el.name === '_gotcha') return false;
        let p = el; while (p) { const c = getComputedStyle(p); if (c.display === 'none' || c.visibility === 'hidden' || p.hidden || +c.opacity === 0) return false;
          if (c.position === 'fixed' || c.position === 'sticky') return false; p = p.parentElement; } return true; });
      for (const el of els) {
        el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' }); await new Promise(r => requestAnimationFrame(() => r()));
        const r = el.getBoundingClientRect(); if (r.right < 0 || r.left > innerWidth || r.top < 0 || r.bottom > innerHeight) continue;
        const x = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), y = r.top + r.height / 2;
        const t = document.elementFromPoint(x, y);
        if (t && !el.contains(t) && !t.contains(el) && !(el.labels && [...el.labels].some(l => l.contains(t)))) {
          let p = t, vast = false; while (p) { const c = getComputedStyle(p); if (c.position === 'fixed' || c.position === 'sticky') { vast = true; break; } p = p.parentElement; }
          if (vast) verdacht.push(el);
        } }
      // opnieuw na 500 ms: balken die op scroll reageren (IntersectionObserver) hebben dan hun eindstand
      for (const el of verdacht) {
        el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' }); await new Promise(r => setTimeout(r, 500));
        const r = el.getBoundingClientRect(); const x = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1), y = r.top + r.height / 2;
        const t = document.elementFromPoint(x, y);
        if (t && !el.contains(t) && !t.contains(el)) {
          let p = t, vast = false; while (p) { const c = getComputedStyle(p); if (c.position === 'fixed' || c.position === 'sticky') { vast = true; break; } p = p.parentElement; }
          if (vast) uit.push((el.innerText || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 40) + ' <- ' + t.tagName + '.' + String(t.className).slice(0, 40));
        } }
      scrollTo({ top: 0, behavior: 'instant' }); return uit; }""")
    for b in sorted(set(bedekt))[:10]:
        m('FOUT', f'bij scrollen naar het midden bedekt door een vaste balk: {b}')

    # formulieren
    for i, f in enumerate(pg.evaluate("""() => [...document.querySelectorAll('form')].map((f, i) => { f.dataset.qaForm = 'f' + i;
            return { id: 'f' + i, action: f.getAttribute('action') || '', nb: f.hasAttribute('data-spiegel-nieuwsbrief') || /nieuwsbrief/.test(f.getAttribute('action') || ''),
                     zichtbaar: f.getBoundingClientRect().height > 0, email: !!f.querySelector('input[type=email]') }; })""")):
        if not f['zichtbaar']:
            continue
        loc = pg.locator(f'[data-qa-form="{f["id"]}"]')
        nb = ctx.__nb
        if f['nb'] and f['email']:
            n0 = len(nb)
            loc.locator('[type=submit]').first.evaluate('b => b.scrollIntoView({ block: "center", inline: "nearest", behavior: "instant" })')
            loc.locator('input[type=email]').first.fill('')
            loc.locator('[type=submit]').first.click()
            pg.wait_for_timeout(500)
            loc.locator('input[type=email]').first.fill('geen-adres')
            loc.locator('[type=submit]').first.click()
            pg.wait_for_timeout(500)
            leeg_post = len(nb) > n0
            loc.locator('input[type=email]').first.fill('qa-test@voorbeeld.nl')
            for cb in loc.locator('input[type=checkbox][required]').all():
                cb.check()
            loc.locator('[type=submit]').first.click()
            pg.wait_for_timeout(1500)
            gepost = len(nb) > n0 + (1 if leeg_post else 0) or (len(nb) > n0 and not leeg_post)
            melding = pg.evaluate("""(id) => { const f = document.querySelector('[data-qa-form="' + id + '"]'); const p = f.parentNode;
                return [...p.querySelectorAll('[data-newsletter-success], .spiegel-melding, [role=status], [aria-live]')].map(e => e.innerText).join(' ').trim().slice(0, 80); }""", f['id'])
            body = nb[-1] if nb else ''
            ok = gepost and not leeg_post and 'qa-test@voorbeeld.nl' in (body or '') and melding
            m('OK' if ok else 'FOUT', f'nieuwsbrief: lege/ongeldige invoer post niet={not leeg_post}, geldig adres post (gemockt)={gepost}, bevestiging={melding!r}')
        elif f['action'].startswith('mailto:'):
            m('INFO', f'contactformulier -> {f["action"]} (spiegel.js maakt een mailto)')
            # verplichte velden leeg -> browser-validatie
            geldig = loc.evaluate('f => f.checkValidity()')
            vulbaar = loc.evaluate("""f => { let n = 0; f.querySelectorAll('input, textarea, select').forEach(el => {
                if (el.type === 'hidden' || el.name === '_gotcha' || el.disabled) return;
                if (el.tagName === 'SELECT') { if (el.options.length > 1) el.selectedIndex = 1; }
                else if (el.type === 'email') el.value = 'qa-test@voorbeeld.nl';
                else if (el.type === 'tel') el.value = '0612345678';
                else if (el.type === 'date') el.value = '2026-12-01';
                else if (el.type === 'number') el.value = '2';
                else if (el.type === 'checkbox' || el.type === 'radio') el.checked = true;
                else el.value = 'QA-test'; n++; }); return n; }""")
            pg.evaluate("""() => { window.__mailto = null; const o = window.open; window.open = (u) => { window.__mailto = u; return null; };
                document.addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[href^="mailto:"]'); if (a) { window.__mailto = a.href; e.preventDefault(); } }, true); }""")
            nav = []
            pg.on('framenavigated', lambda fr: nav.append(fr.url))
            pg.route('mailto:*', lambda r: r.abort())
            try:
                loc.locator('[type=submit]').first.click(timeout=3000)
            except Exception:   # noqa: BLE001
                pass
            pg.wait_for_timeout(800)
            mailto = pg.evaluate('window.spiegelContact || window.__mailto') or pg.evaluate("() => location.href.startsWith('mailto:') ? location.href : null")
            m('OK' if (mailto or nav) and not geldig else 'LET OP',
              f'contactformulier: leeg ongeldig={not geldig}, {vulbaar} velden gevuld, mailto={str(mailto)[:90]!r}')

    if SHOT:
        os.makedirs(SHOT, exist_ok=True)
        pg.evaluate("scrollTo({ top: 0, behavior: 'instant' })")
        pg.screenshot(path=os.path.join(SHOT, (pad.strip('/').replace('/', '_') or 'home') + f'-{breedte}.png'), full_page=False)

    # console + requests
    afgebroken = [x for x in mislukt if 'ERR_ABORTED' in x and re.search(r'\.(webp|jpe?g|png|mp4)', x)]
    mislukt = [x for x in mislukt if x not in afgebroken]
    if afgebroken:
        m('INFO', f'{len(afgebroken)} afbeelding/video-requests afgebroken door snel scrollen (lazy, geen fout)')
    eigen = [x for x in mislukt if eigen_host(x.split(' ', 1)[-1] if x[0].isdigit() else x)]
    derden = [x for x in mislukt if x not in eigen]
    for x in sorted(set(eigen)):
        if LOKAAL and '/api/track' in x:
            continue   # lokaal gemockt; sendBeacon wordt bij het verlaten afgebroken
        m('FOUT', f'request: {x}')
    for x in sorted(set(derden)):
        if not re.search(r'google-analytics|analytics\.google\.com|googletagmanager|doubleclick|googleads|google\.com/(pagead|ccm)|facebook|mews\.com/.*(track|analytics)', x):
            m('LET OP', f'request derden: {x[:160]}')
    for c in sorted(set(console)):
        if not re.search(r'googletagmanager|gtag|google-analytics|doubleclick', c):
            m('FOUT', f'console: {c[:200]}')
    ctx.close()


def qa_scratchcard(br):
    pad = '/hotel-venray-v2'
    ctx = nieuwe_context(br, 390, cookie_ok=True, popup_uit=False)
    pg = ctx.new_page()
    pg.goto(BASIS + pad, wait_until='domcontentloaded')
    pg.wait_for_timeout(1500)
    pg.evaluate("scrollTo({ top: document.documentElement.scrollHeight * 0.5, behavior: 'instant' })")
    pg.wait_for_timeout(1500)
    ov = pg.locator('#scOverlay')
    if not ov.count() or not ov.is_visible():
        meld(pad, 'FOUT', 390, 'scratchcard-pop-up verschijnt niet na 50% scroll')
        ctx.close()
        return
    privacy = pg.evaluate("() => [...document.querySelectorAll('#scOverlay a')].map(a => a.href)")
    for h in privacy:
        LINKS_EXTRA.setdefault(h, set()).add(pad)
    sl = pg.locator('#scClose')
    sl.click()
    pg.wait_for_timeout(600)
    dicht = ov.evaluate("o => !o.classList.contains('is-open') && (+getComputedStyle(o).opacity < 0.05 || !o.offsetParent) && getComputedStyle(o).pointerEvents === 'none' || !o.isConnected")
    vast, s = body_vast(pg)
    meld(pad, 'OK' if dicht and not vast else 'FOUT', 390, f'scratchcard-pop-up verschijnt (50% scroll), kruisje sluit={dicht}, body-scroll hersteld={not vast}; links in pop-up: {privacy}')
    ctx.close()


def check_links(br, linkset):
    req = br.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36').request
    for href, paginas in sorted(linkset.items()):
        u = urllib.parse.urlsplit(href)
        if u.netloc == 'app.mews.com':
            if MEWS_CFG not in href:
                for p in paginas:
                    meld(p, 'FOUT', 0, f'Mews-link met andere configuratie: {href}')
            continue
        intern = eigen_host(href) or u.netloc == 'visit.asteria.nl'
        try:
            r = req.get(href, timeout=25000, max_redirects=5, fail_on_status_code=False)
            st = r.status
            # Pages heeft een terugval: een onbekend adres geeft 200 met de kale index ("Welkom bij Asteria") = soft-404
            if intern and st == 200 and 'text/html' in r.headers.get('content-type', '') and SOFT404 in r.text():
                st = 'soft-404 (Pages-terugval index.html)'
        except Exception as e:   # noqa: BLE001
            st = f'fout {str(e)[:60]}'
        for p in sorted(paginas):
            if intern and st != 200:
                meld(p, 'FOUT', 0, f'interne link {st}: {href}')
            elif not intern and st in (404, 410):
                meld(p, 'FOUT', 0, f'externe link {st}: {href}')
            elif not intern and not isinstance(st, int):
                meld(p, 'LET OP', 0, f'externe link niet te controleren ({st}): {href}')
            elif not intern and st >= 400:
                meld(p, 'LET OP', 0, f'externe link {st} (bot-blokkade?): {href}')
    return len(linkset)


def main():
    srv = start_server() if LOKAAL else None
    linkset = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        for pad in PAGINAS:
            for b in BREEDTES:
                t0 = time.time()
                print(f'.. {pad} @ {b}', flush=True)
                try:
                    qa_pagina(br, pad, b, linkset)
                except Exception as e:   # noqa: BLE001
                    meld(pad, 'FOUT', b, f'QA-script afgebroken: {str(e)[:200]}')
                print(f'   {time.time() - t0:.0f} s', flush=True)
        if '/hotel-venray-v2' in PAGINAS and 390 in BREEDTES:
            qa_scratchcard(br)
        for h, ps in LINKS_EXTRA.items():
            linkset.setdefault(h, set()).update(ps)
        n = 0 if ZONDER_LINKS else check_links(br, linkset)
        br.close()
    if srv:
        srv.shutdown()
    fouten = 0
    print(f'\n==== QA-rapport {BASIS} ({len(PAGINAS)} pagina\'s, breedtes {BREEDTES}, {n} unieke http-links gecontroleerd) ====')
    for pad in PAGINAS:
        regels = rapport.get(pad, [])
        f = [r for r in regels if r[0] == 'FOUT']
        fouten += len(f)
        print(f'\n## {pad}  ({len(f)} fout, {sum(1 for r in regels if r[0] == "LET OP")} let op)')
        gezien = set()
        for niveau, b, tekst in sorted(regels, key=lambda r: ['FOUT', 'LET OP', 'OK', 'INFO'].index(r[0])):
            sleutel = (niveau, tekst)
            if sleutel in gezien:
                continue
            gezien.add(sleutel)
            br_ = sorted({x[1] for x in regels if (x[0], x[2]) == sleutel})
            print(f'  {niveau:6} [{"/".join(str(x) if x else "links" for x in br_)}] {tekst}')
    print(f'\nTotaal: {fouten} fouten')
    if JSON_UIT:
        json.dump({p: [list(r) for r in v] for p, v in rapport.items()}, open(JSON_UIT, 'w'), ensure_ascii=False, indent=1)
    sys.exit(1 if fouten else 0)


if __name__ == '__main__':
    main()
