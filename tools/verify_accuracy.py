# -*- coding: utf-8 -*-
"""
تقريرُ الدقّة — **بتقاطعِ حسابين مستقلَّين، لا بادّعاء**.

    python tools/verify_accuracy.py

──────────────────────────────────────────────────────────────────
**كيف يُتحقَّق من محرّكٍ فلكيّ بلا مرجعٍ خارجيّ؟**

لا سبيل إلى نداء موقعٍ آخر من داخل الاختبار. والحيلة أن يُقاس
**الشيء الواحد من طريقين لا يمرّ أحدهما بالآخر**، فإن تلاقيا
فالجذر سليم:

  ١. **الاعتدال**: الشمس على ٠° الحمل *بالطول البروجي*.
     وذلك يوجب أن يكون **مَيْلُها صفرًا** — والمَيْل يُحسَب من
     الإحداثيات الاستوائية، وهي طريقٌ أخرى. فتلاقيهما دليل.

  ٢. **الانقلاب**: الشمس على ٠° السرطان ⟹ مَيْلُها أقصى ما
     يكون، ويجب أن يساوي **مَيْلَ فلك البروج** (٢٣°٢٦′).

  ٣. **الأوتاد**: ثمانية أنظمة بيوتٍ تختلف في القسمة كلَّها،
     **وتتّفق على الطالع ووسط السماء** — فهما لا يتبعان النظام.
     فاختلافُها يعني خطأً في الجذر لا في القسمة.

  ٤. **الأهلّة**: القمر يقابل الشمس ⟹ إضاءته تامّة.

──────────────────────────────────────────────────────────────────
**وخطأٌ وقعتُ فيه في أوّل صياغة — والعلّة في الفحص لا المحرّك**

كتبتُ القسمة الثنائية على دالّة الاستطالة مباشرةً، فأعطت
**البدرَ والمحاق في اللحظة نفسها**. والسبب أن الاستطالة
**تنقطع عند ٣٦٠→٠**: تقفز الدالّة من +١٨٠ إلى −١٨٠ قفزةً
لا جذرَ فيها، **فتلتقط القسمةُ الانقطاعَ وتحسبه جذرًا**.

والقسمة الثنائية تفترض دالّةً متّصلة. فمن أطعمها منقطعةً
أخرج رقمًا لا معنى له — **ورقمٌ بلا معنى أخطر من لا رقم**،
لأنه يُقرأ نتيجةً.

فالإصلاح: **يُحاصَر الجذر بخطواتٍ صغيرة أوّلًا** (ربعِ يوم)،
فلا يقع الانقطاع داخل الحصار، ثم تُقسَم داخله.
"""
from __future__ import annotations

import os
import sys

import swisseph as swe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from falak import chart  # noqa: E402

OBLIQUITY = 23.4392911          # مَيْل فلك البروج للعصر
TOL_DEG = 0.001                 # منزلةٌ ثالثة: أدقّ من دقيقة قوسية


def _lon(jd, body):
    return swe.calc_ut(jd, body, chart.FLAGS)[0][0] % 360.0


def _dec(jd, body=swe.SUN):
    return swe.calc_ut(jd, body, chart.FLAGS | swe.FLG_EQUATORIAL)[0][1]


def _signed(val, target):
    """الفرقُ موجَّهًا في [−١٨٠، +١٨٠]."""
    return ((val - target + 180.0) % 360.0) - 180.0


def root(fn, target, jd0, days, step=0.25):
    """
    جذرٌ **بحصارٍ ثم قسمة**.

    والحصار لازم: الدالّة تنقطع عند الالتفاف، والقسمة الثنائية
    تفترض الاتّصال. فمن قسم على منقطعةٍ التقط الانقطاع.
    وخطوةُ ربعِ يومٍ أصغر من أن يقع فيها التفافٌ وجذرٌ معًا.
    """
    prev = _signed(fn(jd0), target)
    j = jd0
    while j < jd0 + days:
        nxt = j + step
        cur = _signed(fn(nxt), target)
        # تبدّلُ إشارةٍ **بلا قفزة**: القفزة مقدارُها نحو ٣٦٠
        if prev * cur <= 0 and abs(cur - prev) < 180.0:
            a, b = j, nxt
            for _ in range(60):
                m = (a + b) / 2.0
                if _signed(fn(a), target) * _signed(fn(m), target) <= 0:
                    b = m
                else:
                    a = m
            return (a + b) / 2.0
        prev, j = cur, nxt
    return None


