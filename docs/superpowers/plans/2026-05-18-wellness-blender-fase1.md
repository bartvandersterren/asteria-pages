# Wellness Plattegrond Blender Fase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Importeer de technische wellness-plattegrond als referentie in Blender en overtrek alle ruimtes als benoemde mesh-objecten.

**Architecture:** Blender MCP via Python-code. Referentie-afbeelding als Image Plane op Z=0, buitenwanden en ruimtes als afzonderlijke mesh-objecten. Verificatie via viewport screenshots na elke taak.

**Tech Stack:** Blender 4.4, Blender MCP (mcp__blender__execute_blender_code, mcp__blender__get_viewport_screenshot)

---

### Task 1: Scène opschonen en setup

**Files:**
- Blender scene (in-memory, opslaan aan einde als `wellness-plattegrond-v1.blend` in projectroot)

- [ ] **Stap 1: Verwijder default objecten en stel units in op mm**

```python
import bpy

# Verwijder alles
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Units instellen op millimeters
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 0.001
bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'

print("Scene geleegd, units: mm")
```

- [ ] **Stap 2: Verifieer via scene info**

Gebruik `mcp__blender__get_scene_info` — verwacht: lege scene, unit_scale 0.001

- [ ] **Stap 3: Stel orthografische top-down camera in**

```python
import bpy
import math

# Camera aanmaken
bpy.ops.object.camera_add(location=(0, 0, 10000))
cam = bpy.context.active_object
cam.name = 'Camera_TopDown'
cam.rotation_euler = (0, 0, 0)  # Kijkt recht naar beneden (Z-as)
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 30000  # ~30m breed (aanpassen na referentie laden)

# Maak actieve camera
bpy.context.scene.camera = cam

print("Camera aangemaakt: orthografisch top-down")
```

- [ ] **Stap 4: Screenshot viewport (top-down view)**

Gebruik `mcp__blender__get_viewport_screenshot` — controleer dat viewport leeg en correct is

---

### Task 2: Referentie-afbeelding importeren

- [ ] **Stap 1: Importeer wellness-plattegrond.png als Image Plane**

```python
import bpy

# Zorg dat de Image Import add-on actief is
bpy.ops.preferences.addon_enable(module='io_import_images_as_planes')

# Importeer als image plane
bpy.ops.import_image.to_plane(
    files=[{"name": "wellness-plattegrond.png"}],
    directory="/Users/bartvandersterren/Projects/asteria-pages/",
    align_axis='Z+',
    height=1.0,  # wordt na import geschaald
    use_shadeless=True,
)

img_plane = bpy.context.active_object
img_plane.name = 'Referentie_Plattegrond'

print(f"Image plane aangemaakt: {img_plane.name}, dimensies: {img_plane.dimensions}")
```

- [ ] **Stap 2: Schaal afbeelding op basis van bekende maat**

De tekening toont "3509" mm als breedte van de voetenbaden-zone. We schalen zodat die maat klopt. Eerst meten we de pixel-breedte van de hele tekening vs die zone, dan passen we de schaal aan.

Schatting op basis van tekening: totale breedte ~27.000mm.

```python
import bpy

img_plane = bpy.data.objects['Referentie_Plattegrond']

# Huidige breedte opvragen
current_width = img_plane.dimensions.x
print(f"Huidige breedte: {current_width}")

# Doelbreedte in mm (Blender units bij scale=0.001 → meters intern)
# 27000mm = 27m = 27 Blender units (bij mm-setup)
target_width_mm = 27000
scale_factor = target_width_mm / (current_width * 1000)  # current is in meters

img_plane.scale = (scale_factor, scale_factor, 1)
bpy.ops.object.transform_apply(scale=True)

print(f"Geschaald met factor {scale_factor:.4f}, nieuwe breedte: {img_plane.dimensions.x * 1000:.0f}mm")
```

- [ ] **Stap 3: Vergrendel referentie-plane (niet selecteerbaar)**

