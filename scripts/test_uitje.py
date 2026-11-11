#!/usr/bin/env python3
"""Generieke test van een uitjepagina (uitje.template.html), naar model van scripts/test_adslander.py.

Gebruik:
  python3 -m http.server 8792 --directory .            (in de repo-root)
  python3 scripts/test_uitje.py [URL] [--schermafdruk qa/uitje] [--breedtes 1440,390]
  standaard-URL: http://localhost:8792/zooparc-overloon-v2.html

Het gegevensbestand volgt uit de URL: <slug>-v2.html -> translations/uitje-<slug>-nl.json (met translations/uitje-labels-nl.json
eronder, zoals build_uitje); <slug>-v2-de.html / <slug>-v2-en.html -> uitje-<slug>-de/en.json met uitje-labels-de/en.json en
content/uitje-kamers-de/en.json. Taal van de pagina = html lang, Mews-taal, kop/voet, kalenderlabels en hreflang worden per taal getoetst.
Titel begint met "Hotel bij" (nl), "Hotel " (de) of "Hotel near" (en), of met `test-titel-begin` uit het uitje-JSON. Daaruit komen de verwachtingen: aantal kamers (0 = geen kamerslider-checks), kaartpunten (genummerd,
met url = link, met pop = pop-up), meer-kaarten (met url = gewone link, zonder = pop-up), FAQ's, verhaalrijen, dagmomenten, en of er
een arrangementkaart is (arr-bron: blok ut-arr i.p.v. ut-kamers, boekknop met actiecode die de prijskalender opent).

Mews en de /api/*-functies worden gemockt (Mews-script = stub die elke API-aanroep logt in window.__mews; /api/arr-kalender geeft
een paar beschikbare dagen, elke andere /api geeft 404 en wordt geteld). Exit 0 = alles groen; 'let op' = waarschuwing, geen fout.
Met --schermafdruk <map>: per breedte elk blok als <map>/<slug>-<breedte>-<blok>.png, de hele pagina als <slug>-<breedte>-volledig.png
en op een arrangementpagina de geopende kalender als <slug>-<breedte>-kalender.png. DE/EN: <slug>-de-<breedte>-... resp. <slug>-en-<breedte>-...
"""
import asyncio, calendar, datetime, json, os, re, sys
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
URL = next((a for a in args if a.startswith('http')), 'http://localhost:8792/zooparc-overloon-v2.html')
SHOT = args[args.index('--schermafdruk') + 1] if '--schermafdruk' in args else None
BREEDTES = [int(x) for x in (args[args.index('--breedtes') + 1] if '--breedtes' in args else '1440,390').split(',')]

m = re.search(r'/([a-z0-9-]+)-v2(?:-(de|en))?\.html(?:[?#].*)?$', URL)
if not m:
    sys.exit(f'URL moet eindigen op <slug>-v2.html, <slug>-v2-de.html of <slug>-v2-en.html: {URL}')
SLUG, TAAL = m.group(1), m.group(2) or 'nl'
NAAM = SLUG if TAAL == 'nl' else f'{SLUG}-{TAAL}'   # voorvoegsel van de schermafdrukken
JSON_UITJE = os.path.join(BASE, 'translations', f'uitje-{SLUG}-{TAAL}.json')
if not os.path.exists(JSON_UITJE):
    sys.exit(f'gegevensbestand ontbreekt: {os.path.relpath(JSON_UITJE, BASE)}')
D = json.load(open(os.path.join(BASE, 'translations', f'uitje-labels-{TAAL}.json'), encoding='utf-8'))
D.update(json.load(open(JSON_UITJE, encoding='utf-8')))
MEWS_TAAL = D.get('mews-taal', 'nl-NL')

# verwachtingen per taal: titelbegin, kop/voet-labels (al_kop_voet), prijskalender (AL_KAL_LABELS + arrangement-kalender.js)
TITEL_BEGIN = D.get('test-titel-begin') or {'nl': 'Hotel bij', 'de': 'Hotel ', 'en': 'Hotel near'}[TAAL]   # test-titel-begin: bv. Thermaalbad Arcen
KOPVOET = {'nl': ('Kamers & suites', 'Privacyverklaring'), 'de': ('Zimmer & Suiten', 'Datenschutz'),
           'en': ('Rooms & suites', 'Privacy statement')}[TAAL]
