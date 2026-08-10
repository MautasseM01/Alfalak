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

# ══════════════════════════════════════════════════════════════════
# الرسالة التحذيرية — **بلغة القارئ، وفيها ما يفعله الآن**
#
# أوّل صياغةٍ قالت «النصوص تبقى عربية» ووقفت. وذلك **صدقٌ
# ناقص**: يعرف القارئ أنه لن يقرأ، ولا يعرف ماذا يصنع.
#
# فأُضيف إليها أمران:
#   · **ما يفعله الآن**: النقر بالزرّ الأيمن → ترجمة المتصفّح.
#     وهي ترجمةٌ سطحيّة، **ويُقال إنها سطحيّة** لا يُخفى.
#   · **وما نحن فاعلون**: ترجمةٌ تُراعي المصطلح تُبنى.
#
# فمن قرأها عرف حالَه وحيلتَه معًا.
# ══════════════════════════════════════════════════════════════════
PARTIAL = {
    "en": ("**The readings on this page are still in Arabic.** The menus, "
           "forms and tables are translated; the astrological "
           "interpretations are not — they are traditional Arabic sources, "
           "and a machine would flatten their terminology.\n"
           "**For a rough reading now:** right-click the page and choose "
           "your browser's Translate. It will be shallow, but readable.\n"
           "We are building a proper translation that keeps the "
           "terminology intact."),
    "fr": ("**Les lectures de cette page restent en arabe.** Les menus, "
           "formulaires et tableaux sont traduits ; les interprétations "
           "astrologiques ne le sont pas — ce sont des sources arabes "
           "traditionnelles, qu'une machine aplatirait.\n"
           "**Pour une lecture approximative dès maintenant :** clic droit "
           "sur la page, puis « Traduire ». Ce sera superficiel, mais "
           "lisible.\n"
           "Nous préparons une traduction fidèle qui préserve les termes."),
}

