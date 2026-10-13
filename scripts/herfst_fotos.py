#!/usr/bin/env python3
"""Maakt de foto's voor /herfst (fotos/hf-*.webp, WebP q72 zoals CONTRIBUTING.md).

Bronnen (zie de kiezer asteria-herfst-blokkenkiezer/assets-lijst.md):
  FB = ~/Documents/Asteria /Fotobank Asteria/  (originelen, niet in git)
  AP = deze repo (fotos/)
  PH = ~/projects/parkhotel-site/public/assets/img/  (Maasduinen en Kasteeltuinen: geen Asteria-foto; noodoplossing)

Gebruik:  python3 scripts/herfst_fotos.py   (overschrijft bestaande hf-bestanden)
"""
import os
from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = os.path.expanduser('~/Documents/Asteria /Fotobank Asteria/Omgeving, natuur & fietsen/')
AP = os.path.join(BASE, 'fotos') + '/'
PH = os.path.expanduser('~/projects/parkhotel-site/public/assets/img/')
UIT = os.path.join(BASE, 'fotos')

# naam: (bron, breedtes, uitsnede) ; uitsnede = (beeldverhouding b/h, horizontaal midden 0-1) of None
FOTOS = {
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
}


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
    for naam, (bron, breedtes, snede) in FOTOS.items():
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
