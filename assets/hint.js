/* ══════════════════════════════════════════════════════════════════
   الشرح عند التحويم — hint.js

   الغاية: **ألّا يمرّ على القارئ لفظٌ لا يفهمه**. فمن حوّم على كلمة
   لا يعرفها ظهر له شرحها، ومن حوّم على كوكب في العجلة ظهر له موضعه
   ومعناه — من غير ضغط ولا انتقال إلى صفحة أخرى.

   وفيه ثلاثة أبواب:
   ١. محرّك واحد للشرح، يفتح بالتحويم وبالتركيز وباللمس.
   ٢. وسمٌ تلقائي لمصطلحات المعجم في كل نصّ يُعرَض — فلا نحتاج أن
      نضع علامة «؟» بأيدينا في كل صفحة، ولا يفوتنا موضع.
   ٣. مصدرٌ ثانٍ للشرح: السمة `data-hint` لمن أراد نصًّا خاصًّا
      بالعنصر (كأجرام العجلة)، فلا يقتصر الأمر على المعجم.

   ── درسٌ مدفوع الثمن ───────────────────────────────────────────
   سبق أن سمّينا بطاقات الصفحة الرئيسة `.q`، وهو صنف علامة المعجم
   نفسه — فالتقطها مستمع المعجم وأظهر «undefined» **ومنع الانتقال**،
   فتعطّلت بطاقات الموقع الستّ. ولذلك في هذا الملفّ:
   **كل صنف يخصّ هذا النظام يبدأ بـ `hint-`**، ولا نلتقط عنصرًا إلا
   بسمة صريحة (`[data-term]` أو `[data-hint]`) لا بصنف عامّ.
   ══════════════════════════════════════════════════════════════════ */

/* ── معجم المصطلحات: يُجلب مرّة واحدة ────────────────────────── */
let HINT_TERMS = null;
let HINT_PENDING = null;

function hintTerms() {
  if (HINT_TERMS) return Promise.resolve(HINT_TERMS);
  if (HINT_PENDING) return HINT_PENDING;
  HINT_PENDING = fetch('/api/glossary')
    .then(r => r.json())
    .then(r => (HINT_TERMS = r.terms || {}))
    .catch(() => (HINT_TERMS = {}));
  return HINT_PENDING;
}

const hintEsc = t => String(t == null ? '' : t)
  .replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ══════════════════════════════════════════════════════════════
   ١ ــ اللوحة: واحدة تُعاد، لا واحدة لكل عنصر
   ══════════════════════════════════════════════════════════════ */
const HINT = {
  el: null, arrow: null, owner: null,
  openT: 0, closeT: 0, pinned: false, inside: false,
};

const HINT_OPEN_DELAY = 110;   /* ريثما يعبر المؤشّر مارًّا فلا يُزعج */
const HINT_CLOSE_DELAY = 220;  /* ريثما ينتقل المؤشّر إلى اللوحة نفسها */

function hintPanel() {
  if (HINT.el) return HINT.el;
  const el = document.createElement('div');
  el.className = 'hint-pop';
  el.setAttribute('role', 'tooltip');
  el.id = 'hint-pop';
  el.innerHTML = '<i class="hint-arrow"></i><div class="hint-in"></div>' +
                 '<button class="hint-x" aria-label="إغلاق الشرح">×</button>';
  document.body.appendChild(el);
  HINT.el = el;
  HINT.arrow = el.querySelector('.hint-arrow');

  /* اللوحة نفسها لا تُغلق بمجرّد دخول المؤشّر إليها — وإلّا تعذّرت
     قراءتها، وهذا أشهر عيوب لوحات التحويم. */
  el.addEventListener('pointerenter', () => { HINT.inside = true; clearTimeout(HINT.closeT); });
  el.addEventListener('pointerleave', () => { HINT.inside = false; hintClose(HINT_CLOSE_DELAY); });
  el.querySelector('.hint-x').addEventListener('click', () => { HINT.pinned = false; hintClose(0); });
  return el;
}

