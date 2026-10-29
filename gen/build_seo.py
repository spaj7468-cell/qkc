# -*- coding: utf-8 -*-
"""
OuRi / QKC — генератор SEO-посадочных страниц.

Зачем
-----
Сайт — одностраничное приложение с хешевым роутером (`#/setup`, `#/program`, ...).
Для поисковика это ОДИН URL и один <title>, поэтому запросы вида
«7 класс тест», «тест по алгебре 7 класс 3 четверть» физически не на что посадить:
страницы с таким адресом не существует.

Скрипт генерирует из `assets/bank.json` настоящий статический HTML:
    /7/                 — хаб класса (все предметы, счётчики, темы)
    /7/algebra/         — посадочная под «тест по алгебре 7 класс»
    sitemap.xml         — все URL на основном домене
    robots.txt          — Sitemap на основном домене
    assets/seo-pages.json — индекс страниц (для внутренних ссылок и SW)

Каждая посадочная получает уникальные title / description / h1 / каноникал,
реальные примеры вопросов с объяснениями из банка, таблицу четвертей,
список тем, FAQ, перелинковку «другие предметы этого класса» и
«этот предмет в других классах», а также JSON-LD (Quiz, BreadcrumbList,
FAQPage, ItemList).

Запуск
------
    python3 gen/build_seo.py            # собрать страницы
    npm run build:seo                   # то же самое

Страницы детерминированы: при одном и том же bank.json вывод побайтово
совпадает, так что коммитить их в репозиторий безопасно (никакого «шума»
в истории при повторной сборке).
"""

import json
import os
import re
from collections import OrderedDict
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BANK = os.path.join(ROOT, "assets", "bank.json")
OUT = ROOT

BASE = "https://qkc.runs-on.dev"
MIRROR = "https://spaj7468-cell.github.io/qkc/"
ORG = "OuRi"
PRODUCT = "QKC — Quick Knowledge Check"

# Авторы проекта. Блок вставляется в каждый сгенерированный футер (FOOT_TMPL),
# поэтому при пересборке `python3 gen/build_seo.py` он не теряется.
# Правь здесь — не в готовых HTML-файлах.
AUTHORS = [
    # (роль, имя, ссылка)
    ("Автор", "telrino", "https://vk.ru/telrino"),
    ("Соавтор", "Бро", "https://vk.ru/id920684081"),
]
VK_GLYPH = ('<svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" '
            'focusable="false"><path fill="currentColor" d="M12.79 17.04c-5.14 0-8.08-3.52-'
            '8.2-9.38h2.58c.08 4.3 1.98 6.12 3.48 6.5V7.66h2.43v3.71c1.48-.16 3.03-1.86 '
            '3.55-3.71h2.43a6.4 6.4 0 0 1-2.94 4.67 6.66 6.66 0 0 1 3.42 4.71h-2.67c-.42-'
            '1.32-1.47-2.34-3.79-2.58v2.58h-.29Z"/></svg>')


def authors_html():
    """HTML-блок «Авторы проекта» — попадает в футер каждой собранной страницы."""
    items = "".join(
        '<a href="%s" target="_blank" rel="noopener noreferrer" title="%s: %s — ВКонтакте">'
        '%s<span>%s</span></a>' % (url, esc(role), esc(name), VK_GLYPH, esc(name))
        for role, name, url in AUTHORS)
    return ('<div class="seo-authors">\n'
            '      <span class="seo-authors__label">Авторы проекта</span>\n'
            '      <span class="seo-authors__list">%s</span>\n'
            '    </div>' % items)

# ────────────────────────────────────────────────────────────── словарь
ONES = ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь",
        "восемь", "девять", "десять", "одиннадцать"]
TENS = ["десятого", "одиннадцатого"]          # 10-й, 11-й -> родительный для «класса»
ORD = {
    0: "подготовительный", 1: "1-й", 2: "2-й", 3: "3-й", 4: "4-й", 5: "5-й",
    6: "6-й", 7: "7-й", 8: "8-й", 9: "9-й", 10: "10-й", 11: "11-й",
}
ORD_PREP = {                                     # «в 7-м классе»
    0: "подготовительном", 1: "1-м", 2: "2-м", 3: "3-м", 4: "4-м", 5: "5-м",
    6: "6-м", 7: "7-м", 8: "8-м", 9: "9-м", 10: "10-м", 11: "11-м",
}
ORD_GEN = {                                      # «для 7-го класса»
    0: "подготовительного", 1: "1-го", 2: "2-го", 3: "3-го", 4: "4-го",
    5: "5-го", 6: "6-го", 7: "7-го", 8: "8-го", 9: "9-го", 10: "10-го",
    11: "11-го",
}
ORD_GEN_FULL = {                                 # «для 7-го класса» целиком (для description)
    0: "подготовительной группы детского сада", 1: "1-го класса", 2: "2-го класса",
    3: "3-го класса", 4: "4-го класса", 5: "5-го класса", 6: "6-го класса",
    7: "7-го класса", 8: "8-го класса", 9: "9-го класса", 10: "10-го класса",
    11: "11-го класса",
}
QNAME = {1: "1-я четверть", 2: "2-я четверть", 3: "3-я четверть", 4: "4-я четверть"}
QSHORT = {1: "1 четверть", 2: "2 четверть", 3: "3 четверть", 4: "4 четверть"}
QPREP = {1: "1-й четверти", 2: "2-й четверти", 3: "3-й четверти", 4: "4-й четверти"}
TYPE_RU = {"choice": "выбор ответа", "tf": "верно / неверно", "input": "ввод ответа"}


def plural(n, forms):
    """Русское склонение: plural(5, ('вопрос','вопроса','вопросов')) -> 'вопросов'."""
    n = abs(int(n)) % 100
    n1 = n % 10
    if n > 10 and n < 20:
        return forms[2]
    if n1 > 1 and n1 < 5:
        return forms[1]
    if n1 == 1:
        return forms[0]
    return forms[2]


def nq(n):
    """«144 вопроса» / «1 вопрос» / «360 вопросов» — число + правильная форма."""
    return "%s %s" % (n_words(n), plural(n, ("вопрос", "вопроса", "вопросов")))


def n_works(n):
    """«20 произведений» / «2 произведения» / «1 произведение» — число + верная форма."""
    return "%s %s" % (n_words(n), plural(n, ("произведение", "произведения", "произведений")))


def n_authors(n):
    """«84 автора» / «1 автор» / «12 авторов»."""
    return "%s %s" % (n_words(n), plural(n, ("автор", "автора", "авторов")))


def grade_label(g):
    """«7 класс» / «детский сад» — как его ищут люди."""
    g = int(g)
    return "детский сад" if g == 0 else "%d класс" % g


def grade_label_gen(g):
    g = int(g)
    return "детского сада" if g == 0 else "%d класса" % g


def n_words(n):
    """42823 -> «42 823» (неразрывный пробел тонким пробелом не нужен, обычный)."""
    return "{:,}".format(n).replace(",", "\u2009")


# ────────────────────────────────────────────────────────────── утилиты
def esc(s):
    return escape(str(s), quote=True)


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, text):
    full = os.path.join(OUT, path)
    d = os.path.dirname(full)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text)


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def slug_ok(s):
    """Слаг из латиницы/цифр, дефис только между ними.
    Проверка обязательна: слаги попадают в пути на диске и в URL,
    поэтому '..' и '/' в них недопустимы."""
    return SLUG_RE.fullmatch(str(s)) is not None


# ────────────────────────────────────────────────────────────── данные
def load():
    d = json.loads(read(BANK))
    meta, bank = d["meta"], d["bank"]
    grades = [int(x) for x in meta["grades"]]
    subjects = meta["subjects"]
    grade_subjects = {int(k): list(v) for k, v in meta["gradeSubjects"].items()}
    counts = {int(k): v for k, v in meta.get("counts", {}).items()}
    topics = {int(k): v for k, v in meta.get("topics", {}).items()}
    return dict(meta=meta, bank=bank, grades=grades, subjects=subjects,
                grade_subjects=grade_subjects, counts=counts, topics=topics,
                total=int(meta.get("total", 0)), built=meta.get("builtAt", ""))


