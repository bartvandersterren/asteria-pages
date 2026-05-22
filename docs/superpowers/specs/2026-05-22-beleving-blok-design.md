# Beleving blok — Design Spec
**Datum:** 2026-05-22
**Pagina:** `lander-google.html`
**Vervangt:** huidig `sfeer-blok` (regels 2239–2266)

---

## Doel

Een sfeervolle sectie die de omgeving rondom Hotel Asteria in Noord-Limburg toont. Geen overlap met het USP-blok (hotel faciliteiten). Het blok moet bezoekers inspireren om te boeken door de rijkheid van de omgeving te laten zien.

---

## Goedgekeurd ontwerp

Gebaseerd op Function Health "trusted-cols" carousel, vertaald naar Asteria.

### Structuur per item

Elk item bestaat uit **twee losse elementen** — niet één samengestelde kaart:

1. **Grote foto** (border-radius 18px, height ~340px)
   - Categorietag linksboven (pill, glass-morphism: wit/transparant met backdrop-filter blur)
   - Gradient overlay onderin (zwart, `to top`)
   - Locatienaam overlaid onderaan links (Electrolize, wit)
   - Afstandsbadge overlaid onderaan (glass-morphism pill: "10 min. rijden")

2. **Los tekstkaartje** (wit, border-radius 18px, box-shadow zacht)
   - Korte sfeer-beschrijving (Montserrat 300, ~0.8rem, kleur #555)
   - Geen titel, geen eyebrow — alleen de beschrijvende tekst

### Afwisselend patroon

- Oneven items (1, 3): foto boven → tekstkaart onder
- Even items (2, 4): tekstkaart boven → foto onder (`flex-direction: column-reverse`)

### Scroll-gedrag

- Horizontale scroll, `scroll-snap-type: x mandatory`
- Kaartbreedte: `flex: 0 0 270px`
- Gap tussen items: 14px
- Padding track: `0 28px`
- Scrollbar verborgen

---

## Content (4 items)

| # | Categorie | Locatienaam | Afstand | Beschrijving |
|---|-----------|-------------|---------|--------------|
| 1 | Natuur | Nationaal Park De Maasduinen | 10 min. rijden | Uitgestrekte duinen, stille bossen en honderden kilometers fiets- en wandelpaden — direct achter het hotel. |
| 2 | Cultuur | Kasteeltuinen Arcen | 20 min. rijden | Één van de mooiste tuinen van Nederland. Ideaal voor een middag vol kleur, rust en cultuur. |
| 3 | Actief | Fietsen & wandelen | Start bij het hotel | Noord-Limburg heeft enkele van de mooiste fietsroutes van Nederland, door heuvels en langs de Maas. |
| 4 | Culinair | Hertog Jan Brouwerij | 15 min. rijden | Rondleiding bij de bekendste brouwerij van Limburg, met proeverij en een kijkje in het brouwproces. |

---

## Foto's

Vereist 4 omgevingsfoto's — **nog niet aanwezig in repo**. Opties:
- Rechtenvrije stockfoto's (Unsplash/Pexels) als tijdelijke placeholders
- Echte foto's van de locaties als beschikbaar

Bestandsnamen (te plaatsen in `fotos/`):
- `omgeving-maasduinen.webp`
- `omgeving-kasteeltuinen.webp`
- `omgeving-fietsen.webp`
- `omgeving-hertogjan.webp`

---

## CSS tokens (uit brand.css)

- Primaire kleur: `#c23435`
- Body achtergrond: `#f0efed`
- Heading font: Electrolize
- Body font: Montserrat 300/400/700
- Kaart achtergrond: `#fff`

---

## Sectiekop

```html
<h2>Ontdek de omgeving</h2>
```
Geen eyebrow tekst. Montserrat of Electrolize, max-width ~340px.

---

## Plaatsing in pagina

Huidige `sfeer-blok` (section#sfeer, regels 2239–2266) wordt volledig vervangen door de nieuwe `.beleving` sectie. CSS van `.sfeer-blok`, `.sfeer-inner`, `.sfeer-grid`, `.sfeer-item`, `.sfeer-foto-wrap`, `.sfeer-label` kan worden verwijderd.

---

## Niet in scope

- Klikgedrag / lightbox op kaarten
- Linkjes naar externe sites
- Animaties bij scroll-in
- Meer dan 4 items
