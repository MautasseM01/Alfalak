# -*- coding: utf-8 -*-
"""
البازي — الأركان الأربعة الصينية (四柱).

الخريطة هنا ليست دائرة ولا بروجًا، بل **أربعة أعمدة**: عمود للسنة
وعمود للشهر وعمود لليوم وعمود للساعة. ولكل عمود حرفان: **جذع** من
عشرة، و**فرع** من اثني عشر. فتُقرأ حياتك في ثمانية حروف — ومن هنا
اسمها «بازي» أي الحروف الثمانية.

**والدقيقة التي تُخطئ فيها أكثر المواقع العربية والغربية:**

سنة البازي **لا تبدأ برأس السنة القمرية الصينية**، بل بـ«قيام الربيع»
(لِيتْشُون 立春) — وهو اليوم الذي تبلغ فيه الشمس **٣١٥ درجة** من
المنطقة الاستوائية. وبين الموعدين أسبوعان أحيانًا. فمن وُلد في أواخر
يناير أو أوّل فبراير يُنسب في مواقع كثيرة إلى حيوان السنة الماضية،
وهو خطأ في مذهب البازي.

وكذلك **الشهر يبدأ بالفصل الشمسي لا بالقمر**: اثنا عشر فصلًا رئيسًا
(جِيه 節) كل ثلاثين درجة من مسير الشمس. ونحن نحسب طول الشمس أصلًا
ونجد أوقات بلوغها أيّ درجة بالتنصيف — فهذا في متناولنا، ولا نستورد
جداول.

**وأمّا العماد**: جذع اليوم هو «سيّد النفس» (日主)، وعليه تُبنى القراءة
كلّها. فما في الخريطة يُقاس إليه: ما يُعينه وما يُنهكه وما يحكمه.

المصادر: «滴天髓» (نُخبة أسرار السماء)، و«三命通會»، وعليهما عمل
أكثر من كتب في هذا الباب بعدهما.
"""
from __future__ import annotations

from datetime import date as _date, datetime, timedelta, timezone

from . import ephem

UTC = timezone.utc

# ══════════════════════════════════════════════════════════════
# ١ — الجذوع العشرة والفروع الاثنا عشر
# ══════════════════════════════════════════════════════════════
# (الاسم بالعربية · الصيني · العنصر · اليانغ أم الين)
STEMS = [
    ("جيا", "甲", "خشب", "يانغ"), ("يي", "乙", "خشب", "ين"),
    ("بينغ", "丙", "نار", "يانغ"), ("دينغ", "丁", "نار", "ين"),
    ("وو", "戊", "تراب", "يانغ"), ("جي", "己", "تراب", "ين"),
    ("غِنغ", "庚", "معدن", "يانغ"), ("شين", "辛", "معدن", "ين"),
    ("رِن", "壬", "ماء", "يانغ"), ("قوَي", "癸", "ماء", "ين"),
]
# (الاسم · الصيني · الحيوان · العنصر · اليانغ أم الين · الجذوع المخفيّة)
BRANCHES = [
    ("زي", "子", "الفأر", "ماء", "يانغ", ["قوَي"]),
    ("تشو", "丑", "الثور", "تراب", "ين", ["جي", "قوَي", "شين"]),
    ("يِن", "寅", "النمر", "خشب", "يانغ", ["جيا", "بينغ", "وو"]),
    ("ماو", "卯", "الأرنب", "خشب", "ين", ["يي"]),
    ("تشِن", "辰", "التنّين", "تراب", "يانغ", ["وو", "يي", "قوَي"]),
    ("سي", "巳", "الأفعى", "نار", "ين", ["بينغ", "غِنغ", "وو"]),
    ("وُو", "午", "الحصان", "نار", "يانغ", ["دينغ", "جي"]),
    ("وَي", "未", "الماعز", "تراب", "ين", ["جي", "دينغ", "يي"]),
    ("شِن", "申", "القرد", "معدن", "يانغ", ["غِنغ", "رِن", "وو"]),
    ("يو", "酉", "الديك", "معدن", "ين", ["شين"]),
    ("شو", "戌", "الكلب", "تراب", "يانغ", ["وو", "شين", "دينغ"]),
    ("هاي", "亥", "الخنزير", "ماء", "ين", ["رِن", "جيا"]),
]

