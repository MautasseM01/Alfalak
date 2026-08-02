# -*- coding: utf-8 -*-
"""
تصدير التقويم — iCalendar (RFC 5545).

الغرض أن تدخل السماءُ جدولَك: تشترك بالرابط مرّة، فتظهر منازل القمر
وخلو المسار وأفضل أيامك في تقويم هاتفك مع مواعيدك.

والمعيار دقيق في أشياء يسهل التفريط فيها، وكلّها مُطبَّقة هنا:

* **نهايات الأسطر CRLF** لا LF. تقاويم كثيرة ترفض الملفّ بغيرها.
* **الطيّ عند ٧٥ ثمانيّة** — لا ٧٥ حرفًا. والفرق قاتل في العربية:
  الحرف العربي ثمانيّتان في UTF-8، فلو طوينا بالحروف لخرج السطر عن
  الحدّ، ولو طوينا في وسط حرف لخرج ملفّ فاسد. فالطيّ هنا **على
  حدود المحارف مع عدّ الثمانيّات**.
* **الهروب** من الفاصلة والفاصلة المنقوطة والشرطة المائلة والسطر الجديد.
* **UID ثابت** لكل حدث: يُشتقّ من مضمونه، فإذا حُدِّث الاشتراك لم
  تتكرّر الأحداث ولم تُنشأ نسخ.
* **DTSTAMP** إلزاميّ في كل VEVENT.
* **الأوقات بالتوقيت العالمي** (بلاحقة Z) بدل VTIMEZONE: أبسط وأسلم،
  فيُحوِّلها تقويم القارئ إلى منطقته وحدها.
"""
from __future__ import annotations

import hashlib
from datetime import date as _date, datetime, timedelta, timezone

UTC = timezone.utc
PRODID = "-//Al-Falak//alfalak.vercel.app//AR"
CRLF = "\r\n"


# ══════════════════════════════════════════════════════════════
# أدوات المعيار
# ══════════════════════════════════════════════════════════════
def esc(text: str) -> str:
    """الهروب كما ينصّ المعيار: \\ ثم ; ثم , ثم السطر الجديد."""
    return (str(text).replace("\\", "\\\\")
                     .replace(";", "\\;")
                     .replace(",", "\\,")
                     .replace("\r\n", "\\n")
                     .replace("\n", "\\n"))


def fold(line: str) -> str:
    """
    الطيّ عند ٧٥ ثمانيّة، **على حدود المحارف**.

    المعيار يعدّ الثمانيّات لا الحروف. والعربية حرفها ثمانيّتان، فلو
    عددنا الحروف لتجاوز السطر الحدّ؛ ولو قطعنا عند الثمانيّة ٧٥ بلا
    نظر لوقع القطع في وسط حرف فخرج ملفّ فاسد لا يفتحه تقويم.
    """
    out, cur, size = [], [], 0
    limit = 75
    for ch in line:
        w = len(ch.encode("utf-8"))
        if size + w > limit:
            out.append("".join(cur))
            cur, size = [ch], w + 1     # السطر التالي يبدأ بمسافة
            limit = 75
        else:
            cur.append(ch)
            size += w
    out.append("".join(cur))
    return CRLF.join([out[0]] + [" " + x for x in out[1:]])


def _stamp(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _day(d: _date) -> str:
    return d.strftime("%Y%m%d")


def _uid(*parts) -> str:
    """
    مُعرّف يُشتقّ من مضمون الحدث لا من ساعة التوليد.

    لو ولّدناه عشوائيًّا لتضاعفت الأحداث في تقويم المشترك كلّما
    حُدِّث الرابط — وهذا أشهر عيب في تقاويم الاشتراك.
    """
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:24] + "@alfalak"


class Event:
    """حدث واحد. all_day يجعله يومًا كاملًا بلا ساعة."""

    def __init__(self, uid_parts, summary, start, end=None, desc="",
                 all_day=False, location="", categories=None,
                 transparent=True):
        self.uid = _uid(*uid_parts)
        self.summary = summary
        self.start = start
        self.end = end
        self.desc = desc
        self.all_day = all_day
        self.location = location
        self.categories = categories or []
        self.transparent = transparent

    def lines(self, now: datetime) -> list[str]:
        L = ["BEGIN:VEVENT",
             f"UID:{self.uid}",
             f"DTSTAMP:{_stamp(now)}"]
        if self.all_day:
            end = self.end or (self.start + timedelta(days=1))
            L.append(f"DTSTART;VALUE=DATE:{_day(self.start)}")
            L.append(f"DTEND;VALUE=DATE:{_day(end)}")
        else:
            L.append(f"DTSTART:{_stamp(self.start)}")
            L.append(f"DTEND:{_stamp(self.end or self.start + timedelta(hours=1))}")
        L.append(f"SUMMARY:{esc(self.summary)}")
        if self.desc:
            L.append(f"DESCRIPTION:{esc(self.desc)}")
        if self.location:
            L.append(f"LOCATION:{esc(self.location)}")
        if self.categories:
            L.append("CATEGORIES:" + ",".join(esc(c) for c in self.categories))
        # شفّاف: لا يشغل وقتك ولا يُظهرك «مشغولًا» لمن يرى تقويمك
        L.append("TRANSP:" + ("TRANSPARENT" if self.transparent else "OPAQUE"))
        L.append("END:VEVENT")
        return L


