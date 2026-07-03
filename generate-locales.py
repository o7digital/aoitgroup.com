from pathlib import Path
import re

ROOT = Path(__file__).parent
SOURCE = (ROOT / "index.html").read_text(encoding="utf-8")
# Regeneration is idempotent even when the root page already contains a
# previously generated switcher.
SOURCE = re.sub(
    r'<!-- language-switcher:start -->.*?<!-- language-switcher:end -->\s*',
    '',
    SOURCE,
    flags=re.S,
)
SOURCE = re.sub(
    r'<nav class="demo-language-switcher".*?</style>\s*',
    '',
    SOURCE,
    count=1,
    flags=re.S,
)
BASE_URL = "https://demo.aoitgroup.com"

LANGUAGES = {
    "en": {
        "name": "English",
        "title": "A&O IT Group | Global IT Support Services & Cyber Security",
        "description": "Global IT services, managed support and cyber security solutions.",
        "translations": {},
    },
    "fr": {
        "name": "Français",
        "title": "A&O IT Group | Services informatiques mondiaux et cybersécurité",
        "description": "Services informatiques mondiaux, support managé et solutions de cybersécurité.",
        "translations": {
            "Global IT Services": "Services informatiques mondiaux",
            "Contact the Team": "Contacter l’équipe",
            "IT Services": "Services informatiques",
            "Cyber Security": "Cybersécurité",
            "Find out more": "En savoir plus",
            "Public Sector": "Secteur public",
            "Energy &amp; Utilities": "Énergie et services publics",
            "A Global IT security &amp; support partner you can rely on": "Un partenaire mondial fiable pour votre sécurité et votre support informatique",
        },
    },
    "es": {
        "name": "Español",
        "title": "A&O IT Group | Servicios informáticos globales y ciberseguridad",
        "description": "Servicios informáticos globales, soporte gestionado y soluciones de ciberseguridad.",
        "translations": {
            "Global IT Services": "Servicios informáticos globales",
            "Contact the Team": "Contactar con el equipo",
            "IT Services": "Servicios informáticos",
            "Cyber Security": "Ciberseguridad",
            "Find out more": "Más información",
            "Public Sector": "Sector público",
            "Energy &amp; Utilities": "Energía y servicios públicos",
            "A Global IT security &amp; support partner you can rely on": "Un socio global de seguridad y soporte informático en quien confiar",
        },
    },
    "de": {
        "name": "Deutsch",
        "title": "A&O IT Group | Globale IT-Services und Cybersicherheit",
        "description": "Globale IT-Services, Managed Support und Cybersicherheitslösungen.",
        "translations": {
            "Global IT Services": "Globale IT-Services",
            "Contact the Team": "Team kontaktieren",
            "IT Services": "IT-Services",
            "Cyber Security": "Cybersicherheit",
            "Find out more": "Mehr erfahren",
            "Public Sector": "Öffentlicher Sektor",
            "Energy &amp; Utilities": "Energie und Versorgung",
            "A Global IT security &amp; support partner you can rely on": "Ein globaler Partner für IT-Sicherheit und Support, auf den Sie sich verlassen können",
        },
    },
    "it": {
        "name": "Italiano",
        "title": "A&O IT Group | Servizi IT globali e sicurezza informatica",
        "description": "Servizi IT globali, supporto gestito e soluzioni di sicurezza informatica.",
        "translations": {
            "Global IT Services": "Servizi IT globali",
            "Contact the Team": "Contatta il team",
            "IT Services": "Servizi IT",
            "Cyber Security": "Sicurezza informatica",
            "Find out more": "Scopri di più",
            "Public Sector": "Settore pubblico",
            "Energy &amp; Utilities": "Energia e servizi pubblici",
            "A Global IT security &amp; support partner you can rely on": "Un partner globale affidabile per la sicurezza e il supporto IT",
        },
    },
}


