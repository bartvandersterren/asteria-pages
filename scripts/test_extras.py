#!/usr/bin/env python3
"""Playwright-test voor de extras-lander /extras (pre-arrival upsell).

Gebruik:
  npx --yes wrangler@4 pages dev . --port 8788      # in de repo-root, met .dev.vars (EXTRAS_DRY_RUN=1, MAIL_DRY_RUN=1)
  python3 scripts/test_extras.py [url] [--schermafdruk qa/extras]

Standaard-url: http://localhost:8788/extras?r=0c90a9f6-2e2e-4214-88c8-b4b900b4f047&n=123456&a=2026-10-20&d=2026-10-22&p=2&v=Stijn&k=diner
Checks (1440 en 390): laden met testlink (reserveringskaart, welkomregel), kaarten per groep, aanbevolen kaart,
Voeg toe, stepper, dagchips bij het diner, voorkeurstijd-chip, zijkaart-totaal = bestelbox-totaal (1440),
meelopende balk (390), bestellen in dry-run -> staat Genoteerd met stappen, geen horizontale overloop,
geen consolefouten. Bestellen gaat alleen goed tegen een server met EXTRAS_DRY_RUN=1.
"""
import os, sys
from playwright.sync_api import sync_playwright

args = list(sys.argv[1:])
shotdir = None
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else ('http://localhost:8788/extras?r=0c90a9f6-2e2e-4214-88c8-b4b900b4f047'
                            '&n=123456&a=2026-10-20&d=2026-10-22&p=2&v=Stijn&k=diner')
if shotdir: os.makedirs(shotdir, exist_ok=True)
resultaten = []

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

def kaart(pg, key):
    return pg.locator(f'.xv-kaart[data-kaart="{key}"]')

def tekst(pg, sel):
    return pg.locator(sel).first.inner_text().strip()

