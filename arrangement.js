/* Arrangementsjabloon op lander-w1: aanvulling op lander-w1.js, alleen geladen via build-blok 'arrangement'.
   Kamerraster (.ar-kamers, tot 3 kamers): de meelopende zijkaart stopt gelijk met de onderkant van de kamerkaarten
   (--kant-onder op .lp-zone, zoals lander-w1.js dat voor de slider doet). */
(function () {
  'use strict';
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
