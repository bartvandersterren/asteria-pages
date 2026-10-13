# Zap-blauwdruk: Extras-bestelling → Mews (Asteria)

Pre-arrival upsell-lander `visit.asteria.nl/extras` (bestanden: `extras.template.html`, `extras.js`, `extras.css`,
`functions/api/extras/[[path]].js`). Gelijk aan de Parkhotel-Zap "Extras-bestelling → Mews (Parkhotel)", maar met
de Asteria-service en -producten. **Deze Zap bestaat nog niet.** Zolang `ZAPIER_EXTRAS_HOOK` niet op het
Pages-project staat, gaat elke bestelling als `[HANDMATIG]`-mail naar de receptie (de gast ziet wel "genoteerd").

## Stappen

1. **Webhooks by Zapier · Catch Hook** — de URL wordt `ZAPIER_EXTRAS_HOOK`. De Function stuurt per productregel één
   POST (JSON). Alleen regel 1 heeft `task: "ja"` en de taaktekst; regels met een afwijking staan vooraan.
2. **Filter** — ga alleen door als `secret` exact gelijk is aan `EXTRAS_SHARED_SECRET`.
3. **Delay After Queue** — queue-sleutel `reservation_id`, 1 minuut (regels van één bestelling na elkaar, niet
   tegelijk op dezelfde reservering).
4. **Mews · Add Reservation Product** — Reservation = `reservation_id`; Service = Verblijf
   `755424cc-3077-4320-b069-af1d00ffbe47` (of het veld `service_id`); Product = **custom value** `product_id`;
   Count = `count`.
5. **Filter** — ga alleen door als `task` = `ja`.
6. **Mews · Create Task** — afdeling Front office; Name = `task_name`; Description = `task_description`;
   Deadline = `task_deadline` (aankomstdatum 12:00); gekoppeld aan de reservering.

## Velden die de Zap leest (negen)

| veld | inhoud |
|---|---|
| `secret` | gedeeld geheim (`EXTRAS_SHARED_SECRET`), voor de filterstap |
| `reservation_id` | Mews-reserverings-GUID uit de maillink (`r=`) |
| `service_id` | `755424cc-3077-4320-b069-af1d00ffbe47` (Verblijf) |
| `product_id` | Mews-product-id (zie tabel) |
| `count` | integer; wat Mews boekt (Mews vermenigvuldigt zelf, zie hieronder) |
| `task` | `ja` op de eerste regel, anders `nee` |
| `task_name` | taaknaam, max. 120 tekens, eindigt op `(CORRIGEER)` bij een afwijking |
| `task_description` | volledige receptietaak (bestelling, gast, verblijf, opmerking, te doen) |
| `task_deadline` | `YYYY-MM-DDT12:00:00` (aankomstdatum) |

Informatieve velden (strings, de Zap leest ze niet): `reservation_number`, `guest_name`, `guest_email`, `arrival`,
`departure`, `adults`, `nights`, `remark`, `order_summary`, `order_total`, `lang`, `product_name`, `charging`,
`unit_price`, `line_total`, `persons`, `units`, `evenings`, `evening_labels`, `preferred_time`, `billing`,
`mews_total`, `deviation`, `recommended_key`, `client`, `catalog_product_id`.

## Producten (Mews-Asteria `configuration/get`, 13 okt 2026)

