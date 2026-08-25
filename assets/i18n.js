/* ══════════════════════════════════════════════════════════════════
   تبديل اللغة — i18n.js

   **المفتاح هو النصّ العربي نفسه.** فلا تُعدَّل الصفحات، ولا
   تُوسَم عناصرها بـ`data-i18n`، ومن جاء بلا جافاسكربت رأى
   عربيّةً صحيحة لا مفاتيح. وما لم يُترجَم يبقى عربيًّا من نفسه.

   والآليّة هي آليّة `hint.js` نفسها: مشيٌ على عُقَد النصّ.
   وقد جُرّبت هناك وثبتت، فلا نخترع ثانيةً.

   ── ثلاثة أشياء لا يمسّها المشي ────────────────────────────────
   ١. **حقول الإدخال** — قيمتُها بيانات المستخدم لا نصُّنا.
   ٢. **مخرجات الحساب** — الدرجات والبروج وأسماء الأجرام تأتي
      من الخادم، وهي المتن لا الأثاث. وترجمتُها في القاموس
      العربيّ للمحرّك لا هنا.
   ٣. **`.no-i18n`** — بابٌ صريح لمن أراد استثناء موضع.

   ── والاتّجاه ينقلب ────────────────────────────────────────────
   `dir` على `<html>` يصير `ltr`. والتنسيق مبنيٌّ على الخصائص
   المنطقية (`inset-inline`, `margin-inline-end`) فينقلب معه.
   ══════════════════════════════════════════════════════════════════ */

const I18N_KEY = 'falakLang';
let I18N_DICT = null;
let I18N_LANG = 'ar';
let I18N_BUSY = false;

/* اللغة المطلوبة: من الرابط أوّلًا (فالرابط يُشارَك)، ثم المحفوظة */
function i18nWanted() {
  const q = new URLSearchParams(location.search).get('lang');
  if (q && ['ar', 'en', 'fr'].includes(q)) return q;
  try { return localStorage.getItem(I18N_KEY) || 'ar'; } catch { return 'ar'; }
}

const I18N_SKIP = [
  'script', 'style', 'textarea', 'input', 'code', 'pre',
  /* **و`select` رُفع من هنا.** وضعتُه أوّلًا مع `input` بحجّة
     «قيمتُها بيانات المستخدم» — **وذلك خلطٌ بين الحقل وقائمته**:
     قيمةُ `input` يكتبها الزائر، وأمّا نصُّ `<option>` فنحن
     كتبناه. فكانت كلُّ قائمةٍ منسدلة في الموقع تبقى عربيّةً
     مهما تُرجم القاموس: «— اختر —» و«شهر» و«— كل الساعات —».
     والقيمةُ (`value`) لا تُمَسّ، فالمشي على النصّ لا السمات. */
  '.no-i18n', '.hint-pop', '.wheel',
  /* **`[data-body]` رُفع من هذه القائمة.** وضعتُه أوّلًا حمايةً
     لمخرجات الحساب — فإذا **صفوفُ جدول الأجرام كلُّها تحمله**،
     فكنتُ أحمي الجدول من الترجمة التي بُنيت له. والحمايةُ
     الحقيقية هي حدُّ الطول في المفردات لا استثناءُ الصفوف. */
].join(',');

/* ══════════════════════════════════════════════════════════════
   **الشَّرطةُ لا تدخل `dataset` — وكانت تُسقط الترجمة كلَّها**

   كنتُ أحفظ أصلَ السمة في `el.dataset['i18nA' + a]`. وذلك يصحّ
   في `placeholder` و`title`، **ويرمي في `aria-label`**:

       'i18nAaria-label' is not a valid property name

   فأسماءُ `dataset` تُحوَّل إلى `data-*` بقاعدةٍ لا تقبل الشرطة.

   ــ **وأثرُه لم يكن في السمة وحدها** ــ

   الرَّمْيُ يقع داخل `i18nWalk`، فيخرج منها **قبل تمامها**،
   فلا يُنفَّذ `i18nBar()` ولا `i18nNotice()` بعدها. فكل صفحةٍ
   فيها `aria-label` — **وهي كلُّها** — كانت ترميه.

   ولم يظهر في المتصفّح لأنّه يقع في آخر المشي، بعد أن تُرجم
   النصّ. **فالصفحة تبدو مترجمةً وهي ناقصة.**

   وما التقطه إلّا القياسُ من الصفحة. **والقياسُ من القائمة لا
   يرى رميًا، إذ لا يشغّل شيئًا.**
   ══════════════════════════════════════════════════════════ */