function hintClose(delay) {
  clearTimeout(HINT.closeT);
  HINT.closeT = setTimeout(() => {
    if (HINT.pinned || HINT.inside) return;
    if (!HINT.el) return;
    HINT.el.classList.remove('show', 'pinned');
    if (HINT.owner) {
      HINT.owner.removeAttribute('aria-describedby');
      HINT.owner.classList.remove('hint-on');
      /* رفع الإضاءة عن نظير العنصر في العجلة أو الجدول */
      hintLink(HINT.owner, false);
    }
    HINT.owner = null;
  }, delay == null ? HINT_CLOSE_DELAY : delay);
}

/* ــ من أين يأتي النصّ ــ
   `data-hint` مقدَّمٌ على المعجم: فمن كتب شرحًا خاصًّا بالعنصر
   فهو أعلم بموضعه من شرح عامّ. */
async function hintContent(el) {
  const raw = el.getAttribute('data-hint');
  if (raw != null && raw !== '') {
    const title = el.getAttribute('data-hint-title') || '';
    const lines = raw.split('|').map(s => s.trim()).filter(Boolean);
    const term = el.getAttribute('data-term');
    let more = '';
    if (term) {
      const terms = await hintTerms();
      if (terms[term]) more = `<p class="hint-glo"><b>${hintEsc(term)}</b> — ${hintEsc(terms[term])}</p>`;
    }
    return (title ? `<strong>${hintEsc(title)}</strong>` : '') +
           lines.map(l => `<p>${hintEsc(l)}</p>`).join('') + more;
  }
  const term = el.getAttribute('data-term');
  if (!term) return '';
  const terms = await hintTerms();
  const text = terms[term];
  if (!text) {
    /* لا نطبع «undefined» أبدًا — هذا ما وقع من قبل. */
    return `<strong>${hintEsc(term)}</strong><p>لم يُكتب شرح هذا المصطلح بعد.</p>`;
  }
  return `<strong>${hintEsc(term)}</strong><p>${hintEsc(text)}</p>` +
         `<a href="/learn.html#${encodeURIComponent(term)}">المزيد في صفحة التعلّم ›</a>`;
}

async function hintShow(el, pin) {
  clearTimeout(HINT.closeT);
  const pop = hintPanel();
  const html = await hintContent(el);
  if (!html) return;
  /* قد يكون المؤشّر غادر أثناء انتظار المعجم */
  if (!pin && !el.matches(':hover') && el !== document.activeElement && !HINT.pinned) return;

  if (HINT.owner && HINT.owner !== el) {
    HINT.owner.removeAttribute('aria-describedby');
    HINT.owner.classList.remove('hint-on');
    hintLink(HINT.owner, false);
  }
  pop.querySelector('.hint-in').innerHTML = html;
  HINT.owner = el;
  HINT.pinned = !!pin;
  pop.classList.toggle('pinned', !!pin);
  pop.classList.add('show');
  el.setAttribute('aria-describedby', 'hint-pop');
  el.classList.add('hint-on');
  hintLink(el, true);
  hintPlace(el);
}

/* ــ الموضع: تحت العنصر، فإن ضاق ما تحته فوقه ــ */
function hintPlace(el) {
  const pop = HINT.el;
  const r = el.getBoundingClientRect();
  const w = Math.min(340, innerWidth - 20);
  pop.style.width = w + 'px';
  pop.style.visibility = 'hidden';
  pop.style.top = '0px';
  const h = pop.offsetHeight;
  pop.style.visibility = '';

  const cx = r.left + r.width / 2;
  let left = cx + scrollX - w / 2;
  left = Math.max(10 + scrollX, Math.min(left, scrollX + innerWidth - w - 10));

  const room = innerHeight - r.bottom;
  const above = room < h + 16 && r.top > h + 16;
  const top = above ? r.top + scrollY - h - 10 : r.bottom + scrollY + 10;

  pop.style.left = left + 'px';
  pop.style.top = top + 'px';
  pop.classList.toggle('above', above);
  /* السهم يشير إلى العنصر لا إلى وسط اللوحة */
  const ax = Math.max(14, Math.min(cx + scrollX - left, w - 14));
  HINT.arrow.style.insetInlineStart = 'auto';
  HINT.arrow.style.left = ax + 'px';
}

