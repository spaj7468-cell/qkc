/* OuRi — плашка авторов справа.
   У верха страницы раскрыта; скролл вниз — складывается в полоску и уезжает;
   скролл вверх — появляется полоской; раскрывается только у верха. */
(function () {
  var rail = document.getElementById('authorsRail');
  if (!rail) return;
  var TOP = 90;                                   /* пока hero на экране — состояние top */
  var last = window.scrollY || window.pageYOffset || 0;
  var ticking = false;
  var raf = window.requestAnimationFrame || function (f) { return setTimeout(f, 16); };

  function apply() {
    ticking = false;
    var y = window.scrollY || window.pageYOffset || 0;
    var st = rail.getAttribute('data-state') || 'top';
    if (y < TOP) {
      st = 'top';
    } else if (y > last + 6) {
      st = 'hidden';                              /* вниз: сложиться и пропасть */
    } else if (y < last - 6) {
      st = 'strip';                               /* вверх: показаться полоской */
    }
    last = y;
    if (rail.getAttribute('data-state') !== st) rail.setAttribute('data-state', st);
  }

  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; raf(apply); }
  }, { passive: true });
  apply();
})();
