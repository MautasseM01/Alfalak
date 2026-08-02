# -*- coding: utf-8 -*-
"""
شبكة الأمان — أرقام مرجعية مثبَّتة.

الغرض من هذه الاختبارات ليس إثبات أن الشيفرة تعمل، بل أن تصرخ إن تغيّر
رقم كان صحيحًا. أخطر ما في مشروع حسابي أن ينكسر شيء **صامتًا**: كاشف
الأشكال ظلّ يُسقط الكواكب الخارجية من أول يوم، ولولا نشرة خارجية
قارنّاها به ما انكشف.

فكل رقم هنا تحقّقنا منه بمرجع خارجي أو بقاعدة تراثية صريحة، وهو الآن
مثبَّت. إن كسره تغيير، فالتغيير هو المتّهم.

    pytest -q
"""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from falak import (atlas, bulletin, chart, dignities as dig, elections,
                   ephem, hours, monthly, mundane, parts, patterns, transits)
from falak import timezone as ftz

DAMASCUS = (33.5138, 36.2765, "Asia/Damascus")
ALEPPO = (36.2021, 37.1343, "Asia/Damascus")
UTC = timezone.utc


# ══════════════════════════════════════════════════════════════════
# ١ — المواقع: مقابل جدول Astrotheme المباشر ٢٧ يوليو ٢٠٢٦، ٢٠:١٤ ت.ع
#     (١٢ جِرمًا طابقت إلى الدقيقة القوسية)
# ══════════════════════════════════════════════════════════════════
ASTROTHEME = {
    "الشمس": "4° 49′ الأسد",
    "القمر": "15° 10′ الجدي",
    "عطارد": "17° 03′ السرطان",
    "الزهرة": "19° 42′ العذراء",
    "المريخ": "20° 15′ الجوزاء",
    "المشتري": "6° 02′ الأسد",
    "زحل": "14° 45′ الحمل",
    "أورانوس": "4° 52′ الجوزاء",
    "نبتون": "4° 18′ الحمل",
    "بلوتو": "4° 16′ الدلو",
    "خيرون": "0° 51′ الثور",
    "الرأس": "29° 57′ الدلو",
    "ليليث الحقيقية": "21° 27′ القوس",
}


@pytest.mark.parametrize("body,expected", sorted(ASTROTHEME.items()))
def test_positions_match_astrotheme(body, expected):
    when = datetime(2026, 7, 27, 20, 14, tzinfo=UTC)
    c = chart.compute(when, *DAMASCUS[:2], "whole", DAMASCUS[2])
    got = next((b["text"] for b in c["bodies"] if b["name"] == body), None)
    assert got == expected, f"{body}: توقّعنا {expected} ووجدنا {got}"


def test_retrogrades_match_astrotheme():
    """زحل ونبتون وبلوتو والرأس راجعة في ذلك التاريخ، وسواها مستقيم."""
    when = datetime(2026, 7, 27, 20, 14, tzinfo=UTC)
    c = chart.compute(when, *DAMASCUS[:2], "whole", DAMASCUS[2])
    retro = {b["name"] for b in c["bodies"] if b["retro"]}
    assert {"زحل", "نبتون", "بلوتو", "الرأس"} <= retro
    assert "الشمس" not in retro and "المشتري" not in retro


def test_full_moon_within_a_minute():
    """Astrodienst: البدر ٢٩ يوليو ٢٠٢٦ الساعة ١٤:٣٧ ت.ع."""
    lun = mundane.lunations(datetime(2026, 7, 29, tzinfo=UTC),
                            datetime(2026, 7, 30, tzinfo=UTC))
    full = [e for e in lun if e.detail["phase"] == "البدر"]
    assert len(full) == 1
    diff = abs((full[0].when - datetime(2026, 7, 29, 14, 37, tzinfo=UTC)).total_seconds())
    assert diff < 120, f"فارق {diff/60:.1f} دقيقة عن مرجع Astrodienst"


# ══════════════════════════════════════════════════════════════════
# ٢ — خريطة مرجعية: حلب، ١٧ مايو ١٩٩٠، ٠٨:٣٠
# ══════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def natal():
    res = ftz.resolve(datetime(1990, 5, 17, 8, 30), ALEPPO[2], ALEPPO[1])
    return chart.compute(res["when"], ALEPPO[0], ALEPPO[1], "whole",
                         ALEPPO[2], tz_info=res)


def test_angles(natal):
    assert natal["angles"]["الطالع"]["text"] == "11° 22′ السرطان"
    assert natal["angles"]["وسط السماء"]["text"] == "23° 47′ الحوت"


def test_sect_is_diurnal(natal):
    """الشمس فوق الأفق صباحًا، فالخريطة نهارية."""
    assert natal["sect"] == "نهارية"


def test_almuten(natal):
    assert natal["almuten"]["winner"] == "الزهرة"
    assert natal["almuten"]["score"] == 20


def test_dignities(natal):
    by = {b["name"]: b for b in natal["bodies"]}
    assert "البيت" in by["زحل"]["dignity"]        # زحل في الجدي
    assert "الشرف" in by["المشتري"]["dignity"]     # المشتري في السرطان
    assert "الوبال" in by["الزهرة"]["dignity"]     # الزهرة في الحمل


def test_lots(natal):
    assert len(natal["lots"]) == 18
    fortune = next(L for L in natal["lots"] if L["key"] == "fortune")
    assert fortune["text"] == "4° 14′ الحمل"


def test_fixed_star_algol(natal):
    """الشمس على رأس الغول بوجاج ٠.٠٤° — تحقّق من التقدّم أيضًا."""
    hit = next((s for s in natal["stars"]
                if s["body"] == "الشمس" and s["star"] == "رأس الغول"), None)
    assert hit and hit["orb"] < 0.1


def test_house_systems_agree_on_angles(natal):
    """الطالع ووسط السماء لا يتغيّران بتغيّر نظام البيوت."""
    res = ftz.resolve(datetime(1990, 5, 17, 8, 30), ALEPPO[2], ALEPPO[1])
    for sysname in chart.HOUSE_SYSTEMS:
        c = chart.compute(res["when"], ALEPPO[0], ALEPPO[1], sysname,
                          ALEPPO[2], tz_info=res)
        assert c["angles"]["الطالع"]["text"] == natal["angles"]["الطالع"]["text"], sysname


# ══════════════════════════════════════════════════════════════════
# ٣ — التوقيت التاريخي
# ══════════════════════════════════════════════════════════════════
def test_nonexistent_hour_detected():
    """٣١ مارس ٢٠٢٤ الساعة ٠٢:٣٠ لم توجد بباريس — قُدِّمت الساعة فوقها."""
    r = ftz.resolve(datetime(2024, 3, 31, 2, 30), "Europe/Paris", 2.35)
    assert r["nonexistent"] and not r["ambiguous"]
    assert any("لم توجد" in w for w in r["warnings"])


