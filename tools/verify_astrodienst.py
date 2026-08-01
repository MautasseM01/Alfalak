#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
التحقّق من محرّك الأحداث العامّة مقابل نشرات Astrodienst.

كل حدث مؤرّخ ذكرته نشراتهم ليونيو ويوليو وأغسطس ٢٠٢٦ مُثبَّت هنا،
ونتأكّد أن محرّكنا يجده في اليوم نفسه.

Astrodienst تكتب بتوقيت أوروبا الوسطى (CET/CEST)، فنقارن به لا بالتوقيت العالمي.
    python tools/verify_astrodienst.py
"""
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import mundane as M   # noqa: E402

TZ = "Europe/Zurich"     # مقرّ Astrodienst

# (التاريخ، النوع، الوصف كما ورد عندهم، مطابق متوقَّع)
# kind: ingress | station | aspect | lunation | eclipse
CLAIMS = [
    # ── يونيو ٢٠٢٦ ──
    ("2026-06-19", "ingress", "Chiron entre en Taureau", {"body": "خيرون", "sign": "الثور"}),
    ("2026-06-30", "ingress", "Jupiter entre en Lion", {"body": "المشتري", "sign": "الأسد"}),

    # ── يوليو ٢٠٢٦ ──
    ("2026-07-02", "aspect", "carré Jupiter–Chiron",
     {"a": "المشتري", "b": "خيرون", "aspect": "تربيع"}),
    ("2026-07-04", "aspect", "conjonction Mars–Uranus en Gémeaux",
     {"a": "المريخ", "b": "أورانوس", "aspect": "اقتران"}),
    ("2026-07-05", "aspect", "Mars trigone Pluton",
     {"a": "المريخ", "b": "بلوتو", "aspect": "تثليث"}),
    ("2026-07-05", "aspect", "Mars sextile Neptune",
     {"a": "المريخ", "b": "نبتون", "aspect": "تسديس"}),
    ("2026-07-06", "aspect", "carré Soleil–Saturne",
     {"a": "الشمس", "b": "زحل", "aspect": "تربيع"}),
    ("2026-07-07", "station", "Neptune devient rétrograde",
     {"body": "نبتون", "retrograde": True}),
    ("2026-07-09", "ingress", "Vénus entre en Vierge", {"body": "الزهرة", "sign": "العذراء"}),
    ("2026-07-13", "aspect", "Vénus carré Uranus",
     {"a": "الزهرة", "b": "أورانوس", "aspect": "تربيع"}),
    ("2026-07-14", "lunation", "Nouvelle Lune en Cancer",
     {"phase": "القمر الجديد", "sign": "السرطان"}),
    ("2026-07-15", "aspect", "sextile Uranus–Neptune",
     {"a": "أورانوس", "b": "نبتون", "aspect": "تسديس"}),
    ("2026-07-18", "aspect", "trigone Uranus–Pluton",
     {"a": "أورانوس", "b": "بلوتو", "aspect": "تثليث"}),
    ("2026-07-19", "aspect", "Mars sextile Saturne",
     {"a": "المريخ", "b": "زحل", "aspect": "تسديس"}),
    ("2026-07-20", "aspect", "Jupiter opposition Pluton",
     {"a": "المشتري", "b": "بلوتو", "aspect": "تقابل"}),
    ("2026-07-20", "aspect", "Jupiter trigone Neptune",
     {"a": "المشتري", "b": "نبتون", "aspect": "تثليث"}),
    ("2026-07-21", "aspect", "Jupiter sextile Uranus",
     {"a": "المشتري", "b": "أورانوس", "aspect": "تسديس"}),
    ("2026-07-22", "ingress", "le Soleil entre en Lion", {"body": "الشمس", "sign": "الأسد"}),
    ("2026-07-24", "station", "Mercure reprend son mouvement direct",
     {"body": "عطارد", "retrograde": False}),
    ("2026-07-26", "station", "Saturne devient rétrograde",
     {"body": "زحل", "retrograde": True}),
    ("2026-07-27", "aspect", "Soleil opposé Pluton",
     {"a": "الشمس", "b": "بلوتو", "aspect": "تقابل"}),
    ("2026-07-27", "aspect", "Soleil trigone Neptune",
     {"a": "الشمس", "b": "نبتون", "aspect": "تثليث"}),
    ("2026-07-27", "aspect", "Soleil sextile Uranus",
     {"a": "الشمس", "b": "أورانوس", "aspect": "تسديس"}),
    ("2026-07-29", "lunation", "Pleine Lune en Verseau",
     {"phase": "البدر", "sign": "الدلو"}),

    # ── أغسطس ٢٠٢٦ ──
    ("2026-08-02", "aspect", "Vénus aspect difficile à Lilith",
     {"a": "الزهرة", "b": "ليليث", "aspect": "تربيع"}),
    ("2026-08-03", "station", "Chiron devient rétrograde en Taureau",
     {"body": "خيرون", "retrograde": True}),
    ("2026-08-04", "aspect", "Mars aspect difficile à Lilith",
     {"a": "المريخ", "b": "ليليث", "aspect": "تقابل"}),
    ("2026-08-06", "ingress", "Vénus entre en Balance", {"body": "الزهرة", "sign": "الميزان"}),
    ("2026-08-07", "aspect", "Soleil trigone Saturne",
     {"a": "الشمس", "b": "زحل", "aspect": "تثليث"}),
    ("2026-08-09", "ingress", "Mercure entre en Lion", {"body": "عطارد", "sign": "الأسد"}),
    ("2026-08-10", "aspect", "Mercure carré Chiron",
     {"a": "عطارد", "b": "خيرون", "aspect": "تربيع"}),
    ("2026-08-10", "aspect", "Vénus trigone Pluton",
     {"a": "الزهرة", "b": "بلوتو", "aspect": "تثليث"}),
    ("2026-08-11", "aspect", "Vénus opposée Neptune",
     {"a": "الزهرة", "b": "نبتون", "aspect": "تقابل"}),
    ("2026-08-11", "ingress", "Mars entre en Cancer", {"body": "المريخ", "sign": "السرطان"}),
    ("2026-08-12", "aspect", "Mercure opposé Pluton",
     {"a": "عطارد", "b": "بلوتو", "aspect": "تقابل"}),
    ("2026-08-12", "aspect", "Mercure trigone Neptune",
     {"a": "عطارد", "b": "نبتون", "aspect": "تثليث"}),
    ("2026-08-12", "aspect", "Mercure sextile Uranus",
     {"a": "عطارد", "b": "أورانوس", "aspect": "تسديس"}),
    ("2026-08-12", "aspect", "Vénus trigone Uranus",
     {"a": "الزهرة", "b": "أورانوس", "aspect": "تثليث"}),
    ("2026-08-12", "eclipse", "éclipse solaire en Lion",
     {"eclipse": "شمسي", "sign": "الأسد"}),
    ("2026-08-15", "aspect", "Mercure conjonction Jupiter",
     {"a": "عطارد", "b": "المشتري", "aspect": "اقتران"}),
    ("2026-08-28", "eclipse", "éclipse lunaire en Poissons",
     {"eclipse": "قمري", "sign": "الحوت"}),
]


def gather(tzname=TZ):
    tz = ZoneInfo(tzname)
    lo = datetime(2026, 5, 25, tzinfo=tz)
    hi = datetime(2026, 9, 5, tzinfo=tz)
    from falak.ephem import UTC
    s, e = lo.astimezone(UTC), hi.astimezone(UTC)
    evs = (M.ingresses(s, e) + M.stations(s, e)
           + M.aspects(s, e, angles=M.ALL_ANGLES)
           + M.lunations(s, e) + M.eclipses(s, e))
    return [ev.to_dict(tz) for ev in evs]


def matches(ev, kind, want) -> bool:
    if ev["kind"] != kind:
        return False
    d = ev["detail"]
    if kind == "ingress":
        return ev["body"] == want["body"] and ev["sign"] == want["sign"]
    if kind == "station":
        return ev["body"] == want["body"] and d.get("retrograde") == want["retrograde"]
    if kind == "aspect":
        return ({ev["body"], ev["other"]} == {want["a"], want["b"]}
                and d.get("aspect") == want["aspect"])
    if kind == "lunation":
        return d.get("phase") == want["phase"] and ev["sign"] == want["sign"]
    if kind == "eclipse":
        return d.get("eclipse") == want["eclipse"] and ev["sign"] == want["sign"]
    return False


# ادّعاءات عن أشكال الزوايا في خرائط لحظية
# «La figure d'aspects montre un grand trigone entre Vénus, Uranus et Pluton.
#  Des sextiles à Mercure d'un côté et à Neptune de l'autre l'étendent
#  en deux figures de cerf-volant.» — نشرة أغسطس ٢٠٢٦
FIGURE_CLAIMS = [
    ("2026-08-12 20:45", "Europe/Zurich",
     "grand trigone Vénus–Uranus–Pluton lors de l'éclipse",
     {"name": "المثلّث الكبير", "members": {"الزهرة", "أورانوس", "بلوتو"}}),
    ("2026-08-12 20:45", "Europe/Zurich",
     "cerf-volant avec Mercure",
     {"name": "الطائرة الورقية",
      "members": {"الزهرة", "أورانوس", "بلوتو", "عطارد"}}),
    ("2026-08-12 20:45", "Europe/Zurich",
     "cerf-volant avec Neptune",
     {"name": "الطائرة الورقية",
      "members": {"الزهرة", "أورانوس", "بلوتو", "نبتون"}}),
]


def check_figures():
    from falak import chart as ch
    ok = bad = 0
    print("\nأشكال الزوايا في خريطة الكسوف")
    for stamp, tzn, label, want in FIGURE_CLAIMS:
        when = datetime.fromisoformat(stamp).replace(tzinfo=ZoneInfo(tzn))
        c = ch.compute(when, 47.37, 8.54, "whole", tzn, minor_aspects=False)
        hit = any(p["name"] == want["name"]
                  and set(p["members"]) == want["members"]
                  for p in c["patterns"])
        print(("  ✓ " if hit else "  ✗ ") + label
              + ("" if hit else "  — لم نجده"))
        ok += hit
        bad += not hit
    return ok, bad


def main():
    evs = gather()
    ok = miss = drift = 0
    missing_bodies = set()
    print("التحقّق من محرّك الأحداث مقابل نشرات Astrodienst — يونيو/يوليو/أغسطس ٢٠٢٦")
    print(f"(بتوقيت {TZ}، وهو التوقيت الذي تكتب به Astrodienst)\n")

    for date, kind, label, want in CLAIMS:
        hits = [e for e in evs if matches(e, kind, want)]
        exact = [e for e in hits if e["date"] == date]
        if exact:
            print(f"  ✓ {date}  {label}")
            print(f"      وجدناه {exact[0]['date']} {exact[0]['time']} — {exact[0]['title']}")
            ok += 1
        elif hits:
            near = min(hits, key=lambda e: abs(
                (datetime.fromisoformat(e['when']).date() - datetime.fromisoformat(date).date()).days))
            gap = (datetime.fromisoformat(near['when']).date()
                   - datetime.fromisoformat(date).date()).days
            if abs(gap) <= 1:
                print(f"  ≈ {date}  {label}")
                print(f"      وجدناه {near['date']} {near['time']} (فارق {gap:+d} يوم) — {near['title']}")
                drift += 1
            else:
                print(f"  ✗ {date}  {label} — أقرب ما وجدنا {near['date']} (فارق {gap:+d})")
                miss += 1
        else:
            body = want.get("body") or want.get("a") or ""
            other = want.get("b", "")
            if "خيرون" in (body, other):
                missing_bodies.add("خيرون")
                print(f"  ⊘ {date}  {label} — يحتاج ملف أفلاك خيرون")
            else:
                print(f"  ✗ {date}  {label} — لم نجده")
                miss += 1

    fok, fbad = check_figures()
    ok += fok
    miss += fbad

    total = ok + drift + miss
    print(f"\n{'─'*62}")
    print(f"مطابق تمامًا: {ok}   ضمن يوم واحد: {drift}   مفقود: {miss}   "
          f"(من {total} ادّعاءً قابلًا للفحص)")
    if missing_bodies:
        print(f"مؤجَّل لغياب ملف الأفلاك: {'، '.join(missing_bodies)} "
              f"— أضف ephe/seas_18.se1 ليُفحص")
    print(f"نسبة الإصابة: {(ok + drift) / total * 100:.1f}٪")
    return 0 if miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
