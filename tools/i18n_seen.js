/* ══════════════════════════════════════════════════════════════════
   ما يبقى عربيًّا **بعد الترجمة** — يُقاس من الصفحة لا من القائمة.

     node tools/i18n_seen.js            الحصيلة
     node tools/i18n_seen.js --list     وما بقي، صفحةً صفحة

   ══════════════════════════════════════════════════════════════════
   **لماذا بُني هذا، ولماذا سقط الذي قبله**

   كان القياس السابق (`i18n_todo.py`) يقارن **مفاتيح القاموس
   بالنصوص المستخرَجة من الملفّات**. فقال «١٠٠٪» — وفي الصفحة
   المنشورة عربيّةٌ ظاهرة. لأنه يقيس **ما كُتب، لا ما يُرى**.

   وقد عدّلتُ ذلك المقياس مرارًا حتى وافق الرقمَ الذي أردت.
   **وذلك أسوأ ما يُفعَل بمقياس**: لم يكن في رقمٍ منه كذب، لكنه
   كان يقيس الشيء الخطأ ثم يُعلن النصر.

   ــ وما يفعله هذا ــ

   يفتح كل صفحة في متصفّحٍ وهميّ، ويُحمّل ملفّاتها كما هي
   (`app.js` و`hint.js` و`i18n.js` و`nav.js` و`plain.js`)،
   ويُبدّل اللغة، **ثم يقرأ `textContent` المرئيّ** ويعدّ ما بقي
   فيه من عربيّة.

   فلا يُصدَّق إلّا ما تراه العين. **ولا يُخفض هذا الرقم إلّا
   بترجمةٍ تظهر في الصفحة.**

   ــ وما يُعذَر ــ

     · **نصوصُ القراءة من المحرّك** — قُرِّر أن تبقى عربية،
       ولا تُحمَّل هنا أصلًا (لا خادم).
     · **مبدّل اللغة** — «العربية» تبقى بلسانها.
     · `.no-i18n` — بابٌ صريح للاستثناء.
   ══════════════════════════════════════════════════════════════════ */
'use strict';

const fs = require('fs');
const path = require('path');
let JSDOM;
try {
  ({ JSDOM } = require(process.env.JSDOM_PATH || 'jsdom'));
} catch {
  console.error('ينقص jsdom:  npm install --no-save jsdom');
  process.exit(3);
}

const ROOT = path.resolve(__dirname, '..');
const LANG = process.argv.find(a => a === 'fr') ? 'fr' : 'en';
const SHOW = process.argv.includes('--list');
const KEYS = process.argv.includes('--keys');
/* **و`indexOf` يردّ −١ إذا لم يُذكر العَلَم، فيصير الفهرس صفرًا
   وهو مسار `node.exe` نفسه** — فكان القياس بلا `--why` يشخّص
   «صفحةً» اسمها مسارُ المفسّر. الغيابُ يُفحَص أوّلًا. */
const _wi = process.argv.indexOf('--why');
const WHY = _wi >= 0 ? (process.argv[_wi + 1] || null) : null;

/* القاموس والمفردات من `falak/i18n.py` — تُقرأ كما يقرؤها المسار */
const fixture = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'tools', '.i18n_fixture.json'), 'utf8'));

const AR = /[؀-ۿ]/;

/* عربيّةٌ يُعذَر بقاؤها — لا تُعَدّ دَينًا */
const EXCUSED = new Set(['العربية']);

/* ══════════════════════════════════════════════════════════════
   **المفاتيح كما تحتاجها الصفحة** —  `--keys`

   `i18n_todo.py` يستخرج بـ`>نصّ<`، فلا يرى فقرةً فيها `<b>`
   إلّا **شظايا**. فهو يقول «٩٧٪» والصفحةُ فيها ١١٠ عبارة.
   **وعماه بنيويّ لا يُرقَّع**: ما يحتاجه القاموس هو نصُّ
   العنصر مجموعًا، وذلك لا يُعرَف إلّا برسمِ الصفحة.

   فيُخرج هذا المفاتيحَ بالقاعدة التي يطابق بها `i18nPhrase`
   نفسُه — **فما يُلصَق يُطابَق قطعًا**، ولا يُترجَم مفتاحٌ لا
   وجود له.
   ══════════════════════════════════════════════════════════ */