def test_ambiguous_hour_detected():
    """٢٧ أكتوبر ٢٠٢٤ الساعة ٠٢:٣٠ تكرّرت مرّتين بباريس."""
    r = ftz.resolve(datetime(2024, 10, 27, 2, 30), "Europe/Paris", 2.35)
    assert r["ambiguous"] and not r["nonexistent"]


def test_pre_standard_time_uses_lmt():
    r = ftz.resolve(datetime(1875, 3, 10, 6, 0), "Africa/Cairo", 31.24)
    assert r["mode"] == "lmt"


def test_syria_dst_history():
    """سوريا ألغت التوقيت الصيفي سنة ٢٠٢٢، فصارت +3 طول السنة."""
    summer = ftz.resolve(datetime(2005, 7, 15, 14, 0), "Asia/Damascus", 36.28)
    winter = ftz.resolve(datetime(2025, 1, 15, 14, 0), "Asia/Damascus", 36.28)
    assert summer["is_dst"] and not winter["is_dst"]
    assert summer["offset_text"] == winter["offset_text"] == "+03:00"


# ══════════════════════════════════════════════════════════════════
# ٤ — الكرامات: قواعد تراثية صريحة
# ══════════════════════════════════════════════════════════════════
def test_egyptian_terms_wellformed():
    for sign, rows in dig.TERMS.items():
        assert rows[-1][1] == 30, sign
        planets = [p for p, _ in rows]
        assert len(set(planets)) == 5, sign
        assert "الشمس" not in planets and "القمر" not in planets, sign
        assert all(rows[i][1] < rows[i + 1][1] for i in range(4)), sign


def test_chaldean_faces():
    assert dig.FACES["الحمل"] == ["المريخ", "الشمس", "الزهرة"]
    assert dig.FACES["الحوت"] == ["زحل", "المشتري", "المريخ"]


def test_detriment_and_fall():
    assert dig.detriment_of("الحمل") == "الزهرة"
    assert dig.fall_of("الميزان") == "الشمس"
    assert dig.fall_of("العقرب") == "القمر"


def test_sun_at_exaltation_degree():
    """الشمس في ١٩° الحمل: شرف + درجة الشرف + مثلثة نهارية + وجه."""
    e = dig.evaluate("الشمس", 19.0, is_day=True)
    assert "الشرف" in e["dignities"] and "درجة الشرف" in e["dignities"]
    assert e["score"] == 8


def test_peregrine_is_penalised():
    e = dig.evaluate("القمر", 0.5, is_day=True)     # ٠° الحمل: لا كرامة
    assert e["peregrine"] and e["score"] < 0


# ══════════════════════════════════════════════════════════════════
# ٥ — أشكال الزوايا (الخلل الصامت الذي كُشف بنشرة Astrodienst)
# ══════════════════════════════════════════════════════════════════
def test_eclipse_kite_figures():
    """
    نشرة Astrodienst لأغسطس ٢٠٢٦: خريطة الكسوف فيها مثلّث كبير بين
    الزهرة وأورانوس وبلوتو، وتسديسان إلى عطارد ونبتون يمدّانه
    إلى طائرتين ورقيتين.
    """
    when = datetime(2026, 8, 12, 20, 45, tzinfo=ZoneInfo("Europe/Zurich"))
    c = chart.compute(when, 47.37, 8.54, "whole", "Europe/Zurich",
                      minor_aspects=False)
    got = {(p["name"], frozenset(p["members"])) for p in c["patterns"]}
    assert ("المثلّث الكبير",
            frozenset({"الزهرة", "أورانوس", "بلوتو"})) in got
    assert ("الطائرة الورقية",
            frozenset({"الزهرة", "أورانوس", "بلوتو", "عطارد"})) in got
    assert ("الطائرة الورقية",
            frozenset({"الزهرة", "أورانوس", "بلوتو", "نبتون"})) in got


def test_outer_planets_included_in_patterns():
    """الحارس المباشر للخلل: الكواكب الخارجية تدخل في الأشكال."""
    bodies = [
        {"name": "الزهرة", "lon": 0.0, "sign": "الحمل", "house": 1, "core": True},
        {"name": "أورانوس", "lon": 120.0, "sign": "الأسد", "house": 5, "core": False},
        {"name": "بلوتو", "lon": 240.0, "sign": "القوس", "house": 9, "core": False},
    ]
    asps = [{"a": "الزهرة", "b": "أورانوس", "angle": 120},
            {"a": "أورانوس", "b": "بلوتو", "angle": 120},
            {"a": "الزهرة", "b": "بلوتو", "angle": 120}]
    found = patterns.detect(bodies, asps)
    assert any(p["name"] == "المثلّث الكبير" for p in found)


# ══════════════════════════════════════════════════════════════════
# ٦ — الأحداث العامّة
# ══════════════════════════════════════════════════════════════════
def test_august_2026_eclipses():
    ev = mundane.month_events(2026, 8, "UTC")
    ecl = [e for e in ev["events"] if e["kind"] == "eclipse"]
    assert len(ecl) == 2
    assert ecl[0]["date"] == "2026-08-12" and ecl[0]["sign"] == "الأسد"
    assert ecl[1]["date"] == "2026-08-28" and ecl[1]["sign"] == "الحوت"


def test_neptune_station_july_2026():
    """Astrodienst: نبتون يرجع ٧ يوليو ٢٠٢٦."""
    st = mundane.stations(datetime(2026, 7, 1, tzinfo=UTC),
                          datetime(2026, 7, 15, tzinfo=UTC), ["نبتون"])
    assert len(st) == 1 and st[0].detail["retrograde"]
    assert st[0].when.strftime("%Y-%m-%d") in ("2026-07-06", "2026-07-07")


def test_eclipse_replaces_its_lunation():
    """لا يُذكر القمر الجديد والكسوف معًا في اليوم نفسه."""
    ev = mundane.month_events(2026, 8, "UTC")
    same_day = [e for e in ev["events"]
                if e["date"] == "2026-08-12" and e["kind"] in ("lunation", "eclipse")]
    assert len(same_day) == 1 and same_day[0]["kind"] == "eclipse"


# ══════════════════════════════════════════════════════════════════
# ٧ — ساعات الكواكب
# ══════════════════════════════════════════════════════════════════
def test_day_rulers():
    assert hours.DAY_RULER[2] == "عطارد"      # الأربعاء
    assert hours.DAY_RULER[6] == "الشمس"      # الأحد
    assert hours.DAY_RULER[5] == "زحل"        # السبت


def test_chaldean_sequence_wednesday():
    """أوّل ساعة يحكمها عطارد، ثم الترتيب الكلداني."""
    t = hours.hours_for(datetime(2026, 7, 29, tzinfo=ZoneInfo(DAMASCUS[2])),
                        *DAMASCUS[:2], DAMASCUS[2])
    assert t["day_ruler"] == "عطارد"
    seq = [h["planet"] for h in t["hours"][:5]]
    assert seq == ["عطارد", "القمر", "زحل", "المشتري", "المريخ"]


