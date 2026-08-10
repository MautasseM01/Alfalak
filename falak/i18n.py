# -*- coding: utf-8 -*-
"""
طبقة الترجمة — والمفتاحُ هو النصُّ العربيّ نفسه.

──────────────────────────────────────────────────────────────────
**لماذا المفتاح عربيّ لا رمزيّ؟**

الطريقة المعتادة أن يُوضَع لكل نصٍّ مفتاحٌ رمزيّ (`nav.chart`)
ثم يُبدَّل النصّ في كل صفحة بذلك المفتاح. وذلك يعني **تعديل ستّ
عشرة صفحة بيدٍ**، وأن الصفحة بلا جافاسكربت تعرض مفاتيح لا كلامًا،
وأن كل نصٍّ جديد يحتاج خطوتين.

فالمفتاح هنا **النصّ العربي كما هو مكتوب في الصفحة**:

  · **لا تُعدَّل الصفحات أصلًا** — تبقى عربيّةً في مصدرها،
    وهي أصلُ المشروع ولغتُه.
  · **ومن جاء بلا جافاسكربت رأى عربيّةً صحيحة** لا مفاتيح.
  · **وما لم يُترجَم يبقى عربيًّا من نفسه** — فلا فراغ ولا
    «missing key»، بل تدرّجٌ سليم.
  · **والقاموس هو ما يحتاجه المترجم بعينه**: عمودٌ عربيّ
    وعمودان يُملآن. لا شيفرة فيه.

وثمنُه معلوم: العبارة الواحدة في موضعين مختلفين تُترجَم ترجمةً
واحدة. وهذا مقبولٌ في **أثاث الواجهة** — القوائم والأزرار
والعناوين — وهو المُترجَم هنا.

──────────────────────────────────────────────────────────────────
**ما يُترجَم وما لا يُترجَم — وقياسُه**

قِيس النصّ العربيّ في المشروع فكان **٢٠٨ آلاف حرف** تحتاج
ترجمة (عدا التعليقات والتوثيق):

    نصوص القراءة والتفسير   ١١١٬٥٥٠   ٥٤٪
    مصطلحات وجداول المحرّك    ٥٥٬٧٨٧   ٢٧٪
    أثاث الواجهة              ٤٠٬٩٦٩   ٢٠٪

**والمُترجَم هنا هو الثالث وحده.** فيصير الموقع مسلوكًا بثلاث
لغات: القوائم والحقول والأزرار ورؤوس الجداول. أمّا نصوص القراءة
فتبقى عربيّة **ويُقال ذلك صراحةً** لمن اختار لغةً أخرى — ولا
تُمرَّر على مترجمٍ آليّ، لأن المصطلح الفلكيّ التراثيّ يُفسَد
بسهولة، وجودةُ النصّ هي رأس مال هذا الموقع.
"""
from __future__ import annotations

LANGS = {
    "ar": {"name": "العربية", "native": "العربية", "dir": "rtl"},
    "en": {"name": "الإنجليزية", "native": "English", "dir": "ltr"},
    "fr": {"name": "الفرنسية", "native": "Français", "dir": "ltr"},
}
DEFAULT = "ar"

# ما يُقال لمن اختار لغةً غير العربية
PARTIAL = {
    "en": "Readings and interpretations are still in Arabic. The site's "
          "menus, forms and tables are translated; the astrological texts "
          "are not — they are traditional Arabic sources, and machine "
          "translation would damage them.",
    "fr": "Les lectures et interprétations restent en arabe. Les menus, "
          "formulaires et tableaux sont traduits ; les textes astrologiques "
          "ne le sont pas — ce sont des sources arabes traditionnelles, "
          "qu'une traduction automatique abîmerait.",
}

