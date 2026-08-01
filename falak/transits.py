# -*- coding: utf-8 -*-
"""
العبور — أيّ أحداث السماء تمسّ خريطتك أنت.

الأحداث العامّة تخصّ الناس جميعًا، والعبور يخصّك وحدك: كوكب اليوم يمرّ على
موضع كوكب من خريطة ميلادك، فيُنشِّط ذلك الموضع ويُظهر معناه في حياتك.

ثلاثة أشياء تُحسب هنا:

  ١. زوايا العبور   كوكب سائر ينظر إلى جِرم في خريطتك، بنافذته الزمنية
                    كاملة: متى يدخل الوجاج، ومتى يتمّ، ومتى ينفكّ.
  ٢. مسّ الأحداث    الكسوف والتقميرات: أتقع على درجة من درجات خريطتك؟
  ٣. عبور البيوت    كوكب يدخل برجًا هو بيت من بيوتك، فينتقل أثره إلى بابه.

والترتيب بالأهمّية: الكوكب البطيء على نقطة شخصية أثقل من السريع،
والزاوية التامّة أثقل من المقاربة.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import chart as ch
from . import mundane
from .ephem import UTC, _bisect, _wrap180

# الأجرام السائرة التي يُعتدّ بعبورها
TRANSIT_BODIES = ["الشمس", "عطارد", "الزهرة", "المريخ", "المشتري",
                  "زحل", "أورانوس", "نبتون", "بلوتو", "خيرون"]

# نقاط الخريطة التي يُنظر في عبورها
NATAL_TARGETS = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري",
                 "زحل", "أورانوس", "نبتون", "بلوتو", "الرأس"]
NATAL_ANGLES = ["الطالع", "وسط السماء"]

MAJOR = [0, 60, 90, 120, 180]

# وجاج العبور أضيق من وجاج الخريطة: العبور حدث لا بنية
TRANSIT_ORB = {0: 3.0, 60: 2.0, 90: 3.0, 120: 3.0, 180: 3.0,
               30: 1.0, 45: 1.0, 135: 1.0, 150: 1.5, 72: 1.0}

# وزن الكوكب السائر: البطيء أثقل أثرًا وأطول مكثًا
WEIGHT = {"بلوتو": 10, "نبتون": 9, "أورانوس": 9, "زحل": 8, "خيرون": 6,
          "المشتري": 6, "المريخ": 4, "الشمس": 3, "الزهرة": 2, "عطارد": 2}
# وزن الهدف في الخريطة
TARGET_WEIGHT = {"الشمس": 10, "القمر": 10, "الطالع": 10, "وسط السماء": 9,
                 "عطارد": 6, "الزهرة": 6, "المريخ": 6,
                 "المشتري": 5, "زحل": 5, "الرأس": 4,
                 "أورانوس": 3, "نبتون": 3, "بلوتو": 3}

MEANING = {
    "المشتري": "فرصة واتّساع في الباب الذي يمسّه — يُنتفع به إن طُلب، ولا يأتي وحده",
    "زحل": "اختبار وحدّ ومسؤولية — ما يثبت فيه يبقى، وما لا يثبت يسقط",
    "أورانوس": "زعزعة وتحرّر مفاجئ — لا يُقاوَم، وإنما يُوجَّه",
    "نبتون": "ذوبان حدود والتباس — يُرفع فيه الحجاب ويُخشى فيه الوهم",
    "بلوتو": "تحوّل عميق لا رجعة فيه — يُهدَم ليُبنى",
    "خيرون": "يُفتح الجرح ليُشفى، وما تتعلّمه منه تُعلّمه غيرك",
    "المريخ": "شرارة وحركة سريعة — أثره أيام لا شهور",
    "الشمس": "إضاءة قصيرة تُظهر ما كان مستورًا — أيام معدودة",
    "الزهرة": "لطف ومودّة عابرة",
    "عطارد": "خبر أو كلام أو ورقة",
}


def _lon(body: str, when: datetime) -> float:
    return mundane.lon_at(body, when)


def _orb_of(angle: int) -> float:
    return TRANSIT_ORB.get(angle, 1.0)


def _window(tbody: str, target_lon: float, angle: int,
            around: datetime, span_days: int = 400):
    """
    نافذة العبور: (دخول الوجاج، التمام، الخروج).
    نبحث حول اللحظة المعطاة صعودًا ونزولًا.
    """
    orb = _orb_of(angle)

    def sep(t):
        return abs(_wrap180(_lon(tbody, t) - target_lon))

    def gap(t):
        return sep(t) - angle

    # التمام: أقرب جذر لـ gap
    step = timedelta(hours=12 if tbody in ("الشمس", "عطارد", "الزهرة", "المريخ") else 48)
    exact = None
    t = around - timedelta(days=2)
    prev = gap(t)
    stop = around + timedelta(days=min(span_days, 400))
    while t < stop:
        t2 = t + step
        cur = gap(t2)
        if prev * cur < 0 and abs(prev) < 30 and abs(cur) < 30:
            exact = _bisect(gap, t, t2)
            break
        prev, t = cur, t2
    if exact is None:
        return None

    # حدود الوجاج حول التمام
    def edge(direction):
        t = exact
        d = timedelta(hours=6) * direction
        for _ in range(2000):
            t2 = t + d
            if abs(sep(t2) - angle) > orb:
                f = lambda x: abs(sep(x) - angle) - orb
                return _bisect(f, min(t, t2), max(t, t2))
            t = t2
        return t

    return edge(-1), exact, edge(+1)


def find(natal: dict, start: datetime, end: datetime,
         minor: bool = False, top: int | None = None) -> list[dict]:
    """
    زوايا العبور التي تتقاطع مع الفترة.
    natal: مخرجات chart.compute
    """
    targets = []
    for b in natal["bodies"]:
        if b["name"] in NATAL_TARGETS:
            targets.append((b["name"], b["lon"], b["sign"], b.get("house")))
    for a in NATAL_ANGLES:
        v = natal["angles"][a]
        targets.append((a, v["lon"], v["sign"], None))

    angles = MAJOR + ([30, 45, 135, 150] if minor else [])
    step = timedelta(hours=12)
    n = int((end - start) / step) + 2
    grid = [start + step * i for i in range(n)]

    out = []
    for tb in TRANSIT_BODIES:
        if not mundane._available(tb):
            continue
        lons = [_lon(tb, t) for t in grid]
        for tname, tlon, tsign, thouse in targets:
            seps = [abs(_wrap180(L - tlon)) for L in lons]
            for ang in angles:
                orb = _orb_of(ang)
                inside = [abs(s - ang) <= orb for s in seps]
                if not any(inside):
                    continue
                mid = grid[inside.index(True)]
                w = _window(tb, tlon, ang, mid)
                if not w:
                    continue
                enter, exact, leave = w
                if leave < start or enter > end:
                    continue
                name, polarity, major, sym = ch.ASPECT_BY_ANGLE[ang]
                score = (WEIGHT.get(tb, 3) * TARGET_WEIGHT.get(tname, 4)
                         * (1.3 if major else 0.7)
                         * (1.4 if start <= exact <= end else 1.0))
                out.append({
                    "transit": tb, "target": tname, "target_sign": tsign,
                    "target_house": thouse,
                    "aspect": name, "angle": ang, "symbol": sym,
                    "polarity": polarity, "major": major,
                    "enter": enter, "exact": exact, "leave": leave,
                    "days": round((leave - enter).total_seconds() / 86400, 1),
                    "exact_in_window": start <= exact <= end,
                    "score": round(score, 1),
                    "note": MEANING.get(tb, ""),
                })

    # إزالة التكرار (نفس العبور يتكرّر بالرجوع)
    out.sort(key=lambda x: (-x["score"], x["exact"]))
    seen, uniq = set(), []
    for r in out:
        k = (r["transit"], r["target"], r["angle"],
             r["exact"].strftime("%Y-%m-%d"))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    return uniq[:top] if top else uniq


def touches(natal: dict, events: list, orb: float = 2.5) -> list[dict]:
    """أيّ أحداث الشهر تقع على درجة من درجات خريطتك."""
    pts = [(b["name"], b["lon"], b["sign"]) for b in natal["bodies"]
           if b["name"] in NATAL_TARGETS]
    for a in NATAL_ANGLES:
        v = natal["angles"][a]
        pts.append((a, v["lon"], v["sign"]))

    out = []
    for e in events:
        if e["kind"] not in ("eclipse", "lunation"):
            continue
        L = e.get("lon") or 0.0
        for name, plon, psign in pts:
            d = abs(_wrap180(L - plon))
            if d <= orb:
                out.append({
                    "event": e["title"], "kind": e["kind"],
                    "date": e["date"], "time": e["time"],
                    "target": name, "target_sign": psign,
                    "orb": round(d, 2),
                    "note": (f"يقع هذا الحدث على {name} في خريطتك بفارق "
                             f"{d:.1f}° — فهو يخصّك خصوصًا، "
                             + ("والكسوف يفتح بابًا يمتدّ أثره أشهرًا."
                                if e["kind"] == "eclipse"
                                else "ويُنشِّط هذا الموضع لأسابيع.")),
                })
    out.sort(key=lambda x: x["orb"])
    return out


def house_moves(natal: dict, events: list) -> list[dict]:
    """انتقالات الكواكب إلى بروج هي بيوت من خريطتك."""
    sign_house = {}
    for c in natal["houses"]["cusps"]:
        sign_house.setdefault(c["sign"], c["house"])
    names = ch.HOUSE_NAMES

    out = []
    for e in events:
        if e["kind"] != "ingress" or e["body"] not in TRANSIT_BODIES:
            continue
        h = sign_house.get(e["sign"])
        if not h:
            continue
        out.append({
            "date": e["date"], "body": e["body"], "sign": e["sign"],
            "house": h, "house_name": names[h - 1],
            "retro": e["detail"].get("retro", False),
            "note": (f"{e['body']} ينتقل إلى بيتك {h} — "
                     f"{names[h-1].split(':')[1].strip()}. "
                     + MEANING.get(e["body"], "")),
        })
    return out


def personal_month(natal: dict, year: int, month: int, tzname: str,
                   events: list | None = None, top: int = 12) -> dict:
    """القسم الشخصي في النشرة الشهرية."""
    tz = ZoneInfo(tzname)
    start = datetime(year, month, 1, tzinfo=tz)
    nm, ny = (month % 12) + 1, year + (1 if month == 12 else 0)
    end = datetime(ny, nm, 1, tzinfo=tz)

    if events is None:
        events = mundane.month_events(year, month, tzname)["events"]

    tr = find(natal, start.astimezone(UTC), end.astimezone(UTC), top=top)
    for r in tr:
        for k in ("enter", "exact", "leave"):
            r[k + "_text"] = r[k].astimezone(tz).strftime("%Y-%m-%d")
            r[k] = r[k].astimezone(tz).isoformat()

    hits = touches(natal, events)
    moves = house_moves(natal, events)

    lines = ["#جوّك_الشخصي"]
    if hits:
        lines.append("ما يمسّك من أحداث الشهر:")
        for h in hits:
            lines.append(f"- {h['date']}: {h['event']} — على {h['target']} "
                         f"في خريطتك (فارق {h['orb']}°).")
    if tr:
        lines.append("")
        lines.append("أثقل عبورات الشهر على خريطتك:")
        for r in tr[:6]:
            mark = "★ " if r["exact_in_window"] else ""
            lines.append(
                f"- {mark}{r['transit']} {r['symbol']} {r['target']} "
                f"({r['aspect']}) — يتمّ {r['exact_text']}، "
                f"ونافذته من {r['enter_text']} إلى {r['leave_text']}. {r['note']}.")
    if moves:
        lines.append("")
        lines.append("انتقالات تدخل بيوتك:")
        for m in moves:
            lines.append(f"- {m['date']}: {m['note']}")
    if not (hits or tr or moves):
        lines.append("لا يمسّ أحداث هذا الشهر خريطتك مسًّا قويًّا — شهر هادئ عليك.")

    return {
        "transits": tr, "touches": hits, "house_moves": moves,
        "text": "\n".join(lines),
    }
