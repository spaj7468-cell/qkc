/* ══════════════════════════════════════════════════════════════════
   OuRi · app.js — ядро, экраны, движок тестов
   ══════════════════════════════════════════════════════════════════ */
(function () {
'use strict';

/* ─────────── 0. утилиты ─────────── */
const $  = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.prototype.slice.call((r || document).querySelectorAll(s));
const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = a => a[Math.floor(Math.random() * a.length)];
const shuffle = a => { const r = a.slice(); for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const t = r[i]; r[i] = r[j]; r[j] = t; } return r; };
const pad2 = n => (n < 10 ? '0' : '') + n;
const fmtTime = ms => { const s = Math.max(0, Math.round(ms / 1000)); return Math.floor(s / 60) + ':' + pad2(s % 60); };
const fmtLong = ms => { const m = Math.round(ms / 60000); if (m < 60) return m + ' мин'; if (m < 1440) return Math.floor(m / 60) + ' ч ' + (m % 60) + ' мин'; return Math.floor(m / 1440) + ' д'; };
const fmtNum = n => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const todayKey = () => { const d = new Date(); return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate()); };
const hash = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); };
const mq = q => (window.matchMedia ? window.matchMedia(q) : { matches: false, addEventListener: function () {}, removeEventListener: function () {} });
const debounce = (fn, ms) => { let t; return function () { const a = arguments, c = this; clearTimeout(t); t = setTimeout(() => fn.apply(c, a), ms); }; };

const Store = {
  ok: (function () { try { localStorage.setItem('_t', '1'); localStorage.removeItem('_t'); return true; } catch (e) { return false; } })(),
  mem: {},
  get(k, d) { try { const v = this.ok ? localStorage.getItem(k) : this.mem[k]; return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { const s = JSON.stringify(v); if (this.ok) localStorage.setItem(k, s); else this.mem[k] = s; return true; } catch (e) { return false; } },
  del(k) { try { if (this.ok) localStorage.removeItem(k); else delete this.mem[k]; } catch (e) {} }
};

/* ─────────── 1. данные (индекс банка) ─────────── */
const INDEX = window.OURI_INDEX || { meta: {}, subjects: {}, gradeSubjects: {}, counts: {}, topics: {}, total: 0 };
const META = INDEX.meta || INDEX;
const SUBJECTS = INDEX.subjects || {};
const GRADE_SUBJECTS = INDEX.gradeSubjects || {};
const COUNTS = INDEX.counts || {};
const TOPICS = INDEX.topics || {};
const TOTAL_Q = INDEX.total || 0;
const BANKS = window.OURI_BANKS = window.OURI_BANKS || {};
const IDMAP = {};

const Bank = {
  loading: {},
  has(g) { return !!BANKS[g]; },
  load(g) {
    g = +g;
    if (BANKS[g]) return Promise.resolve(BANKS[g]);
    if (this.loading[g]) return this.loading[g];
    this.loading[g] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = 'assets/bank-' + g + '.js';
      s.onload = () => { this.index(g); res(BANKS[g]); };
      s.onerror = () => { delete this.loading[g]; rej(new Error('bank load fail ' + g)); };
      document.head.appendChild(s);
    });
    return this.loading[g];
  },
  index(g) {
    const b = BANKS[g]; if (!b || IDMAP[g]) return;
    IDMAP[g] = {};
    Object.keys(b).forEach(subj => {
      Object.keys(b[subj]).forEach(q => {
        b[subj][q].forEach(it => { it.id = it.id || hash(subj + '|' + it.t); it.subj = subj; it.qn = +q; it.grade = g; IDMAP[g][it.id] = it; });
      });
    });
  },
  items(g, subj, periods, topics) {
    const b = BANKS[g]; if (!b || !b[subj]) return [];
    let out = [];
    (periods && periods.length ? periods : [1, 2, 3, 4]).forEach(q => {
      if (b[subj][q]) out = out.concat(b[subj][q]);
    });
    const seen = {}; out = out.filter(it => { if (seen[it.id]) return false; seen[it.id] = 1; return true; });
    if (topics && topics.length) out = out.filter(it => topics.indexOf(baseTopic(it.tp)) >= 0);
    return out;
  },
  count(g, subj, periods) {
    let n = 0;
    (periods && periods.length ? periods : [1, 2, 3, 4]).forEach(q => { n += ((COUNTS[g] || {})[subj] || [0, 0, 0, 0])[q - 1] || 0; });
    return n;
  },
  topics(g, subj) { return (TOPICS[g] || {})[subj] || []; },
  subjectGrades(subj) { const out = []; for (let g = 0; g <= 11; g++) if ((GRADE_SUBJECTS[g] || []).indexOf(subj) >= 0) out.push(g); return out; },
  findById(g, id) { return (IDMAP[g] || {})[id]; }
};
function baseTopic(tp) { return String(tp || '').split(' · ')[0].trim(); }

/* ─────────── 2. i18n ─────────── */
const DICT = window.OURI_I18N || { ru: {}, en: {} };
let LANG = 'ru';
function t(key, vars) {
  const d = DICT[LANG] || DICT.ru || {};
  let s = d[key];
  if (s == null) s = (DICT.ru || {})[key];
  if (s == null) s = key;
  if (vars) Object.keys(vars).forEach(k => { s = s.replace(new RegExp('\\{' + k + '\\}', 'g'), vars[k]); });
  return s;
}
function applyI18n() {
  document.documentElement.lang = LANG;
  $$('[data-i18n]').forEach(n => { const k = n.getAttribute('data-i18n'); const v = t(k); if (v) n.textContent = v; });
  $$('[data-i18n-ph]').forEach(n => { n.placeholder = t(n.getAttribute('data-i18n-ph')); });
}

/* ─────────── 3. состояние ─────────── */
const KEY = 'ouri.v1.';
const DEF_SETTINGS = {
  lang: 'ru', theme: 'dark', scale: 'md', contrast: 'normal',
  motion: true, grain: true, bg: true, sound: true, haptics: true,
  timer: true, shuffleQ: true, shuffleA: true, instant: true, autoNext: false, strict: false,
  trimesters: false, sprintSec: 45, count: 20
};
const DEF_PROFILE = () => ({
  xp: 0, tests: 0, answered: 0, correct: 0, timeMs: 0, bestStreak: 0, streakDays: 0, lastDay: null,
  heat: {}, bySubject: {}, byGrade: {}, byMode: {}, ach: {}, fav: [], history: [], records: {}, goal: 30, todayDone: 0, todayKey: null
});
const State = {
  profiles: [], cur: 0, settings: Object.assign({}, DEF_SETTINGS), ready: false
};
function loadState() {
  const s = Store.get(KEY + 'settings', null);
  State.settings = Object.assign({}, DEF_SETTINGS, s || {});
  let ps = Store.get(KEY + 'profiles', null);
  if (!ps || !ps.length) ps = [{ id: 'p1', name: 'Ученик', data: DEF_PROFILE() }];
  ps.forEach(p => { p.data = Object.assign(DEF_PROFILE(), p.data || {}); });
  State.profiles = ps;
  State.cur = clamp(Store.get(KEY + 'cur', 0) || 0, 0, ps.length - 1);
  LANG = State.settings.lang || 'ru';
}
function saveSettings() { Store.set(KEY + 'settings', State.settings); }
function saveProfiles() {
  if (Store.set(KEY + 'profiles', State.profiles)) { Store.set(KEY + 'cur', State.cur); return true; }
  // не хватило места — режем историю и объяснения
  State.profiles.forEach(p => {
    if (!p.data) return;
    p.data.history = (p.data.history || []).slice(0, 12).map(h => {
      if (h.answers) h.answers = h.answers.map(a => ({ id: a.id, t: a.t, ty: a.ty, o: a.o, c: a.c, e: (a.e || '').slice(0, 180), tp: a.tp, given: a.given, ok: a.ok, ms: a.ms }));
      return h;
    });
  });
  const ok = Store.set(KEY + 'profiles', State.profiles);
  Store.set(KEY + 'cur', State.cur);
  return ok;
}
const me = () => State.profiles[State.cur];
const D = () => me().data;

/* уровни и опыт */
const xpForLevel = lv => 250 * lv * (lv - 1) / 2 + 250 * (lv - 1) * 0 ; // накопительный порог
function levelInfo(xp) {
  let lv = 1, need = 250;
  while (xp >= need) { xp -= need; lv++; need = 250 * lv; }
  return { level: lv, inLevel: xp, need: need, pct: xp / need };
}
const RANKS = ['Новичок', 'Ученик', 'Знаток', 'Эксперт', 'Мастер', 'Магистр', 'Легенда', 'Архитектор знаний'];
function rankOf(lv) { return RANKS[clamp(Math.floor((lv - 1) / 3), 0, RANKS.length - 1)]; }

/* ─────────── 4. звук ─────────── */
const Sound = {
  ctx: null,
  init() { if (!this.ctx) { try { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} } if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume(); },
  tone(freq, dur, type, vol, delay) {
    if (!State.settings.sound || !this.ctx) return;
    const c = this.ctx, t0 = c.currentTime + (delay || 0);
    const o = c.createOscillator(), g = c.createGain();
    o.type = type || 'sine'; o.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0, t0); g.gain.linearRampToValueAtTime(vol == null ? 0.06 : vol, t0 + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g); g.connect(c.destination); o.start(t0); o.stop(t0 + dur + 0.02);
  },
  play(kind) {
    if (!State.settings.sound) return; this.init(); if (!this.ctx) return;
    switch (kind) {
      case 'click': this.tone(520, 0.05, 'square', 0.025); break;
      case 'select': this.tone(380, 0.06, 'triangle', 0.04); break;
      case 'right': this.tone(660, 0.1, 'sine', 0.06); this.tone(990, 0.14, 'sine', 0.05, 0.07); break;
      case 'wrong': this.tone(150, 0.22, 'sawtooth', 0.035); this.tone(110, 0.26, 'sine', 0.03, 0.05); break;
      case 'flag': this.tone(880, 0.05, 'triangle', 0.03); break;
      case 'finish': [523, 659, 784, 1046].forEach((f, i) => this.tone(f, 0.18, 'sine', 0.05, i * 0.09)); break;
      case 'level': [660, 880, 1320, 1760].forEach((f, i) => this.tone(f, 0.2, 'triangle', 0.05, i * 0.07)); break;
      case 'ach': [784, 988, 1318].forEach((f, i) => this.tone(f, 0.22, 'sine', 0.05, i * 0.08)); break;
      case 'tick': this.tone(1200, 0.03, 'square', 0.02); break;
    }
  },
  buzz(ms) { if (State.settings.haptics && navigator.vibrate) { try { navigator.vibrate(ms); } catch (e) {} } }
};

/* ─────────── 5. эффекты (частицы / конфетти) ─────────── */
const FX = {
  cv: null, cx: null, parts: [], raf: 0,
  init() {
    this.cv = $('#fx'); if (!this.cv) return;
    try { this.cx = this.cv.getContext('2d'); } catch (e) { this.cx = null; }
    if (!this.cx) return;
    this.resize(); window.addEventListener('resize', debounce(() => this.resize(), 200));
  },
  resize() { if (!this.cv || !this.cx) return; const d = Math.min(window.devicePixelRatio || 1, 2); this.cv.width = innerWidth * d; this.cv.height = innerHeight * d; this.cx.setTransform(d, 0, 0, d, 0, 0); },
  burst(x, y, n, power) {
    if (!State.settings.motion || !this.cx) return;
    n = n || 26; power = power || 1;
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, s = (1.5 + Math.random() * 5) * power;
      this.parts.push({ x: x, y: y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 1.5, life: 1, size: 1.5 + Math.random() * 3.5, sq: Math.random() < 0.4 });
    }
    if (!this.raf) this.loop();
  },
  confetti(n) {
    if (!State.settings.motion || !this.cx) return;
    for (let i = 0; i < (n || 110); i++) {
      this.parts.push({ x: Math.random() * innerWidth, y: -20 - Math.random() * innerHeight * 0.4, vx: (Math.random() - 0.5) * 1.6, vy: 1.4 + Math.random() * 2.6, life: 1, size: 2 + Math.random() * 4, sq: true, fall: true });
    }
    if (!this.raf) this.loop();
  },
  loop() {
    const self = this;
    this.raf = requestAnimationFrame(function step() {
      const cx = self.cx; if (!cx) { self.raf = 0; return; }
      cx.clearRect(0, 0, innerWidth, innerHeight);
      const light = document.documentElement.getAttribute('data-theme') === 'light';
      for (let i = self.parts.length - 1; i >= 0; i--) {
        const p = self.parts[i];
        p.x += p.vx; p.y += p.vy; p.vy += p.fall ? 0.035 : 0.12; p.vx *= 0.99; p.life -= p.fall ? 0.006 : 0.016;
        if (p.life <= 0 || p.y > innerHeight + 30) { self.parts.splice(i, 1); continue; }
        cx.globalAlpha = clamp(p.life, 0, 1) * (light ? 0.75 : 0.9);
        cx.fillStyle = light ? '#111' : '#fff';
        if (p.sq) { cx.save(); cx.translate(p.x, p.y); cx.rotate(p.x * 0.02 + p.y * 0.01); cx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.7); cx.restore(); }
        else { cx.beginPath(); cx.arc(p.x, p.y, p.size, 0, 6.283); cx.fill(); }
      }
      cx.globalAlpha = 1;
      if (self.parts.length) self.raf = requestAnimationFrame(step); else { self.raf = 0; cx.clearRect(0, 0, innerWidth, innerHeight); }
    });
  }
};

/* ─────────── 6. фон (canvas-частицы) ─────────── */
const BG = {
  cv: null, cx: null, dots: [], raf: 0, mouse: { x: -999, y: -999 },
  init() {
    this.cv = $('#bg'); if (!this.cv) return;
    try { this.cx = this.cv.getContext('2d'); } catch (e) { this.cx = null; }
    if (!this.cx) return;
    this.build();
    window.addEventListener('resize', debounce(() => this.build(), 250));
    window.addEventListener('pointermove', e => { this.mouse.x = e.clientX; this.mouse.y = e.clientY; }, { passive: true });
    this.tick();
  },
  build() {
    if (!this.cx) return;
    const d = Math.min(window.devicePixelRatio || 1, 2);
    this.cv.width = innerWidth * d; this.cv.height = innerHeight * d;
    this.cx.setTransform(d, 0, 0, d, 0, 0);
    const n = clamp(Math.round(innerWidth * innerHeight / 26000), 26, 90);
    this.dots = [];
    for (let i = 0; i < n; i++) this.dots.push({ x: Math.random() * innerWidth, y: Math.random() * innerHeight, vx: (Math.random() - 0.5) * 0.16, vy: (Math.random() - 0.5) * 0.16, r: Math.random() * 1.5 + 0.5 });
    this.cv.style.opacity = State.settings.bg ? '' : '0';
  },
  tick() {
    const self = this;
    (function frame() {
      self.raf = requestAnimationFrame(frame);
      const cx = self.cx; if (!cx || !State.settings.bg || !State.settings.motion) return;
      if (document.hidden) return;
      cx.clearRect(0, 0, innerWidth, innerHeight);
      const light = document.documentElement.getAttribute('data-theme') === 'light';
      const col = light ? '0,0,0' : '255,255,255';
      for (let i = 0; i < self.dots.length; i++) {
        const d = self.dots[i];
        d.x += d.vx; d.y += d.vy;
        if (d.x < -20) d.x = innerWidth + 20; if (d.x > innerWidth + 20) d.x = -20;
        if (d.y < -20) d.y = innerHeight + 20; if (d.y > innerHeight + 20) d.y = -20;
        cx.beginPath(); cx.fillStyle = 'rgba(' + col + ',.32)'; cx.arc(d.x, d.y, d.r, 0, 6.283); cx.fill();
        for (let j = i + 1; j < self.dots.length; j++) {
          const o = self.dots[j], dx = d.x - o.x, dy = d.y - o.y, dist = dx * dx + dy * dy;
          if (dist < 15000) { cx.strokeStyle = 'rgba(' + col + ',' + (0.09 * (1 - dist / 15000)).toFixed(3) + ')'; cx.lineWidth = 1; cx.beginPath(); cx.moveTo(d.x, d.y); cx.lineTo(o.x, o.y); cx.stroke(); }
        }
        const mx = d.x - self.mouse.x, my = d.y - self.mouse.y, md = mx * mx + my * my;
        if (md < 26000) { cx.strokeStyle = 'rgba(' + col + ',.13)'; cx.beginPath(); cx.moveTo(d.x, d.y); cx.lineTo(self.mouse.x, self.mouse.y); cx.stroke(); }
      }
    })();
  }
};

/* ─────────── 7. тосты, модалки ─────────── */
function toast(title, sub, icon) {
  const box = $('#toasts'); if (!box) return;
  const n = el('div', 'toast');
  n.innerHTML = '<span class="toast__i">' + (icon || '•') + '</span><span><b>' + esc(title) + '</b>' + (sub ? '<span>' + esc(sub) + '</span>' : '') + '</span>';
  box.appendChild(n);
  setTimeout(() => { n.classList.add('is-out'); setTimeout(() => n.remove(), 320); }, 3600);
  while (box.children.length > 4) box.firstChild.remove();
}
let modalCloser = null;
function modal(opts) {
  const root = $('#modalRoot'); if (!root) return;
  root.hidden = false; root.innerHTML = '';
  const m = el('div', 'modal');
  m.setAttribute('role', 'dialog'); m.setAttribute('aria-modal', 'true');
  m.innerHTML =
    '<div class="modal__h"><h3>' + esc(opts.title || '') + '</h3><button class="icon-btn" data-x aria-label="' + t('common.close') + '"><svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="1.8" fill="none"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' +
    '<div class="modal__b"></div>' +
    (opts.buttons && opts.buttons.length ? '<div class="modal__f"></div>' : '');
  root.appendChild(m);
  const body = $('.modal__b', m);
  if (typeof opts.body === 'string') body.innerHTML = opts.body; else if (opts.body) body.appendChild(opts.body);
  const foot = $('.modal__f', m);
  if (foot) (opts.buttons || []).forEach(b => {
    const btn = el('button', 'btn ' + (b.primary ? 'btn--primary' : 'btn--ghost'), esc(b.label));
    btn.onclick = () => { if (b.onClick) b.onClick(); if (b.keepOpen !== true) closeModal(); };
    foot.appendChild(btn);
  });
  const close = () => closeModal();
  $('[data-x]', m).onclick = close;
  root.onclick = e => { if (e.target === root) close(); };
  modalCloser = close;
  document.body.classList.add('is-locked');
  const f = $('input,button', m); if (f) f.focus();
  return m;
}
function closeModal() { const r = $('#modalRoot'); if (r) { r.hidden = true; r.innerHTML = ''; } modalCloser = null; document.body.classList.remove('is-locked'); }
function confirmBox(title, text, onYes, yesLabel) {
  modal({ title: title, body: '<p>' + esc(text) + '</p>', buttons: [
    { label: t('common.cancel') },
    { label: yesLabel || t('common.yes'), primary: true, onClick: onYes }
  ] });
}

