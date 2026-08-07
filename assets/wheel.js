/* رسم الخريطة الدائرية — SVG خالص بلا مكتبات */

const SIGN_SYMBOLS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
const SIGN_NAMES = ['الحمل','الثور','الجوزاء','السرطان','الأسد','العذراء',
                    'الميزان','العقرب','القوس','الجدي','الدلو','الحوت'];
/* ── لوحة العناصر ──────────────────────────────────────────────
   المفتاح `i % 4` والبروج مرتّبة: حمل(نار) ثور(تراب) جوزاء(هواء)
   سرطان(ماء) — فالدورة رباعية منتظمة. والألوان اختيرت متباعدةً
   في درجة اللون لا في الإضاءة وحدها، فتُقرأ على الخلفية الداكنة
   ويُميّزها عمى الألوان الشائع (الأحمر–الأخضر) بالإضاءة. */
const ELEM_COLOR = { 0:'#e8836f', 1:'#d4a537', 2:'#7fa8e8', 3:'#4fc7a6' };
const ELEM_NAME  = { 0:'ناري', 1:'ترابي', 2:'هوائي', 3:'مائي' };
const ASPECT_COLOR = { 'إيجابية':'#5fc7a1', 'سلبية':'#e08a7d', 'محايدة':'#d9b45b' };

/* ══════════════════════════════════════════════════════════════
   الشرح عند التحويم على عناصر العجلة

   كانت العجلة تحمل `<title>` وحدها، وهو ضعيف: يتأخّر نحو ثانية،
   ولا يقبل تنسيقًا، ولا يظهر بالتركيز بلوحة المفاتيح، ولا يُقرأ
   على الجوّال البتّة. فصرنا نضع `data-hint` ويتولّاه `hint.js`.

   وأبقينا `<title>` معه — فهو ما تقرأه قارئات الشاشة، وما يبقى
   إن تعطّل السكربت.
   ══════════════════════════════════════════════════════════════ */
const wEsc = t => String(t == null ? '' : t)
  .replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

/* ══════════════════════════════════════════════════════════════
   رموز البروج تُرسَم صُوَرًا ملوّنة — ولماذا

   حروف البروج ♈ إلى ♓ (U+2648–U+2653) مُعرَّفة في معيار يونيكود
   بأن **صورتها الافتراضية صورةُ إيموجي**. فالمتصفّح يُسلّمها إلى
   خطّ الإيموجي فيرسمها مربّعاتٍ بنفسجية مستديرة — وهو ما ظهر في
   الموقع الحيّ، ولم أرَه في أداة التحويل عندي لأنها لا تملك خطّ
   إيموجي أصلًا فرسمتها حروفًا.

   والعلاج معياريّ: يُلحَق بالحرف **U+FE0E** (مُحدِّد الصورة
   النصّية)، فيُلزَم المتصفّح بصورة الحرف لا صورة الإيموجي.
   ونُضيف معه خطوطًا تعرف هذه الحروف، فبعض الأنظمة تفتقدها.
   ══════════════════════════════════════════════════════════════ */
const VS15 = '︎';
const wSym = s => String(s == null ? '' : s).replace(/[☀-➿]/gu, m => m + VS15);

const WHEEL_FONT = '"Noto Kufi Arabic", "Segoe UI Symbol", ' +
                   '"Noto Sans Symbols 2", "Noto Sans Symbols", system-ui, sans-serif';

/* الأسطر تُفصَل بـ«|»، فنُسقط ما فيه منها كي لا يُكسَر التقسيم */
function hint(title, lines, extra) {
  const body = (lines || []).filter(Boolean)
    .map(s => String(s).replace(/\|/g, '·')).join('|');
  let a = ` data-hint="${wEsc(body)}" data-hint-title="${wEsc(title)}"`;
  if (extra) a += extra;
  return a;
}

const HOUSE_ORD = ['الأوّل','الثاني','الثالث','الرابع','الخامس','السادس',
                   'السابع','الثامن','التاسع','العاشر','الحادي عشر','الثاني عشر'];

/* «يسير درجةً في اليوم» أوضح لغير المختصّ من رقم عشري مجرّد */
function speedWord(b) {
  if (b.retro) return 'راجع — يبدو سائرًا إلى الوراء، ودلالته المراجعة لا التوقّف.';
  if (b.speed == null) return '';
  const v = Math.abs(b.speed);
  const rate = v >= 1 ? `${v.toFixed(2)}° في اليوم` : `${(v * 60).toFixed(0)}′ في اليوم`;
  return `يسير ${rate} مستقيمًا.`;
}