def test_hour_length_damascus_july():
    """طول الساعة النهارية بدمشق ٢٩ يوليو ٦٩ دقيقة — طابق مرجعًا خارجيًّا."""
    t = hours.hours_for(datetime(2026, 7, 29, tzinfo=ZoneInfo(DAMASCUS[2])),
                        *DAMASCUS[:2], DAMASCUS[2])
    assert 68.5 <= t["day_hour_minutes"] <= 70.0


def test_twelve_day_and_twelve_night_hours():
    t = hours.hours_for(datetime(2026, 3, 15, tzinfo=ZoneInfo(DAMASCUS[2])),
                        *DAMASCUS[:2], DAMASCUS[2])
    assert len([h for h in t["hours"] if h["part"] == "نهارية"]) == 12
    assert len([h for h in t["hours"] if h["part"] == "ليلية"]) == 12


# ══════════════════════════════════════════════════════════════════
# ٨ — الاختيارات
# ══════════════════════════════════════════════════════════════════
def test_surgery_forbidden_on_ruling_sign():
    """قاعدة قاطعة: لا جراحة في عضو والقمر في برجه."""
    r = elections.score_day(date(2026, 8, 12), DAMASCUS[2], *DAMASCUS[:2],
                            "الجراحة")
    assert r["moon_sign"] == "الأسد"
    assert any("القلب" in m for m in r["minus"])
    assert r["score"] < 20


def test_eclipse_blocks_beginnings():
    """الكسوف مانع لكل ابتداء عند القدماء."""
    r = elections.score_day(date(2026, 8, 12), DAMASCUS[2], *DAMASCUS[:2],
                            "الزواج والخِطبة")
    assert any("كسوف" in m for m in r["minus"])


def test_waxing_moon_favours_hair_growth():
    r = elections.score_day(date(2026, 8, 12), DAMASCUS[2], *DAMASCUS[:2],
                            "قصّ الشعر للنموّ")
    assert r["waxing"] and r["score"] >= 70


def test_all_purposes_score_in_range():
    d = bulletin.gather(date(2026, 8, 20), DAMASCUS[2], *DAMASCUS[:2])
    for p in elections.PURPOSES:
        r = elections.score_day(date(2026, 8, 20), DAMASCUS[2], *DAMASCUS[:2],
                                p, d, eclipses=[])
        assert 0 <= r["score"] <= 100, p
        assert r["verdict"], p


def test_month_calendar_covers_every_day():
    cal = elections.month_calendar(2026, 8, DAMASCUS[2], *DAMASCUS[:2],
                                   ["الجراحة"])
    assert len(cal["days"]) == 31
    assert cal["days"][0]["date"] == "2026-08-01"
    assert cal["days"][-1]["date"] == "2026-08-31"


# ══════════════════════════════════════════════════════════════════
# ٩ — النشرات والعبور
# ══════════════════════════════════════════════════════════════════
def test_daily_bulletin_has_all_sections():
    d = bulletin.gather(date(2026, 8, 12), DAMASCUS[2], *DAMASCUS[:2])
    text = bulletin.render_text(d, location="دمشق")
    for tag in ("#النشرة_الفلكية", "#المنازل_القمرية", "#الزوايا_الفلكية",
                "#ساعات_الكواكب", "#الأخبار_الصحية"):
        assert tag in text


def test_monthly_three_voices_differ():
    outs = {v: monthly.compose(2026, 8, DAMASCUS[2], *DAMASCUS[:2],
                               voice=v, with_figures=False)["text"]
            for v in ("daily", "literary", "classic")}
    assert len(set(outs.values())) == 3


def test_monthly_theme_is_eclipse_month():
    m = monthly.compose(2026, 8, DAMASCUS[2], *DAMASCUS[:2],
                        with_figures=False)
    assert m["theme"]["key"] == "eclipse"


def test_transit_windows_are_ordered(natal):
    tr = transits.find(natal, datetime(2026, 8, 1, tzinfo=UTC),
                       datetime(2026, 9, 1, tzinfo=UTC), top=10)
    assert tr
    for r in tr:
        assert r["enter"] <= r["exact"] <= r["leave"]
        assert r["days"] > 0


def test_house_moves_use_natal_houses(natal):
    ev = mundane.month_events(2026, 8, DAMASCUS[2])["events"]
    moves = transits.house_moves(natal, ev)
    assert moves
    for m in moves:
        assert 1 <= m["house"] <= 12


# ══════════════════════════════════════════════════════════════════
# ١٠ — المنازل والأطلس ومتانة عامّة
# ══════════════════════════════════════════════════════════════════
def test_twenty_eight_mansions():
    from falak.tables import MANSIONS
    assert len(MANSIONS) == 28
    assert MANSIONS[0][0] == "الشرطان"
    assert MANSIONS[23][0] == "سعد السعود"


def test_atlas_normalisation():
    for q in ("مكة", "مكه", "makkah", "Mecca"):
        assert atlas.search_local(q, 1), q