ELEMENTS = ["خشب", "نار", "تراب", "معدن", "ماء"]
# دورة التوليد: الخشب يُولّد النار، والنار ترمادًا فترابًا، وهكذا
GENERATES = {"خشب": "نار", "نار": "تراب", "تراب": "معدن",
             "معدن": "ماء", "ماء": "خشب"}
# دورة القهر: الخشب يشقّ التراب، والتراب يسدّ الماء، وهكذا
CONTROLS = {"خشب": "تراب", "تراب": "ماء", "ماء": "نار",
            "نار": "معدن", "معدن": "خشب"}

ELEMENT_NOTE = {
    "خشب": "النموّ والامتداد والمبادرة — كالشجرة تطلب النور.",
    "نار": "الظهور والحرارة والحماسة — تُضيء وتستهلك.",
    "تراب": "الثبات والحفظ والوساطة — يجمع ما تفرّق.",
    "معدن": "الحدّ والتمييز والصرامة — يقطع ما زاد.",
    "ماء": "التكيّف والحكمة والعمق — يسلك حيث لا يسلك غيره.",
}

# ══════════════════════════════════════════════════════════════
# ٢ — الفصول الشمسية الاثنا عشر (جِيه)
#     كل فصل يبدأ حين تبلغ الشمس درجة بعينها
# ══════════════════════════════════════════════════════════════
# (درجة الشمس · الاسم الصيني · بالعربية · فرع الشهر)
JIEQI = [
    (315, "立春", "قيام الربيع", "يِن"),
    (345, "驚蟄", "استيقاظ الحشرات", "ماو"),
    (15,  "清明", "الصفاء والنور", "تشِن"),
    (45,  "立夏", "قيام الصيف", "سي"),
    (75,  "芒種", "السنابل", "وُو"),
    (105, "小暑", "الحرّ الأصغر", "وَي"),
    (135, "立秋", "قيام الخريف", "شِن"),
    (165, "白露", "الندى الأبيض", "يو"),
    (195, "寒露", "الندى البارد", "شو"),
    (225, "立冬", "قيام الشتاء", "هاي"),
    (255, "大雪", "الثلج الكبير", "زي"),
    (285, "小寒", "البرد الأصغر", "تشو"),
]

# الساعات المزدوجة الاثنتا عشرة: (الفرع، من، إلى) بالساعة المحلّية
# وأوّلها «زي» ويمتدّ من ٢٣:٠٠ إلى ٠١:٠٠ — أي يعبر منتصف الليل.
HOUR_BRANCHES = [
    ("زي", 23, 1), ("تشو", 1, 3), ("يِن", 3, 5), ("ماو", 5, 7),
    ("تشِن", 7, 9), ("سي", 9, 11), ("وُو", 11, 13), ("وَي", 13, 15),
    ("شِن", 15, 17), ("يو", 17, 19), ("شو", 19, 21), ("هاي", 21, 23),
]

_STEM_I = {s[0]: i for i, s in enumerate(STEMS)}
_BRANCH_I = {b[0]: i for i, b in enumerate(BRANCHES)}


def _sun_at(deg: float, around: datetime, span_days: int = 40) -> datetime:
    """لحظة بلوغ الشمس درجةً بعينها، قرب وقت معلوم."""
    lo = around - timedelta(days=span_days)
    hi = around + timedelta(days=span_days)
    f = lambda t: ((ephem.lon_of("الشمس", t) - deg + 180) % 360) - 180
    return ephem._bisect(f, lo, hi)