function wheelSVG(c, opts = {}) {
  const S = opts.size || 620;
  const cx = S / 2, cy = S / 2;
  const R = {
    zodiacOut: S * .470, zodiacIn: S * .400,
    mansionOut: S * .400, mansionIn: S * .372,
    houseOut: S * .372, houseIn: S * .290,
    planet: S * .335, aspect: S * .285,
  };
  /* ── أنصاف الأقطار على النسبة الذهبية ──────────────────────────
     الأنصاف القديمة كانت أرقامًا مُختارة بالعين، وفيها **خلل مرئي**:
     وسم «الطالع» يُرسَم على نصف قطر ٣٠٦٫٤ من مركزٍ عند ٣١٠، وهو
     نصّ مُتوسَّط العرض — فينقطع نصفه خارج اللوحة، فيُقرأ «SC» بدل
     «ASC» و«DS» بدل «DSC». (وقد رأيتُه في الصورة المصدَّرة.)

     فأُعيد بناؤها على φ = ١٫٦١٨:
       · القرص الداخلي = القطر الخارجي ÷ φ
       · وما بقي يُقسَم على الأحزمة الثلاثة بالنسب φ² : φ : ١
         (البيوت أعرضها، ثم البروج، ثم المنازل)
       · ودائرة الزوايا = القرص الداخلي ÷ φ
     فصار كل حدٍّ في الرسم نسبةً من الذي قبله لا رقمًا مُصادفًا. */
  const PHI = 1.6180339887;
  const OUT = S * 0.440;                 /* هامشٌ للأوسمة خارجه */
  const INNER = OUT / PHI;               /* القرص الداخلي */
  const band = OUT - INNER;
  const wHouse = band * (PHI * PHI) / (PHI * PHI + PHI + 1);
  const wZod   = band * PHI             / (PHI * PHI + PHI + 1);
  const wMans  = band                   / (PHI * PHI + PHI + 1);
  R.zodiacOut = OUT;
  R.zodiacIn  = OUT - wZod;
  R.mansionOut = R.zodiacIn;
  R.mansionIn  = R.zodiacIn - wMans;
  R.houseOut = R.mansionIn;
  R.houseIn  = INNER;
  R.planet = INNER - (INNER - INNER / PHI) * 0.34;   /* الأجرام داخل القرص */
  R.degLbl = R.planet - (INNER - INNER / PHI) * 0.42;
  R.aspect = INNER / PHI;                /* دائرة خطوط الزوايا */
  R.axisLbl = OUT + wZod * 0.62;         /* ووسم الوتد داخل اللوحة قطعًا */
  const asc = c.angles['الطالع'].lon;
  /* ── الطبقات ──────────────────────────────────────────────────
     العجلة تحمل خمس حلقات ونحو أربعين خطًّا. ومن أراد أن ينظر في
     الزوايا الكبرى وحدها لا ينبغي أن يُجبَر على النظر في الصغرى.
     فصار لكل طبقة مفتاح، كما في Astrodienst. */
  const L = opts.layers || {};
  const showMansions = L.mansions !== false && opts.mansions !== false;
  const showDeg = L.degrees !== false;
  const showLots = !!L.lots;

  /* الطالع إلى اليسار، والبروج تدور عكس عقارب الساعة */
  const ang = lon => (180 + (lon - asc)) * Math.PI / 180;
  const P = (lon, r) => [cx + r * Math.cos(ang(lon)), cy - r * Math.sin(ang(lon))];
  const line = (lon, r1, r2, attrs) => {
    const [x1,y1] = P(lon,r1), [x2,y2] = P(lon,r2);
    return `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" ${attrs}/>`;
  };
  const arcPath = (a, b, r) => {
    const [x1,y1] = P(a,r), [x2,y2] = P(b,r);
    const large = ((b - a + 360) % 360) > 180 ? 1 : 0;
    return `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 ${large} 0 ${x2.toFixed(1)} ${y2.toFixed(1)}`;
  };

  let g = '';

  /* ── حلقة البروج ── */
  g += `<circle cx="${cx}" cy="${cy}" r="${R.zodiacOut}" fill="none" stroke="var(--line2)" stroke-width="1"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="${R.zodiacIn}" fill="none" stroke="var(--line2)" stroke-width="1"/>`;
  const deep = opts.deep || {};
  for (let i = 0; i < 12; i++) {
    const start = i * 30;
    const nm = SIGN_NAMES[i];
    const sd = (deep.signs || {})[nm] || {};
    const inSign = c.bodies.filter(b => b.sign === nm).map(b => b.name);
    g += `<g class="sgn"${hint(`${nm} ${SIGN_SYMBOLS[i]}`, [
        sd.element || sd.mode ? `${sd.element || ''} · ${sd.mode || ''} · صاحبه ${sd.ruler || ''}` : '',
        sd.core,
        inSign.length ? `في هذا البرج من خريطتك: ${inSign.join('، ')}.`
                      : 'لا جِرم لك في هذا البرج.',
      ], ` data-term="البرج"`)}>`;
    /* الشفافية كانت ١٣٪ — فبدت الأقواس بقعًا داكنة متقاربة لا
       حزامًا يُقرأ. ورفعناها ووحّدنا حدّة الألوان فصار العنصر
       يُعرَف بلونه من نظرة. */
    g += `<path d="${arcPath(start, start + 30, (R.zodiacOut + R.zodiacIn) / 2)}" fill="none"
           stroke="${ELEM_COLOR[i % 4]}" stroke-width="${R.zodiacOut - R.zodiacIn}" opacity=".21"/>`;
    /* ── **اسم البرج بالعربية بدل رمزه** ─────────────────────────
       حروف البروج ♈–♓ صورتها الافتراضية في يونيكود صورةُ إيموجي.
       جرّبتُ العلاج المعياريّ — إلحاق U+FE0E وخطًّا يعرف الرموز —
       **ونُشِر، وبقيت المربّعات البنفسجية**. لأن سلسلة الخطوط
       الاحتياطية في نظام الزائر تُقدّم خطّ الإيموجي، ولا حيلة
       للصفحة في ترتيبها.

       فالحلّ ألّا نعتمد على خطٍّ أصلًا: **الموقع عربيّ، فليُكتب
       اسم البرج بالعربية**. وهو أوضح لقارئه من رمزٍ لا يعرفه —
       والرمز يبقى في الشرح عند التحويم لمن يريده. */
    const [tx, ty] = P(start + 15, (R.zodiacOut + R.zodiacIn) / 2);
    const long = nm.length > 6;
    g += `<text x="${tx.toFixed(1)}" y="${(ty + 4).toFixed(1)}" text-anchor="middle"
           font-size="${long ? 9.4 : 11}" font-weight="600"
           fill="${ELEM_COLOR[i % 4]}">${wEsc(nm)}</text>`;
    g += `<title>${wEsc(nm)}</title></g>`;
    g += line(start, R.zodiacIn, R.zodiacOut, 'stroke="var(--line2)" stroke-width="1"');
    /* علامات الدرجات كل خمس */
    for (let d = 5; d < 30; d += 5) {
      const len = d % 10 === 0 ? 6 : 3;
      g += line(start + d, R.zodiacIn, R.zodiacIn + len, 'stroke="var(--line2)" stroke-width=".6" opacity=".7"');
    }
  }

  /* ── حلقة المنازل القمرية الثماني والعشرين ── */
  if (showMansions) {
    const arc = 360 / 28;
    g += `<circle cx="${cx}" cy="${cy}" r="${R.mansionIn}" fill="none" stroke="var(--line)" stroke-width=".8"/>`;
    for (let i = 0; i < 28; i++) {
      g += line(i * arc, R.mansionIn, R.mansionOut, 'stroke="var(--gold-dim)" stroke-width=".5" opacity=".55"');
      const [mx, my] = P(i * arc + arc / 2, (R.mansionIn + R.mansionOut) / 2);
      g += `<text x="${mx.toFixed(1)}" y="${(my + 3).toFixed(1)}" text-anchor="middle"
             font-size="7.5" fill="var(--gold-dim)" opacity=".85">${i + 1}</text>`;
    }
  }

  /* ── البيوت ── */
  const cusps = c.houses.cusps.map(h => h.lon);
  g += `<circle cx="${cx}" cy="${cy}" r="${R.houseIn}" fill="rgba(10,15,29,.5)" stroke="var(--line)" stroke-width="1"/>`;
  cusps.forEach((cu, i) => {
    const major = i % 3 === 0;
    g += line(cu, R.houseIn, R.houseOut,
      `stroke="${major ? 'var(--gold)' : 'var(--line2)'}" stroke-width="${major ? 1.6 : .9}"`);
    const next = cusps[(i + 1) % 12];
    const mid = cu + (((next - cu) % 360 + 360) % 360) / 2;
    const [hx, hy] = P(mid, (R.houseIn + R.houseOut) / 2);
    const cusp = c.houses.cusps[i];
    const hd = (deep.houses || {})[String(i + 1)] || {};
    const tenants = c.bodies.filter(b => b.house === i + 1).map(b => b.name);
    g += `<g class="hs"${hint(`البيت ${HOUSE_ORD[i]}${hd.name ? ' — ' + hd.name : ''}`, [
        `يبدأ من ${cusp.text}، وصاحبه ${cusp.ruler}.`,
        hd.rules || (cusp.name || '').split(':').slice(1).join(':').trim(),
        hd.question ? `السؤال الذي يطرحه: ${hd.question}` : '',
        tenants.length ? `فيه من خريطتك: ${tenants.join('، ')}.`
                       : 'لا جِرم لك في هذا البيت — وهذا لا يعني فراغه في حياتك، بل أن أمره يُقرأ من صاحبه لا من ساكنه.',
      ], ` data-term="البيوت"`)}>
      <circle cx="${hx.toFixed(1)}" cy="${hy.toFixed(1)}" r="11" fill="transparent"/>
      <text x="${hx.toFixed(1)}" y="${(hy + 4).toFixed(1)}" text-anchor="middle"
           font-size="11" fill="var(--muted)">${i + 1}</text>
      <title>البيت ${HOUSE_ORD[i]}</title></g>`;
  });

  /* ── الأوتاد ── */
  const axes = [['الطالع','ASC'], ['وسط السماء','MC'], ['الغارب','DSC'], ['وتد الأرض','IC']];
  axes.forEach(([k, tag]) => {
    const A = c.angles[k];
    const L = A.lon;
    g += line(L, R.houseIn, R.zodiacOut + 4, 'stroke="var(--gold)" stroke-width="1.2" opacity=".85"');
    const [ax, ay] = P(L, R.axisLbl);
    g += `<g class="ax"${hint(`${k} (${tag})`, [
        `${A.text} — أي ${A.deg}° و${A.min}′ من برج ${A.sign}.`,
        'الأوتاد الأربعة ليست أجرامًا، بل مواضع تحدّدها لحظةُ الميلاد ومكانُه.',
        'وهي أدقّ ما في الخريطة حسّاسيةً للوقت: أربع دقائق تُزحزح الطالع درجة.',
      ], ` data-term="${wEsc(k)}"`)}>
      <circle cx="${ax.toFixed(1)}" cy="${ay.toFixed(1)}" r="13" fill="transparent"/>
      <text x="${ax.toFixed(1)}" y="${(ay + 4).toFixed(1)}" text-anchor="middle"
           font-size="10.5" font-weight="600" fill="var(--gold)">${tag}</text>
      <title>${wEsc(k)} — ${wEsc(A.text)}</title></g>`;
  });

  /* ── تفريق الكواكب المتزاحمة ── */
  const bodies = c.bodies.filter(b => b.name !== 'الذنب' || opts.tail !== false);
  const items = bodies.map(b => ({ ...b, rel: ((b.lon - asc) % 360 + 360) % 360 }))
                      .sort((a, b) => a.rel - b.rel);
  /* **التزاحم**: كان الفاصل الأدنى ثماني درجات ثابتة — وهو رقمٌ لا
     يعرف شيئًا عن نصف القطر. فعند ١٤٦ بكسل تساوي الثماني درجات
     ٢٠٫٥ بكسل، وقطر دائرة الجِرم ٢٥ — **فتتراكب الدوائر حتمًا**،
     وهو ما ظهر في زحل ونبتون وأورانوس في الصورة المصدَّرة.
     فصار الفاصل يُحسَب من نصف القطر نفسه: قوسٌ يسع الدائرة وفضلة. */
  const GLYPH = 25.4;                                   /* قطر دائرة الجِرم */
  const MIN = Math.min(16, (GLYPH + 2.6) * 180 / (Math.PI * R.planet));
  for (let pass = 0; pass < 60; pass++) {
    let moved = false;
    for (let i = 0; i < items.length; i++) {
      const a = items[i], b = items[(i + 1) % items.length];
      let gap = ((b.rel - a.rel) % 360 + 360) % 360;
      if (gap < MIN) {
        const push = (MIN - gap) / 2;
        a.rel = (a.rel - push + 360) % 360;
        b.rel = (b.rel + push) % 360;
        moved = true;
      }
    }
    if (!moved) break;
  }

  /* ── خطوط الزوايا ── */
  const pos = {};
  bodies.forEach(b => pos[b.name] = b.lon);
  const asps = (c.aspects || []).filter(a => (L.minor || opts.minorLines) ? true : a.major);
  let lines = '';
  /* النصّ يصل مع الزاوية نفسها من الخادم. وكانت الواجهة تُطابق
     بجداول `/api/depth` الخام فتُصيب ٢٧ من ٤٠ — والمطابقة صارت في
     الخادم حيث تُعرف الأسماء المرادفة وعلامات الجيل وطبائع الصغرى. */
  const aspText = a => [a.theme, a.meaning].filter(Boolean);
  asps.forEach(a => {
    if (pos[a.a] == null || pos[a.b] == null) return;
    const [x1,y1] = P(pos[a.a], R.aspect), [x2,y2] = P(pos[a.b], R.aspect);
    const col = ASPECT_COLOR[a.polarity] || 'var(--muted)';
    const w = (0.5 + a.strength * 1.6).toFixed(2);
    const op = (0.20 + a.strength * 0.55).toFixed(2);
    const pct = Math.round(a.strength * 100);
    const h = hint(`${a.a} ${a.symbol} ${a.b} — ${a.name}`, [
        `الفرق بينهما ${a.orb.toFixed(2)}° عن ${a.angle}° تامّة (الحدّ المسموح ${a.orb_max.toFixed(2)}°).`,
        a.exact ? 'زاوية تامّة تقريبًا — وهذا أشدّ ما تكون.' : `قوّتها ${pct}٪ بحسب قربها من التمام.`,
        a.applying ? 'مُقبِلة: تشتدّ ولمّا تتمّ بعد، فأثرها في ما هو آتٍ.'
                   : 'مُدبِرة: تمّت وانفكّت، فأثرها ماضٍ ينقضي.',
        ...aspText(a),
      ], ` data-term="${wEsc(a.name)}"`);
    /* الخطّ رفيع لا يُصاد بالمؤشّر، فنضع فوقه خطًّا شفّافًا عريضًا
       يلتقط التحويم. وهذه حيلة قديمة في SVG لا غنى عنها. */
    lines += `<g class="asp"${h}>
      <line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
              stroke="${col}" stroke-width="${w}" opacity="${op}"
              ${a.angle === 0 ? 'stroke-dasharray="3 3"' : ''}/>
      <line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
              stroke="transparent" stroke-width="9" pointer-events="stroke"/>
      <title>${wEsc(a.a)} ${wEsc(a.name)} ${wEsc(a.b)}</title></g>`;
  });
  g += `<g>${lines}</g>`;

  /* ── الكواكب ── */
  items.forEach(it => {
    const trueLon = it.lon, drawLon = asc + it.rel;
    /* خطّ رفيع من الموضع الحقيقي إلى الرمز المُزاح */
    g += line(trueLon, R.aspect + 4, R.planet - 12, 'stroke="var(--line2)" stroke-width=".7"');
    const [px, py] = P(drawLon, R.planet);
    const dignity = it.dignity && !/غريب/.test(it.dignity);
    const bad = it.dignity && /وبال|هبوط/.test(it.dignity);
    const col = bad ? 'var(--neg)' : dignity ? 'var(--pos)' : 'var(--text)';
    const ph = (deep.planet_in_house || {})[it.name] || {};
    const withMe = (c.aspects || [])
      .filter(a => a.major && (a.a === it.name || a.b === it.name))
      .map(a => `${a.name} ${a.a === it.name ? a.b : a.a}`);
    g += `<g class="pl" data-name="${it.name}" data-body="${wEsc(it.name)}"${hint(
      `${it.name} ${it.symbol}`, [
        `${it.text} — في البيت ${HOUSE_ORD[it.house - 1] || it.house}.`,
        `برجٌ ${it.element} ${it.mode}، وصاحبه ${it.ruler}.`,
        it.dignity_note ? `الكرامة: ${it.dignity_note}.` : (it.dignity || ''),
        speedWord(it),
        ph[String(it.house)],
        withMe.length ? `زواياه الكبرى: ${withMe.join('، ')}.` : 'لا زاوية كبرى له مع سواه.',
      ], ` data-term="${wEsc(it.name)}"`)}>
      <circle class="hint-halo" cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="16.5"
              fill="none" stroke="var(--gold)" stroke-width="1.4"/>
      <circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="12.5" fill="rgba(10,15,29,.82)" stroke="var(--line2)" stroke-width=".7"/>
      <text x="${px.toFixed(1)}" y="${(py + 6).toFixed(1)}" text-anchor="middle" font-size="16" fill="${col}">${wSym(it.symbol)}</text>
      <title>${wEsc(it.name)} — ${wEsc(it.text)}${it.retro ? ' (راجع)' : ''}${it.dignity ? ' · ' + wEsc(it.dignity) : ''}</title>
    </g>`;
    if (showDeg) {
      const [dx, dy] = P(drawLon, R.degLbl);
      g += `<text x="${dx.toFixed(1)}" y="${(dy + 3).toFixed(1)}" text-anchor="middle"
             font-size="8.5" fill="var(--muted)">${it.deg}°${it.retro ? '℞' : ''}</text>`;
    }
  });

  /* ══════════════════════════════════════════════════════════════
     لُبّ العجلة

     كان المركز فراغًا كبيرًا — نحو ثلث اللوحة بلا شيء. وأصل الرسم
     في الكتب القديمة أن يُكتب في وسطه اسمُ صاحبه ووقتُه.
     فنضع فيه ما لو لم يقرأ الزائر سواه لعرف خريطته:
     الطالع، والشمس، والقمر، وسيّد الخريطة.
     ══════════════════════════════════════════════════════════════ */
  /* ── طبقة السهام ─────────────────────────────────────────────
     تُرسَم على حلقةٍ بين البيوت والأجرام، بعلامةٍ صغيرة لا بدائرة —
     فهي نقاط محسوبة لا أجرام، ولا ينبغي أن تُشبه الكواكب. */
  if (showLots && (c.lots || []).length) {
    const rL = (R.houseIn + R.planet) / 2;
    (c.lots || []).forEach(Lt => {
      if (Lt.lon == null) return;
      const [lx, ly] = P(Lt.lon, rL);
      g += `<g class="lot"${hint(Lt.name, [
          `${Lt.text} — في البيت ${HOUSE_ORD[Lt.house - 1] || Lt.house}.`,
          Lt.formula ? `صيغته: ${Lt.formula}` : '',
          'والسهم نقطة محسوبة لا جِرم لها، فلا تُزاوي كما تُزاوي الكواكب.',
        ], ` data-term="السهم"`)}>
        <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="7" fill="transparent"/>
        <path d="M ${(lx - 3.4).toFixed(1)} ${ly.toFixed(1)} L ${lx.toFixed(1)} ${(ly - 3.4).toFixed(1)}
                 L ${(lx + 3.4).toFixed(1)} ${ly.toFixed(1)} L ${lx.toFixed(1)} ${(ly + 3.4).toFixed(1)} Z"
              fill="none" stroke="var(--gold)" stroke-width="1.1" opacity=".85"/>
        <title>${wEsc(Lt.name)} — ${wEsc(Lt.text)}</title></g>`;
    });
  }

  /* ══════════════════════════════════════════════════════════════
     بيان الخريطة — **خارج الـSVG**

     وضعتُه أوّلًا في وسط العجلة فحجب شكل الزوايا. ثم نقلتُه إلى
     أركان اللوحة، فانقطعت أنصاف كلماته: «الط» و«سيّد» و«Asi».
     فشخّصتُ الأمر بأن `text-anchor` منطقيّ في RTL، وعكستُ القيم،
     **ونُشِر الإصلاح فبقي الانقطاع كما هو حرفًا بحرف**.

     فتشخيصي كان خطأً، لا التنفيذ. ونصُّ SVG لا يلتفّ ولا يعرف
     حدود صندوقه، وضبطُ اتّجاهه يختلف بين محرّك وآخر — فالإصرار
     عليه إصرارٌ على تخمين.

     **والـHTML يعرف العربية ويعرف الالتفاف يقينًا.** فالبيان صار
     شبكةً حول العجلة، تلتفّ على الجوّال، ولا تنقطع أبدًا.
     ══════════════════════════════════════════════════════════════ */
  return `<svg viewBox="0 0 ${S} ${S}" width="100%" xmlns="http://www.w3.org/2000/svg"
            font-family='${WHEEL_FONT}' role="img"
            aria-label="الخريطة الفلكية الدائرية">${g}</svg>`;
}

