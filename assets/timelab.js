/* ══════════════════════════════════════════════════════════════════
   آلة الزمن — عجلةٌ تتحرّك بالزمن

   تُريك أين ترى كلَّ جرمٍ من البروج في لحظةٍ تختارها، ثم تُقدّم
   الزمن أو تؤخّره بالدقيقة أو الساعة أو اليوم أو السنة فترى
   الحركة بعينك.

   ── **ولا تفترض شكلًا للأرض ولا مركزًا للعالم** ──────────────

   المرسومُ هنا **طولٌ في دائرة البروج**: أي في أيّ جهةٍ من
   الفَلَك ترى الجرم. وهذا ما يُرصَد ويُقاس، وأيُّ نموذجٍ للعالم
   فعليه أن يُخرِجه كما يُرى. فالعجلةُ ليست دعوى، إنّما **جدولُ
   ما ستراه**، ومن شاء فليخرج ليلًا وليمتحنه.

   ── ولماذا لا تُطلب لقطةٌ لكلّ إطار ──────────────────────────

   لأنّ الخادم بلا حالة، ونداءُ كلّ إطارٍ ثلاثون نداءً في الثانية.
   فتُطلب المدّةُ كلُّها مرّةً (`/api/track`) وتُحرَّك من الذاكرة.
   **والتحريكُ في المتصفّح لا يكلّف نداءً واحدًا.**
   ══════════════════════════════════════════════════════════════════ */

const TL_SIGN_SYM = '♈♉♊♋♌♍♎♏♐♑♒♓';

/* الألوان تُقرأ من الصفحة لا تُكتَب هنا، فتتبع السمة إن تبدّلت */
function tlColor(name, fallback) {
  const v = getComputedStyle(document.documentElement)
    .getPropertyValue(name).trim();
  return v || fallback;
}

class TimeLab {
  constructor(canvas, opts = {}) {
    this.cv = canvas;
    this.ctx = canvas.getContext('2d');
    this.data = null;
    this.i = 0;
    this.playing = false;
    this.fps = opts.fps || 12;
    this.trail = opts.trail !== false;
    this.onFrame = opts.onFrame || (() => {});
    this._raf = null;
    this._last = 0;
    window.addEventListener('resize', () => this.draw());
  }

  load(data) {
    this.data = data;
    this.i = 0;
    this.draw();
    return this;
  }

  /* موضعُ اللقطة: صفر إلى واحد */
  seek(frac) {
    if (!this.data) return;
    this.i = Math.max(0, Math.min(this.data.count - 1,
      Math.round(frac * (this.data.count - 1))));
    this.draw();
  }

  step(n) {
    if (!this.data) return;
    this.i = Math.max(0, Math.min(this.data.count - 1, this.i + n));
    this.draw();
  }

  play() {
    if (this.playing || !this.data) return;
    this.playing = true;
    this._last = 0;
    const tick = (ts) => {
      if (!this.playing) return;
      if (!this._last || ts - this._last >= 1000 / this.fps) {
        this._last = ts;
        /* **يلتفّ عند الطرف ولا يقف.** التحريك عرضٌ متّصل،
           ووقوفُه عند آخر لقطةٍ يقطع النظر بلا سبب. */
        this.i = (this.i + 1) % this.data.count;
        this.draw();
      }
      this._raf = requestAnimationFrame(tick);
    };
    this._raf = requestAnimationFrame(tick);
  }

  pause() {
    this.playing = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = null;
  }

  toggle() { this.playing ? this.pause() : this.play(); }

  /* وقتُ اللقطة الحالية */
  timeAt(i) {
    const d = this.data;
    if (!d) return null;
    const t0 = new Date(d.start).getTime();
    return new Date(t0 + (i == null ? this.i : i) * d.step_min * 60000);
  }

