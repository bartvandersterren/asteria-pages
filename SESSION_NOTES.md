# Session Notes — 2026-05-23

## Wat gedaan
- Mews Booking Engine widget geïntegreerd in `wellness-arr-c.html` (test)
- Mews script in `<head>` geladen via `Mews.D([configId], callback)`
- `launchMews()` helper: sluit eigen popup → opent Mews widget met datums + voucher
- Wachtrij (`window._mewsPending`) voor clicks vóór async init
- Fallback naar deeplink na 4 seconden timeout

## Probleem (onopgelost)
- `window.mewsApi` blijft `undefined` → fallback naar deeplink
- Callback van `Mews.D([id], callback)` vuurt blijkbaar niet
- Console bevestigt: `typeof Mews = object`, `typeof Mews.D = function`, `window.mewsApi = undefined`
- `showRates(categoryId)` getest maar geeft "PrimaryId" error → verwijderd

## Troubleshoot plan
1. Open pagina via Playwright MCP
2. Check via `browser_evaluate`: `typeof Mews, typeof Mews.D, window.mewsApi`
3. Probeer callback live in console te registreren
4. Bekijk Mews distributor.min.js source voor juiste API-aanroep
5. Alternatief: `Mews.D` direct in `launchMews` aanroepen zonder opgeslagen instance

## Nog te doen
- Fix doorzetten naar template + EN/DE versies
- GA4 tag toevoegen
- `lander-google.html` Mews widget (na succesvolle test wellness-arr-c)