/* بيان الخريطة: يُوضَع حول العجلة في HTML لا داخل الرسم */
function wheelInfo(c) {
  const find = n => (c.bodies || []).find(b => b.name === n);
  const at = k => c.angles[k] ? `${c.angles[k].short} ${c.angles[k].sign}` : '';
  const pos = b => b ? `${b.short} ${b.sign}` : '';
  const sun = find('الشمس'), moon = find('القمر');
  const when = (c.when_local || '').slice(0, 16).replace('T', ' — ');

  const cell = (rows) => `<div class="winf-c">${rows.filter(Boolean).map(
    ([k, v]) => `<div><span>${wEsc(k)}</span><b>${wEsc(v)}</b></div>`).join('')}</div>`;

  return `<div class="winf">
    ${cell([
      [(c.name || '').trim() ? 'الاسم' : 'الخريطة', (c.name || '').trim() || 'خريطة ميلاد'],
      ['الوقت', when], ['المكان', c.place || ''], ['المنطقة', c.tz || ''],
    ])}
    ${cell([
      ['الطالع', at('الطالع')], ['وسط السماء', at('وسط السماء')],
      c.almuten && c.almuten.winner ? ['سيّد الخريطة', c.almuten.winner] : null,
      c.houses ? ['نظام البيوت', c.houses.system_name] : null,
    ])}
    ${cell([
      ['الشمس', pos(sun)], ['القمر', pos(moon)],
      c.sect ? ['الطائفة', c.sect] : null,
      c.moon && c.moon.mansion ? ['منزلة القمر', c.moon.mansion.name] : null,
    ])}
    <div class="winf-c winf-key">
      <div><i class="k-pos"></i>جِرم له كرامة</div>
      <div><i class="k-neg"></i>جِرم في وبال أو هبوط</div>
      <div><i class="k-line k-pos"></i>زاوية موافقة</div>
      <div><i class="k-line k-neg"></i>زاوية مخالفة</div>
    </div>
  </div>`;
}