  /* ── الرسم ─────────────────────────────────────────────── */
  draw() {
    const d = this.data, ctx = this.ctx, cv = this.cv;
    if (!d) return;

    /* **القياس يتبع كثافة الشاشة.** لولا ذلك لخرج الرسم
       مشوَّشًا على الشاشات عالية الكثافة، وهي أكثر الهواتف. */
    const dpr = window.devicePixelRatio || 1;
    const size = Math.min(cv.clientWidth, cv.clientHeight || cv.clientWidth);
    if (cv.width !== size * dpr) {
      cv.width = cv.height = Math.round(size * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size, size);

    const cx = size / 2, cy = size / 2;
    const rOut = size * 0.46, rIn = size * 0.36, rBody = size * 0.30;

    const gold = tlColor('--gold', '#d9b45b');
    const dim = tlColor('--gold-dim', '#8a7434');
    const line = tlColor('--line', '#243049');
    const text = tlColor('--text', '#e8ecf6');
    const muted = tlColor('--muted', '#8fa5d8');
    const neg = tlColor('--neg', '#c96a6a');

    /* **صفرُ الحمل إلى اليمين، والدورانُ عكسَ عقارب الساعة** —
       وهو اصطلاح العجلة في كل كتب الصناعة، وعليه `wheel.js`
       في هذا الموقع. **واصطلاحان في موقعٍ واحد يُربكان.** */
    const ang = lon => -(lon * Math.PI / 180);
    const at = (lon, r) => [cx + r * Math.cos(ang(lon)),
                            cy + r * Math.sin(ang(lon))];

    /* حلقةُ البروج */
    ctx.strokeStyle = line; ctx.lineWidth = 1;
    [rOut, rIn, rBody].forEach(r => {
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
    });
    for (let s = 0; s < 12; s++) {
      const a = s * 30;
      ctx.strokeStyle = line;
      ctx.beginPath();
      ctx.moveTo(...at(a, rIn)); ctx.lineTo(...at(a, rOut)); ctx.stroke();
      const [tx, ty] = at(a + 15, (rIn + rOut) / 2);
      ctx.fillStyle = dim;
      ctx.font = `${Math.round(size * 0.042)}px serif`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(TL_SIGN_SYM[s], tx, ty);
    }

    /* أثرُ المسار: اللقطاتُ السابقة باهتة — **فيُرى الرجوع** */
    if (this.trail && this.i > 0) {
      const from = Math.max(0, this.i - 120);
      for (let b = 0; b < d.bodies.length; b++) {
        ctx.strokeStyle = gold;
        for (let k = from; k < this.i; k++) {
          const v = d.lon[k][b], w = d.lon[k + 1] && d.lon[k + 1][b];
          if (v == null || w == null) continue;
          /* الفرقُ الملتفّ يُقطَع ولا يُرسَم خطًّا عبر العجلة */
          let dd = ((w - v + 540) % 360) - 180;
          if (Math.abs(dd) > 20) continue;
          ctx.globalAlpha = 0.05 + 0.25 * ((k - from) / (this.i - from || 1));
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.moveTo(...at(v, rBody)); ctx.lineTo(...at(w, rBody));
          ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
    }

    /* الأجرام في اللقطة الحالية */
    const mask = d.retro[this.i] || 0;
    const placed = [];
    for (let b = 0; b < d.bodies.length; b++) {
      const L = d.lon[this.i][b];
      if (L == null) continue;
      /* **تفريقُ المتزاحمَين**: جرمان على درجةٍ واحدة يتراكبان
         فلا يُقرأ أيُّهما. فيُزاح الثاني إلى الداخل قليلًا. */
      let r = rBody;
      while (placed.some(p => Math.abs(((p.L - L + 540) % 360) - 180) < 7
                             && Math.abs(p.r - r) < 6)) r -= size * 0.036;
      placed.push({ L, r });

      const [x, y] = at(L, r);
      const retro = (mask >> b) & 1;
      ctx.fillStyle = retro ? neg : text;
      ctx.font = `${Math.round(size * 0.05)}px serif`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(d.symbols[b], x, y);
      if (retro) {
        ctx.fillStyle = neg;
        ctx.font = `${Math.round(size * 0.026)}px sans-serif`;
        ctx.fillText('ر', x + size * 0.026, y - size * 0.026);
      }
    }

    /* الأوتاد، إن حُسبت */
    if (d.ang && d.ang[this.i] && d.ang[this.i][0] != null) {
      const [asc, mc] = d.ang[this.i];
      ctx.strokeStyle = gold; ctx.lineWidth = 1.6;
      ctx.setLineDash([4, 4]);
      [[asc, 'ASC'], [mc, 'MC']].forEach(([v, nm]) => {
        ctx.beginPath();
        ctx.moveTo(cx, cy); ctx.lineTo(...at(v, rOut));
        ctx.stroke();
        const [lx, ly] = at(v, rOut * 1.05);
        ctx.fillStyle = gold;
        ctx.font = `${Math.round(size * 0.028)}px sans-serif`;
        ctx.fillText(nm, lx, ly);
      });
      ctx.setLineDash([]);
    }

    /* الوقتُ في القلب */
    const t = this.timeAt();
    ctx.fillStyle = muted;
    ctx.font = `${Math.round(size * 0.036)}px sans-serif`;
    ctx.fillText(t.toISOString().slice(0, 10), cx, cy - size * 0.022);
    ctx.fillStyle = dim;
    ctx.font = `${Math.round(size * 0.03)}px sans-serif`;
    ctx.fillText(t.toISOString().slice(11, 16) + ' UTC', cx, cy + size * 0.022);

    this.onFrame(this.i, t, d);
  }

  /* جدولُ اللقطة الحالية — للنصّ تحت العجلة */
  rows() {
    const d = this.data;
    if (!d) return [];
    const mask = d.retro[this.i] || 0;
    return d.bodies.map((name, b) => {
      const L = d.lon[this.i][b];
      if (L == null) return { name, text: '—' };
      const s = Math.floor((L % 360) / 30);
      const deg = L % 30;
      return {
        name, symbol: d.symbols[b], lon: L,
        sign: d.signs[s],
        text: `${Math.floor(deg)}° ${String(Math.floor((deg % 1) * 60))
          .padStart(2, '0')}′ ${d.signs[s]}`,
        retro: !!((mask >> b) & 1),
      };
    });
  }
}
