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
from datetime import date, datetime, timezone
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
    assert len(seen) == 84


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
    assert sum(len(v) for v in d["planet_in_house"].values()) == 84
