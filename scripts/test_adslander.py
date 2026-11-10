#!/usr/bin/env python3
"""Test van de Duitse ads-lander (adslander.template.html), naar model van parkhotel-site scripts/test_adslander.mjs.

Gebruik:
  python3 -m http.server 8791 --directory .            (in de repo-root)
  python3 scripts/test_adslander.py [URL] [--schermafdruk qa/adslander] [--breedtes 1440,390]
  standaard-URL: http://localhost:8791/wellnesshotel-limburg-de.html

De /api/*-functies bestaan lokaal niet: arr-vanaf, kamer-vanaf, arr-kalender en nieuwsbrief worden gemockt.
Het Mews-script wordt onderschept en vervangen door een stub die elke API-aanroep logt (window.__mews).
Op een preview (https://...pages.dev) worden de API's ook gemockt, zodat de test stabiel is.
Exit 0 = alles groen; anders de lijst met falende controles.
"""
import asyncio, glob, json, os, re, sys
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
URL = next((a for a in args if a.startswith('http')), 'http://localhost:8791/wellnesshotel-limburg-de.html')
SHOT = args[args.index('--schermafdruk') + 1] if '--schermafdruk' in args else None
BREEDTES = [int(x) for x in (args[args.index('--breedtes') + 1] if '--breedtes' in args else '1440,390').split(',')]

KAL = json.load(open(os.path.join(BASE, 'content', 'arr-kalender.json'), encoding='utf-8'))
KAMERS = ['98900f3b-e5e2-49c9-9776-af1d00ffc315', '85ca19d7-eea5-41c8-8b93-af1d00ffc315', 'fa5b6540-7234-49ce-beb1-af1d00ffc315',
          'a8fd7310-0d61-422f-89e6-af1d00ffc315', 'c737de50-e41e-4c8d-a818-af1d00ffc315', '4a642b66-68e6-444c-beeb-af1d00ffc315',
          'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2']
VOLGORDE = ['al-hero', 'al-intro', 'al-rond', 'al-arr', 'al-kamers', 'al-fac', 'al-omg', 'al-fotorij', 'al-rev', 'al-faq', 'al-nb', 'al-slot']
NL_WOORDEN = ['Boek nu', 'Bekijk', 'beschikbaarheid', 'Reserveer', 'Privacyverklaring', 'Algemene voorwaarden', 'Akkoord', 'kamer ',
              'Kies je', 'Sluiten', 'Vorige', 'Volgende', ' en de ', ' het ', ' een ', 'Wissen', 'nachten', 'Meer info']

MEWS_STUB = """window.Mews={Distributor:function(opt,cb){window.__mews=window.__mews||[];var log={cfg:opt.configurationIds[0],taal:opt.language,calls:[]};
window.__mews.push(log);var api={};['setVoucherCode','setStartDate','setEndDate','setAdultCount','showRates','showRooms','setLanguageCode','open']
.forEach(function(m){api[m]=function(){log.calls.push([m].concat([].slice.call(arguments).map(function(x){return x instanceof Date?x.toISOString().slice(0,10):String(x)})))}});
setTimeout(function(){cb(api)},10);}};"""


def kal_antwoord(url):
    m = re.search(r'code=([A-Z0-9]+)&maand=(\d{4})-(\d{2})&deel=(\d)', url)
    code, j, mnd, deel = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    import calendar, datetime
    laatste = calendar.monthrange(j, mnd)[1]
    van, tot = (deel - 1) * 8 + 1, laatste if deel == 4 else min(deel * 8, laatste)
    dagen = []
    for g in range(van, tot + 1):
        dt = datetime.date(j, mnd, g)
        dagen.append({'datum': dt.isoformat(), 'beschikbaar': True, 'zondag': dt.weekday() == 6, 'aankomst_mag': True,
                      'prijzen': {k: {'prijs_cent': 24900 + 1000 * (g % 3), 'berekend': False} for k in KAMERS}})
    return {'ok': True, 'code': code, 'dagen': dagen}


