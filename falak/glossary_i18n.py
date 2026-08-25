# -*- coding: utf-8 -*-
"""
المعجم بالإنجليزية والفرنسية.

──────────────────────────────────────────────────────────────────
**لماذا ملفٌّ على حدة، ولماذا يجوز أن يكون ناقصًا؟**

المعجم ١٢٦ مصطلحًا وأربعةَ عشر ألف حرف. ولو شُرط تمامُه قبل
وصله لبقي معطَّلًا شهورًا، **ولبقيت التلميحات عربيّةً فوق نصٍّ
إنجليزيّ** — وهو ما شُكي منه.

فالبنية هنا **تحتمل النقص بلا خلط**: `terms_for()` تردّ المصطلح
المترجَم إن وُجد، **وتُسقطه** إن لم يوجد. ولا تردّ عربيًّا في
صفحةٍ إنجليزية.

وإسقاطُه يعني أن الكلمة لا تُوسَم ولا يظهر لها تلميح — **وذلك
خيرٌ من تلميحٍ بلسانٍ آخر**، وهو ما اتُّفق عليه: «الخلطُ أسوأ
من العربيّة الصافية».

ومقياسُ الصفحة (`tools/i18n_seen.js`) يعدّ ما بقي، فينزل الرقم
بكل دفعةٍ تُضاف. **والرقم هو الحكم، لا هذا الملفّ.**

ــ كيف تُضاف دفعة ــ

  EN["الطالع"] = ("Ascendant", "The sign and degree rising …")
  FR["الطالع"] = ("Ascendant", "Le signe et le degré se levant …")

الأوّل اسمُ المصطلح كما يُعرَض، والثاني شرحُه.
"""
from __future__ import annotations

EN: dict[str, tuple[str, str]] = {
    # ــ الأوتاد ــ
    "الطالع": ("Ascendant",
               "The sign and degree rising on the eastern horizon at the "
               "moment of birth. It signifies the body, the appearance, "
               "and your manner of entering life. It moves one degree "
               "every four minutes, which is why an exact birth time "
               "matters."),
    "وسط السماء": ("Midheaven",
                   "The highest point the Sun reaches that day, and the "
                   "cusp of the tenth house. It signifies rank, work, and "
                   "what you are known for among people."),
    "الغارب": ("Descendant",
               "Opposite the Ascendant, and the cusp of the seventh "
               "house. It signifies the partner, the adversary, and "
               "everyone you face."),
    "وتد الأرض": ("Imum Coeli",
                  "Opposite the Midheaven, and the cusp of the fourth "
                  "house. It signifies origin, home, and what is hidden "
                  "of you."),
}

FR: dict[str, tuple[str, str]] = {
    "الطالع": ("Ascendant",
               "Le signe et le degré se levant à l'horizon oriental à "
               "l'instant de la naissance. Il signifie le corps, "
               "l'apparence et votre manière d'entrer dans la vie. Il "
               "avance d'un degré toutes les quatre minutes : de là "
               "l'exigence d'une heure de naissance exacte."),
    "وسط السماء": ("Milieu du Ciel",
                   "Le point le plus haut atteint par le Soleil ce "
                   "jour-là, et la cuspide de la dixième maison. Il "
                   "signifie le rang, le travail, et ce par quoi l'on "
                   "vous connaît."),
    "الغارب": ("Descendant",
               "Opposé à l'Ascendant, cuspide de la septième maison. Il "
               "signifie le partenaire, l'adversaire, et tous ceux que "
               "vous affrontez."),
    "وتد الأرض": ("Fond du Ciel",
                  "Opposé au Milieu du Ciel, cuspide de la quatrième "
                  "maison. Il signifie l'origine, le foyer, et ce qui "
                  "est caché de vous."),
}

TABLES = {"en": EN, "fr": FR}


def terms_for(lang: str, arabic: dict[str, str]) -> dict[str, str]:
    """
    المعجم بلسان الصفحة.

    **وما لم يُترجَم يُسقَط، ولا يُردّ عربيًّا.** فالكلمة
    الإنجليزية لا تُوسَم، ولا يظهر عليها تلميحٌ بلسانٍ ثانٍ.
    """
    if lang not in TABLES:
        return arabic
    return {name: text for (name, text) in TABLES[lang].values()}


def coverage(lang: str, arabic: dict[str, str]) -> tuple[int, int]:
    """المُترجَم من المعجم وكلُّه — يُطبع في `/api/health`."""
    return len(TABLES.get(lang, {})), len(arabic)