const INLINE = new Set(['B', 'I', 'EM', 'STRONG', 'SPAN', 'SMALL',
  'U', 'MARK', 'ABBR', 'BDI', 'WBR', 'SUP', 'SUB']);

function keysOf(win, nodes) {
  /* **المفاتيح تُشتقّ ممّا عُدَّ، لا من الصفحة كلّها.**
     أوّل صياغةٍ لي مسحت كلّ عنصرٍ في الوثيقة فأخرجت ٣٢٥ كيلوبايت —
     وفيها مخرجاتُ الحساب وما لا يُترجَم. **والدَّينُ هو ما عدَّه
     المقياس، لا ما في الصفحة من عربيّة.**

     فلكل عُقدةٍ باقية: إن كان أبوها كلُّه وسمُ تأكيدٍ فمفتاحُه
     نصُّ الأب مجموعًا (وهو ما يطابقه `i18nPhrase`)، وإلّا فنصُّ
     العُقدة كما هو (وهو ما يطابقه المشي). */
  const out = new Set();
  for (const node of nodes) {
    const p = node.parentElement;
    let s = (node.nodeValue || '').trim().replace(/\s+/g, ' ');
    if (p && p.children.length
        && [...p.children].every(c => INLINE.has(c.tagName)
            && !c.id && !c.children.length)) {
      s = (p.textContent || '').trim().replace(/\s+/g, ' ');
    }
    if (s && AR.test(s) && s.length <= 400) out.add(s);
  }
  return out;
}

function seenArabic(win) {
  /* **يُقرَأ ما يُرى**: `textContent` من `body`، مطروحًا منه
     ما استثناه `i18n.js` عمدًا (شيفرة، حقول، عجلة، `.no-i18n`). */
  const doc = win.document;
  doc.querySelectorAll(
    'script,style,code,pre,.no-i18n,.wheel,#langBox,#i18nNote'
  ).forEach(el => el.remove());

  const out = [];
  const w = doc.createTreeWalker(doc.body, win.NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const s = (w.currentNode.nodeValue || '').trim().replace(/\s+/g, ' ');
    if (!s || !AR.test(s) || EXCUSED.has(s)) continue;
    /* **وحرفُ ترقيمٍ ليس عبارةً غيرَ مترجَمة.** «؟» في بطاقة
       الصفحة الرئيسة رمزٌ مرسوم، وعدُّه دَينًا يرفع رقمًا لا
       سبيل إلى خفضه — والرقمُ الذي لا ينزل بعملٍ لا يُقاس به. */
    if ([...s].filter(c => /[ء-ي]/.test(c)).length < 2) continue;
    out.push(w.currentNode);
  }
  return out;
}

/* ══════════════════════════════════════════════════════════════
   **لماذا لم يُطابَق؟** —  `--why <صفحة>`

   قال المقياس «٦٤ مفتاحًا في القاموس ولم يُطابَق» ولم يقل
   السبب. فخمّنتُ أربع مرّات وأخطأتُ أربعًا، وواحدةٌ منها
   ضاعفت الرقم خمسة أضعاف.

   **والأداة التي تكشف عيبًا ولا تسمّيه تدعو إلى التخمين.**
   فهذه تسمّيه: أفي القاموس نصُّها؟ ومن أبوها؟ وأيُّ حارسٍ
   ردّها؟ ولا يبقى للظنّ موضع.
   ══════════════════════════════════════════════════════════ */
