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

# ══════════════════════════════════════════════════════════════════
# **الحدُّ بالمصدر لا بالطول** — وهذا تصحيحُ قاعدةٍ وضعتُها خطأً.
#
# كتبتُ أوّلًا `UI_MAX = 70`، وسمّيتُ ما طال «شرحًا يبقى عربيًّا».
# ثم رُئيت الصفحةُ الرئيسة إنجليزيّةً **وصدرُها عربيّ كامل** —
# وليس ذلك شرحًا فلكيًّا، بل **كلامُ الموقع عن نفسه**.
#
# فالفرقُ الصحيح ليس بين القصير والطويل، بل بين:
#   · **نصّ الصفحات** (HTML و JS) — يُترجَم كلُّه مهما طال
#   · **نصوص المحرّك** (`interpret`, `*_deep`) — تبقى عربية
#
# والحدُّ الباقي هنا واسعٌ جدًّا، ليس ليستثني بل ليطرح ما ليس
# عبارةً أصلًا: سطرَ شيفرةٍ أو تركيبًا آليًّا.
# ══════════════════════════════════════════════════════════════════
UI_MAX = 400


def _is_phrase(s: str) -> bool:
    """
    **حرفُ عطفٍ وحده ليس عبارة.**

    الوسومُ تُخرج أحيانًا نصًّا مثل «و» أو «؟» — وهي فواصلُ
    بين عنصرين لا كلامًا يُترجَم. وكانت تُعَدّ دَينًا، فيبقى
    المتبقّي واحدًا أبدًا في صفحتين مهما عُمل.
    """
    if sum(1 for c in s if c.isalpha()) < 2:
        return False
    # **ومثالُ الشيفرة ليس عبارة** — انظر `_literals`. والفحصُ
    # واحدٌ للوسوم وللجافاسكربت، فما استُثني في أحدهما استُثني
    # في الآخر: **معياران لشيءٍ واحد يُخرجان رقمين**.
    if "?" in s and "=" in s:
        return False
    if s.startswith(("curl ", "http")):
        return False
    # ــ **ومجموعةُ حروفٍ ليست كلمة** ــ
    # في `hint.js`: `'اأإآ'.includes(ch)` — وهي صور الألف تُسوّى
    # في المطابقة، و`'يى'` كذلك. حروفٌ عربيّة بلا مسافة **وبلا
    # حرفٍ مكرَّر**، فهي مجموعةٌ لا لفظ. وأمّا «نار» و«ماء»
    # فكلماتٌ، وحروفُها لا تنتمي إلى صورة حرفٍ واحد.
    ALEFS, YAAS = set("اأإآٱ"), set("يىئ")
    if " " not in s and len(s) <= 5 and (set(s) <= ALEFS or set(s) <= YAAS):
        return False
    return True


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
        # **والوسمُ يُنزَع، ولا يُطرَح النصُّ لأجله.**
        # كان كلُّ نصٍّ فيه `<` أو `>` يُطرَح — فطُرح معه شريطُ
        # التلميح، إذ يُبنى بـ`innerHTML`. **فلم يُعرَض للترجمة
        # قطّ**، وبقي عربيًّا في كلّ صفحة، وهو ٦٨ من ١٧١ باقية.
        # والقياسُ لا يراه، إذ هو يعدّ ما كُتب لا ما لم يُكتَب.
        if "<" in s or ">" in s:
            s = " ".join(re.sub(r"<[^>]*>", "", s).split())
            if not s or not AR.search(s):
                continue
        if any(c in s for c in "${}[]\\/|"):
            continue
        letters = sum(1 for c in s if c.isalpha())
        if letters < max(2, len(s) * 0.5):
            continue
        # ــ **مثالُ المسار شيفرةٌ لا عبارة** ــ
        # `bulletin?city=دمشق` فيه عربيّة، لكنه **يُرسَم داخل
        # `<pre>`** — و`i18n.js` يستثني `code` و`pre` عمدًا، إذ
        # ترجمةُ `?date=` تكسر المثال على من ينسخه.
        #
        # فعدُّه دَينًا **تضخيمٌ لرقمٍ لا سبيل إلى خفضه**:
        # يبقى المتبقّي تسعةً أبدًا مهما تُرجم. والرقمُ الذي لا
        # ينزل بعملٍ لا يُقاس به عمل.
        if not _is_phrase(s):
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
            if s and AR.search(s) and _is_phrase(s):
                found.add(s)
        for a in ("placeholder", "title", "aria-label"):
            for m in re.findall(a + r'="([^"]+)"', t):
                s = " ".join(m.split())
                if s and AR.search(s) and _is_phrase(s):
                    found.add(s)
        for s in found:
            seen[s] = seen.get(s, 0) + 1
    for s in shared:
        seen[s] = seen.get(s, 0) + 1
    return seen