```python
import bpy

img_plane = bpy.data.objects['Referentie_Plattegrond']
img_plane.hide_select = True
img_plane.location.z = -10  # Iets onder de overtrek-meshes

print("Referentie vergrendeld en naar Z=-10 verplaatst")
```

- [ ] **Stap 4: Screenshot — referentie zichtbaar in viewport**

Gebruik `mcp__blender__get_viewport_screenshot` en controleer dat de plattegrond zichtbaar is als achtergrond.

---

### Task 3: Buitenwanden overtrekken

- [ ] **Stap 1: Maak buitenwand-mesh op basis van plattegrond omtrek**

De buitenomtrek van het gebouw is een rechthoek met twee uitstulpingen (entreegebied links, en de ronde uitbouw rechtsonder). Coördinaten zijn in mm, geschat op basis van de referentie.

```python
import bpy
import bmesh

# Maak nieuw mesh-object
mesh = bpy.data.meshes.new('Buitenwand_Mesh')
obj = bpy.data.objects.new('Buitenwand', mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

bm = bmesh.new()

# Buitenomtrek vertices (mm, Z=0, geschat — bijstellen na visuele check)
# Volgorde: linksboven → rechtsboven → rechtsonder → linksonder (tegen klok in)
verts_mm = [
    (-13500, 4800, 0),   # linksboven
    (13500, 4800, 0),    # rechtsboven
    (13500, -5500, 0),   # rechtsonder
    (-13500, -5500, 0),  # linksonder
]

verts = [bm.verts.new((x, y, z)) for x, y, z in verts_mm]
bm.faces.new(verts)

bm.to_mesh(mesh)
bm.free()

# Extrude naar Z=300mm
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value": (0, 0, 300)}
)
bpy.ops.object.mode_set(mode='OBJECT')

print("Buitenwand aangemaakt")
```

- [ ] **Stap 2: Screenshot — check overlap met referentie**

`mcp__blender__get_viewport_screenshot` — buitenwand moet de omtrek van de tekening volgen.

- [ ] **Stap 3: Pas vertices bij indien nodig**

Indien de omtrek niet klopt, aanpassen via Python (vertices herpositioneren). Herhaal screenshot.

---

### Task 4: Saunasectie overtrekken (rechtsboven)

- [ ] **Stap 1: Maak ruimtes voor de 4 saunas**

```python
import bpy
import bmesh

def maak_ruimte(naam, verts_mm):
    mesh = bpy.data.meshes.new(f'{naam}_Mesh')
    obj = bpy.data.objects.new(naam, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for x, y, z in verts_mm]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()

    # Extrude 250mm omhoog
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 250)})
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.location.z = 5  # Boven de referentie
    return obj

# Sauna 1 (Fins, grote sauna rechtsmidden)
maak_ruimte('Ruimte_Sauna1', [
    (7000, 0, 0),
    (10500, 0, 0),
    (10500, 3500, 0),
    (7000, 3500, 0),
])

# Sauna 2 (Bio/Wave, rechtsboven midden)
maak_ruimte('Ruimte_Sauna2', [
    (5500, 2500, 0),
    (9000, 2500, 0),
    (9000, 4800, 0),
    (5500, 4800, 0),
])

# Sauna 3 (Wave, rechtsbovenhoek)
maak_ruimte('Ruimte_Sauna3', [
    (9000, 2500, 0),
    (13500, 2500, 0),
    (13500, 4800, 0),
    (9000, 4800, 0),
])

# Sauna 4 (Infrarood, rechts)
maak_ruimte('Ruimte_Sauna4', [
    (10500, 0, 0),
    (13500, 0, 0),
    (13500, 2500, 0),
    (10500, 2500, 0),
])

print("4 saunaruimtes aangemaakt")
```

- [ ] **Stap 2: Screenshot — check posities saunas**

`mcp__blender__get_viewport_screenshot` — controleer dat de ruimtes overeenkomen met de tekening.

---

### Task 5: Badzone + centrale ruimtes overtrekken