/* ══════════════════════════════════════════════════════════════
   ٢ ــ التمييز المتبادل: العجلة والجدول
   المرور على كوكب في العجلة يُضيء صفّه في الجدول، والعكس.
   وهذا ما يفتقده أكثر المواقع: الرسم في وادٍ والجدول في وادٍ.
   ══════════════════════════════════════════════════════════════ */
function hintBodyName(el) {
  /* الاسم قد يكون على العنصر نفسه (جِرم العجلة) أو على جدٍّ له
     (صفّ الجدول، فالمصطلح الموسوم داخله هو المُحوَّم عليه). */
  const own = el.getAttribute && el.getAttribute('data-body');
  if (own) return own;
  const up = el.closest && el.closest('[data-body]');
  return up ? up.getAttribute('data-body') : null;
}

function hintLink(el, on) {
  const name = hintBodyName(el);
  if (!name) return;
  const self = (el.getAttribute && el.getAttribute('data-body')) ? el : el.closest('[data-body]');
  document.querySelectorAll(`[data-body="${CSS.escape(name)}"]`).forEach(o => {
    if (o !== self) o.classList.toggle('hint-echo', on);
  });
}

/* التمييز المتبادل يعمل ولو لم يكن على العنصر شرح: يكفي أن يحمل
   `data-body`. فالمرور على صفّ المريخ في الجدول يُضيء المريخ في
   العجلة، وإن لم يكن في الصفّ ما يُشرَح. */
function initBodyEcho() {
  let cur = null;
  const set = (el) => {
    if (cur === el) return;
    if (cur) hintLink(cur, false);
    cur = el;
    if (cur) hintLink(cur, true);
  };
  document.addEventListener('pointerover', e => {
    if (e.pointerType === 'touch') return;
    const el = e.target.closest && e.target.closest('[data-body]');
    set(el || null);
  }, true);
  document.addEventListener('pointerleave', () => set(null), true);
}

/* ══════════════════════════════════════════════════════════════
   ٣ ــ المستمعون: تحويم + تركيز + لمس
   ══════════════════════════════════════════════════════════════ */
const HINT_SEL = '[data-term],[data-hint]';

/* ══════════════════════════════════════════════════════════════
   `<title>` يُبتَلع حين نتولّى الشرح

   في العجلة كان كل عنصرٍ يحمل شيئين: `data-hint` لبطاقتنا،
   و`<title>` داخل الـSVG. وكان ذلك **بنيّةٍ حسنة**: `<title>`
   ما تقرأه قارئات الشاشة، وما يبقى إن تعطّل السكربت.

   لكنّ أثره في المتصفّح **تلميحان يظهران معًا**: فقاعة النظام
   الصفراء فوق بطاقتنا، تُعيد الاسم والدرجة اللذين في رأس
   البطاقة. فيقرأ الزائر الشيء مرّتين في نَفَسٍ واحد.

   والحلّ **لا يكون بحذف `<title>` من الرسم** — فذلك يُسقط
   القارئ الضرير ومَن عطّل الجافاسكربت. بل يُنقَل مضمونُه إلى
   `aria-label` ثم يُحذَف العنصر: فمَن جاء بلا سكربت وجد
   `<title>` كما كان، ومَن تولّينا صفحتَه وجد بطاقةً واحدة
   وقارئُ شاشته يقرأ التسمية نفسها.
   ══════════════════════════════════════════════════════════════ */
function hintEatTitles(root) {
  (root || document).querySelectorAll(`${HINT_SEL}`).forEach(el => {
    const t = el.querySelector(':scope > title');
    if (!t) return;
    const txt = (t.textContent || '').trim();
    if (txt && !el.getAttribute('aria-label')) el.setAttribute('aria-label', txt);
    t.remove();
  });
}

