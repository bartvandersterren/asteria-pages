/* Overgenomen uit output/pages/website/index.html op 3-8-2026.
 * Alles wat op de HOMEPAGE staat is een kopie van het pagina-script: NIET met de
 * hand bijwerken, maar opnieuw kopiëren als het script in de pagina verandert.
 * Dat geldt voor selector-strip, dropdowns, kalender en de aanbod-swipe.
 *
 * SINDS 20-8-2026 draagt dit bestand daarnaast BLOK-interacties die niet op de
 * homepage staan (nu: .filmstrip). Die horen bij een blok uit de styleguide en
 * zijn hier canoniek — die kopieer je dus de andere kant op, naar de pagina die
 * het blok gebruikt. Ze staan onderaan, onder een eigen kop, zodat de twee
 * soorten niet door elkaar lopen.
 *
 * Het script is defensief: 35 guards, geen ongecontroleerde dereference. Een
 * blok dat niet in de DOM staat wordt overgeslagen in plaats van dat het script
 * afbreekt. Daarom kan het in de styleguide draaien waar maar een deel van de
 * blokken zichtbaar is.
 */

(() => {
  'use strict';

  const isDesktop = () => window.matchMedia('(min-width: 1024px)').matches;

  /* ───── Kalender-widget voor aankomst / vertrek / booking-bar range ─────
     - Aankomst en vertrek in .booking-card: single-select, elk hun eigen
       kalender (vertrek heeft aankomst+1 als min-date).
     - Booking-bar (mobiel): één range-kalender, tap 1 = aankomst, tap 2 = vertrek.
     - Gedeelde state via bookingState — kalenders re-renderen synchroon.
  */
  (() => {
    const bookingState = { aankomst: null, vertrek: null };
    const monthNames = ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
    const fmt = (d) => new Intl.DateTimeFormat('nl-NL', { day: 'numeric', month: 'short' }).format(d).replace('.', '');
    const eq = (a, b) => a && b && a.toDateString() === b.toDateString();
    const stripTime = (d) => { const n = new Date(d); n.setHours(0,0,0,0); return n; };

    const calendars = [];
    const today = stripTime(new Date());
    const firstOfThisMonth = new Date(today.getFullYear(), today.getMonth(), 1);

    function makeCalendar(container, opts) {
      const grid = container.querySelector('[data-cal-grid]');
      const title = container.querySelector('[data-cal-title]');
      const prevBtn = container.querySelector('.cal-nav.prev');
      const nextBtn = container.querySelector('.cal-nav.next');

      let cursor = new Date(today.getFullYear(), today.getMonth(), 1);

      const render = () => {
        const year = cursor.getFullYear();
        const month = cursor.getMonth();
        title.textContent = `${monthNames[month]} ${year}`;

        const prevMonth = new Date(year, month - 1, 1);
        prevBtn.disabled = prevMonth < firstOfThisMonth;

        grid.innerHTML = '';
        const first = new Date(year, month, 1);
        const last = new Date(year, month + 1, 0);
        const firstDayIdx = (first.getDay() + 6) % 7;

        for (let i = 0; i < firstDayIdx; i++) {
          const empty = document.createElement('span');
          empty.className = 'cal-day is-empty';
          grid.appendChild(empty);
        }

        const minDate = opts.getMinDate ? opts.getMinDate() : today;
        for (let d = 1; d <= last.getDate(); d++) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'cal-day';
          btn.textContent = d;
          const date = new Date(year, month, d);

          if (date < minDate) btn.disabled = true;
          if (eq(date, today)) btn.classList.add('is-today');

          if (opts.mode === 'single') {
            if (eq(date, opts.getSelected && opts.getSelected())) btn.classList.add('is-selected');
          } else if (opts.mode === 'range') {
            const range = opts.getRange ? opts.getRange() : [null, null];
            const start = range[0], end = range[1];
            if (eq(date, start)) btn.classList.add('is-range-start');
            if (eq(date, end)) btn.classList.add('is-range-end');
            if (start && end && date > start && date < end) btn.classList.add('is-in-range');
          }

          if (!btn.disabled) {
            btn.addEventListener('click', (e) => {
              e.stopPropagation();
              opts.onSelect(date);
            });
          }
          grid.appendChild(btn);
        }
      };

      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        cursor = new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1);
        if (cursor < firstOfThisMonth) cursor = new Date(firstOfThisMonth);
        render();
      });
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
        render();
      });

      // Klik binnen kalender niet laten bubbelen naar veld-toggle
      container.addEventListener('click', (e) => e.stopPropagation());

      render();
      calendars.push({ render });
      return { render };
    }

    const renderAll = () => calendars.forEach(c => c.render());

    /* querySelectorAll, niet querySelector. Op de pagina staat één widget, maar
       de styleguide toont er meerdere naast elkaar; met enkelvoud kreeg alleen
       de eerste een kalender en hield de rest een lege grid onder de
       weekdagenrij over. */
    const updateDisplay = () => {
      document.querySelectorAll('.booking-card [data-field="aankomst"] .value').forEach(el => {
        el.textContent = bookingState.aankomst ? fmt(bookingState.aankomst) : 'Kies datum';
      });
      document.querySelectorAll('.booking-card [data-field="vertrek"] .value').forEach(el => {
        el.textContent = bookingState.vertrek ? fmt(bookingState.vertrek) : 'Kies datum';
      });

      document.querySelectorAll('.booking-bar [data-bar-field="datum"] [data-bar-value]').forEach(barVal => {
        if (bookingState.aankomst && bookingState.vertrek) {
          barVal.textContent = `${fmt(bookingState.aankomst)} – ${fmt(bookingState.vertrek)}`;
          barVal.classList.remove('is-placeholder');
        } else if (bookingState.aankomst) {
          barVal.textContent = `Vanaf ${fmt(bookingState.aankomst)}`;
          barVal.classList.remove('is-placeholder');
        } else {
          barVal.textContent = 'Kies een periode';
          barVal.classList.add('is-placeholder');
        }
      });
      /* Publiceer de gekozen periode zodat de Mews-laag hierboven hem als
         mewsStart/mewsEnd kan meesturen. De state zelf blijft binnen deze
         IIFE; dit is een bewust smalle uitgang, geen gedeelde store. */
      window.__asteriaBooking = { aankomst: bookingState.aankomst, vertrek: bookingState.vertrek };
      renderAll();
    };

    document.querySelectorAll('.booking-card [data-field="aankomst"] [data-calendar]').forEach(aC => {
      makeCalendar(aC, {
        mode: 'single',
        getSelected: () => bookingState.aankomst,
        onSelect: (date) => {
          bookingState.aankomst = date;
          /* Klant-review 11-9-2026, item 10 (en de tweede ronde erop): wie een
             aankomst koos moest daarna apart het vertrekveld opzoeken en
             openklikken. Twee dingen gebeuren nu in één beweging.

             Eén: vertrek springt mee op aankomst + 1 nacht, want dat is verreweg
             het vaakste verblijf. Het is een voorzet, geen beslissing — een
             vertrek dat de gast zélf koos wordt niet overschreven, tenzij het
             door de nieuwe aankomst onmogelijk is geworden.

             Twee: de vertrekkalender gaat dan meteen open, zodat je die nacht
             met één klik iets anders maakt in plaats van eerst het veld te
             moeten vinden. Alleen als we het vertrek ook echt hebben gezet —
             stond er al een eigen keuze, dan verandert er niets en zou een
             openspringende kalender alleen in de weg zitten.

             De vertraging is geen sierlijkheid maar noodzaak: deze klik borrelt
             door naar de click-handler op `.field`, en die roept
             closeAllPopovers() aan. Openen we eerder, dan sluit die regel het
             meteen weer. 220 ms is net ná de 200 ms waarmee de aankomstkalender
             zichzelf dichtdoet, zodat de twee elkaar niet kruisen.

             Stond tot 11-9-2026 alleen inline op de homepage. Dat was de enige
             pagina met een `.booking-card`, dus hier verandert er voor de andere
             pagina's niets — maar krijgt er ooit een tweede pagina de widget,
             dan doet hij hetzelfde in plaats van het oude gedrag. */
          const vertrekVeld = aC.closest('.booking-card')
            ?.querySelector('[data-field="vertrek"]');
          let gezet = false;
          if (!bookingState.vertrek || bookingState.vertrek <= date) {
            const volgendeDag = new Date(date);
            volgendeDag.setDate(volgendeDag.getDate() + 1);
            bookingState.vertrek = volgendeDag;
            gezet = true;
          }
          updateDisplay();
          setTimeout(() => aC.closest('.field').classList.remove('is-open'), 200);
          if (gezet && vertrekVeld) {
            setTimeout(() => {
              vertrekVeld.classList.add('is-open');
              vertrekVeld.focus({ preventScroll: true });
            }, 220);
          }
        }
      });
    });

    document.querySelectorAll('.booking-card [data-field="vertrek"] [data-calendar]').forEach(vC => {
      makeCalendar(vC, {
        mode: 'single',
        getSelected: () => bookingState.vertrek,
        getMinDate: () => {
          if (!bookingState.aankomst) return today;
          const d = new Date(bookingState.aankomst);
          d.setDate(d.getDate() + 1);
          return d;
        },
        onSelect: (date) => {
          bookingState.vertrek = date;
          updateDisplay();
          setTimeout(() => vC.closest('.field').classList.remove('is-open'), 200);
        }
      });
    });

    document.querySelectorAll('.booking-bar [data-bar-field="datum"] [data-calendar]').forEach(bC => {
      makeCalendar(bC, {
        mode: 'range',
        getRange: () => [bookingState.aankomst, bookingState.vertrek],
        onSelect: (date) => {
          if (!bookingState.aankomst || (bookingState.aankomst && bookingState.vertrek)) {
            bookingState.aankomst = date;
            bookingState.vertrek = null;
          } else if (date > bookingState.aankomst) {
            bookingState.vertrek = date;
          } else {
            bookingState.aankomst = date;
            bookingState.vertrek = null;
          }
          updateDisplay();
          if (bookingState.aankomst && bookingState.vertrek) {
            setTimeout(() => bC.closest('.booking-bar__field-wrap').classList.remove('is-open'), 250);
          }
        }
      });
    });
  })();

  /* ───── Booking-toggle (desktop): snel ↔ datums ─────
     Zet data-mode op de bijbehorende booking-card. CSS toont/verbergt
     de datum-velden en past de wrap-breedte aan. */
  (() => {
    const toggles = document.querySelectorAll('[data-booking-toggle]');
    toggles.forEach(toggle => {
      const card = toggle.parentElement.querySelector('.booking-card');
      if (!card) return;
      toggle.querySelectorAll('.booking-toggle__opt').forEach(btn => {
        btn.addEventListener('click', () => {
          const mode = btn.dataset.toggle;
          card.setAttribute('data-mode', mode);
          toggle.querySelectorAll('.booking-toggle__opt').forEach(o => {
            const active = o === btn;
            o.classList.toggle('is-active', active);
            o.setAttribute('aria-selected', active ? 'true' : 'false');
          });
        });
      });
    });
  })();

  /* ───── Reisgezelschap-stepper (volwassenen / kinderen / baby's) ─────
     Per popover een eigen state. Steppers respecteren data-min en
     data-max, buttons disabled aan de grenzen. Summary-tekst valt
     terug op "volwassenen" en telt "kind/kinderen" + "baby('s)" erbij
     alleen wanneer > 0. */
  (() => {
    const popovers = document.querySelectorAll('[data-guests-popover]');
    if (!popovers.length) return;

    /* De woorden staan hier en niet in `_build/chrome/{taal}.yaml`, en dat is geen
       uitzondering maar een grens: `vertaal_chrome` vervangt tekstknopen in de HTML,
       en deze zin bestaat op dat moment nog niet — hij wordt bij elke klik opnieuw
       opgebouwd. De HTML draagt wél de juiste begintekst ("2 adults"), maar die werd
       bij het laden meteen overschreven met het Nederlands hieronder.

       Gevonden op 14-9-2026 met een render van /en/, niet met een tekstvergelijking:
       in de HTML stond het goed, dus geen enkele statische controle zag het. Alleen
       een browser die het script uitvoert laat dit zien.

       Valt terug op Nederlands als een taal ontbreekt — dan staat er iets leesbaars
       in plaats van "undefined". */
    const WOORDEN = {
      nl: { volwassene: ['volwassene', 'volwassenen'], kind: ['kind', 'kinderen'], baby: ['baby', "baby's"] },
      en: { volwassene: ['adult', 'adults'],           kind: ['child', 'children'], baby: ['baby', 'babies'] },
      de: { volwassene: ['Erwachsener', 'Erwachsene'], kind: ['Kind', 'Kinder'],    baby: ['Baby', 'Babys'] },
    };
    const taal = (document.documentElement.lang || 'nl').slice(0, 2);
    const W = WOORDEN[taal] || WOORDEN.nl;

    const plural = (n, paar) => `${n} ${n === 1 ? paar[0] : paar[1]}`;
    const summarize = (state) => {
      const parts = [plural(state.volwassenen, W.volwassene)];
      if (state.kinderen > 0) parts.push(plural(state.kinderen, W.kind));
      if (state.babys > 0)    parts.push(plural(state.babys, W.baby));
      return parts.join(', ');
    };

    popovers.forEach(pop => {
      const state = { volwassenen: 2, kinderen: 0, babys: 0 };
      const rows = pop.querySelectorAll('.guests-row');
      const summaryTarget = pop.closest('[data-field], [data-bar-field]')?.querySelector('[data-guests-summary]');

      const render = () => {
        rows.forEach(row => {
          const key = row.dataset.guestsRow;
          const min = parseInt(row.dataset.min, 10);
          const max = parseInt(row.dataset.max, 10);
          const val = state[key];
          row.querySelector('[data-guests-count]').textContent = val;
          row.querySelector('[data-step="-1"]').disabled = val <= min;
          row.querySelector('[data-step="1"]').disabled  = val >= max;
        });
        if (summaryTarget) summaryTarget.textContent = summarize(state);
      };

      rows.forEach(row => {
        const key = row.dataset.guestsRow;
        const min = parseInt(row.dataset.min, 10);
        const max = parseInt(row.dataset.max, 10);
        row.querySelectorAll('.stepper-btn').forEach(btn => {
          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const step = parseInt(btn.dataset.step, 10);
            const next = Math.min(max, Math.max(min, state[key] + step));
            state[key] = next;
            render();
          });
        });
      });

      const done = pop.querySelector('[data-guests-done]');
      if (done) {
        done.addEventListener('click', (e) => {
          e.stopPropagation();
          pop.closest('.field')?.classList.remove('is-open');
          pop.closest('.booking-bar__field-wrap')?.classList.remove('is-open');
        });
      }

      // Klik binnen popover niet laten bubbelen naar veld-toggle.
      pop.addEventListener('click', (e) => e.stopPropagation());

      render();
    });
  })();

  /* ───── Omgeving Optie B — hover op item wisselt foto + caption.
     Naast de foto-wissel updaten we ook de caption die over de foto
     verschijnt (categorie + naam). Zo weet je direct wat je ziet. */
  (() => {
    const section = document.querySelector('[data-omg-list]');
    if (!section) return;
    const photo    = section.querySelector('[data-omg-photo-target]');
    const photoWrap = photo && photo.parentElement;
    const captionEl = section.querySelector('[data-omg-caption]');
    const captionName = section.querySelector('[data-omg-caption-name]');
    const captionCat  = captionEl && captionEl.querySelector('.olc-kicker');
    const items = section.querySelectorAll('[data-omg-photo]');
    if (!photo || !items.length) return;

    const defaultSrc = photo.getAttribute('src');
    const defaultAlt = photo.getAttribute('alt');
    const defaultName = captionName ? captionName.textContent : '';
    const defaultCat  = captionCat ? captionCat.textContent : '';

    items.forEach(it => { const im = new Image(); im.src = it.dataset.omgPhoto; });

    let currentSrc = defaultSrc;
    const swap = (src, alt, name, cat) => {
      if (captionName && name != null) captionName.textContent = name;
      if (captionCat && cat != null)   captionCat.textContent  = cat;
      if (src === currentSrc) return;
      currentSrc = src;
      photoWrap.classList.add('is-swapping');
      window.setTimeout(() => {
        photo.setAttribute('src', src);
        photo.setAttribute('alt', alt || '');
        photoWrap.classList.remove('is-swapping');
      }, 180);
    };

    items.forEach(item => {
      const enter = () => {
        items.forEach(o => o.classList.toggle('is-active', o === item));
        photoWrap.classList.add('is-active');
        section.classList.add('is-hovering');
        swap(item.dataset.omgPhoto, item.dataset.omgAlt, item.querySelector('.oli-name').textContent, item.dataset.omgCat);
      };
      item.addEventListener('mouseenter', enter);
      item.addEventListener('focus', enter);
    });
    section.addEventListener('mouseleave', () => {
      items.forEach(o => o.classList.remove('is-active'));
      photoWrap.classList.remove('is-active');
      section.classList.remove('is-hovering');
      swap(defaultSrc, defaultAlt, defaultName, defaultCat);
    });
  })();


  /* ───── USP-wheel, autoplay verticale carousel ─────
     Werkt nu op alle viewports. Op smal scherm draait de wheel ook,
     in een aangepast frame (320px hoog op mobiel). */
  /* Per wiel initialiseren in plaats van één keer globaal. Stond op
     querySelector, waardoor in de styleguide alleen het eerste wiel draaide en
     het tweede blok (usp-grid) er stil bij stond. De sectie eromheen zoeken we
     nu op vanaf het wiel zelf, zodat het blok mag heten hoe het wil. */
  document.querySelectorAll('.usp-wheel-track').forEach((track) => {
    const section = track.closest('.usp-section, .usp-grid, section') || track.parentElement;
    if (!section) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const photoEl   = section.querySelector('.usp-photo');
    const layers    = photoEl ? photoEl.querySelectorAll('.usp-photo-layer') : [];
    const originals = Array.from(track.querySelectorAll('.usp-wheel-item'));
    if (!originals.length) return;
    const N = originals.length;
    const LEAD = 4, TRAIL = 4;

    for (let i = LEAD; i > 0; i--) {
      const clone = originals[N - i].cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      clone.classList.add('is-clone');
      clone.classList.remove('is-active');
      clone.removeAttribute('aria-selected');
      track.insertBefore(clone, track.firstChild);
    }
    for (let i = 0; i < TRAIL; i++) {
      const clone = originals[i].cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      clone.classList.add('is-clone');
      clone.classList.remove('is-active');
      clone.removeAttribute('aria-selected');
      track.appendChild(clone);
    }

    const allItems  = Array.from(track.querySelectorAll('.usp-wheel-item'));
    const offsetIdx = LEAD;

    originals.forEach(it => {
      const src = it.dataset.photo;
      if (src) { const im = new Image(); im.src = src; }
    });

    let activeLayer = 0;
    const setPhoto = (src) => {
      if (!layers.length || !src) return;
      const next   = 1 - activeLayer;
      const nextEl = layers[next];
      const apply  = () => {
        layers[activeLayer].classList.remove('is-active');
        nextEl.classList.add('is-active');
        activeLayer = next;
      };
      if (nextEl.src && nextEl.src.endsWith(src)) { apply(); return; }
      nextEl.src = src;
      if (nextEl.complete) apply();
      else nextEl.onload = apply;
    };

    const setActive = (absIdx) => {
      track.style.setProperty('--active', absIdx);
      allItems.forEach((it, i) => {
        const d = Math.abs(i - absIdx);
        const opacity = Math.max(0.12, 1 - d * 0.28);
        it.style.opacity = opacity.toFixed(3);
        const isCenter = i === absIdx;
        it.classList.toggle('is-active', isCenter);
        if (isCenter && !it.classList.contains('is-clone')) it.setAttribute('aria-selected', 'true');
        else                                                it.removeAttribute('aria-selected');
      });
      const realIdx = ((absIdx - offsetIdx) % N + N) % N;
      setPhoto(originals[realIdx].dataset.photo);
    };

    let active = offsetIdx;
    setActive(active);

    const TRANSITION_MS = 1000;
    const DWELL_MS      = 1400;
    const STEP_MS       = TRANSITION_MS + DWELL_MS;

    let intervalId = null;
    let snapTimer  = null;
    let paused = false;

    const step = () => {
      if (paused) return;
      active++;
      setActive(active);
      if (active === offsetIdx + N) {
        snapTimer = setTimeout(() => {
          snapTimer = null;
          track.classList.add('no-transition');
          active = offsetIdx;
          setActive(active);
          void track.offsetHeight;
          requestAnimationFrame(() => track.classList.remove('no-transition'));
        }, TRANSITION_MS + 60);
      }
    };

    const start = () => { if (!intervalId) intervalId = setInterval(step, STEP_MS); };
    const stop  = () => {
      if (intervalId) { clearInterval(intervalId); intervalId = null; }
      if (snapTimer)  { clearTimeout(snapTimer);   snapTimer  = null; }
    };

    /* Tap to pause op mobiel; resume na 4s of bij nieuwe tap */
    let resumeTimer = null;
    track.addEventListener('click', () => {
      paused = !paused;
      if (paused) {
        if (resumeTimer) clearTimeout(resumeTimer);
        resumeTimer = setTimeout(() => { paused = false; }, 4000);
      }
    });

    /* Klant-review 11-9-2026, item 14: met de pijlen stapt de gast zelf door het
       wiel. Een stap pauzeert de autoplay zes seconden — anders vecht het wiel
       terug tegen de hand die het bedient. De clones aan beide kanten (LEAD/TRAIL)
       maken een stap over de grens heen mogelijk; daarna springen we zonder
       transitie terug naar de echte positie, hetzelfde recept als `step()`.

       Stond tot 11-9-2026 alleen inline op de homepage; de knoppen zijn op
       dezelfde datum canoniek aan `statement-block` in de styleguide toegevoegd. */
    const snapNaar = (idx) => {
      track.classList.add('no-transition');
      active = idx;
      setActive(active);
      void track.offsetHeight;
      requestAnimationFrame(() => track.classList.remove('no-transition'));
    };
    const stapMet = (richting) => {
      paused = true;
      if (resumeTimer) clearTimeout(resumeTimer);
      resumeTimer = setTimeout(() => { paused = false; }, 6000);
      if (snapTimer) { clearTimeout(snapTimer); snapTimer = null; }
      active += richting;
      setActive(active);
      if (active >= offsetIdx + N) setTimeout(() => snapNaar(offsetIdx), TRANSITION_MS + 60);
      if (active <  offsetIdx)     setTimeout(() => snapNaar(offsetIdx + N - 1), TRANSITION_MS + 60);
    };
    const knopVorige = section.querySelector('[data-wheel-prev]');
    const knopVolgende = section.querySelector('[data-wheel-next]');
    if (knopVorige)   knopVorige.addEventListener('click', () => stapMet(-1));
    if (knopVolgende) knopVolgende.addEventListener('click', () => stapMet(1));

    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => e.isIntersecting ? start() : stop());
    }, { rootMargin: '200px' });
    io.observe(section);
  });

  /* ───── Interactive selector (proposities, hover/tap) ─────────────────────
     Per strip een eigen index. Stond eerder als één globale activeIdx over
     alle tegels heen; met meerdere strips (styleguide) wees die index dan naar
     een tegel in een ándere strip en bleven er twee tegels tegelijk actief. */
  document.querySelectorAll('.selector-strip').forEach((strip) => {
    const tiles = Array.from(strip.querySelectorAll('.tile'));
    if (!tiles.length) return;
    let activeIdx = Math.max(0, tiles.findIndex(t => t.classList.contains('is-active')));

    // aria-selected alleen op echte tabs: de propositietegels zijn sinds 23-10-2026 links,
    // en daar hoort dat attribuut niet (de schuifstrook op vergaderen is nog wél een tablist).
    const isTab = (t) => t.getAttribute('role') === 'tab';
    const setActive = (idx) => {
      if (idx === activeIdx) return;
      tiles[activeIdx].classList.remove('is-active');
      if (isTab(tiles[activeIdx])) tiles[activeIdx].setAttribute('aria-selected', 'false');
      tiles[idx].classList.add('is-active');
      if (isTab(tiles[idx])) tiles[idx].setAttribute('aria-selected', 'true');
      activeIdx = idx;
    };

    tiles.forEach((tile, idx) => {
      tile.addEventListener('mouseenter', () => setActive(idx));
      tile.addEventListener('focus',      () => setActive(idx));
      tile.addEventListener('click',      () => setActive(idx));
      tile.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); tiles[(idx+1)%tiles.length].focus(); }
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); tiles[(idx-1+tiles.length)%tiles.length].focus(); }
      });
    });
  });

  /* ───── Booking-card op desktop, inline popovers ───── */
  const fields = document.querySelectorAll('.booking-card .field');
  /* Sluiten binnen de eigen kaart, niet over alle kaarten heen. Op de pagina
     staat er één, maar in de styleguide staan meerdere widgets onder elkaar en
     daar sloot het openen van het ene veld de velden in een andere demo. */
  const closeAllPopovers = (scope) => {
    const binnen = scope ? scope.querySelectorAll('.field') : fields;
    binnen.forEach(f => f.classList.remove('is-open'));
  };

  fields.forEach(field => {
    const kaart = field.closest('.booking-card');
    field.addEventListener('click', (e) => {
      if (e.target.closest('.option')) return;
      const isOpen = field.classList.contains('is-open');
      closeAllPopovers(kaart);
      if (!isOpen) field.classList.add('is-open');
    });
    field.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const isOpen = field.classList.contains('is-open');
        closeAllPopovers(kaart);
        if (!isOpen) field.classList.add('is-open');
      } else if (e.key === 'Escape') {
        field.classList.remove('is-open');
      }
    });
    field.querySelectorAll('.popover .option').forEach(opt => {
      opt.addEventListener('click', (e) => {
        e.stopPropagation();
        const value = field.querySelector('.value');
        const text = Array.from(opt.childNodes)
          .filter(n => n.nodeType === 3)
          .map(n => n.textContent.trim())
          .filter(Boolean).join(' ');
        if (value) value.textContent = text || opt.textContent.trim();
        field.classList.remove('is-open');
      });
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.booking-card .field')) closeAllPopovers();
  });

  /* ───── Sticky-CTA + suite-CTA scrollen naar zichtbare booking-widget ─────
     Op mobiel/tablet: naar .booking-bar. Op desktop: naar #boeking. Één
     widget-pattern — geen sheet meer. Bij een suite-CTA klik zetten we
     de "Type"-value alvast op de aangeklikte kamer. */
  const setBookingType = (suiteName) => {
    if (!suiteName) return;
    // Desktop booking-card
    const cardTypeValue = document.querySelector('.booking-card [data-field="type"] .value');
    if (cardTypeValue) cardTypeValue.textContent = suiteName;
    // Mobiele booking-bar
    const barTypeValue = document.querySelector('.booking-bar [data-bar-field="type"] [data-bar-value]');
    if (barTypeValue) {
      barTypeValue.textContent = suiteName;
      barTypeValue.classList.remove('is-placeholder');
    }
  };

  document.querySelectorAll('[data-scroll-to-booking], [data-suite]').forEach(link => {
    /* Knoppen die naar Mews gaan zijn hierboven al afgehandeld. Zonder deze
       guard zou een kamerkaart op /kamers/ ook nog naar een #boeking-widget
       zoeken die daar niet bestaat. */
    if (link.hasAttribute('data-mews-open')) return;
    link.addEventListener('click', (e) => {
      // Prefill Type als een suite-CTA is aangeklikt
      const suite = link.getAttribute('data-suite');
      if (suite) setBookingType(suite);

      // Scroll naar de zichtbare widget (mobiel = bar, desktop = card)
      if (link.getAttribute('href') === '#boeking' || link.hasAttribute('data-scroll-to-booking')) {
        e.preventDefault();
        const target = isDesktop()
          ? document.getElementById('boeking')
          : document.getElementById('booking-bar');
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          const firstField = target.querySelector('.booking-bar__field, .booking-card .field');
          if (firstField) setTimeout(() => firstField.focus?.(), 400);
        }
      }
    });
  });

  /* ───── Mews-boekingsstraat ─────────────────────────────────────────
     Contract: output/reference/booking.md (herzien 27-8-2026).

     De Distributor draait NIET als overlay op deze site. Boeken opent een
     nieuw tabblad naar /bookingEngine, dat doorstuurt naar de door Mews
     gehoste pagina. Zo doet de huidige asteria.nl het ook, en dat is een
     bewuste klantkeuze — niet iets om "op te lossen" met een embed.

     Wat we wél meegeven: de datums en het aantal volwassenen die de gast
     hier al gekozen heeft. Nagemeten op 27-8-2026: mewsStart, mewsEnd en
     mewsAdultCount werken als URL-parameter. Kamertype NIET — mewsRooms
     doet niets, dus daar hangt bewust geen parameter aan. Zodra Mews
     bevestigt dat er wél een parameter voor bestaat, is dit de enige plek
     waar hij erbij hoeft.

     Alle knoppen die naar Mews gaan dragen [data-mews-open]. De href in de
     markup blijft /bookingEngine, zodat de link zonder JS gewoon werkt (en
     met middelklik of "openen in nieuw tabblad" ook). */
  const MEWS_ENTRY = 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556';   /* spiegel visit.asteria.nl: Mews-distributor i.p.v. /bookingEngine */

  /* Lokale datum als YYYY-MM-DD. Bewust niet toISOString(): die rekent om
     naar UTC, en dan wordt 15 september 's avonds in NL ineens de 14e. */
  const mewsIsoDate = (d) => {
    if (!(d instanceof Date) || isNaN(d)) return null;
    const p = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  };

  /* Datums komen uit de kalender-IIFE verderop, die zijn state publiceert op
     window.__asteriaBooking. Het aantal volwassenen lezen we uit de zichtbare
     stepper: card en booking-bar houden elk hun eigen teller, dus JS-state
     delen zou hier een grotere verbouwing zijn dan de DOM lezen.
     Staat er niets (zoals op /kamers/, waar geen widget is), dan gaan we
     zonder parameters — de gast kiest zijn datums dan bij Mews. */
  const mewsSnapshot = () => {
    const dates = window.__asteriaBooking || {};
    const countEl = document.querySelector('.booking-card [data-guests-row="volwassenen"] [data-guests-count]')
                 || document.querySelector('[data-guests-row="volwassenen"] [data-guests-count]');
    const volwassenen = countEl ? parseInt(countEl.textContent, 10) : NaN;
    return {
      aankomst: dates.aankomst || null,
      vertrek:  dates.vertrek  || null,
      volwassenen: Number.isFinite(volwassenen) ? volwassenen : null,
    };
  };

  const mewsUrl = () => {
    const s = mewsSnapshot();
    const params = new URLSearchParams();
    const start = mewsIsoDate(s.aankomst);
    const end   = mewsIsoDate(s.vertrek);
    if (start) params.set('mewsStart', start);
    if (end)   params.set('mewsEnd', end);
    /* Alleen meesturen als het van de default (2) afwijkt: een parameter die
       hetzelfde zegt als de default is ruis in de URL en in analytics. */
    if (s.volwassenen && s.volwassenen !== 2) params.set('mewsAdultCount', String(s.volwassenen));
    const q = params.toString();
    return q ? `${MEWS_ENTRY}?${q}` : MEWS_ENTRY;
  };

  document.querySelectorAll('[data-mews-open]').forEach(el => {
    /* Href gelijkhouden aan waar we heen gaan, zodat de statusbalk van de
       browser de waarheid toont en de link ook zonder JS werkt. */
    const href = el.getAttribute('href');
    if (el.tagName === 'A' && (!href || href === '#' || href === '#boeking')) {
      el.setAttribute('href', MEWS_ENTRY);
    }
    el.setAttribute('target', '_blank');
    el.setAttribute('rel', 'noopener');
    /* Een link die het tabblad verlaat hoort dat te melden, ook voor wie de
       knop niet ziet maar hoort. */
    if (!el.hasAttribute('aria-label')) {
      const label = (el.textContent || 'Boeken').trim();
      el.setAttribute('aria-label', `${label} — opent de boekingsmodule in een nieuw tabblad`);
    }
    el.addEventListener('click', (e) => {
      e.preventDefault();
      window.open(mewsUrl(), '_blank', 'noopener');
    });
  });

  /* ───── Submit-fallback op booking-card en booking-bar ─────
     Tot Mews live is: submit toont een eerlijke notice met bel/mail
     opties + mailto pre-filled met de gekozen velden. */
  const notice     = document.querySelector('[data-booking-notice]');
  const noticeSum  = document.querySelector('[data-booking-summary]');
  const noticeMail = document.querySelector('[data-booking-mailto]');

  const readBookingValues = () => {
    const form = document.querySelector('[data-booking-form]');
    if (!form) return null;
    const val = (field) => form.querySelector(`[data-field="${field}"] .value`)?.textContent?.trim() || '';
    return {
      aankomst: val('aankomst'),
      vertrek:  val('vertrek'),
      gasten:   val('gasten'),
      type:     val('type'),
    };
  };
  const readBarValues = () => {
    const bar = document.getElementById('booking-bar');
    if (!bar) return null;
    const val = (field) => bar.querySelector(`[data-bar-field="${field}"] [data-bar-value]`)?.textContent?.trim() || '';
    return {
      datum:  val('datum'),
      gasten: val('gasten'),
      type:   val('type'),
    };
  };

  const showNotice = (values) => {
    if (!notice) return;
    // Vul summary
    if (noticeSum) {
      const parts = Object.entries(values)
        .filter(([, v]) => v && !/^(kies|alle types)/i.test(v))
        .map(([k, v]) => `<span><strong>${k.charAt(0).toUpperCase() + k.slice(1)}:</strong>&nbsp;${v}</span>`);
      noticeSum.innerHTML = parts.length ? parts.join('') : '';
    }
    // Vul mailto met gekozen waarden
    if (noticeMail) {
      const body = Object.entries(values)
        .filter(([, v]) => v)
        .map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)}: ${v}`)
        .join('\n');
      const mailto = `mailto:info@asteria.nl?subject=${encodeURIComponent('Reserveringsaanvraag via website')}&body=${encodeURIComponent('Goedendag,\n\nIk zou graag een verblijf willen boeken met de volgende voorkeuren:\n\n' + body + '\n\nMet vriendelijke groet,\n')}`;
      noticeMail.setAttribute('href', mailto);
    }
    notice.classList.add('is-visible');
    setTimeout(() => notice.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
  };

  const bookingForm = document.querySelector('[data-booking-form]');
  if (bookingForm) {
    bookingForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const values = readBookingValues();
      if (values) showNotice(values);
    });
  }

  /* v5: booking-bar submit is nu een <a href="#" data-link="kamers" data-link-todo="niet-gebouwd" aria-disabled="true" tabindex="-1"> die naar het
     aanbod-blok navigeert (later: eigen kamer-overzichtpagina).
     Geen click-handler meer nodig — de notice-flow is dormant. */

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllPopovers();
  });

  /* ───── Generieke swipe + pagination sync (gedeeld door suite-grid en dining-grid) ───── */
  function bindSwipePagination(gridSelector, dotsSelector, currentId) {
    const grid = document.querySelector(gridSelector);
    const dots = document.querySelectorAll(dotsSelector);
    if (!grid || !dots.length) return;
    const cards = grid.children;
    const currentEl = currentId ? document.getElementById(currentId) : null;
    const setActiveDot = (idx) => {
      Array.from(dots).forEach((d, i) => {
        d.classList.toggle('is-active', i === idx);
        d.setAttribute('aria-selected', i === idx);
      });
      if (currentEl) currentEl.textContent = idx + 1;
    };
    const updateActive = () => {
      const scrollLeft = grid.scrollLeft;
      const cardWidth = cards[0] ? cards[0].offsetWidth + 16 : 1;
      const idx = Math.min(cards.length - 1, Math.round(scrollLeft / cardWidth));
      setActiveDot(idx);
    };
    grid.addEventListener('scroll', updateActive, { passive: true });
    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        if (!cards[i]) return;
        grid.scrollTo({ left: cards[i].offsetLeft - grid.offsetLeft, behavior: 'smooth' });
      });
    });
  }
  bindSwipePagination('#suite-grid', '.aanbod .pagination-dots .dot', 'suite-current');
  bindSwipePagination('#dining-grid', '.feature-deep .pagination-dots .dot', 'dining-current');
  bindSwipePagination('#arrangementen-grid', '.arrangementen .pagination-dots .dot', 'arr-current');

  /* ───── Prev/next arrows voor .aanbod carousel (overkoepelende navigatie) ───── */
  (() => {
    const grid = document.getElementById('suite-grid');
    const prev = document.querySelector('[data-suite-prev]');
    const next = document.querySelector('[data-suite-next]');
    if (!grid || !prev || !next) return;
    const cards = () => Array.from(grid.children);
    const cardStep = () => (cards()[0] ? cards()[0].offsetWidth + 16 : 400);
    const activeIdx = () => {
      const w = cardStep();
      return Math.round(grid.scrollLeft / w);
    };
    const scrollToIdx = (i) => {
      const list = cards();
      const clamped = Math.max(0, Math.min(list.length - 1, i));
      if (!list[clamped]) return;
      grid.scrollTo({ left: list[clamped].offsetLeft - grid.offsetLeft, behavior: 'smooth' });
    };
    const updateDisabled = () => {
      const i = activeIdx();
      const total = cards().length;
      prev.disabled = i <= 0;
      next.disabled = i >= total - 1;
    };
    prev.addEventListener('click', () => scrollToIdx(activeIdx() - 1));
    next.addEventListener('click', () => scrollToIdx(activeIdx() + 1));
    grid.addEventListener('scroll', updateDisabled, { passive: true });
    updateDisabled();
  })();

  /* ───── Booking-bar IntersectionObserver: sticky CTA verschijnt wanneer
     de volledige booking-bar uit beeld is gescrolld ───── */
  const bookingBar = document.getElementById('booking-bar');
  const stickyCta = document.querySelector('.book-cta-sticky');
  if (bookingBar && stickyCta) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        // Sticky verschijnt wanneer booking-bar NIET zichtbaar is
        stickyCta.classList.toggle('is-visible', !e.isIntersecting);
      });
    }, { rootMargin: '0px', threshold: 0 });
    io.observe(bookingBar);
  }

  /* ───── Booking-bar inline accordion (mobiel/tablet only) ─────
     De velden klappen lokaal uit, zonder fullscreen sheet. Eén veld
     tegelijk open. Optie-keuze sluit het veld en updatet de waarde. */
  if (bookingBar) {
    const barWraps = bookingBar.querySelectorAll('.booking-bar__field-wrap');
    barWraps.forEach(wrap => {
      const trigger = wrap.querySelector('.booking-bar__field');
      const valueEl = wrap.querySelector('[data-bar-value]');
      if (trigger) {
        trigger.addEventListener('click', () => {
          const wasOpen = wrap.classList.contains('is-open');
          barWraps.forEach(w => w.classList.remove('is-open'));
          if (!wasOpen) wrap.classList.add('is-open');
        });
      }
      wrap.querySelectorAll('.booking-bar__option').forEach(opt => {
        opt.addEventListener('click', () => {
          const text = Array.from(opt.childNodes)
            .filter(n => n.nodeType === 3)
            .map(n => n.textContent.trim())
            .filter(Boolean).join(' ') || opt.textContent.trim();
          if (valueEl) {
            valueEl.textContent = text;
            valueEl.classList.remove('is-placeholder');
          }
          wrap.classList.remove('is-open');
        });
      });
    });
    // Sluit als je buiten de booking-bar klikt
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.booking-bar')) {
        barWraps.forEach(w => w.classList.remove('is-open'));
      }
    });
  }

  /* ───── Hoofdnav dropdowns (desktop click, hover via CSS) ───── */
  document.querySelectorAll('.nav-links .has-sub').forEach(li => {
    const parent = li.querySelector('.nav-parent');
    if (!parent) return;
    parent.addEventListener('click', (e) => {
      e.stopPropagation();
      const wasOpen = li.classList.contains('is-open');
      document.querySelectorAll('.nav-links .has-sub.is-open').forEach(other => {
        if (other !== li) {
          other.classList.remove('is-open');
          other.querySelector('.nav-parent')?.setAttribute('aria-expanded', 'false');
        }
      });
      li.classList.toggle('is-open', !wasOpen);
      parent.setAttribute('aria-expanded', String(!wasOpen));
    });
  });

  // Sluit dropdowns bij klik buiten of Escape
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-links .has-sub')) {
      document.querySelectorAll('.nav-links .has-sub.is-open').forEach(li => {
        li.classList.remove('is-open');
        li.querySelector('.nav-parent')?.setAttribute('aria-expanded', 'false');
      });
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-links .has-sub.is-open').forEach(li => {
        li.classList.remove('is-open');
        li.querySelector('.nav-parent')?.setAttribute('aria-expanded', 'false');
      });
    }
  });

  /* ───── Mobile drawer accordion (parent-toggle) ───── */
  document.querySelectorAll('.nav-drawer .has-sub').forEach(li => {
    const parent = li.querySelector('.drawer-parent');
    if (!parent) return;
    parent.addEventListener('click', () => {
      const wasOpen = li.classList.contains('is-open');
      document.querySelectorAll('.nav-drawer .has-sub.is-open').forEach(other => {
        if (other !== li) {
          other.classList.remove('is-open');
          other.querySelector('.drawer-parent')?.setAttribute('aria-expanded', 'false');
        }
      });
      li.classList.toggle('is-open', !wasOpen);
      parent.setAttribute('aria-expanded', String(!wasOpen));
    });
  });

  /* ───── Mobile nav-drawer ───── */
  const drawer = document.getElementById('nav-drawer');
  document.querySelectorAll('[data-open-drawer]').forEach(b => {
    b.addEventListener('click', () => {
      if (!drawer) return;
      drawer.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    });
  });
  document.querySelectorAll('[data-close-drawer]').forEach(b => {
    b.addEventListener('click', () => {
      if (!drawer) return;
      drawer.classList.remove('is-open');
      document.body.style.overflow = '';
    });
  });
  if (drawer) {
    drawer.addEventListener('click', (e) => {
      if (e.target === drawer) {
        drawer.classList.remove('is-open');
        document.body.style.overflow = '';
      }
    });
    drawer.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        drawer.classList.remove('is-open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ───── Nieuwsbrief-submit (Formspree) ─────
     Verstuurt naar Formspree via fetch. Als het endpoint nog niet
     is ingevuld (FORMSPREE_ID placeholder), toont een demo-succes
     zodat de UX-flow zichtbaar blijft in preview. Bij ingevulde
     endpoint gaat het echte werk.

     Setup productie:
       1. Maak een Formspree-account (formspree.io)
       2. Maak een nieuw form aan, kopieer de form-ID
       3. Vervang FORMSPREE_ID in de action-URL van .newsletter__form
  */
  const nlForm    = document.querySelector('[data-newsletter-form]');
  const nlSuccess = document.querySelector('[data-newsletter-success]');
  const nlError   = document.querySelector('[data-newsletter-error]');

  if (nlForm) {
    nlForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      nlError?.classList.remove('is-visible');

      const submitBtn = nlForm.querySelector('button[type="submit"]');
      const originalLabel = submitBtn?.textContent;
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Bezig met verzenden...'; }

      const action = nlForm.getAttribute('action') || '';
      const isPlaceholder = action.includes('FORMSPREE_ID');

      const showSuccess = () => {
        nlForm.style.display = 'none';
        nlSuccess?.classList.add('is-visible');
      };
      const showError = () => {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = originalLabel; }
        nlError?.classList.add('is-visible');
      };

      if (isPlaceholder) {
        setTimeout(showSuccess, 500);
        return;
      }

      try {
        const formData = new FormData(nlForm);
        const res = await fetch(action, {
          method: 'POST',
          body: formData,
          headers: { 'Accept': 'application/json' },
        });
        if (res.ok) showSuccess();
        else        showError();
      } catch (err) {
        showError();
      }
    });
  }

  /* ───── Scroll-reveal voor arrangement-cards ─────
     Cards krijgen .is-visible zodra ze de viewport binnenkomen.
     Stagger via CSS nth-child transition-delay (0/120/240ms).
     prefers-reduced-motion valt terug op statische weergave via CSS. */
  const arrangementCards = document.querySelectorAll('.arrangement-card');
  if (arrangementCards.length) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      arrangementCards.forEach(c => c.classList.add('is-visible'));
    } else {
      const revealIO = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealIO.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
      arrangementCards.forEach(c => revealIO.observe(c));
    }
  }

  /* ───── v5 iter 11: mobiele booking-bar — vol in de hero, dockt als pill
      Drie staten, zie de CSS-sectie "v5 iter 11 · 1. BOOKING-BAR":
        .is-full                 → volledige balk in de hero (bij openen)
        .is-docked .is-collapsed → pill onderaan zodra je eroverheen scrollt
        .is-away                 → uit beeld terwijl #galerij in view is,
                                   de widget in dat blok neemt het over.
      De slot-div houdt de oorspronkelijke hoogte vast, zodat de pagina
      niet verspringt op het moment dat de balk fixed wordt. */
  (() => {
    const bar  = document.getElementById('booking-bar');
    const slot = document.getElementById('booking-bar-slot');
    const galerij = document.getElementById('galerij');
    if (!bar || !slot) return;

    const mq = window.matchMedia('(max-width: 1023px)');
    let atGalerij = false;
    let ticking = false;

    const reset = () => {
      bar.classList.remove('is-docked', 'is-collapsed', 'is-away');
      bar.classList.add('is-full');
      slot.style.minHeight = '';
    };

    const measure = () => {
      // Hoogte vastzetten vóór het docken, anders klapt de hero dicht.
      if (!bar.classList.contains('is-docked')) {
        slot.style.minHeight = bar.offsetHeight + 'px';
      }
    };

    const update = () => {
      ticking = false;
      if (!mq.matches) { reset(); return; }

      const slotRect = slot.getBoundingClientRect();
      // Gedockt zodra de onderkant van de balk voorbij de bovenrand is.
      const docked = slotRect.bottom < 8;

      if (docked) {
        measure();
        bar.classList.remove('is-full');
        bar.classList.add('is-docked', 'is-collapsed');
        // Uitklap sluiten: in pill-vorm is het veld toch verborgen.
        bar.querySelectorAll('.booking-bar__field-wrap.is-open')
           .forEach(w => w.classList.remove('is-open'));
      } else {
        bar.classList.remove('is-docked', 'is-collapsed', 'is-away');
        bar.classList.add('is-full');
      }
      bar.classList.toggle('is-away', docked && atGalerij);
    };

    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', () => { slot.style.minHeight = ''; onScroll(); });
    mq.addEventListener?.('change', () => { slot.style.minHeight = ''; update(); });

    if (galerij && 'IntersectionObserver' in window) {
      new IntersectionObserver((entries) => {
        entries.forEach(e => { atGalerij = e.isIntersecting; });
        update();
      }, { threshold: 0.2 }).observe(galerij);
    }

    update();
  })();

  /* ───── v5 iter 11: Omgeving Optie B op mobiel — scroll in plaats van hover
      De foto plakt onder de header; het bestemmings-item dat in de
      leesbaan onder die foto komt, wordt actief en wisselt de foto.
      Op desktop blijft de hover-interactie ongemoeid. */
  (() => {
    const section = document.querySelector('[data-omg-list]');
    if (!section) return;
    const items = Array.from(section.querySelectorAll('[data-omg-photo]'));
    if (!items.length) return;

    const mq = window.matchMedia('(max-width: 1023px)');
    let ticking = false;

    const sync = () => {
      ticking = false;
      if (!mq.matches) return;
      // Alleen bijwerken als de sectie daadwerkelijk in beeld is; anders
      // zou bij het laden van de pagina al een willekeurig item actief
      // worden en de standaardfoto onnodig wisselen.
      const secRect = section.getBoundingClientRect();
      if (secRect.bottom < 0 || secRect.top > window.innerHeight) return;
      const photo = section.querySelector('.omgeving-list__photo');
      if (!photo) return;
      // Leesbaan = net onder de plakkende foto.
      const line = photo.getBoundingClientRect().bottom + 80;
      let best = null, bestDist = Infinity;
      items.forEach(item => {
        const r = item.getBoundingClientRect();
        const dist = Math.abs((r.top + r.bottom) / 2 - line);
        if (dist < bestDist) { bestDist = dist; best = item; }
      });
      if (best && !best.classList.contains('is-active')) {
        best.dispatchEvent(new Event('mouseenter'));
      }
    };

    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(sync);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    sync();
  })();

  /* ───── Omgeving optie C · bento-carrousel ─────────────────────────────────
     Scrollt de bento horizontaal om de cellen te tonen die voorbij de
     rechterrand vallen. Stride is ongeveer één cluster. Pijlen gaan uit aan de
     uiteinden en verdwijnen als er niets te scrollen valt. Overgenomen uit
     output/pages/varianten-omgeving.html, waar deze variant als page-local
     script stond. */
  document.querySelectorAll('.omg-f25').forEach((section) => {
    const track = section.querySelector('.omg-f25__bento');
    const prev  = section.querySelector('[data-f25-prev]');
    const next  = section.querySelector('[data-f25-next]');
    if (!track || !prev || !next) return;

    const stride = () => {
      const cell = track.querySelector('.omg-f25__cell--tall') || track.querySelector('.omg-f25__cell');
      const gap  = parseFloat(getComputedStyle(track).columnGap || '16') || 16;
      return cell ? (cell.getBoundingClientRect().width + gap) * 2 : track.clientWidth * 0.8;
    };
    const update = () => {
      const max = track.scrollWidth - track.clientWidth;
      const scrollable = max > 4;
      prev.disabled = !scrollable || track.scrollLeft <= 2;
      next.disabled = !scrollable || track.scrollLeft >= max - 2;
    };

    prev.addEventListener('click', () => track.scrollBy({ left: -stride(), behavior: 'smooth' }));
    next.addEventListener('click', () => track.scrollBy({ left:  stride(), behavior: 'smooth' }));
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ══════════════════════════════════════════════════════════════════════════
     BLOK-INTERACTIES — canoniek hier, niet gekopieerd van de homepage
     ══════════════════════════════════════════════════════════════════════════ */

  /* ───── Filmstrip · pijlen naast een sleepbare beeldreeks ─────
     Native scroll doet het werk; de pijlen zijn een extra voor wie een muis
     heeft. Ze verschijnen daarom alleen vanaf 1024px (CSS) en de reeks werkt
     zonder JavaScript volledig — vinger, trackpad en toetsenbord scrollen ook
     als dit script er niet is.

     Zelfde opzet als de omgeving-bento onderaan dit bestand: stride uit de
     werkelijke itembreedte plus de gap, en de knoppen gaan op `disabled` aan het
     begin en het eind zodat je niet tegen een muur klikt.
  */
  document.querySelectorAll('.filmstrip-wrap').forEach((wrap) => {
    const strip = wrap.querySelector('.filmstrip');
    const prev  = wrap.querySelector('.nav-arrow.prev');
    const next  = wrap.querySelector('.nav-arrow.next');
    if (!strip || !prev || !next) return;

    /* Twee items per klik, want één item verplaatsen laat de reeks nauwelijks
       bewegen en dan lijkt de knop stuk. Valt terug op 80% van de zichtbare
       breedte als er (nog) geen item in de DOM staat. */
    const stride = () => {
      const item = strip.querySelector('.filmstrip__item');
      const gap  = parseFloat(getComputedStyle(strip).columnGap || '16') || 16;
      return item ? (item.getBoundingClientRect().width + gap) * 2 : strip.clientWidth * 0.8;
    };

    const update = () => {
      const max = strip.scrollWidth - strip.clientWidth;
      const scrollable = max > 4;
      prev.disabled = !scrollable || strip.scrollLeft <= 2;
      next.disabled = !scrollable || strip.scrollLeft >= max - 2;
    };

    prev.addEventListener('click', () => strip.scrollBy({ left: -stride(), behavior: 'smooth' }));
    next.addEventListener('click', () => strip.scrollBy({ left:  stride(), behavior: 'smooth' }));
    strip.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ───── Opstelling · schakelen tussen zaalopstellingen ─────
     Progressive enhancement, en de richting is belangrijk. De HTML bevat álle
     panelen zichtbaar: zonder JavaScript is dit de volledige capaciteitstabel —
     langer, maar compleet en leesbaar. Pas als dit script draait wordt het een
     schakelaar, en dat kondigt het aan door `.js-opstelling` op de wrapper te
     zetten (de CSS-regel die panelen verbergt hangt aan die klasse, niet aan de
     basis).

     Zo kan een pagina nooit in een staat komen waarin de gast een radio ziet die
     niets doet.
  */
  document.querySelectorAll('[data-opstelling-groep]').forEach((groep) => {
    const radios  = groep.querySelectorAll('.opstelling__radio');
    const panelen = groep.querySelectorAll('.opstelling__paneel');
    if (!radios.length || !panelen.length) return;

    groep.classList.add('js-opstelling');

    const toon = (sleutel) => {
      panelen.forEach((p) => { p.hidden = p.getAttribute('data-opstelling') !== sleutel; });
    };

    radios.forEach((r) => r.addEventListener('change', () => { if (r.checked) toon(r.value); }));
    const gekozen = groep.querySelector('.opstelling__radio:checked') || radios[0];
    gekozen.checked = true;
    toon(gekozen.value);
  });


  /* ───── Fotogalerij op een kaart · .photo--galerij ─────
     Terug uit het archief op 7-9-2026 (`git show eb0c44d`), waar dit inline in
     het kameroverzicht stond. Bij de omzetting naar `_build/compose.py` zijn de
     pagina-scripts vervallen — dit stuk is toen meegegaan, en dat was niet te
     zien aan de markup: de kaarten stonden er gewoon, alleen leeg. Reden is
     base.css: alle slides liggen op elkaar en `.photo--galerij img` staat op
     `opacity: 0` tot dit script de actieve aanwijst. Zonder script dus zeven
     kaarten met een crème vlak waar de foto hoort.

     Hier hoort het en niet in de pagina: het is een blok-interactie, de
     styleguide laadt dit bestand ook, en een tweede kopie per pagina is precies
     wat de vorige ronde ons kostte.

     Eén foto is de normale toestand zolang de beeldbank er maar één per type
     draagt. De navigatie blijft dan staan maar gaat op `aria-disabled`: hem
     weghalen zou de kaarten ongelijk maken en de pagina laten verspringen zodra
     Asteria een tweede foto levert. */
  document.querySelectorAll('.photo--galerij').forEach((galerij) => {
    const slides = Array.from(galerij.querySelectorAll('img'));
    const pijlen = Array.from(galerij.querySelectorAll('.nav-arrow'));
    let stippen  = Array.from(galerij.querySelectorAll('.photo__dot'));
    if (!slides.length) return;

    /* Stipjes horen bij slides, niet bij de sjabloonmarkup: het overschot weg. */
    stippen.slice(slides.length).forEach((s) => s.remove());
    stippen = stippen.slice(0, slides.length);

    if (slides.length < 2) {
      slides[0].classList.add('is-actief');
      pijlen.forEach((p) => { p.setAttribute('aria-disabled', 'true'); p.tabIndex = -1; });
      return;
    }

    let actief = 0;
    const toon = (n) => {
      actief = (n + slides.length) % slides.length;
      slides.forEach((img, i) => img.classList.toggle('is-actief', i === actief));
      stippen.forEach((s, i) => s.classList.toggle('is-actief', i === actief));
    };

    galerij.querySelectorAll('.nav-arrow.prev').forEach((b) =>
      b.addEventListener('click', () => toon(actief - 1)));
    galerij.querySelectorAll('.nav-arrow.next').forEach((b) =>
      b.addEventListener('click', () => toon(actief + 1)));
    stippen.forEach((s, i) => s.addEventListener('click', () => toon(i)));

    /* Pijltjestoetsen werken zodra de galerij focus heeft. */
    galerij.setAttribute('tabindex', '0');
    galerij.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft')  { toon(actief - 1); e.preventDefault(); }
      if (e.key === 'ArrowRight') { toon(actief + 1); e.preventDefault(); }
    });

    toon(0);
  });

  /* ── Galerij-lightbox ────────────────────────────────────────────────────
     Terug uit het archief op 27-8-2026 (`git show ebcc398`), waar dit inline in
     de kamerpagina stond. Hier hoort het: de styleguide laadt dit bestand ook,
     dus het blok is nu overal te bekijken zonder een tweede kopie.

     Leest alt en src van de aangeklikte foto, zodat er geen tweede lijst met
     bijschriften ontstaat die uit de pas kan lopen met de beeldbank.

     Nieuw t.o.v. het archief: vorige/volgende. Een lightbox waarin je moet
     sluiten en heropenen om de tweede foto te zien is voor een galerij van
     negen beelden geen vergroting maar een omweg. De pijlen zijn `.nav-arrow`,
     dezelfde die de carrousels gebruiken — geen tweede vorm voor hetzelfde. */
  document.querySelectorAll('.lightbox').forEach((box) => {
    const inhoud = box.querySelector('.lightbox__inhoud');
    const bijschrift = box.querySelector('.lightbox__bijschrift');
    if (!inhoud || !bijschrift) return;

    /* Het <img> wordt hier gemaakt en niet meegeleverd in de markup: een <img>
       zonder src is een gebroken beeld zodra JavaScript uitvalt. */
    const beeld = document.createElement('img');
    beeld.className = 'lightbox__beeld';
    inhoud.prepend(beeld);
    /* Een tegel zonder foto maar met een getekende plattegrond (galerij-plattegrond,
       15-10-2026): de lightbox toont een kloon van de svg, met het aria-label als bijschrift. */
    const plan = document.createElement('div');
    plan.className = 'lightbox__plan';
    plan.hidden = true;
    inhoud.prepend(plan);

    // Ook een vergrootknop in een ander beeldblok ([data-lightbox-item], 9-10-2026: de
    // schuifstrook van "Kijk rond"); het beeld zoekt hij dan in het blok eromheen.
    const knoppen = Array.from(document.querySelectorAll('.galerij__item, [data-lightbox-item]'));
    if (!knoppen.length) return;
    let index = 0;
    let herkomst = null;

    const toon = (i) => {
      index = (i + knoppen.length) % knoppen.length;   /* rondlopen, geen doodloop */
      const k = knoppen[index];
      const svg = !k.querySelector('img') && k.querySelector('svg');
      plan.hidden = !svg;
      beeld.hidden = !!svg;
      if (svg) {
        plan.replaceChildren(svg.cloneNode(true));
        bijschrift.textContent = svg.getAttribute('aria-label') || '';
        return;
      }
      const img = k.querySelector('img') || (k.closest('[data-lightbox-bron]') || k.parentElement).querySelector('img');
      if (!img) return;
      beeld.src = img.currentSrc || img.getAttribute('src') || '';
      beeld.alt = img.alt || '';
      bijschrift.textContent = (knoppen.length > 4 ? (index + 1) + ' / ' + knoppen.length + ' · ' : '') + (img.alt || '');
    };
    const open = (i) => {
      toon(i);
      box.hidden = false;
      document.body.style.overflow = 'hidden';
      box.querySelector('.lightbox__sluit').focus();
    };
    const sluit = () => {
      box.hidden = true;
      beeld.removeAttribute('src');
      document.body.style.overflow = '';
      if (herkomst) herkomst.focus();
    };

    knoppen.forEach((knop, i) => knop.addEventListener('click', () => {
      herkomst = knop;
      open(i);
    }));
    /* "Bekijk alle foto's" en "Plattegrond" (galerij-alle, 15-10-2026): openen de lightbox op
       de eerste foto of op de tekening. Het aantal foto's achter de knop telt het script. */
    const fotoTegels = knoppen.filter((k) => k.querySelector('img'));
    document.querySelectorAll('.galerij__aantal').forEach((el) => { el.textContent = '(' + fotoTegels.length + ')'; });
    document.querySelectorAll('[data-galerij-alle]').forEach((knop) => knop.addEventListener('click', () => {
      herkomst = knop;
      open(0);
    }));
    document.querySelectorAll('[data-galerij-plan]').forEach((knop) => {
      const plan = knoppen.findIndex((k) => k.classList.contains('galerij__item--plan'));
      if (plan < 0) { knop.hidden = true; return; }
      knop.addEventListener('click', () => { herkomst = knop; open(plan); });
    });
    box.addEventListener('click', (e) => {
      if (e.target === box || e.target.closest('.lightbox__sluit')) sluit();
      else if (e.target.closest('.lightbox__nav--vorige')) toon(index - 1);
      else if (e.target.closest('.lightbox__nav--volgende')) toon(index + 1);
    });
    document.addEventListener('keydown', (e) => {
      if (box.hidden) return;
      if (e.key === 'Escape') sluit();
      else if (e.key === 'ArrowLeft') toon(index - 1);
      else if (e.key === 'ArrowRight') toon(index + 1);
    });
  });


  /* ── Boekbalk ────────────────────────────────────────────────────────────
     Verschijnt zodra de boekknop bovenaan de pagina uit beeld is, en verdwijnt
     zodra die weer in beeld komt. Geen scroll-listener maar een
     IntersectionObserver op de kaart zelf: dat is één observer in plaats van
     een berekening bij elke scroll-stap, en het klopt ook als de pagina van
     hoogte verandert doordat er een accordeon opengaat.

     De balk hangt aan [data-boekbalk] en de kaart aan [data-boekbalk-anker].
     Staat het anker er niet, dan doet de balk niets — dan is er geen tweede
     knop nodig omdat de eerste nooit uit beeld gaat.

     Aan het einde van de pagina staat de afsluitende CTA; die is het anker
     niet. Zou hij dat wél zijn, dan flikkert de balk weg zodra je hem nadert
     en dat leest als een fout. */
  const boekbalk = document.querySelector('[data-boekbalk]');
  const boekanker = document.querySelector('[data-boekbalk-anker]');
  if (boekbalk && boekanker) {
    /* De balk is voor een schermlezer een herhaling van een knop die al op de
       pagina staat, dus hij hoort in de tabvolgorde maar niet als landmark. */
    const toon = (aan) => boekbalk.classList.toggle('boekbalk--show', aan);
    if ('IntersectionObserver' in window) {
      /* Alleen als de kaart BOVEN het venster is verdwenen (23-10-2026, kamertop): op een
         telefoon staat de boekkaart onder de galerij, en dan stond de balk er al bij het laden
         terwijl de kaart nog moest komen. */
      new IntersectionObserver(([e]) => toon(!e.isIntersecting && e.boundingClientRect.top < 0), {
        rootMargin: '0px 0px -40px 0px',
      }).observe(boekanker);
    } else {
      /* Zonder IntersectionObserver liever altijd tonen dan nooit: een extra
         knop is hinderlijker dan geen knop, maar veel minder erg. */
      toon(true);
    }
  }

  /* ───── Filterbalk op een kaartenraster ──────────────────────────────────
     Klant-review staging 11-9-2026, item 11: "Filter op de kamer overzicht
     pagina werkt niet."

     Dat klopte dubbel. Er was geen enkele JS voor de chips — de balk was markup
     en verder niets — en de kaarten droegen allemaal dezelfde `data-kenmerken`
     uit het styleguide-sjabloon, dus ook mét code had elk filter alle zeven
     kamers getoond. De haak per kaart is nu een kolom in `pagina/kamers.yaml`
     (compose `attr_in_item:`); dit is de bediening.

     Gedrag, zoals blok 2 van de dev-copy het beschrijft: chips zijn meervoudig
     te kiezen en weer uit te zetten. Meerdere chips is een UNIE, geen doorsnede
     — "met bad" plus "met sauna" betekent: laat me alles zien dat een van beide
     heeft. Een doorsnede levert hier bijna altijd nul kamers op, en een filter
     dat leeg oplevert leest als kapot.

     De contacttegel (`.kaart-contact`) doet niet mee: dat is geen kamertype maar
     de menselijke route, en juist als er niets past wil je hem zien. */
  document.querySelectorAll('.filterbalk').forEach((balk) => {
    const chips = Array.from(balk.querySelectorAll('[data-filter]'));
    if (!chips.length) return;

    /* Het raster hoeft niet in dezelfde container te zitten als de balk, dus
       zoeken we omhoog naar de dichtstbijzijnde sectie en dáárin het raster. */
    const wortel = balk.closest('section, .inner') || document;
    const kaarten = Array.from(wortel.querySelectorAll('[data-kenmerken]'));
    if (!kaarten.length) return;
    const telling = balk.querySelector('.filterbalk__telling');
    const sjabloon = telling ? telling.textContent.replace(/^\s*\d+\s*/, '') : 'kamertypes';

    const isAlles = (chip) => chip.dataset.filter === 'alle';
    const actief = () => chips.filter((c) => !isAlles(c) && c.getAttribute('aria-pressed') === 'true')
                              .map((c) => c.dataset.filter);

    const pas_toe = () => {
      const gekozen = actief();
      let zichtbaar = 0;
      kaarten.forEach((kaart) => {
        const heeft = (kaart.dataset.kenmerken || '').split(/\s+/).filter(Boolean);
        const toon = !gekozen.length || gekozen.some((k) => heeft.includes(k));
        kaart.hidden = !toon;
        if (toon) zichtbaar++;
      });
      /* "Alle kamers" is geen filter maar de stand waarin er niets gekozen is.
         Hij licht dus op zodra de rest uit staat. */
      chips.filter(isAlles).forEach((c) => c.setAttribute('aria-pressed', String(!gekozen.length)));
      if (telling) telling.textContent = `${zichtbaar} ${sjabloon}`.trim();
    };

    chips.forEach((chip) => {
      chip.addEventListener('click', () => {
        if (isAlles(chip)) {
          chips.forEach((c) => c.setAttribute('aria-pressed', 'false'));
        } else {
          const aan = chip.getAttribute('aria-pressed') === 'true';
          chip.setAttribute('aria-pressed', String(!aan));
        }
        pas_toe();
      });
    });

    pas_toe();
  });

  /* ───── Generieke pijlen voor een scrollende rij ──────────────────────────
     Zelfde binder als op de homepage; hier voor de samengestelde pagina's
     (items 26 en 32: opstellingen en reviews). Contract: een [data-carrousel]
     met prev/next, en een [data-carrousel-scroll] in dezelfde sectie. */
  document.querySelectorAll('[data-carrousel]').forEach((nav) => {
    const wortel = nav.closest('section') || nav.parentElement;
    const rij    = wortel && wortel.querySelector('[data-carrousel-scroll]');
    const prev   = nav.querySelector('[data-carrousel-prev]');
    const next   = nav.querySelector('[data-carrousel-next]');
    if (!rij || !prev || !next) return;
    /* De zichtbare items van de rij, en dat is niet hetzelfde als
       `rij.children`. Twee gevallen die dat breken, allebei echt voorgekomen:

       - De reviewrij bevat `.reviews-column`-wrappers die op mobiel op
         `display: contents` staan. Die hebben zélf geen doos, dus opmeten
         levert nul op en de stap wordt nul: de pijl doet dan niets.
       - De opstellingenrij begint met een visueel verborgen radio-input
         (`position: absolute`, 1×1 px). Meet je die op, dan stapt de rij één
         pixel op — wat op een aanraakscherm niet van "kapot" te onderscheiden
         is.

       Dus: overslaan wat uit de stroom is gehaald of geen breedte heeft, en
       door `display: contents` heen kijken naar de kinderen die er wél staan. */
    const items = () => {
      const gevonden = [];
      const loop = (el) => {
        for (const kind of el.children) {
          const stijl = getComputedStyle(kind);
          if (stijl.display === 'contents') { loop(kind); continue; }
          if (stijl.position === 'absolute' || stijl.position === 'fixed') continue;
          if (kind.getBoundingClientRect().width > 1) gevonden.push(kind);
        }
      };
      loop(rij);
      return gevonden;
    };

    /* Stap = de afstand tussen twee opeenvolgende items. Die meten we liever
       dan hem op te tellen uit breedte + gap: de afstand ís het antwoord, en
       hij klopt ook bij ongelijke breedtes of een gap uit een andere regel. */
    const stap = () => {
      const it = items();
      if (it.length >= 2) {
        const d = it[1].getBoundingClientRect().left - it[0].getBoundingClientRect().left;
        if (d > 1) return d;
      }
      if (it.length === 1) return it[0].getBoundingClientRect().width;
      return rij.clientWidth;
    };
    const ijk = () => {
      const max = rij.scrollWidth - rij.clientWidth;
      prev.disabled = rij.scrollLeft <= 1;
      next.disabled = rij.scrollLeft >= max - 1;
      nav.hidden = max <= 1;
    };
    prev.addEventListener('click', () => rij.scrollBy({ left: -stap(), behavior: 'smooth' }));
    next.addEventListener('click', () => rij.scrollBy({ left:  stap(), behavior: 'smooth' }));
    rij.addEventListener('scroll', ijk, { passive: true });
    window.addEventListener('resize', ijk);
    ijk();
  });


  /* ───── Taalswitcher ──────────────────────────────────────────────────────
     Items 34 en 35. De markup komt uit compose.py; dit is alleen de bediening.

     Er staan er TWEE op een pagina (topbar en mobiele drawer), elk met een
     eigen menu-id — twee keer hetzelfde `aria-controls` op één pagina zou naar
     hetzelfde element wijzen en dat is voor een schermlezer onzin. Openen sluit
     daarom altijd eerst de andere. */
  const taalknoppen = Array.from(document.querySelectorAll('[data-langswitch] .langswitch__knop'));
  if (taalknoppen.length) {
    const sluitAlles = (behalve) => {
      taalknoppen.forEach((k) => {
        if (k !== behalve) k.setAttribute('aria-expanded', 'false');
      });
    };
    taalknoppen.forEach((knop) => {
      knop.addEventListener('click', (e) => {
        e.stopPropagation();
        const open = knop.getAttribute('aria-expanded') === 'true';
        sluitAlles(knop);
        knop.setAttribute('aria-expanded', String(!open));
      });
    });
    /* Klik buiten en Escape sluiten. Escape zet de focus terug op de knop:
       zonder dat valt een toetsenbordgebruiker terug naar het begin van de
       pagina en moet hij het hele menu opnieuw door. */
    document.addEventListener('click', (e) => {
      if (!e.target.closest('[data-langswitch]')) sluitAlles(null);
    });
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      const open = taalknoppen.find((k) => k.getAttribute('aria-expanded') === 'true');
      if (!open) return;
      sluitAlles(null);
      open.focus();
    });
  }

  /* ───── Rij-uitlijning: kaarten naast elkaar lijnen uit ─────────────────────
     Klant-review 25-9-2026 (Annelieke): "is een titel 2 regels en in een blok de
     titel 1 regel, dan staat de tekst eronder in beide blokken op gelijke hoogte".
     Gemeten vóór deze regel: op de homepage stonden de titels van "Ons aanbod" op
     44 tot 77 px in de kaart en de knoppen op 324 tot 357 px; op kamers, vergaderen
     en arrangementen hetzelfde verschijnsel.

     Waarom een script en geen CSS-subgrid: de helft van deze rijen is een
     schuifrij (flex), en in de kamerkaart zit de tekst een laag dieper
     (`.content`). Subgrid dekt geen van beide. Dit meet per ZICHTBARE rij (zelfde
     top) de hoogste titel, daarna de hoogste tekst, daarna de hoogste lijst, en geeft
     de buren die hoogte als minimum. Zonder script staan de kaarten zoals ze stonden.

     Een nieuw kaartblok hoort hier in RIJEN te komen, met zijn eigen rollen. */
  const RIJEN = [
    '.suite-grid', '.pakketten', '.stappen', '.arrangementen__grid',
    '.linkband', '.tijdlijn--horizontaal', '.ovz-grid', '.featured__grid', '.featured-duo__grid'
  ];
  const ROLLEN = [
    // het label boven de titel (periode, eyebrow): breekt het in één kaart af, dan
    // zakt daar alles eronder (DE: "WEIHNACHTEN" over twee regels)
    '.tijdlijn__tijd, .eyebrow, .stap__nummer',
    'h3, .kaart-contact__title, .stap__titel, .tijdlijn__titel, .pakket__naam, .arrangement-card__title, .linkband__label, .featured__title',
    'p.body, .stap__body, .tijdlijn__body, .arrangement-card__desc, .pakket__prijs, .linkband__bij, .featured__body',
    '.suite-specs, .pakket__lijst',
    // de knoppen van een uitgelichte kaart: sloeg in één kaart een knoplabel om
    // ("More about the restaurant"), dan stond de eerste knop daar 14 px hoger (7-10-2026)
    '.featured__ctas',
    // de kaart zelf: op tablet staat hij verticaal gecentreerd over de foto, dus een
    // kaart zonder knoppen begon 24 px lager dan zijn buur (wellness, 7-10-2026)
    '.featured__card'
  ];
  // Zolang dit script draait, gaan de vaste terugvalhoogtes uit base.css eraf (een
  // kaarttekst stond vast op drie regels, een lijst op 92 px): die maten een gat
  // bij kaarten met minder tekst, en het script meet het echte maximum.
  document.documentElement.classList.add('js-rijen');
  const lijnUit = () => {
    document.querySelectorAll(RIJEN.join(',')).forEach((rij) => {
      const kaarten = Array.from(rij.children).filter((k) => k.offsetParent !== null && k.getBoundingClientRect().width > 0);
      if (kaarten.length < 2) return;
      ROLLEN.forEach((rol) => {
        const delen = kaarten.map((k) => k.querySelector(rol));
        delen.forEach((d) => { if (d) d.style.minHeight = ''; });
      });
      // groepeer per visuele rij: zelfde bovenrand = naast elkaar
      const groepen = new Map();
      kaarten.forEach((k) => {
        const top = Math.round(k.getBoundingClientRect().top + window.scrollY);
        const sleutel = [...groepen.keys()].find((t) => Math.abs(t - top) < 4);
        if (sleutel === undefined) groepen.set(top, [k]); else groepen.get(sleutel).push(k);
      });
      // Alleen kaarten van hetzelfde soort trekken we gelijk. De contacttegel naast de
      // Mindervalide kamer gaf die kaart de hoogte van zijn twee-regelige titel mee, en
      // dan stond er een gat onder "Mindervalide kamer" (15-10-2026).
      const perSoort = [];
      groepen.forEach((groep) => {
        const soorten = new Map();
        groep.forEach((k) => { const s = k.classList[0] || ''; if (!soorten.has(s)) soorten.set(s, []); soorten.get(s).push(k); });
        soorten.forEach((g) => perSoort.push(g));
      });
      perSoort.forEach((groep) => {
        if (groep.length < 2) return;
        ROLLEN.forEach((rol) => {
          const delen = groep.map((k) => k.querySelector(rol)).filter(Boolean);
          if (delen.length < 2) return;
          const max = Math.max(...delen.map((d) => d.getBoundingClientRect().height));
          delen.forEach((d) => { d.style.minHeight = max + 'px'; });
        });
      });
    });
  };
  let lijnTimer;
  const lijnLater = () => { clearTimeout(lijnTimer); lijnTimer = setTimeout(lijnUit, 120); };
  lijnUit();
  // Opnieuw meten zodra de webfonts er echt zijn. `fonts.ready` alleen is niet
  // genoeg: hij kan al vervuld zijn voordat een font gebruikt en geladen wordt, en
  // dan meet de uitlijning de bredere vervangletter (gemeten: een tekst van twee
  // regels kreeg de hoogte van drie).
  if (document.fonts) {
    if (document.fonts.ready) document.fonts.ready.then(lijnUit);
    document.fonts.addEventListener && document.fonts.addEventListener('loadingdone', lijnLater);
  }
  window.addEventListener('load', () => { lijnUit(); setTimeout(lijnUit, 600); });
  window.addEventListener('resize', lijnLater);

  /* ───── Prijswijzer: tabbladen per soort ────────────────────────────────────
     Arrangementen (25-9-2026). De tabbladen filteren de rijen van één tabel op
     `data-soort`. Zonder script staan de tabbladen verborgen (`hidden` in de markup)
     en zie je alle rijen: niets is dan onbereikbaar. De rij-uitlijning hoeft hier
     niets: het is één tabel. */
  document.querySelectorAll('.prijswijzer').forEach((blok) => {
    const lijst = blok.querySelector('.prijswijzer__tabs');
    const knoppen = lijst ? Array.from(lijst.querySelectorAll('[data-soort]')) : [];
    const rijen = Array.from(blok.querySelectorAll('tbody tr[data-soort], .keuzelijst__regel[data-soort]'));
    if (!knoppen.length || !rijen.length) return;
    const kies = (soort) => {
      knoppen.forEach((k) => k.setAttribute('aria-pressed', String(k.dataset.soort === soort)));
      rijen.forEach((r) => { r.hidden = r.dataset.soort !== soort; });
    };
    knoppen.forEach((k, i) => {
      k.addEventListener('click', () => kies(k.dataset.soort));
      k.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const volgende = knoppen[(i + (e.key === 'ArrowRight' ? 1 : -1) + knoppen.length) % knoppen.length];
        volgende.focus(); kies(volgende.dataset.soort);
      });
    });
    lijst.hidden = false;
    kies(knoppen[0].dataset.soort);
  });

  /* ───── Infovenster: een pop-up achter een i-knop ───────────────────────────
     Eerst op Arrangementen ("Zo reken je" naast de kolom Per persoon, 25-9-2026) en
     de pop-upvariant van klant-review item 30. Native <dialog>: Esc sluit, de focus
     blijft in het venster en keert terug naar de knop. Een klik op de achtergrond
     sluit ook. Zonder script staat het venster als gewoon blok op de pagina (CSS). */
  document.querySelectorAll('.infoknop[aria-controls]').forEach((knop) => {
    const venster = document.getElementById(knop.getAttribute('aria-controls'));
    if (!venster || typeof venster.showModal !== 'function') return;
    knop.addEventListener('click', () => venster.showModal());
    venster.querySelectorAll('.infovenster__sluit').forEach((s) => s.addEventListener('click', () => venster.close()));
    venster.addEventListener('click', (e) => {
      const r = venster.getBoundingClientRect();
      const buiten = e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      if (buiten) venster.close();
    });
    venster.addEventListener('close', () => knop.focus());
  });

  /* ───── Fotocarrousel in de introductie ─────────────────────────────────────
     Arrangementen (25-9-2026, Annelieke: "doorklikbaar en automatisch laten
     lopen"). Elke foto krijgt een positie ten opzichte van het midden (data-pos:
     -3 … 3); de CSS zet daar maat, plek en vervaging bij. Loopt elke 5 seconden
     door, niet bij prefers-reduced-motion en niet als het tabblad verborgen is;
     pauzeert onder de muis en bij focus. Pijlen, een klik op een zijfoto en de
     pijltjestoetsen klikken door. Zonder script staat de reeks als rij foto's. */
  document.querySelectorAll('[data-reeks]').forEach((reeks) => {
    const fotos = Array.from(reeks.querySelectorAll('img'));
    const n = fotos.length;
    if (n < 3) return;
    const sectie = reeks.closest('section') || reeks.parentElement;
    const vorige = sectie.querySelector('[data-reeks-vorige]');
    const volgende = sectie.querySelector('[data-reeks-volgende]');
    let midden = Math.floor(n / 2);
    const zet = () => {
      fotos.forEach((f, i) => {
        let o = i - midden;
        if (o > n / 2) o -= n;
        if (o < -n / 2) o += n;
        f.dataset.pos = String(o);
        f.setAttribute('aria-hidden', String(o !== 0));
      });
    };
    const ga = (stap) => { midden = (midden + stap + n) % n; zet(); };
    reeks.classList.add('is-actief');
    zet();
    fotos.forEach((f, i) => f.addEventListener('click', () => {
      const o = Number(f.dataset.pos);
      if (o !== 0 && Math.abs(o) <= 2) { midden = i; zet(); }
    }));
    if (vorige) vorige.addEventListener('click', () => ga(-1));
    if (volgende) volgende.addEventListener('click', () => ga(1));
    reeks.tabIndex = 0;
    reeks.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); ga(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); ga(-1); }
    });
    const rustig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (rustig) return;
    // Pauzeren alleen terwijl de muis óp de foto's staat, of het toetsenbord op de
    // reeks zelf. Eerder pauzeerde hij bij de hele sectie en bij elke focus, en na een
    // klik op een pijl bleef de focus staan: dan liep hij nooit meer (Annelieke 25-9).
    // Na een handmatige stap begint de telling opnieuw.
    let pauze = false;
    let timer;
    const start = () => { clearInterval(timer); timer = setInterval(() => { if (!pauze && !document.hidden) ga(1); }, 5000); };
    reeks.addEventListener('mouseenter', () => { pauze = true; });
    reeks.addEventListener('mouseleave', () => { pauze = false; });
    reeks.addEventListener('focus', () => { if (reeks.matches(':focus-visible')) pauze = true; });
    reeks.addEventListener('blur', () => { pauze = false; });
    [vorige, volgende].forEach((k) => k && k.addEventListener('click', start));
    fotos.forEach((f) => f.addEventListener('click', start));
    start();
  });

  /* ───── Opstelling met zaalkeuze · .opstelling--zaalkeuze ──────────────────
     Vergaderen (2-10-2026, klant-review 21-9, items 61, 65 en 69). Bovenop de
     gewone kiezer hierboven: elke zaalregel wordt een knop; de gekozen zaal krijgt
     zijn foto op de plek van de tekening (de tekening klein in de hoek), en de
     keuzebalk zegt wat je koos, opent de plattegrond en vult het formulier voor.
     Teksten komen uit data-attributen op de balk ([zaal] [opstelling] [n]), zodat
     ze per taal in de dev-copy staan. Zonder script blijft alles wat hier zichtbaar
     wordt op `hidden`, en zie je de gewone kiezer. */
  document.querySelectorAll('.opstelling--zaalkeuze').forEach((blok) => {
    const balk = blok.querySelector('.opstelling__keuze');
    const houder = blok.querySelector('.opstelling__fotos');
    if (!balk) return;
    const slug = (t) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    const vul = (sjabloon, w) => (sjabloon || '').replace(/\[(\w+)\]/g, (m, k) => (k in w ? w[k] : m));
    const fotoVan = (zaal) => {
      // Een samengestelde zaal ("new-york-manhattan") leent de foto van de zaal waar hij mee
      // begint: één beeld mag maar één keer op een pagina, dus geen tweede slot (9-10-2026).
      const basis = houder && !houder.querySelector(`.opstelling__zaalfoto[data-zaal="${zaal}"]`)
        ? Array.from(houder.querySelectorAll('.opstelling__zaalfoto')).map((x) => x.dataset.zaal).find((z) => zaal && zaal.startsWith(z + '-'))
        : null;
      if (basis) zaal = basis;
      const f = houder && houder.querySelector(`.opstelling__zaalfoto[data-zaal="${zaal}"]`);
      const img = f && f.querySelector('img');
      return img && img.getAttribute('src') ? f : null;
    };

    // Elke regel met een aantal wordt een knop; een regel "bieden we hier niet aan" niet.
    blok.querySelectorAll('.opstelling__rij').forEach((rij) => {
      if (!rij.querySelector('.opstelling__aantal')) { rij.classList.add('is-nvt'); return; }
      const zaalEl = rij.querySelector('.opstelling__zaal');
      const naam = (zaalEl.firstChild ? zaalEl.firstChild.textContent : zaalEl.textContent).trim();
      const knop = document.createElement('button');
      knop.type = 'button';
      knop.className = 'opstelling__kies';
      knop.dataset.zaal = slug(naam);
      knop.dataset.naam = naam;
      knop.dataset.aantal = (rij.querySelector('.opstelling__aantal').firstChild.textContent || '').trim();
      knop.setAttribute('aria-pressed', 'false');
      while (rij.firstChild) knop.appendChild(rij.firstChild);
      rij.appendChild(knop);
    });

    // Zalen zonder deze opstelling: niet als losse regels, maar één regel onderaan
    // ("Niet in deze opstelling: Maastricht, Venray"). Tekst uit data-nvt op de balk.
    blok.querySelectorAll('.opstelling__paneel').forEach((paneel) => {
      const nvt = Array.from(paneel.querySelectorAll('.opstelling__rij.is-nvt'));
      if (!nvt.length || !balk.dataset.nvt) return;
      const namen = nvt.map((r) => { const z = r.querySelector('.opstelling__zaal'); return (z.firstChild ? z.firstChild.textContent : z.textContent).trim(); });
      const lijst = nvt[0].parentElement;
      nvt.forEach((r) => r.remove());
      const samen = document.createElement('li');
      samen.className = 'opstelling__rij opstelling__rij--nvt-samen';
      samen.textContent = balk.dataset.nvt.replace('[zalen]', namen.join(', '));
      lijst.appendChild(samen);
    });

    const zaalNaam = balk.querySelector('.opstelling__gekozen-zaal');
    const zaalDetail = balk.querySelector('.opstelling__gekozen-detail');
    const venster = blok.querySelector('.zaalvenster');
    let gekozen = null;      // slug van de gekozen zaal, blijft staan bij een andere opstelling
    let stand = null;        // {zaal, naam, n, opstelling}

    const actiefPaneel = () => blok.querySelector('.opstelling__paneel:not([hidden])');
    const opstellingNaam = () => {
      const r = blok.querySelector('.opstelling__radio:checked');
      const l = r && blok.querySelector(`label[for="${r.id}"] span`);
      return l ? l.textContent.trim() : '';
    };

    const kies = (zaal) => {
      const paneel = actiefPaneel();
      if (!paneel) return;
      const knoppen = Array.from(paneel.querySelectorAll('.opstelling__kies'));
      if (!knoppen.length) return;
      const knop = knoppen.find((k) => k.dataset.zaal === zaal) || knoppen[0];
      gekozen = knop.dataset.zaal;
      blok.querySelectorAll('.opstelling__kies').forEach((k) => k.setAttribute('aria-pressed', String(k === knop)));
      // De foto naar de tekening van dít paneel; elders terug naar de houder.
      blok.querySelectorAll('.opstelling__tekening').forEach((t) => {
        t.classList.remove('heeft-foto');
        t.querySelectorAll('.opstelling__zaalfoto').forEach((f) => houder.appendChild(f));
      });
      const foto = fotoVan(gekozen);
      const tekening = paneel.querySelector('.opstelling__tekening');
      if (foto && tekening) { tekening.prepend(foto); tekening.classList.add('heeft-foto'); }
      const opst = opstellingNaam();
      stand = { zaal: knop.dataset.naam, opstelling: opst, n: knop.dataset.aantal };
      zaalNaam.textContent = knop.dataset.naam;
      zaalDetail.textContent = vul(balk.dataset.detail, stand);
    };

    blok.addEventListener('click', (e) => {
      const knop = e.target.closest('.opstelling__kies');
      if (knop) kies(knop.dataset.zaal);
    });
    blok.querySelectorAll('.opstelling__radio').forEach((r) =>
      r.addEventListener('change', () => { if (r.checked) kies(gekozen); }));

    // Plattegrond: één venster, de titel per zaal. Een plattegrond per zaal komt als
    // figure[data-zaal] in het venster; tot die er zijn toont het de algemene.
    const knopPlat = balk.querySelector('.opstelling__plattegrond');
    if (venster && knopPlat && typeof venster.showModal === 'function') {
      const titel = venster.querySelector('.infovenster__titel');
      knopPlat.addEventListener('click', () => {
        if (titel && stand) titel.textContent = vul(balk.dataset.vensterTitel, stand);
        venster.showModal();
      });
      venster.querySelectorAll('.infovenster__sluit').forEach((s) => s.addEventListener('click', () => venster.close()));
      venster.addEventListener('click', (e) => {
        const r = venster.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) venster.close();
      });
      venster.addEventListener('close', () => knopPlat.focus());
    } else if (knopPlat) {
      knopPlat.hidden = true;
    }

    // Aanvragen: de keuze gaat mee naar het formulier. Het bericht alleen invullen als
    // de bezoeker er zelf nog niets in typte; de verborgen velden zijn voor MICE.
    const aanvraag = balk.querySelector('.opstelling__aanvraag');
    if (aanvraag) aanvraag.addEventListener('click', () => {
      const doel = document.querySelector(aanvraag.getAttribute('href'));
      const form = doel && (doel.matches('form') ? doel : doel.querySelector('form'));
      if (!form || !stand) return;
      const verborgen = (naam, waarde) => {
        let veld = form.querySelector(`input[type="hidden"][name="${naam}"]`);
        if (!veld) { veld = document.createElement('input'); veld.type = 'hidden'; veld.name = naam; form.appendChild(veld); }
        veld.value = waarde;
      };
      verborgen('zaal', stand.zaal);
      verborgen('opstelling', stand.opstelling);
      const bericht = form.querySelector('textarea');
      if (bericht && (!bericht.value.trim() || bericht.dataset.voorgevuld === bericht.value)) {
        bericht.value = vul(balk.dataset.bericht, stand);
        bericht.dataset.voorgevuld = bericht.value;
      }
      const eerste = form.querySelector('input:not([type="hidden"]), select, textarea');
      if (eerste) setTimeout(() => eerste.focus({ preventScroll: true }), 450);
    });

    balk.hidden = false;
    kies(null);

    // Opstellingen als raster, de zalen in een pop-up (.opstelling--venster, 9-10-2026).
    // De tegel toont het grootste aantal uit de lijst; een klik opent de pop-up met de
    // panelen, de foto en de keuzebalk. "Met hoeveel personen?" dimt te kleine zalen en
    // kiest de kleinste die past. De aanvraagbalk in de hero opent dezelfde pop-up.
    const pop = blok.querySelector('.opstellingvenster');
    if (pop && typeof pop.showModal === 'function') {
      const titel = pop.querySelector('.opstellingvenster__titel');
      const invoer = pop.querySelector('.opstellingvenster__aantal input');
      const getal = (k) => parseInt(k.dataset.aantal, 10) || 0;
      blok.querySelectorAll('.opstelling__radio').forEach((r) => {
        const label = blok.querySelector(`label[for="${r.id}"]`);
        const paneel = blok.querySelector(`.opstelling__paneel[data-opstelling="${r.value}"]`);
        const max = Math.max(0, ...Array.from(paneel ? paneel.querySelectorAll('.opstelling__kies') : []).map(getal));
        const el = label && label.querySelector('.opstelling__label-max');
        if (el && max && blok.dataset.max) { el.textContent = blok.dataset.max.replace('[n]', max); el.hidden = false; }
        const meer = label && label.querySelector('.opstelling__label-meer');
        if (meer && blok.dataset.meer) meer.textContent = blok.dataset.meer;
      });
      const filter = () => {
        const n = invoer ? parseInt(invoer.value, 10) || 0 : 0;
        const paneel = actiefPaneel();
        if (!paneel) return;
        const knoppen = Array.from(paneel.querySelectorAll('.opstelling__kies'));
        knoppen.forEach((k) => {
          const klein = n && getal(k) < n;
          k.closest('.opstelling__rij').dataset.past = klein ? 'nee' : 'ja';
          if (klein && blok.dataset.teKlein) k.dataset.status = blok.dataset.teKlein; else delete k.dataset.status;
        });
        if (!n) return;
        const passend = knoppen.filter((k) => getal(k) >= n).sort((a, b) => getal(a) - getal(b));
        if (passend[0]) { kies(passend[0].dataset.zaal); return; }
        kies(knoppen.slice().sort((a, b) => getal(b) - getal(a))[0].dataset.zaal);
        if (balk.dataset.geenPast) zaalDetail.textContent = balk.dataset.geenPast.replace('[n]', n).replace('[opstelling]', opstellingNaam());
      };
      const open = () => { titel.textContent = opstellingNaam(); filter(); if (!pop.open) pop.showModal(); };
      blok.querySelectorAll('.opstelling__label').forEach((l) => l.addEventListener('click', () => setTimeout(open, 0)));
      blok.querySelectorAll('.opstelling__radio').forEach((r) => r.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        e.preventDefault();
        if (!r.checked) { r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); }
        open();
      }));
      if (invoer) invoer.addEventListener('input', filter);
      pop.querySelectorAll(':scope > .opstellingvenster__kop .infovenster__sluit').forEach((s) => s.addEventListener('click', () => pop.close()));
      pop.addEventListener('click', (e) => {
        if (e.target !== pop) return;
        const r = pop.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) pop.close();
      });
      // "Vraag deze zaal aan": eerst de pop-up dicht, dan naar het formulier. Een link in een
      // <dialog> die tegelijk sluit navigeert niet betrouwbaar, dus zelf scrollen.
      const aanvraagKnop = balk.querySelector('.opstelling__aanvraag');
      if (aanvraagKnop) aanvraagKnop.addEventListener('click', (e) => {
        if (!pop.open) return;
        e.preventDefault();
        pop.close();
        const doel = document.querySelector(aanvraagKnop.getAttribute('href'));
        if (doel) doel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
      });
      blok.openVenster = (n) => { if (invoer && n) invoer.value = n; open(); };
    }
  });

  /* ───── Rekenhulp · .rekenhulp in .prijstabs ────────────────────────────────
     Vergaderen (2-10-2026, Annelieke: "als button, zodat mensen hem kunnen gebruiken
     als ze dat willen"). Een knop opent een pop-up met aantal, arrangement, zaal en
     duur. Er staat GEEN prijs in dit script: de bedragen komen uit de tabbladen van
     hetzelfde blok (pakketten, zaalhuur, verblijf), dus wat de dev-copy zegt, rekent
     de hulp. Bedragen worden per taal gelezen ("€ 41,50", "€41.50", "41,50 €") en per
     taal geschreven (Intl). Zonder script blijft de knop verborgen. */
  document.querySelectorAll('.prijstabs').forEach((blok) => {
    const knop = blok.querySelector('.prijstabs__reken-knop');
    const venster = blok.querySelector('.rekenhulp');
    if (!knop || !venster || typeof venster.showModal !== 'function') return;
    const taal = (document.documentElement.lang || 'nl').slice(0, 2);
    const fmt = new Intl.NumberFormat({ en: 'en-GB', de: 'de-DE' }[taal] || 'nl-NL', { style: 'currency', currency: 'EUR' });
    const getal = (t) => {
      const m = (t || '').replace(/[^\d.,]/g, '');
      const i = Math.max(m.lastIndexOf(','), m.lastIndexOf('.'));
      if (i >= 0 && m.length - i - 1 === 2) return parseFloat(m.slice(0, i).replace(/[.,]/g, '') + '.' + m.slice(i + 1));
      return parseFloat(m.replace(/[.,]/g, ''));
    };
    const eerste = (el) => (el ? (el.firstChild ? el.firstChild.textContent : el.textContent).trim() : '');
    const klein = (t) => t.charAt(0).toLowerCase() + t.slice(1);
    const tab = (k) => { const t = blok.querySelector(`.prijstabs__tabs [data-paneel="${k}"]`); return t ? t.textContent.trim() : ''; };

    const arr = [];
    blok.querySelectorAll('#prijs-dag .pakket').forEach((p) => arr.push({
      naam: p.querySelector('.pakket__naam').textContent.trim(), pp: getal(eerste(p.querySelector('.pakket__prijs'))), zaal: true, groep: tab('dag') }));
    // Zaalhuur en verblijf staan als kaarten (2-10-2026); elke kaart draagt zijn
    // bedragen als data-rh-*, uit dezelfde dev-copy-rij als de tekst op de kaart.
    blok.querySelectorAll('#prijs-verblijf [data-rh-naam]').forEach((k) => arr.push({
      naam: k.dataset.rhNaam, pp: getal(k.dataset.rhPp), zaal: false, groep: tab('verblijf') }));
    const zalen = [];
    blok.querySelectorAll('#prijs-huur [data-rh-zaal]').forEach((k) => zalen.push({
      naam: k.dataset.rhZaal, d1: getal(k.dataset.rhD1), d2: getal(k.dataset.rhD2) }));
    if (!arr.length || !zalen.length || arr.some((a) => isNaN(a.pp)) || zalen.some((z) => isNaN(z.d1) || isNaN(z.d2))) return;

    const veld = (id) => venster.querySelector('#' + id);
    const personen = veld('rh-personen'), selArr = veld('rh-arrangement'), selZaal = veld('rh-zaal'), selDuur = veld('rh-duur');
    const duurVeld = venster.querySelector('.rekenhulp__duur');
    let groep = null;
    arr.forEach((a, i) => {
      if (a.groep !== (groep && groep.label)) { groep = document.createElement('optgroup'); groep.label = a.groep; selArr.appendChild(groep); }
      groep.appendChild(new Option(a.naam, String(i)));
    });
    zalen.forEach((z, i) => selZaal.appendChild(new Option(z.naam, String(i))));
    // Startwaarden: het voorbeeld dat eerst als tekst op de pagina stond (20, Comfort, Amsterdam, de hele dag).
    const start = arr.findIndex((a) => a.zaal && /comfort/i.test(a.naam));
    selArr.value = String(start >= 0 ? start : 0);
    const ams = zalen.findIndex((z) => /amsterdam/i.test(z.naam));
    selZaal.value = String(ams >= 0 ? ams : 0);


    const regel = (k) => venster.querySelector(`.rekenhulp__regel[data-regel="${k}"]`);
    const totaalDd = venster.querySelector('.rekenhulp__totaal dd');
    let stand = null;
    const reken = () => {
      const n = Math.max(1, parseInt(personen.value, 10) || 1);
      const a = arr[+selArr.value], z = zalen[+selZaal.value];
      const lang = selDuur.value === '1';
      const duurTekst = klein(selDuur.options[selDuur.selectedIndex].text);
      duurVeld.hidden = !a.zaal;
      const deel = n * a.pp;
      const huur = a.zaal ? (lang ? z.d1 : z.d2) : 0;
      regel('arrangement').querySelector('dt').textContent = `${n} × ${a.naam}`;
      regel('arrangement').querySelector('dd').textContent = fmt.format(deel);
      regel('zaal').querySelector('dt').textContent = (a.zaal ? venster.dataset.regelZaal : venster.dataset.regelInbegrepen)
        .replace('[zaal]', z.naam).replace('[duur]', duurTekst);
      regel('zaal').querySelector('dd').textContent = a.zaal ? fmt.format(huur) : '';
      totaalDd.textContent = fmt.format(deel + huur);
      stand = { n, arrangement: a.naam, zaal: z.naam, duur: a.zaal ? ', ' + duurTekst : '', totaal: fmt.format(deel + huur), verblijf: !a.zaal };
    };
    [personen, selArr, selZaal, selDuur].forEach((v) => { v.addEventListener('input', reken); v.addEventListener('change', reken); });

    let naarFormulier = false;
    knop.hidden = false;
    knop.addEventListener('click', () => { reken(); venster.showModal(); });
    venster.querySelectorAll('.infovenster__sluit').forEach((s) => s.addEventListener('click', () => venster.close()));
    venster.addEventListener('click', (e) => {
      const r = venster.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) venster.close();
    });
    venster.addEventListener('close', () => { if (!naarFormulier) knop.focus(); naarFormulier = false; });

    // Meenemen naar het formulier: aantal, soort (meerdaags bij een verblijf) en de som in het bericht.
    const mee = venster.querySelector('.rekenhulp__mee');
    if (mee) mee.addEventListener('click', (e) => {
      e.preventDefault();
      reken();
      const doel = document.querySelector(mee.getAttribute('href'));
      const form = doel && (doel.matches('form') ? doel : doel.querySelector('form'));
      naarFormulier = true;
      venster.close();
      // Een link in een <dialog> die tegelijk sluit, navigeert niet betrouwbaar: zelf scrollen.
      if (doel) doel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
      if (!form || !stand) return;
      const aantal = form.querySelector('input[name="personen"]');
      if (aantal) aantal.value = stand.n;
      const soort = form.querySelector('select');
      if (soort && stand.verblijf) soort.selectedIndex = soort.options.length - 1;
      const bericht = form.querySelector('textarea');
      if (bericht && (!bericht.value.trim() || bericht.dataset.voorgevuld === bericht.value)) {
        bericht.value = (venster.dataset.bericht || '').replace(/\[(\w+)\]/g, (m, k) => (k in stand ? stand[k] : m));
        bericht.dataset.voorgevuld = bericht.value;
      }
      const eersteVeld = form.querySelector('input:not([type="hidden"]), select, textarea');
      if (eersteVeld) setTimeout(() => eersteVeld.focus({ preventScroll: true }), 450);
    });
  });

  /* ───── Prijstabs · drie soorten prijs achter tabbladen ─────────────────────
     Vergaderen (2-10-2026). Wisselt hele panelen (de soorten hebben andere
     kolommen; .prijswijzer filtert rijen van één tabel). Zonder script: tabbladen
     verborgen, alle panelen onder elkaar met hun eigen kop. */
  document.querySelectorAll('.prijstabs').forEach((blok) => {
    const lijst = blok.querySelector('.prijstabs__tabs');
    const knoppen = lijst ? Array.from(lijst.querySelectorAll('[data-paneel]')) : [];
    const panelen = Array.from(blok.querySelectorAll('.prijstabs__paneel'));
    if (!knoppen.length || !panelen.length) return;
    const kies = (sleutel, focus) => {
      knoppen.forEach((k) => {
        const aan = k.dataset.paneel === sleutel;
        k.setAttribute('aria-selected', String(aan));
        k.tabIndex = aan ? 0 : -1;
        if (aan && focus) k.focus();
      });
      panelen.forEach((p) => { p.hidden = p.dataset.paneel !== sleutel; });
    };
    knoppen.forEach((k, i) => {
      k.addEventListener('click', () => kies(k.dataset.paneel));
      k.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        const v = knoppen[(i + (e.key === 'ArrowRight' ? 1 : -1) + knoppen.length) % knoppen.length];
        kies(v.dataset.paneel, true);
      });
    });
    lijst.hidden = false;
    blok.classList.add('is-actief');
    kies(knoppen[0].dataset.paneel);
  });

  /* ───── Wisselbeeld · [data-wisselbeeld] ───────────────────────────────────
     Vergaderen, "Zo loopt je dag" (9-10-2026, Annelieke: optie B, "maak hem wel zodat hij
     ook automatisch door de beelden heen gaat"). Links de foto's op elkaar, rechts de
     momenten. Hover, focus of klik op een moment toont zijn foto. Loopt vanzelf door (5 s)
     zolang het blok in beeld is; pauze met de muis of het toetsenbord op het blok, en niet
     bij prefers-reduced-motion of een verborgen tabblad (DESIGN.md §Carrousel). */
  document.querySelectorAll('[data-wisselbeeld]').forEach((blok) => {
    const items = Array.from(blok.querySelectorAll('.omgeving-list__item'));
    const fotos = Array.from(blok.querySelectorAll('.wisselbeeld__foto'));
    if (!items.length || items.length !== fotos.length) return;
    const kicker = blok.querySelector('.olc-kicker');
    const naam = blok.querySelector('.olc-name');
    const duur = 5000;
    const rustig = window.matchMedia('(prefers-reduced-motion: reduce)');
    let index = 0, klok = null, pauze = false, inBeeld = false;
    const toon = (n) => {
      index = (n + items.length) % items.length;
      items.forEach((it, k) => it.classList.toggle('is-active', k === index));
      fotos.forEach((f, k) => f.classList.toggle('is-actief', k === index));
      const it = items[index];
      if (kicker) kicker.textContent = (it.querySelector('.oli-nr') || {}).textContent || '';
      if (naam) naam.textContent = (it.querySelector('.oli-name') || {}).textContent || '';
      it.classList.remove('is-active'); void it.offsetWidth; it.classList.add('is-active');   // streepje opnieuw
    };
    const stop = () => { clearInterval(klok); klok = null; blok.classList.remove('is-auto'); };
    const start = () => {
      stop();
      if (rustig.matches || document.hidden || pauze || !inBeeld) return;
      blok.style.setProperty('--wissel-duur', duur + 'ms');
      blok.classList.add('is-auto');
      klok = setInterval(() => toon(index + 1), duur);
      toon(index);
    };
    items.forEach((it, k) => {
      it.addEventListener('mouseenter', () => toon(k));
      it.addEventListener('focus', () => toon(k));
      it.addEventListener('click', () => toon(k));
    });
    blok.addEventListener('mouseenter', () => { pauze = true; stop(); });
    blok.addEventListener('mouseleave', () => { pauze = false; start(); });
    blok.addEventListener('focusin', () => { pauze = true; stop(); });
    blok.addEventListener('focusout', (e) => { if (!blok.contains(e.relatedTarget)) { pauze = false; start(); } });
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
    toon(0);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((es) => es.forEach((e) => { inBeeld = e.isIntersecting; inBeeld ? start() : stop(); }), { threshold: 0.3 }).observe(blok);
    } else { inBeeld = true; start(); }
  });

  /* ───── Schuifstrook · een klik op de open foto vergroot hem ────────────────
     Kijk rond op vergaderen (9-10-2026). De eerste klik (of tik) schuift een foto open,
     de tweede opent de lightbox, net als het vergrootglas rechtsboven. */
  document.querySelectorAll('.schuifstrook .tile').forEach((tegel) => {
    const knop = tegel.querySelector('.tile__vergroot');
    if (!knop) return;
    let wasOpen = false;
    tegel.addEventListener('pointerdown', () => { wasOpen = tegel.classList.contains('is-active'); });
    tegel.addEventListener('click', (e) => { if (!e.target.closest('.tile__vergroot') && wasOpen) knop.click(); });
    tegel.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target === tegel) { e.preventDefault(); knop.click(); } });
  });

  /* ───── Aanvraagbalk · [data-aanvraagbalk] ──────────────────────────────────
     Vergaderen (2-10-2026, gekozen boven de snelkeuze). Aantal, opstelling en datum →
     de opstellingskiezer gaat op die opstelling staan en kiest de kleinste zaal waar de
     groep in past (past er geen, dan de grootste, met een eerlijke regel). Aantal en
     datum gaan alvast naar het offerteformulier. Geen beschikbaarheid: alleen passende
     zalen. Zonder script verstuurt het formulier niets (geen action). */
  document.querySelectorAll('[data-aanvraagbalk]').forEach((balk) => {
    const kiezer = document.querySelector('.opstelling--zaalkeuze');
    if (!kiezer) return;
    balk.addEventListener('submit', (e) => {
      e.preventDefault();
      const n = parseInt((balk.querySelector('[name="personen"]') || {}).value, 10) || 0;
      const opst = (balk.querySelector('[name="opstelling"]') || {}).value;
      const datum = ((balk.querySelector('[name="datum"]') || {}).value || '').trim();
      const radio = opst && kiezer.querySelector(`.opstelling__radio[value="${opst}"]`);
      if (radio && !radio.checked) { radio.checked = true; radio.dispatchEvent(new Event('change', { bubbles: true })); }
      const paneel = kiezer.querySelector('.opstelling__paneel:not([hidden])');
      const knoppen = paneel ? Array.from(paneel.querySelectorAll('.opstelling__kies')) : [];
      const aantal = (k) => parseInt(k.dataset.aantal, 10) || 0;
      const passend = knoppen.filter((k) => !n || aantal(k) >= n).sort((a, b) => aantal(a) - aantal(b));
      // Zonder aantal: de bovenste (grootste) zaal, zoals de kiezer uit zichzelf staat.
      const keuze = !n ? knoppen[0] : (passend[0] || knoppen.slice().sort((a, b) => aantal(b) - aantal(a))[0]);
      if (keuze) keuze.click();
      // Past niets: de detailregel van de keuzebalk zegt het.
      const detail = kiezer.querySelector('.opstelling__gekozen-detail');
      if (detail && n && !passend.length && balk.dataset.geenPast) {
        const label = radio ? (kiezer.querySelector(`label[for="${radio.id}"] span`) || {}).textContent || '' : '';
        detail.textContent = balk.dataset.geenPast.replace('[n]', n).replace('[opstelling]', label.trim());
      }
      // Alvast in het offerteformulier.
      const form = document.querySelector('#offerte form');
      if (form) {
        const p = form.querySelector('input[name="personen"]'); if (p && n) p.value = n;
        const d = form.querySelector('input[name="datum"], #fz-datum'); if (d && datum) d.value = datum;
      }
      const sectie = kiezer.closest('section') || kiezer;
      // Met de pop-up (9-10-2026): de kiezer in beeld zetten en de pop-up openen met het
      // aantal, zodat het antwoord meteen zichtbaar is in plaats van onder de vouw.
      if (typeof kiezer.openVenster === 'function') {
        sectie.scrollIntoView({ behavior: 'auto', block: 'start' });
        kiezer.openVenster(n);
        return;
      }
      sectie.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });
  });

  /* ───── Reviewstrook · sterren naar het cijfer (blok reviewstrook, 15-10-2026) ───────────
     De sterren zijn één svg met een clip over vijf sterren; de gouden balk eronder krijgt de
     breedte van het cijfer (4,2 van 5 = 84 %). Het cijfer staat als `data-score` op de svg en
     komt uit de dev-copy. Zonder script staat de breedte uit de markup, en die klopt voor 4,2. */
  document.querySelectorAll('.reviewstrook__sterren[data-score]').forEach((svg) => {
    const score = parseFloat(String(svg.dataset.score).replace(',', '.'));
    const vol = svg.querySelector('.ster-vol');
    if (vol && score > 0) vol.setAttribute('width', String(Math.min(score, 5) / 5 * 120));
  });

  /* ───── Offertebalk · springt naar het formulier en vult het alvast in (15-10-2026) ──────
     De balk in de hero van vergaderen (overhangkaart-offerte) en de knop "Vraag deze zaal
     aan" op een zaalkaart. Zonder script is de balk een gewone link naar #offerte. */
  const naarOfferte = (vul) => {
    const doel = document.getElementById('offerte');
    if (!doel) return false;
    vul(doel);
    doel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    const eerste = doel.querySelector('#fz-naam');
    if (eerste) setTimeout(() => eerste.focus({ preventScroll: true }), 700);
    return true;
  };
  document.querySelectorAll('[data-offertebalk]').forEach((balk) => {
    balk.addEventListener('submit', (e) => {
      const p = balk.querySelector('[name="personen"]');
      const d = balk.querySelector('[name="datum"]');
      const gelukt = naarOfferte((doel) => {
        const fp = doel.querySelector('#fz-personen');
        const fd = doel.querySelector('#fz-datum');
        if (fp && p && p.value) fp.value = p.value;
        if (fd && d && d.value) fd.value = d.value;
      });
      if (gelukt) e.preventDefault();
    });
  });
  document.querySelectorAll('[data-offerte-zaal]').forEach((knop) => {
    knop.addEventListener('click', (e) => {
      const zaal = knop.dataset.offerteZaal;
      const gelukt = naarOfferte((doel) => {
        const b = doel.querySelector('#fz-bericht');
        if (b && !b.value.trim()) b.value = (doel.dataset.zaalBericht || 'Ik heb interesse in zaal [zaal].').replace('[zaal]', zaal);
      });
      if (gelukt) e.preventDefault();
    });
  });

  /* ───── Kijk rond · eindeloze strook (filmstrip-uitloop, 15-10-2026) ──────────────────
     Annelieke: "foto's die niet ophouden als je links of rechts swipet". De reeks staat er
     drie keer: een kopie ervoor, het origineel, een kopie erna. Staat de strook na het
     schuiven buiten het origineel, dan springt hij precies één reeksbreedte terug, zonder
     animatie: je ziet hetzelfde beeld, en er is weer ruimte aan beide kanten. De kopieën zijn
     aria-hidden en niet focusbaar; hun vergrootglas klikt het origineel aan, zodat de lightbox
     (die zijn lijst al heeft) gewoon de goede foto opent. Dit draait na de lightbox. */
  document.querySelectorAll('.filmstrip--uitloop').forEach((strip) => {
    const items = Array.from(strip.children);
    if (items.length < 2) return;
    const kloon = (item) => {
      const k = item.cloneNode(true);
      k.setAttribute('aria-hidden', 'true');
      k.classList.add('is-kopie');
      k.removeAttribute('data-lightbox-bron');
      k.querySelectorAll('button, a').forEach((el, n) => {
        el.tabIndex = -1;
        el.addEventListener('click', (e) => {
          e.preventDefault();
          const doel = item.querySelectorAll('button, a')[n];
          if (doel) doel.click();
        });
      });
      return k;
    };
    strip.prepend(...items.map(kloon));
    strip.append(...items.map(kloon));
    const pos = (el) => el.getBoundingClientRect().left - strip.getBoundingClientRect().left + strip.scrollLeft;
    const gap = () => parseFloat(getComputedStyle(strip).columnGap) || 0;
    const reeks = () => pos(items[items.length - 1]) + items[items.length - 1].offsetWidth + gap() - pos(items[0]);
    const begin = () => pos(items[0]) - (parseFloat(getComputedStyle(strip).scrollPaddingLeft) || 0);
    const zet = (x) => {
      strip.style.scrollBehavior = 'auto';
      strip.style.scrollSnapType = 'none';
      strip.scrollLeft = x;
      requestAnimationFrame(() => { strip.style.scrollBehavior = ''; strip.style.scrollSnapType = ''; });
    };
    zet(begin());
    /* Teller "3 / 9" onder de strook (16-10-2026, Annelieke: "aanduiding van hoeveel foto's
       er zijn"). Telt alleen de originelen: de foto die het dichtst bij de linker rustplek
       staat, modulo de reeks, dus een kopie telt als zijn origineel. */
    const teller = strip.closest('.section')?.querySelector('.filmstrip__teller');
    const alle = Array.from(strip.children);
    // In de gecentreerde vorm (.cflow) telt die carrousel zelf; deze strook schuift dan niet.
    const tel = () => {
      if (!teller || strip.classList.contains('cflow')) return;
      const x = strip.scrollLeft + (parseFloat(getComputedStyle(strip).scrollPaddingLeft) || 0);
      let best = 0, afst = Infinity;
      alle.forEach((el, i) => { const d = Math.abs(pos(el) - x); if (d < afst) { afst = d; best = i; } });
      teller.textContent = ((best % items.length) + 1) + ' / ' + items.length;
    };
    tel();
    strip.addEventListener('scroll', () => requestAnimationFrame(tel), { passive: true });
    let klok;
    strip.addEventListener('scroll', () => {
      clearTimeout(klok);
      klok = setTimeout(() => {
        if (strip.classList.contains('cflow')) return;
        const w = reeks(), b = begin();
        if (strip.scrollLeft < b - w / 2) zet(strip.scrollLeft + w);
        else if (strip.scrollLeft > b + w / 2) zet(strip.scrollLeft - w);
      }, 140);
    }, { passive: true });
    window.addEventListener('resize', () => zet(begin()));
  });

  /* ───── Zaal-tabbladen (zalen-tabs, 15-10-2026) · één zaal tegelijk ───────────────────
     Progressive enhancement: zonder script staan alle zalen onder elkaar. Het script kiest
     bij het laden de eerste (de bouwer kloont de panelen uit één sjabloon, dus in de HTML
     staan ze allemaal open) en houdt de tabvolgorde op één tabblad (roving tabindex). */
  document.querySelectorAll('[data-zaaltabs]').forEach((blok) => {
    const tabs = Array.from(blok.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;
    const kies = (tab) => tabs.forEach((t) => {
      const aan = t === tab;
      t.setAttribute('aria-selected', String(aan));
      t.tabIndex = aan ? 0 : -1;
      const p = document.getElementById(t.getAttribute('aria-controls'));
      if (p) p.hidden = !aan;
    });
    kies(tabs[0]);
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => kies(t));
      t.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
        n.focus(); kies(n);
      });
    });
  });

  /* ───── Interactieve plattegrond (plattegrond-interactief, 23-10-2026, comment 40) ─────
     Nagebouwd naar wellnessasteria.nl. De lijst met plekken is de bron: elke plek draagt
     zijn positie op de tekening (`--x`, `--y` in procenten). Dit script zet per plek een
     genummerde stip op de kaart. Desktop: een klik toont die plek in het paneel ernaast
     (de lijst, met één plek tegelijk zichtbaar). Telefoon: de lijst staat onder de kaart
     en een tik op een stip springt naar de plek. Zonder script blijft het een lijst. */
  document.querySelectorAll('[data-plattegrond]').forEach((blok, b) => {
    const kaart = blok.querySelector('.plattegrond-interactief__kaart');
    const plekken = Array.from(blok.querySelectorAll('.plattegrond__plek'));
    if (!kaart || !plekken.length) return;
    blok.classList.add('js-plattegrond');
    const stippen = plekken.map((plek, i) => {
      if (!plek.id) plek.id = `plattegrond-${b}-plek-${i + 1}`;
      /* Het nummer in het paneel komt uit dit attribuut, niet uit een CSS-teller: een teller
         slaat verborgen plekken over, en op desktop is alleen de actieve plek zichtbaar. Dan stond
         er bij plek 11 een "1" (Tom, 23-10-2026). */
      plek.querySelector('.plattegrond__plek-naam')?.setAttribute('data-nr', String(i + 1));
      const st = getComputedStyle(plek);
      const knop = document.createElement('button');
      knop.type = 'button';
      knop.className = 'plattegrond__stip';
      knop.textContent = String(i + 1);
      knop.setAttribute('aria-label', plek.querySelector('.plattegrond__plek-naam')?.textContent.trim() || `Plek ${i + 1}`);
      knop.setAttribute('aria-controls', plek.id);
      knop.setAttribute('aria-pressed', 'false');
      knop.style.setProperty('--x-n', String(parseFloat(st.getPropertyValue('--x')) / 100 || 0));
      knop.style.setProperty('--y-n', String(parseFloat(st.getPropertyValue('--y')) / 100 || 0));
      kaart.appendChild(knop);
      return knop;
    });
    const kies = (i, springen) => {
      plekken.forEach((p, n) => p.classList.toggle('is-actief', n === i));
      stippen.forEach((k, n) => k.setAttribute('aria-pressed', String(n === i)));
      if (springen && !isDesktop()) plekken[i].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    kies(0, false);
    stippen.forEach((k, i) => {
      k.addEventListener('click', () => kies(i, true));
      k.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + stippen.length) % stippen.length;
        stippen[n].focus(); kies(n, false);
      });
    });
  });

})();

/* ───── Datumveld met "Nog flexibel" (26-10-2026) ────────────────────────────────────────────
   Een datum ligt nooit in het verleden, en wie "Nog flexibel" aanvinkt hoeft geen datum te
   kiezen: het datumveld gaat dan uit (en telt niet mee bij versturen). Werkt op de offertebalk
   en op het formulier; de balk geeft zijn keuze door aan het formulier. */
(() => {
  const vandaag = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  document.querySelectorAll('.field-group--datum').forEach((groep) => {
    const datum = groep.querySelector('input[type="date"]');
    const flex = groep.querySelector('.field-check input');
    if (!datum) return;
    datum.min = vandaag;
    // Leeg toont de browser "dd-mm-jjjj": in de kleur van een hint, zoals "Bijv. 40" ernaast.
    const leeg = () => datum.classList.toggle('is-leeg', !datum.value);
    datum.addEventListener('input', leeg); datum.addEventListener('change', leeg); leeg();
    if (!flex) return;
    const zet = () => { datum.disabled = flex.checked; if (flex.checked) datum.value = ''; datum.classList.toggle('is-leeg', !datum.value); };
    flex.addEventListener('change', zet);
    zet();
  });
  document.querySelectorAll('[data-offertebalk]').forEach((balk) => {
    balk.addEventListener('submit', () => {
      const bron = balk.querySelector('.field-check input');
      const doel = document.querySelector('#offerte .field-check input');
      if (!bron || !doel || doel.checked === bron.checked) return;
      doel.checked = bron.checked;
      doel.dispatchEvent(new Event('change'));
    });
  });
})();

/* ───── Carrousels: één vorm, gecentreerd (26-10-2026, Annelieke: "overal A") ─────────────────
   Zoals de introductie op arrangementen: elke kaart krijgt een positie ten opzichte van het
   midden (data-pos −3 … 3), de CSS (.cflow) zet daar maat, plek en vervaging bij. Loopt elke
   5 seconden door, niet bij reduced motion en niet in een verborgen tabblad; pauze onder de muis
   en bij toetsenbordfocus, na een klik telt hij opnieuw. Een klik op een zijkaart haalt hem naar
   het midden. De hoogte van de rij meet het script (de kaarten staan absoluut). Werkt op de
   strook (.filmstrip-wrap--midden) en op de aanbodcarrousel (.aanbod--midden). De teller
   ("3 / 5") volgt mee. Ook aan te roepen als window.asteriaCarrousel(wrap). */
(() => {
  const rustig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const zetOp = (wrap) => {
    if (!wrap || wrap.dataset.carrousel) return;
    let strip; let items; let vorige; let volgende; let teller;
    if (wrap.classList.contains('filmstrip-wrap--midden')) {
      strip = wrap.querySelector('.filmstrip');
      items = Array.from(strip.children).filter((el) => !el.classList.contains('is-kopie'));
      vorige = wrap.querySelector('.nav-arrow.prev');
      volgende = wrap.querySelector('.nav-arrow.next');
      teller = wrap.parentElement.querySelector('.filmstrip__teller');
    } else if (wrap.classList.contains('aanbod--midden')) {
      wrap = wrap.querySelector('.aanbod__carousel');
      strip = wrap.querySelector('.suite-grid');
      items = Array.from(strip.querySelectorAll(':scope > .suite-card'));
      vorige = wrap.querySelector('.aanbod__nav--prev');
      volgende = wrap.querySelector('.aanbod__nav--next');
    } else return;
    const n = items.length;
    if (n < 2) return;
    wrap.dataset.carrousel = 'midden';
    let m = 0;
    const zet = () => {
      items.forEach((el, i) => {
        let o = i - m;
        if (o > n / 2) o -= n;
        if (o < -n / 2) o += n;
        el.dataset.pos = String(o);
        el.setAttribute('aria-hidden', String(o !== 0));
        el.querySelectorAll('a, button').forEach((x) => { x.tabIndex = o === 0 ? 0 : -1; });
      });
      if (teller) teller.textContent = `${m + 1} / ${n}`;
    };
    /* De hoogte van de kaart in het midden, niet van de hoogste (feedback V4-10, 30-10-2026): op de
       telefoon is een zijkaart met meer tekst tot 150 px hoger, en dan stonden de pijlen zo ver onder
       de kaart die je ziet. Meet opnieuw bij elke wissel; de CSS laat de hoogte meeglijden. */
    const meet = () => { strip.style.height = items[m].offsetHeight + 'px'; };
    const ga = (stap) => { m = (m + stap + n) % n; zet(); meet(); };
    strip.classList.add('cflow');
    // De eindeloze strook (Kijk rond) staat al opzij geschoven; de kaarten staan nu absoluut.
    strip.scrollLeft = 0;
    strip.addEventListener('scroll', () => { if (strip.scrollLeft) strip.scrollLeft = 0; });
    zet();
    meet();
    window.addEventListener('resize', meet);
    strip.querySelectorAll('img').forEach((img) => { if (!img.complete) img.addEventListener('load', meet, { once: true }); });
    items.forEach((el, i) => el.addEventListener('click', (e) => {
      if (el.dataset.pos === '0') return;
      e.preventDefault(); e.stopPropagation(); m = i; zet(); meet(); start();
    }, true));
    // De oude knoppen schoven de rij zelf; vervangen door deze vorm.
    [vorige, volgende].forEach((k, i) => {
      if (!k) return;
      const nieuw = k.cloneNode(true);
      nieuw.disabled = false;
      nieuw.removeAttribute('hidden');
      k.replaceWith(nieuw);
      nieuw.addEventListener('click', () => { ga(i === 0 ? -1 : 1); start(); });
    });
    let pauze = false; let timer;
    const start = () => {
      clearInterval(timer);
      if (rustig) return;
      timer = setInterval(() => { if (!pauze && !document.hidden) ga(1); }, 5000);
    };
    strip.addEventListener('mouseenter', () => { pauze = true; });
    strip.addEventListener('mouseleave', () => { pauze = false; });
    strip.addEventListener('focusin', () => { pauze = true; });
    strip.addEventListener('focusout', () => { pauze = false; });
    strip.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); ga(1); start(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); ga(-1); start(); }
    });
    start();
  };
  window.asteriaCarrousel = zetOp;
  document.querySelectorAll('.filmstrip-wrap--midden, .aanbod--midden').forEach(zetOp);
})();

/* ───── Pijlen bij een paginering met bolletjes (feedback V4-10, 30-10-2026) ─────────────────
   Tom: "Als er een blok is waar je doorheen kunt swipen met hieronder bolletjes, missen de pijltjes
   dat je daar kan klikken." De arrangementen- en kamerrijen hadden op de telefoon alleen bolletjes
   (de aanbodrij had pijlen, maar die stonden onder 768 px uit). Dit script zet een pijl links en
   rechts van de bolletjes, met dezelfde knop als de andere carrousels (.carrousel-nav__knop), en
   schuift de rij één kaart op. Op het begin en het eind gaat de knop uit. Waar al zichtbare pijlen
   staan, doet het niets. */
(() => {
  const pijl = (richting) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'carrousel-nav__knop pagination__pijl';
    const taal = (document.documentElement.lang || 'nl').slice(0, 2);
    const woord = { nl: ['Vorige', 'Volgende'], en: ['Previous', 'Next'], de: ['Zurück', 'Weiter'] }[taal] || ['Vorige', 'Volgende'];
    b.setAttribute('aria-label', woord[richting < 0 ? 0 : 1]);
    b.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="${richting < 0 ? '15 18 9 12 15 6' : '9 18 15 12 9 6'}"/></svg>`;
    return b;
  };
  document.querySelectorAll('.pagination').forEach((pag) => {
    const dots = pag.querySelector('.pagination-dots');
    const sectie = pag.closest('section');
    if (!dots || !sectie || pag.querySelector('.pagination__pijl')) return;
    const rij = sectie.querySelector('.arrangementen__grid, .suite-grid, #dining-grid, [id$="-grid"]');
    if (!rij) return;
    const bestaande = [...pag.querySelectorAll('.carousel-nav')];
    if (bestaande.some((k) => k.getBoundingClientRect().width > 0)) return;
    const vorige = pijl(-1), volgende = pijl(1);
    dots.before(vorige); dots.after(volgende);
    pag.classList.add('pagination--pijlen');
    // Onder de rij, zoals bij elke carrousel. De arrangementen hadden hem in de kop, boven de kaarten.
    if (pag.compareDocumentPosition(rij) & Node.DOCUMENT_POSITION_FOLLOWING) { rij.after(pag); pag.classList.add('pagination--onder'); }
    const stap = () => {
      const k = [...rij.children].filter((c) => c.getBoundingClientRect().width > 1);
      return k.length > 1 ? k[1].getBoundingClientRect().left - k[0].getBoundingClientRect().left : rij.clientWidth;
    };
    const zet = () => {
      vorige.disabled = rij.scrollLeft <= 2;
      volgende.disabled = rij.scrollLeft + rij.clientWidth >= rij.scrollWidth - 2;
    };
    vorige.addEventListener('click', () => rij.scrollBy({ left: -stap(), behavior: 'smooth' }));
    volgende.addEventListener('click', () => rij.scrollBy({ left: stap(), behavior: 'smooth' }));
    rij.addEventListener('scroll', zet, { passive: true });
    window.addEventListener('resize', zet);
    zet();
  });
})();