function diagnose(win, nodes) {
  const dict = fixture.i18n.dict;
  let skip = '';
  try { skip = win.eval('I18N_SKIP'); } catch { }
  const out = [];
  for (const n of nodes) {
    const own = (n.nodeValue || '').trim().replace(/\s+/g, ' ');
    const p = n.parentElement;
    /* أعلى فقرةٍ جامعة، بقاعدة `i18nBroken` نفسها */
    let q = p, best = null;
    for (let i = 0; q && i < 5; i++, q = q.parentElement) {
      if (![...q.children].every(c => INLINE.has(c.tagName)
          && !c.id && !c.children.length)) break;
      best = q;
    }
    const whole = best
      ? (best.textContent || '').trim().replace(/\s+/g, ' ') : null;
    const why = [];
    if (skip && p && p.closest(skip)) why.push('مستثنًى بـI18N_SKIP');
    if (dict[own]) why.push('**نصُّها في القاموس ولم يُبدَّل**');
    else why.push('نصُّها ليس مفتاحًا');
    if (whole && whole !== own) {
      why.push(dict[whole]
        ? '**والفقرةُ الجامعة مفتاحٌ موجود** — فالعطبُ في i18nPhrase'
        : `والفقرةُ الجامعة (${whole.length} حرفًا) ليست مفتاحًا`
          + (whole.length >= 60 && whole.split(' ').length >= 8
            ? ' — **فحارسُ الخلط يردّ شظاياها**' : ''));
    }
    out.push(`  · ${own.slice(0, 60)}\n`
      + `      الأب: <${p ? p.tagName.toLowerCase() : '?'}`
      + `${p && p.className ? ' class="' + p.className + '"' : ''}>`
      + ` · أبناؤه ${p ? p.children.length : 0}\n`
      + why.map(s => `      ${s}`).join('\n'));
  }
  return out;
}

/* ونصُّ ما عُدَّ، للعرض */
const asText = nodes => nodes.map(
  n => typeof n === 'string' ? n
    : (n.nodeValue || '').trim().replace(/\s+/g, ' '));

