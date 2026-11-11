/* GEDRAG bij het sjabloon route.template.html (/fietsen-rond-venray-v2, /wandelen-rond-venray-v2, + -de/-en).
   PORT van parkhotel-site src/gedrag/pagina-routes-v3.js (zie de uitleg daar), prefix ro- -> rt-. Gedrag ongewijzigd:

   1  HET LENGTEFILTER: de chips boven het routeraster (3b) en de filterbalk .rt-filt in de kaart (4c) zijn EEN filterstand.
      Verbergt routekaartjes, lijstrijen en routes op de kaart; ?lengte=kort|gemiddeld|lang in de URL (replaceState), bij
      het laden uitgelezen. Telling "3 van 10 routes · filter Kort" + Wissen. Zonder script staat alles open, filterbalk verborgen.
   2  DE KAART: komt het blok in beeld (IntersectionObserver, 400 px vooruit), dan haalt het script de ondergrond
      (data-geo, content/kaart/getekend.json) en bouwt window.AsteriaKaart (kaart-getekend.js) de getekende kaart met de
      routes uit het inline JSON (#rt-kaart-routes); de stilstaande kaartfoto gaat weg. Nummer of lijn tikken, of een rij
      klikken = die route uitgelicht, rij is-actief, strook .rt-voet onderin (foto, nummer, naam, afstand · duur · start,
      Bekijk = pop-up, kruisje). Nog eens dezelfde, kruisje, Escape of de overzichtsknop = terug naar het overzicht.
      Aanwijzen licht alleen op. Zonder hover scrolt een klik op een rij de kaart in beeld. Gebieden zonder lijn (eigen
      wandelgebieden met lijn null) krijgen een speld op het startpunt (nummerknop .rt-speld). Vangnet: de kaartfoto blijft.
   3  DE FOTOSLIDER in het arrangementblok (fiets): pijlen (rondlopend), bolletjes, bijhouden bij vegen. Geen autoplay.
   4  DE POP-UP PER ROUTE (#rtPop; onder 1024 px een blad van onderen, alleen CSS): inhoud uit het kaartje (kaartfoto +
      lus-kaartje + span.rt-extra's als beeldenstrook met naamsvermelding, nummer, naam, feiten, startregel, knooppunten,
      tekst, externe link, Maps-link). Open via foto, naam of Meer over deze route, Bekijk in de strook, of #route-<slug>
      (laden + hashchange). Openen zet #route-<slug> (replaceState), sluiten haalt hem weg. Kruisje, klik ernaast, Escape;
      Tab blijft in het venster, focus naar de kop en terug naar de opener; pijltjestoetsen bladeren; vegen op de strook.
      Toon op de kaart = sluiten en de route op de kaart kiezen.
   Geen localStorage, geen externe scripts. */
