#!/usr/bin/env python3
"""Playwright-test voor de seizoenslanders (seizoen.template.html; standaard herfst), afgeleid van test_lander_w1.py.

Gebruik:
  python3 -m http.server 8765        # in de repo-root, in een tweede terminal
  python3 scripts/test_seizoen.py <seizoen|url> [--schermafdruk map]   # bv. lente --schermafdruk qa/lente

Standaard basis-url: http://localhost:8765/herfst.html (lente: .../lente.html enz.)
Checks (1440 en 390): geen horizontale overloop, noindex, alle foto's laden, kamerslider (teller 1/8, pijlen, lus),
Meer info opent de pop-up met de juiste kamer en data-room, momentenlijst (bureaublad: wisselt foto, telefoon:
accordeon), omgeving (foto + drie regels), reviewmuur (4 kolommen op 1440, 1 op 390, pauze bij hover, statisch bij prefers-reduced-motion),
onderbalk na de hero op 390, Kies deze kamer opent de Mews-poort met data-room en zonder voucher, geen consolefouten.
"""
import sys
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
shotdir = None
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
SEIZOENEN = ('herfst', 'lente', 'zomer', 'winter')
if args and args[0] in SEIZOENEN:
    args[0] = f'http://localhost:8765/{args[0]}.html'
URL = args[0] if args else 'http://localhost:8765/herfst.html'
resultaten = []
ROYALE = 'a8fd7310-0d61-422f-89e6-af1d00ffc315'

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

