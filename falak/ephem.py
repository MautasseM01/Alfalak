# -*- coding: utf-8 -*-
"""
محرك الحسابات — المواقع الظاهرية للكواكب كما تُرى من موقف الراصد،
محسوبة بمكتبة Swiss Ephemeris على المنطقة البروجية الاستوائية.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from . import config

UTC = timezone.utc

SIGNS = [
    "الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء",
    "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت",
]

BODIES = {
    "الشمس": swe.SUN,
    "القمر": swe.MOON,
    "عطارد": swe.MERCURY,
    "الزهرة": swe.VENUS,
    "المريخ": swe.MARS,
    "المشتري": swe.JUPITER,
    "زحل": swe.SATURN,
    "أورانوس": swe.URANUS,
    "نبتون": swe.NEPTUNE,
    "بلوتو": swe.PLUTO,
}

MANSION_ARC = 360.0 / 28.0  # 12° 51' 25.7"

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


# ── أدوات الوقت ──────────────────────────────────────────────────
def to_jd(dt: datetime) -> float:
    u = dt.astimezone(UTC)
    return swe.julday(u.year, u.month, u.day,
                      u.hour + u.minute / 60 + u.second / 3600 + u.microsecond / 3.6e9)


_LON_CACHE: dict = {}


def lon_of(body: str, dt: datetime) -> float:
    """الطول البروجي الظاهري بالدرجات [0, 360)."""
    jd = to_jd(dt)
    key = (body, round(jd, 9))
    v = _LON_CACHE.get(key)
    if v is None:
        v = swe.calc_ut(jd, BODIES[body], FLAGS)[0][0] % 360.0
        if len(_LON_CACHE) > 400000:
            _LON_CACHE.clear()
        _LON_CACHE[key] = v
    return v


def speed_of(body: str, dt: datetime) -> float:
    """السرعة اليومية بالدرجات (سالبة = رجوع)."""
    return swe.calc_ut(to_jd(dt), BODIES[body], FLAGS)[0][3]


def is_retrograde(body: str, dt: datetime) -> bool:
    return speed_of(body, dt) < 0


# ── إيجاد جذور دقيقة بالتنصيف ───────────────────────────────────
def _bisect(f, lo: datetime, hi: datetime, iters: int = 46) -> datetime:
    flo = f(lo)
    for _ in range(iters):
        mid = lo + (hi - lo) / 2
        fm = f(mid)
        if flo * fm <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return lo + (hi - lo) / 2


def _scan(f, start: datetime, end: datetime, step_min: int = 6, max_jump: float = 60.0):
    """
    يُرجع أوقات تغيّر إشارة f بين start و end.
    max_jump يمنع التقاط «قفزة» الالتفاف عند ±180° بدل جذر حقيقي.
    """
    out = []
    step = timedelta(minutes=step_min)
    t, ft = start, f(start)
    while t < end:
        t2 = min(t + step, end)
        f2 = f(t2)
        if ft * f2 < 0 and abs(ft) < max_jump and abs(f2) < max_jump:
            out.append(_bisect(f, t, t2))
        t, ft = t2, f2
    return out


def _wrap180(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


# ── انتقال القمر بين البروج ─────────────────────────────────────
def sign_index(longitude: float) -> int:
    return int(longitude // 30) % 12


def moon_ingresses(start: datetime, end: datetime):
    """[(الوقت, اسم البرج الجديد)] لكل دخول القمر برجًا بين الوقتين."""
    events = []
    pad = timedelta(hours=2)
    t = start - pad
    step = timedelta(minutes=20)
    prev_i = sign_index(lon_of("القمر", t))
    while t < end + pad:
        t2 = t + step
        i2 = sign_index(lon_of("القمر", t2))
        if i2 != prev_i:
            boundary = (i2 * 30.0) % 360.0
            f = lambda x, b=boundary: _wrap180(lon_of("القمر", x) - b)
            hit = _bisect(f, t, t2)
            if start <= hit <= end:
                events.append((hit, SIGNS[i2]))
            prev_i = i2
        t = t2
    return events


def next_moon_ingress(after: datetime):
    """أول دخول القمر برجًا بعد الوقت المعطى."""
    cur = sign_index(lon_of("القمر", after))
    boundary = ((cur + 1) * 30.0) % 360.0
    f = lambda x: _wrap180(lon_of("القمر", x) - boundary)
    lo = after
    hi = after + timedelta(hours=1)
    while f(lo) * f(hi) > 0 and hi < after + timedelta(days=4):
        lo, hi = hi, hi + timedelta(hours=1)
    return _bisect(f, lo, hi), SIGNS[(cur + 1) % 12]


def prev_moon_ingress(before: datetime):
    """آخر دخول للقمر في برجه الحالي."""
    cur = sign_index(lon_of("القمر", before))
    boundary = (cur * 30.0) % 360.0
    f = lambda x: _wrap180(lon_of("القمر", x) - boundary)
    hi = before
    lo = before - timedelta(hours=1)
    while f(lo) * f(hi) > 0 and lo > before - timedelta(days=4):
        hi, lo = lo, lo - timedelta(hours=1)
    return _bisect(f, lo, hi), SIGNS[cur]


# ── المنازل القمرية ──────────────────────────────────────────────
def mansion_index(longitude: float) -> int:
    """رقم المنزلة 1..28"""
    shifted = (longitude - config.MANSION_SHIFT * MANSION_ARC) % 360.0
    return int(shifted // MANSION_ARC) + 1


def mansion_bounds(idx: int):
    """(بداية، نهاية) المنزلة بالدرجات."""
    a = ((idx - 1) * MANSION_ARC + config.MANSION_SHIFT * MANSION_ARC) % 360.0
    return a, (a + MANSION_ARC) % 360.0


def mansion_span(at: datetime):
    """(رقم المنزلة، وقت الدخول، وقت الخروج) للمنزلة التي فيها القمر."""
    idx = mansion_index(lon_of("القمر", at))
    start_deg, end_deg = mansion_bounds(idx)

    f_end = lambda x: _wrap180(lon_of("القمر", x) - end_deg)
    lo, hi = at, at + timedelta(hours=2)
    while f_end(lo) * f_end(hi) > 0 and hi < at + timedelta(days=3):
        lo, hi = hi, hi + timedelta(hours=2)
    t_end = _bisect(f_end, lo, hi)

    f_start = lambda x: _wrap180(lon_of("القمر", x) - start_deg)
    hi2, lo2 = at, at - timedelta(hours=2)
    while f_start(lo2) * f_start(hi2) > 0 and lo2 > at - timedelta(days=3):
        hi2, lo2 = lo2, lo2 - timedelta(hours=2)
    t_start = _bisect(f_start, lo2, hi2)

    return idx, t_start, t_end


def mansions_in_window(start: datetime, end: datetime):
    """كل المنازل التي يمرّ بها القمر خلال النافذة."""
    out = []
    t = start
    while t < end:
        idx, a, b = mansion_span(t)
        out.append((idx, a, b))
        t = b + timedelta(minutes=2)
    return out


# ── الزوايا الفلكية ──────────────────────────────────────────────
@dataclass
class Aspect:
    time: datetime
    planet: str
    angle: int
    name: str
    applying_from: float  # درجة القمر عند التمام


def moon_aspects(start: datetime, end: datetime, step_min: int = 20):
    """
    كل زوايا القمر التامّة بين الوقتين، مرتبة زمنيًا.
    نأخذ عيّنة واحدة للفرق الزاوي ثم نبحث فيها عن كل الزوايا،
    بدل إعادة حساب الأفلاك لكل زاوية على حدة.
    """
    planets = list(config.ASPECT_PLANETS)
    if config.INCLUDE_OUTER:
        planets += config.OUTER_PLANETS

    step = timedelta(minutes=step_min)
    n = max(2, int((end - start) / step) + 1)
    grid = [start + step * i for i in range(n + 1)]

    found = []
    for planet in planets:
        diffs = [(lon_of("القمر", t) - lon_of(planet, t)) % 360.0 for t in grid]
        for angle, name in config.ASPECTS.items():
            targets = [angle] if angle in (0, 180) else [angle, 360 - angle]
            for tgt in targets:
                g = [_wrap180(d - tgt) for d in diffs]
                for i in range(len(g) - 1):
                    a, b = g[i], g[i + 1]
                    if a * b < 0 and abs(a) < 60 and abs(b) < 60:
                        f = (lambda x, p=planet, tt=tgt:
                             _wrap180(((lon_of("القمر", x) - lon_of(p, x)) % 360.0) - tt))
                        hit = _bisect(f, grid[i], grid[i + 1])
                        found.append(Aspect(hit, planet, angle, name,
                                            lon_of("القمر", hit)))

    # إزالة التكرار: نفس الكوكب في نفس اللحظة لا يقبل زاويتين
    found.sort(key=lambda a: a.time)
    uniq = []
    for a in found:
        if any(u.planet == a.planet and abs((a.time - u.time).total_seconds()) < 900
               for u in uniq):
            continue
        uniq.append(a)
    return uniq


_ASPECT_WINDOW: list = []


def preload_aspects(start: datetime, end: datetime):
    """يحسب زوايا نافذة واسعة مرّة واحدة لتُستعمل في خلو المسار."""
    global _ASPECT_WINDOW
    _ASPECT_WINDOW = moon_aspects(start, end)
    return _ASPECT_WINDOW


def last_aspect_before(t: datetime, lookback_hours: int = 72):
    """آخر زاوية تامّة للقمر قبل الوقت المعطى."""
    pool = [a for a in _ASPECT_WINDOW if a.time < t]
    if pool:
        return pool[-1]
    asp = moon_aspects(t - timedelta(hours=lookback_hours), t)
    return asp[-1] if asp else None


# ── خلو المسار ───────────────────────────────────────────────────
@dataclass
class VoidCourse:
    start: datetime
    end: datetime
    next_sign: str
    last_aspect: Aspect | None

    @property
    def hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600.0


def void_of_course_periods(day_start: datetime, day_end: datetime):
    """
    فترات خلو المسار المتقاطعة مع اليوم:
    من آخر زاوية تامّة للقمر في برجه حتى دخوله البرج التالي.
    """
    periods = []
    seen = set()
    # نفحص انتقالات البرج التي تقع داخل اليوم أو بعده مباشرة
    probe = day_start - timedelta(days=1)
    while probe < day_end + timedelta(days=1):
        ing_t, next_sign = next_moon_ingress(probe)
        if ing_t.isoformat() in seen:
            probe = ing_t + timedelta(minutes=5)
            continue
        seen.add(ing_t.isoformat())
        la = last_aspect_before(ing_t)
        if la:
            voc = VoidCourse(la.time, ing_t, next_sign, la)
            if voc.end > day_start and voc.start < day_end:
                periods.append(voc)
        probe = ing_t + timedelta(minutes=5)
    return periods


# ── الشمس: الشروق والغروب والفجر ────────────────────────────────
def sun_events(date_local: datetime, lat: float, lon: float, tz: ZoneInfo):
    """أوقات الفجر والشروق والزوال والعصر والغروب لليوم المحلي."""
    midnight = date_local.replace(hour=0, minute=0, second=0, microsecond=0)
    jd0 = to_jd(midnight)
    geo = (lon, lat, 0.0)
    return {
        "الفجر":  _sun_at_alt(jd0, geo, tz, -18.0, rising=True),
        "الشروق": _sun_at_alt(jd0, geo, tz, -0.833, rising=True),
        "الغروب": _sun_at_alt(jd0, geo, tz, -0.833, rising=False),
    }


def _sun_altitude(jd, geo):
    from math import asin, sin, cos, radians, degrees
    x = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)[0]
    ra, dec = x[0], x[1]
    gst = swe.sidtime(jd) * 15.0
    ha = (gst + geo[0] - ra) % 360.0
    h = asin(sin(radians(geo[1])) * sin(radians(dec)) +
             cos(radians(geo[1])) * cos(radians(dec)) * cos(radians(ha)))
    return degrees(h)


def _sun_at_alt(jd0, geo, tz, alt_deg, rising=True):
    """وقت بلوغ الشمس ارتفاعًا معيّنًا صعودًا أو هبوطًا خلال اليوم."""
    n = 288  # كل خمس دقائق
    prev_j = jd0
    prev_a = _sun_altitude(jd0, geo)
    for i in range(1, n + 1):
        j = jd0 + i / n
        a = _sun_altitude(j, geo)
        crossed = (prev_a < alt_deg <= a) if rising else (prev_a > alt_deg >= a)
        if crossed:
            lo, hi = prev_j, j
            for _ in range(40):
                m = (lo + hi) / 2
                below = _sun_altitude(m, geo) < alt_deg
                if below == rising:
                    lo = m
                else:
                    hi = m
            return _from_jd((lo + hi) / 2, tz)
        prev_j, prev_a = j, a
    return None


def _from_jd(jd: float, tz) -> datetime:
    y, m, d, h = swe.revjul(jd)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int(round((((h - hh) * 60) - mm) * 60))
    if ss == 60:
        ss = 0
        mm += 1
    if mm == 60:
        mm = 0
        hh += 1
    base = datetime(y, m, d, 0, 0, tzinfo=UTC) + timedelta(hours=hh, minutes=mm, seconds=ss)
    return base.astimezone(tz)


# ── طور القمر ───────────────────────────────────────────────────
def moon_phase(dt: datetime):
    elong = (lon_of("القمر", dt) - lon_of("الشمس", dt)) % 360.0
    if elong < 15 or elong >= 345:
        name, waxing = "المحاق / الاقتران", True
    elif elong < 90:
        name, waxing = "الهلال المتزايد", True
    elif elong < 105:
        name, waxing = "التربيع الأول", True
    elif elong < 165:
        name, waxing = "الأحدب المتزايد", True
    elif elong < 195:
        name, waxing = "البدر", False
    elif elong < 255:
        name, waxing = "الأحدب المتناقص", False
    elif elong < 285:
        name, waxing = "التربيع الأخير", False
    else:
        name, waxing = "الهلال المتناقص", False
    return {"elongation": elong, "name": name, "waxing": waxing,
            "illumination": (1 - __import__("math").cos(__import__("math").radians(elong))) / 2}