/* شبكة الزوايا: مثلّث سفلي يعرض الزاوية بين كل جرمين */
function aspectGrid(c) {
  const names = c.bodies.filter(b => b.core || ['أورانوس','نبتون','بلوتو'].includes(b.name))
                        .map(b => b.name);
  const sym = {}; c.bodies.forEach(b => sym[b.name] = b.symbol);
  const find = (a, b) => c.aspects.find(x => (x.a === a && x.b === b) || (x.a === b && x.b === a));
  let html = '<table class="agrid"><tbody>';
  for (let i = names.length - 1; i >= 0; i--) {
    html += `<tr><th>${sym[names[i]]}</th>`;
    for (let j = 0; j < i; j++) {
      const a = find(names[i], names[j]);
      const col = a ? (ASPECT_COLOR[a.polarity] || 'var(--muted)') : 'transparent';
      html += `<td style="color:${col}" title="${a ? names[i] + ' ' + a.name + ' ' + names[j] + ' — وجاج ' + a.orb + '°' : ''}">`
            + (a ? `${a.symbol}<small>${a.orb.toFixed(0)}</small>` : '') + '</td>';
    }
    html += '</tr>';
  }
  html += '<tr><th></th>' + names.slice(0, -1).map(n => `<th>${sym[n]}</th>`).join('') + '</tr>';
  return html + '</tbody></table>';
}