/* ─────────── 8. роутер ─────────── */
const Router = {
  cur: 'home',
  go(name, opts) {
    if (!SCREENS[name]) name = 'home';
    if (this.cur === name && !opts) { window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
    Object.keys(SCREENS).forEach(k => { const n = $('#screen-' + k); if (n) n.hidden = (k !== name); });
    if (this.cur === 'quiz' && name !== 'quiz') { stopTimers(); if (!Quiz.done) Store.del(RESUME_KEY); document.body.classList.remove('in-quiz'); }
    this.cur = name;
    $$('.nav__link').forEach(a => a.classList.toggle('is-on', a.dataset.route === name));
    $('#navLinks').classList.remove('is-open');
    $('#btnBurger').setAttribute('aria-expanded', 'false');
    location.hash = name === 'home' ? '' : name;
    if (SCREENS[name] && SCREENS[name].enter) SCREENS[name].enter(opts);
    if (window.scrollTo) window.scrollTo({ top: 0, behavior: 'auto' });
    document.body.classList.toggle('is-locked', false);
  },
  fromHash() { const h = (location.hash || '').replace('#', ''); return SCREENS[h] ? h : 'home'; }
};
const SCREENS = {};

/* ─────────── 9. контент главной ─────────── */
const FEATURES = [
  ['Тесты', '11 классов', 'Строгая база: 1-й класс не увидит вопросы 9-го'],
  ['Тесты', '20 предметов', 'Математика, языки, естественные и гуманитарные науки, ИЗО, музыка, технология, ОБЖ, физкультура'],
  ['Тесты', 'Четверти и триместры', 'Переключатель календаря: 4 четверти или 3 триместра'],
  ['Тесты', '10 / 20 / 30 вопросов', 'Плюс своё число от 5 до 50 ползунком'],
  ['Тесты', 'Весь год сразу', 'Смешанный тест по всем четвертям предмета'],
  ['Тесты', 'Фильтр по темам', 'Отдельные разделы внутри предмета'],
  ['Тесты', 'Три типа вопросов', 'Выбор ответа, верно/неверно, ввод ответа с клавиатуры'],
  ['Тесты', 'Числовые ответы', 'Проверка с допуском, поддержка дробей и десятичной запятой'],
  ['Тесты', 'Объяснение к каждому вопросу', 'Формулы, ход решения, правило'],
  ['Тесты', 'Мгновенная проверка', 'Или отключи её — режим экзамена'],
  ['Тесты', '41 000+ вопросов', 'База генерируется и проверяется автоматически'],
  ['Тесты', 'Без повторов', 'Внутри теста вопросы не дублируются'],
  ['Режимы', 'Обычный', 'Спокойный темп с подсказками'],
  ['Режимы', 'Экзамен', 'Таймер, без подсказок, разбор в конце'],
  ['Режимы', 'Спринт', 'Ограничение времени на каждый вопрос'],
  ['Режимы', 'Обучение', 'Ответ и объяснение сразу'],
  ['Режимы', 'Марафон', 'Максимальный объём вопросов'],
  ['Режимы', 'Тест дня', 'Одинаковый набор для всех по дате'],
  ['Режимы', 'Случайный тест', 'Кнопка «удиви меня» на главной'],
  ['Режимы', 'Работа над ошибками', 'Повтор только тех вопросов, где была ошибка'],
  ['Режимы', 'Тёплый старт', 'Короткий тест на 5 вопросов'],
  ['Режимы', 'Возврат к вопросу', 'Пропусти и вернись позже'],
  ['Режимы', 'Отмена ответа', 'Передумал — откати ответ'],
  ['Режимы', 'Флаги на вопросах', 'Отметь сложные и вернись к ним'],
  ['Режимы', 'Автопереход', 'Следующий вопрос сам через секунду'],
  ['Интерфейс', 'Тёмная тема', 'Основная, глубокий чёрный'],
  ['Интерфейс', 'Светлая тема', 'Бумажный белый, переключение в один клик'],
  ['Интерфейс', 'Высокий контраст', 'Режим для слабовидящих'],
  ['Интерфейс', '4 размера текста', 'От уменьшенного до очень крупного'],
  ['Интерфейс', 'Плёночное зерно', 'Текстура поверх макета, отключается'],
  ['Интерфейс', 'Живой фон', 'Canvas-частицы, реагируют на курсор'],
  ['Интерфейс', 'Отключение анимаций', 'Для prefers-reduced-motion и вручную'],
  ['Интерфейс', 'Полный экран', 'Ничего лишнего вокруг теста'],
  ['Интерфейс', 'Фокус-режим', 'Скрывает шапку во время теста'],
  ['Интерфейс', 'Бегущая строка', 'Тикер с предметами на главной'],
  ['Интерфейс', 'Анимации появления', 'Плавные scroll-reveal блоки'],
  ['Интерфейс', 'Магнитная кнопка', 'Главная CTA тянется к курсору'],
  ['Интерфейс', 'Микро-взаимодействия', 'Ховеры, нажатия, переходы на всех элементах'],
  ['Интерфейс', 'Палитра вопросов', 'Сетка-навигация по тесту'],
  ['Интерфейс', 'Прогресс-бар', 'Тонкая линия сверху страницы и в тесте'],
  ['Интерфейс', 'Кольцо результата', 'Анимированный процент на экране итогов'],
  ['Интерфейс', 'Графики по темам', 'Полосы точности по разделам'],
  ['Интерфейс', 'Тепловая карта', 'Активность по дням за 18 недель'],
  ['Интерфейс', 'Печать отчёта', 'Отдельные стили для принтера'],
  ['Интерфейс', 'Русский и английский', 'Полный перевод интерфейса'],
  ['Данные', 'Локальное хранение', 'Никаких серверов и регистрации'],
  ['Данные', 'Экспорт в JSON', 'Забери свою статистику файлом'],
  ['Данные', 'Импорт из JSON', 'Верни статистику на другое устройство'],
  ['Данные', 'Несколько профилей', 'До 6 человек на одном устройстве'],
  ['Данные', 'Рейтинг профилей', 'Сравнение по опыту'],
  ['Данные', 'История тестов', 'Последние 40 попыток с разбором'],
  ['Данные', 'Возобновление теста', 'Сохраним прогресс при перезагрузке'],
  ['Данные', 'Личные рекорды', 'Лучший результат для каждого набора'],
  ['Данные', 'Избранные вопросы', 'Сохраняй сложное и возвращайся'],
  ['Данные', 'Сброс прогресса', 'С подтверждением, одним профилем'],
  ['Данные', 'Очистка истории', 'Отдельно от общей статистики'],
  ['Данные', 'Ленивая загрузка базы', 'Класс подгружается по требованию'],
  ['Данные', 'Работа офлайн', 'Service worker кэширует сайт и банк'],
  ['Мотивация', 'Опыт (XP)', 'За каждый верный ответ'],
  ['Мотивация', 'Уровни', 'Растущий порог и кольцо прогресса'],
  ['Мотивация', 'Звания', 'От «Новичка» до «Архитектора знаний»'],
  ['Мотивация', 'Достижения', '34 значка с прогресс-барами'],
  ['Мотивация', 'Серия дней', 'Стрик как в языковых приложениях'],
  ['Мотивация', 'Дневная цель', 'Настраиваемое число вопросов в день'],
  ['Мотивация', 'Серия верных подряд', 'Счётчик внутри теста'],
  ['Мотивация', 'Конфетти за идеал', 'Монохромный салют при 100%'],
  ['Мотивация', 'Звуковые отметки', 'Верно / неверно / финиш / уровень'],
  ['Мотивация', 'Вибро-отклик', 'На мобильных устройствах'],
  ['Доступность', 'Клавиатура везде', 'Ответы 1–4, Enter, стрелки, Esc'],
  ['Доступность', 'Палитра команд', 'Ctrl/⌘+K — быстрый переход'],
  ['Доступность', 'Горячие клавиши в тесте', 'S — флаг, P — пауза, F — финиш'],
  ['Доступность', 'ARIA-разметка', 'Роли, состояния, живые регионы'],
  ['Доступность', 'Живой регион', 'Озвучка результата скринридером'],
  ['Доступность', 'Видимый фокус', 'Контур на всех интерактивных элементах'],
  ['Доступность', 'Skip-link', 'Переход к содержимому с клавиатуры'],
  ['Доступность', 'Крупные цели', 'Кнопки не меньше 38px'],
  ['Доступность', 'Без зависимости от цвета', 'Форма и подписи вместо цвета'],
  ['Доступность', 'Подсказка по клавишам', 'Модалка со списком сочетаний'],
  ['Умное', 'Поиск по предметам', 'В конструкторе и библиотеке'],
  ['Умное', 'Поиск по текстам вопросов', 'Библиотека с фильтрами'],
  ['Умное', 'Библиотека вопросов', 'Просмотр базы без прохождения теста'],
  ['Умное', 'Пагинация библиотеки', 'По 20 вопросов на страницу'],
  ['Умное', 'Ссылка на тест', 'Набор кодируется в URL, можно поделиться'],
  ['Умное', 'Копирование результата', 'Текстовая сводка в буфер обмена'],
  ['Умное', 'Нормализация ответов', 'Ё/е, регистр, пробелы, запятая-точка'],
  ['Умное', 'Допуск в числах', 'Округления не считаются ошибкой'],
  ['Умное', 'Дроби и перечисления', 'Ответы вида 1/2 и «3; 5»'],
  ['Умное', 'Подсчёт времени на вопрос', 'Среднее и по каждому вопросу'],
  ['Умное', 'Статистика по предметам', 'Точность и число ответов'],
  ['Умное', 'Статистика по классам', 'Где тренируешься чаще'],
  ['Умное', 'Статистика по режимам', 'Какой режим предпочитаешь'],
  ['Умное', 'Точность по темам', 'Слабые места видны сразу'],
  ['Умное', 'Индикатор сети', 'Онлайн/офлайн в подвале'],
  ['Умное', 'PWA-манифест', 'Можно установить как приложение'],
  ['Умное', 'Версия в подвале', 'Всегда видно, какая сборка'],
  ['Тесты', 'Детский сад', 'Ступень ниже 1 класса: счёт, буквы, окружающий мир'],
  ['Тесты', 'Программа по классам', 'Темы каждой четверти с объяснением простыми словами'],
  ['Умное', 'Решатель примеров', 'По шагам: порядок действий и линейные уравнения (BETA)'],
  ['Умное', 'Решатель русского', 'Слоги, звуки, ударение по слову (BETA)'],
  ['Связь', 'Форма отзыва', 'Ошибка или идея — открывает готовое письмо в Gmail'],
  ['Связь', 'Канал во ВКонтакте', 'Сообщество компании, ссылка в футере'],
  ['Связь', 'Telegram и WhatsApp', 'Помечены «скоро» — появятся позже'],
  ['Интерфейс', 'Метка BETA', 'Честно предупреждаем о возможных ошибках'],
  ['Данные', 'Живая активность', 'Тепловая карта и серия дней обновляются сразу, даже если тест не завершён']
];

const MODES = [
  { id: 'classic', ico: '◎', tag: 'по умолчанию' },
  { id: 'exam', ico: '▣', tag: 'таймер + строгость' },
  { id: 'sprint', ico: '◷', tag: 'секунды на вопрос' },
  { id: 'study', ico: '✎', tag: 'без оценки' },
  { id: 'marathon', ico: '∞', tag: 'максимум вопросов' }
];

const KEYS_HELP = [
  ['1…4', 'выбрать ответ'], ['Enter', 'ответить / дальше'], ['←', 'предыдущий вопрос'],
  ['→', 'следующий вопрос'], ['S', 'отметить вопрос'], ['P', 'пауза'], ['F', 'завершить тест'],
  ['N', 'пропустить'], ['U', 'отменить ответ'], ['Ctrl/⌘+K', 'палитра команд'],
  ['?', 'эта справка'], ['Esc', 'закрыть / выйти']
];

function renderTicker() {
  const tr = $('#tickerTrack'); if (!tr) return;
  const items = [];
  Object.keys(SUBJECTS).forEach(k => items.push(SUBJECTS[k].name));
  items.push('1 класс', '5 класс', '9 класс', '11 класс', 'четверти и триместры', 'объяснения к ответам', 'офлайн-режим', 'без регистрации', 'чёрное и белое');
  const html = items.map(i => '<span>' + esc(i) + '</span>').join('');
  tr.innerHTML = html + html;
}

function renderHow() {
  const box = $('#howSteps'); if (!box) return;
  box.innerHTML = '';
  for (let i = 1; i <= 4; i++) {
    const c = el('div', 'step-card reveal');
    c.innerHTML = '<div class="step-card__n">0' + i + '</div><h4>' + esc(t('how.' + i + 't')) + '</h4><p>' + esc(t('how.' + i + 'd')) + '</p>';
    box.appendChild(c);
  }
  observeReveals(box);
}

function renderSubjectGrid() {
  const box = $('#subjectGrid'); if (!box) return;
  box.innerHTML = '';
  Object.keys(SUBJECTS).forEach(k => {
    const s = SUBJECTS[k], gs = Bank.subjectGrades(k);
    if (!gs.length) return;
    let total = 0; gs.forEach(g => { const c = (COUNTS[g] || {})[k]; if (c) total += c.reduce((a, b) => a + b, 0); });
    const c = el('div', 'subj-card reveal');
    c.tabIndex = 0; c.setAttribute('role', 'button');
    c.innerHTML = '<span class="subj-card__grades">' + esc(t('subj.classes', { a: gs[0], b: gs[gs.length - 1] })) + '</span>' +
      '<div class="subj-card__ico">' + esc(s.icon) + '</div><h4>' + esc(s.name) + '</h4>' +
      '<p>' + fmtNum(total) + ' ' + esc(t('common.q')) + '</p>';
    const go = () => { Wizard.grade = gs[Math.min(4, gs.length - 1)]; Wizard.subject = k; Wizard.period = 1; Router.go('setup'); };
    c.onclick = go; c.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } };
    box.appendChild(c);
  });
  observeReveals(box);
}

let featShown = 24, featCat = null;
function renderFeatures() {
  const grid = $('#featGrid'), filter = $('#featFilter'); if (!grid) return;
  if (!filter.children.length) {
    const cats = ['Все'];
    FEATURES.forEach(f => { if (cats.indexOf(f[0]) < 0) cats.push(f[0]); });
    cats.forEach((c, i) => {
      const b = el('button', 'chip' + (i === 0 ? ' is-on' : ''), esc(c === 'Все' ? t('feat.all') : c));
      b.onclick = () => { featCat = i === 0 ? null : c; featShown = 24; $$('.chip', filter).forEach(x => x.classList.remove('is-on')); b.classList.add('is-on'); renderFeatures(); Sound.play('select'); };
      filter.appendChild(b);
    });
  }
  const list = FEATURES.filter(f => !featCat || f[0] === featCat);
  grid.innerHTML = '';
  list.slice(0, featShown).forEach((f, i) => {
    const n = el('div', 'feat reveal');
    n.style.transitionDelay = (i % 12) * 0.02 + 's';
    n.innerHTML = '<i>' + pad2(i + 1) + '</i><span><b>' + esc(f[1]) + '</b><span>' + esc(f[2]) + '</span></span>';
    grid.appendChild(n);
  });
  observeReveals(grid);
  const more = $('#featMore');
  if (more) { more.hidden = featShown >= list.length; more.textContent = featShown >= list.length ? t('feat.less') : t('feat.more') + ' (' + Math.max(0, list.length - featShown) + ')'; }
}

function renderModesGrid() {
  const box = $('#modesGrid'); if (!box) return;
  box.innerHTML = '';
  MODES.slice(0, 4).forEach(m => {
    const c = el('div', 'mode reveal');
    c.innerHTML = '<div class="mode__ico">' + m.ico + '</div><h4>' + esc(t('mode.' + m.id)) + '</h4><p>' + esc(t('mode.' + m.id + 'D', { n: State.settings.sprintSec })) + '</p><span class="mode__tag">' + esc(m.tag) + '</span>';
    c.onclick = () => { Wizard.mode = m.id; Router.go('setup'); };
    box.appendChild(c);
  });
  observeReveals(box);
}

function renderKeys() {
  const box = $('#keysList'); if (!box) return;
  box.innerHTML = KEYS_HELP.map(k => '<div class="key-row"><kbd>' + esc(k[0]) + '</kbd><span>' + esc(k[1]) + '</span></div>').join('');
}

function renderQuick() {
  const box = $('#quickSteps'); if (!box) return;
  box.innerHTML = '';
  const steps = [
    ['quick.s1', Wizard.grade != null ? t('n' + Wizard.grade) : '—'],
    ['quick.s2', Wizard.subject ? SUBJECTS[Wizard.subject].name : '—'],
    ['quick.s3', Wizard.periods && Wizard.periods.length ? periodLabel() : '—'],
    ['quick.s4', String(Wizard.count)]
  ];
  steps.forEach((s, i) => {
    const li = el('li');
    li.innerHTML = '<b>' + esc(t(s[0])) + '</b><i>' + esc(s[1]) + '</i>';
    li.onclick = () => { Sound.play('select'); Router.go('setup', { step: i + 1 }); };
    box.appendChild(li);
  });
  syncQuick();
}
function syncQuick() {
  const lis = $$('#quickSteps li');
  if (!lis.length) return;
  const vals = [Wizard.grade != null ? t('n' + Wizard.grade) : '—', Wizard.subject ? SUBJECTS[Wizard.subject].name : '—', periodLabel(), String(Wizard.count)];
  lis.forEach((li, i) => { $('i', li).textContent = vals[i]; li.classList.toggle('is-on', i === 0 ? Wizard.grade != null : i === 1 ? !!Wizard.subject : i === 2 ? !!(Wizard.periods && Wizard.periods.length) : true); });
  const go = $('#quickGo'); if (go) go.disabled = !(Wizard.grade != null && Wizard.subject);
}
function periodLabel() {
  if (!Wizard.periods) return '—';
  if (!Wizard.periods.length) return t('setup.allYear');
  if (State.settings.trimesters) return Wizard.periods.map(p => t('setup.t', { n: p })).join(', ');
  return Wizard.periods.map(p => t('setup.q', { n: p })).join(', ');
}

function renderDaily() {
  const box = $('#dailyBox'); if (!box) return;
  const g = new Date().getDate() % 12;
  const subs = GRADE_SUBJECTS[g] || [];
  const s = subs[new Date().getDate() % subs.length] || 'math';
  const q = (new Date().getMonth() % 4) + 1;
  box.innerHTML = '';
  const row = el('div', 'daily__row');
  row.innerHTML = '<b>' + esc(t('n' + g)) + ' · ' + esc(SUBJECTS[s] ? SUBJECTS[s].name : s) + '</b><i>' + esc(t('setup.q', { n: q })) + ' · 10</i>';
  row.onclick = () => { startTest({ grade: g, subject: s, periods: [q], count: 10, mode: 'classic', daily: true }); };
  box.appendChild(row);
  const row2 = el('div', 'daily__row');
  const s2 = subs[(new Date().getDate() + 3) % subs.length] || 'russian';
  row2.innerHTML = '<b>' + esc(t('n' + g)) + ' · ' + esc(SUBJECTS[s2] ? SUBJECTS[s2].name : s2) + '</b><i>' + esc(t('common.year')) + ' · 20</i>';
  row2.onclick = () => { startTest({ grade: g, subject: s2, periods: [], count: 20, mode: 'classic', daily: true }); };
  box.appendChild(row2);
}

function renderRecent() {
  const box = $('#recentBox'); if (!box) return;
  const h = (D().history || []).slice(0, 5);
  if (!h.length) { box.innerHTML = '<div class="empty">' + esc(t('dash.empty')) + '</div>'; return; }
  box.innerHTML = '';
  h.forEach(x => {
    const n = el('div', 'recent__i');
    n.innerHTML = '<span>' + esc((SUBJECTS[x.subj] || {}).name || x.subj) + ' · ' + esc(x.grade) + '</span>' +
      '<span class="bar"><i style="width:' + x.pct + '%"></i></span><b>' + x.pct + '%</b>';
    n.style.cursor = 'pointer';
    n.onclick = () => openHistory(x.id);
    box.appendChild(n);
  });
}

function renderHeroStats() {
  const sets = Object.keys(COUNTS).reduce((a, g) => a + Object.keys(COUNTS[g]).length, 0);
  const vals = { 0: TOTAL_Q, 1: 12, 2: Object.keys(SUBJECTS).length, 3: sets };
  $$('.hero__stats .num').forEach((n, i) => { countUp(n, vals[i] != null ? vals[i] : +n.dataset.count); });
  const ht = $('#heroTotal'); if (ht) ht.textContent = fmtNum(TOTAL_Q);
}
function countUp(node, to) {
  if (!State.settings.motion || mq('(prefers-reduced-motion: reduce)').matches) { node.textContent = fmtNum(to); return; }
  const dur = 1400, t0 = performance.now();
  (function step(now) {
    const p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 3);
    node.textContent = fmtNum(Math.round(to * e));
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}

let revealObs = null;
function observeReveals(root) {
  if (!('IntersectionObserver' in window)) { $$('.reveal', root || document).forEach(n => n.classList.add('is-in')); return; }
  if (!revealObs) revealObs = new IntersectionObserver(es => {
    es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); revealObs.unobserve(e.target); } });
  }, { threshold: 0.08, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal', root || document).forEach(n => revealObs.observe(n));
}

SCREENS.home = {
  enter() {
    renderHow(); renderSubjectGrid(); renderFeatures(); renderModesGrid(); renderKeys();
    renderQuick(); renderDaily(); renderRecent(); renderHeroStats();
    requestAnimationFrame(() => document.body.classList.add('is-ready'));
    observeReveals();
  }
};

/* ─────────── 10. конструктор теста ─────────── */
const Wizard = { grade: null, subject: null, periods: [1], count: 20, mode: 'classic', topics: [], custom: 20 };

function periodCount(g, s) {
  const c = (COUNTS[g] || {})[s] || [0, 0, 0, 0];
  if (State.settings.trimesters) return [c[0] + c[1], c[2], c[3], 0];
  return c;
}
function periodList() { return State.settings.trimesters ? [1, 2, 3] : [1, 2, 3, 4]; }
function periodToQuarters(p) {
  if (!p) return [1, 2, 3, 4];
  return State.settings.trimesters ? (p === 1 ? [1, 2] : [p]) : [p];
}
function availableCount() {
  if (Wizard.grade == null || !Wizard.subject) return 0;
  let n = 0;
  (Wizard.periods.length ? Wizard.periods : periodList()).forEach(p => { n += periodCount(Wizard.grade, Wizard.subject)[p - 1] || 0; });
  return n;
}

const SetupScreen = {
  enter(opts) { this.render(); if (opts && opts.step) { const s = $('.step[data-step="' + opts.step + '"]'); if (s && s.scrollIntoView) s.scrollIntoView({ behavior: 'smooth', block: 'center' }); } },
  render() {
    renderStepper(); renderGrades(); renderSubjects(); renderPeriods(); renderTopics(); renderCounts(); renderModes2(); renderOpts(); renderSummary();
  }
};
SCREENS.setup = SetupScreen;

function renderStepper() {
  const box = $('#stepper'); if (!box) return;
  const labels = ['setup.s1', 'setup.s2', 'setup.s3', 'setup.s4', 'setup.s5', 'setup.s6'];
  const done = [Wizard.grade != null, !!Wizard.subject, !!Wizard.periods, true, !!Wizard.count, !!Wizard.mode];
  box.innerHTML = labels.map((l, i) => '<li class="' + (done[i] ? 'is-done' : '') + '"><b>' + pad2(i + 1) + '</b>' + esc(t(l)) + '</li>').join('');
}

function renderGrades() {
  const box = $('#gradeGrid'); if (!box) return;
  box.innerHTML = '';
  for (let g = 0; g <= 11; g++) {
    const n = el('button', 'grade' + (Wizard.grade === g ? ' is-on' : ''));
    n.type = 'button'; n.setAttribute('role', 'radio'); n.setAttribute('aria-checked', Wizard.grade === g ? 'true' : 'false');
    const subs = (GRADE_SUBJECTS[g] || []).length;
    let q = 0; (COUNTS[g] || {}); Object.keys(COUNTS[g] || {}).forEach(s => { q += (COUNTS[g][s] || []).reduce((a, b) => a + b, 0); });
    n.innerHTML = '<b>' + (g === 0 ? '0' : g) + '</b><i>' + subs + ' · ' + (q > 999 ? (q / 1000).toFixed(1) + 'k' : q) + '</i>';
    n.title = t('n' + g) + ' · ' + subs + ' ' + t('stat.subjects') + ' · ' + fmtNum(q) + ' ' + t('common.q');
    n.onclick = () => {
      Wizard.grade = g;
      if (Wizard.subject && (GRADE_SUBJECTS[g] || []).indexOf(Wizard.subject) < 0) Wizard.subject = null;
      Wizard.topics = []; Sound.play('select'); SetupScreen.render(); syncQuick();
    };
    box.appendChild(n);
  }
}

function renderSubjects() {
  const box = $('#subjectGrid2'); if (!box) return;
  const q = ($('#subjSearch').value || '').trim().toLowerCase();
  box.innerHTML = '';
  if (Wizard.grade == null) { box.innerHTML = '<div class="empty">' + esc(t('setup.needGrade')) + '</div>'; return; }
  const list = GRADE_SUBJECTS[Wizard.grade] || [];
  Object.keys(SUBJECTS).forEach(k => {
    const s = SUBJECTS[k], has = list.indexOf(k) >= 0;
    if (q && s.name.toLowerCase().indexOf(q) < 0 && s.short.indexOf(q) < 0) return;
    const c = periodCount(Wizard.grade, k);
    const tot = has ? c.reduce((a, b) => a + b, 0) : 0;
    const n = el('button', 'subj' + (has ? '' : ' is-off') + (Wizard.subject === k ? ' is-on' : ''));
    n.type = 'button'; n.disabled = !has;
    n.setAttribute('role', 'radio'); n.setAttribute('aria-checked', Wizard.subject === k ? 'true' : 'false');
    n.innerHTML = '<span class="subj__top"><span class="subj__ico">' + esc(s.icon) + '</span><span><b>' + esc(s.name) + '</b><i>' +
      (has ? fmtNum(tot) + ' ' + t('common.q') : '—') + '</i></span></span>';
    n.onclick = () => { Wizard.subject = k; Wizard.topics = []; Sound.play('select'); SetupScreen.render(); syncQuick(); };
    box.appendChild(n);
  });
}

