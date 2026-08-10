# -*- coding: utf-8 -*-
"""
ما بقي من الترجمة — يُقاس من الصفحات لا من القاموس.

    python tools/i18n_todo.py          # الحصيلة والنسبة
    python tools/i18n_todo.py --list   # وقائمة ما لم يُترجَم

──────────────────────────────────────────────────────────────────
**لماذا هذه الأداة؟**

`i18n.coverage()` كانت تقول «تامّة: نعم» — وهي **تامّةٌ بالنسبة
إلى نفسها**: كل مفتاح فيها له إنجليزيّة وفرنسيّة. لكنّ السؤال
الحقيقيّ غيرُ هذا: **كم من نصوص الصفحات وصلَته الترجمة؟**

فقياسُ القاموس بنفسه يُطمئن على خراب. والقياس هنا من الصفحات:
تُستخرَج عباراتُها المرئية، ثم يُنظَر كم منها في القاموس.
"""
from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from falak import i18n  # noqa: E402

AR = re.compile(r"[؀-ۿ]")

# ما يُعَدّ «أثاثَ واجهة»: العبارة القصيرة. وما طال فهو شرحٌ
# وسياق — وقد قُرّر أن يبقى عربيًّا، فلا يُحسَب دَينًا.
UI_MAX = 70


def _literals(js: str) -> set:
    """
    نصوصٌ عربية داخل الجافاسكربت — **وهي تُرسَم كما يُكتَب**.

    أوّل قياسٍ لي عدّ الوسوم وحدها، فظهر اثنان وثلاثون مفتاحًا
    «يتيمًا» لا وجود لها في صفحة — **ولم تكن يتيمة**: رؤوسُ
    الجداول وأسماءُ الألسنة تُبنى هنا لا هناك. فقياسٌ لا يرى
    ما يُرسَم يُطمئن على خراب.
    """
    js = re.sub(r"/\*[\s\S]*?\*/|//[^\n]*", "", js)
    out = set()
    for m in re.findall(r"'([^'\n]{2,70})'|\"([^\"\n]{2,70})\"", js):
        s = " ".join((m[0] or m[1]).split())
        if not s or not AR.search(s):
            continue
        # ــ ما ليس عبارةً يُطرَح ــ
        # **الأداة كانت تعدّ شظايا التعبيرات النمطية عبارات**:
        # `[اأإآ]` و`[وفبكل]?` و`plain أو expert`. فقياسُ الدَّيْن
        # يتضخّم بما ليس منه، والرقم المتضخّم لا يُوثَق به.
        if any(c in s for c in "${}<>[]\\/|"):
            continue
        letters = sum(1 for c in s if c.isalpha())
        if letters < max(2, len(s) * 0.5):
            continue
        out.add(s)
    return out


def phrases() -> dict:
    """العبارات المرئية في الصفحات، وفي كم صفحةٍ ظهرت."""
    seen: dict[str, int] = {}
    shared = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "assets", "*.js"))):
        shared |= _literals(open(f, encoding="utf-8").read())
    for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        t = open(f, encoding="utf-8").read()
        t = re.sub(r"<!--[\s\S]*?-->", "", t)
        inline = "\n".join(re.findall(r"<script>([\s\S]*?)</script>", t))
        t = re.sub(r"<script[\s\S]*?</script>", "", t)
        t = re.sub(r"<style[\s\S]*?</style>", "", t)
        found = set(_literals(inline))
        for m in re.findall(r">([^<>]+)<", t):
            s = " ".join(m.split())
            if s and AR.search(s):
                found.add(s)
        for a in ("placeholder", "title", "aria-label"):
            for m in re.findall(a + r'="([^"]+)"', t):
                s = " ".join(m.split())
                if s and AR.search(s):
                    found.add(s)
        for s in found:
            seen[s] = seen.get(s, 0) + 1
    for s in shared:
        seen[s] = seen.get(s, 0) + 1
    return seen


def report(show: bool = False) -> int:
    all_p = phrases()
    ui = {s: c for s, c in all_p.items() if len(s) <= UI_MAX}
    done = {s for s in ui if s in i18n.UI}
    todo = sorted(set(ui) - done, key=lambda s: (-ui[s], s))

    pct = round(len(done) * 100 / max(len(ui), 1))
    print(f"عباراتُ الواجهة في الصفحات : {len(ui)}")
    print(f"المُترجَم منها             : {len(done)}  ({pct}٪)")
    print(f"المتبقّي                   : {len(todo)}")
    print()
    print(f"وعباراتٌ طويلة (شرحٌ يبقى عربيًّا عمدًا): "
          f"{len(all_p) - len(ui)}")

    # مفاتيح في القاموس لا وجود لها في صفحة — دَيْنٌ ميّت
    # **ولا يُقال «ميّت» لما لم يُرَ**: الاستخراج ناقصٌ بطبعه —
    # ما كان داخل قالبٍ فيه وسوم لا يُلتقَط. فهذه للمراجعة لا
    # للحذف، وفرقُ ما بينهما أن الأولى تُنظَر والثانية تُمحى.
    orphan = [s for s in i18n.UI if s not in all_p]
    if orphan:
        print(f"\n**مفاتيح لم يلتقطها الاستخراج ({len(orphan)})** — "
              f"للمراجعة لا للحذف:")
        for s in orphan[:12]:
            print(f"   · {s}")

    if show and todo:
        print("\nــ ما لم يُترجَم، الأكثر شيوعًا أوّلًا ــ")
        for s in todo:
            print(f'    "{s}": ("", ""),   # ×{ui[s]}')
    elif todo:
        print(f"\nأضِف `--list` لطبع الـ{len(todo)} الباقية بصيغةٍ "
              f"تُلصَق في `falak/i18n.py`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(report("--list" in sys.argv))
