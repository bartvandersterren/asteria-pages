# Vertalingen EN/DE — Wellness Arr-C Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add English and German versions of wellness-arr-c.html with automatic language detection and manual language switcher.

**Architecture:** 3 separate static HTML files (NL existing, EN + DE new). Auto-detect on NL page only (localStorage → navigator.language → redirect). Manual switcher via existing `<select class="lang-nav">` in nav. hreflang tags on all 3 pages for SEO.

**Tech Stack:** Vanilla HTML/JS/CSS, Cloudflare Pages static hosting (no build step)

---

## Files

| File | Action |
|------|--------|
| `wellness-arr-c.html` | Modify: add hreflang, auto-detect script, lang-nav wiring |
| `wellness-arr-c-en.html` | Create: full English translation of NL file |
| `wellness-arr-c-de.html` | Create: full German translation of NL file |

---

## Translation Reference

All translatable strings, organized by section. Only strings that differ are listed.
**NL column = existing text in file (verify against file before replacing).**

### Meta / Head

| Key | NL | EN | DE |
|-----|----|----|-----|
| `html[lang]` | `nl` | `en` | `de` |
| `<title>` | `Wellness Arrangement \| Hotel Asteria Venray` | `Wellness Package \| Hotel Asteria Venray` | `Wellness Arrangement \| Hotel Asteria Venray` |
| `meta[description]` | `Wellness arrangement met overnachting, drie-gangen diner en ontbijtbuffet bij Hotel Asteria Venray. Vier unieke sauna's op de Top Floor. Vanaf €139,50 p.p.` | `Wellness package with overnight stay, three-course dinner and breakfast buffet at Hotel Asteria Venray. Four unique saunas on the Top Floor. From €139.50 p.p.` | `Wellness-Arrangement mit Übernachtung, Drei-Gänge-Dinner und Frühstücksbuffet im Hotel Asteria Venray. Vier einzigartige Saunen auf der Top Floor. Ab €139,50 p.P.` |
| `og:title` | same as title | same as title | same as title |
| `og:description` | same as meta description | same as EN meta | same as DE meta |
| `og:locale` | `nl_NL` | `en_GB` | `de_DE` |
| `canonical href` | `.../wellness-arr-c` | `.../wellness-arr-c-en` | `.../wellness-arr-c-de` |
| schema.org `description` | `Overnachting, welkomstdrankje, badjas en slippers, vrije toegang wellness, drie-gangen diner en ontbijtbuffet.` | `Overnight stay, welcome drink, bathrobe and slippers, free wellness access, three-course dinner and breakfast buffet.` | `Übernachtung, Willkommensgetränk, Bademantel und Hausschuhe, freier Wellnesszugang, Drei-Gänge-Dinner und Frühstücksbuffet.` |
| schema.org `unitText` | `per persoon` | `per person` | `pro Person` |

### Sticky CTA + Sticky Card

| Key | NL | EN | DE |
|-----|----|----|-----|
| `stickyFab[aria-label]` | `Boek direct: Wellness Arrangement` | `Book now: Wellness Package` | `Jetzt buchen: Wellness Arrangement` |
| stickyFab text | `Boek direct` | `Book now` | `Jetzt buchen` |
| `.sticky-card__name` | `Wellness Arrangement` | `Wellness Package` | `Wellness Arrangement` |
| `.sticky-card__price-sub` | `per persoon` | `per person` | `p.P.` |
| `.sticky-card__btn` | `Boek direct →` | `Book now →` | `Jetzt buchen →` |
| `stickyCard[aria-label]` | `Snel boeken` | `Quick booking` | `Schnell buchen` |

### Nav

| Key | NL | EN | DE |
|-----|----|----|-----|
| `<select>` selected option | `nl` | `en` | `de` |
| Kamers en Suites | `Kamers en Suites` | `Rooms and Suites` | `Zimmer und Suiten` |
| Omgeving | `Omgeving` | `Surroundings` | `Umgebung` |
| Contact | `Contact` | `Contact` | `Kontakt` |
| `.book-now` button | `Boek nu` | `Book now` | `Jetzt buchen` |
| `#menuOpen` text | `Menu` (keep SVG) | `Menu` | `Menü` |
| mobile bel button | `Bel` (keep SVG) | `Call` | `Anrufen` |

### Hero

| Key | NL | EN | DE |
|-----|----|----|-----|
| `.hero__location` | `Venray · Noord-Limburg` | `Venray · North Limburg` | `Venray · Nord-Limburg` |
| `.hero__title` | `Wellness, diner<br>&amp; een goed bed` | `Wellness, dinner<br>&amp; a good night's sleep` | `Wellness, Abendessen<br>&amp; ein gutes Bett` |
| `.hero__sub` | `Sauna, drie-gangen diner en een comfortabele kamer. Alles geregeld, u hoeft alleen te komen.` | `Sauna, three-course dinner and a comfortable room. Everything arranged, all you need to do is arrive.` | `Sauna, Drei-Gänge-Dinner und ein komfortables Zimmer. Alles geregelt, Sie müssen nur kommen.` |
| `.hero__cta` | `Boek het arrangement` | `Book the package` | `Das Arrangement buchen` |
| trust 1 | `&#10003; 4 sauna's op de Top Floor` | `&#10003; 4 saunas on the Top Floor` | `&#10003; 4 Saunen auf der Top Floor` |
| trust 2 | `&#10003; Diner &amp; ontbijt inbegrepen` | `&#10003; Dinner &amp; breakfast included` | `&#10003; Dinner &amp; Frühstück inbegriffen` |
| trust 3 | `&#10003; Gratis annuleren` | `&#10003; Free cancellation` | `&#10003; Kostenlose Stornierung` |

### Arrangement Block (arr-c)

