# Session Notes — 2026-05-25

## Gedaan

- Analytics gisteren (24 mei) opgezocht via D1: 69 page views, 24 popup_open, 8 cta_click, 1 mews_click, 1 email_success
- `email_popup_open` event toegevoegd aan hotel-venray.html, lander-google.html (alle 5 pagina's met email capture hadden dezelfde trigger)
- Dashboard uitgebreid: email_popup_open in funnel rij (paars, tussen boekpopup en stap 2)
- API: dashboard.js funnel object bevat nu ook email_popup_open

## Gotcha ontdekt

- D1 kolom heet `ts` (niet `created_at`) — stats API endpoint heeft geen datum-filter, altijd D1 direct bevragen via wrangler d1 execute --remote

## Open

- Historische email_popup_open data is 0 (event bestond niet voor 25-05-2026)
- Google Reviews API key nog steeds niet geconfigureerd in CF Pages dashboard
