# -*- coding: utf-8 -*-
"""
التوافق بين خريطتين — التزاوج والمركّبة ودافيسون.

ثلاثة أعمال في ملفّ واحد:

١. **التزاوج (synastry)**: تُوضع الخريطتان إحداهما فوق الأخرى، فيُنظر
   في زوايا كواكب الأولى إلى كواكب الثانية، وفي أيّ بيوت الثانية تقع
   كواكب الأولى. هذا هو اللقاء نفسه: ما يفعله كلٌّ بالآخر.

٢. **المركّبة (composite)**: خريطة وهمية لا تُوجد في السماء، كواكبها
   نقاط منتصف بين كوكبي الخريطتين. تصف **العلاقة ككيان ثالث** لا
   الشخصين. وهي طريقة معاصرة لا تراثية، ونقولها صراحة.

٣. **دافيسون (Davison)**: خريطة **حقيقية** تُحسَب للحظة المنتصف بين
   المولدين، ولنقطة المنتصف الجغرافية بينهما. تفضل المركّبة عند من
   يشترط أن تكون الخريطة سماءً وقعت فعلًا.

وثلاثة موازين — عاطفي وصداقة ومهني — لكلٍّ معاييره وأوزانه المعلنة،
مع تفصيل يُظهر للقارئ **من أين جاءت الدرجة**، لا رقمًا يُلقى عليه.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math

from . import chart, dignities as dig
from .chart import (ASPECT_DEFS, BODY_CLASS, BODY_SYMBOL, SIGNS,
                    _wrap180, dms, house_of, orb_for)

UTC = timezone.utc

# الأجرام التي تدخل في التزاوج — الذنب مشتقّ من الرأس، وليليث الحقيقية
# حساب ثانٍ للنقطة نفسها، فلا يُضاعَف بهما الوزن.
SYN_BODIES = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري",
              "زحل", "أورانوس", "نبتون", "بلوتو", "الرأس", "ليليث", "خيرون"]

# كواكب العلاقة — عليها يُحصَر التقبّل من طرف واحد
RELATION_PLANETS = {"الشمس", "القمر", "الزهرة", "المريخ"}

# تسمية الموازين في الكلام العربي السليم
DOMAIN_LABEL = {"عاطفي": "الميزان العاطفي", "صداقة": "ميزان الصداقة",
                "مهني": "الميزان المهني"}


# ══════════════════════════════════════════════════════════════
# ١ — الزوايا المتبادلة
# ══════════════════════════════════════════════════════════════
def inter_aspects(a: dict, b: dict, minor: bool = True) -> list:
    """
    زوايا كواكب (أ) إلى كواكب (ب) — بما فيها الطالع ووسط السماء.

    الوجاج هنا **أضيق** منه في الخريطة الواحدة: الزاوية بين خريطتين
    أضعف أثرًا من الزاوية داخل الخريطة، فنُضيّقها إلى ثلاثة أرباع.
    """
    A = [x for x in a["bodies"] if x["name"] in SYN_BODIES]
    B = [x for x in b["bodies"] if x["name"] in SYN_BODIES]
    # الوتدان يدخلان بوصفهما نقطتين
    for src, dst in ((a, A), (b, B)):
        for ang in ("الطالع", "وسط السماء"):
            v = src["angles"][ang]
            dst.append({"name": ang, "lon": v["lon"], "speed": 0.0,
                        "class": "نيّر", "symbol": "", "sign": v["sign"]})

    out = []
    for x in A:
        for y in B:
            sep = abs(_wrap180(x["lon"] - y["lon"]))
            best = None
            for name, angle, polarity, major, sym in ASPECT_DEFS:
                if not major and not minor:
                    continue
                omax = orb_for(angle, x["class"], y["class"]) * 0.75
                orb = abs(sep - angle)
                if orb <= omax and (best is None or orb < best["orb"]):
                    best = {"a": x["name"], "b": y["name"], "name": name,
                            "angle": angle, "polarity": polarity, "major": major,
                            "symbol": sym, "orb": round(orb, 2),
                            "orb_max": round(omax, 2),
                            "strength": round(max(0.0, 1 - orb / omax), 2)}
            if best:
                out.append(best)
    out.sort(key=lambda x: x["orb"])
    return out


def overlays(a: dict, b: dict) -> list:
    """كواكب (أ) في أيّ بيوت (ب) — أين يقع الأوّل من حياة الثاني."""
    cusps = [h["lon"] for h in b["houses"]["cusps"]]
    out = []
    for x in a["bodies"]:
        if x["name"] not in SYN_BODIES:
            continue
        h = house_of(x["lon"], cusps)
        out.append({"body": x["name"], "symbol": x["symbol"],
                    "sign": x["sign"], "house": h})
    return out


def receptions(a: dict, b: dict) -> list:
    """
    التقبّل بين الخريطتين — أعمق ما في الباب التراثي، ولا يذكره
    أيّ من المواقع العالمية في صفحات التوافق.

    إن وقع كوكبُ الأوّل في برجٍ صاحبُه كوكبٌ للثاني، ووقع ذلك الكوكب
    في برجٍ صاحبُه الأوّل، فبينهما **تقبّل تامّ**: كلٌّ نازل في دار
    الآخر. وهو أقوى علامة ودّ عند المنجّمين العرب، لأن كلًّا منهما
    يحتاج صاحبه ليُقيم.

    وننبّه: كوكب في برجه هو **في داره لا في دار غيره**، فلا يُحسَب
    ذلك تقبّلًا. وهذا خلط يقع فيه من يُبرمج الباب بلا تدقيق.
    """
    A = {x["name"]: x for x in a["bodies"]}
    B = {x["name"]: x for x in b["bodies"]}
    seven = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"]
    out, seen = [], set()
    for p in seven:
        for q in seven:
            if p == q or p not in A or q not in B:
                continue          # كوكب في برجه ليس ضيفًا عند أحد
            key = tuple(sorted((p, q)))
            sa, sb = A[p]["sign"], B[q]["sign"]

            if dig.DOMICILE[sa] == q and dig.DOMICILE[sb] == p:
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "a": p, "b": q, "a_sign": sa, "b_sign": sb,
                    "kind": "تقبّل تامّ بالبيت", "weight": 3,
                    "note": (f"{p} عندك في {sa} — وهو دار {q}. "
                             f"و{q} عنده في {sb} — وهو دار {p}. "
                             "كلٌّ نازل في دار الآخر، وهي أقوى علامة "
                             "ودّ في الباب التراثي."),
                })
            elif dig.EXALT.get(q, (None,))[0] == sa and \
                    dig.EXALT.get(p, (None,))[0] == sb:
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "a": p, "b": q, "a_sign": sa, "b_sign": sb,
                    "kind": "تقبّل بالشرف", "weight": 2,
                    "note": (f"{p} عندك في {sa} — وهو شرف {q}. "
                             f"و{q} عنده في {sb} — وهو شرف {p}. "
                             "يُكرم كلٌّ منكما ما يرفع الآخر."),
                })
            elif (dig.DOMICILE[sa] == q or dig.DOMICILE[sb] == p) and \
                    p in RELATION_PLANETS and q in RELATION_PLANETS:
                # التقبّل من طرف يقع كثيرًا، فلو ذُكر كلّه صار ضجيجًا
                # يُغرق التقبّل التامّ. نحصره في كواكب العلاقة.
                if key in seen:
                    continue
                seen.add(key)
                who = (p, sa, q) if dig.DOMICILE[sa] == q else (q, sb, p)
                out.append({
                    "a": p, "b": q, "a_sign": sa, "b_sign": sb,
                    "kind": "تقبّل من طرف", "weight": 1,
                    "note": (f"{who[0]} في {who[1]}، وهو دار {who[2]}. "
                             "ضيافة من طرف واحد: يحتاجه ولا يحتاجه."),
                })
    order = {"تقبّل تامّ بالبيت": 0, "تقبّل بالشرف": 1, "تقبّل من طرف": 2}
    out.sort(key=lambda x: order[x["kind"]])
    return out


# ══════════════════════════════════════════════════════════════
# ٢ — الموازين الثلاثة
# ══════════════════════════════════════════════════════════════
# كل معيار: (اسم الجرم الأوّل، اسم الثاني، وزن الميسّر، وزن المعسّر، شرحه)
# الوزنان مختلفان عمدًا: زحل على الزهرة يخصم من العاطفي أكثر ممّا
# يُضيفه تثليثُه، بينما يُضيف إلى المهني لأن الالتزام هناك فضيلة.
CRITERIA = {
    "عاطفي": [
        ("الشمس", "القمر", 14, -4, "أقوى وصلة في الباب كلّه: إرادة أحدهما وحاجة الآخر"),
        ("الزهرة", "المريخ", 12, -3, "الودّ والرغبة — بلا هذه تصير الصحبة أخوّة"),
        ("القمر", "القمر", 10, -5, "توافق المزاج والإيقاع اليومي"),
        ("الشمس", "الزهرة", 8, -2, "أن يراك جميلًا وأن تراه"),
        ("القمر", "الزهرة", 8, -2, "حنان يُبادَل بلا شرط"),
        ("الطالع", "الزهرة", 7, -2, "انجذاب أوّل، من النظرة لا من الفكرة"),
        ("الطالع", "المريخ", 5, -3, "شرارة بدنية — تُشعل وتحرق"),
        ("الشمس", "الشمس", 6, -4, "أن تسيرا في اتجاه واحد"),
        ("القمر", "المريخ", 4, -6, "الحماية والغضب في وصلة واحدة"),
        ("الزهرة", "زحل", 4, -8, "التزام يُثقل أو يُثبّت"),
        ("الزهرة", "المشتري", 7, -1, "كرم في الودّ وسعة في الاحتمال"),
        ("القمر", "زحل", 3, -7, "أمان يُبنى ببطء، أو برد يُطفئ"),
        ("الشمس", "زحل", 3, -6, "أحدهما يُربّي الآخر — وقد يخنقه"),
        ("الزهرة", "بلوتو", 5, -6, "شغف يُحوّل، أو استحواذ"),
        ("الزهرة", "نبتون", 5, -5, "حبّ مثاليّ — رحمة أو وهم"),
        ("وسط السماء", "الزهرة", 4, -1, "أن تُفاخر به بين الناس"),
    ],
    "صداقة": [
        ("القمر", "القمر", 13, -5, "الراحة في الحضور — أهمّ ما في الصحبة"),
        ("عطارد", "عطارد", 12, -4, "أن تفهم كلامه من نصفه"),
        ("المشتري", "الشمس", 9, -2, "أحدهما يُوسّع أفق الآخر"),
        ("المشتري", "القمر", 9, -2, "سخاء يُشعر بالأمان"),
        ("الطالع", "الطالع", 8, -3, "أن يتشابه إيقاع الظهور"),
        ("عطارد", "المشتري", 8, -2, "حديث يتّسع ولا يملّ"),
        ("الشمس", "القمر", 8, -3, "قرب لا يُشترط أن يكون عاطفيًّا"),
        ("عطارد", "القمر", 7, -3, "أن يُصغي إليك لا أن يردّ عليك"),
        ("الزهرة", "الزهرة", 7, -2, "ذوق مشترك: ما تُحبّان وما تكرهان"),
        ("المريخ", "المريخ", 5, -6, "أن تتّفقا على ما تفعلانه معًا"),
        ("زحل", "القمر", 3, -6, "ثقل في الصحبة يُطيلها أو يُنهيها"),
        ("أورانوس", "الشمس", 5, -3, "صداقة تُوقظ — وقد لا تدوم"),
        ("زحل", "زحل", 6, -2, "أن تكونا من جيل واحد وتفهما ثقلًا واحدًا"),
    ],
    "مهني": [
        ("زحل", "الشمس", 10, -4, "بنية والتزام — أساس أيّ عمل يدوم"),
        ("عطارد", "عطارد", 11, -4, "أن تتفاهما في التفاصيل بلا شرح"),
        ("المريخ", "زحل", 9, -5, "الدفع والانضباط: أنجع تركيب في التنفيذ"),
        ("وسط السماء", "الشمس", 9, -2, "أن يخدم عملُه هويّتك"),
        ("وسط السماء", "زحل", 8, -2, "مسار يُبنى لا يُرتجل"),
        ("المشتري", "زحل", 8, -3, "الرجاء والحساب في يدين"),
        ("عطارد", "زحل", 8, -3, "أن يُنظَّم الكلام فيصير خطّة"),
        ("المريخ", "الشمس", 7, -4, "قدرة على العمل تحت ضغط واحد"),
        ("المشتري", "وسط السماء", 7, -1, "فرص تأتي من الشراكة"),
        ("الشمس", "الشمس", 6, -4, "وحدة الوجهة"),
        ("زحل", "زحل", 6, -2, "أن تتشابه فكرتكما عن الوقت والحدّ"),
        ("عطارد", "المريخ", 5, -5, "قرار سريع — أو جدال لا ينتهي"),
        ("بلوتو", "الشمس", 4, -6, "صراع على من يمسك الدفّة"),
        ("القمر", "القمر", 4, -3, "أن يُحتمَل مزاج كلٍّ منكما"),
    ],
}

# البيوت التي يُحسَب لها وزن حين تقع فيها كواكب الآخر
OVERLAY_WEIGHT = {
    "عاطفي": {1: 3, 5: 5, 7: 6, 8: 3, 4: 3, 12: -2, 6: -1},
    "صداقة": {1: 3, 3: 3, 5: 4, 11: 6, 9: 3, 12: -1},
    "مهني": {1: 2, 2: 3, 6: 5, 10: 6, 8: 2, 11: 3, 12: -2},
}
# الكواكب التي يُعتدّ بمواضعها في البيوت (الشخصية والنيّران)
OVERLAY_BODIES = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ",
                  "المشتري", "زحل"]

_POS = {"إيجابية"}
_NEG = {"سلبية"}
_MAJOR = {"اقتران", "تسديس", "تربيع", "تثليث", "تقابل"}


def _pair_hits(asp: list, p: str, q: str) -> list:
    """كل زاوية بين الجرمين، في الاتجاهين."""
    return [a for a in asp
            if {a["a"], a["b"]} == {p, q} or (p == q and a["a"] == a["b"] == p)]


def _weigh(a: dict, b: dict, asp: list | None = None) -> dict:
    """الحساب الخام: بنود كل ميزان وأوزانها، قبل أي تحجيم."""
    asp = asp if asp is not None else inter_aspects(a, b)
    ov_ab = overlays(a, b)
    ov_ba = overlays(b, a)
    rec = receptions(a, b)
    out = {}

    for domain, rules in CRITERIA.items():
        detail, plus, minus = [], 0.0, 0.0
        for p, q, w_ok, w_bad, why in rules:
            for h in _pair_hits(asp, p, q):
                if h["name"] not in _MAJOR:
                    continue
                good = h["polarity"] in _POS or h["name"] == "اقتران"
                # الاقتران بالمُنحِسَين يُقرأ معسِّرًا
                if h["name"] == "اقتران" and ("زحل" in (p, q) or "بلوتو" in (p, q)):
                    good = False
                w = (w_ok if good else abs(w_bad)) * h["strength"]
                (plus, minus) = (plus + w, minus) if good else (plus, minus + w)
                detail.append({"pair": f"{p} — {q}", "aspect": h["name"],
                               "orb": h["orb"], "weight": round(w if good else -w, 1),
                               "why": why})

        hw = OVERLAY_WEIGHT[domain]
        for label, ov in (("كواكبه في بيوتك", ov_ba), ("كواكبك في بيوته", ov_ab)):
            for o in ov:
                if o["body"] not in OVERLAY_BODIES:
                    continue
                w = hw.get(o["house"], 0)
                if not w:
                    continue
                (plus, minus) = ((plus + w * .5, minus) if w > 0
                                 else (plus, minus + abs(w) * .5))
                detail.append({
                    "pair": f"{label}: {o['body']} في البيت {o['house']}",
                    "aspect": "موضع", "orb": None, "weight": round(w * .5, 1),
                    "why": f"البيت {o['house']} من أبواب هذا الميزان"})

        # التقبّل يُضاف إلى الموازين الثلاثة، فهو ودّ عامّ لا خاصّ
        for r in rec:
            plus += r["weight"]
            detail.append({"pair": f"{r['kind']}: {r['a']} و{r['b']}",
                           "aspect": "تقبّل", "orb": None,
                           "weight": float(r["weight"]), "why": r["note"]})

        detail.sort(key=lambda d: -abs(d["weight"]))
        out[domain] = {"plus": round(plus, 1), "minus": round(minus, 1),
                       "net": round(plus - minus, 2), "detail": detail}
    return out


def raw_net(a: dict, b: dict, asp: list | None = None) -> dict:
    """الصافي وحده — تستعمله أداة المعايرة."""
    return {d: v["net"] for d, v in _weigh(a, b, asp).items()}


# ثوابت المعايرة — مولَّدة بـ tools/calibrate_synastry.py
# ٦٠٠٠ زوج عشوائي من ٢٦٠ خريطة في عشر مدن متباعدة، ١٩٤٠–٢٠١٠.
# كل قائمة ٢١ نقطة قطع، من المئين ٠ إلى ١٠٠ بخطوة ٥.
# أعِد توليدها إن تغيّرت المعايير أو أوزانها، وإلا كذبت الرتبة.
CALIBRATION: dict[str, list] = {
    "عاطفي": [-19.95, 3.96, 7.41, 10.03, 11.92, 13.63, 15.09, 16.61,
              18.07, 19.45, 20.77, 22.11, 23.59, 25.1, 26.57, 28.48,
              30.48, 32.83, 35.66, 40.71, 68.05],
    "صداقة": [-4.62, 7.91, 10.82, 12.82, 14.55, 15.94, 17.18, 18.26,
              19.37, 20.48, 21.55, 22.79, 24.1, 25.28, 26.67, 28.19,
              29.86, 32.05, 34.78, 39.24, 62.34],
    "مهني": [-8.75, 6.31, 9.17, 11.29, 12.9, 14.52, 15.81, 17.12,
             18.31, 19.52, 20.71, 22.02, 23.26, 24.79, 26.32, 27.78,
             29.46, 31.57, 34.31, 38.31, 59.85],
}


def _percentile(net: float, cuts: list) -> int:
    """
    رتبة مئوية بالاستيفاء الخطّي بين نقاط القطع.

    لا نُرجع ٠ ولا ١٠٠ حدًّا قاطعًا: خارج المدى نُقرّب إلى ١ و٩٩،
    لأن الادّعاء بأن زوجًا «أسوأ من كلّ زوج في الأرض» ادّعاء لا
    تحتمله عيّنة من ستّة آلاف.
    """
    if not cuts:
        return 50
    if net <= cuts[0]:
        return 1
    if net >= cuts[-1]:
        return 99
    step = 100 / (len(cuts) - 1)
    for i in range(1, len(cuts)):
        if net <= cuts[i]:
            lo, hi = cuts[i - 1], cuts[i]
            frac = 0.0 if hi == lo else (net - lo) / (hi - lo)
            return max(1, min(99, round((i - 1 + frac) * step)))
    return 99


BANDS = [
    (85, "استثنائي", "وصلات قويّة نادرة الاجتماع"),
    (70, "قويّ", "أكثر ممّا يجتمع للناس عادة"),
    (55, "فوق المعتاد", "فيه ما يُبنى عليه"),
    (45, "معتاد", "كأكثر ما يقع بين اثنين"),
    (30, "دون المعتاد", "يحتاج عملًا واعيًا"),
    (0, "عسير", "الوصلات المعسِّرة أغلب"),
]


def score(a: dict, b: dict, asp: list | None = None) -> dict:
    """
    الموازين الثلاثة — **رتبة مئوية** لا نسبة مخترعة.

    الدرجة تقول شيئًا محدّدًا: صافي أوزانكما يفوق كذا بالمئة من
    ستّة آلاف زوج عشوائي وُلدوا بين ١٩٤٠ و٢٠١٠ في عشر مدن متباعدة.
    ومعها تفصيل يُظهر من أين جاءت كل نقطة.
    """
    w = _weigh(a, b, asp)
    out = {}
    for domain, v in w.items():
        pc = _percentile(v["net"], CALIBRATION.get(domain, []))
        label = DOMAIN_LABEL[domain]
        band = next(b_ for cut, *b_ in
                    [(c, n, d) for c, n, d in BANDS] if pc >= cut)
        out[domain] = {
            "label": label,
            "score": pc,
            "band": band[0], "band_note": band[1],
            "net": v["net"], "plus": v["plus"], "minus": v["minus"],
            "detail": v["detail"][:14],
            "count": len(v["detail"]),
            "scale": ("رتبة مئوية مقابل ٦٠٠٠ زوج عشوائي — "
                      "لا نسبة مطلقة."),
        }
    return out


# ══════════════════════════════════════════════════════════════
# ٣ — الخريطة المركّبة
# ══════════════════════════════════════════════════════════════
def _mid(x: float, y: float) -> float:
    """
    نقطة المنتصف على **القوس الأقصر** — وهذا موضع الخطأ الأشهر
    في الخرائط المركّبة: من أخذ المتوسّط الحسابي وقع نصف كواكبه
    في البرج المقابل كلّما تجاوز الزوج رأس الحمل.

    وحين يكون الجرمان متقابلين تمامًا (١٨٠° بالضبط) فالقوسان
    متساويان ولا منتصف أقصر. نختار الأمامي — من الأوّل إلى
    الثاني بالترتيب — لأن الاختيار وجب أن يكون معلومًا ثابتًا
    لا متروكًا لتقريب الحاسوب.
    """
    d = (y - x) % 360.0
    if d > 180.0:
        d -= 360.0
    return (x + d / 2) % 360.0


def composite(a: dict, b: dict) -> dict:
    """
    كواكب المركّبة نقاطُ منتصف. ليست سماءً وقعت، بل تجريد يصف
    العلاقة ككيان ثالث. طريقة معاصرة لا تراثية — نقولها ولا نُخفيها.
    """
    A = {x["name"]: x for x in a["bodies"]}
    B = {x["name"]: x for x in b["bodies"]}
    asc = _mid(a["angles"]["الطالع"]["lon"], b["angles"]["الطالع"]["lon"])
    mc = _mid(a["angles"]["وسط السماء"]["lon"], b["angles"]["وسط السماء"]["lon"])

    bodies = []
    for name in SYN_BODIES:
        if name not in A or name not in B:
            continue
        lon = _mid(A[name]["lon"], B[name]["lon"])
        bodies.append({
            "name": name, "symbol": BODY_SYMBOL.get(name, ""),
            "lon": round(lon, 4), "speed": 0.0,
            "class": BODY_CLASS.get(name, "نقطة"),
            "sign": SIGNS[int(lon // 30)],
            "text": dms(lon)["text"], "short": dms(lon)["short"],
            "retro": False, "core": True,
        })

    # بيوت كاملة من طالع المنتصف — أسلمُ نظام لخريطة لا وقت لها
    cusps = [{"house": i + 1, "lon": (int(asc // 30) * 30 + i * 30) % 360.0}
             for i in range(12)]
    cl = [c["lon"] for c in cusps]
    for x in bodies:
        x["house"] = house_of(x["lon"], cl)

    aspects = chart.find_aspects(bodies, minor=False)
    return {
        "kind": "مركّبة",
        "note": ("خريطة نقاط المنتصف. لا توجد في السماء، وإنما تصف "
                 "العلاقة نفسها ككيان ثالث. طريقة معاصرة لا تراثية، "
                 "وأنفع ما فيها موضع شمسها وقمرها وطالعها."),
        "angles": {"الطالع": {"lon": round(asc, 4), **dms(asc)},
                   "وسط السماء": {"lon": round(mc, 4), **dms(mc)}},
        "bodies": bodies,
        "cusps": cusps,
        "aspects": aspects,
        "system": "البيوت الكاملة من طالع المنتصف",
    }


# ══════════════════════════════════════════════════════════════
# ٤ — خريطة دافيسون
# ══════════════════════════════════════════════════════════════
def davison_moment(a_utc: datetime, b_utc: datetime,
                   a_lat: float, a_lon: float,
                   b_lat: float, b_lon: float) -> dict:
    """
    لحظة المنتصف الزمني، ونقطة المنتصف الجغرافي.

    الطول الجغرافي يُتوسَّط على القوس الأقصر أيضًا — وإلا وقع من
    وُلد أحدهما شرق خطّ التاريخ والآخر غربه في منتصف الكرة المقابل.
    """
    mid_t = a_utc + (b_utc - a_utc) / 2
    lat = (a_lat + b_lat) / 2
    d = ((b_lon - a_lon + 540) % 360) - 180
    lon = ((a_lon + d / 2 + 540) % 360) - 180
    return {"when_utc": mid_t, "lat": round(lat, 4), "lon": round(lon, 4)}


def davison(a: dict, b: dict, house_system: str = "whole") -> dict:
    """خريطة حقيقية للحظة المنتصف ومكان المنتصف."""
    a_utc = datetime.fromisoformat(a["when_utc"])
    b_utc = datetime.fromisoformat(b["when_utc"])
    m = davison_moment(a_utc, b_utc, a["lat"], a["lon"], b["lat"], b["lon"])
    c = chart.compute(m["when_utc"].replace(tzinfo=UTC), m["lat"], m["lon"],
                      house_system, "UTC", minor_aspects=False)
    c["kind"] = "دافيسون"
    c["note"] = ("سماء وقعت فعلًا: منتصف الزمن بين المولدين، ومنتصف "
                 "المسافة بين المكانين. يفضّلها من يشترط أن تكون "
                 "الخريطة رصدًا لا تجريدًا.")
    c["midpoint"] = {"when_utc": m["when_utc"].isoformat(),
                     "lat": m["lat"], "lon": m["lon"]}
    return c


# ══════════════════════════════════════════════════════════════
# ٥ — القراءة المجمَّعة
# ══════════════════════════════════════════════════════════════
def read(a: dict, b: dict, name_a: str = "الأوّل", name_b: str = "الثاني",
         top: int = 12) -> dict:
    """كلّ ما يُعرَض على القارئ، مرتّبًا: الوصلات ثم البيوت ثم الموازين."""
    from . import synastry_deep as sd

    asp = inter_aspects(a, b)
    major = [x for x in asp if x["major"]]
    lines = []
    for x in major[:top]:
        d = sd.pair_text(x["a"], x["b"], x["name"])
        lines.append({
            "title": f"{x['a']} ({name_a}) {x['symbol']} {x['b']} ({name_b})",
            "aspect": x["name"], "theme": d["theme"], "text": d["text"],
            "orb": x["orb"], "polarity": x["polarity"],
            "strength": x["strength"],
        })

    def ov_block(src, dst, label):
        out = []
        for o in overlays(src, dst):
            if o["body"] not in OVERLAY_BODIES:
                continue
            out.append({"body": o["body"], "symbol": o["symbol"],
                        "sign": o["sign"], "house": o["house"],
                        "text": sd.OVERLAY_TEXT[o["house"]]})
        out.sort(key=lambda x: x["house"])
        return {"label": label, "items": out}

    rec = receptions(a, b)
    sc = score(a, b, asp)

    # حكم مختصر: أعلى الموازين وأدناها
    best = max(sc, key=lambda k: sc[k]["score"])
    worst = min(sc, key=lambda k: sc[k]["score"])
    verdict = (f"أقوى ما بينكما {DOMAIN_LABEL[best]}: {sc[best]['score']} — "
               f"{sc[best]['band']}. وأضعفها {DOMAIN_LABEL[worst]}: "
               f"{sc[worst]['score']} — {sc[worst]['band']}. "
               "والرتبة نسبيّة لا مطلقة: تقارن حالكما بستّة آلاف زوج "
               "عشوائي، ولا تحكم على علاقة بعينها. الخريطة تصف ميلًا، "
               "والعِشرة تصنعها المعاملة.")

    return {
        "names": {"a": name_a, "b": name_b},
        "scores": sc,
        "verdict": verdict,
        "aspects": lines,
        "aspect_count": {"كبرى": len(major), "الكلّ": len(asp)},
        "overlays": [ov_block(b, a, f"كواكب {name_b} في بيوت {name_a}"),
                     ov_block(a, b, f"كواكب {name_a} في بيوت {name_b}")],
        "receptions": rec,
        "reception_note": ("التقبّل باب تراثي لا تذكره صفحات التوافق "
                           "العالمية: أن ينزل كوكب كلٍّ منكما في دار "
                           "كوكب الآخر، فيحتاج كلٌّ صاحبه ليُقيم."),
        "sources": {
            "الزوايا المتبادلة": ("وجاجها ثلاثة أرباع وجاج الخريطة "
                                  "الواحدة، لأن الوصلة بين خريطتين "
                                  "أضعف من الوصلة داخل الخريطة."),
            "التقبّل": "من باب الكرامات عند ابن أبي الرجال والبيروني.",
            "الموازين": ("رتبة مئوية مقابل ٦٠٠٠ زوج عشوائي — "
                         "انظر tools/calibrate_synastry.py."),
            "المركّبة": "طريقة معاصرة (نقاط المنتصف)، لا أصل لها في التراث.",
            "دافيسون": "خريطة حقيقية للحظة ومكان المنتصف.",
        },
    }