function initHints() {
  hintTerms();
  hintPanel();
  hintEatTitles();

  /* التحويم — بالفأرة وحدها. واللمس يولّد pointerenter كذلك، فنُقصيه
     صراحةً كي لا تفتح اللوحةُ مرّتين على الجوّال. */
  document.addEventListener('pointerover', e => {
    if (e.pointerType === 'touch') return;
    const el = e.target.closest && e.target.closest(HINT_SEL);
    if (!el || el === HINT.owner) return;
    if (HINT.pinned) return;
    clearTimeout(HINT.openT);
    HINT.openT = setTimeout(() => hintShow(el, false), HINT_OPEN_DELAY);
  }, true);

  document.addEventListener('pointerout', e => {
    if (e.pointerType === 'touch') return;
    const el = e.target.closest && e.target.closest(HINT_SEL);
    if (!el) return;
    clearTimeout(HINT.openT);
    hintClose(HINT_CLOSE_DELAY);
  }, true);

  /* الضغط يُثبّت اللوحة — وهو السبيل الوحيد على الجوّال.
     ولا نمنع السلوك الأصلي إلّا لعناصر ليست روابط، حتى لا نُعطّل
     الانتقال كما وقع في بطاقات البوّابة. */
  document.addEventListener('click', e => {
    const el = e.target.closest && e.target.closest(HINT_SEL);
    if (!el) {
      if (!e.target.closest('.hint-pop')) { HINT.pinned = false; hintClose(0); }
      return;
    }
    const navigates = el.tagName === 'A' && el.getAttribute('href');
    if (!navigates) { e.preventDefault(); e.stopPropagation(); }
    if (HINT.pinned && HINT.owner === el) { HINT.pinned = false; hintClose(0); return; }
    hintShow(el, true);
  });

  /* لوحة المفاتيح: التركيز يفتح، وEscape يُغلق. */
  document.addEventListener('focusin', e => {
    const el = e.target.closest && e.target.closest(HINT_SEL);
    if (el) hintShow(el, false);
  });
  document.addEventListener('focusout', e => {
    const el = e.target.closest && e.target.closest(HINT_SEL);
    if (el && !HINT.pinned) hintClose(HINT_CLOSE_DELAY);
  });
  addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    HINT.pinned = false; HINT.inside = false; hintClose(0);
    if (HINT.owner && HINT.owner.focus) HINT.owner.focus();
  });

  addEventListener('scroll', () => {
    if (!HINT.el || !HINT.el.classList.contains('show') || !HINT.owner) return;
    hintPlace(HINT.owner);
  }, { passive: true });
  addEventListener('resize', () => { HINT.pinned = false; HINT.inside = false; hintClose(0); });
}

/* ══════════════════════════════════════════════════════════════
   ٤ ــ الوسم التلقائي للمصطلحات

   كنّا نضع علامة «؟» بأيدينا حيث تذكّرنا، فيفوتنا أكثرها. والصواب
   أن يمرّ ماسحٌ على النصّ المعروض فيَسِم كل مصطلح في المعجم.

   وثلاث دقائق في التنفيذ:
   ــ **الأطول أوّلًا**: «البيوت الكاملة» قبل «البيوت»، وإلّا وسمنا
     نصف اللفظ وتركنا نصفه.
   ــ **التشكيل**: المعجم فيه «الأَلْمُطَن» مشكولًا وقد يرد في النصّ
     بلا شكل — فنبني النمط متسامحًا مع الحركات بين الحروف.
   ــ **حروف الجرّ والعطف**: «والشمس» و«بالشمس» يجب أن تُوسَما،
     فنسمح بحرف واحد من «وفبكل» قبل «ال».
   ══════════════════════════════════════════════════════════════ */
const HINT_HARAKAT = '[\\u064B-\\u0652\\u0640\\u0670]*';
const HINT_LETTER = '\\u0621-\\u064A';
const HINT_MAX_PER_TERM = 2;   /* حتى لا يصير النصّ كله خطوطًا */

function hintTermPattern(term) {
  const bare = term.replace(/[ً-ْـٰ]/g, '');
  let body = '';
  for (const ch of bare) {
    if (/\s/.test(ch)) { body += '\\s+'; continue; }
    if ('اأإآ'.includes(ch)) body += '[اأإآ]';
    else if ('يى'.includes(ch)) body += '[يى]';
    else body += ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    body += HINT_HARAKAT;
  }
  /* «ال» التعريف قد يسبقها حرف واحد من حروف الجرّ والعطف */
  const prefix = /^ا?ل/.test(bare) ? '[وفبكل]?' : '';
  return `(?<![${HINT_LETTER}])${prefix}${body}(?![${HINT_LETTER}])`;
}

