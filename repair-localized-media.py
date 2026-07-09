#!/usr/bin/env python3
import re
import html
from pathlib import Path

ROOT = Path(__file__).parent
LANGS = ("en", "fr", "es", "de", "it")
SKIP_DIRS = set(LANGS) | {"application", "concrete", "packages", ".git", ".vercel"}
PICTURE_RE = re.compile(r"<picture\b[^>]*>.*?</picture>", re.I | re.S)
ALT_RE = re.compile(r'(<img\b[^>]*\balt=)(["\'])(.*?)(\2)', re.I | re.S)
EMPTY_MEDIA_RE = re.compile(
    r'data-src="\s*(?:1x)?\s*,?\s*(?:2x)?\s*"|<img\b[^>]*\bsrc="\s*"',
    re.I | re.S,
)
REAL_IMAGE_RE = re.compile(
    r'\bdata-src="([^"]*/application/files/cache/thumbnails/[^"\s]+\.(?:webp|png|jpe?g))'
    r'(?:\s+\d+x)?',
    re.I,
)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
LEADING_HTML_TEXT_RE = re.compile(r"^html(?=<html\b)", re.I)
INDEX_BODY_HTML_RE = re.compile(r"^(<html\b[^>]*>)<body>html\s*", re.I)


PLACEHOLDER = (
    "data:image/svg+xml,%3Csvg%20width%3D%27900%27%20height%3D%27550%27%20"
    "viewBox%3D%270%200%20900%20550%27%20xmlns%3D%27http%3A%2F%2Fwww.w3.org"
    "%2F2000%2Fsvg%27%3E%3Crect%20x%3D%270%27%20y%3D%270%27%20width%3D%27900"
    "%27%20height%3D%27550%27%20rx%3D%275%27%20ry%3D%275%27%20fill%3D%27"
    "transparent%27%20%2F%3E%3C%2Fsvg%3E"
)
DEFAULT_FALLBACK_IMAGE = "/application/files/cache/thumbnails/e981ab4a8336508ab2c8fe63fd8e6fae.png"


def source_pages():
    home_source = ROOT / "index.php?cID=506.html"
    if home_source.exists():
        yield home_source, Path("index.html")
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.as_posix() == "index.html" and home_source.exists():
            continue
        if rel.parts[0] in SKIP_DIRS or "?" in path.name:
            continue
        yield path, rel


def image_alts(picture):
    return [match.group(3) for match in ALT_RE.finditer(picture)]


def apply_alts(picture, alts):
    iterator = iter(alts)

    def replace(match):
        try:
            alt = next(iterator)
        except StopIteration:
            return match.group(0)
        return f"{match.group(1)}{match.group(2)}{alt}{match.group(4)}"

    return ALT_RE.sub(replace, picture)


def page_heading(html_text):
    match = H1_RE.search(html_text)
    if not match:
        return ""
    text = TAG_RE.sub("", match.group(1))
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def first_real_image(pictures, current_index):
    ordered = list(pictures[current_index + 1 :]) + list(pictures[:current_index])
    for picture in ordered:
        if EMPTY_MEDIA_RE.search(picture):
            continue
        match = REAL_IMAGE_RE.search(picture)
        if match:
            return match.group(1)
    return None


def fallback_picture(image_url, alt):
    escaped_alt = html.escape(alt, quote=True)
    return (
        "<picture>"
        '<img class="banner__image" data-lazyload="image" loading="lazy" '
        f'width="900" height="550" src="{PLACEHOLDER}" '
        f'data-src="{image_url}" alt="{escaped_alt}"/>'
        "</picture>"
    )


def repair_empty_source_pictures(source_html):
    pictures = PICTURE_RE.findall(source_html)
    if not pictures:
        return source_html, 0

    heading = page_heading(source_html)
    replacements = []
    changed = 0
    for index, picture in enumerate(pictures):
        if not EMPTY_MEDIA_RE.search(picture):
            replacements.append(picture)
            continue
        image_url = first_real_image(pictures, index)
        if not image_url:
            image_url = DEFAULT_FALLBACK_IMAGE
        replacements.append(fallback_picture(image_url, heading))
        changed += 1

    if not changed:
        return source_html, 0

    index = 0

    def replace(_match):
        nonlocal index
        restored = replacements[index]
        index += 1
        return restored

    return PICTURE_RE.sub(replace, source_html), changed


def restore_pictures(source_html, target_html):
    source_pictures = PICTURE_RE.findall(source_html)
    target_pictures = PICTURE_RE.findall(target_html)
    if not source_pictures and not target_pictures:
        return target_html, "no-media"
    if len(source_pictures) != len(target_pictures):
        return target_html, f"picture-count {len(target_pictures)} != {len(source_pictures)}"

    replacements = []
    for source_picture, target_picture in zip(source_pictures, target_pictures):
        replacements.append(apply_alts(source_picture, image_alts(target_picture)))

    index = 0

    def replace(_match):
        nonlocal index
        restored = replacements[index]
        index += 1
        return restored

    return PICTURE_RE.sub(replace, target_html), "restored"


def remove_visible_html_text(html_text):
    html_text = LEADING_HTML_TEXT_RE.sub("", html_text, count=1)
    html_text = INDEX_BODY_HTML_RE.sub(r"\1\n<head>\n", html_text, count=1)
    return html_text


def main():
    source_fixed = restored = skipped = unchanged = 0
    page_list = list(source_pages())
    for source, _rel in page_list:
        source_html = source.read_text(encoding="utf-8", errors="ignore")
        repaired = remove_visible_html_text(source_html)
        repaired, changed = repair_empty_source_pictures(repaired)
        if changed or repaired != source_html:
            source.write_text(repaired, encoding="utf-8")
            source_fixed += changed

    for source, rel in page_list:
        source_html = source.read_text(encoding="utf-8", errors="ignore")
        for lang in LANGS:
            target = ROOT / lang / rel
            if not target.exists():
                skipped += 1
                print(f"skip missing: {target.relative_to(ROOT)}")
                continue
            target_html = target.read_text(encoding="utf-8", errors="ignore")
            repaired, status = restore_pictures(source_html, target_html)
            repaired = remove_visible_html_text(repaired)
            if repaired != target_html:
                target.write_text(repaired, encoding="utf-8")
                restored += 1
            elif status == "no-media" or repaired == target_html:
                unchanged += 1
            else:
                skipped += 1
                print(f"skip {status}: {target.relative_to(ROOT)}")

    root_home = ROOT / "index.html"
    en_home = ROOT / "en" / "index.html"
    if en_home.exists():
        root_home.write_text(en_home.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"source_fixed={source_fixed} restored={restored} unchanged={unchanged} skipped={skipped}")


if __name__ == "__main__":
    main()
