/* ══════════════════════════════════════════════════════════
   NIEUWSBRIEF-BACKEND — Hotel Asteria (gedeeld)
   Eén schakelaar voor waar de nieuwsbrief-aanmeldingen van de
   pop-ups (A witte kaart, B scratchcard) heen gaan:
     'revinate' = verborgen Revinate-form (zoals altijd)
     'klaviyo'  = POST /api/nieuwsbrief (Pages Function -> Klaviyo,
                  lijst Nieuwsbrief NL/EN/DE, secret KLAVIYO_API_KEY_ASTERIA)
   Omschakelen = alleen de regel hieronder aanpassen.
   Wordt geladen door popup-ab.js vóór de pop-up zelf.
══════════════════════════════════════════════════════════ */
var NIEUWSBRIEF_BACKEND = 'revinate'; // 'revinate' | 'klaviyo'

(function () {
  'use strict';
  window.AsteriaNieuwsbrief = {
    backend: NIEUWSBRIEF_BACKEND,
    klaviyo: function () { return NIEUWSBRIEF_BACKEND === 'klaviyo'; },
    /**
     * Aanmelden via /api/nieuwsbrief.
     * opts: { taal: 'nl'|'en'|'de', bron: 'popup'|'scratchcard'|'pagina', website: honeypot, ts: ms open }
     * Geeft een Promise<boolean> (true = aangemeld).
     */
    aanmelden: function (email, opts) {
      opts = opts || {};
      return fetch('/api/nieuwsbrief', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          taal: opts.taal || 'nl',
          bron: opts.bron || 'popup',
          website: opts.website || '',
          ts: opts.ts || 0
        })
      }).then(function (res) {
        return res.json().then(function (d) { return !!(res.ok && d && d.ok); }, function () { return false; });
      }, function () { return false; });
    }
  };
})();
