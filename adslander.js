/* GEDRAG bij het sjabloon adslander.template.html (Duitse Google Ads-landers van Hotel Asteria, eerste: /wellnesshotel-limburg-de).
   Port van parkhotel-site src/gedrag/pagina-adslander.js + blok-kaartenrij.js + blok-hero-video.js + lander-fotorij.js,
   aangevuld met wat lander-w1.js op de andere Asteria-pagina's doet (hier niet geladen: die zet de widget op nl-NL).

   0  KOP in de spiegelstand van /hotel-venray-v2 (lade + submenu's zoals lander-w1.js); --kophoogte = gemeten kophoogte.
   1  MEWS-POORT: de widget wordt pas opgehaald bij de eerste klik op een boekknop (.mews-open of een distributor-link),
      taal de-DE, per link de eigen config uit de href (Winterarrangement = Winter-actie 95c70e27), vouchercode uit
      data-voucher, kamer uit data-room (showRates + open), datums uit mewsStart/mewsEnd in de href (prijskalender).
      Zonder knopparameters: morgen/overmorgen/2 gasten vooraf. Lukt laden niet binnen 8 s: gewoon de link volgen.
   2  HERO-VIDEO: bron pas met script; staand (9:16) onder 768 px, liggend erboven; niet bij reduced motion / Save-Data.
   3  VEEGRIJEN (bouwsteen kaartenrij): teller, pijlen, en met [data-lus] oneindig rondlopen (kamers, fotorij, reviews).
   4  FOTOSLIDER (coverflow, 700 ms cubic-bezier(.32,.72,0,1)) + lightbox; vegen/slepen/wiel.
   5  POP-UP achter de Mehr-info-knoppen (content/adslander-pop-de.json, pas bij gebruik opgehaald).
   6  VRAGEN: tabs Wellness / Allgemein.
   7  Live kamerprijzen (/api/kamer-vanaf), nieuwsbrief inline (/api/nieuwsbrief, taal de), onderbalk telefoon,
      cookiemelding, scratchcard-wachter (niet over een eigen pop-up, de lightbox of de prijskalender).
   Geen bibliotheken. */
