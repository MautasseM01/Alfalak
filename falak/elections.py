# -*- coding: utf-8 -*-
"""
علم الاختيارات — متى يُبدأ الأمر ومتى يُتجنّب.

هذا الباب هو ثمرة الفلك العملية عند العرب: لا يكفي أن تعرف السماء، بل أن
تعرف متى تتحرّك تحتها. وأصله في «كتاب الاختيارات» لسهل بن بشر، و«غاية
الحكيم» للمجريطي، و«التفهيم» للبيروني، و«الباري» لابن أبي الرجال.

المعايير التي يقوم عليها الحكم، مرتّبة بحسب ثقلها عند القدماء:

  ١. المنزلة القمرية      لكل منزلة من الثمانٍ والعشرين طبع، وهو أوّل ما يُنظر
  ٢. خلو المسار           «لا تبدأ أمرًا والقمر خالي السير» — قاعدة لا تُخرَق
  ٣. زوايا القمر          مع السعدين (المشتري والزهرة) ومع النحسين (زحل والمريخ)
  ٤. برج القمر            مناسبته للغرض المطلوب
  ٥. زيادة القمر ونقصانه  المتزايد لما يُراد نموّه، والمتناقص لما يُراد نقصه
  ٦. كرامة القمر          قوّته في برجه
  ٧. حال دليل الأمر       الكوكب الحاكم للغرض: أراجع هو أم محترق؟
  ٨. حاكم اليوم           موافقته للغرض

والدرجة من مئة، لا تُقرأ وحدها بل مع أسبابها.
"""
from __future__ import annotations

from datetime import date as _date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import bulletin, config, dignities as dig, ephem, hours as _hours
from .ephem import SIGNS

SEADAN = ("المشتري", "الزهرة")      # السعدان
NAHSAN = ("زحل", "المريخ")          # النحسان

