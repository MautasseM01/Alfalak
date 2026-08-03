# -*- coding: utf-8 -*-
"""
التحقّق من الجيوتِش بمراجع خارجية.

لا نُصدّق أنفسنا. فكما قارنّا الفلك العربي بنشرات Astrodienst، نقارن
هنا بأربعة مراجع مستقلّة عنّا:

١. **نجم تشيترا نفسه.** أينامشا لاهيري مُعرَّفة بأن السماك الأعزل
   (Spica) على ١٨٠ درجة نجمية بالضبط — ومن هنا سُمّيت «تشيترا باكشا».
   فإن لم يقع النجم على ١٨٠° فحسابنا خاطئ، ولا مجال للجدال.

٢. **جدول لاهيري المنشور** في التقويم الرسمي الهندي، بقيم معروفة
   لسنوات ١٩٠٠ و١٩٥٠ و٢٠٠٠.

٣. **نجوم النكشترا.** كريتِّكا هي الثريّا، وروهيني هي الدبران،
   وجيِشتها هي قلب العقرب. فنحسب موضع كل نجم ونتحقّق أنه يقع في
   منزلته المزعومة — وهذا يفحص حدود النكشترا وأسماءها معًا.

٤. **دورة الدشا**: مجموعها مئة وعشرون سنة بالضبط، وترتيبها ثابت.

    python tools/verify_jyotish.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import swisseph as swe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import chart as ch, ephem, jyotish as jy   # noqa: E402

UTC = timezone.utc
OK, BAD = 0, 0


def check(label, got, want, tol, unit="°"):
    global OK, BAD
    diff = abs(got - want)
    good = diff <= tol
    mark = "✓" if good else "✗"
    if good:
        OK += 1
    else:
        BAD += 1
    print(f"  {mark} {label}: {got:.4f}{unit} "
          f"(المرجع {want:.4f}{unit}، الفارق {diff * 60:.2f}′)")


def check_bool(label, cond, note=""):
    global OK, BAD
    if cond:
        OK += 1
        print(f"  ✓ {label}")
    else:
        BAD += 1
        print(f"  ✗ {label} — {note}")


def star_sid(name, when, ayan="lahiri"):
    """الطول النجمي لنجم ثابت."""
    jy._sid(ayan)
    jd = ephem.to_jd(when)
    res = swe.fixstar_ut(name, jd, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    return res[0][0] % 360.0


def main():
    now = datetime(2000, 1, 1, 12, tzinfo=UTC)

    print("\n١ — تعريف لاهيري نفسه: السماك الأعزل على ١٨٠° نجمية")
    print("   (وهذا ليس رأيًا: به تُعرَّف الأينامشا، فإن أخطأناه أخطأنا كلّ شيء)")
    for year in (1900, 2000, 2100):
        t = datetime(year, 1, 1, 12, tzinfo=UTC)
        try:
            check(f"Spica سنة {year}", star_sid("Spica", t), 180.0, 0.02)
        except Exception as exc:
            print(f"  ! تعذّر: {exc}")

    print("\n٢ — جدول لاهيري المنشور في التقويم الهندي الرسمي")
    for when, want, label in [
        (datetime(1900, 1, 1, tzinfo=UTC), 22.4594, "١ يناير ١٩٠٠"),
        (datetime(1950, 1, 1, tzinfo=UTC), 23.1589, "١ يناير ١٩٥٠"),
        (datetime(2000, 1, 1, tzinfo=UTC), 23.8531, "١ يناير ٢٠٠٠"),
    ]:
        check(label, jy.ayanamsha(when, "lahiri"), want, 0.01)

    print("\n٣ — العلاقة الصحيحة بين المقياسين")
    print("   ظننّا أوّلًا أن النجمي = الاستوائي ناقص الأينامشا، فخالفَنا")
    print("   الحساب بـ١٤ ثانية قوسية. والسبب اهتزاز محور الأرض:")
    print("   الاستوائي الظاهري يحمله، والأينامشا تُقاس من الاعتدال المتوسّط.")
    jy._sid("lahiri")
    jd = ephem.to_jd(now)
    trop = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360
    mean = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_NONUT)[0][0] % 360
    sid = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
    ay = jy.ayanamsha(now)
    check("بلا اهتزاز ناقص النجمي", (mean - sid) % 360, ay, 1e-7)
    check_bool(
        f"ومع الاهتزاز يفرق بـ{abs((trop - sid) % 360 - ay) * 3600:.1f} ثانية"
        " — وهذا صواب لا خطأ",
        1 < abs((trop - sid) % 360 - ay) * 3600 < 20)

    print("\n٤ — نجوم النكشترا: أين تقع من حدودها المتساوية؟")
    print("   ظننّا أن كل نجم داخل منزلته، فخرج أربعة منها. وليس ذلك")
    print("   خطأ حساب: المنازل كانت غير متساوية ثم سُوّيت إلى ١٣°٢٠′،")
    print("   فبقيت الأسماء على نجومها وخرج بعضها. فالفحص الصحيح أن")
    print("   يكون النجم في منزلته أو في التي تجاورها مباشرة.")
    for idx, star in sorted(jy.YOGATARA.items()):
        y = jy.yogatara(idx, now)
        if not y:
            print(f"  ! {star}: تعذّر")
            continue
        got = jy.nakshatra_of(y["lon"])["index"]
        near = (got - idx) % 27 in (0, 1, 26)
        nak = jy.NAKSHATRAS[idx - 1]
        where = "داخلها" if y["inside"] else f"خارجها بـ{y['offset']:.2f}°"
        check_bool(f"{star:11s} ← {nak[0]} ({nak[2]}): {where}", near,
                   f"بعيد: وجدناه في المنزلة {got} لا {idx}")

    print("\n٥ — حدود المنازل: ١٣° ٢٠′ لكلٍّ، وسبع وعشرون تُغطّي الفلك")
    check("عرض المنزلة", jy.NAK_ARC, 13 + 20 / 60, 1e-9)
    check_bool("٢٧ منزلة مسمّاة", len(jy.NAKSHATRAS) == 27)
    check_bool("أوّل المنازل عند صفر الحمل النجمي",
               jy.nakshatra_of(0.001)["index"] == 1)
    check_bool("آخر المنازل عند ٣٦٠°",
               jy.nakshatra_of(359.99)["index"] == 27)
    check_bool("أرباع المنزلة أربعة",
               jy.nakshatra_of(NAK := 0.0)["pada"] == 1
               and jy.nakshatra_of(jy.NAK_ARC - 0.01)["pada"] == 4)

    print("\n٦ — دورة فِمْشوتَّري")
    total = sum(jy.DASHA_YEARS.values())
    check("مجموع سني الدورة", total, 120.0, 0)
    check_bool("تسعة أرباب بالترتيب المنصوص",
               jy.DASHA_ORDER == ["الذنب", "الزهرة", "الشمس", "القمر",
                                  "المريخ", "الرأس", "المشتري", "زحل",
                                  "عطارد"])
    check_bool("ربّ المنزلة الأولى هو ربّ أوّل الدورة",
               jy.NAKSHATRAS[0][1] == jy.DASHA_ORDER[0])
    lords = [n[1] for n in jy.NAKSHATRAS]
    check_bool("أرباب المنازل تدور كل تسع",
               all(lords[i] == lords[i % 9] for i in range(27)))

    print("\n٧ — الدشا من مولد مرجعي: الاتّصال والاستمرار")
    birth = datetime(1990, 5, 17, 5, 30, tzinfo=UTC)
    c = jy.compute(birth, 36.2021, 37.1343, "lahiri", "UTC")
    moon = next(b for b in c["bodies"] if b["name"] == "القمر")
    d = jy.vimshottari(birth, moon["lon"])
    ps = d["periods"]
    gaps = [abs((datetime.fromisoformat(ps[i + 1]["start"])
                 - datetime.fromisoformat(ps[i]["end"])).total_seconds())
            for i in range(len(ps) - 1)]
    check_bool("الفترات متّصلة بلا فجوة ولا تداخل", max(gaps) < 1,
               f"أكبر فجوة {max(gaps):.1f} ثانية")
    check_bool("الفترة الأولى ناقصة (ما بقي من المنزلة)", ps[0]["partial"])
    # الفترة الأولى ناقصة، فالدورة الكاملة تبدأ من الثانية:
    # تسع فترات متتالية من ps[1] مجموعها ١٢٠ سنة بالضبط.
    cycle = sum(p["years"] for p in ps[1:10])
    check("دورة كاملة من الفترة الثانية", cycle, 120.0, 1e-6, " سنة")
    check_bool("وتعود إلى ربّ البداية بعدها",
               len(ps) > 9 and ps[9 + 1 - 1]["planet"] == ps[0]["planet"]
               if len(ps) > 9 else True)
    subs = ps[1].get("sub") or []
    check_bool("الفترات الصغرى تسع، ومجموعها الكبرى",
               len(subs) == 9
               and abs(sum(s["years"] for s in subs) - ps[1]["years"]) < 1e-6)

    print("\n٨ — الذروة على درجتها: الشمس ١٠° الحمل النجمي")
    #  نبحث عن اليوم الذي تبلغ فيه الشمس تلك الدرجة، ونتحقّق أن
    #  حسابنا يعدّها ذروة
    jy._sid("lahiri")
    t = datetime(2026, 4, 1, tzinfo=UTC)
    for _ in range(60):
        jdx = ephem.to_jd(t)
        L = swe.calc_ut(jdx, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
        if 9.5 <= L < 10.5:
            break
        t += timedelta(days=1)
    dig = jy.dignity_of("الشمس", ch.SIGNS[int(L // 30)], L % 30)
    check_bool(f"الشمس على {L:.2f}° نجمية يوم {t:%Y-%m-%d}: {dig['kind']}",
               dig["kind"] == "الذروة")

    print("\n" + "─" * 62)
    print(f"مطابق: {OK}   مخالف: {BAD}   "
          f"النسبة: {100 * OK / max(1, OK + BAD):.1f}٪")
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
