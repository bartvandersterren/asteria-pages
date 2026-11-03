/* ══════════════════════════════════════════════════════════
   Live "vanaf"-prijs op de arrangementpagina's (lander-w1, blok arrangement)
   Elk prijselement met data-arr-vanaf="<CODE>" toont server-side de vaste
   prijs uit de arrangement-JSON (terugval). Dit script vraagt
   /api/arr-vanaf?codes=<CODE,...> op en zet het bedrag ("€ 125") erin zodra er
   een antwoord is; de eenheid eromheen (p.p. per nacht / voor N nachten) staat
   al in de pagina en verandert niet. Geen antwoord of null = vaste prijs blijft.
   Geen layout-sprong: alleen de tekst van het inline bedrag wisselt (harde
   spatie, geen andere regelhoogte); blokken eromheen houden hun plek en hoogte.
   window.arrVanaf = log {codes, status, prijzen} (voor tests).
══════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var els = Array.prototype.slice.call(document.querySelectorAll('[data-arr-vanaf]'));
  if (!els.length || !window.fetch) return;
  var codes = [];
  els.forEach(function (el) { var c = el.getAttribute('data-arr-vanaf'); if (c && codes.indexOf(c) < 0) codes.push(c); });
  var log = window.arrVanaf = { codes: codes, status: 'wacht', prijzen: null };
  function bedrag(euro) { return '€ ' + String(euro).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  fetch('/api/arr-vanaf?codes=' + encodeURIComponent(codes.join(',')), { headers: { Accept: 'application/json' } })
    .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
    .then(function (d) {
      var p = (d && d.ok && d.prijzen) || {};
      log.prijzen = p; log.status = 'ok';
      els.forEach(function (el) {
        var x = p[el.getAttribute('data-arr-vanaf')];
        if (!x || typeof x.euro !== 'number' || !(x.euro > 0)) return;
        el.textContent = bedrag(x.euro);
        el.setAttribute('data-arr-vanaf-live', '1');
      });
    })
    .catch(function (e) { log.status = 'fout: ' + e.message; });
})();