# ══════════════════════════════════════════════════════════════════
# القاموس — العربيّة مفتاحًا
#
# ولا يُترجَم هنا إلّا **أثاث الواجهة**. وما نقص بقي عربيًّا،
# و`coverage()` تقول كم بقي بالرقم لا بالظنّ.
# ══════════════════════════════════════════════════════════════════
UI = {
    # ــ الهوية والتصفّح ــ
    "الفَلَك": ("Al-Falak", "Al-Falak"),
    "أدوات فلكية عربية": ("Arabic astrology tools", "Outils d'astrologie arabe"),
    "الفَلَك — أدوات فلكية عربية": ("Al-Falak — Arabic astrology tools",
                                     "Al-Falak — outils d'astrologie arabe"),
    "تخطَّ إلى المحتوى": ("Skip to content", "Aller au contenu"),
    "الرئيسة": ("Home", "Accueil"),
    "خريطة الميلاد": ("Natal chart", "Thème natal"),
    "النشرة اليومية": ("Daily bulletin", "Bulletin quotidien"),
    "النشرة الشهرية": ("Monthly bulletin", "Bulletin mensuel"),
    "الشهرية": ("Monthly", "Mensuel"),
    "ساعات الكواكب": ("Planetary hours", "Heures planétaires"),
    "الاختيارات": ("Electional", "Élections"),
    "متى أفعل؟": ("When should I?", "Quand agir ?"),
    "المسائل": ("Horary", "Horaire"),
    "الصيني": ("Chinese", "Chinois"),
    "الهندي": ("Vedic", "Védique"),
    "التوافق": ("Synastry", "Synastrie"),
    "أرباب الأزمنة": ("Time lords", "Maîtres du temps"),
    "أملاح المولد": ("Birth salts", "Sels de naissance"),
    "خرائط الأرض": ("Astrocartography", "Astrocartographie"),
    "خرائط المشاهير": ("Famous charts", "Thèmes célèbres"),
    "مواقع الكواكب": ("Ephemeris", "Éphémérides"),
    "الواجهة البرمجية": ("API", "API"),
    "الواجهة البرمجية والتقويم": ("API and calendar", "API et calendrier"),
    "تعلّم": ("Learn", "Apprendre"),

    # ــ حقول الميلاد ــ
    "الاسم": ("Name", "Nom"),
    "الاسم (اختياري)": ("Name (optional)", "Nom (facultatif)"),
    "اختياري": ("optional", "facultatif"),
    "تاريخ الميلاد": ("Date of birth", "Date de naissance"),
    "ساعة الميلاد": ("Time of birth", "Heure de naissance"),
    "مكان الميلاد": ("Place of birth", "Lieu de naissance"),
    "مدينة الميلاد": ("Birth city", "Ville de naissance"),
    "المدينة": ("City", "Ville"),
    "التاريخ": ("Date", "Date"),
    "الساعة": ("Time", "Heure"),
    "اليوم": ("Today", "Aujourd'hui"),
    "الغرض": ("Purpose", "Objet"),
    "نظام البيوت": ("House system", "Système de maisons"),
    "قارن بنظام": ("Compare with", "Comparer avec"),
    "بلا مقارنة": ("No comparison", "Sans comparaison"),
    "لتمييز الخريطة": ("to label the chart", "pour identifier le thème"),
    "لتمييز الخريطة عند الحفظ": ("to label the saved chart",
                                  "pour identifier le thème enregistré"),

    # ــ أفعال ــ
    "احسب": ("Calculate", "Calculer"),
    "احسب الخريطة": ("Calculate chart", "Calculer le thème"),
    "ارسم": ("Draw", "Tracer"),
    "حفظ": ("Save", "Enregistrer"),
    "حفظ ميلادي": ("Save my birth data", "Enregistrer ma naissance"),
    "✓ حُفظ": ("✓ Saved", "✓ Enregistré"),
    "اعرض النشرة": ("Show bulletin", "Afficher le bulletin"),
    "اعرض الجدول": ("Show table", "Afficher le tableau"),
    "أنشئ الرابط": ("Create link", "Créer le lien"),
    "نزّل الملفّ": ("Download file", "Télécharger le fichier"),
    "بالحساب العربي": ("Arabic system", "Système arabe"),
    "بالحساب الهندي": ("Vedic system", "Système védique"),
    "بالحساب الصيني": ("Chinese system", "Système chinois"),
    "← عودة إلى الأعلام": ("← Back to figures", "← Retour aux personnalités"),
    "ابحث في الأعلام": ("Search figures", "Rechercher une personnalité"),

    # ــ حالات ــ
    "… أُحمّل": ("… loading", "… chargement"),
    "… أحسب": ("… calculating", "… calcul en cours"),
    "… أحسب العبور": ("… calculating transits", "… calcul des transits"),
    "… أحسب الخطوط": ("… calculating lines", "… calcul des lignes"),

    # ــ مُدد ــ
    "شهر": ("One month", "Un mois"),
    "شهران": ("Two months", "Deux mois"),
    "ثلاثة أشهر": ("Three months", "Trois mois"),
    "لكم يومًا": ("For how many days", "Pour combien de jours"),

    # ــ رؤوس الجداول وعناوين متكرّرة ــ
    "الجِرم": ("Body", "Astre"),
    "البرج": ("Sign", "Signe"),
    "الدرجة": ("Degree", "Degré"),
    "البيت": ("House", "Maison"),
    "الزاوية": ("Aspect", "Aspect"),
    "الزوايا": ("Aspects", "Aspects"),
    "النوع": ("Type", "Type"),
    "الأوّل": ("First", "Premier"),
    "الثاني": ("Second", "Second"),
    "على": ("to", "sur"),
    "فرقُها": ("Orb", "Orbe"),
    "صيغته": ("Formula", "Formule"),
    "السهم": ("Lot", "Part"),
    "السهام": ("Arabic lots", "Parts arabes"),
    "الكواكب": ("Planets", "Planètes"),
    "البيوت": ("Houses", "Maisons"),
    "المنازل القمرية": ("Lunar mansions", "Manoirs lunaires"),
    "النجوم الثابتة": ("Fixed stars", "Étoiles fixes"),
    "الأشكال الزاوية": ("Chart patterns", "Figures du thème"),
    "الغالب في الخريطة": ("Chart dominants", "Dominantes du thème"),
    "الزوايا الخفيّة": ("Hidden aspects", "Aspects cachés"),
    "الموازاة بالمَيْل": ("Declination parallels", "Parallèles de déclinaison"),
    "الأنطسيا": ("Antiscia", "Antisces"),
    "ما يمرّ عليك الآن": ("What is passing over you now",
                          "Ce qui vous traverse en ce moment"),
    "ما يُقبِل عليك": ("Approaching", "À venir"),
    "وما انقضى قريبًا": ("Recently passed", "Récemment passé"),
    "تسييرُ عمرك — يومٌ لسنة": ("Your progressions — a day for a year",
                                 "Vos progressions — un jour pour une année"),
    "القوس الشمسي": ("Solar arc", "Arc solaire"),
    "الأعلام": ("Figures", "Personnalités"),

    # ══════════════════════════════════════════════════════════
    # مفردات الصناعة — وهي **أنفعُ ما يُترجَم**
    #
    # قد يُقال: أليست هذه «متنًا» لا «أثاثًا»؟ والجواب لا.
    # الجداولُ كلُّها مبنيّةٌ على هذه الخمسين كلمة: أسماء
    # الأجرام والبروج والزوايا والبيوت. فمن قرأها بالإنجليزية
    # **قرأ الجدول كلَّه**، ومن لم يقرأها لم ينتفع بشيء.
    # وهي محدودةٌ معدودة، فترجمتُها يقينٌ لا اجتهاد — بخلاف
    # نصوص القراءة التي يُفسدها المترجم الآليّ.
    # ══════════════════════════════════════════════════════════
    "الشمس": ("Sun", "Soleil"),
    "القمر": ("Moon", "Lune"),
    "عطارد": ("Mercury", "Mercure"),
    "الزهرة": ("Venus", "Vénus"),
    "المريخ": ("Mars", "Mars"),
    "المشتري": ("Jupiter", "Jupiter"),
    "زحل": ("Saturn", "Saturne"),
    "أورانوس": ("Uranus", "Uranus"),
    "نبتون": ("Neptune", "Neptune"),
    "بلوتو": ("Pluto", "Pluton"),
    "خيرون": ("Chiron", "Chiron"),
    "ليليث": ("Lilith", "Lilith"),
    "الرأس": ("North Node", "Nœud Nord"),
    "الذنب": ("South Node", "Nœud Sud"),
    "الأجرام": ("Bodies", "Astres"),

    "الحمل": ("Aries", "Bélier"),
    "الثور": ("Taurus", "Taureau"),
    "الجوزاء": ("Gemini", "Gémeaux"),
    "السرطان": ("Cancer", "Cancer"),
    "الأسد": ("Leo", "Lion"),
    "العذراء": ("Virgo", "Vierge"),
    "الميزان": ("Libra", "Balance"),
    "العقرب": ("Scorpio", "Scorpion"),
    "القوس": ("Sagittarius", "Sagittaire"),
    "الجدي": ("Capricorn", "Capricorne"),
    "الدلو": ("Aquarius", "Verseau"),
    "الحوت": ("Pisces", "Poissons"),

    "الطالع": ("Ascendant", "Ascendant"),
    "الغارب": ("Descendant", "Descendant"),
    "وسط السماء": ("Midheaven", "Milieu du Ciel"),
    "وتد الأرض": ("Imum Coeli", "Fond du Ciel"),

    "اقتران": ("Conjunction", "Conjonction"),
    "مقابلة": ("Opposition", "Opposition"),
    "تربيع": ("Square", "Carré"),
    "تثليث": ("Trine", "Trigone"),
    "تسديس": ("Sextile", "Sextile"),
    "إيجابية": ("harmonious", "harmonieux"),
    "سلبية": ("tense", "tendu"),
    "مُقبِلة": ("applying", "appliquant"),
    "مُدبِرة": ("separating", "séparant"),
    "الوجاج": ("Orb", "Orbe"),
    "يتمّ": ("exact on", "exact le"),
    "منزلة القمر": ("Lunar mansion", "Manoir lunaire"),
    "الأَلْمُطَن": ("Almuten", "Almuten"),
    "الطائفة": ("Sect", "Secte"),

    # ــ زمن ــ
    "الأحد": ("Sunday", "Dimanche"),
    "الاثنين": ("Monday", "Lundi"),
    "الثلاثاء": ("Tuesday", "Mardi"),
    "الأربعاء": ("Wednesday", "Mercredi"),
    "الخميس": ("Thursday", "Jeudi"),
    "الجمعة": ("Friday", "Vendredi"),
    "السبت": ("Saturday", "Samedi"),
    "السنة": ("Year", "Année"),
    "الشهر": ("Month", "Mois"),
    "الآن": ("Now", "Maintenant"),
    "من تاريخ": ("From", "À partir du"),

    # ــ ألفاظ متفرّقة في الواجهة ــ
    "الكلّ": ("All", "Tout"),
    "أفضلها": ("Best", "Les meilleurs"),
    "أنثى": ("Female", "Féminin"),
    "ذكر": ("Male", "Masculin"),
    "أين أنت الآن؟": ("Where are you now?", "Où êtes-vous ?"),
    "مكان مولدك": ("Your birthplace", "Votre lieu de naissance"),
    "ساعة مولدك": ("Your birth time", "Votre heure de naissance"),
    "تاريخ السؤال": ("Date of question", "Date de la question"),
    "الخريطة الهندية": ("Vedic chart", "Thème védique"),
    "الأعمدة الصينية": ("Chinese pillars", "Piliers chinois"),
    "عرض النصّ الخام": ("Show raw text", "Afficher le texte brut"),
    "إخفاء النصّ الخام": ("Hide raw text", "Masquer le texte brut"),
    "أغلق قائمة التصفّح": ("Close navigation", "Fermer la navigation"),
    "أقسام الخريطة": ("Chart sections", "Sections du thème"),
    "أحداث الشهر كلّه": ("The whole month's events",
                          "Les événements du mois"),
    "أيّ فترة تعيش الآن": ("Which period you are living",
                            "La période que vous vivez"),
    "أفضل الأيام لغرض": ("Best days for a purpose",
                          "Meilleurs jours selon l'objet"),
    "(راجع)": ("(retrograde)", "(rétrograde)"),
    "· البيت": ("· House", "· Maison"),
    "· يولياني": ("· Julian", "· julien"),
    "(بالتقويم اليولياني)": ("(Julian calendar)", "(calendrier julien)"),

    # ــ ذيل الصفحة ــ
    "alfalak.vercel.app · الحساب بمكتبة Swiss Ephemeris":
        ("alfalak.vercel.app · computed with the Swiss Ephemeris",
         "alfalak.vercel.app · calculé avec la Swiss Ephemeris"),
    "المواقع محسوبة بمكتبة Swiss Ephemeris على المنطقة البروجية الاستوائية.":
        ("Positions computed with the Swiss Ephemeris, tropical zodiac.",
         "Positions calculées avec la Swiss Ephemeris, zodiaque tropical."),
    "المنازل القمرية والاختيارات من تراث الأنواء العربي.":
        ("Lunar mansions and electional rules from the Arabic anwāʾ tradition.",
         "Manoirs lunaires et élections issus de la tradition arabe des anwāʾ."),
}