def qcount(D, g, subj):
    """Точное число вопросов: считаем по банку, counts используем только как сверку."""
    try:
        node = D["bank"][str(g)][subj]
    except KeyError:
        return 0, []
    per = []
    tot = 0
    for q in (1, 2, 3, 4):
        n = len(node.get(str(q), []) or [])
        per.append(n)
        tot += n
    return tot, per


def sample_questions(D, g, subj, limit=3):
    """Детерминированная выборка: по одному вопросу из разных четвертей и тем."""
    try:
        node = D["bank"][str(g)][subj]
    except KeyError:
        return []
    picked, seen_topics = [], set()
    for q in (1, 2, 3, 4):
        for item in (node.get(str(q), []) or []):
            tp = item.get("tp") or ""
            if tp in seen_topics:
                continue
            seen_topics.add(tp)
            picked.append((q, item))
            break
        if len(picked) >= limit:
            break
    if len(picked) < limit:                      # добираем, если тем мало
        for q in (1, 2, 3, 4):
            for item in (node.get(str(q), []) or []):
                if any(item is p[1] for p in picked):
                    continue
                picked.append((q, item))
                if len(picked) >= limit:
                    break
            if len(picked) >= limit:
                break
    return picked[:limit]


def type_mix(D, g, subj):
    try:
        node = D["bank"][str(g)][subj]
    except KeyError:
        return {}
    mix = {}
    for q in (1, 2, 3, 4):
        for item in (node.get(str(q), []) or []):
            k = item.get("ty") or "choice"
            mix[k] = mix.get(k, 0) + 1
    return mix


# ────────────────────────────────────────────────────────────── шапка/подвал
HEAD_TMPL = """<!DOCTYPE html>
<html lang="ru" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<link rel="canonical" href="%(canon)s">
<meta name="description" content="%(desc)s">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0a0a0a">
<meta name="color-scheme" content="dark light">
<meta property="og:title" content="%(ogtitle)s">
<meta property="og:description" content="%(ogdesc)s">
<meta property="og:url" content="%(canon)s">
<meta property="og:type" content="%(ogtype)s">
<meta property="og:site_name" content="QKC — Quick Knowledge Check">
<meta property="og:locale" content="ru_RU">
<meta property="og:image" content="%(base)s/assets/icon-512.png">
<meta property="og:image:width" content="512">
<meta property="og:image:height" content="512">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="%(ogtitle)s">
<meta name="twitter:description" content="%(ogdesc)s">
<meta name="twitter:image" content="%(base)s/assets/icon-512.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;700&display=swap" media="print" onload="this.media='all'">
<link rel="stylesheet" href="/css/style.css">
<link rel="stylesheet" href="/css/seo.css">
%(jsonld)s
</head>
<body>
<a class="skip-link" href="#main">Перейти к содержимому</a>
<header class="seo-nav">
  <a class="seo-brand" href="/">
    <img src="/assets/logo.png" alt="" width="26" height="26" decoding="async">
    <b>Q</b>uick <b>K</b>nowledge <b>C</b>heck
    <span class="seo-beta">BETA</span>
  </a>
  <a class="seo-topcta" href="/#setup">Открыть тренажёр</a>
</header>
<nav class="seo-crumbs" aria-label="Хлебные крошки">%(crumbs)s</nav>
<main class="seo-wrap" id="main">
"""

FOOT_TMPL = """</main>
<footer class="seo-foot">
  <div class="seo-wrap">
    <p><b>%(product)s</b> — открытый офлайн-тренажёр школьных знаний компании %(org)s.
    %(total)s по %(grades)s уровням и %(subjects)s предметам, всё в браузере,
    без регистрации и без серверов.</p>
    <p class="seo-footnav">
      <a href="/">Главная</a> ·
      <a href="/#setup">Тренажёр</a> ·
      <a href="/#program">Программа</a> ·
      <a href="/lit/">Литература</a> ·
      <a href="/#open">Открытый проект</a> ·
      <a href="https://github.com/spaj7468-cell/qkc">GitHub</a> ·
      <a href="https://engine.qkc.runs-on.dev/">QKC Engine</a> ·
      <a href="https://code.qkc.runs-on.dev/">QKCcode</a> ·
      <a href="https://corp.qkc.runs-on.dev/">OuRi Corp</a>
    </p>
    <p class="seo-note">Статус BETA: в вопросах и объяснениях возможны ошибки —
    сообщи о них через форму отзыва на сайте. Лицензия MIT.</p>
    %(authors)s
  </div>
</footer>
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', function () {
    navigator.serviceWorker.getRegistrations().then(function (rs) {
      if (!rs.length) navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
    });
  });
}
</script>
</body>
</html>
"""


def jsonld_block(objs):
    out = []
    for o in objs:
        out.append('<script type="application/ld+json">' +
                   json.dumps(o, ensure_ascii=False, separators=(",", ":")) +
                   "</script>")
    return "\n".join(out)


def crumbs(items):
    parts = []
    for i, (href, label) in enumerate(items):
        if href:
            parts.append('<a href="%s">%s</a>' % (esc(href), esc(label)))
        else:
            parts.append('<span aria-current="page">%s</span>' % esc(label))
    return '<ol itemscope itemtype="https://schema.org/BreadcrumbList">' + "".join(
        '<li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">'
        '<span itemprop="name">%s</span><meta itemprop="position" content="%d"></li>'
        % (p, i + 1) for i, p in enumerate(parts)) + "</ol>"


# ────────────────────────────────────────────────────────────── страницы
def render_question(idx, qn, item):
    ty = item.get("ty") or "choice"
    tname = TYPE_RU.get(ty, ty)
    body = ['<li class="seo-q">']
    body.append('<p class="seo-q__t"><span class="seo-q__n">%d.</span> %s</p>'
                % (idx, esc(item.get("t", ""))))
    opts = item.get("o") or []
    correct = item.get("c")
    if ty == "choice" and opts:
        body.append('<ul class="seo-q__opts">')
        for o in opts:
            cls = "seo-q__opt"
            body.append('<li class="%s">%s</li>' % (cls, esc(o)))
        body.append("</ul>")
    elif ty == "tf":
        body.append('<ul class="seo-q__opts"><li class="seo-q__opt">Верно</li>'
                    '<li class="seo-q__opt">Неверно</li></ul>')
    else:
        body.append('<p class="seo-q__hint">Ответ вводится с клавиатуры.</p>')
    ans = "%s" % (esc(correct) if correct is not None else "—")
    exp = item.get("e") or ""
    inner = "<b>Правильный ответ:</b> %s" % ans
    if exp:
        inner += "<br><b>Объяснение:</b> %s" % esc(exp)
    body.append('<details class="seo-q__ans"><summary>Показать ответ и объяснение</summary>'
                '<p>%s</p></details>' % inner)
    meta = []
    if item.get("tp"):
        meta.append("тема: %s" % esc(item["tp"]))
    meta.append("%s" % esc(QSHORT.get(qn, "%s четверть" % qn)))
    meta.append("%s" % esc(tname))
    body.append('<p class="seo-q__meta">%s</p>' % esc(" · ").join(
        [m.replace("&amp;", "&") for m in meta]))
    body.append("</li>")
    return "".join(body)


