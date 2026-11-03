#!/usr/bin/env python3
"""Playwright-test voor de scratchcard-pop-up in stijlvariant 2026 (lander-w1, build-blok 'scratchcard', hotel-venray-v2).
Geen echte inschrijving: /api/nieuwsbrief en /api/track zijn gemockt.

Gebruik:
  python3 -m http.server 8765
  python3 scripts/test_scratchcard_2026.py [url] [--schermafdruk map]
Standaard url: http://localhost:8765/hotel-venray-v2.html

Checks: 1440 exit-intent opent de pop-up (data-stijl 2026, focus op sluiten), focus-trap (Tab/Shift+Tab), krassen onthult
(claimknop), e-mailstap post {taal: nl, bron: scratchcard} naar /api/nieuwsbrief, succesmelding, ec_converted, D1-events
(email_popup_open, scratch_start, scratch_reveal, email_submit, email_success); Escape sluit (focus terug); 390: niet direct,
wel na 45% scroll, onderbalk verborgen zolang hij open is, geen horizontale scroll; 390 na 20 s (klok); niet opnieuw na
ec_converted of na sluiten in dezelfde sessie; geen consolefouten. Klaviyo-lijst zelf: node --test scripts/test_nieuwsbrief_lijst.mjs.
"""
import sys, json
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
shot = None
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shot = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else 'http://localhost:8765/hotel-venray-v2.html'
res = []

def check(naam, ok, info=''):
    res.append(ok); print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def context(b, w, h, mob, init=''):
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
    ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}" + init)
    posts, events = [], []
    def nb(route):
        posts.append(json.loads(route.request.post_data or '{}'))
        route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
    def tr(route):
        try: events.append(json.loads(route.request.post_data or '{}').get('event'))
        except Exception: pass
        route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
    ctx.route('**/api/nieuwsbrief', nb)
    ctx.route('**/api/track', tr)
    pg = ctx.new_page(); pg._f = []
    pg.on('console', lambda m: pg._f.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: pg._f.append(str(e)))
    return ctx, pg, posts, events

def is_open(pg):
    return pg.evaluate("(()=>{const o=document.getElementById('scOverlay');return !!o&&o.classList.contains('is-open')})()")

def kras(pg):
    box = pg.locator('#scCanvas').bounding_box()
    x0, y0, w, h = box['x'], box['y'], box['width'], box['height']
    pg.mouse.move(x0 + 5, y0 + 8); pg.mouse.down()
    rij = 0
    y = y0 + 8
    while y < y0 + h:
        pg.mouse.move((x0 + w - 5) if rij % 2 == 0 else (x0 + 5), y, steps=12)
        y += 18; rij += 1
        pg.mouse.move((x0 + w - 5) if rij % 2 == 1 else (x0 + 5), y, steps=4)
    pg.mouse.up()

