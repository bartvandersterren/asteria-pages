/* GEDRAG bij omgeving.template.html en omgeving-categorie.template.html (Hotel Asteria, /omgeving-v2 en /omgeving-<cat>-v2).
   Port van parkhotel-site src/gedrag/pagina-gebied-overzicht-v2.js en pagina-categorie-v2.js. Het filteren zelf doet de
   CSS (radio's + broertjes-combinator). Dagblok: uitje.js. Mews, kamerslider, pop-ups, reviews, onderbalk: adslander.js.

   1  DEEPLINK: #golf, #natuur, #cultuur, #dagje-uit, #shoppen, #te-voet, #op-de-fiets (+ DE/EN) zet de juiste radio,
      ook bij hashchange, en scrolt naar het raster.
   2  TOON ALLE N UITJES: .is-kort op het raster (CSS verbergt kaart 13+ zolang beide filters op Alle staan; telefoon 9+),
      knop alleen als er meer kaarten zijn dan de grens. Zonder script alles zichtbaar.
   3  GOLF-VEEGRIJ: teller 01 / 02, pijlen, pijltjestoetsen; geen lus; bij 1 kaart geen teller en pijlen.
   4  FOTOSLIDER (uitgelicht arrangement): pijlen en bolletjes.
   Elk stuk stopt stil als zijn blok er niet is. */
(function () {
  'use strict';
  var HASH = {
    '#golf': 'om-f-golf', '#natuur': 'om-f-natuur', '#nature': 'om-f-natuur', '#cultuur': 'om-f-cultuur', '#kultur': 'om-f-cultuur',
    '#culture': 'om-f-cultuur', '#dagje-uit': 'om-f-dagje-uit', '#ausfluege': 'om-f-dagje-uit', '#day-out': 'om-f-dagje-uit',
    '#days-out': 'om-f-dagje-uit', '#shoppen': 'om-f-shoppen-steden', '#shoppen-steden': 'om-f-shoppen-steden',
    '#shoppen-en-steden': 'om-f-shoppen-steden', '#einkaufen': 'om-f-shoppen-steden', '#shopping': 'om-f-shoppen-steden',
    '#te-voet': 'om-t-lopen', '#op-de-fiets': 'om-t-fiets', '#met-de-auto': 'om-t-auto', '#on-foot': 'om-t-lopen',
    '#by-bike': 'om-t-fiets', '#by-car': 'om-t-auto', '#zu-fuss': 'om-t-lopen', '#mit-dem-rad': 'om-t-fiets', '#mit-dem-auto': 'om-t-auto'
  };
  function deeplink() {
    var id = HASH[(location.hash || '').toLowerCase()];
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    el.checked = true;
    var doel = el.closest('section');
    if (doel) doel.scrollIntoView({ block: 'start' });
  }
  deeplink();
  window.addEventListener('hashchange', deeplink);
})();

(function () {
  'use strict';
  var raster = document.querySelector('[data-om-raster]'), meer = document.querySelector('[data-om-meer]');
  if (!raster || !meer || !window.matchMedia) return;
  var telefoon = matchMedia('(max-width:767.98px)'), knop = meer.querySelector('button'), open = false;
  var n = raster.querySelectorAll('.om-kaart').length;
  function grens() { return Number(raster.getAttribute(telefoon.matches ? 'data-grens-telefoon' : 'data-grens')) || 12; }
  function zet() {
    var kort = !open && n > grens();
    raster.classList.toggle('is-kort', kort);
    raster.classList.toggle('is-kort-telefoon', kort && telefoon.matches);
    meer.classList.toggle('is-aan', kort);
  }
  zet();
  if (telefoon.addEventListener) telefoon.addEventListener('change', zet);
  if (knop) knop.addEventListener('click', function () { open = true; zet(); });
})();

(function () {
  'use strict';
  var blok = document.querySelector('[data-om-slider]');
  if (!blok) return;
  var spoor = blok.querySelector('[data-om-spoor]'), nav = blok.querySelector('[data-om-nav]');
  var dias = spoor ? spoor.querySelectorAll('[data-om-dia]') : [];
  if (!spoor || !nav || dias.length < 2) return;
  var teller = nav.querySelector('[data-om-teller]'), pijlen = nav.querySelectorAll('[data-om-stap]');
  var twee = function (i) { return (i < 10 ? '0' : '') + i; };
  function stap() { var s = getComputedStyle(spoor); return dias[0].getBoundingClientRect().width + (parseFloat(s.columnGap || s.gap) || 0); }
  function ververs() {
    var max = spoor.scrollWidth - spoor.clientWidth, i = Math.round(spoor.scrollLeft / stap());
    if (spoor.scrollLeft >= max - 2) i = dias.length - 1;
    i = Math.max(0, Math.min(dias.length - 1, i));
    if (teller) teller.textContent = twee(i + 1) + ' / ' + twee(dias.length);
    pijlen[0].disabled = spoor.scrollLeft <= 2;
    pijlen[1].disabled = spoor.scrollLeft >= max - 2;
  }
  function ga(r) { spoor.scrollBy({ left: stap() * r }); }
  Array.prototype.forEach.call(pijlen, function (p) { p.addEventListener('click', function () { ga(Number(p.getAttribute('data-om-stap'))); }); });
  spoor.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); ga(1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); ga(-1); }
  });
  var w = null;
  spoor.addEventListener('scroll', function () { clearTimeout(w); w = setTimeout(ververs, 80); }, { passive: true });
  window.addEventListener('resize', function () { clearTimeout(w); w = setTimeout(ververs, 150); });
  nav.hidden = false;
  ververs();
})();

(function () {
  'use strict';
  Array.prototype.forEach.call(document.querySelectorAll('[data-om-fs]'), function (fs) {
    var spoor = fs.querySelector('[data-fs-spoor]'), bollen = fs.querySelectorAll('[data-fs-naar]');
    if (!spoor) return;
    var n = spoor.children.length;
    function huidig() { return Math.round(spoor.scrollLeft / (spoor.clientWidth || 1)); }
    function naar(i) { i = (i + n) % n; spoor.scrollTo({ left: i * spoor.clientWidth }); }
    function ververs() {
      var i = huidig();
      Array.prototype.forEach.call(bollen, function (b, j) { b.classList.toggle('is-aan', j === i); if (j === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    }
    Array.prototype.forEach.call(bollen, function (b) { b.addEventListener('click', function () { naar(Number(b.getAttribute('data-fs-naar'))); }); });
    Array.prototype.forEach.call(fs.querySelectorAll('[data-fs-stap]'), function (p) { p.addEventListener('click', function () { naar(huidig() + Number(p.getAttribute('data-fs-stap'))); }); });
    var w = null;
    spoor.addEventListener('scroll', function () { clearTimeout(w); w = setTimeout(ververs, 80); }, { passive: true });
  });
})();
