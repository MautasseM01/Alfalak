/* أدوات مشتركة بين صفحات الموقع */

const API = (path, params = {}) => {
  const q = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== '' && v != null)
  ).toString();
  return fetch(`/api/${path}${q ? '?' + q : ''}`)
    .then(async r => {
      const j = await r.json().catch(() => ({ error: 'ردّ غير مفهوم من الخادم' }));
      if (!r.ok || j.error) throw new Error(j.error || `خطأ ${r.status}`);
      return j;
    });
};

/* ── سماء النجوم ── */
function starfield(id) {
  const c = document.getElementById(id);
  if (!c) return;
  const x = c.getContext('2d');
  let stars = [];
  const init = () => {
    c.width = innerWidth; c.height = innerHeight; stars = [];
    const n = Math.min(150, Math.floor(innerWidth * innerHeight / 9000));
    for (let i = 0; i < n; i++) stars.push({
      x: Math.random() * c.width, y: Math.random() * c.height,
      r: Math.random() * 1.1 + .2, a: Math.random() * .6 + .15, s: Math.random() * .012 + .003
    });
  };
  const draw = t => {
    x.clearRect(0, 0, c.width, c.height);
    for (const s of stars) {
      const o = s.a + Math.sin(t * s.s) * .25;
      x.beginPath(); x.arc(s.x, s.y, s.r, 0, 7);
      x.fillStyle = 'rgba(232,236,246,' + Math.max(0, o) + ')'; x.fill();
    }
    requestAnimationFrame(draw);
  };
  init(); addEventListener('resize', init); requestAnimationFrame(draw);
}

/* ── إكمال تلقائي لأسماء المدن ── */
function cityInput(input, onPick) {
  const box = document.createElement('div');
  box.className = 'ac';
  input.parentNode.appendChild(box);
  let items = [], sel = -1, timer = null;

  const close = () => { box.classList.remove('show'); sel = -1; };
  const render = () => {
    box.innerHTML = items.map((c, i) =>
      `<div data-i="${i}" class="${i === sel ? 'sel' : ''}">${c.ar}<span>${c.country} · ${c.en}</span></div>`
    ).join('');
    box.classList.toggle('show', items.length > 0);
  };
  const pick = i => {
    const c = items[i];
    if (!c) return;
    input.value = c.ar;
    input.dataset.lat = c.lat; input.dataset.lon = c.lon; input.dataset.tz = c.tz;
    close();
    onPick && onPick(c);
  };

  input.addEventListener('input', () => {
    delete input.dataset.lat; delete input.dataset.lon; delete input.dataset.tz;
    clearTimeout(timer);
    const v = input.value.trim();
    if (v.length < 1) { items = []; close(); return; }
    timer = setTimeout(() => {
      API('atlas', { q: v, limit: 8 })
        .then(r => { items = r.results; sel = -1; render(); })
        .catch(() => { items = []; close(); });
    }, 180);
  });
  input.addEventListener('keydown', e => {
    if (!box.classList.contains('show')) return;
    if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, items.length - 1); render(); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); render(); e.preventDefault(); }
    else if (e.key === 'Enter') { if (sel >= 0) { pick(sel); e.preventDefault(); } }
    else if (e.key === 'Escape') close();
  });
  box.addEventListener('mousedown', e => {
    const d = e.target.closest('[data-i]');
    if (d) { e.preventDefault(); pick(+d.dataset.i); }
  });
  input.addEventListener('blur', () => setTimeout(close, 150));
}

/* ── نسخ إلى الحافظة ── */
async function copyText(text, btn, label) {
  try { await navigator.clipboard.writeText(text); }
  catch (_) {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); ta.remove();
  }
  const old = btn.textContent;
  btn.textContent = '✓ نُسخ'; btn.classList.add('ok');
  setTimeout(() => { btn.textContent = label || old; btn.classList.remove('ok'); }, 1800);
}

/* ── تحويل نصّ النشرة إلى HTML ── */
const esc = t => t.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const hilite = t => t.replace(/(\d{1,2}:\d{2})/g, '<span class="t">$1</span>');