def seo_head(code: str) -> str:
    links = "\n".join(
        f'<link rel="alternate" hreflang="{lang}" href="{BASE_URL}/{lang}/">'
        for lang in LANGUAGES
    )
    return (
        f'<link rel="canonical" href="{BASE_URL}/{code}/">\n'
        f'{links}\n'
        f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/en/">'
    )


def switcher(active: str) -> str:
    links = "".join(
        f'<a role="menuitem" href="/{code}/" lang="{code}" hreflang="{code}">'
        f'<span>{code.upper()}</span><small>{config["name"]}</small></a>'
        for code, config in LANGUAGES.items() if code != active
    )
    return f'''<!-- language-switcher:start -->
<div class="demo-language-switcher">
  <details>
    <summary aria-label="Select language"><span>{active.upper()}</span><i aria-hidden="true"></i></summary>
    <nav role="menu" aria-label="Language selector">{links}</nav>
  </details>
</div>
<style>
.demo-language-switcher{{position:absolute;top:5px;left:24px;z-index:99999;color:#fff;font-family:Arial,sans-serif}}
.demo-language-switcher details{{position:relative}}
.demo-language-switcher summary{{display:flex;align-items:center;gap:8px;min-width:52px;padding:6px 9px;cursor:pointer;list-style:none;font-size:12px;font-weight:700;letter-spacing:.08em;transition:color .2s ease}}
.demo-language-switcher summary::-webkit-details-marker{{display:none}}
.demo-language-switcher summary:hover{{color:#00a4ed}}
.demo-language-switcher summary i{{width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-2px) rotate(45deg);transition:transform .2s ease}}
.demo-language-switcher details[open] summary i{{transform:translateY(2px) rotate(225deg)}}
.demo-language-switcher nav{{position:absolute;top:100%;left:0;min-width:148px;padding:7px 0;background:#171d30;border-top:2px solid #00a4ed;box-shadow:0 12px 28px #0007}}
.demo-language-switcher a{{display:flex;align-items:center;gap:12px;padding:10px 14px;color:#fff;text-decoration:none;font-size:12px;font-weight:700;letter-spacing:.06em;white-space:nowrap}}
.demo-language-switcher a span{{width:22px;color:#00a4ed}}
.demo-language-switcher a small{{font-size:11px;font-weight:400;letter-spacing:0;color:#c9cede}}
.demo-language-switcher a:hover{{background:#222b43}}
@media(max-width:700px){{.demo-language-switcher{{position:fixed;top:12px;right:12px}}.demo-language-switcher summary{{background:#171d30;border-radius:3px}}.demo-language-switcher nav{{left:auto;right:0}}}}
</style>
<!-- language-switcher:end -->'''


for code, config in LANGUAGES.items():
    html = SOURCE
    html = html.replace('<html lang="en"', f'<html lang="{code}"', 1)
    start = html.find("<title>")
    end = html.find("</title>", start) + len("</title>")
    html = html[:start] + f"<title>{config['title']}</title>" + html[end:]
    html = html.replace(
        '<meta name="description" content="A&amp;O IT Group can rapidly remove all your IT services and cyber security headaches. See how we can help your business today.">',
        f'<meta name="description" content="{config["description"]}">',
        1,
    )
    canonical_start = html.find('<link rel="canonical"')
    canonical_end = html.find(">", canonical_start) + 1
    html = html[:canonical_start] + seo_head(code) + html[canonical_end:]
    for original, translated in config["translations"].items():
        html = html.replace(original, translated)
    html = html.replace("</body>", switcher(code) + "\n</body>", 1)
    if '<script src="/olivia-ai.js" defer></script>' not in html:
        html = html.replace("</body>", '<script src="/olivia-ai.js" defer></script>\n</body>', 1)
    output = ROOT / code / "index.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(html, encoding="utf-8")

# The deployed root is the English entry point, so visitors see the language
# selector immediately without first knowing the /en/ URL.
(ROOT / "index.html").write_text(
    (ROOT / "en" / "index.html").read_text(encoding="utf-8"),
    encoding="utf-8",
)

print("Generated: " + ", ".join(f"/{code}/" for code in LANGUAGES))