def solar_terms(year: int) -> list[dict]:
    """
    الفصول الاثنا عشر لسنة بازي واحدة: من قيام الربيع إلى ما قبله.

    وهذه هي **العظمة الفقرية للنظام كلّه**: عليها يُبنى حدّ السنة
    وحدّ الشهر معًا.
    """
    out = []
    for deg, cn, ar, branch in JIEQI:
        # تقدير أوّلي لموعد الفصل ثم تدقيقه بالتنصيف
        approx_month = {315: 2, 345: 3, 15: 4, 45: 5, 75: 6, 105: 7,
                        135: 8, 165: 9, 195: 10, 225: 11, 255: 12,
                        285: 1}[deg]
        yr = year + 1 if deg == 285 else year
        t = _sun_at(deg, datetime(yr, approx_month, 5, tzinfo=UTC), 25)
        out.append({"degree": deg, "chinese": cn, "name": ar,
                    "branch": branch, "when_utc": t})
    out.sort(key=lambda x: x["when_utc"])
    return out


def li_chun(year: int) -> datetime:
    """قيام الربيع: بداية سنة البازي. الشمس على ٣١٥ درجة."""
    return _sun_at(315.0, datetime(year, 2, 4, tzinfo=UTC), 25)


# ══════════════════════════════════════════════════════════════
# ٣ — التقويم الستّيني
#
# الجذوع عشرة والفروع اثنا عشر، فتتوافق كل ستّين. وتدور هذه الدورة
# على السنين والأشهر والأيام والساعات جميعًا بلا انقطاع منذ قرون.
#
# ونقطة الإسناد لليوم: **١ يناير ١٩٠٠ ميلادية كان يوم «جيا-شو»**
# (الجذع ٠، الفرع ١٠) — وهي نقطة يُتحقَّق منها بأيّ تقويم صينيّ.
# ══════════════════════════════════════════════════════════════
_EPOCH_DAY = _date(1900, 1, 1)
_EPOCH_STEM, _EPOCH_BRANCH = 0, 10          # جيا-شو


def day_pillar(d: _date) -> tuple[str, str]:
    """جذع اليوم وفرعه من التقويم الستّيني المتّصل."""
    n = (d - _EPOCH_DAY).days
    return (STEMS[(_EPOCH_STEM + n) % 10][0],
            BRANCHES[(_EPOCH_BRANCH + n) % 12][0])


def year_pillar(bazi_year: int) -> tuple[str, str]:
    """
    جذع السنة وفرعها. سنة ١٩٨٤ كانت «جيا-زي» — أوّل الدورة الستّينية،
    وهي نقطة إسناد مشهورة يعرفها كل من عمل في هذا الباب.
    """
    n = bazi_year - 1984
    return (STEMS[n % 10][0], BRANCHES[n % 12][0])


# جذع الشهر يُشتقّ من جذع السنة بقاعدة «الخمسة النمور» (五虎遁)
_MONTH_STEM_START = {"جيا": 2, "جي": 2, "يي": 4, "غِنغ": 4,
                     "بينغ": 6, "شين": 6, "دينغ": 8, "رِن": 8,
                     "وو": 0, "قوَي": 0}


def month_stem(year_stem: str, month_branch: str) -> str:
    """
    جذع الشهر: يبدأ شهر «يِن» (أوّل شهور السنة) بجذع يُحدّده جذع
    السنة، ثم يتسلسل. قاعدة «الخمسة النمور» المنصوصة.
    """
    start = _MONTH_STEM_START[year_stem]
    offset = (_BRANCH_I[month_branch] - _BRANCH_I["يِن"]) % 12
    return STEMS[(start + offset) % 10][0]