# ══════════════════════════════════════════════════════════════════
# الأغراض
#   ruler        الكوكب الدالّ على الأمر (يُنظر في حاله)
#   good_signs   بروج القمر المحمودة للغرض
#   bad_signs    بروج القمر المذمومة
#   waxing       True يُراد القمر متزايدًا · False متناقصًا · None لا يهمّ
#   moods        طبائع المنازل المحمودة
#   voc          هل خلو المسار مانع قاطع؟
#   organ_sign   برج العضو (للجراحة): يُتجنّب إن كان القمر فيه
# ══════════════════════════════════════════════════════════════════
PURPOSES = {
    # ── العقود والعمل ──
    "العقود والتوقيع": dict(
        ruler="عطارد", group="عمل",
        good_signs=["الثور", "الأسد", "العقرب", "الدلو", "الجدي"],
        bad_signs=["الجوزاء", "الحوت"], waxing=True, voc=True,
        note="يُراد له ثبات ودوام، فيُطلب القمر في برج ثابت متزايدًا، وخلو المسار مانع."),
    "بدء المشاريع": dict(
        ruler="المشتري", group="عمل",
        good_signs=["الحمل", "الأسد", "القوس", "الجدي"],
        bad_signs=["الحوت", "العقرب"], waxing=True, voc=True,
        note="البداية بذرة، فتُطلب في القمر المتزايد وفي برج منقلب أو ناري."),
    "طلب الحاجة والمقابلات": dict(
        ruler="المشتري", group="عمل",
        good_signs=["الأسد", "القوس", "الميزان", "السرطان"],
        bad_signs=["العقرب", "الجدي"], waxing=True, voc=True,
        note="يُطلب القمر متّصلًا بالسعدين، ويُتجنّب اتّصاله بالنحسين."),
    "التعلّم والامتحان": dict(
        ruler="عطارد", group="عمل",
        good_signs=["الجوزاء", "العذراء", "الدلو", "القوس"],
        bad_signs=["الحوت"], waxing=True, voc=False,
        note="دليله عطارد، فيُنظر أراجع هو أم مستقيم."),
    "الشراكة": dict(
        ruler="الزهرة", group="عمل",
        good_signs=["الميزان", "الثور", "الجوزاء"],
        bad_signs=["العقرب", "الحمل"], waxing=True, voc=True,
        note="مدارها على الميزان والزهرة."),

    # ── العلاقات ──
    "الزواج والخِطبة": dict(
        ruler="الزهرة", group="علاقات",
        good_signs=["الثور", "الميزان", "السرطان", "الحوت"],
        bad_signs=["العقرب", "الجدي", "الحمل"], waxing=True, voc=True,
        note="يُطلب القمر متزايدًا في برج الزهرة، وتُتجنّب المنازل النحسة قطعًا."),
    "الصلح والمصالحة": dict(
        ruler="الزهرة", group="علاقات",
        good_signs=["الميزان", "الحوت", "الثور", "السرطان"],
        bad_signs=["العقرب", "الحمل"], waxing=None, voc=True,
        note="يُتجنّب اتّصال القمر بالمريخ، فهو دليل الخصومة."),
    "اللقاء والمودّة": dict(
        ruler="الزهرة", group="علاقات",
        good_signs=["الميزان", "الثور", "الأسد", "الحوت"],
        bad_signs=["العقرب", "الجدي"], waxing=True, voc=False,
        note="خلو المسار ليس مانعًا قاطعًا هنا، لكنه يُضعف."),
    "إنهاء علاقة": dict(
        ruler="زحل", group="علاقات",
        good_signs=["العقرب", "الجدي", "الدلو"],
        bad_signs=["الميزان", "الثور"], waxing=False, voc=False,
        note="ما يُراد قطعه يُختار له القمر المتناقص، على عكس البدايات."),

    # ── الصحّة والبدن ──
    "الجراحة": dict(
        ruler="المريخ", group="صحّة",
        good_signs=[], bad_signs=["العقرب", "الحمل"], waxing=False, voc=True,
        organ_rule=True,
        note="قاعدة قاطعة: لا يُجرَح عضو والقمر في البرج الحاكم له. "
             "ويُختار القمر متناقصًا لقلّة النزف، وتُتجنّب زوايا المريخ."),
    "التجميل الجراحي": dict(
        ruler="الزهرة", group="صحّة",
        good_signs=["الثور", "الميزان"], bad_signs=["العقرب", "الحمل", "الجدي"],
        waxing=False, voc=True, organ_rule=True,
        note="يُشترط فيه ما يُشترط في الجراحة، ويُزاد اشتراط سلامة الزهرة."),
    "التجميل الخفيف": dict(
        ruler="الزهرة", group="صحّة",
        good_signs=["الثور", "الميزان", "الأسد"], bad_signs=["الجدي"],
        waxing=True, voc=False,
        note="ما لا يخترق الجلد: يُطلب له القمر متزايدًا في برج الزهرة."),
    "الأسنان": dict(
        ruler="زحل", group="صحّة",
        good_signs=[], bad_signs=["الجدي", "الحمل", "الثور"], waxing=False,
        voc=True, organ_rule=True,
        note="الأسنان والعظام لزحل، ويُتجنّب القمر في الجدي والحمل والثور."),
    "الدواء والعلاج": dict(
        ruler="القمر", group="صحّة",
        good_signs=["السرطان", "العقرب", "الحوت", "العذراء"],
        bad_signs=["الأسد", "الجدي"], waxing=False, voc=False,
        note="الاستفراغ والتنقية تُطلب في القمر المتناقص وفي البروج المائية."),

    # ── الشعر ──
    "قصّ الشعر للنموّ": dict(
        ruler="القمر", group="شعر",
        good_signs=["الأسد", "العذراء", "الثور", "السرطان"],
        bad_signs=["الجدي", "الدلو", "الحوت"], waxing=True, voc=False,
        note="القمر المتزايد ينمّي، والأسد والعذراء أحمد البروج لقوّة الشعر."),
    "قصّ الشعر لإبطاء النموّ": dict(
        ruler="القمر", group="شعر",
        good_signs=["الجدي", "العقرب"], bad_signs=["الأسد", "السرطان"],
        waxing=False, voc=False,
        note="عكس الأول: القمر المتناقص يُبطئ."),
    "إزالة الشعر": dict(
        ruler="القمر", group="شعر",
        good_signs=["الجدي", "العقرب", "الدلو"], bad_signs=["الأسد", "السرطان"],
        waxing=False, voc=False,
        note="ما يُراد له ألّا يعود يُطلب في القمر المتناقص."),
    "الصبغة والحنّاء": dict(
        ruler="الزهرة", group="شعر",
        good_signs=["الثور", "الميزان", "الأسد"],
        bad_signs=["الجدي", "الدلو", "العقرب"], waxing=True, voc=True,
        note="يُتجنّب القمر في بروج زحل، فهي تُفسد اللون."),

    # ── السفر ──
    "السفر البرّي": dict(
        ruler="عطارد", group="سفر",
        good_signs=["الجوزاء", "القوس", "الحمل", "الدلو"],
        bad_signs=["الثور", "العقرب"], waxing=True, voc=True,
        note="البروج المتغيّرة والنارية أحمد للحركة."),
    "السفر البحري": dict(
        ruler="القمر", group="سفر",
        good_signs=["السرطان", "الحوت", "الميزان"],
        bad_signs=["العقرب"], waxing=True, voc=True, water_care=True,
        note="يُتجنّب اتّصال القمر بالمريخ إن كان في برج مائي — "
             "فذلك من دلائل حوادث الماء عند القدماء."),
    "السفر الجوّي": dict(
        ruler="عطارد", group="سفر",
        good_signs=["الجوزاء", "الميزان", "الدلو", "القوس"],
        bad_signs=["العقرب", "الحوت"], waxing=True, voc=True,
        note="البروج الهوائية أحمد، ويُتجنّب اتّصال القمر بأورانوس والمريخ."),

    # ── المال ──
    "الشراء": dict(
        ruler="الزهرة", group="مال",
        good_signs=["الثور", "الميزان", "الجدي", "الأسد"],
        bad_signs=["الحوت", "العقرب"], waxing=True, voc=True,
        note="يُطلب القمر متزايدًا في برج ترابي، ويُتجنّب رجوع عطارد."),
    "البيع": dict(
        ruler="عطارد", group="مال",
        good_signs=["الجوزاء", "العذراء", "الميزان"],
        bad_signs=["الحوت"], waxing=False, voc=True,
        note="ما يُراد إخراجه من اليد يُطلب في القمر المتناقص."),
    "القرض والدَّين": dict(
        ruler="المشتري", group="مال",
        good_signs=["القوس", "الأسد"], bad_signs=["العقرب", "الجدي", "الحوت"],
        waxing=False, voc=True,
        note="القدماء يكرهون الاستدانة في القمر المتزايد، لئلّا يزيد الدَّين."),
    "الاستثمار": dict(
        ruler="المشتري", group="مال",
        good_signs=["الثور", "الجدي", "الأسد", "القوس"],
        bad_signs=["الحوت", "الجوزاء"], waxing=True, voc=True,
        note="يُشترط سلامة المشتري وعدم احتراقه."),

    # ── الأرض والبيت ──
    "الزرع والغرس": dict(
        ruler="القمر", group="أرض",
        good_signs=["السرطان", "العقرب", "الحوت", "الثور"],
        bad_signs=["الأسد", "الحمل", "الجوزاء"], waxing=True, voc=False,
        note="البروج المائية والخصبة، والقمر متزايدًا لما يُثمر فوق الأرض."),
    "البناء والترميم": dict(
        ruler="زحل", group="أرض",
        good_signs=["الثور", "الأسد", "العقرب", "الدلو", "الجدي"],
        bad_signs=["الحوت", "الجوزاء"], waxing=True, voc=True,
        note="يُطلب برج ثابت ليدوم البناء."),
    "الانتقال والسكن": dict(
        ruler="القمر", group="أرض",
        good_signs=["السرطان", "الثور", "الميزان"],
        bad_signs=["العقرب", "الجدي"], waxing=True, voc=True,
        note="القمر دليل الانتقال، ويُطلب متزايدًا في برج ليّن."),

    # ── الروح ──
    "كتابة النوايا والدعاء": dict(
        ruler="المشتري", group="روح",
        good_signs=["السرطان", "الحوت", "القوس", "الأسد"],
        bad_signs=[], waxing=None, voc=False, lunation_bonus=True,
        note="يُختار عند القمر الجديد للبدايات وعند البدر للحصاد، "
             "وفي ساعة المشتري أو الشمس."),
    "الاعتكاف والخلوة": dict(
        ruler="زحل", group="روح",
        good_signs=["الحوت", "العقرب", "الجدي"], bad_signs=["الأسد", "الحمل"],
        waxing=False, voc=False,
        note="خلو المسار هنا نافع لا ضارّ، فهو وقت انقطاع."),
}

