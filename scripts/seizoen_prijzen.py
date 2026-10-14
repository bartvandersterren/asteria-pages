#!/usr/bin/env python3
"""Vanaf-prijzen voor de kamerslider van de seizoenslanders (visit.asteria.nl/herfst, lente, zomer, winter).

Haalt per nacht (seizoensvenster uit VENSTERS, standaard herfst 15 okt t/m 30 nov 2026; --van/--tot JJJJ-MM-DD, 2 volwassenen) de beschikbaarheid op via de Mews
Distributor API (hotels/getAvailability, zonder vouchercode) en neemt per kamercategorie de
laagste prijs per nacht over alle publieke tarieven (IsPrivate false). OTA-tarieven (naam
bevat "OTA") tellen niet mee: die zijn voor de boekingssites, niet voor de eigen site.
Prijzen zijn inclusief btw; de verblijfsbelasting zit er niet in.

Gebruik:
  python3 scripts/seizoen_prijzen.py lente      # seizoensvenster (herfst, lente, zomer, winter); standaard herfst
  python3 scripts/seizoen_prijzen.py --detail   # ook datum en tarief per kamer
  python3 scripts/seizoen_prijzen.py --van 2027-03-20 --tot 2027-05-31   # ander seizoen

Faalt de API, dan print het script de waarden uit build_kamers.py met de melding CONTROLEREN.
"""
import json, sys, time, urllib.error, urllib.request
from datetime import date, timedelta

API = 'https://api.mews.com/api/distributor/v1/hotels/getAvailability'
BASIS = {
    'Client': 'Asteria Booking 1.0.0',
    'ConfigurationId': '6dc9094c-76e3-4fd8-83a7-af1d00ffc556',
    'HotelId': '65a522c9-4828-413d-9ad8-af1d00ffb83f',
    'AdultCount': 2,
}
VENSTERS = {  # seizoen: (eerste, laatste aankomstnacht)
    'herfst': (date(2026, 10, 15), date(2026, 11, 30)),
    'lente':  (date(2027, 3, 1), date(2027, 5, 31)),
    'zomer':  (date(2027, 6, 1), date(2027, 8, 31)),
    'winter': (date(2026, 12, 1), date(2027, 2, 28)),
}
START, EIND = VENSTERS['herfst']

KAMERS = [  # key in <seizoen>-nl.json, Mews-categorie
    ('PRIJS_COMFORT',      '98900f3b-e5e2-49c9-9776-af1d00ffc315'),
    ('PRIJS_COMFORT_3',    '85ca19d7-eea5-41c8-8b93-af1d00ffc315'),
    ('PRIJS_ROYALE',       'a8fd7310-0d61-422f-89e6-af1d00ffc315'),
    ('PRIJS_DELUXE',       'c737de50-e41e-4c8d-a818-af1d00ffc315'),
    ('PRIJS_JUNIOR_SUITE', '27ea8deb-ded5-4856-8fdd-af1d00ffc315'),
    ('PRIJS_SUITE',        '4a642b66-68e6-444c-beeb-af1d00ffc315'),
    ('PRIJS_BRUIDSSUITE',  'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'),
    ('PRIJS_MINDERVALIDE', 'fa5b6540-7234-49ce-beb1-af1d00ffc315'),
]
TERUGVAL = {  # build_kamers.py (peildatum onbekend)
    'PRIJS_COMFORT': '114,30', 'PRIJS_COMFORT_3': '123,30', 'PRIJS_ROYALE': '123,30',
    'PRIJS_DELUXE': '132,30', 'PRIJS_JUNIOR_SUITE': '141,30', 'PRIJS_SUITE': '150,30',
    'PRIJS_BRUIDSSUITE': '177,30', 'PRIJS_MINDERVALIDE': '114,30',
}


def nacht(d, poging=0):
    body = dict(BASIS, StartUtc=d.isoformat() + 'T12:00:00Z',
                EndUtc=(d + timedelta(days=1)).isoformat() + 'T12:00:00Z')
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 and poging < 5:   # rate limit: even wachten en opnieuw
            time.sleep(30 * (poging + 1))
            return nacht(d, poging + 1)
        raise


def euro(v):
    return f'{v:.2f}'.replace('.', ',')


def main():
    global START, EIND
    detail = '--detail' in sys.argv
    seizoen = next((a for a in sys.argv[1:] if a in VENSTERS), None)
    if seizoen:
        START, EIND = VENSTERS[seizoen]
    if '--van' in sys.argv: START = date.fromisoformat(sys.argv[sys.argv.index('--van') + 1])
    if '--tot' in sys.argv: EIND = date.fromisoformat(sys.argv[sys.argv.index('--tot') + 1])
    laagst = {}  # categorie -> (prijs, datum, tariefnaam)
    try:
        d = START
        while d <= EIND:
            data = nacht(d)
            tarieven = {r['Id']: r for r in data.get('Rates', [])}
            for cat in data.get('RoomCategoryAvailabilities', []):
                if not cat.get('AvailableRoomCount'):
                    continue
                for occ in cat.get('RoomOccupancyAvailabilities', []):
                    if occ.get('AdultCount') not in (None, 2) or occ.get('ChildCount'):
                        continue
                    for p in occ.get('Pricing', []):
                        t = tarieven.get(p.get('RateId'))
                        if not t or t.get('IsPrivate'):
                            continue
                        naam = (t.get('Name') or {}).get('nl-NL') or next(iter((t.get('Name') or {}).values()), '')
                        if 'OTA' in naam:
                            continue
                        eur = (p.get('Price') or {}).get('Total', {}).get('EUR')
                        if eur is None:
                            continue
                        oud = laagst.get(cat['RoomCategoryId'])
                        if oud is None or eur < oud[0]:
                            laagst[cat['RoomCategoryId']] = (eur, d.isoformat(), naam)
            d += timedelta(days=1)
            time.sleep(1)   # de API geeft bij snelle reeksen 429
    except Exception as e:  # API onbereikbaar of ander formaat
        print(f'Mews-API faalt ({e}); waarden uit build_kamers.py, CONTROLEREN', file=sys.stderr)
        print(json.dumps(TERUGVAL, indent=1, ensure_ascii=False))
        return 1

    uit, mist = {}, []
    for key, cat in KAMERS:
        if cat in laagst:
            uit[key] = euro(laagst[cat][0])
            if detail:
                print(f'{key:20} {uit[key]:>8}  {laagst[cat][1]}  {laagst[cat][2]}', file=sys.stderr)
        else:
            uit[key] = TERUGVAL[key]
            mist.append(key)
    if mist:
        print('Geen beschikbaarheid gevonden voor ' + ', '.join(mist) + '; waarde uit build_kamers.py, CONTROLEREN', file=sys.stderr)
    print(f'Peildatum {date.today().isoformat()}, nachten {START.isoformat()} t/m {EIND.isoformat()}, 2 volwassenen', file=sys.stderr)
    print(json.dumps(uit, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
