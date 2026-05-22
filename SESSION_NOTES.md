# Session Notes — 2026-05-22 (update)

## Wat gedaan

### Hero trust merge (lander-google.html)
- `.hero__trust-bar` (witte absolute kaart onderaan) verwijderd
- Nieuwe `.hero__trust-micro` strip direct onder CTA-knop (sterren + 4,2, Gratis annuleren, Laagste prijs)
- Hero padding-bottom: 80px → 56px (desktop), 60px → 40px (mobile)

### Logies & Ontbijt kaart (lander-google.html)
- Weekend kaart vervangen door L&O (arr-card--bb, id=arrBbCard)
- Foto: kamer-comfort.webp, CTA zonder voucher (mewsRoute=rooms)
- ARR_DATA.logiebb — popup-schema: foto/features/note (niet photo/includes)
- Popup-renderer: displayPrice — leest #bbPrice als geladen, anders d.price
- Popup-guard checkt alleen op 'Laden…' (fallback is nu ook geldige prijs)

### Wellness voucher
- WELLNESS → 2026WELLNESS (kaart-CTA + ARR_DATA)

### Mews prijs-fetch — OPEN ISSUE
- Client-side fetch naar /mews/api/distributor/v1/hotels/getAvailability werkt NIET: vereist sessie-token
- CF function functions/api/bb-price.js gebouwd: leest KV-sessie, doet server-side Mews call
- PROBLEEM: KV-sessie is leeg → geeft altijd { error: 'no session' }
- FALLBACK actief: "vanaf € 120,– per kamer · 1 nacht"
- Oplossingsrichtingen voor later:
  - A: sessieharvesting (onderschep sessie als bezoeker booking popup opent)
  - B: Mews vragen om server-side API key
  - C: statische prijs accepteren (staat nu op €120)
