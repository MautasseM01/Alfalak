# -*- coding: utf-8 -*-
"""
قياس التكرار عبر العائلات كلّها — لا كلّ عائلة على حدة.

    python tools/measure_duplication.py            # تقرير
    python tools/measure_duplication.py --charts 8 # على خرائط أكثر

──────────────────────────────────────────────────────────────────
**لماذا هذا الملفّ**

بنينا في الجولات الماضية ثلاثة حرّاس: واحدًا للأشكال، وواحدًا
للسهام، وواحدًا للنجوم. وكلٌّ منها يقيس عائلته وحدها — **فلا
أحد يرى الصورة كاملة**.

والزائر لا يقرأ عائلةً عائلة: يقرأ صفحةً واحدة. فإن تشابه نصُّ
شكلٍ ونصُّ سهم، أو نصُّ سهم وشرحُ المعجم له، **رآه هو ولم يرَه
أيٌّ من حرّاسنا**. وهذا بعينه ما وقع: «سهم الغيب» وشرحُ المعجم
له كانا متشابهين ٨٨٪، ولم يكن ثمّة حارس يفحص ما بين العائلتين.

──────────────────────────────────────────────────────────────────
**حدودٌ مختلفة، وكلٌّ له سببه**

لا حدَّ واحدًا يصلح للجميع، **والتسوية بينها تزوير**:

  · نصّان في عائلة واحدة   → ٨٨٪   قد يشتركان في البيت والبرج بحقّ
  · نصّان في عائلتين       → ٧٠٪   لا عذر لهما، فموضوعهما مختلف
  · نصٌّ وشرحُ المعجم له    → ٧٥٪   الشرح تعريف والنصّ قراءة،
                                    فإن تطابقا فأحدهما زائد

وهذه الحدود **تُقاس ولا تُفترَض**: كل واحد منها مضبوط على ما
قِيس فعلًا، بهامشٍ يسير — فإن ارتفع التشابه سقط الفحص.
"""
from __future__ import annotations

import argparse
import difflib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.index import dispatch
    from falak import interpret
except ModuleNotFoundError as exc:
    if exc.name in ("swisseph", "pyswisseph"):
        raise SystemExit(
            "ينقص pyswisseph.\n  pip install -r requirements-dev.txt"
        ) from None
    raise

CITIES = ["حلب", "القاهرة", "بغداد", "دمشق", "تونس", "عمّان", "الرباط"]

# الحدود — انظر صدر الملفّ
LIMIT_SAME = 0.88
LIMIT_CROSS = 0.70
LIMIT_GLOSS = 0.75


def blocks(chart: dict) -> list[tuple[str, str, str]]:
    """(العائلة، العنوان، النصّ) لكل ما يُعرَض للزائر."""
    out: list[tuple[str, str, str]] = []
    R = chart.get("reading") or {}

    def add(family, title, text):
        t = (text or "").strip()
        if len(t) >= 40:
            out.append((family, str(title), t))

    for x in R.get("core", []) + R.get("others", []):
        add("أجرام", x.get("title"), x.get("text"))
    for a in chart.get("aspects", []):
        if a.get("meaning"):
            add("زوايا", f"{a['a']}–{a['b']}", a["meaning"])
    for p in R.get("patterns", []):
        add("أشكال", p.get("title"), p.get("text"))
    for L in R.get("lots", []):
        add("سهام", L.get("title"), L.get("text"))
    for s in R.get("stars", []):
        add("نجوم", s.get("title"), s.get("text"))
    for h in (R.get("profiles", {}) or {}).get("houses", {}).values():
        add("بيوت", h.get("name"), h.get("rules"))
    return out


def measure(n_charts: int = 6, seed: int = 17) -> dict:
    rnd = random.Random(seed)
    gloss = [("معجم", k, v) for k, v in interpret.GLOSSARY.items()]
    worst = {"same": (0.0, None), "cross": (0.0, None), "gloss": (0.0, None)}
    pairs = 0

    for _ in range(n_charts):
        q = {"date": [f"{rnd.randint(1935, 2012)}-{rnd.randint(1, 12):02d}"
                      f"-{rnd.randint(1, 28):02d}"],
             "time": [f"{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}"],
             "city": [rnd.choice(CITIES)], "system": ["whole"]}
        page = blocks(dispatch("/api/chart", q))

        # داخل الصفحة: كل اثنين
        for i in range(len(page)):
            for j in range(i + 1, len(page)):
                f1, t1, x1 = page[i]
                f2, t2, x2 = page[j]
                r = difflib.SequenceMatcher(None, x1, x2).ratio()
                pairs += 1
                key = "same" if f1 == f2 else "cross"
                if r > worst[key][0]:
                    worst[key] = (r, f"{f1}: {t1[:26]}  ⟷  {f2}: {t2[:26]}")

        # وكلُّ نصٍّ مع شرح المعجم لمصطلحٍ يخصّه
        for f1, t1, x1 in page:
            for _, term, expl in gloss:
                if term not in t1 and term not in x1[:60]:
                    continue
                r = difflib.SequenceMatcher(None, x1, expl).ratio()
                pairs += 1
                if r > worst["gloss"][0]:
                    worst["gloss"] = (r, f"{f1}: {t1[:26]}  ⟷  معجم: {term}")

    return {"pairs": pairs, "worst": worst,
            "limits": {"same": LIMIT_SAME, "cross": LIMIT_CROSS,
                       "gloss": LIMIT_GLOSS}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", type=int, default=6)
    a = ap.parse_args()

    m = measure(a.charts)
    names = {"same": "داخل العائلة الواحدة", "cross": "بين عائلتين",
             "gloss": "نصٌّ وشرحُ المعجم له"}
    print(f"\nقيس {m['pairs']:,} زوجًا على {a.charts} خرائط\n" + "─" * 64)
    bad = 0
    for k in ("same", "cross", "gloss"):
        r, where = m["worst"][k]
        lim = m["limits"][k]
        ok = r <= lim
        bad += not ok
        print(f"  {'✓' if ok else '✗'} {names[k]:24} {r:5.0%}  (الحدّ {lim:.0%})")
        if where:
            print(f"      {where}")
    print("─" * 64)
    print("  لا تكرار فوق الحدّ." if not bad else f"  **{bad} تجاوزًا للحدّ.**")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
