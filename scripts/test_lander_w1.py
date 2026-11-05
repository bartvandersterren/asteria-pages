#!/usr/bin/env python3
"""Playwright-test voor de lander W1 (verblijfsverjaardag-v2).

Gebruik:
  python3 -m http.server 8765        # in de repo-root, in een tweede terminal
  python3 scripts/test_lander_w1.py [basis-url] [--schermafdruk map]

Standaard basis-url: http://localhost:8765/verblijfsverjaardag-v2.html
Checks (1440 en 390): geen horizontale overloop, boekbalk (voucher, datums, reisgezelschap naar
Mews-widget of URL-fallback), kamerslider (teller 1 van 8, pijlen, lus), Bekijk kamer-pop-up
met data-room, Boek nu op een kamerkaart (showRates(kamer) + open() met voucher), Wellness-/Restaurant-pop-up uit de tegelstrook (titel, link, foto's, past in beeld, Escape/kruisje/
achtergrond sluiten, focus terug), reviewmuur (4 kolommen op 1440, 1 op 390, pauze bij hover, statisch bij
prefers-reduced-motion), eerste FAQ open, onderbalk na de hero op 390, uitklaptab (>= 720: na de hero,
weg bij 7a, open/Escape/buiten/sluitknop, Mews met voucher; niet op 390), overloop ook 1100/800, geen consolefouten.

Variant v3 (zijkaart):  python3 scripts/test_lander_w1.py http://localhost:8765/verblijfsverjaardag.html --v3   (v3 is sinds 14 okt de live /verblijfsverjaardag)
In plaats van de uitklaptab-checks: geen tab in de DOM, kaart naast de tegels (1440 en 1100), sticky in beeld
midden kamerslider, weg en zonder overlap bij de reviewmuur, knop opent Mews met JUBILEUM, op 800 als blok na 3a,
op 390 geen kaart; overloop ook 1280/1100/1024/800.

Flow-landers (zelfde sjabloon als v3):  ... http://localhost:8765/bedankt.html --v3 --voucher BEDANKT
(--voucher, standaard JUBILEUM, is de code die de Mews-knoppen en de boekbalk moeten meegeven; bij een andere
code dan JUBILEUM checkt de test ook dat JUBILEUM en 'verblijfsverjaardag' niet in de zichtbare tekst staan.)

Arrangementen (blokken zijkaart + arrangement):
  ... http://localhost:8765/najaarsarrangement.html --v3 --voucher NAJAAR2D --arrangement "€ 128,50"
Extra: robots noindex, alle Mews-links met de voucher, geen oude config bee2f902 in de bron, prijs zichtbaar in de
zijkaart (1440) en in de onderbalk (390). Kamerslider-checks volgen het aantal kamers op de pagina (8 of minder);
vanaf 3 kamers de slider met lus (klonen), bij 1-2 het raster. Inbegrepen-blok: paneel loopt links tot de schermrand,
fotoslider met 4-6 dia's, bolletjes en pijlen (pijlklik schuift een dia). Zondagblok (ontwerp a9): ivoren paneel met kop,
2 kaarten en voetnoot erin, pil in de zondagkaart, even breed (een kolom op 390), zondagprijs met doorgestreepte gewone
prijs, geen keuzeschakelaar (ook niet met ?zv=). Ook interessant (o2): 3 kaarten als link, foto over de volle kaart,
ivoren sectie, geen overloop op 390. Waarom Asteria: wiel met 6 echte punten en 8 klonen, pijlklik verandert --active en
de foto. FAQ: 4 tot 8 vragen, eerste open. Zondagblok alleen als de pagina het heeft (ZV_TOON); zonder: geen blok, geen
zondagregel in zij- en telefoonkaart, geen zondag-FAQ. Boekbalk: actiecode volledig zichtbaar (ook een code van 14 tekens),
vertrek = aankomst + data-nachten (ARR_NACHTEN, standaard 1), widget krijgt N nachten ook als het vertrek te kort stond.
De prijskalender (arrangement-kalender.js) staat in deze test uit (eigen test: scripts/test_arr_kalender.py).
Met --schermafdruk ook: kamerslider na twee pijlklikken, inbegrepen-blok, zondagblok en het wiel in twee standen.

Algemene hotellander (blok 'hotel', zonder actiecode; hotel-venray-v2):
  ... http://localhost:8765/hotel-venray-v2.html --hotel [--schermafdruk map]
Telefoon (blok 'boekkaart'): staging-boekkaart over de hero (maten zoals de staging), periode/reisgezelschap/kamertype -> Mews.
Met --hotel: voucher leeg (geen setVoucherCode, geen mewsVoucherCode/data-voucher in de links, geen actiecodeveld),
geen tegelstrook, geen uitklaptab en geen zijkaart; ster-split aanwezig; blokvolgorde kamers > faciliteiten > omgeving >
arrangementen > reviews > FAQ > slot; faciliteiten = tekstkaart + 5 tegels (Wellness/Restaurant openen de faciliteit-pop-up,
dezelfde pop-upchecks als de tegelstrook), omgeving = blok van de staging-homepage (3-6 plekken, hover/scroll wisselt foto,
Bekijk = pop-up met Mews-knop, Route plannen naar Google Maps en fotoregel), herokop zoals de staging, arrangementkaarten naar bestaande lander-w1-pagina's
(visit.asteria.nl, bestand in de repo), geen prijzen in die blokken; tags GA4 + Google Ads zoals hotel-venray.html. Met herovideo (blok 'video'): speelt
af op 1440 en 390 (zelfde liggende bron als de staging), dekt de hero onder de overlay; reduced motion = alleen de foto.

Upgradeblok A · Ladder-slider (blok 3a-variant 'ladder', aan via UPGRADE_LADDER in de JSON: bedankt en gemist):
  ... http://localhost:8765/bedankt.html --v3 --voucher BEDANKT --ladder
Met --ladder: blok aanwezig (ster-split weg, kop blijft), teller 1 van 5, beginstand (vorige uit), volgende/vorige,
geen lus aan het eind (volgende uit), streepjes, pijltjestoetsen, swipe (scrollpositie), alleen de actieve stap voor
schermlezers, kaarten passen in de kolom (1440: links van de zijkaart; 390: onder elkaar). Zonder --ladder: blok afwezig.

Cadeaublok (blok 3a-variant 'cadeau', aan via CADEAU_ITEMS in de JSON, welkom, sinds 14 okt op /welkom):
  ... http://localhost:8765/welkom.html --v3 --voucher WELKOM --cadeau
Met --cadeau: blok aanwezig (ster-split weg, ster en kop blijven), 3 kaarten met badge, voetregel, geen knop of link in het
blok, kaarten passen in de kolom zonder overloop (>= 720: naast elkaar, >= 1024 links van de zijkaart; 390: onder elkaar,
foto links). Zonder --cadeau: blok afwezig.
"""
import sys, json
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
shotdir = None
V3 = '--v3' in args
if V3: args.remove('--v3')
LADDER = '--ladder' in args
LADDER_N = 5   # stappen in het upgradeblok: Comfort > Royale > Deluxe > Junior Suite > Suite > Bruidssuite
if LADDER: args.remove('--ladder')
CADEAU = '--cadeau' in args
if CADEAU: args.remove('--cadeau')
HOTEL = '--hotel' in args
if HOTEL: args.remove('--hotel')
GESLOTEN = HOTEL   # hotel-venray-v2: inhoud zoals de gesloten lander (geen links naar asteria.nl, pop-upknop = Mews)
# Spiegelstand (GESLOTEN_LANDER: "spiegel", sinds 3 nov 2026 op hotel-venray-v2): kop en voet volledig zoals de staging, alle
# menu- en voetlinks naar de spiegel van de staging op visit.asteria.nl (translations/spiegel-links.json).
SPIEGEL = HOTEL
VOUCHER = '' if HOTEL else 'JUBILEUM'
if '--voucher' in args:
    i = args.index('--voucher'); VOUCHER = args[i + 1]; del args[i:i + 2]
PRIJS = None
if '--arrangement' in args:
    i = args.index('--arrangement'); PRIJS = args[i + 1]; del args[i:i + 2]
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else 'http://localhost:8765/verblijfsverjaardag-v2.html'
NAAM = URL.rstrip('/').rsplit('/', 1)[-1].replace('.html', '')
fouten, resultaten = [], []
# Ankers voor de zijkaart-checks: flow-landers meten tegen de tegelstrook (2a) en attentie (3a); de arrangementpagina
# heeft geen tegelstrook en meet tegen 'Dit is inbegrepen' (.ar-inb) en het zondagblok (.ar-zv).
# __na is een selectorlijst: querySelector geeft het eerste blok na 'inbegrepen' (zondagblok, anders Waarom Asteria, anders kamers).
ANKERS = ("window.__anker='.ar-inb .wrap';window.__ankerSec='.ar-inb';window.__voor='.ar-inb';window.__na='.ar-zv, .ar-waarom, .b4b';window.__arr=true;"
          if PRIJS else
          "window.__anker='.b3a .wrap';window.__ankerSec='.b3a';window.__voor='.b3a';window.__na='.b4b';window.__arr=false;window.__trust=true;"
          if HOTEL else
          "window.__anker='.b2a-strook';window.__ankerSec='.b2a';window.__voor='.b3a';window.__na='.b4b';window.__arr=false;")

FAC = '.ho-fac' if HOTEL else '.b2a-strook'
FAC_TEGEL = '.ho-fac-tegel' if HOTEL else '.b2a-tegel'

def vc():
    """Verwachte setVoucherCode-aanroep in de gestubde Mews-API (zonder actiecode: geen)."""
    return ['v:' + VOUCHER] if VOUCHER else []

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def cadeau_layout(pg, w):
    """Cadeaublok: 3 kaarten binnen de rij, geen overloop; >= 720 naast elkaar (>= 1024 links van de zijkaart), < 720 onder elkaar met de foto links."""
    pg.evaluate("window.scrollTo(0, document.querySelector('#attentie').getBoundingClientRect().top + scrollY - 120)"); pg.wait_for_timeout(500)
    m = pg.evaluate("""()=>{const rij=document.querySelector('#attentie .b3c-rij'),r=rij.getBoundingClientRect(),
        k=[...rij.querySelectorAll('.b3c-kaart')],kr=k.map(x=>x.getBoundingClientRect()),
        f=k.map(x=>x.querySelector('.b3l-foto').getBoundingClientRect()),i=k.map(x=>x.querySelector('.b3l-inhoud').getBoundingClientRect()),
        z=document.querySelector('.lp-zone-kant .b1k-kaart--vast'),zr=z?z.getBoundingClientRect():null;
        return {over:Math.max(rij.scrollWidth-rij.clientWidth,...k.map(x=>x.scrollWidth-x.clientWidth)),
          inRij:kr.every(q=>q.left>=r.left-1&&q.right<=r.right+1),
          naast:kr[1].left>kr[0].right&&kr[2].left>kr[1].right&&Math.abs(kr[0].top-kr[2].top)<2,
          onder:kr[1].top>=kr[0].bottom&&kr[2].top>=kr[1].bottom, fotoLinks:f.every((q,j)=>q.right<=i[j].left+1),
          zijL:zr&&zr.width&&getComputedStyle(z).position==='sticky'?Math.round(zr.left):null, kR:Math.round(Math.max(...kr.map(q=>q.right))),
          L:Math.round(r.left), R:Math.round(r.right)}}""")
    if w >= 720:
        ok = m['over'] <= 0 and m['inRij'] and m['naast'] and (w < 1024 or (m['zijL'] is not None and m['kR'] < m['zijL']))
        check(f'[{w}] cadeaukaarten naast elkaar in de kolom' + (', links van de zijkaart' if w >= 1024 else '') + ', geen overloop', ok, str(m))
    else:
        check(f'[{w}] cadeaukaarten onder elkaar, foto links, geen overloop', m['over'] <= 0 and m['inRij'] and m['onder'] and m['fotoLinks'], str(m))
    return m

