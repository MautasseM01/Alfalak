# -*- coding: utf-8 -*-
"""
النشرة الشهرية — سرد الشهر ومعناه.

تُبنى على `mundane.month_events` و`elections.month_calendar`، وتُصاغ
بثلاثة ألسنة يختارها القارئ:

  daily     لسان النشرة اليومية: مباشر عملي قصير الجمل
  literary  لسان أدبي أوسع نفَسًا، على طريقة النشرات العالمية
  classic   لسان التراث، على صياغة كتب الأحكام

والقوالب نصّية خالصة بلا ذكاء اصطناعي: النصّ نفسه لا يتغيّر بين طلبين،
ولا يخرج من الخادم شيء، ولا يكلّف شيئًا.
"""
from __future__ import annotations

from datetime import date as _date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import chart as ch
from . import elections, ephem, mundane, patterns
from .ephem import SIGNS

MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
             "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

VOICES = {
    "daily":    "لسان النشرة اليومية — مباشر عملي",
    "literary": "لسان أدبي — أوسع نفَسًا",
    "classic":  "لسان التراث — على صياغة كتب الأحكام",
}

ELEMENT = ch.ELEMENT

# ── عناوين الشهر بحسب غالب أحداثه ───────────────────────────────
# (المفتاح، العنوان، الوصف)
THEMES = {
    "eclipse":   ("شهر الانكشاف",
                  "الكسوف والخسوف يفتحان أبوابًا ويغلقان أخرى، وأثرهما يمتدّ أشهرًا"),
    "stations":  ("شهر المراجعة",
                  "كواكب تقف وترجع، فما بُني على عجل يُعاد النظر فيه"),
    "ingress":   ("شهر الانتقالات",
                  "الكواكب تبدّل بروجها، فتتبدّل معها أبواب الحياة التي تحكمها"),
    "outer":     ("شهر التحوّل",
                  "الكواكب البعيدة تتلاقى، وأثرها في العامّة لا في الأفراد"),
    "benefic":   ("شهر الفرج",
                  "السعدان غالبان على تكوينات الشهر، وهي فترة تيسير"),
    "malefic":   ("شهر الجَلَد",
                  "النحسان غالبان، والشهر يطلب صبرًا وحسن تدبير"),
    "calm":      ("شهر السكون",
                  "قليل الأحداث، وهو وقت الترتيب والاستعداد لما بعده"),
}


def _fmt_date(iso: str) -> str:
    d = _date.fromisoformat(iso)
    return f"{d.day} {MONTHS_AR[d.month - 1]}"


def _fmt_day_num(iso: str) -> int:
    return _date.fromisoformat(iso).day


# ══════════════════════════════════════════════════════════════════
# استخراج عنوان الشهر ومعناه
# ══════════════════════════════════════════════════════════════════
def derive_theme(events: list, retro_windows: list) -> dict:
    counts = {}
    for e in events:
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1

    outers = {"أورانوس", "نبتون", "بلوتو", "خيرون"}
    outer_aspects = [e for e in events if e["kind"] == "aspect"
                     and e["body"] in outers and e["other"] in outers]
    benefic = [e for e in events if e["kind"] == "aspect"
               and e["detail"].get("polarity") == "إيجابية"]
    malefic = [e for e in events if e["kind"] == "aspect"
               and e["detail"].get("polarity") == "سلبية"]

    score = {
        "eclipse": counts.get("eclipse", 0) * 40,
        "stations": counts.get("station", 0) * 14,
        "ingress": counts.get("ingress", 0) * 5,
        "outer": len(outer_aspects) * 18,
        "benefic": len(benefic) * 3,
        "malefic": len(malefic) * 3,
        "calm": 12 if len(events) < 18 else 0,
    }
    key = max(score, key=score.get)
    title, note = THEMES[key]

    # العنصر الغالب على بروج أحداث الشهر
    els = {}
    for e in events:
        if e.get("sign"):
            el = ELEMENT.get(e["sign"])
            if el:
                els[el] = els.get(el, 0) + 1
    top_el = max(els, key=els.get) if els else None

    return {
        "key": key, "title": title, "note": note,
        "element": top_el,
        "counts": counts,
        "benefic": len(benefic), "malefic": len(malefic),
        "outer_aspects": len(outer_aspects),
    }


