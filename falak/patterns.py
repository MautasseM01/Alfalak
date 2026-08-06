# -*- coding: utf-8 -*-
"""
الأشكال الزاوية — الأنماط الهندسية التي تصنعها الكواكب مجتمعةً.

الزاوية المفردة تصف علاقة بين اثنين، أما الشكل فيصف بنية كاملة في الخريطة
تتصرّف كوحدة واحدة. ثلاثة كواكب أو أكثر تنتظم في هيئة لها دلالة تفوق
مجموع أجزائها.
"""
from __future__ import annotations

from itertools import combinations


def _wrap180(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def sep(a: float, b: float) -> float:
    return abs(_wrap180(a - b))


def _has(aspects, a, b, angle, tol=0.0):
    """هل بين الجرمين زاوية بالدرجة المطلوبة ضمن ما رُصد؟"""
    for x in aspects:
        if x["angle"] == angle and {x["a"], x["b"]} == {a, b}:
            return x
    return None


PATTERN_NOTES = {
    "المثلّث الكبير": "ثلاثة أجرام يفصل بين كلٍّ منها تثليث، فتنتظم مثلّثًا متساوي الأضلاع "
                     "في عنصر واحد. دلالته سيولة وموهبة تأتي بلا كدّ — وخطره أن ما يأتي "
                     "بلا كدّ قد لا يُستثمر.",
    "الصليب المتقابل": "أربعة أجرام في تربيعات متتالية وتقابلين متقاطعين. ضغط من أربع جهات "
                      "لا مهرب منه، ومعه طاقة عمل هائلة لمن احتمله. من أشقّ الأشكال وأكثرها إنتاجًا.",
    "التربيع المزدوج": "جرمان متقابلان يُربّعهما ثالث. الثالث هو موضع التوتّر ومفتاح الحلّ معًا: "
                      "ما يقابله في الخريطة هو المخرج.",
    "الإصبع": "جرمان بينهما تسديس، وكلاهما يُسدّس السادس من الآخر بزاوية مائة وخمسين. "
             "يُسمّى إصبع القدر: ضغط خفيّ يدفع نحو موضع بعينه دفعًا لا يُقاوَم.",
    "الطائرة الورقية": "مثلّث كبير أضيف إليه جرم يقابل أحد أضلاعه ويُسدّس الآخرين. "
                      "يعطي المثلّث الكبير ما ينقصه: مخرجًا عمليًّا ودافعًا للتحقّق.",
    "المستطيل الصوفي": "تقابلان متوازيان تربطهما تسديسات وتثليثات. بنية مغلقة متوازنة، "
                      "فيها قدرة على التوفيق بين المتناقضات.",
    "الكومة": "ثلاثة أجرام فأكثر مجتمعة في برج واحد أو بيت واحد. تركيز شديد للطاقة "
             "في باب واحد من أبواب الحياة، يغلب على سائر الخريطة.",
    "قبضة اليد": "جرمان بينهما تسديس أو تثليث، يجمعهما ثالث بزاويتين حادّتين. "
                "شكل حادّ الاتّجاه، صاحبه ذو غاية واحدة يمضي إليها.",
}


def detect(bodies: list, aspects: list, cusps: list | None = None) -> list:
    """
    bodies: [{name, lon, sign, house}]
    aspects: مخرجات محرّك الزوايا [{a, b, angle, orb, ...}]
    """
    found = []
    by_name = {b["name"]: b for b in bodies}
    # كل الأجرام المُمرَّرة تدخل في الأشكال — المُستدعي هو الذي ينتقي.
    # (كان الفلتر هنا يُسقط الكواكب الخارجية، فيضيع المثلّث الكبير
    #  الذي يقوم بين كوكب شخصي وأورانوس وبلوتو.)
    names = [b["name"] for b in bodies]

    # ── الكومة: ثلاثة فأكثر في برج واحد أو بيت واحد ──
    #
    # **خلل كان قائمًا**: نبحث بالبرج ثم بالبيت ونُضيف ما نجد. وفي
    # نظام البيوت الكاملة **يوافق البيتُ البرجَ دائمًا** — فالكومة
    # الواحدة تُبلَّغ مرّتين بالأعضاء أنفسهم، مرّةً «برج الجدي»
    # ومرّةً «بيت ٧». وحارس التفرّد أسفلَ الدالّة يُميّز بـ`where`
    # فيراهما اثنتين. وقد ظهر ذلك للزائر نصًّا مكرَّرًا حرفًا بحرف.
    #
    # والعلاج أن تُجمَع الكومة بأعضائها لا بموضعها، ثم يُذكر لها
    # الموضعان معًا إن توافقا — فهي كومة واحدة في الحقيقة.
    stelliums: dict[tuple, dict] = {}
    for key, label in (("sign", "برج"), ("house", "بيت")):
        groups: dict = {}
        for b in bodies:
            if b.get(key) is None:
                continue
            groups.setdefault(b[key], []).append(b["name"])
        for where, members in groups.items():
            if len(members) < 3:
                continue
            k = tuple(sorted(members))
            rec = stelliums.setdefault(k, {"members": members, "places": []})
            rec["places"].append(f"{label} {where}")

    for rec in stelliums.values():
        found.append({
            "name": "الكومة", "members": rec["members"],
            # «الجدي (وهو البيت السابع)» أوضح من سطرين متطابقين
            "where": (rec["places"][0] if len(rec["places"]) == 1
                      else f"{rec['places'][0]} (وهو {rec['places'][1]})"),
            "places": rec["places"],
            "note": PATTERN_NOTES["الكومة"],
            "strength": min(1.0, len(rec["members"]) / 5),
        })

    trip = list(combinations(names, 3))

    # ── المثلّث الكبير ──
    #
    # والعلّة نفسها: مثلّثٌ أحدُ أركانه كوكبان مقترنان يخرج **مرّتين**،
    # مرّةً بهذا ومرّةً بذاك، فيقرأ الزائر نصّين متطابقين بنسبة ٩٣٪.
    # فالقاعدة الجامعة في هذا الملفّ كلّه: **المقترنان ركنٌ واحد**.
    grand_trines = []
    _gt_raw: dict = {}
    for a, b, c in trip:
        if _has(aspects, a, b, 120) and _has(aspects, b, c, 120) and _has(aspects, a, c, 120):
            grand_trines.append((a, b, c))
            _gt_raw.setdefault(by_name[a].get("element") or "", set()).update((a, b, c))

    for el, bodies_in in _gt_raw.items():
        parent = {x: x for x in bodies_in}

        def find(x, _p=parent):
            while _p[x] != x:
                _p[x] = _p[_p[x]]
                x = _p[x]
            return x

        for x, y in combinations(sorted(bodies_in), 2):
            if _has(aspects, x, y, 0):
                parent[find(y)] = find(x)
        corners: dict = {}
        for b in sorted(bodies_in):
            corners.setdefault(find(b), []).append(b)
        found.append({"name": "المثلّث الكبير",
                      "members": [b for k in corners.values() for b in k],
                      "corners": list(corners.values()),
                      "where": f"عنصر {el}" if el else "",
                      "note": PATTERN_NOTES["المثلّث الكبير"], "strength": .9})

    # ── التربيع المزدوج ──
    #
    # **وهنا العلّة نفسها في ثوب آخر.** كنّا نُبلّغ كل ثلاثيّ على
    # حدة، فإذا كان في الخريطة كوكبان مقترنان — كأورانوس ونبتون في
    # الجدي — خرج التربيعُ الواحد **مرّتين**، مرّةً بأورانوس ومرّةً
    # بنبتون، والباقي واحد. فيقرأ الزائر نصّين متطابقين بنسبة ٩٣٪
    # ويظنّهما شكلين، وهما شكل واحد أحد أضلاعه اقتران.
    #
    # والصواب أن يُجمَع المقترنان في ضلع واحد — فهما في الحقيقة
    # يعملان معًا، وهذا معنى الاقتران.
    t_squares = {}
    for a, b, c in trip:
        for opp, apex in (((a, b), c), ((a, c), b), ((b, c), a)):
            if _has(aspects, opp[0], opp[1], 180) \
               and _has(aspects, opp[0], apex, 90) and _has(aspects, opp[1], apex, 90):
                t_squares[tuple(sorted([opp[0], opp[1], apex]))] = (opp, apex)

    # الأضلاع تُستخرج بتجميع المقترنين لا بموازنة الثلاثيّات واحدًا
    # واحدًا — فالموازنة أوّل مرّة أخرجت نبتون مرّتين في قائمة واحدة.
    # والقاعدة صريحة: **لكل رأسٍ ضلعان، وكلّ مقترنَين ضلعٌ واحد.**
    by_apex: dict[str, set] = {}
    for (opp, apex) in t_squares.values():
        by_apex.setdefault(apex, set()).update(opp)

    for apex, side_bodies in by_apex.items():
        parent = {b: b for b in side_bodies}

        def find(x, _p=parent):
            while _p[x] != x:
                _p[x] = _p[_p[x]]
                x = _p[x]
            return x

        for x, y in combinations(sorted(side_bodies), 2):
            if _has(aspects, x, y, 0):
                parent[find(y)] = find(x)

        legs: dict = {}
        for b in sorted(side_bodies):
            legs.setdefault(find(b), []).append(b)
        members = [b for leg in legs.values() for b in leg]
        found.append({"name": "التربيع المزدوج",
                      "members": members + [apex],
                      "legs": list(legs.values()),
                      "where": f"رأسه {apex} في {by_name[apex]['sign']}",
                      "note": PATTERN_NOTES["التربيع المزدوج"], "strength": .85})

    # ── الصليب المتقابل ──
    for quad in combinations(names, 4):
        opps = [p for p in combinations(quad, 2) if _has(aspects, p[0], p[1], 180)]
        sqs = [p for p in combinations(quad, 2) if _has(aspects, p[0], p[1], 90)]
        if len(opps) >= 2 and len(sqs) >= 4:
            found.append({"name": "الصليب المتقابل", "members": list(quad),
                          "where": by_name[quad[0]].get("mode", ""),
                          "note": PATTERN_NOTES["الصليب المتقابل"], "strength": 1.0})

    # ── الإصبع ──
    for a, b, c in trip:
        for base, apex in (((a, b), c), ((a, c), b), ((b, c), a)):
            if _has(aspects, base[0], base[1], 60) \
               and _has(aspects, base[0], apex, 150) and _has(aspects, base[1], apex, 150):
                found.append({"name": "الإصبع", "members": [base[0], base[1], apex],
                              "where": f"رأسه {apex} في {by_name[apex]['sign']}",
                              "note": PATTERN_NOTES["الإصبع"], "strength": .8})

    # ── الطائرة الورقية ──
    for gt in grand_trines:
        for d in names:
            if d in gt:
                continue
            opp = [x for x in gt if _has(aspects, x, d, 180)]
            sxt = [x for x in gt if _has(aspects, x, d, 60)]
            if len(opp) == 1 and len(sxt) == 2:
                found.append({"name": "الطائرة الورقية", "members": list(gt) + [d],
                              "where": f"ذيلها {d}",
                              "note": PATTERN_NOTES["الطائرة الورقية"], "strength": .95})

    # ── المستطيل الصوفي ──
    for quad in combinations(names, 4):
        opps = [p for p in combinations(quad, 2) if _has(aspects, p[0], p[1], 180)]
        sxt = [p for p in combinations(quad, 2) if _has(aspects, p[0], p[1], 60)]
        trn = [p for p in combinations(quad, 2) if _has(aspects, p[0], p[1], 120)]
        if len(opps) == 2 and len(sxt) >= 2 and len(trn) >= 2:
            found.append({"name": "المستطيل الصوفي", "members": list(quad), "where": "",
                          "note": PATTERN_NOTES["المستطيل الصوفي"], "strength": .75})

    # إزالة التكرار
    uniq, seen = [], set()
    for f in found:
        k = (f["name"], tuple(sorted(f["members"])), f.get("where", ""))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(f)
    uniq.sort(key=lambda x: -x["strength"])
    return uniq
