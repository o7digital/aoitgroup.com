from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = (ROOT / "index.html").read_text(encoding="utf-8")
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
        f'<a href="/{code}/" lang="{code}" hreflang="{code}" '
        f'aria-current="{"page" if code == active else "false"}">{code.upper()}</a>'
        for code in LANGUAGES
    )
    return f'''<nav class="demo-language-switcher" aria-label="Language selector">{links}</nav>
<style>
.demo-language-switcher{{position:fixed;right:16px;bottom:16px;z-index:99999;display:flex;gap:4px;padding:6px;background:#151b2d;border:1px solid #2b3857;border-radius:7px;box-shadow:0 8px 30px #0005}}
.demo-language-switcher a{{padding:7px 9px;color:#fff;text-decoration:none;font:700 12px/1 Arial,sans-serif;border-radius:4px}}
.demo-language-switcher a:hover,.demo-language-switcher a[aria-current="page"]{{background:#009fe3}}
</style>'''


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
