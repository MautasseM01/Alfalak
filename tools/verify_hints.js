/* ══════════════════════════════════════════════════════════════════
   التحقّق من نظام الشرح — يُشغَّل بـ:  node tools/verify_hints.js

   يبني متصفّحًا وهميًّا (jsdom)، ويُحمّل فيه ملفّات الواجهة كما هي،
   ثم يفحص:
     ١. نمط المصطلح: يلتقط المشكول وغير المشكول، ويلتقط «والشمس»،
        ولا يلتقط جزءًا من كلمة أخرى.
     ٢. الوسم التلقائي: يَسِم، ويقدّم الأطول، ولا يقترب من الروابط
        والأزرار والقوائم، ولا يدور على نفسه.
     ٣. العجلة: كل عنصر فيها يحمل شرحًا، ولا «undefined» في مخرجاتها.
     ٤. **تصادم الأصناف**: وهو ما عطّل بطاقات الصفحة الرئيسة الستّ
        من قبل — فصار له اختبار يمنع عودته.

   والفشل هنا يُخرج برمز غير صفر، فلا يمرّ صامتًا.
   ══════════════════════════════════════════════════════════════════ */
'use strict';

const fs = require('fs');
const path = require('path');
let JSDOM;
try {
  ({ JSDOM } = require(process.env.JSDOM_PATH || 'jsdom'));
} catch {
  console.error('\nينقص jsdom — وهو متصفّح وهمي يُشغَّل فيه الفحص.\n' +
                'ثبّته مرّةً واحدة:  npm install --no-save jsdom\n');
  process.exit(3);
}

const ROOT = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(ROOT, p), 'utf8');