KAL_TAAL = {
    'nl': {'wd': 'MaDiWo', 'kop': 'Kies je', 'btn': 'Bekijk kamers en prijzen', 'code': 'Actiecode',
           'maanden': ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']},
    'de': {'wd': 'MoDiMi', 'kop': 'Wählen Sie', 'btn': 'Zimmer und Preise ansehen', 'code': 'Aktionscode',
           'maanden': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']},
    'en': {'wd': 'MoTuWe', 'kop': 'Choose your', 'btn': 'View rooms and prices', 'code': 'Promo code',
           'maanden': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']},
}[TAAL]
# hreflang zoals build.py ut_hreflang: talen waarvan het uitje-JSON bestaat, pas vanaf twee; x-default = NL
HREF_TALEN = [t for t in ('nl', 'de', 'en') if os.path.exists(os.path.join(BASE, 'translations', f'uitje-{SLUG}-{t}.json'))]
HREFLANG = {}
if len(HREF_TALEN) >= 2:
    HREFLANG = {t: f'https://visit.asteria.nl/{SLUG}-v2' + ('' if t == 'nl' else f'-{t}') for t in HREF_TALEN}
    if 'nl' in HREFLANG:
        HREFLANG['x-default'] = HREFLANG['nl']

STD_CFG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
KAMERBRON = json.load(open(os.path.join(BASE, 'content', f'uitje-kamers-{TAAL}.json'), encoding='utf-8'))['kamer']
KAMER_IDS = [v['kamer'] for v in KAMERBRON.values()]


def genummerd(voorvoegsel, achtervoegsel, maxi):
    """Gevulde genummerde slots zoals build.py al_lijst: doorlopend vanaf 1, leeg veld telt niet."""
    uit, i = [], 1
    while f'{voorvoegsel}{i}{achtervoegsel}' in D:
        if D[f'{voorvoegsel}{i}{achtervoegsel}']:
            uit.append(i)
        i += 1
    return uit[:maxi]


# verwachtingen uit het gegevensbestand
KAMERS = D.get('kamers') or []
ARR = bool(D.get('arr-bron'))
if ARR:
    A = json.load(open(os.path.join(BASE, 'translations', D['arr-bron'] + '-nl.json'), encoding='utf-8'))
    VOUCHER = A['VOUCHER']
    ARR_CFG = A.get('MEWS_CONFIG') or STD_CFG
    KAL = json.load(open(os.path.join(BASE, 'content', 'arr-kalender.json'), encoding='utf-8'))
    ARR_KALENDER = A.get('ARR_KALENDER', True) is not False and VOUCHER in KAL
V_RIJEN = genummerd('v', '-kop', 3)
MOMENTEN = genummerd('m', '-naam', 4) if D.get('dag-kop') else []
G_KAARTEN = genummerd('g', '-kop', 6)
FAQ = genummerd('f', '-v', 6)
MEER = [i for i in genummerd('meer', '-naam', 3)] if D.get('meer-kop') else []
PUNTEN = (D.get('kaart') or {}).get('punten', []) if D.get('kaart-kop') else []
NR_PUNTEN = [p for p in PUNTEN if not p.get('hoofd')]

VOLGORDE = (['ut-hero', 'ut-oog', 'ut-verhaal'] + (['ut-tip'] if D.get('tip') else []) + (['ut-prak'] if G_KAARTEN else [])
            + (['ut-dag'] if MOMENTEN else []) + (['ut-arr'] if ARR else []) + (['ut-kamers'] if KAMERS else [])
            + (['ut-kaart'] if PUNTEN else []) + ['ut-faq', 'rta'] + (['ut-meer'] if MEER else []) + ['ut-slot'])

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[],code:''};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){if(m==='setVoucherCode')log.code=String(arguments[0]==null?'':arguments[0]);
log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""


def kal_antwoord(url):
    """Een paar beschikbare dagen per deelaanvraag (zoals test_adslander.py)."""
    m = re.search(r'code=([A-Z0-9]+)&maand=(\d{4})-(\d{2})&deel=(\d)', url)
    code, j, mnd, deel = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    laatste = calendar.monthrange(j, mnd)[1]
    van, tot = (deel - 1) * 8 + 1, laatste if deel == 4 else min(deel * 8, laatste)
    dagen = []
    for g in range(van, tot + 1):
        dt = datetime.date(j, mnd, g)
        dagen.append({'datum': dt.isoformat(), 'beschikbaar': True, 'zondag': dt.weekday() == 6, 'aankomst_mag': True,
                      'prijzen': {k: {'prijs_cent': 24900 + 1000 * (g % 3), 'berekend': False} for k in KAMER_IDS}})
    return {'ok': True, 'code': code, 'dagen': dagen}


async def mocks(ctx, log):
    async def api(route):
        u = route.request.url
        if '/api/track' in u:   # analytics-d1.js (D1-events) mag wel
            await route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
            return
        log['api'].append(u)
        if '/api/arr-kalender' in u:
            await route.fulfill(status=200, content_type='application/json', body=json.dumps(kal_antwoord(u)))
            return
        await route.fulfill(status=404, content_type='application/json', body='{"ok":false}')
    await ctx.route(re.compile(r'.*/api/.*'), api)
    await ctx.route(re.compile(r'https://app\.mews\.com/distributor/distributor\.min\.js.*'),
                    lambda r: r.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB))
    await ctx.route(re.compile(r'https://www\.googletagmanager\.com/.*'), lambda r: r.fulfill(status=200, body=''))


async def scroll_alles(pg):
    h = await pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, h, 500):
        await pg.evaluate(f'window.scrollTo(0,{y})')
        await pg.wait_for_timeout(60)
    await pg.wait_for_timeout(800)
    await pg.evaluate('window.scrollTo(0,0)')
    await pg.wait_for_timeout(300)


