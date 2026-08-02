# -*- coding: utf-8 -*-
"""
أرباب الأزمنة — أيّ كوكب يحكم هذه السنة من عمرك.

خريطة الميلاد تقول ما أنت، ولا تقول متى. وأرباب الأزمنة هي جواب «متى»:
تقسيم العمر على الكواكب، فيتولّى كلٌّ منها فترة يصبغها بطبعه.

ثلاثة أبواب هنا، كلّها من صميم التراث الفارسي العربي:

  ١. الفردارات   دورة خمس وسبعين سنة، لكل كوكب فيها مدّة معلومة، وتنقسم
                 مدّته على سبعة فردارات صغرى. أصلها فارسي، ونقلها إلى
                 العربية أبو معشر البلخي وابن أبي الرجال.
  ٢. التسيير     ينتقل الطالع بيتًا كل سنة من العمر، فسيّد ذلك البيت هو
                 سيّد السنة. وهو أبسط تقنيات التوقيت وأقدمها.
  ٣. العودة الشمسية   لحظة عودة الشمس إلى موضعها الميلادي بالضبط،
                 وخريطة تلك اللحظة هي خريطة سنتك.

وغياب البابين الأولين عن المواقع العالمية هو فرصتنا الكبرى: Astrodienst
تبيع العودة الشمسية والتقدّمات، ولا تعرف الفردارات ولا التسيير.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import chart as ch
from . import dignities as dig
from .ephem import SIGNS, UTC, _bisect, _wrap180, lon_of, to_jd

# ══════════════════════════════════════════════════════════════════
# ١ — الفردارات
#
# الترتيب يبدأ من الشمس في الخريطة النهارية ومن القمر في الليلية، ثم
# يمضي على الترتيب المعروف. ومدّة كل كوكب بالسنوات:
# ══════════════════════════════════════════════════════════════════
FIRDARIA_YEARS = {
    "الشمس": 10, "الزهرة": 8, "عطارد": 13, "القمر": 9, "زحل": 11,
    "المشتري": 12, "المريخ": 7, "الرأس": 3, "الذنب": 2,
}

# ترتيب الدور النهاري: يبدأ بالشمس
DAY_ORDER = ["الشمس", "الزهرة", "عطارد", "القمر", "زحل",
             "المشتري", "المريخ", "الرأس", "الذنب"]
# ترتيب الدور الليلي: يبدأ بالقمر
NIGHT_ORDER = ["القمر", "زحل", "المشتري", "المريخ", "الشمس",
               "الزهرة", "عطارد", "الرأس", "الذنب"]

# العقدتان لا فردارات صغرى لهما عند الأكثرين
NO_SUB = {"الرأس", "الذنب"}

# ترتيب الفردارات الصغرى داخل مدّة الكوكب: يبدأ بالكوكب نفسه ثم يتوالى
SUB_ORDER = ["الشمس", "الزهرة", "عطارد", "القمر", "زحل", "المشتري", "المريخ"]

FIRDARIA_MEANING = {
    "الشمس": "سنوات ظهور ومرتبة وصلة بأصحاب الشأن. يُطلب فيها الاعتراف، "
             "ويُخشى فيها الكبرياء.",
    "القمر": "سنوات تقلّب وانتقال وشؤون بيت وعائلة. كثيرة الحركة قليلة الثبات.",
    "عطارد": "سنوات علم وكتابة وتجارة وأسفار قريبة. يُتعلَّم فيها ما يُنتفع به.",
    "الزهرة": "سنوات مودّة وزواج وجمال وفنّ. ألين سنوات العمر وأيسرها.",
    "المريخ": "سنوات جهد وخصومة وحركة شديدة. تُبنى فيها القوّة بالمواجهة.",
    "المشتري": "سنوات اتّساع وبركة وسفر وتعليم. أحمد الفردارات وأكثرها نفعًا.",
    "زحل": "سنوات حدّ ومسؤولية وصبر. ثقيلة، وما يُبنى فيها يدوم.",
    "الرأس": "سنوات زيادة ونموّ سريع، وميل إلى الإفراط.",
    "الذنب": "سنوات نقص وتخلٍّ وانكفاء، ومراجعة لما مضى.",
}


def firdaria(birth: datetime, is_day: bool, upto_age: int = 75) -> list[dict]:
    """
    جدول الفردارات من الولادة إلى سنّ معيّنة.
    كل فردار أكبر يحمل فردارات صغرى بداخله.
    """
    order = DAY_ORDER if is_day else NIGHT_ORDER
    out = []
    cursor = birth
    age = 0.0
    i = 0
    while age < upto_age:
        planet = order[i % len(order)]
        years = FIRDARIA_YEARS[planet]
        end = cursor + timedelta(days=years * 365.2425)

        subs = []
        if planet not in NO_SUB:
            # سبعة فردارات صغرى متساوية، تبدأ بالكوكب نفسه
            start_idx = SUB_ORDER.index(planet)
            each = (end - cursor) / 7
            for k in range(7):
                sp = SUB_ORDER[(start_idx + k) % 7]
                s0 = cursor + each * k
                s1 = cursor + each * (k + 1)
                subs.append({
                    "planet": sp,
                    "start": s0, "end": s1,
                    "age_from": round(age + (years / 7) * k, 2),
                    "age_to": round(age + (years / 7) * (k + 1), 2),
                    "meaning": FIRDARIA_MEANING.get(sp, ""),
                })

        out.append({
            "planet": planet, "years": years,
            "start": cursor, "end": end,
            "age_from": round(age, 2), "age_to": round(age + years, 2),
            "meaning": FIRDARIA_MEANING.get(planet, ""),
            "subs": subs,
        })
        cursor = end
        age += years
        i += 1
    return out


def firdaria_at(birth: datetime, is_day: bool, when: datetime) -> dict:
    """الفردار الأكبر والأصغر الجاريان في لحظة معيّنة."""
    table = firdaria(birth, is_day, upto_age=120)
    major = next((f for f in table if f["start"] <= when < f["end"]), None)
    if not major:
        return {"error": "الوقت خارج الجدول المحسوب."}
    minor = next((s for s in major["subs"] if s["start"] <= when < s["end"]), None)
    return {
        "major": {k: v for k, v in major.items() if k != "subs"},
        "minor": minor,
        "note": (f"أنت في فردار {major['planet']} الأكبر"
                 + (f"، وفردار {minor['planet']} الأصغر داخله." if minor else ".")
                 + " والفردار الأكبر يصبغ السنوات، والأصغر يفصّل داخلها."),
    }


# ══════════════════════════════════════════════════════════════════
# ٢ — التسيير السنوي (profection)
#
# ينتقل الطالع بيتًا كاملًا كل سنة: في السنة الأولى البيت الأول، وفي
# الثانية الثاني، وهكذا. فإذا بلغ الثاني عشر عاد إلى الأول. وسيّد البيت
# الذي بلغته سنتك هو **سيّد السنة**، ويُنظر في حاله في خريطة الميلاد.
# ══════════════════════════════════════════════════════════════════
def profection(birth: datetime, when: datetime, asc_lon: float) -> dict:
    age_years = (when - birth).days / 365.2425
    age = int(age_years)
    house = (age % 12) + 1

    asc_sign_idx = int(asc_lon // 30)
    sign = SIGNS[(asc_sign_idx + age) % 12]
    lord = dig.DOMICILE[sign]

    # التسيير الشهري: ينتقل بيتًا كل شهر داخل السنة
    frac = age_years - age
    month_index = int(frac * 12)
    month_house = ((house - 1 + month_index) % 12) + 1
    month_sign = SIGNS[(asc_sign_idx + age + month_index) % 12]

    return {
        "age": age,
        "house": house,
        "sign": sign,
        "lord": lord,
        "house_name": ch.HOUSE_NAMES[house - 1],
        "month_house": month_house,
        "month_sign": month_sign,
        "month_lord": dig.DOMICILE[month_sign],
        "month_house_name": ch.HOUSE_NAMES[month_house - 1],
        "note": (f"سنتك الـ{age + 1} تُسيَّر إلى البيت {house} "
                 f"({ch.HOUSE_NAMES[house-1].split(':')[1].strip()})، "
                 f"وبرجه {sign}، فسيّد سنتك {lord}. "
                 f"يُنظر في حال {lord} في خريطة ميلادك وفي عبوره هذه السنة، "
                 f"فهو المسؤول عن أحداثها."),
    }


def profection_years(birth: datetime, asc_lon: float,
                     from_age: int = 0, to_age: int = 90) -> list[dict]:
    """جدول التسيير لسنوات العمر."""
    asc_sign_idx = int(asc_lon // 30)
    out = []
    for age in range(from_age, to_age + 1):
        house = (age % 12) + 1
        sign = SIGNS[(asc_sign_idx + age) % 12]
        out.append({
            "age": age,
            "from": (birth + timedelta(days=age * 365.2425)).date().isoformat(),
            "house": house, "sign": sign,
            "lord": dig.DOMICILE[sign],
            "house_name": ch.HOUSE_NAMES[house - 1],
        })
    return out


# ══════════════════════════════════════════════════════════════════
# ٣ — العودة الشمسية
#
# الشمس تعود إلى درجة ميلادها مرّة كل سنة، وليس ذلك يوم ميلادك بالضبط
# بل قد يسبقه أو يتأخّر ساعات. وخريطة تلك اللحظة — مرسومة لموضعك الذي
# أنت فيه لا لموضع ميلادك — هي خريطة سنتك.
# ══════════════════════════════════════════════════════════════════
def solar_return_moment(natal_sun_lon: float, year: int,
                        around: datetime | None = None) -> datetime:
    """لحظة عودة الشمس إلى درجة ميلادها في سنة معيّنة."""
    guess = around or datetime(year, 1, 1, tzinfo=UTC)
    # نبحث في السنة كلّها عن عبور الشمس للدرجة
    start = datetime(year, 1, 1, tzinfo=UTC)
    f = lambda x: _wrap180(lon_of("الشمس", x) - natal_sun_lon)
    t = start
    step = timedelta(days=2)
    prev = f(t)
    while t < datetime(year + 1, 1, 5, tzinfo=UTC):
        t2 = t + step
        cur = f(t2)
        if prev * cur < 0 and abs(prev) < 20 and abs(cur) < 20:
            return _bisect(f, t, t2)
        prev, t = cur, t2
    raise ValueError("تعذّر إيجاد لحظة العودة الشمسية")


def solar_return(natal: dict, year: int, lat: float, lon: float,
                 tzname: str, house_system: str = "whole") -> dict:
    """خريطة السنة، مرسومة للموضع الذي يقيم فيه صاحبها."""
    sun_lon = next(b["lon"] for b in natal["bodies"] if b["name"] == "الشمس")
    moment = solar_return_moment(sun_lon, year)
    tz = ZoneInfo(tzname)
    local = moment.astimezone(tz)
    c = ch.compute(local, lat, lon, house_system, tzname, minor_aspects=False)

    # ما يميّز السنة: الطالع، وسيّد الطالع، والقمر، وأقوى الزوايا
    asc_sign = c["dominants"]["asc_sign"]
    asc_lord = c["dominants"]["asc_ruler"]
    lord_body = next((b for b in c["bodies"] if b["name"] == asc_lord), None)

    return {
        "year": year,
        "moment_utc": moment.isoformat(),
        "moment_local": local.isoformat(),
        "moment_text": local.strftime("%Y-%m-%d %H:%M"),
        "place": f"{lat}, {lon}",
        "tz": tzname,
        "chart": c,
        "asc_sign": asc_sign,
        "asc_lord": asc_lord,
        "asc_lord_house": lord_body["house"] if lord_body else None,
        "note": (f"طالع سنتك {c['angles']['الطالع']['text']}، وسيّده {asc_lord}"
                 + (f" في البيت {lord_body['house']} من خريطة السنة."
                    if lord_body else ".")
                 + " وخريطة السنة تُقرأ مع خريطة الميلاد لا وحدها: "
                   "هي تُبيّن لون السنة، والميلاد يُبيّن حدودها."),
    }


# ══════════════════════════════════════════════════════════════════
# التجميع
# ══════════════════════════════════════════════════════════════════
def timelords(natal: dict, when: datetime, lat: float, lon: float,
              tzname: str) -> dict:
    """أرباب الأزمنة كلّها للحظة معيّنة."""
    birth = datetime.fromisoformat(natal["when_utc"])
    if birth.tzinfo is None:
        birth = birth.replace(tzinfo=UTC)
    is_day = natal["sect"] == "نهارية"
    asc_lon = natal["angles"]["الطالع"]["lon"]

    when_utc = when.astimezone(UTC)
    f_now = firdaria_at(birth, is_day, when_utc)
    prof = profection(birth, when_utc, asc_lon)

    # سيّد السنة: حاله في خريطة الميلاد
    lord = prof["lord"]
    lord_natal = next((b for b in natal["bodies"] if b["name"] == lord), None)

    sr = None
    try:
        sr = solar_return(natal, when_utc.year, lat, lon, tzname)
    except Exception:
        sr = None

    return {
        "sect": natal["sect"],
        "firdaria": f_now,
        "firdaria_table": [
            {k: (v.isoformat() if isinstance(v, datetime) else v)
             for k, v in f.items() if k != "subs"}
            for f in firdaria(birth, is_day, 90)],
        "profection": prof,
        "year_lord_natal": ({
            "name": lord, "sign": lord_natal["sign"],
            "house": lord_natal["house"], "text": lord_natal["text"],
            "dignity": lord_natal.get("dignity"),
            "retro": lord_natal["retro"],
        } if lord_natal else None),
        "solar_return": ({
            "year": sr["year"], "moment_text": sr["moment_text"],
            "asc": sr["chart"]["angles"]["الطالع"]["text"],
            "asc_sign": sr["asc_sign"], "asc_lord": sr["asc_lord"],
            "asc_lord_house": sr["asc_lord_house"],
            "note": sr["note"],
            "bodies": [{"name": b["name"], "symbol": b["symbol"],
                        "text": b["text"], "house": b["house"],
                        "retro": b["retro"]}
                       for b in sr["chart"]["bodies"] if b["core"]],
            "aspects": sr["chart"]["aspects"][:8],
        } if sr else None),
    }


def render_text(t: dict) -> str:
    """نصّ جاهز للنسخ."""
    lines = ["#أرباب_الأزمنة"]
    f = t["firdaria"]
    if "error" not in f:
        lines.append(f["note"])
        lines.append(f"- الفردار الأكبر: {f['major']['planet']} "
                     f"({f['major']['age_from']:.0f}–{f['major']['age_to']:.0f} سنة). "
                     f"{f['major']['meaning']}")
        if f.get("minor"):
            m = f["minor"]
            lines.append(f"- الفردار الأصغر: {m['planet']} "
                         f"({m['age_from']:.1f}–{m['age_to']:.1f} سنة). {m['meaning']}")
    p = t["profection"]
    lines.append("")
    lines.append(p["note"])
    yl = t.get("year_lord_natal")
    if yl:
        lines.append(f"- سيّد السنة {yl['name']} في خريطة ميلادك: "
                     f"{yl['text']}، البيت {yl['house']}"
                     + (f"، {yl['dignity']}" if yl.get("dignity") else "")
                     + (" وهو راجع." if yl["retro"] else "."))
    sr = t.get("solar_return")
    if sr:
        lines.append("")
        lines.append(f"#العودة_الشمسية {sr['year']}")
        lines.append(f"تعود الشمس إلى درجة ميلادك في {sr['moment_text']}.")
        lines.append(sr["note"])
    return "\n".join(lines)