| key | Mews-naam | product_id | prijs | ChargingMode | type op de lander | groep |
|---|---|---|---|---|---|---|
| diner | Driegangen diner | `75fce6f2-6339-41c2-9e48-b3b60095d412` | € 37,50 | PerPersonPerTimeUnit | perdag (avond) | verblijf |
| ontbijt | Ontbijt | `a80b1abc-7079-44f7-be63-af2e00bb4d9f` | € 17,50 | PerPersonPerTimeUnit | pernacht | verblijf |
| wellness | Wellness toegang (1 dag) | `bd06307a-e86f-434c-a799-b43400d93806` | € 12,50 | PerPerson | perdag (dag) | verblijf |
| fiets | Fietshuur (eenmalig p.p.) | `a3a062b9-3854-449c-b74f-b05300c1a15e` | € 9,50 | PerPerson | personen (fietsen) | verblijf |
| ebike | Elektrische fietshuur | `527b5916-5451-4db7-9839-b0b2008e6dd3` | € 25,00 | PerPerson | personen (fietsen) | verblijf |
| kruidenolie | Kruidenolie | `a2871461-233c-4aac-a2b9-b43400854b25` | € 4,95 | Once | eenmalig (max 3) | verblijf |
| badjas | Badjas & Slippers | `8a5468e9-1aa8-4a2f-818a-af810098ec66` | € 7,00 | PerPerson | personen | aankomst |
| handdoek | Handdoekpakket | `c558563b-c217-4b66-ac99-b43300d08641` | € 4,50 | PerPerson | personen | aankomst |
| early | Early check-in 12:00 uur | `325c73ef-09f9-4596-81d9-b0970067bd55` | € 25,00 | Once | eenmalig | aankomst |
| late | Late check-out 14:00 uur | `196e6fe4-f15a-4384-a7e0-b097006801ee` | € 25,00 | Once | eenmalig | vertrek |

Prijs, foto en chargingmode komen live uit Mews (10 min cache); naam en tekst op de lander staan in `AANBOD` in de
Function. Niet aangeboden: Babybedje, Ontbijtpakket.

**Gotcha count × personen × nachten:** Mews vermenigvuldigt het meegestuurde Count zelf: `PerPerson` = count ×
personen op de reservering, `PerPersonPerTimeUnit` = count × personen × nachten, alleen `Once` = exact (bewezen bij
Parkhotel, reservering 117796). Asteria heeft nog geen aparte Once-bestelproducten (`bestel_id`), dus de Function
kiest het Count dat het dichtst bij het gasttotaal komt (billing `B`). Wijkt het af (bijv. 1 badjas bij 2 gasten,
diner op 1 van 2 avonden, wellness 1 van 2 dagen), dan staat in de taak bovenaan `!! CORRIGEER IN MEWS` met het
juiste bedrag, krijgt de taaknaam `(CORRIGEER)` en het mailonderwerp `[CORRIGEER]`.

## Env-vars op het Pages-project (asteria-pages)

| naam | waarde | waar |
|---|---|---|
| `ZAPIER_EXTRAS_HOOK` | Catch Hook-URL van de Zap | production (secret) |
| `EXTRAS_SHARED_SECRET` | willekeurige string, gelijk aan de filterstap | production (secret) |
| `RESEND_API_KEY` | optioneel; zonder gaat de receptiemail via FormSubmit (info@asteria.nl) en is er geen gastmail | production (secret) |
| `MAIL_FROM` | `Hotel Asteria <info@asteria.nl>` (alleen met Resend, domein moet geverifieerd zijn) | production |
| `MAIL_INFO` | `info@asteria.nl` (standaard als leeg) | production |
| `EXTRAS_DRY_RUN` | `1` (hook overslaan, payload loggen) | **alleen preview** |

Optioneel: ratelimit-binding `FORM_LIMIT` (zonder binding gaat alles door; honeypot + 3 s-tijdcheck blijven).

## Open punten

- Zap + Mews-Marketplace-koppeling (Zapier ↔ Mews Asteria) bestaan nog niet (Stijn, via Chrome).
- Env-vars hierboven op het Pages-project zetten (`EXTRAS_DRY_RUN=1` alleen op preview).
- Once-bestelproducten "(per persoon per avond)" in Mews-Asteria aanmaken en als `bestel_id` in `AANBOD` zetten;
  tot dan CORRIGEER-taak bij diner/ontbijt/wellness/fiets/e-bike/badjas/handdoek als de keuze afwijkt.
- Asteria-mail 03 belooft "fles bubbels op je kamer", maar daar is geen betaald Mews-product voor; staat dus niet op
  de lander.
- Resend-domein asteria.nl verifiëren (tot dan geen bevestigingsmail aan de gast; de pagina belooft die dan ook niet).
- Feiten bevestigen bij de receptie: early 12.00 / late 14.00 (staan zo in Mews), wellness reserveren via de
  receptie, wijzigen tot de dag voor aankomst.
