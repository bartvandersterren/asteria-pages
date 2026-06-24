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
- `design-dna.md` — visuele stijl, anti-patronen, referenties (lezen vóór bouwen)

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

## Mews Booking Engine API (2026-06-23 — getest en werkend)

- **Client:** `"Client": "Asteria Booking 1.0.0"` — geregistreerd bij Mews, geen API key nodig
- **Base URL:** `https://api.mews.com/api/distributor/v1/...`
- **Mews IDs:** configId **6dc9094c-76e3-4fd8-83a7-af1d00ffc556** | enterpriseId/HotelId `65a522c9-4828-413d-9ad8-af1d00ffb83f` | serviceId `755424cc-3077-4320-b069-af1d00ffbe47`
- **Oude ID** bee2f902-... — nooit gebruiken
- **Wellness voucher code:** **2026WELLNESS** (niet WELLNESS)

### Geteste endpoints:
- `/configuration/get` — hotel + kamers + rates (ConfigurationIds + PrimaryId)
- `/hotels/getAvailability` — prijzen per rate/kamer (HotelId + datums + occupancy)
- `/hotels/getPaymentConfiguration` — payment gateway info
- `/reservations/getPricing` — prijsberekening voor specifieke selectie
- `/reservationGroups/create` — reservering aanmaken (Customer + Reservations + optioneel CreditCardData)
- `/vouchers/validate` — vouchercode checken (nog niet getest)

### Pricing:
- Geen custom prijzen via API — altijd bepaald door Mews via RateId + VoucherCode
- Special offers: via Rates/VoucherCodes in Mews Operations instellen

### Payments:
- **PCI Proxy merchantId:** `3000013748` (= PaymentGateway.PublicKey)
- **Creditcard:** eigen design via PCI Proxy Secure Fields SDK (`pay.datatrans.com/.../secure-fields-2.0.0.min.js`), `initTokenize(merchantId, fields)`, token als `CreditCardData.PaymentGatewayData`
- **iDEAL/Google Pay/Apple Pay:** alleen via Mews hosted betaalpagina (redirect naar `app.mews.com/navigator/payment-requests/detail/{PaymentRequestId}?returnUrl={base64}`)
- **Non-refundable rates** geven `PaymentRequestId` terug, flexibele rates niet
- **Prototype:** `payment-test.html` — werkend bewijs creditcard + iDEAL flow

### Legacy (niet meer nodig):
- `functions/mews/[[path]].js` (proxy met gespoofde headers) — vervangen door directe API calls
- `functions/api/session.js` (KV session hijack) — niet meer nodig
- Deeplinks: `mewsRoute=rates&mewsRoom=<categoryId>` — nog in gebruik op bestaande pagina's

## Booking engine bestanden

- `boeken.html` — multi-step booking flow (nog op oude proxy, moet omgebouwd)
- `boeken-stap1/2/3.html` — verouderd
- `payment-test.html` — payment prototype (hardcoded testdata, niet voor productie)

## Foto's

- fotos/ in repo = geselecteerde WebP foto's (semantisch benoemd, 23 stuks, quality=72)
- ~/Documents/Asteria Fotobank/ = volledig archief (318MB, 399 originelen) — niet in git

## Testing & Playwright

- Mobile testen: gebruik `browser_run_code_unsafe` met `page.setViewportSize({ width: 375, height: 812 })` — `browser_resize` werkt niet (type coercion bug)
- Na `git push` ~35 seconden wachten vóór live URL testen (Cloudflare deploy tijd)
- Screenshot workflow: `browser_run_code_unsafe` voor viewport + navigate + scroll, dan `browser_take_screenshot`

## Cloudflare Functions

- Google Reviews proxy: `functions/api/google-reviews.js` — vereist `GOOGLE_PLACES_API_KEY` env var in Cloudflare Pages dashboard
- Place ID opzoeken: `curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Hotel+Asteria+Venray&inputtype=textquery&fields=place_id&key=JOUW_KEY"`
- Place ID staat als placeholder in google-reviews.js regel 9 — nog invullen

