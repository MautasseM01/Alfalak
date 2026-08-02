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
            font-family="Noto Kufi Arabic, system-ui, sans-serif" role="img"
            aria-label="العجلة المزدوجة — خريطتان متراكبتان">${g}</svg>`;
}
