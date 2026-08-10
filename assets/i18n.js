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
  'script', 'style', 'textarea', 'input', 'select', 'code', 'pre',
  '.no-i18n', '.hint-pop', '.wheel',
  /* **`[data-body]` رُفع من هذه القائمة.** وضعتُه أوّلًا حمايةً
     لمخرجات الحساب — فإذا **صفوفُ جدول الأجرام كلُّها تحمله**،
     فكنتُ أحمي الجدول من الترجمة التي بُنيت له. والحمايةُ
     الحقيقية هي حدُّ الطول في المفردات لا استثناءُ الصفوف. */
].join(',');

/* ــ المشي: نصٌّ بنصّ، وما وُجد في القاموس بُدِّل ــ
   ونحفظ الأصل في `dataset` كي يرجع العربيّ بلا إعادة تحميل. */
function i18nWalk(root, dict) {
  if (!dict) return 0;
  let n = 0;
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
    node.nodeValue = raw.replace(key, hit);
    n++;
  });

  /* السمات المرئية: النائب والعنوان ووصف قارئ الشاشة */
  ['placeholder', 'title', 'aria-label'].forEach(a => {
    (root || document.body).querySelectorAll('[' + a + ']').forEach(el => {
      if (el.closest('.no-i18n')) return;
      const key = (el.getAttribute(a) || '').trim().replace(/\s+/g, ' ');
      const hit = dict[key];
      if (!hit) return;
      if (!el.dataset['i18nA' + a]) el.dataset['i18nA' + a] = el.getAttribute(a);
      el.setAttribute(a, hit);
      n++;
    });
  });
  return n;
}

/* الرجوع إلى العربية: يُستعاد المحفوظ، فلا إعادة تحميل */
function i18nRestore() {
  document.querySelectorAll('[data-i18n-ar]').forEach(p => {
    const orig = p.dataset.i18nAr;
    const t = [...p.childNodes].find(x => x.nodeType === 3 && x.nodeValue.trim());
    if (t) t.nodeValue = orig;
    delete p.dataset.i18nAr;
  });
  ['placeholder', 'title', 'aria-label'].forEach(a => {
    document.querySelectorAll('[data-i18n-a' + a + ']').forEach(el => {
      el.setAttribute(a, el.dataset['i18nA' + a]);
      delete el.dataset['i18nA' + a];
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

    if (I18N_LANG === 'ar') { I18N_DICT = null; i18nBar(); return; }

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
  const p = document.createElement('p');
  p.id = 'i18nNote';
  p.className = 'note no-i18n';
  p.dir = 'ltr';
  p.style.cssText = 'border-inline-start:3px solid var(--gold);' +
    'padding-inline-start:12px;margin:14px 0';
  p.textContent = I18N_NOTE;
  main.insertBefore(p, main.firstChild);
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
    t = setTimeout(() => i18nWalk(document.body, I18N_DICT), 140);
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