| Key | NL | EN | DE |
|-----|----|----|-----|
| `section[aria-label]` | `Wellness arrangement, wat is inbegrepen` | `Wellness package, what is included` | `Wellness Arrangement, was ist inbegriffen` |
| `arr-c__rating[aria-label]` | `4,2 van 5 sterren · 2.219 Google reviews` | `4.2 out of 5 stars · 2,219 Google reviews` | `4,2 von 5 Sternen · 2.219 Google-Bewertungen` |
| `.arr-c__rating-count` | `· 2.219 reviews` | `· 2,219 reviews` | `· 2.219 Bewertungen` |
| `.arr-c__eyebrow` | `Wellness Arrangement` | `Wellness Package` | `Wellness Arrangement` |
| `.arr-c__title` | `Wat is inbegrepen?` | `What's included?` | `Was ist inbegriffen?` |
| `.arr-c__intro` | `Eén overnachting met wellness, diner en ontbijt. Vrije toegang tot de wellness op de Top Floor.` | `One overnight stay with wellness, dinner and breakfast. Free access to the wellness on the Top Floor.` | `Eine Übernachtung mit Wellness, Abendessen und Frühstück. Freier Zugang zum Wellnessbereich auf der Top Floor.` |
| feature 1 name | `Overnachting` | `Overnight stay` | `Übernachtung` |
| feature 1 desc | `Kamer naar keuze, van Comfort tot Suite` | `Room of your choice, from Comfort to Suite` | `Zimmer nach Wahl, vom Comfort bis zur Suite` |
| feature 1 `data-caption` | `Comfortabele kamer` | `Comfortable room` | `Komfortables Zimmer` |
| feature 2 name | `Welkomstdrankje` | `Welcome drink` | `Willkommensgetränk` |
| feature 2 desc | `Botega prosecco op de kamer bij aankomst` | `Botega prosecco in your room on arrival` | `Botega Prosecco auf dem Zimmer bei der Ankunft` |
| feature 2 `data-caption` | `Botega welkomstdrankje op de kamer` | `Botega welcome drink in your room` | `Botega Willkommensgetränk auf dem Zimmer` |
| feature 3 name | `Badjas & slippers` | `Bathrobe & slippers` | `Bademantel & Pantoffeln` |
| feature 3 desc | `Alles klaargelegd, niets mee te nemen` | `Everything prepared, nothing to bring` | `Alles bereitgestellt, nichts mitbringen` |
| feature 3 `data-caption` | `Badjas, slippers & handdoekpakket` | `Bathrobe, slippers & towel set` | `Bademantel, Pantoffeln & Handtücher` |
| feature 4 name | `Vrije wellness toegang` | `Free wellness access` | `Freier Wellnesszugang` |
| feature 4 desc | `4 sauna's & stoombad op de Top Floor` | `4 saunas & steam bath on the Top Floor` | `4 Saunen & Dampfbad auf der Top Floor` |
| feature 4 `data-caption` | `4 sauna's & stoombad · Top Floor` | `4 saunas & steam bath · Top Floor` | `4 Saunen & Dampfbad · Top Floor` |
| feature 5 name | `Drie-gangen diner` | `Three-course dinner` | `Drei-Gänge-Dinner` |
| feature 5 desc | `Seizoensgerechten, rustig aan tafel` | `Seasonal dishes, no rush at the table` | `Saisonale Gerichte, entspanntes Abendessen` |
| feature 5 `data-caption` | `Drie-gangen diner` | `Three-course dinner` | `Drei-Gänge-Dinner` |
| feature 6 name | `Uitgebreid ontbijtbuffet` | `Extensive breakfast buffet` | `Ausgiebiges Frühstücksbuffet` |
| feature 6 desc | `Warme broodjes, charcuterie en meer` | `Fresh bread, charcuterie and more` | `Frisches Brot, Aufschnitt und mehr` |
| feature 6 `data-caption` | `Uitgebreid ontbijtbuffet` | `Extensive breakfast buffet` | `Ausgiebiges Frühstücksbuffet` |
| `.arr-c__price-from` | `Vanaf` | `From` | `Ab` |
| `.arr-c__price-sub` | `p.p. op basis van een Comfort Kamer` | `p.p. based on a Comfort Room` | `p.P. auf Basis eines Comfort-Zimmers` |
| `.arr-c__cta` | `Boek het arrangement` | `Book the package` | `Das Arrangement buchen` |

### Reviews Section

| Key | NL | EN | DE |
|-----|----|----|-----|
| `section[aria-label]` | `Gastbeoordelingen` | `Guest reviews` | `Gästebewertungen` |
| `#reviewsTotal` | `2.219 beoordelingen` | `2,219 reviews` | `2.219 Bewertungen` |
| `.reviews__loading` | `Reviews worden geladen…` | `Loading reviews…` | `Bewertungen werden geladen…` |
| JS: `total.textContent` suffix | `+ ' beoordelingen'` | `+ ' reviews'` | `+ ' Bewertungen'` |
| JS: `toLocaleString` locale | `'nl-NL'` | `'en-GB'` | `'de-DE'` |

**Note:** Static fallback reviews (Dutch guest quotes) remain in Dutch — authentic reviews retain value in original language.

### Wellness Plattegrond

| Key | NL | EN | DE |
|-----|----|----|-----|
| `section[aria-label]` | `Wellness faciliteiten, interactieve plattegrond` | `Wellness facilities, interactive floor plan` | `Wellnesseinrichtungen, interaktiver Grundriss` |
| `wp-intro__label` | `Wellness · Top Floor` | `Wellness · Top Floor` | `Wellness · Top Floor` |
| `wp-intro__title` | `Verken de faciliteiten` | `Explore the facilities` | `Erkunden Sie die Einrichtungen` |
| `wp-intro__sub` | `Ontdek alle ruimtes van onze 300m² wellness op de Top Floor. Tik op een locatie voor meer informatie over elke ruimte.` | `Discover all spaces of our 300m² wellness area on the Top Floor. Tap a location for more information about each space.` | `Entdecken Sie alle Räume unseres 300m² großen Wellnessbereichs auf der Top Floor. Tippen Sie auf einen Standort für weitere Informationen.` |
| `img[alt]` | `Plattegrond van de wellness op de Top Floor van Hotel Asteria` | `Floor plan of the wellness area on the Top Floor of Hotel Asteria` | `Grundriss des Wellnessbereichs auf der Top Floor von Hotel Asteria` |
| `wp-panel[aria-label]` | `Wellness ruimte details` | `Wellness space details` | `Wellnessraum Details` |
| `#wp-panel-close[aria-label]` | `Sluiten` | `Close` | `Schließen` |
| `wp-panel__label` | `Wellness · Top Floor` | `Wellness · Top Floor` | `Wellness · Top Floor` |
| JS pin `aria-label` suffix | `', tik voor meer info'` | `', tap for more info'` | `', tippen für mehr Infos'` |

#### WP_ZONES — alleen naam, label, omschrijving en specs tekst wijzigen. Pin-posities (left/top) en foto-paden zijn identiek in alle versies.