GROUPS = ["عمل", "علاقات", "صحّة", "شعر", "سفر", "مال", "أرض", "روح"]

MOOD_SCORE = {"سعيدة جدًا": 18, "سعيدة": 12, "ممتزجة": 0, "نحسة": -16}

VERDICTS = [
    (85, "ممتاز", "من أحسن أيام الشهر لهذا الأمر"),
    (70, "جيّد", "يوم صالح، امضِ فيه"),
    (55, "مقبول", "لا بأس، مع شيء من الحذر"),
    (40, "ضعيف", "أجّله إن استطعت"),
    (0,  "يُتجنّب", "لا تبدأ فيه هذا الأمر"),
]


def _verdict(score: int):
    for th, name, note in VERDICTS:
        if score >= th:
            return name, note
    return VERDICTS[-1][1], VERDICTS[-1][2]


# الأغراض التي يُعدّ الكسوف والخسوف مانعًا فيها (كل ما فيه ابتداء أو التزام)
ECLIPSE_SENSITIVE = {"عمل", "علاقات", "صحّة", "سفر", "مال", "أرض"}


def eclipses_on(day: _date, tzname: str) -> list[dict]:
    """كسوف أو خسوف يقع في هذا اليوم المحلّي."""
    from . import mundane
    tz = ZoneInfo(tzname)
    d0 = datetime(day.year, day.month, day.day, tzinfo=tz)
    d1 = d0 + timedelta(days=1)
    try:
        evs = mundane.eclipses(d0.astimezone(ephem.UTC), d1.astimezone(ephem.UTC))
    except Exception:
        return []
    return [e.to_dict(tz) for e in evs]


