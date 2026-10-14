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

Upgradeblok A · Ladder-slider (blok 3a-variant 'ladder', aan via UPGRADE_LADDER in de JSON, nu alleen bedankt):
  ... http://localhost:8765/bedankt.html --v3 --voucher BEDANKT --ladder
Met --ladder: blok aanwezig (ster-split weg, kop blijft), teller 1 van 4, beginstand (vorige uit), volgende/vorige,
geen lus aan het eind (volgende uit), streepjes, pijltjestoetsen, swipe (scrollpositie), alleen de actieve stap voor
schermlezers, kaarten passen in de kolom (1440: links van de zijkaart; 390: onder elkaar). Zonder --ladder: blok afwezig.
"""
import sys, json
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
shotdir = None
V3 = '--v3' in args
if V3: args.remove('--v3')
LADDER = '--ladder' in args
if LADDER: args.remove('--ladder')
VOUCHER = 'JUBILEUM'
if '--voucher' in args:
    i = args.index('--voucher'); VOUCHER = args[i + 1]; del args[i:i + 2]
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else 'http://localhost:8765/verblijfsverjaardag-v2.html'
NAAM = URL.rstrip('/').rsplit('/', 1)[-1].replace('.html', '')
fouten, resultaten = [], []

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def nieuwe_pagina(b, w, h, mob, rustig=False):
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob,
                        reduced_motion='reduce' if rustig else 'no-preference')
    ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
    pg = ctx.new_page()
    pg._fouten = []
    pg.on('console', lambda m: pg._fouten.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: pg._fouten.append(str(e)))
    pg.goto(URL, wait_until='networkidle')
    pg.wait_for_timeout(600)
    return ctx, pg

with sync_playwright() as p:
    b = p.chromium.launch()
    for w in ((1280, 1100, 1024, 800) if V3 else (1100, 800)):
        ctx, pg = nieuwe_pagina(b, w, 900, False)
        pg.evaluate("window.scrollTo(0, document.querySelector('.b4b').offsetTop)"); pg.wait_for_timeout(800)
        if V3:
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'[{w}] geen horizontale overloop', sw <= w, f'scrollWidth {sw}')
            if w == 1100:
                pg.evaluate("window.scrollTo(0, document.querySelector('.b2a').getBoundingClientRect().top + scrollY - 150)"); pg.wait_for_timeout(700)
                z = pg.evaluate("""()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect(),s=document.querySelector('.b2a-strook').getBoundingClientRect();
                    return {kl:k.left,kr:k.right,kt:k.top,sr:s.right,st:s.top,sb:s.bottom}}""")
                check(f'[{w}] kaart naast de tegels', z['kl'] > z['sr'] and z['kr'] <= w and z['kt'] < z['sb'], str(z))
            if w == 800:
                z = pg.evaluate("""()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast'),r=k.getBoundingClientRect(),a=document.querySelector('.b3a').getBoundingClientRect(),
                    m=document.querySelector('.b4b').getBoundingClientRect();return {w:r.width,pos:getComputedStyle(k).position,na3a:r.top+scrollY>=a.bottom+scrollY-1,voor4b:r.bottom<=m.top+1}}""")
                check(f'[{w}] kaart als blok tussen attentie en kamers', z['w'] > 0 and z['pos'] != 'sticky' and z['na3a'] and z['voor4b'], str(z))
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

        # upgradeblok A · Ladder-slider
        if not LADDER:
            check(f'{tag} geen upgradeblok (ladder), ster-split aanwezig', pg.locator('.b3l').count() == 0 and pg.locator('#attentie .b3a-grid').count() == 1)
        else:
            check(f'{tag} upgradeblok aanwezig in #attentie, ster-split weg, kop blijft',
                  pg.locator('#attentie .b3l').count() == 1 and pg.locator('.b3a-grid').count() == 0 and pg.locator('#attentie .b3a-ster').count() == 1
                  and 'de upgrade' in pg.locator('#attentie h2').inner_text() and pg.locator('.b3l-stap').count() == 4)
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
            check(f'{tag} ladder beginstand: 1 van 4, vorige uit, volgende aan', s0['nu'] == '1' and '4' in s0['tot'] and s0['vorige'] == 'true'
                  and s0['volgende'] == 'false' and s0['dot'] == '1' and s0['zicht'] == '1' and s0['pos'] == 0, str(s0))
            pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900); s1 = ls()
            check(f'{tag} ladder volgende: 2 van 4, streepje 2, vorige aan', s1['nu'] == '2' and s1['dot'] == '2' and s1['zicht'] == '2'
                  and s1['vorige'] == 'false' and s1['pos'] == 1, str(s1))
            pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900)
            pg.locator('.b3l-volgende').click(); pg.wait_for_timeout(900); s3 = ls()
            pg.locator('.b3l-volgende').click(force=True); pg.wait_for_timeout(900); s4 = ls()   # aria-disabled: klik moet niets doen
            check(f'{tag} ladder eindstand: 4 van 4, volgende uit, geen lus', s3['nu'] == '4' and s3['volgende'] == 'true' and s4['nu'] == '4'
                  and s4['pos'] == 3 and s4['zicht'] == '4', f'{s3} / {s4}')
            pg.locator('.b3l-vorige').click(); pg.wait_for_timeout(900); s5 = ls()
            check(f'{tag} ladder vorige: 3 van 4, volgende weer aan', s5['nu'] == '3' and s5['volgende'] == 'false' and s5['dot'] == '3', str(s5))
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

        # kamerslider
        tel = lambda: pg.locator('.b4b-nu').inner_text()
        check(f'{tag} kamerteller start op 1 van 8', tel() == '1' and '8' in pg.locator('.b4b-tel').inner_text())
        pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(900)
        t2 = tel()
        pg.locator('.b4b-vorige').click(); pg.wait_for_timeout(900)
        t1 = tel()
        pg.locator('.b4b-vorige').click(); pg.wait_for_timeout(900)
        t8 = tel()
        check(f'{tag} pijlen werken (volgende 2, vorige 1, vorige 8)', (t2, t1, t8) == ('2', '1', '8'), f'{t2},{t1},{t8}')
        actief = lambda: pg.evaluate("[...document.querySelectorAll('.b4b-dot')].map((d,i)=>d.classList.contains('is-active')?i+1:0).filter(Boolean).join(',')")
        check(f'{tag} streepjes volgen de teller (8 stuks, actief 8)', pg.locator('.b4b-dot').count() == 8 and actief() == '8', actief())
        pg.locator('.b4b-dot').nth(3).click(); pg.wait_for_timeout(1100)
        t4 = tel(); a4 = actief()
        check(f'{tag} klik op streepje 4 springt naar kamer 4', t4 == '4' and a4 == '4', f'{t4} / {a4}')
        pg.locator('.b4b-dot').nth(7).click(); pg.wait_for_timeout(1100)
        pg.locator('.b4b-volgende').click(); pg.wait_for_timeout(900)

        # Bekijk kamer -> pop-up
        knop = pg.locator('.b4b-kaart:not([data-kloon]) [data-kamer="royale"]')
        knop.scroll_into_view_if_needed(); knop.click(force=True); pg.wait_for_timeout(500)
        titel = pg.locator('#lp-pop-kamer-naam').inner_text()
        room = pg.locator('#lp-pop-kamer .lp-pop__boek').get_attribute('data-room')
        check(f'{tag} Bekijk kamer opent pop-up met juiste kamer en data-room',
              pg.evaluate("document.getElementById('lp-pop-kamer').open") and titel == 'Royale kamer'
              and room == 'a8fd7310-0d61-422f-89e6-af1d00ffc315', f'{titel} / {room}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

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
            pg.evaluate("window.scrollTo(0, document.querySelector('.b2a').offsetTop + 400)"); pg.wait_for_timeout(700)
            na = pg.evaluate("document.querySelector('.mob-cta').classList.contains('is-zichtbaar')")
            check(f'{tag} onderbalk verschijnt na de hero', (not vooraf) and na, f'voor {vooraf}, na {na}')
            pg.wait_for_timeout(400)
            echt = pg.evaluate("""(()=>{const m=document.querySelector('.mob-cta'),r=m.getBoundingClientRect(),c=getComputedStyle(m);return c.display!=='none'&&c.visibility==='visible'&&r.height>40&&r.bottom<=innerHeight+1&&r.top<innerHeight})()""")
            check(f'{tag} onderbalk echt zichtbaar onderin beeld', echt)
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)

        if V3:
            geen = pg.evaluate("!document.querySelector('.b1k-uitklap, .b1k-tab, .b1k-paneel')")
            check(f'{tag} geen uitklaptab in de pagina', geen)
            if mob:
                zk = pg.evaluate("document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect().width")
                check(f'{tag} geen zijkaart op de telefoon', zk == 0, str(zk))
            else:
                kaart = """()=>{const k=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect(),kop=document.querySelector('.top-stack').getBoundingClientRect().bottom,
                    s=document.querySelector('.b2a-strook').getBoundingClientRect(),m=document.querySelector('.b5a').getBoundingClientRect();
                    return {l:Math.round(k.left),r:Math.round(k.right),t:Math.round(k.top),b:Math.round(k.bottom),kop:Math.round(kop),sr:Math.round(s.right),st:Math.round(s.top),sb:Math.round(s.bottom),m5:Math.round(m.top)}}"""
                pg.evaluate("window.scrollTo(0, document.querySelector('.b2a-strook').getBoundingClientRect().top + scrollY - document.querySelector('.top-stack').offsetHeight - 24)"); pg.wait_for_timeout(700)
                z = pg.evaluate(kaart)
                check(f'{tag} kaart zichtbaar naast de tegels', z['l'] > z['sr'] and z['r'] <= w and abs(z['t'] - z['st']) <= 4 and z['b'] <= h, str(z))
                if shotdir: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-tegels.png')
                pg.evaluate("(()=>{const s=document.querySelector('.b4b-strook');window.scrollTo(0, s.getBoundingClientRect().top + scrollY + s.offsetHeight/2 - innerHeight/2)})()"); pg.wait_for_timeout(700)
                z = pg.evaluate(kaart)
                check(f'{tag} kaart in beeld midden kamerslider', z['b'] > z['kop'] + 200 and z['t'] <= z['kop'] + 40, str(z))
                eind = pg.evaluate("(()=>{const k=document.querySelector('.lp-zone .b4b-kaart:not([data-kloon])');window.scrollTo(0, k.getBoundingClientRect().bottom + scrollY - innerHeight + 150);const a=document.querySelector('.lp-zone-kant .b1k-kaart--vast').getBoundingClientRect().bottom,b=k.getBoundingClientRect().bottom;return [Math.round(a),Math.round(b)]})()")
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
                return {kaart:r.height>300&&r.width>300, balkWeg:getComputedStyle(f).display==='none', onderKop:r.top>h.getBoundingClientRect().bottom,
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
        verwacht = 9 if w == 1440 else 5
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