- [ ] **Stap 1: Voetenbaden, IJs-/dompelbad, Kruidenbad, Stoomdouche**

```python
import bpy
import bmesh

def maak_ruimte(naam, verts_mm, z_offset=5):
    mesh = bpy.data.meshes.new(f'{naam}_Mesh')
    obj = bpy.data.objects.new(naam, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for x, y, z in verts_mm]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 250)})
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.location.z = z_offset
    return obj

# Infrarood sauna (midden-boven)
maak_ruimte('Ruimte_InfraroodSauna', [
    (1500, 1500, 0),
    (4800, 1500, 0),
    (4800, 4800, 0),
    (1500, 4800, 0),
])

# Voetenbaden (ronde zone — benaderen als octagon)
import math
cx, cy, r = 3500, 0, 1800
verts_voet = [(cx + r*math.cos(math.radians(i*45)), cy + r*math.sin(math.radians(i*45)), 0) for i in range(8)]
maak_ruimte('Ruimte_Voetenbaden', verts_voet)

# IJs-/dompelbad
maak_ruimte('Ruimte_IJsDompelbad', [
    (0, -500, 0),
    (3000, -500, 0),
    (3000, 1500, 0),
    (0, 1500, 0),
])

# Kruidenbad
maak_ruimte('Ruimte_Kruidenbad', [
    (0, -2000, 0),
    (3000, -2000, 0),
    (3000, -500, 0),
    (0, -500, 0),
])

# Stoomdouche
maak_ruimte('Ruimte_Stoomdouche', [
    (-2000, -1500, 0),
    (0, -1500, 0),
    (0, 1500, 0),
    (-2000, 1500, 0),
])

# Belevingsdouche (kleine ruimte)
maak_ruimte('Ruimte_Belevingsdouche', [
    (3000, -2500, 0),
    (5000, -2500, 0),
    (5000, -1000, 0),
    (3000, -1000, 0),
])

print("Badzone + centrale ruimtes aangemaakt")
```

- [ ] **Stap 2: Screenshot — check badzone posities**

---

### Task 6: Entree, omkleed, sanitair, techniek overtrekken

- [ ] **Stap 1: Westelijk gedeelte (links)**

```python
import bpy
import bmesh

def maak_ruimte(naam, verts_mm, z_offset=5):
    mesh = bpy.data.meshes.new(f'{naam}_Mesh')
    obj = bpy.data.objects.new(naam, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for x, y, z in verts_mm]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 250)})
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.location.z = z_offset
    return obj

# Entree
maak_ruimte('Ruimte_Entree', [
    (-13500, 1500, 0),
    (-9500, 1500, 0),
    (-9500, 4800, 0),
    (-13500, 4800, 0),
])

# Omkleed + Lockers
maak_ruimte('Ruimte_Omkleed', [
    (-9500, 1500, 0),
    (-5500, 1500, 0),
    (-5500, 4800, 0),
    (-9500, 4800, 0),
])

# Sanitair links (douche + toilet)
maak_ruimte('Ruimte_Sanitair', [
    (-13500, -1500, 0),
    (-9000, -1500, 0),
    (-9000, 1500, 0),
    (-13500, 1500, 0),
])

# Toilet + douche midden
maak_ruimte('Ruimte_ToiletDouche', [
    (-6500, -500, 0),
    (-3500, -500, 0),
    (-3500, 1500, 0),
    (-6500, 1500, 0),
])

# Techniek
maak_ruimte('Ruimte_Techniek', [
    (-5500, -2500, 0),
    (-2000, -2500, 0),
    (-2000, -500, 0),
    (-5500, -500, 0),
])

# Verkeersruimte (corridor midden-links)
maak_ruimte('Ruimte_Verkeersruimte', [
    (-9000, -1500, 0),
    (-2000, -1500, 0),
    (-2000, 1500, 0),
    (-9000, 1500, 0),
])

print("Entree, omkleed, sanitair, techniek aangemaakt")
```

- [ ] **Stap 2: Screenshot — check westelijk gedeelte**

