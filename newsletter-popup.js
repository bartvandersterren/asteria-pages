/* ══════════════════════════════════════════════════════════
   UNIVERSELE NIEUWSBRIEF-POPUP — Hotel Asteria
   Witte-kaart ontwerp (foto links / boven), Asteria-brand.
   Injecteert zichzelf op elke pagina waar de popup nog niet
   inline aanwezig is. Taal via <html lang> (nl / en / de).
   Insluiten met: <script src="/newsletter-popup.js" defer></script>
══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ── Guards ─────────────────────────────────────────────
  if (document.getElementById('ecOverlay')) return;       // al inline aanwezig
  if (localStorage.getItem('ec_converted')) return;        // al aangemeld

  // ── Taal & copy ────────────────────────────────────────
  var lang = (document.documentElement.getAttribute('lang') || 'nl').slice(0, 2).toLowerCase();
  if (lang !== 'en' && lang !== 'de') lang = 'nl';

  // Revinate-lijst per taal (token op het verborgen form bepaalt de e-maillijst)
  var TOKEN_NL = '210bb345-899a-4f69-9b9f-4a00624a2024';
  var TOKEN_EN = 'b7a5ebe6-df0d-4a05-a5b6-3e9274ba9cc6';
  var TOKEN_DE = '449e7373-329f-4087-8f96-0124d65c69a4';

  var COPY = {
    nl: {
      token: TOKEN_NL,
      overlayAria: 'Nieuwsbrief aanmelden',
      closeAria: 'Sluiten',
      title: 'Gratis welkomstcadeau<br>bij je verblijf',
      perks: ['Flesje bubbels op de kamer', 'Badjas &amp; badhanddoeken'],
      terms: 'Niet in combinatie met arrangementen. Geldig bij je eerste verblijf.',
      label: 'E-mailadres',
      placeholder: 'jouw@email.nl',
      submit: 'Schrijf me in',
      submitReset: 'Schrijf me in',
      consent: 'Door in te schrijven ga je akkoord met ons <a href="/privacyverklaring" target="_blank">privacybeleid</a>. Je kunt je altijd afmelden.',
      error: 'Er ging iets mis. Probeer het opnieuw.',
      successTitle: 'Bijna klaar!',
      successSub: 'Check je inbox en bevestig je aanmelding. Je welkomstcode staat in diezelfde mail. Vermeld hem bij het boeken.',
      spamNote: 'Geen mail ontvangen? Check je spamfolder.'
    },
    en: {
      token: TOKEN_EN,
      overlayAria: 'Newsletter sign-up',
      closeAria: 'Close',
      title: 'Free welcome gift<br>with your stay',
      perks: ['Bottle of bubbles in your room', 'Bathrobe &amp; towels'],
      terms: 'Not valid in combination with packages. Valid on your first stay.',
      label: 'Email address',
      placeholder: 'you@email.com',
      submit: 'Sign me up',
      submitReset: 'Sign me up',
      consent: 'By signing up you agree to our <a href="/privacyverklaring" target="_blank">privacy policy</a>. You can unsubscribe at any time.',
      error: 'Something went wrong. Please try again.',
      successTitle: 'Almost done!',
      successSub: 'Check your inbox and confirm your sign-up. Your welcome code is in that same email. Mention it when you book.',
      spamNote: 'No email? Check your spam folder.'
    },
    de: {
      token: TOKEN_DE,
      overlayAria: 'Newsletter anmelden',
      closeAria: 'Schließen',
      title: 'Gratis Willkommensgeschenk<br>bei Ihrem Aufenthalt',
      perks: ['Flasche Sekt auf dem Zimmer', 'Bademantel &amp; Handtücher'],
      terms: 'Nicht mit Arrangements kombinierbar. Gültig bei Ihrem ersten Aufenthalt.',
      label: 'E-Mail-Adresse',
      placeholder: 'ihre@email.de',
      submit: 'Anmelden',
      submitReset: 'Anmelden',
      consent: 'Mit der Anmeldung stimmen Sie unserer <a href="/privacyverklaring" target="_blank">Datenschutzerklärung</a> zu. Abmeldung jederzeit möglich.',
      error: 'Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.',
      successTitle: 'Fast geschafft!',
      successSub: 'Prüfen Sie Ihren Posteingang und bestätigen Sie Ihre Anmeldung. Ihr Willkommenscode steht in derselben E-Mail. Nennen Sie ihn bei der Buchung.',
      spamNote: 'Keine E-Mail erhalten? Prüfen Sie Ihren Spam-Ordner.'
    }
  };
  var t = COPY[lang];

  // ── Styles ─────────────────────────────────────────────
  var CSS = ''
    + '.nlp-overlay{position:fixed;inset:0;background:rgba(20,20,20,0.62);z-index:1200;display:flex;align-items:center;justify-content:center;padding:16px;opacity:0;pointer-events:none;transition:opacity .3s ease;overflow-y:auto;font-family:"Montserrat",sans-serif;}'
    + '.nlp-overlay.is-open{opacity:1;pointer-events:auto;}'
    + '.nlp-modal{display:flex;width:100%;max-width:860px;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 32px 80px rgba(0,0,0,0.45);position:relative;transform:translateY(12px);transition:transform .3s ease;max-height:92vh;}'
    + '.nlp-overlay.is-open .nlp-modal{transform:translateY(0);}'
    + '.nlp-photo{flex:0 0 44%;background-image:url("/fotos/popup-welkomstpakket.webp");background-size:cover;background-position:center;min-height:520px;}'
    + '.nlp-panel{flex:1 1 auto;position:relative;padding:52px 52px 44px;display:flex;flex-direction:column;justify-content:center;overflow-y:auto;}'
    + '.nlp-close{position:absolute;top:14px;right:14px;width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,0.85);border:none;color:#333;font-size:18px;font-weight:400;line-height:1;cursor:pointer;z-index:2;display:flex;align-items:center;justify-content:center;transition:background .2s;font-family:inherit;}'
    + '.nlp-close:hover{background:#fff;}'
    + '.nlp-title{font-family:"Montserrat",sans-serif;font-weight:600;font-size:29px;color:#1a1a1a;line-height:1.22;margin:0 0 20px;letter-spacing:-0.2px;}'
    + '.nlp-perks{list-style:none;padding:0;margin:0 0 14px;display:flex;flex-direction:column;gap:8px;}'
    + '.nlp-perks li{position:relative;padding-left:28px;font-size:16px;color:#333;font-family:"Montserrat",sans-serif;font-weight:400;line-height:1.4;}'
    + '.nlp-perks li::before{content:"";position:absolute;left:0;top:3px;width:15px;height:15px;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23c23435\' stroke-width=\'3\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><polyline points=\'20 6 9 17 4 12\'/></svg>");background-size:contain;background-repeat:no-repeat;}'
    + '.nlp-terms{font-family:"Montserrat",sans-serif;font-weight:300;font-size:11px;color:#9a9a9a;line-height:1.5;margin:0 0 24px;}'
    + '.nlp-label{display:block;font-family:"Montserrat",sans-serif;font-weight:700;font-size:12px;color:#1a1a1a;margin:0 0 8px;}'
    + '.nlp-email-input{width:100%;box-sizing:border-box;background:#fff;border:1px solid #cccccc;border-radius:4px;padding:13px 14px;font-family:"Montserrat",sans-serif;font-weight:400;font-size:14px;color:#111;outline:none;transition:border-color .2s;}'
    + '.nlp-email-input::placeholder{color:#a5a5a5;}'
    + '.nlp-email-input:focus{border-color:#c23435;}'
    + '.nlp-submit-btn{width:100%;margin-top:16px;background:#c23435;border:none;border-radius:4px;padding:15px 18px;font-family:"Montserrat",sans-serif;font-weight:600;font-size:15px;color:#fff;cursor:pointer;transition:background .2s;}'
    + '.nlp-submit-btn:hover{background:#a82c2c;}'
    + '.nlp-submit-btn:disabled{background:#b98a8a;cursor:default;}'
    + '.nlp-consent{font-family:"Montserrat",sans-serif;font-weight:300;font-size:11px;color:#8f8f8f;line-height:1.6;margin:16px 0 0;}'
    + '.nlp-consent a{color:#c23435;text-decoration:underline;}'
    + '.nlp-error{font-size:12px;color:#c23435;margin:12px 0 0;display:none;}'
    + '.nlp-error.is-visible{display:block;}'
    + '.nlp-success{display:none;}'
    + '.nlp-success.is-visible{display:flex;flex-direction:column;}'
    + '.nlp-form-state.is-hidden{display:none;}'
    + '.nlp-success-icon{width:46px;height:46px;border-radius:50%;background:#c23435;display:flex;align-items:center;justify-content:center;margin-bottom:20px;flex-shrink:0;}'
    + '.nlp-success-icon svg{width:22px;height:22px;stroke:#fff;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;}'
    + '.nlp-success-title{font-family:"Montserrat",sans-serif;font-weight:600;font-size:24px;color:#1a1a1a;line-height:1.25;margin:0 0 12px;}'
    + '.nlp-success-sub{font-family:"Montserrat",sans-serif;font-weight:300;font-size:14px;color:#555;line-height:1.65;margin:0 0 12px;}'
    + '.nlp-spam-note{font-family:"Montserrat",sans-serif;font-weight:300;font-size:11px;color:#9a9a9a;line-height:1.6;margin:0;}'
    + '@media (max-width:640px){'
    +   '.nlp-modal{flex-direction:column;max-width:400px;}'
    +   '.nlp-photo{flex:none;width:100%;min-height:0;height:190px;}'
    +   '.nlp-panel{padding:26px 24px 30px;}'
    +   '.nlp-title{font-size:22px;}'
    + '}';

  var styleEl = document.createElement('style');
  styleEl.id = 'nlp-styles';
  styleEl.textContent = CSS;
  document.head.appendChild(styleEl);

  // ── Markup ─────────────────────────────────────────────
  var perksHtml = t.perks.map(function (p) { return '<li>' + p + '</li>'; }).join('');
  var markup = ''
    + '<div class="nlp-overlay" id="ecOverlay" role="dialog" aria-modal="true" aria-label="' + t.overlayAria + '">'
    +   '<div class="nlp-modal" id="ecModal">'
    +     '<div class="nlp-photo"></div>'
    +     '<div class="nlp-panel">'
    +       '<button class="nlp-close" id="ecClose" aria-label="' + t.closeAria + '">&times;</button>'
    +       '<div class="nlp-form-state" id="ecFormState">'
    +         '<h2 class="nlp-title">' + t.title + '</h2>'
    +         '<ul class="nlp-perks">' + perksHtml + '</ul>'
    +         '<p class="nlp-terms">' + t.terms + '</p>'
    +         '<label class="nlp-label" for="ecEmail">' + t.label + '</label>'
    +         '<input class="nlp-email-input" type="email" id="ecEmail" placeholder="' + t.placeholder + '" autocomplete="email">'
    +         '<p class="nlp-error" id="ecError">' + t.error + '</p>'
    +         '<button class="nlp-submit-btn" id="ecSubmit">' + t.submit + '</button>'
    +         '<p class="nlp-consent">' + t.consent + '</p>'
    +       '</div>'
    +       '<div class="nlp-success" id="ecSuccess">'
    +         '<div class="nlp-success-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg></div>'
    +         '<h2 class="nlp-success-title">' + t.successTitle + '</h2>'
    +         '<p class="nlp-success-sub">' + t.successSub + '</p>'
    +         '<p class="nlp-spam-note">' + t.spamNote + '</p>'
    +       '</div>'
    +     '</div>'
    +   '</div>'
    + '</div>'
    // Verborgen Revinate-form (submit-doel → e-maillijst)
    + '<form id="revinate_contact_api_form" token="' + t.token + '" style="visibility:hidden;position:absolute;left:-9999px;width:1px;height:1px;">'
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
    if (window.track) window.track('email_popup_open', { variant_email: 'A_whitecard' });
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
    if (window.track) window.track('email_success', { variant_email: 'A_whitecard' });
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
    if (window.track) window.track('email_submit', { variant_email: 'A_whitecard' });

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
