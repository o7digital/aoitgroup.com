#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re
import ssl
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).parent
BASE = "https://www.aoitgroup.com"
SSL_CONTEXT = ssl._create_unverified_context()
ASSET_RE = re.compile(r'(?:src|href|data-src|srcset)="([^"]+)"|url\(([^)]+)\)', re.I)
ASSET_PREFIXES = ("/application/", "/concrete/", "/packages/")


def html_files():
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            path = ROOT / arg
            if path.exists():
                yield path
        return
    yield from ROOT.rglob("*.html")


def referenced_assets():
    paths = set()
    for file in html_files():
        if ".git" in file.parts:
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        for match in ASSET_RE.finditer(text):
            value = (match.group(1) or match.group(2) or "").strip("'\" ")
            for part in value.split(","):
                url = part.strip().split()[0] if part.strip() else ""
                if url.startswith(ASSET_PREFIXES):
                    paths.add(url.split("?", 1)[0])
    return sorted(paths)


def missing_assets():
    for url_path in referenced_assets():
        local = ROOT / url_path.lstrip("/")
        if not local.exists():
            yield url_path, local


def download(item):
    url_path, local = item
    local.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        BASE + url_path,
        headers={"User-Agent": "Mozilla/5.0 asset repair"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12, context=SSL_CONTEXT) as response:
            content = response.read()
            content_type = response.headers.get("content-type", "")
        if not content or "text/html" in content_type.lower():
            return url_path, "skipped-html"
        local.write_bytes(content)
        return url_path, "downloaded"
    except urllib.error.HTTPError as exc:
        return url_path, f"http-{exc.code}"
    except Exception as exc:
        return url_path, exc.__class__.__name__


def main():
    items = list(missing_assets())
    print(f"missing={len(items)}")
    if not items:
        return

    counts = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(download, item) for item in items]
        for index, future in enumerate(as_completed(futures), 1):
            url_path, status = future.result()
            counts[status] = counts.get(status, 0) + 1
            if status != "downloaded":
                print(f"{status}: {url_path}", file=sys.stderr)
            if index % 100 == 0:
                print(f"processed={index}/{len(items)}")
    print(" ".join(f"{key}={counts[key]}" for key in sorted(counts)))


if __name__ == "__main__":
    main()