function renderPeriods() {
  const box = $('#quarterGrid'); if (!box) return;
  box.innerHTML = '';
  if (Wizard.grade == null || !Wizard.subject) { box.innerHTML = '<div class="empty">' + esc(t('setup.needSubj')) + '</div>'; return; }
  const tri = State.settings.trimesters;
  const all = el('button', 'quarter' + (Wizard.periods.length === 0 ? ' is-on' : ''));
  all.type = 'button';
  const totalAll = periodCount(Wizard.grade, Wizard.subject).reduce((a, b) => a + b, 0);
  all.innerHTML = '<b>' + esc(t('setup.allYear')) + '</b><i>' + esc(t('setup.avail', { n: fmtNum(totalAll) })) + '</i>';
  all.onclick = () => { Wizard.periods = []; Sound.play('select'); SetupScreen.render(); syncQuick(); };
  box.appendChild(all);
  periodList().forEach(p => {
    const cnt = periodCount(Wizard.grade, Wizard.subject)[p - 1] || 0;
    const n = el('button', 'quarter' + (Wizard.periods.indexOf(p) >= 0 ? ' is-on' : ''));
    n.type = 'button'; n.disabled = cnt === 0;
    n.innerHTML = '<b>' + esc(tri ? t('setup.t', { n: p }) : t('setup.q', { n: p })) + '</b><i>' + esc(t('setup.avail', { n: fmtNum(cnt) })) + '</i>';
    n.onclick = () => {
      const i = Wizard.periods.indexOf(p);
      if (i >= 0) Wizard.periods.splice(i, 1); else Wizard.periods.push(p);
      Wizard.periods.sort(); Sound.play('select'); SetupScreen.render(); syncQuick();
    };
    box.appendChild(n);
  });
  const note = $('#quarterNote');
  if (note) note.textContent = tri
    ? 'Триместр 1 = I и II четверти, триместр 2 = III, триместр 3 = IV.'
    : 'Вопросы каждой четверти строго свои — пересечений между четвертями нет.';
}

function renderTopics() {
  const box = $('#topicGrid'); if (!box) return;
  box.innerHTML = '';
  if (Wizard.grade == null || !Wizard.subject) { box.innerHTML = '<div class="empty">' + esc(t('setup.noTopics')) + '</div>'; return; }
  const list = Bank.topics(Wizard.grade, Wizard.subject);
  if (!list.length) { box.innerHTML = '<div class="empty">' + esc(t('setup.noTopics')) + '</div>'; return; }
  const all = el('button', 'topic-chip' + (Wizard.topics.length === 0 ? ' is-on' : ''));
  all.type = 'button'; all.textContent = t('common.all');
  all.onclick = () => { Wizard.topics = []; Sound.play('select'); renderTopics(); renderCounts(); renderSummary(); };
  box.appendChild(all);
  list.forEach(tp => {
    const c = el('button', 'topic-chip' + (Wizard.topics.indexOf(tp) >= 0 ? ' is-on' : ''));
    c.type = 'button'; c.innerHTML = esc(tp);
    c.onclick = () => {
      const i = Wizard.topics.indexOf(tp);
      if (i >= 0) Wizard.topics.splice(i, 1); else Wizard.topics.push(tp);
      Sound.play('select'); renderTopics(); renderCounts(); renderSummary();
    };
    box.appendChild(c);
  });
}

function renderCounts() {
  const box = $('#countGrid'); if (!box) return;
  const avail = availableCount();
  box.innerHTML = '';
  [10, 20, 30].forEach(n => {
    const b = el('button', 'count' + (Wizard.count === n ? ' is-on' : ''));
    b.type = 'button'; b.disabled = avail === 0;
    b.innerHTML = '<b>' + n + '</b><i>' + (n > avail && avail > 0 ? esc(t('setup.max', { n: avail })) : esc(t('common.q'))) + '</i>';
    b.onclick = () => { Wizard.count = Math.min(n, Math.max(avail, 1)); Sound.play('select'); renderCounts(); renderSummary(); syncQuick(); };
    box.appendChild(b);
  });
  const maxN = Math.max(10, Math.min(avail || 50, 50));
  const range = $('#customCount'), out = $('#customOut');
  if (range) {
    range.max = maxN; range.value = clamp(Wizard.count, 5, maxN); out.textContent = range.value;
    range.oninput = () => { Wizard.count = +range.value; out.textContent = range.value; renderCounts2(); renderSummary(); syncQuick(); };
  }
}
function renderCounts2() { $$('#countGrid .count').forEach((b, i) => b.classList.toggle('is-on', Wizard.count === [10, 20, 30][i])); }

function renderModes2() {
  const box = $('#modeGrid'); if (!box) return;
  box.innerHTML = '';
  MODES.forEach(m => {
    const n = el('button', 'mode' + (Wizard.mode === m.id ? ' is-on' : ''));
    n.type = 'button'; n.setAttribute('role', 'radio'); n.setAttribute('aria-checked', Wizard.mode === m.id ? 'true' : 'false');
    n.innerHTML = '<div class="mode__ico">' + m.ico + '</div><h4>' + esc(t('mode.' + m.id)) + '</h4><p>' +
      esc(t('mode.' + m.id + 'D', { n: State.settings.sprintSec })) + '</p><span class="mode__tag">' + esc(m.tag) + '</span>';
    n.onclick = () => {
      Wizard.mode = m.id; Sound.play('select');
      if (m.id === 'exam') { State.settings.instant = false; State.settings.timer = true; }
      if (m.id === 'study') { State.settings.instant = true; }
      if (m.id === 'marathon') { Wizard.periods = []; Wizard.count = 50; }
      saveSettings(); SetupScreen.render(); syncQuick();
    };
    box.appendChild(n);
  });
}

function renderOpts() {
  const box = $('#optGrid'); if (!box) return;
  const opts = [
    ['timer', 'opt.timer', 'opt.timerD'], ['shuffleQ', 'opt.shuffleQ', 'opt.shuffleQD'], ['shuffleA', 'opt.shuffleA', 'opt.shuffleAD'],
    ['instant', 'opt.instant', 'opt.instantD'], ['autoNext', 'opt.autoNext', 'opt.autoNextD'], ['strict', 'opt.strict', 'opt.strictD']
  ];
  box.innerHTML = '';
  opts.forEach(o => {
    const l = el('label', 'opt-row switch');
    l.innerHTML = '<input type="checkbox" ' + (State.settings[o[0]] ? 'checked' : '') + '><span class="switch__box"></span>' +
      '<span><b>' + esc(t(o[1])) + '</b><i>' + esc(t(o[2])) + '</i></span>';
    $('input', l).onchange = e => { State.settings[o[0]] = e.target.checked; saveSettings(); };
    box.appendChild(l);
  });
}

function renderSummary() {
  const box = $('#summary'); if (!box) return;
  const parts = [];
  parts.push('<span class="tag">' + esc(Wizard.grade != null ? t('n' + Wizard.grade) : '…') + '</span>');
  parts.push('<span class="tag">' + esc(Wizard.subject ? SUBJECTS[Wizard.subject].name : '…') + '</span>');
  parts.push('<span class="tag tag--ghost">' + esc(periodLabel()) + '</span>');
  if (Wizard.topics.length) parts.push('<span class="tag tag--ghost">' + Wizard.topics.length + ' тем</span>');
  parts.push('<span class="tag">' + esc(t('summary.qs', { n: Wizard.count })) + '</span>');
  parts.push('<span class="tag tag--ghost">' + esc(t('mode.' + Wizard.mode)) + '</span>');
  const avail = availableCount();
  if (avail && Wizard.count > avail) parts.push('<span class="tag tag--ghost">доступно ' + avail + '</span>');
  box.innerHTML = parts.join('');
  const go = $('#setupStart');
  if (go) { go.disabled = !(Wizard.grade != null && Wizard.subject && avail > 0); go.querySelector('span').textContent = t('setup.start') + (avail ? ' · ' + Math.min(Wizard.count, avail) : ''); }
}

/* ─────────── 11. движок теста ─────────── */
const Quiz = { cfg: null, items: [], idx: 0, answers: [], times: [], flags: {}, t0: 0, timer: null, paused: false, done: false, sprintLeft: 0, sprintTimer: null, lastPick: null };
const RESUME_KEY = KEY + 'resume';

function buildItems(cfg) {
  let pool = Bank.items(cfg.grade, cfg.subject, cfg.periods && cfg.periods.length ? cfg.periods.map(periodToQuarters).reduce((a, b) => a.concat(b), []) : [], cfg.topics);
  if (cfg.ids && cfg.ids.length) pool = pool.filter(it => cfg.ids.indexOf(it.id) >= 0);
  if (!pool.length) return [];
  if (cfg.mode === 'marathon') cfg.count = Math.min(cfg.count || 50, pool.length);
  let list = State.settings.shuffleQ === false ? pool.slice() : shuffle(pool);
  return list.slice(0, Math.min(cfg.count || 20, list.length));
}

function startTest(cfg) {
  const grade = +cfg.grade;
  $('#quickGo') && ($('#quickGo').textContent = t('lib.loading', { n: grade }));
  Bank.load(grade).then(() => {
    const items = buildItems(cfg);
    if (!items.length) { toast('Нет вопросов', 'Попробуй другую четверть или тему', '!'); Router.go('setup'); return; }
    Quiz.cfg = cfg; Quiz.items = items; Quiz.idx = 0; Quiz.answers = items.map(() => ({ given: null, ok: null, ms: 0, timedOut: false }));
    Quiz.times = items.map(() => 0); Quiz.flags = {}; Quiz.done = false; Quiz.paused = false; Quiz.t0 = Date.now(); Quiz._logged = 0;
    saveResume();
    Router.go('quiz');
    renderQuizHeader(); renderQuestion(); startTimers();
  }).catch(() => {
    toast('База недоступна', 'Не удалось загрузить банк ' + grade + ' класса', '!');
    Router.go('setup');
  }).finally(() => { const b = $('#quickGo'); if (b) b.textContent = t('quick.go'); });
}

function saveResume() {
  if (!Quiz.cfg || Quiz.done) { Store.del(RESUME_KEY); return; }
  Store.set(RESUME_KEY, {
    cfg: Quiz.cfg, idx: Quiz.idx, answers: Quiz.answers, flags: Quiz.flags, elapsed: Date.now() - Quiz.t0, ts: Date.now()
  });
}

function renderQuizHeader() {
  const c = Quiz.cfg;
  $('#quizBadge').textContent = t('n' + c.grade) + ' · ' + SUBJECTS[c.subject].name + ' · ' + t('mode.' + c.mode);
  $('#btnNext').hidden = false; $('#btnFinish').hidden = true;
  $('#timer').hidden = !State.settings.timer && c.mode !== 'exam' && c.mode !== 'sprint';
  if (c.mode === 'exam' || c.mode === 'sprint') $('#timer').hidden = false;
}

