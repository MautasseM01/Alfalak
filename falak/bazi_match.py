# -*- coding: utf-8 -*-
"""
التوافق الصيني — بين خريطتَي أعمدة.

ولا يُقاس هنا بدرجة واحدة كما في التزاوج الغربي ولا بستّ وثلاثين
كما في الهندي، بل بثلاثة أنظار متمايزة:

١. **علاقات الفروع**: تآلف ثلاثيّ، ووفاق سداسيّ، وتصادم، وأذًى،
   وعقوبة. وهي أوضح ما في الباب وأسرعه ظهورًا.

٢. **العناصر**: أينقص أحدهما ما يفيض عند الآخر؟ وهذا **أهمّ من
   التآلف الظاهر**: من غلبت عليه النار وقرن نفسه بمن غلبه الماء
   وجد راحةً لا يجدها مع من يُشبهه.

٣. **سيّدا النفس**: ما نسبة كلٍّ إلى الآخر بالعلاقات العشر؟

**وأمّا حيوانا السنة** — الذي يعرفه الناس ويُبنى عليه كلام كثير —
فهو **ركن واحد من أربعة**. ومن ردّ إنسانًا لأن حيوانه يُصادم حيوانه
فقد حكم بربع الخريطة وترك ثلاثة أرباعها.
"""
from __future__ import annotations

from . import bazi as bz

# ══════════════════════════════════════════════════════════════
# علاقات الفروع الاثني عشر
# ══════════════════════════════════════════════════════════════
# التآلف الثلاثي (三合): ثلاثة فروع تُولّد عنصرًا واحدًا
TRINES = [
    (["زي", "تشِن", "شِن"], "ماء", "مثلّث الماء: تدبير وحكمة وبُعد نظر"),
    (["تشو", "سي", "يو"], "معدن", "مثلّث المعدن: انضباط ودقّة وإنجاز"),
    (["يِن", "وُو", "شو"], "نار", "مثلّث النار: حماسة وحركة وظهور"),
    (["ماو", "وَي", "هاي"], "خشب", "مثلّث الخشب: نموّ ورقّة وتعاون"),
]
# الوفاق السداسي (六合): زوجان يتّحدان
HARMONIES = [("زي", "تشو"), ("يِن", "هاي"), ("ماو", "شو"),
             ("تشِن", "يو"), ("سي", "شِن"), ("وُو", "وَي")]
# التصادم (六冲): متقابلان على الدائرة
CLASHES = [("زي", "وُو"), ("تشو", "وَي"), ("يِن", "شِن"),
           ("ماو", "يو"), ("تشِن", "شو"), ("سي", "هاي")]
# الأذى (六害): خفيّ لا يظهر مثل التصادم
HARMS = [("زي", "وَي"), ("تشو", "وُو"), ("يِن", "سي"),
         ("ماو", "تشِن"), ("شِن", "هاي"), ("يو", "شو")]

_TRINE = {}
for group, el, note in TRINES:
    for b in group:
        _TRINE[b] = (group, el, note)
_HARM = {frozenset(p) for p in HARMONIES}
_CLASH = {frozenset(p) for p in CLASHES}
_HURT = {frozenset(p) for p in HARMS}


def branch_relation(a: str, b: str) -> dict:
    """العلاقة بين فرعين: أقواها التآلف وأشدّها التصادم."""
    pair = frozenset({a, b})
    if a == b:
        return {"kind": "تطابق", "weight": 2,
                "note": ("الفرع نفسه: تشابه في الطبع والإيقاع. "
                         "راحة، وقلّة ما يُضيف كلٌّ إلى الآخر.")}
    if pair in _HARM:
        return {"kind": "وفاق سداسي", "weight": 3,
                "note": ("من أقوى الوفاق: يُكمّل كلٌّ الآخر مباشرة، "
                         "ويسهل بينهما ما يشقّ على غيرهما.")}
    if a in _TRINE and b in _TRINE[a][0]:
        _g, el, note = _TRINE[a]
        return {"kind": "تآلف ثلاثي", "weight": 3, "element": el,
                "note": f"{note}. يجتمعان على غاية واحدة."}
    if pair in _CLASH:
        return {"kind": "تصادم", "weight": -3,
                "note": ("متقابلان على الدائرة: احتكاك ظاهر وسريع. "
                         "ولا يعني الفراق — يعني أن الاصطدام يقع "
                         "علانيةً لا خفاءً، وهذا أهون من المكتوم.")}
    if pair in _HURT:
        return {"kind": "أذًى خفيّ", "weight": -2,
                "note": ("لا يظهر كالتصادم، ويعمل من تحت: عتب "
                         "لا يُقال، وسوء فهم يتراكم.")}
    return {"kind": "محايد", "weight": 0,
            "note": "لا وفاق خاصّ ولا تصادم."}


