#!/usr/bin/env python3
"""
Eenmalig script: genereert translations/{nl,en,de}.json en wellness-arr-c.template.html
vanuit de 3 bestaande HTML-bestanden.

Daarna: python3 build.py  →  regenereert alle 3 HTML-bestanden.
"""

import json, os, re

# ── helpers ──────────────────────────────────────────────────────────────────

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()

def extract_between(text, start, end_ctx, end_len=0):
    s = text.index(start)
    e = text.index(end_ctx, s + len(start))
    return text[s : e + end_len]

def extract_wp_zones(text):
    return extract_between(text, 'const WP_ZONES = [\n', '\n];', len('\n];'))

def extract_rooms_data(text):
    start = '  var ROOMS = {\n'
    end_ctx = '\n  };\n\n  // Bijhouden'
    s = text.index(start)
    e = text.index(end_ctx, s)
    return text[s : e + len('\n  };')]

def extract_fallback_reviews(text):
    start = '    var fallback = [\n'
    end_ctx = '\n    ];\n\n    fetch('
    s = text.index(start)
    e = text.index(end_ctx, s)
    return text[s : e + len('\n    ];')]

def extract_month_names(text):
    start = '  var MONTH_NAMES = '
    s = text.index(start)
    e = text.index('];', s)
    return text[s : e + 2]

def extract_day_names(text):
    start = '  var DAY_NAMES   = '
    s = text.index(start)
    e = text.index('];', s)
    return text[s : e + 2]

def extract_days_nl(text):
    start = '  var DAYS_NL = '
    s = text.index(start)
    e = text.index(';', s + len(start))
    return text[s : e + 1]

def extract_months_nl(text):
    start = '  var MONTHS_NL = '
    s = text.index(start)
    e = text.index(';', s + len(start))
    return text[s : e + 1]

def extract_lang_detect(text):
    marker = '<!-- ══ TAALDETECTIE ══════════════════════════════════════════ -->'
    if marker not in text:
        return ''
    s = text.index(marker)
    end_marker = '</script>'
    e = text.index(end_marker, s)
    return text[s : e + len(end_marker)]

# ── read source files ─────────────────────────────────────────────────────────

base = os.path.dirname(os.path.abspath(__file__))
nl = read(os.path.join(base, 'wellness-arr-c.html'))
en = read(os.path.join(base, 'wellness-arr-c-en.html'))
de = read(os.path.join(base, 'wellness-arr-c-de.html'))

# ── translation table ─────────────────────────────────────────────────────────

entries = []

def t(key, nl_val, en_val, de_val):
    entries.append((key, nl_val, en_val, de_val))

# HTML / meta
t('HTML_LANG', 'nl', 'en', 'de')
t('PAGE_TITLE',
  'Wellness Arrangement | Hotel Asteria Venray',
  'Wellness Package | Hotel Asteria Venray',
  'Wellness Arrangement | Hotel Asteria Venray')
t('META_DESC',
  "Wellness arrangement met overnachting, drie-gangen diner en ontbijtbuffet bij Hotel Asteria Venray. Vier unieke sauna's op de Top Floor. Vanaf \u20ac139,50 p.p.",
  "Wellness package with overnight stay, three-course dinner and breakfast buffet at Hotel Asteria Venray. Four unique saunas on the Top Floor. From \u20ac139.50 p.p.",
  "Wellness-Arrangement mit \u00dcbernachtung, Drei-G\u00e4nge-Dinner und Fr\u00fchst\u00fccksbuffet im Hotel Asteria Venray. Vier einzigartige Saunen auf der Top Floor. Ab \u20ac139,50 p.P.")
t('CANONICAL_URL',
  'https://visit.asteria.nl/wellness-arr-c',
  'https://visit.asteria.nl/wellness-arr-c-en',
  'https://visit.asteria.nl/wellness-arr-c-de')
t('OG_LOCALE', 'nl_NL', 'en_GB', 'de_DE')

# Schema.org
t('ARRANGEMENT_NAME', 'Wellness Arrangement', 'Wellness Package', 'Wellness Arrangement')
t('SCHEMA_OFFER_DESC',
  'Overnachting, welkomstdrankje, badjas en slippers, vrije toegang wellness, drie-gangen diner en ontbijtbuffet.',
  'Overnight stay, welcome drink, bathrobe and slippers, free wellness access, three-course dinner and breakfast buffet.',
  '\u00dcbernachtung, Willkommensgetr\u00e4nk, Bademantel und Hausschuhe, freier Wellnesszugang, Drei-G\u00e4nge-Dinner und Fr\u00fchst\u00fccksbuffet.')