function i18nBak(attr) {
  return 'i18nA' + attr.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
}

/* ══════════════════════════════════════════════════════════════
   **العبارةُ تُطابَق على العنصر، لا على عُقدة النصّ**

   هذا إصلاحُ عيبٍ صنعتُه بيدي. أضفتُ `i18nMarkFirst()` لينجو
   التلميح، فصار `hint.js` يلفّ المصطلح في `<b class="hint-term">`
   **فيشقّ عُقدة النصّ ثلاثًا**:

       «المنازل القمرية» + « والاختيارات من تراث الأنواء العربي.»

   والمفتاح في القاموس هو الجملةُ كاملة، ولم تعد موجودةً كعُقدة.
   فتُترجَم الشظيّةُ وحدها ويبقى سائرُها عربيًّا:

       Lunar mansions والاختيارات من تراث الأنواء العربي.

   **وهو أسوأ من العربيّة الصافية** — وقد كتبتُ ذلك في هذا الملفّ
   نفسه ثم خالفتُه.

   ــ **ولماذا لا يُحلّ بالترتيب** ــ

   جرّبتُ الترتيبين: الوسمُ أوّلًا يكسر العبارة، والترجمةُ أوّلًا
   تُخفي التلميح (إذ يبحث `hint.js` عن عربيّةٍ لم تعد هناك).
   **فالعلّة ليست في أيّهما يسبق، بل في أنّ الترجمة كانت تنظر
   في العُقدة وحدها.** فتُنظَر في العنصر كلِّه أوّلًا.

   ــ **وحدُّه ضيّق عمدًا** ــ

   لا يُستبدَل إلّا عنصرٌ **كلُّ أبنائه `b.hint-term`** — أي ما
   كسره الوسمُ بعينه. فلا يُمَسّ عنصرٌ فيه رابطٌ أو زرّ، إذ
   استبدالُ نصّه يمحو الرابط. **والإصلاح الواسع يكسر ما لم
   يُشتَكَ منه.**

   والتلميحُ يسقط عن هذه العناصر بالإنجليزية حتى يُترجَم المعجم
   (وهي الخطوة التالية) — **وسقوطُه خيرٌ من تلميحٍ عربيّ فوق
   كلمةٍ إنجليزية**، وذلك ما اشترطتَه.
   ══════════════════════════════════════════════════════════ */
const I18N_INLINE = new Set(['B', 'I', 'EM', 'STRONG', 'SPAN', 'SMALL',
  'U', 'MARK', 'ABBR', 'BDI', 'WBR', 'SUP', 'SUB']);

/* عنصرٌ يجوز ابتلاعُ نصّه: تأكيدٌ محضٌ لا يُفقَد بفقده شيء */
function i18nInline(c) {
  if (!I18N_INLINE.has(c.tagName)) return false;   /* رابطٌ أو زرّ: لا */
  if (c.id || c.hasAttribute('onclick')) return false;
  if (c.children.length) return false;             /* تعشيشٌ: لا نُخاطر */
  return true;
}

/* ══════════════════════════════════════════════════════════════
   **الحارسُ ينظر في الفقرة، لا في الأب المباشر.**

   أوّل صياغةٍ لي فحصت `node.parentElement` وحده. وأبو الشظيّة
   في `<b>` **لا أبناء له**، فيمرّ الفحص وتُترجَم الشظيّة داخل
   فقرةٍ عربيّة، فيخرج على الزائر:

       ... والمسائل، and synastry، وأرباب الأزمنة ...

   **وهذا خليطٌ صنعتُه بحارسٍ وضعتُه لمنع الخلط.** فالحارسُ
   الذي ينظر خطوةً واحدة يحرس خطوةً واحدة.

   فيُصعَد الآن إلى **أقرب فقرةٍ جامعة**: أوّل جدٍّ يحمل أكثر
   من ابنٍ أو نصًّا مباشرًا حول أبنائه. فإن كانت جملةً عربيّةً
   كاملةً لا مفتاح لها، تُركت شظاياها كلُّها.
   ══════════════════════════════════════════════════════════ */
