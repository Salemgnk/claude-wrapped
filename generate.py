#!/usr/bin/env python3
"""
My Claude Wrapped — generate a shareable retro-arcade HTML page from your local
Claude Code transcripts (~/.claude/projects/**/*.jsonl).

My Claude Wrapped — génère une page HTML partageable (style arcade rétro) à
partir de tes transcripts locaux Claude Code.

Usage:
    python3 generate.py                     # full history, French (default)
    python3 generate.py --lang en           # English version
    python3 generate.py --days 30           # last 30 days only
    python3 generate.py --out wrapped.html  # custom output name
    python3 generate.py --projects-dir /path/to/projects
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_ABBR = {
    "fr": {"Monday": "LUN", "Tuesday": "MAR", "Wednesday": "MER", "Thursday": "JEU",
           "Friday": "VEN", "Saturday": "SAM", "Sunday": "DIM"},
    "en": {"Monday": "MON", "Tuesday": "TUE", "Wednesday": "WED", "Thursday": "THU",
           "Friday": "FRI", "Saturday": "SAT", "Sunday": "SUN"},
}


def parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def pretty_project(raw: str) -> str:
    """'-home-pr1nx3-Frisz-frisz-flutter' -> 'Frisz/frisz/flutter'."""
    s = raw
    for prefix in ("-home-pr1nx3-", "-home-pr1nx3", "-Users-", "-home-"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    s = s.lstrip("-")
    return s.replace("-", "/") or raw


def is_real_prompt(msg: dict) -> bool:
    """A user message that is not just a tool_result / meta entry."""
    c = msg.get("content")
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        for b in c:
            if isinstance(b, str) and b.strip():
                return True
            if isinstance(b, dict) and b.get("type") == "text" and (b.get("text") or "").strip():
                return True
    return False


def collect(projects_dir: str, since: datetime | None, lang: str):
    files = glob.glob(os.path.join(projects_dir, "**", "*.jsonl"), recursive=True)

    models = Counter()
    tools = Counter()
    hours = [0] * 24
    weekdays = Counter()
    by_project_prompts = Counter()
    by_day = Counter()
    sessions = set()
    projects_seen = set()

    tok_in = tok_out = cache_read = cache_create = 0
    user_prompts = 0
    assistant_msgs = 0
    first_ts = last_ts = None

    for f in files:
        proj = f.split(os.sep + "projects" + os.sep)[-1].split(os.sep)[0]
        try:
            fh = open(f, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = o.get("timestamp")
                dt = parse_ts(ts) if ts else None
                if since and dt and dt < since:
                    continue

                t = o.get("type")
                if o.get("sessionId"):
                    sessions.add(o["sessionId"])

                if dt:
                    if first_ts is None or dt < first_ts:
                        first_ts = dt
                    if last_ts is None or dt > last_ts:
                        last_ts = dt
                    hours[dt.hour] += 1
                    weekdays[dt.strftime("%A")] += 1
                    by_day[dt.date().isoformat()] += 1

                if t == "user":
                    msg = o.get("message", {}) or {}
                    if is_real_prompt(msg):
                        user_prompts += 1
                        by_project_prompts[proj] += 1
                        projects_seen.add(proj)
                elif t == "assistant":
                    projects_seen.add(proj)
                    msg = o.get("message", {}) or {}
                    m = msg.get("model")
                    if m and m != "<synthetic>":
                        models[m] += 1
                        assistant_msgs += 1
                    u = msg.get("usage", {}) or {}
                    tok_in += u.get("input_tokens", 0) or 0
                    tok_out += u.get("output_tokens", 0) or 0
                    cache_read += u.get("cache_read_input_tokens", 0) or 0
                    cache_create += u.get("cache_creation_input_tokens", 0) or 0
                    for b in (msg.get("content") or []):
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            tools[b.get("name", "?")] += 1

    tokens_total = tok_in + tok_out + cache_read + cache_create
    days_active = len(by_day)
    busiest_day = by_day.most_common(1)[0] if by_day else ["-", 0]
    peak_hour = max(range(24), key=lambda h: hours[h]) if any(hours) else 0

    night = sum(hours[h] for h in list(range(22, 24)) + list(range(0, 5)))
    total_h = sum(hours) or 1
    night_pct = round(100 * night / total_h)

    abbr = WEEKDAY_ABBR[lang]
    weekday_list = [[abbr[d], weekdays.get(d, 0)] for d in WEEKDAYS]
    busiest_weekday = max(WEEKDAYS, key=lambda d: weekdays.get(d, 0)) if weekdays else "Monday"

    top_projects = [[pretty_project(p), n] for p, n in by_project_prompts.most_common(8)]
    top_model = models.most_common(1)[0][0] if models else "-"
    top_tool = tools.most_common(1)[0][0] if tools else "-"

    persona = build_persona(top_model, top_tool, peak_hour, night_pct, lang)
    achievements = build_achievements(
        user_prompts, tokens_total, len(projects_seen), peak_hour,
        top_tool, len(sessions), len(models), busiest_day[1], lang,
    )

    return {
        "meta": {
            "lang": lang,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "start": first_ts.date().isoformat() if first_ts else "-",
            "end": last_ts.date().isoformat() if last_ts else "-",
            "days_active": days_active,
            "player": os.environ.get("USER", "PLAYER 1"),
        },
        "totals": {
            "sessions": len(sessions),
            "projects": len(projects_seen),
            "prompts": user_prompts,
            "tokens_total": tokens_total,
            "tokens_in": tok_in,
            "tokens_out": tok_out,
            "cache_read": cache_read,
            "cache_create": cache_create,
            "tool_calls": sum(tools.values()),
            "assistant_msgs": assistant_msgs,
        },
        "models": models.most_common(8),
        "tools": tools.most_common(6),
        "hours": hours,
        "weekdays": weekday_list,
        "busiest_weekday": abbr[busiest_weekday],
        "projects": top_projects,
        "busiest_day": busiest_day,
        "peak_hour": peak_hour,
        "night_pct": night_pct,
        "top_model": top_model,
        "top_tool": top_tool,
        "persona": persona,
        "achievements": achievements,
    }


def build_persona(top_model, top_tool, peak_hour, night_pct, lang):
    model_short = top_model.replace("claude-", "").replace("-", " ").upper()
    variants = {
        "night":  ("THE NIGHT CODER", "Tu codes quand le reste du monde dort.",
                                      "You code while the rest of the world sleeps."),
        "early":  ("THE EARLY GRINDER", "Premier au clavier, café en main.",
                                        "First to the keyboard, coffee in hand."),
        "bash":   ("THE TERMINAL GLADIATOR", "Le shell est ton arène.",
                                             "The shell is your arena."),
        "smith":  ("THE CODE SMITH", "Tu forges du code, ligne par ligne.",
                                     "You forge code, line by line."),
        "builder":("THE BUILDER", "Tu construis, sans relâche.",
                                  "You build, relentlessly."),
    }
    if night_pct >= 35:
        key = "night"
    elif 5 <= peak_hour <= 9:
        key = "early"
    elif top_tool == "Bash":
        key = "bash"
    elif top_tool in ("Edit", "Write"):
        key = "smith"
    else:
        key = "builder"
    title, sub_fr, sub_en = variants[key]
    return {"title": title, "sub": sub_fr if lang == "fr" else sub_en, "main_model": model_short}


def build_achievements(prompts, tokens, projects, peak_hour, top_tool,
                       sessions, n_models, busy_day, lang):
    fr = lang == "fr"
    a = []

    def add(icon, title_fr, title_en, desc_fr, desc_en):
        a.append({"icon": icon,
                  "title": title_fr if fr else title_en,
                  "desc": desc_fr if fr else desc_en})

    if prompts >= 500:
        add("💬", "PROLIFIQUE", "PROLIFIC", f"{prompts} prompts envoyés", f"{prompts} prompts sent")
    if tokens >= 1_000_000_000:
        add("🪙", "TOKEN BILLIONAIRE", "TOKEN BILLIONAIRE",
            f"{tokens/1e9:.1f}B tokens traités", f"{tokens/1e9:.1f}B tokens processed")
    elif tokens >= 100_000_000:
        add("🪙", "TOKEN TYCOON", "TOKEN TYCOON",
            f"{tokens/1e6:.0f}M tokens traités", f"{tokens/1e6:.0f}M tokens processed")
    if projects >= 20:
        add("🗺️", "EXPLORATEUR", "EXPLORER", f"{projects} projets visités", f"{projects} projects visited")
    if peak_hour >= 22 or peak_hour < 5:
        add("🦉", "NOCTAMBULE", "NIGHT OWL", f"Pic d'activité à {peak_hour}h", f"Peak activity at {peak_hour}:00")
    elif 5 <= peak_hour <= 9:
        add("🌅", "LÈVE-TÔT", "EARLY BIRD", f"Pic d'activité à {peak_hour}h", f"Peak activity at {peak_hour}:00")
    if top_tool == "Bash":
        add("⚔️", "TERMINAL MASTER", "TERMINAL MASTER",
            "Bash, ton arme de prédilection", "Bash, your weapon of choice")
    if sessions >= 40:
        add("🏃", "MARATHONIEN", "MARATHONER", f"{sessions} sessions jouées", f"{sessions} sessions played")
    if n_models >= 5:
        add("🎭", "COLLECTIONNEUR", "COLLECTOR", f"{n_models} modèles utilisés", f"{n_models} models used")
    if busy_day >= 200:
        add("🔥", "JOURNÉE DE FEU", "DAY ON FIRE", f"{busy_day} events en 1 jour", f"{busy_day} events in 1 day")
    return a


def _font_faces() -> str:
    """@font-face en base64 (polices néo-brutalistes) pour un HTML 100% autonome."""
    fonts_dir = Path(__file__).parent / "fonts"
    faces = [("Grotesk", 700, "SpaceGrotesk-700.woff2"),
             ("Grotesk", 500, "SpaceGrotesk-500.woff2"),
             ("Mono", 700, "SpaceMono-700.woff2")]
    css = ""
    for family, weight, fn in faces:
        p = fonts_dir / fn
        if not p.exists():
            continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        css += (f"@font-face{{font-family:'{family}';font-weight:{weight};font-display:block;"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return css


def render_html(data: dict, template_path: str) -> str:
    tpl = Path(template_path).read_text(encoding="utf-8")
    tpl = tpl.replace("/*__FONTS__*/", _font_faces())
    return tpl.replace("/*__WRAPPED_DATA__*/", json.dumps(data, ensure_ascii=False))


# --- Optional PNG export (one image per screen) via a headless browser ---
# No Python dependency added: uses a system Chrome/Chromium if available.

CHROME_CANDIDATES = ["google-chrome-stable", "google-chrome", "chromium",
                     "chromium-browser", "chrome"]


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        p = shutil.which(c)
        if p:
            return p
    return None


def _run(chrome: str, args: list, **kw):
    return subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu",
                           "--hide-scrollbars"] + args,
                          capture_output=True, text=True, timeout=90, **kw)


def slide_count(chrome: str, url: str) -> int | None:
    """Read data-slides exposed by the page (falls back gracefully)."""
    try:
        out = _run(chrome, ["--virtual-time-budget=2500", "--dump-dom", url]).stdout
        m = re.search(r'data-slides="(\d+)"', out)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def render_images(html_path: str, out_dir: str, width: int, height: int) -> None:
    chrome = find_chrome()
    if not chrome:
        print("⚠️  --images needs Chrome/Chromium (none found on PATH). Skipping image export.")
        print("   Install Chrome/Chromium, then re-run with --images.")
        return
    base = "file://" + os.path.abspath(html_path)
    n = slide_count(chrome, base + "?shot=1") or 10
    os.makedirs(out_dir, exist_ok=True)
    for i in range(1, n + 1):
        png = os.path.join(out_dir, f"slide_{i:02d}.png")
        _run(chrome, [
            "--force-device-scale-factor=2",
            f"--window-size={width},{height}",
            "--virtual-time-budget=3000",
            f"--screenshot={png}",
            f"{base}?slide={i}&shot=1",
        ])
    print(f"🖼️  {n} images ({width}x{height} @2x) → {out_dir}/")


def main():
    here = Path(__file__).parent
    ap = argparse.ArgumentParser(description="Generate your Claude Code Wrapped.")
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--lang", choices=["fr", "en"], default="fr")
    ap.add_argument("--days", type=int, default=None, help="Limit to the last N days")
    ap.add_argument("--out", default=None)
    ap.add_argument("--template", default=str(here / "template.html"))
    ap.add_argument("--images", action="store_true",
                    help="Also export one PNG per screen (needs Chrome/Chromium)")
    ap.add_argument("--images-dir", default=None,
                    help="Output folder for --images (default: <out folder>/images)")
    ap.add_argument("--image-size", default="1200x800",
                    help="WxH of exported images (default: 1200x800)")
    args = ap.parse_args()

    out = args.out or str(here / ("claude_wrapped.html" if args.lang == "fr"
                                  else "claude_wrapped.en.html"))

    since = None
    if args.days:
        since = datetime.now(timezone.utc) - timedelta(days=args.days)

    print(f"⏳ Analyzing transcripts… (lang={args.lang})")
    data = collect(args.projects_dir, since, args.lang)
    html = render_html(data, args.template)
    Path(out).write_text(html, encoding="utf-8")

    t = data["totals"]
    print("✅ Wrapped generated!")
    print(f"   → {out}")
    print(f"   Sessions: {t['sessions']} | Projects: {t['projects']} | Prompts: {t['prompts']}")
    print(f"   Tokens: {t['tokens_total']:,} | Top model: {data['top_model']} | Top tool: {data['top_tool']}")
    print(f"   Persona: {data['persona']['title']}")

    if args.images:
        img_dir = args.images_dir or str(Path(out).resolve().parent / "images")
        try:
            w, h = (int(x) for x in args.image_size.lower().split("x"))
        except ValueError:
            w, h = 1200, 800
        render_images(out, img_dir, w, h)


if __name__ == "__main__":
    main()