t('SCHEMA_UNIT_TEXT', '"unitText": "per persoon"', '"unitText": "per person"', '"unitText": "pro Person"')

# Language detection script (NL only, empty for EN/DE)
t('LANG_DETECT_SCRIPT', extract_lang_detect(nl), '', '')

# Sticky FAB (full aria first, then shorter BTN_BOOK_DIRECT)
t('STICKY_FAB_ARIA', 'Boek direct: Wellness Arrangement', 'Book now: Wellness Package', 'Jetzt buchen: Wellness Arrangement')

# Sticky card
t('STICKY_CARD_ARIA', 'Snel boeken', 'Quick booking', 'Schnell buchen')
t('STICKY_CARD_PER_PERSON', 'per persoon', 'per person', 'p.P.')

# Language selector (full options block — handles selected attribute per lang)
t('LANG_SELECT_OPTIONS',
  '<option value="nl" selected>nl</option>\n          <option value="en">en</option>\n          <option value="de">de</option>',
  '<option value="nl">nl</option>\n          <option value="en" selected>en</option>\n          <option value="de">de</option>',
  '<option value="nl">nl</option>\n          <option value="en">en</option>\n          <option value="de" selected>de</option>')

# Nav
t('NAV_ROOMS', 'Kamers en Suites', 'Rooms and Suites', 'Zimmer und Suiten')
t('NAV_SURROUNDINGS', 'Omgeving', 'Surroundings', 'Umgebung')
t('NAV_CONTACT', 'Contact', 'Contact', 'Kontakt')
t('NAV_BOOK_BTN', 'Boek nu', 'Book now', 'Jetzt buchen')
t('NAV_MENU', 'Menu', 'Menu', 'Men\u00fc')
t('NAV_CALL', 'Bel', 'Call', 'Anrufen')
t('LANG_SWITCH_SEL_VALUE', "'nl'", "'en'", "'de'")
t('LANG_SWITCH_JS',
  "    if (v === 'en') window.location.replace('/wellness-arr-c-en');\n    else if (v === 'de') window.location.replace('/wellness-arr-c-de');",
  "    if (v === 'nl') window.location.replace('/wellness-arr-c');\n    else if (v === 'de') window.location.replace('/wellness-arr-c-de');",
  "    if (v === 'nl') window.location.replace('/wellness-arr-c');\n    else if (v === 'en') window.location.replace('/wellness-arr-c-en');")

# Hero
t('HERO_LOCATION', 'Noord-Limburg', 'North Limburg', 'Nord-Limburg')
t('HERO_TITLE', 'Wellness, diner<br>&amp; een goed bed', "Wellness, dinner<br>&amp; a good night's sleep", 'Wellness, Abendessen<br>&amp; ein gutes Bett')
t('HERO_SUBTITLE',
  'Sauna, drie-gangen diner en een comfortabele kamer. Alles geregeld, u hoeft alleen te komen.',
  'Sauna, three-course dinner and a comfortable room. Everything arranged, all you need to do is arrive.',
  'Sauna, Drei-G\u00e4nge-Dinner und ein komfortables Zimmer. Alles geregelt, Sie m\u00fcssen nur kommen.')
t('BTN_BOOK_ARRANGEMENT', 'Boek het arrangement', 'Book the package', 'Das Arrangement buchen')
t('HERO_USP1', "4 sauna's op de Top Floor", "4 saunas on the Top Floor", "4 Saunen auf der Top Floor")
t('HERO_USP2', "Diner &amp; ontbijt inbegrepen", "Dinner &amp; breakfast included", "Dinner &amp; Fr\u00fchst\u00fcck inbegriffen")
t('HERO_USP3', 'Gratis annuleren', 'Free cancellation', 'Kostenlose Stornierung')