# جذع الساعة من جذع اليوم بقاعدة «الخمسة الفئران» (五鼠遁)
_HOUR_STEM_START = {"جيا": 0, "جي": 0, "يي": 2, "غِنغ": 2,
                    "بينغ": 4, "شين": 4, "دينغ": 6, "رِن": 6,
                    "وو": 8, "قوَي": 8}


def hour_stem(day_stem: str, hour_branch: str) -> str:
    start = _HOUR_STEM_START[day_stem]
    return STEMS[(start + _BRANCH_I[hour_branch]) % 10][0]


def hour_branch_of(local: datetime) -> tuple[str, bool]:
    """
    فرع الساعة، ومعه: أيقع الميلاد في ساعة «زي» الليلية بعد
    الحادية عشرة؟ فتلك تُحسَب لليوم **التالي** عند أكثرهم — وهي
    مزلّة أخرى.
    """
    h = local.hour
    if h >= 23:
        return "زي", True
    for name, lo, hi in HOUR_BRANCHES:
        if lo <= h < hi:
            return name, False
    return "زي", False


# ══════════════════════════════════════════════════════════════
# ٤ — العلاقات العشر: كل شيء يُقاس إلى سيّد النفس
# ══════════════════════════════════════════════════════════════
def ten_god(day_stem: str, other: str) -> dict:
    """
    نسبة جذع إلى سيّد النفس. عشر نِسَب تُبنى عليها القراءة كلّها:
    ما يُولّدني، وما أُولّده، وما أقهره، وما يقهرني، ومن هو مثلي —
    وكلٌّ منها وجهان بحسب اتّفاق اليانغ والين أو اختلافهما.
    """
    if day_stem not in _STEM_I or other not in _STEM_I:
        return {}
    me = STEMS[_STEM_I[day_stem]]
    it = STEMS[_STEM_I[other]]
    same_polarity = me[3] == it[3]

    if it[2] == me[2]:
        pair = ("أخ مُوازٍ", "أخ مُنافس")
        note = ("مثلك في العنصر: يُعينك ويُزاحمك معًا. "
                "أصدقاء وإخوة وشركاء.")
    elif GENERATES[it[2]] == me[2]:
        pair = ("سند غير مباشر", "أمّ وسند")
        note = "ما يُولّدك ويُغذّيك: التعلّم والرعاية والسند والشهادات."
    elif GENERATES[me[2]] == it[2]:
        pair = ("إخراج مُنطلِق", "إخراج مُتقَن")
        note = ("ما تُخرجه أنت: الكلام والإبداع والولد والصنعة. "
                "به تُنفق طاقتك وتُظهر ما فيك.")
    elif CONTROLS[me[2]] == it[2]:
        pair = ("مال غير ثابت", "مال ثابت")
        note = "ما تقهره وتملكه: المال والرزق، وعندهم الزوجة للرجل."
    else:
        pair = ("سلطة قاهرة", "سلطة منظِّمة")
        note = ("ما يقهرك ويحدّك: الرئيس والنظام والمسؤولية، "
                "وعندهم الزوج للمرأة.")

    return {"name": pair[0] if same_polarity else pair[1],
            "note": note, "element": it[2],
            "same_polarity": same_polarity}


# ══════════════════════════════════════════════════════════════
# ٥ — الخريطة
# ══════════════════════════════════════════════════════════════
def _branch_info(name: str) -> dict:
    b = BRANCHES[_BRANCH_I[name]]
    return {"name": b[0], "chinese": b[1], "animal": b[2],
            "element": b[3], "polarity": b[4], "hidden": b[5]}


def _stem_info(name: str) -> dict:
    s = STEMS[_STEM_I[name]]
    return {"name": s[0], "chinese": s[1], "element": s[2], "polarity": s[3]}