async def mews_calls(pg):
    return [c for m in await pg.evaluate('window.__mews || []') for c in m['calls']]


async def mews_code(pg, cfg):
    """laatst gezette actiecode in de (gemockte) widget van deze config; '' = gewist of nooit gezet"""
    return next((m['code'] for m in await pg.evaluate('window.__mews || []') if m['cfg'] == cfg), None)


async def kal_open(pg):
    return await pg.evaluate("()=>{const k=document.getElementById('ar-kal');return !!(k&&k.open)}")


async def test_breedte(p, w, fouten, waarschuwingen):
    b = await p.chromium.launch()
    mobiel = w < 768
    ctx = await b.new_context(viewport={'width': w, 'height': 844 if mobiel else 900}, is_mobile=mobiel, has_touch=mobiel)
    log = {'api': [], 'console': []}
    await mocks(ctx, log)
    pg = await ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: log['console'].append(str(e)))
    await pg.goto(URL, wait_until='networkidle')
    await pg.evaluate("try{localStorage.setItem('cookie-consent','1')}catch(e){}; var c=document.getElementById('cookieBanner'); if(c) c.classList.remove('show')")

    def ok(cond, naam):
        print(('  ok   ' if cond else '  FOUT ') + f'[{w}] {naam}')
        if not cond:
            fouten.append(f'[{w}] {naam}')

    def let_op(cond, naam):
        print(('  ok   ' if cond else '  let op ') + f'[{w}] {naam}')
        if not cond:
            waarschuwingen.append(f'[{w}] {naam}')

    # kop en meta
    titel = await pg.title()
    ok(titel.startswith(TITEL_BEGIN), f'<title> begint met "{TITEL_BEGIN}" ({titel})')
    ok(await pg.get_attribute('meta[name=robots]', 'content') == 'noindex, follow', 'robots = noindex, follow')
    ok(await pg.get_attribute('html', 'lang') == D['html-taal'] == TAAL, f'html lang {TAAL}')
    ok(await pg.get_attribute('html', 'data-mews-taal') == MEWS_TAAL, f'data-mews-taal {MEWS_TAAL}')
    hl = await pg.eval_on_selector_all('head link[rel="alternate"][hreflang]', 'els => els.map(e => [e.getAttribute("hreflang"), e.getAttribute("href")])')
    ok(dict(hl) == HREFLANG and len(hl) == len(HREFLANG), f'hreflang in de head: {sorted(HREFLANG) or "geen (een taal)"} ({hl})')
    kv = await pg.evaluate("() => [document.querySelector('header.top-stack').textContent, document.querySelector('footer.footer').textContent]")
    ok(KOPVOET[0] in kv[0] and KOPVOET[1] in kv[1], f'kop/voet in het {TAAL} ({KOPVOET[0]!r} in de kop, {KOPVOET[1]!r} in de voet)')
    html = await pg.content()
    ok(not re.search(r'\{\{[A-Za-z_0-9-]+\}\}', html), 'geen open {{velden}}')
    ok('—' not in html, 'geen em-dash')

    # blokvolgorde
    comps = await pg.eval_on_selector_all('main [data-component]', 'els => els.map(e => e.getAttribute("data-component"))')
    ok(comps == VOLGORDE, f'blokvolgorde {" > ".join(VOLGORDE)} ({len(comps)} gevonden: {comps if comps != VOLGORDE else "gelijk"})')

    # oogopslag overlapt de hero
    ov = await pg.evaluate("""() => { var h=document.querySelector('.ut-hero').getBoundingClientRect(), o=document.querySelector('.ut-oog__paneel').getBoundingClientRect(); return Math.round(h.bottom - o.top) }""")
    ok(ov == (64 if mobiel else 120), f'oogopslagpaneel hangt {64 if mobiel else 120} px over de hero ({ov})')

    # geen prijs buiten de kalenderdialoog
    ok(await pg.locator('.kk-prijs, [data-kamer-vanaf], [data-arr-vanaf], .al-ak__prijs, .al-ak__prijsblok').count() == 0, 'geen prijselementen')
    ok(await pg.locator('script[src*="arr-vanaf"]').count() == 0, 'arr-vanaf.js niet geladen')

    # verhaal + Lees meer (alleen bij meer dan een rij)
    ok(await pg.locator('.ut-verhaal .ut-it').count() == len(V_RIJEN), f'{len(V_RIJEN)} verhaalrijen')
    if len(V_RIJEN) > 1:
        knop = pg.locator('.ut-meerbalk__knop')
        ok(await knop.is_visible(), 'Lees meer-balk zichtbaar')
        ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 1, 'verhaal rij 2-3 ingeklapt')
        await knop.scroll_into_view_if_needed(); await knop.click(); await pg.wait_for_timeout(300)
        ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 0 and (await knop.inner_text()).strip() == D['l-leesminder'], 'Lees meer opent (label Lees minder)')
        await knop.click(); await pg.wait_for_timeout(500)
        ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 1 and (await knop.inner_text()).strip() == D['l-leesmeer'], 'Lees minder sluit weer')
    else:
        ok(await pg.locator('.ut-meerbalk__knop').count() == 0, 'geen Lees meer bij een verhaalrij')

    # dagverloop: een open + fotowissel naar het laatste moment
    if MOMENTEN:
        ok(await pg.locator('.ut-moment').count() == len(MOMENTEN), f'{len(MOMENTEN)} dagmomenten')
        ok(await pg.locator('.ut-moment.is-aan').count() == 1, 'dagverloop: een moment open')
        if len(MOMENTEN) > 1:
            nr = str(MOMENTEN[-1])
            mk = pg.locator(f'.ut-moment[data-moment="{nr}"] .ut-moment__kies')
            await mk.scroll_into_view_if_needed(); await mk.click(); await pg.wait_for_timeout(400)
            aan = await pg.eval_on_selector_all('.ut-moment.is-aan', 'els => els.map(e => e.dataset.moment)')
            beeld = await pg.eval_on_selector_all('.ut-dag__beeld.is-aan', 'els => els.map(e => e.dataset.beeld)')
            ok(aan == [nr] and beeld == [nr], f'moment {nr} open en foto {nr} zichtbaar ({aan}, {beeld})')
            ok(await mk.get_attribute('aria-expanded') == 'true', 'aria-expanded volgt het moment')

    # kamerslider (alleen bij een gevulde kamers-lijst)
    if KAMERS:
        n = len(KAMERS)
        echt = await pg.locator('#kamers .kk-kaart:not([data-kloon])').count()
        klonen = await pg.locator('#kamers .kk-kaart[data-kloon]:not([hidden])').count()
        ok(echt == n, f'{n} kamerkaarten ({echt})')
        ok(klonen == 2 * echt, f'lus: {2 * echt} klonen ({klonen})')
        teller = pg.locator('#kamers .kk-teller')
        await teller.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
        t0 = (await teller.inner_text()).strip()
        await pg.locator('#kamers .kk-pijl[data-stap="1"]').click(); await pg.wait_for_timeout(900)
        t1 = (await teller.inner_text()).strip()
        await pg.locator('#kamers .kk-pijl[data-stap="-1"]').click(); await pg.wait_for_timeout(900)
        await pg.locator('#kamers .kk-pijl[data-stap="-1"]').click(); await pg.wait_for_timeout(900)
        t2 = (await teller.inner_text()).strip()
        ok(t0 == f'1/{echt}' and t1 == f'2/{echt}' and t2 == f'{echt}/{echt}', f'teller 1 -> 2 -> terug rond naar {echt} ({t0}, {t1}, {t2})')
    else:
        ok(await pg.locator('#kamers, .kk-kaart, #lp-pop-kamer, #al-kamerdata').count() == 0, 'geen kamerslider, kamer-pop-up of kamerdata')

    # Mews-links: config + Mews-taal; actiecode alleen op de arrangementknop
    hrefs = await pg.eval_on_selector_all('a.mews-open', 'els => els.map(e => [e.getAttribute("href"), e.getAttribute("data-voucher") || "", e.className])')
    ok(hrefs and all(f'language={MEWS_TAAL}' in h for h, _, _ in hrefs), f'alle {len(hrefs)} boekknoppen in {MEWS_TAAL}')
    ok(all((ARR_CFG if (ARR and v) else STD_CFG) in h for h, v, _ in hrefs), 'boekknoppen met de juiste Mews-config')
    met_code = await pg.eval_on_selector_all('[href*="mewsVoucherCode"], [data-voucher]', 'els => els.map(e => e.className)')
    if ARR:
        ok(met_code == ['btn btn-primary al-btn mews-open ut-arr__knop'], f'mewsVoucherCode/data-voucher alleen op de arrangementknop ({met_code})')
        ak = pg.locator('.ut-arr__knop')
        ok(await ak.get_attribute('data-voucher') == VOUCHER and f'mewsVoucherCode={VOUCHER}' in (await ak.get_attribute('href'))
           and f'distributor/{ARR_CFG}' in (await ak.get_attribute('href')), f'arrangementknop: data-voucher {VOUCHER} en config {ARR_CFG[:8]}')
    else:
        ok(not met_code and 'mewsVoucherCode' not in html, 'geen actiecode op de pagina')
    ok('bee2f902' not in html, 'geen oude config')
    if KAMERS:
        kids = {v['kamer'] for v in KAMERBRON.values()}
        kamerknop = await pg.eval_on_selector_all('#kamers .kk-kaart a.mews-open', 'els => els.map(e => [e.getAttribute("href"), e.getAttribute("data-room")])')
        ok(kamerknop and all(r in kids and f'mewsRoom={r}' in h and 'mewsRoute=rooms' in h for h, r in kamerknop), 'kamerknoppen: juiste kamer-id + mewsRoute=rooms')

        # kamer-pop-up
        info = pg.locator('#kamers .kk-kaart:not([data-kloon]) a.btn-secondary[data-kamer]').first
        await info.scroll_into_view_if_needed(); await info.click(); await pg.wait_for_timeout(600)
        if mobiel:
            zicht = await pg.locator('[data-pop-dialog]:not([hidden]) .al-pop__naam').count() == 1
            naam = (await pg.locator('#al-pop-naam').inner_text()).strip() if zicht else ''
            ok(zicht and naam, f'kamer-pop-up (telefoonsheet) open: {naam}')
        else:
            open_ = await pg.evaluate("document.getElementById('lp-pop-kamer').open")
            naam = (await pg.locator('#lp-pop-kamer-naam').inner_text()).strip()
            boek = await pg.get_attribute('#lp-pop-kamer .lp-pop__boek', 'href')
            ok(open_ and naam and 'mewsRoom=' in boek and f'language={MEWS_TAAL}' in boek, f'kamer-pop-up open: {naam}, boekknop met kamer')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # kaart: hotel + punten; genummerde punten = link (url) of pop-up (pop)
    if PUNTEN:
        kaart = pg.locator('.ut-kaart__beeld')
        await kaart.scroll_into_view_if_needed(); await pg.wait_for_timeout(1500)
        ok(await pg.locator('.ut-kaart__beeld.is-interactief').count() == 1, 'kaart interactief (vangnetfoto weg)')
        ok(await pg.locator('.ut-kaart .gk-hotel img').count() == 1, 'hotelvignet op de kaart')
        n_hoofd = sum(1 for q in PUNTEN if q.get('hoofd'))
        n_pop = sum(1 for q in NR_PUNTEN if q.get('pop') and not q.get('url'))
        urls = [q['url'] for q in NR_PUNTEN if q.get('url')]
        ok(await pg.locator('.ut-kaart .gk-punt').count() == len(PUNTEN) and await pg.locator('.ut-kaart .gk-punt--hoofd').count() == n_hoofd
           and await pg.locator('.ut-kaart .gk-punt--nr').count() == len(NR_PUNTEN),
           f'kaart: {len(PUNTEN)} punten ({n_hoofd} speld, {len(NR_PUNTEN)} genummerd)')
        ok(await pg.locator('.ut-kaart a.gk-punt[data-pop^="uitje:"]').count() == n_pop, f'kaart: {n_pop} punten met pop-up')
        kaart_hrefs = await pg.eval_on_selector_all('.ut-kaart a.gk-punt:not([data-pop])', 'els => els.map(e => e.getAttribute("href"))')
        ok(sorted(kaart_hrefs) == sorted(urls), f'kaart: {len(urls)} punten als gewone link ({kaart_hrefs})')
        s0 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
        await pg.locator('.ut-kaart .gk-knop').first.click(); await pg.wait_for_timeout(700)
        s1 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
        ok(s0 and s1 and s1 > s0 * 1.2, f'inzoomen werkt ({s0} -> {s1})')
        await pg.locator('.ut-kaart .gk-knop').nth(2).click(); await pg.wait_for_timeout(700)
        if n_pop:
            await pg.locator('.ut-kaart a.gk-punt[data-pop] .gk-punt__nr').first.click(); await pg.wait_for_timeout(500)
            pnaam = (await pg.locator('#al-pop-naam').inner_text()).strip() if await pg.locator('[data-pop-dialog]:not([hidden])').count() else ''
            ok(bool(pnaam), f'eerste kaartknop met pop opent de uitje-pop-up ({pnaam})')
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # meer-kaarten: met url = gewone link, zonder = pop-up met naam en Route plannen
    if MEER:
        kaarten = pg.locator('.ut-meer .ut-uk')
        ok(await kaarten.count() == len(MEER), f'{len(MEER)} meer-kaarten')
        goed, links_goed = True, True
        for j, i in enumerate(MEER):
            k = kaarten.nth(j)
            url = D.get(f'meer{i}-url', '')
            if url:
                links_goed = links_goed and await k.get_attribute('href') == url and await k.get_attribute('data-pop') is None
                continue
            await k.scroll_into_view_if_needed(); await k.click(); await pg.wait_for_timeout(400)
            n = (await pg.locator('#al-pop-naam').inner_text()).strip() if await pg.locator('[data-pop-dialog]:not([hidden])').count() else ''
            route = await pg.locator('[data-pop-dialog] .al-pop__boek').get_attribute('href') if n else ''
            goed = goed and bool(n) and 'google.com/maps' in (route or '')
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        ok(goed, 'meer-kaarten zonder url openen de pop-up met naam en Route plannen')
        ok(links_goed, 'meer-kaarten met url zijn een gewone link (href, geen pop-up)')

    # FAQ en JSON-LD
    ld = json.loads(await pg.eval_on_selector('script[type="application/ld+json"]', 'e => e.textContent'))
    vragen = await pg.eval_on_selector_all('.ut-faq .as-accordeon__item', 'els => els.map(e => [e.querySelector("summary").textContent.trim(), e.querySelector(".as-accordeon__paneel").textContent.trim()])')
    ld_paren = [[q['name'], q['acceptedAnswer']['text']] for q in ld['mainEntity']]
    ok(ld['@type'] == 'FAQPage' and ld_paren == vragen and len(vragen) == len(FAQ), f'FAQPage JSON-LD = zichtbare tekst ({len(vragen)} van {len(FAQ)} vragen)')
    ok(await pg.locator('.ut-faq details[open]').count() == 1, 'eerste vraag open')
    ok(await pg.locator('.ut-faq [role="tablist"]').count() == 0, 'geen tabs')

    # arrangementkaart: knop opent de prijskalender (taal van de pagina), tekstlink = Mews zonder code
    if ARR:
        ok(not log['api'], f'geen /api-aanroepen voor de klik ({log["api"][:3]})')
        ok((await pg.locator('.ut-arr__knop').inner_text()).strip() == D['arr-knop'], f'arrangementknop: {D["arr-knop"]!r}')
        if D.get('arr-kamerlink'):
            ok((await pg.locator('.ut-arr__link.mews-open').inner_text()).strip() == D['arr-kamerlink'], f'kamerlink: {D["arr-kamerlink"]!r}')
        ok(await pg.locator('.ut-arr .ut-arr__vinkjes li').count() >= 1, 'arrangementkaart heeft vinkjes')
        ok('€' not in await pg.locator('.ut-arr').inner_text(), 'geen prijs op de arrangementkaart')
        ak = pg.locator('.ut-arr__knop')
        await ak.scroll_into_view_if_needed(); await ak.click(); await pg.wait_for_timeout(1200)
        if ARR_KALENDER:
            kal = await pg.evaluate("""()=>{const k=document.getElementById('ar-kal');return k&&k.open?{code:k.dataset.code,
              prijzen:k.querySelectorAll('.ark-d .t.p').length,kop:k.querySelector('.ark-kop').textContent,wd:k.querySelector('.ark-wdag')?k.querySelector('.ark-wdag').textContent:'',
              btn:k.querySelector('.ark-btn').textContent,code_regel:k.querySelector('.ark-code').textContent,
              maand:k.querySelector('.ark-naam')?k.querySelector('.ark-naam').textContent:''}:null}""")
            ok(kal and kal['code'] == VOUCHER and kal['prijzen'] > 5, f'prijskalender {VOUCHER} open met prijzen ' + json.dumps(kal, ensure_ascii=False))
            ok(kal and kal['wd'].startswith(KAL_TAAL['wd']) and kal['kop'].startswith(KAL_TAAL['kop']) and kal['btn'] == KAL_TAAL['btn']
               and kal['code_regel'].startswith(KAL_TAAL['code']) and kal['maand'].split(' ')[0] in KAL_TAAL['maanden'],
               f'kalender in het {TAAL} (weekdagen, maand, kop, knop, code)')
            ok(log['api'] and all('/api/arr-kalender' in u and f'code={VOUCHER}' in u for u in log['api']), f'na de klik alleen /api/arr-kalender ({len(log["api"])} aanroepen)')
            cellen = pg.locator('#ar-kal .ark-d.kan')
            await cellen.nth(3).click(); await pg.wait_for_timeout(100)
            await pg.locator('#ar-kal .ark-d.kan').nth(4).click(); await pg.wait_for_timeout(100)
            await pg.click('#ar-kal .ark-btn'); await pg.wait_for_timeout(800)
            calls = await mews_calls(pg)
            ok(['setVoucherCode', VOUCHER] in calls and ['setLanguageCode', MEWS_TAAL] in calls and any(c[0] == 'setStartDate' for c in calls)
               and ['open'] in calls, f'kalender -> Mews met code, datums en {MEWS_TAAL}')
        else:
            calls = await mews_calls(pg)
            ok(not await kal_open(pg) and ['setVoucherCode', VOUCHER] in calls and ['open'] in calls, 'zonder kalender: knop opent Mews direct met de code')
        ok(await mews_code(pg, ARR_CFG) == VOUCHER, f'arrangementknop zet de code {VOUCHER} in de widget ({await mews_code(pg, ARR_CFG)!r})')
        voor = len(await mews_calls(pg))
        kl = pg.locator('.ut-arr__link.mews-open')
        if D.get('arr-kamerlink'):
            ok(await kl.count() == 1 and (await kl.get_attribute('href')).endswith(f'?language={MEWS_TAAL}') and await kl.get_attribute('data-voucher') is None,
               'tekstlink "liever alleen een kamer": Mews zonder code')
            await kl.scroll_into_view_if_needed(); await kl.click(); await pg.wait_for_timeout(800)
            nieuw = (await mews_calls(pg))[voor:]
            ok(not await kal_open(pg) and ['open'] in nieuw and not any(c[0] == 'setVoucherCode' and c[1:] != [''] for c in nieuw),
               f'tekstlink opent Mews zonder code en zonder kalender ({nieuw})')
            ok(await mews_code(pg, STD_CFG) == '', f'na arrangement boeken -> kamerlink is de code in de widget gewist ({await mews_code(pg, STD_CFG)!r})')
        else:
            ok(await kl.count() == 0, 'geen kamerlink (arr-kamerlink leeg)')
        if D.get('arr-pagina-url') and D.get('arr-paginalink'):
            ok(await pg.locator(f'.ut-arr__link[href="{D["arr-pagina-url"]}"]').count() == 1, f'tekstlink naar {D["arr-pagina-url"]}')

    # Mews klik (boekknop slot) opent de widget in de Mews-taal, zonder kalender
    slot = pg.locator('.ut-slot a.mews-open')
    ok(await slot.count() == 1 and await pg.locator('.ut-slot .btn').count() == 1, 'slot: precies een boekknop')
    voor = len(await mews_calls(pg))
    await slot.scroll_into_view_if_needed(); await slot.click(); await pg.wait_for_timeout(1200)
    mews = await pg.evaluate('window.__mews || []')
    ok(any(m['taal'] == MEWS_TAAL and any(c[0] == 'open' for c in m['calls']) for m in mews), f'Mews-widget opent in {MEWS_TAAL}')
    nieuw = (await mews_calls(pg))[voor:]
    ok(not await kal_open(pg) and not any(c[0] == 'setVoucherCode' and c[1:] != [''] for c in nieuw), 'slotknop: geen kalender en geen code')
    ok(await mews_code(pg, STD_CFG) in ('', None), f'slotknop: code in de widget leeg ({await mews_code(pg, STD_CFG)!r})')

    # overloop en console
    breed = await pg.evaluate('document.documentElement.scrollWidth')
    ok(breed <= w, f'geen horizontale overloop ({breed} <= {w})')
    if not ARR:
        ok(not log['api'], f'geen /api-aanroepen ({log["api"][:3]})')
    else:
        ok(all('/api/arr-kalender' in u for u in log['api']), 'alleen /api/arr-kalender aangeroepen')
    ok(not log['console'], f'geen consolefouten ({log["console"][:3]})')
    await b.close()