# arr-c section
t('ARR_C_ARIA', 'Wellness arrangement, wat is inbegrepen', 'Wellness package, what is included', 'Wellness Arrangement, was ist inbegriffen')
t('ARR_C_RATING_ARIA', '4,2 van 5 sterren \u00b7 2.219 Google reviews', '4.2 out of 5 stars \u00b7 2,219 Google reviews', '4,2 von 5 Sternen \u00b7 2.219 Google-Bewertungen')
t('ARR_C_RATING_COUNT', '\u00b7 2.219 reviews', '\u00b7 2,219 reviews', '\u00b7 2.219 Bewertungen')
t('ARR_C_CAPTION_INIT', 'Comfortabele kamer', 'Comfortable room', 'Komfortables Zimmer')
t('ARR_C_TITLE', 'Wat is inbegrepen?', "What's included?", 'Was ist inbegriffen?')
t('ARR_C_INTRO',
  'E\u00e9n overnachting met wellness, diner en ontbijt. Vrije toegang tot de wellness op de Top Floor.',
  'One overnight stay with wellness, dinner and breakfast. Free access to the wellness on the Top Floor.',
  'Eine \u00dcbernachtung mit Wellness, Abendessen und Fr\u00fchst\u00fcck. Freier Zugang zum Wellnessbereich auf der Top Floor.')
t('ARR_C_F1_NAME', 'Overnachting', 'Overnight stay', '\u00dcbernachtung')
t('ARR_C_F1_DESC', 'Kamer naar keuze, van Comfort tot Suite', 'Room of your choice, from Comfort to Suite', 'Zimmer nach Wahl, vom Comfort bis zur Suite')
t('ARR_C_F2_CAP', 'Botega welkomstdrankje op de kamer', 'Botega welcome drink in your room', 'Botega Willkommensgetr\u00e4nk auf dem Zimmer')
t('ARR_C_F2_NAME', 'Welkomstdrankje', 'Welcome drink', 'Willkommensgetr\u00e4nk')
t('ARR_C_F2_DESC', 'Botega prosecco op de kamer bij aankomst', 'Botega prosecco in your room on arrival', 'Botega Prosecco auf dem Zimmer bei der Ankunft')
t('ARR_C_F3_CAP', 'Badjas, slippers &amp; handdoekpakket', 'Bathrobe, slippers &amp; towel set', 'Bademantel, Pantoffeln &amp; Handtücher')
t('ARR_C_F3_NAME', 'Badjas &amp; slippers', 'Bathrobe &amp; slippers', 'Bademantel &amp; Pantoffeln')
t('ARR_C_F3_DESC', 'Alles klaargelegd, niets mee te nemen', 'Everything prepared, nothing to bring', 'Alles bereitgestellt, nichts mitbringen')
t('ARR_C_F4_CAP', "4 sauna's &amp; stoombad \u00b7 Top Floor", "4 saunas &amp; steam bath &middot; Top Floor", "4 Saunen &amp; Dampfbad \u00b7 Top Floor")
t('ARR_C_F4_NAME', 'Vrije wellness toegang', 'Free wellness access', 'Freier Wellnesszugang')
t('ARR_C_F4_DESC', "4 sauna&rsquo;s &amp; stoombad op de Top Floor", "4 saunas &amp; steam bath on the Top Floor", "4 Saunen &amp; Dampfbad auf der Top Floor")
t('ARR_C_F5_CAP', 'Drie-gangen diner', 'Three-course dinner', 'Drei-G\u00e4nge-Dinner')
t('ARR_C_F5_DESC', 'Seizoensgerechten, rustig aan tafel', 'Seasonal dishes, no rush at the table', 'Saisonale Gerichte, entspanntes Abendessen')
t('ARR_C_F6_CAP', 'Uitgebreid ontbijtbuffet', 'Extensive breakfast buffet', 'Ausgiebiges Fr\u00fchst\u00fccksbuffet')
t('ARR_C_F6_DESC', 'Warme broodjes, charcuterie en meer', 'Fresh bread, charcuterie and more', 'Frisches Brot, Aufschnitt und mehr')
t('ARR_C_PRICE_FROM', 'Vanaf', 'From', 'Ab')
t('ARR_C_PRICE_SUB', 'p.p. op basis van een Comfort Kamer', 'p.p. based on a Comfort Room', 'p.P. auf Basis eines Comfort-Zimmers')

