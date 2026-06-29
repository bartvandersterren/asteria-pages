#!/usr/bin/env python3
"""Genereer kamerdetailpagina's (NL/EN/DE) voor Hotel Asteria.

Hergebruikt de gedeelde shell uit comfort-kamer.html en vult per kamer en
per taal de unieke secties in. comfort-kamer.html (NL) wordt niet
overschreven; wel bijgewerkt (kamertypes-lijst, prijs, sticky, hreflang,
taalwisselaar). EN/DE-varianten worden als <slug>-en.html / <slug>-de.html
weggeschreven.
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'comfort-kamer.html')
with open(SRC, encoding='utf-8') as f:
    html = f.read()

def slice_between(text, start_marker, end_marker, include_end=False):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[i:(j + len(end_marker)) if include_end else j].rstrip() + '\n'

STYLE   = slice_between(html, '  <style>', '  </style>', include_end=True)
NAV     = slice_between(html, '<!-- ══ NAV', '</nav>', include_end=True)
INCLUDED= slice_between(html, '<!-- ══ INCLUSIEF-BALK', '<!-- ══ KAMERTYPES')
ARR     = slice_between(html, '<!-- ══ ARRANGEMENTEN', '<!-- ══ FAQ')
FOOTER  = slice_between(html, '<!-- ══ FOOTER', '</footer>', include_end=True)
_si = html.index('/* ── Mews booking')
SCRIPTS = html[html.rindex('<script>', 0, _si):html.index('</script>', _si) + len('</script>')]

# ── Boekingsmodule overnemen van de arrangementpagina ──────────────────
import json
ARRSRC = open(os.path.join(BASE, 'happy-summer-arrangement.html'), encoding='utf-8').read()
def _bt(a, b, inc_b=False):
    i = ARRSRC.index(a); j = ARRSRC.index(b, i); return ARRSRC[i:j + (len(b) if inc_b else 0)]
MEWS_HEAD  = _bt('<!-- Mews BookingEngine -->', '<!-- End Mews BookingEngine -->', True)
_cs = ARRSRC.rindex('/*', 0, ARRSRC.index('.bk-overlay {'))
_ce = ARRSRC.rindex('/*', 0, ARRSRC.index('.ec-overlay {'))
BK_CSS     = ARRSRC[_cs:_ce].rstrip()
BK_MARKUP  = _bt('<div class="bk-overlay"', '<!-- ══ DINER').rstrip()
_dps = ARRSRC.rindex('(function', 0, ARRSRC.index('var MONTH_NAMES'))
_dpe = ARRSRC.index('})();', ARRSRC.index('window.clearCustomCalendar')) + len('})();')
DATEPICKER = ARRSRC[_dps:_dpe]
BOOKING    = _bt('/* ══ BOOKING POPUP', '}());', True)
# Voucher verwijderen (kamerboeking, geen arrangement)
BOOKING = BOOKING.replace("var VOUCHER   = 'SUMMER';", "var VOUCHER   = null;")
BOOKING = BOOKING.replace("var url = MEWS_BASE + '?mewsVoucherCode=' + VOUCHER + '&mewsStart=' + toYMD(checkin)",
                          "var url = MEWS_BASE + '?mewsStart=' + toYMD(checkin)")
BOOKING = BOOKING.replace("      window.mewsApi.setVoucherCode(VOUCHER);\n", "")
BOOKING = BOOKING.replace("        VoucherCode: VOUCHER,\n", "")

CATEGORY = {'comfort':'98900f3b-e5e2-49c9-9776-af1d00ffc315','comfort-3':'85ca19d7-eea5-41c8-8b93-af1d00ffc315',
            'mindervalide':'fa5b6540-7234-49ce-beb1-af1d00ffc315','royale':'a8fd7310-0d61-422f-89e6-af1d00ffc315',
            'deluxe':'c737de50-e41e-4c8d-a818-af1d00ffc315','junior-suite':'27ea8deb-ded5-4856-8fdd-af1d00ffc315',
            'suite':'4a642b66-68e6-444c-beeb-af1d00ffc315','bruidssuite':'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'}
BOOKABLE = ['comfort','comfort-3','mindervalide','royale','deluxe','junior-suite','suite','bruidssuite']
# Kamerkeuze-stap toont nu alle 8 kamers (i.p.v. de hardgecodeerde 6)
BOOKING = BOOKING.replace(
    "var ROOM_KEYS = ['comfort', 'royale', 'deluxe', 'junior-suite', 'suite', 'bruidssuite'];",
    "var ROOM_KEYS = ['comfort', 'comfort-3', 'mindervalide', 'royale', 'deluxe', 'junior-suite', 'suite', 'bruidssuite'];")

BK_TR = {
 'en':[("var MONTH_NAMES = ['Januari','Februari','Maart','April','Mei','Juni',",
        "var MONTH_NAMES = ['January','February','March','April','May','June',"),
       ("'Juli','Augustus','September','Oktober','November','December'];",
        "'July','August','September','October','November','December'];"),
       ("var DAY_NAMES   = ['Ma','Di','Wo','Do','Vr','Za','Zo'];","var DAY_NAMES   = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];"),
       ("var DAYS_NL = ['zo','ma','di','wo','do','vr','za'];","var DAYS_NL = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];"),
       ("var MONTHS_NL = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];",
        "var MONTHS_NL = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];"),
       ("' nacht'", "' night'"),("' nachten'", "' nights'"),
       ("Kies uw verblijfsdata","Choose your dates"),(">Aankomst</span>",">Arrival</span>"),
       (">Vertrek</span>",">Departure</span>"),(">Nachten</span>",">Nights</span>"),
       (">Geselecteerde kamer</span>",">Selected room</span>"),(">wijzig</button>",">change</button>"),
       ("Volgende: kies kamer &rarr;","Next: choose room →"),("Volgende: kies kamer \\u2192","Next: choose room \\u2192"),
       ("Of boek direct zonder kamerkeuze","Or book directly without choosing a room"),
       (">Kies uw kamer</h2>",">Choose your room</h2>"),("Bekijk beschikbaarheid &rarr;","Check availability →"),
       ("Bekijk beschikbaarheid \\u2192","Check availability \\u2192"),("&larr; Aanpassen","← Adjust"),
       ("&larr; Terug","← Back"),("Laden\\u2026","Loading\\u2026"),("Kies een kamer","Choose a room"),
       (">Vol<",">Full<"),(">meer info<",">more info<"),("Selecteer deze kamer","Select this room")],
 'de':[("var MONTH_NAMES = ['Januari','Februari','Maart','April','Mei','Juni',",
        "var MONTH_NAMES = ['Januar','Februar','März','April','Mai','Juni',"),
       ("'Juli','Augustus','September','Oktober','November','December'];",
        "'Juli','August','September','Oktober','November','Dezember'];"),
       ("var DAY_NAMES   = ['Ma','Di','Wo','Do','Vr','Za','Zo'];","var DAY_NAMES   = ['Mo','Di','Mi','Do','Fr','Sa','So'];"),
       ("var DAYS_NL = ['zo','ma','di','wo','do','vr','za'];","var DAYS_NL = ['So','Mo','Di','Mi','Do','Fr','Sa'];"),
       ("var MONTHS_NL = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];",
        "var MONTHS_NL = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];"),
       ("' nacht'", "' Nacht'"),("' nachten'", "' Nächte'"),
       ("Kies uw verblijfsdata","Wählen Sie Ihre Daten"),(">Aankomst</span>",">Anreise</span>"),
       (">Vertrek</span>",">Abreise</span>"),(">Nachten</span>",">Nächte</span>"),
       (">Geselecteerde kamer</span>",">Ausgewähltes Zimmer</span>"),(">wijzig</button>",">ändern</button>"),
       ("Volgende: kies kamer &rarr;","Weiter: Zimmer wählen →"),("Volgende: kies kamer \\u2192","Weiter: Zimmer wählen \\u2192"),
       ("Of boek direct zonder kamerkeuze","Oder direkt ohne Zimmerwahl buchen"),
       (">Kies uw kamer</h2>",">Wählen Sie Ihr Zimmer</h2>"),("Bekijk beschikbaarheid &rarr;","Verfügbarkeit prüfen →"),
       ("Bekijk beschikbaarheid \\u2192","Verfügbarkeit prüfen \\u2192"),("&larr; Aanpassen","← Ändern"),
       ("&larr; Terug","← Zurück"),("Laden\\u2026","Lädt\\u2026"),("Kies een kamer","Zimmer wählen"),
       (">Vol<",">Belegt<"),(">meer info<",">mehr Infos<"),("Selecteer deze kamer","Dieses Zimmer wählen")],
}
def bk_localize(text, lang):
    if lang == 'nl':
        return text
    for a, b in BK_TR[lang]:
        text = text.replace(a, b)
    return text

def rooms_js(lang):
    obj = {}
    for k in BOOKABLE:
        r = BYKEY[k]
        obj[k] = {'name': NAME[k][lang], 'upgrade': '', 'mewsCategoryId': CATEGORY[k],
                  'imgs': [slides_for(r)[0]], 'badge': '', 'desc': SHORT[k][lang],
                  'features': FEAT[k][lang]}
    return 'window.ROOMS = ' + json.dumps(obj, ensure_ascii=False) + ';'

def booking_bundle(lang):
    override = ("window.openBooking = function (k) { if (window.ROOMS && window.ROOMS[k]) "
                "window.openBookingPopup(k); else window.openBookingPopup(); };")
    return '\n'.join([rooms_js(lang), bk_localize(DATEPICKER, lang), bk_localize(BOOKING, lang), override])

SUFFIX = {'nl': '', 'en': '-en', 'de': '-de'}
HTMLLANG = {'nl': 'nl', 'en': 'en', 'de': 'de'}
OGLOCALE = {'nl': 'nl_NL', 'en': 'en_US', 'de': 'de_DE'}
MISSING = set()

# ── Iconen specs-kaart ─────────────────────────────────────────────────
IC_M2   = '<svg viewBox="0 0 24 24"><path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/></svg>'
IC_BED  = '<svg viewBox="0 0 24 24"><path d="M2 17v-4a2 2 0 012-2h16a2 2 0 012 2v4M2 17v3M22 17v3M4 11V8a2 2 0 012-2h12a2 2 0 012 2v3"/></svg>'
IC_PERS = '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><circle cx="16" cy="8" r="2.5"/><path d="M3 20v-1a5 5 0 015-5h2a5 5 0 015 5v1M16 14a4 4 0 014 4v2"/></svg>'
IC_BATH = '<svg viewBox="0 0 24 24"><path d="M4 12h16M6 12V6a2 2 0 012-2h0a2 2 0 012 2M4 12v3a5 5 0 005 5h6a5 5 0 005-5v-3"/></svg>'

# ── UI-strings ─────────────────────────────────────────────────────────
UI = {
 'gasten':       {'nl':'Gasten','en':'Guests','de':'Gäste'},
 'pers2':        {'nl':'2 personen','en':'2 guests','de':'2 Personen'},
 'pers1':        {'nl':'1 persoon','en':'1 guest','de':'1 Person'},
 'aankomst':     {'nl':'Aankomst','en':'Arrival','de':'Anreise'},
 'vertrek':      {'nl':'Vertrek','en':'Departure','de':'Abreise'},
 'availability': {'nl':'Bekijk beschikbaarheid','en':'Check availability','de':'Verfügbarkeit prüfen'},
 'crumb_rooms':  {'nl':'Kamers en Suites','en':'Rooms & Suites','de':'Zimmer & Suiten'},
 'eyebrow':      {'nl':'Kamertype','en':'Room type','de':'Zimmertyp'},
 'kenmerken':    {'nl':'Kenmerken','en':'Features','de':'Merkmale'},
 'faciliteiten': {'nl':'Faciliteiten','en':'Facilities','de':'Ausstattung'},
 'badkamer':     {'nl':'Badkamer','en':'Bathroom','de':'Badezimmer'},
 'disclaimer':   {'nl':'De getoonde afbeeldingen zijn ter illustratie. De werkelijke kamerindeling en inrichting kunnen afwijken.',
                  'en':'The images shown are for illustration purposes. The actual room layout and furnishings may vary.',
                  'de':'Die gezeigten Bilder dienen zur Veranschaulichung. Die tatsächliche Zimmeraufteilung und -einrichtung kann abweichen.'},
 'spec_area':    {'nl':'Kameroppervlak','en':'Room size','de':'Zimmergröße'},
 'spec_occ':     {'nl':'Bezetting','en':'Occupancy','de':'Belegung'},
 'price_label':  {'nl':'Vanaf, per kamer per nacht','en':'From, per room per night','de':'Ab, pro Zimmer pro Nacht'},
 'reserve_direct':{'nl':'Reserveren direct','en':'Book directly','de':'Direkt reservieren'},
 'reserve':      {'nl':'Reserveren','en':'Book','de':'Reservieren'},
 'types_h':      {'nl':'Verschillende kamertypes','en':'Our room types','de':'Unsere Zimmertypen'},
 'types_sub':    {'nl':'Elke kamer ingericht voor comfort, voor elk verblijf en elk budget. Vergelijk de typen en kies wat bij u past.',
                  'en':'Every room designed for comfort, for every stay and every budget. Compare the types and choose what suits you.',
                  'de':'Jedes Zimmer auf Komfort ausgelegt, für jeden Aufenthalt und jedes Budget. Vergleichen Sie die Typen und wählen Sie, was zu Ihnen passt.'},
 'tab_all':      {'nl':'Alle','en':'All','de':'Alle'},
 'tab_std':      {'nl':'Standaard','en':'Standard','de':'Standard'},
 'tab_lux':      {'nl':'Luxe','en':'Luxury','de':'Luxus'},
 'current':      {'nl':'U bekijkt deze kamer','en':'You are viewing this room','de':'Sie betrachten dieses Zimmer'},
 'details':      {'nl':'Meer details','en':'More details','de':'Mehr Details'},
 'arr_h':        {'nl':'Hotelarrangementen bij dit kamertype','en':'Hotel packages for this room type','de':'Hotelarrangements für diesen Zimmertyp'},
 'arr_cta':      {'nl':'Bekijk arrangement','en':'View package','de':'Arrangement ansehen'},
 'faq_h':        {'nl':'Veelgestelde vragen','en':'Frequently asked questions','de':'Häufig gestellte Fragen'},
 'sticky_from':  {'nl':'Vanaf','en':'From','de':'Ab'},
 'menu':         {'nl':'Menu','en':'Menu','de':'Menü'},
 'bel':          {'nl':'Bel','en':'Call','de':'Anrufen'},
}
UI.update({
 'crumb_overview':{'nl':'Kamertypes','en':'Room types','de':'Zimmertypen'},
 'ov_hero':   {'nl':'Onze kamertypes','en':'Our room types','de':'Unsere Zimmertypen'},
 'ov_eyebrow':{'nl':'Welkom in Noord-Limburg','en':'Welcome to North Limburg','de':'Willkommen in Nord-Limburg'},
 'ov_h':      {'nl':'Ontspannen overnachten in het hart van Limburg','en':'Relaxed stays in the heart of Limburg','de':'Entspannt übernachten im Herzen Limburgs'},
 'ov_p':      {'nl':'Hotel Asteria ligt op een steenworp van de A73, omringd door de bossen en velden van Noord-Limburg. Of u nu komt voor rust, romantiek of een zakelijk bezoek — bij ons vindt u een kamer die bij uw verblijf past, met de warme Limburgse gastvrijheid die Asteria kenmerkt.',
              'en':'Hotel Asteria sits just off the A73, surrounded by the woods and fields of North Limburg. Whether you come for rest, romance or business, you will find a room to suit your stay — with the warm Limburg hospitality that defines Asteria.',
              'de':'Hotel Asteria liegt nur einen Steinwurf von der A73 entfernt, umgeben von den Wäldern und Feldern Nord-Limburgs. Ob für Ruhe, Romantik oder eine Geschäftsreise — bei uns finden Sie ein Zimmer, das zu Ihrem Aufenthalt passt, mit der herzlichen limburgischen Gastfreundschaft, die Asteria auszeichnet.'},
 'ov_sub_h':  {'nl':'Moderne kamers van alle gemakken voorzien','en':'Modern rooms with every comfort','de':'Moderne Zimmer mit allem Komfort'},
 'ov_sub_p':  {'nl':'Al onze kamers zijn modern en sfeervol ingericht en standaard voorzien van alle comfort. Van een comfortabele Comfort kamer tot de luxe Bruidssuite met vrijstaand ligbad — elke kamer is met zorg ingericht.',
              'en':'All our rooms are modern and tastefully furnished and come with every comfort as standard. From a cosy Comfort room to the luxurious Bridal Suite with a freestanding bathtub — every room is appointed with care.',
              'de':'Alle unsere Zimmer sind modern und stilvoll eingerichtet und standardmäßig mit allem Komfort ausgestattet. Vom gemütlichen Komfortzimmer bis zur luxuriösen Hochzeitssuite mit freistehender Badewanne — jedes Zimmer ist mit Sorgfalt gestaltet.'},
 'promo_eyebrow':{'nl':'Meer dan een overnachting','en':'More than a stay','de':'Mehr als eine Übernachtung'},
 'promo_h':   {'nl':'Maak van uw verblijf een complete ervaring','en':'Turn your stay into a complete experience','de':'Machen Sie Ihren Aufenthalt zu einem kompletten Erlebnis'},
 'promo_p':   {'nl':'Combineer uw kamer met onze wellness van 300 m² op de Top Floor, een heerlijk diner in de brasserie of een van onze arrangementen. Zo wordt een overnachting een moment om naar uit te kijken.',
              'en':'Combine your room with our 300 m² wellness area on the Top Floor, a delicious dinner in the brasserie or one of our packages. That is how an overnight stay becomes something to look forward to.',
              'de':'Kombinieren Sie Ihr Zimmer mit unserem 300 m² großen Wellnessbereich im Top Floor, einem köstlichen Abendessen in der Brasserie oder einem unserer Arrangements. So wird aus einer Übernachtung ein Moment, auf den man sich freut.'},
 'promo_btn1':{'nl':'Bekijk arrangementen','en':'View packages','de':'Arrangements ansehen'},
 'promo_btn2':{'nl':'Reserveer direct','en':'Book directly','de':'Direkt reservieren'},
 'ov_faq_q':  {'nl':'Welke kamertypes biedt Hotel Asteria?','en':'Which room types does Hotel Asteria offer?','de':'Welche Zimmertypen bietet Hotel Asteria?'},
 'ov_faq_a':  {'nl':'Hotel Asteria heeft Comfort kamers (ook voor 3 personen), een aangepaste kamer, Royale en Deluxe kamers, een Junior Suite, een Suite en een Bruidssuite. Op elke kameromschrijving vindt u de details, foto\'s en de actuele prijs.',
              'en':'Hotel Asteria offers Comfort rooms (also for 3 guests), an accessible room, Royale and Deluxe rooms, a Junior Suite, a Suite and a Bridal Suite. Each room page shows the details, photos and current price.',
              'de':'Hotel Asteria bietet Komfortzimmer (auch für 3 Personen), ein barrierefreies Zimmer, Royale und Deluxe Zimmer, eine Junior-Suite, eine Suite und eine Hochzeitssuite. Auf jeder Zimmerseite finden Sie die Details, Fotos und den aktuellen Preis.'},
})
OVLIST = {
 'nl':['Comfortabel bed','Moderne badkamer met douche','Gratis WiFi','Airconditioning','Koffie- en theefaciliteiten','Flatscreen-tv','Föhn','Toegang tot de fitnessruimte'],
 'en':['Comfortable bed','Modern bathroom with shower','Free WiFi','Air conditioning','Coffee and tea facilities','Flatscreen TV','Hairdryer','Access to the fitness room'],
 'de':['Bequemes Bett','Modernes Badezimmer mit Dusche','Kostenloses WLAN','Klimaanlage','Kaffee- und Teezubehör','Flachbild-TV','Föhn','Zugang zum Fitnessraum'],
}

def ui(k, lang): return UI[k][lang]

def area(n, lang):  # "Circa 22 m²"
    return {'nl':f'Circa {n} m&sup2;','en':f'Approx. {n} m&sup2;','de':f'Ca. {n} m&sup2;'}[lang]
def maxg(n, lang):
    return {'nl':f'Max. {n} gasten','en':f'Max. {n} guests','de':f'Max. {n} Gäste'}[lang]

# ── Termen-woordenboek (NL → (en, de)) ─────────────────────────────────
TERM = {
 # faciliteiten
 'Airconditioning':('Air conditioning','Klimaanlage'),
 'Koffie- en theefaciliteiten':('Coffee and tea facilities','Kaffee- und Teezubehör'),
 'Flatscreen-tv':('Flatscreen TV','Flachbild-TV'),
 'Föhn':('Hairdryer','Föhn'),
 'Gratis WiFi':('Free WiFi','Kostenloses WLAN'),
 'Toegang tot de fitnessruimte':('Access to the fitness room','Zugang zum Fitnessraum'),
 'Koelkastje met gratis flesjes water':('Mini-fridge with free bottled water','Kühlschrank mit kostenlosem Flaschenwasser'),
 # kenmerken
 'Twinbeds (2 eenpersoonsbedden)':('Twin beds (2 single beds)','Twinbetten (2 Einzelbetten)'),
 '3 eenpersoonsbedden':('3 single beds','3 Einzelbetten'),
 'Tweepersoonsbed of twinbeds (2 eenpersoonsbedden)':('Double bed or twin beds (2 single beds)','Doppelbett oder Twinbetten (2 Einzelbetten)'),
 'Tweepersoons kingsize bed':('Kingsize double bed','Kingsize-Doppelbett'),
 'Bedbank voor extra slaapgelegenheid':('Sofa bed for extra sleeping space','Schlafsofa für zusätzliche Schlafmöglichkeit'),
 'Geschikt voor maximaal 2 personen':('Suitable for up to 2 guests','Geeignet für bis zu 2 Personen'),
 'Geschikt voor maximaal 3 personen':('Suitable for up to 3 guests','Geeignet für bis zu 3 Personen'),
 'Geschikt voor maximaal 4 personen':('Suitable for up to 4 guests','Geeignet für bis zu 4 Personen'),
 'Zithoek met comfortabele stoelen':('Seating area with comfortable chairs','Sitzecke mit bequemen Sesseln'),
 'Ruime zithoek met comfortabele stoelen':('Spacious seating area with comfortable chairs','Geräumige Sitzecke mit bequemen Sesseln'),
 'Extra brede deuren en ruime indeling voor rolstoel of rollator':('Extra-wide doors and a spacious layout for wheelchair or walker','Besonders breite Türen und geräumiges Layout für Rollstuhl oder Rollator'),
 'Badjassen en slippers':('Bathrobes and slippers','Bademäntel und Hausschuhe'),
 # badkamer-lijst
 'Eigen badkamer met douche':('Private bathroom with shower','Eigenes Badezimmer mit Dusche'),
 'Föhn aanwezig':('Hairdryer provided','Föhn vorhanden'),
 'Eigen badkamer met douche en/of bad':('Private bathroom with shower and/or bath','Eigenes Badezimmer mit Dusche und/oder Badewanne'),
 'Aangepaste, rolstoeltoegankelijke badkamer met douche':('Accessible, wheelchair-friendly bathroom with shower','Barrierefreies, rollstuhlgerechtes Badezimmer mit Dusche'),
 'Extra beugels en zitje in de douche':('Extra grab rails and a seat in the shower','Zusätzliche Haltegriffe und Sitz in der Dusche'),
 'Luxe private infraroodsauna':('Luxury private infrared sauna','Luxuriöse private Infrarotsauna'),
 'Eigen badkamer met bad en douche':('Private bathroom with bath and shower','Eigenes Badezimmer mit Badewanne und Dusche'),
 'Private infraroodsauna':('Private infrared sauna','Private Infrarotsauna'),
 'Luxe badkamer met inloopdouche':('Luxury bathroom with walk-in shower','Luxuriöses Badezimmer mit ebenerdiger Dusche'),
 'Ruim vrijstaand ligbad':('Spacious freestanding bathtub','Geräumige freistehende Badewanne'),
 # bed strong / sub
 'Twinbeds':('Twin beds','Twinbetten'),
 'Twin of tweepersoons':('Twin or double','Twin oder Doppelbett'),
 'Kingsize bed':('Kingsize bed','Kingsize-Bett'),
 '2 eenpersoonsbedden':('2 single beds','2 Einzelbetten'),
 'Ruimte voor drie':('Room for three','Platz für drei'),
 '+ bedbank':('+ sofa bed','+ Schlafsofa'),
 'Naar keuze':('Your choice','Nach Wahl'),
 'Tweepersoons':('Double bed','Doppelbett'),
 # badkamer strong / sub
 'Badkamer met douche':('Bathroom with shower','Badezimmer mit Dusche'),
 'Douche en/of bad':('Shower and/or bath','Dusche und/oder Badewanne'),
 'Aangepaste badkamer':('Accessible bathroom','Barrierefreies Bad'),
 'Douche + infraroodsauna':('Shower + infrared sauna','Dusche + Infrarotsauna'),
 'Bad en douche':('Bath and shower','Badewanne und Dusche'),
 'Ligbad + inloopdouche':('Bathtub + walk-in shower','Badewanne + ebenerdige Dusche'),
 'Inloopdouche':('Walk-in shower','Ebenerdige Dusche'),
 'Eigen badkamer':('Private bathroom','Eigenes Badezimmer'),
 'Rolstoeltoegankelijk, douche':('Wheelchair-accessible, shower','Rollstuhlgerecht, Dusche'),
 'Privé wellness':('Private wellness','Private Wellness'),
 'Luxe badkamer':('Luxury bathroom','Luxuriöses Badezimmer'),
 # badges
 'Voordelig':('Great value','Günstig'),
 '3 personen':('3 persons','3 Personen'),
 'Aangepast':('Accessible','Barrierefrei'),
 'Ruimer':('More space','Geräumiger'),
 '+ Eigen sauna':('+ Private sauna','+ Eigene Sauna'),
 'Familie':('Family','Familie'),
 'Premium':('Premium','Premium'),
}
def tr(s, lang):
    if lang == 'nl':
        return s
    if s in TERM:
        return TERM[s][0 if lang == 'en' else 1]
    MISSING.add(s)
    return s

# ── Namen, omschrijvingen, short, feat per kamer/taal ──────────────────
NAME = {
 'comfort':      {'nl':'Comfort kamer','en':'Comfort room','de':'Komfortzimmer'},
 'comfort-3':    {'nl':'Comfort kamer 3 personen','en':'Comfort room for 3','de':'Komfortzimmer für 3 Personen'},
 'mindervalide': {'nl':'Mindervalide kamer','en':'Accessible room','de':'Barrierefreies Zimmer'},
 'royale':       {'nl':'Royale kamer','en':'Royale room','de':'Royale Zimmer'},
 'deluxe':       {'nl':'Deluxe kamer','en':'Deluxe room','de':'Deluxe-Zimmer'},
 'junior-suite': {'nl':'Junior suite','en':'Junior Suite','de':'Junior-Suite'},
 'suite':        {'nl':'Suite','en':'Suite','de':'Suite'},
 'bruidssuite':  {'nl':'Bruidssuite','en':'Bridal Suite','de':'Hochzeitssuite'},
}
DESC = {
 'comfort':{
  'nl':['Geniet van een comfortabele en modern ingerichte kamer, ideaal voor een ontspannen verblijf in Noord-Limburg. Of u nu komt voor een korte break of een zakelijk bezoek, in onze Comfort kamer voelt u zich direct thuis.',
        'De kamer beschikt over twee eenpersoonsbedden, een eigen badkamer met douche en een zithoek met comfortabele stoelen — alles wat u nodig hebt om tot rust te komen.'],
  'en':['Enjoy a comfortable, modern room — ideal for a relaxing stay in North Limburg. Whether you come for a short break or a business trip, you will feel right at home in our Comfort room.',
        'The room has two single beds, a private bathroom with shower and a seating area with comfortable chairs — everything you need to unwind.'],
  'de':['Genießen Sie ein komfortables, modern eingerichtetes Zimmer — ideal für einen erholsamen Aufenthalt in Nord-Limburg. Ob für eine kurze Auszeit oder eine Geschäftsreise, in unserem Komfortzimmer fühlen Sie sich sofort zu Hause.',
        'Das Zimmer verfügt über zwei Einzelbetten, ein eigenes Badezimmer mit Dusche und eine Sitzecke mit bequemen Sesseln — alles, was Sie zum Entspannen brauchen.']},
 'comfort-3':{
  'nl':['Onze 3-persoons Comfort kamer biedt extra ruimte voor families of vrienden die samen op pad gaan. Alles is aanwezig voor een aangenaam en zorgeloos verblijf in het groene Noord-Limburg.',
        'Drie eenpersoonsbedden, een eigen badkamer en een fijne zithoek maken deze kamer ideaal voor wie samen reist.'],
  'en':['Our Comfort room for three offers extra space for families or friends travelling together. Everything is on hand for a pleasant, carefree stay in green North Limburg.',
        'Three single beds, a private bathroom and a pleasant seating area make this room ideal for those travelling together.'],
  'de':['Unser Komfortzimmer für drei Personen bietet zusätzlichen Platz für Familien oder Freunde, die gemeinsam unterwegs sind. Alles ist vorhanden für einen angenehmen, sorglosen Aufenthalt im grünen Nord-Limburg.',
        'Drei Einzelbetten, ein eigenes Badezimmer und eine gemütliche Sitzecke machen dieses Zimmer ideal für alle, die zusammen reisen.']},
 'mindervalide':{
  'nl':['Onze aangepaste kamer is speciaal ontworpen voor gasten met beperkte mobiliteit. Ook ons restaurant en terras zijn rolstoelvriendelijk, zodat u tijdens uw verblijf zorgeloos kunt genieten van een heerlijk diner en de gastvrijheid van Asteria.',
        'Een ruime indeling, extra brede deuren en een aangepaste badkamer zorgen voor comfort en zelfstandigheid.'],
  'en':['Our accessible room is specially designed for guests with limited mobility. Our restaurant and terrace are wheelchair-friendly too, so you can enjoy a delicious dinner and the hospitality of Asteria with complete ease.',
        'A spacious layout, extra-wide doors and an adapted bathroom provide comfort and independence.'],
  'de':['Unser barrierefreies Zimmer ist speziell für Gäste mit eingeschränkter Mobilität konzipiert. Auch unser Restaurant und die Terrasse sind rollstuhlgerecht, sodass Sie ein köstliches Abendessen und die Gastfreundschaft von Asteria unbeschwert genießen können.',
        'Ein geräumiges Layout, besonders breite Türen und ein angepasstes Badezimmer sorgen für Komfort und Selbstständigkeit.']},
 'royale':{
  'nl':['Onze Royale kamers zijn groter dan de Comfort kamers en bieden net dat beetje extra. Het ruime gevoel en de comfortabele zithoek maken deze kamer ideaal voor wie iets meer luxe wil tijdens het verblijf.',
        'Kies voor een tweepersoonsbed of twinbeds en geniet van de extra ruimte en een eigen badkamer met douche of bad.'],
  'en':['Our Royale rooms are larger than the Comfort rooms and offer just that little bit extra. The spacious feel and comfortable seating area make this room ideal for those who want a touch more luxury during their stay.',
        'Choose a double bed or twin beds and enjoy the extra space and a private bathroom with shower or bath.'],
  'de':['Unsere Royale Zimmer sind größer als die Komfortzimmer und bieten genau das gewisse Extra. Das großzügige Raumgefühl und die bequeme Sitzecke machen dieses Zimmer ideal für alle, die etwas mehr Luxus wünschen.',
        'Wählen Sie ein Doppelbett oder Twinbetten und genießen Sie den zusätzlichen Platz und ein eigenes Badezimmer mit Dusche oder Badewanne.']},
 'deluxe':{
  'nl':['Onze Deluxe kamers hebben alles voor een luxe verblijf in Noord-Limburg. De private infraroodsauna in de badkamer maakt deze kamer ideaal voor wie écht wil ontspannen — een kleine wellness-ervaring op uw eigen kamer.',
        'Naast de eigen sauna geniet u van een comfortabele zithoek en alle gemakken binnen handbereik.'],
  'en':['Our Deluxe rooms have everything for a luxurious stay in North Limburg. The private infrared sauna in the bathroom makes this room ideal for those who really want to relax — a little wellness experience in your own room.',
        'Besides your own sauna, you enjoy a comfortable seating area and every convenience within reach.'],
  'de':['Unsere Deluxe-Zimmer bieten alles für einen luxuriösen Aufenthalt in Nord-Limburg. Die private Infrarotsauna im Badezimmer macht dieses Zimmer ideal für alle, die wirklich entspannen möchten — ein kleines Wellness-Erlebnis im eigenen Zimmer.',
        'Neben der eigenen Sauna genießen Sie eine bequeme Sitzecke und allen Komfort in Reichweite.']},
 'junior-suite':{
  'nl':['Onze ruime Junior Suites bieden de luxe van ruimte met een grote zithoek om even heerlijk te ontspannen na een dag op pad. Ideaal voor wie net dat beetje extra wil tijdens het verblijf in Noord-Limburg.',
        'Met een kingsize bed en een bedbank voor extra slaapgelegenheid is de Junior Suite ook perfect voor families.'],
  'en':['Our spacious Junior Suites offer the luxury of space with a large seating area to relax after a day out. Ideal for those who want just that little bit extra during their stay in North Limburg.',
        'With a kingsize bed and a sofa bed for extra sleeping space, the Junior Suite is also perfect for families.'],
  'de':['Unsere geräumigen Junior-Suiten bieten den Luxus von Platz mit einer großen Sitzecke, um nach einem Tag unterwegs herrlich zu entspannen. Ideal für alle, die genau das gewisse Extra während ihres Aufenthalts in Nord-Limburg wünschen.',
        'Mit einem Kingsize-Bett und einem Schlafsofa für zusätzliche Schlafmöglichkeit ist die Junior-Suite auch perfekt für Familien.']},
 'suite':{
  'nl':['Beleef Asteria in onze meest ruime en luxe kamer. Met een eigen infraroodsauna, een ruime zithoek en alle gemakken binnen handbereik is de Suite dé plek om volledig tot rust te komen — meer dan een hotelkamer, een complete ervaring.',
        'Een kingsize bed en bedbank bieden ruimte voor maximaal vier personen.'],
  'en':['Experience Asteria in our most spacious and luxurious room. With a private infrared sauna, a spacious seating area and every convenience within reach, the Suite is the place to fully unwind — more than a hotel room, a complete experience.',
        'A kingsize bed and sofa bed offer space for up to four guests.'],
  'de':['Erleben Sie Asteria in unserem geräumigsten und luxuriösesten Zimmer. Mit einer privaten Infrarotsauna, einer großzügigen Sitzecke und allem Komfort in Reichweite ist die Suite der Ort, um vollkommen zur Ruhe zu kommen — mehr als ein Hotelzimmer, ein komplettes Erlebnis.',
        'Ein Kingsize-Bett und ein Schlafsofa bieten Platz für bis zu vier Personen.']},
 'bruidssuite':{
  'nl':['Onze Bruidssuite is ontworpen voor bijzondere momenten. Of u nu net getrouwd bent of een romantisch weekend viert, geniet samen van de luxe, de rust en de warme sfeer die Asteria zo kenmerkt.',
        'Een vrijstaand ligbad, een ruime inloopdouche en badjassen met slippers maken het verblijf compleet.'],
  'en':['Our Bridal Suite is designed for special moments. Whether you have just married or are celebrating a romantic weekend, enjoy together the luxury, the calm and the warm atmosphere that so characterises Asteria.',
        'A freestanding bathtub, a spacious walk-in shower and bathrobes with slippers complete the stay.'],
  'de':['Unsere Hochzeitssuite ist für besondere Momente gestaltet. Ob frisch vermählt oder bei einem romantischen Wochenende — genießen Sie gemeinsam den Luxus, die Ruhe und die warme Atmosphäre, die Asteria so auszeichnet.',
        'Eine freistehende Badewanne, eine geräumige ebenerdige Dusche sowie Bademäntel und Hausschuhe machen den Aufenthalt komplett.']},
}
SHORT = {
 'comfort':     {'nl':'Een comfortabele kamer voor twee personen met alles wat u nodig hebt voor een ontspannen verblijf.',
                 'en':'A comfortable room for two with everything you need for a relaxing stay.',
                 'de':'Ein komfortables Zimmer für zwei mit allem, was Sie für einen erholsamen Aufenthalt brauchen.'},
 'comfort-3':   {'nl':'Extra ruimte voor families of vrienden — drie eenpersoonsbedden en alle gemakken.',
                 'en':'Extra space for families or friends — three single beds and every convenience.',
                 'de':'Zusätzlicher Platz für Familien oder Freunde — drei Einzelbetten und jeder Komfort.'},
 'mindervalide':{'nl':'Ruime, aangepaste kamer voor gasten met beperkte mobiliteit, met rolstoeltoegankelijke badkamer.',
                 'en':'Spacious, accessible room for guests with limited mobility, with a wheelchair-friendly bathroom.',
                 'de':'Geräumiges, barrierefreies Zimmer für Gäste mit eingeschränkter Mobilität, mit rollstuhlgerechtem Bad.'},
 'royale':      {'nl':'Ruimer dan de Comfort kamer, met een comfortabele zithoek en de keuze voor een bad.',
                 'en':'Larger than the Comfort room, with a comfortable seating area and the option of a bath.',
                 'de':'Größer als das Komfortzimmer, mit bequemer Sitzecke und der Wahl einer Badewanne.'},
 'deluxe':      {'nl':'Een privé infraroodsauna op de kamer — wellness begint bij u aan de deur.',
                 'en':'A private infrared sauna in the room — wellness starts at your door.',
                 'de':'Eine private Infrarotsauna im Zimmer — Wellness beginnt vor Ihrer Tür.'},
 'junior-suite':{'nl':'Kingsize bed, bad en een ruime zithoek met bedbank voor extra slaapgelegenheid.',
                 'en':'Kingsize bed, bath and a spacious seating area with a sofa bed for extra sleeping space.',
                 'de':'Kingsize-Bett, Badewanne und eine geräumige Sitzecke mit Schlafsofa für zusätzliche Schlafmöglichkeit.'},
 'suite':       {'nl':'Onze meest ruime kamer met eigen infraroodsauna en royale zithoek.',
                 'en':'Our most spacious room with a private infrared sauna and a generous seating area.',
                 'de':'Unser geräumigstes Zimmer mit privater Infrarotsauna und großzügiger Sitzecke.'},
 'bruidssuite': {'nl':'Vrijstaand ligbad, ruime inloopdouche en de meest romantische sfeer van het hotel.',
                 'en':'Freestanding bathtub, spacious walk-in shower and the most romantic atmosphere in the hotel.',
                 'de':'Freistehende Badewanne, geräumige ebenerdige Dusche und die romantischste Atmosphäre des Hotels.'},
}
FEAT = {
 'comfort':     {'nl':['~22 m&sup2;','Twinbeds','Douche','Airco','WiFi'],
                 'en':['~22 m&sup2;','Twin beds','Shower','A/C','WiFi'],
                 'de':['~22 m&sup2;','Twinbetten','Dusche','Klima','WLAN']},
 'comfort-3':   {'nl':['~22 m&sup2;','3 bedden','Max. 3','Douche/bad'],
                 'en':['~22 m&sup2;','3 beds','Max. 3','Shower/bath'],
                 'de':['~22 m&sup2;','3 Betten','Max. 3','Dusche/Bad']},
 'mindervalide':{'nl':['~37 m&sup2;','Aangepast','Twinbeds','Bedbank'],
                 'en':['~37 m&sup2;','Accessible','Twin beds','Sofa bed'],
                 'de':['~37 m&sup2;','Barrierefrei','Twinbetten','Schlafsofa']},
 'royale':      {'nl':['~25 m&sup2;','Bad of douche','Zithoek','Airco'],
                 'en':['~25 m&sup2;','Bath or shower','Seating area','A/C'],
                 'de':['~25 m&sup2;','Bad oder Dusche','Sitzecke','Klima']},
 'deluxe':      {'nl':['~25 m&sup2;','Infraroodsauna','Douche','Zithoek'],
                 'en':['~25 m&sup2;','Infrared sauna','Shower','Seating area'],
                 'de':['~25 m&sup2;','Infrarotsauna','Dusche','Sitzecke']},
 'junior-suite':{'nl':['~37 m&sup2;','Kingsize','Bedbank','Bad & douche'],
                 'en':['~37 m&sup2;','Kingsize','Sofa bed','Bath & shower'],
                 'de':['~37 m&sup2;','Kingsize','Schlafsofa','Bad & Dusche']},
 'suite':       {'nl':['~40 m&sup2;','Kingsize','Infraroodsauna','Bedbank'],
                 'en':['~40 m&sup2;','Kingsize','Infrared sauna','Sofa bed'],
                 'de':['~40 m&sup2;','Kingsize','Infrarotsauna','Schlafsofa']},
 'bruidssuite': {'nl':['~36 m&sup2;','Kingsize','Ligbad','Inloopdouche'],
                 'en':['~36 m&sup2;','Kingsize','Bathtub','Walk-in shower'],
                 'de':['~36 m&sup2;','Kingsize','Badewanne','Ebenerdige Dusche']},
}

# ── Kamer-basisdata (NL termen; vertaald via tr/TERM) ──────────────────
FAC_BASE = ['Airconditioning','Koffie- en theefaciliteiten','Flatscreen-tv','Föhn','Gratis WiFi','Toegang tot de fitnessruimte']
ROOMS = [
 {'key':'comfort','slug':'comfort-kamer','cat':'standaard','badge':'Voordelig','price':'114,30','maxpers':2,
  'video':'videos/comfort.mp4','m2':22,'bed':('Twinbeds','2 eenpersoonsbedden'),'bath':('Badkamer met douche','Inloopdouche'),
  'customslides':['fotos/kamer-comfort-a.webp','fotos/kamer-comfort-b.webp','fotos/kamer-comfort-c.webp','fotos/kamer-comfort-d.webp'],
  'kenmerken':['Circa 22 m&sup2;','Twinbeds (2 eenpersoonsbedden)','Geschikt voor maximaal 2 personen','Zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,'badkamer':['Eigen badkamer met douche','Föhn aanwezig'],'m2key':22},
 {'key':'comfort-3','slug':'comfort-kamer-3-personen','cat':'standaard','badge':'3 personen','price':'123,30','maxpers':3,
  'video':'videos/comfort-3.mp4','slides':4,'photoslug':'comfort-3','m2':22,'bed':('3 eenpersoonsbedden','Ruimte voor drie'),'bath':('Douche en/of bad','Eigen badkamer'),
  'kenmerken':['Circa 22 m&sup2;','3 eenpersoonsbedden','Geschikt voor maximaal 3 personen','Zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,'badkamer':['Eigen badkamer met douche en/of bad','Föhn aanwezig'],'m2key':22},
 {'key':'mindervalide','slug':'mindervalide-kamer','cat':'standaard','badge':'Aangepast','price':'114,30','maxpers':2,
  'video':'videos/mindervalide.mp4','slides':4,'photoslug':'mindervalide','m2':37,'bed':('Twinbeds','+ bedbank'),'bath':('Aangepaste badkamer','Rolstoeltoegankelijk, douche'),
  'kenmerken':['Circa 37 m&sup2;','Twinbeds (2 eenpersoonsbedden)','Bedbank voor extra slaapgelegenheid','Extra brede deuren en ruime indeling voor rolstoel of rollator','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,'badkamer':['Aangepaste, rolstoeltoegankelijke badkamer met douche','Extra beugels en zitje in de douche','Föhn aanwezig'],'m2key':37},
 {'key':'royale','slug':'royale-kamer','cat':'standaard','badge':'Ruimer','price':'123,30','maxpers':2,
  'video':'videos/royale.mp4','slides':4,'photoslug':'royale','m2':25,'bed':('Twin of tweepersoons','Naar keuze'),'bath':('Douche en/of bad','Eigen badkamer'),
  'kenmerken':['Circa 25 m&sup2;','Tweepersoonsbed of twinbeds (2 eenpersoonsbedden)','Geschikt voor maximaal 2 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,'badkamer':['Eigen badkamer met douche en/of bad','Föhn aanwezig'],'m2key':25},
 {'key':'deluxe','slug':'deluxe-kamer','cat':'luxe','badge':'+ Eigen sauna','price':'132,30','maxpers':2,
  'video':'videos/deluxe.mp4','slides':4,'photoslug':'deluxe','m2':25,'bed':('Twin of tweepersoons','Naar keuze'),'bath':('Douche + infraroodsauna','Privé wellness'),
  'kenmerken':['Circa 25 m&sup2;','Tweepersoonsbed of twinbeds (2 eenpersoonsbedden)','Geschikt voor maximaal 2 personen','Zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,'badkamer':['Eigen badkamer met douche','Luxe private infraroodsauna','Föhn aanwezig'],'m2key':25},
 {'key':'junior-suite','slug':'junior-suite','cat':'luxe','badge':'Familie','price':'141,30','maxpers':4,
  'video':None,'poster':'fotos/kamer-junior-suite.webp','customslides':['fotos/kamer-junior-suite.webp','fotos/kamer-junior-suite-2.webp'],
  'm2':37,'bed':('Kingsize bed','+ bedbank'),'bath':('Bad en douche','Eigen badkamer'),
  'kenmerken':['Circa 37 m&sup2;','Tweepersoons kingsize bed','Bedbank voor extra slaapgelegenheid','Geschikt voor maximaal 4 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':['Koelkastje met gratis flesjes water']+FAC_BASE,'badkamer':['Eigen badkamer met bad en douche','Föhn aanwezig'],'m2key':37},
 {'key':'suite','slug':'suite','cat':'luxe','badge':'+ Eigen sauna','price':'150,30','maxpers':4,
  'video':'videos/suite.mp4','slides':4,'photoslug':'suite','m2':40,'bed':('Kingsize bed','+ bedbank'),'bath':('Douche + infraroodsauna','Privé wellness'),
  'kenmerken':['Circa 40 m&sup2;','Tweepersoons kingsize bed','Bedbank voor extra slaapgelegenheid','Geschikt voor maximaal 4 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':['Koelkastje met gratis flesjes water']+FAC_BASE,'badkamer':['Eigen badkamer met douche','Private infraroodsauna','Föhn aanwezig'],'m2key':40},
 {'key':'bruidssuite','slug':'bruidssuite','cat':'luxe','badge':'Premium','price':'177,30','maxpers':2,
  'video':'videos/bruidssuite.mp4','slides':4,'photoslug':'bruidssuite','m2':36,'bed':('Kingsize bed','Tweepersoons'),'bath':('Ligbad + inloopdouche','Luxe badkamer'),
  'kenmerken':['Circa 36 m&sup2;','Tweepersoons kingsize bed','Ruime zithoek met comfortabele stoelen','Badjassen en slippers'],
  'faciliteiten':['Koelkastje met gratis flesjes water']+FAC_BASE,'badkamer':['Luxe badkamer met inloopdouche','Ruim vrijstaand ligbad','Föhn aanwezig'],'m2key':36},
]
BYKEY = {r['key']: r for r in ROOMS}

# ── Arrangementen-content per taal ─────────────────────────────────────
ARRCARDS = {
 'wellness':{'title':{'nl':'Wellnessarrangement','en':'Wellness package','de':'Wellness-Arrangement'},
   'desc':{'nl':'Overnachting, welkomstdrankje, badjas en handdoekpakket, gratis toegang tot de wellness, een drie-gangen diner en uitgebreid ontbijtbuffet.',
           'en':'An overnight stay, welcome drink, bathrobe and towel set, free access to the wellness area, a three-course dinner and an extensive breakfast buffet.',
           'de':'Übernachtung, Willkommensgetränk, Bademantel- und Handtuchset, kostenloser Zugang zum Wellnessbereich, ein Drei-Gänge-Menü und ein reichhaltiges Frühstücksbuffet.'},
   'link':{'nl':'https://visit.asteria.nl/wellness-arrangement','en':'https://visit.asteria.nl/wellness-arrangement-en','de':'https://visit.asteria.nl/wellness-arrangement-de'}},
 'summer':{'title':{'nl':'Happy Summer','en':'Happy Summer','de':'Happy Summer'},
   'desc':{'nl':'Een zomerse welkomstcocktail, ontbijtbuffet en elke avond een heerlijk drie-gangen diner. Zorgeloos genieten van de zomer.',
           'en':'A summery welcome cocktail, breakfast buffet and a delicious three-course dinner every evening. Carefree summer enjoyment.',
           'de':'Ein sommerlicher Willkommenscocktail, Frühstücksbuffet und jeden Abend ein köstliches Drei-Gänge-Menü. Unbeschwerter Sommergenuss.'},
   'link':{'nl':'https://visit.asteria.nl/happy-summer-arrangement','en':'https://visit.asteria.nl/happy-summer-arrangement-en','de':'https://visit.asteria.nl/happy-summer-arrangement-de'}},
 'limburg':{'title':{'nl':'Limburg Arrangement','en':'Limburg package','de':'Limburg-Arrangement'},
   'desc':{'nl':'Ontdek Noord-Limburg op de fiets: drie overnachtingen, elke ochtend ontbijt, elke avond diner en elektrische fietshuur inbegrepen.',
           'en':'Discover North Limburg by bike: three nights, breakfast every morning, dinner every evening and electric bike rental included.',
           'de':'Entdecken Sie Nord-Limburg mit dem Fahrrad: drei Übernachtungen, jeden Morgen Frühstück, jeden Abend Abendessen und E-Bike-Verleih inklusive.'},
   'link':{'nl':'https://www.asteria.nl/arrangementen','en':'https://www.asteria.nl/arrangementen','de':'https://www.asteria.nl/arrangementen'}},
}
# ── FAQ per taal ───────────────────────────────────────────────────────
FAQ = {
 'nl':[('Hoe laat kan ik inchecken en uitchecken?','Inchecken kan vanaf 15:00 uur, uitchecken tot 11:00 uur. Eerder aankomen of later vertrekken is op aanvraag en afhankelijk van de beschikbaarheid mogelijk.'),
       ('Is parkeren gratis?','Ja. U parkeert gratis op ons eigen terrein en er is een afgesloten fietsenstalling beschikbaar.'),
       ('Is het ontbijt inbegrepen?','Geniet \'s ochtends van ons uitgebreide ontbijtbuffet. Het ontbijt is bij veel van onze arrangementen inbegrepen en kunt u bij een losse overnachting eenvoudig bijboeken.'),
       ('Heb ik toegang tot de wellness en fitness?','Als hotelgast heeft u toegang tot onze fitnessruimte. Onze wellness van 300 m² op de Top Floor reserveert u eenvoudig vooraf bij de receptie of via wellnessasteria.nl.'),
       ('__OCC__',None),
       ('Kan ik mijn reservering kosteloos annuleren?','Dat hangt af van het gekozen tarief. Bij een flexibel tarief kunt u kosteloos annuleren; bij een voordeliger niet-restitueerbaar tarief niet. De voorwaarden ziet u tijdens het boeken.')],
 'en':[('What time are check-in and check-out?','Check-in is from 3:00 PM, check-out until 11:00 AM. Earlier arrival or later departure is possible on request, subject to availability.'),
       ('Is parking free?','Yes. You can park free of charge on our own grounds, and a secure bicycle storage is available.'),
       ('Is breakfast included?','Enjoy our extensive breakfast buffet each morning. Breakfast is included in many of our packages and can easily be added to a standalone stay.'),
       ('Do I have access to the wellness and fitness area?','As a hotel guest you have access to our fitness room. Our 300 m² wellness area on the Top Floor can easily be reserved in advance at reception or via wellnessasteria.nl.'),
       ('__OCC__',None),
       ('Can I cancel my reservation free of charge?','That depends on the rate you select. With a flexible rate you can cancel free of charge; with a cheaper non-refundable rate you cannot. You will see the conditions during booking.')],
 'de':[('Wann sind Check-in und Check-out?','Check-in ab 15:00 Uhr, Check-out bis 11:00 Uhr. Eine frühere Anreise oder spätere Abreise ist auf Anfrage und je nach Verfügbarkeit möglich.'),
       ('Ist das Parken kostenlos?','Ja. Sie parken kostenlos auf unserem eigenen Gelände, und ein abschließbarer Fahrradraum steht zur Verfügung.'),
       ('Ist das Frühstück inbegriffen?','Genießen Sie morgens unser reichhaltiges Frühstücksbuffet. Das Frühstück ist in vielen unserer Arrangements enthalten und kann bei einer einzelnen Übernachtung einfach hinzugebucht werden.'),
       ('Habe ich Zugang zum Wellness- und Fitnessbereich?','Als Hotelgast haben Sie Zugang zu unserem Fitnessraum. Unseren 300 m² großen Wellnessbereich im Top Floor reservieren Sie einfach vorab an der Rezeption oder über wellnessasteria.nl.'),
       ('__OCC__',None),
       ('Kann ich meine Reservierung kostenlos stornieren?','Das hängt vom gewählten Tarif ab. Bei einem flexiblen Tarif können Sie kostenlos stornieren, bei einem günstigeren, nicht erstattbaren Tarif nicht. Die Bedingungen sehen Sie während der Buchung.')],
}
def occ_q(name, n, lang):
    if lang=='en':
        return (f'How many guests is the {name} suitable for?', f'The {name} is suitable for up to {n} guest{"s" if n!=1 else ""}. During booking you will immediately see availability for your party.')
    if lang=='de':
        return (f'Für wie viele Personen ist {name} geeignet?', f'{name} ist für bis zu {n} Person{"en" if n!=1 else ""} geeignet. Während der Buchung sehen Sie direkt die Verfügbarkeit für Ihre Gruppe.')
    return (f'Voor hoeveel personen is de {name} geschikt?', f'De {name} is geschikt voor maximaal {n} {"personen" if n!=1 else "persoon"}. Tijdens het boeken ziet u direct de beschikbaarheid voor uw gezelschap.')

# ── Shell-vertaling (NL → EN/DE) via gerichte replacements ─────────────
SHELL_TR = {
 'en':[('>Kamers en Suites</a>','>Rooms & Suites</a>'),('>Omgeving</a>','>Surroundings</a>'),
       ('>Boek nu</button>','>Book now</button>'),('</svg> Menu</span>','</svg> Menu</span>'),
       ('</svg> Bel</a>','</svg> Call</a>'),
       ('>Al onze kamers zijn inclusief</h2>','>All our rooms include</h2>'),
       ('>Gratis WiFi</span>','>Free WiFi</span>'),('>Föhn</span>','>Hairdryer</span>'),
       ('>Flatscreen-tv</span>','>Flatscreen TV</span>'),('>Koffie &amp; thee</span>','>Coffee &amp; tea</span>'),
       ('>Airco</span>','>Air conditioning</span>'),('>Toegang gym</span>','>Gym access</span>'),
       ('>Hotelarrangementen bij dit kamertype</h2>','>Hotel packages for this room type</h2>'),
       ('>Algemene voorwaarden</a>','>Terms & conditions</a>'),
       ('Onderdeel van Van der Sterren Hotels','Part of Van der Sterren Hotels')],
 'de':[('>Kamers en Suites</a>','>Zimmer & Suiten</a>'),('>Omgeving</a>','>Umgebung</a>'),
       ('>Contact</a>','>Kontakt</a>'),
       ('>Boek nu</button>','>Jetzt buchen</button>'),('</svg> Menu</span>','</svg> Menü</span>'),
       ('</svg> Bel</a>','</svg> Anrufen</a>'),
       ('>Al onze kamers zijn inclusief</h2>','>In allen Zimmern inbegriffen</h2>'),
       ('>Gratis WiFi</span>','>Kostenloses WLAN</span>'),('>Föhn</span>','>Föhn</span>'),
       ('>Flatscreen-tv</span>','>Flachbild-TV</span>'),('>Koffie &amp; thee</span>','>Kaffee &amp; Tee</span>'),
       ('>Airco</span>','>Klimaanlage</span>'),('>Toegang gym</span>','>Fitnessraum</span>'),
       ('>Hotelarrangementen bij dit kamertype</h2>','>Hotelarrangements für diesen Zimmertyp</h2>'),
       ('>Algemene voorwaarden</a>','>AGB</a>'),
       ('Onderdeel van Van der Sterren Hotels','Teil der Van der Sterren Hotels')],
}
def shell(block, lang):
    if lang == 'nl':
        return block
    for a, b in SHELL_TR[lang]:
        block = block.replace(a, b)
    return block

def li(items): return '\n'.join(f'                <li>{x}</li>' for x in items)

def slides_for(r):
    if r.get('customslides'):
        return r['customslides']
    return [f"fotos/room-{r['photoslug']}-{i}.webp" for i in range(1, r.get('slides', 4) + 1)]

def build_types_list(current_key, lang):
    suf = SUFFIX[lang]
    rows = []
    for r in ROOMS:
        cur = r['key'] == current_key
        thumb = r.get('thumb') or slides_for(r)[0]
        nm = NAME[r['key']][lang]
        chips = ''.join(f'<span>{c}</span>' for c in FEAT[r['key']][lang])
        if cur:
            badge = f'<span class="room-row__badge current">{ui("current",lang)}</span>'
            actions = (f'<a class="btn-primary" href="#" onclick="window.openBooking(\'{r["key"]}\');return false;"'
                       f' data-track-cta="types_{r["key"]}">{ui("reserve",lang)}</a>')
            rowcls = 'room-row is-current'
        else:
            badge = f'<span class="room-row__badge">{tr(r["badge"],lang)}</span>'
            actions = (f'<a class="btn-ghost" href="/{r["slug"]}{suf}">{ui("details",lang)}</a>\n'
                       f'          <a class="btn-primary" href="#" onclick="window.openBooking(\'{r["key"]}\');return false;"'
                       f' data-track-cta="types_{r["key"]}">{ui("reserve",lang)}</a>')
            rowcls = 'room-row'
        rows.append(f'''      <article class="{rowcls}" data-cat="{r['cat']}">
        <img class="room-row__img" src="{thumb}" alt="{nm}" loading="lazy">
        <div>
          <h3 class="room-row__name">{nm} {badge}</h3>
          <p class="room-row__desc">{SHORT[r['key']][lang]}</p>
          <div class="room-row__feat">{chips}</div>
        </div>
        <div class="room-row__actions">
          {actions}
        </div>
      </article>''')
    return '\n\n'.join(rows)

def lang_switcher(slug, lang):
    return f'''/* ── Taalwisselaar ── */
(function () {{
  var sel = document.querySelector('.lang-nav');
  if (!sel) return;
  sel.value = '{lang}';
  sel.addEventListener('change', function () {{
    var urls = {{ 'nl': '/{slug}', 'en': '/{slug}-en', 'de': '/{slug}-de' }};
    if (urls[sel.value]) window.location.href = urls[sel.value];
  }});
}}())'''

_SW_RE = re.compile(r'/\* ── Taalwisselaar ── \*/\n\(function \(\) \{.*?\}\(\)\)', re.S)
def scripts_for(slug, lang):
    return _SW_RE.sub(lambda m: lang_switcher(slug, lang), SCRIPTS)

def nav_for(lang):
    block = shell(NAV, lang)
    # juiste taaloptie geselecteerd
    block = block.replace('<option value="nl" selected>nl</option>', '<option value="nl">nl</option>')
    block = block.replace(f'<option value="{lang}">{lang}</option>', f'<option value="{lang}" selected>{lang}</option>')
    return block

def arr_for(lang):
    cards = []
    for k in ('wellness','summer','limburg'):
        c = ARRCARDS[k]
        img = {'wellness':'fotos/arr-c-wellness.webp','summer':'fotos/hero-zomer.webp','limburg':'fotos/omgeving-fietsers.webp'}[k]
        cards.append(f'''      <article class="arr__card">
        <img src="{img}" alt="{c['title'][lang]}" loading="lazy">
        <div class="arr__body">
          <h3>{c['title'][lang]}</h3>
          <p>{c['desc'][lang]}</p>
          <a class="btn-ghost" href="{c['link'][lang]}">{ui('arr_cta',lang)}</a>
        </div>
      </article>''')
    return f'''<!-- ══ ARRANGEMENTEN ═════════════════════════════════════════ -->
<section class="arr">
  <div class="wrap">
    <div class="arr__head">
      <h2>{ui('arr_h',lang)}</h2>
    </div>
    <div class="arr__grid">
{chr(10).join(cards)}
    </div>
  </div>
</section>
'''

def faq_for(r, lang):
    items = []
    for q, a in FAQ[lang]:
        if q == '__OCC__':
            q, a = occ_q(NAME[r['key']][lang], r['maxpers'], lang)
        items.append(f'''      <details>
        <summary>{q}</summary>
        <div class="faq__a">{a}</div>
      </details>''')
    return f'''<!-- ══ FAQ ═══════════════════════════════════════════════════ -->
<section class="faq">
  <div class="wrap">
    <div class="faq__head">
      <h2>{ui('faq_h',lang)}</h2>
    </div>
    <div class="faq__list">
{chr(10).join(items)}
    </div>
  </div>
</section>
'''

def build_page(r, lang):
    suf = SUFFIX[lang]
    slug = r['slug']
    name = NAME[r['key']][lang]
    price = r['price']
    poster = r.get('poster') or slides_for(r)[0]
    descs = '\n        '.join(f'<p>{p}</p>' for p in DESC[r['key']][lang])
    bed = (tr(r['bed'][0], lang), tr(r['bed'][1], lang))
    bath = (tr(r['bath'][0], lang), tr(r['bath'][1], lang))
    kenmerken = [area(r['m2key'], lang) if x.startswith('Circa ') else tr(x, lang) for x in r['kenmerken']]
    faciliteiten = [tr(x, lang) for x in r['faciliteiten']]
    badkamer = [tr(x, lang) for x in r['badkamer']]
    if r.get('video'):
        hero_media = (f'  <video class="hero__video" autoplay muted loop playsinline poster="{poster}">\n'
                      f'    <source src="{r["video"]}" type="video/mp4">\n  </video>')
    else:
        hero_media = f'  <img class="hero__video" src="{poster}" alt="{name}">'
    slide_html = []
    for i, s in enumerate(slides_for(r)):
        lazy = '' if i == 0 else ' loading="lazy"'
        slide_html.append(f'        <div class="slider__slide"><img src="{s}" alt="{name}"{lazy}></div>')
    slide_html = '\n'.join(slide_html)
    acc = f'''        <div class="acc">
          <details>
            <summary>{ui('kenmerken',lang)}</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(kenmerken)}
              </ul>
            </div>
          </details>
          <details>
            <summary>{ui('faciliteiten',lang)}</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(faciliteiten)}
              </ul>
            </div>
          </details>
          <details>
            <summary>{ui('badkamer',lang)}</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(badkamer)}
              </ul>
            </div>
          </details>
        </div>'''
    alturls = ''.join(f'  <link rel="alternate" hreflang="{lg}" href="https://visit.asteria.nl/{slug}{SUFFIX[lg]}">\n' for lg in ('nl','en','de'))
    page = f'''<!DOCTYPE html>
<html lang="{HTMLLANG[lang]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | Hotel Asteria Venray</title>
  <link rel="icon" href="/favicon.ico">
  <meta name="description" content="{DESC[r['key']][lang][0]}">

  <link rel="canonical" href="https://visit.asteria.nl/{slug}{suf}">
{alturls}  <link rel="alternate" hreflang="x-default" href="https://visit.asteria.nl/{slug}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{name} | Hotel Asteria Venray">
  <meta property="og:description" content="{DESC[r['key']][lang][0]}">
  <meta property="og:image" content="https://visit.asteria.nl/{poster}">
  <meta property="og:url" content="https://visit.asteria.nl/{slug}{suf}">
  <meta property="og:locale" content="{OGLOCALE[lang]}">
  <meta property="og:site_name" content="Hotel Asteria Venray">

  <link rel="preload" as="image" href="{poster}" type="image/webp">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Electrolize&family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="brand.css">

  <!-- GA4 + Google Ads -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DPCP945DCG"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-DPCP945DCG', {{ linker: {{ domains: ['asteria.nl', 'visit.asteria.nl'] }} }});
    gtag('config', 'AW-998609513');
    window.GA_ADS_LABEL = 'AW-998609513/t8vbCLm6i7IcEOmkltwD';
  </script>

{MEWS_HEAD}

{STYLE}
  <style>
{BK_CSS}
  </style>
</head>
<body>

{nav_for(lang)}

<!-- ══ HERO ══════════════════════════════════════════════════ -->
<section class="hero" id="hero">
{hero_media}
  <div class="hero__overlay"></div>
  <div class="hero__inner">
    <h1 class="hero__title">{name}</h1>
  </div>
</section>

<!-- ══ BOEKBALK ══════════════════════════════════════════════ -->
<div class="wrap">
  <div class="bookbar">
    <div class="bookbar__card">
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('gasten',lang)}</span>
        <select class="bookbar__value" id="bbGuests">
          <option value="2">{ui('pers2',lang)}</option>
          <option value="1">{ui('pers1',lang)}</option>
        </select>
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('aankomst',lang)}</span>
        <input class="bookbar__value" type="date" id="bbStart">
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('vertrek',lang)}</span>
        <input class="bookbar__value" type="date" id="bbEnd">
      </div>
      <button class="bookbar__btn" onclick="window.openBooking('{r['key']}')" data-track-cta="bookbar">{ui('availability',lang)}</button>
    </div>
  </div>
</div>

<!-- ══ KAMER-INTRO ═══════════════════════════════════════════ -->
<div class="wrap">
  <nav class="crumb" aria-label="Kruimelpad">
    <a href="https://www.asteria.nl">Hotel Asteria</a> &nbsp;/&nbsp;
    <a href="/kamertypes{suf}">{ui('crumb_rooms',lang)}</a> &nbsp;/&nbsp;
    <span>{name}</span>
  </nav>
</div>

<section class="intro">
  <div class="wrap">
    <div class="intro__grid">
      <div class="intro__text">
        <span class="section-eyebrow">{ui('eyebrow',lang)}</span>
        <h2 class="title">{name}</h2>
        {descs}

{acc}
        <p style="font-size:12px;color:#9a9a95;margin-top:22px;">{ui('disclaimer',lang)}</p>
      </div>

      <aside class="spec-card">
        <ul class="spec-card__list">
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_M2}</span>
            <span class="spec-card__txt"><strong>{area(r['m2key'],lang)}</strong><span>{ui('spec_area',lang)}</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_BED}</span>
            <span class="spec-card__txt"><strong>{bed[0]}</strong><span>{bed[1]}</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_PERS}</span>
            <span class="spec-card__txt"><strong>{maxg(r['maxpers'],lang)}</strong><span>{ui('spec_occ',lang)}</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_BATH}</span>
            <span class="spec-card__txt"><strong>{bath[0]}</strong><span>{bath[1]}</span></span>
          </li>
        </ul>
        <div class="spec-card__price">
          {ui('price_label',lang)}
          <b>&euro;{price}</b>
        </div>
        <a class="btn-primary" href="#" onclick="window.openBooking('{r['key']}');return false;" data-track-cta="intro_reserve">{ui('reserve_direct',lang)}</a>
      </aside>
    </div>
  </div>
</section>

<!-- ══ IN BEELD — slider ═════════════════════════════════════ -->
<section class="gallery">
  <div class="wrap">
    <div class="slider" id="comfortSlider">
      <div class="slider__track" id="sliderTrack">
{slide_html}
      </div>
      <button class="slider__arrow slider__arrow--prev" id="sliderPrev" aria-label="Vorige foto"><span>&#8249;</span></button>
      <button class="slider__arrow slider__arrow--next" id="sliderNext" aria-label="Volgende foto"><span>&#8250;</span></button>
      <div class="slider__dots" id="sliderDots"></div>
    </div>
  </div>
</section>

{shell(INCLUDED, lang)}

<!-- ══ KAMERTYPES ════════════════════════════════════════════ -->
<section class="types">
  <div class="wrap">
    <div class="types__head">
      <h2>{ui('types_h',lang)}</h2>
      <p>{ui('types_sub',lang)}</p>
    </div>

    <div class="tabs">
      <button class="tab is-active" data-cat="all">{ui('tab_all',lang)}</button>
      <button class="tab" data-cat="standaard">{ui('tab_std',lang)}</button>
      <button class="tab" data-cat="luxe">{ui('tab_lux',lang)}</button>
    </div>

    <div id="roomList">
{build_types_list(r['key'], lang)}
    </div>
  </div>
</section>

{arr_for(lang)}
{faq_for(r, lang)}
<!-- ══ STICKY MOBILE CTA ═════════════════════════════════════ -->
<div class="sticky-cta">
  <div class="sticky-cta__price">{name}<b>{ui('sticky_from',lang)} &euro;{price}</b></div>
  <a class="btn-primary" href="#" onclick="window.openBooking('{r['key']}');return false;" data-track-cta="sticky">{ui('reserve',lang)}</a>
</div>

{bk_localize(BK_MARKUP, lang)}

{shell(FOOTER, lang)}

{scripts_for(slug, lang)}

<script>
{booking_bundle(lang)}
</script>

</body>
</html>
'''
    return page

# ── Overzichtspagina /kamertypes ───────────────────────────────────────
def build_overview(lang):
    suf = SUFFIX[lang]
    hero_img = 'fotos/room-suite-1.webp'
    checklist = ''.join(f'<li>{x}</li>' for x in OVLIST[lang])
    alturls = ''.join(f'  <link rel="alternate" hreflang="{lg}" href="https://visit.asteria.nl/kamertypes{SUFFIX[lg]}">\n' for lg in ('nl','en','de'))
    OV_CSS = '''  <style>
    .ov-hero { min-height: 64vh; }
    .ov-intro { text-align: center; max-width: 760px; margin: 0 auto; padding: 80px 0 10px; }
    .ov-intro .section-eyebrow { color: #c23435; }
    .ov-intro h2 { font-family:'Electrolize',sans-serif; text-transform:uppercase; letter-spacing:.03em; font-weight:400; font-size:clamp(28px,3.6vw,42px); line-height:1.12; margin-bottom:22px; }
    .ov-intro p { font-weight:300; font-size:16px; line-height:1.75; color:#475569; }
    .ov-feat { max-width:900px; margin:50px auto 0; padding-bottom:80px; text-align:center; }
    .ov-feat h3 { font-family:'Electrolize',sans-serif; text-transform:uppercase; letter-spacing:.03em; font-weight:400; font-size:clamp(22px,2.6vw,30px); margin-bottom:16px; }
    .ov-feat p { font-weight:300; font-size:16px; line-height:1.7; color:#475569; max-width:640px; margin:0 auto 30px; }
    .ov-checklist { list-style:none; display:grid; grid-template-columns:repeat(2,1fr); gap:14px 40px; max-width:680px; margin:0 auto; text-align:left; }
    .ov-checklist li { position:relative; padding-left:30px; font-weight:300; font-size:15px; color:#1a1a1a; }
    .ov-checklist li::before { content:''; position:absolute; left:2px; top:5px; width:14px; height:9px; border-left:2px solid #c23435; border-bottom:2px solid #c23435; transform:rotate(-45deg); }
    .promo { position:relative; max-width:1100px; margin:0 auto; padding:0 24px; }
    .promo__inner { position:relative; }
    .promo__img { width:100%; height:460px; object-fit:cover; border-radius:18px; display:block; }
    .promo__card { position:absolute; left:0; top:50%; transform:translateY(-50%); background:#242424; color:#fff; padding:46px 42px; border-radius:16px; max-width:480px; }
    .promo__card .section-eyebrow { color:#e8923a; }
    .promo__card h2 { font-family:'Electrolize',sans-serif; text-transform:uppercase; letter-spacing:.03em; font-weight:400; font-size:clamp(24px,2.8vw,32px); color:#fff; margin-bottom:16px; }
    .promo__card p { font-weight:300; font-size:15px; line-height:1.7; color:rgba(255,255,255,.85); margin-bottom:26px; }
    .promo__btns { display:flex; gap:12px; flex-wrap:wrap; }
    .promo__btns .btn-primary { width:auto; padding:13px 24px; }
    .promo__btns .btn-light { display:inline-block; text-align:center; border:1px solid rgba(255,255,255,.55); color:#fff; background:transparent; border-radius:10px; padding:13px 24px; font-size:14px; font-family:'Montserrat',sans-serif; text-decoration:none; transition:all .2s; cursor:pointer; }
    .promo__btns .btn-light:hover { background:#fff; color:#242424; }
    @media (max-width: 860px) {
      .ov-checklist { grid-template-columns:1fr; max-width:340px; gap:12px; }
      .promo__img { height:340px; }
      .promo__card { position:static; transform:none; max-width:none; margin-top:-60px; margin-left:16px; margin-right:16px; }
    }
  </style>'''
    page = f'''<!DOCTYPE html>
<html lang="{HTMLLANG[lang]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ui('ov_hero',lang)} | Hotel Asteria Venray</title>
  <link rel="icon" href="/favicon.ico">
  <meta name="description" content="{ui('ov_p',lang)}">

  <link rel="canonical" href="https://visit.asteria.nl/kamertypes{suf}">
{alturls}  <link rel="alternate" hreflang="x-default" href="https://visit.asteria.nl/kamertypes">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{ui('ov_hero',lang)} | Hotel Asteria Venray">
  <meta property="og:description" content="{ui('ov_p',lang)}">
  <meta property="og:image" content="https://visit.asteria.nl/{hero_img}">
  <meta property="og:url" content="https://visit.asteria.nl/kamertypes{suf}">
  <meta property="og:locale" content="{OGLOCALE[lang]}">
  <meta property="og:site_name" content="Hotel Asteria Venray">

  <link rel="preload" as="image" href="{hero_img}" type="image/webp">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Electrolize&family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="brand.css">

  <!-- GA4 + Google Ads -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DPCP945DCG"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-DPCP945DCG', {{ linker: {{ domains: ['asteria.nl', 'visit.asteria.nl'] }} }});
    gtag('config', 'AW-998609513');
    window.GA_ADS_LABEL = 'AW-998609513/t8vbCLm6i7IcEOmkltwD';
  </script>

{MEWS_HEAD}

{STYLE}
  <style>
{BK_CSS}
  </style>
{OV_CSS}
</head>
<body>

{nav_for(lang)}

<!-- ══ HERO ══════════════════════════════════════════════════ -->
<section class="hero ov-hero" id="hero">
  <img class="hero__video" src="{hero_img}" alt="Hotel Asteria — {ui('ov_hero',lang)}">
  <div class="hero__overlay"></div>
  <div class="hero__inner">
    <h1 class="hero__title">{ui('ov_hero',lang)}</h1>
  </div>
</section>

<!-- ══ BOEKBALK ══════════════════════════════════════════════ -->
<div class="wrap">
  <div class="bookbar">
    <div class="bookbar__card">
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('gasten',lang)}</span>
        <select class="bookbar__value" id="bbGuests">
          <option value="2">{ui('pers2',lang)}</option>
          <option value="1">{ui('pers1',lang)}</option>
        </select>
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('aankomst',lang)}</span>
        <input class="bookbar__value" type="date" id="bbStart">
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">{ui('vertrek',lang)}</span>
        <input class="bookbar__value" type="date" id="bbEnd">
      </div>
      <button class="bookbar__btn" onclick="window.openBooking()" data-track-cta="bookbar">{ui('availability',lang)}</button>
    </div>
  </div>
</div>

<!-- ══ BREADCRUMB ════════════════════════════════════════════ -->
<div class="wrap">
  <nav class="crumb" aria-label="Kruimelpad">
    <a href="https://www.asteria.nl">Hotel Asteria</a> &nbsp;/&nbsp;
    <span>{ui('crumb_overview',lang)}</span>
  </nav>
</div>

<!-- ══ INTRO ═════════════════════════════════════════════════ -->
<section class="ov-intro">
  <div class="wrap">
    <span class="section-eyebrow">{ui('ov_eyebrow',lang)}</span>
    <h2>{ui('ov_h',lang)}</h2>
    <p>{ui('ov_p',lang)}</p>
  </div>
</section>

<section class="ov-feat">
  <div class="wrap">
    <h3>{ui('ov_sub_h',lang)}</h3>
    <p>{ui('ov_sub_p',lang)}</p>
    <ul class="ov-checklist">{checklist}</ul>
  </div>
</section>

<!-- ══ KAMERTYPES ════════════════════════════════════════════ -->
<section class="types" style="padding-top:0;">
  <div class="wrap">
    <div class="tabs">
      <button class="tab is-active" data-cat="all">{ui('tab_all',lang)}</button>
      <button class="tab" data-cat="standaard">{ui('tab_std',lang)}</button>
      <button class="tab" data-cat="luxe">{ui('tab_lux',lang)}</button>
    </div>

    <div id="roomList">
{build_types_list(None, lang)}
    </div>
  </div>
</section>

<!-- ══ PROMO ═════════════════════════════════════════════════ -->
<section class="section" style="padding:30px 0 90px;">
  <div class="promo">
    <div class="promo__inner">
      <img class="promo__img" src="fotos/wellness-spa.webp" alt="{ui('promo_h',lang)}" loading="lazy">
      <div class="promo__card">
        <span class="section-eyebrow">{ui('promo_eyebrow',lang)}</span>
        <h2>{ui('promo_h',lang)}</h2>
        <p>{ui('promo_p',lang)}</p>
        <div class="promo__btns">
          <a class="btn-light" href="https://www.asteria.nl/arrangementen">{ui('promo_btn1',lang)}</a>
          <a class="btn-primary" href="#" onclick="window.openBooking();return false;" data-track-cta="promo">{ui('promo_btn2',lang)}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ══ FAQ ═══════════════════════════════════════════════════ -->
<section class="faq">
  <div class="wrap">
    <div class="faq__head">
      <h2>{ui('faq_h',lang)}</h2>
    </div>
    <div class="faq__list">
      <details>
        <summary>{ui('ov_faq_q',lang)}</summary>
        <div class="faq__a">{ui('ov_faq_a',lang)}</div>
      </details>
{faq_items_overview(lang)}
    </div>
  </div>
</section>

{bk_localize(BK_MARKUP, lang)}

{shell(FOOTER, lang)}

{scripts_for('kamertypes', lang)}

<script>
{booking_bundle(lang)}
</script>

</body>
</html>
'''
    return page

def faq_items_overview(lang):
    out = []
    for q, a in FAQ[lang]:
        if q == '__OCC__':
            continue
        out.append(f'''      <details>
        <summary>{q}</summary>
        <div class="faq__a">{a}</div>
      </details>''')
    return '\n'.join(out)

# ── Schrijf pagina's ───────────────────────────────────────────────────
written = []
for lang in ('nl', 'en', 'de'):
    out = os.path.join(BASE, 'kamertypes' + SUFFIX[lang] + '.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build_overview(lang))
    written.append(os.path.basename(out))
for r in ROOMS:
    for lang in ('nl', 'en', 'de'):
        if r['key'] == 'comfort' and lang == 'nl':
            continue  # comfort-kamer.html niet overschrijven
        out = os.path.join(BASE, r['slug'] + SUFFIX[lang] + '.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(build_page(r, lang))
        written.append(os.path.basename(out))

# ── comfort-kamer.html (NL) bijwerken ──────────────────────────────────
comfort = html
new_list = '    <div id="roomList">\n' + build_types_list('comfort', 'nl') + '\n    </div>'
comfort = re.sub(r'    <div id="roomList">.*?\n    </div>', lambda m: new_list, comfort, count=1, flags=re.S)
comfort = comfort.replace(
    '''        <div class="spec-card__price">
          Direct boeken via het hotel
          <b>Beste prijsgarantie</b>
        </div>''',
    f'''        <div class="spec-card__price">
          {ui('price_label','nl')}
          <b>&euro;114,30</b>
        </div>''')
comfort = comfort.replace('<div class="sticky-cta__price">Comfort kamer<b>Beste prijsgarantie</b></div>',
                          "<div class=\"sticky-cta__price\">Comfort kamer<b>Vanaf &euro;114,30</b></div>")
# hreflang en/de → eigen vertaalde pagina's
comfort = comfort.replace('<link rel="alternate" hreflang="en" href="https://www.asteria.nl/en/rooms/comfort-room">',
                          '<link rel="alternate" hreflang="en" href="https://visit.asteria.nl/comfort-kamer-en">')
comfort = comfort.replace('<link rel="alternate" hreflang="de" href="https://www.asteria.nl/de/zimmer/komfort-zimmer">',
                          '<link rel="alternate" hreflang="de" href="https://visit.asteria.nl/comfort-kamer-de">')
# taalwisselaar → eigen vertaalde pagina's
comfort = _SW_RE.sub(lambda m: lang_switcher('comfort-kamer', 'nl'), comfort)
comfort = comfort.replace('<a href="https://www.asteria.nl/kamers">Kamers en Suites</a>',
                          '<a href="/kamertypes">Kamers en Suites</a>')
# Boekingsmodule in comfort-kamer.html injecteren (idempotent via markers)
for _tag in ('BK-HEAD', 'BK-CSS', 'BK-MARKUP', 'BK-JS'):
    comfort = re.sub('\\n?<!--' + _tag + '-->.*?<!--/' + _tag + '-->', '', comfort, flags=re.S)
comfort = comfort.replace('  </script>\n\n  <style>',
    '  </script>\n\n<!--BK-HEAD-->\n' + MEWS_HEAD + '\n<!--/BK-HEAD-->\n\n  <style>', 1)
comfort = comfort.replace('  </style>\n</head>',
    '  </style>\n<!--BK-CSS--><style>\n' + BK_CSS + '\n  </style><!--/BK-CSS-->\n</head>', 1)
comfort = comfort.replace('<!-- ══ FOOTER',
    '<!--BK-MARKUP-->\n' + BK_MARKUP + '\n<!--/BK-MARKUP-->\n\n<!-- ══ FOOTER', 1)
comfort = comfort.replace('\n</body>',
    '\n<!--BK-JS--><script>\n' + booking_bundle('nl') + '\n</script><!--/BK-JS-->\n</body>', 1)
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(comfort)

if MISSING:
    print('!! ONVERTAALDE TERMEN:', MISSING)
else:
    print('Alle termen vertaald.')
print(f'Gegenereerd: {len(written)} pagina\'s')
print('comfort-kamer.html bijgewerkt')
