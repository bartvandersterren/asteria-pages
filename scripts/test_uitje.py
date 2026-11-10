#!/usr/bin/env python3
"""Test van de uitjepagina (uitje.template.html), naar model van scripts/test_adslander.py.

Gebruik:
  python3 -m http.server 8792 --directory .            (in de repo-root)
  python3 scripts/test_uitje.py [URL] [--schermafdruk qa/uitje] [--breedtes 1440,390]
  standaard-URL: http://localhost:8792/zooparc-overloon-v2.html

Mews en de /api/*-functies worden gemockt (Mews-script = stub die elke API-aanroep logt in window.__mews; /api/* geeft 404
en wordt geteld: de pagina mag GEEN /api/kamer-vanaf of andere API vragen). Exit 0 = alles groen.
Met --schermafdruk <map>: per breedte de volledige pagina en elk blok als <map>/asteria-<breedte>-<blok>.png
(bloknamen gelijk aan de Parkhotel-platen: hero, oog, verhaal, tip, prak, dag, kamers, kaart, faq, meer, slot).
"""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
URL = next((a for a in args if a.startswith('http')), 'http://localhost:8792/zooparc-overloon-v2.html')
SHOT = args[args.index('--schermafdruk') + 1] if '--schermafdruk' in args else None
BREEDTES = [int(x) for x in (args[args.index('--breedtes') + 1] if '--breedtes' in args else '1440,390').split(',')]

CFG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
KAMERS = json.load(open(os.path.join(BASE, 'content', 'uitje-kamers-nl.json'), encoding='utf-8'))['kamer']
VOLGORDE = ['ut-hero', 'ut-oog', 'ut-verhaal', 'ut-tip', 'ut-prak', 'ut-dag', 'ut-kamers', 'ut-kaart', 'ut-faq', 'ut-meer', 'ut-slot']
BLOKNAAM = {'ut-hero': 'hero', 'ut-oog': 'oog', 'ut-verhaal': 'verhaal', 'ut-tip': 'tip', 'ut-prak': 'prak', 'ut-dag': 'dag',
            'ut-kamers': 'kamers', 'ut-kaart': 'kaart', 'ut-faq': 'faq', 'ut-meer': 'meer', 'ut-slot': 'slot'}

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[]};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""


async def mocks(ctx, log):
    async def api(route):
        if '/api/track' in route.request.url:   # analytics-d1.js (D1-events) mag wel
            await route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
            return
        log['api'].append(route.request.url)
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


