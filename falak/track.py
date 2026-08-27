# -*- coding: utf-8 -*-
"""
التتبّع: مواقعُ الأجرام في لقطاتٍ متتابعة — لآلة الزمن.

──────────────────────────────────────────────────────────────────
**لماذا لقطاتٌ كثيرة في نداءٍ واحد؟**

آلةُ الزمن تُريك السماء تتحرّك. ولو طلبت الواجهةُ لكلّ إطارٍ
نداءً لكان في الثانية ثلاثون نداءً — **ودالّةٌ بلا خادم تُشغَّل
لكلّ نداءٍ من جديد**، فيصير التحريكُ عبئًا لا ميزة، ويقف عند
حدّ الاستعمال في دقيقة.

فتُحسب المدّةُ كلُّها هنا، وتُردّ مرّةً واحدة، ويُحرِّكها
المتصفّح من ذاكرته. **ونداءٌ واحدٌ لمئتَي لقطة أرخصُ من مئتَي
نداءٍ للقطة.**

──────────────────────────────────────────────────────────────────
**ولماذا مصفوفاتٌ لا كائنات؟**

    {"الشمس": {"lon": 123.45, "retro": false}}   ← ٤٥ حرفًا للجرم
    [123.45]                                     ← ٦ أحرف

ومئتا لقطةٍ في ثلاثةَ عشرَ جرمًا. فالفرق بين ردٍّ في مئة كيلوبايت
وردٍّ في عشرين. **والأسماء تُرسَل مرّةً في الرأس، لا مع كل رقم.**

──────────────────────────────────────────────────────────────────
**والرجوعُ يُؤخَذ من السرعة لا يُستنتَج من الفرق**

الفرقُ بين لقطتين يلتفّ عند ٣٦٠→٠ فيبدو الجرمُ راجعًا وهو مستقيم.
والمكتبةُ تردّ السرعة اليومية مع الطول في نداءٍ واحد
(`FLG_SPEED`)، فتُؤخَذ منها. **وما يُعرَف بلا استنتاج لا يُستنتَج.**
"""
from __future__ import annotations

from datetime import datetime, timedelta

import swisseph as swe

from .chart import BODIES, BODY_SYMBOL, HOUSE_SYSTEMS
from .ephem import FLAGS, SIGNS, UTC, to_jd

# أقصى ما يُحسَب في نداء — حدٌّ يحمي الدالّة من طلبٍ مفتوح
MAX_FRAMES = 400

# خطواتٌ مسمّاة، بالدقائق. و«الشهر» و«السنة» تقريبيّان عمدًا:
# التحريكُ عرضٌ لا تقويم، والدقّةُ في اللقطة لا في طول الخطوة.
STEPS = {
    "دقيقة": 1,
    "ساعة": 60,
    "يوم": 1440,
    "أسبوع": 10080,
    "شهر": 43800,          # ٣٠٫٤٤ يومًا
    "سنة": 525960,         # ٣٦٥٫٢٥ يومًا
}


def _bodies(names: list[str] | None) -> list[tuple[str, int, str]]:
    pick = []
    want = set(names) if names else None
    for name, code, sym, _major, _cls in BODIES:
        if want is None or name in want:
            pick.append((name, code, sym))
    return pick


def frames(start: datetime, step_min: float, count: int,
           bodies: list[str] | None = None,
           lat: float | None = None, lon: float | None = None,
           system: str = "whole") -> dict:
    """
    لقطاتٌ متتابعة من `start`، كلُّ لقطةٍ بعد `step_min` دقيقة.

    ويُردّ لكل لقطة:
      · `lon`   — أطوال الأجرام بالترتيب نفسه في `bodies`
      · `retro` — قناعُ بتّاتٍ للرجوع (بِتٌّ لكل جرم)
      · `ang`   — الطالع ووسط السماء، إن أُعطي موضع

    **وقناعُ البتّات لا قائمةُ منطق**: ثلاثةَ عشرَ `false` في كل
    لقطةٍ تُثقل الردّ بلا معنى، والعددُ الواحد يحملها كلَّها.
    """
    picks = _bodies(bodies)
    count = max(1, min(int(count), MAX_FRAMES))
    step = timedelta(minutes=float(step_min))

    lons: list[list[float]] = []
    retro: list[int] = []
    angs: list[list[float]] = []

    want_ang = lat is not None and lon is not None
    # **و`HOUSE_SYSTEMS` قيمتُها كائنٌ لا رمز.** أخذتُها رمزًا
    # فردّت `swe.houses` خطأً ابتلعه `except`، فخرجت الأوتاد
    # `None` والردُّ يبدو تامًّا. فيُؤخذ `code` منها صراحةً.
    hsys = HOUSE_SYSTEMS.get(system, HOUSE_SYSTEMS["whole"])["code"]

    t = start
    for _ in range(count):
        jd = to_jd(t)
        row, mask = [], 0
        for i, (_name, code, _sym) in enumerate(picks):
            try:
                res = swe.calc_ut(jd, code, FLAGS)[0]
                row.append(round(res[0] % 360.0, 3))
                if res[3] < 0:                 # السرعة سالبة = راجع
                    mask |= (1 << i)
            except Exception:
                # **جرمٌ لا يُحسَب لا يُسقط اللقطة كلَّها.** خيرون
                # يحتاج ملفًّا اختياريًّا، وغيابُه متوقَّع.
                row.append(None)
        lons.append(row)
        retro.append(mask)
        if want_ang:
            try:
                _c, asc = swe.houses(jd, lat, lon, hsys)
                angs.append([round(asc[0] % 360.0, 3),
                             round(asc[1] % 360.0, 3)])
            except Exception as exc:
                # **ولا يُبتلَع الخطأ صامتًا.** ابتلعتُه أوّلًا
                # فخرجت الأوتاد فارغةً والردُّ يبدو سليمًا، ولم
                # أعلم إلّا بالنظر في الأرقام. فليُذكر سببُه.
                angs.append([None, None])
                out_err = str(exc)
                if not hasattr(frames, "_warned"):
                    frames._warned = out_err
        t += step

    out = {
        "start": start.astimezone(UTC).isoformat(),
        "step_min": step_min,
        "count": count,
        "bodies": [n for n, _, _ in picks],
        "symbols": [s for _, _, s in picks],
        "signs": SIGNS,
        "lon": lons,
        "retro": retro,
        "steps": STEPS,
    }
    if want_ang:
        out["ang"] = angs
        out["ang_names"] = ["الطالع", "وسط السماء"]
        if angs and angs[0][0] is None:
            out["ang_error"] = getattr(frames, "_warned",
                                       "تعذّر حساب الأوتاد لهذا الموضع.")
    return out
