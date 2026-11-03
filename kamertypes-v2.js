/* Hotel Asteria, kamertypes-v2 (build-blok 'kamertypes'): filterchips, fotogalerij per kamerkaart en de
   breedte van de contactkaart. Laadt na lander-w1.js (die opent Mews via .mews-open met data-room). */
(function () {
  'use strict';

  /* ── fotogalerij: crossfade tussen de foto's, pijlen (lus), bolletjes, vegen op touch ── */
  document.querySelectorAll('[data-kt-galerij]').forEach(function (g) {
    var dias = g.querySelectorAll('.kt-dia'), dots = g.querySelectorAll('.kt-dot'), n = dias.length, nu = 0;
    if (n < 2) {
      g.querySelectorAll('.kt-pijl, .kt-dots').forEach(function (x) { x.hidden = true; });
      return;
    }
    function toon(i) {
      nu = (i + n) % n;
      Array.prototype.forEach.call(dias, function (d, j) {
        d.classList.toggle('is-actief', j === nu);
        if (j === nu) { d.removeAttribute('aria-hidden'); d.loading = 'eager'; } else d.setAttribute('aria-hidden', 'true');
      });
      Array.prototype.forEach.call(dots, function (d, j) {
        d.classList.toggle('is-actief', j === nu);
        if (j === nu) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current');
      });
    }
    g.querySelectorAll('[data-kt-stap]').forEach(function (b) {
      b.addEventListener('click', function () { toon(nu + parseInt(b.getAttribute('data-kt-stap'), 10)); });
    });
    Array.prototype.forEach.call(dots, function (d) {
      d.addEventListener('click', function () { toon(parseInt(d.getAttribute('data-kt-naar'), 10)); });
    });
    /* volgende foto alvast laden zodra de kaart in beeld is */
    g.addEventListener('pointerenter', function () { if (dias[1]) dias[1].loading = 'eager'; }, { once: true });
    var x0 = null;
    g.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    g.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) toon(nu + (dx < 0 ? 1 : -1));
    }, { passive: true });
  });

  /* ── contactkaart vult de rest van de laatste rij (staging: twee kolommen naast de Mindervalide kamer) ── */
  var grid = document.querySelector('.kt-grid');
  var contact = grid && grid.querySelector('.kt-contact');
  function zetContact() {
    if (!contact) return;
    var kolommen = getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length || 1;
    if (kolommen < 2) { contact.style.gridColumn = ''; contact.classList.remove('kt-contact--smal', 'kt-contact--breed'); return; }
    var zichtbaar = grid.querySelectorAll('.kt-kaart:not([hidden])').length;
    var rest = kolommen - (zichtbaar % kolommen);
    var span = rest === kolommen ? kolommen : rest;
    contact.style.gridColumn = 'span ' + span;
    contact.classList.toggle('kt-contact--smal', span === 1);
    contact.classList.toggle('kt-contact--breed', span >= 3);
  }

  /* ── filterchips: een chip tegelijk; 'alle' toont alles ── */
  var chips = document.querySelectorAll('.kt-chip');
  var kaarten = document.querySelectorAll('.kt-kaart');
  var tel = document.querySelector('[data-kt-tel]'), woord = document.querySelector('[data-kt-woord]');
  function filter(sleutel) {
    var n = 0;
    Array.prototype.forEach.call(kaarten, function (k) {
      var past = sleutel === 'alle' || (' ' + k.getAttribute('data-kenmerken') + ' ').indexOf(' ' + sleutel + ' ') > -1;
      k.hidden = !past;
      if (past) n++;
    });
    Array.prototype.forEach.call(chips, function (c) { c.setAttribute('aria-pressed', c.getAttribute('data-filter') === sleutel ? 'true' : 'false'); });
    if (tel) tel.textContent = n;
    if (woord) woord.textContent = n === 1 ? 'kamertype' : 'kamertypes';
    zetContact();
  }
  Array.prototype.forEach.call(chips, function (c) {
    c.addEventListener('click', function () { filter(c.getAttribute('data-filter')); });
  });
  window.ktFilter = filter;

  zetContact();
  var wacht;
  window.addEventListener('resize', function () { clearTimeout(wacht); wacht = setTimeout(zetContact, 100); });
})();