# ══════════════════════════════════════════════════════════════════
# القوالب الثلاثة
# ══════════════════════════════════════════════════════════════════
def _line(e: dict, voice: str) -> str:
    d = e["detail"]
    day = _fmt_date(e["date"])
    t = e["time"]
    k = e["kind"]

    if voice == "classic":
        if k == "ingress":
            s = f"وفي {day} ينتقل {e['body']} إلى برج {e['sign']}"
            if d.get("retro"):
                s += " راجعًا"
            return s + "."
        if k == "station":
            return (f"وفي {day} يقف {e['body']} في {e['sign']} ثم "
                    + ("يرجع" if d.get("retrograde") else "يستقيم") + ".")
        if k == "aspect":
            return (f"وفي {day} ينظر {e['body']} إلى {e['other']} "
                    f"نظر {d['aspect']}.")
        if k == "lunation":
            return f"وفي {day} يكون {d['phase']} في برج {e['sign']}."
        if k == "eclipse":
            return (f"وفي {day} ينكسف {'النيّر الأعظم' if d['eclipse']=='شمسي' else 'القمر'} "
                    f"{d['kind']} في برج {e['sign']}، وهو وقت يُتحرّز فيه.")
        if k == "season":
            return f"وفي {day} تحلّ {e['title']}."
        if k == "combust":
            return f"وفي {day} {e['title']}."
        return f"وفي {day} {e['title']}."

    if voice == "literary":
        if k == "ingress":
            return (f"في {day} يعبر {e['body']} إلى {e['sign']}"
                    + (" راجعًا، عائدًا إلى ما لم يُستوفَ" if d.get("retro") else "")
                    + f". {d.get('note','')}")
        if k == "station":
            return (f"في {day} يتوقّف {e['body']} في {e['sign']} ثم "
                    + ("يبدأ رجوعه" if d.get("retrograde") else "يستأنف سيره")
                    + f". {d.get('note','')}")
        if k == "aspect":
            return f"في {day} الساعة {t} — {e['body']} {d['symbol']} {e['other']}. {d.get('note','')}."
        if k == "lunation":
            return f"في {day} الساعة {t} — {d['phase']} في {e['sign']}. {d.get('note','')}"
        if k == "eclipse":
            return f"في {day} الساعة {t} — {e['title']}. {d.get('note','')}"
        return f"في {day} — {e['title']}."

    # daily
    if k == "ingress":
        return (f"{_fmt_day_num(e['date'])} {MONTHS_AR[_date.fromisoformat(e['date']).month-1]}: "
                f"{e['body']} ينتقل إلى {e['sign']}"
                + (" راجعًا" if d.get("retro") else "") + ".")
    if k == "station":
        verb = "يبدأ الرجوع" if d.get("retrograde") else "يستقيم"
        return f"{_fmt_date(e['date'])}: {e['body']} {verb} في {e['sign']}."
    if k == "aspect":
        pol = d.get("polarity", "")
        return (f"{_fmt_date(e['date'])} {t}: {d['aspect']} بين {e['body']} و{e['other']}"
                + (f" — {pol}." if pol else "."))
    if k == "lunation":
        return f"{_fmt_date(e['date'])} {t}: {d['phase']} في {e['sign']}."
    if k == "eclipse":
        return f"{_fmt_date(e['date'])} {t}: {e['title']} — لا تبدأ فيه أمرًا."
    return f"{_fmt_date(e['date'])}: {e['title']}."


def _summary(theme: dict, events: list, retro: list, voice: str,
             year: int, month: int) -> str:
    mn = MONTHS_AR[month - 1]
    c = theme["counts"]
    ecl = [e for e in events if e["kind"] == "eclipse"]
    lun = [e for e in events if e["kind"] == "lunation"]
    ing = [e for e in events if e["kind"] == "ingress"]
    sta = [e for e in events if e["kind"] == "station"]

    bits = []
    if ecl:
        bits.append("، و".join(e["title"] for e in ecl))
    if lun:
        bits.append("، و".join(f"{e['detail']['phase']} في {e['sign']}" for e in lun[:2]))
    if ing:
        bits.append(f"{len(ing)} انتقالًا بين البروج")
    if sta:
        bits.append("، و".join(
            f"{e['body']} {'يرجع' if e['detail'].get('retrograde') else 'يستقيم'}"
            for e in sta))

    body = "، و".join(bits) if bits else "أحداث قليلة"

    if voice == "classic":
        return (f"أمّا شهر {mn} من سنة {year} فإنّ فيه {body}. "
                f"والغالب على تكويناته العنصر {theme['element'] or 'المختلط'}، "
                f"وهو {theme['note']}.")
    if voice == "literary":
        return (f"يحمل {mn} هذا العام {body}. الغالب على مزاجه العنصر "
                f"{theme['element'] or 'المختلط'}، و{theme['note']}. "
                f"وفيه من الزوايا الموافقة {theme['benefic']} ومن المخالفة "
                f"{theme['malefic']}، فاقرأ أيامه بميزانها لا بجملتها.")
    return (f"{mn} {year}: {body}. "
            f"الغالب عنصر {theme['element'] or 'مختلط'}. "
            f"{theme['benefic']} زاوية موافقة و{theme['malefic']} مخالفة.")


