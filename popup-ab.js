/* ══════════════════════════════════════════════════════════
   NIEUWSBRIEF-POPUP — A/B LOADER
   Wijst elke bezoeker 50/50 toe aan:
     A = newsletter-popup.js  (witte-kaart popup)
     B = scratchcard-popup.js (kras & win)
   De keuze wordt per bezoeker vastgezet (localStorage popup_variant),
   zodat een terugkerende bezoeker steeds dezelfde variant ziet.
   Insluiten met: <script src="/popup-ab.js" defer></script>
══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // Popup al aanwezig (inline op arrangementpagina's) of al aangemeld → niets doen
  if (document.getElementById('ecOverlay') || document.getElementById('scOverlay')) return;
  if (localStorage.getItem('ec_converted')) return;

  // Variant bepalen en vastzetten
  var v = localStorage.getItem('popup_variant');
  if (v !== 'A' && v !== 'B') {
    v = Math.random() < 0.5 ? 'A' : 'B';
    try { localStorage.setItem('popup_variant', v); } catch (e) {}
  }
  window.POPUP_VARIANT = v;

  // Gekozen variant laden
  var src = (v === 'B') ? '/scratchcard-popup.js' : '/newsletter-popup.js';
  var s = document.createElement('script');
  s.src = src;
  s.defer = true;
  document.head.appendChild(s);
})();
