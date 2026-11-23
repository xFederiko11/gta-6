/* One task at a time. No account, cookies, tracking or gameplay assumptions.
   Without JS all original numbered steps remain readable in the HTML. */
(() => {
  'use strict';
  const tutorial = document.querySelector('#procedura.v-tutorial');
  if (!tutorial) return;
  const list = tutorial.querySelector('ol.v-steps');
  if (!list) return;
  const steps = Array.from(list.children).filter(el => el.classList.contains('v-step'));
  if (steps.length < 2) return;

  const doc = document.documentElement;
  const total = steps.length;
  const guideHeading = tutorial.querySelector('#titolo-procedura');
  if (guideHeading) guideHeading.textContent = 'FAI QUESTI PASSAGGI IN ORDINE';
  const start = tutorial.querySelector('.v-tutorial-start-here');
  if (start) start.textContent = '▶ QUESTA È LA GUIDA. SI PARTE DA QUI.';
  const explanation = tutorial.querySelector('.v-tutorial-head > p');
  if (explanation) explanation.textContent = 'Completa l’azione qui sotto, poi premi il pulsante AVANTI.';

  const status = document.createElement('div');
  status.className = 'gf-progress';
  status.innerHTML = '<div class="gf-progress-label">'
    + '<strong data-gf-status aria-live="polite">PASSO 1</strong>'
    + '<span data-gf-instruction>Una cosa per volta.</span></div>'
    + '<div class="gf-progress-track" role="progressbar" aria-label="Avanzamento della guida"'
    + ' aria-valuemin="1" aria-valuemax="' + total + '" aria-valuenow="1">'
    + '<span data-gf-fill></span></div>';
  list.before(status);

  const controls = document.createElement('nav');
  controls.className = 'gf-controls';
  controls.setAttribute('aria-label', 'Navigazione passo per passo');
  controls.innerHTML =
      '<div class="gf-actions">'
    + '<button type="button" class="gf-back" data-gf-back>← PASSO PRIMA</button>'
    + '<button type="button" class="gf-next" data-gf-next>FATTO → PASSO 2</button>'
    + '</div>'
    + '<button type="button" class="gf-all" data-gf-all>Preferisci leggere tutto? Mostra tutti i passi</button>';
  list.after(controls);
  const done = document.createElement('section');
  done.className = 'gf-done';
  done.hidden = true;
  done.innerHTML = '<h2>✅ HAI FINITO IL TUTORIAL</h2>'
    + '<p>I passaggi sono terminati. Se vuoi, sotto trovi mappe, fonti e approfondimenti. Non sono altri passi da eseguire.</p>'
    + '<button type="button" class="gf-restart" data-gf-restart>↺ Ricomincia dal passo 1</button>';
  controls.after(done);

  const back = controls.querySelector('[data-gf-back]');
  const next = controls.querySelector('[data-gf-next]');
  const showAll = controls.querySelector('[data-gf-all]');
  const mosesShowAll = tutorial.querySelector('[data-mo-show-all]');
  const restart = done.querySelector('[data-gf-restart]');
  const statusText = status.querySelector('[data-gf-status]');
  const instructions = status.querySelector('[data-gf-instruction]');
  const progress = status.querySelector('[role="progressbar"]');
  const fill = status.querySelector('[data-gf-fill]');
  const hash = window.location.hash;
  const requested = /^#passaggio-([1-9][0-9]*)$/.exec(hash);
  const alreadyComplete = hash === '#tutorial-completato';
  let current = alreadyComplete ? total - 1
    : (requested && Number(requested[1]) <= total ? Number(requested[1]) - 1 : 0);
  let all = !!hash && hash !== '#procedura' && hash !== '#inizio'
    && !requested && !alreadyComplete;
  let complete = alreadyComplete;

  function moveViewport(step, focus) {
    if (focus) {
      const title = step.querySelector('h3');
      if (title) {
        title.tabIndex = -1;
        title.focus({preventScroll: true});
      }
    }
    step.scrollIntoView({block: 'start', behavior: 'auto'});
  }

  function render(shouldScroll, focus) {
    doc.classList.toggle('guide-flow-on', true);
    doc.classList.toggle('guide-flow-all', all);
    doc.classList.toggle('guide-flow-completed', complete && !all);
    tutorial.setAttribute('data-guided-step', String(current + 1));
    tutorial.setAttribute('data-guided-total', String(total));
    steps.forEach((step, i) => {
      step.hidden = !all && i !== current;
      step.setAttribute('aria-current', !all && i === current ? 'step' : 'false');
    });

    statusText.textContent = all ? 'TUTTI I ' + total + ' PASSAGGI' : 'PASSO ' + (current + 1) + ' DI ' + total;
    instructions.textContent = all ? 'Scorri per leggere ogni passaggio.' : 'Fai questa azione. Poi premi FATTO.';
    progress.setAttribute('aria-valuenow', String(all ? total : current + 1));
    fill.style.width = ((all ? total : current + 1) * 100 / total) + '%';

    back.hidden = all || current === 0;
    next.hidden = all || complete;
    next.textContent = current === total - 1 ? '✓ HO FINITO IL TUTORIAL' : 'FATTO → PASSO ' + (current + 2);
    showAll.textContent = all ? '← Torna a un passo alla volta' : 'Preferisci leggere tutto? Mostra tutti i passi';
    if (mosesShowAll) {
      mosesShowAll.textContent = all
        ? '← Torna a un passaggio alla volta'
        : '📖 Mostra l’articolo completo (' + total + ' passaggi)';
      mosesShowAll.setAttribute('aria-pressed', String(all));
    }
    done.hidden = !complete || all;
    if (shouldScroll) {
      if (complete && !all) {
        done.scrollIntoView({block: 'center', behavior: 'auto'});
      } else if (all) {
        status.scrollIntoView({block: 'start', behavior: 'auto'});
      } else {
        moveViewport(steps[current], focus);
      }
    }
  }

  back.addEventListener('click', () => {
    if (current === 0) return;
    current -= 1;
    complete = false;
    history.replaceState(null, '', '#passaggio-' + (current + 1));
    render(true, true);
  });
  next.addEventListener('click', () => {
    if (current < total - 1) {
      current += 1;
      history.replaceState(null, '', '#passaggio-' + (current + 1));
      render(true, true);
    } else {
      complete = true;
      history.replaceState(null, '', '#tutorial-completato');
      render(true, false);
    }
  });
  if (mosesShowAll) mosesShowAll.addEventListener('click', () => {
    all = !all;
    complete = false;
    if (!all) history.replaceState(null, '', '#passaggio-' + (current + 1));
    render(true, false);
  });
  showAll.addEventListener('click', () => {
    all = !all;
    complete = false;
    if (!all) history.replaceState(null, '', '#passaggio-' + (current + 1));
    render(true, false);
  });
  restart.addEventListener('click', () => {
    current = 0;
    complete = false;
    all = false;
    history.replaceState(null, '', '#passaggio-1');
    render(true, true);
  });
  window.addEventListener('hashchange', () => {
    if (location.hash === '#tutorial-completato') {
      current = total - 1;
      all = false;
      complete = true;
      render(true, false);
      return;
    }
    const m = /^#passaggio-([1-9][0-9]*)$/.exec(location.hash);
    if (m && Number(m[1]) <= total) {
      current = Number(m[1]) - 1;
      all = false;
      complete = false;
      render(true, false);
    }
  });
  render(false, false);
})();