# Reviews
t('DINER_ARIA', 'Drie-gangen diner, inbegrepen in het arrangement', 'Three-course dinner, included in the package', 'Drei-G\u00e4nge-Dinner, im Arrangement enthalten')
t('REVIEWS_ARIA', 'Gastbeoordelingen', 'Guest reviews', 'G\u00e4stebewertungen')
t('REVIEWS_TOTAL_INIT', '2.219 beoordelingen', '2,219 reviews', '2.219 Bewertungen')
t('REVIEWS_LOADING', 'Reviews worden geladen&hellip;', 'Loading reviews&hellip;', 'Bewertungen werden geladen&hellip;')
t('REVIEWS_JS_EXPR',
  "(data.total ? data.total.toLocaleString('nl-NL') : '2.219') + ' beoordelingen'",
  "(data.total ? data.total.toLocaleString('en-GB') : '2,219') + ' reviews'",
  "(data.total ? data.total.toLocaleString('de-DE') : '2.219') + ' Bewertungen'")
t('REVIEWS_FALLBACK_JS', extract_fallback_reviews(nl), extract_fallback_reviews(en), extract_fallback_reviews(de))

# Wellness plattegrond
t('WP_ARIA', 'Wellness faciliteiten, interactieve plattegrond', 'Wellness facilities, interactive floor plan', 'Wellnesseinrichtungen, interaktiver Grundriss')
t('WP_TITLE', 'Verken de faciliteiten', 'Explore the facilities', 'Erkunden Sie die Einrichtungen')
t('WP_SUBTITLE',
  'Ontdek alle ruimtes van onze 300m\u00b2 wellness op de Top Floor. Tik op een locatie voor meer informatie over elke ruimte.',
  'Discover all spaces of our 300m\u00b2 wellness area on the Top Floor. Tap a location for more information about each space.',
  'Entdecken Sie alle R\u00e4ume unseres 300m\u00b2 gro\u00dfen Wellnessbereichs auf der Top Floor. Tippen Sie auf einen Standort f\u00fcr weitere Informationen.')
t('WP_IMG_ALT',
  'Plattegrond van de wellness op de Top Floor van Hotel Asteria',
  'Floor plan of the wellness area on the Top Floor of Hotel Asteria',
  'Grundriss des Wellnessbereichs auf der Top Floor von Hotel Asteria')
t('WP_PANEL_ARIA', 'Wellness ruimte details', 'Wellness space details', 'Wellnessraum Details')
t('BTN_CLOSE_ARIA', 'Sluiten', 'Close', 'Schlie\u00dfen')
t('WP_PIN_ARIA_SUFFIX', ', tik voor meer info', ', tap for more info', ', tippen f\u00fcr mehr Infos')
t('WP_ZONES_JS', extract_wp_zones(nl), extract_wp_zones(en), extract_wp_zones(de))

# Rooms static HTML
t('ROOMS_ARIA', 'Kamertypes', 'Room types', 'Zimmertypen')
t('ROOMS_EYEBROW', 'Kies uw kamer', 'Choose your room', 'W\u00e4hlen Sie Ihr Zimmer')
t('ROOMS_TITLE', 'Welke kamer past bij u?', 'Which room suits you?', 'Welches Zimmer passt zu Ihnen?')
t('ROOMS_SUB', 'Upgrade voor meer comfort of privacy', 'Upgrade for more comfort or privacy', 'Upgrade f\u00fcr mehr Komfort oder Privatsph\u00e4re')
t('ROOM_COMFORT_IMG_ALT', 'Comfort Kamer', 'Comfort Room', 'Comfort Zimmer')
t('ROOM_COMFORT_BADGE_STATIC', 'Standaard inbegrepen', 'Included in package', 'Im Arrangement enthalten')
t('ROOM_COMFORT_FEATS_STATIC',
  '~22 m\u00b2 \u00b7 tweepersoons bed \u00b7 douche \u00b7 zithoek \u00b7 airco \u00b7 WiFi',
  '~22 m\u00b2 \u00b7 double bed \u00b7 shower \u00b7 seating area \u00b7 A/C \u00b7 WiFi',
  '~22 m\u00b2 \u00b7 Doppelbett \u00b7 Dusche \u00b7 Sitzecke \u00b7 Klimaanlage \u00b7 WLAN')
t('ROOM_ROYALE_IMG_ALT', 'Royale Kamer', 'Royale Room', 'Royale Kamer')
t('ROOM_ROYALE_DELTAS',
  'meer ruimte <span class="plus">+</span> ligbad',
  'more space <span class="plus">+</span> bathtub',
  'mehr Platz <span class="plus">+</span> Badewanne')
