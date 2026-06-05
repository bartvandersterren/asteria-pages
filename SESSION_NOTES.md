# Session Notes — 2026-06-05

## Wat gedaan

1. **Upgrade kosten p.p. → p.n.** in alle 3 talen (NL/EN/DE) — ROOMS_JS_DATA + ARR_C_PRICE_SUB
2. **Logo's EN/DE gefixt** — `asteria.{{HTML_LANG}}` → `asteria.nl` (asteria.en/de bestaan niet)
3. **CSS broken op EN/DE gefixt** — `i{{HTML_LANG}}ine-flex` → `inline` (was `ienine-flex` op EN)
4. **URL rename** — `wellness-arr-c` → `wellness-arrangement` (build.py, canonicals, taalswitch, taaldetectie)
   - Oude `wellness-arrangement.html` bewaard als `wellness-arrangement-v2.html`
   - `_redirects` bestand aangemaakt voor 301 redirects van oude URLs
5. **Mews taal per pagina** — `language` param in Distributor init: nl-NL / en-US / de-DE
6. **Sticky booking summary** — bk-summary + CTA sticky onderaan popup, kalender scrollt
   - Fix: `bk-step[hidden] { display: none !important }` nodig omdat flex de hidden attr overschreef

## Wat open

- Oude iteratie-bestanden opruimen (`wellness-arrangement-blok.html`, `-blok-b`, `-blok-c`, `-v2`)
- `hotel-venray.html` en `lander-google.html` hebben mogelijk dezelfde p.p./p.n. en logo issues
- Google Reviews API key nog niet geconfigureerd in Cloudflare (500 error)
