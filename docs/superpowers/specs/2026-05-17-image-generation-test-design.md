# Design: AI Image Generation Test — Asteria Wellness

_Datum: 2026-05-17_

## Doel

Verkennen of AI-beeldgeneratie bruikbare sfeerbeelden kan produceren die ontbreken in de Asteria fotobank. Specifiek: wellness-fotografie met koppel die de bestaande fotografiestijl matcht. Resultaten worden vergeleken over meerdere modellen met identieke input.

## Testscène

**Koppel in de Finse sauna — avondsfeer**

Een man en vrouw zitten ontspannen naast elkaar op de houten bank van de Finse sauna van Hotel Asteria. Warme gouden gloed van de saunaverwarming. Witte handdoeken. Gesloten ogen of zacht naar elkaar kijken. Geen pose — een moment van diepe rust.

## Referentiebeelden

Vier foto's uit de fotobank worden als visuele referentie meegestuurd naar elk model:

| Bestand | Rol |
|---|---|
| `/Users/bartvandersterren/Documents/Asteria Fotobank/P1046696.jpg` | Interieur infraroodcabine — hout, licht, handdoeken |
| `/Users/bartvandersterren/Documents/Asteria Fotobank/P1046715.jpg` | Finse sauna interieur — panelen, bank, sfeer |
| `/Users/bartvandersterren/Documents/Asteria Fotobank/P1057456.jpg` | Koppel in badjassen — persoon-stijl, warme sfeer |
| `/Users/bartvandersterren/Documents/Asteria Fotobank/P1057468.jpg` | Koppel in badjassen — licht en intimiteit referentie |

## Fotografiestijl (te matchen)

Gebaseerd op analyse van de Asteria fotobank:

- **Licht**: Warm, gouden tonen. Geen koele/blauwe tint. Zachte schaduwwerking.
- **Diepte**: Ondiepe scherptediepte — achtergrond wazig, personen/object scherp.
- **Mensen**: Authentiek, niet geposeerd. Casual elegant. Neutrale kledingkleuren (wit, beige, grijs).
- **Kleurpalet**: Beige, crème, grijs, donkerblauw, groen. Gouden accenten.
- **Compositie**: Momentfotografie. Horizontaal. Ruime kadrage.
- **Interieur**: Modern minimalistisch. Hout, witte accenten.

## Tekstprompt (EN)

```
A couple relaxing together in a Finnish sauna at a luxury four-star hotel in the Netherlands.
They are seated side by side on a wooden bench, eyes closed or softly looking at each other.
White towels draped over them. The sauna interior has warm golden light from the heating element,
wooden walls and benches, subtle steam in the air.

Photography style: editorial hotel photography, warm golden tones, shallow depth of field,
soft natural-feeling light, authentic moment — not posed or stock-photo.
35mm lens, horizontal composition. The mood is intimate, peaceful, luxurious.

Match the visual style and interior details from the reference images provided.
Do not add logos, text, or unrealistic elements.
```

## Modellen

Alle modellen ontvangen identieke input: de 4 referentiebeelden + bovenstaande prompt.

| Model | Via | Opmerking |
|---|---|---|
| `openai/gpt-5-image` | OpenRouter | Sterkste instructievolging OpenAI |
| `openai/gpt-5.4-image-2` | OpenRouter | Snel + nauwkeurig |
| `google/gemini-3-pro-image-preview` | OpenRouter | Google top-kwaliteit |
| `google/gemini-3.1-flash-image-preview` | OpenRouter | Snel, Google |
| Aurora | xAI direct (`api.x.ai`) | Fotorealistisch — testen of image input werkt |

## API-aanroep structuur

### OpenRouter (multimodal chat completions)

```javascript
const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'openai/gpt-5-image',
    messages: [{
      role: 'user',
      content: [
        { type: 'text', text: PROMPT },
        { type: 'image_url', image_url: { url: toBase64DataUrl(ref1) } },
        { type: 'image_url', image_url: { url: toBase64DataUrl(ref2) } },
        { type: 'image_url', image_url: { url: toBase64DataUrl(ref3) } },
        { type: 'image_url', image_url: { url: toBase64DataUrl(ref4) } }
      ]
    }]
  })
});
// Output: base64 image in response.choices[0].message.content
```

### xAI Aurora

```javascript
const response = await fetch('https://api.x.ai/v1/images/generations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.XAI_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'aurora',
    prompt: PROMPT,
    n: 1,
    response_format: 'url'
    // Opmerking: image input mogelijk niet ondersteund — eerst zonder references testen
  })
});
```

## Testscript

Een Node.js script `test-image-gen.js` in de projectroot:

1. Laadt de 4 referentiefoto's en converteert naar base64 data URLs
2. Roept elk model aan (sequentieel om rate limits te vermijden)
3. Slaat elke output op als `test-output/<model-naam>.png`
4. Logt prijs/tijd per model naar console

## Evaluatiecriteria

Na het genereren beoordelen we elk resultaat op:

| Criterium | Gewicht | Beschrijving |
|---|---|---|
| Stijlmatch | Hoog | Matcht het de warme, authentieke Asteria-fotografiestijl? |
| Interieuraccuraatheid | Hoog | Klopt het saunainterior met de references? |
| Persoon-authenticiteit | Hoog | Zien de mensen er echt uit, niet als stockfoto-modellen? |
| Licht & kleur | Middel | Warme gouden tonen, geen koele kleuren? |
| Bruikbaarheid | Middel | Zou je dit op de website willen plaatsen? |
| Prijs/kwaliteit | Laag | Kosten per generatie |

## Output

- Gegenereerde afbeeldingen: `test-output/` (tijdelijk, niet in git)
- Vergelijkingspagina: `test-output/vergelijking.html` met alle outputs naast elkaar
- Conclusie documenteren in `docs/superpowers/specs/2026-05-17-image-generation-test-conclusie.md` na uitvoering