def volle_plaat(pg, w, pad):
    pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    pg.evaluate("window.scrollTo(0,0)")
    pg.add_style_tag(content='.top-stack{position:relative!important}')  # anders staat de sticky kop midden op de plaat
    pg.wait_for_timeout(1200)
    pg.screenshot(path=pad, full_page=True)
    pg.evaluate("document.querySelectorAll('style').forEach(s=>{if(s.textContent.includes('.top-stack{position:relative'))s.remove()})")

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, mob in [(1440, 900, False), (390, 844, True)]:
        tag = f'[{w}]'
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
        ctx.add_init_script("try{localStorage.setItem('cookie-consent','1');localStorage.removeItem('asteria-extras-0c90a9f6-2e2e-4214-88c8-b4b900b4f047')}catch(e){}")
        pg = ctx.new_page()
        fouten = []
        pg.on('console', lambda m: fouten.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: fouten.append(str(e)))
        pg.goto(URL, wait_until='networkidle')
        pg.wait_for_selector('.xv-kaart', timeout=15000)
        pg.wait_for_timeout(500)

        # laden met testlink
        check(f'{tag} reserveringskaart zichtbaar met datums en gasten',
              pg.locator('#xvKaart').is_visible()
              and tekst(pg, '[data-veld="aankomst"]') == 'di 20 okt 2026'
              and tekst(pg, '[data-veld="vertrek"]') == 'do 22 okt 2026'
              and tekst(pg, '[data-veld="gasten"]') == '2 personen',
              ' | '.join([tekst(pg, '[data-veld="aankomst"]'), tekst(pg, '[data-veld="vertrek"]'), tekst(pg, '[data-veld="gasten"]')]))
        check(f'{tag} reserveringsnummer en welkomregel met voornaam',
              'Reserveringsnummer 123456' in tekst(pg, '[data-veld="regel"]') and tekst(pg, '#xvWelkom').startswith('Stijn, alles wat je kiest'),
              tekst(pg, '#xvWelkom'))
        check(f'{tag} slotkop met aankomstdatum', tekst(pg, '#xvSlotKop') == 'Tot dinsdag 20 oktober', tekst(pg, '#xvSlotKop'))

        # kaarten per groep
        per = pg.evaluate("""()=>Object.fromEntries(['aankomst','verblijf','vertrek'].map(g=>[g,
              [...document.querySelectorAll('[data-raster="'+g+'"] .xv-kaart')].map(k=>k.dataset.kaart)]))""")
        check(f'{tag} kaarten per groep',
              per == {'aankomst': ['badjas', 'handdoek', 'early'],
                      'verblijf': ['diner', 'ontbijt', 'wellness', 'fiets', 'ebike', 'kruidenolie'],
                      'vertrek': ['late']}, str(per))
        prijzen = pg.evaluate("Object.fromEntries([...document.querySelectorAll('.xv-kaart')].map(k=>[k.dataset.kaart,k.querySelector('.xv-kaart__prijs .xv-bedrag').textContent]))")
        check(f'{tag} prijzen uit Mews op de kaarten',
              prijzen.get('diner') == '€ 37,50' and prijzen.get('wellness') == '€ 12,50' and prijzen.get('kruidenolie') == '€ 4,95'
              and prijzen.get('late') == '€ 25,00', str(prijzen))
        pg.evaluate("document.querySelectorAll('.xv-kaart__foto img').forEach(i=>i.loading='eager')")
        pg.wait_for_timeout(1200)
        fotos = pg.evaluate("[...document.querySelectorAll('.xv-kaart')].map(k=>{const i=k.querySelector('.xv-kaart__foto img');return !!i&&i.complete&&i.naturalWidth>0&&/\\/fotos\\/extras-[a-z]+\\.webp$/.test(i.src)})")
        check(f'{tag} productfoto\'s geladen uit fotos/extras-*.webp', len(fotos) == 10 and all(fotos), str(fotos))
        check(f'{tag} aanbevolen kaart (k=diner) gemarkeerd', 'is-aanbevolen' in (kaart(pg, 'diner').get_attribute('class') or ''))

        # Voeg toe + stepper (badjas)
        kaart(pg, 'badjas').locator('[data-act="add"]').click()
        aantal = lambda k: kaart(pg, k).locator('[data-aantal]').inner_text()
        check(f'{tag} Voeg toe zet de kaart aan, stepper start op 2', 'is-on' in kaart(pg, 'badjas').get_attribute('class') and aantal('badjas') == '2')
        kaart(pg, 'badjas').locator('[data-act="inc"]').click()
        a3 = aantal('badjas')
        kaart(pg, 'badjas').locator('[data-act="dec"]').click(); kaart(pg, 'badjas').locator('[data-act="dec"]').click()
        a1 = aantal('badjas')
        check(f'{tag} stepper plus/min (3, dan 1)', (a3, a1) == ('3', '1'), f'{a3},{a1}')

        # diner: dagchips (avondchips) + tijdveld
        kaart(pg, 'diner').locator('[data-act="add"]').click()
        aan = lambda: kaart(pg, 'diner').locator('.xv-chip--aan').count()
        twee = aan()
        kaart(pg, 'diner').locator('[data-act="avond"][data-avond="2026-10-20"]').click()
        een = aan()
        check(f'{tag} avondchips diner: beide aan, na klik alleen wo 21 okt', (twee, een) == (2, 1), f'{twee},{een}')
        tijdveld = pg.locator('#xvForm [data-als="diner"]')
        check(f'{tag} voorkeurstijd verschijnt bij het diner', tijdveld.is_visible())
        pg.locator('[data-act="tijd"][data-tijd="19.00"]').click()
        check(f'{tag} tijdchip 19.00 aan', pg.locator('[data-act="tijd"][data-tijd="19.00"]').get_attribute('aria-pressed') == 'true')

        # wellness: dagchips heten "Welke dag(en)?"
        kaart(pg, 'wellness').locator('[data-act="add"]').click()
        check(f'{tag} wellness-kaart vraagt welke dag(en)', 'Welke dag(en)?' in kaart(pg, 'wellness').inner_text())

        # totalen: badjas 1 x 7 + diner 2 x 37,50 x 1 + wellness 2 x 12,50 x 2 = 7 + 75 + 50 = 132
        tot_bestel = tekst(pg, '.xv-bestel__totaal [data-sum-totaal]')
        check(f'{tag} bestelbox-totaal klopt (€ 132,00)', tot_bestel == '€ 132,00', tot_bestel)
        if not mob:
            tot_zij = tekst(pg, '.xv-keuze [data-sum-totaal]')
            check(f'{tag} zijkaart-totaal = bestelbox-totaal', tot_zij == tot_bestel, f'{tot_zij} / {tot_bestel}')
            pos = pg.evaluate("getComputedStyle(document.getElementById('xvZij')).position")
            check(f'{tag} zijkaart sticky', pos == 'sticky', pos)
            check(f'{tag} balk verborgen op bureaublad', not pg.locator('#xvBalk').is_visible())
        else:
            balk = tekst(pg, '[data-sum-balk]')
            check(f'{tag} meelopende balk zichtbaar met hetzelfde totaal', pg.locator('#xvBalk').is_visible() and balk == '3 extra\'s · ' + tot_bestel, balk)
            check(f'{tag} zijkaart verborgen op telefoon', not pg.locator('#xvZij').is_visible())

        sw = pg.evaluate('document.documentElement.scrollWidth')
        check(f'{tag} geen horizontale overloop', sw <= w, f'scrollWidth {sw}')

        if shotdir:
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)
            pg.screenshot(path=f'{shotdir}/extras-{w}-eerste-scherm.png')
            kaart(pg, 'diner').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
            pg.screenshot(path=f'{shotdir}/extras-{w}-kaarten.png')
            volle_plaat(pg, w, f'{shotdir}/extras-{w}-heel.png')

        # bestellen (dry-run)
        pg.fill('#xvEmail', 'test@example.com')
        pg.fill('#xvOpmerking', 'Testbestelling via scripts/test_extras.py')
        pg.evaluate("document.getElementById('xvT0').value=String(Date.now()-10000)")
        with pg.expect_response(lambda r: '/api/extras/bestel' in r.url) as resp:
            pg.locator('#xvBestelKnop').click()
        r = resp.value
        j = r.json()
        check(f'{tag} bestellen -> 200 ok (dry-run)', r.status == 200 and j.get('ok') and j.get('total_cents') == 13200, f'{r.status} {j.get("total_cents")} fallback={j.get("fallback")}')
        pg.wait_for_selector('#xvKlaar:not([hidden])', timeout=5000)
        stappen = pg.evaluate("[...document.querySelectorAll('.xv-klaar__stappen li')].filter(l=>!l.hidden).map(l=>l.dataset.stap+': '+l.textContent)")
        check(f'{tag} staat Genoteerd, aanbod weg',
              pg.locator('#xvKlaar').is_visible() and not pg.locator('#xvAanbod').is_visible()
              and tekst(pg, '#xvKlaarTotaal') == '€ 132,00', tekst(pg, '#xvKlaarTotaal'))
        check(f'{tag} stappen kamer, diner en wellness',
              [s.split(':')[0] for s in stappen] == ['kamer', 'diner', 'wellness']
              and 'woensdag 21 oktober' in stappen[1] and 'dinsdag 20 oktober en woensdag 21 oktober' in stappen[2], ' | '.join(stappen))
        check(f'{tag} verheugregel met datum', tekst(pg, '#xvKlaarSlot') == 'Wij verheugen ons op je komst op dinsdag 20 oktober.', tekst(pg, '#xvKlaarSlot'))
        if mob:
            check(f'{tag} balk weg na bestellen', not pg.locator('#xvBalk').is_visible())
        if shotdir:
            pg.locator('#xvKlaar').scroll_into_view_if_needed(); pg.wait_for_timeout(300)
            pg.screenshot(path=f'{shotdir}/extras-{w}-genoteerd.png')

        # Nog iets toevoegen
        pg.locator('#xvNogIets').click()
        check(f'{tag} Nog iets toevoegen: aanbod terug, keuze leeg, melding al eerder',
              pg.locator('#xvAanbod').is_visible() and pg.locator('.xv-kaart.is-on').count() == 0 and pg.locator('#xvAlEerder').is_visible())

        sw = pg.evaluate('document.documentElement.scrollWidth')
        check(f'{tag} geen horizontale overloop (na bestellen)', sw <= w, f'scrollWidth {sw}')
        check(f'{tag} geen consolefouten', not fouten, '; '.join(fouten)[:300])
        ctx.close()

    # zonder geldige link: foutstaat
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True)
    pg = ctx.new_page()
    pg.goto(URL.split('?')[0], wait_until='networkidle')
    check('[390] zonder link: melding, geen aanbod', 'persoonlijke link' in tekst(pg, '#xvWelkom') and not pg.locator('#xvAanbod').is_visible())
    ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK, {len(mis)} FOUT')
sys.exit(1 if mis else 0)