let HINT_RE = null;
let HINT_ORDER = null;

function hintBuildRegex(terms) {
  HINT_ORDER = Object.keys(terms).sort((a, b) => b.length - a.length);
  const parts = HINT_ORDER.map(t => `(${hintTermPattern(t)})`);
  try {
    HINT_RE = new RegExp(parts.join('|'), 'g');
  } catch {
    HINT_RE = null;   /* متصفّح قديم لا يعرف النظر إلى الخلف — نمضي بلا وسم */
  }
}

/* ══════════════════════════════════════════════════════════════
   أين لا يدخل الماسح — والثمن الذي دُفع

   **خللٌ شحنتُه**: بنيتُ قائمة اختيار من عندنا، فدخل الماسحُ
   خياراتِها ووسم «البيوت الكاملة» و«القبّاني» و«بلاسيدوس»
   داخل `role="option"`. فوقع أمران:
     ١. صار في الخيار عنصرٌ `role="button"` — فاختلّت دلالة
        القائمة عند قارئ الشاشة.
     ٢. و`hint.js` يستدعي `stopPropagation()` عند الضغط، **فلا
        يصل اختيار النظام إلى القائمة أصلًا**. أي إنّي كسرتُ
        بيدي المكوّنَ الذي بنيتُه في الجولة السابقة.

   والقاعدة المستخلصة: **الماسح لا يدخل عنصرًا تفاعليًّا ولا ما
   يحمل دورًا في ARIA**. وكل مكوّن جديد يُضاف إلى هذه القائمة يوم
   يُبنى، لا يوم يُكتشف الخلل.
   ══════════════════════════════════════════════════════════════ */
const HINT_SKIP = [
  'script', 'style', 'textarea', 'input', 'select', 'option', 'code', 'pre',
  'button', 'a', 'label', 'kbd',
  '.hint-pop', '.no-hint', '[data-term]', '[data-hint]',
  '.topbar', 'nav', '.doors', '.printhead',
  /* المكوّنات التفاعلية */
  '.sel', '.sel-list', '.sel-btn', '.ac', '.tabs', '.chips', '.seg',
  '[role="option"]', '[role="listbox"]', '[role="combobox"]',
  '[role="tab"]', '[role="tablist"]', '[role="menu"]',
  /* عناوين البطاقات: تُضغَط لتُطوى، فلا يُزاحمها الشرح */
  '.card-title', '.card-top',
].join(',');

let HINT_MARKING = false;

