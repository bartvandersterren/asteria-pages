/* Hotel Asteria, pre-arrival upsell-lander /extras (visit.asteria.nl). Vanilla, geen frameworks.
   Port van parkhotel-site src/gedrag/pagina-extras-v2.js (pagina-gedrag letterlijk: staatsmodel, kaartHtml, iconen,
   data-act-handler, genoteerd() met data-als/data-stap) plus het kop-, drawer-, cookie- en Mews-poortgedrag uit
   lander-w1.js (lander-w1.js zelf laadt hier niet: die verwacht kamerslider en reviewmuur).

   Link uit de mail (alleen r is verplicht):
     /extras?r=<Mews-GUID>&n=<nummer>&a=<YYYY-MM-DD>&d=<YYYY-MM-DD>&p=<personen>&v=<voornaam>&e=<e-mail>&k=<key>&t=<kamertype>
   1. Hero en slot worden meteen uit de link gevuld (datums met vaste NL-tabellen, niet Intl), daarna overschreven met
      wat GET /api/extras/sessie teruggeeft.
   2. De kaarten worden uit products[] gebouwd, in drie groepen op p.groep (aankomst | verblijf | vertrek). Staat per
      product: {aan, n, avonden (Set van ISO-datums), tijd}. Beginstaat: niets gekozen.
      Producttypes: eenmalig, personen (stepper; eenheid persoon of fiets), perdag (stepper + dagchips uit nights_list;
      dagLabel avond|dag) en pernacht (stepper voor personen, x alle nachten; het ontbijt).
   3. Zijkaart Jouw keuze, balk en bestelbox tonen steeds hetzelfde totaal (een bron: totaal()).
   4. POST /api/extras/bestel met client extras-v2; bij 200 de staat Genoteerd, die aanbod en bestelbox vervangt.
      Bij 400 met fields de melding + de kaart markeren.
   Geen smooth scroll: alle scrollIntoView-aanroepen springen direct. */
