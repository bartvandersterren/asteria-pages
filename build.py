#!/usr/bin/env python3
"""
Genereer taalversies vanuit templates + JSON-vertalingen.

Gebruik:
  python3 build.py                    # bouwt alles
  python3 build.py wellness           # alleen wellness template
  python3 build.py feedback           # oude feedbackpagina -> feedback-oud(-en/-de).html
  python3 build.py feedback-v2        # feedback in de nieuwe huisstijl (lander-w1-kop/voet) -> feedback(-en/-de).html = live /feedback
  python3 build.py verblijfsverjaardag-v2   # lander W1 (reviewmuur uit content/)
  python3 build.py verblijfsverjaardag-v3   # zelfde sjabloon, blok 'zijkaart' -> verblijfsverjaardag.html (live sinds 14 okt 2026; oude lander -> verblijfsverjaardag-oud.html)
  python3 build.py herfst lente zomer winter   # seizoenslanders (visit.asteria.nl/<seizoen>)
  python3 build.py hotel-venray-v2      # algemene hotellander (Meta/Google) op lander-w1 met blok 'hotel', zonder actiecode
  python3 build.py kamertypes-v2        # kamertypes in de nieuwe stijl (lander-w1, blokken 'hotel' + 'kamertypes') -> kamertypes-v2.html
  python3 build.py bedankt welkom-terug gemist verjaardag   # flow-landers op lander-w1 met zijkaart (zoals verblijfsverjaardag-v3)
  python3 build.py welkom-v2           # welkomstlander (code WELKOM) op lander-w1 met zijkaart -> welkom.html (live /welkom; oude NL -> welkom-oud.html)
  python3 build.py najaarsarrangement   # arrangementsjabloon: lander-w1 met blokken zijkaart + arrangement (ook wellness-arrangement,
                                        # oorlogsmuseum-arrangement, limburg-arrangement, weekend-aanbieding, golfarrangement)
  python3 build.py arrangementen       # arrangementenoverzicht -> arrangementen-v2.html (noindex, apply_overzicht)
  python3 build.py kamers/royale-kamer  # kamerdetailpagina nieuwe stijl (kamer-w1; ook kamers/suite, kamers/bruidssuite,
                                      # kamers/comfort-kamer-3-personen, kamers/mindervalide-kamer)
  python3 build.py wellness nl        # wellness, alleen NL
"""

import json, os, re, sys, urllib.parse

base = os.path.dirname(os.path.abspath(__file__))

TEMPLATES = {
    # NL-uitvoer van 'wellness' en 'najaar' is sinds de promotie van de arrangementen (okt 2026) -oud + noindex;
    # /wellness-arrangement en /najaarsarrangement zijn de lander-w1-arrangementen ('najaar' NL stond 16 okt t/m 5 nov 2026
    # tijdelijk weer op /najaarsarrangement voor campagnemail 1; sinds 5 nov 2026 definitief lander-w1). EN/DE ongewijzigd.
    'wellness': {
        'template': 'wellness-arr-c.template.html',
        'noindex': ('nl',),
        'langs': {
            'nl': ('wellness-arrangement-oud.html', 'translations/nl.json'),   # sinds de promotie (okt 2026) -oud, noindex
            'en': ('wellness-arrangement-en.html', 'translations/en.json'),
            'de': ('wellness-arrangement-de.html', 'translations/de.json'),
        },
    },
    # Oude feedbackpagina (brand.css-stijl): sinds 14 okt 2026 op /feedback-oud(-en/-de), noindex. /feedback = entry 'feedback-v2'.
    'feedback': {
        'template': 'feedback.template.html',
        'langs': {
            'nl': ('feedback-oud.html',    'translations/feedback-nl.json'),
            'en': ('feedback-oud-en.html', 'translations/feedback-en.json'),
            'de': ('feedback-oud-de.html', 'translations/feedback-de.json'),
        },
    },
    # Feedbackpagina in de nieuwe huisstijl (lander-w1-kop/voet), sinds 14 okt 2026 live op /feedback(-en/-de);
    # noindex (robots-meta staat in het sjabloon), niet in sitemap.xml. Zelfde werking en teksten als 'feedback'; stijl in feedback-v2.css (prefix fb2-).
    'feedback-v2': {
        'template': 'feedback-v2.template.html',
        'langs': {
            'nl': ('feedback.html',    'translations/feedback-v2-nl.json'),   # live /feedback sinds 14 okt 2026 (/feedback-v2 -> 301)
            'en': ('feedback-en.html', 'translations/feedback-v2-en.json'),
            'de': ('feedback-de.html', 'translations/feedback-v2-de.json'),
        },
    },
    'happy-summer': {
        'template': 'happy-summer.template.html',
        'langs': {
            'nl': ('happy-summer-arrangement.html',    'translations/happy-summer-nl.json'),
            'en': ('happy-summer-arrangement-en.html', 'translations/happy-summer-en.json'),
            'de': ('happy-summer-arrangement-de.html', 'translations/happy-summer-de.json'),
        },
    },
    'najaar': {
        'template': 'najaar.template.html',
        'noindex': ('nl',),
        'langs': {
            'nl': ('najaarsarrangement-oud.html', 'translations/najaar-nl.json'),   # sinds 5 nov 2026 weer -oud, noindex
            'en': ('najaarsarrangement-en.html', 'translations/najaar-en.json'),
            'de': ('najaarsarrangement-de.html', 'translations/najaar-de.json'),
        },
    },
    'welkom': {
        'template': 'welkom.template.html',
        'langs': {
            'nl': ('welkom-oud.html', 'translations/welkom-nl.json'),   # oude NL-lander; /welkom = welkom-v2 (sinds 14 okt 2026)
            'en': ('welkom-en.html', 'translations/welkom-en.json'),
            'de': ('welkom-de.html', 'translations/welkom-de.json'),
        },
    },
    'augustus-actie': {
        'template': 'augustus-actie.template.html',
        'langs': {
            'nl': ('augustus-actie.html',    'translations/augustus-actie-nl.json'),
            'en': ('augustus-actie-en.html', 'translations/augustus-actie-en.json'),
            'de': ('augustus-actie-de.html', 'translations/augustus-actie-de.json'),
        },
        # De cadeau-/kamersecties staan letterlijk (NL) in de template; voor EN/DE
        # worden die na de {{KEY}}-pass vertaald via een geordende NL→taal-lijst.
        'literals': {
            'en': 'translations/augustus-actie-literals-en.json',
            'de': 'translations/augustus-actie-literals-de.json',
        },
    },
    # Lander-sjabloon 2026 (nieuwe huisstijl asteria.nl): alleen NL, noindex.
    # Andere flow-landers = zelfde template + eigen JSON + eigen fotos/l26-*.
    'verblijfsverjaardag': {
        'template': 'lander-2026.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag-oud.html', 'translations/verblijfsverjaardag-nl.json'),
        },
    },
    # Lander-sjabloon W1 Thuiskomst (blokkenkiezer 1a-2a-3a-4b-5a-6c-7a): alleen NL, noindex.
    # Reviewmuur wordt gevuld uit content/reviews-google-asteria.json (zie inject_reviews).
    'verblijfsverjaardag-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag-v2.html', 'translations/verblijfsverjaardag-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
    },
    # Variant v3 van dezelfde lander: zelfde sjabloon, blok 'zijkaart' aan = tegels, attentie en
    # kamerslider in een linker kolom met rechts een meelopende (sticky) boekkaart, zonder uitklaptab.
    'verblijfsverjaardag-v3': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('verblijfsverjaardag.html', 'translations/verblijfsverjaardag-v3-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    },
    # Flow-landers op hetzelfde sjabloon als verblijfsverjaardag-v3 (blok 'zijkaart'), alleen NL, noindex,
    # niet in sitemap. Per lander eigen translations/<slug>-nl.json + fotos/l26-<slug>-*.webp.
    # bedankt = BEDANKT (upgrade), welkom-terug = WELKOMTERUG (eerste ontbijt), gemist = GEMIST (upgrade),
    # verjaardag = VERJAARDAG (fles bubbels).
    **{s: {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    } for s in ('bedankt', 'welkom-terug', 'gemist', 'verjaardag')},
    # Welkomstlander (welkomstflow na nieuwsbriefaanmelding) op lander-w1 met zijkaart: code WELKOM,
    # welkomstgeschenk (bubbels, badjas, badlaken) bij het eerste verblijf. Alleen NL, noindex.
    # Blok 3a is het cadeaublok (variant 'cadeau', aan via CADEAU_ITEMS in de JSON, render_cadeau).
    # Sinds 14 okt 2026 de live /welkom (welkom.html); oude NL-lander -> welkom-oud.html (entry 'welkom'),
    # EN/DE blijven welkom-en/-de. /welkom-v2 -> 301 naar /welkom in _redirects.
    'welkom-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('welkom.html', 'translations/welkom-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True},
    },
    # Arrangementen op lander-w1 (blokken 'zijkaart' + 'arrangement'; arrangement.css/.js): alleen NL, noindex, niet in sitemap.
    # Live sinds okt 2026 op de nette adressen (oude -v2/-v3 301 in _redirects; oude najaar/wellness-NL -> -oud).
    # Najaarsarrangement stond 16 okt t/m 5 nov 2026 tijdelijk op /najaarsarrangement-v2; sinds 5 nov 2026 weer op /najaarsarrangement.
    # Nieuw arrangement = translations/<slug>-nl.json (kopie van najaarsarrangement-nl.json) + slug in deze lijst.
    # Opbouw en velden: zie CLAUDE.md (Arrangementen op lander-w1) en apply_arrangement(). Schakelaars in de JSON:
    # ZV_TOON (zondagvoordeel), WAAROM_TOON (Waarom Asteria, standaard aan), ANDERE_TOON (+ lijst '_andere'),
    # lijst '_banen' (golfbanen na Dit is inbegrepen; alleen golf).
    # Keys met een '_' vooraan en niet-tekstwaarden gaan niet de {{KEY}}-pass in.
    **{s: {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True, 'arrangement': True},
    } for s in ('najaarsarrangement', 'wellness-arrangement', 'oorlogsmuseum-arrangement', 'limburg-arrangement', 'weekend-aanbieding', 'golfarrangement')},
    # Winterarrangement 2027: sinds 5 nov 2026 LIVE op /winterarrangement (index, follow via 'index'; /winterarrangement-v2
    # 301 in _redirects, bestand weg). ARR_KALENDER stond false zolang WINTER27 niet in Mews stond; sinds 5 nov true
    # (prijskalender aan), ZV_BEREKENEN false (zondag uit Mews).
    'winterarrangement': {
        'template': 'lander-w1.template.html',
        'index': ('nl',),
        'langs': {
            'nl': ('winterarrangement.html', 'translations/winterarrangement-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'zijkaart': True, 'arrangement': True},
    },
    # Algemene hotellander (tegenhanger van parkhotelhorst.nl/hotel-horst-2/, voor Meta-verkoopads en branded Google Ads):
    # lander-w1 met blok 'hotel' = geen vouchercode (VOUCHER leeg, zie zonder_voucher), geen tegelstrook en geen
    # uitklaptab; ster-split = 'Een verblijf dat bij je past'; na de kamers faciliteiten, omgeving en arrangementen
    # (hotel.css, prefix ho-, lijsten '_faciliteiten', '_fac_extra', '_omgeving', '_arrangementen' via render_hotel).
    # Alleen NL, noindex, niet in sitemap. Preview op /hotel-venray-v2; /hotel-venray en /lander-google blijven.
    'hotel-venray-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('hotel-venray-v2.html', 'translations/hotel-venray-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        # 'trustrij': op het bureaublad alle drie de KAART_VINK_* onder de boekbalk in plaats van de ene BOEKBALK_NOOT
        'blokken': {'hotel': True, 'trustrij': True},
    },
    # Kamertypes in de nieuwe stijl (nabouw staging /kamers/; live /kamertypes blijft de oude build_kamers.py-pagina tot akkoord):
    # lander-w1 met blokken 'hotel' (geen actiecode, hotel.css, arrangementenstrook ho-arr) + 'kamertypes' (kamertypes-v2.css/.js,
    # prefix kt-): subhero met boekbalk, Kies je kamer (filterchips + kaarten met fotogalerij, geen prijzen), Wat in elke kamer
    # klaarstaat, arrangementen, reviewmuur, Goed om te weten, FAQ, fotowolk. Geen ster-split, kamerslider, faciliteiten, omgeving
    # of kamer-pop-up. Lijsten in de JSON via render_kamertypes. Alleen NL, noindex, niet in sitemap, gesloten (GESLOTEN_LANDER).
    'kamertypes-v2': {
        'template': 'lander-w1.template.html',
        'langs': {
            'nl': ('kamertypes-v2.html', 'translations/kamertypes-v2-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'blokken': {'hotel': True, 'kamertypes': True},
    },
    # Kamerdetailpagina's in de nieuwe stijl (nov 2026): kamer-w1.template.html + kamer-w1.css/.js (prefix km-), structuur
    # 1-op-1 van de Effecty-staging /kamers/comfort-kamer/, voor de kamers zonder staging-detailpagina (KAMER_PAGINAS:
    # Royale, Suite, Bruidssuite, Comfort 3-persoons, Mindervalide; Comfort en Deluxe = spiegelpagina's, Junior Suite niet).
    # Kop/voet uit lander-w1.template.html in de spiegelstand (GESLOTEN_LANDER "spiegel", links uit spiegel-links.json),
    # live vanaf-prijs via /api/kamer-vanaf. Alleen NL, noindex, niet in sitemap. translations/kamer-<slug>-v2-nl.json -> kamers/<slug>.html.
    **{f'kamers/{s}': {
        'template': 'kamer-w1.template.html',
        'langs': {
            'nl': (f'kamers/{s}.html', f'translations/kamer-{s}-v2-nl.json'),
        },
        'kamer': True,
    } for s in ('royale-kamer', 'suite', 'bruidssuite', 'comfort-kamer-3-personen', 'mindervalide-kamer')},
    # Seizoenslanders (blokkenkiezer 1c-2d-3a-4a-5c-6i-7b-8b): alleen NL, noindex, niet in sitemap.
    # Eén sjabloon (seizoen.template.html + seizoen.css + seizoen.js); alle seizoensinhoud in de JSON.
    # Per seizoen een entry met eigen translations/<seizoen>-nl.json. Reviewmuur zoals lander-w1.
    **{s: {
        'template': 'seizoen.template.html',
        'langs': {
            'nl': (f'{s}.html', f'translations/{s}-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
    } for s in ('herfst', 'lente', 'zomer', 'winter')},
    # Arrangementenoverzicht (opbouw Parkhotel /arrangement/, uiterlijk Asteria): alleen NL, noindex, niet in sitemap, nergens gelinkt.
    # Kop/voet/kamers/reviews/kamer-pop-up uit lander-w1.template.html, kaartdata uit de arrangement-JSON's (apply_overzicht).
    'arrangementen': {
        'template': 'arrangementen.template.html',
        'langs': {
            'nl': ('arrangementen-v2.html', 'translations/arrangementen-nl.json'),
        },
        'reviews': 'content/reviews-google-asteria.json',
        'overzicht': True,
    },
    # Duitse Google Ads-landers (nov 2026): eigen sjabloon adslander.template.html + adslander.css/-pop.css/.js, nabouw van
    # parkhotelhorst.nl/de/wellnesshotel-limburg-nieuw/ in de Asteria-stijl. Alles per lander in translations/adslander-<naam>-de.json
    # (veldnamen zoals Parkhotel), pop-upinhoud in content/adslander-pop-de.json; build_adslander() doet de rest.
    # noindex, nofollow, niet in sitemap, nergens gelinkt. Volgende lander = JSON + entry hieronder.
    'adslander-wellnesshotel': {
        'template': 'adslander.template.html',
        'langs': {
            'de': ('wellnesshotel-limburg-de.html', 'translations/adslander-wellnesshotel-de.json'),
        },
        'adslander': True,
    },
    # Uitjepagina's (nov 2026): sjabloon uitje.template.html + uitje.css/.js + kaart-getekend.css/.js, nabouw van de
    # Parkhotel-omgevingspagina's (parkhotelhorst.nl/gebied/<slug>/) in de Asteria-stijl van de adslander. Alles per uitje in
    # translations/uitje-<slug>-nl.json (vaste labels in translations/uitje-labels-nl.json, kamers in content/uitje-kamers-nl.json);
    # build_uitje() doet de rest. Volgend uitje = JSON kopieren + regel hieronder. Proef: noindex, follow.
    'uitje-zooparc-overloon': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('zooparc-overloon-v2.html', 'translations/uitje-zooparc-overloon-nl.json'),
        },
        'uitje': True,
    },
    # Uitjes met een arrangementkaart (arr-bron) i.p.v. de kamerslider. Ontbreekt het JSON nog, dan slaat een volledige
    # build (zonder argument) het uitje over; met de entry als argument stopt de build met een fout.
    'uitje-oorlogsmuseum-overloon': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('oorlogsmuseum-overloon-v2.html', 'translations/uitje-oorlogsmuseum-overloon-nl.json'),
        },
        'uitje': True,
    },
    'uitje-venray-centrum': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('venray-centrum-v2.html', 'translations/uitje-venray-centrum-nl.json'),
        },
        'uitje': True,
    },
    'uitje-nationaal-park-de-maasduinen': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('nationaal-park-de-maasduinen-v2.html', 'translations/uitje-nationaal-park-de-maasduinen-nl.json'),
        },
        'uitje': True,
    },
    # Omgevingspagina's (nov 2026): overzicht + vijf categoriepagina's, nabouw van parkhotelhorst.nl/gebied/ en /gebieden/<cat>/
    # in de Asteria-stijl (omgeving.template.html / omgeving-categorie.template.html + omgeving.css/.js, prefix om-). Kaarten komen
    # bij elke build uit om_register() (alle uitje-/route-/zoek-JSON's die er dan zijn). Taal zonder JSON = overgeslagen.
    'omgeving-overzicht': {'template': 'omgeving.template.html', 'omgeving': 'overzicht', 'langs': {
        'nl': ('omgeving-v2.html', 'translations/omgeving-overzicht-nl.json'),
        'de': ('omgeving-v2-de.html', 'translations/omgeving-overzicht-de.json'),
        'en': ('omgeving-v2-en.html', 'translations/omgeving-overzicht-en.json')}},
    'omgeving-cultuur': {'template': 'omgeving-categorie.template.html', 'omgeving': 'cultuur', 'langs': {
        'nl': ('omgeving-cultuur-v2.html', 'translations/omgeving-cultuur-nl.json'),
        'de': ('omgeving-cultuur-v2-de.html', 'translations/omgeving-cultuur-de.json'),
        'en': ('omgeving-cultuur-v2-en.html', 'translations/omgeving-cultuur-en.json')}},
    'omgeving-dagje-uit': {'template': 'omgeving-categorie.template.html', 'omgeving': 'dagje-uit', 'langs': {
        'nl': ('omgeving-dagje-uit-v2.html', 'translations/omgeving-dagje-uit-nl.json'),
        'de': ('omgeving-dagje-uit-v2-de.html', 'translations/omgeving-dagje-uit-de.json'),
        'en': ('omgeving-dagje-uit-v2-en.html', 'translations/omgeving-dagje-uit-en.json')}},
    'omgeving-natuur': {'template': 'omgeving-categorie.template.html', 'omgeving': 'natuur', 'langs': {
        'nl': ('omgeving-natuur-v2.html', 'translations/omgeving-natuur-nl.json'),
        'de': ('omgeving-natuur-v2-de.html', 'translations/omgeving-natuur-de.json'),
        'en': ('omgeving-natuur-v2-en.html', 'translations/omgeving-natuur-en.json')}},
    'omgeving-shoppen-steden': {'template': 'omgeving-categorie.template.html', 'omgeving': 'shoppen-steden', 'langs': {
        'nl': ('omgeving-shoppen-steden-v2.html', 'translations/omgeving-shoppen-steden-nl.json'),
        'de': ('omgeving-shoppen-steden-v2-de.html', 'translations/omgeving-shoppen-steden-de.json'),
        'en': ('omgeving-shoppen-steden-v2-en.html', 'translations/omgeving-shoppen-steden-en.json')}},
    'omgeving-golf': {'template': 'omgeving-categorie.template.html', 'omgeving': 'golf', 'langs': {
        'nl': ('omgeving-golf-v2.html', 'translations/omgeving-golf-nl.json'),
        'de': ('omgeving-golf-v2-de.html', 'translations/omgeving-golf-de.json'),
        'en': ('omgeving-golf-v2-en.html', 'translations/omgeving-golf-en.json')}},
    'uitje-kasteeltuinen-arcen': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('kasteeltuinen-arcen-v2.html', 'translations/uitje-kasteeltuinen-arcen-nl.json'),
            'de': ('kasteeltuinen-arcen-v2-de.html', 'translations/uitje-kasteeltuinen-arcen-de.json'),
            'en': ('kasteeltuinen-arcen-v2-en.html', 'translations/uitje-kasteeltuinen-arcen-en.json'),
        },
        'uitje': True,
    },
    'uitje-hertog-jan-brouwerij': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('hertog-jan-brouwerij-v2.html', 'translations/uitje-hertog-jan-brouwerij-nl.json'),
            'de': ('hertog-jan-brouwerij-v2-de.html', 'translations/uitje-hertog-jan-brouwerij-de.json'),
            'en': ('hertog-jan-brouwerij-v2-en.html', 'translations/uitje-hertog-jan-brouwerij-en.json'),
        },
        'uitje': True,
    },
    'uitje-mind-mystery': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('mind-mystery-v2.html', 'translations/uitje-mind-mystery-nl.json'),
            'de': ('mind-mystery-v2-de.html', 'translations/uitje-mind-mystery-de.json'),
            'en': ('mind-mystery-v2-en.html', 'translations/uitje-mind-mystery-en.json'),
        },
        'uitje': True,
    },
    'uitje-designer-outlet-roermond': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('designer-outlet-roermond-v2.html', 'translations/uitje-designer-outlet-roermond-nl.json'),
            'de': ('designer-outlet-roermond-v2-de.html', 'translations/uitje-designer-outlet-roermond-de.json'),
            'en': ('designer-outlet-roermond-v2-en.html', 'translations/uitje-designer-outlet-roermond-en.json'),
        },
        'uitje': True,
    },
    'uitje-venlo-centrum': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('venlo-centrum-v2.html', 'translations/uitje-venlo-centrum-nl.json'),
            'de': ('venlo-centrum-v2-de.html', 'translations/uitje-venlo-centrum-de.json'),
            'en': ('venlo-centrum-v2-en.html', 'translations/uitje-venlo-centrum-en.json'),
        },
        'uitje': True,
    },
    'uitje-de-groote-peel': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('de-groote-peel-v2.html', 'translations/uitje-de-groote-peel-nl.json'),
            'de': ('de-groote-peel-v2-de.html', 'translations/uitje-de-groote-peel-de.json'),
            'en': ('de-groote-peel-v2-en.html', 'translations/uitje-de-groote-peel-en.json'),
        },
        'uitje': True,
    },
    'uitje-openluchtmuseum-de-locht': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('openluchtmuseum-de-locht-v2.html', 'translations/uitje-openluchtmuseum-de-locht-nl.json'),
            'de': ('openluchtmuseum-de-locht-v2-de.html', 'translations/uitje-openluchtmuseum-de-locht-de.json'),
            'en': ('openluchtmuseum-de-locht-v2-en.html', 'translations/uitje-openluchtmuseum-de-locht-en.json'),
        },
        'uitje': True,
    },
    'uitje-limburgs-museum': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('limburgs-museum-v2.html', 'translations/uitje-limburgs-museum-nl.json'),
            'de': ('limburgs-museum-v2-de.html', 'translations/uitje-limburgs-museum-de.json'),
            'en': ('limburgs-museum-v2-en.html', 'translations/uitje-limburgs-museum-en.json'),
        },
        'uitje': True,
    },
    'uitje-toverland': {
        'template': 'uitje.template.html',
        'langs': {
            'nl': ('toverland-v2.html', 'translations/uitje-toverland-nl.json'),
            'de': ('toverland-v2-de.html', 'translations/uitje-toverland-de.json'),
            'en': ('toverland-v2-en.html', 'translations/uitje-toverland-en.json'),
        },
        'uitje': True,
    },
}

def add_mews_language(html, lang):
    """Voeg &language=<code> toe aan alle Mews-deeplink-URL's. Alleen EN/DE;
    NL blijft byte-identiek. Dekt statische hrefs, JS-deeplinks met/zonder
    voucher en de openBooking params-array."""
    code = {'en': 'en-US', 'de': 'de-DE'}.get(lang)
    if not code:
        return html
    q = '&language=' + code
    # 1. Statische voucher-URL (href/string met inline code): ?mewsVoucherCode=CODE
    html = re.sub(r'(mewsVoucherCode=[A-Za-z0-9_-]+)', r'\1' + q, html)
    # 2. JS-deeplink MET voucher (arrangementen): '?mewsVoucherCode=' + VOUCHER
    html = html.replace(
        "+ '?mewsVoucherCode=' + VOUCHER",
        "+ '?mewsVoucherCode=' + VOUCHER + '" + q + "'")
    # 3. JS-deeplink ZONDER voucher (kamers): MEWS_BASE + '?mewsStart=' + toYMD(checkin)
    html = html.replace(
        "MEWS_BASE + '?mewsStart=' + toYMD(checkin)",
        "MEWS_BASE + '?mewsStart=' + toYMD(checkin) + '" + q + "'")
    # 4. openBooking params-array (kamers): var params = [];
    html = html.replace(
        "var params = [];",
        "var params = ['language=" + code + "'];")
    # 5. Inline Mews-widget: de Distributor-config negeert 'language:', dus taal
    #    via de API-methode zetten zodra de widget klaar is (dit is wat de
    #    boekingsmodule daadwerkelijk in de juiste taal opent).
    html = html.replace(
        "window.mewsApi=api;",
        "window.mewsApi=api;if(api.setLanguageCode)api.setLanguageCode('" + code + "');")
    return html


# Detailpagina-media per kamer (bron van waarheid: kamerdetailpagina's /
# build_kamers.slides_for). Video eerst, dan foto's in detailvolgorde.
DETAIL_MEDIA = {
    'comfort':      ('videos/comfort.mp4',      ['fotos/kamer-comfort-a.webp', 'fotos/kamer-comfort-b.webp', 'fotos/kamer-comfort-c.webp', 'fotos/kamer-comfort-d.webp']),
    'comfort-3':    ('videos/comfort-3.mp4',    ['fotos/room-comfort-3-1.webp', 'fotos/room-comfort-3-2.webp', 'fotos/room-comfort-3-3.webp', 'fotos/room-comfort-3-4.webp']),
    'mindervalide': ('videos/mindervalide.mp4', ['fotos/room-mindervalide-1.webp', 'fotos/room-mindervalide-2.webp', 'fotos/room-mindervalide-3.webp', 'fotos/room-mindervalide-4.webp']),
    'royale':       ('videos/royale.mp4',       ['fotos/room-royale-1.webp', 'fotos/room-royale-2.webp', 'fotos/room-royale-3.webp', 'fotos/room-royale-4.webp']),
    'deluxe':       ('videos/deluxe.mp4',       ['fotos/room-deluxe-1.webp', 'fotos/room-deluxe-2.webp', 'fotos/room-deluxe-3.webp', 'fotos/room-deluxe-4.webp']),
    'junior-suite': (None,                       ['fotos/kamer-junior-suite.webp', 'fotos/kamer-junior-suite-2.webp']),
    'suite':        ('videos/suite.mp4',        ['fotos/room-suite-1.webp', 'fotos/room-suite-2.webp', 'fotos/room-suite-3.webp', 'fotos/room-suite-4.webp']),
    'bruidssuite':  ('videos/bruidssuite.mp4',  ['fotos/room-bruidssuite-1.webp', 'fotos/room-bruidssuite-2.webp', 'fotos/room-bruidssuite-3.webp', 'fotos/room-bruidssuite-4.webp']),
}


def fix_room_media(html):
    """Zet in alle ROOMS-objecten de kamer-media gelijk aan de detailpagina's
    (video + volledige fotoset in detailvolgorde). Alleen objecten met 'imgs:'
    (de room-datasets) worden aangeraakt."""
    for key, (video, imgs) in DETAIL_MEDIA.items():
        imgs_js = '[' + ', '.join("'" + s + "'" for s in imgs) + ']'
        vid_js = ("'" + video + "'") if video else 'null'
        for q in ("'", '"'):
            marker = q + key + q + ':'
            pos = 0
            while True:
                p = html.find(marker, pos)
                if p == -1:
                    break
                b = html.find('{', p)
                if b == -1 or b - (p + len(marker)) > 3:
                    pos = p + len(marker); continue
                depth = 0; j = b
                while j < len(html):
                    if html[j] == '{': depth += 1
                    elif html[j] == '}':
                        depth -= 1
                        if depth == 0: break
                    j += 1
                obj = html[b:j + 1]
                if 'imgs:' not in obj:
                    pos = j + 1; continue
                new_obj = re.sub(r"imgs:\s*\[[^\]]*\]", "imgs: " + imgs_js, obj, count=1)
                if re.search(r"video:\s*('[^']*'|null|None)", new_obj):
                    new_obj = re.sub(r"video:\s*('[^']*'|null|None)", "video: " + vid_js, new_obj, count=1)
                else:
                    new_obj = '{ video: ' + vid_js + ',' + new_obj[1:]
                html = html[:b] + new_obj + html[j + 1:]
                pos = b + len(new_obj)
    return html


def inject_welkom_booking():
    """Geef de welkom-pagina's dezelfde 3-staps boekingsmodule als de
    arrangementen (inline Mews-widget + datepicker-overlay), met de welkom-
    voucher. Bron per taal = de al-gebouwde, gelokaliseerde arrangementpagina.
    Idempotent via <!--WELKOM-BK--> markers; CTA-deeplinks worden herbedraad
    naar window.openBookingPopup(). Draait als post-stap na build('welkom')."""
    SRC = {
        '-oud': ('happy-summer-arrangement.html',   'WELKOM'),   # oude NL-lander (welkom-oud.html)
        '-en': ('happy-summer-arrangement-en.html', 'WELCOME'),
        '-de': ('happy-summer-arrangement-de.html', 'WILLKOMMEN'),
    }
    START, END = '<!--WELKOM-BK-START-->', '<!--WELKOM-BK-END-->'
    for suffix, (arr_file, voucher) in SRC.items():
        welkom_path = os.path.join(base, 'welkom' + suffix + '.html')
        arr_path = os.path.join(base, arr_file)
        if not (os.path.exists(welkom_path) and os.path.exists(arr_path)):
            print(f'  [welkom-booking/{suffix or "nl"}] overgeslagen (bron ontbreekt)')
            continue
        arr = open(arr_path, encoding='utf-8').read()
        w = open(welkom_path, encoding='utf-8').read()

        def between(a, b, inclusive_end=True):
            i = arr.index(a); j = arr.index(b, i)
            return arr[i:(j + len(b)) if inclusive_end else j]

        def enclosing_script(keyword):
            k = arr.index(keyword)
            s = arr.rindex('<script', 0, k)
            e = arr.index('</script>', k) + len('</script>')
            return arr[s:e]

        mews_head = between('<!-- Mews BookingEngine -->', '<!-- End Mews BookingEngine -->')
        cs = arr.rindex('/*', 0, arr.index('.bk-overlay {'))
        ce = arr.rindex('/*', 0, arr.index('.ec-overlay {'))
        bk_css = arr[cs:ce].rstrip()
        bk_markup = between('<div class="bk-overlay"', '<!-- ══ DINER', inclusive_end=False).rstrip()
        dp_js = enclosing_script('MONTH_NAMES')
        bk_js = enclosing_script('/* ══ BOOKING POPUP')

        # Welkom-voucher in de booking-JS zetten (arrangement had z'n eigen code)
        bk_js = re.sub(r"var VOUCHER\s*=\s*'[^']*';",
                       "var VOUCHER = '" + voucher + "';", bk_js, count=1)

        # Meerprijzen (upgrade-labels als '+€10 p.n.') uit de kamerkeuze-stap
        # halen: welkom is een algemeen welkomstaanbod, niet arrangement-specifiek.
        # De echte beschikbaarheidsprijs (priceLabel) blijft staan.
        bk_js = re.sub(r"upgrade:\s*'[^']*'", "upgrade: ''", bk_js)

        # Oude injectie verwijderen (idempotent)
        w = re.sub(re.escape(START) + '.*?' + re.escape(END), '', w, flags=re.S)

        # In <head>: widget-script + overlay-CSS
        head_block = ('\n' + START + '\n' + mews_head + '\n<style>\n' + bk_css
                      + '\n</style>\n' + END + '\n')
        w = w.replace('</head>', head_block + '</head>', 1)

        # Vóór </body>: overlay-markup + datepicker-JS + booking-JS
        body_block = ('\n' + START + '\n' + bk_markup + '\n' + dp_js + '\n'
                      + bk_js + '\n' + END + '\n')
        w = w.replace('</body>', body_block + '</body>', 1)

        # CTA's: Mews-deeplinks vervangen door de popup-trigger
        w = re.sub(r'href="https://app\.mews\.com/distributor/[^"]*"',
                   'href="#" onclick="window.openBookingPopup();return false;"', w)

        with open(welkom_path, 'w', encoding='utf-8') as f:
            f.write(w)
        print(f'  [welkom-booking/{suffix or "nl"}] geinjecteerd (voucher {voucher})')


