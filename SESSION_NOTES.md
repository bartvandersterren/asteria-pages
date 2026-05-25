# Session Notes — 2026-05-25

## Wat gedaan
- Plan geschreven voor Mews boekingen in dashboard
- Zapier MCP verkend: Mews-koppeling werkt maar reservation lookup via MCP bleek niet mogelijk (permission/context issue)
- Geconcludeerd: fieldmapping verifiëren via "Test trigger" in Zapier UI

## Plan
`docs/superpowers/plans/2026-05-25-mews-boekingen-dashboard.md`

## Wat de volgende sessie oppakt
Uitvoeren van het plan, Task 1 t/m 7:
1. D1-tabel aanmaken (`mews_bookings`)
2. Webhook endpoint (`functions/api/mews-webhook.js`)
3. `dashboard.js` uitbreiden met `fetchMews()`
4. `admin/dashboard.html` uitbreiden met Mews-sectie
5. Cloudflare secret `MEWS_WEBHOOK_SECRET` instellen
6. Zapier Zap inrichten (handmatig)
7. End-to-end test via curl

## Zapier veldmapping
Exacte Mews veldnamen zijn onbekend — verifiëren via "Test trigger" in Zapier bij inrichten Zap.
Zoek naar: Channel/Source/Origin (moet "Mews Booking Engine" bevatten), Space Category Name, Total Price, Nights.
