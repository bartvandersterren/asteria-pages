/* Hotel Asteria, arrangementenoverzicht (arrangementen-v2.html). Vanilla, geen externe scripts, geen localStorage.
   Port van de Parkhotel-pagina /arrangement/ (parkhotel-site src/gedrag/pagina-arrangement-v3.js, deel 1 en 2),
   met de klassenprefix ao- in plaats van ar-. Data-attributen data-ao-* zoals daar.
   1  THEMAFILTER boven de kaarten: chips (checkbox in een label), data-ao-cat mag meerdere categorieen hebben
      (spatie-gescheiden, een treffer is genoeg); Alles = reset; teller en lege melding.
   2  KEUZEHULP in twee standen: zolang niet alle vragen beantwoord zijn staan ze open; daarna (.ao-kh--klaar)
      de regel met antwoordchips [data-ao-edit] + Aanpassen [data-ao-edit-all], de aanbeveling (hoogste som van
      data-ao-score, gelijk = data-ao-order) met maximaal drie redenen in antwoordvolgorde (aangevuld met de
      vaste regel 'default' tot minstens twee) en de twee volgende als alternatief. <= 720 px: stappenmodus.
   Kop, kamers, reviews en kamer-pop-up draaien op lander-w1.js. */
/* ---- 1 themafilter --------------------------------------------------------------------- */
(function () {
	'use strict';

	function init() {
		var filter = document.querySelector('[data-ao-filter]');
		var grid = document.querySelector('[data-ao-grid]');
		var empty = document.querySelector('[data-ao-empty]');
		var counter = document.querySelector('[data-ao-count]');

		if (!filter || !grid) {
			return;
		}

		var reset = filter.querySelector('[data-ao-reset]');
		var boxes = Array.prototype.slice.call(
			filter.querySelectorAll('input[type="checkbox"][value]')
		);
		var cards = Array.prototype.slice.call(grid.querySelectorAll('[data-ao-cat]'));

		var one = filter.getAttribute('data-ao-count-one') || '%d arrangement';
		var many = filter.getAttribute('data-ao-count-many') || '%d arrangementen';

		function markLabel(box) {
			var label = box.closest('.ao-chip');
			if (label) {
				label.classList.toggle('ao-is-aan', box.checked);
			}
		}

		function apply() {
			var active = boxes.filter(function (box) {
				return box.checked;
			}).map(function (box) {
				return box.value;
			});

			// Geen enkel thema aan = alles tonen, en "Alles" weer aanvinken.
			if (reset) {
				reset.checked = active.length === 0;
				markLabel(reset);
			}

			var visible = 0;

			cards.forEach(function (card) {
				var cats = (card.getAttribute('data-ao-cat') || '').split(/\s+/);
				var show = active.length === 0 || active.some(function (a) {
					return cats.indexOf(a) !== -1;
				});
				card.hidden = !show;
				if (show) {
					visible++;
				}
			});

			boxes.forEach(markLabel);

			if (counter) {
				counter.textContent = (visible === 1 ? one : many).replace('%d', visible);
			}

			if (empty) {
				empty.hidden = visible !== 0;
			}

			grid.hidden = visible === 0;
		}

		boxes.forEach(function (box) {
			box.addEventListener('change', apply);
		});

		if (reset) {
			reset.addEventListener('change', function () {
				// "Alles" is een reset, geen toggle: uitzetten kan alleen door een thema te kiezen.
				boxes.forEach(function (box) {
					box.checked = false;
				});
				reset.checked = true;
				apply();
			});
		}

		apply();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();

/* ---- 2 keuzehulp ----------------------------------------------------------------------- */
(function () {
	'use strict';

	function list(root, sel) {
		return Array.prototype.slice.call(root.querySelectorAll(sel));
	}

	function initQuiz() {
		var quiz = document.querySelector('[data-ao-quiz]');
		if (!quiz) {
			return;
		}

		var questions = list(quiz, '[data-ao-q]');
		var results = list(quiz, '[data-ao-res]');
		var alts = list(quiz, '[data-ao-alt]');
		var progress = quiz.querySelector('[data-ao-progress]');
		var backBtn = quiz.querySelector('[data-ao-back]');
		var hint = quiz.querySelector('[data-ao-hint]');
		var result = quiz.querySelector('[data-ao-result]');
		var altsBox = quiz.querySelector('[data-ao-alts]');
		var resetBtn = quiz.querySelector('[data-ao-reset]');
		var summary = quiz.querySelector('[data-ao-summary]');
		var qBox = quiz.querySelector('[data-ao-questions]');
		var editBtns = list(quiz, '[data-ao-edit]');
		var editAll = quiz.querySelector('[data-ao-edit-all]');

		if (!questions.length || !results.length || !result) {
			return;
		}

		var stepTpl = quiz.getAttribute('data-ao-step-label') || '';
		var total = questions.length;
		var answers = {};
		var step = 0;
		var stepsMode = false;
		var editing = null; // stand 2: null (ingeklapt), 'alle' of de sleutel van een vraag

		var mq = window.matchMedia ? window.matchMedia('(max-width: 720px)') : null;

		/* Score-mapping per kaart, uit het data-attribuut. */
		var scores = {};
		results.forEach(function (el) {
			var key = el.getAttribute('data-ao-res');
			try {
				scores[key] = JSON.parse(el.getAttribute('data-ao-score') || '{}');
			} catch (e) {
				scores[key] = {};
			}
		});

		function answeredCount() {
			var n = 0;
			questions.forEach(function (q) {
				if (answers[q.getAttribute('data-ao-q')]) {
					n++;
				}
			});
			return n;
		}

		/* Antwoordwaarden in de volgorde waarin de vragen staan; die volgorde
		   bepaalt ook welke "waarom"-zinnen voorrang krijgen. */
		function answerOrder() {
			var out = [];
			questions.forEach(function (q) {
				var v = answers[q.getAttribute('data-ao-q')];
				if (v) {
					out.push(v);
				}
			});
			return out;
		}

		function renderSteps() {
			questions.forEach(function (q, i) {
				q.classList.toggle('ao-is-huidig', stepsMode && i === step);
			});

			// in stand 2 alleen bij Aanpassen (alle vragen na elkaar) voortgang en Terug tonen
			var walk = stepsMode && (answeredCount() < total || editing === 'alle');

			if (progress) {
				progress.hidden = !walk;
				if (walk) {
					progress.textContent = stepTpl
						.replace('%1$d', String(step + 1))
						.replace('%2$d', String(total));
				}
			}

			if (backBtn) {
				backBtn.hidden = !walk || step === 0;
			}
		}

		function fade(el) {
			if (!el) {
				return;
			}
			el.classList.remove('ao-is-in');
			void el.offsetWidth;
			el.classList.add('ao-is-in');
		}

		function indexOf(key) {
			for (var i = 0; i < questions.length; i++) {
				if (questions[i].getAttribute('data-ao-q') === key) {
					return i;
				}
			}
			return 0;
		}

		/* Stand 1 of stand 2, en welke vragen er in stand 2 open staan. */
		function renderView() {
			var complete = answeredCount() === total;
			if (!complete) {
				editing = null;
			}
			var single = complete && editing !== null && editing !== 'alle';

			quiz.classList.toggle('ao-kh--klaar', complete);
			quiz.classList.toggle('ao-kh--alle', complete && editing === 'alle');
			quiz.classList.toggle('ao-kh--enkel', single);

			if (summary) {
				summary.hidden = !complete;
			}
			if (qBox) {
				qBox.hidden = complete && editing === null;
			}

			questions.forEach(function (q) {
				q.classList.toggle('ao-is-dicht', !stepsMode && single && q.getAttribute('data-ao-q') !== editing);
			});

			editBtns.forEach(function (btn) {
				var key = btn.getAttribute('data-ao-edit');
				var q = quiz.querySelector('[data-ao-q="' + key + '"]');
				var on = q ? q.querySelector('.ao-chip[aria-pressed="true"]') : null;
				var txt = btn.querySelector('[data-ao-edit-text]');
				if (txt) {
					txt.textContent = on ? on.textContent.trim() : '';
				}
				btn.setAttribute('aria-expanded', String(complete && (editing === 'alle' || editing === key)));
			});

			if (editAll) {
				var allOpen = complete && editing === 'alle';
				editAll.setAttribute('aria-expanded', String(allOpen));
				editAll.textContent = editAll.getAttribute(allOpen ? 'data-ao-label-close' : 'data-ao-label-open') || editAll.textContent;
			}

			renderSteps();
		}

		function syncMode() {
			stepsMode = !!(mq && mq.matches);
			quiz.classList.toggle('ao-kh--stappen', stepsMode);
			if (step > total - 1) {
				step = total - 1;
			}
			renderView();
		}

		function showReasons(card) {
			var items = list(card, '[data-ao-reason]');
			var shown = 0;

			items.forEach(function (li) {
				li.hidden = true;
			});

			answerOrder().forEach(function (value) {
				if (shown >= 3) {
					return;
				}
				items.forEach(function (li) {
					if (shown < 3 && li.hidden && li.getAttribute('data-ao-reason') === value) {
						li.hidden = false;
						shown++;
					}
				});
			});

			// Minstens twee zinnen: aanvullen met de vaste regel van dit arrangement.
			if (shown < 2) {
				items.forEach(function (li) {
					if (shown < 2 && li.hidden && li.getAttribute('data-ao-reason') === 'default') {
						li.hidden = false;
						shown++;
					}
				});
			}
		}

		function render() {
			var complete = answeredCount() === total;

			if (hint) {
				hint.hidden = complete;
			}

			if (!complete) {
				result.hidden = true;
				result.classList.remove('ao-is-in');
				return;
			}

			var values = answerOrder();

			var ranked = results.slice().sort(function (a, b) {
				var sa = 0;
				var sb = 0;
				var ma = scores[a.getAttribute('data-ao-res')] || {};
				var mb = scores[b.getAttribute('data-ao-res')] || {};

				values.forEach(function (v) {
					sa += Number(ma[v]) || 0;
					sb += Number(mb[v]) || 0;
				});

				if (sb !== sa) {
					return sb - sa;
				}
				// Gelijke stand: de vaste volgorde uit de datafile beslist.
				return (Number(a.getAttribute('data-ao-order')) || 0) -
					(Number(b.getAttribute('data-ao-order')) || 0);
			});

			var winner = ranked[0];
			var wasHidden = result.hidden;

			results.forEach(function (el) {
				el.hidden = el !== winner;
			});
			showReasons(winner);

			var altKeys = [];
			if (ranked[1]) {
				altKeys.push(ranked[1].getAttribute('data-ao-res'));
			}
			if (ranked[2]) {
				altKeys.push(ranked[2].getAttribute('data-ao-res'));
			}

			alts.forEach(function (el) {
				el.hidden = altKeys.indexOf(el.getAttribute('data-ao-alt')) === -1;
			});

			// Volgorde van de twee alternatieven gelijktrekken met de ranking.
			if (altsBox) {
				altKeys.forEach(function (key) {
					var el = altsBox.querySelector('[data-ao-alt="' + key + '"]');
					if (el) {
						altsBox.appendChild(el);
					}
				});
			}

			result.hidden = false;
			// Reflow forceren (in fade) zodat de fade ook bij een volgende wijziging speelt.
			fade(result);

			// Net in stand 2: de vragen zijn ingeklapt en het paneel is korter geworden.
			if (wasHidden && summary) {
				fade(summary);
				var top = summary.getBoundingClientRect().top;
				if ((top < 0 || top > window.innerHeight * 0.5) && summary.scrollIntoView) {
					summary.scrollIntoView({ behavior: 'smooth', block: 'start' });
				}
			}
		}

		questions.forEach(function (q, index) {
			var key = q.getAttribute('data-ao-q');

			q.addEventListener('click', function (event) {
				var chip = event.target.closest ? event.target.closest('.ao-chip') : null;
				if (!chip || !q.contains(chip)) {
					return;
				}

				list(q, '.ao-chip').forEach(function (c) {
					c.setAttribute('aria-pressed', 'false');
				});
				chip.setAttribute('aria-pressed', 'true');
				answers[key] = chip.getAttribute('data-ao-v');

				if (editing !== null && editing !== 'alle') {
					// Stand 2, een vraag open: na het antwoord weer dicht.
					editing = null;
				} else if (editing === 'alle') {
					// Aanpassen: op het bureaublad blijven alle vier open (Klaar sluit),
					// in de stappenmodus door naar de volgende en dicht na de vierde.
					if (stepsMode) {
						if (index < total - 1) {
							step = index + 1;
						} else {
							editing = null;
						}
					}
				} else if (stepsMode && index < total - 1) {
					// Stappenflow: automatisch door naar de volgende vraag.
					step = index + 1;
				}

				renderView();
				render();
			});
		});

		if (backBtn) {
			backBtn.addEventListener('click', function () {
				if (step > 0) {
					step--;
					renderSteps();
				}
			});
		}

		editBtns.forEach(function (btn) {
			btn.addEventListener('click', function () {
				var key = btn.getAttribute('data-ao-edit');
				editing = editing === key ? null : key;
				if (editing) {
					step = indexOf(key);
				}
				renderView();
				if (editing) {
					fade(qBox);
				}
			});
		});

		if (editAll) {
			editAll.addEventListener('click', function () {
				editing = editing === 'alle' ? null : 'alle';
				if (editing) {
					step = 0;
				}
				renderView();
				if (editing) {
					fade(qBox);
				}
			});
		}

		if (resetBtn) {
			resetBtn.addEventListener('click', function () {
				answers = {};
				step = 0;
				editing = null;
				list(quiz, '.ao-chip').forEach(function (c) {
					c.setAttribute('aria-pressed', 'false');
				});
				renderView();
				render();
				var sec = quiz.closest ? (quiz.closest('section') || quiz) : quiz;
				if (sec.getBoundingClientRect().top < 0 && sec.scrollIntoView) {
					sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
				}
			});
		}

		if (mq) {
			if (mq.addEventListener) {
				mq.addEventListener('change', syncMode);
			} else if (mq.addListener) {
				mq.addListener(syncMode);
			}
		}

		syncMode();
		render();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initQuiz);
	} else {
		initQuiz();
	}
})();
