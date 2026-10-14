/* Prijskalender "Kies je nachten" op de arrangementpagina's (lander-w1, build-blok 'arrangement'; dialoog #ar-kal).
   Port van de Parkhotel-bouwsteen blok-kalender-prijs (parkhotel-site src/gedrag/blok-kalender-prijs.js) in Asteria-stijl.
   - Prijzen uit /api/arr-kalender (functions/api/arr-kalender.js): per getoonde maand vier delen naast elkaar; elk deel
     tekent zichzelf; mislukt een deel, dan nog eens na 1,5 s en na 4 s, daarna storingsdagen (geen prijs, wel kiesbaar;
     Mews zegt bij het boeken alsnog of het kan). Cel = EUR ceil(prijs_cent / 100 / 2).
   - Zondag goud (ark-dag--zondag), met de lagere prijs (uit Mews, of berekend door de API zolang Mews geen zondagtarief heeft).
   - Normaal: aankomst A en vertrek B kiezen (hover toont de reeks); vertrekken mag op een grijze dag.
     Vaste nachten (data-nachten > 1, Limburg/Weekend): één klik = aankomst, vertrek = A + N; alleen aankomst_mag-dagen.
   - Kamertype = data-room van de aangeklikte knop, anders data-kamer-standaard (de inbegrepen kamer).
   - Openen (capture op window, vóór lander-w1.js): elke .mews-open met data-voucher = de code, en de datumvelden en
     de knop van de boekbalken (form[data-boekbalk]). Cmd/ctrl/shift-klik laten we met rust.
   - Bevestigen: datums in de boekbalk van de hero; zonder kamer form.requestSubmit() (de bestaande widgetflow van
     lander-w1.js + arrangement.js), met kamer een tijdelijke .mews-open met data-room en een href met mewsStart/mewsEnd
     (fallback-tabblad van lander-w1.js) en de datums vooraf op de widget-API. lander-w1.js blijft ongewijzigd.
   - Bureaublad (>= 1024): zwevende kaart naast de knop, twee maanden, niet-modaal. Telefoon: bottom sheet, een maand,
     modaal (showModal). Bereik: vandaag t/m 18 maanden vooruit. */