def build_subject_page(D, g, subj):
    S = D["subjects"][subj]
    name = S["name"]
    g = int(g)
    gl, glp, glg = grade_label(g), ORD_PREP[g], ORD_GEN[g]
    url_path = "/%d/%s/" % (g, subj)
    canon = BASE + url_path
    tot, per = qcount(D, g, subj)
    if tot == 0:
        return None
    tps = D["topics"].get(g, {}).get(subj, []) or []
    mix = type_mix(D, g, subj)
    mix_txt = ", ".join("%s — %s" % (TYPE_RU.get(k, k), n_words(v))
                        for k, v in sorted(mix.items(), key=lambda i: -i[1]))
    quarters_txt = ", ".join("%s — %s" % (QSHORT[q], n_words(per[q - 1]))
                             for q in (1, 2, 3, 4) if per[q - 1])

    title = "Тест по предмету «%s» — %s: %s онлайн бесплатно | QKC" % (
        name, gl, nq(tot))
    if len(title) > 70:
        title = "Тест «%s» %s — %s | QKC" % (name, gl, nq(tot))
    desc = ("Бесплатный тест по предмету «%s» для %s: %s с ответами и "
            "объяснениями. По четвертям: %s. Тем: %d. 10, 20, 30 вопросов или своё "
            "число, мгновенная проверка. Без регистрации, работает офлайн. OuRi QKC."
            % (name, ORD_GEN_FULL[g], nq(tot),
               " / ".join(str(per[q - 1]) for q in (1, 2, 3, 4)), len(tps)))
    desc = re.sub(r"\s+", " ", desc)[:300]

    h1 = "Тест по предмету «%s» — %s" % (name, gl)
    lede = ("Собери свой тест: %s по предмету «%s» для %s, разбитых на четыре "
            "четверти и %d тем. Выбираешь четверть и количество вопросов — сайт "
            "мгновенно собирает тест, проверяет ответы и объясняет каждый вопрос. "
            "Без регистрации, без серверов, прогресс хранится в браузере."
            % (nq(tot), name, glg, len(tps)))

    # ── CTA
    cta = ('<div class="seo-cta">'
           '<a class="btn btn--primary btn--lg" href="/#setup?g=%d&s=%s&p=all&n=20&m=classic">'
           'Собрать тест: %s · %s</a>'
           '<a class="btn btn--ghost" href="/%d/">Все предметы %s</a>'
           '</div>' % (g, esc(subj), esc(name), esc(gl), g, esc(glp + " класса")))

    # ── статистика
    stats = ('<section class="seo-sec"><h2 class="seo-h2">Что внутри теста</h2>'
             '<dl class="seo-stats">'
             '<div><dt>Вопросов всего</dt><dd>%s</dd></div>'
             '<div><dt>Четверти</dt><dd>%s</dd></div>'
             '<div><dt>Тем в предмете</dt><dd>%d</dd></div>'
             '<div><dt>Типы вопросов</dt><dd>%s</dd></div>'
             '</dl>'
             '<p class="seo-p">База строго разбита по классам: %s не увидит вопросы '
             'другого класса. Внутри теста вопросы не повторяются, числовые ответы '
             'проверяются с допуском (дроби и десятичная запятая поддерживаются).</p>'
             '</section>'
             % (n_words(tot), esc(quarters_txt), len(tps), esc(mix_txt),
                esc("ученик %s" % glp)))

    # ── темы
    if tps:
        chips = "".join('<a class="seo-chip" href="/#setup?g=%d&s=%s&p=all&n=20&m=classic">%s</a>'
                        % (g, esc(subj), esc(t)) for t in tps)
        topics_sec = ('<section class="seo-sec"><h2 class="seo-h2">Темы: %s, %s</h2>'
                      '<p class="seo-p">Разделы внутри предмета — можно собрать тест '
                      'только по нужным темам:</p><div class="seo-chips">%s</div></section>'
                      % (esc(name), esc(glp + " класс"), chips))
    else:
        topics_sec = ""

    # ── четверти
    rows = []
    for q in (1, 2, 3, 4):
        if not per[q - 1]:
            continue
        rows.append('<tr><th scope="row">%s</th><td>%s</td>'
                    '<td><a href="/#setup?g=%d&s=%s&p=%d&n=20&m=classic">Пройти тест</a></td></tr>'
                    % (esc(QNAME[q]), n_words(per[q - 1]), g, esc(subj), q))
    rows.append('<tr class="seo-rowall"><th scope="row">Весь год сразу</th><td>%s</td>'
                '<td><a href="/#setup?g=%d&s=%s&p=all&n=20&m=classic">Смешанный тест</a></td></tr>'
                % (n_words(tot), g, esc(subj)))
    quarters_sec = ('<section class="seo-sec"><h2 class="seo-h2">Тест по %s за четверть</h2>'
                    '<table class="seo-table"><thead><tr><th>Четверть</th>'
                    '<th>Вопросов</th><th></th></tr></thead><tbody>%s</tbody></table></section>'
                    % (esc(name.lower()), "".join(rows)))

    # ── примеры вопросов
    samples = sample_questions(D, g, subj, 3)
    if samples:
        items = "".join(render_question(i + 1, qn, it) for i, (qn, it) in enumerate(samples))
        ex_sec = ('<section class="seo-sec"><h2 class="seo-h2">Примеры вопросов с ответами</h2>'
                  '<p class="seo-p">Настоящие вопросы из базы — ровно такие же попадутся '
                  'в тесте. Ответ и объяснение спрятаны под спойлер, чтобы можно было '
                  'сначала подумать.</p><ol class="seo-qlist">%s</ol>'
                  '<p class="seo-p"><a class="btn btn--ghost" '
                  'href="/#setup?g=%d&s=%s&p=all&n=20&m=classic">Пройти полный тест</a></p>'
                  '</section>' % (items, g, esc(subj)))
    else:
        ex_sec = ""

    # ── FAQ
    faq = [
        ("Сколько вопросов по предмету «%s» для %s?" % (name, gl),
         "В базе %s: %s. Все они разбиты на темы (%d шт.), внутри теста "
         "вопросы не повторяются." % (nq(tot), quarters_txt, len(tps))),
        ("Это бесплатно и без регистрации?",
         "Да. QKC — открытый проект компании OuRi под лицензией MIT: движок, "
         "генератор банка и вся база вопросов лежат на GitHub. Регистрация не нужна, "
         "прогресс хранится локально в браузере."),
        ("Можно ли проходить тест офлайн?",
         "Да, сайт — PWA: после первого визита страницы и банк вопросов кэшируются, "
         "и тест работает без интернета."),
        ("Какие типы вопросов встречаются?",
         "%s. К каждому вопросу даётся объяснение: формула, ход решения или правило."
         % (mix_txt or "Выбор ответа, верно/неверно и ввод ответа с клавиатуры")),
        ("Почему стоит статус BETA?",
         "Проект честно помечен как бета: в формулировках вопросов и объяснениях "
         "возможны ошибки. Сообщить о них можно через форму отзыва на сайте — она "
         "отправляет письмо на почту разработчика."),
    ]
    faq_html = "".join("<details><summary>%s</summary><p>%s</p></details>" % (esc(q_), esc(a_))
                       for q_, a_ in faq)
    faq_sec = ('<section class="seo-sec"><h2 class="seo-h2">Частые вопросы</h2>'
               '<div class="seo-faq">%s</div></section>' % faq_html)

    # ── перелинковка
    others = [s for s in D["grade_subjects"].get(g, []) if s != subj and s in D["subjects"]]
    other_links = "".join('<a href="/%d/%s/">%s</a>' % (g, esc(s), esc(D["subjects"][s]["name"]))
                          for s in others)
    same_other = []
    for g2 in D["grades"]:
        if g2 == g:
            continue
        t2, _ = qcount(D, g2, subj)
        if t2:
            same_other.append('<a href="/%d/%s/">%s</a>' % (g2, esc(subj), esc(grade_label(g2))))
    cross = ('<section class="seo-sec"><h2 class="seo-h2">Дальше</h2>'
             '<p class="seo-seolink"><b>Другие предметы %s:</b> %s</p>'
             '<p class="seo-seolink"><b>«%s» в других классах:</b> %s</p></section>'
             % (esc(glp + " класса"), other_links or "—", esc(name),
                ", ".join(same_other) or "—"))

    ld = [
        OrderedDict([("@context", "https://schema.org"), ("@type", "BreadcrumbList"),
                     ("itemListElement", [
                         OrderedDict([("@type", "ListItem"), ("position", 1), ("name", "Главная"),
                                      ("item", BASE + "/")]),
                         OrderedDict([("@type", "ListItem"), ("position", 2), ("name", grade_label(g)),
                                      ("item", "%s/%d/" % (BASE, g))]),
                         OrderedDict([("@type", "ListItem"), ("position", 3), ("name", name),
                                      ("item", canon)]),
                     ])]),
        OrderedDict([("@context", "https://schema.org"), ("@type", "Quiz"),
                     ("educationalLevel", grade_label(g)),
                     ("about", name), ("name", h1), ("description", desc),
                     ("url", canon), ("inLanguage", "ru"),
                     ("isAccessibleForFree", True),
                     ("typicalAgeRange", "6-18" if g else "5-7"),
                     ("assesses", name),
                     ("hasPart", [OrderedDict([("@type", "Question"),
                                              ("eduQuestioningType", TYPE_RU.get(it.get("ty"), "choice")),
                                              ("text", it.get("t", "")),
                                              ("about", it.get("tp", name)),
                                              ("suggestedAnswer", OrderedDict(
                                                  [("@type", "Answer"), ("text", str(it.get("c", ""))),
                                                   ("comment", it.get("e", ""))]))])
                                  for _, it in samples]),
                     ("publisher", OrderedDict([("@type", "Organization"), ("name", ORG),
                                                ("url", "https://corp.qkc.runs-on.dev/")])),
                     ("offers", OrderedDict([("@type", "Offer"), ("price", "0"),
                                             ("priceCurrency", "RUB")]))]),
        OrderedDict([("@context", "https://schema.org"), ("@type", "FAQPage"),
                     ("mainEntity", [OrderedDict([("@type", "Question"), ("name", q_),
                                                  ("acceptedAnswer",
                                                   OrderedDict([("@type", "Answer"), ("answerText", a_)]))])
                                     for q_, a_ in faq])]),
        OrderedDict([("@context", "https://schema.org"), ("@type", "ItemList"),
                     ("name", "Четверти: %s, %s" % (name, gl)),
                     ("itemListElement", [OrderedDict([("@type", "ListItem"), ("position", q),
                                                      ("name", QNAME[q]),
                                                      ("url", canon)])
                                          for q in (1, 2, 3, 4) if per[q - 1]])]),
    ]

    page = HEAD_TMPL % dict(title=esc(title), canon=esc(canon), desc=esc(desc),
                            ogtitle=esc(h1), ogdesc=esc(desc[:200]),
                            ogtype="website", base=BASE,
                            jsonld=jsonld_block(ld),
                            crumbs=crumbs([("/", "Главная"),
                                           ("/%d/" % g, grade_label(g)),
                                           ("", name)]))
    page += ('<h1 class="seo-h1">%s</h1>\n<p class="seo-lede">%s</p>\n%s\n%s%s%s%s%s%s'
             % (esc(h1), esc(lede), cta, stats, topics_sec, quarters_sec,
                ex_sec, faq_sec, cross))
    page += FOOT_TMPL % dict(authors=authors_html(), product=esc(PRODUCT), org=esc(ORG),
                             total=nq(D["total"]), grades=len(D["grades"]),
                             subjects=len(D["subjects"]))
    return url_path, title, page