(function(){
  'use strict';

  /* ================================================================ kop, drawer, cookie, Mews-poort (uit lander-w1.js) */
  var MEWS_CONFIG = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
  var MEWS_SRC = 'https://app.mews.com/distributor/distributor.min.js';
  var root = document.documentElement;

  /* hoogte van de sticky kop → --kop-h (voor de meelopende zijkaart en de ankers) */
  var kop = document.querySelector('.top-stack');
  function meetKop() { if (kop) root.style.setProperty('--kop-h', kop.offsetHeight + 'px'); }
  meetKop();
  window.addEventListener('resize', meetKop);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(meetKop);

  /* Mews-poort: de widget wordt pas geladen bij de eerste klik op .mews-open (Boek nu in kop en voet) */
  var mewsLaden = false;
  function laadMews() {
    if (mewsLaden) return;
    mewsLaden = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = MEWS_SRC;
    s.onload = function () {
      if (!window.Mews || !window.Mews.Distributor) return;
      window.Mews.Distributor({ configurationIds: [MEWS_CONFIG] }, function (api) {
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
    var href = knop.getAttribute('href');
    sluitDrawer();
    function open() {
      var api = window.mewsApi;
      if (api.setLanguageCode) api.setLanguageCode('nl-NL');
      api.open();
    }
    if (window.mewsApi) { open(); return; }
    window._mewsPending = open;
    laadMews();
    setTimeout(function () {
      if (window._mewsPending) { window._mewsPending = null; window.open(href, '_blank', 'noopener'); }
    }, 4000);
  });

  /* mobiele drawer */
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
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') sluitDrawer(); });

  /* cookiemelding (zoals welkom) */
  var banner = document.getElementById('cookieBanner');
  var akkoord = document.getElementById('cookieAccept');
  if (banner) {
    try { if (!localStorage.getItem('cookie-consent')) banner.classList.add('show'); } catch (e) { banner.classList.add('show'); }
    if (akkoord) akkoord.addEventListener('click', function () {
      try { localStorage.setItem('cookie-consent', '1'); } catch (e) {}
      banner.classList.remove('show');
    });
  }

  /* ================================================================ pagina-gedrag (pagina-extras-v2.js) */
  var T = JSON.parse(document.getElementById('extrasTeksten').textContent);
  var q = new URLSearchParams(location.search);
  var GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
  var ISO = /^(\d{4})-(\d{2})-(\d{2})$/;
  function par(k, max){ return (q.get(k) || '').trim().slice(0, max || 80); }
  var ctx = { r: par('r', 40).toLowerCase(), n: par('n', 20), a: par('a', 10), d: par('d', 10), p: par('p', 2),
              v: par('v', 60), e: par('e', 200), k: par('k', 20).toLowerCase(), t: par('t', 60) };

  /* ---------------------------------------------------------------- vaste tabellen */
  /* fallback zolang de API geen groep/type/dagLabel/eenheid meestuurt */
  var VOLG = ['diner', 'ontbijt', 'wellness', 'fiets', 'ebike', 'kruidenolie', 'badjas', 'handdoek', 'early', 'late'];
  var GROEP = { diner:'verblijf', ontbijt:'verblijf', wellness:'verblijf', fiets:'verblijf', ebike:'verblijf', kruidenolie:'verblijf',
                badjas:'aankomst', handdoek:'aankomst', early:'aankomst', late:'vertrek' };
  var TYPE = { diner:'perdag', ontbijt:'pernacht', wellness:'perdag', fiets:'personen', ebike:'personen', kruidenolie:'eenmalig',
               badjas:'personen', handdoek:'personen', early:'eenmalig', late:'eenmalig' };
  var DAGLABEL = { diner:'avond', wellness:'dag' };
  var EENHEID = { fiets:'fiets', ebike:'fiets' };
  var MAX = { diner:8, ontbijt:8, wellness:8, fiets:8, ebike:8, kruidenolie:3, badjas:8, handdoek:8, early:1, late:1 };
  var GROEPEN = ['aankomst', 'verblijf', 'vertrek'];
  var DAG_K = ['zo', 'ma', 'di', 'wo', 'do', 'vr', 'za'];
  var DAG_L = ['zondag', 'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag'];
  var MND_K = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
  var MND_L = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december'];

  /* ---------------------------------------------------------------- hulpjes */
  function $(s, r){ return (r || document).querySelector(s); }
  function $$(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; }); }
  function euro(c){ return '€ ' + (Math.round(c) / 100).toFixed(2).replace('.', ','); }
  function datum(iso){ var m = ISO.exec(iso || ''); if (!m) return null; var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3])); return isNaN(d) ? null : d; }
  function isoVan(d){ return d.toISOString().slice(0, 10); }
  function labelKort(iso, metJaar){ var d = datum(iso); if (!d) return ''; return DAG_K[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MND_K[d.getUTCMonth()] + (metJaar ? ' ' + d.getUTCFullYear() : ''); }
  function labelLang(iso){ var d = datum(iso); if (!d) return ''; return DAG_L[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MND_L[d.getUTCMonth()]; }
  function nachtenLijst(a, d){
    var da = datum(a), dd = datum(d), uit = [];
    if (!da || !dd) return uit;
    var n = Math.round((dd - da) / 86400000);
    if (n < 1 || n > 30) return uit;
    for (var i = 0; i < n; i++) { var x = new Date(da.getTime() + i * 86400000), s = isoVan(x); uit.push({ date: s, label: labelKort(s, true), short: labelKort(s, false) }); }
    return uit;
  }
  function meervoud(n, een, veel){ return n + ' ' + (n === 1 ? een : veel); }
  function keyUitNaam(naam){
    var s = String(naam || '').toLowerCase();
    if (/elektrische|e-?bike/.test(s)) return 'ebike';
    var kandidaten = ['diner', 'ontbijt', 'wellness', 'fiets', 'kruidenolie', 'badjas', 'handdoek', 'early', 'late'];
    for (var i = 0; i < kandidaten.length; i++) if (s.indexOf(kandidaten[i]) !== -1) return kandidaten[i];
    return '';
  }
  function zetTekst(el, t){ if (el) el.textContent = t; }

  /* ---------------------------------------------------------------- staat */
  var res = { adults: Math.min(8, Math.max(1, parseInt(ctx.p, 10) || 2)), nights_list: nachtenLijst(ctx.a, ctx.d), arrival: ISO.test(ctx.a) ? ctx.a : '', number: ctx.n, first_name: ctx.v };
  var producten = [], perKey = {}, staat = {}, bezig = false;

  function nachten(){ return res.nights_list.length || res.nights || 1; }
  function avondenVan(k){ var s = staat[k]; return s && s.avonden ? s.avonden.size : 0; }
  function kaartTotaal(k){
    var p = perKey[k], s = staat[k];
    if (p.type === 'eenmalig') return p.price_cents;
    if (p.type === 'personen') return p.price_cents * s.n;
    if (p.type === 'pernacht') return p.price_cents * s.n * nachten();
    /* niet gekozen: toon wat Voeg toe oplevert (alle nachten) */
    var av = res.nights_list.length ? (s.aan ? Math.max(1, avondenVan(k)) : res.nights_list.length) : nachten();
    return p.price_cents * s.n * av;
  }
  function gekozen(){ return producten.filter(function(p){ return staat[p.key].aan; }).map(function(p){ return p.key; }); }
  function totaal(){ return gekozen().reduce(function(t, k){ return t + kaartTotaal(k); }, 0); }
  function avondIsos(k){ var s = staat[k]; return res.nights_list.filter(function(n){ return s.avonden.has(n.date); }).map(function(n){ return n.date; }); }
  function opsomming(ls){ return ls.length < 2 ? (ls[0] || '') : ls.slice(0, -1).join(', ') + ' ' + T.en + ' ' + ls[ls.length - 1]; }
  function korteLabels(isos){ return isos.map(function(iso){ var n = res.nights_list.filter(function(x){ return x.date === iso; })[0]; return (n && n.short) || labelKort(iso, false); }); }
  function tijdTekst(t){ return t && t !== 'geen' ? String(t).replace(':', '.') + ' ' + T.uur : ''; }
  function isFiets(p){ return p.eenheid === 'fiets'; }
  function dagWoord(p, n){ return p.dagLabel === 'dag' ? meervoud(n, T.dag, T.dagen) : meervoud(n, T.avond, T.avonden); }

  /* Regeltekst per product, gedeeld door zijkaart, bestelbox en Genoteerd.
     n = aantal (personen/fietsen), dagLbls = korte datumlabels (perdag), dagen = aantal dagen,
     tijd = voorkeurstijd (alleen diner). Geeft {regel, kort, sub, aantal}. */
  function regelTekst(p, n, dagLbls, dagen, tijd){
    var x = { regel: p.name, kort: p.name + ' ' + (p.type === 'eenmalig' ? 1 : n) + '×', sub: '', aantal: (p.type === 'eenmalig' ? 1 : n) + '×' };
    if (p.type === 'personen' && isFiets(p)) {
      /* Fietshuur 2 fietsen (eenmalig per fiets) */
      x.kort = p.name + ' ' + meervoud(n, T.fiets, T.fietsen);
      x.aantal = meervoud(n, T.fiets, T.fietsen);
    } else if (p.type === 'perdag') {
      var delen = [meervoud(n, T.persoon, T.personen)];
      if (dagLbls.length) delen.push(opsomming(dagLbls));
      if (tijdTekst(tijd)) delen.push(tijdTekst(tijd));
      x.sub = delen.join(', ');
      x.kort = p.name + ' ' + n + ' ' + T.pers + ' × ' + dagWoord(p, dagen);
    } else if (p.type === 'pernacht') {
      /* Ontbijtbuffet, subregel: 2 personen, 2 nachten */
      x.sub = meervoud(n, T.persoon, T.personen) + ', ' + meervoud(dagen, T.nacht, T.nachten);
      x.kort = p.name + ' ' + n + ' ' + T.pers + ' × ' + meervoud(dagen, T.nacht, T.nachten);
    }
    return x;
  }

  function regelInfo(k){
    var p = perKey[k], s = staat[k], x;
    if (p.type === 'perdag') {
      var dagen = res.nights_list.length ? avondenVan(k) : nachten();
      x = regelTekst(p, s.n, res.nights_list.length ? korteLabels(avondIsos(k)) : [], dagen, k === 'diner' ? s.tijd : '');
    } else {
      x = regelTekst(p, s.n, [], nachten(), '');
    }
    return { k: k, naam: p.name, regel: x.regel, aantal: x.aantal, sub: x.sub, kort: x.kort, bedrag: euro(kaartTotaal(k)) };
  }

  /* ---------------------------------------------------------------- iconen */
  var IC_KRUIS_D = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  var IC_MIN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/></svg>';
  var IC_PLUS = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14M12 5v14"/></svg>';
  var IC_VINK = '<svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>';
  /* groepsicoon op het vlak als er geen foto is (16:10, zodat de kaartrij niet verspringt) */
  var IC_GROEP = {
    aankomst: '<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 17h16M5 17a7 7 0 0 1 14 0M12 10V8M10.5 8h3M3 20h18"/></svg>',
    verblijf: '<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 19v-9M21 19v-5a3 3 0 0 0-3-3h-8v6M3 17h18M6.5 13.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/></svg>',
    vertrek: '<svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="7" width="14" height="12" rx="1"/><path d="M9 7V5h6v2M9 11v4M15 11v4M7 19v1.5M17 19v1.5"/></svg>'
  };
  var IC_KLOK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>';

  /* ---------------------------------------------------------------- kaarten bouwen (beide staten in de markup) */
  function kaartHtml(p){
    var k = p.key, stepper = p.type !== 'eenmalig';
    var eenheid = p.type === 'eenmalig' ? T.eenmalig
      : p.type === 'pernacht' ? T.ppnacht
      : p.type === 'perdag' ? (isFiets(p) ? T.pfdag : (p.dagLabel === 'dag' ? T.ppdag : T.ppavond))
      : (isFiets(p) ? T.perfiets : T.perpersoon);
    var avond = '';
    if (p.type === 'perdag' && res.nights_list.length) {
      avond = '<div class="xv-kaart__avond"><span class="xv-kaart__avondlabel">' + esc(p.dagLabel === 'dag' ? T.welkedag : T.welkeavond) + '</span><div class="xv-chips">'
        + res.nights_list.map(function(n){ return '<button type="button" class="xv-chip" data-act="avond" data-avond="' + esc(n.date) + '" aria-pressed="false">' + esc(n.short || labelKort(n.date, false)) + '</button>'; }).join('')
        + '</div></div>';
    }
    /* aan-staat op de plek van de knop: [stepper] Toegevoegd [x]; eenmalig zonder stepper */
    var aan = '<div class="xv-kaart__aan">'
      + (stepper ? '<span class="xv-stepper" role="group" aria-label="' + esc(isFiets(p) ? T.aantalfietsen : T.aantal) + '"><button type="button" data-act="dec" aria-label="' + esc(T.minder) + '">' + IC_MIN + '</button><b data-aantal>' + staat[k].n + '</b><button type="button" data-act="inc" aria-label="' + esc(T.meer) + '">' + IC_PLUS + '</button></span>' : '')
      + '<span class="xv-kaart__toeg">' + IC_VINK + ' ' + esc(T.toegevoegd) + '</span>'
      + '<button type="button" class="xv-kaart__weg" data-act="remove" aria-label="' + esc(T.toegevoegd + ', ' + T.verwijder) + '">' + IC_KRUIS_D + '</button></div>';
    return '<article class="xv-kaart xv-kaart--' + esc(k) + '" data-kaart="' + esc(k) + '" data-type="' + esc(p.type) + '">'
      + '<div class="xv-kaart__foto' + (p.image_url ? '' : ' is-leeg') + '">' + (p.image_url ? '<img src="' + esc(p.image_url) + '" alt="' + esc(p.name) + '" width="640" height="400" loading="lazy" decoding="async">' : '')
      + '<span class="xv-kaart__icoon">' + (IC_GROEP[p.groep] || IC_GROEP.verblijf) + '</span></div>'
      + '<div class="xv-kaart__body"><h4 class="xv-kaart__naam">' + esc(p.name) + '</h4>'
      + (p.description ? '<p class="xv-kaart__regel">' + esc(p.description) + '</p>' : '')
      + (p.tijd_overleg ? '<p class="xv-kaart__noot">' + IC_KLOK + '<span>' + esc(T.tijdoverleg) + '</span></p>' : '')
      + avond
      + '<p class="xv-kaart__prijs"><span class="xv-bedrag">' + euro(p.price_cents) + '</span> <small>' + esc(eenheid) + '</small></p>'
      + '<div class="xv-kaart__voet">'
      + '<span class="xv-kaart__staat" data-staat="uit"><button type="button" class="btn btn-primary knop knop--vol xv-kaart__voeg" data-act="add">' + esc(T.voegtoe) + '</button></span>'
      + '<span class="xv-kaart__staat" data-staat="aan" hidden>' + aan + '</span></div></div>'
      + '</article>';
  }

  function bouwKaarten(){
    GROEPEN.forEach(function(g){
      var lijst = producten.filter(function(p){ return p.groep === g; });
      var raster = $('[data-raster="' + g + '"]');
      raster.innerHTML = lijst.map(kaartHtml).join('');
      $('[data-groep="' + g + '"]').hidden = !lijst.length;
    });
  }

  /* ---------------------------------------------------------------- tekenen */
  function toonKaarten(){
    $$('.xv-kaart[data-kaart]').forEach(function(card){
      var k = card.getAttribute('data-kaart'), s = staat[k]; if (!s) return;
      card.classList.toggle('is-on', s.aan);
      $$('[data-staat]', card).forEach(function(e){ e.hidden = (e.getAttribute('data-staat') === 'aan') !== s.aan; });
      $$('[data-aantal]', card).forEach(function(e){ e.textContent = s.n; });
      $$('[data-act="avond"]', card).forEach(function(ch){
        var on = s.aan && s.avonden.has(ch.getAttribute('data-avond'));
        ch.classList.toggle('xv-chip--aan', on); ch.setAttribute('aria-pressed', String(on));
      });
    });
    var tijd = staat.diner ? staat.diner.tijd : 'geen';
    $$('[data-act="tijd"]').forEach(function(ch){
      var on = (ch.getAttribute('data-tijd') || 'geen') === tijd;
      ch.classList.toggle('xv-chip--aan', on); ch.setAttribute('aria-pressed', String(on));
    });
  }

  function toonSom(){
    var ks = gekozen(), rs = ks.map(regelInfo), n = rs.length, tot = euro(totaal());
    var aantalTekst = n + ' ' + (n === 1 ? T.extra : T.extras);
    var kolom = $('[data-sum="kolom"]');
    kolom.innerHTML = rs.length
      ? rs.map(function(r){ return '<li><span>' + esc(r.kort) + '</span><span class="xv-bedrag">' + esc(r.bedrag) + '</span></li>'; }).join('')
      : '<li class="is-leeg">' + esc(T.niets) + '</li>';
    var bestel = $('[data-sum="bestel"]');
    bestel.innerHTML = rs.length
      ? rs.map(function(r){
          return '<li class="xv-bestel__regel"><span class="xv-bestel__naam"><b>' + esc(r.regel) + '</b>' + (r.sub ? '<small>' + esc(r.sub) + '</small>' : '') + '</span>'
            + '<span class="xv-bestel__aantal">' + esc(r.aantal) + '</span><span class="xv-bedrag">' + esc(r.bedrag) + '</span>'
            + '<button type="button" class="xv-bestel__weg" data-act="remove" data-kaart="' + esc(r.k) + '" aria-label="' + esc(T.verwijder + ': ' + r.naam) + '">' + IC_KRUIS_D + '</button></li>';
        }).join('')
      : '<li class="xv-bestel__regel is-leeg">' + esc(T.niets) + '</li>';
    $$('[data-sum-aantal]').forEach(function(e){ e.textContent = aantalTekst; });
    $$('[data-sum-totaal]').forEach(function(e){ e.textContent = tot; });
    zetTekst($('[data-sum-balk]'), aantalTekst + ' · ' + tot);
    zetTekst($('[data-sum-balksub]'), n ? T.balkvol : T.balkleeg);
    $$('#xvAanbod [data-als]').forEach(function(e){
      e.hidden = !e.getAttribute('data-als').split(',').some(function(k){ return staat[k] && staat[k].aan; });
    });
  }

  function herteken(){ toonKaarten(); toonSom(); }

  /* ---------------------------------------------------------------- hero en slot uit de link / de sessie */
  function vulHero(){
    var heeftData = !!(res.arrival_label || res.arrival);
    var kaart = $('#xvKaart');
    zetTekst($('[data-veld="aankomst"]'), res.arrival_label || labelKort(res.arrival, true));
    zetTekst($('[data-veld="vertrek"]'), res.departure_label || labelKort(res.departure || (ISO.test(ctx.d) ? ctx.d : ''), true));
    zetTekst($('[data-veld="gasten"]'), meervoud(res.adults, T.persoon, T.personen));
    var regel = $('[data-veld="regel"]'), delen = [];
    if (ctx.t) delen.push(ctx.t);
    if (res.number) delen.push(T.resnr.replace('[nummer]', res.number));
    regel.textContent = delen.join(' · ');
    regel.hidden = !delen.length;
    kaart.hidden = !heeftData;
    $('.xv-hero').classList.toggle('xv-hero--zonder-kaart', !heeftData);
    var naam = res.first_name || ctx.v;
    zetTekst($('#xvWelkom'), naam ? T.regelnaam.replace('[naam]', naam) : T.regel);
    var lang = labelLang(res.arrival);
    zetTekst($('#xvSlotKop'), lang ? T.slotkop.replace('[datum]', lang) : T.slotkopleeg);
    zetTekst($('#xvKlaarSlot'), lang ? T.verheugdatum.replace('[datum]', lang) : T.verheug);
  }

  /* ---------------------------------------------------------------- foutstaten */
  function geenLink(){
    $('#xvKaart').hidden = true;
    $('.xv-hero').classList.add('xv-hero--zonder-kaart');
    zetTekst($('#xvWelkom'), T.geenlink);
    $('#xvAanbod').hidden = true;
    zetTekst($('#xvSlotKop'), T.slotkopleeg);
  }
  function laadFout(msg){
    var m = $('#xvMelding'); m.textContent = msg || T.laadfout; m.hidden = false;
    $$('.xv-groep').forEach(function(g){ g.hidden = true; });
    $('#bevestig').hidden = true; $('#xvZij').hidden = true; balk(false);
  }
  function balk(aan){
    $('#xvBalk').hidden = !aan;
    document.body.classList.toggle('heeft-balk', !!aan);
    root.classList.toggle('heeft-balk', !!aan);
  }

  /* ---------------------------------------------------------------- start */
  if (!GUID.test(ctx.r)) { geenLink(); return; }
  vulHero();
  var emailVeld = $('#xvEmail');
  if (ctx.e) emailVeld.value = ctx.e;
  $('#xvT0').value = String(Date.now());
  try { if (localStorage.getItem('asteria-extras-' + ctx.r)) $('#xvAlEerder').hidden = false; } catch (e) {}

  var qs = ['r', 'n', 'a', 'd', 'p', 'v', 'k'].map(function(k){ return k + '=' + encodeURIComponent(ctx[k]); }).join('&') + '&taal=' + encodeURIComponent(T.taal || 'nl') + '&client=extras-v2';
  fetch('/api/extras/sessie?' + qs, { headers: { Accept: 'application/json' } })
    .then(function(r){ return r.json(); })
    .then(function(data){
      if (!data || !data.ok) { laadFout((data && data.message) || T.laadfout); return; }
      var rv = data.reservation || {};
      if (rv.adults) res.adults = rv.adults;
      if (rv.nights) res.nights = rv.nights;
      if (Array.isArray(rv.nights_list) && rv.nights_list.length) res.nights_list = rv.nights_list;
      if (rv.arrival) res.arrival = rv.arrival;
      if (rv.departure) res.departure = rv.departure;
      if (rv.arrival_label) res.arrival_label = rv.arrival_label;
      if (rv.departure_label) res.departure_label = rv.departure_label;
      if (rv.first_name) res.first_name = rv.first_name;
      if (rv.number) res.number = rv.number;
      vulHero();
      var ruw = data.products || [];
      var metGroep = ruw.length > 0 && ruw.every(function(p){ return GROEPEN.indexOf(p.groep) !== -1; });
      producten = ruw.map(function(p){
        var k = p.key || keyUitNaam(p.name);
        var type = p.type || TYPE[k] || 'eenmalig';
        var dagLabel = p.dagLabel || DAGLABEL[k] || 'avond', eenheid = p.eenheid || EENHEID[k] || 'persoon';
        var groep = GROEPEN.indexOf(p.groep) !== -1 ? p.groep : (GROEP[k] || 'verblijf');
        var max = parseInt(p.max, 10) || MAX[k] || (type === 'eenmalig' ? 1 : 8);
        var std = parseInt(p.default_count, 10);
        if (!std) std = (type === 'eenmalig') ? 1 : res.adults;
        return { id: p.id, key: k, type: type, dagLabel: type === 'perdag' ? dagLabel : '', eenheid: type === 'eenmalig' ? '' : eenheid, groep: groep,
                 max: max, default_count: Math.max(1, Math.min(max, std)), price_cents: p.price_cents, name: p.name, description: p.description, image_url: p.image_url, tijd_overleg: !!p.tijd_overleg };
      }).filter(function(p){ return p.key && p.id && typeof p.price_cents === 'number'; });
      /* met groep uit de API: API-volgorde; anders de vaste volgorde (onbekende keys achteraan) */
      function volg(k){ var i = VOLG.indexOf(k); return i === -1 ? VOLG.length : i; }
      if (!metGroep) producten.sort(function(x, y){ return volg(x.key) - volg(y.key); });
      if (!producten.length) { laadFout(T.laadfout); return; }
      producten.forEach(function(p){ perKey[p.key] = p; staat[p.key] = { aan: false, n: p.default_count, avonden: new Set(), tijd: 'geen' }; });
      $('#xvMelding').hidden = true;
      bouwKaarten();
      $('#bevestig').hidden = false; $('#xvZij').hidden = false; balk(true);
      herteken();
      var aanbevolen = data.recommended || ctx.k;
      var kaart = aanbevolen && $('.xv-kaart[data-kaart="' + aanbevolen + '"]');
      if (kaart) {
        kaart.classList.add('is-aanbevolen');
        setTimeout(function(){ kaart.scrollIntoView({ block: 'center' }); }, 60);
      }
    })
    .catch(function(){ laadFout(T.laadfout); });

  /* foto die niet laadt: dan toch het vlak met het groepsicoon */
  document.addEventListener('error', function(ev){
    var img = ev.target;
    if (img && img.tagName === 'IMG' && img.parentNode && img.parentNode.classList && img.parentNode.classList.contains('xv-kaart__foto')) {
      img.parentNode.classList.add('is-leeg'); img.parentNode.removeChild(img);
    }
  }, true);

  /* ---------------------------------------------------------------- klikken */
  document.addEventListener('click', function(ev){
    var t = ev.target && ev.target.closest ? ev.target.closest('[data-act]') : null;
    if (!t) return;
    var act = t.getAttribute('data-act');
    if (act === 'tijd') { if (staat.diner) { staat.diner.tijd = t.getAttribute('data-tijd') || 'geen'; herteken(); } return; }
    var card = t.closest('[data-kaart]'), k = card ? card.getAttribute('data-kaart') : t.getAttribute('data-kaart');
    if (!k || !staat[k]) return;
    ev.preventDefault();
    var s = staat[k], p = perKey[k];
    var c = $('.xv-kaart[data-kaart="' + k + '"]'); if (c) c.classList.remove('is-fout');
    if (act === 'add') {
      s.aan = true;
      if (p.type === 'perdag') s.avonden = new Set(res.nights_list.map(function(n){ return n.date; }));
    } else if (act === 'remove') {
      s.aan = false; s.n = p.default_count;
    } else if (act === 'inc') {
      s.n = Math.min(p.max, s.n + 1);
    } else if (act === 'dec') {
      if (s.n <= 1) { s.aan = false; s.n = p.default_count; } else { s.n -= 1; }
    } else if (act === 'avond') {
      var a = t.getAttribute('data-avond');
      if (!s.aan) { s.aan = true; s.avonden = new Set([a]); }
      else if (s.avonden.has(a)) { s.avonden.delete(a); if (!s.avonden.size) { s.aan = false; } }
      else { s.avonden.add(a); }
    }
    herteken();
  });

  /* ---------------------------------------------------------------- bestellen */
  var melding = $('#xvBestelMelding'), knop = $('#xvBestelKnop');
  $('#xvForm').addEventListener('submit', function(ev){
    ev.preventDefault();
    if (bezig) return;
    var ks = gekozen();
    if (!ks.length) { melding.textContent = T.kiesiets; return; }
    var email = emailVeld.value.trim();
    if (!/^[^\s@,;:<>"]+@[^\s@,;:<>"]+\.[A-Za-z]{2,}$/.test(email)) { melding.textContent = T.emailfout; emailVeld.focus(); return; }
    var regels = ks.map(function(k){
      var p = perKey[k], s = staat[k], r = { product_id: p.id, count: p.type === 'eenmalig' ? 1 : s.n };
      if (p.type === 'perdag') {
        if (res.nights_list.length) r.avonden = avondIsos(k); /* veld heet ook bij dagen avonden */
        if (k === 'diner' && s.tijd && s.tijd !== 'geen') r.tijd = s.tijd;
      }
      return r;
    });
    var lokaal = ks.map(function(k){ var i = regelInfo(k); return { key: k, naam: i.regel, sub: i.sub || i.aantal, total_cents: kaartTotaal(k), avonden: perKey[k].type === 'perdag' ? avondIsos(k) : undefined }; });
    var lokaalTotaal = totaal();
    var body = { client: 'extras-v2', r: ctx.r, n: ctx.n, a: ctx.a, d: ctx.d, p: ctx.p, v: ctx.v, e: email, k: ctx.k, taal: T.taal || 'nl',
      regels: regels, opmerking: $('#xvOpmerking').value, website: $('#xvWebsite').value, t0: $('#xvT0').value };
    bezig = true; knop.disabled = true; melding.textContent = T.bezig;
    fetch('/api/extras/bestel', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body) })
      .then(function(r){ return r.json().catch(function(){ return null; }).then(function(j){ return { s: r.status, j: j }; }); })
      .then(function(x){
        bezig = false; knop.disabled = false;
        if (x.s === 200 && x.j && x.j.ok) { genoteerd(x.j, lokaal, lokaalTotaal); return; }
        if (x.s === 400 && x.j) {
          var velden = Array.isArray(x.j.fields) ? x.j.fields : [];
          if (velden.indexOf('e') !== -1 || velden.indexOf('email') !== -1) { melding.textContent = T.emailfout; emailVeld.focus(); return; }
          melding.textContent = x.j.message || T.verstuurfout;
          var p = x.j.product_id && producten.filter(function(pp){ return pp.id === String(x.j.product_id).toLowerCase(); })[0];
          var c = p && $('.xv-kaart[data-kaart="' + p.key + '"]');
          if (c) { c.classList.add('is-fout'); c.scrollIntoView({ block: 'center' }); }
          return;
        }
        melding.textContent = (x.j && x.j.message) || T.verstuurfout;
      })
      .catch(function(){ bezig = false; knop.disabled = false; melding.textContent = T.verstuurfout; });
  });

  /* ---------------------------------------------------------------- genoteerd */
  function genoteerd(j, lokaal, lokaalTotaal){
    try { localStorage.setItem('asteria-extras-' + ctx.r, String(Date.now())); } catch (e) {}
    var regels;
    if (Array.isArray(j.regels) && j.regels.length) {
      regels = j.regels.map(function(r){
        var p = producten.filter(function(pp){ return pp.id === String(r.product_id || '').toLowerCase() || (r.key && pp.key === r.key); })[0] || {};
        var k = r.key || p.key;
        var pp = p.type ? p : { name: p.name || '', type: TYPE[k] || 'eenmalig', dagLabel: DAGLABEL[k] || 'avond', eenheid: EENHEID[k] || 'persoon' };
        var n = r.personen || r.count || 1, x;
        if (pp.type === 'perdag') {
          var lbl = Array.isArray(r.avonden) && r.avonden.length ? korteLabels(r.avonden) : (Array.isArray(r.avond_labels) ? r.avond_labels : []);
          x = regelTekst(pp, n, lbl, lbl.length || nachten(), r.tijd || '');
        } else {
          x = regelTekst(pp, n, [], r.nachten || nachten(), '');
        }
        return { key: k, naam: x.regel, sub: x.sub || x.aantal, total_cents: typeof r.total_cents === 'number' ? r.total_cents : 0, avonden: r.avonden };
      });
    } else {
      regels = lokaal;
    }
    /* de API zet regels met een afwijking voorop (voor de Zap); de gast ziet de volgorde van de kaarten */
    function plek(k){ for (var i = 0; i < producten.length; i++) if (producten[i].key === k) return i; return producten.length; }
    regels.sort(function(x, y){ return plek(x.key) - plek(y.key); });
    var tot = typeof j.total_cents === 'number' ? j.total_cents : lokaalTotaal;
    $('[data-sum="klaar"]').innerHTML = regels.map(function(r){
      return '<li><span>' + esc(r.naam) + '<small>' + esc(r.sub) + '</small></span><span class="xv-bedrag">' + euro(r.total_cents) + '</span></li>';
    }).join('');
    zetTekst($('#xvKlaarTotaal'), euro(tot));
    $('#xvKlaarReceptie').hidden = !j.fallback;
    /* zonder bevestigingsmail (geen Resend) geen mail beloven */
    if (j.mail_sent === false && T.klaartekstzondermail) zetTekst($('#xvKlaarTekst'), T.klaartekstzondermail);
    /* Wat gebeurt er nu: alleen de stappen van wat gekozen is */
    var ks = regels.map(function(r){ return r.key; });
    function heeft(k){ return ks.indexOf(k) !== -1; }
    function dagenTekst(key){
      var dr = regels.filter(function(r){ return r.key === key; })[0];
      var isos = (dr && Array.isArray(dr.avonden) && dr.avonden.length) ? dr.avonden : (staat[key] ? avondIsos(key) : []);
      if (!isos.length) isos = res.nights_list.map(function(n){ return n.date; });
      var ls = isos.map(labelLang).filter(Boolean);
      return ls.length < 2 ? (ls[0] || '') : ls.slice(0, -1).join(', ') + ' ' + T.en + ' ' + ls[ls.length - 1];
    }
    var kamer = $('[data-stap="kamer"]');
    kamer.textContent = heeft('badjas') && heeft('handdoek') ? T.nubeide : (heeft('badjas') ? T.nubadjas : T.nuhanddoek);
    kamer.hidden = !(heeft('badjas') || heeft('handdoek'));
    var diner = $('[data-stap="diner"]');
    diner.textContent = T.nudiner.replace('[avonden]', heeft('diner') ? dagenTekst('diner') : '').replace(/ voor \.$/, '.');
    diner.hidden = !heeft('diner');
    var wellness = $('[data-stap="wellness"]');
    wellness.textContent = T.nuwellness.replace('[dagen]', heeft('wellness') ? dagenTekst('wellness') : '').replace(/ op  en /, ' en ');
    wellness.hidden = !heeft('wellness');
    /* stappen met data-als (kruidenolie, early, ontbijt, fiets/ebike, late): zichtbaar als een van de keys gekozen is */
    $$('.xv-klaar__stappen li[data-als]').forEach(function(li){
      li.hidden = !li.getAttribute('data-als').split(',').some(heeft);
    });
    var zichtbaar = $$('.xv-klaar__stappen li').filter(function(li){ li.classList.remove('is-laatste'); return !li.hidden; });
    if (zichtbaar.length) zichtbaar[zichtbaar.length - 1].classList.add('is-laatste');
    $('.xv-klaar__nu').hidden = !zichtbaar.length;
    /* staat wisselen: aanbod en bestelbox weg, Genoteerd erin */
    $('#xvAanbod').hidden = true; balk(false);
    var klaar = $('#xvKlaar'); klaar.hidden = false;
    melding.textContent = '';
    klaar.scrollIntoView({ block: 'start' }); try { klaar.focus({ preventScroll: true }); } catch (e) {}
  }

  /* Nog iets toevoegen: terug naar het aanbod, met een lege keuze en de melding dat er al besteld is */
  $('#xvNogIets').addEventListener('click', function(ev){
    ev.preventDefault();
    producten.forEach(function(p){ staat[p.key] = { aan: false, n: p.default_count, avonden: new Set(), tijd: 'geen' }; });
    $('#xvOpmerking').value = '';
    $('#xvT0').value = String(Date.now());
    $('#xvAlEerder').hidden = false;
    $('#xvKlaar').hidden = true; $('#xvAanbod').hidden = false; balk(true);
    herteken();
    $('#extras').scrollIntoView({ block: 'start' });
  });
})();
