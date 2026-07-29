# -*- coding: utf-8 -*-
"""
السهام العربية (Arabic Parts / Lots).

السهم نقطة محسوبة لا جِرم لها، تُستخرج بجمع موضعين وطرح ثالث:
        السهم = (أ + ب) − ج
وأشهرها سهم السعادة، وقد أفرد له البيروني في «التفهيم» بابًا، وعدّ نحو
سبعة وتسعين سهمًا. أخذنا منها ما له أثر بيّن في القراءة.

قاعدة الليل والنهار: أكثر السهام تنقلب صيغتها إن كانت الولادة ليلًا،
فيصير المطروح مجموعًا والمجموع مطروحًا.
"""
from __future__ import annotations

# (المفتاح، الاسم، أ، ب، ج، هل ينقلب ليلًا؟، الشرح)
# الرموز: ASC الطالع، MC وسط السماء، والباقي أسماء الأجرام،
# و«H2».. رؤوس البيوت، و«R2».. حكّامها.
LOTS = [
    ("fortune", "سهم السعادة", "ASC", "القمر", "الشمس", True,
     "موضع الرزق والتوفيق وحظّ البدن. أوّل ما يُنظر إليه بعد النيّرين والطالع، "
     "ويدلّ على الباب الذي يأتي منه اليُسر."),
    ("spirit", "سهم الغيب", "ASC", "الشمس", "القمر", True,
     "موضع العقل والإرادة والمصير المختار. سهم السعادة ما يُساق إليك، "
     "وسهم الغيب ما تسوق إليه نفسك."),
    ("eros", "سهم المحبّة", "ASC", "الزهرة", "الشمس", True,
     "موضع الميل والرغبة وما يتعلّق به القلب."),
    ("necessity", "سهم الضرورة", "ASC", "عطارد", "الشمس", True,
     "موضع ما يُضطرّ إليه المرء من الأمور، والخصومات والقيود."),
    ("courage", "سهم الشجاعة", "ASC", "المريخ", "زحل", True,
     "موضع الإقدام والبأس وما يُواجَه به الخطر."),
    ("victory", "سهم النصر", "ASC", "المشتري", "زحل", True,
     "موضع التوفيق والظفر والعون من حيث لا يُحتسب."),
    ("nemesis", "سهم النكبة", "ASC", "زحل", "الشمس", True,
     "موضع العثرة والخفاء وما يُخشى منه."),
    ("father", "سهم الأب", "ASC", "الشمس", "زحل", True,
     "دلالة الأب وحاله وما يصل منه."),
    ("mother", "سهم الأم", "ASC", "القمر", "الزهرة", True,
     "دلالة الأمّ وحالها وما يصل منها."),
    ("siblings", "سهم الإخوة", "ASC", "زحل", "المشتري", False,
     "دلالة الإخوة والأخوات وعددهم وحالهم."),
    ("children", "سهم الأولاد", "ASC", "المشتري", "زحل", False,
     "دلالة النسل والذرّية."),
    ("marriage_m", "سهم الزواج للرجل", "ASC", "الزهرة", "زحل", False,
     "دلالة الزوجة والاقتران في خريطة الرجل."),
    ("marriage_f", "سهم الزواج للمرأة", "ASC", "زحل", "الزهرة", False,
     "دلالة الزوج والاقتران في خريطة المرأة."),
    ("illness", "سهم المرض", "ASC", "المريخ", "زحل", False,
     "موضع العلّة والضعف في البدن."),
    ("wealth", "سهم المال", "ASC", "H2", "R2", False,
     "موضع الكسب والمقتنى."),
    ("travel", "سهم السفر", "ASC", "H9", "R9", False,
     "موضع الأسفار البعيدة والاغتراب."),
    ("work", "سهم العمل", "ASC", "MC", "الشمس", False,
     "موضع الصنعة والمرتبة وما يُعرف به المرء بين الناس."),
    ("death", "سهم الموت", "ASC", "H8", "القمر", False,
     "موضع الانقضاء والتحوّل. يُنظر فيه بتحفّظ شديد، ولا يُقطع منه بأجل."),
]

CORE = {"fortune", "spirit", "eros", "victory", "work", "father", "mother"}


def _value(token: str, bodies: dict, angles: dict, cusps: list, rulers: dict):
    if token == "ASC":
        return angles["الطالع"]
    if token == "MC":
        return angles["وسط السماء"]
    if token.startswith("H") and token[1:].isdigit():
        return cusps[int(token[1:]) - 1]
    if token.startswith("R") and token[1:].isdigit():
        return rulers.get(int(token[1:]))
    return bodies.get(token)


def compute(bodies: dict, angles: dict, cusps: list, rulers: dict,
            is_day: bool, only_core: bool = False) -> list:
    """
    bodies: {اسم الجرم: طوله}
    angles: {"الطالع": درجة, "وسط السماء": درجة}
    cusps:  قائمة رؤوس البيوت الاثني عشر
    rulers: {رقم البيت: طول حاكمه}
    """
    out = []
    for key, name, a, b, c, flips, note in LOTS:
        if only_core and key not in CORE:
            continue
        va = _value(a, bodies, angles, cusps, rulers)
        vb = _value(b, bodies, angles, cusps, rulers)
        vc = _value(c, bodies, angles, cusps, rulers)
        if None in (va, vb, vc):
            continue
        if flips and not is_day:
            vb, vc = vc, vb
        lon = (va + vb - vc) % 360.0
        out.append({
            "key": key, "name": name, "lon": lon, "note": note,
            "formula": f"الطالع + {b} − {c}" if not (flips and not is_day)
                       else f"الطالع + {c} − {b}",
            "core": key in CORE,
        })
    return out