function renderQuestion() {
  const it = Quiz.items[Quiz.idx], a = Quiz.answers[Quiz.idx];
  $('#quizCounter').textContent = (Quiz.idx + 1) + ' / ' + Quiz.items.length;
  $('#quizBar').style.width = ((Quiz.idx + (a.given != null ? 1 : 0)) / Quiz.items.length * 100) + '%';
  $('#palCount').textContent = Quiz.answers.filter(x => x.given != null).length + '/' + Quiz.items.length;
  $('#qTopic').textContent = it.tp || '';
  const typeNames = { choice: 'выбор ответа', tf: 'верно / неверно', input: 'ввод ответа' };
  $('#qType').textContent = typeNames[it.ty] || it.ty;
  const qt = $('#qText'); qt.textContent = it.t; qt.classList.toggle('is-code', /print\(|def |x = |\^\d|→/.test(it.t));
  $('#btnFlag').setAttribute('aria-pressed', Quiz.flags[Quiz.idx] ? 'true' : 'false');
  const box = $('#answers'); box.innerHTML = '';
  const iw = $('#inputWrap');
  box.classList.toggle('answers--grid', it.ty === 'tf');
  if (it.ty === 'input') {
    iw.hidden = false; box.hidden = true;
    const inp = $('#answerInput'); inp.value = a.given == null ? '' : a.given; inp.placeholder = t('quiz.inputPh');
    $('#answerUnit').textContent = it.u || '';
    iw.classList.remove('is-right', 'is-wrong');
    if (a.given != null && shownFeedback()) lockInput();
    setTimeout(() => inp.focus(), 60);
  } else {
    iw.hidden = true; box.hidden = false;
    const opts = it.o ? (State.settings.shuffleA === false ? it.o.slice() : shuffleOpts(it, a)) : [];
    a._opts = opts;
    opts.forEach((o, i) => {
      const b = el('button', 'ans');
      b.type = 'button'; b.dataset.i = i;
      b.innerHTML = '<span class="ans__k">' + (i + 1) + '</span><span class="ans__t">' + esc(o) + '</span>';
      b.onclick = () => choose(i, b);
      box.appendChild(b);
    });
    if (a.given != null && shownFeedback()) paintAnswers();
    else if (a.given != null) $$('.ans', box).forEach((b, i) => b.classList.toggle('is-on', i === a.given));
  }
  const fb = $('#feedback'); fb.hidden = !(a.given != null && shownFeedback());
  if (!fb.hidden) fillFeedback(a, it);
  $('#btnUndo').hidden = !(a.given != null && shownFeedback() && Quiz.cfg.mode !== 'exam');
  $('#btnPrev').disabled = Quiz.idx === 0;
  $('#btnNext').textContent = Quiz.idx === Quiz.items.length - 1 ? t('quiz.finish') : t('quiz.next');
  renderPalette();
  Quiz._qT0 = Date.now();
  if (a.given == null) unlockInput();
  if (Quiz.cfg.mode === 'sprint') startSprint();
  announce((Quiz.idx + 1) + ' из ' + Quiz.items.length + '. ' + it.t);
}
function shuffleOpts(it, a) {
  if (a._opts && a._opts.length === (it.o || []).length) return a._opts;
  return shuffle(it.o || []);
}
function shownFeedback() {
  const m = Quiz.cfg.mode;
  if (m === 'study') return true;
  if (m === 'exam') return Quiz.done;
  return !!State.settings.instant;
}
function lockInput() { $('#answerInput').setAttribute('readonly', 'readonly'); }
function unlockInput() { $('#answerInput').removeAttribute('readonly'); }

function choose(i, btn) {
  const a = Quiz.answers[Quiz.idx], it = Quiz.items[Quiz.idx];
  if (a.given != null && shownFeedback() && Quiz.cfg.mode !== 'exam') return;
  if (Quiz.paused) return;
  a.given = i; a.ms = Date.now() - (Quiz._qT0 || Quiz.t0);
  const ok = checkChoice(it, a._opts ? a._opts[i] : (it.o || [])[i]);
  a.ok = ok; a.givenText = a._opts ? a._opts[i] : (it.o || [])[i];
  Sound.play(ok ? 'right' : 'wrong'); Sound.buzz(ok ? 12 : [0, 40, 60]);
  bumpActivity();
  paintAnswers();
  if (shownFeedback()) {
    const fb = $('#feedback'); fb.hidden = false; fillFeedback(a, it);
    if (!ok) { $('#qcard').classList.add('shake'); setTimeout(() => $('#qcard').classList.remove('shake'), 520); }
    else { const rc = $('#qcard').getBoundingClientRect(); FX.burst(rc.left + rc.width / 2, rc.top + rc.height / 3, 18, 0.9); }
    updateStreakBox(ok);
    if (State.settings.autoNext) setTimeout(() => next(), 900);
  } else {
    updateStreakBox(ok);
    setTimeout(() => next(), 220);
  }
  saveResume();
}
function submitInput() {
  const a = Quiz.answers[Quiz.idx], it = Quiz.items[Quiz.idx];
  if (a.given != null && shownFeedback() && Quiz.cfg.mode !== 'exam') return;
  const v = $('#answerInput').value;
  if (!v.trim()) { $('#inputWrap').classList.add('shake'); setTimeout(() => $('#inputWrap').classList.remove('shake'), 500); return; }
  a.given = v.trim(); a.givenText = v.trim();
  a.ok = checkInput(it, v);
  a.ms = Date.now() - (Quiz._qT0 || Quiz.t0);
  Sound.play(a.ok ? 'right' : 'wrong'); Sound.buzz(a.ok ? 12 : [0, 40, 60]);
  bumpActivity();
  $('#inputWrap').classList.add(a.ok ? 'is-right' : 'is-wrong');
  lockInput();
  if (shownFeedback()) { const fb = $('#feedback'); fb.hidden = false; fillFeedback(a, it); updateStreakBox(a.ok); if (State.settings.autoNext) setTimeout(() => next(), 900); }
  else { updateStreakBox(a.ok); setTimeout(() => next(), 220); }
  saveResume();
}
function checkChoice(it, given) { return norm(given) === norm(it.c); }
function norm(s) {
  return String(s == null ? '' : s).trim().toLowerCase().replace(/ё/g, 'е').replace(/\s+/g, ' ').replace(/[\u2013\u2014]/g, '-');
}
function toNum(s) {
  s = norm(s).replace(/\s/g, '').replace(',', '.');
  let m = s.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
  if (m) return parseFloat(m[1]) / parseFloat(m[2]);
  const v = parseFloat(s);
  return isNaN(v) ? null : v;
}
function checkInput(it, given) {
  const strict = State.settings.strict;
  const parts = String(it.c).split(';').map(x => x.trim()).filter(Boolean);
  const gparts = String(given).split(';').map(x => x.trim()).filter(Boolean);
  const one = (a, b) => {
    if (norm(a) === norm(b)) return true;
    const na = toNum(a), nb = toNum(b);
    if (na != null && nb != null) {
      if (strict) return Math.abs(na - nb) < 1e-9;
      return Math.abs(na - nb) <= Math.max(0.011, Math.abs(nb) * 0.012);
    }
    return false;
  };
  if (parts.length > 1) {
    if (gparts.length !== parts.length) return false;
    return parts.every(p => gparts.some(g => one(g, p)));
  }
  return one(given, it.c);
}
function paintAnswers() {
  const it = Quiz.items[Quiz.idx], a = Quiz.answers[Quiz.idx];
  $$('#answers .ans').forEach((b, i) => {
    b.disabled = true;
    const txt = a._opts ? a._opts[i] : (it.o || [])[i];
    b.classList.remove('is-on', 'is-right', 'is-wrong', 'is-miss');
    if (shownFeedback()) {
      if (norm(txt) === norm(it.c)) b.classList.add('is-right');
      else if (a.given === i) b.classList.add('is-wrong');
    } else if (a.given === i) b.classList.add('is-on');
  });
}
function fillFeedback(a, it) {
  const fb = $('#feedback');
  fb.classList.toggle('is-bad', !a.ok);
  $('.feedback__ico', fb).textContent = a.ok ? '✓' : '✕';
  $('#fbTitle').textContent = a.ok ? t('quiz.right') : (a.timedOut ? t('quiz.timeUp') : t('quiz.wrong'));
  const lines = [];
  lines.push('<div class="row"><b>' + esc(t('quiz.yourAnswer')) + ':</b><span>' + esc(a.givenText != null ? a.givenText : t('quiz.noAnswer')) + '</span></div>');
  if (!a.ok) lines.push('<div class="row"><b>' + esc(t('quiz.correctIs')) + ':</b><span>' + esc(it.c) + '</span></div>');
  if (it.e) lines.push('<div class="exp">' + esc(it.e) + '</div>');
  $('#fbExp').innerHTML = lines.join('');
  $('#btnUndo').hidden = !(Quiz.cfg.mode !== 'exam' && !Quiz.done);
}
function updateStreakBox(ok) {
  let s = 0;
  for (let i = Quiz.answers.length - 1; i >= 0; i--) { if (Quiz.answers[i].ok) s++; else if (Quiz.answers[i].given != null) break; }
  const b = $('#streakFire'); if (b) { b.textContent = s; const p = $('#streakBox'); p.classList.add('is-hot'); setTimeout(() => p.classList.remove('is-hot'), 420); }
}
function currentStreak() {
  let best = 0, cur = 0;
  Quiz.answers.forEach(a => { if (a.ok) { cur++; best = Math.max(best, cur); } else if (a.given != null) cur = 0; });
  return best;
}

function next() {
  if (Quiz.done) return;
  if (Quiz.idx < Quiz.items.length - 1) { Quiz.idx++; renderQuestion(); }
  else finish();
}
function prev() { if (Quiz.idx > 0) { Quiz.idx--; renderQuestion(); } }
function gotoQ(i) { if (i >= 0 && i < Quiz.items.length) { Quiz.idx = i; renderQuestion(); } }
function skipQ() { Quiz.answers[Quiz.idx].given = null; next(); }
function undoAnswer() {
  const a = Quiz.answers[Quiz.idx];
  a.given = null; a.ok = null; a.givenText = null; a.timedOut = false;
  $('#feedback').hidden = true; unlockInput();
  $('#answers').querySelectorAll('.ans').forEach(b => { b.disabled = false; b.className = 'ans'; });
  $('#inputWrap').classList.remove('is-right', 'is-wrong'); $('#answerInput').value = '';
  renderQuestion(); saveResume();
}
function toggleFlag() {
  Quiz.flags[Quiz.idx] = !Quiz.flags[Quiz.idx];
  $('#btnFlag').setAttribute('aria-pressed', Quiz.flags[Quiz.idx] ? 'true' : 'false');
  Sound.play('flag'); renderPalette(); saveResume();
}
function renderPalette() {
  const p = $('#palette'); if (!p || p.hidden) return;
  p.innerHTML = '';
  Quiz.items.forEach((it, i) => {
    const b = el('button'); b.type = 'button'; b.textContent = i + 1;
    b.setAttribute('role', 'option');
    if (i === Quiz.idx) b.classList.add('is-cur');
    if (Quiz.answers[i].given != null) b.classList.add('is-ans');
    if (Quiz.flags[i]) b.classList.add('is-flag');
    b.onclick = () => gotoQ(i);
    p.appendChild(b);
  });
  const lg = el('div', 'palette__legend');
  lg.innerHTML = '<span>■ ' + esc(t('quiz.pal.cur')) + '</span><span>□ ' + esc(t('quiz.pal.ans')) + '</span><span>⚑ ' + esc(t('quiz.pal.flag')) + '</span>';
  p.appendChild(lg);
}

function startTimers() {
  stopTimers();
  const tick = () => {
    if (Quiz.paused || Quiz.done) return;
    const ms = Date.now() - Quiz.t0;
    $('#timerTxt').textContent = fmtTime(ms);
    Quiz.answers.forEach(a => { if (a._t0 == null) a._t0 = Quiz.t0; });
  };
  tick(); Quiz.timer = setInterval(tick, 500);
  Quiz.answers.forEach(a => a._t0 = Date.now());
}
function stopTimers() { if (Quiz.timer) clearInterval(Quiz.timer); Quiz.timer = null; if (Quiz.sprintTimer) clearInterval(Quiz.sprintTimer); Quiz.sprintTimer = null; }
function startSprint() {
  if (Quiz.sprintTimer) clearInterval(Quiz.sprintTimer);
  const a = Quiz.answers[Quiz.idx];
  Quiz.sprintLeft = a.given != null ? 0 : State.settings.sprintSec;
  const upd = () => {
    $('#timerTxt').textContent = Quiz.sprintLeft + 'с';
    $('#timer').classList.toggle('is-warn', Quiz.sprintLeft <= 8);
    if (Quiz.sprintLeft <= 5 && Quiz.sprintLeft > 0) Sound.play('tick');
  };
  upd();
  Quiz.sprintTimer = setInterval(() => {
    if (Quiz.paused || Quiz.done) return;
    Quiz.sprintLeft--; upd();
    if (Quiz.sprintLeft <= 0) {
      clearInterval(Quiz.sprintTimer); Quiz.sprintTimer = null;
      const ans = Quiz.answers[Quiz.idx];
      if (ans.given == null) { ans.given = ''; ans.givenText = null; ans.ok = false; ans.timedOut = true; Sound.play('wrong'); if (shownFeedback()) { const fb = $('#feedback'); fb.hidden = false; fillFeedback(ans, Quiz.items[Quiz.idx]); } }
      setTimeout(() => next(), shownFeedback() ? 1100 : 300);
    }
  }, 1000);
}
function togglePause(force) {
  if (Quiz.done) return;
  Quiz.paused = force == null ? !Quiz.paused : force;
  $('#pauseVeil').hidden = !Quiz.paused;
  if (Quiz.paused) { Quiz._pauseT = Date.now(); }
  else if (Quiz._pauseT) { const d = Date.now() - Quiz._pauseT; Quiz.t0 += d; Quiz.answers.forEach(a => { if (a._t0) a._t0 += d; }); Quiz._pauseT = null; }
}

function finish(force) {
  const un = Quiz.answers.filter(a => a.given == null).length;
  if (!force && un > 0 && Quiz.cfg.mode !== 'study') {
    confirmBox(t('quiz.finish'), t('quiz.confirmFinish', { n: un }), () => finish(true), t('quiz.finish'));
    return;
  }
  Quiz.done = true; stopTimers(); Store.del(RESUME_KEY);
  const totalMs = Date.now() - Quiz.t0;
  const items = Quiz.items, answers = Quiz.answers;
  let correct = 0, wrong = 0, skip = 0;
  const byTopic = {};
  answers.forEach((a, i) => {
    if (a.given == null) { skip++; a.ok = false; }
    else if (a.ok) correct++; else wrong++;
    const tp = baseTopic(items[i].tp) || '—';
    byTopic[tp] = byTopic[tp] || { n: 0, c: 0 };
    byTopic[tp].n++; if (a.ok) byTopic[tp].c++;
  });
  const pct = items.length ? Math.round(correct / items.length * 100) : 0;
  const res = {
    id: 'r' + Date.now().toString(36), date: Date.now(), grade: Quiz.cfg.grade, subj: Quiz.cfg.subject,
    period: Quiz.cfg.periods && Quiz.cfg.periods.length ? Quiz.cfg.periods.join('+') : 'all',
    mode: Quiz.cfg.mode, count: items.length, correct: correct, wrong: wrong, skip: skip, pct: pct, timeMs: totalMs,
    bestStreak: currentStreak(), topics: byTopic,
    answers: items.map((it, i) => ({ id: it.id, t: it.t, ty: it.ty, o: it.o, c: it.c, e: it.e, tp: it.tp, given: answers[i].givenText != null ? answers[i].givenText : (answers[i].given != null ? String(answers[i].given) : null), ok: !!answers[i].ok, ms: answers[i].ms || 0 }))
  };
  applyProgress(res);
  renderResult(res);
  Router.go('result');
  Sound.play('finish');
  if (pct === 100) { FX.confetti(160); setTimeout(() => FX.confetti(90), 700); }
  else if (pct >= 70) FX.burst(innerWidth / 2, innerHeight / 3, 60, 1.4);
}

/* ─────────── 12. прогресс и достижения ─────────── */
function logActivity(n) {
  if (!n || n <= 0) return;
  const d = D(); const tk = todayKey();
  if (d.todayKey !== tk) { d.todayKey = tk; d.todayDone = 0; }
  d.todayDone += n;
  d.heat[tk] = (d.heat[tk] || 0) + n;
  const y = new Date(); y.setDate(y.getDate() - 1);
  const yk = y.getFullYear() + '-' + pad2(y.getMonth() + 1) + '-' + pad2(y.getDate());
  if (d.lastDay !== tk) { d.streakDays = (d.lastDay === yk) ? (d.streakDays || 0) + 1 : 1; d.lastDay = tk; }
  saveProfiles(); syncNavXP();
}
function bumpActivity() {
  if (!Quiz.answers || !Quiz.answers.length) return;
  const given = Quiz.answers.filter(a => a.given != null).length;
  if (given > (Quiz._logged || 0)) { logActivity(given - (Quiz._logged || 0)); Quiz._logged = given; }
}
function applyProgress(res) {
  const d = D();
  d.tests = (d.tests || 0) + 1;
  d.answered = (d.answered || 0) + res.count;
  d.correct = (d.correct || 0) + res.correct;
  d.timeMs = (d.timeMs || 0) + res.timeMs;
  d.bestStreak = Math.max(d.bestStreak || 0, res.bestStreak);
  const byS = d.bySubject[res.subj] = d.bySubject[res.subj] || { n: 0, c: 0 };
  byS.n += res.count; byS.c += res.correct;
  const byG = d.byGrade[res.grade] = d.byGrade[res.grade] || { n: 0, c: 0 };
  byG.n += res.count; byG.c += res.correct;
  d.byMode[res.mode] = (d.byMode[res.mode] || 0) + 1;
  const key = res.grade + '|' + res.subj + '|' + res.period;
  const prev = d.records[key];
  res.isRecord = !!(!prev || res.pct > prev.pct) && res.pct > 0;
  if (!prev || res.pct > prev.pct) d.records[key] = { pct: res.pct, date: res.date };
  // опыт
  let xp = res.correct * 10 + Math.round(res.correct / Math.max(1, res.count) * 30);
  if (res.mode === 'exam') xp = Math.round(xp * 1.5);
  if (res.mode === 'sprint') xp = Math.round(xp * 1.3);
  if (res.pct === 100) xp += 60;
  const before = levelInfo(d.xp), after = levelInfo(d.xp + xp);
  res.xpGain = xp; res.levelUp = after.level > before.level; res.level = after.level;
  d.xp += xp;
  // активность: добор за пропущенные/незалогированные вопросы (остальное уже залогировано живо)
  logActivity(Math.max(0, res.count - (Quiz._logged || 0)));
  Quiz._logged = 0;
  // история
  d.history.unshift(res);
  d.history = d.history.slice(0, 40);
  // избранное: авто-добавление ошибок выключено (только вручную)
  checkAchievements(res);
  saveProfiles();
}

const ACH = [
  ['first', 'Первый шаг', 'Пройти первый тест', d => d.tests >= 1, d => Math.min(1, d.tests)],
  ['t10', 'Разогрев', 'Пройти 10 тестов', d => d.tests >= 10, d => Math.min(1, d.tests / 10)],
  ['t50', 'Регулярность', 'Пройти 50 тестов', d => d.tests >= 50, d => Math.min(1, d.tests / 50)],
  ['q100', 'Сотня', 'Ответить на 100 вопросов', d => d.answered >= 100, d => Math.min(1, d.answered / 100)],
  ['q1000', 'Тысяча', 'Ответить на 1000 вопросов', d => d.answered >= 1000, d => Math.min(1, d.answered / 1000)],
  ['q5000', 'Пять тысяч', 'Ответить на 5000 вопросов', d => d.answered >= 5000, d => Math.min(1, d.answered / 5000)],
  ['perfect', 'Идеал', 'Пройти тест на 100%', (d, r) => r && r.pct === 100, () => 0],
  ['p3', 'Три идеала', 'Три теста на 100%', d => d.history.filter(x => x.pct === 100).length >= 3, d => Math.min(1, d.history.filter(x => x.pct === 100).length / 3)],
  ['streak5', 'Пятёрка', '5 верных ответов подряд', (d, r) => (r ? r.bestStreak : 0) >= 5 || (d.bestStreak || 0) >= 5, d => Math.min(1, (d.bestStreak || 0) / 5)],
  ['streak20', 'Двадцать', '20 верных подряд', d => (d.bestStreak || 0) >= 20, d => Math.min(1, (d.bestStreak || 0) / 20)],
  ['streak30', 'Тридцать', '30 верных подряд', d => (d.bestStreak || 0) >= 30, d => Math.min(1, (d.bestStreak || 0) / 30)],
  ['days3', 'Три дня', 'Серия 3 дня подряд', d => (d.streakDays || 0) >= 3, d => Math.min(1, (d.streakDays || 0) / 3)],
  ['days7', 'Неделя', 'Серия 7 дней подряд', d => (d.streakDays || 0) >= 7, d => Math.min(1, (d.streakDays || 0) / 7)],
  ['days30', 'Месяц', 'Серия 30 дней', d => (d.streakDays || 0) >= 30, d => Math.min(1, (d.streakDays || 0) / 30)],
  ['lv5', 'Уровень 5', 'Достичь 5 уровня', d => levelInfo(d.xp).level >= 5, d => Math.min(1, levelInfo(d.xp).level / 5)],
  ['lv10', 'Уровень 10', 'Достичь 10 уровня', d => levelInfo(d.xp).level >= 10, d => Math.min(1, levelInfo(d.xp).level / 10)],
  ['lv20', 'Уровень 20', 'Достичь 20 уровня', d => levelInfo(d.xp).level >= 20, d => Math.min(1, levelInfo(d.xp).level / 20)],
  ['subj5', 'Пять предметов', 'Тренировать 5 разных предметов', d => Object.keys(d.bySubject).length >= 5, d => Math.min(1, Object.keys(d.bySubject).length / 5)],
  ['subj10', 'Десять предметов', 'Тренировать 10 разных предметов', d => Object.keys(d.bySubject).length >= 10, d => Math.min(1, Object.keys(d.bySubject).length / 10)],
  ['grades5', 'Пять классов', 'Пройти тесты за 5 разных классов', d => Object.keys(d.byGrade).length >= 5, d => Math.min(1, Object.keys(d.byGrade).length / 5)],
  ['allgrades', 'Все классы', 'Тренировать все 11 классов', d => Object.keys(d.byGrade).length >= 11, d => Math.min(1, Object.keys(d.byGrade).length / 11)],
  ['exam', 'Строгий режим', 'Пройти тест в режиме «Экзамен»', (d, r) => (r && r.mode === 'exam') || (d.byMode.exam || 0) >= 1, d => Math.min(1, d.byMode.exam || 0)],
  ['sprint', 'Спринтер', 'Пройти тест в режиме «Спринт»', (d, r) => (r && r.mode === 'sprint') || (d.byMode.sprint || 0) >= 1, d => Math.min(1, d.byMode.sprint || 0)],
  ['study', 'Ученик', 'Пройти тест в режиме «Обучение»', (d, r) => (r && r.mode === 'study') || (d.byMode.study || 0) >= 1, d => Math.min(1, d.byMode.study || 0)],
  ['marathon', 'Марафонец', 'Пройти марафон на 50 вопросов', (d, r) => (r && r.mode === 'marathon' && r.count >= 50) || (d.byMode.marathon || 0) >= 1, d => Math.min(1, d.byMode.marathon || 0)],
  ['modes', 'Все режимы', 'Попробовать все режимы', d => Object.keys(d.byMode).length >= 4, d => Math.min(1, Object.keys(d.byMode).length / 4)],
  ['speed', 'Молния', 'Среднее время ответа меньше 10 с', (d, r) => r && r.timeMs / Math.max(1, r.count) < 10000 && r.count >= 10, () => 0],
  ['think', 'Вдумчивость', 'Среднее время больше 60 с на вопрос', (d, r) => r && r.timeMs / Math.max(1, r.count) > 60000 && r.count >= 5, () => 0],
  ['fav5', 'Коллекционер', 'Добавить 5 вопросов в избранное', d => (d.fav || []).length >= 5, d => Math.min(1, (d.fav || []).length / 5)],
  ['fav25', 'Хранитель', '25 избранных вопросов', d => (d.fav || []).length >= 25, d => Math.min(1, (d.fav || []).length / 25)],
  ['goal', 'Цель дня', 'Выполнить дневную цель', d => (d.todayDone || 0) >= (d.goal || 30), d => Math.min(1, (d.todayDone || 0) / (d.goal || 30))],
  ['night', 'Ночная смена', 'Пройти тест после 23:00', (d, r) => r && new Date(r.date).getHours() >= 23, () => 0],
  ['early', 'Ранняя пташка', 'Пройти тест до 7:00', (d, r) => r && new Date(r.date).getHours() < 7, () => 0],
  ['topics', 'Снайпер', 'Пройти тест с фильтром по темам', () => !!window.__ouri_topic_run, () => 0],
  ['daily', 'Тест дня', 'Пройти «Тест дня»', () => !!window.__ouri_daily_run, () => 0],
  ['comeback', 'Возвращение', 'Пройти работу над ошибками', () => !!window.__ouri_mistakes_run, () => 0]
];

/* монохромные иконки достижений (stroke = currentColor) */
const ACH_ICONS = {
  first:    '<path d="M6 3v18M6 4h11l-2 4 2 4H6"/>',
  t10:      '<path d="M4 7h16M4 12h16M4 17h10"/>',
  t50:      '<path d="M4 5h16M4 9h16M4 13h16M4 17h10"/>',
  q100:     '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8.5 12.5l2.5 2.5 5-6"/>',
  q1000:    '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
  q5000:    '<rect x="4" y="4" width="16" height="6" rx="2"/><rect x="4" y="14" width="16" height="6" rx="2"/><path d="M8 7h.01M8 17h.01"/>',
  perfect:  '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
  p3:       '<path d="M7 4l1.2 2.6L11 7l-2 2 .5 2.8L7 10.5 4.5 11.8 5 9 3 7l2.8-.4zM17 4l1.2 2.6L21 7l-2 2 .5 2.8L17 10.5l-2.5 1.3.5-2.8-2-2 2.8-.4zM12 12l1.2 2.6 2.8.4-2 2 .5 2.8-2.5-1.3-2.5 1.3.5-2.8-2-2 2.8-.4z"/>',
  streak5:  '<path d="M13 2L5 13h6l-1 9 8-11h-6z"/>',
  streak20: '<path d="M10 2L3 12h5l-1 8 6-9H9zM18 4l-4 6h3l-.5 6 4.5-7h-3.5z"/>',
  streak30: '<circle cx="12" cy="12" r="9"/><path d="M13 7l-4 5.5h3L11 17l4-5.5h-3z"/>',
  days3:    '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
  days7:    '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4M9 15l2 2 4-4.5"/>',
  days30:   '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4M8 14h2M12 14h2M16 14h2M8 17h2M12 17h2"/>',
  lv5:      '<path d="M12 19V5M6 11l6-6 6 6"/>',
  lv10:     '<path d="M12 20V9M7 13l5-5 5 5M12 8V3M9 5.5L12 3l3 2.5"/>',
  lv20:     '<path d="M3 20l6-11 4 7 3-4 5 8z"/><circle cx="17.5" cy="6.5" r="2"/>',
  subj5:    '<path d="M5 4h6a3 3 0 0 1 3 3v13a2.5 2.5 0 0 0-2.5-2.5H5z"/><path d="M19 4h-5v13.5A2.5 2.5 0 0 1 16.5 20H19z"/>',
  subj10:   '<path d="M4 20V6a2 2 0 0 1 2-2h3v16H6a2 2 0 0 1-2-2zM11 20V4h4v16zM17 20V7h3v13z"/>',
  grades5:  '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5M22 9v6"/>',
  allgrades:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 4 5.6 4 9s-1.5 6.4-4 9c-2.5-2.6-4-5.6-4-9s1.5-6.4 4-9z"/>',
  exam:     '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 10h6M9 14h6M9 18h3"/>',
  sprint:   '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M9 2h6M19 5l1.5 1.5"/>',
  study:    '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  marathon: '<path d="M5 12c0-2 1.5-3.5 3.5-3.5S12 10 12 12s1.5 3.5 3.5 3.5S19 14 19 12s-1.5-3.5-3.5-3.5S12 10 12 12s1.5 3.5 3.5 3.5"/>',
  modes:    '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
  speed:    '<circle cx="12" cy="13" r="8"/><path d="M12 13l3.5-3.5M10 2h4M13 2v2"/>',
  think:    '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.8.6 1.5 1.6 1.5 2.6h4c0-1 .7-2 1.5-2.6A6 6 0 0 0 12 3z"/>',
  fav5:     '<path d="M12 3l2.7 5.6 6.3.9-4.5 4.4 1 6.1-5.5-2.9-5.5 2.9 1-6.1L3 9.5l6.3-.9z"/>',
  fav25:    '<path d="M6 3h12v18l-6-4-6 4z"/><path d="M9 7h6"/>',
  goal:     '<circle cx="12" cy="12" r="9"/><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/>',
  night:    '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/><path d="M17 4l.6 1.6L19 6l-1.4.6L17 8l-.6-1.4L15 6l1.4-.4z"/>',
  early:    '<path d="M4 18h16M7 14a5 5 0 0 1 10 0M12 4v3M5 8l2 2M19 8l-2 2"/>',
  topics:   '<path d="M4 5h16M7 12h10M10 19h4"/>',
  daily:    '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/>',
  comeback: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>'
};
function achIcon(id, on) {
  const p = ACH_ICONS[id];
  if (!p) return on ? '★' : '☆';
  return '<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + p + '</svg>';
}

function checkAchievements(res) {
  const d = D(); d.ach = d.ach || {};
  const got = [];
  ACH.forEach(a => {
    if (d.ach[a[0]]) return;
    let ok = false; try { ok = !!a[3](d, res); } catch (e) {}
    if (ok) { d.ach[a[0]] = Date.now(); got.push(a); }
  });
  got.forEach((a, i) => setTimeout(() => { toast(t('toast.ach'), a[1] + ' — ' + a[2], '★'); Sound.play('ach'); FX.burst(innerWidth - 60, innerHeight - 60, 26, 1.1); }, 500 + i * 900));
}

/* ─────────── 13. экран результата ─────────── */
let lastResult = null;
function renderResult(res) {
  lastResult = res;
  const grade = res.pct >= 90 ? 'res.grade5' : res.pct >= 75 ? 'res.grade4' : res.pct >= 50 ? 'res.grade3' : res.pct >= 25 ? 'res.grade2' : 'res.grade0';
  $('#resKicker').textContent = t('res.kicker');
  $('#resTitle').textContent = t(grade);
  $('#resSub').textContent = t('res.sub', { grade: res.grade, subj: SUBJECTS[res.subj] ? SUBJECTS[res.subj].name : res.subj, period: res.period === 'all' ? t('common.year') : res.period, mode: t('mode.' + res.mode) });
  const avg = res.count ? Math.round(res.timeMs / res.count / 100) / 10 : 0;
  $('#resStats').innerHTML = [
    ['res.correct', res.correct], ['res.wrong', res.wrong], ['res.skip', res.skip],
    ['res.time', fmtTime(res.timeMs)], ['res.avg', avg + ' с'], ['res.best', res.bestStreak], ['res.xp', '+' + (res.xpGain || 0)]
  ].map(x => '<div><dt>' + esc(t(x[0])) + '</dt><dd>' + esc(String(x[1])) + '</dd></div>').join('');
  const isRecord = !!res.isRecord;
  const oldNote = $('.res-note'); if (oldNote) oldNote.remove();
  const acts = $('#resActs'); acts.innerHTML = '';
  const mk = (label, cls, fn, icon) => { const b = el('button', 'btn ' + cls, (icon || '') + '<span>' + esc(label) + '</span>'); b.onclick = fn; acts.appendChild(b); return b; };
  mk(t('res.again'), 'btn--primary', () => startTest(Object.assign({}, res2cfg(res))), '', '');
  if (res.wrong + res.skip > 0) mk(t('res.mistakes'), 'btn--ghost', () => retryMistakes(res));
  mk(t('res.new'), 'btn--ghost', () => Router.go('setup'));
  mk(t('res.dash'), 'btn--ghost', () => Router.go('dash'));
  mk(t('res.share'), 'btn--ghost', () => shareResult(res));
  mk(t('res.print'), 'btn--ghost', () => window.print());
  const extra = [];
  if (res.pct === 100) extra.push(t('res.noMistakes'));
  if (isRecord) extra.push(t('res.newRecord'));
  if (extra.length) { const p = el('p', 'muted sm res-note'); p.textContent = extra.join(' · '); acts.parentNode.insertBefore(p, acts); setTimeout(() => { if (p.parentNode) p.remove(); }, 9000); }
  // XP
  const li = levelInfo(D().xp);
  const xpBox = $('#resXp'); xpBox.hidden = false;
  xpBox.innerHTML = '<b>' + esc(t('res.xpGain', { n: res.xpGain || 0 })) + '</b>' +
    '<span class="muted sm">' + esc(rankOf(li.level)) + ' · ' + esc(t('xp.level')) + ' ' + li.level + '</span>' +
    '<span class="res-xp__bar"><i></i></span>' +
    '<span class="muted sm num">' + li.inLevel + ' / ' + li.need + ' XP</span>';
  setTimeout(() => { const i = $('.res-xp__bar i', xpBox); if (i) i.style.width = (li.pct * 100) + '%'; }, 120);
  if (res.levelUp) { Sound.play('level'); toast(t('toast.levelUp'), rankOf(li.level) + ' · ' + li.level, '↑'); }
  // кольцо
  const ring = $('#ringFg'); const C = 2 * Math.PI * 88;
  ring.style.strokeDasharray = C; ring.style.strokeDashoffset = C;
  setTimeout(() => { ring.style.strokeDashoffset = C * (1 - res.pct / 100); }, 160);
  const pctNode = $('#scorePct'); animateNum(pctNode, res.pct, '%');
  $('#scoreGrade').textContent = t(grade);
  // темы
  const tb = $('#topicBars'); tb.innerHTML = '';
  const tps = Object.keys(res.topics || {}).sort((a, b) => res.topics[a].n - res.topics[b].n).slice(-12).reverse();
  if (!tps.length) tb.innerHTML = '<div class="empty">—</div>';
  tps.forEach(k => {
    const v = res.topics[k], p = Math.round(v.c / v.n * 100);
    const row = el('div', 'tbar');
    row.innerHTML = '<span class="tbar__n" title="' + esc(k) + '">' + esc(k) + '</span><span class="tbar__t"><i></i></span><span class="tbar__v">' + v.c + '/' + v.n + ' · ' + p + '%</span>';
    tb.appendChild(row);
    setTimeout(() => { $('i', row).style.width = p + '%'; }, 200);
  });
  // разбор
  renderReview(res, 'all');
  syncNavXP();
}
function animateNum(node, to, suffix) {
  if (!State.settings.motion) { node.textContent = to + (suffix || ''); return; }
  const t0 = performance.now(), dur = 1100;
  (function step(now) {
    const p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 3);
    node.textContent = Math.round(to * e) + (suffix || '');
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}
function res2cfg(res) {
  return { grade: res.grade, subject: res.subj, periods: res.period === 'all' ? [] : String(res.period).split('+').map(Number), count: res.count, mode: res.mode };
}
function retryMistakes(res) {
  const ids = res.answers.filter(a => !a.ok).map(a => a.id);
  if (!ids.length) return;
  window.__ouri_mistakes_run = true;
  startTest({ grade: res.grade, subject: res.subj, periods: res.period === 'all' ? [] : String(res.period).split('+').map(Number), count: ids.length, mode: 'study', ids: ids });
}
let reviewFilter = 'all';
function renderReview(res, filter) {
  reviewFilter = filter || reviewFilter;
  const box = $('#reviewList'); if (!box) return;
  box.innerHTML = '';
  const list = res.answers.map((a, i) => ({ a: a, i: i })).filter(x => {
    if (reviewFilter === 'wrong') return !x.a.ok && x.a.given != null;
    if (reviewFilter === 'right') return x.a.ok;
    if (reviewFilter === 'skip') return x.a.given == null;
    return true;
  });
  if (!list.length) { box.innerHTML = '<div class="empty">—</div>'; return; }
  list.forEach(x => {
    const a = x.a;
    const n = el('div', 'rev ' + (a.given == null ? 'is-skip' : a.ok ? 'is-right' : 'is-wrong'));
    const isFav = favIndex(D(), a.id) >= 0;
    n.innerHTML = '<button class="rev__h" aria-expanded="false">' +
      '<span class="rev__i">' + (a.given == null ? '–' : a.ok ? '✓' : '✕') + '</span>' +
      '<span class="rev__q">' + esc(a.t) + '<span class="rev__a">' + esc(t('quiz.yourAnswer')) + ': ' + esc(a.given == null ? t('quiz.noAnswer') : a.given) + (a.ok ? '' : ' · ' + esc(t('quiz.correctIs')) + ': ' + esc(a.c)) + '</span></span>' +
      '</button>' +
      '<button class="rev__fav' + (isFav ? ' is-on' : '') + '" title="' + esc(isFav ? t('lib.unfav') : t('lib.fav')) + '">★</button>' +
      '<div class="rev__b">' + (a.tp ? '<div class="row"><b>Тема:</b><span>' + esc(a.tp) + '</span></div>' : '') +
      '<div class="row"><b>Время:</b><span>' + (a.ms ? (a.ms / 1000).toFixed(1) + ' с' : '—') + '</span></div>' +
      (a.o ? '<div class="row"><b>Варианты:</b><span>' + a.o.map(o => esc(o)).join(' · ') + '</span></div>' : '') +
      (a.e ? '<div class="exp">' + esc(a.e) + '</div>' : '') + '</div>';
    const h = $('.rev__h', n);
    h.onclick = () => { n.classList.toggle('is-open'); h.setAttribute('aria-expanded', n.classList.contains('is-open') ? 'true' : 'false'); };
    $('.rev__fav', n).onclick = e => { e.stopPropagation(); toggleFav(a, $('.rev__fav', n)); };
    box.appendChild(n);
  });
}
function favIndex(d, id) { return (d.fav || []).findIndex(x => (x && x.id ? x.id : x) === id); }
function toggleFav(item, btn) {
  const d = D(); d.fav = d.fav || [];
  const i = favIndex(d, item.id);
  if (i >= 0) { d.fav.splice(i, 1); if (btn) btn.classList.remove('is-on'); toast(t('toast.favDel'), '', '–'); }
  else {
    d.fav.push({ id: item.id, g: item.grade || null, subj: item.subj || null, tp: item.tp || '', t: item.t, c: item.c, e: item.e || '', ts: Date.now() });
    if (btn) btn.classList.add('is-on'); toast(t('toast.favAdd'), '', '★'); Sound.play('flag');
  }
  if (d.fav.length > 300) d.fav = d.fav.slice(-300);
  saveProfiles();
}
function shareResult(res) {
  const txt = 'QKC · ' + t('n' + res.grade) + ' · ' + (SUBJECTS[res.subj] || {}).name + ' · ' + res.period +
    '\nРезультат: ' + res.correct + '/' + res.count + ' (' + res.pct + '%) за ' + fmtTime(res.timeMs) +
    '\nРежим: ' + t('mode.' + res.mode) + ' · XP +' + (res.xpGain || 0);
  const url = location.origin + location.pathname + '#setup?g=' + res.grade + '&s=' + res.subj + '&p=' + res.period + '&n=' + res.count + '&m=' + res.mode;
  const full = txt + '\n' + url;
  if (navigator.share) { navigator.share({ title: 'OuRi', text: txt, url: url }).catch(() => {}); return; }
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(full).then(() => toast(t('toast.copied'), 'Результат и ссылка в буфере обмена', '⧉'), () => fallbackCopy(full));
  else fallbackCopy(full);
}
function fallbackCopy(text) {
  const ta = el('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
  document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); toast(t('toast.copied'), '', '⧉'); } catch (e) { modal({ title: t('res.share'), body: '<p>' + esc(text).replace(/\n/g, '<br>') + '</p>', buttons: [{ label: t('common.ok'), primary: true }] }); }
  ta.remove();
}
SCREENS.result = { enter() { if (!lastResult) Router.go('home'); } };
SCREENS.quiz = { enter() { document.body.classList.add('in-quiz'); }, leave() { document.body.classList.remove('in-quiz'); } };

/* ─────────── 14. экран прогресса ─────────── */
SCREENS.dash = { enter() { renderDash(); } };
function renderDash() {
  const d = D();
  renderProfiles();
  const li = levelInfo(d.xp);
  const acc = d.answered ? Math.round(d.correct / d.answered * 100) : 0;
  const stats = [
    ['dash.tests', d.tests || 0, ''], ['dash.answered', fmtNum(d.answered || 0), ''],
    ['dash.acc', acc, '%'], ['dash.time', fmtLong(d.timeMs || 0), ''],
    ['dash.streak', d.streakDays || 0, 'дн.'], ['dash.best', d.bestStreak || 0, ''],
    ['dash.level', li.level, rankOf(li.level)], ['dash.xp', fmtNum(d.xp || 0), '']
  ];
  $('#statGrid').innerHTML = stats.map(s => '<dl class="stat"><dt>' + esc(t(s[0])) + '</dt><dd>' + esc(String(s[1])) + (s[2] ? '<small>' + esc(s[2]) + '</small>' : '') + '</dd></dl>').join('');
  renderHeat(d); renderSubjectBars(d); renderAch(d); renderHistory(d); renderBoard(); renderFav(d);
  syncNavXP();
}
function renderProfiles() {
  const box = $('#profileSwitch'); if (!box) return;
  box.innerHTML = '';
  State.profiles.forEach((p, i) => {
    const b = el('button', 'prof' + (i === State.cur ? ' is-on' : ''));
    b.type = 'button'; b.textContent = p.name;
    b.onclick = () => { State.cur = i; saveProfiles(); renderDash(); syncNavXP(); toast('Профиль', p.name, '◍'); };
    b.oncontextmenu = e => {
      e.preventDefault();
      if (State.profiles.length <= 1) return;
      confirmBox(t('dash.delProfile'), 'Удалить профиль «' + p.name + '» вместе со статистикой?', () => {
        State.profiles.splice(i, 1); State.cur = clamp(State.cur, 0, State.profiles.length - 1); saveProfiles(); renderDash();
      });
    };
    box.appendChild(b);
  });
}
function renderHeat(d) {
  const box = $('#heat'); if (!box) return;
  box.innerHTML = '';
  const days = 18 * 7, now = new Date();
  const start = new Date(now.getTime() - (days - 1) * 86400000);
  start.setDate(start.getDate() - ((start.getDay() + 6) % 7));
  const cells = Math.ceil((now - start) / 86400000) + 1;
  for (let i = 0; i < cells; i++) {
    const dt = new Date(start.getTime() + i * 86400000);
    const k = dt.getFullYear() + '-' + pad2(dt.getMonth() + 1) + '-' + pad2(dt.getDate());
    const v = d.heat[k] || 0;
    const lvl = v === 0 ? 0 : v < 10 ? 1 : v < 25 ? 2 : v < 60 ? 3 : 4;
    const c = el('i'); c.dataset.l = lvl;
    c.title = k + ': ' + v + ' ' + t('common.q');
    box.appendChild(c);
  }
}
function renderSubjectBars(d) {
  const box = $('#dashSubjects'); if (!box) return;
  const keys = Object.keys(d.bySubject || {}).sort((a, b) => d.bySubject[b].n - d.bySubject[a].n).slice(0, 10);
  if (!keys.length) { box.innerHTML = '<div class="empty">' + esc(t('dash.empty')) + '</div>'; return; }
  box.innerHTML = '';
  keys.forEach(k => {
    const v = d.bySubject[k], p = Math.round(v.c / v.n * 100);
    const row = el('div', 'tbar');
    row.innerHTML = '<span class="tbar__n">' + esc((SUBJECTS[k] || {}).name || k) + '</span><span class="tbar__t"><i></i></span><span class="tbar__v">' + p + '% · ' + v.n + '</span>';
    box.appendChild(row);
    setTimeout(() => { $('i', row).style.width = p + '%'; }, 120);
  });
}
function renderAch(d) {
  const box = $('#achGrid'); if (!box) return;
  box.innerHTML = '';
  let got = 0;
  ACH.forEach(a => {
    const on = !!d.ach[a[0]];
    if (on) got++;
    let p = 0; try { p = a[4](d) || 0; } catch (e) { p = on ? 1 : 0; }
    if (on) p = 1;
    const n = el('div', 'ach__i ' + (on ? 'is-on' : 'is-off'));
    n.title = a[1] + ' — ' + a[2];
    n.innerHTML = '<span class="ach__ico">' + achIcon(a[0], on) + '</span><span><b>' + esc(a[1]) + '</b><span>' + esc(a[2]) + '</span>' +
      (on ? '' : '<span class="ach__p"><i style="width:' + Math.round(p * 100) + '%"></i></span>') + '</span>';
    box.appendChild(n);
  });
  $('#achCount').textContent = got + ' / ' + ACH.length;
}
function renderHistory(d) {
  const box = $('#histList'); if (!box) return;
  box.innerHTML = '';
  if (!d.history.length) { box.innerHTML = '<div class="empty">' + esc(t('dash.empty')) + '</div>'; return; }
  d.history.forEach(h => {
    const n = el('div', 'hist__i');
    const dt = new Date(h.date);
    n.innerHTML = '<span class="hist__p">' + h.pct + '%</span>' +
      '<span class="hist__m">' + esc((SUBJECTS[h.subj] || {}).name || h.subj) + ' · ' + h.correct + '/' + h.count +
      '<i>' + esc(t('n' + h.grade)) + ' · ' + esc(h.period === 'all' ? t('common.year') : h.period) + ' · ' + esc(t('mode.' + h.mode)) + ' · ' +
      pad2(dt.getDate()) + '.' + pad2(dt.getMonth() + 1) + ' ' + pad2(dt.getHours()) + ':' + pad2(dt.getMinutes()) + ' · ' + fmtTime(h.timeMs) + '</i></span>' +
      '<span class="hist__a"></span>';
    const acts = $('.hist__a', n);
    const b1 = el('button', 'btn btn--ghost btn--xs'); b1.textContent = t('dash.review');
    b1.onclick = () => openHistory(h.id);
    const b2 = el('button', 'btn btn--ghost btn--xs'); b2.textContent = '↻';
    b2.title = t('res.again'); b2.onclick = () => startTest(res2cfg(h));
    acts.appendChild(b1); acts.appendChild(b2);
    box.appendChild(n);
  });
}
function openHistory(id) {
  const h = (D().history || []).find(x => x.id === id);
  if (!h) return;
  lastResult = h;
  renderResult(h);
  Router.go('result');
}
function renderBoard() {
  const box = $('#boardList'); if (!box) return;
  const list = State.profiles.map((p, i) => ({ p: p, i: i, xp: p.data.xp || 0 })).sort((a, b) => b.xp - a.xp);
  box.innerHTML = '';
  list.forEach((x, k) => {
    const li = levelInfo(x.xp);
    const n = el('div', 'board__i' + (x.i === State.cur ? ' is-me' : ''));
    n.innerHTML = '<span class="board__r">' + (k + 1) + '</span><b>' + esc(x.p.name) + '</b>' +
      '<span class="muted sm">' + esc(rankOf(li.level)) + ' · ур. ' + li.level + '</span><span class="xp">' + fmtNum(x.xp) + ' XP</span>';
    box.appendChild(n);
  });
}
function renderFav(d) {
  const box = $('#favList'); if (!box) return;
  box.innerHTML = '';
  const list = (d.fav || []).slice(-40).reverse();
  if (!list.length) { box.innerHTML = '<div class="empty">' + esc(t('dash.noFav')) + '</div>'; return; }
  list.forEach(f => {
    const id = f && f.id ? f.id : f;
    let it = f && f.t ? f : null;
    if (!it) { for (let g = 0; g <= 11; g++) if (IDMAP[g] && IDMAP[g][id]) { it = IDMAP[g][id]; break; } }
    if (!it) return;
    const n = el('div', 'fav__i');
    n.innerHTML = '<p>' + esc(it.t) + '<small>' + esc((it.g ? t('n' + it.g) : '') + ' · ' + ((SUBJECTS[it.subj] || {}).name || it.subj || '') + (it.tp ? ' · ' + it.tp : '')) + '</small>' +
      '<small>' + esc(t('lib.answer')) + ': ' + esc(it.c) + '</small></p>';
    const b = el('button', 'btn btn--ghost btn--xs'); b.textContent = '✕'; b.title = t('dash.clearFav');
    b.onclick = () => { const i = favIndex(D(), id); if (i >= 0) D().fav.splice(i, 1); saveProfiles(); n.remove(); };
    n.appendChild(b);
    box.appendChild(n);
  });
  if (!box.children.length) box.innerHTML = '<div class="empty">' + esc(t('dash.noFav')) + '</div>';
}

/* ─────────── 15. библиотека вопросов ─────────── */
const Lib = { grade: 5, subj: null, q: 1, search: '', page: 0, per: 20, items: [] };
SCREENS.library = { enter() { renderLibControls(); loadLib(); } };
function renderLibControls() {
  const g = $('#libGrade'); g.innerHTML = '';
  for (let i = 0; i <= 11; i++) {
    const b = el('button', 'chip' + (Lib.grade === i ? ' is-on' : ''), i === 0 ? '0' : String(i));
    b.title = t('n' + i);
    b.onclick = () => { Lib.grade = i; Lib.subj = null; Lib.page = 0; renderLibControls(); loadLib(); };
    g.appendChild(b);
  }
}
function renderLibSubjects() {
  const box = $('#libSubject'); box.innerHTML = '';
  const all = el('button', 'chip' + (!Lib.subj ? ' is-on' : ''), t('common.all'));
  all.onclick = () => { Lib.subj = null; Lib.page = 0; renderLibSubjects(); loadLib(); };
  box.appendChild(all);
  (GRADE_SUBJECTS[Lib.grade] || []).forEach(s => {
    const b = el('button', 'chip' + (Lib.subj === s ? ' is-on' : ''), SUBJECTS[s].name);
    b.onclick = () => { Lib.subj = s; Lib.page = 0; renderLibSubjects(); loadLib(); };
    box.appendChild(b);
  });
}
function renderLibQuarters() {
  const box = $('#libQuarter'); box.innerHTML = '';
  const all = el('button', 'chip' + (Lib.q === 0 ? ' is-on' : ''), t('lib.allQ'));
  all.onclick = () => { Lib.q = 0; Lib.page = 0; renderLibQuarters(); loadLib(); };
  box.appendChild(all);
  [1, 2, 3, 4].forEach(q => {
    const b = el('button', 'chip' + (Lib.q === q ? ' is-on' : ''), t('setup.q', { n: q }));
    b.onclick = () => { Lib.q = q; Lib.page = 0; renderLibQuarters(); loadLib(); };
    box.appendChild(b);
  });
}
function loadLib() {
  $('#libMeta').textContent = t('lib.loading', { n: Lib.grade });
  Bank.load(Lib.grade).then(() => {
    renderLibSubjects(); renderLibQuarters();
    let out = [];
    const subs = Lib.subj ? [Lib.subj] : (GRADE_SUBJECTS[Lib.grade] || []);
    subs.forEach(s => {
      const b = BANKS[Lib.grade][s] || {};
      (Lib.q ? [Lib.q] : [1, 2, 3, 4]).forEach(q => { (b[q] || []).forEach(it => out.push(it)); });
    });
    const seen = {}; out = out.filter(it => seen[it.id] ? false : (seen[it.id] = 1));
    if (Lib.search) { const s = Lib.search.toLowerCase(); out = out.filter(it => it.t.toLowerCase().indexOf(s) >= 0 || (it.tp || '').toLowerCase().indexOf(s) >= 0); }
    Lib.items = out; Lib.page = 0; renderLibList();
  }).catch(() => { $('#libMeta').textContent = 'Ошибка загрузки базы'; });
}
function renderLibList() {
  const box = $('#libList'); box.innerHTML = '';
  const total = Lib.items.length;
  const pages = Math.max(1, Math.ceil(total / Lib.per));
  Lib.page = clamp(Lib.page, 0, pages - 1);
  const slice = Lib.items.slice(Lib.page * Lib.per, Lib.page * Lib.per + Lib.per);
  $('#libMeta').innerHTML = '<span>' + esc(t('lib.found', { n: fmtNum(total) })) + '</span><span>' +
    esc(t('lib.shown', { a: total ? Lib.page * Lib.per + 1 : 0, b: Math.min(total, (Lib.page + 1) * Lib.per) })) + '</span>' +
    '<span>' + esc(t('n' + Lib.grade)) + '</span>' + (Lib.subj ? '<span>' + esc(SUBJECTS[Lib.subj].name) + '</span>' : '') +
    (Lib.q ? '<span>' + esc(t('setup.q', { n: Lib.q })) + '</span>' : '');
  if (!total) { box.innerHTML = '<div class="empty">' + esc(t('lib.nothing')) + '</div>'; }
  slice.forEach(it => {
    const n = el('div', 'libq');
    const fav = favIndex(D(), it.id) >= 0;
    n.innerHTML = '<div class="libq__t">' + esc(it.t) + '</div>' +
      '<div class="libq__m"><span class="tag tag--ghost">' + esc((SUBJECTS[it.subj] || {}).name || it.subj) + '</span>' +
      (it.tp ? '<span class="tag tag--ghost">' + esc(it.tp) + '</span>' : '') +
      '<span class="tag tag--ghost">' + esc(t('setup.q', { n: it.qn })) + '</span>' +
      '<span class="tag tag--ghost">' + esc(it.ty === 'input' ? 'ввод' : it.ty === 'tf' ? 'верно/неверно' : 'выбор') + '</span></div>' +
      '<div class="libq__a" hidden><b>' + esc(t('lib.answer')) + ':</b> ' + esc(it.c) + (it.e ? '<div class="exp" style="margin-top:8px">' + esc(it.e) + '</div>' : '') + '</div>';
    const acts = el('div', 'libq__m');
    acts.style.marginTop = '10px';
    const b1 = el('button', 'btn btn--ghost btn--xs'); b1.textContent = t('lib.answer');
    b1.onclick = () => { const a = $('.libq__a', n); a.hidden = !a.hidden; };
    const b2 = el('button', 'btn btn--ghost btn--xs' + (fav ? ' btn--primary' : '')); b2.textContent = fav ? '★' : '☆ ' + t('lib.fav');
    b2.onclick = () => { toggleFav(it, null); b2.textContent = favIndex(D(), it.id) >= 0 ? '★' : '☆ ' + t('lib.fav'); b2.classList.toggle('btn--primary'); };
    const b3 = el('button', 'btn btn--ghost btn--xs'); b3.textContent = 'Тренировать тему';
    b3.onclick = () => {
      Wizard.grade = Lib.grade; Wizard.subject = it.subj; Wizard.periods = [it.qn]; Wizard.topics = it.tp ? [baseTopic(it.tp)] : []; Wizard.count = 20;
      startTest({ grade: Lib.grade, subject: it.subj, periods: [it.qn], topics: Wizard.topics, count: 20, mode: 'classic' });
    };
    acts.appendChild(b1); acts.appendChild(b2); acts.appendChild(b3);
    n.appendChild(acts);
    box.appendChild(n);
  });
  const pg = $('#libPager'); pg.innerHTML = '';
  for (let i = 0; i < pages; i++) {
    if (pages > 9 && Math.abs(i - Lib.page) > 3 && i !== 0 && i !== pages - 1) { if (pg.lastChild && pg.lastChild.textContent !== '…') pg.appendChild(el('span', 'muted sm', '…')); continue; }
    const b = el('button', 'chip' + (i === Lib.page ? ' is-on' : ''), String(i + 1));
    b.onclick = () => { Lib.page = i; renderLibList(); if (window.scrollTo) window.scrollTo({ top: 0, behavior: 'smooth' }); };
    pg.appendChild(b);
  }
}

/* ─────────── 16. о компании ─────────── */
SCREENS.about = {
  enter() {
    const sets = Object.keys(COUNTS).reduce((a, g) => a + Object.keys(COUNTS[g]).length, 0);
    $('#aboutNums').innerHTML = [
      [fmtNum(TOTAL_Q), t('stat.questions')], [Object.keys(SUBJECTS).length, t('stat.subjects')],
      [12, t('stat.grades')], [sets, t('stat.sets')], [ACH.length, 'достижений'], [FEATURES.length, 'возможностей']
    ].map(x => '<div><b>' + esc(x[0]) + '</b><span>' + esc(x[1]) + '</span></div>').join('');
    $('#aboutHow').innerHTML = [1, 2, 3, 4, 5, 6].map(i => '<li>' + esc(t('about.how' + i)) + '</li>').join('');
    $('#contactBox').innerHTML =
      '<a href="mailto:juravlev.aleksandr2020@gmail.com"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>juravlev.aleksandr2020@gmail.com</a>' +
      '<a href="https://vk.ru/im/channels/-242032915" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 8c1 6 4 9 8 9h1v-3c1.5 0 3 1 4 3h3c-1-3-3-4.5-4-5 1-.5 3-2 4-5h-3c-1 2-2.5 3-4 3V7h-2c-4 0-6-1-7-3z" transform="scale(.9) translate(1,1)"/></svg>' + esc(t('contacts.vk')) + '</a>' +
      '<a href="https://vk.com/id715180861" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 8c1 6 4 9 8 9h1v-3c1.5 0 3 1 4 3h3c-1-3-3-4.5-4-5 1-.5 3-2 4-5h-3c-1 2-2.5 3-4 3V7h-2c-4 0-6-1-7-3z" transform="scale(.9) translate(1,1)"/></svg>' + esc(t('contacts.vkDev')) + '</a>' +
      '<a href="https://github.com/spaj7468-cell" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-4 1.5-4-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 4.5-1.4 4.5-4.7a4 4 0 0 0-1.1-2.8c.3-.9.2-1.9-.2-2.8 0 0-1.2-.2-3 1.4a10 10 0 0 0-5.4 0C7.4 3.2 6.2 3.4 6.2 3.4c-.4.9-.5 1.9-.2 2.8A4 4 0 0 0 5 9c0 3.3 1.7 4.4 4.5 4.7-.6.6-.6 1.2-.5 2V19"/></svg>' + esc(t('contacts.ghDev')) + '</a>' +
      '<span class="soon">' + esc(t('contacts.tg')) + '</span>' +
      '<span class="soon">' + esc(t('contacts.wa')) + '</span>';
  }
};

/* ─────────── 16o. экран «Открытый проект» ─────────── */
const OPEN_ICONS = {
  site: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14 0 18M12 3c-3 3.5-3 14 0 18"/></svg>',
  git: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="6" cy="6" r="2.3"/><circle cx="6" cy="18" r="2.3"/><circle cx="18" cy="9" r="2.3"/><path d="M6 8.3v7.4M8.3 6h4.4a3 3 0 0 1 3 3v0M16.4 10.6 8.6 17"/></svg>',
  folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
  doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></svg>',
  user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5z"/></svg>',
  mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>'
};
function renderOpen() {
  const L = [
    ['site', 'open.l1n', 'open.l1d', 'spaj7468-cell.github.io/qkc', 'https://spaj7468-cell.github.io/qkc/', 1],
    ['git', 'open.l2n', 'open.l2d', 'github.com/spaj7468-cell/qkc', 'https://github.com/spaj7468-cell/qkc', 1],
    ['folder', 'open.l4n', 'open.l4d', 'corp/index.html', 'corp/index.html', 0],
    ['doc', 'open.l3n', 'open.l3d', 'PR #12650 · js.org/js.org', 'https://github.com/js-org/js.org/pull/12650', 1],
    ['user', 'open.l5n', 'open.l5d', 'github.com/spaj7468-cell', 'https://github.com/spaj7468-cell', 1],
    ['chat', 'open.l6n', 'open.l6d', 'vk.com/id715180861', 'https://vk.com/id715180861', 1],
    ['chat', 'open.l7n', 'open.l7d', 'vk.ru/im/channels/-242032915', 'https://vk.ru/im/channels/-242032915', 1],
    ['mail', 'open.l8n', 'open.l8d', 'juravlev.aleksandr2020@gmail.com', 'mailto:juravlev.aleksandr2020@gmail.com', 0]
  ];
  $('#openLinks').innerHTML = L.map(x =>
    '<a class="olink" href="' + x[4] + '"' + (x[5] ? ' target="_blank" rel="noopener noreferrer"' : '') + '>' +
      '<span class="olink__ico">' + OPEN_ICONS[x[0]] + '</span>' +
      '<span class="olink__body"><span class="olink__t">' + esc(t(x[1])) + '</span>' +
      '<span class="olink__d">' + esc(t(x[2])) + '</span>' +
      '<span class="olink__u">' + esc(x[3]) + '</span></span>' +
      '<span class="olink__arrow">↗</span></a>').join('');
  let h = '';
  for (let i = 1; i <= 10; i++) h += '<li>' + t('open.m' + i) + '</li>';
  $('#openMap').innerHTML = h;
  h = '';
  for (let i = 1; i <= 5; i++) h += '<li>' + t('open.r' + i) + '</li>';
  $('#openRun').innerHTML = h;
}
SCREENS.open = { enter() { renderOpen(); } };

/* ─────────── 17. настройки ─────────── */
function applySettings() {
  const s = State.settings, r = document.documentElement;
  r.setAttribute('data-theme', s.theme);
  r.setAttribute('data-scale', s.scale === 'md' ? '' : s.scale) ; if (s.scale === 'md') r.removeAttribute('data-scale');
  r.setAttribute('data-contrast', s.contrast === 'high' ? 'high' : 'normal');
  r.setAttribute('data-grain', s.grain ? 'on' : 'off');
  r.setAttribute('data-motion', s.motion ? 'on' : 'off');
  const bg = $('#bg'); if (bg) bg.style.opacity = s.bg ? '' : '0';
  const mt = $('meta[name="theme-color"]'); if (mt) mt.content = s.theme === 'light' ? '#f6f5f3' : '#08080a';
  document.body.classList.toggle('no-sound', !s.sound);
  const sb = $('#btnSound'); if (sb) sb.setAttribute('aria-pressed', s.sound ? 'true' : 'false');
  applyI18n();
}
function openSettings() {
  const s = State.settings;
  const body = el('div');
  const row = (label, control) => { const d = el('div', 'opt-row'); d.style.marginBottom = '8px'; d.innerHTML = '<span><b>' + esc(label) + '</b></span>'; d.appendChild(control); body.appendChild(d); return d; };
  const seg = (opts, cur, onPick) => {
    const w = el('div', 'seg'); w.style.marginLeft = 'auto';
    opts.forEach(o => { const b = el('button', 'seg__b' + (o[0] === cur ? ' is-on' : ''), esc(o[1])); b.onclick = () => { $$('.seg__b', w).forEach(x => x.classList.remove('is-on')); b.classList.add('is-on'); onPick(o[0]); }; w.appendChild(b); });
    return w;
  };
  const sw = (key, onChange) => {
    const l = el('label', 'switch'); l.style.marginLeft = 'auto';
    l.innerHTML = '<input type="checkbox" ' + (s[key] ? 'checked' : '') + '><span class="switch__box"></span>';
    $('input', l).onchange = e => { s[key] = e.target.checked; saveSettings(); applySettings(); if (onChange) onChange(e.target.checked); };
    return l;
  };
  body.appendChild(el('h3', 'h3', esc(t('settings.view'))));
  row(t('settings.theme'), seg([['dark', t('settings.dark')], ['light', t('settings.light')]], s.theme, v => { s.theme = v; saveSettings(); applySettings(); }));
  row(t('settings.scale'), seg([['sm', t('settings.sm')], ['md', t('settings.md')], ['lg', t('settings.lg')], ['xl', t('settings.xl')]], s.scale, v => { s.scale = v; saveSettings(); applySettings(); }));
  row(t('settings.contrast'), seg([['normal', t('settings.normal')], ['high', t('settings.high')]], s.contrast, v => { s.contrast = v; saveSettings(); applySettings(); }));
  row(t('settings.lang'), seg([['ru', 'RU'], ['en', 'EN']], s.lang, v => { s.lang = v; LANG = v; saveSettings(); applySettings(); renderAllStatic(); toast(t('toast.langChanged'), '', '⌘'); }));
  row(t('settings.motion'), sw('motion'));
  row(t('settings.grain'), sw('grain'));
  row('Фоновые частицы', sw('bg'));
  body.appendChild(el('h3', 'h3', esc(t('settings.quiz'))));
  row(t('settings.sound'), sw('sound', v => { $('#btnSound').setAttribute('aria-pressed', v ? 'true' : 'false'); }));
  row(t('settings.haptics'), sw('haptics'));
  row(t('opt.timer'), sw('timer'));
  row(t('opt.instant'), sw('instant'));
  row(t('opt.autoNext'), sw('autoNext'));
  row(t('opt.shuffleQ'), sw('shuffleQ'));
  row(t('opt.shuffleA'), sw('shuffleA'));
  row(t('opt.strict'), sw('strict'));
  row('Секунд на вопрос в спринте', (function () { const w = el('div'); w.style.marginLeft = 'auto'; w.style.display = 'flex'; w.style.gap = '8px'; w.style.alignItems = 'center';
    const i = el('input'); i.type = 'range'; i.min = 15; i.max = 120; i.step = 5; i.value = s.sprintSec; const o = el('output', 'num', String(s.sprintSec));
    i.oninput = () => { s.sprintSec = +i.value; o.textContent = i.value; saveSettings(); }; w.appendChild(i); w.appendChild(o); return w; })());
  row('Дневная цель (вопросов)', (function () { const w = el('div'); w.style.marginLeft = 'auto'; w.style.display = 'flex'; w.style.gap = '8px'; w.style.alignItems = 'center';
    const i = el('input'); i.type = 'range'; i.min = 10; i.max = 200; i.step = 10; i.value = D().goal || 30; const o = el('output', 'num', String(D().goal || 30));
    i.oninput = () => { D().goal = +i.value; o.textContent = i.value; saveProfiles(); }; w.appendChild(i); w.appendChild(o); return w; })());
  body.appendChild(el('h3', 'h3', esc(t('settings.data'))));
  const info = el('p', 'muted sm');
  info.textContent = 'Профиль: ' + me().name + ' · XP: ' + fmtNum(D().xp) + ' · тестов: ' + (D().tests || 0) + ' · вопросов в избранных: ' + ((D().fav || []).length) + ' · записей в истории: ' + ((D().history || []).length);
  body.appendChild(info);
  const st = el('div'); st.style.display = 'flex'; st.style.gap = '8px'; st.style.flexWrap = 'wrap'; st.style.marginTop = '10px';
  const b1 = el('button', 'btn btn--ghost btn--sm', esc(t('dash.export'))); b1.onclick = exportData;
  const b2 = el('button', 'btn btn--ghost btn--sm', esc(t('dash.import'))); b2.onclick = () => $('#importFile').click();
  const b3 = el('button', 'btn btn--ghost btn--sm btn--danger', esc(t('dash.reset'))); b3.onclick = () => confirmBox(t('dash.reset'), t('dash.confirmReset'), resetAll);
  st.appendChild(b1); st.appendChild(b2); st.appendChild(b3); body.appendChild(st);
  modal({ title: t('settings.title'), body: body, buttons: [{ label: t('common.ok'), primary: true }] });
}

/* ─────────── 18. палитра команд ─────────── */
const Cmd = {
  open() {
    const c = $('#cmdk'); c.hidden = false; document.body.classList.add('is-locked');
    const inp = $('#cmdInput'); inp.value = ''; this.fill(''); inp.focus();
    this.sel = 0;
  },
  close() { $('#cmdk').hidden = true; document.body.classList.remove('is-locked'); },
  items(q) {
    const out = [];
    const add = (label, group, run, hint) => out.push({ label: label, group: group, run: run, hint: hint || '' });
    add(t('nav.home'), t('cmd.goto'), () => Router.go('home'), 'home');
    add(t('nav.setup'), t('cmd.goto'), () => Router.go('setup'), 'setup');
    add(t('nav.dash'), t('cmd.goto'), () => Router.go('dash'), 'progress');
    add(t('nav.library'), t('cmd.goto'), () => Router.go('library'), 'library');
    add(t('nav.open'), t('cmd.goto'), () => Router.go('open'), 'open source github');
    add(t('nav.program'), t('cmd.goto'), () => Router.go('program'), 'program');
    add(t('nav.solvers'), t('cmd.goto'), () => Router.go('solvers'), 'solvers');
    add(t('nav.about'), t('cmd.goto'), () => Router.go('about'), 'about');
    add(t('settings.title'), t('cmd.action'), openSettings, '⚙');
    add('Сменить тему', t('cmd.action'), toggleTheme, '◐');
    add('Тест дня', t('cmd.action'), () => { const g = (new Date().getDate() % 11) + 1; const subs = GRADE_SUBJECTS[g]; startTest({ grade: g, subject: subs[new Date().getDate() % subs.length], periods: [(new Date().getMonth() % 4) + 1], count: 10, mode: 'classic', daily: true }); }, '★');
    add('Случайный тест', t('cmd.action'), randomTest, '⚄');
    add('Тёплый старт (5 вопросов)', t('cmd.action'), () => warmup(), '5');
    add('Показать горячие клавиши', t('cmd.action'), showKeys, '?');
    add('Экспорт данных', t('cmd.action'), exportData, '↓');
    add('Сбросить прогресс', t('cmd.action'), () => confirmBox(t('dash.reset'), t('dash.confirmReset'), resetAll), '⌫');
    Object.keys(SUBJECTS).forEach(k => {
      const gs = Bank.subjectGrades(k);
      if (!gs.length) return;
      add(SUBJECTS[k].name, t('cmd.subject'), () => { Wizard.grade = gs[Math.min(4, gs.length - 1)]; Wizard.subject = k; Wizard.periods = [1]; Router.go('setup'); }, gs[0] + '–' + gs[gs.length - 1] + ' кл.');
    });
    for (let g = 0; g <= 11; g++) add(t('n' + g) + ' — все предметы', t('cmd.goto'), () => { Lib.grade = g; Lib.subj = null; Router.go('library'); }, String(g));
    const s = q.toLowerCase().trim();
    return s ? out.filter(x => x.label.toLowerCase().indexOf(s) >= 0 || x.group.toLowerCase().indexOf(s) >= 0 || (x.hint || '').toLowerCase().indexOf(s) >= 0) : out;
  },
  fill(q) {
    const list = this.items(q).slice(0, 40);
    const box = $('#cmdList'); box.innerHTML = '';
    this.list = list;
    if (!list.length) { box.innerHTML = '<div class="empty" style="padding:16px">Ничего не найдено</div>'; return; }
    list.forEach((it, i) => {
      const n = el('div', 'cmdk__i' + (i === this.sel ? ' is-sel' : ''));
      n.setAttribute('role', 'option');
      n.innerHTML = '<i>' + esc(it.hint || '') + '</i><b>' + esc(it.label) + '</b><span>' + esc(it.group) + '</span>';
      n.onmouseenter = () => { this.sel = i; this.mark(); };
      n.onclick = () => { this.close(); it.run(); };
      box.appendChild(n);
    });
  },
  mark() { $$('#cmdList .cmdk__i').forEach((n, i) => n.classList.toggle('is-sel', i === this.sel)); const s = $('#cmdList .is-sel'); if (s) s.scrollIntoView({ block: 'nearest' }); },
  move(d) { if (!this.list) return; this.sel = clamp(this.sel + d, 0, this.list.length - 1); this.mark(); },
  run() { const it = this.list && this.list[this.sel]; if (!it) return; this.close(); it.run(); }
};

/* ─────────── 19. общие действия ─────────── */
function toggleTheme() {
  State.settings.theme = State.settings.theme === 'dark' ? 'light' : 'dark';
  saveSettings(); applySettings();
  toast(t('toast.theme', { v: t(State.settings.theme === 'dark' ? 'toast.dark' : 'toast.light') }), '', '◐');
}
function randomTest() {
  const grades = []; for (let g = 0; g <= 11; g++) if ((GRADE_SUBJECTS[g] || []).length) grades.push(g);
  const g = pick(grades); const subs = GRADE_SUBJECTS[g]; const s = pick(subs);
  const p = [rnd(1, 4)];
  Wizard.grade = g; Wizard.subject = s; Wizard.periods = p.slice(); Wizard.count = 20;
  startTest({ grade: g, subject: s, periods: p, count: 20, mode: pick(['classic', 'classic', 'study', 'sprint']) });
}
function warmup() {
  const g = Wizard.grade || pick([5, 6, 7, 8]); const s = Wizard.subject || pick(GRADE_SUBJECTS[g]);
  startTest({ grade: g, subject: s, periods: [], count: 5, mode: 'classic' });
}
function showKeys() {
  modal({ title: t('keys.title'), body: '<div class="keys">' + KEYS_HELP.map(k => '<div class="key-row"><kbd>' + esc(k[0]) + '</kbd><span>' + esc(k[1]) + '</span></div>').join('') + '</div>', buttons: [{ label: t('common.ok'), primary: true }] });
}
function exportData() {
  const payload = { app: 'OuRi', version: '1.0.0', exported: new Date().toISOString(), settings: State.settings, profiles: State.profiles };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = el('a'); a.href = URL.createObjectURL(blob); a.download = 'ouri-progress-' + todayKey() + '.json';
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 3000);
  toast(t('dash.exported'), a.download, '↓');
}
function importData(file) {
  const r = new FileReader();
  r.onload = () => {
    try {
      const d = JSON.parse(r.result);
      if (!d || !d.profiles) throw new Error('bad');
      if (d.settings) { State.settings = Object.assign({}, DEF_SETTINGS, d.settings); saveSettings(); applySettings(); }
      State.profiles = d.profiles.map(p => ({ id: p.id || 'p' + Math.random().toString(36).slice(2, 7), name: p.name || 'Профиль', data: Object.assign(DEF_PROFILE(), p.data || {}) }));
      State.cur = 0; saveProfiles(); renderAllStatic();
      toast(t('dash.imported'), State.profiles.length + ' профилей', '↑');
    } catch (e) { toast(t('dash.badImport'), '', '!'); }
  };
  r.readAsText(file);
}
function resetAll() {
  me().data = DEF_PROFILE(); saveProfiles(); renderAllStatic(); toast('Сброшено', me().name, '⌫');
}
function clearHistory() { D().history = []; saveProfiles(); renderDash(); toast('История очищена', '', '⌫'); }
function clearFav() { D().fav = []; saveProfiles(); renderDash(); toast('Избранное очищено', '', '⌫'); }
function addProfile() {
  if (State.profiles.length >= 6) { toast('Максимум 6 профилей', '', '!'); return; }
  const body = el('div');
  body.innerHTML = '<p>' + esc(t('dash.profileAsk')) + '</p><input id="npName" type="text" class="cmdk__in" style="width:100%;border:1px solid var(--line2);border-radius:10px;padding:12px 14px" maxlength="18">';
  modal({ title: t('dash.addProfile'), body: body, buttons: [{ label: t('common.cancel') }, {
    label: t('common.ok'), primary: true, onClick: () => {
      const v = ($('#npName') || {}).value; const name = (v || '').trim() || ('Ученик ' + (State.profiles.length + 1));
      State.profiles.push({ id: 'p' + Date.now().toString(36), name: name, data: DEF_PROFILE() });
      State.cur = State.profiles.length - 1; saveProfiles(); renderAllStatic(); toast(t('dash.added'), name, '+');
    }
  }] });
  setTimeout(() => { const i = $('#npName'); if (i) { i.focus(); i.onkeydown = e => { if (e.key === 'Enter') { const b = $$('.modal__f .btn--primary')[0]; if (b) b.click(); } }; } }, 80);
}
function syncNavXP() {
  const li = levelInfo(D().xp);
  $('#xpLevel').textContent = li.level;
  $('#xpNow').textContent = fmtNum(D().xp);
  const C = 2 * Math.PI * 15.5;
  const r = $('#xpRing'); r.style.strokeDasharray = C; r.style.strokeDashoffset = C * (1 - li.pct);
  $('#streakNum').textContent = D().streakDays || 0;
  const pill = $('#xpPill'); pill.title = rankOf(li.level) + ' · ' + t('xp.level') + ' ' + li.level + ' · ' + li.inLevel + '/' + li.need + ' XP';
}
function announce(msg) { const l = $('#live'); if (l) l.textContent = msg; }

