# Email Capture — Design Spec
_wellness-arr-c.html — 2026-05-20_

## Doel

Nieuwsbriefinschrijvingen verzamelen via een contextuele popup op de wellness arrangement pagina. Het offer: gratis badjas, badhandoek en fles bubbels op de kamer bij het eerste verblijf. Na aanmelding ontvangt de gast een welkomstmail (via Revinate) met een persoonlijke vouchercode (`WELKOM`) voor gebruik bij boeking.

## A/B Test — Trigger

Twee varianten, willekeurig 50/50 toegewezen per sessie (sessionStorage):

| Variant | Trigger |
|---------|---------|
| A | Tijdvertraging: popup na **4 seconden** op de pagina |
| B | **Exit intent** (desktop: muisbeweging richting tabbar) + **70% scroll-depth** (mobile) |

Variant opslaan in `sessionStorage` als `ec_variant` (`"A"` of `"B"`).

## Frequentie

- **Per sessie:** popup maximaal één keer tonen. Flag: `sessionStorage.ec_shown = "1"`.
- **Na conversie:** nooit meer tonen. Flag: `localStorage.ec_converted = "1"`.
- Bij laden: als `ec_converted` in localStorage → nooit registreren, ook geen trigger.

## UI — Twee schermen

### Scherm 1: Email capture

- **Layout:** centered modal, donker backdrop (rgba zwart), foto als achtergrond van de modal
- **Foto:** wellness sfeershot uit `fotos/` (bijv. `wellness-hero.webp`)
- **Overlay op foto:** gradient van onderaf voor leesbaarheid (rgba zwart ~75% onderaan → transparant bovenin)
- **Sluitknop:** rechtsboven in modal, subtiel (×)
- **Headline:** "Gratis badjas, handdoek & bubbels op de kamer" (Montserrat 300, ~26px)
- **Subtekst:** "Meld u aan voor de nieuwsbrief en ontvang het pakket bij uw eerste verblijf." (Montserrat 300, 13px, rgba wit 55%)
- **Form:** input + knop naast elkaar op één regel
  - Input: `type="email"`, placeholder "uw e-mailadres", glazen achtergrond (rgba wit 8%)
  - Knop: "Aanmelden" — Electrolize, uppercase, letter-spacing 2px, `#c23435`
- **Consent:** "Door u aan te melden gaat u akkoord met onze privacyverklaring. Afmelden kan altijd." (10px, rgba wit 30%)
- **Sluiten:** klik backdrop of × → popup verdwijnt, `ec_shown = "1"` gezet (maar geen conversie)

### Scherm 2: Succes

Vervangt scherm 1 na succesvolle submit (geen page reload):

- **Icoon:** envelop (inline SVG), cirkel met border, rgba wit 20%
- **Headline:** "Check uw inbox" (zelfde typografie als scherm 1)
- **Subtekst:** "We hebben u een mail gestuurd. Open hem om uw aanmelding te bevestigen — uw persoonlijke code staat daarin."
- **Spam-note:** "Geen mail? Check uw spamfolder." (10px, rgba wit 25%)
- Geen geblurde code weergeven op dit scherm

## Revinate Integratie

- Script laden: `//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1`
- Verborgen `<form id="revinate_contact_api_form" token="210bb345-899a-4f69-9b9f-4a00624a2024">` in de DOM
- Bij submit: email-waarde kopiëren naar hidden input, `revFormOnSubmit()` aanroepen
- `vipStatus`: veld meesturen met waarde `"Wellness nieuwsbrief"` voor segmentatie in Revinate
- Error handling: als `revFormOnSubmit()` mislukt → foutmelding tonen in modal ("Er ging iets mis. Probeer het opnieuw.")

## Mews Vouchercode

- Code: `WELKOM` — **moet handmatig aangemaakt worden in Mews** (los van bestaande `WELLNESSARRA`)
- De code geldt voor gasten die via de nieuwsbrief binnenkomen
- De welkomstmail met de code wordt ingesteld als **automatisering in Revinate** (niet via code)

## Productie-notities

- **Branding:** in productie echte Asteria fonts (Electrolize + Montserrat) en exacte kleuren controleren t.o.v. rest van pagina
- **Geen geblurde code** op succes scherm (dit was een mockup-idee, niet de eindversie)
- **Foto:** `wellness-hero.webp` als `background-image` op modal-inner, `object-fit: cover`

## Technische architectuur

- Volledig vanilla JS IIFE (patroon van booking popup en datepicker)
- Exporteert `window.openEmailCapture()` voor eventuele handmatige trigger
- Geen externe dependencies behalve Revinate CDN script
- Cloudflare Function **niet** nodig — Revinate JS handelt API call af

## A/B Meting

De variant (`ec_variant`) wordt opgeslagen in `sessionStorage`. Conversie-events kunnen later doorgestuurd worden naar analytics. Voor nu: geen extra tracking — eerst valideren of de popup überhaupt converteert.