async def test_breedte(p, w, fouten):
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

    # kop en meta
    ok(await pg.get_attribute('meta[name=robots]', 'content') == 'noindex, follow', 'robots = noindex, follow')
    ok(await pg.get_attribute('html', 'lang') == 'nl', 'html lang nl')
    html = await pg.content()
    ok(not re.search(r'\{\{[A-Za-z_0-9-]+\}\}', html), 'geen open {{velden}}')
    ok('—' not in html, 'geen em-dash')

    # blokvolgorde
    comps = await pg.eval_on_selector_all('main [data-component]', 'els => els.map(e => e.getAttribute("data-component"))')
    ok(comps == VOLGORDE, f'10 blokken + kamers in de juiste volgorde ({len(comps)} gevonden)')

    # oogopslag overlapt de hero
    ov = await pg.evaluate("""() => { var h=document.querySelector('.ut-hero').getBoundingClientRect(), o=document.querySelector('.ut-oog__paneel').getBoundingClientRect(); return Math.round(h.bottom - o.top) }""")
    ok(ov == (64 if mobiel else 120), f'oogopslagpaneel hangt {64 if mobiel else 120} px over de hero ({ov})')

    # geen prijs
    ok(await pg.locator('.kk-prijs, [data-kamer-vanaf], [data-arr-vanaf]').count() == 0, 'geen prijselementen')

    # Lees meer
    knop = pg.locator('.ut-meerbalk__knop')
    ok(await knop.is_visible(), 'Lees meer-balk zichtbaar')
    ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 1, 'verhaal rij 2-3 ingeklapt')
    await knop.scroll_into_view_if_needed(); await knop.click(); await pg.wait_for_timeout(300)
    ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 0 and (await knop.inner_text()).strip() == 'Lees minder', 'Lees meer opent (label Lees minder)')
    await knop.click(); await pg.wait_for_timeout(500)
    ok(await pg.locator('#ut-verhaal-meer.is-dicht').count() == 1 and (await knop.inner_text()).strip() == 'Lees meer', 'Lees minder sluit weer')

    # dagverloop: een open + fotowissel
    ok(await pg.locator('.ut-moment.is-aan').count() == 1, 'dagverloop: een moment open')
    m3 = pg.locator('.ut-moment[data-moment="3"] .ut-moment__kies')
    await m3.scroll_into_view_if_needed(); await m3.click(); await pg.wait_for_timeout(400)
    aan = await pg.eval_on_selector_all('.ut-moment.is-aan', 'els => els.map(e => e.dataset.moment)')
    beeld = await pg.eval_on_selector_all('.ut-dag__beeld.is-aan', 'els => els.map(e => e.dataset.beeld)')
    ok(aan == ['3'] and beeld == ['3'], f'moment 3 open en foto 3 zichtbaar ({aan}, {beeld})')
    ok(await pg.locator('.ut-moment[data-moment="3"] .ut-moment__kies').get_attribute('aria-expanded') == 'true', 'aria-expanded volgt het moment')

    # kamerslider: lus en teller
    n = len(KAMERS)
    echt = await pg.locator('#kamers .kk-kaart:not([data-kloon])').count()
    klonen = await pg.locator('#kamers .kk-kaart[data-kloon]:not([hidden])').count()
    ok(echt == 7, f'7 kamerkaarten ({echt})')
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

    # Mews-links
    hrefs = await pg.eval_on_selector_all('a.mews-open', 'els => els.map(e => [e.getAttribute("href"), e.getAttribute("data-room")])')
    ok(hrefs and all(CFG in h and 'language=nl-NL' in h for h, _ in hrefs), f'alle {len(hrefs)} boekknoppen: config {CFG[:8]} en nl-NL')
    kids = {v['kamer'] for v in KAMERS.values()}
    kamerknop = await pg.eval_on_selector_all('#kamers .kk-kaart a.mews-open', 'els => els.map(e => [e.getAttribute("href"), e.getAttribute("data-room")])')
    ok(kamerknop and all(r in kids and f'mewsRoom={r}' in h and 'mewsRoute=rooms' in h for h, r in kamerknop), 'kamerknoppen: juiste kamer-id + mewsRoute=rooms')
    ok('bee2f902' not in html and 'mewsVoucherCode' not in html, 'geen oude config, geen actiecode')

    # kamer-pop-up
    info = pg.locator('#kamers .kk-kaart:not([data-kloon]) a.btn-secondary[data-kamer]').first
    await info.scroll_into_view_if_needed(); await info.click(); await pg.wait_for_timeout(600)
    if mobiel:
        zicht = await pg.locator('[data-pop-dialog]:not([hidden]) .al-pop__naam').count() == 1
        naam = (await pg.locator('#al-pop-naam').inner_text()).strip() if zicht else ''
        ok(zicht and naam, f'kamer-pop-up (telefoonsheet) open: {naam}')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    else:
        open_ = await pg.evaluate("document.getElementById('lp-pop-kamer').open")
        naam = (await pg.locator('#lp-pop-kamer-naam').inner_text()).strip()
        boek = await pg.get_attribute('#lp-pop-kamer .lp-pop__boek', 'href')
        ok(open_ and naam and 'mewsRoom=' in boek and 'language=nl-NL' in boek, f'kamer-pop-up open: {naam}, boekknop met kamer')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # kaart: hotel + 4 punten, zoomt
    kaart = pg.locator('.ut-kaart__beeld')
    await kaart.scroll_into_view_if_needed(); await pg.wait_for_timeout(1500)
    ok(await pg.locator('.ut-kaart__beeld.is-interactief').count() == 1, 'kaart interactief (vangnetfoto weg)')
    ok(await pg.locator('.ut-kaart .gk-hotel img').count() == 1, 'hotelvignet op de kaart')
    ok(await pg.locator('.ut-kaart .gk-punt').count() == 4 and await pg.locator('.ut-kaart .gk-punt--hoofd').count() == 1
       and await pg.locator('.ut-kaart a.gk-punt[data-pop^="uitje:"]').count() == 3, 'kaart: speld + 3 knoppen met pop-up')
    s0 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
    await pg.locator('.ut-kaart .gk-knop').first.click(); await pg.wait_for_timeout(700)
    s1 = await pg.evaluate('window.utKaart && window.utKaart.stand().s')
    ok(s0 and s1 and s1 > s0 * 1.2, f'inzoomen werkt ({s0} -> {s1})')
    await pg.locator('.ut-kaart .gk-knop').nth(2).click(); await pg.wait_for_timeout(700)
    # kaartknop opent pop-up
    await pg.locator('.ut-kaart a.gk-punt[data-pop] .gk-punt__nr').first.click(); await pg.wait_for_timeout(500)
    pnaam = (await pg.locator('#al-pop-naam').inner_text()).strip() if await pg.locator('[data-pop-dialog]:not([hidden])').count() else ''
    ok(bool(pnaam), f'kaartknop 1 opent de uitje-pop-up ({pnaam})')
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

    # meer-kaarten openen de pop-up met route
    kaarten = pg.locator('.ut-meer .ut-uk')
    ok(await kaarten.count() == 3, '3 meer-kaarten')
    goed = True
    for i in range(await kaarten.count()):
        k = kaarten.nth(i)
        await k.scroll_into_view_if_needed(); await k.click(); await pg.wait_for_timeout(400)
        n = (await pg.locator('#al-pop-naam').inner_text()).strip() if await pg.locator('[data-pop-dialog]:not([hidden])').count() else ''
        route = await pg.locator('[data-pop-dialog] .al-pop__boek').get_attribute('href') if n else ''
        goed = goed and bool(n) and 'google.com/maps' in (route or '')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    ok(goed, 'elke meer-kaart opent de pop-up met naam en Route plannen')

    # FAQ en JSON-LD
    ld = json.loads(await pg.eval_on_selector('script[type="application/ld+json"]', 'e => e.textContent'))
    vragen = await pg.eval_on_selector_all('.ut-faq .as-accordeon__item', 'els => els.map(e => [e.querySelector("summary").textContent.trim(), e.querySelector(".as-accordeon__paneel").textContent.trim()])')
    ld_paren = [[q['name'], q['acceptedAnswer']['text']] for q in ld['mainEntity']]
    ok(ld['@type'] == 'FAQPage' and ld_paren == vragen and len(vragen) == 6, f'FAQPage JSON-LD = zichtbare tekst ({len(vragen)} vragen)')
    ok(await pg.locator('.ut-faq details[open]').count() == 1, 'eerste vraag open')
    ok(await pg.locator('.ut-faq [role="tablist"]').count() == 0, 'geen tabs')

    # Mews klik (boekknop slot) opent de widget in nl-NL
    slot = pg.locator('.ut-slot a.mews-open')
    ok(await slot.count() == 1 and await pg.locator('.ut-slot .btn').count() == 1, 'slot: precies een boekknop')
    await slot.scroll_into_view_if_needed(); await slot.click(); await pg.wait_for_timeout(1200)
    mews = await pg.evaluate('window.__mews || []')
    ok(any(m['taal'] == 'nl-NL' and any(c[0] == 'open' for c in m['calls']) for m in mews), 'Mews-widget opent in nl-NL')

    # overloop en console
    breed = await pg.evaluate('document.documentElement.scrollWidth')
    ok(breed <= w, f'geen horizontale overloop ({breed} <= {w})')
    ok(not log['api'], f'geen /api-aanroepen ({log["api"][:3]})')
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
            await el.screenshot(path=os.path.join(map_, f'asteria-{w}-{BLOKNAAM[comp]}.png'))
    await pg.screenshot(path=os.path.join(map_, f'asteria-{w}-volledig.png'), full_page=True)
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