/* ─────────── 20. статический рендер ─────────── */
function renderAllStatic() {
  applyI18n();
  const nav = $('#footNav');
  if (nav) nav.innerHTML = [['home', 'nav.home'], ['setup', 'nav.setup'], ['dash', 'nav.dash'], ['library', 'nav.library'], ['open', 'nav.open'], ['about', 'nav.about']]
    .map(x => '<a href="#' + x[0] + '" data-route="' + x[0] + '">' + esc(t(x[1])) + '</a>').join('');
  $('#footVersion').textContent = 'v' + (META.version || '1.0.0') + ' · ' + fmtNum(TOTAL_Q) + ' ' + t('common.q');
  $('#footYear').textContent = new Date().getFullYear();
  renderTicker();
  if (Router.cur === 'home') SCREENS.home.enter();
  if (Router.cur === 'dash') renderDash();
  if (Router.cur === 'about') SCREENS.about.enter();
  if (Router.cur === 'open') renderOpen();
  syncNavXP(); syncQuick();
}

/* ─────────── 21. события ─────────── */
function bindEvents() {
  // навигация
  $$('[data-route]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); Router.go(a.dataset.route); }));
  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('[data-route]');
    if (a && !a.dataset.bound) { e.preventDefault(); Router.go(a.dataset.route); }
  });
  window.addEventListener('hashchange', () => {
    const h = Router.fromHash();
    if (h !== Router.cur) Router.go(h);
    applyHashParams();
  });
  $('#btnBurger').onclick = () => { const n = $('#navLinks'); const o = n.classList.toggle('is-open'); $('#btnBurger').setAttribute('aria-expanded', o ? 'true' : 'false'); };
  // тап/клик по QKC — слова красиво падают вниз каскадом (работает на телефонах)
  const brandEl = $('.brand'), brandDrop = $('#brandDrop');
  if (brandEl && brandDrop) {
    let bdT1 = 0, bdT2 = 0;
    brandEl.addEventListener('click', () => {
      const r = brandEl.getBoundingClientRect();
      brandDrop.style.left = Math.max(10, r.left) + 'px';
      brandDrop.style.top = (r.bottom + 10) + 'px';
      brandDrop.classList.remove('is-on', 'is-out');
      void brandDrop.offsetWidth;
      brandDrop.classList.add('is-on');
      clearTimeout(bdT1); clearTimeout(bdT2);
      bdT1 = setTimeout(() => brandDrop.classList.add('is-out'), 2300);
      bdT2 = setTimeout(() => brandDrop.classList.remove('is-on', 'is-out'), 2900);
    });
  }
  $('#heroStart').onclick = () => { Router.go('setup'); };
  $('#ctaStart').onclick = () => { Router.go('setup'); };
  $('#heroSurprise').onclick = randomTest;
  $('#quickGo').onclick = () => {
    if (!(Wizard.grade != null && Wizard.subject)) { Router.go('setup'); return; }
    startTest({ grade: Wizard.grade, subject: Wizard.subject, periods: Wizard.periods.slice(), count: Wizard.count, mode: Wizard.mode, topics: Wizard.topics.slice() });
    if (Wizard.topics.length) window.__ouri_topic_run = true;
  };
  $('#featMore').onclick = () => { const list = FEATURES.filter(f => !featCat || f[0] === featCat); featShown = featShown >= list.length ? 24 : featShown + 36; renderFeatures(); };
  $('#btnTheme').onclick = toggleTheme;
  $('#btnSound').onclick = () => { State.settings.sound = !State.settings.sound; saveSettings(); applySettings(); Sound.play('select'); toast(State.settings.sound ? t('toast.soundOn') : t('toast.soundOff'), '', State.settings.sound ? '♪' : '✕'); };
  $('#btnStreak').onclick = () => { Router.go('dash'); };
  $('#btnCmd').onclick = () => Cmd.open();
  $('#btnStreak').title = 'Серия: ' + (D().streakDays || 0) + ' дн.';

  // конструктор
  $('#subjSearch').addEventListener('input', debounce(renderSubjects, 120));
  $('#setupReset').onclick = () => { Wizard.grade = null; Wizard.subject = null; Wizard.periods = [1]; Wizard.count = 20; Wizard.topics = []; Wizard.mode = 'classic'; SetupScreen.render(); syncQuick(); };
  $('#setupRandom').onclick = () => {
    const grades = []; for (let g = 1; g <= 11; g++) grades.push(g);
    Wizard.grade = pick(grades); Wizard.subject = pick(GRADE_SUBJECTS[Wizard.grade]); Wizard.periods = [rnd(1, 4)];
    Wizard.count = pick([10, 20, 30]); Wizard.mode = pick(MODES).id; Wizard.topics = [];
    SetupScreen.render(); syncQuick(); toast('Случайный набор', t('n' + Wizard.grade) + ' · ' + SUBJECTS[Wizard.subject].name, '⚄');
  };
  $('#setupStart').onclick = () => {
    if (!(Wizard.grade != null && Wizard.subject)) return;
    if (Wizard.topics.length) window.__ouri_topic_run = true;
    startTest({ grade: Wizard.grade, subject: Wizard.subject, periods: Wizard.periods.slice(), count: Wizard.count, mode: Wizard.mode, topics: Wizard.topics.slice() });
  };
  $('#trimesterMode').onchange = e => {
    State.settings.trimesters = e.target.checked; saveSettings();
    Wizard.periods = e.target.checked ? [1] : [1];
    SetupScreen.render(); syncQuick();
  };

  // тест
  $('#btnNext').onclick = () => { if (Quiz.cfg && Quiz.items[Quiz.idx] && Quiz.items[Quiz.idx].ty === 'input' && Quiz.answers[Quiz.idx].given == null) submitInput(); else next(); };
  $('#btnNextFb').onclick = () => next();
  $('#btnPrev').onclick = prev;
  $('#btnSkip').onclick = skipQ;
  $('#btnFinish').onclick = () => finish(false);
  $('#btnFlag').onclick = toggleFlag;
  $('#btnUndo').onclick = undoAnswer;
  $('#btnPalette').onclick = () => { const p = $('#palette'); p.hidden = !p.hidden; $('#btnPalette').setAttribute('aria-expanded', p.hidden ? 'false' : 'true'); if (!p.hidden) renderPalette(); };
  $('#quizExit').onclick = () => {
    if (!Quiz.cfg) { Router.go('home'); return; }
    confirmBox(t('nav.setup'), t('quiz.confirmExit'), () => { stopTimers(); Quiz.done = true; Store.del(RESUME_KEY); Router.go('setup'); });
  };
  $('#quizSound').onclick = () => { State.settings.sound = !State.settings.sound; saveSettings(); applySettings(); renderQuizSound(); };
  $('#quizFull').onclick = toggleFullscreen;
  $('#quizHelp').onclick = showKeys;
  $('#btnResume').onclick = () => togglePause(false);
  $('#answerInput').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); submitInput(); } });
  document.addEventListener('keydown', onKey);
  document.addEventListener('visibilitychange', () => { if (document.hidden && Router.cur === 'quiz' && !Quiz.done) togglePause(true); });
  window.addEventListener('beforeunload', e => { if (Router.cur === 'quiz' && !Quiz.done) { e.preventDefault(); e.returnValue = ''; } });

  // результат
  $$('#reviewFilter .seg__b').forEach(b => b.onclick = () => { $$('#reviewFilter .seg__b').forEach(x => x.classList.remove('is-on')); b.classList.add('is-on'); if (lastResult) renderReview(lastResult, b.dataset.f); });

  // прогресс
  $('#clearHistory').onclick = () => confirmBox(t('dash.clear'), t('dash.confirmHist'), clearHistory);
  $('#clearFav').onclick = clearFav;
  $('#addProfile').onclick = addProfile;
  $('#exportData').onclick = exportData;
  $('#importData').onclick = () => $('#importFile').click();
  $('#importFile').onchange = e => { if (e.target.files[0]) importData(e.target.files[0]); e.target.value = ''; };
  $('#resetAll').onclick = () => confirmBox(t('dash.reset'), t('dash.confirmReset'), resetAll);

  // решатели и форма отзыва
  bindFeedback();
  $$('#solvTabs .seg__b').forEach(b => b.onclick = () => {
    $$('#solvTabs .seg__b').forEach(x => x.classList.remove('is-on')); b.classList.add('is-on');
    $$('.solv__pane').forEach(p2 => { p2.hidden = p2.dataset.pane !== b.dataset.t; });
    Sound.play('select');
  });
  $('#mathGo').onclick = () => solveMath($('#mathIn').value);
  $('#mathIn').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); solveMath($('#mathIn').value); } });
  $('#rusGo').onclick = () => analyzeRus($('#rusIn').value);
  $('#rusIn').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); analyzeRus($('#rusIn').value); } });

  // библиотека
  $('#libSearch').addEventListener('input', debounce(e => { Lib.search = e.target.value.trim(); Lib.page = 0; loadLib(); }, 220));
  $('#libTrain').onclick = () => {
    if (!Lib.items.length) return;
    startTest({ grade: Lib.grade, subject: Lib.subj || Lib.items[0].subj, periods: Lib.q ? [Lib.q] : [], count: Math.min(20, Lib.items.length), mode: 'classic', topics: Lib.subj ? [] : [] });
  };

  // команды
  $('#cmdInput').addEventListener('input', e => { Cmd.sel = 0; Cmd.fill(e.target.value); });
  $('#cmdInput').addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); Cmd.move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); Cmd.move(-1); }
    else if (e.key === 'Enter') { e.preventDefault(); Cmd.run(); }
    else if (e.key === 'Escape') { Cmd.close(); }
  });
  $('#cmdk').addEventListener('click', e => { if (e.target.id === 'cmdk') Cmd.close(); });

  // скролл
  let lastY = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    const h = document.documentElement.scrollHeight - innerHeight;
    $('#scrollBar').style.width = (h > 0 ? (y / h * 100) : 0) + '%';
    $('#nav').classList.toggle('is-stuck', y > 12);
    $('#nav').classList.toggle('is-mini', y > 340);
    lastY = y;
  }, { passive: true });

  // магнитные кнопки
  $$('.magnetic').forEach(b => {
    b.addEventListener('pointermove', e => {
      if (!State.settings.motion) return;
      const r = b.getBoundingClientRect();
      b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.16) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.22) + 'px)';
    });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });

  // сеть
  const setNet = () => { const n = navigator.onLine; const s = $('#footStatus'); if (s) s.textContent = t(n ? 'foot.online' : 'foot.offline'); };
  window.addEventListener('online', () => { setNet(); toast(t('toast.online'), '', '⇅'); });
  window.addEventListener('offline', () => { setNet(); toast(t('toast.offline'), '', '⇅'); });
  setNet();

  // консоль-пасхалка
  try {
    console.log('%cQKC', 'font:700 46px/1 system-ui;letter-spacing:-3px');
    console.log('%cQuick Knowledge Check — продукт компании OuRi', 'color:#888');
    console.log('%cЧёрное. Белое. Знания. — ' + fmtNum(TOTAL_Q) + ' вопросов в базе', 'color:#888');
    window.ouri = { State: State, Bank: Bank, Quiz: Quiz, startTest: startTest, ACH: ACH, FEATURES: FEATURES };
  } catch (e) {}
}

