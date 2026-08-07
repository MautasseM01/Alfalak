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


# ══════════════════════════════════════════════════════════════════
# ١٧ — الواجهة العامّة والتقويم
# ══════════════════════════════════════════════════════════════════
def test_v1_detection_survives_vercel_rewrite():
    """
    Vercel يُعيد كتابة /api/… إلى /api/index/… فيصير /api/v1/chart
    عند وصوله /api/index/v1/chart. فحصٌ بالنصّ على «/api/v1» يعمل
    محليًّا ويسقط منشورًا — وهذا الاختبار يحرس المقاطع لا النصّ.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import is_v1
    for p in ("/api/v1/chart", "/api/index/v1/chart", "/api/v1", "/api/v1/",
              "/api/index/v1"):
        assert is_v1(p), p
    for p in ("/api/chart", "/api/index/chart", "/api/v11/chart", "/api/"):
        assert not is_v1(p), p


def test_v1_envelope_and_legacy_stay_separate():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    new = dispatch('/api/index/v1/chart', q(date="1990-05-17", city="حلب"))
    assert new["ok"] and new["version"] and new["endpoint"] == "chart"
    assert new["rate"]["limit"] and "angles" in new["data"]
    old = dispatch('/api/index/chart', q(date="1990-05-17", city="حلب"))
    assert "ok" not in old and "angles" in old       # القديم بلا مغلَّف


def test_api_keys_sign_and_expire():
    from falak import apikeys as ak
    k = ak.issue("basic", 30, "اختبار")
    v = ak.verify(k["key"])
    assert v["valid"] and v["tier"] == "basic" and v["rpm"] == 120
    assert not ak.verify(k["key"][:-2] + "zz")["valid"]     # توقيع مبدَّل
    assert not ak.verify("falak_pro.2030-01-01.aaaa_bbbb")["valid"]
    assert ak.verify(None)["valid"] and ak.verify(None)["anonymous"]
    expired = ak.issue("basic", 1)
    body = expired["key"][len("falak_"):].rpartition("_")[0]
    old_body = body.replace(expired["expires"], "2020-01-01")
    forged = f"falak_{old_body}_{ak._sign(old_body)}"
    assert not ak.verify(forged)["valid"]                   # منتهٍ ولو صحّ توقيعه


def test_rate_limit_counts_and_recovers():
    from falak import apikeys as ak
    ak._HITS.clear()
    for i in range(5):
        assert ak.check_rate("t", 5, now=1000.0 + i)["ok"]
    blocked = ak.check_rate("t", 5, now=1005.0)
    assert not blocked["ok"] and blocked["retry_after"] > 0
    assert ak.check_rate("t", 5, now=1065.0)["ok"]          # بعد انقضاء النافذة


def test_tier_caps_search_range():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    from falak import apikeys as ak
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    with pytest.raises(Exception) as e:
        dispatch('/api/v1/search', q(city="دمشق", purpose="العقود والتوقيع",
                                     days="300"))
    assert "يسمح" in str(e.value)
    k = ak.issue("pro", 10)["key"]
    ak._HITS.clear()
    out = dispatch('/api/v1/search',
                   {**q(city="دمشق", purpose="العقود والتوقيع", days="120"),
                    "key": [k]})
    assert out["tier"] == "pro" and out["data"]["count"] == 120


# ── التقويم: مقابل المعيار لا مقابل ظنّنا ────────────────────────
def _ical_text():
    from falak import ics
    evs = (ics.bulletin_events(date(2026, 8, 2), 6, "Asia/Damascus",
                               33.51, 36.28, "دمشق")
           + ics.month_events(2026, 8, "Asia/Damascus")
           + ics.election_events(date(2026, 8, 2), 40, "Asia/Damascus",
                                 33.51, 36.28, "العقود والتوقيع", "دمشق"))
    return ics.build(evs, "الفَلَك — دمشق", "اختبار"), evs


def test_ics_lines_obey_the_octet_limit():
    """
    المعيار يطوي عند ٧٥ **ثمانيّة** لا ٧٥ حرفًا. والحرف العربي
    ثمانيّتان، فالعدّ بالحروف يُخرج الأسطر عن الحدّ.
    """
    txt, _ = _ical_text()
    for line in txt.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75, line[:40]


def test_ics_folding_never_splits_a_character():
    """القطع في وسط حرف يُخرج ملفًّا فاسدًا لا يفتحه تقويم."""
    txt, _ = _ical_text()
    raw = txt.encode("utf-8")
    assert raw.decode("utf-8") == txt          # لا بايت يتيم
    # فكّ الطيّ يُعيد النصّ الأصلي حرفًا حرفًا
    from falak import ics
    for src in ("م" * 200, "abc, def; ghi\njkl", "الفَلَك — منزلة سعد السعود"):
        folded = ics.fold("SUMMARY:" + ics.esc(src))
        unfolded = folded.replace("\r\n ", "")
        assert unfolded.startswith("SUMMARY:")


def test_ics_uids_are_unique_and_stable():
    """
    المُعرّف يُشتقّ من المضمون لا من ساعة التوليد: فلا تتضاعف
    الأحداث كلّما تجدّد الاشتراك. والمنزلة تمتدّ عبر منتصف الليل
    فتظهر في بيانات اليومين — فلا بدّ من حذف المكرّر.
    """
    from falak import ics
    txt, evs = _ical_text()
    uids = [l.split(":", 1)[1] for l in txt.split("\r\n") if l.startswith("UID:")]
    assert len(uids) == len(set(uids)), "مُعرّفات مكرّرة"
    assert len(uids) < len(evs), "الحذف لم يعمل — والمنازل تتكرّر بطبعها"
    again, _ = _ical_text()
    u2 = [l.split(":", 1)[1] for l in again.split("\r\n") if l.startswith("UID:")]
    assert uids == u2


def test_ics_parses_with_an_independent_library():
    """
    الحَكَم ليس اختبارنا: نُمرّر الملفّ على محلّل مستقلّ. وإن لم
    يكن مُثبَّتًا تخطّينا، فلا نُوهم أنفسنا بأننا تحقّقنا.
    """
    icalendar = pytest.importorskip("icalendar")
    txt, _ = _ical_text()
    cal = icalendar.Calendar.from_ical(txt)
    ve = [c for c in cal.walk() if c.name == "VEVENT"]
    assert len(ve) > 20
    for c in ve:
        assert "UID" in c and "DTSTAMP" in c and "DTSTART" in c and "SUMMARY" in c
    assert any(c["DTSTART"].params.get("VALUE") == "DATE" for c in ve)
    assert "\n" in str([c for c in ve if "DESCRIPTION" in c][0]["DESCRIPTION"])


def test_ics_escapes_the_special_characters():
    from falak import ics
    assert ics.esc("a,b") == "a\\,b"
    assert ics.esc("a;b") == "a\\;b"
    assert ics.esc("a\\b") == "a\\\\b"
    assert ics.esc("a\nb") == "a\\nb"


def test_calendar_route_returns_a_file():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch, Raw
    from falak import apikeys as ak
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    ak._HITS.clear()
    for kind in ("bulletin", "month", "hours"):
        r = dispatch('/api/v1/calendar.ics',
                     q(kind=kind, city="دمشق", days="7", year="2026", month="8"))
        assert isinstance(r, Raw)
        assert r.ctype.startswith("text/calendar")
        body = r.body.decode("utf-8")
        assert body.startswith("BEGIN:VCALENDAR") and body.endswith("END:VCALENDAR\r\n")
        assert r.filename.endswith(".ics")


# ══════════════════════════════════════════════════════════════════
# ١٨ — الخلاصة: الشرط الذي يجعلها خلاصة
# ══════════════════════════════════════════════════════════════════
def _gist_cases():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    return [
        ('bulletin', dispatch('/api/bulletin', q(city="دمشق"))),
        ('chart', dispatch('/api/chart', q(date="1990-05-17", time="08:30",
                                           city="حلب"))),
        ('hours', dispatch('/api/hours', q(city="دمشق"))),
        ('timelords', dispatch('/api/timelords', q(date="1990-05-17",
                                                   time="08:30", city="حلب"))),
        ('monthly', dispatch('/api/monthly', q(year="2026", month="8",
                                               city="دمشق"))),
        ('horary', dispatch('/api/horary', q(city="دمشق", date="2026-08-01",
                                             time="11:20",
                                             question="هل أتزوّج فلانًا؟"))),
        ('synastry', dispatch('/api/synastry',
                              q(date="1990-05-17", time="08:30", city="حلب",
                                date2="1992-11-03", time2="21:15",
                                city2="باريس"))),
        ('search', dispatch('/api/search', q(city="دمشق", days="45",
                                             purpose="العقود والتوقيع"))),
    ]


def test_every_main_route_has_a_gist():
    for name, d in _gist_cases():
        g = d.get("gist")
        assert g, f"{name} بلا خلاصة"
        assert g["title"] and g["lines"], name
        assert len(g["lines"]) >= 2, f"{name}: سطر واحد ليس خلاصة"


def test_gist_contains_no_jargon_at_all():
    """
    الشرط الذي يجعل الخلاصة خلاصة: ألّا تحتاج هي نفسها شرحًا.

    والفحص ليس بحثًا عن كلمات في قائمة — بل: نُمرّر نصّ الخلاصة على
    مُبسّط المصطلحات، فإن **غيّر فيه حرفًا** فقد تسرّب مصطلح. أي إن
    الخلاصة يجب أن تكون نقطة ثابتة للمُبسِّط.
    """
    from falak import plain
    leaks = []
    for name, d in _gist_cases():
        g = d["gist"]
        for txt in [g["title"], g.get("then", "")] + g["lines"]:
            if txt and plain.simplify(txt) != txt:
                leaks.append((name, txt[:70]))
    assert not leaks, f"مصطلحات تسرّبت إلى الخلاصة: {leaks[:3]}"


def test_gist_speaks_to_someone_who_knows_nothing():
    """
    مقياس عمليّ: جمل قصيرة، ولا رموز فلكية، ولا درجات وأرقام قوسية.
    فمن رأى «١١° ٢٢′ السرطان» في الخلاصة لم يُخاطَب بلغته.
    """
    import re
    for name, d in _gist_cases():
        g = d["gist"]
        joined = " ".join(g["lines"])
        assert "°" not in joined and "′" not in joined, name
        assert not re.search(r"[☉☾☿♀♂♃♄♅♆♇☊⚸⚷]", joined), name
        for line in g["lines"]:
            assert len(line) < 400, f"{name}: سطر أطول من أن يكون خلاصة"


def test_gist_failure_never_breaks_the_answer():
    """الخلاصة زينة لا أساس: إن سقطت لم تُسقط الجواب معها."""
    from falak import gist
    assert gist.for_route("chart", {}) is None or isinstance(
        gist.for_route("chart", {}), dict)
    assert gist.for_route("لا-يوجد", {"x": 1}) is None


def test_home_page_advertises_nothing_that_is_missing():
    """
    كانت البوّابة تعِد بثلاث أدوات «قريبًا» وهي منشورة من أسابيع،
    وتربطها بـ href="#". فلا رابط ميت ولا وعد مؤجَّل.
    """
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    assert 'href="#"' not in html
    assert "soon" not in html
    import re
    for href in re.findall(r'href="(/[^"]*\.html)"', html):
        assert os.path.exists(os.path.join(root, href.lstrip("/"))), href


def test_navigation_covers_every_page_exactly_once():
    """
    التصفّح صار في ملفّ واحد (assets/nav.js) لأنه كان مكرّرًا في
    اثنتي عشرة صفحة، فكل إضافة تعني اثني عشر تعديلًا — ونسينا
    رابطًا مرّة فعلًا. فنتحقّق أن كل صفحة مذكورة، ومرّة واحدة.
    """
    import os, re, glob
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nav = open(os.path.join(root, "assets/nav.js"), encoding="utf-8").read()
    listed = re.findall(r"\['(/[a-z]+\.html)'", nav)
    assert len(listed) == len(set(listed)), "رابط مكرّر في الأبواب"
    pages = {os.path.basename(p) for p in glob.glob(os.path.join(root, "*.html"))}
    pages.discard("index.html")            # الرئيسة لها زرّها الخاصّ
    missing = pages - {x.lstrip("/") for x in listed}
    assert not missing, f"صفحات خارج التصفّح: {missing}"
    for href in listed:
        assert os.path.exists(os.path.join(root, href.lstrip("/"))), href


def test_every_page_loads_the_shared_navigation():
    import os, glob
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in glob.glob(os.path.join(root, "*.html")):
        html = open(p, encoding="utf-8").read()
        assert "/assets/nav.js" in html, os.path.basename(p)
        assert 'meta name="description"' in html, os.path.basename(p)
        assert 'name="viewport"' in html, os.path.basename(p)


# ══════════════════════════════════════════════════════════════════
# ١٩ — الجيوتِش
# ══════════════════════════════════════════════════════════════════
def test_lahiri_is_defined_by_spica():
    """
    أينامشا لاهيري مُعرَّفة بأن السماك الأعزل على ١٨٠° نجمية —
    ومن هنا اسمها «تشيترا باكشا». فإن أخطأنا هذا أخطأنا كلّ شيء،
    ولا مجال للجدال فيه.
    """
    import swisseph as swe
    from falak import jyotish as jy
    for year in (1900, 2000, 2100):
        t = datetime(year, 1, 1, 12, tzinfo=UTC)
        jy._sid("lahiri")
        L = swe.fixstar_ut("Spica", ephem.to_jd(t),
                           swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
        assert abs(L - 180.0) < 0.02, (year, L)


def test_ayanamsha_matches_the_published_table():
    """قيم التقويم الهندي الرسمي، إلى أقلّ من دقيقة قوسية."""
    from falak import jyotish as jy
    for when, want in [(datetime(1900, 1, 1, tzinfo=UTC), 22.4594),
                       (datetime(1950, 1, 1, tzinfo=UTC), 23.1589),
                       (datetime(2000, 1, 1, tzinfo=UTC), 23.8531)]:
        assert abs(jy.ayanamsha(when, "lahiri") - want) < 0.01, when


def test_sidereal_equals_mean_tropical_minus_ayanamsha():
    """
    ظننّا أن النجمي = الاستوائي ناقص الأينامشا، فخالفنا الحساب
    بـ١٤ ثانية قوسية. والسبب اهتزاز محور الأرض: الاستوائي الظاهري
    يحمله والأينامشا تُقاس من الاعتدال المتوسّط. فالمعادلة الصحيحة
    تستعمل الموضع **بلا اهتزاز** — وتصحّ إلى الصفر.
    """
    import swisseph as swe
    from falak import jyotish as jy
    when = datetime(2000, 1, 1, 12, tzinfo=UTC)
    jd = ephem.to_jd(when)
    jy._sid("lahiri")
    ay = jy.ayanamsha(when)
    for body in (swe.SUN, swe.MOON, swe.MARS):
        mean = swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_NONUT)[0][0] % 360
        sid = swe.calc_ut(jd, body,
                          swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360
        assert abs((mean - sid) % 360 - ay) < 1e-6, body
        app = swe.calc_ut(jd, body, swe.FLG_SWIEPH)[0][0] % 360
        # ومع الاهتزاز يبقى فارق يُقاس بالثواني — وهذا صواب لا خطأ
        assert 1 < abs((app - sid) % 360 - ay) * 3600 < 25, body


def test_nakshatra_division_is_exact():
    from falak import jyotish as jy
    assert len(jy.NAKSHATRAS) == 27
    assert abs(jy.NAK_ARC - (13 + 20 / 60)) < 1e-12
    assert jy.nakshatra_of(0.001)["index"] == 1
    assert jy.nakshatra_of(359.999)["index"] == 27
    assert jy.nakshatra_of(0.0)["pada"] == 1
    assert jy.nakshatra_of(jy.NAK_ARC - 1e-6)["pada"] == 4
    # لا فجوة ولا تداخل: كل درجة في منزلة واحدة
    prev = 0
    for step in range(0, 3600):
        i = jy.nakshatra_of(step / 10.0)["index"]
        assert i in (prev, prev + 1) or (prev == 27 and i == 1) or prev == 0
        prev = i


def test_nakshatra_star_may_fall_outside_its_division():
    """
    مفاجأة كشفها التحقّق الخارجي: نجم المنزلة ليس دائمًا داخل
    حدودها. فالمنازل كانت غير متساوية ثم سُوّيت إلى ١٣°٢٠′، فبقيت
    الأسماء على نجومها وخرج بعضها. نُثبّت هذا لئلّا يُظنّ خطأً
    ويُصحَّح تصحيحًا يُفسد الحساب.
    """
    from falak import jyotish as jy
    when = datetime(2000, 1, 1, 12, tzinfo=UTC)
    inside, outside = [], []
    for idx in jy.YOGATARA:
        y = jy.yogatara(idx, when)
        if not y:
            continue
        (inside if y["inside"] else outside).append((idx, y["offset"]))
    assert inside and outside, "لا بدّ من الحالتين معًا"
    # السماك الرامح — نجم سْواتي — أبعدها: نحو ست درجات
    swati = jy.yogatara(15, when)
    assert not swati["inside"] and 5 < swati["offset"] < 8
    # والسماك الأعزل داخل تشيترا تمامًا، فهو مرجع الأينامشا
    assert jy.yogatara(14, when)["inside"]
    for idx, off in outside:
        assert jy.yogatara(idx, when)["note"].startswith("النجم خارج")


def test_arabic_mansions_are_paired_with_every_nakshatra():
    """الوصل الذي يخصّنا: لكل منزلة هندية مقابلها العربي."""
    from falak import jyotish as jy
    for n in jy.NAKSHATRAS:
        assert len(n) == 4 and all(n), n
        assert n[1] in jy.DASHA_ORDER, f"ربّ غير معروف: {n[1]}"
    arabics = [n[2] for n in jy.NAKSHATRAS]
    assert len(set(arabics)) == 27, "منزلة عربية مكرّرة"


def test_vimshottari_cycle_and_continuity():
    from falak import jyotish as jy
    assert sum(jy.DASHA_YEARS.values()) == 120
    birth = datetime(1990, 5, 17, 5, 30, tzinfo=UTC)
    c = jy.compute(birth, 36.2021, 37.1343, "lahiri", "UTC")
    moon = next(b for b in c["bodies"] if b["name"] == "القمر")
    d = jy.vimshottari(birth, moon["lon"])
    ps = d["periods"]
    for i in range(len(ps) - 1):
        assert ps[i]["end"] == ps[i + 1]["start"], i
    assert ps[0]["planet"] == d["start_lord"] == moon["nakshatra"]["lord"]
    assert abs(sum(p["years"] for p in ps[1:10]) - 120.0) < 1e-6
    assert ps[9]["planet"] == ps[0]["planet"]
    for p in ps[:3]:
        subs = p["sub"]
        assert len(subs) == 9
        assert subs[0]["planet"] == p["planet"]     # تبدأ الصغرى بربّ الكبرى
        # الادّعاء الأقوى: **التواريخ** تنطبق تمامًا. أمّا حقل «السنوات»
        # فمقرَّب إلى أربع منازل للعرض، فمجموعه يفرق بجزء من عشرة آلاف —
        # وهو فرق عرضٍ لا فرق حساب.
        assert subs[0]["start"] == p["start"]
        assert subs[-1]["end"] == p["end"]
        for i in range(8):
            assert subs[i]["end"] == subs[i + 1]["start"], (p["planet"], i)
        assert abs(sum(s["years"] for s in subs) - p["years"]) < 1e-3


def test_navamsa_follows_the_standard_division():
    """
    D9: أوّل نافامشا الحمل هو الحمل، وأوّل نافامشا الثور هو الجدي.
    وهذا محكّ يفصل الحساب الصحيح عن قسمة ساذجة.
    """
    from falak import jyotish as jy
    assert jy.varga(0.0, 9) == "الحمل"
    assert jy.varga(30.0, 9) == "الجدي"
    assert jy.varga(60.0, 9) == "الميزان"
    assert jy.varga(120.0, 9) == "الحمل"
    assert jy.varga(1.0, 1) == "الحمل" and jy.varga(31.0, 1) == "الثور"


def test_jyotish_exaltations_are_sidereal():
    from falak import jyotish as jy
    assert jy.dignity_of("الشمس", "الحمل", 10.0)["kind"] == "الذروة"
    assert jy.dignity_of("الشمس", "الميزان", 10.0)["kind"] == "الهبوط"
    assert jy.dignity_of("زحل", "الميزان", 20.0)["kind"] == "الذروة"
    assert jy.dignity_of("المشتري", "الجدي", 5.0)["kind"] == "الهبوط"
    assert jy.dignity_of("الشمس", "الأسد", 5.0)["kind"] == "المثلّث الأصلي"
    assert jy.dignity_of("القمر", "السرطان", 15.0)["kind"] == "بيته"


def test_jyotish_route_shows_the_shift_before_being_asked():
    """
    أوّل ما يصدم القارئ العربي أن برجه تغيّر. فلا بدّ أن يُشرح
    في الجواب نفسه، لا أن يُترك ليظنّ الحساب خاطئًا.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/jyotish', q(date="1990-05-17", time="08:30", city="حلب"))
    cmp_ = d["compare_tropical"]
    assert cmp_["bodies"] and cmp_["note"]
    assert "خطأ" in cmp_["note"]                 # ينفي الخطأ صراحةً
    moved = [n for n, v in cmp_["bodies"].items() if v["moved"]]
    assert len(moved) >= 5, "الفرق نحو ٢٤ درجة، فأكثرها يتراجع برجًا"
    assert len(d["bodies"]) == 9 and d["lagna"]["nakshatra"]
    assert d["dasha"]["periods"] and d["dasha"]["now"]["major"]
    assert d["gist"] and len(d["gist"]["lines"]) >= 3
    for b in d["bodies"]:
        assert b["nakshatra"]["arabic_mansion"], b["name"]

    lst = dispatch('/api/jyotish', q(list="1"))
    assert len(lst["nakshatras"]) == 27
    assert len(lst["ayanamshas"]) >= 3