t('ROOM_SAUNA_BADGE_STATIC', '+ Eigen sauna', '+ Private sauna', '+ Eigene Sauna')
t('ROOM_DELUXE_IMG_ALT', 'Deluxe Kamer', 'Deluxe Room', 'Deluxe Kamer')
t('ROOM_DELUXE_DELTAS',
  'meer ruimte <span class="plus">+</span> priv\u00e9 infraroodsauna',
  'more space <span class="plus">+</span> private infrared sauna',
  'mehr Platz <span class="plus">+</span> private Infrarotsauna')
t('ROOM_JUNIOR_DELTAS',
  'ruime zithoek <span class="plus">+</span> ligbad <span class="plus">+</span> koelkast',
  'spacious seating area <span class="plus">+</span> bathtub <span class="plus">+</span> mini fridge',
  'gro\u00dfe Sitzecke <span class="plus">+</span> Badewanne <span class="plus">+</span> K\u00fchlschrank')
t('ROOM_SUITE_DELTAS',
  'priv\u00e9 infraroodsauna <span class="plus">+</span> ruime zithoek <span class="plus">+</span> koelkast',
  'private infrared sauna <span class="plus">+</span> spacious seating area <span class="plus">+</span> mini fridge',
  'private Infrarotsauna <span class="plus">+</span> gro\u00dfe Sitzecke <span class="plus">+</span> K\u00fchlschrank')
t('ROOM_BRUIDSSUITE_IMG_ALT', 'Bruidssuite', 'Bridal Suite', 'Bruidssuite')
t('ROOM_BRUIDSSUITE_DELTAS',
  'vrijstaand bad <span class="plus">+</span> inloopdouche <span class="plus">+</span> koelkast',
  'freestanding bath <span class="plus">+</span> walk-in shower <span class="plus">+</span> mini fridge',
  'freistehende Badewanne <span class="plus">+</span> begehbare Dusche <span class="plus">+</span> K\u00fchlschrank')

# ROOMS JS data (large block — must precede individual room string keys)
t('ROOMS_JS_DATA', extract_rooms_data(nl), extract_rooms_data(en), extract_rooms_data(de))

# Room popup JS
t('POPUP_ARIA', 'Kamerdetails', 'Room details', 'Zimmerdetails')
t('ROOM_POPUP_PREV_ARIA', 'Vorige', 'Previous', 'Zur\u00fcck')
t('ROOM_POPUP_NEXT_ARIA', 'Volgende', 'Next', 'Weiter')
t('ROOM_POPUP_CTA', 'Boek dit arrangement', 'Book this package', 'Dieses Zimmer w\u00e4hlen')

# Booking popup HTML
t('BK_POPUP_ARIA', 'Verblijf boeken', 'Book your stay', 'Aufenthalt buchen')
t('BK_COMMENT_STEP1', 'Stap 1: Datum kiezen', 'Step 1: Choose dates', 'Stap 1: Datum kiezen')
t('BK_TITLE_STEP1', 'Kies uw verblijfsdata', 'Choose your stay dates', 'W\u00e4hlen Sie Ihre Aufenthaltsdaten')
t('BK_LABEL_ARRIVAL', 'Aankomst', 'Arrival', 'Ankunft')
t('BK_LABEL_DEPARTURE', 'Vertrek', 'Departure', 'Abreise')
t('BK_LABEL_NIGHTS', 'Nachten', 'Nights', 'N\u00e4chte')
t('BK_SELECTED_ROOM_LABEL', 'Geselecteerde kamer', 'Selected room', 'Ausgew\u00e4hltes Zimmer')
t('BK_CHANGE_ROOM_BTN', 'wijzig', 'change', '\u00e4ndern')
t('BK_BTN_NEXT_STEP2_HTML', 'Volgende: kies kamer &rarr;', 'Next: choose room &rarr;', 'Weiter: Zimmer w\u00e4hlen &rarr;')
t('BK_BTN_DIRECT_BOOK', 'Of boek direct zonder kamerkeuze', 'Or book directly without room selection', 'Oder direkt ohne Zimmerauswahl buchen')
t('BK_COMMENT_STEP2', 'Stap 2: Kamer kiezen', 'Step 2: Choose room', 'Stap 2: Kamer kiezen')
t('BK_BACK_STEP1_ARIA', 'Terug naar datumkeuze', 'Back to date selection', 'Zur\u00fcck zur Datumsauswahl')
t('BK_BACK_STEP1_TEXT', 'Aanpassen', 'Back', 'Zur\u00fcck')
t('BK_ROOMS_ARIA', 'Kamertype kiezen', 'Choose room type', 'Kamertype kiezen')
t('BK_BTN_CONFIRM_HTML', 'Bekijk beschikbaarheid &rarr;', 'Check availability &rarr;', 'Verf\u00fcgbarkeit pr\u00fcfen &rarr;')
t('BK_COMMENT_STEP3', 'Stap 3: Kamerdetail sub-view', 'Step 3: Room detail sub-view', 'Stap 3: Kamerdetail sub-view')
t('BK_BACK_STEP2_ARIA', 'Terug naar kamerkeuze', 'Back to room selection', 'Zur\u00fcck zur Zimmerauswahl')

