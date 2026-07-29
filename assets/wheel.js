/* رسم الخريطة الدائرية — SVG خالص بلا مكتبات */

const SIGN_SYMBOLS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
const SIGN_NAMES = ['الحمل','الثور','الجوزاء','السرطان','الأسد','العذراء',
                    'الميزان','العقرب','القوس','الجدي','الدلو','الحوت'];
const ELEM_COLOR = { 0:'#e08a7d', 1:'#c9a227', 2:'#8fa5d8', 3:'#5fc7a1' };
const ASPECT_COLOR = { 'إيجابية':'#5fc7a1', 'سلبية':'#e08a7d', 'محايدة':'#d9b45b' };

function wheelSVG(c, opts = {}) {
  const S = opts.size || 620;
  const cx = S / 2, cy = S / 2;
  const R = {
    zodiacOut: S * .470, zodiacIn: S * .400,
    mansionOut: S * .400, mansionIn: S * .372,
    houseOut: S * .372, houseIn: S * .290,
    planet: S * .335, aspect: S * .285,
  };
  const asc = c.angles['الطالع'].lon;
  const showMansions = opts.mansions !== false;

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
  for (let i = 0; i < 12; i++) {
    const start = i * 30;
    g += `<path d="${arcPath(start, start + 30, (R.zodiacOut + R.zodiacIn) / 2)}" fill="none"
           stroke="${ELEM_COLOR[i % 4]}" stroke-width="${R.zodiacOut - R.zodiacIn}" opacity=".13"/>`;
    g += line(start, R.zodiacIn, R.zodiacOut, 'stroke="var(--line2)" stroke-width="1"');
    const [tx, ty] = P(start + 15, (R.zodiacOut + R.zodiacIn) / 2);
    g += `<text x="${tx.toFixed(1)}" y="${(ty + 7).toFixed(1)}" text-anchor="middle"
           font-size="21" fill="${ELEM_COLOR[i % 4]}">${SIGN_SYMBOLS[i]}</text>`;
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
    g += `<text x="${hx.toFixed(1)}" y="${(hy + 4).toFixed(1)}" text-anchor="middle"
           font-size="11" fill="var(--muted)">${i + 1}</text>`;
  });

  /* ── الأوتاد ── */
  const axes = [['الطالع','ASC'], ['وسط السماء','MC'], ['الغارب','DSC'], ['وتد الأرض','IC']];
  axes.forEach(([k, tag]) => {
    const L = c.angles[k].lon;
    g += line(L, R.houseIn, R.zodiacOut + 4, 'stroke="var(--gold)" stroke-width="1.2" opacity=".85"');
    const [ax, ay] = P(L, R.zodiacOut + 15);
    g += `<text x="${ax.toFixed(1)}" y="${(ay + 4).toFixed(1)}" text-anchor="middle"
           font-size="10.5" font-weight="600" fill="var(--gold)">${tag}</text>`;
  });

  /* ── تفريق الكواكب المتزاحمة ── */
  const bodies = c.bodies.filter(b => b.name !== 'الذنب' || opts.tail !== false);
  const items = bodies.map(b => ({ ...b, rel: ((b.lon - asc) % 360 + 360) % 360 }))
                      .sort((a, b) => a.rel - b.rel);
  const MIN = 8;
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
  const asps = (c.aspects || []).filter(a => opts.minorLines ? true : a.major);
  let lines = '';
  asps.forEach(a => {
    if (pos[a.a] == null || pos[a.b] == null) return;
    const [x1,y1] = P(pos[a.a], R.aspect), [x2,y2] = P(pos[a.b], R.aspect);
    const col = ASPECT_COLOR[a.polarity] || 'var(--muted)';
    const w = (0.5 + a.strength * 1.6).toFixed(2);
    const op = (0.20 + a.strength * 0.55).toFixed(2);
    lines += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"
              stroke="${col}" stroke-width="${w}" opacity="${op}"
              ${a.angle === 0 ? 'stroke-dasharray="3 3"' : ''}/>`;
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
    g += `<g class="pl" data-name="${it.name}">
      <circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="12.5" fill="rgba(10,15,29,.82)" stroke="var(--line2)" stroke-width=".7"/>
      <text x="${px.toFixed(1)}" y="${(py + 6).toFixed(1)}" text-anchor="middle" font-size="16" fill="${col}">${it.symbol}</text>
      <title>${it.name} — ${it.text}${it.retro ? ' (راجع)' : ''}${it.dignity ? ' · ' + it.dignity : ''}</title>
    </g>`;
    const [dx, dy] = P(drawLon, R.planet - 25);
    g += `<text x="${dx.toFixed(1)}" y="${(dy + 3).toFixed(1)}" text-anchor="middle"
           font-size="8.5" fill="var(--muted)">${it.deg}°${it.retro ? '℞' : ''}</text>`;
  });

  return `<svg viewBox="0 0 ${S} ${S}" width="100%" xmlns="http://www.w3.org/2000/svg"
            font-family="Noto Kufi Arabic, system-ui, sans-serif" role="img"
            aria-label="الخريطة الفلكية الدائرية">${g}</svg>`;
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
