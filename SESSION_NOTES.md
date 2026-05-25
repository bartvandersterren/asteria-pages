# Session Notes — 2026-05-25

## Gedaan
- Besproken dat Cloudflare D1 events client-side zijn en dus niet 100% accuraat (ad blockers)
- Mews Connector API als betrouwbaardere databron voor boekingen besproken (nog niet gebouwd)
- Zapier-MCP geïnstalleerd: `claude mcp add --transport http --scope user "Zapier-MCP" https://mcp.zapier.com/api/v1/connect`
  - Staat in user scope (~/.claude.json) — beschikbaar in alle projecten

## Open
- Mews Connector API integratie in dashboard (reserveringen, omzet, bezetting)
  - Vereist Mews Connector API credentials (AccessToken via Operations API)
  - Toe te voegen aan `functions/api/dashboard.js` als 4e databron naast D1/Ads/GA4

## Volgende sessie oppakt
- Na Zapier-MCP onboarding: bekijk welke Zapier skills relevant zijn
- Beslissen of Mews dashboard-integratie prioriteit heeft