function i18nBroken(node, dict) {
  /* **والصعودُ يقف عند أوّل حاوية.**
     أوّل صياغةٍ للصعود بلغت أربعة آباء بلا شرط، فأصابت
     البطاقاتِ والأقسام — ونصُّها الكامل طويلٌ ليس مفتاحًا
     أبدًا. **فمنع الحارسُ الترجمةَ في كل موضع: ٨٢ صارت ٣٩٢.**

     فالفقرةُ عنصرٌ **كلُّ أبنائه تأكيدٌ محض**. فإذا وُجد ابنٌ
     غيرُ ذلك فهو حاوية، وعندها يقف الصعود ولا يُمنَع شيء. */
  let p = node && node.parentElement, best = null;
  for (let i = 0; p && i < 5; i++, p = p.parentElement) {
    if (p.dataset.i18nHtml !== undefined) return false;   /* تُرجمت كاملة */
    if (![...p.children].every(c => i18nInline(c))) break; /* حاوية: قف */
    best = p;
  }
  if (!best || best.closest(I18N_SKIP)) return false;
  const whole = (best.textContent || '').trim().replace(/\s+/g, ' ');
  /* جملةٌ حقيقيّة لا سطرَ جدول ولا زرًّا */
  if (whole.length < 60 || whole.split(' ').length < 8) return false;
  if (dict[whole]) return false;
  /* ══════════════════════════════════════════════════════
     **ولا يُمنَع ما لا خلطَ فيه.**

     بطاقاتُ الصفحة الرئيسة `<a><b>من أنا؟</b><em>خريطة
     مولدك…</em></a>` — نصُّها الجامع ٦٥ حرفًا وليس مفتاحًا،
     **فكان الحارس يردّها**. وشظاياها كلُّها في القاموس!

     فالحارسُ إنّما وُضع لمنع بقاء نصفٍ عربيًّا. **فإذا كان
     كلُّ جزءٍ مترجَمًا فلا نصف يبقى، ولا علّة للمنع.**
     ومنعُه هنا حِرمانٌ لا حراسة. */
  const w2 = document.createTreeWalker(best, NodeFilter.SHOW_TEXT);
  while (w2.nextNode()) {
    const s = (w2.currentNode.nodeValue || '').trim().replace(/\s+/g, ' ');
    if (!s || !/[؀-ۿ]/.test(s)) continue;
    /* **وعلامةُ ترقيمٍ ليست شظيّةً تبقى عربيّة.**
       في بطاقات الصفحة الرئيسة `<span class="i">؟</span>` — رمزٌ
       مرسوم لا نصّ. وكان يُسقط البطاقة كلَّها في يد الحارس،
       فتبقى ثلاثُ عباراتٍ مترجَمةٍ عربيّةً لأجل حرفٍ واحد. */
    if ([...s].filter(c => /[ء-ي]/.test(c)).length < 2) continue;
    if (!dict[s]) return true;          /* شظيّةٌ ستبقى عربيّة: امنع */
  }
  return false;                         /* الكلُّ معروف: لا خلط */
}

