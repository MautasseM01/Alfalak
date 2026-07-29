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
