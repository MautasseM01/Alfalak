# -*- coding: utf-8 -*-
"""
الكرامات الخمس والأَلْمُطَن — مقياس قوّة الكوكب في الخريطة.

خمس درجات من الكرامة، أعلاها البيت وأدناها الوجه:
  البيت    (Domicile)   الكوكب في داره، أقوى ما يكون          ٥ درجات
  الشرف    (Exaltation) في مقام تكريمه                        ٤
  المثلثة  (Triplicity) في عنصره، بحسب ليل الميلاد أو نهاره    ٣
  الحدّ     (Term)       في قسمه من البرج، بالحدود المصرية      ٢
  الوجه    (Face)       في عشره من البرج، بالترتيب الكلداني     ١

ويقابلها ضَعْفان:
  الوبال   (Detriment)  في مقابل بيته                          −٥
  الهبوط   (Fall)       في مقابل شرفه                          −٤
والغريب (Peregrine) هو الذي لا كرامة له ولا ضعف.

الأَلْمُطَن هو صاحب أعلى مجموع في موضع بعينه — وأَلْمُطَن الخريطة كلها
هو الكوكب الذي يحكمها، ومفتاح قراءة صاحبها.
"""
from __future__ import annotations

SIGNS = ["الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء",
         "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت"]

PLANETS7 = ["الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل"]

# ── البيوت ───────────────────────────────────────────────────────
DOMICILE = {
    "الحمل": "المريخ", "الثور": "الزهرة", "الجوزاء": "عطارد", "السرطان": "القمر",
    "الأسد": "الشمس", "العذراء": "عطارد", "الميزان": "الزهرة", "العقرب": "المريخ",
    "القوس": "المشتري", "الجدي": "زحل", "الدلو": "زحل", "الحوت": "المشتري",
}

# ── الشرف ودرجته ─────────────────────────────────────────────────
EXALT = {          # الكوكب: (البرج، درجة الشرف)
    "الشمس": ("الحمل", 19), "القمر": ("الثور", 3), "عطارد": ("العذراء", 15),
    "الزهرة": ("الحوت", 27), "المريخ": ("الجدي", 28), "المشتري": ("السرطان", 15),
    "زحل": ("الميزان", 21), "الرأس": ("الجوزاء", 3),
}
EXALT_SIGN = {v[0]: k for k, v in EXALT.items() if k in PLANETS7}

# ── المثلثات (على مذهب دوروثيوس، وهو الذي عليه العرب) ────────────
# العنصر: (حاكم النهار، حاكم الليل، الشريك)
TRIPLICITY = {
    "ناري":  ("الشمس", "المشتري", "زحل"),
    "ترابي": ("الزهرة", "القمر", "المريخ"),
    "هوائي": ("زحل", "عطارد", "المشتري"),
    "مائي":  ("الزهرة", "المريخ", "القمر"),
}
ELEMENT = {"الحمل": "ناري", "الأسد": "ناري", "القوس": "ناري",
           "الثور": "ترابي", "العذراء": "ترابي", "الجدي": "ترابي",
           "الجوزاء": "هوائي", "الميزان": "هوائي", "الدلو": "هوائي",
           "السرطان": "مائي", "العقرب": "مائي", "الحوت": "مائي"}

# ── الحدود المصرية: (الكوكب، الدرجة التي ينتهي عندها حدّه) ────────
TERMS = {
    "الحمل":   [("المشتري", 6), ("الزهرة", 12), ("عطارد", 20), ("المريخ", 25), ("زحل", 30)],
    "الثور":   [("الزهرة", 8), ("عطارد", 14), ("المشتري", 22), ("زحل", 27), ("المريخ", 30)],
    "الجوزاء": [("عطارد", 6), ("المشتري", 12), ("الزهرة", 17), ("المريخ", 24), ("زحل", 30)],
    "السرطان": [("المريخ", 7), ("الزهرة", 13), ("عطارد", 19), ("المشتري", 26), ("زحل", 30)],
    "الأسد":   [("المشتري", 6), ("الزهرة", 11), ("زحل", 18), ("عطارد", 24), ("المريخ", 30)],
    "العذراء": [("عطارد", 7), ("الزهرة", 17), ("المشتري", 21), ("المريخ", 28), ("زحل", 30)],
    "الميزان": [("زحل", 6), ("عطارد", 14), ("المشتري", 21), ("الزهرة", 28), ("المريخ", 30)],
    "العقرب":  [("المريخ", 7), ("الزهرة", 11), ("عطارد", 19), ("المشتري", 24), ("زحل", 30)],
    "القوس":   [("المشتري", 12), ("الزهرة", 17), ("عطارد", 21), ("زحل", 26), ("المريخ", 30)],
    "الجدي":   [("عطارد", 7), ("المشتري", 14), ("الزهرة", 22), ("زحل", 26), ("المريخ", 30)],
    "الدلو":   [("عطارد", 7), ("الزهرة", 13), ("المشتري", 20), ("المريخ", 25), ("زحل", 30)],
    "الحوت":   [("الزهرة", 12), ("المشتري", 16), ("عطارد", 19), ("المريخ", 28), ("زحل", 30)],
}

