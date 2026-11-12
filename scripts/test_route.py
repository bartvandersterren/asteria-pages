#!/usr/bin/env python3
"""Test van de routepagina's (route.template.html), naar model van scripts/test_uitje.py.

Gebruik:
  python3 -m http.server 8793 --directory .            (in de repo-root)
  python3 scripts/test_route.py [URL ...] [--schermafdruk qa/routes] [--breedtes 1440,390] [--parkhotel]
  zonder URL: alle zes pagina's op http://localhost:8793/ (fietsen-/wandelen-rond-venray-v2[-de|-en].html)

Mews en de /api/*-functies worden gemockt (Mews-script = stub die elke API-aanroep logt in window.__mews; /api/* geeft 404
en wordt geteld: de pagina mag GEEN API vragen). Exit 0 = alles groen.
Controles per pagina en breedte: robots, lang, canonical, hreflang nl/de/en/x-default, geen open velden/em-dash/prijs, de
blokvolgorde (= Parkhotel), aantal routekaartjes = content/routes/<soort>.json, lengtefilter (chips en kaartbalk een stand,
?lengte= in de URL, telling, Wissen, beginstand uit de URL), kaart (lazy gebouwd, een lijn per route, lijnen zichtbaar),
lijstklik (rij actief, strook open, Bekijk = pop-up), pop-up (deeplink #route-<slug>, inhoud, focus-trap, Escape, hash weg),
Mews (taal per pagina, arrangementknop met code LIMBURG op de fietspagina), kamerslider (wandel), fotoslider (fiets),
geen horizontale overloop, geen /api-aanroepen, geen consolefouten.
Met --schermafdruk <map>: per pagina en breedte de volledige pagina en elk blok als webp (<map>/<pagina>-<breedte>-<blok>.webp).
Met --parkhotel erbij: ook de live Parkhotel-pagina's (/gebied/fietsroutes/, /gebied/wandelroutes/) per blok, en per blok een
vergelijkingsbeeld Parkhotel links / Asteria rechts in <map>/vergelijk/ (alleen de NL-pagina's).
"""
import asyncio, io, json, os, re, sys
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
SHOT = args[args.index('--schermafdruk') + 1] if '--schermafdruk' in args else None
BREEDTES = [int(x) for x in (args[args.index('--breedtes') + 1] if '--breedtes' in args else '1440,390').split(',')]
PARKHOTEL = '--parkhotel' in args
URLS = [a for a in args if a.startswith('http')] or [f'http://localhost:8793/{p}-rond-venray-v2{t}.html'
                                                    for p in ('fietsen', 'wandelen') for t in ('', '-de', '-en')]
PH_URL = {'fietsen': 'https://www.parkhotelhorst.nl/gebied/fietsroutes/', 'wandelen': 'https://www.parkhotelhorst.nl/gebied/wandelroutes/'}
TAAL = {'': ('nl', 'nl-NL'), '-de': ('de', 'de-DE'), '-en': ('en', 'en-US')}
BLOKKEN = ['hero', 'oog', 'routes', 'kaart', 'prak', 'conversie', 'faq', 'wissel', 'slot']

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[]};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""


def pagina_info(url):
    m = re.search(r'/(fietsen|wandelen)-rond-venray-v2(-de|-en)?\.html', url)
    soort = m.group(1)
    taal, mews = TAAL[m.group(2) or '']
    naam = f'{soort}{m.group(2) or ""}'
    with open(os.path.join(BASE, 'content', 'routes', ('fiets' if soort == 'fietsen' else 'wandel') + '.json'), encoding='utf-8') as f:
        data = json.load(f)
    return soort, taal, mews, naam, data


async def mocks(ctx, log):
    async def api(route):
        if '/api/track' in route.request.url:
            await route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
            return
        log['api'].append(route.request.url)
        await route.fulfill(status=404, content_type='application/json', body='{"ok":false}')
    await ctx.route(re.compile(r'https?://(localhost|127\.0\.0\.1)[^/]*/api/.*'), api)
    await ctx.route(re.compile(r'https://app\.mews\.com/distributor/distributor\.min\.js.*'),
                    lambda r: r.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB))
    await ctx.route(re.compile(r'https://www\.googletagmanager\.com/.*'), lambda r: r.fulfill(status=200, body=''))