(function () {
  'use strict';
  var pop = document.getElementById('ar-kal');
  if (!pop) return;
  var D = pop.dataset;
  var CODE = (D.code || '').toUpperCase();
  if (!CODE) return;
  var NACHTEN = parseInt(D.nachten, 10) || 1, VAST = NACHTEN > 1;
  var AANKOMSTDAGEN = (D.aankomstdagen || '').split(',').filter(Boolean).map(Number);
  var STD = (D.kamerStandaard || '').toLowerCase(), ZONDAG = D.zondag === 'ja';
  var KAMERS = {};
  try { KAMERS = JSON.parse(D.kamers || '{}'); } catch (e) { KAMERS = {}; }
  var MEWS_URL = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
  var kanModal = typeof pop.showModal === 'function';

  function pd(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec((s || '').trim()); return m ? new Date(+m[1], m[2] - 1, +m[3]) : null; }
  function twee(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(d) { return d.getFullYear() + '-' + twee(d.getMonth() + 1) + '-' + twee(d.getDate()); }
  function plus(d, n) { return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n); }
  var nu = new Date(), START = new Date(nu.getFullYear(), nu.getMonth(), nu.getDate());
  var TOT = new Date(START.getFullYear(), START.getMonth() + 18, START.getDate());
  var LAATSTE_VERTREK = plus(TOT, NACHTEN);
  var MND = [], md = new Date(START.getFullYear(), START.getMonth(), 1);
  while (md <= LAATSTE_VERTREK) { MND.push(md); md = new Date(md.getFullYear(), md.getMonth() + 1, 1); }

  /* ── prijzen ophalen ── */
  var DAG = {}, MAAND = {}, HERKANSING = [1500, 4000], KAMER = STD;
  function mkey(d) { return d.getFullYear() + '-' + twee(d.getMonth() + 1); }
  function wacht(ms) { return new Promise(function (k) { setTimeout(k, ms); }); }
  function deelOpStoring(s, deel) {
    var j = +s.slice(0, 4), m = +s.slice(5) - 1, laatste = new Date(j, m + 1, 0).getDate();
    var van = (deel - 1) * 8 + 1, tot = deel === 4 ? laatste : Math.min(deel * 8, laatste);
    for (var g = van; g <= tot; g++) {
      var k = s + '-' + twee(g);
      if (!DAG[k]) DAG[k] = { datum: k, beschikbaar: false, storing: true, aankomst_mag: magDag(pd(k)) };
    }
  }
  function haalDeel(s, deel, poging) {
    return fetch('/api/arr-kalender?code=' + encodeURIComponent(CODE) + '&maand=' + s + '&deel=' + deel, { headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) { var f = new Error('kalender ' + r.status); f.blijvend = r.status < 500; throw f; } return r.json(); })
      .then(function (d) {
        if (!d || !d.ok || !d.dagen) throw new Error('kalender antwoord');
        for (var i = 0; i < d.dagen.length; i++) DAG[d.dagen[i].datum] = d.dagen[i];
        klaar(s);
      })
      .catch(function (e) {
        if (!(e && e.blijvend) && poging < HERKANSING.length) return wacht(HERKANSING[poging]).then(function () { return haalDeel(s, deel, poging + 1); });
        deelOpStoring(s, deel); klaar(s);
      });
  }
  /* hoogstens 4 deelaanvragen tegelijk (een maand); de tweede maand op het bureaublad wacht tot er plek is. Elke
     deelaanvraag doet bij Mews zelf hoogstens 2 calls tegelijk, dus nooit meer dan 8 tegelijk bij een koude cache. */
  var rij = [], bezig = 0;
  function volgende() {
    while (bezig < 4 && rij.length) {
      var t = rij.shift(); bezig++;
      haalDeel(t[0], t[1], 0).then(function () { bezig--; volgende(); });
    }
  }
  function haalMaand(m) { var s = mkey(m); if (MAAND[s]) return; MAAND[s] = 1; [1, 2, 3, 4].forEach(function (deel) { rij.push([s, deel]); }); volgende(); }
  function klaar(s) {
    if (!isOpen) return;
    for (var j = 0; j < aantal; j++) { var m = MND[idx + j]; if (m && mkey(m) === s) { controleer(); verf(); return; } }
  }

  /* ── stand van een dag (als aankomstnacht) voor het huidige kamertype: uit, laden, open of dicht ── */
  function magDag(d) { return !AANKOMSTDAGEN.length || AANKOMSTDAGEN.indexOf(d.getDay()) > -1; }
  function info(d) { return DAG[ymd(d)] || null; }
  function prijsVan(x) { if (!x || !x.beschikbaar || !x.prijzen) return null; return x.prijzen[KAMER] || null; }
  function stand(d) {
    if (d < START || d > TOT) return 'uit';
    if (VAST && !magDag(d)) return 'dicht';
    var x = info(d);
    if (!x) return 'laden';
    if (x.storing || prijsVan(x)) return 'open';
    return 'dicht';
  }
  function nachtOpen(d) { return stand(d) === 'open'; }
  /* een nacht die nog niet binnen is breekt de reeks niet: dat is onbekend, geen "vol" */
  function reeksOpen(a, b) { for (var d = a; d < b; d = plus(d, 1)) { var s = stand(d); if (s !== 'open' && s !== 'laden') return false; } return true; }
  function euro(x) { var p = prijsVan(x); if (!p) return ''; return '€ ' + Math.ceil(p.prijs_cent / 100 / 2 - 1e-9); }
  function controleer() {
    if (A && stand(A) === 'dicht') { A = B = H = null; return; }
    if (!VAST && A && B && !reeksOpen(A, B)) B = null;
  }

  /* ── de kalender ── */
  var fDag = new Intl.DateTimeFormat('nl-NL', { weekday: 'short', day: 'numeric', month: 'short' });
  var fMnd = new Intl.DateTimeFormat('nl-NL', { month: 'long', year: 'numeric' });
  var WDN = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo'];
  var PL = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M10 3 5 8l5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var PR = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var maandenEl = pop.querySelector('.ark-maanden'), watEl = pop.querySelector('.ark-wat'), wisEl = pop.querySelector('.ark-wis');
  var btnEl = pop.querySelector('.ark-btn'), tipEl = pop.querySelector('.ark-tip'), kamerEl = pop.querySelector('.ark-kamer');
  var A = null, B = null, H = null, idx = 0, aantal = 2, isOpen = false, trigger = null, sluitTimer = null;
  var mq = window.matchMedia('(min-width:1024px)');

  function bouw() {
    var h = '', max = Math.max(0, MND.length - aantal);
    if (idx > max) idx = max;
    for (var j = 0; j < aantal && idx + j < MND.length; j++) {
      var m = MND[idx + j], y = m.getFullYear(), mo = m.getMonth(), eerste = j === 0, laatste = j === aantal - 1 || idx + j === MND.length - 1;
      haalMaand(m);
      h += '<div class="ark-maand"><div class="ark-mkop">';
      h += eerste ? '<button type="button" class="ark-pijl" data-r="-1" aria-label="' + D.vorige + '"' + (idx <= 0 ? ' disabled' : '') + '>' + PL + '</button>' : '<span class="ark-leeg"></span>';
      h += '<span class="ark-naam">' + fMnd.format(m) + '</span>';
      h += laatste ? '<button type="button" class="ark-pijl" data-r="1" aria-label="' + D.volgende + '"' + (idx >= max ? ' disabled' : '') + '>' + PR + '</button>' : '<span class="ark-leeg"></span>';
      h += '</div><div class="ark-wdag">' + WDN.map(function (s) { return '<span>' + s + '</span>'; }).join('') + '</div><div class="ark-raster">';
      var off = (new Date(y, mo, 1).getDay() + 6) % 7, n = new Date(y, mo + 1, 0).getDate();
      for (var k = 0; k < off; k++) h += '<span class="ark-d leeg"></span>';
      for (var g = 1; g <= n; g++) {
        var d = new Date(y, mo, g);
        h += '<button type="button" class="ark-d" data-d="' + ymd(d) + '" aria-label="' + fDag.format(d) + '"><span class="n">' + g + '</span><span class="t"></span></button>';
      }
      h += '</div></div>';
    }
    maandenEl.innerHTML = h;
    verf();
  }
  function eindpunt() {
    if (VAST) { if (A) return plus(A, NACHTEN); if (H && nachtOpen(H)) return plus(H, NACHTEN); return null; }
    if (B) return B;
    if (A && H && H > A && reeksOpen(A, H)) return H;
    return null;
  }
  function verf() {
    var E = eindpunt(), begin = VAST ? (A || (H && nachtOpen(H) ? H : null)) : A;
    var cellen = maandenEl.querySelectorAll('.ark-d[data-d]'), vraagGezet = false;
    for (var i = 0; i < cellen.length; i++) {
      var c = cellen[i], d = pd(c.getAttribute('data-d')), st = stand(d), kan = false, lab = '';
      var x = st === 'open' ? info(d) : null, prijs = x ? euro(x) : '';
      if (VAST || !A || B) kan = st === 'open';
      else kan = (d > A && reeksOpen(A, d)) || (d < A && st === 'open');
      var cls = 'ark-d ' + st;
      if (ZONDAG && st === 'open' && x && x.zondag && prijs) cls += ' ark-dag--zondag';
      if (st === 'laden') cls += ' ark-dag--laden';
      if (begin && +d === +begin) { cls += ' sel'; lab = D.aankomst; }
      else if (begin && E && d > begin && d < E) cls += ' sel';
      else if (E && +d === +E) { cls += ' vertrek'; lab = D.vertrek; }
      else if (!VAST && A && !B && d > A && kan) { cls += ' kand'; if (st !== 'open' && !vraagGezet) { lab = D.vertrekVraag; vraagGezet = true; } }
      if (kan) cls += ' kan';
      c.className = cls;
      c.setAttribute('aria-disabled', kan ? 'false' : 'true');
      if ((A && +d === +A) || (B && +d === +B)) c.setAttribute('aria-pressed', 'true'); else c.removeAttribute('aria-pressed');
      var t = c.querySelector('.t');
      if (lab) { t.className = 't'; t.textContent = lab; }
      else if (prijs) { t.className = 't p'; t.textContent = prijs; c.setAttribute('aria-label', fDag.format(d) + ', ' + prijs); }
      else { t.className = 't'; t.textContent = ''; }
    }
    samen();
  }
  function samen() {
    var t = '';
    if (A && B) {
      var n = Math.round((Date.UTC(B.getFullYear(), B.getMonth(), B.getDate()) - Date.UTC(A.getFullYear(), A.getMonth(), A.getDate())) / 864e5);
      t = fDag.format(A) + ' – ' + fDag.format(B) + ' · ' + n + ' ' + (n === 1 ? D.nacht : D.nachtenWoord);
    } else if (A) t = fDag.format(A) + ' – …';
    watEl.textContent = t;
    wisEl.hidden = !A;
    btnEl.disabled = !(A && B);
  }
  maandenEl.addEventListener('click', function (e) {
    var p = e.target.closest('.ark-pijl');
    if (p) { if (!p.disabled) { idx += +p.getAttribute('data-r'); bouw(); plaats(); } return; }
    var c = e.target.closest('.ark-d[data-d]');
    if (!c) return;
    var d = pd(c.getAttribute('data-d'));
    if (VAST) { if (nachtOpen(d)) { A = d; B = plus(d, NACHTEN); H = null; } }
    else if (!A || B) { if (nachtOpen(d)) { A = d; B = null; H = null; } }
    else if (d > A) { if (reeksOpen(A, d)) { B = d; H = null; } }
    else if (d < A && nachtOpen(d)) A = d;
    verf();
  });
  maandenEl.addEventListener('mouseover', function (e) {
    if (VAST ? A : (!A || B)) return;
    var c = e.target.closest('.ark-d[data-d]');
    var d = c ? pd(c.getAttribute('data-d')) : null;
    if (+d !== +H) { H = d; verf(); }
  });
  maandenEl.addEventListener('mouseleave', function () { if (H) { H = null; verf(); } });
  wisEl.addEventListener('click', function () { A = B = H = null; verf(); });
  pop.querySelector('.ark-x').addEventListener('click', function () { sluit(true); });
  btnEl.addEventListener('click', bevestig);

  function kamerNaam() { kamerEl.textContent = KAMERS[KAMER] || KAMERS[STD] || ''; }

  /* ── plaatsen (bureaublad): onder of boven de knop, anders naast de zijkaart, anders midden ── */
  var eerstePlaats = false;
  function kopH() { var k = document.querySelector('.top-stack'); return (k ? k.getBoundingClientRect().bottom : 0) + 12; }
  function plaats() {
    if (!isOpen || !trigger || !mq.matches) return;
    var vw = document.documentElement.clientWidth, vh = window.innerHeight, r = trigger.getBoundingClientRect();
    var w = pop.offsetWidth, h = pop.offsetHeight, gap = 18, x, y, k = '', KOP = kopH();
    if (!r.width && !r.height) {
      x = Math.max(12, (vw - w) / 2); y = Math.max(KOP, (vh - h) / 2); eerstePlaats = false;
      pop.style.left = Math.round(x) + 'px'; pop.style.top = Math.round(y) + 'px'; pop.setAttribute('data-kant', 'midden');
      tipEl.style.top = tipEl.style.left = ''; return;
    }
    var kaart = trigger.closest('.lp-zone-kant');
    if (kaart) {
      var kr = kaart.getBoundingClientRect();
      if (kr.left - gap - w >= 12) {
        k = 'links'; x = kr.left - gap - w; y = r.top + r.height / 2 - (h - 94);
        y = Math.max(KOP, Math.min(y, vh - h - 12));
      }
    }
    if (!k) {
      x = r.left + r.width / 2 - w / 2; x = Math.max(12, Math.min(x, vw - w - 12));
      var onder = vh - r.bottom - gap - 12, boven = r.top - gap - KOP;
      if (onder < h && boven < h && eerstePlaats) {
        var dy = Math.min(h - onder, r.top - KOP);
        if (dy > 0) { window.scrollBy({ top: dy, left: 0, behavior: 'instant' }); r = trigger.getBoundingClientRect(); onder = vh - r.bottom - gap - 12; boven = r.top - gap - KOP; }
      }
      k = (onder >= h || onder >= boven) ? 'onder' : 'boven';
      y = k === 'onder' ? r.bottom + gap : r.top - gap - h;
      y = Math.max(Math.min(KOP, vh - h - 12), Math.min(y, vh - h - 12));
    }
    eerstePlaats = false;
    pop.style.left = Math.round(x) + 'px'; pop.style.top = Math.round(y) + 'px'; pop.setAttribute('data-kant', k);
    tipEl.style.top = tipEl.style.left = '';
    if (k === 'links') tipEl.style.top = Math.round(Math.max(18, Math.min(r.top + r.height / 2 - y - 8, h - 34))) + 'px';
    else tipEl.style.left = Math.round(Math.max(18, Math.min(r.left + r.width / 2 - x - 8, w - 34))) + 'px';
  }
  var raf = 0;
  function herplaats() { if (raf) return; raf = requestAnimationFrame(function () { raf = 0; plaats(); }); }

  function open(el, kamer) {
    if (sluitTimer) { clearTimeout(sluitTimer); sluitTimer = null; }
    trigger = el; isOpen = true;
    var desk = mq.matches; aantal = desk ? 2 : 1;
    var k = (kamer || STD).toLowerCase();
    if (k !== KAMER) { KAMER = k; A = B = H = null; }
    kamerNaam();
    if (A) {
      for (var i = 0; i < MND.length; i++) { if (MND[i].getFullYear() === A.getFullYear() && MND[i].getMonth() === A.getMonth()) { idx = i; break; } }
    }
    bouw(); eerstePlaats = true;
    pop.classList.toggle('ark--sheet', !desk);
    if (desk || !kanModal) { if (!pop.open) pop.show(); }
    else if (!pop.open) pop.showModal();
    document.documentElement.classList.add('ark-open');
    if (!desk) document.documentElement.classList.add('ark-slot');
    plaats();
    void pop.offsetWidth;
    pop.classList.add('toon');
    try { pop.querySelector('.ark-x').focus({ preventScroll: true }); } catch (x) { /* oude browser */ }
  }
  function sluit(focusTerug) {
    if (!isOpen) return;
    isOpen = false; H = null;
    pop.classList.remove('toon');
    document.documentElement.classList.remove('ark-slot', 'ark-open');
    var t = trigger;
    sluitTimer = setTimeout(function () { if (pop.open) pop.close(); sluitTimer = null; }, mq.matches ? 180 : 260);
    if (focusTerug && t && document.contains(t)) { try { t.focus({ preventScroll: true }); } catch (x) { /* niets */ } }
  }
  function isModal() { try { return pop.open && pop.matches(':modal'); } catch (x) { return false; } }
  /* Esc bij showModal: native 'cancel' -> zelf sluiten met animatie */
  pop.addEventListener('cancel', function (e) { e.preventDefault(); sluit(true); });
  /* klik op de achtergrond van de modale sheet */
  pop.addEventListener('click', function (e) { if (e.target === pop && pop.classList.contains('ark--sheet')) sluit(true); });

  /* ── bevestigen ── */
  var hero = document.querySelector('.b1a-balk[data-boekbalk]') || document.querySelector('form[data-boekbalk]');
  function zetDatum(invoer, d) {
    if (!invoer) return;
    invoer.value = ymd(d);
    invoer.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function bevestig() {
    if (!(A && B)) return;
    var el = trigger, a = A, v = B, kamer = (el && el.getAttribute('data-room')) || '';
    var bron = el && el.closest ? el.closest('form[data-boekbalk]') : null;
    var gasten = 2;
    var gs = bron && bron.querySelector('[data-rol="gasten"]');
    if (gs) gasten = parseInt(gs.value, 10) || 2;
    sluit(false);
    if (hero) {
      var ha = hero.querySelector('[data-rol="aankomst"]'), hv = hero.querySelector('[data-rol="vertrek"]'), hg = hero.querySelector('[data-rol="gasten"]');
      zetDatum(ha, a); zetDatum(hv, v);
      if (hg && bron && bron !== hero && String(hg.value) !== String(gasten)) { hg.value = String(gasten); hg.dispatchEvent(new Event('change', { bubbles: true })); }
    }
    window.arKalender = { start: ymd(a), eind: ymd(v), voucher: CODE, kamer: kamer || null, route: kamer ? 'kamer' : 'boekbalk' };
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'arr_kalender_kies', { voucher: CODE, start: ymd(a), nachten: Math.round((v - a) / 864e5), kamer: kamer || '' });
    }
    if (!kamer && hero && typeof hero.requestSubmit === 'function') { hero.requestSubmit(); return; }
    /* met kamer (of zonder requestSubmit): via de Mews-poort van lander-w1.js, met de datums vooraf op de widget */
    var url = MEWS_URL + '?mewsVoucherCode=' + encodeURIComponent(CODE) + '&mewsStart=' + ymd(a) + '&mewsEnd=' + ymd(v)
      + '&mewsAdultCount=' + gasten + (kamer ? '&mewsRoom=' + encodeURIComponent(kamer) + '&mewsRoute=rates' : '');
    function datums() {
      var api = window.mewsApi;
      if (!api) return;
      if (api.setStartDate && api.setEndDate) { api.setStartDate(a); api.setEndDate(v); }
      if (api.setAdultCount) api.setAdultCount(gasten);
    }
    var door = document.createElement('a');
    door.className = 'mews-open';
    door.setAttribute('data-ark-door', '');
    door.setAttribute('data-voucher', CODE);
    if (kamer) door.setAttribute('data-room', kamer);
    door.href = url;
    door.hidden = true;
    document.body.appendChild(door);
    if (window.mewsApi) datums();
    door.click();
    if (window._mewsPending) {
      var wachtend = window._mewsPending;
      window._mewsPending = function () { datums(); wachtend(); };
    }
    setTimeout(function () { if (door.parentNode) door.parentNode.removeChild(door); }, 0);
  }

  /* ── openen ── */
  function isKnop(el) {
    if (!el || pop.contains(el) || el.hasAttribute('data-ark-door')) return false;
    return (el.getAttribute('data-voucher') || '').toUpperCase() === CODE;
  }
  function balkDoel(t) {
    var form = t && t.closest ? t.closest('form[data-boekbalk]') : null;
    if (!form) return null;
    if (t.closest('button[type="submit"]')) return form.querySelector('button[type="submit"]');
    var inv = t.closest('.field--datum');
    return inv ? inv : null;
  }
  function voorbereiden(el) {
    /* knop in een open modale dialoog (kamer-pop-up): die eerst stil dicht, zoals sluitPop(d, true) in lander-w1.js */
    var dlg = el.closest ? el.closest('dialog[open]') : null;
    if (dlg && dlg !== pop) { dlg._stil = true; dlg.close(); }
    /* knop in de menulade (telefoon): lade dicht via de Escape-afhandeling van lander-w1.js */
    var lade = el.closest ? el.closest('.nav-drawer') : null;
    if (lade && lade.classList.contains('is-open')) document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  }
  window.addEventListener('click', function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    var t = e.target;
    var knop = t && t.closest ? t.closest('.mews-open') : null;
    var doel = null, kamer = '';
    if (knop && isKnop(knop)) { doel = knop; kamer = knop.getAttribute('data-room') || ''; }
    else if (!knop) doel = balkDoel(t);
    if (!doel) return;
    e.preventDefault(); e.stopPropagation();
    if (isOpen && trigger === doel) { sluit(true); return; }
    voorbereiden(doel);
    open(doel, kamer);
  }, true);
  /* datumvelden: geen native datumkiezer (focus/toetsen) */
  Array.prototype.forEach.call(document.querySelectorAll('form[data-boekbalk] .field--datum .field__invoer'), function (inv) {
    inv.addEventListener('mousedown', function (e) { e.preventDefault(); });
    inv.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') { e.preventDefault(); open(inv.closest('.field--datum'), ''); }
      else if (e.key !== 'Tab' && e.key !== 'Escape') e.preventDefault();
    });
  });
  document.addEventListener('pointerdown', function (e) {
    if (!isOpen || !mq.matches) return;
    var t = e.target;
    if (pop.contains(t) || (trigger && trigger.contains(t))) return;
    var knop = t.closest ? t.closest('.mews-open') : null;
    if ((knop && isKnop(knop)) || balkDoel(t)) return;
    sluit(false);
  }, true);
  document.addEventListener('keydown', function (e) { if (isOpen && (e.key === 'Escape' || e.key === 'Esc') && !isModal()) { e.preventDefault(); sluit(true); } });
  window.addEventListener('scroll', herplaats, { passive: true });
  window.addEventListener('resize', function () { if (!isOpen) return; if ((aantal === 2) !== mq.matches) { sluit(false); return; } herplaats(); });
})();
