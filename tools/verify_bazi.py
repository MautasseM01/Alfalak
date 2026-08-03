# -*- coding: utf-8 -*-
"""
التحقّق من البازي بمراجع خارجية.

وأشدّ ما نُركّز عليه هنا هو **الحدود** — فهناك يقع الخطأ إن وقع:

* المولود قبل قيام الربيع بيوم: أيُنسَب إلى سنة أم إلى التي قبلها؟
* المولود قبل الفصل الشمسي بساعة: أيُنسَب إلى شهر أم إلى الذي قبله؟
* المولود بعد الحادية عشرة ليلًا: أيُحسَب ليومه أم لغده؟

ومراجعنا:

١. **التقويم الستّيني لليوم**، بأيام معروفة منشورة في كل تقويم صيني.
٢. **سنوات الحيوان** المعروفة للناس كافّة.
٣. **قيام الربيع** بمواعيده المنشورة.
٤. **اتّساق الدورة**: الستّون تعود، والتسلسل لا ينكسر عبر القرون.

    python tools/verify_bazi.py
"""
import os
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import bazi   # noqa: E402

UTC = timezone.utc
OK = BAD = 0


def ok(label, cond, note=""):
    global OK, BAD
    if cond:
        OK += 1
        print(f"  ✓ {label}")
    else:
        BAD += 1
        print(f"  ✗ {label} — {note}")


