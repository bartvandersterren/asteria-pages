/* Hotel Asteria, lander-sjabloon 2026 (visit.asteria.nl). Vanilla, geen frameworks.
   - Mews-poort: eerste klik op .mews-open laadt de widget; voucher uit data-voucher, kamer uit data-room.
     Valt na 4 s terug op de deeplink (href) in een nieuw tabblad.
   - Kamerslider met teller, reviewstrook-pijl, onderbalk op de telefoon, drawer, dropdowns, --kop-h.
   - Pop-ups (dialog) voor Meer info bij de kamers en de faciliteitentegels; Laad meer faciliteiten. */
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

  /* ── oneindige strook zoals de Parkhotel-landers: de hele rij staat een keer vooraan en een keer
     achteraan gekloond; na 120 ms stilstand springt de strook onzichtbaar terug naar het echte
     exemplaar. Teller (optioneel) telt alleen de echte kaarten. ── */
  function lus(strook, cfg) {
    if (!strook || strook.children.length < 2) return;
    var echt = Array.prototype.slice.call(strook.children), n = echt.length, off = n;
    var kloon = function (k) {
      var c = k.cloneNode(true); c.setAttribute('data-kloon', ''); c.setAttribute('aria-hidden', 'true');
      c.querySelectorAll('a,button').forEach(function (x) { x.setAttribute('tabindex', '-1'); });
      return c;
    };
    echt.forEach(function (k) { strook.insertBefore(kloon(k), echt[0]); });
    echt.forEach(function (k) { strook.appendChild(kloon(k)); });
    var alle = strook.children, tellers = cfg.tellers ? document.querySelectorAll(cfg.tellers) : [], huidig = 0;
    var stapK = function () { return alle[off + 1].offsetLeft - alle[off].offsetLeft || strook.clientWidth; };
    var positie = function () { return Math.round(strook.scrollLeft / stapK()) - off; };
    var update = function () {
      var i = ((positie() % n) + n) % n + 1; huidig = i - 1;
      for (var t = 0; t < tellers.length; t++) tellers[t].textContent = i + '/' + n;
    };
    var zetStart = function () { strook.scrollLeft = (off + huidig) * stapK(); };
    var wacht, wachtMaat, maatWissel = false, breedte = window.innerWidth;
    window.addEventListener('resize', function () {
      if (window.innerWidth === breedte) return;
      maatWissel = true; clearTimeout(wachtMaat);
      wachtMaat = setTimeout(function () { breedte = window.innerWidth; zetStart(); setTimeout(function () { maatWissel = false; update(); }, 50); }, 100);
    });
    strook.addEventListener('scroll', function () {
      if (maatWissel) return;
      window.requestAnimationFrame(update);
      clearTimeout(wacht);
      wacht = setTimeout(function () {
        var p = positie();
        if (p < 0) strook.scrollLeft += n * stapK(); else if (p >= n) strook.scrollLeft -= n * stapK();
      }, 120);
    }, { passive: true });
    if (cfg.volgende) document.querySelectorAll(cfg.volgende).forEach(function (b) { b.addEventListener('click', function () { strook.scrollBy({ left: stapK(), behavior: 'smooth' }); }); });
    if (cfg.vorige) document.querySelectorAll(cfg.vorige).forEach(function (b) { b.addEventListener('click', function () { strook.scrollBy({ left: -stapK(), behavior: 'smooth' }); }); });
    zetStart(); update();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(zetStart);
    window.addEventListener('load', zetStart);
  }
  lus(document.querySelector('.b4a-strook'), { tellers: '.b4a-telgetal', volgende: '.b4a-volgende', vorige: '.b4a-vorige' });
  lus(document.querySelector('.b5a-spoor'), { volgende: '.b5a-pijl' });

  /* ── de zijkaart loopt mee tot de onderkant van de kamerkaarten (zoals Parkhotel), niet tot de
     onderkant van de hele kamersectie ── */
  var zijkol = document.querySelector('.b1a-zijkol'), kaartStrook = document.querySelector('.b4a-strook');
  function zijkolHoogte() {
    if (!zijkol || !kaartStrook) return;
    zijkol.style.height = '';
    if (window.innerWidth < 1024) return;
    var pad = parseFloat(getComputedStyle(kaartStrook).paddingBottom) || 0;
    var onder = kaartStrook.getBoundingClientRect().bottom - pad, boven = zijkol.getBoundingClientRect().top;
    if (onder - boven > 200) zijkol.style.height = Math.round(onder - boven) + 'px';
  }
  zijkolHoogte(); window.addEventListener('resize', zijkolHoogte); window.addEventListener('load', zijkolHoogte);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(zijkolHoogte);

  /* ── onderbalk op de telefoon zodra de hero uit beeld is ── */
  var balk = document.querySelector('.mob-cta');
  var hero = document.querySelector('.b1a-hero');
  if (balk && hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (items) {
      var it = items[0];
      var weg = !it.isIntersecting && it.boundingClientRect.top < 0;
      balk.classList.toggle('is-zichtbaar', weg);
      document.documentElement.classList.toggle('mob-cta-aan', weg);
      document.documentElement.style.setProperty('--mob-cta-h', balk.offsetHeight + 'px');
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

  /* ── pop-ups: kamer (Meer info, blok 4a) en faciliteit (tegels, blok 6a) ──
     Eén <dialog> per soort, gevuld uit de JSON in het sjabloon (#lp-kamerdata, #lp-facdata).
     Native showModal (Escape, top layer, ::backdrop); zonder showModal een div met hidden + overlay.
     Video pas laden bij openen, leegmaken bij sluiten. Focus terug naar de knop die opende. */
  function leesJson(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  var kamerData = leesJson('lp-kamerdata') || {};
  var facData = leesJson('lp-facdata') || {};
  var popKamer = document.getElementById('lp-pop-kamer');
  var popFac = document.getElementById('lp-pop-fac');
  var popOverlay = document.querySelector('.lp-pop-overlay');
  var vinkSjabloon = document.getElementById('lp-pop-vink');
  var kanModal = !!(popKamer && typeof popKamer.showModal === 'function');
  var rustig = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var openPop = null, opener = null;

  if (!kanModal) [popKamer, popFac].forEach(function (d) { if (d) d.hidden = true; });

  function maak(tag, cls, tekst) {
    var el = document.createElement(tag);
    if (cls) el.className = cls;
    if (tekst != null) el.textContent = tekst;
    return el;
  }

  function toonPop(d, knop) {
    if (!d) return;
    if (openPop) sluitPop(openPop, true);
    opener = knop || null;
    openPop = d;
    root.classList.add('lp-pop-vast');
    var binnen = d.querySelector('.lp-pop__binnen');
    if (binnen) binnen.scrollTop = 0;
    if (kanModal) {
      d.showModal();
    } else {
      d.hidden = false;
      d.classList.add('is-open');
      d.setAttribute('role', 'dialog');
      if (popOverlay) popOverlay.hidden = false;
    }
    var sluit = d.querySelector('.lp-pop__sluit');
    if (sluit) sluit.focus();
  }

  function opruimen(d, stil) {
    var v = d.querySelector('video');
    if (v) { try { v.pause(); } catch (e) {} v.removeAttribute('src'); v.load(); }
    root.classList.remove('lp-pop-vast');
    if (openPop === d) openPop = null;
    var terug = opener;
    opener = null;
    if (!stil && terug && document.contains(terug)) terug.focus();
  }

  function sluitPop(d, stil) {
    if (!d) return;
    if (kanModal) {
      if (!d.open) return;
      d._stil = !!stil;
      d.close();
    } else {
      if (d.hidden) return;
      d.hidden = true;
      d.classList.remove('is-open');
      if (popOverlay) popOverlay.hidden = true;
      opruimen(d, stil);
    }
  }

  [popKamer, popFac].forEach(function (d) {
    if (!d) return;
    if (kanModal) {
      d.addEventListener('close', function () { var stil = d._stil; d._stil = false; opruimen(d, stil); });
    }
    d.addEventListener('click', function (e) {
      if (e.target === d || (e.target.closest && e.target.closest('.lp-pop__sluit'))) { sluitPop(d); return; }
      /* boekknop: pop-up dicht, de Mews-poort (document-listener) opent daarna de widget */
      if (e.target.closest && e.target.closest('.mews-open')) sluitPop(d, true);
    });
  });
  if (popOverlay) popOverlay.addEventListener('click', function () { if (openPop) sluitPop(openPop); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && openPop && !kanModal) sluitPop(openPop);
  });

  function vulKamer(key) {
    var k = kamerData[key];
    if (!k || !popKamer) return false;
    var fotos = k.fotos || [];
    var video = popKamer.querySelector('.lp-pop__video');
    var hero = popKamer.querySelector('.lp-pop__hero');
    var rij = popKamer.querySelector('.lp-pop__fotos');
    rij.textContent = '';
    var rijFotos;
    if (k.video) {
      hero.hidden = true; hero.removeAttribute('src');
      video.hidden = false;
      video.poster = fotos[0] || '';
      video.autoplay = !rustig;
      video.controls = rustig;
      video.src = k.video;
      if (!rustig) { var p = video.play(); if (p && p.catch) p.catch(function () {}); }
      rijFotos = fotos.slice(0, 3);
    } else {
      video.hidden = true; video.removeAttribute('src'); video.removeAttribute('poster');
      hero.hidden = false;
      hero.src = fotos[0] || '';
      hero.alt = k.naam + ' bij Hotel Asteria';
      rijFotos = fotos.slice(1, 4);
    }
    rij.setAttribute('data-n', rijFotos.length);
    rijFotos.forEach(function (src, i) {
      var img = maak('img');
      img.src = src; img.alt = k.naam + ', foto ' + (i + 1); img.loading = 'lazy'; img.decoding = 'async';
      rij.appendChild(img);
    });
    popKamer.querySelector('.lp-pop__titel').textContent = k.naam;
    var tekst = popKamer.querySelector('.lp-pop__tekst');
    tekst.textContent = '';
    (k.tekst || []).forEach(function (t) { tekst.appendChild(maak('p', null, t)); });
    var lijst = popKamer.querySelector('.lp-pop__kenmerken');
    lijst.textContent = '';
    (k.kenmerken || []).forEach(function (t) {
      var li = maak('li');
      if (vinkSjabloon && vinkSjabloon.content) li.appendChild(vinkSjabloon.content.cloneNode(true));
      li.appendChild(maak('span', null, t));
      lijst.appendChild(li);
    });
    var boek = popKamer.querySelector('.lp-pop__boek');
    boek.setAttribute('data-room', k.kamer);
    boek.setAttribute('href', boek.getAttribute('data-basis') + '&mewsRoom=' + k.kamer + '&mewsRoute=rooms');
    boek.setAttribute('aria-label', 'Boek de ' + k.naam);
    var link = popKamer.querySelector('.lp-pop__link');
    link.setAttribute('href', k.pagina);
    link.setAttribute('aria-label', 'Bekijk de kamerpagina van de ' + k.naam);
    return true;
  }

  function vulFac(key, knop) {
    var f = facData[key];
    if (!f || !popFac) return false;
    var tegel = knop.closest('.b6a-tegel');
    var bron = tegel ? tegel.querySelector('img') : null;
    var hero = popFac.querySelector('.lp-pop__hero');
    if (bron) { hero.src = bron.getAttribute('src'); hero.alt = bron.getAttribute('alt') || ''; hero.style.objectPosition = getComputedStyle(bron).objectPosition; }
    popFac.querySelector('.lp-pop__titel').textContent = f.titel;
    popFac.querySelector('.lp-pop__tekst').textContent = f.tekst;
    var chips = popFac.querySelector('.lp-pop__chips');
    chips.textContent = '';
    (f.chips || []).forEach(function (t) { chips.appendChild(maak('li', null, t)); });
    var meer = popFac.querySelector('.lp-pop__meer');
    meer.setAttribute('href', f.link);
    meer.setAttribute('aria-label', 'Meer over ' + f.titel.toLowerCase() + ' op asteria.nl');
    return true;
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest) return;
    var kk = e.target.closest('[data-kamer]');
    if (kk) { e.preventDefault(); if (vulKamer(kk.getAttribute('data-kamer'))) toonPop(popKamer, kk); return; }
    var fk = e.target.closest('[data-fac]');
    if (fk) { e.preventDefault(); if (vulFac(fk.getAttribute('data-fac'), fk)) toonPop(popFac, fk); }
  });

  /* ── faciliteiten: "Laad meer" toont de verborgen tegels en verdwijnt ── */
  var laadMeer = document.querySelector('.b6a-laadmeer');
  var tegels = Array.prototype.slice.call(document.querySelectorAll('.b6a-tegel'));
  var mobiel = window.matchMedia('(max-width: 719px)');
  var facOpen = false;
  /* op de telefoon staan alleen de eerste twee tegels open (zoals de Parkhotel-landers); Laad meer toont de rest */
  function facStand() {
    tegels.forEach(function (t, i) {
      var extra = t.classList.contains('b6a-extra');
      var verberg = !facOpen && (extra || (mobiel.matches && i >= 2));
      if (verberg) t.setAttribute('hidden', ''); else t.removeAttribute('hidden');
    });
    if (laadMeer) laadMeer.parentElement.hidden = facOpen;
  }
  if (laadMeer) {
    laadMeer.addEventListener('click', function () {
      facOpen = true; laadMeer.setAttribute('aria-expanded', 'true'); facStand();
      var eerste = tegels.filter(function (t) { return t.offsetParent !== null; })[2];
      if (eerste && mobiel.matches) eerste.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
  facStand();
  if (mobiel.addEventListener) mobiel.addEventListener('change', facStand); else if (mobiel.addListener) mobiel.addListener(facStand);

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
