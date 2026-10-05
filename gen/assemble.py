# -*- coding: utf-8 -*-
"""Сборка банка: класс -> предмет -> четверть -> вопросы (строго)."""
import json, os, sys, random, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_bank import gen_math, gen_physics, gen_chem, gen_info, uniq, Item
from data_english import gen_english
from data_russian import gen_russian
from data_primary import gen_reading, gen_om
from data_lit import gen_lit
from data_hist import gen_hist
from data_geo import gen_geo
from data_bio import gen_bio
from data_soc import gen_soc
from data_light import gen_izo, gen_music, gen_tech, gen_obzh, gen_pe
from data_kinder import GENS as KINDER_GENS

TARGET_PER_QUARTER = 44
PAD_MIN = 36
MAX_PASSES = 14

# ---- каталог: (id, название, короткое имя, иконка) ----
SUBJECTS = {
    "math":    ("Математика", "мат", "МА"),
    "algebra": ("Алгебра", "алг", "АЛ"),
    "geom":    ("Геометрия", "геом", "ГМ"),
    "russian": ("Русский язык", "рус", "РУ"),
    "reading": ("Литературное чтение", "чтен", "ЧТ"),
    "lit":     ("Литература", "лит", "ЛИ"),
    "om":      ("Окружающий мир", "окр", "ОК"),
    "english": ("Английский язык", "англ", "АН"),
    "physics": ("Физика", "физ", "ФЗ"),
    "chemistry": ("Химия", "хим", "ХМ"),
    "biology": ("Биология", "био", "БЛ"),
    "geography": ("География", "геог", "ГР"),
    "history": ("История", "ист", "ИС"),
    "social":  ("Обществознание", "общ", "ОБ"),
    "informatics": ("Информатика", "инф", "ИН"),
    "art":     ("ИЗО", "изо", "ИЗ"),
    "music":   ("Музыка", "муз", "МЗ"),
    "tech":    ("Технология", "тех", "ТХ"),
    "obzh":    ("ОБЖ", "обж", "ОЖ"),
    "pe":      ("Физкультура", "физ-ра", "ФК"),
}

# ---- какие предметы в каком классе (строго) ----
GRADE_SUBJECTS = {
    0:  ["math", "russian", "om", "english", "art"],
    1:  ["math", "russian", "reading", "om", "english", "art", "music", "tech", "pe", "obzh"],
    2:  ["math", "russian", "reading", "om", "english", "art", "music", "tech", "pe", "obzh"],
    3:  ["math", "russian", "reading", "om", "english", "art", "music", "tech", "pe", "obzh"],
    4:  ["math", "russian", "reading", "om", "english", "art", "music", "tech", "pe", "obzh"],
    5:  ["math", "russian", "lit", "english", "biology", "geography", "history", "informatics", "art", "music", "tech", "pe", "obzh"],
    6:  ["math", "russian", "lit", "english", "biology", "geography", "history", "social", "informatics", "art", "music", "tech", "pe", "obzh"],
    7:  ["algebra", "geom", "russian", "lit", "english", "physics", "biology", "geography", "history", "social", "informatics", "art", "music", "tech", "pe", "obzh"],
    8:  ["algebra", "geom", "russian", "lit", "english", "physics", "chemistry", "biology", "geography", "history", "social", "informatics", "art", "music", "tech", "pe", "obzh"],
    9:  ["algebra", "geom", "russian", "lit", "english", "physics", "chemistry", "biology", "geography", "history", "social", "informatics", "art", "music", "pe", "obzh"],
    10: ["algebra", "geom", "russian", "lit", "english", "physics", "chemistry", "biology", "geography", "history", "social", "informatics", "pe"],
    11: ["algebra", "geom", "russian", "lit", "english", "physics", "chemistry", "biology", "geography", "history", "social", "informatics", "pe"],
}