def alle_fotos_laden(pg):
    pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    pg.wait_for_timeout(300)
    pg.wait_for_function("[...document.images].every(i=>i.complete)", timeout=20000)
    return pg.evaluate("[...document.images].filter(i=>i.currentSrc && !i.currentSrc.startsWith('data:') && i.naturalWidth===0).map(i=>i.currentSrc)")

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, mob in [(1440, 900, False), (390, 844, True)]:
        tag = f'[{w}]'
        ctx, pg = nieuwe_pagina(b, w, h, mob)
        sw = pg.evaluate('document.documentElement.scrollWidth')
        check(f'{tag} geen horizontale overloop', sw <= w, f'scrollWidth {sw}')
        if not mob:
            robots = pg.evaluate("document.querySelector('meta[name=robots]').content")
            check(f'{tag} noindex', 'noindex' in robots, robots)
        kapot = alle_fotos_laden(pg)
        check(f'{tag} alle foto\'s laden', not kapot, ', '.join(kapot)[:300])

        # kamerslider
        tel = lambda: pg.locator('.hf-nu').first.inner_text()
        tel_zicht = lambda: [t for t, v in zip(pg.locator('.hf-nu').all_inner_texts(), pg.evaluate("[...document.querySelectorAll('.hf-nu')].map(e=>!!e.offsetParent)")) if v][0]
        check(f'{tag} kamerteller start op 1/8', tel_zicht() == '1/8', tel_zicht())
        vol = pg.locator('.hf-volgende').nth(1 if mob else 0)
        vor = pg.locator('.hf-vorige').nth(1 if mob else 0)
        vol.scroll_into_view_if_needed()
        vol.click(); pg.wait_for_timeout(900); t2 = tel_zicht()
        vor.click(); pg.wait_for_timeout(900); t1 = tel_zicht()
        vor.click(); pg.wait_for_timeout(900); t8 = tel_zicht()
        check(f'{tag} pijlen werken (volgende 2/8, vorige 1/8, vorige 8/8)', (t2, t1, t8) == ('2/8', '1/8', '8/8'), f'{t2},{t1},{t8}')
        vol.click(); pg.wait_for_timeout(900)
        aantal = pg.evaluate("document.querySelectorAll('.hf-strook .hf-kaart:not([data-kloon])').length")
        prijzen = pg.evaluate("[...document.querySelectorAll('.hf-strook .hf-kaart:not([data-kloon]) .hf-prijs b')].map(b=>b.textContent)")
        check(f'{tag} acht kamers met vanaf-prijs', aantal == 8 and len(prijzen) == 8 and all('€' in x for x in prijzen), ' | '.join(prijzen))

        # Meer info -> pop-up
        knop = pg.locator('.hf-kaart:not([data-kloon]) [data-kamer="royale"]')
        knop.scroll_into_view_if_needed(); knop.click(force=True); pg.wait_for_timeout(500)
        titel = pg.locator('#lp-pop-kamer-naam').inner_text()
        room = pg.locator('#lp-pop-kamer .lp-pop__boek').get_attribute('data-room')
        href = pg.locator('#lp-pop-kamer .lp-pop__boek').get_attribute('href')
        check(f'{tag} Meer info opent pop-up met juiste kamer en data-room',
              pg.evaluate("document.getElementById('lp-pop-kamer').open") and titel == 'Royale kamer' and room == ROYALE
              and 'mewsVoucherCode' not in href and f'mewsRoom={ROYALE}' in href, f'{titel} / {room} / {href}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

        # momentenlijst
        pg.locator('.hf-momenten').scroll_into_view_if_needed()
        open_ = lambda: pg.evaluate("[...document.querySelectorAll('.hf-moment')].map(l=>l.classList.contains('is-open'))")
        start = open_()
        check(f'{tag} momenten: eerste open, rest dicht', start == [True, False, False, False], str(start))
        src0 = pg.evaluate("document.querySelector('.hf-dag-foto').getAttribute('src')")
        pg.locator('.hf-moment').nth(2).locator('.hf-moment-kop').click(); pg.wait_for_timeout(900)
        na = open_()
        src1 = pg.evaluate("document.querySelector('.hf-dag-foto').getAttribute('src')")
        tagtekst = pg.locator('.hf-dag-tag').inner_text()
        zichtbaar = pg.evaluate("getComputedStyle(document.querySelector('.hf-moment:nth-child(3) .hf-open')).display !== 'none'")
        if not mob:
            check(f'{tag} klik op Namiddag opent dat moment en wisselt de foto',
                  na == [False, False, True, False] and src1 == pg.evaluate("document.querySelector('.hf-moment:nth-child(3)').dataset.foto") and src1 != src0 and zichtbaar
                  and pg.evaluate("getComputedStyle(document.querySelector('.hf-dag-foto')).opacity") == '1',
                  f'{na} {src1} tag={tagtekst}')
        else:
            pg.locator('.hf-moment').nth(2).locator('.hf-moment-kop').click(); pg.wait_for_timeout(400)
            dicht = open_()
            check(f'{tag} accordeon: Namiddag klapt open en weer dicht, foto blijft',
                  na == [True, False, True, False] and dicht == [True, False, False, False] and src1 == src0 and zichtbaar,
                  f'{na} -> {dicht}, foto {src1}')

        # omgeving (6i): staande foto en drie regels met thumbnail, naam en regel
        omg = pg.evaluate("""()=>[...document.querySelectorAll('.hf-omg-rij')].map(r=>({img:r.querySelector('img').naturalWidth>0,
            naam:r.querySelector('.hf-omg-naam').textContent.trim(),regel:r.querySelector('.hf-omg-regel').textContent.trim(),href:r.getAttribute('href')}))""")
        check(f'{tag} omgeving: foto en drie regels met foto, naam en regel',
              len(omg) == 3 and all(o['img'] and o['naam'] and o['regel'] and o['href'].startswith('http') for o in omg)
              and pg.evaluate("document.querySelector('.hf-omg-foto').naturalWidth>0"), ' | '.join(o['naam'] for o in omg))

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
            pg.evaluate("window.scrollTo(0, document.querySelector('.hf-intro').offsetTop + 400)"); pg.wait_for_timeout(700)
            na_ = pg.evaluate("document.querySelector('.mob-cta').classList.contains('is-zichtbaar')")
            href = pg.evaluate("document.querySelector('.mob-cta .btn').getAttribute('href')")
            check(f'{tag} onderbalk verschijnt na de hero en wijst naar #kamers', (not vooraf) and na_ and href == '#kamers', f'voor {vooraf}, na {na_}, {href}')
            pg.wait_for_timeout(400)
            echt = pg.evaluate("""(()=>{const m=document.querySelector('.mob-cta'),r=m.getBoundingClientRect(),c=getComputedStyle(m);return c.display!=='none'&&c.visibility==='visible'&&r.height>40&&r.bottom<=innerHeight+1&&r.top<innerHeight})()""")
            check(f'{tag} onderbalk echt zichtbaar onderin beeld', echt)
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)

        # Kies deze kamer -> Mews-poort (laatst, laadt de widget)
        popups = []
        ctx.on('page', lambda np: popups.append(np.url))
        kies = pg.locator(f'.hf-kaart:not([data-kloon]) a.mews-open[data-room="{ROYALE}"]')
        kies_href = kies.get_attribute('href')
        check(f'{tag} Kies deze kamer: data-room, geen voucher',
              kies.get_attribute('data-voucher') is None and 'mewsVoucherCode' not in kies_href and f'mewsRoom={ROYALE}' in kies_href, kies_href)
        kies.scroll_into_view_if_needed(); kies.click(force=True)
        pg.wait_for_timeout(7000)
        mews = pg.evaluate("!!document.querySelector('script[src*=\"distributor.min.js\"]')")
        widget = pg.evaluate("!!window.mewsApi")
        check(f'{tag} Kies deze kamer opent de Mews-poort (widget of deeplink)', mews and (widget or len(popups) > 0),
              f'script={mews} api={widget} popups={popups}')

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
            alle_fotos_laden(pg)
            pg.wait_for_timeout(800)
            H = pg.evaluate('document.documentElement.scrollHeight')
            pg.set_viewport_size({'width': w, 'height': H}); pg.wait_for_timeout(800)
            pg.screenshot(path=f"{shotdir}/{URL.rstrip('/').split('/')[-1].replace('.html', '')}-{w}.png")
        ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK')
sys.exit(1 if mis else 0)
