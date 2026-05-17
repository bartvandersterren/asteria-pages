# Image Generation Test — Asteria Wellness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Schrijf en draai een Node.js testscript dat 5 AI-modellen aanroept met identieke input (prompt + 4 referentiefoto's) en de outputs opslaat als PNG's + een vergelijkings-HTML pagina.

**Architecture:** Één script `test-image-gen.js` in de projectroot. Laadt referentiebeelden als base64, roept OpenRouter (chat completions) en xAI (images/generations) sequentieel aan, parseert responses, slaat images op in `test-output/`, genereert vergelijkings-HTML.

**Tech Stack:** Node.js (built-in fetch), fs, path — geen externe dependencies nodig.

---

## Bestandsstructuur

```
test-image-gen.js          # Hoofdscript — alle logica
test-output/               # Gegenereerde afbeeldingen (gitignored)
  <model-naam>.png         # Output per model
  vergelijking.html        # Side-by-side vergelijkingspagina
```

---

### Task 1: Setup — gitignore + output directory

**Files:**
- Modify: `.gitignore`

- [ ] **Stap 1: Voeg test-output/ toe aan .gitignore**

Open `.gitignore` (of maak aan als het niet bestaat) en voeg toe:

```
# Image generation test output
test-output/
test-image-gen.js
```

- [ ] **Stap 2: Maak test-output/ directory aan**

```bash
mkdir -p test-output
```

- [ ] **Stap 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore test-output en testscript"
```

---

### Task 2: Scriptskelet + constanten

**Files:**
- Create: `test-image-gen.js`

- [ ] **Stap 1: Schrijf het skelet met PROMPT, MODELS en main()**

Maak `test-image-gen.js` aan met de volgende inhoud:

```javascript
import fs from 'fs';
import path from 'path';

const PROMPT = `A couple relaxing together in a Finnish sauna at a luxury four-star hotel in the Netherlands.
They are seated side by side on a wooden bench, eyes closed or softly looking at each other.
White towels draped over them. The sauna interior has warm golden light from the heating element,
wooden walls and benches, subtle steam in the air.

Photography style: editorial hotel photography, warm golden tones, shallow depth of field,
soft natural-feeling light, authentic moment — not posed or stock-photo.
35mm lens, horizontal composition. The mood is intimate, peaceful, luxurious.

Match the visual style and interior details from the reference images provided.
Do not add logos, text, or unrealistic elements.`;

const REFERENCE_PATHS = [
  '/Users/bartvandersterren/Documents/Asteria Fotobank/P1046696.jpg',
  '/Users/bartvandersterren/Documents/Asteria Fotobank/P1046715.jpg',
  '/Users/bartvandersterren/Documents/Asteria Fotobank/P1057456.jpg',
  '/Users/bartvandersterren/Documents/Asteria Fotobank/P1057468.jpg',
];

const OPENROUTER_MODELS = [
  'openai/gpt-5-image',
  'openai/gpt-5.4-image-2',
  'google/gemini-3-pro-image-preview',
  'google/gemini-3.1-flash-image-preview',
];

const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY;
const XAI_KEY = process.env.XAI_API_KEY;

async function main() {
  console.log('=== Asteria Image Generation Test ===\n');
  // Tasks worden hier aangeroepen
}

main().catch(console.error);
```

- [ ] **Stap 2: Verifieer dat het script startbaar is**

```bash
node test-image-gen.js
```

Verwacht output:
```
=== Asteria Image Generation Test ===
```

---

### Task 3: Referentiebeelden laden als base64

**Files:**
- Modify: `test-image-gen.js`

- [ ] **Stap 1: Voeg loadReferences() toe na de constanten**

```javascript
function loadReferences() {
  return REFERENCE_PATHS.map(filePath => {
    const data = fs.readFileSync(filePath);
    const base64 = data.toString('base64');
    return `data:image/jpeg;base64,${base64}`;
  });
}
```

- [ ] **Stap 2: Test de functie in main()**

Vervang de body van `main()` tijdelijk:

```javascript
async function main() {
  console.log('=== Asteria Image Generation Test ===\n');
  const refs = loadReferences();
  console.log(`Referenties geladen: ${refs.length} stuks`);
  refs.forEach((r, i) => console.log(`  Ref ${i + 1}: ${r.length} chars`));
}
```

- [ ] **Stap 3: Draai en verifieer**

```bash
node test-image-gen.js
```

Verwacht output (getallen variëren per bestandsgrootte):
```
=== Asteria Image Generation Test ===
Referenties geladen: 4 stuks
  Ref 1: 4521384 chars
  Ref 2: 3987234 chars
  Ref 3: 5102938 chars
  Ref 4: 4891234 chars