/* ─────────────────────────────────────────────────────────────
   العجلة المزدوجة — خريطتان في دائرة واحدة

   الداخل خريطة الأوّل، والخارج خريطة الثاني. الطالع المرجعي
   طالع الأوّل دائمًا: العجلة تُقرأ من موضعه هو، فيرى القارئ
   في أيّ بيوته وقعت كواكب صاحبه.
   ───────────────────────────────────────────────────────────── */
function doubleWheelSVG(a, b, inter, opts = {}) {
  const S = opts.size || 660;
  const cx = S / 2, cy = S / 2;
  const R = {
    zodiacOut: S * .478, zodiacIn: S * .418,
    outerPlanet: S * .385,          /* كواكب الثاني */
    ringMid: S * .350,
    innerPlanet: S * .300,          /* كواكب الأوّل */
    houseOut: S * .268, houseIn: S * .200,
    aspect: S * .196,
  };
  const asc = a.angles['الطالع'].lon;
  const ang = lon => (180 + (lon - asc)) * Math.PI / 180;
  const P = (lon, r) => [cx + r * Math.cos(ang(lon)), cy - r * Math.sin(ang(lon))];
  const line = (lon, r1, r2, at) => {
    const [x1,y1] = P(lon,r1), [x2,y2] = P(lon,r2);
    return `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" ${at}/>`;
  };
  const arcPath = (p, q, r) => {
    const [x1,y1] = P(p,r), [x2,y2] = P(q,r);
    const large = ((q - p + 360) % 360) > 180 ? 1 : 0;
    return `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 ${large} 0 ${x2.toFixed(1)} ${y2.toFixed(1)}`;
  };

  let g = '';

  /* حلقة البروج */
  g += `<circle cx="${cx}" cy="${cy}" r="${R.zodiacOut}" fill="none" stroke="var(--line2)"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="${R.zodiacIn}" fill="none" stroke="var(--line2)"/>`;
  for (let i = 0; i < 12; i++) {
    const st = i * 30;
    g += `<path d="${arcPath(st, st + 30, (R.zodiacOut + R.zodiacIn) / 2)}" fill="none"
           stroke="${ELEM_COLOR[i % 4]}" stroke-width="${R.zodiacOut - R.zodiacIn}" opacity=".12"/>`;
    g += line(st, R.zodiacIn, R.zodiacOut, 'stroke="var(--line2)" stroke-width="1"');
    const [tx, ty] = P(st + 15, (R.zodiacOut + R.zodiacIn) / 2);
    g += `<text x="${tx.toFixed(1)}" y="${(ty + 7).toFixed(1)}" text-anchor="middle"
           font-size="20" fill="${ELEM_COLOR[i % 4]}">${SIGN_SYMBOLS[i]}</text>`;
  }

  /* حلقتان فاصلتان */
  [R.ringMid, R.houseOut].forEach(r =>
    g += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--line)" stroke-width=".8"/>`);

  /* بيوت الأوّل — هي مرجع القراءة */
  const cusps = a.houses.cusps.map(h => h.lon);
  g += `<circle cx="${cx}" cy="${cy}" r="${R.houseIn}" fill="rgba(10,15,29,.55)" stroke="var(--line)"/>`;
  cusps.forEach((cu, i) => {
    const major = i % 3 === 0;
    g += line(cu, R.houseIn, R.houseOut,
      `stroke="${major ? 'var(--gold)' : 'var(--line2)'}" stroke-width="${major ? 1.5 : .8}"`);
    const next = cusps[(i + 1) % 12];
    const mid = cu + (((next - cu) % 360 + 360) % 360) / 2;
    const [hx, hy] = P(mid, (R.houseIn + R.houseOut) / 2);
    g += `<text x="${hx.toFixed(1)}" y="${(hy + 4).toFixed(1)}" text-anchor="middle"
           font-size="10.5" fill="var(--muted)">${i + 1}</text>`;
  });

  /* أوتاد الأوّل */
  [['الطالع','ASC'], ['وسط السماء','MC'], ['الغارب','DSC'], ['وتد الأرض','IC']]
    .forEach(([k, tag]) => {
      const L = a.angles[k].lon;
      g += line(L, R.houseIn, R.zodiacOut + 3, 'stroke="var(--gold)" stroke-width="1.1" opacity=".8"');
      const [ax, ay] = P(L, R.zodiacOut + 15);
      g += `<text x="${ax.toFixed(1)}" y="${(ay + 4).toFixed(1)}" text-anchor="middle"
             font-size="10" font-weight="600" fill="var(--gold)">${tag}</text>`;
    });

  /* خطوط الوصلات المتبادلة، من الحلقة الداخلية إلى الخارجية */
  const posA = {}, posB = {};
  a.bodies.forEach(x => posA[x.name] = x.lon);
  b.bodies.forEach(x => posB[x.name] = x.lon);
  posA['الطالع'] = a.angles['الطالع'].lon;
  posA['وسط السماء'] = a.angles['وسط السماء'].lon;
  posB['الطالع'] = b.angles['الطالع'].lon;
  posB['وسط السماء'] = b.angles['وسط السماء'].lon;

  let lines = '';
  (inter || []).filter(x => x.major).forEach(x => {
    if (posA[x.a] == null || posB[x.b] == null) return;
    const [x1,y1] = P(posA[x.a], R.aspect), [x2,y2] = P(posB[x.b], R.aspect);
    const col = ASPECT_COLOR[x.polarity] || 'var(--muted)';
    lines += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
              stroke="${col}" stroke-width="${(0.5 + x.strength * 1.5).toFixed(2)}"
              opacity="${(0.18 + x.strength * 0.5).toFixed(2)}"
              ${x.angle === 0 ? 'stroke-dasharray="3 3"' : ''}/>`;
  });
  g += `<g>${lines}</g>`;

  /* تفريق المتزاحمة داخل كل حلقة على حدة */
  const spread = (list, minGap) => {
    const items = list.map(x => ({ ...x, rel: ((x.lon - asc) % 360 + 360) % 360 }))
                      .sort((p, q) => p.rel - q.rel);
    for (let pass = 0; pass < 60; pass++) {
      let moved = false;
      for (let i = 0; i < items.length; i++) {
        const p = items[i], q = items[(i + 1) % items.length];
        let gap = ((q.rel - p.rel) % 360 + 360) % 360;
        if (gap < minGap) {
          const push = (minGap - gap) / 2;
          p.rel = (p.rel - push + 360) % 360;
          q.rel = (q.rel + push) % 360;
          moved = true;
        }
      }
      if (!moved) break;
    }
    return items;
  };

  const draw = (items, radius, ringName, tone) => {
    items.forEach(it => {
      const drawLon = asc + it.rel;
      g += line(it.lon, radius + (tone === 'in' ? 10 : -10),
                radius + (tone === 'in' ? -1 : 1) * 0, 'stroke="var(--line2)" stroke-width=".6"');
      const [px, py] = P(drawLon, radius);
      const fill = tone === 'in' ? 'rgba(10,15,29,.9)' : 'rgba(30,22,10,.9)';
      const stroke = tone === 'in' ? 'var(--line2)' : 'var(--gold-dim)';
      g += `<g class="pl" data-name="${it.name}">
        <circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="12" fill="${fill}"
                stroke="${stroke}" stroke-width=".8"/>
        <text x="${px.toFixed(1)}" y="${(py + 5.5).toFixed(1)}" text-anchor="middle"
              font-size="15" fill="${tone === 'in' ? 'var(--text)' : 'var(--gold)'}">${it.symbol}</text>
        <title>${ringName}: ${it.name} — ${it.text || ''}${it.retro ? ' (راجع)' : ''}</title>
      </g>`;
    });
  };

  const keep = x => x.name !== 'الذنب' && x.name !== 'ليليث الحقيقية';
  draw(spread(a.bodies.filter(keep), 9), R.innerPlanet, a.name || 'الأوّل', 'in');
  draw(spread(b.bodies.filter(keep), 9), R.outerPlanet, b.name || 'الثاني', 'out');

  /* وسم الحلقتين */
  g += `<text x="${cx}" y="${cy - 6}" text-anchor="middle" font-size="11" fill="var(--muted)">
          الداخل: ${a.name || 'الأوّل'}</text>
        <text x="${cx}" y="${cy + 10}" text-anchor="middle" font-size="11" fill="var(--gold)">
          الخارج: ${b.name || 'الثاني'}</text>`;

  return `<svg viewBox="0 0 ${S} ${S}" width="100%" xmlns="http://www.w3.org/2000/svg"
            font-family='${WHEEL_FONT}' role="img"
            aria-label="العجلة المزدوجة — خريطتان متراكبتان">${g}</svg>`;
}