def build_grade_page(D, g):
    g = int(g)
    gl, glp = grade_label(g), ORD_PREP[g]
    url_path = "/%d/" % g
    canon = BASE + url_path
    subs = [s for s in D["grade_subjects"].get(g, []) if s in D["subjects"]]
    tot_all = sum(qcount(D, g, s)[0] for s in subs)
    if not subs or tot_all == 0:
        return None
    title = "Тесты за %s — все предметы: %s онлайн | QKC" % (gl, nq(tot_all))
    desc = ("Онлайн-тесты за %s по %s: %s с ответами и объяснениями. "
            "Выбор предмета, четверти и числа вопросов, мгновенная проверка, офлайн-режим. "
            "Бесплатно и без регистрации — QKC от OuRi."
            % (gl, n_words(len(subs)) + " " + plural(len(subs), ("предмету", "предметам", "предметам")), nq(tot_all)))
    desc = re.sub(r"\s+", " ", desc)[:300]
    h1 = "Тесты за %s" % gl

    rows = []
    for s in sorted(subs, key=lambda x: -qcount(D, g, x)[0]):
        t, per = qcount(D, g, s)
        if not t:
            continue
        nm = D["subjects"][s]["name"]
        tps = D["topics"].get(g, {}).get(s, []) or []
        rows.append('<tr><th scope="row"><a href="/%d/%s/">%s</a></th>'
                    '<td>%s</td><td>%d</td><td>%s</td>'
                    '<td><a href="/#setup?g=%d&s=%s&p=all&n=20&m=classic">Пройти</a></td></tr>'
                    % (g, esc(s), esc(nm), n_words(t), len(tps),
                       esc(", ".join(tps[:4]) + ("…" if len(tps) > 4 else "")), g, esc(s)))
    body = ('<p class="seo-lede">%s по %s для %s. Строгая разбивка '
            '«класс → предмет → четверть → тема»: %s не попадётся вопрос из другой '
            'программы. Всё бесплатно, без регистрации, работает офлайн.</p>'
            '<div class="seo-cta"><a class="btn btn--primary btn--lg" href="/#setup">Открыть тренажёр</a>'
            '<a class="btn btn--ghost" href="/">На главную</a></div>'
            '<section class="seo-sec"><h2 class="seo-h2">Предметы %s</h2>'
            '<table class="seo-table"><thead><tr><th>Предмет</th><th>Вопросов</th>'
            '<th>Тем</th><th>Разделы</th><th></th></tr></thead><tbody>%s</tbody></table></section>'
            % (nq(tot_all), esc(n_words(len(subs)) + " " + plural(len(subs), ("предмету", "предметам", "предметам"))),
               gl, esc(glp + " класса"), esc(glp + " классу"),
               "".join(rows)))

    # другие классы
    other = "".join('<a href="/%d/">%s</a>' % (g2, esc(grade_label(g2)))
                    for g2 in D["grades"] if g2 != g)
    body += ('<section class="seo-sec"><h2 class="seo-h2">Другие классы</h2>'
             '<p class="seo-seolink">%s</p></section>' % other)

    ld = [OrderedDict([("@context", "https://schema.org"), ("@type", "BreadcrumbList"),
                       ("itemListElement", [
                           OrderedDict([("@type", "ListItem"), ("position", 1),
                                        ("name", "Главная"), ("item", BASE + "/")]),
                           OrderedDict([("@type", "ListItem"), ("position", 2),
                                        ("name", gl), ("item", canon)])])]),
          OrderedDict([("@context", "https://schema.org"), ("@type", "CollectionPage"),
                       ("name", h1), ("description", desc), ("url", canon),
                       ("inLanguage", "ru"), ("isPartOf", OrderedDict(
                           [("@type", "WebSite"), ("name", PRODUCT), ("url", BASE + "/")]))]),
          OrderedDict([("@context", "https://schema.org"), ("@type", "ItemList"),
                       ("name", "Предметы: %s" % gl),
                       ("numberOfItems", len(rows)),
                       ("itemListElement", [OrderedDict(
                           [("@type", "ListItem"), ("position", i + 1),
                            ("name", D["subjects"][s]["name"]),
                            ("url", "%s%d/%s/" % (BASE, g, s))])
                           for i, s in enumerate(sorted(
                               subs, key=lambda x: -qcount(D, g, x)[0]))
                           if qcount(D, g, s)[0]])])]

    page = HEAD_TMPL % dict(title=esc(title), canon=esc(canon), desc=esc(desc),
                            ogtitle=esc(h1), ogdesc=esc(desc[:200]), ogtype="website",
                            base=BASE, jsonld=jsonld_block(ld),
                            crumbs=crumbs([("/", "Главная"), ("", gl)]))
    page += '<h1 class="seo-h1">%s</h1>\n%s' % (esc(h1), body)
    page += FOOT_TMPL % dict(authors=authors_html(), product=esc(PRODUCT), org=esc(ORG),
                             total=nq(D["total"]), grades=len(D["grades"]),
                             subjects=len(D["subjects"]))
    return url_path, title, page


