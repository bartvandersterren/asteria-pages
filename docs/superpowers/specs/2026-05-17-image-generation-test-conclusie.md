# AI Image Generation Test — Conclusie

**Datum:** 2026-05-17
**Scene:** Koppel in Finse sauna, Hotel Asteria
**Input:** Identieke prompt (EN) + 4 reference images (sauna interieur + koppel in sauna)

---

## Resultaten

| Model | Status | Tijd | Oordeel |
|---|---|---|---|
| openai/gpt-5-image | ❌ Safety blocked | — | Onbruikbaar via API |
| openai/gpt-5.4-image-2 | ✅ | 200s | Hoge kwaliteit, maar traag en onbetrouwbaar (safety) |
| google/gemini-3-pro-image-preview | ✅ | 36s | **Winnaar** |
| google/gemini-3.1-flash-image-preview | ✅ | 16s | Snel alternatief |
| xai/grok-imagine-image-quality | ✅ | 4s | Snel, minder reference-nauwkeurig |

## Winnaar: Gemini 3 Pro (via OpenRouter)

**Waarom:**
- Consistent betrouwbaar — geen safety blocks op wellness-scenes
- Werkt via API (automatiseerbaar)
- Volgt reference images goed genoeg voor fotobank-aanvulling
- Redelijke snelheid (36s)

## OpenAI-kanttekening

OpenAI via ChatGPT (handmatig) levert aantoonbaar betere kwaliteit: het model volgt references precies (zoutsteen, raam met bomen + bakstenen gebouw, licht hout). Maar via API/OpenRouter blokkeert het safety-systeem wellness-scenes met mensen consistent. Onbruikbaar voor geautomatiseerd gebruik.

## Aanbeveling voor Asteria-projecten

**Standaard model:** `google/gemini-3-pro-image-preview` via OpenRouter
**Budget/snel:** `google/gemini-3.1-flash-image-preview`
**Handmatig/hoge kwaliteit:** ChatGPT met GPT-image + references als bijlage

## Prompt-richtlijnen (bewezen)

- Schrijf prompt in het Engels
- Beschrijf het interieur accuraat en specifiek (materialen, kleuren, lichtbron)
- Geef 4 references mee: 2x interieur + 2x sfeer/personages
- Maximaal 4 references — meer helpt niet aantoonbaar
- Vermeld fotostijl expliciet: editorial hotel photography, lens, compositie, mood