(function () {
  'use strict';
  var elk = function (lijst, fn) { Array.prototype.forEach.call(lijst, fn); };
  var zacht = !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var root = document.documentElement;

  /* ---- 1 het lengtefilter */
  var URLNAAM = { kort: 'kort', middel: 'gemiddeld', lang: 'lang' };
  var filterNu = 'alle';
  var chips = document.querySelectorAll('.rt-routes .rt-chip[data-filter]'),
      balk = document.querySelector('.rt-kaart .rt-filt'),
      balkKnoppen = balk ? balk.querySelectorAll('.rt-filt__knop[data-filter]') : [],
      kaartjes = document.querySelectorAll('.rt-routes .rt-kaartje[data-lengte]'),
      live = document.querySelector('.rt-filt__live');
  var tel = function (n, f) {
    if (!live) return;
    var woord = function (x) { return x === 1 ? live.getAttribute('data-woord-1') : live.getAttribute('data-woord'); };
    var tot = kaartjes.length, b = document.createElement('b');
    live.innerHTML = '';
    if (f === 'alle') { b.textContent = tot + ' ' + woord(tot); live.appendChild(b); return; }
    b.textContent = n + ' ' + (live.getAttribute('data-van') || '') + ' ' + tot + ' ' + woord(tot);
    live.appendChild(b);
    var knop = balk ? balk.querySelector('.rt-filt__knop[data-filter="' + f + '"] b') : null;
    if (knop) live.appendChild(document.createTextNode(' · ' + (live.getAttribute('data-filter') || '') + ' ' + knop.textContent.trim()));
  };
  var lengteVanSlug = function (slug) { var k = document.getElementById('rt-' + slug); return k ? k.getAttribute('data-lengte') : ''; };
  var past = function (slug) { return filterNu === 'alle' || lengteVanSlug(slug) === filterNu; };
  var zetUrl = function (f) {
    if (!window.history || !history.replaceState) return;
    var q = location.search.replace(/^\?/, '').split('&').filter(function (d) { return d && d.split('=')[0] !== 'lengte'; });
    if (f !== 'alle') q.push('lengte=' + URLNAAM[f]);
    try { history.replaceState(history.state, '', location.pathname + (q.length ? '?' + q.join('&') : '') + location.hash); } catch (e) {}
  };
  function zetFilter(f, stil, anker) {
    if (f !== 'kort' && f !== 'middel' && f !== 'lang') f = 'alle';
    /* het filter verbergt kaartjes boven de kaart; het aangeklikte element blijft op dezelfde plek staan */
    var ankerTop = anker && anker.getBoundingClientRect ? anker.getBoundingClientRect().top : null;
    filterNu = f;
    elk(chips, function (c) { var aan = c.getAttribute('data-filter') === f; c.classList.toggle('is-aan', aan); c.setAttribute('aria-pressed', aan ? 'true' : 'false'); });
    elk(balkKnoppen, function (c) { var aan = c.getAttribute('data-filter') === f; c.classList.toggle('is-aan', aan); c.setAttribute('aria-pressed', aan ? 'true' : 'false'); });
    var n = 0;
    elk(kaartjes, function (k) { var ja = f === 'alle' || k.getAttribute('data-lengte') === f; k.hidden = !ja; if (ja) n++; });
    elk(document.querySelectorAll('.rt-kaart .rt-rij[data-slug]'), function (r) {
      var li = r.parentNode && r.parentNode.tagName === 'LI' ? r.parentNode : r;
      li.hidden = !past(r.getAttribute('data-slug'));
    });
    var kb = document.querySelector('.rt-kaart');
    if (kb && kb.pasFilterToe) kb.pasFilterToe(f);
    if (balk) balk.classList.toggle('is-actief', f !== 'alle');
    tel(n, f);
    if (!stil) zetUrl(f);
    if (ankerTop !== null && document.contains(anker)) {
      var verschil = anker.getBoundingClientRect().top - ankerTop;
      if (Math.abs(verschil) > 1) window.scrollTo(window.pageXOffset, window.pageYOffset + verschil);
    }
  }
  elk(chips, function (chip) { chip.addEventListener('click', function () { zetFilter(chip.getAttribute('data-filter'), false, chip); }); });
  elk(balkKnoppen, function (k) {
    k.addEventListener('click', function () { var f = k.getAttribute('data-filter'); zetFilter(f === filterNu ? 'alle' : f, false, k); });
  });
  var wissen = balk ? balk.querySelector('.rt-filt__wissen') : null;
  if (wissen) wissen.addEventListener('click', function () {
    zetFilter('alle', false, balk);
    if (balkKnoppen[0]) try { balkKnoppen[0].focus({ preventScroll: true }); } catch (e) { balkKnoppen[0].focus(); }
  });
  if (balk) { balk.hidden = false; tel(kaartjes.length, 'alle'); }

  /* ---- 2 de kaart */
  var kaart = document.querySelector('.rt-kaart');
  var kaartApi = null, kaartActief = null, openPop = function () { return false; };
  if (kaart) {
    var beeld = kaart.querySelector('[data-kaart]'),
        voet = kaart.querySelector('.rt-voet'),
        rijen = kaart.querySelectorAll('.rt-rij[data-slug]');
    var zweven = !!(window.matchMedia && window.matchMedia('(hover: hover)').matches);
    var rijVan = function (slug) { return kaart.querySelector('.rt-rij[data-slug="' + slug + '"]'); };
    var voetSlug = null, PAD = { tl: [24, 24], br: [64, 28] }, PAD_ONDER = 28;
    var vulVoet = function (slug) {
      var rij = rijVan(slug);
      if (!voet || !rij) return false;
      var txt = function (el) { return el ? el.textContent.replace(/\s+/g, ' ').trim() : ''; };
      var img = rij.querySelector('.rt-rij__mini img'), tijd = rij.querySelectorAll('.rt-rij__tijd span');
      var km = txt(rij.querySelector('.rt-rij__km')), duur = txt(tijd[0]);
      var kj = document.getElementById('rt-' + slug), start = txt(kj ? kj.querySelector('.rt-start') : null);
      var foto = voet.querySelector('.rt-voet__foto'), fi = foto.querySelector('img');
      if (!fi) { fi = document.createElement('img'); fi.alt = ''; fi.width = 84; fi.height = 84; fi.decoding = 'async'; foto.appendChild(fi); }
      if (img) fi.src = img.currentSrc || img.src;
      voet.querySelector('.rt-stip').textContent = txt(rij.querySelector('.rt-stip'));
      voet.querySelector('.rt-voet__naam').textContent = txt(rij.querySelector('.rt-rij__tk b'));
      var kort = [km, duur].filter(Boolean).join(' · ');
      voet.querySelector('.rt-voet__lang').textContent = [kort, start].filter(Boolean).join(' · ');
      voet.querySelector('.rt-voet__kort').textContent = kort;
      return true;
    };
    var voetOpen = function (slug) {
      if (!voet || !vulVoet(slug)) return;
      voetSlug = slug;
      voet.classList.add('is-open');
      voet.removeAttribute('aria-hidden');
      if (beeld) beeld.classList.add('heeft-voet');
    };
    var voetDicht = function () {
      if (!voet) return;
      var hadFocus = voet.contains(document.activeElement), slug = voetSlug;
      voetSlug = null;
      voet.classList.remove('is-open');
      voet.setAttribute('aria-hidden', 'true');
      if (beeld) beeld.classList.remove('heeft-voet');
      if (hadFocus && slug) { var r = rijVan(slug); if (r) { try { r.focus({ preventScroll: true }); } catch (e) { r.focus(); } } }
    };
    var zetPad = function () {
      PAD.br[1] = voetSlug && voet ? voet.offsetHeight + (parseFloat(getComputedStyle(voet).bottom) || 0) + 8 : PAD_ONDER;
    };
    var markeer = function (slug) { elk(rijen, function (r) { r.classList.toggle('is-actief', r.getAttribute('data-slug') === slug); }); };
    var naarOverzicht = function () {
      kaartActief = null;
      markeer(null);
      voetDicht();
      zetPad();
      kaartApi.setActiveRoute(null);
      kaartApi.overzicht(true);
    };
    var kies = function (slug) {
      if (!kaartApi) return false;
      if (slug === kaartActief) { naarOverzicht(); return true; }
      kaartActief = slug;
      markeer(slug);
      voetOpen(slug);
      zetPad();
      kaartApi.focusRouteAnim(slug);
      return true;
    };
    var pasFilterToe = function () {
      if (!kaartApi) return;
      kaartApi.zetZichtbaar(function (r) { return past(r.slug); });
      if (kaartActief && !past(kaartActief)) { kaartActief = null; kaartApi.setActiveRoute(null); voetDicht(); }
      zetPad();
      markeer(kaartActief);
      if (kaartActief) kaartApi.focusRouteAnim(kaartActief); else kaartApi.overzicht(true);
    };
    kaart.pasFilterToe = function () { pasFilterToe(); };
    kaart.sluitVoet = function () { if (kaartApi) naarOverzicht(); else voetDicht(); };
    var wachtend = null, stilMuis = false;
    var muisBeweegt = function (e) {
      if (!e.movementX && !e.movementY) return;
      stilMuis = false; document.removeEventListener('mousemove', muisBeweegt);
    };
    kaart.toonRoute = function (slug) {
      if (zweven && !stilMuis) { stilMuis = true; document.addEventListener('mousemove', muisBeweegt); }
      if (beeld && beeld.scrollIntoView) beeld.scrollIntoView({ behavior: zacht ? 'smooth' : 'auto', block: 'center' });
      if (kaartApi) { if (kaartActief !== slug) kies(slug); return; }
      wachtend = slug;
      markeer(slug);
    };
    elk(rijen, function (rij) {
      var slug = rij.getAttribute('data-slug');
      var licht = function (e) { if (e && e.type === 'mouseenter' && stilMuis) return; if (kaartApi) kaartApi.setActiveRoute(slug); };
      var terug = function () { if (kaartApi) kaartApi.setActiveRoute(kaartActief); };
      if (zweven) { rij.addEventListener('mouseenter', licht); rij.addEventListener('mouseleave', terug); }
      rij.addEventListener('focus', licht);
      rij.addEventListener('blur', terug);
      rij.addEventListener('click', function (e) {
        if (!kaartApi) return; // nog geen kaart: de link gaat naar het routekaartje
        e.preventDefault();
        kies(slug);
        if (!zweven && beeld.scrollIntoView) beeld.scrollIntoView({ behavior: zacht ? 'smooth' : 'auto', block: 'center' });
      });
    });
    var gebouwd = false;
    var bouw = function () {
      if (gebouwd) return;
      gebouwd = true;
      var geoUrl = beeld && beeld.getAttribute('data-geo'), bron = beeld && document.querySelector(beeld.getAttribute('data-routes'));
      if (!geoUrl || !bron || !window.AsteriaKaart || !window.fetch || !window.Promise) return;
      var data;
      try { data = JSON.parse(bron.textContent); } catch (e) { return; }
      if (voet) {
        voet.querySelector('.rt-voet__bekijk').addEventListener('click', function (e) { if (voetSlug) openPop(voetSlug, e.currentTarget); });
        voet.querySelector('.rt-voet__sluit').addEventListener('click', function () { if (kaartApi) naarOverzicht(); else voetDicht(); });
      }
      fetch(geoUrl).then(function (r) { if (!r.ok) throw new Error(geoUrl + ' ' + r.status); return r.json(); }).then(function (geo) {
        elk(beeld.querySelectorAll('.rt-kaart__grond'), function (el) { el.remove(); });
        beeld.classList.add('is-interactief');
        var smal = beeld.clientWidth < 600;
        PAD.tl = [smal ? 16 : 24, smal ? 16 : 24]; PAD.br = [smal ? 60 : 64, smal ? 24 : 28]; PAD_ONDER = PAD.br[1];
        var kt = function (k) { return beeld.getAttribute('data-t-' + k) || ''; };
        kaartApi = window.AsteriaKaart.maak(beeld, {
          geo: geo,
          hotel: { lat: data.hotel[0], lng: data.hotel[1], naam: beeld.getAttribute('data-hotel') || 'Hotel Asteria' },
          vignet: beeld.getAttribute('data-vignet'),
          padding: PAD,
          teksten: { in: kt('in'), uit: kt('uit'), alles: kt('alles'), wiel: kt('wiel'), vingers: kt('vingers'), attributie: kt('attributie') },
          onRoute: kies,
          onOverzicht: naarOverzicht
        });
        if (voet) beeld.appendChild(voet); // boven de kaart
        kaartApi.zetRoutes(data.routes);
        /* gebieden zonder lijn: de nummerknop wordt een speld op het startpunt */
        var speld = {};
        data.routes.forEach(function (r) { if (r.speld) speld[String(r.nr)] = true; });
        elk(beeld.querySelectorAll('.gk-pins > .routebadge'), function (b) {
          if (speld[b.textContent.trim()]) { b.classList.add('rt-speld'); b.innerHTML = '<span>' + b.textContent + '</span>'; }
        });
        kaartApi.zetZichtbaar(function (r) { return past(r.slug); });
        kaartApi.overzicht(false);
        beeld.setAttribute('data-gebouwd', '1');
        if (wachtend) { var w = wachtend; wachtend = null; kies(w); }
      }).catch(function (err) {
        if (window.console) console.warn('routekaart: blijft stilstaand', err);
      });
    };
    if (beeld && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (items) {
        if (items.some(function (i) { return i.isIntersecting; })) { io.disconnect(); bouw(); }
      }, { rootMargin: '400px 0px' });
      io.observe(beeld);
    } else if (beeld) bouw();
  }

  /* Escape sluit de strook en zet de kaart terug op het overzicht (de pop-up vangt Escape zelf als hij open is) */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' && e.key !== 'Esc') return;
    var p = document.getElementById('rtPop');
    if (p && p.classList.contains('is-open')) return;
    var v = document.querySelector('.rt-kaart .rt-voet.is-open'), kb = document.querySelector('.rt-kaart');
    if (v && kb && kb.sluitVoet) { e.preventDefault(); kb.sluitVoet(); }
  });

  /* ---- 1b de beginstand uit de URL, na de kaart zodat die meefiltert */
  (function () {
    var m = /[?&]lengte=([a-z]+)/.exec(location.search || '');
    var f = m ? { kort: 'kort', gemiddeld: 'middel', middel: 'middel', lang: 'lang' }[m[1]] : null;
    if (f) zetFilter(f, true);
  })();

  /* ---- 4 de pop-up per route */
  var pop = document.getElementById('rtPop');
  var popVenster = pop ? pop.querySelector('.rt-pop') : null;
  var popOpener = null, popSlug = null, popIdx = 0, popLen = 0, popBeelden = [];
  function popCredit(b) {
    var p = pop.querySelector('.rt-pop__credit');
    if (!p) return;
    p.hidden = !popBeelden.some(function (x) { return x.credit; });
    p.classList.toggle('is-leeg', !(b && b.credit));
    if (!b || !b.credit) return;
    var naam = p.querySelector('.rt-pop__credit-naam'), lic = p.querySelector('.rt-pop__credit-lic');
    naam.textContent = b.credit; naam.href = b.creditUrl || '#';
    if (!b.creditUrl) naam.removeAttribute('target'); else naam.target = '_blank';
    lic.textContent = '';
    if (b.licUrl) {
      var a = document.createElement('a');
      a.href = b.licUrl; a.rel = 'noopener'; a.target = '_blank'; a.textContent = b.lic;
      lic.appendChild(a);
    } else lic.textContent = b.lic || '';
  }
  function popGa(i) {
    if (!popLen) return;
    popIdx = (i + popLen) % popLen;
    pop.querySelector('.rt-pop__track').style.transform = 'translateX(-' + (popIdx * 100) + '%)';
    var imgs = pop.querySelectorAll('.rt-pop__beeld');
    [popIdx + 1, popIdx - 1].forEach(function (j) { var el = imgs[(j + popLen) % popLen]; if (el) el.loading = 'eager'; });
    popCredit(popBeelden[popIdx]);
    elk(pop.querySelectorAll('.rt-pop__dot'), function (d, j) {
      d.classList.toggle('is-aan', j === popIdx);
      if (j === popIdx) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current');
    });
  }
  function popFocusbaar() {
    return [].filter.call(popVenster.querySelectorAll('a[href], button, [tabindex]:not([tabindex="-1"])'), function (el) {
      return el.offsetParent !== null || el === document.activeElement;
    });
  }
  function popZetHash(slug) {
    if (!window.history || !history.replaceState) return;
    try { history.replaceState(history.state, '', location.pathname + location.search + (slug ? '#route-' + slug : '')); } catch (e) {}
  }
  openPop = function (slug, opener) {
    var k = document.getElementById('rt-' + slug);
    if (!pop || !k || !k.hasAttribute('data-slug')) return false;
    var naam = k.querySelector('.rt-kaartje__naam'), nr = k.querySelector('.rt-nr'), img = k.querySelector('.rt-kaartje__beeld img');
    var extern = k.querySelector('.rt-acties a.rt-extern'), maps = k.querySelector('.rt-acties a.rt-plan');
    var titel = naam ? naam.textContent.trim() : '';
    function credit(el, b) {
      b.credit = el.getAttribute('data-credit') || '';
      b.creditUrl = el.getAttribute('data-credit-url') || '';
      b.lic = el.getAttribute('data-licentie') || '';
      b.licUrl = el.getAttribute('data-licentie-url') || '';
      return b;
    }
    var beelden = [];
    var foto = k.getAttribute('data-foto') || (img ? img.getAttribute('src') : '');
    if (foto) beelden.push(credit(k, { src: foto, alt: img ? img.getAttribute('alt') : titel, lus: false }));
    var lus = k.getAttribute('data-lus');
    if (lus) beelden.push({ src: lus, alt: (pop.getAttribute('data-lus-alt') || '') + ': ' + titel, lus: true });
    elk(k.querySelectorAll('.rt-extra[data-foto]'), function (x) {
      beelden.push(credit(x, { src: x.getAttribute('data-foto'), alt: x.getAttribute('data-alt') || titel, lus: false, extra: true }));
    });
    popBeelden = beelden;
    var track = pop.querySelector('.rt-pop__track'), dots = pop.querySelector('.rt-pop__dots');
    track.innerHTML = ''; dots.innerHTML = '';
    beelden.forEach(function (b, i) {
      var el = document.createElement('img');
      el.className = 'rt-pop__beeld' + (b.lus ? ' rt-pop__beeld--lus' : '');
      if (b.extra) el.loading = 'lazy';
      el.src = b.src; el.alt = b.alt || ''; el.decoding = 'async';
      el.width = b.lus ? 800 : 1000; el.height = b.lus ? 600 : 667;
      track.appendChild(el);
      var d = document.createElement('button');
      d.type = 'button'; d.className = 'rt-pop__dot';
      d.setAttribute('aria-label', (pop.getAttribute('data-beeld') || '') + ' ' + (i + 1));
      d.addEventListener('click', function () { popGa(i); });
      dots.appendChild(d);
    });
    popLen = beelden.length;
    pop.querySelector('.rt-pop__strook').classList.toggle('is-enkel', popLen < 2);
    popGa(0);
    pop.querySelector('.rt-pop__vorm').textContent = k.getAttribute('data-vorm') || '';
    pop.querySelector('.rt-pop__naam .rt-stip').textContent = nr ? nr.textContent : '';
    pop.querySelector('.rt-pop__titel').textContent = titel;
    var feiten = pop.querySelector('.rt-pop__feiten');
    feiten.innerHTML = '';
    elk(k.querySelectorAll('.rt-stat, .rt-start, .rt-knoop'), function (el) { feiten.appendChild(el.cloneNode(true)); });
    pop.querySelector('.rt-pop__tekst').textContent = k.getAttribute('data-tekst') || '';
    var cta = pop.querySelector('.rt-pop__cta'), pm = pop.querySelector('.rt-pop__maps');
    cta.hidden = !extern;
    if (extern) { cta.href = extern.href; cta.textContent = (extern.firstChild && extern.firstChild.nodeType === 3 ? extern.firstChild.nodeValue : extern.textContent).trim(); }
    pm.hidden = !maps; if (maps) pm.href = maps.href;
    popSlug = slug;
    popOpener = opener || (document.activeElement !== document.body ? document.activeElement : null);
    pop.classList.add('is-open');
    pop.removeAttribute('aria-hidden');
    root.classList.add('rt-pop-open');
    document.body.style.overflow = 'hidden';
    pop.querySelector('.rt-pop__body').scrollTop = 0;
    popZetHash(slug);
    var kop = pop.querySelector('.rt-pop__naam');
    try { kop.focus({ preventScroll: true }); } catch (e) { kop.focus(); }
    return true;
  };
  function sluitPop(focusTerug) {
    if (!pop || !pop.classList.contains('is-open')) return;
    pop.classList.remove('is-open');
    pop.setAttribute('aria-hidden', 'true');
    root.classList.remove('rt-pop-open');
    document.body.style.overflow = '';
    popZetHash(null);
    var o = popOpener; popOpener = null; popSlug = null;
    if (focusTerug !== false && o && o.focus && document.contains(o)) { try { o.focus({ preventScroll: true }); } catch (e) { o.focus(); } }
  }
  if (pop && popVenster) {
    pop.setAttribute('aria-hidden', 'true');
    pop.addEventListener('click', function (e) { if (e.target === pop) sluitPop(); });
    pop.querySelector('.rt-pop__sluit').addEventListener('click', function () { sluitPop(); });
    elk(pop.querySelectorAll('.rt-pop__pijl'), function (b) {
      b.addEventListener('click', function () { popGa(popIdx + Number(b.getAttribute('data-stap'))); });
    });
    var strook = pop.querySelector('.rt-pop__strook'), x0 = 0;
    strook.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    strook.addEventListener('touchend', function (e) { var v = x0 - e.changedTouches[0].clientX; if (Math.abs(v) > 40) popGa(popIdx + (v > 0 ? 1 : -1)); });
    pop.querySelector('.rt-pop__toon').addEventListener('click', function () {
      var slug = popSlug;
      sluitPop(false);
      var kb = document.querySelector('.rt-kaart');
      if (kb && kb.toonRoute && slug) {
        kb.toonRoute(slug);
        var rij = kb.querySelector('.rt-rij[data-slug="' + slug + '"]');
        if (rij) { try { rij.focus({ preventScroll: true }); } catch (e) {} }
      }
    });
    document.addEventListener('keydown', function (e) {
      if (!pop.classList.contains('is-open')) return;
      if (e.key === 'Escape' || e.key === 'Esc') { e.preventDefault(); sluitPop(); return; }
      var opKnop = /^(A|BUTTON)$/.test((document.activeElement || {}).tagName || '');
      if (e.key === 'ArrowLeft' && popLen > 1 && !opKnop) popGa(popIdx - 1);
      if (e.key === 'ArrowRight' && popLen > 1 && !opKnop) popGa(popIdx + 1);
      if (e.key !== 'Tab') return;
      var f = popFocusbaar();
      if (!f.length) { e.preventDefault(); return; }
      var eerste = f[0], laatste = f[f.length - 1], nu = document.activeElement;
      if (!popVenster.contains(nu)) { e.preventDefault(); eerste.focus(); }
      else if (e.shiftKey && (nu === eerste || nu === pop.querySelector('.rt-pop__naam'))) { e.preventDefault(); laatste.focus(); }
      else if (!e.shiftKey && nu === laatste) { e.preventDefault(); eerste.focus(); }
    });
    elk(document.querySelectorAll('.rt-routes .rt-kaartje[data-slug]'), function (k) {
      var slug = k.getAttribute('data-slug');
      elk(k.querySelectorAll('[data-pop]'), function (el) {
        el.addEventListener('click', function (e) { if (e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); openPop(slug, el); });
      });
      var bl = k.querySelector('.rt-kaartje__beeld');
      if (bl) bl.addEventListener('click', function () { openPop(slug, k.querySelector('.rt-meer') || null); });
    });
    var vanHash = function () {
      var m = /^#route-([a-z0-9-]+)$/.exec(location.hash || '');
      if (m && m[1] !== popSlug) openPop(m[1], null);
    };
    window.addEventListener('hashchange', vanHash);
    vanHash();
  }

  /* ---- 3 de fotoslider */
  elk(document.querySelectorAll('.rt [data-fotoslider]'), function (fs) {
    var spoor = fs.querySelector('[data-fs-spoor]');
    if (!spoor) return;
    var n = spoor.children.length, bollen = fs.querySelectorAll('[data-fs-naar]');
    function nu() { var b = spoor.clientWidth || 1; return Math.max(0, Math.min(n - 1, Math.round(spoor.scrollLeft / b))); }
    function naar(i) { i = (i + n) % n; spoor.scrollTo({ left: i * spoor.clientWidth, behavior: zacht ? 'smooth' : 'auto' }); }
    function bij() {
      var i = nu();
      elk(bollen, function (b, j) { b.classList.toggle('is-aan', j === i); if (j === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    }
    var wacht = false;
    spoor.addEventListener('scroll', function () { if (wacht) return; wacht = true; window.requestAnimationFrame(function () { wacht = false; bij(); }); }, { passive: true });
    elk(fs.querySelectorAll('[data-fs-stap]'), function (b) { b.addEventListener('click', function () { naar(nu() + Number(b.getAttribute('data-fs-stap'))); }); });
    elk(bollen, function (b) { b.addEventListener('click', function () { naar(Number(b.getAttribute('data-fs-naar'))); }); });
    bij();
  });
})();