**EN WP_ZONES:**
```js
const WP_ZONES = [
  { id:'sauna-bos',       naam:'Sauna 2 · Forest Sauna',     label:'Forest',
    foto:'fotos/wp-sauna-bos.webp',
    omschrijving:'The hottest sauna with an atmospheric illuminated forest backdrop. Intense dry heat for the experienced sauna-goer.',
    specs:[{icon:'temp',tekst:'±100°C'},{icon:'type',tekst:'Dry heat'}],
    pin:{left:76.5,top:15.5} },
  { id:'sauna-zoutsteen', naam:'Sauna 3 · Salt Stone Sauna', label:'Salt Stone',
    foto:'fotos/wp-sauna-zoutsteen.webp',
    omschrijving:'Illuminated with salt stone lamps that cast a warm pink light. The salt in the air benefits the respiratory tract and skin.',
    specs:[{icon:'temp',tekst:'±90°C'},{icon:'type',tekst:'Salt stone'}],
    pin:{left:91.1,top:15.7} },
  { id:'sauna-fins',      naam:'Sauna 4 · Finnish Sauna',    label:'Finnish',
    foto:'fotos/wp-sauna-fins.webp',
    omschrijving:'The classic Finnish sauna with dry heat. Ideal for deep muscle relaxation and stimulating circulation.',
    specs:[{icon:'temp',tekst:'±80°C'},{icon:'type',tekst:'Dry heat'}],
    pin:{left:90.9,top:35.2} },
  { id:'sauna-infrarood', naam:'Infrared Sauna',             label:'Infrared',
    foto:'fotos/wp-sauna-infrarood.webp',
    omschrijving:'Infrared radiation heats the body from within without heating the air. Gentle warmth that penetrates deep into muscles and joints. Perfect for recovery.',
    specs:[{icon:'temp',tekst:'40–50°C'},{icon:'type',tekst:'Infrared'}],
    pin:{left:53.3,top:11.4} },
  { id:'voetenbaden',     naam:'Foot Baths',                 label:'4 basins',
    foto:'fotos/wp-voetenbaden.webp',
    omschrijving:'Four foot baths alternating warm and cold. Pamper your feet after a walk or sauna session. Reflex points are stimulated and legs feel lighter.',
    specs:[{icon:'aantal',tekst:'4 basins'},{icon:'type',tekst:'Warm & cold'}],
    pin:{left:65.5,top:19.1} },
  { id:'ijsbad',          naam:'Ice/Plunge Bath',            label:'Contrast',
    foto:'fotos/wp-dompelbad.webp',
    omschrijving:'The cold plunge after the sauna is the secret of contrast bathing. The sudden cold stimulates circulation and gives an immediate energy boost.',
    specs:[{icon:'temp',tekst:'±10°C'},{icon:'type',tekst:'Cold bath'}],
    pin:{left:44.5,top:25.9} },
  { id:'kruidenbad',      naam:'Herbal Bath',                label:'Herbal bath',
    foto:'fotos/wp-kruidenbad.webp',
    omschrijving:'A warm atmospheric bath with fresh herbs. The scents and warmth provide deep relaxation of body and mind.',
    specs:[{icon:'temp',tekst:'±38°C'},{icon:'type',tekst:'Warm bath'}],
    pin:{left:44.5,top:37.3} },
  { id:'stoomdouche',     naam:'Steam Shower',               label:'Steam',
    foto:'fotos/wp-stoomdouche.webp',
    omschrijving:'A steam cabin full of moist heat. The steam opens pores, cleanses the skin and relaxes the upper airways. Ideal after the sauna.',
    specs:[{icon:'temp',tekst:'40–45°C'},{icon:'type',tekst:'Steam'}],
    pin:{left:41.7,top:50.1} },
  { id:'gym',             naam:'Gym & Fitness',              label:'Fitness',
    foto:'fotos/wp-gym.webp',
    omschrijving:'A modern fitness room with cardio and strength equipment. Freely accessible for all hotel guests, for an active start or end to the day.',
    specs:[{icon:'type',tekst:'Cardio & Strength'}],
    pin:{left:19.9,top:71.0} },
  { id:'lounge',          naam:'Relaxation Area',            label:'Lounge',
    foto:'fotos/wp-relaxruimte.webp',
    omschrijving:'The relaxation area with comfortable loungers offers views over the surroundings. Take your time after the sauna. Rest is part of the ritual.',
    specs:[{icon:'type',tekst:'Loungers'}],
    pin:{left:78.7,top:70.0} },
];
```

