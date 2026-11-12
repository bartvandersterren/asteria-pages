#!/usr/bin/env python3
"""Test van de omgevingspagina's (omgeving.template.html + omgeving-categorie.template.html), naar model van scripts/test_uitje.py.

Gebruik:
  python3 -m http.server 8813 --directory .          (in de repo-root)
  python3 scripts/test_omgeving.py [BASIS-URL] [--paginas omgeving-v2,omgeving-golf-v2] [--breedtes 1440,390] [--schermafdruk qa/omgeving]
  standaard: http://localhost:8813, alle zes NL-pagina's, 1440 en 390.

Verwachtingen komen uit translations/omgeving-<pagina>-nl.json (+ labels). Mews is een stub (logt elke API-aanroep in window.__mews),
/api/arr-kalender geeft een paar dagen, /api/track 204, elke andere /api 404 (geteld). Exit 0 = alles groen.
Controleert: noindex/canonical, blokvolgorde, geen horizontale scroll, consolefouten, 404's (foto's), geen "€" in de zichtbare tekst
(de gesloten prijskalender telt niet mee), Mews-links (6dc9094c, nl-NL, geen bee2f902, kamerknoppen met mewsRoom zonder prijs),
tegels (aantal = kaarten op de categoriepagina, niet op de telefoon), filters (elke combinatie + lege melding), deeplinks + hashchange,
Toon alle, dagaccordeon, FAQ + FAQPage, kamerslider + pop-up, golf-veegrij (teller, pijlen, toetsen), vergelijkingstabel, arrangementknop
met kalender, meer-blok.
"""
import json, os, re, sys, datetime
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
BASIS = next((a for a in args if a.startswith('http')), 'http://localhost:8813').rstrip('/')
SHOT = args[args.index('--schermafdruk') + 1] if '--schermafdruk' in args else None
BREEDTES = [int(x) for x in (args[args.index('--breedtes') + 1] if '--breedtes' in args else '1440,390').split(',')]
NL_PAGINAS = ['omgeving-v2', 'omgeving-cultuur-v2', 'omgeving-dagje-uit-v2', 'omgeving-natuur-v2', 'omgeving-shoppen-steden-v2', 'omgeving-golf-v2']
TALEN = ['nl', 'de', 'en']
PAGINAS = (args[args.index('--paginas') + 1].split(',') if '--paginas' in args else
           [p + ('' if t == 'nl' else '-' + t) for t in TALEN for p in NL_PAGINAS
            if os.path.exists(os.path.join(BASE, p + ('' if t == 'nl' else '-' + t) + '.html'))])
CATS = ['golf', 'natuur', 'cultuur', 'dagje-uit', 'shoppen-steden']
MODES = ['auto', 'lopen', 'fiets']
STD = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
LABELS = {t: json.load(open(os.path.join(BASE, 'translations', f'omgeving-labels-{t}.json'), encoding='utf-8'))
          for t in TALEN if os.path.exists(os.path.join(BASE, 'translations', f'omgeving-labels-{t}.json'))}
