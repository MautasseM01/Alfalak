/* ══════════════════════════════════════════════════════════════════
   قائمة اختيار من عندنا — select.js

   قلتُ من قبل إنّ قائمة النظام «لا تقبل التنسيق»، وهذا صحيح ولكنّه
   **اعتذار لا جواب**: زوايا القائمة المنسدلة حادّة لأن النظام يرسمها،
   والجواب أن تُبنى قائمة من عندنا لا أن يُعتذَر عن قائمته.

   وفي الموقع **ستّ عشرة قائمة** موزّعة على تسع صفحات. فلا تُبنى في
   كل صفحة على حدة — بل تُطبَّق من هنا مرّةً واحدة على كل `<select>`.
   (وهذا الدرس مدفوع الثمن: حقنُ شريط الأدوات في كل صفحة بتعبير نمطيّ
   كسر عشر صفحات دفعةً واحدة.)

   ── ثلاثة شروط لا نتنازل عنها ──────────────────────────────────
   ١. **`<select>` الأصلي يبقى** في النموذج ويبقى مصدر الحقيقة. فمن
      عطّل الجافاسكربت، أو أرسل النموذج، أو قرأ `.value` من صفحته —
      وجد كل شيء يعمل كما كان. نحن نضع واجهةً فوقه لا بديلًا عنه.
   ٢. **لوحة المفاتيح كاملة**: الأسهم، وHome وEnd، وEnter والمسافة،
      وEscape، **والقفز بأوّل حرف** — وهو ما يفعله المعتادون على
      قوائم النظام ويفتقدونه في أكثر البدائل.
   ٣. **معيار ARIA**: `combobox` و`listbox` و`option`، فيقرؤها
      قارئ الشاشة قائمةً لا زرًّا غامضًا.
   ══════════════════════════════════════════════════════════════════ */

const SEL_OPEN = new Set();