def inject_reviews(html, reviews_file, max_kaarten=24, max_tekens=260, voorkeur=None):
    """Vul de reviewmuur (lander-w1, blok 5a) uit een Google-reviews-JSON
    (formaat zoals zaalzeven-pages/content/reviews-google.json). Vervangt
    <!-- REVIEWS --> door maximaal 24 kaarten en vult {{GOOGLE_PROFIEL}} /
    {{GOOGLE_REVIEW_URL}} met profiel_url / review_url uit de JSON als de
    vertalings-JSON ze niet al gaf. Lange teksten worden op een woordgrens
    afgekapt (ongeveer 260 tekens) met een beletselteken.
    Arrangementen: 'voorkeur' = woorden (bijv. sauna, diner, ontbijt); reviews die er een noemen komen eerst
    (verder de volgorde van de JSON). {{REVIEWS_AANTAL}} wordt het aantal Google-reviews uit de JSON (2.280)."""
    from html import escape
    with open(os.path.join(base, reviews_file), encoding='utf-8') as f:
        data = json.load(f)
    ster = ('<svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 '
            '17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>')
    kaarten = []
    reviews = list(data.get('reviews') or [])
    if voorkeur:
        noemt = lambda r: any(w in (r.get('tekst') or '').lower() for w in voorkeur)
        reviews = [r for r in reviews if noemt(r)] + [r for r in reviews if not noemt(r)]
    for r in reviews[:max_kaarten]:
        tekst = ' '.join((r.get('tekst') or '').split())
        if len(tekst) > max_tekens:
            tekst = tekst[:max_tekens].rsplit(' ', 1)[0].rstrip(' ,.;:!?') + ' \u2026'
        n = max(1, min(5, int(r.get('sterren') or 5)))
        datum = (r.get('datum') or '').strip()
        meta = (escape(datum) + ' &middot; Google') if datum else 'Google'
        kaarten.append(
            '      <article class="kaart b5a-kaart">\n'
            f'        <span class="b5a-k-sterren" role="img" aria-label="{n} van 5 sterren">{ster * n}</span>\n'
            f'        <p>\u201c{escape(tekst, quote=False)}\u201d</p>\n'
            f'        <p class="b5a-naam">{escape(r.get("naam") or "Gast", quote=False)}<span>{meta}</span></p>\n'
            '      </article>')
    if not kaarten:
        print(f'  WARNING: geen reviews in {reviews_file}')
    html = html.replace('<!-- REVIEWS -->', '\n'.join(kaarten))
    profiel = data.get('profiel_url') or 'https://www.google.com/maps/search/?api=1&query=Hotel+Asteria+Venray'
    schrijf = data.get('review_url') or profiel
    if data.get('aantal'):
        html = html.replace('{{REVIEWS_AANTAL}}', f"{int(data['aantal']):,}".replace(',', '.'))
    html = html.replace('{{GOOGLE_PROFIEL}}', escape(profiel)).replace('{{GOOGLE_REVIEW_URL}}', escape(schrijf))
    return html


LADDER_ICOON = {
    'm2': '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
    'bed': '<path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8M2 16h20M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/>',
    'personen': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    'sauna': '<path d="M14 14.8V4a2 2 0 0 0-4 0v10.8a4 4 0 1 0 4 0z"/>',
    'bad': '<path d="M12 2.7l5.7 5.7a8 8 0 1 1-11.3 0z"/>',
    'zit': '<path d="M5 11V8a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v3M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM6 19v2M18 19v2"/>',
}


def render_ladder(cfg):
    """Upgradeblok 'A · Ladder-slider' (blok 3a-variant 'ladder') uit UPGRADE_LADDER in de vertalings-JSON:
    per stap twee kamerkaarten 'Je boekt' -> 'Upgrade' met een pijl, de winstregel eronder; teller,
    streepjes en vorige/volgende-knoppen erboven, één vaste voetregel. Eén stap per keer, geen lus,
    geen boekknop, geen prijzen. Vervangt <!-- UPGRADE_LADDER --> in lander-w1.template.html."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')
    ic = lambda pad, kl='as-icoon': f'<svg class="{kl}" viewBox="0 0 24 24" aria-hidden="true">{pad}</svg>'
    lab = cfg.get('labels', {})
    kamers, stappen = cfg['kamers'], cfg['stappen']
    n = len(stappen)

    def kaart(sleutel, upgrade):
        k = kamers[sleutel]
        specs = ''.join(f'<li><span class="b3l-ic">{ic(LADDER_ICOON[s[0]])}</span>{e(s[1])}</li>' for s in k['specs'])
        pil = (f'<span class="b3l-pil b3l-pil--up">{ic(LADDER_PIJL["op"])}{e(lab.get("upgrade", "Upgrade"))}</span>'
               if upgrade else f'<span class="b3l-pil">{e(lab.get("boekt", "Je boekt"))}</span>')
        return (f'<article class="b3l-kaart{" b3l-kaart--up" if upgrade else ""}">'
                f'<div class="b3l-foto"><img src="{a(k["foto"])}" alt="{a(k["alt"])}" width="1400" height="933" loading="lazy">{pil}</div>'
                f'<div class="b3l-inhoud">{pil}<h3>{e(k["naam"])}</h3><ul class="b3l-specs">{specs}</ul></div></article>')

    blokken = []
    for i, s in enumerate(stappen):
        van, naar = kamers[s['van']]['naam'], kamers[s['naar']]['naam']
        blokken.append(
            f'        <div class="b3l-stap" role="group" aria-roledescription="stap" aria-label="Stap {i + 1} van {n}: {a(van)} naar {a(naar)}"'
            + ('' if i == 0 else ' aria-hidden="true"') + '>\n'
            f'          <div class="b3l-route">{kaart(s["van"], False)}<span class="b3l-pijl" aria-hidden="true">'
            f'{ic(LADDER_PIJL["rechts"], "as-icoon b3l-pijl-r")}{ic(LADDER_PIJL["omlaag"], "as-icoon b3l-pijl-o")}</span>{kaart(s["naar"], True)}</div>\n'
            f'          <p class="b3l-winst"><span class="b3l-vink">{ic(LADDER_PIJL["vink"])}</span><span><b>{e(lab.get("erbij", "Je krijgt erbij:"))}</b> {e(s["winst"])}</span></p>\n'
            '        </div>')
    dots = ''.join(
        f'<button type="button" class="b3l-dot{" is-active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
        f'aria-label="Stap {i + 1}: {a(kamers[s["van"]]["naam"])} naar {a(kamers[s["naar"]]["naam"])}"></button>'
        for i, s in enumerate(stappen))
    nav = (f'      <div class="b3l-nav"><span class="b3l-tel" aria-live="polite"><b class="b3l-nu">1</b> van <b>{n}</b></span>'
           f'<div class="b3l-dots" role="tablist" aria-label="Upgradestappen">{dots}</div>'
           f'<div class="b3l-pijlen"><button type="button" class="as-pijl b3l-vorige" aria-label="Vorige stap" aria-disabled="true">{ic(LADDER_PIJL["links"])}</button>'
           f'<button type="button" class="as-pijl b3l-volgende" aria-label="Volgende stap">{ic(LADDER_PIJL["chev-r"])}</button></div></div>\n')
    return ('<div class="b3l" aria-roledescription="carrousel" aria-label="Zo ziet je upgrade eruit">\n' + nav
            + '      <div class="b3l-spoor strook-scroll" tabindex="0" aria-label="Upgradestappen, schuif of gebruik de pijltjestoetsen">\n'
            + '\n'.join(blokken) + '\n      </div>\n'
            + f'      <p class="b3l-voet">{e(cfg.get("voet"))}</p>\n    </div>')


def render_cadeau(items, voet):
    """Cadeaublok (blok 3a-variant 'cadeau') uit CADEAU_ITEMS in de vertalings-JSON: drie fotokaarten naast
    elkaar in de kaartstijl van het upgradeblok (b3l-kaart) met badge (standaard 'Gratis'), naam en één regel,
    daaronder één voetregel (CADEAU_VOET). Geen boekknop, geen prijzen. Telefoon: kaarten onder elkaar, foto
    links. Vervangt <!-- CADEAU_ITEMS --> in lander-w1.template.html; de intro is de tekst-key CADEAU_INTRO."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')

    def kaart(it):
        pil = f'<span class="b3l-pil b3l-pil--up">{e(it.get("badge", "Gratis"))}</span>'
        return (f'        <article class="b3l-kaart b3c-kaart" role="listitem">'
                f'<div class="b3l-foto"><img src="{a(it["foto"])}" alt="{a(it["alt"])}" width="1200" height="800" loading="lazy">{pil}</div>'
                f'<div class="b3l-inhoud">{pil}<h3>{e(it["naam"])}</h3><p class="b3c-regel">{e(it["regel"])}</p></div></article>')

    return ('<div class="b3c">\n      <div class="b3c-rij" role="list">\n'
            + '\n'.join(kaart(it) for it in items) + '\n      </div>\n'
            + f'      <p class="b3l-voet b3c-voet">{e(voet)}</p>\n    </div>')


LADDER_PIJL = {
    'links': '<path d="M15 18l-6-6 6-6"/>',
    'chev-r': '<path d="M9 18l6-6-6-6"/>',
    'rechts': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'omlaag': '<path d="M12 5v14M6 13l6 6 6-6"/>',
    'op': '<path d="M12 19V5M5 12l7-7 7 7"/>',
    'vink': '<path d="M20 6L9 17l-5-5"/>',
}


ATTENTIE_ICOON_STANDAARD = {
    'PUNT_TWEE_ICOON': '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
    'PUNT_DRIE_ICOON': '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    'PUNT_VIJF_ICOON': '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M9 16l2 2 4-4"/>',
}


PIJL_SVG = ('<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/>'
            '<polyline points="12 5 19 12 12 19"/></svg>')


def spiegel_linkset():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations', 'spiegel-links.json'), encoding='utf-8') as f:
        return json.load(f)


def spiegel_adres(sleutel, links=None):
    """Sleutel uit translations/spiegel-links.json -> adres ('arrangementen' = het arrangementenoverzicht)."""
    links = links or spiegel_linkset()
    if sleutel == 'arrangementen':
        return links['arrangementenoverzicht']
    if sleutel not in links['paginas']:
        sys.exit(f'spiegel: onbekende sleutel {sleutel!r} (zie translations/spiegel-links.json)')
    return links['paginas'][sleutel]


def vul_spiegel_links(html):
    """Spiegelstand: href="spiegel:<sleutel>" (sjabloon, JSON-velden) en "info": "spiegel:<sleutel>" (pop-updata) -> adres.
    Daarna mag er geen link naar asteria.nl meer staan, behalve privacy en algemene voorwaarden."""
    links = spiegel_linkset()
    html = re.sub(r'spiegel:([a-z][a-z0-9-]*)', lambda m: spiegel_adres(m.group(1), links), html)
    rest = [u for u in re.findall(r'(?:href="|"link": ")(https://www\.asteria\.nl[^"]*)"', html)
            if u not in ('https://www.asteria.nl/privacy', 'https://www.asteria.nl/algemene-voorwaarden')]
    if rest:
        sys.exit(f'spiegel: nog links naar asteria.nl: {rest[:5]}')
    return html


# asteria.nl-pagina -> sleutel van de spiegel (inhoudslinks op het arrangementenoverzicht; andere asteria.nl-links blijven)
SPIEGEL_INHOUD = {'/kamers': 'kamers', '/wellness': 'wellness', '/restaurant': 'restaurant', '/omgeving': 'omgeving',
                  '/contact': 'contact', '/faciliteiten': 'faciliteiten', '/over-ons': 'over-ons'}


def spiegel_inhoud(html):
    """Inhoudslinks naar spiegeladressen: asteria.nl-pagina's uit SPIEGEL_INHOUD en de kamerpagina's in #lp-kamerdata
    ("pagina": oude kamerpagina's op visit.asteria.nl -> spiegel- of kamer-w1-detailpagina, Junior Suite het kameroverzicht)."""
    links = spiegel_linkset()
    kamerpagina = {'/comfort-kamer': 'kamer-comfort', '/deluxe-kamer': 'kamer-deluxe', '/royale-kamer': 'kamer-royale',
                   '/suite': 'kamer-suite', '/bruidssuite': 'kamer-bruidssuite', '/comfort-kamer-3-personen': 'kamer-comfort-3',
                   '/mindervalide-kamer': 'kamer-mindervalide'}
    html = html.replace('<a class="lp-pop__link" href="/">', f'<a class="lp-pop__link" href="{spiegel_adres("kamers", links)}">')
    html = re.sub(r'("pagina": )"(/[a-z0-9-]+)"', lambda m: f'{m.group(1)}"{spiegel_adres(kamerpagina.get(m.group(2), "kamers"), links)}"', html)
    return re.sub(r'href="https://www\.asteria\.nl(/[a-z-]+)/?"',
                  lambda m: f'href="{spiegel_adres(SPIEGEL_INHOUD[m.group(1)], links)}"' if m.group(1) in SPIEGEL_INHOUD else m.group(0), html)


# Kamerkaarten (blok 4b) in de spiegelstand (hotel-venray-v2): 'Bekijk kamer' opent geen pop-up maar de detailpagina
# (Comfort/Deluxe = spiegel, de andere vijf = kamer-w1 onder /kamers/). Junior Suite houdt de pop-up (geen detailpagina).
KAART_DETAIL = {'comfort': 'kamer-comfort', 'comfort-3': 'kamer-comfort-3', 'mindervalide': 'kamer-mindervalide',
                'royale': 'kamer-royale', 'deluxe': 'kamer-deluxe', 'suite': 'kamer-suite', 'bruidssuite': 'kamer-bruidssuite'}


def kamerkaart_links(html):
    def vervang(m):
        sleutel = m.group(1)
        if sleutel not in KAART_DETAIL:
            return m.group(0)
        return f'<a class="btn btn-secondary btn--klein" href="spiegel:{KAART_DETAIL[sleutel]}" aria-label="{m.group(2)}">Bekijk kamer</a>'
    return re.sub(r'<button type="button" class="btn btn-secondary btn--klein" data-kamer="([a-z0-9-]+)" aria-haspopup="dialog" '
                  r'aria-label="([^"]*)">Bekijk kamer</button>', vervang, html)


# asteria.nl-pad uit de pop-updata -> sleutel van de spiegel (Meer informatie in de faciliteit-pop-up)
SPIEGEL_POP = {'/wellness': 'wellness', '/restaurant': 'restaurant', '/faciliteiten': 'faciliteiten', '/omgeving': 'omgeving'}


