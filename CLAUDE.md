# Asteria Pages — Claude Instructies

Dit is de repository voor landingspagina's op visit.asteria.nl.

## Pagina's bouwen

Gebruik altijd de `asteria-lander` skill bij het bouwen van een nieuwe landingspagina. Die skill bevat het volledige 8-stappen proces inclusief verplichte design brief (Stap 0).

Beschikbare kennisdocumenten — altijd raadplegen bij een pagina-sessie:
- `hotel-content.md` — kamers, arrangementen, prijzen, reviews, contact
- `foto-index.md` — fotoselectie per use case (verwijst naar lokale fotobank)
- `tone-of-voice.md` — stemgeluid en schrijfstijl
- `cro-guidelines.md` — conversie-optimalisatie richtlijnen
- `brand.css` — design tokens (kleuren, typografie, spacing)

## Technische context

- **Repo:** github.com/bartvandersterren/asteria-pages
- **Lokale clone:** ~/Projects/asteria-pages/ — dit is de enige werkdirectory
- **Hosting:** Cloudflare Pages → auto-deploy op push naar `main`
- **Subdomain:** visit.asteria.nl (CNAME → asteria-pages.pages.dev)
- **Brand:** `brand.css` in root van deze repo
- **Logo:** https://www.asteria.nl/images/logo-hotel-asteria.png (90×104px)
- **Primaire kleur:** `#c23435`
- **Fonts:** Electrolize (headings) + Montserrat 300/400/700 (body)

## Git workflow

- GitHub token (bartvandersterren): zie ~/.claude/projects/.../memory/reference_github_token.md
- Push naar main → Cloudflare deployt automatisch (geen extra stap)
- git config: user.email = bart@vandersterrenhotels.nl, user.name = Bart van der Sterren

## Booking engine

- Bestanden: boeken.html, boeken-stap1-3.html
- Backend: functions/mews/[[path]].js (Mews proxy) + functions/api/session.js (KV session)
- KV binding: ASTERIA_KV (gekoppeld aan Cloudflare Pages, namespace_id: 0b06387ff7724995b0e287df3f0c5cb0)
- Session injecteren: POST https://visit.asteria.nl/api/session met {"session":"<token>","client":"Mews Distributor 5656.0.0"}
- Mews IDs: configId 9fc01bd9-bc04-49f2-83cf-b44400835224 | enterpriseId 65a522c9-4828-413d-9ad8-af1d00ffb83f

## Foto's

- fotos/ in repo = geselecteerde foto's (semantisch benoemd, ~17 stuks)
- ~/Documents/Asteria Fotobank/ = volledig archief (318MB, 800 foto's) — niet in git
