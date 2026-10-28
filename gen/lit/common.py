# -*- coding: utf-8 -*-
"""
Схема данных раздела «Хрестоматия» и общие константы.

Здесь только ФАКТЫ: имена, даты жизни, годы издания, жанры. Факты не охраняются
авторским правом. Самих текстов в этих файлах нет — их тянет gen/fetch_lit.py.

ПРАВИЛА ОТБОРА (проверяет gen/build_lit.py, в рантайме их не обойти)
--------------------------------------------------------------------
1. died < 1955.
   РФ: жизнь + 70 лет. Реабилитированным и погибшим в 1941-1945 срок продлён
   на 4 года, поэтому порог взят с запасом: 1954 + 4 = 1958 — всё равно до 2026.
2. pub < 1930.
   США: с 1 января 2026 в PD всё опубликованное до 1930, независимо от года
   смерти. Заслон «died < 1955 И pub < 1930» закрывает и РФ, и США — самые
   строгие из нужных нам юрисдикций.
3. Перевод — самостоятельное произведение переводчика.
   Если lang != "ru", русский текст охраняется, пока не истёк срок у переводчика.
   Такие произведения получают статус needs-translation-check и в банк текстов
   не попадают, пока не заполнены tr / tr_died (< 1955).
4. Год издания — только дата ПЕРВОЙ публикации. Посмертные публикации
   («После бала», 1911; «Хаджи-Мурат», 1912) под заслон не проходят и в каталог
   не включены, даже если написаны раньше.

ЧЕСТНОСТЬ ДАННЫХ
----------------
conf="ok"  — год общепризнанный.
conf="chk" — год стоит сверить с Викиданными перед публикацией текста.
Произведение без известного года первой публикации в список не попадает —
догадки вместо даты здесь запрещены.

Отрицательные годы — до н. э. Отображаются как «551 до н. э.».
"""

PD_DEATH_CUTOFF = 1955
PD_PUB_CUTOFF = 1930

GENRES = ("рассказ", "стихотворение", "сказка", "повесть", "роман", "поэма",
          "драма", "басня", "очерк", "новелла", "афоризмы", "трактат", "ода",
          "комедия", "цикл стихов", "сборник")

STATUS_OK = "ok"
STATUS_NEEDS_TRANSLATION = "needs-translation-check"
STATUS_REJECTED = "rejected"


def W(slug, title, genre, pub, lang="ru", orig=None, conf="ok", tr=None, tr_died=None):
    """Произведение. `orig` — название в оригинале (для переводов)."""
    return dict(slug=slug, title=title, orig=orig, genre=genre, pub=pub,
                lang=lang, conf=conf, tr=tr, tr_died=tr_died)


def A(slug, name, orig, born, died, era, bio, genres, works):
    """Автор. born/died — целые; отрицательные = до н. э.; died=None = дошло
    до нас под именем, но даты жизни неизвестны (античная/древняя традиция)."""
    return dict(slug=slug, name=name, orig=orig, born=born, died=died,
                era=era, bio=bio, genres=genres, works=list(works))


def year_str(y):
    """551 -> '551'; -551 -> '551 до н. э.'; None -> '?'"""
    if y is None:
        return "?"
    return str(-y) + " до н. э." if y < 0 else str(y)


def author_status(a):
    """Проходит ли автор заслон по году смерти."""
    if a["died"] is None:
        return STATUS_OK
    return STATUS_OK if a["died"] < PD_DEATH_CUTOFF else STATUS_REJECTED


def work_status(w):
    """Проходит ли произведение оба заслона."""
    if w["pub"] is None or w["pub"] >= PD_PUB_CUTOFF:
        return STATUS_REJECTED
    if w["lang"] != "ru":
        if w["tr"] is None or w["tr_died"] is None or w["tr_died"] >= PD_DEATH_CUTOFF:
            return STATUS_NEEDS_TRANSLATION
    return STATUS_OK
