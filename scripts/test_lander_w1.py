#!/usr/bin/env python3
"""Playwright-test voor de lander W1 (verblijfsverjaardag-v2).

Gebruik:
  python3 -m http.server 8765        # in de repo-root, in een tweede terminal
  python3 scripts/test_lander_w1.py [basis-url] [--schermafdruk map]

Standaard basis-url: http://localhost:8765/verblijfsverjaardag-v2.html
Checks (1440 en 390): geen horizontale overloop, boekbalk (voucher, datums, reisgezelschap naar
Mews-widget of URL-fallback), kamerslider (teller 1 van 8, pijlen, lus), Bekijk kamer-pop-up
met data-room, Wellness-/Restaurant-pop-up uit de tegelstrook (titel, link, foto's, past in beeld, Escape/kruisje/
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
  ... http://localhost:8765/najaarsarrangement-v2.html --v3 --voucher NAJAAR2D --arrangement "€ 128,50"
Extra: robots noindex, alle Mews-links met de voucher, geen oude config bee2f902 in de bron, prijs zichtbaar in de
zijkaart (1440) en in de onderbalk (390). Kamerslider-checks volgen het aantal kamers op de pagina (8 of minder).
"""
import sys, json
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
shotdir = None
V3 = '--v3' in args
if V3: args.remove('--v3')
VOUCHER = 'JUBILEUM'
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
ANKERS = ("window.__anker='.ar-inb .wrap';window.__ankerSec='.ar-inb';window.__voor='.ar-inb';window.__na='.ar-zv';window.__arr=true;"
          if PRIJS else
          "window.__anker='.b2a-strook';window.__ankerSec='.b2a';window.__voor='.b3a';window.__na='.b4b';window.__arr=false;")

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def nieuwe_pagina(b, w, h, mob, rustig=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob,
                        reduced_motion='reduce' if rustig else 'no-preference')
    ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
    ctx.add_init_script(ANKERS)
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
        ctx, pg = nieuwe_pagina(b, 1440, 900, False)
        links = pg.evaluate("[...document.querySelectorAll('a[href*=\"app.mews.com\"]')].map(a=>a.getAttribute('href'))")
        zonder = [l for l in links if 'mewsVoucherCode=' + VOUCHER not in l or '6dc9094c-76e3-4fd8-83a7-af1d00ffc556' not in l]
        check(f'[bron] alle {len(links)} Mews-links op config 6dc9094c met {VOUCHER}', links and not zonder, '; '.join(zonder)[:300])
        kamers = pg.evaluate("[...document.querySelectorAll('.b4b-kaart:not([data-kloon]) .b4b-knoppen a.mews-open')].map(a=>a.getAttribute('href'))")
        check('[bron] kamerknoppen met mewsRoom en mewsRoute=rooms', kamers and all('mewsRoom=' in k and 'mewsRoute=rooms' in k for k in kamers), str(len(kamers)))
        ctx.close()
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
        else:
            pg.locator('.b1k-tab').click(); pg.wait_for_timeout(700)
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'[{w}] geen horizontale overloop (tab + open kaart)', sw <= w, f'scrollWidth {sw}')
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
            check(f'{tag} code {VOUCHER} in de tekst', VOUCHER in tekst)

        # FAQ
        open_ = pg.evaluate("[...document.querySelectorAll('.b6c details')].map(d=>d.open)")
        check(f'{tag} eerste FAQ open, rest dicht', open_[0] and not any(open_[1:]), str(open_))

        raster = pg.evaluate("!!document.querySelector('.ar-kamers')")
        if raster:
            r = pg.evaluate("""(()=>{const g=document.querySelector('.ar-kamers'),k=[...g.querySelectorAll('.b4b-kaart')].map(x=>x.getBoundingClientRect());
                return {n:k.length,n_attr:+g.dataset.n,strook:!!document.querySelector('.b4b-strook, .b4b-teller, .b4b-dots'),klonen:document.querySelectorAll('[data-kloon]').length,
                  rij:k.every(x=>Math.abs(x.top-k[0].top)<2),peek:k.length>1&&k[1].left<innerWidth&&k[1].right>innerWidth,veeg:g.scrollWidth>g.clientWidth+10,
                  prijs:[...g.querySelectorAll('.ar-kprijs')].length,rand:getComputedStyle(g.querySelector('.ar-kaart-inbegrepen')).boxShadow.includes('199, 110, 78')}})()""")
            check(f'{tag} kamerraster bij {r["n"]} kamers: geen slider, teller, streepjes of klonen', r['n'] <= 3 and r['n'] == r['n_attr'] and not r['strook'] and r['klonen'] == 0, str(r))
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

        if PRIJS:
            a = pg.evaluate("""(()=>{const q=s=>document.querySelector(s),zv=q('.ar-zv'),wa=q('.ar-waarom'),kant=q('.lp-zone-kant'),an=q('.ar-andere');
                return {zv:!!zv&&zv.querySelectorAll('.ar-zv-kaart').length===2&&!!zv.querySelector('.ar-zv-kaart--zondag .ar-zv-pil')&&!!zv.querySelector('.ar-zv-noot')&&!!zv.querySelector('s'),
                  zvKop:zv?zv.querySelector('h2').innerText.replace(/\\u00a0/g,' '):'',
                  wKop:wa?wa.querySelector('h2').innerText:'',wPunten:wa?wa.querySelectorAll('.as-usp-wheel-item').length:0,
                  wFoto:wa?(i=>i.complete&&i.naturalWidth>0)(wa.querySelector('.b3a-foto img')):false,
                  wKnop:wa?wa.querySelector('.mews-open').dataset.voucher:'',
                  kantFoto:kant?kant.querySelectorAll('img').length:-1,kantPrijs:kant?!!kant.querySelector('.b1k-prijs'):false,
                  andere:an?[...an.querySelectorAll('a.ar-ander')].map(x=>x.getAttribute('href')):[],
                  chips:document.querySelectorAll('.ar-chips li').length,
                  faq:[...document.querySelectorAll('.b6c summary')].map(s=>s.innerText)}})()""")
            check(f'{tag} zondagblok: twee kaarten, pil, doorgestreepte prijs, voetnoot', a['zv'] and 'Op zondag' in a['zvKop'] and '20 per kamer' in a['zvKop'], str(a)[:300])
            check(f'{tag} Waarom Asteria: kop, zes punten, foto geladen, knop met {VOUCHER}',
                  a['wKop'].startswith('Voor de grote dagen') and a['wPunten'] == 6 and a['wFoto'] and a['wKnop'] == VOUCHER, str(a)[:300])
            check(f'{tag} zijkaart zonder foto, met prijs', a['kantFoto'] == 0 and a['kantPrijs'], str(a)[:200])
            check(f'{tag} drie andere arrangementen met link', len(a['andere']) == 3 and all(h.startswith('https://') for h in a['andere']), str(a['andere']))
            check(f'{tag} drie chips onder de hero', a['chips'] == 3, str(a['chips']))
            check(f'{tag} FAQ: zes vragen, eerste over het arrangement', len(a['faq']) == 6 and 'arrangement' in a['faq'][0], ' | '.join(a['faq']))
            ok_rev = pg.evaluate("(()=>{const m=document.querySelector('.b5a-muur');return m.classList.contains('is-loop')?[...m.querySelectorAll('.b5a-baan .b5a-kaart:not([aria-hidden])')].length:m.querySelectorAll('.b5a-kaart').length})()")
            check(f'{tag} reviewmuur: precies 8 of 12 kaarten', ok_rev in (8, 12), str(ok_rev))

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

        if PRIJS:
            check(f'{tag} geen tegelstrook (b2a) op de arrangementpagina', pg.evaluate("!document.querySelector('.b2a, .b2a-strook')"))
        else:
            # tegelstrook: Wellness- en Restaurant-knop -> faciliteiten-pop-up
            for key, titel_v, link_v in (('wellness', 'Wellness op de Top Floor', 'https://www.asteria.nl/wellness'),
                                         ('restaurant', 'Restaurant en terras', 'https://www.asteria.nl/restaurant')):
                fk = pg.locator(f'.b2a-strook [data-fac="{key}"]').first
                tegel = pg.locator(f'.b2a-strook .b2a-tegel:has([data-fac="{key}"])').first
                tegel.scroll_into_view_if_needed()
                if not mob: tegel.hover()
                pg.wait_for_timeout(700)
                fk.click(); pg.wait_for_timeout(1200)
                f = pg.evaluate("""()=>{const d=document.getElementById('lp-pop-fac'),r=d.getBoundingClientRect(),bi=d.querySelector('.lp-pop__binnen');
                    const imgs=[...d.querySelectorAll('.lp-pop__hero,.lp-pop__fotos img')];
                    return {open:d.open,titel:d.querySelector('.lp-pop__titel').textContent,link:d.querySelector('.lp-pop__meer').getAttribute('href'),
                      fotos:imgs.length,geladen:imgs.filter(i=>i.complete&&i.naturalWidth>0).length,chips:d.querySelectorAll('.lp-pop__chips li').length,
                      t:Math.round(r.top),b:Math.round(r.bottom),l:Math.round(r.left),r:Math.round(r.right),
                      scroll:bi.scrollHeight-bi.clientHeight,sw:document.documentElement.scrollWidth}}""")
                check(f'{tag} {key}-knop opent pop-up met juiste titel, link en geladen foto\'s',
                      f['open'] and f['titel'] == titel_v and f['link'] == link_v and f['fotos'] == 4 and f['geladen'] == 4 and f['chips'] == 4, str(f))
                check(f'{tag} {key}-pop-up past in beeld' + (', zonder scrollen' if not mob else ''),
                      f['t'] >= 0 and f['l'] >= 0 and f['r'] <= w and f['b'] <= h and f['sw'] <= w and (mob or f['scroll'] <= 1), str(f))
                if shotdir:
                    pg.screenshot(path=f'{shotdir}/{NAAM}-fac-{key}-{w}.png')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
                dicht = pg.evaluate("""k=>({open:document.getElementById('lp-pop-fac').open,focus:document.activeElement===document.querySelector('.b2a-strook [data-fac="'+k+'"]')})""", key)
                check(f'{tag} Escape sluit de {key}-pop-up, focus terug op de knop', not dicht['open'] and dicht['focus'], str(dicht))
            # sluiten via kruisje en via de achtergrond
            def open_wellness():
                tegel = pg.locator('.b2a-strook .b2a-wellness').first
                tegel.scroll_into_view_if_needed()
                if not mob: tegel.hover()
                pg.wait_for_timeout(700)
                pg.locator('.b2a-strook [data-fac="wellness"]').first.click(); pg.wait_for_timeout(500)
            open_wellness()
            pg.locator('#lp-pop-fac .lp-pop__sluit').click(); pg.wait_for_timeout(400)
            x1 = pg.evaluate("document.getElementById('lp-pop-fac').open")
            open_wellness()
            pg.mouse.click(3, 3); pg.wait_for_timeout(400)
            x2 = pg.evaluate("document.getElementById('lp-pop-fac').open")
            check(f'{tag} kruisje en klik op de achtergrond sluiten de pop-up', not x1 and not x2, f'{x1}/{x2}')

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
                check(f'{tag} knop in de kaart opent Mews met voucher {VOUCHER}', r == ['v:' + VOUCHER, 'open'], str(r))
                pg.evaluate("delete window.mewsApi")
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)

        # uitklaptab (alleen >= 720): verborgen bovenaan, zichtbaar na de hero, weg bij slotblok 7a
        tabst = lambda: pg.evaluate("""()=>{const u=document.querySelector('.b1k-uitklap'),t=u.querySelector('.b1k-tab'),r=t.getBoundingClientRect(),cs=getComputedStyle(t);
            return {zicht:cs.display!=='none'&&cs.visibility==='visible'&&r.width>0&&r.left<innerWidth,aria:u.getAttribute('aria-hidden'),tab:t.getAttribute('tabindex')}}""")
        if not V3:
          pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(600)
          t0 = tabst()
          pg.evaluate("window.scrollTo(0, document.querySelector('.b4b').offsetTop)"); pg.wait_for_timeout(900)
          t1 = tabst()
        if V3:
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
            check(f'{tag} knop in de kaart opent Mews met voucher {VOUCHER}', r == ['v:' + VOUCHER, 'open'], str(r))
            pg.evaluate("delete window.mewsApi")
            pg.evaluate("document.querySelector('.b7a').scrollIntoView({block:'center'})"); pg.wait_for_timeout(900)
            t2 = tabst()
            pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(900)
            t3 = tabst()
            check(f'{tag} uitklaptab weg bij het slotblok en daarna', not t2['zicht'] and not t3['zicht'] and t2['aria'] == 'true', f"{t2} / {t3}")
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)

        if mob:
            # telefoon: boekkaart in plaats van de datumbalk
            mk = pg.evaluate("""(()=>{const k=document.querySelector('.b1a-mobkaart .b1k-kaart'),f=document.querySelector('.b1a-balk'),h=document.querySelector('.b1a-tekst h1, .b1a h1');
                const r=k.getBoundingClientRect(),kn=k.querySelector('.b1k-knop');
                return {kaart:r.height>(window.__arr?150:300)&&r.width>300, balkWeg:getComputedStyle(f).display==='none', onderKop:r.top>h.getBoundingClientRect().bottom,
                        knop:kn&&kn.classList.contains('mews-open')&&kn.dataset.voucher===%r}})()""" % VOUCHER)
            check(f'{tag} boekkaart onder de hero in plaats van de datumbalk', all(mk.values()), str(mk))
        else:
            # boekbalk (laatst, laadt de Mews-widget)
            a = date.today() + timedelta(days=30)
            pg.fill('#bb-aankomst', a.isoformat())
            vert = pg.input_value('#bb-vertrek')
            check(f'{tag} vertrek volgt aankomst + 1 nacht', vert == (a + timedelta(days=1)).isoformat(), vert)
            pg.fill('#bb-vertrek', (a + timedelta(days=2)).isoformat())
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
                  and f'mewsEnd={(a + timedelta(days=2)).isoformat()}' in u and 'mewsAdultCount=3' in u, u)
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
        if shotdir:
            pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
            pg.wait_for_timeout(1500)
            H = pg.evaluate('document.documentElement.scrollHeight')
            pg.set_viewport_size({'width': w, 'height': H}); pg.wait_for_timeout(600)
            pg.screenshot(path=f'{shotdir}/{NAAM}-{w}.png')
        ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK')
sys.exit(1 if mis else 0)