async def scroll_alles(pg):
    h = await pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, h, 500):
        await pg.evaluate(f'window.scrollTo(0,{y})')
        await pg.wait_for_timeout(60)
    await pg.wait_for_timeout(900)
    await pg.evaluate('window.scrollTo(0,0)')
    await pg.wait_for_timeout(300)


async def nieuwe_pagina(b, w, log):
    mobiel = w < 768
    ctx = await b.new_context(viewport={'width': w, 'height': 844 if mobiel else 900}, is_mobile=mobiel, has_touch=mobiel)
    await mocks(ctx, log)
    pg = await ctx.new_page()
    pg.on('console', lambda m: log['console'].append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: log['console'].append(str(e)))
    return ctx, pg


async def test_pagina(p, url, w, fouten):
    soort, taal, mews_taal, naam, data = pagina_info(url)
    routes = data['routes']
    b = await p.chromium.launch()
    log = {'api': [], 'console': []}
    ctx, pg = await nieuwe_pagina(b, w, log)
    await pg.goto(url, wait_until='networkidle')
    await pg.evaluate("try{localStorage.setItem('cookie-consent','1')}catch(e){}; var c=document.getElementById('cookieBanner'); if(c) c.classList.remove('show')")

    def ok(cond, tekst):
        print(('  ok   ' if cond else '  FOUT ') + f'[{naam} {w}] {tekst}')
        if not cond:
            fouten.append(f'[{naam} {w}] {tekst}')

    # kop, meta, inhoud
    ok(await pg.get_attribute('meta[name=robots]', 'content') == 'noindex, follow', 'robots = noindex, follow')
    ok(await pg.get_attribute('html', 'lang') == taal, f'html lang {taal}')
    ok(await pg.get_attribute('html', 'data-mews-taal') == mews_taal, f'data-mews-taal {mews_taal}')
    canon = await pg.get_attribute('link[rel=canonical]', 'href')
    ok(canon and canon.endswith(url.rsplit('/', 1)[-1].replace('.html', '')), f'canonical op het eigen adres ({canon})')
    hl = await pg.eval_on_selector_all('link[rel=alternate][hreflang]', 'ls => ls.map(l => l.hreflang + "=" + l.href)')
    ok(sorted(x.split('=')[0] for x in hl) == ['de', 'en', 'nl', 'x-default'], f'hreflang nl/de/en/x-default ({len(hl)})')
    html = await pg.content()
    ok(not re.search(r'\{\{[^}]+\}\}', html), 'geen open {{velden}}')
    ok('—' not in html and not re.search(r'\s–\s', html), 'geen em-dash of en-dash als cesuur')
    ok('€' not in html and '&euro;' not in html, 'geen prijs (€)')
    ok('bee2f902' not in html, 'geen oude Mews-config')
    ld = await pg.eval_on_selector_all('script[type="application/ld+json"]', 'ss => ss.map(s => s.textContent)')
    typen = []
    for s in ld:
        try:
            j = json.loads(s)
            typen += [g['@type'] for g in j.get('@graph', [j])]
        except Exception:
            typen.append('ONGELDIG')
    ok(all(t in typen for t in ('WebPage', 'BreadcrumbList', 'FAQPage')) and 'ONGELDIG' not in typen, f'JSON-LD {typen}')
    h1 = (await pg.text_content('h1')).strip()
    if soort == 'fietsen':
        ok({'nl': 'Fietshotel', 'de': 'Fahrradhotel', 'en': 'cycling hotel'}[taal].lower() in h1.lower(), f'h1 bevat het zoekwoord ({h1})')
        ok({'nl': 'Fietshotel', 'de': 'Fahrradhotel', 'en': 'Cycling hotel'}[taal].lower() in (await pg.title()).lower(), 'titel bevat het zoekwoord')

    # blokvolgorde = Parkhotel (1b 2a 3b 4c 6a 7b 8a 9c 10a)
    comps = await pg.eval_on_selector_all('main [data-component]', 'es => es.map(e => e.getAttribute("data-component"))')
    zevenb = 'rt-arr' if soort == 'fietsen' else 'rt-kamers'
    verwacht = ['rt-hero', 'rt-oog', 'rt-routes', 'rt-kaart', 'rt-prak', zevenb, 'rt-faq', 'grv', 'rt-wissel', 'rt-slot']
    ok(comps == verwacht, f'blokvolgorde {comps}')
    ok(await pg.locator('.rt-kaartje').count() == len(routes), f'{len(routes)} routekaartjes')
    ok(await pg.locator('.rt-kaart__lijst .rt-rij').count() == len(routes), f'{len(routes)} lijstrijen')
    ok(await pg.locator('.rt-chip').count() == 4, '4 lengtechips')
    ok(await pg.locator('.rt-tegels .rt-icotegel').count() == 4, '4 oogopslagtegels')
    ok(await pg.locator('.rt-prak__tegels .rt-fotokaart').count() == 4, '4 fotokaarten Goed om te weten')
    ok(await pg.locator('.rt-faq details').count() == 5 and await pg.locator('.rt-faq details[open]').count() == 1, 'FAQ 5 vragen, eerste open')
    oog_top = await pg.evaluate("document.querySelector('.rt-oog__paneel').getBoundingClientRect().top - document.querySelector('.rt-hero').getBoundingClientRect().bottom")
    ok(oog_top < -40, f'oogopslagpaneel hangt over de hero ({round(oog_top)} px)')

    # lengtefilter: chips en kaartbalk een stand, URL, telling
    per = {k: sum(1 for r in routes if r['lengteklasse'] == k) for k in ('kort', 'middel', 'lang')}
    ok(all(per.values()), f'elke lengteklasse heeft een route {per}')
    zichtbaar = "() => [...document.querySelectorAll('.rt-kaartje')].filter(k => !k.hidden).length"
    await pg.click('.rt-chip[data-filter="kort"]')
    ok(await pg.evaluate(zichtbaar) == per['kort'], f'chip Kort toont {per["kort"]} kaartjes')
    ok('lengte=kort' in pg.url, f'URL ?lengte=kort ({pg.url.rsplit("/", 1)[-1]})')
    ok(await pg.get_attribute('.rt-filt__knop[data-filter="kort"]', 'aria-pressed') == 'true', 'kaartbalk volgt de chip')
    live = await pg.text_content('.rt-filt__live')
    ok(f'{per["kort"]} ' in live and str(len(routes)) in live, f'telling ({live})')
    rijen = await pg.evaluate("[...document.querySelectorAll('.rt-kaart__lijst li')].filter(l => !l.hidden).length")
    ok(rijen == per['kort'], 'lijst filtert mee')
    await pg.click('.rt-filt__knop[data-filter="lang"]')
    ok('lengte=lang' in pg.url and await pg.evaluate(zichtbaar) == per['lang'], 'kaartbalk Lang: URL + kaartjes')
    ok(await pg.get_attribute('.rt-chip[data-filter="lang"]', 'aria-pressed') == 'true', 'chip volgt de kaartbalk')
    await pg.click('.rt-filt__wissen')
    ok('lengte=' not in pg.url and await pg.evaluate(zichtbaar) == len(routes), 'Wissen: alles terug, URL schoon')

    # kaart: lazy gebouwd, een lijn per route, zichtbaar
    await pg.locator('.rt-kaart__beeld').scroll_into_view_if_needed()
    try:
        await pg.wait_for_selector('.rt-kaart__beeld[data-gebouwd="1"]', timeout=8000)
        gebouwd = True
    except Exception:
        gebouwd = False
    ok(gebouwd, 'interactieve kaart gebouwd na in beeld komen')
    nlijn = await pg.locator('.rt-kaart .gk-routes .rt').count()
    ok(nlijn == len(routes), f'{nlijn} routes op de kaart')
    zichtbaar_lijn = await pg.evaluate("""[...document.querySelectorAll('.rt-kaart .gk-routes .rt .rt-lijn')].filter(l => { const b = l.getBoundingClientRect(); return b.width > 2 || b.height > 2 }).length""")
    speld = sum(1 for r in routes if not r.get('lijn'))
    ok(zichtbaar_lijn >= len(routes) - speld, f'lijnen zichtbaar ({zichtbaar_lijn})')
    ok(await pg.locator('.rt-kaart .routebadge.rt-speld').count() == speld, f'{speld} speld(en) voor gebieden zonder lijn')
    eerste = routes[0]['slug']
    await pg.click(f'.rt-rij[data-slug="{eerste}"]')
    await pg.wait_for_timeout(700)
    ok('is-actief' in (await pg.get_attribute(f'.rt-rij[data-slug="{eerste}"]', 'class')), 'lijstklik: rij actief')
    ok('is-open' in (await pg.get_attribute('.rt-voet', 'class')), 'lijstklik: strook open')
    ok(await pg.locator('.rt-kaart .gk-routes .rt.on').count() == 1, 'lijstklik: route uitgelicht')
    await pg.click('.rt-voet__bekijk')
    await pg.wait_for_timeout(400)
    ok('is-open' in (await pg.get_attribute('#rtPop', 'class')) and pg.url.endswith(f'#route-{eerste}'), 'Bekijk opent de pop-up met #route-<slug>')
    await pg.keyboard.press('Escape')
    await pg.wait_for_timeout(300)
    ok('is-open' not in (await pg.get_attribute('#rtPop', 'class')) and '#route-' not in pg.url, 'Escape sluit de pop-up, hash weg')
    await pg.keyboard.press('Escape')
    await pg.wait_for_timeout(300)
    ok('is-open' not in (await pg.get_attribute('.rt-voet', 'class')), 'Escape sluit de strook')

    # Mews
    knop = pg.locator('.rt-oog .mews-open').first
    await knop.click()
    await pg.wait_for_timeout(600)
    mews = await pg.evaluate('window.__mews || []')
    ok(any(m['taal'] == mews_taal for m in mews), f'Mews in {mews_taal} ({[m["taal"] for m in mews]})')
    ok(any(c[0] == 'open' for m in mews for c in m['calls']), 'boekknop opent Mews')
    hrefs = await pg.eval_on_selector_all('main a[href*="mews.com/distributor"]', 'as => as.map(a => a.href)')
    ok(hrefs and all(f'language={mews_taal}' in h for h in hrefs), f'alle Mews-links in {mews_taal} ({len(hrefs)})')
    if soort == 'fietsen':
        arr = pg.locator('.rt-arr .mews-open')
        ok(await arr.count() == 1 and await arr.get_attribute('data-voucher') == 'LIMBURG', 'arrangementknop met code LIMBURG')
        ok(await pg.locator('main .mews-open[data-voucher]').count() == 1, 'alleen de arrangementknop draagt een code')
        ok(await pg.get_attribute('.rt-arr__acties a[href="/limburg-arrangement"]', 'href') == '/limburg-arrangement', 'knop naar /limburg-arrangement')
        await pg.locator('.rt-arr').scroll_into_view_if_needed()
        await pg.click('.rt-fs__pijl[data-fs-stap="1"]')
        await pg.wait_for_timeout(700)
        ok('is-aan' in (await pg.get_attribute('.rt-fs__bol[data-fs-naar="1"]', 'class')), 'fotoslider: pijl naar dia 2')
        ok(await pg.locator('.rt-fs__dia').count() == 6, 'fotoslider zes dia\'s')
    else:
        ok(await pg.locator('#kamers .kk-kaart:not([aria-hidden="true"])').count() >= 7 or await pg.locator('#kamers .kk-kaart').count() >= 7, 'kamerslider met de kamers')
        kh = await pg.eval_on_selector_all('#kamers a.mews-open[data-room]', 'as => as.map(a => a.href)')
        ok(kh and all('mewsRoom=' in h and f'language={mews_taal}' in h for h in kh), 'kamerknoppen naar Mews met kamer en taal')
    ok('wandelen' in (await pg.get_attribute('.rt-wtegel--ander', 'href')) if soort == 'fietsen'
       else 'fietsen' in (await pg.get_attribute('.rt-wtegel--ander', 'href')), 'kruislink naar de andere pagina')
    ander = await pg.get_attribute('.rt-wtegel--ander', 'href')
    ok(ander.endswith({'nl': 'v2', 'de': 'v2-de', 'en': 'v2-en'}[taal]), f'kruislink in dezelfde taal ({ander})')
    breed = await pg.evaluate('document.documentElement.scrollWidth')
    ok(breed <= w, f'geen horizontale overloop ({breed} <= {w})')
    await ctx.close()

    # pop-up via deeplink + focus-trap
    ctx, pg = await nieuwe_pagina(b, w, log)
    laatste = routes[-1]['slug']
    await pg.goto(f'{url}#route-{laatste}', wait_until='networkidle')
    await pg.wait_for_timeout(400)
    ok('is-open' in (await pg.get_attribute('#rtPop', 'class')), 'deeplink #route-<slug> opent de pop-up')
    titel = (await pg.text_content('.rt-pop__titel')).strip()
    ok(titel == (routes[-1]['naam'].get(taal) or routes[-1]['naam']['nl']), f'pop-up toont de route ({titel})')
    ok(await pg.locator('.rt-pop__beeld').count() >= 2, 'beeldenstrook: foto + lus-kaartje')
    ok(await pg.locator('.rt-pop__feiten .rt-stat').count() == 1 and await pg.locator('.rt-pop__feiten .rt-start').count() == 1, 'pop-up: feiten + startregel')
    cta = await pg.get_attribute('.rt-pop__cta', 'href')
    ok(cta == routes[-1]['url'], f'externe knop naar de routebron ({cta})')
    ok('google.com/maps' in (await pg.get_attribute('.rt-pop__maps', 'href')), 'Google Maps-link')
    ok((await pg.text_content('.rt-pop__tekst')).strip() != '', 'pop-uptekst gevuld')
    binnen = True
    for _ in range(10):
        await pg.keyboard.press('Tab')
        binnen = binnen and await pg.evaluate("document.getElementById('rtPop').contains(document.activeElement)")
    ok(binnen, 'focus blijft in de pop-up (Tab)')
    if soort == 'fietsen':
        kn = [r for r in routes if r.get('knooppunten')]
        if kn:
            await pg.evaluate("location.hash = '#route-" + kn[0]['slug'] + "'")
            await pg.wait_for_timeout(400)
            ok(await pg.locator('.rt-pop__feiten .rt-knoop').count() == 1, 'Fietsknoop-route: knooppuntenreeks in de pop-up')
            ok('fietsknoop.nl/fietsroute/' in (await pg.get_attribute('.rt-pop__cta', 'href')), 'Fietsknoop-route: knop naar fietsknoop.nl')
    await pg.click('.rt-pop__toon')
    await pg.wait_for_timeout(1500)
    ok('is-open' not in (await pg.get_attribute('#rtPop', 'class')), 'Toon op de kaart sluit de pop-up')
    await ctx.close()

    # beginstand uit de URL
    ctx, pg = await nieuwe_pagina(b, w, log)
    await pg.goto(url + '?lengte=gemiddeld', wait_until='networkidle')
    ok(await pg.evaluate(zichtbaar) == per['middel'] and await pg.get_attribute('.rt-chip[data-filter="middel"]', 'aria-pressed') == 'true',
       '?lengte=gemiddeld bij het laden')
    await ctx.close()

    ok(not log['api'], f'geen /api-aanroepen ({log["api"][:3]})')
    ok(not log['console'], f'geen consolefouten ({log["console"][:3]})')
    await b.close()


