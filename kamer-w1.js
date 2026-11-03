/* Hotel Asteria, kamerdetailpagina kamer-w1 (visit.asteria.nl/<kamer>-v2). Vanilla, laadt na lander-w1.js.
   - Lightbox (dialog #km-lb): items uit #km-media (video eerst, dan de foto's); elke [data-lb="i"] opent item i.
     Pijlen, pijltjestoetsen, vegen op de telefoon, Esc/sluitknop; video pauzeert bij wisselen en sluiten.
   - Schuifstroken [data-schuif] (reviews, andere kamers): vorige/volgende scrollen een kaart, knoppen uit aan de randen.
   - Onderbalk (telefoon, .mob-cta uit lander-w1): zichtbaar zodra de boekkaart boven uit beeld is.
   Mews (.mews-open met data-room) en de cookiemelding regelt lander-w1.js. */
(function () {
  'use strict';
  var root = document.documentElement;

  function leesJson(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  /* ── lightbox ── */
  var media = leesJson('km-media') || [];
  var tekst = leesJson('km-tekst') || {};
  var lb = document.getElementById('km-lb');
  if (lb && media.length) {
    var vak = lb.querySelector('.km-lb-beeld');
    var teller = lb.querySelector('.km-lb-teller');
    var vorige = lb.querySelector('.km-lb-vorige');
    var volgende = lb.querySelector('.km-lb-volgende');
    var aantalFotos = media.filter(function (m) { return m.type === 'img'; }).length;
    var huidig = 0, terugFocus = null;
    var kanModal = typeof lb.showModal === 'function';

    var toon = function (i) {
      huidig = (i + media.length) % media.length;
      var m = media[huidig];
      var oud = vak.querySelector('video');
      if (oud) { try { oud.pause(); } catch (e) {} }
      vak.textContent = '';
      var el;
      if (m.type === 'video') {
        el = document.createElement('video');
        el.src = m.src; el.poster = m.poster || ''; el.controls = true; el.playsInline = true; el.preload = 'metadata';
        el.setAttribute('aria-label', m.alt || tekst.video || 'Video');
        if (!window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          el.muted = true; el.autoplay = true;
        }
      } else {
        el = document.createElement('img');
        el.src = m.src; el.alt = m.alt || '';
      }
      vak.appendChild(el);
      var fotoNr = media.slice(0, huidig + 1).filter(function (x) { return x.type === 'img'; }).length;
      teller.textContent = m.type === 'video' ? (tekst.video || 'Video')
        : fotoNr + ' ' + (tekst.van || 'van') + ' ' + aantalFotos;
      var meer = media.length > 1;
      vorige.hidden = !meer; volgende.hidden = !meer;
    };
    var open = function (i, knop) {
      terugFocus = knop || document.activeElement;
      toon(i);
      root.classList.add('km-lb-vast');
      if (kanModal) lb.showModal(); else lb.setAttribute('open', '');
      lb.querySelector('.km-lb-sluit').focus({ preventScroll: true });
    };
    var sluit = function () {
      if (kanModal && lb.open) lb.close(); else lb.removeAttribute('open');
    };
    lb.addEventListener('close', function () {
      var v = vak.querySelector('video');
      if (v) { try { v.pause(); } catch (e) {} }
      vak.textContent = '';
      root.classList.remove('km-lb-vast');
      if (terugFocus && terugFocus.focus) terugFocus.focus({ preventScroll: true });
    });
    document.addEventListener('click', function (e) {
      var knop = e.target.closest ? e.target.closest('[data-lb]') : null;
      if (!knop) return;
      e.preventDefault();
      open(parseInt(knop.getAttribute('data-lb'), 10) || 0, knop);
    });
    lb.querySelector('.km-lb-sluit').addEventListener('click', sluit);
    vorige.addEventListener('click', function () { toon(huidig - 1); });
    volgende.addEventListener('click', function () { toon(huidig + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('km-lb-binnen') || e.target === vak) sluit(); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); toon(huidig - 1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); toon(huidig + 1); }
      else if (e.key === 'Escape' && !kanModal) sluit();
    });
    var startX = null;
    lb.addEventListener('touchstart', function (e) { startX = e.touches.length === 1 ? e.touches[0].clientX : null; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 50 && !(e.target && e.target.tagName === 'VIDEO')) toon(huidig + (dx < 0 ? 1 : -1));
    }, { passive: true });
  }

  /* ── schuifstroken ── */
  document.querySelectorAll('[data-schuif]').forEach(function (blok) {
    var spoor = blok.querySelector('.km-spoor');
    var knoppen = blok.querySelectorAll('.km-pijl');
    if (!spoor) return;
    var stap = function () {
      var items = spoor.children;
      if (items.length > 1) return items[1].offsetLeft - items[0].offsetLeft;
      return spoor.clientWidth;
    };
    var zet = function () {
      var max = spoor.scrollWidth - spoor.clientWidth - 4;
      knoppen.forEach(function (k) {
        var r = parseInt(k.getAttribute('data-richting'), 10);
        k.disabled = r < 0 ? spoor.scrollLeft <= 4 : spoor.scrollLeft >= max;
      });
      var nav = blok.querySelector('.km-nav');
      if (nav) nav.hidden = spoor.scrollWidth <= spoor.clientWidth + 4;
    };
    knoppen.forEach(function (k) {
      k.addEventListener('click', function () {
        spoor.scrollBy({ left: stap() * parseInt(k.getAttribute('data-richting'), 10), behavior: 'smooth' });
      });
    });
    var wacht;
    spoor.addEventListener('scroll', function () { clearTimeout(wacht); wacht = setTimeout(zet, 60); }, { passive: true });
    window.addEventListener('resize', zet);
    zet();
  });

  /* ── onderbalk op de telefoon: zodra de boekkaart boven uit beeld is ── */
  var balk = document.querySelector('.mob-cta');
  var kaart = document.querySelector('.km-boek');
  if (balk && kaart && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (items) {
      var it = items[0];
      var weg = !it.isIntersecting && it.boundingClientRect.top < 0;
      balk.classList.toggle('is-zichtbaar', weg);
      root.classList.toggle('mob-cta-aan', weg);
      root.style.setProperty('--mob-cta-h', balk.offsetHeight + 'px');
      balk.setAttribute('aria-hidden', weg ? 'false' : 'true');
      balk.querySelectorAll('a').forEach(function (a) { a.setAttribute('tabindex', weg ? '0' : '-1'); });
    }).observe(kaart);
  }
})();
