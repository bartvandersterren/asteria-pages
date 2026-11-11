/* REVIEWS-TA: pijlknop van het Tripadvisor-reviewblok (build.py ta_reviewblok, reviews-ta.css). Port van Parkhotel
   gedrag/blok-reviews-tripadvisor.js. Telefoon: veegspoor met scroll-snap, knop staat uit in de CSS. Bureaublad: het spoor
   staat op overflow:hidden; de knop schuift een kaart op en springt aan het eind terug naar het begin. */
(function () {
  'use strict';
  Array.prototype.forEach.call(document.querySelectorAll('[data-rta-strook]'), function (strook) {
    var spoor = strook.querySelector('.rta__spoor'), knop = strook.querySelector('[data-rta-pijl]');
    if (!spoor || !knop) return;
    knop.addEventListener('click', function () {
      var kaart = spoor.querySelector('.rta__kaart');
      if (!kaart) return;
      var gat = parseFloat(getComputedStyle(spoor).columnGap) || 16,
          stap = kaart.getBoundingClientRect().width + gat,
          eind = spoor.scrollWidth - spoor.clientWidth;
      spoor.scrollTo({ left: spoor.scrollLeft >= eind - 2 ? 0 : Math.min(spoor.scrollLeft + stap, eind), behavior: 'smooth' });
    });
  });
})();