function bulletinHtml(raw) {
  let html = '';
  for (const block of raw.split('\n\n')) {
    const lines = block.split('\n');
    const isHead = lines[0].startsWith('#');
    const title = isHead ? lines[0].replace(/^#/, '').replace(/_/g, ' ').replace(/ —.*$/, '') : null;
    const rest = isHead ? lines.slice(1) : lines;
    html += '<div class="sec">';
    if (title) html += `<h3>${esc(title)}</h3>`;
    let ul = false;
    for (const ln of rest) {
      if (!ln.trim()) continue;
      if (ln.startsWith('- ')) {
        if (!ul) { html += '<ul>'; ul = true; }
        const body = ln.slice(2);
        let cls = /سلبية/.test(body) ? 'neg' : /إيجابية/.test(body) ? 'pos' : '';
        if (/خلو مسار/.test(body)) cls = 'voc';
        html += `<li class="${cls}">${hilite(esc(body))}</li>`;
      } else {
        if (ul) { html += '</ul>'; ul = false; }
        html += `<p class="${ln.startsWith('  ') ? 'note' : ''}">${hilite(esc(ln.trim()))}</p>`;
      }
    }
    if (ul) html += '</ul>';
    html += '</div>';
  }
  return html;
}

/* ── الشرح عند الطلب ── */
let GLOSSARY = null;
const glossaryReady = () =>
  GLOSSARY ? Promise.resolve(GLOSSARY)
           : API('glossary').then(r => (GLOSSARY = r.terms)).catch(() => (GLOSSARY = {}));

/* علامة استفهام تفتح شرحًا موجزًا */
const q = term => `<button class="q" data-term="${term}" aria-label="ما معنى ${term}؟">؟</button>`;

function initGlossary() {
  glossaryReady();
  let pop = document.querySelector('.gpop');
  if (!pop) {
    pop = document.createElement('div');
    pop.className = 'gpop';
    document.body.appendChild(pop);
  }
  const close = () => pop.classList.remove('show');

  document.addEventListener('click', async e => {
    const b = e.target.closest('.q');
    if (!b) { if (!e.target.closest('.gpop')) close(); return; }
    e.preventDefault(); e.stopPropagation();
    const terms = await glossaryReady();
    const t = b.dataset.term;
    const text = terms[t] || 'لا شرح متاحًا لهذا المصطلح بعد.';
    pop.innerHTML = `<strong>${t}</strong><p>${text}</p>
      <a href="/learn.html#${encodeURIComponent(t)}">المزيد في صفحة التعلّم ›</a>`;
    pop.classList.add('show');
    const r = b.getBoundingClientRect();
    const w = Math.min(330, innerWidth - 24);
    pop.style.width = w + 'px';
    let left = r.left + scrollX + r.width / 2 - w / 2;
    left = Math.max(12, Math.min(left, innerWidth - w - 12));
    pop.style.left = left + 'px';
    pop.style.top = (r.bottom + scrollY + 8) + 'px';
  });
  addEventListener('keydown', e => e.key === 'Escape' && close());
  addEventListener('scroll', close, { passive: true });
}

/* ── تخزين محلي ── */
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { } },
};