def render_hotel(html, data, gesloten=False, spiegel=False):
    """Blok 'hotel' (algemene lander hotel-venray-v2): vult de drie hotelblokken uit lijsten in de JSON.
      _faciliteiten: precies 5 tegels {titel, regel, img, alt, pos?, knop, url | fac} (fac = sleutel in #lp-facdata: 'wellness',
                     'restaurant' of een sleutel uit _facdata; opent de faciliteit-pop-up van lander-w1); tegel 2 en 3 zijn breed
                     (mozaiek zoals Parkhotel); op de telefoon het tegelmozaiek van de staging-homepage (hotel.css).
      _facdata:      extra pop-ups {sleutel: {titel, link, fotos[4], tekst, chips[4]}}, achter de vaste wellness/restaurant in #lp-facdata.
      _fac_video:    {sleutel: videopad} = video als eerste beeld in die pop-up (lander-w1.js vulFac; reduced motion = foto).
      _fac_extra:    lijst {tekst, icoon} onder de tekst van de faciliteitenkaart (icoon = svg-paden).
      _omgeving:     3 tot 6 plekken {naam, afstand, label, img, alt, pos?, fac} (omgevingsblok van de staging-homepage):
                     label = pil op de foto, fac = sleutel in _facdata (pop-up; daar ook 'route' = Google Maps-link,
                     'credit' = fotoregel en 'alts' = alt-teksten per foto). De eerste plek staat bij het laden op de foto.
      _arrangementen: 3 tot 8 kaarten {naam, regel, url, img, alt, pos?}; geen prijzen."""
    from html import escape
    fac = data.get('_faciliteiten') or []
    if '<!-- HO_FAC -->' in html and len(fac) != 5:
        sys.exit(f'render_hotel: _faciliteiten moet 5 tegels hebben, niet {len(fac)}')
    tegels = []
    for i, t in enumerate(fac):
        breed = ' ho-fac-breed' if i in (1, 2) else ''
        pos = f' style="object-position:{t["pos"]}"' if t.get('pos') else ''
        if t.get('fac'):
            knop = (f'<button type="button" class="btn btn-outline-light btn--klein" data-fac="{t["fac"]}" aria-haspopup="dialog" '
                    f'aria-label="Meer info over {escape(t["titel"].lower())}">{t["knop"]}</button>')
        else:
            knop = f'<a class="btn btn-outline-light btn--klein" href="{t["url"]}">{t["knop"]}</a>'
        tegels.append(
            f'        <div class="ho-fac-tegel{breed}">\n'
            f'          <img src="{t["img"]}" alt="{t["alt"]}"{pos} loading="lazy">\n'
            f'          <div class="ho-fac-tekst"><h3>{t["titel"]}</h3><p>{t["regel"]}</p>{knop}</div>\n'
            '        </div>')
    html = html.replace('<!-- HO_FAC -->', '\n'.join(tegels))
    if spiegel:   # Meer informatie in de pop-up = spiegelpagina; de knop blijft Bekijk beschikbaarheid
        def pop_info(m):
            pad = m.group(2).rstrip('/')
            return f'{m.group(1)}"", "info": "spiegel:{SPIEGEL_POP[pad]}"' if pad in SPIEGEL_POP else m.group(0)
        html = re.sub(r'("link": )"https://www\.asteria\.nl(/[^"]*)"', pop_info, html)
    if gesloten:   # geen asteria.nl-links in de pop-updata (de knop is dan Bekijk beschikbaarheid)
        html = re.sub(r'("link": )"https://www\.asteria\.nl[^"]*"', r'\1""', html)
    extra = data.get('_facdata') or {}
    if spiegel:
        def info(k, v):
            pad = urllib.parse.urlsplit(v.get('link') or '').path.rstrip('/') if 'asteria.nl' in (v.get('link') or '') else ''
            if pad in SPIEGEL_POP:
                return dict(v, info='spiegel:' + SPIEGEL_POP[pad])
            if k.startswith('omg-'):
                return dict(v, info='spiegel:omgeving')
            return v
        extra = {k: info(k, v) for k, v in extra.items()}
    if gesloten:
        extra = {k: dict(v, link='') for k, v in extra.items()}
    # Video in de faciliteit-pop-up ('_fac_video': {sleutel: pad}); wellness/restaurant staan vast in het sjabloon
    for k, pad in (data.get('_fac_video') or {}).items():
        if k in extra:
            extra[k] = dict(extra[k], video=pad)
        else:
            vast = f'\n "{k}": {{\n'
            if vast not in html:
                sys.exit(f'render_hotel: _fac_video {k!r} niet gevonden in #lp-facdata')
            html = html.replace(vast, vast + f'  "video": {json.dumps(pad)},\n', 1)
    html = html.replace('<!-- HO_FACDATA -->', ',\n'.join(
        f' {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in extra.items()))
    html = html.replace('<!-- HO_FAC_EXTRA -->', ''.join(
        f'<li><span class="b3a-ic">{icoon(x["icoon"])}</span><span>{x["tekst"]}</span></li>' for x in data.get('_fac_extra') or []))
    omg = data.get('_omgeving') or []
    if '<!-- HO_OMG -->' in html and not 3 <= len(omg) <= 6:
        sys.exit(f'render_hotel: _omgeving moet 3 tot 6 plekken hebben, niet {len(omg)}')
    # Omgevingsblok van de staging-homepage (.omgeving-list): elke plek is een knop die de foto bovenaan kiest
    # (data-omg-*, lander-w1.js) en met data-fac de faciliteit-pop-up opent (pop-updata in '_facdata').
    a = lambda t: escape(t or '')
    rijen = []
    for r in omg:
        if r.get('fac') and r['fac'] not in (data.get('_facdata') or {}):
            sys.exit(f'render_hotel: _omgeving {r["naam"]!r} verwijst naar onbekende pop-up {r["fac"]!r} (zet hem in _facdata)')
        if not os.path.exists(os.path.join(base, r['img'])):
            sys.exit(f'render_hotel: {r["img"]} bestaat niet')
        rijen.append(
            f'          <li><button type="button" class="omgeving-list__item" data-fac="{a(r["fac"])}" aria-haspopup="dialog" '
            f'aria-label="Bekijk {a(r["naam"])}, {a(r["afstand"])}" data-omg-photo="{a(r["img"])}" data-omg-alt="{a(r["alt"])}" '
            f'data-omg-cat="{a(r["label"])}" data-omg-pos="{a(r.get("pos", "center"))}">'
            f'<span class="oli-name">{escape(r["naam"], quote=False)}</span><span class="oli-distance">{escape(r["afstand"], quote=False)}</span>'
            '<span class="card-more oli-more">Bekijk</span></button></li>')
    html = html.replace('<!-- HO_OMG -->', '\n'.join(rijen))
    if omg:   # de fotokaart begint op de eerste plek
        eerste = omg[0]
        for k, v in (('OMG_IMG', eerste['img']), ('OMG_ALT', eerste['alt']), ('OMG_IMG_POS', eerste.get('pos', 'center')),
                     ('OMG_LABEL', eerste['label']), ('OMG_NAAM', eerste['naam'])):
            html = html.replace('{{' + k + '}}', a(v) if k in ('OMG_IMG', 'OMG_ALT', 'OMG_IMG_POS') else escape(v, quote=False))
    arr = data.get('_arrangementen') or []
    if not 3 <= len(arr) <= 8:
        sys.exit(f'render_hotel: _arrangementen moet 3 tot 8 kaarten hebben, niet {len(arr)}')
    kaarten = []
    for a in arr:
        pos = f' style="object-position:{a["pos"]}"' if a.get('pos') else ''
        kaarten.append(
            f'        <a class="ho-arr-kaart" href="{a["url"]}">\n'
            f'          <span class="ho-arr-foto"><img src="{a["img"]}" alt="{a["alt"]}"{pos} loading="lazy"></span>\n'
            f'          <span class="ho-arr-tekst"><span class="ho-arr-naam">{a["naam"]}</span><span class="ho-arr-regel">{a["regel"]}</span>'
            f'<span class="ho-arr-rond" aria-hidden="true">{PIJL_SVG}</span></span>\n'
            '        </a>')
    return html.replace('<!-- HO_ARR -->', '\n'.join(kaarten))


# Mews-categorie per kamer (config 6dc9094c; gelijk aan CATEGORY in build_kamers.py). Junior Suite staat niet op kamertypes-v2.
KAMER_MEWS = {'comfort': '98900f3b-e5e2-49c9-9776-af1d00ffc315', 'comfort-3': '85ca19d7-eea5-41c8-8b93-af1d00ffc315',
              'mindervalide': 'fa5b6540-7234-49ce-beb1-af1d00ffc315', 'royale': 'a8fd7310-0d61-422f-89e6-af1d00ffc315',
              'deluxe': 'c737de50-e41e-4c8d-a818-af1d00ffc315', 'suite': '4a642b66-68e6-444c-beeb-af1d00ffc315',
              'bruidssuite': 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'}
KT_SPEC_ICOON = {
    'douche': '<path d="M4 21V7a3 3 0 0 1 3-3h1a3 3 0 0 1 3 3"/><path d="M8 10h6"/><path d="M9 14v.01M12 14v.01M15 14v.01M10.5 17v.01M13.5 17v.01"/>',
    'rolstoel': '<circle cx="10" cy="4" r="1.6"/><path d="M10 7v6h6l2 5"/><path d="M7.5 10.6a6 6 0 1 0 7.4 7.6"/>',
}


def render_kamertypes(html, data):
    """Blok 'kamertypes' (kamertypes-v2, nabouw staging /kamers/): vult de kt-blokken uit lijsten in de JSON.
      _filters:  chips [{sleutel, label}], de eerste = alle kamers (sleutel 'alle').
      _kamers:   kaarten in volgorde [{sleutel, naam, tekst, kenmerken[], specs[[icoon, tekst]], fotos[{img, alt, pos?}] (precies 3)}];
                 icoon uit LADDER_ICOON/KT_SPEC_ICOON (m2, bed, personen, sauna, bad, zit, douche, rolstoel); Mews-categorie uit KAMER_MEWS.
                 Knop 'Boek deze kamer' = .mews-open met data-room (lander-w1.js opent de widget op die kamer). Geen prijzen.
      _inbegrepen: tegels [{tekst, icoon}] (Wat in elke kamer klaarstaat).
      _goed_om_te_weten: [{titel, tekst, icoon}].   _faq: [{q, a}] (eerste open)."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')
    iconen = dict(LADDER_ICOON, **KT_SPEC_ICOON)
    kamers = data.get('_kamers') or []
    if not kamers:
        sys.exit('render_kamertypes: _kamers ontbreekt')
    filters = data.get('_filters') or []
    if not filters or filters[0]['sleutel'] != 'alle':
        sys.exit("render_kamertypes: _filters moet beginnen met sleutel 'alle'")
    geldig = {f['sleutel'] for f in filters}
    kaarten = []
    for k in kamers:
        s = k['sleutel']
        if s not in KAMER_MEWS:
            sys.exit(f'render_kamertypes: onbekende of uitgesloten kamer {s!r} (kies uit {", ".join(KAMER_MEWS)})')
        for t in k.get('kenmerken', []):
            if t not in geldig:
                sys.exit(f'render_kamertypes: kenmerk {t!r} van {s} staat niet in _filters')
        fotos = k.get('fotos') or []
        if len(fotos) != 3:
            sys.exit(f'render_kamertypes: {s} heeft {len(fotos)} foto\'s, precies 3 nodig')
        for f in fotos:
            if not os.path.exists(os.path.join(base, f['img'])):
                sys.exit(f'render_kamertypes: {f["img"]} bestaat niet')
        guid = KAMER_MEWS[s]
        naam = k['naam']
        imgs = ''.join(
            f'<img class="kt-dia{" is-actief" if i == 0 else ""}" src="{a(f["img"])}" alt="{a(f["alt"])}"'
            + (f' style="object-position:{a(f["pos"])}"' if f.get('pos') else '')
            + (' aria-hidden="true"' if i else '') + ' loading="lazy" width="1400" height="934">'
            for i, f in enumerate(fotos))
        dots = ''.join(
            f'<button type="button" class="kt-dot{" is-actief" if i == 0 else ""}" data-kt-naar="{i}" aria-label="Foto {i + 1} van {len(fotos)}"'
            + (' aria-current="true"' if i == 0 else '') + '></button>' for i in range(len(fotos)))
        specs = ''.join(f'<li class="kt-spec"><span class="dot" aria-hidden="true">{icoon(iconen[ic])}</span>{e(t)}</li>' for ic, t in k['specs'])
        kaarten.append(
            f'        <article class="kt-kaart" data-kamer="{s}" data-kenmerken="{" ".join(k.get("kenmerken", []))}">\n'
            f'          <div class="kt-foto" data-kt-galerij role="group" aria-roledescription="fotogalerij" aria-label="Foto\'s van de {a(naam)}">\n'
            f'            {imgs}\n'
            f'            <button type="button" class="kt-pijl kt-pijl--vorige" data-kt-stap="-1" aria-label="Vorige foto">{icoon(LADDER_PIJL["links"])}</button>'
            f'<button type="button" class="kt-pijl kt-pijl--volgende" data-kt-stap="1" aria-label="Volgende foto">{icoon(LADDER_PIJL["chev-r"])}</button>\n'
            f'            <div class="kt-dots">{dots}</div>\n'
            '          </div>\n'
            '          <div class="kt-inhoud">\n'
            f'            <h3>{e(naam)}</h3>\n'
            f'            <p class="kt-tekst">{e(k["tekst"])}</p>\n'
            f'            <ul class="kt-specs">{specs}</ul>\n'
            f'            <div class="kt-ctas"><a class="btn btn-primary mews-open" data-room="{guid}" '
            f'href="https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsRoom={guid}&amp;mewsRoute=rooms" '
            f'aria-label="Boek de {a(naam)}">Boek deze kamer</a></div>\n'
            '          </div>\n'
            '        </article>')
    html = html.replace('<!-- KT_KAMERS -->', '\n'.join(kaarten))
    html = html.replace('<!-- KT_TELLING -->', f'<span data-kt-tel>{len(kamers)}</span> <span data-kt-woord>kamertypes</span>')
    html = html.replace('<!-- KT_FILTERS -->', '\n'.join(
        f'        <button type="button" class="kt-chip" data-filter="{a(f["sleutel"])}" aria-pressed="{"true" if i == 0 else "false"}">{e(f["label"])}</button>'
        for i, f in enumerate(filters)))
    html = html.replace('<!-- KT_INBEGREPEN -->', '\n'.join(
        f'        <li class="kt-inb-item"><span class="kt-inb-ic" aria-hidden="true">{icoon(x["icoon"])}</span><span class="kt-inb-tekst">{e(x["tekst"])}</span></li>'
        for x in data.get('_inbegrepen') or []))
    html = html.replace('<!-- KT_GOW -->', '\n'.join(
        f'          <div class="kt-gow-feit"><span class="kt-gow-ic" aria-hidden="true">{icoon(x["icoon"])}</span><div><dt>{e(x["titel"])}</dt><dd>{e(x["tekst"])}</dd></div></div>'
        for x in data.get('_goed_om_te_weten') or []))
    faq = data.get('_faq') or []
    if not 4 <= len(faq) <= 8:
        sys.exit(f'render_kamertypes: _faq moet 4 tot 8 vragen hebben, niet {len(faq)}')
    html = html.replace('<!-- KT_FAQ -->', '\n'.join(
        f'          <details class="as-accordeon__item"{" open" if i == 0 else ""}><summary class="as-accordeon__kop">{e(f["q"])}</summary>'
        f'<div class="as-accordeon__paneel"><p>{e(f["a"])}</p></div></details>'
        for i, f in enumerate(faq)))
    return html


def zonder_voucher(html):
    """Lander zonder actiecode (VOUCHER leeg, bijv. hotel-venray-v2): geen lege mewsVoucherCode in de Mews-links,
    geen lege data-voucher en geen 'met code' in de aria-labels. data-basis van de kamer-pop-up houdt zijn '?'
    (lander-w1.js plakt er '&mewsRoom=' achter)."""
    html = html.replace('?mewsVoucherCode=&amp;', '?')
    html = re.sub(r'href="([^"?]*)\?mewsVoucherCode="', r'href="\1"', html)
    html = html.replace(' data-voucher=""', '')
    html = re.sub(r' met code "', '"', html)
    return html


def apply_blokken(html, aan):
    """Varianten binnen een sjabloon zonder template-taal. Een blok staat tussen
    <!--[naam[--> en <!--]naam]-->; <!--[!naam[--> ... <!--]!naam]--> is het omgekeerde.
    'aan' = de namen die in de build-config op True staan. Staat een blok aan, dan
    verdwijnen alleen de markers; staat hij uit, dan verdwijnt het hele blok. Een marker
    die alleen op zijn regel staat, neemt die regel mee (uitvoer zonder blok blijft dus
    byte-gelijk aan het sjabloon zonder markers)."""
    namen = set(re.findall(r'<!--\[(!?[a-z0-9-]+)\[-->', html))
    for naam in namen:
        kaal = naam.lstrip('!')
        houden = (kaal in aan) != naam.startswith('!')
        n = re.escape(naam)
        if houden:
            html = re.sub(r'(?m)^[ \t]*<!--[\[\]]' + n + r'[\[\]]-->[ \t]*\n', '', html)
            html = re.sub(r'<!--[\[\]]' + n + r'[\[\]]-->', '', html)
        else:
            html = re.sub(r'(?ms)^[ \t]*<!--\[' + n + r'\[-->.*?<!--\]' + n + r'\]-->[ \t]*\n', '', html)
            html = re.sub(r'(?s)<!--\[' + n + r'\[-->.*?<!--\]' + n + r'\]-->', '', html)
    return html


# Pil-iconen per soort in de kamerslider van een arrangement (blok 4b)
PIL_ICOON = {
    'inbegrepen': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>',
    'upgrade': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
    'toeslag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
}


VINK_SVG = ('<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/>'
            '<path d="M8 12.5l2.5 2.5 5.5-6"/></svg>')


def icoon(paden, cls='as-icoon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{paden}</svg>'


def apply_arrangement(html, data):
    """Arrangementblokken uit de lijsten in de JSON (alleen met blok 'arrangement'):
    - '_kamers': welke kamers (blok 4b), in welke volgorde, met pil en prijsregel per kaart, bijv.
      {"deluxe": {"pil": "Inbegrepen", "soort": "inbegrepen", "prijs_label": "vanaf", "prijs": "€ 128,50 p.p."},
       "suite": {"pil": "Upgrade", "soort": "upgrade", "prijs": "Upgrade mogelijk"}}.
      Sleutels = data-kamer in het sjabloon (comfort, comfort-3, royale, deluxe, junior-suite, suite, bruidssuite,
      mindervalide); soort inbegrepen (terracotta rand), upgrade of toeslag. 1 of 2 kamers: raster zonder
      slider, teller en lus (.ar-kamers; telefoon veegbaar met peek). Vanaf 3: de brede slider met lus zoals /bedankt,
      teller en streepjes volgen het aantal.
    - '_chips' (hero), '_inbegrepen' ({titel, regel, icoon}; vakje met lijnicoon, 2 kolommen),
      '_inbegrepen_fotos' ({img, alt, pos?}; fotoslider in het inbegrepen-blok, 4 tot 6), '_tijden' ({tekst, icoon}), '_faq' ({q, a}; eerste open;
      "zondag": true = alleen met ZV_TOON), '_andere' ({naam, url, img, alt, prijs?}).
    - '_banen' (optioneel, 1 tot 4; build-blok 'banen' na 'Dit is inbegrepen'): {naam, plaats, tekst, rijtijd, url, foto, alt,
      pos?, link?}; kaart per golfbaan met foto, naam, plaats · rijtijd, tekst en link (nieuw tabblad). Kop BANEN_KOP_A/EM, BANEN_INTRO.
    - 'ARR_NACHTEN' (getal, standaard 1): vast aantal nachten. Bij meer dan 1 krijgen de boekbalken
      data-nachten; arrangement.js zet het vertrek dan op aankomst + N (balk, widget en URL-fallback).
    - '_fotowolk': 12 foto's ({img, pos?} of een pad) die de vaste foto's van de fotowolk (blok 7a)
      in volgorde vervangen; SLOT_FOTO_A/B blijven staan. Zonder lijst blijft de vaste set."""
    from html import escape
    kamers = data.get('_kamers')
    if kamers:
        s = html.index('<div class="b4b-strook')
        voet = html.index('<div class="b4b-voet">', s)
        start = html.index('<article class="b4b-kaart">', s)
        eind = html.rindex('</article>', s, voet) + len('</article>')
        kaarten = {}
        for m in re.finditer(r'<article class="b4b-kaart">.*?</article>', html[start:eind], re.S):
            kaarten[re.search(r'data-kamer="([^"]+)"', m.group(0)).group(1)] = m.group(0)
        nieuw = []
        for key, cfg in kamers.items():
            if key not in kaarten:
                sys.exit(f'apply_arrangement: onbekende kamer {key!r} (kies uit {", ".join(kaarten)})')
            soort = cfg.get('soort', 'inbegrepen')
            pil = f'<span class="b4b-pil b4b-pil--{soort}">{PIL_ICOON[soort]}{escape(cfg["pil"], quote=False)}</span>'
            k = re.sub(r'<span class="b4b-pil">.*?</span>', lambda _: pil, kaarten[key], count=1, flags=re.S)
            if cfg.get('prijs'):
                lab = f'<span>{escape(cfg["prijs_label"], quote=False)}</span>' if cfg.get('prijs_label') else ''
                regel = f'<div class="ar-kprijs ar-kprijs--{soort}">{lab}<b>{escape(cfg["prijs"], quote=False)}</b></div>\n          '
                k = k.replace('<div class="b4b-knoppen">', regel + '<div class="b4b-knoppen">', 1)
            if soort == 'inbegrepen':
                k = k.replace('<article class="b4b-kaart">', '<article class="b4b-kaart ar-kaart-inbegrepen">', 1)
            nieuw.append(k)
        html = html[:start] + '\n        '.join(nieuw) + html[eind:]
        n = len(nieuw)
        if n <= 2:
            # raster: geen teller/streepjes/pijlen, geen .b4b-strook (dan laat lander-w1.js lus() hem met rust)
            html = re.sub(r'<div class="b4b-teller">.*?</button></div></div>', '', html, count=1, flags=re.S)
            html = html.replace('<div class="b4b-strook strook-scroll" tabindex="0" aria-label="Kamers, schuif voor meer">',
                                f'<div class="ar-kamers strook-scroll" data-n="{n}" aria-label="Kamers">', 1)
        else:
            html = html.replace('van <b>8</b></span>', f'van <b>{n}</b></span>', 1)
            stippen = ''.join(
                f'<button type="button" class="b4b-dot{" is-active" if i == 0 else ""}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-label="Kamer {i + 1}"></button>'
                for i in range(n))
            html = re.sub(r'(<div class="b4b-dots"[^>]*>).*?(</div>)', lambda m: m.group(1) + stippen + m.group(2), html, count=1, flags=re.S)

    chips = ''.join(f'<li>{VINK_SVG}<span>{c}</span></li>' for c in data.get('_chips', []))
    html = html.replace('<!-- ARR_CHIPS -->', chips)
    inb = '\n'.join(
        f'            <li class="ar-inb-punt"><span class="ar-vak">{icoon(p.get("icoon", ""))}</span>'
        f'<span class="ar-inb-tekst"><b>{p["titel"]}</b><span>{p.get("regel", "")}</span></span></li>'
        for p in data.get('_inbegrepen', []))
    html = html.replace('<!-- ARR_INBEGREPEN -->', inb)
    fotos = data.get('_inbegrepen_fotos', [])
    if '<!-- ARR_INB_FOTOS -->' in html and not 4 <= len(fotos) <= 6:
        sys.exit(f'_inbegrepen_fotos: 4 tot 6 foto\'s nodig, niet {len(fotos)}')
    html = html.replace('<!-- ARR_INB_FOTOS -->', '\n'.join(
        f'            <figure class="ar-fs-dia"><img src="{escape(f["img"])}" alt="{escape(f.get("alt", ""))}"'
        + (f' style="object-position:{escape(f["pos"])}"' if f.get('pos') else '')
        + (' loading="lazy"' if i else '') + '></figure>'
        for i, f in enumerate(fotos)))
    html = html.replace('<!-- ARR_INB_BOLLEN -->', ''.join(
        f'<button type="button" class="ar-fs-bol{" is-aan" if i == 0 else ""}" data-fs-naar="{i}" aria-label="Foto {i + 1}"'
        + (' aria-current="true"' if i == 0 else '') + '></button>'
        for i in range(len(fotos))))
    tijden = ''.join(f'<li>{icoon(p.get("icoon", ""))}<span>{p["tekst"]}</span></li>' for p in data.get('_tijden', []))
    html = html.replace('<!-- ARR_TIJDEN -->', tijden)
    faq = [f for f in data.get('_faq', []) if data.get('ZV_TOON') or not f.get('zondag')]
    html = html.replace('<!-- ARR_FAQ -->', '\n'.join(
        f'          <details class="as-accordeon__item"{" open" if i == 0 else ""}><summary class="as-accordeon__kop">{f["q"]}</summary>'
        f'<div class="as-accordeon__paneel"><p>{f["a"]}</p></div></details>'
        for i, f in enumerate(faq)))
    pijl = '<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    html = html.replace('<!-- ARR_ANDERE -->', '\n'.join(
        f'        <a class="ar-ander" href="{escape(a["url"])}">'
        f'<span class="ar-ander-foto"><img src="{escape(a["img"])}" alt="{escape(a.get("alt", ""))}" loading="lazy"></span>'
        f'<span class="ar-ander-tekst"><b class="ar-ander-naam">{a["naam"]}</b>'
        + (f'<span class="ar-ander-prijs">{re.sub(r"(€\s?[0-9.,]+)", r"<b>\1</b>", a["prijs"])}</span>' if a.get('prijs') else '')
        + f'<span class="ar-ander-rond">{pijl}</span></span></a>'
        for a in data.get('_andere', [])))

    banen = data.get('_banen')
    if banen:
        if not 1 <= len(banen) <= 4:
            sys.exit(f'_banen: 1 tot 4 banen nodig, niet {len(banen)}')
        pin = ('<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0'
               'c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>')
        kaarten = []
        for b in banen:
            for veld in ('naam', 'plaats', 'tekst', 'rijtijd', 'url', 'foto', 'alt'):
                if not b.get(veld):
                    sys.exit(f'_banen: veld {veld!r} ontbreekt bij {b.get("naam", "?")!r}')
            if not os.path.exists(os.path.join(base, b['foto'])):
                sys.exit(f'_banen: {b["foto"]} bestaat niet')
            kaarten.append(
                f'        <article class="ar-baan">'
                f'<div class="ar-baan-foto"><img src="{escape(b["foto"])}" alt="{escape(b["alt"])}"'
                + (f' style="object-position:{escape(b["pos"])}"' if b.get('pos') else '')
                + ' loading="lazy"></div>'
                f'<div class="ar-baan-inhoud"><h3>{b["naam"]}</h3>'
                f'<p class="ar-baan-plek">{pin}<span>{b["plaats"]} · {b["rijtijd"]}</span></p>'
                f'<p class="ar-baan-tekst">{b["tekst"]}</p>'
                f'<a class="ar-inb-link ar-baan-link" href="{escape(b["url"])}" target="_blank" rel="noopener">'
                f'{b.get("link", "Naar de website")}{pijl}</a></div></article>')
        html = html.replace('<!-- ARR_BANEN -->', '\n'.join(kaarten))

    nachten = data.get('ARR_NACHTEN', 1)
    if not isinstance(nachten, int) or nachten < 1:
        sys.exit(f'ARR_NACHTEN moet een heel getal van 1 of meer zijn, niet {nachten!r}')
    if nachten > 1:
        html = html.replace(' data-boekbalk ', f' data-boekbalk data-nachten="{nachten}" ')
    if data.get('ARR_KALENDER') is False:
        # Prijskalender en live vanaf-prijs uit (bijv. code nog niet actief in Mews): dialoog, css en js eruit; de
        # boekknoppen gaan dan rechtstreeks via de Mews-flow van lander-w1.js, de prijs blijft vaste tekst uit de JSON.
        html = re.sub(r'\n  <!-- ══ PRIJSKALENDER.*?</dialog>', '', html, count=1, flags=re.S)
        html = html.replace('<link rel="stylesheet" href="arrangement-kalender.css">', '')
        html = html.replace('<script src="arrangement-kalender.js" defer></script>', '')
        html = html.replace('<script src="arr-vanaf.js" defer></script>', '')
    elif '{{KAL_KOP}}' in html:
        html = apply_kalender(html, data, kamers, nachten)
        if data.get('ARR_VANAF_LIVE') is False:
            # alleen de live vanaf-prijs uit (bijv. de komende 56 dagen zijn duurder dan de vanaf-prijs van het
            # arrangement, Winter: december EUR 309 tegen januari EUR 269): prijzen blijven vaste tekst uit de JSON
            html = html.replace('<script src="arr-vanaf.js" defer></script>', '')
        else:
            html = markeer_vanaf(html, data['VOUCHER'])

    wolk = data.get('_fotowolk')
    if wolk:
        s = html.index('<section class="sec b7a"')
        e = html.index('<div class="b7a-inhoud">', s)
        vast = [m for m in re.finditer(r'<img class="b7a-foto[^"]*" data-h="[^"]+" src="[^"]+" alt="" loading="lazy">', html[s:e])]
        if len(wolk) != len(vast):
            sys.exit(f'_fotowolk: precies {len(vast)} foto\'s nodig, niet {len(wolk)}')
        stuk = html[s:e]
        for m, f in reversed(list(zip(vast, wolk))):
            f = {'img': f} if isinstance(f, str) else f
            if not os.path.exists(os.path.join(base, f['img'])):
                sys.exit(f'_fotowolk: {f["img"]} bestaat niet')
            tag = re.sub(r'src="[^"]+"', lambda _: f'src="{escape(f["img"])}"', m.group(0), count=1)
            if f.get('pos'):
                tag = tag[:-1] + f' style="object-position:{escape(f["pos"])}">'
            stuk = stuk[:m.start()] + tag + stuk[m.end():]
        html = html[:s] + stuk + html[e:]
    return html


WEEKDAGEN = ['zondag', 'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag']
KALENDER_JSON = os.path.join(base, 'content', 'arr-kalender.json')


def markeer_vanaf(html, code):
    """Live vanaf-prijs (arr-vanaf.js + /api/arr-vanaf, alleen blok 'arrangement'): zet data-arr-vanaf="<CODE>" om het
    bedrag in de hero-pil, de zijkaart/telefoonkaart, de inbegrepen-regel en de onderbalk; de vaste prijs uit de JSON
    blijft de server-side terugval. De Ook-interessant-kaarten krijgen de code van hun eigen arrangement (slug uit
    content/arr-kalender.json; /najaarsarrangement = NAJAAR2D). Zondagblok en kamerprijzen blijven vast."""
    bedrag = r'€\s?[0-9.]+(?:,[0-9]{2})?'
    attr = f' data-arr-vanaf="{code}"'
    # pil is inline-flex: de hele tekst in één span, anders worden 'vanaf', bedrag en eenheid losse flex-items
    html = re.sub(r'<span class="b1a-prijspil">([^<]*?)(' + bedrag + r')([^<]*)</span>',
                  lambda m: f'<span class="b1a-prijspil"><span>{m.group(1)}<span{attr}>{m.group(2)}</span>{m.group(3)}</span></span>', html)
    html = html.replace('<b class="b1k-prijs-bedrag">', f'<b class="b1k-prijs-bedrag"{attr}>')
    html = html.replace('<p class="ar-inb-prijs">vanaf <b>', f'<p class="ar-inb-prijs">vanaf <b{attr}>')
    html = re.sub(r'(<div class="mob-cta"[\s\S]*?<span class="om">[^<]*?)(' + bedrag + ')', lambda m: f'{m.group(1)}<span{attr}>{m.group(2)}</span>', html, count=1)
    # vaste en live bedrag allebei met een harde spatie: '€' en het getal breken nooit over twee regels
    html = re.sub(r'(<(?:span|b)[^>]*data-arr-vanaf="[A-Z0-9]+"[^>]*>)€ ', r'\1€&nbsp;', html)
    with open(os.path.join(base, 'content/arr-kalender.json'), encoding='utf-8') as f:
        per_slug = {v['slug']: k for k, v in json.load(f).items()}
    def ander(m):
        c = per_slug.get(m.group(2).rstrip('/').rsplit('/', 1)[-1])
        return m.group(0).replace('<span class="ar-ander-prijs">vanaf <b>', f'<span class="ar-ander-prijs">vanaf <b data-arr-vanaf="{c}">') if c else m.group(0)
    html = re.sub(r'(<a class="ar-ander" href="([^"]+)">[\s\S]*?</a>)', ander, html)
    html = re.sub(r'(<b data-arr-vanaf="[A-Z0-9]+">)€ ', r'\1€&nbsp;', html)
    return html


def apply_kalender(html, data, kamers, nachten):
    """Prijskalender 'Kies je nachten' (dialog #ar-kal, arrangement-kalender.js, /api/arr-kalender):
    - data-attributen en teksten van de dialoog uit de JSON: VOUCHER, ARR_NACHTEN, ARR_AANKOMSTDAGEN (optioneel,
      lijst van weekdagnummers 0 = zondag ... 6 = zaterdag; Weekend [5, 6]), ZV_TOON (zondag goud + berekende korting),
      standaardkamer = de eerste kamer met soort 'inbegrepen' uit '_kamers' (anders de eerste), kamernamen uit de kaarten;
    - schrijft de instellingen van deze code in content/arr-kalender.json (whitelist van de Pages Function). Eén bron:
      de arrangement-JSON. Een andere code onder dezelfde slug vervalt."""
    from html import escape
    code = data['VOUCHER']
    dagen = data.get('ARR_AANKOMSTDAGEN')
    if dagen is not None and (not isinstance(dagen, list) or not dagen or any(not isinstance(d, int) or not 0 <= d <= 6 for d in dagen)):
        sys.exit(f'ARR_AANKOMSTDAGEN moet een lijst weekdagnummers 0-6 zijn (0 = zondag), niet {dagen!r}')
    zondag = bool(data.get('ZV_TOON'))
    # kamernamen en Mews-id's uit de kaarten die op de pagina staan
    namen = {}
    for m in re.finditer(r'<article class="b4b-kaart[^"]*">.*?</article>', html, re.S):
        k = m.group(0)
        if 'data-kloon' in k:
            continue
        rid = re.search(r'data-room="([^"]+)"', k)
        naam = re.search(r'<h3>([^<]+)</h3>', k)
        if rid and naam:
            namen[rid.group(1).lower()] = naam.group(1).strip()
    sleutels = list((kamers or {}).keys())
    std_sleutel = next((k for k in sleutels if (kamers[k].get('soort', 'inbegrepen') == 'inbegrepen')), sleutels[0] if sleutels else None)
    std = ''
    if std_sleutel:
        m = re.search(r'data-room="([^"]+)"[^>]*>Boek nu</a><button type="button" class="btn btn-secondary btn--klein" data-kamer="'
                      + re.escape(std_sleutel) + '"', html)
        std = m.group(1).lower() if m else ''
    if not std:
        sys.exit(f'apply_kalender: geen standaardkamer gevonden voor {code}')
    if nachten > 1:
        kop = 'Kies je aankomstdag'
        if dagen:
            lijst = [WEEKDAGEN[d] for d in sorted(dagen, key=lambda d: (d + 6) % 7)]
            wanneer = lijst[0] if len(lijst) == 1 else ', '.join(lijst[:-1]) + ' of ' + lijst[-1]
            sub = f'Aankomst kan op {wanneer}. Je vertrek na {nachten} nachten komt er vanzelf bij.'
        else:
            sub = f'Klik op je aankomstdag. Je vertrek na {nachten} nachten komt er vanzelf bij.'
        noot = f'Prijs per persoon voor {nachten} nachten bij aankomst op die dag,'
        dicht = 'Grijs: geen aankomst mogelijk'
    else:
        kop = 'Kies je nachten'
        sub = 'Klik op je aankomstdag en daarna op je vertrekdag. Vertrekken kan ook op een grijze dag.'
        noot = 'Prijs per persoon per nacht bij aankomst op die dag,'
        dicht = 'Grijs: niet beschikbaar, vertrekken kan wel'
    leg_zondag = '<span><i class="o"></i>Goud: aankomst op zondag, € 20 per kamer voordeliger</span>' if zondag else ''
    vervang = {
        '{{KAL_NACHTEN}}': str(nachten),
        '{{KAL_AANKOMSTDAGEN}}': ','.join(str(d) for d in dagen) if dagen else '',
        '{{KAL_ZONDAG}}': 'ja' if zondag else 'nee',
        '{{KAL_KAMER_STANDAARD}}': std,
        '{{KAL_KAMERS}}': escape(json.dumps(namen, ensure_ascii=False, separators=(',', ':'))),
        '{{KAL_KOP}}': kop, '{{KAL_SUB}}': sub, '{{KAL_NOOT_VOOR}}': noot,
        '{{KAL_LEG_ZONDAG}}': leg_zondag, '{{KAL_LEG_DICHT}}': dicht,
    }
    for k, v in vervang.items():
        html = html.replace(k, v)

    slug = re.search(r'<link rel="canonical" href="https://visit\.asteria\.nl/([^"]+)"', html)
    slug = slug.group(1) if slug else ''
    try:
        with open(KALENDER_JSON, encoding='utf-8') as f:
            alle = json.load(f)
    except (OSError, ValueError):
        alle = {}
    alle = {c: v for c, v in alle.items() if c == code or v.get('slug') != slug}
    alle[code] = {'slug': slug, 'nachten': nachten, 'aankomstdagen': sorted(dagen) if dagen else None,
                  'zondag': zondag, 'standaardkamer': std}
    if data.get('ZV_BEREKENEN') is False:
        # zondagkorting staat in Mews (geen berekende EUR 20) en een zondag zonder lagere prijs krijgt geen goud
        alle[code]['zondag_berekenen'] = False
    if data.get('MEWS_CONFIG'):
        # eigen Mews-boekingsmodule voor deze pagina (bijv. Winter-actie 95c70e27): de API bevraagt die config
        alle[code]['config'] = data['MEWS_CONFIG']
    nieuw = json.dumps(dict(sorted(alle.items())), ensure_ascii=False, indent=2) + '\n'
    try:
        with open(KALENDER_JSON, encoding='utf-8') as f:
            oud = f.read()
    except OSError:
        oud = None
    if nieuw != oud:
        with open(KALENDER_JSON, 'w', encoding='utf-8') as f:
            f.write(nieuw)
    return html


MEWS_BASIS = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
# lander-w1-iconen (klasse as-icoon: stroke currentColor, breedte 2); vinkje = VINK_SVG zoals in de zijkaart
AO_PIJL = icoon('<path d="M5 12h14M13 6l6 6-6 6"/>')
AO_POTLOOD = icoon('<path d="M17 3l4 4L8 20H4v-4z"/>', 'as-icoon ao-kh__potlood')


def ao_vak(paden):
    """Icoon in een zandvakje, zoals .ar-vak in 'Dit is inbegrepen' van de arrangementen."""
    return f'<span class="ao-vak">{icoon(paden)}</span>'


def w1_blokken(spiegel=False):
    """Kop, kamers (4b), reviews (5a), kamer-pop-up en voet letterlijk uit lander-w1.template.html, zodat het overzicht
    met de flow-landers en arrangementen meeloopt. Zonder vouchercode: '?mewsVoucherCode={{VOUCHER}}' en
    data-voucher="{{VOUCHER}}" vallen weg (kamerknoppen openen de widget met data-room); de pil op de kamerfoto ook.
    spiegel=True: kop en voet in de spiegelstand van hotel-venray-v2 (blokken gesloten + spiegel, links uit
    translations/spiegel-links.json, geen asteria.nl behalve privacy/voorwaarden); kamers, reviews en pop-up ongewijzigd."""
    with open(os.path.join(base, 'lander-w1.template.html'), encoding='utf-8') as f:
        w1 = f.read()

    def stuk(begin, eind):
        i = w1.find(begin)
        if i < 0:
            sys.exit(f'apply_overzicht: {begin!r} niet gevonden in lander-w1.template.html')
        j = w1.find(eind, i)
        if j < 0:
            sys.exit(f'apply_overzicht: {eind!r} na {begin!r} niet gevonden in lander-w1.template.html')
        return w1[i:j + len(eind)]

    i, j = w1.find('<header class="top-stack'), w1.find('<main class="lp">')
    if i < 0 or j < i:
        sys.exit('apply_overzicht: kop van lander-w1 niet gevonden')
    delen = {
        'W1_KOP': w1[i:j],   # rstrip na de blokkenpass (de slotmarker van de drawer staat op een eigen regel)
        'W1_KAMERS': '  ' + stuk('<section class="sec b4b"', '</section>'),
        'W1_REVIEWS': '  ' + stuk('<section class="sec b5a"', '</section>'),
        'W1_POP': '  ' + '\n  '.join([stuk('<dialog class="lp-pop lp-pop--kamer"', '</dialog>'),
                                      '<div class="lp-pop-overlay" hidden></div>',
                                      stuk('<template id="lp-pop-vink">', '</template>'),
                                      stuk('<script type="application/json" id="lp-kamerdata">', '</script>')]),
        'W1_VOET': stuk('<footer class="footer', '</footer>') + '\n\n' + stuk('<div class="cookie-banner"', '</div>'),
    }
    for k, s in delen.items():
        s = s.replace(f'data-basis="{MEWS_BASIS}?mewsVoucherCode={{{{VOUCHER}}}}"', f'data-basis="{MEWS_BASIS}?"')
        s = s.replace('?mewsVoucherCode={{VOUCHER}}&amp;', '?').replace('?mewsVoucherCode={{VOUCHER}}', '')
        s = s.replace(' data-voucher="{{VOUCHER}}"', '')
        s = re.sub(r'<span class="b4b-pil">.*?</span>', '', s, flags=re.S)
        if '{{VOUCHER}}' in s:
            sys.exit(f'apply_overzicht: {{{{VOUCHER}}}} blijft over in {k}')
        # reviewsticker: de arrangementvariant (met het aantal reviews)
        if spiegel and k in ('W1_KOP', 'W1_VOET'):
            delen[k] = vul_spiegel_links(apply_blokken(s, {'arrangement', 'gesloten', 'spiegel'}))
        else:
            delen[k] = apply_blokken(s, {'arrangement'})
    delen['W1_KOP'] = delen['W1_KOP'].rstrip()
    return delen


def apply_overzicht(html, data):
    """Arrangementenoverzicht (arrangementen.template.html, prefix ao-):
    - lander-w1-blokken op <!-- W1_KOP/KAMERS/REVIEWS/POP/VOET --> (w1_blokken);
    - kaarten (meest geboekt, alle, keuzehulp) uit '_arrangementen' ({slug, url, cat, volgorde, scores, redenen}); per
      slug leest de build translations/<slug>-nl.json: KAART_KOP (titel), eerste zin van SUB (korte omschrijving),
      ARR_PRIJS + ARR_PRIJS_KAART_EENHEID (vanaf-prijs), ARR_NACHTEN, HERO_IMG/HERO_ALT/HERO_ATTR (foto), KAART_VINK_A..C,
      ZV_TOON + ZV_ZONDAG_PRIJS (zondagregel; die kaarten krijgen categorie 'zondag'). Zo lopen prijzen niet uit de pas met de arrangementpagina's.
    - '_meest_geboekt' (3 slugs), '_categorieen' (chips), '_kh_vragen' (4 vragen), '_intro_tegels' (4), '_praktisch' (6), '_faq'."""
    from html import escape
    spiegel = bool(data.get('_kop_spiegel'))
    for k, s in w1_blokken(spiegel).items():
        html = html.replace(f'<!-- {k} -->', s, 1)

    cats = data['_categorieen']
    arrs = []
    for a in data['_arrangementen']:
        with open(os.path.join(base, 'translations', f'{a["slug"]}-nl.json'), encoding='utf-8') as f:
            j = json.load(f)
        if not os.path.exists(os.path.join(base, j['HERO_IMG'])):
            sys.exit(f'apply_overzicht: {j["HERO_IMG"]} bestaat niet')
        nachten = j.get('ARR_NACHTEN', 1)
        x = re.search(r'--hero-x:\s*([0-9.]+%)', j.get('HERO_ATTR', ''))
        zin = re.match(r'.+?[.!?](?=\s|$)', j['SUB'].strip())
        arrs.append(dict(a, naam=j['KAART_KOP'], oms=a.get('oms') or (zin.group(0) if zin else j['SUB']), prijs=j['ARR_PRIJS'],
                         eenheid=j['ARR_PRIJS_KAART_EENHEID'], nachten=nachten, foto=j['HERO_IMG'], alt=j.get('HERO_ALT', ''),
                         pos=f'{x.group(1)} 50%' if x else '50% 50%',
                         vinken=[j[f'KAART_VINK_{l}'] for l in 'ABC' if j.get(f'KAART_VINK_{l}')],
                         # zondagregel zoals Parkhotel (Op zondag vanaf <b>prijs</b> p.p.), bedrag = ZV_ZONDAG_PRIJS van het zondagblok (a9)
                         zondag=(f'Op zondag vanaf <b>{j["ZV_ZONDAG_PRIJS"]}</b> {j["ARR_PRIJS_KAART_EENHEID"]}'
                                 if j.get('ZV_TOON') and j.get('ZV_ZONDAG_PRIJS') else ''),
                         tag=a.get('tag') or ' · '.join([cats[a['cat'][0]], '1 nacht' if nachten == 1 else f'{nachten} nachten'])))
    # '_extra': statische kaarten zonder eigen arrangement-JSON (feestdagen op asteria.nl); alle data staat in de lijst zelf.
    # Velden: slug, url, naam, oms, prijs? (alleen als de bronpagina hem noemt), eenheid?, tag, foto, alt, pos?, vinken, cat, volgorde, scores, redenen.
    for e in data.get('_extra', []):
        for veld in ('slug', 'url', 'naam', 'oms', 'tag', 'foto', 'alt', 'vinken', 'cat', 'volgorde', 'scores', 'redenen'):
            if veld not in e:
                sys.exit(f'_extra: veld {veld!r} ontbreekt bij {e.get("slug", "?")!r}')
        if not os.path.exists(os.path.join(base, e['foto'])):
            sys.exit(f'_extra: {e["foto"]} bestaat niet')
        arrs.append(dict(e, prijs=e.get('prijs', ''), eenheid=e.get('eenheid', ''), pos=e.get('pos', '50% 50%'), zondag=''))
    for a in arrs:
        for c in a['cat']:
            if c not in cats:
                sys.exit(f'apply_overzicht: onbekende categorie {c!r} bij {a["slug"]}')
    volgorde = data.get('_volgorde')
    if volgorde:
        per = {a['slug']: a for a in arrs}
        if sorted(volgorde) != sorted(per):
            sys.exit(f'_volgorde moet precies de slugs van _arrangementen + _extra bevatten')
        arrs = [per[s] for s in volgorde]
    # zoals Parkhotel: elke kaart met een zondagregel hoort ook bij de chip Zondagvoordeel (categorie 'zondag')
    if 'zondag' in cats:
        for a in arrs:
            if a['zondag'] and 'zondag' not in a['cat']:
                a['cat'] = a['cat'] + ['zondag']
    per_slug = {a['slug']: a for a in arrs}
    top = data['_meest_geboekt']
    if len(top) != 3 or any(s not in per_slug for s in top):
        sys.exit(f'_meest_geboekt: drie slugs uit _arrangementen nodig, niet {top!r}')

    vanaf, knop = data['VANAF'], data['KNOP_ARR']

    def foto(a, cls, w=800, h=534):
        return (f'<img class="{cls}" src="{escape(a["foto"])}" alt="{escape(a["alt"])}" width="{w}" height="{h}" loading="lazy" '
                f'decoding="async" style="object-position:{a["pos"]}">')

    def prijs(a, cls='ao-prijs'):
        if not a['prijs']:
            return ''
        return f'<p class="{cls}"><span class="ao-vf">{vanaf}</span> <b>{a["prijs"]}</b> <span>{a["eenheid"]}</span></p>'

    def zondag(a):
        return f'<p class="ao-zondagregel">{a["zondag"]}</p>' if a['zondag'] else ''

    def vinken(a, cls='vinkjes ao-incl'):
        return f'<ul class="{cls}">' + ''.join(f'<li>{VINK_SVG}<span>{v}</span></li>' for v in a['vinken']) + '</ul>'

    def acties(a, cls='ao-acties'):
        return f'<div class="{cls}"><a class="btn btn-primary" href="{escape(a["url"])}">{knop}</a></div>'

    html = html.replace('<!-- AO_INTRO -->', '\n'.join(
        f'          <li class="ao-icotegel">{ao_vak(t["icoon"])}<span><b>{t["titel"]}</b>{t["tekst"]}</span></li>'
        for t in data['_intro_tegels']))
    html = html.replace('<!-- AO_TOP -->', '\n'.join(
        f'          <article class="ao-tk">{foto(a, "ao-tk__foto")}<div class="ao-tk__body">'
        f'<p class="ao-tag">{a["tag"]}</p><h3 class="ao-naam">{a["naam"]}</h3>'
        f'<div class="ao-prijsblok">{prijs(a)}{zondag(a)}</div><p class="ao-oms">{a["oms"]}</p>{vinken(a)}{acties(a)}</div></article>'
        for a in (per_slug[s] for s in top)))
    html = html.replace('<!-- AO_CHIPS -->', '\n'.join(
        ['            <label class="ao-chip ao-is-aan"><input class="ao-chip__vak" type="checkbox" data-ao-reset checked><span>'
         f'{data["FILTER_ALLES"]}</span></label>']
        + [f'            <label class="ao-chip"><input class="ao-chip__vak" type="checkbox" value="{k}"><span>{escape(v, quote=False)}</span></label>'
           for k, v in cats.items()]))
    html = html.replace('<!-- AO_ALLE -->', '\n'.join(
        f'        <article class="kaart ao-kaart" data-ao-cat="{" ".join(a["cat"])}">'
        f'<div class="ao-kaart__foto">{foto(a, "ao-kaart__img")}'
        + (f'<span class="ao-past">{data["LABEL_MEEST"]}</span>' if a['slug'] in top else '')
        + f'</div><div class="ao-kaart__kop"><p class="ao-kaart__tag">{a["tag"]}</p><h3 class="ao-naam">{a["naam"]}</h3></div>'
        f'<div class="ao-prijsblok ao-kaart__prijs">{prijs(a)}{zondag(a)}</div><p class="ao-oms ao-kaart__oms">{a["oms"]}</p>'
        f'{vinken(a, "vinkjes ao-incl ao-kaart__incl")}'
        f'{acties(a, "ao-acties ao-kaart__acties")}</article>'
        for a in arrs))

    # keuzehulp
    vragen = data['_kh_vragen']
    if len(vragen) != 4:
        sys.exit('_kh_vragen: precies 4 vragen nodig')
    html = html.replace('<!-- AO_KH_ANTW -->', '\n'.join(
        f'          <button type="button" class="ao-kh__antw" data-ao-edit="{v["key"]}" aria-expanded="false"><span class="ao-kh__vh">'
        f'{data["KH_WIJZIG"]}: {v["vraag"]} </span><span data-ao-edit-text></span>{AO_POTLOOD}</button>' for v in vragen))
    blokken = []
    for i, v in enumerate(vragen):
        if i == 2:
            blokken.append('            <div class="ao-kh__lijn" aria-hidden="true"></div>')
        chips = ''.join(f'<button type="button" class="ao-chip" data-ao-v="{o["v"]}" aria-pressed="false">{o["label"]}</button>'
                        for o in v['opties'])
        blokken.append(
            f'            <fieldset class="ao-kh__vraag{" ao-kh__vraag--onder" if i % 2 else ""}" data-ao-q="{v["key"]}">'
            f'<legend class="ao-kh__vraagkop"><span class="ao-kh__nr" aria-hidden="true">{i + 1}</span><span>{v["vraag"]}</span></legend>'
            f'<div class="ao-kh__chips">{chips}</div></fieldset>')
    html = html.replace('<!-- AO_KH_VRAGEN -->', '\n'.join(blokken))
    waarden = [o['v'] for v in vragen for o in v['opties']]
    res, alts = [], []
    for a in arrs:
        for w in list(a['scores']) + [r for r in a['redenen'] if r != 'default']:
            if w not in waarden:
                sys.exit(f'apply_overzicht: onbekend antwoord {w!r} bij {a["slug"]}')
        redenen = ''.join(f'<li data-ao-reason="{w}" hidden>{t}</li>' for w, t in a['redenen'].items())
        score = escape(json.dumps(a['scores'], separators=(',', ':')))
        res.append(
            f'            <article class="ao-res" data-ao-res="{a["slug"]}" data-ao-order="{a["volgorde"]}" data-ao-score="{score}" hidden>'
            f'{foto(a, "ao-res__foto")}<div class="ao-res__body"><p class="ao-kh__resultaatkop">{data["KH_AANBEVELING"]}</p>'
            f'<p class="ao-tag">{a["tag"]}</p><h3 class="ao-naam">{a["naam"]}</h3>{prijs(a, "ao-prijs ao-res__prijs")}{zondag(a)}'
            f'<div class="ao-res__waarom"><p class="ao-res__waaromkop">{data["KH_WAAROM"]}</p><ul class="ao-res__redenen">{redenen}</ul></div>'
            f'{acties(a, "ao-acties ao-res__acties")}</div></article>')
        alts.append(
            f'              <a class="ao-alt" data-ao-alt="{a["slug"]}" href="{escape(a["url"])}" hidden>'
            f'<img src="{escape(a["foto"])}" alt="" width="800" height="534" loading="lazy" decoding="async" style="object-position:{a["pos"]}">'
            f'<span class="ao-alt__tekst"><span class="ao-alt__naam">{a["naam"]}</span>'
            + (f'<span class="ao-alt__prijs"><span class="ao-vf">{vanaf}</span> {a["prijs"]} {a["eenheid"]}</span>' if a['prijs'] else '')
            + '</span>'
            f'<span class="ao-alt__bekijk">{data["KH_BEKIJK"]}{AO_PIJL}</span></a>')
    html = html.replace('<!-- AO_KH_RES -->', '\n'.join(res)).replace('<!-- AO_KH_ALTS -->', '\n'.join(alts))

    html = html.replace('<!-- AO_PRAKTISCH -->', '\n'.join(
        f'        <li class="ao-ptegel">{ao_vak(t["icoon"])}<h3>{t["titel"]}</h3><p>{t["tekst"]}</p></li>' for t in data['_praktisch']))
    html = html.replace('<!-- AO_FAQ -->', '\n'.join(
        f'          <details class="as-accordeon__item"{" open" if i == 0 else ""}><summary class="as-accordeon__kop">{f["q"]}</summary>'
        f'<div class="as-accordeon__paneel"><p>{f["a"]}</p></div></details>' for i, f in enumerate(data['_faq'])))
    if spiegel:   # links in de inhoud naar kamers/wellness/restaurant/omgeving/contact/... -> spiegeladressen
        html = spiegel_inhoud(html)
    if '<!-- AO_' in html or '<!-- W1_' in html:
        sys.exit('apply_overzicht: niet alle plekken zijn gevuld: ' + ', '.join(re.findall(r'<!-- ((?:AO|W1)_[A-Z_]+) -->', html)))
    return html


# ── Kamerdetailpagina's (kamer-w1, nov 2026) ─────────────────────────────────────────────────────────────
# Kamers in de volgorde van 'Andere kamers bij Asteria': (slug, sleutel, spiegelsleutel). slug = translations/kamer-<slug>-v2-nl.json,
# sleutel = /api/kamer-vanaf (live vanaf-prijs, data-kamer-vanaf), spiegelsleutel = adres uit translations/spiegel-links.json
# (Comfort en Deluxe = Effecty-spiegelpagina's, de rest = de kamer-w1-pagina's hieronder). Junior Suite niet (besluit Stijn:
# niet in het aanbod op /kamers); translations/kamer-junior-suite-v2-nl.json blijft ongebruikt staan.
KAMER_VOLGORDE = [('comfort-kamer', 'comfort', 'kamer-comfort'), ('comfort-kamer-3-personen', 'comfort-3', 'kamer-comfort-3'),
                  ('mindervalide-kamer', 'mindervalide', 'kamer-mindervalide'), ('royale-kamer', 'royale', 'kamer-royale'),
                  ('deluxe-kamer', 'deluxe', 'kamer-deluxe'), ('suite', 'suite', 'kamer-suite'),
                  ('bruidssuite', 'bruidssuite', 'kamer-bruidssuite')]
# Kamers met een eigen kamer-w1-pagina (build-entry kamers/<slug> -> kamers/<slug>.html); Comfort/Deluxe zijn spiegelpagina's.
KAMER_PAGINAS = ['royale-kamer', 'suite', 'bruidssuite', 'comfort-kamer-3-personen', 'mindervalide-kamer']
MEWS_KAMER_URL = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsRoom={id}&amp;mewsRoute=rooms'

# Lijniconen (24x24, stroke) voor spec-tegels, faciliteiten en 'Goed om te weten'; sleutel = 'icoon' in de JSON.
KAMER_ICOON = {
    'm2': '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
    'bed': '<path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8M2 16h20M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/>',
    'personen': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    'douche': '<path d="M4 4l2.5 2.5M6.5 6.5a5 5 0 0 1 7 0l-7 7a5 5 0 0 1 0-7zM14 11v.01M17 14v.01M14 17v.01M20 17v.01M17 20v.01M11 14v.01"/>',
    'bad': '<path d="M3 12h18v3a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5zM6 12V5a2 2 0 0 1 3.5-1.3M7 20l-1 2M17 20l1 2"/>',
    'zit': '<path d="M5 11V8a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v3M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM6 19v2M18 19v2"/>',
    'sauna': '<path d="M14 14.8V4a2 2 0 0 0-4 0v10.8a4 4 0 1 0 4 0z"/>',
    'rolstoel': '<circle cx="11" cy="4" r="2"/><path d="M11 7v6h6l2 6M11 10h5M8 10.5a6 6 0 1 0 8 7.5"/>',
    'bedbank': '<path d="M4 10V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3M2 12a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2zM4 17v2M20 17v2"/>',
    'airco': '<path d="M3 5h18v7H3zM6 9h12M7 16c0 1.5-1 2-1 3M12 16v3M17 16c0 1.5 1 2 1 3"/>',
    'koffie': '<path d="M17 8h1a4 4 0 1 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4zM6 2v2M10 2v2M14 2v2"/>',
    'tv': '<rect x="2" y="5" width="20" height="13" rx="2"/><path d="M8 21h8M12 18v3"/>',
    'fohn': '<path d="M14 4a5 5 0 1 0 0 10h6V4zM14 14l-2 7h-3l1-7M9 9h.01"/>',
    'wifi': '<path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/>',
    'fitness': '<path d="M6.5 6.5v11M17.5 6.5v11M3 9.5v5M21 9.5v5M6.5 12h11"/>',
    'koelkast': '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 10h14M9 6v1M9 14v2"/>',
    'badjas': '<path d="M8 3l4 4 4-4 4 3-2 5v10H6V11L4 6zM12 7v14M9 14h6"/>',
    'inchecken': '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
    'uitchecken': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    'ontbijt': '<path d="M3 11h18M5 11a7 7 0 0 0 14 0M12 3v3M8 5l1 2M16 5l-1 2M3 21h18"/>',
    'parkeren': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>',
    'vink': '<path d="M20 6L9 17l-5-5"/>',
    'raster': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
}


def kamer_icoon(sleutel, cls='as-icoon'):
    if sleutel not in KAMER_ICOON:
        sys.exit(f'render_kamer: onbekend icoon {sleutel!r} (kies uit {", ".join(KAMER_ICOON)})')
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{KAMER_ICOON[sleutel]}</svg>'


def lw1_delen():
    """Kop (header + mobiel menu) en voet (footer, onderbalk, cookiemelding) uit lander-w1.template.html, met de
    blokmarkers erin (gesloten/!gesloten worden daarna door apply_blokken afgehandeld). Zo blijft lander-w1 de enige bron."""
    with open(os.path.join(base, 'lander-w1.template.html'), encoding='utf-8') as f:
        lw = f.read()
    kop = lw[lw.index('<header class="top-stack'):lw.index('<main class="lp">')].rstrip() + '\n'
    voet = lw[lw.index('<footer class="footer'):lw.index('</body>')].rstrip() + '\n'
    return kop, voet


def kamer_absoluut(html):
    """Kamerpagina's staan onder /kamers/: relatieve src/href/poster (fotos/..., videos/..., lander-w1.css) en de
    lightbox-items in #km-media worden absoluut, zodat ze niet naar /kamers/fotos/... wijzen."""
    html = re.sub(r'\b(src|href|poster)="(?!/|[a-z][a-z0-9+.-]*:|#)([^"]+)"', r'\1="/\2"', html)
    return re.sub(r'("(?:src|poster)": ")(?!/|https?:)', r'\1/', html)


def render_kamer(html, data):
    """Kamerdetailpagina (kamer-w1.template.html) uit translations/kamer-<slug>-v2-nl.json. Vult de lijstblokken in:
      _fotos         lijst {img, alt, pos?} (1 tot 8): mozaiek (groot, breed, klein + tegel 'Bekijk alle foto's (n)') en lightbox;
      _video         {src, poster} of null: eerste item in de lightbox (geen herovideo);
      _vinkjes       3 korte regels in de boekkaart;  _specs  5 tegels {icoon, tekst};  _faciliteiten  {icoon, tekst};
      _weten         {icoon, titel, tekst} (Goed om te weten);  _faq  {q, a} (4);  _verder  {titel, regel, url, img, alt} (4);
      ALLES_FOTO     index in _fotos van de grote foto bij 'Wat er in de kamer staat'.
    'Andere kamers' leest de JSON's van de andere kamers (KAMER_VOLGORDE): KAMER_NAAM, KAART_REGEL, KAART_CHIP, KAMER_ROOM,
    _fotos[0]; link via spiegel:<sleutel> (Comfort/Deluxe = spiegelpagina, de rest /kamers/<slug>), geen Junior Suite.
    Prijzen (boekkaart, andere kamers, onderbalk) = live vanaf-prijs: data-kamer-vanaf="<sleutel>" + data-kamer-vanaf-bedrag,
    gevuld door kamer-w1.js uit /api/kamer-vanaf; geen vaste bedragen uit de JSON.
    Reviews: content/reviews-google-asteria.json (reviews met 'kamer' eerst)."""
    from html import escape
    e = lambda s: escape(s or '', quote=False)
    a = lambda s: escape(s or '')
    kop, voet = lw1_delen()
    html = html.replace('<!-- LW1_KOP -->', kop).replace('<!-- LW1_VOET -->', voet)

    eigen = data['CANONICAL_URL'].rstrip('/').rsplit('/', 1)[-1]
    sleutels = {slug: sl for slug, sl, _ in KAMER_VOLGORDE}
    if eigen not in sleutels:
        sys.exit(f'render_kamer: {eigen!r} staat niet in KAMER_VOLGORDE')
    sleutel = sleutels[eigen]
    if KAMER_MEWS.get(sleutel) != data['KAMER_ROOM']:
        sys.exit(f'render_kamer: KAMER_ROOM van {eigen} hoort bij een andere kamer dan {sleutel}')
    html = html.replace('{{KM_SLEUTEL}}', sleutel)
    # onderbalk: 'Vanaf € X per nacht' live (verborgen tot gevuld)
    data['STICKY_SUB'] = (f'<span data-kamer-vanaf="{sleutel}">{e(data["PRIJS_VANAF"])} <span data-kamer-vanaf-bedrag>€ …</span> '
                          f'{e(data.get("STICKY_PER", "per nacht"))}</span>')

    # onderbalk: Boek-knop opent Mews met deze kamer voorgeselecteerd
    rid = data['KAMER_ROOM']
    html = html.replace('<a class="btn btn-primary mews-open" data-voucher="{{VOUCHER}}" href="https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsVoucherCode={{VOUCHER}}" tabindex="-1">{{STICKY_KNOP}}</a>',
                        f'<a class="btn btn-primary mews-open" data-room="{rid}" href="{MEWS_KAMER_URL.format(id=rid)}" tabindex="-1">{{{{STICKY_KNOP}}}}</a>', 1)
    if f'data-room="{rid}" href' not in html:
        sys.exit('render_kamer: onderbalk-knop van lander-w1 niet gevonden (sjabloon veranderd?)')

    fotos = data.get('_fotos') or []
    if not 1 <= len(fotos) <= 8:
        sys.exit(f'render_kamer: _fotos moet 1 tot 8 foto\'s hebben, niet {len(fotos)}')
    for f in fotos:
        if not os.path.exists(os.path.join(base, f['img'])):
            sys.exit(f'render_kamer: {f["img"]} bestaat niet')
    video = data.get('_video')
    if video and not os.path.exists(os.path.join(base, video['src'])):
        sys.exit(f'render_kamer: {video["src"]} bestaat niet')
    start = 1 if video else 0          # lightbox-index van de eerste foto
    n = len(fotos)
    alle = f'{e(data["FOTOS_KNOP"])} <span class="km-g-aantal">({n})</span>'
    pos = lambda f: f' style="object-position:{a(f["pos"])}"' if f.get('pos') else ''

    # mozaiek: bureaublad 5 kolommen (groot 3x2, breed 2x1, klein 1x1; bij 8 foto's onderrij 4 klein + tegel zoals de staging);
    # minder dan 8: groot + breed + klein + tegel (data-n = aantal zichtbare foto's, 1-3 of 8), de rest staat in de lightbox
    tegels = []
    zichtbaar = fotos[:8] if n >= 8 else fotos[:3]
    for i, f in enumerate(zichtbaar):
        soort = ' km-g-groot' if i == 0 else (' km-g-breed' if i == 1 else '')
        tegels.append(f'        <button type="button" class="km-g-item{soort}" data-lb="{start + i}" aria-label="{a(data["FOTO_VERGROOT"])}: {a(f["alt"])}">'
                      f'<img src="{a(f["img"])}" alt="{a(f["alt"])}"{pos(f)}' + ('' if i == 0 else ' loading="lazy"') + ' width="1600" height="1068"></button>')
    tegels.append(f'        <button type="button" class="km-g-alle" data-lb="0">{kamer_icoon("raster")}<span>{alle}</span></button>')
    html = html.replace('<!-- KM_GALERIJ -->', '\n'.join(tegels)).replace('{{KM_N}}', str(len(zichtbaar)))

    media = ([{'type': 'video', 'src': video['src'], 'poster': video.get('poster') or fotos[0]['img'], 'alt': data.get('VIDEO_ALT', '')}] if video else []) \
        + [{'type': 'img', 'src': f['img'], 'alt': f['alt']} for f in fotos]
    html = html.replace('<!-- KM_MEDIA -->', json.dumps(media, ensure_ascii=False).replace('</', '<\\/'))
    html = html.replace('{{KM_FOTOS_ALLE}}', alle).replace('{{KM_HERO_IMG}}', a(fotos[0]['img']))

    gi = data.get('ALLES_FOTO', 0)
    html = html.replace('{{KM_ALLES_IMG}}', a(fotos[gi]['img'])).replace('{{KM_ALLES_ALT}}', a(fotos[gi]['alt'])) \
               .replace('{{KM_ALLES_POS}}', pos(fotos[gi])).replace('{{KM_ALLES_LB}}', str(start + gi))

    vink = kamer_icoon('vink')
    html = html.replace('<!-- KM_VINKJES -->', ''.join(f'<li>{vink}<span>{e(v)}</span></li>' for v in data['_vinkjes']))
    specs = data['_specs']
    if len(specs) != 5:
        sys.exit(f'render_kamer: _specs moet 5 tegels hebben, niet {len(specs)}')
    html = html.replace('<!-- KM_SPECS -->', '\n'.join(
        f'            <li class="km-spec"><span class="km-dot">{kamer_icoon(s["icoon"])}</span><span class="km-spec-tekst">{e(s["tekst"])}</span></li>' for s in specs))
    html = html.replace('<!-- KM_FACILITEITEN -->', '\n'.join(
        f'            <li><span class="km-dot">{kamer_icoon(s["icoon"])}</span><span>{e(s["tekst"])}</span></li>' for s in data['_faciliteiten']))
    html = html.replace('<!-- KM_WETEN -->', '\n'.join(
        f'            <div class="km-feit"><span class="km-dot km-dot--groot">{kamer_icoon(w["icoon"])}</span><div><dt>{e(w["titel"])}</dt><dd>{e(w["tekst"])}</dd></div></div>'
        for w in data['_weten']))
    faq = data['_faq']
    if not 3 <= len(faq) <= 6:
        sys.exit(f'render_kamer: _faq moet 3 tot 6 vragen hebben, niet {len(faq)}')
    html = html.replace('<!-- KM_FAQ -->', '\n'.join(
        f'            <details class="km-faq-item"><summary>{e(q["q"])}<span class="km-plus" aria-hidden="true"></span></summary><div class="km-faq-a"><p>{e(q["a"])}</p></div></details>'
        for q in faq))
    pijl = '<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    verder = data['_verder']
    for v in verder:
        if not os.path.exists(os.path.join(base, v['img'])):
            sys.exit(f'render_kamer: {v["img"]} bestaat niet')
        if not v['url'].startswith('/'):
            sys.exit(f'render_kamer: _verder-url {v["url"]!r} moet een visit.asteria.nl-pad zijn (geen asteria.nl, gesloten)')
    html = html.replace('<!-- KM_VERDER -->', '\n'.join(
        f'        <a class="km-link" href="{a(v["url"])}"><span class="km-link-beeld"><img src="{a(v["img"])}" alt="{a(v["alt"])}" loading="lazy"{pos(v)}></span>'
        f'<span class="km-link-tekst"><span class="km-link-titel">{e(v["titel"])}</span><span class="km-link-regel">{e(v["regel"])}</span></span></a>'
        for v in verder))

    # andere kamers uit de JSON's van de andere kamers
    kaarten = []
    for slug, ksleutel, link in KAMER_VOLGORDE:
        if slug == eigen:
            continue
        with open(os.path.join(base, f'translations/kamer-{slug}-v2-nl.json'), encoding='utf-8') as f:
            k = json.load(f)
        foto = k['_fotos'][0]
        kaarten.append(
            f'          <li class="km-ak"><article class="km-ak-kaart">'
            f'<div class="km-ak-tekst"><h3>{e(k["KAMER_NAAM"])}</h3><p>{e(k["KAART_REGEL"])}</p>'
            f'<span class="km-chip">{e(k["KAART_CHIP"])}</span>'
            f'<p class="km-ak-prijs" data-kamer-vanaf="{ksleutel}"><span class="km-ak-vanaf">{e(data["PRIJS_VANAF"])}</span><b data-kamer-vanaf-bedrag>€ …</b><span>{e(data["PRIJS_PER"])}</span></p>'
            f'<span class="km-ak-knoppen"><a class="btn btn-primary mews-open" data-room="{k["KAMER_ROOM"]}" href="{MEWS_KAMER_URL.format(id=k["KAMER_ROOM"])}" aria-label="{a(data["KAART_KNOP"])}: {a(k["KAMER_NAAM"])}">{e(data["KAART_KNOP"])}</a>'
            f'<a class="btn btn-secondary" href="spiegel:{link}">{e(data["ANDERE_KNOP"])}</a></span></div>'
            f'<div class="km-ak-foto"><img src="{a(foto["img"])}" alt="{a(foto["alt"])}" loading="lazy"{pos(foto)}></div></article></li>')
    html = html.replace('<!-- KM_ANDERE -->', '\n'.join(kaarten))

    # reviews: donkere scorekaart (in het sjabloon) + quote-kaarten
    with open(os.path.join(base, 'content/reviews-google-asteria.json'), encoding='utf-8') as f:
        rev = json.load(f)
    lijst = list(rev.get('reviews') or [])
    noemt = lambda r: 'kamer' in (r.get('tekst') or '').lower()
    lijst = [r for r in lijst if noemt(r)] + [r for r in lijst if not noemt(r)]
    quote = '<svg class="km-q-ic" viewBox="0 0 32 24" aria-hidden="true"><path d="M0 24V13.7C0 5.9 4.2 1.3 12.4 0l1.3 3.4C9.3 4.6 7.2 7.2 7 11h6v13zm18 0V13.7C18 5.9 22.2 1.3 30.4 0l1.3 3.4c-4.4 1.2-6.5 3.8-6.7 7.6h6v13z"/></svg>'
    rk = []
    for r in lijst[:8]:
        tekst = ' '.join((r.get('tekst') or '').split())
        if len(tekst) > 200:
            tekst = tekst[:200].rsplit(' ', 1)[0].rstrip(' ,.;:!?') + ' …'
        naam = r.get('naam') or 'Gast'
        delen = naam.split()
        kort = delen[0] + (f' {delen[-1][0]}.' if len(delen) > 1 else '')
        datum = (r.get('datum') or '').strip()
        rk.append(f'          <li><figure class="km-rev">{quote}<blockquote>{e(tekst)}</blockquote>'
                  f'<figcaption><span class="km-rev-ini" aria-hidden="true">{e(naam[0].upper())}</span><span><b>{e(kort)}</b>'
                  f'<span>Google{" &middot; " + e(datum) if datum else ""}</span></span></figcaption></figure></li>')
    html = html.replace('<!-- KM_REVIEWS -->', '\n'.join(rk))
    html = html.replace('{{GOOGLE_PROFIEL}}', escape(rev.get('profiel_url') or ''))
    return html


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# Duitse Google Ads-landers (sjabloon adslander.template.html). Nabouw van de Parkhotel-lander
# /de/wellnesshotel-limburg-nieuw/ in de Asteria-stijl; zie de kop van het sjabloon en CLAUDE.md.
# Alle teksten/foto's/slots uit translations/adslander-<naam>-de.json (veldnamen zoals Parkhotel),
# pop-upinhoud + kamerkaarten uit content/adslander-pop-de.json, arrangementcode/prijs/nachten/
# Mews-config uit de arrangement-JSON (veld arr-<slot>-bron), kalenderinstellingen uit
# content/arr-kalender.json, kop en voet letterlijk (gesloten stand) uit lander-w1.template.html.
# ═══════════════════════════════════════════════════════════════════════════════════════════════

AL_POP = 'content/adslander-pop-de.json'
AL_GOOGLE_G = ('<svg width="26" height="26" viewBox="0 0 48 48" aria-hidden="true"><path d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" fill="#FFC107"/>'
               '<path d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z" fill="#FF3D00"/>'
               '<path d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z" fill="#4CAF50"/>'
               '<path d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z" fill="#1976D2"/></svg>')
AL_STER = '<svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"/></svg>'
AL_VINK = ('<svg class="al-vink" width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>')
AL_TRUST_IC = ('<svg class="al-trust__ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5 5.5-6"/></svg>')
AL_PIJL = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>')
AL_VERGROOT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
               'aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5M11 8v6M8 11h6"/></svg>')
AL_REIS = {
    'auto': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.75 15.25V13a2 2 0 0 1 1.5-1.94l2.1-.53 2.05-2.9a2 2 0 0 1 1.63-.88h4.1a2 2 0 0 1 1.6.8l2.27 3.03 1.8.45A2 2 0 0 1 21.25 13v2.25"/><path d="M2.75 15.25h1.9M9.15 15.25h5.7M19.35 15.25h1.9"/><path d="M6.35 10.6h11.9M12 6.75v3.85"/><circle cx="6.9" cy="15.75" r="2.25"/><circle cx="17.1" cy="15.75" r="2.25"/></svg>',
    'voet': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="13.6" cy="4.1" r="1.75"/><path d="M12.6 7.6 10.4 13.2 8.2 20.5"/><path d="M10.4 13.2 13.2 16l1 4.5"/><path d="M12.3 8.4l2.3 3 2.4.8"/><path d="M12 8.5 9.2 10.2l-1 2.6"/></svg>',
    'rad': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.75" cy="16.25" r="3.5"/><circle cx="18.25" cy="16.25" r="3.5"/><path d="M5.75 16.25h5.75l4.1-6.85M5.75 16.25 9.3 9.4l2.2 6.85M9.3 9.4h6.3l2.65 6.85"/><path d="M15.6 9.4l-.5-2.65h2.3M9.3 9.4l-.4-2h-1.4h3"/></svg>',
    'start': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
}
# kenmerk-iconen op de kamerkaart (as-icoon: stroke currentColor)
AL_KAMER_IC = {
    'm2': '<path d="M3 3h18v18H3z"/><path d="M3 9h4M3 15h4M9 3v4M15 3v4"/>',
    'bed': '<path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/>',
    'personen': '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>',
    'airco': '<path d="M12 2v20"/><path d="M4.93 7l14.14 10"/><path d="M4.93 17L19.07 7"/><path d="M9 4l3 2 3-2"/><path d="M9 20l3-2 3 2"/>',
    'sauna': '<path d="M8 3c-1 1.5 1 2.5 0 4M12 3c-1 1.5 1 2.5 0 4M16 3c-1 1.5 1 2.5 0 4"/><path d="M3 11h18v4H3z"/><path d="M5 15v6M19 15v6M3 19h18"/>',
    'stoel': '<path d="M6 19v2M18 19v2"/><path d="M5 11V7a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v4"/><path d="M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    'bad': '<path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.68 3 4 3.68 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/><path d="M2 12h20"/><path d="M7 19v2M17 19v2"/>',
    'douche': '<path d="M4 4l2.5 2.5"/><path d="M13.5 6.5a4.95 4.95 0 0 0-7 7"/><path d="M15 5 5 15"/><path d="M14 17v.01M10 16v.01M13 13v.01M16 10v.01M11 20v.01M17 14v.01M20 11v.01"/>',
    'rolstoel': '<circle cx="12" cy="4" r="2"/><path d="M12 6v7h5l2 5"/><path d="M12 9h4"/><path d="M8.5 10.5a6 6 0 1 0 7.9 7.9"/>',
}


def al_lijst(d, voorvoegsel, achtervoegsel=''):
    """Genummerde slots ({voorvoegsel}1{achtervoegsel}, 2, ...) tot het eerste ontbrekende nummer."""
    uit, i = [], 1
    while (voorvoegsel + str(i) + achtervoegsel) in d:
        uit.append(i)
        i += 1
    return uit


def al_kalender_teksten(nachten, zondag, taal='de', dagen=None):
    """Teksten van de prijskalender (dialog.ark). taal='de' (adslander, standaard) of 'nl' (uitje-sjabloon; zelfde
    zinnen als apply_kalender op de NL-arrangementpagina's)."""
    if taal == 'nl':
        if nachten > 1:
            if dagen:
                lijst = [WEEKDAGEN[x] for x in sorted(dagen, key=lambda x: (x + 6) % 7)]
                wanneer = lijst[0] if len(lijst) == 1 else ', '.join(lijst[:-1]) + ' of ' + lijst[-1]
                sub = f'Aankomst kan op {wanneer}. Je vertrek na {nachten} nachten komt er vanzelf bij.'
            else:
                sub = f'Klik op je aankomstdag. Je vertrek na {nachten} nachten komt er vanzelf bij.'
            return {'kop': 'Kies je aankomstdag', 'sub': sub,
                    'noot': f'Prijs per persoon voor {nachten} nachten bij aankomst op die dag,',
                    'dicht': 'Grijs: geen aankomst mogelijk'}
        return {'kop': 'Kies je nachten',
                'sub': 'Klik op je aankomstdag en daarna op je vertrekdag. Vertrekken kan ook op een grijze dag.',
                'noot': 'Prijs per persoon per nacht bij aankomst op die dag,',
                'dicht': 'Grijs: niet beschikbaar, vertrekken kan wel'}
    if nachten > 1:
        return {'kop': 'Wählen Sie Ihren Anreisetag',
                'sub': f'Klicken Sie auf Ihren Anreisetag. Die Abreise nach {nachten} Nächten kommt automatisch dazu.',
                'noot': f'Preis pro Person für {nachten} Nächte bei Anreise an diesem Tag,',
                'dicht': 'Grau: keine Anreise möglich'}
    return {'kop': 'Wählen Sie Ihre Nächte',
            'sub': 'Klicken Sie auf Ihren Anreisetag und danach auf Ihren Abreisetag. Abreisen geht auch an einem grauen Tag.',
            'noot': 'Preis pro Person und Nacht bei Anreise an diesem Tag,',
            'dicht': 'Grau: nicht verfügbar, Abreise ist möglich'}


AL_KAL_LABELS = {
    'de': {'aankomst': 'Anreise', 'vertrek': 'Abreise', 'vertrek-vraag': 'Abreise?', 'nacht': 'Nacht', 'nachten-woord': 'Nächte',
           'vorige': 'Vorheriger Monat', 'volgende': 'Nächster Monat', 'personen': '2 Personen',
           'zondag': 'Gold: Anreise am Sonntag, 20 € pro Zimmer günstiger', 'gevuld': 'Gefüllt: Ihre gewählten Nächte',
           'wis': 'Löschen', 'knop': 'Zimmer und Preise ansehen', 'code': 'Aktionscode <b>{code}</b> wird automatisch eingetragen'},
    # NL = de labels van de dialoog #ar-kal in lander-w1.template.html (NL-arrangementpagina's)
    'nl': {'aankomst': 'aankomst', 'vertrek': 'vertrek', 'vertrek-vraag': 'vertrek?', 'nacht': 'nacht', 'nachten-woord': 'nachten',
           'vorige': 'Vorige maand', 'volgende': 'Volgende maand', 'personen': '2 personen',
           'zondag': 'Goud: aankomst op zondag, € 20 per kamer voordeliger', 'gevuld': 'Gevuld: je gekozen nachten',
           'wis': 'Wissen', 'knop': 'Bekijk kamers en prijzen', 'code': 'Actiecode <b>{code}</b> wordt automatisch ingevuld'},
}


def al_kalender_dialoog(code, cfg, nachten, k, kamer_namen, sluit_label, taal='de'):
    """Een prijskalender dialog.ark voor een arrangementcode (arrangement-kalender.js, /api/arr-kalender). k = de instellingen
    van de code uit content/arr-kalender.json; kamer_namen = {Mews-kamer-id: naam}. taal 'de' (adslander) of 'nl' (uitje)."""
    from html import escape
    L = AL_KAL_LABELS[taal]
    zondag = bool(k.get('zondag'))
    dagen = k.get('aankomstdagen') or []
    t = al_kalender_teksten(nachten, zondag, taal, dagen)
    leg_zondag = f'<span><i class="o"></i>{L["zondag"]}</span>' if zondag else ''
    kid = 'ar-kal-kop-' + code.lower()
    return (
        f'<dialog class="ark" aria-labelledby="{kid}" data-code="{code}" data-mews-config="{cfg}" data-nachten="{nachten}" '
        f'data-aankomstdagen="{",".join(str(x) for x in dagen)}" data-zondag="{"ja" if zondag else "nee"}" data-kamer-standaard="{k["standaardkamer"]}" '
        f'data-kamers="{escape(json.dumps(kamer_namen, ensure_ascii=False, separators=(",", ":")))}" '
        f'data-aankomst="{L["aankomst"]}" data-vertrek="{L["vertrek"]}" data-vertrek-vraag="{L["vertrek-vraag"]}" data-nacht="{L["nacht"]}" data-nachten-woord="{L["nachten-woord"]}" '
        f'data-vorige="{L["vorige"]}" data-volgende="{L["volgende"]}">\n'
        '    <div class="ark-greep" aria-hidden="true"></div>\n'
        f'    <div class="ark-kopr"><div><p class="ark-kop" id="{kid}">{t["kop"]}</p><p class="ark-sub">{t["sub"]}</p></div><button type="button" class="ark-x" aria-label="{sluit_label}"><svg viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M2 2l10 10M12 2 2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button></div>\n'
        '    <div class="ark-mid">\n'
        f'      <div class="ark-kal"><div class="ark-maanden"></div><p class="ark-noot">{t["noot"]} <span class="ark-kamer"></span>, {L["personen"]}</p></div>\n'
        f'      <div class="ark-leg">{leg_zondag}<span><i class="c"></i>{t["dicht"]}</span><span><i class="s"></i>{L["gevuld"]}</span></div>\n'
        '    </div>\n'
        '    <div class="ark-voet">\n'
        f'      <div class="ark-samen"><span class="ark-wat" aria-live="polite"></span><button type="button" class="ark-wis" hidden>{L["wis"]}</button></div>\n'
        f'      <button type="button" class="btn btn-primary ark-btn" disabled>{L["knop"]}</button>\n'
        f'      <p class="ark-code">{L["code"].format(code=code)}</p>\n'
        '    </div>\n'
        '    <span class="ark-tip" aria-hidden="true"></span>\n'
        '  </dialog>')


def al_kop_voet(d, mews_basis, taal='de'):
    """Kop (utility-balk, menu met submenu's, telefoonknop, boekknop), mobiele lade en voet letterlijk uit
    lander-w1.template.html in de spiegelstand zoals /hotel-venray-v2 (blokken gesloten + spiegel; links uit
    translations/spiegel-links.json via vul_spiegel_links, dus dezelfde bestemmingen), met Duitse labels en zonder actiecode.
    Logo naar de lander zelf. taal='nl' (uitje-sjabloon): de Duitse labelvervanging wordt overgeslagen, de NL-labels uit
    lander-w1.template.html blijven staan; logo, actiecode en Mews-taal gaan wel om."""
    with open(os.path.join(base, 'lander-w1.template.html'), encoding='utf-8') as f:
        w1 = apply_blokken(f.read(), {'gesloten', 'spiegel'})
    kop = re.search(r'<header class="top-stack[\s\S]*?</header>', w1).group(0)
    lade = re.search(r'<aside class="nav-drawer[\s\S]*?</aside>', w1).group(0)
    voet = re.search(r'<footer class="footer[\s\S]*?</footer>', w1).group(0)
    eigen = '/' + d['canonical'].rstrip('/').rsplit('/', 1)[-1]
    vervang = [
        ('{{GESLOTEN_LOGO_URL}}', eigen),
        ('?mewsVoucherCode={{VOUCHER}}&amp;', '?'),
        ('?mewsVoucherCode={{VOUCHER}}', '?language=' + d.get('mews-taal', 'de-DE')),
        (' data-voucher="{{VOUCHER}}"', ''),
    ]
    if taal == 'de':
        vervang += al_kop_voet_de(d)
    elif taal == 'en':
        vervang += al_kop_voet_en(d)
    delen = []
    for x in (kop, lade, voet):
        for a_, b_ in vervang:
            x = x.replace(a_, b_)
        delen.append(vul_spiegel_links(x))
    kop, lade, voet = delen
    if re.search(r'\{\{[A-Z_]+\}\}|mewsVoucherCode', kop + lade + voet):
        sys.exit('adslander: kop/voet bevat een open veld of een actiecode')
    return kop + '\n' + lade, voet


def al_kop_voet_de(d):
    """Duitse labels van de spiegelkop/-voet (adslander), in deze volgorde na de vier vaste vervangingen."""
    tel = d['telefoon']
    return [
        ('Hotel Asteria, naar het begin van de pagina', 'Hotel Asteria, zum Seitenanfang'),
        ('aria-label="Hoofdnavigatie"', 'aria-label="Hauptnavigation"'),
        ('aria-label="Bel Hotel Asteria: 0478 511466"', f'aria-label="Hotel Asteria anrufen: {tel}"'),
        ('aria-label="Bel ons"', 'aria-label="Rufen Sie uns an"'),
        ('aria-label="E-mail ons"', 'aria-label="Schreiben Sie uns"'),
        ('aria-label="Open menu"', 'aria-label="Menü öffnen"'),
        ('aria-label="Mobiel menu"', 'aria-label="Mobiles Menü"'),
        ('aria-label="Sluit menu"', 'aria-label="Menü schließen"'),
        ('aria-label="Volg ons"', 'aria-label="Folgen Sie uns"'),
        ('>0478 511466<', f'>{tel}<'),
        ('>0478 511 466<', f'>{tel}<'),
        ('>Kamers &amp; suites<', '>Zimmer &amp; Suiten<'),
        ('>Faciliteiten<', '>Einrichtungen<'),
        ('>Wellness &amp; fitness<', '>Wellness &amp; Fitness<'),
        ('>Arrangementen<', '>Arrangements<'),
        ('>Omgeving<', '>Umgebung<'),
        ('>Over ons <', '>Über uns <'),
        ('>Ons verhaal<', '>Unsere Geschichte<'),
        ('>Contact<', '>Kontakt<'),
        ('>Boek nu<', '>' + d['kop-boek'] + '<'),
        ('>Verblijf<', '>Aufenthalt<'),
        ('>Bruidssuite<', '>Brautsuite<'),
        ('>Junior suite<', '>Junior Suite<'),
        ('>Comfort kamer<', '>Comfort-Zimmer<'),
        ('>Deluxe kamer<', '>Deluxe-Zimmer<'),
        ('>Beschikbaarheid<', '>Verfügbarkeit<'),
        ('>Bij ons<', '>Bei uns<'),
        ('>Route &amp; parkeren<', '>Anfahrt &amp; Parken<'),
        ('Privacyverklaring', 'Datenschutz'),
        ('Algemene voorwaarden', 'AGB'),
        ('A73, afrit 8 Venray Noord&middot; KvK 12028838 &middot; btw NL804668528B01',
         'A73, Ausfahrt 8 Venray-Noord &middot; KvK 12028838 &middot; USt-IdNr. NL804668528B01'),
    ]


def al_kop_voet_en(d):
    """Engelse labels van de spiegelkop/-voet (uitje-sjabloon, taal en), zelfde volgorde en doelen als al_kop_voet_de."""
    tel = d['telefoon']
    return [
        ('Hotel Asteria, naar het begin van de pagina', 'Hotel Asteria, back to the top of the page'),
        ('aria-label="Hoofdnavigatie"', 'aria-label="Main navigation"'),
        ('aria-label="Bel Hotel Asteria: 0478 511466"', f'aria-label="Call Hotel Asteria: {tel}"'),
        ('aria-label="Bel ons"', 'aria-label="Call us"'),
        ('aria-label="E-mail ons"', 'aria-label="Email us"'),
        ('aria-label="Open menu"', 'aria-label="Open menu"'),
        ('aria-label="Mobiel menu"', 'aria-label="Mobile menu"'),
        ('aria-label="Sluit menu"', 'aria-label="Close menu"'),
        ('aria-label="Volg ons"', 'aria-label="Follow us"'),
        ('>0478 511466<', f'>{tel}<'),
        ('>0478 511 466<', f'>{tel}<'),
        ('>Kamers &amp; suites<', '>Rooms &amp; suites<'),
        ('>Faciliteiten<', '>Facilities<'),
        ('>Wellness &amp; fitness<', '>Wellness &amp; fitness<'),
        ('>Arrangementen<', '>Packages<'),
        ('>Omgeving<', '>Surroundings<'),
        ('>Over ons <', '>About us <'),
        ('>Ons verhaal<', '>Our story<'),
        ('>Contact<', '>Contact<'),
        ('>Boek nu<', '>' + d['kop-boek'] + '<'),
        ('>Verblijf<', '>Stay<'),
        ('>Bruidssuite<', '>Bridal suite<'),
        ('>Junior suite<', '>Junior suite<'),
        ('>Comfort kamer<', '>Comfort room<'),
        ('>Deluxe kamer<', '>Deluxe room<'),
        ('>Beschikbaarheid<', '>Availability<'),
        ('>Bij ons<', '>At Asteria<'),
        ('>Route &amp; parkeren<', '>Directions &amp; parking<'),
        ('Privacyverklaring', 'Privacy statement'),
        ('Algemene voorwaarden', 'Terms and conditions'),
        ('A73, afrit 8 Venray Noord&middot; KvK 12028838 &middot; btw NL804668528B01',
         'A73, exit 8 Venray-Noord &middot; Chamber of Commerce 12028838 &middot; VAT NL804668528B01'),
    ]


def build_adslander(config, output_file, json_file, template_name, lang):
    from html import escape
    import hashlib
    with open(os.path.join(base, config['template']), encoding='utf-8') as f:
        html = f.read()
    with open(os.path.join(base, json_file), encoding='utf-8') as f:
        d = json.load(f)
    with open(os.path.join(base, AL_POP), encoding='utf-8') as f:
        pop_tekst = f.read()
    pop = json.loads(pop_tekst)
    with open(KALENDER_JSON, encoding='utf-8') as f:
        kal_cfg = json.load(f)
    taal = d.get('mews-taal', 'de-DE')
    mews = lambda cfg='6dc9094c-76e3-4fd8-83a7-af1d00ffc556', extra='': f'https://app.mews.com/distributor/{cfg}?language={taal}{extra}'
    d['mews-basis'] = mews()
    d['pop-bron'] = AL_POP + '?v=' + hashlib.md5(pop_tekst.encode()).hexdigest()[:8]
    fouten = []

    def bestaat(pad):
        if pad and not os.path.exists(os.path.join(base, pad)):
            fouten.append('bestand ontbreekt: ' + pad)
        return pad

    for k in ('hero-video-bureaublad', 'hero-video-mobiel', 'hero-poster-bureaublad', 'hero-poster-bureaublad-klein', 'hero-poster-mobiel',
              'slot-foto', 'slot-portret'):
        bestaat(d.get(k))

    blok = {}
    blok['AL_GOOGLE_G'] = AL_GOOGLE_G
    blok['AL_STERREN'] = AL_STER * 4 + AL_STER.replace('<svg ', '<svg style="opacity:.35" ', 1)
    blok['AL_HERO_TRUST'] = ''.join(f'<li>{AL_TRUST_IC}<span>{d[f"hero-trust-{i}"]}</span></li>' for i in al_lijst(d, 'hero-trust-') if d[f'hero-trust-{i}'])
    blok['AL_SLOT_USPS'] = ''.join(f'<li>{AL_TRUST_IC}<span>{d[f"slot-usp-{i}"]}</span></li>' for i in al_lijst(d, 'slot-usp-') if d[f'slot-usp-{i}'])
    blok['AL_FEITEN'] = ''.join(f'<li>{AL_VINK}<span>{d[f"feit-{i}"]}</span></li>' for i in al_lijst(d, 'feit-'))

    # 3 fotoslider: beginstand rond-1 in het midden, de rest links/rechts verdeeld zoals adslander.js
    rond = al_lijst(d, 'rond-', '-foto')
    n = len(rond)
    if n < 5:
        sys.exit('adslander: de fotoslider heeft minstens 5 foto\'s nodig')
    standen = {-3: 'm3', -2: 'm2', -1: 'm1', 0: '0', 1: 'p1', 2: 'p2', 3: 'p3'}
    li = []
    for j, i in enumerate(rond):
        dd = j if j <= n // 2 else j - n
        foto = bestaat(d[f'rond-{i}-foto'])
        groot = d.get(f'rond-{i}-groot') or foto
        li.append(f'<li class="al-rond__item al-rond__item--{standen.get(dd, "weg")}" data-i="{j}"><div class="al-rond__beeld"><img src="{foto}" alt="{d[f"rond-{i}-alt"]}" width="600" height="800" loading="lazy" decoding="async">'
                  f'<button type="button" class="al-rond__vergroot" data-groot="{groot}" aria-label="{d["rond-vergroot"]}">{AL_VERGROOT}</button></div></li>')
    blok['AL_ROND'] = ''.join(li)

    # 4 arrangementen: drie slots, code/prijs/nachten uit de arrangement-JSON (arr-<slot>-bron)
    kamer_namen = {KAMER_MEWS[k]: v['naam'] for k, v in pop['kamer'].items() if k in KAMER_MEWS}
    kaarten, kalenders, live = [], [], False
    for slot in ('links', 'uit', 'rechts'):
        p = f'arr-{slot}-'
        with open(os.path.join(base, 'translations', d[p + 'bron'] + '-nl.json'), encoding='utf-8') as f:
            a = json.load(f)
        code, cfg = a['VOUCHER'], a.get('MEWS_CONFIG') or '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
        nachten = int(a.get('ARR_NACHTEN') or 1)
        kalender = a.get('ARR_KALENDER', True) is not False and code in kal_cfg
        vanaf_live = kalender and a.get('ARR_VANAF_LIVE', True) is not False
        live = live or vanaf_live
        eenheid = 'p.P. pro Nacht' if nachten == 1 else f'p.P. für {nachten} Nächte'
        bedrag = a['ARR_PRIJS'].replace('€ ', '€&nbsp;')
        bedrag_html = f'<span data-arr-vanaf="{code}">{bedrag}</span>' if vanaf_live else f'<span>{bedrag}</span>'
        sleutel = d[p + 'sleutel']
        if sleutel not in pop['arr']:
            fouten.append(f'pop-updata ontbreekt voor arr:{sleutel}')
        incl = ''.join(f'<li>{AL_VINK}<span>{d[f"{p}incl-{i}"]}</span></li>' for i in al_lijst(d, p + 'incl-'))
        past = f'<span class="al-ak__past">{d[p + "past"]}</span>' if d.get(p + 'past') else ''
        cls = 'al-ak al-ak--uit' if slot == 'uit' else 'al-ak al-ak--buiten'
        href = mews(cfg, f'&amp;mewsVoucherCode={code}')
        zondag_kaart = bool(kalender and kal_cfg[code].get('zondag'))
        kaarten.append(
            f'<article class="{cls}" data-code="{code}" data-zondag="{"ja" if zondag_kaart else "nee"}">'
            f'<div class="al-ak__foto"><img src="{bestaat(d[p + "foto"])}" alt="{d[p + "alt"]}" width="800" height="533" loading="lazy" decoding="async">{past}</div>'
            f'<div class="al-ak__kop"><p class="al-ak__tag">{d[p + "tag"]}</p><h3 class="al-ak__naam">{d[p + "naam"]}</h3></div>'
            f'<div class="al-ak__prijsblok"><p class="al-ak__prijs"><span class="al-ak__vf">{d["arr-vanaf-label"]}</span> {bedrag_html} <small>{eenheid}</small></p></div>'
            f'<ul class="al-ak__incl">{incl}</ul>'
            f'<div class="al-ak__acties"><a class="btn btn-primary al-ak__knop mews-open" href="{href}" data-voucher="{code}">{d["arr-knop"]}</a>'
            f'<a class="al-ak__ontdek" href="#al-arr" data-pop="arr:{sleutel}">{d["arr-link"]}&nbsp;&rarr;</a></div></article>')
        if kalender:
            kalenders.append(al_kalender_dialoog(code, cfg, nachten, kal_cfg[code], kamer_namen, d['rond-sluit']))
    blok['AL_ARR'] = ''.join(kaarten)
    blok['AL_KALENDERS'] = '\n  '.join(kalenders)
    blok['AL_VANAF_SCRIPT'] = '<script src="arr-vanaf.js" defer></script>' if live else ''

    # 5 kamerrij
    kk, kamerdata = [], {}
    for k in d['kamers']:
        if k not in KAMER_MEWS or k not in pop['kamer']:
            sys.exit(f'adslander: kamer {k!r} heeft geen Mews-id (KAMER_MEWS) of geen pop-updata')
        r, room = pop['kamer'][k], KAMER_MEWS[k]
        if r.get('kamer') != room:
            sys.exit(f'adslander: Mews-id van {k} in {AL_POP} wijkt af van KAMER_MEWS')
        for x in r['fotos'] + r.get('pop_fotos', []) + [r.get('video') or '', r['kaart_foto']]:
            bestaat(x)
        kenm = ''.join(f'<li>{icoon(AL_KAMER_IC[ic])}<span>{escape(t, quote=False)}</span></li>' for ic, t in r['kaart'])
        naam = escape(r['naam'], quote=False)
        kk.append(
            f'<article class="kk-kaart" data-kamerkaart="{k}"><a class="kk-foto" href="#al-kamers" data-kamer="{k}" aria-haspopup="dialog" tabindex="-1" aria-hidden="true"><img src="{r["kaart_foto"]}" width="1400" height="934" alt="" loading="lazy" decoding="async"></a>'
            f'<div class="kk-inhoud"><h3 class="kk-naam">{naam}</h3><p class="kk-tekst">{escape(r["kort"], quote=False)}</p>'
            f'<ul class="kk-kenmerken">{kenm}</ul>'
            f'<p class="kk-prijs" data-kamer-vanaf="{k}"><span>{d["kamer-vanaf"]}</span> <span class="kk-bedrag" data-kamer-vanaf-bedrag>€ …</span> <span>{d["kamer-per"]}</span></p>'
            f'<p class="kk-knoppen"><a class="btn btn-primary mews-open" href="{mews(extra="&amp;mewsRoom=" + room + "&amp;mewsRoute=rooms")}" data-room="{room}">{d["kamer-boek"]}</a>'
            f'<a class="btn btn-secondary" href="#al-kamers" data-kamer="{k}" aria-haspopup="dialog" aria-label="{d["kamer-info"]}: {naam}">{d["kamer-info"]}</a></p></div></article>')
        kamerdata[k] = {x: r[x] for x in ('naam', 'video', 'fotos', 'tekst', 'kenmerken', 'kamer')}
    blok['AL_KAMERS'] = ''.join(kk)
    # kamer-pop-up = de lander-w1-dialoog #lp-pop-kamer (opmaak uit lander-w1.css), Duitse labels, geen pil/actiecode/kamerpagina
    blok['AL_KAMERPOP'] = (
        f'<dialog class="lp-pop lp-pop--kamer" id="lp-pop-kamer" aria-modal="true" aria-labelledby="lp-pop-kamer-naam" data-l-foto="{d["kamer-pop-foto"]}" data-l-boek="{d["kamer-boek"]}">\n'
        f'    <button type="button" class="lp-pop__sluit" aria-label="{d["rond-sluit"]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>\n'
        '    <div class="lp-pop__binnen">\n'
        '      <div class="lp-pop__media">\n'
        f'        <video class="lp-pop__video" muted playsinline loop autoplay preload="none" aria-label="{d["kamer-pop-video"]}"></video>\n'
        '        <img class="lp-pop__hero" alt="" hidden>\n'
        '      </div>\n'
        '      <div class="lp-pop__fotos"></div>\n'
        '      <div class="lp-pop__body">\n'
        '        <h3 class="lp-pop__titel" id="lp-pop-kamer-naam"></h3>\n'
        '        <div class="lp-pop__tekst"></div>\n'
        '        <ul class="lp-pop__kenmerken"></ul>\n'
        '        <div class="lp-pop__acties">\n'
        f'          <a class="btn btn-primary mews-open lp-pop__boek" data-basis="{mews()}" href="{mews()}">{d["kamer-boek"]}</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </dialog>\n'
        '  <div class="lp-pop-overlay" hidden></div>\n'
        '  <template id="lp-pop-vink"><svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5 5.5-6"/></svg></template>\n'
        '  <script type="application/json" id="al-kamerdata">' + json.dumps(kamerdata, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    blok['AL_KAMER_KOP'] = f'<h2 class="al-kamers__kop">{d["kamer-kop"]}</h2>' if d.get('kamer-kop') else ''

    # 6 faciliteiten (precies 5: een groot + vier klein)
    fac = al_lijst(d, 'fac-', '-naam')
    if len(fac) != 5:
        sys.exit('adslander: het mozaiek heeft precies 5 faciliteiten nodig')
    tegels = []
    for j, i in enumerate(fac):
        s = d[f'fac-{i}-sleutel']
        if s not in pop['fac']:
            fouten.append(f'pop-updata ontbreekt voor fac:{s}')
        regel = f'<span class="al-tegel__regel">{d[f"fac-{i}-regel"]}</span>' if d.get(f'fac-{i}-regel') else ''
        tegels.append(f'<a class="al-tegel{" al-tegel--breed" if j == 0 else ""}" href="#al-fac" data-pop="fac:{s}"><img src="{bestaat(d[f"fac-{i}-foto"])}" alt="{d[f"fac-{i}-alt"]}" width="1400" height="934" loading="lazy" decoding="async">'
                      f'<span class="al-tegel__tekst"><span class="al-tegel__naam">{d[f"fac-{i}-naam"]}</span>{regel}<span class="al-tegel__meer">{d["fac-meer"]} {AL_PIJL}</span></span></a>')
    blok['AL_FAC'] = ''.join(tegels)

    # 7 omgeving (tot zes kaarten; leeg naam-veld = kaart weg)
    uk = []
    for i in al_lijst(d, 'omg-', '-naam'):
        p = f'omg-{i}-'
        if not d[p + 'naam']:
            continue
        s = d[p + 'sleutel']
        if s not in pop['uitje']:
            fouten.append(f'pop-updata ontbreekt voor uitje:{s}')
        reis = ''
        for soort in ('auto', 'voet', 'rad'):
            if d.get(p + soort):
                reis += f'<span title="{d["reis-" + soort]}">{AL_REIS[soort]}{d[p + soort]}<span class="al-vh"> {d["reis-" + soort]}</span></span>'
        if d.get(p + 'start'):
            reis += f'<span>{AL_REIS["start"]}{d[p + "start"]}</span>'
        uk.append(f'<a class="al-uk" href="#al-omg" data-pop="uitje:{s}"><img src="{bestaat(d[p + "foto"])}" alt="{d[p + "alt"]}" width="1400" height="932" loading="lazy" decoding="async">'
                  f'<span class="al-uk__body"><span class="al-uk__cat">{d[p + "cat"]}</span><span class="al-uk__naam">{d[p + "naam"]}</span><span class="al-uk__tekst">{d[p + "tekst"]}</span>'
                  f'<span class="al-uk__reis">{reis}</span><span class="al-uk__meer">{d["omg-knop"]} {AL_PIJL}</span></span></a>')
    blok['AL_OMG'] = ''.join(uk)
    html = html.replace('aria-live="polite">1/6</span>', f'aria-live="polite">1/{len(uk)}</span>')

    # 8 fotorij
    blok['AL_FOTORIJ'] = ''.join(f'<img class="al-fotorij__foto" src="{bestaat(d[f"fotorij-2-{i}-foto"])}" width="460" height="402" alt="{d[f"fotorij-2-{i}-alt"]}" loading="lazy" decoding="async">'
                                 for i in al_lijst(d, 'fotorij-2-', '-foto'))

    # 9 reviews (Duitse vertaling)
    with open(os.path.join(base, d['rev-bestand']), encoding='utf-8') as f:
        rv = json.load(f)
    d['rev-profiel'] = escape(rv.get('profiel_url', 'https://www.google.com/maps?cid=10392502528258527703'))
    rk = []
    for r in rv['reviews']:
        st = max(1, min(5, int(r.get('sterren') or 5)))
        rk.append(f'<article class="al-rev__kaart"><span class="al-rev__sterren" role="img" aria-label="{st}/5">{AL_STER * st}</span>'
                  f'<p class="al-rev__naam">{escape(r["naam"], quote=False)} <span class="al-rev__datum">&middot; {escape(r.get("datum", ""), quote=False)}</span></p>'
                  f'<p class="al-rev__tekst">„{escape(r["tekst"], quote=False)}“</p>'
                  f'<p class="al-rev__bron">{d["rev-bron"]} <b>Google</b></p></article>')
    blok['AL_REVIEWS'] = ''.join(rk)

    # 10 vragen + FAQPage
    ld = []
    for soort, plek in (('thema', 'AL_FAQ_THEMA'), ('alg', 'AL_FAQ_ALG')):
        items = []
        for j, i in enumerate(al_lijst(d, f'faq-{soort}-', '-v')):
            v, a = d[f'faq-{soort}-{i}-v'], d[f'faq-{soort}-{i}-a']
            items.append(f'<details class="as-accordeon__item"{" open" if soort == "thema" and j == 0 else ""}><summary class="as-accordeon__kop"><h3>{v}</h3></summary>'
                         f'<div class="as-accordeon__paneel"><p>{a}</p></div></details>')
            plat = lambda t: re.sub(r'<[^>]+>', '', t).replace('&amp;', '&')
            ld.append({'@type': 'Question', 'name': plat(v), 'acceptedAnswer': {'@type': 'Answer', 'text': plat(a)}})
        blok[plek] = ''.join(items)
    blok['AL_FAQ_LD'] = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': ld}, ensure_ascii=False).replace('</', '<\\/')

    blok['AL_SCRATCHCARD'] = ('<script>window.ScratchcardConfig = { stijl: \'2026\' };</script><link rel="stylesheet" href="scratchcard-2026.css">'
                              '<script src="analytics-d1.js" defer></script><script src="nieuwsbrief.js" defer></script><script src="scratchcard-popup.js" defer></script>'
                              if d.get('_popup_scratchcard') else '<script src="analytics-d1.js" defer></script><script src="nieuwsbrief.js" defer></script>')
    blok['AL_KOP'], blok['AL_VOET'] = al_kop_voet(d, d['mews-basis'])

    for k, v in blok.items():
        if f'<!-- {k} -->' not in html:
            sys.exit(f'adslander: plek <!-- {k} --> niet in het sjabloon')
        html = html.replace(f'<!-- {k} -->', v)
    for k, v in d.items():
        if isinstance(v, str) and not k.startswith('_'):
            html = html.replace('{{' + k + '}}', v)
    open_velden = sorted(set(re.findall(r'\{\{[^}]+\}\}', html)))
    if open_velden:
        sys.exit(f'adslander: open velden in {output_file}: {open_velden}')
    if fouten:
        sys.exit('adslander:\n  ' + '\n  '.join(fouten))
    if '—' in html:
        sys.exit('adslander: em-dash in de uitvoer')
    with open(os.path.join(base, output_file), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  [{template_name}/{lang}] → {output_file}  ({len(html)} chars)')


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# Uitjepagina's (sjabloon uitje.template.html). Exacte nabouw van de Parkhotel-omgevingspagina
# (parkhotel-site src/fragmenten/pagina-gebied-v2.html) in de Asteria-stijl van de adslander; zie de kop van het
# sjabloon en CLAUDE.md (Uitje-sjabloon). Gegevens: translations/uitje-labels-nl.json (vaste labels, eerst geladen)
# + translations/uitje-<slug>-nl.json (wint); kamers uit content/uitje-kamers-nl.json + KAMER_MEWS; kop/voet uit
# al_kop_voet(taal='nl'). Genummerde slots via al_lijst. Stopt bij een open veld, ontbrekend bestand, em-dash of
# een half gevuld FAQ-/meer-slot.
# ═══════════════════════════════════════════════════════════════════════════════════════════════

UT_LABELS = 'translations/uitje-labels-nl.json'
UT_KAMERS = 'content/uitje-kamers-nl.json'
UT_PIJL = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>')
UT_EXTERN = ('<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><path d="M9.5 2.5h4v4M13.5 2.5 7.5 8.5M11.5 9.5v3a1 1 0 0 1-1 1h-7a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1h3"/></svg>')
UT_VK = {
    'auto': AL_REIS['auto'],
    'fiets': AL_REIS['rad'],
    'lopen': AL_REIS['voet'],
    'km': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.5" cy="18.5" r="2"/><path d="M7.5 18.5h8a3 3 0 0 0 0-6h-7a3 3 0 0 1 0-6h9.5"/><path d="M15.5 3.5l3 3-3 3"/></svg>',
}
UT_SPELD = ('<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true"><path d="M12 21.5c-3.6-4-6.8-7.6-6.8-11.3a6.8 6.8 0 0 1 13.6 0c0 3.7-3.2 7.3-6.8 11.3z"/><circle cx="12" cy="10.2" r="2.6"/></svg>')
UT_CHEV = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'


def ut_taalbron(pad, lang):
    """Labels/kamerbron per taal: nl = het bestaande -nl-bestand, de/en = hetzelfde pad met -de/-en."""
    return pad if lang == 'nl' else pad.replace('-nl.json', f'-{lang}.json')


def ut_hreflang(config):
    """hreflang-links voor de head (via de plek UT_FAQ_LD, die binnen een script-tag staat: eerst die tag sluiten,
    na de links een lege script-tag openen die de </script> van het sjabloon sluit). Alleen talen waarvan de JSON
    bestaat; bij minder dan twee talen niets. x-default = de NL-pagina."""
    talen = {t: f for t, (f, j) in config.get('langs', {}).items() if os.path.exists(os.path.join(base, j))}
    if len(talen) < 2:
        return ''
    url = lambda f: 'https://visit.asteria.nl/' + f[:-5]
    regels = [f'<link rel="alternate" hreflang="{t}" href="{url(f)}">' for t, f in talen.items()]
    if 'nl' in talen:
        regels.append(f'<link rel="alternate" hreflang="x-default" href="{url(talen["nl"])}">')
    return '</script>\n  ' + '\n  '.join(regels) + '\n  <script>'


def build_uitje(config, output_file, json_file, template_name, lang):
    from html import escape
    with open(os.path.join(base, config['template']), encoding='utf-8') as f:
        html = f.read()
    with open(os.path.join(base, ut_taalbron(UT_LABELS, lang)), encoding='utf-8') as f:
        d = json.load(f)
    with open(os.path.join(base, json_file), encoding='utf-8') as f:
        d.update(json.load(f))   # het uitje-JSON wint van de labels
    with open(os.path.join(base, ut_taalbron(UT_KAMERS, lang)), encoding='utf-8') as f:
        kamerbron = json.load(f)['kamer']
    taal = d.get('mews-taal', 'nl-NL')
    mews = lambda extra='': f'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?language={taal}{extra}'
    d['mews-basis'] = mews()
    d.setdefault('hero-foto-klein', d.get('hero-foto', ''))
    d.setdefault('slot-foto-klein', d.get('slot-foto', ''))
    fouten = []
    plat = lambda t: re.sub(r'<[^>]+>', '', t).replace('&amp;', '&')

    def bestaat(pad):
        if pad and not pad.startswith('http') and not os.path.exists(os.path.join(base, pad)):
            fouten.append('bestand ontbreekt: ' + pad)
        return pad

    def klein(p):
        return d.get(p + '-foto-klein') or d[p + '-foto']

    def slot_compleet(voorvoegsel, nummers, achtervoegsels, verplicht):
        """Een slot is heel of leeg: staat een van de verplichte velden er, dan moeten ze er allemaal (gevuld) zijn."""
        for i in nummers:
            velden = [f'{voorvoegsel}{i}{a}' for a in verplicht]
            gevuld = [v for v in velden if d.get(v)]
            if gevuld and len(gevuld) != len(velden):
                fouten.append(f'slot {voorvoegsel}{i} is half gevuld: {", ".join(v for v in velden if not d.get(v))} ontbreekt')

    for k in ('hero-foto', 'hero-foto-klein', 'slot-foto', 'slot-foto-klein', 'kaart-foto', 'kaart-foto-klein', 'kaart-vignet'):
        bestaat(d.get(k))

    blok = {}

    # 2 oogopslag: vakjes alleen als het veld gevuld is; tabel t1..t5; routelink
    vk_label = {'auto': d['l-auto'], 'fiets': d['l-fiets'], 'lopen': d['l-lopen'], 'km': d['l-afstand']}
    vk_ico = {s: v.replace('<svg ', '<svg class="ut-vk__ico" ', 1) for s, v in UT_VK.items()}
    blok['UT_VAKJES'] = ''.join(f'<div class="ut-vk"><span class="ut-vk__ib">{vk_ico[s]}</span>'
                                f'<span class="ut-vk__t"><strong>{d["vk-" + s]}</strong><span>{vk_label[s]}</span></span></div>'
                                for s in ('auto', 'fiets', 'lopen', 'km') if d.get('vk-' + s))
    # tijdvakken (09.30-18.00) en dagbereiken (ma-vr) niet op het streepje afbreken
    ut_nw = lambda t: re.sub(r'\b(\d{1,2}\.\d{2}-\d{1,2}\.\d{2}|[A-Za-z]{2}-[a-z]{2})\b', r'<span class="ut-nw">\1</span>', t)
    blok['UT_TABEL'] = ''.join(f'<div class="ut-tabel__rij"><dt>{d[f"t{i}-label"]}</dt><dd>{ut_nw(d.get(f"t{i}-waarde", ""))}</dd></div>'
                               for i in al_lijst(d, 't', '-label') if d[f't{i}-label'])
    blok['UT_ROUTE'] = (f'<a class="al-intro__link ut-route" href="{d["route-url"]}" target="_blank" rel="noopener">{d["knop-route"]} {UT_PIJL}'
                        f'<span class="al-vh"> {d["l-nieuw-tabblad"]}</span></a>') if d.get('route-url') else ''

    # 3 verhaal: v1 foto rechts, v2 links, v3 rechts; v2 en v3 in .ut-verhaal__meer achter Lees meer
    def rij(i, rechts):
        p = f'v{i}-'
        foto = bestaat(d[p + 'foto'])
        b, h = d.get(p + 'b', '1400'), d.get(p + 'h', '933')
        link = ''
        if d.get(p + 'knop'):
            ext = str(d.get(p + 'knop-extern', '')).lower() in ('ja', 'true', '1')
            link = (f'<p class="ut-it__link"><a class="al-intro__link ut-verwijs" href="{d[p + "knop-url"]}"'
                    + (' target="_blank" rel="noopener"' if ext else '') + f'><span>{d[p + "knop"]}</span>'
                    + (f'<span class="al-vh"> {d["l-nieuw-tabblad"]}</span>{UT_EXTERN}' if ext else UT_PIJL) + '</a></p>')
        p2 = f'<p>{d[p + "p2"]}</p>' if d.get(p + 'p2') else ''
        return (f'<div class="ut-it{" ut-it--rechts" if rechts else ""}"><div class="ut-it__omhulsel"><div class="ut-it__rij">'
                f'<div class="ut-it__kolom ut-it__kolom--foto"><div class="ut-it__foto"><img src="{klein(p[:-1])}" srcset="{klein(p[:-1])} 700w, {foto} {b}w" '
                f'sizes="(min-width:1024px) 50vw, 100vw" alt="{d[p + "alt"]}" width="{b}" height="{h}" loading="lazy" decoding="async"></div></div>'
                f'<div class="ut-it__kolom ut-it__kolom--tekst"><div class="ut-it__tekst"><h2>{d[p + "kop"]}</h2><p>{d[p + "p1"]}</p>{p2}{link}</div></div>'
                '</div></div></div>')
    v = [i for i in al_lijst(d, 'v', '-kop') if d[f'v{i}-kop']][:3]
    if not v:
        sys.exit('uitje: het verhaal heeft minstens v1 nodig')
    meer = ''
    if len(v) > 1:
        meer = ('<div class="ut-verhaal__meer" id="ut-verhaal-meer">' + ''.join(rij(i, j % 2 == 0) for j, i in enumerate(v) if j) + '</div>'
                f'<div class="ut-meerbalk" hidden><button type="button" class="btn btn-primary ut-meerbalk__knop" aria-expanded="false" aria-controls="ut-verhaal-meer" '
                f'data-open="{d["l-leesmeer"]}" data-dicht="{d["l-leesminder"]}"><span class="ut-meerbalk__label">{d["l-leesmeer"]}</span>'
                f'<span class="ut-meerbalk__chev" aria-hidden="true">{UT_CHEV}</span></button></div>')
    credit = f'<div class="al-wrap"><p class="ut-fotocredit">{d["fotocredit-verhaal"]}</p></div>' if d.get('fotocredit-verhaal') else ''
    blok['UT_VERHAAL'] = f'<section data-component="ut-verhaal" class="ut-verhaal">{rij(v[0], True)}{meer}{credit}</section>'

    # 4 tip (alleen als gevuld)
    blok['UT_TIP'] = (f'<section data-component="ut-tip" class="al-sec ut-tip"><div class="al-wrap"><div class="al-paneel ut-tip__strook">'
                      f'<div class="ut-tip__kop"><h2>{d["tip-kop"]}</h2></div><div class="ut-tip__tekst"><p class="ut-tip__tip">{d["tip"]}</p>'
                      f'<p class="ut-tip__van">{d.get("tip-van", "")}</p></div></div></div></section>') if d.get('tip') else ''

    # 5 goed om te weten: tot zes kaarten; zonder foto een kaart met groot icoon
    kaarten = []
    for i in [i for i in al_lijst(d, 'g', '-kop') if d[f'g{i}-kop']][:6]:
        p = f'g{i}-'
        ico = f'<svg class="as-icoon ut-fk__ico" viewBox="0 0 24 24" aria-hidden="true">{d.get(p + "ico", "")}</svg>'
        if d.get(p + 'foto'):
            beeld = f'<img class="ut-fk__foto" src="{bestaat(d[p + "foto"])}" alt="{d.get(p + "alt", "")}" width="440" height="330" loading="lazy" decoding="async">'
            kaarten.append(f'<li class="ut-fk">{beeld}<div class="ut-fk__body">{ico}<h3 class="ut-fk__naam">{d[p + "kop"]}</h3><p>{d.get(p + "tekst", "")}</p></div></li>')
        else:
            kaarten.append(f'<li class="ut-fk ut-fk--leeg"><span class="ut-fk__leeg">{ico}</span><div class="ut-fk__body"><h3 class="ut-fk__naam">{d[p + "kop"]}</h3><p>{d.get(p + "tekst", "")}</p></div></li>')
    credit = f'<p class="ut-fotocredit">{d["fotocredit-prak"]}</p>' if d.get('fotocredit-prak') else ''
    blok['UT_PRAK'] = (f'<section data-component="ut-prak" class="al-sec ut-prak"><div class="ut-wrap--breed"><div class="ut-prak__kop"><h2>{d["g-kop"]}</h2></div>'
                       f'<ul class="ut-prak__tegels">{"".join(kaarten)}</ul>{credit}</div></section>') if kaarten else ''

    # 6 dag in vier momenten (alleen als dag-kop gevuld is)
    if d.get('dag-kop'):
        m = [i for i in al_lijst(d, 'm', '-naam') if d[f'm{i}-naam']][:4]
        beelden = ''.join(f'<figure class="ut-dag__beeld{" is-aan" if j == 0 else ""}" data-beeld="{i}"><img src="{klein(f"m{i}")}" '
                          f'alt="{d[f"m{i}-alt"]}" width="800" height="1000" loading="lazy" decoding="async" style="object-position:{d.get(f"m{i}-positie", "50% 50%")}"></figure>'
                          for j, i in enumerate(m) if bestaat(d[f'm{i}-foto']))
        momenten = ''.join(f'<li class="ut-moment{" is-aan" if j == 0 else ""}" data-moment="{i}"><h3 class="ut-moment__kop"><button type="button" class="ut-moment__kies" '
                           f'aria-expanded="{"true" if j == 0 else "false"}" aria-controls="ut-moment-{i}-open"><span class="ut-moment__deel">{d[f"m{i}-deel"]}</span>'
                           f'<span class="ut-moment__naam">{d[f"m{i}-naam"]}</span></button></h3><div class="ut-moment__open" id="ut-moment-{i}-open"><div>'
                           f'<p class="ut-moment__tekst">{d[f"m{i}-tekst"]}</p></div></div></li>' for j, i in enumerate(m))
        credit = f'<p class="ut-fotocredit">{d["fotocredit-dag"]}</p>' if d.get('fotocredit-dag') else ''
        sub = f'<p class="ut-dag__sub">{d["dag-sub"]}</p>' if d.get('dag-sub') else ''
        blok['UT_DAG'] = (f'<section data-component="ut-dag" class="al-sec ut-dag" data-start="{d.get("dag-start", "1")}"><div class="al-wrap">'
                          f'<div class="ut-dag__blok"><div class="ut-dag__bg" aria-hidden="true"></div><div class="ut-dag__foto">{beelden}</div>'
                          f'<div class="ut-dag__inner"><h2>{d["dag-kop"]}</h2>{sub}<ol class="ut-dag__lijst">{momenten}</ol></div></div>{credit}</div></section>')
    else:
        blok['UT_DAG'] = ''

    # 6a arrangementkaart (arr-bron) OF 6k kamers: sluiten elkaar uit
    kamers = d.get('kamers') or []
    if d.get('arr-bron') and kamers:
        sys.exit(f'uitje: {json_file} heeft zowel arr-bron ({d["arr-bron"]}) als een gevulde kamers-lijst; die sluiten elkaar uit '
                 '(zet kamers op [] voor een arrangementpagina, of haal arr-bron weg)')
    blok_arr, kalenders = '', []
    if d.get('arr-bron'):
        bron = os.path.join('translations', d['arr-bron'] + '-nl.json')
        if not os.path.exists(os.path.join(base, bron)):
            sys.exit(f'uitje: arr-bron {d["arr-bron"]!r}: {bron} bestaat niet')
        with open(os.path.join(base, bron), encoding='utf-8') as f:
            a = json.load(f)
        with open(KALENDER_JSON, encoding='utf-8') as f:
            kal_cfg = json.load(f)
        code = a['VOUCHER']
        cfg = a.get('MEWS_CONFIG') or '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
        nachten = int(a.get('ARR_NACHTEN') or 1)
        for x in ('arr-naam', 'arr-regel', 'arr-foto', 'arr-alt', 'arr-knop'):
            if not d.get(x):
                fouten.append(f'arrangementkaart: veld {x} ontbreekt of is leeg')
        # vinkjes: arr-vink1..6 doorlopend tot het eerste ontbrekende/lege; geen arr-vink1 = KAART_VINK_A..D van het arrangement
        vink = []
        for i in range(1, 7):
            if not d.get(f'arr-vink{i}'):
                break
            vink.append(d[f'arr-vink{i}'])
        if not vink:
            vink = [a[f'KAART_VINK_{x}'] for x in 'ABCD' if a.get(f'KAART_VINK_{x}')]
        regel2 = f'<p class="ut-arr__regel2">{d["arr-regel2"]}</p>' if d.get('arr-regel2') else ''
        lijst = (f'<ul class="ut-arr__vinkjes">' + ''.join(f'<li>{AL_VINK}<span>{v}</span></li>' for v in vink) + '</ul>') if vink else ''
        links = []
        if d.get('arr-pagina-url') and d.get('arr-paginalink'):
            links.append(f'<a class="al-intro__link ut-arr__link" href="{d["arr-pagina-url"]}">{d["arr-paginalink"]} {UT_PIJL}</a>')
        if d.get('arr-kamerlink'):
            links.append(f'<a class="al-intro__link ut-arr__link mews-open" href="{mews()}">{d["arr-kamerlink"]} {UT_PIJL}</a>')
        mews_arr = f'https://app.mews.com/distributor/{cfg}?language={taal}&amp;mewsVoucherCode={code}'
        fb, fh = 1400, 934   # echte fotomaten als Pillow er is (width/height tegen verspringen)
        try:
            from PIL import Image
            with Image.open(os.path.join(base, d['arr-foto'])) as im:
                fb, fh = im.size
        except Exception:
            pass
        blok_arr = (
            '  <!-- 6a. Arrangement: kaart met foto, vinkjes en boekknop (prijskalender, arrangement-kalender.js), zonder prijs -->\n'
            f'  <section data-component="ut-arr" class="al-sec ut-arr" id="arrangement"><div class="al-wrap"><div class="al-paneel ut-arr__kaart">'
            f'<img class="ut-arr__foto" src="{bestaat(d.get("arr-foto", ""))}" alt="{d.get("arr-alt", "")}" width="{fb}" height="{fh}" loading="lazy" decoding="async">'
            f'<div class="ut-arr__tekst"><h3 class="ut-arr__kop">{d.get("arr-naam", "")}</h3><p class="ut-arr__regel">{d.get("arr-regel", "")}</p>{regel2}{lijst}'
            f'<a class="btn btn-primary al-btn mews-open ut-arr__knop" href="{mews_arr}" data-voucher="{code}">{d.get("arr-knop", "")}</a>'
            + (f'<p class="ut-arr__links">{"".join(links)}</p>' if links else '') + '</div></div></div></section>\n\n')
        if a.get('ARR_KALENDER', True) is not False and code in kal_cfg:
            namen = {KAMER_MEWS[k]: v['naam'] for k, v in kamerbron.items() if k in KAMER_MEWS}
            # één dialoog op de pagina: meteen id ar-kal (daar hangt de stijl aan; arrangement-kalender.js zet de id alleen
            # zelf bij meerdere dialogen)
            kalenders.append(al_kalender_dialoog(code, cfg, nachten, kal_cfg[code], namen, d['pop-sluit'], taal='nl')
                             .replace('<dialog class="ark" ', '<dialog class="ark" id="ar-kal" ', 1))

    # 6k kamers: kaarten zoals de adslander, ZONDER prijs; Mews met kamer-id (KAMER_MEWS), Meer info = kamer-pop-up
    kk, kamerdata, popkamer = [], {}, {}
    for k in kamers:
        if k not in KAMER_MEWS or k not in kamerbron:
            sys.exit(f'uitje: kamer {k!r} heeft geen Mews-id (KAMER_MEWS) of geen kamerdata ({ut_taalbron(UT_KAMERS, lang)})')
        r, room = kamerbron[k], KAMER_MEWS[k]
        if r.get('kamer') != room:
            sys.exit(f'uitje: Mews-id van {k} in {ut_taalbron(UT_KAMERS, lang)} wijkt af van KAMER_MEWS')
        for x in r['fotos'] + r.get('pop_fotos', []) + [r.get('video') or '', r['kaart_foto']]:
            bestaat(x)
        kenm = ''.join(f'<li>{icoon(AL_KAMER_IC[ic])}<span>{escape(t, quote=False)}</span></li>' for ic, t in r['kaart'])
        naam = escape(r['naam'], quote=False)
        kk.append(
            f'<article class="kk-kaart" data-kamerkaart="{k}"><a class="kk-foto" href="#kamers" data-kamer="{k}" aria-haspopup="dialog" tabindex="-1" aria-hidden="true"><img src="{r["kaart_foto"]}" width="1400" height="934" alt="" loading="lazy" decoding="async"></a>'
            f'<div class="kk-inhoud"><h3 class="kk-naam">{naam}</h3><p class="kk-tekst">{escape(r["kort"], quote=False)}</p>'
            f'<ul class="kk-kenmerken">{kenm}</ul>'
            f'<p class="kk-knoppen"><a class="btn btn-primary mews-open" href="{mews("&amp;mewsRoom=" + room + "&amp;mewsRoute=rooms")}" data-room="{room}">{d["knop-kamer"]}</a>'
            f'<a class="btn btn-secondary" href="#kamers" data-kamer="{k}" aria-haspopup="dialog" aria-label="{d["knop-info"]}: {naam}">{d["knop-info"]}</a></p></div></article>')
        kamerdata[k] = {x: r[x] for x in ('naam', 'video', 'fotos', 'tekst', 'kenmerken', 'kamer')}
        popkamer[k] = {x: r[x] for x in ('naam', 'desc', 'pop_fotos', 'video', 'fotos', 'kenmerken', 'kamer') if x in r}
    def regel(plek, inhoud):
        """Vervang een hele sjabloonregel '  <!-- PLEK -->' (met regeleinde); leeg = de regel verdwijnt zonder spoor."""
        nonlocal html
        r = f'  <!-- {plek} -->\n'
        if html.count(r) != 1:
            sys.exit(f'uitje: regel <!-- {plek} --> niet precies een keer in het sjabloon')
        html = html.replace(r, inhoud)

    regel('UT_ARR', blok_arr)
    regel('UT_KALENDER_KOP', '  <link rel="stylesheet" href="arrangement-kalender.css">\n  <script src="arrangement-kalender.js" defer></script>\n'
          if kalenders else '')
    regel('UT_KALENDERS', ''.join(f'  {k}\n' for k in kalenders))
    if not kamers:
        # geen kamers: kamersectie (incl. de lege regel erna), kamer-pop-up en kamerdata weg
        html, n = re.subn(r'  <!-- UT_KAMERSECTIE -->\n[\s\S]*?  <!-- /UT_KAMERSECTIE -->\n\n', '', html)
        html, m = re.subn(r'  <!-- Kamer-pop-up[^\n]*-->\n  <!-- UT_KAMERPOP -->\n', '', html)
        if n != 1 or m != 1:
            sys.exit('uitje: kamersectie of kamer-pop-up niet gevonden in het sjabloon')
    else:
        regel('UT_KAMERSECTIE', '')
        regel('/UT_KAMERSECTIE', '')
        blok['UT_KAMERS'] = ''.join(kk)
    if kamers: blok['UT_KAMERPOP'] = (
        f'<dialog class="lp-pop lp-pop--kamer" id="lp-pop-kamer" aria-modal="true" aria-labelledby="lp-pop-kamer-naam" data-l-foto="{d["kamer-pop-foto"]}" data-l-boek="{d["knop-kamer"]}">\n'
        f'    <button type="button" class="lp-pop__sluit" aria-label="{d["pop-sluit"]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>\n'
        '    <div class="lp-pop__binnen">\n'
        '      <div class="lp-pop__media">\n'
        f'        <video class="lp-pop__video" muted playsinline loop autoplay preload="none" aria-label="{d["kamer-pop-video"]}"></video>\n'
        '        <img class="lp-pop__hero" alt="" hidden>\n'
        '      </div>\n'
        '      <div class="lp-pop__fotos"></div>\n'
        '      <div class="lp-pop__body">\n'
        '        <h3 class="lp-pop__titel" id="lp-pop-kamer-naam"></h3>\n'
        '        <div class="lp-pop__tekst"></div>\n'
        '        <ul class="lp-pop__kenmerken"></ul>\n'
        '        <div class="lp-pop__acties">\n'
        f'          <a class="btn btn-primary mews-open lp-pop__boek" data-basis="{mews()}" href="{mews()}">{d["knop-kamer"]}</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </dialog>\n'
        '  <div class="lp-pop-overlay" hidden></div>\n'
        '  <template id="lp-pop-vink"><svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5 5.5-6"/></svg></template>\n'
        '  <script type="application/json" id="al-kamerdata">' + json.dumps(kamerdata, ensure_ascii=False).replace('</', '<\\/') + '</script>')

    # 9 meer-uitjes (eerst, want de kaartknoppen verwijzen naar dezelfde pop-ups)
    pop_uitje = (d.get('_pop') or {}).get('uitje', {})
    for s, r in pop_uitje.items():
        for f in r.get('fotos', []):
            bestaat(f)
    meer_slots = al_lijst(d, 'meer', '-naam')
    slot_compleet('meer', meer_slots, ('-naam', '-cat', '-foto', '-alt'), ('-naam', '-cat', '-foto', '-alt'))
    uk = []
    for i in meer_slots[:3]:
        p = f'meer{i}-'
        if not d[p + 'naam']:
            continue
        url, pop = d.get(p + 'url', ''), d.get(p + 'pop', '')
        if not url and not pop:
            fouten.append(f'slot meer{i} heeft geen url en geen pop')
        if not url and pop not in pop_uitje:
            fouten.append(f'pop-updata ontbreekt voor uitje:{pop} (_pop.uitje in {json_file})')
        attr = f'href="{url}"' if url else f'href="#ut-meer" data-pop="uitje:{pop}"'
        reis = ''
        for soort, ic in (('auto', 'auto'), ('lopen', 'voet'), ('fiets', 'rad')):
            if d.get(p + soort):
                reis += f'<span>{AL_REIS[ic]}{d[p + soort]}<span class="al-vh"> {d["l-" + soort]}</span></span>'
        uk.append(f'<a class="al-uk ut-uk" {attr}><img src="{bestaat(d[p + "foto"])}" alt="{d[p + "alt"]}" width="1400" height="980" loading="lazy" decoding="async">'
                  f'<span class="al-uk__body"><span class="al-uk__cat ut-uk__cat">{d[p + "cat"]}</span><span class="al-uk__naam">{d[p + "naam"]}</span>'
                  f'<span class="al-uk__reis">{reis}</span><span class="al-uk__meer">{d["knop-meer"]} {AL_PIJL}</span></span></a>')
    credit = f'<p class="ut-fotocredit">{d["fotocredit-meer"]}</p>' if d.get('fotocredit-meer') else ''
    blok['UT_MEER'] = (f'<section data-component="ut-meer" class="al-sec ut-meer" id="ut-meer"><div class="ut-wrap--breed"><div class="ut-meer__kop"><h2>{d["meer-kop"]}</h2></div>'
                       f'<div class="ut-meer__rij">{"".join(uk)}</div>{credit}</div></section>') if d.get('meer-kop') and uk else ''

    # 7 ligging: getekende kaart; punten met pop moeten een bekende pop-up hebben
    if d.get('kaart-kop'):
        kaart = d.get('kaart') or {}
        if not isinstance(kaart, dict) or len(kaart.get('hotel') or []) != 2 or not kaart.get('punten'):
            sys.exit('uitje: kaart moet een object zijn met hotel [lat, lng] en punten')
        for pt in kaart['punten']:
            if not pt.get('hoofd'):
                if pt.get('pop') and pt['pop'].split(':', 1)[-1] not in pop_uitje:
                    fouten.append(f'kaartpunt {pt.get("naam")}: pop-updata ontbreekt voor {pt["pop"]}')
                if not pt.get('pop') and not pt.get('url'):
                    fouten.append(f'kaartpunt {pt.get("naam")}: geen url en geen pop')
        meta = ''
        if d.get('kaart-rijtijd') or d.get('kaart-km'):
            delen = [f'<b>{d["kaart-rijtijd"]}</b> {d["l-met-auto"]}'] if d.get('kaart-rijtijd') else []
            if d.get('kaart-km'):
                delen.append(f'({d["kaart-km"]})' if delen else d['kaart-km'])
            meta = f'<p class="ut-voet__meta">{AL_REIS["auto"]}<span>{" ".join(delen)}</span></p>'
        naam = f'<p class="ut-voet__naam">{d["kaart-naam"]}</p>' if d.get('kaart-naam') else ''
        knop = (f'<a class="btn btn-primary ut-voet__knop" href="{d["route-url"]}" target="_blank" rel="noopener">{d["knop-route"]}'
                f'<span class="al-vh"> {d["l-nieuw-tabblad"]}</span></a>') if d.get('route-url') else ''
        regel = f'<p>{d["kaart-regel"]}</p>' if d.get('kaart-regel') else ''
        t = lambda k: escape(d[k], quote=True)
        blok['UT_KAART'] = (
            f'<section data-component="ut-kaart" class="al-sec ut-kaart"><div class="al-wrap"><div class="al-paneel ut-kaart__paneel">'
            f'<div class="ut-kaart__kop"><h2>{d["kaart-kop"]}</h2>{regel}</div><div class="ut-kaart__veld">'
            f'<div class="ut-kaart__beeld" data-kaart data-geo="content/kaart/getekend.json" data-punten="#ut-kaart-punten" data-vignet="{d["kaart-vignet"]}" '
            f'data-t-in="{t("kaart-knop-inzoomen")}" data-t-uit="{t("kaart-knop-uitzoomen")}" data-t-alles="{t("kaart-knop-alles")}" '
            f'data-t-wiel="{t("kaart-hint-wiel")}" data-t-vingers="{t("kaart-hint-vingers")}" data-t-attributie="{t("kaart-attributie")}">'
            f'<img class="ut-kaart__grond" src="{d["kaart-foto-klein"]}" srcset="{d["kaart-foto-klein"]} 720w, {d["kaart-foto"]} 1200w" sizes="(max-width:767px) 100vw, 1060px" '
            f'alt="{d["kaart-alt"]}" width="1200" height="675" loading="lazy" decoding="async"></div>'
            f'<div class="ut-voet"><span class="ut-voet__ic" aria-hidden="true">{UT_SPELD}</span><div class="ut-voet__tk">{naam}{meta}</div>{knop}</div>'
            '</div></div></div>'
            '<script type="application/json" id="ut-kaart-punten">' + json.dumps(kaart, ensure_ascii=False).replace('</', '<\\/') + '</script></section>')
    else:
        blok['UT_KAART'] = ''

    # 8 FAQ + FAQPage (tekst = zichtbare tekst zonder tags)
    faq_slots = al_lijst(d, 'f', '-v')
    slot_compleet('f', faq_slots, (), ('-v', '-a'))
    items, ld = [], []
    for j, i in enumerate([i for i in faq_slots if d.get(f'f{i}-v')][:6]):
        vr, an = d[f'f{i}-v'], d[f'f{i}-a']
        items.append(f'<details class="as-accordeon__item"{" open" if j == 0 else ""}><summary class="as-accordeon__kop"><h3>{vr}</h3></summary>'
                     f'<div class="as-accordeon__paneel"><p>{an}</p></div></details>')
        ld.append({'@type': 'Question', 'name': plat(vr), 'acceptedAnswer': {'@type': 'Answer', 'text': plat(an)}})
    if not items:
        sys.exit('uitje: minstens een FAQ-vraag (f1-v + f1-a) nodig')
    blok['UT_FAQ'] = ''.join(items)
    blok['UT_FAQ_LD'] = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': ld}, ensure_ascii=False).replace('</', '<\\/')
    blok['UT_FAQ_LD'] += ut_hreflang(config)

    # fotocredit voor de hele pagina (voor het slot)
    blok['UT_FOTOCREDIT'] = f'<div class="al-wrap ut-fotocredit-rij"><p class="ut-fotocredit">{d["fotocredit"]}</p></div>' if d.get('fotocredit') else ''

    # pop-upinhoud inline: uitjes (meer-kaarten, kaartknoppen) + kamers (telefoonvariant van de kamer-pop-up)
    blok['UT_POPDATA'] = ('<script type="application/json" id="ut-popdata">'
                          + json.dumps({'uitje': pop_uitje, 'kamer': popkamer}, ensure_ascii=False).replace('</', '<\\/') + '</script>')

    blok['AL_KOP'], blok['AL_VOET'] = al_kop_voet(d, d['mews-basis'], taal=lang)
    # kamerlinks in de spiegelvoet (zonder actiecode) krijgen ook de Mews-taal, net als de rest van de pagina
    blok['AL_KOP'], blok['AL_VOET'] = (x.replace('af1d00ffc556?mewsRoom=', f'af1d00ffc556?language={taal}&amp;mewsRoom=') for x in (blok['AL_KOP'], blok['AL_VOET']))

    for k, v in blok.items():
        if f'<!-- {k} -->' not in html:
            sys.exit(f'uitje: plek <!-- {k} --> niet in het sjabloon')
        html = html.replace(f'<!-- {k} -->', v)
    for k, v in d.items():
        if isinstance(v, str) and not k.startswith('_'):
            html = html.replace('{{' + k + '}}', v)
    open_velden = sorted(set(re.findall(r'\{\{[^}]+\}\}', html)))
    if open_velden:
        sys.exit(f'uitje: open velden in {output_file}: {open_velden}')
    if fouten:
        sys.exit('uitje:\n  ' + '\n  '.join(fouten))
    if '—' in html:
        sys.exit('uitje: em-dash in de uitvoer')
    with open(os.path.join(base, output_file), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  [{template_name}/{lang}] → {output_file}  ({len(html)} chars)')


def build(template_name, lang):
    config = TEMPLATES[template_name]
    output_file, json_file = config['langs'][lang]
    if config.get('adslander'):
        return build_adslander(config, output_file, json_file, template_name, lang)
    if config.get('uitje'):
        # volledige build (geen template als argument): een uitje-taal zonder JSON overslaan i.p.v. stoppen
        if not os.path.exists(os.path.join(base, json_file)) and not any(a in TEMPLATES for a in sys.argv[1:]):
            print(f'  [{template_name}/{lang}] overgeslagen: {json_file} bestaat nog niet')
            return
        return build_uitje(config, output_file, json_file, template_name, lang)
    if config.get('omgeving'): return build_omgeving(config, output_file, json_file, template_name, lang)

    template_path = os.path.join(base, config['template'])
    json_path     = os.path.join(base, json_file)
    output_path   = os.path.join(base, output_file)

    with open(template_path, encoding='utf-8') as f:
        html = f.read()

    with open(json_path, encoding='utf-8') as f:
        translations = json.load(f)

    # Arrangementenoverzicht: lander-w1-blokken en kaarten invoegen vóór de blokken- en {{KEY}}-pass
    if config.get('overzicht'):
        html = apply_overzicht(html, translations)

    # Optioneel upgradeblok (ladder) staat aan zodra de JSON een UPGRADE_LADDER heeft (geen tekst-key)
    ladder = translations.pop('UPGRADE_LADDER', None)
    # Optioneel cadeaublok (cadeau) staat aan zodra de JSON CADEAU_ITEMS heeft (lijst; CADEAU_VOET hoort erbij)
    cadeau = translations.pop('CADEAU_ITEMS', None)
    cadeau_voet = translations.pop('CADEAU_VOET', '') if cadeau else None
    # Ster-split (blok 3a): iconen van punt 2, 3 en 5 zijn per JSON te kiezen (standaard sleutel, label, kalender);
    # de knop onder het blok volgt ATTENTIE_KNOP (ontbreekt = tekst van CTA, leeg = geen knop).
    for k, v in ATTENTIE_ICOON_STANDAARD.items():
        translations.setdefault(k, v)
    translations.setdefault('ATTENTIE_KNOP', translations.get('CTA', ''))
    # Gesloten lander: logo linkt naar de pagina zelf (standaard /hotel-venray-v2)
    translations.setdefault('GESLOTEN_LOGO_URL', '/hotel-venray-v2')
    # Optionele herovideo (blok 'video'): aan zodra de JSON HERO_VIDEO heeft; HERO_VIDEO_MOBIEL (staand, < 720 px) en
    # HERO_VIDEO_POSTER vallen terug op HERO_VIDEO en HERO_IMG. Bij prefers-reduced-motion toont lander-w1.css alleen HERO_IMG.
    if translations.get('HERO_VIDEO'):
        translations.setdefault('HERO_VIDEO_MOBIEL', translations['HERO_VIDEO'])
        translations.setdefault('HERO_VIDEO_POSTER', translations.get('HERO_IMG', ''))
    # Trustkaart (blok 'trustkaart'): KAART_IMG staat leeg in de JSON = boekkaart (telefoon onder de hero, zijkaart) zonder scorevak,
    # foto, pil en titel; de kaart begint met de vinkjes (alleen de varianten zonder blok arrangement).
    # Scratchcard-pop-up (blok 'scratchcard', '_popup_scratchcard': true in de JSON): kras & win in stijlvariant 2026
    # (scratchcard-2026.css), aanmelding via nieuwsbrief.js -> /api/nieuwsbrief (Klaviyo), D1-events via analytics-d1.js.
    # Los van popup-ab.js (sitebreed uit met POPUP_UIT); geen A/B.
    # Gesloten lander (blok 'gesloten', GESLOTEN_LANDER: true in de JSON): geen links naar asteria.nl zolang de nieuwe
    # asteria.nl niet live is. Kop alleen logo + telefoon + Boek nu, voet alleen logo/adres/contact/juridisch, pop-upknop =
    # Bekijk beschikbaarheid (Mews), geen Alle faciliteiten/Ontdek de omgeving/Alle arrangementen/Neem contact op/Bekijk alle
    # kamers; kamerknoppen 'Bekijk beschikbaarheid' (Mews + data-room), geen link naar de kamerpagina's (oude stijl).
    # Overzichtsknoppen in de nieuwe stijl: OVERZICHT_ARR_URL (Alle arrangementen) en OVERZICHT_KAMERS_URL (Bekijk alle kamers). Volledig menu terug = schakelaar op false.
    # Spiegelstand (GESLOTEN_LANDER: "spiegel"): inhoud als de gesloten lander (blok 'gesloten': kamerknoppen en pop-upknop
    # = Bekijk beschikbaarheid), maar kop en voet volledig zoals de staging (blok 'spiegel' i.p.v. 'kopdicht') met alle menu- en
    # voetlinks naar de spiegel van de staging op visit.asteria.nl. Links staan in het sjabloon als href="spiegel:<sleutel>"
    # en komen uit translations/spiegel-links.json (vul_spiegel_links); met één wijziging daar later naar de echte asteria.nl.
    # Plus Alle faciliteiten / Ontdek de omgeving / Neem contact op naar de spiegel en Meer informatie in de faciliteit-pop-up.
    gesloten_stand = translations.get('GESLOTEN_LANDER')
    if gesloten_stand not in (None, True, False, 'spiegel'):
        sys.exit(f'GESLOTEN_LANDER moet true, false of "spiegel" zijn, niet {gesloten_stand!r}')
    aan = ({'gesloten', 'kopdicht'} if gesloten_stand is True else {'gesloten', 'spiegel'} if gesloten_stand == 'spiegel' else set()) | ({'scratchcard'} if translations.get('_popup_scratchcard') else set()) | ({'trustkaart'} if translations.get('KAART_IMG', None) == '' else set()) | ({'video'} if translations.get('HERO_VIDEO') else set()) | ({k for k, v in config.get('blokken', {}).items() if v} | ({'ladder'} if ladder else set())
           | ({'cadeau'} if cadeau else set()) | ({'attentie-knop'} if translations['ATTENTIE_KNOP'] else set()))

    # Staging-boekkaart op de telefoon (blok 'boekkaart'): op de algemene lander (blok 'hotel') vervangt hij de boekkaart onder de hero
    if 'hotel' in aan:
        aan.add('boekkaart')

    if 'arrangement' in aan:
        # arrangementblokken aan/uit per arrangement in de JSON
        if translations.get('ZV_TOON'): aan.add('zondag')
        if translations.get('WAAROM_TOON', True): aan.add('waarom')
        if translations.get('ANDERE_TOON') and translations.get('_andere'): aan.add('andere')
        if translations.get('_banen'): aan.add('banen')

    # Kamerdetailpagina (kamer-w1): kop/voet uit lander-w1 + lijstblokken, vóór de blokken en de {{KEY}}-pass
    if config.get('kamer'):
        html = render_kamer(html, translations)

    # Variantblokken (bijv. zijkaart, ladder, cadeau, arrangement) vóór de {{KEY}}-pass
    html = apply_blokken(html, aan)
    if ladder:
        html = html.replace('<!-- UPGRADE_LADDER -->', render_ladder(ladder))
    if cadeau:
        html = html.replace('<!-- CADEAU_ITEMS -->', render_cadeau(cadeau, cadeau_voet))

    if 'hotel' in aan:
        html = render_hotel(html, translations, 'gesloten' in aan, 'spiegel' in aan)
    if 'kamertypes' in aan:
        html = render_kamertypes(html, translations)

    for key, value in translations.items():
        if isinstance(value, str) and not key.startswith('_'):
            html = html.replace('{{' + key + '}}', value)

    # Lege zondagregel in de zijkaart (ZV_KAART_REGEL = "") laat geen leeg streepje achter
    html = html.replace('<p class="ar-zondagregel"></p>', '')

    # Arrangement: kamers + pillen uit '_kamers' (alleen met blok 'arrangement')
    if 'arrangement' in aan:
        html = apply_arrangement(html, translations)

    # Letterlijke (hardcoded) NL-strings vertalen, in lijstvolgorde: langste/
    # meest specifieke strings staan vooraan zodat substrings niet half raken.
    literals_file = config.get('literals', {}).get(lang)
    if literals_file:
        with open(os.path.join(base, literals_file), encoding='utf-8') as f:
            for source, target in json.load(f):
                html = html.replace(source, target)

    # Reviewmuur uit de Google-reviews-JSON (alleen templates met 'reviews')
    if config.get('reviews'):
        if 'arrangement' in aan or config.get('overzicht'):
            n = translations.get('_reviews_aantal', 12)
            if n not in (8, 12):
                sys.exit(f'_reviews_aantal moet 8 of 12 zijn, niet {n!r}')
            html = inject_reviews(html, config['reviews'], max_kaarten=n, voorkeur=translations.get('_reviews_voorkeur'))
        elif 'kamertypes' in aan:
            html = inject_reviews(html, config['reviews'], voorkeur=translations.get('_reviews_voorkeur'))
        else:
            html = inject_reviews(html, config['reviews'])

    # Gesloten lander: kamerknoppen heten 'Bekijk beschikbaarheid' (Mews met de kamer voorgeselecteerd via data-room);
    # geen link naar de kamerpagina's (oude stijl), de kamerinformatie staat in de pop-up.
    if 'gesloten' in aan:
        html = re.sub(r'(aria-label="Boek de [^"]*">)Boek nu(</a>)', r'\1Bekijk beschikbaarheid\2', html)
        # lege OVERZICHT_*_URL = geen overzichtsknop (later met één regel terug)
        html = html.replace('<a class="btn btn-secondary" href="">Bekijk alle kamers</a>', '')
        html = html.replace('<a class="btn btn-secondary" href="">' + translations.get('AANBOD_KNOP', '') + '</a>', '')
        if 'kamertypes' not in aan and not config.get('kamer'):   # kamertypes-v2 en kamerpagina's: 'Boek deze kamer' blijft (staging)
            html = html.replace('>Boek deze kamer</a>', '>Bekijk beschikbaarheid</a>')

    if 'spiegel' in aan:
        if not config.get('kamer'):
            html = kamerkaart_links(html)
        html = vul_spiegel_links(html)

    if config.get('kamer'):
        html = kamer_absoluut(html)

    # Zonder actiecode: lege voucher uit de Mews-links en labels
    if translations.get('VOUCHER', None) == '':
        html = zonder_voucher(html)

    # Eigen Mews-boekingsmodule (optioneel JSON-veld MEWS_CONFIG, bijv. winterarrangement = Winter-actie 95c70e27):
    # alle distributor-links op deze pagina naar die config, en data-mews-config op <html> zodat lander-w1.js en
    # arrangement-kalender.js de widget/deeplinks met die config openen. Zonder het veld: niets verandert.
    mews_cfg = translations.get('MEWS_CONFIG')
    if mews_cfg:
        if not re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', mews_cfg):
            sys.exit(f'MEWS_CONFIG is geen Mews-config-id: {mews_cfg!r}')
        html = html.replace('distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556', 'distributor/' + mews_cfg)
        html, n = re.subn(r'<html( [^>]*)?>', lambda m: m.group(0)[:-1] + f' data-mews-config="{mews_cfg}">', html, count=1)
        if not n or '6dc9094c' in html:
            sys.exit(f'MEWS_CONFIG: niet volledig doorgevoerd in {output_file}')

    # Mews-boekingslinks in de juiste taal openen (alleen EN/DE)
    html = add_mews_language(html, lang)

    # Kamer-media in ROOMS gelijk aan de detailpagina's (video + volledige fotoset)
    html = fix_room_media(html)

    # Oude pagina's (-oud) niet indexeren: robots-meta direct na de charset-regel
    if lang in config.get('noindex', ()) and 'name="robots"' not in html:
        html = re.sub(r'(<meta charset="[^"]*">)', r'\1\n  <meta name="robots" content="noindex, follow">', html, count=1)
        if 'name="robots"' not in html:
            sys.exit(f'noindex: geen <meta charset> in {output_file}')
    # Wel indexeren (bijv. winterarrangement): de noindex-meta uit het sjabloon wordt index, follow
    if lang in config.get('index', ()):
        html, n = re.subn(r'<meta name="robots" content="noindex, follow">', '<meta name="robots" content="index, follow">', html)
        if n != 1:
            sys.exit(f'index: robots-meta niet precies een keer gevonden in {output_file}')

    # Sanity check: no unreplaced markers
    remaining = re.findall(r'\{\{[A-Z_0-9]+\}\}', html)
    if remaining:
        print(f'  WARNING [{template_name}/{lang}]: unreplaced markers: {remaining}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  [{template_name}/{lang}] → {output_file}  ({len(html)} chars)')

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# Omgevingspagina's (nov 2026): overzicht /omgeving-v2 (omgeving.template.html) en vijf categoriepagina's
# /omgeving-<cat>-v2 (omgeving-categorie.template.html), nabouw van parkhotelhorst.nl/gebied/ en /gebieden/<cat>/.
# Gegevens: translations/omgeving-labels-<taal>.json (vaste labels, eerst geladen) + translations/omgeving-<pagina>-<taal>.json
# (wint). De kaarten komen bij ELKE build uit om_register(taal): alle uitje-/route-/zoek-JSON's die er op dat moment zijn,
# dus een nieuw uitje verschijnt vanzelf. Velden via de aliaslijst OM_ALIAS hieronder (uitbreiden = naam erbij zetten).
# Categorie: veld 'categorie' -> content/omgeving-categorie.json -> OM_HEROCAT -> alleen overzicht + waarschuwing.
# Stopt bij een open veld, ontbrekend fotobestand of een em-dash. Zie ook CLAUDE.md (Omgevingspagina's).
# ═══════════════════════════════════════════════════════════════════════════════════════════════

OM_CATS = ['golf', 'natuur', 'cultuur', 'dagje-uit', 'shoppen-steden']   # volgorde filterbalk en tegels (zoals Parkhotel)
OM_MODES = ['auto', 'lopen', 'fiets']
OM_BRONNEN = [('uitje', 'uitje-'), ('route', 'route-'), ('zoek', 'zoek-')]   # soort, voorvoegsel van het bestand
# aliaslijst: eerste gevulde veld wint. naam/regel zonder HTML-tags; plaats zie om_plaats; adres = pad uit canonical.
OM_ALIAS = {
    'naam': ['kaart-titel', 'kruimel', 'hero-kop'],
    'foto': ['kaart-foto-uitje', 'hero-foto-klein', 'hero-foto', 'hero-poster-bureaublad-klein', 'hero-poster-bureaublad'],
    'alt': ['kaart-foto-alt', 'hero-alt'],
    'regel': ['kaart-regel-kort', 'hero-sub'],
    'auto': ['vk-auto'], 'fiets': ['vk-fiets'], 'lopen': ['vk-lopen'],
    'adres': ['canonical'],
    'categorie': ['categorie'],
}
# hero-cat (kleine letters) -> categorie, als laatste terugval
OM_HEROCAT = {'natuur': 'natuur', 'museum': 'cultuur', 'cultuur': 'cultuur', 'dagje uit': 'dagje-uit', 'pretpark': 'dagje-uit',
              'winkelen en terrassen': 'shoppen-steden', 'stad aan de maas': 'shoppen-steden', 'winkelen': 'shoppen-steden',
              'golf': 'golf', 'golfbaan': 'golf'}
# adres zonder canonical en zonder TEMPLATES-entry (bijv. de routepagina's in een proefbouw)
OM_ADRES_TERUGVAL = {'route-wandelen': '/wandelen-rond-venray-v2', 'route-fietsen': '/fietsen-rond-venray-v2'}
OM_ROUTE_VOLGORDE = ['wandelen', 'fietsen']
OM_CAT_ICO = {
    'golf': '<path d="M9 19V3l8 3.5-8 3.5"/><ellipse cx="12" cy="19" rx="9" ry="2"/>',
    'natuur': '<path d="M5 19C5 10 10.5 5 20 4c0 9.5-5.5 15-14 15z"/><path d="M5 19l9-9"/>',
    'cultuur': '<path d="M12 3l9 4.5H3z"/><path d="M4 10h16M4 18h16M3 21h18"/><path d="M6.5 10v8M10.5 10v8M13.5 10v8M17.5 10v8"/>',
    'dagje-uit': '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M15 7v2M15 11.5v1M15 15v2"/>',
    'shoppen-steden': '<path d="M5 8h14l-1.2 13H6.2z"/><path d="M9 10V7a3 3 0 0 1 6 0v3"/>',
}
OM_VINK = ('<svg class="om-vinkje" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.2l2.6 2.6L16 9.5"/></svg>')
OM_PIJL_L = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>')
OM_PIJL_R = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>')
OM_CHIP = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
           'aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M8.5 12.2l2.3 2.3 4.7-4.9"/></svg>')
OM_HASH = {}   # gevuld in omgeving.js; hier alleen voor de documentatie


def om_svgcls(svg, cls):
    return svg.replace('<svg ', f'<svg class="{cls}" ', 1)


def om_plat(t):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t or '').replace('&amp;', '&')).strip()


def om_eerste(d, sleutel):
    for k in OM_ALIAS[sleutel]:
        if isinstance(d.get(k), str) and d[k].strip():
            return d[k].strip()
    return ''


def om_minuten(t):
    """'11 min' -> 11, '1 u 10 min' -> 70, 'ca. 15 minuten rijden' -> 15, leeg/onbekend -> None."""
    t = (t or '').lower()
    if not t.strip():
        return None
    u = re.search(r'(\d+)\s*(?:u\b|uur)', t)
    m = re.search(r'(\d+)\s*min', t)
    if not u and not m:
        return None
    return (int(u.group(1)) * 60 if u else 0) + (int(m.group(1)) if m else 0)


def om_plaats(d):
    """Plaats: veld 'plaats' -> stad achter de postcode in kaart-naam -> t1-waarde voor de komma."""
    if d.get('plaats'):
        return d['plaats']
    m = re.search(r'\b\d{4}\s?[A-Z]{2}\s+([^,]+)$', d.get('kaart-naam') or '')
    if m:
        return m.group(1).strip()
    return (d.get('t1-waarde') or '').split(',')[0].strip()


def om_adressen():
    """json-pad -> '/<uitvoer zonder .html>' over alle TEMPLATES (zo vinden pagina's zonder canonical hun adres)."""
    uit = {}
    for cfg in TEMPLATES.values():
        for html_, js in cfg['langs'].values():
            uit[js] = '/' + html_[:-5] if html_.endswith('.html') else '/' + html_
    return uit


def om_register(taal):
    """Alle kaarten die er nu zijn, als lijst dicts (soort, slug, naam, plaats, auto/fiets/lopen, foto, alt, url, regel,
    categorie, taal, bron). Een taal zonder eigen bestand valt terug op NL (kaart linkt dan naar de NL-pagina).
    Gesorteerd op autominuten (onbekend achteraan), daarna naam."""
    import glob
    with open(os.path.join(base, 'content', 'omgeving-categorie.json'), encoding='utf-8') as f:
        tabel = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
    adressen = om_adressen()
    items = []
    for soort, voor in OM_BRONNEN:
        def lees(t):
            uit = {}
            for pad in sorted(glob.glob(os.path.join(base, 'translations', f'{voor}*-{t}.json'))):
                slug = os.path.basename(pad)[len(voor):-len(f'-{t}.json')]
                if slug == 'labels' or slug.startswith('labels'):
                    continue
                with open(pad, encoding='utf-8') as f:
                    uit[slug] = (os.path.relpath(pad, base), json.load(f))
            return uit
        eigen = lees(taal)
        nl = lees('nl') if taal != 'nl' else {}
        # NL-terugval alleen voor plekken die de taal niet zelf heeft (ook niet onder een andere slug, via hreflang.nl)
        gedekt = {str((d.get('hreflang') or {}).get('nl', '')).rstrip('/') for _, d in eigen.values()}
        bronnen = [(s, p, d, taal) for s, (p, d) in eigen.items()]
        for s, (p, d) in nl.items():
            if s in eigen or (d.get('canonical') or '').rstrip('/') in gedekt:
                continue
            bronnen.append((s, p, d, 'nl'))
        for slug, pad, d, t in bronnen:
            naam = om_plat(om_eerste(d, 'naam'))
            adres = om_eerste(d, 'adres')
            if adres:
                adres = '/' + urllib.parse.urlparse(adres).path.lstrip('/')
            else:
                adres = adressen.get(pad) or OM_ADRES_TERUGVAL.get(f'{voor}{slug}', '')
            if not naam or not adres:
                print(f'  WAARSCHUWING omgeving: {pad} overgeslagen (geen naam of adres)')
                continue
            cat = om_eerste(d, 'categorie') or tabel.get(slug) or OM_HEROCAT.get(om_plat(d.get('hero-cat', '')).lower(), '')
            if cat and cat not in OM_CATS:
                print(f'  WAARSCHUWING omgeving: {pad} heeft onbekende categorie {cat!r}')
                cat = ''
            if not cat:
                print(f'  WAARSCHUWING omgeving: {pad} heeft geen categorie; kaart alleen op het overzicht')
            items.append({'soort': soort, 'slug': slug, 'naam': naam, 'plaats': om_plaats(d),
                          'auto': om_minuten(d.get('vk-auto')), 'fiets': om_minuten(d.get('vk-fiets')),
                          'lopen': om_minuten(d.get('vk-lopen')), 'foto': om_eerste(d, 'foto'), 'alt': om_plat(om_eerste(d, 'alt')),
                          'url': adres, 'regel': om_plat(om_eerste(d, 'regel')), 'categorie': cat, 'taal': t, 'bron': pad})
    items.sort(key=lambda x: (x['auto'] is None, x['auto'] or 0, x['naam'].lower()))
    return items


def om_banen(register):
    """Golfbanen: golf-uitjes uit het register, anders _banen uit translations/golfarrangement-nl.json."""
    eigen = [x for x in register if x['categorie'] == 'golf' and x['soort'] != 'route']
    if eigen:
        return [dict(x, tekst=x['regel'], site='', rijtijd='', pos='50% 50%') for x in eigen]
    with open(os.path.join(base, 'translations', 'golfarrangement-nl.json'), encoding='utf-8') as f:
        banen = json.load(f).get('_banen') or []
    uit = []
    for b in banen:
        uit.append({'soort': 'baan', 'slug': re.sub(r'[^a-z0-9]+', '-', b['naam'].lower()).strip('-'), 'naam': b['naam'],
                    'plaats': b.get('plaats', ''), 'auto': om_minuten(b.get('rijtijd')), 'fiets': None, 'lopen': None,
                    'foto': b['foto'], 'alt': b.get('alt', ''), 'url': '', 'site': b.get('url', ''), 'tekst': b.get('tekst', ''),
                    'rijtijd': b.get('rijtijd', ''), 'pos': b.get('pos', '50% 50%'), 'categorie': 'golf', 'regel': '', 'taal': 'nl',
                    'bron': 'translations/golfarrangement-nl.json'})
    uit.sort(key=lambda x: (x['auto'] is None, x['auto'] or 0, x['naam'].lower()))
    return uit


def om_kaart(x, L, golf_url=''):
    """Een uitjekaart (overzicht en categoriepagina): foto 10:7, categorie, naam, plaats, reistijdvakjes, knop."""
    from html import escape
    cls = ['om-kaart'] + ([f'cat-{x["categorie"]}'] if x['categorie'] else []) + [f'mode-{m}' for m in OM_MODES if x.get(m)]
    vk = ''.join(f'<li class="om-vk"><span class="om-vk__ib">{om_svgcls(UT_VK[m], "om-vk__ico")}</span>'
                 f'<span class="om-vk__t"><strong>{x[m]} {L.get("l-min", "min")}</strong><span>{L["l-" + m]}</span></span></li>'
                 for m in ('auto', 'fiets', 'lopen') if x.get(m))
    cat = L.get(f'cat-{x["categorie"]}-naam', '') if x['categorie'] else ''
    url = x['url'] or golf_url
    plaats = f'<p class="om-kaart__plaats">{escape(x["plaats"], quote=False)}</p>' if x.get('plaats') else ''
    return (f'<article class="{" ".join(cls)}"><a class="om-kaart__media" href="{url}" tabindex="-1" aria-hidden="true">'
            f'<img src="{x["foto"]}" alt="" width="700" height="490" loading="lazy" decoding="async"></a>'
            f'<div class="om-kaart__body">' + (f'<p class="om-kaart__cat">{cat}</p>' if cat else '') +
            f'<h3 class="om-kaart__naam">{escape(x["naam"], quote=False)}</h3>{plaats}'
            + (f'<ul class="om-kaart__vakjes">{vk}</ul>' if vk else '') +
            f'<a class="btn btn-secondary om-kaart__knop" href="{url}" aria-label="{L["knop-meer-info"]}: {escape(x["naam"])}">{L["knop-meer-info"]}</a></div></article>')


def om_kop_voet(d, mews_basis, taal):
    """Spiegelkop/-voet: al_kop_voet voor nl/de; en = al_kop_voet(nl) + de paren uit _kop_voet in omgeving-labels-en.json.
    Daarna krijgen de kamerlinks zonder actiecode ook de Mews-taal (zoals build_uitje)."""
    if taal in ('nl', 'de'):
        kop, voet = al_kop_voet(d, mews_basis, taal=taal)
    else:
        kop, voet = al_kop_voet(dict(d, **{'mews-taal': d.get('mews-taal', 'en-GB')}), mews_basis, taal='nl')
        paren = d.get('_kop_voet') or []
        if not paren:
            sys.exit(f'omgeving: _kop_voet (Engelse kop/voet-labels) ontbreekt in {OM_LABELS_PAD.format(taal=taal)}')
        for a_, b_ in paren:
            kop, voet = kop.replace(a_, b_), voet.replace(a_, b_)
    mt = d.get('mews-taal', 'nl-NL')
    return tuple(x.replace('af1d00ffc556?mewsRoom=', f'af1d00ffc556?language={mt}&amp;mewsRoom=') for x in (kop, voet))


OM_LABELS_PAD = 'translations/omgeving-labels-{taal}.json'


def om_arr_url(slug, nl_url, taal):
    """Adres van een arrangementpagina in de paginataal: een TEMPLATES-uitvoer <slug>-<taal>.html die bestaat en niet de oude
    Mews-config bee2f902 gebruikt; anders de NL-pagina."""
    if taal == 'nl':
        return nl_url
    naam = f'{slug}-{taal}.html'
    for cfg in TEMPLATES.values():
        uit = (cfg['langs'].get(taal) or ('',))[0]
        if uit == naam and os.path.exists(os.path.join(base, naam)):
            with open(os.path.join(base, naam), encoding='utf-8') as f:
                if 'bee2f902' not in f.read():
                    return '/' + naam[:-5]
    return nl_url


def build_omgeving(config, output_file, json_file, template_name, lang):
    from html import escape
    if not os.path.exists(os.path.join(base, json_file)):
        if expliciet and (lang == 'nl' or lang in langs_filter):
            sys.exit(f'omgeving: {json_file} bestaat niet (nodig voor {template_name}/{lang})')
        print(f'  [{template_name}/{lang}] overgeslagen: {json_file} bestaat nog niet')
        return
    pagina = config['omgeving']
    labels_pad = OM_LABELS_PAD.format(taal=lang)
    if not os.path.exists(os.path.join(base, labels_pad)):
        sys.exit(f'omgeving: {labels_pad} ontbreekt')
    with open(os.path.join(base, config['template']), encoding='utf-8') as f:
        html = f.read()
    with open(os.path.join(base, labels_pad), encoding='utf-8') as f:
        d = json.load(f)
    L = dict(d)   # alleen labels (voor de kaarten)
    with open(os.path.join(base, json_file), encoding='utf-8') as f:
        d.update(json.load(f))
    kamers_pad = f'content/uitje-kamers-{lang}.json' if os.path.exists(os.path.join(base, f'content/uitje-kamers-{lang}.json')) else UT_KAMERS
    with open(os.path.join(base, kamers_pad), encoding='utf-8') as f:
        kamerbron = json.load(f)['kamer']
    taal = d.get('mews-taal', 'nl-NL')
    mews = lambda extra='': f'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?language={taal}{extra}'
    d['mews-basis'] = mews()
    d.setdefault('hero-foto-klein', d.get('hero-foto', ''))
    d.setdefault('slot-foto-klein', d.get('slot-foto', ''))
    d.setdefault('og-image', 'https://visit.asteria.nl/' + d.get('hero-foto', ''))
    d.setdefault('categorie', pagina)
    d['overzicht-url'] = L['url-overzicht']
    fouten = []

    def bestaat(pad):
        if pad and not pad.startswith('http') and not os.path.exists(os.path.join(base, pad)):
            fouten.append('bestand ontbreekt: ' + pad)
        return pad

    for k in ('hero-foto', 'hero-foto-klein', 'slot-foto', 'slot-foto-klein'):
        bestaat(d.get(k))

    register = om_register(lang)
    banen = om_banen(register)
    golf_url = L['url-golf']
    # wat per categorie op de categoriepagina staat (routes wel, golf = banen)
    per_cat = {c: [x for x in register if x['categorie'] == c] for c in OM_CATS}
    per_cat['golf'] = banen
    for x in register + banen:
        bestaat(x['foto'])
    blok, kop_extra = {}, ''
    woord = lambda n, c: L['woord-baan' if n == 1 else 'woord-banen'] if c == 'golf' else L['woord-uitje' if n == 1 else 'woord-uitjes']

    # --- de dag in vier momenten (uitje.css/uitje.js), foto met label; categorie = spiegelbeeld, moment 2 open
    m = [i for i in al_lijst(d, 'm', '-naam') if d[f'm{i}-naam']][:4]
    if len(m) != 4 or not d.get('dag-kop'):
        sys.exit(f'omgeving: {json_file} heeft dag-kop en precies vier momenten (m1..m4) nodig')
    beelden = ''.join(f'<figure class="ut-dag__beeld{" is-aan" if j == 0 else ""}" data-beeld="{i}"><img src="{bestaat(d.get(f"m{i}-foto-klein") or d[f"m{i}-foto"])}" '
                      f'alt="{d[f"m{i}-alt"]}" width="800" height="1000" loading="lazy" decoding="async" style="object-position:{d.get(f"m{i}-positie", "50% 50%")}">'
                      f'<span class="om-dag__tag">{d[f"m{i}-deel"]}</span></figure>' for j, i in enumerate(m))
    for i in m:
        bestaat(d[f'm{i}-foto'])
    momenten = ''.join(f'<li class="ut-moment{" is-aan" if j == 0 else ""}" data-moment="{i}"><h3 class="ut-moment__kop"><button type="button" class="ut-moment__kies" '
                       f'aria-expanded="{"true" if j == 0 else "false"}" aria-controls="om-moment-{i}-open"><span class="ut-moment__deel">{d[f"m{i}-deel"]}</span>'
                       f'<span class="ut-moment__naam">{d[f"m{i}-naam"]}</span></button></h3><div class="ut-moment__open" id="om-moment-{i}-open"><div>'
                       f'<p class="ut-moment__tekst">{d[f"m{i}-tekst"]}</p></div></div></li>' for j, i in enumerate(m))
    # categorie: spiegelbeeld van het arrangementblok erboven (daar foto links), dus hier paneel links en foto rechts; moment 2 open
    start = d.get('dag-start', '1' if pagina == 'overzicht' else '2')
    blok['OM_DAG'] = (f'<section data-component="om-dag" class="al-sec ut-dag om-dag" data-start="{start}"><div class="al-wrap">'
                      f'<div class="ut-dag__blok"><div class="ut-dag__bg" aria-hidden="true"></div><div class="ut-dag__foto">{beelden}</div>'
                      f'<div class="ut-dag__inner"><h2>{d["dag-kop"]}</h2><p class="ut-dag__sub">{d["dag-sub"]}</p><ol class="ut-dag__lijst" aria-label="{L["dag-lijst-label"]}">{momenten}</ol>'
                      f'<a class="btn btn-primary al-btn mews-open om-dag__knop" href="{mews()}">{L["knop-boek"]}</a></div></div></div></section>')

    # --- kamers (overzicht altijd; categorie bij conversie 'kamers'): kamerslider van het uitje-sjabloon, zonder prijs
    conversie = 'kamers' if pagina == 'overzicht' else d.get('conversie', 'kamers')
    if conversie not in ('kamers', 'arr'):
        sys.exit(f'omgeving: conversie moet "kamers" of "arr" zijn, niet {conversie!r}')
    popkamer, kalenders = {}, []
    kamer_html = ''
    if conversie == 'kamers':
        kk, kamerdata = [], {}
        for k in d.get('kamers') or []:
            if k not in KAMER_MEWS or k not in kamerbron:
                sys.exit(f'omgeving: kamer {k!r} heeft geen Mews-id of geen kamerdata ({kamers_pad})')
            r, room = kamerbron[k], KAMER_MEWS[k]
            if r.get('kamer') != room:
                sys.exit(f'omgeving: Mews-id van {k} in {kamers_pad} wijkt af van KAMER_MEWS')
            for x in r['fotos'] + r.get('pop_fotos', []) + [r.get('video') or '', r['kaart_foto']]:
                bestaat(x)
            kenm = ''.join(f'<li>{icoon(AL_KAMER_IC[ic])}<span>{escape(t, quote=False)}</span></li>' for ic, t in r['kaart'])
            naam = escape(r['naam'], quote=False)
            kk.append(
                f'<article class="kk-kaart" data-kamerkaart="{k}"><a class="kk-foto" href="#kamers" data-kamer="{k}" aria-haspopup="dialog" tabindex="-1" aria-hidden="true"><img src="{r["kaart_foto"]}" width="1400" height="934" alt="" loading="lazy" decoding="async"></a>'
                f'<div class="kk-inhoud"><h3 class="kk-naam">{naam}</h3><p class="kk-tekst">{escape(r["kort"], quote=False)}</p>'
                f'<ul class="kk-kenmerken">{kenm}</ul>'
                f'<p class="kk-knoppen"><a class="btn btn-primary mews-open" href="{mews("&amp;mewsRoom=" + room + "&amp;mewsRoute=rooms")}" data-room="{room}">{d["knop-kamer"]}</a>'
                f'<a class="btn btn-secondary" href="#kamers" data-kamer="{k}" aria-haspopup="dialog" aria-label="{d["knop-info"]}: {naam}">{d["knop-info"]}</a></p></div></article>')
            kamerdata[k] = {x: r[x] for x in ('naam', 'video', 'fotos', 'tekst', 'kenmerken', 'kamer')}
            popkamer[k] = {x: r[x] for x in ('naam', 'desc', 'pop_fotos', 'video', 'fotos', 'kenmerken', 'kamer') if x in r}
        if not kk:
            sys.exit(f'omgeving: {json_file} heeft een gevulde kamers-lijst nodig')
        kamer_html = (
            f'<section data-component="om-kamers" class="al-kamers ut-kamers om-kamers" id="kamers"><div class="al-kamers__wrap">'
            f'<div class="ut-kamers__kop"><h2 class="al-kamers__kop">{d["kamers-kop"]}</h2><p class="ut-kamers__sub">{d["kamers-sub"]}</p></div>'
            f'<div class="kk-rij" data-rij data-lus><div class="kk-spoor" data-spoor tabindex="0" role="group" aria-label="{d["kamer-rij-label"]}">{"".join(kk)}</div>'
            f'<div class="kk-nav"><span class="kk-teller" data-teller aria-live="polite"></span>'
            f'<button type="button" class="kk-pijl" data-stap="-1" aria-label="{d["kamer-vorige"]}">{OM_PIJL_L}</button>'
            f'<button type="button" class="kk-pijl" data-stap="1" aria-label="{d["kamer-volgende"]}">{OM_PIJL_R}</button></div></div></div></section>')
        blok['OM_KAMERPOP'] = (
            f'<dialog class="lp-pop lp-pop--kamer" id="lp-pop-kamer" aria-modal="true" aria-labelledby="lp-pop-kamer-naam" data-l-foto="{d["kamer-pop-foto"]}" data-l-boek="{d["knop-kamer"]}">\n'
            f'    <button type="button" class="lp-pop__sluit" aria-label="{d["pop-sluit"]}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>\n'
            '    <div class="lp-pop__binnen">\n      <div class="lp-pop__media">\n'
            f'        <video class="lp-pop__video" muted playsinline loop autoplay preload="none" aria-label="{d["kamer-pop-video"]}"></video>\n'
            '        <img class="lp-pop__hero" alt="" hidden>\n      </div>\n      <div class="lp-pop__fotos"></div>\n      <div class="lp-pop__body">\n'
            '        <h3 class="lp-pop__titel" id="lp-pop-kamer-naam"></h3>\n        <div class="lp-pop__tekst"></div>\n        <ul class="lp-pop__kenmerken"></ul>\n'
            f'        <div class="lp-pop__acties">\n          <a class="btn btn-primary mews-open lp-pop__boek" data-basis="{mews()}" href="{mews()}">{d["knop-kamer"]}</a>\n        </div>\n'
            '      </div>\n    </div>\n  </dialog>\n  <div class="lp-pop-overlay" hidden></div>\n'
            '  <template id="lp-pop-vink"><svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5 5.5-6"/></svg></template>\n'
            '  <script type="application/json" id="al-kamerdata">' + json.dumps(kamerdata, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    else:
        blok['OM_KAMERPOP'] = ''
    blok['OM_POPDATA'] = ('<script type="application/json" id="om-popdata">'
                          + json.dumps({'uitje': {}, 'kamer': popkamer}, ensure_ascii=False).replace('</', '<\\/') + '</script>')

    # --- FAQ + FAQPage (overzicht: een accordeon; categorie: twee kolommen van drie)
    faq = [i for i in al_lijst(d, 'f', '-v') if d.get(f'f{i}-v')][:6]
    if len(faq) != 6 or any(not d.get(f'f{i}-a') for i in faq):
        sys.exit(f'omgeving: {json_file} heeft precies zes vragen met antwoord nodig (f1..f6)')
    items, ld = [], []
    for j, i in enumerate(faq):
        vr, an = d[f'f{i}-v'], d[f'f{i}-a']
        items.append(f'<details class="as-accordeon__item"{" open" if j == 0 else ""}><summary class="as-accordeon__kop"><h3>{vr}</h3></summary>'
                     f'<div class="as-accordeon__paneel"><p>{an}</p></div></details>')
        ld.append({'@type': 'Question', 'name': om_plat(vr), 'acceptedAnswer': {'@type': 'Answer', 'text': om_plat(an)}})
    blok['OM_FAQ'] = ''.join(items) if pagina == 'overzicht' else (
        f'<div class="as-accordeon">{"".join(items[:3])}</div><div class="as-accordeon">{"".join(items[3:])}</div>')
    blok['OM_FAQ_LD'] = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': ld}, ensure_ascii=False).replace('</', '<\\/')

    # --- hreflang: alleen talen waarvan het JSON bestaat, en alleen als er meer dan een is
    alt = []
    for t, (_, js) in config['langs'].items():
        if os.path.exists(os.path.join(base, js)):
            with open(os.path.join(base, js), encoding='utf-8') as f:
                c = json.load(f).get('canonical')
            if c:
                alt.append(f'<link rel="alternate" hreflang="{t}" href="{c}">')
    if len(alt) > 1 and 'hreflang="nl"' in alt[0]:
        alt.append(alt[0].replace('hreflang="nl"', 'hreflang="x-default"'))
    blok['OM_HREFLANG'] = '\n  '.join(alt) if len(alt) > 1 else ''

    if pagina == 'overzicht':
        # tegels: vijf categorieen, aantal geteld uit het register (0 = tegel zonder aantal)
        tegels = []
        for c in OM_CATS:
            n = len(per_cat[c])
            aantal = f'<i>{n} {woord(n, c)}</i>' if n else ''
            tegels.append(f'<li><a class="om-tegel" href="{L["url-" + c]}">{icoon(OM_CAT_ICO[c], "om-tegel__ico")}<span class="om-tegel__tekst">'
                          f'<b>{L["cat-" + c + "-naam"]}</b>{aantal}<em>{L["cat-" + c + "-regel"]}</em></span>'
                          f'<span class="om-tegel__link">{L["tegel-link"]} {UT_PIJL}</span></a></li>')
        blok['OM_TEGELS'] = ''.join(tegels)
        # raster: alles behalve routes (die staan in de routes-strook); golf-uitjes, anders de banen
        raster = [x for x in register if x['soort'] != 'route' and x['categorie'] != 'golf'] + banen
        raster.sort(key=lambda x: (x['auto'] is None, x['auto'] or 0, x['naam'].lower()))
        radio = (f'<input checked class="om-radio" id="om-f-alle" name="om-f" type="radio">'
                 + ''.join(f'<input class="om-radio" id="om-f-{c}" name="om-f" type="radio">' for c in OM_CATS)
                 + '<input checked class="om-radio" id="om-t-alle" name="om-t" type="radio">'
                 + ''.join(f'<input class="om-radio" id="om-t-{m_}" name="om-t" type="radio">' for m_ in OM_MODES))
        chips_cat = f'<label for="om-f-alle">{L["filter-alle"]}</label>' + ''.join(f'<label for="om-f-{c}">{L["cat-" + c + "-naam"]}</label>' for c in OM_CATS)
        blok['OM_FILTERS'] = (radio + f'<div class="om-filter om-filter--cat" role="group" aria-label="{L["filter-cat-label"]}">{chips_cat}</div>'
                              + om_reischips(L))
        kaarten = ''.join(om_kaart(x, L, golf_url) for x in raster)
        blok['OM_RASTER'] = (f'<div class="om-raster__grid" data-om-raster data-grens="12" data-grens-telefoon="8">{kaarten}<p class="om-leeg">{L["leeg"]}</p></div>'
                             f'<div class="om-toonalle" data-om-meer><button type="button" class="btn al-btn al-btn--ghost-donker">{L["toon-alle"].format(n=len(raster))}</button></div>')
        kop_extra += om_leeg_css(raster, metcat=True)
        # routes-strook: alleen routepagina's die er zijn
        routes = [x for x in register if x['soort'] == 'route']
        routes.sort(key=lambda x: OM_ROUTE_VOLGORDE.index(x['slug']) if x['slug'] in OM_ROUTE_VOLGORDE else 99)
        if routes:
            rk = ''.join(f'<a class="om-route" href="{x["url"]}"><img src="{x["foto"]}" alt="{escape(x["alt"])}" width="960" height="640" loading="lazy" decoding="async">'
                         f'<span class="om-route__tekst"><b>{escape(x["naam"], quote=False)}</b><span class="om-route__regel">{escape(x["regel"], quote=False)}</span>'
                         f'<span class="om-route__link">{L["route-link"]} {UT_PIJL}</span></span></a>' for x in routes)
            blok['OM_ROUTES'] = (f'<div class="om-routes"><h3 class="om-routes__kop">{d["routes-kop"]}</h3><p class="om-routes__sub">{d["routes-sub"]}</p>'
                                 f'<div class="om-routes__rij">{rk}</div></div>')
        else:
            blok['OM_ROUTES'] = ''
        blok['OM_KAMERS'] = kamer_html
        # arrangementen: drie kaarten uit de arrangement-JSON's, zonder prijs; ontbrekende slugs overgeslagen
        with open(os.path.join(base, 'translations', 'arrangementen-nl.json'), encoding='utf-8') as f:
            ao = {x['slug']: x for x in json.load(f)['_arrangementen']}
        ak = []
        for slug in d.get('arrangementen') or []:
            bron = os.path.join(base, 'translations', f'{slug}-nl.json')
            if slug not in ao or not os.path.exists(bron):
                print(f'  WAARSCHUWING omgeving: arrangement {slug!r} bestaat niet, overgeslagen')
                continue
            with open(bron, encoding='utf-8') as f:
                a = json.load(f)
            at = (d.get('_arr_teksten') or {}).get(slug) or {}
            regel = at.get('regel') or ao[slug].get('oms') or a['SUB'].split('. ')[0].rstrip('.') + '.'
            vinken = at.get('vink') or [a['KAART_VINK_' + x] for x in 'ABC' if a.get('KAART_VINK_' + x)]
            vink = ''.join(f'<li>{AL_VINK}<span>{v}</span></li>' for v in vinken)
            arr_url = om_arr_url(slug, ao[slug]['url'], lang)
            ak.append(f'<article class="om-ak"><a class="om-ak__foto" href="{arr_url}" tabindex="-1" aria-hidden="true">'
                      f'<img src="{bestaat(a["HERO_IMG"])}" alt="" width="800" height="533" loading="lazy" decoding="async"></a>'
                      f'<div class="om-ak__body"><h3 class="om-ak__naam">{at.get("naam") or a["KAART_KOP"]}</h3><p class="om-ak__regel">{regel}</p>'
                      f'<ul class="om-ak__incl">{vink}</ul><a class="btn btn-primary om-ak__knop" href="{arr_url}">{L["knop-arr"]}</a></div></article>')
        blok['OM_ARR'] = (f'<section data-component="om-arr" class="al-sec om-arr"><div class="ut-wrap--breed"><div class="om-arr__kop"><div><h2>{d["arr-kop"]}</h2>'
                          f'<p class="om-arr__sub">{d["arr-sub"]}</p></div><a class="al-intro__link" href="spiegel:arrangementen">{L["arr-alle"]} {UT_PIJL}</a></div>'
                          f'<div class="om-arr__rij">{"".join(ak[:3])}</div></div></section>') if ak else ''
        # Google-reviews (opbouw van de adslander, NL-bron met de originele reviewtekst)
        rev_taal = f'content/reviews-google-asteria-{lang}.json'
        rev_pad = d.get('rev-bestand') or (rev_taal if lang != 'nl' and os.path.exists(os.path.join(base, rev_taal)) else 'content/reviews-google-asteria.json')
        with open(os.path.join(base, rev_pad), encoding='utf-8') as f:
            rv = json.load(f)
        noot = L.get('rev-vertaald', '') if rev_pad == rev_taal else (L.get('rev-origineel', '') if lang != 'nl' else '')
        noot = f'<p class="al-rev__vertaald">{noot}</p>' if noot else ''
        score = f'{rv["gemiddelde"]:.1f}'.replace('.', ',')
        aantal = L['rev-aantal'].format(n=f'{rv["aantal"]:,}'.replace(',', '.'))
        profiel = escape(rv.get('profiel_url', 'https://www.google.com/maps?cid=10392502528258527703'))
        sterren = AL_STER * 4 + AL_STER.replace('<svg ', '<svg style="opacity:.35" ', 1)
        rk = []
        for r in rv['reviews'][:12]:
            st = max(1, min(5, int(r.get('sterren') or 5)))
            rk.append(f'<article class="al-rev__kaart"><span class="al-rev__sterren" role="img" aria-label="{st}/5">{AL_STER * st}</span>'
                      f'<p class="al-rev__naam">{escape(r["naam"], quote=False)} <span class="al-rev__datum">&middot; {escape(r.get("datum", ""), quote=False)}</span></p>'
                      f'<p class="al-rev__tekst">&bdquo;{escape(r["tekst"], quote=False)}&rdquo;</p>'
                      f'<p class="al-rev__bron">{L["rev-bron"]} <b>Google</b></p></article>')
        blok['OM_REVIEWS'] = (
            f'<section data-component="al-rev" class="al-rev om-rev"><div class="al-rev__omhulsel"><div class="al-rev__kop"><h2>{d["rev-kop"]}</h2>'
            f'<p class="al-rev__score"><b>{score}</b><span class="al-rev__sterren" role="img" aria-label="{score}/5">{sterren}</span>'
            f'<a class="al-rev__aantal" href="{profiel}" target="_blank" rel="noopener">{aantal}</a></p></div>'
            f'<div class="al-rev__strook"><div class="al-rev__paneel"><p class="al-rev__merk">{AL_GOOGLE_G}Google</p>'
            f'<div class="al-rev__pkop"><span class="al-rev__cijfer">{score}</span><div><p class="al-rev__pregel"><span class="al-rev__sterren" aria-hidden="true">{sterren}</span>{aantal}</p></div></div>{noot}'
            f'<a class="al-rev__alle" href="{profiel}" target="_blank" rel="noopener">{L["rev-alle"]}</a></div>'
            f'<div class="al-rev__spoor" data-spoor tabindex="0" role="group" aria-label="{L["rev-rij-label"]}">{"".join(rk)}</div>'
            f'<button type="button" class="al-rev__pijl" data-stap="1" aria-label="{L["rev-volgende"]}">{OM_PIJL_R}</button></div></div></section>')
    else:
        # categoriepagina: vier icoontegels
        tegels = []
        for i in range(1, 5):
            if not d.get(f'p{i}-kop'):
                sys.exit(f'omgeving: {json_file} heeft vier icoontegels nodig (p1..p4)')
            tegels.append(f'<li class="om-icotegel">{icoon(d[f"p{i}-ico"], "om-icotegel__ico")}<span><b>{d[f"p{i}-kop"]}</b><em>{d[f"p{i}-regel"]}</em></span></li>')
        blok['OM_ICOTEGELS'] = ''.join(tegels)
        eigen = per_cat[pagina]
        if pagina == 'golf':
            bt = d.get('_baan_teksten') or {}
            eigen = [dict(x, **{k: v for k, v in (bt.get(x['naam']) or {}).items() if k in ('tekst', 'rijtijd', 'alt', 'plaats')}) for x in eigen]
            chips = d.get('_baan_chips') or {}
            bk = []
            for x in eigen:
                ch = ''.join(f'<span class="om-chip">{OM_CHIP}{escape(c, quote=False)}</span>' for c in (chips.get(x['naam']) or [])[:4])
                rij = x.get('rijtijd') or (f'{x["auto"]} {L.get("l-min", "min")}' if x.get('auto') else '')
                afstand = ' &middot; '.join(escape(v, quote=False) for v in (x['plaats'], rij) if v)
                if x['url']:
                    knop = f'<a class="btn btn-primary om-baan__knop" href="{x["url"]}">{L["knop-meer-info"]}</a>'
                else:
                    knop = (f'<a class="btn btn-secondary om-baan__knop" href="{x["site"]}" target="_blank" rel="noopener">{L["knop-website"]}'
                            f'<span class="al-vh"> {L["l-nieuw-tabblad"]}</span>{UT_EXTERN}</a>')
                bk.append(f'<article class="om-baan" data-om-dia><div class="om-baan__inhoud"><h3>{escape(x["naam"], quote=False)}</h3>'
                          f'<p class="om-baan__tekst">{escape(x["tekst"], quote=False)}</p>' + (f'<div class="om-baan__chips">{ch}</div>' if ch else '')
                          + (f'<p class="om-baan__afstand">{om_svgcls(UT_VK["auto"], "om-baan__ico")}<span>{afstand}</span></p>' if afstand else '')
                          + f'<div class="om-baan__knoppen">{knop}</div></div>'
                          f'<div class="om-baan__foto"><img src="{x["foto"]}" alt="{escape(x["alt"])}" width="800" height="533" loading="lazy" decoding="async" style="object-position:{x.get("pos", "50% 50%")}"></div></article>')
            nav = ''
            if len(bk) > 1:
                nav = (f'<div class="om-banen__nav" data-om-nav hidden><span class="om-banen__teller" data-om-teller aria-live="polite"></span>'
                       f'<button type="button" class="om-banen__pijl" data-om-stap="-1" aria-label="{L["baan-vorige"]}" aria-controls="om-banen-spoor">{OM_PIJL_L}</button>'
                       f'<button type="button" class="om-banen__pijl" data-om-stap="1" aria-label="{L["baan-volgende"]}" aria-controls="om-banen-spoor">{OM_PIJL_R}</button></div>')
            blok['OM_UITJES'] = (f'<section data-component="om-banen" class="al-sec om-banen" id="uitjes" data-om-slider><div class="ut-wrap--breed">'
                                 f'<div class="om-banen__kop"><div><h2>{d["uitjes-kop"]}</h2><p class="om-banen__sub">{d["uitjes-sub"]}</p></div>{nav}</div>'
                                 f'<div class="om-banen__spoor" id="om-banen-spoor" data-om-spoor tabindex="0" role="region" aria-roledescription="slider" aria-label="{L["banen-label"]}">{"".join(bk)}</div>'
                                 '</div></section>') if bk else ''
            # vergelijkingstabel: een rij alleen als elke baan een waarde heeft
            vgl = d.get('_vergelijk') or {}
            rijen = [r for r in vgl.get('rijen', []) if all((r.get('waarden') or {}).get(x['naam']) for x in eigen)]
            if vgl and rijen and eigen:
                kolommen = ''.join(f'<div class="om-vgl__kol" role="row"><div class="om-vgl__hoofd" role="columnheader"><img src="{x["foto"]}" alt="" width="400" height="267" loading="lazy" decoding="async">'
                                   f'<b>{escape(x["naam"], quote=False)}</b></div>'
                                   + ''.join(f'<div class="om-vgl__cel" role="cell">{escape(r["waarden"][x["naam"]], quote=False)}</div>' for r in rijen) + '</div>' for x in eigen)
                labels = ('<div class="om-vgl__kol om-vgl__labels" aria-hidden="true"><div class="om-vgl__hoofd"></div>'
                          + ''.join(f'<div class="om-vgl__cel">{icoon(r.get("ico", ""), "om-vgl__ico")}<span>{r["label"]}</span></div>' for r in rijen) + '</div>')
                blok['OM_VGL'] = (f'<section data-component="om-vgl" class="al-sec om-vgl" id="vergelijk"><div class="ut-wrap--breed"><div class="om-vgl__kopblok"><h2>{vgl["kop"]}</h2>'
                                  f'<p class="om-vgl__sub">{vgl["sub"]}</p></div><div class="al-paneel om-vgl__paneel"><div class="om-vgl__tabel" tabindex="0" role="table" aria-label="{escape(om_plat(vgl["kop"]))}" '
                                  f'style="--om-kol:{len(eigen)};--om-rij:{len(rijen)}">{labels}{kolommen}</div></div></div></section>')
            else:
                blok['OM_VGL'] = ''
        else:
            blok['OM_VGL'] = ''
            if eigen:
                radio = '<input checked class="om-radio" id="om-t-alle" name="om-t" type="radio">' + ''.join(
                    f'<input class="om-radio" id="om-t-{m_}" name="om-t" type="radio">' for m_ in OM_MODES)
                kaarten = ''.join(om_kaart(x, L, golf_url) for x in eigen)
                blok['OM_UITJES'] = (f'<section data-component="om-uitjes" class="al-sec om-raster om-uitjes" id="uitjes">{radio}{om_reischips(L)}'
                                     f'<div class="om-raster__kop"><h2>{d["uitjes-kop"]}</h2><p class="om-raster__sub">{d["uitjes-sub"]}</p></div>'
                                     f'<div class="om-raster__grid">{kaarten}<p class="om-leeg">{L["leeg-reis"]}</p></div></section>')
                kop_extra += om_leeg_css(eigen, metcat=False)
            else:
                blok['OM_UITJES'] = ''
        # conversie: uitgelicht arrangement of kamerslider
        if conversie == 'arr':
            bron = os.path.join(base, 'translations', d['arr-bron'] + '-nl.json')
            if not os.path.exists(bron):
                sys.exit(f'omgeving: arr-bron {d.get("arr-bron")!r} bestaat niet')
            with open(bron, encoding='utf-8') as f:
                a = json.load(f)
            with open(KALENDER_JSON, encoding='utf-8') as f:
                kal_cfg = json.load(f)
            code = a['VOUCHER']
            cfg = a.get('MEWS_CONFIG') or '6dc9094c-76e3-4fd8-83a7-af1d00ffc556'
            nachten = int(a.get('ARR_NACHTEN') or 1)
            fotos = (a.get('_inbegrepen_fotos') or [])[:6] or [{'img': a['HERO_IMG'], 'alt': a.get('HERO_ALT', '')}]
            alts = d.get('_arr_alts') or []
            fotos = [dict(x, alt=alts[j]) if j < len(alts) else x for j, x in enumerate(fotos)]
            dia = ''.join(f'<figure class="om-fs__dia"><img src="{bestaat(x["img"])}" alt="{escape(x.get("alt", ""))}" width="800" height="1000" loading="lazy" decoding="async" '
                          f'style="object-position:{x.get("pos", "50% 50%")}"></figure>' for x in fotos)
            bol = ''.join(f'<button type="button" class="om-fs__bol{" is-aan" if j == 0 else ""}" data-fs-naar="{j}" aria-label="{L["fs-foto"]} {j + 1}"></button>' for j in range(len(fotos)))
            vink = [d[f'arr-vink{i}'] for i in range(1, 7) if d.get(f'arr-vink{i}')] or [a[f'KAART_VINK_{x}'] for x in 'ABCD' if a.get(f'KAART_VINK_{x}')]
            url = om_arr_url(d['arr-bron'], '/' + urllib.parse.urlparse(a.get('CANONICAL_URL', '')).path.lstrip('/'), lang)
            blok['OM_CONVERSIE'] = (
                f'<section data-component="om-carr" class="al-sec om-carr" id="arrangement"><div class="al-wrap"><div class="om-carr__blok">'
                f'<div class="om-carr__bg" aria-hidden="true"></div>'
                f'<div class="om-carr__foto om-fs" data-om-fs><div class="om-fs__spoor" data-fs-spoor>{dia}</div>'
                + (f'<div class="om-fs__bolletjes">{bol}</div><div class="om-fs__pijlen"><button type="button" class="om-fs__pijl" data-fs-stap="-1" aria-label="{L["fs-vorige"]}">{OM_PIJL_L}</button>'
                   f'<button type="button" class="om-fs__pijl" data-fs-stap="1" aria-label="{L["fs-volgende"]}">{OM_PIJL_R}</button></div>' if len(fotos) > 1 else '')
                + f'</div><div class="om-carr__inner"><h2>{d.get("arr-kop") or a["KAART_KOP"]}</h2><p class="om-carr__sub">{d.get("arr-sub") or a["SUB"]}</p>'
                f'<ul class="om-carr__vinkjes">' + ''.join(f'<li>{OM_VINK}<span>{v}</span></li>' for v in vink) + '</ul>'
                f'<div class="om-carr__acties"><a class="btn btn-primary al-btn mews-open" href="https://app.mews.com/distributor/{cfg}?language={taal}&amp;mewsVoucherCode={code}" data-voucher="{code}">{L["arr-knop"]}</a>'
                f'<a class="al-intro__link" href="{url}">{L["arr-paginalink"]} {UT_PIJL}</a></div></div></div></div></section>')
            if a.get('ARR_KALENDER', True) is not False and code in kal_cfg and lang in AL_KAL_LABELS:
                namen = {KAMER_MEWS[k]: v['naam'] for k, v in kamerbron.items() if k in KAMER_MEWS}
                kalenders.append(al_kalender_dialoog(code, cfg, nachten, kal_cfg[code], namen, d['pop-sluit'], taal=lang)
                                 .replace('<dialog class="ark" ', '<dialog class="ark" id="ar-kal" ', 1))
        else:
            blok['OM_CONVERSIE'] = kamer_html
        blok['OM_KALENDER_KOP'] = ('<link rel="stylesheet" href="arrangement-kalender.css">\n  <script src="arrangement-kalender.js" defer></script>'
                                   if kalenders else '')
        blok['OM_KALENDERS'] = '\n  '.join(kalenders)
        # meer in de omgeving: de vier andere categorieen
        mk = []
        for c in [c for c in OM_CATS if c != pagina]:
            mk.append(f'<a class="om-meer__kaart" href="{L["url-" + c]}"><img src="{bestaat(L["cat-" + c + "-foto"])}" alt="" width="800" height="500" loading="lazy" decoding="async">'
                      f'<span class="om-meer__tekst"><span class="om-meer__naam">{L["cat-" + c + "-naam"]}</span><span class="om-meer__regel">{L["cat-" + c + "-regel"]}</span></span></a>')
        blok['OM_MEER'] = ''.join(mk)

    blok['AL_KOP'], blok['AL_VOET'] = om_kop_voet(d, d['mews-basis'], lang)
    for k, v in blok.items():
        if f'<!-- {k} -->' not in html:
            sys.exit(f'omgeving: plek <!-- {k} --> niet in het sjabloon {config["template"]}')
        html = html.replace(f'<!-- {k} -->', v)
    if kop_extra:
        html = html.replace('</head>', f'  <style>{kop_extra}</style>\n</head>', 1)
    for k, v in d.items():
        if isinstance(v, str) and not k.startswith('_'):
            html = html.replace('{{' + k + '}}', v)
    html = vul_spiegel_links(html)
    open_velden = sorted(set(re.findall(r'\{\{[^}]+\}\}|<!-- (?:OM|AL)_[A-Z_]+ -->', html)))
    if open_velden:
        sys.exit(f'omgeving: open velden in {output_file}: {open_velden}')
    if fouten:
        sys.exit('omgeving:\n  ' + '\n  '.join(sorted(set(fouten))))
    if '—' in html:
        sys.exit(f'omgeving: em-dash in {output_file}')
    if 'bee2f902' in html:
        sys.exit(f'omgeving: oude Mews-config bee2f902 in {output_file}')
    with open(os.path.join(base, output_file), 'w', encoding='utf-8') as f:
        f.write(html)
    tel = ', '.join(f'{c} {len(per_cat[c])}' for c in OM_CATS)
    print(f'  [{template_name}/{lang}] → {output_file}  ({len(html)} chars; register {len(register)} kaarten: {tel})')


def om_reischips(L):
    """Filterbalk reiswijze (labels voor de radio's om-t-*), met lijnicoon."""
    ico = {'auto': UT_VK['auto'], 'lopen': UT_VK['lopen'], 'fiets': UT_VK['fiets']}
    return (f'<div class="om-filter om-filter--reis" role="group" aria-label="{L["filter-reis-label"]}"><label for="om-t-alle">{L["filter-alle"]}</label>'
            + ''.join(f'<label for="om-t-{m_}">{om_svgcls(ico[m_], "om-fico")}{L["filter-" + m_]}</label>' for m_ in OM_MODES) + '</div>')


def om_leeg_css(kaarten, metcat):
    """CSS voor de lege melding: alleen voor filtercombinaties waarin geen enkele kaart overblijft."""
    regels = []
    cats = (['alle'] + OM_CATS) if metcat else ['alle']
    for c in cats:
        for m_ in ['alle'] + OM_MODES:
            n = sum(1 for x in kaarten if (c == 'alle' or x['categorie'] == c) and (m_ == 'alle' or x.get(m_)))
            if n == 0:
                sel = (f'#om-f-{c}:checked ~ ' if metcat else '') + f'#om-t-{m_}:checked ~ .om-raster__grid .om-leeg'
                regels.append(sel)
    return (',\n'.join(regels) + '{display:block}') if regels else ''


# Parse args: optional template name + optional lang codes
args = sys.argv[1:]
templates_to_build = []
langs_filter = []

for arg in args:
    if arg in TEMPLATES:
        templates_to_build.append(arg)
    else:
        langs_filter.append(arg)

expliciet = bool(templates_to_build)
if not templates_to_build:
    templates_to_build = list(TEMPLATES.keys())

for tpl in templates_to_build:
    config = TEMPLATES[tpl]
    langs = langs_filter if langs_filter else list(config['langs'].keys())
    print(f'Building {tpl} [{", ".join(langs)}]...')
    for lang in langs:
        if lang not in config['langs']:
            print(f'  Unknown lang for {tpl}: {lang}')
            sys.exit(1)
        # uitje zonder gegevensbestand: volledige build slaat het over, expliciet gevraagd = fout
        json_uitje = config['langs'][lang][1]
        if config.get('uitje') and not os.path.exists(os.path.join(base, json_uitje)):
            if expliciet:
                sys.exit(f'uitje: {json_uitje} bestaat niet (nodig voor {tpl})')
            print(f'  [{tpl}/{lang}] overgeslagen: {json_uitje} bestaat nog niet')
            continue
        build(tpl, lang)

# Welkom krijgt dezelfde boekingsmodule als de arrangementen (post-stap,
# na build zodat de gelokaliseerde arrangement-bronnen bestaan).
if 'welkom' in templates_to_build:
    print('Injecting welkom booking module...')
    inject_welkom_booking()

print('Done.')