function i18nPhrase(root, dict) {
  let n = 0;
  const scope = root || document.body;
  const els = [scope, ...scope.querySelectorAll('*')];
  for (const el of els) {
    if (!el.children.length) continue;          /* بلا أبناء: يكفيه المشي */
    if (el.closest(I18N_SKIP)) continue;
    if (el.dataset.i18nHtml !== undefined) continue;
    /* **الشرط**: كلُّ أبنائه وسمُ تأكيدٍ لا يحمل فعلًا ولا وجهة.
       وأوّل صياغةٍ لي اشترطت `b.hint-term` وحدها — **وهو حدٌّ
       أضيق ممّا يجب**: نزل الرقم ٥٨ وبقي التذييل مكسورًا في
       كلّ صفحة، لأنّ فيه `<b>` عاديّة كتبتُها في `hint.js`.
       فأصلحتُ الكسر الذي عرفتُه لا الكسرَ كلَّه.

       والمقصود إخراجُ ما يُفقَد باستبدال النصّ: رابطٌ أو زرّ
       أو عنصرٌ يُنادى باسمه أو يحمل مستمعًا. **وأمّا التأكيد
       فيُفقَد عمدًا، وفقدُه أهون من خلط اللسانين.** */
    if (![...el.children].every(c => i18nInline(c))) continue;
    const key = (el.textContent || '').trim().replace(/\s+/g, ' ');
    const hit = key && dict[key];
    if (!hit) continue;
    el.dataset.i18nHtml = el.innerHTML;         /* الوسمُ كلُّه يُحفَظ */
    el.textContent = hit;
    n++;
  }
  return n;
}

/* ــ المشي: نصٌّ بنصّ، وما وُجد في القاموس بُدِّل ــ
   ونحفظ الأصل في `dataset` كي يرجع العربيّ بلا إعادة تحميل. */