def score_day(day: _date, tzname: str, lat: float, lon: float,
              purpose: str, data: dict | None = None,
              eclipses: list | None = None) -> dict:
    """يُقيّم يومًا واحدًا لغرض واحد، ويشرح كل نقطة."""
    p = PURPOSES.get(purpose)
    if not p:
        return {"error": f"غرض غير معروف: {purpose}"}

    d = data or bulletin.gather(day, tzname, lat, lon)
    tz = ZoneInfo(tzname)
    d0 = datetime(day.year, day.month, day.day, tzinfo=tz)
    d1 = d0 + timedelta(days=1)

    score = 50
    plus, minus = [], []

    # ١ — المنزلة القمرية (تُؤخذ أطول منزلة في اليوم)
    mn = max(d["mansions"], key=lambda m: (min(m["end"], d1) - max(m["start"], d0)))
    s = MOOD_SCORE.get(mn["mood"], 0)
    score += s
    (plus if s > 0 else minus if s < 0 else plus).append(
        f"القمر في منزلة {mn['name']} وهي {mn['mood']}" + (f" ({s:+d})" if s else ""))

    # ٢ — خلو المسار
    voc_hours = sum((min(v["end"], d1) - max(v["start"], d0)).total_seconds() / 3600
                    for v in d["voc"])
    if voc_hours > 0:
        frac = min(1.0, voc_hours / 24)
        pen = int(-(28 if p.get("voc") else 12) * frac)
        score += pen
        minus.append(f"خلو مسار {voc_hours:.1f} ساعة من اليوم ({pen:+d})"
                     + ("، وهو مانع في هذا الباب" if p.get("voc") else ""))
    elif p.get("voc"):
        score += 6
        plus.append("لا خلو مسار في هذا اليوم (+6)")

    # ٣ — زوايا القمر مع السعدين والنحسين
    good_asp = [a for a in d["aspects"]
                if a["planet"] in SEADAN and a["name"] in ("تثليث", "تسديس", "اقتران")]
    bad_asp = [a for a in d["aspects"]
               if a["planet"] in NAHSAN and a["name"] in ("تربيع", "تقابل", "اقتران")]
    if good_asp:
        s = min(16, 8 * len(good_asp))
        score += s
        plus.append("اتّصال القمر بالسعدين: "
                    + "، ".join(f"{a['name']} مع {a['planet']}" for a in good_asp)
                    + f" ({s:+d})")
    if bad_asp:
        s = -min(20, 10 * len(bad_asp))
        score += s
        minus.append("اتّصال القمر بالنحسين: "
                     + "، ".join(f"{a['name']} مع {a['planet']}" for a in bad_asp)
                     + f" ({s:+d})")

    # ٤ — برج القمر
    sign = d["moon_sign_noon"]
    if sign in p.get("good_signs", []):
        score += 12
        plus.append(f"القمر في برج {sign}، وهو من أحمد البروج لهذا الأمر (+12)")
    elif sign in p.get("bad_signs", []):
        score += -16
        minus.append(f"القمر في برج {sign}، وهو مذموم لهذا الأمر (−16)")

    # ٥ — زيادة القمر ونقصانه
    waxing = d["phase"]["waxing"]
    want = p.get("waxing")
    if want is not None:
        if waxing == want:
            score += 10
            plus.append(f"القمر {'متزايد' if waxing else 'متناقص'}، وهو المطلوب (+10)")
        else:
            score += -12
            minus.append(f"القمر {'متزايد' if waxing else 'متناقص'}، "
                         f"والمطلوب عكسه (−12)")

    # ٦ — كرامة القمر
    is_day_chart = True
    e = dig.evaluate("القمر", ephem.lon_of("القمر", d0 + timedelta(hours=12)), is_day_chart)
    if e["dignities"]:
        score += 6
        plus.append(f"القمر {e['summary']} (+6)")
    elif e["debilities"]:
        score += -8
        minus.append(f"القمر {e['summary']} (−8)")

    # ٧ — حال دليل الأمر
    ruler = p.get("ruler")
    if ruler and ruler != "القمر":
        noon = d0 + timedelta(hours=12)
        if ephem.is_retrograde(ruler, noon):
            score += -8
            minus.append(f"{ruler} دليل هذا الأمر وهو راجع (−8)")
        sep = abs(((ephem.lon_of(ruler, noon) - ephem.lon_of("الشمس", noon) + 180) % 360) - 180)
        if sep <= 8:
            score += -8
            minus.append(f"{ruler} محترق تحت شعاع الشمس (−8)")
        elif sep <= 17:
            score += -3
            minus.append(f"{ruler} تحت الشعاع (−3)")

    # ٨ — حاكم اليوم
    day_ruler = _hours.DAY_RULER[d0.weekday()]
    if day_ruler == ruler:
        score += 6
        plus.append(f"حاكم اليوم {day_ruler} وهو دليل هذا الأمر (+6)")
    elif day_ruler in NAHSAN and p.get("group") in ("علاقات", "روح"):
        score += -4
        minus.append(f"حاكم اليوم {day_ruler} وهو نحس (−4)")

    # ٩ — قاعدة العضو في الجراحة
    if p.get("organ_rule"):
        organ = dig.SIGNS.index(sign)
        from .tables import SIGN_INFO
        score += -20
        minus.append(f"يُتجنّب في هذا اليوم كل تدخّل في "
                     f"{SIGN_INFO[sign]['عضو']} — القمر في {sign} (−20)")

    # ١٠ — الكسوف والخسوف: مانع عند القدماء لكل ابتداء
    ecl = eclipses_on(day, tzname) if eclipses is None else [
        e for e in eclipses if e["date"] == day.isoformat()]
    for e in ecl:
        kind = e["detail"]["eclipse"]
        if p.get("group") in ECLIPSE_SENSITIVE:
            score += -30
            minus.append(
                f"{e['title']} — والقدماء يمنعون ابتداء الأمور والعقود "
                f"والأسفار يوم الكسوف والخسوف، ويمتدّ حكمه أيامًا حوله (−30)")
        else:
            score += -10
            minus.append(f"{e['title']} — وقت مشحون، يُتحرّى فيه (−10)")

    # ١١ — التقميرات (للنوايا)
    if p.get("lunation_bonus"):
        el = d["phase"]["elongation"]
        if ecl:
            plus.append("النيّة يوم الكسوف تُكتب ولا يُشرَع فيها بعمل: "
                        "الكسوف يفتح بابًا يظهر أثره بعد أسابيع.")
        elif el < 12 or el > 348:
            score += 15
            plus.append("قمر جديد — أحمد أوقات النيّة للبدايات (+15)")
        elif 168 < el < 192:
            score += 12
            plus.append("بدر — أحمد أوقات النيّة للحصاد والشكر (+12)")

    # ١٢ — حوادث الماء
    if p.get("water_care") and sign in ("السرطان", "العقرب", "الحوت"):
        if any(a["planet"] == "المريخ" for a in d["aspects"]):
            score += -14
            minus.append("القمر في برج مائي متّصلًا بالمريخ — "
                         "من دلائل حوادث الماء عند القدماء (−14)")

    score = max(0, min(100, score))
    verdict, verdict_note = _verdict(score)

    # أفضل ساعات اليوم لهذا الغرض
    best = []
    try:
        want_planets = _hours.PURPOSE_HOURS.get(purpose) or [ruler] if ruler else []
        if want_planets:
            best = [{k: v for k, v in h.items() if k not in ("start", "end")}
                    for h in _hours.best_hours(d0, lat, lon, tzname, want_planets)]
    except Exception:
        best = []

    return {
        "date": day.isoformat(), "purpose": purpose, "group": p.get("group"),
        "score": score, "verdict": verdict, "verdict_note": verdict_note,
        "moon_sign": sign, "mansion": mn["name"], "mansion_mood": mn["mood"],
        "waxing": waxing, "voc_hours": round(voc_hours, 1),
        "plus": plus, "minus": minus,
        "rule": p.get("note", ""),
        "best_hours": best,
    }