# ── الوجوه: كل برج ثلاثة وجوه، على الترتيب الكلداني ──────────────
_CHALDEAN = ["المريخ", "الشمس", "الزهرة", "عطارد", "القمر", "زحل", "المشتري"]
FACES = {s: [_CHALDEAN[(i * 3 + j) % 7] for j in range(3)] for i, s in enumerate(SIGNS)}

SCORE = {"البيت": 5, "الشرف": 4, "المثلثة": 3, "الحدّ": 2, "الوجه": 1,
         "الوبال": -5, "الهبوط": -4, "الغريب": -5}

DIGNITY_NOTE = {
    "البيت": "في داره، يتصرّف بحرّية وقوّة",
    "الشرف": "في مقام تكريمه، ظاهر النفع مرفوع القدر",
    "المثلثة": "في عنصره، مُعان مسنود",
    "الحدّ": "في حدّه، له فيه أثر خاصّ",
    "الوجه": "في وجهه، أضعف الكرامات وأقلّها أثرًا",
    "الوبال": "في وباله، غريب عن داره ضيّق الحيلة",
    "الهبوط": "في هبوطه، مغمور القدر يحتاج جهدًا مضاعفًا",
    "الغريب": "غريب لا كرامة له في موضعه، أثره تابع لغيره",
}


