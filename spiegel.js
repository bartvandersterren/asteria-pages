/* Hotel Asteria, spiegel van de Effecty-staging op visit.asteria.nl (scripts/staging_spiegel.py).
   Eigen script naast de gespiegelde page-interactions.js; dat bestand blijft zoals de staging het levert.
   Luistert in de capture-fase op window, dus vóór de handlers van page-interactions.js:
   - Boeken: elke [data-mews-open] / a.mews-open opent de Mews-widget (config 6dc9094c) op deze pagina,
     met de datums en het aantal volwassenen uit de staging-boekkaart (window.__asteriaBooking) en de kamer uit
     data-room of uit het veld Type kamer. Laadt de widget niet binnen 4 s, dan de distributor-URL in een nieuw
     tabblad (mewsStart/mewsEnd/mewsAdultCount/mewsRoom). Conversie na boeken: GA4 purchase + Google Ads, zoals
     lander-w1.js op hotel-venray-v2.
   - Nieuwsbrief (voet + nieuwsbriefblok, data-spiegel-nieuwsbrief): POST /api/nieuwsbrief (Klaviyo, taal nl,
     bron pagina) in plaats van de Formspree-plaatshouder van de staging.
   - Contactformulier (.formblock__form): opent een e-mail aan info@asteria.nl met de ingevulde velden
     (de staging post naar een Formspree-plaatshouder).
   - Cookiemelding zoals hotel-venray-v2. */