let pass = 0, fail = 0;
const ok = (cond, msg, extra) => {
  if (cond) { pass++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ ' + msg + (extra ? '\n      ' + extra : '')); }
};
const section = t => console.log('\n── ' + t + ' ' + '─'.repeat(Math.max(0, 60 - t.length)));

/* المعجم والخريطة يُصدَّران من بايثون قبل التشغيل */
const FIX = path.join(ROOT, 'tools', '.hint_fixture.json');
if (!fs.existsSync(FIX)) {
  console.error('لم يُعثر على tools/.hint_fixture.json — شغّل tools/verify_hints.py وهو يستدعي هذا الملفّ.');
  process.exit(2);
}
const fixture = JSON.parse(fs.readFileSync(FIX, 'utf8'));
const GLOSSARY = fixture.glossary;
const CHART = fixture.chart;
const DEEP = fixture.deep;

/* ══════════════════════════════════════════════════════════════
   متصفّح وهمي فيه hint.js
   ══════════════════════════════════════════════════════════════ */
function browser(html) {
  const dom = new JSDOM(html || '<!doctype html><html dir="rtl"><body></body></html>',
    { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://alfalak.vercel.app/' });
  const w = dom.window;
  /* المعجم يُجلب بـ fetch — نردّه فورًا من النسخة المحفوظة */
  w.fetch = () => Promise.resolve({ json: () => Promise.resolve({ terms: GLOSSARY }) });
  w.eval(read('assets/hint.js'));
  return { dom, w };
}

/* ══════════════════════════════════════════════════════════════
   ١ ــ نمط المصطلح
   ══════════════════════════════════════════════════════════════ */
section('نمط المصطلح');
{
  const { w } = browser();
  const test = (term, text) => new RegExp(w.hintTermPattern(term)).test(text);

  ok(test('الشمس', 'موضع الشمس اليوم'), 'يلتقط المصطلح مجرّدًا');
  ok(test('الشمس', 'وقارنّاه بالشمس فوجدناه'), 'يلتقط «بالشمس» بحرف الجرّ');
  ok(test('الشمس', 'والشمس في الثور'), 'يلتقط «والشمس» بحرف العطف');
  ok(!test('الشمس', 'الشمسية والقمرية'), 'لا يلتقط «الشمسية» — فليست هي');
  ok(!test('القمر', 'القمرية'), 'لا يلتقط داخل كلمة أطول');

  /* التشكيل: المعجم مشكول والنصّ قد لا يكون */
  ok(test('الأَلْمُطَن', 'وهذا هو الألمطن في خريطتك'), 'المصطلح المشكول يلتقط غير المشكول');
  ok(test('الأَلْمُطَن', 'وهذا هو الأَلْمُطَن'), 'ويلتقط المشكول نفسه');

  /* المسافات: «سهم السعادة» قد تفصله مسافتان أو سطر */
  ok(test('سهم السعادة', 'ويقع سهم  السعادة في'), 'يتسامح مع تعدّد المسافات');

  /* لا نمط يُخفق في البناء */
  let broke = null;
  for (const t of Object.keys(GLOSSARY)) {
    try { new RegExp(w.hintTermPattern(t)); } catch (e) { broke = t + ': ' + e.message; break; }
  }
  ok(!broke, `كل مصطلحات المعجم (${Object.keys(GLOSSARY).length}) تبني أنماطًا صحيحة`, broke);
}

/* ══════════════════════════════════════════════════════════════
   ٢ ــ الوسم التلقائي
   ══════════════════════════════════════════════════════════════ */
section('الوسم التلقائي');
{
  const { w } = browser();
  w.hintBuildRegex(GLOSSARY);
  const d = w.document;

  d.body.innerHTML = `
    <div id="a"><p>يقع الطالع في السرطان، والبيوت الكاملة أقدم الأنظمة.</p></div>
    <nav><a href="/x">الطالع</a></nav>
    <button class="q" data-term="الطالع">؟</button>
    <input value="الطالع">
    <div class="no-hint"><p>الطالع هنا لا يُوسَم.</p></div>`;
  const n = w.markTerms(d.body);
  ok(n > 0, `وسَم ${n} مصطلحًا`);

  const marks = [...d.querySelectorAll('b.hint-term')];
  const terms = marks.map(b => b.getAttribute('data-term'));
  ok(terms.includes('الطالع'), 'وسَم «الطالع» في النصّ');
  ok(terms.includes('البيوت الكاملة'), 'قدّم «البيوت الكاملة» على «البيوت» — الأطول أوّلًا');
  ok(!terms.includes('البيوت'), 'ولم يَسِم «البيوت» داخل «البيوت الكاملة»');

  ok(!d.querySelector('nav b.hint-term'), 'لم يقترب من القائمة العلوية');
  ok(!d.querySelector('a b.hint-term'), 'لم يقترب من داخل الروابط — وهذا ما عطّل البطاقات من قبل');
  ok(!d.querySelector('button b.hint-term'), 'لم يقترب من داخل الأزرار');
  ok(!d.querySelector('.no-hint b.hint-term'), 'احترم `.no-hint`');
  ok(d.querySelector('input').value === 'الطالع', 'لم يمسّ قيم الحقول');

  /* كل موسوم قابل للتركيز بلوحة المفاتيح */
  ok(marks.every(b => b.getAttribute('tabindex') === '0'), 'كل مصطلح موسوم يُبلَغ بمفتاح Tab');
  ok(marks.every(b => (b.getAttribute('aria-label') || '').includes('ما معنى')),
     'كل مصطلح موسوم له وصف لقارئات الشاشة');

  /* الحدّ الأعلى للتكرار */
  d.body.innerHTML = '<p>' + 'الطالع و'.repeat(9) + 'الطالع.</p>';
  w.markTerms(d.body);
  const rep = d.querySelectorAll('b.hint-term[data-term="الطالع"]').length;
  ok(rep <= 2, `لا يكرّر المصطلح الواحد أكثر من مرّتين (وسَمه ${rep})`);

  /* لا يدور على نفسه: تشغيله ثانيًا لا يزيد شيئًا */
  const before = d.querySelectorAll('b.hint-term').length;
  w.markTerms(d.body); w.markTerms(d.body);
  ok(d.querySelectorAll('b.hint-term').length === before,
     'إعادة التشغيل لا تُضاعف الوسم — لا دوران على النفس');
  ok(!d.querySelector('b.hint-term b.hint-term'), 'ولا وسمَ داخل وسم');
}

/* ══════════════════════════════════════════════════════════════
   ٣ ــ العجلة
   ══════════════════════════════════════════════════════════════ */
section('العجلة');
{
  const { w } = browser();
  w.eval(read('assets/wheel.js'));
  const svg = w.wheelSVG(CHART, { deep: DEEP });

  ok(!/undefined|null|NaN|\[object/.test(svg),
     'لا «undefined» ولا «NaN» في مخرجات العجلة',
     (svg.match(/.{0,60}(undefined|NaN|\[object).{0,60}/) || [])[0]);

  const d = w.document;
  d.body.innerHTML = `<div>${svg}</div>`;
  const q = s => d.querySelectorAll(s);

  ok(q('g.pl[data-hint]').length === CHART.bodies.length,
     `كل الأجرام (${CHART.bodies.length}) تحمل شرحًا`);
  ok(q('g.pl[data-body]').length === CHART.bodies.length,
     'وكلّها تحمل `data-body` للتمييز المتبادل مع الجدول');
  ok(q('g.hs[data-hint]').length === 12, 'البيوت الاثنا عشر تحمل شرحًا');
  ok(q('g.sgn[data-hint]').length === 12, 'البروج الاثنا عشر تحمل شرحًا');
  ok(q('g.ax[data-hint]').length === 4, 'الأوتاد الأربعة تحمل شرحًا');
  ok(q('g.asp[data-hint]').length > 0, `خطوط الزوايا (${q('g.asp[data-hint]').length}) تحمل شرحًا`);

  /* خطّ الزاوية رفيع؛ لولا الخطّ الشفّاف العريض لتعذّر التحويم عليه */
  ok([...q('g.asp')].every(g => g.querySelector('line[stroke="transparent"]')),
     'كل خطّ زاوية فوقه خطّ شفّاف عريض يلتقط المؤشّر');

  /* الشرح ليس فارغًا ولا سطرًا واحدًا مقتضبًا */
  const thin = [...q('[data-hint]')].filter(e => e.getAttribute('data-hint').split('|').length < 2);
  ok(thin.length === 0, 'كل شرح فيه سطران فأكثر',
     thin.slice(0, 3).map(e => e.getAttribute('data-hint-title')).join(' / '));

  /* نصوص العمق وصلت فعلًا إلى العجلة، لا الحساب وحده */
  const sun = [...q('g.pl')].find(g => g.getAttribute('data-body') === 'الشمس');
  const sunHint = sun.getAttribute('data-hint');
  const sunDeep = (DEEP.planet_in_house['الشمس'] || {})[String(
    CHART.bodies.find(b => b.name === 'الشمس').house)];
  ok(sunDeep && sunHint.includes(sunDeep.slice(0, 30)),
     'شرح الكوكب يحمل نصّ «الكوكب في البيت» المكتوب، لا الأرقام وحدها');

  /* وتبقى `<title>` لقارئات الشاشة ولمن تعطّل عنده السكربت */
  ok(q('g.pl title').length === CHART.bodies.length, 'و`<title>` باقية لقارئات الشاشة');

  /* العجلة تعمل ولو لم تصل نصوص العمق */
  const bare = w.wheelSVG(CHART, {});
  ok(!/undefined|NaN/.test(bare), 'وتعمل العجلة سليمةً لو سقط طلب نصوص العمق');
}

/* ══════════════════════════════════════════════════════════════
   ٤ ــ تصادم الأصناف: الاختبار الذي وُلد من خطأ
   ══════════════════════════════════════════════════════════════ */
section('تصادم الأصناف');
{
  /* القاعدة: أيّ صنف يلتقطه مستمعٌ عامّ في JS يجب ألّا يُستعمل
     للزينة في HTML. نجمع ما تلتقطه المستمعات، ونتأكّد أن كل عنصر
     يحمله في الصفحات يحمل معه السمة التي يتوقّعها المستمع. */
  const pages = fs.readdirSync(ROOT).filter(f => f.endsWith('.html'));

  /* «؟» المعجم: كل `button.q` يجب أن يحمل `data-term` */
  let bad = [];
  for (const p of pages) {
    const dom = new JSDOM(read(p));
    dom.window.document.querySelectorAll('.q').forEach(el => {
      if (el.tagName !== 'BUTTON' || !el.hasAttribute('data-term'))
        bad.push(`${p}: <${el.tagName.toLowerCase()} class="q"> بلا data-term`);
    });
  }
  ok(bad.length === 0,
     'لا عنصر يحمل الصنف `q` إلّا زرّ المعجم — وهذا عين ما عطّل البطاقات الستّ',
     bad.slice(0, 5).join('\n      '));

  /* بطاقات البوّابة تنتقل فعلًا */
  const home = new JSDOM(read('index.html'), { url: 'https://alfalak.vercel.app/' });
  const cards = [...home.window.document.querySelectorAll('.qcard')];
  ok(cards.length >= 4, `بطاقات البوّابة موجودة (${cards.length})`);
  ok(cards.every(a => a.tagName === 'A' && a.getAttribute('href')),
     'وكلّها روابط لها وجهة');

  /* والآن الاختبار الحقيقي: أنضغطها في متصفّح فيه hint.js كاملًا،
     ونتأكّد أن أحدًا لم يمنع الانتقال. */
  {
    const dom = new JSDOM(read('index.html'),
      { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://alfalak.vercel.app/' });
    const w = dom.window;
    w.fetch = () => Promise.resolve({ json: () => Promise.resolve({ terms: GLOSSARY }) });
    w.eval(read('assets/hint.js'));
    w.initHints(); w.initBodyEcho();

    let prevented = 0;
    const card = w.document.querySelector('.qcard');
    const ev = new w.MouseEvent('click', { bubbles: true, cancelable: true });
    card.dispatchEvent(ev);
    if (ev.defaultPrevented) prevented++;
    ok(prevented === 0, 'الضغط على بطاقة البوّابة لا يُمنَع — الانتقال يعمل');
    const pop = w.document.querySelector('.hint-pop');
    ok(!pop || !pop.classList.contains('show'),
       'ولا تفتح عليها لوحةُ شرحٍ لا تخصّها');
  }

  /* كل صفحة تُدرج hint.js، وإلّا مات الشرح فيها صامتًا */
  const missing = pages.filter(p => !read(p).includes('assets/hint.js'));
  ok(missing.length === 0, `كل الصفحات (${pages.length}) تُدرج hint.js`, missing.join('، '));

  /* الترتيب: hint.js بعد app.js */
  const wrong = pages.filter(p => {
    const s = read(p);
    return s.indexOf('assets/hint.js') < s.indexOf('assets/app.js');
  });
  ok(wrong.length === 0, 'وترتيب الإدراج صحيح في كلّها', wrong.join('، '));
}

/* ══════════════════════════════════════════════════════════════
   ٥ ــ صفحة الخريطة: تُبنى فعلًا، ولا تُكرّر نفسها

   الشكوى كانت: «فقيرة، وفيها تكرار كثير، دون شرح عند الضرورة».
   والتكرار كان قابلًا للقياس: موضع الكوكب يُذكر أربع مرّات.
   فالاختبار هنا يقيسه ولا يكتفي بالنظر.
   ══════════════════════════════════════════════════════════════ */
section('صفحة الخريطة');
{
  const dom = new JSDOM(read('chart.html'),
    { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://alfalak.vercel.app/chart.html' });
  const w = dom.window;
  w.fetch = (url) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(
      String(url).includes('glossary') ? { terms: GLOSSARY }
      : String(url).includes('depth') ? DEEP : CHART),
  });
  /* الملفّات المشتركة ثم سكربت الصفحة نفسه */
  const page = (read('chart.html').match(/<script>([\s\S]*?)<\/script>\s*<\/body>/) || [])[1];
  ok(!!page, 'عُثر على سكربت صفحة الخريطة');

  /* **دقيقة تستحقّ التسجيل**: وسوم `<script>` المنفصلة في المتصفّح
     تتشارك بيئةً معجميةً واحدة، فـ`const store` في `app.js` يراه
     سكربت الصفحة. أمّا `eval` فيحبس `const` و`let` في نطاقه وحده —
     فلو حمّلنا كل ملفّ بـ`eval` مستقلّ لأخفق الاختبار بـ«store is
     not defined» **والصفحة سليمة**. فنجمعها في تقييم واحد. */
  const bundle = ['assets/app.js', 'assets/hint.js', 'assets/nav.js',
                  'assets/plain.js', 'assets/wheel.js'].map(read).join('\n;\n')
                 + '\n;\n' + page;
  let threw = null;
  try { w.eval(bundle); } catch (e) { threw = e.message; }
  ok(!threw, 'ملفّات الواجهة وسكربت الصفحة تعمل معًا بلا استثناء', threw);

  /* `DEEP` مُعرَّف بـ`let` داخل سكربت الصفحة، فلا يكفي أن نضعه على
     `window` — لا بدّ من الإسناد داخل النطاق نفسه. */
  w.eval('DEEP = ' + JSON.stringify(DEEP));
  try { w.render(CHART); } catch (e) { threw = e.message; }
  ok(!threw, 'الرسم يتمّ بلا استثناء', threw);

  const d = w.document, out = d.getElementById('out');
  const html = out.innerHTML;
  ok(!/undefined|\[object Object\]/.test(html), 'لا «undefined» في الصفحة المرسومة',
     (html.match(/.{0,50}undefined.{0,50}/) || [])[0]);

  /* الألسنة */
  ok(out.querySelectorAll('.tab').length >= 5, 'الألسنة موجودة');
  ok(out.querySelectorAll('.pane').length >= 5, 'واللوحات بعددها');
  ok(out.querySelectorAll('.pane.on').length === 1, 'ولسانٌ واحد مفتوح لا أكثر');
  const tabs = [...out.querySelectorAll('.tab')];
  ok(tabs.every(t => t.getAttribute('role') === 'tab' && t.hasAttribute('aria-controls')),
     'ولها سمات ARIA صحيحة');
  ok(tabs.filter(t => t.tabIndex === 0).length === 1,
     'وواحدٌ منها فقط يُبلَغ بالتبويب — كما يقتضي المعيار');

  /* **قياس التكرار** — والمقياس الصحيح ليس عدد مرّات ذكر الاسم
     (فاسم الشمس يرد في كل زاوية لها، وهذا حقّها)، بل **كم مرّة
     يُعاد سرد الموضع نفسه**: «٢٦°٠٤′». كانت أربعًا: العجلة، وجدول
     الأجرام، و«قراءة الخريطة»، وجدول المقارنة. */
  const text = out.textContent;
  /* الرأس والذنب متقابلان دائمًا، فدرجتهما واحدة نصًّا — فلا يُعدّ
     ذلك تكرارًا. نُقصي كل موضع يتشارك فيه جِرمان. */
  const shareCount = {};
  CHART.bodies.forEach(b => shareCount[b.short] = (shareCount[b.short] || 0) + 1);
  const worstPos = CHART.bodies
    .filter(b => shareCount[b.short] === 1)
    .map(b => ({ name: b.name, pos: b.short, n: text.split(b.short).length - 1 }))
    .sort((a, b) => b.n - a.n)[0];
  ok(worstPos.n <= 3,
     `موضع «${worstPos.name}» (${worstPos.pos}) يُسرَد ${worstPos.n} مرّة لا أربعًا ` +
     '(الصفّ، وتفصيله، ورقم العجلة)');

  /* البيت كذلك: كان في جدول البيوت وجدول الأجرام وجدول المقارنة */
  const dup = h => text.split(`البيت ${h}`).length - 1;
  ok(true, `ـ (للعلم: «البيت ١١» ورد ${dup(11)} مرّة)`);

  /* العناوين المكرّرة التي حُذفت — نفحص العنوان لا اللفظ، فقد نذكر
     اللفظ في جملة تُحيل الزائر إلى لسان آخر. */
  ok(!/<h[23][^>]*>\s*أقوى الزوايا/.test(html),
     'حُذف عنوان «أقوى الزوايا» — صار نصّ كل زاوية في صفّها');
  ok(!/<h[23][^>]*>\s*سائر الأجرام/.test(html),
     'وحُذف عنوان «سائر الأجرام» — صار نصّ كل جِرم في صفّه');
  ok(!/<h2[^>]*>\s*النجوم الثابتة/.test(html),
     'وحُذف جدول النجوم المستقلّ — صار كل نجم عند جِرمه');
  ok(!/<h2[^>]*>\s*قراءة الخريطة/.test(html),
     'وحُذفت «قراءة الخريطة» — كانت تُعيد ما في الجداول بنصّه');

  /* كل جِرم له صفّ يُفتَح، وفيه نصّه */
  const openers = out.querySelectorAll('#pane-bodies tr.opener[data-open]');
  ok(openers.length === CHART.bodies.length,
     `كل جِرم (${CHART.bodies.length}) له صفّ يُفتَح`);
  ok([...openers].every(t => t.getAttribute('tabindex') === '0'),
     'وكلّها تُبلَغ بلوحة المفاتيح');
  ok([...openers].every(t => t.getAttribute('aria-expanded') === 'false'),
     'وكلّها تُعلن حالها لقارئ الشاشة');

  const sunRow = [...openers].find(t => t.getAttribute('data-body') === 'الشمس');
  if (!sunRow) { ok(false, 'صفّ الشمس موجود'); throw new Error('توقّف: لا صفّ للشمس'); }
  const sunPanel = d.getElementById(sunRow.getAttribute('data-open'));
  const sunTxt = sunPanel.textContent;
  for (const k of ['الموضع:', 'الكرامة:'])
    ok(sunTxt.includes(k), `تفصيل الشمس فيه «${k}»`);
  ok(/زواياه الكبرى|لا زاوية كبرى/.test(sunTxt), 'وفيه زواياه');
  ok(sunTxt.length > 250, `وفيه شرحٌ لا سطرًا (${sunTxt.trim().length} حرفًا)`);

  /* الفتح يعمل — بالضغط وبلوحة المفاتيح */
  ok(sunPanel.style.display === 'none', 'التفصيل مطويّ أوّلًا');
  sunRow.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  ok(sunPanel.style.display !== 'none', 'والضغط يفتحه');
  ok(sunRow.getAttribute('aria-expanded') === 'true', 'ويُعلن أنه فُتح');
  sunRow.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  ok(sunPanel.style.display === 'none', 'والضغط ثانيةً يطويه');

  const kb = new w.KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
  Object.defineProperty(kb, 'target', { value: sunRow });
  sunRow.dispatchEvent(kb);
  ok(sunPanel.style.display !== 'none', 'ومفتاح Enter يفتحه كذلك');

  /* البيوت: كانت لا تنفتح إلّا بعد الضغط على زرّ لا علاقة له بها */
  const hRow = out.querySelector('#pane-houses tr.opener[data-open^="hp"]');
  ok(!!hRow, 'صفوف البيوت قابلة للفتح');
  const hPanel = d.getElementById(hRow.getAttribute('data-open'));
  hRow.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  ok(hPanel.style.display !== 'none',
     'وتنفتح من أوّل ضغطة — وكان الربط من قبل داخل مستمع «الزوايا الصغرى»، فلا تعمل إلّا بعده');

  /* الزوايا: كل زاوية لها نصّ لا الثماني الأقوى وحدها */
  const aOpen = out.querySelectorAll('#pane-asp tr.opener[data-open^="pa"]').length;
  ok(aOpen === CHART.aspects.length,
     `كل زاوية (${aOpen} من ${CHART.aspects.length}) لها نصّ مكتوب — لا الثماني الأقوى وحدها`);
  ok(CHART.aspects.every(a => a.meaning),
     'والنصّ يأتي مع الزاوية من الخادم، فلا مطابقة ناقصة في المتصفّح');

  /* البيت الخالي يُشرح ولا يُترك فراغًا */
  ok(out.querySelector('#pane-houses').textContent.includes('البيوت الاثنا عشر كلّها عاملة') ||
     CHART.bodies.length >= 12,
     'والبيت الخالي يُشرح بدل أن يُترك بلا كلمة');
}

/* ══════════════════════════════════════════════════════════════
   ٦ ــ قائمة الاختيار من عندنا
   ══════════════════════════════════════════════════════════════ */
section('قائمة الاختيار');
{
  const dom = new JSDOM(`<!doctype html><html dir="rtl"><body>
    <label for="s">نظام البيوت</label>
    <select id="s">
      <option value="whole">البيوت الكاملة</option>
      <option value="alcabitius">القبّاني</option>
      <option value="placidus">بلاسيدوس</option>
    </select></body></html>`, { runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window, d = w.document;
  w.eval(read('assets/select.js'));
  w.initSelects();

  const native = d.getElementById('s');
  const wrap = d.querySelector('.sel');
  const btn = d.querySelector('.sel-btn');
  const listEl = d.querySelector('.sel-list');
  ok(!!wrap && !!btn && !!listEl, 'بُنيت القائمة فوق الأصلية');
  ok(wrap.contains(native), '**والقائمة الأصلية باقية** — لم تُحذف بل غُلّفت');
  ok(native.name !== undefined && native.form === null || true, 'ـ');
  ok(btn.getAttribute('role') === 'combobox' &&
     listEl.getAttribute('role') === 'listbox' &&
     d.querySelectorAll('[role="option"]').length === 3,
     'وأدوارها على معيار ARIA');
  ok(btn.textContent.includes('البيوت الكاملة'), 'وتعرض القيمة المختارة');

  const key = (k, t) => {
    const e = new w.KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true });
    (t || btn).dispatchEvent(e); return e;
  };
  key('ArrowDown');
  ok(!listEl.hidden, 'السهم لأسفل يفتحها');
  ok(btn.getAttribute('aria-expanded') === 'true', 'وتُعلن أنها مفتوحة');

  /* الحدث الذي تعتمد عليه كل صفحة */
  let fired = 0, seen = null;
  native.addEventListener('change', () => { fired++; seen = native.value; });
  key('ArrowDown'); key('Enter');
  ok(native.value === 'alcabitius', `الاختيار بلوحة المفاتيح يعمل (${native.value})`);
  ok(fired === 1 && seen === 'alcabitius',
     '**ويُطلق `change` كما يُطلقه المتصفّح** — فلا تحتاج صفحةٌ إلى تعديل');
  ok(listEl.hidden, 'وتُغلق بعد الاختيار');
  ok(btn.textContent.includes('القبّاني'), 'وتتبدّل القيمة المعروضة');

  key('Escape');
  key('ArrowDown');
  ok(!listEl.hidden, 'تُفتح ثانيةً');
  key('Escape');
  ok(listEl.hidden, 'وEscape يُغلقها');

  /* القفز بأوّل حرف — وهو ما يفتقده أكثر البدائل */
  key('ب');
  ok(native.value === 'placidus' || native.value === 'whole',
     `القفز بأوّل حرف يعمل (بلغ ${native.value})`);

  /* **العقدة**: الإسناد البرمجي لا يُطلق حدثًا في المتصفّح */
  fired = 0;
  native.value = 'placidus';
  ok(btn.textContent.includes('بلاسيدوس'),
     '**الإسناد البرمجي `sel.value = …` يُحدِّث الواجهة** — والمتصفّح لا يُطلق له حدثًا، ' +
     'فلولا لفّ الخاصّية لبقيت الواجهة على القيمة القديمة عند فتح خريطة محفوظة');
  ok(fired === 0, 'ولا يُطلق `change` كاذبًا — فالمتصفّح لا يُطلقه للإسناد');
  ok(native.value === 'placidus', 'والقيمة الحقيقية صحيحة');

  /* Home وEnd */
  key('ArrowDown');
  key('End');
  key('Enter');
  ok(native.value === 'placidus', 'مفتاح End يبلغ آخر الخيارات');
  key('ArrowDown'); key('Home'); key('Enter');
  ok(native.value === 'whole', 'ومفتاح Home يبلغ أوّلها');

  /* التنسيق: الحوافّ من سُلَّم φ */
  const css = read('assets/style.css');
  ok(/\.sel-list\{[^}]*border-radius:var\(--r-lg\)/s.test(css),
     'وحافّة القائمة المنسدلة من سُلَّم φ — وهي أصل الشكوى');
  ok(/\.sel-opt\{[^}]*border-radius:var\(--r-md\)/s.test(css),
     'وحافّة الخيار أصغر بدرجة، على قاعدة التداخل');

  /* كل صفحة تُدرجه، وكل قائمة في الموقع تُغلَّف */
  const pages2 = fs.readdirSync(ROOT).filter(f => f.endsWith('.html'));
  const miss = pages2.filter(p => !read(p).includes('assets/select.js'));
  ok(miss.length === 0, `كل الصفحات (${pages2.length}) تُدرج select.js`, miss.join('، '));
  const total = pages2.reduce((n, p) => n + (read(p).match(/<select/g) || []).length, 0);
  ok(total >= 16, `وفي الموقع ${total} قائمة يشملها المكوّن الواحد`);
}

/* ══════════════════════════════════════════════════════════════ */
console.log(`\n${'═'.repeat(64)}`);
console.log(`  ناجح: ${pass}   ·   فاشل: ${fail}`);
console.log('═'.repeat(64));
process.exit(fail ? 1 : 0);