function renderQuizSound() {
  const b = $('#quizSound'); if (!b) return;
  b.innerHTML = State.settings.sound
    ? '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/></svg>'
    : '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M17 9l4 6M21 9l-4 6"/></svg>';
  b.setAttribute('aria-pressed', State.settings.sound ? 'true' : 'false');
}
function toggleFullscreen() {
  const d = document;
  if (!d.fullscreenElement) { (d.documentElement.requestFullscreen ? d.documentElement.requestFullscreen() : Promise.reject()).catch(() => {}); }
  else if (d.exitFullscreen) d.exitFullscreen();
}

/* горячие клавиши */
function onKey(e) {
  const inField = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ''));
  const cmdK = (e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K' || e.key === 'л' || e.key === 'Л');
  if (cmdK) { e.preventDefault(); if ($('#cmdk').hidden) Cmd.open(); else Cmd.close(); return; }
  if (e.key === 'Escape') {
    if (!$('#cmdk').hidden) { Cmd.close(); return; }
    if (!$('#modalRoot').hidden) { closeModal(); return; }
    if (!$('#palette').hidden) { $('#palette').hidden = true; return; }
    if (Router.cur === 'quiz' && !Quiz.done) { togglePause(true); return; }
  }
  if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) { e.preventDefault(); openSettings(); return; }
  if (e.key === '?' || (e.key === '/' && e.shiftKey)) { if (!inField) { e.preventDefault(); showKeys(); return; } }
  if (inField) return;
  if (Router.cur === 'quiz' && Quiz.cfg && !Quiz.done) {
    const it = Quiz.items[Quiz.idx], a = Quiz.answers[Quiz.idx];
    if (/^[1-9]$/.test(e.key)) {
      const i = +e.key - 1;
      if (it.ty !== 'input' && i < (a._opts || it.o || []).length) { const b = $$('#answers .ans')[i]; if (b && !b.disabled) { e.preventDefault(); choose(i, b); } }
      return;
    }
    switch (e.key) {
      case 'Enter': e.preventDefault(); if (it.ty === 'input' && a.given == null) submitInput(); else next(); break;
      case 'ArrowRight': e.preventDefault(); next(); break;
      case 'ArrowLeft': e.preventDefault(); prev(); break;
      case 's': case 'S': case 'ы': case 'Ы': e.preventDefault(); toggleFlag(); break;
      case 'p': case 'P': case 'з': case 'З': e.preventDefault(); togglePause(); break;
      case 'f': case 'F': case 'а': case 'А': e.preventDefault(); finish(false); break;
      case 'n': case 'N': case 'т': case 'Т': e.preventDefault(); skipQ(); break;
      case 'u': case 'U': case 'г': case 'Г': e.preventDefault(); undoAnswer(); break;
      case ' ': e.preventDefault(); if (it.ty !== 'input') { const i = 0; } else $('#answerInput').focus(); break;
    }
    return;
  }
  switch (e.key) {
    case 'g': case 'G': Router.go('home'); break;
    case 't': case 'T': Router.go('setup'); break;
    case 'd': case 'D': Router.go('dash'); break;
    case 'l': case 'L': Router.go('library'); break;
  }
}