```

Als een bestand niet gevonden wordt: `Error: ENOENT: no such file or directory` — controleer het pad in REFERENCE_PATHS.

---

### Task 4: OpenRouter aanroepen + response parsen

**Files:**
- Modify: `test-image-gen.js`

- [ ] **Stap 1: Voeg callOpenRouter() toe**

```javascript
async function callOpenRouter(model, refs) {
  const start = Date.now();
  console.log(`  Aanroepen: ${model}...`);

  const content = [
    { type: 'text', text: PROMPT },
    ...refs.map(url => ({ type: 'image_url', image_url: { url } })),
  ];

  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENROUTER_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content }],
    }),
  });

  const data = await response.json();
  const elapsed = ((Date.now() - start) / 1000).toFixed(1);

  if (!response.ok) {
    throw new Error(`API fout (${response.status}): ${JSON.stringify(data)}`);
  }

  const imageBase64 = extractImageBase64(data);
  console.log(`  Klaar in ${elapsed}s`);
  return imageBase64;
}
```

- [ ] **Stap 2: Voeg extractImageBase64() toe**

OpenRouter image models retourneren de afbeelding op twee manieren afhankelijk van het model:
- Als `data:image/png;base64,...` string in `choices[0].message.content` (string)
- Als content array met `{type: 'image_url', image_url: {url: 'data:...'}}` item

```javascript
function extractImageBase64(data) {
  const msg = data.choices?.[0]?.message;
  if (!msg) throw new Error(`Onverwacht response formaat: ${JSON.stringify(data).slice(0, 200)}`);

  // Formaat 1: content is een string met data URL
  if (typeof msg.content === 'string') {
    const match = msg.content.match(/data:image\/[^;]+;base64,([A-Za-z0-9+/=]+)/);
    if (match) return match[1];
    // Sommige modellen retourneren alleen base64 zonder data: prefix
    if (/^[A-Za-z0-9+/=]{100,}$/.test(msg.content.trim())) return msg.content.trim();
    throw new Error(`Geen afbeelding gevonden in string content: ${msg.content.slice(0, 200)}`);
  }

  // Formaat 2: content is een array
  if (Array.isArray(msg.content)) {
    for (const block of msg.content) {
      if (block.type === 'image_url') {
        const url = block.image_url?.url ?? '';
        const match = url.match(/data:image\/[^;]+;base64,([A-Za-z0-9+/=]+)/);
        if (match) return match[1];
      }
      if (block.type === 'image' && block.source?.data) {
        return block.source.data;
      }
    }
  }

  throw new Error(`Geen afbeelding gevonden in response: ${JSON.stringify(data).slice(0, 400)}`);
}
```

- [ ] **Stap 3: Voeg saveImage() toe**

```javascript
function saveImage(base64, filename) {
  const outputPath = path.join('test-output', filename);
  fs.writeFileSync(outputPath, Buffer.from(base64, 'base64'));
  console.log(`  Opgeslagen: ${outputPath}`);
  return outputPath;
}
```

---

### Task 5: xAI Aurora aanroepen

**Files:**
- Modify: `test-image-gen.js`

Opmerking: Aurora ondersteunt mogelijk geen image input. We testen eerst zonder referenties, en bij succes eventueel met.

- [ ] **Stap 1: Voeg callXAI() toe**

```javascript
async function callXAI() {
  const start = Date.now();
  console.log('  Aanroepen: xai/aurora...');

  const response = await fetch('https://api.x.ai/v1/images/generations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${XAI_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'aurora',
      prompt: PROMPT,
      n: 1,
      response_format: 'b64_json',
    }),
  });

  const data = await response.json();
  const elapsed = ((Date.now() - start) / 1000).toFixed(1);

  if (!response.ok) {
    throw new Error(`xAI API fout (${response.status}): ${JSON.stringify(data)}`);
  }

  const base64 = data.data?.[0]?.b64_json;
  if (!base64) throw new Error(`Geen afbeelding in xAI response: ${JSON.stringify(data).slice(0, 200)}`);

  console.log(`  Klaar in ${elapsed}s`);
  return base64;
}
```

---

### Task 6: Main runner + foutafhandeling per model

**Files:**
- Modify: `test-image-gen.js`

- [ ] **Stap 1: Vervang de body van main() met de volledige runner**

```javascript
async function main() {
  console.log('=== Asteria Image Generation Test ===\n');

  if (!OPENROUTER_KEY) { console.error('OPENROUTER_API_KEY niet gevonden'); process.exit(1); }
  if (!XAI_KEY) { console.error('XAI_API_KEY niet gevonden'); process.exit(1); }

  const refs = loadReferences();
  console.log(`Referenties geladen: ${refs.length} stuks\n`);

  const results = [];

  // OpenRouter modellen
  for (const model of OPENROUTER_MODELS) {
    const modelShort = model.replace('/', '-');
    console.log(`[${modelShort}]`);
    try {
      const base64 = await callOpenRouter(model, refs);
      const outputPath = saveImage(base64, `${modelShort}.png`);
      results.push({ model, status: 'ok', path: outputPath });
    } catch (err) {
      console.error(`  FOUT: ${err.message}`);
      results.push({ model, status: 'error', error: err.message });
    }
    console.log('');
  }

  // xAI Aurora
  console.log('[xai-aurora]');
  try {
    const base64 = await callXAI();
    const outputPath = saveImage(base64, 'xai-aurora.png');
    results.push({ model: 'xai/aurora', status: 'ok', path: outputPath });
  } catch (err) {
    console.error(`  FOUT: ${err.message}`);
    results.push({ model: 'xai/aurora', status: 'error', error: err.message });
  }
  console.log('');

  generateComparison(results);
  console.log('\nKlaar! Open test-output/vergelijking.html in je browser.');
}
```

---

### Task 7: Vergelijkings-HTML genereren

**Files:**
- Modify: `test-image-gen.js`

- [ ] **Stap 1: Voeg generateComparison() toe**

```javascript
function generateComparison(results) {
  const cards = results.map(r => {
    if (r.status === 'error') {
      return `
        <div class="card error">
          <div class="model-name">${r.model}</div>
          <div class="error-msg">FOUT: ${r.error}</div>
        </div>`;
    }
    const filename = path.basename(r.path);
    return `
      <div class="card">
        <div class="model-name">${r.model}</div>
        <img src="${filename}" alt="${r.model}" />
        <div class="score-grid">
          <label>Stijlmatch <input type="range" min="1" max="5" value="3"></label>
          <label>Interieur <input type="range" min="1" max="5" value="3"></label>
          <label>Personen <input type="range" min="1" max="5" value="3"></label>
          <label>Bruikbaar <input type="range" min="1" max="5" value="3"></label>
        </div>
      </div>`;
  }).join('\n');

  const html = `<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <title>AI Image Generation — Asteria Vergelijking</title>
  <style>
    body { font-family: system-ui; background: #f0efed; padding: 32px; margin: 0; }
    h1 { font-size: 20px; margin-bottom: 24px; color: #1a1a1a; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 24px; }
    .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .card img { width: 100%; display: block; }
    .model-name { padding: 12px 16px; font-size: 13px; font-weight: 600; color: #c23435; background: #faf9f8; border-bottom: 1px solid #eee; }
    .score-grid { padding: 12px 16px; display: grid; gap: 8px; }
    .score-grid label { font-size: 12px; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
    .score-grid input[type=range] { flex: 1; }
    .error { border: 2px solid #c23435; }
    .error-msg { padding: 16px; color: #c23435; font-size: 13px; }
    .refs { margin-bottom: 32px; }
    .refs h2 { font-size: 14px; margin-bottom: 12px; }
    .refs-grid { display: flex; gap: 12px; }
    .refs-grid img { width: 200px; height: 133px; object-fit: cover; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>Asteria — AI Image Generation Vergelijking</h1>
  <p style="font-size:13px;color:#666;margin-bottom:24px;">Testscène: koppel in Finse sauna, avondsfeer. Identieke prompt + 4 referenties per model.</p>
  <div class="grid">
    ${cards}
  </div>
</body>
</html>`;

  fs.writeFileSync('test-output/vergelijking.html', html);
  console.log('Vergelijkingspagina gegenereerd: test-output/vergelijking.html');
}
```

---

### Task 8: Volledig draaien + evalueren

**Files:**
- Read: `test-output/vergelijking.html` (in browser)

- [ ] **Stap 1: Draai het script**

```bash
node test-image-gen.js
```

Verwacht output (modellen sequentieel):
```
=== Asteria Image Generation Test ===

