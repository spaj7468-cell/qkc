#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборщик каталога «Хрестоматии».

  python3 gen/lit/build_lit.py          # собрать в ../../assets/lit/
  python3 gen/lit/build_lit.py --check  # только проверить данные, ничего не писать
  python3 gen/lit/build_lit.py --root DIR

Что делает
----------
1. Загружает russia/usa/china/japan.py + excluded.py.
2. Проверяет КАЖДУЮ строку через двойной заслон common.work_status / author_status.
   Ни одна строка не попадает в выдачу в обход проверки — обойти её в рантайме нельзя,
   потому что рантайм читает только результат сборки.
3. Пишет:
     assets/lit/index.json            — каталог: страны → авторы → произведения (без текстов)
     assets/lit/catalog.js            — window.OURI_LIT = {...} для ленивой подгрузки
     assets/lit/<страна>/<автор>.json — тексты всех произведений автора (phase 2)
4. Печатает отчёт: что прошло, что отклонено, что ждёт проверки переводов.

Правила отбора — в docstring common.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import common  # noqa: E402
from common import STATUS_OK, STATUS_NEEDS_TRANSLATION, STATUS_REJECTED  # noqa: E402
import russia, usa, china, japan, excluded  # noqa: E402

COUNTRIES = [russia, usa, china, japan]
SCHEMA_VERSION = 1


def die(msg):
    sys.stderr.write("build_lit: " + msg + "\n")
    sys.exit(1)


def validate(slug, authors):
    """Строгая проверка целостности данных страны. Возвращает список ошибок."""
    errs = []
    seen_a = set()
    seen_w = set()
    for a in authors:
        if not a["slug"] or not a["name"]:
            errs.append("%s: автор без slug/name" % slug)
            continue
        if a["slug"] in seen_a:
            errs.append("%s: дубль slug автора %r" % (slug, a["slug"]))
        seen_a.add(a["slug"])
        if common.author_status(a) != STATUS_OK:
            errs.append("%s/%s: автор не прошёл заслон по году смерти (%s), "
                        "его не должно быть в каталоге" % (slug, a["slug"], a["died"]))
        if not a["works"]:
            errs.append("%s/%s: у автора нет произведений" % (slug, a["slug"]))
        if not a["bio"].strip():
            errs.append("%s/%s: пустая биография" % (slug, a["slug"]))
        for w in a["works"]:
            key = (a["slug"], w["slug"])
            if key in seen_w:
                errs.append("%s: дубль slug произведения %s/%s" % (slug, a["slug"], w["slug"]))
            seen_w.add(key)
            st = common.work_status(w)
            if st == STATUS_REJECTED:
                errs.append("%s/%s/%s: произведение не прошло заслон (pub=%s, lang=%s) — "
                            "уберите его из каталога" % (slug, a["slug"], w["slug"], w["pub"], w["lang"]))
            if w["genre"] not in common.GENRES:
                errs.append("%s/%s/%s: жанр %r не в GENRES" % (slug, a["slug"], w["slug"], w["genre"]))
            if w["conf"] not in ("ok", "chk"):
                errs.append("%s/%s/%s: conf=%r" % (slug, a["slug"], w["slug"], w["conf"]))
            if w["lang"] != "ru" and not w["orig"]:
                errs.append("%s/%s/%s: не-русский оригинал без orig" % (slug, a["slug"], w["slug"]))
            if w["tr"] and not w["tr_died"]:
                errs.append("%s/%s/%s: указан переводчик без tr_died" % (slug, a["slug"], w["slug"]))
            # дубли названий внутри одного автора = почти всегда опечатка в slug
            titles = [x["title"] for x in a["works"]]
            if titles.count(w["title"]) > 1:
                errs.append("%s/%s: название %r встречается дважды" % (slug, a["slug"], w["title"]))
    return errs