# ══════════════════════════════════════════════════════════════
# الميزان
# ══════════════════════════════════════════════════════════════
PILLAR_WEIGHT = {"السنة": 1.0, "الشهر": 1.5, "اليوم": 2.5, "الساعة": 1.0}
# عمود اليوم أثقل لأنه عمود الشريك عندهم: فيه سيّد النفس وفرع الزوج.


def _element_need(chart: dict) -> tuple[str, str]:
    """ما يفيض عند صاحب الخريطة، وما ينقصه."""
    return chart["strongest"], chart["weakest"]


def compare(a: dict, b: dict, name_a: str = "الأوّل",
            name_b: str = "الثاني") -> dict:
    """التوافق بين خريطتَي بازي."""
    rows, score, cap = [], 0.0, 0.0
    for pa, pb in zip(a["pillars"], b["pillars"]):
        r = branch_relation(pa["branch"]["name"], pb["branch"]["name"])
        w = PILLAR_WEIGHT[pa["key"]]
        score += r["weight"] * w
        cap += 3 * w
        rows.append({
            "pillar": pa["key"],
            "a": {"branch": pa["branch"]["name"],
                  "animal": pa["branch"]["animal"]},
            "b": {"branch": pb["branch"]["name"],
                  "animal": pb["branch"]["animal"]},
            "relation": r, "weight": w,
        })

    # ── تكامل العناصر: أنفع ما في هذا الباب ──
    a_strong, a_weak = _element_need(a)
    b_strong, b_weak = _element_need(b)
    fills = []
    if b_strong == a_weak:
        fills.append(f"{name_b} يفيض عنده {b_strong}، وهو ما ينقص "
                     f"{name_a} — فيُكمّله.")
        score += 3
    if a_strong == b_weak:
        fills.append(f"{name_a} يفيض عنده {a_strong}، وهو ما ينقص "
                     f"{name_b} — فيُكمّله.")
        score += 3
    cap += 6
    if a_strong == b_strong:
        fills.append(f"وكلاهما يغلب عليه {a_strong} — تشابه يُريح، "
                     "ولا يُكمّل نقصًا.")

    # ── سيّدا النفس ──
    dm_a = a["day_master"]["name"]
    dm_b = b["day_master"]["name"]
    g_ab = bz.ten_god(dm_a, dm_b)
    g_ba = bz.ten_god(dm_b, dm_a)
    from . import bazi_deep as bd
    masters = {
        "a_sees_b": {"name": g_ab.get("name"), "note": g_ab.get("note"),
                     "reading": bd.god_text(g_ab.get("name", ""))},
        "b_sees_a": {"name": g_ba.get("name"), "note": g_ba.get("note"),
                     "reading": bd.god_text(g_ba.get("name", ""))},
        "note": ("النسبة غير متبادلة: قد يكون هو «مالًا» لها وهي "
                 "«سلطة» له. وهذا من النظام لا خلل فيه — بل هو "
                 "أدقّ ما فيه، إذ يصف ما يفعله كلٌّ بالآخر لا "
                 "«ما بينهما»."),
    }

    pct = max(0, min(100, round(50 + 50 * score / (cap or 1))))
    band = ("قويّ" if pct >= 70 else "فوق المعتاد" if pct >= 55
            else "معتاد" if pct >= 45 else "يحتاج عملًا")

    year = rows[0]["relation"]
    return {
        "score": pct, "band": band,
        "raw": round(score, 1), "cap": round(cap, 1),
        "pillars": rows,
        "elements": {
            "a": {"strong": a_strong, "weak": a_weak},
            "b": {"strong": b_strong, "weak": b_weak},
            "fills": fills,
            "note": ("تكامل العناصر أهمّ عندهم من تآلف الحيوانات: "
                     "من غلبت عليه النار وقرن نفسه بمن غلبه الماء "
                     "وجد راحةً لا يجدها مع من يُشبهه."),
        },
        "day_masters": masters,
        "animals_note": (
            f"حيوانا سنتيكما {rows[0]['a']['animal']} و"
            f"{rows[0]['b']['animal']}، وبينهما {year['relation']['kind']}"
            if False else
            f"حيوانا سنتيكما {rows[0]['a']['animal']} و"
            f"{rows[0]['b']['animal']}، وبينهما «{year['kind']}». "
            "وهذا **ركن واحد من أربعة** — ومن ردّ إنسانًا لأن حيوانه "
            "يُصادم حيوانه فقد حكم بربع الخريطة وترك ثلاثة أرباعها."),
        "limits": ("والدرجة وصف لا حكم. أنجح ما يقع بين اثنين "
                   "يُصنَع بالمعاملة، وأضعفه يُهدَم بها."),
    }
