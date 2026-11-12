/* GEDRAG van de bouwsteen kaart-getekend op visit.asteria.nl (uitje-sjabloon, blok Ligging; nov 2026).
   PORT van parkhotel-site src/gedrag/blok-kaart-getekend.js (zie de uitleg daar): de getekende regiokaart van het
   omgevingsscherm als interactieve kaart midden in een pagina. Gedrag ongewijzigd: knoppen +, - en overzicht, het
   wiel zoomt alleen met Ctrl/Cmd (anders scrolt de pagina, met een korte hint), op aanraakschermen scrolt een
   vinger de pagina (touch-action:pan-y) en bewegen twee vingers de kaart, attributieregel linksonder.
   Verschillen met Parkhotel: de global heet window.AsteriaKaart, kleuren staan in kaart-getekend.css (Asteria-
   tokens), en een punt mag naast url ook pop hebben: dan wordt de nummerknop een link met data-pop="<pop>" die
   de uitje-pop-up van adslander.js opent (href = #ut-meer als terugval).
   Gebruik: window.AsteriaKaart.maak(el, opties) -> api (zetPunten, overzicht, stand, ...); opties zie Parkhotel.
   Data: content/kaart/getekend.json (kopie van parkhotel-site public/assets/kaart/getekend.json, dekt Venray en
   Overloon). Een IIFE, geen bundler. */
