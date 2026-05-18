# Design Spec — Wellness plattegrond Blender Fase 1: referentie + overtrekken

**Datum:** 2026-05-18
**Doel:** Technische tekening overtrekken in Blender als schone 3D-geometrie

---

## Scope Fase 1

Import van `wellness-plattegrond.png` als referentie in Blender, gevolgd door het handmatig overtrekken van alle ruimtes als mesh-objecten. Fase 1 levert een geometrisch correcte wireframe-plattegrond op — geen materialen, geen render.

Fase 2 (apart): materialen + flat-kleur per zone, render top-down + isometrisch.

---

## Blender-scène setup

- **Engine:** Eevee (snelle preview)
- **Units:** Millimeters (tekening heeft maten in mm)
- **Camera:** Orthografisch, exact top-down (Z-as omlaag), rotatie (90°, 0°, 0°)
- **Viewport:** Top orthografisch tijdens het overtrekken

---

## Referentie-afbeelding

- Bestand: `/Users/bartvandersterren/Projects/asteria-pages/wellness-plattegrond.png`
- Importeren als **Image Plane** op Z=0, gecentreerd op origin
- Schaal: afmeten op tekening — breedte plattegrond ~27.000mm (schatting op basis van maten)
- Lock op positie, niet selecteerbaar tijdens modelleren (layer apart)

---

## Overtrek-strategie

### Buitenwand
- Één gesloten mesh: `Buitenwand`
- Vertices op alle buitenhoeken van het gebouw
- Extrude naar Z=300mm (symbolische muurhoogte voor fase 2)

### Ruimtes (afzonderlijke mesh-objecten)
Elke ruimte = eigen object, benoemd:

| Object naam | Ruimte |
|-------------|--------|
| `Ruimte_Entree` | Entree |
| `Ruimte_Omkleed` | Omkleed + Lockers |
| `Ruimte_Sanitair` | Toiletten + Douche links |
| `Ruimte_Techniek` | Techniek |
| `Ruimte_Stoomdouche` | Stoomdouche |
| `Ruimte_BadZone` | IJs-/dompelbad + Kruidenbad + Voetenbaden |
| `Ruimte_Sauna1` | Sauna 1 (Fins) |
| `Ruimte_Sauna2` | Sauna 2 (Bio/Wave) |
| `Ruimte_Sauna3` | Sauna 3 (Wave) |
| `Ruimte_Sauna4` | Infrarood sauna links |
| `Ruimte_InfraroodSauna` | Infrarood sauna midden |
| `Ruimte_Pantry` | Pantry |
| `Ruimte_Gym` | Gym / Fitness |
| `Ruimte_Rustruimte` | Rustruimte / Lounge |
| `Ruimte_Verkeersruimte` | Verkeersruimte (corridor) |

### Vloervlak
- Plat vlak (`Vloer`) onder alle ruimtes — één mesh, Z=0

---

## Eindresultaat Fase 1

- Blender-bestand opgeslagen als `wellness-plattegrond-v1.blend` in projectroot
- Alle ruimtes afzonderlijk benoemd en selecteerbaar
- Geometrie klopt visueel met de referentie-PNG
- Klaar voor Fase 2: materialen + render

---

## Openstaande punten

- Exacte schaal wordt bepaald door maten op de tekening (3509, 3522, 3460mm zichtbaar)
- Meubilair (ligbedden, sauna-banken) wordt in Fase 2 optioneel toegevoegd
