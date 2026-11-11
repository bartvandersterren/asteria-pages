#!/usr/bin/env python3
"""Stilstaande kaartbeelden voor de routepagina's (vangnet van blok 4c en de lus-kaartjes in de route-pop-up).

Rendert met Playwright de getekende kaart zelf (kaart-getekend.js + kaart-getekend.css + route.css, ondergrond
content/kaart/getekend.json, routes uit content/routes/<soort>.json), dus precies wat de interactieve kaart toont:
  fotos/l26-route-kaart-fiets.webp, fotos/l26-route-kaart-wandel.webp   overzicht van alle routes (1600 x 1000),
                                                                          zonder knoppen en hint, met de attributie
  fotos/l26-route-lus-<slug>.webp                                          per route: alleen die route, uitgelicht,
                                                                          met het hotel (800 x 600; Parkhotel ro-lus-*)
Draait een eigen http-server op de repo-root (vrije poort), geen netwerk buiten localhost.

  python3 scripts/route_kaartfoto.py              # alles
  python3 scripts/route_kaartfoto.py fiets        # alleen fiets
"""
import asyncio
import functools
import http.server
import io
import json
import os
import sys
import threading

WORTEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIGNET = 'fotos/l26-uitje-vignet-asteria.webp'

HARNAS = """<!doctype html><html lang="nl"><head><meta charset="utf-8">
<link rel="stylesheet" href="/lander-w1.css"><link rel="stylesheet" href="/adslander.css">
<link rel="stylesheet" href="/kaart-getekend.css"><link rel="stylesheet" href="/route.css">
<style>html,body{margin:0;background:#fff}.gk-knoppen,.gk-hint{display:none!important}
#k{position:relative;overflow:hidden;border:0;border-radius:0;background:var(--paper-shade)}</style>
<script src="/kaart-getekend.js"></script></head>
<body><main class="lp al rt"><section class="rt-kaart"><div class="rt-kaart__beeld is-interactief" id="k"></div></section></main></body></html>"""


def server():
    class Stil(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Stil, directory=WORTEL)
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def opslaan(png, pad, breed):
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert('RGB')
    if im.width != breed:
        im = im.resize((breed, round(im.height * breed / im.width)), Image.LANCZOS)
    im.save(os.path.join(WORTEL, pad), 'WEBP', quality=80, method=6)
    print(f'  {pad} {im.size}')


async def render(soorten):
    from playwright.async_api import async_playwright
    httpd = server()
    basis = f'http://127.0.0.1:{httpd.server_address[1]}'
    with open(os.path.join(WORTEL, 'content/kaart/getekend.json'), encoding='utf-8') as f:
        geo = json.load(f)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for soort in soorten:
            with open(os.path.join(WORTEL, f'content/routes/{soort}.json'), encoding='utf-8') as f:
                data = json.load(f)
            routes = [{'slug': r['slug'], 'nr': r['nr'], 'naam': r['naam']['nl'], 'afstand_km': r['afstand_km'], 'rondje': r['rondje'],
                       'lijn': r['lijn'] or [r['start'], [r['start'][0], r['start'][1] + 0.00002]], 'speld': not r['lijn']} for r in data['routes']]
            for slug, (b, h, dpr, pad, breed) in [(None, (1120, 700, 2, f'fotos/l26-route-kaart-{soort}.webp', 1600))] + \
                    [(r['slug'], (800, 600, 1.5, f'fotos/l26-route-lus-{r["slug"]}.webp', 800)) for r in routes]:
                page = await browser.new_page(viewport={'width': b, 'height': h}, device_scale_factor=dpr)
                await page.route(basis + '/__kaart.html', lambda route: route.fulfill(body=HARNAS, content_type='text/html'))
                await page.goto(basis + '/__kaart.html', wait_until='load')
                await page.evaluate("""([geo, data, routes, slug, b, h, vignet]) => new Promise((klaar) => {
                    const el = document.getElementById('k'); el.style.width = b + 'px'; el.style.height = h + 'px';
                    const api = window.AsteriaKaart.maak(el, { geo, hotel: { lat: data.hotel[0], lng: data.hotel[1], naam: 'Hotel Asteria' },
                      vignet, padding: !slug ? { tl: [24, 24], br: [24, 28] } : (routes.find((q) => q.slug === slug) || {}).speld
                        ? { tl: [345, 262], br: [345, 238] } : { tl: [40, 40], br: [40, 40] } });
                    api.zetRoutes(routes);
                    document.querySelectorAll('.gk-pins > .routebadge').forEach((x) => {
                      const r = routes.find((q) => String(q.nr) === x.textContent.trim());
                      if (r && r.speld) { x.classList.add('rt-speld'); x.innerHTML = '<span>' + x.textContent + '</span>'; }
                    });
                    if (slug) { api.zetZichtbaar((r) => r.slug === slug); api.setActiveRoute(slug); }
                    api.overzicht(false);
                    const img = el.querySelector('.gk-hotel img');
                    const af = () => setTimeout(klaar, 300);
                    if (img && !img.complete) { img.onload = af; img.onerror = af; } else af();
                  })""", [geo, data, routes, slug, b, h, VIGNET])
                png = await page.locator('#k').screenshot()
                opslaan(png, pad, breed)
                await page.close()
        await browser.close()
    httpd.shutdown()


if __name__ == '__main__':
    soorten = [a for a in sys.argv[1:] if a in ('fiets', 'wandel')] or ['fiets', 'wandel']
    asyncio.run(render(soorten))
