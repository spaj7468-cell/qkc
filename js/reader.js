/* OuRi / QKC — экран «Литература» (хрестоматия).
   Vanilla JS, без зависимостей и сборки. Подключается в index.html после js/app.js.

   Данные: assets/lit/catalog.js задаёт window.OURI_LIT (собирает gen/lit/build_lit.py).
   Тексты: assets/lit/<страна>/<автор>.json — подгружаются по одному автору, только
           когда он открыт. В рантайме здесь ничего не проверяется на авторские
           права: всё уже отфильтровано двойным заслоном на этапе сборки, а экран
           умеет показывать только то, что лежит в собранном каталоге. */
(function () {
  'use strict';

  /* Хелперы берём из window.ouri (их экспортирует js/app.js) ЛЕНИВО, в момент
     вызова: app.js мог ещё не дойти до экспорта, а если он упал — экран
     всё равно отрисуется на собственных запасных реализациях. */
  var _esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var _el = function (tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  };
  function H() { return window.ouri || {}; }
  function t(k, vars) { var f = H().t; return f ? f(k, vars) : k; }
  function esc(s) { var f = H().esc; return f ? f(s) : _esc(s); }
  function el(tag, cls, html) { var f = H().el; return f ? f(tag, cls, html) : _el(tag, cls, html); }
  function $(s) { var f = H().$; return f ? f(s) : document.querySelector(s); }

  var CATALOG_URL = 'assets/lit/catalog.js';
  var MAX_AUTHORS = 50;          /* лимит раздела: не больше 50 авторов на страну */

  var Lit = {
    cat: null, loading: false, loaded: false, failed: false,
    country: null, author: null, work: null, q: '',
    texts: {},                   /* кэш: "страна/автор" -> объект с текстами */
    boot: function () {          /* вызывается один раз при открытии экрана */
      if (this.cat) { this.render(); return; }
      if (this.loading) return;
      if (window.OURI_LIT) { this.setCatalog(window.OURI_LIT); return; }
      this.loading = true;
      this.render();
      var self = this;
      var s = document.createElement('script');
      s.src = CATALOG_URL;
      s.onload = function () {
        self.loading = false;
        if (window.OURI_LIT) self.setCatalog(window.OURI_LIT);
        else self.fetchCatalog();
      };
      s.onerror = function () { self.loading = false; self.fetchCatalog(); };
      document.head.appendChild(s);
    },
    /* Запасной путь: тот же каталог, но JSON-ом через fetch. Нужен там, где
       динамический <script> не исполняется (например, jsdom в тестах). */
    fetchCatalog: function () {
      var self = this;
      if (!window.fetch || !/^https?:$/.test(location.protocol)) {
        this.failed = true; this.render(); return;
      }
      fetch('assets/lit/index.json', { cache: 'force-cache' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (d) self.setCatalog(d);
          else { self.failed = true; self.render(); }
        })
        .catch(function () { self.failed = true; self.render(); });
    },
    setCatalog: function (cat) {
      this.cat = cat; this.loaded = true; this.failed = false;
      var slugs = (cat.countries || []).map(function (c) { return c.slug; });
      if (slugs.indexOf(this.country) < 0) this.country = slugs[0] || null;
      this.render();
    }
  };

  function curCountry() {
    if (!Lit.cat) return null;
    var list = Lit.cat.countries || [];
    for (var i = 0; i < list.length; i++) if (list[i].slug === Lit.country) return list[i];
    return list[0] || null;
  }
  function curAuthor() {
    var c = curCountry();
    if (!c) return null;
    var list = c.authors || [];
    for (var i = 0; i < list.length; i++) if (list[i].slug === Lit.author) return list[i];
    return null;
  }
  function curWork() {
    var a = curAuthor();
    if (!a || !Lit.work) return null;
    var list = a.works || [];
    for (var i = 0; i < list.length; i++) if (list[i].slug === Lit.work) return list[i];
    return null;
  }

  /* Хэш экрана: #lit?c=russia&a=pushkin&w=nos — такие ссылки можно шарить. */
  function readHash() {
    var h = location.hash || '';
    var i = h.indexOf('?');
    if (i < 0) return;
    h.slice(i + 1).split('&').forEach(function (kv) {
      var p = kv.split('=');
      var k = p[0], v = decodeURIComponent(p[1] || '');
      if (k === 'c' && v) Lit.country = v;
      if (k === 'a') Lit.author = v || null;
      if (k === 'w') Lit.work = v || null;
    });
  }
  function writeHash() {
    var s = '#lit';
    if (Lit.country) s += '?c=' + Lit.country;
    if (Lit.author) s += '&a=' + Lit.author;
    if (Lit.work) s += '&w=' + Lit.work;
    try { if (location.hash !== s) history.replaceState(null, '', s); } catch (e) { location.hash = s; }
  }

  /* Текст произведения. Возвращает Promise: null = текста пока нет. */
  function loadTexts(country, author) {
    var key = country + '/' + author;
    if (Lit.texts[key]) return Promise.resolve(Lit.texts[key]);
    /* Под file:// (локальное открытие страницы, jsdom-тесты) fetch не работает —
       не дёргаем его, иначе консоль забьётся ошибками. Тексты всё равно подтянутся
       при следующем открытии по http(s). */
    if (!window.fetch || !/^https?:$/.test(location.protocol)) return Promise.resolve(null);
    return fetch('assets/lit/' + key + '.json', { cache: 'force-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { Lit.texts[key] = d || null; return Lit.texts[key]; })
      .catch(function () { Lit.texts[key] = null; return null; });
  }

  /* ── отрисовка ─────────────────────────────────────────────── */
  Lit.render = function () {
    var box = $('#screen-lit');
    if (!box) return;
    renderStats();
    renderCountries();
    renderRule();
    renderAuthors();
    renderWorks();
    renderExcluded();
    if (Lit.author) {
      renderReaderLoading();
      loadTexts(Lit.country, Lit.author).then(function (d) { renderReader(d); });
    } else {
      renderReader(null);
    }
  };

  function renderStats() {
    var n = $('#litStats');
    if (!n || !Lit.cat) { if (n) n.textContent = ''; return; }
    var s = Lit.cat.stats || {};
    n.textContent = t('lit.stats', { c: s.countries || 0, a: s.authors || 0, w: s.works || 0 });
  }

  function renderCountries() {
    var box = $('#litCountries');
    if (!box) return;
    box.innerHTML = '';
    if (!Lit.cat) {
      var ph = el('span', 'lit__ph');
      ph.textContent = Lit.failed ? t('lit.catalogFail') : t('lit.loading');
      box.appendChild(ph);
      return;
    }
    (Lit.cat.countries || []).forEach(function (c) {
      var b = el('button', 'chip' + (c.slug === Lit.country ? ' is-on' : ''), esc(c.name));
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', c.slug === Lit.country ? 'true' : 'false');
      b.title = c.label;
      b.onclick = function () {
        Lit.country = c.slug; Lit.author = null; Lit.work = null;
        /* Поиск сбрасываем: фильтровали по другой стране, иначе список
           встретит пользователя пустым и он решит, что каталог сломан. */
        Lit.q = '';
        var inp = $('#litSearch');
        if (inp) inp.value = '';
        writeHash(); Lit.render();
      };
      box.appendChild(b);
    });
  }

  function renderRule() {
    var box = $('#litRule');
    if (!box) return;
    var c = curCountry();
    box.innerHTML = '';
    if (!c) return;
    var p = el('p', null);
    p.textContent = c.rule || '';
    box.appendChild(p);
    if (c.authors && c.authors.length > MAX_AUTHORS) {
      var w = el('p', 'lit__warn');
      w.textContent = t('lit.tooManyAuthors');
      box.appendChild(w);
    }
  }

  function matchAuthor(a, q) {
    if (!q) return true;
    q = q.toLowerCase();
    if ((a.name || '').toLowerCase().indexOf(q) >= 0) return true;
    if ((a.orig || '').toLowerCase().indexOf(q) >= 0) return true;
    return (a.works || []).some(function (w) {
      return (w.title || '').toLowerCase().indexOf(q) >= 0 ||
             (w.orig || '').toLowerCase().indexOf(q) >= 0;
    });
  }

  function renderAuthors() {
    var box = $('#litAuthors');
    if (!box) return;
    box.innerHTML = '';
    var c = curCountry();
    if (!c) return;
    var list = (c.authors || []).filter(function (a) { return matchAuthor(a, Lit.q); });
    if (!list.length) {
      box.appendChild(el('div', 'empty', esc(t('lit.noAuthors'))));
      return;
    }
    list.forEach(function (a) {
      var on = a.slug === Lit.author;
      var b = el('button', 'lit__a' + (on ? ' is-on' : ''));
      b.type = 'button';
      b.setAttribute('role', 'listitem');
      b.setAttribute('aria-current', on ? 'true' : 'false');
      var ready = (a.works || []).filter(function (w) { return w.status === 'ok'; }).length;
      b.innerHTML =
        '<b>' + esc(a.name) + '</b>' +
        (a.orig ? '<i class="lit__orig">' + esc(a.orig) + '</i>' : '') +
        '<span class="lit__life">' + esc(a.born_str) + '–' + esc(a.died_str) + ' · ' + esc(a.era) + '</span>' +
        '<span class="lit__cnt">' + t('lit.worksN', { n: a.works_count }) +
        (ready < a.works_count ? '<em title="' + esc(t('lit.waitTranslation')) + '"> · ' + t('lit.readyN', { n: ready }) + '</em>' : '') +
        '</span>';
      b.onclick = function () {
        Lit.author = a.slug;
        Lit.work = null;
        writeHash();
        Lit.render();
      };
      box.appendChild(b);
    });
  }

  function renderWorks() {
    var box = $('#litWorks');
    if (!box) return;
    box.innerHTML = '';
    var a = curAuthor();
    if (!a) {
      box.appendChild(el('div', 'empty', esc(t('lit.pickAuthor'))));
      return;
    }
    var head = el('div', 'lit__ahead');
    head.innerHTML = '<h3>' + esc(a.name) + '</h3>' +
      '<p class="muted">' + esc(a.born_str) + '–' + esc(a.died_str) + ' · ' + esc(a.era) + '</p>' +
      (a.genres ? '<p class="lit__genres">' + esc(a.genres) + '</p>' : '') +
      '<p class="lit__bio">' + esc(a.bio) + '</p>';
    box.appendChild(head);

    (a.works || []).forEach(function (w) {
      var on = w.slug === Lit.work;
      var n = el('button', 'lit__w' + (on ? ' is-on' : '') + (w.status !== 'ok' ? ' is-wait' : ''));
      n.type = 'button';
      n.innerHTML =
        '<b>' + esc(w.title) + '</b>' +
        (w.orig ? '<i>' + esc(w.orig) + '</i>' : '') +
        '<span>' + esc(w.genre) + ' · ' + esc(w.pub_str) +
        (w.conf === 'chk' ? ' <em title="' + esc(t('lit.dateUnverified')) + '">' + esc(t('lit.dateUnverifiedShort')) + '</em>' : '') +
        '</span>' +
        (w.status !== 'ok' ? '<span class="lit__badge">' + esc(t('lit.waitTranslation')) + '</span>' : '');
      n.onclick = function () {
        Lit.work = on ? null : w.slug;
        writeHash();
        Lit.render();
      };
      box.appendChild(n);
    });
  }

  function renderReaderLoading() {
    var box = $('#litReader');
    if (!box || !Lit.work) return;
    box.innerHTML = '';
    box.appendChild(el('div', 'lit__ph', esc(t('lit.loadingText'))));
  }

  function renderReader(texts) {
    var box = $('#litReader');
    if (!box) return;
    box.innerHTML = '';
    var a = curAuthor(), w = curWork();
    if (!a) return;
    if (!w) {
      box.appendChild(el('div', 'lit__hint', esc(t('lit.pickWork'))));
      return;
    }

    var art = el('article', 'lit__art');
    art.id = 'lit-article';
    var h = el('h3');
    h.textContent = w.title;
    art.appendChild(h);
    var meta = el('p', 'lit__ameta');
    meta.textContent = a.name + ' · ' + w.genre + ' · ' + w.pub_str +
      (w.orig ? ' · ' + w.orig : '');
    art.appendChild(meta);

    var body = findText(texts, w.slug);
    if (body && body.text) {
      body.text.split(/\n{2,}/).forEach(function (para) {
        para = para.trim();
        if (!para) return;
        var p = el('p');
        p.textContent = para;
        art.appendChild(p);
      });
      var note = el('p', 'lit__src');
      note.textContent = t('lit.sourceNote') + (body.source ? ' ' + body.source : '') +
        (body.abridged ? ' · ' + t('lit.abridged') : '');
      art.appendChild(note);
    } else {
      var wait = el('div', 'lit__wait');
      wait.innerHTML = '<b>' + esc(t('lit.noTextTitle')) + '</b><p>' + esc(t('lit.noText')) + '</p>';
      if (w.status !== 'ok') {
        var p2 = el('p', 'lit__warn');
        p2.textContent = t('lit.translationNote', { n: w.pub });
        wait.appendChild(p2);
      }
      art.appendChild(wait);
    }
    box.appendChild(art);
  }

  function findText(texts, slug) {
    if (!texts || !texts.works) return null;
    for (var i = 0; i < texts.works.length; i++) {
      if (texts.works[i].slug === slug) return texts.works[i];
    }
    return null;
  }

  function renderExcluded() {
    var box = $('#litExcluded');
    if (!box) return;
    box.innerHTML = '';
    var list = (Lit.cat && Lit.cat.excluded) || [];
    if (!list.length) {
      var wrap = box.parentNode;
      if (wrap) wrap.hidden = true;
      return;
    }
    list.forEach(function (x) {
      var n = el('div', 'lit__ex');
      n.innerHTML = '<b>' + esc(x.name) + '</b><i>' + esc(x.life) + '</i>' +
        '<span>' + esc(x.reason) + '</span>' +
        (x.note ? '<small>' + esc(x.note) + '</small>' : '');
      box.appendChild(n);
    });
  }

  /* ── интеграция с роутером ─────────────────────────────────── */
  function applyLitHash() {
    var h = location.hash || '';
    if (h.split('?')[0].replace('#', '') !== 'lit') return;
    readHash();
    Lit.render();
  }

  /* Регистрируем экран в роутере app.js. SCREENS объявлен в app.js раньше,
     чем выполняется этот файл, поэтому к моменту boot он уже есть. */
  if (H().SCREENS) {
    H().SCREENS.lit = {
      enter: function () {
        readHash();
        Lit.boot();
        var inp = $('#litSearch');
        if (inp && !inp.dataset.bound) {
          inp.dataset.bound = '1';
          inp.addEventListener('input', function () {
            Lit.q = inp.value.trim();
            renderAuthors();
          });
        }
      }
    };
  }
  window.addEventListener('hashchange', applyLitHash);

  try {
    window.ouri = window.ouri || {};
    window.ouri.Lit = Lit;
  } catch (e) {}
})();
