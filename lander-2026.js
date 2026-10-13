/* Hotel Asteria, lander-sjabloon 2026 (visit.asteria.nl). Vanilla, geen frameworks.
   - Mews-poort: eerste klik op .mews-open laadt de widget; voucher uit data-voucher, kamer uit data-room.
     Valt na 4 s terug op de deeplink (href) in een nieuw tabblad.
   - Kamerslider met teller, reviewstrook-pijl, onderbalk op de telefoon, drawer, dropdowns, --kop-h. */
(function () {
  'use strict';

  var MEWS_CONFIG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
  var MEWS_SRC = 'https://app.mews.com/distributor/distributor.min.js';
  var root = document.documentElement;

  /* ── hoogte van de sticky kop → --kop-h (voor de meelopende zijkaart) ── */
  var kop = document.querySelector('.top-stack');
  function meetKop() {
    if (kop) root.style.setProperty('--kop-h', kop.offsetHeight + 'px');
  }
  meetKop();
  window.addEventListener('resize', meetKop);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(meetKop);

  /* ── Mews-poort ── */
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

  document.addEventListener('click', function (e) {
    var knop = e.target.closest ? e.target.closest('.mews-open') : null;
    if (!knop) return;
    e.preventDefault();
    var voucher = knop.getAttribute('data-voucher') || '';
    var kamer = knop.getAttribute('data-room') || '';
    var href = knop.getAttribute('href');
    sluitDrawer();
    function open() {
      var api = window.mewsApi;
      if (voucher && api.setVoucherCode) api.setVoucherCode(voucher);
      if (api.setLanguageCode) api.setLanguageCode('nl-NL');
      if (kamer && api.showRates) api.showRates(kamer);
      else api.open();
    }
    if (window.mewsApi) { open(); return; }
    window._mewsPending = open;
    laadMews();
    setTimeout(function () {
      if (window._mewsPending) {
        window._mewsPending = null;
        window.open(href, '_blank', 'noopener');
      }
    }, 4000);
  });

  /* ── strook-hulp: één kaart verder of terug, met lus ── */
  function stap(strook) {
    var kaart = strook.firstElementChild;
    if (!kaart) return 0;
    var gap = parseFloat(getComputedStyle(strook).columnGap) || 0;
    return kaart.getBoundingClientRect().width + gap;
  }
  function aanEind(strook) { return strook.scrollLeft + strook.clientWidth >= strook.scrollWidth - 4; }
  function verschuif(strook, richting) {
    if (richting > 0 && aanEind(strook)) { strook.scrollTo({ left: 0, behavior: 'smooth' }); return; }
    if (richting < 0 && strook.scrollLeft <= 4) { strook.scrollTo({ left: strook.scrollWidth, behavior: 'smooth' }); return; }
    strook.scrollBy({ left: richting * stap(strook), behavior: 'smooth' });
  }

  /* ── kamerslider met teller i/8 boven en onder ── */
  var kamers = document.querySelector('.b4a-strook');
  if (kamers) {
    var totaal = kamers.children.length;
    var tellers = document.querySelectorAll('.b4a-telgetal');
    var zetTeller = function () {
      var w = stap(kamers) || 1;
      var i = Math.round(kamers.scrollLeft / w) + 1;
      if (aanEind(kamers)) i = Math.max(i, totaal - Math.round(kamers.clientWidth / w) + 1);
      i = Math.min(Math.max(i, 1), totaal);
      for (var t = 0; t < tellers.length; t++) tellers[t].textContent = i + '/' + totaal;
    };
    var wacht;
    kamers.addEventListener('scroll', function () { clearTimeout(wacht); wacht = setTimeout(zetTeller, 60); }, { passive: true });
    document.querySelectorAll('.b4a-volgende').forEach(function (b) { b.addEventListener('click', function () { verschuif(kamers, 1); }); });
    document.querySelectorAll('.b4a-vorige').forEach(function (b) { b.addEventListener('click', function () { verschuif(kamers, -1); }); });
    zetTeller();
  }

  /* ── reviewstrook: pijl schuift één kaart, aan het eind terug naar het begin ── */
  var spoor = document.querySelector('.b5a-spoor');
  var reviewPijl = document.querySelector('.b5a-pijl');
  if (spoor && reviewPijl) reviewPijl.addEventListener('click', function () { verschuif(spoor, 1); });

  /* ── onderbalk op de telefoon zodra de hero uit beeld is ── */
  var balk = document.querySelector('.mob-cta');
  var hero = document.querySelector('.b1a-hero');
  if (balk && hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (items) {
      var it = items[0];
      var weg = !it.isIntersecting && it.boundingClientRect.top < 0;
      balk.classList.toggle('is-zichtbaar', weg);
      balk.setAttribute('aria-hidden', weg ? 'false' : 'true');
      var a = balk.querySelector('a');
      if (a) a.setAttribute('tabindex', weg ? '0' : '-1');
    }).observe(hero);
  }

  /* ── mobiele drawer ── */
  var drawer = document.getElementById('nav-drawer');
  var hamburger = document.querySelector('.nav-hamburger');
  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
    var sluit = drawer.querySelector('.nav-drawer__close');
    if (sluit) sluit.focus();
  }
  function sluitDrawer() {
    if (!drawer || !drawer.classList.contains('is-open')) return;
    drawer.classList.remove('is-open');
    document.body.style.overflow = '';
    if (hamburger) { hamburger.setAttribute('aria-expanded', 'false'); hamburger.focus(); }
  }
  if (hamburger) hamburger.addEventListener('click', openDrawer);
  if (drawer) {
    drawer.addEventListener('click', function (e) {
      if (e.target === drawer || e.target.closest('.nav-drawer__close')) sluitDrawer();
    });
    drawer.querySelectorAll('.drawer-parent').forEach(function (b) {
      b.addEventListener('click', function () {
        var li = b.parentElement;
        var open = li.classList.toggle('is-open');
        b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ── dropdowns in het hoofdmenu: hover via css, klik via .is-open ── */
  var subs = document.querySelectorAll('.nav-links .has-sub');
  function sluitSubs(behalve) {
    subs.forEach(function (li) {
      if (li === behalve) return;
      li.classList.remove('is-open');
      var b = li.querySelector('.nav-parent');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
  }
  subs.forEach(function (li) {
    var b = li.querySelector('.nav-parent');
    if (!b) return;
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !li.classList.contains('is-open');
      sluitSubs(li);
      li.classList.toggle('is-open', open);
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.nav-links .has-sub')) sluitSubs(null);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { sluitDrawer(); sluitSubs(null); }
  });

  /* ── cookiemelding (zoals welkom) ── */
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