def month_calendar(year: int, month: int, tzname: str, lat: float, lon: float,
                   purposes: list[str] | None = None) -> dict:
    """تقويم الشهر كاملًا: درجة كل يوم لكل غرض."""
    purposes = purposes or list(PURPOSES)
    unknown = [p for p in purposes if p not in PURPOSES]
    if unknown:
        return {"error": f"أغراض غير معروفة: {'، '.join(unknown)}"}

    nm = (month % 12) + 1
    ny = year + (1 if month == 12 else 0)
    days = (_date(ny, nm, 1) - _date(year, month, 1)).days

    # كسوف الشهر يُحسب مرّة واحدة لا لكل يوم
    from . import mundane
    tz = ZoneInfo(tzname)
    m0 = datetime(year, month, 1, tzinfo=tz)
    m1 = datetime(ny, nm, 1, tzinfo=tz)
    try:
        month_ecl = [e.to_dict(tz) for e in mundane.eclipses(
            m0.astimezone(ephem.UTC), m1.astimezone(ephem.UTC))]
    except Exception:
        month_ecl = []

    # زوايا القمر للشهر كلّه مرّة واحدة، بدل إعادة حسابها لكل يوم
    ephem.preload_aspects(m0.astimezone(ephem.UTC) - timedelta(days=3),
                          m1.astimezone(ephem.UTC) + timedelta(days=3))

    rows = []
    for i in range(days):
        day = _date(year, month, 1) + timedelta(days=i)
        data = bulletin.gather(day, tzname, lat, lon, preload=False)
        entry = {"date": day.isoformat(), "weekday": _hours.WEEKDAY_AR[day.weekday()],
                 "moon_sign": data["moon_sign_noon"],
                 "mansion": data["mansions"][0]["name"],
                 "waxing": data["phase"]["waxing"],
                 "eclipse": next((e["title"] for e in month_ecl
                                  if e["date"] == day.isoformat()), None),
                 "scores": {}}
        for p in purposes:
            r = score_day(day, tzname, lat, lon, p, data, eclipses=month_ecl)
            entry["scores"][p] = {"score": r["score"], "verdict": r["verdict"]}
        rows.append(entry)

    # أفضل الأيام وأسوأها لكل غرض
    ranking = {}
    for p in purposes:
        srt = sorted(rows, key=lambda r: -r["scores"][p]["score"])
        ranking[p] = {
            "best": [{"date": r["date"], "weekday": r["weekday"],
                      "score": r["scores"][p]["score"],
                      "verdict": r["scores"][p]["verdict"]} for r in srt[:5]],
            "worst": [{"date": r["date"], "weekday": r["weekday"],
                       "score": r["scores"][p]["score"],
                       "verdict": r["scores"][p]["verdict"]} for r in srt[-3:]],
            "note": PURPOSES[p].get("note", ""),
            "group": PURPOSES[p].get("group"),
        }

    return {"year": year, "month": month, "tz": tzname,
            "purposes": purposes, "groups": GROUPS,
            "days": rows, "ranking": ranking}
