# -*- coding: utf-8 -*-
"""
المسائل — خريطة اللحظة التي وقع فيها السؤال.

هذا أعرق أبواب الصناعة عند العرب وأشدّها انضباطًا. مبناه أن السؤال
إذا اضطرم في صدر صاحبه فسأل، كانت السماء في تلك اللحظة صورةً لجوابه.
ولا يُحكَم فيه بالمزاج، بل بقواعد منصوصة:

**أوّلًا: الاعتبارات قبل الحكم.** لا يُحكم في كلّ خريطة. فإن كان
الطالع في أوّل درجة أو آخرها، أو القمر خاليَ المسار، أو زحلٌ في
البيت السابع — تُردّ المسألة ولا يُتكلَّف لها جواب. وهذا أشرف ما في
الباب: أن يعرف صاحبُه متى يسكت.

**ثانيًا: الدليلان.** للسائل ربُّ الطالع، ومعه القمر دائمًا.
وللمسؤول عنه ربُّ البيت الذي يخصّ مسألته: السابع للشريك، والعاشر
للعمل، والثاني للمال، وهكذا.

**ثالثًا: التمام.** أيقع بين الدليلين اتّصال قبل أن يخرج أحدهما من
برجه؟ فإن وقع تمّ الأمر. وإن لم يقع فقد يتمّ بـ**نقل النور** — كوكب
سريع يأخذ من هذا ويُعطي ذاك — أو بـ**جمع النور** — بطيء يجمع
نظرهما. ويمنعه **المنع** أو **الرجوع**.

المصادر: «التفهيم» للبيروني، و«البارع» لابن أبي الرجال، وعليهما
جرى عمل من جاء بعدهما.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import chart, dignities as dig, ephem
from .chart import SIGNS, _wrap180, dms

UTC = timezone.utc

# ══════════════════════════════════════════════════════════════
# ١ — أبواب المسائل: كل سؤال وبيته
# ══════════════════════════════════════════════════════════════
QUESTIONS = {
    "هل أُشفى من مرضي؟": dict(house=6, note="السادس للمرض، والأوّل للبدن."),
    "هل يعود الغائب؟": dict(house=9, note="التاسع للسفر البعيد، والثالث للقريب."),
    "أين الشيء الضائع؟": dict(house=2, note="الثاني للمال والمتاع المملوك."),
    "هل أتزوّج فلانًا؟": dict(house=7, note="السابع لكل شريك: زوج أو خصم."),
    "هل يعود من هجرني؟": dict(house=7, note="السابع للطرف الآخر."),
    "هل أنال هذه الوظيفة؟": dict(house=10, note="العاشر للمرتبة والعمل."),
    "هل يُقبَل طلبي؟": dict(house=10, note="العاشر لمن بيده القرار."),
    "هل أربح في هذه التجارة؟": dict(house=2, note="الثاني لمالك أنت."),
    "هل أشتري هذا العقار؟": dict(house=4, note="الرابع للأرض والدار."),
    "هل أنتقل إلى بيت جديد؟": dict(house=4, note="الرابع للسكن والجذر."),
    "هل أنجح في الامتحان؟": dict(house=9, note="التاسع للعلم العالي، والثالث للدراسة القريبة."),
    "هل أُرزق ولدًا؟": dict(house=5, note="الخامس للولد."),
    "هل يصدُقني هذا الشخص؟": dict(house=7, note="السابع للطرف المقابل."),
    "هل أسافر؟": dict(house=9, note="التاسع للسفر البعيد."),
    "هل أُقرِض فلانًا؟": dict(house=8, note="الثامن لمال الغير وما يُشارَك."),
    "هل يُوفَّى لي ديني؟": dict(house=8, note="الثامن لمال الغير — ومنه دينك عنده."),
    "هل هذا الصديق صادق؟": dict(house=11, note="الحادي عشر للأصدقاء والرجاء."),
    "من يكيد لي؟": dict(house=12, note="الثاني عشر للعدوّ الخفيّ."),
    "هل أُشارك فلانًا في عمل؟": dict(house=7, note="السابع للشريك."),
    "هل أترك عملي؟": dict(house=10, note="العاشر للمهنة، وانظر السادس للعمل اليومي."),
    "هل تُقبَل دعواي في المحكمة؟": dict(house=7, note="السابع للخصم، والعاشر للقاضي."),
    "هل يُشفى قريبي؟": dict(house=6, note="انظر بيت المريض ثم سادسه منه."),
    "أين وضعتُ الشيء؟": dict(house=4, note="الرابع للمكان المخبوء."),
    "هل أُقدِم على هذا القرار؟": dict(house=1, note="الأوّل للسائل نفسه ومصلحته."),
}

# ══════════════════════════════════════════════════════════════
# ٢ — الاعتبارات قبل الحكم
# ══════════════════════════════════════════════════════════════
# الطريق المحترق: من ١٥° الميزان إلى ١٥° العقرب — بين شرف زحل
# وهبوط القمر. القدماء يعدّونه موضع اضطراب لا يُحكَم فيه.
VIA_COMBUSTA = (195.0, 225.0)


def considerations(c: dict) -> list[dict]:
    """
    ما يمنع الحكم أو يُضعفه. لكلٍّ درجة: «مانع» تُردّ به المسألة،
    و«تحذير» يُقرأ معه الجواب بحذر.

    وهذا الباب هو ما يفصل المسائل عن التخمين: أن يُقال «لا جواب
    في هذه اللحظة، أعِد السؤال حين يشتدّ عليك» بدل تلفيق جواب.
    """
    out = []
    asc = c["angles"]["الطالع"]
    deg = asc["lon"] % 30.0
    by = {b["name"]: b for b in c["bodies"]}
    moon = by["القمر"]
    cusps = [h["lon"] for h in c["houses"]["cusps"]]

    if deg < 3.0:
        out.append({"kind": "مانع", "name": "الطالع في أوّل درجات البرج",
                    "note": (f"الطالع في {deg:.1f}° من {asc['sign']}. "
                             "الأمر لم ينضج بعد، والسؤال سابق لأوانه. "
                             "أعِد السؤال بعد حين.")})
    elif deg > 27.0:
        out.append({"kind": "مانع", "name": "الطالع في آخر درجات البرج",
                    "note": (f"الطالع في {deg:.1f}° من {asc['sign']}. "
                             "الأمر إمّا انقضى وإمّا خرج من يدك، "
                             "فلا حكم فيه.")})

    # القمر خالي المسار: لا يتّصل بشيء قبل خروجه من برجه
    voc = _moon_void(c)
    if voc["void"]:
        out.append({"kind": "مانع", "name": "القمر خالي المسار",
                    "note": ("لا يتّصل القمر بكوكب قبل خروجه من "
                             f"{moon['sign']}. وحكم القدماء فيه: "
                             "«لا يكون شيء» — أي لا يقع الأمر ولا "
                             "ضدّه، وإنما يبقى على حاله.")})

    if VIA_COMBUSTA[0] <= moon["lon"] < VIA_COMBUSTA[1]:
        out.append({"kind": "تحذير", "name": "القمر في الطريق المحترق",
                    "note": ("القمر بين ١٥° الميزان و١٥° العقرب — "
                             "موضع اضطراب عند القدماء، بين شرف زحل "
                             "وهبوط القمر. يُقرأ الجواب بحذر.")})

    sat = by.get("زحل")
    if sat:
        h = sat["house"]
        if h == 7:
            out.append({"kind": "تحذير", "name": "زحل في البيت السابع",
                        "note": ("البيت السابع بيت المنجّم في هذا الباب، "
                                 "وزحل فيه علامة خطأ في الحكم لا في "
                                 "الأمر. تُقرأ الخريطة بتواضع.")})
        if h == 1:
            out.append({"kind": "تحذير", "name": "زحل في البيت الأوّل",
                        "note": ("زحل على السائل: الأمر أثقل ممّا يبدو، "
                                 "وفيه تأخير أو مانع لم يُذكر في السؤال.")})

    # القمر في هبوطه أو وباله
    md = dig.evaluate("القمر", moon["lon"], is_day=(c["sect"] == "نهارية"))
    if md.get("peregrine") or "هبوط" in (moon.get("dignity") or ""):
        out.append({"kind": "تحذير", "name": "القمر ضعيف",
                    "note": (f"القمر في {moon['sign']} "
                             f"({moon.get('dignity') or 'غريب'}) — "
                             "شاهد ضعيف، فلا يُبنى عليه وحده.")})

    if not out:
        out.append({"kind": "سليم", "name": "لا مانع من الحكم",
                    "note": ("الطالع في وسط برجه، والقمر متّصل، "
                             "ولا زحل على أوتاد الحكم. الخريطة "
                             "صالحة للنظر.")})
    return out


def _moon_void(c: dict) -> dict:
    """أيتّصل القمر بكوكب قبل خروجه من برجه؟ ومَن هو؟"""
    when = datetime.fromisoformat(c["when_utc"])
    moon_lon = next(b["lon"] for b in c["bodies"] if b["name"] == "القمر")
    end_of_sign = (int(moon_lon // 30) + 1) * 30.0
    to_go = (end_of_sign - moon_lon) % 30.0
    hours = to_go / (13.2 / 24.0) / 1.0        # تقدير أوّلي بسرعة وسطى
    horizon = when + timedelta(hours=min(72, hours * 1.4 + 2))

    others = ["الشمس", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"]
    hits = []
    for name in others:
        for asp_name, angle in (("اقتران", 0), ("تسديس", 60), ("تربيع", 90),
                                ("تثليث", 120), ("تقابل", 180)):
            t = _perfect_time("القمر", name, angle, when, horizon)
            if t:
                # لا بدّ أن يتمّ قبل خروج القمر من برجه
                if int(ephem.lon_of("القمر", t) // 30) == int(moon_lon // 30):
                    hits.append({"planet": name, "aspect": asp_name,
                                 "when": t.isoformat(),
                                 "hours": round((t - when).total_seconds() / 3600, 1)})
    hits.sort(key=lambda x: x["hours"])
    return {"void": not hits, "next": hits[0] if hits else None,
            "all": hits[:4], "sign_exit_hours": round(to_go / 0.55, 1)}


# ══════════════════════════════════════════════════════════════
# ٣ — التمام: أيقع الاتّصال قبل خروج الدليل من برجه؟
# ══════════════════════════════════════════════════════════════
ASPECTS5 = [("اقتران", 0), ("تسديس", 60), ("تربيع", 90),
            ("تثليث", 120), ("تقابل", 180)]

SPEED_ORDER = ["القمر", "عطارد", "الزهرة", "الشمس", "المريخ", "المشتري", "زحل"]


def _sep(a: str, b: str, angle: int, t: datetime) -> float:
    """الفارق عن الزاوية المطلوبة، بإشارة تصلح للتنصيف."""
    return _wrap180(abs(_wrap180(ephem.lon_of(a, t) - ephem.lon_of(b, t))) - angle)


def _perfect_time(a: str, b: str, angle: int, start: datetime,
                  end: datetime) -> datetime | None:
    """لحظة تمام الاتّصال بين a و b على هذه الزاوية، إن وقع."""
    step = timedelta(hours=2 if a == "القمر" or b == "القمر" else 12)
    t, prev = start, _sep(a, b, angle, start)
    if abs(prev) > 60:                       # بعيد جدًّا، لا فائدة من المسح
        pass
    while t < end:
        nxt = min(t + step, end)
        cur = _sep(a, b, angle, nxt)
        if prev == 0:
            return t
        if prev * cur < 0 and abs(prev - cur) < 60:
            return ephem._bisect(lambda x: _sep(a, b, angle, x), t, nxt)
        t, prev = nxt, cur
    return None


def _sign_exit(name: str, start: datetime, end: datetime) -> datetime | None:
    """متى يخرج الكوكب من برجه الحالي؟ (وهو حدّ صلاحية الاتّصال)."""
    s0 = int(ephem.lon_of(name, start) // 30)
    t, step = start, timedelta(hours=6)
    while t < end:
        nxt = min(t + step, end)
        if int(ephem.lon_of(name, nxt) // 30) != s0:
            return ephem._bisect(
                lambda x: 1.0 if int(ephem.lon_of(name, x) // 30) == s0 else -1.0,
                t, nxt)
        t = nxt
    return None


def perfection(c: dict, sig_q: str, sig_t: str, horizon_days: int = 45) -> dict:
    """
    أيتمّ الأمر؟ بالاتّصال المباشر، أو بنقل النور، أو بجمعه.

    الشرط في كلٍّ واحد: أن يقع التمام **قبل أن يخرج الدليل الأسرع
    من برجه**. فإن خرج فقد انفكّ الأمر، ولو كانت الزاوية قريبة.
    """
    when = datetime.fromisoformat(c["when_utc"])
    end = when + timedelta(days=horizon_days)
    out = {"perfects": False, "how": None, "detail": [], "when": None}

    if sig_q == sig_t:
        out.update(perfects=True, how="الدليل واحد",
                   detail=[{"kind": "الدليل واحد",
                            "note": (f"دليل السائل ودليل المسؤول عنه كوكب "
                                     f"واحد ({sig_q}). وهذا في الباب علامة "
                                     "أن الأمر بيدك أنت، لا بيد غيرك.")}])
        return out

    limit_q = _sign_exit(sig_q, when, end) or end
    limit_t = _sign_exit(sig_t, when, end) or end
    limit = min(limit_q, limit_t)

    # ── الاتّصال المباشر ──
    # نجمع كلّ الزوايا الممكنة ثم نأخذ **أسبقها وقوعًا**، لا أوّلها
    # في ترتيب الجدول: الذي يقع أوّلًا هو الذي يحكم.
    valid = []
    for name, angle in ASPECTS5:
        t = _perfect_time(sig_q, sig_t, angle, when, end)
        if not t:
            continue
        ok = t <= limit
        days = round((t - when).total_seconds() / 86400, 1)
        rec = _reception(c, sig_q, sig_t)
        out["detail"].append({
            "kind": "اتّصال مباشر", "aspect": name, "when": t.isoformat(),
            "days": days, "in_time": ok, "reception": rec,
            "note": (f"يتّصل {sig_q} بـ{sig_t} اتّصال {name} بعد {days} يومًا"
                     + ("." if ok else
                        " — لكن بعد خروج أحدهما من برجه، فلا يُعتدّ به.")),
        })
        if ok:
            valid.append((t, name, rec))
    if valid:
        valid.sort(key=lambda x: x[0])
        t, name, rec = valid[0]
        out.update(perfects=True, how=f"اتّصال مباشر ({name})",
                   when=t.isoformat(), aspect=name, reception=rec)
    out["detail"].sort(key=lambda x: x.get("days", 1e9))

    # ── نقل النور ──
    #
    # الشرط الذي أهملته أوّل صياغة: لا يكفي أن يكون الناقل قد فارق
    # هذا يومًا ما وسيلقى ذاك يومًا ما. لا بدّ أن يكون **الآن** في
    # وجاج الاتّصالين معًا: منفصلًا عن الأوّل ولمّا يخرج من وجاجه،
    # ومقبلًا على الثاني وقد دخل فيه. وبدون هذا الشرط يقع «نقل نور»
    # في كل خريطة تقريبًا، فيفقد الباب معناه.
    NOQL_ORB = 6.0
    if not out["perfects"]:
        for mid in SPEED_ORDER:
            if mid in (sig_q, sig_t):
                continue
            if not _faster(mid, sig_q, sig_t):
                continue          # الناقل لا بدّ أن يكون أسرع من الدليلين
            sep_a = _closest_aspect(mid, sig_q, when)
            app_b = _closest_aspect(mid, sig_t, when)
            if not sep_a or not app_b:
                continue
            if sep_a["orb"] > NOQL_ORB or app_b["orb"] > NOQL_ORB:
                continue
            if sep_a["applying"] or not app_b["applying"]:
                continue          # لا بدّ: منفصل عن الأوّل مقبل على الثاني
            t2 = _perfect_time(mid, sig_t, app_b["angle"], when, end)
            if not t2 or t2 > (_sign_exit(mid, when, end) or end):
                continue
            days = round((t2 - when).total_seconds() / 86400, 1)
            out["detail"].append({
                "kind": "نقل النور", "by": mid, "when": t2.isoformat(),
                "days": days,
                "note": (f"{mid} انفصل عن {sig_q} ({sep_a['name']}، وجاج "
                         f"{sep_a['orb']:.1f}°) وهو مقبل على {sig_t} "
                         f"({app_b['name']}) بعد {days} يومًا: ينقل النور "
                         "بينهما. يتمّ الأمر بواسطة — شخص يتوسّط، "
                         "أو خبر ينتقل.")})
            out.update(perfects=True, how=f"نقل النور بـ{mid}",
                       when=t2.isoformat())
            break

    # ── جمع النور ──
    if not out["perfects"]:
        for coll in reversed(SPEED_ORDER):
            if coll in (sig_q, sig_t):
                continue
            if _faster(coll, sig_q, sig_t):
                continue          # الجامع لا بدّ أن يكون أبطأ من الدليلين
            a1 = _closest_aspect(sig_q, coll, when)
            a2 = _closest_aspect(sig_t, coll, when)
            if not a1 or not a2:
                continue
            if a1["orb"] > NOQL_ORB or a2["orb"] > NOQL_ORB:
                continue
            if not (a1["applying"] and a2["applying"]):
                continue          # لا بدّ أن يُقبلا عليه كلاهما
            ta = _perfect_time(sig_q, coll, a1["angle"], when, end)
            tb = _perfect_time(sig_t, coll, a2["angle"], when, end)
            if not ta or not tb:
                continue
            last = max(ta, tb)
            out["detail"].append({
                "kind": "جمع النور", "by": coll, "when": last.isoformat(),
                "days": round((last - when).total_seconds() / 86400, 1),
                "note": (f"{sig_q} و{sig_t} يُقبلان معًا على {coll} فيجمع "
                         "نورهما. يتمّ الأمر بجهة أثقل من الطرفين: "
                         "سلطة، أو عقد، أو مؤسّسة.")})
            out.update(perfects=True, how=f"جمع النور بـ{coll}",
                       when=last.isoformat())
            break

    if not out["perfects"] and not out["detail"]:
        out["detail"].append({
            "kind": "لا اتّصال",
            "note": (f"لا يقع بين {sig_q} و{sig_t} اتّصال قبل خروج "
                     "أحدهما من برجه، ولا ناقل ولا جامع. "
                     "والحكم: لا يتمّ الأمر على حاله هذا.")})
    return out



def _speed(name: str, t: datetime) -> float:
    return abs(ephem.speed_of(name, t))


def _faster(who: str, a: str, b: str) -> bool:
    """أهو أسرع من الاثنين؟ يُقاس بالترتيب المعروف لا بالحساب اللحظي."""
    if who not in SPEED_ORDER:
        return False
    i = SPEED_ORDER.index(who)
    ia = SPEED_ORDER.index(a) if a in SPEED_ORDER else 99
    ib = SPEED_ORDER.index(b) if b in SPEED_ORDER else 99
    return i < ia and i < ib


def _closest_aspect(a: str, b: str, t: datetime) -> dict | None:
    """
    أقرب زاوية كبرى بين الجرمين الآن: اسمها ووجاجها، وأمُقبلة هي
    أم مُدبِرة. وهذا ما يفصل «انفصل عنه» عن «سيلقاه بعد شهر».
    """
    la, lb = ephem.lon_of(a, t), ephem.lon_of(b, t)
    sep = abs(_wrap180(la - lb))
    best = None
    for name, angle in ASPECTS5:
        orb = abs(sep - angle)
        if best is None or orb < best["orb"]:
            best = {"name": name, "angle": angle, "orb": orb}
    if best is None:
        return None
    later = t + timedelta(hours=6)
    sep2 = abs(_wrap180(ephem.lon_of(a, later) - ephem.lon_of(b, later)))
    best["applying"] = abs(sep2 - best["angle"]) < best["orb"]
    return best


def _last_separation(a: str, b: str, when: datetime,
                     back_days: int = 20) -> datetime | None:
    """آخر اتّصال انفصل عنه a مع b — شرط نقل النور."""
    start = when - timedelta(days=back_days)
    best = None
    for _, angle in ASPECTS5:
        t = _perfect_time(a, b, angle, start, when)
        if t and (best is None or t > best):
            best = t
    return best


def _reception(c: dict, a: str, b: str) -> dict | None:
    """أيقبل كلٌّ صاحبَه؟ التقبّل يُقوّي الاتّصال ويُليّن العسير منه."""
    by = {x["name"]: x for x in c["bodies"]}
    if a not in by or b not in by:
        return None
    sa, sb = by[a]["sign"], by[b]["sign"]
    mutual_dom = dig.DOMICILE[sa] == b and dig.DOMICILE[sb] == a
    mutual_ex = (dig.EXALT.get(b, (None,))[0] == sa
                 and dig.EXALT.get(a, (None,))[0] == sb)
    if mutual_dom:
        return {"kind": "تقبّل تامّ",
                "note": (f"{a} في {sa} دارِ {b}، و{b} في {sb} دارِ {a}. "
                         "يقبل كلٌّ صاحبه، فيتمّ الأمر برضا الطرفين "
                         "ولو كانت الزاوية عسيرة.")}
    if mutual_ex:
        return {"kind": "تقبّل بالشرف",
                "note": f"{a} في شرف {b}، و{b} في شرف {a}. يُكرم كلٌّ الآخر."}
    if dig.DOMICILE[sa] == b:
        return {"kind": "تقبّل من طرف",
                "note": (f"{a} في {sa} دارِ {b}: يحتاجه ولا يحتاجه. "
                         "يتمّ الأمر، وفيه انحياز لصاحب الدار.")}
    if dig.DOMICILE[sb] == a:
        return {"kind": "تقبّل من طرف",
                "note": (f"{b} في {sb} دارِ {a}: الحاجة من الطرف الآخر، "
                         "وأنت صاحب الدار.")}
    return None


# ══════════════════════════════════════════════════════════════
# ٤ — الحكم
# ══════════════════════════════════════════════════════════════
def judge(c: dict, house: int, question: str = "",
          horizon_days: int = 45) -> dict:
    """الحكم الكامل في مسألة: الاعتبارات، ثم الدليلان، ثم التمام."""
    by = {b["name"]: b for b in c["bodies"]}
    cusps = c["houses"]["cusps"]

    asc_sign = c["angles"]["الطالع"]["sign"]
    sig_q = dig.DOMICILE[asc_sign]
    house_sign = SIGNS[int(cusps[house - 1]["lon"] // 30)]
    sig_t = dig.DOMICILE[house_sign]

    cons = considerations(c)
    blocked = [x for x in cons if x["kind"] == "مانع"]

    perf = perfection(c, sig_q, sig_t, horizon_days) if not blocked else {
        "perfects": False, "how": None, "detail": [], "when": None}

    voc = _moon_void(c)

    # حال الدليلين: الكرامة والرجوع والاحتراق
    def state(name):
        b = by.get(name)
        if not b:
            return None
        combust = (name not in ("الشمس",)
                   and abs(_wrap180(b["lon"] - by["الشمس"]["lon"])) < 8.5)
        return {"name": name, "sign": b["sign"], "house": b["house"],
                "text": b["text"], "retro": b["retro"],
                "dignity": b.get("dignity"),
                "score": b.get("dignity_score"),
                "combust": combust,
                "note": _state_note(b, combust)}

    sq, st = state(sig_q), state(sig_t)

    if blocked:
        verdict = "تُردّ المسألة"
        summary = ("لا يُحكَم في هذه الخريطة: " +
                   "، ".join(x["name"] for x in blocked) +
                   ". وهذا حكمٌ بذاته لا عجز: قال القدماء إن السؤال "
                   "إن لم ينضج في صدر صاحبه لم تُجب عنه السماء. "
                   "أعِد السؤال حين يشتدّ عليك الأمر فعلًا.")
    elif perf["perfects"]:
        asp = perf.get("aspect")
        rec = perf.get("reception")
        if perf["how"] == "الدليل واحد":
            # ربّ الطالع هو نفسه ربّ بيت المسألة. ليس تمامًا بواسطة
            # ولا بعُسر: هو أن الأمر بيدك أنت.
            verdict = "بيدك أنت"
            summary = ("دليل السائل ودليل المسؤول عنه كوكب واحد "
                       f"({sig_q}) — لأن برج الطالع وبرج البيت "
                       f"{house} صاحبهما واحد. وحكم الباب في هذا: "
                       "لا مانع خارجيّ ولا مُعين خارجيّ. الأمر موقوف "
                       "على قرارك، فانظر في حال هذا الكوكب: "
                       "إن كان قويًّا مضيتَ، وإن كان ضعيفًا فتردّدك "
                       "هو العائق لا الظرف.")
        elif asp is None:
            # نقل النور أو جمعه: يتمّ بواسطة، لا بعُسر. والخلط بينهما
            # يظلم الباب: الواسطة ليست مشقّة.
            verdict = "يتمّ بواسطة"
            summary = (f"يتمّ الأمر — {perf['how']}. لا يقع بين الدليلين "
                       "اتّصال مباشر، وإنما يتمّ بثالث: شخص يتوسّط، "
                       "أو خبر ينتقل، أو جهة تجمع الطرفين. "
                       "فاطلبه من بابه لا مباشرةً.")
        elif asp in ("تسديس", "تثليث") or (asp == "اقتران" and rec):
            verdict = "يتمّ"
            summary = (f"يتمّ الأمر — {perf['how']}." +
                       (f" ومعه {rec['kind']}، وهو يُليّن ما عسُر."
                        if rec else " والزاوية ميسِّرة."))
        elif asp == "اقتران":
            verdict = "يتمّ"
            summary = ("يتمّ الأمر — اقتران الدليلين، وهو أقوى "
                       "الاتّصالات وأسرعها وقوعًا.")
        elif rec:
            verdict = "يتمّ بعد جهد"
            summary = (f"يتمّ الأمر — {perf['how']}. الزاوية عسيرة، "
                       f"لكن {rec['kind']} بين الدليلين يُليّنها: "
                       "يقع المطلوب بعد مفاوضة أو تنازل.")
        else:
            verdict = "يتمّ بعُسر"
            summary = (f"يتمّ الأمر لكن بمشقّة — {perf['how']}، "
                       "وهي زاوية عسيرة بلا تقبّل يُليّنها. "
                       "يقع المطلوب بعد جهد أو خصومة.")
    else:
        verdict = "لا يتمّ"
        summary = ("لا يقع بين الدليلين اتّصال قبل خروج أحدهما من برجه، "
                   "ولا ناقل ولا جامع. والحكم أن الأمر لا يتمّ "
                   "على حاله هذا — وقد يتغيّر إن تغيّرت أسبابه.")

    return {
        "question": question,
        "house": house,
        "house_sign": house_sign,
        "asc_sign": asc_sign,
        "significators": {
            "السائل": {"ruler": sig_q, "why": f"ربّ الطالع ({asc_sign})",
                       "state": sq},
            "المسؤول عنه": {"ruler": sig_t,
                            "why": f"ربّ البيت {house} ({house_sign})",
                            "state": st},
            "القمر": {"ruler": "القمر",
                      "why": "شاهد في كل مسألة، ودليل السائل الثاني",
                      "state": state("القمر")},
        },
        "considerations": cons,
        "blocked": bool(blocked),
        "perfection": perf,
        "moon": voc,
        "verdict": verdict,
        "summary": summary,
        "limits": (
            "هذا باب رمزيّ من التراث، لا وسيلة معرفة بالغيب ولا بديل "
            "عن الفحص والاستشارة. لا يُبنى عليه قرار طبّي ولا مالي "
            "ولا قانوني. وأصدق ما فيه أنه يُجبرك على صياغة سؤالك "
            "صياغة دقيقة — وأكثر الحيرة تنحلّ بذلك وحده."
        ),
    }


def _state_note(b: dict, combust: bool) -> str:
    bits = []
    d = b.get("dignity")
    if d and d != "—":
        if any(k in d for k in ("بيت", "شرف", "مثلثة")):
            bits.append(f"في كرامته ({d}) — قويّ نافذ")
        elif any(k in d for k in ("وبال", "هبوط")):
            bits.append(f"في ضعفه ({d}) — لا يُنفّذ ما يعِد")
        else:
            bits.append(d)
    else:
        bits.append("غريب لا كرامة له — ضعيف الحال")
    if b["retro"]:
        bits.append("راجع: تردّد، أو رجوع عن أمر، أو عودة شيء ضاع")
    if combust:
        bits.append("محترق تحت شعاع الشمس: مغلوب، أو أمرٌ خفيّ لا يظهر")
    return "، و".join(bits) + "."