**DE WP_ZONES:**
```js
const WP_ZONES = [
  { id:'sauna-bos',       naam:'Sauna 2 · Waldsauna',        label:'Wald',
    foto:'fotos/wp-sauna-bos.webp',
    omschrijving:'Die heißeste Sauna mit atmosphärisch beleuchtetem Waldhintergrund. Intensive Trockenhitze für den erfahrenen Saunagänger.',
    specs:[{icon:'temp',tekst:'±100°C'},{icon:'type',tekst:'Trockenhitze'}],
    pin:{left:76.5,top:15.5} },
  { id:'sauna-zoutsteen', naam:'Sauna 3 · Salzsteinsauna',   label:'Salzstein',
    foto:'fotos/wp-sauna-zoutsteen.webp',
    omschrijving:'Beleuchtet mit Salzsteinlampen, die ein warmes rosa Licht verbreiten. Das Salz in der Luft wirkt sich positiv auf die Atemwege und die Haut aus.',
    specs:[{icon:'temp',tekst:'±90°C'},{icon:'type',tekst:'Salzstein'}],
    pin:{left:91.1,top:15.7} },
  { id:'sauna-fins',      naam:'Sauna 4 · Finnische Sauna',  label:'Finnisch',
    foto:'fotos/wp-sauna-fins.webp',
    omschrijving:'Die klassische finnische Sauna mit Trockenhitze. Ideal für tiefe Muskelentspannung und zur Anregung des Blutkreislaufs.',
    specs:[{icon:'temp',tekst:'±80°C'},{icon:'type',tekst:'Trockenhitze'}],
    pin:{left:90.9,top:35.2} },
  { id:'sauna-infrarood', naam:'Infrarotsauna',              label:'Infrarot',
    foto:'fotos/wp-sauna-infrarood.webp',
    omschrijving:'Infrarotstrahlung erwärmt den Körper von innen, ohne die Luft zu erhitzen. Sanfte Wärme, die tief in Muskeln und Gelenke eindringt. Ideal zur Regeneration.',
    specs:[{icon:'temp',tekst:'40–50°C'},{icon:'type',tekst:'Infrarot'}],
    pin:{left:53.3,top:11.4} },
  { id:'voetenbaden',     naam:'Fußbäder',                   label:'4 Becken',
    foto:'fotos/wp-voetenbaden.webp',
    omschrijving:'Vier Fußbäder wechseln warm und kalt ab. Verwöhnen Sie Ihre Füße nach einem Spaziergang oder einer Saunasitzung. Reflexzonen werden stimuliert, die Beine fühlen sich leichter an.',
    specs:[{icon:'aantal',tekst:'4 Becken'},{icon:'type',tekst:'Warm & kalt'}],
    pin:{left:65.5,top:19.1} },
  { id:'ijsbad',          naam:'Eis-/Tauchbad',              label:'Kontrast',
    foto:'fotos/wp-dompelbad.webp',
    omschrijving:'Das kalte Tauchbad nach der Sauna ist das Geheimnis des Kontrastbadens. Die plötzliche Kälte regt den Blutkreislauf an und gibt sofortige Energie.',
    specs:[{icon:'temp',tekst:'±10°C'},{icon:'type',tekst:'Kaltes Bad'}],
    pin:{left:44.5,top:25.9} },
  { id:'kruidenbad',      naam:'Kräuterbad',                 label:'Kräuterbad',
    foto:'fotos/wp-kruidenbad.webp',
    omschrijving:'Ein warmes, stimmungsvolles Bad mit frischen Kräutern. Die Düfte und Wärme sorgen für tiefe Entspannung von Körper und Geist.',
    specs:[{icon:'temp',tekst:'±38°C'},{icon:'type',tekst:'Warmes Bad'}],
    pin:{left:44.5,top:37.3} },
  { id:'stoomdouche',     naam:'Dampfdusche',                label:'Dampf',
    foto:'fotos/wp-stoomdouche.webp',
    omschrijving:'Eine Dampfkabine voller feuchter Wärme. Der Dampf öffnet die Poren, reinigt die Haut und entspannt die oberen Atemwege. Ideal nach der Sauna.',
    specs:[{icon:'temp',tekst:'40–45°C'},{icon:'type',tekst:'Dampf'}],
    pin:{left:41.7,top:50.1} },
  { id:'gym',             naam:'Gym & Fitness',              label:'Fitness',
    foto:'fotos/wp-gym.webp',
    omschrijving:'Ein moderner Fitnessraum mit Cardio- und Kraftgeräten. Frei zugänglich für alle Hotelgäste, für einen aktiven Start oder Abschluss des Tages.',
    specs:[{icon:'type',tekst:'Cardio & Kraft'}],
    pin:{left:19.9,top:71.0} },
  { id:'lounge',          naam:'Ruheraum',                   label:'Lounge',
    foto:'fotos/wp-relaxruimte.webp',
    omschrijving:'Der Ruheraum mit komfortablen Liegebetten bietet Ausblick über die Umgebung. Nehmen Sie sich Zeit nach der Sauna. Ruhe ist Teil des Rituals.',
    specs:[{icon:'type',tekst:'Liegebetten'}],
    pin:{left:78.7,top:70.0} },
];
```

### Kamertypes Section (HTML)

| Key | NL | EN | DE |
|-----|----|----|-----|
| `section[aria-label]` | `Kamertypes` | `Room types` | `Zimmertypen` |
| `.rooms__eyebrow` | `Kies uw kamer` | `Choose your room` | `Wählen Sie Ihr Zimmer` |
| `.rooms__title` | `Welke kamer past bij u?` | `Which room suits you?` | `Welches Zimmer passt zu Ihnen?` |
| `.rooms__sub` | `Upgrade voor meer comfort of privacy` | `Upgrade for more comfort or privacy` | `Upgrade für mehr Komfort oder Privatsphäre` |
| `.rooms__base-badge` | `Standaard inbegrepen` | `Included in package` | `Im Arrangement enthalten` |
| `.rooms__base-name` | `Comfort Kamer` | `Comfort Room` | `Comfort Zimmer` |
| `.rooms__base-feats` | `~22 m² · tweepersoons bed · douche · zithoek · airco · WiFi` | `~22 m² · double bed · shower · seating area · A/C · WiFi` | `~22 m² · Doppelbett · Dusche · Sitzecke · Klimaanlage · WLAN` |
| `rooms__base-img[alt]` | `Comfort Kamer` | `Comfort Room` | `Comfort Zimmer` |
| Royale badge span | `Upgrade` | `Upgrade` | `Upgrade` |
| Royale deltas | `meer ruimte` + `ligbad` | `more space` + `bathtub` | `mehr Platz` + `Badewanne` |
| Deluxe badge span | `+ Eigen sauna` | `+ Private sauna` | `+ Eigene Sauna` |
| Deluxe deltas | `meer ruimte` + `privé infraroodsauna` | `more space` + `private infrared sauna` | `mehr Platz` + `private Infrarotsauna` |
| Junior Suite deltas | `kingsize bed` + `ruime zithoek` + `ligbad` + `koelkast` | `kingsize bed` + `spacious seating area` + `bathtub` + `mini fridge` | `Kingsize-Bett` + `große Sitzecke` + `Badewanne` + `Kühlschrank` |
| Suite deltas | `kingsize bed` + `privé infraroodsauna` + `ruime zithoek` + `koelkast` | `kingsize bed` + `private infrared sauna` + `spacious seating area` + `mini fridge` | `Kingsize-Bett` + `private Infrarotsauna` + `große Sitzecke` + `Kühlschrank` |
| Bruidssuite deltas | `kingsize bed` + `vrijstaand bad` + `inloopdouche` + `koelkast` | `kingsize bed` + `freestanding bath` + `walk-in shower` + `mini fridge` | `Kingsize-Bett` + `freistehende Badewanne` + `begehbare Dusche` + `Kühlschrank` |
| `roomPopup[aria-label]` | `Kamerdetails` | `Room details` | `Zimmerdetails` |

### Kamertypes JS — ROOMS object

Translate `name`, `desc`, `features`, `shortDesc`, and badge span text. Keep `imgs`, `upgrade` (price delta), `mewsCategoryId` unchanged.