def build(root, write=True):
    errors = []
    index = dict(schema=SCHEMA_VERSION, built=None, cutoff_death=common.PD_DEATH_CUTOFF,
                 cutoff_pub=common.PD_PUB_CUTOFF, countries=[], excluded=[], stats=dict())
    total_authors = total_works = total_ready = total_trans = 0
    text_files = []

    for mod in COUNTRIES:
        slug = mod.COUNTRY["slug"]
        errors.extend(validate(slug, mod.AUTHORS))
        cat = dict(slug=slug, name=mod.COUNTRY["name"], label=mod.COUNTRY["label"],
                   rule=mod.COUNTRY["rule"], authors=[])
        for a in sorted(mod.AUTHORS, key=lambda x: (x["born"] is None, x["born"] or 0)):
            works = []
            for w in sorted(a["works"], key=lambda x: x["pub"]):
                st = common.work_status(w)
                if st == STATUS_REJECTED:
                    continue
                works.append(dict(slug=w["slug"], title=w["title"], orig=w["orig"],
                                  genre=w["genre"], pub=w["pub"], pub_str=common.year_str(w["pub"]),
                                  lang=w["lang"], conf=w["conf"], status=st,
                                  tr=w["tr"], tr_died=w["tr_died"]))
                total_works += 1
                if st == STATUS_OK:
                    total_ready += 1
                else:
                    total_trans += 1
            cat["authors"].append(dict(
                slug=a["slug"], name=a["name"], orig=a["orig"], born=a["born"], died=a["died"],
                born_str=common.year_str(a["born"]), died_str=common.year_str(a["died"]),
                era=a["era"], bio=a["bio"], genres=a["genres"],
                works_count=len(works), works=works))
            total_authors += 1
            text_files.append((slug, a["slug"], [x["slug"] for x in works if x["status"] == STATUS_OK]))
        index["countries"].append(cat)

    for name, life, country, code, note in excluded.AUTHORS:
        if code not in excluded.REASONS:
            errors.append("excluded: неизвестный reason_code %r у %s" % (code, name))
            continue
        index["excluded"].append(dict(name=name, life=life, country=country,
                                      reason_code=code, reason=excluded.REASONS[code], note=note))

    if len(index["countries"]) > 50 or any(len(c["authors"]) > 50 for c in index["countries"]):
        errors.append("нарушен лимит: не больше 50 авторов на страну")

    index["stats"] = dict(countries=len(index["countries"]), authors=total_authors,
                          works=total_works, ready=total_ready,
                          needs_translation=total_trans, excluded=len(index["excluded"]))

    if errors:
        for e in errors:
            sys.stderr.write("  ✗ " + e + "\n")
        die("данные не прошли проверку: %d ошибок" % len(errors))

    if not write:
        return index, text_files

    out = os.path.join(root, "assets", "lit")
    index["built"] = os.environ.get("SOURCE_DATE_EPOCH") or None
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    with open(os.path.join(out, "catalog.js"), "w", encoding="utf-8") as f:
        f.write("/* собрано gen/lit/build_lit.py — не править руками */\n")
        f.write("window.OURI_LIT=")
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    # Один файл на автора: тексты всех его произведений. fetch_lit.py (phase 2)
    # заполнит поле text; существующие файлы не перетираются.
    written = 0
    for c, a, work_slugs in text_files:
        d = os.path.join(out, c)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, a + ".json")
        if os.path.exists(p):
            continue
        with open(p, "w", encoding="utf-8") as f:
            json.dump(dict(schema=SCHEMA_VERSION, country=c, author=a,
                           works=[dict(slug=ws, text=None, abridged=None,
                                       source=None, fetched=None) for ws in work_slugs],
                           status="placeholder"),
                      f, ensure_ascii=False, separators=(",", ":"))
        written += 1
    return index, written


def main():
    args = sys.argv[1:]
    check = "--check" in args
    root = HERE
    if "--root" in args:
        root = args[args.index("--root") + 1]
    elif not check:
        root = os.path.abspath(os.path.join(HERE, "..", ".."))

    if check:
        index, ph = build(root, write=False)
    else:
        index, written = build(root, write=True)
        print("создано файлов текстов (по одному на автора): %d" % written)

    s = index["stats"]
    print("─" * 62)
    print("Хрестоматия: стран %d, авторов %d, произведений %d" %
          (s["countries"], s["authors"], s["works"]))
    print("  готовы к публикации текста (ru, оба заслона):  %d" % s["ready"])
    print("  ждут проверки перевода:                        %d" % s["needs_translation"])
    print("  исключено (под охраной) — показано в разделе:  %d" % s["excluded"])
    for c in index["countries"]:
        n = len(c["authors"])
        print("    %-8s авторов %3d, произведений %4d" %
              (c["slug"], n, sum(a["works_count"] for a in c["authors"])))
        if n > 50:
            die("%s: %d авторов — больше лимита 50" % (c["slug"], n))
    chk = sum(1 for c in index["countries"] for a in c["authors"] for w in a["works"] if w["conf"] == "chk")
    print("  помечено conf=chk (сверить год до публикации текста): %d" % chk)
    print("─" * 62)
    print("OK: двойной заслон (died < %d И pub < %d) прошли все строки каталога."
          % (common.PD_DEATH_CUTOFF, common.PD_PUB_CUTOFF))


if __name__ == "__main__":
    main()