# Calendar JS arrays
t('CAL_MONTH_NAMES_JS', extract_month_names(nl), extract_month_names(en), extract_month_names(de))
t('CAL_DAY_NAMES_JS', extract_day_names(nl), extract_day_names(en), extract_day_names(de))
t('BOOKING_DAYS_NL_JS', extract_days_nl(nl), extract_days_nl(en), extract_days_nl(de))
t('BOOKING_MONTHS_NL_JS', extract_months_nl(nl), extract_months_nl(en), extract_months_nl(de))

# Booking popup JS dynamic text
t('BK_JS_CHECK_AVAIL',
  "'Bekijk beschikbaarheid \\u2192'",
  "'Check availability \\u2192'",
  "'Verf\u00fcgbarkeit pr\u00fcfen \\u2192'")
t('BK_JS_NEXT_STEP2',
  "'Volgende: kies kamer \\u2192'",
  "'Next: choose room \\u2192'",
  "'Weiter: Zimmer w\u00e4hlen \\u2192'")
t('BK_JS_LOADING', "'Laden\\u2026'", "'Loading\\u2026'", "'Laden\\u2026'")
t('BK_JS_NO_AVAIL', "'Kies een kamer'", "'Choose a room'", "'Kies een kamer'")
t('BK_JS_NIGHTS_SINGULAR', "' nacht'", "' night'", "' Nacht'")
t('BK_JS_NIGHTS_PLURAL', "' nachten'", "' nights'", "' N\u00e4chte'")
t('BK_JS_VOL', 'bk-room-card__vol">Vol</span>', 'bk-room-card__vol">Full</span>', 'bk-room-card__vol">Belegt</span>')
t('BK_JS_MEER_INFO', 'tabindex="-1">meer info</button>', 'tabindex="-1">more info</button>', 'tabindex="-1">mehr Info</button>')
t('BK_JS_SELECT_ROOM', '>Selecteer deze kamer</button>', '>Select this room</button>', '>Selecteer deze kamer</button>')
t('BTN_SUBSCRIBE', 'Aanmelden', 'Sign up', 'Anmelden')

# Diner section
t('DINER_BG_ARIA',
  'Restaurant Hotel Asteria, intiem dineren met uitzicht op het groen',
  'Restaurant Hotel Asteria, intimate dining with a view of the greenery',
  'Restaurant Hotel Asteria, intimes Dinieren mit Blick ins Gr\u00fcne')
t('DINER_EYEBROW', 'Inbegrepen in het arrangement', 'Included in the package', 'Im Arrangement enthalten')
t('DINER_TITLE', 'Een heerlijk drie-gangen diner', 'A delicious three-course dinner', 'Ein k\u00f6stliches Drei-G\u00e4nge-Dinner')
t('DINER_SUB',
  'Na een avond in de wellness schuift u aan in ons restaurant. Vers bereid, seizoensgebonden, geen haast.',
  'After an evening in the wellness centre, you join us in our restaurant. Freshly prepared, seasonal, no rush.',
  'Nach einem Abend im Wellnessbereich nehmen Sie in unserem Restaurant Platz. Frisch zubereitet, saisonal, keine Eile.')

# Footer
t('FOOTER_TERMS', 'Algemene voorwaarden', 'Terms &amp; conditions', 'AGB')
t('FOOTER_COPYRIGHT', 'Onderdeel van Van der Sterren Hotels', 'Part of Van der Sterren Hotels', 'Teil von Van der Sterren Hotels')

