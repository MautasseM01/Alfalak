# -*- coding: utf-8 -*-
"""
واجهة الخادم — دالة واحدة بلا خادم تخدم كل المسارات.
تعمل على Vercel وعلى الجهاز المحلي بنفس الشيفرة.

المسارات:
  GET /api/health
  GET /api/atlas?q=دمشق
  GET /api/ephemeris?date=2026-07-28&time=12:00&tz=Asia/Damascus
  GET /api/bulletin?date=2026-07-28&city=دمشق[&tz=&lat=&lon=&shift=0]
  GET /api/chart?date=1990-05-17&time=08:30&city=دمشق[&system=whole|placidus|equal]
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import date as _date, datetime, timedelta
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from falak import atlas, bulletin, chart, config, ephem, interpret  # noqa: E402
from falak import timezone as ftz  # noqa: E402


# ── أدوات ────────────────────────────────────────────────────────
def _one(q: dict, key: str, default=None):
    v = q.get(key)
    return v[0] if v else default


class ApiError(Exception):
    def __init__(self, msg, status=400):
        super().__init__(msg)
        self.status = status


def resolve_place(q: dict):
    """يُرجع (lat, lon, tzname, label) من اسم مدينة أو من إحداثيات صريحة."""
    city = _one(q, "city")
    lat, lon, tz = _one(q, "lat"), _one(q, "lon"), _one(q, "tz")
    label = None
    if city:
        hit = atlas.find(city)
        if not hit:
            raise ApiError(f"لم أجد مدينة باسم «{city}». جرّب اسمًا آخر أو أرسل lat و lon و tz.")
        lat = lat or hit["lat"]
        lon = lon or hit["lon"]
        tz = tz or hit["tz"]
        label = hit["label"]
    if lat is None or lon is None or tz is None:
        raise ApiError("لا بدّ من city، أو من lat و lon و tz معًا.")
    try:
        ZoneInfo(str(tz))
    except (ZoneInfoNotFoundError, ValueError):
        raise ApiError(f"منطقة زمنية غير معروفة: {tz}")
    return float(lat), float(lon), str(tz), label or f"{lat}, {lon}"


def parse_when(q: dict, tzname: str, default_time="12:00"):
    ds = _one(q, "date")
    ts = _one(q, "time", default_time)
    tz = ZoneInfo(tzname)
    if not ds:
        return datetime.now(tz)
    try:
        d = _date.fromisoformat(ds)
        hh, mm = (ts.split(":") + ["0"])[:2]
        return datetime(d.year, d.month, d.day, int(hh), int(mm), tzinfo=tz)
    except ValueError:
        raise ApiError("صيغة التاريخ يجب أن تكون YYYY-MM-DD والوقت HH:MM")


def parse_birth(q: dict, tzname: str, lon: float, default_time="12:00"):
    """يُرجع (الوقت المُدرك، تفاصيل التوقيت التاريخي وتحذيراته)."""
    ds = _one(q, "date")
    ts = _one(q, "time", default_time)
    if not ds:
        now = datetime.now(ZoneInfo(tzname))
        return now, ftz.resolve(now.replace(tzinfo=None), tzname, lon)
    try:
        d = _date.fromisoformat(ds)
        hh, mm = (ts.split(":") + ["0"])[:2]
        naive = datetime(d.year, d.month, d.day, int(hh), int(mm))
    except ValueError:
        raise ApiError("صيغة التاريخ يجب أن تكون YYYY-MM-DD والوقت HH:MM")
    info = ftz.resolve(naive, tzname, lon)
    return info["when"], info


# ── المسارات ─────────────────────────────────────────────────────
def route_health(q):
    return {"ok": True, "cities": len(atlas.CITIES),
            "systems": {k: v["name"] for k, v in chart.HOUSE_SYSTEMS.items()},
            "chiron": os.path.isdir(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe"))}


def route_atlas(q):
    term = _one(q, "q", "")
    return {"query": term, "results": atlas.search(term, int(_one(q, "limit", "12")))}


def route_ephemeris(q):
    tzname = _one(q, "tz", "UTC")
    try:
        ZoneInfo(tzname)
    except Exception:
        raise ApiError(f"منطقة زمنية غير معروفة: {tzname}")
    when = parse_when(q, tzname)
    jd = ephem.to_jd(when)
    rows = []
    for name, code, sym, core, _cls in chart.BODIES:
        try:
            import swisseph as swe
            x = swe.calc_ut(jd, code, chart.FLAGS)[0]
        except Exception:
            continue
        L = x[0] % 360.0
        rows.append({"name": name, "symbol": sym, "lon": round(L, 6),
                     "speed": round(x[3], 6), "retro": x[3] < 0, **chart.dms(L)})
    return {"when_local": when.isoformat(), "when_utc": when.astimezone(ephem.UTC).isoformat(),
            "tz": tzname, "bodies": rows, "moon_phase": ephem.moon_phase(when)}


def route_bulletin(q):
    lat, lon, tzname, label = resolve_place(q)
    tz = ZoneInfo(tzname)
    ds = _one(q, "date")
    day = _date.fromisoformat(ds) if ds else datetime.now(tz).date()

    shift = _one(q, "shift")
    if shift is not None:
        config.MANSION_SHIFT = int(shift)

    d = bulletin.gather(day, tzname, lat, lon)
    for_tomorrow = _one(q, "voice", "today") == "tomorrow"
    place = _one(q, "city") or label
    text = bulletin.render_text(d, for_tomorrow=for_tomorrow, location=place)

    return {
        "date": day.isoformat(), "tz": tzname, "place": place,
        "lat": lat, "lon": lon, "mansion_shift": config.MANSION_SHIFT,
        "text": text,
        "summary": {
            "moon_sign": d["moon_sign_noon"], "sun_sign": d["sun_sign"],
            "phase": d["phase"]["name"],
            "illum": round(d["phase"]["illumination"] * 100),
            "retrogrades": d["retrogrades"],
            "sun_times": {k: v.strftime("%H:%M") for k, v in (d.get("sun_times") or {}).items()},
            "mansions": [{"index": m["index"], "name": m["name"], "mood": m["mood"],
                          "start": m["start"].isoformat(), "end": m["end"].isoformat()}
                         for m in d["mansions"]],
            "aspects": [{"time": a["time"].strftime("%H:%M"), "planet": a["planet"],
                         "name": a["name"], "polarity": a["polarity"], "text": a["text"]}
                        for a in d["aspects"]],
            "voc": [{"start": v["start"].strftime("%H:%M"), "end": v["end"].isoformat(),
                     "hours": round(v["hours"], 1), "long": v["long"],
                     "next_sign": v["next_sign"]} for v in d["voc"]],
        },
    }


def route_chart(q):
    lat, lon, tzname, label = resolve_place(q)
    when, tzinfo = parse_birth(q, tzname, lon)
    system = _one(q, "system", "whole")
    if system not in chart.HOUSE_SYSTEMS:
        raise ApiError(f"نظام بيوت غير معروف: {system}. المتاح: "
                       + "، ".join(chart.HOUSE_SYSTEMS))
    minor = _one(q, "minor", "1") == "1"
    out = chart.compute(when, lat, lon, system, tzname,
                        minor_aspects=minor, tz_info=tzinfo)
    out["place"] = _one(q, "city") or label
    out["name"] = _one(q, "name", "")
    out["tz_describe"] = ftz.describe(tzinfo)

    if _one(q, "interpret", "1") == "1":
        out["reading"] = interpret.read_chart(out)

    # الخريطة نفسها بنظام آخر، لتيسير المقارنة
    if _one(q, "both", "1") == "1":
        other = _one(q, "compare") or ("placidus" if system == "whole" else "whole")
        if other in chart.HOUSE_SYSTEMS and other != system:
            alt = chart.compute(when, lat, lon, other, tzname,
                                minor_aspects=False, tz_info=tzinfo)
            out["alt"] = {"system": other,
                          "system_name": chart.HOUSE_SYSTEMS[other]["name"],
                          "system_note": chart.HOUSE_SYSTEMS[other]["note"],
                          "houses": alt["houses"], "angles": alt["angles"],
                          "bodies": [{"name": b["name"], "house": b["house"]}
                                     for b in alt["bodies"]],
                          "dominants": alt["dominants"]}
    return out


def route_glossary(q):
    """معجم المصطلحات — لشروح «عند الطلب» في الواجهة."""
    return {"terms": interpret.GLOSSARY}


ROUTES = {
    "health": route_health,
    "atlas": route_atlas,
    "ephemeris": route_ephemeris,
    "bulletin": route_bulletin,
    "chart": route_chart,
    "glossary": route_glossary,
}


def decode_path(raw: str) -> str:
    """
    خوادم HTTP تفكّ المسار بترميز latin-1، فتظهر العربية مشوّهة
    إن أرسلها العميل بايتات خامًا. نُعيدها إلى UTF-8.
    """
    try:
        return raw.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return raw


def dispatch(path: str, query: dict):
    name = path.rstrip("/").split("/")[-1] or "health"
    fn = ROUTES.get(name)
    if not fn:
        raise ApiError(f"مسار غير معروف: {name}. المتاح: " + "، ".join(ROUTES), 404)
    return fn(query)


# ── الملفات الثابتة ──────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml", ".ico": "image/x-icon", ".png": "image/png",
        ".woff2": "font/woff2", ".txt": "text/plain; charset=utf-8"}
STATIC_OK = set(MIME)


def read_static(path: str):
    """
    يخدم صفحات الموقع من الدالة نفسها.
    احتياط: إن عامل Vercel المشروع تطبيقًا كاملًا بدل مزيج ثابت + دوال،
    يبقى الموقع عاملًا بلا تغيير في الإعدادات.
    """
    rel = (path or "/").split("?")[0].lstrip("/")
    if rel in ("", "/"):
        rel = "index.html"
    if "\\" in rel or ".." in rel:
        return None
    ext = os.path.splitext(rel)[1].lower()
    if ext not in STATIC_OK:
        return None
    full = os.path.normpath(os.path.join(ROOT_DIR, rel))
    if not full.startswith(ROOT_DIR) or not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        return f.read(), MIME[ext]


# ── معالج Vercel ─────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body, ctype, status=200):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(decode_path(self.path))
        if "/api/" not in u.path and not u.path.rstrip("/").endswith("/api"):
            hit = read_static(u.path)
            if hit:
                return self._send_bytes(*hit)
        try:
            self._send(200, dispatch(u.path, parse_qs(u.query)))
        except ApiError as e:
            self._send(e.status, {"error": str(e)})
        except Exception as e:
            self._send(500, {"error": f"خطأ داخلي: {e}",
                             "trace": traceback.format_exc()[-1200:]})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, *a):
        pass


# ── تشغيل محلي: python api/index.py ─────────────────────────────
if __name__ == "__main__":
    import http.server
    import socketserver
    from functools import partial

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Local(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def do_GET(self):
            u = urlparse(decode_path(self.path))
            if u.path.startswith("/api/"):
                try:
                    payload, status = dispatch(u.path, parse_qs(u.query)), 200
                except ApiError as e:
                    payload, status = {"error": str(e)}, e.status
                except Exception as e:
                    payload, status = {"error": str(e),
                                       "trace": traceback.format_exc()[-1200:]}, 500
                body = json.dumps(payload, ensure_ascii=False, default=str).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            return super().do_GET()

        def log_message(self, *a):
            pass

    port = int(os.environ.get("PORT", 8000))
    with socketserver.TCPServer(("", port), Local) as httpd:
        print(f"يعمل على http://localhost:{port}")
        httpd.serve_forever()
