# -*- coding: utf-8 -*-
"""
محرّك الخرائط الفلكية — الخريطة الكاملة.
كل المواقع ظاهرية (geocentric apparent) على المنطقة البروجية الاستوائية.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import swisseph as swe

from . import dignities as dig
from . import ephem, parts, patterns, stars
from .ephem import SIGNS, UTC, to_jd, _wrap180

_EPHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe")
if os.path.isdir(_EPHE_DIR):
    swe.set_ephe_path(_EPHE_DIR)

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# ── الأجرام ──────────────────────────────────────────────────────
# (الاسم، ثابت المكتبة، الرمز، أساسي؟، صنف الوجاج)
BODIES = [
    ("الشمس",    swe.SUN,       "☉", True,  "نيّر"),
    ("القمر",    swe.MOON,      "☾", True,  "نيّر"),
    ("عطارد",    swe.MERCURY,   "☿", True,  "شخصي"),
    ("الزهرة",   swe.VENUS,     "♀", True,  "شخصي"),
    ("المريخ",   swe.MARS,      "♂", True,  "شخصي"),
    ("المشتري",  swe.JUPITER,   "♃", True,  "اجتماعي"),
    ("زحل",      swe.SATURN,    "♄", True,  "اجتماعي"),
    ("أورانوس",  swe.URANUS,    "♅", False, "خارجي"),
    ("نبتون",    swe.NEPTUNE,   "♆", False, "خارجي"),
    ("بلوتو",    swe.PLUTO,     "♇", False, "خارجي"),
    ("الرأس",    swe.TRUE_NODE, "☊", False, "نقطة"),
    # ليليث نقطتان لا واحدة: الوسطى تسير بانتظام وعليها عمل أكثر البرامج
    # (ومنها Astrodienst)، والحقيقية تتذبذب وعليها عمل Astrotheme.
    ("ليليث",           swe.MEAN_APOG, "⚸", False, "نقطة"),
    ("ليليث الحقيقية",  swe.OSCU_APOG, "⚸", False, "نقطة"),
    ("خيرون",    swe.CHIRON,    "⚷", False, "نقطة"),
]
BODY_SYMBOL = {n: s for n, _, s, _, _ in BODIES}
BODY_CLASS = {n: c for n, _, _, _, c in BODIES}
BODY_CLASS["الذنب"] = "نقطة"
SIGN_SYMBOL = dict(zip(SIGNS, "♈♉♊♋♌♍♎♏♐♑♒♓"))

ANGLES = ["الطالع", "وسط السماء", "الغارب", "وتد الأرض"]
ANGLE_SYMBOL = {"الطالع": "ASC", "وسط السماء": "MC", "الغارب": "DSC", "وتد الأرض": "IC"}

# ── أنظمة البيوت ─────────────────────────────────────────────────
HOUSE_SYSTEMS = {
    "whole":       {"code": b"W", "name": "البيوت الكاملة",
                    "note": "نظام المنجّمين العرب الأوائل: كل برج بيت كامل، والطالع في البيت الأول."},
    "alcabitius":  {"code": b"B", "name": "القبّاني",
                    "note": "نظام أبي الصقر القبيصي، وعليه عمل أهل بغداد. يقسّم قوس نهار الطالع."},
    "placidus":    {"code": b"P", "name": "بلاسيدوس",
                    "note": "النظام المعاصر الأشهر، وعليه Astrotheme. يقسّم الزمن لا المكان."},
    "koch":        {"code": b"K", "name": "كوخ",
                    "note": "قريب من بلاسيدوس، أدقّ عند خطوط العرض المتوسّطة."},
    "regiomontanus": {"code": b"R", "name": "ريجومونتانوس",
                    "note": "نظام قرون وسطى، يعتمده أهل المسائل والاختيارات."},
    "campanus":    {"code": b"C", "name": "كامبانوس",
                    "note": "يقسّم دائرة الوتد الأول تقسيمًا متساويًا في الفضاء."},
    "porphyry":    {"code": b"O", "name": "بورفيري",
                    "note": "أقدم الأنظمة الرباعية: يقسّم ما بين الأوتاد أثلاثًا متساوية."},
    "equal":       {"code": b"E", "name": "البيوت المتساوية",
                    "note": "ثلاثون درجة من الطالع، بلا حساب لخط العرض."},
}
# أنظمة تنهار قرب القطبين
POLAR_FRAGILE = {"placidus", "koch", "alcabitius", "regiomontanus"}
POLAR_LIMIT = 66.0

# ── الزوايا ──────────────────────────────────────────────────────
# (الاسم، الدرجة، الطبع، رئيسية؟، الرمز)
ASPECT_DEFS = [
    ("اقتران",     0,   "محايدة", True,  "☌"),
    ("توازي ناقص", 30,  "إيجابية", False, "⚺"),
    ("نصف تربيع",  45,  "سلبية",  False, "∠"),
    ("تسديس",      60,  "إيجابية", True,  "⚹"),
    ("خُمسي",       72,  "إيجابية", False, "Q"),
    ("تربيع",      90,  "سلبية",  True,  "□"),
    ("تثليث",      120, "إيجابية", True,  "△"),
    ("تربيع ونصف", 135, "سلبية",  False, "⚼"),
    ("سُدسي ناقص",  150, "سلبية",  False, "⚻"),
    ("تقابل",      180, "سلبية",  True,  "☍"),
]
ASPECT_BY_ANGLE = {a: (n, p, m, s) for n, a, p, m, s in ASPECT_DEFS}
ASPECT_SYMBOL = {n: s for n, a, p, m, s in ASPECT_DEFS}

# الوجاج الأساسي لكل زاوية بالدرجات
ASPECT_ORB = {0: 8.0, 30: 1.5, 45: 2.0, 60: 4.0, 72: 1.5,
              90: 6.0, 120: 6.0, 135: 2.0, 150: 3.0, 180: 8.0}
# معامل يُضرب بالوجاج بحسب صنف الجرم
CLASS_FACTOR = {"نيّر": 1.25, "شخصي": 1.0, "اجتماعي": 0.95, "خارجي": 0.85, "نقطة": 0.6}
ANGLE_ORB = 5.0

ELEMENT = dig.ELEMENT
MODE = {"الحمل": "منقلب", "السرطان": "منقلب", "الميزان": "منقلب", "الجدي": "منقلب",
        "الثور": "ثابت", "الأسد": "ثابت", "العقرب": "ثابت", "الدلو": "ثابت",
        "الجوزاء": "متغيّر", "العذراء": "متغيّر", "القوس": "متغيّر", "الحوت": "متغيّر"}
SIGN_RULER = dig.DOMICILE

HOUSE_NAMES = [
    "الأول: النفس والبدن والمظهر",
    "الثاني: المال والمكتسبات",
    "الثالث: الإخوة والأسفار القريبة والكلام",
    "الرابع: الأصل والبيت والوالد",
    "الخامس: الولد واللذّة والإبداع",
    "السادس: المرض والخدمة والعمل اليومي",
    "السابع: الشريك والخصم والزواج",
    "الثامن: الموت والميراث ومال الغير",
    "التاسع: السفر البعيد والدين والعلم",
    "العاشر: المرتبة والعمل والسلطان",
    "الحادي عشر: الأصدقاء والرجاء",
    "الثاني عشر: الأعداء والخفاء والانعزال",
]


# ── تنسيق الدرجات ────────────────────────────────────────────────
def dms(longitude: float) -> dict:
    s = int(longitude // 30) % 12
    within = longitude % 30
    d = int(within)
    m_f = (within - d) * 60
    m, sec = int(m_f), int(round((m_f - int(m_f)) * 60))
    if sec == 60:
        sec, m = 0, m + 1
    if m == 60:
        m, d = 0, d + 1
    dd, mm = int(within), int(round((within - int(within)) * 60))
    if mm == 60:
        mm, dd = 0, dd + 1
    if dd == 30:
        dd, mm = 29, 59
    return {"sign": SIGNS[s], "sign_symbol": SIGN_SYMBOL[SIGNS[s]],
            "deg": d, "min": m, "sec": sec,
            "text": f"{dd}° {mm:02d}′ {SIGNS[s]}", "short": f"{dd}°{mm:02d}′"}


# ── الأجرام والبيوت ──────────────────────────────────────────────
def _body_positions(jd: float):
    out = []
    for name, code, sym, core, cls in BODIES:
        try:
            x = swe.calc_ut(jd, code, FLAGS)[0]
        except Exception:
            continue
        lon_ = x[0] % 360.0
        out.append({"name": name, "symbol": sym, "core": core, "class": cls,
                    "lon": lon_, "lat": x[1], "speed": x[3],
                    "retro": x[3] < 0, **dms(lon_)})
    head = next((b for b in out if b["name"] == "الرأس"), None)
    if head:
        t = (head["lon"] + 180.0) % 360.0
        out.append({"name": "الذنب", "symbol": "☋", "core": False, "class": "نقطة",
                    "lon": t, "lat": -head["lat"], "speed": head["speed"],
                    "retro": head["retro"], **dms(t)})
    return out


def _houses(jd: float, lat: float, lon: float, system: str):
    """يُرجع (رؤوس البيوت، الأوتاد، تحذيرات)."""
    warnings = []
    used = system
    if system in POLAR_FRAGILE and abs(lat) >= POLAR_LIMIT:
        warnings.append(
            f"نظام {HOUSE_SYSTEMS[system]['name']} لا يصحّ عند خط عرض {lat:.1f}° "
            f"لأن بعض الدرجات لا تطلع هناك أصلًا. حُسبت البيوت بنظام بورفيري بدلًا منه.")
        used = "porphyry"
    cusps, ascmc = swe.houses(jd, lat, lon, HOUSE_SYSTEMS[used]["code"])
    cusps = [c % 360.0 for c in cusps[:12]]
    asc, mc = ascmc[0] % 360.0, ascmc[1] % 360.0
    if used == "whole":
        cusps = [((int(asc // 30) + i) % 12) * 30.0 for i in range(12)]
    angles = {"الطالع": asc, "وسط السماء": mc,
              "الغارب": (asc + 180.0) % 360.0, "وتد الأرض": (mc + 180.0) % 360.0}
    return cusps, angles, warnings, used


def house_of(longitude: float, cusps: list) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        span = (b - a) % 360.0 or 360.0
        if (longitude - a) % 360.0 < span:
            return i + 1
    return 1


# ── الزوايا ──────────────────────────────────────────────────────
def orb_for(angle: int, a_class: str, b_class: str) -> float:
    base = ASPECT_ORB[angle]
    return base * max(CLASS_FACTOR.get(a_class, 1.0), CLASS_FACTOR.get(b_class, 1.0))


def _applying(a: dict, b: dict, angle: int) -> bool:
    now = abs(abs(_wrap180(a["lon"] - b["lon"])) - angle)
    later = abs(abs(_wrap180((a["lon"] + a["speed"] / 24.0)
                             - (b["lon"] + b["speed"] / 24.0))) - angle)
    return later < now


def find_aspects(bodies: list, minor: bool = True):
    # ــ **ليليث الحقيقية لا تُولّد زوايا** ــ
    #
    # كنّا نستبعد اقتران الليليثَين ببعضهما وحده، وهو ناقص: فكلٌّ
    # منهما يُزاوي سائر الأجرام على حدة، **وهما نقطةٌ واحدة بحسابين**
    # (أوج القمر: متوسّطًا وحقيقيًّا). فيخرج للزائر سطران متطابقان
    # مئةً في المئة: «عطارد – ليليث» و«عطارد – ليليث الحقيقية».
    #
    # كشفه فحصُ التكرار عبر العائلات — ولم يكشفه أيٌّ من حرّاس
    # العائلات، لأنه تكرارٌ **داخل** عائلة الزوايا ولم يكن لها حارس.
    #
    # والموضع يبقى في الجدول وفي العجلة ليرى القارئ الفرق بين
    # الحسابين، لكن الزوايا تُحسَب من المتوسّطة وحدها كما هو
    # المتعارَف.
    real = [b for b in bodies
            if b["name"] not in ("الذنب", "ليليث الحقيقية")]
    out = []
    for i in range(len(real)):
        for j in range(i + 1, len(real)):
            a, b = real[i], real[j]
            sep = abs(_wrap180(a["lon"] - b["lon"]))
            best = None
            for name, angle, polarity, major, sym in ASPECT_DEFS:
                if not major and not minor:
                    continue
                omax = orb_for(angle, a["class"], b["class"])
                orb = abs(sep - angle)
                if orb <= omax and (best is None or orb < best["orb"]):
                    best = {"a": a["name"], "b": b["name"], "name": name, "angle": angle,
                            "polarity": polarity, "major": major, "symbol": sym,
                            "orb": round(orb, 2), "orb_max": round(omax, 2),
                            "exact": orb < 0.5,
                            "strength": round(max(0.0, 1 - orb / omax), 2),
                            "applying": _applying(a, b, angle)}
            if best:
                out.append(best)
    out.sort(key=lambda x: x["orb"])
    return out


def find_angle_aspects(bodies: list, angles: dict, minor: bool = False):
    out = []
    for aname in ("الطالع", "وسط السماء"):
        av = angles[aname]
        for b in bodies:
            if b["name"] == "الذنب":
                continue
            sep = abs(_wrap180(b["lon"] - av))
            for name, angle, polarity, major, sym in ASPECT_DEFS:
                if not major and not minor:
                    continue
                orb = abs(sep - angle)
                if orb <= ANGLE_ORB:
                    out.append({"a": b["name"], "b": aname, "name": name, "angle": angle,
                                "polarity": polarity, "symbol": sym, "major": major,
                                "orb": round(orb, 2), "exact": orb < 0.5,
                                "strength": round(max(0.0, 1 - orb / ANGLE_ORB), 2),
                                "applying": None})
                    break
    out.sort(key=lambda x: x["orb"])
    return out


# ── الغالب ───────────────────────────────────────────────────────
def _dominants(bodies: list, angles: dict):
    weights = {"الشمس": 4, "القمر": 4, "عطارد": 2.5, "الزهرة": 2.5, "المريخ": 2.5,
               "المشتري": 2.5, "زحل": 2.5, "أورانوس": 1.5, "نبتون": 1.5, "بلوتو": 1.5,
               "الرأس": 1, "الذنب": 0, "ليليث": 0.5, "ليليث الحقيقية": 0, "خيرون": 0.5}
    el = {"ناري": 0.0, "ترابي": 0.0, "هوائي": 0.0, "مائي": 0.0}
    md = {"منقلب": 0.0, "ثابت": 0.0, "متغيّر": 0.0}
    pl = {}
    for b in bodies:
        w = weights.get(b["name"], 1)
        if not w:
            continue
        for av in angles.values():
            if abs(_wrap180(b["lon"] - av)) <= 8:
                w += 2
                break
        el[ELEMENT[b["sign"]]] += w
        md[MODE[b["sign"]]] += w
        ruler = SIGN_RULER[b["sign"]]
        pl[ruler] = pl.get(ruler, 0) + w * 0.5
        if weights.get(b["name"], 0) >= 1.5:
            pl[b["name"]] = pl.get(b["name"], 0) + w
    asc_sign = SIGNS[int(angles["الطالع"] // 30)]
    asc_ruler = SIGN_RULER[asc_sign]
    pl[asc_ruler] = pl.get(asc_ruler, 0) + 6
    el[ELEMENT[asc_sign]] += 4
    md[MODE[asc_sign]] += 4

    def pct(d):
        t = sum(d.values()) or 1
        return {k: round(v / t * 100, 1) for k, v in sorted(d.items(), key=lambda x: -x[1])}

    return {"elements": pct(el), "modes": pct(md), "planets": pct(pl),
            "asc_sign": asc_sign, "asc_ruler": asc_ruler}


# ── الخريطة الكاملة ──────────────────────────────────────────────
def compute(when_local: datetime, lat: float, lon: float,
            house_system: str = "whole", tzname: str = "",
            minor_aspects: bool = True, tz_info: dict | None = None) -> dict:
    if when_local.tzinfo is None:
        raise ValueError("الوقت يجب أن يحمل منطقته الزمنية")
    when_utc = when_local.astimezone(UTC)
    jd = to_jd(when_utc)
    year = when_utc.year + (when_utc.timetuple().tm_yday / 365.25)

    bodies = _body_positions(jd)
    cusps, angles, warns, used_system = _houses(jd, lat, lon, house_system)

    sun = next(b for b in bodies if b["name"] == "الشمس")
    is_day = dig.is_day_chart(sun["lon"], angles["الطالع"])

    for b in bodies:
        b["house"] = house_of(b["lon"], cusps)
        b["element"] = ELEMENT[b["sign"]]
        b["mode"] = MODE[b["sign"]]
        b["ruler"] = SIGN_RULER[b["sign"]]
        if b["name"] in dig.PLANETS7:
            e = dig.evaluate(b["name"], b["lon"], is_day)
            b["dignity"] = e["summary"]
            b["dignity_score"] = e["score"]
            b["dignity_note"] = e["note"]
            b["dignity_states"] = e["states"]
        else:
            b["dignity"] = None
            b["dignity_score"] = None

    aspects = find_aspects(bodies, minor=minor_aspects)
    angle_aspects = find_angle_aspects(bodies, angles)

    # السهام
    body_lons = {b["name"]: b["lon"] for b in bodies}
    house_rulers = {i + 1: body_lons.get(SIGN_RULER[SIGNS[int(c // 30)]])
                    for i, c in enumerate(cusps)}
    lots = parts.compute(body_lons, angles, cusps, house_rulers, is_day)
    for L in lots:
        L.update(dms(L["lon"]))
        L["house"] = house_of(L["lon"], cusps)

    fortune = next((L["lon"] for L in lots if L["key"] == "fortune"), None)
    almuten = dig.almuten_of_chart(bodies, angles, is_day, fortune)

    shapes = patterns.detect(
        [b for b in bodies if b["core"] or b["name"] in ("أورانوس", "نبتون", "بلوتو")],
        [a for a in aspects if a["major"]], cusps)

    star_hits = stars.conjunctions(bodies, year, orb=1.0, angles=angles)

    houses = {
        "system": used_system,
        "requested_system": house_system,
        "system_name": HOUSE_SYSTEMS[used_system]["name"],
        "system_note": HOUSE_SYSTEMS[used_system]["note"],
        "cusps": [{"house": i + 1, "lon": c, "name": HOUSE_NAMES[i],
                   "ruler": SIGN_RULER[SIGNS[int(c // 30)]], **dms(c)}
                  for i, c in enumerate(cusps)],
    }
    angles_out = {k: {"lon": v, "symbol": ANGLE_SYMBOL[k], **dms(v)} for k, v in angles.items()}

    moon = next(b for b in bodies if b["name"] == "القمر")
    m_idx = ephem.mansion_index(moon["lon"])
    from .tables import MANSIONS, MANSION_MOOD
    mn, mood, desc, good = MANSIONS[m_idx - 1]

    out = {
        "when_utc": when_utc.isoformat(),
        "when_local": when_local.isoformat(),
        "tz": tzname or str(when_local.tzinfo),
        "lat": lat, "lon": lon,
        "sect": "نهارية" if is_day else "ليلية",
        "sect_note": ("الشمس فوق الأفق، فالخريطة نهارية: تُقدَّم الشمس وزحل والمشتري."
                      if is_day else
                      "الشمس تحت الأفق، فالخريطة ليلية: يُقدَّم القمر والزهرة والمريخ."),
        "bodies": bodies,
        "houses": houses,
        "angles": angles_out,
        "aspects": aspects,
        "angle_aspects": angle_aspects,
        "lots": lots,
        "almuten": almuten,
        "patterns": shapes,
        "stars": star_hits,
        "dominants": _dominants(bodies, angles),
        "moon": {
            "phase": ephem.moon_phase(when_utc),
            "mansion": {"index": m_idx, "name": mn, "mood": mood,
                        "mood_text": MANSION_MOOD[mood], "desc": desc, "good_for": good},
        },
        "warnings": warns + ((tz_info or {}).get("warnings") or []),
        "notes": (tz_info or {}).get("notes") or [],
        "tz_mode": (tz_info or {}).get("mode", "standard"),
        "tz_offset": (tz_info or {}).get("offset_text", ""),
        "available_systems": {k: v["name"] for k, v in HOUSE_SYSTEMS.items()},
        "chiron_available": any(b["name"] == "خيرون" for b in bodies),
    }
    return out
