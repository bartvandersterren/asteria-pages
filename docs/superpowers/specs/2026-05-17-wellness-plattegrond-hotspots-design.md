# Design Spec — Wellness plattegrond met hotspots

**Datum:** 2026-05-17
**Pagina:** `/wellness-arr-c` op visit.asteria.nl
**Blok:** Vervangt blok 6 (WELLNESS — Top Floor) uit de pagina-structuur spec

---

## Doel

Een fullscreen interactieve plattegrond van de wellness op de Top Floor. Gasten zien in één oogopslag welke ruimtes er zijn en kunnen op elke ruimte tikken voor een popup met foto, naam, omschrijving en faciliteitsinfo (bijv. temperatuur, type sauna).

---

## Visueel ontwerp

### Sectie-container
- `width: 100vw; height: 100vh` (100svh op mobile voor correcte viewport)
- `position: relative; overflow: hidden`
- Geen padding, geen max-width — letterlijk full-bleed
- Eventuele sectie-titel wordt pas na bouw bepaald op basis van beschikbare ruimte

### Achtergrond: AI-gegenereerde illustratie
- Bron: te genereren in aparte AI-subsessie (OpenAI / Gemini Imagen)
- Stijl: isometrische of bird's-eye ingekleurde illustratie van de wellness
- Kleurpalet: warme beiges/zandtinten, donker hout voor saunas, blauw-groen voor water, zachtgroen voor planten
- Bestandsnaam na generatie: `fotos/wellness-plattegrond-illustratie.webp`
- In HTML: `<img>` met `object-fit: cover; width: 100%; height: 100%`
- Lichte donkere gradient onderaan (rgba zwart, 40-50%) voor leesbaarheid hotspots

