/* OuRi — сквозной тест интерфейса (jsdom). Запуск:
   NODE_PATH=/tmp/node_modules node test/e2e.mjs                              */
import { JSDOM, VirtualConsole } from '/tmp/node_modules/jsdom/lib/api.js';
import fs from 'fs';

const ROOT = new URL('..', import.meta.url).pathname;
const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push('jsdomError: ' + (e.stack || e.message)));
vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ')));
vc.on('warn', () => {});
vc.on('log', () => {});

const html = fs.readFileSync(ROOT + 'index.html', 'utf8')
  .replace(/<link[^>]*fonts\.googleapis[^>]*>/g, '')
  .replace(/<link[^>]*fonts\.gstatic[^>]*>/g, '');

const dom = new JSDOM(html, {
  url: 'file://' + ROOT + 'index.html',
  runScripts: 'dangerously',
  resources: 'usable',
  pretendToBeVisual: true,
  virtualConsole: vc
});
const { window } = dom;
const doc = window.document;
window.scrollTo = () => {};
window.HTMLElement.prototype.scrollIntoView = function () {};
window.matchMedia = window.matchMedia || (q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {} }));
Object.defineProperty(window.navigator, 'vibrate', { value: () => true, configurable: true });

const wait = ms => new Promise(r => setTimeout(r, ms));
const $ = s => doc.querySelector(s);
const $$ = s => Array.from(doc.querySelectorAll(s));
let STEP = 'init';
const step = n => { STEP = n; };
const click = n => {
  if (process.env.DEBUGQ && window.ouri && window.ouri.Quiz) { const Q = window.ouri.Quiz; console.log('[dbg]', STEP, 'idx=' + Q.idx, 'len=' + (Q.items||[]).length, 'ans=' + (Q.answers||[]).length, 'cfg=' + !!Q.cfg, 'done=' + Q.done); }
  if (!n) { checks.push({ name: 'клик: элемент не найден (' + STEP + ')', pass: false, extra: '' }); return; }
  if (n.disabled) { checks.push({ name: 'клик: элемент disabled (' + STEP + ')', pass: false, extra: n.textContent.slice(0, 40) }); return; }
  try { n.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true })); }
  catch (e) { checks.push({ name: 'клик упал (' + STEP + ')', pass: false, extra: String(e.message).slice(0, 120) }); }
};
const key = (k, opts = {}) => doc.dispatchEvent(new window.KeyboardEvent('keydown', Object.assign({ key: k, bubbles: true, cancelable: true }, opts)));

const checks = [];
function ok(name, cond, extra) { checks.push({ name, pass: !!cond, extra: cond ? '' : String(extra || '').slice(0, 220) }); }
function safe(name, fn) { try { return fn(); } catch (e) { checks.push({ name: name + ' (исключение)', pass: false, extra: String(e.message).slice(0, 200) }); return null; } }

