# -*- coding: utf-8 -*-
"""
معايرة اليوغات: كم خريطة تحمل كلَّ واحدة؟

كتب الجيوتِش تصف اليوغات وصف النوادر: «صاحبها ملك، ومَن وُلد بها
ساد قومه». والحساب يقول شيئًا آخر: راجا يوغا تقع في أكثر من نصف
الخرائط، وبودهاديتْيا في نحو ستّين بالمئة — لأن عطارد لا يفارق
الشمس أكثر من ثمانٍ وعشرين درجة، فكثيرًا ما يقعان في برج واحد.

**فما العمل؟** لا نحذف اليوغة — فهي منصوصة ولها معناها. ولا نُشدّد
شرطها حتى تندر — فذلك تحريف. وإنما **نقول للقارئ كم تقع**:

    «راجا يوغا — وتحملها ٥٦٪ من الخرائط.»

فيعرف من رآها في خريطته أنها ليست بشارة تخصّه وحده، ويعرف من رأى
هَمْسا يوغا (٦٪) أنه أمام شيء أندر. وهذا أنفع من الوعد، وأصدق.

    python tools/calibrate_yogas.py
"""
import os
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import jyotish as jy   # noqa: E402

PLACES = [
    (28.61, 77.21, "Asia/Kolkata"), (19.08, 72.88, "Asia/Kolkata"),
    (13.08, 80.27, "Asia/Kolkata"), (33.51, 36.28, "Asia/Damascus"),
    (30.04, 31.24, "Africa/Cairo"), (41.01, 28.98, "Europe/Istanbul"),
    (48.86, 2.35, "Europe/Paris"), (59.33, 18.07, "Europe/Stockholm"),
    (-1.29, 36.82, "Africa/Nairobi"), (-34.60, -58.38,
                                       "America/Argentina/Buenos_Aires"),
]
N = 3000


def main():
    rnd = random.Random(20260803)
    tally, total = {}, 0
    for i in range(N):
        lat, lon, tz = PLACES[i % len(PLACES)]
        when = datetime(rnd.randint(1935, 2015), rnd.randint(1, 12),
                        rnd.randint(1, 28), rnd.randint(0, 23),
                        rnd.randint(0, 59), tzinfo=ZoneInfo(tz))
        try:
            c = jy.compute(when, lat, lon, "lahiri", tz)
            names = {y["name"] for y in jy.yogas(c)}
        except Exception:
            continue
        total += 1
        for n in names:
            tally[n] = tally.get(n, 0) + 1
        if (i + 1) % 500 == 0:
            print(f"  … {i + 1}/{N}", file=sys.stderr)

    print(f"\n# نسبة الخرائط التي تحمل كل يوغا — من {total} خريطة")
    print(f"# في عشر مدن بين الهند وأوروبا وإفريقيا وأمريكا، ١٩٣٥–٢٠١٥.")
    print("# مولَّدة بـ tools/calibrate_yogas.py — أعِد توليدها إن")
    print("# تغيّرت شروط اليوغات، وإلا كذبت النسبة.")
    print("YOGA_FREQUENCY = {")
    for n, c in sorted(tally.items(), key=lambda x: -x[1]):
        print(f'    "{n}": {round(100 * c / total, 1)},')
    print("}")
    print(f"\n# غير المذكور لم يقع في العيّنة كلّها (أندر من "
          f"{round(100 / total, 2)}٪).", file=sys.stderr)


if __name__ == "__main__":
    main()
