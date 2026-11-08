#!/usr/bin/env python3
"""Capture title-screen and gameplay screenshots of every OuterHeavenX GitHub Pages build.

Writes   shots/<repo>/title.jpg, play1.jpg, play2.jpg   and   shots/index.json
Run by .github/workflows/capture-shots.yml (weekly + manual). Best effort: a game that
cannot be driven automatically simply keeps whatever shots it already had. Add your own
files to shots/<repo>/ (same names) at any time; set "skip" in shots/config.json to stop
the bot from touching a repo.
"""
import argparse, datetime, hashlib, io, json, os, re, sys, urllib.request
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

OWNER = "OuterHeavenX"
START_RE = re.compile(r"^\s*(start|play|new game|begin|enter|continue|tap to|click to|press|let'?s go|ok|got it|next|skip)", re.I)
W, H = 1280, 720


def gh_repos():
    req = urllib.request.Request(f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=pushed",
                                 headers={"Accept": "application/vnd.github+json",
                                          **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {})})
    out = []
    for r in json.load(urllib.request.urlopen(req, timeout=30)):
        if r.get("fork") or r.get("archived") or not r.get("has_pages"):
            continue
        home = r.get("homepage") or ""
        url = home if home.startswith("http") else f"https://{OWNER.lower()}.github.io/{r['name']}/"
        out.append({"name": r["name"], "url": url})
    return out


def snap(page) -> bytes:
    png = page.screenshot(type="png")
    im = Image.open(io.BytesIO(png)).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True)
    return buf.getvalue()


def thumb_hash(jpg: bytes):
    im = Image.open(io.BytesIO(jpg)).convert("L").resize((32, 18))
    return list(im.tobytes())


def differs(a: bytes, b: bytes) -> bool:
    pa, pb = thumb_hash(a), thumb_hash(b)
    d = [abs(x - y) for x, y in zip(pa, pb)]
    return sum(d) / len(d) > 2.5 or max(d) > 20  # broad change, or one region changed a lot


def make_thumb(d: Path):
    """480x270 card thumbnail derived from title.jpg (about 15 KB instead of about 100 KB)."""
    src = d / "title.jpg"
    if not src.exists():
        return False
    im = Image.open(src).convert("RGB")
    im.thumbnail((480, 270), Image.LANCZOS)
    im.save(d / "thumb.jpg", "JPEG", quality=72, optimize=True, progressive=True)
    return True


def blank(jpg: bytes) -> bool:
    px = thumb_hash(jpg)
    return max(px) - min(px) < 8


def advance(page):
    """Click the most start-like control, else the canvas centre, then Enter."""
    clicked = False
    for sel in ("button", "[role=button]", "a", "input[type=button]", "div", "span"):
        try:
            for el in page.locator(sel).all()[:60]:
                if not el.is_visible():
                    continue
                t = (el.inner_text(timeout=300) or "").strip()
                if t and len(t) < 40 and START_RE.search(t):
                    el.click(timeout=1500)
                    clicked = True
                    break
        except Exception:
            pass
        if clicked:
            break
    if not clicked:
        page.mouse.click(W // 2, H // 2)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1800)


def explore(page):
    """Wander a little so the second gameplay shot shows something moving."""
    for key in ("ArrowRight", "d"):
        page.keyboard.down(key); page.wait_for_timeout(900); page.keyboard.up(key)
    for key in ("ArrowUp", "w"):
        page.keyboard.down(key); page.wait_for_timeout(700); page.keyboard.up(key)
    for x, y in ((W * .3, H * .6), (W * .7, H * .5), (W * .5, H * .35)):
        page.mouse.click(x, y); page.wait_for_timeout(400)
    page.keyboard.press("Space")
    page.wait_for_timeout(2200)


def capture(browser, repo, out: Path, interact: bool):
    ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1)
    page = ctx.new_page()
    page.on("dialog", lambda d: d.dismiss())
    got = {}
    try:
        page.goto(repo["url"], wait_until="load", timeout=30000)
        page.wait_for_timeout(4500)
        title = snap(page)
        if blank(title):
            return got
        got["title"] = title
        if interact:
            advance(page); advance(page)
            p1 = snap(page)
            if differs(title, p1) and not blank(p1):
                got["play1"] = p1
            explore(page)
            p2 = snap(page)
            if not blank(p2) and differs(title, p2) and ("play1" not in got or differs(got["play1"], p2)):
                got["play2"] = p2
    except Exception as e:
        print(f"  ! {repo['name']}: {e}", file=sys.stderr)
    finally:
        ctx.close()
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="shots")
    ap.add_argument("--only", help="comma-separated repo names")
    ap.add_argument("--repos-file", help="JSON [{name,url}] instead of querying GitHub")
    ap.add_argument("--chrome", default=os.environ.get("CHROME_PATH"))
    ap.add_argument("--thumbs-only", action="store_true", help="only (re)build thumb.jpg files and index.json, no browsing")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(exist_ok=True)
    cfg_path = out / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    skip = {s.lower() for s in cfg.get("skip", [])}
    no_interact = {s.lower() for s in cfg.get("title_only", [])}
    idx_path = out / "index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"repos": {}}
    refreshed = set()
    repos = []
    if not a.thumbs_only:
        repos = json.load(open(a.repos_file)) if a.repos_file else gh_repos()
        if a.only:
            want = {s.lower() for s in a.only.split(",")}
            repos = [r for r in repos if r["name"].lower() in want]
    if repos:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=a.chrome, args=["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"])
            for r in repos:
                n = r["name"]
                if n.lower() in skip:
                    print(f"- {n}: skipped"); continue
                print(f"- {n}: {r['url']}")
                got = capture(browser, r, out / n, interact=n.lower() not in no_interact)
                if not got:
                    print("  no usable capture; keeping existing"); continue
                d = out / n; d.mkdir(exist_ok=True)
                ent = idx["repos"].setdefault(n, {})
                botmade = set(ent.get("bot", []))
                for slot, data in got.items():
                    f = d / f"{slot}.jpg"
                    # never overwrite a screenshot you committed by hand: only replace files this bot wrote
                    if f.exists() and slot not in botmade:
                        continue
                    f.write_bytes(data)
                    botmade.add(slot)
                    if slot == "title":
                        refreshed.add(n)
                ent["bot"] = sorted(botmade)
                ent["captured"] = datetime.date.today().isoformat()
                print(f"  saved {sorted(got)}")
            browser.close()
    # thumbnails, plus pick up any hand-added files for every repo folder
    for d in sorted(p for p in out.iterdir() if p.is_dir()):
        have = [s for s in ("title", "play1", "play2") if (d / f"{s}.jpg").exists()]
        if not have:
            continue
        ent = idx["repos"].setdefault(d.name, {})
        ent["shots"] = have
        if (d / "title.jpg").exists() and (d.name in refreshed or not (d / "thumb.jpg").exists()):
            make_thumb(d)
        ent["thumb"] = (d / "thumb.jpg").exists()
    idx["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    idx_path.write_text(json.dumps(idx, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
