#!/usr/bin/env python3
"""Playwright-test voor de prijskalender "Kies je nachten" op de arrangementpagina's (dialoog #ar-kal,
arrangement-kalender.js/.css, /api/arr-kalender).

Gebruik:
  python3 -m http.server 8765        # in de repo-root (of: npx wrangler pages dev . --port 8788)
  python3 scripts/test_arr_kalender.py http://localhost:8765/najaarsarrangement.html [--echt] [--schermafdruk qa/arr-kalender]

Standaard wordt /api/arr-kalender gemockt (Playwright route): deterministische prijzen per kamer, elke zondag
EUR 20 per kamer lager (berekend), elke woensdag dicht, Weekend alleen vr/za. Met --echt gaat de pagina naar de
echte API (wrangler pages dev of de preview) en controleert de test alleen wat altijd moet gelden.
Checks (1440 en 390):
- pop-up opent bij zijkaartknop (1440), telefoonkaart en onderbalk (390), kamerknop (noot noemt die kamer), datumveld en
  knop van de boekbalk (1440), slotknop; geen native datumkiezer;
- prijs in de cellen (EUR ceil(cent/100/2)), zondag goud met de lagere prijs, dicht grijs doorgestreept;
- normaal: A en B kiezen, samenvatting "N nachten", knop aan; vaste nachten (data-nachten > 1): één klik = aankomst +
  vertrek N dagen later; Weekend: alleen vr/za klikbaar;
- bevestigen: widget-log (gestubde Mews-API) met datums, voucher en, via een kamerknop, de kamer (showRates);
  zonder kamer via de boekbalk (window.lpBoekbalk met mewsStart/mewsEnd);
- Esc sluit; telefoon: bottom sheet binnen beeld, geen horizontale overloop; geen consolefouten.
"""
import sys, json, re
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
ECHT = '--echt' in args
if ECHT: args.remove('--echt')
shotdir = None
if '--schermafdruk' in args:
    i = args.index('--schermafdruk'); shotdir = args[i + 1]; del args[i:i + 2]
URL = args[0] if args else 'http://localhost:8765/najaarsarrangement.html'
NAAM = URL.rstrip('/').rsplit('/', 1)[-1].replace('.html', '')
resultaten = []

def check(naam, ok, info=''):
    resultaten.append((naam, ok, info))
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({info})' if info else ''))

CATS = {  # categorie -> basisprijs voor 2 personen per nacht, in centen
    '98900f3b-e5e2-49c9-9776-af1d00ffc315': 24900, '85ca19d7-eea5-41c8-8b93-af1d00ffc315': 25900,
    'fa5b6540-7234-49ce-beb1-af1d00ffc315': 24900, 'a8fd7310-0d61-422f-89e6-af1d00ffc315': 25900,
    'c737de50-e41e-4c8d-a818-af1d00ffc315': 26900, '27ea8deb-ded5-4856-8fdd-af1d00ffc315': 27900,
    '4a642b66-68e6-444c-beeb-af1d00ffc315': 28900, 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2': 30900,
}
STAND = {}  # wordt gevuld uit de dialoog: nachten, aankomstdagen, zondag