def build_index_page(D, index_rows):
    canon = BASE + "/"
    total = D["total"]
    title = ("QKC — онлайн-тесты по классам и предметам: %s бесплатно"
             % nq(total))
    desc = ("Бесплатный тренажёр школьных знаний: детский сад и 1–11 класс, 20 предметов, "
            "4 четверти, %s с ответами и объяснениями. Мгновенная проверка, "
            "офлайн-режим, без регистрации. Открытый проект OuRi." % nq(total))
    h1 = "Онлайн-тесты по классам и предметам"
    rows = []
    for g in D["grades"]:
        subs = [s for s in D["grade_subjects"].get(g, []) if s in D["subjects"]]
        tot = sum(qcount(D, g, s)[0] for s in subs)
        if not tot:
            continue
        top = sorted(subs, key=lambda x: -qcount(D, g, x)[0])[:6]
        links = ", ".join('<a href="/%d/%s/">%s</a>' % (g, esc(s), esc(D["subjects"][s]["name"]))
                          for s in top)
        rows.append('<tr><th scope="row"><a href="/%d/">%s</a></th><td>%s</td>'
                    '<td>%d</td><td>%s</td></tr>'
                    % (g, esc(grade_label(g)), n_words(tot), len(subs), links))
    body = ('<p class="seo-lede">%s по школьной программе: детский сад и 1–11 класс, '
            '%d предметов, четыре четверти и темы внутри каждого предмета. Выбираешь '
            'класс, предмет и количество вопросов — сайт собирает тест, проверяет ответы '
            'и объясняет каждый вопрос. Без регистрации, без серверов, работает офлайн.</p>'
            '<div class="seo-cta"><a class="btn btn--primary btn--lg" href="/#setup">Открыть тренажёр</a>'
            '<a class="btn btn--ghost" href="/#program">Что внутри</a></div>'
            '<section class="seo-sec"><h2 class="seo-h2">Тесты по классам</h2>'
            '<table class="seo-table"><thead><tr><th>Класс</th><th>Вопросов</th>'
            '<th>Предметов</th><th>Самые большие разделы</th></tr></thead>'
            '<tbody>%s</tbody></table></section>'
            % (nq(total), len(D["subjects"]), "".join(rows)))

    # все предметы сквозным списком
    subj_seen = OrderedDict()
    for g in D["grades"]:
        for s in D["grade_subjects"].get(g, []):
            if s in D["subjects"]:
                subj_seen.setdefault(s, []).append(g)
    sl = []
    for s, gs in subj_seen.items():
        nm = D["subjects"][s]["name"]
        sl.append('<span class="seo-subj">%s: %s</span>' % (
            esc(nm), ", ".join('<a href="/%d/%s/">%s</a>' % (g, esc(s), g) for g in gs)))
    body += ('<section class="seo-sec"><h2 class="seo-h2">Тесты по предметам и классам</h2>'
             '<div class="seo-subjlist">%s</div></section>' % "".join(sl))

    ld = [
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "WebSite"),
            ("name", PRODUCT), ("alternateName", "QKC"), ("url", canon),
            ("inLanguage", "ru"),
            ("publisher", OrderedDict([
                ("@type", "Organization"), ("name", ORG),
                ("url", "https://corp.qkc.runs-on.dev/")])),
        ]),
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "ItemList"),
            ("name", "Тесты по классам"), ("numberOfItems", len(rows)),
            ("itemListElement", [
                OrderedDict([("@type", "ListItem"), ("position", i + 1),
                             ("name", grade_label(g)),
                             ("url", "%s%d/" % (BASE, g))])
                for i, g in enumerate(D["grades"])]),
        ]),
    ]

    page = HEAD_TMPL % dict(title=esc(title), canon=esc(canon), desc=esc(desc),
                            ogtitle=esc(h1), ogdesc=esc(desc[:200]), ogtype="website",
                            base=BASE, jsonld=jsonld_block(ld),
                            crumbs=crumbs([("", "Главная")]))
    page += '<h1 class="seo-h1">%s</h1>\n%s' % (esc(h1), body)
    page += FOOT_TMPL % dict(authors=authors_html(), product=esc(PRODUCT), org=esc(ORG),
                             total=nq(total), grades=len(D["grades"]),
                             subjects=len(D["subjects"]))
    return "/", title, page


# ────────────────────────────────────────────────────────────── хрестоматия
"""
Посадочные страницы раздела «Литература» (хрестоматия).

Данные берём из gen/lit/*.py — того же единственного источника, из которого
gen/lit/build_lit.py собирает каталог приложения. Никаких отдельных списков
авторов здесь нет: расхождение между сайтом и приложением невозможно.

  /lit/                     — хаб: страны, авторы, правило отбора
  /lit/<страна>/<автор>/    — страница автора: биография, годы жизни,
                              список произведений с годами первой публикации

Страницы описывают ФАКТЫ (кто, что, когда написал, что в общественном
достоянии) — они полезны сами по себе и не зависят от того, подтянут ли уже
текст. Тексты подтягивает отдельный проход (gen/lit/fetch_lit.py).
"""
import sys as _sys

LIT_DIR = os.path.join(HERE, "lit")
if LIT_DIR not in _sys.path:
    _sys.path.insert(0, LIT_DIR)


def load_lit():
    """Каталог хрестоматии + список исключённых авторов. None, если данных нет."""
    try:
        import common as litcommon
        import russia, usa, china, japan, excluded as litexcluded
    except ImportError:
        return None
    countries = []
    for mod in (russia, usa, china, japan):
        c = dict(mod.COUNTRY)
        c["authors"] = mod.AUTHORS
        countries.append(c)
    return dict(common=litcommon, countries=countries, excluded=litexcluded)


def lit_year(common, y):
    return common.year_str(y)


def lit_work_status(common, w):
    return common.work_status(w)