function markTerms(root) {
  if (!HINT_RE || HINT_MARKING) return 0;
  root = root || document.body;
  if (!root || root.nodeType !== 1) return 0;
  HINT_MARKING = true;
  let marked = 0;
  try {
    const seen = Object.create(null);
    document.querySelectorAll('b.hint-term[data-term]').forEach(b => {
      const t = b.getAttribute('data-term');
      seen[t] = (seen[t] || 0) + 1;
    });

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (!n.nodeValue || n.nodeValue.length < 3) return NodeFilter.FILTER_REJECT;
        if (!n.parentElement || n.parentElement.closest(HINT_SKIP)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const targets = [];
    for (let n = walker.nextNode(); n; n = walker.nextNode()) targets.push(n);

    for (const node of targets) {
      const text = node.nodeValue;
      HINT_RE.lastIndex = 0;
      let m, out = null, last = 0;
      while ((m = HINT_RE.exec(text))) {
        const gi = m.findIndex((v, i) => i > 0 && v !== undefined);
        if (gi < 1) continue;
        const term = HINT_ORDER[gi - 1];
        if ((seen[term] || 0) >= HINT_MAX_PER_TERM) continue;
        seen[term] = (seen[term] || 0) + 1;
        out = out || document.createDocumentFragment();
        if (m.index > last) out.appendChild(document.createTextNode(text.slice(last, m.index)));
        const b = document.createElement('b');
        b.className = 'hint-term';
        b.setAttribute('data-term', term);
        b.setAttribute('tabindex', '0');
        b.setAttribute('role', 'button');
        b.setAttribute('aria-label', `ما معنى ${term}؟`);
        b.textContent = m[0];
        out.appendChild(b);
        last = m.index + m[0].length;
        marked++;
      }
      if (out) {
        if (last < text.length) out.appendChild(document.createTextNode(text.slice(last)));
        node.parentNode.replaceChild(out, node);
      }
    }
  } finally {
    HINT_MARKING = false;
  }
  return marked;
}

/* ــ تعريف الزائر بالميزة مرّةً واحدة ــ
   ميزةٌ لا يعرف بها أحد كأنها غير موجودة. فنُظهر سطرًا واحدًا أوّل
   مرّة يُوسَم فيها مصطلح، ثم لا يعود أبدًا. */
/* **خطأ كلّفني ثقة القارئ**: كانت هذه الدالّة تُستدعى من المُراقب بعد
   كل تغيير في الشجرة، **بلا حارس** — فتُدرج نسخةً جديدة في كل مرّة.
   فامتلأت الصفحة بالسطر نفسه مكرَّرًا كأنه في حلقة، **وكل إدراج
   يُزحزح ما تحته فتَرتجّ الشاشة**.

   وفيه خطآن لا واحد:
   ١. لا حارس يمنع التكرار — وهذا سببه المباشر.
   ٢. إدراجه **داخل تدفّق الصفحة** يُزحزح المحتوى. والصواب أن يطفو
      فوقها فلا يُزحزح شيئًا مهما ظهر أو اختفى. */
let HINT_TIP_DONE = false;

function hintFirstTip() {
  if (HINT_TIP_DONE) return;
  if (document.querySelector('.hint-tip')) { HINT_TIP_DONE = true; return; }
  try { if (localStorage.getItem('falak.hintTip')) { HINT_TIP_DONE = true; return; } }
  catch { HINT_TIP_DONE = true; return; }
  if (!document.querySelector('b.hint-term')) return;
  HINT_TIP_DONE = true;

  const bar = document.createElement('div');
  bar.className = 'hint-tip';
  bar.setAttribute('role', 'status');
  bar.innerHTML = '<span>الكلمات ذات الخطّ المنقّط مشروحة — <b>مرّر المؤشّر عليها</b>، ' +
                  'وكذلك كل عنصر في العجلة.</span>' +
                  '<button class="hint-tip-x" aria-label="فهمت، أخفِ هذا">فهمت</button>';
  const done = () => {
    try { localStorage.setItem('falak.hintTip', '1'); } catch { }
    bar.classList.remove('in');
    setTimeout(() => bar.remove(), 220);
  };
  bar.querySelector('.hint-tip-x').addEventListener('click', done);
  document.body.appendChild(bar);            /* يطفو، فلا يُزحزح سطرًا */
  requestAnimationFrame(() => bar.classList.add('in'));
  setTimeout(done, 14000);                   /* ولا يبقى معلّقًا أبدًا */
}

/* يُشغَّل بعد كل عرض جديد. والمراقب مؤجَّل حتى تهدأ الصفحة، فوسمُ
   المصطلحات يُحدث بذاته تغييرًا في الشجرة — ولولا `HINT_MARKING`
   لدار على نفسه بلا نهاية. */
function initAutoTerms() {
  hintTerms().then(terms => {
    if (!terms || !Object.keys(terms).length) return;
    hintBuildRegex(terms);
    markTerms(document.body);
    hintFirstTip();
    let t = 0;
    const obs = new MutationObserver(() => {
      if (HINT_MARKING) return;
      clearTimeout(t);
      /* **والعجلة تُرسَم بعد التحميل**، فلا يكفي ابتلاعُ العناوين
         مرّةً عند الإقلاع: كل رسمٍ جديد يأتي بـ`<title>` جديدة. */
      t = setTimeout(() => {
        markTerms(document.body); hintEatTitles(document.body); hintFirstTip();
      }, 160);
    });
    obs.observe(document.body, { childList: true, subtree: true });
  });
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', () => { initHints(); initBodyEcho(); initAutoTerms(); });
  else { initHints(); initBodyEcho(); initAutoTerms(); }
}

if (typeof module !== 'undefined' && module.exports)
  module.exports = { hintTermPattern, markTerms, hintBuildRegex, hintEsc };