def mock(route):
    q = parse_qs(urlparse(route.request.url).query)
    code, maand, deel = q['code'][0], q['maand'][0], int(q['deel'][0])
    j, m = map(int, maand.split('-'))
    laatste = (date(j + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).day
    van, tot = (deel - 1) * 8 + 1, (laatste if deel == 4 else min(deel * 8, laatste))
    n, dagen, zondag = STAND['nachten'], STAND['aankomstdagen'], STAND['zondag']
    uit = []
    for g in range(van, tot + 1):
        d = date(j, m, g); wd = (d.weekday() + 1) % 7  # 0 = zondag
        mag = not dagen or wd in dagen
        x = {'datum': d.isoformat(), 'zondag': wd == 0, 'aankomst_mag': mag}
        if d < date.today(): x.update(beschikbaar=False, buiten_bereik=True)
        elif not mag or wd == 3: x.update(beschikbaar=False)
        else:
            pr = {}
            for c, p in CATS.items():
                cent = p * n
                b = zondag and wd == 0
                pr[c] = {'prijs_cent': cent - 2000 if b else cent, 'berekend': b}
            x.update(beschikbaar=True, prijzen=pr)
        uit.append(x)
    route.fulfill(status=200, content_type='application/json',
                  body=json.dumps({'ok': True, 'code': code, 'maand': maand, 'deel': deel, 'nachten': n, 'personen': 2, 'dagen': uit}))

STUB = """()=>{window._mews=[];window.mewsApi={setVoucherCode:v=>_mews.push('v:'+v),setLanguageCode:()=>{},
  setStartDate:d=>_mews.push('s:'+d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')),
  setEndDate:d=>_mews.push('e:'+d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')),
  setAdultCount:n=>_mews.push('a:'+n),showRates:r=>_mews.push('r:'+r),open:()=>_mews.push('open')}}"""

STAAT = """()=>{const p=document.getElementById('ar-kal'),r=p.getBoundingClientRect();
  return {open:p.open&&p.classList.contains('toon'),kant:p.getAttribute('data-kant'),l:Math.round(r.left),r:Math.round(r.right),t:Math.round(r.top),b:Math.round(r.bottom),
    kamer:p.querySelector('.ark-kamer').textContent,maanden:p.querySelectorAll('.ark-maand').length,sw:document.documentElement.scrollWidth,
    prijzen:p.querySelectorAll('.ark-d .t.p').length,laden:p.querySelectorAll('.ark-d.laden').length}}"""

def wacht_prijzen(pg):
    for _ in range(60):
        s = pg.evaluate(STAAT)
        if s['prijzen'] and not s['laden']: return s
        pg.wait_for_timeout(250)
    return pg.evaluate(STAAT)

def sluit(pg):
    pg.keyboard.press('Escape'); pg.wait_for_timeout(450)

def eerste_kiesbare(pg, na=None, zondag=None):
    """datum van de eerste kiesbare cel (optioneel na een datum, optioneel zondag)."""
    return pg.evaluate("""([na,zo])=>{for(const c of document.querySelectorAll('#ar-kal .ark-d.kan[data-d]')){const d=c.dataset.d;
        if(na&&d<=na)continue;if(zo!==null&&(new Date(d+'T12:00:00').getDay()===0)!==zo)continue;if(!c.querySelector('.t.p'))continue;return d}return null}""", [na, zondag])

def klik_dag(pg, d):
    pg.locator(f'#ar-kal .ark-d[data-d="{d}"]').click(); pg.wait_for_timeout(150)

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, mob in [(1440, 900, False), (390, 844, True)]:
        tag = f'[{w}]'
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob)
        ctx.add_init_script("try{localStorage.setItem('cookie-consent','1')}catch(e){}")
        # de echte Mews-widget niet laden (de test stubt window.mewsApi)
        ctx.route('**/distributor.min.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=''))
        if not ECHT:
            ctx.route('**/api/arr-kalender*', mock)
        pg = ctx.new_page(); fouten = []
        pg.on('console', lambda m: fouten.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: fouten.append(str(e)))
        pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(500)
        cfg = pg.evaluate("(()=>{const d=document.getElementById('ar-kal').dataset;return {code:d.code,nachten:+d.nachten,dagen:d.aankomstdagen,zondag:d.zondag,std:d.kamerStandaard,kamers:JSON.parse(d.kamers)}})()")
        STAND.update(nachten=cfg['nachten'], aankomstdagen=[int(x) for x in cfg['dagen'].split(',') if x], zondag=cfg['zondag'] == 'ja')
        CODE, N = cfg['code'], cfg['nachten']
        if w == 1440:
            check('[bron] dialoog met code, nachten, standaardkamer en kamernamen',
                  bool(CODE) and N >= 1 and cfg['std'] in cfg['kamers'], json.dumps(cfg, ensure_ascii=False)[:200])

        # 1. openen: zijkaart (1440) of telefoonkaart (390)
        knop = '.lp-zone-kant .b1k-knop' if not mob else '.b1a-mobkaart .b1k-knop'
        pg.locator(knop).first.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        pg.locator(knop).first.click(); pg.wait_for_timeout(500)
        s = wacht_prijzen(pg)
        check(f'{tag} kaartknop opent de kalender ({"2 maanden, naast de knop" if not mob else "1 maand, bottom sheet"})',
              s['open'] and s['maanden'] == (1 if mob else 2) and s['kamer'] == cfg['kamers'][cfg['std']]
              and (not mob or (s['l'] == 0 and s['r'] == w and s['b'] == h)) and (mob or s['kant'] in ('links', 'onder', 'boven')), str(s))
        check(f'{tag} geen horizontale overloop met kalender open', s['sw'] <= w and s['l'] >= 0 and s['r'] <= w, str(s))
        if shotdir:
            if mob: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kalender.png')
            else: pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kalender.png'); pg.locator('#ar-kal').screenshot(path=f'{shotdir}/{NAAM}-{w}-kalender-kaart.png')
        # 2. prijzen, zondag, dicht
        cel = pg.evaluate("""()=>{const o=[...document.querySelectorAll('#ar-kal .ark-d.open .t.p')].map(t=>t.textContent);
            const z=[...document.querySelectorAll('#ar-kal .ark-d.ark-dag--zondag')].map(c=>({d:c.dataset.d,p:c.querySelector('.t').textContent,
              bg:getComputedStyle(c).backgroundColor,rand:getComputedStyle(c).borderTopColor}));
            const g=[...document.querySelectorAll('#ar-kal .ark-d.open:not(.ark-dag--zondag) .t.p')].map(t=>t.textContent);
            const dicht=[...document.querySelectorAll('#ar-kal .ark-d.dicht')].map(c=>getComputedStyle(c.querySelector('.n')).textDecorationLine);
            return {open:o.length,eerste:o[0],zondag:z,gewoon:g.slice(0,3),dicht:dicht.length,doorgestreept:dicht.every(x=>x.includes('line-through'))}}""")
        if not ECHT:
            std_p = CATS[cfg['std']] * N
            gewoon = f"€ {-(-std_p // 200)}"
            zo = f"€ {-(-(std_p - 2000) // 200)}"
            check(f'{tag} prijs p.p. in de cellen ({gewoon})', cel['open'] > 0 and gewoon in cel['gewoon'], str(cel)[:200])
            if STAND['zondag']:
                check(f'{tag} zondag goud (zand + terracotta rand) met de lagere prijs {zo}',
                      len(cel['zondag']) > 0 and all(z['p'] == zo and z['bg'] == 'rgb(248, 237, 219)' and z['rand'] == 'rgb(199, 110, 78)' for z in cel['zondag']),
                      str(cel['zondag'][:2]))
            else:
                check(f'{tag} geen gouden zondag (arrangement zonder zondagvoordeel)', not cel['zondag'], str(cel['zondag'][:2]))
            check(f'{tag} dichte dagen grijs doorgestreept', cel['dicht'] > 0 and cel['doorgestreept'], str(cel['dicht']))
        else:
            check(f'{tag} echte prijzen in de cellen', cel['open'] > 0 and (cel['eerste'] or '').startswith('€ '), str(cel)[:200])
        if STAND['aankomstdagen']:
            wd = pg.evaluate("[...new Set([...document.querySelectorAll('#ar-kal .ark-d.kan[data-d]')].map(c=>new Date(c.dataset.d+'T12:00:00').getDay()))].sort()")
            check(f'{tag} alleen aankomstdagen {STAND["aankomstdagen"]} klikbaar', wd and set(wd) <= set(STAND['aankomstdagen']), str(wd))
        # 3. kiezen
        a = eerste_kiesbare(pg)
        if not a:
            pg.locator('#ar-kal .ark-pijl[data-r="1"]').click(); wacht_prijzen(pg); a = eerste_kiesbare(pg)
        klik_dag(pg, a)
        ad = date.fromisoformat(a)
        if N > 1:
            k = pg.evaluate("""()=>({sel:[...document.querySelectorAll('#ar-kal .ark-d.sel')].map(c=>c.dataset.d),vertrek:(document.querySelector('#ar-kal .ark-d.vertrek')||{}).dataset,
                wat:document.querySelector('#ar-kal .ark-wat').textContent,btn:!document.querySelector('#ar-kal .ark-btn').disabled})""")
            bd = ad + timedelta(days=N)
            check(f'{tag} één klik = aankomst + {N} nachten (reeks gemarkeerd, knop aan)',
                  len(k['sel']) == N and k['vertrek'] and k['vertrek'].get('d') == bd.isoformat() and f'{N} nachten' in k['wat'] and k['btn'], str(k))
        else:
            na = eerste_kiesbare(pg, na=a)
            bd = date.fromisoformat(na) if na else ad + timedelta(days=1)
            # een vertrek een paar dagen later, maar binnen een open reeks
            for extra in (2, 1):
                kand = (ad + timedelta(days=extra)).isoformat()
                if pg.evaluate(f"!!document.querySelector('#ar-kal .ark-d.kan[data-d=\"{kand}\"]')"):
                    bd = ad + timedelta(days=extra); break
            pg.locator(f'#ar-kal .ark-d[data-d="{bd.isoformat()}"]').hover(); pg.wait_for_timeout(120)
            hv = pg.evaluate("document.querySelectorAll('#ar-kal .ark-d.sel').length")
            klik_dag(pg, bd.isoformat())
            k = pg.evaluate("""()=>({sel:document.querySelectorAll('#ar-kal .ark-d.sel').length,wat:document.querySelector('#ar-kal .ark-wat').textContent,btn:!document.querySelector('#ar-kal .ark-btn').disabled})""")
            n = (bd - ad).days
            check(f'{tag} aankomst en vertrek kiezen (hover toont de reeks, {n} nacht' + ('en' if n > 1 else '') + ')',
                  hv == n and k['sel'] == n and f'{n} nacht' in k['wat'] and k['btn'], f'hover={hv} {k}')
        # 4. bevestigen zonder kamer: via de boekbalk
        pg.evaluate(STUB)
        pg.locator('#ar-kal .ark-btn').click(); pg.wait_for_timeout(500)
        log = pg.evaluate("({lp:window.lpBoekbalk||null,ark:window.arKalender||null,m:window._mews.slice(),open:document.getElementById('ar-kal').classList.contains('toon')})")
        lp = log['lp'] or {}
        check(f'{tag} bevestigen: boekbalk naar de widget met {CODE}, {a} t/m {bd.isoformat()}',
              lp.get('route') == 'widget' and lp.get('voucher') == CODE and lp.get('start') == a and lp.get('eind') == bd.isoformat()
              and f's:{a}' in log['m'] and f'e:{bd.isoformat()}' in log['m'] and 'open' in log['m'] and not log['open'], json.dumps(log)[:300])
        print('     widget-log:', json.dumps(log['m']))
        pg.wait_for_timeout(400)

        # 5. kamerknop: opent met die kamer; bevestigen geeft showRates(kamer) met datums en voucher
        kk = pg.evaluate("""()=>{const k=[...document.querySelectorAll('.b4b-kaart:not([data-kloon]) .mews-open[data-room]')].find(a=>a.offsetParent);
            if(!k)return null;k.scrollIntoView({block:'center'});return {room:k.dataset.room}}""")
        pg.wait_for_timeout(500)
        if kk:
            pg.locator(f'.b4b-kaart:not([data-kloon]) .mews-open[data-room="{kk["room"]}"]').first.click(); pg.wait_for_timeout(400)
            s = wacht_prijzen(pg)
            check(f'{tag} kamerknop opent de kalender voor die kamer ({cfg["kamers"].get(kk["room"])})', s['open'] and s['kamer'] == cfg['kamers'].get(kk['room']), str(s))
            a2 = eerste_kiesbare(pg)
            if a2:
                klik_dag(pg, a2)
                if N == 1:
                    b2 = eerste_kiesbare(pg, na=a2)
                    if b2 and pg.evaluate(f"!!document.querySelector('#ar-kal .ark-d.kan[data-d=\"{(date.fromisoformat(a2)+timedelta(days=1)).isoformat()}\"]')"):
                        b2 = (date.fromisoformat(a2) + timedelta(days=1)).isoformat()
                    klik_dag(pg, b2)
                else:
                    b2 = (date.fromisoformat(a2) + timedelta(days=N)).isoformat()
                pg.evaluate(STUB)
                pg.locator('#ar-kal .ark-btn').click(); pg.wait_for_timeout(500)
                m = pg.evaluate('window._mews.slice()')
                check(f'{tag} bevestigen met kamer: widget krijgt datums, voucher en showRates(kamer)',
                      m[:2] == [f's:{a2}', f'e:{b2}'] and f'v:{CODE}' in m and f'r:{kk["room"]}' in m, str(m))
                print('     widget-log kamer:', json.dumps(m))
            else:
                check(f'{tag} kamerknop: kiesbare dag gevonden', False, 'geen kiesbare dag voor deze kamer')
        else:
            check(f'{tag} kamerknop gevonden', False)

        # 6. boekbalk (1440): datumveld en knop openen de kalender, geen native datumkiezer; onderbalk (390)
        if not mob:
            pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)
            pg.locator('.b1a-balk .field--datum').first.click(); pg.wait_for_timeout(400)
            s = pg.evaluate(STAAT); foc = pg.evaluate("document.activeElement && document.activeElement.id")
            check(f'{tag} datumveld van de boekbalk opent de kalender (geen native kiezer)', s['open'] and foc != 'bb-aankomst', f'{s} focus={foc}')
            sluit(pg)
            s = pg.evaluate(STAAT)
            check(f'{tag} Esc sluit de kalender', not s['open'], str(s))
            pg.locator('.b1a-balk button[type=submit]').click(); pg.wait_for_timeout(400)
            s = pg.evaluate(STAAT)
            check(f'{tag} knop van de boekbalk opent de kalender', s['open'] and s['kant'] in ('onder', 'boven'), str(s))
            sluit(pg)
            pg.evaluate("document.querySelector('.b7a').scrollIntoView({block:'center'})"); pg.wait_for_timeout(500)
            pg.locator('.b7a-balk button[type=submit]').click(); pg.wait_for_timeout(400)
            s = pg.evaluate(STAAT)
            check(f'{tag} knop van het slotblok opent de kalender', s['open'] and s['t'] >= 0 and s['b'] <= h, str(s))
            pg.mouse.click(5, h // 2); pg.wait_for_timeout(400)
            s = pg.evaluate(STAAT)
            check(f'{tag} klik buiten de kalender sluit hem', not s['open'], str(s))
        else:
            pg.evaluate("window.scrollTo(0, document.querySelector('.b5a').getBoundingClientRect().top + scrollY)"); pg.wait_for_timeout(700)
            pg.locator('.mob-cta .mews-open').click(); pg.wait_for_timeout(500)
            s = wacht_prijzen(pg)
            check(f'{tag} onderbalk opent de kalender als bottom sheet binnen beeld', s['open'] and s['l'] == 0 and s['r'] == w and s['b'] == h and s['t'] > 0 and s['sw'] <= w, str(s))
            if shotdir:
                pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-onderbalk.png')
            sluit(pg)
            s = pg.evaluate(STAAT)
            check(f'{tag} Esc sluit de bottom sheet', not s['open'], str(s))
        if shotdir and not mob:
            # kalender met een keuze, voor de schermafdruk
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
            pg.locator('.lp-zone-kant .b1k-knop').first.scroll_into_view_if_needed()
            pg.locator('.lp-zone-kant .b1k-knop').first.click(); wacht_prijzen(pg)
            a3 = eerste_kiesbare(pg)
            if a3:
                klik_dag(pg, a3)
                if N == 1:
                    b3 = eerste_kiesbare(pg, na=a3)
                    if b3: pg.locator(f'#ar-kal .ark-d[data-d="{b3}"]').hover(); pg.wait_for_timeout(150)
            pg.screenshot(path=f'{shotdir}/{NAAM}-{w}-kalender-keuze.png')
            sluit(pg)
        eigen = [f for f in fouten if 'mews' not in f.lower()]
        check(f'{tag} geen consolefouten', not eigen, '; '.join(eigen)[:300])
        ctx.close()
    b.close()

mis = [r for r in resultaten if not r[1]]
print(f'\n{len(resultaten) - len(mis)}/{len(resultaten)} checks OK')
sys.exit(1 if mis else 0)