def test_polar_fallback_warns():
    when = datetime(1990, 1, 15, 3, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    c = chart.compute(when, 70.0, 25.0, "placidus", "Europe/Oslo")
    assert c["houses"]["system"] == "porphyry"
    assert c["warnings"]


@pytest.mark.parametrize("year", [1850, 1900, 1969, 2026, 2100, 2350])
def test_chart_works_across_centuries(year):
    when = datetime(year, 6, 15, 12, 0, tzinfo=ZoneInfo(DAMASCUS[2]))
    c = chart.compute(when, *DAMASCUS[:2], "whole", DAMASCUS[2])
    assert len(c["bodies"]) >= 13
    assert c["angles"]["الطالع"]["sign"] in ephem.SIGNS


def test_moon_never_retrograde():
    """القمر لا يرجع أبدًا — حارس ضدّ خلل في إشارة السرعة."""
    for d in range(0, 400, 37):
        when = datetime(2026, 1, 1, tzinfo=UTC) + __import__("datetime").timedelta(days=d)
        assert not ephem.is_retrograde("القمر", when)


# ══════════════════════════════════════════════════════════════════
# ١١ — اللغة المبسّطة
# ══════════════════════════════════════════════════════════════════
def test_plain_replaces_hard_terms():
    from falak import plain
    out = plain.simplify("أَلْمُطَن الخريطة الزهرة، وزحل في وباله.")
    assert "أَلْمُطَن" not in out.split("(")[0]
    assert "الكوكب الذي يحكم الخريطة" in out
    assert "موضع ضعف" in out


def test_plain_keeps_proper_names():
    """«سعد السعود» منزلة، ولا يجوز أن تصير «مُيسِّر السعود»."""
    from falak import plain
    for name in ("سعد السعود", "سعد الذابح", "سعد الأخبية", "رأس الغول"):
        out = plain.simplify(f"القمر في منزلة {name} اليوم.")
        assert name in out, name


def test_plain_keeps_moon_phases():
    from falak import plain
    for ph in ("التربيع الأول", "التربيع الأخير", "المحاق / الاقتران"):
        assert ph in plain.simplify(f"القمر في طور {ph}.")


def test_plain_respects_word_boundaries():
    """لا يُبدَّل جزء من كلمة أطول."""
    from falak import plain
    out = plain.simplify("المسعود أسعد الناس.")
    assert "مُيسِّر" not in out


def test_plain_teaches_original_once():
    """المصطلح الأصلي يظهر بين قوسين أوّل مرّة فقط."""
    from falak import plain
    out = plain.simplify("خلو المسار طويل. وخلو المسار مانع.")
    assert out.count("(خلو المسار)") == 1


def test_plain_no_double_parentheses():
    from falak import plain
    out = plain.simplify("زاوية تثليث بين القمر وزحل.")
    assert ") (" not in out


def test_api_level_changes_text():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    p = dispatch('/api/bulletin', q(date="2026-08-12", city="دمشق", level="plain"))
    e = dispatch('/api/bulletin', q(date="2026-08-12", city="دمشق", level="expert"))
    assert p["text"] != e["text"]
    assert p["level"] == "plain" and e["level"] == "expert"
    assert "تثليث" in e["text"] and "منسجمة" in p["text"]


# ══════════════════════════════════════════════════════════════════
# ١٢ — أرباب الأزمنة
# ══════════════════════════════════════════════════════════════════
def test_firdaria_cycle_is_75_years():
    """المجموع المشهور لدورة الفردارات خمس وسبعون سنة."""
    from falak import timelords as T
    assert sum(T.FIRDARIA_YEARS[p] for p in T.DAY_ORDER) == 75
    assert sum(T.FIRDARIA_YEARS[p] for p in T.NIGHT_ORDER) == 75


def test_firdaria_starts_by_sect():
    """النهارية تبدأ بالشمس والليلية بالقمر."""
    from falak import timelords as T
    assert T.DAY_ORDER[0] == "الشمس"
    assert T.NIGHT_ORDER[0] == "القمر"
    b = datetime(1990, 5, 17, tzinfo=UTC)
    assert T.firdaria(b, True)[0]["planet"] == "الشمس"
    assert T.firdaria(b, False)[0]["planet"] == "القمر"


def test_firdaria_subperiods():
    """كل فردار أكبر ينقسم سبعة أقسام متساوية، إلا العقدتين."""
    from falak import timelords as T
    tbl = T.firdaria(datetime(1990, 5, 17, tzinfo=UTC), True, 75)
    for f in tbl:
        if f["planet"] in T.NO_SUB:
            assert f["subs"] == []
        else:
            assert len(f["subs"]) == 7
            assert f["subs"][0]["planet"] == f["planet"]


def test_firdaria_periods_are_contiguous():
    from falak import timelords as T
    tbl = T.firdaria(datetime(1990, 5, 17, tzinfo=UTC), True, 75)
    for a, b in zip(tbl, tbl[1:]):
        assert a["end"] == b["start"]
        assert a["age_to"] == b["age_from"]


def test_profection_returns_to_first_house_every_12_years():
    from falak import timelords as T
    b = datetime(1990, 5, 17, tzinfo=UTC)
    for age in (0, 12, 24, 36, 48):
        when = b + __import__("datetime").timedelta(days=age * 365.2425 + 1)
        assert T.profection(b, when, 101.36)["house"] == 1, age
    when = b + __import__("datetime").timedelta(days=6 * 365.2425 + 1)
    assert T.profection(b, when, 101.36)["house"] == 7


def test_profection_lord_matches_sign_ruler():
    from falak import timelords as T
    b = datetime(1990, 5, 17, tzinfo=UTC)
    when = datetime(2026, 8, 2, tzinfo=UTC)
    p = T.profection(b, when, 101.36)
    assert p["lord"] == dig.DOMICILE[p["sign"]]


def test_solar_return_lands_near_birthday(natal):
    """الشمس تعود إلى درجة ميلادها قرب يوم الميلاد لا بعيدًا عنه."""
    from falak import timelords as T
    sun = next(b["lon"] for b in natal["bodies"] if b["name"] == "الشمس")
    m = T.solar_return_moment(sun, 2026)
    assert m.month == 5 and 15 <= m.day <= 19
    # وموضع الشمس عندها يساوي موضعها الميلادي
    from falak.ephem import lon_of, _wrap180
    assert abs(_wrap180(lon_of("الشمس", m) - sun)) < 0.001


def test_timelords_api():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/timelords',
                 q(date="1990-05-17", time="08:30", city="حلب", live="دمشق"))
    assert d["firdaria"]["major"]["planet"]
    assert 1 <= d["profection"]["house"] <= 12
    assert d["solar_return"]["moment_text"].startswith("2026-05-1")
    assert len(d["profection_table"]) == 91


# ══════════════════════════════════════════════════════════════════
# ١٣ — نصوص العمق
# ══════════════════════════════════════════════════════════════════
def test_all_houses_have_full_profile():
    from falak import depth
    assert len(depth.HOUSES) == 12
    for h, d in depth.HOUSES.items():
        assert d.get("name"), h
        for k in ("rules", "question", "strong", "weak", "shadow"):
            assert d.get(k) and len(d[k]) > 20, (h, k)


def test_all_signs_have_full_profile():
    from falak import depth
    assert len(depth.SIGNS_DEEP) == 12
    for s, d in depth.SIGNS_DEEP.items():
        for k in ("element", "mode", "ruler", "core", "gift", "cost", "body"):
            assert d.get(k), (s, k)
        assert len(d["core"]) > 40 and len(d["gift"]) > 30, s


def test_seven_planets_written_in_all_houses():
    """السبعة التقليدية لها نصّ مكتوب في كل بيت — لا تركيب آلي."""
    from falak import depth
    for p in ("الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"):
        assert p in depth.PLANET_IN_HOUSE, p
        assert len(depth.PLANET_IN_HOUSE[p]) == 12, p
        for h, t in depth.PLANET_IN_HOUSE[p].items():
            assert len(t) > 45, (p, h)


def test_house_texts_are_distinct():
    """لا نصّين متطابقين — دليل أنها مكتوبة لا مركّبة."""
    from falak import depth
    seen = set()
    for p, tbl in depth.PLANET_IN_HOUSE.items():
        for h, t in tbl.items():
            assert t not in seen, f"{p}/{h} مكرّر"
            seen.add(t)
    assert len(seen) == 168


def test_jupiter_saturn_written_in_all_signs():
    from falak import interpret as I
    for tbl in (I.JUPITER_IN_SIGN, I.SATURN_IN_SIGN):
        assert len(tbl) == 12
        assert len(set(tbl.values())) == 12
        for s, t in tbl.items():
            assert len(t) > 40, s


def test_reading_includes_profiles():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    c = dispatch('/api/chart', q(date="1990-05-17", time="08:30",
                                 city="حلب", both="0"))
    pr = c["reading"]["profiles"]
    assert pr["houses"] and pr["signs"]
    any_h = next(iter(pr["houses"].values()))
    assert any_h["question"] and any_h["shadow"]