# ══════════════════════════════════════════════════════════════════
# المفردات — بابٌ ثانٍ لا غنًى عنه
#
# **مطابقةُ العبارة كاملةً لا تكفي.** خليّةُ الجدول تقول
# «3° 28′ العذراء»، وهي ليست مفتاحًا في القاموس ولن تكون —
# فالدرجة تتبدّل في كل خريطة. فلو اكتفينا بالعبارات لبقيت
# الجداول عربيّةً **وإن بلغ القاموس مئةً بالمئة**.
#
# فهذه المفردات تُبدَّل **داخل** النصّ لا بمطابقته.
#
# ── وحدٌّ يمنع الفساد ────────────────────────────────────────
# ولا تُطبَّق إلّا على **النصوص القصيرة** (انظر `VOCAB_MAX`):
# فخليّةُ الجدول قصيرة، وفقرةُ القراءة طويلة. ولو بُدِّلت
# المفردات داخل الفقرات لخرج خليطٌ أعجميّ لا يُقرأ:
# «تُحبّ Venus صورةً لا شخصًا». **والخلطُ أسوأ من العربيّة
# الصافية**، ونصوصُ القراءة قُرِّر أن تبقى عربيّة.
# ══════════════════════════════════════════════════════════════════
VOCAB_KEYS = (
    # الأجرام
    "الشمس", "القمر", "عطارد", "الزهرة", "المريخ", "المشتري", "زحل",
    "أورانوس", "نبتون", "بلوتو", "خيرون", "ليليث", "الرأس", "الذنب",
    # البروج
    "الحمل", "الثور", "الجوزاء", "السرطان", "الأسد", "العذراء",
    "الميزان", "العقرب", "القوس", "الجدي", "الدلو", "الحوت",
    # الأوتاد والزوايا
    "الطالع", "الغارب", "وسط السماء", "وتد الأرض",
    "اقتران", "مقابلة", "تربيع", "تثليث", "تسديس",
    "مُقبِلة", "مُدبِرة", "إيجابية", "سلبية",
)