function i18nWalk(root, dict) {
  if (!dict) return 0;
  let n = i18nPhrase(root, dict);
  const w = document.createTreeWalker(root || document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      const p = node.parentElement;
      if (!p || p.closest(I18N_SKIP)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  const hits = [];
  while (w.nextNode()) hits.push(w.currentNode);
  hits.forEach(node => {
    const raw = node.nodeValue;
    const key = raw.trim().replace(/\s+/g, ' ');
    /* ══════════════════════════════════════════════════════
       **الجملةُ تُترجَم كاملةً أو تُترَك — ولا تُشقّ.**

       فقرةٌ ليست في القاموس، وفيها `<b>البرج</b>` وهو مفتاح.
       فيترجمه المشي وحده، فيخرج على الزائر:

           Sign يقول how, and the house says where.

       **وهذا خليطٌ صنعناه صنعًا**، ولم يكن ليقع لو تُركت
       الفقرة عربيّةً صافية. وقد كتبتُ في هذا الملفّ نفسه
       «والخلطُ أسوأ من العربيّة الصافية» ثم أنتجتُه من باب
       ثانٍ — أوّلُه كسرُ الوسم، وهذا ثانيه.

       فإن كان أبو العُقدة فقرةً عربيّةً كاملة **لا مفتاح
       لها**، تُركت شظاياها كلُّها. والنقصُ الصافي يُرى
       فيُعالَج، والخليطُ يُخفي نفسه. */
    if (i18nBroken(node, dict)) return;
    let hit = dict[key];
    /* **المفردات: بابٌ ثانٍ لا غنًى عنه.**
       خليّةُ الجدول تقول «3° 28′ العذراء»، وهي ليست مفتاحًا
       ولن تكون — فالدرجة تتبدّل في كل خريطة. فلو اكتفينا
       بمطابقة العبارة لبقيت الجداول عربيّةً **وإن بلغ القاموس
       مئةً بالمئة**.

       ولا تُطبَّق إلّا على القصير: خليّةُ الجدول قصيرة وفقرةُ
       القراءة طويلة، ولو بُدِّلت المفردات داخل الفقرات لخرج
       خليطٌ لا يُقرأ: «تُحبّ Venus صورةً لا شخصًا».
       **والخلطُ أسوأ من العربيّة الصافية.** */
    if (!hit && I18N_VOCAB && key.length <= I18N_VMAX) {
        const sub = i18nVocab(key);
        if (sub !== key) hit = sub;
    }
    if (!hit) return;
    const p = node.parentElement;
    /* الأصل يُحفَظ مرّةً واحدة: أوّلُ ترجمةٍ تُثبّته، وما بعدها
       يُترجم عنه لا عن المترجَم — وإلّا ضاع العربيّ بعد تبديلين. */
    if (!p.dataset.i18nAr) p.dataset.i18nAr = raw;
    /* ══════════════════════════════════════════════════════
       **الفراغُ يُحفَظ، ولا يُبحَث عن المفتاح في الخام.**

       كان `raw.replace(key, hit)`. والمفتاح **مسوّى** (سطرٌ
       واحد ومسافةٌ مفردة)، والخامُ كما كُتب في الصفحة —
       وأكثرُ الفقرات تمتدّ سطرين:

           <p class="lede">
             أدوات فلكية بالعربية، ...
             ولستَ مضطرًّا أن تعرف ...
           </p>

       فالمفتاح **ليس نصًّا فرعيًّا من الخام**، فلا يُبدِّل
       `replace` شيئًا — **ويسقط بلا خطأ ولا أثر**. فبقيت
       صدور الصفحات عربيّةً وهي مترجَمةٌ في القاموس، وقلتُ
       «مطابقةٌ لا تقع» ولم أعرف لِمَ حتى قِستُ.

       والمفتاح هو النصُّ المقصوص كلُّه، فيكفي أن يُوضع
       المترجَم بين فراغَي الطرفين. */
    const lead = raw.match(/^\s*/)[0];
    const tail = raw.match(/\s*$/)[0];
    node.nodeValue = lead + hit + tail;
    n++;
  });

  /* السمات المرئية: النائب والعنوان ووصف قارئ الشاشة */
  ['placeholder', 'title', 'aria-label'].forEach(a => {
    (root || document.body).querySelectorAll('[' + a + ']').forEach(el => {
      if (el.closest('.no-i18n')) return;
      const key = (el.getAttribute(a) || '').trim().replace(/\s+/g, ' ');
      const hit = dict[key];
      if (!hit) return;
      if (!el.dataset[i18nBak(a)]) el.dataset[i18nBak(a)] = el.getAttribute(a);
      el.setAttribute(a, hit);
      n++;
    });
  });
  return n;
}

/* ══════════════════════════════════════════════════════════════
   **الوسمُ قبل الترجمة — وإلّا ضاعت التلميحات كلُّها**

   `hint.js` يَسِم المصطلحات بالبحث عن **نصّها العربي**. وكنّا
   نترجم أوّلًا (بعد ١٤٠ مللي) ثم يَسِم هو (بعد ١٦٠) — فيجد
   إنجليزيّةً لا يعرفها، **فلا يَسِم شيئًا**. فكانت كل صفحةٍ
   تُرسَم بعد تبديل اللغة تخرج **بلا تلميحٍ واحد**.

   وقد قِيس ذلك: صفرُ مصطلحاتٍ موسومة في نتيجةٍ رُسمت بالإنجليزية.

   والحلّ **لا يكون بتأخير رقمٍ عن رقم** — فالتوقيت يتبدّل
   بتبدّل الجهاز والشبكة، ومن بنى ترتيبًا على مللي ثانية بنى
   على رمل. بل يُنادى الوسمُ صراحةً قبل الترجمة.

   وعندئذٍ يبقى `<b data-term="الشمس">` غلافًا، ويُترجَم ما
   بداخله إلى `Sun` — **فالغلاف قائمٌ ومفتاحُه عربيّ**، فيعمل
   التلميح ويُظهر شرحَه.
   ══════════════════════════════════════════════════════════ */
function i18nMarkFirst() {
  try {
    /* **والمعجم المحفوظ يُنسى عند تبدّل اللسان.**
       `hint.js` يخزّن المصطلحات في أوّل طلب. فلو بقي المخزون
       بعد التبديل لوُسمت الصفحةُ الإنجليزية بمعجمٍ عربيّ. */
    if (typeof hintForget === 'function') hintForget();
    if (typeof markTerms === 'function') markTerms(document.body);
  } catch { /* لا تسقط الترجمة لأجل الوسم */ }
}

/* الرجوع إلى العربية: يُستعاد المحفوظ، فلا إعادة تحميل */
function i18nRestore() {
  /* **الوسمُ يُعاد كما كان** — والعبارةُ المستبدَلة حُفظ وسمُها
     كلُّه لا نصُّها، فيرجع التلميحُ معها. وهذا يسبق استعادةَ
     العُقَد، إذ يُعيد بناء أبناءٍ تُستعاد بعده. */
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    el.innerHTML = el.dataset.i18nHtml;
    delete el.dataset.i18nHtml;
  });
  document.querySelectorAll('[data-i18n-ar]').forEach(p => {
    const orig = p.dataset.i18nAr;
    const t = [...p.childNodes].find(x => x.nodeType === 3 && x.nodeValue.trim());
    if (t) t.nodeValue = orig;
    delete p.dataset.i18nAr;
  });
  ['placeholder', 'title', 'aria-label'].forEach(a => {
    /* الاسمُ المحفوظ يُشتَقّ بالقاعدة نفسها — **واشتقاقان
       مختلفان لمفتاحٍ واحد يعني حفظًا لا يُستعاد**. */
    const k = i18nBak(a);
    const sel = '[data-' + k.replace(/[A-Z]/g, c => '-' + c.toLowerCase()) + ']';
    document.querySelectorAll(sel).forEach(el => {
      el.setAttribute(a, el.dataset[k]);
      delete el.dataset[k];
    });
  });
}