---

### Task 7: Gym, rustruimte, pantry overtrekken

- [ ] **Stap 1: Zuidelijk gedeelte**

```python
import bpy
import bmesh

def maak_ruimte(naam, verts_mm, z_offset=5):
    mesh = bpy.data.meshes.new(f'{naam}_Mesh')
    obj = bpy.data.objects.new(naam, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for x, y, z in verts_mm]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 250)})
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.location.z = z_offset
    return obj

# Gym / Fitness (groot vlak linksonder)
maak_ruimte('Ruimte_Gym', [
    (-13500, -5500, 0),
    (0, -5500, 0),
    (0, -2500, 0),
    (-13500, -2500, 0),
])

# Rustruimte / Lounge (rechtsonder)
maak_ruimte('Ruimte_Rustruimte', [
    (0, -5500, 0),
    (13500, -5500, 0),
    (13500, -2500, 0),
    (0, -2500, 0),
])

# Pantry
maak_ruimte('Ruimte_Pantry', [
    (8000, -500, 0),
    (13500, -500, 0),
    (13500, -2500, 0),
    (8000, -2500, 0),
])

print("Gym, rustruimte, pantry aangemaakt")
```

- [ ] **Stap 2: Screenshot — check zuidelijk gedeelte**

---

### Task 8: Visuele check en bijstellen

- [ ] **Stap 1: Maak referentie weer zichtbaar (tijdelijk)**

```python
import bpy

ref = bpy.data.objects.get('Referentie_Plattegrond')
if ref:
    ref.hide_select = False
    ref.location.z = 0
    ref.hide_render = False
print("Referentie tijdelijk zichtbaar op Z=0")
```

- [ ] **Stap 2: Screenshot overlay — mesh boven referentie**

`mcp__blender__get_viewport_screenshot` — controleer of alle ruimtes overeenkomen met de tekening. Noteer afwijkingen.

- [ ] **Stap 3: Corrigeer afwijkende vertices**

Voor elke ruimte die niet klopt:

```python
import bpy

obj = bpy.data.objects['Ruimte_Naam']  # vervang met juiste naam
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
# Gebruik bmesh om specifieke vertices te verplaatsen
import bmesh
bm = bmesh.from_edit_mesh(obj.data)
# Selecteer vertex op index i:
bm.verts.ensure_lookup_table()
bm.verts[0].co.x = nieuwe_x  # in mm
bm.verts[0].co.y = nieuwe_y
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
```

- [ ] **Stap 4: Vergrendel referentie opnieuw**

```python
import bpy
ref = bpy.data.objects.get('Referentie_Plattegrond')
if ref:
    ref.hide_select = True
    ref.location.z = -10
print("Referentie vergrendeld")
```

---

### Task 9: Opslaan

- [ ] **Stap 1: Sla het Blender-bestand op**

```python
import bpy
bpy.ops.wm.save_as_mainfile(
    filepath="/Users/bartvandersterren/Projects/asteria-pages/wellness-plattegrond-v1.blend"
)
print("Opgeslagen als wellness-plattegrond-v1.blend")
```

- [ ] **Stap 2: Eindscreenshot — volledig overzicht**

`mcp__blender__get_viewport_screenshot` — documenteer de eindstand van Fase 1.

- [ ] **Stap 3: Commit**

```bash
git add docs/superpowers/specs/2026-05-18-wellness-blender-plattegrond-fase1-design.md
git add docs/superpowers/plans/2026-05-18-wellness-blender-fase1.md
git add wellness-plattegrond-v1.blend
git commit -m "feat: wellness plattegrond Blender Fase 1 — referentie + geometrie"
```

---

## Notities voor Fase 2

- Alle coördinaten zijn schattingen — Task 8 is het kritieke bijstelmoment
- Na Fase 1 zijn de exacte vertices bekend → pin-percentages voor hotspot-blok kunnen worden afgeleid
- Fase 2: materialen (flat kleur per zone), licht, render top-down + isometrisch
