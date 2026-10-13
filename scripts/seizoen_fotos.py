#!/usr/bin/env python3
"""Maakt de foto's voor de seizoenslanders (fotos/hf-*, lt-*, zm-*, wt-*.webp, WebP q72 zoals CONTRIBUTING.md).

Bronnen (zie de kiezer asteria-herfst-blokkenkiezer/assets-lijst.md):
  FB = ~/Documents/Asteria /Fotobank Asteria/  (originelen, niet in git)
  AP = deze repo (fotos/)
  PH = ~/projects/parkhotel-site/public/assets/img/  (alleen uitjes zonder Asteria-foto, nooit het Parkhotel-gebouw;
       noodoplossing: Maasduinen, Kasteeltuinen, Peel, Venlo, Designer Outlet)
Foto's die al geschikt in fotos/ staan (l26-*, wp-sauna-fins, omgeving-hertogjan) en gedeelde foto's van een ander
seizoen (bv. hf-kasteeltuinen, lt-bos) verwijst de JSON direct; die staan hier niet dubbel.

Gebruik:  python3 scripts/seizoen_fotos.py <herfst|lente|zomer|winter>   (overschrijft bestaande bestanden)
"""
import os, sys
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FBR = os.path.expanduser('~/Documents/Asteria /Fotobank Asteria/')
FB = FBR + 'Omgeving, natuur & fietsen/'
MAIL = os.path.join(BASE, 'mail') + '/'
AP = os.path.join(BASE, 'fotos') + '/'
PH = os.path.expanduser('~/projects/parkhotel-site/public/assets/img/')
UIT = os.path.join(BASE, 'fotos')

# naam: (bron, breedtes, uitsnede) ; uitsnede = (beeldverhouding b/h, horizontaal midden 0-1) of None
SEIZOENEN = {'herfst': {
    'hf-hero':          (FB + 'Koppel wandelen in het bos/P1081729.jpg', [1600, 800], None),
    'hf-zomer':         (AP + 'hero-zomer.webp', [800], None),
    'hf-laan':          (FB + 'Koppel wandelen in het bos/P1091862.jpg', [1000], (0.75, 0.45)),
    'hf-bos-hand':      (FB + 'Koppel wandelen in het bos/P1081802.jpg', [1200], None),
    'hf-fietsen-bos':   (FB + 'Koppel fietsend door het bos/P1092018.jpg', [1200], None),
    'hf-fietsen-bord':  (FB + 'Koppel bij fietsroutes voor het hotel/P1081520.jpg', [1200], None),
    'hf-brug':          (FB + 'Koppel bij Fietsenstalling/P1081404.jpg', [1200], None),
    'hf-sauna-bos':     (AP + 'wp-sauna-bos.webp', [1200], None),
    'hf-diner':         (AP + 'arr-c-diner.webp', [1200], None),
    'hf-vlaai':         (AP + 'arr-c-vlaai.webp', [1200], None),
    'hf-deluxe':        (AP + 'kamer-deluxe.webp', [1600, 800], None),
    'hf-maasduinen':    (PH + 'ct-natuur-maasduinen-2345ed.webp', [1200], None),
    'hf-kasteeltuinen': (PH + 'ct-cultuur-kasteeltuinen-da9adc.webp', [1200], None),
    'hf-hertogjan':     (AP + 'omgeving-hertogjan.webp', [600], None),
}, 'lente': {
    'lt-hero':          (FBR + 'Restaurant, Brasserie & Terras/Terras/P1057196.jpg', [1600, 800], None),
    'lt-winter':        (FBR + 'Receptie/P1046500.jpg', [800], None),
    'lt-laan':          (FB + 'Koppel bij Fietsenstalling/P1081459.jpg', [1000], (0.75, 0.55)),
    'lt-terras':        (FBR + 'Restaurant, Brasserie & Terras/Terras/P1057257.jpg', [1200], None),
    'lt-asperges':      (FBR + 'Restaurant, Brasserie & Terras/Restaurant/Gerechten/P1092712.jpg', [1200], None),
    'lt-arr':           (FBR + 'Restaurant, Brasserie & Terras/Restaurant/Gerechten/P1092719.jpg', [1600, 800], None),
    'lt-bos':           (FB + 'Koppel wandelen in het bos/P1091862.jpg', [1200], None),
    'lt-maasduinen':    (PH + 'maasduinen-ven-8db83b.webp', [600], None),
    'lt-peel':          (PH + 'Peel-vlonderpad-77f872.webp', [600], None),
}, 'zomer': {
    'zm-hero':          (AP + 'l26-hotel-zonsondergang.webp', [1400, 800], (1.506, 0.56)),
    'zm-intro':         (FBR + 'Exterieur & aankomst/P1057182.jpg', [1000], (0.75, 0.62)),
    'zm-ontbijt':       (FBR + 'Restaurant, Brasserie & Terras/Terras/P1057251.jpg', [1200], None),
    'zm-fietsen':       (FB + 'Koppel fietsen voor het hotel/P1081692.jpg', [1200], None),
    'zm-arr':           (MAIL + 'summer-diner.jpg', [1030, 800], None),
}, 'winter': {
    'wt-hero':          (FBR + 'Wellness/Finse sauna/148A4027.jpg', [1600, 800], None),   # P1046509: gast valt achter de tekstkaart

    'wt-intro':         (AP + 'l26-wellness-staand.webp', [1000], (0.75, 0.5)),
    'wt-ontbijt':       (FBR + 'Kamers/Bruidssuite/P1057472.jpg', [1200], None),
    'wt-diner':         (FBR + 'Restaurant, Brasserie & Terras/Restaurant/Gerechten/P1092704.jpg', [1200], None),
    'wt-arr':           (FBR + 'Wellness/Relaxruimte/P1058084.jpg', [1600, 800], None),
    'wt-bos':           (FB + 'Koppel wandelen in het bos/P1081716.jpg', [1200], None),
    'wt-venlo':         (PH + 'Kest-in-Venlo-baa763.webp', [870], None),
    'wt-outlet':        (PH + 'Roermond-DayOut-outlet-087609.webp', [600], None),
}}


def uitsnede(im, verhouding, midden):
    w, h = im.size
    if w / h > verhouding:                      # te breed: zijkanten eraf
        nw = round(h * verhouding)
        x = min(max(0, round(w * midden - nw / 2)), w - nw)
        return im.crop((x, 0, x + nw, h))
    nh = round(w / verhouding)                  # te hoog: midden houden
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SEIZOENEN:
        sys.exit('Gebruik: python3 scripts/seizoen_fotos.py <' + '|'.join(SEIZOENEN) + '>')
    for naam, (bron, breedtes, snede) in SEIZOENEN[sys.argv[1]].items():
        im = ImageOps.exif_transpose(Image.open(bron)).convert('RGB')
        if snede:
            im = uitsnede(im, *snede)
        for i, b in enumerate(breedtes):
            kopie = im.copy()
            if kopie.width > b:
                kopie = kopie.resize((b, round(kopie.height * b / kopie.width)), Image.LANCZOS)
            doel = os.path.join(UIT, naam + ('' if i == 0 else f'-{b}') + '.webp')
            kopie.save(doel, 'WEBP', quality=72, method=6)
            print(f'{os.path.basename(doel):26} {kopie.width}x{kopie.height}  {os.path.getsize(doel) // 1024} KB')


if __name__ == '__main__':
    main()
