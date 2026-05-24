# Session Notes — 2026-05-24

## Gedaan
- Analytics no-track opt-out toegevoegd aan alle pagina's (hotel-venray, lander-google, wellness-arr-c + template + vertaalversies)
  - Check: `if (localStorage.getItem('asteria_no_track')) return;` in track() functie
  - Instellen op apparaat: `localStorage.setItem('asteria_no_track', '1')` in browser console op visit.asteria.nl
- Stats opgehaald: 63 page_views, 31 popup_opens (50%), 24 mews_clicks (38%), 1 email signup
  - Email signup: 23 mei 19:07, /hotel-venray, variant B, via Google

## Volgende sessie
- Mobiel analytics dashboard bouwen
  - Bestaand bestand: admin/stats.html (inhoud onbekend — lezen vóór bouwen)
  - Tonen: funnel (page_view → popup_open → mews_click + %), variant A/B breakdown, recente email signups
  - Brand: #c23435, Electrolize + Montserrat, achtergrond #f0efed
  - Route: /admin/stats — beschermd via Cloudflare Access