def eigen(pg):
    return [f for f in pg._f if 'mews' not in f.lower()]

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, mob in ((1440, 900, False), (390, 844, True)):
        tag = f'[{w}]'
        ctx, pg, posts, events = context(b, w, h, mob)
        pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(800)
        check(f'{tag} pop-up staat klaar maar is dicht, stijl 2026', not is_open(pg)
              and pg.evaluate("document.getElementById('scOverlay').dataset.stijl") == '2026')
        if mob:
            pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight*0.2)"); pg.wait_for_timeout(500)
            check(f'{tag} nog dicht bij 20% scroll', not is_open(pg))
            pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight*0.5)"); pg.wait_for_timeout(700)
            check(f'{tag} 45% scroll opent de pop-up', is_open(pg))
            check(f'{tag} onderbalk verborgen zolang de pop-up open is', pg.evaluate("getComputedStyle(document.querySelector('.mob-cta')).visibility") == 'hidden')
        else:
            pg.mouse.move(700, 400); pg.wait_for_timeout(300)
            check(f'{tag} nog dicht zonder exit-intent', not is_open(pg))
            pg.evaluate("document.dispatchEvent(new MouseEvent('mouseleave',{clientY:0,bubbles:false}))"); pg.wait_for_timeout(600)
            check(f'{tag} exit-intent opent de pop-up', is_open(pg))
        pg.wait_for_timeout(400)
        check(f'{tag} focus op de sluitknop', pg.evaluate("document.activeElement&&document.activeElement.id") == 'scClose')
        binnen = []
        for _ in range(4):
            pg.keyboard.press('Tab'); binnen.append(pg.evaluate("document.getElementById('scOverlay').contains(document.activeElement)"))
        pg.keyboard.press('Shift+Tab'); binnen.append(pg.evaluate("document.getElementById('scOverlay').contains(document.activeElement)"))
        check(f'{tag} focus-trap: Tab en Shift+Tab blijven in de pop-up', all(binnen), str(binnen))
        sw = pg.evaluate('document.documentElement.scrollWidth')
        m = pg.evaluate("(()=>{const r=document.querySelector('#scOverlay .sc-modal').getBoundingClientRect();return {l:r.left,r:r.right,t:r.top,b:r.bottom}})()")
        check(f'{tag} geen horizontale scroll, pop-up binnen beeld', sw <= w and m['l'] >= 0 and m['r'] <= w, f'{sw} {m}')
        st = pg.evaluate("""(()=>{const o=document.getElementById('scOverlay'),h=o.querySelector('.sc-h'),b=o.querySelector('.sc-btn'),m=o.querySelector('.sc-modal');
            return {kop:getComputedStyle(h).fontFamily.slice(0,14),knop:getComputedStyle(b).backgroundColor,rad:getComputedStyle(m).borderRadius,z:getComputedStyle(o).zIndex}})()""")
        check(f'{tag} huisstijl: serifkop, terracotta knop, kaartafronding, boven de onderbalk', st['kop'].startswith('"Abhaya Libre') and st['knop'] == 'rgb(199, 110, 78)'
              and st['rad'] == '14px' and int(st['z']) > 1600, str(st))
        if shot: pg.screenshot(path=f'{shot}/scratchcard-{w}-1-kras.png')
        kras(pg); pg.wait_for_timeout(700)
        check(f'{tag} krassen onthult het cadeau en de claimknop', pg.evaluate("document.getElementById('scClaim').classList.contains('is-visible')"))
        if shot: pg.screenshot(path=f'{shot}/scratchcard-{w}-2-onthuld.png')
        pg.locator('#scClaimBtn').click(); pg.wait_for_timeout(500)
        check(f'{tag} e-mailstap', pg.evaluate("document.getElementById('scStageEmail').classList.contains('is-active')"))
        pg.wait_for_timeout(2200)   # /api/nieuwsbrief weigert sneller dan 2 s na openen als bot
        pg.fill('#scEmail', 'test@example.com')
        if shot: pg.screenshot(path=f'{shot}/scratchcard-{w}-3-email.png')
        pg.locator('#scSubmit').click(); pg.wait_for_timeout(800)
        ok = len(posts) == 1 and posts[0].get('taal') == 'nl' and posts[0].get('bron') == 'scratchcard' and posts[0].get('email') == 'test@example.com' and posts[0].get('website') == ''
        check(f'{tag} aanmelding POST /api/nieuwsbrief met taal nl (lijst Nieuwsbrief NL), bron scratchcard', ok, str(posts))
        check(f'{tag} succesmelding + ec_converted', pg.evaluate("document.getElementById('scStageSuccess').classList.contains('is-active')")
              and pg.evaluate("localStorage.getItem('ec_converted')") == '1' and 'op de lijst' in pg.locator('#scStageSuccess').inner_text())
        if shot: pg.screenshot(path=f'{shot}/scratchcard-{w}-4-succes.png')
        nodig = ['page_view', 'email_popup_open', 'scratch_start', 'scratch_reveal', 'email_submit', 'email_success']
        check(f'{tag} D1-events zoals de oude pop-up', all(e in events for e in nodig), str(events))
        check(f'{tag} geen consolefouten', not eigen(pg), '; '.join(eigen(pg))[:300])
        pg.reload(wait_until='networkidle'); pg.wait_for_timeout(500)
        check(f'{tag} na aanmelding geen pop-up meer (ec_converted)', not pg.evaluate("!!document.getElementById('scOverlay')"))
        ctx.close()

        # Escape + sluiten + niet opnieuw in dezelfde sessie
        ctx, pg, posts, events = context(b, w, h, mob)
        pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(500)
        pg.evaluate("window.openScratchcard()"); pg.wait_for_timeout(400)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
        check(f'{tag} Escape sluit de pop-up', not is_open(pg))
        pg.evaluate("window.openScratchcard()"); pg.wait_for_timeout(300)
        check(f'{tag} na sluiten niet opnieuw in dezelfde sessie', not is_open(pg))
        ctx.close()

    # telefoon: na 20 s ook zonder scrollen
    ctx, pg, posts, events = context(b, 390, 844, True)
    pg.clock.install()
    pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(300)
    pg.clock.run_for(16000); r1 = is_open(pg)   # laden telt ook mee (klok loopt door)
    pg.clock.run_for(5000); pg.wait_for_timeout(300); r2 = is_open(pg)
    check('[390] na 20 s open zonder scrollen (en niet eerder)', not r1 and r2, f'{r1}/{r2}')
    ctx.close()
    b.close()

print(f'\n{sum(res)}/{len(res)} checks OK')
sys.exit(0 if all(res) else 1)
