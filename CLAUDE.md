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

## Samenwerking

- **Eigenaar:** Bart van der Sterren (@bartvandersterren)
- **Medewerker:** Stijn (@MarketingParkhotel) — write access
- **Branch protection:** `main` is beschermd — directe pushes niet toegestaan voor medewerkers
- **Workflow:** altijd via feature branch + Pull Request naar `main`
- **Deploy:** Cloudflare Pages deployt automatisch bij merge naar `main`

### Eerste keer opzetten (voor Stijn)

```bash
git clone https://github.com/bartvandersterren/asteria-pages.git
cd asteria-pages
```

### Werkwijze voor wijzigingen

```bash
git checkout main && git pull                  # altijd starten vanaf up-to-date main
git checkout -b feature/beschrijving           # nieuwe branch voor je wijziging
# ... wijzigingen maken ...
git add <bestanden> && git commit -m "wat je deed"
git push -u origin feature/beschrijving        # push branch naar GitHub
gh pr create --title "Beschrijving" --base main  # of maak PR via github.com
```

Na review/goedkeuring wordt de PR gemerged → Cloudflare deployt automatisch.

## Git workflow

- Push naar main → Cloudflare deployt automatisch (geen extra stap)
- git config (Bart): user.email = bart@vandersterrenhotels.nl, user.name = Bart van der Sterren

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

- `wellness-arrangement.html` → `visit.asteria.nl/wellness-arrangement` — sinds okt 2026 het arrangementsjabloon (lander-w1, alleen NL, zie Arrangementen op lander-w1); oude NL-lander op `/wellness-arrangement-oud` (noindex), EN/DE ongewijzigd op `-en`/`-de`
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
  - `wellness-arr-c.template.html` + `translations/{nl,en,de}.json` → `wellness-arrangement-oud.html` (NL, noindex via `'noindex': ('nl',)` in build.py) + `wellness-arrangement-en/-de.html`; zelfde voor `najaar.template.html` → `najaarsarrangement-oud.html` + `-en/-de`
  - `feedback.template.html` + `translations/feedback-{nl,en,de}.json` → feedback HTMLs
- **Wijziging aanbrengen:** pas JSON aan → `python3 build.py` → commit template + JSONs + HTMLs
- `generate_translations.py` = eenmalig bootstrapscript, niet meer nodig voor dagelijks gebruik
- **GOTCHA `{{KEY}}` in CSS:** gebruik NOOIT template keys als onderdeel van CSS-waarden (bijv. `i{{HTML_LANG}}ine-flex`). Dit breekt op andere talen. Hardcode zulke waarden.
- **Redirects:** `_redirects` in root — oude `/wellness-arr-c` URLs → 301 naar `/wellness-arrangement`

## Foto-index lezen
- `foto-index.md` is te groot voor de Read tool (~60k tokens) — gebruik `Bash head -N foto-index.md` of grep om specifieke secties op te zoeken

## Flow-landers (lander-w1, okt 2026)