def compute(when_local: datetime, tzname: str = "") -> dict:
    """
    الأركان الأربعة. الوقت **محلّي** لا عالمي — فالساعة المزدوجة
    والحدود اليومية تُقاس بشمس مكانك.
    """
    if when_local.tzinfo is None:
        raise ValueError("الوقت يجب أن يحمل منطقته الزمنية")
    utc = when_local.astimezone(UTC)

    # ── ركن السنة: قيام الربيع هو الحدّ لا رأس السنة القمرية ──
    lc_this = li_chun(when_local.year)
    bazi_year = when_local.year if utc >= lc_this else when_local.year - 1
    before_li_chun = utc < lc_this
    ys, yb = year_pillar(bazi_year)

    # ── ركن الشهر: الفصل الشمسي الذي وقع فيه المولد ──
    terms = solar_terms(bazi_year)
    cur = terms[0]
    for t in terms:
        if utc >= t["when_utc"]:
            cur = t
        else:
            break
    mb = cur["branch"]
    ms = month_stem(ys, mb)

    # ── ركن اليوم: التقويم الستّيني، وساعة «زي» تُنقل إلى الغد ──
    hb, late_zi = hour_branch_of(when_local)
    day_date = when_local.date() + (timedelta(days=1) if late_zi
                                    else timedelta(0))
    ds, db = day_pillar(day_date)
    hs = hour_stem(ds, hb)

    pillars = [
        {"key": "السنة", "role": "الأصل والأجداد وأوّل العمر",
         "stem": _stem_info(ys), "branch": _branch_info(yb)},
        {"key": "الشهر", "role": "الأبوان والمهنة ومنتصف العمر",
         "stem": _stem_info(ms), "branch": _branch_info(mb)},
        {"key": "اليوم", "role": "أنت والشريك — وجذعه سيّد النفس",
         "stem": _stem_info(ds), "branch": _branch_info(db)},
        {"key": "الساعة", "role": "الولد وآخر العمر وما تُخلّفه",
         "stem": _stem_info(hs), "branch": _branch_info(hb)},
    ]

    # ── ميزان العناصر الخمسة ──
    tally = {e: 0.0 for e in ELEMENTS}
    for p in pillars:
        tally[p["stem"]["element"]] += 1.0
        tally[p["branch"]["element"]] += 1.0
        # الجذوع المخفيّة أخفّ وزنًا: الأوّل نصف، وما بعده ربع
        for i, h in enumerate(p["branch"]["hidden"]):
            tally[_stem_info(h)["element"]] += 0.5 if i == 0 else 0.25
    total = sum(tally.values()) or 1
    balance = {e: {"weight": round(v, 2),
                   "pct": round(100 * v / total, 1),
                   "note": ELEMENT_NOTE[e]}
               for e, v in tally.items()}
    ordered = sorted(balance.items(), key=lambda kv: -kv[1]["weight"])

    # ── العلاقات العشر لكل جذع ──
    gods = []
    for p in pillars:
        if p["key"] == "اليوم":
            gods.append({"pillar": p["key"], "stem": p["stem"]["name"],
                         "god": {"name": "سيّد النفس",
                                 "note": "أنت. وإليه يُقاس كل ما سواه.",
                                 "element": p["stem"]["element"]}})
        else:
            gods.append({"pillar": p["key"], "stem": p["stem"]["name"],
                         "god": ten_god(ds, p["stem"]["name"])})

    return {
        "when_local": when_local.isoformat(),
        "when_utc": utc.isoformat(),
        "tz": tzname or str(when_local.tzinfo),
        "bazi_year": bazi_year,
        "li_chun": {"when_utc": lc_this.isoformat(),
                    "before": before_li_chun,
                    "note": (
                        f"سنة البازي تبدأ بقيام الربيع، وهو في "
                        f"{lc_this.strftime('%Y-%m-%d %H:%M')} ت.ع. "
                        + ("ومولدك قبله، فأنت من سنة "
                           f"{bazi_year} لا {when_local.year} — "
                           "وهذا موضع يُخطئ فيه أكثر ما يُنشَر، إذ "
                           "يُحسَب بحيوان رأس السنة القمرية."
                           if before_li_chun else
                           "ومولدك بعده، فسنتك هي سنة ميلادك."))},
        "solar_term": {"name": cur["name"], "chinese": cur["chinese"],
                       "degree": cur["degree"],
                       "started": cur["when_utc"].isoformat(),
                       "note": ("الشهر عندهم يبدأ بالفصل الشمسي لا "
                                "بالقمر — أي حين تبلغ الشمس درجة بعينها.")},
        "late_zi": late_zi,
        "pillars": pillars,
        "day_master": {**_stem_info(ds),
                       "note": ("جذع اليوم هو «سيّد النفس»: أنت في هذه "
                                "الخريطة. وكل ما فيها يُقرأ بنسبته إليه.")},
        "animal": _branch_info(yb)["animal"],
        "elements": balance,
        "strongest": ordered[0][0],
        "weakest": ordered[-1][0],
        "missing": [e for e, v in balance.items() if v["weight"] == 0],
        "ten_gods": gods,
    }