GEN_MAP = {
    "russian": lambda g, s: gen_russian(g, s),
    "reading": lambda g, s: gen_reading(g, s),
    "lit": lambda g, s: gen_lit(g, s),
    "om": lambda g, s: gen_om(g, s),
    "english": lambda g, s: gen_english(g, s),
    "physics": lambda g, s: gen_physics(g, s),
    "chemistry": lambda g, s: gen_chem(g, s),
    "biology": lambda g, s: gen_bio(g, s),
    "geography": lambda g, s: gen_geo(g, s),
    "history": lambda g, s: gen_hist(g, s),
    "social": lambda g, s: gen_soc(g, s),
    "informatics": lambda g, s: gen_info(g, s),
    "art": lambda g, s: gen_izo(g, s),
    "music": lambda g, s: gen_music(g, s),
    "tech": lambda g, s: gen_tech(g, s),
    "obzh": lambda g, s: gen_obzh(g, s),
    "pe": lambda g, s: gen_pe(g, s),
}

GEOM_TOPICS = {"Геометрия", "Геометрия: треугольник", "Геометрия: углы", "Геометрия: окружность", "Геометрия: многоугольники",
               "Теорема Пифагора", "Четырёхугольники", "Площади фигур", "Векторы", "Стереометрия", "Координаты"}


def collect_pool(grade, subj):
    """Собирает большой пул вопросов (несколько проходов с разными сидами)."""
    pool = []
    if grade == 0:
        fn = KINDER_GENS[subj]
        for p in range(MAX_PASSES):
            pool.extend([x for x in fn(seed=grade * 31 + p * 17 + 5) if x])
            if p >= 2 and len(uniq(pool)) >= TARGET_PER_QUARTER * 4 + 20:
                break
        return uniq(pool)
    if subj in ("math", "algebra", "geom"):
        passes = MAX_PASSES
        for p in range(passes):
            items = [x for x in gen_math(grade, seed=grade * 1000 + p * 97 + 13) if x]
            if subj in ("algebra", "geom"):
                items = [x for x in items if (x.topic.split(" · ")[0] in GEOM_TOPICS) == (subj == "geom")]
            pool.extend(items)
            if p >= 4 and len(uniq(pool)) >= TARGET_PER_QUARTER * 4 + 20:
                break
    else:
        fn = GEN_MAP[subj]
        for p in range(MAX_PASSES):
            items = [x for x in fn(grade, grade * 7919 + p * 131 + 7) if x]
            pool.extend(items)
            if p >= 2 and len(uniq(pool)) >= TARGET_PER_QUARTER * 4 + 20:
                break
    return uniq(pool)


def deal_by_quarters(pool, nq=4):
    """Строгая раздача: каждый вопрос попадает ровно в одну четверть."""
    buckets = collections.defaultdict(list)
    for it in pool:
        qs = it.q if it.q else list(range(1, nq + 1))
        buckets[tuple(sorted(qs))].append(it)
    for k in buckets:
        random.shuffle(buckets[k])
    quarters = {q: [] for q in range(1, nq + 1)}
    keys = sorted(buckets.keys(), key=lambda k: -len(buckets[k]))
    progress = True
    while progress:
        progress = False
        for q in range(1, nq + 1):
            if len(quarters[q]) >= TARGET_PER_QUARTER:
                continue
            # берём из самой «богатой» подходящей корзины
            cand = [k for k in keys if q in k and buckets[k]]
            if not cand:
                continue
            k = max(cand, key=lambda kk: len(buckets[kk]))
            quarters[q].append(buckets[k].pop())
            progress = True
    # остатки — в четверти с наименьшим числом (чтобы не потерять контент)
    rest = [it for k in buckets for it in buckets[k]]
    random.shuffle(rest)
    for it in rest:
        q = min(range(1, nq + 1), key=lambda x: (len(quarters[x]) >= TARGET_PER_QUARTER, len(quarters[x])))
        quarters[q].append(it)
    # если четверть тонкая — дополняем копиями из других четвертей этого же класса/предмета
    total_pool = len(pool)
    if total_pool >= PAD_MIN:
        for q in range(1, nq + 1):
            if len(quarters[q]) >= PAD_MIN:
                continue
            have = {id(x) for x in quarters[q]}
            donors = [it for qq in range(1, nq + 1) if qq != q for it in quarters[qq]]
            random.shuffle(donors)
            seen_text = {(it.text, str(it.answer)) for it in quarters[q]}
            for it in donors:
                if len(quarters[q]) >= PAD_MIN:
                    break
                key = (it.text, str(it.answer))
                if key in seen_text:
                    continue
                seen_text.add(key)
                quarters[q].append(it)
    return quarters