(function () {
  'use strict';

  var MEWS_CONFIG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
  var MEWS_SRC = 'https://app.mews.com/distributor/distributor.min.js';
  var MEWS_URL = 'https://app.mews.com/distributor/' + MEWS_CONFIG;
  /* kamernamen zoals in het veld Type kamer van de staging -> Mews-categorie (zelfde id's als build.py KAMER_MEWS) */
  var KAMERS = {
    'comfort kamer': '98900f3b-e5e2-49c9-9776-af1d00ffc315',
    'comfort 3-persoons': '85ca19d7-eea5-41c8-8b93-af1d00ffc315',
    'comfort kamer 3 personen': '85ca19d7-eea5-41c8-8b93-af1d00ffc315',
    'mindervalide kamer': 'fa5b6540-7234-49ce-beb1-af1d00ffc315',
    'royale kamer': 'a8fd7310-0d61-422f-89e6-af1d00ffc315',
    'deluxe kamer': 'c737de50-e41e-4c8d-a818-af1d00ffc315',
    'junior suite': '27ea8deb-ded5-4856-8fdd-af1d00ffc315',
    'suite': '4a642b66-68e6-444c-beeb-af1d00ffc315',
    'bruidssuite': 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'
  };

  /* ── Mews-widget ── */
  var mewsLaden = false;
  function laadMews() {
    if (mewsLaden) return;
    mewsLaden = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = MEWS_SRC;
    s.onload = function () {
      if (!window.Mews || !window.Mews.Distributor) return;
      window.Mews.Distributor({
        configurationIds: [MEWS_CONFIG],
        onBookingFinished: function (res) {
          try {
            var val = null;
            if (res && res.length) {
              val = res.reduce(function (t, r) { return t + (r.totalCost && r.totalCost.value ? r.totalCost.value : 0); }, 0);
            }
            var txId = (res && res[0] && (res[0].reservationGroupId || res[0].id)) || Date.now().toString(36);
            if (typeof window.gtag === 'function') {
              if (val) window.gtag('event', 'purchase', { send_to: 'G-DPCP945DCG', value: val, currency: 'EUR', transaction_id: txId });
              if (window.GA_ADS_LABEL) window.gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL, value: val || 0, currency: 'EUR', transaction_id: txId });
            }
          } catch (e) {}
        }
      }, function (api) {
        window.mewsApi = api;
        if (window._mewsPending) { window._mewsPending(); window._mewsPending = null; }
      });
    };
    document.head.appendChild(s);
  }

  function viaMews(open, href) {
    if (window.mewsApi) { open(); return; }
    window._mewsPending = open;
    laadMews();
    setTimeout(function () {
      if (window._mewsPending) {
        window._mewsPending = null;
        window.open(href, '_blank', 'noopener');
      }
    }, 4000);
  }

  function twee(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(d) { return d.getFullYear() + '-' + twee(d.getMonth() + 1) + '-' + twee(d.getDate()); }
  function geldig(d) { return d instanceof Date && !isNaN(d); }

  /* keuzes uit de staging-boekkaart (zelfde bronnen als mewsSnapshot in page-interactions.js) */
  function keuzes(knop) {
    var data = window.__asteriaBooking || {};
    var a = geldig(data.aankomst) ? data.aankomst : null;
    var v = geldig(data.vertrek) ? data.vertrek : null;
    if (a && (!v || v <= a)) v = new Date(a.getFullYear(), a.getMonth(), a.getDate() + 1);
    var tel = document.querySelector('.booking-card [data-guests-row="volwassenen"] [data-guests-count]')
           || document.querySelector('[data-guests-row="volwassenen"] [data-guests-count]');
    var n = tel ? parseInt(tel.textContent, 10) : NaN;
    var kamer = knop && knop.getAttribute('data-room') || '';
    if (!kamer) {
      var type = document.querySelector('.booking-card [data-field="type"] .value')
              || document.querySelector('.booking-bar [data-bar-field="type"] [data-bar-value]');
      var naam = type ? type.textContent.trim().toLowerCase() : '';
      kamer = KAMERS[naam] || '';
    }
    return { a: a, v: v, n: isFinite(n) && n > 0 ? n : 2, kamer: kamer };
  }

  function sluitDrawer() {
    var d = document.getElementById('nav-drawer');
    if (d && d.classList.contains('is-open')) {
      d.classList.remove('is-open');
      document.body.style.overflow = '';
    }
  }

  function boek(knop) {
    var k = keuzes(knop);
    var url = MEWS_URL + '?mewsAdultCount=' + k.n
      + (k.a ? '&mewsStart=' + ymd(k.a) + '&mewsEnd=' + ymd(k.v) : '')
      + (k.kamer ? '&mewsRoom=' + k.kamer + '&mewsRoute=rooms' : '');
    var log = { start: k.a ? ymd(k.a) : null, eind: k.v ? ymd(k.v) : null, volwassenen: k.n, kamer: k.kamer, url: url, route: 'wacht' };
    window.spiegelBoek = log;
    sluitDrawer();
    viaMews(function () {
      var api = window.mewsApi;
      if (api.setLanguageCode) api.setLanguageCode('nl-NL');
      if (k.a && api.setStartDate && api.setEndDate) { api.setStartDate(k.a); api.setEndDate(k.v); }
      if (api.setAdultCount) api.setAdultCount(k.n);
      if (k.kamer && api.showRates) api.showRates(k.kamer);
      log.route = 'widget';
      api.open();
    }, url);
  }

  window.addEventListener('click', function (e) {
    var knop = e.target.closest ? e.target.closest('[data-mews-open], a.mews-open') : null;
    if (!knop) return;
    if (e.button || e.metaKey || e.ctrlKey || e.shiftKey) return;   /* middelklik / nieuw tabblad: gewone link */
    e.preventDefault();
    e.stopImmediatePropagation();
    boek(knop);
  }, true);

  /* ── formulieren ── */
  function meld(form, tekst, fout) {
    var p = form.querySelector('.spiegel-melding');
    if (!p) {
      p = document.createElement('p');
      p.className = 'spiegel-melding';
      p.setAttribute('role', 'status');
      form.appendChild(p);
    }
    p.textContent = tekst;
    p.classList.toggle('is-fout', !!fout);
  }

  var geopend = Date.now();

  function nieuwsbrief(form) {
    var veld = form.querySelector('input[type="email"]');
    var mail = veld ? veld.value.trim() : '';
    if (!mail || (veld.checkValidity && !veld.checkValidity())) {
      meld(form, 'Vul een geldig e-mailadres in.', true);
      if (veld) veld.focus();
      return;
    }
    var knop = form.querySelector('button[type="submit"]');
    if (knop) knop.disabled = true;
    var ok = form.parentNode && form.parentNode.querySelector('[data-newsletter-success]');
    var fout = form.parentNode && form.parentNode.querySelector('[data-newsletter-error]');
    if (fout) fout.classList.remove('is-visible');
    fetch('/api/nieuwsbrief', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: mail, taal: 'nl', bron: 'pagina', website: '', ts: geopend })
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { return r.ok && j.ok !== false; });
    }).then(function (gelukt) {
      if (knop) knop.disabled = false;
      if (gelukt) {
        if (typeof window.gtag === 'function') window.gtag('event', 'sign_up', { method: 'nieuwsbrief', bron: 'spiegel' });
        if (ok) { form.style.display = 'none'; ok.classList.add('is-visible'); }
        else { form.reset(); meld(form, 'Bedankt, je bent aangemeld voor de nieuwsbrief.'); }
      } else {
        if (fout) fout.classList.add('is-visible');
        else meld(form, 'Aanmelden lukte niet. Probeer het later opnieuw of mail naar info@asteria.nl.', true);
      }
    }).catch(function () {
      if (knop) knop.disabled = false;
      if (fout) fout.classList.add('is-visible');
      else meld(form, 'Aanmelden lukte niet. Probeer het later opnieuw of mail naar info@asteria.nl.', true);
    });
  }

  function contact(form) {
    if (form.checkValidity && !form.checkValidity()) {
      if (form.reportValidity) form.reportValidity();
      return;
    }
    if ((form.querySelector('[name="_gotcha"]') || {}).value) return;
    var regels = [];
    Array.prototype.forEach.call(form.querySelectorAll('input, select, textarea'), function (el) {
      if (!el.name || el.name.charAt(0) === '_' || !el.value) return;
      var label = form.querySelector('label[for="' + el.id + '"]');
      var naam = label ? label.textContent.replace('*', '').trim() : el.name;
      regels.push(naam + ': ' + el.value);
    });
    var onderwerp = (form.querySelector('[name="onderwerp"]') || {}).value || 'Contact';
    var href = 'mailto:info@asteria.nl?subject=' + encodeURIComponent('Contactformulier: ' + onderwerp)
      + '&body=' + encodeURIComponent(regels.join('\n'));
    window.spiegelContact = href;
    window.location.href = href;
    meld(form, 'Je e-mailprogramma opent met je bericht aan info@asteria.nl. Verstuur het daar.');
  }

  window.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.matches) return;
    if (form.matches('[data-spiegel-nieuwsbrief]')) { e.preventDefault(); e.stopImmediatePropagation(); nieuwsbrief(form); return; }
    if (form.matches('.formblock__form')) { e.preventDefault(); e.stopImmediatePropagation(); contact(form); return; }
    if (form.matches('[data-booking-form], .final-cta__widget')) { e.preventDefault(); e.stopImmediatePropagation(); boek(null); }
  }, true);

  /* ── live kamerprijzen: [data-kamer-vanaf="<sleutel>"] (staging_spiegel.py markeer_prijzen) via /api/kamer-vanaf.
     spiegel.css houdt het element verborgen (visibility) tot het gevuld is; geen prijs of fout = blijft verborgen. ── */
  var prijsEls = document.querySelectorAll('[data-kamer-vanaf]');
  if (prijsEls.length && window.fetch) {
    fetch('/api/kamer-vanaf', { headers: { Accept: 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        var prijzen = (data && data.ok && data.prijzen) || {};
        window.spiegelKamerVanaf = prijzen;
        Array.prototype.forEach.call(prijsEls, function (el) {
          var p = prijzen[el.getAttribute('data-kamer-vanaf')];
          var bedrag = el.querySelector('[data-kamer-vanaf-bedrag]');
          if (!p || typeof p.euro !== 'number' || !bedrag) return;
          bedrag.textContent = '€ ' + p.euro;
          el.classList.add('is-gevuld');
        });
      })
      .catch(function () { window.spiegelKamerVanaf = null; });
  }

  /* ── Kaartblok (contact): de staging heeft de knop "Laad de kaart" zonder script. Een klik is de toestemming:
     dan pas de Google-kaart (embed zonder API-sleutel) op de plek van de consenttekst; het adres komt uit de
     routelink van hetzelfde blok (destination=...), anders het vaste hoteladres. CSS staat al in base.css
     (.kaartblok__kaart iframe). ── */
  Array.prototype.forEach.call(document.querySelectorAll('.kaartblok__consent button'), function (knop) {
    knop.addEventListener('click', function () {
      var blok = knop.closest('.kaartblok');
      var kaart = knop.closest('.kaartblok__kaart');
      if (!kaart) return;
      var route = blok && blok.querySelector('a[href*="destination="]');
      var adres = 'Hotel Asteria, Maasheseweg 80a, 5804 AD Venray';
      if (route) {
        try { adres = new URL(route.href).searchParams.get('destination') || adres; } catch (e) {}
      }
      var f = document.createElement('iframe');
      f.src = 'https://www.google.com/maps?q=' + encodeURIComponent(adres) + '&output=embed';
      f.title = 'Kaart: ' + adres;
      f.loading = 'lazy';
      f.referrerPolicy = 'no-referrer-when-downgrade';
      f.setAttribute('allowfullscreen', '');
      var consent = knop.closest('.kaartblok__consent');
      if (consent) consent.remove();
      kaart.appendChild(f);
    });
  });

  /* ── cookiemelding (zoals hotel-venray-v2) ── */
  var banner = document.getElementById('cookieBanner');
  var akkoord = document.getElementById('cookieAccept');
  if (banner) {
    try { if (!localStorage.getItem('cookie-consent')) banner.classList.add('show'); } catch (e) { banner.classList.add('show'); }
    if (akkoord) akkoord.addEventListener('click', function () {
      try { localStorage.setItem('cookie-consent', '1'); } catch (e) {}
      banner.classList.remove('show');
    });
  }
})();