async def schermafdrukken(p, w, map_):
    b = await p.chromium.launch()
    mobiel = w < 768
    ctx = await b.new_context(viewport={'width': w, 'height': 844 if mobiel else 900}, is_mobile=mobiel, has_touch=mobiel)
    await mocks(ctx, {'api': [], 'console': []})
    pg = await ctx.new_page()
    await pg.goto(URL, wait_until='networkidle')
    await pg.evaluate("try{localStorage.setItem('cookie-consent','1')}catch(e){}; var c=document.getElementById('cookieBanner'); if(c) c.classList.remove('show')")
    await scroll_alles(pg)
    await pg.add_style_tag(content='.mob-cta,.cookie-banner{display:none!important} .top-stack{position:relative!important}')
    await pg.wait_for_timeout(300)
    for comp in VOLGORDE:
        el = pg.locator(f'[data-component="{comp}"]')
        if await el.count():
            await el.screenshot(path=os.path.join(map_, f'{NAAM}-{w}-{comp[3:]}.png'))
    await pg.screenshot(path=os.path.join(map_, f'{NAAM}-{w}-volledig.png'), full_page=True)
    if ARR and ARR_KALENDER:
        ak = pg.locator('.ut-arr__knop')
        await ak.scroll_into_view_if_needed(); await ak.click(); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=os.path.join(map_, f'{NAAM}-{w}-kalender.png'))
    await b.close()


async def main():
    fouten, waarschuwingen = [], []
    print(f'{SLUG} [{TAAL}]: {os.path.relpath(JSON_UITJE, BASE)} | kamers {len(KAMERS)} | arrangement {"ja (" + VOUCHER + ")" if ARR else "nee"} | '
          f'verhaal {len(V_RIJEN)} | momenten {len(MOMENTEN)} | kaartpunten {len(PUNTEN)} ({len(NR_PUNTEN)} genummerd) | meer {len(MEER)} | faq {len(FAQ)}')
    async with async_playwright() as p:
        for w in BREEDTES:
            print(f'== {w} px')
            await test_breedte(p, w, fouten, waarschuwingen)
            if SHOT:
                os.makedirs(SHOT, exist_ok=True)
                await schermafdrukken(p, w, SHOT)
    if waarschuwingen:
        print('\nLet op (geen fout):\n  ' + '\n  '.join(waarschuwingen))
    if fouten:
        print('\nFOUT:\n  ' + '\n  '.join(fouten))
        sys.exit(1)
    print('\nAlles groen.')


asyncio.run(main())
