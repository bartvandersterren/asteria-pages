# Session Notes — 2026-05-26

## Wat gedaan
- Tracking audit plan geschreven voor hotel-venray.html
- Task 1 ✅: D1 stats API werkt — 189 page_views, 71 popup_opens, 37 cta_clicks, 33 mews_clicks
- Task 2 ✅: Playwright bevestigt page_view + cta_click(sticky_fab) + popup_open correct verstuurd

## Wat open staat
- Task 3: handmatig GA4 DebugView (https://visit.asteria.nl/hotel-venray?gtag_debug=1 + GA4 property 262565995 → Beheer → DebugView)
- Task 4: data-track-cta toevoegen aan 5 CTAs in hotel-venray.html
- Task 5: Playwright verificatie na de fix

## Tracking gaps (gevonden, nog niet gefixed)
5 CTAs missen data-track-cta in hotel-venray.html:
- ~2651: nav desktop → data-track-cta="nav_desktop"
- ~2654: nav mobile → data-track-cta="nav_mobile"
- ~2944: arr-card L&O (id=bbCta) → data-track-cta="arr_logies"
- ~2971: arr-card Wellness → data-track-cta="arr_wellness"
- ~2998: arr-card Asperge → data-track-cta="arr_asperge"

## Plan
docs/superpowers/plans/2026-05-26-tracking-audit-hotel-venray.md