KAL = json.load(open(os.path.join(BASE, 'content', 'arr-kalender.json'), encoding='utf-8'))

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[],code:''};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){if(m==='setVoucherCode')log.code=String(arguments[0]==null?'':arguments[0]);
log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""

goed, fout, let = [], [], []


def check(naam, ok, extra=''):
    (goed if ok else fout).append(naam + ('' if ok else f'  ({extra})'))
    if not ok:
        print('  FOUT', naam, extra)


def taal_van(pagina):
    return pagina[-2:] if pagina[-3:] in ('-de', '-en') else 'nl'


def gegevens(pagina):
    t = taal_van(pagina)
    kaal = pagina[:-3] if t != 'nl' else pagina
    sleutel = 'overzicht' if kaal == 'omgeving-v2' else kaal[len('omgeving-'):-len('-v2')]
    d = dict(LABELS[t])
    d.update(json.load(open(os.path.join(BASE, 'translations', f'omgeving-{sleutel}-{t}.json'), encoding='utf-8')))
    return sleutel, d, t


def kalender_api(route):
    m = re.search(r'maand=(\d{4})-(\d{2})', route.request.url)
    j, mnd = (int(m.group(1)), int(m.group(2))) if m else (2027, 1)
    dagen = [{'datum': f'{j}-{mnd:02d}-{d:02d}', 'zondag': datetime.date(j, mnd, d).weekday() == 6, 'aankomst_mag': True, 'beschikbaar': True,
              'prijzen': {'4a642b66-68e6-444c-beeb-af1d00ffc315': {'prijs_cent': 30000, 'berekend': False}}} for d in range(1, 9)]
    route.fulfill(status=200, content_type='application/json', body=json.dumps({'ok': True, 'dagen': dagen}))


def zichtbaar_aantal(page, sel):
    return page.evaluate(f"Array.from(document.querySelectorAll({json.dumps(sel)})).filter(e=>e.offsetParent!==null&&getComputedStyle(e).display!=='none').length")


def test_pagina(b, pagina, w, tegelverwachting):
    sleutel, d, taal = gegevens(pagina)
    L = LABELS[taal]
    tegelverwachting = tegelverwachting[taal]
    tag = f'[{pagina} {w}]'
    ctx = b.new_context(viewport={'width': w, 'height': 900}, is_mobile=w < 600, has_touch=w < 600)
    page = ctx.new_page()
    console, kapot, api = [], [], []
    page.on('console', lambda m: console.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: kapot.append(f'{r.status} {r.url}') if r.status >= 400 and '/api/' not in r.url else None)
    # Playwright: de laatst geregistreerde route wint, dus de vangnetroute eerst
    page.route('**/api/**', lambda r: (api.append(r.request.url), r.fulfill(status=404, body='')))
    page.route('**/app.mews.com/distributor/distributor.min.js', lambda r: r.fulfill(status=200, content_type='text/javascript', body=MEWS_STUB))
    page.route('**/api/arr-kalender**', kalender_api)
    page.route('**/api/track**', lambda r: r.fulfill(status=204, body=''))
    page.route('**/googletagmanager.com/**', lambda r: r.fulfill(status=200, content_type='text/javascript', body=''))
    page.goto(f'{BASIS}/{pagina}.html', wait_until='networkidle')
    page.evaluate("try{localStorage.setItem('cookieConsent','1')}catch(e){};var c=document.getElementById('cookieBanner');c&&c.remove()")

    # kop, robots, canonical
    check(f'{tag} robots noindex, follow', page.get_attribute('meta[name=robots]', 'content') == 'noindex, follow')
    check(f'{tag} canonical', page.get_attribute('link[rel=canonical]', 'href') == d['canonical'], page.get_attribute('link[rel=canonical]', 'href'))
    check(f'{tag} titel', page.title() == d['titel'], page.title())
    check(f'{tag} html lang {taal}', page.get_attribute('html', 'lang') == taal)
    alt = page.eval_on_selector_all('link[rel=alternate]', 'els=>els.map(e=>[e.hreflang,e.getAttribute("href")])')
    talen_er = [t for t in TALEN if os.path.exists(os.path.join(BASE, pagina[:-3] + ('' if t == 'nl' else '-' + t) + '.html'))] if taal != 'nl' else \
        [t for t in TALEN if os.path.exists(os.path.join(BASE, pagina + ('' if t == 'nl' else '-' + t) + '.html'))]
    if len(talen_er) > 1:
        check(f'{tag} hreflang {"/".join(talen_er)} + x-default', sorted(h for h, _ in alt) == sorted(talen_er + ['x-default'])
              and dict(alt).get(taal) == d['canonical'], alt)

    # blokvolgorde
    comp = page.eval_on_selector_all('main > [data-component]', 'els=>els.map(e=>e.getAttribute("data-component"))')
    if sleutel == 'overzicht':
        verwacht = ['om-hero', 'om-intro', 'om-raster', 'om-dag', 'om-kamers'] + (['om-arr'] if 'om-arr' in comp else []) + ['om-faq', 'grv', 'om-slot']
        check(f'{tag} arrangementenblok aanwezig', 'om-arr' in comp)
    else:
        uit = 'om-banen' if sleutel == 'golf' else 'om-uitjes'
        verwacht = (['om-hero', 'om-cintro'] + ([uit] if uit in comp else []) + (['om-vgl'] if sleutel == 'golf' else [])
                    + (['om-carr'] if d.get('conversie') == 'arr' else ['om-kamers']) + ['om-dag', 'om-cfaq', 'om-meer', 'om-slot'])
    check(f'{tag} blokvolgorde', comp == verwacht, f'{comp} != {verwacht}')

    # overloop, zichtbare tekst zonder euro, oude config
    breed = page.evaluate('document.documentElement.scrollWidth')
    check(f'{tag} geen horizontale scroll', breed <= w, f'scrollWidth {breed}')
    tekst = page.evaluate('document.body.innerText')
    check(f'{tag} geen € in de zichtbare tekst', '€' not in tekst)
    html = page.content()
    check(f'{tag} geen bee2f902', 'bee2f902' not in html)
    hrefs = page.eval_on_selector_all('a[href*="mews.com/distributor"]', 'els=>els.map(e=>e.getAttribute("href"))')
    mt = 'language=' + d['mews-taal']
    check(f'{tag} Mews-links op 6dc9094c met {d["mews-taal"]}', bool(hrefs) and all(STD in h and mt in h for h in hrefs),
          [h for h in hrefs if STD not in h or mt not in h][:3])
    check(f'{tag} geen em-dash', '\u2014' not in html)
    check(f'{tag} geen kamerprijs', page.locator('.kk-prijs, [data-kamer-vanaf]').count() == 0)

    # dag in vier momenten
    start = d.get('dag-start', '1' if sleutel == 'overzicht' else '2')
    check(f'{tag} dag: startmoment {start} open', page.locator(f'.ut-dag .ut-moment[data-moment="{start}"].is-aan').count() == 1)
    page.locator('.ut-dag .ut-moment[data-moment="3"] .ut-moment__kies').click()
    check(f'{tag} dag: moment 3 open + foto 3', page.locator('.ut-moment[data-moment="3"].is-aan').count() == 1
          and page.locator('.ut-dag__beeld[data-beeld="3"].is-aan').count() == 1 and page.locator('.ut-moment.is-aan').count() == 1)

    # FAQ + JSON-LD
    n_faq = page.locator('main details.as-accordeon__item').count()
    check(f'{tag} zes vragen, eerste open', n_faq == 6 and page.locator('main details.as-accordeon__item[open]').count() == 1
          and page.locator('main details.as-accordeon__item').first.get_attribute('open') is not None)
    ld = json.loads(page.eval_on_selector('script[type="application/ld+json"]', 'e=>e.textContent'))
    check(f'{tag} FAQPage met zes vragen', ld.get('@type') == 'FAQPage' and len(ld['mainEntity']) == 6)

    # kamerslider + pop-up
    if page.locator('#kamers').count():
        kaarten = page.locator('#kamers article.kk-kaart:not([data-kloon])')
        check(f'{tag} kamerslider met {len(d.get("kamers", []))} kamers', kaarten.count() == len(d.get('kamers', [])), kaarten.count())
        kh = page.eval_on_selector_all('#kamers article.kk-kaart:not([data-kloon]) a.mews-open', 'els=>els.map(e=>e.getAttribute("href"))')
        check(f'{tag} kamerknoppen naar Mews met mewsRoom', all('mewsRoom=' in h and 'mewsRoute=rooms' in h for h in kh))
        page.locator('#kamers').scroll_into_view_if_needed()
        knop = page.locator('#kamers article.kk-kaart:not([data-kloon]) .btn-secondary').first
        knop.scroll_into_view_if_needed()
        knop.click()
        page.wait_for_timeout(400)
        open_ = page.evaluate("(()=>{var a=document.getElementById('lp-pop-kamer');var b=document.querySelector('[data-pop-dialog]');return (a&&a.open)||(b&&!b.hidden)})()")
        check(f'{tag} kamer-pop-up opent', bool(open_))
        page.keyboard.press('Escape')
        page.wait_for_timeout(300)
        page.evaluate("var a=document.getElementById('lp-pop-kamer');a&&a.open&&a.close();var b=document.querySelector('[data-pop-dialog]');if(b)b.hidden=true")
        kk = page.locator('#kamers article.kk-kaart:not([data-kloon]) a.mews-open').first
        room = kk.get_attribute('data-room')
        kk.scroll_into_view_if_needed()
        kk.click()
        page.wait_for_timeout(600)
        log = page.evaluate('window.__mews||[]')
        check(f'{tag} kamerknop opent Mews met de kamer', any(any(c[0] == 'showRates' and room in c for c in l['calls']) for l in log)
              or any(any(c[0] == 'open' for c in l['calls']) for l in log), json.dumps(log)[:200])

    if sleutel == 'overzicht':
        # tegels
        tegels = page.locator('.om-tegel')
        check(f'{tag} vijf tegels', tegels.count() == 5)
        check(f'{tag} tegels {"zichtbaar" if w >= 768 else "verborgen"}', (zichtbaar_aantal(page, '.om-tegel') == 5) == (w >= 768))
        for i, c in enumerate(CATS):
            n = tegelverwachting.get(c)
            t = tegels.nth(i).inner_text() if w >= 768 else page.eval_on_selector_all('.om-tegel', f'els=>els[{i}].textContent')
            if n is not None:
                woord = (L['woord-baan'] if n == 1 else L['woord-banen']) if c == 'golf' else (L['woord-uitje'] if n == 1 else L['woord-uitjes'])
                check(f'{tag} tegel {c}: {n} {woord}', (f'{n} {woord}' in t) if n else not re.search(r'\d+ (uitje|baan)', t), t[:60])
        # filters: elke combinatie, lege melding exact als er niets overblijft
        page.locator('#activiteiten').scroll_into_view_if_needed()
        totaal = page.locator('.om-raster__grid .om-kaart').count()
        for c in ['alle'] + CATS:
            for m_ in ['alle'] + MODES:
                page.locator(f'label[for="om-f-{c}"]').click()
                page.locator(f'label[for="om-t-{m_}"]').click()
                kaarten = page.eval_on_selector_all('.om-raster__grid .om-kaart', 'els=>els.filter(e=>getComputedStyle(e).display!=="none").map(e=>e.className)')
                juist = all((c == 'alle' or f'cat-{c}' in k) and (m_ == 'alle' or f'mode-{m_}' in k) for k in kaarten)
                leeg = zichtbaar_aantal(page, '.om-leeg') == 1
                verwacht = sum(1 for k in page.eval_on_selector_all('.om-raster__grid .om-kaart', 'els=>els.map(e=>e.className)')
                               if (c == 'alle' or f'cat-{c}' in k) and (m_ == 'alle' or f'mode-{m_}' in k))
                if c == 'alle' and m_ == 'alle':
                    verwacht = min(verwacht, len(kaarten))   # Toon alle kan de rest verbergen
                check(f'{tag} filter {c} + {m_}: {verwacht} kaarten, lege melding {"aan" if verwacht == 0 else "uit"}',
                      juist and len(kaarten) == verwacht and leeg == (verwacht == 0), f'{len(kaarten)} kaarten, leeg {leeg}')
        page.locator('label[for="om-f-alle"]').click()
        page.locator('label[for="om-t-alle"]').click()
        # Toon alle
        grens = 8 if w < 768 else 12
        knop_zichtbaar = zichtbaar_aantal(page, '[data-om-meer] button') == 1
        if totaal > grens:
            check(f'{tag} Toon alle zichtbaar, {grens} kaarten', knop_zichtbaar and zichtbaar_aantal(page, '.om-raster__grid .om-kaart') == grens)
            check(f'{tag} Toon alle-tekst', page.inner_text('[data-om-meer] button').strip() == L['toon-alle'].format(n=totaal))
            page.locator('[data-om-meer] button').click()
            check(f'{tag} na Toon alle alle {totaal} kaarten', zichtbaar_aantal(page, '.om-raster__grid .om-kaart') == totaal)
        else:
            check(f'{tag} geen Toon alle bij {totaal} kaarten', not knop_zichtbaar and zichtbaar_aantal(page, '.om-raster__grid .om-kaart') == totaal)
        # kaarten gesorteerd op autominuten
        mins = page.eval_on_selector_all('.om-raster__grid .om-kaart', """els=>els.map(e=>{var v=[...e.querySelectorAll('.om-vk')].find(x=>/auto/.test(x.textContent));return v?parseInt(v.textContent):9999})""")
        check(f'{tag} kaarten gesorteerd op rijtijd', mins == sorted(mins), mins)
        # routes-strook alleen met routes
        check(f'{tag} routes-strook {page.locator(".om-route").count()} kaarten', page.locator('.om-routes').count() == (1 if page.locator('.om-route').count() else 0))
        # deeplinks + hashchange
        h_nat, h_fiets, h_voet = {'nl': ('#natuur', '#op-de-fiets', '#te-voet'), 'de': ('#natur', '#mit-dem-rad', '#zu-fuss'),
                                  'en': ('#nature', '#by-bike', '#on-foot')}[taal]
        page.goto(f'{BASIS}/{pagina}.html{h_nat}', wait_until='networkidle')
        check(f'{tag} deeplink {h_nat}', page.is_checked('#om-f-natuur'))
        page.evaluate(f"location.hash='{h_fiets}'")
        page.wait_for_timeout(200)
        check(f'{tag} hashchange {h_fiets}', page.is_checked('#om-t-fiets'))
        page.evaluate(f"location.hash='{h_voet}'")
        page.wait_for_timeout(200)
        check(f'{tag} hashchange {h_voet}', page.is_checked('#om-t-lopen'))
        page.evaluate("location.hash='#golf'")
        page.wait_for_timeout(200)
        check(f'{tag} hashchange #golf', page.is_checked('#om-f-golf'))
        page.evaluate("location.hash='#shoppen'")
        page.wait_for_timeout(200)
        check(f'{tag} hashchange #shoppen', page.is_checked('#om-f-shoppen-steden'))
        # arrangementen zonder prijs, links naar arrangementpagina's
        ak = page.eval_on_selector_all('.om-ak__knop', 'els=>els.map(e=>e.getAttribute("href"))')
        check(f'{tag} drie arrangementkaarten naar de arrangementpagina', len(ak) == 3 and all(h.startswith('/') for h in ak), ak)
    else:
        # icoontegels en meer-blok
        check(f'{tag} vier icoontegels', page.locator('.om-icotegel').count() == 4)
        meer = page.eval_on_selector_all('.om-meer__kaart', 'els=>els.map(e=>e.getAttribute("href"))')
        andere = [L['url-' + c] for c in CATS if c != sleutel]
        check(f'{tag} meer-blok naar de vier andere categorieen', sorted(meer) == sorted(andere), meer)
        if sleutel == 'golf':
            n = page.locator('.om-baan').count()
            check(f'{tag} baankaarten', n >= 1)
            if n > 1:
                page.locator('#uitjes').scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                t0 = page.inner_text('[data-om-teller]')
                check(f'{tag} teller 01 / 0{n}', t0 == f'01 / {n:02d}', t0)
                page.locator('[data-om-stap="1"]').click()
                page.wait_for_timeout(900)
                t1 = page.inner_text('[data-om-teller]')
                check(f'{tag} pijl rechts -> 02', t1.startswith('02'), t1)
                page.focus('[data-om-spoor]')
                page.keyboard.press('ArrowLeft')
                page.wait_for_timeout(900)
                check(f'{tag} pijltjestoets links -> 01', page.inner_text('[data-om-teller]').startswith('01'))
                check(f'{tag} geen lus (geen klonen)', page.locator('.om-baan[data-kloon]').count() == 0)
            else:
                check(f'{tag} bij 1 baan geen teller', page.locator('[data-om-nav]').count() == 0)
            # vergelijkingstabel
            vgl = page.inner_text('.om-vgl')
            check(f'{tag} vergelijkingstabel zonder greenfee-prijs', page.locator('.om-vgl').count() == 1 and '€' not in vgl)
            if w < 768:
                info = page.evaluate("(()=>{var t=document.querySelector('.om-vgl__tabel');var l=document.querySelector('.om-vgl__labels');return [t.scrollWidth>t.clientWidth,getComputedStyle(l).position]})()")
                check(f'{tag} tabel scrollt, labelkolom sticky', info == [True, 'sticky'], info)
        elif page.locator('#uitjes').count():
            # reiswijzefilter + lege melding
            for m_ in ['alle'] + MODES:
                page.locator(f'label[for="om-t-{m_}"]').click()
                kl = page.eval_on_selector_all('.om-raster__grid .om-kaart', 'els=>els.map(e=>[e.className,getComputedStyle(e).display!=="none"])')
                verwacht = [k for k, z in kl if m_ == 'alle' or f'mode-{m_}' in k]
                zicht = [k for k, z in kl if z]
                leeg = zichtbaar_aantal(page, '.om-leeg') == 1
                check(f'{tag} reiswijze {m_}: {len(verwacht)} kaarten', zicht == verwacht and leeg == (not verwacht), f'{len(zicht)}, leeg {leeg}')
            page.locator('label[for="om-t-alle"]').click()
            check(f'{tag} kaarten alle van categorie {sleutel}',
                  all(f'cat-{sleutel}' in k for k in page.eval_on_selector_all('.om-raster__grid .om-kaart', 'els=>els.map(e=>e.className)')))
        if d.get('conversie') == 'arr':
            a = json.load(open(os.path.join(BASE, 'translations', d['arr-bron'] + '-nl.json'), encoding='utf-8'))
            code = a['VOUCHER']
            knop = page.locator('.om-carr a.mews-open[data-voucher]')
            check(f'{tag} arrangementknop met code {code}', knop.count() == 1 and knop.get_attribute('data-voucher') == code
                  and f'mewsVoucherCode={code}' in knop.get_attribute('href'))
            if code in KAL and taal in ('nl', 'de'):
                knop.scroll_into_view_if_needed()
                knop.click()
                page.wait_for_timeout(1200)
                check(f'{tag} arrangementknop opent de prijskalender', page.evaluate("!!document.querySelector('dialog.ark[open]')"))
                if SHOT:
                    page.screenshot(path=os.path.join(SHOT, f'{pagina}-{w}-kalender.png'))
                page.keyboard.press('Escape')
            check(f'{tag} tekstlink naar de arrangementpagina', page.locator('.om-carr a.al-intro__link').get_attribute('href').startswith('/'))

    check(f'{tag} geen consolefouten', not console, console[:3])
    check(f'{tag} geen 404 (foto\'s, bestanden)', not kapot, kapot[:3])
    if api:
        let.append(f'{tag} onverwachte /api-aanroepen: {api[:3]}')
    if SHOT:
        page.goto(f'{BASIS}/{pagina}.html', wait_until='networkidle')
        page.evaluate("var c=document.getElementById('cookieBanner');c&&c.remove()")
        page.evaluate("""async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}window.scrollTo(0,0)}""")
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(SHOT, f'{pagina}-{w}.png'), full_page=True)
    ctx.close()


