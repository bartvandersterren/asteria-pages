/* Arrangementsjabloon op lander-w1: aanvulling op lander-w1.js, alleen geladen via build-blok 'arrangement'.
   1. Kamerraster (.ar-kamers, 1 of 2 kamers): de meelopende zijkaart stopt gelijk met de onderkant van de kamerkaarten
      (--kant-onder op .lp-zone, zoals lander-w1.js dat voor de slider doet). Vanaf 3 kamers doet lander-w1.js alles.
   2. Fotoslider in 'Dit is inbegrepen' (Parkhotel .wv-fs): vegen = scroll-snap, pijlen rondlopend, bolletjes; geen autoplay.
   3. Waarom Asteria: draaiend wiel zoals de staging-homepage (4 klonen voor en na, autoplay 2400 ms alleen in beeld,
      pijlen pauzeren 6 s, foto wisselt mee met crossfade). Bij prefers-reduced-motion geen autoplay.
   4. Actiecodeveld in de boekbalk zo breed als de code (lander-w1.css zet 9,5ch; WELLNESS2026 viel daarbuiten).
   5. Vast aantal nachten (ARR_NACHTEN > 1 in de JSON -> data-nachten op form[data-boekbalk]): vertrek = aankomst + N
      bij elke aankomstkeuze, en vlak voor verzenden (capture op document, dus vóór de submit van lander-w1.js), zodat
      widget (setStartDate/setEndDate) en URL-fallback (mewsStart/mewsEnd) N nachten krijgen. lander-w1.js blijft ongewijzigd. */