async def mocks(ctx, log):
    async def api(route):
        u = route.request.url
        if '/api/arr-vanaf' in u:
            body = {'ok': True, 'prijzen': {'WELLNESS2026': {'euro': 119}, 'NAJAAR2D': {'euro': 121}, 'WINTER27': {'euro': 999}}}
        elif '/api/kamer-vanaf' in u:
            body = {'ok': True, 'prijzen': {k: {'euro': 140 + i * 10} for i, k in enumerate(['comfort', 'comfort-3', 'mindervalide', 'royale', 'deluxe', 'suite', 'bruidssuite'])}}
        elif '/api/arr-kalender' in u:
            body = kal_antwoord(u)
        elif '/api/nieuwsbrief' in u:
            log['nieuwsbrief'] = route.request.post_data
            body = {'ok': True}
        else:
            body = {'ok': False}
        await route.fulfill(status=200, content_type='application/json', body=json.dumps(body))
    await ctx.route(re.compile(r'.*/api/.*'), api)

    async def mews(route):
        log['mews_script'] += 1
        await route.fulfill(status=200, content_type='application/javascript', body=MEWS_STUB)
    await ctx.route(re.compile(r'https://app\.mews\.com/distributor/distributor\.min\.js.*'), mews)
    await ctx.route(re.compile(r'https://www\.googletagmanager\.com/.*'), lambda r: r.fulfill(status=200, body=''))


