#!/usr/bin/env python3
"""Playwright-test voor de lander W1 (verblijfsverjaardag-v2).

Gebruik:
  python3 -m http.server 8765        # in de repo-root, in een tweede terminal
  python3 scripts/test_lander_w1.py [basis-url] [--schermafdruk map]

Standaard basis-url: http://localhost:8765/verblijfsverjaardag-v2.html
Checks (1440 en 390): geen horizontale overloop, boekbalk (voucher, datums, reisgezelschap naar
Mews-widget of URL-fallback), kamerslider (teller 1 van 8, pijlen, lus), Bekijk kamer-pop-up
met data-room, reviewmuur (4 kolommen op 1440, 1 op 390, pauze bij hover, statisch bij
prefers-reduced-motion), eerste FAQ open, onderbalk na de hero op 390, geen consolefouten.
"""
import sys, json
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
shotdir = None
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else 'http://localhost:8765/verblijfsverjaardag-v2.html'
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
    for w, h, mob in [(1440, 900, False), (390, 844, True)]:
        tag = f'[{w}]'
        ctx, pg = nieuwe_pagina(b, w, h, mob)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        check(f'{tag} geen horizontale overloop', sw <= w, f'scrollWidth {sw}')

        # FAQ
        open_ = pg.evaluate("[...document.querySelectorAll('.b6c details')].map(d=>d.open)")
        check(f'{tag} eerste FAQ open, rest dicht', open_[0] and not any(open_[1:]), str(open_))

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
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)

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
        check(f'{tag} boekbalk-URL bevat JUBILEUM, mewsStart, mewsEnd, mewsAdultCount=3',
              'mewsVoucherCode=JUBILEUM' in u and f'mewsStart={a.isoformat()}' in u
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
            pg.screenshot(path=f'{shotdir}/verblijfsverjaardag-v2-{w}.png')
        ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK')
sys.exit(1 if mis else 0)
