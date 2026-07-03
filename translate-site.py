#!/usr/bin/env python3
import html
import json
import re
import time
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).parent
LANGS = {"en": "English", "fr": "Français", "es": "Español", "de": "Deutsch", "it": "Italiano"}
SKIP_DIRS = set(LANGS) | {"application", "concrete", "packages", ".git", ".vercel"}
BASE = "https://aoitgroup.vercel.app"
PATH_ALIASES = {
    "/cyber-security/cyber-assurance/managed-detection-response": "/cyber-security/cyber-consultancy/managed-detection-response",
    "/cyber-security/cyber-essentials": "/cyber-security/cyber-assurance/cyber-essentials",
    "/cyber-security/cyber-security-awareness-training": "/cyber-security/cyber-assurance/cyber-security-awareness-training",
    "/cyber-security/iot-device-security-assessments": "/cyber-security/cyber-assurance/iot-device-security-assessments",
    "/cyber-security/managed-detection-response": "/cyber-security/cyber-consultancy/managed-detection-response",
    "/cyber-security/penetration-testing": "/cyber-security/cyber-assurance/penetration-testing",
    "/cyber-security/physical-penetration-testing": "/cyber-security/cyber-assurance/physical-penetration-testing",
    "/cyber-security/red-teaming": "/cyber-security/cyber-assurance/red-teaming",
    "/cyber-security/social-engineering": "/cyber-security/cyber-assurance/social-engineering",
    "/cyber-security/vulnerability-assessments": "/cyber-security/cyber-assurance/vulnerability-assessments",
    "/data-privacy": "/privacy-policy",
    "/jobs": "/about-a-and-o/jobs",
    "/it-services/managed-services/packaged-services": "/it-services",
    "/knowledge-hub/business-continuity-disruption-home-working": "/knowledge-hub",
    "/newsroom/press-releases/2021-11-10-gartner-says-cloud-will-be-the-centerpiece-of-new-digital-experiences": "/knowledge-hub",
}
CACHE_FILE = ROOT / f".translation-cache-{(sys.argv[1] if len(sys.argv) > 1 else 'all')}.json"
CACHE = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}


def source_pages():
    pages = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS or "?" in path.name:
            continue
        pages.append(path)
    return sorted(pages)


def translatable(value):
    value = re.sub(r"\s+", " ", value).strip()
    return value if value and re.search(r"[A-Za-z]", value) and not re.fullmatch(r"[\w.+-]+@[\w.-]+", value) else None


def translate_batches(strings, lang):
    missing = [s for s in strings if f"{lang}\0{s}" not in CACHE]
    batches, current, size = [], [], 0
    for text in missing:
        addition = len(text) + 18
        if current and size + addition > 3500:
            batches.append(current); current, size = [], 0
        current.append(text); size += addition
    if current: batches.append(current)
    for batch_no, batch in enumerate(batches, 1):
        payload = "\n".join(f"___T{i:04d}___ {text}" for i, text in enumerate(batch))
        query = urllib.parse.urlencode({"client":"gtx", "sl":"en", "tl":lang, "dt":"t", "q":payload})
        for attempt in range(4):
            try:
                with urllib.request.urlopen("https://translate.googleapis.com/translate_a/single?" + query, timeout=30) as response:
                    data = json.load(response)
                result = "".join(part[0] for part in data[0])
                matches = re.findall(r"___T(\d{4})___\s*(.*?)(?=\n?___T\d{4}___|$)", result, re.S)
                found = {int(i): value.strip() for i, value in matches}
                for i, original in enumerate(batch):
                    CACHE[f"{lang}\0{original}"] = found.get(i, original)
                break
            except Exception:
                if attempt == 3: raise
                time.sleep(2 ** attempt)
        if batch_no % 10 == 0:
            CACHE_FILE.write_text(json.dumps(CACHE, ensure_ascii=False))
    CACHE_FILE.write_text(json.dumps(CACHE, ensure_ascii=False))