def lit_author_page(L, country, a):
    """Страница одного автора. Возвращает (path, title, html) или None."""
    common = L["common"]
    if not slug_ok(country["slug"]) or not slug_ok(a["slug"]):
        return None
    path = "/lit/%s/%s/" % (country["slug"], a["slug"])
    canon = BASE + path
    works = [w for w in a["works"]
             if lit_work_status(common, w) != common.STATUS_REJECTED]
    if not works:
        return None
    works = sorted(works, key=lambda w: w["pub"])
    n = len(works)
    life = "%s–%s" % (lit_year(common, a["born"]), lit_year(common, a["died"]))
    if a["died"] is None:
        life = "даты жизни неизвестны"
    first = works[0]["title"]
    last = works[-1]["title"]

    title = ("%s (%s) — %s в общественном достоянии | Хрестоматия QKC"
             % (a["name"], life, n_works(n)))
    desc = ("%s, %s. %s с годами первой публикации: %s (%s) … %s (%s). "
            "%s Хрестоматия QKC публикует только тексты, перешедшие в общественное достояние."
            % (a["name"], life, n_works(n), first, lit_year(common, works[0]["pub"]),
               last, lit_year(common, works[-1]["pub"]), a["bio"]))
    desc = desc[:300]
    h1 = a["name"]

    genres = OrderedDict()
    for w in works:
        genres[w["genre"]] = genres.get(w["genre"], 0) + 1
    gstr = ", ".join("%s — %d" % (g, c) for g, c in sorted(genres.items(), key=lambda x: -x[1]))

    rows = []
    for w in works:
        st = lit_work_status(common, w)
        if st == common.STATUS_NEEDS_TRANSLATION:
            note = ("перевод проверяется" if w["lang"] != "ru" else "—")
        else:
            note = "общественное достояние"
        orig = (" <span class=\"seo-orig\">%s</span>" % esc(w["orig"])) if w.get("orig") else ""
        conf = (' <span class="seo-conf" title="Год первой публикации помечен как '
                'требующий сверки с Викиданными">год сверяется</span>') if w.get("conf") == "chk" else ""
        rows.append('<tr><th scope="row"><a href="/#lit?c=%s&amp;a=%s&amp;w=%s">%s</a>%s</th>'
                    '<td>%s</td><td>%s%s</td><td>%s</td></tr>'
                    % (esc(country["slug"]), esc(a["slug"]), esc(w["slug"]),
                       esc(w["title"]), orig, esc(w["genre"]),
                       esc(lit_year(common, w["pub"])), conf, esc(note)))

    body = ('<p class="seo-lede">%s (%s) — %s. В хрестоматии QKC %d '
            'произведений этого автора: годы первой публикации проверены, '
            'в каталог попадают только тексты, перешедшие в общественное достояние.</p>'
            '<div class="seo-cta"><a class="btn btn--primary btn--lg" '
            'href="/#lit?c=%s&amp;a=%s">Открыть в хрестоматии</a>'
            '<a class="btn btn--ghost" href="/lit/">Все авторы</a></div>'
            '<section class="seo-sec"><h2 class="seo-h2">Об авторе</h2>'
            '<table class="seo-table seo-facts"><tbody>'
            '<tr><th scope="row">Годы жизни</th><td>%s</td></tr>'
            '<tr><th scope="row">Период</th><td>%s</td></tr>'
            '<tr><th scope="row">Жанры в каталоге</th><td>%s</td></tr>'
            '<tr><th scope="row">Произведений</th><td>%d</td></tr>'
            '%s</tbody></table><p>%s</p></section>'
            % (esc(a["name"]), esc(life), esc(a["era"]), n,
               esc(country["slug"]), esc(a["slug"]),
               esc(life), esc(a["era"]), esc(gstr), n,
               ('<tr><th scope="row">Имя в оригинале</th><td>%s</td></tr>' % esc(a["orig"])) if a.get("orig") else "",
               esc(a["bio"])))

    body += ('<section class="seo-sec"><h2 class="seo-h2">Произведения: годы первой публикации</h2>'
             '<table class="seo-table"><thead><tr><th>Название</th><th>Жанр</th>'
             '<th>Первая публикация</th><th>Правовой статус</th></tr></thead>'
             '<tbody>%s</tbody></table>'
             '<p class="seo-note">Год указан по первой публикации, а не по дате '
             'написания: для авторского права важна именно она. Посмертные '
             'публикации в каталог не включаются, даже если текст написан раньше.</p>'
             '</section>' % "".join(rows))

    body += ('<section class="seo-sec"><h2 class="seo-h2">Почему здесь не всё</h2>'
             '<p>Произведение попадает в хрестоматию только если выполнены оба условия: '
             'автор умер раньше %d года <b>и</b> текст впервые опубликован раньше %d года. '
             'Первый заслон закрывает Россию (жизнь + 70 лет, с запасом на продление срока '
             'реабилитированным и погибшим в 1941–1945), второй — США (там с 1 января 2026 года '
             'свободно всё изданное до 1930-го). Отдельно проверяется перевод: он охраняется '
             'как произведение переводчика, поэтому у переводных текстов статус '
             '«перевод проверяется», пока не подтверждено, что срок истёк.</p>'
             '<p class="seo-note">Тексты подтягиваются в хрестоматию отдельным проходом '
             'и только из источников, где общественное достояние подтверждено. '
             'Сокращённые пересказы чужих текстов мы не публикуем: пересказ охраняемого '
             'произведения остаётся нарушением, сколько бы слов в нём ни было.</p>'
             '</section>' % (common.PD_DEATH_CUTOFF, common.PD_PUB_CUTOFF))

    others = [x for x in country["authors"] if x["slug"] != a["slug"] and x["works"]]
    if others:
        body += ('<section class="seo-sec"><h2 class="seo-h2">Другие авторы: %s</h2>'
                 '<div class="seo-subjlist">%s</div></section>'
                 % (esc(country["name"]),
                    "".join('<span class="seo-subj"><a href="/lit/%s/%s/">%s</a></span>'
                            % (esc(country["slug"]), esc(x["slug"]), esc(x["name"]))
                            for x in others[:40])))

    ld = [
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "Person"),
            ("name", a["name"]), ("url", canon),
            ("birthDate", str(a["born"]) if a["born"] and a["born"] > 0 else None),
            ("deathDate", str(a["died"]) if a["died"] and a["died"] > 0 else None),
            ("description", a["bio"]),
            ("knowsAbout", [g for g in genres]),
        ]),
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "ItemList"),
            ("name", "%s — произведения" % a["name"]), ("numberOfItems", n),
            ("itemListElement", [
                OrderedDict([("@type", "ListItem"), ("position", i + 1),
                             ("name", w["title"]),
                             ("url", "%s#lit?c=%s&a=%s&w=%s" % (BASE, country["slug"], a["slug"], w["slug"]))])
                for i, w in enumerate(works)]),
        ]),
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "BreadcrumbList"),
            ("itemListElement", [
                OrderedDict([("@type", "ListItem"), ("position", 1), ("name", "Главная"), ("item", BASE + "/")]),
                OrderedDict([("@type", "ListItem"), ("position", 2), ("name", "Литература"), ("item", BASE + "/lit/")]),
                OrderedDict([("@type", "ListItem"), ("position", 3), ("name", a["name"]), ("item", canon)]),
            ]),
        ]),
    ]
    ld = [x for x in ld if x]
    # Person с пустым birthDate ломает валидатор — чистим None
    for o in ld:
        for k in list(o.keys()):
            if o[k] is None:
                del o[k]

    page = HEAD_TMPL % dict(title=esc(title), canon=esc(canon), desc=esc(desc),
                            ogtitle=esc(h1), ogdesc=esc(desc[:200]), ogtype="profile",
                            base=BASE, jsonld=jsonld_block(ld),
                            crumbs=crumbs([("/", "Главная"), ("/lit/", "Литература"),
                                           (path, a["name"])]))
    page += '<h1 class="seo-h1">%s</h1>\n%s' % (esc(h1), body)
    page += FOOT_TMPL % dict(authors=authors_html(), product=esc(PRODUCT), org=esc(ORG),
                             total="%d произв." % n, grades="1 стране",
                             subjects="%d" % 1)
    return path, title, page