**EN ROOMS:**
```js
'comfort':      { badge:'<span class="room-row__badge badge--included">Included in package</span>',
                  name:'Comfort Room',
                  desc:'A comfortable room for two people with everything you need for a relaxed stay.',
                  features:['~22 m²','Double bed','Shower','Seating area','A/C','WiFi'],
                  shortDesc:'~22 m² · double bed · shower' },
'royale':       { badge:'<span class="room-row__badge badge--upgrade">Upgrade</span>',
                  name:'Royale Room',
                  desc:'More space to breathe — and the option of a bath if you want to relax in your room after wellness too.',
                  features:['More spacious than Comfort','Bath or shower','Seating area','Coffee maker','A/C'],
                  shortDesc:'More spacious · bath or shower · coffee maker' },
'deluxe':       { badge:'<span class="room-row__badge badge--sauna">+ Private sauna</span>',
                  name:'Deluxe Room',
                  desc:'A private infrared sauna in your room. Wellness starts at your door — no shared spaces.',
                  features:['Private infrared sauna','More space','Double bed','Shower','Seating area','Coffee maker','A/C'],
                  shortDesc:'~25 m² · private infrared sauna · kingsize bed' },
'junior-suite': { badge:'<span class="room-row__badge badge--upgrade">Upgrade</span>',
                  name:'Junior Suite',
                  desc:'The extra size that makes a wellness evening truly luxurious: kingsize bed, a bath and a spacious seating area.',
                  features:['Kingsize bed','Bath','Spacious seating area with sofa bed','Mini fridge','Coffee maker','A/C'],
                  shortDesc:'Kingsize bed · bath · spacious seating area' },
'suite':        { badge:'<span class="room-row__badge badge--sauna">+ Private sauna</span>',
                  name:'Suite',
                  desc:'The best of both worlds: a spacious suite with private infrared sauna and access to the shared wellness centre.',
                  features:['Kingsize bed','Private infrared sauna','Spacious seating area with sofa bed','Mini fridge','A/C'],
                  shortDesc:'Kingsize bed · private infrared sauna · spacious suite' },
'bruidssuite':  { badge:'<span class="room-row__badge badge--premium">Premium</span>',
                  name:'Bridal Suite',
                  desc:'Freestanding bathtub, spacious walk-in shower and the most romantic atmosphere in the hotel. For an unforgettable evening.',
                  features:['Kingsize bed','Freestanding bathtub','Spacious walk-in shower','Seating area','Mini fridge','A/C'],
                  shortDesc:'Kingsize bed · freestanding bathtub · romantic atmosphere' },
```

**DE ROOMS:**
```js
'comfort':      { badge:'<span class="room-row__badge badge--included">Im Arrangement enthalten</span>',
                  name:'Comfort Zimmer',
                  desc:'Ein komfortables Zimmer für zwei Personen mit allem, was Sie für einen entspannten Aufenthalt benötigen.',
                  features:['~22 m²','Doppelbett','Dusche','Sitzecke','Klimaanlage','WLAN'],
                  shortDesc:'~22 m² · Doppelbett · Dusche' },
'royale':       { badge:'<span class="room-row__badge badge--upgrade">Upgrade</span>',
                  name:'Royale Zimmer',
                  desc:'Mehr Platz zum Atmen — und die Wahl einer Badewanne, wenn Sie sich nach dem Wellness auch auf dem Zimmer entspannen möchten.',
                  features:['Geräumiger als Comfort','Badewanne oder Dusche','Sitzecke','Kaffeemaschine','Klimaanlage'],
                  shortDesc:'Geräumiger · Badewanne oder Dusche · Kaffeemaschine' },
'deluxe':       { badge:'<span class="room-row__badge badge--sauna">+ Eigene Sauna</span>',
                  name:'Deluxe Zimmer',
                  desc:'Eine private Infrarotsauna auf dem Zimmer. Wellness beginnt an Ihrer Tür — keine Gemeinschaftsräume.',
                  features:['Private Infrarotsauna','Mehr Platz','Doppelbett','Dusche','Sitzecke','Kaffeemaschine','Klimaanlage'],
                  shortDesc:'~25 m² · private Infrarotsauna · Kingsize-Bett' },
'junior-suite': { badge:'<span class="room-row__badge badge--upgrade">Upgrade</span>',
                  name:'Junior Suite',
                  desc:'Die extra Größe, die einen Wellnessabend wirklich luxuriös macht: Kingsize-Bett, eine Badewanne und eine große Sitzecke.',
                  features:['Kingsize-Bett','Badewanne','Große Sitzecke mit Schlafsofa','Kühlschrank','Kaffeemaschine','Klimaanlage'],
                  shortDesc:'Kingsize-Bett · Badewanne · große Sitzecke' },
'suite':        { badge:'<span class="room-row__badge badge--sauna">+ Eigene Sauna</span>',
                  name:'Suite',
                  desc:'Das Beste aus beiden Welten: eine geräumige Suite mit privater Infrarotsauna und Zugang zum gemeinsamen Wellnesszentrum.',
                  features:['Kingsize-Bett','Private Infrarotsauna','Große Sitzecke mit Schlafsofa','Kühlschrank','Klimaanlage'],
                  shortDesc:'Kingsize-Bett · private Infrarotsauna · geräumige Suite' },
'bruidssuite':  { badge:'<span class="room-row__badge badge--premium">Premium</span>',
                  name:'Brautsuite',
                  desc:'Freistehende Badewanne, geräumige begehbare Dusche und die romantischste Atmosphäre des Hotels. Für einen unvergesslichen Abend.',
                  features:['Kingsize-Bett','Freistehende Badewanne','Geräumige begehbare Dusche','Sitzecke','Kühlschrank','Klimaanlage'],
                  shortDesc:'Kingsize-Bett · freistehende Badewanne · romantische Atmosphäre' },
```

### Kamertypes JS — Dynamisch gegenereerde tekst

| Key | NL | EN | DE |
|-----|----|----|-----|
| room-popup arrow prev `aria-label` | `Vorige` | `Previous` | `Zurück` |
| room-popup arrow next `aria-label` | `Volgende` | `Next` | `Weiter` |
| `bk-room-card__toggle` button text | `meer info` | `more info` | `mehr Info` |
| room detail select button | `Selecteer deze kamer` | `Select this room` | `Dieses Zimmer wählen` |
| `bk-room-card__vol` | `Vol` | `Full` | `Belegt` |

### Booking Popup (HTML)