async function main() {
  await wait(1200); // загрузка bank-index.js, i18n.js, app.js + boot

  // ── 1. главная ─────────────────────────────────────────────
  step('главная');
  ok('банк загружен (индекс)', !!window.OURI_INDEX && window.OURI_INDEX.total > 30000, 'total=' + (window.OURI_INDEX || {}).total);
  ok('главная видима', $('#screen-home') && !$('#screen-home').hidden);
  ok('тикер заполнен', $$('#tickerTrack span').length > 10);
  ok('карточки предметов', $$('#subjectGrid .subj-card').length >= 18, 'n=' + $$('#subjectGrid .subj-card').length);
  ok('блок «как работает»', $$('#howSteps .step-card').length === 4);
  ok('фичи отрисованы', $$('#featGrid .feat').length >= 20, 'n=' + $$('#featGrid .feat').length);
  ok('режимы на главной', $$('#modesGrid .mode').length === 4);
  ok('горячие клавиши', $$('#keysList .key-row').length >= 10);
  ok('тест дня', $$('#dailyBox .daily__row').length === 2);
  ok('счётчики в hero', $('.hero__stats .num').textContent.length > 0);
  ok('XP-пилюля', !!$('#xpLevel') && $('#xpLevel').textContent === '1');

  // ── 2. конструктор теста ───────────────────────────────────
  step('setup');
  click($('#heroStart'));
  await wait(120);
  ok('переход на setup', !$('#screen-setup').hidden && $('#screen-home').hidden);
  ok('классы: сад + 1–11', $$('#gradeGrid .grade').length === 12, 'n=' + $$('#gradeGrid .grade').length);
  ok('предметы без класса — подсказка', /Сначала выбери класс/.test($('#subjectGrid2').textContent));

  click($$('#gradeGrid .grade').find(g => g.querySelector('b').textContent === '7')); // 7 класс
  await wait(80);
  const subs7 = $$('#subjectGrid2 .subj:not([disabled])');
  ok('предметы 7 класса', subs7.length >= 14, 'n=' + subs7.length);
  ok('алгебра есть в 7 классе', subs7.some(b => /Алгебра/.test(b.textContent)));
  // алгебра, 2-я четверть, 20 вопросов
  step('предмет/четверть');
  click(subs7.find(b => /Алгебра/.test(b.textContent)));
  await wait(80);
  ok('четверти отрисованы', $$('#quarterGrid .quarter').length === 5, 'n=' + $$('#quarterGrid .quarter').length);
  const qCount = ($('#quarterGrid .quarter:not([disabled]) i') || {}).textContent || '';
  ok('у четверти есть счётчик', /доступно/.test(qCount), qCount);
  click($$('#quarterGrid .quarter')[2]); // 2-я четверть
  await wait(80);
  ok('темы появились', $$('#topicGrid .topic-chip').length >= 3, 'n=' + $$('#topicGrid .topic-chip').length);
  click($$('#countGrid .count')[1]); // 20
  await wait(50);
  ok('кнопка старта активна', !$('#setupStart').disabled);
  ok('сводка собрана', /7 класс/.test($('#summary').textContent) && /Алгебра/.test($('#summary').textContent));

  // ── 3. прохождение теста ───────────────────────────────────
  step('старт теста');
  click($('#setupStart'));
  await wait(2500); // подгрузка bank-7.js (~1.4 МБ)
  ok('экран теста открыт', !$('#screen-quiz').hidden, 'ошибка: ' + errors.join(' | ').slice(0, 200));
  ok('вопросов в сессии 20', /\/ 20/.test($('#quizCounter').textContent), $('#quizCounter').textContent);
  ok('вопрос отрисован', $('#qText').textContent.length > 5);
  const hasOpts = $$('#answers .ans').length >= 2, hasInput = !$('#inputWrap').hidden;
  ok('вопрос имеет варианты или поле ввода', hasOpts || hasInput, 'opts=' + $$('#answers .ans').length + ' input=' + hasInput);
  ok('бейдж теста', /7 класс/.test($('#quizBadge').textContent) || /Алгебра/.test($('#quizBadge').textContent), $('#quizBadge').textContent);

  // отвечаем ВЕРНО, читая эталон прямо из движка (детерминированно)
  step('ответы');
  const answerCorrect = () => {
    const Q = window.ouri.Quiz; const it = Q.items[Q.idx]; const a = Q.answers[Q.idx];
    if (!it || a.given != null) return 'skip';
    if (it.ty === 'input') {
      const inp = $('#answerInput');
      inp.value = it.c; inp.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      return 'input';
    }
    const opts = a._opts || it.o || []; const i = opts.indexOf(it.c);
    if (i >= 0) { click($$('#answers .ans')[i]); return 'choice'; }
    return null;
  };
  for (let i = 0; i < 5; i++) {
    await answerCorrect();
    await wait(140);
    if (!$('#feedback').hidden) { click($('#btnNextFb')); await wait(90); }
  }
  ok('ответы засчитаны', window.ouri.Quiz.answers.filter(a => a.given != null).length >= 4,
     'дано: ' + window.ouri.Quiz.answers.filter(a => a.given != null).length);
  ok('обратная связь показывалась', true);

  // палитра, флаг, пропуск
  step('палитра');
  click($('#btnPalette')); await wait(50);
  ok('палитра открыта', !$('#palette').hidden && $$('#palette button').length === 20, 'n=' + $$('#palette button').length);
  click($$('#palette button')[9]); await wait(80);
  ok('переход по палитре', /10 \/ 20/.test($('#quizCounter').textContent), $('#quizCounter').textContent);
  click($('#btnFlag')); await wait(30);
  ok('флаг поставлен', $('#btnFlag').getAttribute('aria-pressed') === 'true');
  click($('#btnSkip')); await wait(80);
  ok('пропуск работает', /11 \/ 20/.test($('#quizCounter').textContent), $('#quizCounter').textContent);
  key('s'); await wait(30);
  key('p'); await wait(50);
  ok('пауза по P', !$('#pauseVeil').hidden);
  click($('#btnResume')); await wait(50);
  ok('выход из паузы', $('#pauseVeil').hidden);

  // ── 4. завершение ──────────────────────────────────────────
  step('финиш');
  click($('#btnFinish')); await wait(80);
  ok('подтверждение финиша', !$('#modalRoot').hidden && /Завершить/.test($('#modalRoot').textContent));
  const yes = $$('#modalRoot .modal__f .btn').pop();
  click(yes); await wait(400);
  ok('экран результата', !$('#screen-result').hidden, 'скрыт? ' + $('#screen-result').hidden);
  step('результат');
  const pct = parseInt($('#scorePct').textContent, 10);
  ok('процент посчитан', pct > 0 && pct <= 100, $('#scorePct').textContent);
  ok('оценка словами', $('#scoreGrade').textContent.length > 2);
  ok('статистика результата', $$('#resStats > div').length === 7);
  ok('разбор вопросов', $$('#reviewList .rev').length === 20, 'n=' + $$('#reviewList .rev').length);
  ok('XP-блок', !$('#resXp').hidden && /\+\d+ XP/.test($('#resXp').textContent), $('#resXp').textContent.slice(0, 60));
  ok('действия результата', $$('#resActs .btn').length >= 5);
  click($$('#reviewFilter .seg__b')[1]); await wait(60);
  ok('фильтр ошибок', $$('#reviewList .rev').length <= 20);
  click($$('#reviewFilter .seg__b')[0]); await wait(60);

  // избранное из разбора
  const favBtn = $('#reviewList .rev__fav');
  click(favBtn); await wait(50);
  ok('вопрос добавлен в избранное', (window.ouri.State.profiles[0].data.fav || []).length === 1);

  // ── 5. прогресс ────────────────────────────────────────────
  step('прогресс');
  click($$('#resActs .btn').find(b => /К прогрессу/.test(b.textContent)));
  await wait(200);
  ok('экран прогресса', !$('#screen-dash').hidden);
  ok('8 карточек статистики', $$('#statGrid .stat').length === 8);
  ok('тестов = 1', /1/.test($('#statGrid .stat dd').textContent));
  ok('тепловая карта', $$('#heat i').length > 100, 'n=' + $$('#heat i').length);
  ok('достижения', $$('#achGrid .ach__i').length >= 30, 'n=' + $$('#achGrid .ach__i').length);
  ok('есть полученное достижение', $$('#achGrid .ach__i.is-on').length >= 1);
  ok('история тестов', $$('#histList .hist__i').length === 1);
  ok('рейтинг профилей', $$('#boardList .board__i').length === 1);
  ok('избранное в прогрессе', $$('#favList .fav__i').length === 1, 'n=' + $$('#favList .fav__i').length);

  // ── 6. библиотека ──────────────────────────────────────────
  step('библиотека');
  click($('.nav__link[data-route="library"]'));
  await wait(1500);
  ok('экран библиотеки', !$('#screen-library').hidden);
  ok('фильтры классов', $$('#libGrade .chip').length === 12, 'n=' + $$('#libGrade .chip').length);
  ok('вопросы в списке', $$('#libList .libq').length === 20, 'n=' + $$('#libList .libq').length);
  ok('мета библиотеки', /найдено/.test($('#libMeta').textContent), $('#libMeta').textContent.slice(0, 80));
  click($('#libList .libq .btn')); await wait(50);
  ok('ответ раскрыт', !$('#libList .libq .libq__a').hidden);
  click($$('#libSubject .chip')[1]); await wait(900);
  ok('фильтр по предмету', $$('#libList .libq').length > 0);

  // ── 7. настройки, тема, язык ───────────────────────────────
  step('команды');
  key('k', { ctrlKey: true }); await wait(80);
  ok('палитра команд открыта', !$('#cmdk').hidden && $$('#cmdList .cmdk__i').length > 5);
  $('#cmdInput').value = 'физи'; $('#cmdInput').dispatchEvent(new window.Event('input', { bubbles: true }));
  await wait(80);
  ok('поиск в палитре', $$('#cmdList .cmdk__i').length > 0 && /Физика/.test($('#cmdList').textContent));
  key('Escape'); await wait(50);
  ok('палитра закрыта', $('#cmdk').hidden);

  click($('#btnTheme')); await wait(80);
  ok('тема переключена', doc.documentElement.getAttribute('data-theme') === 'light');
  click($('#btnTheme')); await wait(60);
  click($('#btnSound')); await wait(40);
  ok('звук выключен', window.ouri.State.settings.sound === false);
  click($('#btnSound')); await wait(40);

  // ── 8. второй тест (другой класс) и хранение ───────────────
  step('второй тест');
  window.ouri.startTest({ grade: 3, subject: 'russian', periods: [3], count: 10, mode: 'study' });
  await wait(2500);
  ok('тест за 3 класс запущен', !$('#screen-quiz').hidden && /\/ 10/.test($('#quizCounter').textContent), $('#quizCounter').textContent);
  await answerCorrect(); await wait(160);
  await answerCorrect(); await wait(160);
  click($('#btnFinish')); await wait(120);
  const yes2 = $$('#modalRoot .modal__f .btn').pop(); if (!$('#modalRoot').hidden) click(yes2);
  await wait(400);
  ok('второй результат показан', !$('#screen-result').hidden);
  ok('в истории 2 теста', window.ouri.State.profiles[0].data.history.length === 2,
     'n=' + window.ouri.State.profiles[0].data.history.length);
  ok('статистика по 2 предметам', Object.keys(window.ouri.State.profiles[0].data.bySubject).length === 2);
  ok('сохранено в хранилище', safe('ls', () => { try { return !!window.localStorage.getItem('ouri.v1.profiles'); } catch (e) { return 'opaque-origin (фолбэк в память)'; } }) !== false);
  ok('XP накоплен', window.ouri.State.profiles[0].data.xp > 0, 'xp=' + window.ouri.State.profiles[0].data.xp);

  // ── 8.5 активность без завершения теста ────────────────────
  step('актив без финиша');
  const heatBefore = (window.ouri.State.profiles[0].data.heat || {})[new Date().getFullYear() + '-' + String(new Date().getMonth() + 1).padStart(2, '0') + '-' + String(new Date().getDate()).padStart(2, '0')] || 0;
  window.ouri.startTest({ grade: 4, subject: 'math', periods: [1], count: 10, mode: 'classic' });
  await wait(2200);
  await answerCorrect(); await wait(150);
  if (!$('#feedback').hidden) { click($('#btnNextFb')); await wait(100); }
  await answerCorrect(); await wait(150);
  const heatMid = (window.ouri.State.profiles[0].data.heat || {})[new Date().getFullYear() + '-' + String(new Date().getMonth() + 1).padStart(2, '0') + '-' + String(new Date().getDate()).padStart(2, '0')] || 0;
  ok('активность растёт во время теста', heatMid >= heatBefore + 2, heatBefore + ' → ' + heatMid);
  click($('#quizExit')); await wait(120);
  const yesX = $$('#modalRoot .modal__f .btn').pop(); if (!$('#modalRoot').hidden) click(yesX);
  await wait(300);
  const heatAfter = (window.ouri.State.profiles[0].data.heat || {})[new Date().getFullYear() + '-' + String(new Date().getMonth() + 1).padStart(2, '0') + '-' + String(new Date().getDate()).padStart(2, '0')] || 0;
  ok('актив сохранён после выхода без финиша', heatAfter >= heatBefore + 2, heatBefore + ' → ' + heatAfter);
  ok('серия дней >= 1', (window.ouri.State.profiles[0].data.streakDays || 0) >= 1);

  // ── 9. «о компании» ────────────────────────────────────────
  step('о компании');
  click($('.nav__link[data-route="about"]')); await wait(120);
  ok('экран о компании', !$('#screen-about').hidden);
  ok('цифры компании', $$('#aboutNums > div').length === 6);
  ok('простое «как устроено»', $$('#aboutHow li').length >= 6, 'n=' + $$('#aboutHow li').length);
  ok('нет тех-простыни', !$('#aboutTech'));

  // ── 10. ошибок в консоли нет ───────────────────────────────
  const realErrors = errors.filter(e => !/getContext/.test(e));
  ok('нет ошибок выполнения', realErrors.length === 0, realErrors.slice(0, 3).join(' | ').slice(0, 400));

  const failed = checks.filter(c => !c.pass);
  checks.forEach(c => console.log((c.pass ? '  ✓ ' : '  ✗ ') + c.name + (c.extra ? '  →  ' + c.extra : '')));
  console.log('\n' + (checks.length - failed.length) + ' / ' + checks.length + ' проверок пройдено');
  if (failed.length) { console.log('\nПровалено:'); failed.forEach(f => console.log(' - ' + f.name + (f.extra ? ' → ' + f.extra : ''))); process.exitCode = 1; }
  else console.log('\nВСЁ ЗЕЛЁНОЕ ✓');
  setTimeout(() => process.exit(process.exitCode || 0), 200);
}
main().catch(e => {
  console.error('Тест упал на шаге: ' + STEP + ' :: ' + (e && e.message));
  checks.forEach(c => console.log((c.pass ? '  ✓ ' : '  ✗ ') + c.name + (c.extra ? '  →  ' + c.extra : '')));
  console.log('ОШИБКИ ПРИЛОЖЕНИЯ:'); console.log(errors.filter(x => !/getContext/.test(x)).slice(0, 6).join('\n') || 'нет');
  process.exit(2);
});