# ── أدوات ────────────────────────────────────────────────────────
def sign_of(lon: float) -> str:
    return SIGNS[int(lon // 30) % 12]


def term_ruler(lon: float) -> str:
    within = lon % 30
    for planet, end in TERMS[sign_of(lon)]:
        if within < end:
            return planet
    return TERMS[sign_of(lon)][-1][0]


def face_ruler(lon: float) -> str:
    return FACES[sign_of(lon)][min(2, int((lon % 30) // 10))]


def triplicity_rulers(lon: float, is_day: bool):
    day_r, night_r, part = TRIPLICITY[ELEMENT[sign_of(lon)]]
    primary = day_r if is_day else night_r
    return primary, part


def detriment_of(sign: str) -> str:
    return DOMICILE[SIGNS[(SIGNS.index(sign) + 6) % 12]]


def fall_of(sign: str):
    opposite = SIGNS[(SIGNS.index(sign) + 6) % 12]
    return EXALT_SIGN.get(opposite)


# ── تقييم كوكب في موضعه ─────────────────────────────────────────
def evaluate(planet: str, lon: float, is_day: bool) -> dict:
    """يُرجع كرامات الكوكب في موضعه ومجموع قوّته."""
    sign = sign_of(lon)
    held, score = [], 0

    if DOMICILE[sign] == planet:
        held.append("البيت"); score += SCORE["البيت"]
    if planet in EXALT and EXALT[planet][0] == sign:
        held.append("الشرف"); score += SCORE["الشرف"]
        if abs((lon % 30) - EXALT[planet][1]) < 1:
            held.append("درجة الشرف")
    primary, part = triplicity_rulers(lon, is_day)
    if planet == primary:
        held.append("المثلثة"); score += SCORE["المثلثة"]
    elif planet == part:
        held.append("شريك المثلثة"); score += 1
    if term_ruler(lon) == planet:
        held.append("الحدّ"); score += SCORE["الحدّ"]
    if face_ruler(lon) == planet:
        held.append("الوجه"); score += SCORE["الوجه"]

    debilities = []
    if detriment_of(sign) == planet:
        debilities.append("الوبال"); score += SCORE["الوبال"]
    if fall_of(sign) == planet:
        debilities.append("الهبوط"); score += SCORE["الهبوط"]

    peregrine = not held and not debilities
    if peregrine:
        score += SCORE["الغريب"]

    all_states = held + debilities + (["الغريب"] if peregrine else [])
    return {
        "planet": planet, "sign": sign,
        "dignities": held, "debilities": debilities,
        "peregrine": peregrine, "score": score,
        "states": all_states,
        "summary": "، ".join(all_states) if all_states else "—",
        "note": DIGNITY_NOTE.get(all_states[0], "") if all_states else "",
        "rulers": {
            "البيت": DOMICILE[sign],
            "الشرف": EXALT_SIGN.get(sign),
            "المثلثة": primary,
            "الحدّ": term_ruler(lon),
            "الوجه": face_ruler(lon),
        },
    }


def almuten_of_place(lon: float, is_day: bool) -> dict:
    """أَلْمُطَن موضع بعينه: صاحب أعلى مجموع فيه."""
    sign = sign_of(lon)
    tally = {}
    def add(p, n):
        if p:
            tally[p] = tally.get(p, 0) + n
    add(DOMICILE[sign], 5)
    add(EXALT_SIGN.get(sign), 4)
    primary, part = triplicity_rulers(lon, is_day)
    add(primary, 3)
    add(part, 1)
    add(term_ruler(lon), 2)
    add(face_ruler(lon), 1)
    ranked = sorted(tally.items(), key=lambda x: -x[1])
    return {"winner": ranked[0][0], "score": ranked[0][1],
            "table": [{"planet": p, "score": s} for p, s in ranked]}


def almuten_of_chart(bodies: list, angles: dict, is_day: bool,
                     part_of_fortune: float | None = None) -> dict:
    """
    أَلْمُطَن الخريطة كلها — على طريقة ابن أبي الرجال:
    يُجمع لكل كوكب ما يملكه من كرامات في المواضع الخمسة الحاكمة
    (الشمس، القمر، الطالع، سهم السعادة، اجتماع أو استقبال ما قبل الميلاد)،
    ويُزاد له من حاله في الخريطة.
    """
    places = []
    sun = next((b for b in bodies if b["name"] == "الشمس"), None)
    moon = next((b for b in bodies if b["name"] == "القمر"), None)
    if sun:
        places.append(("الشمس", sun["lon"]))
    if moon:
        places.append(("القمر", moon["lon"]))
    places.append(("الطالع", angles["الطالع"] if isinstance(angles["الطالع"], float)
                   else angles["الطالع"]["lon"]))
    mc = angles["وسط السماء"]
    places.append(("وسط السماء", mc if isinstance(mc, float) else mc["lon"]))
    if part_of_fortune is not None:
        places.append(("سهم السعادة", part_of_fortune))

    tally = {p: 0 for p in PLANETS7}
    detail = []
    for label, lon in places:
        a = almuten_of_place(lon, is_day)
        row = {"place": label, "sign": sign_of(lon), "winner": a["winner"], "shares": {}}
        for item in a["table"]:
            tally[item["planet"]] = tally.get(item["planet"], 0) + item["score"]
            row["shares"][item["planet"]] = item["score"]
        detail.append(row)

    # حال الكوكب نفسه في الخريطة يُزاد إلى مجموعه
    own = {}
    for b in bodies:
        if b["name"] in PLANETS7:
            e = evaluate(b["name"], b["lon"], is_day)
            own[b["name"]] = e
            tally[b["name"]] = tally.get(b["name"], 0) + max(0, e["score"])

    ranked = sorted(tally.items(), key=lambda x: -x[1])
    return {
        "winner": ranked[0][0], "score": ranked[0][1],
        "ranking": [{"planet": p, "score": s} for p, s in ranked],
        "places": detail,
        "own_state": {k: {"summary": v["summary"], "score": v["score"]} for k, v in own.items()},
    }


def is_day_chart(sun_lon: float, asc_lon: float) -> bool:
    """النهار إن كانت الشمس فوق الأفق — أي في البيوت من السابع إلى الثاني عشر."""
    rel = (sun_lon - asc_lon) % 360.0
    return rel >= 180.0