async def test_breedte(p, w, fouten, schermafdruk=None):
    h = 900 if w > 800 else 844
    mob = w < 800
    browser = await p.chromium.launch()
    ctx = await browser.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
    log = {'mews_script': 0}
    await mocks(ctx, log)
    pg = await ctx.new_page()
    consolefouten = []
    pg.on('pageerror', lambda e: consolefouten.append(str(e)))
    pg.on('console', lambda m: consolefouten.append(m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
    await pg.add_init_script("try{sessionStorage.setItem('ec_shown','1');localStorage.setItem('cookie-consent','1')}catch(e){}")
    await pg.goto(URL, wait_until='networkidle')
    tag = f'[{w}]'

    def ok(cond, naam):
        if not cond:
            fouten.append(f'{tag} {naam}')
        print(('  OK  ' if cond else '  FOUT') + f' {tag} {naam}')

    # kop/meta
    meta = await pg.evaluate("""()=>({lang:document.documentElement.lang,robots:(document.querySelector('meta[name=robots]')||{}).content,
      canon:(document.querySelector('link[rel=canonical]')||{}).href, loc:(document.querySelector('meta[property="og:locale"]')||{}).content,
      ld:Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s=>s.textContent)})""")
    ok(meta['lang'] == 'de', 'html lang = de')
    ok(meta['robots'] == 'noindex, nofollow', 'robots noindex, nofollow')
    ok(meta['canon'] == 'https://visit.asteria.nl/wellnesshotel-limburg-de', 'canonical')
    ok(meta['loc'] == 'de_DE', 'og:locale de_DE')
    faqld = [json.loads(x) for x in meta['ld'] if '"FAQPage"' in x]
    nvragen = await pg.locator('.al-faq .as-accordeon__item').count()
    ok(faqld and len(faqld[0]['mainEntity']) == nvragen and nvragen >= 8, f'FAQPage JSON-LD met alle {nvragen} vragen')
    if w == BREEDTES[0]:
        sm = open(os.path.join(BASE, 'sitemap.xml'), encoding='utf-8').read()
        ok('wellnesshotel-limburg-de' not in sm, 'niet in sitemap.xml')

    # blokvolgorde
    volg = await pg.evaluate("()=>Array.from(document.querySelectorAll('main > [data-component]')).map(e=>e.getAttribute('data-component'))")
    ok(volg == VOLGORDE, 'blokvolgorde ' + ','.join(volg))
    ok(log['mews_script'] == 0, 'geen Mews-script bij laden')
    ok(not consolefouten, 'geen consolefouten ' + '; '.join(consolefouten[:3]))

    # overloop
    over = await pg.evaluate("()=>document.documentElement.scrollWidth - document.documentElement.clientWidth")
    ok(over <= 0, f'geen horizontale overloop ({over})')

    # links: geen asteria.nl behalve privacy/voorwaarden, geen NL-pagina's van visit.asteria.nl
    hrefs = await pg.evaluate("()=>Array.from(document.querySelectorAll('a[href]')).map(a=>a.getAttribute('href'))")
    slecht = [x for x in hrefs if re.search(r'asteria\.nl', x) and not x.startswith('mailto:') and not re.search(r'www\.asteria\.nl/(privacy|algemene-voorwaarden|de/datenschutz)$|visit\.asteria\.nl/wellnesshotel-limburg-de', x)]
    slecht += [x for x in hrefs if x.startswith('/') and x not in ('/wellnesshotel-limburg-de',)]
    ok(not slecht, 'geen links naar asteria.nl of NL-pagina\'s ' + ' '.join(slecht[:4]))

    # geen Nederlandse literals in de zichtbare tekst + aria-labels
    tekst = await pg.evaluate("""()=>document.body.innerText+' '+Array.from(document.querySelectorAll('[aria-label],[alt],[placeholder]'))
      .map(e=>(e.getAttribute('aria-label')||'')+' '+(e.getAttribute('alt')||'')+' '+(e.getAttribute('placeholder')||'')).join(' ')""")
    nl = [x for x in NL_WOORDEN if re.search(r'(?<![A-Za-zÄÖÜäöüß])' + re.escape(x.strip()) + r'(?![A-Za-zÄÖÜäöüß])', tekst)]
    ok(not nl, 'geen Nederlandse literals ' + ', '.join(nl))
    ok('—' not in tekst, 'geen em-dashes')
    ok('Schwimmbad' not in tekst and 'Hallenbad' not in tekst, 'geen zwembad genoemd')

    # hero
    hero = await pg.evaluate("""()=>{const h=document.querySelector('.al-hero'),f=h.querySelector('.al-hero__foto').getBoundingClientRect(),
      b=h.querySelector('.al-hero .mews-open').getBoundingClientRect(),g=h.querySelector('.al-hero__badge').getBoundingClientRect(),
      v=h.querySelector('video');return {fh:f.height,fb:f.bottom,ht:h.getBoundingClientRect().top,bt:b.top,bb:b.bottom,gx:g.right,gy:g.top,vsrc:v.currentSrc||v.src||'',
      over:document.documentElement.classList.contains('al-kop-over')}}""")
    ok(hero['over'], 'kop doorschijnend over de hero')
    if mob:
        ok(abs(hero['fh'] - 0.75 * h) < 4, f'telefoon: videovak 75svh ({hero["fh"]:.0f} van {h})')
        ok(hero['bt'] < hero['fb'] < hero['bb'], 'telefoon: knop op de onderrand van de video')
        ok(abs(hero['ht']) < 1, f"hero begint bovenaan de pagina, onder de doorschijnende kop ({hero['ht']})")
        ok('9x16' in hero['vsrc'], 'telefoon: 9:16-video')
    else:
        ok('16x9' in hero['vsrc'], 'bureaublad: 16:9-video')
        ok(hero['gx'] >= w - 1 and hero['gy'] < 200, 'Google-badge rechtsboven')
    balk = await pg.evaluate("()=>document.querySelector('.mob-cta').classList.contains('is-zichtbaar')")
    ok(not balk, 'onderbalk niet zichtbaar in de hero')

    # arrangementen
    codes = await pg.evaluate("()=>Array.from(document.querySelectorAll('.al-ak .al-ak__knop')).map(a=>a.getAttribute('data-voucher'))")
    ok(codes == ['WINTER27', 'WELLNESS2026', 'NAJAAR2D'], 'kaartcodes ' + ','.join(codes))
    prijzen = await pg.evaluate("()=>Array.from(document.querySelectorAll('.al-ak__prijs')).map(p=>p.textContent.replace(/\\s+/g,' ').trim())")
    ok('119' in prijzen[1] and '121' in prijzen[2] and '134,50' in prijzen[0] and '999' not in prijzen[0], 'vanaf-prijzen (live wellness/herbst, vast winter) ' + ' | '.join(prijzen))
    uit = await pg.evaluate("()=>{const k=document.querySelector('.al-ak--uit');return getComputedStyle(k).borderTopColor}")
    ok('199, 110, 78' in uit, 'uitgelichte kaart met terracotta rand')

    # fotoslider + lightbox
    nrond = await pg.locator('.al-rond__item').count()
    ok(nrond == 7, f'fotoslider 7 foto\'s ({nrond})')
    await pg.locator('.al-rond').scroll_into_view_if_needed()
    await pg.click('.al-rond [data-rond-stap="1"]')
    await pg.wait_for_timeout(800)
    st = await pg.evaluate("()=>document.querySelector('.al-rond__status').textContent")
    ok(st.startswith('2/7'), 'slider stap naar 2/7')
    trans = await pg.evaluate("()=>getComputedStyle(document.querySelector('.al-rond__item')).transition")
    ok('0.7s' in trans and 'cubic-bezier(0.32, 0.72, 0, 1)' in trans, 'slider-overgang 700 ms cubic-bezier(.32,.72,0,1)')
    await pg.click('.al-rond__item--0 .al-rond__vergroot')
    lbo = await pg.evaluate("()=>!document.querySelector('[data-lb]').hidden && document.querySelector('.al-lb__teller').textContent")
    ok(lbo == '2/7', 'lightbox open op 2/7')
    await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(300)
    lbo = await pg.evaluate("()=>document.querySelector('.al-lb__teller').textContent")
    ok(lbo == '3/7', 'lightbox bladert naar 3/7')
    await pg.keyboard.press('Escape')
    ok(await pg.evaluate("()=>document.querySelector('[data-lb]').hidden"), 'lightbox sluit met Escape')

    # FAQ-tabs
    await pg.locator('.al-faq').scroll_into_view_if_needed()
    zicht = await pg.evaluate("()=>[!document.getElementById('al-faq-thema').hidden,!document.getElementById('al-faq-alg').hidden]")
    ok(zicht == [True, False], 'FAQ: tab Wellness actief')
    await pg.click('#al-tab-alg')
    zicht = await pg.evaluate("()=>[!document.getElementById('al-faq-thema').hidden,!document.getElementById('al-faq-alg').hidden]")
    ok(zicht == [False, True], 'FAQ: tab Allgemein werkt')

    # omgeving 1/6 -> 2/6
    await pg.locator('.al-omg').scroll_into_view_if_needed()
    t1 = await pg.evaluate("()=>document.querySelector('.al-omg__teller').textContent")
    await pg.click('.al-omg__pijl[data-stap="1"]')
    await pg.wait_for_timeout(900)
    t2 = await pg.evaluate("()=>document.querySelector('.al-omg__teller').textContent")
    ok(t1 == '1/6' and t2 == '2/6', f'omgeving {t1} -> {t2}')

    # kamerprijzen live
    kp = await pg.evaluate("()=>document.querySelectorAll('.kk-kaart:not([data-kloon]) .kk-prijs.is-gevuld').length")
    ok(kp == 7, f'7 kamerprijzen gevuld ({kp})')

    # pop-ups: elke soort opent, zonder scroll op het bureaublad
    sleutels = await pg.evaluate("()=>[...new Set(Array.from(document.querySelectorAll('[data-pop]')).filter(a=>!a.closest('[data-kloon]')).map(a=>a.getAttribute('data-pop')))]")
    maten = [(1024, 768), (1280, 800), (1440, 900), (1920, 1080), (2560, 1440)] if not mob else [(w, h)]
    for vw, vh in maten:
        await pg.set_viewport_size({'width': vw, 'height': vh})
        await pg.wait_for_timeout(150)
        mis = []
        for s in sleutels:
            el = pg.locator(f'[data-pop="{s}"]:not([data-kloon] *)').first
            await el.scroll_into_view_if_needed()
            await el.click()
            await pg.wait_for_timeout(250)
            r = await pg.evaluate("""()=>{const p=document.querySelector('[data-pop-dialog]');if(p.hidden)return null;const k=p.querySelector('.al-pop__kaart'),
              b=p.querySelector('.al-pop__body'),kr=k.getBoundingClientRect();return {scroll:b.scrollHeight-b.clientHeight,kh:k.scrollHeight-k.clientHeight,
              top:kr.top,bot:kr.bottom,vh:innerHeight,naam:(p.querySelector('.al-pop__naam')||{}).textContent,boek:!!p.querySelector('.al-pop__boek'),
              video:!!p.querySelector('video')}}""")
            if not r:
                mis.append(s + ':niet open')
            else:
                if not mob and (r['scroll'] > 1 or r['kh'] > 1 or r['top'] < 0 or r['bot'] > r['vh']):
                    mis.append(f"{s}:scroll {r['scroll']}/{r['kh']}")
                if mob and r['bot'] > r['vh'] + 1:
                    mis.append(f'{s}:buiten beeld')
                if s.startswith('kamer:') and not r['video']:
                    mis.append(s + ':geen video')
            await pg.keyboard.press('Escape')
            await pg.wait_for_timeout(80)
        ok(not mis, f'pop-ups {len(sleutels)} stuks op {vw}x{vh} open en zonder scroll ' + ' '.join(mis[:5]))
    await pg.set_viewport_size({'width': w, 'height': h})
    await pg.wait_for_timeout(200)
    if mob:
        sheet = await pg.evaluate("()=>getComputedStyle(document.querySelector('.al-pop')).alignItems")
        ok(sheet == 'flex-end', 'telefoon: pop-up als sheet van onderaf')

    # prijskalender (WELLNESS2026) opent en geeft prijzen
    await pg.locator('.al-ak--uit .al-ak__knop').scroll_into_view_if_needed()
    await pg.click('.al-ak--uit .al-ak__knop')
    await pg.wait_for_timeout(900)
    kal = await pg.evaluate("""()=>{const k=document.getElementById('ar-kal');return k&&k.open?{code:k.dataset.code,
      prijzen:k.querySelectorAll('.ark-d .t.p').length,kop:k.querySelector('.ark-kop').textContent,wd:k.querySelector('.ark-wdag').textContent}:null}""")
    ok(kal and kal['code'] == 'WELLNESS2026' and kal['prijzen'] > 5, 'prijskalender WELLNESS2026 open met prijzen ' + json.dumps(kal, ensure_ascii=False))
    ok(kal and kal['wd'].startswith('MoDiMi'), 'kalender in het Duits (weekdagen)')
    ok(log['mews_script'] == 0, 'kalender opent zonder Mews te laden')
    # twee dagen kiezen en bevestigen -> Mews met WELLNESS2026, datums en de-DE
    cellen = pg.locator('#ar-kal .ark-d.kan')
    await cellen.nth(3).click(); await pg.wait_for_timeout(100)
    await pg.locator('#ar-kal .ark-d.kan').nth(4).click(); await pg.wait_for_timeout(100)
    await pg.click('#ar-kal .ark-btn')
    await pg.wait_for_timeout(600)
    mw = await pg.evaluate("()=>window.__mews||[]")
    calls = [c for m in mw for c in m['calls']]
    ok(log['mews_script'] == 1 and ['setVoucherCode', 'WELLNESS2026'] in calls and ['setLanguageCode', 'de-DE'] in calls
       and any(c[0] == 'setStartDate' for c in calls) and ['open'] in calls, 'kalender -> Mews met code, datums, de-DE')
    # Winterarrangement: eigen config
    await pg.locator('.al-ak--buiten .al-ak__knop').first.scroll_into_view_if_needed()
    await pg.click('.al-ak--buiten .al-ak__knop >> nth=0')
    await pg.wait_for_timeout(700)
    wk = await pg.evaluate("()=>{const k=document.getElementById('ar-kal');return k&&k.open?[k.dataset.code,k.dataset.mewsConfig,k.dataset.nachten]:null}")
    ok(wk == ['WINTER27', '95c70e27-1332-4d94-a1d4-b4f900da3be8', '2'], 'winterkalender met eigen Mews-config en 2 nachten ' + str(wk))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    await pg.evaluate("()=>{const k=document.getElementById('ar-kal');if(k&&k.open)k.close()}")

    # heroknop en kamerknop openen Mews
    await pg.evaluate("()=>{window.__mews.forEach(m=>m.calls=[]);window.scrollTo(0,0)}")
    await pg.click('.al-hero .mews-open')
    await pg.wait_for_timeout(300)
    mw = await pg.evaluate("()=>window.__mews")
    std = [m for m in mw if m['cfg'].startswith('6dc9094c')]
    ok(std and ['open'] in std[0]['calls'] and ['setLanguageCode', 'de-DE'] in std[0]['calls'] and std[0]['taal'] == 'de-DE', 'heroknop opent Mews (de-DE)')
    await pg.evaluate("()=>window.__mews.forEach(m=>m.calls=[])")
    await pg.locator('.kk-kaart:not([data-kloon]) .mews-open').first.scroll_into_view_if_needed()
    await pg.locator('.kk-kaart:not([data-kloon]) .mews-open').first.click()
    await pg.wait_for_timeout(300)
    mw = await pg.evaluate("()=>window.__mews")
    calls = [c for m in mw for c in m['calls']]
    ok(['showRates', 'c737de50-e41e-4c8d-a818-af1d00ffc315'] in calls and ['open'] in calls, 'kamerknop (Deluxe) opent Mews met de kamer')

    # onderbalk na de hero (telefoon)
    if mob:
        await pg.evaluate("()=>window.scrollTo(0, document.querySelector('.al-intro').offsetTop + 400)")
        await pg.wait_for_timeout(500)
        ok(await pg.evaluate("()=>document.querySelector('.mob-cta').classList.contains('is-zichtbaar')"), 'onderbalk zichtbaar na de hero')

    # nieuwsbrief
    await pg.locator('#al-nb').scroll_into_view_if_needed()
    await pg.wait_for_timeout(2100)
    await pg.fill('#al-nb-email', 'test@example.com')
    await pg.click('.al-nb__knop')
    await pg.wait_for_timeout(400)
    nbm = await pg.evaluate("()=>document.querySelector('.al-nb__melding').textContent")
    ok(log.get('nieuwsbrief') and '"taal": "de"' in json.dumps(json.loads(log['nieuwsbrief'])).replace('":"', '": "') and 'Vielen Dank' in nbm, 'nieuwsbrief POST taal de')

    await ctx.close()
    if schermafdruk:
        ctx = await browser.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
        await mocks(ctx, {'mews_script': 0})
        pg = await ctx.new_page()
        await pg.add_init_script("try{sessionStorage.setItem('ec_shown','1');localStorage.setItem('cookie-consent','1')}catch(e){}")
        await pg.goto(URL, wait_until='networkidle')
        await schermafdrukken(pg, w, schermafdruk)
        await ctx.close()

    # reduced motion: geen video, geen overgangen
    ctx = await browser.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, reduced_motion='reduce')
    await mocks(ctx, {'mews_script': 0})
    pg = await ctx.new_page()
    await pg.goto(URL, wait_until='networkidle')
    rm = await pg.evaluate("""()=>({v:document.querySelector('.al-hero video').getAttribute('src'),
      t:getComputedStyle(document.querySelector('.al-rond__item')).transitionDuration})""")
    ok(not rm['v'] and rm['t'] in ('0s', '0s, 0s'), f'reduced motion: geen video, geen overgang ({rm})')
    await ctx.close()

    # zonder JavaScript
    ctx = await browser.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, java_script_enabled=False)
    pg = await ctx.new_page()
    await pg.goto(URL, wait_until='load')
    zicht_thema = await pg.locator('#al-faq-thema').is_visible()
    zicht_alg = await pg.locator('#al-faq-alg').is_visible()
    tabs = await pg.locator('.al-faq__tabs').is_visible()
    h1 = await pg.locator('h1').is_visible()
    ok(zicht_thema and zicht_alg and not tabs and h1, 'zonder JS: hero zichtbaar, beide vragenlijsten onder elkaar, geen tabs')
    await ctx.close()
    await browser.close()