/* ── تاريخ اليوم بصيغة ISO ── */
const todayISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};
const shiftISO = (iso, days) => {
  const d = new Date(iso + 'T12:00:00');
  d.setDate(d.getDate() + days);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

/* ══════════════════════════════════════════════════════════════
   الخلاصة — أوّل ما تراه العين

   قاعدة الصفحة: لا يُعرَض جدول قبل جملة. فمن دخل الموقع أوّل مرّة
   يقرأ سطرين يفهمهما، ثم يختار أن ينزل أو لا ينزل.
   ══════════════════════════════════════════════════════════════ */
function gistHTML(g) {
  if (!g || !g.lines || !g.lines.length) return '';
  const e = t => String(t == null ? '' : t)
    .replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  return `<div class="gist">
    <h3>${e(g.title)}</h3>
    ${g.lines.map(l => `<p>${e(l)}</p>`).join('')}
    ${g.then ? `<p style="color:var(--muted);font-size:.87rem">${e(g.then)}</p>` : ''}
  </div>`;
}

/* ══════════════════════════════════════════════════════════════
   الانتظار — تقدّم يُقاس لا دوران أبديّ

   الدوران الأبديّ يقول «لم أُعلَّق» ولا يقول «كم بقي». والبحث عندنا
   قد يبلغ أربع ثوانٍ، وهي دهر أمام شاشة صامتة. فنعرض خطوات معلومة
   وشريطًا يتقدّم بتقدير مبنيّ على قياس فعليّ لا على تخمين.
   ══════════════════════════════════════════════════════════════ */
function waitBox(el, steps, expectMs) {
  const e = t => String(t).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  el.innerHTML = `<div class="card"><div class="wait">
    <div class="step" id="_wstep">${e(steps[0])}</div>
    <div class="bar"><i id="_wbar"></i></div>
    <div class="hint" id="_whint"></div>
  </div></div>`;
  const bar = document.getElementById('_wbar');
  const step = document.getElementById('_wstep');
  const hint = document.getElementById('_whint');
  const t0 = Date.now();
  let done = false;

  const tick = setInterval(() => {
    if (done) return;
    const dt = Date.now() - t0;
    /* نقترب من ٩٢٪ ولا نبلغ المئة: الوصول إلى المئة قبل الجواب كذب */
    const pct = Math.min(92, 100 * (1 - Math.exp(-dt / (expectMs * 0.55))));
    bar.style.width = pct.toFixed(0) + '%';
    const i = Math.min(steps.length - 1, Math.floor(dt / (expectMs / steps.length)));
    step.textContent = steps[i];
    if (dt > expectMs * 2) hint.textContent = 'أطول من المعتاد… ما زلت أعمل.';
  }, 220);

  return {
    finish() { done = true; clearInterval(tick); bar.style.width = '100%'; },
    fail(msg) {
      done = true; clearInterval(tick);
      el.innerHTML = `<div class="card"><div class="msg err">${e(msg)}</div></div>`;
    },
  };
}

/* ══════════════════════════════════════════════════════════════
   الروابط تُشارَك وتُستعاد

   كان من حسب خريطته لا يستطيع أن يُرسلها لصاحبه: الصفحة لا تحمل
   ما فيها في عنوانها. فصارت المعطيات في العنوان، فيُنسخ ويُرسَل
   ويُحفظ في المفضّلة ويعود كما هو.
   ══════════════════════════════════════════════════════════════ */
function urlState(fields) {
  const p = new URLSearchParams(location.search);
  const out = {};
  fields.forEach(f => { const v = p.get(f); if (v) out[f] = v; });
  return out;
}

function pushState(obj) {
  const p = new URLSearchParams();
  Object.entries(obj).forEach(([k, v]) => {
    if (v !== '' && v != null) p.set(k, v);
  });
  const url = location.pathname + (p.toString() ? '?' + p : '');
  history.replaceState(null, '', url);
}

function shareButton(label) {
  return `<button class="btn ghost" id="_share">${label || 'انسخ رابط هذه النتيجة'}</button>`;
}

function initShare() {
  const b = document.getElementById('_share');
  if (!b) return;
  b.onclick = async () => {
    const url = location.href;
    try {
      if (navigator.share) { await navigator.share({ url }); return; }
      await navigator.clipboard.writeText(url);
      const old = b.textContent;
      b.textContent = 'نُسخ ✓';
      setTimeout(() => (b.textContent = old), 1600);
    } catch (e) { /* المستخدم ألغى المشاركة — لا شيء يُقال */ }
  };
}

/* ══════════════════════════════════════════════════════════════
   الطباعة والحفظ والمشاركة

   الطباعة هنا ليست زينة: من حسب خريطته أراد ورقةً يقرؤها ويُريها
   غيره. وقواعد الطباعة في style.css تُخفي الشريط والأزرار، وتقلب
   الخلفية بيضاء، وتفتح كل ما كان مطويًّا — فالورقة لا يُضغَط عليها.
   ══════════════════════════════════════════════════════════════ */
function toolbarHTML(opts = {}) {
  const e = t => String(t).replace(/[&<>]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  return `<div class="row toolbar" style="margin-top:18px">
    <button class="btn ghost" id="_print">اطبع أو احفظ PDF</button>
    <button class="btn ghost" id="_share">${e(opts.share || 'انسخ رابط هذه النتيجة')}</button>
    ${opts.svg ? '<button class="btn ghost" id="_img">نزّل العجلة صورة</button>' : ''}
  </div>`;
}

function initToolbar() {
  initShare();
  const p = document.getElementById('_print');
  if (p) p.onclick = () => window.print();

  const im = document.getElementById('_img');
  if (im) im.onclick = () => {
    const svg = document.querySelector('#out svg');
    if (!svg) return;
    /* نُثبّت الألوان قبل التصدير: المتغيّرات CSS لا تعبر إلى الملفّ،
       فلو صدّرناه كما هو خرجت الصورة بلا ألوان. */
    const clone = svg.cloneNode(true);
    const cs = getComputedStyle(document.documentElement);
    const vars = ['--gold', '--gold-dim', '--text', '--muted', '--dim',
                  '--line', '--line2', '--pos', '--neg', '--neu', '--bg'];
    let s = new XMLSerializer().serializeToString(clone);
    vars.forEach(v => {
      s = s.split(`var(${v})`).join(cs.getPropertyValue(v).trim() || '#888');
    });
    s = s.replace('<svg', '<svg style="background:#0a0f1d"');
    const blob = new Blob([s], { type: 'image/svg+xml;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'alfalak.svg';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  };
}

/* منطقة النتيجة تُعلن عن نفسها لقارئ الشاشة.
   وبدون هذا، من يتصفّح بالقارئ يضغط «احسب» فلا يسمع شيئًا: المحتوى
   تبدّل تحته وهو لا يدري. */
function markLive(el) {
  if (!el) return;
  el.setAttribute('role', 'region');
  el.setAttribute('aria-live', 'polite');
  el.setAttribute('aria-busy', 'false');
  el.setAttribute('tabindex', '-1');
}

function announce(msg) {
  let n = document.getElementById('_announce');
  if (!n) {
    n = document.createElement('div');
    n.id = '_announce';
    n.className = 'sr-only';
    n.setAttribute('role', 'status');
    n.setAttribute('aria-live', 'polite');
    document.body.appendChild(n);
  }
  n.textContent = msg;
}

/* ══════════════════════════════════════════════════════════════
   شريط الأدوات يُركَّب وحده

   أوّل محاولة حقنت استدعاء toolbarHTML في كل صفحة بتعبير نمطيّ،
   فأصابت **سطر التحميل** بدل سطر النتيجة في بعضها، وقطعت قالبًا
   نصّيًّا في بعضها الآخر — فسقطت عشر صفحات دفعةً واحدة.

   والصواب أن يكون في موضع واحد: مُراقِب يرى متى امتلأ #out
   بنتيجة، فيُلحق الشريط في آخرها. لا تعديل في أيّ صفحة، ولا
   تعبير نمطيّ يُخطئ موضعه.
   ══════════════════════════════════════════════════════════════ */
function autoToolbar() {
  const out = document.getElementById('out');
  if (!out || out.dataset.tb) return;
  out.dataset.tb = '1';
  markLive(out);

  const attach = () => {
    /* نتيجة حقيقية لا رسالة انتظار: بطاقة فيها جسم، لا msg وحدها */
    const real = out.querySelector('.card .card-body, .gist');
    const waiting = out.querySelector('.wait, .msg');
    if (!real || waiting) return;
    if (out.querySelector('.toolbar')) return;
    const hasSvg = !!out.querySelector('svg');
    out.insertAdjacentHTML('beforeend', toolbarHTML({ svg: hasSvg }));
    initToolbar();
    announce('تمّ الحساب. النتيجة معروضة أسفل النموذج.');
  };

  new MutationObserver(attach).observe(out, { childList: true, subtree: false });
  attach();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoToolbar);
} else {
  autoToolbar();
}
