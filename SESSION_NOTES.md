# Session Notes — 2026-05-22

## Wat gedaan

- **hotel-venray.html** aangemaakt als nieuwe Google Ads lander (fork van lander-google.html)
  - URL: visit.asteria.nl/hotel-venray
  - lander-google.html blijft bestaan maar wordt niet meer bijgehouden

- **Arrangement "Boek direct"** gaat nu via booking popup flow (datum kiezen → kamer → Mews)
  - arr-kaart CTA: `<button onclick="openBookingPopup(null, 'VOUCHER')">`
  - arr-popup CTA: sluit popup → opent booking popup met voucher
  - `buildBookingUrl` gebruikt `pendingVoucherCode` state variabele
  - Vouchers: 2026WELLNESS (wellness), ASPERGE (asperge), null (L&O)

- **Mobile arrangement kaarten**: layout verticaal (foto boven, tekst onder)
  - flex-direction: column, foto 180px hoog, border-radius 16px 16px 0 0

- **Prijs**: p.p. → per nacht in kaarten en popups

- **Hero**: min-height: 100svh → 100vh (desktop was te klein)

## Open / volgende sessie

- Google Reviews proxy: functions/api/google-reviews.js geeft 500 → Place ID invullen + GOOGLE_PLACES_API_KEY in Cloudflare dashboard
- lander-google.html is nu stale — alleen hotel-venray.html onderhouden
