# Session Notes — 2026-05-20 (sessie 4)

## Gedaan

### Translations refactor — plan gestart maar NIET afgerond

Plan aangemaakt maar schrijven mislukt vanwege te grote bestandsinhoud (bash heredoc + Write tool hadden moeite met special chars in JSON).

Geanalyseerd:
- Alle NL/EN/DE diffs grondig doorgelopen
- ~120 vertaalsleutels geïdentificeerd
- Aanpak vastgesteld: `{{key}}` template + 3 JSON-bestanden + build.py
- Bugs in huidige DE vertaling gevonden: `Kies een kamer`, `Cookiemelding`, `Comfortabele kamer` caption — fixen in refactor

## Openstaand — volgende sessie

### Translations refactor — plan schrijven

**Aanpak:**
- Gebruik Python script om planbestand te genereren (niet bash heredoc, niet Write tool voor grote bestanden)
- Of: schrijf plan in meerdere kleine Write tool-calls per sectie

**Wat het plan moet bevatten:**
- Task 1: translations/ map + nl.json + en.json + de.json (complete JSON met ~120 keys)
- Task 2: template aanmaken uit wellness-arr-c.html (complete substitutie-tabel)
- Task 3: build.py schrijven
- Task 4: testen lokaal
- Task 5: CLAUDE.md updaten + push

**Key design beslissingen (vastgesteld):**
- Template: `wellness-arr-c.template.html` met `{{key}}` markers
- Build: Python 3 stdlib, geen Cloudflare build-stap nodig (gegenereerde HTML gecommit)
- NL file is de basis voor het template
- Taaldetectie script (alleen NL): als `lang_detect_script` key — leeg in EN/DE
- fallback_reviews als JSON-string in key (zodat build.py simpel blijft)
- JS arrays (MONTH_NAMES etc.) als string-literal in JSON value

**Alle keys zijn geïdentificeerd** — zie analyse in sessie 4 (niet opgeslagen, herhaal via diff).

## Manuele stappen nog steeds openstaand

### CF Dashboard
1. D1 database aanmaken → `asteria-analytics`
2. Schema uitvoeren (zie header `functions/api/track.js`)
3. Binding `ASTERIA_D1` toevoegen
4. CF Access op `/admin/*` en `/api/stats*`

### Mews
- Voucher `WELLNESS124` (€124,50 p.p.)
- Voucher `WELKOM` (email capture)

### Revinate
- Welkomstautomation instellen

### Google Reviews
- `GOOGLE_PLACES_API_KEY` + Place ID in CF Pages dashboard