/* параметры в хэше (#setup?g=7&s=algebra&p=2&n=20&m=exam) */
function applyHashParams() {
  const h = location.hash || '';
  if (h.indexOf('?') < 0) return;
  const qs = h.split('?')[1];
  const p = {}; qs.split('&').forEach(kv => { const a = kv.split('='); p[a[0]] = decodeURIComponent(a[1] || ''); });
  if (p.g && p.s) {
    Wizard.grade = +p.g; Wizard.subject = p.s;
    Wizard.periods = p.p && p.p !== 'all' ? String(p.p).split('+').map(Number) : [];
    Wizard.count = +p.n || 20; Wizard.mode = p.m || 'classic';
    if (Router.cur === 'setup') SetupScreen.render();
  }
}
function buildShareUrl() {
  return location.origin + location.pathname + '#setup?g=' + Wizard.grade + '&s=' + Wizard.subject + '&p=' + (Wizard.periods.length ? Wizard.periods.join('+') : 'all') + '&n=' + Wizard.count + '&m=' + Wizard.mode;
}

/* ─────────── 22. service worker ─────────── */
function registerSW() {
  if (!('serviceWorker' in navigator)) return;
  if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') return;
  window.addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
}


/* ─────────── 22.5 программа по классам ─────────── */
const TOPIC_NOTES_RU = {
  'Сложение и вычитание': 'Учимся складывать и вычитать числа: сначала до 10, потом до 100 и больше.',
  'Таблица умножения': 'Учим наизусть таблицу умножения и решаем примеры на деление.',
  'Задачи': 'Читаем условие, рисуем схему и решаем задачи в 1–2 действия.',
  'Задачи на движение': 'Скорость, время и путь: как они связаны и как находить каждое.',
  'Геометрия': 'Фигуры, периметр и площадь: измеряем, считаем, чертим.',
  'Геометрия: треугольник': 'Треугольники: углы, стороны, признаки равенства.',
  'Геометрия: окружность': 'Окружность и круг: радиус, диаметр, длина, площадь.',
  'Дроби': 'Доли и дроби: что такое числитель и знаменатель, как сравнивать и складывать.',
  'Обыкновенные дроби': 'Дроби со знаменателем: сокращение, приведение, действия.',
  'Проценты': 'Процент — это сотая часть: находим процент числа и число по проценту.',
  'Уравнения': 'Учимся находить неизвестное: что такое уравнение и корень уравнения.',
  'Линейные уравнения': 'Уравнения вида ax + b = c и способы их решения.',
  'Степень': 'Запись умножения одинаковых множителей: свойства степеней.',
  'Многочлены': 'Складываем, вычитаем и умножаем буквенные выражения.',
  'Одночлены': 'Произведение чисел и букв: приведение к стандартному виду.',
  'Формулы сокращённого умножения': 'Квадрат суммы и разности, разность квадратов — учимся применять.',
  'Квадратные уравнения': 'Дискриминант и теорема Виета: способы найти корни.',
  'Квадратичная функция': 'Парабола: вершина, ветви, график.',
  'Квадратные корни': 'Что такое корень из числа и как с ним работать.',
  'Рациональные дроби': 'Дроби с буквами в знаменателе: сложение и сокращение.',
  'Неравенства': 'Сравниваем выражения и решаем неравенства.',
  'Прогрессии': 'Последовательности по правилу: арифметическая и геометрическая.',
  'Производная': 'Скорость изменения функции: правила дифференцирования и применение.',
  'Применение производной': 'Экстремумы, касательная, задачи на оптимум.',
  'Первообразная': 'Функция, производная которой равна данной.',
  'Интеграл': 'Площадь под графиком и определённый интеграл.',
  'Логарифмы': 'Показатель, в который нужно возвести основание: свойства и уравнения.',
  'Показательные уравнения': 'Уравнения, где неизвестное стоит в показателе.',
  'Тригонометрия': 'Синус, косинус, тангенс: таблицы значений и тождества.',
  'Стереометрия': 'Объёмы и поверхности тел: куб, призма, цилиндр, конус, шар.',
  'Комбинаторика': 'Способы подсчёта вариантов: перестановки, размещения, сочетания.',
  'Вероятность': 'Шанс события: от отношения числа исходов до формул.',
  'Функции': 'Что такое функция, график, область определения и значений.',
  'Линейная функция': 'Прямая на координатной плоскости: y = kx + b.',
  'Векторы': 'Направленные отрезки: действия и скалярное произведение.',
  'Слоги': 'Делим слова на слоги: слогов столько, сколько гласных.',
  'Звуки и буквы': 'Различаем гласные и согласные, звонкие и глухие, твёрдые и мягкие.',
  'Ударение': 'Учимся ставить ударение правильно — в том числе в «коварных» словах.',
  'Орфография': 'Правила написания слов: безударные гласные, парные согласные и другие.',
  'Орфоэпия': 'Как правильно произносить слова: нормы ударения и произношения.',
  'Орфоэпия (нормы ЕГЭ)': 'Слова-ловушки из банка заданий ЕГЭ: учим ударения.',
  'Правописание ЖИ–ШИ': 'Классическое правило: ЖИ и ШИ пиши с буквой И.',
  'Правописание ЧА–ЩА': 'ЧА и ЩА пиши с буквой А.',
  'Правописание ЧУ–ЩУ': 'ЧУ и ЩУ пиши с буквой У.',
  'Парные согласные': 'Проверяем согласные в корне изменением слова.',
  'Безударные гласные': 'Подбираем проверочное слово, чтобы услышать гласную.',
  'Состав слова': 'Корень, приставка, суффикс, окончание: из чего состоит слово.',
  'Части речи': 'Существительное, прилагательное, глагол и другие: учимся различать.',
  'Падежи': 'Шесть падежей русского языка и их вопросы.',
  'Глагол': 'Время, лицо, спряжение: всё о глаголе.',
  'Имя существительное': 'Род, число, падеж, склонение существительных.',
  'Местоимение': 'Слова-заместители: разряды местоимений.',
  'Причастие': 'Признак по действию: образуем и пишем правильно.',
  'Деепричастие': 'Добавочное действие: обороты и запятые.',
  'Наречие': 'Признак действия: степени сравнения, правописание.',
  'Служебные части речи': 'Предлоги, союзы, частицы и их роль.',
  'Н/НН': 'Когда пишется одна Н, а когда две.',
  'Орфография НЕ': 'Слитно или раздельно с разными частями речи.',
  'Синтаксис': 'Словосочетание и предложение: главные и второстепенные члены.',
  'Пунктуация': 'Где ставить запятые, тире и двоеточия.',
  'Однородные члены': 'Перечисления в предложении и знаки между ними.',
  'Односоставные предложения': 'Предложения с одним главным членом и их типы.',
  'Обособленные члены': 'Выделяем запятыми обороты и уточнения.',
  'Вводные слова': 'Слова-оценки и их выделение на письме.',
  'Сложное предложение': 'ССП, СПП и БСП: учимся видеть части и ставить знаки.',
  'Сложноподчинённое предложение': 'Главная и придаточная части, союзы и знаки.',
  'Средства выразительности': 'Метафора, эпитет, сравнение и другие украшения речи.',
  'Лексика': 'Синонимы, антонимы, омонимы и значение слов.',
  'Лексика · синонимы': 'Близкие по значению слова: подбираем пары.',
  'Лексика · антонимы': 'Противоположные по значению слова.',
  'Фразеология': 'Устойчивые выражения и их смысл.',
  'Стили речи': 'Научный, деловой, публицистический, художественный, разговорный.',
  'Типы речи': 'Повествование, описание, рассуждение.',
  'Текст': 'Тема, основная мысль, строение текста.',
  'Авторы и произведения': 'Кто написал и что: запоминаем пары «автор — текст».',
  'Герои произведений': 'Кто есть кто в книгах школьной программы.',
  'Теория литературы': 'Жанры, роды литературы и литературные термины.',
  'Литературные направления': 'Классицизм, романтизм, реализм и другие.',
  'Цитаты': 'Узнаём строки и их авторов.',
  'Фольклор': 'Устное народное творчество: сказки, былины, пословицы.',
  'Жанры': 'Роды и жанры литературы: эпос, лирика, драма.',
  'Даты и события': 'Учим главные даты и связываем их с событиями.',
  'Исторические личности': 'Кто есть кто в истории: правители, полководцы, учёные.',
  'Исторические термины': 'Понятия, без которых не понять учебник истории.',
  'Хронология': 'Учимся считать века и расставлять события по порядку.',
  'Историческая наука': 'Вспомогательные исторические дисциплины и источники.',
  'Материки и океаны': 'Карта мира: материки, океаны, их особенности.',
  'Страны и столицы': 'Учим пары «страна — столица».',
  'Реки России': 'Крупнейшие реки и куда они впадают.',
  'Озёра России': 'От Байкала до Ладоги: особенности озёр.',
  'Горы России': 'Урал, Кавказ, Алтай и другие горные системы.',
  'Равнины России': 'Крупные равнины и плоскогорья страны.',
  'Моря России': 'Моря трёх океанов у берегов России.',
  'Климат': 'Погода и климат: температура, осадки, пояса.',
  'Население': 'Численность, плотность и размещение людей.',
  'Масштаб': 'Отношение на карте к местности: решаем задачи.',
  'Часовые пояса': 'Поясное время и задачи на разницу времени.',
  'Мировое хозяйство': 'Экономика мира: отрасли, страны, связи.',
  'Глобальные проблемы': 'Проблемы всей планеты и пути их решения.',
  'Клетка': 'Строение клетки: органоиды и их работа.',
  'Цитология': 'Клетка под микроскопом: органоиды и их функции.',
  'Фотосинтез': 'Как растения делают пищу и выделяют кислород.',
  'Дыхание растений': 'Растения дышат круглосуточно: поглощают кислород.',
  'ДНК': 'Молекула наследственности: комплементарность и расчёты.',
  'Биосинтез белка': 'От гена к белку: транскрипция и трансляция.',
  'Энергетический обмен': 'Как клетка получает энергию: гликолиз и дыхание.',
  'Генетика': 'Законы Менделя и задачи на скрещивание.',
  'Клетка и деление': 'Митоз и мейоз: наборы хромосом.',
  'Экосистемы': 'Цепи питания и правило 10 процентов.',
  'Экология': 'Взаимосвязи организмов и среды.',
  'Эволюция': 'Как меняются виды: отбор и приспособленность.',
  'Селекция': 'Создание сортов и пород человеком.',
  'Биосфера': 'Живая оболочка Земли и учение Вернадского.',
  'Анатомия человека': 'Системы органов: как работает наше тело.',
  'Системы органов': 'Каждая система и её органы: учим пары.',
  'Кровообращение': 'Сердце, сосуды, круги кровообращения.',
  'Пищеварение': 'Путь пищи и органы пищеварения.',
  'Дыхание': 'Лёгкие и газообмен.',
  'Нервная система': 'Нейроны, рефлексы, отделы нервной системы.',
  'Витамины': 'Что даёт каждый витамин и чем грозит нехватка.',
  'Атом и молекула': 'Строение вещества: атомы, молекулы, массы.',
  'Количество вещества': 'Моль, молярная масса, число Авогадро.',
  'Растворы': 'Массовая доля и приготовление растворов.',
  'Углеводороды': 'Алканы, алкены, алкины: формулы и названия.',
  'Гидролиз солей': 'Какая среда будет в растворе соли.',
  'ОВР': 'Окислительно-восстановительные реакции и степени окисления.',
  'Электролиты': 'Диссоциация и ионы в растворе.',
  'Ионные уравнения': 'Какие ионы дают осадок, газ или воду.',
  'Классы неорганических веществ': 'Кислоты, основания, соли, оксиды.',
  'Скорость': 'Путь, время, скорость: первые формулы физики.',
  'Плотность': 'Масса и объём: как найти плотность.',
  'Сила тяжести': 'Сила притяжения Земли: F = mg.',
  'Давление': 'Сила на площадь: паскаль и задачи.',
  'Работа и мощность': 'Механическая работа и мощность.',
  'Энергия': 'Потенциальная и кинетическая энергия, закон сохранения.',
  'Электричество': 'Ток, напряжение, сопротивление: закон Ома.',
  'Тепловые явления': 'Нагрев, плавление, испарение: количество теплоты.',
  'Кинематика': 'Движение тел: скорость, ускорение, путь.',
  'Динамика': 'Законы Ньютона и силы.',
  'Импульс': 'Импульс тела и закон сохранения импульса.',
  'Колебания и волны': 'Период, частота, длина волны.',
  'МКТ': 'Молекулярно-кинетическая теория: моли и уравнение состояния.',
  'Электростатика': 'Заряды, поле, конденсаторы.',
  'Vocabulary': 'Словарный запас: учим слова по темам.',
  'Irregular verbs': 'Неправильные глаголы: три формы наизусть.',
  'Regular verbs': 'Правильные глаголы: окончание -ed.',
  'Comparatives': 'Степени сравнения прилагательных.',
  'Superlatives': 'Превосходная степень: the + -est.',
  'Plurals': 'Множественное число существительных.',
  'Articles': 'Артикли a, an, the и когда они не нужны.',
  'to be': 'Глагол-связка am, is, are.',
  'Present Simple': 'Настоящее простое время: привычки и факты.',
  'Present Continuous': 'Действие прямо сейчас.',
  'Past Simple': 'Прошедшее время: факты прошлого.',
  'Present Perfect': 'Результат к настоящему моменту.',
  'Conditionals': 'Условия: if-предложения трёх типов.',
  'Passive Voice': 'Страдательный залог: be + V3.',
  'Modals': 'Модальные глаголы: can, must, may, should.',
  'Culture': 'Страноведение: факты о странах и традициях.',
  'Spelling': 'Правописание английских слов.',
  'Системы счисления': 'Двоичная, десятичная, шестнадцатеричная: переводы.',
  'Информация': 'Биты, байты, объём сообщений.',
  'Логика': 'И, ИЛИ, НЕ: логические операции.',
  'Программирование': 'Основы Python: вывод, циклы, списки.',
  'Алгоритмы': 'Свойства алгоритмов и их сложность.',
  'Устройства компьютера': 'Ввод, вывод, хранение и обработка.',
  'Файлы': 'Расширения и типы файлов.',
  'Сети': 'Интернет, браузеры, электронная почта.',
  'Безопасность': 'Пароли и безопасное поведение в сети.',
  'Человек и общество': 'Человек среди людей: деятельность и общение.',
  'Право': 'Законы, права и обязанности.',
  'Экономика': 'Рынок, деньги, налоги и бюджет.',
  'Экономика и право': 'Основы экономики и права рядом.',
  'Политика': 'Власть, государство, выборы.',
  'Социальные отношения': 'Группы, статусы, роли, конфликты.',
  'Познание': 'Как человек познаёт мир: чувства и разум.',
  'Духовная культура': 'Наука, искусство, религия, мораль.',
  'Основы права': 'Конституция и ветви власти.',
  'Безопасность': 'Правила безопасного поведения.',
  'Экстренные службы': 'Номера и правила вызова помощи.',
  'Первая помощь': 'Как помочь до приезда врачей.',
  'Пожарная безопасность': 'Правила при пожаре и профилактика.',
  'Природные опасности': 'Гроза, землетрясение, наводнение: как себя вести.',
  'ЧС': 'Чрезвычайные ситуации и действия при них.',
  'Физическая культура': 'Качества, разминка, самоконтроль.',
  'Лёгкая атлетика': 'Бег, прыжки, метания: задачи и правила.',
  'Самоконтроль': 'Пульс и наблюдение за своим состоянием.',
  'Олимпизм': 'Олимпийские игры и их символы.',
  'Основы изобразительного искусства': 'Жанры, композиция, материалы.',
  'Цветоведение': 'Основные и составные цвета, тёплые и холодные.',
  'Великие мастера': 'Художники и их картины.',
  'Стили искусства': 'Направления в искусстве.',
  'Народные промыслы': 'Хохлома, гжель и другие росписи.',
  'Основы музыки': 'Ноты, длительности, темп, динамика.',
  'Композиторы': 'Кто написал знакомую музыку.',
  'Музыкальные инструменты': 'Группы инструментов и их голоса.',
  'Жанры': 'Музыкальные жанры и формы.',
  'Технология': 'Материалы, инструменты, технологии обработки.',
  'Материаловедение': 'Свойства материалов и как их определить.',
  'Безопасность': 'Безопасные приёмы работы.',
  'Соединения': 'Виды соединений деталей.',
  'Механизмы': 'Передачи движения и их отношения.'
};
function topicNote(tp) {
  if (LANG === 'ru' && TOPIC_NOTES_RU[tp]) return TOPIC_NOTES_RU[tp];
  return LANG === 'ru' ? 'Раздел школьной программы этого класса.' : 'A section of the school curriculum for this grade.';
}
const Prog = { grade: 5, subj: null };
SCREENS.program = { enter() { renderProgGrades(); renderProgSubjects(); renderProgQuarters(); } };
function renderProgGrades() {
  const box = $('#progGrade'); if (!box) return;
  box.innerHTML = '';
  for (let g = 0; g <= 11; g++) {
    const b = el('button', 'chip' + (Prog.grade === g ? ' is-on' : ''), g === 0 ? '0' : String(g));
    b.title = t('n' + g);
    b.onclick = () => { Prog.grade = g; if (Prog.subj && (GRADE_SUBJECTS[g] || []).indexOf(Prog.subj) < 0) Prog.subj = null; renderProgGrades(); renderProgSubjects(); renderProgQuarters(); };
    box.appendChild(b);
  }
}
function renderProgSubjects() {
  const box = $('#progSubject'); if (!box) return;
  box.innerHTML = '';
  (GRADE_SUBJECTS[Prog.grade] || []).forEach(k => {
    const b = el('button', 'chip' + (Prog.subj === k ? ' is-on' : ''), SUBJECTS[k].name);
    b.onclick = () => { Prog.subj = k; renderProgSubjects(); renderProgQuarters(); };
    box.appendChild(b);
  });
}
function renderProgQuarters() {
  const box = $('#progQuarters'); if (!box) return;
  if (!Prog.subj) { box.innerHTML = '<div class="empty">' + esc(t('prog.empty')) + '</div>'; return; }
  box.innerHTML = '<div class="empty">' + esc(t('lib.loading', { n: Prog.grade })) + '</div>';
  Bank.load(Prog.grade).then(() => {
    box.innerHTML = '';
    const b = BANKS[Prog.grade][Prog.subj] || {};
    [1, 2, 3, 4].forEach(q => {
      const items = b[q] || [];
      const byTopic = {};
      items.forEach(it => { const tp = baseTopic(it.tp) || '—'; byTopic[tp] = (byTopic[tp] || 0) + 1; });
      const keys = Object.keys(byTopic).sort((x, y) => byTopic[y] - byTopic[x]);
      const panel = el('div', 'pq');
      let html = '<div class="pq__h"><b>' + esc(t('setup.q', { n: q })) + '</b><i>' + esc(t('prog.qcount', { n: items.length })) + '</i></div><div class="pq__list">';
      keys.forEach(k => {
        html += '<div class="pq__t"><b>' + esc(k) + '</b><span>' + esc(topicNote(k)) + '</span><i>' + byTopic[k] + ' ' + esc(t('common.q')) + '</i></div>';
      });
      html += '</div>';
      panel.innerHTML = html;
      const btn = el('button', 'btn btn--ghost btn--sm', esc(t('prog.train')));
      btn.onclick = () => startTest({ grade: Prog.grade, subject: Prog.subj, periods: [q], count: Math.min(20, items.length || 10), mode: 'classic' });
      panel.appendChild(btn);
      box.appendChild(panel);
    });
  });
}