def dedupe(events: list[Event]) -> list[Event]:
    """
    حدث واحد لكل مُعرّف.

    منزلة القمر تمتدّ عبر منتصف الليل، فتظهر في بيانات اليومين معًا.
    ومُعرّفها واحد لأنه مُشتقّ من مضمونها — فلولا هذا الحذف لظهرت
    مرّتين في تقويم القارئ، أو رفض بعض التقاويم الملفّ كلّه.
    """
    seen, out = set(), []
    for e in events:
        if e.uid in seen:
            continue
        seen.add(e.uid)
        out.append(e)
    return out


def build(events: list[Event], name: str, desc: str = "",
          refresh_hours: int = 12, now: datetime | None = None) -> str:
    """يُركّب الملفّ كاملًا. يُرجع نصًّا بنهايات CRLF جاهزًا للإرسال."""
    now = now or datetime.now(UTC)
    events = dedupe(events)
    L = ["BEGIN:VCALENDAR",
         "VERSION:2.0",
         f"PRODID:{PRODID}",
         "CALSCALE:GREGORIAN",
         "METHOD:PUBLISH",
         f"X-WR-CALNAME:{esc(name)}",
         f"NAME:{esc(name)}"]
    if desc:
        L.append(f"X-WR-CALDESC:{esc(desc)}")
        L.append(f"DESCRIPTION:{esc(desc)}")
    L.append(f"REFRESH-INTERVAL;VALUE=DURATION:PT{refresh_hours}H")
    L.append(f"X-PUBLISHED-TTL:PT{refresh_hours}H")
    L.append("X-WR-TIMEZONE:UTC")
    for e in events:
        L.extend(e.lines(now))
    L.append("END:VCALENDAR")
    return CRLF.join(fold(x) for x in L) + CRLF


# ══════════════════════════════════════════════════════════════
# ١ — تقويم النشرة اليومية: المنازل وخلو المسار
# ══════════════════════════════════════════════════════════════
def bulletin_events(start: _date, days: int, tzname: str,
                    lat: float, lon: float, place: str) -> list[Event]:
    from . import bulletin
    out = []
    for i in range(days):
        d = start + timedelta(days=i)
        try:
            g = bulletin.gather(d, tzname, lat, lon)
        except Exception:
            continue

        for m in g["mansions"]:
            out.append(Event(
                ("mansion", place, m["name"], m["start"].isoformat()),
                f"منزلة {m['name']} — {m['mood']}",
                m["start"], m["end"],
                desc=f"{m['desc']}\n{m['good_for']}",
                location=place, categories=["المنازل القمرية"]))

        for v in g["voc"]:
            hrs = round(v["hours"], 1)
            out.append(Event(
                ("voc", place, v["start"].isoformat()),
                f"خلو المسار ({hrs} ساعة)",
                v["start"], v["end"],
                desc=("القمر لا يتّصل بكوكب حتى يدخل "
                      f"{v['next_sign']}. وقت لا يُبدأ فيه أمر جديد؛ "
                      "يصلح للمراجعة والترتيب وإنهاء ما بُدئ."),
                location=place, categories=["خلو المسار"]))
    return out