# ══════════════════════════════════════════════════════════════════
# القاموس — العربيّة مفتاحًا
#
# ولا يُترجَم هنا إلّا **أثاث الواجهة**. وما نقص بقي عربيًّا،
# و`coverage()` تقول كم بقي بالرقم لا بالظنّ.
# ══════════════════════════════════════════════════════════════════
UI = {
    # ══════════════════════════════════════════════════════════
    # بطاقاتُ الرئيسة — **وهي أوّل ما تراه العين، وبقيت عربية**
    # ══════════════════════════════════════════════════════════
    "كيف يومي؟": ("How is my day?", "Comment est ma journée ?"),
    "من أنا؟": ("Who am I?", "Qui suis-je ?"),
    "متى أفعل هذا؟": ("When should I do this?", "Quand dois-je agir ?"),
    "هل نتوافق؟": ("Are we compatible?", "Sommes-nous compatibles ?"),
    "عندي سؤال محيّر": ("I have a puzzling question",
                        "J'ai une question qui m'embarrasse"),
    "أريد أن أفهم هذا العلم": ("I want to understand this craft",
                                "Je veux comprendre cet art"),
    "حال السماء اليوم، وما يصلح فيه وما يُؤجَّل":
        ("The sky today — what suits it and what should wait",
         "Le ciel aujourd'hui — ce qui convient et ce qui attend"),
    "خريطة مولدك وقراءتها — تحتاج تاريخ ميلادك وساعته ومكانه":
        ("Your birth chart and its reading — needs your date, time and place",
         "Votre thème natal et sa lecture — date, heure et lieu requis"),
    "أفضل يوم وساعة لأمر تنويه، عبر الشهور القادمة":
        ("The best day and hour for what you intend, across coming months",
         "Le meilleur jour et heure pour votre projet, dans les mois à venir"),
    "أحداث الشهر كلّه: الانتقالات والكسوف والرجوع، بثلاثة أساليب في الصياغة":
        ("The whole month's events: ingresses, eclipses and retrogrades, "
         "in three styles of wording",
         "Les événements du mois : entrées de signe, éclipses et rétrogradations, "
         "en trois styles"),
    "اثنتا عشرة ساعة نهارًا ومثلها ليلًا، لكلٍّ كوكبها وما تصلح له.":
        ("Twelve hours by day and twelve by night, each with its planet "
         "and what it suits.",
         "Douze heures le jour et douze la nuit, chacune avec sa planète."),
    "أيّ فترة من عمرك تعيش الآن، ومتى تنتهي، وخريطة سنتك القادمة.":
        ("Which period of your life you are living, when it ends, and "
         "your coming year's chart.",
         "Quelle période de votre vie vous vivez, quand elle finit, et le "
         "thème de votre année."),
    "جدول المواقع لأي لحظة، مع الرجوع وطور القمر.":
        ("A table of positions for any moment, with retrogrades and moon phase.",
         "Un tableau des positions à tout instant, avec rétrogradations et phase lunaire."),
    "ابنِ على الفَلَك، أو أدخِل السماء إلى تقويم هاتفك باشتراك واحد.":
        ("Build on Al-Falak, or bring the sky into your phone's calendar.",
         "Construisez sur Al-Falak, ou faites entrer le ciel dans votre agenda."),
    "السماء الآن": ("The sky now", "Le ciel maintenant"),
    "الهلال المتناقص": ("Waning crescent", "Dernier croissant"),
    "الهلال المتزايد": ("Waxing crescent", "Premier croissant"),
    "الأحدب المتزايد": ("Waxing gibbous", "Gibbeuse croissante"),
    "الأحدب المتناقص": ("Waning gibbous", "Gibbeuse décroissante"),
    "التربيع الأوّل": ("First quarter", "Premier quartier"),
    "التربيع الأخير": ("Last quarter", "Dernier quartier"),
    "البدر": ("Full moon", "Pleine lune"),
    "المحاق": ("New moon", "Nouvelle lune"),
    "ليليث الحقيقية": ("True Lilith", "Vraie Lilith"),

    # ══════════════════════════════════════════════════════════
    # أبوابُ التصفّح ومبدّل المستوى — **وهي أوّل ما يُرى ولم تُترجَم**
    #
    # ظهرت الصفحة الرئيسة إنجليزيّةً وفيها «يومي» و«خريطتي»
    # و«قراري» و«أتعلّم» و«لغة الصناعة» عربيّةً وسطَها. وسببُها
    # أن هذه **تُبنى في `nav.js` و`plain.js`** لا في الوسوم،
    # فلم يلتقطها الاستخراج ولم أضعها بيدي.
    # ══════════════════════════════════════════════════════════
    "يومي": ("Today", "Aujourd'hui"),
    "خريطتي": ("My chart", "Mon thème"),
    "قراري": ("My decision", "Ma décision"),
    "أتعلّم": ("Learn", "J'apprends"),
    "ما حال السماء الآن، وما يصلح لهذا اليوم":
        ("The sky right now, and what suits today",
         "Le ciel maintenant, et ce qui convient aujourd'hui"),
    "مولدك بثلاث مدارس: عربية وهندية وصينية":
        ("Your birth in three traditions: Arabic, Vedic, Chinese",
         "Votre naissance en trois traditions : arabe, védique, chinoise"),
    "بلغة مبسّطة": ("Plain language", "Langage simple"),
    "بلغة أهل الصناعة": ("Technical language", "Langage technique"),
    "مبسّطة": ("Plain", "Simple"),
    "لغة الصناعة": ("Technical", "Technique"),

    # ــ الصفحة الرئيسة ــ
    # **والقاعدة التي وضعتُها كانت خطأً**: قصرتُ الترجمة على ما
    # دون سبعين حرفًا، وسمّيتُ ما طال «شرحًا يبقى عربيًّا». وهذا
    # صحيحٌ في نصوص القراءة، **باطلٌ في نصّ الصفحة نفسه**: صدرُ
    # الرئيسة ليس قراءةً فلكية بل كلامُ الموقع عن نفسه.
    # فالحدُّ الصحيح **بالمصدر لا بالطول**.
    "ماذا تريد أن تعرف؟": ("What do you want to know?",
                            "Que voulez-vous savoir ?"),
    "أدوات فلكية بالعربية، محسوبة لحظيًّا لأيّ يوم وأيّ مكان — بلا اشتراك ولا حساب ولا إعلانات. ولستَ مضطرًّا أن تعرف شيئًا عن الفلك: كل صفحة تبدأ بسطرين يفهمهما من لم يقرأ في هذا قطّ.":
        ("Arabic astrology tools, computed live for any day and any place — "
         "no subscription, no account, no ads. And you need not know any "
         "astrology: every page opens with two lines that a complete "
         "newcomer can follow.",
         "Des outils d'astrologie arabe, calculés en direct pour tout jour "
         "et tout lieu — sans abonnement, sans compte, sans publicité. Et "
         "nul besoin de connaître l'astrologie : chaque page s'ouvre sur "
         "deux lignes qu'un débutant comprend."),

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

    # ــ ألفاظُ الحال — **وهي ما بقي عربيًّا وسط الإنجليزية** ــ
    # قال صاحب المشروع: «تُرجم المُجمَل وبقيت كلمات، مثل
    # الكوكب الراجع». وهذه هي: صفاتٌ قصيرة تُلحَق بالمخرجات
    # فتبقى ظاهرةً وسط النصّ المترجَم، **وهي أشدُّ ما يُرى**.
    "راجع": ("retrograde", "rétrograde"),
    "مستقيم": ("direct", "direct"),
    "الكوكب الراجع": ("Retrograde planet", "Planète rétrograde"),
    "متراجع": ("retrograde", "rétrograde"),
    "تحت الشعاع": ("under the beams", "sous les rayons"),
    "محترق": ("combust", "combuste"),
    "في قلب الشمس": ("cazimi", "cazimi"),
    "نهارية": ("diurnal", "diurne"),
    "ليلية": ("nocturnal", "nocturne"),
    "الغريب": ("peregrine", "pérégrin"),
    "بيته": ("domicile", "domicile"),
    "شرفه": ("exaltation", "exaltation"),
    "هبوطه": ("fall", "chute"),
    "وباله": ("detriment", "exil"),
    "مثلثته": ("triplicity", "triplicité"),
    "حدّه": ("term", "terme"),
    "وجهه": ("face", "face"),
    "ناري": ("Fire", "Feu"),
    "ترابي": ("Earth", "Terre"),
    "هوائي": ("Air", "Air"),
    "مائي": ("Water", "Eau"),
    "منقلب": ("Cardinal", "Cardinal"),
    "ثابت": ("Fixed", "Fixe"),
    "ذو جسدين": ("Mutable", "Mutable"),
    "نيّر": ("Luminary", "Luminaire"),
    "سعد": ("Benefic", "Bénéfique"),
    "نحس": ("Malefic", "Maléfique"),
    "خلوّ المسار": ("Void of course", "Vide de course"),
    "العناصر": ("Elements", "Éléments"),
    "الطبائع": ("Modes", "Modes"),
    "تامّة": ("exact", "exact"),
    "الشروق": ("Sunrise", "Lever du soleil"),
    "الغروب": ("Sunset", "Coucher du soleil"),
    "الزوال": ("Noon", "Midi"),
    "طور القمر": ("Moon phase", "Phase lunaire"),
    "المنزلة": ("Mansion", "Manoir"),
    "سيّد الخريطة": ("Chart ruler", "Maître du thème"),
    "سيّد الطالع": ("Ascendant ruler", "Maître de l'ascendant"),
    "الكرامات": ("Dignities", "Dignités"),
    "القراءة": ("Reading", "Lecture"),
    "الأوتاد": ("Angles", "Angles"),
    "لا شيء": ("None", "Aucun"),
    "الخريطة": ("Chart", "Thème"),
    "الوصلات": ("Contacts", "Contacts"),
    "التراكب": ("Overlays", "Superpositions"),
    "الميزان الكلّي": ("Overall score", "Score global"),

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
    # ــ **ألفاظُ الحال: وهي عينُ ما شكا منه صاحب المشروع** ــ
    # «تُرجم المُجمَل وبقيت كلمات، مثل الكوكب الراجع». وهذه
    # لا تقع وحدها في خليّة بل **داخل نصّ**: «زحل: 14° 36′
    # الحمل (راجع)». فلا تنفع فيها مطابقةُ العبارة، وإنما
    # تُبدَّل داخل النصّ — وهذا بابُ المفردات لا بابُ القاموس.
    "راجع", "مستقيم", "متراجع", "محترق", "تحت الشعاع",
    "نهارية", "ليلية", "الغريب", "تامّة",
    "ناري", "ترابي", "هوائي", "مائي",
    "منقلب", "ثابت", "ذو جسدين", "نيّر", "سعد", "نحس",
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