# Email capture
t('EC_OVERLAY_ARIA', 'Nieuwsbrief aanmelden', 'Newsletter sign-up', 'Newsletter anmelden')
t('EC_COMMENT_SCREEN1', 'Scherm 1: form', 'Screen 1: form', 'Scherm 1: form')
t('EC_TITLE',
  'Gratis badjas, handdoek<br>&amp; bubbels op de kamer',
  'Free bathrobe, towel<br>&amp; bubbles in your room',
  'Kostenloser Bademantel, Handtuch<br>&amp; Sekt auf dem Zimmer')
t('EC_SUB',
  'Meld u aan voor de nieuwsbrief en ontvang het pakket bij uw eerste verblijf.',
  'Sign up for the newsletter and receive the package on your first stay.',
  'Melden Sie sich f\u00fcr den Newsletter an und erhalten Sie das Paket bei Ihrem ersten Aufenthalt.')
t('EC_ERROR',
  'Er ging iets mis. Probeer het opnieuw.',
  'Something went wrong. Please try again.',
  'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.')
t('EC_EMAIL_PLACEHOLDER', 'uw e-mailadres', 'your email address', 'Ihre E-Mail-Adresse')
t('EC_CONSENT',
  'Door u aan te melden gaat u akkoord met onze <a href="/privacyverklaring" target="_blank">privacyverklaring</a>. Afmelden kan altijd.',
  'By signing up you agree to our <a href="/privacyverklaring" target="_blank">privacy policy</a>. You can unsubscribe at any time.',
  'Mit der Anmeldung stimmen Sie unserer <a href="/privacyverklaring" target="_blank">Datenschutzerkl\u00e4rung</a> zu. Abmeldung jederzeit m\u00f6glich.')
t('EC_SUCCESS_TITLE', 'Check uw inbox', 'Check your inbox', 'Pr\u00fcfen Sie Ihren Posteingang')
t('EC_SUCCESS_SUB',
  'We hebben u een mail gestuurd. Open hem om uw aanmelding te bevestigen. Uw persoonlijke code staat daarin.',
  "We've sent you an email. Open it to confirm your subscription. Your personal code is inside.",
  'Wir haben Ihnen eine E-Mail geschickt. \u00d6ffnen Sie sie, um Ihre Anmeldung zu best\u00e4tigen. Ihr pers\u00f6nlicher Code ist darin enthalten.')
t('EC_SPAM_NOTE',
  'Geen mail ontvangen? Check uw spamfolder.',
  "Didn't receive an email? Check your spam folder.",
  'Keine E-Mail erhalten? Pr\u00fcfen Sie Ihren Spam-Ordner.')
t('EC_COMMENT_SCREEN2', 'Scherm 2: succes', 'Screen 2: success', 'Scherm 2: succes')

# Cookie banner
t('COOKIE_BANNER_ARIA', 'Cookiemelding', 'Cookie notice', 'Cookiemelding')
t('COOKIE_TEXT',
  'Deze website gebruikt cookies voor een optimale ervaring.',
  'This website uses cookies for an optimal experience.',
  'Diese Website verwendet Cookies f\u00fcr ein optimales Erlebnis.')
t('COOKIE_LINK_TEXT', 'Meer info', 'More info', 'Mehr Infos')
t('COOKIE_BTN', 'Akkoord', 'Accept', 'Akzeptieren')

# BTN_BOOK_DIRECT last: shorter than STICKY_FAB_ARIA which contains it
t('BTN_BOOK_DIRECT', 'Boek direct', 'Book now', 'Jetzt buchen')

# ── write JSON files ──────────────────────────────────────────────────────────

trans_dir = os.path.join(base, 'translations')
os.makedirs(trans_dir, exist_ok=True)

for lang_idx, filename in [(0, 'nl.json'), (1, 'en.json'), (2, 'de.json')]:
    data = {key: vals[lang_idx] for key, *vals in entries}
    path = os.path.join(trans_dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Written: {path}')

# ── create template ───────────────────────────────────────────────────────────
# Sort by NL value length (longest first) to avoid partial replacements.

sorted_entries = sorted(entries, key=lambda x: len(x[1]), reverse=True)

template = nl

for key, nl_val, en_val, de_val in sorted_entries:
    if not nl_val:
        continue
    marker = '{{' + key + '}}'
    count = template.count(nl_val)
    if count == 0:
        print(f'WARNING: key {key!r} — NL value not found in template')
    template = template.replace(nl_val, marker)

template_path = os.path.join(base, 'wellness-arr-c.template.html')
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(template)
print(f'Written: {template_path}  ({len(template)} chars)')
