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
    # سبعُ صفحاتٍ دفعةً — الأصولُ والملوثيزيا والأملاح والمشاهير
    # وخرائط الأرض وأرباب الأزمنة ومواقع الكواكب
    # ══════════════════════════════════════════════════════════
    "الأصول": ("Origins", "Origines"),
    "الأصول — من أين جاءت البروج — الفَلَك":
        ("Origins — where the signs came from — Al-Falak",
         "Origines — d'où viennent les signes — Al-Falak"),
    "الفَلَك — الأصول": ("Al-Falak — Origins", "Al-Falak — Origines"),
    "ساعاتُ يومك الأربع والعشرون جاءت من مصر، وبروجُك من بابل.":
        ("Your day's twenty-four hours came from Egypt, and your signs "
         "from Babylon.",
         "Les vingt-quatre heures de votre journée viennent d'Égypte, et "
         "vos signes de Babylone."),
    "وهذه الصفحة تاريخٌ موثّق لا حُكم: من أين جاء ما نحسبه في سائر الصفحات، وما لم يصلنا منه شيء —":
        ("This page is documented history, not judgement: where what we "
         "compute elsewhere came from, and what did not reach us —",
         "Cette page est de l'histoire documentée, non un jugement : d'où "
         "vient ce que nous calculons ailleurs, et ce qui ne nous est pas "
         "parvenu —"),
    "فيُقال إنه لم يصل": ("so we say it did not", "nous le disons franchement"),
    "من أين جاء هذا كلُّه": ("Where all this came from", "D'où vient tout cela"),
    "أرباب الوجوه — مذهبان": ("Rulers of the decans — two schools",
                               "Maîtres des décans — deux écoles"),
    "اتّفقا": ("agree", "d'accord"),
    "اختلفا": ("differ", "diffèrent"),
    "يتّفق فيها المذهبان": ("where the two schools agree",
                            "où les deux écoles s'accordent"),
    "المصادر: أغطية التوابيت المصرية وسقفُ مقبرة سنموت · «مول أبين» و«إينوما آنو إنليل» · «الأربعة» لبطلَميوس · «التفهيم» للبيروني.":
        ("Sources: Egyptian coffin lids and the ceiling of Senenmut's tomb "
         "· MUL.APIN and Enūma Anu Enlil · Ptolemy's Tetrabiblos · "
         "al-Biruni's Tafhim.",
         "Sources : couvercles de sarcophages égyptiens et plafond de la "
         "tombe de Senenmout · MUL.APIN et Enūma Anu Enlil · le "
         "Tetrabiblos de Ptolémée · le Tafhim d'al-Biruni."),

    # ــ الملوثيزيا ــ
    "الملوثيزيا": ("Melothesia", "Mélothésie"),
    "الملوثيزيا — البدن والبروج": ("Melothesia — the body and the signs",
                                    "Mélothésie — le corps et les signes"),
    "الملوثيزيا — البدن والبروج — الفَلَك":
        ("Melothesia — the body and the signs — Al-Falak",
         "Mélothésie — le corps et les signes — Al-Falak"),
    "الفَلَك — الملوثيزيا": ("Al-Falak — Melothesia",
                              "Al-Falak — Mélothésie"),
    "alfalak.vercel.app · تاريخُ فكرةٍ لا طبّ":
        ("alfalak.vercel.app · the history of an idea, not medicine",
         "alfalak.vercel.app · l'histoire d'une idée, non de la médecine"),
    "اقرأ هذا أوّلًا": ("Read this first", "Lisez ceci d'abord"),
    "قسّم القدماء البدن على البروج: الحملُ الرأس، والحوتُ القدمان، وما بينهما بالترتيب. وردّوه إلى":
        ("The ancients divided the body among the signs: Aries the head, "
         "Pisces the feet, and the rest in order. They traced it back to",
         "Les anciens répartissaient le corps entre les signes : le Bélier "
         "la tête, les Poissons les pieds. Ils le ramenaient à"),
    "أربعة أخلاط": ("four humours", "quatre humeurs"),
    "لكلٍّ حرارةٌ ورطوبة. وهذه الصفحة تعرض ذلك":
        ("each with its heat and moisture. This page presents it",
         "chacune avec sa chaleur et son humidité. Cette page le présente"),
    "كما قالوه": ("as they said it", "tel qu'ils l'ont dit"),
    "— ومنه ما يُحسَب بقاعدة، ومنه ما هو حكايةُ زمن.":
        ("— some of it computed by rule, some of it the tale of an age.",
         "— une part calculée par règle, une part récit d'une époque."),
    "مِزاجُك على مذهبهم": ("Your temperament by their method",
                            "Votre tempérament selon leur méthode"),
    "الأخلاط الأربعة": ("The four humours", "Les quatre humeurs"),
    "البدن على البروج": ("The body across the signs",
                          "Le corps réparti sur les signes"),
    "البيت السادس": ("The sixth house", "La sixième maison"),
    "في البيت": ("in house", "en maison"),
    "ونظريةُ الأخلاط تجاوزها الطبّ منذ قرنٍ ونصف.":
        ("Humoral theory was left behind by medicine a century and a half ago.",
         "La théorie des humeurs a été abandonnée par la médecine il y a un "
         "siècle et demi."),
    "المصادر: «الأربعة» لبطلَميوس (المقالة الثالثة) · جالينوس في الأخلاط · ونقلُ أطبّاء العرب عنهما.":
        ("Sources: Ptolemy's Tetrabiblos (Book III) · Galen on the humours "
         "· and the Arab physicians who transmitted them.",
         "Sources : le Tetrabiblos de Ptolémée (livre III) · Galien sur les "
         "humeurs · et les médecins arabes qui les ont transmis."),
    "الفَلَك لا يُقدّم استشارة طبّية.":
        ("Al-Falak does not give medical advice.",
         "Al-Falak ne donne pas de conseil médical."),
    "وهذه صفحة تاريخِ فكرة، لا تشخيصٍ ولا دواء.":
        ("This is the history of an idea — not diagnosis, not treatment.",
         "Ceci est l'histoire d'une idée — ni diagnostic, ni traitement."),

    # ــ الأملاح ــ
    "ملح مولدك": ("Your birth salt", "Votre sel de naissance"),
    "الأملاح الاثنا عشر": ("The twelve salts", "Les douze sels"),
    "من أين جاءت هذه الفكرة؟": ("Where did this idea come from?",
                                 "D'où vient cette idée ?"),
    "فيلهلم شوسلر": ("Wilhelm Schüssler", "Wilhelm Schüssler"),
    "جورج كيري": ("George W. Carey", "George W. Carey"),
    "اثنا عشر ملحًا معدنيًّا عند الطبيب الألماني":
        ("Twelve mineral salts, from the German physician",
         "Douze sels minéraux, du médecin allemand"),
    "، ربطها الأمريكي": ("; the American", "; l'Américain"),
    "بالبروج الاثني عشر بعده بأربعين سنة.":
        ("linked them to the twelve signs forty years later.",
         "les a liés aux douze signes quarante ans plus tard."),
    "أملاح المولد — شوسلر وكيري — الفَلَك":
        ("Birth salts — Schüssler and Carey — Al-Falak",
         "Sels de naissance — Schüssler et Carey — Al-Falak"),
    "الفَلَك — أملاح المولد": ("Al-Falak — Birth salts",
                                "Al-Falak — Sels de naissance"),
    "alfalak.vercel.app · شوسلر (١٨٧٣) وكيري (١٩٢٠)":
        ("alfalak.vercel.app · Schüssler (1873) and Carey (1920)",
         "alfalak.vercel.app · Schüssler (1873) et Carey (1920)"),
    "المصدر: W. H. Schüßler «Eine abgekürzte Therapie» (1873)، وG. W. Carey «The Zodiac and the Salts of Salvation» (1920).":
        ("Sources: W. H. Schüßler, *Eine abgekürzte Therapie* (1873); "
         "G. W. Carey, *The Zodiac and the Salts of Salvation* (1920).",
         "Sources : W. H. Schüßler, *Eine abgekürzte Therapie* (1873) ; "
         "G. W. Carey, *The Zodiac and the Salts of Salvation* (1920)."),

    # ــ المشاهير ــ
    "خرائط المشاهير — الفَلَك": ("Famous charts — Al-Falak",
                                  "Thèmes célèbres — Al-Falak"),
    "الفَلَك — خرائط المشاهير": ("Al-Falak — Famous charts",
                                  "Al-Falak — Thèmes célèbres"),
    "مواليد أعلامٍ من العرب والعالم.":
        ("Birth data of figures from the Arab world and beyond.",
         "Naissances de personnalités arabes et du monde entier."),
    "وما نعرضه محدود عمدًا": ("and what we show is deliberately limited",
                              "et ce que nous montrons est volontairement limité"),
    ": ساعةُ ميلاد هؤلاء لا تُعرَف، فلا طالعَ لهم هنا ولا بيوت — وأكثر المواقع تضع الساعة ١٢:٠٠ وترسم عجلةً كاملة، والطالع يدور اثنتي عشرة مرّةً في اليوم.":
        (": their birth times are unknown, so there is no Ascendant here "
         "and no houses — most sites set the clock to 12:00 and draw a full "
         "wheel, yet the Ascendant turns twelve times a day.",
         ": leur heure de naissance est inconnue, donc pas d'Ascendant ici "
         "ni de maisons — la plupart des sites mettent 12:00 et tracent une "
         "roue entière, alors que l'Ascendant tourne douze fois par jour."),
    "ما يصحّ بالتاريخ وحده": ("What the date alone supports",
                              "Ce que la date seule permet"),
    "زوايا الكواكب البطيئة": ("Aspects among the slow planets",
                               "Aspects entre planètes lentes"),
    "برجُه يصحّ، ودرجتُه لا": ("its sign holds, its degree does not",
                               "son signe tient, son degré non"),
    "بدّل برجه في ذلك اليوم": ("changed sign that day",
                                "a changé de signe ce jour-là"),
    "شاعر، مصر، عالِم، ابن…": ("poet, Egypt, scientist, Ibn…",
                               "poète, Égypte, savant, Ibn…"),
    "درجات التوثيق على اصطلاح لويس رودِن، معرَّبةً. وما قبل ١٥٨٢/١٠/١٥ محسوبٌ بالتقويم اليولياني كما سجّلته المصادر.":
        ("Accuracy ratings follow Lois Rodden's convention. Dates before "
         "15 Oct 1582 are computed on the Julian calendar, as the sources "
         "recorded them.",
         "Les cotes de fiabilité suivent la convention de Lois Rodden. Les "
         "dates antérieures au 15 oct. 1582 sont calculées en calendrier "
         "julien, comme les sources les ont notées."),

    # ــ خرائط الأرض ــ
    "خرائط الأرض — الفَلَك": ("Astrocartography — Al-Falak",
                               "Astrocartographie — Al-Falak"),
    "الفَلَك — خرائط الأرض": ("Al-Falak — Astrocartography",
                               "Al-Falak — Astrocartographie"),
    "خطوط كواكبك على الأرض": ("Your planetary lines on Earth",
                               "Vos lignes planétaires sur Terre"),
    "خريطة العالم وعليها خطوط كواكب مولدك":
        ("A world map with your natal planetary lines",
         "Une carte du monde avec vos lignes planétaires natales"),
    "مدينةٌ تسأل عنها": ("A city you are asking about",
                          "Une ville qui vous intéresse"),
    "اتركه لمكان مولدك": ("leave blank for your birthplace",
                          "laisser vide pour votre lieu de naissance"),
    "حدُّ القرب": ("Proximity limit", "Limite de proximité"),
    "٣ درجات — الأشدّ وحده": ("3° — the strongest only",
                              "3° — les plus forts seulement"),
    "٦ درجات — المعتاد": ("6° — the usual", "6° — l'usuel"),
    "١٠ درجات — الواسع": ("10° — the wide", "10° — le large"),
    "خطّ الاستواء": ("Equator", "Équateur"),
    "مَدار السرطان": ("Tropic of Cancer", "Tropique du Cancer"),
    "مَدار الجدي": ("Tropic of Capricorn", "Tropique du Capricorne"),
    "الدائرة القطبية الشمالية": ("Arctic Circle", "Cercle arctique"),
    "الدائرة القطبية الجنوبية": ("Antarctic Circle", "Cercle antarctique"),
    "أوتادها": ("its angles", "ses angles"),
    "خريطتك سماءُ لحظةٍ واحدة، مرئيّةً من مكانٍ واحد. ولو وُلدتَ في اللحظة نفسها في مكانٍ آخر لكانت الكواكب هي هي — لكن":
        ("Your chart is the sky of a single instant, seen from a single "
         "place. Had you been born at that same instant elsewhere, the "
         "planets would be identical — but",
         "Votre thème est le ciel d'un seul instant, vu d'un seul lieu. Né "
         "au même instant ailleurs, les planètes seraient identiques — mais"),
    "تختلف: ما كان طالعًا يصير في وسط السماء، وما كان غاربًا يصير طالعًا. فلكل كوكبٍ على وجه الأرض أربعة خطوط.":
        ("would differ: what was rising becomes culminating, and what was "
         "setting becomes rising. So every planet has four lines on Earth.",
         "différeraient : ce qui se levait culmine, ce qui se couchait se "
         "lève. Chaque planète a donc quatre lignes sur Terre."),
    "الحساب من المطالع المستقيمة والمَيْل والوقت النجمي بغرينتش. والخريطة إسقاطٌ مستطيل، والمدن من أطلس الموقع نفسه.":
        ("Computed from right ascension, declination and Greenwich sidereal "
         "time. The map is an equirectangular projection; the cities come "
         "from the site's own atlas.",
         "Calculé à partir de l'ascension droite, de la déclinaison et du "
         "temps sidéral de Greenwich. Projection équirectangulaire ; villes "
         "issues de l'atlas du site."),

    # ــ أرباب الأزمنة ومواقع الكواكب ــ
    "أرباب الأزمنة — الفَلَك": ("Time lords — Al-Falak",
                                 "Maîtres du temps — Al-Falak"),
    "الفَلَك — أرباب الأزمنة": ("Al-Falak — Time lords",
                                 "Al-Falak — Maîtres du temps"),
    "الفردارات": ("Firdaria", "Firdaria"),
    "خريطة الميلاد تقول": ("The natal chart tells you", "Le thème natal dit"),
    "ما أنت": ("what you are", "ce que vous êtes"),
    "، ولا تقول": (", and does not tell you", ", et ne dit pas"),
    "متى": ("when", "quand"),
    ". وأرباب الأزمنة جواب «متى»: تقسيم العمر على الكواكب، فيتولّى كلٌّ منها فترة يصبغها بطبعه. الفردارات فارسية نقلها أبو معشر، والتسيير أقدم منها.":
        (". The time lords answer \"when\": a life divided among the "
         "planets, each governing a stretch and colouring it with its own "
         "nature. Firdaria are Persian, transmitted by Abu Ma'shar; "
         "direction is older still.",
         ". Les maîtres du temps répondent à « quand » : une vie répartie "
         "entre les planètes, chacune gouvernant une période. Les firdaria "
         "sont persanes, transmises par Abu Ma'shar ; la direction est plus "
         "ancienne encore."),
    "مكان إقامتك الآن": ("Where you live now", "Où vous vivez maintenant"),
    "للعودة الشمسية — اتركه إن لم تنتقل":
        ("for the solar return — leave blank if you have not moved",
         "pour la révolution solaire — laisser vide si vous n'avez pas déménagé"),
    "احسب لتاريخ": ("Compute for date", "Calculer pour la date"),
    "الفردارات من التراث الفارسي، نقلها أبو معشر البلخي وابن أبي الرجال. والتسيير والعودة الشمسية من أصول صناعة الأحكام.":
        ("Firdaria come from the Persian tradition, transmitted by Abu "
         "Ma'shar al-Balkhi and Ibn Abi al-Rijal. Direction and the solar "
         "return are foundations of the craft.",
         "Les firdaria viennent de la tradition persane, transmises par Abu "
         "Ma'shar al-Balkhi et Ibn Abi al-Rijal. La direction et la "
         "révolution solaire sont des fondements de l'art."),
    "مواقع الكواكب — الفَلَك": ("Ephemeris — Al-Falak",
                                 "Éphémérides — Al-Falak"),
    "الفَلَك — مواقع الكواكب": ("Al-Falak — Ephemeris",
                                 "Al-Falak — Éphémérides"),
    "جدول المواقع الظاهرية لأي لحظة، مع الرجوع والسرعة اليومية وطور القمر.":
        ("A table of apparent positions for any moment, with retrogrades, "
         "daily motion and the moon phase.",
         "Un tableau des positions apparentes à tout instant, avec "
         "rétrogradations, mouvement diurne et phase lunaire."),
    "التوقيت حسب مدينة": ("Time zone by city", "Fuseau selon la ville"),
    "بالتوقيت العالمي": ("in UTC", "en UTC"),
    "محسوبة بمكتبة Swiss Ephemeris — مواقع ظاهرية على المنطقة البروجية الاستوائية.":
        ("Computed with the Swiss Ephemeris — apparent positions on the "
         "tropical zodiac.",
         "Calculé avec la Swiss Ephemeris — positions apparentes, zodiaque "
         "tropical."),
    "اعرض": ("Show", "Afficher"),
    "وفيه:": ("Containing:", "Contient :"),
    "نسخ النصّ": ("Copy text", "Copier le texte"),

    # ══════════════════════════════════════════════════════════
    # ساعاتُ الكواكب والاختيارات والنشرة الشهرية
    #
    # **وأسماءُ الكتب لا تُترجَم**: «غاية الحكيم» كتابٌ بعينه،
    # وقد عُرِف في اللاتينية باسم *Picatrix* قرونًا — فيُذكَر
    # بالاسمين، إذ من قرأ بالإنجليزية يعرفه بذاك لا بهذا.
    # ══════════════════════════════════════════════════════════
    "ساعات الكواكب — الفَلَك": ("Planetary hours — Al-Falak",
                                 "Heures planétaires — Al-Falak"),
    "الفَلَك — ساعات الكواكب": ("Al-Falak — Planetary hours",
                                 "Al-Falak — Heures planétaires"),
    "ليست الساعة هنا ستّين دقيقة. النهار من الشروق إلى الغروب يُقسَم اثنتي عشرة ساعة متساوية، والليل مثله — فتطول ساعات النهار صيفًا وتقصر شتاءً. الدلالات من «غاية الحكيم» للمجريطي و«التفهيم» للبيروني.":
        ("An hour here is not sixty minutes. Daylight, from sunrise to "
         "sunset, is divided into twelve equal hours, and the night "
         "likewise — so day hours lengthen in summer and shorten in winter. "
         "The meanings come from al-Majriti's Ghayat al-Hakim (the Latin "
         "Picatrix) and al-Biruni's Tafhim.",
         "Une heure n'est pas ici soixante minutes. Le jour, du lever au "
         "coucher, est divisé en douze heures égales, et la nuit de même — "
         "les heures du jour s'allongent en été. Les significations "
         "viennent du Ghayat al-Hakim d'al-Majriti (le Picatrix latin) et "
         "du Tafhim d'al-Biruni."),
    "النهار": ("Day", "Jour"),
    "الليل": ("Night", "Nuit"),
    "طبعها": ("Its nature", "Sa nature"),
    "تصلح": ("Suits", "Convient à"),
    "تُتجنّب": ("Avoid", "À éviter"),
    "وما يُتجنّب": ("and what to avoid", "et ce qu'il faut éviter"),
    "من غاية الحكيم": ("From Ghayat al-Hakim (Picatrix)",
                        "Du Ghayat al-Hakim (Picatrix)"),
    "من التفهيم": ("From al-Biruni's Tafhim", "Du Tafhim d'al-Biruni"),
    "المصادر": ("Sources", "Sources"),
    "نسخ الجدول": ("Copy table", "Copier le tableau"),
    "— كل الساعات —": ("— all hours —", "— toutes les heures —"),
    "الشروق والغروب محسوبان بمكتبة Swiss Ephemeris لموضعك تحديدًا.":
        ("Sunrise and sunset are computed with the Swiss Ephemeris for "
         "your exact location.",
         "Lever et coucher calculés avec la Swiss Ephemeris pour votre "
         "position exacte."),
    "الدلالات من التراث الفلكي العربي، والصياغة معاصرة.":
        ("The meanings are from the Arabic astrological tradition; the "
         "wording is modern.",
         "Les significations viennent de la tradition arabe ; la "
         "formulation est moderne."),
    "أحسب مواقع القمر والكواكب…": ("… computing Moon and planet positions",
                                    "… calcul des positions"),

    # ــ الاختيارات ــ
    "الاختيارات — متى أفعل؟ — الفَلَك":
        ("Electional astrology — when should I? — Al-Falak",
         "Astrologie élective — quand agir ? — Al-Falak"),
    "الفَلَك — الاختيارات": ("Al-Falak — Electional",
                              "Al-Falak — Élections"),
    "تقويم الشهر يُجيب عن «كيف حال هذا اليوم؟». وهذه الصفحة تُجيب عن السؤال المعكوس، وهو الذي يسأله الناس فعلًا:":
        ("The month's calendar answers \"how is this day?\". This page "
         "answers the reverse question — the one people actually ask:",
         "Le calendrier du mois répond à « comment est ce jour ? ». Cette "
         "page répond à la question inverse, celle qu'on pose vraiment :"),
    ". تمسح الشهور القادمة، وتُعطي مع كل يوم ساعته — فالقدماء يختارون الساعة كما يختارون اليوم.":
        (". It scans the coming months and gives, with each day, its hour "
         "— for the ancients chose the hour as they chose the day.",
         ". Elle balaie les mois à venir et donne, avec chaque jour, son "
         "heure — car les anciens choisissaient l'heure comme le jour."),
    "لأيّ غرض؟": ("For what purpose?", "Dans quel but ?"),
    "أعطني أفضل يوم": ("Give me the best day", "Donnez-moi le meilleur jour"),
    "لغرض بعينه": ("for a specific purpose", "pour un objet précis"),
    "ستّة أشهر": ("Six months", "Six mois"),
    "من اليوم": ("From today", "À partir d'aujourd'hui"),
    "رجّح البحث بخريطة مولدي (اختياري)":
        ("Weight the search by my natal chart (optional)",
         "Pondérer la recherche par mon thème natal (facultatif)"),
    "حين تُعطي مولدك، تُرجَّح الأيام التي يُوافقها العابر في خريطتك أنت. والوزن هنا أصغر عمدًا: العبور البطيء يدوم شهورًا، فلو ثقُل وزنه لسوّى بين كلّ أيام الفصل.":
        ("When you give your birth data, days whose transits suit your own "
         "chart are favoured. The weight is deliberately small: slow "
         "transits last for months, so a heavy weight would flatten every "
         "day of the season into one.",
         "Si vous donnez votre naissance, les jours dont les transits "
         "conviennent à votre thème sont favorisés. Le poids est "
         "volontairement faible : les transits lents durent des mois."),
    "أختار أفضل ساعة في كل يوم…": ("… choosing the best hour each day",
                                    "… choix de la meilleure heure"),
    "أُرتّب النتائج…": ("… ranking the results", "… classement des résultats"),
    "لا تُبنى على هذا قرارات لا رجعة فيها.":
        ("Do not base irreversible decisions on this.",
         "Ne fondez pas sur ceci de décisions irréversibles."),
    "الأغراض وشروطها من التراث الفلكي العربي · الساعات من «غاية الحكيم» و«التفهيم».":
        ("Purposes and their conditions from the Arabic tradition · hours "
         "from Ghayat al-Hakim (Picatrix) and al-Biruni's Tafhim.",
         "Objets et conditions issus de la tradition arabe · heures du "
         "Ghayat al-Hakim (Picatrix) et du Tafhim d'al-Biruni."),

    # ــ النشرة الشهرية ــ
    "النشرة الشهرية — الفَلَك": ("Monthly bulletin — Al-Falak",
                                  "Bulletin mensuel — Al-Falak"),
    "الفَلَك — الشهرية": ("Al-Falak — Monthly", "Al-Falak — Mensuel"),
    "أي شهر بين ١٨٠٠ و٢٤٠٠: انتقالات الكواكب ومحطّات رجوعها، الزوايا التامّة بأوقاتها، التقميرات والكسوف بأشكالها، وتقويم الاختيارات لكل يوم.":
        ("Any month between 1800 and 2400: planetary ingresses and "
         "retrograde stations, exact aspects with their times, lunations "
         "and eclipses with their types, and an electional calendar for "
         "every day.",
         "N'importe quel mois entre 1800 et 2400 : entrées de signe et "
         "stations rétrogrades, aspects exacts avec leurs heures, "
         "lunaisons et éclipses, et un calendrier électif jour par jour."),
    "هذا الشهر": ("This month", "Ce mois"),
    "الشهر السابق ›": ("Previous month ›", "Mois précédent ›"),
    "‹ الشهر التالي": ("‹ Next month", "‹ Mois suivant"),
    "السابق ›": ("Previous ›", "Précédent ›"),
    "‹ التالي": ("‹ Next", "‹ Suivant"),
    "اللسان": ("Voice", "Ton"),
    "لسان النشرة اليومية": ("Daily-bulletin voice", "Ton du bulletin quotidien"),
    "لسان التراث": ("Traditional voice", "Ton traditionnel"),
    "لسان أدبي": ("Literary voice", "Ton littéraire"),
    "الرجوع": ("Retrogrades", "Rétrogradations"),
    "العبور": ("Transits", "Transits"),
    "+ جوّي الشخصي": ("+ my personal weather", "+ ma météo personnelle"),
    "− جوّي الشخصي": ("− my personal weather", "− ma météo personnelle"),
    "احسب جوّي": ("Compute my weather", "Calculer ma météo"),
    "أدخل ميلادك ليقول لك الشهر أيّ أحداثه تمسّك أنت. البيانات تُرسَل للحساب فقط ولا تُحفَظ على الخادم، وتُخزَّن في متصفّحك وحده.":
        ("Enter your birth data and the month will tell you which of its "
         "events touch you. The data is sent for calculation only, is not "
         "stored on the server, and is kept in your browser alone.",
         "Saisissez votre naissance et le mois vous dira lesquels de ses "
         "événements vous concernent. Les données servent au calcul seul, "
         "ne sont pas conservées sur le serveur, et restent dans votre "
         "navigateur."),
    "امسح بياناتي": ("Erase my data", "Effacer mes données"),
    "تاريخ مولدك": ("Your birth date", "Votre date de naissance"),
    "تاريخ ميلادك": ("Your birth date", "Votre date de naissance"),
    "ساعة ميلادك": ("Your birth time", "Votre heure de naissance"),
    "مكان ميلادك": ("Your birthplace", "Votre lieu de naissance"),
    "أين؟": ("Where?", "Où ?"),
    "أمثلة": ("Examples", "Exemples"),
    "ابحث": ("Search", "Rechercher"),
    "نسخ النشرة": ("Copy bulletin", "Copier le bulletin"),
    "أدخل تاريخ ميلادك ومكانه.": ("Enter your birth date and place.",
                                   "Saisissez votre date et lieu de naissance."),
    "أجمع أحداث الشهر…": ("… gathering the month's events",
                           "… collecte des événements"),
    "أحسب الانتقالات والكسوف…": ("… computing ingresses and eclipses",
                                  "… calcul des entrées et éclipses"),
    "أصوغ النشرة…": ("… composing the bulletin", "… rédaction du bulletin"),
    "المواقع محسوبة بمكتبة Swiss Ephemeris. تقويم الاختيارات على قواعد «غاية الحكيم» و«التفهيم» وكتب الاختيارات العربية.":
        ("Positions are computed with the Swiss Ephemeris. The electional "
         "calendar follows Ghayat al-Hakim (Picatrix), al-Biruni's Tafhim, "
         "and the Arabic books of elections.",
         "Positions calculées avec la Swiss Ephemeris. Le calendrier "
         "électif suit le Ghayat al-Hakim (Picatrix), le Tafhim d'al-Biruni "
         "et les traités arabes d'élections."),

    # ــ الشهور وأيّام الأسبوع ــ
    "يناير": ("January", "Janvier"), "فبراير": ("February", "Février"),
    "مارس": ("March", "Mars"), "أبريل": ("April", "Avril"),
    "مايو": ("May", "Mai"), "يونيو": ("June", "Juin"),
    "يوليو": ("July", "Juillet"), "أغسطس": ("August", "Août"),
    "سبتمبر": ("September", "Septembre"), "أكتوبر": ("October", "Octobre"),
    "نوفمبر": ("November", "Novembre"), "ديسمبر": ("December", "Décembre"),
    "الإثنين": ("Monday", "Lundi"),

    # ــ الصفحة الرئيسة: ما بقي ــ
    "الفَلَك — الرئيسة": ("Al-Falak — Home", "Al-Falak — Accueil"),
    "… أقرأ السماء": ("… reading the sky", "… lecture du ciel"),
    "تعذّر الاتصال بالخادم:": ("Could not reach the server:",
                                "Impossible de joindre le serveur :"),
    "وفيه أيضًا": ("Also here", "Également ici"),
    "البيوت والبروج والزوايا مشروحة، ومعجم لكل مصطلح":
        ("Houses, signs and aspects explained, with a glossary for every term",
         "Maisons, signes et aspects expliqués, avec un glossaire complet"),
    "جواب من خريطة اللحظة التي وقع فيها سؤالك — وقد لا يكون له جواب":
        ("An answer from the chart of the moment your question arose — "
         "and it may have none",
         "Une réponse tirée du thème de l'instant de votre question — "
         "qui peut n'en avoir aucune"),
    "خريطتان معًا: الحبّ والصحبة والشراكة، وما رفع كل درجة":
        ("Two charts together: love, friendship and partnership, and what "
         "raised each score",
         "Deux thèmes ensemble : amour, amitié et association, et ce qui "
         "fait chaque score"),
    "أحداث الشهر كلّه: الانتقالات والكسوف والرجوع، بثلاثة أساليب في الصياغة.":
        ("The whole month's events: ingresses, eclipses and retrogrades, "
         "in three styles of wording.",
         "Les événements du mois : entrées de signe, éclipses et "
         "rétrogradations, en trois styles."),

    # ــ صفحة خريطة الميلاد ــ
    # **وأنظمةُ البيوت أسماءُ أعلامٍ لا تُترجَم** — بلاسيدوس رجلٌ
    # وكوخ رجل. فتُنقَل حروفًا كما تُكتب في كتب الصناعة، ويُترجَم
    # وصفُها وحده.
    "خريطة الميلاد والطالع": ("Natal chart and Ascendant",
                               "Thème natal et Ascendant"),
    "خريطة الميلاد والطالع — الفَلَك": ("Natal chart and Ascendant — Al-Falak",
                                         "Thème natal et Ascendant — Al-Falak"),
    "الفَلَك — خريطة الميلاد": ("Al-Falak — Natal chart",
                                 "Al-Falak — Thème natal"),
    "دقّة الساعة مهمّة: كل أربع دقائق تُزحزح الطالع درجة كاملة. التوقيت الصيفي التاريخي يُطبَّق تلقائيًّا، وتُنبَّه إن كانت ساعتك ملتبسة. الخرائط تُحفظ في متصفّحك وحده.":
        ("The hour matters: every four minutes shifts the Ascendant by a "
         "full degree. Historical daylight saving is applied automatically, "
         "and you are warned if your time is ambiguous. Charts are saved in "
         "your browser alone.",
         "L'heure compte : chaque quatre minutes décale l'Ascendant d'un "
         "degré entier. L'heure d'été historique est appliquée "
         "automatiquement, et vous êtes averti si votre heure est ambiguë. "
         "Les thèmes sont enregistrés dans votre navigateur seul."),
    "دمشق، معرّة النعمان، أي قرية…":
        ("Damascus, Maarat al-Numan, any village…",
         "Damas, Maarat al-Numan, n'importe quel village…"),
    "البيوت الكاملة": ("Whole sign houses", "Maisons en signes entiers"),
    "البيوت الكاملة — نظام العرب": ("Whole sign — the Arabic system",
                                     "Signes entiers — le système arabe"),
    "القبّاني": ("Alcabitius", "Alcabitius"),
    "القبّاني — نظام بغداد": ("Alcabitius — the Baghdad system",
                               "Alcabitius — le système de Bagdad"),
    "بلاسيدوس": ("Placidus", "Placidus"),
    "بلاسيدوس — المعاصر": ("Placidus — the modern system",
                            "Placidus — le système moderne"),
    "كوخ": ("Koch", "Koch"),
    "ريجومونتانوس": ("Regiomontanus", "Regiomontanus"),
    "كامبانوس": ("Campanus", "Campanus"),
    "بورفيري": ("Porphyry", "Porphyre"),
    "البيوت المتساوية": ("Equal houses", "Maisons égales"),
    "العجلة": ("Wheel", "Roue"),
    "الخلاصة": ("Summary", "Résumé"),
    "الثلاثة الكبار": ("The big three", "Les trois grands"),
    "البيوت والأوتاد": ("Houses and angles", "Maisons et angles"),
    "السهام والأشكال": ("Lots and patterns", "Parts et figures"),
    "طبقات العجلة": ("Wheel layers", "Couches de la roue"),
    "درجات الأجرام": ("Body degrees", "Degrés des astres"),
    "الزوايا الصغرى": ("Minor aspects", "Aspects mineurs"),
    "مع الزوايا الصغرى": ("With minor aspects", "Avec aspects mineurs"),
    "الرئيسية فقط": ("Major only", "Majeurs seulement"),
    "مُقبِلة ومُدبِرة": ("Applying and separating",
                          "Appliquant et séparant"),
    "مُقبِلة، أثرها في ما هو آتٍ":
        ("Applying — its effect lies ahead",
         "Appliquant — son effet est à venir"),
    "مُدبِرة، أثرها ماضٍ ينقضي":
        ("Separating — its effect is passing",
         "Séparant — son effet s'achève"),
    "راجع — يبدو سائرًا إلى الوراء، ودلالته المراجعة والإعادة لا التوقّف.":
        ("Retrograde — it appears to move backwards; it signifies review "
         "and return, not a halt.",
         "Rétrograde — il semble reculer ; il signifie révision et retour, "
         "non un arrêt."),
    "لا كرامة له هنا": ("No dignity here", "Aucune dignité ici"),
    "يؤكّد زاويةً ظاهرة بينهما": ("Confirms a visible aspect between them",
                                   "Confirme un aspect visible entre eux"),
    "° في اليوم": ("° per day", "° par jour"),
    "′ في اليوم": ("′ per day", "′ par jour"),
    "— ملكي": ("— royal", "— royale"),
    "سهم": ("Lot", "Part"),
    "المواقع ظاهرية على المنطقة البروجية الاستوائية، بمكتبة Swiss Ephemeris.":
        ("Positions are apparent, on the tropical zodiac, via the Swiss Ephemeris.",
         "Positions apparentes, zodiaque tropical, via la Swiss Ephemeris."),
    "الكرامات والسهام والمنازل من التراث الفلكي العربي.":
        ("Dignities, lots and mansions from the Arabic astrological tradition.",
         "Dignités, parts et manoirs issus de la tradition astrologique arabe."),

    # ــ صفحة النشرة اليومية ــ
    # عُوينت وحدها فبقي فيها خمسة عشر. **والمعاينة صفحةً صفحة
    # هي التي تكشف هذا** — لا الرقمُ الكلّي، فهو يُخفي أيَّ
    # صفحةٍ بعينها هي المتروكة.
    "النشرة الفلكية": ("Astrological bulletin", "Bulletin astrologique"),
    "النشرة الفلكية اليومية — الفَلَك":
        ("Daily astrological bulletin — Al-Falak",
         "Bulletin astrologique quotidien — Al-Falak"),
    "الفَلَك — النشرة اليومية": ("Al-Falak — Daily bulletin",
                                  "Al-Falak — Bulletin quotidien"),
    "اختر أي يوم وأي مدينة. تُحسب لحظيًا، وتُنسخ جاهزة للتلغرام أو الواتساب.":
        ("Pick any day and any city. Computed live, and ready to copy "
         "into Telegram or WhatsApp.",
         "Choisissez un jour et une ville. Calculé en direct, prêt à copier "
         "dans Telegram ou WhatsApp."),
    "نشرة اليوم": ("Today's bulletin", "Bulletin du jour"),
    "نشرة الغد": ("Tomorrow's bulletin", "Bulletin de demain"),
    "اليوم السابق ›": ("Previous day ›", "Jour précédent ›"),
    "‹ اليوم التالي": ("‹ Next day", "‹ Jour suivant"),
    "نسخ النصّ للتلغرام أو الواتساب":
        ("Copy text for Telegram or WhatsApp",
         "Copier le texte pour Telegram ou WhatsApp"),
    "الصيغة": ("Wording", "Formulation"),
    "عدّ المنازل": ("Mansion counting", "Comptage des manoirs"),
    "المذهب المشهور": ("The common convention", "La convention courante"),
    "مُزاح منزلة واحدة": ("Shifted by one mansion", "Décalé d'un manoir"),
    "دمشق": ("Damascus", "Damas"),
    "دمشق، باريس، القاهرة…": ("Damascus, Paris, Cairo…",
                              "Damas, Paris, Le Caire…"),
    "حلب، دمشق…": ("Aleppo, Damascus…", "Alep, Damas…"),
    "دمشق…": ("Damascus…", "Damas…"),
    "دمشق، باريس…": ("Damascus, Paris…", "Damas, Paris…"),
    "حلب…": ("Aleppo…", "Alep…"),

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