# فوقه يُظنّ النصُّ فقرةً لا خليّة — والفقرة تبقى عربيّة
VOCAB_MAX = 44


def vocab_for(lang: str) -> dict:
    """المفردات وحدها — **ولا تُكرَّر نصًّا**: تُؤخَذ من `UI`."""
    if lang == "ar" or lang not in LANGS:
        return {}
    i = 0 if lang == "en" else 1
    return {k: UI[k][i] for k in VOCAB_KEYS if k in UI}


def dict_for(lang: str) -> dict:
    """قاموسُ لغةٍ بعينها: عربيّ ← مُترجَم. وما نقص لا يُذكَر أصلًا."""
    if lang == "ar" or lang not in LANGS:
        return {}
    i = 0 if lang == "en" else 1
    return {ar: pair[i] for ar, pair in UI.items() if pair[i]}


def normalize(lang: str | None) -> str:
    return lang if lang in LANGS else DEFAULT


def coverage() -> dict:
    """
    حالُ القاموس في نفسه — **لا نسبةُ تغطيته للصفحات**.

    وهذا فرقٌ وقعتُ فيه: كتبتُ أوّلًا `"تامّة": True` لأن كل
    مفتاحٍ له إنجليزيّةٌ وفرنسيّة — **وهي تامّةٌ بالنسبة إلى
    نفسها**. ثم قِسْتُها من الصفحات فإذا التغطية إحدى عشرة
    بالمئة. **فقياسُ الشيء بنفسه يُطمئن على خراب.**

    والنسبةُ الصادقة في `tools/i18n_todo.py`، وهو يستخرجها من
    الصفحات لا من هنا.
    """
    return {
        "مفاتيح مترجَمة": len(UI),
        "لغات": [k for k in LANGS if k != "ar"],
        "كل مفتاح تامّ اللغتين": all(all(p) for p in UI.values()),
        "التغطية": "تُقاس بـ tools/i18n_todo.py من الصفحات لا من هنا",
        "ملاحظة": ("نصوص القراءة تبقى عربية عمدًا — والمصطلح "
                   "التراثيّ يُفسَد بالترجمة الآلية."),
    }