async function setLang(lang) {
  if (I18N_BUSY) return;
  I18N_BUSY = true;
  try {
    I18N_LANG = ['ar', 'en', 'fr'].includes(lang) ? lang : 'ar';
    try { localStorage.setItem(I18N_KEY, I18N_LANG); } catch {}

    i18nRestore();
    const html = document.documentElement;
    html.lang = I18N_LANG;
    html.dir = I18N_LANG === 'ar' ? 'rtl' : 'ltr';

    if (I18N_LANG === 'ar') {
      /* **العودةُ إلى العربية كانت تنسى الرسالة.**
         كان هذا السطر يرجع بعد `i18nBar()` وحدها، فيبقى صندوق
         «هذه الصفحة ليست مترجمة» **بالإنجليزية فوق صفحةٍ عربية**.
         وهو أسوأ ما يمكن: القارئ اختار العربية، فيُقال له
         بالإنجليزية إن الصفحة غير مترجمة.

         **والخروجُ المبكّر بابُ نسيان**: كل ما يُضاف بعده لا
         يُنفَّذ في هذا الطريق. فيُنظَّف كلُّ ما وُضع أوّلًا. */
      I18N_DICT = null;
      I18N_VOCAB = null;
      I18N_VRE = null;
      I18N_NOTE = '';
      i18nBar();
      i18nNotice();          /* تُزيلها، فهي تحذف ثم تُعيد الرسم */
      return;
    }

    if (!I18N_DICT || I18N_DICT._lang !== I18N_LANG) {
      const r = await fetch('/api/i18n?lang=' + I18N_LANG);
      const d = await r.json();
      I18N_DICT = d.dict || {};
      I18N_DICT._lang = I18N_LANG;
      I18N_NOTE = d.partial || '';
      I18N_VOCAB = d.vocab || null;
      I18N_VMAX = d.vocab_max || 44;
      if (I18N_VOCAB) i18nVocabRe(I18N_VOCAB);
    }
    i18nMarkFirst();
    i18nWalk(document.body, I18N_DICT);
    i18nBar();
    i18nNotice();
  } finally { I18N_BUSY = false; }
}

let I18N_NOTE = '';
let I18N_VOCAB = null, I18N_VMAX = 44, I18N_VRE = null;

/* النمط يُبنى مرّةً: الأطول أوّلًا كي لا يُلتقَط «القوس» داخل
   «القوس الشمسي». وحرفا العطف والجرّ يُقبَلان قبل المفردة،
   كما في `hint.js` — فالعربية تُلصِق «وال» و«بال» بالكلمة. */
