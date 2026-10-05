# -*- coding: utf-8 -*-
"""Общие хелперы для курируемых предметов."""
import random
from build_bank import Item, build_choice, build_input, build_tf

VOW = set("аеёиоуыэюя")
CONS = set("бвгджзйклмнпрстфхцчшщ")


def syl(w):
    parts, cur = [], ""
    for ch in w:
        cur += ch
        if ch in VOW:
            parts.append(cur)
            cur = ""
    if cur:
        if parts:
            parts[-1] += cur
        else:
            parts.append(cur)
    return parts


def n_vow(w):
    return sum(1 for c in w if c in VOW)


def n_cons(w):
    return sum(1 for c in w if c in CONS)


def mask(w, prefer_vowel=True, pos=None):
    letters = list(w)
    cand = [i for i, c in enumerate(letters) if (c in VOW) == prefer_vowel]
    if not cand:
        return None
    i = pos if pos is not None else random.choice(cand)
    letters[i] = "_"
    return "".join(letters), w[i], i


def word_items(word, stress, topic, quarters, allow_input=True):
    """word — слово; stress — номер ударного слога (1-based)."""
    out = []
    s = syl(word)
    n = max(len(s), 1)
    nv, nc = n_vow(word), n_cons(word)
    distr = [x for x in (n + 1, n - 1, n + 2, nv + nc) if x > 0 and x != n]
    out.append(build_choice(f"Сколько слогов в слове «{word}»?", n, distr,
                            f"Слово делится так: {'-'.join(s)}. Значит, слогов: {n}.", topic + " · слоговой анализ", quarters))
    out.append(build_choice(f"Сколько гласных букв в слове «{word}»?", nv, [x for x in (nv + 1, nv - 1, nc, nv + 2) if x > 0 and x != nv],
                            f"Гласные буквы: {''.join(c for c in word if c in VOW)} — всего {nv}.", topic + " · звуки и буквы", quarters))
    out.append(build_choice(f"Сколько согласных букв в слове «{word}»?", nc, [x for x in (nc + 1, nc - 1, nv, nc + 2) if x > 0 and x != nc],
                            f"Согласные: {''.join(c for c in word if c in CONS)} — всего {nc}.", topic + " · звуки и буквы", quarters))
    if stress and n > 1:
        pos_ans = f"на {stress}-й слог"
        pos_wrong = [f"на {i}-й слог" for i in range(1, n + 1) if i != stress]
        out.append(build_choice(f"На какой слог падает ударение в слове «{word}»?", pos_ans, pos_wrong[:3],
                                f"Ударный слог: «{s[stress-1]}» — это {stress}-й слог ({'-'.join(s)}).", topic + " · орфоэпия", quarters))
    m = mask(word, prefer_vowel=True)
    if m and n_vow(word) >= 1:
        masked, letter, _i = m
        if allow_input and random.random() < 0.5:
            out.append(build_input(f"Вставь пропущенную букву: {masked}", letter,
                                   f"Правильно: {word}. Пропущена буква «{letter}».", topic + " · орфография", quarters))
        else:
            out.append(build_choice(f"Вставь пропущенную букву: {masked}", letter,
                                    [c for c in "аоиеыуяе" if c != letter][:3],
                                    f"Правильно: {word}. Пропущена буква «{letter}».", topic + " · орфография", quarters))
    good = "-".join(s)
    variants = []
    if n > 1:
        variants.append("-".join([s[0] + "".join(s[1:])]) if n > 1 else good)
        variants.append("".join(s[:1]) + "-" + "".join(s[1:2]) + "-" + "".join(s[2:]) if n > 2 else "-".join(reversed(s)))
        variants.append("-".join(reversed(s)))
        variants.append("".join(word[:2]) + "-" + "".join(word[2:]))
    variants = [v for v in variants if v != good and len(v) <= 24]
    out.append(build_choice(f"Раздели слово «{word}» на слоги.", good, variants[:3] or [word, good + "а", good.replace("-", " ")],
                            f"Слогов {n}: {good}.", topic + " · слоговой анализ", quarters))
    return out


def stress_items(pairs, quarters, topic="Орфоэпия"):
    """pairs: [(слово, номер ударного слога)]"""
    out = []
    for w, st in pairs:
        n = max(len(syl(w)), 1)
        wrong = [f"на {i}-м слоге" for i in range(1, n + 2) if i != st][:3]
        out.append(build_choice(f"Где ударение в слове «{w}»?", f"на {st}-м слоге", wrong,
                                f"«{w}»: ударение падает на {st}-й слог.", topic + " · нормы ударения", quarters))
        other = [x for x, s in pairs if x != w and syl(x)]
        random.shuffle(other)
        if other and n > 1:
            out.append(build_choice(f"В каком слове ударение падает на {st}-й слог?", w, other[:3],
                                    f"В слове «{w}» ударение на {st}-м слоге.", topic + " · нормы ударения", quarters))
    return out


def pairs_items(pairs, q_fwd, q_back, topic, quarters, tf=True, exp=None, tfmt="{a} — {b}"):
    """pairs: [(левое, правое)] — генерирует прямой, обратный и true/false вопросы."""
    out = []
    lefts = [a for a, _ in pairs]
    rights = [b for _, b in pairs]
    for a, b in pairs:
        w = [x for x in rights if x != b]
        random.shuffle(w)
        out.append(build_choice(q_fwd.format(a=a, b=b), b, w[:3],
                                (exp or "Правильный ответ: {b}.").format(a=a, b=b), topic, quarters))
        w2 = [x for x in lefts if x != a]
        random.shuffle(w2)
        out.append(build_choice(q_back.format(a=a, b=b), a, w2[:3],
                                (exp or "Правильный ответ: {a}.").format(a=a, b=b), topic, quarters))
        if tf and w and w2:
            if random.random() < 0.5:
                st = tfmt.format(a=a, b=b)
                out.append(build_tf(f"Верно ли, что {st}?", "Верно", f"Да: {st}.", topic, quarters))
            else:
                st = tfmt.format(a=a, b=w[0])
                out.append(build_tf(f"Верно ли, что {st}?", "Неверно",
                                    f"Неверно. Правильно: {tfmt.format(a=a, b=b)}.", topic, quarters))
    return out


def direct(rows, default_topic=""):
    """rows: [(вопрос, верный ответ, [неверные], объяснение, тема, четверти)]"""
    out = []
    for r in rows:
        text, ans, wrongs, exp = r[0], r[1], r[2], r[3]
        topic = r[4] if len(r) > 4 and r[4] else default_topic
        quarters = r[5] if len(r) > 5 and r[5] else [1, 2, 3, 4]
        out.append(build_choice(text, ans, wrongs, exp, topic, quarters))
    return out


def shuffle_distractors(pool, correct, k=3):
    w = [x for x in pool if x != correct]
    random.shuffle(w)
    return w[:k]
