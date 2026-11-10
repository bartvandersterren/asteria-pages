/* GEDRAG bij het sjabloon uitje.template.html (de uitjepagina van Hotel Asteria, eerste: /zooparc-overloon-v2).
   Port van parkhotel-site src/gedrag/pagina-gebied-v2.js (stuk 1-3; stuk 4, de fotoslider van het arrangementblok,
   bestaat hier niet). Mews, kamerslider, pop-ups, onderbalk en cookie doet adslander.js. Elk stuk stopt stil als
   zijn blok er niet is.

   1  LEES MEER (blok 3): rij 2 en 3 staan in .ut-verhaal__meer. Zonder script open en de balk verborgen. Met script
      op elke breedte ingeklapt (.is-dicht: 300 px met verloop, inert), de balk verschijnt; klik wisselt open/dicht en
      het label tussen data-open en data-dicht; bij dichtklappen scrollt de knop naar het midden.
   2  DE DAG IN VIER MOMENTEN (blok 6): klaplijst, alleen het gekozen moment toont zijn tekst, de staande foto wisselt
      mee. Startmoment uit data-start. Zonder script staan alle teksten open en toont de foto het eerste moment.
   3  DE KAART (blok 7): komt het kaartvlak in beeld (400 px vooruit), dan haalt het script de ondergrond (data-geo)
      en leest de punten (data-punten = #id van een JSON-script in de pagina, of een adres), en bouwt
      window.AsteriaKaart (kaart-getekend.js) de kaart met het hotel en de punten. Daarna legt pasNamenIn de namen
      zo dat ze nergens overheen vallen (1-op-1 Parkhotel: voorkeurskant, uitwijken, leiderlijn, en anders een
      legenda onder de kaart). VANGNET: zonder script, of als laden mislukt, blijft de stilstaande kaartfoto staan.
   Een IIFE per stuk, geen bundler, geen localStorage. */
(function () {
  'use strict';
  var knop = document.querySelector('.ut-meerbalk__knop');
  var doos = document.getElementById('ut-verhaal-meer');
  if (!knop || !doos) return;
  var balk = knop.parentNode, label = knop.querySelector('.ut-meerbalk__label');
  var zet = function (open) {
    knop.setAttribute('aria-expanded', open ? 'true' : 'false');
    doos.classList.toggle('is-dicht', !open);
    if (open) doos.removeAttribute('inert'); else doos.setAttribute('inert', '');
    if (label) label.textContent = open ? knop.getAttribute('data-dicht') : knop.getAttribute('data-open');
  };
  balk.hidden = false;
  zet(false);
  knop.addEventListener('click', function () {
    var open = knop.getAttribute('aria-expanded') === 'true';
    zet(!open);
    if (open) knop.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
})();

(function () {
  'use strict';
  var dag = document.querySelector('.ut-dag');
  if (!dag) return;
  var momenten = dag.querySelectorAll('.ut-moment'),
      beelden = dag.querySelectorAll('.ut-dag__beeld');
  dag.classList.add('ut-dag--js');
  var zet = function (nr) {
    Array.prototype.forEach.call(momenten, function (m) {
      var aan = m.getAttribute('data-moment') === nr;
      m.classList.toggle('is-aan', aan);
      var k = m.querySelector('.ut-moment__kies');
      if (k) k.setAttribute('aria-expanded', aan ? 'true' : 'false');
    });
    Array.prototype.forEach.call(beelden, function (b) {
      b.classList.toggle('is-aan', b.getAttribute('data-beeld') === nr);
    });
  };
  var start = dag.getAttribute('data-start') || '1';
  if (!dag.querySelector('.ut-moment[data-moment="' + start + '"]')) start = '1';
  zet(start);
  Array.prototype.forEach.call(momenten, function (m) {
    m.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('a')) return;
      zet(m.getAttribute('data-moment'));
    });
  });
})();