(function () {
  'use strict';
  if (window.AsteriaKaart) return;

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var SLEEP_MIN = 6;        // px: pas daarna is een muisbeweging slepen (en geen klik)
  var WIEL_RUST = 150;      // ms zonder wielbeweging = einde van het wielgebaar
  var RAND = 320;           // px: zoveel is de svg tijdens een gebaar aan elke kant groter
  var DUUR_KNOP = 220;      // ms: + en -
  var DUUR_ROUTE = 450;     // ms: naar een route en terug naar het overzicht
  var R_BADGE = 16;         // straal nummerknop (css .routebadge 32), actief 19
  var BADGE_TUSSEN = 3;
  var HOTEL_R = 64 * 0.47;  // straal van het hotelvignet (css .gk-hotel 64 px)
  var RUIMTE_ROUTE = 28;    // px rond een route bij focusRouteAnim (bovenop de padding)
  var MARGE = 0.15;         // zoveel ruimer dan het overzicht mag je slepen
  var ZOOM_MAX = 4;         // niet verder in dan 4x het overzicht
  var LABEL_SCHAAL = 0.34;  // dx/dy van plaatsnamen staan in kioskpixels (4K-scherm)
  var HINT_DUUR = 1500;
  var zacht = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var ICOON = {
    in: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
    uit: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/></svg>',
    alles: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>'
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function min(a) { return Math.min.apply(Math, a); }
  function max(a) { return Math.max.apply(Math, a); }

  function maak(el, o) {
    o = o || {};
    var geo = o.geo, T = o.teksten || {};
    var WERELD = 256 * Math.pow(2, geo.z);
    var wereld = function (lat, lng) {
      var r = lat * Math.PI / 180;
      return [(lng + 180) / 360 * WERELD - geo.origin[0],
        (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * WERELD - geo.origin[1]];
    };
    var padding = function () { return o.padding || { tl: [20, 20], br: [20, 20] }; };

    el.classList.add('kaart-getekend');
    // ---- de kaart zelf
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'gk-kaart');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    var pad = function (cls, d) { return '<path class="' + cls + '" d="' + d + '" vector-effect="non-scaling-stroke"/>'; };
    var wegen = geo.snelwegen.join('');
    svg.innerHTML = '<g class="gk-wereld"><rect class="gk-buitenland" x="-20000" y="-20000" width="60000" height="60000"/>' +
      pad('gk-vlak gk-buur', geo.vlakken.brabant) + pad('gk-vlak gk-buur', geo.vlakken.gelderland) +
      pad('gk-vlak gk-limburg', geo.vlakken.limburg) + pad('gk-vlak gk-nlimburg', geo.vlakken.noordLimburg) +
      pad('gk-snelweg-rand', wegen) + pad('gk-snelweg', wegen) + pad('gk-plas', geo.plassen.join('')) +
      '<g class="gk-lus"></g><g class="gk-routes"></g></g>';
    el.appendChild(svg);
    var wereldG = svg.firstElementChild,
        routesG = wereldG.querySelector('.gk-routes'),
        lusG = wereldG.querySelector('.gk-lus');

    // ---- de overlay: regio's < plaatsen < bordjes < hotel en knoppen
    var overlay = document.createElement('div');
    overlay.className = 'gk-overlay';
    el.appendChild(overlay);
    var laag = function (cls) { var d = document.createElement('div'); d.className = 'gk-laag ' + cls; overlay.appendChild(d); return d; };
    var lRegio = laag('gk-regios'), lPlaats = laag('gk-plaatsen'), lBord = laag('gk-borden'), lPin = laag('gk-pins');
    var labels = [];
    var plaatsLabels = [];   // [div, plaats, half]: alleen gebruikt door zetPunten (zie PUNTEN), routes-v3 raakt ze niet
    // regionamen in de paginataal (<html lang> begint met en/de); plaatsnamen blijven zoals ze zijn
    var TAAL = (document.documentElement.lang || '').slice(0, 2).toLowerCase();
    if (TAAL !== 'en' && TAAL !== 'de') TAAL = '';
    (geo.regios || []).forEach(function (r) {
      var d = document.createElement('div');
      d.className = 'gk-regio' + (r.k ? ' klein' : '');
      d.textContent = r[TAAL] || r.n;   // optioneel en/de in getekend.json, anders de NL-naam
      lRegio.appendChild(d);
      labels.push([d, wereld(r.lat, r.lng)]);
    });
    (geo.plaatsen || []).forEach(function (p) {
      var d = document.createElement('div');
      d.className = 'gk-plaats' + (p.s ? ' stad' : '') + (p.a === 'l' ? ' l' : '') + (p.d ? ' duits' : '');
      d.innerHTML = '<i></i><span>' + esc(p.n) + '</span>';
      var dx = (p.dx || 0) * LABEL_SCHAAL, dy = (p.dy || 0) * LABEL_SCHAAL, half = p.s ? 5 : 3;
      d.style.transform = p.a === 'l'
        ? 'translate(-100%,-50%) translate(' + (dx + half).toFixed(1) + 'px,' + dy.toFixed(1) + 'px)'
        : 'translate(0,-50%) translate(' + (dx - half).toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
      lPlaats.appendChild(d);
      labels.push([d, wereld(p.lat, p.lng)]);
      plaatsLabels.push([d, p, half]);
    });
    (geo.borden || []).forEach(function (b) {
      var d = document.createElement('div');
      d.className = 'gk-bord' + (b.de ? ' de' : '');
      d.textContent = b.n;
      lBord.appendChild(d);
      labels.push([d, [b.x, b.y]]);
    });

    // ---- het hotel (vignet; laadt het niet, dan een donker blokje met een huisje)
    var hotel = o.hotel || { lat: 51.54774, lng: 5.99732, naam: 'Hotel Asteria' };
    var H = document.createElement('div');
    H.className = 'gk-hotel';
    H.innerHTML = '<img alt="' + esc(hotel.naam || '') + '" width="64" height="64" draggable="false" decoding="async">';
    var hImg = H.firstChild;
    hImg.onerror = function () { H.classList.add('gk-hotel--terug'); hImg.remove(); };
    if (o.vignet) hImg.src = o.vignet; else hImg.onerror();
    lPin.appendChild(H);
    var hotelW = wereld(hotel.lat, hotel.lng);

    // ---- knoppen, attributie, hint
    var knoppen = document.createElement('div');
    knoppen.className = 'gk-knoppen';
    knoppen.innerHTML =
      '<button type="button" class="gk-knop" data-gk="in" aria-label="' + esc(T.in || 'Inzoomen') + '">' + ICOON.in + '</button>' +
      '<button type="button" class="gk-knop" data-gk="uit" aria-label="' + esc(T.uit || 'Uitzoomen') + '">' + ICOON.uit + '</button>' +
      '<button type="button" class="gk-knop" data-gk="alles" aria-label="' + esc(T.alles || 'Overzicht') + '">' + ICOON.alles + '</button>';
    el.appendChild(knoppen);
    var attr = document.createElement('div');
    attr.className = 'gk-attr';
    attr.innerHTML = T.attributie || 'Grenzen CBS/Kadaster &middot; water en wegen &copy; OpenStreetMap-bijdragers';
    el.appendChild(attr);
    var hint = document.createElement('div');
    hint.className = 'gk-hint';
    hint.setAttribute('aria-hidden', 'true');
    hint.innerHTML = '<span></span>';
    el.appendChild(hint);
    var hintTimer = 0;
    var toonHint = function (tekst) {
      if (!tekst) return;
      hint.firstChild.textContent = tekst;
      hint.classList.add('is-aan');
      clearTimeout(hintTimer);
      hintTimer = setTimeout(function () { hint.classList.remove('is-aan'); }, HINT_DUUR);
    };

    // ---- routes: lijnen in g.gk-routes, nummerknoppen in .gk-pins
    var routes = [];   // { r, slug, w:[[x,y]...], g, badge, uit }
    var routeActief = null;
    var lus = null, lusUit = false;
    var dPad = function (w, dicht) {
      return w.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join('') + (dicht ? 'Z' : '');
    };
    var api = {};
    api.zetRoutes = function (lijst) {
      routes.forEach(function (q) { q.badge.remove(); });
      routes = (lijst || []).filter(function (r) { return r.lijn && r.lijn.length >= 2; }).map(function (r) {
        return { r: r, slug: r.slug, w: r.lijn.map(function (p) { return wereld(p[0], p[1]); }), uit: false };
      }).sort(function (a, b) { return (b.r.afstand_km || 0) - (a.r.afstand_km || 0); });
      var defs = routes.map(function (q) { return '<path id="gk-rt-' + esc(q.slug) + '" d="' + dPad(q.w, q.r.rondje) + '" vector-effect="non-scaling-stroke"/>'; }).join('');
      routesG.innerHTML = '<defs>' + defs + '</defs>' + routes.map(function (q) {
        var h = '#gk-rt-' + esc(q.slug);
        return '<g class="rt" data-slug="' + esc(q.slug) + '"><use href="' + h + '" class="rt-rand"/><use href="' + h + '" class="rt-lijn"/><use href="' + h + '" class="rt-tik"/></g>';
      }).join('');
      // knoppen in nummervolgorde (tabvolgorde), boven het hotel
      routes.slice().sort(function (a, b) { return (a.r.nr || 0) - (b.r.nr || 0); }).forEach(function (q) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'routebadge';
        b.textContent = String(q.r.nr == null ? '' : q.r.nr);
        b.setAttribute('aria-label', (q.r.nr != null ? q.r.nr + '. ' : '') + (q.r.naam || ''));
        b.addEventListener('click', function (e) {
          e.stopPropagation();
          if (!q.uit && o.onRoute) o.onRoute(q.slug);
        });
        lPin.appendChild(b);
        q.badge = b;
      });
      routes.forEach(function (q) { q.g = routesG.querySelector('.rt[data-slug="' + q.slug + '"]'); });
      routeKlassen();
      gelegd = null;
    };
    api.zetLus = function (lijn) {
      lus = lijn && lijn.length >= 2 ? lijn.map(function (p) { return wereld(p[0], p[1]); }) : null;
      lusG.innerHTML = lus ? '<path class="gk-lus__lijn" d="' + dPad(lus, true) + '" vector-effect="non-scaling-stroke"/>' : '';
    };
    // ---- punten (pagina-gebied-v2): badges met een naam in .gk-pins; zie PUNTEN bovenaan
    var punten = [];   // { p, w:[x,y], el, hoofd }
    var SPELD = '<svg viewBox="0 0 30 40" aria-hidden="true" focusable="false"><path d="M15 39C9 31 2.5 23.5 2.5 14.5a12.5 12.5 0 0 1 25 0C27.5 23.5 21 31 15 39z"/><circle cx="15" cy="14.5" r="4.5"/></svg>';
    api.zetPunten = function (data) {
      punten.forEach(function (q) { q.el.remove(); });
      // PLAATSNAMEN OP HUN COORDINAAT (7 okt 2026, integratieronde gebied-v2). De dx/dy van een plaats in getekend.json
      // zijn vaste kioskpixels (x LABEL_SCHAAL), gemaakt voor de zoomstand van het lobbyscherm, en ze verschuiven de
      // HELE plaatsnaam, stip incluis. Op een kaart met punten is het overzicht vaak veel verder uitgezoomd (s 0,07 tot
      // 0,3), dus stond Venlo's stip 65 px te laag (bij Roermond) en Horst's stip 111 px links van Horst. Met punten
      // staat de stip daarom exact op de plaats en de naam er direct naast; botst hij met een punt, dan kiest de pagina
      // (pagina-gebied-v2, pasNamenIn) de andere kant of laat hem weg. Zonder zetPunten (routes-v3) blijft alles gelijk.
      plaatsLabels.forEach(function (x) {
        x[0].style.transform = x[1].a === 'l'
          ? 'translate(-100%,-50%) translate(' + x[2] + 'px,0px)'
          : 'translate(0,-50%) translate(' + (-x[2]) + 'px,0px)';
      });
      var lijst = (data && data.punten) || (Array.isArray(data) ? data : []);
      punten = lijst.filter(function (p) { return p && isFinite(p.lat) && isFinite(p.lng); }).map(function (p) {
        var hoofd = !!p.hoofd, link = !hoofd && (p.url || p.pop);
        var el = document.createElement(link ? 'a' : 'div');
        el.className = 'gk-punt ' + (hoofd ? 'gk-punt--hoofd' : 'gk-punt--nr') + ' gk-punt--' + esc(p.label || (hoofd ? 'boven' : 'rechts'));
        if (link) {
          el.href = p.url || '#ut-meer';
          if (!p.url && p.pop) el.setAttribute('data-pop', p.pop);
          el.setAttribute('aria-label', (p.nr != null ? p.nr + '. ' : '') + (p.naam || ''));
        }
        el.innerHTML = (hoofd ? '<span class="gk-punt__speld">' + SPELD + '</span>'
          : '<span class="gk-punt__nr" aria-hidden="true">' + esc(p.nr == null ? '' : p.nr) + '</span>') +
          '<span class="gk-punt__naam"' + (link ? ' aria-hidden="true"' : '') + '>' + esc(p.naam) + '</span>';
        lPin.appendChild(el);
        return { p: p, w: wereld(p.lat, p.lng), el: el, hoofd: hoofd };
      });
      gelegd = null;
    };
    /** Punten op de huidige schaal, ALTIJD exact op hun coordinaat (7 okt 2026, integratieronde: spelden en
        nummerknoppen schuiven niet meer weg van het hotelvignet of van elkaar; ze liggen boven het vignet, z-index 12
        tegen 10). Alleen de namen wijken uit; dat doet de pagina (pagina-gebied-v2, pasNamenIn). */
    function legPunten() {
      if (!punten.length || gelegd == null) return;
      punten.forEach(function (q) {
        q.el.style.left = (q.w[0] * s).toFixed(1) + 'px';
        q.el.style.top = (q.w[1] * s).toFixed(1) + 'px';
      });
    }
    // Een tik op een lijn (het brede, onzichtbare tikvlak).
    routesG.addEventListener('click', function (e) {
      var g = e.target.closest ? e.target.closest('.rt') : null;
      if (!g || g.classList.contains('uit')) return;
      e.stopPropagation();
      if (o.onRoute) o.onRoute(g.getAttribute('data-slug'));
    });
    function routeKlassen() {
      routes.forEach(function (q) {
        var on = q.slug === routeActief, dim = routeActief != null && !on && !q.uit;
        [q.g, q.badge].forEach(function (x) {
          if (!x) return;
          x.classList.toggle('on', on);
          x.classList.toggle('dim', dim);
          x.classList.toggle('uit', q.uit);
        });
        if (q.badge) {
          q.badge.style.zIndex = on ? '30' : '20';
          if (q.uit) q.badge.setAttribute('tabindex', '-1'); else q.badge.removeAttribute('tabindex');
          q.badge.setAttribute('aria-pressed', on ? 'true' : 'false');
        }
      });
      // volgorde in de svg: langste onder, de actieve bovenop
      routes.forEach(function (q) { if (q.g) routesG.appendChild(q.g); });
      var a = routes.filter(function (q) { return q.slug === routeActief; })[0];
      if (a && a.g) routesG.appendChild(a.g);
      lusG.classList.toggle('uit', lusUit);
    }

    // ---- weergave: scherm-px = t + s x wereld-px
    var s = 1, tx = 0, ty = 0, sMin = 0.05, sMax = 64;
    var ovS = 0, ovTx = 0, ovTy = 0, grens = null;
    var B = function () { return el.clientWidth || 1; };
    var Hh = function () { return el.clientHeight || 1; };
    var klem = function () {
      if (!grens) return;
      // padding.klemOnder (px, optioneel): zoveel verder mag de kaart omhoog schuiven, voor iets dat onderin over de kaart
      // ligt (de strook van pagina-routes-v3); zo kan een route onderaan het gebied tóch boven die strook gecentreerd worden
      var ko = (padding().klemOnder || 0);
      var minX = B() - grens[2] * s, maxX = -grens[0] * s, minY = Hh() - grens[3] * s - ko, maxY = -grens[1] * s;
      tx = minX > maxX ? (minX + maxX) / 2 : Math.min(maxX, Math.max(minX, tx));
      ty = minY > maxY ? (minY + maxY) / 2 : Math.min(maxY, Math.max(minY, ty));
    };
    var gelegd = null;

    /** Overlay op de huidige schaal leggen: labels, hotel, nummerknoppen. */
    var leg = function () {
      labels.forEach(function (l) { l[0].style.left = (l[1][0] * s).toFixed(1) + 'px'; l[0].style.top = (l[1][1] * s).toFixed(1) + 'px'; });
      H.style.left = (hotelW[0] * s).toFixed(1) + 'px';
      H.style.top = (hotelW[1] * s).toFixed(1) + 'px';
      gelegd = s;
      legBadges();
      legPunten();
    };
    /** Nummerknop op de start van de route, of het eerste vrije punt verderop langs de lijn. */
    function legBadges() {
      if (!routes.length || gelegd == null) return;
      var bezet = [{ x: hotelW[0] * s, y: hotelW[1] * s, r: HOTEL_R }];
      var volg = routes.filter(function (q) { return !q.uit; }).sort(function (a, b) {
        return ((b.slug === routeActief) - (a.slug === routeActief)) || ((a.r.nr || 0) - (b.r.nr || 0));
      });
      volg.forEach(function (q) {
        var r0 = q.slug === routeActief ? R_BADGE + 3 : R_BADGE;
        var best = [q.w[0][0] * s, q.w[0][1] * s], bestVrij = -Infinity;
        for (var i = 0; i < q.w.length; i++) {
          var x = q.w[i][0] * s, y = q.w[i][1] * s, vrij = Infinity;
          for (var j = 0; j < bezet.length; j++) vrij = Math.min(vrij, Math.hypot(x - bezet[j].x, y - bezet[j].y) - bezet[j].r - r0 - BADGE_TUSSEN);
          if (vrij > bestVrij) { bestVrij = vrij; best = [x, y]; }
          if (vrij >= 0) break;
        }
        q.badge.style.left = best[0].toFixed(1) + 'px';
        q.badge.style.top = best[1].toFixed(1) + 'px';
        q.bx = best[0]; q.by = best[1];
        bezet.push({ x: best[0], y: best[1], r: r0 });
      });
    }

    var knijpend = false, wielTimer = 0, anim = 0, slepend = false;
    var inGebaar = function () { return knijpend || Boolean(wielTimer) || Boolean(anim); };
    var gS = null, gTx = 0, gTy = 0, groot = false;
    var zetG = function () {
      var r = groot ? RAND : 0;
      wereldG.setAttribute('transform', 'translate(' + (tx + r).toFixed(2) + ' ' + (ty + r).toFixed(2) + ') scale(' + s + ')');
      if (groot) svg.style.transform = 'translate(' + (-RAND) + 'px,' + (-RAND) + 'px)';
      gS = s; gTx = tx; gTy = ty;
    };
    var vergroot = function (aan) {
      if (aan === groot) return;
      groot = aan;
      if (aan) {
        svg.style.width = svg.style.height = 'calc(100% + ' + (2 * RAND) + 'px)';
        svg.style.transformOrigin = RAND + 'px ' + RAND + 'px';
      } else svg.removeAttribute('style');
    };
    var tekenKaart = function (bezig) {
      if (!bezig) { vergroot(false); zetG(); return; }
      if (!groot || gS == null) { vergroot(true); zetG(); return; }
      var k = s / gS, dx = tx - k * gTx, dy = ty - k * gTy;
      var dekt = dx - k * RAND <= 0 && dx + k * (B() + RAND) >= B() && dy - k * RAND <= 0 && dy + k * (Hh() + RAND) >= Hh();
      if (!dekt) { zetG(); return; }
      svg.style.transform = 'translate(' + (dx - RAND).toFixed(2) + 'px,' + (dy - RAND).toFixed(2) + 'px)' + (Math.abs(k - 1) > 1e-6 ? ' scale(' + k.toFixed(5) + ')' : '');
    };
    var pinK = 1;
    /** Tijdens een zoomgebaar: hotel en knoppen op tegenschaal 1/k, labels even weg. */
    var opMaat = function (k) {
      if (k === pinK) return;
      overlay.classList.toggle('gk-zoomt', k !== 1);
      pinK = k;
      var t = k === 1 ? '' : 'translate(-50%,-50%) scale(' + (1 / k).toFixed(5) + ')';
      H.style.transform = t;
      routes.forEach(function (q) { if (q.badge) q.badge.style.transform = t; });
      punten.forEach(function (q) { q.el.style.transform = k === 1 ? '' : 'scale(' + (1 / k).toFixed(5) + ')'; });
    };
    var teken = function () {
      tekenKaart(inGebaar() || slepend);
      if (gelegd !== s && (gelegd == null || !inGebaar())) leg();
      var k = s / gelegd, schaalt = Math.abs(k - 1) > 1e-6;
      overlay.style.transform = 'translate(' + tx.toFixed(2) + 'px,' + ty.toFixed(2) + 'px)' + (schaalt ? ' scale(' + k.toFixed(5) + ')' : '');
      opMaat(schaalt ? k : 1);
      if (!schaalt && !inGebaar() && !slepend) knipLabels();
      if (o.naTeken) o.naTeken();
    };
    /** Regio-, plaats- en bordnamen die niet helemaal binnen het kaartvlak vallen verbergen (geen half afgesneden
        "lmond" aan de rand). Bij stilstand: overzicht, na slepen, na zoomen; de pagina roept hem opnieuw aan nadat
        ze plaatsnamen van kant heeft gewisseld (uitje.js, pasNamenIn). */
    function knipLabels() {
      var v = el.getBoundingClientRect();
      if (!v.width || !v.height) return;
      labels.forEach(function (l) {
        var r = l[0].getBoundingClientRect();
        var buiten = r.width > 0 && (r.left < v.left - 0.5 || r.right > v.right + 0.5 || r.top < v.top - 0.5 || r.bottom > v.bottom + 0.5);
        l[0].classList.toggle('gk-buiten', buiten);
      });
    }
    api.knipLabels = knipLabels;
    var rafId = 0;
    var plan = function () { if (!rafId) rafId = requestAnimationFrame(function () { rafId = 0; teken(); }); };
    var zetSchaal = function (n) { return Math.max(sMin, Math.min(sMax, n)); };
    var zoomOm = function (n, cx, cy) {
      if (cx == null) { cx = B() / 2; cy = Hh() / 2; }
      n = zetSchaal(n);
      tx = cx - (cx - tx) * (n / s);
      ty = cy - (cy - ty) * (n / s);
      s = n;
      klem();
    };

    // Korte animatie naar s/tx/ty; de schaal geometrisch met een vast punt (voelt als één beweging).
    var naar = function (ns, ntx, nty, duur) {
      cancelAnimationFrame(anim);
      if (!zacht) duur = 0;
      var s0 = s, x0 = tx, y0 = ty;
      var zoomt = Math.abs(ns - s0) > 1e-9;
      var wx = zoomt ? (ntx - x0) / (s0 - ns) : 0, wy = zoomt ? (nty - y0) / (s0 - ns) : 0;
      var t0 = performance.now();
      var stap = function (nu) {
        var k = duur ? Math.min(1, Math.max(0, (nu - t0) / duur)) : 1;
        var e = 1 - Math.pow(1 - k, 3);
        if (k >= 1) { s = ns; tx = ntx; ty = nty; }
        else if (zoomt) { s = s0 * Math.pow(ns / s0, e); tx = x0 + s0 * wx - s * wx; ty = y0 + s0 * wy - s * wy; }
        else { tx = x0 + (ntx - x0) * e; ty = y0 + (nty - y0) * e; }
        anim = k < 1 ? requestAnimationFrame(stap) : 0;
        teken();
      };
      anim = requestAnimationFrame(stap);
    };
    var stopAnim = function () { if (anim) { cancelAnimationFrame(anim); anim = 0; teken(); } };
    var geklemd = function (ns, ntx, nty) {
      var bs = s, bx = tx, by = ty;
      s = ns; tx = ntx; ty = nty;
      klem();
      var uit = [s, tx, ty];
      s = bs; tx = bx; ty = by;
      return uit;
    };

    /** Stand waarop de wereldpunten ws passen binnen het kaartvlak min de padding. */
    var overzichtVan = function (ws) {
      var xs = ws.map(function (w) { return w[0]; }), ys = ws.map(function (w) { return w[1]; });
      var x0 = min(xs), x1 = max(xs), y0 = min(ys), y1 = max(ys);
      var p = padding();
      var bw = Math.max(1, B() - p.tl[0] - p.br[0]), bh = Math.max(1, Hh() - p.tl[1] - p.br[1]);
      var os = Math.min(bw / Math.max(1, x1 - x0), bh / Math.max(1, y1 - y0));
      return [os, p.tl[0] + bw / 2 - os * (x0 + x1) / 2, p.tl[1] + bh / 2 - os * (y0 + y1) / 2];
    };
    /** Het overzicht: de zichtbare routes (+ de lus als die zichtbaar is) + het hotel. */
    var routeOverzicht = function () {
      var ws = [hotelW];
      routes.forEach(function (q) { if (!q.uit) ws = ws.concat(q.w); });
      if (lus && !lusUit) ws = ws.concat(lus);
      punten.forEach(function (q) { ws.push(q.w); });
      if (ws.length === 1) routes.forEach(function (q) { ws = ws.concat(q.w); });
      return overzichtVan(ws);
    };
    var ongerept = function () { return ovS && Math.abs(s / ovS - 1) < 1e-3 && Math.abs(tx - ovTx) < 0.5 && Math.abs(ty - ovTy) < 0.5; };

    /** Naar het overzicht; zet ook de zoomgrenzen (overzicht .. 4x) en de sleepgrens (+15 %). */
    var zetGrenzen = function () {
      var ov = routeOverzicht();
      sMin = ov[0];
      sMax = ov[0] * ZOOM_MAX;
      var vx0 = -ov[1] / ov[0], vy0 = -ov[2] / ov[0], vw = B() / ov[0], vh = Hh() / ov[0];
      grens = [vx0 - vw * MARGE, vy0 - vh * MARGE, vx0 + vw * (1 + MARGE), vy0 + vh * (1 + MARGE)];
      ovS = ov[0]; ovTx = ov[1]; ovTy = ov[2];
      return ov;
    };
    api.overzicht = function (animeer) {
      if (!el.clientWidth || !el.clientHeight) return;
      var ov = zetGrenzen();
      if (animeer) { naar(ov[0], ov[1], ov[2], DUUR_ROUTE); return; }
      stopAnim();
      s = ov[0]; tx = ov[1]; ty = ov[2];
      gelegd = null;
      teken();
      el.setAttribute('data-klaar', '1');
    };
    api.zetZichtbaar = function (fn, lusZichtbaar) {
      routes.forEach(function (q) { q.uit = !fn(q.r); });
      lusUit = !lusZichtbaar;
      if (routeActief != null && routes.some(function (q) { return q.slug === routeActief && q.uit; })) routeActief = null;
      routeKlassen();
      if (gelegd === s) legBadges();
    };
    api.setActiveRoute = function (slug) {
      routeActief = slug == null ? null : slug;
      routeKlassen();
      if (gelegd === s) legBadges();
      if (o.naTeken) o.naTeken();
    };
    api.focusRouteAnim = function (slug) {
      var q = routes.filter(function (x) { return x.slug === slug; })[0];
      if (!q || !ovS) return;
      stopAnim();
      api.setActiveRoute(slug);
      var p = padding();
      var x0 = p.tl[0] + RUIMTE_ROUTE, y0 = p.tl[1] + RUIMTE_ROUTE, x1 = B() - p.br[0] - RUIMTE_ROUTE, y1 = Hh() - p.br[1] - RUIMTE_ROUTE;
      var xs = q.w.map(function (w) { return w[0]; }), ys = q.w.map(function (w) { return w[1]; });
      var bx0 = min(xs), bx1 = max(xs), by0 = min(ys), by1 = max(ys);
      var ns = zetSchaal(Math.min((x1 - x0) / Math.max(1, bx1 - bx0), (y1 - y0) / Math.max(1, by1 - by0)));
      var g = geklemd(ns, (x0 + x1) / 2 - ns * (bx0 + bx1) / 2, (y0 + y1) / 2 - ns * (by0 + by1) / 2);
      naar(g[0], g[1], g[2], DUUR_ROUTE);
    };
    api.zoomIn = function () {
      if (s >= sMax * 0.999) return;
      var ns = zetSchaal(s * 2), cx = B() / 2, cy = Hh() / 2;
      var g = geklemd(ns, cx - (cx - tx) * (ns / s), cy - (cy - ty) * (ns / s));
      naar(g[0], g[1], g[2], DUUR_KNOP);
    };
    api.zoomOut = function () {
      if (s <= sMin * 1.001) return;
      var bs = s, bx = tx, by = ty;
      zoomOm(s / 2);
      var ns = s, ntx = tx, nty = ty;
      s = bs; tx = bx; ty = by;
      naar(ns, ntx, nty, DUUR_KNOP);
    };
    /** Waar de nummerknop van een route nu staat (px in het kaartvlak), of null. */
    api.badgePlek = function (slug) {
      var q = routes.filter(function (x) { return x.slug === slug; })[0];
      if (!q || q.bx == null || gelegd == null) return null;
      var k = s / gelegd;
      return [tx + q.bx * k, ty + q.by * k];
    };
    api.stand = function () { return { s: s, tx: tx, ty: ty, overzicht: !!ongerept(), actief: routeActief, sMin: sMin, sMax: sMax }; };

    // ---- knoppen
    knoppen.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-gk]') : null;
      if (!b) return;
      e.stopPropagation();
      var w = b.getAttribute('data-gk');
      if (w === 'in') api.zoomIn();
      else if (w === 'uit') api.zoomOut();
      else if (o.onOverzicht) o.onOverzicht();
      else api.overzicht(true);
    });

    // ---- muis: slepen (aanraken gaat via de touch-events hieronder)
    var pt = function (x, y) { var r = el.getBoundingClientRect(); return [x - r.left - el.clientLeft, y - r.top - el.clientTop]; };
    var sleep = null, gesleept = false;
    el.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch' || e.button > 0) return;
      if (e.target.closest && e.target.closest('.gk-knoppen, a, .ro-kaart__label')) return;
      stopAnim();
      sleep = { id: e.pointerId, start: pt(e.clientX, e.clientY), vorig: pt(e.clientX, e.clientY) };
      gesleept = false;
    });
    window.addEventListener('pointermove', function (e) {
      if (!sleep || e.pointerId !== sleep.id) return;
      var nu = pt(e.clientX, e.clientY);
      if (!gesleept && Math.hypot(nu[0] - sleep.start[0], nu[1] - sleep.start[1]) < SLEEP_MIN) return;
      if (!gesleept) { gesleept = true; slepend = true; el.classList.add('sleept'); }
      tx += nu[0] - sleep.vorig[0];
      ty += nu[1] - sleep.vorig[1];
      sleep.vorig = nu;
      klem();
      plan();
    });
    var los = function (e) {
      if (!sleep || (e && e.pointerId !== sleep.id)) return;
      sleep = null;
      slepend = false;
      el.classList.remove('sleept');
      plan();
      if (gesleept) setTimeout(function () { gesleept = false; }, 60);
    };
    window.addEventListener('pointerup', los);
    window.addEventListener('pointercancel', los);
    window.addEventListener('blur', function () { los(); });
    // Na slepen of knijpen is het loslaten geen klik op een nummer.
    el.addEventListener('click', function (e) {
      if (gesleept) { e.stopPropagation(); e.preventDefault(); gesleept = false; }
    }, true);

    // ---- wiel: alleen met Ctrl/Cmd (en de knijp op een trackpad, die stuurt ctrlKey mee)
    el.addEventListener('wheel', function (e) {
      if (!(e.ctrlKey || e.metaKey)) { toonHint(T.wiel || 'Ctrl + scrollen om te zoomen'); return; }
      e.preventDefault();
      stopAnim();
      var p = pt(e.clientX, e.clientY);
      var d = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      d = Math.max(-60, Math.min(60, d));
      clearTimeout(wielTimer);
      wielTimer = setTimeout(function () { wielTimer = 0; teken(); }, WIEL_RUST);
      zoomOm(s * Math.exp(-d * 0.006), p[0], p[1]);
      plan();
    }, { passive: false });

    // ---- aanraken: één vinger scrolt de pagina, twee vingers bewegen en knijpen de kaart
    var knijp = null, een = null;
    var meet = function (e) {
      var a = pt(e.touches[0].clientX, e.touches[0].clientY), b = pt(e.touches[1].clientX, e.touches[1].clientY);
      return { d: Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, c: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2] };
    };
    el.addEventListener('touchstart', function (e) {
      if (e.touches.length >= 2) {
        stopAnim();
        knijp = meet(e);
        knijpend = true;
        gesleept = true;
        een = null;
        hint.classList.remove('is-aan');
        if (e.cancelable) e.preventDefault();
      } else if (e.touches.length === 1) {
        een = { x: e.touches[0].clientX, y: e.touches[0].clientY, getoond: false };
      }
    }, { passive: false });
    el.addEventListener('touchmove', function (e) {
      if (e.touches.length >= 2 && knijp) {
        if (e.cancelable) e.preventDefault();
        var nu = meet(e);
        tx += nu.c[0] - knijp.c[0];
        ty += nu.c[1] - knijp.c[1];
        zoomOm(s * nu.d / knijp.d, nu.c[0], nu.c[1]);
        knijp = nu;
        plan();
      } else if (e.touches.length === 1 && een && !een.getoond) {
        if (Math.hypot(e.touches[0].clientX - een.x, e.touches[0].clientY - een.y) > 12) {
          een.getoond = true;
          toonHint(T.vingers || 'Gebruik twee vingers om de kaart te bewegen');
        }
      }
    }, { passive: false });
    var touchLos = function (e) {
      if (e.touches.length < 2 && knijp) {
        knijp = null;
        knijpend = false;
        plan();
        setTimeout(function () { gesleept = false; }, 80);
      }
      if (!e.touches.length) een = null;
    };
    el.addEventListener('touchend', touchLos);
    el.addEventListener('touchcancel', touchLos);

    // ---- maatverandering: op het overzicht blijven, of binnen de grens houden
    var maatW = el.clientWidth, maatH = el.clientHeight;
    var opnieuw = function () {
      if (el.clientWidth === maatW && el.clientHeight === maatH) return;
      maatW = el.clientWidth; maatH = el.clientHeight;
      if (!ovS || (ongerept() && !anim)) { api.overzicht(false); return; }
      // ingezoomd of onderweg: grenzen opnieuw, de stand zelf blijft (binnen de grenzen)
      if (!el.clientWidth || !el.clientHeight) return;
      stopAnim();
      zetGrenzen();
      s = zetSchaal(s);
      klem();
      gelegd = null;
      teken();
    };
    if (window.ResizeObserver) new ResizeObserver(opnieuw).observe(el);
    else window.addEventListener('resize', opnieuw);

    return api;
  }

  window.AsteriaKaart = { maak: maak };
})();
