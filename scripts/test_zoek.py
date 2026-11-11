#!/usr/bin/env python3
"""Test van de zoekpagina "Hotel bij ..." (zoek.template.html), naar model van scripts/test_uitje.py.

Gebruik:
  python3 -m http.server 8797 --directory .            (in de repo-root)
  python3 scripts/test_zoek.py [URL] [--json translations/zoek-<slug>-<taal>.json] [--schermafdruk qa/zoek] [--naam de-arcen]
                               [--breedtes 1440,390]
  standaard: http://localhost:8797/hotel-thermalbad-arcen-de-v2.html met translations/zoek-hotel-thermalbad-arcen-de.json

Mews en de /api/*-functies worden gemockt (Mews-script = stub die elke aanroep logt in window.__mews; /api/arr-vanaf en
/api/arr-kalender geven testprijzen; elke andere /api wordt geteld en mag niet voorkomen, dus ook geen /api/kamer-vanaf).
Taal, blokvolgorde, rijtijd en kaartpunten komen uit de pagina-JSON, zodat dezelfde test voor elke pagina en taal werkt.
Exit 0 = alles groen. Met --schermafdruk <map>: per breedte elk blok als <map>/<naam>-<breedte>-<blok>.png en de hele
pagina als <map>/<naam>-<breedte>-pagina.png.
"""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
arg = lambda naam, std: args[args.index(naam) + 1] if naam in args else std
URL = next((a for a in args if a.startswith('http')), 'http://localhost:8797/hotel-thermalbad-arcen-de-v2.html')
JSON = arg('--json', 'translations/zoek-hotel-thermalbad-arcen-de.json')
SHOT = arg('--schermafdruk', None)
NAAM = arg('--naam', 'de-arcen')
BREEDTES = [int(x) for x in arg('--breedtes', '1440,390').split(',')]

D = json.load(open(os.path.join(BASE, JSON), encoding='utf-8'))
TAAL = re.search(r'-(nl|de|en)\.json$', JSON).group(1)
MEWS_TAAL = {'nl': 'nl-NL', 'de': 'de-DE', 'en': 'en-US'}[TAAL]
KAMERS = json.load(open(os.path.join(BASE, 'content', f'zoek-kamers-{TAAL}.json'), encoding='utf-8'))['kamer']
COMP = {'hero': 'zk-hero', 'oog': 'zk-oog', 'intro': 'zk-intro', 'kamers': 'zk-kamers', 'wellness': 'zk-well', 'arr': 'zk-arr',
        'ligging': 'zk-ligging', 'reviews': 'grv', 'faq': 'zk-faq', 'slot': 'zk-slot'}
BLOKKEN = ['hero'] + D['blokken']
VOLGORDE = [COMP[b] for b in BLOKKEN]
# rijtijd zoals in de eerste alinea: veld test-rijtijd in de pagina-JSON (terugval: Arcen, 23 minuten)
RIJTIJD = D.get('test-rijtijd') or {'de': '23 Minuten', 'nl': '23 minuten', 'en': '23 minutes'}[TAAL]
CFG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[]};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""


def kal_antwoord(url):
    import calendar, datetime
    m = re.search(r'code=([A-Z0-9]+)&maand=(\d{4})-(\d{2})&deel=(\d)', url)
    if not m:
        return {'ok': False}
    code, j, mnd, deel = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    laatste = calendar.monthrange(j, mnd)[1]
    van, tot = (deel - 1) * 8 + 1, laatste if deel == 4 else min(deel * 8, laatste)
    dagen = [{'datum': datetime.date(j, mnd, g).isoformat(), 'beschikbaar': True, 'zondag': datetime.date(j, mnd, g).weekday() == 6,
              'aankomst_mag': True, 'prijzen': {k: {'prijs_cent': 24900, 'berekend': False} for k in KAMERS}} for g in range(van, tot + 1)]
    return {'ok': True, 'code': code, 'dagen': dagen}


