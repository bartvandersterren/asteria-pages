# Session Notes — 2026-06-23/24

## Wat gedaan

### Mews Booking Engine API — goedgekeurd en getest
- Client "Asteria Booking 1.0.0" geregistreerd door Mews Support (productie + demo)
- Authenticatie: alleen `"Client": "Asteria Booking 1.0.0"` in elke request body
- API pad: `https://api.mews.com/api/distributor/v1/...`

### API endpoints getest (allemaal werkend):
1. **Configuration** — `/configuration/get` met ConfigurationIds → hotel + kamers + rates
2. **Availability** — `/hotels/getAvailability` met HotelId → prijzen per rate/kamer
3. **Payment config** — `/hotels/getPaymentConfiguration` → PCI Proxy, iDEAL/Apple Pay/Google Pay
4. **Reservering aanmaken** — `/reservationGroups/create` → werkt end-to-end
5. **Creditcard betaling** — PCI Proxy Secure Fields tokenisatie + CreditCardData → werkt
6. **iDEAL** — via PaymentRequestId redirect naar app.mews.com → werkt (maar niet eigen design)

### Bevindingen payments:
- Creditcard: volledig eigen design mogelijk via PCI Proxy Secure Fields (merchantId `3000013748`)
- iDEAL/Google Pay/Apple Pay: altijd redirect naar Mews hosted betaalpagina (niet aanpasbaar)
- Non-refundable rates geven PaymentRequestId terug, flexibele rates niet
- Geen custom prijzen mogelijk via API — pricing altijd door Mews bepaald (via Rates + VoucherCodes)

### Prototype:
- `payment-test.html` — werkend betaalformulier, creditcard flow bewezen (reservering 101301)

## Testreserveringen (ANNULEREN!)
- 101296, 101298, 101299, 101301 — allemaal Royale kamer, begin juli

## Wat open staat
- Booking engine frontend bouwen (boeken.html ombouwen naar eigen API)
- Voucher validatie testen
- 3D Secure flow afhandelen
- payment-test.html opruimen of integreren
