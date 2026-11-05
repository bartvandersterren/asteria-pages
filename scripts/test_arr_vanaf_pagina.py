#!/usr/bin/env python3
"""Playwright-test live vanaf-prijs (arr-vanaf.js) op de arrangementpagina's, met gemockte /api/arr-vanaf.

Gebruik: python3 -m http.server 8765 ; python3 scripts/test_arr_vanaf_pagina.py [slug ...] [--basis URL] [--schermafdruk map]
Standaard alle zes. Per pagina, 1440 en 390: prijselementen met data-arr-vanaf = de code van de pagina (pil, kaart,
inbegrepen, onderbalk), Ook-interessant met de eigen code; gemockte API -> live bedrag (vaste prijs min 1 euro) in alle elementen
van die code, positie gelijk en omringend blok even hoog (geen layout-sprong); API 500 -> vaste prijs blijft; API met
null -> vaste prijs blijft; geen horizontale scroll.
"""
import sys, json, re
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
shot = None; basis = 'http://localhost:8765'
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shot = args[i + 1]; del args[i:i + 2]
if '--basis' in args:
    i = args.index('--basis'); basis = args[i + 1]; del args[i:i + 2]
SLUGS = args or ['wellness-arrangement', 'najaarsarrangement', 'oorlogsmuseum-arrangement', 'limburg-arrangement', 'weekend-aanbieding', 'golfarrangement']
res = []
def check(n, ok, info=''):
    res.append(ok); print(('OK   ' if ok else 'FOUT ') + n + (f'  ({info})' if info else ''))

def ctx_met(b, w, h, mob, modus, mock=None):
    ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
    ctx.add_init_script("try{localStorage.setItem('cookie-consent','1');localStorage.setItem('ec_converted','1')}catch(e){}")
    ctx.route('**/distributor.min.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))
    ctx.route('**/api/track', lambda r: r.fulfill(status=204, body=''))
    def api(route):
        codes = re.search(r'codes=([^&]*)', route.request.url).group(1).replace('%2C', ',').split(',')
        if modus == 'fout': return route.fulfill(status=500, content_type='application/json', body='{"ok":false}')
        pr = {c: (None if modus == 'null' else {'euro': (mock or {}).get(c, 111), 'eenheid': 'pp_nacht'}) for c in codes}
        route.fulfill(status=200, content_type='application/json', body=json.dumps({'ok': True, 'prijzen': pr}))
    ctx.route('**/api/arr-vanaf*', api)
    return ctx

with sync_playwright() as p:
    b = p.chromium.launch()
    for slug in SLUGS:
        url = f'{basis}/{slug}.html'
        for w, h, mob in ((1440, 900, False), (390, 844, True)):
            tag = f'[{slug} {w}]'
            # zonder antwoord eerst: vaste prijs + posities meten (API blokkeren tot na de meting)
            ctx = ctx_met(b, w, h, mob, 'fout'); pg = ctx.new_page()
            pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(500)
            meet = """(()=>[...document.querySelectorAll('[data-arr-vanaf]')].map(e=>{const r=e.getBoundingClientRect(),
                b=(e.closest('p,div,li,a')||e.parentElement).getBoundingClientRect();
                return {c:e.dataset.arrVanaf,t:e.textContent.trim(),l:Math.round(r.left+scrollX),y:Math.round(r.top+scrollY),w:r.width,
                  bh:Math.round(b.height),by:Math.round(b.top+scrollY),ander:!!e.closest('.ar-ander'),live:e.dataset.arrVanafLive||''}}))()"""
            vast = pg.evaluate(meet)
            code = pg.evaluate("document.getElementById('bb-code').value")
            eigen = [x for x in vast if x['c'] == code]
            check(f'{tag} prijselementen met code {code}: pil, kaart, inbegrepen, onderbalk (>= 4), elk met een bedrag', len(eigen) >= 4 and all(x['t'].startswith('€') for x in eigen), str([x['t'] for x in eigen]))
            check(f'{tag} API-fout: vaste prijs blijft staan', all(not x['live'] for x in vast) and pg.evaluate("window.arrVanaf.status").startswith('fout'))
            ctx.close()
            ctx = ctx_met(b, w, h, mob, 'null'); pg = ctx.new_page(); pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(500)
            nul = pg.evaluate(meet)
            check(f'{tag} API met null: vaste prijs blijft', [x['t'] for x in nul] == [x['t'] for x in vast] and not any(x['live'] for x in nul))
            ctx.close()
            # realistische live waarde: vaste prijs per code min 1 euro (zelfde aantal cijfers)
            mock = {x['c']: int(re.sub(r'[^0-9]', '', x['t'].split(',')[0])) - 1 for x in vast}
            ctx = ctx_met(b, w, h, mob, 'live', mock); pg = ctx.new_page(); pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(700)
            live = pg.evaluate(meet)
            ok = all(x['t'] == '€\u00a0' + str(mock[x['c']]) and x['live'] == '1' for x in live) and len(live) == len(vast)
            check(f'{tag} live bedrag in alle {len(live)} prijselementen', ok, str([x['t'] for x in live][:6]))
            sprong = [(a['t'], a['l'], c['l'], a['y'], c['y'], a['bh'], c['bh']) for a, c in zip(vast, live)
                      if a['w'] and (abs(a['by'] - c['by']) > 1 or abs(a['bh'] - c['bh']) > 1
                          or (not a['ander'] and (abs(a['l'] - c['l']) > 1 or abs(a['y'] - c['y']) > 1)))]
            # Ook-interessant-kaarten hebben een vaste hoogte met de tekst onderaan: een regel meer of minder door een ander
            # bedrag verschuift de tekst binnen de kaart, niet de pagina; daar telt alleen dat de kaart zelf gelijk blijft.
            check(f'{tag} geen layout-sprong (bedrag op dezelfde plek, blok eromheen even hoog)', not sprong, str(sprong[:3]))
            sw = pg.evaluate('document.documentElement.scrollWidth')
            check(f'{tag} geen horizontale scroll', sw <= w, str(sw))
            if shot and slug == SLUGS[0]:
                pg.screenshot(path=f'{shot}/arr-vanaf-{slug}-{w}-hero.png')
            ctx.close()
    b.close()
print(f'\n{sum(res)}/{len(res)} checks OK'); sys.exit(0 if all(res) else 1)
