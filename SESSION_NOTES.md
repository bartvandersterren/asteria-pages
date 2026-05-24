# Session Notes — 2026-05-24

## Wat gedaan

### Admin Dashboard gebouwd (visit.asteria.nl/admin/dashboard)

Twee nieuwe bestanden:
- `functions/api/dashboard.js` — Cloudflare Function die D1 + Maton Google Ads API + Maton GA4 API parallel aggregeert
- `admin/dashboard.html` — Dashboard UI met 5 secties

### Features
- **Google Ads:** spend, kliks, revenue, ROAS + campagne-tabel (0-spend gefilterd)
- **Funnel:** bezoekers → popup → stap2 → Mews → email (% van bezoekers + % van popup voor Mews)
- **A/B tests:** variant_price A vs B met CVR
- **Interacties:** CTA kliks + email submit/success ratio
- **GA4:** sessies, gebruikers, bounce rate, gem. duur
- **Periode-toggle:** Vandaag / Gisteren / 7 dagen / 30 dagen

### Secrets gezet via wrangler
- `MATON_API_KEY` — Maton API key (Google Ads + GA4 proxy)
- `DASHBOARD_SECRET` — `EVdVu33QbrfBYn2OY2_MpVqplVriKNTSzUugENsDlX0`

### Auth
Dashboard endpoint vereist `Authorization: Bearer <DASHBOARD_SECRET>` header.
HTML slaat token op in `localStorage('asteria_dashboard_secret')` — bij eerste bezoek prompt.

## Open / volgende sessie
- Geen open taken
- Eventueel: time-series grafieken toevoegen (buiten huidige scope)
