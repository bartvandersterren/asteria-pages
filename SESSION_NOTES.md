# Session Notes — 2026-05-23

## Wat onderzocht: bb-price / logies & ontbijt prijs

### Probleem
`/api/bb-price` geeft `{"error":"no session"}` — KV is leeg, sessie nooit geïnjecteerd.

### Bevindingen Mews API
- **Booking Engine API** (`api/bookingEngine/v1`) = voor de browser-widget, heeft Cloudflare anti-scraping bescherming
- Sessie tokens zijn client-side gegenereerd via Cloudflare challenge — niet na te bouwen zonder echte browser
- Zelf gegenereerde sessie geeft `{"Message":"Invalid Client."}` — Cloudflare valideert de token
- Met gecaptured echte sessie werkt `getPricing` WEL server-side:
  - Endpoint: `POST https://api.mews.com/api/bookingEngine/v1/services/getPricing`
  - Response: `CategoryPrices[].OccupancyPrices[].RateGroupPrices[].MinPrice.TotalAmount.GrossValue`
  - Comfort kamer 2 personen: €151,85/nacht → €75,93 p.p.
- **Connector API** = de juiste server-to-server API. Vereist ClientToken (certificeringsproces) + AccessToken. Bart heeft dit in gang gezet, duurt lang.

### Zapier optie geëvalueerd
- Zapier heeft Mews integratie met "Search for Current Rate Prices" action
- Mews al gekoppeld aan Zapier account
- 4x/uur updates = 5.760 tasks/maand → ~$50-73/maand op Professional plan
- **Conclusie: niet de moeite waard** voor een "vanaf prijs" op een landingspagina
- Zapier geeft ook geen prijskalender — dat kan alleen de Connector API

### Beslissing
1. **Nu:** Hardcode "vanaf €76,–" p.p. in hotel-venray.html en lander-google.html
2. **Later (na Connector API credentials):** Real-time prijs + prijskalender bouwen

### Volgende sessie: doe dit
- Hardcode prijs in hotel-venray.html en lander-google.html
- Vervang de fetch('/api/bb-price') logica door vaste tekst
- Bevestig bedrag met Bart (live test gaf €76,– p.p.)
- bb-price.js ongemoeid laten
- Plan docs/superpowers/plans/2026-05-23-bb-price-fix.md NIET uitvoeren — wacht op Connector API
