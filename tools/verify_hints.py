# -*- coding: utf-8 -*-
"""
يُصدِّر المعجم وخريطةً حقيقية إلى ملفّ، ثم يُشغّل فحص الواجهة بـ node.

    python tools/verify_hints.py

الفكرة: النصوص والحسابات مصدرها بايثون، والفحص مصدره المتصفّح —
فنجعل بايثون يُخرج ما يحتاجه المتصفّح بدل أن نكتب نسخةً ثانية من
البيانات في JS، فتفترق النسختان ويظنّ الاختبار أنه يفحص شيئًا وهو
يفحص نسخةً قديمة. **هذا خطأ وقعنا فيه من قبل في مواضع أخرى.**
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from api.index import dispatch  # noqa: E402
from falak import interpret  # noqa: E402

Q = {"date": ["1990-05-17"], "time": ["08:30"], "city": ["حلب"], "system": ["whole"]}


def main() -> int:
    fixture = {
        "glossary": interpret.GLOSSARY,
        "chart": dispatch("/api/chart", Q),
        "deep": dispatch("/api/depth", Q),
    }
    path = os.path.join(HERE, ".hint_fixture.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fixture, f, ensure_ascii=False)

    print(f"المعجم: {len(fixture['glossary'])} مصطلحًا · "
          f"الخريطة: {len(fixture['chart']['bodies'])} جِرمًا، "
          f"{len(fixture['chart']['aspects'])} زاوية")

    node = shutil.which("node")
    if not node:
        print("لم يُعثر على node — فحص الواجهة يحتاجه.")
        return 2

    env = dict(os.environ)
    try:
        code = subprocess.call([node, os.path.join(HERE, "verify_hints.js")],
                               cwd=ROOT, env=env)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass   # ملفّ مؤقّت لا غير؛ وهو في .gitignore
    return code


if __name__ == "__main__":
    raise SystemExit(main())