function i18nVocabRe(vocab) {
  const keys = Object.keys(vocab).sort((a, b) => b.length - a.length)
    .map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  /* **ولا يُلتقَط حرفُ العطف.** كتبتُ أوّلًا `([وفبكل]?)` كما في
     `hint.js`، ثم أسقطتُه في التبديل — فكانت «والشمس» تصير
     «Sun» بلا واو. **وابتلاعُ حرفٍ أسوأ من تركِ كلمةٍ عربية.**
     والمفرداتُ هنا في خلايا جداول لا في جُمَل، فحرفُ العطف
     نادرٌ فيها أصلًا. */
  I18N_VRE = new RegExp('(^|[\\s(،؛:·—-])(' + keys.join('|') + ')(?=$|[\\s)،؛:.·—-])', 'g');
}

function i18nVocab(s) {
  if (!I18N_VRE) return s;
  I18N_VRE.lastIndex = 0;
  return s.replace(I18N_VRE, (m, pre, word) => pre + (I18N_VOCAB[word] || word));
}

/* **التنبيه يُقال ولا يُخبَّأ.** من اختار الإنجليزية ورأى القراءة
   عربيّةً حسِب الموقع معطوبًا — والصواب أن يُقال له قبل أن يسأل:
   الأثاث مترجَم والنصوص لا، وذلك عمدًا. */
function i18nNotice() {
  document.getElementById('i18nNote')?.remove();
  if (I18N_LANG === 'ar' || !I18N_NOTE) return;
  const main = document.getElementById('main');
  if (!main) return;
  /* **الرسالة أسطرٌ لا سطر.** أوّلُ صياغةٍ وضعتها في `<p>`
     واحدة بـ`textContent`، فابتُلعت أسطرُها وصارت كتلةً واحدة —
     **وفيها ما يفعله القارئ الآن**، وهو أنفعُ ما فيها.
     فتُقسَم على أسطرها، ويُغلَّظ ما بين نجمتين. */
  const box = document.createElement('div');
  box.id = 'i18nNote';
  box.className = 'i18n-note no-i18n';
  box.dir = 'ltr';
  box.setAttribute('role', 'note');
  const esc0 = t => String(t).replace(/[&<>]/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  box.innerHTML = I18N_NOTE.split('\n')
    .map(line => `<p>${esc0(line).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')}</p>`)
    .join('');
  main.insertBefore(box, main.firstChild);
}

/* مبدّل اللغة في الشريط — بأسماء اللغات بألسنتها لا بأعلام:
   العَلَم يدلّ على بلدٍ لا على لسان، والفرنسية ليست فرنسا وحدها. */
function i18nBar() {
  const bar = document.getElementById('topbar');
  if (!bar) return;
  let box = document.getElementById('langBox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'langBox';
    box.className = 'langbox no-i18n';
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', 'اللغة / Language');
    bar.appendChild(box);
  }
  box.innerHTML = [['ar', 'العربية'], ['en', 'English'], ['fr', 'Français']]
    .map(([k, n]) => `<button type="button" data-lang="${k}"
      class="${k === I18N_LANG ? 'on' : ''}"
      aria-pressed="${k === I18N_LANG}" lang="${k}">${n}</button>`).join('');
}

document.addEventListener('click', e => {
  const b = e.target.closest && e.target.closest('#langBox button[data-lang]');
  if (b) setLang(b.dataset.lang);
});

/* **والصفحات تُعيد بناء نفسها بعد كل حساب** — فما تُرجم مرّةً
   يعود عربيًّا عند أوّل إعادة رسم. فالمراقب يُترجم الجديد وحده. */
function i18nObserve() {
  let t = 0;
  new MutationObserver(() => {
    if (I18N_LANG === 'ar' || !I18N_DICT || I18N_BUSY) return;
    clearTimeout(t);
    /* **الوسمُ قبل الترجمة هنا أيضًا** — وهذا الموضع هو المهمّ:
       نتيجةُ الحساب تُرسَم بعد التبديل، فلولاه خرجت بلا تلميح. */
    t = setTimeout(() => {
      i18nMarkFirst();
      i18nWalk(document.body, I18N_DICT);
    }, 200);
  }).observe(document.body, { childList: true, subtree: true });
}

if (typeof document !== 'undefined') {
  const boot = () => {
    i18nBar();
    i18nObserve();
    const w = i18nWanted();
    if (w !== 'ar') setLang(w);
  };
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', boot);
  else boot();
}
