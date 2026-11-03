/* ══════════════════════════════════════════════════════════
   D1-ANALYTICS (window.track) voor pagina's zonder eigen tracker
   Zelfde code als het ANALYTICS-blok in hotel-venray.html: page_view bij
   laden, cta_click op [data-track-cta], window.track(event, props) voor de
   pop-ups (email_popup_open, scratch_start, scratch_reveal, email_submit,
   email_success). POST naar /api/track (D1 asteria-analytics).
   Geladen door lander-w1-pagina's met de scratchcard (build-blok 'scratchcard').
══════════════════════════════════════════════════════════ */
(function () {
  if (window.track) return;
  var sid = sessionStorage.getItem('_sid');
  if (!sid) {
    sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem('_sid', sid);
  }

  function track(event, props) {
    if (localStorage.getItem('asteria_no_track')) return;
    var payload = {
      session_id:    sid,
      event:         event,
      page:          location.pathname,
      referrer:      document.referrer || null,
      variant_price: sessionStorage.getItem('price_variant') || null,
      variant_email: sessionStorage.getItem('ec_variant') || null,
    };
    if (props) {
      Object.keys(props).forEach(function (k) { payload[k] = props[k]; });
    }
    fetch('/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(function () {});
  }

  window.track = track;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { track('page_view'); });
  } else {
    track('page_view');
  }

  function ctas() {
    document.querySelectorAll('[data-track-cta]').forEach(function (el) {
      el.addEventListener('click', function () {
        track('cta_click', { cta: el.getAttribute('data-track-cta') });
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ctas); else ctas();
})();