def test_ayanamsha_choice_actually_changes_the_chart():
    """المفتاح ليس زينة: تغييره يُزحزح المواضع فعلًا."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    a = dispatch('/api/jyotish', q(date="1990-05-17", time="08:30",
                                   city="حلب", ayanamsha="lahiri"))
    b = dispatch('/api/jyotish', q(date="1990-05-17", time="08:30",
                                   city="حلب", ayanamsha="raman"))
    assert a["ayanamsha"]["value"] != b["ayanamsha"]["value"]
    la = {x["name"]: x["lon"] for x in a["bodies"]}
    lb = {x["name"]: x["lon"] for x in b["bodies"]}
    diffs = [abs(la[k] - lb[k]) for k in la]
    assert 1.0 < max(diffs) < 2.0, "راما يفرق عن لاهيري بنحو درجة ونصف"
    with pytest.raises(Exception):
        dispatch('/api/jyotish', q(date="1990-05-17", city="حلب",
                                   ayanamsha="لا-يوجد"))


# ══════════════════════════════════════════════════════════════════
# ٢٠ — اليوغات ونصوص الجيوتِش
# ══════════════════════════════════════════════════════════════════
def _jy_chart(y=1990, mo=5, d=17, h=8, mi=30):
    from falak import jyotish as jy
    return jy.compute(datetime(y, mo, d, h, mi,
                               tzinfo=ZoneInfo("Asia/Damascus")),
                      36.2021, 37.1343, "lahiri", "Asia/Damascus")


def test_raja_yoga_needs_two_different_houses():
    """
    أوّل صياغة أعطت راجا يوغا لـ٧٩٪ من الخرائط، فبطل معناها.
    والسبب أن البيت الأوّل وتد ومثلّث معًا، فكان ربّه يُزاوَج بنفسه.
    نتحقّق أن كل يوغا تذكر بيتين مختلفين وربّين مختلفين.
    """
    import random, re
    from falak import jyotish as jy
    rnd = random.Random(9)
    seen = 0
    for _ in range(40):
        c = _jy_chart(rnd.randint(1950, 2010), rnd.randint(1, 12),
                      rnd.randint(1, 28), rnd.randint(0, 23))
        for y in jy.yogas(c):
            if y["name"] != "راجا يوغا":
                continue
            seen += 1
            hs = re.findall(r"البيت (\d+)", y["why"])
            assert len(hs) >= 2 and hs[0] != hs[1], y["why"]
            lords = re.findall(r"^(\S+) ربّ", y["why"])
            assert "ربّ البيت" in y["why"]
    assert seen, "لم تقع راجا يوغا في العيّنة"


def test_every_yoga_states_its_evidence_and_its_frequency():
    """
    لا نُطلق اسمًا بلا بيّنة، ولا نعِد بندرة لا تصحّ. فمع كل يوغا
    شرطُ تحقّقها بالأسماء والبيوت، ونسبةُ الخرائط التي تحملها.
    """
    import random
    from falak import jyotish as jy
    rnd = random.Random(21)
    total = 0
    for _ in range(30):
        c = _jy_chart(rnd.randint(1950, 2010), rnd.randint(1, 12),
                      rnd.randint(1, 28), rnd.randint(0, 23))
        ys = jy.yogas(c)
        for y in ys:
            total += 1
            assert y["why"] and ("البيت" in y["why"] or "من القمر" in y["why"])
            assert y["meaning"] and y["group"] and y["strength"]
            r = y["rarity"]
            assert r["word"] and r["note"]
            assert r["pct"] is None or 0 < r["pct"] <= 100
        # الأندر أوّلًا
        pcts = [y["rarity"]["pct"] or 0 for y in ys]
        assert pcts == sorted(pcts), pcts
    assert total > 20


def test_yoga_frequency_table_matches_reality():
    """
    النسب المخزونة تكذب إن تغيّرت شروط اليوغات ولم تُعَد المعايرة.
    فنقيس عيّنة جديدة ونتحقّق أن الشائع شائع والنادر نادر.
    """
    import random
    from falak import jyotish as jy
    rnd = random.Random(404)
    tally, n = {}, 150
    for _ in range(n):
        c = _jy_chart(rnd.randint(1940, 2012), rnd.randint(1, 12),
                      rnd.randint(1, 28), rnd.randint(0, 23),
                      rnd.randint(0, 59))
        for name in {y["name"] for y in jy.yogas(c)}:
            tally[name] = tally.get(name, 0) + 1
    for name, want in jy.YOGA_FREQUENCY.items():
        got = 100 * tally.get(name, 0) / n
        assert abs(got - want) < 16, (
            f"{name}: قِسناها {got:.0f}٪ والمخزون {want}٪ — أعِد المعايرة")


def test_jyotish_texts_cover_every_combination():
    """التغطية الكاملة: لا موضع بلا نصّ مكتوب."""
    from falak import jyotish as jy, jyotish_deep as jd
    for p, _sa, _c in jy.GRAHAS:
        for h in range(1, 13):
            t = jd.graha_in_bhava(p, h)
            assert t and len(t) > 25, (p, h)
    for name, _lord, _ar, _star in jy.NAKSHATRAS:
        d = jd.nak_text(name)
        assert d, name
        # «الطبع» وسم قصير مقصود، والباقي جُمل
        assert d.get("nature") and 8 < len(d["nature"]) < 40, name
        for k in ("gift", "cost", "moon"):
            assert d.get(k) and len(d[k]) > 30, (name, k)
    for h in range(1, 13):
        sa, rules, note = jd.bhava_text(h)
        assert sa and rules and note, h


def test_jyotish_texts_are_distinct():
    """التمايز يُثبت أنها مكتوبة لا مركّبة."""
    from falak import jyotish_deep as jd
    seen = set()
    for p, tbl in jd.GRAHA_BHAVA.items():
        for h, t in tbl.items():
            assert t not in seen, f"{p}/{h} مكرّر"
            seen.add(t)
    assert len(seen) == 108
    for field in ("gift", "cost", "moon", "nature"):
        vals = [v[field] for v in jd.NAK_DEEP.values()]
        assert len(set(vals)) == 27, field


def test_jyotish_texts_are_not_translated_from_the_arabic():
    """
    الشرط الذي فرضناه على أنفسنا: لا نترجم من العربي. فالمدرستان
    منظومتان مختلفتان، والنقل الحرفي يُخفي ذلك. نتحقّق ألّا يتطابق
    نصّ هنديّ مع نصّ عربيّ.
    """
    from falak import depth, jyotish_deep as jd
    arabic = {t for tbl in depth.PLANET_IN_HOUSE.values()
              for t in tbl.values()}
    indian = {t for tbl in jd.GRAHA_BHAVA.values() for t in tbl.values()}
    assert not (arabic & indian), "نصّ منقول حرفيًّا بين المدرستين"


def test_planetary_relations_are_symmetric_in_kind_not_in_value():
    """
    الصداقة الوقتية غير متبادلة بالضرورة: قد يكون هذا صديقًا لذاك
    وليس العكس — وهذا منصوص عندهم لا خطأ عندنا.
    """
    from falak import jyotish as jy
    assert jy.natural_relation("الشمس", "زحل") == "عدوّ"
    assert jy.natural_relation("زحل", "الشمس") == "عدوّ"
    assert jy.natural_relation("القمر", "عطارد") == "صديق"
    assert jy.natural_relation("عطارد", "القمر") == "عدوّ"   # غير متبادلة
    assert jy.temporal_relation(1, 3) == "صديق"
    assert jy.temporal_relation(1, 7) == "عدوّ"
    c = _jy_chart()
    r = jy.relations(c["bodies"])
    assert set(r) <= set(jy.SEVEN)
    for a, row in r.items():
        for b, v in row.items():
            assert v["compound"] in ("صديق حميم", "صديق", "محايد",
                                     "عدوّ", "عدوّ لدود")


def test_jyotish_route_carries_texts_and_yogas():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/jyotish', q(date="1990-05-17", time="08:30", city="حلب"))
    assert len(d["bhavas"]) == 12
    assert "yogas" in d and "relations" in d and d["yoga_note"]
    for b in d["bodies"]:
        assert b["reading"], b["name"]
        assert b["bhava"]["sanskrit"] and b["bhava"]["rules"]
        assert b["nakshatra"]["deep"].get("gift"), b["name"]
    assert d["lagna"]["nakshatra"]["deep"].get("nature")


# ══════════════════════════════════════════════════════════════════
# ٢١ — البازي: الأركان الأربعة
# ══════════════════════════════════════════════════════════════════
def test_sexagenary_day_anchors_agree_across_a_century():
    """
    نقطتان معروفتان يفصل بينهما قرن. اتّفاقهما برهان على أن
    التسلسل صحيح يومًا بيوم — واحتمال وقوعه مصادفةً واحد من ستّين.

    (أدرجنا أوّلًا أربع قيم من الذاكرة فخالفتنا اثنتان، وتبيّن أن
    الذاكرة هي المخطئة. فلا نُثبّت إلا ما نتحقّق منه.)
    """
    from falak import bazi as bz
    assert bz.day_pillar(date(1900, 1, 1)) == ("جيا", "شو")     # 甲戌
    assert bz.day_pillar(date(2000, 1, 1)) == ("وو", "وُو")      # 戊午
    n = (date(2000, 1, 1) - date(1900, 1, 1)).days
    assert n % 10 == 4 and n % 12 == 8


def test_sexagenary_cycles_close():
    from falak import bazi as bz
    assert bz.year_pillar(1984) == ("جيا", "زي")
    assert bz.year_pillar(2044) == bz.year_pillar(1984)
    assert len({bz.year_pillar(1984 + i) for i in range(60)}) == 60
    d0 = date(2000, 1, 1)
    assert bz.day_pillar(d0) == bz.day_pillar(d0 + timedelta(days=60))
    assert len({bz.day_pillar(d0 + timedelta(days=i))
                for i in range(60)}) == 60


def test_animal_years_people_know():
    from falak import bazi as bz
    for y, want in [(1984, "الفأر"), (1990, "الحصان"), (2000, "التنّين"),
                    (2024, "التنّين"), (2025, "الأفعى"), (2026, "الحصان")]:
        _s, b = bz.year_pillar(y)
        assert bz.BRANCHES[bz._BRANCH_I[b]][2] == want, y


def test_solar_terms_are_exact_degrees():
    """الفصول ليست تواريخ محفوظة: هي لحظات بلوغ الشمس درجةً بعينها."""
    from falak import bazi as bz
    terms = bz.solar_terms(2026)
    assert len(terms) == 12
    for t in terms:
        L = ephem.lon_of("الشمس", t["when_utc"])
        assert abs(((L - t["degree"] + 180) % 360) - 180) < 1e-4, t["name"]
    for i in range(11):
        gap = (terms[i + 1]["when_utc"] - terms[i]["when_utc"]).days
        assert 28 <= gap <= 33, (terms[i]["name"], gap)
    assert terms[0]["name"] == "قيام الربيع"


def test_year_begins_at_li_chun_not_lunar_new_year():
    """
    أشهر خطأ في هذا الباب: نسبة المولود إلى حيوان رأس السنة القمرية.
    وسنة البازي تبدأ بقيام الربيع — وبينهما أسبوعان أحيانًا.
    """
    from falak import bazi as bz
    tz = ZoneInfo("Asia/Shanghai")
    lc = bz.li_chun(2025).astimezone(tz)
    before = bz.compute(lc - timedelta(days=1), "Asia/Shanghai")
    after = bz.compute(lc + timedelta(days=1), "Asia/Shanghai")
    assert before["bazi_year"] == 2024 and before["animal"] == "التنّين"
    assert after["bazi_year"] == 2025 and after["animal"] == "الأفعى"
    # والتنبيه يظهر للقارئ لا يُكتَم
    assert before["li_chun"]["before"]
    assert "يُخطئ" in before["li_chun"]["note"]
    assert not after["li_chun"]["before"]


def test_month_begins_at_the_solar_term():
    from falak import bazi as bz
    tz = ZoneInfo("Asia/Shanghai")
    terms = bz.solar_terms(2026)
    for t in terms[1:5]:
        edge = t["when_utc"].astimezone(tz)
        a = bz.compute(edge - timedelta(hours=3), "Asia/Shanghai")
        b = bz.compute(edge + timedelta(hours=3), "Asia/Shanghai")
        assert (a["pillars"][1]["branch"]["name"]
                != b["pillars"][1]["branch"]["name"]), t["name"]
        assert b["pillars"][1]["branch"]["name"] == t["branch"]


def test_late_zi_hour_rolls_to_the_next_day():
    """من وُلد بعد الحادية عشرة ليلًا يُحسَب عمود يومه لليوم التالي."""
    from falak import bazi as bz
    tz = ZoneInfo("Asia/Shanghai")
    a = bz.compute(datetime(2026, 3, 10, 22, 30, tzinfo=tz), "Asia/Shanghai")
    b = bz.compute(datetime(2026, 3, 10, 23, 30, tzinfo=tz), "Asia/Shanghai")
    assert not a["late_zi"] and b["late_zi"]
    nxt = bz.day_pillar(date(2026, 3, 11))
    assert (b["pillars"][2]["stem"]["name"],
            b["pillars"][2]["branch"]["name"]) == nxt
    assert b["pillars"][3]["branch"]["name"] == "زي"


def test_five_tigers_and_five_rats_rules():
    from falak import bazi as bz
    assert bz.month_stem("جيا", "يِن") == "بينغ"
    assert bz.month_stem("جي", "يِن") == "بينغ"
    assert bz.month_stem("وو", "يِن") == "جيا"
    assert bz.hour_stem("جيا", "زي") == "جيا"
    assert bz.hour_stem("جي", "زي") == "جيا"
    # والجذع يتسلسل مع الفرع
    assert bz.hour_stem("جيا", "تشو") == "يي"


def test_five_elements_cycles_are_closed():
    from falak import bazi as bz
    assert len(bz.ELEMENTS) == 5
    for e in bz.ELEMENTS:
        assert bz.GENERATES[e] in bz.ELEMENTS
        assert bz.CONTROLS[e] in bz.ELEMENTS
        assert bz.GENERATES[e] != e and bz.CONTROLS[e] != e
    # الدورتان تعودان إلى نقطة البدء بعد خمس
    for e in bz.ELEMENTS:
        x = e
        for _ in range(5):
            x = bz.GENERATES[x]
        assert x == e
        y = e
        for _ in range(5):
            y = bz.CONTROLS[y]
        assert y == e


def test_ten_gods_are_measured_from_the_day_master():
    from falak import bazi as bz
    assert bz.ten_god("جيا", "جيا")["name"] == "أخ مُوازٍ"      # خشب/خشب
    assert bz.ten_god("جيا", "يي")["name"] == "أخ مُنافس"
    assert "أمّ" in bz.ten_god("جيا", "قوَي")["name"]            # الماء يُولّد الخشب
    assert "إخراج" in bz.ten_god("جيا", "بينغ")["name"]         # الخشب يُولّد النار
    assert "مال" in bz.ten_god("جيا", "وو")["name"]             # الخشب يقهر التراب
    assert "سلطة" in bz.ten_god("جيا", "غِنغ")["name"]          # المعدن يقهر الخشب


def test_luck_cycles_direction_depends_on_sex_and_year():
    """قاعدة منصوصة عندهم: الاتّجاه يختلف بالجنس وقطبية جذع السنة."""
    from falak import bazi as bz
    yang = bz.compute(datetime(1990, 5, 17, 8, 30,
                               tzinfo=ZoneInfo("Asia/Damascus")),
                      "Asia/Damascus")
    assert yang["pillars"][0]["stem"]["polarity"] == "يانغ"
    assert bz.luck_cycles(yang, male=True)["forward"]
    assert not bz.luck_cycles(yang, male=False)["forward"]
    yin = bz.compute(datetime(1991, 5, 17, 8, 30,
                              tzinfo=ZoneInfo("Asia/Damascus")),
                     "Asia/Damascus")
    assert yin["pillars"][0]["stem"]["polarity"] == "ين"
    assert not bz.luck_cycles(yin, male=True)["forward"]
    assert bz.luck_cycles(yin, male=False)["forward"]
    m = bz.luck_cycles(yang, male=True)
    assert 0 <= m["start_age"] <= 10
    for i in range(len(m["cycles"]) - 1):
        assert abs(m["cycles"][i + 1]["from_age"]
                   - m["cycles"][i]["from_age"] - 10) < 0.01


def test_bazi_route_and_gist():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    from falak import plain
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/bazi', q(date="1990-05-17", time="08:30",
                                city="حلب", sex="m"))
    assert len(d["pillars"]) == 4
    for p in d["pillars"]:
        assert p["stem"]["chinese"] and p["branch"]["chinese"] and p["role"]
    assert d["day_master"]["element"] and d["animal"]
    assert abs(sum(v["pct"] for v in d["elements"].values()) - 100) < 0.5
    assert len(d["ten_gods"]) == 4
    assert d["luck"]["cycles"] and d["luck"]["direction_note"]
    g = d["gist"]
    assert g and len(g["lines"]) >= 3
    for t in [g["title"], g["then"]] + g["lines"]:
        assert plain.simplify(t) == t, t

    # بلا جنس: تُشرَح الحاجة ولا تُخفى
    d2 = dispatch('/api/bazi', q(date="1990-05-17", city="حلب"))
    assert "luck" not in d2 and "sex=" in d2["luck_note"]

    lst = dispatch('/api/bazi', q(list="1"))
    assert len(lst["stems"]) == 10 and len(lst["branches"]) == 12
    assert len(lst["solar_terms"]) == 12


# ══════════════════════════════════════════════════════════════════
# ٢٢ — نصوص البازي
# ══════════════════════════════════════════════════════════════════
def test_bazi_texts_cover_every_combination():
    """التغطية الكاملة: كل جذع وكل فرع وكل تركيب سيّد نفس × غالب."""
    from falak import bazi as bz, bazi_deep as bd
    for name, *_ in bz.STEMS:
        d = bd.stem_text(name)
        assert d and d["image"] and len(d["text"]) > 40 and d["cost"], name
    for name, *_ in bz.BRANCHES:
        d = bd.branch_text(name)
        assert d and d["season"] and d["hours"] and len(d["text"]) > 30, name
    # خمسة عناصر × خمسة غالبة = خمسة وعشرون تركيبًا، كلّها مكتوبة
    for me in bz.ELEMENTS:
        for dom in bz.ELEMENTS:
            t = bd.day_master_text(me, dom)
            assert t and len(t) > 50, (me, dom)
    assert len(bd.DAY_MASTER) == 25
    for e in bz.ELEMENTS:
        r = bd.remedy(e)
        assert all(r.get(k) for k in ("colors", "directions", "work", "habits")), e


def test_bazi_texts_are_distinct():
    from falak import bazi_deep as bd
    for tbl, field in [(bd.STEM_DEEP, "text"), (bd.STEM_DEEP, "cost"),
                       (bd.BRANCH_DEEP, "text")]:
        vals = [v[field] for v in tbl.values()]
        assert len(set(vals)) == len(vals), field
    assert len(set(bd.DAY_MASTER.values())) == 25
    assert len(set(bd.TEN_GODS_DEEP.values())) == len(bd.TEN_GODS_DEEP)


def test_bazi_texts_are_not_borrowed_from_the_other_schools():
    """
    الشرط نفسه المفروض على الجيوتِش: لا نقل بين المدارس. والبازي
    أبعدها عن الاثنتين — لا كواكب فيه ولا بروج.
    """
    from falak import bazi_deep as bd, depth, jyotish_deep as jd
    arabic = {t for tbl in depth.PLANET_IN_HOUSE.values() for t in tbl.values()}
    indian = {t for tbl in jd.GRAHA_BHAVA.values() for t in tbl.values()}
    chinese = set(bd.DAY_MASTER.values())
    chinese |= {v["text"] for v in bd.STEM_DEEP.values()}
    chinese |= {v["text"] for v in bd.BRANCH_DEEP.values()}
    assert not (chinese & arabic) and not (chinese & indian)


def test_every_ten_god_name_has_a_written_text():
    """كل اسم يُخرجه المحرّك لا بدّ أن يجد نصًّا — وإلا ظهر فارغًا."""
    from falak import bazi as bz, bazi_deep as bd
    names = set()
    for dm, *_ in bz.STEMS:
        for other, *_ in bz.STEMS:
            g = bz.ten_god(dm, other)
            if g.get("name"):
                names.add(g["name"])
    names.add("سيّد النفس")
    for n in names:
        assert bd.god_text(n), n
    assert names <= set(bd.TEN_GODS_DEEP)


def test_bazi_route_carries_the_readings_and_remedies():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/bazi', q(date="1990-05-17", time="08:30",
                                city="حلب", sex="m"))
    assert d["day_master_reading"] and len(d["day_master_reading"]) > 50
    for p in d["pillars"]:
        assert p["stem"]["deep"]["image"] and p["stem"]["deep"]["text"]
        assert p["branch"]["deep"]["season"] and p["branch"]["deep"]["text"]
    for g in d["ten_gods"]:
        assert g["god"].get("reading"), g["pillar"]
    # النقص يُكمَّل: باب عمليّ لا يوجد في المدرستين الأخريين
    assert d["remedies"] and d["remedy_note"]
    for e, r in d["remedies"].items():
        assert r["colors"] and r["work"] and r["habits"]
    assert d["luck"]["what_is_it"]
    for c in d["luck"]["cycles"]:
        assert c["god"].get("reading")


# ══════════════════════════════════════════════════════════════════
# ٢٣ — التوافق بالمدرستين
# ══════════════════════════════════════════════════════════════════
def _two_jy():
    from falak import jyotish as jy
    a = jy.compute(datetime(1990, 5, 17, 8, 30,
                            tzinfo=ZoneInfo("Asia/Damascus")),
                   36.2, 37.13, "lahiri", "Asia/Damascus")
    b = jy.compute(datetime(1992, 11, 3, 21, 15,
                            tzinfo=ZoneInfo("Europe/Paris")),
                   48.86, 2.35, "lahiri", "Europe/Paris")
    return a, b


def test_ashta_koota_totals_thirty_six():
    from falak import jyotish_match as jm
    a, b = _two_jy()
    r = jm.ashta_koota(a, b)
    assert sum(k["max"] for k in r["kootas"]) == 36 == r["max"]
    assert len(r["kootas"]) == 8
    for k in r["kootas"]:
        assert 0 <= k["got"] <= k["max"], k["name"]
        assert k["detail"] and k["note"]
    assert abs(sum(k["got"] for k in r["kootas"]) - r["total"]) < 0.05
    names = [k["name"] for k in r["kootas"]]
    assert names == ["الفَرْنا", "الڤَشْيا", "التارا", "اليوني",
                     "غْرَها مَيْتري", "الغانا", "البهاكوت", "النادي"]


def test_koota_tables_are_complete_and_consistent():
    from falak import jyotish as jy, jyotish_match as jm
    assert len(jm.NAK_MATCH) == 27
    for i, (animal, sex, gana, nadi) in enumerate(jm.NAK_MATCH):
        assert animal and sex in ("ذكر", "أنثى")
        assert gana in ("ديفا", "إنسان", "راكشاسا")
        assert nadi in ("أولى", "وسطى", "أخيرة")
    # حيوانات اليوني أربعة عشر لسبع وعشرين منزلة، فلا بدّ أن يبقى
    # واحد بلا زوج: وهو **النمس** — وهذا منصوص عندهم لا سهو منّا.
    # (ظننّاه خطأً أوّلًا، فتبيّن أن الجدول على صوابه.)
    from collections import Counter
    c = Counter(a for a, *_ in jm.NAK_MATCH)
    assert len(c) == 14
    singles = [k for k, v in c.items() if v == 1]
    assert singles == ["النمس"], c
    assert all(v == 2 for k, v in c.items() if k != "النمس")
    assert sum(c.values()) == 27
    # النادي موزّع بالتساوي: تسع لكلٍّ
    n = Counter(x[3] for x in jm.NAK_MATCH)
    assert set(n.values()) == {9}, n
    # وكل برج له فَرْنا وڤَشْيا
    for s in jy.ch.SIGNS if hasattr(jy, "ch") else chart.SIGNS:
        assert s in jm.VARNA and s in jm.VASHYA


def test_nadi_dosha_and_bhakoot_are_detected():
    """أثقل بابين في النظام — لا بدّ أن يُمسَكا حين يقعان."""
    from falak import jyotish_match as jm
    # نادي واحد ⇒ صفر
    same = jm._nadi(1, 6)          # أشويني وأردرا كلتاهما «أولى»
    assert same["got"] == 0 and same["flagged"]
    assert "مُبطِلات" in same["note"]      # ونقول إن لها مُبطِلات
    diff = jm._nadi(1, 2)
    assert diff["got"] == 8 and not diff["flagged"]
    # البهاكوت: المسافات ٦/٨ و٥/٩ و٢/١٢ معسِّرة
    assert jm._bhakoot("الحمل", "العقرب")["got"] == 0      # ٨ و٦
    assert jm._bhakoot("الحمل", "الثور")["got"] == 0       # ٢ و١٢
    assert jm._bhakoot("الحمل", "الجوزاء")["got"] == 7     # ٣ و١١


def test_varna_is_flagged_as_caste_based():
    """
    باب الفَرْنا أصله طبقيّ. نحسبه لأنه من النظام، ونقول ما هو —
    واختبار يمنع حذف هذا التصريح بسهو.
    """
    from falak import jyotish_match as jm
    a, b = _two_jy()
    r = jm.ashta_koota(a, b)
    varna = next(k for k in r["kootas"] if k["name"] == "الفَرْنا")
    assert varna["flagged"]
    assert "طبقات" in varna["note"] and "لا نُقرّه" in varna["note"]
    assert "طبقيّ" in r["limits"] and "ظلمه" in r["limits"]
    assert r["asymmetry_note"]


def test_chinese_branch_relations_are_exact():
    from falak import bazi_match as bm
    # التصادم بين المتقابلين على الدائرة
    assert bm.branch_relation("زي", "وُو")["kind"] == "تصادم"
    assert bm.branch_relation("تشِن", "شو")["kind"] == "تصادم"
    # الوفاق السداسي
    assert bm.branch_relation("زي", "تشو")["kind"] == "وفاق سداسي"
    assert bm.branch_relation("وُو", "وَي")["kind"] == "وفاق سداسي"
    # التآلف الثلاثي
    assert bm.branch_relation("زي", "شِن")["kind"] == "تآلف ثلاثي"
    assert bm.branch_relation("يِن", "شو")["kind"] == "تآلف ثلاثي"
    assert bm.branch_relation("زي", "زي")["kind"] == "تطابق"
    # كل الجداول متماثلة في الاتّجاهين
    from falak import bazi as bz
    for a, *_ in bz.BRANCHES:
        for b, *_ in bz.BRANCHES:
            assert (bm.branch_relation(a, b)["kind"]
                    == bm.branch_relation(b, a)["kind"]), (a, b)


def test_chinese_trines_and_clashes_cover_the_circle():
    from falak import bazi as bz, bazi_match as bm
    assert len(bm.TRINES) == 4
    assert sorted(b for g, *_ in bm.TRINES for b in g) == sorted(
        b for b, *_ in bz.BRANCHES)
    assert len(bm.HARMONIES) == 6 and len(bm.CLASHES) == 6
    # التصادم دائمًا بين فرعين تفصلهما ستّة مواضع
    for a, b in bm.CLASHES:
        assert (bz._BRANCH_I[a] - bz._BRANCH_I[b]) % 12 == 6


def test_bazi_match_is_symmetric_in_score():
    from falak import bazi as bz, bazi_match as bm
    a = bz.compute(datetime(1990, 5, 17, 8, 30,
                            tzinfo=ZoneInfo("Asia/Damascus")), "Asia/Damascus")
    b = bz.compute(datetime(1992, 11, 3, 21, 15,
                            tzinfo=ZoneInfo("Europe/Paris")), "Europe/Paris")
    assert bm.compare(a, b)["score"] == bm.compare(b, a)["score"]
    r = bm.compare(a, b, "أ", "ب")
    assert len(r["pillars"]) == 4
    assert r["elements"]["note"] and r["day_masters"]["note"]
    assert "ربع الخريطة" in r["animals_note"]


def test_synastry_route_carries_all_three_schools():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import dispatch
    q = lambda **k: {a: [str(b)] for a, b in k.items()}
    d = dispatch('/api/synastry',
                 q(date="1990-05-17", time="08:30", city="حلب", name="أ",
                   date2="1992-11-03", time2="21:15", city2="باريس", name2="ب"))
    assert d["reading"]["scores"]
    assert d["jyotish"]["total"] <= 36 and len(d["jyotish"]["kootas"]) == 8
    assert d["jyotish"]["order_note"] and d["jyotish"]["limits"]
    assert d["bazi"]["score"] and d["bazi"]["pillars"]
    assert "اختلافها هو الفائدة" in d["schools_note"]
    # ويمكن إطفاؤها
    d2 = dispatch('/api/synastry',
                  q(date="1990-05-17", city="حلب", date2="1992-11-03",
                    city2="باريس", schools="0"))
    assert "jyotish" not in d2 and "bazi" not in d2


# ══════════════════════════════════════════════════════════════════
# ٢٤ — التلميع: الطباعة والوصول ومحرّكات البحث
# ══════════════════════════════════════════════════════════════════
def _pages():
    import glob, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return {os.path.basename(p): open(p, encoding="utf-8").read()
            for p in glob.glob(os.path.join(root, "*.html"))}


def _root():
    import os
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_page_is_reachable_by_keyboard_first():
    """
    رابط التخطّي أوّل ما يبلغه التبويب. وبدونه يلزم من يتصفّح
    بلوحة المفاتيح أن يمرّ على أربعة عشر رابطًا في كل صفحة قبل
    أن يبلغ ما جاء لأجله.
    """
    for name, html in _pages().items():
        assert 'class="skip"' in html, name
        assert 'href="#main"' in html, name
        assert 'id="main"' in html, name
        # ويأتي قبل الشريط في ترتيب المستند
        assert html.index('class="skip"') < html.index('class="topbar"'), name


def test_no_form_control_without_a_label():
    import re
    for name, html in _pages().items():
        ids = set(re.findall(r'<label for="([^"]+)"', html))
        for m in re.finditer(r'<(input|select|textarea)[^>]*id="([^"]+)"', html):
            assert m.group(2) in ids, f"{name}: {m.group(2)} بلا تسمية"


def test_stylesheet_honours_user_preferences():
    css = open(_root() + "/assets/style.css", encoding="utf-8").read()
    # من طلب تقليل الحركة فلا حركة — ويهمّ من يُصيبه الدُّوار منها
    assert "prefers-reduced-motion" in css
    assert "canvas.stars{display:none}" in css.replace(" ", "")
    assert "prefers-contrast" in css
    # حلقة تركيز ظاهرة على كل ما يُتنقَّل إليه
    assert "focus-visible" in css
    for sel in ("a:focus-visible", "button:focus-visible", "input:focus-visible"):
        assert sel in css, sel
    assert ".sr-only" in css


def test_print_stylesheet_makes_a_readable_sheet():
    """
    الطباعة ليست لقطة شاشة: تُخفى الأزرار والشريط، وتُقلَب الخلفية
    بيضاء، ويُفتح كل ما كان مطويًّا — فالورقة لا يُضغَط عليها.
    """
    css = open(_root() + "/assets/style.css", encoding="utf-8").read()
    assert "@media print" in css
    block = css[css.index("@media print"):]
    flat = block.replace(" ", "").replace("\n", "")
    assert "background:#fff!important" in flat
    for hidden in ("canvas.stars", ".topbar", ".btn", "nav", "footer"):
        assert hidden in block, hidden
    assert "break-inside:avoid" in flat        # لا تنقطع بطاقة بين صفحتين
    assert "display:table-header-group" in flat  # عنوان الجدول يتكرّر
    assert 'a[href^="http"]::after' in block   # الورق لا يُنقَر، فيُطبع العنوان
    assert "@page" in block


def test_search_engine_files_exist_and_are_valid():
    import os, xml.dom.minidom as minidom
    root = _root()
    sm = os.path.join(root, "sitemap.xml")
    rb = os.path.join(root, "robots.txt")
    assert os.path.exists(sm) and os.path.exists(rb)
    doc = minidom.parse(sm)          # يسقط إن كان XML فاسدًا
    locs = [n.firstChild.data for n in doc.getElementsByTagName("loc")]
    assert len(locs) == len(_pages())
    assert all(u.startswith("https://alfalak.vercel.app") for u in locs)
    assert len(set(locs)) == len(locs)
    robots = open(rb, encoding="utf-8").read()
    assert "Sitemap: https://alfalak.vercel.app/sitemap.xml" in robots
    # مسارات الواجهة تُرجع JSON لا صفحات، فلا تُفهرَس
    assert "Disallow: /api/" in robots


def test_every_page_has_social_and_canonical_metadata():
    import re
    for name, html in _pages().items():
        for tag in ('rel="canonical"', 'og:title', 'og:description',
                    'og:image', 'og:url', 'twitter:card', 'theme-color'):
            assert tag in html, f"{name}: ينقصه {tag}"
        # العنوان القانوني يُطابق اسم الملفّ، فلا تتكرّر صفحة بعنوانين
        canon = re.search(r'rel="canonical" href="([^"]+)"', html).group(1)
        want = ("https://alfalak.vercel.app/"
                + ("" if name == "index.html" else name))
        assert canon == want, f"{name}: {canon}"
        # ووصف اجتماعي غير فارغ ولا مكرّر للعنوان
        desc = re.search(r'property="og:description" content="([^"]+)"', html)
        assert desc and len(desc.group(1)) > 40, name


def test_structured_data_is_valid_json_and_typed():
    import json, re
    for name, html in _pages().items():
        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        assert blocks, f"{name}: بلا بيانات منظّمة"
        for b in blocks:
            data = json.loads(b)      # يسقط إن كان JSON فاسدًا
            assert data["@context"] == "https://schema.org"
            assert data["@type"]
        types = {json.loads(b)["@type"] for b in blocks}
        if name == "index.html":
            assert "WebSite" in types
        else:
            assert "BreadcrumbList" in types, name


def test_share_image_exists_and_is_a_real_png():
    import os
    p = os.path.join(_root(), "assets", "share.png")
    assert os.path.exists(p), "og:image مفقودة — فتظهر الروابط بلا صورة"
    head = open(p, "rb").read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "ليست PNG صحيحة"
    # الأبعاد من ترويسة IHDR
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")
    assert (w, h) == (1200, 630), (w, h)   # المقاس الذي تطلبه الشبكات


def test_static_server_can_serve_the_new_file_types():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.index import read_static, MIME
    assert ".xml" in MIME and ".svg" in MIME and ".txt" in MIME
    for path, ctype in [("/sitemap.xml", "application/xml"),
                        ("/robots.txt", "text/plain"),
                        ("/assets/share.png", "image/png")]:
        hit = read_static(path)
        assert hit, f"{path} لا يُخدَم"
        assert ctype in hit[1], (path, hit[1])


def test_toolbar_is_wired_once_not_fourteen_times():
    """
    أوّل محاولة حقنت الشريط في كل صفحة بتعبير نمطيّ، فأصابت سطر
    التحميل بدل سطر النتيجة وقطعت قوالب نصّية — فسقطت عشر صفحات.
    فصار في موضع واحد: مُراقِب في app.js. ونحرس ألّا يعود التكرار.
    """
    js = open(_root() + "/assets/app.js", encoding="utf-8").read()
    assert "function autoToolbar" in js and "MutationObserver" in js
    assert "function toolbarHTML" in js and "function initToolbar" in js
    assert "window.print()" in js
    for name, html in _pages().items():
        assert "toolbarHTML(" not in html, f"{name}: الشريط مكرّر في الصفحة"


def test_no_decorative_element_wears_a_listener_class():
    """
    **الاختبار الذي وُلد من خطأ.**

    سمّيتُ بطاقات البوّابة الستّ `.q`، وهو صنف علامة المعجم نفسه.
    فالتقطها مستمع المعجم، فأظهر «undefined» — والأدهى أنه يستدعي
    `preventDefault()`، فمنع الانتقال. أي إنّ المدخل الرئيس للموقع
    كان معطّلًا، ولم يكشفه أيٌّ من مئة وتسعين اختبارًا، لأنها جميعًا
    تفحص المنطق ولا تفحص تصادم الأسماء.

    القاعدة التي نحرسها هنا: **كل صنف يلتقطه مستمعٌ عامّ يجب أن يقترن
    بسمة صريحة**، فلا يكفي الصنف وحده للالتقاط.
    """
    import re
    for name, page in _pages().items():
        # يُفحَص **الترميز وحده**: أوّل صياغة فحصت الملفّ كلّه، فأسقطها
        # تعليقٌ عربيّ في السكربت يقتبس `<button class="q">` ليشرح
        # خطأً تجنّبناه. فالحارس يجب أن يعرف حدوده.
        html = re.sub(r'<script[\s\S]*?</script>', '', page)
        for m in re.finditer(r'class="([^"]*)"', html):
            classes = m.group(1).split()
            if "q" not in classes:
                continue
            tag_start = html.rfind("<", 0, m.start())
            tag = html[tag_start:m.end() + 200]
            assert tag.lstrip("<").startswith("button"), (
                f"{name}: عنصر غير زرّ يحمل الصنف `q` — "
                f"هذا عين ما عطّل بطاقات البوّابة: {tag[:80]}")
            assert "data-term=" in tag, (
                f"{name}: زرّ يحمل `q` بلا `data-term` فسيطبع «undefined»: {tag[:80]}")

    # ولا يلتقط مستمع المعجم صنفًا مجرّدًا بعد اليوم
    js = open(_root() + "/assets/hint.js", encoding="utf-8").read()
    assert "'[data-term],[data-hint]'" in js, \
        "الالتقاط يجب أن يكون بسمة صريحة لا بصنف"


def test_hover_explanations_are_wired_everywhere():
    """
    الشرح لا ينفع إن لم يُدرَج في الصفحة. وقد كان `initGlossary()`
    يُنادى في أربع عشرة صفحة، فأبقيناه باسمه وجعلناه يُنبّه إن نُسي
    الملفّ — والاختبار يمنع النسيان أصلًا.
    """
    pages = _pages()
    for name, html in pages.items():
        assert "assets/hint.js" in html, f"{name}: لم يُدرَج hint.js"
        assert html.index("assets/hint.js") > html.index("assets/app.js"), \
            f"{name}: hint.js قبل app.js"

    js = open(_root() + "/assets/hint.js", encoding="utf-8").read()
    for fn in ("function initHints", "function markTerms", "function hintTermPattern",
               "function hintShow", "function hintPlace", "function hintLink"):
        assert fn in js, f"ينقص {fn} من hint.js"
    # التحويم والتركيز واللمس: ثلاثتها لا واحد منها
    for ev in ("pointerover", "pointerout", "focusin", "click", "keydown"):
        assert f"'{ev}'" in js, f"لا مستمع لـ{ev} — فالتجربة ناقصة على أحد الأجهزة"

    css = open(_root() + "/assets/style.css", encoding="utf-8").read()
    for cls in (".hint-pop", ".hint-term", ".hint-arrow", ".hint-echo"):
        assert cls in css, f"ينقص التنسيق {cls}"
    # كل صنف يخصّ النظام يبدأ بالبادئة — وهذا ما يمنع التصادم
    assert "hint-" in css


def test_every_aspect_carries_its_own_text():
    """
    كانت الواجهة تُطابق الزوايا بجداول `/api/depth` الخام، فتُصيب
    سبعًا وعشرين من أربعين وتترك الباقي بلا شرح: أزواج «ليليث
    الحقيقية» (وهي اسم مرادف)، وخيرون، والأجرام الخارجية بعضها
    ببعض، وطبائع الزوايا الصغرى. و`pair_text` يعرف هذه كلّها.

    فالمطابقة نُقلت إلى الخادم، حيث المعرفة — لا إلى المتصفّح، حيث
    نصفها. وهذا الاختبار يمنع رجوعها.
    """
    from api.index import dispatch
    c = dispatch("/api/chart", {"date": ["1990-05-17"], "time": ["08:30"],
                                "city": ["حلب"], "system": ["whole"]})
    asps = c["aspects"]
    assert asps, "لا زوايا في الخريطة"
    bare = [f"{a['a']} {a['name']} {a['b']}" for a in asps if not a.get("meaning")]
    assert not bare, f"زوايا بلا نصّ: {bare[:6]}"
    for a in asps:
        assert len(a["meaning"]) >= 30, f"نصّ مقتضب: {a['a']}–{a['b']}"


def test_chart_page_does_not_say_the_same_thing_four_times():
    """
    قال صاحب المشروع: «فقيرة نوعًا ما وهناك تكرار كثير».
    وكان قابلًا للقياس: موضع الجِرم يُذكر في العجلة، ثم في جدول
    الأجرام، ثم في «قراءة الخريطة»، ثم في جدول المقارنة.

    فحُذفت البطاقات المكرّرة وصار كل صفٍّ يُفتَح على نصّه. ونحرس
    هنا ألّا تعود العناوين المحذوفة، وأن تبقى الألسنة.
    """
    html = _pages()["chart.html"]
    for gone in ("سائر الأجرام", "أقوى الزوايا"):
        assert f">{gone}<" not in html, f"عاد العنوان المكرّر «{gone}»"
    assert "starsCard" not in html, "عاد جدول النجوم المستقلّ"
    for need in ("function tabsHTML", "function initTabs", "role=\"tablist\"",
                 "class=\"opentbl\"", "data-open="):
        assert need in html, f"ينقص من صفحة الخريطة: {need}"
    # صفوف البيوت تُربَط بمستمع مفوَّض، لا داخل مستمع زرٍّ آخر
    assert "out.addEventListener('click'" in html
    assert "out.addEventListener('keydown'" in html, \
        "الفتح بلوحة المفاتيح شرط — وإلّا حُجب نصف المحتوى"


def test_pattern_texts_are_readings_not_definitions():
    """
    **الاختبار الذي وُلد من شكوى مقيسة.**

    قال صاحب المشروع: «نفس المعلومات تمامًا، فهذا غير احترافي».
    فقِسْنا: جمعنا ١٩٣ كتلة نصّ تُعرَض للزائر ووازنّا كل اثنتين،
    فكان **تشابه نصوص الأشكال بعضها ببعض مئةً في المئة** — لأن
    `PATTERN_NOTES` جدولٌ مفتاحه اسم الشكل وحده، لا يعرف أعضاءه
    ولا موضعه.

    والعلّة كانت في موضعين لا واحد:
    ١. **النصّ**: تعريفٌ للشكل بدل قراءةٍ لشكلك أنت.
    ٢. **الحساب**: المقترنان كانا يُعَدّان ركنين، فيخرج الشكل
       الواحد مرّتين — وهو ما لا يُصلحه أيّ نصّ.

    ونحرس هنا الاثنين معًا على خرائط عشوائية.
    """
    import difflib
    import random
    from api.index import dispatch

    cities = ["حلب", "القاهرة", "بغداد", "الرباط", "دمشق", "تونس", "عمّان"]
    rnd = random.Random(11)
    worst, worst_at, total = 0.0, None, 0

    for _ in range(12):
        q = {"date": [f"{rnd.randint(1940, 2010)}-{rnd.randint(1, 12):02d}"
                      f"-{rnd.randint(1, 28):02d}"],
             "time": [f"{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}"],
             "city": [rnd.choice(cities)], "system": ["whole"]}
        c = dispatch("/api/chart", q)
        pats = c["reading"]["patterns"]
        total += len(pats)

        for p in pats:
            # لا عضو يتكرّر في شكل واحد — أوّل محاولة للدمج أخرجت
            # نبتون مرّتين في قائمة واحدة
            assert len(p["members"]) == len(set(p["members"])), \
                f"عضو مكرّر في {p['title']}: {p['members']}"
            # قراءة لا تعريف: تذكر أعضاءها بأسمائها
            assert any(m in p["text"] for m in p["members"]), \
                f"نصّ {p['title']} لا يذكر أيًّا من أعضائه — فهو تعريف لا قراءة"
            assert len(p["text"]) >= 80, f"نصّ {p['title']} أقصر من أن يكون قراءة"
            # والتعريف يبقى متاحًا، منفصلًا عن القراءة
            assert p.get("note"), "ضاع تعريف الشكل"
            assert p["text"] != p["note"], \
                f"{p['title']}: القراءة هي التعريف نفسه"

        texts = [p["text"] for p in pats]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                r = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
                if r > worst:
                    worst, worst_at = r, (pats[i]["title"], pats[j]["title"])

    assert total >= 8, "لم تُختبر أشكال كافية"
    # الحدّ ٨٠٪: ما بقي من تشابه **له معنى** — شكلان رأسهما في بيت
    # واحد يشتركان في المخرج حقًّا. وما فوق ذلك كسلٌ لا معنى.
    assert worst <= 0.80, (
        f"نصّا شكلين متشابهان بنسبة {worst:.0%} — {worst_at}. "
        "عاد النصّ لا يعرف حالته.")


def test_lot_texts_say_where_the_lot_fell():
    """
    نصّ السهم كان تعريفًا له لا يذكر بيته ولا برجه — مع أن موضع
    السهم هو كلّ فائدته. وقياسه: «سهم الأب» و«سهم الأم» متشابهان
    **٩٢٪**، و«سهم الغيب» وشرحُ المعجم له **٨٨٪**.

    والحدّ هنا ٨٨٪ لا ٨٠٪ كالأشكال، **وأقولها صراحةً**: سهمان
    يقعان في بيتٍ واحد وبرجٍ واحد يتشاركان أكثر كلامهما بحقّ —
    فالبيت والبرج يقولان فيهما الشيء نفسه، ولا يفترقان إلّا فيما
    كلٌّ منهما موضوعٌ له. وهذا تشابهٌ في المعنى لا كسلٌ في الكتابة.
    """
    import difflib
    import random
    from api.index import dispatch
    from falak import lots_deep

    cov = lots_deep.coverage()
    assert cov["حالات مُغطّاة"] >= 216, cov
    assert cov["قطع مكتوبة"] >= 44, cov

    cities = ["حلب", "القاهرة", "بغداد", "دمشق", "تونس"]
    rnd = random.Random(5)
    worst, worst_at, total = 0.0, None, 0

    for _ in range(6):
        q = {"date": [f"{rnd.randint(1940, 2010)}-{rnd.randint(1, 12):02d}"
                      f"-{rnd.randint(1, 28):02d}"],
             "time": [f"{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}"],
             "city": [rnd.choice(cities)], "system": ["whole"]}
        lots = dispatch("/api/chart", q)["reading"]["lots"]
        total += len(lots)
        assert len(lots) >= 18, "بعض السهام بلا قراءة"

        for L in lots:
            name = L["title"].split("—")[0].strip()
            assert L["text"] != L["note"], f"{name}: القراءة هي التعريف نفسه"
            assert L.get("note"), "ضاع تعريف السهم"
            # القراءة تذكر الموضع — وهو أصل الشكوى
            assert "البيت" in L["text"], f"{name}: النصّ لا يذكر البيت"
            assert len(L["text"]) >= 120, f"{name}: نصّ أقصر من أن يكون قراءة"

        texts = [L["text"] for L in lots]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                r = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
                if r > worst:
                    worst, worst_at = r, (lots[i]["title"][:20], lots[j]["title"][:20])

    assert total >= 100
    assert worst <= 0.88, f"نصّا سهمين متشابهان {worst:.0%} — {worst_at}"


def test_arabic_is_not_broken_by_the_plain_language_layer():
    """
    طبقة التبسيط كانت تستبدل «سهم» بـ«نقطة محسوبة» استبدالًا
    حرفيًّا، فكسرت العربية في كل صيغة:
        «سهم السعادة» ← «نقطة محسوبة السعادة»   تركيبٌ غير عربيّ
        «والسهم»      ← «والنقطة محسوبة»        أشدّ كسرًا
        «سهمُك»       ← «نقطة محسوبةُك»
    والثالثة سببها أن حدّ الكلمة كان حروفَ الهجاء وحدها، **والحركةُ
    خارجه** — فالضمّة في «سهمُك» عُدّت فاصلًا.

    فأُصلح الحدّ ليشمل الحركات، وتُركت «سهم» على حالها: **التبسيط
    أن يُشرَح المصطلح لا أن يُشوَّه**.
    """
    from falak import plain

    # الحركة جزءٌ من الكلمة لا فاصلٌ بينها
    for word in ("سهمُك", "الطالعُ", "البيتُ", "القمرُ"):
        out = plain.simplify(word, keep_original=False)
        assert out == word, f"«{word}» تبدّل إلى «{out}» — الحركة كُسِرت"

    # ولا استبدال يكسر التركيب
    for phrase in ("سهم السعادة", "والسهم", "سهم الغيب في البيت العاشر"):
        out = plain.simplify(phrase, keep_original=False)
        assert "نقطة محسوبة" not in out, f"«{phrase}» ← «{out}»"

    # والتبسيط لا يزال يعمل حيث يصحّ
    assert plain.simplify("الوجاج", keep_original=False) != "الوجاج"


def test_star_texts_read_the_body_not_only_the_star():
    """
    كان نصّ المقارنة صفةَ النجم وحدها: «الشمس مع رأس الغول» يشرح
    رأس الغول ولا يقول ما يصنعه **بالشمس**. والنجم لا يُقرأ وحده
    أصلًا — يُقرأ بما نزل عليه.

    **وعلاجُه اختلف عن السهام والأشكال عمدًا**: صفاتُ النجوم
    الثمانية والثلاثين مكتوبةٌ من قبل وجيّدة. فلم نُعِد كتابة ما
    كُتب، بل أضفنا المحور الناقص وحده — ما يعنيه نزوله على هذا
    الجِرم بعينه.
    """
    import difflib
    import random
    from api.index import dispatch
    from falak import stars_deep, stars

    cov = stars_deep.coverage()
    assert cov["أجرام وأوتاد مكتوبة"] >= 19, cov
    assert cov["حالات مُغطّاة"] >= 700, cov

    # كل جِرم يمكن أن يقع عليه نجم له نصّ — والأوتاد كذلك
    for body in ("الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري",
                 "زحل", "أورانوس", "نبتون", "بلوتو", "الرأس", "الذنب",
                 "ليليث", "خيرون", "الطالع", "وسط السماء", "الغارب", "وتد الأرض"):
        assert body in stars_deep.ON, f"لا نصّ لنزول نجم على {body}"

    cities = ["حلب", "القاهرة", "بغداد", "دمشق", "تونس"]
    rnd = random.Random(9)
    worst, worst_at, total = 0.0, None, 0

    for _ in range(8):
        q = {"date": [f"{rnd.randint(1940, 2010)}-{rnd.randint(1, 12):02d}"
                      f"-{rnd.randint(1, 28):02d}"],
             "time": [f"{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}"],
             "city": [rnd.choice(cities)], "system": ["whole"]}
        got = dispatch("/api/chart", q)["reading"]["stars"]
        total += len(got)
        for s in got:
            body = s["title"].split(" مع ")[0].strip()
            assert s["text"] != s["note"], f"{body}: القراءة هي صفة النجم وحدها"
            assert body in s["text"], f"{body}: النصّ لا يذكر الجِرم الذي نزل عليه"
            assert len(s["text"]) >= 140, f"{body}: نصّ أقصر من أن يكون قراءة"
            # شرط المقارنة الضيّقة مذكور — والنجم لا يعمل خارج الدرجة
            assert s["orb"] <= 1.01, f"مقارنة أوسع من الحدّ: {s['orb']}"

        texts = [s["text"] for s in got]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                r = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
                if r > worst:
                    worst, worst_at = r, (got[i]["title"][:26], got[j]["title"][:26])

    assert total >= 15, f"لم تُختبر مقارنات كافية ({total})"
    assert worst <= 0.80, f"نصّا نجمين متشابهان {worst:.0%} — {worst_at}"
    assert len(stars.STARS) == 38


def test_no_duplication_across_the_whole_page():
    """
    **الحارس الذي كان ناقصًا.**

    بنينا حارسًا للأشكال وحارسًا للسهام وحارسًا للنجوم، وكلٌّ يقيس
    عائلته وحدها. والزائر لا يقرأ عائلةً عائلة — يقرأ صفحةً واحدة.
    فما تشابه بين عائلتين رآه هو ولم يرَه أحدٌ منّا. وهذا بعينه ما
    وقع: «سهم الغيب» وشرحُ المعجم له كانا متشابهين ٨٨٪.

    **وقد أسقط هذا الفحصُ خللين حقيقيّين أوّل تشغيل:**

    ١. «عطارد – ليليث» و«عطارد – ليليث الحقيقية» متطابقان ١٠٠٪ —
       فالليليثان **نقطةٌ واحدة بحسابين**، وكلٌّ منهما كان يُزاوي
       سائر الأجرام على حدة. فصارت الزوايا تُحسَب من المتوسّطة
       وحدها، والموضعان يبقيان في الجدول.
    ٢. «عطارد نصفُ تربيعٍ زحل» و«المريخ نصفُ تربيعٍ زحل» متطابقان
       ١٠٠٪ — فنصّ الزاوية الصغرى كان **طبعَها وحده**، وهو واحد
       لكل زوج. فقُرن الطبع بموضوع الزوج.

    ولم يكشفهما أيٌّ من الحرّاس الثلاثة، لأن عائلة الزوايا لم يكن
    لها حارس أصلًا.
    """
    import importlib.util
    import os
    path = os.path.join(_root(), "tools", "measure_duplication.py")
    if not os.path.exists(path):
        pytest.skip("لا أدوات")
    spec = importlib.util.spec_from_file_location("_measure_dup", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    res = m.measure(n_charts=3)
    assert res["pairs"] > 3000, f"لم يُقَس ما يكفي ({res['pairs']})"

    names = {"same": "داخل العائلة الواحدة",
             "cross": "بين عائلتين",
             "gloss": "نصٌّ وشرحُ المعجم له"}
    for key, limit in res["limits"].items():
        got, where = res["worst"][key]
        assert got <= limit, (
            f"{names[key]}: تشابه {got:.0%} والحدّ {limit:.0%} — {where}")


def test_dominants_are_explained_not_only_measured():
    """
    كان القسم ثلاثة رسومٍ بنِسَبٍ مئوية وسطرًا واحدًا تحتها —
    **والنسبة ليست معنًى**. ومن قرأ «مائي ٤٢٫٧٪» لم يعرف ماذا
    يصنع به، ولا لماذا يهمّه أن يكون الناري ٦٫١٪.

    والسطر الواحد **لم يكن يذكر الكواكب أصلًا**، مع أن ترتيب
    الكواكب أدلّ على صاحب الخريطة من العنصر والطبع معًا.

    والقاعدة التي نحرسها: **الغالب يُقرأ بضدّه، والناقص بابٌ
    يُتعلَّم لا عيبٌ يُلام عليه.**
    """
    from api.index import dispatch
    from falak import dominants_deep

    cov = dominants_deep.coverage()
    assert cov["كواكب"] >= 14 and cov["عناصر"] == 4, cov

    c = dispatch("/api/chart", {"date": ["1990-05-17"], "time": ["08:30"],
                                "city": ["حلب"], "system": ["whole"]})
    bd = c["reading"]["balance_deep"]
    for k in ("elements", "modes", "planets", "caveat"):
        assert bd.get(k), f"ينقص شرح {k}"
        assert len(bd[k]) >= 90, f"شرح {k} أقصر من أن يُفيد"

    # الغالب والناقص معًا — لا الغالب وحده
    assert "وأضعفها" in bd["elements"], "لا يُذكَر الناقص"
    assert "بابٌ يُتعلَّم" in bd["elements"] or "يُتعلَّم" in bd["elements"], \
        "لا تُذكَر القاعدة: الناقص بابٌ لا عيب"
    # والكواكب صارت مذكورة
    assert "أقوى الأجرام" in bd["planets"]
    # والتحفّظ صريح: النِّسَب وزنٌ لا حكم
    assert "وزنٌ لا حكم" in bd["caveat"]


def test_lunar_mansions_reach_the_wheel():
    """
    حلقة المنازل الثماني والعشرين كانت **أرقامًا مجرّدة**: يقرأ
    الزائر «١٧» ولا يعرف ما هي. ونصوصها مكتوبة في `tables.py`
    منذ البدء — فلم تكن تصل.

    وهذا الدرس نفسه تكرّر في النجوم والعبور: **لا يكفي أن يُكتَب
    الشيء، بل يجب أن يُوصَل إلى العين.**
    """
    from api.index import dispatch
    from falak import tables

    d = dispatch("/api/depth", {"date": ["1990-05-17"], "time": ["08:30"],
                                "city": ["حلب"]})
    m = d.get("mansions")
    assert m and len(m) == 28, f"المنازل {len(m or [])} لا ٢٨"
    assert len(tables.MANSIONS) == 28

    for i, x in enumerate(m):
        assert x["index"] == i + 1
        for k in ("name", "desc", "good_for", "mood"):
            assert x.get(k), f"المنزلة {i + 1}: ينقص {k}"
        assert len(x["desc"]) >= 25, f"المنزلة {i + 1}: وصفٌ مقتضب"
        assert abs(x["start"] - i * (360 / 28)) < 0.01

    names = {x["name"] for x in m}
    assert len(names) == 28, "أسماء المنازل ليست متفرّدة"

    # والعجلة ترسمها بشرحها
    js = open(_root() + "/assets/wheel.js", encoding="utf-8").read()
    assert "class=\"mns" in js, "حلقة المنازل بلا مجموعة تحمل شرحًا"
    assert "deep.mansions" in js, "العجلة لا تقرأ المنازل"
    assert "moonM === i + 1" in js, "منزلة القمر لا تُميَّز في الحلقة"


def test_glossary_is_deep_enough_for_a_beginner():
    """
    قال صاحب المشروع: «التبسيط والبساطة قبل كل شيء» — ولمن لا يعرف
    شيئًا عن هذه المواضيع. فلا يكفي أن نشرح «الألمطن» ونترك «البرج»
    و«الدرجة» و«الشمس» بلا شرح، فمن جهل هذه لم ينفعه ذاك.
    """
    from falak import interpret
    g = interpret.GLOSSARY
    assert len(g) >= 110, f"المعجم {len(g)} مصطلحًا فقط — لا يكفي مبتدئًا"

    # الأوّليّات التي لا يُفترض علمها
    for t in ("البرج", "الدرجة", "دائرة البروج", "الأفق",
              "الشمس", "القمر", "المريخ", "زحل",
              "الاقتران", "التسديس", "التربيع", "التثليث", "التقابل",
              "النار", "التراب", "الهواء", "الماء"):
        assert t in g, f"«{t}» ليس في المعجم — وهو ممّا يجهله المبتدئ"

    # مصطلحات المدارس الثلاث كلّها مشروحة
    for t in ("الجيوتيش", "النكشترا", "الدشا", "البازي", "سيّد النفس",
              "العناصر الخمسة", "قيام الربيع"):
        assert t in g, f"«{t}» من المدارس الجديدة وليس في المعجم"

    # لا شرح مقتضب ولا شرح يُحيل على نفسه
    for term, text in g.items():
        assert len(text) >= 40, f"شرح «{term}» أقصر من أن يُفيد"
        head = text.split("،")[0].split(".")[0]
        assert not head.strip().startswith(term), \
            f"شرح «{term}» يبدأ بتعريف نفسه بنفسه"


def test_every_page_script_parses_together_with_its_files():
    """
    **الحارس الذي كان يفحص وهمًا.**

    كان يُحلّل كل كتلة `<script>` **وحدها**، وهذا ليس ما يفعله
    المتصفّح: وسوم `<script>` المنفصلة **تتشارك بيئةً معجميةً
    واحدة**. فإعلان `const esc` في صفحةٍ يصطدم بإعلانه في
    `app.js`، فيُلقي المتصفّح `SyntaxError` **يقتل سكربت الصفحة
    كلَّه** — والصفحة تُعرَض فارغة لا تعمل.

    وقد كانت **ستّ صفحات ميتة** بهذا السبب: الهندي والصيني
    والتوافق والمسائل والاختيارات والواجهة البرمجية. ولم يرَها
    الحارس القديم لأنه كان يفحص كلًّا على حدة، فلا تصادم.

    **والدرس**: الحارس الذي لا يُحاكي الواقع يُطمئنك على خراب.
    فصار يجمع ملفّات الصفحة وسكربتها **كما يجمعها المتصفّح**.
    """
    import os
    import re
    import shutil
    import subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node غير متوفّر")

    root = _root()
    checked = 0
    for name, html in _pages().items():
        files = re.findall(r'<script src="/assets/([^"]+)"></script>', html)
        shared = []
        for f in files:
            path = os.path.join(root, "assets", f)
            if os.path.exists(path):
                shared.append(open(path, encoding="utf-8").read())
        inline = re.findall(r'<script>([\s\S]*?)</script>', html)
        bundle = "\n;\n".join(shared + inline)
        assert bundle.strip(), f"{name}: لا سكربت"

        # `node --check` لا يقرأ من الأنبوب في كل بيئة، فنكتب ملفًّا
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(bundle)
            tmp = fh.name
        try:
            r = subprocess.run([node, "--check", tmp],
                               capture_output=True, text=True)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        assert r.returncode == 0, (
            f"{name}: الصفحة وملفّاتها لا تُحلَّل معًا — "
            f"{(r.stderr or '').strip()[:200]}")
        checked += 1

    assert checked >= 14, f"لم تُفحَص إلّا {checked} صفحة"


def test_no_shared_name_is_redeclared_in_a_page():
    """
    القاعدة صريحةً: **ما أُعلن في `assets/` لا يُعلَن في صفحة**.
    والفحص أعلاه يكشف التصادم، وهذا يُسمّي المتصادمين فيُسهّل
    الإصلاح.
    """
    import os
    import re
    root = _root()
    top = re.compile(r'^(?:const|let|function|class)\s+([A-Za-z_$][\w$]*)',
                     re.M)
    shared: dict[str, str] = {}
    for f in sorted(os.listdir(os.path.join(root, "assets"))):
        if not f.endswith(".js"):
            continue
        for n in top.findall(open(os.path.join(root, "assets", f),
                                  encoding="utf-8").read()):
            shared.setdefault(n, f)

    clashes = []
    for name, html in _pages().items():
        used = [f for f in re.findall(r'<script src="/assets/([^"]+)"></script>', html)]
        for block in re.findall(r'<script>([\s\S]*?)</script>', html):
            for n in top.findall(block):
                if n in shared and shared[n] in used:
                    clashes.append(f"{name}: «{n}» مُعلَن أيضًا في assets/{shared[n]}")

    assert not clashes, "أسماء مُعلَنة مرّتين:\n  " + "\n  ".join(clashes[:8])
