/* OuRi FX — премиальный монокром-слой: прогресс скролла, spotlight, ripple,
   scramble-декод, счётчики, кроссфейд темы. Без зависимостей, всё защищено. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement, body = doc.body;
  if (!body) return;
  var mm = function (q) { try { return window.matchMedia && window.matchMedia(q).matches; } catch (e) { return false; } };
  var reduce = mm('(prefers-reduced-motion: reduce)');
  var fine = mm('(pointer: fine)');

  /* ── 1. полоса прогресса скролла ───────────────────────────── */
  var bar = doc.createElement('div');
  bar.className = 'fx-progress'; bar.setAttribute('aria-hidden', 'true');
  body.appendChild(bar);
  var tick = false;
  function updBar() {
    tick = false;
    var h = root.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(1, Math.max(0, window.scrollY / h)) : 0;
    bar.style.transform = 'scaleX(' + p + ')';
  }
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(updBar); } }, { passive: true });
  window.addEventListener('resize', updBar, { passive: true });
  updBar();

  /* ── 2. spotlight: курсор подсвечивает карточки изнутри ────── */
  if (fine && !reduce) {
    doc.addEventListener('pointermove', function (e) {
      var t = e.target && e.target.closest ? e.target.closest('.spot') : null;
      if (!t) return;
      var r = t.getBoundingClientRect();
      t.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      t.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  /* ── 3. ripple по кнопкам ──────────────────────────────────── */
  doc.addEventListener('pointerdown', function (e) {
    if (reduce) return;
    var b = e.target && e.target.closest ? e.target.closest('.btn, .icon-btn') : null;
    if (!b || b.disabled) return;
    var r = b.getBoundingClientRect();
    var s = doc.createElement('span');
    s.className = 'fx-ripple';
    var d = Math.max(r.width, r.height) * 2.2;
    s.style.width = s.style.height = d + 'px';
    s.style.left = (e.clientX - r.left - d / 2) + 'px';
    s.style.top = (e.clientY - r.top - d / 2) + 'px';
    b.appendChild(s);
    setTimeout(function () { s.remove(); }, 700);
  }, { passive: true });

  /* ── 4. scramble-декод заголовков ──────────────────────────── */
  var CH = '#@$%&*+=<>/[]{}01';
  function scramble(node) {
    var fin = node.getAttribute('data-scramble-text') || node.textContent;
    node.setAttribute('data-scramble-text', fin);
    if (reduce) { node.textContent = fin; return; }
    var frame = 0, total = Math.max(16, fin.length * 2);
    var id = setInterval(function () {
      frame++;
      var reveal = (frame / total) * fin.length * 1.35, out = '';
      for (var i = 0; i < fin.length; i++) {
        var ch = fin.charAt(i);
        if (ch === ' ') { out += ' '; continue; }
        out += i < reveal ? ch : CH.charAt((Math.random() * CH.length) | 0);
      }
      node.textContent = out;
      if (frame >= total) { clearInterval(id); node.textContent = fin; }
    }, 34);
  }
  var sc = doc.querySelectorAll('[data-scramble]');
  if (sc.length && 'IntersectionObserver' in window) {
    var ioS = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { ioS.unobserve(en.target); scramble(en.target); } });
    }, { threshold: .35 });
    sc.forEach(function (n) { ioS.observe(n); });
  }

  /* ── 5. счётчики [data-fx-count] ───────────────────────────── */
  function count(node) {
    var to = parseFloat(node.getAttribute('data-fx-count')) || 0;
    if (reduce) { node.textContent = to.toLocaleString('ru-RU'); return; }
    var t0 = null, dur = 1400;
    function step(ts) {
      if (t0 == null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      p = 1 - Math.pow(1 - p, 3);
      node.textContent = Math.round(to * p).toLocaleString('ru-RU');
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var cn = doc.querySelectorAll('[data-fx-count]');
  if (cn.length) {
    if ('IntersectionObserver' in window) {
      var ioC = new IntersectionObserver(function (es) {
        es.forEach(function (en) { if (en.isIntersecting) { ioC.unobserve(en.target); count(en.target); } });
      }, { threshold: .5 });
      cn.forEach(function (n) { ioC.observe(n); });
    } else { cn.forEach(count); }
  }

  /* ── 6. мягкий кроссфейд при смене темы ────────────────────── */
  if ('MutationObserver' in window) {
    var mo = new MutationObserver(function () {
      root.classList.add('theme-anim');
      clearTimeout(mo._t);
      mo._t = setTimeout(function () { root.classList.remove('theme-anim'); }, 480);
    });
    mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  }
})();
