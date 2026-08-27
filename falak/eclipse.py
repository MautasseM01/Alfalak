# -*- coding: utf-8 -*-
"""
الكسوف والخسوف — حسابًا وعقدةً وسلسلةَ ساروس.

──────────────────────────────────────────────────────────────────
**لماذا وحدةٌ جديدة و`mundane.eclipses` موجودة؟**

تلك تُخرج حدثًا في النشرة: «كسوف شمسي كلّي في برج الحمل». وهذا
يكفي للنشرة ولا يكفي لصفحةٍ يُدرَس فيها الكسوف نفسه، إذ تُسأل
عن:

  · **العقدة**: أيّهما، الرأس أم الذنب؟ وكم بينها وبين الشمس؟
    فمن هنا يُعلَم **لِمَ وقع الكسوف** لا أنّه وقع.
  · **ساروس**: أيُّ سلسلة، وأيُّ عضوٍ منها؟ وأين نظيرُه قبل
    ثمانيَ عشرةَ سنةً وبعدها؟
  · **المقدار**: كم غُطّي من القرص، وكم من مساحته؟
  · **الموضع**: أين يُرى تامًّا على الأرض، وكيف يُرى من مدينتك؟

وهذه أربعةٌ لا تُشتَقّ من تلك، فبُنيت هنا.

──────────────────────────────────────────────────────────────────
**وساروس تأتي من المكتبة، لا من صيغةٍ نخترعها**

لسلسلة ساروس ترقيمٌ اصطلاحيّ (فان دن بيرغ)، ولو حسبتُه بصيغةٍ
من عندي لخالف الجداولَ المنشورة في بعض الحدود. و`swisseph` تردّه
في `attr[9]` والعضوَ في `attr[10]`.

وقد قُوبل: كسوف ٨ نيسان ٢٠٢٤ ← سلسلة ١٣٩ العضو ٣٠، وهو نصُّ
ما عند ناسا. **فالرقم منقولٌ لا مُستنبَط.**

──────────────────────────────────────────────────────────────────
**والدورة تُثبَت بالبحث لا بالجمع**

`saros_chain` لا تكتفي بأن تزيد ٦٥٨٥٫٣٢ يومًا وتقول «ها هو».
بل تزيدُها **ثم تبحث عن كسوفٍ حقيقيّ هناك**، وتردّ الفارق بين
المتوقَّع والواقع. فإن كان الفارق ساعاتٍ فالدورة صادقة، وإن
لم يوجد كسوفٌ فلا دورة — **والزائر يرى الفحص لا الدعوى**.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import swisseph as swe

from .ephem import FLAGS, SIGNS, UTC, lon_of, to_jd

# ── دورة ساروس: ٦٥٨٥ يومًا و٧ ساعات و٤٣ دقيقة تقريبًا ──────────
# وهي ثمانيَ عشرةَ سنةً وأحدَ عشرَ يومًا وثُلثَ يوم. والثُّلثُ هو
# سببُ انتقال موضع الرؤية غربًا نحو ١٢٠° في كل دورة — فالنظيرُ
# يقع في الوقت نفسه من دورة الأرض لا في المكان نفسه.
SAROS_DAYS = 6585.3211

KIND_SOL = [
    (swe.ECL_TOTAL, "كلّي"),
    (swe.ECL_ANNULAR_TOTAL, "هجين"),
    (swe.ECL_ANNULAR, "حلقي"),
    (swe.ECL_PARTIAL, "جزئي"),
]
KIND_LUN = [
    (swe.ECL_TOTAL, "كلّي"),
    (swe.ECL_PARTIAL, "جزئي"),
    (swe.ECL_PENUMBRAL, "شبه ظلّي"),
]

KIND_NOTE = {
    "كلّي": "يُغطّى القرص كلُّه.",
    "حلقي": "يبقى من القرص حلقةٌ مضيئة، لأنّ القمر في أبعد مسافته فيقصر عن تغطيته.",
    "هجين": "يُرى كلّيًّا من بعض الأرض وحلقيًّا من بعضها، لتقوّس الأرض.",
    "جزئي": "يُغطّى بعض القرص.",
    "شبه ظلّي": "يمرّ القمر في شبه الظلّ فيخفت ضوءه ولا يُقتطع منه شيء.",
}


def _sign(lon: float) -> str:
    return SIGNS[int(lon % 360.0 // 30)]


def _dms(lon: float) -> str:
    d = lon % 30.0
    return f"{int(d)}° {int((d - int(d)) * 60):02d}′ {_sign(lon)}"


def _from_jd(jd: float) -> datetime:
    y, m, d, ut = swe.revjul(jd, swe.GREG_CAL)
    h = int(ut)
    mi = int((ut - h) * 60)
    s = int(round(((ut - h) * 60 - mi) * 60))
    if s == 60:
        s, mi = 0, mi + 1
    if mi == 60:
        mi, h = 0, h + 1
    return datetime(y, m, d, min(h, 23), min(mi, 59), min(s, 59), tzinfo=UTC)


def _kind(ret: int, lunar: bool) -> str:
    table = KIND_LUN if lunar else KIND_SOL
    for flag, name in table:
        if ret & flag:
            return name
    return "جزئي"


# ══════════════════════════════════════════════════════════════════
# العقدة — ولها البابُ كلُّه
# ══════════════════════════════════════════════════════════════════
def node_at(when: datetime) -> dict:
    """
    العقدة عند لحظةٍ ما، وبُعد الشمس عنها.

    **وهذا هو تعليل الكسوف لا وصفُه.** فالقمر يجتمع بالشمس
    اثنتي عشرة مرّةً في السنة ولا يقع الكسوف إلّا في اثنتين أو
    ثلاث — لأنّ مدار القمر مائلٌ نحو خمس درجات، فلا يقع الاجتماع
    على سَمْتِ الشمس إلّا حين يكون قريبًا من **العقدة**، وهي
    حيث يقطع مدارُه دائرةَ البروج.

    فالعقدةُ هي الشرط، والاجتماعُ وحده لا يكفي.
    """
    # **والعقدة تُحسَب هنا لا تُطلَب من `ephem`**: جدولُ الأجرام
    # هناك لا يحوي العقدة، وهي في `chart.py` بـ`TRUE_NODE`. فليكن
    # المصدر واحدًا — **وعقدتان مختلفتان في موقعٍ واحد تُفسدان
    # المقابلة بين صفحة الخريطة وصفحة الكسوف**.
    head = swe.calc_ut(to_jd(when), swe.TRUE_NODE, FLAGS)[0][0] % 360.0
    tail = (head + 180.0) % 360.0
    sun = lon_of("الشمس", when)

    def gap(a: float) -> float:
        d = (sun - a) % 360.0
        return d - 360.0 if d > 180.0 else d

    gh, gt = gap(head), gap(tail)
    near_head = abs(gh) <= abs(gt)
    return {
        "head": round(head, 4), "head_text": _dms(head),
        "tail": round(tail, 4), "tail_text": _dms(tail),
        "near": "الرأس" if near_head else "الذنب",
        "near_lon": round(head if near_head else tail, 4),
        "near_sign": _sign(head if near_head else tail),
        "gap": round(gh if near_head else gt, 3),
        "gap_abs": round(abs(gh if near_head else gt), 3),
    }


# ══════════════════════════════════════════════════════════════════
# كسوفٌ واحد، بكلّ ما يُسأل عنه
# ══════════════════════════════════════════════════════════════════
def _solar(jd: float, back: bool = False, lat=None, lon=None) -> dict | None:
    try:
        ret, tret = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0, back)
    except Exception:
        return None
    if not ret:
        return None
    peak = tret[0]
    when = _from_jd(peak)
    try:
        _, geo, attr = swe.sol_eclipse_where(peak, swe.FLG_SWIEPH)
    except Exception:
        geo, attr = (0.0,) * 10, (0.0,) * 20

    sun = lon_of("الشمس", when)
    out = {
        "type": "شمسي",
        "kind": _kind(ret, False),
        "jd": peak,
        "utc": when.isoformat(),
        "date": when.date().isoformat(),
        "lon": round(sun, 4),
        "sign": _sign(sun),
        "position": _dms(sun),
        "magnitude": round(attr[0], 4) if attr else None,
        "obscuration": round(attr[2], 4) if attr and attr[2] else None,
        "central": bool(ret & swe.ECL_CENTRAL),
        "saros": int(attr[9]) if attr and attr[9] > -9e7 else None,
        "member": int(attr[10]) if attr and attr[10] > -9e7 else None,
        "greatest": ({"lat": round(geo[1], 3), "lon": round(geo[0], 3)}
                     if geo and (geo[0] or geo[1]) else None),
        "node": node_at(when),
    }
    out["note"] = KIND_NOTE.get(out["kind"], "")
    if lat is not None and lon is not None:
        out["local"] = _local_solar(peak, lat, lon)
    return out


def _lunar(jd: float, back: bool = False, lat=None, lon=None) -> dict | None:
    try:
        ret, tret = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0, back)
    except Exception:
        return None
    if not ret:
        return None
    peak = tret[0]
    when = _from_jd(peak)
    try:
        _, attr = swe.lun_eclipse_how(peak, (0.0, 0.0, 0.0), swe.FLG_SWIEPH)
    except Exception:
        attr = (0.0,) * 20

    moon = lon_of("القمر", when)
    out = {
        "type": "قمري",
        "kind": _kind(ret, True),
        "jd": peak,
        "utc": when.isoformat(),
        "date": when.date().isoformat(),
        "lon": round(moon, 4),
        "sign": _sign(moon),
        "position": _dms(moon),
        "magnitude": round(attr[0], 4) if attr else None,
        "penumbral": round(attr[1], 4) if attr else None,
        "central": False,
        "saros": int(attr[9]) if attr and attr[9] > -9e7 else None,
        "member": int(attr[10]) if attr and attr[10] > -9e7 else None,
        "greatest": None,
        "node": node_at(when),
    }
    out["note"] = KIND_NOTE.get(out["kind"], "")
    if lat is not None and lon is not None:
        out["local"] = _local_lunar(peak, lat, lon)
    return out


# ══════════════════════════════════════════════════════════════════
# الرؤية من مدينةٍ بعينها
# ══════════════════════════════════════════════════════════════════
def _local_solar(peak: float, lat: float, lon: float) -> dict:
    """
    **والارتفاع هو الحَكَم.** كسوفٌ عظيمٌ في السماء لا يُرى ممّن
    الشمسُ تحت أفقه — والمواقع التي تُهمل هذا تَعِد الزائر بما
    لا يراه.
    """
    geo = (lon, lat, 0.0)
    # ══════════════════════════════════════════════════════════════
    # **ذروةُ البلد غيرُ ذروة الأرض** — وهذا خطأٌ وقعتُ فيه ثم قِسته.
    #
    # كنتُ أحسب الحال عند `peak`، وهي لحظةُ الذروة **العظمى على
    # الأرض كلِّها**. وكسوفُ ٢٠٢٦/٨/١٢ ذروتُه العظمى فوق المحيط،
    # وذروتُه في مدريد بعدها بدقائق. فخرج القدر **٠٫١٦ ومدريدُ
    # تكاد تراه تامًّا**.
    #
    # ولم يظهر إلّا بمقابلة موضعين معلومين: الأقصر ٢٠٢٧ (كلّي)
    # ومدريد ٢٠٢٦. **ورقمٌ معقولُ الشكل لا يُصدَّق حتى يُقابَل
    # بموضعٍ يُعرَف جوابُه.**
    #
    # فتُطلَب أوّلًا ذروةُ الموضع بـ`when_loc`، ثم يُحسب عندها.
    # ══════════════════════════════════════════════════════════════
    tmax = peak
    try:
        rl, tret, _ = swe.sol_eclipse_when_loc(peak - 2.0, geo,
                                               swe.FLG_SWIEPH, False)
        # لا بدّ أن تكون الذروةُ المحلّية للكسوف نفسه لا لتاليه
        if rl and abs(tret[0] - peak) < 1.0:
            tmax = tret[0]
    except Exception:
        pass

    try:
        ret, attr = swe.sol_eclipse_how(tmax, geo, swe.FLG_SWIEPH)
    except Exception:
        return {"visible": False, "why": "تعذّر الحساب لهذا الموضع."}
    alt = attr[6] if attr else -90.0
    mag = attr[0] if attr else 0.0
    if not ret or mag <= 0:
        return {"visible": False, "why": "لا يُرى من هذا الموضع البتّة."}
    if alt <= 0:
        return {"visible": False, "altitude": round(alt, 2),
                "why": "الشمس تحت الأفق وقت الذروة، فلا يُرى منه."}
    return {
        "visible": True,
        "kind": _kind(ret, False),
        "magnitude": round(mag, 4),
        "obscuration": round(attr[2], 4) if attr[2] else None,
        "altitude": round(alt, 2),
        "azimuth": round(attr[4], 2),
        "utc": _from_jd(tmax).isoformat(),
        "peak_shift_min": round((tmax - peak) * 1440.0),
    }


def _local_lunar(peak: float, lat: float, lon: float) -> dict:
    geo = (lon, lat, 0.0)
    try:
        ret, attr = swe.lun_eclipse_how(peak, geo, swe.FLG_SWIEPH)
    except Exception:
        return {"visible": False, "why": "تعذّر الحساب لهذا الموضع."}
    alt = attr[6] if attr else -90.0
    if alt <= 0:
        return {"visible": False, "altitude": round(alt, 2),
                "why": "القمر تحت الأفق وقت الذروة، فلا يُرى منه."}
    return {
        "visible": True,
        "kind": _kind(ret, True),
        "magnitude": round(attr[0], 4),
        "altitude": round(alt, 2),
        "azimuth": round(attr[4], 2),
    }


# ══════════════════════════════════════════════════════════════════
# المسح: كلُّ ما يقع بين تاريخين
# ══════════════════════════════════════════════════════════════════
def between(start: datetime, end: datetime, lat=None, lon=None,
            kinds: str = "both", limit: int = 400) -> list[dict]:
    """كسوفات الشمس والخسوفات في المدّة، مرتَّبةً بالزمن."""
    out: list[dict] = []
    jd_end = to_jd(end)

    for want, fn in (("شمسي", _solar), ("قمري", _lunar)):
        if kinds != "both" and kinds != want:
            continue
        jd = to_jd(start)
        for _ in range(limit):
            e = fn(jd, False, lat, lon)
            if not e or e["jd"] > jd_end:
                break
            out.append(e)
            jd = e["jd"] + 20.0          # أقصر فاصلٍ بين كسوفين ~٢٩ يومًا

    out.sort(key=lambda e: e["jd"])
    return out


def nearest(when: datetime, lat=None, lon=None) -> dict:
    """أقربُ كسوفٍ ماضٍ وأقربُ آتٍ — لصدر الصفحة."""
    jd = to_jd(when)
    prev = [e for e in (_solar(jd, True, lat, lon), _lunar(jd, True, lat, lon))
            if e]
    nxt = [e for e in (_solar(jd, False, lat, lon), _lunar(jd, False, lat, lon))
           if e]
    return {
        "past": max(prev, key=lambda e: e["jd"]) if prev else None,
        "next": min(nxt, key=lambda e: e["jd"]) if nxt else None,
    }


# ══════════════════════════════════════════════════════════════════
# ساروس: الدورة تُجرَّب، ولا تُدَّعى
# ══════════════════════════════════════════════════════════════════
def saros_chain(when: datetime, lunar: bool, back: int = 2,
                fwd: int = 2, lat=None, lon=None) -> dict:
    """
    نظائرُ الكسوف في سلسلته، قبلُ وبعدُ.

    **والطريقة هي طريقةُ الامتحان لا الإخبار:**

      ١. يُؤخَذ الكسوفُ الأصل.
      ٢. يُزاد عليه (أو يُنقَص منه) ٦٥٨٥٫٣٢ يومًا — وهو ما تقوله
         القاعدة.
      ٣. **ثم يُبحَث عن كسوفٍ حقيقيّ قرب ذلك اليوم.**
      ٤. ويُردّ الفارقُ بين المتوقَّع والواقع بالساعات.

    فإن كان الفارق ساعاتٍ قليلة فقد صدقت القاعدة أمام عين
    الزائر، وإن لم يوجد كسوفٌ ظهر ذلك أيضًا. **وقاعدةٌ تُعرَض
    بلا امتحان تُصدَّق أو تُكذَّب بالثقة، وكلاهما لا يُبنى عليه.**
    """
    fn = _lunar if lunar else _solar
    base = fn(to_jd(when) - 5.0, False, lat, lon)
    if not base:
        return {"base": None, "links": []}

    links = []
    for step in list(range(-back, 0)) + list(range(1, fwd + 1)):
        want = base["jd"] + step * SAROS_DAYS
        found = fn(want - 8.0, False, lat, lon)
        if not found:
            links.append({"step": step, "expected": _from_jd(want).isoformat(),
                          "found": None,
                          "note": "لم يقع كسوفٌ قرب الموعد المتوقَّع."})
            continue
        drift = (found["jd"] - want) * 24.0
        links.append({
            "step": step,
            "expected": _from_jd(want).isoformat(),
            "expected_date": _from_jd(want).date().isoformat(),
            "drift_hours": round(drift, 2),
            "same_saros": (found.get("saros") == base.get("saros")),
            "eclipse": found,
        })
    links.sort(key=lambda x: x["step"])

    # ══════════════════════════════════════════════════════════════
    # **الثلث** — وهو أدقُّ ما في الدورة وأقلُّه ذكرًا.
    #
    # ٦٥٨٥٫٣٢ يومًا = ١٨ سنة و١١ يومًا **وثُلثَ يوم**. ولولا الثلث
    # لعاد الكسوف إلى المكان نفسه من الأرض. لكنّ الأرض تدور ثلثَ
    # دورةٍ في تلك الساعات الثماني، **فيقع النظير على بُعد ١٢٠°
    # غربًا** من موضع أصله.
    #
    # وثلاثةُ أثلاثٍ دورةٌ كاملة: فبعد **ثلاث** دوراتٍ (٥٤ سنة
    # و٣٣ يومًا) يعود الكسوف إلى الناحية نفسها. وهذا ما سمّاه
    # اليونان «إكسِلِغموس».
    #
    # وهو مُقاسٌ لا مُدَّعى: يُؤخَذ خطُّ طول موضع الذروة من
    # المكتبة، ويُعرَض الفرقُ بين كلّ نظيرٍ وسابقه.
    # ══════════════════════════════════════════════════════════════
    # **والإزاحة تُقاس بين المتتاليَين، لا بينها وبين الأصل.**
    # أوّلُ صياغةٍ لي قست كلَّ نظيرٍ إلى الأصل ثم قسمت على عدد
    # الدورات — **وذلك باطلٌ لأن الزاوية تلتفّ**: النظيرُ الثاني
    # أزاحت ٢٤٠°، وتُقرأ ‎−١١٥٫٩‎، فتخرج القسمةُ ‎+٥٨‎ وهو عددٌ لا
    # معنى له. والفرقُ بين خطوتين متجاورتين لا يلتفّ.
    chain = [(0, base)] + [(l["step"], l.get("eclipse")) for l in links]
    chain = [(s, e) for s, e in chain
             if e and e.get("greatest")]
    chain.sort(key=lambda x: x[0])
    shifts = {}
    for (s0, e0), (s1, e1) in zip(chain, chain[1:]):
        d = (e1["greatest"]["lon"] - e0["greatest"]["lon"]) % 360.0
        if d > 180.0:
            d -= 360.0
        shifts[s1] = round(d, 1)

    for link in links:
        e = link.get("eclipse")
        link["greatest"] = e.get("greatest") if e else None
        # الإزاحة عن الخطوة التي قبلها — وهي التي تُقارَب ١٢٠°
        link["shift_deg"] = shifts.get(link["step"])

    return {"base": base, "links": links,
            "saros_days": SAROS_DAYS,
            "period_text": "١٨ سنة و١١ يومًا و٨ ساعات",
            "third": {
                "fraction_days": round(SAROS_DAYS - int(SAROS_DAYS), 4),
                "hours": round((SAROS_DAYS - int(SAROS_DAYS)) * 24, 2),
                "shift_expected": 120.0,
                "text": ("الكسرُ الباقي من الدورة ثُلثُ يومٍ تقريبًا "
                         "(نحو ثماني ساعات). وفي تلك الساعات تدور الأرض "
                         "ثلثَ دورة، فيقع النظيرُ على نحو ١٢٠° غربًا من "
                         "موضع أصله."),
                "exeligmos_text": ("وثلاثةُ أثلاثٍ دورةٌ تامّة: فبعد ثلاث "
                                   "دورات — أي ٥٤ سنة و٣٣ يومًا — يعود "
                                   "الكسوف إلى الناحية نفسها. وهي التي "
                                   "سمّاها اليونان «إكسِلِغموس»."),
                "exeligmos_days": round(SAROS_DAYS * 3, 2),
                # وبقيّةُ الإكسلغموس: كم بقي بعد ثلاث دوراتٍ من
                # الرجوع التامّ. تُقاس ولا تُدَّعى.
                "exeligmos_residual": _residual(base, links, 3),
            }}


def _residual(base: dict, links: list, n: int) -> float | None:
    """ما بقي من الدورة بعد `n` دورات — بالدرجات، بين الأصل والنظير."""
    g0 = base.get("greatest")
    hit = next((l for l in links if l["step"] == n and l.get("greatest")), None)
    hit = hit or next((l for l in links
                       if l["step"] == -n and l.get("greatest")), None)
    if not g0 or not hit:
        return None
    d = (hit["greatest"]["lon"] - g0["lon"]) % 360.0
    return round(d - 360.0 if d > 180.0 else d, 1)


# ══════════════════════════════════════════════════════════════════
# الأحكام — تراثٌ يُنسَب إلى قائليه، لا قولٌ لنا
# ══════════════════════════════════════════════════════════════════
RULING_KIND = {
    "شمسي": (
        "الكسوف عند القدماء اجتماعٌ مشدَّد: بدايةُ أمرٍ تمتدّ آثاره "
        "أشهرًا. وما يُفتَح فيه من بابٍ يبقى مفتوحًا طويلًا، "
        "وأثرُه يظهر في الأسابيع التالية لا في يومه غالبًا."),
    "قمري": (
        "الخسوف بدرٌ مشدَّد: انكشافٌ وانقضاء. يُنهي ما استُنفد، "
        "ويُظهر ما كان مستورًا. ولا يُبتدأ فيه عند أهل الاختيارات."),
}

# **قاعدة المدّة عند بطلَميوس** (الرابعة، المقالة الثانية):
# يُقاس زمنُ الكسوف بالساعات الاستوائية، فيُجعل لكلّ ساعةٍ من
# كسوف الشمس سنةٌ من الأثر، ومن الخسوف شهر. وهي قاعدةٌ **تُنسَب
# ولا تُتبنّى** — ولا سند لها من الرصد، وإنّما تُذكر لأنّها ممّا
# بُنيت عليه أحكامُ الملل والدول في كتبهم.
DURATION_RULE = {
    "شمسي": ("لكلّ ساعةٍ من زمن الكسوف سنةٌ من الأثر", "سنة"),
    "قمري": ("لكلّ ساعةٍ من زمن الخسوف شهرٌ من الأثر", "شهر"),
}

# ما يُتجنَّب فيه — وهو موصولٌ بما في `elections.py` كي لا يفترق
# قولُ الصفحتين. **وقولان لشيءٍ واحد في موقعٍ واحد عيبٌ ظاهر.**
AVOID = ("الابتداءات كلُّها: عقدُ النكاح، وافتتاحُ التجارة، "
         "وتوليةُ العمل، والسفرُ، والدواءُ والحجامة. ويمتدّ حكمه "
         "أيامًا حوله لا يومَه وحده.")


def rulings(e: dict) -> dict:
    """
    ما قاله القدماء في هذا الكسوف بعينه — منسوبًا إلى كتبهم.

    **ولا يُقال «سيقع كذا»**، إنّما «قالوا كذا». والفرقُ بينهما
    هو الفرقُ بين نقلِ تراثٍ وادّعاءِ غيب.
    """
    kind = e["type"]
    rule, unit = DURATION_RULE[kind]
    return {
        "general": RULING_KIND[kind],
        "sign": e["sign"],
        "node": e["node"]["near"],
        "node_note": (
            "وقع عند الرأس، وهو عندهم زائدٌ في أمر البرج الذي وقع فيه."
            if e["node"]["near"] == "الرأس" else
            "وقع عند الذنب، وهو عندهم ناقصٌ من أمر البرج الذي وقع فيه."),
        "duration_rule": rule,
        "duration_unit": unit,
        "avoid": AVOID,
        "sources": "«الأربعة» لبطلَميوس (المقالة الثانية) · «التفهيم» "
                   "للبيروني · «البارع» لابن أبي الرجال.",
        "caveat": "أحكامُ الكسوف تراثٌ يُنقَل، لا نتيجةَ رصدٍ ولا "
                  "تنبّؤًا بحادث. والحسابُ في هذه الصفحة قطعيّ، "
                  "والحكمُ الذي بعده منقولٌ عن أهله.",
    }


def personal(e: dict, cusps: list[float]) -> dict:
    """
    أين يقع هذا الكسوف من خريطة صاحبها — بالبيت لا بالدعوى.

    **وهذا كلُّ ما يُحسَب**: البيت الذي يسقط فيه طولُ الكسوف.
    وأمّا ما يُقال عن البيت فمن كتبهم، وقد فُصل عنه في `rulings`.
    """
    from .chart import house_of  # noqa: PLC0415
    h = house_of(e["lon"], cusps)
    return {"house": h,
            "text": f"يقع هذا الكسوف في البيت {h} من خريطتك، "
                    f"في {e['position']}."}


# ══════════════════════════════════════════════════════════════════
# لماذا لا يقع كسوفٌ في كل شهر؟ — يُعرَض بالعدد
# ══════════════════════════════════════════════════════════════════
def conjunction_audit(year: int) -> dict:
    """
    كلُّ اجتماعٍ للنيّرين في سنة، وأيُّها أورث كسوفًا.

    **وهذه هي الحجّة كلُّها في جدولٍ واحد**: تُعَدّ الاجتماعات
    فتُوجَد اثنَي عشرَ أو ثلاثةَ عشرَ، ويُعَدّ ما كسف منها فيُوجَد
    اثنان أو ثلاثة — **وكلُّها عند العقدة**. فيرى الزائر بعينه
    أن الاجتماع شرطٌ لا يكفي، وأن العقدة هي الفارق.
    """
    from .ephem import _bisect  # noqa: PLC0415

    start = datetime(year, 1, 1, tzinfo=UTC)
    end = datetime(year + 1, 1, 1, tzinfo=UTC)

    def elong(t: datetime) -> float:
        d = (lon_of("القمر", t) - lon_of("الشمس", t)) % 360.0
        return d - 360.0 if d > 180.0 else d

    rows, t = [], start
    while t < end:
        nxt = t + timedelta(days=1)
        a, b = elong(t), elong(nxt)
        if a > 0 >= b or (a < 0 and b >= 0 and abs(a) < 30):
            if abs(a - b) < 180:                  # لا قفزةَ التفاف
                exact = _bisect(elong, t, nxt)
                nd = node_at(exact)
                rows.append({
                    "utc": exact.isoformat(),
                    "date": exact.date().isoformat(),
                    "sign": _sign(lon_of("الشمس", exact)),
                    "node": nd["near"],
                    "gap": nd["gap_abs"],
                })
        t = nxt

    ecl = {e["date"]: e for e in between(start, end, kinds="شمسي")}
    for r in rows:
        hit = ecl.get(r["date"])
        r["eclipse"] = hit["kind"] if hit else None
    return {
        "year": year,
        "conjunctions": rows,
        "total": len(rows),
        "eclipsed": sum(1 for r in rows if r["eclipse"]),
        # الحدُّ المشهور: الكسوف ممكنٌ ضمن ~١٨٫٥° من العقدة، ومتحتّمٌ
        # ضمن ~١٥٫٤°. وهذا يُرى في العمود «البُعد عن العقدة».
        "limit_possible": 18.5,
        "limit_certain": 15.4,
    }
