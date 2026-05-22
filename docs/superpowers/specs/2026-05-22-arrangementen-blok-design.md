# Arrangementen Blok — Design Spec
_lander-google.html · 2026-05-22_

## Plaatsing

Na het kamertypes-blok (`#kamertypes`), vóór het beleving-blok (`#sfeer`).

## Arrangementen (3 stuks)

| Arrangement | Prijs | Voucher | Foto |
|---|---|---|---|
| Weekend Aanbieding | €166,– p.p. · 2 nachten | WEEKEND | fotos/restaurant-diner.webp |
| Wellnessarrangement | €139,50 p.p. · 1 nacht | WELLNESS | fotos/wellness-spa.webp |
| Asperge Arrangement | €138,– p.p. · 1 nacht | ASPERGE | fotos/restaurant-sfeer.webp |

Wellness = featured (meest gekozen badge, lichte rode schaduw).
Asperge = seizoensbadge "t/m 24 juni".

## Desktop layout

- 3 kolommen, `grid-template-columns: 1fr 1.12fr 1fr` (featured iets breder)
- Kaart: border-radius 20px, overflow hidden, subtiele box-shadow
- Hover: translateY(-4px) + zwaardere schaduw
- Foto bovenin: 200px (featured: 240px), object-fit cover, gradient overlay naar onder
- Badge op foto: rood pill (featured) of glazen pill (seizoen)
- Kaartbody: Electrolize eyebrow + title uppercase, Montserrat tagline + features
- Prijs in #c23435, bold
- Feature-lijst: grijze stippen voor basisitems, rode stippen voor arrangement-specifieke extras
- CTA: rood, full-width, border-radius 10px
- "Meer informatie"-knop: ghost, opent popup

## Mobile layout

- Verticale stack, 3 full-width kaarten
- Kaartfoto: 150px hoog
- Kaartbody: titel + tagline + prijs + twee knoppen (Info ghost / Boek rood)
- Spacing tussen kaarten: 12px

## Popup

Per arrangement een popup overlay (zelfde patroon als kamertypes-popup):
- Grote foto bovenin
- Badge op foto
- Titel + prijs
- Volledige includes-lijst met checkmarks
- Kleine notitie: verblijfsbelasting + gratis parkeren + WiFi
- CTA "Boek direct — €X p.p." → Mews deeplink met vouchercode

## Mews deeplinks

Basis: `https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556`
- Weekend: `?mewsVoucherCode=WEEKEND`
- Wellness: `?mewsVoucherCode=WELLNESS`
- Asperge: `?mewsVoucherCode=ASPERGE`

## Stijlregels

- Geen donkere sectie-achtergronden
- Achtergrond sectie: `#f8f7f5` of `#fff`
- Sectie-padding: 100px desktop / 64px mobile
- Anti-patroon: geen tekst midden op foto met zware overlay
- Aanspreekvorm: "u" (niet "je")
