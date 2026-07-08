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
_template_soup = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "lxml")
SWITCHER_TEMPLATE = _template_soup.select_one(".demo-language-switcher")
SWITCHER_STYLE = next(
    (style for style in _template_soup.find_all("style") if ".demo-language-switcher" in style.get_text()),
    None,
)

# Google Translate is useful for the long-form first pass, but it must not be
# allowed to translate brand names or compose UI fragments independently.  Keep
# this editorial layer deterministic so a full regeneration cannot reintroduce
# the same mistakes.
EXACT_TRANSLATIONS = {
    "fr": {
        "A&O IT Group": "A&O IT Group",
        "A&O IT Group | Global IT Support Services & Cyber Security": "A&O IT Group | Services informatiques globaux et cybersécurité",
        "Global IT Services": "Services informatiques globaux",
        "Global IT Services & support": "Services informatiques globaux et assistance",
        "IT Services <span>global</span>": "Services informatiques <span>globaux</span>",
        "Supporting businesses in over 130 countries.": "Au service des entreprises dans plus de 130 pays.",
        "Contact the Team": "Contacter notre équipe",
        "IT Managed Services": "Services informatiques gérés",
        "IT Project Services": "Services de projets informatiques",
        "Global IT Engineering Services": "Services globaux d’ingénierie informatique",
        "Cyber Security Solutions": "Solutions de cybersécurité",
        "Cyber Assurance": "Évaluation et assurance cybersécurité",
        "Cyber Operations": "Opérations de cybersécurité",
        "Red Teaming": "Red Teaming",
        "One Solution": "One Solution",
        "FieldView": "FieldView",
        "TrainView": "TrainView",
        "LinkedIn": "LinkedIn",
        "A&O Corsaire designs autonomous systems that think, decide and execute. Let's set yours up.": "A&O Corsaire conçoit des systèmes autonomes capables de réfléchir, de décider et d’agir. Construisons le vôtre.",
    },
    "es": {
        "A&O IT Group": "A&O IT Group",
        "A&O IT Group | Global IT Support Services & Cyber Security": "A&O IT Group | Servicios informáticos globales y ciberseguridad",
        "Global IT Services": "Servicios informáticos globales",
        "Global IT Services & support": "Servicios informáticos globales y soporte",
        "IT Services <span>global</span>": "Servicios informáticos <span>globales</span>",
        "Supporting businesses in over 130 countries.": "Ayudamos a empresas en más de 130 países.",
        "Contact the Team": "Contactar con el equipo",
        "IT Managed Services": "Servicios informáticos gestionados",
        "IT Project Services": "Servicios de proyectos informáticos",
        "Global IT Engineering Services": "Servicios globales de ingeniería informática",
        "Cyber Security Solutions": "Soluciones de ciberseguridad",
        "Cyber Assurance": "Evaluación y garantía de ciberseguridad",
        "Cyber Operations": "Operaciones de ciberseguridad",
        "Red Teaming": "Red Teaming",
        "One Solution": "One Solution",
        "FieldView": "FieldView",
        "TrainView": "TrainView",
        "LinkedIn": "LinkedIn",
    },
    "de": {
        "A&O IT Group": "A&O IT Group",
        "A&O IT Group | Global IT Support Services & Cyber Security": "A&O IT Group | Globale IT-Services und Cybersicherheit",
        "Global IT Services": "Globale IT-Services",
        "Global IT Services & support": "Globale IT-Services und Support",
        "IT Services <span>global</span>": "<span>Globale</span> IT-Services",
        "Supporting businesses in over 130 countries.": "Wir unterstützen Unternehmen in über 130 Ländern.",
        "Contact the Team": "Team kontaktieren",
        "IT Managed Services": "Managed IT Services",
        "IT Project Services": "IT-Projektservices",
        "Global IT Engineering Services": "Globale IT-Engineering-Services",
        "Cyber Security Solutions": "Cybersicherheitslösungen",
        "Cyber Assurance": "Cyber Security Assurance",
        "Cyber Operations": "Cyber Security Operations",
        "Red Teaming": "Red Teaming",
        "One Solution": "One Solution",
        "FieldView": "FieldView",
        "TrainView": "TrainView",
        "LinkedIn": "LinkedIn",
    },
    "it": {
        "A&O IT Group": "A&O IT Group",
        "A&O IT Group | Global IT Support Services & Cyber Security": "A&O IT Group | Servizi IT globali e sicurezza informatica",
        "Global IT Services": "Servizi IT globali",
        "Global IT Services & support": "Servizi IT globali e assistenza",
        "IT Services <span>global</span>": "Servizi IT <span>globali</span>",
        "Supporting businesses in over 130 countries.": "Supportiamo le aziende in oltre 130 Paesi.",
        "Contact the Team": "Contatta il team",
        "IT Managed Services": "Servizi IT gestiti",
        "IT Project Services": "Servizi per progetti IT",
        "Global IT Engineering Services": "Servizi globali di ingegneria IT",
        "Cyber Security Solutions": "Soluzioni di sicurezza informatica",
        "Cyber Assurance": "Valutazione e garanzia della sicurezza informatica",
        "Cyber Operations": "Operazioni di sicurezza informatica",
        "Red Teaming": "Red Teaming",
        "One Solution": "One Solution",
        "FieldView": "FieldView",
        "TrainView": "TrainView",
        "LinkedIn": "LinkedIn",
    },
}