| Key | NL | EN | DE |
|-----|----|----|-----|
| `bk-overlay[aria-label]` | `Verblijf boeken` | `Book your stay` | `Aufenthalt buchen` |
| `bk-close[aria-label]` | `Sluiten` | `Close` | `Schließen` |
| `.bk-title` stap 1 | `Kies uw verblijfsdata` | `Choose your stay dates` | `Wählen Sie Ihre Aufenthaltsdaten` |
| `bk-summary__label` Aankomst | `Aankomst` | `Arrival` | `Ankunft` |
| `bk-summary__label` Vertrek | `Vertrek` | `Departure` | `Abreise` |
| `bk-summary__label` Nachten | `Nachten` | `Nights` | `Nächte` |
| `bk-selected-room__label` | `Geselecteerde kamer` | `Selected room` | `Ausgewähltes Zimmer` |
| `#bkChangeRoom` | `wijzig` | `change` | `ändern` |
| `#bkToStep2` (initial) | `Volgende: kies kamer →` | `Next: choose room →` | `Weiter: Zimmer wählen →` |
| `#bkDirectBook` | `Of boek direct zonder kamerkeuze` | `Or book directly without room selection` | `Oder direkt ohne Zimmerauswahl buchen` |
| `#bkBack[aria-label]` | `Terug naar datumkeuze` | `Back to date selection` | `Zurück zur Datumsauswahl` |
| `#bkBack` text | `← Aanpassen` | `← Back` | `← Zurück` |
| `.bk-title` stap 2 | `Kies uw kamer` | `Choose your room` | `Wählen Sie Ihr Zimmer` |
| `#bkConfirm` | `Bekijk beschikbaarheid →` | `Check availability →` | `Verfügbarkeit prüfen →` |
| `#bkBackToRooms[aria-label]` | `Terug naar kamerkeuze` | `Back to room selection` | `Zurück zur Zimmerauswahl` |
| `#bkBackToRooms` text | `← Terug` | `← Back` | `← Zurück` |

### Booking Popup JS — Dynamisch gegenereerde tekst

| Key | NL | EN | DE |
|-----|----|----|-----|
| `DAYS_NL` array | `['zo','ma','di','wo','do','vr','za']` | `['Su','Mo','Tu','We','Th','Fr','Sa']` | `['So','Mo','Di','Mi','Do','Fr','Sa']` |
| `MONTHS_NL` array | `['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec']` | `['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']` | `['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez']` |
| nacht singular | `' nacht'` | `' night'` | `' Nacht'` |
| nacht plural | `' nachten'` | `' nights'` | `' Nächte'` |
| dynamic btnToStep2 (with pre-selected room) | `'Bekijk beschikbaarheid \u2192'` | `'Check availability \u2192'` | `'Verfügbarkeit prüfen \u2192'` |
| dynamic btnToStep2 (no pre-selection) | `'Volgende: kies kamer \u2192'` | `'Next: choose room \u2192'` | `'Weiter: Zimmer wählen \u2192'` |

### Custom Datepicker JS

| Key | NL | EN | DE |
|-----|----|----|-----|
| `MONTH_NAMES` | `['Januari','Februari','Maart','April','Mei','Juni','Juli','Augustus','September','Oktober','November','December']` | `['January','February','March','April','May','June','July','August','September','October','November','December']` | `['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']` |
| `DAY_NAMES` | `['Ma','Di','Wo','Do','Vr','Za','Zo']` | `['Mo','Tu','We','Th','Fr','Sa','Su']` | `['Mo','Di','Mi','Do','Fr','Sa','So']` |

### Diner Block

| Key | NL | EN | DE |
|-----|----|----|-----|
| `section[aria-label]` | `Drie-gangen diner, inbegrepen in het arrangement` | `Three-course dinner, included in the package` | `Drei-Gänge-Dinner, im Arrangement enthalten` |
| `diner__bg[aria-label]` | `Restaurant Hotel Asteria, intiem dineren met uitzicht op het groen` | `Restaurant Hotel Asteria, intimate dining with a view of the greenery` | `Restaurant Hotel Asteria, intimes Dinieren mit Blick ins Grüne` |
| `.diner__eyebrow` | `Inbegrepen in het arrangement` | `Included in the package` | `Im Arrangement enthalten` |
| `.diner__title` | `Een heerlijk drie-gangen diner` | `A delicious three-course dinner` | `Ein köstliches Drei-Gänge-Dinner` |
| `.diner__sub` | `Na een avond in de wellness schuift u aan in ons restaurant. Vers bereid, seizoensgebonden, geen haast.` | `After an evening in the wellness centre, you join us in our restaurant. Freshly prepared, seasonal, no rush.` | `Nach einem Abend im Wellnessbereich nehmen Sie in unserem Restaurant Platz. Frisch zubereitet, saisonal, keine Eile.` |
| `.diner__cta` | `Boek het arrangement` | `Book the package` | `Das Arrangement buchen` |

### Footer

| Key | NL | EN | DE |
|-----|----|----|-----|
| Privacy link | `Privacy` | `Privacy` | `Datenschutz` |
| Voorwaarden link | `Algemene voorwaarden` | `Terms & conditions` | `AGB` |
| `.footer__copy` | `© 2026 Hotel Asteria · Onderdeel van Van der Sterren Hotels` | `© 2026 Hotel Asteria · Part of Van der Sterren Hotels` | `© 2026 Hotel Asteria · Teil von Van der Sterren Hotels` |

### Email Capture Popup

| Key | NL | EN | DE |
|-----|----|----|-----|
| `ec-overlay[aria-label]` | `Nieuwsbrief aanmelden` | `Newsletter sign-up` | `Newsletter anmelden` |
| `.ec-title` | `Gratis badjas, handdoek<br>&amp; bubbels op de kamer` | `Free bathrobe, towel<br>&amp; bubbles in your room` | `Kostenloser Bademantel, Handtuch<br>&amp; Sekt auf dem Zimmer` |
| `.ec-sub` | `Meld u aan voor de nieuwsbrief en ontvang het pakket bij uw eerste verblijf.` | `Sign up for the newsletter and receive the package on your first stay.` | `Melden Sie sich für den Newsletter an und erhalten Sie das Paket bei Ihrem ersten Aufenthalt.` |
| `.ec-error` | `Er ging iets mis. Probeer het opnieuw.` | `Something went wrong. Please try again.` | `Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.` |
| `#ecEmail[placeholder]` | `uw e-mailadres` | `your email address` | `Ihre E-Mail-Adresse` |
| `#ecSubmit` | `Aanmelden` | `Sign up` | `Anmelden` |
| `.ec-consent` text | `Door u aan te melden gaat u akkoord met onze` + link `privacyverklaring` + `. Afmelden kan altijd.` | `By signing up you agree to our` + link `privacy policy` + `. You can unsubscribe at any time.` | `Mit der Anmeldung stimmen Sie unserer` + link `Datenschutzerklärung` + ` zu. Abmeldung jederzeit möglich.` |
| `.ec-success-title` | `Check uw inbox` | `Check your inbox` | `Prüfen Sie Ihren Posteingang` |
| `.ec-success-sub` | `We hebben u een mail gestuurd. Open hem om uw aanmelding te bevestigen. Uw persoonlijke code staat daarin.` | `We've sent you an email. Open it to confirm your subscription. Your personal code is inside.` | `Wir haben Ihnen eine E-Mail geschickt. Öffnen Sie sie, um Ihre Anmeldung zu bestätigen. Ihr persönlicher Code ist darin enthalten.` |
| `.ec-spam-note` | `Geen mail ontvangen? Check uw spamfolder.` | `Didn't receive an email? Check your spam folder.` | `Keine E-Mail erhalten? Prüfen Sie Ihren Spam-Ordner.` |
| JS `showError()` reset | `submitBtn.textContent = 'Aanmelden'` | `submitBtn.textContent = 'Sign up'` | `submitBtn.textContent = 'Anmelden'` |