def build_lit_pages(L, pages_out):
    """Хаб /lit/ + страницы авторов. Возвращает [(path, title, html, kind), ...]."""
    common = L["common"]
    out = []
    countries = L["countries"]
    n_auth = sum(len(c["authors"]) for c in countries)
    n_wk = sum(len(a["works"]) for c in countries for a in c["authors"])
    n_excl = len(L["excluded"].AUTHORS)

    # ── страницы авторов ──
    author_rows = OrderedDict()
    for c in countries:
        rows = []
        for a in sorted(c["authors"], key=lambda x: (x["born"] is None, x["born"] or 0)):
            r = lit_author_page(L, c, a)
            if not r:
                continue
            path, title, html = r
            out.append((path, title, html, "lit-author"))
            pages_out.append(dict(path=path, title=title, kind="lit-author",
                                  country=c["slug"], author=a["slug"]))
            rows.append('<tr><th scope="row"><a href="%s">%s</a></th><td>%s</td>'
                        '<td>%s</td><td>%d</td></tr>'
                        % (esc(path), esc(a["name"]),
                           esc("%s–%s" % (lit_year(common, a["born"]), lit_year(common, a["died"]))),
                           esc(a["era"]), len(a["works"])))
        author_rows[c["slug"]] = "".join(rows)

    # ── хаб ──
    title = ("Хрестоматия: %s и %s в общественном достоянии | QKC"
             % (n_authors(n_auth), n_works(n_wk)))
    desc = ("Русская, американская, китайская и японская классика, перешедшая в "
            "общественное достояние: %s, %s с годами первой публикации. "
            "Рассказы, стихи, сказки, повести и романы. Открытый проект OuRi, "
            "без регистрации."
            % (n_authors(n_auth), n_works(n_wk)))
    h1 = "Литература: хрестоматия общественного достояния"
    body = ('<p class="seo-lede">%s и %s из четырёх литератур — '
            'русской, американской, китайской и японской. В каталог попадают только '
            'тексты, перешедшие в общественное достояние: мы проверяем и год смерти '
            'автора, и год первой публикации, а для переводных вещей — ещё и срок '
            'охраны перевода. Ниже у каждого автора указаны годы жизни и полный список '
            'произведений с годами.</p>'
            '<div class="seo-cta"><a class="btn btn--primary btn--lg" href="/#lit">Открыть хрестоматию</a>'
            '<a class="btn btn--ghost" href="/#setup">Тренажёр тестов</a></div>'
            % (n_authors(n_auth), n_works(n_wk)))

    for c in countries:
        rows = author_rows.get(c["slug"], "")
        if not rows:
            continue
        body += ('<section class="seo-sec"><h2 class="seo-h2">%s — %s</h2>'
                 '<p>%s</p>'
                 '<table class="seo-table"><thead><tr><th>Автор</th><th>Годы жизни</th>'
                 '<th>Период</th><th>Произведений</th></tr></thead><tbody>%s</tbody></table>'
                 '</section>' % (esc(c["name"]), esc(c["label"]), esc(c["rule"]), rows))

    body += ('<section class="seo-sec"><h2 class="seo-h2">Как мы отбираем тексты</h2>'
             '<ol class="seo-list">'
             '<li><b>Автор умер раньше %d года.</b> В России срок охраны — жизнь плюс '
             '70 лет; реабилитированным и погибшим в 1941–1945 он продлевается на 4 года, '
             'поэтому порог взят с запасом.</li>'
             '<li><b>Текст впервые опубликован раньше %d года.</b> В США с 1 января 2026 года '
             'в общественном достоянии всё изданное до 1930-го, независимо от года смерти автора.</li>'
             '<li><b>Перевод проверен отдельно.</b> Перевод — самостоятельное произведение '
             'переводчика. Пока срок его охраны не подтверждён как истёкший, переводной текст '
             'в хрестоматию не попадает.</li>'
             '<li><b>Год — только первой публикации.</b> Посмертные публикации не проходят, '
             'даже если написаны раньше: для права важна дата выхода в свет.</li>'
             '</ol>'
             '<p class="seo-note">Сокращённые пересказы охраняемых произведений мы не публикуем. '
             'Производный текст остаётся производным независимо от объёма.</p>'
             '</section>' % (common.PD_DEATH_CUTOFF, common.PD_PUB_CUTOFF))

    if L["excluded"].AUTHORS:
        rows = "".join(
            '<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (esc(x[0]), esc(x[1]), esc(x[2]), esc(x[4]))
            for x in L["excluded"].AUTHORS)
        body += ('<section class="seo-sec"><h2 class="seo-h2">Кого здесь сознательно нет</h2>'
                 '<p>Этих авторов часто ищут вместе с классикой, но их тексты всё ещё '
                 'под охраной — или охраняется их перевод. %d имени, чтобы не было '
                 'недопонимания.</p>'
                 '<table class="seo-table"><thead><tr><th>Автор</th><th>Годы</th>'
                 '<th>Страна</th><th>Почему не публикуем</th></tr></thead>'
                 '<tbody>%s</tbody></table></section>' % (n_excl, rows))

    ld = [
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "CollectionPage"),
            ("name", h1), ("url", BASE + "/lit/"), ("inLanguage", "ru"),
            ("description", desc),
            ("isPartOf", OrderedDict([("@type", "WebSite"), ("name", PRODUCT), ("url", BASE + "/")])),
        ]),
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "ItemList"),
            ("name", "Авторы хрестоматии"), ("numberOfItems", n_auth),
            ("itemListElement", [
                OrderedDict([("@type", "ListItem"), ("position", i + 1),
                             ("name", a["name"]),
                             ("url", "%s/lit/%s/%s/" % (BASE, c["slug"], a["slug"]))])
                for i, (c, a) in enumerate((c, a) for c in countries for a in c["authors"])]),
        ]),
        OrderedDict([
            ("@context", "https://schema.org"), ("@type", "BreadcrumbList"),
            ("itemListElement", [
                OrderedDict([("@type", "ListItem"), ("position", 1), ("name", "Главная"), ("item", BASE + "/")]),
                OrderedDict([("@type", "ListItem"), ("position", 2), ("name", "Литература"), ("item", BASE + "/lit/")]),
            ]),
        ]),
    ]
    page = HEAD_TMPL % dict(title=esc(title), canon=esc(BASE + "/lit/"), desc=esc(desc),
                            ogtitle=esc(h1), ogdesc=esc(desc[:200]), ogtype="website",
                            base=BASE, jsonld=jsonld_block(ld),
                            crumbs=crumbs([("/", "Главная"), ("", "Литература")]))
    page += '<h1 class="seo-h1">%s</h1>\n%s' % (esc(h1), body)
    page += FOOT_TMPL % dict(authors=authors_html(), product=esc(PRODUCT), org=esc(ORG),
                             total="%d произв." % n_wk, grades="%d странам" % len(countries),
                             subjects="%d" % n_auth)
    out.insert(0, ("/lit/", title, page, "lit-hub"))
    return out


# ────────────────────────────────────────────────────────────── sitemap/robots/css
def build_sitemap(pages):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    out.append('  <url><loc>%s/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>' % BASE)
    for p in pages:
        if p["path"] == "/":
            continue
        pr = "0.9" if p["kind"] == "subject" else "0.8"
        out.append('  <url><loc>%s%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>'
                   % (BASE, p["path"], pr))
    out.append("</urlset>")
    return "\n".join(out) + "\n"


ROBOTS = """User-agent: *
Allow: /
Disallow: /gen/
Disallow: /test/
Disallow: /assets/bank-
Disallow: /assets/bank.json

Sitemap: {base}/sitemap.xml
Host: {host}
""".format(base=BASE, host="qkc.runs-on.dev")