# ══════════════════════════════════════════════════════════════
# ٦ — دورات الحظّ (大運)
#
# كل عشر سنين يحكم الحياةَ عمودٌ جديد. واتّجاه الدوران — إلى الأمام
# أو إلى الخلف — يختلف **بحسب جنس المولود وجذع سنته**: الذكر في
# سنة يانغ والأنثى في سنة ين يسيران إلى الأمام، وعكسهما إلى الخلف.
#
# وبداية أوّل دورة تُحسَب من **المسافة إلى الفصل التالي أو السابق**:
# كل ثلاثة أيام بيوم واحد تُعدّ سنةً.
# ══════════════════════════════════════════════════════════════
def luck_cycles(chart: dict, male: bool, count: int = 8) -> dict:
    when = datetime.fromisoformat(chart["when_utc"])
    ys = chart["pillars"][0]["stem"]
    forward = (ys["polarity"] == "يانغ") == male

    terms = solar_terms(chart["bazi_year"])
    times = sorted(t["when_utc"] for t in terms)
    if forward:
        nxt = next((t for t in times if t > when), times[-1] + timedelta(days=30))
        days = (nxt - when).total_seconds() / 86400
    else:
        prv = max([t for t in times if t <= when],
                  default=times[0] - timedelta(days=30))
        days = (when - prv).total_seconds() / 86400
    start_age = days / 3.0            # ثلاثة أيام بسنة

    mi = _BRANCH_I[chart["pillars"][1]["branch"]["name"]]
    msi = _STEM_I[chart["pillars"][1]["stem"]["name"]]
    step = 1 if forward else -1

    out = []
    for k in range(1, count + 1):
        s = STEMS[(msi + step * k) % 10][0]
        b = BRANCHES[(mi + step * k) % 12][0]
        age = start_age + (k - 1) * 10
        out.append({
            "from_age": round(age, 1), "to_age": round(age + 10, 1),
            "from_year": when.year + int(age),
            "to_year": when.year + int(age) + 10,
            "stem": _stem_info(s), "branch": _branch_info(b),
            "god": ten_god(chart["pillars"][2]["stem"]["name"], s),
        })
    return {
        "forward": forward,
        "start_age": round(start_age, 1),
        "direction_note": (
            f"{'ذكر' if male else 'أنثى'} وُلد في سنة "
            f"{ys['polarity']}، فدورات حظّه تسير "
            f"{'إلى الأمام' if forward else 'إلى الخلف'} — "
            "وهذه قاعدة منصوصة تختلف بالجنس، ولا نظير لها في "
            "الفلك العربي ولا الهندي."),
        "start_note": (
            f"تبدأ أوّل دورة عند سنّ {round(start_age, 1)}، وهي "
            "المسافة إلى الفصل الشمسي مقسومةً على ثلاثة: كل ثلاثة "
            "أيام بسنة."),
        "cycles": out,
    }
