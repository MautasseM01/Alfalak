# -*- coding: utf-8 -*-
"""
التوقيت التاريخي — أكبر مصدر خطأ في خرائط الميلاد.

ثلاث مشكلات تُعالج هنا:
  ١. التوقيت الصيفي التاريخي: كل بلد غيّر قواعده مرارًا. مكتبة المناطق الزمنية
     (IANA tzdata) تحفظ هذه التواريخ، فنعتمد عليها بدل فرض إزاحة ثابتة.
  ٢. الساعات الملتبسة والمعدومة: ليلة تأخير الساعة تتكرّر ساعة كاملة مرّتين،
     وليلة تقديمها تُحذف ساعة لا وجود لها. نكشفهما ونحذّر.
  ٣. ما قبل التوقيت القياسي: قبل أن تعتمد البلاد التوقيت القياسي كانت الساعة
     شمسية محلّية خالصة (LMT). نحسبها من خط الطول ونُعلم المستخدم.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# قبل هذه السنة يغلب أن يكون التوقيت شمسيًّا محلّيًّا لا قياسيًّا
STANDARD_TIME_ERA = 1900


def _offset(dt_naive: datetime, tz: ZoneInfo, fold: int):
    aware = dt_naive.replace(tzinfo=tz, fold=fold)
    return aware.utcoffset(), aware


def lmt_offset(lon: float) -> timedelta:
    """التوقيت المحلّي الحقيقي: أربع دقائق لكل درجة من خط الطول."""
    return timedelta(seconds=round(lon * 240.0))


def resolve(dt_naive: datetime, tzname: str, lon: float) -> dict:
    """
    يُحوّل وقتًا محلّيًّا مجرّدًا إلى وقت مُدرك، مع بيان ما جرى.

    يُرجع:
      when      الوقت المُدرك النهائي
      utc       ما يقابله بالتوقيت العالمي
      offset    الإزاحة المطبَّقة
      mode      standard | lmt
      warnings  قائمة تحذيرات بالعربية
      notes     ملاحظات تفسيرية
    """
    warnings, notes = [], []
    tz = ZoneInfo(tzname)

    # ── ما قبل التوقيت القياسي ──
    if dt_naive.year < STANDARD_TIME_ERA:
        off = lmt_offset(lon)
        when = dt_naive.replace(tzinfo=timezone(off))
        notes.append(
            f"التاريخ سابق لاعتماد التوقيت القياسي، فحُسب بالتوقيت الشمسي المحلّي "
            f"لخط الطول {lon:.2f}° (إزاحة {_fmt_off(off)}).")
        return {"when": when, "utc": when.astimezone(timezone.utc),
                "offset": off, "offset_text": _fmt_off(off),
                "mode": "lmt", "tz": tzname,
                "warnings": warnings, "notes": notes, "is_dst": False}

    # ── الساعات المعدومة والملتبسة ──
    off0, aware0 = _offset(dt_naive, tz, 0)
    off1, aware1 = _offset(dt_naive, tz, 1)

    # اختبار الرجوع: إن لم يعُد الوقت إلى نفسه فهو وقت لم يوجد أصلًا
    roundtrip = aware0.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None)
    nonexistent = roundtrip != dt_naive
    ambiguous = (not nonexistent) and off0 != off1

    if nonexistent:
        jump = _fmt_off(abs(off1 - off0))
        warnings.append(
            f"هذه الساعة لم توجد في ذلك اليوم: قُدِّمت الساعة {jump} للتوقيت الصيفي "
            f"فقفزت فوقها. راجع ساعة الميلاد المسجّلة — الأرجح أنها قبل التقديم أو بعده.")
    elif ambiguous:
        warnings.append(
            f"هذه الساعة تكرّرت مرّتين في ذلك اليوم عند العودة من التوقيت الصيفي "
            f"(مرّة بإزاحة {_fmt_off(off0)} ومرّة بإزاحة {_fmt_off(off1)}). "
            f"اعتمدنا الأولى. إن كانت الولادة بعد إعادة الساعة فالطالع سيختلف.")

    when = dt_naive.replace(tzinfo=tz)
    off = when.utcoffset()
    is_dst = bool(when.dst())
    if is_dst:
        notes.append(f"كان التوقيت الصيفي ساريًا في {tzname} بذلك التاريخ، "
                     f"والإزاحة المطبَّقة {_fmt_off(off)}.")
    else:
        notes.append(f"الإزاحة المطبَّقة {_fmt_off(off)} بتوقيت {tzname}.")

    # فرق التوقيت القياسي عن الشمسي المحلّي — مفيد لمن يريد الساعة الحقيقية
    delta = off - lmt_offset(lon)
    if abs(delta.total_seconds()) > 1800:
        notes.append(
            f"التوقيت القياسي هنا يسبق الشمس المحلّية بـ {_fmt_off(delta)} "
            f"— أي أن الظهر الفلكي لا يوافق الساعة ١٢.")

    return {"when": when, "utc": when.astimezone(timezone.utc),
            "offset": off, "offset_text": _fmt_off(off),
            "mode": "standard", "tz": tzname, "is_dst": is_dst,
            "ambiguous": ambiguous, "nonexistent": nonexistent,
            "warnings": warnings, "notes": notes}


def _fmt_off(td: timedelta) -> str:
    total = int(td.total_seconds())
    sign = "+" if total >= 0 else "−"
    total = abs(total)
    return f"{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"


def describe(res: dict) -> str:
    """سطر واحد يصف ما جرى، للعرض تحت الخريطة."""
    if res["mode"] == "lmt":
        return f"توقيت شمسي محلّي {res['offset_text']}"
    tag = "توقيت صيفي" if res["is_dst"] else "توقيت قياسي"
    return f"{tag} {res['offset_text']} — {res['tz']}"