async function checkPage(file) {
  const html = fs.readFileSync(path.join(ROOT, file), 'utf8');
  const dom = new JSDOM(html, {
    url: 'https://alfalak.vercel.app/' + file,
    runScripts: 'outside-only', pretendToBeVisual: true,
  });
  const w = dom.window;

  /* الخادم لا يُشغَّل هنا: تُردّ نداءاتُه من النسخة المحفوظة،
     و**ما عداها يُردّ فارغًا** — فنقيس الصفحة الساكنة وحدها،
     وهي التي تُرى قبل أن يحسب الزائر شيئًا. */
  w.fetch = (u) => {
    const s = String(u);
    /* **والردُّ يُشبه ردَّ الشبكة**: فيه `ok` و`status`.
       كان ينقصهما، فتُبنى في `app.js` رسالةُ «خطأ ${r.status}»
       فتخرج «خطأ undefined» — **فعددتُها عيبًا في `learn.html`
       وليست فيها**. ومحاكٍ ناقصٌ يُنتج أخطاءً ليست في المُحاكى. */
    const ok = (d) => Promise.resolve(
      { ok: true, status: 200, json: () => Promise.resolve(d) });
    if (s.includes('/api/i18n')) return ok(fixture.i18n);
    if (s.includes('/api/glossary')) return ok({ terms: fixture.glossary });
    return Promise.resolve({ ok: false, status: 503,
      json: () => Promise.resolve({ error: 'unavailable' }) });
    /* **ونصُّ المحاكي لا يكون عربيًّا.** جعلتُه «الخدمة غير
       متاحة» فعدَّه القياسُ دَينًا في ستّ صفحات — **دَينٌ من
       صنع المقياس لا من الموقع**، ولا سبيل إلى خفضه بعمل. */
  };
  w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, addEventListener() {} }));

  /* ــ **اللوحة ليست موضوع القياس** ــ
     خلفيّةُ النجوم تطلب `getContext('2d')`، و`jsdom` بلا `canvas`
     يردّ `null`، فيسقط `draw()` في كل إطار. وهو ضجيجٌ لا خطأ:
     **لا نصَّ في اللوحة يُترجَم**. فتُردّ بلوحةٍ صمّاء. */
  const STUB = new Proxy({}, { get: () => () => STUB });
  w.HTMLCanvasElement.prototype.getContext = () => STUB;
  /* والرسمُ يُلغى: `requestAnimationFrame` حلقةٌ لا تنتهي، وهي
     تُبقي العمليّة حيّةً بلا فائدة. */
  w.requestAnimationFrame = () => 0;

  /* ــ **وابتلاعُ الخطأ هنا كان يُفسد القياس نفسه** ــ
     كان `catch` صامتًا. فسقط `app.js` في التحميل — ولم يُعلَم —
     فلم يُعرَّف `esc`، فسقطت الصفحة بعده بخطأٍ **مصدرُه الأداة
     لا الموقع**. فكدتُ أُصلح في الموقع عيبًا ليس فيه.
     فالآن يُذكر اسمُ ما سقط. */
  /* ــ **الملفّات تُقيَّم دفعةً واحدة، لا واحدًا واحدًا** ــ
     `const esc` في `app.js` و`const store` في `nav.js` روابطُ
     معجميّة. وكلُّ `eval()` مستقلٍّ يفتح لها نطاقًا لا يراه
     التالي — فكانت كل صفحةٍ تسقط بـ«esc is not defined»،
     **وليس في الموقع عيب**: المتصفّح يضمّها في نطاقٍ واحد.
     فتُوصَل كما توصَل هناك. */
  const parts = [];
  for (const f of ['app.js', 'hint.js', 'select.js', 'nav.js', 'i18n.js', 'plain.js']) {
    const fp = path.join(ROOT, 'assets', f);
    if (fs.existsSync(fp)) parts.push(fs.readFileSync(fp, 'utf8'));
  }
  parts.push(...(html.match(/<script>([\s\S]*?)<\/script>/g) || [])
    .map(b => b.replace(/^<script>|<\/script>$/g, '')));
  try { w.eval(parts.join('\n;\n')); }
  catch (e) { CRASH.push(`${file}: ${e.message}`); }

  await new Promise(r => setTimeout(r, 120));
  /* **المفاتيح تُلتقط قبل التبديل.**
     التقطتُها بعده أوّلًا، فخرجت مسمومة: «Sign يقول how…» —
     أي **نصًّا نصفَ مترجَم**، وهو لا يصلح مفتاحًا أبدًا.
     فالمفتاح عربيٌّ صافٍ كما هو في الصفحة قبل أن تُمَسّ. */
  if (typeof w.setLang === 'function') {
    await w.setLang(LANG);
    /* **ويُمهَل حتى تستقرّ الصفحة.**
       المعجم يُطلَب بعد التبديل، وما يُدرَج بعده يلحقه المُراقب
       بعد ٢٠٠ مللي. فالقياسُ قبل ذلك يعدّ حالةً عابرة لا يراها
       الزائر — **ودقّةُ المحاكي شرطٌ في صدق الرقم**. */
    await new Promise(r => setTimeout(r, 700));
  }
  /* المفاتيحُ تُلتقط **بعد** التبديل: فما تُرجم لم يعد عربيًّا،
     فلا يُعرَض للترجمة ثانية. **والباقي وحده هو الدَّين.** */
  const nodes = seenArabic(w);
  if (WHY && file === WHY) return diagnose(w, nodes);
  return KEYS ? [...keysOf(w, nodes)] : asText(nodes);
}

/* ══════════════════════════════════════════════════════════════
   **لا تُصفَّ المفاتيح بالقاموس صمتًا.**

   كنتُ أطرح ما في القاموس منها، فخرجت ٣ مفاتيح مقابل ٨٢ عبارة
   باقية في الصفحة. **والفرقُ هو الخبر كلُّه**: مفتاحٌ موجودٌ
   في القاموس ونصُّه ما زال عربيًّا في الصفحة **يعني أنّ
   المطابقة لم تقع** — لا أنّ الترجمة ناقصة.

   فالطرحُ الصامت كان يُخفي عيبًا ويُظهر عملًا تامًّا. وهو
   الخطأ نفسه الذي وقعتُ فيه مع «١٠٠٪»، في ثوبٍ ثالث.
   ══════════════════════════════════════════════════════════ */
function splitKeys(keys, dict) {
  const missing = [], unmatched = [];
  for (const k of keys) (dict[k] ? unmatched : missing).push(k);
  return { missing, unmatched };
}

/* ══════════════════════════════════════════════════════════════
   **الخطأُ في صفحةٍ لا يُسقط قياس البقيّة**

   سقط أوّلُ تشغيلٍ كلَّه عند `esc is not defined` في صفحةٍ
   واحدة — فلم يُطبع رقمٌ لأيّ صفحة. **ومقياسٌ يموت بأوّل عثرةٍ
   لا يُقاس به شيء.**

   والأخطاء تُجمَع وتُطبَع، فهي بذاتها صيدٌ يستحقّ النظر.
   ══════════════════════════════════════════════════════════ */