def test_depth_route():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    d = dispatch('/api/depth', {})
    assert len(d["houses"]) == 12 and len(d["signs"]) == 12
    assert sum(len(v) for v in d["planet_in_house"].values()) == 168
    assert d["coverage"]["المجموع"] == 279


# ══════════════════════════════════════════════════════════════════
# ١٤ — نصوص الزوايا
# ══════════════════════════════════════════════════════════════════
def test_all_outer_and_points_written_in_all_houses():
    """الخارجية والنقاط لها نصّ في كل بيت — لا صيغة الباب العامّة."""
    from falak import depth
    for p in ("أورانوس", "نبتون", "بلوتو", "خيرون",
              "الرأس", "الذنب", "ليليث"):
        assert p in depth.PLANET_IN_HOUSE, p
        assert len(depth.PLANET_IN_HOUSE[p]) == 12, p
        for h, t in depth.PLANET_IN_HOUSE[p].items():
            assert len(t) > 45, (p, h)


def test_true_lilith_reads_as_mean():
    """النقطتان معنى واحد بحسابين، فلا يُترك أحدهما بلا نصّ."""
    from falak import depth
    assert depth.house_text("ليليث الحقيقية", 7) == depth.house_text("ليليث", 7)


def test_every_traditional_pair_is_written():
    """٢١ زوجًا من السبعة، لكلٍّ موضوعه ونصوص زواياه."""
    from falak import aspects_deep as A
    seven = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"]
    for i in range(len(seven)):
        for j in range(i + 1, len(seven)):
            k = A._key(seven[i], seven[j], A.PAIRS)
            assert k, f"{seven[i]}/{seven[j]} غير مكتوب"
            assert len(A.PAIRS[k]["theme"]) > 20


def test_impossible_aspects_are_absent():
    """
    عطارد لا يفارق الشمس أكثر من ٢٨° والزهرة أكثر من ٤٨°،
    وعطارد والزهرة لا يتباعدان أكثر من ٧٦°. فوجود «تربيع»
    بينها في الجدول يعني أننا ملأنا خانة لا تُملأ في السماء.
    """
    from falak import aspects_deep as A
    assert set(A.PAIRS[("الشمس", "عطارد")]) == {"theme", "اقتران"}
    assert set(A.PAIRS[("الشمس", "الزهرة")]) == {"theme", "اقتران"}
    assert set(A.PAIRS[("عطارد", "الزهرة")]) == {"theme", "اقتران", "تسديس"}


def test_impossible_aspects_never_occur_in_the_sky():
    """نتحقّق من الادّعاء نفسه بالحساب: مسح قرنين كاملين."""
    from datetime import datetime, timedelta
    day = datetime(1900, 1, 1, tzinfo=UTC)
    worst_merc = worst_ven = 0.0
    while day.year < 2100:
        sun = ephem.lon_of("الشمس", day)
        merc = abs(ephem._wrap180(ephem.lon_of("عطارد", day) - sun))
        ven = abs(ephem._wrap180(ephem.lon_of("الزهرة", day) - sun))
        worst_merc = max(worst_merc, merc)
        worst_ven = max(worst_ven, ven)
        day += timedelta(days=5)
    assert worst_merc < 29, worst_merc
    assert worst_ven < 48, worst_ven


def test_aspect_texts_are_distinct():
    """لا نصّين متطابقين في جدول الزوايا."""
    from falak import aspects_deep as A
    seen = set()
    for pair, d in A.PAIRS.items():
        for k, t in d.items():
            if k == "theme":
                continue
            assert t not in seen, f"{pair}/{k} مكرّر"
            seen.add(t)
    assert len(seen) == 94
    for pair, d in A.OUTER_PAIRS.items():
        for k in ("سهل", "صعب"):
            assert d[k] not in seen, f"{pair}/{k} مكرّر"
            seen.add(d[k])
    for pair, t in A.GENERATIONAL.items():
        assert t not in seen, f"{pair} مكرّر"
        seen.add(t)
    assert len(seen) == 202


def test_all_outers_paired_with_all_personals():
    from falak import aspects_deep as A
    for outer in ("أورانوس", "نبتون", "بلوتو", "خيرون"):
        for p in ("الشمس", "القمر", "عطارد", "الزهرة",
                  "المريخ", "المشتري", "زحل"):
            assert A._key(outer, p, A.OUTER_PAIRS), f"{outer}/{p}"


