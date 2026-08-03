# -*- coding: utf-8 -*-
"""
واجهة الخادم — دالة واحدة بلا خادم تخدم كل المسارات.
تعمل على Vercel وعلى الجهاز المحلي بنفس الشيفرة.

المسارات:
  GET /api/health
  GET /api/atlas?q=دمشق
  GET /api/ephemeris?date=2026-07-28&time=12:00&tz=Asia/Damascus
  GET /api/bulletin?date=2026-07-28&city=دمشق[&tz=&lat=&lon=&shift=0]
  GET /api/chart?date=1990-05-17&time=08:30&city=دمشق[&system=whole|placidus|equal]
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from datetime import date as _date, datetime, timedelta
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import atlas, bulletin, chart, config, elections, ephem, hours  # noqa: E402
from falak import apikeys, depth, gist, horary, ics, interpret  # noqa: E402
from falak import jyotish, monthly  # noqa: E402
from falak import mundane, plain, timelords, transits  # noqa: E402
from falak import timezone as ftz  # noqa: E402


# ── أدوات ────────────────────────────────────────────────────────
def _one(q: dict, key: str, default=None):
    v = q.get(key)
    return v[0] if v else default


class ApiError(Exception):
    def __init__(self, msg, status=400):
        super().__init__(msg)
        self.status = status


def resolve_place(q: dict):
    """يُرجع (lat, lon, tzname, label) من اسم مدينة أو من إحداثيات صريحة."""
    city = _one(q, "city")
    lat, lon, tz = _one(q, "lat"), _one(q, "lon"), _one(q, "tz")
    label = None
    if city:
        hit = atlas.find(city)
        if not hit:
            raise ApiError(f"لم أجد مدينة باسم «{city}». جرّب اسمًا آخر أو أرسل lat و lon و tz.")
        lat = lat or hit["lat"]
        lon = lon or hit["lon"]
        tz = tz or hit["tz"]
        label = hit["label"]
    if lat is None or lon is None or tz is None:
        raise ApiError("لا بدّ من city، أو من lat و lon و tz معًا.")
    try:
        ZoneInfo(str(tz))
    except (ZoneInfoNotFoundError, ValueError):
        raise ApiError(f"منطقة زمنية غير معروفة: {tz}")
    return float(lat), float(lon), str(tz), label or f"{lat}, {lon}"


def parse_when(q: dict, tzname: str, default_time="12:00"):
    ds = _one(q, "date")
    ts = _one(q, "time", default_time)
    tz = ZoneInfo(tzname)
    if not ds:
        return datetime.now(tz)
    try:
        d = _date.fromisoformat(ds)
        hh, mm = (ts.split(":") + ["0"])[:2]
        return datetime(d.year, d.month, d.day, int(hh), int(mm), tzinfo=tz)
    except ValueError:
        raise ApiError("صيغة التاريخ يجب أن تكون YYYY-MM-DD والوقت HH:MM")


def parse_birth(q: dict, tzname: str, lon: float, default_time="12:00"):
    """يُرجع (الوقت المُدرك، تفاصيل التوقيت التاريخي وتحذيراته)."""
    ds = _one(q, "date")
    ts = _one(q, "time", default_time)
    if not ds:
        now = datetime.now(ZoneInfo(tzname))
        return now, ftz.resolve(now.replace(tzinfo=None), tzname, lon)
    try:
        d = _date.fromisoformat(ds)
        hh, mm = (ts.split(":") + ["0"])[:2]
        naive = datetime(d.year, d.month, d.day, int(hh), int(mm))
    except ValueError:
        raise ApiError("صيغة التاريخ يجب أن تكون YYYY-MM-DD والوقت HH:MM")
    info = ftz.resolve(naive, tzname, lon)
    return info["when"], info



def _level(q: dict) -> str:
    """مستوى اللغة المطلوب: plain (افتراضي) أو expert."""
    lv = _one(q, "level", plain.DEFAULT_LEVEL)
    return lv if lv in plain.LEVELS else plain.DEFAULT_LEVEL


def _apply_level(out: dict, q: dict) -> dict:
    """يُبسّط النصوص المولَّدة إن كان المستوى المطلوب هو العامّي."""
    lv = _level(q)
    out["level"] = lv
    out["levels"] = plain.LEVELS
    if lv != "plain":
        return out
    out = plain.simplify_deep(out, keep_original=True)
    out["level"] = lv
    out["levels"] = plain.LEVELS
    return out


# ── المسارات ─────────────────────────────────────────────────────
def route_health(q):
    out = {"ok": True, "cities": len(atlas.CITIES),
           "api_version": API_VERSION,
           "systems": {k: v["name"] for k, v in chart.HOUSE_SYSTEMS.items()},
           "chiron": os.path.isdir(os.path.join(
               os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe"))}
    if apikeys.is_dev_secret():
        # لا يُكتَم: مفاتيح مُصدَرة بمفتاح سرّي تجريبي تسقط عند النشر
        out["warning"] = ("الخادم يعمل بمفتاح سرّي تجريبي. اضبط "
                          "FALAK_API_SECRET في بيئة النشر، وإلا سقطت "
                          "كلّ المفاتيح المُصدَرة عند أوّل ضبط له.")
    return out


def route_atlas(q):
    term = _one(q, "q", "")
    return {"query": term, "results": atlas.search(term, int(_one(q, "limit", "12")))}


def route_ephemeris(q):
    tzname = _one(q, "tz", "UTC")
    try:
        ZoneInfo(tzname)
    except Exception:
        raise ApiError(f"منطقة زمنية غير معروفة: {tzname}")
    when = parse_when(q, tzname)
    jd = ephem.to_jd(when)
    rows = []
    for name, code, sym, core, _cls in chart.BODIES:
        try:
            import swisseph as swe
            x = swe.calc_ut(jd, code, chart.FLAGS)[0]
        except Exception:
            continue
        L = x[0] % 360.0
        rows.append({"name": name, "symbol": sym, "lon": round(L, 6),
                     "speed": round(x[3], 6), "retro": x[3] < 0, **chart.dms(L)})
    return {"when_local": when.isoformat(), "when_utc": when.astimezone(ephem.UTC).isoformat(),
            "tz": tzname, "bodies": rows, "moon_phase": ephem.moon_phase(when)}


def route_bulletin(q):
    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    ds = _one(q, "date")
    day = _date.fromisoformat(ds) if ds else datetime.now(tz).date()

    shift = _one(q, "shift")
    if shift is not None:
        config.MANSION_SHIFT = int(shift)

    d = bulletin.gather(day, tzname, lat, lon)
    for_tomorrow = _one(q, "voice", "today") == "tomorrow"
    place = _one(q, "city") or label
    text = bulletin.render_text(d, for_tomorrow=for_tomorrow, location=place)

    return _apply_level({
        "date": day.isoformat(), "tz": tzname, "place": place,
        "lat": lat, "lon": lon, "mansion_shift": config.MANSION_SHIFT,
        "text": text,
        "summary": {
            "moon_sign": d["moon_sign_noon"], "sun_sign": d["sun_sign"],
            "phase": d["phase"]["name"],
            "illum": round(d["phase"]["illumination"] * 100),
            "retrogrades": d["retrogrades"],
            "sun_times": {k: v.strftime("%H:%M") for k, v in (d.get("sun_times") or {}).items()},
            "mansions": [{"index": m["index"], "name": m["name"], "mood": m["mood"],
                          "start": m["start"].isoformat(), "end": m["end"].isoformat()}
                         for m in d["mansions"]],
            "aspects": [{"time": a["time"].strftime("%H:%M"), "planet": a["planet"],
                         "name": a["name"], "polarity": a["polarity"], "text": a["text"]}
                        for a in d["aspects"]],
            "voc": [{"start": v["start"].strftime("%H:%M"), "end": v["end"].isoformat(),
                     "hours": round(v["hours"], 1), "long": v["long"],
                     "next_sign": v["next_sign"]} for v in d["voc"]],
        },
    }, q)


def route_chart(q):
    lat, lon, tzname, label = resolve_place(q)
    when, tzinfo = parse_birth(q, tzname, lon)
    system = _one(q, "system", "whole")
    if system not in chart.HOUSE_SYSTEMS:
        raise ApiError(f"نظام بيوت غير معروف: {system}. المتاح: "
                       + "، ".join(chart.HOUSE_SYSTEMS))
    minor = _one(q, "minor", "1") == "1"
    out = chart.compute(when, lat, lon, system, tzname,
                        minor_aspects=minor, tz_info=tzinfo)
    out["place"] = _one(q, "city") or label
    out["name"] = _one(q, "name", "")
    out["tz_describe"] = ftz.describe(tzinfo)

    if _one(q, "interpret", "1") == "1":
        out["reading"] = interpret.read_chart(out)

    # الخريطة نفسها بنظام آخر، لتيسير المقارنة
    if _one(q, "both", "1") == "1":
        other = _one(q, "compare") or ("placidus" if system == "whole" else "whole")
        if other in chart.HOUSE_SYSTEMS and other != system:
            alt = chart.compute(when, lat, lon, other, tzname,
                                minor_aspects=False, tz_info=tzinfo)
            out["alt"] = {"system": other,
                          "system_name": chart.HOUSE_SYSTEMS[other]["name"],
                          "system_note": chart.HOUSE_SYSTEMS[other]["note"],
                          "houses": alt["houses"], "angles": alt["angles"],
                          "bodies": [{"name": b["name"], "house": b["house"]}
                                     for b in alt["bodies"]],
                          "dominants": alt["dominants"]}
    return _apply_level(out, q)


def _side(q: dict, suffix: str):
    """يقرأ معطيات أحد الطرفين: date2/time2/city2 مثلًا."""
    sub = {}
    for k in ("date", "time", "city", "lat", "lon", "tz", "name"):
        v = _one(q, k + suffix)
        if v is not None:
            sub[k] = [v]
    return sub


def route_synastry(q):
    """
    التوافق بين خريطتين: التزاوج والمركّبة ودافيسون وثلاثة موازين.

    المعطيات: date/time/city للأوّل، وdate2/time2/city2 للثاني،
    وname وname2 اختياريان.
    """
    from falak import synastry as syn

    q1 = _side(q, "")
    q2 = _side(q, "2")
    if not q2.get("date"):
        raise ApiError("لا بدّ من مولد ثانٍ: date2 و time2 و city2.")

    def build(sub, who):
        lat, lon, tzname, label = resolve_place(sub)
        when, tzinfo = parse_birth(sub, tzname, lon)
        c = chart.compute(when, lat, lon, _one(q, "system", "whole"),
                          tzname, minor_aspects=True, tz_info=tzinfo)
        c["place"] = _one(sub, "city") or label
        c["name"] = _one(sub, "name") or who
        c["tz_describe"] = ftz.describe(tzinfo)
        return c

    A = build(q1, "الأوّل")
    B = build(q2, "الثاني")

    out = {
        "a": {"name": A["name"], "place": A["place"],
              "when_local": A["when_local"], "bodies": A["bodies"],
              "angles": A["angles"], "houses": A["houses"],
              "warnings": A["warnings"]},
        "b": {"name": B["name"], "place": B["place"],
              "when_local": B["when_local"], "bodies": B["bodies"],
              "angles": B["angles"], "houses": B["houses"],
              "warnings": B["warnings"]},
        "reading": syn.read(A, B, A["name"], B["name"]),
        "inter_aspects": syn.inter_aspects(A, B),
    }
    if _one(q, "composite", "1") == "1":
        out["composite"] = syn.composite(A, B)
    if _one(q, "davison", "1") == "1":
        out["davison"] = syn.davison(A, B)
    out["disclaimer"] = (
        "لا تُبنى على هذه الصفحة قرارات زواج ولا فراق ولا شراكة. "
        "الخريطة تصف ميلًا وطبعًا، ولا تعرف ما تعرفانه أنتما عن "
        "بعضكما، ولا ما يصنعه الاختيار والمعاملة."
    )
    return _apply_level(out, q)


def route_jyotish(q):
    """
    الجيوتِش: الخريطة الهندية بالمنطقة النجمية.

      /api/jyotish?date=&time=&city=[&ayanamsha=lahiri&vargas=9,10]
      /api/jyotish?list=1   لمذاهب الأينامشا والمنازل السبع والعشرين
    """
    if _one(q, "list") == "1":
        now = datetime.now(ephem.UTC)
        return {
            "ayanamshas": {k: {"name": v["name"], "note": v["note"],
                               "value": round(jyotish.ayanamsha(now, k), 4)}
                           for k, v in jyotish.AYANAMSHAS.items()},
            "nakshatras": [
                {"index": i + 1, "name": n[0], "lord": n[1],
                 "arabic_mansion": n[2], "star": n[3],
                 "from": round(i * jyotish.NAK_ARC, 4),
                 "to": round((i + 1) * jyotish.NAK_ARC, 4),
                 "yogatara": jyotish.yogatara(i + 1, now)}
                for i, n in enumerate(jyotish.NAKSHATRAS)],
            "vargas": jyotish.VARGAS,
            "dasha_years": jyotish.DASHA_YEARS,
            "note": ("المنازل السبع والعشرون عند الهنود والثماني "
                     "والعشرون عند العرب نجومها واحدة — والعمود الثالث "
                     "يُقابل بينهما."),
        }

    lat, lon, tzname, label = resolve_place(q)
    when, tzinfo = parse_birth(q, tzname, lon)
    ayan = _one(q, "ayanamsha", jyotish.DEFAULT_AYANAMSHA)
    if ayan not in jyotish.AYANAMSHAS:
        raise ApiError(f"مذهب أينامشا غير معروف: {ayan}. المتاح: "
                       + "، ".join(jyotish.AYANAMSHAS))
    try:
        vg = [int(x) for x in (_one(q, "vargas", "9,10") or "").split(",") if x]
    except ValueError:
        raise ApiError("vargas أعداد مفصولة بفواصل، مثل 9,10")

    out = jyotish.compute(when, lat, lon, ayan, tzname, vargas=vg)
    out["yogas"] = jyotish.yogas(out)
    out["relations"] = jyotish.relations(out["bodies"])
    out["yoga_note"] = (
        "مع كل يوغا شرطُ تحقّقها بالأسماء والبيوت، ونسبةُ الخرائط "
        "التي تحملها. فالكتب تصفها وصف النوادر، والحساب يقول إن "
        "بعضها في ثلثَي الناس — والأندر أوّلًا في هذه القائمة.")
    out["place"] = _one(q, "city") or label
    out["name"] = _one(q, "name", "")
    out["tz_describe"] = ftz.describe(tzinfo)
    out["warnings"] = (tzinfo or {}).get("warnings") or []

    moon = next(b for b in out["bodies"] if b["name"] == "القمر")
    out["dasha"] = jyotish.vimshottari(
        datetime.fromisoformat(out["when_utc"]), moon["lon"],
        levels=int(_one(q, "levels", "2")))
    out["dasha"]["now"] = jyotish.current_dasha(
        out["dasha"], datetime.now(ephem.UTC))

    # الفرق عن الخريطة الاستوائية — أوّل ما يسأل عنه القارئ
    trop = chart.compute(when, lat, lon, "whole", tzname,
                         minor_aspects=False, tz_info=tzinfo)
    tby = {b["name"]: b["sign"] for b in trop["bodies"]}
    out["compare_tropical"] = {
        "system": "العربي/الغربي الاستوائي",
        "ascendant": trop["angles"]["الطالع"]["sign"],
        "bodies": {b["name"]: {"sidereal": b["sign"],
                               "tropical": tby.get(b["name"], ""),
                               "moved": tby.get(b["name"]) != b["sign"]}
                   for b in out["bodies"] if b["name"] in tby},
        "note": ("الفرق بين المقياسين نحو "
                 f"{out['ayanamsha']['value']:.1f} درجة اليوم. فأكثر "
                 "الأجرام تتراجع برجًا واحدًا — وليس هذا خطأً في أحد "
                 "المقياسين، بل اختلاف في نقطة البداية: الاعتدال "
                 "الربيعي هناك، والنجوم الثابتة هنا."),
    }
    return _apply_level(out, q)


def route_horary(q):
    """
    المسألة: خريطة اللحظة التي وقع فيها السؤال.

      قائمة الأسئلة:  /api/horary?list=1
      الحكم:          /api/horary?city=&question=...  (أو house=7)
                      و date/time اختياريان — والأصل لحظة السؤال الآن.
    """
    if _one(q, "list") == "1":
        return {"questions": {k: v for k, v in horary.QUESTIONS.items()},
                "houses": {str(k): v["name"] for k, v in depth.HOUSES.items()}}

    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    question = _one(q, "question", "")
    house = _one(q, "house")
    if question and question in horary.QUESTIONS:
        h = horary.QUESTIONS[question]["house"]
    elif house and house.isdigit() and 1 <= int(house) <= 12:
        h = int(house)
    else:
        raise ApiError("لا بدّ من question من القائمة، أو house بين ١ و١٢. "
                       "انظر /api/horary?list=1")

    ds = _one(q, "date")
    if ds:
        when = parse_when(q, tzname, default_time=datetime.now(tz).strftime("%H:%M"))
    else:
        when = datetime.now(tz)

    # المسائل تُعمل على ريجومونتانوس عند أهل الصناعة، لأن الحكم فيها
    # على البيوت لا على البروج. ونتيح تغييره لمن يذهب مذهبًا آخر.
    system = _one(q, "system", "regiomontanus")
    if system not in chart.HOUSE_SYSTEMS:
        raise ApiError(f"نظام بيوت غير معروف: {system}")

    c = chart.compute(when, lat, lon, system, tzname, minor_aspects=False)
    j = horary.judge(c, h, question,
                     horizon_days=int(_one(q, "horizon", "45")))
    return _apply_level({
        "place": _one(q, "city") or label,
        "when_local": c["when_local"], "tz": tzname,
        "system": system, "system_name": chart.HOUSE_SYSTEMS[system]["name"],
        "chart": {"bodies": c["bodies"], "angles": c["angles"],
                  "houses": c["houses"], "aspects": c["aspects"],
                  "sect": c["sect"], "moon": c["moon"]},
        "judgment": j,
    }, q)


def route_search(q):
    """
    البحث عن أفضل وقت: /api/search?purpose=&city=&start=&days=90
      ومع خريطة السائل: أضِف birth و birthtime و birthcity.
    """
    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    purpose = _one(q, "purpose")
    if not purpose:
        raise ApiError("لا بدّ من purpose. انظر /api/elections?list=1")

    ss = _one(q, "start")
    start = _date.fromisoformat(ss) if ss else datetime.now(tz).date()
    days = int(_one(q, "days", "90"))
    if days > 200:
        raise ApiError("أقصى مدى للبحث مئتا يوم، حتى لا تنقضي مهلة الخادم. "
                       "قسّمه على بحثين.")

    natal = None
    if _one(q, "birth"):
        sub = {"date": [_one(q, "birth")],
               "time": [_one(q, "birthtime", "12:00")]}
        bcity = _one(q, "birthcity")
        if bcity:
            sub["city"] = [bcity]
        blat, blon, btz, _l = resolve_place(sub if bcity else q)
        bwhen, binfo = parse_birth(sub, btz, blon)
        natal = chart.compute(bwhen, blat, blon, "whole", btz,
                              minor_aspects=False, tz_info=binfo)

    out = elections.search(start, days, tzname, lat, lon, purpose,
                           natal=natal, top=int(_one(q, "top", "10")))
    if "error" in out:
        raise ApiError(out["error"])
    out["place"] = _one(q, "city") or label
    out["tz"] = tzname
    return _apply_level(out, q)


def route_depth(q):
    """المرجع: ملفّ كل بيت وكل برج، والكواكب في البيوت، والزوايا."""
    from falak import aspects_deep as adeep
    return _apply_level({
        "houses": {str(k): v for k, v in depth.HOUSES.items()},
        "signs": depth.SIGNS_DEEP,
        "planet_in_house": {p: {str(h): t for h, t in tbl.items()}
                            for p, tbl in depth.PLANET_IN_HOUSE.items()},
        "aspects": {f"{a} — {b}": v for (a, b), v in adeep.PAIRS.items()},
        "aspects_outer": {f"{a} — {b}": v for (a, b), v in adeep.OUTER_PAIRS.items()},
        "coverage": {**depth.house_coverage(), **adeep.coverage()},
    }, q)


def route_glossary(q):
    """معجم المصطلحات — لشروح «عند الطلب» في الواجهة."""
    return {"terms": interpret.GLOSSARY, "ui": plain.UI_LABELS,
            "intros": plain.INTROS, "levels": plain.LEVELS,
            "default_level": plain.DEFAULT_LEVEL}


def route_hours(q):
    """ساعات الكواكب: الاثنتا عشرة نهارًا ومثلها ليلًا."""
    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    ds = _one(q, "date")
    day = (datetime.fromisoformat(ds) if ds else datetime.now(tz)).replace(tzinfo=tz)

    tbl = hours.hours_for(day, lat, lon, tzname)
    if "error" in tbl:
        raise ApiError(tbl["error"])

    now = datetime.now(tz)
    current = hours.hour_at(now, lat, lon, tzname) if day.date() == now.date() else None

    purpose = _one(q, "purpose")
    purpose_hours = None
    if purpose:
        purpose_hours = hours.for_purpose(day, lat, lon, tzname, purpose,
                                          day_only=_one(q, "dayonly", "1") == "1")

    return _apply_level({
        "place": _one(q, "city") or label,
        "purposes": list(hours.PURPOSE_HOURS),
        "purpose_result": purpose_hours,
        "sources": hours.SOURCES,
        "date": tbl["date"], "weekday": tbl["weekday"], "tz": tzname,
        "day_ruler": tbl["day_ruler"], "day_ruler_symbol": tbl["day_ruler_symbol"],
        "day_ruler_note": tbl["day_ruler_note"],
        "sunrise": tbl["sunrise_text"], "sunset": tbl["sunset_text"],
        "day_hour_minutes": tbl["day_hour_minutes"],
        "night_hour_minutes": tbl["night_hour_minutes"],
        "current": {k: v for k, v in current.items()
                    if k not in ("start", "end")} if current else None,
        "hours": [{k: v for k, v in h.items() if k not in ("start", "end")}
                  for h in tbl["hours"]],
        "text": hours.render_text(tbl),
    }, q)


def route_elections(q):
    """
    تقويم الاختيارات: درجة كل يوم لكل غرض.
      يوم واحد لغرض:      /api/elections?date=&city=&purpose=الزواج والخِطبة
      شهر كامل:           /api/elections?year=&month=&city=&purposes=أ،ب
      قائمة الأغراض فقط:  /api/elections?list=1
    """
    if _one(q, "list") == "1":
        return {"purposes": {k: {"group": v.get("group"), "note": v.get("note", ""),
                                 "ruler": v.get("ruler")}
                             for k, v in elections.PURPOSES.items()},
                "groups": elections.GROUPS,
                "verdicts": [{"min": t, "name": n, "note": d}
                             for t, n, d in elections.VERDICTS]}

    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    place = _one(q, "city") or label

    # يوم واحد
    ds = _one(q, "date")
    purpose = _one(q, "purpose")
    if ds or (purpose and not _one(q, "month")):
        day = _date.fromisoformat(ds) if ds else datetime.now(tz).date()
        if purpose:
            r = elections.score_day(day, tzname, lat, lon, purpose)
            if "error" in r:
                raise ApiError(r["error"])
            return {"place": place, "tz": tzname, **r}
        # كل الأغراض ليوم واحد
        data = bulletin.gather(day, tzname, lat, lon)
        ecl = elections.eclipses_on(day, tzname)
        rows = []
        for p in elections.PURPOSES:
            r = elections.score_day(day, tzname, lat, lon, p, data, eclipses=ecl)
            rows.append({"purpose": p, "group": r["group"], "score": r["score"],
                         "verdict": r["verdict"], "plus": r["plus"],
                         "minus": r["minus"], "rule": r["rule"],
                         "best_hours": r["best_hours"]})
        rows.sort(key=lambda x: -x["score"])
        return {"place": place, "tz": tzname, "date": day.isoformat(),
                "eclipse": ecl[0]["title"] if ecl else None,
                "moon_sign": data["moon_sign_noon"],
                "mansion": data["mansions"][0]["name"],
                "groups": elections.GROUPS, "results": rows}

    # شهر كامل
    now = datetime.now(tz)
    year = int(_one(q, "year", now.year))
    month = int(_one(q, "month", now.month))
    if not (1 <= month <= 12):
        raise ApiError("الشهر يجب أن يكون بين ١ و١٢")
    ps = _one(q, "purposes")
    plist = [x.strip() for x in ps.split("،")] if ps else None
    if plist:
        plist = [x for x in plist if x]
    out = elections.month_calendar(year, month, tzname, lat, lon, plist)
    if "error" in out:
        raise ApiError(out["error"])
    out["place"] = place
    return _apply_level(out, q)



def route_timelords(q):
    """
    أرباب الأزمنة: الفردارات والتسيير السنوي والعودة الشمسية.
      /api/timelords?date=1990-05-17&time=08:30&city=حلب[&for=2026-08-02][&live=دمشق]
    """
    lat, lon, tzname, label = resolve_place(q)
    when, tzinfo = parse_birth(q, tzname, lon)
    natal = chart.compute(when, lat, lon, "whole", tzname,
                          minor_aspects=False, tz_info=tzinfo)

    # الموضع الذي يقيم فيه صاحب الخريطة الآن (للعودة الشمسية)
    live = _one(q, "live")
    if live:
        hit = atlas.find(live)
        if not hit:
            raise ApiError(f"لم أجد مدينة الإقامة «{live}».")
        rlat, rlon, rtz, rlabel = hit["lat"], hit["lon"], hit["tz"], hit["label"]
    else:
        rlat, rlon, rtz, rlabel = lat, lon, tzname, label

    fd = _one(q, "for")
    tz = ZoneInfo(rtz)
    moment = (datetime.fromisoformat(fd).replace(tzinfo=tz)
              if fd else datetime.now(tz))

    t = timelords.timelords(natal, moment, rlat, rlon, rtz)
    t["text"] = timelords.render_text(t)
    t["birth_place"] = _one(q, "city") or label
    t["residence"] = rlabel
    t["asked_for"] = moment.date().isoformat()
    t["natal_summary"] = {
        "asc": natal["angles"]["الطالع"]["text"],
        "sun": next(b["text"] for b in natal["bodies"] if b["name"] == "الشمس"),
        "moon": next(b["text"] for b in natal["bodies"] if b["name"] == "القمر"),
        "sect": natal["sect"],
    }
    if _one(q, "table", "1") == "1":
        t["profection_table"] = timelords.profection_years(
            datetime.fromisoformat(natal["when_utc"]),
            natal["angles"]["الطالع"]["lon"], 0, 90)
    return _apply_level(t, q)


def route_monthly(q):
    """النشرة الشهرية: سرد الشهر ومعناه بثلاثة ألسنة."""
    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    now = datetime.now(tz)
    year = int(_one(q, "year", now.year))
    month = int(_one(q, "month", now.month))
    if not (1 <= month <= 12):
        raise ApiError("الشهر يجب أن يكون بين ١ و١٢")
    if not (1800 <= year <= 2400):
        raise ApiError("السنة يجب أن تكون بين ١٨٠٠ و٢٤٠٠")
    voice = _one(q, "voice", "daily")
    if voice not in monthly.VOICES:
        raise ApiError("لسان غير معروف: " + voice + ". المتاح: "
                       + "، ".join(monthly.VOICES))
    ps = _one(q, "purposes")
    plist = [x.strip() for x in ps.split("،") if x.strip()] if ps else None

    # القسم الشخصي: يحتاج تاريخ ميلاد ومكانه
    natal = None
    nd = _one(q, "natal_date")
    if nd:
        ncity = _one(q, "natal_city") or _one(q, "city")
        nq = {"city": [ncity]} if ncity else {}
        for k in ("natal_lat", "natal_lon", "natal_tz"):
            v = _one(q, k)
            if v:
                nq[k.replace("natal_", "")] = [v]
        nlat, nlon, ntz, nlabel = resolve_place(nq)
        nwhen, ninfo = parse_birth(
            {"date": [nd], "time": [_one(q, "natal_time", "12:00")]}, ntz, nlon)
        natal = chart.compute(nwhen, nlat, nlon, "whole", ntz,
                              minor_aspects=False, tz_info=ninfo)
        natal["place"] = nlabel

    out = monthly.compose(year, month, tzname, lat, lon, voice=voice,
                          place=_one(q, "city") or label, purposes=plist,
                          with_figures=_one(q, "figures", "1") == "1",
                          natal=natal)
    if natal:
        out["natal_summary"] = {
            "place": natal["place"],
            "asc": natal["angles"]["الطالع"]["text"],
            "sun": next(b["text"] for b in natal["bodies"] if b["name"] == "الشمس"),
            "moon": next(b["text"] for b in natal["bodies"] if b["name"] == "القمر"),
        }
    return _apply_level(out, q)


def route_month(q):
    """أحداث الشهر العامّة: انتقالات، رجوع، زوايا، تقميرات، كسوف."""
    tzname = _one(q, "tz")
    if not tzname:
        city = _one(q, "city")
        if city:
            hit = atlas.find(city)
            tzname = hit["tz"] if hit else "UTC"
        else:
            tzname = "UTC"
    try:
        ZoneInfo(tzname)
    except Exception:
        raise ApiError(f"منطقة زمنية غير معروفة: {tzname}")

    now = datetime.now(ZoneInfo(tzname))
    year = int(_one(q, "year", now.year))
    month = int(_one(q, "month", now.month))
    if not (1 <= month <= 12):
        raise ApiError("الشهر يجب أن يكون بين ١ و١٢")
    if not (1800 <= year <= 2400):
        raise ApiError("السنة يجب أن تكون بين ١٨٠٠ و٢٤٠٠")

    return _apply_level(mundane.month_events(
        year, month, tzname,
        minor_aspects=_one(q, "minor", "0") == "1",
        quarters=_one(q, "quarters", "1") == "1"), q)


ROUTES = {
    "health": route_health,
    "atlas": route_atlas,
    "ephemeris": route_ephemeris,
    "bulletin": route_bulletin,
    "chart": route_chart,
    "glossary": route_glossary,
    "depth": route_depth,
    "hours": route_hours,
    "month": route_month,
    "elections": route_elections,
    "monthly": route_monthly,
    "timelords": route_timelords,
    "synastry": route_synastry,
    "horary": route_horary,
    "search": route_search,
    "jyotish": route_jyotish,
}



# ══════════════════════════════════════════════════════════════════
# الواجهة البرمجية العامّة — /api/v1/…
#
# المسارات نفسها، ولكن بعقد معلَن: إصدار مرقَّم، ومغلَّف موحَّد
# للجواب والخطأ، ومفتاح ومستوى وحدّ استعمال. والمسارات القديمة
# /api/… تبقى كما هي لصفحات الموقع نفسه.
# ══════════════════════════════════════════════════════════════════
API_VERSION = "1.0"


class Raw:
    """جواب ليس JSON — كملفّ التقويم."""

    def __init__(self, body: bytes, ctype: str, filename: str = "",
                 status: int = 200):
        self.body = body
        self.ctype = ctype
        self.filename = filename
        self.status = status


def _client_id(q: dict, key_info: dict) -> str:
    """
    من نعدّ عليه الطلبات. المفتاح إن وُجد، وإلا فما يمرّره الوسيط
    من عنوان — وهو غير موثوق، فالحدّ على المجهولين تقريبيّ أصلًا.
    """
    k = _one(q, "key") or _one(q, "api_key")
    if k:
        return "k:" + hashlib.sha1(k.encode()).hexdigest()[:16]
    return "a:" + (_one(q, "_ip") or "anon")


def route_v1(path: str, query: dict, headers: dict | None = None):
    """بوّابة الإصدار الأوّل: مفتاح، ثم حدّ، ثم المسار."""
    headers = headers or {}
    name = path.rstrip("/").split("/")[-1] or "index"

    key = (_one(query, "key") or _one(query, "api_key")
           or headers.get("x-api-key") or "")
    info = apikeys.verify(key or None)
    if key and not info["valid"]:
        raise ApiError(info.get("error", "مفتاح غير صالح."), 401)

    if name in ("index", "v1", ""):
        return _v1_index(info)
    if name == "key":
        return _v1_key(query)

    rate = apikeys.check_rate(_client_id(query, info), info["rpm"])
    if not rate["ok"]:
        raise ApiError(
            f"تجاوزت {rate['limit']} طلبًا في الدقيقة. "
            f"أعِد المحاولة بعد {rate['retry_after']} ثانية. "
            "وللمزيد استخرج مفتاحًا من /api.html.", 429)

    if name in ("calendar.ics", "calendar", "ics"):
        return route_calendar(query, info)

    if name not in ROUTES:
        raise ApiError(f"مسار غير معروف: {name}. المتاح: "
                       + "، ".join(sorted(ROUTES)), 404)

    # المستوى يحدّ مدى البحث
    if name == "search":
        d = int(_one(query, "days", "90"))
        if d > info["max_days"]:
            raise ApiError(
                f"مستواك ({info['name']}) يسمح بـ{info['max_days']} يومًا، "
                f"وطلبت {d}. استخرج مفتاحًا أوسع أو قسّم البحث.", 403)

    data = ROUTES[name](query)
    g = gist.for_route(name, data)
    if g:
        data = {**data, "gist": g}
    return {
        "ok": True,
        "version": API_VERSION,
        "endpoint": name,
        "tier": info["tier"],
        "rate": {"limit": rate["limit"], "remaining": rate["remaining"],
                 "window": "60s"},
        "data": data,
    }


def _v1_index(info: dict) -> dict:
    return {
        "ok": True, "version": API_VERSION,
        "name": "الفَلَك — واجهة برمجية عربية للفلك التقليدي",
        "base": "/api/v1/",
        "endpoints": {
            "health": "حال الخادم", "atlas": "بحث المدن",
            "ephemeris": "مواقع الأجرام في لحظة",
            "chart": "خريطة ميلاد كاملة مع القراءة",
            "bulletin": "النشرة اليومية", "monthly": "النشرة الشهرية",
            "month": "أحداث الشهر الفلكية", "hours": "ساعات الكواكب",
            "elections": "تقويم الاختيارات",
            "search": "البحث عن أفضل وقت لغرض",
            "horary": "الحكم في مسألة", "synastry": "التوافق بين خريطتين",
            "timelords": "الفردارات والتسيير والعودة الشمسية",
            "depth": "مرجع النصوص: البيوت والبروج والزوايا",
            "glossary": "معجم المصطلحات",
            "calendar.ics": "تصدير تقويم iCalendar",
            "key": "استخراج مفتاح وصول",
        },
        "tiers": apikeys.TIERS,
        "your_tier": {"tier": info["tier"], "name": info["name"],
                      "rpm": info["rpm"], "max_days": info["max_days"],
                      "anonymous": info.get("anonymous", True)},
        "envelope": ("كل جواب: {ok, version, endpoint, tier, rate, data}. "
                     "وكل خطأ: {ok:false, error, status}."),
        "licence": ("الحساب بمكتبة Swiss Ephemeris (AGPL). من بنى عليها "
                    "خدمة مغلقة فعليه رخصتها التجارية — انظر astro.com."),
        "limits": ("حدّ الاستعمال يُعدّ في ذاكرة النسخة الواحدة، والدالّة "
                   "بلا خادم تُشغَّل نسخًا متعدّدة. فهو مُهدّئ لا حارس: "
                   "يمنع الحلقة المنفلتة ولا يمنع هجومًا مقصودًا. "
                   "قلناها صراحةً فلا يبني عليها أحد ما لا تحتمل."),
    }


def _v1_key(q: dict) -> dict:
    """استخراج مفتاح. المستوى المفتوح والأساسي بلا شرط؛ والموسّع بطلب."""
    tier = _one(q, "tier", "free")
    if tier not in ("free", "basic"):
        raise ApiError("المستوى الموسّع يُطلَب بالمراسلة، لا من هذا المسار.",
                       403)
    days = int(_one(q, "days", "365"))
    k = apikeys.issue(tier, days, _one(q, "label", ""))
    return {"ok": True, "version": API_VERSION, "data": k}


def route_calendar(q: dict, info: dict | None = None):
    """
    تصدير iCalendar. يُرجع Raw لا JSON.

      /api/v1/calendar.ics?kind=bulletin&city=دمشق&days=30
      /api/v1/calendar.ics?kind=elections&city=دمشق&purpose=…&days=90
      /api/v1/calendar.ics?kind=month&city=دمشق&year=2026&month=8
      /api/v1/calendar.ics?kind=hours&city=دمشق&days=7&planets=المشتري,الزهرة
    """
    info = info or apikeys.verify(None)
    kind = _one(q, "kind", "bulletin")
    if kind not in ics.KINDS:
        raise ApiError(f"نوع غير معروف: {kind}. المتاح: "
                       + "، ".join(ics.KINDS))

    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    place = _one(q, "city") or label
    ss = _one(q, "start")
    start = _date.fromisoformat(ss) if ss else datetime.now(tz).date()
    days = max(1, min(int(_one(q, "days", "30")), info["max_days"]))

    if kind == "bulletin":
        evs = ics.bulletin_events(start, min(days, 60), tzname, lat, lon, place)
        title = f"الفَلَك — منازل القمر ({place})"
        desc = "منازل القمر الثماني والعشرون وأوقات خلو المسار."
    elif kind == "elections":
        purpose = _one(q, "purpose")
        if not purpose:
            raise ApiError("لا بدّ من purpose مع kind=elections.")
        natal = None
        if _one(q, "birth"):
            sub = {"date": [_one(q, "birth")],
                   "time": [_one(q, "birthtime", "12:00")]}
            bc = _one(q, "birthcity")
            if bc:
                sub["city"] = [bc]
            blat, blon, btz, _l = resolve_place(sub if bc else q)
            bwhen, binfo = parse_birth(sub, btz, blon)
            natal = chart.compute(bwhen, blat, blon, "whole", btz,
                                  minor_aspects=False, tz_info=binfo)
        evs = ics.election_events(start, days, tzname, lat, lon, purpose,
                                  place, int(_one(q, "min", "70")), natal)
        title = f"الفَلَك — {purpose} ({place})"
        desc = f"أفضل الأيام لـ«{purpose}» بدرجة {_one(q, 'min', '70')} فأعلى."
    elif kind == "month":
        y = int(_one(q, "year", str(start.year)))
        m = int(_one(q, "month", str(start.month)))
        evs = ics.month_events(y, m, tzname)
        title = f"الفَلَك — أحداث السماء {y}/{m}"
        desc = "الانتقالات والوقوف والرجوع والتقمير والكسوف."
    else:
        planets = [x.strip() for x in (_one(q, "planets", "") or "").split(",")
                   if x.strip()]
        evs = ics.hour_events(start, min(days, 14), tzname, lat, lon, place,
                              only=planets or None,
                              day_only=_one(q, "night", "0") != "1")
        title = f"الفَلَك — ساعات الكواكب ({place})"
        desc = "الساعات الاثنتا عشرة النهارية بدلالاتها."

    text = ics.build(evs, title, desc)
    return Raw(text.encode("utf-8"), "text/calendar; charset=utf-8",
               f"alfalak-{kind}.ics")


def decode_path(raw: str) -> str:
    """
    خوادم HTTP تفكّ المسار بترميز latin-1، فتظهر العربية مشوّهة
    إن أرسلها العميل بايتات خامًا. نُعيدها إلى UTF-8.
    """
    try:
        return raw.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return raw


def is_v1(path: str) -> bool:
    """
    هل هذا مسار الإصدار الأوّل؟

    **حذارِ من الفحص بالنصّ**: Vercel يُعيد كتابة /api/… إلى
    /api/index/… (انظر vercel.json)، فيصير /api/v1/chart عند وصوله
    إلى هنا /api/index/v1/chart — ولا يحوي «/api/v1» أصلًا. فالفحص
    على **مقاطع المسار** لا على النصّ، وإلا عمل محليًّا وسقط منشورًا.
    """
    return "v1" in path.strip("/").split("/")


def dispatch(path: str, query: dict, headers: dict | None = None):
    clean = path.rstrip("/")
    if is_v1(clean):
        return route_v1(clean, query, headers)
    name = clean.split("/")[-1] or "health"
    fn = ROUTES.get(name)
    if not fn:
        raise ApiError(f"مسار غير معروف: {name}. المتاح: " + "، ".join(ROUTES), 404)
    out = fn(query)
    if isinstance(out, dict):
        g = gist.for_route(name, out)
        if g:
            out["gist"] = g
    return out


# ── الملفات الثابتة ──────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml", ".ico": "image/x-icon", ".png": "image/png",
        ".woff2": "font/woff2", ".txt": "text/plain; charset=utf-8"}
STATIC_OK = set(MIME)


def read_static(path: str):
    """
    يخدم صفحات الموقع من الدالة نفسها.
    احتياط: إن عامل Vercel المشروع تطبيقًا كاملًا بدل مزيج ثابت + دوال،
    يبقى الموقع عاملًا بلا تغيير في الإعدادات.
    """
    rel = (path or "/").split("?")[0].lstrip("/")
    if rel in ("", "/"):
        rel = "index.html"
    if "\\" in rel or ".." in rel:
        return None
    ext = os.path.splitext(rel)[1].lower()
    if ext not in STATIC_OK:
        return None
    full = os.path.normpath(os.path.join(ROOT_DIR, rel))
    if not full.startswith(ROOT_DIR) or not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        return f.read(), MIME[ext]


def _err(msg: str, status: int, versioned: bool, trace: str = "") -> dict:
    """
    مغلَّف الخطأ. الإصدار الأوّل يلتزم صيغة معلَنة، والمسارات
    القديمة تبقى على صيغتها لئلّا تنكسر صفحات الموقع.
    """
    if versioned:
        out = {"ok": False, "version": API_VERSION,
               "error": msg, "status": status}
    else:
        out = {"error": msg}
    if trace:
        out["trace"] = trace
    return out


# ── معالج Vercel ─────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body, ctype, status=200):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(decode_path(self.path))
        if "/api/" not in u.path and not u.path.rstrip("/").endswith("/api"):
            hit = read_static(u.path)
            if hit:
                return self._send_bytes(*hit)
        versioned = is_v1(u.path)
        try:
            hdr = {k.lower(): v for k, v in self.headers.items()}
            out = dispatch(u.path, parse_qs(u.query), hdr)
            if isinstance(out, Raw):
                return self._send_file(out)
            self._send(200, out)
        except ApiError as e:
            self._send(e.status, _err(str(e), e.status, versioned))
        except Exception as e:
            self._send(500, _err(f"خطأ داخلي: {e}", 500, versioned,
                                 traceback.format_exc()[-1200:]))

    def _send_file(self, raw):
        self.send_response(raw.status)
        self.send_header("Content-Type", raw.ctype)
        self.send_header("Content-Length", str(len(raw.body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if raw.filename:
            self.send_header("Content-Disposition",
                             f'attachment; filename="{raw.filename}"')
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(raw.body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, *a):
        pass


# ── تشغيل محلي: python api/index.py ─────────────────────────────
if __name__ == "__main__":
    import http.server
    import socketserver
    from functools import partial

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Local(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def do_GET(self):
            u = urlparse(decode_path(self.path))
            if u.path.startswith("/api/"):
                versioned = is_v1(u.path)
                ctype = "application/json; charset=utf-8"
                extra = {}
                try:
                    hdr = {k.lower(): v for k, v in self.headers.items()}
                    out = dispatch(u.path, parse_qs(u.query), hdr)
                    if isinstance(out, Raw):
                        body, status, ctype = out.body, out.status, out.ctype
                        if out.filename:
                            extra["Content-Disposition"] = \
                                f'attachment; filename="{out.filename}"'
                    else:
                        body = json.dumps(out, ensure_ascii=False,
                                          default=str).encode()
                        status = 200
                except ApiError as e:
                    body = json.dumps(_err(str(e), e.status, versioned),
                                      ensure_ascii=False).encode()
                    status = e.status
                except Exception as e:
                    body = json.dumps(
                        _err(str(e), 500, versioned,
                             traceback.format_exc()[-1200:]),
                        ensure_ascii=False, default=str).encode()
                    status = 500
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                for k, v in extra.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
                return
            return super().do_GET()

        def log_message(self, *a):
            pass

    port = int(os.environ.get("PORT", 8000))
    with socketserver.TCPServer(("", port), Local) as httpd:
        print(f"يعمل على http://localhost:{port}")
        httpd.serve_forever()
