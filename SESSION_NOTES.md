# Session Notes — 2026-05-22

## Wat gedaan

### Arrangementen blok — lander-google.html (commits 0ad69a9, 557b72a, 6511df9)

1. **Desktop layout:** 3-koloms grid (Weekend | Wellness | Asperge), Wellness featured in het midden
2. **Mobile layout:** Horizontale kaarten (foto links 110px, content rechts)
3. **Features getrimd:** Alleen highlights op de kaart + hint-tekst "Klik op 'Meer informatie'..."
4. **Mobile volgorde:** Wellness → Asperge → Weekend via CSS `order` (nth-child)

### Andere wijzigingen (andere sessie, al gepusht)
- vipStatus Revinate form → "Google Lander"
- Nav → alleen logo + "Boek nu"
- Hero trust bar → witte kaartbalk onderin hero

## Open / volgende sessie

- Visueel verifiëren op live URL zodra Cloudflare deploy klaar is
- Popup "Meer informatie" testen op mobile

## Technische notities

- Desktop: `grid-template-columns: 1fr 1.12fr 1fr` + `height: 100%` op `.arr-card`
- Mobile: `.arr-card { flex-direction: row }` + foto `width: 110px; min-height: 150px`
- CSS order: Weekend `order:3`, Wellness `order:1`, Asperge `order:2` in `@media (max-width: 768px)`
- Eyebrow + tagline verborgen op mobile (`display: none`)