def per_page() -> list[tuple[str, int, int]]:
    """
    **التغطية صفحةً صفحة** — وهذا ما يكشف المتروك.

    الرقمُ الكلّي يُخفي أيَّ صفحةٍ بعينها هي الناقصة: كان
    ٢٦٪ عامّةً، وفي النشرة اليومية ٦٣٪ وفي `api` ٣٠٪. **والزائر
    لا يزور «الموقع»، إنما يزور صفحة** — فتُقاس كما يراها.
    """
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        t = open(f, encoding="utf-8").read()
        t = re.sub(r"<!--[\s\S]*?-->", "", t)
        inline = "\n".join(re.findall(r"<script>([\s\S]*?)</script>", t))
        t2 = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", t)
        found = set(_literals(inline))
        for m in re.findall(r">([^<>]+)<", t2):
            s = " ".join(m.split())
            if s and AR.search(s) and _is_phrase(s):
                found.add(s)
        for a in ("placeholder", "title", "aria-label"):
            for m in re.findall(a + r'="([^"]+)"', t2):
                s = " ".join(m.split())
                if s and AR.search(s) and _is_phrase(s):
                    found.add(s)
        todo = found - set(i18n.UI)
        rows.append((os.path.basename(f), len(found), len(todo)))
    return sorted(rows, key=lambda r: -r[2])


def coverage() -> tuple[int, int, list[str]]:
    """
    (المُغطّى، الكلّ، الباقي) — **مصدرٌ واحد للرقم**.

    كان الاختبار يحسب النسبة بصيغته والأداةُ بصيغتها، فاختلفا:
    الأداة ١٠٠٪ والاختبار ٩٩٫٧. **وحاسبان لشيءٍ واحد يُخرجان
    رقمين، وأحدُهما يكذب حتمًا.** فليُحسب في موضعٍ واحد.
    """
    all_p = phrases()
    ui = {s: c for s, c in all_p.items() if len(s) <= UI_MAX}
    done = {s for s in ui if s in i18n.UI}
    keys = set(i18n.UI)
    # **والشظيّة تُعرَف بطولها، لا بكونها نصًّا فرعيًّا.**
    #
    # كتبتُ الشرط أوّلًا: «كلُّ ما هو جزءٌ من مفتاحٍ أطول شظيّة».
    # فعُفي عن **«يوم»** و**«سنة»** و**«دقيقة»** — لأنّها تقع داخل
    # عباراتٍ أطول في القاموس. وهي كلماتٌ قائمةٌ بذاتها في القوائم
    # المنسدلة، **فبقيت عربيّةً في صفحةٍ إنجليزية والأداةُ تقول
    # ١٠٠٪**. ولم يكشفها إلّا القياسُ من الصفحة.
    #
    # والشظيّةُ الحقيقية قطعةٌ من جملةٍ شُقّت في المصدر، وهي طويلة.
    # والكلمةُ القصيرة تُشبه الشظيّةَ بالمصادفة لا بالبنية.
    frag = {s for s in set(ui) - done
            if len(s) >= 20 and any(s in k for k in keys if len(k) > len(s))}
    todo = sorted(set(ui) - done - frag)
    return len(done) + len(frag), len(ui), todo


def report(show: bool = False) -> int:
    all_p = phrases()
    ui = {s: c for s, c in all_p.items() if len(s) <= UI_MAX}
    done = {s for s in ui if s in i18n.UI}
    # ══════════════════════════════════════════════════════════════
    # **وشظيّةُ عبارةٍ مترجَمة ليست دَينًا.**
    #
    # شريطُ التلميح يُبنى من نصّين متتاليين في `hint.js`، فيراهما
    # الاستخراجُ اثنين ويرى الصفحةُ واحدًا. **والمترجَم هو ما تراه
    # الصفحة** — وقد تُرجم كاملًا وطُوبق كاملًا (مقياسُ الصفحة صفر).
    #
    # فعدُّهما دَينًا **رقمٌ لا ينزل بعمل**: لو تُرجما لما تغيّر في
    # الصفحة حرف. ولا يُقاس بعملٍ رقمٌ لا يستجيب له.
    # ══════════════════════════════════════════════════════════════
    keys = set(i18n.UI)
    # **والشظيّة تُعرَف بطولها، لا بكونها نصًّا فرعيًّا.**
    #
    # كتبتُ الشرط أوّلًا: «كلُّ ما هو جزءٌ من مفتاحٍ أطول شظيّة».
    # فعُفي عن **«يوم»** و**«سنة»** و**«دقيقة»** — لأنّها تقع داخل
    # عباراتٍ أطول في القاموس. وهي كلماتٌ قائمةٌ بذاتها في القوائم
    # المنسدلة، **فبقيت عربيّةً في صفحةٍ إنجليزية والأداةُ تقول
    # ١٠٠٪**. ولم يكشفها إلّا القياسُ من الصفحة.
    #
    # والشظيّةُ الحقيقية قطعةٌ من جملةٍ شُقّت في المصدر، وهي طويلة.
    # والكلمةُ القصيرة تُشبه الشظيّةَ بالمصادفة لا بالبنية.
    frag = {s for s in set(ui) - done
            if len(s) >= 20 and any(s in k for k in keys if len(k) > len(s))}
    todo = sorted(set(ui) - done - frag, key=lambda s: (-ui[s], s))

    pct = round((len(done) + len(frag)) * 100 / max(len(ui), 1))
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
    if "--pages" in sys.argv:
        print(f"{'الصفحة':24}{'الكلّ':>6}{'باقٍ':>7}{'تغطية':>8}")
        for n, a, b in per_page():
            print(f"  {n:22}{a:>6}{b:>7}{round((a - b) * 100 / max(a, 1)):>7}٪")
        raise SystemExit(0)
    raise SystemExit(report("--list" in sys.argv))