async def mocks(ctx, log):
    async def api(route):
        u = route.request.url
        if '/api/track' in u:
            body = {'ok': True}
        elif '/api/arr-vanaf' in u:
            body = {'ok': True, 'prijzen': {'WELLNESS2026': {'euro': 119}, 'NAJAAR2D': {'euro': 121}, 'WINTER27': {'euro': 299}, 'OORLOGSMUSEUM': {'euro': 131}}}
        elif '/api/arr-kalender' in u:
            body = kal_antwoord(u)
        else:
            log['api'].append(u)
            await route.fulfill(status=404, content_type='application/json', body='{"ok":false}')
            return
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(body))
    await ctx.route(re.compile(r'.*/api/.*'), api)
    await ctx.route(re.compile(r'https://app\.mews\.com/distributor/distributor\.min\.js.*'),
                    lambda r: r.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB))
    await ctx.route(re.compile(r'https://www\.googletagmanager\.com/.*'), lambda r: r.fulfill(status=200, body=''))


async def klik(pg, loc):
    """Pagina verticaal zo schuiven dat het element midden in beeld staat (geen horizontale rij verschuiven), laten uitrollen
    en klikken; lukt de gewone klik niet binnen 3 s (rij beweegt nog of de onderbalk ligt erover), dan een muisklik op het
    midden, zoals een bezoeker."""
    await loc.evaluate("e => { var r = e.getBoundingClientRect(); window.scrollBy(0, r.top + r.height / 2 - innerHeight / 2) }")
    await pg.wait_for_timeout(700)
    try:
        await loc.click(timeout=3000)
    except Exception:
        bb = await loc.bounding_box()
        await pg.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2)


async def scroll_alles(pg):
    h = await pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, h, 500):
        await pg.evaluate(f'window.scrollTo(0,{y})')
        await pg.wait_for_timeout(60)
    await pg.wait_for_timeout(1200)
    await pg.evaluate('window.scrollTo(0,0)')
    await pg.wait_for_timeout(300)


async def nieuwe_pagina(p, w, log):
    b = await p.chromium.launch()
    mobiel = w < 768
    ctx = await b.new_context(viewport={'width': w, 'height': 844 if mobiel else 900}, is_mobile=mobiel, has_touch=mobiel)
    await mocks(ctx, log)
    pg = await ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: log['console'].append(str(e)))
    await pg.goto(URL, wait_until='networkidle')
    await pg.evaluate("try{localStorage.setItem('cookie-consent','1')}catch(e){}; var c=document.getElementById('cookieBanner'); if(c) c.classList.remove('show')")
    return b, pg


