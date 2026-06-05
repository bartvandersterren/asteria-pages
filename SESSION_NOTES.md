# Session Notes — 2026-06-05 (sessie 2)

## Wat gedaan

1. **Vouchercodes A/B test gefixt** — oude codes (WELLNESSARRA / WELLNESS124) vervangen door Mews-codes
   - Variant A (€139,50) → `2026WELLNESS`
   - Variant B (€124,50) → `WELLNESS2026`
   - Availability-fetch gebruikt nu dynamische VOUCHER variabele i.p.v. hardcoded string
2. **Prijslabel p.n. → p.p.p.n.** in alle 3 talen (NL/EN/DE) — ARR_C_PRICE_SUB

## Wat open

- Oude iteratie-bestanden opruimen (`wellness-arrangement-blok.html`, `-blok-b`, `-blok-c`, `-v2`)
- `hotel-venray.html` en `lander-google.html` hebben mogelijk dezelfde p.p./p.n. en logo issues
- Google Reviews API key nog niet geconfigureerd in Cloudflare (500 error)
