#!/usr/bin/env python3
"""Vangnet-kaartfoto van een uitjepagina: rendert de getekende kaart (kaart-getekend.js) van <slug>-v2.html met Playwright.

Gebruik (in de repo-root, na python3 build.py uitje-<slug>):
  python3 scripts/uitje_kaartfoto.py <slug> [--poort N] [--naar MAP]

- Gegevens: translations/uitje-<slug>-nl.json; de bestandsnamen komen uit de velden kaart-foto (1200x675) en
  kaart-foto-klein (720x540), bv. fotos/l26-uitje-kaart-<kort>.webp en fotos/l26-uitje-kaart-<kort>-klein.webp.
- Element .ut-kaart__beeld, op exact die maat gezet; zoomknoppen, hint en de voetstrook (.ut-voet) verborgen, de attributie
  naar de onderrand (zonder voetstrook). De kaart staat op "Hele kaart tonen".
- Zonder --poort start het script zelf een tijdelijke http.server op een vrije poort (map = repo-root); met --poort gebruikt
  het een server die al draait op localhost:<N>.
- Let op: de pagina toont tot de eerste build zonder deze foto's een kapotte vangnetfoto; dat is geen probleem, het script
  wacht op de interactieve kaart. Opnieuw bouwen is daarna niet nodig (de namen staan al in het JSON).
- --naar MAP: schrijf de twee foto's (zelfde bestandsnamen) in MAP in plaats van op hun plek in fotos/ (proefdraaien).
"""
import argparse, asyncio, functools, http.server, io, json, os, socketserver, sys, threading
from playwright.async_api import async_playwright
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATEN = (('kaart-foto', 1200, 675), ('kaart-foto-klein', 720, 540))
VERBERG = ('.gk-knoppen,.gk-hint,.ut-voet{visibility:hidden!important} '
           '.ut-kaart__beeld .gk-attr{bottom:5px!important} .mob-cta,.cookie-banner{display:none!important}')


def server_starten():
    class Stil(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Stil, directory=BASE)
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


async def render(url, uit, naar=None):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for veld, br, ho in MATEN:
            ctx = await b.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
            await ctx.route('**/api/**', lambda r: r.fulfill(status=200, content_type='application/json', body='{"ok":true}'))
            await ctx.route('https://www.googletagmanager.com/**', lambda r: r.fulfill(status=200, body=''))
            pg = await ctx.new_page()
            await pg.goto(url, wait_until='networkidle')
            kaart = pg.locator('.ut-kaart__beeld')
            if not await kaart.count():
                sys.exit(f'geen .ut-kaart__beeld op {url} (staat kaart-kop in het JSON?)')
            await pg.add_style_tag(content=f'.ut-kaart__beeld{{width:{br}px!important;height:{ho}px!important;max-width:none!important;'
                                           f'aspect-ratio:auto!important;flex:none!important}} ' + VERBERG)
            await kaart.scroll_into_view_if_needed()
            await pg.wait_for_selector('.ut-kaart__beeld.is-interactief', timeout=15000)
            await pg.evaluate("window.dispatchEvent(new Event('resize'))")
            await pg.wait_for_timeout(600)
            alles = pg.locator('.ut-kaart .gk-knop').nth(2)   # Hele kaart tonen
            if await alles.count():
                await alles.click(force=True)
            await pg.wait_for_timeout(900)
            doos = await kaart.bounding_box()
            if round(doos['width']) != br or round(doos['height']) != ho:
                sys.exit(f'kaart is {doos["width"]}x{doos["height"]}, verwacht {br}x{ho}')
            png = await kaart.screenshot()
            pad = os.path.join(naar, os.path.basename(uit[veld])) if naar else os.path.join(BASE, uit[veld])
            Image.open(io.BytesIO(png)).convert('RGB').save(pad, 'WEBP', quality=86, method=6)
            print(f'  {os.path.relpath(pad, BASE)}  ({br}x{ho}, {os.path.getsize(pad) // 1024} KB)')
            await ctx.close()
        await b.close()


def main():
    ap = argparse.ArgumentParser(description='Vangnet-kaartfoto van een uitjepagina renderen')
    ap.add_argument('slug', help='bv. zooparc-overloon (pagina <slug>-v2.html, JSON translations/uitje-<slug>-nl.json)')
    ap.add_argument('--poort', type=int, help='poort van een al draaiende server; zonder = tijdelijke server')
    ap.add_argument('--naar', help='andere uitvoermap (proef), zelfde bestandsnamen')
    a = ap.parse_args()
    bron = os.path.join(BASE, 'translations', f'uitje-{a.slug}-nl.json')
    pagina = os.path.join(BASE, f'{a.slug}-v2.html')
    for x in (bron, pagina):
        if not os.path.exists(x):
            sys.exit(f'ontbreekt: {os.path.relpath(x, BASE)}' + (' (eerst python3 build.py uitje-' + a.slug + ')' if x == pagina else ''))
    d = json.load(open(bron, encoding='utf-8'))
    uit = {}
    for veld, _, _ in MATEN:
        if not d.get(veld) or not d[veld].endswith('.webp'):
            sys.exit(f'{veld} ontbreekt in het JSON of is geen .webp')
        uit[veld] = d[veld]
    httpd = None
    poort = a.poort
    if not poort:
        httpd, poort = server_starten()
    try:
        if a.naar:
            os.makedirs(a.naar, exist_ok=True)
        asyncio.run(render(f'http://localhost:{poort}/{a.slug}-v2.html', uit, os.path.abspath(a.naar) if a.naar else None))
    finally:
        if httpd:
            httpd.shutdown()


if __name__ == '__main__':
    main()