def add_seo(soup, lang, rel):
    if soup.html: soup.html["lang"] = lang
    for link in soup.select('link[rel="canonical"], link[rel="alternate"][hreflang]'):
        link.decompose()
    head = soup.head
    if not head: return
    slug = "" if rel.as_posix() == "index.html" else rel.with_suffix("").as_posix() + "/"
    canonical = soup.new_tag("link", rel="canonical", href=f"{BASE}/{lang}/{slug}")
    head.append(canonical)
    for code in LANGS:
        head.append(soup.new_tag("link", rel="alternate", hreflang=code, href=f"{BASE}/{code}/{slug}"))
    head.append(soup.new_tag("link", rel="alternate", hreflang="x-default", href=f"{BASE}/en/{slug}"))


def localize_links(soup, lang):
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        query = ""
        if href.startswith("https://www.aoitgroup.com") or href.startswith("https://aoitgroup.com"):
            href = urllib.parse.urlsplit(href).path or "/"
        for code in LANGS:
            if href.startswith(f"/{code}/"):
                href = href[len(code) + 1:]
                break
        if href.startswith("/"):
            parts = urllib.parse.urlsplit(href)
            href, query = parts.path, parts.query
        if href in {"/connect/login", "/sso_login", "/index.php"}:
            anchor["href"] = f"https://www.aoitgroup.com{href}"
            continue
        suffix = "/" if href.endswith("/") and href != "/" else ""
        href = PATH_ALIASES.get(href.rstrip("/") or "/", href)
        if href.startswith("/") and not href.startswith(("/application/", "/concrete/", "/packages/", "/en/", "/fr/", "/es/", "/de/", "/it/")):
            href = f"/{lang}" + href
        if query:
            href += "?" + query
        anchor["href"] = href


def language_switcher(soup, lang):
    old = soup.select_one(".demo-language-switcher")
    if not old: return
    old.select_one("summary span").string = lang.upper()
    nav = old.select_one("nav")
    nav.clear()
    for code, name in LANGS.items():
        if code == lang: continue
        a = soup.new_tag("a", href=f"/{code}/", role="menuitem", lang=code, hreflang=code)
        span = soup.new_tag("span"); span.string = code.upper(); a.append(span)
        small = soup.new_tag("small"); small.string = name; a.append(small)
        nav.append(a)


pages = source_pages()
print(f"Source pages: {len(pages)}")
targets = sys.argv[1:] or list(LANGS)
for lang in targets:
    for page_no, source in enumerate(pages, 1):
        rel = source.relative_to(ROOT)
        raw = source.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "lxml")
        nodes = []
        attrs = []
        for node in soup.find_all(string=True):
            if isinstance(node, Comment) or node.parent.name in {"script", "style", "noscript", "svg", "code", "pre"}: continue
            clean = translatable(str(node))
            if clean: nodes.append((node, clean))
        for tag in soup.find_all(True):
            for attr in ("alt", "title", "placeholder", "aria-label"):
                clean = translatable(tag.get(attr, ""))
                if clean: attrs.append((tag, attr, clean))
        strings = list(dict.fromkeys([text for _, text in nodes] + [text for _, _, text in attrs]))
        if lang != "en": translate_batches(strings, lang)
        for node, text in nodes:
            translated = text if lang == "en" else CACHE.get(f"{lang}\0{text}", text)
            original = str(node); lead = original[:len(original)-len(original.lstrip())]; trail = original[len(original.rstrip()):]
            node.replace_with(lead + translated + trail)
        for tag, attr, text in attrs:
            tag[attr] = text if lang == "en" else CACHE.get(f"{lang}\0{text}", text)
        add_seo(soup, lang, rel)
        localize_links(soup, lang)
        language_switcher(soup, lang)
        target = ROOT / lang / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(soup), encoding="utf-8")
        if page_no % 25 == 0: print(f"{lang}: {page_no}/{len(pages)}")
print("Translation complete")

# The public root is the English localized homepage.
if not sys.argv[1:] or "en" in targets:
    (ROOT / "index.html").write_text((ROOT / "en" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
