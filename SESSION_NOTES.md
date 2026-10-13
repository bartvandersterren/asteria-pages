# Session Notes — 2026-10-13 (avond)

## Gedaan
- Wireframes W1-W5 voor /verblijfsverjaardag (artifact https://claude.ai/artifact/6BW4NDhkPkJWFdA251L8fF); Stijn koos W1 Thuiskomst.
- Blokkenkiezer W1 (artifact https://claude.ai/artifact/QhumV7ep2THkzt9DRbgPS5, bronmap
  `~/Documents/Parkhotel /Website ontwerp/asteria-verblijfsverjaardag-w1-blokkenkiezer/`); keuze **1a-2a-3a-4b-5a-6c-7a**,
  blok 4 op zand, blok 5 = reviewmuur zoals Zaal Zeven v2-feesten (b6d).
- Gebouwd: `lander-w1.template.html`, `lander-w1.css`, `lander-w1.js`, `translations/verblijfsverjaardag-v2-nl.json`,
  `content/reviews-google-asteria.json` (24 Google-reviews, cid 10392502528258527703, place-id ChIJ8QbzR7lqx0cR19Ey1PyVOZA),
  `scripts/test_lander_w1.py` (26 checks), build.py-entry `verblijfsverjaardag-v2`. Plan: `~/.claude/plans/peppy-zooming-kazoo.md`.
- **PR #149** (branch `feature/verblijfsverjaardag-v2`, niet gemerged), preview
  https://feature-verblijfsverjaardag.asteria-pages.pages.dev/verblijfsverjaardag-v2
- Kamerslider loopt tot de schermrand (commit 6c21f34, preview bijgewerkt). Lus (clones + stille reset) is identiek aan de oude lander.
- Boekbalk: Mews-widget `setStartDate/setEndDate/setAdultCount/setVoucherCode` werken; widget opent op stap Datums
  (`showRooms()` zou die stap overslaan); URL-fallback mewsStart/mewsEnd/mewsAdultCount.

## Open
- Akkoord Stijn op de preview → `gh pr merge 149 --merge` → live-check `curl -sI https://visit.asteria.nl/verblijfsverjaardag-v2`
  (200 + noindex). Oude /verblijfsverjaardag blijft staan.
- Hero-badge "2.200+ reviews" (Google telt 2.280); CONTROLEREN-feiten: annuleren 24 u, in-/uitchecktijden, wellnesstijden,
  Royale/Deluxe 26 m².
- Kop/voet wijken 4,6 %/0,6 % van de staging af (staging veranderd sinds lander-2026: menu-pijltjes, hogere mobiele voet);
  bij gelegenheid kop/voet opnieuw uit de staging overnemen voor beide landers.
- Volgende landers op lander-w1: bedankt (BEDANKT, kamerupgrade), welkom-terug (WELKOMTERUG, ontbijt), gemist (GEMIST, upgrade):
  nieuwe JSON + build.py-entry + eigen l26-foto's.

## Volgende sessie: extras-lander Asteria (verzoek Stijn 13 okt, "zelfde structuur als Parkhotel")
- Model: parkhotelhorst.nl/extras/ (LIVE 13 okt 2026, repo `~/projects/parkhotel-site`: `src/fragmenten/pagina-extras-v2.html`,
  `src/paginas/extras/`, memory `project_parkhotel_extras_upsell.md` + `project_parkhotel_extras_wireframes.md`):
  upsell-lander uit de mail met e/k/t-parameters (e-mail, kamer, tijd?), Mews-bestelling van Once-producten
  (count × personen × nachten gotcha), bestel_id, zijkaart/overzicht van gekozen extra's.
- Asteria: Mews-config `6dc9094c-76e3-4fd8-83a7-af1d00ffc556`, enterprise `65a522c9-4828-413d-9ad8-af1d00ffb83f`, service
  `755424cc-3077-4320-b069-af1d00ffbe47` (CLAUDE.md); Asteria-producten/extra's en prijzen nog op te halen (Mews Operations
  of Connector API); kop/voet/tokens uit lander-w1; structuur 1:1 Parkhotel-/extras/ in Asteria-stijl, als
  `/extras-v2`? (bestaat nog niet op visit.asteria.nl, dus `/extras` kan direct, noindex).
- Eerst: Parkhotel-/extras/ lezen (sonnet-verkenner), productlijst Asteria bepalen, dan /plan.
