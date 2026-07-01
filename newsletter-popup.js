/* ══════════════════════════════════════════════════════════
   UNIVERSELE NIEUWSBRIEF-POPUP — Hotel Asteria
   Injecteert zelf de e-mail-capture popup (welkomstpakket) op
   elke pagina waar deze nog niet inline aanwezig is.
   Taal wordt afgeleid uit <html lang> (nl / en / de).
   Insluiten met: <script src="/newsletter-popup.js" defer></script>
══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── Guards ─────────────────────────────────────────────
  // Pagina heeft de popup al inline → niets doen (geen dubbele markup/ID's)
  if (document.getElementById('ecOverlay')) return;
  // Bezoeker heeft zich al aangemeld → nooit meer tonen
  if (localStorage.getItem('ec_converted')) return;

  // ── Taal & copy ────────────────────────────────────────
  var lang = (document.documentElement.getAttribute('lang') || 'nl').slice(0, 2).toLowerCase();
  if (lang !== 'en' && lang !== 'de') lang = 'nl';

  var COPY = {
    nl: {
      overlayAria: 'Nieuwsbrief aanmelden',
      closeAria: 'Sluiten',
      title: 'Gratis welkomstpakket<br>bij uw verblijf',
      perks: ['&#x1F6C1; Badjas &amp; handdoek', '&#x1F942; Fles bubbels op de kamer'],
      sub: 'Meld u aan en ontvang uw persoonlijke code per e-mail.',
      error: 'Er ging iets mis. Probeer het opnieuw.',
      placeholder: 'uw e-mailadres',
      submit: 'Stuur mij de code &#x2192;',
      submitReset: 'Aanmelden',
      consent: 'Door u aan te melden gaat u akkoord met onze <a href="/privacyverklaring" target="_blank">privacyverklaring</a>. Afmelden kan altijd.',
      successTitle: 'Bijna klaar!',
      successSub: 'Check uw inbox en bevestig uw aanmelding. Uw welkomstcode staat in diezelfde mail. Vermeld hem bij het boeken.',
      spamNote: 'Geen mail ontvangen? Check uw spamfolder.'
    },
    en: {
      overlayAria: 'Newsletter sign-up',
      closeAria: 'Close',
      title: 'Free welcome package<br>with your stay',
      perks: ['&#x1F6C1; Bathrobe &amp; towel', '&#x1F942; Bottle of bubbles in your room'],
      sub: 'Sign up and receive your personal code by email.',
      error: 'Something went wrong. Please try again.',
      placeholder: 'your email address',
      submit: 'Send me the code &#x2192;',
      submitReset: 'Sign up',
      consent: 'By signing up you agree to our <a href="/privacyverklaring" target="_blank">privacy policy</a>. You can unsubscribe at any time.',
      successTitle: 'Almost done!',
      successSub: 'Check your inbox and confirm your sign-up. Your welcome code is in that same email. Mention it when you book.',
      spamNote: 'No email? Check your spam folder.'
    },
    de: {
      overlayAria: 'Newsletter anmelden',
      closeAria: 'Schließen',
      title: 'Gratis Willkommenspaket<br>bei Ihrem Aufenthalt',
      perks: ['&#x1F6C1; Bademantel &amp; Handtuch', '&#x1F942; Flasche Sekt auf dem Zimmer'],
      sub: 'Melden Sie sich an und erhalten Sie Ihren persönlichen Code per E-Mail.',
      error: 'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.',
      placeholder: 'Ihre E-Mail-Adresse',
      submit: 'Code senden &#x2192;',
      submitReset: 'Anmelden',
      consent: 'Mit der Anmeldung stimmen Sie unserer <a href="/privacyverklaring" target="_blank">Datenschutzerklärung</a> zu. Abmeldung jederzeit möglich.',
      successTitle: 'Fast geschafft!',
      successSub: 'Prüfen Sie Ihren Posteingang und bestätigen Sie Ihre Anmeldung. Ihr Willkommenscode steht in derselben E-Mail. Nennen Sie ihn bei der Buchung.',
      spamNote: 'Keine E-Mail erhalten? Prüfen Sie Ihren Spam-Ordner.'
    }
  };
  var t = COPY[lang];

  // ── Styles injecteren (eenmalig) ───────────────────────
  var CSS = ''
    + '.ec-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.65);z-index:1200;display:flex;align-items:center;justify-content:center;padding:16px;opacity:0;pointer-events:none;transition:opacity .3s ease;}'
    + '.ec-overlay.is-open{opacity:1;pointer-events:auto;}'
    + '.ec-modal{width:100%;max-width:480px;border-radius:4px;overflow:hidden;box-shadow:0 32px 80px rgba(0,0,0,0.65);position:relative;transform:translateY(12px);transition:transform .3s ease;}'
    + '.ec-overlay.is-open .ec-modal{transform:translateY(0);}'
    + '.ec-modal-inner{position:relative;min-height:480px;display:flex;flex-direction:column;justify-content:flex-end;padding:40px 40px 40px;}'
    + '.ec-modal-bg{position:absolute;inset:-6px;background-image:url("/fotos/hero-buitenkant.webp");background-size:cover;background-position:center;filter:blur(5px);}'
    + '.ec-modal-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,0.90) 0%,rgba(0,0,0,0.55) 50%,rgba(0,0,0,0.30) 100%);}'
    + '.ec-close{position:absolute;top:14px;right:16px;background:none;border:none;color:rgba(255,255,255,0.45);font-size:22px;font-weight:300;cursor:pointer;line-height:1;z-index:2;transition:color .2s;padding:4px;font-family:inherit;}'
    + '.ec-close:hover{color:rgba(255,255,255,0.85);}'
    + '.ec-content{position:relative;z-index:1;}'
    + '.ec-title{font-family:"Montserrat",sans-serif;font-weight:300;font-size:27px;color:#fff;line-height:1.25;margin:0 0 12px;letter-spacing:-0.3px;}'
    + '.ec-sub{font-family:"Montserrat",sans-serif;font-weight:300;font-size:14px;color:rgba(255,255,255,0.72);line-height:1.65;margin:0 0 28px;}'
    + '.ec-form-row{display:flex;flex-direction:column;gap:10px;margin-bottom:14px;}'
    + '.ec-email-input{width:100%;background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.25);border-radius:3px;padding:14px 16px;font-family:"Montserrat",sans-serif;font-weight:300;font-size:14px;color:#fff;outline:none;transition:border-color .2s,background .2s;}'
    + '.ec-email-input::placeholder{color:rgba(255,255,255,0.38);}'
    + '.ec-email-input:focus{background:rgba(255,255,255,0.14);border-color:rgba(255,255,255,0.50);}'
    + '.ec-submit-btn{width:100%;background:#c23435;border:none;border-radius:3px;padding:15px 18px;font-family:"Electrolize",sans-serif;font-size:11px;letter-spacing:2.5px;color:#fff;text-transform:uppercase;cursor:pointer;transition:background .2s;}'
    + '.ec-submit-btn:hover{background:#a82c2c;}'
    + '.ec-submit-btn:disabled{background:#888;cursor:default;}'
    + '.ec-consent{font-family:"Montserrat",sans-serif;font-weight:300;font-size:11px;color:rgba(255,255,255,0.42);line-height:1.6;}'
    + '.ec-consent a{color:rgba(255,255,255,0.60);text-decoration:underline;text-decoration-color:rgba(255,255,255,0.25);}'
    + '.ec-perks{list-style:none;padding:0;margin:0 0 12px;display:flex;flex-direction:column;gap:4px;}'
    + '.ec-perks li{font-size:14px;color:rgba(255,255,255,0.88);font-family:"Montserrat",sans-serif;font-weight:400;}'
    + '.ec-error{font-size:11px;color:#ff8a8a;margin-bottom:10px;display:none;}'
    + '.ec-error.is-visible{display:block;}'
    + '.ec-success{display:none;}'
    + '.ec-success.is-visible{display:flex;flex-direction:column;}'
    + '.ec-form-state.is-hidden{display:none;}'
    + '.ec-success-icon{width:44px;height:44px;border:1px solid rgba(255,255,255,0.22);border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:20px;flex-shrink:0;}'
    + '.ec-success-icon svg{width:18px;height:18px;stroke:rgba(255,255,255,0.6);fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;}'
    + '.ec-success-title{font-family:"Montserrat",sans-serif;font-weight:300;font-size:27px;color:#fff;line-height:1.25;margin:0 0 12px;}'
    + '.ec-success-sub{font-family:"Montserrat",sans-serif;font-weight:300;font-size:14px;color:rgba(255,255,255,0.72);line-height:1.65;margin:0 0 12px;}'
    + '.ec-spam-note{font-family:"Montserrat",sans-serif;font-weight:300;font-size:11px;color:rgba(255,255,255,0.38);line-height:1.6;}'
    + '@media (max-width:480px){.ec-modal-inner{padding:32px 24px 32px;min-height:400px;}.ec-title,.ec-success-title{font-size:22px;}.ec-sub,.ec-success-sub{font-size:13px;}}';

  var styleEl = document.createElement('style');
  styleEl.id = 'ec-styles';
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ── Markup injecteren ──────────────────────────────────
  var perksHtml = t.perks.map(function (p) { return '<li>' + p + '</li>'; }).join('');
  var markup = ''
    + '<div class="ec-overlay" id="ecOverlay" role="dialog" aria-modal="true" aria-label="' + t.overlayAria + '">'
    +   '<div class="ec-modal" id="ecModal">'
    +     '<div class="ec-modal-inner">'
    +       '<div class="ec-modal-bg"></div>'
    +       '<button class="ec-close" id="ecClose" aria-label="' + t.closeAria + '">&times;</button>'
    +       '<div class="ec-content">'
    +         '<div class="ec-form-state" id="ecFormState">'
    +           '<h2 class="ec-title">' + t.title + '</h2>'
    +           '<ul class="ec-perks">' + perksHtml + '</ul>'
    +           '<p class="ec-sub">' + t.sub + '</p>'
    +           '<p class="ec-error" id="ecError">' + t.error + '</p>'
    +           '<div class="ec-form-row">'
    +             '<input class="ec-email-input" type="email" id="ecEmail" placeholder="' + t.placeholder + '" autocomplete="email">'
    +             '<button class="ec-submit-btn" id="ecSubmit">' + t.submit + '</button>'
    +           '</div>'
    +           '<p class="ec-consent">' + t.consent + '</p>'
    +         '</div>'
    +         '<div class="ec-success" id="ecSuccess">'
    +           '<div class="ec-success-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2,4 12,13 22,4"/></svg></div>'
    +           '<h2 class="ec-success-title">' + t.successTitle + '</h2>'
    +           '<p class="ec-success-sub">' + t.successSub + '</p>'
    +           '<p class="ec-spam-note">' + t.spamNote + '</p>'
    +         '</div>'
    +       '</div>'
    +     '</div>'
    +   '</div>'
    + '</div>'
    // Verborgen Revinate-form (submit-doel)
    + '<form id="revinate_contact_api_form" token="210bb345-899a-4f69-9b9f-4a00624a2024" style="visibility:hidden;position:absolute;left:-9999px;width:1px;height:1px;">'
    +   '<input type="email" name="email" id="ec_hidden_email">'
    +   '<input type="text" name="vipStatus" value="Website popup">'
    +   '<button type="submit" style="display:none">Submit</button>'
    + '</form>';

  var holder = document.createElement('div');
  holder.innerHTML = markup;
  while (holder.firstChild) document.body.appendChild(holder.firstChild);

  // ── Revinate Contact API script laden (indien nog niet aanwezig) ──
  if (!document.querySelector('script[src*="revinatecontactapi"]')) {
    var rev = document.createElement('script');
    rev.src = '//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1';
    rev.defer = true;
    document.head.appendChild(rev);
  }

  // ── Popup-logica ───────────────────────────────────────
  var overlay    = document.getElementById('ecOverlay');
  var btnClose   = document.getElementById('ecClose');
  var formState  = document.getElementById('ecFormState');
  var successEl  = document.getElementById('ecSuccess');
  var emailInput = document.getElementById('ecEmail');
  var submitBtn  = document.getElementById('ecSubmit');
  var errorEl    = document.getElementById('ecError');

  if (!overlay) return;

  var shown = false;
  var submitting = false;

  // Variant toewijzen vóór triggers
  var variant = sessionStorage.getItem('ec_variant');
  if (!variant) {
    variant = Math.random() < 0.5 ? 'A' : 'B';
    sessionStorage.setItem('ec_variant', variant);
  }

  function openPopup() {
    if (shown) return;
    if (sessionStorage.getItem('ec_shown')) return;
    shown = true;
    sessionStorage.setItem('ec_shown', '1');
    overlay.classList.add('is-open');
    if (window.track) window.track('email_popup_open');
    setTimeout(function () { emailInput && emailInput.focus(); }, 350);
  }

  function closePopup() {
    overlay.classList.remove('is-open');
  }

  btnClose.addEventListener('click', closePopup);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePopup();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closePopup();
  });

  window.openEmailCapture = openPopup;

  function showSuccess() {
    submitting = false;
    formState.classList.add('is-hidden');
    successEl.classList.add('is-visible');
    localStorage.setItem('ec_converted', '1');
    if (window.track) window.track('email_success');
  }

  function showError() {
    submitting = false;
    errorEl.classList.add('is-visible');
    submitBtn.disabled = false;
    submitBtn.innerHTML = t.submitReset;
  }

  submitBtn.addEventListener('click', function () {
    if (submitting) return;
    submitting = true;

    var email = emailInput.value.trim();
    if (!email || !emailInput.checkValidity()) {
      submitting = false;
      emailInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = '...';
    errorEl.classList.remove('is-visible');
    if (window.track) window.track('email_submit');

    // Kopieer email naar verborgen Revinate-form
    var hiddenEmail = document.getElementById('ec_hidden_email');
    if (hiddenEmail) hiddenEmail.value = email;

    // Roep Revinate submit aan
    try {
      var revForm = document.getElementById('revinate_contact_api_form');
      if (typeof revFormOnSubmit === 'function') {
        revFormOnSubmit();
      } else if (revForm) {
        revForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      } else {
        showError();
        return;
      }
      showSuccess();
    } catch (e) {
      showError();
    }
  });

  emailInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !submitting) submitBtn.click();
  });

  // ── A/B split ──────────────────────────────────────────
  // Variant A: timer 12s + scroll 45% backup op mobile
  if (variant === 'A') {
    setTimeout(openPopup, 12000);
    if (window.matchMedia('(max-width: 768px)').matches) {
      window.addEventListener('scroll', function onScrollA() {
        var scrolled = window.scrollY + window.innerHeight;
        var total = document.documentElement.scrollHeight;
        if (scrolled / total >= 0.45) {
          window.removeEventListener('scroll', onScrollA);
          openPopup();
        }
      }, { passive: true });
    }
    return;
  }

  // Variant B: exit intent (desktop) + scroll 45% (mobile)
  var isMobile = window.matchMedia('(max-width: 768px)').matches;
  if (!isMobile) {
    document.addEventListener('mouseleave', function handler(e) {
      if (e.clientY <= 5) {
        document.removeEventListener('mouseleave', handler);
        openPopup();
      }
    });
  } else {
    window.addEventListener('scroll', function onScroll() {
      var scrolled = window.scrollY + window.innerHeight;
      var total = document.documentElement.scrollHeight;
      if (scrolled / total >= 0.45) {
        window.removeEventListener('scroll', onScroll);
        openPopup();
      }
    }, { passive: true });
  }
})();
