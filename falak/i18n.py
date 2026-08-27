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
    # الملفّاتُ المشتركة — **وهي أعمُّ من أيّ صفحة**
    #
    # `plain.js` و`wheel.js` و`nav.js` تُرسَم في **كل** صفحة.
    # فكانت كلُّ صفحةٍ تُقاس ١٠٠٪ وفيها هذه عربيّةً — لأن
    # القياسَ صفحةً صفحة لا يرى المشترك.
    #
    # **ومقياسان لا يتّفقان أحدُهما ناقص**: الصفحاتُ ١٠٠٪
    # والكلُّ ٨٧٪، والفرقُ هو هذا كلُّه.
    # ══════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════
    # **ما لم يعرضه الاستخراج أصلًا** — وهذا عيبٌ ثالث كُشف
    # بالقياس من الصفحة.
    #
    # `i18n_todo.py` يطرح كلَّ نصٍّ فيه `<` أو `>`، منعًا لعدّ
    # شظايا التعبيرات النمطية. **وشريطُ التلميح يُبنى بـ
    # `innerHTML` وفيه وسوم** — فلم يُعرَض عليّ للترجمة قطّ.
    #
    # فبقي في كلّ صفحةٍ من الموقع، **وهو ٦٨ من ١٧١** الباقية:
    # ثلاثُ عُقَدٍ × ١٧ صفحة، وزرُّ «فهمت» × ١٧.
    #
    # ولم يكن نقصًا في القاموس ولا في المشي، بل في **ما عُرض**.
    # ومقياسٌ يعدّ ما كُتب لا يرى ما لم يُكتَب.
    # ══════════════════════════════════════════════════════════
    "الكلمات ذات الخطّ المنقّط مشروحة — مرّر المؤشّر عليها، "
    "وكذلك كل عنصر في العجلة.": (
        "Dotted-underlined words have explanations — hover over them, "
        "as well as any element in the wheel.",
        "Les mots soulignés en pointillé sont expliqués — survolez-les, "
        "ainsi que chaque élément de la roue."),
    "فهمت": ("Got it", "J'ai compris"),
    "فهمت، أخفِ هذا": ("Got it, hide this", "J'ai compris, masquer"),
    "ما هذه الصفحة؟": ("What is this page?", "Qu'est-ce que cette page ?"),
    "مرّر المؤشّر عليها": ("hover over them", "survolez-les"),
    # ══════════════════════════════════════════════════════════
    # **ما لا يبلغه المحاكي** — رسائلُ الانتظار والفراغ.
    #
    # مقياسُ الصفحة (`i18n_seen.js`) بلغ صفرًا وهذه عربيّة، لأنّها
    # **لا تُرسَم إلّا بعد حساب**، والمحاكي بلا خادم. فأمسكها
    # المقياسُ المصدريّ وحده.
    #
    # **فهما متكاملان لا متكرّران**: أحدهما يرى ما رُسم، والآخر
    # يرى ما كُتب. ومن أسقط أحدَهما لأنّ الآخر بلغ التمام أسقط
    # نصفَ ما يُرى.
    # ══════════════════════════════════════════════════════════
    "أدخل مدينة.": ("Enter a city.", "Saisissez une ville."),
    "أنت هنا الآن ·": ("You are here now ·", "Vous êtes ici ·"),
    "— أنت هنا": ("— you are here", "— vous êtes ici"),
    "المحفوظة:": ("Saved:", "Enregistrés :"),
    "بلا معطيات.": ("No data.", "Aucune donnée."),
    "ساعة": ("hour", "heure"),
    "مُرجَّح بمولدك": ("weighted by your birth chart",
                     "pondéré par votre thème natal"),
    "نزّل العجلة صورة": ("Download the wheel as an image",
                        "Télécharger la roue en image"),
    "لا أشكال زاوية في هذه اللحظة.": (
        "No aspect patterns at this moment.",
        "Aucune figure d'aspects à cet instant."),
    "لا زاوية كبرى تُقبِل في هذه المدّة.": (
        "No major aspect is applying in this period.",
        "Aucun aspect majeur ne s'applique dans cette période."),
    "لا مصطلح بهذا الاسم.": ("No term by that name.",
                            "Aucun terme de ce nom."),
    "لا يُكمّل أحدكما نقص الآخر مباشرة.": (
        "Neither of you directly completes the other's lack.",
        "Aucun de vous ne comble directement le manque de l'autre."),
    "لم يُنظر في التمام لأن المسألة رُدّت.": (
        "Perfection was not examined because the question was returned.",
        "La perfection n'a pas été examinée : la question a été renvoyée."),
    "… أحسب الخريطة": ("… computing the chart", "… calcul du thème"),
    "… أحسب مواقع الأفلاك": ("… computing planetary positions",
                            "… calcul des positions planétaires"),
    "… أحسب الشروق والغروب": ("… computing sunrise and sunset",
                              "… calcul du lever et du coucher"),
    "… أحسب أرباب الأزمنة": ("… computing the time lords",
                             "… calcul des maîtres du temps"),
    "… أنظر في خريطة اللحظة": ("… examining the chart of the moment",
                              "… examen du thème de l'instant"),

    # ══════════════════════════════════════════════════════════
    # صفحة «أين تُضبَط المعلومة؟»
    # ══════════════════════════════════════════════════════════
    "أين تُضبَط المعلومة؟": ("Where can a claim be settled?",
                            "Où une affirmation se tranche-t-elle ?"),
    "أين تُضبَط المعلومة؟ — الفَلَك": (
        "Where can a claim be settled? — Al-Falak",
        "Où une affirmation se tranche-t-elle ? — Al-Falak"),
    "الفَلَك — أين تُضبَط المعلومة؟": (
        "Al-Falak — Where can a claim be settled?",
        "Al-Falak — Où une affirmation se tranche-t-elle ?"),
    "alfalak.vercel.app · قياساتٌ يفعلها القارئ بنفسه": (
        "alfalak.vercel.app · measurements you can make yourself",
        "alfalak.vercel.app · des mesures que vous faites vous-même"),
    "قياساتٌ تفعلها بنفسك بدل أن يُقال لك": (
        "Measurements you make yourself, instead of being told",
        "Des mesures que vous faites vous-même, au lieu qu'on vous dise"),
    "في مسير النيّرين وشكل الأرض دعاوى تُتداول، ولكلٍّ منها أصحابٌ "
    "يحتجّون. ولسنا هنا لنقول لك من الصادق. هذه الصفحة تفعل شيئًا "
    "واحدًا: تضع إزاء كل دعوى": (
        "Claims circulate about the course of the luminaries and the "
        "shape of the Earth, and each has advocates who argue for it. We "
        "are not here to tell you who is right. This page does one "
        "thing: it sets beside each claim",
        "Des affirmations circulent sur la course des luminaires et la "
        "forme de la Terre, et chacune a ses défenseurs. Nous ne sommes "
        "pas ici pour vous dire qui a raison. Cette page fait une seule "
        "chose : elle place en regard de chaque affirmation"),
    "قياسًا يفصل فيها": ("a measurement that settles it",
                        "une mesure qui la tranche"),
    "— قياسًا تستطيع أنت أن تفعله، أو تجد نتيجته منشورةً يقارنها من "
    "شاء.": (
        "— one you can make yourself, or whose result is published for "
        "anyone to compare.",
        "— une mesure que vous pouvez faire, ou dont le résultat est "
        "publié et que chacun peut comparer."),
    "دعاوى في شكل الأرض ومسير النيّرين، وإزاء كلٍّ منها": (
        "Claims about the shape of the Earth and the course of the "
        "luminaries, and beside each of them",
        "Des affirmations sur la forme de la Terre et la course des "
        "luminaires, et en regard de chacune"),
    "قياسٌ تفعله بنفسك": ("a measurement you make yourself",
                         "une mesure que vous faites vous-même"),
    "— لا حكمٌ يُملى. ومنها امتحانُ هذا الموقع بتنبّؤ الكسوف.": (
        "— not a verdict handed down. Among them: testing this very site "
        "by its eclipse predictions.",
        "— non un verdict imposé. Parmi elles : éprouver ce site même "
        "par ses prédictions d'éclipses."),

    "القاعدة التي نمشي عليها": ("The rule we follow",
                               "La règle que nous suivons"),
    "الدعوى التي لا يفصل فيها قياسٌ لا تُقبَل ولا تُردّ": (
        "A claim that no measurement can settle is neither accepted nor "
        "rejected",
        "Une affirmation qu'aucune mesure ne tranche n'est ni acceptée "
        "ni rejetée"),
    "— إنّما يُقال إنّها خارج ما يُبتّ فيه.": (
        "— it is simply said to lie outside what can be decided.",
        "— on dit seulement qu'elle est hors de ce qui se décide."),
    "ونموذجٌ لا يُخرِج رقمًا يُقابَل بالرصد ليس نموذجًا": (
        "A model that yields no number to check against observation is "
        "not a model",
        "Un modèle qui ne donne aucun nombre à confronter à "
        "l'observation n'est pas un modèle"),
    "، مهما حسُنت صورته.": (", however fine its picture.",
                          ", si belle qu'en soit l'image."),
    "ونحن أوّلُ من يُمتحَن": ("And we are the first to be tested",
                            "Et nous sommes les premiers à être éprouvés"),
    ": هذا الموقع يتنبّأ بأوقات الكسوف ومقاديره وارتفاعه لأيّ مدينة. "
    "فمن أراد امتحاننا فليأخذ الرقم ويقابله.": (
        ": this site predicts eclipse times, magnitudes and altitudes "
        "for any city. Whoever wishes to test us, let him take the "
        "number and check it.",
        ": ce site prédit les heures, grandeurs et hauteurs des éclipses "
        "pour toute ville. Qui veut nous éprouver n'a qu'à prendre le "
        "nombre et le vérifier."),
    "وما نجهله نقول إنّا نجهله.": (
        "And what we do not know, we say we do not know.",
        "Et ce que nous ignorons, nous disons l'ignorer."),
    "وقد فعلنا ذلك في": ("We did so in", "Nous l'avons fait dans"),
    "حين لم نجد أصلًا لِما يُسمّى «التنجيم السومري».": (
        "when we found no source for what is called \"Sumerian "
        "astrology\".",
        "quand nous n'avons trouvé aucune source à ce qu'on appelle "
        "« l'astrologie sumérienne »."),

    "المسافات على الإسقاط السَّمْتيّ": (
        "Distances on the azimuthal projection",
        "Les distances sur la projection azimutale"),
    "١ — «الخريطة الدائرية تُري الأرض على حقيقتها»": (
        "1 — \"The circular map shows the Earth as it really is\"",
        "1 — « La carte circulaire montre la Terre telle qu'elle est »"),
    "تُعرَض خريطةٌ دائرية مركزها القطب الشمالي ومحيطها الجنوب، ويُقال "
    "إنّ هذا شكل الأرض لا إسقاطًا لها.": (
        "A circular map is shown, centred on the North Pole with the "
        "south at its rim, and it is said that this is the shape of the "
        "Earth and not a projection of it.",
        "On présente une carte circulaire centrée sur le pôle Nord, le "
        "sud à son pourtour, en disant que c'est la forme de la Terre et "
        "non une projection."),
    "القياس الفاصل: المسافات الجنوبية.": (
        "The deciding measurement: southern distances.",
        "La mesure décisive : les distances australes."),
    "هذا الإسقاط (سَمْتيّ متساوي المسافات)": (
        "This projection (azimuthal equidistant)",
        "Cette projection (azimutale équidistante)"),
    "يحفظ المسافات من مركزه وحده": (
        "preserves distances from its centre only",
        "ne conserve les distances que depuis son centre"),
    ". فبُعدُ نقطتين جنوبيّتين إحداهما عن الأخرى يخرج عليه أكبرَ من "
    "حقيقته أضعافًا.": (
        ". So the distance between two southern points comes out several "
        "times larger than it truly is.",
        ". Ainsi la distance entre deux points australes en ressort "
        "plusieurs fois plus grande qu'elle ne l'est."),
    "وهذا يُقاس بزمن رحلةٍ مباشرة": (
        "And this is measured by the duration of a direct flight",
        "Et cela se mesure par la durée d'un vol direct"),
    "— والرحلاتُ الثلاث أدناه تُباع تذاكرُها اليوم، ومدّتُها منشورة. "
    "احسب على الإسقاط وقارن.": (
        "— tickets for the routes below are sold today and their "
        "durations are published. Compute on the projection and compare.",
        "— les billets des liaisons ci-dessous se vendent aujourd'hui et "
        "leurs durées sont publiées. Calculez sur la projection et "
        "comparez."),
    "الرحلة": ("The route", "La liaison"),
    # ــ نتيجةُ الحساب: تُبنى في المتصفّح، فيراها المقياسُ من الصفحة
    #   ولا يراها المستخرِج (لأنّها داخل قالبٍ فيه `${}`) ــ
    "· على الكرة:": ("· On the sphere:", "· Sur la sphère :"),
    "· على الإسقاط السَّمْتيّ:": ("· On the azimuthal projection:",
                                "· Sur la projection azimutale :"),
    "كم": ("km", "km"),
    "كم — أي": ("km — that is", "km — soit"),
    "· والرحلة المباشرة تستغرق نحو": (
        "· And the direct flight takes about",
        "· Et le vol direct dure environ"),
    "ساعة. وبسرعة طيرانٍ معتادة (900 كم/س) يقتضي ذلك نحو": (
        "hours. At a usual cruising speed (900 km/h) that implies about",
        "heures. À une vitesse de croisière habituelle (900 km/h) cela "
        "implique environ"),
    "كم — وهو قريبٌ من الأوّل، بعيدٌ عن الثاني.": (
        "km — close to the first, far from the second.",
        "km — proche du premier, loin du second."),
    "والقياسان محسوبان الآن في متصفّحك من إحداثيات المدينتين: الأوّل "
    "بهافرساين، والثاني بمقياس الإسقاط نفسه.": (
        "Both figures are computed right now in your browser from the "
        "two cities' coordinates: the first by haversine, the second by "
        "the projection's own scale.",
        "Les deux valeurs sont calculées à l'instant dans votre "
        "navigateur à partir des coordonnées des deux villes : la "
        "première par haversine, la seconde à l'échelle de la projection "
        "elle-même."),
    # مفردةٌ تُلصَق بعدد — انظر `VOCAB_KEYS`
    "ضعفًا": ("times", "fois"),
    "جوهانسبرغ": ("Johannesburg", "Johannesburg"),
    "بيرث": ("Perth", "Perth"),
    "سانتياغو": ("Santiago", "Santiago"),
    "سِدني": ("Sydney", "Sydney"),
    "بوينس آيرس": ("Buenos Aires", "Buenos Aires"),
    "أوكلاند": ("Auckland", "Auckland"),
    "كيب تاون": ("Cape Town", "Le Cap"),
    "جوهانسبرغ ← بيرث": ("Johannesburg → Perth", "Johannesburg → Perth"),
    "سانتياغو ← سِدني": ("Santiago → Sydney", "Santiago → Sydney"),
    "بوينس آيرس ← أوكلاند": ("Buenos Aires → Auckland",
                            "Buenos Aires → Auckland"),
    "كيب تاون ← سِدني": ("Cape Town → Sydney", "Le Cap → Sydney"),
    "وليس في هذا ذمٌّ للإسقاط: هو إسقاطٌ نافع، عليه شعارُ الأمم المتحدة "
    "وخرائطُ اللاسلكي، وصفحةُ": (
        "This is no reproach to the projection: it is a useful one — the "
        "United Nations emblem and radio charts use it, and our page",
        "Ce n'est nullement un reproche à la projection : elle est "
        "utile — l'emblème des Nations unies et les cartes radio "
        "l'emploient, et notre page"),
    "عندنا تعرضه خيارًا.": ("offers it as an option.",
                          "la propose en option."),
    "وإنّما الذمُّ أن يُقرأ خريطةً للمسافات وهو لا يحفظها إلّا من "
    "مركزه.": (
        "The reproach is only to read it as a map of distances when it "
        "preserves them from its centre alone.",
        "Le reproche est seulement de la lire comme une carte des "
        "distances alors qu'elle ne les conserve que depuis son centre."),

    "٢ — «الشمس والقمر إسقاطٌ ضوئيّ لا أجسام»": (
        "2 — \"The Sun and Moon are light projections, not bodies\"",
        "2 — « Le Soleil et la Lune sont des projections lumineuses, non "
        "des corps »"),
    "يُقال إنّ ما نراه في السماء ليس جِرمًا ماديًّا، وإنّما صورةٌ "
    "تُسقَط في الجوّ.": (
        "It is said that what we see in the sky is not a material body "
        "but an image projected into the air.",
        "On dit que ce que nous voyons au ciel n'est pas un corps "
        "matériel mais une image projetée dans l'air."),
    "القياس الفاصل: القدر الزاويّ عبر النهار.": (
        "The deciding measurement: the angular size across the day.",
        "La mesure décisive : le diamètre apparent au fil du jour."),
    "جِرمٌ يدور فوق سطحٍ مستوٍ يقترب منك ويبتعد،": (
        "A body circling above a flat surface draws near and moves away,",
        "Un astre tournant au-dessus d'une surface plane s'approche puis "
        "s'éloigne,"),
    "فيتغيّر قطرُه الظاهر تغيّرًا كبيرًا": (
        "so its apparent diameter changes greatly",
        "de sorte que son diamètre apparent change fortement"),
    "— يقتضي الحسابُ نحوَ الضعف بين الظهر والغروب.": (
        "— the calculation requires roughly a factor of two between "
        "noon and sunset.",
        "— le calcul exige environ un facteur deux entre midi et le "
        "coucher."),
    "والمقيس:": ("What is measured:", "Ce qui est mesuré :"),
    "قطرُ الشمس الظاهر يبقى نحو": (
        "the Sun's apparent diameter stays at about",
        "le diamètre apparent du Soleil reste d'environ"),
    "من الشروق إلى الغروب، ولا يتغيّر إلّا بأجزاءٍ من المئة. ويُقاس "
    "بمرشِّح شمسيٍّ رخيص وآلة تصوير: صوّرها ثلاث مرّات في اليوم وقِس "
    "القرص بالبكسل.": (
        "from sunrise to sunset, varying only by fractions of a percent. "
        "It is measured with a cheap solar filter and a camera: "
        "photograph it three times in the day and measure the disc in "
        "pixels.",
        "du lever au coucher, ne variant que de fractions de pour cent. "
        "Cela se mesure avec un filtre solaire bon marché et un "
        "appareil photo : photographiez-le trois fois dans la journée et "
        "mesurez le disque en pixels."),
    "وهذا قياسٌ لا يحتاج إلى تصديق أحد: أنت تلتقط الصور، وأنت تعدّ "
    "البكسلات.": (
        "This measurement requires trusting no one: you take the "
        "photographs, and you count the pixels.",
        "Cette mesure n'exige la confiance de personne : c'est vous qui "
        "prenez les photos, et vous qui comptez les pixels."),

    "٣ — «مركزٌ واحد للسماء»": ("3 — \"A single centre for the sky\"",
                              "3 — « Un centre unique du ciel »"),
    "تُعرَض صورُ التعريض الطويل لنجوم الشمال وهي تدور حول نقطةٍ واحدة، "
    "ويُستدَلّ بها على مركزٍ واحد للفَلَك.": (
        "Long-exposure photographs of the northern stars circling one "
        "point are shown, and taken as proof of a single centre of the "
        "heavens.",
        "On montre des poses longues des étoiles du nord tournant autour "
        "d'un seul point, et l'on y voit la preuve d'un centre unique du "
        "ciel."),
    "القياس الفاصل: الجنوب.": ("The deciding measurement: the south.",
                              "La mesure décisive : le sud."),
    "صوّر السماء من جنوب خطّ الاستواء تعريضًا طويلًا. تجد النجوم تدور "
    "حول نقطةٍ أخرى — قربَ نجم": (
        "Photograph the sky south of the equator with a long exposure. "
        "You will find the stars circling another point — near the star",
        "Photographiez le ciel au sud de l'équateur en pose longue. Vous "
        "trouverez les étoiles tournant autour d'un autre point — près "
        "de l'étoile"),
    "سيغما الثُّمن (Sigma Octantis)": ("Sigma Octantis", "Sigma Octantis"),
    "وباتّجاهٍ معاكس": ("and in the opposite direction",
                       "et en sens inverse"),
    "مركزُ دورانٍ واحد لا يُخرِج مركزين متضادّين": (
        "A single centre of rotation cannot produce two opposed centres",
        "Un seul centre de rotation ne peut produire deux centres "
        "opposés"),
    "في الوقت نفسه. والصورُ متاحةٌ من مراصد الجنوب، ويلتقطها هواةٌ في "
    "تشيلي وأستراليا وجنوب إفريقيا كلَّ ليلة.": (
        "at the same time. The photographs are available from southern "
        "observatories, and amateurs in Chile, Australia and South "
        "Africa take them every night.",
        "en même temps. Les clichés sont disponibles auprès des "
        "observatoires austraux, et des amateurs au Chili, en Australie "
        "et en Afrique du Sud en prennent chaque nuit."),

    "٤ — «الكسوف لا يسبّبه القمر»": (
        "4 — \"The Moon does not cause the eclipse\"",
        "4 — « Ce n'est pas la Lune qui cause l'éclipse »"),
    "يُقال إنّ الكاسف جِرمٌ خفيّ لا يُرى، لا القمر.": (
        "It is said the eclipser is an unseen body, not the Moon.",
        "On dit que l'occulteur est un corps invisible, non la Lune."),
    "القياس الفاصل: التنبّؤ المحلّي.": (
        "The deciding measurement: local prediction.",
        "La mesure décisive : la prédiction locale."),
    "النموذج الذي نحسب به يُخرِج لكلّ مدينةٍ على الأرض:": (
        "The model we compute with yields, for every city on Earth:",
        "Le modèle avec lequel nous calculons donne, pour chaque ville "
        "de la Terre :"),
    "ساعةَ الذروة بالدقيقة": ("the time of greatest eclipse to the minute",
                            "l'heure du maximum à la minute"),
    "كم يُغطَّى من القرص": ("how much of the disc is covered",
                          "quelle part du disque est couverte"),
    "ارتفاعَ الجرم عن الأفق": ("the body's altitude above the horizon",
                             "la hauteur de l'astre au-dessus de "
                             "l'horizon"),
    ". وهي أرقامٌ تُكذَّب بسهولة لو كانت خطأً.": (
        ". These are numbers easily falsified if they were wrong.",
        ". Ce sont des nombres aisément démentis s'ils étaient faux."),
    "وصفحةُ": ("And the page", "Et la page"),
    "تُخرجها لك. أمثلة مُقابَلة:": ("gives them to you. Checked examples:",
                                  "vous les donne. Exemples vérifiés :"),
    "· الأقصر، ٢ آب ٢٠٢٧ —": ("· Luxor, 2 August 2027 —",
                             "· Louxor, 2 août 2027 —"),
    "· مدريد، ١٢ آب ٢٠٢٦ — جزئي، القدر": (
        "· Madrid, 12 August 2026 — partial, magnitude",
        "· Madrid, 12 août 2026 — partielle, grandeur"),
    "· نيويورك، ٨ نيسان ٢٠٢٤ — جزئي، القدر": (
        "· New York, 8 April 2024 — partial, magnitude",
        "· New York, 8 avril 2024 — partielle, grandeur"),
    "، القدر": (", magnitude", ", grandeur"),
    "، ارتفاع": (", altitude", ", hauteur"),
    "ونحن نُمتحَن بهذا لا نحتجّ به": (
        "We are tested by this; we do not argue from it",
        "Nous sommes éprouvés par cela ; nous n'en argumentons pas"),
    ": خذ الرقم، واذهب إلى المدينة أو اسأل من كان فيها. فإن أخطأنا "
    "فالنموذج الذي نحسب به خطأ، ويلزمنا تغييرُه.": (
        ": take the number, go to the city or ask someone who was there. "
        "If we are wrong, the model we compute with is wrong, and we are "
        "bound to change it.",
        ": prenez le nombre, allez sur place ou demandez à qui y était. "
        "Si nous nous trompons, le modèle avec lequel nous calculons est "
        "faux, et il nous faut le changer."),

    "٥ — «ما لا يفصل فيه قياس»": (
        "5 — \"What no measurement can settle\"",
        "5 — « Ce qu'aucune mesure ne tranche »"),
    "وثمّة دعاوى لا نضع إزاءها شيئًا، لأنّها": (
        "There are claims beside which we set nothing, because they",
        "Il est des affirmations en regard desquelles nous ne mettons "
        "rien, parce qu'elles"),
    "لا تُخرِج رقمًا يُقابَل": ("yield no number that can be checked",
                             "ne donnent aucun nombre vérifiable"),
    ": من قال إنّ كلّ صورةٍ مزوّرة وكلّ رحلةٍ ملفَّقة وكلّ قياسٍ مدسوس، "
    "فقد وضع دعواه خارج ما يُبتّ فيه.": (
        ": whoever says that every photograph is forged, every flight "
        "fabricated and every measurement planted, has placed his claim "
        "outside what can be decided.",
        ": qui affirme que toute photographie est truquée, tout vol "
        "inventé et toute mesure falsifiée, a placé son affirmation hors "
        "de ce qui se décide."),
    "ولا نُسمّي ذلك كذبًا ولا صدقًا": (
        "We call that neither false nor true",
        "Nous n'appelons cela ni faux ni vrai"),
    "— نقول إنّه خارج ما تفصل فيه هذه الصفحة، وهذا كلُّ ما نستطيع قوله "
    "بإنصاف.": (
        "— we say it lies outside what this page can settle, and that is "
        "all we can fairly say.",
        "— nous disons que cela est hors de ce que cette page peut "
        "trancher, et c'est tout ce que nous pouvons dire avec équité."),

    "المسافات محسوبة بصيغة هافرساين على نصف قطر ٦٣٧١ كم، والمقارنة على "
    "الإسقاط السَّمْتيّ محسوبة من الصفحة نفسها لا منقولة.": (
        "Distances are computed with the haversine formula on a radius "
        "of 6371 km, and the azimuthal comparison is computed by this "
        "page itself, not quoted.",
        "Les distances sont calculées par la formule de haversine sur un "
        "rayon de 6371 km, et la comparaison azimutale est calculée par "
        "la page elle-même, non citée."),
    "وأزمنة الرحلات المذكورة من جداول الطيران المنشورة، وهي تتبدّل "
    "بتبدّل الطائرة والرياح.": (
        "The flight times given are from published airline schedules, "
        "and they vary with aircraft and winds.",
        "Les durées de vol indiquées proviennent des horaires publiés, "
        "et varient selon l'appareil et les vents."),

    # ــ خرائط الأرض: تسمية الإسقاطين ــ
    "منظر القطب": ("Polar view", "Vue polaire"),
    "الإسقاط": ("projection", "projection"),
    "منظر القطب — إسقاطٌ سَمْتيٌّ متساوي المسافات، مركزه القطب": (
        "Polar view — an azimuthal equidistant projection, centred on "
        "the North",
        "Vue polaire — projection azimutale équidistante, centrée sur le "
        "pôle"),
    "الشمالي. عليه شعار الأمم المتحدة وخرائط الطيران واللاسلكي.": (
        "Pole. The United Nations emblem, aviation and radio charts use "
        "it.",
        "Nord. L'emblème des Nations unies, les cartes aéronautiques et "
        "radio l'emploient."),
    "وفيه: المركز شمال، والمحيط جنوب، والشرق عكس عقارب الساعة.": (
        "On it: the centre is north, the rim is south, and east runs "
        "counter-clockwise.",
        "Sur elle : le centre est au nord, le pourtour au sud, et l'est "
        "va dans le sens antihoraire."),
    "ويحفظ المسافات من المركز وحده — فبُعد نقطتين جنوبيّتين": (
        "And it preserves distances from the centre alone — so the "
        "distance between two southern points",
        "Et elle ne conserve les distances que depuis le centre — la "
        "distance entre deux points australes"),
    "إحداهما عن الأخرى يخرج عليه أضعافَ حقيقته.": (
        "comes out several times its true value.",
        "en ressort plusieurs fois sa valeur réelle."),
    "الإسقاط المستطيل — خطوط الطول والعرض فيه مستقيمة متعامدة،": (
        "The rectangular projection — its meridians and parallels are "
        "straight and perpendicular,",
        "La projection rectangulaire — ses méridiens et parallèles sont "
        "droits et perpendiculaires,"),
    "ويمطّ المسافات كلّما بعُدتَ عن خطّ الاستواء: غرينلاند": (
        "and it stretches distances the further you go from the "
        "equator: Greenland",
        "et elle étire les distances à mesure que l'on s'éloigne de "
        "l'équateur : le Groenland"),
    "فيه بحجم إفريقيا، وهي أصغر منها أربعةَ عشرَ ضعفًا.": (
        "appears the size of Africa on it, though it is fourteen times "
        "smaller.",
        "y paraît de la taille de l'Afrique, alors qu'il est quatorze "
        "fois plus petit."),
    "الحساب من المطالع المستقيمة والمَيْل والوقت النجمي بغرينتش، "
    "والمدن من أطلس الموقع نفسه.": (
        "Computed from right ascensions, declination and Greenwich "
        "sidereal time; the cities come from this site's own atlas.",
        "Calculé à partir des ascensions droites, de la déclinaison et "
        "du temps sidéral de Greenwich ; les villes viennent de l'atlas "
        "du site."),
    ": مستطيلٌ أو سَمْتيٌّ مركزه القطب. وكلُّ إسقاطٍ يحفظ شيئًا ويُفسد "
    "شيئًا، فليس أحدهما شكلَ الأرض — وتفصيلُ ذلك في": (
        ": rectangular, or azimuthal centred on the pole. Every "
        "projection preserves something and spoils something, so neither "
        "is the shape of the Earth — the details are in",
        ": rectangulaire, ou azimutale centrée sur le pôle. Toute "
        "projection conserve une chose et en fausse une autre : aucune "
        "n'est la forme de la Terre — le détail se trouve dans"),

    # ══════════════════════════════════════════════════════════
    # مختبر السماء — آلة الزمن
    # ══════════════════════════════════════════════════════════
    "مختبر السماء": ("Sky Lab", "Laboratoire du ciel"),
    "مختبر السماء — الفَلَك": ("Sky Lab — Al-Falak",
                              "Laboratoire du ciel — Al-Falak"),
    "الفَلَك — مختبر السماء": ("Al-Falak — Sky Lab",
                              "Al-Falak — Laboratoire du ciel"),
    "كيف تتحرّك السماء؟": ("How does the sky move?",
                          "Comment le ciel se meut-il ?"),
    "عجلةٌ تتقدّم بالزمن وتتأخّر — ترى مسير الكواكب ورجوعها بعينك": (
        "A wheel that runs time forward and back — watch the planets "
        "move and turn retrograde with your own eyes",
        "Une roue qui avance et recule dans le temps — voyez de vos yeux "
        "les planètes marcher et rétrograder"),
    "قدّم الزمن وانظر السماء تتحرّك": (
        "Run time forward and watch the sky move",
        "Avancez le temps et regardez le ciel bouger"),
    "قدّم الزمن أو أخّره — بالدقيقة أو الساعة أو اليوم أو السنة — وانظر "
    "كيف تسير الكواكب في البروج. والمرسوم هنا ليس نموذجًا للعالم، بل "
    "جدولُ ما ستراه في السماء: في أيّ جهةٍ من الفَلَك يقع كلُّ جرم، "
    "وهو ما يُرصَد ويُقاس.": (
        "Run time forward or back — by the minute, the hour, the day or "
        "the year — and watch the planets move through the signs. What "
        "is drawn here is not a model of the world but a table of what "
        "you will see in the sky: in which direction of the heavens each "
        "body lies. That is what is observed and measured.",
        "Avancez ou reculez le temps — à la minute, à l'heure, au jour "
        "ou à l'année — et regardez les planètes parcourir les signes. "
        "Ce qui est tracé ici n'est pas un modèle du monde, mais une "
        "table de ce que vous verrez au ciel : dans quelle direction du "
        "firmament se tient chaque astre. Voilà ce qui s'observe et se "
        "mesure."),
    "عجلةٌ تتحرّك بالزمن: قدّم الساعة أو اليوم أو السنة وانظر كيف تسير "
    "الكواكب في البروج، ومتى ترجع. والمرسوم جهةُ الجرم كما تُرى.": (
        "A wheel that moves with time: advance the hour, the day or the "
        "year and watch how the planets travel through the signs, and "
        "when they turn retrograde. What is drawn is the body's "
        "direction as seen.",
        "Une roue qui se meut avec le temps : avancez l'heure, le jour "
        "ou l'année et voyez les planètes parcourir les signes, et quand "
        "elles rétrogradent. Ce qui est tracé est la direction de "
        "l'astre telle qu'on la voit."),
    "عجلةٌ تتحرّك بالزمن: قدّم الساعة أو اليوم أو السنة وانظر كيف تسير": (
        "A wheel that moves with time: advance the hour, the day or the "
        "year and watch how",
        "Une roue qui se meut avec le temps : avancez l'heure, le jour "
        "ou l'année et voyez"),
    "الكواكب في البروج، ومتى ترجع. والمرسوم جهةُ الجرم كما تُرى.": (
        "the planets travel through the signs, and when they turn "
        "retrograde. What is drawn is the body's direction as seen.",
        "les planètes parcourir les signes, et quand elles rétrogradent. "
        "Ce qui est tracé est la direction de l'astre telle qu'on la voit."),
    "عجلةٌ تتحرّك بالزمن: قدّم الساعة أو اليوم أو السنة، وانظر مسير كل "
    "كوكب في البروج ومتى يرجع.": (
        "A wheel that moves with time: advance the hour, the day or the "
        "year, and watch each planet's course through the signs and when "
        "it turns retrograde.",
        "Une roue qui se meut avec le temps : avancez l'heure, le jour "
        "ou l'année, et suivez la course de chaque planète dans les "
        "signes et le moment où elle rétrograde."),
    "ابدأ من": ("Start from", "Commencer le"),
    "الخطوة": ("Step", "Pas"),
    "خطوة": ("step", "pas"),
    "أسبوع": ("Week", "Semaine"),
    "دقيقة": ("Minute", "Minute"),
    "يوم": ("Day", "Jour"),
    "سنة": ("Year", "Année"),
    "الزمن": ("Time", "Temps"),
    "السرعة": ("Speed", "Vitesse"),
    "بطيء": ("Slow", "Lent"),
    "وسط": ("Medium", "Moyen"),
    "كلّي": ("total", "totale"),
    "مستطيل": ("Rectangular", "Rectangulaire"),
    "إسقاط": ("projection", "projection"),
    "والخريطة": ("And the map is a", "Et la carte est une"),
    "▶ تشغيل": ("▶ Play", "▶ Lecture"),
    "⏸ إيقاف": ("⏸ Pause", "⏸ Pause"),
    "تشغيل": ("Play", "Lecture"),
    "سريع": ("Fast", "Rapide"),
    "أخفِ الأثر": ("Hide the trail", "Masquer la trace"),
    "أظهر الأثر": ("Show the trail", "Afficher la trace"),
    "إلى الآن": ("To now", "À maintenant"),
    "… أحسب مسير الأجرام": ("… computing the bodies' courses",
                           "… calcul de la course des astres"),
    "الأثر الباهت": ("The faint trail", "La trace pâle"),
    "هو مسار الجرم في اللقطات السابقة. وحين يرتدّ إلى الوراء فذلك": (
        "is the body's path across the previous frames. When it doubles "
        "back, that is",
        "est le chemin de l'astre sur les images précédentes. Quand il "
        "revient en arrière, c'est"),
    "— يُرسَم الجرم أحمر ومعه حرف «ر». والرجوع ليس توقّفًا في السماء: "
    "هو ما نراه من جهةٍ نحن فيها نتحرّك أيضًا.": (
        "— the body is drawn in red with the letter «ر». Retrogradation "
        "is not a halt in the sky: it is what we see from a place that "
        "is itself moving.",
        "— l'astre est tracé en rouge avec la lettre « ر ». La "
        "rétrogradation n'est pas un arrêt dans le ciel : c'est ce que "
        "l'on voit depuis un lieu qui se meut lui aussi."),
    "المواقع محسوبة بمكتبة Swiss Ephemeris لحظةً بلحظة، لا من جدولٍ "
    "مخزون.": (
        "Positions are computed moment by moment with the Swiss "
        "Ephemeris library, not read from a stored table.",
        "Les positions sont calculées instant par instant avec la "
        "bibliothèque Swiss Ephemeris, non lues dans une table."),
    "والمرسوم طولٌ في دائرة البروج: جهةُ الجرم كما تُرى، لا مسافتُه ولا "
    "مساره في الفضاء.": (
        "What is drawn is a longitude on the ecliptic: the body's "
        "direction as seen — not its distance, nor its path through "
        "space.",
        "Ce qui est tracé est une longitude sur l'écliptique : la "
        "direction de l'astre telle qu'on la voit — non sa distance, ni "
        "sa trajectoire dans l'espace."),

    # ══════════════════════════════════════════════════════════
    # صفحةُ الكسوف والخسوف
    # ══════════════════════════════════════════════════════════
    "الكسوف والخسوف": ("Eclipses", "Éclipses"),
    "الكسوف والخسوف — الفَلَك": ("Eclipses — Al-Falak",
                                "Éclipses — Al-Falak"),
    "الفَلَك — الكسوف والخسوف": ("Al-Falak — Eclipses",
                                "Al-Falak — Éclipses"),
    "متى الكسوف؟": ("When is the eclipse?", "Quand l'éclipse ?"),
    "كسوفات الشمس وخسوفات القمر، وهل تُرى من مدينتك — ولماذا لا "
    "يكسف كل شهر": (
        "Solar and lunar eclipses, whether they are visible from your "
        "city — and why there is not one every month",
        "Éclipses de Soleil et de Lune, visibles ou non depuis votre "
        "ville — et pourquoi il n'y en a pas chaque mois"),
    "لأيّ سنة ومكان: العقدة وسلسلة ساروس والمقدار، وهل يُرى من "
    "مدينتك — ولماذا لا يكسف كل شهر.": (
        "For any year and place: the node, the Saros series, the "
        "magnitude, and whether it is visible from your city — and why "
        "there is not one every month.",
        "Pour toute année et tout lieu : le nœud, la série de Saros, la "
        "grandeur, et la visibilité depuis votre ville — et pourquoi il "
        "n'y en a pas chaque mois."),
    "يجتمع النيّران اثنتي عشرة مرّةً في السنة ولا يكسفان إلّا مرّتين "
    "أو ثلاثًا. والفارقُ هو العقدة: حيث يقطع مسير القمر دائرةَ "
    "البروج. وهذه الصفحة تحسب الكسوفات لأيّ مدّة ومكان، وتعرض عليك "
    "القاعدة لتمتحنها بنفسك.": (
        "The two luminaries meet twelve times a year, yet eclipse only "
        "twice or thrice. The difference is the node: where the Moon's "
        "path crosses the ecliptic. This page computes eclipses for any "
        "period and place, and lays the rule before you to test yourself.",
        "Les deux luminaires se rejoignent douze fois par an et ne "
        "s'éclipsent que deux ou trois fois. La différence tient au "
        "nœud : là où la route de la Lune coupe l'écliptique. Cette page "
        "calcule les éclipses pour toute période et tout lieu, et vous "
        "soumet la règle pour que vous l'éprouviez vous-même."),
    "يجتمع النيّران اثنتي عشرة مرّةً في السنة ولا يكسفان إلّا مرّتين": (
        "The two luminaries meet twelve times a year, yet eclipse only "
        "twice",
        "Les deux luminaires se rejoignent douze fois par an et ne "
        "s'éclipsent que deux"),
    "أو ثلاثًا. والفارقُ هو العقدة، وهذه الصفحة تحسبها وتعرض القاعدة": (
        "or thrice. The difference is the node; this page computes it "
        "and lays out the rule",
        "ou trois fois. La différence tient au nœud ; cette page le "
        "calcule et expose la règle"),
    "لتمتحنها بنفسك.": ("for you to test yourself.",
                       "pour que vous l'éprouviez vous-même."),
    # **ونصُّ «ما هذه الصفحة؟» كما يُرسَم لا كما يُكتَب.**
    # هو في `plain.js` ثلاثةُ نصوصٍ موصولة بـ`+`، فيراها المُستخرَج
    # ثلاثًا وتراها الصفحةُ واحدة. والمفتاحُ ما تراه الصفحة.
    "يجتمع النيّران اثنتي عشرة مرّةً في السنة ولا يكسفان إلّا مرّتين "
    "أو ثلاثًا. والفارقُ هو العقدة، وهذه الصفحة تحسبها وتعرض القاعدة "
    "لتمتحنها بنفسك.": (
        "The two luminaries meet twelve times a year, yet eclipse only "
        "twice or thrice. The difference is the node; this page computes "
        "it and lays out the rule for you to test yourself.",
        "Les deux luminaires se rejoignent douze fois par an et ne "
        "s'éclipsent que deux ou trois fois. La différence tient au "
        "nœud ; cette page le calcule et expose la règle pour que vous "
        "l'éprouviez vous-même."),
    "من سنة": ("From year", "De l'année"),
    "إلى سنة": ("To year", "À l'année"),
    "دمشق، القاهرة…": ("Damascus, Cairo…", "Damas, Le Caire…"),
    "تاريخ مولدك (اختياري)": ("Your birth date (optional)",
                             "Votre date de naissance (facultatif)"),
    "اعرض الكسوفات": ("Show eclipses", "Afficher les éclipses"),
    "ما يُرى من مدينتي فقط": ("Only what is visible from my city",
                             "Seulement ce qui est visible de ma ville"),
    "اعرض الكل": ("Show all", "Tout afficher"),
    "لماذا لا يكسف كل شهر؟": ("Why not every month?",
                             "Pourquoi pas chaque mois ?"),
    "دورة ساروس": ("The Saros cycle", "Le cycle de Saros"),
    "الجوزهر والتنّين": ("Al-Jawzahr and the Dragon",
                        "Al-Jawzahr et le Dragon"),
    "كسوف الشمس": ("Solar eclipses", "Éclipses de Soleil"),
    "خسوف القمر": ("Lunar eclipses", "Éclipses de Lune"),
    "خسوف": ("Lunar eclipse", "Éclipse de Lune"),
    "كسوف": ("Solar eclipse", "Éclipse de Soleil"),
    "الجدول": ("The table", "Le tableau"),
    "شمسي": ("solar", "solaire"),
    "مدينتك": ("your city", "votre ville"),
    "لا يُرى من مدينتك": ("Not visible from your city",
                         "Non visible depuis votre ville"),
    "لا كسوف في هذه المدّة.": ("No eclipse in this period.",
                              "Aucune éclipse dans cette période."),
    "… أحسب الكسوفات": ("… computing eclipses", "… calcul des éclipses"),
    "… أتتبّع السلسلة": ("… tracing the series", "… suivi de la série"),
    "· السلسلة نفسها ✓": ("· same series ✓", "· même série ✓"),
    "· سلسلة أخرى": ("· another series", "· autre série"),
    "العقدة وساروس، وهل يُرى من مدينتك": (
        "The node and Saros, and whether it is visible from your city",
        "Le nœud et Saros, et la visibilité depuis votre ville"),
    "المواقع والأوقات محسوبة بمكتبة Swiss Ephemeris، وأرقام سلاسل "
    "ساروس منها لا من صيغة عندنا.": (
        "Positions and times are computed with the Swiss Ephemeris "
        "library, and the Saros series numbers come from it, not from a "
        "formula of ours.",
        "Positions et horaires sont calculés avec la bibliothèque Swiss "
        "Ephemeris, et les numéros de série de Saros en proviennent, non "
        "d'une formule de notre cru."),
    "والأحكام في آخر كل بطاقة منقولةٌ عن كتب القوم، لا نتيجةَ رصد.": (
        "The judgements at the foot of each card are transmitted from "
        "the old books; they are not the result of observation.",
        "Les jugements au bas de chaque fiche sont transmis des livres "
        "anciens ; ils ne résultent pas de l'observation."),
    "المصادر: أغطية التوابيت المصرية وسقفُ مقبرة سنموت · «مول أبين» "
    "و«إينوما آنو إنليل» · «الأربعة» لبطلَميوس · «التفهيم» للبيروني "
    "· «المناظر» لابن الهيثم.": (
        "Sources: Egyptian coffin lids and the ceiling of Senenmut's "
        "tomb · MUL.APIN and Enūma Anu Enlil · Ptolemy's Tetrabiblos · "
        "al-Bīrūnī's al-Tafhīm · Ibn al-Haytham's Book of Optics.",
        "Sources : couvercles de sarcophages égyptiens et plafond de la "
        "tombe de Senenmout · MUL.APIN et Enūma Anu Enlil · la "
        "Tétrabible de Ptolémée · al-Tafhīm d'al-Bīrūnī · le Traité "
        "d'optique d'Ibn al-Haytham."),

    # مفردةٌ تُلصَق بعدد — انظر `VOCAB_KEYS`
    "مصطلحًا": ("terms", "termes"),
    # ورسالةُ العطل يتبدّل ذيلُها بنصّ الخادم، فتُعامَل مفردةً
    "تعذّر الاتصال بالخادم": ("Could not reach the server",
                              "Connexion au serveur impossible"),

    # ══════════════════════════════════════════════════════════
    # **صدور الصفحات وذيولها** — كلامُ الموقع عن نفسه.
    # وهذه أُخذت من `tools/i18n_seen.js --keys`، أي **من الصفحة
    # المرسومة** لا من استخراج المصدر. فما هنا يُطابَق قطعًا.
    # ══════════════════════════════════════════════════════════
    "خريطة الميلاد صورة للسماء لحظة ولادتك: أين كان كل كوكب، "
    "وأيّ برج كان صاعدًا في": (
        "The natal chart is a picture of the sky at the moment you were "
        "born: where each planet stood, and which sign was rising on",
        "Le thème natal est une image du ciel à l'instant de votre "
        "naissance : où se tenait chaque planète, et quel signe se levait à"),
    ". منها تُقرأ الطباع والميول.": (
        ". From it character and inclination are read.",
        ". On y lit le caractère et les inclinations."),
    "والسهام والمنازل من التراث الفلكي العربي.": (
        "and the lots and mansions from the Arabic astrological tradition.",
        "et les parts et les manoirs de la tradition astrologique arabe."),
    "والاختيارات من تراث الأنواء العربي.": (
        "and the elections from the Arabic anwāʾ tradition.",
        "et les élections de la tradition arabe des anwāʾ."),

    # **والنصُّ الكامل كما هو في `plain.js`** — لا شقُّه.
    # كان مفتاحي شظيّةً تنتهي عند «أين»، لأنّ `hint.js` يَسِم
    # «القمر» فيشقّ العُقدة. وبعد أن صار التطابق على العنصر
    # كلِّه صار المطلوب الجملةَ تامّة.
    "النشرة اليومية تصف حال السماء في يوم بعينه: أين القمر، وما "
    "الأوقات المناسبة وما يُفضّل تأجيله.": (
        "The daily bulletin describes the state of the sky on a given "
        "day: where the Moon is, which hours suit, and what is better "
        "postponed.",
        "Le bulletin quotidien décrit l'état du ciel un jour donné : où "
        "est la Lune, quelles heures conviennent, et ce qu'il vaut mieux "
        "différer."),
    "خريطة الميلاد صورة للسماء لحظة ولادتك: أين كان كل كوكب، وأيّ برج "
    "كان صاعدًا في الأفق. منها تُقرأ الطباع والميول.": (
        "The natal chart is a picture of the sky at the moment you were "
        "born: where each planet stood, and which sign was rising on the "
        "horizon. From it character and inclination are read.",
        "Le thème natal est une image du ciel à l'instant de votre "
        "naissance : où se tenait chaque planète, et quel signe se levait "
        "à l'horizon. On y lit le caractère et les inclinations."),
    "النشرة اليومية تصف حال السماء في يوم بعينه: أين": (
        "The daily bulletin describes the state of the sky on a given day: "
        "where",
        "Le bulletin quotidien décrit l'état du ciel un jour donné : où"),
    "، وما الأوقات المناسبة وما يُفضّل تأجيله.": (
        ", which hours suit, and what is better postponed.",
        ", quelles heures conviennent, et ce qu'il vaut mieux différer."),
    "النشرة الشهرية تجمع أحداث الشهر كلّه: انتقالات الكواكب، والكسوف، "
    "وأفضل أيام الشهر لكل غرض.": (
        "The monthly bulletin gathers the whole month's events: planetary "
        "ingresses, eclipses, and the month's best days for each purpose.",
        "Le bulletin mensuel rassemble les événements du mois : ingrès "
        "planétaires, éclipses, et les meilleurs jours pour chaque fin."),

    "خريطتك سماءُ لحظةٍ واحدة، مرئيّةً من مكانٍ واحد. ولو وُلدتَ في "
    "اللحظة نفسها في مكانٍ آخر لكانت الكواكب هي هي — لكن أوتادها "
    "تختلف: ما كان طالعًا يصير في وسط السماء، وما كان غاربًا يصير "
    "طالعًا. فلكل كوكبٍ على وجه الأرض أربعة خطوط.": (
        "Your chart is the sky of a single moment, seen from a single "
        "place. Had you been born at the same moment elsewhere, the "
        "planets would be the same — but the angles would differ: what "
        "was rising becomes culminating, and what was setting becomes "
        "rising. So every planet has four lines across the Earth.",
        "Votre thème est le ciel d'un seul instant, vu d'un seul lieu. "
        "Né au même instant ailleurs, vous auriez les mêmes planètes — "
        "mais d'autres angles : ce qui se levait culmine, ce qui se "
        "couchait se lève. Chaque planète trace ainsi quatre lignes sur "
        "la Terre."),

    "خريطة الميلاد تقول ما أنت، ولا تقول متى. وأرباب الأزمنة جواب "
    "«متى»: تقسيم العمر على الكواكب، فيتولّى كلٌّ منها فترة يصبغها "
    "بطبعه. الفردارات فارسية نقلها أبو معشر، والتسيير أقدم منها.": (
        "The natal chart says what you are; it does not say when. The "
        "time lords answer \"when\": the lifetime is divided among the "
        "planets, each governing a span it colours with its own nature. "
        "The firdaria are Persian, transmitted by Abū Maʿshar; direction "
        "is older still.",
        "Le thème natal dit ce que vous êtes, non pas quand. Les maîtres "
        "du temps répondent au « quand » : la vie est partagée entre les "
        "planètes, chacune gouvernant une période qu'elle teinte de sa "
        "nature. Les firdaria sont persans, transmis par Abū Maʿshar ; "
        "la direction est plus ancienne encore."),

    "تقويم الشهر يُجيب عن «كيف حال هذا اليوم؟». وهذه الصفحة تُجيب عن "
    "السؤال المعكوس، وهو الذي يسأله الناس فعلًا: أعطني أفضل يوم. "
    "تمسح الشهور القادمة، وتُعطي مع كل يوم ساعته — فالقدماء يختارون "
    "الساعة كما يختارون اليوم.": (
        "The monthly calendar answers \"how is this day?\". This page "
        "answers the reverse — the question people actually ask: give me "
        "the best day. It scans the coming months and gives each day its "
        "hour, for the ancients elected the hour as they elected the day.",
        "Le calendrier mensuel répond à « comment est ce jour ? ». Cette "
        "page répond à l'inverse, la question réellement posée : donnez-"
        "moi le meilleur jour. Elle balaie les mois à venir et donne à "
        "chaque jour son heure — les anciens élisaient l'heure autant que "
        "le jour."),

    "مبنى هذا الباب أن السؤال إذا اضطرم في صدر صاحبه فسأل، كانت "
    "السماء في تلك اللحظة صورةً لجوابه. ولا يُحكم فيه بالمزاج: تُنظر "
    "الاعتبارات أوّلًا، فإن كان في الخريطة ما يمنع رُدّت المسألة ولم "
    "يُتكلَّف لها جواب. ثم يُنظر في دليل السائل ودليل المسؤول عنه: "
    "أيقع بينهما اتّصال قبل أن يخرج أحدهما من برجه؟": (
        "This art rests on the premise that when a question burns in its "
        "asker and he asks, the sky at that moment is an image of its "
        "answer. It is not judged by whim: the considerations are "
        "examined first, and if the chart forbids, the question is "
        "returned and no answer is forced. Then the significators of "
        "querent and quesited are examined: does an aspect perfect "
        "between them before either leaves its sign?",
        "Cet art repose sur ce principe : quand une question brûle celui "
        "qui la pose, le ciel de cet instant est l'image de sa réponse. "
        "On n'y juge pas au gré : les considérations viennent d'abord, "
        "et si le thème l'interdit, la question est renvoyée sans "
        "réponse forcée. Puis on examine les significateurs du "
        "consultant et du sujet : un aspect se perfectionne-t-il entre "
        "eux avant que l'un quitte son signe ?"),
    "الوقت هنا هو لحظة وقوع السؤال في نفسك، لا وقت فتحك للصفحة. "
    "وكلّما كان السؤال مصوغًا صياغة دقيقة كان الجواب أوضح — وأكثر "
    "الحيرة تنحلّ بصياغة السؤال وحدها.": (
        "The time here is the moment the question arose in you, not the "
        "moment you opened this page. The more precisely the question is "
        "framed, the clearer the answer — and most perplexity dissolves "
        "in the framing alone.",
        "L'heure est ici celle où la question a surgi en vous, non celle "
        "où vous avez ouvert la page. Mieux la question est formulée, "
        "plus la réponse est claire — et la plupart des perplexités se "
        "dénouent dans la seule formulation."),
    "من «التفهيم» للبيروني و«البارع» لابن أبي الرجال.": (
        "from al-Bīrūnī's al-Tafhīm and Ibn Abī al-Rijāl's al-Bāriʿ.",
        "d'après al-Tafhīm d'al-Bīrūnī et al-Bāriʿ d'Ibn Abī al-Rijāl."),
    "على ريجومونتانوس، وهو مذهب أهل هذا الباب.": (
        "on Regiomontanus, the method of this art's practitioners.",
        "sur Regiomontanus, méthode des praticiens de cet art."),
    "الاعتبارات وقواعد": ("The considerations and the rules of",
                          "Les considérations et les règles de"),

    "قسّم القدماء النهار اثنتي عشرة ساعة والليل مثلها، ونسبوا كل "
    "ساعة إلى كوكب. فلكل ساعة طبع، ولكل عمل ساعة تناسبه.": (
        "The ancients divided the day into twelve hours and the night "
        "likewise, assigning each hour to a planet. Every hour has its "
        "nature, and every undertaking its fitting hour.",
        "Les anciens divisaient le jour en douze heures et la nuit de "
        "même, attribuant chaque heure à une planète. Chaque heure a sa "
        "nature, et chaque entreprise son heure propre."),

    "قسّم القدماء البدن على البروج: الحملُ الرأس، والحوتُ القدمان، "
    "وما بينهما بالترتيب. وردّوه إلى أربعة أخلاط لكلٍّ حرارةٌ ورطوبة. "
    "وهذه الصفحة تعرض ذلك كما قالوه — ومنه ما يُحسَب بقاعدة، ومنه ما "
    "هو حكايةُ زمن.": (
        "The ancients divided the body among the signs: Aries the head, "
        "Pisces the feet, and the rest in order. They referred it to four "
        "humours, each with its heat and moisture. This page presents "
        "that as they stated it — some of it computed by rule, some of "
        "it the record of an age.",
        "Les anciens répartissaient le corps entre les signes : le "
        "Bélier la tête, les Poissons les pieds, et le reste dans "
        "l'ordre. Ils le ramenaient à quatre humeurs, chacune avec sa "
        "chaleur et son humidité. Cette page l'expose tel qu'ils l'ont "
        "dit — pour partie calculé par règle, pour partie témoignage "
        "d'une époque."),
    "المصادر: «الأربعة» لبطلَميوس (المقالة الثالثة) · جالينوس في "
    "الأخلاط · ونقلُ أطبّاء العرب عنهما. ونظريةُ الأخلاط تجاوزها "
    "الطبّ منذ قرنٍ ونصف.": (
        "Sources: Ptolemy's Tetrabiblos (Book III) · Galen on the "
        "humours · and the Arab physicians' transmission of both. "
        "Humoral theory was left behind by medicine a century and a half "
        "ago.",
        "Sources : la Tétrabible de Ptolémée (livre III) · Galien sur "
        "les humeurs · et leur transmission par les médecins arabes. La "
        "théorie humorale a été abandonnée par la médecine il y a un "
        "siècle et demi."),

    "اثنا عشر ملحًا معدنيًّا عند الطبيب الألماني فيلهلم شوسلر، ربطها "
    "الأمريكي جورج كيري بالبروج الاثني عشر بعده بأربعين سنة. وهذه "
    "صفحة تاريخِ فكرة، لا تشخيصٍ ولا دواء.": (
        "Twelve mineral salts, from the German physician Wilhelm "
        "Schüßler; the American George W. Carey linked them to the "
        "twelve signs forty years later. This is the history of an idea "
        "— not diagnosis, not treatment.",
        "Douze sels minéraux, du médecin allemand Wilhelm Schüßler ; "
        "l'Américain George W. Carey les a rattachés aux douze signes "
        "quarante ans plus tard. Ceci est l'histoire d'une idée — ni "
        "diagnostic, ni traitement."),

    "ساعاتُ يومك الأربع والعشرون جاءت من مصر، وبروجُك من بابل. وهذه "
    "الصفحة تاريخٌ موثّق لا حُكم: من أين جاء ما نحسبه في سائر "
    "الصفحات، وما لم يصلنا منه شيء — فيُقال إنه لم يصل.": (
        "Your day's twenty-four hours came from Egypt, and your signs "
        "from Babylon. This page is documented history, not judgement: "
        "where what we compute on the other pages came from, and what "
        "did not reach us — of which we say it did not.",
        "Les vingt-quatre heures de votre journée viennent d'Égypte, et "
        "vos signes de Babylone. Cette page est une histoire documentée, "
        "non un jugement : d'où vient ce que nous calculons ailleurs, et "
        "ce qui ne nous est pas parvenu — dont nous disons qu'il ne l'est "
        "pas."),

    "مواليد أعلامٍ من العرب والعالم. وما نعرضه محدود عمدًا: ساعةُ "
    "ميلاد هؤلاء لا تُعرَف، فلا طالعَ لهم هنا ولا بيوت — وأكثر "
    "المواقع تضع الساعة ١٢:٠٠ وترسم عجلةً كاملة، والطالع يدور اثنتي "
    "عشرة مرّةً في اليوم.": (
        "Birth data of figures from the Arab world and beyond. What we "
        "show is deliberately limited: their birth hours are unknown, so "
        "there is no Ascendant here and no houses — while most sites set "
        "the hour to 12:00 and draw a full wheel, though the Ascendant "
        "turns twelve times a day.",
        "Naissances de figures du monde arabe et d'ailleurs. Ce que nous "
        "montrons est délibérément limité : leur heure de naissance est "
        "inconnue, donc ni Ascendant ni maisons ici — alors que la "
        "plupart des sites fixent 12:00 et tracent une roue complète, "
        "quand l'Ascendant tourne douze fois par jour."),

    "كل ما في هذا الموقع متاح بواجهة واحدة: خرائط الميلاد بقراءتها، "
    "والنشرات، وتقويم الاختيارات، والمسائل، والتوافق، وأرباب الأزمنة. "
    "تُرجع JSON بالعربية مباشرة ()، وتُصدّر تقويمًا يدخل هاتفك.": (
        "Everything on this site is available through one interface: "
        "natal charts with their readings, the bulletins, the electional "
        "calendar, horary questions, synastry, and the time lords. It "
        "returns JSON in Arabic directly (), and exports a calendar that "
        "goes straight into your phone.",
        "Tout ce site est accessible par une seule interface : thèmes "
        "natals et leurs lectures, bulletins, calendrier électionnel, "
        "questions horaires, synastrie et maîtres du temps. Renvoie du "
        "JSON en arabe directement (), et exporte un calendrier qui "
        "entre dans votre téléphone."),
    "في تقويم آبل: ملفّ ← اشتراك جديد بتقويم. وفي تقويم غوغل: "
    "«تقاويم أخرى» ← «من رابط». الأحداث كلّها شفّافة — لا تُظهرك "
    "مشغولًا لمن يرى تقويمك.": (
        "In Apple Calendar: File → New Calendar Subscription. In Google "
        "Calendar: \"Other calendars\" → \"From URL\". All events are "
        "transparent — they will not show you as busy to anyone viewing "
        "your calendar.",
        "Dans Calendrier Apple : Fichier → Nouvel abonnement à un "
        "calendrier. Dans Google Agenda : « Autres agendas » → « À "
        "partir de l'URL ». Tous les événements sont transparents — ils "
        "ne vous affichent pas comme occupé."),
    "وحدّ الاستعمال مُهدّئ لا حارس: العدّاد في ذاكرة النسخة الواحدة، "
    "والدالّة بلا خادم تُشغَّل نسخًا متعدّدة، فكلٌّ تعدّ وحدها. يمنع "
    "الحلقة المنفلتة من عميل، ولا يمنع هجومًا مقصودًا. قلناها صراحةً "
    "فلا يبني عليها أحد ما لا تحتمل.": (
        "The rate limit is a damper, not a guard: the counter lives in "
        "one instance's memory, and a serverless function runs as many "
        "instances, each counting alone. It stops a runaway loop in a "
        "client; it does not stop a deliberate attack. We say so plainly "
        "so no one builds on it what it cannot bear.",
        "La limite d'usage est un amortisseur, non une garde : le "
        "compteur vit dans la mémoire d'une instance, et une fonction "
        "sans serveur s'exécute en plusieurs instances comptant chacune "
        "seule. Elle arrête la boucle emballée d'un client ; elle "
        "n'arrête pas une attaque délibérée. Nous le disons clairement, "
        "pour que nul n'y appuie ce qu'elle ne peut porter."),
    "Swiss Ephemeris. الحساب كلّه بمكتبة Swiss Ephemeris، وهي مزدوجة "
    "الرخصة: AGPL أو تجارية. فمن بنى على هذه الواجهة خدمةً مغلقة "
    "المصدر فعليه أن ينظر في رخصتها التجارية من astro.com. نحن نقول "
    "هذا لأنه يُنسى كثيرًا، ولا نُفتي فيه — راجع أهل الاختصاص.": (
        "Swiss Ephemeris. All computation uses the Swiss Ephemeris "
        "library, which is dual-licensed: AGPL or commercial. Anyone "
        "building a closed-source service on this API should look into "
        "its commercial licence at astro.com. We say this because it is "
        "often forgotten; we are not giving legal advice — consult a "
        "specialist.",
        "Swiss Ephemeris. Tout le calcul passe par la bibliothèque Swiss "
        "Ephemeris, à double licence : AGPL ou commerciale. Qui bâtit "
        "sur cette API un service à source fermée doit examiner sa "
        "licence commerciale sur astro.com. Nous le signalons car on "
        "l'oublie souvent ; ce n'est pas un avis juridique — consultez "
        "un spécialiste."),

    "البرج يقول كيف، والبيت يقول أين. المريخ في العقرب يقول إن "
    "إرادتك صامتة نافذة؛ ووقوعه في البيت العاشر يقول إن مجراها في "
    "العمل والمرتبة.": (
        "The sign says how, the house says where. Mars in Scorpio says "
        "your will is silent and penetrating; its fall in the tenth "
        "house says its course runs through work and standing.",
        "Le signe dit comment, la maison dit où. Mars en Scorpion dit "
        "que votre volonté est silencieuse et pénétrante ; sa chute en "
        "dixième maison dit qu'elle passe par le travail et le rang."),

    # ── وصدرُ صفحة الواجهة يشقّه `<code>` ──────────────────────
    # وهو ابنٌ لا يُبتلَع نصُّه (وإلّا مُحي المثال على من ينسخه)،
    # فالفقرةُ حاوية لا جملة. **فيُترجَم شقّاها، لا مجموعُهما.**
    "كل ما في هذا الموقع متاح بواجهة واحدة: خرائط الميلاد بقراءتها، "
    "والنشرات، وتقويم الاختيارات، والمسائل،": (
        "Everything on this site is available through one interface: natal "
        "charts with their readings, the bulletins, the electional "
        "calendar, horary questions,",
        "Tout ce site est accessible par une seule interface : thèmes "
        "natals et leurs lectures, bulletins, calendrier électionnel, "
        "questions horaires,"),
    "، وأرباب الأزمنة. تُرجع JSON بالعربية مباشرة (": (
        ", and the time lords. It returns JSON in Arabic directly (",
        ", et maîtres du temps. Renvoie du JSON en arabe directement ("),
    ")، وتُصدّر تقويمًا يدخل هاتفك.": (
        "), and exports a calendar that goes straight into your phone.",
        "), et exporte un calendrier qui entre dans votre téléphone."),

    "بمكتبة Swiss Ephemeris، لا من جداول مستوردة.": (
        "with the Swiss Ephemeris library, not from imported tables.",
        "avec la bibliothèque Swiss Ephemeris, non d'après des tables "
        "importées."),
    "تعذّر الاتصال بالخادم: offline": (
        "Could not reach the server: offline",
        "Connexion au serveur impossible : hors ligne"),

    # ــ شظايا مؤكَّدة داخل الجُمَل ــ
    "الأفق": ("the horizon", "l'horizon"),
    "الاقتران": ("conjunction", "la conjonction"),
    "التمام": ("perfection", "la perfection"),
    "التوقيت الصيفي": ("Daylight saving time", "L'heure d'été"),
    "الفصول الشمسية": ("The solar terms", "Les termes solaires"),
    "المطالع": ("right ascensions", "les ascensions droites"),
    "خلو المسار": ("void of course", "vide de course"),
    "محسوبة من طول": ("computed from the longitude of",
                     "calculés d'après la longitude de"),
    "بالبيوت الكاملة": ("with whole signs", "en signes entiers"),
    "بالقبّاني": ("with Alcabitius", "en Alcabitius"),
    "والقمر": ("and the Moon", "et la Lune"),
    "والزهرة": ("and Venus", "et Vénus"),
    "والطالع": ("and the Ascendant", "et l'Ascendant"),
    "والزاوية": ("and the aspect", "et l'aspect"),
    "والأَلْمُطَن": ("and the almuten", "et l'almuten"),
    "والنجوم الثابتة": ("and the fixed stars", "et les étoiles fixes"),
    "والتسيير": ("and direction", "et la direction"),
    "والتوافق": ("and synastry", "et la synastrie"),
    "والعودة الشمسية": ("and the solar return", "et la révolution solaire"),


    # ــ أسماء البيوت الاثني عشر ــ
    "الثالث": ("Third", "Troisième"),
    "الرابع": ("Fourth", "Quatrième"),
    "الخامس": ("Fifth", "Cinquième"),
    "السادس": ("Sixth", "Sixième"),
    "السابع": ("Seventh", "Septième"),
    "الثامن": ("Eighth", "Huitième"),
    "التاسع": ("Ninth", "Neuvième"),
    "العاشر": ("Tenth", "Dixième"),
    "الحادي عشر": ("Eleventh", "Onzième"),
    "الثاني عشر": ("Twelfth", "Douzième"),

    # ــ مفرداتُ العجلة والجداول ــ
    "الجرم": ("Body", "Astre"),
    "الكوكب": ("Planet", "Planète"),
    "الموضع": ("Position", "Position"),
    "المكان": ("Place", "Lieu"),
    "الوقت": ("Time", "Heure"),
    "القوّة": ("Strength", "Force"),
    "الكرامة": ("Dignity", "Dignité"),
    "الفارق": ("Difference", "Écart"),
    "مدّته": ("its span", "sa durée"),
    "نافذته": ("its window", "sa fenêtre"),
    "تشتدّ": ("tightening", "se resserre"),
    "تنفكّ": ("loosening", "se relâche"),
    "يكتمل": ("perfects", "se perfectionne"),
    "محايدة": ("neutral", "neutre"),
    "العابر": ("Transiting", "En transit"),
    "الكوكب المارّ": ("The transiting planet", "La planète en transit"),
    "الكوكب الحاكم": ("The ruling planet", "La planète maîtresse"),
    "حاكم اليوم": ("Ruler of the day", "Maître du jour"),
    "كوكب اليوم": ("Planet of the day", "Planète du jour"),
    "سرعته اليومية": ("its daily motion", "son mouvement diurne"),
    "السرعة اليومية": ("Daily motion", "Mouvement diurne"),
    "الكواكب الراجعة": ("Retrograde planets", "Planètes rétrogrades"),
    "الكواكب المتراجعة": ("Retrograde planets", "Planètes rétrogrades"),
    "النقاط المحسوبة": ("Calculated points", "Points calculés"),
    "الأشكال الهندسية": ("Geometric patterns", "Figures géométriques"),
    "الزوايا بين الكواكب": ("Aspects between the planets",
                             "Aspects entre planètes"),
    "الزوايا بين الأجرام": ("Aspects between the bodies",
                             "Aspects entre astres"),
    "الخريطة الفلكية الدائرية": ("The circular chart wheel",
                                  "La roue du thème"),
    "العجلة المزدوجة — خريطتان متراكبتان":
        ("The bi-wheel — two charts overlaid",
         "La double roue — deux thèmes superposés"),
    "خلو مسار": ("void of course", "vide de course"),
    "فراغ قمر": ("Moon void", "Lune vide"),
    "**وفيها قمرُك أنت.**": ("**And your own Moon is here.**",
                              "**Et votre Lune s'y trouve.**"),
    "لا جِرم لك في هذا البرج.": ("You have no body in this sign.",
                                  "Aucun astre dans ce signe."),
    "لا زاوية كبرى له مع سواه.": ("It forms no major aspect with anything.",
                                   "Aucun aspect majeur avec les autres."),
    "زاوية تامّة تقريبًا — وهذا أشدّ ما تكون.":
        ("Very nearly exact — and this is as strong as an aspect gets.",
         "Presque exact — c'est là son maximum de force."),
    "مُقبِلة: تشتدّ ولمّا تتمّ بعد، فأثرها في ما هو آتٍ.":
        ("Applying: tightening and not yet perfected, so its effect lies "
         "ahead.",
         "Appliquant : se resserre sans être exact, son effet est à venir."),
    "مُدبِرة: تمّت وانفكّت، فأثرها ماضٍ ينقضي.":
        ("Separating: perfected and loosening, so its effect is passing.",
         "Séparant : exact puis se relâche, son effet s'achève."),
    "راجع — يبدو سائرًا إلى الوراء، ودلالته المراجعة لا التوقّف.":
        ("Retrograde — it appears to move backwards; it signifies review, "
         "not a halt.",
         "Rétrograde — il semble reculer ; il signifie révision, non arrêt."),
    "وتفصيلُه في جدول السهام أسفلَ الصفحة.":
        ("Its detail is in the table of lots below.",
         "Son détail est dans le tableau des parts ci-dessous."),
    "· صيغته:": ("· formula:", "· formule :"),

    # ــ مستوى اللغة والتصفّح ــ
    "مستوى اللغة": ("Language level", "Niveau de langue"),
    "الأجرام والكرامات": ("Bodies and dignities", "Astres et dignités"),
    "الكواكب وقوّتها": ("The planets and their strength",
                        "Les planètes et leur force"),
    "الأوتاد والبيوت": ("Angles and houses", "Angles et maisons"),
    "النقاط الرئيسية والبيوت": ("The main points and the houses",
                                 "Les points principaux et les maisons"),
    "افتح قائمة التصفّح": ("Open navigation", "Ouvrir la navigation"),
    "طيّ القسم أو فتحه": ("Collapse or expand the section",
                           "Replier ou déplier la section"),
    "انسخ رابط هذه النتيجة": ("Copy a link to this result",
                               "Copier le lien de ce résultat"),
    "✓ نُسخ": ("✓ Copied", "✓ Copié"),
    "نُسخ ✓": ("Copied ✓", "Copié ✓"),
    "العربية": ("Arabic", "Arabe"),
    "الفَلَك:": ("Al-Falak:", "Al-Falak :"),
    "ردّ غير مفهوم من الخادم": ("Unreadable response from the server",
                                 "Réponse illisible du serveur"),
    "الفَلَك: لا خيارات للمفتاح": ("Al-Falak: no options for this key",
                                    "Al-Falak : aucune option pour cette clé"),
    "أطول من المعتاد… ما زلت أعمل.": ("Longer than usual… still working.",
                                       "Plus long que d'habitude… en cours."),
    "تمّ الحساب. النتيجة معروضة أسفل النموذج.":
        ("Done. The result is shown below the form.",
         "Terminé. Le résultat s'affiche sous le formulaire."),

    # ــ أوصافُ أبواب التصفّح ــ
    "الطالع والكواكب والقراءة": ("Ascendant, planets and the reading",
                                  "Ascendant, planètes et lecture"),
    "منزلة القمر وأوقات اليوم": ("The Moon's mansion and the day's hours",
                                  "Manoir lunaire et heures du jour"),
    "لكل ساعة كوكب وطبع": ("Each hour has its planet and nature",
                            "Chaque heure a sa planète"),
    "متى أفعل، وهل أفعل": ("When to act, and whether to",
                            "Quand agir, et faut-il agir"),
    "جواب من لحظة سؤالك": ("An answer from the moment you asked",
                            "Une réponse tirée de l'instant de la question"),
    "خريطتان معًا وثلاثة موازين": ("Two charts together and three scores",
                                    "Deux thèmes et trois scores"),
    "جدول المواقع في أي لحظة": ("Positions for any moment",
                                 "Positions à tout instant"),
    "أفضل الأيام وأصعبها": ("The best days and the hardest",
                             "Les meilleurs jours et les plus durs"),
    "أفضل الأيام وأسوأها": ("The best days and the worst",
                             "Les meilleurs et les pires jours"),
    "أفضل يوم وساعة لأمرك": ("The best day and hour for your purpose",
                              "Le meilleur jour et heure pour votre projet"),
    "ما يغلب على شخصيتك": ("What predominates in your character",
                            "Ce qui domine votre caractère"),
    "ما يخصّك أنت": ("What concerns you personally",
                     "Ce qui vous concerne"),
    "جوّك الشخصي": ("Your personal weather", "Votre météo personnelle"),
    "البيوت والبروج والزوايا والمعجم":
        ("Houses, signs, aspects and the glossary",
         "Maisons, signes, aspects et glossaire"),
    "المعاني والمصطلحات وأدوات المبرمجين":
        ("Meanings, terms and developer tools",
         "Sens, termes et outils pour développeurs"),
    "الجيوتِش: منازل القمر وفترات العمر":
        ("Jyotish: nakshatras and life periods",
         "Jyotish : nakshatras et périodes de vie"),
    "البازي: ثمانية حروف وميزان العناصر":
        ("Bazi: eight characters and the balance of elements",
         "Bazi : huit caractères et l'équilibre des éléments"),
    "شوسلر وكيري — تاريخُ فكرة لا دواء":
        ("Schüssler and Carey — the history of an idea, not a remedy",
         "Schüssler et Carey — l'histoire d'une idée, non un remède"),
    "البدن على البروج — تاريخُ فكرة لا طبّ":
        ("The body across the signs — history, not medicine",
         "Le corps sur les signes — histoire, non médecine"),
    "أين تقع كواكبك على وجه الأرض": ("Where your planets fall on Earth",
                                      "Où vos planètes tombent sur Terre"),
    "مواليد الأعلام بما يصحّ بالتاريخ وحده":
        ("Figures' births, by what the date alone supports",
         "Naissances de personnalités, selon la date seule"),
    "من أين جاءت البروج والوجوه — تاريخٌ موثّق":
        ("Where the signs and decans came from — documented history",
         "D'où viennent signes et décans — histoire documentée"),
    "ابنِ على الفَلَك، وصدّر تقويمك":
        ("Build on Al-Falak, and export your calendar",
         "Bâtissez sur Al-Falak, exportez votre agenda"),

    # ــ صدورُ الصفحات المشتركة ــ
    "خريطة الميلاد صورة للسماء لحظة ولادتك: أين كان كل كوكب، وأيّ برج":
        ("A natal chart is a picture of the sky at the moment of your "
         "birth: where each planet stood, and which sign",
         "Le thème natal est une image du ciel à votre naissance : où se "
         "tenait chaque planète, et quel signe"),
    "كان صاعدًا في الأفق. منها تُقرأ الطباع والميول.":
        ("was rising on the horizon. From it are read character and "
         "inclination.",
         "se levait à l'horizon. On y lit caractère et penchants."),
    "الأوتاد الأربعة ليست أجرامًا، بل مواضع تحدّدها لحظةُ الميلاد ومكانُه.":
        ("The four angles are not bodies but positions fixed by the moment "
         "and place of birth.",
         "Les quatre angles ne sont pas des astres mais des positions "
         "fixées par l'heure et le lieu de naissance."),
    "وهي أدقّ ما في الخريطة حسّاسيةً للوقت: أربع دقائق تُزحزح الطالع درجة.":
        ("They are the most time-sensitive part of the chart: four minutes "
         "shift the Ascendant by a degree.",
         "C'est la part la plus sensible à l'heure : quatre minutes "
         "décalent l'Ascendant d'un degré."),
    "النشرة اليومية تصف حال السماء في يوم بعينه: أين القمر، وما":
        ("The daily bulletin describes the sky on a given day: where the "
         "Moon is, and what",
         "Le bulletin quotidien décrit le ciel d'un jour donné : où est la "
         "Lune, et ce que"),
    "النشرة الشهرية تجمع أحداث الشهر كلّه: انتقالات الكواكب، والكسوف،":
        ("The monthly bulletin gathers the whole month's events: planetary "
         "ingresses, eclipses,",
         "Le bulletin mensuel réunit les événements du mois : entrées de "
         "signe, éclipses,"),
    "وأفضل أيام الشهر لكل غرض.": ("and the month's best days for each purpose.",
                                   "et les meilleurs jours pour chaque objet."),
    "الأوقات المناسبة وما يُفضّل تأجيله.":
        ("The suitable hours, and what is better postponed.",
         "Les heures propices, et ce qu'il vaut mieux différer."),
    "قسّم القدماء النهار اثنتي عشرة ساعة والليل مثلها، ونسبوا كل ساعة":
        ("The ancients divided daylight into twelve hours and the night "
         "likewise, and assigned each hour",
         "Les anciens divisaient le jour en douze heures et la nuit de "
         "même, attribuant chaque heure"),
    "إلى كوكب. فلكل ساعة طبع، ولكل عمل ساعة تناسبه.":
        ("to a planet. Each hour has its nature, and each task its "
         "fitting hour.",
         "à une planète. Chaque heure a sa nature, chaque tâche son heure."),
    "جدول يبيّن موضع كل كوكب في السماء في أي لحظة تختارها.":
        ("A table showing where each planet stands in the sky at any "
         "moment you choose.",
         "Un tableau montrant la position de chaque planète à l'instant "
         "de votre choix."),

    # ══════════════════════════════════════════════════════════
    # صفحة الواجهة البرمجية — آخرُ الصفحات وأكثرُها نصًّا
    #
    # **وأمثلةُ المسارات لا تُترجَم إلّا في قيمة المدينة**:
    # `city=دمشق` تصير `city=Damascus`، لأن الأطلس يعرف الاسمين.
    # أمّا `?date=` و`&time=` فهي أسماءُ معاملاتٍ في الشيفرة،
    # ومن ترجمها كسر المثال على من ينسخه.
    # ══════════════════════════════════════════════════════════
    "الواجهة البرمجية والتقويم — الفَلَك":
        ("API and calendar — Al-Falak", "API et calendrier — Al-Falak"),
    "الفَلَك — الواجهة البرمجية": ("Al-Falak — API", "Al-Falak — API"),
    "الفَلَك — أدوات فلكية عربية ·": ("Al-Falak — Arabic astrology tools ·",
                                       "Al-Falak — outils d'astrologie arabe ·"),
    "كل ما في هذا الموقع متاح بواجهة واحدة: خرائط الميلاد بقراءتها، والنشرات، وتقويم الاختيارات، والمسائل، والتوافق، وأرباب الأزمنة. تُرجع JSON بالعربية مباشرة (":
        ("Everything on this site is available through one API: natal "
         "charts with their readings, the bulletins, the electional "
         "calendar, horary, synastry and the time lords. It returns JSON "
         "in Arabic directly (",
         "Tout ce site est accessible par une seule API : thèmes natals et "
         "leurs lectures, bulletins, calendrier électif, horaire, "
         "synastrie et maîtres du temps. Renvoie du JSON en arabe ("),
    ")، وتُصدّر تقويمًا يدخل هاتفك.":
        ("), and exports a calendar that goes straight into your phone.",
         "), et exporte un calendrier pour votre téléphone."),
    "البداية في ثلاثة أسطر": ("Getting started in three lines",
                               "Démarrer en trois lignes"),
    "لا تحتاج مفتاحًا للتجريب. جرّب هذا الآن:":
        ("You need no key to try it. Run this now:",
         "Aucune clé n'est nécessaire pour essayer. Lancez ceci :"),
    "وكل جواب في المغلَّف نفسه:": ("Every response comes in the same envelope:",
                                    "Chaque réponse a la même enveloppe :"),
    "وكل خطأ:": ("And every error:", "Et chaque erreur :"),
    "المسارات": ("Endpoints", "Points d'accès"),
    "المسارات القديمة": ("Legacy endpoints", "Points d'accès hérités"),
    "بلا مغلَّف ولا إصدار — تخدم صفحات الموقع نفسه، وقد تتغيّر. ابنِ على":
        ("No envelope and no version — they serve the site's own pages and "
         "may change. Build on",
         "Sans enveloppe ni version — ils servent les pages du site et "
         "peuvent changer. Construisez sur"),
    "وحدها.": ("only.", "uniquement."),
    "المستويات والمفاتيح": ("Tiers and keys", "Niveaux et clés"),
    "كيف تعمل المفاتيح هنا — ولماذا:": ("How keys work here — and why:",
                                          "Comment fonctionnent les clés — et pourquoi :"),
    "المشروع كلّه دالّة بلا خادم ولا قاعدة بيانات. فالمفتاح":
        ("The whole project is one serverless function with no database. "
         "So the key is",
         "Tout le projet est une fonction sans serveur, sans base de "
         "données. La clé est donc"),
    "موقَّع لا مخزَّن": ("signed, not stored", "signée, non stockée"),
    ": يحمل في نفسه مستواه وتاريخ انتهائه وتوقيعًا يُثبت أننا أصدرناه، فيُتحقَّق منه بالحساب لا بالبحث.":
        (": it carries its own tier, expiry and a signature proving we "
         "issued it, so it is verified by computation rather than lookup.",
         ": elle porte son niveau, son expiration et une signature "
         "prouvant que nous l'avons émise ; elle se vérifie par calcul."),
    "وثمن ذلك": ("The cost of this is", "Le prix en est"),
    "أن ما لا يُخزَّن لا يُلغى فرديًّا. فأقصى عمر للمفتاح سنة، ولا نحفظ نسخة منه عندنا — احفظه أنت عند إصداره.":
        ("that what is not stored cannot be revoked individually. So a key "
         "lasts at most a year, and we keep no copy — save it yourself "
         "when you issue it.",
         "que ce qui n'est pas stocké ne peut être révoqué "
         "individuellement. Une clé dure au plus un an, et nous n'en "
         "gardons aucune copie — conservez-la vous-même."),
    "وحدّ الاستعمال مُهدّئ لا حارس:": ("The rate limit is a damper, not a guard:",
                                        "La limite d'usage est un frein, non un garde :"),
    "العدّاد في ذاكرة النسخة الواحدة، والدالّة بلا خادم تُشغَّل نسخًا متعدّدة، فكلٌّ تعدّ وحدها. يمنع الحلقة المنفلتة من عميل، ولا يمنع هجومًا مقصودًا. قلناها صراحةً فلا يبني عليها أحد ما لا تحتمل.":
        ("The counter lives in one instance's memory, and a serverless "
         "function runs as many instances, each counting alone. It stops a "
         "runaway loop in a client; it does not stop a deliberate attack. "
         "We say so plainly, so that no one builds on it more than it "
         "will bear.",
         "Le compteur vit dans la mémoire d'une instance, et la fonction "
         "s'exécute en plusieurs instances qui comptent chacune de leur "
         "côté. Cela arrête une boucle folle, non une attaque délibérée."),
    "استخرج مفتاحًا مفتوحًا": ("Issue an open key", "Émettre une clé ouverte"),
    "استخراج مفتاح وصول. لا يُخزَّن عندنا، فاحفظه.":
        ("Issue an access key. We do not store it — save it.",
         "Émettre une clé d'accès. Nous ne la stockons pas — conservez-la."),
    "عمر المفتاح، أقصاه ٣٦٦": ("Key lifetime, at most 366 days",
                                "Durée de la clé, 366 jours au plus"),
    "وسم تذكاري لك": ("A label for your own reference",
                       "Une étiquette pour votre usage"),
    "تعذّر الإصدار:": ("Could not issue:", "Émission impossible :"),
    "… أُصدر": ("… issuing", "… émission"),
    "خطأ:": ("Error:", "Erreur :"),
    "الاسمان": ("Both names", "Les deux noms"),
    "مطلوب": ("required", "requis"),
    "مطلوب أو lat+lon+tz": ("required, or lat+lon+tz",
                             "requis, ou lat+lon+tz"),
    "مطلوب أو house": ("required, or house", "requis, ou house"),
    "المنطقة": ("Zone", "Zone"),
    "المنطقة الزمنية": ("Time zone", "Fuseau horaire"),
    "الساعة HH:MM": ("Time HH:MM", "Heure HH:MM"),
    "تاريخ الميلاد YYYY-MM-DD": ("Birth date YYYY-MM-DD",
                                  "Date de naissance AAAA-MM-JJ"),
    "بيانات المولد": ("Birth data", "Données de naissance"),
    "مولد الأوّل": ("First person's birth", "Naissance du premier"),
    "مولد الثاني": ("Second person's birth", "Naissance du second"),
    "ساعته": ("its hour", "son heure"),
    "غرض بعينه": ("a specific purpose", "un objet précis"),
    "البيت ١–١٢": ("House 1–12", "Maison 1–12"),
    "عدد الأيام": ("Number of days", "Nombre de jours"),
    "عدد الأيام (بحسب مستواك)": ("Number of days (per your tier)",
                                  "Nombre de jours (selon votre niveau)"),
    "عدد النتائج": ("Number of results", "Nombre de résultats"),
    "أدنى درجة تُصدَّر": ("Minimum score to export",
                          "Score minimal à exporter"),
    "ما تبحث عنه": ("What you are searching for",
                     "Ce que vous cherchez"),
    "سؤالك من القائمة": ("Your question from the list",
                          "Votre question dans la liste"),
    "مدينة إقامتك الآن": ("The city you live in now",
                           "La ville où vous vivez"),
    "تاريخ مولدك — للترجيح الشخصي": ("Your birth date — for personal weighting",
                                       "Votre date de naissance — pondération"),
    "1 لقائمة الأغراض": ("1 for the list of purposes",
                          "1 pour la liste des objets"),
    "1 لقائمة الأسئلة": ("1 for the list of questions",
                          "1 pour la liste des questions"),
    "0 لإلغاء أيّهما": ("0 to disable either", "0 pour désactiver l'un ou l'autre"),
    "مع kind=elections": ("with kind=elections", "avec kind=elections"),
    "مع kind=hours، مفصولة بفواصل": ("with kind=hours, comma-separated",
                                       "avec kind=hours, séparés par virgules"),
    "مفتاحًا أساسيًّا": ("a basic key", "une clé basic"),
    "free أو basic": ("free or basic", "free ou basic"),
    "plain أو expert": ("plain or expert", "plain ou expert"),
    "today أو tomorrow": ("today or tomorrow", "today ou tomorrow"),
    "حال الخادم: عدد المدن وأنظمة البيوت وتوفّر ملفّات خيرون.":
        ("Server status: number of cities, house systems, and whether the "
         "Chiron ephemeris files are present.",
         "État du serveur : nombre de villes, systèmes de maisons, et "
         "présence des fichiers d'éphémérides de Chiron."),
    "مواقع الأجرام الأربعة عشر في لحظة تختارها.":
        ("Positions of the fourteen bodies at a moment you choose.",
         "Positions des quatorze astres à un instant choisi."),
    "منازل القمر وخلو المسار": ("Lunar mansions and void of course",
                                 "Manoirs lunaires et vide de course"),
    "أحداث السماء: الانتقالات والرجوع والكسوف":
        ("Sky events: ingresses, retrogrades and eclipses",
         "Événements du ciel : entrées, rétrogradations et éclipses"),
    "النشرة الشهرية المصوغة بثلاثة ألسنة: يومي وأدبي وتراثي.":
        ("The monthly bulletin in three voices: daily, literary and "
         "traditional.",
         "Le bulletin mensuel en trois tons : quotidien, littéraire et "
         "traditionnel."),
    "تقويم الاختيارات: درجة كل يوم لكل غرض، بأسبابها.":
        ("The electional calendar: each day's score for each purpose, with "
         "its reasons.",
         "Le calendrier électif : le score de chaque jour pour chaque "
         "objet, avec ses raisons."),
    "الفردارات والتسيير السنوي والشهري والعودة الشمسية.":
        ("Firdaria, annual and monthly profection, and the solar return.",
         "Firdaria, profections annuelle et mensuelle, révolution solaire."),
    "معجم المصطلحات وتسمياتها المبسّطة.":
        ("The glossary of terms and their plain-language names.",
         "Le glossaire des termes et leurs noms simplifiés."),
    "تصدير iCalendar. يُرجع ملفًّا لا JSON.":
        ("iCalendar export. Returns a file, not JSON.",
         "Export iCalendar. Renvoie un fichier, non du JSON."),
    "التقويم — أن تدخل السماء جدولك":
        ("The calendar — bringing the sky into your schedule",
         "Le calendrier — faire entrer le ciel dans votre agenda"),
    "اشترك بالرابط مرّة في تقويم هاتفك أو حاسوبك، فتظهر منازل القمر وأوقات خلو المسار وأفضل أيامك مع مواعيدك، وتتجدّد وحدها.":
        ("Subscribe to the link once in your phone's or computer's "
         "calendar, and the lunar mansions, void-of-course windows and "
         "your best days appear alongside your appointments, refreshing "
         "themselves.",
         "Abonnez-vous une fois au lien dans votre agenda : manoirs "
         "lunaires, périodes de vide de course et meilleurs jours "
         "apparaissent avec vos rendez-vous, et se mettent à jour seuls."),
    "ماذا تريد في تقويمك؟": ("What do you want in your calendar?",
                              "Que voulez-vous dans votre agenda ?"),
    "أين أنت": ("Where you are", "Où vous êtes"),
    "شفّافة": ("Transparent", "Transparent"),
    "— لا تُظهرك مشغولًا لمن يرى تقويمك.":
        ("— it will not show you as busy to anyone viewing your calendar.",
         "— vous n'apparaîtrez pas occupé à qui consulte votre agenda."),
    "في تقويم آبل: ملفّ ← اشتراك جديد بتقويم. وفي تقويم غوغل: «تقاويم أخرى» ← «من رابط». الأحداث كلّها":
        ("In Apple Calendar: File → New Calendar Subscription. In Google "
         "Calendar: \"Other calendars\" → \"From URL\". All events are",
         "Dans Calendrier Apple : Fichier → Nouvel abonnement. Dans Google "
         "Agenda : « Autres agendas » → « À partir de l'URL »."),
    "الرخصة والشروط": ("Licence and terms", "Licence et conditions"),
    "الحساب كلّه بمكتبة Swiss Ephemeris، وهي مزدوجة الرخصة: AGPL أو تجارية. فمن بنى على هذه الواجهة خدمةً مغلقة المصدر فعليه أن ينظر في رخصتها التجارية من astro.com. نحن نقول هذا لأنه يُنسى كثيرًا، ولا نُفتي فيه — راجع أهل الاختصاص.":
        ("All computation runs on the Swiss Ephemeris, which is dual "
         "licensed: AGPL or commercial. If you build a closed-source "
         "service on this API, you should look into its commercial licence "
         "from astro.com. We mention this because it is often forgotten; "
         "we are not giving legal advice — consult a professional.",
         "Tout le calcul repose sur la Swiss Ephemeris, à double licence : "
         "AGPL ou commerciale. Si vous bâtissez un service à source fermée "
         "sur cette API, examinez sa licence commerciale sur astro.com. "
         "Ceci n'est pas un conseil juridique."),
    "أمّا نصوص التفسير والقراءة في هذا الموقع فمكتوبة لنا، ولك أن تعرضها مع الإشارة إلى المصدر.":
        ("The interpretive and reading texts on this site are our own; you "
         "may display them with attribution.",
         "Les textes d'interprétation de ce site sont les nôtres ; vous "
         "pouvez les afficher en citant la source."),
    "هذا الموقع أداة حسابية وقراءة رمزية، لا أداة تشخيص ولا نصيحة طبية ولا مالية ولا قانونية.":
        ("This site is a calculating tool and a symbolic reading — not a "
         "diagnostic instrument, and not medical, financial or legal advice.",
         "Ce site est un outil de calcul et une lecture symbolique — ni "
         "diagnostic, ni conseil médical, financier ou juridique."),

    # ══════════════════════════════════════════════════════════
    # صفحة «تعلّم» — الدروسُ الخمسة ودليلُ الصفحات
    # ══════════════════════════════════════════════════════════
    "تعلّم — الفَلَك": ("Learn — Al-Falak", "Apprendre — Al-Falak"),
    "الفَلَك — تعلّم": ("Al-Falak — Learn", "Al-Falak — Apprendre"),
    "كل مصطلح تراه في الجداول مشروح هنا. ابحث عنه أو تصفّح الأبواب.":
        ("Every term you see in the tables is explained here. Search for "
         "it, or browse the sections.",
         "Chaque terme des tableaux est expliqué ici. Cherchez-le ou "
         "parcourez les sections."),
    "دليل الصفحات — ماذا في كلّ باب؟":
        ("A guide to the pages — what is in each?",
         "Guide des pages — que contient chacune ?"),
    "قبل المصطلحات: هذه خريطةُ الموقع نفسه. كل صفحة وما تُعطيك، في سطر — فتعرف أين تذهب قبل أن تتعلّم.":
        ("Before the terms: this is a map of the site itself. Each page "
         "and what it gives you, in one line — so you know where to go "
         "before you start learning.",
         "Avant les termes : voici la carte du site lui-même. Chaque page "
         "et ce qu'elle apporte, en une ligne."),
    "كيف تُقرأ خريطة": ("How to read a chart", "Comment lire un thème"),
    "١ — ابدأ بالثلاثة": ("1 — Begin with the three",
                          "1 — Commencez par les trois"),
    "٢ — ثم البيوت": ("2 — Then the houses", "2 — Puis les maisons"),
    "٣ — ثم الكرامات": ("3 — Then the dignities",
                        "3 — Puis les dignités"),
    "٤ — ثم الزوايا": ("4 — Then the aspects", "4 — Puis les aspects"),
    "٥ — وأخيرًا ما يُميّز التراث العربي":
        ("5 — And finally, what sets the Arabic tradition apart",
         "5 — Enfin, ce qui distingue la tradition arabe"),
    "الشمس والقمر والطالع. الشمس جوهر إرادتك، والقمر ما يطمئنّ إليه قلبك، والطالع الباب الذي تدخل منه على الناس. من عرف هذه الثلاثة عرف نصف الخريطة.":
        ("Sun, Moon and Ascendant. The Sun is the core of your will, the "
         "Moon is what your heart settles into, and the Ascendant is the "
         "door through which you meet people. Know these three and you "
         "know half the chart.",
         "Soleil, Lune et Ascendant. Le Soleil est le cœur de votre "
         "volonté, la Lune ce qui apaise votre cœur, l'Ascendant la porte "
         "par laquelle vous abordez les autres. Qui connaît ces trois "
         "connaît la moitié du thème."),
    "ثم انظر في سيّد الطالع — حاكم البرج الطالع — وأين وقع. هو دليلك في الخريطة، وحيث وقع فثمّ مجرى حياتك.":
        ("Then look at the Ascendant's ruler — the lord of the rising sign "
         "— and where it fell. It is your guide in the chart, and where it "
         "lands is where your life runs.",
         "Regardez ensuite le maître de l'Ascendant et où il se trouve. "
         "C'est votre guide dans le thème, et là où il tombe coule votre "
         "vie."),
    "البرج يقول": ("The sign says", "Le signe dit"),
    "، والبيت يقول": (", and the house says", ", et la maison dit"),
    ". المريخ في العقرب يقول إن إرادتك صامتة نافذة؛ ووقوعه في البيت العاشر يقول إن مجراها في العمل والمرتبة.":
        (". Mars in Scorpio says your will is silent and penetrating; its "
         "falling in the tenth house says its course runs through work and "
         "standing.",
         ". Mars en Scorpion dit que votre volonté est silencieuse et "
         "pénétrante ; sa chute en dixième maison dit qu'elle passe par le "
         "travail et le rang."),
    "ولا تنسَ أن نظام تقسيم البيوت مذهب لا حقيقة. جرّب الخريطة بالبيوت الكاملة ثم بالقبّاني ثم ببلاسيدوس، وانظر أيّها يصف حياتك أصدق وصف.":
        ("And do not forget that a house system is a school of thought, "
         "not a fact. Try your chart in whole signs, then Alcabitius, then "
         "Placidus, and see which describes your life most truly.",
         "N'oubliez pas qu'un système de maisons est une école, non un "
         "fait. Essayez signes entiers, puis Alcabitius, puis Placidus, et "
         "voyez lequel décrit le plus fidèlement votre vie."),
    "ليس كل كوكب في الخريطة بقوّة واحدة. الكوكب في بيته يتصرّف بحرّية، وفي وباله يتصرّف بضيق. فقبل أن تُحمّل كوكبًا معنى، انظر أله من القوّة ما يُنفّذه به.":
        ("Not every planet in a chart has the same strength. A planet in "
         "its own domicile acts freely; in its detriment it acts "
         "constrained. Before you load a planet with meaning, ask whether "
         "it has the power to carry it out.",
         "Toutes les planètes n'ont pas la même force. En domicile, une "
         "planète agit librement ; en exil, elle agit à l'étroit. Avant de "
         "charger une planète de sens, demandez si elle a le pouvoir de "
         "l'accomplir."),
    "والأَلْمُطَن — أقوى الكواكب مجموعًا — هو الذي يحكم بنية الخريطة كلها.":
        ("And the almuten — the planet strongest in total — is the one "
         "that governs the whole structure of the chart.",
         "Et l'almuten — la planète la plus forte au total — gouverne toute "
         "la structure du thème."),
    "الكوكب المنعزل لا يفعل شيئًا. الزوايا هي ما يربط الأجزاء ببعضها، والزاوية الدقيقة أشدّ أثرًا من عشر زوايا واسعة.":
        ("An isolated planet does nothing. Aspects are what bind the parts "
         "together, and one tight aspect weighs more than ten wide ones.",
         "Une planète isolée ne fait rien. Les aspects relient les parties, "
         "et un aspect serré pèse plus que dix aspects larges."),
    "وانظر أهي مُقبِلة أم مُدبِرة: المُقبِلة لمّا تتمّ بعد فأثرها آتٍ، والمُدبِرة تمّت وانفكّت فأثرها ماضٍ.":
        ("And see whether it is applying or separating: an applying aspect "
         "has not yet perfected, so its effect lies ahead; a separating one "
         "has perfected and loosened, so its effect is past.",
         "Voyez s'il est appliquant ou séparant : l'appliquant n'est pas "
         "encore exact, son effet est à venir ; le séparant s'est achevé, "
         "son effet est passé."),
    "المنازل القمرية الثماني والعشرون، والسهام، والنجوم الثابتة بأسمائها. هذه أبواب أهملتها المدرسة الغربية المعاصرة، وهي أصل علم الاختيارات عند العرب: متى تبدأ وما تتجنّب.":
        ("The twenty-eight lunar mansions, the Arabic lots, and the fixed "
         "stars by their names. These are chapters the modern Western "
         "school let go of, and they are the root of the Arabic art of "
         "elections: when to begin and what to avoid.",
         "Les vingt-huit manoirs lunaires, les parts arabes et les étoiles "
         "fixes par leurs noms. Des chapitres délaissés par l'école "
         "occidentale moderne, et qui fondent l'art arabe des élections."),
    "معجم المصطلحات": ("Glossary of terms", "Glossaire des termes"),
    "ابحث في المصطلحات": ("Search the terms", "Rechercher un terme"),
    "ابحث عن مصطلح: الطالع، الوجاج، الأَلْمُطَن…":
        ("Search a term: Ascendant, orb, almuten…",
         "Cherchez un terme : Ascendant, orbe, almuten…"),
    "… أُحمّل المعجم": ("… loading the glossary", "… chargement du glossaire"),
    "دليل البيوت الاثني عشر": ("Guide to the twelve houses",
                                "Guide des douze maisons"),
    "دليل البروج الاثني عشر": ("Guide to the twelve signs",
                                "Guide des douze signes"),
    "دليل الزوايا بين الكواكب": ("Guide to the aspects between planets",
                                  "Guide des aspects entre planètes"),
    "اضغط أيّ بيت": ("Click any house", "Cliquez sur une maison"),
    "اضغط أيّ برج": ("Click any sign", "Cliquez sur un signe"),
    "لكل زوج من الكواكب «موضوع» يجمعه في كل حال، ثم لكل زاوية بينهما نصّها. وسترى أن الشمس مع عطارد والزهرة لا يقع بينها إلا الاقتران — فذلك ما تسمح به السماء، لا ما اخترناه نحن.":
        ("Every pair of planets has a theme that holds in all cases, and "
         "then each aspect between them has its own text. You will notice "
         "that the Sun with Mercury or Venus can only ever conjoin — that "
         "is what the sky permits, not something we chose.",
         "Chaque paire de planètes a un thème constant, puis chaque aspect "
         "a son propre texte. Vous verrez que le Soleil avec Mercure ou "
         "Vénus ne peut que se conjoindre — c'est ce que le ciel permet, "
         "non notre choix."),
    "تنبيه": ("Note", "Avertissement"),
    "هذا الموقع أداة حسابية وقراءة رمزية، لا أداة تشخيص ولا نصيحة طبية ولا مالية ولا قانونية. لا تُبنى عليه قرارات مصيرية، ولا يُستغنى به عن أهل الاختصاص.":
        ("This site is a calculating tool and a symbolic reading — not a "
         "diagnostic instrument, and not medical, financial or legal "
         "advice. Do not build life-changing decisions on it, and do not "
         "let it stand in for a qualified professional.",
         "Ce site est un outil de calcul et une lecture symbolique — ni un "
         "instrument de diagnostic, ni un conseil médical, financier ou "
         "juridique. N'y fondez pas de décisions décisives, et ne "
         "remplacez pas un professionnel qualifié."),
    "المجموع": ("Total", "Total"),
    "كيف": ("how", "comment"),
    "أين": ("where", "où"),

    # ــ بطاقاتُ دليل الصفحات ــ
    "بوّابة الموقع: تسألك ماذا تريد بلغتك، لا بلغة الصناعة.":
        ("The gateway: it asks what you want in your own words, not in the "
         "jargon of the craft.",
         "La porte d'entrée : elle demande ce que vous voulez dans vos "
         "mots, non dans le jargon."),
    "صورة السماء لحظة مولدك: الطالع والكواكب والبيوت والكرامات والسهام، مع قراءة مكتوبة لكل موضع، و**لسانٌ لما يمرّ عليك الآن** من عبور وربّ سنة.":
        ("The sky at the moment of your birth: Ascendant, planets, houses, "
         "dignities and lots, with a written reading for every placement, "
         "and **a tab for what is passing over you now** — transits and "
         "the lord of your year.",
         "Le ciel à l'instant de votre naissance : Ascendant, planètes, "
         "maisons, dignités et parts, avec une lecture écrite pour chaque "
         "position, et **un onglet pour ce qui vous traverse** en ce moment."),
    "حال السماء اليوم: منزلة القمر، وخلوّ المسار، وأوقات الشمس، وما يصلح لهذا اليوم وما لا يصلح.":
        ("The state of the sky today: the Moon's mansion, void of course, "
         "the solar hours, and what today suits and what it does not.",
         "L'état du ciel aujourd'hui : manoir lunaire, vide de course, "
         "heures solaires, et ce qui convient ou non."),
    "أحداث الشهر كلّه في تقويم واحد، وما يقع منها على درجات خريطتك أنت.":
        ("The whole month's events in one calendar, and which of them fall "
         "on the degrees of your own chart.",
         "Tous les événements du mois en un calendrier, et lesquels tombent "
         "sur les degrés de votre thème."),
    "اثنتا عشرة ساعة نهارًا ومثلها ليلًا، لكلٍّ كوكبٌ وطبع — وتطول صيفًا وتقصر شتاءً.":
        ("Twelve hours by day and twelve by night, each with its planet "
         "and nature — lengthening in summer, shortening in winter.",
         "Douze heures le jour et douze la nuit, chacune avec sa planète — "
         "plus longues en été, plus courtes en hiver."),
    "تختار غرضًا فيبحث لك عن أفضل يوم وساعة له في الأشهر القادمة.":
        ("Choose a purpose and it searches the coming months for the best "
         "day and hour for it.",
         "Choisissez un objet : il cherche dans les mois à venir le "
         "meilleur jour et la meilleure heure."),
    "تُنجَّم على لحظة سؤالك لا على مولدك. أربع وعشرون مسألة، بحكمٍ مُعلَّل.":
        ("Cast on the moment of your question, not on your birth. "
         "Twenty-four question types, each with a reasoned judgement.",
         "Dressé sur l'instant de votre question, non sur votre naissance. "
         "Vingt-quatre types de questions, avec un jugement motivé."),
    "الجيوتِش: البروج من النجوم لا من الفصول، والنكشترا والدشا والفرغا واليوغات.":
        ("Jyotish: signs measured from the stars rather than the seasons, "
         "with nakshatras, dashas, vargas and yogas.",
         "Jyotish : signes mesurés depuis les étoiles et non les saisons, "
         "avec nakshatras, dashas, vargas et yogas."),
    "البازي: ثمانية حروف، وسيّد النفس، وميزان العناصر الخمسة، ودورات الحظّ.":
        ("Bazi: eight characters, the Day Master, the balance of the five "
         "elements, and the luck cycles.",
         "Bazi : huit caractères, le Maître du Jour, l'équilibre des cinq "
         "éléments et les cycles de chance."),
    "خريطتان معًا: الوصلات والتراكب والتقبّل، وثلاثة موازين من ثلاث مدارس.":
        ("Two charts together: contacts, house overlays and reception, "
         "with three scores drawn from three traditions.",
         "Deux thèmes ensemble : contacts, superpositions et réception, "
         "avec trois scores issus de trois traditions."),
    "أيّ فترة تعيش الآن: الفردارية والتسيير والعودة الشمسية.":
        ("Which period you are living now: firdaria, direction and the "
         "solar return.",
         "La période que vous vivez : firdaria, direction et révolution "
         "solaire."),
    "أملاح شوسلر الاثنا عشر وربطُها بالبروج عند كيري. **تاريخُ فكرةٍ لا تشخيصٌ ولا دواء.**":
        ("Schüssler's twelve salts and Carey's linking of them to the "
         "signs. **The history of an idea — not diagnosis, not treatment.**",
         "Les douze sels de Schüssler et leur lien aux signes chez Carey. "
         "**L'histoire d'une idée — ni diagnostic ni traitement.**"),
    "لكل كوكبٍ أربعة خطوط على وجه الأرض: يكون فيها طالعًا أو غاربًا أو في وسط السماء أو وتد الأرض. **ومَن سكن قريبًا من خطٍّ منها اشتدّ عليه ذلك الكوكب هناك** — والخطّ لا يقول خيرٌ أو شرّ، بل: هذا الكوكب أعلى صوتًا هنا.":
        ("Every planet has four lines on Earth: where it rises, sets, "
         "culminates or anti-culminates. **Live near one and that planet "
         "grows louder for you there** — the line does not say good or "
         "bad, only: this planet speaks louder here.",
         "Chaque planète a quatre lignes sur Terre : où elle se lève, se "
         "couche, culmine ou anticulmine. **Vivre près d'une ligne rend "
         "cette planète plus forte** — la ligne ne dit ni bien ni mal."),
    "مواليد أعلامٍ من العرب والعالم. **وما يُعرَض محدود عمدًا**: ساعةُ ميلادهم لا تُعرَف، فلا طالعَ لهم ولا بيوت — وأكثر المواقع تضع ١٢:٠٠ وترسم عجلةً كاملة، والطالع يدور اثنتي عشرة مرّةً في اليوم. فنعرض ما يصحّ بالتاريخ وحده.":
        ("Birth data of figures from the Arab world and beyond. **What is "
         "shown is deliberately limited**: their birth times are unknown, "
         "so no Ascendant and no houses — most sites set the clock to "
         "12:00 and draw a full wheel, yet the Ascendant turns twelve "
         "times a day. We show only what the date alone supports.",
         "Naissances de personnalités arabes et du monde. **Ce qui est "
         "montré est volontairement limité** : leurs heures de naissance "
         "sont inconnues, donc ni Ascendant ni maisons."),
    "**ساعاتُ يومك الأربع والعشرون جاءت من ديكانات مصر، وبروجُك من بابل.** تاريخٌ موثّق: من أين جاء ما نحسبه، وأرباب الوجوه بمذهبين لا يتّفقان إلّا في تسعةٍ من ستّةٍ وثلاثين. **وما لا يُعرَف يُقال إنه لا يُعرَف** — ولا «برج سومريّ» مُختلَق.":
        ("**Your day's twenty-four hours came from Egypt's decans, and "
         "your signs from Babylon.** Documented history: where what we "
         "compute came from, and the rulers of the decans in two schools "
         "that agree on only nine of thirty-six. **What is not known is "
         "said to be unknown** — and no invented \"Sumerian sign\".",
         "**Les vingt-quatre heures viennent des décans d'Égypte, et vos "
         "signes de Babylone.** Histoire documentée, et les maîtres des "
         "décans en deux écoles qui ne s'accordent que sur neuf sur "
         "trente-six. **Ce qu'on ignore est dit ignoré.**"),
    "البدن على البروج: الحملُ الرأس والحوتُ القدمان، والمِزاج بالأخلاط الأربعة **محسوبًا بمواضع بطلَميوس الخمسة**، ويُرى من أين جاءت كل نقطة. **تاريخُ فكرةٍ لا طبّ — ولا تشخيصٌ ولا دواء، ومن وجد شيئًا فالطبيب.**":
        ("The body across the signs: Aries the head, Pisces the feet; and "
         "temperament by the four humours, **computed from Ptolemy's five "
         "placements**, with every point traced to its source. **The "
         "history of an idea, not medicine — no diagnosis, no treatment; "
         "if something troubles you, see a doctor.**",
         "Le corps réparti sur les signes ; et le tempérament par les "
         "quatre humeurs, **calculé selon les cinq positions de Ptolémée**. "
         "**L'histoire d'une idée, non de la médecine — consultez un "
         "médecin.**"),
    "جدول مواضع الأجرام في أي لحظة تختارها.":
        ("A table of body positions for any moment you choose.",
         "Un tableau des positions pour tout instant choisi."),
    "لمن أراد أن يبني على الفَلَك، أو يُصدّر تقويمه.":
        ("For anyone who wants to build on Al-Falak, or export their "
         "calendar.",
         "Pour qui veut bâtir sur Al-Falak, ou exporter son calendrier."),

    # ══════════════════════════════════════════════════════════
    # التوافق والمسائل والبازي والجيوتِش
    #
    # **ومصطلحُ كل مدرسة يبقى باسمه**: `Bazi` و`Jyotish` و
    # `Ashtakoota` و`Dasha` — فمن قرأ بالإنجليزية يعرفها بهذه
    # وحدها، ومن ترجمها إلى «Four Pillars of Destiny» وحدها
    # قطع القارئ عن مصادره.
    # ══════════════════════════════════════════════════════════
    "التوافق بين خريطتين": ("Synastry — two charts compared",
                             "Synastrie — deux thèmes comparés"),
    "التوافق بين خريطتين — الفَلَك": ("Synastry — Al-Falak",
                                       "Synastrie — Al-Falak"),
    "الفَلَك — التوافق": ("Al-Falak — Synastry", "Al-Falak — Synastrie"),
    "احسب التوافق": ("Compute synastry", "Calculer la synastrie"),
    "اعكس الطرفين": ("Swap the two", "Inverser les deux"),
    "أقوى الوصلات بينكما": ("Your strongest contacts",
                             "Vos contacts les plus forts"),
    "الموازين الثلاثة": ("The three scores", "Les trois scores"),
    "عاطفي": ("Romantic", "Amoureux"),
    "صداقة": ("Friendship", "Amitié"),
    "مهني": ("Working", "Professionnel"),
    "تقبّل": ("Reception", "Réception"),
    "التقبّل": ("Reception", "Réception"),
    "تراكب البيوت — أين يقع كلٌّ من حياة الآخر":
        ("House overlays — where each falls in the other's life",
         "Superpositions de maisons — où chacun tombe dans la vie de l'autre"),
    "الخريطة المركّبة": ("The composite chart", "Le thème composite"),
    "المركّبة": ("Composite", "Composite"),
    "خريطة دافيسون": ("The Davison chart", "Le thème de Davison"),
    "دافيسون": ("Davison", "Davison"),
    "العجلة المزدوجة": ("The bi-wheel", "La double roue"),
    "٪ من الخرائط": ("% of charts", "% des thèmes"),
    "إخفاء التفصيل": ("Hide the detail", "Masquer le détail"),
    "ساعة الميلاد تهمّ هنا أكثر ممّا تهمّ في الخريطة الواحدة: وصلات الطالع ووسط السماء وتراكب البيوت كلّها تتغيّر بتغيّر الساعة. فإن كانت مقدَّرة، اقرأ الوصلات بين الكواكب وحدها ودع الباقي.":
        ("Birth time matters more here than in a single chart: contacts to "
         "the Ascendant and Midheaven, and all the house overlays, shift "
         "with the hour. If your time is only estimated, read the "
         "planet-to-planet contacts alone and leave the rest.",
         "L'heure compte davantage ici que pour un thème seul : les "
         "contacts à l'Ascendant et au Milieu du Ciel, et toutes les "
         "superpositions, changent avec l'heure. Si elle est estimée, ne "
         "lisez que les contacts entre planètes."),
    "تُوضع الخريطتان إحداهما فوق الأخرى، فيُنظر في زوايا كواكب كلٍّ إلى كواكب الآخر، وفي أيّ بيوت كلٍّ وقعت كواكب صاحبه. ومعها ثلاثة موازين — عاطفي وصداقة ومهني — ومع كلّ ميزان تفصيلٌ يُظهر من أين جاءت درجته.":
        ("The two charts are laid one over the other: each one's planets "
         "are read against the other's, and each is seen in whose houses "
         "the other's planets fall. With them come three scores — "
         "romantic, friendship and working — each with a breakdown showing "
         "where its points came from.",
         "Les deux thèmes sont superposés : les planètes de chacun sont "
         "lues face à celles de l'autre, et l'on voit dans quelles maisons "
         "elles tombent. S'y ajoutent trois scores — amoureux, amitié et "
         "professionnel — chacun détaillé."),
    "الخريطة تصف ميلًا، والعِشرة تصنعها المعاملة.":
        ("A chart describes an inclination; a relationship is made by how "
         "people treat each other.",
         "Un thème décrit un penchant ; une relation se construit par la "
         "manière dont on se traite."),
    "الحساب بمكتبة Swiss Ephemeris · الموازين رتبة مئوية مقابل ستّة آلاف زوج عشوائي.":
        ("Computed with the Swiss Ephemeris · the scores are percentile "
         "ranks against six thousand random pairs.",
         "Calculé avec la Swiss Ephemeris · les scores sont des rangs "
         "centiles face à six mille couples aléatoires."),

    # ــ المسائل ــ
    "المسائل — الفَلَك": ("Horary — Al-Falak", "Horaire — Al-Falak"),
    "الفَلَك — المسائل": ("Al-Falak — Horary", "Al-Falak — Horaire"),
    "خريطة اللحظة": ("The chart of the moment", "Le thème de l'instant"),
    "اللحظة الآن": ("This very moment", "Cet instant même"),
    "ساعة السؤال": ("Hour of the question", "Heure de la question"),
    "سؤالك": ("your question", "votre question"),
    "احكم في المسألة": ("Judge the question", "Juger la question"),
    "الاعتبارات": ("Considerations", "Considérations"),
    "الاعتبارات قبل الحكم": ("Considerations before judgement",
                              "Considérations avant jugement"),
    "دليل السائل": ("Significator of the querent",
                     "Significateur du consultant"),
    "دليل المسؤول عنه": ("Significator of the quesited",
                          "Significateur du sujet"),
    "الدليلان والشاهد": ("The two significators and the witness",
                          "Les deux significateurs et le témoin"),
    "القمر — شاهد كل مسألة": ("The Moon — witness to every question",
                               "La Lune — témoin de chaque question"),
    "التمام — أيقع الاتّصال قبل خروج الدليل من برجه؟":
        ("Perfection — does the contact complete before the significator "
         "leaves its sign?",
         "Perfection — le contact s'achève-t-il avant que le significateur "
         "ne quitte son signe ?"),
    ": أيقع بينهما اتّصال قبل أن يخرج أحدهما من برجه؟":
        (": does a contact form between them before either leaves its sign?",
         ": un contact se forme-t-il avant que l'un ne quitte son signe ?"),
    "يتمّ بواسطة": ("completes by translation", "s'achève par translation"),
    "يتمّ بعد جهد": ("completes after effort", "s'achève après effort"),
    "تُردّ المسألة": ("the question is returned unjudged",
                       "la question est renvoyée sans jugement"),
    "بيدك أنت": ("in your own hands", "entre vos mains"),
    "حدود هذا الباب": ("The limits of this craft",
                        "Les limites de cet art"),
    "المصادر والحدود": ("Sources and limits", "Sources et limites"),
    "وقوع السؤال في نفسك": ("when the question took hold of you",
                             "quand la question s'est imposée à vous"),
    "الوقت هنا هو لحظة": ("The time here is the moment",
                           "L'heure ici est l'instant"),
    "مبنى هذا الباب أن السؤال إذا اضطرم في صدر صاحبه فسأل، كانت السماء في تلك اللحظة صورةً لجوابه. ولا يُحكم فيه بالمزاج: تُنظر":
        ("This craft rests on the idea that when a question burns in someone "
         "and they ask it, the sky of that moment mirrors its answer. It is "
         "not judged by mood: first are examined the",
         "Cet art repose sur l'idée que lorsqu'une question brûle en "
         "quelqu'un et qu'il la pose, le ciel de cet instant en reflète la "
         "réponse. On ne juge pas à l'humeur : on examine d'abord les"),
    "أوّلًا، فإن كان في الخريطة ما يمنع رُدّت المسألة ولم يُتكلَّف لها جواب. ثم يُنظر في":
        ("first, and if the chart forbids, the question is returned and no "
         "answer is forced. Then are examined the",
         "d'abord, et si le thème l'interdit, la question est renvoyée sans "
         "réponse forcée. Puis on examine les"),
    ", لا وقت فتحك للصفحة. وكلّما كان السؤال مصوغًا صياغة دقيقة كان الجواب أوضح — وأكثر الحيرة تنحلّ بصياغة السؤال وحدها.":
        (", not when you opened this page. The more precisely the question "
         "is framed, the clearer the answer — and most confusion dissolves "
         "in the framing alone.",
         ", non l'heure d'ouverture de cette page. Plus la question est "
         "précise, plus la réponse est claire."),
    "، لا وقت فتحك للصفحة. وكلّما كان السؤال مصوغًا صياغة دقيقة كان الجواب أوضح — وأكثر الحيرة تنحلّ بصياغة السؤال وحدها.":
        (", not when you opened this page. The more precisely the question "
         "is framed, the clearer the answer — and most confusion dissolves "
         "in the framing alone.",
         ", non l'heure d'ouverture de cette page. Plus la question est "
         "précise, plus la réponse est claire."),
    "البيوت على ريجومونتانوس، وهو مذهب أهل هذا الباب.":
        ("Houses by Regiomontanus, the convention of this craft.",
         "Maisons selon Regiomontanus, la convention de cet art."),
    "الاعتبارات وقواعد التمام من «التفهيم» للبيروني و«البارع» لابن أبي الرجال.":
        ("The considerations and rules of perfection come from al-Biruni's "
         "Tafhim and Ibn Abi al-Rijal's al-Bari'.",
         "Les considérations et règles de perfection viennent du Tafhim "
         "d'al-Biruni et du Bari' d'Ibn Abi al-Rijal."),

    # ــ البازي ــ
    "الأعمدة الأربعة": ("The four pillars", "Les quatre piliers"),
    "الأعمدة الأربعة — البازي — الفَلَك":
        ("The four pillars — Bazi — Al-Falak",
         "Les quatre piliers — Bazi — Al-Falak"),
    "الفَلَك — الأعمدة الأربعة": ("Al-Falak — Four pillars",
                                   "Al-Falak — Quatre piliers"),
    "احسب الأعمدة": ("Compute the pillars", "Calculer les piliers"),
    "أعمدتك الأربعة": ("Your four pillars", "Vos quatre piliers"),
    "سيّد النفس": ("Day Master", "Maître du Jour"),
    "— سيّد النفس": ("— Day Master", "— Maître du Jour"),
    "ميزان العناصر الخمسة": ("The balance of the five elements",
                              "L'équilibre des cinq éléments"),
    "نسبة كل عمود إليك": ("What each pillar is to you",
                           "Ce que chaque pilier est pour vous"),
    "دورات الحظّ": ("Luck cycles", "Cycles de chance"),
    "دورات الحظّ — عشرًا عشرًا": ("Luck cycles — ten years at a time",
                                   "Cycles de chance — par dix ans"),
    "— لدورات الحظّ —": ("— for the luck cycles —",
                          "— pour les cycles de chance —"),
    "ما ينقصك، وكيف يُطلَب": ("What you lack, and how it is sought",
                               "Ce qui vous manque, et comment le chercher"),
    "خشب": ("Wood", "Bois"), "نار": ("Fire", "Feu"),
    "تراب": ("Earth", "Terre"), "معدن": ("Metal", "Métal"),
    "ماء": ("Water", "Eau"),
    "الجنس": ("Sex", "Sexe"),
    "التوافق الصيني — الفروع والعناصر":
        ("Chinese compatibility — branches and elements",
         "Compatibilité chinoise — branches et éléments"),
    "اتّجاه دورات الحظّ يختلف بالجنس وجذع السنة — وهذه قاعدة منصوصة في كتبهم، لا تمييز منّا. ولذلك يُسأل عنه هنا ولا يُسأل في الصفحات الأخرى.":
        ("The direction of the luck cycles differs by sex and by the year's "
         "stem — a rule stated in their own books, not a distinction of "
         "ours. That is why it is asked here and nowhere else.",
         "Le sens des cycles de chance dépend du sexe et du tronc de "
         "l'année — une règle énoncée dans leurs propres livres, non une "
         "distinction de notre part."),
    "لا دائرة هنا ولا بروج: أربعة أعمدة للسنة والشهر واليوم والساعة، لكلٍّ حرفان — فثمانية حروف تُقرأ بها حياتك، ومن هنا اسمها «بازي». وحرف يوم مولدك هو":
        ("No wheel here and no signs: four pillars — year, month, day and "
         "hour — each of two characters. Eight characters in all, by which "
         "your life is read; hence the name Bazi (\"eight characters\"). "
         "The character of your birth day is your",
         "Ni roue ni signes : quatre piliers — année, mois, jour et heure — "
         "de deux caractères chacun. Huit caractères en tout, d'où le nom "
         "Bazi. Le caractère de votre jour de naissance est votre"),
    ": أنت في هذه الخريطة، وإليه يُقاس كل ما سواه.":
        (": you in this chart, and everything else is measured against it.",
         ": vous dans ce thème, et tout le reste s'y mesure."),
    "الفصول الشمسية محسوبة من طول الشمس بمكتبة Swiss Ephemeris، لا من جداول مستوردة.":
        ("The solar terms are computed from the Sun's longitude with the "
         "Swiss Ephemeris, not from imported tables.",
         "Les termes solaires sont calculés depuis la longitude du Soleil "
         "avec la Swiss Ephemeris, non depuis des tables importées."),
    "المصادر: «滴天髓» نُخبة أسرار السماء، و«三命通會».":
        ("Sources: Di Tian Sui (\"Drops of Heavenly Marrow\") and San Ming "
         "Tong Hui.",
         "Sources : Di Tian Sui et San Ming Tong Hui."),
    "أزن العناصر الخمسة…": ("… weighing the five elements",
                             "… pesée des cinq éléments"),
    "أُركّب الأعمدة الأربعة…": ("… assembling the four pillars",
                                 "… assemblage des quatre piliers"),
    "أحسب الفصول الشمسية…": ("… computing the solar terms",
                              "… calcul des termes solaires"),

    # ــ الجيوتِش ــ
    "الخريطة الهندية — الجيوتِش — الفَلَك":
        ("Vedic chart — Jyotish — Al-Falak",
         "Thème védique — Jyotish — Al-Falak"),
    "الفَلَك — الخريطة الهندية": ("Al-Falak — Vedic chart",
                                   "Al-Falak — Thème védique"),
    "احسب الخريطة الهندية": ("Compute the Vedic chart",
                              "Calculer le thème védique"),
    "خريطتك بالحساب الهندي": ("Your chart in the Vedic system",
                               "Votre thème en système védique"),
    "مذهب القياس (أينامشا)": ("Ayanamsha (the measuring convention)",
                               "Ayanamsha (convention de mesure)"),
    "الكواكب التسعة": ("The nine grahas", "Les neuf grahas"),
    "فترات عمرك — الدشا": ("The periods of your life — Dasha",
                            "Les périodes de votre vie — Dasha"),
    "الخرائط المقسَّمة (الفَرغا)": ("The divisional charts (Varga)",
                                     "Les thèmes divisionnaires (Varga)"),
    "اليوغات المتحقّقة": ("The yogas present", "Les yogas présents"),
    "التوافق الهندي — الأشتا كوتا": ("Vedic compatibility — Ashtakoota",
                                      "Compatibilité védique — Ashtakoota"),
    "الحسابان جنبًا إلى جنب": ("The two systems side by side",
                                "Les deux systèmes côte à côte"),
    "المدارس الثلاث جنبًا إلى جنب": ("The three traditions side by side",
                                      "Les trois traditions côte à côte"),
    "وفرقه عن الحساب العربي اليوم": ("and how it differs from the Arabic "
                                      "reckoning today",
                                      "et sa différence avec le comput arabe"),
    "السماء نفسها، مقيسةً من نقطة أخرى. الهنود يقيسون من النجوم الثابتة، والعرب والغربيّون من نقطة اعتدال الربيع — وقد تباعدت النقطتان مع القرون حتى صار بينهما نحو أربع وعشرين درجة. فأكثر أبراجك ستتراجع برجًا، وهذا ليس خطأً.":
        ("The same sky, measured from a different point. Indian astrology "
         "measures from the fixed stars; Arabic and Western astrology from "
         "the spring equinox — and the two points have drifted apart over "
         "the centuries until some twenty-four degrees now lie between "
         "them. So most of your signs will step back by one. This is not "
         "an error.",
         "Le même ciel, mesuré depuis un autre point. L'Inde mesure depuis "
         "les étoiles fixes ; le monde arabe et l'Occident depuis "
         "l'équinoxe de printemps — et les deux points se sont écartés au "
         "fil des siècles jusqu'à quelque vingt-quatre degrés. La plupart "
         "de vos signes reculeront d'un cran. Ce n'est pas une erreur."),
    "المثلّث الأصلي": ("The original trine", "Le trigone d'origine"),
    "الهبوط": ("Debilitation", "Débilitation"),
    "الذروة": ("Exaltation", "Exaltation"),
    "التزاوج": ("Combination", "Combinaison"),
    "كبرى": ("major", "majeur"),
    "نادرة": ("rare", "rare"),
    "موضع": ("position", "position"),
    "درجة.": ("degrees.", "degrés."),
    "قراءة المواضع": ("Reading of the positions",
                       "Lecture des positions"),
    "(ما بقي منها)": ("(what remains of it)", "(ce qu'il en reste)"),
    "أُحدّد المنازل…": ("… locating the nakshatras",
                         "… localisation des nakshatras"),
    "أحسب المواقع النجمية…": ("… computing sidereal positions",
                               "… calcul des positions sidérales"),
    "أحسب فترات العمر…": ("… computing the life periods",
                           "… calcul des périodes"),
    "المصادر: بريهات باراشارا هورا شاسترا، وبريهات جاتاكا لڤاراها ميهيرا.":
        ("Sources: Brihat Parashara Hora Shastra, and Varahamihira's "
         "Brihat Jataka.",
         "Sources : Brihat Parashara Hora Shastra, et le Brihat Jataka de "
         "Varahamihira."),
    "الحساب بمكتبة Swiss Ephemeris على المنطقة النجمية · أينامشا لاهيري افتراضًا.":
        ("Computed with the Swiss Ephemeris on the sidereal zodiac · "
         "Lahiri ayanamsha by default.",
         "Calculé avec la Swiss Ephemeris sur le zodiaque sidéral · "
         "ayanamsha Lahiri par défaut."),
    "— اختر —": ("— choose —", "— choisir —"),
    "باريس…": ("Paris…", "Paris…"),

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
    # **وكلمةٌ تُلصَق بعددٍ متغيّر لا تكون مفتاحًا.**
    # «١٢٦ مصطلحًا» يتبدّل عددُه بتبدّل المعجم، فلا عبارةَ ثابتة
    # تُطابَق. والمفرداتُ هي البابُ الموضوع لهذا بعينه.
    "مصطلحًا", "تعذّر الاتصال بالخادم", "ضعفًا",
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