Referenties geladen: 4 stuks

[openai-gpt-5-image]
  Aanroepen: openai/gpt-5-image...
  Klaar in 12.3s
  Opgeslagen: test-output/openai-gpt-5-image.png

[openai-gpt-5.4-image-2]
  ...

[google-gemini-3-pro-image-preview]
  ...

[google-gemini-3.1-flash-image-preview]
  ...

[xai-aurora]
  ...

Vergelijkingspagina gegenereerd: test-output/vergelijking.html

Klaar! Open test-output/vergelijking.html in je browser.
```

Bij API-fouten (bijv. model niet beschikbaar, quota): het script gaat door naar het volgende model en toont de fout in de vergelijkingspagina.

- [ ] **Stap 2: Open vergelijking in browser**

```bash
open test-output/vergelijking.html
```

- [ ] **Stap 3: Beoordeel elk resultaat op de 4 criteria**

Gebruik de sliders in de vergelijkingspagina:
- Stijlmatch (1–5): matcht het de warme Asteria-fotografiestijl?
- Interieur (1–5): klopt de saunaruimte met de referenties?
- Personen (1–5): authentiek of stockfoto-gevoel?
- Bruikbaar (1–5): zou je dit op de website plaatsen?

- [ ] **Stap 4: Documenteer de conclusie**

Maak `docs/superpowers/specs/2026-05-17-image-generation-test-conclusie.md` aan met:
- Winnend model + score
- Wat goed werkte / wat niet
- Aanbeveling voor gebruik in Asteria projecten
- Eventuele prompt-verbeteringen voor de volgende test
