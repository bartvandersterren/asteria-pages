/* ══════════════════════════════════════════════════════════
   NIEUWSBRIEF-POPUP — VARIANT B: SCRATCHCARD (kras & win)
   Zelf-injecterend, meertalig (nl/en/de), Revinate-koppeling
   per taal. Analytics getagd als variant_email = 'B_scratchcard'.
   Wordt geladen door popup-ab.js (A/B-test tegen variant A).
══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── Guards ─────────────────────────────────────────────
  if (document.getElementById('scOverlay') || document.getElementById('ecOverlay')) return;
  if (localStorage.getItem('ec_converted')) return;

  var AB = 'B_scratchcard';
  function track(event) { if (window.track) window.track(event, { variant_email: AB }); }

  // ── Taal ───────────────────────────────────────────────
  var lang = (document.documentElement.getAttribute('lang') || 'nl').slice(0, 2).toLowerCase();
  if (lang !== 'en' && lang !== 'de') lang = 'nl';

  var TOKEN = { nl: '210bb345-899a-4f69-9b9f-4a00624a2024',
                en: 'b7a5ebe6-df0d-4a05-a5b6-3e9274ba9cc6',
                de: '449e7373-329f-4087-8f96-0124d65c69a4' };

  var COPY = {
    nl: {
      closeAria: 'Sluiten',
      heading: 'Probeer je geluk',
      sub: 'Kras het vak open en ontdek wat je wint',
      coverText: 'KRAS HIER',
      prize: 'Gratis welkomstcadeau',
      prizeItems: ['Flesje bubbels op de kamer', 'Badjas &amp; badhanddoeken'],
      claimBtn: 'Claim je cadeau',
      emailHeading: 'Waar mogen we je code naartoe sturen?',
      emailPlaceholder: 'jouw@email.nl',
      emailBtn: 'Stuur mij de code',
      terms: 'Niet in combinatie met arrangementen. Geldig bij je eerste verblijf.',
      consent: 'Door in te schrijven ga je akkoord met ons <a href="/privacyverklaring" target="_blank">privacybeleid</a>. Je kunt je altijd afmelden.',
      errorText: 'Er ging iets mis. Probeer het opnieuw.',
      successHeading: 'Bijna klaar!',
      successSub: 'Check je inbox en bevestig je aanmelding. Je welkomstcode staat in diezelfde mail. Vermeld hem bij het boeken.',
      spamNote: 'Geen mail ontvangen? Check je spamfolder.'
    },
    en: {
      closeAria: 'Close',
      heading: 'Try your luck',
      sub: 'Scratch the panel and see what you win',
      coverText: 'SCRATCH HERE',
      prize: 'Free welcome gift',
      prizeItems: ['Bottle of bubbles in your room', 'Bathrobe &amp; towels'],
      claimBtn: 'Claim your gift',
      emailHeading: 'Where shall we send your code?',
      emailPlaceholder: 'you@email.com',
      emailBtn: 'Send me the code',
      terms: 'Not valid in combination with packages. Valid on your first stay.',
      consent: 'By signing up you agree to our <a href="/privacyverklaring" target="_blank">privacy policy</a>. You can unsubscribe at any time.',
      errorText: 'Something went wrong. Please try again.',
      successHeading: 'Almost done!',
      successSub: 'Check your inbox and confirm your sign-up. Your welcome code is in that same email. Mention it when you book.',
      spamNote: 'No email? Check your spam folder.'
    },
    de: {
      closeAria: 'Schließen',
      heading: 'Versuchen Sie Ihr Glück',
      sub: 'Rubbeln Sie das Feld frei und sehen Sie, was Sie gewinnen',
      coverText: 'HIER RUBBELN',
      prize: 'Gratis Willkommensgeschenk',
      prizeItems: ['Flasche Sekt auf dem Zimmer', 'Bademantel &amp; Handtücher'],
      claimBtn: 'Geschenk einlösen',
      emailHeading: 'Wohin dürfen wir Ihren Code senden?',
      emailPlaceholder: 'ihre@email.de',
      emailBtn: 'Code senden',
      terms: 'Nicht mit Arrangements kombinierbar. Gültig bei Ihrem ersten Aufenthalt.',
      consent: 'Mit der Anmeldung stimmen Sie unserer <a href="/privacyverklaring" target="_blank">Datenschutzerklärung</a> zu. Abmeldung jederzeit möglich.',
      errorText: 'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.',
      successHeading: 'Fast geschafft!',
      successSub: 'Prüfen Sie Ihren Posteingang und bestätigen Sie Ihre Anmeldung. Ihr Willkommenscode steht in derselben E-Mail. Nennen Sie ihn bei der Buchung.',
      spamNote: 'Keine E-Mail erhalten? Prüfen Sie Ihren Spam-Ordner.'
    }
  };
  var t = COPY[lang];

  var LOGO   = 'https://www.asteria.nl/images/logo-hotel-asteria.png';
  var PHOTO  = '/fotos/popup-welkomstpakket.webp';
  var SCRIB  = '/fotos/scratch-scribble.png';
  var col = { accent: '#c23435', accentDark: '#a82c2c', coverTop: '#ecd681',
              coverBottom: '#c8a63d', coverInk: 'rgba(255,255,255,0.72)',
              scribble: '#8a7330', heading: '#1a1a1a' };
  var SCRIB_SCALE = 0.78, SCRIB_ALPHA = 0.6, SCRATCH_THRESHOLD = 0.5;

  // ── Styles ─────────────────────────────────────────────
  var css = ''
    + ".sc-overlay{position:fixed;inset:0;background:rgba(20,20,20,0.62);z-index:1200;display:flex;align-items:center;justify-content:center;padding:16px;font-family:'Montserrat',sans-serif;overflow-y:auto;opacity:0;pointer-events:none;transition:opacity .3s ease;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;}"
    + ".sc-overlay.is-open{opacity:1;pointer-events:auto;}"
    + ".sc-overlay input{-webkit-user-select:text;user-select:text;}"
    + ".sc-modal{display:flex;width:100%;max-width:900px;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 32px 90px rgba(0,0,0,0.5);position:relative;max-height:94vh;}"
    + ".sc-photo{flex:0 0 50%;background:url('" + PHOTO + "') 78% center/cover no-repeat;min-height:500px;margin:22px;border-radius:16px;}"
    + ".sc-panel{flex:1 1 auto;position:relative;padding:44px 48px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow-y:auto;}"
    + ".sc-close{position:absolute;top:16px;right:16px;width:32px;height:32px;border-radius:50%;background:rgba(0,0,0,0.05);border:none;color:#333;font-size:18px;line-height:1;cursor:pointer;z-index:5;display:flex;align-items:center;justify-content:center;transition:background .2s;font-family:inherit;}"
    + ".sc-close:hover{background:rgba(0,0,0,0.12);}"
    + ".sc-logo{height:46px;width:auto;margin:0 0 22px;}"
    + ".sc-h{font-family:'Montserrat',sans-serif;font-weight:600;font-size:34px;color:" + col.heading + ";line-height:1.1;margin:0 0 10px;letter-spacing:-0.5px;}"
    + ".sc-sub{font-size:15px;color:#555;font-weight:400;margin:0 0 26px;line-height:1.5;}"
    + ".sc-card{position:relative;width:280px;height:205px;border-radius:14px;overflow:hidden;box-shadow:0 12px 30px rgba(0,0,0,0.28);}"
    + ".sc-scratch-zone{display:inline-block;padding:20px;border-radius:26px;cursor:grab;border:2px dashed rgba(138,115,48,0.35);-webkit-tap-highlight-color:transparent;touch-action:none;}"
    + ".sc-scratch-zone:active{cursor:grabbing;}"
    + ".sc-prize{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:22px;background:#faf8f5;box-sizing:border-box;}"
    + ".sc-prize-title{font-weight:700;font-size:22px;color:" + col.heading + ";line-height:1.2;margin:0 0 10px;}"
    + ".sc-prize-list{list-style:none;padding:0;margin:12px auto 0;display:inline-block;text-align:left;}"
    + ".sc-prize-list li{position:relative;padding-left:24px;font-size:14px;color:#333;line-height:1.4;margin:6px 0;}"
    + ".sc-prize-list li::before{content:\"\";position:absolute;left:0;top:2px;width:15px;height:15px;background-image:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23c23435' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>\");background-size:contain;background-repeat:no-repeat;}"
    + ".sc-canvas{position:absolute;inset:0;width:100%;height:100%;cursor:grab;touch-action:none;transition:opacity .45s ease;}"
    + ".sc-canvas:active{cursor:grabbing;}"
    + ".sc-claim{margin-top:26px;opacity:0;transform:translateY(8px);pointer-events:none;transition:opacity .4s ease,transform .4s ease;width:100%;max-width:300px;}"
    + ".sc-claim.is-visible{opacity:1;transform:none;pointer-events:auto;}"
    + ".sc-btn{width:100%;background:" + col.accent + ";border:none;border-radius:4px;padding:16px 18px;font-family:'Montserrat',sans-serif;font-weight:600;font-size:15px;color:#fff;cursor:pointer;transition:background .2s;}"
    + ".sc-btn:hover{background:" + col.accentDark + ";}"
    + ".sc-btn:disabled{background:#b98a8a;cursor:default;}"
    + ".sc-stage{display:none;flex-direction:column;align-items:center;justify-content:center;width:100%;}"
    + ".sc-stage.is-active{display:flex;}"
    + ".sc-form{width:100%;max-width:340px;}"
    + ".sc-input{width:100%;box-sizing:border-box;background:#fff;border:1px solid #ccc;border-radius:4px;padding:14px 15px;font-family:'Montserrat',sans-serif;font-size:14px;color:#111;outline:none;margin-bottom:12px;transition:border-color .2s;}"
    + ".sc-input:focus{border-color:" + col.accent + ";}"
    + ".sc-input::placeholder{color:#a5a5a5;}"
    + ".sc-terms{font-size:11px;color:#9a9a9a;line-height:1.5;margin:14px 0 0;}"
    + ".sc-consent{font-size:11px;color:#8f8f8f;line-height:1.6;margin:14px 0 0;}"
    + ".sc-consent a{color:" + col.accent + ";text-decoration:underline;}"
    + ".sc-error{font-size:12px;color:" + col.accent + ";margin:10px 0 0;display:none;}"
    + ".sc-error.is-visible{display:block;}"
    + ".sc-success-icon{width:52px;height:52px;border-radius:50%;background:" + col.accent + ";display:flex;align-items:center;justify-content:center;margin:0 0 22px;}"
    + ".sc-success-icon svg{width:24px;height:24px;stroke:#fff;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;}"
    + ".sc-spam{font-size:11px;color:#9a9a9a;margin:12px 0 0;}"
    + "@media (max-width:680px){"
    +   ".sc-modal{flex-direction:column;max-width:420px;}"
    +   ".sc-photo{flex:none;order:2;width:auto;min-height:0;height:200px;margin:0 20px 20px;border-radius:14px;background-position:center;}"
    +   ".sc-panel{order:1;padding:34px 26px 26px;}"
    +   ".sc-h{font-size:28px;}"
    +   ".sc-card{width:250px;height:200px;}"
    +   ".sc-prize{padding:18px 16px;}"
    +   ".sc-prize-title{font-size:19px;margin:0 0 14px;}"
    +   ".sc-prize-list li{font-size:13px;margin:8px 0;}"
    + "}";
  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Verborgen Revinate-form + script ───────────────────
  var revForm = document.getElementById('revinate_contact_api_form');
  if (!revForm) {
    var f = document.createElement('form');
    f.id = 'revinate_contact_api_form';
    f.setAttribute('token', TOKEN[lang]);
    f.style.cssText = 'visibility:hidden;position:absolute;left:-9999px;width:1px;height:1px;';
    f.innerHTML = '<input type="email" name="email" id="sc_hidden_email">'
                + '<input type="text" name="vipStatus" value="Scratchcard">'
                + '<button type="submit" style="display:none">Submit</button>';
    document.body.appendChild(f);
    revForm = f;
  }
  if (!document.querySelector('script[src*="revinatecontactapi"]')) {
    var rev = document.createElement('script');
    rev.src = '//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1';
    rev.defer = true;
    document.head.appendChild(rev);
  }

  // ── Markup ─────────────────────────────────────────────
  var perksHtml = t.prizeItems.map(function (x) { return '<li>' + x + '</li>'; }).join('');
  var wrap = document.createElement('div');
  wrap.innerHTML = ''
    + '<div class="sc-overlay" id="scOverlay" role="dialog" aria-modal="true" aria-label="' + t.heading + '">'
    +   '<div class="sc-modal">'
    +     '<div class="sc-photo"></div>'
    +     '<div class="sc-panel">'
    +       '<button class="sc-close" id="scClose" aria-label="' + t.closeAria + '">&times;</button>'
    +       '<div class="sc-stage is-active" id="scStageScratch">'
    +         '<img class="sc-logo" src="' + LOGO + '" alt="Hotel Asteria">'
    +         '<h2 class="sc-h">' + t.heading + '</h2>'
    +         '<p class="sc-sub">' + t.sub + '</p>'
    +         '<div class="sc-scratch-zone" id="scZone">'
    +         '<div class="sc-card" id="scCard">'
    +           '<div class="sc-prize">'
    +             '<p class="sc-prize-title">' + t.prize + '</p>'
    +             '<ul class="sc-prize-list">' + perksHtml + '</ul>'
    +           '</div>'
    +           '<canvas class="sc-canvas" id="scCanvas"></canvas>'
    +         '</div>'
    +         '</div>'
    +         '<div class="sc-claim" id="scClaim"><button class="sc-btn" id="scClaimBtn">' + t.claimBtn + '</button></div>'
    +       '</div>'
    +       '<div class="sc-stage" id="scStageEmail">'
    +         '<img class="sc-logo" src="' + LOGO + '" alt="Hotel Asteria">'
    +         '<h2 class="sc-h" style="font-size:26px;margin-bottom:20px;">' + t.emailHeading + '</h2>'
    +         '<div class="sc-form">'
    +           '<input class="sc-input" type="email" id="scEmail" placeholder="' + t.emailPlaceholder + '" autocomplete="email">'
    +           '<button class="sc-btn" id="scSubmit">' + t.emailBtn + '</button>'
    +           '<p class="sc-error" id="scError">' + t.errorText + '</p>'
    +           '<p class="sc-terms">' + t.terms + '</p>'
    +           '<p class="sc-consent">' + t.consent + '</p>'
    +         '</div>'
    +       '</div>'
    +       '<div class="sc-stage" id="scStageSuccess">'
    +         '<div class="sc-success-icon"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div>'
    +         '<h2 class="sc-h" style="font-size:26px;">' + t.successHeading + '</h2>'
    +         '<p class="sc-sub" style="max-width:340px;">' + t.successSub + '</p>'
    +         '<p class="sc-spam">' + t.spamNote + '</p>'
    +       '</div>'
    +     '</div>'
    +   '</div>'
    + '</div>';
  document.body.appendChild(wrap.firstElementChild);

  // ── Refs ───────────────────────────────────────────────
  var overlay   = document.getElementById('scOverlay');
  var canvas    = document.getElementById('scCanvas');
  var claim     = document.getElementById('scClaim');
  var claimBtn  = document.getElementById('scClaimBtn');
  var stScratch = document.getElementById('scStageScratch');
  var stEmail   = document.getElementById('scStageEmail');
  var stSuccess = document.getElementById('scStageSuccess');
  var emailIn   = document.getElementById('scEmail');
  var submitBtn = document.getElementById('scSubmit');
  var errorEl   = document.getElementById('scError');

  function closePopup() { overlay.classList.remove('is-open'); }
  document.getElementById('scClose').addEventListener('click', closePopup);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) closePopup(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && overlay.classList.contains('is-open')) closePopup(); });

  // ── Kraslaag tekenen ───────────────────────────────────
  var ctx = canvas.getContext('2d');
  var revealed = false;

  var scribbleImage = new Image();
  scribbleImage.src = SCRIB;
  scribbleImage.onload = function () { if (!revealed) drawCover(); };

  function drawScribble(w, h) {
    if (!scribbleImage.complete || !scribbleImage.naturalWidth) return;
    var iw = scribbleImage.naturalWidth, ih = scribbleImage.naturalHeight;
    var tw = w * SCRIB_SCALE, th = tw * (ih / iw);
    var off = document.createElement('canvas');
    off.width = Math.max(1, Math.round(tw));
    off.height = Math.max(1, Math.round(th));
    var octx = off.getContext('2d');
    octx.drawImage(scribbleImage, 0, 0, off.width, off.height);
    octx.globalCompositeOperation = 'source-in';
    octx.fillStyle = col.scribble;
    octx.fillRect(0, 0, off.width, off.height);
    ctx.save();
    ctx.globalAlpha = SCRIB_ALPHA;
    ctx.drawImage(off, (w - tw) / 2, (h - th) / 2, tw, th);
    ctx.restore();
  }

  function drawCover() {
    var rect = canvas.getBoundingClientRect();
    if (!rect.width) return;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var w = rect.width, h = rect.height;

    ctx.globalCompositeOperation = 'source-over';
    var g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0.00, col.coverTop); g.addColorStop(0.45, col.coverBottom); g.addColorStop(1.00, col.coverTop);
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

    var rg = ctx.createRadialGradient(w*0.5, h*0.42, 8, w*0.5, h*0.5, Math.max(w, h)*0.72);
    rg.addColorStop(0, 'rgba(255,252,244,0.35)'); rg.addColorStop(1, 'rgba(255,252,244,0)');
    ctx.fillStyle = rg; ctx.fillRect(0, 0, w, h);

    var specks = Math.round(w * h * 0.9);
    for (var i = 0; i < specks; i++) {
      var x = Math.random() * w, y = Math.random() * h, r = Math.random();
      ctx.fillStyle = r < 0.72 ? 'rgba(255,248,214,' + (0.04 + r * 0.10).toFixed(3) + ')'
                               : 'rgba(120,95,35,' + (0.03 + (r - 0.72) * 0.12).toFixed(3) + ')';
      ctx.fillRect(x, y, 1, 1);
    }

    var sh = ctx.createLinearGradient(0, h, w, 0);
    sh.addColorStop(0.30, 'rgba(255,255,255,0)'); sh.addColorStop(0.50, 'rgba(255,255,238,0.22)'); sh.addColorStop(0.70, 'rgba(255,255,255,0)');
    ctx.fillStyle = sh; ctx.fillRect(0, 0, w, h);

    drawScribble(w, h);

    var vg = ctx.createRadialGradient(w*0.5, h*0.5, Math.min(w, h)*0.35, w*0.5, h*0.5, Math.max(w, h)*0.72);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(120,88,20,0.24)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);

    ctx.fillStyle = col.coverInk; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    if ('letterSpacing' in ctx) ctx.letterSpacing = '1px';
    var fs = Math.round(h * 0.19);
    ctx.font = "800 " + fs + "px 'Montserrat', sans-serif";
    while (ctx.measureText(t.coverText).width > w * 0.86 && fs > 10) { fs -= 1; ctx.font = "800 " + fs + "px 'Montserrat', sans-serif"; }
    ctx.fillText(t.coverText, w/2, h/2);
    if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
  }

  // ── Scratch-tracking ───────────────────────────────────
  var COLS = 26, ROWS = 30, cells = new Uint8Array(COLS * ROWS), BRUSH = 24;
  var scratchedCount = 0, drawing = false, lastX = null, lastY = null, scratchStarted = false;

  function markPoint(x, y) {
    var rect = canvas.getBoundingClientRect();
    var cw = rect.width / COLS, ch = rect.height / ROWS;
    for (var c = 0; c < COLS; c++) for (var r = 0; r < ROWS; r++) {
      var idx = r * COLS + c;
      if (cells[idx]) continue;
      var cx = (c + 0.5) * cw, cy = (r + 0.5) * ch;
      if (Math.hypot(cx - x, cy - y) <= BRUSH) { cells[idx] = 1; scratchedCount++; }
    }
  }

  function scratchLine(x0, y0, x1, y1) {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.globalAlpha = 1; ctx.strokeStyle = 'rgba(0,0,0,1)'; ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.lineWidth = BRUSH * 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    ctx.beginPath(); ctx.arc(x1, y1, BRUSH, 0, Math.PI * 2); ctx.fill();
    var dist = Math.hypot(x1 - x0, y1 - y0);
    var steps = Math.max(1, Math.round(dist / (BRUSH * 0.6)));
    for (var s = 0; s <= steps; s++) markPoint(x0 + (x1 - x0) * (s / steps), y0 + (y1 - y0) * (s / steps));
    if (!revealed && scratchedCount / (COLS * ROWS) >= SCRATCH_THRESHOLD) reveal();
  }

  function posFromEvent(e) {
    var rect = canvas.getBoundingClientRect();
    var p = e.touches ? e.touches[0] : e;
    return { x: p.clientX - rect.left, y: p.clientY - rect.top };
  }

  canvas.addEventListener('pointerdown', function (e) {
    e.preventDefault(); drawing = true; canvas.setPointerCapture(e.pointerId);
    if (!scratchStarted) { scratchStarted = true; track('scratch_start'); }
    var p = posFromEvent(e); lastX = p.x; lastY = p.y; scratchLine(p.x, p.y, p.x, p.y);
  });
  canvas.addEventListener('pointermove', function (e) {
    if (!drawing) return; e.preventDefault();
    var p = posFromEvent(e); scratchLine(lastX, lastY, p.x, p.y); lastX = p.x; lastY = p.y;
  });
  canvas.addEventListener('pointerup', function () { drawing = false; lastX = lastY = null; });
  canvas.addEventListener('pointercancel', function () { drawing = false; lastX = lastY = null; });

  function reveal() {
    revealed = true;
    canvas.style.opacity = '0';
    setTimeout(function () { canvas.style.display = 'none'; }, 450);
    claim.classList.add('is-visible');
    track('scratch_reveal');
  }

  // ── Stappen ────────────────────────────────────────────
  claimBtn.addEventListener('click', function () {
    stScratch.classList.remove('is-active');
    stEmail.classList.add('is-active');
    setTimeout(function () { emailIn.focus(); }, 250);
  });

  var submitting = false;
  function showSuccess() {
    submitting = false;
    stEmail.classList.remove('is-active');
    stSuccess.classList.add('is-active');
    localStorage.setItem('ec_converted', '1');
    track('email_success');
  }
  function showError() {
    submitting = false;
    errorEl.classList.add('is-visible');
    submitBtn.disabled = false;
    submitBtn.innerHTML = t.emailBtn;
  }

  submitBtn.addEventListener('click', function () {
    if (submitting) return;
    submitting = true;
    var email = emailIn.value.trim();
    if (!email || !emailIn.checkValidity()) { submitting = false; emailIn.focus(); return; }
    submitBtn.disabled = true; submitBtn.textContent = '...';
    errorEl.classList.remove('is-visible');
    track('email_submit');
    var hidden = document.getElementById('sc_hidden_email');
    if (hidden) hidden.value = email;
    try {
      if (typeof revFormOnSubmit === 'function') { revFormOnSubmit(); }
      else if (revForm) { revForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); }
      else { showError(); return; }
      showSuccess();
    } catch (err) { showError(); }
  });
  emailIn.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !submitting) submitBtn.click(); });

  // ── Open/close + triggers ──────────────────────────────
  var shown = false;
  function openPopup() {
    if (shown || sessionStorage.getItem('ec_shown')) return;
    shown = true;
    sessionStorage.setItem('ec_shown', '1');
    overlay.classList.add('is-open');
    drawCover();
    track('email_popup_open');
  }
  window.openScratchcard = openPopup;

  // Kraslaag alvast tekenen zodra fonts klaar zijn (canvas heeft layout, ook bij opacity 0)
  var paint = function () { drawCover(); };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(paint); else window.addEventListener('load', paint);
  window.addEventListener('resize', function () { if (!revealed) { scratchedCount = 0; cells.fill(0); drawCover(); } });

  // Trigger-timing (zelfde als variant A)
  var variant = sessionStorage.getItem('ec_variant');
  if (!variant) { variant = Math.random() < 0.5 ? 'A' : 'B'; sessionStorage.setItem('ec_variant', variant); }
  var isMobile = window.matchMedia('(max-width: 768px)').matches;

  if (variant === 'A') {
    setTimeout(openPopup, 12000);
    if (isMobile) {
      window.addEventListener('scroll', function onScrollA() {
        if ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight >= 0.45) {
          window.removeEventListener('scroll', onScrollA); openPopup();
        }
      }, { passive: true });
    }
  } else if (!isMobile) {
    document.addEventListener('mouseleave', function handler(e) {
      if (e.clientY <= 5) { document.removeEventListener('mouseleave', handler); openPopup(); }
    });
  } else {
    window.addEventListener('scroll', function onScroll() {
      if ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight >= 0.45) {
        window.removeEventListener('scroll', onScroll); openPopup();
      }
    }, { passive: true });
  }
})();