def webp(png, pad):
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert('RGB')
    im.save(pad, 'WEBP', quality=72, method=4)
    return im


async def blokplaten(b, url, w, ph=False):
    """{blok: PIL-beeld}, plus de volledige pagina (alleen Asteria)."""
    log = {'api': [], 'console': []}
    ctx, pg = await nieuwe_pagina(b, w, log)
    if ph:
        await ctx.route(re.compile(r'https://(app|api)\.mews\.com/.*'), lambda r: r.fulfill(status=200, body=''))
    await pg.goto(url, wait_until='load', timeout=60000)
    await pg.wait_for_timeout(1500)
    await scroll_alles(pg)
    if ph:
        await pg.add_style_tag(content='#nb-overlay,.nb-overlay,#CybotCookiebotDialog,#CybotCookiebotDialogBodyUnderlay,[id*=cookie],[class*=cookie],.kopbalk__zweef{display:none!important} .kopbalk,header{position:absolute!important}')
        pref = 'ro-'
        naam = {'hero': 'ro-hero', 'oog': 'ro-oog', 'routes': 'ro-routes', 'kaart': 'ro-kaart', 'prak': 'ro-prak', 'conversie': 'ro-arr',
                'faq': 'ro-faq', 'wissel': 'ro-wissel', 'slot': 'ro-slot'}
    else:
        await pg.evaluate("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
        await pg.add_style_tag(content='.mob-cta,.cookie-banner{display:none!important} .top-stack{position:relative!important}')
        naam = {'hero': 'rt-hero', 'oog': 'rt-oog', 'routes': 'rt-routes', 'kaart': 'rt-kaart', 'prak': 'rt-prak',
                'conversie': 'rt-arr, [data-component=rt-kamers]', 'faq': 'rt-faq', 'wissel': 'rt-wissel', 'slot': 'rt-slot'}
    # alle lazy beelden laden, dan EEN volledige plaat en de blokken daaruit knippen (element-screenshots verschoven op
    # de live Parkhotel-pagina door laden tijdens het scrollen)
    await pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
    await scroll_alles(pg)
    await pg.wait_for_timeout(800)
    from PIL import Image
    vol = await pg.screenshot(full_page=True)
    plaat = Image.open(io.BytesIO(vol)).convert('RGB')
    uit = {}
    for blok in BLOKKEN:
        sel = ', '.join(f'[data-component="{x.strip()}"]' if not x.strip().startswith('[') else x.strip() for x in naam[blok].split(','))
        r = await pg.evaluate("(s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect();"
                              " return [b.left + scrollX, b.top + scrollY, b.right + scrollX, b.bottom + scrollY]; }", sel)
        if r:
            uit[blok] = plaat.crop(tuple(round(v) for v in r))
    await ctx.close()
    return uit, (None if ph else vol)


def naast(links, rechts, pad, titel_l='Parkhotel', titel_r='Asteria'):
    from PIL import Image, ImageDraw
    b = max(x.width for x in (links, rechts) if x)
    sch = lambda im: im.resize((b, round(im.height * b / im.width))) if im and im.width != b else im
    links, rechts = sch(links), sch(rechts)
    h = max(x.height for x in (links, rechts) if x) + 28
    c = Image.new('RGB', (b * 2 + 20, h), 'white')
    d = ImageDraw.Draw(c)
    d.text((6, 6), titel_l, fill='black'); d.text((b + 26, 6), titel_r, fill='black')
    if links: c.paste(links, (0, 28))
    if rechts: c.paste(rechts, (b + 20, 28))
    if c.width > 2400:
        c = c.resize((2400, round(c.height * 2400 / c.width)))
    c.save(pad, 'WEBP', quality=70, method=4)


async def platen(p, url, w, map_):
    soort, taal, _, naam, _ = pagina_info(url)
    b = await p.chromium.launch()
    blokken, vol = await blokplaten(b, url, w)
    for blok, im in blokken.items():
        im.save(os.path.join(map_, f'{naam}-{w}-{blok}.webp'), 'WEBP', quality=72, method=4)
    if vol:
        webp(vol, os.path.join(map_, f'{naam}-{w}-volledig.webp'))
    if PARKHOTEL and taal == 'nl':
        vmap = os.path.join(map_, 'vergelijk')
        os.makedirs(vmap, exist_ok=True)
        try:
            ph, _ = await blokplaten(b, PH_URL[soort], w, ph=True)
        except Exception as e:  # noqa: BLE001
            print(f'  Parkhotel niet bereikbaar: {e}')
            ph = {}
        for blok in BLOKKEN:
            if blok in ph:
                ph[blok].save(os.path.join(vmap, f'parkhotel-{soort}-{w}-{blok}.webp'), 'WEBP', quality=70, method=4)
            if blok in ph or blok in blokken:
                naast(ph.get(blok), blokken.get(blok), os.path.join(vmap, f'{soort}-{w}-{blok}.webp'))
    await b.close()


async def main():
    fouten = []
    async with async_playwright() as p:
        for url in URLS:
            for w in BREEDTES:
                print(f'== {url.rsplit("/", 1)[-1]} {w} px')
                await test_pagina(p, url, w, fouten)
                if SHOT:
                    os.makedirs(SHOT, exist_ok=True)
                    await platen(p, url, w, SHOT)
    if fouten:
        print(f'\nFOUT ({len(fouten)}):\n  ' + '\n  '.join(fouten))
        sys.exit(1)
    print('\nAlles groen.')


asyncio.run(main())
