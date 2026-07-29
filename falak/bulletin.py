# -*- coding: utf-8 -*-
"""تركيب النشرة الفلكية بالعربية بصيغة المثال المعتمد."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import config, ephem, tables

WEEKDAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
WEEKDAYS_DEF = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
          "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


# ── صياغة الأوقات ────────────────────────────────────────────────
def day_name(dt: datetime) -> str:
    return WEEKDAYS[dt.weekday()]


def date_phrase(dt: datetime) -> str:
    return f"{day_name(dt)} {dt.day} {MONTHS[dt.month - 1]}"


def part_of_day(dt: datetime) -> str:
    h = dt.hour
    if h == 0:
        return "منتصف ليل"
    if h < 4:
        return "بعد منتصف ليل"
    if h < 6:
        return "فجر"
    if h < 12:
        return "صباح"
    if h < 13:
        return "ظهر"
    if h < 16:
        return "بعد ظهر"
    if h < 18:
        return "عصر"
    if h < 20:
        return "مساء"
    return "ليل"


_ADVERB = {
    "منتصف ليل": "منتصف ليل {d}",
    "بعد منتصف ليل": "بعد منتصف ليل {d}",
    "فجر": "فجرًا {d}",
    "صباح": "صباحًا {d}",
    "ظهر": "ظهرًا {d}",
    "بعد ظهر": "بعد الظهر {d}",
    "عصر": "عصرًا {d}",
    "مساء": "مساءً {d}",
    "ليل": "ليلًا {d}",
}


def clock(dt: datetime) -> str:
    """12:10 — بصيغة الاثنتي عشرة ساعة."""
    h = dt.hour % 12
    if h == 0:
        h = 12
    return f"{h}:{dt.minute:02d}"


def time_phrase(dt: datetime, ref_day: datetime | None = None) -> str:
    """«6:10 صباحًا الثلاثاء» أو «12:10 منتصف ليل الثلاثاء»."""
    d = day_name(dt)
    part = part_of_day(dt)
    adv = _ADVERB[part].format(d=d)
    return f"{clock(dt)} {adv}"


def moment_phrase(dt: datetime) -> str:
    """«فجر الأربعاء» — للإشارة إلى لحظة بلا رقم."""
    part = part_of_day(dt)
    d = day_name(dt)
    simple = {
        "منتصف ليل": f"منتصف ليل {d}",
        "بعد منتصف ليل": f"ساعات ما بعد منتصف ليل {d}",
        "فجر": f"فجر {d}",
        "صباح": f"صباح {d}",
        "ظهر": f"ظهر {d}",
        "بعد ظهر": f"بعد ظهر {d}",
        "عصر": f"عصر {d}",
        "مساء": f"مساء {d}",
        "ليل": f"ليل {d}",
    }
    return simple[part]


def dur_phrase(hours: float) -> str:
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    if h and m:
        return f"{h} ساعة و{m} دقيقة"
    if h:
        return f"{h} ساعة"
    return f"{m} دقيقة"


# ── جمع معطيات اليوم ─────────────────────────────────────────────
def gather(target_date, tzname: str, lat: float | None = None,
           lon: float | None = None) -> dict:
    tz = ZoneInfo(tzname)
    d0 = datetime(target_date.year, target_date.month, target_date.day, 0, 0, tzinfo=tz)
    d1 = d0 + timedelta(days=1)
    noon = d0 + timedelta(hours=12)

    # نحسب زوايا نافذة واسعة مرّة واحدة (تُستعمل لخلو المسار أيضًا)
    ephem.preload_aspects(d0 - timedelta(hours=48), d1 + timedelta(hours=48))

    data = {"tz": tzname, "date": d0, "day_name": day_name(d0),
            "date_phrase": date_phrase(d0)}

    # ١. برج القمر
    moon_lon = ephem.lon_of("القمر", noon)
    sign_now = ephem.SIGNS[ephem.sign_index(moon_lon)]
    ingresses = ephem.moon_ingresses(d0, d1)
    entry_t, _ = ephem.prev_moon_ingress(d0 + timedelta(minutes=1))
    exit_t, next_sign = ephem.next_moon_ingress(d1 - timedelta(minutes=1))
    if ingresses:
        # القمر يغيّر برجه خلال اليوم
        data["moon_sign_changes"] = [
            {"time": t, "sign": s} for t, s in ingresses
        ]
    else:
        data["moon_sign_changes"] = []
    data["moon_sign_start"] = ephem.SIGNS[ephem.sign_index(ephem.lon_of("القمر", d0))]
    data["moon_sign_noon"] = sign_now
    data["moon_sign_end"] = ephem.SIGNS[ephem.sign_index(ephem.lon_of("القمر", d1 - timedelta(minutes=1)))]
    data["moon_entered_at"] = entry_t.astimezone(tz)
    data["moon_leaves_at"] = exit_t.astimezone(tz)
    data["moon_next_sign"] = next_sign
    data["moon_lon"] = moon_lon

    # ٢. المنازل القمرية
    data["mansions"] = []
    for idx, a, b in ephem.mansions_in_window(d0, d1):
        name, mood, desc, good = tables.MANSIONS[idx - 1]
        data["mansions"].append({
            "index": idx, "name": name, "mood": mood,
            "mood_text": tables.MANSION_MOOD[mood],
            "desc": desc, "good_for": good,
            "start": a.astimezone(tz), "end": b.astimezone(tz),
        })

    # ٣. الزوايا
    data["aspects"] = []
    for a in [x for x in ephem._ASPECT_WINDOW if d0 <= x.time < d1]:
        txt = tables.MOON_ASPECTS.get(a.planet, {}).get(a.name, tables.ASPECT_BASE[a.name])
        data["aspects"].append({
            "time": a.time.astimezone(tz), "planet": a.planet,
            "name": a.name, "angle": a.angle,
            "polarity": tables.ASPECT_POLARITY[a.name],
            "text": txt,
        })

    # ٤. خلو المسار
    data["voc"] = []
    for v in ephem.void_of_course_periods(d0, d1):
        data["voc"].append({
            "start": v.start.astimezone(tz), "end": v.end.astimezone(tz),
            "hours": v.hours, "next_sign": v.next_sign,
            "long": v.hours >= config.VOC_LONG_HOURS,
            "last_aspect": (v.last_aspect.name + " مع " + v.last_aspect.planet)
                           if v.last_aspect else None,
        })

    # ٥. الطور والرجوع والشمس
    data["phase"] = ephem.moon_phase(noon)
    data["retrogrades"] = [p for p in config.ASPECT_PLANETS + (
        config.OUTER_PLANETS if config.INCLUDE_OUTER else [])
        if p != "الشمس" and ephem.is_retrograde(p, noon)]
    data["sun_sign"] = ephem.SIGNS[ephem.sign_index(ephem.lon_of("الشمس", noon))]

    # ٦. أوقات الشمس (تُثبّت معنى «الفجر» و«العصر» و«المغرب» في النصّ)
    data["sun_times"] = {}
    if lat is not None and lon is not None:
        for k, v in ephem.sun_events(d0, lat, lon, tz).items():
            if v:
                data["sun_times"][k] = v
    return data


# ── الأخبار الصحية ───────────────────────────────────────────────
def health_section(d: dict) -> list[str]:
    lines = []
    sign = d["moon_sign_noon"]
    organ = tables.SIGN_INFO[sign]["عضو"]
    waxing = d["phase"]["waxing"]

    # خلو المسار المهيمن
    voc_hours = sum(
        (min(v["end"], d["date"] + timedelta(days=1)) - max(v["start"], d["date"])).total_seconds() / 3600
        for v in d["voc"])
    heavy_voc = voc_hours >= 8

    malefic = [a for a in d["aspects"]
               if a["planet"] in ("المريخ", "زحل") and a["name"] in ("تربيع", "تقابل", "اقتران")]

    # الجراحة
    if heavy_voc or malefic:
        reason = []
        if heavy_voc:
            reason.append("لطول خلو المسار")
        if malefic:
            reason.append("لوجود زاوية شديدة مع " + " و".join(sorted({a["planet"] for a in malefic})))
        lines.append(
            "اليوم غير مناسب للعمليات الجراحية " + "، ".join(reason) +
            "، ما عدا من تمّ تحديد موعدها قبل اليوم وقبل خلو المسار.")
        lines.append(f"ويُتجنّب في كل الأحوال التدخّل الجراحي فيما يحكمه برج {sign}: {organ}.")
    else:
        lines.append(
            f"اليوم مقبول للعمليات الجراحية عمومًا، على أن يُتجنّب التدخّل فيما يحكمه "
            f"برج {sign} ما دام القمر فيه: {organ}.")

    # التجميل
    if heavy_voc:
        lines.append("مناسب للتجميل الخفيف فقط، ولا يصلح لما يُراد له أن يدوم.")
    elif waxing:
        lines.append("مناسب للتجميل ولما يُراد له بناء وامتلاء، لأن القمر متزايد.")
    else:
        lines.append("مناسب لما يُراد له شدّ وتقليل وإزالة، لأن القمر متناقص.")

    # قصّ الشعر
    if sign in tables.HAIR_RULES["cut_bad_signs"]:
        lines.append(f"لا يصلح لقصّ الشعر لأن القمر في برج {sign}.")
    elif sign in tables.HAIR_RULES["growth_signs"] and waxing:
        lines.append(f"يصلح جدًا لقصّ الشعر لنموّه وقوّته، القمر متزايد في برج {sign}.")
    elif waxing:
        lines.append("يصلح لقصّ الشعر إن أردت نموّه أسرع، القمر متزايد.")
    else:
        lines.append("يصلح لقصّ الشعر إن أردت إبطاء نموّه، القمر متناقص.")

    # إزالة الشعر
    if not waxing:
        lines.append("يصلح لإزالة الشعر الزائد بالليزر وغيره، وهو من أنسب أوقاتها لأن القمر متناقص.")
    else:
        lines.append("إزالة الشعر فيه مقبولة لكنها ليست في أفضل أوقاتها، لأن القمر متزايد.")

    # الصبغة والحنّاء
    if sign in tables.HAIR_RULES["dye_bad_signs"] or heavy_voc:
        lines.append("غير مناسب للصبغة والحنّاء.")
    else:
        lines.append("مناسب للصبغة والحنّاء.")

    return lines


# ── النصّ النهائي ────────────────────────────────────────────────
def render_text(d: dict, for_tomorrow: bool = True, location: str = "") -> str:
    parts = []
    lead = "للغد" if for_tomorrow else "لليوم"
    day = d["day_name"]

    # ١ — رأس النشرة وبرج القمر
    head = f"#النشرة_الفلكية {lead} {d['date_phrase']}"
    if location:
        head += f" — بتوقيت {location}"
    changes = d["moon_sign_changes"]
    if not changes:
        head += (f"\nالقمر في برج {d['moon_sign_noon']} طيلة {day} "
                 f"حتَّى {moment_phrase(d['moon_leaves_at'])} "
                 f"بعدها ينتقل لبرج {d['moon_next_sign']}.")
    else:
        seq = [f"القمر في برج {d['moon_sign_start']} من أول {day}"]
        for c in changes:
            seq.append(f"حتَّى {time_phrase(c['time'])} فينتقل لبرج {c['sign']}")
        seq.append(f"ويبقى فيه حتَّى {moment_phrase(d['moon_leaves_at'])} "
                   f"بعدها ينتقل لبرج {d['moon_next_sign']}")
        head += "\n" + "، ".join(seq) + "."
    head += (f"\nالشمس في برج {d['sun_sign']}، والقمر في طور "
             f"{d['phase']['name']} ({round(d['phase']['illumination']*100)}٪ إضاءة).")
    if d["retrogrades"]:
        head += "\nكواكب راجعة: " + "، ".join(d["retrogrades"]) + "."
    st = d.get("sun_times") or {}
    if st:
        head += "\n" + "، ".join(f"{k} {v.hour}:{v.minute:02d}" for k, v in st.items()) + "."
    parts.append(head)

    # ٢ — المنازل القمرية
    mn = ["#المنازل_القمرية"]
    for i, m in enumerate(d["mansions"]):
        start_txt = ("طيلة الليلة" if m["start"] < d["date"]
                     else f"من {time_phrase(m['start'])}")
        end_txt = (f"حتَّى {moment_phrase(m['end'])}"
                   if m["end"].date() != d["date"].date()
                   else f"حتَّى {time_phrase(m['end'])}")
        mn.append(f"القمر في منزلة {m['name']} (المنزلة {m['index']})، "
                  f"{m['mood_text']}، {start_txt} {end_txt}.")
        mn.append(f"  {m['desc']} {m['good_for']}")
    parts.append("\n".join(mn))

    # ٣ — الزوايا الفلكية
    az = ["#الزوايا_الفلكية"]
    if not d["aspects"] and not d["voc"]:
        az.append("- لا زوايا تامّة اليوم، يوم هادئ فلكيًا.")
    for a in d["aspects"]:
        az.append(f"- {time_phrase(a['time'])} زاوية {a['name']} "
                  f"بين القمر و{a['planet']}، {a['polarity']}. {a['text']}")
    for v in d["voc"]:
        kind = "خلو مسار طويل" if v["long"] else "خلو مسار"
        az.append(
            f"- {kind} يبدأ عند الساعة {time_phrase(v['start'])} "
            f"ويستمرّ حتَّى {moment_phrase(v['end'])} عند دخول القمر برج {v['next_sign']} "
            f"({dur_phrase(v['hours'])}). فترة فارغة من الحظوظ، غير مناسبة للبدايات "
            f"ولا للقرارات المصيريّة ولا لإنهاء علاقة ولا لتوقيع عقود.")
    parts.append("\n".join(az))

    # ٤ — الأخبار الصحية
    parts.append("#الأخبار_الصحية\n" + "\n".join(health_section(d)))

    return "\n\n".join(parts)
