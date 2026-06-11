# Session Notes — 2026-06-11 — Feedback pagina

## Wat gedaan

- Feedback pagina gebouwd (NL/EN/DE) via template-systeem
- D1 `feedback` tabel aangemaakt in `asteria-analytics`
- Cloudflare Function `functions/api/feedback.js` (D1 insert + FormSubmit.co email)
- `build.py` uitgebreid: multi-template support (`python3 build.py feedback`)
- TripAdvisor link gefixt naar juiste hotel (g652276-d1726559)
- Google review knop verwijderd (writereview endpoint afgeschaft, geen werkend alternatief)

## Live URLs

- `visit.asteria.nl/feedback` (NL)
- `visit.asteria.nl/feedback-en` (EN)
- `visit.asteria.nl/feedback-de` (DE)

## Wat open

- Google review knop later weer toevoegen als werkende directe-review-URL gevonden
- FormSubmit.co vereist eenmalige bevestiging via email op info@asteria.nl (eerste submit triggert dit)
- Playwright end-to-end test (formulier submit, D1 check) nog niet uitgevoerd