/* ─────────── 22.6 решатели (BETA) ─────────── */
const SUPPORT_EMAIL = 'juravlev.aleksandr2020@gmail.com';
function num2str(v) {
  if (!isFinite(v)) return '∞';
  const r = Math.round(v * 1e6) / 1e6;
  return String(r).replace('.', ',');
}
function tokenizeMath(src) {
  const s = String(src).replace(/,/g, '.').replace(/×/g, '*').replace(/÷/g, '/').replace(/−/g, '-').replace(/·/g, '*').replace(/\s+/g, '');
  if (!s) return null;
  const toks = []; let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (/[0-9.]/.test(c)) { let j = i; while (j < s.length && /[0-9.]/.test(s[j])) j++; const v = parseFloat(s.slice(i, j)); if (isNaN(v)) return null; toks.push({ t: 'num', v: v }); i = j; continue; }
    if (c === 'x' || c === 'X' || c === 'х' || c === 'Х') { toks.push({ t: 'x' }); i++; continue; }
    if ('+-*/^()='.indexOf(c) >= 0) { toks.push({ t: c }); i++; continue; }
    return null;
  }
  return toks;
}
function parseMath(toks) {
  let p = 0;
  const err = () => { throw new Error('parse'); };
  function expr() { let n = term(); while (p < toks.length && (toks[p].t === '+' || toks[p].t === '-')) { const op = toks[p++].t; n = { t: 'op', op: op, l: n, r: term() }; } return n; }
  function term() { let n = factor(); while (p < toks.length && (toks[p].t === '*' || toks[p].t === '/')) { const op = toks[p++].t; n = { t: 'op', op: op, l: n, r: factor() }; } return n; }
  function factor() { let n = unary(); if (p < toks.length && toks[p].t === '^') { p++; n = { t: 'op', op: '^', l: n, r: factor() }; } return n; }
  function unary() { if (p < toks.length && (toks[p].t === '-' || toks[p].t === '+')) { const op = toks[p++].t; const n = unary(); return op === '-' ? { t: 'op', op: '-', l: { t: 'num', v: 0 }, r: n } : n; } return atom(); }
  function atom() {
    if (p >= toks.length) err();
    const tk = toks[p];
    if (tk.t === 'num') { p++; return { t: 'num', v: tk.v }; }
    if (tk.t === 'x') { p++; return { t: 'x' }; }
    if (tk.t === '(') { p++; const n = expr(); if (!toks[p] || toks[p].t !== ')') err(); p++; return n; }
    err();
  }
  const root = expr();
  if (p !== toks.length) err();
  return root;
}
function evalSteps(node, steps) {
  if (node.t === 'num') return { v: node.v, s: num2str(node.v) };
  if (node.t === 'x') throw new Error('x');
  const L = evalSteps(node.l, steps), R = evalSteps(node.r, steps);
  let v;
  switch (node.op) {
    case '+': v = L.v + R.v; break;
    case '-': v = L.v - R.v; break;
    case '*': v = L.v * R.v; break;
    case '/': if (R.v === 0) throw new Error('div0'); v = L.v / R.v; break;
    case '^': v = Math.pow(L.v, R.v); break;
    default: throw new Error('op');
  }
  steps.push(L.s + ' ' + node.op + ' ' + R.s + ' = ' + num2str(v));
  return { v: v, s: num2str(v) };
}
function linEval(node) {
  if (node.t === 'num') return { k: 0, b: node.v };
  if (node.t === 'x') return { k: 1, b: 0 };
  const L = linEval(node.l), R = linEval(node.r);
  switch (node.op) {
    case '+': return { k: L.k + R.k, b: L.b + R.b };
    case '-': return { k: L.k - R.k, b: L.b - R.b };
    case '*':
      if (L.k === 0) return { k: R.k * L.b, b: R.b * L.b };
      if (R.k === 0) return { k: L.k * R.b, b: L.b * R.b };
      throw new Error('nonlinear');
    case '/':
      if (R.k !== 0 || R.b === 0) throw new Error('nonlinear');
      return { k: L.k / R.b, b: L.b / R.b };
    case '^':
      if (L.k !== 0 || R.k !== 0 || Math.round(R.b) !== R.b) throw new Error('nonlinear');
      return { k: 0, b: Math.pow(L.b, R.b) };
  }
  throw new Error('op');
}
function lin2str(a) {
  if (a.k === 0) return num2str(a.b);
  let s2 = (a.k === 1 ? '' : a.k === -1 ? '−' : num2str(a.k)) + 'x';
  if (a.b) s2 += (a.b > 0 ? ' + ' : ' − ') + num2str(Math.abs(a.b));
  return s2;
}
function solveMath(src) {
  const out = $('#mathOut'); out.innerHTML = '';
  const push = (label, txt, cls) => {
    const n = el('div', 'solv__step' + (cls ? ' ' + cls : ''));
    n.innerHTML = (label ? '<b>' + esc(label) + '</b>' : '') + '<span>' + esc(txt) + '</span>';
    out.appendChild(n); return n;
  };
  try {
    const toks = tokenizeMath(src);
    if (!toks || !toks.length) throw new Error('tok');
    const eqAt = toks.findIndex(tk => tk.t === '=');
    if (eqAt >= 0) {
      const L = parseMath(toks.slice(0, eqAt)), R = parseMath(toks.slice(eqAt + 1));
      const a = linEval(L), b = linEval(R);
      push('1', lin2str(a) + ' = ' + lin2str(b));
      const k = a.k - b.k, c = b.b - a.b;
      push('2', (k ? num2str(k) + 'x' : '0') + ' = ' + num2str(c) + '  ·  ' + (LANG === 'ru' ? 'переносим x влево, числа вправо' : 'move x left, numbers right'));
      if (k === 0) { push('!', c === 0 ? (LANG === 'ru' ? 'x — любое число' : 'x is any number') : (LANG === 'ru' ? 'решений нет' : 'no solutions'), 'solv__step--err'); return; }
      push(t('solv.ans'), 'x = ' + num2str(c / k), 'solv__step--final');
    } else {
      const steps = [];
      const root = parseMath(toks);
      if (root.t === 'num') { push(t('solv.ans'), num2str(root.v), 'solv__step--final'); return; }
      const res = evalSteps(root, steps);
      push('', src);
      steps.forEach((st, i) => push(String(i + 1), st));
      push(t('solv.ans'), res.s, 'solv__step--final');
    }
  } catch (e) {
    push('!', t('solv.err'), 'solv__step--err');
  }
  const note = el('div', 'solv__note'); note.textContent = t('solv.note'); out.appendChild(note);
}
const STRESS_JS = { мама:1, папа:1, каша:1, луна:2, вода:2, корова:2, молоко:3, собака:2, машина:2, учитель:2, ученик:3, библиотека:4, квартира:2, корзина:2, рисунок:2, планета:2, столица:2, россия:2, животное:2, растение:2, космонавт:3, президент:3, государство:3, горизонт:3, компас:1, звонит:2, договор:3, каталог:3, документ:3, квартал:2, торты:1, банты:1, шарфы:1, свекла:1, щавель:1, жалюзи:3, портфель:2, километр:3, сантиметр:3, алфавит:3, магазин:3, директор:2, инженер:3, шофер:2, цемент:2, красивее:2, баловать:3, кухонный:1, сироты:2, средства:1, деревья:2, суббота:2, праздник:1, морковь:2, карандаш:3, воробей:3, петух:2, лиса:2, рука:2, нога:2, голова:3, борода:3, облако:1, дерево:1, улица:1, яблоко:1, малина:2, рябина:2, скворец:2, трактор:1, завод:2, комната:1, береза:2, осина:2, дорога:2, корова:2, сорока:3, лягушка:2, черепаха:3, медведь:2, петух:2, молоко:3, колесо:3, крыльцо:3, письмо:2, окно:2, стекло:3 };
const VOWJS = 'аеёиоуыэюя', CONSJS = 'бвгджзклмнпрстфхцчшщ';
const VOICEDJS = 'бвгджзлмнр';
const DEVOICE = { б:'п', в:'ф', г:'к', д:'т', ж:'ш', з:'с' };
const UNVOICED = 'пфтскхшщчц';
function sylJs(w) {
  const parts = []; let cur = '';
  for (const ch of w) { cur += ch; if (VOWJS.indexOf(ch) >= 0) { parts.push(cur); cur = ''; } }
  if (cur) { if (parts.length) parts[parts.length - 1] += cur; else parts.push(cur); }
  return parts;
}
function analyzeRus(word) {
  const out = $('#rusOut'); out.innerHTML = '';
  const row = (k, v) => { const n = el('div', 'rus-line'); n.innerHTML = '<b>' + esc(k) + '</b><span>' + esc(v) + '</span>'; out.appendChild(n); };
  const w0 = String(word || '').trim().toLowerCase();
  const w = w0.replace(/[^а-яё]/g, '');
  if (!w || w.length < 2 || w !== w0) { row('!', t('solv.err') + ' (' + (LANG === 'ru' ? 'только одно слово кириллицей' : 'one Cyrillic word only') + ')'); return; }
  const syl = sylJs(w);
  const letters = Array.from(w);
  const vow = letters.filter(c => VOWJS.indexOf(c) >= 0);
  const cons = letters.filter(c => CONSJS.indexOf(c) >= 0);
  row(t('solv.letters'), letters.length + ': ' + letters.join(', '));
  row(t('solv.syl'), t('solv.sylN', { n: syl.length }) + ' → ' + syl.join('-'));
  row(t('solv.vow'), vow.join(', ') + ' (' + vow.length + ')');
  row(t('solv.cons'), (cons.join(', ') || '—') + ' (' + cons.length + ')');
  const st = STRESS_JS[w.replace(/ё/g, 'е')];
  row(t('solv.stress'), st ? (LANG === 'ru' ? 'на ' + st + '-й слог («' + syl[st - 1] + '»)' : 'on syllable ' + st) : t('solv.stressNA'));
  const scheme = letters.map((c, i) => {
    if (VOWJS.indexOf(c) >= 0) {
      const stressed = !!(st && syl[st - 1] && syl[st - 1].indexOf(c) >= 0);
      return '[' + c + (stressed ? '́' : '') + '] ' + (stressed ? (LANG === 'ru' ? 'ударн.' : 'stressed') : (LANG === 'ru' ? 'безуд.' : 'unstressed'));
    }
    if (CONSJS.indexOf(c) >= 0) {
      const next = letters[i + 1] || '';
      const soft = 'еёиюь'.indexOf(next) >= 0;
      let ch = c;
      if (DEVOICE[c] && (i === letters.length - 1 || (CONSJS.indexOf(next) >= 0 && UNVOICED.indexOf(next) >= 0))) ch = DEVOICE[c];
      const alwaysHard = 'шжц'.indexOf(c) >= 0, alwaysSoft = 'чщй'.indexOf(c) >= 0;
      const softF = alwaysHard ? false : alwaysSoft ? true : soft;
      const voiced = VOICEDJS.indexOf(c) >= 0 && !(i === letters.length - 1 || (CONSJS.indexOf(next) >= 0 && UNVOICED.indexOf(next) >= 0));
      return '[' + ch + (softF ? '′' : '') + '] ' + (softF ? (LANG === 'ru' ? 'мягк.' : 'soft') : (LANG === 'ru' ? 'тв.' : 'hard')) + ' ' + (voiced ? (LANG === 'ru' ? 'звон.' : 'voiced') : (LANG === 'ru' ? 'глух.' : 'unvoiced'));
    }
    return c + ' (—)';
  });
  row(t('solv.sounds'), scheme.join(' · '));
  const note = el('div', 'solv__note'); note.textContent = t('solv.note'); out.appendChild(note);
}
SCREENS.solvers = {
  enter() {
    const mex = $('#mathExamples'), rex = $('#rusExamples');
    if (mex && !mex.querySelector('.chip')) {
      mex.innerHTML = '<div class="solv__note">' + esc(t('solv.try')) + '</div>';
      ['2+3*4', '(10-4)/2', '7*(3+2)-5', '2^10', '100/4+25', '2x+6=10', 'x-7=12', '3*x+5=2*x+9'].forEach(x => {
        const b = el('button', 'chip', esc(x));
        b.onclick = () => { $('#mathIn').value = x; solveMath(x); };
        mex.appendChild(b);
      });
    }
    if (rex && !rex.querySelector('.chip')) {
      rex.innerHTML = '<div class="solv__note">' + esc(t('solv.try')) + '</div>';
      ['машина', 'учитель', 'корова', 'звонит', 'библиотека', 'мяч'].forEach(x => {
        const b = el('button', 'chip', esc(x));
        b.onclick = () => { $('#rusIn').value = x; analyzeRus(x); };
        rex.appendChild(b);
      });
    }
  }
};

/* ─────────── 22.7 форма отзыва → Gmail ─────────── */
function bindFeedback() {
  const f = $('#fbForm'); if (!f) return;
  f.addEventListener('submit', e => {
    e.preventDefault();
    const email = ($('#fbEmail').value || '').trim();
    const type = $('#fbType').value;
    const msg = ($('#fbMsg').value || '').trim();
    f.classList.remove('is-bad');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(email)) { f.classList.add('is-bad'); $('#fbEmail').focus(); toast(t('fb.needEmail'), '', '!'); return; }
    if (msg.length < 3) { f.classList.add('is-bad'); $('#fbMsg').focus(); toast(t('fb.needMsg'), '', '!'); return; }
    const typeLabel = t('fb.' + type);
    const subj = '[QKC BETA] ' + typeLabel;
    const body = typeLabel + '\nE-mail: ' + email + '\n\n' + msg + '\n\n--\n' + (LANG === 'ru' ? 'Отправлено с сайта QKC (Quick Knowledge Check), бета-версия' : 'Sent from the QKC (Quick Knowledge Check) site, beta');
    const url = 'https://mail.google.com/mail/?view=cm&fs=1&to=' + encodeURIComponent(SUPPORT_EMAIL) + '&su=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(body);
    const w = window.open(url, '_blank', 'noopener');
    if (!w) location.href = 'mailto:' + SUPPORT_EMAIL + '?subject=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(body);
    toast(t('fb.opened'), SUPPORT_EMAIL, '✉');
    Sound.play('select');
  });
}

/* ─────────── 23. загрузка ─────────── */
function boot() {
  loadState();
  LANG = State.settings.lang || 'ru';
  applySettings();
  FX.init(); BG.init();
  renderQuizSound();
  renderAllStatic();
  bindEvents();
  applyI18n();
  $('#trimesterMode').checked = !!State.settings.trimesters;
  $('#cmdInput').placeholder = t('cmd.ph');
  applyHashParams();
  Router.go(Router.fromHash());
  registerSW();
  // дневная цель
  const d = D();
  if (d.todayKey !== todayKey()) { d.todayKey = todayKey(); d.todayDone = 0; saveProfiles(); }
  // восстановление теста
  const rs = Store.get(RESUME_KEY, null);
  if (rs && rs.cfg && Date.now() - rs.ts < 1000 * 60 * 60 * 12) {
    setTimeout(() => {
      confirmBox(t('quiz.resumed'), t('quiz.confirmExit').replace('не сохранится', 'будет потерян') + ' Продолжить?', () => {
        Bank.load(rs.cfg.grade).then(() => {
          Quiz.cfg = rs.cfg; Quiz.items = buildItems(rs.cfg); Quiz.answers = rs.answers && rs.answers.length === Quiz.items.length ? rs.answers : Quiz.items.map(() => ({ given: null, ok: null, ms: 0 }));
          Quiz.idx = clamp(rs.idx || 0, 0, Math.max(0, Quiz.items.length - 1)); Quiz.flags = rs.flags || {}; Quiz.done = false;
          Quiz.t0 = Date.now() - (rs.elapsed || 0);
          Router.go('quiz'); renderQuizHeader(); renderQuestion(); startTimers();
          toast(t('quiz.resumed'), '', '↺');
        }).catch(() => Store.del(RESUME_KEY));
      }, t('quiz.resume'));
    }, 900);
  }
  // приветствие
  setTimeout(() => {
    if (!Store.get(KEY + 'seen', false)) {
      Store.set(KEY + 'seen', true);
      toast('QKC — Quick Knowledge Check · BETA', fmtNum(TOTAL_Q) + ' ' + t('common.q') + ' · ' + t('n0') + '–11 ' + t('stat.grades') + ' · ' + t('stat.subjects') + ': ' + Object.keys(SUBJECTS).length, '◆');
    }
  }, 1400);
  State.ready = true;
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