SEO_CSS = """/* ═══════════════════════════════════════════════════════════════
   OuRi / QKC — стили статических SEO-страниц (классы и предметы).
   Только токены из css/style.css, ничего своего по цветам: страницы
   обязаны выглядеть как остальной сайт (строго монохром).
   ═══════════════════════════════════════════════════════════════ */

.seo-wrap{ width:min(100% - 32px, 900px); margin-inline:auto }
.seo-nav{ position:sticky; top:0; z-index:20; display:flex; align-items:center;
  justify-content:space-between; gap:16px; padding:12px clamp(14px,3vw,26px);
  background:color-mix(in srgb, var(--bg) 88%, transparent);
  border-bottom:1px solid var(--line); backdrop-filter:blur(10px) }
.seo-brand{ display:flex; align-items:center; gap:9px; font-family:var(--font-d);
  font-size:.95rem; letter-spacing:.01em; color:var(--text) }
.seo-brand img{ border-radius:7px }
.seo-brand b{ font-weight:800 }
.seo-beta{ border:1px solid var(--line2); border-radius:999px; padding:1px 8px;
  font-size:.62rem; letter-spacing:.14em; color:var(--muted) }
.seo-topcta{ flex:none; border:1px solid var(--line2); border-radius:999px;
  padding:7px 15px; font-size:.82rem; color:var(--text2); transition:.2s }
.seo-topcta:hover{ border-color:var(--text); color:var(--text) }

.seo-crumbs{ padding:14px clamp(14px,3vw,26px) 0 }
.seo-crumbs ol{ display:flex; flex-wrap:wrap; gap:6px; list-style:none; margin:0;
  padding:0; font-size:.78rem; color:var(--muted2) }
.seo-crumbs li + li::before{ content:"/"; margin-right:6px; color:var(--muted2) }
.seo-crumbs a{ color:var(--muted); border-bottom:1px solid transparent }
.seo-crumbs a:hover{ color:var(--text); border-bottom-color:var(--line2) }
.seo-crumbs [aria-current]{ color:var(--text2) }

.seo-h1{ font-family:var(--font-d); font-weight:800; letter-spacing:-.02em;
  font-size:clamp(1.75rem,4.4vw,2.9rem); line-height:1.1; margin:18px 0 14px }
.seo-lede{ color:var(--text2); font-size:clamp(1rem,1.5vw,1.09rem); max-width:74ch;
  margin:0 0 24px }
.seo-h2{ font-family:var(--font-d); font-weight:700; letter-spacing:-.01em;
  font-size:clamp(1.15rem,2.3vw,1.5rem); margin:0 0 12px }
.seo-p{ color:var(--text2); max-width:76ch; margin:0 0 14px }

.seo-cta{ display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 8px }
.seo-sec{ margin-top:clamp(34px,5vw,56px); padding-top:clamp(20px,3vw,28px);
  border-top:1px solid var(--line) }

.seo-stats{ display:grid; gap:12px; margin:0 0 16px;
  grid-template-columns:repeat(auto-fit,minmax(170px,1fr)) }
.seo-stats>div{ border:1px solid var(--line); border-radius:var(--r-sm);
  padding:14px 16px; background:var(--surface) }
.seo-stats dt{ font-size:.74rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted2); margin-bottom:6px }
.seo-stats dd{ margin:0; font-family:var(--font-d); font-weight:700;
  font-size:1.02rem; color:var(--text) }

.seo-table{ width:100%; border-collapse:collapse; font-size:.92rem }
.seo-table th,.seo-table td{ text-align:left; padding:11px 12px;
  border-bottom:1px solid var(--line); vertical-align:top }
.seo-table thead th{ font-size:.72rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted2); font-weight:600; border-bottom:1px solid var(--line2) }
.seo-table tbody th{ font-weight:600; color:var(--text) }
.seo-table td{ color:var(--text2) }
.seo-table a{ border-bottom:1px solid var(--line2) }
.seo-table a:hover{ color:var(--text); border-bottom-color:var(--text) }
.seo-rowall th,.seo-rowall td{ border-bottom:none; font-weight:700; color:var(--text) }
@media (max-width:640px){
  .seo-table thead{ display:none }
  .seo-table tr{ display:grid; gap:4px; padding:12px 0; border-bottom:1px solid var(--line) }
  .seo-table th,.seo-table td{ border:none; padding:2px 0 }
}

.seo-chips{ display:flex; flex-wrap:wrap; gap:8px }
.seo-chip{ border:1px solid var(--line); border-radius:999px; padding:6px 14px;
  font-size:.82rem; color:var(--muted); transition:.2s }
.seo-chip:hover{ color:var(--text); border-color:var(--line2) }

.seo-qlist{ list-style:none; counter-reset:q; margin:0 0 18px; padding:0;
  display:grid; gap:14px }
.seo-q{ border:1px solid var(--line); border-radius:var(--r-sm); padding:16px 18px;
  background:var(--surface) }
.seo-q__t{ margin:0 0 12px; color:var(--text); font-weight:500 }
.seo-q__n{ display:inline-block; min-width:1.6em; color:var(--muted2);
  font-family:var(--font-mono); font-size:.9em }
.seo-q__opts{ list-style:none; margin:0 0 12px; padding:0; display:grid; gap:7px }
.seo-q__opt{ border:1px solid var(--line); border-radius:9px; padding:9px 12px;
  color:var(--text2); font-size:.92rem }
.seo-q__hint{ margin:0 0 12px; color:var(--muted); font-size:.86rem }
.seo-q__ans{ border-top:1px dashed var(--line2); padding-top:10px }
.seo-q__ans summary{ cursor:pointer; color:var(--muted); font-size:.86rem;
  list-style:none }
.seo-q__ans summary::-webkit-details-marker{ display:none }
.seo-q__ans summary::before{ content:"+ "; font-family:var(--font-mono) }
.seo-q__ans[open] summary::before{ content:"− " }
.seo-q__ans summary:hover{ color:var(--text) }
.seo-q__ans p{ margin:10px 0 0; color:var(--text2); font-size:.92rem;
  border-left:2px solid var(--line2); padding-left:12px }
.seo-q__meta{ margin:10px 0 0; font-size:.76rem; color:var(--muted2) }

.seo-faq{ display:grid; gap:10px }
.seo-faq details{ border:1px solid var(--line); border-radius:var(--r-sm);
  padding:13px 16px; background:var(--surface) }
.seo-faq summary{ cursor:pointer; font-weight:600; color:var(--text); list-style:none }
.seo-faq summary::-webkit-details-marker{ display:none }
.seo-faq summary::before{ content:"+ "; font-family:var(--font-mono); color:var(--muted2) }
.seo-faq details[open] summary::before{ content:"− " }
.seo-faq p{ margin:10px 0 0; color:var(--text2); font-size:.93rem; max-width:76ch }

.seo-seolink{ color:var(--text2); max-width:80ch }
.seo-seolink a{ display:inline-block; margin:2px 6px 2px 0; padding:3px 10px;
  border:1px solid var(--line); border-radius:999px; font-size:.84rem; color:var(--muted) }
.seo-seolink a:hover{ color:var(--text); border-color:var(--line2) }
.seo-subjlist{ display:grid; gap:7px }
.seo-subj{ font-size:.88rem; color:var(--muted) }
.seo-subj a{ color:var(--text2); border-bottom:1px solid var(--line) }
.seo-subj a:hover{ color:var(--text) }

.seo-foot{ margin-top:clamp(46px,7vw,86px); border-top:1px solid var(--line);
  padding:28px 0 40px; color:var(--muted); font-size:.86rem }
.seo-foot p{ max-width:82ch }
.seo-footnav a{ border-bottom:1px solid var(--line) }
.seo-footnav a:hover{ color:var(--text) }
.seo-note{ color:var(--muted2); font-size:.8rem }

.seo-authors{ margin-top:16px; padding-top:14px; border-top:1px solid var(--line);
  display:flex; flex-wrap:wrap; gap:8px 14px; align-items:center; justify-content:center;
  text-align:center }
.seo-authors__label{ font-family:var(--font-mono); font-size:.68rem; letter-spacing:.16em;
  text-transform:uppercase; color:var(--muted2) }
.seo-authors__list{ display:flex; flex-wrap:wrap; gap:8px 12px; align-items:center;
  justify-content:center }
.seo-authors__list a{ display:inline-flex; align-items:center; gap:7px; padding:5px 12px;
  border:1px solid var(--line); border-radius:999px; color:var(--text2); font-size:.82rem;
  font-weight:600; text-decoration:none; transition:.2s; max-width:100% }
.seo-authors__list a:hover{ color:var(--text); border-color:var(--line2);
  background:var(--surface2) }
.seo-authors__list svg{ flex:none; opacity:.75 }

@media (prefers-reduced-motion:reduce){
  .seo-nav,.seo-topcta,.seo-chip,.seo-subj a{ transition:none }
}
"""


# ────────────────────────────────────────────────────────────── главное
def main():
    D = load()
    pages = []
    total_bytes = 0

    # хаб-страница «все классы»
    r = build_index_page(D, pages)
    if r:
        path, title, html = r
        total_bytes += write("seo/index.html", html)
        pages.append(dict(path="/seo/", title=title, kind="index"))
        print("  /seo/                     %s" % title[:62])

    for g in D["grades"]:
        r = build_grade_page(D, g)
        if r:
            path, title, html = r
            total_bytes += write(path.lstrip("/") + "index.html", html)
            pages.append(dict(path=path, title=title, kind="grade"))
            print("  %-25s %s" % (path, title[:58]))
        for subj in D["grade_subjects"].get(g, []):
            if subj not in D["subjects"] or not slug_ok(subj):
                continue
            r = build_subject_page(D, g, subj)
            if not r:
                continue
            path, title, html = r
            total_bytes += write(path.lstrip("/") + "index.html", html)
            pages.append(dict(path=path, title=title, kind="subject",
                              grade=g, subject=subj))
            print("  %-25s %s" % (path, title[:58]))

    # хрестоматия: хаб + страницы авторов (данные — gen/lit/*.py)
    L = load_lit()
    if L:
        lit_rows = []
        lit_pages = build_lit_pages(L, lit_rows)
        for path, title, html, kind in lit_pages:
            total_bytes += write(path.lstrip("/") + "index.html", html)
            if kind == "lit-hub":      # хаб добавляется в build_lit_pages последним,
                lit_rows.insert(0, dict(path=path, title=title, kind=kind))   # в pages_out его не было
        pages.extend(lit_rows)
        print("  /lit/ и страницы авторов: %d" % len(lit_pages))
    else:
        print("  хрестоматия: gen/lit/*.py не найдены, страницы не собирались")

    write("sitemap.xml", build_sitemap(pages))
    write("robots.txt", ROBOTS)
    write("css/seo.css", SEO_CSS)
    write("assets/seo-pages.json",
          json.dumps(dict(base=BASE, generatedBy="gen/build_seo.py",
                          bankBuiltAt=D["built"], total=D["total"],
                          count=len(pages),
                          lit=sum(1 for p in pages if p["kind"].startswith("lit")),
                          pages=pages),
                     ensure_ascii=False, indent=1))

    n_grade = sum(1 for p in pages if p["kind"] == "grade")
    n_subj = sum(1 for p in pages if p["kind"] == "subject")
    n_lit = sum(1 for p in pages if p["kind"].startswith("lit"))
    n_other = len(pages) - n_grade - n_subj - n_lit
    print("\n  собрано страниц: %d  (классов: %d, предметов: %d, литература: %d, прочие: %d)"
          % (len(pages), n_grade, n_subj, n_lit, n_other))
    print("  суммарно: %.2f MB HTML" % (total_bytes / 1048576.0))
    print("  sitemap.xml: %d URL" % len(pages))
    return pages


if __name__ == "__main__":
    main()