def test_reading_aspects_are_written_not_composed():
    """كل زاوية كبرى في خريطة مرجعية تجد نصًّا مكتوبًا."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    c = dispatch('/api/chart', q(date="1990-05-17", time="08:30",
                                 city="حلب", both="0"))
    asp = c["reading"]["aspects"]
    assert asp
    for a in asp:
        assert a["theme"] and a["text"], a["title"]
        assert len(a["text"]) > 40, a["title"]


def test_nodes_and_lilith_paired_with_all_personals():
    """الرأس وليليث ليسا زينة: لهما نصّ مع كلّ كوكب شخصي."""
    from falak import aspects_deep as A
    for pt in ("الرأس", "ليليث"):
        for p in ("الشمس", "القمر", "عطارد", "الزهرة",
                  "المريخ", "المشتري", "زحل"):
            assert A._key(pt, p, A.OUTER_PAIRS), f"{pt}/{p}"


def test_generational_pairs_say_so():
    """
    زاوية بين خارجيّين يشترك فيها ملايين. فمن الأمانة أن يُقال
    للقارئ إنها علامة جيل، لا صفة تخصّه هو.
    """
    from falak import aspects_deep as A
    for pair in (("أورانوس", "نبتون"), ("أورانوس", "بلوتو"),
                 ("نبتون", "بلوتو")):
        assert pair in A.GENERATIONAL
        assert "جيل" in A.GENERATIONAL[pair]
    d = A.pair_text("نبتون", "بلوتو", "تسديس")
    assert d["written"] and "جيل" in d["theme"]


def test_two_liliths_make_no_aspect():
    """
    ليليث الوسطى والحقيقية حسابان لنقطة واحدة. اقترانهما ليس
    زاوية في السماء بل تقارب حسابَين، فلا يُعرَض على القارئ.
    """
    when = datetime(1990, 5, 17, 5, 30, tzinfo=UTC)
    c = chart.compute(when, *ALEPPO[:2], "whole", ALEPPO[2])
    for a in c["aspects"]:
        assert {a["a"], a["b"]} != {"ليليث", "ليليث الحقيقية"}


def test_every_aspect_in_real_charts_is_written():
    """
    الحارس الحقيقي: نمسح مئة خريطة عشوائية على قرن كامل، ونتأكّد
    أن كلّ زاوية تقع فيها تجد نصًّا مكتوبًا — لا صياغة آلية.
    إن سقط هذا الاختبار فقد ظهر تركيب جديد لم نكتب له شيئًا.
    """
    import random
    from falak.interpret import aspect_text
    random.seed(11)
    unwritten = {}
    for _ in range(100):
        when = datetime(random.randint(1925, 2015), random.randint(1, 12),
                        random.randint(1, 28), random.randint(0, 23),
                        random.randint(0, 59), tzinfo=UTC)
        c = chart.compute(when, *DAMASCUS[:2], "whole", DAMASCUS[2])
        for a in c["aspects"]:
            if not aspect_text(a["a"], a["b"], a["name"])["written"]:
                k = (a["a"], a["b"], a["name"])
                unwritten[k] = unwritten.get(k, 0) + 1
    assert not unwritten, f"تراكيب بلا نصّ: {sorted(unwritten)[:5]}"


# ══════════════════════════════════════════════════════════════════
# ١٥ — التوافق: التزاوج والمركّبة ودافيسون
# ══════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def pair():
    from falak import synastry as syn
    r1 = ftz.resolve(datetime(1990, 5, 17, 8, 30), ALEPPO[2], ALEPPO[1])
    A = chart.compute(r1["when"], ALEPPO[0], ALEPPO[1], "whole",
                      ALEPPO[2], tz_info=r1)
    r2 = ftz.resolve(datetime(1992, 11, 3, 21, 15), "Europe/Paris", 2.35)
    B = chart.compute(r2["when"], 48.8566, 2.3522, "whole",
                      "Europe/Paris", tz_info=r2)
    return A, B, syn


def test_synastry_is_symmetric(pair):
    """
    التوافق لا يعرف من سُئل أوّلًا: عدد الوصلات ودرجاتها لا تتغيّر
    بعكس الطرفين. لو تغيّرت لكان في الحساب اتجاه لا مبرّر له.
    """
    A, B, syn = pair
    ab, ba = syn.inter_aspects(A, B), syn.inter_aspects(B, A)
    assert len(ab) == len(ba)
    key = lambda L: sorted((tuple(sorted((x["a"], x["b"]))), x["name"],
                            x["orb"]) for x in L)
    assert key(ab) == key(ba)
    for d, v in syn.score(A, B).items():
        assert abs(v["score"] - syn.score(B, A)[d]["score"]) <= 1, d


def test_synastry_orbs_are_tighter(pair):
    """وجاج التزاوج ثلاثة أرباع وجاج الخريطة الواحدة."""
    A, B, syn = pair
    for x in syn.inter_aspects(A, B):
        full = chart.orb_for(x["angle"],
                             chart.BODY_CLASS.get(x["a"], "نيّر"),
                             chart.BODY_CLASS.get(x["b"], "نيّر"))
        # orb_max مقرَّب إلى منزلتين، فنسمح بنصف جزء من مئة
        assert x["orb_max"] <= full * 0.75 + 0.005


def test_midpoint_takes_the_short_arc():
    """
    ٣٥٠° و١٠° منتصفهما ٠° لا ١٨٠°. هذا موضع الخطأ الأشهر في
    الخرائط المركّبة، ويجعل نصف كواكبها في البرج المقابل.
    """
    from falak.synastry import _mid
    assert abs(_mid(350.0, 10.0) - 0.0) < 1e-9
    assert abs(_mid(10.0, 350.0) - 0.0) < 1e-9
    # متقابلان تمامًا: القوسان سواء، والاختيار الأمامي معلَن
    assert abs(_mid(0.0, 180.0) - 90.0) < 1e-9
    assert abs(_mid(180.0, 0.0) - 270.0) < 1e-9
    assert abs(_mid(100.0, 140.0) - 120.0) < 1e-9


def test_composite_is_midpoint_of_both(pair):
    A, B, syn = pair
    co = syn.composite(A, B)
    a = {x["name"]: x["lon"] for x in A["bodies"]}
    b = {x["name"]: x["lon"] for x in B["bodies"]}
    from falak.synastry import _mid
    for x in co["bodies"]:
        assert abs(x["lon"] - _mid(a[x["name"]], b[x["name"]])) < 1e-3, x["name"]
    assert len(co["cusps"]) == 12


def test_davison_is_a_real_sky(pair):
    """
    دافيسون ليست تجريدًا: هي خريطة للحظة المنتصف. فمواقع كواكبها
    يجب أن تطابق ما تعطيه الآلة لتلك اللحظة بعينها.
    """
    A, B, syn = pair
    dv = syn.davison(A, B)
    mid = datetime.fromisoformat(dv["midpoint"]["when_utc"])
    a_utc = datetime.fromisoformat(A["when_utc"])
    b_utc = datetime.fromisoformat(B["when_utc"])
    assert abs((mid - (a_utc + (b_utc - a_utc) / 2)).total_seconds()) < 1
    direct = chart.compute(mid, dv["midpoint"]["lat"], dv["midpoint"]["lon"],
                           "whole", "UTC", minor_aspects=False)
    got = {x["name"]: x["lon"] for x in dv["bodies"]}
    for x in direct["bodies"]:
        assert abs(got[x["name"]] - x["lon"]) < 1e-6, x["name"]


def test_davison_longitude_crosses_the_date_line():
    """
    مولودان أحدهما شرق خطّ التاريخ والآخر غربه: منتصفهما في
    المحيط الهادئ، لا في وسط آسيا. متوسّط حسابي ساذج يقع هنا.
    """
    from falak.synastry import davison_moment
    m = davison_moment(datetime(1990, 1, 1, tzinfo=UTC),
                       datetime(1990, 1, 1, tzinfo=UTC),
                       0.0, 179.0, 0.0, -179.0)
    assert abs(abs(m["lon"]) - 180.0) < 0.001, m["lon"]


def test_reception_is_not_domicile(pair):
    """
    كوكب في برجه نازل في داره هو، لا في دار غيره. فلا يُحسَب
    تقبّلًا — وهذا خلط يقع فيه من يُبرمج الباب على عجل.
    """
    A, B, syn = pair
    for r in syn.receptions(A, B):
        assert r["a"] != r["b"] or r["kind"] != "تقبّل تامّ بالبيت"
    # حالة مصنوعة: زحل في الجدي عند كليهما — دار زحل نفسه
    fake_a = {"bodies": [{"name": "زحل", "sign": "الجدي"}]}
    fake_b = {"bodies": [{"name": "زحل", "sign": "الجدي"}]}
    assert syn.receptions(fake_a, fake_b) == []


def test_scores_spread_across_the_range():
    """
    درجة تُعطي كلّ الناس ٥٧ لا تقول شيئًا. نتحقّق أن الرتبة
    المئوية تتوزّع فعلًا: ربعها دون ٣٥ وربعها فوق ٦٥.
    """
    import random
    from falak import synastry as syn
    rnd = random.Random(2026)
    pool = [chart.compute(
        datetime(rnd.randint(1950, 2005), rnd.randint(1, 12),
                 rnd.randint(1, 28), rnd.randint(0, 23),
                 rnd.randint(0, 59), tzinfo=ZoneInfo("Europe/Paris")),
        48.86, 2.35, "whole", "Europe/Paris") for _ in range(24)]
    vals = []
    for _ in range(80):
        a, b = rnd.sample(pool, 2)
        vals.append(syn.score(a, b)["عاطفي"]["score"])
    vals.sort()
    assert vals[0] < 25 and vals[-1] > 75, vals[:3] + vals[-3:]
    assert vals[len(vals) // 4] < 40
    assert vals[3 * len(vals) // 4] > 60


def test_every_synastry_link_is_written():
    """
    الحارس نفسه المستعمَل في الخريطة الواحدة، مطبَّقًا على
    الوصلات بين خريطتين: لا وصلة تُعرَض بلا نصّ مكتوب.
    """
    import random
    from falak import synastry as syn, synastry_deep as sd
    rnd = random.Random(2027)
    pool = [chart.compute(
        datetime(rnd.randint(1940, 2010), rnd.randint(1, 12),
                 rnd.randint(1, 28), rnd.randint(0, 23),
                 rnd.randint(0, 59), tzinfo=ZoneInfo("Asia/Damascus")),
        33.51, 36.28, "whole", "Asia/Damascus") for _ in range(20)]
    unwritten = {}
    for _ in range(60):
        a, b = rnd.sample(pool, 2)
        for x in syn.inter_aspects(a, b):
            if not sd.pair_text(x["a"], x["b"], x["name"])["written"]:
                k = (x["a"], x["b"])
                unwritten[k] = unwritten.get(k, 0) + 1
    assert not unwritten, f"وصلات بلا نصّ: {sorted(unwritten)[:5]}"


def test_synastry_texts_are_distinct():
    from falak import synastry_deep as sd
    seen = set()
    for pair_, d in sd.SYN_PAIRS.items():
        for k, t in d.items():
            assert t not in seen, f"{pair_}/{k} مكرّر"
            seen.add(t)
    for tbl in (sd.SYN_OUTER, sd.ANGLE_TEXT, sd.SLOW_PAIRS):
        for k, t in tbl.items():
            assert t not in seen, f"{k} مكرّر"
            seen.add(t)
    for h, t in sd.OVERLAY_TEXT.items():
        assert t not in seen, f"بيت {h} مكرّر"
        seen.add(t)
    assert len(seen) == sd.coverage()["المجموع"]


def test_synastry_route():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/synastry', q(date="1990-05-17", time="08:30", city="حلب",
                                    name="الأوّل", date2="1992-11-03",
                                    time2="21:15", city2="باريس", name2="الثاني"))
    R = d["reading"]
    assert set(R["scores"]) == {"عاطفي", "صداقة", "مهني"}
    for v in R["scores"].values():
        assert 1 <= v["score"] <= 99 and v["label"] and v["band"]
        assert v["detail"], "لا بدّ من تفصيل يُظهر مصدر الدرجة"
    assert R["aspects"] and all(x["text"] for x in R["aspects"])
    assert len(R["overlays"]) == 2
    assert d["composite"]["bodies"] and d["davison"]["midpoint"]
    assert "لا تُبنى" in d["disclaimer"]


def test_calibration_matches_the_criteria():
    """
    الرتبة المئوية تكذب إن تغيّرت المعايير ولم تُعَد المعايرة.
    فنتحقّق أن وسيط عيّنة جديدة قريب من الخمسين.
    """
    import random, statistics
    from falak import synastry as syn
    rnd = random.Random(555)
    pool = [chart.compute(
        datetime(rnd.randint(1940, 2010), rnd.randint(1, 12),
                 rnd.randint(1, 28), rnd.randint(0, 23),
                 rnd.randint(0, 59), tzinfo=ZoneInfo("Asia/Damascus")),
        33.51, 36.28, "whole", "Asia/Damascus") for _ in range(30)]
    for domain in ("عاطفي", "صداقة", "مهني"):
        vals = []
        for _ in range(120):
            a, b = rnd.sample(pool, 2)
            vals.append(syn.score(a, b)[domain]["score"])
        med = statistics.median(vals)
        assert 35 <= med <= 65, f"{domain}: الوسيط {med} — أعِد المعايرة"


# ══════════════════════════════════════════════════════════════════
# ١٦ — المسائل والاختيارات
# ══════════════════════════════════════════════════════════════════
def _q_chart(y, mo, d, h, mi, tzname="Asia/Damascus", lat=33.51, lon=36.28):
    return chart.compute(datetime(y, mo, d, h, mi, tzinfo=ZoneInfo(tzname)),
                         lat, lon, "regiomontanus", tzname, minor_aspects=False)


def test_late_ascendant_blocks_judgment():
    """
    الطالع فوق ٢٧° أو دون ٣°: تُردّ المسألة. وهذا أشرف ما في الباب —
    أن يُقال «لا جواب» بدل تلفيق واحد.
    """
    from falak import horary
    found_late = found_early = False
    for h in range(24):
        for mi in (0, 20, 40):
            c = _q_chart(2026, 8, 1, h, mi)
            deg = c["angles"]["الطالع"]["lon"] % 30
            cons = horary.considerations(c)
            names = {x["name"] for x in cons if x["kind"] == "مانع"}
            if deg > 27:
                assert "الطالع في آخر درجات البرج" in names, deg
                found_late = True
            elif deg < 3:
                assert "الطالع في أوّل درجات البرج" in names, deg
                found_early = True
            else:
                assert not (names & {"الطالع في أوّل درجات البرج",
                                     "الطالع في آخر درجات البرج"}), deg
    assert found_late and found_early


def test_blocked_chart_yields_no_judgment():
    """إن رُدّت المسألة فلا يُنظَر في التمام أصلًا."""
    from falak import horary
    found = 0
    for h in range(24):
        for mi in (0, 30):
            c = _q_chart(2026, 3, 15, h, mi)
            j = horary.judge(c, 7)
            if j["blocked"]:
                assert j["verdict"] == "تُردّ المسألة"
                assert j["perfection"]["detail"] == []
                assert "أعِد السؤال" in j["summary"]
                found += 1
    # الطالع يقطع برجًا كلّ ساعتين، فلا بدّ أن يمرّ بأوّل درجاته
    # وآخرها مرّات في اليوم الواحد
    assert found >= 3, f"المنع لم يقع إلا {found} مرّة في اليوم"


def test_perfection_requires_staying_in_sign():
    """
    شرط التمام أن يقع الاتّصال **قبل خروج الدليل من برجه**.
    فكل اتّصال مُثبَت لا بدّ أن يسبق خروج أيٍّ من الدليلين.
    """
    from falak import horary
    checked = 0
    for h in (3, 9, 15, 21):
        c = _q_chart(2026, 6, 10, h, 0)
        j = horary.judge(c, 10)
        P = j["perfection"]
        if not P["perfects"] or not P.get("aspect"):
            continue
        sq = j["significators"]["السائل"]["ruler"]
        st = j["significators"]["المسؤول عنه"]["ruler"]
        if sq == st:
            continue
        when = datetime.fromisoformat(c["when_utc"])
        end = when + timedelta(days=45)
        t = datetime.fromisoformat(P["when"])
        for sig in (sq, st):
            exit_t = horary._sign_exit(sig, when, end)
            if exit_t:
                assert t <= exit_t + timedelta(seconds=1), (sig, t, exit_t)
        checked += 1
    assert checked, "لم يقع اتّصال مباشر في العيّنة"


def test_translation_needs_both_orbs():
    """
    نقل النور لا يكفي فيه أن يكون الناقل قد فارق هذا يومًا وسيلقى
    ذاك يومًا. لا بدّ أن يكون الآن في وجاج الاتّصالين معًا: مُدبِرًا
    عن الأوّل مُقبِلًا على الثاني. وبغير هذا يقع «نقل نور» في كل
    خريطة تقريبًا فيفقد الباب معناه.
    """
    import random
    from falak import horary
    rnd = random.Random(31)
    kinds = {}
    for _ in range(60):
        c = _q_chart(2026, 1, 1, 0, 0)
        c = chart.compute(
            datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Damascus"))
            + timedelta(hours=rnd.randint(0, 8760)),
            33.51, 36.28, "regiomontanus", "Asia/Damascus", minor_aspects=False)
        j = horary.judge(c, rnd.randint(1, 12))
        for step in j["perfection"]["detail"]:
            kinds[step["kind"]] = kinds.get(step["kind"], 0) + 1
    trans = kinds.get("نقل النور", 0)
    assert trans <= 12, f"نقل النور وقع {trans} مرّة من ٦٠ — الشرط مُنفلت"


def test_single_significator_is_its_own_verdict():
    """
    إن كان ربّ الطالع هو ربّ بيت المسألة فليس تمامًا بواسطة ولا
    بعُسر: الأمر بيد السائل. وخلطه بغيره يُفسد الحكم.
    """
    from falak import horary
    for h in range(24):
        c = _q_chart(2026, 5, 20, h, 0)
        asc = c["angles"]["الطالع"]["sign"]
        for house in range(1, 13):
            hs = chart.SIGNS[int(c["houses"]["cusps"][house - 1]["lon"] // 30)]
            from falak import dignities as dg
            if dg.DOMICILE[asc] == dg.DOMICILE[hs] and not any(
                    x["kind"] == "مانع" for x in horary.considerations(c)):
                j = horary.judge(c, house)
                assert j["verdict"] == "بيدك أنت", j["verdict"]
                assert "بيدك" in j["summary"] or "قرارك" in j["summary"]
                return
    pytest.skip("لم يقع تطابق الدليلين في العيّنة")


def test_horary_verdicts_are_not_all_the_same():
    """حكم يقول للجميع الشيء نفسه لا يقول شيئًا."""
    import random
    from falak import horary
    rnd = random.Random(77)
    seen = {}
    for _ in range(60):
        c = chart.compute(
            datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Damascus"))
            + timedelta(hours=rnd.randint(0, 8760)),
            33.51, 36.28, "regiomontanus", "Asia/Damascus", minor_aspects=False)
        v = horary.judge(c, rnd.randint(1, 12))["verdict"]
        seen[v] = seen.get(v, 0) + 1
    assert len(seen) >= 4, seen
    assert max(seen.values()) < 45, seen           # لا حكم يغلب على كل شيء
    assert seen.get("تُردّ المسألة", 0) >= 10      # الردّ باب حقيقي لا زينة


def test_wide_window_matches_day_by_day():
    """
    تسريع البحث يقتطع زوايا القمر من نافذة واسعة بدل حسابها لكل
    يوم. فلا بدّ أن تكون النتيجة **مطابقة تمامًا**، وإلا كان
    التسريع تغييرًا في الأرقام لا في السرعة.
    """
    a = datetime(2026, 8, 1, tzinfo=UTC)
    b = a + timedelta(days=5)
    ephem.clear_range()
    plain_ = [(x.time, x.planet, x.angle) for x in ephem.moon_aspects(a, b)]
    ephem.preload_range(a - timedelta(days=6), b + timedelta(days=6))
    try:
        sliced = [(x.time, x.planet, x.angle) for x in ephem.moon_aspects(a, b)]
    finally:
        ephem.clear_range()
    assert plain_ == sliced and len(plain_) > 3


def test_sun_events_cache_is_exact():
    """الذاكرة تُسرّع ولا تُغيّر: النتيجة قبلها وبعدها واحدة."""
    tz = ZoneInfo("Asia/Damascus")
    day = datetime(2026, 8, 1, tzinfo=tz)
    ephem._SUN_EVENTS_CACHE.clear()
    first = ephem.sun_events(day, 33.51, 36.28, tz)
    second = ephem.sun_events(day, 33.51, 36.28, tz)
    assert first == second
    ephem._SUN_EVENTS_CACHE.clear()
    assert ephem.sun_events(day, 33.51, 36.28, tz) == first


def test_search_finds_and_ranks():
    from falak import elections as el
    r = el.search(date(2026, 8, 2), 45, "Asia/Damascus", 33.51, 36.28,
                  "العقود والتوقيع")
    assert r["count"] == 45 and len(r["best"]) == 10
    scores = [x["score"] for x in r["best"]]
    assert scores == sorted(scores, reverse=True)
    assert r["best"][0]["score"] > r["worst"][0]["score"]
    assert r["best"][0]["plus"], "لا بدّ من أسباب لكل درجة"


def test_search_personal_bonus_is_bounded():
    """
    ترجيح المولد يُرجّح ولا يقلب: العبور البطيء يدوم شهورًا، فلو
    ثقُل وزنه لسوّى بين كل أيام الفصل.
    """
    from falak import elections as el
    natal = chart.compute(datetime(1990, 5, 17, 8, 30,
                                   tzinfo=ZoneInfo("Asia/Damascus")),
                          36.2, 37.13, "whole", "Asia/Damascus")
    r = el.search(date(2026, 8, 2), 40, "Asia/Damascus", 33.51, 36.28,
                  "العقود والتوقيع", natal=natal)
    assert r["personalised"]
    for x in r["best"] + r["worst"]:
        assert abs(x["personal"]) <= 20, x
        assert abs(x["score"] - x["base_score"]) <= 20


def test_horary_and_search_routes():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}

    lst = dispatch('/api/horary', q(list="1"))
    assert len(lst["questions"]) >= 20

    d = dispatch('/api/horary', q(city="دمشق", date="2026-08-01",
                                  time="11:20", question="هل أتزوّج فلانًا؟"))
    j = d["judgment"]
    assert j["verdict"] and j["summary"] and j["considerations"]
    assert set(j["significators"]) == {"السائل", "المسؤول عنه", "القمر"}
    assert "لا يُبنى" in j["limits"] or "لا وسيلة" in j["limits"]
    assert d["system"] == "regiomontanus"

    s = dispatch('/api/search', q(city="دمشق", purpose="العقود والتوقيع",
                                  start="2026-08-02", days="40"))
    assert s["best"] and s["all"] and s["average"]

    with pytest.raises(Exception):
        dispatch('/api/search', q(city="دمشق", purpose="العقود والتوقيع",
                                  days="900"))
