# -*- coding: utf-8 -*-
"""
الجيوتِش — التنجيم الهندي، بالمنطقة النجمية.

**أوّل ما يجب أن يعرفه القارئ**: هذه المدرسة تقرأ السماء على
**المنطقة النجمية** لا الاستوائية. والفرق بينهما اليوم نحو **٢٤ درجة**
— أي إنّ من شمسه في الأسد عند العرب والغربيّين هي في السرطان عند
الهنود في أكثر الحالات.

وليس أحدهما خطأً: الاستوائية تقيس من الاعتدال الربيعي، والنجمية تقيس
من النجوم الثابتة. والاعتدال يتقهقر بين النجوم درجةً كل ٧٢ سنة، فتباعد
المقياسان مع القرون. فالسؤال ليس «أيّهما صحيح» بل «أيّهما تقيس به».

**والوصل الذي يخصّنا نحن**: منازل القمر الثماني والعشرون في تراث
العرب، والنكشترا السبع والعشرون عند الهنود، **نجومهما واحدة**. كريتِّكا
هي الثريّا، وروهيني هي الدبران، وتشيترا هي السماك الأعزل، وجيِشتها هي
قلب العقرب. مدرستان نظرتا إلى السماء نفسها وسمّتا نجومها بلغتيهما —
ونحن نعرض الاسمين معًا، وهذا ما لا يفعله موقع هندي ولا غربي.

**ودقيقتان كشفهما التحقّق الخارجي، نُسجّلهما لأنهما تُفاجئان:**

١. **النجمي ليس الاستوائيَّ ناقص الأينامشا بالضبط.** بينهما فرق يبلغ
   نحو ١٤ ثانية قوسية، سببه **اهتزاز محور الأرض** (النوتيشن): الموضع
   الاستوائي الظاهري يحمله، والأينامشا تُقاس من الاعتدال المتوسّط لا
   الظاهري. فالمعادلة الصحيحة: النجمي = الاستوائي **بلا اهتزاز** ناقص
   الأينامشا — وقد تحقّقنا منها إلى الصفر تمامًا.

٢. **نجم المنزلة ليس دائمًا داخل حدودها.** المنازل كانت في الأصل
   مبنيّة على النجوم، وامتداداتها غير متساوية، ثم نُظّمت إلى أقسام
   متساوية من ١٣° ٢٠′ لتنضبط الحسابات. فبقيت الأسماء منسوبة إلى
   نجومها، وخرج بعض النجوم من أقسامها: السماك الرامح — نجم سْواتي —
   خارج سْواتي بستّ درجات، وقلب العقرب خارج جيِشتها بثلاثة أرباع
   درجة. وليس هذا خطأ حساب: هو أثرُ تسوية قسمةٍ كانت غير مستوية.
   ونعرض الفارق للقارئ بدل أن نكتمه (انظر YOGATARA).

المصادر: «بريهات باراشارا هورا شاسترا»، و«بريهات جاتاكا» لڤاراها ميهيرا،
وأينامشا لاهيري الرسمية في الهند.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import swisseph as swe

from . import chart as ch, ephem

UTC = timezone.utc

# ══════════════════════════════════════════════════════════════
# ١ — الأينامشا: الفرق بين المقياسين
# ══════════════════════════════════════════════════════════════
AYANAMSHAS = {
    "lahiri": {"mode": swe.SIDM_LAHIRI, "name": "لاهيري",
               "note": ("الرسمية في الهند، وعليها عمل أكثر الكتب "
                        "والبرامج. نقطة الصفر فيها نحو سنة ٢٨٥ ميلادية.")},
    "krishnamurti": {"mode": swe.SIDM_KRISHNAMURTI, "name": "كرشنامورتي",
                     "note": ("مذهب KP، وعليه عمل مدرسة كاملة في "
                              "جنوب الهند. يفرق عن لاهيري بنحو ٦ دقائق.")},
    "raman": {"mode": swe.SIDM_RAMAN, "name": "راما",
              "note": ("مذهب ب. ف. راما، يفرق عن لاهيري بنحو "
                       "درجة وأربع دقائق.")},
    "fagan": {"mode": swe.SIDM_FAGAN_BRADLEY, "name": "فاغان–برادلي",
              "note": ("مذهب الغربيّين الذين اختاروا المنطقة النجمية. "
                       "الأوسع من لاهيري بنحو نصف درجة.")},
}
DEFAULT_AYANAMSHA = "lahiri"

SIGNS_SA = ["ميشا", "ڤريشابها", "ميثونا", "كَركا", "سيمها", "كَنيا",
            "تولا", "ڤريشتشيكا", "دهانو", "مَكَرا", "كومبها", "ميناTemp"]
SIGNS_SA[11] = "مينا"

# ══════════════════════════════════════════════════════════════
# ٢ — النكشترا السبع والعشرون
#     (الاسم · ربّها · المنزلة العربية المقابلة · نجمها)
# ══════════════════════════════════════════════════════════════
NAKSHATRAS = [
    ("أشْويني", "الذنب", "الشرطان", "الحمل β"),
    ("بَهَرَني", "الزهرة", "البُطَين", "الحمل 41"),
    ("كريتِّكا", "الشمس", "الثريّا", "الثريّا — Pleiades"),
    ("روهيني", "القمر", "الدَّبَران", "الدبران — Aldebaran"),
    ("مريغَشيرشا", "المريخ", "الهَقعة", "الجوزاء λ"),
    ("أردرا", "الرأس", "الهَنعة", "منكب الجوزاء — Betelgeuse"),
    ("بونَرڤَسو", "المشتري", "الذراع", "التوأمان — Pollux"),
    ("بوشْيا", "زحل", "النَّثرة", "السرطان — Praesepe"),
    ("أشليشا", "عطارد", "الطَّرْف", "الشجاع ε"),
    ("مَغَها", "الذنب", "الجَبهة", "قلب الأسد — Regulus"),
    ("بورڤا فَلغوني", "الزهرة", "الزُّبْرة", "الأسد δ"),
    ("أُتَّرا فَلغوني", "الشمس", "الصَّرْفة", "الصرفة — Denebola"),
    ("هَستا", "القمر", "العَوّاء", "الغراب"),
    ("تشيترا", "المريخ", "السِّماك", "السماك الأعزل — Spica"),
    ("سْواتي", "الرأس", "الغَفْر", "السماك الرامح — Arcturus"),
    ("ڤيشاكها", "المشتري", "الزُّبانى", "الميزان α و β"),
    ("أنورادها", "زحل", "الإكليل", "العقرب δ"),
    ("جيِشتها", "عطارد", "القَلْب", "قلب العقرب — Antares"),
    ("مولا", "الذنب", "الشَّوْلة", "شولة العقرب"),
    ("بورڤا أشادها", "الزهرة", "النَّعائم", "القوس δ و ε"),
    ("أُتَّرا أشادها", "الشمس", "البَلْدة", "القوس ζ و σ"),
    ("شرَڤَنا", "القمر", "سعد الذابح", "النسر الطائر — Altair"),
    ("دَهَنِشْتا", "المريخ", "سعد بُلَع", "الدلفين"),
    ("شَتَبهيشا", "الرأس", "سعد السعود", "الدلو γ"),
    ("بورڤا بهادرَبَدا", "المشتري", "سعد الأخبية", "الفرس الأعظم α"),
    ("أُتَّرا بهادرَبَدا", "زحل", "الفَرْغ المؤخَّر", "الفرس الأعظم γ"),
    ("ريڤَتي", "عطارد", "بطن الحوت", "الحوت ζ"),
]
NAK_ARC = 360.0 / 27.0            # ١٣° ٢٠′
PADA_ARC = NAK_ARC / 4.0          # ٣° ٢٠′

# «يوغاتارا»: النجم الذي سُمّيت به المنزلة، باسمه في مكتبة النجوم.
# نعرضه ونعرض معه أيقع داخل حدودها المتساوية أم خارجها — انظر
# الدقيقة الثانية في صدر الملفّ.
YOGATARA = {
    3: "Alcyone", 4: "Aldebaran", 6: "Betelgeuse", 10: "Regulus",
    12: "Denebola", 14: "Spica", 15: "Arcturus", 18: "Antares",
    22: "Altair", 27: "Revati",
}


def yogatara(index: int, when: datetime,
             ayan: str = "lahiri") -> dict | None:
    """موضع نجم المنزلة، وأداخل حدودها هو أم خارجها."""
    star = YOGATARA.get(index)
    if not star:
        return None
    _sid(ayan)
    try:
        L = swe.fixstar_ut(star, ephem.to_jd(when),
                           swe.FLG_SWIEPH | swe.FLG_SIDEREAL)[0][0] % 360.0
    except Exception:
        return None
    lo, hi = (index - 1) * NAK_ARC, index * NAK_ARC
    inside = lo <= L < hi
    off = 0.0 if inside else min(abs(L - lo), abs(L - hi), abs(L - lo + 360),
                                 abs(L - hi - 360))
    return {
        "star": star, "lon": round(L, 4), "inside": inside,
        "offset": round(off, 3),
        "note": ("النجم داخل حدود منزلته." if inside else
                 f"النجم خارج حدود منزلته بـ{off:.2f}°. وليس هذا خطأ "
                 "حساب: المنازل كانت غير متساوية في الأصل ثم سُوّيت، "
                 "فبقي الاسم على نجمه وخرج النجم من القسمة."),
    }

# ══════════════════════════════════════════════════════════════
# ٣ — الأجرام التسعة (نَڤَغْرَها)
# ══════════════════════════════════════════════════════════════
GRAHAS = [
    ("الشمس", "سوريا", swe.SUN),
    ("القمر", "تشاندرا", swe.MOON),
    ("المريخ", "مَنغَلا", swe.MARS),
    ("عطارد", "بودها", swe.MERCURY),
    ("المشتري", "غورو", swe.JUPITER),
    ("الزهرة", "شوكرا", swe.VENUS),
    ("زحل", "شَني", swe.SATURN),
    ("الرأس", "راهو", swe.TRUE_NODE),
    ("الذنب", "كيتو", None),          # مقابل الرأس تمامًا
]

# الكرامات الهندية
OWN = {
    "الشمس": ["الأسد"], "القمر": ["السرطان"],
    "المريخ": ["الحمل", "العقرب"], "عطارد": ["الجوزاء", "العذراء"],
    "المشتري": ["القوس", "الحوت"], "الزهرة": ["الثور", "الميزان"],
    "زحل": ["الجدي", "الدلو"],
}
EXALT = {                              # (البرج، درجة الذروة)
    "الشمس": ("الحمل", 10), "القمر": ("الثور", 3),
    "المريخ": ("الجدي", 28), "عطارد": ("العذراء", 15),
    "المشتري": ("السرطان", 5), "الزهرة": ("الحوت", 27),
    "زحل": ("الميزان", 20), "الرأس": ("الجوزاء", 20),
    "الذنب": ("القوس", 20),
}
MOOLA = {                              # المثلّث الأصلي: (البرج، من، إلى)
    "الشمس": ("الأسد", 0, 20), "القمر": ("الثور", 4, 30),
    "المريخ": ("الحمل", 0, 12), "عطارد": ("العذراء", 16, 20),
    "المشتري": ("القوس", 0, 10), "الزهرة": ("الميزان", 0, 15),
    "زحل": ("الدلو", 0, 20),
}
_OPP = {s: ch.SIGNS[(i + 6) % 12] for i, s in enumerate(ch.SIGNS)}
DEBIL = {p: (_OPP[s], d) for p, (s, d) in EXALT.items()}

BENEFIC = {"المشتري", "الزهرة"}
MALEFIC = {"زحل", "المريخ", "الرأس", "الذنب"}


def _sid(mode_key: str):
    swe.set_sid_mode(AYANAMSHAS[mode_key]["mode"], 0, 0)


def ayanamsha(when: datetime, mode_key: str = DEFAULT_AYANAMSHA) -> float:
    _sid(mode_key)
    return swe.get_ayanamsa_ut(ephem.to_jd(when))


def nakshatra_of(lon: float) -> dict:
    """المنزلة النجمية وربعها — وربّها هو مفتاح الدشا كلّها."""
    i = int(lon // NAK_ARC) % 27
    name, lord, arabic, star = NAKSHATRAS[i]
    within = lon - i * NAK_ARC
    pada = int(within // PADA_ARC) + 1
    return {
        "index": i + 1, "name": name, "lord": lord,
        "arabic_mansion": arabic, "star": star,
        "pada": pada,
        "degree_in": round(within, 4),
        "fraction_left": round(1 - within / NAK_ARC, 6),
        "text": f"{name} — الربع {pada}",
    }


def dignity_of(planet: str, sign: str, deg: float) -> dict:
    """الكرامة الهندية: الذروة والهبوط والمثلّث الأصلي والبيت."""
    ex = EXALT.get(planet)
    de = DEBIL.get(planet)
    mt = MOOLA.get(planet)
    if ex and sign == ex[0]:
        exact = abs(deg - ex[1]) < 1.0
        return {"kind": "الذروة", "score": 5,
                "note": (f"في ذروته ({sign})" +
                         (" وعلى درجتها بالضبط — أقوى ما يكون."
                          if exact else "، وهو أقوى مواضعه."))}
    if de and sign == de[0]:
        return {"kind": "الهبوط", "score": -5,
                "note": f"في هبوطه ({sign}) — أضعف مواضعه، ويحتاج من يُعينه."}
    if mt and sign == mt[0] and mt[1] <= deg < mt[2]:
        return {"kind": "المثلّث الأصلي", "score": 4,
                "note": "في مثلّثه الأصلي — قويّ نافذ."}
    if sign in OWN.get(planet, []):
        return {"kind": "بيته", "score": 3,
                "note": "في بيته — يتصرّف بحرّية."}
    return {"kind": "—", "score": 0, "note": "لا كرامة خاصّة له هنا."}


# ══════════════════════════════════════════════════════════════
# ٤ — نافامْشا (D9) وسائر الفرغا
# ══════════════════════════════════════════════════════════════
def varga(lon: float, n: int) -> str:
    """
    برج الجرم في الخريطة المقسَّمة رقم n.

    وأشهرها D9 «نافامْشا»، وهي عند الهنود **الخريطة الثانية لا
    الزينة**: تُقرأ مع الأولى دائمًا، ويُقال إنّ ما وعدت به الأولى
    تُثبته الثانية أو تنقضه.
    """
    return ch.SIGNS[int(lon * n / 30.0) % 12]


VARGAS = {1: "راشي — الخريطة الأمّ", 9: "نافامْشا — الزواج والثمرة",
          10: "دَشامْشا — العمل والمرتبة", 7: "سَبتامْشا — الولد",
          12: "دْوادَشامْشا — الأبوان", 3: "دريكانا — الإخوة",
          4: "تشَتورتامْشا — الدار", 2: "هورا — المال"}


# ══════════════════════════════════════════════════════════════
# ٥ — الخريطة
# ══════════════════════════════════════════════════════════════
def compute(when_local: datetime, lat: float, lon: float,
            ayan: str = DEFAULT_AYANAMSHA, tzname: str = "",
            vargas: list[int] | None = None) -> dict:
    if when_local.tzinfo is None:
        raise ValueError("الوقت يجب أن يحمل منطقته الزمنية")
    if ayan not in AYANAMSHAS:
        raise ValueError(f"مذهب أينامشا غير معروف: {ayan}")

    when_utc = when_local.astimezone(UTC)
    jd = ephem.to_jd(when_utc)
    _sid(ayan)
    ayan_val = swe.get_ayanamsa_ut(jd)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    # الطالع النجمي (لَغْنا) وبيوت الإشارة الكاملة
    cusps_trop, ascmc = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
    lagna = ascmc[0] % 360.0
    lagna_sign_i = int(lagna // 30)

    bodies = []
    rahu_lon = None
    for name, sa, code in GRAHAS:
        if code is None:
            L = (rahu_lon + 180.0) % 360.0
            speed = -0.053
        else:
            x = swe.calc_ut(jd, code, flags)[0]
            L, speed = x[0] % 360.0, x[3]
            if name == "الرأس":
                rahu_lon = L
        si = int(L // 30)
        sign = ch.SIGNS[si]
        deg = L % 30.0
        house = ((si - lagna_sign_i) % 12) + 1
        dig = dignity_of(name, sign, deg)
        bodies.append({
            "name": name, "sanskrit": sa, "lon": round(L, 6),
            "speed": round(speed, 6), "retro": speed < 0,
            "sign": sign, "sign_sanskrit": SIGNS_SA[si],
            "house": house, **ch.dms(L),
            "nakshatra": nakshatra_of(L),
            "dignity": dig,
            "nature": ("سعد" if name in BENEFIC else
                       "نحس" if name in MALEFIC else "متغيّر"),
            "navamsa": varga(L, 9),
        })

    want = vargas or [9, 10]
    varga_tables = {}
    for n in want:
        if n in VARGAS:
            varga_tables[str(n)] = {
                "name": VARGAS[n],
                "lagna": varga(lagna, n),
                "bodies": {b["name"]: varga(b["lon"], n) for b in bodies},
            }

    moon = next(b for b in bodies if b["name"] == "القمر")
    return {
        "when_local": when_local.isoformat(),
        "when_utc": when_utc.isoformat(),
        "tz": tzname or str(when_local.tzinfo),
        "lat": lat, "lon": lon,
        "ayanamsha": {"key": ayan, "name": AYANAMSHAS[ayan]["name"],
                      "value": round(ayan_val, 6),
                      "text": ch.dms(ayan_val)["short"],
                      "note": AYANAMSHAS[ayan]["note"]},
        "lagna": {"lon": round(lagna, 6), "sign": ch.SIGNS[lagna_sign_i],
                  "sign_sanskrit": SIGNS_SA[lagna_sign_i],
                  **ch.dms(lagna),
                  "nakshatra": nakshatra_of(lagna)},
        "bodies": bodies,
        "houses": [{"house": i + 1,
                    "sign": ch.SIGNS[(lagna_sign_i + i) % 12],
                    "sign_sanskrit": SIGNS_SA[(lagna_sign_i + i) % 12]}
                   for i in range(12)],
        "house_system": ("الإشارة الكاملة (راشي) — كل برج بيت كامل، "
                         "وهو الغالب في الجيوتِش وأصله فيه لا في الغرب."),
        "moon_nakshatra": moon["nakshatra"],
        "vargas": varga_tables,
    }


# ══════════════════════════════════════════════════════════════
# ٦ — الدشا: فِمْشوتَّري
#
# دورة مئة وعشرين سنة، تبدأ من **موضع القمر في نكشترته** لا من
# الشمس ولا من الطالع. فمن وُلد والقمر في أوّل منزلته بدأت فترته
# كاملة، ومن وُلد وقد قطعها بدأ بما بقي منها.
#
# والسنة هنا سنة شمسية متوسّطة (٣٦٥.٢٥ يومًا) على مذهب الأكثرين.
# ══════════════════════════════════════════════════════════════
DASHA_ORDER = ["الذنب", "الزهرة", "الشمس", "القمر", "المريخ",
               "الرأس", "المشتري", "زحل", "عطارد"]
DASHA_YEARS = {"الذنب": 7, "الزهرة": 20, "الشمس": 6, "القمر": 10,
               "المريخ": 7, "الرأس": 18, "المشتري": 16, "زحل": 19,
               "عطارد": 17}
YEAR_DAYS = 365.25


def vimshottari(birth_utc: datetime, moon_lon: float,
                until: datetime | None = None, levels: int = 2) -> dict:
    """
    فترات العمر ومواعيدها. levels=1 الكبرى وحدها، و2 معها الصغرى.
    """
    assert sum(DASHA_YEARS.values()) == 120, "دورة فمشوتّري مئة وعشرون سنة"
    nak = nakshatra_of(moon_lon)
    lord = nak["lord"]
    i0 = DASHA_ORDER.index(lord)
    left = nak["fraction_left"]                 # ما بقي من المنزلة

    until = until or (birth_utc + timedelta(days=YEAR_DAYS * 120))
    out, t = [], birth_utc
    for k in range(9 + 3):                      # دورة وزيادة
        p = DASHA_ORDER[(i0 + k) % 9]
        years = DASHA_YEARS[p] * (left if k == 0 else 1.0)
        end = t + timedelta(days=years * YEAR_DAYS)
        entry = {
            "planet": p, "years": round(years, 4),
            "start": t.isoformat(), "end": end.isoformat(),
            "start_year": t.year, "end_year": end.year,
            "partial": k == 0 and left < 0.999,
        }
        if levels >= 2:
            entry["sub"] = _antardasha(p, t, years)
        out.append(entry)
        t = end
        if t > until:
            break
    return {
        "moon_nakshatra": nak,
        "start_lord": lord,
        "balance_note": (
            f"وُلدت والقمر في {nak['name']}، وربّها {lord}. "
            f"وقد بقي من المنزلة {left * 100:.1f}٪، فبدأت الحياة "
            f"بما بقي من فترة {lord} لا بها كاملة."
        ),
        "periods": out,
    }


def _antardasha(major: str, start: datetime, major_years: float) -> list:
    """الفترات الصغرى داخل الكبرى، على نسبة سني كل ربّ من المئة والعشرين."""
    i0 = DASHA_ORDER.index(major)
    out, t = [], start
    for k in range(9):
        p = DASHA_ORDER[(i0 + k) % 9]
        yrs = major_years * DASHA_YEARS[p] / 120.0
        end = t + timedelta(days=yrs * YEAR_DAYS)
        out.append({"planet": p, "years": round(yrs, 4),
                    "start": t.isoformat(), "end": end.isoformat()})
        t = end
    return out


def current_dasha(dasha: dict, at: datetime) -> dict:
    """أيّ فترة يعيشها صاحب الخريطة الآن — الكبرى والصغرى."""
    for p in dasha["periods"]:
        if p["start"] <= at.isoformat() <= p["end"]:
            sub = None
            for s in p.get("sub") or []:
                if s["start"] <= at.isoformat() <= s["end"]:
                    sub = s
                    break
            return {"major": p, "minor": sub}
    return {"major": None, "minor": None}
