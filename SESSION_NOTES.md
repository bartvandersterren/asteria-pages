# Session Notes — 2026-05-25

## Gedaan
- Dashboard redesign: `admin/dashboard.html` volledig gestyled (Stripe/Vercel look)
  - Inter font, #f8fafc achtergrond, 1080px max-width
  - Witte topbar met rode linkerborder + subtitle
  - KPI kaarten: 32px font, gekleurde topborder (ads=blauw, ga4=paars)
  - Section headers met horizontale lijn
  - Funnel: genummerde stap-cirkels, 10px bars
  - Campagne tabel: rechtsuitlijning, blauwe hover
  - A/B kaarten: 4px border, 24px metrics, Hoogste CVR badge
  - Skeleton loading animatie + rode error pill
- Mobile fix: 2-koloms KPI grid op ≤640px, kleinere fonts, funnel kolom verborgen

## Commits
- `3dfa543` feat: redesign analytics dashboard
- `ca614c1` fix: responsive KPI grid and layout for mobile

## Open
- Google Reviews API key nog steeds niet geconfigureerd in CF Pages dashboard
