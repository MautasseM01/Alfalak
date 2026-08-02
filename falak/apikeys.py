# -*- coding: utf-8 -*-
"""
مفاتيح الوصول — بلا قاعدة بيانات.

المشروع كلّه دالّة بلا خادم ولا قاعدة بيانات، ولا نريد إدخال واحدة
لأجل المفاتيح. فالمفتاح هنا **موقَّع لا مخزَّن**: يحمل في نفسه
مستواه وتاريخ انتهائه، وتوقيعٌ بمفتاح سرّي يُثبت أننا أصدرناه.
فيُتحقَّق منه بالحساب لا بالبحث.

**وهذا مقايضة نقولها ولا نُخفيها**: ما لا يُخزَّن لا يُلغى فرديًّا.
فإن تسرّب مفتاح فليس أمامنا إلا انتظار انتهائه، أو تدوير المفتاح
السرّي فتسقط المفاتيح كلّها معًا. ولذلك:
  * أقصى عمر للمفتاح سنة، فالتسريب لا يدوم أبدًا.
  * وقائمة منع صغيرة في متغيّر بيئة، للحالات المستعجلة.

فإن كبر الاستعمال حتى صار هذا ضيقًا، فالحلّ عندئذ قاعدة بيانات —
لا حيلة أخرى.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import date as _date, datetime, timedelta, timezone

UTC = timezone.utc

# مستويات الوصول: الاسم، الطلبات في الدقيقة، أقصى مدى بحث، الوصف
TIERS = {
    "free": {"name": "مفتوح", "rpm": 20, "max_days": 90,
             "note": "بلا تسجيل. يكفي للتجريب والمواقع الصغيرة."},
    "basic": {"name": "أساسي", "rpm": 120, "max_days": 200,
              "note": "لتطبيق أو موقع يخدم جمهورًا."},
    "pro": {"name": "موسّع", "rpm": 600, "max_days": 400,
            "note": "للاستعمال الكثيف والتقاويم المشتركة."},
}
DEFAULT_TIER = "free"

_DEV_SECRET = "falak-dev-secret-غير-صالح-للنشر"


def _secret() -> bytes:
    s = os.environ.get("FALAK_API_SECRET") or _DEV_SECRET
    return s.encode("utf-8")


def is_dev_secret() -> bool:
    """هل ما زلنا على المفتاح السرّي التجريبي؟ يُنبَّه عليه في /health."""
    return not os.environ.get("FALAK_API_SECRET")


def _blocked() -> set:
    raw = os.environ.get("FALAK_BLOCKED_KEYS", "")
    return {x.strip() for x in raw.split(",") if x.strip()}


def _b32(b: bytes) -> str:
    return base64.b32encode(b).decode("ascii").rstrip("=").lower()


def _sign(payload: str) -> str:
    mac = hmac.new(_secret(), payload.encode("utf-8"), hashlib.sha256).digest()
    return _b32(mac[:15])


def issue(tier: str = DEFAULT_TIER, days: int = 365,
          label: str = "") -> dict:
    """
    يُصدر مفتاحًا. صيغته: falak_<المستوى>_<الانتهاء>_<التوقيع>

    والانتهاء داخل المفتاح لا خارجه، فيُقرأ بلا استعلام.
    """
    if tier not in TIERS:
        raise ValueError(f"مستوى غير معروف: {tier}")
    days = max(1, min(int(days), 366))
    exp = (datetime.now(UTC).date() + timedelta(days=days))
    body = f"{tier}.{exp.isoformat()}.{_b32(os.urandom(6))}"
    key = f"falak_{body}_{_sign(body)}"
    return {
        "key": key, "tier": tier, "tier_name": TIERS[tier]["name"],
        "expires": exp.isoformat(), "label": label,
        "rpm": TIERS[tier]["rpm"], "max_days": TIERS[tier]["max_days"],
        "warning": ("هذا المفتاح لا يُخزَّن عندنا ولا يمكن استرجاعه. "
                    "احفظه الآن.")
        + (" وتنبيه: الخادم يعمل بمفتاح سرّي تجريبي، فالمفاتيح "
           "المُصدَرة الآن ستسقط عند النشر." if is_dev_secret() else ""),
    }


def verify(key: str | None) -> dict:
    """
    يتحقّق من المفتاح. يُرجع دائمًا مستوًى صالحًا للعمل —
    فغياب المفتاح ليس خطأً، بل هو المستوى المفتوح.
    """
    if not key:
        return {"valid": True, "tier": DEFAULT_TIER, "anonymous": True,
                **TIERS[DEFAULT_TIER]}

    key = key.strip()
    if key in _blocked():
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": "هذا المفتاح موقوف.", **TIERS[DEFAULT_TIER]}

    if not key.startswith("falak_") or key.count("_") < 2:
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": "صيغة المفتاح غير صحيحة.", **TIERS[DEFAULT_TIER]}

    rest = key[len("falak_"):]
    body, _, sig = rest.rpartition("_")
    if not hmac.compare_digest(sig, _sign(body)):
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": "توقيع المفتاح لا يُطابق.", **TIERS[DEFAULT_TIER]}

    try:
        tier, exp_s, _rand = body.split(".", 2)
        exp = _date.fromisoformat(exp_s)
    except ValueError:
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": "محتوى المفتاح تالف.", **TIERS[DEFAULT_TIER]}

    if tier not in TIERS:
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": "مستوى غير معروف.", **TIERS[DEFAULT_TIER]}

    if exp < datetime.now(UTC).date():
        return {"valid": False, "tier": DEFAULT_TIER, "anonymous": False,
                "error": f"انتهى المفتاح في {exp_s}.", **TIERS[DEFAULT_TIER]}

    return {"valid": True, "tier": tier, "anonymous": False,
            "expires": exp_s, **TIERS[tier]}


# ══════════════════════════════════════════════════════════════
# حدّ الاستعمال
#
# **بصراحة**: هذا العدّاد في ذاكرة النسخة الواحدة. والدالّة بلا
# خادم تُشغَّل نسخًا متعدّدة، فكلٌّ تعدّ وحدها — أي إن الحدّ الفعليّ
# قد يبلغ أضعاف المعلن حين تتوزّع الطلبات.
#
# فهو إذن **مُهدّئ لا حارس**: يمنع الحلقة المنفلتة من عميل واحد،
# ولا يمنع هجومًا مقصودًا. والحارس الحقيقي يحتاج مخزنًا مشتركًا،
# ولا نُدخله ما لم يلزم. قلنا هذا في التوثيق أيضًا، فلا يبني عليه
# أحد ما لا يحتمله.
# ══════════════════════════════════════════════════════════════
_HITS: dict = {}


def check_rate(ident: str, rpm: int, now: float | None = None) -> dict:
    import time
    now = now if now is not None else time.time()
    window = 60.0
    bucket = _HITS.setdefault(ident, [])
    cut = now - window
    bucket[:] = [t for t in bucket if t > cut]
    if len(_HITS) > 5000:
        _HITS.clear()
    if len(bucket) >= rpm:
        oldest = min(bucket)
        return {"ok": False, "remaining": 0,
                "retry_after": max(1, int(oldest + window - now) + 1),
                "limit": rpm}
    bucket.append(now)
    return {"ok": True, "remaining": rpm - len(bucket), "limit": rpm,
            "retry_after": 0}