# ══════════════════════════════════════════════════════════════════
# أشكال الزوايا عند التقميرات
# ══════════════════════════════════════════════════════════════════
def lunation_figures(events: list, tzname: str, lat: float, lon: float) -> list:
    """خريطة كل تقمير وكسوف، وما فيها من أشكال زاوية."""
    out = []
    for e in events:
        if e["kind"] not in ("lunation", "eclipse"):
            continue
        when = datetime.fromisoformat(e["when"])
        c = ch.compute(when, lat, lon, "whole", tzname,
                       minor_aspects=False)
        out.append({
            "date": e["date"], "time": e["time"], "title": e["title"],
            "kind": e["kind"], "sign": e["sign"],
            "asc": c["angles"]["الطالع"]["text"],
            "patterns": [{"name": p["name"], "members": p["members"],
                          "where": p["where"], "note": p["note"]}
                         for p in c["patterns"]],
            "aspects": [{"a": a["a"], "b": a["b"], "name": a["name"],
                         "symbol": a["symbol"], "orb": a["orb"],
                         "polarity": a["polarity"]}
                        for a in c["aspects"][:8]],
            "bodies": [{"name": b["name"], "symbol": b["symbol"],
                        "text": b["text"], "retro": b["retro"]}
                       for b in c["bodies"] if b["core"]],
        })
    return out


# ══════════════════════════════════════════════════════════════════
# النشرة كاملة
# ══════════════════════════════════════════════════════════════════
def compose(year: int, month: int, tzname: str, lat: float, lon: float,
            voice: str = "daily", place: str = "",
            purposes: list[str] | None = None,
            with_figures: bool = True,
            natal: dict | None = None) -> dict:
    if voice not in VOICES:
        voice = "daily"

    ev = mundane.month_events(year, month, tzname)
    events, retro = ev["events"], ev["retrograde_windows"]
    theme = derive_theme(events, retro)

    # الاختيارات: نأخذ أبرز الأغراض إن لم تُحدَّد
    default_p = ["العقود والتوقيع", "بدء المشاريع", "الزواج والخِطبة",
                 "السفر البرّي", "الجراحة", "قصّ الشعر للنموّ",
                 "الشراء", "كتابة النوايا والدعاء"]
    cal = elections.month_calendar(year, month, tzname, lat, lon,
                                   purposes or default_p)

    figures = lunation_figures(events, tzname, lat, lon) if with_figures else []

    # تقويم المنازل: نأخذه من تقويم الاختيارات لتفادي إعادة الحساب
    mansions, prev = [], None
    for row in cal["days"]:
        if row["mansion"] != prev:
            mansions.append({"from": row["date"], "name": row["mansion"]})
            prev = row["mansion"]

    # ── النصّ ──
    head = {
        "daily":    f"#النشرة_الشهرية {MONTHS_AR[month-1]} {year}"
                    + (f" — {place}" if place else ""),
        "literary": f"{MONTHS_AR[month-1]} {year} — {theme['title']}",
        "classic":  f"القول في شهر {MONTHS_AR[month-1]} من سنة {year}",
    }[voice]

    lines = [head, "", theme["title"] + " — " + theme["note"], "",
             _summary(theme, events, retro, voice, year, month), ""]

    lines.append({"daily": "#الأحداث",
                  "literary": "أحداث الشهر",
                  "classic": "ذكر ما يحدث فيه"}[voice])
    for e in events:
        lines.append(("- " if voice == "daily" else "") + _line(e, voice))

    if retro:
        lines += ["", {"daily": "#الرجوع", "literary": "الكواكب الراجعة",
                       "classic": "ذكر الرواجع"}[voice]]
        for w in retro:
            lines.append(
                f"{'- ' if voice=='daily' else ''}{w['body']} راجع من "
                f"{_fmt_date(w['start'][:10])} إلى {_fmt_date(w['end'][:10])} "
                f"({w['days']:.0f} يومًا).")

    # أفضل الأيام
    lines += ["", {"daily": "#أفضل_الأيام", "literary": "أحمد أيام الشهر",
                   "classic": "ذكر الاختيارات"}[voice]]
    for p, r in cal["ranking"].items():
        best = "، ".join(f"{_fmt_day_num(b['date'])}" for b in r["best"][:3])
        worst = "، ".join(f"{_fmt_day_num(b['date'])}" for b in r["worst"][:2])
        lines.append(f"{'- ' if voice=='daily' else ''}{p}: أحمدها {best} — "
                     f"وتُتجنّب {worst}.")

    # ── القسم الشخصي ──
    personal = None
    if natal:
        from . import transits
        personal = transits.personal_month(natal, year, month, tzname,
                                           events=events)
        lines += ["", personal["text"]]

    text = "\n".join(lines)

    return {
        "personal": personal,
        "year": year, "month": month, "month_name": MONTHS_AR[month - 1],
        "tz": tzname, "place": place, "voice": voice,
        "voice_name": VOICES[voice], "voices": VOICES,
        "theme": theme,
        "summary": _summary(theme, events, retro, voice, year, month),
        "events": events,
        "retrograde_windows": retro,
        "figures": figures,
        "calendar": cal["days"],
        "ranking": cal["ranking"],
        "purposes": cal["purposes"],
        "mansions": mansions,
        "text": text,
    }