def nieuwe_pagina(b, w, h, mob, rustig=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob,
                        reduced_motion='reduce' if rustig else 'no-preference')
    ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
    # scratchcard-pop-up (blok 'scratchcard') uit voor deze test; eigen test: scripts/test_scratchcard_2026.py
    ctx.add_init_script("try{localStorage.setItem('ec_converted','1')}catch(e){}")
    ctx.route('**/api/track', lambda r: r.fulfill(status=204, body=''))   # D1-events (analytics-d1.js), lokaal geen Function
    ctx.route('**/api/arr-vanaf*', lambda r: r.fulfill(status=200, content_type='application/json', body='{"ok":true,"prijzen":{}}'))   # live vanaf-prijs: eigen test scripts/test_arr_vanaf_pagina.py
    ctx.add_init_script(ANKERS)
    if PRIJS:
        # De prijskalender (arrangement-kalender.js) vangt de boekknoppen en de boekbalk af; die heeft een eigen test
        # (scripts/test_arr_kalender.py). Hier staat hij uit, zodat de checks de onderliggende Mews-flow zien.
        ctx.route('**/arrangement-kalender.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))
    pg = ctx.new_page()
    pg._fouten = []
    pg.on('console', lambda m: pg._fouten.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: pg._fouten.append(str(e)))
    pg.goto(URL, wait_until='networkidle')
    pg.wait_for_timeout(600)
    return ctx, pg

with sync_playwright() as p:
    b = p.chromium.launch()
    if PRIJS:
        import urllib.request
        bron = urllib.request.urlopen(URL).read().decode('utf-8')
        check('[bron] robots noindex, follow', '<meta name="robots" content="noindex, follow">' in bron)
        check('[bron] geen oude Mews-config bee2f902', 'bee2f902' not in bron)
        nrev = bron.count('<article class="kaart b5a-kaart">')
        check('[bron] reviewmuur met 8 of 12 kaarten', nrev in (8, 12), str(nrev))
        check('[bron] één reviewgetal (2.280) in badge, zijkaart en reviewkop, geen 2.200',
              '2.200' not in bron and bron.count('2.280 reviews') >= 3, str(bron.count('2.280 reviews')))
        check('[bron] geen tegelstrook (b2a)', 'class="sec b2a"' not in bron)
        check('[bron] prijskalender aanwezig (dialoog #ar-kal + arrangement-kalender.js/.css)',
              'id="ar-kal"' in bron and 'arrangement-kalender.js' in bron and 'arrangement-kalender.css' in bron and '{{KAL_' not in bron)
        ctx, pg = nieuwe_pagina(b, 1440, 900, False)
        links = pg.evaluate("[...document.querySelectorAll('a[href*=\"app.mews.com\"]')].map(a=>a.getAttribute('href'))")
        zonder = [l for l in links if 'mewsVoucherCode=' + VOUCHER not in l or '6dc9094c-76e3-4fd8-83a7-af1d00ffc556' not in l]
        check(f'[bron] alle {len(links)} Mews-links op config 6dc9094c met {VOUCHER}', links and not zonder, '; '.join(zonder)[:300])
        kamers = pg.evaluate("[...document.querySelectorAll('.b4b-kaart:not([data-kloon]) .b4b-knoppen a.mews-open')].map(a=>a.getAttribute('href'))")
        check('[bron] kamerknoppen met mewsRoom en mewsRoute=rooms', kamers and all('mewsRoom=' in k and 'mewsRoute=rooms' in k for k in kamers), str(len(kamers)))
        ctx.close()
    if HOTEL:
        import urllib.request, re as _re, os as _os
        bron = urllib.request.urlopen(URL).read().decode('utf-8')
        check('[bron] robots noindex, follow', '<meta name="robots" content="noindex, follow">' in bron)
        check('[bron] geen oude Mews-config bee2f902', 'bee2f902' not in bron)
        check('[bron] tags zoals hotel-venray.html: GA4, Google Ads, conversielabel, linker accept_incoming',
              all(t in bron for t in ("gtag/js?id=", "gtag('config', 'G-DPCP945DCG', { linker: { domains: ['asteria.nl', 'visit.asteria.nl'] } })",
                                       "gtag('config', 'AW-998609513')", "AW-998609513/t8vbCLm6i7IcEOmkltwD", "gtag('set', 'linker', { accept_incoming: true })")))
        hrefs = _re.findall(r'href="(https://app\.mews\.com/[^"]*)"', bron)
        check(f'[bron] alle {len(hrefs)} Mews-links op 6dc9094c, zonder mewsVoucherCode', hrefs and all('6dc9094c-76e3-4fd8-83a7-af1d00ffc556' in h and 'mewsVoucherCode' not in h for h in hrefs))
        check('[bron] geen data-voucher, geen actiecodeveld, geen "met code"', 'data-voucher' not in bron and 'id="bb-code"' not in bron and ' met code' not in bron)
        check('[bron] geen tegelstrook, uitklaptab of zijkaart', 'class="sec b2a"' not in bron and 'b1k-uitklap' not in bron and 'lp-zone-kant' not in bron)
        check('[bron] geen onvervangen {{KEY}}-markers', not _re.findall(r'\{\{[A-Z_0-9]+\}\}', bron))
        hrefs_alle = _re.findall(r'href="([^"]*)"', bron)
        mag = lambda h: (h.startswith(('tel:', 'mailto:', '/', '#', 'https://visit.asteria.nl/', 'https://app.mews.com/distributor/6dc9094c',
                                       'https://www.google.com/maps/'))
                         or not h.startswith('http') or 'asteria.nl' not in h or h in ('https://www.asteria.nl/privacy', 'https://www.asteria.nl/algemene-voorwaarden'))
        fout = [h for h in hrefs_alle if not mag(h)]
        check('[bron] geen links naar asteria.nl behalve privacy en algemene voorwaarden', not fout, ', '.join(fout))
        # omgevingsblok: pop-updata zonder asteria.nl-links; Route plannen alleen naar Google Maps (allowlist)
        _fd = json.loads(_re.search(r'<script type="application/json" id="lp-facdata">(.*?)</script>', bron, _re.S).group(1))
        _omg = {k: v for k, v in _fd.items() if k.startswith('omg-')}
        _routes = [v['route'] for v in _omg.values() if v.get('route')]
        check('[bron] omgeving-pop-ups: geen asteria.nl-link, Route plannen alleen naar Google Maps (vanaf Maasheseweg 80a), fotoregel bij Commons-foto\'s',
              bool(_omg) and all(not v.get('link') for v in _omg.values()) and len(_routes) >= 4
              and all(r.startswith('https://www.google.com/maps/dir/?api=1&origin=Hotel+Asteria%2C+Maasheseweg+80a') for r in _routes)
              and all(v.get('credit') for k, v in _omg.items() if k != 'omg-fietsen'), str(_routes)[:300])
        _tekst = ' '.join(v['tekst'] + ' '.join(v['chips']) for v in _omg.values())
        check('[bron] omgeving-pop-ups: geen &, geen em- of en-dash', '&' not in _tekst and '—' not in _tekst and '–' not in _tekst)
        jur = _re.findall(r'<a href="https://www\.asteria\.nl/(privacy|algemene-voorwaarden)" target="_blank" rel="noopener">', bron)
        check('[bron] juridische links (voet + cookiemelding) openen in een nieuw tabblad (rel noopener)', set(jur) == {'algemene-voorwaarden', 'privacy'}, str(jur))
        if SPIEGEL:
            _sl = json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'translations', 'spiegel-links.json'), encoding='utf-8'))
            _pg = _sl['paginas']; _ovz = _sl['arrangementenoverzicht']
            _spiegel = {_pg[v['sleutel']] for v in _sl['spiegel'].values()} | {_ovz, _pg['home']}
            # eigen kamerdetailpagina's (kamer-w1, build.py kamers/<slug>) voor de kamers zonder staging-pagina
            _kamer_w1 = {_pg[k] for k in ('kamer-comfort-3', 'kamer-mindervalide', 'kamer-royale', 'kamer-suite', 'kamer-bruidssuite')}
            _spiegel |= _kamer_w1
            _kop = bron[bron.index('<header'):bron.index('</header>')]
            _drawer = bron[bron.index('<aside class="nav-drawer"'):bron.index('</aside>')]
            _voet = bron[bron.index('<footer'):bron.index('</footer>')]
            _kl = lambda deel: [h for h in _re.findall(r'href="([^"]*)"', deel) if not h.startswith(('tel:', 'mailto:', 'https://app.mews.com/distributor/6dc9094c'))]
            _menu = {'Kamers &amp; suites': _pg['kamers'], 'Faciliteiten': _pg['faciliteiten'], 'Wellness &amp; fitness': _pg['wellnessfaciliteiten'],
                     'Arrangementen': _ovz, 'Omgeving': _pg['omgeving'], 'Restaurant': _pg['restaurant'], 'Wellness': _pg['wellness'],
                     'Ons verhaal': _pg['over-ons'], 'Contact': _pg['contact']}
            _menu_ok = all(f'<li><a href="{u}">{t}</a></li>' in _kop and f'<li><a href="{u}">{t}</a></li>' in _drawer for t, u in _menu.items())
            check('[bron] spiegel: kop met utility-balk, menu (Hotel en Over ons met submenu), hamburger en mobiel menu; logo naar /hotel-venray-v2',
                  'class="utility-bar"' in _kop and 'class="nav-links"' in _kop and _kop.count('class="has-sub"') == 2 and 'nav-hamburger' in _kop
                  and 'id="nav-drawer"' in bron and _drawer.count('class="has-sub"') == 2 and _menu_ok
                  and '<a href="/hotel-venray-v2" class="logo"' in bron and 'nav-cta mews-open' in bron and 'langswitch' not in _kop)
            _zalen = [x for x in (_kop + _drawer + _voet).split('\n') if _re.search(r'zalen|vergader|feesten|vacature|veelgestelde', x, _re.I)]
            check('[bron] spiegel: geen Zalen & feesten, Vergaderen, FAQ of Werken bij in kop, drawer en voet', not _zalen, str(_zalen)[:200])
            _alle = _kl(_kop) + _kl(_drawer) + _kl(_voet)
            _buiten = [h for h in _alle if h not in _spiegel and h not in ('https://www.asteria.nl/privacy', 'https://www.asteria.nl/algemene-voorwaarden')
                       and not h.startswith(('https://maps.google.com/', 'https://www.facebook.com/', 'https://www.instagram.com/', 'https://www.linkedin.com/'))]
            check(f'[bron] spiegel: alle {len(_alle)} kop-, drawer- en voetlinks naar spiegeladressen (of Mews/tel/mail/juridisch/kaart/social)', not _buiten, str(_buiten))
            check('[bron] spiegel: voet met kolommen Verblijf/Bij ons/Contact en socials; Comfort/Deluxe/Bruidssuite naar de detailpagina, Junior suite naar Mews met kamer',
                  'footer__socials' in _voet and all(f'<h3>{k}</h3>' in _voet for k in ('Verblijf', 'Bij ons', 'Contact'))
                  and f'<a href="{_pg["kamer-comfort"]}">Comfort kamer</a>' in _voet and f'<a href="{_pg["kamer-deluxe"]}">Deluxe kamer</a>' in _voet
                  and f'<a href="{_pg["kamer-bruidssuite"]}">Bruidssuite</a>' in _voet and 'data-room="27ea8deb-ded5-4856-8fdd-af1d00ffc315">Junior suite' in _voet)
            _bk = dict(_re.findall(r'<a class="btn btn-secondary btn--klein" href="([^"]*)" aria-label="Bekijk de ([^"]*)">Bekijk kamer</a>', bron))
            check('[bron] spiegel: kamerkaarten Bekijk kamer = link naar de detailpagina (7 kamers), Junior Suite houdt de pop-up',
                  len(_bk) == 7 and set(_bk) == {_pg['kamer-comfort'], _pg['kamer-deluxe']} | _kamer_w1
                  and 'data-kamer="junior-suite" aria-haspopup="dialog"' in bron, str(_bk))
            _ovk = {t: _re.findall(r'<a class="btn [^"]*" href="([^"]*)">' + t + '</a>', bron) for t in ('Alle arrangementen', 'Bekijk alle kamers', 'Alle faciliteiten', 'Plan een dag in de buurt', 'Neem contact op')}
            check('[bron] spiegel: overzichtsknoppen Alle arrangementen/Bekijk alle kamers/Alle faciliteiten/Plan een dag in de buurt/Neem contact op naar de spiegel',
                  _ovk == {'Alle arrangementen': [_ovz], 'Bekijk alle kamers': [_pg['kamers']], 'Alle faciliteiten': [_pg['faciliteiten']],
                           'Plan een dag in de buurt': [_pg['omgeving']], 'Neem contact op': [_pg['contact']]}, str(_ovk))
            check('[bron] spiegel: faciliteit-pop-ups met Meer informatie naar de spiegel (info), knop blijft Mews',
                  all(v.get('info') in _spiegel and not v.get('link') for v in _fd.values()) and _fd['wellness']['info'] == _pg['wellness'], str({k: v.get('info') for k, v in _fd.items()}))
        else:
            check('[bron] kop zonder menu, utility-balk, hamburger en mobiel menu; logo naar /hotel-venray-v2',
                  'class="nav-links"' not in bron and 'class="utility-bar"' not in bron and 'nav-hamburger' not in bron and 'id="nav-drawer"' not in bron
                  and '<a href="/hotel-venray-v2" class="logo"' in bron and 'class="nav-phone"' in bron and 'nav-cta mews-open' in bron)
            check('[bron] voet alleen logo, adres, contact en juridisch (geen kolommen, geen socials)',
                  'footer__socials' not in bron and '<h3>Verblijf</h3>' not in bron and '<h3>Bij ons</h3>' not in bron and '0478 511 466' in bron and 'Maasheseweg 80a' in bron)
        kamerp = [h for h in hrefs_alle if h.rstrip('/').rsplit('/', 1)[-1] in ('kamertypes', 'comfort-kamer', 'comfort-kamer-3-personen', 'mindervalide-kamer',
                                                                           'royale-kamer', 'deluxe-kamer', 'junior-suite', 'suite', 'bruidssuite')
                  and not (SPIEGEL and h in _spiegel)]
        check('[bron] geen links naar /kamertypes of de oude kamerpagina\'s (wel de spiegel), geen kamerpaginalink in de pop-up',
              not kamerp and 'class="lp-pop__link" href="/"' not in bron, str(kamerp))
        if not SPIEGEL:
            # OVERZICHT_ARR_URL is leeg tot /arrangementen-v2 live staat (PR #180); dan weer '/arrangementen-v2' verwachten.
            check('[bron] geen Alle arrangementen en geen Bekijk alle kamers zolang de overzichten niet live zijn (OVERZICHT_*_URL leeg)',
                  'Alle arrangementen' not in bron and 'Bekijk alle kamers' not in bron and 'href=""' not in bron)
        check('[bron] kamerknoppen heten Bekijk beschikbaarheid (8 kaarten + pop-up), met data-room',
              len(_re.findall(r'data-room="[^"]+"[^>]*>Bekijk beschikbaarheid</a>', bron)) >= 8 and '>Boek deze kamer<' not in bron and '>Boek nu</a><button' not in bron)
        arr = _re.findall(r'<a class="ho-arr-kaart" href="https://visit\.asteria\.nl/([a-z0-9-]+)"', bron)
        check(f'[bron] {len(arr)} arrangementkaarten naar bestaande pagina\'s', 3 <= len(arr) <= 8 and all(_os.path.exists(a + '.html') for a in arr), ', '.join(arr))
    for w in ((1280, 1100, 1024, 800) if V3 else (1100, 800)):
        ctx, pg = nieuwe_pagina(b, w, 900, False)
        pg.evaluate("window.scrollTo(0, document.querySelector('.b4b').offsetTop)"); pg.wait_for_timeout(800)
        if V3:
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'[{w}] geen horizontale overloop', sw <= w, f'scrollWidth {sw}')
            if w == 1100:
                pg.evaluate("window.scrollTo(0, document.querySelector(window.__ankerSec).getBoundingClientRect().top + scrollY - 150)"); pg.wait_for_timeout(700)
                z = pg.evaluate("""()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect(),s=document.querySelector(window.__anker).getBoundingClientRect();
                    return {kl:k.left,kr:k.right,kt:k.top,sr:s.right,st:s.top,sb:s.bottom}}""")
                check(f'[{w}] kaart naast de tegels', z['kl'] > z['sr'] and z['kr'] <= w and z['kt'] < z['sb'], str(z))
            if w == 800:
                z = pg.evaluate("""()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast'),r=k.getBoundingClientRect(),a=document.querySelector(window.__voor).getBoundingClientRect(),
                    m=document.querySelector(window.__na).getBoundingClientRect();return {w:r.width,pos:getComputedStyle(k).position,na3a:r.top+scrollY>=a.bottom+scrollY-1,voor4b:r.bottom<=m.top+1}}""")
                check(f'[{w}] kaart als blok tussen ' + ('inbegrepen en zondagblok' if PRIJS else 'attentie en kamers'), z['w'] > 0 and z['pos'] != 'sticky' and z['na3a'] and z['voor4b'], str(z))
        elif HOTEL:
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'[{w}] geen horizontale overloop', sw <= w, f'scrollWidth {sw}')
            fz = pg.evaluate("""(()=>{const g=document.querySelector('.ho-fac-grid'),k=[...g.children].map(x=>x.getBoundingClientRect());
                return {over:g.scrollWidth-g.clientWidth,binnen:k.every(r=>r.right<=g.getBoundingClientRect().right+1)}})()""")
            check(f'[{w}] faciliteitenmozaiek past in de kolom', fz['over'] <= 0 and fz['binnen'], str(fz))
        else:
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(700)
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'[{w}] geen horizontale overloop (tab + open kaart)', sw <= w, f'scrollWidth {sw}')
        if CADEAU:
            cadeau_layout(pg, w)
        eigen = [f for f in pg._fouten if 'mews' not in f.lower()]
        check(f'[{w}] geen consolefouten (eigen code)', not eigen, '; '.join(eigen)[:300])
        ctx.close()
    for w, h, mob in [(1440, 900, False), (390, 844, True)]:
        tag = f'[{w}]'
        ctx, pg = nieuwe_pagina(b, w, h, mob)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        check(f'{tag} geen horizontale overloop', sw <= w, f'scrollWidth {sw}')
        if VOUCHER != 'JUBILEUM':
            tekst = pg.evaluate('document.body.innerText')
            rest = [t for t in ('JUBILEUM', 'verblijfsverjaardag', 'Verblijfsverjaardag') if t in tekst]
            check(f'{tag} geen resten van de verblijfsverjaardag in de tekst', not rest, ', '.join(rest))
            if VOUCHER: check(f'{tag} code {VOUCHER} in de tekst', VOUCHER in tekst)

        # FAQ
        open_ = pg.evaluate("[...document.querySelectorAll('.b6c details')].map(d=>d.open)")
        check(f'{tag} eerste FAQ open, rest dicht', open_[0] and not any(open_[1:]), str(open_))

        # upgradeblok A · Ladder-slider
        if not LADDER:
            if CADEAU or PRIJS:   # cadeaublok of arrangement: geen ster-split
                check(f'{tag} geen upgradeblok (ladder)', pg.locator('.b3l').count() == 0)
            else:
                check(f'{tag} geen upgradeblok (ladder), ster-split aanwezig', pg.locator('.b3l').count() == 0 and pg.locator('#attentie .b3a-grid').count() == 1)
        else:
            check(f'{tag} upgradeblok aanwezig in #attentie, ster-split weg, kop blijft',
                  pg.locator('#attentie .b3l').count() == 1 and pg.locator('.b3a-grid').count() == 0 and pg.locator('#attentie .b3a-ster').count() == 1
                  and 'de upgrade' in pg.locator('#attentie h2').inner_text() and pg.locator('.b3l-stap').count() == LADDER_N)
            check(f'{tag} upgradeblok zonder boekknop en zonder prijzen',
                  pg.locator('#attentie a, #attentie .mews-open').count() == 0 and '\u20ac' not in pg.locator('#attentie').inner_text())
            pg.locator('#attentie').scroll_into_view_if_needed(); pg.wait_for_timeout(400)
            ls = lambda: pg.evaluate("""()=>{const b=document.querySelector('.b3l'),sp=b.querySelector('.b3l-spoor');
                return {nu:b.querySelector('.b3l-nu').textContent, tot:b.querySelector('.b3l-tel').innerText,
                  vorige:b.querySelector('.b3l-vorige').getAttribute('aria-disabled'), volgende:b.querySelector('.b3l-volgende').getAttribute('aria-disabled'),
                  dot:[...b.querySelectorAll('.b3l-dot')].map((d,i)=>d.classList.contains('is-active')&&d.getAttribute('aria-selected')==='true'?i+1:0).filter(Boolean).join(','),
                  zicht:[...b.querySelectorAll('.b3l-stap')].map((s,i)=>s.hasAttribute('aria-hidden')?0:i+1).filter(Boolean).join(','),
                  pos:Math.round(sp.scrollLeft/sp.clientWidth*100)/100}}""")
            s0 = ls()
            check(f'{tag} ladder beginstand: 1 van {LADDER_N}, vorige uit, volgende aan', s0['nu'] == '1' and str(LADDER_N) in s0['tot'] and s0['vorige'] == 'true'
                  and s0['volgende'] == 'false' and s0['dot'] == '1' and s0['zicht'] == '1' and s0['pos'] == 0, str(s0))
            pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900); s1 = ls()
            check(f'{tag} ladder volgende: 2 van {LADDER_N}, streepje 2, vorige aan', s1['nu'] == '2' and s1['dot'] == '2' and s1['zicht'] == '2'
                  and s1['vorige'] == 'false' and s1['pos'] == 1, str(s1))
            for _ in range(LADDER_N - 3):
                pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900)
            pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900); s3 = ls()
            pg.locator('.b3l-volgende').click(force=True); pg.wait_for_timeout(900); s4 = ls()   # aria-disabled: klik moet niets doen
            check(f'{tag} ladder eindstand: {LADDER_N} van {LADDER_N}, volgende uit, geen lus', s3['nu'] == str(LADDER_N) and s3['volgende'] == 'true'
                  and s4['nu'] == str(LADDER_N) and s4['pos'] == LADDER_N - 1 and s4['zicht'] == str(LADDER_N), f'{s3} / {s4}')
            pg.locator('.b3l-vorige').click(); pg.wait_for_timeout(900); s5 = ls()
            check(f'{tag} ladder vorige: {LADDER_N - 1} van {LADDER_N}, volgende weer aan', s5['nu'] == str(LADDER_N - 1) and s5['volgende'] == 'false'
                  and s5['dot'] == str(LADDER_N - 1), str(s5))
            pg.locator('.b3l-dot').nth(0).click(); pg.wait_for_timeout(1100); s6 = ls()
            check(f'{tag} ladder streepje 1 springt terug naar het begin', s6['nu'] == '1' and s6['vorige'] == 'true' and s6['pos'] == 0, str(s6))
            pg.locator('.b3l-spoor').focus(); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(900); k1 = ls()
            pg.keyboard.press('ArrowLeft'); pg.wait_for_timeout(900); k2 = ls()
            check(f'{tag} ladder pijltjestoetsen (rechts 2, links 1)', (k1['nu'], k2['nu']) == ('2', '1'), f"{k1['nu']},{k2['nu']}")
            pg.evaluate("(()=>{const sp=document.querySelector('.b3l-spoor');sp.scrollTo({left:sp.clientWidth*2,behavior:'auto'})})()"); pg.wait_for_timeout(700); sw2 = ls()
            check(f'{tag} ladder volgt swipe/scroll (stap 3)', sw2['nu'] == '3' and sw2['dot'] == '3', str(sw2))
            m = pg.evaluate("""()=>{const st=[...document.querySelectorAll('.b3l-stap')],sp=document.querySelector('.b3l-spoor').getBoundingClientRect(),
                k=[...document.querySelectorAll('.b3l-stap:nth-child(3) .b3l-kaart')].map(x=>x.getBoundingClientRect()),
                z=document.querySelector('.lp-zone-kant .b1k-kaart--vast'),zr=z?z.getBoundingClientRect():null;
                return {over:st.map(s=>s.scrollWidth-s.clientWidth).reduce((a,b)=>Math.max(a,b)),inSpoor:k.every(r=>r.left>=sp.left-1&&r.right<=sp.right+1),
                  naast:k[1].left>k[0].right, onder:k[1].top>k[0].bottom, zijL:zr&&zr.width?zr.left:null, kR:Math.max(k[0].right,k[1].right)}}""")
            if w >= 1024:
                check(f'{tag} ladderkaarten naast elkaar in de kolom, links van de zijkaart, geen overloop',
                      m['over'] <= 0 and m['inSpoor'] and m['naast'] and m['zijL'] is not None and m['kR'] < m['zijL'], str(m))
            else:
                check(f'{tag} ladderkaarten onder elkaar, geen overloop', m['over'] <= 0 and m['inSpoor'] and m['onder'], str(m))
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)

        # cadeaublok (blok 3a-variant 'cadeau')
        if not CADEAU:
            check(f'{tag} geen cadeaublok', pg.locator('.b3c').count() == 0)
        else:
            check(f'{tag} cadeaublok aanwezig in #attentie, ster-split weg, ster en kop blijven, 3 kaarten',
                  pg.locator('#attentie .b3c').count() == 1 and pg.locator('.b3a-grid').count() == 0 and pg.locator('#attentie .b3a-foto, #attentie .b3a-lijst').count() == 0
                  and pg.locator('#attentie .b3a-ster').count() == 1 and 'het cadeau' in pg.locator('#attentie h2').inner_text()
                  and pg.locator('#attentie .b3c-kaart').count() == 3)
            check(f'{tag} cadeaublok zonder knop of link en zonder prijzen',
                  pg.locator('#attentie a, #attentie button, #attentie .btn, #attentie .mews-open').count() == 0 and '\u20ac' not in pg.locator('#attentie').inner_text())
            pg.locator('#attentie').scroll_into_view_if_needed(); pg.wait_for_timeout(600)
            zicht = pg.evaluate("""()=>[...document.querySelectorAll('#attentie .b3c-kaart')].map(k=>{const p=[...k.querySelectorAll('.b3l-pil')].filter(x=>x.offsetParent);
                return {pil:p.length===1?p[0].innerText.trim():p.length, h3:k.querySelector('h3').innerText, regel:k.querySelector('.b3c-regel').innerText,
                  foto:k.querySelector('img').complete&&k.querySelector('img').naturalWidth>0}})""")
            check(f'{tag} elke kaart: één zichtbare badge (Gratis of Te leen), naam, regel, foto geladen',
                  all(z['pil'].upper() in ('GRATIS', 'TE LEEN') if isinstance(z['pil'], str) else False for z in zicht) and all(z['h3'] and z['regel'] and z['foto'] for z in zicht), str(zicht))
            check(f'{tag} voetregel onder de kaarten', 'eerste verblijf' in pg.locator('#attentie .b3c-voet').inner_text()
                  and pg.evaluate("document.querySelector('#attentie .b3c-voet').getBoundingClientRect().top>=document.querySelector('#attentie .b3c-rij').getBoundingClientRect().bottom"))
            cadeau_layout(pg, w)
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)

        raster = pg.evaluate("!!document.querySelector('.ar-kamers')")
        if raster:
            r = pg.evaluate("""(()=>{const g=document.querySelector('.ar-kamers'),k=[...g.querySelectorAll('.b4b-kaart')].map(x=>x.getBoundingClientRect());
                return {n:k.length,n_attr:+g.dataset.n,strook:!!document.querySelector('.b4b-strook, .b4b-teller, .b4b-dots'),klonen:document.querySelectorAll('[data-kloon]').length,
                  rij:k.every(x=>Math.abs(x.top-k[0].top)<2),peek:k.length>1&&k[1].left<innerWidth&&k[1].right>innerWidth,veeg:g.scrollWidth>g.clientWidth+10,
                  prijs:[...g.querySelectorAll('.ar-kprijs')].length,rand:getComputedStyle(g.querySelector('.ar-kaart-inbegrepen')).boxShadow.includes('199, 110, 78')}})()""")
            check(f'{tag} kamerraster bij {r["n"]} kamers: geen slider, teller, streepjes of klonen', r['n'] <= 2 and r['n'] == r['n_attr'] and not r['strook'] and r['klonen'] == 0, str(r))
            check(f'{tag} prijsregel op elke kamerkaart, inbegrepen kamer met terracotta rand', r['prijs'] == r['n'] and r['rand'], str(r))
            if mob: check(f'{tag} kamerraster veegbaar, volgende kaart piept in beeld', r['veeg'] and r['peek'], str(r))
            else: check(f'{tag} kamers naast elkaar in een rij', r['rij'] and not r['veeg'], str(r))
        else:
            # kamerslider
            tel = lambda: pg.locator('.b4b-nu').inner_text()
            N = pg.evaluate("document.querySelectorAll('.b4b-strook .b4b-kaart:not([data-kloon])').length")
            check(f'{tag} kamerteller start op 1 van {N}', tel() == '1' and f'van {N}' in pg.locator('.b4b-tel').inner_text().lower())
            pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(900)
            t2 = tel()
            pg.locator('.b4b-vorige').click(); pg.wait_for_timeout(900)
            t1 = tel()
            pg.locator('.b4b-vorige').click(); pg.wait_for_timeout(900)
            t8 = tel()
            check(f'{tag} pijlen werken (volgende 2, vorige 1, vorige {N})', (t2, t1, t8) == ('2', '1', str(N)), f'{t2},{t1},{t8}')
            actief = lambda: pg.evaluate("[...document.querySelectorAll('.b4b-dot')].map((d,i)=>d.classList.contains('is-active')?i+1:0).filter(Boolean).join(',')")
            check(f'{tag} streepjes volgen de teller ({N} stuks, actief {N})', pg.locator('.b4b-dot').count() == N and actief() == str(N), actief())
            sd = min(4, N - 1)
            pg.locator('.b4b-dot').nth(sd - 1).click(); pg.wait_for_timeout(1100)
            t4 = tel(); a4 = actief()
            check(f'{tag} klik op streepje {sd} springt naar kamer {sd}', t4 == str(sd) and a4 == str(sd), f'{t4} / {a4}')
            pg.locator('.b4b-dot').nth(N - 1).click(); pg.wait_for_timeout(1100)
            pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(900)
            if shotdir and PRIJS:
                pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(900)
                pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(1100)
                pg.evaluate("window.scrollTo(0, document.querySelector('.b4b').getBoundingClientRect().top + scrollY - (innerWidth < 720 ? 60 : 110))"); pg.wait_for_timeout(600)
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kamers-2klik.png')

        if PRIJS:
            a = pg.evaluate("""(()=>{const q=s=>document.querySelector(s),zv=q('.ar-zv'),wa=q('.ar-waarom'),kant=q('.lp-zone-kant'),an=q('.ar-andere');
                const zk=zv?[...zv.querySelectorAll('.ar-zv-kaart')]:[],zz=zv&&zv.querySelector('.ar-zv-kaart--zondag'),za=zk.find(k=>k!==zz);
                return {zvEr:!!zv,zvRegels:document.querySelectorAll('.ar-zondagregel').length,zv:!!zv&&zv.offsetParent!==null&&!!zz&&!!zz.querySelector('.ar-zv-pil')&&!!zv.querySelector('.ar-zv-noot')&&!!zz.querySelector('s'),
                  zvN:zk.length,zvKop:zv?zv.querySelector('h2').innerText.replace(/\\u00a0/g,' '):'',
                  zvPrijs:zz?zz.querySelector('.ar-zv-prijs b').innerText.replace(/\\u00a0/g,' '):'',zvWas:zz?zz.querySelector('s').innerText.replace(/\\u00a0/g,' '):'',
                  zvW:zz?Math.round(zz.getBoundingClientRect().width):0,zvWa:za?Math.round(za.getBoundingClientRect().width):0,
                  zvPaneel:(()=>{const pn=zv&&zv.querySelector('.ar-zv-paneel');return !!pn&&!!pn.querySelector('h2.ar-zv-kop')&&pn.querySelectorAll('.ar-zv-grid > .ar-zv-kaart').length===2&&!!pn.querySelector('.ar-zv-noot')&&!!(zz&&zz.querySelector('.ar-zv-top .ar-zv-pil'))})(),
                  zvKiezer:!!document.querySelector('.ar-zv-kiezer,.ar-zv-optie,[data-zv-schakel],.ar-zv-zondagknop'),
                  wKop:wa?wa.querySelector('h2').innerText:'',wPunten:wa?wa.querySelectorAll('.ar-wiel-item:not([data-kloon])').length:0,
                  wFoto:wa?(i=>i.complete&&i.naturalWidth>0)(wa.querySelector('.b3a-foto img.is-actief')):false,
                  wKnop:wa?wa.querySelector('.mews-open').dataset.voucher:'',
                  kantFoto:kant?kant.querySelectorAll('img').length:-1,kantPrijs:kant?!!kant.querySelector('.b1k-prijs'):false,
                  andere:an?[...an.querySelectorAll('a.ar-ander')].map(x=>x.getAttribute('href')):[],
                  anVol:an?[...an.querySelectorAll('a.ar-ander')].every(k=>{const i=k.querySelector('.ar-ander-foto img'),r=k.getBoundingClientRect(),f=i&&i.getBoundingClientRect();
                    return !!f&&Math.abs(f.width-r.width)<=2&&Math.abs(f.height-r.height)<=2&&!!k.querySelector('.ar-ander-naam')&&!!k.querySelector('.ar-ander-rond')}):false,
                  anBg:an?getComputedStyle(an).backgroundColor:'',anToon:an?an.dataset.toon:'',
                  anOv:document.documentElement.scrollWidth-innerWidth,
                  chips:document.querySelectorAll('.ar-chips li').length,
                  faq:[...document.querySelectorAll('.b6c summary')].map(s=>s.innerText)}})()""")
            if a['zvEr']:
                check(f'{tag} zondagblok (a9): paneel met kop, 2 kaarten en voetnoot erin, pil in de zondagkaart', a['zvPaneel'])
                check(f'{tag} zondagblok: kop, pil, doorgestreepte prijs, voetnoot', a['zv'] and 'Op zondag' in a['zvKop'] and '20 per kamer' in a['zvKop'], str(a)[:300])
                check(f'{tag} zondagblok: precies 2 kaarten', a['zvN'] == 2, str(a['zvN']))
                check(f'{tag} zondagblok: zondagprijs staat er (lager dan {PRIJS}, die doorgestreept)', a['zvPrijs'].startswith('€') and a['zvPrijs'] != PRIJS and a['zvWas'] == PRIJS, f"{a['zvPrijs']} / {a['zvWas']}")
                if mob:
                    check(f'{tag} zondagblok: een kolom (kaarten even breed)', a['zvW'] > 0 and a['zvW'] == a['zvWa'], f"{a['zvW']} / {a['zvWa']}")
                else:
                    check(f'{tag} zondagblok: twee kaarten naast elkaar, even breed', a['zvW'] > 0 and abs(a['zvW'] - a['zvWa']) <= 1, f"{a['zvW']} / {a['zvWa']}")
            else:
                # ZV_TOON false: geen zondagblok, geen zondagregel in zijkaart of telefoonkaart, geen zondag-FAQ
                check(f'{tag} zonder zondagvoordeel: geen zondagblok, geen zondagregel in de kaarten, geen zondag-FAQ',
                      a['zvN'] == 0 and a['zvRegels'] == 0 and not any('zondag' in q.lower() for q in a['faq']), f"{a['zvN']} / {a['zvRegels']} / {a['faq']}")
            check(f'{tag} zondagblok: geen keuzeschakelaar of oude opties', not a['zvKiezer'])
            # Golfbanen (build-blok 'banen', lijst '_banen' in de JSON): aantal kaarten = lengte van de lijst, anders geen blok
            try:
                with open(f'translations/{NAAM}-nl.json', encoding='utf-8') as fj:
                    BANEN_N = len(json.load(fj).get('_banen') or [])
            except OSError:
                BANEN_N = 0
            pg.evaluate("(()=>{const s=document.querySelector('.ar-banen');if(s){s.scrollIntoView({block:'center'});s.querySelectorAll('img').forEach(i=>i.loading='eager')}})()")
            pg.wait_for_timeout(900)
            bn = pg.evaluate("""(()=>{const s=document.querySelector('.ar-banen');if(!s)return {er:false,n:0};
                const k=[...s.querySelectorAll('.ar-baan')],inb=document.querySelector('.ar-inb'),na=document.querySelector('.ar-zv, .ar-waarom, .b4b');
                return {er:true,n:k.length,kop:s.querySelector('h2').innerText,
                  kaarten:k.map(x=>{const i=x.querySelector('.ar-baan-foto img'),l=x.querySelector('a.ar-baan-link'),r=x.getBoundingClientRect();
                    return {naam:(x.querySelector('h3')||{}).innerText||'',plek:(x.querySelector('.ar-baan-plek')||{}).innerText||'',
                      href:l?l.getAttribute('href'):'',blank:!!l&&l.target==='_blank'&&/noopener/.test(l.rel),
                      foto:!!i&&i.complete&&i.naturalWidth>0&&!!i.alt,top:Math.round(r.top),w:Math.round(r.width),l:Math.round(r.left),rechts:Math.round(r.right)}}),
                  volgorde:!!inb&&!!(inb.compareDocumentPosition(s)&Node.DOCUMENT_POSITION_FOLLOWING)&&(!na||!!(s.compareDocumentPosition(na)&Node.DOCUMENT_POSITION_FOLLOWING)),
                  ov:document.documentElement.scrollWidth-innerWidth}})()""")
            if BANEN_N:
                kk = bn.get('kaarten', [])
                check(f'{tag} golfbanen: blok met kop en {BANEN_N} baankaarten, elk met naam, plaats/rijtijd, link (nieuw tabblad) en foto',
                      bn['er'] and 'golfbaan' in bn['kop'] and bn['n'] == BANEN_N and all(x['naam'] and 'minuten' in x['plek'] and x['href'].startswith('https://') and x['blank'] and x['foto'] for x in kk), str(bn)[:400])
                check(f'{tag} golfbanen: na Dit is inbegrepen, voor het zondagblok', bn['volgorde'], str(bn['volgorde']))
                if mob:
                    check(f'{tag} golfbanen: veegrij, eerste kaart in beeld, geen horizontale overloop van de pagina',
                          kk and kk[0]['l'] >= 0 and kk[0]['rechts'] <= w and bn['ov'] <= 0, str(kk)[:200])
                else:
                    check(f'{tag} golfbanen: kaarten naast elkaar, even breed', len(kk) >= 2 and len({x['top'] for x in kk}) == 1 and abs(kk[0]['w'] - kk[1]['w']) <= 1, str(kk)[:200])
            else:
                check(f'{tag} geen golfbanenblok (geen _banen in de JSON)', not bn['er'] and not pg.locator('.ar-baan').count(), str(bn)[:120])
            if shotdir and bn['er']:
                pg.locator('.ar-banen').screenshot(path=f'{shotdir}/{NAAM}-{w}-golfbanen.png')
            check(f'{tag} Waarom Asteria: kop, zes punten, foto geladen, knop met {VOUCHER}',
                  a['wKop'].startswith('Voor de grote dagen') and a['wPunten'] == 6 and a['wFoto'] and a['wKnop'] == VOUCHER, str(a)[:300])
            check(f'{tag} zijkaart met foto en prijs', a['kantFoto'] == 1 and a['kantPrijs'], str(a)[:200])
            check(f'{tag} ook interessant (o2): 3 kaarten als link', len(a['andere']) == 3 and all(h.startswith('https://') for h in a['andere']), str(a['andere']))
            check(f'{tag} ook interessant: foto over de volle kaart, naam en pijlknop erop', a['anVol'])
            check(f'{tag} ook interessant: ivoren achtergrond (surface)', a['anToon'] == 'surface' and a['anBg'] == 'rgb(255, 250, 241)', f"{a['anToon']} / {a['anBg']}")
            if mob:
                check(f'{tag} geen horizontale overloop', a['anOv'] <= 0, str(a['anOv']))
            check(f'{tag} drie chips onder de hero', a['chips'] == 3, str(a['chips']))
            check(f'{tag} FAQ: 4 tot 8 vragen', 4 <= len(a['faq']) <= 8, f"{len(a['faq'])}: " + ' | '.join(a['faq']))
            ok_rev = pg.evaluate("(()=>{const m=document.querySelector('.b5a-muur');return m.classList.contains('is-loop')?[...m.querySelectorAll('.b5a-baan .b5a-kaart:not([aria-hidden])')].length:m.querySelectorAll('.b5a-kaart').length})()")
            check(f'{tag} reviewmuur: precies 8 of 12 kaarten', ok_rev in (8, 12), str(ok_rev))

            # kamerslider vanaf 3 kamers: brede kaarten met lus (zoals /bedankt)
            ks = pg.evaluate("""(()=>{const s=document.querySelector('.b4b-strook');if(!s)return null;const e=[...s.querySelectorAll('.b4b-kaart:not([data-kloon])')];
                return {n:e.length,klonen:s.querySelectorAll('[data-kloon]').length,w:Math.round(e[0].getBoundingClientRect().width),raster:!!document.querySelector('.ar-kamers')}})()""")
            if ks or not pg.evaluate("!!document.querySelector('.ar-kamers')"):
                check(f'{tag} kamerslider met lus vanaf 3 kamers (klonen voor en na, geen raster)', bool(ks) and ks['n'] >= 3 and ks['klonen'] == 2 * ks['n'] and not ks['raster'], str(ks))
            # inbegrepen: paneel vanaf de linker schermrand, fotoslider met bolletjes en pijlen
            ib = pg.evaluate("""(()=>{const q=s=>document.querySelector(s),r=s=>{const e=q(s);if(!e)return null;const b=e.getBoundingClientRect();return {l:Math.round(b.left),t:Math.round(b.top+scrollY),b:Math.round(b.bottom+scrollY),r:Math.round(b.right),w:Math.round(b.width),h:Math.round(b.height),d:getComputedStyle(e).display}};
                return {bg:r('.ar-inb-bg'),inhoud:r('.ar-inb-inhoud'),foto:r('.ar-inb-foto'),dias:document.querySelectorAll('.ar-fs-dia').length,
                  bollen:document.querySelectorAll('.ar-fs-bol').length,pijlen:document.querySelectorAll('.ar-fs-pijl').length,
                  vink:document.querySelectorAll('.ar-inb-punt').length,prijs:(q('.ar-inb-prijs')||{}).innerText||'',
                  knop:(q('.ar-inb-acties .mews-open')||{dataset:{}}).dataset.voucher,link:(q('.ar-inb-link')||{getAttribute:()=>''}).getAttribute('href'),
                  tijden:document.querySelectorAll('.ar-inb-inhoud .ar-tijden li').length,tijdenLos:document.querySelectorAll('.ar-tijden').length}})()""")
            check(f'{tag} inbegrepen: tijdenregel in het paneel, geen losse strook eronder', ib['tijden'] >= 1 and ib['tijdenLos'] == 1, f"{ib['tijden']} / {ib['tijdenLos']}")
            check(f'{tag} inbegrepen: fotoslider met 4-6 dia\'s, evenveel bolletjes, twee pijlen', 4 <= ib['dias'] <= 6 and ib['bollen'] == ib['dias'] and ib['pijlen'] == 2, str(ib)[:300])
            check(f'{tag} inbegrepen: vinkjes, vanaf-prijs, knop met {VOUCHER}, tekstlink alle arrangementen',
                  ib['vink'] >= 4 and PRIJS in ib['prijs'].replace('\u00a0', ' ') and ib['knop'] == VOUCHER and ib['link'] == 'https://www.asteria.nl/arrangementen', str(ib)[:300])
            if mob:
                check(f'{tag} inbegrepen: eerst het paneel, daaronder de fotoslider (290 hoog)', ib['bg']['d'] == 'none' and ib['inhoud']['b'] <= ib['foto']['t'] + 1 and ib['foto']['h'] == 290, str(ib)[:300])
            else:
                check(f'{tag} inbegrepen: paneel loopt links tot de schermrand, foto rechts 47 px hoger',
                      ib['bg']['l'] <= 0 and ib['foto']['r'] > ib['bg']['r'] and ib['bg']['t'] - ib['foto']['t'] == 47 and ib['bg']['b'] - ib['foto']['b'] >= 47, str(ib)[:300])
                check(f'{tag} inbegrepen: paneel loopt 61 px onder de foto door (zd-alles), inhoud 56 px van boven- en onderrand',
                      ib['bg']['r'] - ib['foto']['l'] == 61 and ib['inhoud']['t'] == ib['bg']['t'] and ib['inhoud']['b'] == ib['bg']['b'], str(ib)[:300])
            pg.locator('.ar-fs').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
            pg.locator('.ar-fs-pijl[data-fs-stap="1"]').click(); pg.wait_for_timeout(900)
            fs = pg.evaluate("(()=>{const s=document.querySelector('.ar-fs-spoor');return {i:Math.round(s.scrollLeft/s.clientWidth),bol:[...document.querySelectorAll('.ar-fs-bol')].findIndex(b=>b.classList.contains('is-aan'))}})()")
            pg.locator('.ar-fs-pijl[data-fs-stap="-1"]').click(); pg.wait_for_timeout(900)
            pg.locator('.ar-fs-pijl[data-fs-stap="-1"]').click(); pg.wait_for_timeout(900)
            fs2 = pg.evaluate("(()=>{const s=document.querySelector('.ar-fs-spoor');return Math.round(s.scrollLeft/s.clientWidth)})()")
            check(f'{tag} inbegrepen: pijl schuift een dia (bolletje volgt), terug vanaf de eerste naar de laatste', fs == {'i': 1, 'bol': 1} and fs2 == ib['dias'] - 1, f'{fs} / {fs2}')
            pg.locator('.ar-fs-pijl[data-fs-stap="1"]').click(); pg.wait_for_timeout(900)
            if shotdir:
                pg.evaluate("window.scrollTo(0, document.querySelector('.ar-inb').getBoundingClientRect().top + scrollY - (innerWidth < 720 ? 40 : 110))"); pg.wait_for_timeout(700)
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-inbegrepen.png')
            # waarom: wiel met klonen, pijl verandert --active en de foto
            pg.evaluate("window.scrollTo(0, document.querySelector('.ar-waarom').getBoundingClientRect().top + scrollY - 80)"); pg.wait_for_timeout(600)
            wl = lambda: pg.evaluate("(()=>{const s=document.querySelector('.ar-wiel-spoor');return {echt:s.querySelectorAll('.ar-wiel-item:not([data-kloon])').length,klonen:s.querySelectorAll('[data-kloon]').length,"
                                     "active:+s.style.getPropertyValue('--active'),foto:document.querySelector('.ar-wiel-laag.is-actief').getAttribute('src'),wiel:document.querySelector('.ar-wiel-wrap').classList.contains('is-wiel')}})()")
            w0 = wl()
            check(f'{tag} wiel: 6 echte punten plus 8 klonen, draait', w0['echt'] == 6 and w0['klonen'] == 8 and w0['wiel'], str(w0))
            if shotdir: pg.locator('.ar-waarom').screenshot(path=f'{shotdir}/{NAAM}-{w}-wiel-1.png')
            pg.locator('.ar-wiel-knop[data-wiel-stap="1"]').click(); a1 = wl()['active']
            pg.wait_for_timeout(1500); w1 = wl()
            check(f'{tag} wiel: pijl omlaag verandert --active en de foto', a1 == w0['active'] + 1 and w1['foto'] != w0['foto'], f'{w0} -> {a1}, {w1}')
            pg.locator('.ar-wiel-knop[data-wiel-stap="-1"]').click(); a2 = wl()['active']
            check(f'{tag} wiel: pijl omhoog stapt terug', a2 == w1['active'] - 1, f'{w1["active"]} -> {a2}')
            pg.locator('.ar-wiel-knop[data-wiel-stap="1"]').click(); pg.wait_for_timeout(1500)
            if shotdir: pg.locator('.ar-waarom').screenshot(path=f'{shotdir}/{NAAM}-{w}-wiel-2.png')

        # Bekijk kamer -> pop-up
        kk = pg.evaluate("""(()=>{const ks=[...document.querySelectorAll('.b4b-kaart:not([data-kloon]) [data-kamer]')].map(b=>b.dataset.kamer);
            return ks.includes('royale')?'royale':ks[0]})()""")
        kd = pg.evaluate(f"JSON.parse(document.getElementById('lp-kamerdata').textContent)['{kk}']")
        knop = pg.locator(f'.b4b-kaart:not([data-kloon]) [data-kamer="{kk}"]')
        knop.scroll_into_view_if_needed(); knop.click(force=True); pg.wait_for_timeout(500)
        titel = pg.locator('#lp-pop-kamer-naam').inner_text()
        room = pg.locator('#lp-pop-kamer .lp-pop__boek').get_attribute('data-room')
        check(f'{tag} Bekijk kamer opent pop-up met juiste kamer en data-room',
              pg.evaluate("document.getElementById('lp-pop-kamer').open") and titel == kd['naam']
              and room == kd['kamer'], f'{titel} / {room}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

        # Boek nu op een kamerkaart: showRates(kamer) kiest alleen de kamer, de widget gaat pas open met open()
        # (live fout 14 okt 2026: zonder open() gebeurde er niets). Gestubde widget-API, geen netwerk.
        pg.evaluate("""()=>{window._mews=[];window.mewsApi={setVoucherCode:v=>window._mews.push('v:'+v),setLanguageCode:()=>{},
            showRates:r=>window._mews.push('rates:'+r),open:()=>window._mews.push('open')}}""")
        bk = pg.locator(f'.b4b-kaart:not([data-kloon]) .mews-open[data-room="{kd["kamer"]}"]').first
        bk.scroll_into_view_if_needed(); bk.click(force=True); pg.wait_for_timeout(300)
        r = pg.evaluate('window._mews.slice()')
        check(f'{tag} Boek nu op een kamerkaart roept showRates(kamer) en open() aan, met voucher {VOUCHER}',
              r == vc() + ['rates:' + kd['kamer'], 'open'], str(r))
        pg.evaluate("delete window.mewsApi")

        if PRIJS:
            check(f'{tag} geen tegelstrook (b2a) op de arrangementpagina', pg.evaluate("!document.querySelector('.b2a, .b2a-strook')"))
        else:
            # tegelstrook: Wellness- en Restaurant-knop -> faciliteiten-pop-up
            FACVIDEO = {}
            POPS = [('wellness', 'Wellness op de Top Floor', 'https://www.asteria.nl/wellness'),
                    ('restaurant', 'Restaurant en terras', 'https://www.asteria.nl/restaurant')]
            if HOTEL:   # extra pop-ups uit '_facdata' (fitness, fietsen, parkeren)
                fd = pg.evaluate("JSON.parse(document.getElementById('lp-facdata').textContent)")
                POPS += [(k, v['titel'], v['link']) for k, v in fd.items() if k not in ('wellness', 'restaurant') and not k.startswith('omg-')]
                FACVIDEO = {k: v['video'] for k, v in fd.items() if v.get('video')}
            for key, titel_v, link_v in POPS:
                fk = pg.locator(f'{FAC} [data-fac="{key}"]').first
                tegel = pg.locator(f'{FAC} {FAC_TEGEL}:has([data-fac="{key}"])').first
                tegel.scroll_into_view_if_needed()
                if not mob: tegel.hover()
                pg.wait_for_timeout(700)
                fk.click(); pg.wait_for_timeout(1200)
                f = pg.evaluate("""()=>{const d=document.getElementById('lp-pop-fac'),r=d.getBoundingClientRect(),bi=d.querySelector('.lp-pop__binnen');
                    const imgs=[...d.querySelectorAll('.lp-pop__hero:not([hidden]),.lp-pop__fotos img')],v=d.querySelector('.lp-pop__video:not([hidden])');
                    return {open:d.open,info:(d.querySelector('.lp-pop__info:not([hidden])')||{getAttribute:()=>null}).getAttribute('href'),titel:d.querySelector('.lp-pop__titel').textContent,link:d.querySelector('.lp-pop__meer').getAttribute('href'),knop:d.querySelector('.lp-pop__meer').textContent.trim(),boek:d.querySelector('.lp-pop__meer').classList.contains('mews-open'),
                      fotos:imgs.length+(v?1:0),geladen:imgs.filter(i=>i.complete&&i.naturalWidth>0).length+(v&&v.poster?1:0),video:v?{src:v.currentSrc.split('/').pop(),t:v.currentTime,paused:v.paused,muted:v.muted,poster:v.poster.split('/').pop()}:null,chips:d.querySelectorAll('.lp-pop__chips li').length,
                      t:Math.round(r.top),b:Math.round(r.bottom),l:Math.round(r.left),r:Math.round(r.right),
                      scroll:bi.scrollHeight-bi.clientHeight,sw:document.documentElement.scrollWidth}}""")
                check(f'{tag} {key}-knop opent pop-up met juiste titel, link en geladen foto\'s',
                      f['open'] and f['titel'] == titel_v and (f['link'] == link_v if not GESLOTEN else (f['link'].startswith('https://app.mews.com/distributor/6dc9094c') and f['boek'] and f['knop'] == 'Bekijk beschikbaarheid')) and f['fotos'] == 4 and f['geladen'] == 4 and f['chips'] == 4, str(f))
                if SPIEGEL:
                    check(f'{tag} {key}-pop-up: tekstlink Meer informatie naar de spiegel naast Bekijk beschikbaarheid',
                          f['info'] in ('/wellness', '/restaurant', '/faciliteiten'), str(f['info']))
                vid = FACVIDEO.get(key)
                if vid:
                    pg.wait_for_timeout(1200)
                    vv = pg.evaluate("(()=>{const v=document.querySelector('#lp-pop-fac .lp-pop__video:not([hidden])');return v?{src:v.currentSrc.split('/').pop(),t:v.currentTime,paused:v.paused,muted:v.muted,poster:!!v.poster}:null})()")
                    check(f'{tag} {key}-pop-up: video speelt (gedempt) als eerste beeld, poster = eerste foto', bool(vv) and vv['src'] == vid.split('/')[-1]
                          and vv['t'] > 0.2 and not vv['paused'] and vv['muted'] and vv['poster'], str(vv))
                    if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-fac-{key}-video-{w}.png')
                check(f'{tag} {key}-pop-up past in beeld' + (', zonder scrollen' if not mob else ''),
                      f['t'] >= 0 and f['l'] >= 0 and f['r'] <= w and f['b'] <= h and f['sw'] <= w and (mob or f['scroll'] <= 1), str(f))
                if shotdir:
                    pg.screenshot(path=f'{shotdir}/{NAAM}-fac-{key}-{w}.png')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
                dicht = pg.evaluate("""([k,f])=>({open:document.getElementById('lp-pop-fac').open,focus:document.activeElement===document.querySelector(f+' [data-fac="'+k+'"]')})""", [key, FAC])
                check(f'{tag} Escape sluit de {key}-pop-up, focus terug op de knop', not dicht['open'] and dicht['focus'], str(dicht))
            # sluiten via kruisje en via de achtergrond
            def open_wellness():
                tegel = pg.locator(f'{FAC} {FAC_TEGEL}:has([data-fac="wellness"])').first
                tegel.scroll_into_view_if_needed()
                if not mob: tegel.hover()
                pg.wait_for_timeout(700)
                pg.locator(f'{FAC} [data-fac="wellness"]').first.click(); pg.wait_for_timeout(500)
            open_wellness()
            pg.locator('#lp-pop-fac .lp-pop__sluit').click(); pg.wait_for_timeout(400)
            x1 = pg.evaluate("document.getElementById('lp-pop-fac').open")
            open_wellness()
            pg.mouse.click(3, 3); pg.wait_for_timeout(400)
            x2 = pg.evaluate("document.getElementById('lp-pop-fac').open")
            check(f'{tag} kruisje en klik op de achtergrond sluiten de pop-up', not x1 and not x2, f'{x1}/{x2}')

        if HOTEL and pg.evaluate("!!document.querySelector('.b1a-video')"):
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(2500)
            hv = pg.evaluate("""(()=>{const v=document.querySelector('.b1a-video'),f=document.querySelector('.b1a-foto'),r=v.getBoundingClientRect(),fr=f.getBoundingClientRect(),
                o=getComputedStyle(f,'::after');return {t:v.currentTime,paused:v.paused,muted:v.muted,loop:v.loop,err:v.error&&v.error.code,
                src:v.currentSrc.split('/').pop(),poster:v.getAttribute('poster'),dekt:Math.abs(r.width-fr.width)<2&&Math.abs(r.height-fr.height)<2,
                overlay:o.backgroundImage.includes('gradient'),tekstBoven:+getComputedStyle(document.querySelector('.b1a-tekst')).zIndex>=2}})()""")
            bron = 'hero-asteria-building-sunset.mp4'   # ook op de telefoon de liggende video, uitsnede 50% 50% zoals de staging
            check(f'{tag} herovideo speelt af (gedempt, lus), bron {bron}, dekt de hero, overlay + tekst erboven',
                  hv['t'] > 0.5 and not hv['paused'] and hv['muted'] and hv['loop'] and not hv['err'] and hv['src'] == bron and hv['dekt'] and hv['overlay'] and hv['tekstBoven'], str(hv))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-hero-video.png')

        if HOTEL:
            hb = pg.evaluate("""(()=>{const q=s=>document.querySelector(s),y=s=>{const e=q(s);return e?e.getBoundingClientRect().top+scrollY:-1};
                const fac=q('.ho-fac'),omg=q('.ho-omg'),arr=q('.ho-arr');
                return {volg:['.b3a','.b4b','.ho-fac','.ho-omg','.ho-arr','.b5a','.b6c','.b7a'].map(y),
                  ster:!!q('#attentie .b3a-grid'),sterKop:q('#attentie h2').innerText,
                  tegels:fac.querySelectorAll('.ho-fac-tegel').length,kaart:!!fac.querySelector('.ho-fac-kaart h2'),extra:fac.querySelectorAll('.ho-fac-extra li').length,
                  facKnoppen:[...fac.querySelectorAll('[data-fac]')].map(b=>b.dataset.fac).join(','),
                  rijen:omg.querySelectorAll('.omgeving-list__item[data-fac][data-omg-photo]').length,omgKop:omg.querySelector('h2').innerText,
                  h1fs:parseFloat(getComputedStyle(q('.b1a h1')).fontSize),
                  kaarten:[...arr.querySelectorAll('a.ho-arr-kaart')].map(a=>!!a.querySelector('img')&&!!a.querySelector('.ho-arr-naam').innerText).filter(Boolean).length,
                  euro:[fac,omg,arr].some(e=>e.innerText.includes('\u20ac')),
                  arrVeeg:(r=>r.scrollWidth>r.clientWidth)(arr.querySelector('.ho-arr-rij')),
                  h1:q('.b1a h1').innerText,sub:(q('.b1a-sub')||{offsetHeight:0}).offsetHeight,badge:q('.b1a-rb .rb-reviews').innerText,code:!!q('#bb-code'),pil:[...document.querySelectorAll('.b4b-pil')].some(p=>p.offsetParent)}})()""")
            v = hb['volg']
            check(f'{tag} blokvolgorde ster-split > kamers > faciliteiten > omgeving > arrangementen > reviews > FAQ > slot', all(x >= 0 for x in v) and v == sorted(v), str(v))
            check(f'{tag} hero: kop Even weg, helemaal hier (zonder introalinea), badge 2.200+ reviews, geen actiecodeveld', ' '.join(hb['h1'].split()) == 'Even weg, helemaal hier' and hb['sub'] == 0 and '2.200+' in hb['badge'] and not hb['code'], f"{hb['h1']} / {hb['badge']}")
            check(f'{tag} ster-split "Een verblijf dat bij je past"', hb['ster'] and 'verblijf dat bij je' in hb['sterKop'].replace('\n', ' '), hb['sterKop'])
            check(f'{tag} faciliteiten: tekstkaart, 5 tegels, extra punten, elke tegel opent een pop-up',
                  hb['kaart'] and hb['tegels'] == 5 and hb['extra'] >= 1 and hb['facKnoppen'] == 'wellness,restaurant,fitness,parkeren,fietsen', str(hb))
            if mob:
                mz = pg.evaluate("""(()=>[...document.querySelectorAll('.ho-fac-tegel')].map(x=>{const r=x.getBoundingClientRect(),
                    a=getComputedStyle(x.querySelector('.ho-fac-tekst'),'::after');return {n:x.querySelector('h3').innerText.trim(),l:Math.round(r.left),
                    t:Math.round(r.top+scrollY),w:Math.round(r.width),h:Math.round(r.height),
                    pijl:a.content!=='none'&&a.backgroundColor!=='rgba(0, 0, 0, 0)',p:getComputedStyle(x.querySelector('p')).display}}))()""")
                # volgorde-onafhankelijk: één brede tegel (onderaan), de andere vier in twee kolommen: links hoog boven laag, rechts laag boven hoog
                smal = min(x['w'] for x in mz)
                breed = [x for x in mz if x['w'] > smal * 1.8]
                rest = [x for x in mz if x not in breed]
                links = sorted([x for x in rest if x['l'] == min(y['l'] for y in rest)], key=lambda x: x['t'])
                rechts = sorted([x for x in rest if x['l'] != min(y['l'] for y in rest)], key=lambda x: x['t'])
                ok = (len(breed) == 1 and len(links) == 2 and len(rechts) == 2
                      and links[0]['h'] > links[1]['h'] and rechts[0]['h'] < rechts[1]['h']
                      and breed[0]['t'] > max(x['t'] + x['h'] for x in rest) - 1
                      and all(x['pijl'] and x['p'] == 'none' for x in mz))
                check(f'{tag} faciliteiten als staging-mozaiek: links hoog+laag, rechts laag+hoog, brede tegel onder, pijl, geen omschrijving', ok, str(mz))
                check(f'{tag} brede tegel onderaan is Restaurant en brasserie', len(breed) == 1 and breed[0]['n'] == 'Restaurant en brasserie', str([x['n'] for x in breed]))
            check(f'{tag} omgeving: 3-6 plekken (knop met pop-up en foto), kop "Even weg, alles vlakbij"', 3 <= hb['rijen'] <= 6 and 'alles vlakbij' in hb['omgKop'], str(hb['rijen']))
            # herokop: bureaublad zoals de staging-homepage (--text-hero = clamp(72px, 9vw, 130px)), telefoon 44 px
            h1_doel = 44 if w < 720 else (min(130, max(72, 0.09 * w)) if w >= 1024 else 72)
            check(f'{tag} herokop {h1_doel:.1f} px (staging-homepage)', abs(hb['h1fs'] - h1_doel) < 0.6, str(hb['h1fs']))
            # omgevingsblok: plek kiezen wisselt de foto en het bijschrift; Bekijk opent de pop-up met Route plannen en fotoregel
            omg_items = pg.evaluate("[...document.querySelectorAll('[data-omg-list] .omgeving-list__item')].map(b=>({fac:b.dataset.fac,foto:b.dataset.omgPhoto,cat:b.dataset.omgCat,naam:b.querySelector('.oli-name').innerText.trim(),afstand:b.querySelector('.oli-distance').innerText.trim(),meer:b.querySelector('.oli-more').innerText.trim()}))")
            check(f'{tag} omgeving: elke plek heeft naam, afstand en Bekijk', all(x['naam'] and x['afstand'] and x['meer'] == 'Bekijk' for x in omg_items), str(omg_items)[:300])
            fd_omg = pg.evaluate("JSON.parse(document.getElementById('lp-facdata').textContent)")
            JS_STAND = '''(()=>{const s=document.querySelector('[data-omg-list]'),a=s.querySelector('.omgeving-list__item.is-active'),f=s.querySelector('[data-omg-photo-target]'),
                c=s.querySelector('.omgeving-list__caption'),r=s.querySelector('.omgeving-list__photo').getBoundingClientRect();
                return {actief:a?a.dataset.fac:null,src:f.getAttribute('src'),naam:s.querySelector('[data-omg-caption-name]').textContent,cat:s.querySelector('.olc-kicker').textContent,
                  cap:+getComputedStyle(c).opacity,top:Math.round(r.top),streep:a?+getComputedStyle(a,'::before').opacity:0}})()'''
            if not mob:
                doel = omg_items[1]
                pg.locator('[data-omg-list] .omgeving-list__item').nth(1).scroll_into_view_if_needed()
                pg.locator('[data-omg-list] .omgeving-list__item').nth(1).hover(); pg.wait_for_timeout(700)
                st = pg.evaluate(JS_STAND)
                check(f'{tag} omgeving: hover op een plek kiest hem (streep), wisselt foto, label en naam op de foto', st['actief'] == doel['fac'] and st['src'] == doel['foto']
                      and st['naam'] == doel['naam'] and st['cat'] == doel['cat'] and st['cap'] > .9 and st['streep'] > .9, str(st))
                pg.mouse.move(5, 5); pg.wait_for_timeout(700)
                st = pg.evaluate(JS_STAND)
                check(f'{tag} omgeving: muis eruit = terug naar de eerste plek, bijschrift weg', st['actief'] is None and st['src'] == omg_items[0]['foto'] and st['cap'] < .1, str(st))
            else:
                pg.evaluate("(()=>{const li=document.querySelectorAll('[data-omg-list] .omgeving-list__items li')[2];window.scrollTo(0,li.getBoundingClientRect().top+scrollY-420)})()")
                pg.wait_for_timeout(900)
                st = pg.evaluate(JS_STAND)
                kop_h = pg.evaluate("document.querySelector('.top-stack').getBoundingClientRect().bottom")
                gekozen = next((x for x in omg_items if x['fac'] == st['actief']), None)
                check(f'{tag} omgeving: foto plakt onder de kop, de plek onder de foto wordt actief en bepaalt foto en naam', gekozen is not None and st['src'] == gekozen['foto']
                      and st['naam'] == gekozen['naam'] and st['cap'] > .9 and abs(st['top'] - (kop_h + 14)) <= 2 and omg_items.index(gekozen) >= 1, f'{st} kop={kop_h}')
            JS_POP = '''()=>{const d=document.getElementById('lp-pop-fac'),r=d.getBoundingClientRect(),bi=d.querySelector('.lp-pop__binnen'),ro=d.querySelector('.lp-pop__route'),cr=d.querySelector('.lp-pop__credit');
                    const imgs=[...d.querySelectorAll('.lp-pop__hero:not([hidden]),.lp-pop__fotos img')];
                    return {open:d.open,titel:d.querySelector('.lp-pop__titel').textContent,knop:d.querySelector('.lp-pop__meer').textContent.trim(),boek:d.querySelector('.lp-pop__meer').classList.contains('mews-open'),
                      mews:d.querySelector('.lp-pop__meer').getAttribute('href'),fotos:imgs.length,geladen:imgs.filter(i=>i.complete&&i.naturalWidth>0).length,alt:imgs.every(i=>i.alt&&!i.alt.includes('foto ')),
                      chips:[...d.querySelectorAll('.lp-pop__chips li')].map(c=>c.textContent),
                      route:ro&&!ro.hidden?{href:ro.href,doel:ro.target,rel:ro.rel,tekst:ro.textContent}:null,credit:cr&&!cr.hidden?cr.textContent:null,
                      t:Math.round(r.top),b:Math.round(r.bottom),l:Math.round(r.left),r:Math.round(r.right),scroll:bi.scrollHeight-bi.clientHeight,sw:document.documentElement.scrollWidth}}'''
            for i, x in enumerate(omg_items):
                v = fd_omg[x['fac']]
                pg.evaluate("i=>document.querySelectorAll('[data-omg-list] .omgeving-list__item')[i].scrollIntoView({block:'center'})", i); pg.wait_for_timeout(300)
                pg.locator('[data-omg-list] .omgeving-list__item').nth(i).click(); pg.wait_for_timeout(1000)
                f = pg.evaluate(JS_POP)
                ok_route = (f['route'] == {'href': v['route'], 'doel': '_blank', 'rel': 'noopener', 'tekst': 'Route plannen'}) if v.get('route') else f['route'] is None
                check(f'{tag} omgeving {x["fac"]}: pop-up met titel, {len(v["fotos"])} geladen foto\'s met alt, afstand in de chips, Bekijk beschikbaarheid (Mews), Route plannen, fotoregel',
                      f['open'] and f['titel'] == v['titel'] and f['boek'] and f['knop'] == 'Bekijk beschikbaarheid' and f['mews'].startswith('https://app.mews.com/distributor/6dc9094c')
                      and 3 <= f['fotos'] == f['geladen'] == len(v['fotos']) <= 4 and f['alt'] and (x['afstand'] in f['chips'] or x['fac'] == 'omg-fietsen')
                      and ok_route and f['credit'] == v.get('credit'), str(f)[:400])
                check(f'{tag} omgeving {x["fac"]}-pop-up past in beeld' + (', zonder scrollen' if not mob else ''),
                      f['t'] >= 0 and f['l'] >= 0 and f['r'] <= w and f['b'] <= h and f['sw'] <= w and (mob or f['scroll'] <= 1), str(f)[-160:])
                if shotdir and i == 1:
                    pg.screenshot(path=f'{shotdir}/{NAAM}-omg-{x["fac"]}-{w}.png')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
                dicht = pg.evaluate("i=>({open:document.getElementById('lp-pop-fac').open,focus:document.activeElement===document.querySelectorAll('[data-omg-list] .omgeving-list__item')[i]})", i)
                check(f'{tag} Escape sluit de {x["fac"]}-pop-up, focus terug op de plek', not dicht['open'] and dicht['focus'], str(dicht))
            # de faciliteit-pop-up daarna weer zonder route en fotoregel
            pg.evaluate("document.querySelector('.ho-fac [data-fac=\"fietsen\"]').click()"); pg.wait_for_timeout(500)
            schoon = pg.evaluate("(()=>{const d=document.getElementById('lp-pop-fac'),ro=d.querySelector('.lp-pop__route'),cr=d.querySelector('.lp-pop__credit');return {route:!!ro&&!ro.hidden,credit:!!cr&&!cr.hidden}})()")
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            check(f'{tag} faciliteit-pop-up na een omgeving-pop-up: geen Route plannen en geen fotoregel', not schoon['route'] and not schoon['credit'], str(schoon))
            check(f'{tag} arrangementen: kaarten met foto en naam, veegrij', hb['kaarten'] >= 3 and hb['arrVeeg'], str(hb['kaarten']))
            check(f'{tag} geen prijzen in faciliteiten, omgeving en arrangementen; geen pil op de kamerkaarten', not hb['euro'] and not hb['pil'])
            if shotdir:
                for sel, naam in (('.b3a', 'sterplit'), ('.ho-fac', 'faciliteiten'), ('.ho-omg', 'omgeving'), ('.ho-arr', 'arrangementen')):
                    pg.evaluate(f"(()=>{{const s=document.querySelector('{sel}');s.querySelectorAll('img').forEach(i=>i.loading='eager');window.scrollTo(0,s.getBoundingClientRect().top+scrollY-document.querySelector('.top-stack').offsetHeight)}})()")
                    pg.wait_for_timeout(900)
                    pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-{naam}.png')
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)

        # reviewmuur
        kol = pg.evaluate("document.querySelectorAll('.b5a-muur.is-loop .b5a-kol').length")
        verwacht = 4 if w == 1440 else 1
        check(f'{tag} reviewmuur bouwt {verwacht} kolommen', kol == verwacht, f'{kol}')
        if not mob:
            pg.locator('.b5a-muur').scroll_into_view_if_needed(); pg.locator('.b5a-muur').hover(); pg.wait_for_timeout(300)
            st = pg.evaluate("getComputedStyle(document.querySelector('.b5a-baan')).animationPlayState")
            check(f'{tag} reviewmuur pauzeert bij hover', st == 'paused', st)
            pg.mouse.move(5, 5)

        # onderbalk (alleen telefoon zichtbaar)
        if mob:
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(700)
            vooraf = pg.evaluate("document.querySelector('.mob-cta').classList.contains('is-zichtbaar')")
            pg.evaluate("window.scrollTo(0, document.querySelector(window.__ankerSec).offsetTop + 400)"); pg.wait_for_timeout(700)
            na = pg.evaluate("document.querySelector('.mob-cta').classList.contains('is-zichtbaar')")
            check(f'{tag} onderbalk verschijnt na de hero', (not vooraf) and na, f'voor {vooraf}, na {na}')
            pg.wait_for_timeout(400)
            echt = pg.evaluate("""(()=>{const m=document.querySelector('.mob-cta'),r=m.getBoundingClientRect(),c=getComputedStyle(m);return c.display!=='none'&&c.visibility==='visible'&&r.height>40&&r.bottom<=innerHeight+1&&r.top<innerHeight})()""")
            check(f'{tag} onderbalk echt zichtbaar onderin beeld', echt)
            if PRIJS:
                ob = pg.locator('.mob-cta').inner_text().replace('\u00a0', ' ')
                check(f'{tag} prijs {PRIJS} in de onderbalk', PRIJS in ob, ob.replace('\n', ' | '))
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)

        if V3:
            geen = pg.evaluate("!document.querySelector('.b1k-uitklap, .b1k-tab, .b1k-paneel')")
            check(f'{tag} geen uitklaptab in de pagina', geen)
            if mob:
                zk = pg.evaluate("document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect().width")
                check(f'{tag} geen zijkaart op de telefoon', zk == 0, str(zk))
            else:
                kaart = """()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect(),kop=document.querySelector('.top-stack').getBoundingClientRect().bottom,
                    s=document.querySelector(window.__anker).getBoundingClientRect(),m=document.querySelector('.b5a').getBoundingClientRect();
                    return {l:Math.round(k.left),r:Math.round(k.right),t:Math.round(k.top),b:Math.round(k.bottom),kop:Math.round(kop),sr:Math.round(s.right),st:Math.round(s.top),sb:Math.round(s.bottom),m5:Math.round(m.top)}}"""
                pg.evaluate("window.scrollTo(0, document.querySelector(window.__anker).getBoundingClientRect().top + scrollY - document.querySelector('.top-stack').offsetHeight - 24)"); pg.wait_for_timeout(700)
                z = pg.evaluate(kaart)
                check(f'{tag} kaart zichtbaar naast de tegels', z['l'] > z['sr'] and z['r'] <= w and abs(z['t'] - z['st']) <= 4 and z['b'] <= h, str(z))
                if PRIJS:
                    pz = pg.evaluate("""(()=>{const e=document.querySelector('.lp-zone-kant .b1k-prijs'),r=e&&e.getBoundingClientRect();
                        return e?{t:e.innerText.replace(/\\u00a0/g,' '),zicht:r.height>0&&r.top>=0&&r.bottom<=innerHeight}:null})()""")
                    check(f'{tag} prijs {PRIJS} zichtbaar in de zijkaart', bool(pz) and PRIJS in pz['t'] and pz['zicht'], str(pz))
                if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-tegels.png')
                if PRIJS:
                    for sel, naam in (('.ar-zv', 'zondag'), ('.ar-waarom', 'waarom')):
                        if not pg.evaluate(f"!!document.querySelector('{sel}')"): continue
                        pg.evaluate(f"window.scrollTo(0, document.querySelector('{sel}').getBoundingClientRect().top + scrollY - 140)"); pg.wait_for_timeout(700)
                        z = pg.evaluate(kaart)
                        check(f'{tag} zijkaart loopt mee bij {naam}', z['t'] <= z['kop'] + 40 and z['b'] > z['kop'] + 300, str(z))
                        if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-{naam}.png')
                pg.evaluate("(()=>{const s=document.querySelector('.b4b-strook, .ar-kamers');window.scrollTo(0, s.getBoundingClientRect().top + scrollY + s.offsetHeight/2 - innerHeight/2)})()"); pg.wait_for_timeout(700)
                z = pg.evaluate(kaart)
                check(f'{tag} kaart in beeld midden kamerslider', z['b'] > z['kop'] + 200 and z['t'] <= z['kop'] + 40, str(z))
                eind = pg.evaluate("(()=>{const k=document.querySelector('.lp-zone .b4b-kaart:not([data-kloon])');window.scrollTo(0, k.getBoundingClientRect().bottom + scrollY - innerHeight + (window.__arr ? 500 : 150));const a=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect().bottom,b=k.getBoundingClientRect().bottom;return [Math.round(a),Math.round(b)]})()")
                check(f'{tag} kaart stopt gelijk met de kamerkaarten', abs(eind[0] - eind[1]) <= 3, str(eind))
                if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kamerslider.png')
                pg.evaluate("window.scrollTo(0, document.querySelector('.b5a').getBoundingClientRect().top + scrollY - document.querySelector('.top-stack').offsetHeight)"); pg.wait_for_timeout(700)
                z = pg.evaluate(kaart)
                check(f'{tag} kaart weg bij de reviewmuur, geen overlap', z['b'] <= z['m5'] and z['b'] <= z['kop'] + 1, str(z))
                if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-reviewmuur.png')
                pg.evaluate("window.scrollTo(0, document.querySelector('.b3a').getBoundingClientRect().top + scrollY - 150)"); pg.wait_for_timeout(700)
                pg.evaluate("""()=>{window._mews=[];window.mewsApi={setVoucherCode:v=>window._mews.push('v:'+v),setLanguageCode:()=>{},open:()=>window._mews.push('open')}}""")
                pg.locator('.lp-zone-kant .b1k-knop').click(); pg.wait_for_timeout(300)
                r = pg.evaluate('window._mews.slice()')
                check(f'{tag} knop in de kaart opent Mews met voucher {VOUCHER}', r == vc() + ['open'], str(r))
                pg.evaluate("delete window.mewsApi")
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)

        # uitklaptab (alleen >= 720): verborgen bovenaan, zichtbaar na de hero, weg bij slotblok 7a
        tabst = lambda: pg.evaluate("""()=>{const u=document.querySelector('.b1k-uitklap'),t=u.querySelector('.b1k-tab'),r=t.getBoundingClientRect(),cs=getComputedStyle(t);
            return {zicht:cs.display!=='none'&&cs.visibility==='visible'&&r.width>0&&r.left<innerWidth,aria:u.getAttribute('aria-hidden'),tab:t.getAttribute('tabindex')}}""")
        if not V3 and not HOTEL:
          pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(600)
          t0 = tabst()
          pg.evaluate("window.scrollTo(0, document.querySelector('.b4b').offsetTop)"); pg.wait_for_timeout(900)
          t1 = tabst()
        if SPIEGEL and mob:
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
            pg.locator('.nav-hamburger').click(); pg.wait_for_timeout(500)
            d1 = pg.evaluate("document.getElementById('nav-drawer').classList.contains('is-open')")
            pg.locator('#nav-drawer .drawer-parent').first.click(); pg.wait_for_timeout(400)
            d2 = pg.evaluate("(()=>{const li=document.querySelector('#nav-drawer .has-sub');return li.classList.contains('is-open')&&li.querySelector('.drawer-sub').getBoundingClientRect().height>100})()")
            pg.locator('#nav-drawer .nav-drawer__close').click(); pg.wait_for_timeout(500)
            d3 = not pg.evaluate("document.getElementById('nav-drawer').classList.contains('is-open')")
            check(f'{tag} spiegel: hamburger opent de drawer, Hotel klapt uit, sluitknop sluit', d1 and d2 and d3, f'{d1} {d2} {d3}')
            if shotdir:
                pg.locator('.nav-hamburger').click(); pg.wait_for_timeout(500)   # Hotel staat nog uitgeklapt
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-drawer.png')
                pg.locator('#nav-drawer .nav-drawer__close').click(); pg.wait_for_timeout(400)
        elif SPIEGEL:
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
            pg.locator('.nav-links .has-sub').first.hover(); pg.wait_for_timeout(500)
            m = pg.evaluate("(()=>{const s=document.querySelector('.nav-links .has-sub .nav-sub'),r=s.getBoundingClientRect();return {vis:getComputedStyle(s).visibility,items:s.querySelectorAll('a').length,r:Math.round(r.right),w:innerWidth}})()")
            check(f'{tag} spiegel: submenu Hotel opent bij hover (4 links, binnen beeld)', m['vis'] == 'visible' and m['items'] == 4 and m['r'] <= m['w'], str(m))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-submenu.png')
            pg.mouse.move(5, h - 5); pg.wait_for_timeout(300)
        if HOTEL:
            check(f'{tag} geen uitklaptab en geen zijkaart', pg.evaluate("!document.querySelector('.b1k-uitklap, .b1k-tab, .b1k-paneel, .lp-zone-kant')"))
        elif V3:
            pass
        elif mob:
            check(f'{tag} uitklaptab niet zichtbaar op de telefoon', not t0['zicht'] and not t1['zicht'], f"{t0} / {t1}")
        else:
            check(f'{tag} uitklaptab verborgen bovenaan (aria-hidden, tabindex -1)', not t0['zicht'] and t0['aria'] == 'true' and t0['tab'] == '-1', str(t0))
            check(f'{tag} uitklaptab zichtbaar na de hero', t1['zicht'] and t1['aria'] == 'false' and t1['tab'] == '0', str(t1))
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(700)
            k = pg.evaluate("""()=>{const r=document.querySelector('.b1k-paneel').getBoundingClientRect(),kop=document.querySelector('.top-stack').getBoundingClientRect().bottom;
                return {exp:document.querySelector('.b1k-tab').getAttribute('aria-expanded'),l:r.left,r:r.right,t:r.top,b:r.bottom,kop,vis:getComputedStyle(document.querySelector('.b1k-paneel')).visibility}}""")
            check(f'{tag} klik op de tab opent de kaart in beeld, onder de kop', k['exp'] == 'true' and k['vis'] == 'visible' and k['l'] >= 0
                  and k['r'] <= w and k['t'] >= k['kop'] and k['b'] <= h, str(k))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kaart-open.png')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
            ex = pg.evaluate("[document.querySelector('.b1k-tab').getAttribute('aria-expanded'),getComputedStyle(document.querySelector('.b1k-paneel')).visibility]")
            check(f'{tag} Escape klapt de kaart in', ex == ['false', 'hidden'], str(ex))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-tab-dicht.png')
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(600)
            pg.mouse.click(200, h - 100); pg.wait_for_timeout(600)
            ex2 = pg.evaluate("document.querySelector('.b1k-tab').getAttribute('aria-expanded')")
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(600)
            pg.locator('.b1k-sluit').click(); pg.wait_for_timeout(600)
            ex3 = pg.evaluate("document.querySelector('.b1k-tab').getAttribute('aria-expanded')")
            check(f'{tag} klik buiten de kaart en sluitknop klappen in', ex2 == 'false' and ex3 == 'false', f'{ex2}/{ex3}')
            # Mews-poort met voucher (gestubde widget-API, geen netwerk)
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(600)
            pg.evaluate("""()=>{window._mews=[];window.mewsApi={setVoucherCode:v=>window._mews.push('v:'+v),setLanguageCode:()=>{},open:()=>window._mews.push('open')}}""")
            pg.locator('.b1k-paneel .b1k-knop').click(); pg.wait_for_timeout(300)
            r = pg.evaluate('window._mews.slice()')
            check(f'{tag} knop in de kaart opent Mews met voucher {VOUCHER}', r == vc() + ['open'], str(r))
            pg.evaluate("delete window.mewsApi")
            pg.evaluate("document.querySelector('.b7a').scrollIntoView({block:'center'})"); pg.wait_for_timeout(900)
            t2 = tabst()
            pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(900)
            t3 = tabst()
            check(f'{tag} uitklaptab weg bij het slotblok en daarna', not t2['zicht'] and not t3['zicht'] and t2['aria'] == 'true', f"{t2} / {t3}")
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)

        if mob and HOTEL:
            # telefoon, algemene lander: de staging-boekkaart (hero 490, kop 44 px, kaart 24 px over de hero, 3 velden + knop)
            sb = pg.evaluate("""(()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top+scrollY),Math.round(b.width),Math.round(b.height)]};
                const k=document.querySelector('.b1a-mobkaart .hb-kaart'),f=document.querySelector('.b1a-foto'),h=document.querySelector('.b1a-tekst h1'),g=document.querySelector('.b1a-rb');
                const kr=k.getBoundingClientRect(),fr=f.getBoundingClientRect(),hr=h.getBoundingClientRect(),gr=g.getBoundingClientRect();
                return {oudeKaart:document.querySelectorAll('.b1a-mobkaart .b1k-kaart').length,balkWeg:getComputedStyle(document.querySelector('.b1a-balk')).display==='none',
                  hero:r(f),h1fs:getComputedStyle(h).fontSize,kaart:r(k),overlap:Math.round(fr.bottom-kr.top),kopVrij:Math.round(kr.top-hr.bottom),
                  badge:gr.bottom<=kr.top,rad:getComputedStyle(k).borderRadius,
                  labels:[...k.querySelectorAll('.hb-label')].map(x=>x.innerText.trim().toLowerCase()),waarden:[...k.querySelectorAll('.hb-waarde')].map(x=>x.innerText.trim()),
                  velden:[...k.querySelectorAll('.hb-veld')].map(x=>Math.round(x.getBoundingClientRect().height)),knop:k.querySelector('.hb-knop').innerText.trim(),
                  trust:[...document.querySelectorAll('.b1a-mobkaart .hb-trust li')].map(x=>x.innerText.trim()),
                  trustOnder:document.querySelector('.hb-trust').getBoundingClientRect().top>=kr.bottom}})()""")
            check(f'{tag} staging-boekkaart in plaats van de oude kaart en de datumbalk', sb['oudeKaart'] == 0 and sb['balkWeg'], str(sb))
            check(f'{tag} hero als de staging: 490 hoog, kop 44 px, kaart 24 px over de hero, kop en badge vrij, afronding 14',
                  sb['hero'][3] == 490 and sb['h1fs'] == '44px' and sb['overlap'] == 24 and sb['kopVrij'] >= 0 and sb['badge'] and sb['rad'] == '14px', str(sb))
            check(f'{tag} kaart: Aankomst en vertrek / Reisgezelschap / Type kamer, velden 56-57 px, knop Bekijk beschikbaarheid',
                  sb['labels'] == ['aankomst en vertrek', 'reisgezelschap', 'type kamer'] and sb['waarden'] == ['Kies een periode', '2 volwassenen', 'Alle types']
                  and all(56 <= x <= 57 for x in sb['velden']) and sb['knop'] == 'Bekijk beschikbaarheid' and sb['kaart'][3] == 262, str(sb))
            check(f'{tag} trust-vinkjes als compacte rij onder de kaart', len(sb['trust']) == 3 and sb['trustOnder'], str(sb['trust']))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-hero-kaart.png')
            # koppeling met Mews: periode, reisgezelschap en kamertype (gestubde widget-API)
            a = date.today() + timedelta(days=30)
            pg.fill('#hb-aankomst', a.isoformat())
            per = pg.locator('[data-periode]').inner_text()
            check(f'{tag} periode toont aankomst en vertrek (+1 nacht)', str(a.day) in per and str((a + timedelta(days=1)).day) in per and '\u2013' in per, per)
            pg.select_option('#hb-gasten', '3'); pg.select_option('#hb-kamer', 'a8fd7310-0d61-422f-89e6-af1d00ffc315')
            zicht = [x.strip() for x in pg.locator('.hb-kaart .hb-waarde').all_inner_texts()]
            check(f'{tag} zichtbare waarden volgen de keuze', zicht[1] == '3 volwassenen' and zicht[2] == 'Royale kamer', str(zicht))
            pg.evaluate("""()=>{window._mews=[];window.mewsApi={setVoucherCode:v=>window._mews.push('v:'+v),setLanguageCode:()=>{},setStartDate:d=>window._mews.push('start'),
                setEndDate:d=>window._mews.push('eind'),setAdultCount:n=>window._mews.push('n:'+n),showRates:r=>window._mews.push('rates:'+r),showRooms:()=>{},open:()=>window._mews.push('open')}}""")
            pg.locator('.hb-knop').click(); pg.wait_for_timeout(300)
            r = pg.evaluate('window._mews.slice()'); log = pg.evaluate('window.lpBoekbalk') or {}
            check(f'{tag} knop opent Mews met datums, 3 volwassenen en de Royale kamer voorgeselecteerd',
                  r == ['start', 'eind', 'n:3', 'rates:a8fd7310-0d61-422f-89e6-af1d00ffc315', 'open'] and 'mewsRoom=a8fd7310' in log.get('url', '')
                  and f'mewsStart={a.isoformat()}' in log.get('url', '') and 'mewsAdultCount=3' in log.get('url', ''), f"{r} {log.get('url')}")
            pg.evaluate("delete window.mewsApi")
        elif mob:
            # telefoon: boekkaart in plaats van de datumbalk
            mk = pg.evaluate("""(()=>{const k=document.querySelector('.b1a-mobkaart .b1k-kaart'),f=document.querySelector('.b1a-balk'),h=document.querySelector('.b1a-tekst h1, .b1a h1');
                const r=k.getBoundingClientRect(),kn=k.querySelector('.b1k-knop');
                return {kaart:r.height>(window.__arr||window.__trust?150:300)&&r.width>300, balkWeg:getComputedStyle(f).display==='none', onderKop:r.top>h.getBoundingClientRect().bottom,
                        knop:kn&&kn.classList.contains('mews-open')&&(kn.dataset.voucher||'')===%r}})()""" % VOUCHER)
            check(f'{tag} boekkaart onder de hero in plaats van de datumbalk', all(mk.values()), str(mk))
        else:
            # boekbalk (laatst, laadt de Mews-widget)
            if PRIJS:
                cv = pg.evaluate("(()=>{const i=document.getElementById('bb-code'),f=i.closest('.field').getBoundingClientRect(),r=i.getBoundingClientRect();return {waarde:i.value,cw:i.clientWidth,sw:i.scrollWidth,binnen:r.right<=f.right+1}})()")
                check(f'{tag} actiecode {VOUCHER} volledig zichtbaar in de boekbalk', cv['waarde'] == VOUCHER and cv['sw'] <= cv['cw'] + 1 and cv['binnen'], str(cv))
                # 14 tekens moeten ook passen (en de balk blijft binnen beeld)
                cv14 = pg.evaluate("(()=>{const i=document.getElementById('bb-code'),oud=i.value;i.value='OORLOGSMUSEUM2';window.dispatchEvent(new Event('resize'));"
                                   "const f=i.closest('.field').getBoundingClientRect(),r=i.getBoundingClientRect(),b=i.closest('form').getBoundingClientRect(),"
                                   "u={cw:i.clientWidth,sw:i.scrollWidth,binnen:r.right<=f.right+1,balk:b.right<=innerWidth,sw2:document.documentElement.scrollWidth};i.value=oud;window.dispatchEvent(new Event('resize'));return u})()")
                check(f'{tag} actiecode van 14 tekens past ook', cv14['sw'] <= cv14['cw'] + 1 and cv14['binnen'] and cv14['balk'] and cv14['sw2'] <= w, str(cv14))
            NACHTEN = int(pg.evaluate("document.querySelector('.b1a-balk').getAttribute('data-nachten') || '1'"))
            a = date.today() + timedelta(days=30)
            pg.fill('#bb-aankomst', a.isoformat())
            vert = pg.input_value('#bb-vertrek')
            zv_vert = pg.locator('.b1a-balk .value').all_inner_texts()[1]
            check(f'{tag} vertrek volgt aankomst + {NACHTEN} nacht' + ('en' if NACHTEN > 1 else '') + ' (ook zichtbaar)',
                  vert == (a + timedelta(days=NACHTEN)).isoformat() and zv_vert != 'Kies datum' and str((a + timedelta(days=NACHTEN)).day) in zv_vert, f'{vert} / {zv_vert}')
            if NACHTEN > 1:
                # te kort vertrek wordt bij verzenden rechtgezet (gestubde widget-API)
                pg.fill('#bb-vertrek', (a + timedelta(days=1)).isoformat())
                pg.evaluate("window._mews=[];window.mewsApi={setVoucherCode:()=>{},setLanguageCode:()=>{},setStartDate:d=>window._mews.push(d),setEndDate:d=>window._mews.push(d),setAdultCount:()=>{},open:()=>{}}")
                pg.locator('.b1a-balk button[type=submit]').click(); pg.wait_for_timeout(300)
                st = pg.evaluate("(()=>{const l=window.lpBoekbalk||{},m=window._mews;return {start:l.start,eind:l.eind,route:l.route,nachten:m.length==2?Math.round((m[1]-m[0])/864e5):null}})()")
                pg.evaluate("delete window.mewsApi")
                check(f'{tag} widget krijgt {NACHTEN} nachten, ook als het vertrek te kort stond',
                      st['route'] == 'widget' and st['nachten'] == NACHTEN and st['eind'] == (a + timedelta(days=NACHTEN)).isoformat(), str(st))
                print('     widget-log:', json.dumps(st))
            ext = max(2, NACHTEN)
            pg.fill('#bb-vertrek', (a + timedelta(days=ext)).isoformat())
            pg.select_option('#bb-gasten', '3')
            zicht = pg.locator('.b1a-balk .value').all_inner_texts()
            check(f'{tag} zichtbare waarden volgen de invoer', zicht[2] == '3 volwassenen' and zicht[0] != 'Kies datum', ' | '.join(zicht[:3]))
            popups = []
            ctx.on('page', lambda np: popups.append(np.url))
            pg.locator('.b1a-balk button[type=submit]').click()
            pg.wait_for_timeout(7000)
            log = pg.evaluate('window.lpBoekbalk') or {}
            u = log.get('url', '')
            check(f'{tag} boekbalk-URL bevat {VOUCHER}, mewsStart, mewsEnd, mewsAdultCount=3',
                  f'mewsVoucherCode={VOUCHER}' in u and f'mewsStart={a.isoformat()}' in u
                  and f'mewsEnd={(a + timedelta(days=ext)).isoformat()}' in u and 'mewsAdultCount=3' in u, u)
            widget = pg.evaluate("!!document.querySelector('iframe[src*=\"mews\"], .mews-distributor, [class*=\"mews\"] iframe')")
            check(f'{tag} boekbalk opent Mews (widget of URL-fallback)',
                  log.get('route') in ('widget', 'url (geen datum-methodes)') or len(popups) > 0,
                  f"route={log.get('route')} methodes={log.get('methodes')} iframe={widget} popups={popups}")
            print('     boekbalk-log:', json.dumps(log, ensure_ascii=False))

        eigen = [f for f in pg._fouten if 'mews' not in f.lower()]
        check(f'{tag} geen consolefouten (eigen code)', not eigen, '; '.join(eigen)[:300])
        if pg._fouten and len(eigen) != len(pg._fouten):
            print('     (Mews-meldingen genegeerd):', '; '.join(f for f in pg._fouten if f not in eigen)[:300])
        ctx.close()

        # reduced motion: statische muur
        ctx, pg = nieuwe_pagina(b, w, h, mob, rustig=True)
        st = pg.evaluate("""()=>{const m=document.querySelector('.b5a-muur');
            return {loop:m.classList.contains('is-loop'),zicht:[...m.querySelectorAll('.b5a-kaart')].filter(k=>k.offsetParent).length}}""")
        verwacht = (8 if PRIJS else 9) if w == 1440 else 5
        totaal = pg.evaluate("document.querySelectorAll('.b5a-muur .b5a-kaart').length")
        check(f'{tag} reduced-motion: statische muur', not st['loop'] and st['zicht'] == min(verwacht, totaal), str(st))
        if HOTEL and pg.evaluate("!!document.querySelector('.b1a-video')"):
            rm = pg.evaluate("(()=>{const v=document.querySelector('.b1a-video'),i=document.querySelector('.b1a-foto>img');return {video:getComputedStyle(v).display,foto:i.complete&&i.naturalWidth>0&&getComputedStyle(i).display!=='none'}})()")
            check(f'{tag} reduced-motion: geen video, alleen de poster/foto', rm['video'] == 'none' and rm['foto'], str(rm))
            fk = pg.locator('.ho-fac [data-fac="wellness"]').first; fk.scroll_into_view_if_needed(); fk.click(force=True); pg.wait_for_timeout(800)
            rf = pg.evaluate("(()=>{const d=document.getElementById('lp-pop-fac'),v=d.querySelector('.lp-pop__video'),h=d.querySelector('.lp-pop__hero');return {open:d.open,video:!!(v&&!v.hidden&&v.getAttribute('src')),foto:!h.hidden&&!!h.getAttribute('src')}})()")
            check(f'{tag} reduced-motion: wellness-pop-up zonder video, met foto', rf['open'] and not rf['video'] and rf['foto'], str(rf))
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-hero-reduced-motion.png')
        if shotdir:
            pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
            pg.wait_for_timeout(1500)
            H = pg.evaluate('document.documentElement.scrollHeight')
            pg.set_viewport_size({'width': w, 'height': H}); pg.wait_for_timeout(600)
            pg.screenshot(path=f'{shotdir}/{NAAM}-{w}.png')
        ctx.close()
    if PRIJS:
        for w, h, mob in [(1440, 900, False), (390, 844, True)]:
            # ?zv= doet niets meer: geen keuzeschakelaar, hetzelfde zondagblok
            ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
            ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
            pg = ctx.new_page(); fz = []
            pg.on('pageerror', lambda e: fz.append(str(e)))
            pg.goto(URL + '?zv=c', wait_until='networkidle'); pg.wait_for_timeout(400)
            z = pg.evaluate("({kiezer:!!document.querySelector('.ar-zv-kiezer,.ar-zv-optie'),zv:!!document.querySelector('.ar-zv'),n:document.querySelectorAll('.ar-zv .ar-zv-kaart').length,sw:document.documentElement.scrollWidth})")
            check(f'[{w}] ?zv=c: geen keuzeschakelaar, ' + ('zondagblok met 2 kaarten' if z['zv'] else 'geen zondagblok'),
                  not z['kiezer'] and z['n'] == (2 if z['zv'] else 0) and z['sw'] <= w and not fz, str(z) + ' ' + '; '.join(fz))
            if shotdir and z['zv']:
                pg.locator('.ar-zv').scroll_into_view_if_needed(); pg.wait_for_timeout(900)
                pg.locator('.ar-zv').screenshot(path=f'{shotdir}/{NAAM}-{w}-zondag.png')
            ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK')
sys.exit(1 if mis else 0)