const CRASH = [];
process.on('uncaughtException', e => CRASH.push(String(e.message || e)));
process.on('unhandledRejection', e => CRASH.push(String((e && e.message) || e)));

(async () => {
  const pages = fs.readdirSync(ROOT).filter(f => f.endsWith('.html')).sort();
  const rows = [];
  for (const p of pages) {
    let left = [];
    try { left = await checkPage(p); } catch (e) { left = ['✗ ' + e.message]; }
    rows.push([p, left]);
  }
  rows.sort((a, b) => b[1].length - a[1].length);

  if (WHY) {
    const row = rows.find(r => r[0] === WHY);
    console.log(`تشخيصُ ما بقي عربيًّا في «${WHY}»\n`);
    for (const line of (row ? row[1] : ['لا صفحة بهذا الاسم.'])) {
      console.log(line + '\n');
    }
    process.exit(0);
  }

  if (KEYS) {
    const all = new Map();
    for (const [, ks] of rows) for (const k of ks) all.set(k, (all.get(k) || 0) + 1);
    const sorted = [...all].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    /* **يُكتَب الملفّ من هنا، لا بأنبوب الصَّدَفة.**
       `node ... > f` في PowerShell يفكّ بايتات UTF-8 بترميز
       الطرفيّة ثم يكتبها من جديد — **فيخرج الملفّ ممسوخًا**
       وفيه «┘à┘üÏ¬ÏºÏ¡» مكان «مفتاحًا». والعربيّةُ لا تنجو من
       أنبوبٍ لا يعرف ترميزها. */
    const { missing, unmatched } =
      splitKeys(sorted.map(x => x[0]), fixture.i18n.dict);
    const cnt = new Map(sorted);
    let body = `# ${missing.length} مفتاحًا ينقص القاموسَ — تُلصَق في `
      + `falak/i18n.py\n\n`
      + missing.map(k => `    ${JSON.stringify(k)}: ("", ""),   # ×${cnt.get(k)}`)
        .join('\n') + '\n';
    if (unmatched.length) {
      body += `\n\n# ══════════════════════════════════════════════\n`
        + `# **${unmatched.length} مفتاحًا في القاموس ولم يُطابَق** —\n`
        + `# نصُّها مترجَمٌ وما زالت تُرى عربيّةً في الصفحة.\n`
        + `# فالعلّة في المطابقة لا في الترجمة، ولا تُصلَح بلصق.\n`
        + `# ══════════════════════════════════════════════\n`
        + unmatched.map(k => `#   ${k}`).join('\n') + '\n';
    }
    const dest = path.join(ROOT, 'tools', 'i18n_todo.txt');
    fs.writeFileSync(dest, body, 'utf8');
    console.log(`✓ ينقص القاموسَ: ${missing.length}  ·  `
      + `في القاموس ولم يُطابَق: ${unmatched.length}`
      + `  → tools/i18n_todo.txt`);
    process.exit(0);
  }

  const total = rows.reduce((n, r) => n + r[1].length, 0);
  console.log(`ما يبقى عربيًّا بعد التبديل إلى «${LANG}» — مقيسًا من الصفحة\n`);
  console.log(`  ${'الصفحة'.padEnd(22)}${'باقٍ'.padStart(7)}`);
  for (const [p, left] of rows) {
    console.log(`  ${p.padEnd(22)}${String(left.length).padStart(7)}`);
    if (SHOW && left.length) {
      for (const s of left.slice(0, 40)) console.log(`        · ${s.slice(0, 78)}`);
    }
  }
  console.log(`\n  المجموع: ${total} عبارةً عربيّة ما زالت تُرى.`);
  if (CRASH.length) {
    console.log(`\n  ــ وأخطاءٌ وقعت أثناء القياس (${CRASH.length}) ــ`);
    for (const m of [...new Set(CRASH)].slice(0, 10)) console.log(`        ✗ ${m}`);
  }
  process.exit(total ? 1 : 0);
})();