(function () {
  'use strict';
  var beeld = document.querySelector('.ut-kaart [data-kaart]');
  if (!beeld) return;
  /* NAMEN INPASSEN (1-op-1 Parkhotel pasNamenIn). Spelden en nummerknoppen staan altijd exact op hun coordinaat;
     alleen de namen wijken uit: eerst naast het punt aan de voorkeurskant (label), dan rechts, links, boven, onder,
     schuin; lukt dat nergens, dan verder weg (tot 84 px) met een leiderlijn; anders de plek met de minste overlap.
     Daarna de plaatsnamen van de ondergrond: botst er een, dan naar de andere kant van zijn stip of weg. */
  var KANTEN = ['rechts', 'links', 'boven', 'onder', 'rb', 'ro', 'lb', 'lo'];
  var AFSTANDEN = [6, 18, 32, 52, 84];
  var raakt = function (a, b, m) { m = m || 0; return a.left < b.right + m && a.right > b.left - m && a.top < b.bottom + m && a.bottom > b.top - m; };
  var overlap = function (a, b) { return Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top)); };
  var rect = function (l, t, w, h) { return { left: l, top: t, right: l + w, bottom: t + h }; };
  var pasNamenIn = function () {
    beeld.classList.remove('ut-kaart--legenda');
    var oudeLegenda = beeld.parentNode && beeld.parentNode.parentNode && beeld.parentNode.parentNode.querySelector('.ut-kaart__legenda');
    if (oudeLegenda) oudeLegenda.remove();
    var vak = beeld.getBoundingClientRect(), bezet = [], mislukt = false;
    /* ligt de voetstrook (bureaublad) over de kaart, dan is de bovenkant van die strook de onderrand */
    var voet = beeld.parentNode && beeld.parentNode.querySelector('.ut-voet'), onder = vak.bottom;
    if (voet) { var vr = voet.getBoundingClientRect(); if (vr.height && vr.top < vak.bottom && vr.bottom > vak.top) onder = Math.min(onder, vr.top); }
    var grens = { left: vak.left + 3, right: vak.right - 51, top: vak.top + 4, bottom: onder - 4 };
    var binnen = function (r) { return r.left >= grens.left && r.right <= grens.right && r.top >= grens.top && r.bottom <= grens.bottom; };
    /* nummerknoppen die op een eerder punt of het hotelvignet vallen: stip op de coordinaat, knop ernaast met lijntje */
    var hotelEl = beeld.querySelector('.gk-hotel'), hr = hotelEl ? hotelEl.getBoundingClientRect() : null;
    var ankers = [];
    if (hr) ankers.push({ x: (hr.left + hr.right) / 2, y: (hr.top + hr.bottom) / 2, r: hr.width * 0.47 });
    Array.prototype.forEach.call(beeld.querySelectorAll('.gk-punt__speld'), function (e) { var r = e.getBoundingClientRect(); ankers.push({ x: (r.left + r.right) / 2, y: r.top + r.height * 0.36, r: 15 }); });
    Array.prototype.forEach.call(beeld.querySelectorAll('.gk-punt--nr'), function (pt) {
      var knop = pt.querySelector('.gk-punt__nr');
      ['.gk-punt__stip', '.gk-punt__knoplijn'].forEach(function (s) { var x = pt.querySelector(s); if (x) x.remove(); });
      knop.style.left = knop.style.top = '';
      var o = pt.getBoundingClientRect(), x0 = o.left, y0 = o.top, R = 14;
      var vrijOp = function (x, y) {
        return x - R >= grens.left && x + R <= vak.right - 51 && y - R >= grens.top && y + R <= grens.bottom &&
          ankers.every(function (a) { return Math.hypot(x - a.x, y - a.y) >= a.r + R + 3; });
      };
      if (!vrijOp(x0, y0) && ankers.some(function (a) { return Math.hypot(x0 - a.x, y0 - a.y) < a.r + R - 2; })) {
        var hx = hr ? (hr.left + hr.right) / 2 : x0 - 1, hy = hr ? (hr.top + hr.bottom) / 2 : y0;
        var basis = Math.atan2(y0 - hy, x0 - hx), keus = null;
        for (var straal = 30; straal <= 70 && !keus; straal += 8) {
          for (var i = 0; i < 16 && !keus; i++) {
            var hoek = basis + (i % 2 ? 1 : -1) * Math.ceil(i / 2) * Math.PI / 8;
            var x = x0 + Math.cos(hoek) * straal, y = y0 + Math.sin(hoek) * straal;
            if (vrijOp(x, y)) keus = [x, y];
          }
        }
        if (keus) {
          knop.style.left = (keus[0] - x0 - R).toFixed(1) + 'px';
          knop.style.top = (keus[1] - y0 - R).toFixed(1) + 'px';
          var stip = document.createElement('span'); stip.className = 'gk-punt__stip'; stip.setAttribute('aria-hidden', 'true');
          var lijn = document.createElement('span'); lijn.className = 'gk-punt__knoplijn'; lijn.setAttribute('aria-hidden', 'true');
          var dx = keus[0] - x0, dy = keus[1] - y0, len = Math.hypot(dx, dy);
          lijn.style.width = Math.max(0, len - R).toFixed(1) + 'px';
          lijn.style.transform = 'rotate(' + Math.atan2(dy, dx).toFixed(4) + 'rad)';
          pt.insertBefore(lijn, pt.firstChild);
          pt.insertBefore(stip, pt.firstChild);
          x0 = keus[0]; y0 = keus[1];
        }
      }
      ankers.push({ x: x0, y: y0, r: R });
    });
    Array.prototype.forEach.call(beeld.querySelectorAll('.gk-punt__nr, .gk-punt__speld, .gk-punt__stip, .gk-hotel, .gk-attr'), function (e) { bezet.push(e.getBoundingClientRect()); });
    if (onder < vak.bottom) bezet.push({ left: vak.left, right: vak.right, top: onder, bottom: vak.bottom });
    Array.prototype.forEach.call(beeld.querySelectorAll('.gk-punt'), function (pt) {
      var naam = pt.querySelector('.gk-punt__naam');
      if (!naam) return;
      if (!pt.getAttribute('data-kant')) pt.setAttribute('data-kant', (pt.className.match(/gk-punt--(rechts|links|onder|boven)/) || [])[1] || 'rechts');
      var eigen = pt.getAttribute('data-kant');
      var oud = pt.querySelector('.gk-punt__lijn');
      if (oud) oud.remove();
      naam.style.marginLeft = '';
      naam.style.left = naam.style.top = '0px';
      naam.style.right = naam.style.bottom = 'auto';
      naam.style.transform = 'none';
      var o = pt.getBoundingClientRect(), merk = pt.querySelector('.gk-punt__nr, .gk-punt__speld').getBoundingClientRect();
      var hoofd = pt.classList.contains('gk-punt--hoofd');
      var cx = (merk.left + merk.right) / 2, cy = hoofd ? merk.top + merk.height * 0.36 : (merk.top + merk.bottom) / 2;
      var w = naam.offsetWidth, h = naam.offsetHeight;
      var plek = function (kant, g) {
        var l, tp, d = g * 0.7;
        if (kant === 'rechts') { l = merk.right + g; tp = cy - h / 2; }
        else if (kant === 'links') { l = merk.left - g - w; tp = cy - h / 2; }
        else if (kant === 'boven') { l = cx - w / 2; tp = merk.top - g - h; }
        else if (kant === 'onder') { l = cx - w / 2; tp = merk.bottom + g; }
        else if (kant === 'rb') { l = merk.right + d; tp = merk.top - d - h; }
        else if (kant === 'ro') { l = merk.right + d; tp = merk.bottom + d; }
        else if (kant === 'lb') { l = merk.left - d - w; tp = merk.top - d - h; }
        else { l = merk.left - d - w; tp = merk.bottom + d; }
        if (kant === 'boven' || kant === 'onder') l = Math.min(Math.max(l, grens.left), grens.right - w);
        return rect(l, tp, w, h);
      };
      var volg = [eigen].concat(KANTEN.filter(function (k) { return k !== eigen; }));
      var keus = null, beste = null, besteO = Infinity;
      for (var a = 0; a < AFSTANDEN.length && !keus; a++) {
        for (var k = 0; k < volg.length && !keus; k++) {
          var r = plek(volg[k], AFSTANDEN[a]);
          if (binnen(r) && !bezet.some(function (b) { return raakt(r, b, 2); })) keus = { r: r, a: a, kant: volg[k] };
          else if (binnen(r)) {
            var ov = bezet.reduce(function (som, b) { return som + overlap(r, b); }, 0) + a * 4;
            if (ov < besteO) { besteO = ov; beste = { r: r, a: a, kant: volg[k] }; }
          }
        }
      }
      if (!keus) mislukt = true;
      keus = keus || beste || { r: plek(eigen, AFSTANDEN[0]), a: 0, kant: eigen };
      naam.style.left = (keus.r.left - o.left).toFixed(1) + 'px';
      naam.style.top = (keus.r.top - o.top).toFixed(1) + 'px';
      pt.setAttribute('data-naam-kant', keus.kant);
      if (keus.a > 0) {
        var nx = Math.min(Math.max(cx, keus.r.left), keus.r.right), ny = Math.min(Math.max(cy, keus.r.top), keus.r.bottom);
        var dx = nx - cx, dy = ny - cy, len = Math.hypot(dx, dy), straal = hoofd ? 15 : 14;
        if (len > straal + 2) {
          var lijn = document.createElement('span');
          lijn.className = 'gk-punt__lijn';
          lijn.setAttribute('aria-hidden', 'true');
          lijn.style.left = (cx + dx / len * straal - o.left).toFixed(1) + 'px';
          lijn.style.top = (cy + dy / len * straal - o.top).toFixed(1) + 'px';
          lijn.style.width = (len - straal).toFixed(1) + 'px';
          lijn.style.transform = 'rotate(' + Math.atan2(dy, dx).toFixed(4) + 'rad)';
          pt.insertBefore(lijn, pt.firstChild);
        }
      }
      var nr = naam.getBoundingClientRect();
      bezet.push({ left: nr.left, right: nr.right, top: nr.top, bottom: nr.bottom, isNaam: true });
    });
    /* LEGENDA: past niet elke naam vrij, dan alle namen van de kaart, letters in de spelden en een lijst onder de kaart */
    if (mislukt) {
      beeld.classList.add('ut-kaart--legenda');
      bezet = bezet.filter(function (b) { return !b.isNaam; });
      var ol = document.createElement('ol'), letter = 0;
      ol.className = 'ut-kaart__legenda';
      Array.prototype.forEach.call(beeld.querySelectorAll('.gk-punt'), function (pt) {
        var naam = pt.querySelector('.gk-punt__naam'), hoofd = pt.classList.contains('gk-punt--hoofd');
        if (!naam) return;
        var teken = hoofd ? String.fromCharCode(65 + letter++) : (pt.querySelector('.gk-punt__nr') || {}).textContent;
        if (hoofd) {
          var sp = pt.querySelector('.gk-punt__letter');
          if (!sp) { sp = document.createElement('span'); sp.className = 'gk-punt__letter'; sp.setAttribute('aria-hidden', 'true'); pt.appendChild(sp); }
          sp.textContent = teken;
        }
        var li = document.createElement('li');
        li.className = hoofd ? 'is-hoofd' : 'is-nr';
        var url = !hoofd && pt.getAttribute('href'), pop = !hoofd && pt.getAttribute('data-pop');
        li.innerHTML = '<span class="ut-kaart__teken" aria-hidden="true"></span>' + (url ? '<a></a>' : '<span></span>');
        li.firstChild.textContent = teken;
        li.lastChild.textContent = naam.textContent;
        if (url) li.lastChild.setAttribute('href', url);
        if (pop) li.lastChild.setAttribute('data-pop', pop);
        ol.appendChild(li);
      });
      var veld = beeld.parentNode, opStrook = voet && getComputedStyle(voet).position === 'static';
      if (opStrook) veld.insertBefore(ol, voet); else veld.parentNode.insertBefore(ol, veld.nextSibling);
    }
    Array.prototype.forEach.call(beeld.querySelectorAll('.gk-plaats'), function (d) {
      d.classList.remove('ut-plaats-weg');
      if (d.getAttribute('data-l') == null) d.setAttribute('data-l', d.classList.contains('l') ? '1' : '0');
      var origL = d.getAttribute('data-l') === '1', half = d.classList.contains('stad') ? 5 : 3;
      var zet = function (l) {
        d.classList.toggle('l', l);
        d.style.transform = l ? 'translate(-100%,-50%) translate(' + half + 'px,0px)' : 'translate(0,-50%) translate(' + (-half) + 'px,0px)';
      };
      var vrij = function () { var r = d.getBoundingClientRect(); return !bezet.some(function (b) { return raakt(r, b, 1); }); };
      zet(origL);
      if (vrij()) return;
      zet(!origL);
      if (vrij()) return;
      zet(origL);
      d.classList.add('ut-plaats-weg');
    });
  };
  /* punten: data-punten = '#id' (JSON in de pagina) of een adres */
  var leesPunten = function (bron) {
    if (bron.charAt(0) === '#') {
      var el = document.querySelector(bron);
      return Promise.resolve().then(function () { if (!el) throw new Error('punten ontbreken'); return JSON.parse(el.textContent); });
    }
    return fetch(bron).then(function (r) { if (!r.ok) throw new Error(bron + ' ' + r.status); return r.json(); });
  };
  var bouw = function () {
    var geoUrl = beeld.getAttribute('data-geo'), puntenBron = beeld.getAttribute('data-punten');
    if (!geoUrl || !puntenBron || !window.AsteriaKaart || !window.fetch || !window.Promise) return;
    var geo = fetch(geoUrl).then(function (r) { if (!r.ok) throw new Error(geoUrl + ' ' + r.status); return r.json(); });
    Promise.all([geo, leesPunten(puntenBron)]).then(function (res) {
      var data = res[1];
      var grond = beeld.querySelector('.ut-kaart__grond');
      if (grond) grond.remove();
      beeld.classList.add('is-interactief');
      var smal = beeld.clientWidth < 600;
      /* bureaublad: onderrand 136 (Parkhotel 112) zodat het laagste punt boven de attributieregel en de voetstrook blijft */
      var pad = smal ? { tl: [48, 52], br: [64, 36] } : { tl: [120, 64], br: [150, 136] };
      var kt = function (k, nl) { return beeld.getAttribute('data-t-' + k) || nl; };
      var api = window.AsteriaKaart.maak(beeld, {
        geo: res[0],
        hotel: { lat: data.hotel[0], lng: data.hotel[1], naam: 'Hotel Asteria' },
        vignet: beeld.getAttribute('data-vignet'),
        padding: pad,
        teksten: { in: kt('in', 'Inzoomen'), uit: kt('uit', 'Uitzoomen'), alles: kt('alles', 'Hele kaart tonen'),
          wiel: kt('wiel', 'Ctrl + scrollen om te zoomen'), vingers: kt('vingers', 'Gebruik twee vingers om de kaart te bewegen'),
          attributie: kt('attributie', 'Grenzen CBS/Kadaster &middot; water en wegen &copy; OpenStreetMap-bijdragers') }
      });
      api.zetPunten(data);
      api.overzicht(false);
      pasNamenIn();
      window.utKaart = api;
      if (window.ResizeObserver) {
        var raf = 0;
        new ResizeObserver(function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { if (api.stand().overzicht) pasNamenIn(); }); }).observe(beeld);
      }
    }).catch(function (err) {
      if (window.console) console.warn('kaart: blijft stilstaand', err);
    });
  };
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (items) {
      if (items.some(function (i) { return i.isIntersecting; })) { io.disconnect(); bouw(); }
    }, { rootMargin: '400px 0px' });
    io.observe(beeld);
  } else bouw();
})();