async def schermafdrukken(pg, w, map_):
    os.makedirs(map_, exist_ok=True)
    await pg.evaluate("()=>{const k=document.getElementById('ar-kal');if(k&&k.open)k.close();document.documentElement.classList.remove('ark-open','ark-slot')}")
    await pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,50));}window.scrollTo(0,0)}")
    await pg.wait_for_timeout(600)
    # per blok schermvullende opnames bij de normale vensterhoogte (full-page-opnames veranderen de vensterhoogte,
    # waardoor de compacte kamerkaart en de lusrijen niet meer kloppen); te hoog blok = meer opnames onder elkaar
    vh = pg.viewport_size['height']
    blokken = await pg.evaluate("()=>[['kop',document.querySelector('.top-stack')]].concat(Array.from(document.querySelectorAll('main > [data-component]')).map(e=>[e.getAttribute('data-component'),e])).concat([['voet',document.querySelector('footer')]]).map(([n,e])=>{const r=e.getBoundingClientRect();return [n,r.top+scrollY,r.height]})")
    from PIL import Image
    for i, (n, y, hh) in enumerate(blokken):
        zicht = '' if i < 2 else 'hidden'
        await pg.evaluate("z=>{document.querySelector('.top-stack').style.visibility=z;document.querySelector('.mob-cta').style.display='none'}", zicht)
        delen, dy = [], 0
        while dy < hh - 1:
            await pg.evaluate(f'window.scrollTo(0,{y + dy})')
            await pg.wait_for_timeout(250)
            echt = await pg.evaluate('scrollY')
            pad = os.path.join(map_, f'_tmp{len(delen)}.png')
            await pg.screenshot(path=pad)
            hoog = min(vh, hh - dy)
            off = (y + dy) - echt
            delen.append(Image.open(pad).crop((0, int(off), w, int(off + hoog))))
            dy += vh
        tot = Image.new('RGB', (w, sum(x.height for x in delen)))
        yy = 0
        for x in delen:
            tot.paste(x, (0, yy)); yy += x.height
        tot.save(os.path.join(map_, f'al-{w}-{i:02d}-{n}.png'))
    for f in glob.glob(os.path.join(map_, '_tmp*.png')):
        os.remove(f)
    await pg.evaluate("()=>{document.querySelector('.top-stack').style.visibility='';document.querySelector('.mob-cta').style.display=''}")
    # een pop-up per soort
    for s in ['arr:wellness', 'kamer:deluxe', 'fac:wellness', 'uitje:maasduinen']:
        el = pg.locator(f'[data-pop="{s}"]').first
        await el.scroll_into_view_if_needed(); await el.click(); await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(map_, f'al-{w}-pop-{s.replace(":", "-")}.png'))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(150)
    el = pg.locator('.al-ak--uit .al-ak__knop')
    await el.scroll_into_view_if_needed(); await el.click(); await pg.wait_for_timeout(900)
    await pg.screenshot(path=os.path.join(map_, f'al-{w}-kalender.png'))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    await pg.screenshot(path=os.path.join(map_, f'al-{w}-full.png'), full_page=True)


async def main():
    fouten = []
    async with async_playwright() as p:
        for w in BREEDTES:
            print(f'== {w} px ==')
            await test_breedte(p, w, fouten, SHOT)
    print()
    if fouten:
        print(f'{len(fouten)} controle(s) FOUT:')
        for f in fouten:
            print('  -', f)
        sys.exit(1)
    print('Alle controles groen.')

asyncio.run(main())
