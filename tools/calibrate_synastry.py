# -*- coding: utf-8 -*-
"""
معايرة موازين التوافق.

المشكلة التي وُلد منها هذا الملفّ: أوّل صياغة للدرجة قسمت صافي
الأوزان على مجموع الأوزان الممكنة، فخرجت كلّ الأزواج بين ٤٤ و٧٢
ووسيطها ٥٧. درجة تقول لكلّ الناس الشيء نفسه لا تقول شيئًا.

فالدرجة الآن **رتبة مئوية**: نُولّد آلاف الأزواج العشوائية، نحسب
صافي أوزانها، ونحفظ نقاط القطع. فإذا قيل لك «٧٨ في الميزان
العاطفي» فمعناه محدّد: صافي زواياكما يفوق ٧٨٪ من الأزواج العشوائية.

    python tools/calibrate_synastry.py

يطبع الثوابت جاهزةً للصق في falak/synastry.py.
"""
import os
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import chart, synastry as syn   # noqa: E402

# مدن متباعدة في خطوط العرض، لأن البيوت والأوتاد تتأثّر بالموضع
PLACES = [
    (33.51, 36.28, "Asia/Damascus"), (48.86, 2.35, "Europe/Paris"),
    (30.04, 31.24, "Africa/Cairo"), (24.71, 46.68, "Asia/Riyadh"),
    (41.01, 28.98, "Europe/Istanbul"), (59.33, 18.07, "Europe/Stockholm"),
    (-1.29, 36.82, "Africa/Nairobi"), (35.69, 139.69, "Asia/Tokyo"),
    (40.71, -74.01, "America/New_York"), (-34.60, -58.38, "America/Argentina/Buenos_Aires"),
]

N_CHARTS = 260        # نُولّدها مرّة، ثم نُزاوج بينها
N_PAIRS = 6000


def make_pool(seed=20260801):
    rnd = random.Random(seed)
    pool = []
    for i in range(N_CHARTS):
        lat, lon, tz = PLACES[i % len(PLACES)]
        when = datetime(rnd.randint(1940, 2010), rnd.randint(1, 12),
                        rnd.randint(1, 28), rnd.randint(0, 23),
                        rnd.randint(0, 59), tzinfo=ZoneInfo(tz))
        pool.append(chart.compute(when, lat, lon, "whole", tz))
        if (i + 1) % 40 == 0:
            print(f"  … {i + 1}/{N_CHARTS} خريطة", file=sys.stderr)
    return pool


def main():
    print("أُولّد بركة الخرائط…", file=sys.stderr)
    pool = make_pool()
    rnd = random.Random(7)
    nets = {d: [] for d in syn.CRITERIA}

    print("أُزاوج وأحسب…", file=sys.stderr)
    for k in range(N_PAIRS):
        a, b = rnd.sample(pool, 2)
        raw = syn.raw_net(a, b)
        for d, v in raw.items():
            nets[d].append(v)
        if (k + 1) % 1000 == 0:
            print(f"  … {k + 1}/{N_PAIRS} زوجًا", file=sys.stderr)

    print("\n# ثوابت المعايرة — مولَّدة بـ tools/calibrate_synastry.py")
    print(f"# {N_PAIRS} زوجًا عشوائيًّا من {N_CHARTS} خريطة في "
          f"{len(PLACES)} مدينة، ١٩٤٠–٢٠١٠.")
    print("# كل قائمة ٢١ نقطة قطع، من المئين ٠ إلى ١٠٠ بخطوة ٥.")
    print("CALIBRATION = {")
    for d, vals in nets.items():
        vals.sort()
        cuts = [round(vals[min(len(vals) - 1, int(len(vals) * p / 100))], 2)
                for p in range(0, 101, 5)]
        print(f'    "{d}": {cuts},')
    print("}")


if __name__ == "__main__":
    main()