def item_json(it, qid):
    d = {"t": it.text, "ty": it.typ, "c": it.answer, "e": it.exp or "", "tp": it.topic or "", "q": qid}
    if it.options:
        d["o"] = it.options
    if it.unit:
        d["u"] = it.unit
    return d


def main():
    random.seed(20261005)
    bank = {}
    stats = []
    for grade in range(0, 12):
        bank[grade] = {}
        for subj in GRADE_SUBJECTS[grade]:
            pool = collect_pool(grade, subj)
            quarters = deal_by_quarters(pool, 4)
            subj_bank = {}
            counts = []
            for q in range(1, 5):
                items = quarters[q]
                random.shuffle(items)
                subj_bank[q] = [item_json(it, q) for it in items]
                counts.append(len(items))
            bank[grade][subj] = subj_bank
            stats.append((grade, subj, counts, sum(counts)))
    meta = {
        "version": "1.0.0",
        "company": "OuRi",
        "tagline": "Тренажёр школьных знаний",
        "grades": list(range(0, 12)),
        "subjects": {k: {"name": v[0], "short": v[1], "icon": v[2]} for k, v in SUBJECTS.items()},
        "gradeSubjects": {str(g): GRADE_SUBJECTS[g] for g in GRADE_SUBJECTS},
        "total": sum(s[3] for s in stats),
        "builtAt": "2026-10-05",
    }
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    counts, topics = {}, {}
    for g, subjs in bank.items():
        counts[str(g)] = {}
        topics[str(g)] = {}
        for s, qs in subjs.items():
            counts[str(g)][s] = [len(qs[q]) for q in range(1, 5)]
            seen, tl = set(), []
            for q in range(1, 5):
                for it in qs[q]:
                    t = it["tp"].split(" · ")[0]
                    if t and t not in seen:
                        seen.add(t); tl.append(t)
            topics[str(g)][s] = tl[:24]
    meta["counts"] = counts
    meta["topics"] = topics
    # полный банк одним файлом (данные для повторного использования)
    with open(os.path.join(out_dir, "bank.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"meta": meta, "bank": bank}, ensure_ascii=False, separators=(",", ":")))
    # индекс (лёгкий, грузится сразу)
    with open(os.path.join(out_dir, "bank-index.js"), "w", encoding="utf-8") as f:
        f.write("window.OURI_INDEX=" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";")
    # по классу (подгружаются по требованию)
    sizes = []
    for g in range(0, 12):
        p = os.path.join(out_dir, f"bank-{g}.js")
        with open(p, "w", encoding="utf-8") as f:
            f.write("(function(){window.OURI_BANKS=window.OURI_BANKS||{};window.OURI_BANKS[%d]=%s;})();" %
                    (g, json.dumps(bank[g], ensure_ascii=False, separators=(",", ":"))))
        sizes.append(os.path.getsize(p) // 1024)
    print(f"TOTAL questions: {meta['total']} | per-grade files (KB): {sizes}")
    worst = sorted(stats, key=lambda s: min(s[2]))[:14]
    print("\n--- минимум по четвертям (слабые места) ---")
    for g, s, c, t in worst:
        print(f"  {g} класс {SUBJECTS[s][0]:22} {c} = {t}")
    return meta


if __name__ == "__main__":
    main()
