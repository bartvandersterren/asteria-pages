# Wellness Plattegrond — AI Illustratie Prompt

## Strategie
- Plattegrond PDF als **enige** referentie-input (geen stijl-referentieafbeeldingen)
- Stijl en materialen volledig in tekst beschreven op basis van de referentiefoto's
- Layout zo gedetailleerd mogelijk beschreven per zone

---

## Prompt v3

Isometric cutaway architectural illustration of a luxury hotel wellness center, viewed directly from above with roof removed. Warm editorial illustration style — luxury spa brochure quality. No text, no labels, no numbers, no annotations anywhere in the image.

**Materials (match these precisely):**
- Floors throughout: large-format light travertine/limestone tiles, warm off-white with subtle veining
- Walls: smooth plaster, warm white
- Sauna exteriors (outside walls): dark near-black walnut wood cladding
- Sauna interiors: horizontal bench slats in light Nordic pine/aspen, warm amber LED strip lighting running along bench levels, glowing from within
- Steam cabin: dark blue-grey mosaic tile walls, heavy glass door
- Bath surrounds: same travertine stone as floor
- Round baths/foot baths: tiled basins with clear blue-turquoise water, slight steam rising
- Herbal bath: oval basin, warm sage-green water, stone surround
- Plant walls: lush vertical garden with dense tropical foliage — monstera, ferns, philodendron — near the bathing area
- Relaxation loungers: white/cream padded sun loungers, light wood frames
- Gym equipment: dark matte steel machines, black rubber floor mat areas

**Layout — strictly follow the reference floor plan:**

Building footprint approximately 2:1 wide-to-tall.

Top-left corner — Arrival & Changing:
Entrance door with arc swing. Changing room with tall wooden locker cabinets. Separate toilet cubicles and shower stalls.

Top-center — Bathing zone:
Infrared sauna cabin (rectangular, dark wood exterior, amber glow inside). Then moving right: circular room with three round foot bath basins set into travertine floor, with a dense vertical plant wall backdrop.

Top-right — Sauna cluster:
Four saunas: two side-by-side (Sauna 2 + 3) with horizontal pine bench slats and amber LED glow, and two more (Sauna 1 + 4) on the far right with glass front panels. All have dark walnut exterior cladding.

Center — Water experiences:
Oval cold plunge/ice bath with bright cold blue water. Below it: oval herbal bath with warm sage-green water. To the left: steam cabin with dark blue-grey mosaic tiles and glass door. Experience shower with rain ceiling panel next to it. Mosaic tile bench seating.

Left-center — Circulation:
Wide open circulation corridor. Small enclosed technical room.

Bottom-left — Gym:
Large open fitness area. Treadmills, cable machines, weight rack, rowing machine. Black rubber floor mat zones. A few plants in corners.

Bottom-right — Rest area:
Large relaxation lounge. Rows of white padded sun loungers. Cluster of round lounge chairs with low travertine side tables. Soft indirect lighting. Small pantry counter in far corner.

**Lighting:**
Soft directional light from upper-right. Warm amber glow emanates from all sauna interiors. Cold blue light reflects off ice bath water. Gentle drop shadows on all walls to create depth and room separation.

**Style:** High-detail editorial illustration, 4K quality. Distinct room separation through wall thickness variation and subtle color temperature differences. No human figures. Photorealistic materials, illustrative composition.

---

## Higgsfield instellingen
- Model: beste beschikbare (Flux Pro of vergelijkbaar)
- Reference image: `plattegrond-v2-preview.png` (hoge-res PNG van de PDF) — weight zo hoog mogelijk (~0.75-0.85)
- **Geen** extra stijl-referentieafbeeldingen — stijl zit volledig in de tekst

---

## Referentiefoto's geanalyseerd (niet uploaden, wel beschreven in prompt)
- `01-badareal-overzicht.jpg` — lichte travertijn vloer, overzicht badgebied
- `02-jacuzzi-verticaletuinen.jpg` — weelderige verticale plantenwand bij rond bad
- `03-badareal-rondbad-voetenbad.jpg` — ronde bassins, steen surround, voetenbaden
- `04-sauna-led.jpg` — licht Nordic hout, LED strip langs bankniveaus
- `08-sauna-donkerhout-bos.jpg` — bijna zwart walnoot exterieur, groot raam
- `09-stoomcabine.jpg` — donker blauw-grijs mozaïek, glazen deur

---

## Wat niet werkte (v1/v2)
- Stijl-referentieafbeeldingen uploaden → model verliest layout-accuraatheid
- Fix: stijl en materialen volledig in tekst, plattegrond als enige visuele input