(function () {
  'use strict';
  var root = document.documentElement;
  /* taal van de Mews-widget: data-mews-taal op <html> (uitje-sjabloon nl-NL), anders de-DE (adslander) */
  var LANG = root.getAttribute('data-mews-taal') || 'de-DE';
  var zacht = !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var meet = function (naam, extra) {
    window.dataLayer = window.dataLayer || [];
    var o = { event: naam }; for (var k in extra) o[k] = extra[k];
    window.dataLayer.push(o);
    if (typeof window.gtag === 'function') { try { window.gtag('event', naam, extra || {}); } catch (x) {} }
  };

  /* ---- 0 kop over de hero ---- */
  var kop = document.querySelector('.top-stack');
  var heroEl = document.querySelector('.al-hero');
  var meetKop = function () { if (kop) { root.style.setProperty('--kophoogte', kop.offsetHeight + 'px'); root.style.setProperty('--kop-h', kop.offsetHeight + 'px'); } };
  meetKop();
  window.addEventListener('resize', meetKop);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(meetKop);
  /* ---- 0b kop in de spiegelstand (zoals /hotel-venray-v2): mobiele lade en submenu's, 1-op-1 uit lander-w1.js ---- */
  var drawer = document.getElementById('nav-drawer');
  var hamburger = document.querySelector('.nav-hamburger');
  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
    var sl = drawer.querySelector('.nav-drawer__close'); if (sl) sl.focus();
  }
  function sluitDrawer() {
    if (!drawer || !drawer.classList.contains('is-open')) return;
    drawer.classList.remove('is-open');
    document.body.style.overflow = '';
    if (hamburger) { hamburger.setAttribute('aria-expanded', 'false'); hamburger.focus(); }
  }
  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (drawer) {
    drawer.addEventListener('click', function (e) { if (e.target === drawer || e.target.closest('.nav-drawer__close')) sluitDrawer(); });
    drawer.querySelectorAll('.drawer-parent').forEach(function (b) {
      b.addEventListener('click', function () { var li = b.parentElement, open = li.classList.toggle('is-open'); b.setAttribute('aria-expanded', open ? 'true' : 'false'); });
    });
  }
  var subs = document.querySelectorAll('.nav-links .has-sub');
  function sluitSubs(behalve) {
    subs.forEach(function (li) { if (li === behalve) return; li.classList.remove('is-open'); var b = li.querySelector('.nav-parent'); if (b) b.setAttribute('aria-expanded', 'false'); });
  }
  subs.forEach(function (li) {
    var b = li.querySelector('.nav-parent'); if (!b) return;
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !li.classList.contains('is-open');
      sluitSubs(li); li.classList.toggle('is-open', open); b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest || !e.target.closest('.nav-links .has-sub')) sluitSubs(null); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { sluitDrawer(); sluitSubs(null); } });

  /* ---- 1 Mews-poort ---- */
  var STD_CFG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556', HOTEL = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
  var SEL = '.mews-open, a[href*="mews.com/distributor/"]';
  var apis = {}, laden = false, klaar = false, wacht = null, timer = null;
  var cfgVan = function (href) { var m = (href || '').match(/distributor\/([0-9a-fA-F-]{36})/); return m ? m[1].toLowerCase() : STD_CFG; };
  var configs = [STD_CFG];
  Array.prototype.forEach.call(document.querySelectorAll(SEL + ', dialog.ark[data-mews-config]'), function (el) {
    var c = el.getAttribute('data-mews-config') || cfgVan(el.getAttribute('href'));
    if (configs.indexOf(c) < 0) configs.push(c);
  });
  function ymd(d) { var m = d.getMonth() + 1, g = d.getDate(); return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (g < 10 ? '0' : '') + g; }
  function openVoor(el) {
    var href = el.getAttribute('href') || '', api = apis[cfgVan(href)];
    if (!api) return false;
    var p = null; try { p = new URL(href, location.href).searchParams; } catch (x) {}
    var code = el.getAttribute('data-voucher') || (p && p.get('mewsVoucherCode')) || '';
    /* zonder code de code wissen: anders houdt de widget een eerder gezette actiecode vast (arrangementknop -> kamerlink) */
    if (api.setVoucherCode) api.setVoucherCode(code ? code.replace(/[^A-Za-z0-9_-]/g, '') : '');
    if (p) {
      var s = p.get('mewsStart'), e = p.get('mewsEnd'), a = p.get('mewsAdultCount');
      if (s && api.setStartDate) api.setStartDate(new Date(s));
      if (e && api.setEndDate) api.setEndDate(new Date(e));
      if (a && api.setAdultCount) { try { api.setAdultCount(parseInt(a, 10)); } catch (x) {} }
    }
    var kamer = el.getAttribute('data-room') || (p && p.get('mewsRoom')) || '';
    if (api.setLanguageCode) api.setLanguageCode(LANG);
    /* showRates() kiest alleen de kamer; open() daarna opent de widget op de kamerstap (lander-w1.js, 14 okt 2026) */
    if (kamer && api.showRates) { try { api.showRates(kamer); } catch (x) {} }
    api.open();
    meet('mews_open', { voucher: code, kamer: kamer });
    if (window.track) { try { window.track('mews_click'); } catch (x) {} }
    return true;
  }
  function conversie(res) {
    try {
      var val = null;
      if (res && res.length) val = res.reduce(function (t, r) { return t + (r.totalCost && r.totalCost.value ? r.totalCost.value : 0); }, 0);
      var tx = (res && res[0] && (res[0].reservationGroupId || res[0].id)) || Date.now().toString(36);
      if (typeof window.gtag === 'function') {
        if (val) window.gtag('event', 'purchase', { send_to: 'G-DPCP945DCG', value: val, currency: 'EUR', transaction_id: tx });
        if (window.GA_ADS_LABEL) window.gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL, value: val || 0, currency: 'EUR', transaction_id: tx });
      }
    } catch (x) {}
  }
  function init() {
    if (!window.Mews || !window.Mews.Distributor) { setTimeout(init, 80); return; }
    var MP = /[?&]mews[A-Z]/.test(location.search), morgen = new Date(), over = new Date();
    morgen.setDate(morgen.getDate() + 1); over.setDate(over.getDate() + 2);
    configs.forEach(function (c) {
      var opt = { configurationIds: [c], language: LANG, onBookingFinished: conversie };
      if (c === STD_CFG && !MP) { opt.startDate = ymd(morgen); opt.endDate = ymd(over); opt.adultCount = 2; opt.hotelId = HOTEL; }
      window.Mews.Distributor(opt, function (api) {
        apis[c] = api; if (api.setLanguageCode) api.setLanguageCode(LANG);
        if (wacht && cfgVan(wacht.getAttribute('href')) === c) { var el = wacht; wacht = null; klaar = true; if (timer) { clearTimeout(timer); timer = null; } openVoor(el); }
        if (c === STD_CFG) klaar = true;
      });
    });
  }
  function laad() {
    if (laden) return; laden = true;
    var s = document.createElement('script'); s.async = true; s.src = 'https://app.mews.com/distributor/distributor.min.js';
    s.onerror = function () { laden = false; if (wacht && wacht.href) location.href = wacht.href; };
    (document.head || root).appendChild(s);
    init();
  }
  window.alMewsLaad = laad;
  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest(SEL) : null;
    if (!el || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    if (window.alPopDicht) window.alPopDicht(true);
    sluitDrawer();
    if (apis[cfgVan(el.getAttribute('href'))]) { openVoor(el); return; }
    wacht = el; laad();
    if (!timer) timer = setTimeout(function () { timer = null; if (wacht && wacht.href) location.href = wacht.href; }, 8000);
  }, true);
  if (/[?&]mewsDistributorOpened\b/.test(location.search)) laad();

  /* ---- 2 hero-video ---- */
  (function () {
    var v = document.querySelector('video[data-bron-bureaublad]');
    if (!v || !window.matchMedia || !zacht) return;
    if (navigator.connection && navigator.connection.saveData) return;
    var bron = v.getAttribute(matchMedia('(min-width: 768px)').matches ? 'data-bron-bureaublad' : 'data-bron-mobiel');
    if (!bron) return;
    v.addEventListener('playing', function () { v.classList.add('is-speelt'); });
    v.muted = true; v.src = bron; v.load();
    var p = v.play(); if (p && p.catch) p.catch(function () {});
    /* iOS-energiebesparing: bij de eerste tik alsnog starten */
    document.addEventListener('touchstart', function t() { document.removeEventListener('touchstart', t); if (v.paused) { var q = v.play(); if (q && q.catch) q.catch(function () {}); } }, { passive: true });
  })();

  /* ---- 0b vegen op alle invoer (vinger, muis slepen, trackpad/shift+wiel) voor slider, lightbox en pop-up ---- */
  var laatsteSleep = 0;
  window.addEventListener('click', function (e) {
    if (Date.now() - laatsteSleep < 350) { e.preventDefault(); e.stopImmediatePropagation(); laatsteSleep = 0; }
  }, true);
  var veegbaar = function (el, o) {
    var x0 = 0, y0 = 0, t0 = 0, as = '', actief = false, dx = 0;
    el.addEventListener('dragstart', function (e) { e.preventDefault(); });
    el.addEventListener('pointerdown', function (e) {
      if (e.button || !e.isPrimary || (o.niet && e.target.closest(o.niet))) return;
      actief = true; as = ''; dx = 0; x0 = e.clientX; y0 = e.clientY; t0 = Date.now();
    });
    window.addEventListener('pointermove', function (e) {
      if (!actief || !e.isPrimary) return;
      dx = e.clientX - x0; var dy = e.clientY - y0;
      if (!as) {
        if (Math.abs(dx) > 6 && Math.abs(dx) > Math.abs(dy)) { as = 'x'; el.classList.add('is-sleept'); o.start(); }
        else if (Math.abs(dy) > 6) { actief = false; return; }
      }
      if (as === 'x') o.beweeg(dx);
    });
    var los = function (e) {
      if (!actief || !e.isPrimary) return; actief = false;
      if (as !== 'x') return;
      el.classList.remove('is-sleept'); laatsteSleep = Date.now();
      var snel = Math.abs(dx) > 30 && Math.abs(dx) / Math.max(1, Date.now() - t0) > 0.35;
      o.einde(dx, snel);
    };
    window.addEventListener('pointerup', los);
    window.addEventListener('pointercancel', function (e) { if (actief && as === 'x') { dx = 0; los(e); } actief = false; });
    var som = 0, rust = null, vast = false;
    el.addEventListener('wheel', function (e) {
      var h = e.deltaX || (e.shiftKey ? e.deltaY : 0);
      if (!h || (!e.shiftKey && Math.abs(e.deltaX) <= Math.abs(e.deltaY))) return;
      e.preventDefault();
      clearTimeout(rust); rust = setTimeout(function () { vast = false; som = 0; }, 180);
      if (vast) return;
      som += h;
      if (Math.abs(som) > 30) { vast = true; o.wiel(som > 0 ? 1 : -1); som = 0; }
    }, { passive: false });
  };

  /* ---- 3 veegrijen (port van gedrag/blok-kaartenrij): eerst de reviewrij op het bureaublad als lus aanzetten ---- */
  (function () {
    if (!window.matchMedia || !matchMedia('(min-width:1024px)').matches) return;
    var s = document.querySelector('.al-rev__strook');
    if (s) { s.setAttribute('data-rij', ''); s.setAttribute('data-lus', ''); }
  })();
  (function () {
    function zichtbaar(spoor) { return Array.prototype.filter.call(spoor.children, function (k) { return k.nodeType === 1 && !k.hidden; }); }
    function maakRij(rij) {
      var spoor = rij.querySelector('[data-spoor]'), teller = rij.querySelector('[data-teller]'), pijlen = rij.querySelectorAll('[data-stap]');
      if (!spoor) return;
      function stap() { var k = zichtbaar(spoor)[0]; if (!k) return spoor.clientWidth; var s = getComputedStyle(spoor), g = parseFloat(s.columnGap || s.gap) || 0; return k.getBoundingClientRect().width + g; }
      function perScherm() { var b = stap(); return b ? Math.max(1, Math.round(spoor.clientWidth / b)) : 1; }
      function ververs() {
        var n = zichtbaar(spoor).length; if (!n) return;
        var b = stap(), max = spoor.scrollWidth - spoor.clientWidth, i = max > 4 ? Math.round(spoor.scrollLeft / b) : 0;
        if (spoor.scrollLeft >= max - 2) i = Math.max(0, n - perScherm());
        i = Math.max(0, Math.min(n - 1, i));
        if (teller) teller.textContent = (i + 1) + '/' + n;
        if (pijlen[0]) pijlen[0].disabled = spoor.scrollLeft <= 2;
        if (pijlen[1]) pijlen[1].disabled = spoor.scrollLeft >= max - 2;
      }
      Array.prototype.forEach.call(pijlen, function (p) { p.addEventListener('click', function () { spoor.scrollBy({ left: stap() * Number(p.getAttribute('data-stap')), behavior: 'smooth' }); }); });
      var w = null;
      spoor.addEventListener('scroll', function () { clearTimeout(w); w = setTimeout(ververs, 90); }, { passive: true });
      window.addEventListener('resize', function () { clearTimeout(w); w = setTimeout(ververs, 150); });
      ververs();
    }
    function maakLus(rij) {
      var spoor = rij.querySelector('[data-spoor]'), teller = rij.querySelector('[data-teller]'), pijlen = rij.querySelectorAll('[data-stap]');
      if (!spoor) return;
      var origineel = zichtbaar(spoor), n0 = origineel.length; if (!n0) return;
      var kVoor = [], kNa = [];
      function kloonset(bak) {
        var stuk = document.createDocumentFragment();
        for (var i = 0; i < n0; i++) {
          var k = origineel[i].cloneNode(true);
          k.setAttribute('data-kloon', ''); k.setAttribute('aria-hidden', 'true');
          Array.prototype.forEach.call(k.querySelectorAll('a,button,input,select,textarea'), function (e) { e.setAttribute('tabindex', '-1'); });
          bak.push(k); stuk.appendChild(k);
        }
        return stuk;
      }
      spoor.insertBefore(kloonset(kVoor), origineel[0]);
      spoor.appendChild(kloonset(kNa));
      function stap() { var k = zichtbaar(spoor)[0]; if (!k) return spoor.clientWidth; var s = getComputedStyle(spoor), g = parseFloat(s.columnGap || s.gap) || 0; return k.getBoundingClientRect().width + g; }
      function perScherm() { var b = stap(); if (!b) return 1; var s = getComputedStyle(spoor), binnen = spoor.clientWidth - (parseFloat(s.paddingLeft) || 0) - (parseFloat(s.paddingRight) || 0); return Math.max(1, Math.round(binnen / b)); }
      function stil(fn) { var oud = spoor.style.scrollBehavior; spoor.style.scrollBehavior = 'auto'; fn(); spoor.style.scrollBehavior = oud; }
      var lusUit = false, doel = null, laatsteStap = 0, laatstePer = 0;
      function ververs() {
        var n = n0, b = stap(); if (!b) return;
        if (lusUit) {
          var max = spoor.scrollWidth - spoor.clientWidth, i = max > 4 ? Math.round(spoor.scrollLeft / b) : 0;
          if (spoor.scrollLeft >= max - 2) i = Math.max(0, n - perScherm());
          if (teller) teller.textContent = (Math.max(0, Math.min(n - 1, i)) + 1) + '/' + n;
          if (pijlen[0]) pijlen[0].disabled = spoor.scrollLeft <= 2;
          if (pijlen[1]) pijlen[1].disabled = spoor.scrollLeft >= max - 2;
          return;
        }
        var j = Math.round(spoor.scrollLeft / b);
        if (j < n) j += n; else if (j >= 2 * n) j -= n;
        var wens = j * b;
        if (Math.abs(spoor.scrollLeft - wens) > 1) stil(function () { spoor.scrollLeft = wens; });
        if (teller) teller.textContent = (((j - n) % n + n) % n + 1) + '/' + n;
        if (pijlen[0]) pijlen[0].disabled = false;
        if (pijlen[1]) pijlen[1].disabled = false;
      }
      Array.prototype.forEach.call(pijlen, function (p) {
        p.addEventListener('click', function () {
          var b = stap(); if (!b) return;
          var r = Number(p.getAttribute('data-stap'));
          if (lusUit) { spoor.scrollBy({ left: b * r, behavior: 'smooth' }); return; }
          var vanaf = doel === null ? Math.round(spoor.scrollLeft / b) * b : doel;
          doel = vanaf + b * r;
          spoor.scrollTo({ left: doel, behavior: zacht ? 'smooth' : 'auto' });
        });
      });
      function gestopt() { ververs(); doel = null; }
      var w = null;
      if ('onscrollend' in window) spoor.addEventListener('scrollend', gestopt);
      else spoor.addEventListener('scroll', function () { clearTimeout(w); w = setTimeout(gestopt, 90); }, { passive: true });
      function herzet() {
        var b = stap(); if (!b) return;
        var p = perScherm();
        lusUit = !(n0 > p);
        for (var i = 0; i < n0; i++) { kVoor[i].hidden = lusUit; kNa[i].hidden = lusUit; }
        b = stap(); laatsteStap = b; laatstePer = p; doel = null;
        stil(function () { spoor.scrollLeft = lusUit ? 0 : n0 * b; });
        ververs();
      }
      var wm = null;
      window.addEventListener('resize', function () {
        clearTimeout(wm);
        wm = setTimeout(function () { if (Math.abs(stap() - laatsteStap) > 1 || perScherm() !== laatstePer) herzet(); else ververs(); }, 150);
      });
      herzet();
      /* een foto die later binnenkomt verandert de maat: opnieuw zetten */
      Array.prototype.forEach.call(spoor.querySelectorAll('img'), function (im) { if (!im.complete) im.addEventListener('load', function () { if (Math.abs(stap() - laatsteStap) > 1) herzet(); }, { once: true }); });
    }
    Array.prototype.forEach.call(document.querySelectorAll('[data-rij]'), function (r) { if (r.hasAttribute('data-lus')) maakLus(r); else maakRij(r); });
  })();

  /* fotorij: actieve foto's vol, de rest gedimd (port van gedrag/lander-fotorij) */
  Array.prototype.forEach.call(document.querySelectorAll('[data-fotorij]'), function (spoor) {
    var bezig = false;
    function ijk() {
      bezig = false;
      var fotos = Array.prototype.filter.call(spoor.children, function (el) { return el.nodeType === 1 && !el.hidden; });
      if (!fotos.length) return;
      var st = fotos[0].getBoundingClientRect().width + (parseFloat(getComputedStyle(spoor).columnGap) || 0);
      var eerste = st > 0 ? Math.round(spoor.scrollLeft / st) : 0, vol = matchMedia('(min-width:1024px)').matches ? 3 : 1;
      for (var i = 0; i < fotos.length; i++) fotos[i].classList.toggle('is-vol', i >= eerste && i < eerste + vol);
    }
    spoor.classList.add('js'); ijk();
    spoor.addEventListener('scroll', function () { if (bezig) return; bezig = true; requestAnimationFrame(ijk); }, { passive: true });
    window.addEventListener('resize', ijk);
  });

  /* ---- 4 fotoslider (coverflow) ---- */
  var STANDEN = { '-3': 'm3', '-2': 'm2', '-1': 'm1', '0': '0', '1': 'p1', '2': 'p2', '3': 'p3' };
  Array.prototype.forEach.call(document.querySelectorAll('[data-rond]'), function (rond) {
    var items = Array.prototype.slice.call(rond.querySelectorAll('.al-rond__item'));
    var n = items.length, actief = 0;
    if (!n) return;
    var status = rond.querySelector('.al-rond__status');
    function zet() {
      items.forEach(function (li, i) {
        var d = ((i - actief) % n + n) % n; if (d > n / 2) d -= n;
        li.className = 'al-rond__item al-rond__item--' + (STANDEN[String(d)] || 'weg');
        var knop = li.querySelector('.al-rond__vergroot'), zicht = Math.abs(d) <= 2;
        if (knop) knop.tabIndex = zicht ? 0 : -1;
        li.setAttribute('aria-hidden', zicht ? 'false' : 'true');
      });
      if (status) { var img = items[actief].querySelector('img'); status.textContent = (actief + 1) + '/' + n + (img && img.alt ? ', ' + img.alt : ''); }
    }
    function stap(s) { actief = ((actief + s) % n + n) % n; zet(); }
    Array.prototype.forEach.call(rond.querySelectorAll('[data-rond-stap]'), function (p) { p.addEventListener('click', function () { stap(Number(p.getAttribute('data-rond-stap'))); }); });
    var rij = rond.querySelector('.al-rond__rij');
    if (rij) {
      rij.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') { e.preventDefault(); stap(-1); } else if (e.key === 'ArrowRight') { e.preventDefault(); stap(1); }
      });
      rij.addEventListener('click', function (e) {
        if (e.target.closest('.al-rond__vergroot')) return;
        var li = e.target.closest('.al-rond__item'); if (!li) return;
        var i = items.indexOf(li); if (i > -1 && i !== actief) { actief = i; zet(); }
      });
    }
    zet();
    rond.__naar = function (i) { actief = ((i % n) + n) % n; zet(); };
    rond.__actief = function () { return actief; };
    if (rij && n > 1) {
      var maat = null, stapPx = 1;
      var meetStanden = function () {
        var m = {};
        items.forEach(function (li, i) {
          var d = ((i - actief) % n + n) % n; if (d > n / 2) d -= n;
          if (Math.abs(d) > 3) return;
          var cs = getComputedStyle(li), t = cs.transform, mx = [1, 0, 0, 1, 0, 0];
          if (t && t !== 'none') mx = t.replace(/^matrix\(|\)$/g, '').split(',').map(Number);
          m[d] = { s: mx[0], x: mx[4], y: mx[5], o: Number(cs.opacity) };
        });
        for (var k = -3; k <= 3; k++) if (!m[k]) m[k] = m[k < 0 ? k + 1 : k - 1] || m[0];
        return m;
      };
      var tussen = function (p) {
        p = Math.max(-3, Math.min(3, p));
        var a = Math.floor(p), b = Math.min(3, a + 1), f = p - a, A = maat[a], B = maat[b];
        return { s: A.s + (B.s - A.s) * f, x: A.x + (B.x - A.x) * f, y: A.y + (B.y - A.y) * f, o: A.o + (B.o - A.o) * f };
      };
      rij.querySelectorAll('img').forEach(function (im) { im.setAttribute('draggable', 'false'); });
      veegbaar(rij, {
        niet: '[data-rond-stap]',
        start: function () { maat = meetStanden(); stapPx = Math.abs(maat[1].x - maat[0].x) || 1; items.forEach(function (li) { li.style.transition = 'none'; }); },
        beweeg: function (dx) {
          var f = Math.max(-1.2, Math.min(1.2, dx / stapPx));
          items.forEach(function (li, i) {
            var d = ((i - actief) % n + n) % n; if (d > n / 2) d -= n;
            var p = d + f;
            if (Math.abs(p) > 3.5) { li.style.opacity = '0'; return; }
            var w = tussen(p);
            li.style.transform = 'matrix(' + w.s + ',0,0,' + w.s + ',' + w.x + ',' + w.y + ')';
            li.style.opacity = String(Math.max(0, Math.min(1, w.o)));
            li.style.zIndex = String(Math.max(0, 3 - Math.round(Math.abs(p))));
          });
        },
        einde: function (dx, snel) {
          var f = dx / stapPx, st = 0;
          if (Math.abs(f) > 0.4 || snel) st = (f < 0 ? 1 : -1) * Math.max(1, Math.round(Math.abs(f)));
          items.forEach(function (li) { li.style.transition = ''; });
          void rij.offsetWidth;
          items.forEach(function (li) { li.style.transform = ''; li.style.opacity = ''; li.style.zIndex = ''; });
          stap(st);
        },
        wiel: function (r) { stap(r); }
      });
    }
    var imgs = rond.querySelectorAll('img');
    var laadAlle = function () { Array.prototype.forEach.call(imgs, function (im) { im.loading = 'eager'; if (im.decode) im.decode().catch(function () {}); }); };
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (e) { if (e[0].isIntersecting) { io.disconnect(); laadAlle(); } }, { rootMargin: '800px 0px' });
      io.observe(rond);
    } else laadAlle();
  });

  /* lightbox */
  var lb = document.querySelector('[data-lb]');
  if (lb) {
    var lbBeeld = lb.querySelector('.al-lb__beeld'), lbSluit = lb.querySelector('[data-lb-sluit]'),
        lbTeller = lb.querySelector('.al-lb__teller'), lbOnder = lb.querySelector('.al-lb__bijschrift'),
        lbKnoppen = Array.prototype.slice.call(lb.querySelectorAll('button')), lijst = [], nu = 0, rondEl = null, terug = null;
    var bron = function (li) { var k = li.querySelector('.al-rond__vergroot'), im = li.querySelector('img'); return { src: (k && k.getAttribute('data-groot')) || (im && im.src) || '', alt: im ? im.alt : '' }; };
    var voorladen = function (i) { var b = lijst[(i + lijst.length) % lijst.length]; if (b) { var im = new Image(); im.src = bron(b).src; } };
    var toon = function (i, fade) {
      nu = (i + lijst.length) % lijst.length;
      var b = bron(lijst[nu]);
      lbTeller.textContent = (nu + 1) + '/' + lijst.length; lbOnder.textContent = b.alt;
      var zetB = function () {
        if (lijst[nu] && bron(lijst[nu]).src !== b.src) return;
        lbBeeld.src = b.src; lbBeeld.alt = b.alt;
        if (fade && zacht && lbBeeld.animate) lbBeeld.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, easing: 'ease-out' });
      };
      if (!fade) zetB(); else { var pre = new Image(); pre.onload = pre.onerror = zetB; pre.src = b.src; if (pre.complete) { pre.onload = pre.onerror = null; zetB(); } }
      voorladen(nu + 1); voorladen(nu - 1);
    };
    var lbOpen = function (knop) {
      rondEl = knop.closest('[data-rond]');
      lijst = rondEl ? Array.prototype.slice.call(rondEl.querySelectorAll('.al-rond__item')) : [knop.closest('li')];
      terug = knop;
      toon(Math.max(0, lijst.indexOf(knop.closest('.al-rond__item'))), false);
      lb.hidden = false; root.classList.add('al-lb-open'); lbSluit.focus();
    };
    var lbDicht = function () {
      if (lb.hidden) return;
      lb.hidden = true; root.classList.remove('al-lb-open');
      if (rondEl && rondEl.__naar) rondEl.__naar(nu);
      var k = lijst[nu] && lijst[nu].querySelector('.al-rond__vergroot');
      (k || terug) && (k || terug).focus({ preventScroll: true });
    };
    document.addEventListener('click', function (e) {
      var k = e.target.closest ? e.target.closest('.al-rond__vergroot') : null;
      if (k) { e.preventDefault(); e.stopPropagation(); lbOpen(k); }
    }, true);
    lb.addEventListener('click', function (e) {
      var st = e.target.closest('[data-lb-stap]');
      if (st) { toon(nu + Number(st.getAttribute('data-lb-stap')), true); return; }
      if (e.target.closest('[data-lb-sluit]') || e.target === lb || e.target.classList.contains('al-lb__kader')) lbDicht();
    });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') lbDicht();
      else if (e.key === 'ArrowRight') { e.preventDefault(); toon(nu + 1, true); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); toon(nu - 1, true); }
      else if (e.key === 'Tab') { e.preventDefault(); var i = lbKnoppen.indexOf(document.activeElement); lbKnoppen[(i + (e.shiftKey ? -1 : 1) + lbKnoppen.length) % lbKnoppen.length].focus(); }
    });
    lbBeeld.setAttribute('draggable', 'false');
    veegbaar(lb, {
      niet: 'button',
      start: function () { lbBeeld.style.transition = 'none'; },
      beweeg: function (dx) { lbBeeld.style.transform = 'translateX(' + dx + 'px)'; },
      einde: function (dx, snel) {
        lbBeeld.style.transition = 'transform .3s ease'; lbBeeld.style.transform = '';
        if (Math.abs(dx) > lb.clientWidth * 0.15 || snel) { lbBeeld.style.transition = 'none'; toon(nu + (dx < 0 ? 1 : -1), true); }
      },
      wiel: function (r) { toon(nu + r, true); }
    });
  }

  /* ---- 5 pop-up achter de Mehr-info-knoppen ---- */
  var popEl = document.querySelector('[data-pop-dialog]');
  if (popEl && popEl.getAttribute('data-bron')) {
    var POP = null, popLaden = null;
    var haalPop = function () {
      /* data-bron '#id' = de inhoud staat in de pagina (script type=application/json, uitje-sjabloon); anders ophalen */
      var bronAttr = popEl.getAttribute('data-bron'), inline = bronAttr.charAt(0) === '#' ? document.querySelector(bronAttr) : null;
      if (!popLaden && inline) popLaden = Promise.resolve().then(function () { return JSON.parse(inline.textContent); })
        .then(function (d) { POP = d; return d; }).catch(function () { popLaden = null; return null; });
      if (!popLaden) popLaden = fetch(bronAttr).then(function (r) { if (!r.ok) throw r; return r.json(); })
        .then(function (d) { POP = d; return d; }).catch(function () { popLaden = null; return null; });
      return popLaden;
    };
    var POPKNOP = '[data-pop]';
    ['pointerover', 'focusin', 'touchstart'].forEach(function (ev) {
      document.addEventListener(ev, function (e) { if (!POP && e.target.closest && e.target.closest(POPKNOP + ', [data-kamer]')) haalPop(); }, { passive: true });
    });
    var kaartEl = popEl.querySelector('.al-pop__kaart'), L = popEl.dataset, popTerug = null, popIdx = 0, popN = 0, popSoort = '', popSleutel = '', popOpenIdx = false;
    var VINK = '<svg class="al-vink" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>';
    var SPEEL = '<svg class="al-pop__ico-speel" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9.5-5.5z"/></svg><svg class="al-pop__ico-pauze" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 2.5h3v11h-3zM9.5 2.5h3v11h-3z"/></svg>';
    var PL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>';
    var PR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>';
    var KRUIS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    var REIS = {
      auto: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.75 15.25V13a2 2 0 0 1 1.5-1.94l2.1-.53 2.05-2.9a2 2 0 0 1 1.63-.88h4.1a2 2 0 0 1 1.6.8l2.27 3.03 1.8.45A2 2 0 0 1 21.25 13v2.25"/><path d="M2.75 15.25h1.9M9.15 15.25h5.7M19.35 15.25h1.9"/><path d="M6.35 10.6h11.9M12 6.75v3.85"/><circle cx="6.9" cy="15.75" r="2.25"/><circle cx="17.1" cy="15.75" r="2.25"/></svg>',
      voet: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="13.6" cy="4.1" r="1.75"/><path d="M12.6 7.6 10.4 13.2 8.2 20.5"/><path d="M10.4 13.2 13.2 16l1 4.5"/><path d="M12.3 8.4l2.3 3 2.4.8"/><path d="M12 8.5 9.2 10.2l-1 2.6"/></svg>',
      rad: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.75" cy="16.25" r="3.5"/><circle cx="18.25" cy="16.25" r="3.5"/><path d="M5.75 16.25h5.75l4.1-6.85M5.75 16.25 9.3 9.4l2.2 6.85M9.3 9.4h6.3l2.65 6.85"/><path d="M15.6 9.4l-.5-2.65h2.3M9.3 9.4l-.4-2h-1.4h3"/></svg>',
      start: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
    };
    var plat = function (h) { var x = document.createElement('div'); x.innerHTML = h || ''; return x.textContent; };
    var esc = function (t) { var x = document.createElement('div'); x.textContent = t == null ? '' : String(t); return x.innerHTML; };
    var tekstVan = function (el, sel) { var e = el && el.querySelector(sel); return e ? e.innerHTML.trim() : ''; };
    /* bureaublad (>= 1024): geen scrollen in de pop-up, dus de omschrijving begrensd op de eerste 3 hele zinnen */
    var kortDesc = function (t) {
      if (!t || !(window.matchMedia && matchMedia('(min-width:1024px)').matches)) return t;
      var re = /([.!?])\s+(?=[A-ZÄÖÜ„"])/g, m, n = 0, s = String(t);
      while ((m = re.exec(s))) {
        var voor = s.slice(0, m.index).split(/\s/).pop();
        if (m[1] === '.' && (/^\S{0,2}$/.test(voor) || /^(ca|bzw|inkl|zzgl|evtl|max|min|Nr|Str|etc|usw)$/i.test(voor))) continue;
        if (++n === 3) return s.slice(0, m.index + 1);
      }
      return s;
    };
    var heroBoek = function () { var h = document.querySelector('.al-hero .mews-open'); return h ? h.getAttribute('href') : ''; };
    /* arrangement-pop-up = kiezeroptie c "Fotoband bovenaan met boekkaart" (letterlijk nagebouwd): bovenaan drie foto's als
       mozaiek (telefoon: een groot + twee klein), sluitkruis rond op de band; daaronder links pil, naam, subregel, omschrijving
       en Das ist inbegriffen (bureaublad twee kolommen), rechts een boekkaart met de prijs van de kaart, de zondagregel (alleen
       als de kaart data-zondag="ja" heeft), drie zekerheden en Arrangement buchen. Telefoon: de knop vast onderin. De knop is de
       kaartknop (mews-open + data-voucher), dus de prijskalender opent zoals vanaf de kaart. */
    var PCVINK = '<svg class="al-pc-vink" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>';
    var PCKAL = '<svg class="as-icoon" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>';
    var bouwArr = function (r, kaart) {
      var naam = tekstVan(kaart, '.al-ak__naam') || esc(r.naam), badge = tekstVan(kaart, '.al-ak__tag');
      var pr = kaart && kaart.querySelector('.al-ak__prijs'), bedragEl = pr && pr.querySelector('[data-arr-vanaf]') || (pr && pr.querySelectorAll('span')[1]);
      var vf = tekstVan(kaart, '.al-ak__vf'), eenheid = tekstVan(kaart, '.al-ak__prijs small');
      var k = kaart && kaart.querySelector('.al-ak__knop');
      var knopHtml = k ? '<a class="btn btn-primary al-pop__boek mews-open" href="' + esc(k.getAttribute('href')) + '" data-voucher="' + esc(k.getAttribute('data-voucher')) + '" data-pop-boek>' + esc(L.lArrboek) + '</a>' : '';
      var zondag = kaart && kaart.getAttribute('data-zondag') === 'ja' && L.lZondag;
      var fotos = (r.fotos || []).slice(0, 3);
      var zeker = (L.lZeker || '').split('|').filter(Boolean);
      popN = 0; popIdx = 0;
      return '<div class="al-pc-band">' + fotos.map(function (f, i) { return '<img class="al-pc-foto" src="' + esc(f) + '" alt="' + (i ? '' : esc(plat(naam))) + '" decoding="async" draggable="false">'; }).join('') +
          '<button type="button" class="al-pc-sluit" data-pop-sluit aria-label="' + esc(L.lSluit) + '">' + KRUIS + '</button></div>' +
        '<div class="al-pc-scroll"><div class="al-pc-tekst">' +
          (badge ? '<span class="al-pop__badge">' + badge + '</span>' : '') +
          '<h3 class="al-pop__naam al-pc-naam" id="al-pop-naam">' + naam + '</h3>' +
          (r.sub ? '<p class="al-pc-sub">' + esc(r.sub) + '</p>' : '') +
          '<p class="al-pc-desc">' + esc(r.desc) + '</p>' +
          (r.incl && r.incl.length ? '<p class="al-pop__tk al-pc-tk">' + esc(L.lIncl) + '</p><ul class="al-pc-lijst">' + r.incl.map(function (i) { return '<li>' + PCVINK + '<span>' + esc(i) + '</span></li>'; }).join('') + '</ul>' : '') +
        '</div><aside class="al-pc-boek" aria-label="' + esc(L.lArrboek) + '">' +
          '<p class="al-pc-prijs"><span class="vf">' + vf + '</span><b>' + (bedragEl ? bedragEl.innerHTML : '') + '</b><small>' + eenheid + '</small></p>' +
          (zondag ? '<p class="al-pc-zondag">' + PCKAL + '<span>' + esc(L.lZondag) + '</span></p>' : '') +
          (zeker.length ? '<ul class="al-pc-zeker">' + zeker.map(function (z) { return '<li>' + PCVINK + '<span>' + esc(z) + '</span></li>'; }).join('') + '</ul>' : '') +
          knopHtml + '</aside></div>' +
        (knopHtml ? '<div class="al-pc-voet">' + knopHtml + '</div>' : '');
    };
    var bouw = function (soort, sleutel, knop) {
      var r = ((POP || {})[soort] || {})[sleutel]; if (!r) return null;
      var kaart = knop.closest('.al-ak, .kk-kaart, .al-tegel, .al-uk');
      var naam = r.naam || '', badge = '', prijs = '', kenm = '', extra = '', voet = '', sub = r.sub || '';
      var boek = null, boeklabel = '', boekAttr = '', ext = false;
      if (soort === 'arr') return bouwArr(r, kaart);
      if (soort === 'arr-oud') {
        naam = tekstVan(kaart, '.al-ak__naam') || esc(naam); badge = tekstVan(kaart, '.al-ak__tag');
        var pb = kaart && kaart.querySelector('.al-ak__prijsblok'); prijs = pb ? '<div class="al-pop__prijs">' + pb.innerHTML + '</div>' : '';
        if (r.incl && r.incl.length) extra += '<p class="al-pop__tk">' + esc(L.lIncl) + '</p><ul class="al-pop__lijst">' + r.incl.map(function (i) { return '<li>' + VINK + '<span>' + esc(i) + '</span></li>'; }).join('') + '</ul>';
        var k = kaart && kaart.querySelector('.al-ak__knop');
        if (k) { boek = k.getAttribute('href'); boekAttr = ' data-voucher="' + esc(k.getAttribute('data-voucher')) + '"'; }
        boeklabel = L.lArrboek;
      } else if (soort === 'kamer') {
        naam = esc(naam); badge = esc(L.lKamerbadge);
        var kp = kaart && kaart.querySelector('.kk-prijs.is-gevuld'); prijs = kp ? '<p class="al-pop__kamerprijs">' + kp.innerHTML + '</p>' : '';
        kenm = r.kenmerken;
        var kb = kaart && kaart.querySelector('.mews-open[data-room]');
        if (kb) { boek = kb.getAttribute('href'); boekAttr = ' data-room="' + esc(kb.getAttribute('data-room')) + '"'; }
        boeklabel = L.lKamerboek;
      } else if (soort === 'fac') {
        naam = tekstVan(kaart, '.al-tegel__naam'); badge = esc(L.lFacbadge); kenm = r.kenmerken;
        if (r.hotelboek) { boek = heroBoek(); boeklabel = L.lHotelboek; }
      } else if (soort === 'uitje') {
        /* zonder kaart (genummerde knop op de kaart) komen naam en categorie uit de pop-updata */
        naam = tekstVan(kaart, '.al-uk__naam') || esc(r.naam); badge = tekstVan(kaart, '.al-uk__cat') || esc(r.cat || '');
        var reis = ['auto', 'voet', 'rad'].filter(function (x) { return r[x]; }).map(function (x) {
          return '<span>' + REIS[x] + '<b>' + esc(r[x]) + '</b> ' + esc(L['l' + x.charAt(0).toUpperCase() + x.slice(1)]) + '</span>'; }).join('');
        if (r.start) reis += '<span>' + REIS.start + '<b>' + esc(r.start) + '</b></span>';
        if (reis) extra += '<p class="al-pop__reis" aria-label="' + esc(L.lVanaf) + '">' + reis + '</p>';
        if (r.credit) extra += '<p class="al-pop__credit">' + esc(r.credit) + '</p>';
        if (r.route) { boek = r.route; boeklabel = L.lRoute; ext = true; }
      }
      var fotos = (soort === 'kamer' && r.pop_fotos) || r.fotos || [], vid = r.video || ''; popN = fotos.length + (vid ? 1 : 0); popIdx = 0;
      var dia = (vid ? '<div class="al-pop__vid"><video class="al-pop__video" muted playsinline loop preload="none" poster="' + esc(fotos[0] || '') + '" data-src="' + esc(vid) + '" aria-label="' + esc(plat(naam)) + '"></video>' +
          '<button type="button" class="al-pop__speel" data-pop-speel aria-label="' + esc(L.lSpeel) + '">' + SPEEL + '</button></div>' : '') +
        fotos.map(function (f, i) { return '<img class="al-pop__foto" draggable="false" data-src="' + esc(f) + '" alt="' + (i === 0 && !vid ? esc(plat(naam)) : '') + '" decoding="async">'; }).join('');
      var nav = popN > 1 ? '<button type="button" class="al-pop__pijl al-pop__pijl--vorige" data-pop-stap="-1" aria-label="' + esc(L.lVorige) + '">' + PL + '</button><button type="button" class="al-pop__pijl al-pop__pijl--volgende" data-pop-stap="1" aria-label="' + esc(L.lVolgende) + '">' + PR + '</button><div class="al-pop__dots">' + Array.apply(null, Array(popN)).map(function (_, i) { return '<button type="button" class="al-pop__dot' + (i ? '' : ' is-aan') + '" data-pop-dot="' + i + '" aria-label="' + (i + 1) + '/' + popN + '"></button>'; }).join('') + '</div>' : '';
      if (kenm && kenm.length) extra = '<ul class="al-pop__kenmerken">' + kenm.map(function (x) { return '<li>' + VINK + '<span>' + esc(x) + '</span></li>'; }).join('') + '</ul>' + extra;
      if (boek) {
        voet = '<div class="al-pop__voet"><a class="btn btn-primary al-pop__boek' + (ext ? '' : ' mews-open') + '" href="' + esc(boek) + '"' + boekAttr + (ext ? ' target="_blank" rel="noopener"' : '') + ' data-pop-boek>' + esc(boeklabel) + '</a></div>';
      }
      return '<div class="al-pop__slider"><div class="al-pop__spoor">' + dia + '</div>' + nav + '</div>' +
        '<div class="al-pop__body"><button type="button" class="al-pop__sluit" data-pop-sluit aria-label="' + esc(L.lSluit) + '">' + KRUIS + '</button>' +
        (badge ? '<span class="al-pop__badge">' + badge + '</span>' : '') +
        '<h3 class="al-pop__naam" id="al-pop-naam">' + naam + '</h3>' +
        (sub ? '<p class="al-pop__sub">' + esc(sub) + '</p>' : '') + prijs +
        '<p class="al-pop__desc">' + esc(kortDesc(r.desc)) + '</p>' + extra + '</div>' + voet;
    };
    var laadFoto = function (i) {
      var img = kaartEl.querySelector('.al-pop__spoor').children[i];
      if (img && img.tagName === 'IMG' && img.getAttribute('data-src')) { img.src = img.getAttribute('data-src'); img.removeAttribute('data-src'); }
    };
    var VIDAUTO = zacht && !(navigator.connection && navigator.connection.saveData);
    var popVid = function () { return kaartEl.querySelector('.al-pop__video'); };
    var vidBron = function (v) { if (v.getAttribute('data-src')) { v.src = v.getAttribute('data-src'); v.removeAttribute('data-src'); } };
    var vidSpeel = function (v, vanafBegin) { vidBron(v); if (vanafBegin && v.currentTime) v.currentTime = 0; var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); };
    var vidStand = function (vorige) {
      var v = popVid(); if (!v) return;
      if (popIdx !== 0) { v.pause(); return; }
      if (VIDAUTO && !v.__handPauze) vidSpeel(v, vorige !== undefined && vorige !== 0);
    };
    var gaFoto = function (i) {
      if (!popN) return;
      var vorige = popOpenIdx ? popIdx : undefined; popOpenIdx = true;
      popIdx = (i + popN) % popN;
      var sp = kaartEl.querySelector('.al-pop__spoor'); if (sp) sp.style.transform = 'translateX(-' + (popIdx * 100) + '%)';
      Array.prototype.forEach.call(kaartEl.querySelectorAll('.al-pop__dot'), function (x, j) { x.classList.toggle('is-aan', j === popIdx); });
      laadFoto(popIdx); laadFoto((popIdx + 1) % popN);
      vidStand(vorige);
    };
    var popOpen = function (soort, sleutel, knop) {
      var h = bouw(soort, sleutel, knop); if (!h) return false;
      kaartEl.innerHTML = h; kaartEl.classList.toggle('al-pop__kaart--arr', soort === 'arr'); popSoort = soort; popSleutel = sleutel; popTerug = knop; popOpenIdx = false;
      var v = kaartEl.querySelector('.al-pop__video');
      if (v) {
        var vd = v.parentNode, sk = vd.querySelector('[data-pop-speel]');
        var knopStand = function () { var aan = !v.paused; vd.classList.toggle('is-speelt', aan); sk.setAttribute('aria-label', aan ? L.lPauze : L.lSpeel); };
        v.addEventListener('play', knopStand); v.addEventListener('pause', knopStand);
      }
      gaFoto(0);
      popEl.hidden = false; root.classList.add('al-pop-open');
      if (zacht) { popEl.classList.remove('is-open'); void popEl.offsetWidth; }
      popEl.classList.add('is-open');
      kaartEl.querySelector('[data-pop-sluit]').focus({ preventScroll: true });
      meet('adslander_popup_open', { popup_soort: soort, popup_sleutel: sleutel });
      return true;
    };
    var popDicht = function (stil) {
      if (popEl.hidden) return;
      var v = popVid(); if (v) { v.pause(); v.removeAttribute('src'); v.load(); }
      popEl.classList.remove('is-open'); popEl.hidden = true; kaartEl.innerHTML = '';
      root.classList.remove('al-pop-open');
      if (popTerug && !stil) popTerug.focus({ preventScroll: true });
    };
    /* een boekknop in de pop-up die Mews opent (geen kalender): pop-up eerst dicht. De kalender ligt erboven, daar blijft hij open. */
    window.alPopDicht = function (stil) { popDicht(stil); };
    /* kamer-pop-up op de telefoon (< 768 px): de al-pop-sheet; vanaf 768 px de lander-w1-dialoog (5b) */
    window.alPopKamer = function (sleutel, knop) { if (POP) popOpen('kamer', sleutel, knop); else haalPop().then(function () { popOpen('kamer', sleutel, knop); }); };
    window.alPopKamerDicht = function () { if (popSoort === 'kamer') popDicht(true); };
    document.addEventListener('click', function (e) {
      if (!e.target.closest || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      var a = e.target.closest(POPKNOP);
      if (!a) return;
      var p = a.getAttribute('data-pop').split(':');
      e.preventDefault();
      if (POP) { popOpen(p[0], p[1], a); return; }
      haalPop().then(function () { popOpen(p[0], p[1], a); });
    });
    popEl.addEventListener('click', function (e) {
      if (e.target === popEl || e.target.closest('[data-pop-sluit]')) { popDicht(); return; }
      var dt = e.target.closest('[data-pop-dot]'); if (dt) { gaFoto(Number(dt.getAttribute('data-pop-dot'))); return; }
      var sp = e.target.closest('[data-pop-speel], .al-pop__video');
      if (sp) { var v = popVid(); if (v.paused) { v.__handPauze = false; if (popIdx !== 0) gaFoto(0); vidSpeel(v); } else { v.__handPauze = true; v.pause(); } return; }
      var st = e.target.closest('[data-pop-stap]'); if (st) { gaFoto(popIdx + Number(st.getAttribute('data-pop-stap'))); return; }
      if (e.target.closest('[data-pop-boek]')) meet('adslander_popup_boek', { popup_soort: popSoort, popup_sleutel: popSleutel });
    });
    document.addEventListener('keydown', function (e) {
      if (popEl.hidden || root.classList.contains('ark-open')) return;
      if (e.key === 'Escape') { popDicht(); return; }
      if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && popN > 1 && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); gaFoto(popIdx + (e.key === 'ArrowRight' ? 1 : -1)); return; }
      if (e.key === 'Tab') {
        var f = Array.prototype.slice.call(kaartEl.querySelectorAll('a[href], button'));
        if (!f.length) return;
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && (i === f.length - 1 || i < 0)) { e.preventDefault(); f[0].focus(); }
      }
    });
    var spoorVan = function () { return kaartEl.querySelector('.al-pop__spoor'); };
    veegbaar(kaartEl, {
      niet: 'button:not(.al-pop__speel), a, .al-pop__body, .al-pop__voet',
      start: function () { var sp = spoorVan(); if (!sp || popN < 2) return; sp.style.transition = 'none'; laadFoto((popIdx + 1) % popN); laadFoto((popIdx - 1 + popN) % popN); },
      beweeg: function (dx) {
        var sp = spoorVan(); if (!sp || popN < 2) return;
        if ((popIdx === 0 && dx > 0) || (popIdx === popN - 1 && dx < 0)) dx *= 0.4;
        sp.style.transform = 'translateX(calc(' + (-popIdx * 100) + '% + ' + dx + 'px))';
      },
      einde: function (dx, snel) {
        var sp = spoorVan(); if (!sp) return; sp.style.transition = '';
        if (popN < 2) return;
        var b = sp.parentNode.clientWidth || 1;
        gaFoto(popIdx + ((Math.abs(dx) > b * 0.2 || snel) ? (dx < 0 ? 1 : -1) : 0));
      },
      wiel: function (r) { if (popN > 1) gaFoto(popIdx + r); }
    });
  }

  /* ---- 5b kamer-pop-up vanaf 768 px = de lander-w1-dialoog #lp-pop-kamer (telefoon: al-pop-sheet, zie 5) (opmaak lander-w1.css), gedrag 1-op-1 uit lander-w1.js
          (toonPop/sluitPop/opruimen/vulKamer + focusrand-logica), data uit #al-kamerdata, Duitse labels uit de dialoog.
          Native showModal (Escape, top layer, ::backdrop); zonder showModal hidden + overlay. Video pas bij openen,
          leeg bij sluiten; focus terug naar de knop die opende. Boekknop = Mews met de kamer via de poort hierboven. ---- */
  (function () {
    var popKamer = document.getElementById('lp-pop-kamer');
    var dataEl = document.getElementById('al-kamerdata');
    var telefoon = window.matchMedia('(max-width:767.98px)');
    if (!popKamer || !dataEl) return;
    var kamerData = {};
    try { kamerData = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var popOverlay = document.querySelector('.lp-pop-overlay');
    var vinkSjabloon = document.getElementById('lp-pop-vink');
    var kanModal = typeof popKamer.showModal === 'function';
    var rustig = !zacht;
    var LF = popKamer.getAttribute('data-l-foto') || 'Foto', LB = popKamer.getAttribute('data-l-boek') || '';
    var openPop = null, opener = null, laatsteToets = false;
    if (!kanModal) popKamer.hidden = true;
    document.addEventListener('keydown', function (e) { if (e.key === 'Tab' || e.key === 'Enter' || e.key === ' ') laatsteToets = true; }, true);
    document.addEventListener('pointerdown', function () { laatsteToets = false; popKamer.classList.remove('lp-pop--muis'); }, true);
    document.addEventListener('keydown', function (e) { if (e.key === 'Tab') popKamer.classList.remove('lp-pop--muis'); }, true);
    function maak(tag, cls, tekst) { var el = document.createElement(tag); if (cls) el.className = cls; if (tekst != null) el.textContent = tekst; return el; }
    function toonPop(d, knop) {
      if (openPop) sluitPop(openPop, true);
      opener = knop || null; openPop = d;
      root.classList.add('lp-pop-vast');
      var binnen = d.querySelector('.lp-pop__binnen'); if (binnen) binnen.scrollTop = 0;
      if (kanModal) d.showModal();
      else { d.hidden = false; d.classList.add('is-open'); d.setAttribute('role', 'dialog'); if (popOverlay) popOverlay.hidden = false; }
      var sluit = d.querySelector('.lp-pop__sluit');
      d.classList.toggle('lp-pop--muis', !laatsteToets);
      if (sluit) sluit.focus();
      meet('adslander_popup_open', { popup_soort: 'kamer', popup_sleutel: knop ? knop.getAttribute('data-kamer') : '' });
    }
    function opruimen(d, stil) {
      var v = d.querySelector('video');
      if (v) { try { v.pause(); } catch (e) {} v.removeAttribute('src'); v.load(); }
      root.classList.remove('lp-pop-vast');
      if (openPop === d) openPop = null;
      var terug = opener; opener = null;
      if (!stil && terug && document.contains(terug)) terug.focus();
    }
    function sluitPop(d, stil) {
      if (kanModal) { if (!d.open) return; d._stil = !!stil; d.close(); }
      else { if (d.hidden) return; d.hidden = true; d.classList.remove('is-open'); if (popOverlay) popOverlay.hidden = true; opruimen(d, stil); }
    }
    if (kanModal) popKamer.addEventListener('close', function () { var stil = popKamer._stil; popKamer._stil = false; opruimen(popKamer, stil); });
    popKamer.addEventListener('click', function (e) {
      if (e.target === popKamer || (e.target.closest && e.target.closest('.lp-pop__sluit'))) { sluitPop(popKamer); return; }
      if (e.target.closest && e.target.closest('.mews-open')) sluitPop(popKamer, true);
    });
    if (popOverlay) popOverlay.addEventListener('click', function () { if (openPop) sluitPop(openPop); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openPop && !kanModal) sluitPop(openPop); });
    function vulKamer(key) {
      var k = kamerData[key];
      if (!k) return false;
      var fotos = k.fotos || [];
      var video = popKamer.querySelector('.lp-pop__video'), hero = popKamer.querySelector('.lp-pop__hero'), rij = popKamer.querySelector('.lp-pop__fotos');
      rij.textContent = '';
      var rijFotos;
      if (k.video) {
        hero.hidden = true; hero.removeAttribute('src');
        video.hidden = false; video.poster = fotos[0] || ''; video.autoplay = !rustig; video.controls = rustig; video.src = k.video;
        if (!rustig) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
        rijFotos = fotos.slice(0, 3);
      } else {
        video.hidden = true; video.removeAttribute('src'); video.removeAttribute('poster');
        hero.hidden = false; hero.src = fotos[0] || ''; hero.alt = k.naam;
        rijFotos = fotos.slice(1, 4);
      }
      rij.setAttribute('data-n', rijFotos.length);
      rijFotos.forEach(function (src, i) {
        var img = maak('img'); img.src = src; img.alt = k.naam + ', ' + LF + ' ' + (i + 1); img.loading = 'lazy'; img.decoding = 'async';
        rij.appendChild(img);
      });
      popKamer.querySelector('.lp-pop__titel').textContent = k.naam;
      var tekst = popKamer.querySelector('.lp-pop__tekst'); tekst.textContent = '';
      (k.tekst || []).forEach(function (t) { tekst.appendChild(maak('p', null, t)); });
      var lijst = popKamer.querySelector('.lp-pop__kenmerken'); lijst.textContent = '';
      (k.kenmerken || []).forEach(function (t) {
        var li = maak('li');
        if (vinkSjabloon && vinkSjabloon.content) li.appendChild(vinkSjabloon.content.cloneNode(true));
        li.appendChild(maak('span', null, t));
        lijst.appendChild(li);
      });
      var boek = popKamer.querySelector('.lp-pop__boek');
      boek.setAttribute('data-room', k.kamer);
      boek.setAttribute('href', boek.getAttribute('data-basis') + '&mewsRoom=' + k.kamer + '&mewsRoute=rooms');
      boek.setAttribute('aria-label', k.naam + ': ' + LB);
      return true;
    }
    document.addEventListener('click', function (e) {
      if (!e.target.closest || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      var kk = e.target.closest('[data-kamer]');
      if (!kk) return;
      e.preventDefault();
      if (telefoon.matches && window.alPopKamer) { window.alPopKamer(kk.getAttribute('data-kamer'), kk); return; }
      if (vulKamer(kk.getAttribute('data-kamer'))) toonPop(popKamer, kk);
    });
    /* draaien/venster over 768 px: geen kamer-pop-up van de andere vorm laten openstaan */
    var wissel = function () { sluitPop(popKamer, true); if (window.alPopKamerDicht) window.alPopKamerDicht(); };
    if (telefoon.addEventListener) telefoon.addEventListener('change', wissel); else if (telefoon.addListener) telefoon.addListener(wissel);
  })();

  /* ---- 6 vragen: tabs ---- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-faq]'), function (faq) {
    var lijst = faq.querySelector('[role="tablist"]'); if (!lijst) return;
    var tabs = Array.prototype.slice.call(lijst.querySelectorAll('[role="tab"]'));
    function kies(tab, focus) {
      tabs.forEach(function (t) {
        var aan = t === tab, paneel = document.getElementById(t.getAttribute('aria-controls'));
        t.setAttribute('aria-selected', aan ? 'true' : 'false'); t.tabIndex = aan ? 0 : -1;
        t.classList.toggle('al-chip--aan', aan);
        if (paneel) paneel.hidden = !aan;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { kies(t, false); });
      t.addEventListener('keydown', function (e) {
        var j = -1;
        if (e.key === 'ArrowRight') j = (i + 1) % tabs.length; else if (e.key === 'ArrowLeft') j = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') j = 0; else if (e.key === 'End') j = tabs.length - 1;
        if (j > -1) { e.preventDefault(); kies(tabs[j], true); }
      });
    });
    lijst.hidden = false; faq.classList.add('al-faq--tabs'); kies(tabs[0], false);
  });

  /* ---- 7a live kamerprijzen (zelfde code als spiegel.js): verborgen tot gevuld ---- */
  var prijsEls = document.querySelectorAll('[data-kamer-vanaf]');
  if (prijsEls.length && window.fetch) {
    fetch('/api/kamer-vanaf', { headers: { Accept: 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        var prijzen = (data && data.ok && data.prijzen) || {};
        window.alKamerVanaf = prijzen;
        Array.prototype.forEach.call(document.querySelectorAll('[data-kamer-vanaf]'), function (el) {
          var p = prijzen[el.getAttribute('data-kamer-vanaf')], b = el.querySelector('[data-kamer-vanaf-bedrag]');
          if (!p || typeof p.euro !== 'number' || !b) return;
          b.textContent = '€ ' + p.euro; el.classList.add('is-gevuld');
        });
      })
      .catch(function () { window.alKamerVanaf = null; });
  }

  /* ---- 7b nieuwsbrief inline (Klaviyo via /api/nieuwsbrief, lijst DE) ---- */
  var nb = document.getElementById('al-nb');
  if (nb) {
    var nbOpen = Date.now(), nbBezig = false;
    nb.addEventListener('submit', function (e) {
      e.preventDefault();
      if (nbBezig) return;
      var veld = nb.querySelector('input[type=email]'), melding = nb.querySelector('.al-nb__melding'), pot = nb.querySelector('.al-nb__pot');
      var mail = (veld.value || '').trim();
      melding.classList.remove('is-fout');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail)) { melding.textContent = nb.getAttribute('data-fout'); melding.classList.add('is-fout'); veld.focus(); return; }
      nbBezig = true;
      if (window.track) { try { window.track('email_submit'); } catch (x) {} }
      fetch('/api/nieuwsbrief', { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: mail, taal: 'de', bron: 'pagina', website: pot ? pot.value : '', ts: nbOpen }) })
        .then(function (r) { return r.json().then(function (d) { return !!(r.ok && d && d.ok); }, function () { return false; }); }, function () { return false; })
        .then(function (ok) {
          nbBezig = false;
          if (ok) { melding.textContent = nb.getAttribute('data-ok'); veld.value = ''; meet('adslander_nieuwsbrief', {}); if (window.track) { try { window.track('email_success'); } catch (x) {} } }
          else { melding.textContent = nb.getAttribute('data-fout'); melding.classList.add('is-fout'); }
        });
    });
  }

  /* ---- 7c onderbalk telefoon: pas zichtbaar als de hero uit beeld is ---- */
  var balk = document.querySelector('.mob-cta');
  if (balk && heroEl && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (items) {
      var it = items[0], weg = !it.isIntersecting && it.boundingClientRect.top < 0;
      balk.classList.toggle('is-zichtbaar', weg);
      root.classList.toggle('mob-cta-aan', weg);
      root.style.setProperty('--mob-cta-h', balk.offsetHeight + 'px');
      balk.setAttribute('aria-hidden', weg ? 'false' : 'true');
      balk.querySelectorAll('a').forEach(function (a) { a.setAttribute('tabindex', weg ? '0' : '-1'); });
    }, { threshold: 0 }).observe(heroEl);
  }

  /* ---- 7d cookiemelding (zoals lander-w1.js) ---- */
  var banner = document.getElementById('cookieBanner'), akkoord = document.getElementById('cookieAccept');
  if (banner && akkoord) {
    try { if (!localStorage.getItem('cookie-consent')) banner.classList.add('show'); } catch (e) { banner.classList.add('show'); }
    akkoord.addEventListener('click', function () { try { localStorage.setItem('cookie-consent', '1'); } catch (e) {} banner.classList.remove('show'); });
  }

  /* ---- 7e scratchcard-pop-up niet over een eigen pop-up, de lightbox of de prijskalender: even weg en daarna terug ---- */
  (function wachter() {
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', wachter); return; }
    if (!window.MutationObserver) return;
    var bezet = function () { return root.classList.contains('al-pop-open') || root.classList.contains('al-lb-open') || root.classList.contains('ark-open') || root.classList.contains('lp-pop-vast'); };
    var k = document.getElementById('scClose'), sc = k ? k.closest('[data-stijl]') : null, wacht = false;
    if (!sc) return;
    var kijk = function () {
      if (sc.classList.contains('is-open') && bezet()) { wacht = true; sc.classList.remove('is-open'); }
      else if (wacht && !bezet()) { wacht = false; setTimeout(function () { if (!bezet()) sc.classList.add('is-open'); else wacht = true; }, 400); }
    };
    var mo = new MutationObserver(kijk);
    mo.observe(sc, { attributes: true, attributeFilter: ['class'] });
    mo.observe(root, { attributes: true, attributeFilter: ['class'] });
  })();
})();
