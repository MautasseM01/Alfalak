#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يبني معاينة تعمل بنقرة مزدوجة بلا خادم:
ينسخ الصفحات ويحقن طبقة تعترض نداءات /api/ وتردّ من بيانات مُولّدة مسبقًا.
    python tools/make_preview.py
"""
import json
import os
import re
import shutil
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from api.index import dispatch                      # noqa: E402
from falak import atlas                             # noqa: E402

PREVIEW = os.path.join(ROOT, "preview")
PAGES = ["index.html", "bulletin.html", "chart.html", "ephemeris.html", "learn.html"]
ASSETS = ["style.css", "app.js", "wheel.js"]

CITIES = ["دمشق", "باريس"]
TODAY = date.today()


def q(**kw):
    return {k: [str(v)] for k, v in kw.items()}


def key(path, params):
    items = sorted((k, str(v)) for k, v in params.items() if v not in ("", None))
    return path + "?" + "&".join(f"{k}={v}" for k, v in items)


def build_fixtures():
    fx = {}

    def add(path, params):
        try:
            fx[key(path, params)] = dispatch("/api/" + path, q(**params))
        except Exception as e:
            print("  ✗", path, params, e)

    add("health", {})
    add("glossary", {})
    for tz in ("Asia/Damascus", "Europe/Paris", "UTC"):
        add("ephemeris", {"tz": tz})
        add("ephemeris", {"date": TODAY.isoformat(), "time": "12:00", "tz": tz})

    for i in range(-2, 8):
        d = (TODAY + timedelta(days=i)).isoformat()
        for city in CITIES:
            for voice in ("today", "tomorrow"):
                add("bulletin", {"date": d, "city": city, "voice": voice, "shift": 0})
        add("bulletin", {"date": d, "city": "دمشق", "voice": "today", "shift": 1})

    # خرائط نموذجية بكل أنظمة البيوت
    ALL_SYS = ("whole", "alcabitius", "placidus", "koch",
               "regiomontanus", "campanus", "porphyry", "equal")
    demo = [("1990-05-17", "08:30", "حلب", ALL_SYS, ("1", "0")),
            # ساعة معدومة بباريس، لعرض التحذير
            ("2024-03-31", "02:30", "باريس", ("whole", "alcabitius", "placidus"), ("1",))]
    for date_, time_, city, systems, minors in demo:
        for sysname in systems:
            for minor in minors:
                add("chart", {"date": date_, "time": time_, "city": city,
                              "system": sysname, "compare": "placidus",
                              "minor": minor, "both": "1"})
    print(f"  ✓ {len(fx)} ردًّا مُولّدًا")
    return fx


MOCK = """
<script>
/* طبقة معاينة: تردّ على نداءات /api/ من بيانات محفوظة، بلا خادم */
(function(){
  const FX = __FIXTURES__;
  const CITIES = __CITIES__;
  const norm = s => (s||'').normalize('NFKD').replace(/[\\u0300-\\u036f]/g,'')
      .replace(/[أإآ]/g,'ا').replace(/ى/g,'ي').replace(/ة/g,'ه')
      .replace(/ؤ/g,'و').replace(/ئ/g,'ي').replace(/ـ/g,'').toLowerCase().trim();

  function atlasSearch(term, limit){
    const t = norm(term); if(!t) return [];
    const starts=[], has=[];
    for(const c of CITIES){
      if(norm(c.ar).startsWith(t) || norm(c.en).startsWith(t)) starts.push(c);
      else if((norm(c.ar)+' '+norm(c.en)+' '+norm(c.country)).includes(t)) has.push(c);
    }
    return starts.concat(has).slice(0, limit||12);
  }

  const realFetch = window.fetch ? window.fetch.bind(window)
                                 : () => Promise.reject(new Error('لا اتصال'));
  window.fetch = function(url, opts){
    const s = String(url);
    if(!s.includes('/api/')) return realFetch(url, opts);
    const u = new URL(s, 'http://x');
    const path = u.pathname.split('/api/')[1] || 'health';
    const p = {}; u.searchParams.forEach((v,k)=>{ if(v!=='') p[k]=v; });

    const reply = (data, status) => Promise.resolve({
      ok: (status||200) < 400, status: status||200, json: async()=>data });

    if(path === 'atlas'){
      return reply({query:p.q||'', results: atlasSearch(p.q, +(p.limit||12))});
    }
    const k = path + '?' + Object.keys(p).sort().map(x=>x+'='+p[x]).join('&');
    let hit = FX[k];
    /* في المعاينة نتساهل: جدول المواقع يُقرَّب لأقرب ردّ محفوظ */
    if(!hit && path === 'ephemeris'){
      const want = 'ephemeris?tz=' + (p.tz||'UTC');
      hit = FX[want] || FX[Object.keys(FX).find(x=>x.startsWith('ephemeris?'))];
    }
    if(hit) return reply(hit);
    return reply({error:
      'هذه معاينة بلا خادم، وهذا الطلب غير محفوظ فيها مسبقًا. '+
      'بعد النشر على Vercel يُحسب أي تاريخ وأي مدينة لحظيًا.'}, 404);
  };
})();
</script>
"""


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    os.makedirs(os.path.join(PREVIEW, "assets"), exist_ok=True)
    for f in ASSETS:
        src = open(os.path.join(ROOT, "assets", f), encoding="utf-8").read()
        src = src.replace('/learn.html#', 'learn.html#')
        open(os.path.join(PREVIEW, "assets", f), "w", encoding="utf-8").write(src)

    print("… أُولّد الردود")
    fx = build_fixtures()
    cities = [{k: v for k, v in c.items() if not k.startswith("_")} for c in atlas.CITIES]
    mock = (MOCK
            .replace("__FIXTURES__", json.dumps(fx, ensure_ascii=False, default=str))
            .replace("__CITIES__", json.dumps(cities, ensure_ascii=False)))

    for page in PAGES:
        html = open(os.path.join(ROOT, page), encoding="utf-8").read()
        html = html.replace('href="/assets/', 'href="assets/')
        html = html.replace('src="/assets/', 'src="assets/')
        html = re.sub(r'href="/([a-z]+\.html)"', r'href="\1"', html)
        html = html.replace('href="/"', 'href="index.html"')
        html = html.replace('<script src="assets/app.js"></script>',
                            mock + '\n<script src="assets/app.js"></script>')
        open(os.path.join(PREVIEW, page), "w", encoding="utf-8").write(html)
        print("  ✓", page)

    print(f"✓ المعاينة جاهزة: {os.path.join(PREVIEW, 'index.html')}")


if __name__ == "__main__":
    main()