### Cookie Banner

| Key | NL | EN | DE |
|-----|----|----|-----|
| `.cookie-banner__text` | `Deze website gebruikt cookies voor een optimale ervaring.` | `This website uses cookies for an optimal experience.` | `Diese Website verwendet Cookies für ein optimales Erlebnis.` |
| Meer info link | `Meer info` | `More info` | `Mehr Infos` |
| `#cookieAccept` | `Akkoord` | `Accept` | `Akzeptieren` |

---

## Task 1: Prep NL page — hreflang + auto-detect + lang-nav wiring

**Files:**
- Modify: `wellness-arr-c.html`

- [ ] **Step 1: Add hreflang tags to `<head>`**

Find the `<!-- Canonical -->` block (around line 10) and add after it:
```html
<!-- Hreflang -->
<link rel="alternate" hreflang="nl" href="https://visit.asteria.nl/wellness-arr-c">
<link rel="alternate" hreflang="en" href="https://visit.asteria.nl/wellness-arr-c-en">
<link rel="alternate" hreflang="de" href="https://visit.asteria.nl/wellness-arr-c-de">
<link rel="alternate" hreflang="x-default" href="https://visit.asteria.nl/wellness-arr-c">
```

- [ ] **Step 2: Add auto-detect script before `<nav>`**

Find `<!-- ══ NAV` comment (around line 2504) and insert immediately before it:
```html
<!-- ══ TAALDETECTIE ══════════════════════════════════════════ -->
<script>
(function() {
  var stored = localStorage.getItem('asteria_lang');
  if (stored === 'en') { window.location.replace('/wellness-arr-c-en'); return; }
  if (stored === 'de') { window.location.replace('/wellness-arr-c-de'); return; }
  if (!stored) {
    var lang = (navigator.language || navigator.userLanguage || '').toLowerCase();
    if (lang.startsWith('de')) {
      localStorage.setItem('asteria_lang', 'de');
      window.location.replace('/wellness-arr-c-de');
    } else if (!lang.startsWith('nl')) {
      localStorage.setItem('asteria_lang', 'en');
      window.location.replace('/wellness-arr-c-en');
    }
  }
})();
</script>
```

- [ ] **Step 3: Wire lang-nav select at bottom of main `<script>` block**

Find the closing `</script>` tag (last one in the file, around line 4472) and add immediately before it:
```js
/* ── Taalwisselaar ── */
(function() {
  var sel = document.querySelector('.lang-nav');
  if (!sel) return;
  sel.value = 'nl';
  sel.addEventListener('change', function() {
    var v = sel.value;
    localStorage.setItem('asteria_lang', v);
    if (v === 'en') window.location.href = '/wellness-arr-c-en';
    else if (v === 'de') window.location.href = '/wellness-arr-c-de';
  });
})();
```

- [ ] **Step 4: Commit**

```bash
cd ~/Projects/asteria-pages
git add wellness-arr-c.html
git commit -m "feat: taaldetectie + hreflang op NL pagina"
```

---

## Task 2: Create EN version

**Files:**
- Create: `wellness-arr-c-en.html`

- [ ] **Step 1: Copy NL file as starting point**

```bash
cp ~/Projects/asteria-pages/wellness-arr-c.html ~/Projects/asteria-pages/wellness-arr-c-en.html
```

- [ ] **Step 2: Apply all EN translations**

Read `wellness-arr-c-en.html` in chunks and apply every EN translation from the Translation Reference above. Work section by section:

1. **Head:** `lang="nl"` → `lang="en"`, title, meta description, og:locale→`en_GB`, og:title, og:description, canonical href→`wellness-arr-c-en`, schema.org description + unitText
2. **Sticky CTA/card:** fab aria-label + text, card name/price-sub/btn, stickyCard aria-label
3. **Nav:** select `nl` option gets `selected` removed, `en` option gets `selected`; menu items per table; Boek nu→Book now; Bel→Call
4. **Hero:** location, h1, sub, cta, all 3 trust spans
5. **Arr-c:** section aria-label, rating aria-label + count, eyebrow, title, intro, all 6 features (name + desc + data-caption), price-from, price-sub, cta
6. **Reviews:** section aria-label, `#reviewsTotal` text, `.reviews__loading` text
7. **Wellness plattegrond:** section aria-label, intro label/title/sub, img alt, panel aria-label, close aria-label, panel label; replace entire `WP_ZONES` array with EN version from plan; update pin aria-label suffix string
8. **Kamertypes HTML:** section aria-label, eyebrow, title, sub, base badge/name/feats/img-alt, all room-row badges + delta texts, roomPopup aria-label
9. **ROOMS JS object:** replace all `name`, `desc`, `features`, `shortDesc`, `badge` fields with EN values from plan
10. **Room popup arrow aria-labels:** `'Vorige'`→`'Previous'`, `'Volgende'`→`'Next'`
11. **Booking popup HTML:** bk-overlay aria-label, bk-close aria-label, bk-title stap 1 + 2, all bk-summary labels, bk-selected-room label, bkChangeRoom, bkToStep2, bkDirectBook, bkBack (aria-label + text), bkConfirm, bkBackToRooms (aria-label + text)
12. **Booking popup JS:** `DAYS_NL`→EN days array, `MONTHS_NL`→EN months array; `' nacht'`→`' night'`; `' nachten'`→`' nights'`; both `btnToStep2.textContent` dynamic strings; `'meer info'`→`'more info'`; `'Selecteer deze kamer'`→`'Select this room'`; `'Vol'`→`'Full'`; `toLocaleString('nl-NL')`→`toLocaleString('en-GB')`; `' beoordelingen'`→`' reviews'`
13. **Custom datepicker JS:** `MONTH_NAMES`→EN array, `DAY_NAMES`→EN array
14. **Diner block:** section aria-label, bg aria-label, eyebrow, title, sub, cta
15. **Footer:** Algemene voorwaarden→Terms & conditions; copyright line
16. **Email capture:** overlay aria-label, ec-title, ec-sub, ec-error, ecEmail placeholder, ecSubmit, ec-consent text + link text, ec-success-title, ec-success-sub, ec-spam-note; JS `showError` reset: `'Aanmelden'`→`'Sign up'`
17. **Cookie banner:** text, Meer info→More info, Akkoord→Accept