function selEsc(t) {
  return String(t == null ? '' : t)
    .replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

let SEL_SEQ = 0;

function enhanceSelect(native) {
  if (!native || native.dataset.selDone || native.multiple || native.size > 1) return;
  native.dataset.selDone = '1';
  const id = 'sel' + (++SEL_SEQ);

  const wrap = document.createElement('div');
  wrap.className = 'sel';
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'sel-btn';
  btn.id = id + 'b';
  btn.setAttribute('role', 'combobox');
  btn.setAttribute('aria-haspopup', 'listbox');
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-controls', id + 'l');
  const lbl = native.labels && native.labels[0];
  if (lbl) btn.setAttribute('aria-labelledby', (lbl.id || (lbl.id = id + 'lb')) + ' ' + btn.id);

  const list = document.createElement('div');
  list.className = 'sel-list';
  list.id = id + 'l';
  list.setAttribute('role', 'listbox');
  list.hidden = true;

  /* ــ بناء الخيارات، مع احترام `<optgroup>` ــ */
  const opts = [];
  const build = () => {
    list.innerHTML = '';
    opts.length = 0;
    [...native.children].forEach(node => {
      if (node.tagName === 'OPTGROUP') {
        const h = document.createElement('div');
        h.className = 'sel-grp';
        h.textContent = node.label;
        list.appendChild(h);
        [...node.children].forEach(o => addOpt(o));
      } else if (node.tagName === 'OPTION') addOpt(node);
    });
  };
  const addOpt = o => {
    const el = document.createElement('div');
    el.className = 'sel-opt';
    el.setAttribute('role', 'option');
    el.id = `${id}o${opts.length}`;
    el.dataset.v = o.value;
    el.textContent = o.textContent;
    if (o.disabled) el.setAttribute('aria-disabled', 'true');
    list.appendChild(el);
    opts.push(el);
  };

  wrap.appendChild(btn);
  wrap.appendChild(list);
  native.parentNode.insertBefore(wrap, native);
  wrap.appendChild(native);
  native.classList.add('sel-native');
  native.setAttribute('tabindex', '-1');
  native.setAttribute('aria-hidden', 'true');

  let active = -1;

  const paint = () => {
    const sel = native.selectedIndex;
    btn.textContent = '';
    const v = document.createElement('span');
    v.className = 'sel-val';
    v.textContent = native.options[sel] ? native.options[sel].textContent : '';
    btn.appendChild(v);
    const car = document.createElement('i');
    car.className = 'sel-caret';
    car.setAttribute('aria-hidden', 'true');
    btn.appendChild(car);
    opts.forEach((o, i) => o.setAttribute('aria-selected', i === sel ? 'true' : 'false'));
  };

  const mark = i => {
    if (i < 0 || i >= opts.length) return;
    opts.forEach(o => o.classList.remove('on'));
    opts[i].classList.add('on');
    active = i;
    btn.setAttribute('aria-activedescendant', opts[i].id);
    const r = opts[i].getBoundingClientRect(), lr = list.getBoundingClientRect();
    if (r.bottom > lr.bottom) list.scrollTop += r.bottom - lr.bottom;
    else if (r.top < lr.top) list.scrollTop -= lr.top - r.top;
  };

  const open = () => {
    SEL_OPEN.forEach(f => f());
    list.hidden = false;
    wrap.classList.add('open');
    btn.setAttribute('aria-expanded', 'true');
    mark(native.selectedIndex);
    /* إن ضاق ما تحتها فُتحت إلى أعلى — وإلّا خرجت عن الشاشة */
    const r = btn.getBoundingClientRect();
    wrap.classList.toggle('up', innerHeight - r.bottom < Math.min(280, opts.length * 40) + 16
                                 && r.top > innerHeight - r.bottom);
  };
  const close = (focus) => {
    if (list.hidden) return;
    list.hidden = true;
    wrap.classList.remove('open', 'up');
    btn.setAttribute('aria-expanded', 'false');
    btn.removeAttribute('aria-activedescendant');
    if (focus) btn.focus();
  };
  SEL_OPEN.add(() => close(false));

  const choose = i => {
    if (i < 0 || i >= opts.length) return;
    if (opts[i].getAttribute('aria-disabled') === 'true') return;
    if (native.selectedIndex !== i) {
      native.selectedIndex = i;
      /* الصفحات تُصغي إلى `change` على القائمة الأصلية — فنُطلقه
         كما يُطلقه المتصفّح، فلا تحتاج صفحةٌ واحدة إلى تعديل. */
      native.dispatchEvent(new Event('input', { bubbles: true }));
      native.dispatchEvent(new Event('change', { bubbles: true }));
    }
    paint();
    close(true);
  };

  btn.addEventListener('click', () => (list.hidden ? open() : close(true)));
  list.addEventListener('click', e => {
    const o = e.target.closest('.sel-opt');
    if (o) choose(opts.indexOf(o));
  });
  list.addEventListener('pointermove', e => {
    const o = e.target.closest('.sel-opt');
    if (o) mark(opts.indexOf(o));
  });

  /* ــ القفز بأوّل حرف: يُجمَع ما يُكتب سريعًا ثم يُنسى ــ */
  let typed = '', typeT = 0;
  btn.addEventListener('keydown', e => {
    const k = e.key;
    if (k === 'Escape') { close(true); return; }
    if (k === 'Tab') { close(false); return; }
    if (list.hidden && (k === 'ArrowDown' || k === 'ArrowUp' || k === 'Enter' || k === ' ')) {
      e.preventDefault(); open(); return;
    }
    if (list.hidden) {
      /* مغلقةً: الأسهم تُبدّل الاختيار مباشرةً، كقائمة النظام */
      if (k === 'ArrowRight' || k === 'ArrowLeft') return;
    }
    if (k === 'ArrowDown') { e.preventDefault(); mark(Math.min(active + 1, opts.length - 1)); }
    else if (k === 'ArrowUp') { e.preventDefault(); mark(Math.max(active - 1, 0)); }
    else if (k === 'Home') { e.preventDefault(); mark(0); }
    else if (k === 'End') { e.preventDefault(); mark(opts.length - 1); }
    else if (k === 'Enter' || k === ' ') { e.preventDefault(); choose(active); }
    else if (k.length === 1) {
      clearTimeout(typeT);
      typed += k;
      typeT = setTimeout(() => (typed = ''), 700);
      const norm = s => s.replace(/[ً-ْـ]/g, '').replace(/[أإآ]/g, 'ا');
      const t = norm(typed);
      const i = opts.findIndex(o => norm(o.textContent).trim().startsWith(t));
      if (i >= 0) { if (list.hidden) choose(i); else mark(i); }
    }
  });

  document.addEventListener('pointerdown', e => {
    if (!wrap.contains(e.target)) close(false);
  });

  /* ــ عقدة: الإسناد البرمجي لا يُطلق حدثًا ــ
     صفحات كثيرة تكتب `$('system').value = c.system` عند فتح خريطة
     محفوظة. والمتصفّح **لا يُطلق `change`** على الإسناد البرمجي،
     فتبقى واجهتنا على القيمة القديمة والقائمةُ على الجديدة.
     فنلفّ خاصّية `value` على هذا العنصر وحده — بواصف النموذج
     الأصلي نفسه لا بتقليد له — فيبقى السلوك سلوك المتصفّح ونعلم
     متى تبدّل. ولا تحتاج صفحةٌ واحدة إلى تعديل. */
  ['value', 'selectedIndex'].forEach(prop => {
    const d = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, prop);
    if (!d || !d.set) return;
    Object.defineProperty(native, prop, {
      configurable: true,
      get() { return d.get.call(this); },
      set(v) { d.set.call(this, v); paint(); },
    });
  });
  native.addEventListener('change', paint);

  build();
  paint();
  return { rebuild() { build(); paint(); } };
}

function initSelects(root) {
  (root || document).querySelectorAll('select:not([data-sel-done])')
    .forEach(enhanceSelect);
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', () => initSelects());
  else initSelects();
}

if (typeof module !== 'undefined' && module.exports)
  module.exports = { enhanceSelect, initSelects };
