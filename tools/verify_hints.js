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
const { JSDOM } = require(process.env.JSDOM_PATH || 'jsdom');

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

/* ══════════════════════════════════════════════════════════════ */
console.log(`\n${'═'.repeat(64)}`);
console.log(`  ناجح: ${pass}   ·   فاشل: ${fail}`);
console.log('═'.repeat(64));
process.exit(fail ? 1 : 0);