### Hotspot-pins
- Stijl: rode cirkel (#c23435), 14px diameter
- CSS pulse-animatie: na-element schaalt van 1 → 1.4 met opacity 0.6 → 0, 2s infinite
- Gepositioneerd absoluut via `left: X%; top: Y%` — percentages worden bepaald op de werkelijke AI-illustratie na generatie
- `transform: translate(-50%, -50%)` voor centerpunt op de zone
- `cursor: pointer` + `aria-label` per pin voor toegankelijkheid

---

## Zones en content

De volgende zones krijgen een hotspot. Entree, Omkleed/Lockers en Pantry worden niet gemarkeerd. Content per zone wordt ingevuld als aparte subtaak (zie Bouwtaken).

| Zone | Specs-voorbeelden |
|------|-------------------|
| Sauna 1 (Fins) | Temperatuur: ~85°C, Capaciteit: 8 pers. |
| Sauna 2 (Bio) | Temperatuur: ~60°C, Luchtvochtigheid: hoog |
| Sauna 3 (Zoutsteen) | Temperatuur: ~70°C |
| Sauna 4 (Infrarood) | Temperatuur: ~45°C, Diepe warmte |
| Infrarood sauna | Temperatuur: ~40°C |
| IJz-/dompelbad | Temperatuur: ~10°C, Contrast-bad |
| Kruidenbad | Temperatuur: ~38°C, Warm |
| Voetenbaden | 4 bassins, warm/koud |
| Stoomdouche | Stoom, ~42°C |
| Belevingsdouche | Regen/mist/tropisch |
| Gym / Fitness | Cardio + krachtapparatuur |
| Lounge / Ruimte | Ligbedden, uitzicht |

*Exacte teksten + foto-koppeling = aparte content-subtaak vóór bouw van de drawer.*

---

## Drawer (popup)

### Gedrag
- Tap op een hotspot-pin → drawer schuift omhoog vanuit onderkant scherm
- Animatie: `transform: translateY(0)` met `cubic-bezier(0.32, 0.72, 0, 1)`, 350ms
- Semi-transparante backdrop (rgba zwart 40%) achter drawer
- Sluit via: tap op backdrop, swipe-down, of kruisje rechtsboven
- Slechts één drawer tegelijk open

### Structuur van de drawer (mobile)
```
┌─────────────────────────────┐
│  — drag handle —            │
│  [foto van de ruimte]       │  ~180px hoog, object-fit: cover
│                             │
│  WELLNESS · TOP FLOOR       │  label (rood, uppercase, 11px)
│  Sauna 1                    │  titel (Electrolize, 22px)
│                             │
│  [svg] 85°C  [svg] 8 pers.  │  specs-badges (SVG-icoon + tekst, geen emoji)
│                             │
│  Omschrijving van de ruimte │  Montserrat 300, 14px, kleur #555
│  in twee à drie zinnen.     │
└─────────────────────────────┘
```

### Desktop: zijpaneel (side panel, ≥900px)
- Bij klik op pin: paneel schuift in aan de rechterkant van de sectie
- Breedte: ~300px, hoogte: 100% van de sectie
- Plattegrond blijft volledig zichtbaar links
- Geen backdrop — paneel staat naast de kaart, niet eroverheen
- Structuur paneel: foto bovenaan (~200px), dan label + titel + specs-badges + omschrijving
- Wisselen tussen zones: klik op andere pin vervangt paneel-inhoud zonder animatie-reset

### Specs-badges
- Horizontale rij van 2–4 badges
- Per badge: klein inline SVG-icoon + korte tekst (geen emoji)
- SVG-iconen: thermometer (temperatuur), silhouetten (capaciteit), druppel (water), etc.
- Niet alle zones hebben dezelfde badges — alleen relevante specs tonen

### Foto
- Uit eigen fotobank (`~/Documents/Asteria Fotobank/`)
- Geselecteerd en geconverteerd naar WebP (quality 72) in content-subtaak
- Fallback: gradient-placeholder als foto ontbreekt

---

## Mobile-first gedrag

- Sectie: `height: 100svh` (safe viewport height voor iOS)
- Hotspot-pins: minimaal 44×44px taptarget (pin zelf + onzichtbaar vergroot klikgebied)
- Drawer: max-height 70vh zodat plattegrond altijd deels zichtbaar blijft
- Overscroll binnen drawer mogelijk als content lang is

---

## Datastructuur (JS)

Zones worden gedefinieerd als een array van objecten in de pagina-HTML:

```js
const zones = [
  {
    id: 'sauna-1',
    naam: 'Sauna 1',
    label: 'Fins',
    foto: 'fotos/wellness-sauna-fins.webp',
    omschrijving: '...',
    specs: [
      { icoon: 'thermometer', tekst: '85°C' },
      { icoon: 'personen', tekst: '8 personen' }
    ],
    pin: { left: 64, top: 45 } // percentages, definitief na AI-illustratie
  },
  // ... overige zones
];
```

---

## Bouwtaken (volgorde)

1. **Content invullen** — voor alle zones: naam, omschrijving, specs-badges, foto-koppeling. Dit is een redactionele subtaak vóór implementatie.
2. **AI-illustratie genereren** — in aparte subsessie (OpenAI/Gemini). Prompt staat in `docs/superpowers/specs/arr-wellness-prompt.md`.
3. **Illustratie verwerken** — bijsnijden, converteren naar WebP, opslaan als `fotos/wellness-plattegrond-illustratie.webp`.
4. **Sectie bouwen** — HTML/CSS: fullscreen container, img-achtergrond, gradient overlay.
5. **Hotspots plaatsen** — pins positioneren op de werkelijke illustratie via percentages.
6. **Drawer bouwen** — HTML/CSS/JS: animatie, backdrop, specs-badges, foto, close-gedrag.
7. **Content koppelen** — zones-array invullen, foto's koppelen.
8. **Mobile QA** — testen op 375px en 430px viewport.

---

## Openstaande beslissingen

- Sectie-titel: na bouw beoordelen of er ruimte is voor een kop boven de plattegrond
- Hotspot-posities (percentages): definitief pas na ontvangst AI-illustratie
- Welke foto per zone: keuze uit fotobank in content-subtaak
- Precieze spec-teksten per zone: invullen in content-subtaak