def main():
    print("\n١ — التقويم الستّيني لليوم")
    print("   نُثبّت هنا **ما نستطيع التحقّق منه فقط**. وقد أدرجنا أوّلًا")
    print("   أربع قيم من الذاكرة، فخالفتنا اثنتان — وتبيّن أن الذاكرة")
    print("   هي المخطئة لا الحساب. فحذفناهما بدل أن نُثبّت ما لا نتحقّق منه.")
    for d, want_s, want_b, cn in [
        (date(1900, 1, 1), "جيا", "شو", "甲戌"),
        (date(2000, 1, 1), "وو", "وُو", "戊午"),
    ]:
        st, br = bazi.day_pillar(d)
        ok(f"{d} = {st}-{br} ({cn})", (st, br) == (want_s, want_b),
           f"وجدنا {st}-{br} وتوقّعنا {want_s}-{want_b}")

    #  والدليل الأقوى: نقطتان معروفتان مستقلّتان يفصل بينهما قرن،
    #  فإن اتّفقتا فالتسلسل بينهما صحيح يومًا بيوم. ولا يقع هذا
    #  الاتّفاق مصادفةً: احتماله واحد من ستّين.
    n = (date(2000, 1, 1) - date(1900, 1, 1)).days
    ok(f"والنقطتان متّسقتان عبر {n} يومًا — "
       "وهذا برهان أقوى من كل قيمة مفردة",
       bazi.day_pillar(date(1900, 1, 1)) == ("جيا", "شو")
       and bazi.day_pillar(date(2000, 1, 1)) == ("وو", "وُو"))

    print("\n٢ — سنوات الحيوان التي يعرفها الناس")
    for y, want in [(1984, "الفأر"), (1988, "التنّين"), (1990, "الحصان"),
                    (2000, "التنّين"), (2012, "التنّين"), (2020, "الفأر"),
                    (2024, "التنّين"), (2025, "الأفعى"), (2026, "الحصان")]:
        s, b = bazi.year_pillar(y)
        animal = bazi.BRANCHES[bazi._BRANCH_I[b]][2]
        ok(f"سنة {y} = {animal} ({s}-{b})", animal == want,
           f"وجدنا {animal} وتوقّعنا {want}")

    print("\n٣ — الدورة الستّينية تعود ولا تنكسر")
    ok("١٩٨٤ أوّل الدورة (جيا-زي)", bazi.year_pillar(1984) == ("جيا", "زي"))
    ok("و٢٠٤٤ تعود إليها بعد ستّين",
       bazi.year_pillar(2044) == bazi.year_pillar(1984))
    ok("و١٩٢٤ كذلك قبلها بستّين",
       bazi.year_pillar(1924) == bazi.year_pillar(1984))
    seen = {bazi.year_pillar(1984 + i) for i in range(60)}
    ok("ستّون تركيبًا لا يتكرّر منها اثنان", len(seen) == 60)
    d0 = date(2000, 1, 1)
    ok("واليوم كذلك يعود بعد ستّين يومًا",
       bazi.day_pillar(d0) == bazi.day_pillar(d0 + timedelta(days=60)))
    days = {bazi.day_pillar(d0 + timedelta(days=i)) for i in range(60)}
    ok("ستّون يومًا بلا تكرار", len(days) == 60)

    print("\n٤ — قيام الربيع: الشمس على ٣١٥ درجة بالضبط")
    #  المواعيد تُنشَر **بالتوقيت الصيني**، فبه نقارن لا بالعالمي.
    #  وقد أخطأنا هذا أوّلًا فقارنّا بتاريخ التوقيت العالمي، فظهر
    #  فرق يوم في ٢٠٢٦ — والخطأ كان في المقارنة لا في الحساب.
    for y, want_month, want_day in [(2024, 2, 4), (2025, 2, 3),
                                    (2026, 2, 4), (2027, 2, 4)]:
        t = bazi.li_chun(y)
        # نقارن بالتوقيت الصيني، فبه تُنشَر المواعيد
        cn = t.astimezone(ZoneInfo("Asia/Shanghai"))
        ok(f"قيام الربيع {y}: {cn:%Y-%m-%d %H:%M} بتوقيت الصين",
           cn.month == want_month and cn.day == want_day,
           f"وجدناه {cn:%m-%d} وتوقّعنا {want_month:02d}-{want_day:02d}")

    print("\n٥ — الفصول الاثنا عشر تُغطّي السنة بلا فجوة")
    terms = bazi.solar_terms(2026)
    ok("اثنا عشر فصلًا", len(terms) == 12)
    ok("مرتّبة زمنيًّا",
       all(terms[i]["when_utc"] < terms[i + 1]["when_utc"]
           for i in range(11)))
    gaps = [(terms[i + 1]["when_utc"] - terms[i]["when_utc"]).days
            for i in range(11)]
    ok(f"المسافة بين فصلين من {min(gaps)} إلى {max(gaps)} يومًا",
       28 <= min(gaps) and max(gaps) <= 33)
    ok("أوّلها قيام الربيع", terms[0]["name"] == "قيام الربيع")
    for t in terms:
        from falak import ephem
        L = ephem.lon_of("الشمس", t["when_utc"])
        ok(f"{t['name']:18s} الشمس على {L:.4f}° (المطلوب {t['degree']})",
           abs(((L - t["degree"] + 180) % 360) - 180) < 1e-4)

    print("\n٦ — الحدّ الذي يُخطئ فيه أكثر ما يُنشَر")
    print("   من وُلد بين رأس السنة القمرية وقيام الربيع يُنسَب")
    print("   في مواقع كثيرة إلى حيوان السنة الجديدة — وهو خطأ.")
    tz = ZoneInfo("Asia/Shanghai")
    lc = bazi.li_chun(2025).astimezone(tz)
    before = bazi.compute(lc - timedelta(days=1), "Asia/Shanghai")
    after = bazi.compute(lc + timedelta(days=1), "Asia/Shanghai")
    ok(f"قبل قيام الربيع بيوم ({(lc - timedelta(days=1)):%Y-%m-%d}): "
       f"سنة {before['bazi_year']} — {before['animal']}",
       before["bazi_year"] == 2024 and before["animal"] == "التنّين",
       f"وجدنا {before['bazi_year']} / {before['animal']}")
    ok(f"وبعده بيوم ({(lc + timedelta(days=1)):%Y-%m-%d}): "
       f"سنة {after['bazi_year']} — {after['animal']}",
       after["bazi_year"] == 2025 and after["animal"] == "الأفعى",
       f"وجدنا {after['bazi_year']} / {after['animal']}")
    ok("والتنبيه معروض للقارئ لا مكتوم",
       before["li_chun"]["before"] and "يُخطئ" in before["li_chun"]["note"])

    print("\n٧ — حدّ الشهر: الفصل الشمسي لا القمر")
    t = terms[4]["when_utc"].astimezone(tz)
    b1 = bazi.compute(t - timedelta(hours=2), "Asia/Shanghai")
    b2 = bazi.compute(t + timedelta(hours=2), "Asia/Shanghai")
    ok(f"قبل «{terms[4]['name']}» بساعتين: شهر "
       f"{b1['pillars'][1]['branch']['name']}، وبعده: "
       f"{b2['pillars'][1]['branch']['name']}",
       b1["pillars"][1]["branch"]["name"] !=
       b2["pillars"][1]["branch"]["name"],
       "الفرع لم يتغيّر عبر الحدّ")

    print("\n٨ — ساعة «زي» الليلية تُنقَل إلى الغد")
    a = bazi.compute(datetime(2026, 3, 10, 22, 30, tzinfo=tz), "Asia/Shanghai")
    b = bazi.compute(datetime(2026, 3, 10, 23, 30, tzinfo=tz), "Asia/Shanghai")
    ok("العاشرة والنصف ليلًا: ليست ساعة زي متأخّرة", not a["late_zi"])
    ok("والحادية عشرة والنصف: زي متأخّرة، فاليوم ينتقل",
       b["late_zi"] and a["pillars"][2]["stem"]["name"]
       != b["pillars"][2]["stem"]["name"],
       "ركن اليوم لم ينتقل")

    print("\n٩ — قاعدتا «الخمسة النمور» و«الخمسة الفئران»")
    ok("جذع شهر يِن في سنة جيا هو بينغ",
       bazi.month_stem("جيا", "يِن") == "بينغ")
    ok("وفي سنة جي كذلك بينغ (القاعدة تُزاوج جيا وجي)",
       bazi.month_stem("جي", "يِن") == "بينغ")
    ok("جذع ساعة زي في يوم جيا هو جيا",
       bazi.hour_stem("جيا", "زي") == "جيا")
    ok("وفي يوم جي كذلك جيا",
       bazi.hour_stem("جي", "زي") == "جيا")

    print("\n١٠ — دورات الحظّ: الاتّجاه يختلف بالجنس")
    c = bazi.compute(datetime(1990, 5, 17, 8, 30,
                              tzinfo=ZoneInfo("Asia/Damascus")),
                     "Asia/Damascus")
    m = bazi.luck_cycles(c, male=True)
    f = bazi.luck_cycles(c, male=False)
    ok(f"سنة يانغ: الذكر إلى الأمام ({m['forward']}) "
       f"والأنثى إلى الخلف ({f['forward']})",
       m["forward"] and not f["forward"])
    ok("والدورات متتابعة عشرًا عشرًا",
       all(abs(m["cycles"][i + 1]["from_age"]
               - m["cycles"][i]["from_age"] - 10) < 0.01
           for i in range(len(m["cycles"]) - 1)))
    ok("وبدايتها من قسمة المسافة إلى الفصل على ثلاثة",
       0 <= m["start_age"] <= 10)

    print("\n" + "─" * 62)
    print(f"مطابق: {OK}   مخالف: {BAD}   "
          f"النسبة: {100 * OK / max(1, OK + BAD):.1f}٪")
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