BRAND_VARIANTS = {
    "fr": ("Groupe informatique A&O", "Groupe IT A&O", "A&O Groupe informatique"),
    "es": ("Grupo A&O TI", "Grupo TI A&O", "Grupo de TI A&O", "Grupo de A&O TI"),
    "de": ("A&O IT-Gruppe", "A&O-Gruppe IT"),
    "it": ("Gruppo IT A&O", "Gruppo A&O IT", "gruppo IT A&O", "gruppo A&O IT"),
}

TERM_VARIANTS = {
    "fr": {"Équipe Rouge": "Red Teaming", "Équipe rouge": "Red Teaming", "Lié à": "LinkedIn"},
    "es": {"Equipo rojo": "Red Teaming", "equipo rojo": "Red Teaming"},
    "de": {"Rotes Teaming": "Red Teaming", "rotes Teaming": "Red Teaming"},
    "it": {"Squadra Rossa": "Red Teaming", "squadra rossa": "Red Teaming", "Visualizzazione campo": "FieldView"},
}


def polish_translation(source, translated, lang):
    translated = EXACT_TRANSLATIONS.get(lang, {}).get(source, translated)
    translated = translated.replace("\u200b", "")
    for variant in BRAND_VARIANTS.get(lang, ()):
        translated = translated.replace(variant, "A&O IT Group")
    for variant, preferred in TERM_VARIANTS.get(lang, {}).items():
        translated = translated.replace(variant, preferred)
    return translated


def polish_composed_content(soup, lang):
    """Fix phrases whose grammar crosses inline HTML element boundaries."""
    heading = soup.select_one("h1.hero__heading")
    if heading and lang in EXACT_TRANSLATIONS:
        fragment = BeautifulSoup(
            EXACT_TRANSLATIONS[lang]["IT Services <span>global</span>"], "lxml"
        ).body
        heading.clear()
        for child in list(fragment.contents):
            heading.append(child)


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


def language_switcher(soup, lang, rel):
    old = soup.select_one(".demo-language-switcher")
    if not old:
        if not SWITCHER_TEMPLATE or not soup.body:
            return
        fragment = BeautifulSoup(str(SWITCHER_TEMPLATE), "lxml").select_one(".demo-language-switcher")
        soup.body.append(fragment)
        old = soup.select_one(".demo-language-switcher")
        if SWITCHER_STYLE and not any(".demo-language-switcher" in s.get_text() for s in soup.find_all("style")):
            soup.body.append(BeautifulSoup(str(SWITCHER_STYLE), "lxml").style)
    old.select_one("summary span").string = lang.upper()
    nav = old.select_one("nav")
    nav.clear()
    slug = "" if rel.as_posix() == "index.html" else rel.with_suffix("").as_posix()
    for code, name in LANGS.items():
        if code == lang: continue
        target = f"/{code}/" + slug
        a = soup.new_tag("a", href=target, role="menuitem", lang=code, hreflang=code)
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
            translated = polish_translation(text, translated, lang)
            original = str(node); lead = original[:len(original)-len(original.lstrip())]; trail = original[len(original.rstrip()):]
            node.replace_with(lead + translated + trail)
        for tag, attr, text in attrs:
            translated = text if lang == "en" else CACHE.get(f"{lang}\0{text}", text)
            tag[attr] = polish_translation(text, translated, lang)
        polish_composed_content(soup, lang)
        add_seo(soup, lang, rel)
        localize_links(soup, lang)
        language_switcher(soup, lang, rel)
        target = ROOT / lang / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        # U+200B occasionally arrives from copied CMS list markup. It has no
        # semantic value here and creates inconsistent search/indexing text.
        target.write_text(str(soup).replace("\u200b", ""), encoding="utf-8")
        if page_no % 25 == 0: print(f"{lang}: {page_no}/{len(pages)}")
print("Translation complete")

# The public root is the English localized homepage.
if not sys.argv[1:] or "en" in targets:
    (ROOT / "index.html").write_text((ROOT / "en" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