## Mobile layout gotcha

- Op mobile heeft `body { background: #f0efed }` — secties ná de arr-c kaart (margin: 16px) krijgen 16px gap in body-kleur. Houd hier rekening mee bij nieuwe blokken.

## Analytics (D1)

- **Database:** `asteria-analytics` (D1, `d993796f-f35c-4997-8ead-ec368a1f0956`, regio WEUR)
- **Binding:** `ASTERIA_D1` (gekoppeld aan production + preview via CF API)
- **Events:** `page_view`, `cta_click`, `popup_open`, `step2_reached`, `mews_click`, `email_submit`, `email_success`
- **Stats:** `curl https://visit.asteria.nl/api/stats?summary=1`
- **D1 CLI gotcha:** gebruik altijd `--remote` flag bij `wrangler d1 execute`, anders zoekt wrangler naar een lokale wrangler.toml binding
- **Binding toevoegen via API:** `PATCH /accounts/{id}/pages/projects/asteria-pages` met `deployment_configs.production/preview.d1_databases`

## Actieve campaign pagina's

- `wellness-arrangement.html` → `visit.asteria.nl/wellness-arrangement` — wellness arrangement lander (3 talen via template)
- `hotel-venray.html` → `visit.asteria.nl/hotel-venray` — branded Google Ads lander, meest up-to-date
- `lander-google.html` → `visit.asteria.nl/lander-google` — actieve PMax campaign final URL (onderhoud nodig)
- Beide hebben Mews inline widget + Google Ads + GA4 tracking
- `hotel-venray.html` en `lander-google.html` zijn bijna identiek — wijzigingen vaak in beide nodig
- `feedback.html` → `visit.asteria.nl/feedback` — feedback pagina (3 talen via template), D1 opslag + FormSubmit email

## Google Ads & GA4 tracking

- **GA4 property:** 262565995 | Measurement ID: `G-DPCP945DCG`
- **Google Ads:** `AW-998609513` | Conversion label: `t8vbCLm6i7IcEOmkltwD` | send_to: `AW-998609513/t8vbCLm6i7IcEOmkltwD`
- **GTM container:** `GTM-PLQ49QN` (actief op asteria.nl, NIET op visit.asteria.nl — gtag.js direct gebruikt)
- **Conversion Linker:** automatisch via `gtag('config', 'AW-...')` — geen aparte GTM tag nodig
- **Cross-domain:** `gtag('config', 'G-DPCP945DCG', { linker: { domains: ['asteria.nl', 'visit.asteria.nl'] } })`
- **GA_ADS_LABEL:** `window.GA_ADS_LABEL` gezet in head, gebruikt door booking IIFE voor conversion events
- Conversion event sturen: `if (typeof gtag === 'function') gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL })`

## Translations workflow (2026-05-20 — live)

- **Bouwen:** `python3 build.py` → bouwt alle templates (wellness + feedback)
- **Selectief:** `python3 build.py feedback` of `python3 build.py wellness nl`
- **Templates:**
  - `wellness-arr-c.template.html` + `translations/{nl,en,de}.json` → wellness-arrangement HTMLs
  - `feedback.template.html` + `translations/feedback-{nl,en,de}.json` → feedback HTMLs
- **Wijziging aanbrengen:** pas JSON aan → `python3 build.py` → commit template + JSONs + HTMLs
- `generate_translations.py` = eenmalig bootstrapscript, niet meer nodig voor dagelijks gebruik
- **GOTCHA `{{KEY}}` in CSS:** gebruik NOOIT template keys als onderdeel van CSS-waarden (bijv. `i{{HTML_LANG}}ine-flex`). Dit breekt op andere talen. Hardcode zulke waarden.
- **Redirects:** `_redirects` in root — oude `/wellness-arr-c` URLs → 301 naar `/wellness-arrangement`

## Foto-index lezen
- `foto-index.md` is te groot voor de Read tool (~60k tokens) — gebruik `Bash head -N foto-index.md` of grep om specifieke secties op te zoeken