def tegels_tellen(b):
    """Aantal kaarten per categoriepagina (golf: banen) = verwachte telling op de overzichtstegels, per taal."""
    return {t: tegels_tellen_taal(b, '' if t == 'nl' else '-' + t) for t in TALEN}


def tegels_tellen_taal(b, achter):
    uit = {}
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()
    page.route('**/api/**', lambda r: r.fulfill(status=204, body=''))
    for c in CATS:
        pad = os.path.join(BASE, f'omgeving-{c}-v2{achter}.html')
        if not os.path.exists(pad):
            continue
        page.goto(f'{BASIS}/omgeving-{c}-v2{achter}.html', wait_until='domcontentloaded')
        uit[c] = page.locator('.om-baan').count() if c == 'golf' else page.locator('.om-raster__grid .om-kaart').count()
    ctx.close()
    return uit


with sync_playwright() as p:
    b = p.chromium.launch()
    if SHOT:
        os.makedirs(SHOT, exist_ok=True)
    verwachting = tegels_tellen(b)
    print('kaarten per categoriepagina:', verwachting)
    for pg in PAGINAS:
        for w in BREEDTES:
            test_pagina(b, pg, w, verwachting)
    b.close()

for x in let:
    print('  let op', x)
print(f'\n{len(goed)} geslaagd, {len(fout)} gefaald')
sys.exit(1 if fout else 0)