# ══════════════════════════════════════════════════════════════
# ٢ — تقويم الاختيارات: أفضل الأيام لغرض
# ══════════════════════════════════════════════════════════════
def election_events(start: _date, days: int, tzname: str, lat: float,
                    lon: float, purpose: str, place: str,
                    min_score: int = 70, natal: dict | None = None) -> list[Event]:
    from . import elections
    r = elections.search(start, days, tzname, lat, lon, purpose,
                         natal=natal, top=days)
    if "error" in r:
        return []
    out = []
    for row in r["best"]:
        if row["score"] < min_score:
            continue
        d = _date.fromisoformat(row["date"])
        h = (row.get("best_hours") or [None])[0]
        desc = [f"الدرجة {row['score']} — {row['verdict']}: {row['verdict_note']}"]
        if h:
            desc.append(f"أفضل ساعة: {h['start_text']}–{h['end_text']} "
                        f"(ساعة {h['planet']})")
        if row.get("plus"):
            desc.append("ما يُقوّيه: " + "؛ ".join(row["plus"][:5]))
        if row.get("minus"):
            desc.append("ما يُضعفه: " + "؛ ".join(row["minus"][:3]))
        desc.append(r["rule"])
        out.append(Event(
            ("elect", place, purpose, row["date"]),
            f"{purpose} — {row['score']}/100 ({row['verdict']})",
            d, d + timedelta(days=1), desc="\n".join(desc),
            all_day=True, location=place,
            categories=["الاختيارات", purpose]))
    return out


# ══════════════════════════════════════════════════════════════
# ٣ — تقويم أحداث الشهر: الانتقالات والرجوع والكسوف
# ══════════════════════════════════════════════════════════════
def month_events(year: int, month: int, tzname: str) -> list[Event]:
    """انتقالات ورجوع وتقمير وكسوف الشهر، ونوافذ الرجوع كأيام كاملة."""
    from . import mundane
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tzname)
    data = mundane.month_events(year, month, tzname)

    KIND_AR = {"ingress": "انتقال", "station": "وقوف", "aspect": "زاوية",
               "lunation": "تقمير", "eclipse": "كسوف وخسوف",
               "season": "فصل", "combust": "احتراق"}

    out = []
    for d in data["events"]:
        when = datetime.fromisoformat(d["when"])
        title = d["title"]
        desc = []
        det = d.get("detail") or {}
        for k, v in det.items():
            if isinstance(v, (str, int, float)) and str(v).strip():
                desc.append(f"{k}: {v}")
        if d.get("sign"):
            desc.append(f"البرج: {d['sign']}")
        out.append(Event(
            ("mundane", d["kind"], d["when"], title),
            f"{KIND_AR.get(d['kind'], d['kind'])} — {title}",
            when, when + timedelta(minutes=30),
            desc="\n".join(desc),
            categories=["أحداث السماء", KIND_AR.get(d["kind"], d["kind"])]))

    # نوافذ الرجوع أيامٌ كاملة ممتدّة، لا لحظات
    for w in data.get("retrograde_windows", []):
        a = datetime.fromisoformat(w["start"]).astimezone(tz).date()
        b = datetime.fromisoformat(w["end"]).astimezone(tz).date()
        out.append(Event(
            ("retro", w.get("body", ""), w["start"]),
            f"رجوع {w.get('body', '')}",
            a, b + timedelta(days=1),
            desc=(f"من {a.isoformat()} إلى {b.isoformat()}. "
                  "زمن مراجعة لا ابتداء: يُعاد النظر فيما يخصّ "
                  "هذا الكوكب، ويُؤجَّل ما يمكن تأجيله منه."),
            all_day=True, categories=["أحداث السماء", "رجوع"]))
    return out


# ══════════════════════════════════════════════════════════════
# ٤ — تقويم ساعات الكواكب
# ══════════════════════════════════════════════════════════════
def hour_events(start: _date, days: int, tzname: str, lat: float,
                lon: float, place: str,
                only: list[str] | None = None,
                day_only: bool = True) -> list[Event]:
    from . import hours as _h
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(tzname)
    out = []
    for i in range(days):
        d = start + timedelta(days=i)
        tbl = _h.hours_for(datetime(d.year, d.month, d.day, tzinfo=tz),
                           lat, lon, tzname)
        if "error" in tbl:
            continue
        for h in tbl["hours"]:
            if only and h["planet"] not in only:
                continue
            if day_only and h["part"] != "نهارية":
                continue
            out.append(Event(
                ("hour", place, h["start"].isoformat(), h["planet"]),
                f"ساعة {h['planet']} {h['symbol']} — {h['طبعها']}",
                h["start"], h["end"],
                desc=(f"تصلح: {h['تصلح']}\nتُتجنّب: {h['تُتجنّب']}\n\n"
                      f"من التفهيم — {h['من التفهيم']}\n"
                      f"من غاية الحكيم — {h['من غاية الحكيم']}"),
                location=place, categories=["ساعات الكواكب", h["planet"]]))
    return out


KINDS = {
    "bulletin": "منازل القمر وخلو المسار",
    "elections": "أفضل الأيام لغرض تختاره",
    "month": "أحداث السماء: الانتقالات والرجوع والكسوف",
    "hours": "ساعات الكواكب",
}
