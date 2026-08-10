/* ─────────────────────────────────────────────────────────────
   التصفّح — أبواب لا قائمة

   كان الشريط اثني عشر رابطًا في سطر واحد. والعين لا تقرأ اثني عشر
   خيارًا متساويًا، بل تمسح ثلاثة أو أربعة. فجُمعت الصفحات في أربعة
   أبواب بأسئلة لا بمصطلحات: «يومي» و«خريطتي» و«قراري» و«أتعلّم».

   ولماذا في ملفّ واحد؟ لأنها كانت مكرّرة في اثنتي عشرة صفحة، فكل
   إضافة تعني اثني عشر تعديلًا — وقد نسينا رابطًا مرّة فعلًا.

   والروابط تبقى مكتوبة في HTML كما هي، وهذا الملفّ يُعيد ترتيبها:
   فمن جاء بلا جافاسكربت — أو كان زاحف محرّك بحث — رأى القائمة
   كاملة، ومن جاء بمتصفّح رأى الأبواب.
   ───────────────────────────────────────────────────────────── */

const NAV_DOORS = [
  {
    key: 'day',
    label: 'يومي',
    hint: 'ما حال السماء الآن، وما يصلح لهذا اليوم',
    items: [
      ['/bulletin.html', 'النشرة اليومية', 'منزلة القمر وأوقات اليوم'],
      ['/monthly.html', 'النشرة الشهرية', 'أحداث الشهر كلّه'],
      ['/hours.html', 'ساعات الكواكب', 'لكل ساعة كوكب وطبع'],
      ['/ephemeris.html', 'مواقع الكواكب', 'جدول المواقع في أي لحظة'],
    ],
  },
  {
    key: 'me',
    label: 'خريطتي',
    hint: 'مولدك بثلاث مدارس: عربية وهندية وصينية',
    items: [
      ['/chart.html', 'خريطة الميلاد', 'الطالع والكواكب والقراءة'],
      ['/jyotish.html', 'الخريطة الهندية', 'الجيوتِش: منازل القمر وفترات العمر'],
      ['/bazi.html', 'الأعمدة الصينية', 'البازي: ثمانية حروف وميزان العناصر'],
      ['/synastry.html', 'التوافق', 'خريطتان معًا وثلاثة موازين'],
      ['/timelords.html', 'أرباب الأزمنة', 'أيّ فترة تعيش الآن'],
      ['/salts.html', 'أملاح المولد', 'شوسلر وكيري — تاريخُ فكرة لا دواء'],
      ['/astromap.html', 'خرائط الأرض', 'أين تقع كواكبك على وجه الأرض'],
      ['/figures.html', 'خرائط المشاهير', 'مواليد الأعلام بما يصحّ بالتاريخ وحده'],
      ['/origins.html', 'الأصول', 'من أين جاءت البروج والوجوه — تاريخٌ موثّق'],
    ],
  },
  {
    key: 'do',
    label: 'قراري',
    hint: 'متى أفعل، وهل أفعل',
    items: [
      ['/elections.html', 'متى أفعل؟', 'أفضل يوم وساعة لأمرك'],
      ['/horary.html', 'المسائل', 'جواب من لحظة سؤالك'],
    ],
  },
  {
    key: 'learn',
    label: 'أتعلّم',
    hint: 'المعاني والمصطلحات وأدوات المبرمجين',
    items: [
      ['/learn.html', 'تعلّم', 'البيوت والبروج والزوايا والمعجم'],
      ['/api.html', 'الواجهة البرمجية', 'ابنِ على الفَلَك، وصدّر تقويمك'],
    ],
  },
];

function buildNav() {
  const old = document.querySelector('.topbar nav');
  if (!old) return;
  const here = location.pathname.replace(/\/index\.html$/, '/') || '/';
  const isHome = here === '/' || here === '/index.html';

  const doorHtml = NAV_DOORS.map(d => {
    const active = d.items.some(([href]) => href === here);
    const links = d.items.map(([href, name, what]) =>
      `<a href="${href}" class="${href === here ? 'cur' : ''}">
         <span class="n">${name}</span><span class="w">${what}</span></a>`).join('');
    return `<div class="door ${active ? 'on' : ''}" data-door="${d.key}">
      <button type="button" aria-expanded="false" aria-controls="dm-${d.key}">
        ${d.label}<svg width="9" height="6" viewBox="0 0 10 6" aria-hidden="true">
          <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.6"
                fill="none" stroke-linecap="round"/></svg>
      </button>
      <div class="menu" id="dm-${d.key}" role="menu">
        <p class="hint">${d.hint}</p>${links}</div>
    </div>`;
  }).join('');

  const nav = document.createElement('nav');
  nav.className = 'doors';
  nav.innerHTML =
    `<a href="/" class="home ${isHome ? 'cur' : ''}">الرئيسة</a>${doorHtml}`;
  old.replaceWith(nav);

  /* زرّ الجوّال */
  const bar = document.querySelector('.topbar');
  if (bar && !bar.querySelector('.burger')) {
    const b = document.createElement('button');
    b.className = 'burger';
    b.type = 'button';
    b.setAttribute('aria-label', 'افتح قائمة التصفّح');
    b.setAttribute('aria-expanded', 'false');
    b.innerHTML = '<span></span><span></span><span></span>';
    b.onclick = () => {
      const open = bar.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
      b.setAttribute('aria-label', open ? 'أغلق قائمة التصفّح' : 'افتح قائمة التصفّح');
    };
    bar.insertBefore(b, bar.querySelector('nav'));
  }

  /* فتح الأبواب: بالضغط لا بالمرور — فالمرور لا وجود له على اللمس */
  nav.querySelectorAll('.door > button').forEach(btn => {
    btn.onclick = e => {
      e.stopPropagation();
      const door = btn.parentElement;
      const wasOpen = door.classList.contains('open');
      nav.querySelectorAll('.door').forEach(d => {
        d.classList.remove('open');
        d.querySelector('button').setAttribute('aria-expanded', 'false');
      });
      if (!wasOpen) {
        door.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    };
  });
  document.addEventListener('click', () => {
    nav.querySelectorAll('.door.open').forEach(d => {
      d.classList.remove('open');
      d.querySelector('button').setAttribute('aria-expanded', 'false');
    });
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    nav.querySelectorAll('.door.open').forEach(d => d.classList.remove('open'));
    document.querySelector('.topbar')?.classList.remove('open');
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', buildNav);
} else {
  buildNav();
}
