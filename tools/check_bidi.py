# -*- coding: utf-8 -*-
"""
فحصُ الاتّجاه — هل ينقلب التنسيق مع اللغة فعلًا؟

    python tools/check_bidi.py

──────────────────────────────────────────────────────────────────
**لماذا؟**

قلتُ عند بناء طبقة الترجمة إن التنسيق «مبنيٌّ على الخصائص
المنطقية فينقلب مع `dir`» — **وقلتُها ولم أقِسها**. ثم قِسْتُها
فكان الادّعاء صحيحًا في جملته (٩٣٪ منطقيّة) **وباطلًا في
موضعٍ يمسّ كل صفحة**:

    th, td { text-align: right }

فكلُّ خليّةٍ في كل جدولٍ في الموقع مصفوفةٌ إلى اليمين. وذلك
صحيحٌ بالعربية، **خطأٌ محضٌ بالإنجليزية**: جداولُ إنجليزية
مصفوفةٌ إلى اليمين في نصٍّ يجري إلى اليسار.

فهذه الأداة تمنع عودة ذلك: **لا خاصّيّة ماديّة إلّا بعذر**.

──────────────────────────────────────────────────────────────────
**والأعذار المقبولة**

  · `direction:ltr` مع `text-align:left` في الشيفرة والأرقام —
    فالشيفرة تجري إلى اليسار في كل لسان.
  · الماديّة المتبوعة بمنطقيّةٍ تنسخها — احتياطٌ لمتصفّحٍ قديم.
"""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ما يجب أن يكون منطقيًّا، وبديلُه
PHYSICAL = {
    r"\bmargin-left\s*:": "margin-inline-start",
    r"\bmargin-right\s*:": "margin-inline-end",
    r"\bpadding-left\s*:": "padding-inline-start",
    r"\bpadding-right\s*:": "padding-inline-end",
    r"\bborder-left(-\w+)?\s*:": "border-inline-start",
    r"\bborder-right(-\w+)?\s*:": "border-inline-end",
    r"(?<![-\w])left\s*:\s*(?!auto)": "inset-inline-start",
    r"(?<![-\w])right\s*:\s*(?!auto)": "inset-inline-end",
    r"text-align\s*:\s*left": "text-align:start",
    r"text-align\s*:\s*right": "text-align:end",
    r"float\s*:\s*left": "float:inline-end",
    r"float\s*:\s*right": "float:inline-start",
}

# قواعدُ يُعذَر فيها المادّيّ — الشيفرة تجري إلى اليسار دائمًا
EXEMPT = re.compile(r"direction\s*:\s*ltr")


def scan() -> list[tuple[str, int, str, str]]:
    bad = []
    files = (sorted(glob.glob(os.path.join(ROOT, "assets", "*.css")))
             + sorted(glob.glob(os.path.join(ROOT, "*.html"))))
    for f in files:
        raw = open(f, encoding="utf-8").read()
        if f.endswith(".html"):
            raw = "\n".join(re.findall(r"<style>([\s\S]*?)</style>", raw))
        css = re.sub(r"/\*[\s\S]*?\*/", "", raw)
        for pat, fix in PHYSICAL.items():
            for m in re.finditer(pat, css):
                # ــ القاعدة كلُّها تُنظَر، لا السطر ــ
                a = css.rfind("{", 0, m.start())
                b = css.find("}", m.start())
                rule = css[a:b] if a >= 0 and b > 0 else ""
                if EXEMPT.search(rule):
                    continue
                # ــ **ماديّةٌ تنسخها منطقيّةٌ بعدها: احتياطٌ مقصود** ــ
                #
                # وأوّل صياغةٍ لهذا الشرط كانت **تُبطِل الأداةَ
                # كلَّها**: كنتُ أبحث عن اسم الخاصّيّة في القاعدة —
                # `text-align\s*:` — والقاعدةُ تحوي `text-align:right`
                # نفسَه! فكان كل خطأٍ يُعفي نفسَه بنفسه، والأداة
                # تقول «✓ لا خطأ» وفيها الخطأ.
                #
                # اكتشفتُه بأن **أعدتُ الخطأ عمدًا فلم تصطده**.
                # والحارسُ الذي لا يُجرَّب على خطأٍ معلوم لا يُوثَق به.
                #
                # فالمفحوص الآن **القيمة المنطقيّة بعينها** لا اسم
                # الخاصّيّة.
                if re.search(re.escape(fix).replace(r"\:", r"\s*:\s*"), rule):
                    continue
                line = css[:m.start()].count("\n") + 1
                bad.append((os.path.basename(f), line, m.group(0).strip(), fix))
    return bad


def main() -> int:
    bad = scan()
    if not bad:
        print("✓ لا خاصّيّة ماديّة بلا عذر — التنسيق ينقلب مع اللغة.")
        return 0
    print(f"✗ خصائص ماديّة لا تنقلب مع `dir` ({len(bad)}):\n")
    for f, ln, got, fix in bad:
        print(f"  {f}:{ln}   «{got}»  →  {fix}")
    print("\nوالماديّة صحيحةٌ بالعربية وخطأٌ بالإنجليزية — "
          "والموقع سيُنشَر بثلاث لغات.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
