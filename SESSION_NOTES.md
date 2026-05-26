# Session Notes — 2026-05-26

## Wat gedaan

### Scentech weer-analyse (nieuw project)
Nieuw project aangemaakt: `~/Projects/scentech-weather-analyse/`

Onderzocht of weer invloed heeft op Scentech contribution margin. Eenmalig Python-analyseproject:
- Databron: Triple Whale API (contribution margin % per dag)
- Weerdata: Open-Meteo Archive API, De Bilt
- Periode: mei 2025 – mei 2026 (351 dagen met omzet)

**Bevindingen:**
- Temperatuur: r = −0.128, significant → warmere dagen = lagere marge
- Zonneschijn: r = −0.163, significant → meer zon = lagere marge
- Neerslag: niet significant → geen effect

**Metric:** (netSales − cogs − blendedAds) / netSales ≈ Triple Whale "Gross Profit / Revenue"
Gemiddelde contribution margin: ~29–36% over het jaar

**Rapport draaien:**
```bash
cd ~/Projects/scentech-weather-analyse && python3 analyse.py && open rapport.html
```

### Asteria tracking audit (vorige sessie, open)
- Task 3: handmatig GA4 DebugView (https://visit.asteria.nl/hotel-venray?gtag_debug=1)
- Task 4: data-track-cta toevoegen aan 5 CTAs in hotel-venray.html
  - ~2651: nav desktop → data-track-cta="nav_desktop"
  - ~2654: nav mobile → data-track-cta="nav_mobile"
  - ~2944: arr-card L&O (id=bbCta) → data-track-cta="arr_logies"
  - ~2971: arr-card Wellness → data-track-cta="arr_wellness"
  - ~2998: arr-card Asperge → data-track-cta="arr_asperge"
- Task 5: Playwright verificatie na de fix

## Plannen
- `docs/superpowers/plans/2026-05-26-tracking-audit-hotel-venray.md` — open
- `docs/superpowers/plans/2026-05-26-weer-verkoop-analyse.md` — afgerond
