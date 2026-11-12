/* REVIEWS-GOOGLE: pijlknop van het Google-reviewblok (build.py google_reviewblok, reviews-google.css). Telefoon: veegspoor met
   scroll-snap, knop staat uit in de CSS. Bureaublad: het spoor staat op overflow:hidden; de knop schuift een kaart op en springt
   aan het eind terug naar het begin. */
(function () {
  'use strict';
  Array.prototype.forEach.call(document.querySelectorAll('[data-grv-strook]'), function (strook) {
    var spoor = strook.querySelector('.grv__spoor'), knop = strook.querySelector('[data-grv-pijl]');
    if (!spoor || !knop) return;
    knop.addEventListener('click', function () {
      var kaart = spoor.querySelector('.grv__kaart');
      if (!kaart) return;
      var gat = parseFloat(getComputedStyle(spoor).columnGap) || 16,
          stap = kaart.getBoundingClientRect().width + gat,
          eind = spoor.scrollWidth - spoor.clientWidth;
      spoor.scrollTo({ left: spoor.scrollLeft >= eind - 2 ? 0 : Math.min(spoor.scrollLeft + stap, eind), behavior: 'smooth' });
    });
  });
})();