- `lander-w1.template.html` + `lander-w1.css` + `lander-w1.js` = sjabloon voor de flow-landers in de nieuwe asteria.nl-huisstijl
  (structuur W1 Thuiskomst: hero met boekbalk, tegelstrook, ster-split, kamerslider, reviewmuur, FAQ, fotowolk). Eerste pagina:
  `verblijfsverjaardag-v2` (build.py-entry, `translations/verblijfsverjaardag-v2-nl.json`, foto's `fotos/l26-*.webp`). Nieuwe lander
  (bedankt, welkom-terug, gemist) = nieuwe JSON + build.py-entry + eigen l26-foto's. `lander-2026.*` is het oude Parkhotel-model.
- Reviewmuur leest `content/reviews-google-asteria.json` (24 Google-reviews, opgehaald via google.com/travel; Maps-weergave toont voor
  dit profiel geen reviews). Google-profiel cid `10392502528258527703`, place-id `ChIJ8QbzR7lqx0cR19Ey1PyVOZA`.
- Boekbalk: Mews-widget-API `setVoucherCode`, `setStartDate`, `setEndDate`, `setAdultCount` werken (widget opent op stap Datums;
  `showRooms()` slaat die over); URL-fallback `mewsStart`, `mewsEnd`, `mewsAdultCount` op de distributor-URL.
- Kop/voet komen uit de Effecty-staging (asteria.staging.effectytools.com) van sep 2026; de staging is sindsdien veranderd
  (menu-pijltjes, hogere mobiele voet), dus de pixelcheck geeft 4,6 % op 1440.
- Test: `python3 scripts/test_lander_w1.py` (v2) en `python3 scripts/test_lander_w1.py http://localhost:8765/verblijfsverjaardag.html --v3`.
- LIVE sinds 14 okt 2026: build-entry `verblijfsverjaardag-v3` (blok `zijkaart`) schrijft `verblijfsverjaardag.html` = visit.asteria.nl/verblijfsverjaardag
  (link uit de jubileummail). Oude lander-2026-versie bewaard als `verblijfsverjaardag-oud.html`; `/verblijfsverjaardag-v3` 301 in `_redirects`.
  v2 (uitklaptab) blijft als variant op /verblijfsverjaardag-v2. Alles noindex.
- Upgradeblok A · Ladder-slider (14 okt 2026, /bedankt en /gemist; 5 stappen Comfort > Royale > Deluxe > Junior Suite > Suite > Bruidssuite): blok 3a-variant `ladder` in
  `lander-w1.template.html` (`<!--[ladder[-->` / `<!--[!ladder[-->`), staat aan zodra de JSON een `UPGRADE_LADDER` heeft
  (kamers, stappen, winstregels, labels, voet; build.py `render_ladder`) + `UPGRADE_INTRO`. CSS/JS prefix `b3l-`. Andere landers
  ook? = `UPGRADE_LADDER` + `UPGRADE_INTRO` in hun JSON. Test: `... /bedankt.html --v3 --voucher BEDANKT --ladder` (zonder `--ladder`: blok afwezig).
- Cadeaublok (14 okt 2026, /welkom): blok 3a-variant `cadeau` (`<!--[cadeau[-->` / `<!--[!cadeau[-->` om de ster-split),
  aan zodra de JSON `CADEAU_ITEMS` heeft (lijst naam/regel/foto/alt, optioneel badge, standaard Gratis) + `CADEAU_INTRO` + `CADEAU_VOET`;
  build.py `render_cadeau`. Drie kaarten in b3l-kaartstijl (CSS `b3c-`, breedte via `.b3l-wrap`), geen knop. Foto's `fotos/l26-welkom-cadeau-*.webp`.
  Test: `... /welkom.html --v3 --voucher WELKOM --cadeau` (zonder `--cadeau`: blok afwezig).
- LIVE-promotie welkom (14 okt 2026): build-entry `welkom-v2` schrijft `welkom.html` = visit.asteria.nl/welkom; entry `welkom` schrijft
  NL nu naar `welkom-oud.html` (EN/DE ongewijzigd welkom-en/-de, taalkeuze daar wijst naar /welkom = nieuwe pagina); `/welkom-v2` 301 in `_redirects`.
- Ster-split (blok 3a) per JSON: `PUNT_EEN..VIJF_ICOON` (svg-inhoud; TWEE/DRIE/VIJF hebben een standaard in build.py
  `ATTENTIE_ICOON_STANDAARD`) en `ATTENTIE_KNOP` (ontbreekt = tekst van CTA, leeg = geen knop; build-blok `attentie-knop`).
- Vaste feiten (Stijn, 14 okt 2026): Royale en Deluxe 25 m²; badjas te leen; ontbijt ma-vr 07.00-10.00, za-zo 08.00-10.30;
  VERJAARDAG = verblijf rond je verjaardag, verjaardag melden bij het boeken; Google-reviews 2.280 (hero-badge mag "2.200+").
- Algemene hotellander `hotel-venray-v2` (3 nov 2026, preview, tegenhanger van parkhotelhorst.nl/hotel-horst-2/ voor Meta/branded Google):
  build-blok `hotel` = geen actiecode (`VOUCHER` leeg; build.py `zonder_voucher` haalt lege mewsVoucherCode/data-voucher/"met code" weg),
  geen tegelstrook, uitklaptab of zijkaart; ster-split = "Een verblijf dat bij je past"; na de kamers drie eigen blokken uit lijsten in
  `translations/hotel-venray-v2-nl.json` (build.py `render_hotel`, stijl `hotel.css`, prefix `ho-`): faciliteiten (mozaiek kiezerblok 6a,
  `_faciliteiten` precies 5, `_fac_extra`), omgeving (`_omgeving` 3-6), arrangementen (`_arrangementen` 3-8, geen prijzen).
  Omgeving (3 nov 2026) = omgevingsblok van de staging-homepage (`.omgeving-list`, CSS uit staging base.css in hotel.css, JS in
  lander-w1.js alleen bij `[data-omg-list]`): fotokaart met label-pil + naam, lijst plekken {naam, afstand, label, img, alt, fac};
  hover/focus (>= 1024) of scrollen (telefoon, foto sticky onder de kop van 60 px) kiest de plek. Bekijk = faciliteit-pop-up
  (`_facdata` sleutels `omg-*`, extra velden `route` = Google Maps-link (tekstlink Route plannen, nieuw tabblad), `credit` =
  fotoregel, `alts`); foto's `fotos/l26-omg-*.webp`, Wikimedia-bronnen/licenties in `_bronnen.fotos` van de JSON.
  Herokop op >= 1024 = staging-grootte (`--text-hero`, 129,6 px op 1440), alleen hotel-venray-v2 (hotel.css, niet `.b1a--sub`).
  Extra tag `gtag('set','linker',{accept_incoming:true})` zoals hotel-venray.html. Test: `... /hotel-venray-v2.html --hotel`.
- Kamertypes in de nieuwe stijl `kamertypes-v2` (3 nov 2026, preview op PR #179; live /kamertypes = oude build_kamers.py tot akkoord):
  lander-w1 met blokken `hotel` + `kamertypes` (build.py `render_kamertypes`, `kamertypes-v2.css`/`.js`, prefix `kt-`), nabouw van
  staging /kamers/: subhero (`.b1a--sub`, 480/300 px, boekbalk ook op de telefoon, geen boekkaart), Kies je kamer (filterchips
  `_filters` + kaarten `_kamers`: 3 foto's met crossfade/pijlen/bolletjes, specs, knop Boek deze kamer = Mews met data-room uit
  `KAMER_MEWS`; geen prijzen, geen Junior Suite, geen knop naar de kamerpagina's; contactkaart vult de laatste rij), Wat in elke
  kamer klaarstaat (`_inbegrepen`), arrangementen (ho-arr), reviewmuur (`_reviews_voorkeur`), Goed om te weten (`_goed_om_te_weten`),
  FAQ (`_faq`, 4-8), fotowolk. Ster-split, kamerslider, faciliteiten, omgeving en kamer-pop-up staan uit (`<!--[!kamertypes[-->`).
  Gesloten: logo naar `GESLOTEN_LOGO_URL` (standaard /hotel-venray-v2). Herofoto `fotos/l26-kamertypes-hero.webp` (P1081257).
- Optionele herovideo op lander-w1 (blok `video`, aan met `HERO_VIDEO` in de JSON; `HERO_VIDEO_MOBIEL` = staande bron < 720 px via
  `<source media>`, `HERO_VIDEO_POSTER`; terugval HERO_VIDEO/HERO_IMG). Video van de staging-homepage op staging-kwaliteit:
  `videos/hero-asteria-building-sunset.mp4` = staging-origineel 1:1 (1280x720, stream copy + faststart, zonder audio), ook op de
  telefoon (zelfde uitsnede 50% 50% als de staging; de staande -mobiel.mp4 is vervallen), poster `fotos/hero-asteria-building-sunset.webp` = frame 0, 1280x720, webp 90.
  Reduced motion = alleen HERO_IMG (lander-w1.css `.b1a-video`).
- Trustkaart (blok `trustkaart`, aan met lege `KAART_IMG` in de JSON): boekkaart onder de hero (telefoon) en zijkaart zonder foto,
  pil, titel en Google-scorevak (de score staat al in de herobadge); begint met de vinkjes (`.b1k-kaart--trust`). Alleen hotel-venray-v2.
- Staging-boekkaart op de telefoon (blok `boekkaart`, aan met blok `hotel`): vervangt op hotel-venray-v2 de boekkaart onder de hero door
  de kaart van de staging-homepage (.booking-bar--stacked: Aankomst en vertrek / Reisgezelschap / Type kamer + Bekijk beschikbaarheid,
  24 px over de hero van 490 px, kop 44 px; CSS `hb-` in hotel.css). Velden = form[data-boekbalk] van lander-w1.js; nieuw daar
  (alleen actief als de elementen bestaan): `[data-periode]` (één regel met aankomst en vertrek, linker/rechter helft = twee native
  datumvelden) en `[data-rol="kamer"]` (kamertype -> mewsRoom/mewsRoute=rooms en showRates). Trust-vinkjes als compacte rij eronder.
- Scratchcard-pop-up op lander-w1 (blok `scratchcard`, aan met `"_popup_scratchcard": true` in de JSON; nu alleen hotel-venray-v2):
  zet `window.ScratchcardConfig = {stijl:'2026'}` en laadt `scratchcard-2026.css`, `analytics-d1.js` (window.track, zelfde D1-events
  als hotel-venray.html), `nieuwsbrief.js` (backend klaviyo) en `scratchcard-popup.js`. Stijl 2026 = overlay `data-stijl="2026"`,
  kraslaag zand/goud, logo uit de kop, focus-trap, vaste trigger (desktop exit-intent; telefoon 45% scroll of 20 s), onderbalk weg
  zolang hij open is. Zonder config gedraagt `scratchcard-popup.js` zich als voorheen; sitebreed blijft `popup-ab.js` uit (POPUP_UIT).
  Aanmelding: `/api/nieuwsbrief` (taal nl -> Klaviyo-lijst `WfwqBR`, bron scratchcard). Test: `scripts/test_scratchcard_2026.py`
  (gemockte API) + `node --test scripts/test_nieuwsbrief_lijst.mjs`.
- Gesloten lander (blok `gesloten`, `"GESLOTEN_LANDER": true` in de JSON; nu hotel-venray-v2, besluit Stijn 3 nov 2026: zolang
  de nieuwe asteria.nl niet live is geen links naar asteria.nl): kop alleen logo (-> /hotel-venray-v2), telefoon en Boek nu
  (`.top-stack--gesloten`), voet alleen logo, adres, telefoon, mail en privacy/voorwaarden in nieuw tabblad (`.footer--gesloten`);
  faciliteit-pop-up knop = Bekijk beschikbaarheid (Mews, `data-boek`, lander-w1.js zet dan geen asteria-link), geen Alle
  faciliteiten/Ontdek de omgeving/Alle arrangementen/Neem contact op/Bekijk alle kamers, omgevingsregels zonder asteria-link;
  kamerknoppen (kaart + pop-up) = Bekijk beschikbaarheid (Mews met data-room), geen link naar de kamerpagina's (oude stijl).
  Overzichtsknoppen naar de nieuwe-stijlpagina's via JSON: `OVERZICHT_ARR_URL` (nu /arrangementen-v2, PR #180) en
  `OVERZICHT_KAMERS_URL` (nu leeg = geen knop; later bv. /kamertypes-v2, tak feature/kamers-v2). Leeg veld = geen knop.
- Faciliteit-pop-up met video: `_fac_video` {sleutel: pad} in de JSON (hotel-venray-v2: wellness -> videos/wellness-walk-pop.mp4,
  fitness -> videos/gym-pop.mp4, lichte H.264-varianten 960 px zonder audio); lander-w1.js vulFac maakt het `<video>` pas aan als er
  een video is (HTML van andere pagina's gelijk), poster = eerste foto, reduced motion = foto. Volledig menu terug = `GESLOTEN_LANDER` op false en opnieuw bouwen. Test `--hotel` controleert de hrefs.
- Spiegelstand (3 nov 2026, hotel-venray-v2): `"GESLOTEN_LANDER": "spiegel"` = inhoud als de gesloten lander (blok `gesloten`:
  kamerknoppen en faciliteit-pop-upknop = Bekijk beschikbaarheid), maar kop (utility-balk met Contact, menu met submenu's Hotel en
  Over ons, hamburger + drawer) en voet (Verblijf/Bij ons/Contact, socials) volledig zoals de staging (blok `spiegel`; de gesloten kop/voet
  heet nu blok `kopdicht` en staat alleen aan bij `true`). Alle menu-/voetlinks staan in het sjabloon als `href="spiegel:<sleutel>"`
  en komen uit `translations/spiegel-links.json` (build.py `vul_spiegel_links`; stopt bij een onbekende sleutel of een asteria.nl-link
  behalve privacy/voorwaarden). `OVERZICHT_ARR_URL`/`OVERZICHT_KAMERS_URL` = `spiegel:arrangementen`/`spiegel:kamers`; extra knoppen
  Alle faciliteiten, Plan een dag in de buurt, Neem contact op; faciliteit-pop-ups krijgen `info` (lander-w1.js: tekstlink Meer
  informatie naast Bekijk beschikbaarheid). Geen Zalen & feesten, FAQ, Werken bij of taalkeuze. `true` = weer gesloten, `false` = oude
  volledige kop met asteria.nl-links.

### Spiegel van de Effecty-staging (3 nov 2026, tak feature/staging-spiegel)

- `python3 scripts/staging_spiegel.py` haalt de NL-pagina's van asteria.staging.effectytools.com op (statische HTML, gewone requests
  volstaan) en schrijft ze als `home-nieuw.html` (/home-nieuw, niet gelinkt), `kamers.html`, `kamers/comfort-kamer.html`,
  `kamers/deluxe-kamer.html`, `faciliteiten.html`, `wellness.html`, `restaurant.html`, `omgeving.html`, `over-ons.html`, `contact.html`.
  Niet met de hand bewerken: opnieuw draaien ververst alles. Niet gespiegeld: /arrangementen/ (eigen /arrangementen-v2, PR #180),
  /vergaderen/ en alles van Zalen & feesten (besluit Stijn), /bookingEngine/ (= Mews), EN/DE.
- Assets in `nieuw-assets/` (staging /assets/x -> /nieuw-assets/x, ?v= weg, byte-gelijke fonts uit fonts/ hergebruikt, ongebruikte
  bestanden worden opgeruimd). `page-interactions.js` krijgt alleen MEWS_ENTRY = Mews-distributor.
- Linkset `translations/spiegel-links.json`: `paginas` (sleutel = data-link van de staging -> adres), `arrangementenoverzicht`,
  `arrangementen` (trefwoord in knoptekst/kaartkop -> eigen lander-w1-arrangement, anders het overzicht), `weg` (links eruit: menu-item,
  voetlink, knop of tegel; in lopende tekst blijft de tekst), `spiegel` (staging-pad -> bestand + sleutel). Naar de echte asteria.nl =
  adressen in `paginas` vervangen en spiegel + hotel-venray-v2 opnieuw bouwen.
- Boeken: /bookingEngine/, #boeking (kop, drawer, voet) en niet-gebouwde kamerdetails -> `data-mews-open` + Mews-URL (kamer via
  `data-room`); `spiegel.js` (eigen, niet gespiegeld) opent in de capture-fase de Mews-widget met datums/volwassenen/kamertype van de
  staging-boekkaart (`window.__asteriaBooking`), terugval na 4 s de distributor-URL; conversie GA4 purchase + Ads zoals lander-w1.js.
  Formulieren: nieuwsbrief (voet + blok) -> `/api/nieuwsbrief` (Klaviyo, bron pagina); contactformulier -> mailto info@asteria.nl met
  de velden. Plus GA4/Ads-tags en cookiemelding zoals hotel-venray-v2 (`spiegel.css`). Alles noindex, follow, canonical/og:url op het
  eigen adres, niet in sitemap.xml.
- Kamerprijzen (3 nov 2026): `staging_spiegel.py markeer_prijzen` geeft elk prijselement (`.suite-price`, `.overhangkaart__prijs`,
  `.boekbalk__prijs`; op /home-nieuw de suitekaarten) `data-kamer-vanaf="<sleutel>"` (kaartkop, data-room of de kamer van de pagina)
  en het bedrag `data-kamer-vanaf-bedrag` (verborgen plaatshouder "€ …"); `spiegel.css` verbergt het (visibility, ruimte blijft),
  `spiegel.js` vult "€ X" uit `/api/kamer-vanaf`; geen prijs/fout = blijft verborgen. API `functions/api/kamer-vanaf.js` + kern
  `kamer-vanaf-kern.js`: per dag één getAvailability (1 nacht, geen AdultCount, CurrencyCode EUR verplicht: zonder is het antwoord
  22 MB -> Worker-fout 1102), laagste Total over de publieke niet-OTA-tarieven bij 2 volwassenen (Comfort 3-persoons 3), komende
  56 dagen, euro = ceil(cent/100) = hele kamer per nacht. Venster in 7 delen van 8 dagen via de eigen URL (`?deel=1..7`, na elkaar),
  edge-cache 3 u (5 min onvolledig), `?vers=1`. Koud ~30 s, daarna uit de cache. Laagste prijs viel op 3 nov 2026 steeds op een
  zondag (tarief "Kamer zonder ontbijt (terugbetaling niet mogelijk)"). Tests: `node --test scripts/test_kamer_vanaf.mjs`;
  `test_staging_spiegel.py` mockt de API (`--alleen-prijzen` alleen de prijschecks, `--prijzen-echt` ook de echte API).
- /arrangementen-v2 (zelfde tak): `"_kop_spiegel": true` in `translations/arrangementen-nl.json` = build.py `w1_blokken(spiegel)` knipt
  kop en voet in de spiegelstand (blokken gesloten + spiegel, `vul_spiegel_links`) en `spiegel_inhoud` zet inhoudslinks naar
  asteria.nl-kamers/wellness/restaurant/omgeving/contact en de kamerpagina's in `#lp-kamerdata` (Comfort/Deluxe -> spiegel, rest
  /kamers) om. Feestdagkaarten (Kerst, Oud & Nieuw) blijven naar www.asteria.nl/arrangementen/... Zonder de vlag is de uitvoer gelijk aan main.
- Test: `python3 -m http.server 8781 --directory .` + `python3 scripts/test_staging_spiegel.py [--basis URL] [--schermafdruk map]
  [--zonder-staging]` (ook /arrangementen-v2: 404's, console, overloop, allowlist, menu, drawer, Mews; geen pixelvergelijking) (pixelverschil staging/spiegel op 390 en 1440, 404's, consolefouten, overloop, kop/tags, link-allowlist, menu,
  drawer, Mews-stub, nieuwsbrief-mock, contact-mailto). Op een preview (`--basis https://...pages.dev`) de nette adressen.

### Arrangementen op lander-w1 (arrangementsjabloon, okt 2026)

- Zelfde sjabloon als de flow-landers, met build-blokken `zijkaart` + `arrangement`. Eerste pagina: `najaarsarrangement`
  (`translations/najaarsarrangement-nl.json`, voucher NAJAAR2D, foto's `fotos/l26-najaar-*.webp`).
- **LIVE sinds 14 okt 2026 (PR #162)** op de nette adressen, alle zes noindex, follow, niet in sitemap.xml, canonical/og:url op het
  nette adres; build-entry = slug = `translations/<slug>-nl.json` -> `<slug>.html`:
  `/najaarsarrangement` (NAJAAR2D), `/wellness-arrangement` (WELLNESS2026), `/oorlogsmuseum-arrangement` (OORLOGSMUSEUM),
  `/limburg-arrangement` (LIMBURG), `/weekend-aanbieding` (WEEKEND, zonder zondagblok), `/golfarrangement` (GOLF).
  Oude NL-pagina's: `/najaarsarrangement-oud` (najaar.template.html, oude config bee2f902) en `/wellness-arrangement-oud`
  (wellness-arr-c.template.html), beide noindex; hun EN/DE (`-en`/`-de`) zijn ongewijzigd. De preview-adressen
  `/najaarsarrangement-v2`, `/wellness-arrangement-v3`, `/oorlogsmuseum-arrangement-v2`, `/limburg-arrangement-v2`,
  `/weekend-aanbieding-v2`, `/golfarrangement-v2` sturen met een 301 door (`_redirects`); de HTML-bestanden zijn weg.
  `/wellness-arrangement-v2` is een losse oude pagina (geen build-entry) en blijft staan.
  `_andere` (Ook interessant) linkt naar elkaars visit.asteria.nl-adres; kerst blijft naar asteria.nl.
- **Opbouw (wireframe-ideaal 14 okt 2026, bron `~/Documents/Parkhotel /Website ontwerp/asteria-arrangement-blokkenkiezer/bron/wireframe-ideaal.html`):**
  1 hero + boekbalk met prijs-pil en chips, zijkaart (sticky, zonder foto) naast 2-5 die stopt na de kamers, 2 dit is inbegrepen
  (ronde 2, 14 okt: gespiegeld Parkhotel-blok 'Het wellnessarrangement' van /wellness/: ivoren paneel vanaf de linker schermrand,
  rechts een staande fotoslider die 47 px boven het paneel uitsteekt, bolletjes + pijlen; vinkjes in 2 kolommen vanaf 1440 (1280-1439: een kolom, foto 260 breed),
  vanaf-prijs, knop + tekstlink asteria.nl/arrangementen; telefoon: paneel, daaronder de slider van 290 hoog; tijdenregel met hairline in het paneel onder de vinkjes; 14 okt: paneel loopt 61 px
  onder de foto door zoals zd-alles, inhoud 56 px boven/onder, `display:flow-root` op het blok tegen margin-collapse),
  3 zondagvoordeel (variant a9 zoals Parkhotel, zie onder), 4 waarom Asteria (vaste inhoud; draaiend wiel zoals de staging-homepage:
  4 klonen voor en na, autoplay 2400 ms alleen in beeld, pijlen omhoog/omlaag pauzeren 6 s, foto wisselt mee met crossfade,
  foto's `fotos/l26-waarom-<punt>.webp` met data-foto/data-pos in het sjabloon; geen autoplay bij reduced motion),
  5 kamers, 6 reviewmuur, 7 FAQ + contactkaart, 8 ook interessant, 9 fotowolk. Geen tegelstrook
  (b2a) en geen attentie-ster-split. Telefoon: boekkaart onder de hero (prijs, zondagregel, knop, codenoot), daarna de onderbalk.
  Stijl in `arrangement.css` (prefix `ar-`), script `arrangement.js` (zijkaart bij het kamerraster, fotoslider, zondagopties,
  wiel); beide alleen via het blok
  `arrangement` geladen, dus flow-landers raken ze niet. Eén reviewgetal: `{{REVIEWS_AANTAL}}` = `aantal` uit
  `content/reviews-google-asteria.json` (badge, zijkaart, reviewkop).
- **Nieuw arrangement toevoegen:** kopieer `translations/najaarsarrangement-nl.json` naar `translations/<slug>-nl.json`,
  pas teksten/foto's/VOUCHER/CANONICAL_URL aan, zet de slug in de arrangement-lijst in build.py en draai `python3 build.py <slug>`.
  Velden:
  - Hero: `ARR_PRIJS_PIL`, `_chips` (lijst van 3 korte teksten). `BOEKBALK_NOOT` = regel onder de boekbalk (bijv. aankomstdagen).
  - `ARR_NACHTEN` (getal, standaard 1): vast aantal nachten (Limburg 3, Weekend 2). Build zet `data-nachten` op beide
    `form[data-boekbalk]`; `arrangement.js` zet het vertrek op aankomst + N bij elke aankomstkeuze, corrigeert een te kort
    vertrek en zet het vlak voor verzenden nog eens (capture-listener vóór de submit van lander-w1.js), zodat widget
    (setStartDate/setEndDate) en URL-fallback (mewsStart/mewsEnd) N nachten krijgen. Sinds de prijskalender (zie onder)
    openen alle boekknoppen eerst de kalender; die dwingt N nachten en de aankomstdagen (`ARR_AANKOMSTDAGEN`) af. Noem de
    aankomstdag ook in `BOEKBALK_NOOT`.
  - Actiecodeveld in de boekbalk: `arrangement.js` maakt het zo breed als de code (codes tot ±14 tekens passen op 1280/1440).
  - Zijkaart/telefoonkaart: `KAART_KOP`, `ARR_PRIJS`, `ARR_PRIJS_KAART_EENHEID` ("p.p. per nacht"), `ARR_VOORWAARDEN`
    (annuleren alleen noemen als het vaststaat), `KAART_VINK_A..D`, `KAART_KNOP`, `KAART_TRUST`, `ARR_MOB_NOOT`.
  - Inbegrepen: `INB_KOP_A/EM`, `ARR_INB_INTRO` (een of twee zinnen), `_inbegrepen` (lijst `{titel, regel, icoon}`; icoon =
    svg-paden, in een zandvakje; 4 tot 8 punten), `_inbegrepen_fotos` (lijst `{img, alt, pos}`, 4 tot 6, anders stopt de build;
    `pos` = object-position, want de foto is staand op het bureaublad en liggend op de telefoon), `_tijden` (lijst `{tekst, icoon}`
    voor de tijdenstrook). Prijs en knop komen uit `ARR_PRIJS`, `ARR_PRIJS_KAART_EENHEID`, `CTA`.
  - Golfbanen (optioneel, alleen golf): `_banen` (lijst `{naam, plaats, tekst, rijtijd, url, foto, alt, pos?, link?}`, 1 tot 4) +
    `BANEN_KOP_A/EM`, `BANEN_INTRO` zet build-blok `banen` aan: kaart per baan (foto, naam, plaats · rijtijd, tekst, link in nieuw
    tabblad) direct na Dit is inbegrepen, voor het zondagblok. Opzet van het Parkhotel-blok 'Kies uw golfbaan'; CSS `ar-banen`/`ar-baan`
    in `arrangement.css` (2 naast elkaar vanaf 640 px kolombreedte, anders veegrij). Foto's `fotos/l26-golfarrangement-baan-*.webp`.
  - Zondagvoordeel: `ZV_TOON` (true/false; uit bij kerst en oud en nieuw), `ZV_KOP_A/EM/B`, `ZV_PIL`, `ZV_ZONDAG_KOP`,
    `ZV_ZONDAG_PRIJS`, `ZV_GEWOON_PRIJS`, `ZV_ZONDAG_REGEL`, `ZV_ANDERS_KOP`, `ZV_ANDERS_REGEL`, `ZV_VOETNOOT`,
    `ZV_KAART_REGEL` (zondagregel in de zijkaart), gekozen vorm (14 okt): a9, zoals het Parkhotel-blok zondagvoordeel: ivoren paneel met kop, twee kaarten erin (zondag met terracotta rand en pil op de titelregel, gewone kaart kleiner/grijs), voetnoot in het paneel. Geen `?zv`-opties meer. Bedragen meten via Mews getAvailability (2 volwassenen, voucher, zondag- en
    doordeweekse aankomst); zit de korting niet in Mews, dan gewone prijs - EUR 10 p.p. en een regel in `_controleren`.
  - Waarom Asteria: `WAAROM_TOON` (standaard true); inhoud staat vast in het sjabloon.
  - Kamers: `_kamers` = welke kamers, volgorde, pil en prijsregel:
    `{"deluxe": {"pil": "Inbegrepen", "soort": "inbegrepen", "prijs_label": "vanaf", "prijs": "€ 128,50 p.p."},
      "suite": {"pil": "Upgrade", "soort": "upgrade", "prijs": "Upgrade mogelijk"}}` (soort `inbegrepen` = terracotta rand,
    `upgrade` of `toeslag`). Vanaf 3 kamers de brede slider met lus zoals /bedankt (twee kaarten van 390 px in de zijkaartzone op
    1440, teller en streepjes volgen het aantal); 1 of 2 kamers: raster `.ar-kamers` zonder slider/lus/teller. Plus `KAMER_KOP_*`, `KAMER_SUB`, `KAMER_NOOT`.
  - Reviews: `_reviews_aantal` (8 of 12, anders stopt de build), `_reviews_voorkeur` (woorden; reviews die er een noemen eerst).
  - FAQ: `_faq` (lijst `{q, a}`, 4 tot 8 vragen, eerste staat open; `"zondag": true` = alleen met ZV_TOON). Geen herhaling van de tijdenstrook.
  - Ook interessant: `ANDERE_TOON` + `_andere` (lijst `{naam, url, img, alt, prijs?}`; prijs alleen als hij bekend is, url met
    curl op 200 checken).
  - Fotowolk: `_fotowolk` (optioneel, precies 12 items `{img, pos?}` of een pad) vervangt in volgorde de 12 vaste foto's van
    blok 7a; `SLOT_FOTO_A/B` blijven. Volgorde/formaten: tall, tall, vierkant x3, staand 1:2 x3, vierkant x2, tall, tall;
    op de telefoon zichtbaar: 1, 4, 9, 11, 12 (+ SLOT_FOTO_A). Zonder lijst de vaste set (wellness, bar). Limburg en Golf hebben er een.
  - Verder `STICKY_KOP/SUB/KNOP` (onderbalk), `SLOT_*` (fotowolk), `POP_BADGE`, `REVIEW_KOP_*`. Onzekere feiten in
    `_controleren` (lijst; `_`-keys en niet-tekstwaarden gaan niet de {{KEY}}-pass in).
- Blokken in het sjabloon zijn zo geplaatst dat landers zonder blok `arrangement` byte-identiek blijven; controleer na
  sjabloonwijzigingen: alle entries bouwen vóór en na en `cmp` (zo gedaan bij de invoering).
- Test: `python3 scripts/test_lander_w1.py http://localhost:8765/najaarsarrangement.html --v3 --voucher NAJAAR2D --arrangement "€ 128,50" [--schermafdruk qa/najaarsarrangement]`
  (extra: noindex, alle Mews-links op 6dc9094c met de voucher, geen bee2f902, prijs in zijkaart en onderbalk, zondagblok (paneel met kop,
  2 kaarten, pil in de zondagkaart), Waarom Asteria (6 punten + 8 klonen, pijl verandert --active en
  foto), kamerslider met lus bij 3 kamers, inbegrepen-paneel tot de linker schermrand + fotoslider (pijlen, bolletjes), reviewmuur
  8/12, geen b2a, zijkaart met foto, zijkaart loopt mee en stopt na de kamers). Generiek sinds 14 okt: kamers = aantal op de pagina
  (lus met 2n klonen vanaf 3, raster bij 1-2), FAQ 4-8, zondagchecks alleen met zondagblok (zonder: geen blok, geen zondagregel,
  geen zondag-FAQ), actiecode volledig zichtbaar (ook 14 tekens), vertrek = aankomst + data-nachten en widget krijgt N nachten.
  Gotcha: draait er op 8765 al een server uit een andere worktree, start dan een eigen server met `--directory` op een andere poort.
- **Prijskalender "Kies je nachten" (okt 2026, port van de Parkhotel-bouwsteen blok-kalender-prijs):** dialoog `#ar-kal` in het
  arrangement-deel van het sjabloon, `arrangement-kalender.js` + `arrangement-kalender.css` (prefix `ark-`, alleen via blok
  `arrangement`), API `functions/api/arr-kalender.js` (`GET /api/arr-kalender?code=NAJAAR2D&maand=2026-11&deel=1..4[&vers=1]`).
  - Elke `.mews-open` met `data-voucher` = de code (zijkaart, telefoonkaart, inbegrepen, kamers, onderbalk, kop, voet, kamer-pop-up)
    en de datumvelden + knoppen van beide boekbalken openen eerst de kalender (capture op window, vóór lander-w1.js; geen native
    datumkiezer meer). Bureaublad: zwevende kaart van 740 px naast de knop, 2 maanden. Telefoon: bottom sheet (showModal), 1 maand.
  - Cel = EUR ceil(prijs_cent/100/2): p.p. per nacht, bij vaste nachten p.p. voor het hele verblijf. Zondag goud (zand + terracotta
    rand) met de lagere prijs; grijs doorgestreept = niet beschikbaar. Normaal A/B kiezen (vertrekken mag op een grijze dag);
    vaste nachten: één klik = aankomst + N, alleen `aankomst_mag`-dagen (Weekend vr/za).
  - Bevestigen: datums in de hero-boekbalk; zonder kamer `requestSubmit()` (bestaande widgetflow, `window.lpBoekbalk`), met kamer
    (kamerknop) een tijdelijke `.mews-open` met `data-room` en een href met mewsStart/mewsEnd via de Mews-poort van lander-w1.js,
    met `setStartDate/setEndDate` vooraf (`window.arKalender` = log). lander-w1.js/.css blijven ongewijzigd.
  - Instellingen per code: `content/arr-kalender.json`, door build.py (`apply_kalender`) gegenereerd uit de arrangement-JSON's
    (`VOUCHER`, `ARR_NACHTEN`, nieuw optioneel `ARR_AANKOMSTDAGEN` = weekdagnummers 0 = zondag, Weekend `[5, 6]`, `ZV_TOON`,
    standaardkamer = eerste `inbegrepen` uit `_kamers`). Niet met de hand bewerken; meecommitten na een build. Onbekende code = 400.
  - API: per dag één getAvailability (StartUtc = aankomst, EndUtc = + nachten, 2 volwassenen, voucher); per categorie de laagste
    Total over de PRIVÉ-tarieven in het antwoord (`Rates[].IsPrivate`; Mews geeft met een code ook de publieke kamertarieven terug,
    die tellen niet mee). Zondag (`ZV_TOON`): niet lager dan za/ma = korting nog niet in Mews -> gewoon - EUR 20 per kamer,
    `berekend:true`; wel lager = echte Mews-prijs. Cache API 6 u per code/maand/deel (5 min met storingsdagen), concurrency 2,
    3 pogingen, subrequestteller < 45, tijdbudget 25 s; de pop-up vraagt hoogstens 4 delen tegelijk.
  - Test: `python3 scripts/test_arr_kalender.py http://localhost:8765/najaarsarrangement.html [--echt] [--schermafdruk qa/arr-kalender]`
    (mockt /api/arr-kalender; `--echt` tegen `npx wrangler pages dev . --port 8788` of de preview). `test_lander_w1.py` zet de
    kalender in arrangementmodus uit (lege arrangement-kalender.js), zodat de oude Mews-checks blijven gelden.
- **Live vanaf-prijs (nov 2026, PR #179, pas live na merge):** `functions/api/arr-vanaf.js` (`GET /api/arr-vanaf?codes=WELLNESS2026,...`)
  met de kern in `arr-vanaf-kern.js`: laagste echte prijs (berekende zondagkorting telt niet) van de standaardkamer in de komende
  56 dagen, EUR ceil(cent/100/2) zoals de kalendercel (p.p. per nacht, bij vaste nachten p.p. voor het verblijf). Dagprijzen via de
  eigen `/api/arr-kalender` (per maand/deel, na elkaar: parallel gaf 429 van Mews); onbekende code overgeslagen, geen prijs/fout = null.
  Edge-cache 3 uur (5 min als onvolledig), CORS *. Pagina: build.py `markeer_vanaf` zet `data-arr-vanaf="<CODE>"` om het bedrag in
  hero-pil, zij-/telefoonkaart, inbegrepen-regel, onderbalk en Ook-interessant (code via slug); vaste JSON-prijs = terugval;
  `arr-vanaf.js` vervangt alleen het bedrag. Zondagblok en kamerprijzen blijven vast. Flow-landers en hotel-venray-v2 laden het niet.
  Tests: `node --test scripts/test_arr_vanaf.mjs`, `python3 scripts/test_arr_vanaf_pagina.py [--basis URL]` (gemockte API, fout, null).
- Mews: NAJAAR2D geeft op config 6dc9094c alleen een tarief voor de Deluxe kamer (14 okt 2026: EUR 257 voor 2 p.); Suite en
  Bruidssuite staan als "Upgrade mogelijk" tot de meerprijs bekend is. Zondagkorting zit (14 okt) nog niet in Mews: zondag en dinsdag
  geven allebei EUR 257; de pagina toont EUR 118,50 berekend. Tweede nacht met NAJAAR2D: EUR 499,50 voor 2 p. (3-5 nov).

### Arrangementenoverzicht /arrangementen-v2 (nov 2026, preview)

- Opbouw en gedrag van parkhotelhorst.nl/arrangement/ (parkhotel-site `src/fragmenten/pagina-arrangement-v3.html` + css + gedrag),
  uiterlijk = nieuwe huisstijl zoals de arrangementpagina's: tokens, fonts (Abhaya Libre/Montserrat), zand/terracotta, `.btn`, `.vinkjes`,
  `.as-icoon` en `.as-accordeon--kaart` uit lander-w1.css; panelen/vakjes/zondagregel naar het voorbeeld van arrangement.css. Geen eigen
  kleurwaarden; kamer- (4b) en reviewblok (5a) ongemoeid, gelijk aan /najaarsarrangement-v2.
  Bestanden: `arrangementen.template.html`, `arrangementen.css` (prefix `ao-`), `arrangementen.js` (filterchips + keuzehulp, port van
  Parkhotel deel 1 en 2), `translations/arrangementen-nl.json`, build-entry `arrangementen` -> `arrangementen-v2.html`. Alleen NL,
  noindex, niet in sitemap.xml, nergens gelinkt.
- build.py `apply_overzicht()`: kop, kamers (4b), reviews (5a), kamer-pop-up en voet worden bij elke build letterlijk uit
  `lander-w1.template.html` geknipt (zonder actiecode en zonder pil); kaartdata (KAART_KOP, eerste zin van SUB, ARR_PRIJS +
  ARR_PRIJS_KAART_EENHEID, ARR_NACHTEN, HERO_IMG/ALT/--hero-x, KAART_VINK_A..C) uit de arrangement-JSON's in `_arrangementen`
  (slug, url, cat, volgorde, scores, redenen, oms = korte tekst van Stijn). Zondagregel "Op zondag vanaf <b>ZV_ZONDAG_PRIJS</b>" bij ZV_TOON
  (zelfde bron als het zondagblok a9); die kaarten krijgen ook categorie `zondag` (chip Zondagvoordeel), zoals Parkhotel.
  `_extra` = statische kaarten zonder eigen JSON (Kerst, Oud & Nieuw, Oud en Nieuw Bridge, links naar www.asteria.nl/arrangementen/...,
  categorie `feest`, geen zondagkorting); `_volgorde` = volgorde van alle 9 kaarten. Najaar linkt naar /najaarsarrangement. Geen Happy Summer.
- Kaartknoppen linken naar de arrangementpagina (geen directe Mews-boeking): vaste nachten en aankomstdagen dwingt alleen de prijskalender daar af.
- Test: `python3 -m http.server <poort>` + Playwright (desktop 1440, mobiel 390): overflow, 9 kaarten, chips (feest 3, zondag 5), keuzehulp (actief/1 nacht -> golf, feestdagen -> feestkaart,
  vr-za + 2 nachten -> weekend), kamer-pop-up zonder voucher. Promotie naar /arrangementen (indexeerbaar, sitemap, menulink, EN/DE) pas na akkoord Stijn.

### Seizoenslanders /herfst, /lente, /zomer, /winter (rebooking-flow 04), okt 2026

- Eén sjabloon voor alle seizoenen: `seizoen.template.html` + `seizoen.css` (laadt na `lander-w1.css`, blokken met prefix `hf-`)
  + `seizoen.js` (kopie van `lander-w1.js` met `lus()` op `.hf-strook`, onderbalk op `.hf-hero`, `momenten()` voor blok 3a).
  ALLE seizoensinhoud (teksten, foto's, links, arrangement-URL + `ARR_ALLE_URL`, tags, prijzen, fotowolk `WOLK_1..14` met
  `WOLK_n_ALT`) staat in `translations/<seizoen>-nl.json`; in het sjabloon staan alleen structuur, kamers (namen, specs,
  Mews-id's) en iconen. Nieuw seizoen = JSON kopiëren + seizoen toevoegen aan de lijst in build.py + eigen foto's.
- Kiezerkeuze 1c-2d-3a-4a-5c-6i-7b-8b (`~/Documents/Parkhotel /Website ontwerp/asteria-herfst-blokkenkiezer/`); reviewmuur (W1 b5a)
  en fotowolk (W1 b7a) 1:1 uit lander-w1. Geen vouchercode: `mews-open` zonder `data-voucher`, per kamer `data-room`.
- Bouwen: `python3 build.py herfst lente zomer winter` -> `<seizoen>.html`. noindex, niet in sitemap.xml. Let op: de
  marker-check in build.py ziet keys met cijfers (`WOLK_1`) niet; controleer met `grep -o '{{[A-Z_0-9]*}}' *.html`.
- Foto's: `python3 scripts/seizoen_fotos.py <seizoen>` maakt `fotos/hf-*` (herfst), `lt-*` (lente), `zm-*` (zomer),
  `wt-*` (winter) uit Fotobank + repo. Gedeelde foto's (l26-*, wp-sauna-fins, hf-kasteeltuinen, lt-bos, lt-hero-800 als
  inzet zomer, hf-hero-800 als inzet winter) verwijst de JSON direct. Parkhotel-assets als noodoplossing voor uitjes zonder
  Asteria-foto: Maasduinen, Kasteeltuinen, Groote Peel, Venlo, Designer Outlet. Thermaalbad Arcen toont een Asteria-sauna.
- Vanaf-prijzen: `python3 scripts/seizoen_prijzen.py <seizoen> --detail` (vensters in `VENSTERS`: herfst 15 okt-30 nov 2026,
  lente 1 mrt-31 mei 2027, zomer 1 jun-31 aug 2027, winter 1 dec 2026-28 feb 2027; of `--van/--tot JJJJ-MM-DD`). Mews
  Distributor getAvailability per nacht, 2 volwassenen, publieke tarieven zonder OTA, zonder voucher. De API geeft 429 bij
  snelle reeksen: script wacht 1 s per nacht en probeert opnieuw; draai seizoenen na elkaar, niet parallel.
  -> waarden in `PRIJS_*` van de JSON zetten en opnieuw bouwen.
- Test: `python3 -m http.server 8765` + `python3 scripts/test_seizoen.py <seizoen> [--schermafdruk qa/<seizoen>]`
  (Playwright, 1440 en 390, 31 checks). `qa/` staat niet in git.
- Rebooking-mail 04 (asteria-flows) en herfst `ARR_URL` linken naar /najaarsarrangement = sinds 14 okt het nieuwe arrangement. Lente heeft nog geen
  eigen aspergepagina (knop naar asteria.nl/arrangementen); Happy Summer-periode 2027 controleren.

## Seizoensroute /seizoen/ voor de flowmails (16 okt 2026; R2-bron sinds 16 okt avond)

- `functions/seizoen/[[path]].js` (Pages Function) + logica in `seizoen-kern.js` (repo-root, gelijk aan
  `~/projects/parkhotel-site/src/seizoen-kern.js`) laat de flowmails (repo asteria-flows, zie daar `SEIZOEN.md`) één vaste URL
  gebruiken die per periode iets anders teruggeeft:
  - `/seizoen/hero.jpg` (1200x520) en `/seizoen/sfeer.jpg` (496x380): de foto zelf (geen redirect), `Cache-Control: public, max-age=3600`,
    headers `X-Seizoen` (geldende periode), `X-Periode` (periode van de getoonde foto) en `X-Bron: r2|repo`.
  - `/seizoen/lander/` -> 302 naar `/herfst`, `/winter`, `/lente` of `/zomer`; `/seizoen/arrangement/` -> 302 naar het seizoensarrangement
    (herfst `/najaarsarrangement`, zomer `/happy-summer-arrangement`, winter en lente voorlopig `www.asteria.nl/arrangementen`). Beide `no-store`.
  - Onbekend slot of pad: 404. GET en HEAD (HEAD = zelfde headers, lege body), andere methoden 405.
- **Bron = R2, repo = terugval.** `laadKalender()` haalt `https://pub-c740ef36abd24be1aa637f4ee69d7a03.r2.dev/seizoen/asteria/actief.json`
  (env `SEIZOEN_BASIS` overschrijft de basis, alleen voor lokaal testen), bewaart de uitkomst 300 s in de Cache API (eigen sleutel
  `/__seizoen-cache/asteria/actief.json`, ook een 404; `?vers=1` haalt opnieuw op, hoogstens eens per 60 s, via `context.waitUntil`).
  Geldig = JSON met `versie: 1`, `periodes` en `slots`; anders (404, netwerkfout, ongeldige JSON) geldt `seizoen-kalender.json`
  (repo-root, wordt in de Function geïmporteerd; niet in `content/`, dat is gitignored). Het OS (Mediabank › Seizoensfoto's)
  schrijft `actief.json` en de foto's; zolang die er niet is geeft alles `X-Bron: repo`.
- **Schema (versie 1, gelijk aan Parkhotel):** `versie`, `hotel`, `tijdzone`, `bijgewerkt_op?`, `bijgewerkt_door?`,
  `periodes: [{id, naam, van, tot, prioriteit}]` (MM-DD, `tot` inclusief, winter over de jaargrens), `links.lander|arrangement.<periode>`,
  `slots.<slot>: {maat: [b,h], label_nu, mails, fotos.<periode>: {key|pad, bron, landerfoto?, door?, op?}}`. `key` = R2-sleutel
  (foto via `fetch` met `cf.cacheTtl 3600`), `pad` = bestand in deze repo (`context.env.ASSETS`).
  Seizoenen in de bundel: lente 03-01..05-31, zomer 06-01..08-31, herfst 09-01..11-30, winter 12-01..02-29, alle prioriteit 0.
- **Periodekeuze:** hoogste `prioriteit` die de dag bevat wint (bv. feest 12-15..01-01 prio 10); heeft een slot daar geen foto, dan de
  volgende periode die de dag bevat (feest -> winter), daarna de repo-foto. Onbereikbare R2-foto -> ook de repo-foto. Links idem.
- Repo-foto's (terugval, laten staan): `mail/seizoen/<slot>-<seizoen>.jpg` (center-crop, kwaliteit 82, geen EXIF). Winter heeft nog geen
  echt winterbeeld (hero = sauna van de winterlander, sfeer = bospad van de winterlander; `landerfoto: true`).
- Foto ruilen: in OS › Mediabank › Seizoensfoto's (binnen 5 min op de site, mailclients cachen tot 1 uur). Alleen de terugval wijzigen =
  jpg op exact dezelfde maat vervangen en committen op main.
- Overzichtspagina `/seizoen/` (ook `/seizoen`, noindex, `no-store`, header `X-Bron`): bron (R2 met bijgewerkt op/door, of repo met reden),
  de periodes uit de actieve kalender (ook extra periodes, met prioriteit), per slot per periode de foto met "Nu"-kader ("Geen eigen foto:
  toont …" bij terugval), mails, bron, landerfoto-melding en de link-doelen; `?datum=` simuleert.
- Unit-test: `node --test scripts/test_seizoen_kern.mjs` (prioriteit, jaargrens, terugval, `laadKalender` met gefaalde fetch). R2 nabootsen:
  `python3 -m http.server 8796 --directory <map met seizoen/asteria/actief.json + jpg's>` en `wrangler pages dev … --binding SEIZOEN_BASIS=http://127.0.0.1:8796`.
- Testen: `?datum=YYYY-MM-DD` op elke URL, bv. `curl -sI "https://visit.asteria.nl/seizoen/hero.jpg?datum=2026-12-15"` (X-Seizoen: winter).
  Lokaal: `~/projects/parkhotel-site/node_modules/.bin/wrangler pages dev . --compatibility-date=2026-06-01` (zonder datum weigert workerd 4.103 de datum van vandaag).
