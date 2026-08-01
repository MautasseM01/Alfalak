# -*- coding: utf-8 -*-
"""
محرّك الأحداث العامّة — أحداث السماء التي تخصّ الناس جميعًا لا فردًا بعينه.

هذا ما تبني عليه النشرات الشهرية في العالم كلّه، والفرق أنه يُحسَب هنا
لأي شهر من أي سنة، لا يُكتب بيد لشهر واحد.

ما يُرصَد:
  انتقالات البروج   متى يدخل كل كوكب برجًا جديدًا
  محطّات الرجوع     متى يرجع الكوكب ومتى يستقيم، ونافذة الرجوع كاملة
  الزوايا التامّة    بين كل كوكبين، بأوقاتها إلى الدقيقة
  التقميرات        القمر الجديد والبدر والتربيعان
  الكسوف والخسوف   بنوعه وقدره وموضعه
  الفصول           الاعتدالان والانقلابان
  الاحتراق         قرب الكوكب من الشمس: تحت الشعاع، محترق، في قلب الشمس
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import os

import swisseph as swe

_EPHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe")
if os.path.isdir(_EPHE_DIR):
    swe.set_ephe_path(_EPHE_DIR)

from .ephem import SIGNS, UTC, _bisect, _wrap180, to_jd
from . import chart as ch

# ── الأجرام المرصودة في الأحداث العامّة ─────────────────────────
MUNDANE_BODIES = [
    ("الشمس",   swe.SUN),
    ("عطارد",   swe.MERCURY),
    ("الزهرة",  swe.VENUS),
    ("المريخ",  swe.MARS),
    ("المشتري", swe.JUPITER),
    ("زحل",     swe.SATURN),
    ("أورانوس", swe.URANUS),
    ("نبتون",   swe.NEPTUNE),
    ("بلوتو",   swe.PLUTO),
    ("خيرون",   swe.CHIRON),
    ("الرأس",   swe.TRUE_NODE),
    ("ليليث",   swe.MEAN_APOG),
    ("ليليث الحقيقية", swe.OSCU_APOG),
]
# الكواكب التي تُرصَد الزوايا بينها (بلا القمر لسرعته، وله بابه في النشرة اليومية)
ASPECT_BODIES = ["الشمس", "عطارد", "الزهرة", "المريخ", "المشتري",
                 "زحل", "أورانوس", "نبتون", "بلوتو", "خيرون", "ليليث"]

CODE = dict(MUNDANE_BODIES)
CODE["القمر"] = swe.MOON

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

MAJOR_ANGLES = [0, 60, 90, 120, 180]
ALL_ANGLES = [0, 30, 45, 60, 72, 90, 120, 135, 150, 180]

SEASONS = {0: "الاعتدال الربيعي", 90: "الانقلاب الصيفي",
           180: "الاعتدال الخريفي", 270: "الانقلاب الشتوي"}

PHASE_NAMES = {0: "القمر الجديد", 90: "التربيع الأول",
               180: "البدر", 270: "التربيع الأخير"}

# حدود الاحتراق بالدرجات من الشمس
CAZIMI_ORB = 0.2833      # في قلب الشمس (١٧ دقيقة قوسية)
COMBUST_ORB = 8.0        # محترق
UNDER_BEAMS_ORB = 17.0   # تحت الشعاع


# ── أدوات ────────────────────────────────────────────────────────
def lon_at(body: str, dt: datetime) -> float:
    return swe.calc_ut(to_jd(dt), CODE[body], FLAGS)[0][0] % 360.0


def speed_at(body: str, dt: datetime) -> float:
    return swe.calc_ut(to_jd(dt), CODE[body], FLAGS)[0][3]


def _available(body: str) -> bool:
    try:
        swe.calc_ut(to_jd(datetime(2000, 1, 1, tzinfo=UTC)), CODE[body], FLAGS)
        return True
    except Exception:
        return False


def _sign(lon: float) -> str:
    return SIGNS[int(lon // 30) % 12]


@dataclass
class Event:
    when: datetime
    kind: str            # ingress | station | aspect | lunation | eclipse | season | combust
    title: str
    body: str = ""
    other: str = ""
    sign: str = ""
    lon: float = 0.0
    detail: dict = field(default_factory=dict)

    def to_dict(self, tz=None):
        t = self.when.astimezone(tz) if tz else self.when
        return {"when": t.isoformat(), "date": t.strftime("%Y-%m-%d"),
                "time": t.strftime("%H:%M"), "kind": self.kind, "title": self.title,
                "body": self.body, "other": self.other, "sign": self.sign,
                "lon": round(self.lon, 4), **({"degree": ch.dms(self.lon)} if self.lon else {}),
                "detail": self.detail}


# ── انتقالات البروج ─────────────────────────────────────────────
def ingresses(start: datetime, end: datetime, bodies=None) -> list[Event]:
    out = []
    bodies = bodies or [b for b, _ in MUNDANE_BODIES]
    for name in bodies:
        if not _available(name):
            continue
        step = timedelta(hours=6 if name in ("الشمس", "عطارد", "الزهرة", "المريخ") else 24)
        t = start
        prev = int(lon_at(name, t) // 30) % 12
        while t < end:
            t2 = min(t + step, end)
            cur = int(lon_at(name, t2) // 30) % 12
            if cur != prev:
                boundary = (cur * 30.0) % 360.0
                f = lambda x, b=boundary, n=name: _wrap180(lon_at(n, x) - b)
                hit = _bisect(f, t, t2)
                retro = speed_at(name, hit) < 0
                out.append(Event(
                    hit, "ingress",
                    f"{name} يدخل برج {SIGNS[cur]}" + (" راجعًا" if retro else ""),
                    body=name, sign=SIGNS[cur], lon=boundary,
                    detail={"retro": retro,
                            "from": SIGNS[prev],
                            "note": _ingress_note(name, SIGNS[cur], retro)}))
                prev = cur
            t = t2
    return out


def _ingress_note(body: str, sign: str, retro: bool) -> str:
    from .interpret import FUNCTION, MANNER
    fn = FUNCTION.get(body, "")
    mn = MANNER.get(sign, "")
    base = f"{fn} يعمل من الآن {mn}."
    if retro:
        base += " ودخوله راجعًا يعني عودةً إلى ما لم يُستوفَ في هذا البرج."
    return base


# ── محطّات الرجوع والاستقامة ────────────────────────────────────
def stations(start: datetime, end: datetime, bodies=None) -> list[Event]:
    out = []
    bodies = bodies or ["عطارد", "الزهرة", "المريخ", "المشتري",
                        "زحل", "أورانوس", "نبتون", "بلوتو", "خيرون"]
    for name in bodies:
        if not _available(name):
            continue
        step = timedelta(hours=12)
        t = start
        prev = speed_at(name, t)
        while t < end:
            t2 = min(t + step, end)
            cur = speed_at(name, t2)
            if prev * cur < 0:
                f = lambda x, n=name: speed_at(n, x)
                hit = _bisect(f, t, t2)
                going_retro = prev > 0
                L = lon_at(name, hit)
                out.append(Event(
                    hit, "station",
                    f"{name} يبدأ الرجوع" if going_retro else f"{name} يستقيم",
                    body=name, sign=_sign(L), lon=L,
                    detail={"retrograde": going_retro,
                            "note": ("فترة مراجعة وإعادة نظر في ما يحكمه هذا الكوكب، "
                                     "لا فترة توقّف." if going_retro else
                                     "ينتهي وقت المراجعة، وتُستأنف الأمور المؤجّلة.")}))
                prev = cur
                t = hit + timedelta(days=3)
                continue
            prev = cur
            t = t2
    return out


def retrograde_windows(around: datetime, bodies=None, span_days=800) -> list[dict]:
    """نوافذ الرجوع الكاملة التي تتقاطع مع الفترة: من بدء الرجوع إلى الاستقامة."""
    lo = around - timedelta(days=span_days // 2)
    hi = around + timedelta(days=span_days // 2)
    st = sorted(stations(lo, hi, bodies), key=lambda e: e.when)
    out = []
    for i, e in enumerate(st):
        if not e.detail.get("retrograde"):
            continue
        nxt = next((x for x in st[i + 1:]
                    if x.body == e.body and not x.detail.get("retrograde")), None)
        if nxt:
            out.append({"body": e.body, "start": e.when, "end": nxt.when,
                        "start_sign": e.sign, "end_sign": nxt.sign,
                        "days": round((nxt.when - e.when).total_seconds() / 86400, 1)})
    return out


# ── الزوايا التامّة بين الكواكب ─────────────────────────────────
def aspects(start: datetime, end: datetime, bodies=None,
            angles=None, step_hours: int = 12) -> list[Event]:
    bodies = [b for b in (bodies or ASPECT_BODIES) if _available(b)]
    angles = angles or MAJOR_ANGLES
    step = timedelta(hours=step_hours)

    n = int((end - start) / step) + 2
    grid = [start + step * i for i in range(n)]
    lons = {b: [lon_at(b, t) for t in grid] for b in bodies}

    out = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            diffs = [(lons[a][k] - lons[b][k]) % 360.0 for k in range(len(grid))]
            for ang in angles:
                targets = [ang] if ang in (0, 180) else [ang, 360 - ang]
                for tgt in targets:
                    g = [_wrap180(d - tgt) for d in diffs]
                    for k in range(len(g) - 1):
                        if g[k] * g[k + 1] < 0 and abs(g[k]) < 40 and abs(g[k + 1]) < 40:
                            f = (lambda x, aa=a, bb=b, tt=tgt:
                                 _wrap180(((lon_at(aa, x) - lon_at(bb, x)) % 360.0) - tt))
                            hit = _bisect(f, grid[k], grid[k + 1])
                            if not (start <= hit <= end):
                                continue
                            name, polarity, major, sym = ch.ASPECT_BY_ANGLE[ang]
                            La = lon_at(a, hit)
                            out.append(Event(
                                hit, "aspect",
                                f"{a} {sym} {b} — {name}",
                                body=a, other=b, sign=_sign(La), lon=La,
                                detail={"aspect": name, "angle": ang, "symbol": sym,
                                        "polarity": polarity, "major": major,
                                        "a_sign": _sign(La), "b_sign": _sign(lon_at(b, hit)),
                                        "note": _aspect_note(a, b, name, polarity)}))
    return out


def _aspect_note(a: str, b: str, aspect: str, polarity: str) -> str:
    from .interpret import KEYWORD, ASPECT_QUALITY
    ka, kb = KEYWORD.get(a, a), KEYWORD.get(b, b)
    return f"{ka} ({a}) و{kb} ({b}) {ASPECT_QUALITY.get(aspect, '')}"


# ── التقميرات: القمر الجديد والبدر والتربيعان ───────────────────
def lunations(start: datetime, end: datetime, quarters: bool = True) -> list[Event]:
    out = []
    step = timedelta(hours=6)
    phases = [0, 90, 180, 270] if quarters else [0, 180]
    t = start - timedelta(days=1)
    stop = end + timedelta(days=1)

    def elong(x):
        return (lon_at("القمر", x) - lon_at("الشمس", x)) % 360.0

    prev_t, prev_e = t, elong(t)
    while t < stop:
        t2 = t + step
        e2 = elong(t2)
        for ph in phases:
            f = lambda x, p=ph: _wrap180(elong(x) - p)
            f1, f2 = f(prev_t), f(t2)
            if f1 * f2 < 0 and abs(f1) < 40 and abs(f2) < 40:
                hit = _bisect(f, prev_t, t2)
                if not (start <= hit <= end):
                    continue
                L = lon_at("القمر", hit)
                sun = lon_at("الشمس", hit)
                pos = sun if ph in (0,) else L
                out.append(Event(
                    hit, "lunation", f"{PHASE_NAMES[ph]} في برج {_sign(pos)}",
                    body="القمر", sign=_sign(pos), lon=pos,
                    detail={"phase": PHASE_NAMES[ph], "angle": ph,
                            "moon_lon": L, "sun_lon": sun,
                            "moon_sign": _sign(L), "sun_sign": _sign(sun),
                            "note": _lunation_note(ph, _sign(pos))}))
        prev_t, prev_e = t2, e2
        t = t2
    return sorted(out, key=lambda e: e.when)


def _lunation_note(phase: int, sign: str) -> str:
    from .interpret import MANNER
    mn = MANNER.get(sign, "")
    if phase == 0:
        return (f"بداية دورة قمرية جديدة {mn}. وقت النيّة والبذر لا الحصاد، "
                f"وما يُبدأ فيه ينمو مع نموّ القمر.")
    if phase == 180:
        return (f"ذروة الدورة واكتمال ما بُذر. تظهر الحقائق وتشتدّ الانفعالات {mn}. "
                f"وقت الحصاد والوضوح، لا وقت البدء.")
    if phase == 90:
        return "أزمة نموّ: ما بدأته يحتاج جهدًا وقرارًا ليستمرّ."
    return "أزمة وعي: تُراجَع الدورة وتُطرَح ما لم يعد نافعًا قبل بداية جديدة."


# ── الكسوف والخسوف ──────────────────────────────────────────────
ECLIPSE_KIND = {
    swe.ECL_TOTAL: "كلّي", swe.ECL_ANNULAR: "حلقي", swe.ECL_PARTIAL: "جزئي",
    swe.ECL_ANNULAR_TOTAL: "هجين", swe.ECL_PENUMBRAL: "شبه ظلّي",
}


def eclipses(start: datetime, end: datetime) -> list[Event]:
    out = []
    jd0 = to_jd(start)
    jd_end = to_jd(end)

    # كسوف الشمس
    jd = jd0
    while jd < jd_end:
        try:
            ret, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0)
        except Exception:
            break
        peak = tret[0]
        if peak > jd_end:
            break
        when = _from_jd(peak)
        kind = next((v for k, v in ECLIPSE_KIND.items() if ret & k), "جزئي")
        L = lon_at("الشمس", when)
        out.append(Event(
            when, "eclipse", f"كسوف شمسي {kind} في برج {_sign(L)}",
            body="الشمس", sign=_sign(L), lon=L,
            detail={"eclipse": "شمسي", "kind": kind,
                    "note": ("الكسوف قمر جديد مشدَّد: بداية دورة تمتدّ آثارها أشهرًا. "
                             "ما يُفتح فيه من باب يبقى مفتوحًا طويلًا، وأثره يظهر "
                             "في الأسابيع التالية لا في يومه غالبًا.")}))
        jd = peak + 20

    # خسوف القمر
    jd = jd0
    while jd < jd_end:
        try:
            ret, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0)
        except Exception:
            break
        peak = tret[0]
        if peak > jd_end:
            break
        when = _from_jd(peak)
        kind = next((v for k, v in ECLIPSE_KIND.items() if ret & k), "جزئي")
        L = lon_at("القمر", when)
        out.append(Event(
            when, "eclipse", f"خسوف قمري {kind} في برج {_sign(L)}",
            body="القمر", sign=_sign(L), lon=L,
            detail={"eclipse": "قمري", "kind": kind,
                    "note": ("الخسوف بدر مشدَّد: انكشاف وانقضاء. يُنهي ما استُنفد، "
                             "ويُظهر ما كان مستورًا. لا يُبدأ فيه، ويُترك فيه ما يُترك.")}))
        jd = peak + 20

    return sorted(out, key=lambda e: e.when)


def _from_jd(jd: float) -> datetime:
    y, m, d, h = swe.revjul(jd)
    return datetime(y, m, d, tzinfo=UTC) + timedelta(hours=h)


# ── الفصول ───────────────────────────────────────────────────────
def seasons(start: datetime, end: datetime) -> list[Event]:
    out = []
    step = timedelta(days=1)
    t = start
    while t < end:
        t2 = min(t + step, end)
        for deg, name in SEASONS.items():
            f = lambda x, d=deg: _wrap180(lon_at("الشمس", x) - d)
            if f(t) * f(t2) < 0 and abs(f(t)) < 20:
                hit = _bisect(f, t, t2)
                out.append(Event(hit, "season", name, body="الشمس",
                                 sign=_sign(deg), lon=float(deg),
                                 detail={"note": "دخول الشمس وتدًا من أوتاد السنة، "
                                                 "وهي خريطة الفصل كلّه."}))
        t = t2
    return sorted(out, key=lambda e: e.when)


# ── الاحتراق ────────────────────────────────────────────────────
def combustions(start: datetime, end: datetime) -> list[Event]:
    """دخول الكواكب وخروجها من شعاع الشمس."""
    out = []
    step = timedelta(days=1)
    for name in ("عطارد", "الزهرة", "المريخ", "المشتري", "زحل"):
        t = start
        prev_state = None
        while t < end:
            d = abs(_wrap180(lon_at(name, t) - lon_at("الشمس", t)))
            state = ("في قلب الشمس" if d <= CAZIMI_ORB else
                     "محترق" if d <= COMBUST_ORB else
                     "تحت الشعاع" if d <= UNDER_BEAMS_ORB else None)
            if state != prev_state and prev_state is not None:
                L = lon_at(name, t)
                if state:
                    title = f"{name} يصير {state}"
                    note = {"في قلب الشمس": "أقوى حالات الكوكب عند القدماء: "
                                            "يجلس في عرش الشمس فيقوى أثره جدًّا.",
                            "محترق": "يُحرقه شعاع الشمس فيضعف ويخفى أثره.",
                            "تحت الشعاع": "يدخل في شعاع الشمس فيبدأ ضعفه."}[state]
                else:
                    title = f"{name} يخرج من شعاع الشمس"
                    note = "يستعيد الكوكب ظهوره وقوّته بعد خفاء."
                out.append(Event(t, "combust", title, body=name,
                                 sign=_sign(L), lon=L,
                                 detail={"state": state, "note": note}))
            prev_state = state
            t += step
    return out


# ── تجميع الشهر ─────────────────────────────────────────────────
def month_events(year: int, month: int, tzname: str = "UTC",
                 minor_aspects: bool = False, quarters: bool = True) -> dict:
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tzname)
    start = datetime(year, month, 1, tzinfo=tz)
    nm = (month % 12) + 1
    ny = year + (1 if month == 12 else 0)
    end = datetime(ny, nm, 1, tzinfo=tz)
    s_utc, e_utc = start.astimezone(UTC), end.astimezone(UTC)

    ang = ALL_ANGLES if minor_aspects else MAJOR_ANGLES
    evs = (ingresses(s_utc, e_utc)
           + stations(s_utc, e_utc)
           + aspects(s_utc, e_utc, angles=ang)
           + lunations(s_utc, e_utc, quarters=quarters)
           + eclipses(s_utc, e_utc)
           + seasons(s_utc, e_utc)
           + combustions(s_utc, e_utc))
    evs.sort(key=lambda e: e.when)

    # الكسوف يُغني عن التقمير الذي يقع فيه
    ecl_times = [e.when for e in evs if e.kind == "eclipse"]
    evs = [e for e in evs
           if not (e.kind == "lunation"
                   and any(abs((e.when - x).total_seconds()) < 7200 for x in ecl_times))]

    return {
        "year": year, "month": month, "tz": tzname,
        "start": start.isoformat(), "end": end.isoformat(),
        "events": [e.to_dict(tz) for e in evs],
        "retrograde_windows": [
            {**w, "start": w["start"].astimezone(tz).isoformat(),
             "end": w["end"].astimezone(tz).isoformat()}
            for w in retrograde_windows(s_utc + (e_utc - s_utc) / 2)
            if w["start"] <= e_utc and w["end"] >= s_utc],
    }