async def test_breedte(p, w, fouten):
    mobiel = w < 768
    log = {'api': [], 'console': []}
    b, pg = await nieuwe_pagina(p, w, log)

    def ok(cond, naam):
        print(('  ok   ' if cond else '  FOUT ') + f'[{w}] {naam}')
        if not cond:
            fouten.append(f'[{w}] {naam}')

    # kop en meta
    ok(await pg.get_attribute('meta[name=robots]', 'content') == 'noindex, follow', 'robots = noindex, follow')
    ok(await pg.get_attribute('html', 'lang') == TAAL, f'html lang {TAAL}')
    ok(await pg.get_attribute('link[rel=canonical]', 'href') == D['canonical'], 'canonical = eigen adres')
    ok((await pg.title()) == D['titel'], f'title = {D["titel"]}')
    hl = await pg.eval_on_selector_all('link[rel=alternate][hreflang]', 'els => Object.fromEntries(els.map(e => [e.hreflang, e.href]))')
    ok(hl == (D.get('hreflang') or {}), f'hreflang = JSON ({", ".join(hl) or "geen"})')
    if D.get('hero-kop'):
        ok((await pg.inner_text('.zk-hero h1')).strip() == re.sub(r'<[^>]+>', '', D['hero-kop']), 'h1 = hero-kop')
    html = await pg.content()
    ok(not re.search(r'\{\{[A-Za-z_0-9-]+\}\}|<!-- ZK_', html), 'geen open {{velden}} of ZK-plekken')
    ok('—' not in html, 'geen em-dash')

    # blokvolgorde
    comps = await pg.eval_on_selector_all('main > [data-component]', 'els => els.map(e => e.getAttribute("data-component"))')
    ok(comps == VOLGORDE, f'blokken in de volgorde van de JSON ({", ".join(c[3:] for c in comps)})')

    # boekknop boven de vouw
    knop = await pg.evaluate("""() => { var k=document.querySelector('.zk-hero .al-btn.mews-open'), r=k.getBoundingClientRect();
      return {zicht: r.width > 0 && r.height > 0 && getComputedStyle(k).visibility !== 'hidden', onder: Math.round(r.bottom), vh: innerHeight} }""")
    ok(knop['zicht'] and knop['onder'] <= knop['vh'], f'boekknop boven de vouw (onderkant {knop["onder"]} <= {knop["vh"]})')

    # oogopslag: 120 px over de hero op het bureaublad, op de telefoon eronder
    if 'oog' in D['blokken']:
        ov = await pg.evaluate("""() => { var h=document.querySelector('.zk-hero').getBoundingClientRect(), o=document.querySelector('.zk-oog .ut-oog__paneel').getBoundingClientRect(); return Math.round(h.bottom - o.top) }""")
        if D['blokken'][0] == 'oog':
            ok(ov == 120 if not mobiel else ov <= 0, f'oogopslagpaneel {"onder de hero" if mobiel else "hangt 120 px over de hero"} ({ov})')
        tekst = await pg.evaluate("""() => { var h=document.querySelector('.zk-hero .al-hero__trust').getBoundingClientRect(), o=document.querySelector('.zk-oog .ut-oog__paneel').getBoundingClientRect(); return Math.round(o.top - h.bottom) }""")
        ok(tekst >= 0, f'zekerheden in de hero niet onder het paneel ({tekst} px ruimte)')

    # rijtijd in de eerste alinea
    p1 = await pg.evaluate("() => { var p=document.querySelector('.zk-intro__tekst p'); return p ? p.textContent : '' }")
    ok(RIJTIJD in p1, f'"{RIJTIJD}" in de eerste alinea')
    ok('Maasheseweg 80a' in p1, 'adres in de eerste alinea')

    # geen prijs in de kamers, geen kamer-vanaf-API
    ok(await pg.locator('.kk-prijs, [data-kamer-vanaf]').count() == 0, 'geen kk-prijs / data-kamer-vanaf in de DOM')

    # kamerslider: lus en teller
    echt = await pg.locator('#kamers .kk-kaart:not([data-kloon])').count()
    klonen = await pg.locator('#kamers .kk-kaart[data-kloon]:not([hidden])').count()
    ok(echt == len(D['kamers']), f'{len(D["kamers"])} kamerkaarten ({echt})')
    ok(klonen == 2 * echt, f'lus: {2 * echt} klonen ({klonen})')
    teller = pg.locator('#kamers .kk-teller')
    await teller.scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
    t0 = (await teller.inner_text()).strip()
    # klik() valt terug op een muisklik: Playwrights hit-check meldde op 390 px EN ten onrechte dat .kk-rij de klik onderschept
    await klik(pg, pg.locator('#kamers .kk-pijl[data-stap="1"]')); await pg.wait_for_timeout(900)
    t1 = (await teller.inner_text()).strip()
    ok(t0 == f'1/{echt}' and t1 == f'2/{echt}', f'teller 1 -> 2 ({t0}, {t1})')

    # Mews-links
    hrefs = await pg.eval_on_selector_all('a[href*="app.mews.com/distributor"]', 'els => els.map(e => e.getAttribute("href"))')
    ok(hrefs and all(f'language={MEWS_TAAL}' in h for h in hrefs), f'alle {len(hrefs)} Mews-links met language={MEWS_TAAL}')
    ok('bee2f902' not in html, 'geen oude Mews-config')
    kids = {v['kamer'] for v in KAMERS.values()}
    kamerknop = await pg.eval_on_selector_all('#kamers .kk-kaart a.mews-open', 'els => els.map(e => [e.getAttribute("href"), e.getAttribute("data-room")])')
    ok(kamerknop and all(CFG in h and r in kids and f'mewsRoom={r}' in h and 'mewsRoute=rooms' in h for h, r in kamerknop), 'kamerknoppen: juiste kamer-id + mewsRoute=rooms')

    # kamer-pop-up via de tekstlink Meer info
    info = pg.locator('#kamers .kk-kaart:not([data-kloon]) a.zk-info[data-kamer]').first
    await klik(pg, info); await pg.wait_for_timeout(600)
    if mobiel:
        zicht = await pg.locator('[data-pop-dialog]:not([hidden]) .al-pop__naam').count() == 1
        ok(zicht, 'kamer-pop-up (telefoonsheet) opent via Meer info')
    else:
        open_ = await pg.evaluate("document.getElementById('lp-pop-kamer').open")
        boek = await pg.get_attribute('#lp-pop-kamer .lp-pop__boek', 'href')
        ok(open_ and 'mewsRoom=' in boek and f'language={MEWS_TAAL}' in boek, 'kamer-pop-up opent via Meer info, boekknop met kamer')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # wellness: 5 tegels, tegel opent de pop-up
    if 'wellness' in D['blokken']:
        ok(await pg.locator('.zk-well .al-tegel').count() == 5 and await pg.locator('.zk-well .zk-well__feiten li').count() == 4, 'wellness: 5 tegels en 4 feiten')
        tg = pg.locator('.zk-well .al-tegel').nth(1)
        await klik(pg, tg); await pg.wait_for_timeout(500)
        ok(await pg.locator('[data-pop-dialog]:not([hidden]) .al-pop__naam').count() == 1, 'wellnesstegel opent de pop-up')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # arrangementen: kaarten, uitgelicht, live prijs, Mehr Info
    if 'arr' in D['blokken']:
        n = sum(1 for s in ('links', 'uit', 'rechts') if D.get(f'arr-{s}-bron'))
        ok(await pg.locator('.zk-arr .al-ak').count() == n and await pg.locator('.zk-arr .al-ak--uit').count() == (1 if D.get('arr-uit-bron') else 0), f'{n} arrangementkaarten, midden uitgelicht')
        await pg.wait_for_timeout(300)
        ok(await pg.locator('.zk-arr [data-arr-vanaf-live]').count() >= 1, 'arrangementprijzen live gevuld (arr-vanaf gemockt)')
        ak = pg.locator('.zk-arr .al-ak--uit .al-ak__ontdek')
        await klik(pg, ak); await pg.wait_for_timeout(500)
        ok(await pg.locator('[data-pop-dialog]:not([hidden]) .al-pc-naam').count() == 1, 'Mehr Info opent de arrangement-pop-up')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # kaart: hotel + punten, punt 1 uitgelicht, geen legenda
    if 'ligging' in D['blokken']:
        n = len(D['kaart']['punten'])
        kaart = pg.locator('.zk-ligging .ut-kaart__beeld')
        await kaart.scroll_into_view_if_needed(); await pg.wait_for_timeout(1800)
        ok(await pg.locator('.zk-ligging .ut-kaart__beeld.is-interactief').count() == 1, 'kaart interactief (vangnetfoto weg)')
        ok(await pg.locator('.zk-ligging .gk-hotel img').count() == 1, 'hotelvignet op de kaart')
        ok(await pg.locator('.zk-ligging .gk-punt').count() == n, f'kaart rendert met {n} punten')
        st = await pg.evaluate("""() => { var p=[].slice.call(document.querySelectorAll('.zk-ligging .gk-punt'));
          return p.map(function(x){ var nr=x.querySelector('.gk-punt__nr'), nm=x.querySelector('.gk-punt__naam');
            return [nr.textContent, getComputedStyle(nr).backgroundColor, getComputedStyle(nm).display] }) }""")
        ok(st and st[0][0] == '1' and st[0][2] != 'none' and all(x[2] == 'none' for x in st[1:]) and st[0][1] != st[1][1],
           f'punt 1 uitgelicht met naam, andere punten alleen nummer ({[x[0] for x in st]})')
        ok(await pg.locator('.zk-ligging .ut-kaart__legenda').count() == 0, 'geen legenda nodig')
        links = [[p['url'], p['url-label']] for p in D['kaart']['punten'] if p.get('url')]
        gevonden = await pg.eval_on_selector_all('.zk-ligging .zk-rij__link', 'els => els.map(e => [e.getAttribute("href"), e.textContent.replace(/\\s*\u2192$/, "").trim()])')
        ok(gevonden == links, f'tekstlinks in de lijst = kaartpunten met url ({len(links)})')
        pt_json = await pg.evaluate("JSON.parse(document.getElementById('ut-kaart-punten').textContent).punten.some(p => 'url' in p)")
        ok(not pt_json, 'kaartdata zonder url (alleen de lijst linkt)')
        ok(await pg.locator('.zk-ligging .zk-rij').count() == n and await pg.locator('.zk-ligging .zk-rij--uit').count() == 1, f'lijst: {n} regels, nummer 1 uitgelicht')
        s0 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
        await pg.locator('.zk-ligging .gk-knop').first.click(); await pg.wait_for_timeout(700)
        s1 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
        ok(s0 and s1 and s1 > s0 * 1.2, f'inzoomen werkt ({s0} -> {s1})')
        await pg.locator('.zk-ligging .gk-knop').nth(2).click(); await pg.wait_for_timeout(700)
        rk = await pg.get_attribute('.zk-ligging__knop', 'href')
        ok(rk and 'google.com/maps' in rk, 'routeknop naar Google Maps')

    # FAQ: tabs schakelen, JSON-LD = zichtbare tekst
    if 'faq' in D['blokken']:
        tabs = pg.locator('.zk-faq [role="tab"]')
        nt = await tabs.count()
        ok(nt >= 2 and await pg.locator('.zk-faq [role="tablist"]:not([hidden])').count() == 1, f'FAQ-tabs zichtbaar ({nt})')
        await klik(pg, tabs.nth(1)); await pg.wait_for_timeout(300)
        p1z = await pg.locator('.zk-faq .al-faq__paneel').nth(0).is_visible()
        p2z = await pg.locator('.zk-faq .al-faq__paneel').nth(1).is_visible()
        sel = await tabs.nth(1).get_attribute('aria-selected')
        ok(not p1z and p2z and sel == 'true', 'tab 2 schakelt: paneel 2 zichtbaar, paneel 1 verborgen')
        await tabs.nth(0).click(); await pg.wait_for_timeout(300)
        ok(await pg.locator('.zk-faq .al-faq__paneel').nth(0).is_visible(), 'tab 1 schakelt terug')
        lds = [json.loads(x) for x in await pg.eval_on_selector_all('script[type="application/ld+json"]', 'els => els.map(e => e.textContent)')]
        ld = next((x for x in lds if x.get('@type') == 'FAQPage'), None)
        vragen = await pg.eval_on_selector_all('.zk-faq .as-accordeon__item', 'els => els.map(e => [e.querySelector("summary").textContent.trim(), e.querySelector(".as-accordeon__paneel").textContent.trim()])')
        ok(ld and [[q['name'], q['acceptedAnswer']['text']] for q in ld['mainEntity']] == vragen, f'FAQPage JSON-LD = zichtbare tekst ({len(vragen)} vragen)')

    # Mews klik (boekknop slot) opent de widget in de taal
    slot = pg.locator('.zk-slot .al-slot__band a.mews-open')
    await klik(pg, slot); await pg.wait_for_timeout(1200)
    mews = await pg.evaluate('window.__mews || []')
    ok(any(m['taal'] == MEWS_TAAL and any(c[0] == 'open' for c in m['calls']) for m in mews), f'Mews-widget opent in {MEWS_TAAL}')

    # overloop en console
    breed = await pg.evaluate('document.documentElement.scrollWidth')
    ok(breed <= w, f'geen horizontale overloop ({breed} <= {w})')
    ok(not log['api'], f'geen andere /api-aanroepen, ook geen kamer-vanaf ({log["api"][:3]})')
    ok(not log['console'], f'geen consolefouten ({log["console"][:3]})')
    await b.close()


async def schermafdrukken(p, w, map_):
    b, pg = await nieuwe_pagina(p, w, {'api': [], 'console': []})
    await scroll_alles(pg)
    await pg.add_style_tag(content='.mob-cta,.cookie-banner{display:none!important} .top-stack{position:relative!important}')
    await pg.wait_for_timeout(400)
    for blok, comp in zip(BLOKKEN, VOLGORDE):
        el = pg.locator(f'main > [data-component="{comp}"]')
        if await el.count():
            await el.screenshot(path=os.path.join(map_, f'{NAAM}-{w}-{blok}.png'))
    await pg.screenshot(path=os.path.join(map_, f'{NAAM}-{w}-pagina.png'), full_page=True)
    await b.close()


async def main():
    fouten = []
    async with async_playwright() as p:
        for w in BREEDTES:
            print(f'== {w} px')
            await test_breedte(p, w, fouten)
            if SHOT:
                os.makedirs(SHOT, exist_ok=True)
                await schermafdrukken(p, w, SHOT)
    if fouten:
        print('\nFOUT:\n  ' + '\n  '.join(fouten))
        sys.exit(1)
    print('\nAlles groen.')


asyncio.run(main())
