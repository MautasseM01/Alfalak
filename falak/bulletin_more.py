# -*- coding: utf-8 -*-
"""
تتمّة النشرة اليومية — أقسامٌ كانت محسوبةً ولا تصل.

──────────────────────────────────────────────────────────────────
**ما كان ينقص، ولماذا**

النشرة كانت ستّة أقسام في ٢٠٨٧ حرفًا: القمرُ وبرجُه، والمنازل،
وزوايا القمر، وساعات الكواكب، والأخبار الصحّية. وهي **تدور على
القمر وحده تقريبًا**.

والناقص ليس محتاجًا إلى حسابٍ جديد — بل هو **محسوبٌ عندنا منذ
البداية في مواضع أخرى**:

  · مواضع الأجرام كلّها      → في `chart.py` و`/api/ephemeris`
  · زوايا الكواكب بعضها ببعض → في `chart.find_aspects`
  · دخول البروج والكسوفات     → في `mundane.month_events`
  · الطالع في لحظة بعينها     → في `chart.compute`

فما كان يرى الزائرُ إلّا القمر، وسائرُ السماء محجوب. وهذا هو
الدرس الذي تكرّر في النجوم والعبور والمنازل:
**لا يكفي أن يُحسَب الشيء، بل يجب أن يُوصَل إلى العين.**
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import aspects_deep as adeep
from . import chart, mundane

# الكواكب التي يُعتدّ بزواياها في نشرة اليوم — القمر له قسمه
SLOW = ["الشمس", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل",
        "أورانوس", "نبتون", "بلوتو"]


def sky_today(day, tzname: str, lat: float, lon: float) -> dict:
    """
    سماء اليوم كاملةً: مواضع الأجرام، ومن بدّل برجه، والزوايا بين
    الكواكب — لا زوايا القمر وحدها.
    """
    tz = ZoneInfo(tzname)
    noon = datetime(day.year, day.month, day.day, 12, 0, tzinfo=tz)
    prev = noon - timedelta(days=1)

    c = chart.compute(noon, lat, lon, "whole", tzname, minor_aspects=False)
    y = chart.compute(prev, lat, lon, "whole", tzname, minor_aspects=False)
    ysign = {b["name"]: b["sign"] for b in y["bodies"]}

    bodies, moved = [], []
    for b in c["bodies"]:
        if b["name"] in ("الذنب", "ليليث الحقيقية"):
            continue
        row = {"name": b["name"], "symbol": b["symbol"], "sign": b["sign"],
               "text": b["text"], "retro": b["retro"],
               "speed_word": ("راجع" if b["retro"] else "مستقيم")}
        bodies.append(row)
        was = ysign.get(b["name"])
        if was and was != b["sign"]:
            moved.append({"name": b["name"], "from": was, "to": b["sign"]})

    # ــ زوايا الكواكب بعضها ببعض ــ
    # القمر يُستثنى: له قسمه، وزواياه تتبدّل في ساعات فلا تصف اليوم.
    pairs = []
    for a in c["aspects"]:
        if "القمر" in (a["a"], a["b"]):
            continue
        if a["a"] not in SLOW or a["b"] not in SLOW:
            continue
        pairs.append({
            "a": a["a"], "b": a["b"], "name": a["name"], "symbol": a["symbol"],
            "polarity": a["polarity"], "orb": a["orb"],
            "applying": a["applying"], "exact": a.get("exact", False),
        })
        # النصّ يُطلَب هنا: `chart.compute` وحده لا يُلحقه — وهو
        # يُلحَق في مسار الخريطة فقط. فلو لم نطلبه لخرجت الزوايا
        # أرقامًا بلا معنى، وهو عين ما نُصلحه.
        t = adeep.pair_text(a["a"], a["b"], a["name"])
        pairs[-1]["meaning"] = (t or {}).get("text", "")
        pairs[-1]["theme"] = (t or {}).get("theme", "")

    # ــ الترتيب: **الأقرب إلى الإنسان أوّلًا** ــ
    # الأدقّ وجاجًا ليس أهمّ بالضرورة: أورانوس وبلوتو قد يتسدّسان
    # بفارق ٠٫١° وهما لا يتحرّكان في السنة إلّا قليلًا، فليس ذلك
    # خبرَ اليوم. والزاوية التي فيها كوكبٌ سريع هي التي تتبدّل
    # وتُحَسّ. فالسرعة أوّلًا، ثم الدقّة.
    FAST = {"الشمس", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"}
    pairs.sort(key=lambda x: (0 if (x["a"] in FAST or x["b"] in FAST) else 1,
                              x["orb"]))

    return {"bodies": bodies, "moved": moved, "pairs": pairs[:6],
            "asc_noon": c["angles"]["الطالع"]["text"],
            "sect": c["sect"]}


def coming(day, tzname: str, days: int = 21) -> list[dict]:
    """
    ما يقترب: دخول البروج والكسوفات وتحوّلات الرجوع في المدّة
    القادمة. تُجمَع من `mundane` — وهي تُعرَض في النشرة الشهرية
    ولا تصل إلى اليومية، مع أن من يقرأ اليوم يريد أن يعرف الغد.
    """
    tz = ZoneInfo(tzname)
    start = datetime(day.year, day.month, day.day, tzinfo=tz)
    end = start + timedelta(days=days)

    out = []
    seen = set()
    for y, m in {(start.year, start.month), (end.year, end.month)}:
        try:
            ev = mundane.month_events(y, m, tzname)["events"]
        except Exception:
            continue
        for e in ev:
            when = e.get("when")
            if isinstance(when, str):
                try:
                    when = datetime.fromisoformat(when)
                except ValueError:
                    continue
            if not isinstance(when, datetime) or not (start <= when <= end):
                continue
            key = (e.get("kind"), e.get("title"), when.isoformat())
            if key in seen:
                continue
            seen.add(key)
            out.append({"when": when.isoformat(timespec="minutes"),
                        "day": when.strftime("%d"),
                        "kind": e.get("kind", ""),
                        "title": e.get("title") or e.get("text", ""),
                        "text": e.get("text", "")})
    out.sort(key=lambda x: x["when"])
    return out[:10]


def render(sky: dict, soon: list[dict]) -> list[str]:
    """أسطر تُضاف إلى نصّ النشرة، بصيغتها نفسها."""
    lines = ["", "#سماء_اليوم"]

    if sky.get("moved"):
        for m in sky["moved"]:
            lines.append(f"- **{m['name']}** ينتقل من {m['from']} إلى "
                         f"{m['to']} اليوم.")
    lines.append("مواضع الأجرام ظهرًا:")
    for b in sky["bodies"]:
        r = " (راجع)" if b["retro"] else ""
        lines.append(f"- {b['name']}: {b['text']}{r}")
    # **لا نقول «الطالع» هنا**: طبقة التبسيط تُبدّله بـ«البرج الصاعد
    # لحظة الميلاد» — وهذا صحيحٌ في خريطة المولد، **خطأٌ في نشرة
    # اليوم**: هذا صاعدُ الظهيرة لا صاعدُ ميلاد أحد.
    lines.append(f"  البرج الصاعد على الأفق ظهرًا: {sky['asc_noon']}، "
                 f"وسماء اليوم {sky['sect']}.")

    if sky.get("pairs"):
        lines += ["", "#زوايا_الكواكب"]
        lines.append("  وهذه غير زوايا القمر: أبطأ منها وأطول مُكثًا، "
                     "فهي خبر الأسبوع لا خبر الساعة.")
        for p in sky["pairs"]:
            # **لا نُكرّر ما تُفسّره طبقة التبسيط**: كتبتُ أوّلًا
            # «مُقبِلة تشتدّ»، والطبقة تُبدّل «مُقبِلة» بـ«تشتدّ ولم
            # تتمّ بعد (مُقبِلة)» — فخرج «تشتدّ ولم تتمّ بعد
            # (مُقبِلة) تشتدّ». فالوصف هنا بغير المصطلح.
            state = "تامّة الآن" if p["exact"] else (
                "لم تتمّ بعد" if p["applying"] else "تمّت وتنفكّ")
            lines.append(f"- {p['a']} {p['symbol']} {p['b']} "
                         f"({p['name']}، {p['polarity']}، فرقُها "
                         f"{p['orb']:.1f}°، {state}).")
            if p.get("meaning"):
                lines.append(f"  {p['meaning']}")

    if soon:
        lines += ["", "#ما_يقترب"]
        for e in soon:
            lines.append(f"- يوم {e['day']}: {e['title']}")

    return lines


def coverage() -> dict:
    return {"أقسام مُضافة": 3, "أجرام تُعرَض": len(SLOW) + 1}
