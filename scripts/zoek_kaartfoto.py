#!/usr/bin/env python3
"""Vangnet-kaartfoto's van een zoekpagina "Hotel bij ..." (zoek.template.html, blok ligging).

De getekende kaart (kaart-getekend.js via uitje.js) wordt met Playwright gerenderd en als stilstaande foto opgeslagen,
zoals de kaart-foto van het uitje-sjabloon: zonder script, of als het laden mislukt, blijft die foto staan.

Gebruik (repo-root):  python3 scripts/zoek_kaartfoto.py zoek-<slug>-<taal>
  1. bouwt de pagina zonder kaartfoto (ZOEK_ZONDER_KAARTFOTO=1 python3 build.py <entry>), want de build stopt bij een
     ontbrekend fotobestand;
  2. start een eigen server op een vrije poort, rendert het kaartvlak op 1200x800 (veld kaart-foto) en 720x540
     (veld kaart-foto-klein), zonder zoomknoppen en hint, en schrijft WebP q72;
  3. bouwt de pagina opnieuw, nu met de foto's.
Paden komen uit de pagina-JSON (translations/zoek-<slug>-<taal>.json: kaart-foto, kaart-foto-klein, canonical).
"""
import asyncio, functools, http.server, io, json, os, socket, subprocess, sys, threading
from PIL import Image
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2 or not sys.argv[1].startswith('zoek-'):
    sys.exit('gebruik: python3 scripts/zoek_kaartfoto.py zoek-<slug>-<taal>')
ENTRY = sys.argv[1]
D = json.load(open(os.path.join(BASE, 'translations', ENTRY + '.json'), encoding='utf-8'))
PAGINA = D['canonical'].rstrip('/').rsplit('/', 1)[-1] + '.html'
MATEN = [('kaart-foto', 1200, 800), ('kaart-foto-klein', 720, 540)]


def bouw(zonder):
    env = dict(os.environ)
    if zonder:
        env['ZOEK_ZONDER_KAARTFOTO'] = '1'
    else:
        env.pop('ZOEK_ZONDER_KAARTFOTO', None)
    subprocess.run([sys.executable, 'build.py', ENTRY], cwd=BASE, env=env, check=True)


def server():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); poort = s.getsockname()[1]; s.close()
    class Stil(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Stil, directory=BASE)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', poort), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, poort


async def render(poort):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for veld, w, h in MATEN:
            if not D.get(veld):
                continue
            pg = await b.new_page(viewport={'width': 1440, 'height': 1000})
            await pg.route('**/googletagmanager.com/**', lambda r: r.fulfill(status=200, body=''))
            await pg.route('**/api/**', lambda r: r.fulfill(status=404, body='{}'))
            await pg.goto(f'http://127.0.0.1:{poort}/{PAGINA}', wait_until='networkidle')
            await pg.add_style_tag(content=(
                f'.zk-ligging .zk-ligging__raster{{display:block}} .zk-ligging .zk-ligging__paneel{{display:none}}'
                f'.zk-ligging .zk-ligging__veld,.zk-ligging .ut-kaart__beeld{{width:{w}px!important;height:{h}px!important;min-height:0!important;aspect-ratio:auto!important;'
                'border:0!important;border-radius:0!important;box-shadow:none!important}'
                '.zk-ligging .gk-knoppen,.zk-ligging .gk-hint,.top-stack,.mob-cta,.cookie-banner{display:none!important}'))
            el = pg.locator('.zk-ligging .ut-kaart__beeld')
            await el.scroll_into_view_if_needed()
            await pg.wait_for_selector('.zk-ligging .ut-kaart__beeld.is-interactief', timeout=15000)
            await pg.wait_for_timeout(1200)
            png = await el.screenshot()
            uit = os.path.join(BASE, D[veld])
            Image.open(io.BytesIO(png)).convert('RGB').save(uit, 'WEBP', quality=72, method=6)
            print(f'  {D[veld]}  {w}x{h}  ({os.path.getsize(uit) // 1024} kB)')
            await pg.close()
        await b.close()


bouw(True)
srv, poort = server()
try:
    asyncio.run(render(poort))
finally:
    srv.shutdown()
bouw(False)
