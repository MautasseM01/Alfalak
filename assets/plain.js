/* مفتاح اللغة — يبدّل الموقع كلّه بين لغة عامّة ولغة الصناعة */

const LEVELS = { plain: 'بلغة مبسّطة', expert: 'بلغة أهل الصناعة' };

/* المستوى الحالي — يُقرأ من التخزين، وافتراضه المبسّط */
function getLevel() {
  const v = store.get('level', null);
  return (v === 'plain' || v === 'expert') ? v : 'plain';
}
function setLevel(v) { store.set('level', v); }

/* عناوين الواجهة الثابتة: تُبدَّل في الصفحة نفسها */
const UI = {
  'الأجرام والكرامات': 'الكواكب وقوّتها',
  'الأوتاد والبيوت': 'النقاط الرئيسية والبيوت',
  'الزوايا بين الأجرام': 'الزوايا بين الكواكب',
  'الأشكال الزاوية': 'الأشكال الهندسية',
  'الغالب في الخريطة': 'ما يغلب على شخصيتك',
  'جوّك الشخصي': 'ما يخصّك أنت',
  'السهام': 'النقاط المحسوبة',
  'الأَلْمُطَن': 'الكوكب الحاكم',
  'الجرم': 'الكوكب',
  'الدرجة': 'الموضع',
  'الكرامة': 'القوّة',
  'الوجاج': 'الفارق',
  'العابر': 'الكوكب المارّ',
  'يتمّ': 'يكتمل',
  'نافذته': 'مدّته',
  'حاكم اليوم': 'كوكب اليوم',
  'أفضل الأيام وأسوأها': 'أفضل الأيام وأصعبها',
  'الكواكب الراجعة': 'الكواكب المتراجعة',
  'مواقع الكواكب': 'مواقع الكواكب',
  'السرعة اليومية': 'سرعته اليومية',
  'مُقبِلة': 'تشتدّ',
  'مُدبِرة': 'تنفكّ',
  'خلو مسار': 'فراغ قمر',
  'الطالع': 'الطالع',
};

/* جُمل تمهيدية تشرح الصفحة لمن يراها أوّل مرّة */
const INTROS = {
  chart: 'خريطة الميلاد صورة للسماء لحظة ولادتك: أين كان كل كوكب، وأيّ برج '
       + 'كان صاعدًا في الأفق. منها تُقرأ الطباع والميول.',
  bulletin: 'النشرة اليومية تصف حال السماء في يوم بعينه: أين القمر، وما '
          + 'الأوقات المناسبة وما يُفضّل تأجيله.',
  monthly: 'النشرة الشهرية تجمع أحداث الشهر كلّه: انتقالات الكواكب، والكسوف، '
         + 'وأفضل أيام الشهر لكل غرض.',
  sky: 'عجلةٌ تتحرّك بالزمن: قدّم الساعة أو اليوم أو السنة وانظر كيف تسير '
     + 'الكواكب في البروج، ومتى ترجع. والمرسوم جهةُ الجرم كما تُرى.',
  eclipses: 'يجتمع النيّران اثنتي عشرة مرّةً في السنة ولا يكسفان إلّا مرّتين '
          + 'أو ثلاثًا. والفارقُ هو العقدة، وهذه الصفحة تحسبها وتعرض القاعدة '
          + 'لتمتحنها بنفسك.',
  hours: 'قسّم القدماء النهار اثنتي عشرة ساعة والليل مثلها، ونسبوا كل ساعة '
       + 'إلى كوكب. فلكل ساعة طبع، ولكل عمل ساعة تناسبه.',
  ephemeris: 'جدول يبيّن موضع كل كوكب في السماء في أي لحظة تختارها.',
};

/* تبديل النصوص الثابتة داخل الصفحة (العناوين وأسماء الأعمدة) */
function applyUiLevel(root) {
  const level = getLevel();
  (root || document).querySelectorAll('[data-term]').forEach(el => {
    const t = el.dataset.term;
    el.textContent = (level === 'plain' && UI[t]) ? UI[t] : t;
  });
}

/* بناء المفتاح في شريط التصفّح */
function initLevelSwitch(onChange) {
  const nav = document.querySelector('.topbar');
  if (!nav || document.getElementById('levelSw')) return;

  const wrap = document.createElement('div');
  wrap.className = 'seg levelsw';
  wrap.id = 'levelSw';
  wrap.setAttribute('role', 'group');
  wrap.setAttribute('aria-label', 'مستوى اللغة');
  wrap.innerHTML =
    `<button data-lv="plain">مبسّطة</button>` +
    `<button data-lv="expert">لغة الصناعة</button>`;
  nav.appendChild(wrap);

  const paint = () => {
    const lv = getLevel();
    wrap.querySelectorAll('button').forEach(b =>
      b.setAttribute('aria-pressed', b.dataset.lv === lv ? 'true' : 'false'));
  };
  wrap.querySelectorAll('button').forEach(b => {
    b.onclick = () => {
      setLevel(b.dataset.lv);
      paint();
      applyUiLevel();
      if (onChange) onChange(getLevel());
    };
  });
  paint();
  applyUiLevel();
}

/* جملة تمهيدية أعلى الصفحة، تظهر في الوضع المبسّط وحده */
function pageIntro(key) {
  if (getLevel() !== 'plain' || !INTROS[key]) return;
  const lede = document.querySelector('p.lede');
  if (!lede || lede.dataset.introDone) return;
  lede.dataset.introDone = '1';
  const box = document.createElement('div');
  box.className = 'alert note';
  box.style.marginBottom = '18px';
  box.innerHTML = `<strong>ما هذه الصفحة؟</strong><br>${INTROS[key]}`;
  lede.after(box);
}

/* يُضاف تلقائيًّا إلى كل نداء API */
function withLevel(params) {
  return Object.assign({ level: getLevel() }, params || {});
}