- [ ] **Step 3: Add lang-nav wiring with `en` as selected, remove auto-detect**

Remove the auto-detect `<script>` block added in Task 1 (the one before `<!-- ══ NAV`).
Replace the lang-nav IIFE with:
```js
(function() {
  var sel = document.querySelector('.lang-nav');
  if (!sel) return;
  sel.value = 'en';
  sel.addEventListener('change', function() {
    var v = sel.value;
    localStorage.setItem('asteria_lang', v);
    if (v === 'nl') window.location.href = '/wellness-arr-c';
    else if (v === 'de') window.location.href = '/wellness-arr-c-de';
  });
})();
```

- [ ] **Step 4: Verify key elements in EN file**

Check:
- `<html lang="en">`
- `<link rel="canonical" href="https://visit.asteria.nl/wellness-arr-c-en">`
- All 4 hreflang tags present
- `og:locale` = `en_GB`
- Hero h1 contains "dinner" (not "diner")
- No auto-detect script present

- [ ] **Step 5: Commit**

```bash
git add wellness-arr-c-en.html
git commit -m "feat: Engelse vertaling wellness-arr-c"
```

---

## Task 3: Create DE version

**Files:**
- Create: `wellness-arr-c-de.html`

- [ ] **Step 1: Copy NL file as starting point**

```bash
cp ~/Projects/asteria-pages/wellness-arr-c.html ~/Projects/asteria-pages/wellness-arr-c-de.html
```

- [ ] **Step 2: Apply all DE translations**

Same sequence as Task 2 Step 2, using DE column from Translation Reference. Key differences vs EN:
- `lang="de"`, `og:locale="de_DE"`, canonical→`wellness-arr-c-de`
- `<select>` selected option: `de`
- WP_ZONES: use DE array from plan (Waldsauna, Salzsteinsauna, etc.)
- ROOMS: use DE object from plan (Comfort Zimmer, Brautsuite, etc.)
- `MONTH_NAMES` (datepicker): `['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']`
- `DAY_NAMES` (datepicker): `['Mo','Di','Mi','Do','Fr','Sa','So']`
- `DAYS_NL` (booking summary): `['So','Mo','Di','Mi','Do','Fr','Sa']`
- `MONTHS_NL` (booking summary): `['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez']`
- `' nacht'`→`' Nacht'`, `' nachten'`→`' Nächte'`
- `'meer info'`→`'mehr Info'`, `'Selecteer deze kamer'`→`'Dieses Zimmer wählen'`, `'Vol'`→`'Belegt'`
- `toLocaleString('de-DE')`, `' beoordelingen'`→`' Bewertungen'`
- `showError` reset: `'Aanmelden'`→`'Anmelden'`
- `'Vorige'`→`'Zurück'`, `'Volgende'`→`'Weiter'`

- [ ] **Step 3: Add lang-nav wiring with `de` as selected, remove auto-detect**

Remove auto-detect script. Replace lang-nav IIFE with:
```js
(function() {
  var sel = document.querySelector('.lang-nav');
  if (!sel) return;
  sel.value = 'de';
  sel.addEventListener('change', function() {
    var v = sel.value;
    localStorage.setItem('asteria_lang', v);
    if (v === 'nl') window.location.href = '/wellness-arr-c';
    else if (v === 'en') window.location.href = '/wellness-arr-c-en';
  });
})();
```

- [ ] **Step 4: Verify key elements in DE file**

Check:
- `<html lang="de">`
- `<link rel="canonical" href="https://visit.asteria.nl/wellness-arr-c-de">`
- `og:locale` = `de_DE`
- Hero h1 contains "Abendessen"
- No auto-detect script present

- [ ] **Step 5: Commit**

```bash
git add wellness-arr-c-de.html
git commit -m "feat: Duitse vertaling wellness-arr-c"
```

---

## Task 4: Test all 3 versions

**Files:** No changes (visual verification only)

- [ ] **Step 1: Wait for Cloudflare deploy**

```bash
sleep 40
```

- [ ] **Step 2: Screenshot EN desktop**

```js
// browser_run_code_unsafe:
await page.goto('https://visit.asteria.nl/wellness-arr-c-en');
await page.waitForTimeout(1500);
```
Then `browser_take_screenshot`. Verify English text in hero, "EN" selected in lang dropdown.

- [ ] **Step 3: Screenshot DE desktop**

```js
await page.goto('https://visit.asteria.nl/wellness-arr-c-de');
await page.waitForTimeout(1500);
```
Verify German text, "DE" selected in dropdown.

- [ ] **Step 4: Screenshot EN mobile**

```js
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/wellness-arr-c-en');
await page.waitForTimeout(1500);
```
Verify layout intact.

- [ ] **Step 5: Test lang switcher on EN page**

```js
// browser_evaluate on /wellness-arr-c-en:
document.querySelector('.lang-nav').value = 'de';
document.querySelector('.lang-nav').dispatchEvent(new Event('change'));
// Expected: redirect to /wellness-arr-c-de
```

- [ ] **Step 6: Verify NL auto-detect fires correctly**

Open browser console on `/wellness-arr-c` after clearing localStorage:
```js
localStorage.removeItem('asteria_lang');
location.reload();
// With en-US browser locale → should redirect to /wellness-arr-c-en
```

- [ ] **Step 7: Push to main**

```bash
git push origin main
```

---

## Notes

- Static fallback reviews (Dutch guest quotes) intentionally NOT translated — authentic reviews retain value in original language
- The Revinate form `vipStatus` value (`"Wellness nieuwsbrief"`) is a backend tag — not translated
- Price A/B test (€139,50 / €124,50, WELLNESSARRA / WELLNESS124) is unchanged — applies to all languages
- `data-track-cta` attributes are language-agnostic — unchanged
- `sessionStorage` keys (rooms-variant, ec_variant, price_variant) are shared across language versions — intentional
