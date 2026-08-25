# -*- coding: utf-8 -*-
"""
نسخةُ القاموس للمقياس — `tools/.i18n_fixture.json`

    python tools/i18n_fixture.py en

يكتب ما يردّه `/api/i18n` و`/api/glossary` في ملفٍّ واحد، ليقرأه
`tools/i18n_seen.js` بلا خادم. **فيُقاس بما يُخدَم به الزائر لا
بنسخةٍ مكتوبةٍ بيدٍ ثانية** — ونسختان لشيءٍ واحد تفترقان.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from falak import glossary_i18n, i18n, interpret  # noqa: E402

lang = sys.argv[1] if len(sys.argv) > 1 else "en"

out = {
    "i18n": {
        "dict": i18n.dict_for(lang),
        "vocab": i18n.vocab_for(lang),
        "vocab_max": i18n.VOCAB_MAX,
        "partial": i18n.PARTIAL.get(lang, ""),
    },
    # **ويُحاكى المسار كما يخدم**: المعجم بلسان الصفحة لا بالعربية،
    # وإلّا قِيست صفحةٌ إنجليزية بمعجمٍ لا تُخدَم به.
    "glossary": glossary_i18n.terms_for(lang, interpret.GLOSSARY),
}

p = os.path.join(ROOT, "tools", ".i18n_fixture.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"✓ {p}  ({len(out['i18n']['dict'])} مفتاحًا، "
      f"{len(out['glossary'])} مصطلحًا)")
