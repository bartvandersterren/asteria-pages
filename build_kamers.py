#!/usr/bin/env python3
"""Genereer kamerdetailpagina's voor Hotel Asteria (visit.asteria.nl).

Hergebruikt de gedeelde shell (CSS, nav, inclusief-blok, arrangementen,
footer, scripts) uit comfort-kamer.html en vult per kamer de unieke
secties in. comfort-kamer.html zelf wordt NIET overschreven; wel wordt de
'Verschillende kamertypes'-lijst + prijs + sticky-CTA erin bijgewerkt.
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

# ── Iconen voor specs-kaart ────────────────────────────────────────────
IC_M2   = '<svg viewBox="0 0 24 24"><path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/></svg>'
IC_BED  = '<svg viewBox="0 0 24 24"><path d="M2 17v-4a2 2 0 012-2h16a2 2 0 012 2v4M2 17v3M22 17v3M4 11V8a2 2 0 012-2h12a2 2 0 012 2v3"/></svg>'
IC_PERS = '<svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="3"/><circle cx="16" cy="8" r="2.5"/><path d="M3 20v-1a5 5 0 015-5h2a5 5 0 015 5v1M16 14a4 4 0 014 4v2"/></svg>'
IC_BATH = '<svg viewBox="0 0 24 24"><path d="M4 12h16M6 12V6a2 2 0 012-2h0a2 2 0 012 2M4 12v3a5 5 0 005 5h6a5 5 0 005-5v-3"/></svg>'

FAC_BASE = ['Airconditioning', 'Koffie- en theefaciliteiten', 'Flatscreen-tv', 'Föhn',
            'Gratis WiFi', 'Toegang tot de fitnessruimte']

# ── Kameromschrijvingen ────────────────────────────────────────────────
ROOMS = [
 {'key':'comfort','slug':'comfort-kamer','name':'Comfort kamer','cat':'standaard',
  'badge':'Voordelig','price':'114,30','maxpers':2,
  'short':'Een comfortabele kamer voor twee personen met alles wat u nodig hebt voor een ontspannen verblijf.',
  'feat':['~22 m&sup2;','Twinbeds','Douche','Airco','WiFi'],
  'thumb':'fotos/kamer-comfort-a.webp'},

 {'key':'comfort-3','slug':'comfort-kamer-3-personen','name':'Comfort kamer 3 personen','cat':'standaard',
  'badge':'3 personen','price':'123,30','maxpers':3,
  'titletag':'22m² · ruimte voor drie',
  'video':'videos/comfort-3.mp4','slides':4,'photoslug':'comfort-3',
  'm2':22,'bed':('3 eenpersoonsbedden','Ruimte voor drie'),
  'bath':('Douche en/of bad','Eigen badkamer'),
  'desc':['Onze 3-persoons Comfort kamer biedt extra ruimte voor families of vrienden die samen op pad gaan. Alles is aanwezig voor een aangenaam en zorgeloos verblijf in het groene Noord-Limburg.',
          'Drie eenpersoonsbedden, een eigen badkamer en een fijne zithoek maken deze kamer ideaal voor wie samen reist.'],
  'kenmerken':['Circa 22 m&sup2;','3 eenpersoonsbedden','Geschikt voor maximaal 3 personen','Zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,
  'badkamer':['Eigen badkamer met douche en/of bad','Föhn aanwezig'],
  'short':'Extra ruimte voor families of vrienden — drie eenpersoonsbedden en alle gemakken.',
  'feat':['~22 m&sup2;','3 bedden','Max. 3','Douche/bad']},

 {'key':'mindervalide','slug':'mindervalide-kamer','name':'Mindervalide kamer','cat':'standaard',
  'badge':'Aangepast','price':'114,30','maxpers':2,
  'titletag':'37m² · aangepast & ruim',
  'video':'videos/mindervalide.mp4','slides':4,'photoslug':'mindervalide',
  'm2':37,'bed':('Twinbeds','+ bedbank'),
  'bath':('Aangepaste badkamer','Rolstoeltoegankelijk, douche'),
  'desc':['Onze aangepaste kamer is speciaal ontworpen voor gasten met beperkte mobiliteit. Ook ons restaurant en terras zijn rolstoelvriendelijk, zodat u tijdens uw verblijf zorgeloos kunt genieten van een heerlijk diner en de gastvrijheid van Asteria.',
          'Een ruime indeling, extra brede deuren en een aangepaste badkamer zorgen voor comfort en zelfstandigheid.'],
  'kenmerken':['Circa 37 m&sup2;','Twinbeds (2 eenpersoonsbedden)','Bedbank voor extra slaapgelegenheid','Extra brede deuren en ruime indeling voor rolstoel of rollator','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,
  'badkamer':['Aangepaste, rolstoeltoegankelijke badkamer met douche','Extra beugels en zitje in de douche','Föhn aanwezig'],
  'short':'Ruime, aangepaste kamer voor gasten met beperkte mobiliteit, met rolstoeltoegankelijke badkamer.',
  'feat':['~37 m&sup2;','Aangepast','Twinbeds','Bedbank']},

 {'key':'royale','slug':'royale-kamer','name':'Royale kamer','cat':'standaard',
  'badge':'Ruimer','price':'123,30','maxpers':2,
  'titletag':'25m² · ruime zithoek',
  'video':'videos/royale.mp4','slides':4,'photoslug':'royale',
  'm2':25,'bed':('Twin of tweepersoons','Naar keuze'),
  'bath':('Douche en/of bad','Eigen badkamer'),
  'desc':['Onze Royale kamers zijn groter dan de Comfort kamers en bieden net dat beetje extra. Het ruime gevoel en de comfortabele zithoek maken deze kamer ideaal voor wie iets meer luxe wil tijdens het verblijf.',
          'Kies voor een tweepersoonsbed of twinbeds en geniet van de extra ruimte en een eigen badkamer met douche of bad.'],
  'kenmerken':['Circa 25 m&sup2;','Tweepersoonsbed of twinbeds (2 eenpersoonsbedden)','Geschikt voor maximaal 2 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,
  'badkamer':['Eigen badkamer met douche en/of bad','Föhn aanwezig'],
  'short':'Ruimer dan de Comfort kamer, met een comfortabele zithoek en de keuze voor een bad.',
  'feat':['~25 m&sup2;','Bad of douche','Zithoek','Airco']},

 {'key':'deluxe','slug':'deluxe-kamer','name':'Deluxe kamer','cat':'luxe',
  'badge':'+ Eigen sauna','price':'132,30','maxpers':2,
  'titletag':'25m² · infraroodsauna',
  'video':'videos/deluxe.mp4','slides':4,'photoslug':'deluxe',
  'm2':25,'bed':('Twin of tweepersoons','Naar keuze'),
  'bath':('Douche + infraroodsauna','Privé wellness'),
  'desc':['Onze Deluxe kamers hebben alles voor een luxe verblijf in Noord-Limburg. De private infraroodsauna in de badkamer maakt deze kamer ideaal voor wie écht wil ontspannen — een kleine wellness-ervaring op uw eigen kamer.',
          'Naast de eigen sauna geniet u van een comfortabele zithoek en alle gemakken binnen handbereik.'],
  'kenmerken':['Circa 25 m&sup2;','Tweepersoonsbed of twinbeds (2 eenpersoonsbedden)','Geschikt voor maximaal 2 personen','Zithoek met comfortabele stoelen'],
  'faciliteiten':FAC_BASE,
  'badkamer':['Eigen badkamer met douche','Luxe private infraroodsauna','Föhn aanwezig'],
  'short':'Een privé infraroodsauna op de kamer — wellness begint bij u aan de deur.',
  'feat':['~25 m&sup2;','Infraroodsauna','Douche','Zithoek']},

 {'key':'junior-suite','slug':'junior-suite','name':'Junior suite','cat':'luxe',
  'badge':'Familie','price':'141,30','maxpers':4,
  'titletag':'37m² · kingsize bed · bedbank',
  'video':None,'poster':'fotos/kamer-junior-suite.webp',
  'customslides':['fotos/kamer-junior-suite.webp','fotos/kamer-junior-suite-2.webp'],
  'm2':37,'bed':('Kingsize bed','+ bedbank'),
  'bath':('Bad en douche','Eigen badkamer'),
  'desc':['Onze ruime Junior Suites bieden de luxe van ruimte met een grote zithoek om even heerlijk te ontspannen na een dag op pad. Ideaal voor wie net dat beetje extra wil tijdens het verblijf in Noord-Limburg.',
          'Met een kingsize bed en een bedbank voor extra slaapgelegenheid is de Junior Suite ook perfect voor families.'],
  'kenmerken':['Circa 37 m&sup2;','Tweepersoons kingsize bed','Bedbank voor extra slaapgelegenheid','Geschikt voor maximaal 4 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':['Koelkastje met gratis flesjes water'] + FAC_BASE,
  'badkamer':['Eigen badkamer met bad en douche','Föhn aanwezig'],
  'short':'Kingsize bed, bad en een ruime zithoek met bedbank voor extra slaapgelegenheid.',
  'feat':['~37 m&sup2;','Kingsize','Bedbank','Bad & douche']},

 {'key':'suite','slug':'suite','name':'Suite','cat':'luxe',
  'badge':'+ Eigen sauna','price':'150,30','maxpers':4,
  'titletag':'40m² · kingsize bed · infraroodsauna',
  'video':'videos/suite.mp4','slides':4,'photoslug':'suite',
  'm2':40,'bed':('Kingsize bed','+ bedbank'),
  'bath':('Douche + infraroodsauna','Privé wellness'),
  'desc':['Beleef Asteria in onze meest ruime en luxe kamer. Met een eigen infraroodsauna, een ruime zithoek en alle gemakken binnen handbereik is de Suite dé plek om volledig tot rust te komen — meer dan een hotelkamer, een complete ervaring.',
          'Een kingsize bed en bedbank bieden ruimte voor maximaal vier personen.'],
  'kenmerken':['Circa 40 m&sup2;','Tweepersoons kingsize bed','Bedbank voor extra slaapgelegenheid','Geschikt voor maximaal 4 personen','Ruime zithoek met comfortabele stoelen'],
  'faciliteiten':['Koelkastje met gratis flesjes water'] + FAC_BASE,
  'badkamer':['Eigen badkamer met douche','Private infraroodsauna','Föhn aanwezig'],
  'short':'Onze meest ruime kamer met eigen infraroodsauna en royale zithoek.',
  'feat':['~40 m&sup2;','Kingsize','Infraroodsauna','Bedbank']},

 {'key':'bruidssuite','slug':'bruidssuite','name':'Bruidssuite','cat':'luxe',
  'badge':'Premium','price':'177,30','maxpers':2,
  'titletag':'36m² · luxe ligbad · inloopdouche',
  'video':'videos/bruidssuite.mp4','slides':4,'photoslug':'bruidssuite',
  'm2':36,'bed':('Kingsize bed','Tweepersoons'),
  'bath':('Ligbad + inloopdouche','Luxe badkamer'),
  'desc':['Onze Bruidssuite is ontworpen voor bijzondere momenten. Of u nu net getrouwd bent of een romantisch weekend viert, geniet samen van de luxe, de rust en de warme sfeer die Asteria zo kenmerkt.',
          'Een vrijstaand ligbad, een ruime inloopdouche en badjassen met slippers maken het verblijf compleet.'],
  'kenmerken':['Circa 36 m&sup2;','Tweepersoons kingsize bed','Ruime zithoek met comfortabele stoelen','Badjassen en slippers'],
  'faciliteiten':['Koelkastje met gratis flesjes water'] + FAC_BASE,
  'badkamer':['Luxe badkamer met inloopdouche','Ruim vrijstaand ligbad','Föhn aanwezig'],
  'short':'Vrijstaand ligbad, ruime inloopdouche en de meest romantische sfeer van het hotel.',
  'feat':['~36 m&sup2;','Kingsize','Ligbad','Inloopdouche']},
]
BYKEY = {r['key']: r for r in ROOMS}

def slides_for(r):
    if r.get('customslides'):
        return r['customslides']
    return [f"fotos/room-{r['photoslug']}-{i}.webp" for i in range(1, r.get('slides', 4) + 1)]

def li(items):
    return '\n'.join(f'                <li>{x}</li>' for x in items)

def build_types_list(current_key):
    rows = []
    for r in ROOMS:
        cur = r['key'] == current_key
        thumb = r.get('thumb') or slides_for(r)[0]
        chips = ''.join(f'<span>{c}</span>' for c in r['feat'])
        if cur:
            badge = '<span class="room-row__badge current">U bekijkt deze kamer</span>'
            actions = (f'<a class="btn-primary" href="#" onclick="window.openBooking(\'{r["key"]}\');return false;"'
                       f' data-track-cta="types_{r["key"]}">Reserveren</a>')
            rowcls = 'room-row is-current'
        else:
            badge = f'<span class="room-row__badge">{r["badge"]}</span>'
            actions = (f'<a class="btn-ghost" href="/{r["slug"]}">Meer details</a>\n'
                       f'          <a class="btn-primary" href="#" onclick="window.openBooking(\'{r["key"]}\');return false;"'
                       f' data-track-cta="types_{r["key"]}">Reserveren</a>')
            rowcls = 'room-row'
        rows.append(f'''      <article class="{rowcls}" data-cat="{r['cat']}">
        <img class="room-row__img" src="{thumb}" alt="{r['name']}" loading="lazy">
        <div>
          <h3 class="room-row__name">{r['name']} {badge}</h3>
          <p class="room-row__desc">{r['short']}</p>
          <div class="room-row__feat">{chips}</div>
        </div>
        <div class="room-row__actions">
          {actions}
        </div>
      </article>''')
    return '\n\n'.join(rows)

def build_page(r):
    name = r['name']
    slug = r['slug']
    price = r['price']
    poster = r.get('poster') or slides_for(r)[0]
    ogdesc = r['desc'][0]
    metadesc = ogdesc
    # hero media
    if r.get('video'):
        hero_media = (f'  <video class="hero__video" autoplay muted loop playsinline poster="{poster}">\n'
                      f'    <source src="{r["video"]}" type="video/mp4">\n  </video>')
    else:
        hero_media = f'  <img class="hero__video" src="{poster}" alt="{name} van Hotel Asteria">'
    # slider slides
    slides = slides_for(r)
    slide_html = []
    for i, s in enumerate(slides):
        lazy = '' if i == 0 else ' loading="lazy"'
        slide_html.append(f'        <div class="slider__slide"><img src="{s}" alt="{name} van Hotel Asteria"{lazy}></div>')
    slide_html = '\n'.join(slide_html)
    # specs
    m2 = r['m2']; bed = r['bed']; bath = r['bath']
    # accordion
    acc = f'''        <div class="acc">
          <details open>
            <summary>Kenmerken</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(r['kenmerken'])}
              </ul>
            </div>
          </details>
          <details>
            <summary>Faciliteiten</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(r['faciliteiten'])}
              </ul>
            </div>
          </details>
          <details>
            <summary>Badkamer</summary>
            <div class="acc__body">
              <ul class="acc__list">
{li(r['badkamer'])}
              </ul>
            </div>
          </details>
        </div>'''
    descs = '\n        '.join(f'<p>{p}</p>' for p in r['desc'])
    page = f'''<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} | Hotel Asteria Venray</title>
  <link rel="icon" href="/favicon.ico">
  <meta name="description" content="{metadesc}">

  <link rel="canonical" href="https://visit.asteria.nl/{slug}">
  <link rel="alternate" hreflang="nl" href="https://visit.asteria.nl/{slug}">
  <link rel="alternate" hreflang="x-default" href="https://visit.asteria.nl/{slug}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{name} | Hotel Asteria Venray">
  <meta property="og:description" content="{ogdesc}">
  <meta property="og:image" content="https://visit.asteria.nl/{poster}">
  <meta property="og:url" content="https://visit.asteria.nl/{slug}">
  <meta property="og:locale" content="nl_NL">
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

{STYLE}
</head>
<body>

{NAV}

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
        <span class="bookbar__label">Gasten</span>
        <select class="bookbar__value" id="bbGuests">
          <option value="2">2 personen</option>
          <option value="1">1 persoon</option>
        </select>
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">Aankomst</span>
        <input class="bookbar__value" type="date" id="bbStart">
      </div>
      <div class="bookbar__field">
        <span class="bookbar__label">Vertrek</span>
        <input class="bookbar__value" type="date" id="bbEnd">
      </div>
      <button class="bookbar__btn" onclick="window.openBooking('{r['key']}')" data-track-cta="bookbar">Bekijk beschikbaarheid</button>
    </div>
  </div>
</div>

<!-- ══ KAMER-INTRO ═══════════════════════════════════════════ -->
<div class="wrap">
  <nav class="crumb" aria-label="Kruimelpad">
    <a href="https://www.asteria.nl">Hotel Asteria</a> &nbsp;/&nbsp;
    <a href="https://www.asteria.nl/kamers">Kamers en Suites</a> &nbsp;/&nbsp;
    <span>{name}</span>
  </nav>
</div>

<section class="intro">
  <div class="wrap">
    <div class="intro__grid">
      <div class="intro__text">
        <span class="section-eyebrow">Kamertype</span>
        <h2 class="title">{name}</h2>
        {descs}

{acc}
        <p style="font-size:12px;color:#9a9a95;margin-top:22px;">De getoonde afbeeldingen zijn ter illustratie. De werkelijke kamerindeling en inrichting kunnen afwijken.</p>
      </div>

      <aside class="spec-card">
        <ul class="spec-card__list">
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_M2}</span>
            <span class="spec-card__txt"><strong>Circa {m2} m&sup2;</strong><span>Kameroppervlak</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_BED}</span>
            <span class="spec-card__txt"><strong>{bed[0]}</strong><span>{bed[1]}</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_PERS}</span>
            <span class="spec-card__txt"><strong>Max. {r['maxpers']} gasten</strong><span>Bezetting</span></span>
          </li>
          <li class="spec-card__item">
            <span class="spec-card__icon">{IC_BATH}</span>
            <span class="spec-card__txt"><strong>{bath[0]}</strong><span>{bath[1]}</span></span>
          </li>
        </ul>
        <div class="spec-card__price">
          Vanaf, per kamer per nacht
          <b>&euro;{price}</b>
        </div>
        <a class="btn-primary" href="#" onclick="window.openBooking('{r['key']}');return false;" data-track-cta="intro_reserve">Reserveren direct</a>
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

{INCLUDED}

<!-- ══ KAMERTYPES ════════════════════════════════════════════ -->
<section class="types">
  <div class="wrap">
    <div class="types__head">
      <h2>Verschillende kamertypes</h2>
      <p>Elke kamer ingericht voor comfort, voor elk verblijf en elk budget. Vergelijk de typen en kies wat bij u past.</p>
    </div>

    <div class="tabs">
      <button class="tab is-active" data-cat="all">Alle</button>
      <button class="tab" data-cat="standaard">Standaard</button>
      <button class="tab" data-cat="luxe">Luxe</button>
    </div>

    <div id="roomList">
{build_types_list(r['key'])}
    </div>
  </div>
</section>

{ARR}

<!-- ══ FAQ ═══════════════════════════════════════════════════ -->
<section class="faq">
  <div class="wrap">
    <div class="faq__head">
      <h2>Veelgestelde vragen</h2>
    </div>
    <div class="faq__list">
      <details>
        <summary>Hoe laat kan ik inchecken en uitchecken?</summary>
        <div class="faq__a">Inchecken kan vanaf 15:00 uur, uitchecken tot 11:00 uur. Eerder aankomen of later vertrekken is op aanvraag en afhankelijk van de beschikbaarheid mogelijk.</div>
      </details>
      <details>
        <summary>Is parkeren gratis?</summary>
        <div class="faq__a">Ja. U parkeert gratis op ons eigen terrein en er is een afgesloten fietsenstalling beschikbaar.</div>
      </details>
      <details>
        <summary>Is het ontbijt inbegrepen?</summary>
        <div class="faq__a">Geniet 's ochtends van ons uitgebreide ontbijtbuffet. Het ontbijt is bij veel van onze arrangementen inbegrepen en kunt u bij een losse overnachting eenvoudig bijboeken.</div>
      </details>
      <details>
        <summary>Heb ik toegang tot de wellness en fitness?</summary>
        <div class="faq__a">Als hotelgast heeft u toegang tot onze fitnessruimte. Onze wellness van 300 m² op de Top Floor reserveert u eenvoudig vooraf bij de receptie of via wellnessasteria.nl.</div>
      </details>
      <details>
        <summary>Voor hoeveel personen is de {name} geschikt?</summary>
        <div class="faq__a">De {name} is geschikt voor maximaal {r['maxpers']} {'persoon' if r['maxpers']==1 else 'personen'}. Tijdens het boeken ziet u direct de beschikbaarheid voor uw gezelschap.</div>
      </details>
      <details>
        <summary>Kan ik mijn reservering kosteloos annuleren?</summary>
        <div class="faq__a">Dat hangt af van het gekozen tarief. Bij een flexibel tarief kunt u kosteloos annuleren; bij een voordeliger niet-restitueerbaar tarief niet. De voorwaarden ziet u tijdens het boeken.</div>
      </details>
    </div>
  </div>
</section>

<!-- ══ STICKY MOBILE CTA ═════════════════════════════════════ -->
<div class="sticky-cta">
  <div class="sticky-cta__price">{name}<b>Vanaf &euro;{price}</b></div>
  <a class="btn-primary" href="#" onclick="window.openBooking('{r['key']}');return false;" data-track-cta="sticky">Reserveren</a>
</div>

{FOOTER}

{SCRIPTS}

</body>
</html>
'''
    return page

# ── Genereer de nieuwe pagina's (alle behalve comfort) ─────────────────
written = []
for r in ROOMS:
    if r['key'] == 'comfort':
        continue
    out = os.path.join(BASE, r['slug'] + '.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(build_page(r))
    written.append(r['slug'] + '.html')

# ── Werk comfort-kamer.html bij: roomList + prijs + sticky ─────────────
comfort = html
new_list = '    <div id="roomList">\n' + build_types_list('comfort') + '\n    </div>'
comfort = re.sub(r'    <div id="roomList">.*?\n    </div>', lambda m: new_list, comfort, count=1, flags=re.S)
comfort = comfort.replace(
    '''        <div class="spec-card__price">
          Direct boeken via het hotel
          <b>Beste prijsgarantie</b>
        </div>''',
    '''        <div class="spec-card__price">
          Vanaf, per kamer per nacht
          <b>&euro;114,30</b>
        </div>''')
comfort = comfort.replace(
    '<div class="sticky-cta__price">Comfort kamer<b>Beste prijsgarantie</b></div>',
    '<div class="sticky-cta__price">Comfort kamer<b>Vanaf &euro;114,30</b></div>')
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(comfort)

print('Gegenereerd:', ', '.join(written))
print('comfort-kamer.html bijgewerkt (roomList + prijs + sticky)')