(function () {
  'use strict';
  var rustig = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. kamerraster */
  (function () {
    var zone = document.querySelector('.lp-zone');
    var raster = zone && zone.querySelector('.ar-kamers');
    if (!raster) return;
    function zet() {
      var kaart = raster.querySelector('.b4b-kaart');
      var blok = raster.closest('.b4b');
      if (!kaart || !blok) return;
      var onder = blok.getBoundingClientRect().bottom - kaart.getBoundingClientRect().bottom;
      zone.style.setProperty('--kant-onder', Math.max(0, Math.round(onder)) + 'px');
    }
    zet();
    window.addEventListener('load', zet);
    window.addEventListener('resize', zet);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(zet);
  })();

  /* 2. fotoslider */
  Array.prototype.forEach.call(document.querySelectorAll('[data-ar-fs]'), function (fs) {
    var spoor = fs.querySelector('[data-fs-spoor]');
    if (!spoor) return;
    var n = spoor.children.length;
    var bollen = fs.querySelectorAll('[data-fs-naar]');
    function nu() { var b = spoor.clientWidth || 1; return Math.max(0, Math.min(n - 1, Math.round(spoor.scrollLeft / b))); }
    function naar(i) {
      i = (i + n) % n;
      spoor.scrollTo({ left: i * spoor.clientWidth, behavior: rustig ? 'auto' : 'smooth' });
    }
    function bij() {
      var i = nu();
      Array.prototype.forEach.call(bollen, function (b, j) {
        b.classList.toggle('is-aan', j === i);
        if (j === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
      });
    }
    var wacht = false;
    spoor.addEventListener('scroll', function () {
      if (wacht) return; wacht = true;
      window.requestAnimationFrame(function () { wacht = false; bij(); });
    }, { passive: true });
    Array.prototype.forEach.call(fs.querySelectorAll('[data-fs-stap]'), function (b) {
      b.addEventListener('click', function () { naar(nu() + Number(b.getAttribute('data-fs-stap'))); });
    });
    Array.prototype.forEach.call(bollen, function (b) {
      b.addEventListener('click', function () { naar(Number(b.getAttribute('data-fs-naar'))); });
    });
    spoor.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); naar(nu() + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); naar(nu() - 1); }
    });
    bij();
  });

  /* 3. waarom Asteria: draaiend wiel */
  Array.prototype.forEach.call(document.querySelectorAll('.ar-waarom'), function (sec) {
    var wrap = sec.querySelector('.ar-wiel-wrap');
    var spoor = sec.querySelector('.ar-wiel-spoor');
    var lagen = sec.querySelectorAll('.ar-wiel-laag');
    if (!wrap || !spoor) return;
    var echt = Array.prototype.slice.call(spoor.querySelectorAll('.ar-wiel-item'));
    var N = echt.length, VOOR = 4, NA = 4;
    if (N < 2) return;
    function kloon(it) {
      var c = it.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      c.setAttribute('data-kloon', '');
      c.classList.add('is-kloon');
      return c;
    }
    for (var i = VOOR; i > 0; i--) spoor.insertBefore(kloon(echt[N - i]), echt[0]);
    for (var j = 0; j < NA; j++) spoor.appendChild(kloon(echt[j]));
    var alle = Array.prototype.slice.call(spoor.querySelectorAll('.ar-wiel-item'));
    wrap.classList.add('is-wiel');

    echt.forEach(function (it) { var f = it.getAttribute('data-foto'); if (f) { var im = new Image(); im.src = f; } });

    var laag = 0;
    function zetFoto(it) {
      var src = it.getAttribute('data-foto');
      if (!lagen.length || !src) return;
      var volgende = 1 - laag, el = lagen[volgende];
      var toon = function () {
        lagen[laag].classList.remove('is-actief');
        lagen[laag].setAttribute('aria-hidden', 'true'); lagen[laag].alt = '';
        el.classList.add('is-actief');
        el.removeAttribute('aria-hidden'); el.alt = it.getAttribute('data-alt') || '';
        laag = volgende;
      };
      if (lagen[laag].getAttribute('src') === src) return;
      el.style.objectPosition = it.getAttribute('data-pos') || '50% 50%';
      if (el.getAttribute('src') === src && el.complete) { toon(); return; }
      el.onload = function () { el.onload = null; toon(); };
      el.setAttribute('src', src);
      if (el.complete && el.naturalWidth) { el.onload = null; toon(); }
    }

    var actief = VOOR;
    function zet(idx) {
      actief = idx;
      spoor.style.setProperty('--active', idx);
      alle.forEach(function (it, k) {
        var d = Math.abs(k - idx);
        it.style.opacity = Math.max(0.12, 1 - d * 0.28).toFixed(3);
        it.classList.toggle('is-active', k === idx);
        if (k === idx && !it.hasAttribute('data-kloon')) it.setAttribute('aria-current', 'true'); else it.removeAttribute('aria-current');
      });
      zetFoto(echt[((idx - VOOR) % N + N) % N]);
    }
    function snap(idx) {
      spoor.classList.add('no-transition');
      zet(idx);
      void spoor.offsetHeight;
      window.requestAnimationFrame(function () { spoor.classList.remove('no-transition'); });
    }
    zet(actief);

    var OVERGANG = rustig ? 0 : 1000, STAP = 2400;
    var klok = null, snapKlok = null, pauze = false, hervat = null;
    function naGrens() {
      if (snapKlok) clearTimeout(snapKlok);
      snapKlok = setTimeout(function () {
        snapKlok = null;
        if (actief >= VOOR + N) snap(actief - N);
        else if (actief < VOOR) snap(actief + N);
      }, OVERGANG + 60);
    }
    function stap(r) { zet(actief + r); if (actief >= VOOR + N || actief < VOOR) naGrens(); }
    function start() { if (!klok && !rustig) klok = setInterval(function () { if (!pauze) stap(1); }, STAP); }
    function stop() { if (klok) { clearInterval(klok); klok = null; } }
    Array.prototype.forEach.call(sec.querySelectorAll('[data-wiel-stap]'), function (b) {
      b.addEventListener('click', function () {
        pauze = true;
        if (hervat) clearTimeout(hervat);
        hervat = setTimeout(function () { pauze = false; }, 6000);
        stap(Number(b.getAttribute('data-wiel-stap')));
      });
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (items) {
        items.forEach(function (e) { if (e.isIntersecting) start(); else stop(); });
      }).observe(sec);
    }
  });

  /* 4. actiecodeveld zo breed als de code */
  Array.prototype.forEach.call(document.querySelectorAll('.b1a-balk .b1a-codeveld'), function (veld) {
    function maat() {
      if (!veld.offsetParent) return;
      veld.style.width = '0px';
      veld.style.width = (veld.scrollWidth + 2) + 'px';
    }
    maat();
    window.addEventListener('load', maat);
    window.addEventListener('resize', maat);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(maat);
  });

  /* 5. vast aantal nachten */
  function twee(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(d) { return d.getFullYear() + '-' + twee(d.getMonth() + 1) + '-' + twee(d.getDate()); }
  function leesDatum(v) {
    var p = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || '');
    return p ? new Date(+p[1], +p[2] - 1, +p[3]) : null;
  }
  function plusDagen(d, n) { return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n); }
  var vandaag = new Date(); vandaag = new Date(vandaag.getFullYear(), vandaag.getMonth(), vandaag.getDate());
  function nachtenVan(form) { return parseInt(form.getAttribute('data-nachten'), 10) || 1; }
  /* waarde zetten en 'change' sturen: lander-w1.js werkt dan de zichtbare datum bij */
  function zetDatum(invoer, d) {
    invoer.value = ymd(d);
    invoer.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function vastVertrek(form, altijd) {
    var n = nachtenVan(form);
    var aankomst = form.querySelector('[data-rol="aankomst"]'), vertrek = form.querySelector('[data-rol="vertrek"]');
    if (n < 2 || !aankomst || !vertrek) return;
    var a = leesDatum(aankomst.value), v = leesDatum(vertrek.value);
    if (!a && v) {
      a = plusDagen(v, -n);
      if (a < vandaag) return;
      zetDatum(aankomst, a);
    }
    if (!a) return;
    var doel = plusDagen(a, n);
    vertrek.min = ymd(doel);
    if (altijd || !v || v < doel) zetDatum(vertrek, doel);
  }
  Array.prototype.forEach.call(document.querySelectorAll('form[data-boekbalk][data-nachten]'), function (form) {
    var aankomst = form.querySelector('[data-rol="aankomst"]'), vertrek = form.querySelector('[data-rol="vertrek"]');
    if (!aankomst || !vertrek || nachtenVan(form) < 2) return;
    vertrek.min = ymd(plusDagen(vandaag, nachtenVan(form)));
    aankomst.addEventListener('change', function () { vastVertrek(form, true); });
    /* te kort vertrek direct terugzetten (anders blokkeert min= het verzenden) */
    vertrek.addEventListener('change', function () { vastVertrek(form, false); });
  });
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (form && form.matches && form.matches('form[data-boekbalk][data-nachten]')) vastVertrek(form, false);
  }, true);
})();