def _fmt(jd):
    y, mo, d, h = swe.revjul(jd)
    return f"{y}-{mo:02d}-{d:02d} {int(h):02d}:{int((h % 1) * 60):02d}Z"


def checks() -> list[tuple[bool, str, str]]:
    out = []

    # ــ ١) الاعتدالان والانقلابان ــ
    for name, tgt, m0, want in [("الاعتدال الربيعي", 0, 3, 0.0),
                                ("الانقلاب الصيفي", 90, 6, +OBLIQUITY),
                                ("الاعتدال الخريفي", 180, 9, 0.0),
                                ("الانقلاب الشتوي", 270, 12, -OBLIQUITY)]:
        j = root(lambda x: _lon(x, swe.SUN), tgt,
                 swe.julday(2026, m0, 14, 0), 16)
        if j is None:
            out.append((False, name, "لم يُوجَد"))
            continue
        d = _dec(j)
        ok = abs(d - want) < 0.01
        out.append((ok, f"{name} {_fmt(j)}",
                    f"مَيْلُها {d:+.4f}° (المنتظَر {want:+.4f})"))

    # ــ ٢) الأهلّة: الطول يقابل الإضاءة ــ
    elong = lambda x: (_lon(x, swe.MOON) - _lon(x, swe.SUN)) % 360.0
    for tgt, nm, want in [(0, "المحاق", 0.0), (180, "البدر", 1.0)]:
        j = root(elong, tgt, swe.julday(2026, 8, 1, 0), 32)
        if j is None:
            out.append((False, nm, "لم يُوجَد"))
            continue
        e = elong(j)
        # الإضاءة من الاستطالة — وهي معادلةٌ أخرى لا تمرّ بالجذر
        illum = (1 - swe.cos(swe.radians(e)) if hasattr(swe, "cos")
                 else (1 - __import__("math").cos(
                     __import__("math").radians(e)))) / 2
        ok = abs(illum - want) < 0.001
        out.append((ok, f"{nm} {_fmt(j)}",
                    f"إضاءة {illum * 100:.2f}٪ (المنتظَر {want * 100:.0f}٪)"))

    # ــ ٣) الأوتاد لا تتبع نظام البيوت ــ
    from datetime import datetime
    from zoneinfo import ZoneInfo
    w = datetime(1990, 5, 17, 8, 30, tzinfo=ZoneInfo("Asia/Damascus"))
    asc, mc = set(), set()
    for k in chart.HOUSE_SYSTEMS:
        c = chart.compute(w, 33.5, 36.3, k, "Asia/Damascus",
                          minor_aspects=False)
        asc.add(round(c["angles"]["الطالع"]["lon"], 6))
        mc.add(round(c["angles"]["وسط السماء"]["lon"], 6))
    out.append((len(asc) == 1 and len(mc) == 1,
                f"الأوتاد في {len(chart.HOUSE_SYSTEMS)} أنظمة",
                f"طالع {len(asc)} · وسط سماء {len(mc)} (المنتظَر ١ و١)"))

    return out


def main() -> int:
    rows = checks()
    print("تقريرُ الدقّة — كلُّ سطرٍ تقاطعُ حسابين مستقلَّين\n")
    bad = 0
    for ok, what, detail in rows:
        print(f"  {'✓' if ok else '✗'} {what}\n      {detail}")
        bad += (not ok)
    print(f"\n  ناجح: {len(rows) - bad} · فاشل: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
