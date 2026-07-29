# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

الفَلَك (Al-Falak) — an Arabic-language traditional astrology web app. It computes planetary
positions, houses, lunar mansions, Arabic dignities/almuten, Arabic parts (lots), fixed stars,
and aspect patterns using Swiss Ephemeris, and renders them through server-side-computed
JSON APIs consumed by static HTML/vanilla-JS pages. There is no build step, no JS framework,
and no database — everything is computed live per request.

The whole repo doubles as a Vercel serverless deployment and a local dev server, using the
exact same Python file (`api/index.py`) for both.

All code comments, docstrings, UI text, and commit-worthy content in this repo are in Arabic.
Keep new code/comments/strings in Arabic to match the existing style unless told otherwise.

## Commands

```bash
pip install -r requirements.txt      # only dependency: pyswisseph
python api/index.py                  # run locally at http://localhost:8000 (PORT env var to override)
python tools/make_preview.py         # regenerate preview/ (static, serverless snapshot with baked-in fixtures)
```

There is no test suite, linter, or build step configured in this repo — don't invent commands
for `npm test`, `pytest`, etc.

To sanity-check a change, run the local server and hit routes directly, e.g.:
```
http://localhost:8000/api/health
http://localhost:8000/api/chart?date=1990-05-17&time=08:30&city=حلب&system=whole
```
`api/index.py`'s `if __name__ == "__main__"` block spins up a stdlib `http.server` that serves
both `/api/*` (dispatched through the same `dispatch()` used on Vercel) and static files from
the repo root — no separate frontend dev server exists.

`preview/` is a self-contained, no-server build (open `preview/index.html` by double-click):
`make_preview.py` calls `dispatch()` directly for a fixed matrix of dates/cities/house systems
and bakes the JSON responses into a `<script>` fixture that monkey-patches `window.fetch`.
Regenerate it after any API response-shape change; it's gitignored and excluded from the
Vercel function bundle (see `vercel.json`).

## Architecture

### Request flow
Every request — local or on Vercel — goes through `api/index.py`:
1. `handler.do_GET` (Vercel) or `Local.do_GET` (local dev) parses the path.
2. Paths without `/api/` are served as static files via `read_static()` (HTML/CSS/JS in the
   repo root and `assets/`), with a path-traversal guard.
3. `/api/<name>` is routed by `dispatch()` to one of the functions registered in `ROUTES`
   (`health`, `atlas`, `ephemeris`, `bulletin`, `chart`, `glossary`).
4. Route handlers call into the `falak` package, then return a plain dict that gets
   JSON-serialized (`ensure_ascii=False`, so Arabic text stays literal UTF-8 in the response).

On Vercel, `vercel.json` rewrites all `/api/*` to the single `api/index.py` function
(memory 1024MB, 30s timeout); there's no other backend infrastructure.

### The `falak` package — calculation engine
- `ephem.py` — low-level ephemeris primitives: Julian day conversion, geocentric apparent
  longitude/speed of a body (with a 400k-entry longitude cache keyed by `(body, jd)`),
  bisection root-finding for sign/mansion ingress times, Moon aspect scanning, void-of-course
  computation, sunrise/noon/sunset, moon phase. Almost everything downstream calls into this
  module rather than `swisseph` directly.
- `chart.py` — full natal/mundane chart: body table (13 bodies incl. Rahu/Lilith/Chiron),
  house systems (`HOUSE_SYSTEMS` dict maps 8 systems to Swiss Ephemeris house codes), aspect
  detection with per-body-class orb scaling (`CLASS_FACTOR` × `ASPECT_ORB`), and `_dominants()`
  for "strongest planet" scoring. `compute()` is the entry point that assembles everything
  a chart route needs.
- `dignities.py` — the five classical dignities (domicile/exaltation/triplicity/term/face) and
  almuten calculation (`almuten_of_place`, `almuten_of_chart`), following Ibn Abi al-Rijal's method.
- `parts.py` — the 18 Arabic lots (سهام) from al-Biruni's *al-Tafhim*, with day/night formulas.
- `patterns.py` — angular chart patterns (grand trine, T-square, yod, etc.).
- `stars.py` — 38 fixed stars with Arabic names and conjunction orbs to chart points.
- `timezone.py` — historical timezone resolution: detects ambiguous/nonexistent local times
  (DST folds/gaps) and falls back to local mean solar time for pre-1900 dates, returning both
  the resolved datetime and a warning payload (`resolve()`, `describe()`).
- `tables.py` — the 28 lunar mansions and their bulletin text tables.
- `bulletin.py` — assembles and renders the daily Arabic-language bulletin (`gather()` collects
  all the day's data; `render_text()` formats it into copyable prose, in "today" or "tomorrow" voice).
- `interpret.py` — chart-reading text generator (`read_chart()`) and the on-demand glossary
  (`GLOSSARY`, served via `/api/glossary`) — the natural place to edit reading tone/wording.
- `atlas.py` — ~294 built-in cities (`lat|lon|tz`, pipe-delimited data baked into the module) with
  fuzzy Arabic/English search; falls back to Open-Meteo geocoding for cities not in the list.
- `config.py` — the single place to tune behavior: `MANSION_SHIFT` (0 vs 1 mansion-counting
  convention), aspect angle set, orb long-VOC threshold, which locations get a dedicated bulletin.

### Frontend
Five static pages (`index.html`, `bulletin.html`, `chart.html`, `ephemeris.html`, `learn.html`)
share `assets/app.js` (a small `API()` fetch helper, starfield canvas background, city
autocomplete against `/api/atlas`) and `assets/style.css`. `assets/wheel.js` draws the natal
chart wheel (sign ring, 28-mansion ring, house ring). There's no bundler — pages load these
scripts via plain `<script src>` tags, so keep additions dependency-free vanilla JS/CSS.

### Key domain conventions worth knowing before changing calculation code
- All positions are **geocentric apparent, tropical zodiac** (not sidereal) — verified against
  Astrotheme to the arcminute (see README's "التحقق" section).
- House systems that break down near the poles are flagged in `POLAR_FRAGILE` /
  `POLAR_LIMIT` in `chart.py` — don't remove those guards.
- Chiron requires an optional `ephe/seas_18.se1` ephemeris file (not checked in); its absence
  is expected and handled gracefully — `route_health` reports whether the `ephe/` dir exists.
- Outer planets (Uranus/Neptune/Pluto) are excluded from Moon aspects and void-of-course by
  default (`config.INCLUDE_OUTER = False`) since they're outside the traditional/Arabic system
  this project models — don't enable them without understanding why they're off.
