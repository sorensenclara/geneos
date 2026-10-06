#!/usr/bin/env python3
"""Genera el sitio estático de GENEOS en ./public a partir de ./templates y ./static.

Uso:
    pip install jinja2
    python build.py                       # sitio servido desde la raíz del dominio
    BASE_PATH=/geneos python build.py     # p. ej. GitHub Pages de proyecto

Variables de entorno:
    BASE_PATH      subcarpeta donde se publica (vacío en dominio propio)
    SITE_URL       URL pública donde se sirve este build (para redirecciones del formulario)
    CANONICAL_URL  dominio oficial para canonical, sitemap y datos estructurados
"""
import json
import os
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "public"
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
CANONICAL_URL = os.environ.get("CANONICAL_URL", "https://geneos.coop.ar").rstrip("/")
SITE_URL = (os.environ.get("SITE_URL") or CANONICAL_URL).rstrip("/")
TODAY = date.today().isoformat()

SITE = {
    "name": "GENEOS",
    "legal_name": "Cooperativa de Trabajo GENEOS Ltda.",
    "tagline": "Cooperativa de Software Libre",
    "whatsapp": "5492494521418",
    "whatsapp_label": "+549 2494 521418",
    "phone": "+54 9 249 452-1418",
    "email": "info@geneos.com.ar",
    "address": "Alem 1015 - Tandil",
    "street": "Alem 1015",
    "city": "Tandil",
    "province": "Buenos Aires",
    "postal_code": "B7000",
    "country": "AR",
    "region": "Buenos Aires - Argentina",
    "maps": "https://maps.app.goo.gl/SG3oBGYpz7ttdvbB8",
    # Endpoint del formulario de contacto. FormSubmit reenvía al mail sin backend
    # (la primera vez manda un mail de activación). Se puede cambiar por Formspree,
    # un endpoint propio en Django, etc.
    "form_action": "https://formsubmit.co/info@geneos.com.ar",
    "social": [
        ("Facebook", "https://www.facebook.com/coopgeneos/", "facebook"),
        ("Instagram", "https://www.instagram.com/coopgeneos/", "instagram"),
        ("X / Twitter", "https://x.com/CoopGENEOS", "twitter"),
        ("LinkedIn", "https://ar.linkedin.com/company/geneos-coop", "linkedin"),
    ],
}

# Cada página: plantilla, ruta, título (<60 car.), descripción (<160 car.),
# miga de pan (nombre corto), imagen para redes y prioridad en el sitemap.
PAGES = [
    dict(tpl="index.html", out="",
         title="GENEOS | Cooperativa de software libre: ERP, apps y webs",
         description="Cooperativa de software libre de Argentina. Desarrollamos software de gestión Odoo, apps, sitios web y campus Moodle para Argentina y Latinoamérica.",
         crumb="Inicio", priority="1.0"),
    dict(tpl="servicios.html", out="servicios/",
         title="Servicios de desarrollo de software libre | GENEOS",
         description="Software de gestión Odoo, staff augmentation, apps y sitios web, plataformas Moodle y diseño. Soluciones con software libre para Argentina y Latam.",
         crumb="Servicios", priority="0.9"),
    dict(tpl="software-de-gestion.html", out="software-de-gestion-completo/", parent="servicios/",
         title="Software de gestión ERP para pymes basado en Odoo | GERP",
         description="GERP: sistema de gestión online basado en Odoo Community para pymes. Inventario, compras, ventas, facturación y contabilidad, con implementación y soporte.",
         crumb="Software de Gestión GERP", og="2026/01/Beneficios-GERP-1536x1029-1-1024x686.webp", priority="0.9"),
    dict(tpl="gema.html", out="software-gestion-matafuegos-extintores/", parent="servicios/",
         title="Software para talleres de matafuegos y extintores | GEMA",
         description="GEMA es el sistema online para talleres de recarga de matafuegos: control de vencimientos, historial de servicios, obleas, presupuestos y avisos a clientes.",
         crumb="Software de Matafuegos GEMA", og="2024/04/5-1024x637.webp", priority="0.9"),
    dict(tpl="geagro.html", out="software-agropecuario-geagro/", parent="servicios/",
         title="Software agropecuario GEAGRO: gestión agrícola y viñedos",
         description="GEAGRO, software de gestión agropecuaria: campañas, lotes, clima, insumos y acopio con GEAGRO CEREALES, y gestión de viñedos con GEAGRO VID.",
         crumb="Software Agropecuario GEAGRO", og="geagro/geagro-hero.webp", priority="0.9"),
    dict(tpl="staff-augmentation.html", out="staff-augmentation/", parent="servicios/",
         title="Staff augmentation: desarrolladores para tu equipo | GENEOS",
         description="Sumá desarrolladores, DevOps, analistas, PM y diseñadores UX/UI de Argentina a tu equipo. Staff augmentation nearshore para empresas de Latinoamérica.",
         crumb="Staff Augmentation", priority="0.8"),
    dict(tpl="apps-y-webs.html", out="desarrollo-apps-sitios-web-cooperativos/", parent="servicios/",
         title="Desarrollo de apps y sitios web a medida | GENEOS",
         description="Desarrollo de sitios web, tiendas online y apps móviles con WordPress, Django, Angular y React Native. Tecnología libre y diseño centrado en las personas.",
         crumb="Apps y Sitios Web", priority="0.8"),
    dict(tpl="e-learning.html", out="plataformas-e-learning-lms-moodle/", parent="servicios/",
         title="Plataformas e-learning y campus virtual Moodle | GENEOS",
         description="Creamos campus virtuales en Moodle para universidades, institutos y empresas: diseño a medida, gamificación con H5P, capacitación y soporte. Argentina y Latam.",
         crumb="E-learning Moodle", og="2023/11/notebook_moodle.webp", priority="0.8"),
    dict(tpl="diseno.html", out="diseno-sitios-web-identidades/", parent="servicios/",
         title="Diseño web, identidad visual y comunicación | GENEOS",
         description="Diseño de sitios web UX/UI, identidades visuales y estrategia de comunicación digital para cooperativas, pymes e instituciones de Argentina y Latinoamérica.",
         crumb="Diseño y Comunicación", priority="0.8"),
    dict(tpl="quienes-somos.html", out="quienes-somos/",
         title="Quiénes somos: cooperativa de software libre | GENEOS",
         description="Somos GENEOS, cooperativa de trabajo de Tandil que desarrolla soluciones tecnológicas con software libre. Conocé al equipo, nuestra misión y visión.",
         crumb="Quiénes somos", og="elementor/thumbs/5-rh26ect4j6zr6ywqu4myqmyj8w1qub7ot9nx5za9i8.webp", priority="0.7"),
    dict(tpl="recursos-graficos.html", out="recursos-graficos/", parent="quienes-somos/",
         title="Recursos gráficos y manual de marca | GENEOS",
         description="Descargá los isologotipos de GENEOS y GERP en SVG y PNG y consultá el manual de marca con los lineamientos de uso de la identidad visual.",
         crumb="Recursos Gráficos", priority="0.3"),
    dict(tpl="contacto.html", out="contacto-geneos/",
         title="Contacto | GENEOS, cooperativa de software libre",
         description="Escribinos por WhatsApp, mail o formulario. Desarrollo de software, Odoo, WordPress, Moodle y diseño para Argentina y Latinoamérica. Alem 1015, Tandil.",
         crumb="Contacto", priority="0.7"),
    dict(tpl="404.html", out="404.html", title="Página no encontrada | GENEOS",
         description="La página que buscás no existe.", crumb="Error 404", noindex=True),
]
PAGE_BY_OUT = {p["out"]: p for p in PAGES}

# URLs viejas (WordPress) -> nuevas. Se generan _redirects (Netlify/Cloudflare) y .htaccess (Apache).
REDIRECTS = {
    "/index.php/apps-y-sitios-web/": "/desarrollo-apps-sitios-web-cooperativos/",
    "/index.php/plataformas-e-learning/": "/plataformas-e-learning-lms-moodle/",
    "/index.php/disenamos-sitios-web-identidades/": "/diseno-sitios-web-identidades/",
    "/index.php/plataformas-de-gestion/": "/software-de-gestion-completo/",
    "/index.php/software-de-gestion/": "/software-de-gestion-completo/",
    "/index.php/app-webs/": "/desarrollo-apps-sitios-web-cooperativos/",
    "/index.php/diseno-grafico-y-web/": "/diseno-sitios-web-identidades/",
    "/index.php/contact/": "/contacto-geneos/",
    "/apps-y-sitios-web/": "/desarrollo-apps-sitios-web-cooperativos/",
    "/plataformas-e-learning/": "/plataformas-e-learning-lms-moodle/",
    "/disenamos-sitios-web-identidades/": "/diseno-sitios-web-identidades/",
    "/contact/": "/contacto-geneos/",
}


def url(path=""):
    """Ruta interna respetando BASE_PATH."""
    if path.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return path
    return f"{BASE_PATH}/{path.lstrip('/')}"


def asset(path):
    return url("assets/" + path.lstrip("/"))


def img(path):
    """Imagen en assets/img. Las rasterizadas se publican como .webp."""
    p = Path(path)
    if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
        p = p.with_suffix(".webp")
    return asset("img/" + p.as_posix())


def abs_url(path=""):
    """URL absoluta en el dominio oficial (canonical, schema, sitemap)."""
    return f"{CANONICAL_URL}/{path.lstrip('/')}"


_icon_cache = {}


def icon(name, cls="icon"):
    if name not in _icon_cache:
        _icon_cache[name] = (ROOT / "templates" / "icons" / f"{name}.svg").read_text()
    svg = _icon_cache[name].replace("<svg ", f'<svg class="{cls}" ', 1)
    return Markup(svg)


def wa(text=""):
    from urllib.parse import quote
    return f"https://wa.me/{SITE['whatsapp']}" + (f"?text={quote(text)}" if text else "")


def jsonld(data):
    """Bloque <script type=application/ld+json> seguro."""
    raw = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return Markup(f'<script type="application/ld+json">{raw}</script>')


def breadcrumbs(page):
    """Lista [(nombre, ruta)] desde Inicio hasta la página."""
    chain, p = [], page
    while p:
        chain.insert(0, (p["crumb"], p["out"]))
        p = PAGE_BY_OUT.get(p.get("parent")) if p.get("parent") is not None else None
    if page["out"] != "":
        chain.insert(0, ("Inicio", ""))
    return chain


def crumbs_schema(crumbs):
    return [{"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(href)}
            for i, (name, href) in enumerate(crumbs)]


def faq_entities(items):
    import re
    return [{"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in items]


SERVICE_PAGES = ["software-de-gestion-completo/", "software-gestion-matafuegos-extintores/",
                 "software-agropecuario-geagro/", "staff-augmentation/",
                 "desarrollo-apps-sitios-web-cooperativos/", "plataformas-e-learning-lms-moodle/",
                 "diseno-sitios-web-identidades/"]


def service_items():
    return [{"@type": "ListItem", "position": i + 1, "name": PAGE_BY_OUT[o]["crumb"], "url": abs_url(o)}
            for i, o in enumerate(SERVICE_PAGES)]


def org_schema():
    s = SITE
    return {
        "@type": ["Organization", "LocalBusiness"],
        "@id": abs_url("#organizacion"),
        "name": s["name"],
        "legalName": s["legal_name"],
        "alternateName": "GENEOS Cooperativa de Software Libre",
        "url": abs_url(),
        "logo": abs_url("assets/img/favicon-192.png"),
        "image": abs_url("assets/img/og-geneos.webp"),
        "description": "Cooperativa de trabajo de software libre que desarrolla software de gestión, aplicaciones, sitios web y plataformas e-learning.",
        "email": s["email"],
        "telephone": s["phone"],
        "address": {"@type": "PostalAddress", "streetAddress": s["street"], "addressLocality": s["city"],
                    "addressRegion": s["province"], "postalCode": s["postal_code"], "addressCountry": s["country"]},
        "hasMap": s["maps"],
        "areaServed": [{"@type": "Country", "name": "Argentina"}, {"@type": "Place", "name": "Latinoamérica"}],
        "knowsAbout": ["Software libre", "Odoo", "ERP", "Software agropecuario", "Django", "Python", "WordPress", "Moodle", "Angular",
                       "React Native", "Desarrollo web", "Diseño UX/UI", "Staff augmentation"],
        "memberOf": {"@type": "Organization", "name": "FACTTIC", "url": "https://facttic.org.ar/"},
        "sameAs": [href for _, href, _ in s["social"]],
        "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "telephone": s["phone"],
                         "email": s["email"], "availableLanguage": ["es"], "areaServed": ["AR", "419"]},
    }


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.globals.update(site=SITE, url=url, asset=asset, img=img, icon=icon, wa=wa, jsonld=jsonld,
                       abs_url=abs_url, year=date.today().year, site_url=SITE_URL, org_schema=org_schema, crumbs_schema=crumbs_schema, faq_entities=faq_entities, service_items=service_items,
                       pages=PAGE_BY_OUT)

    for page in PAGES:
        out = page["out"]
        target = OUT / out if out.endswith(".html") else OUT / out / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        crumbs = breadcrumbs(page)
        html = env.get_template(page["tpl"]).render(
            page=page, title=page["title"], description=page["description"],
            path="/" + (out if not out.endswith(".html") else ""),
            canonical=None if page.get("noindex") else abs_url(out),
            og_image=abs_url("assets/img/" + page.get("og", "og-geneos.webp")),
            crumbs=crumbs,
        )
        target.write_text(html)
        print("✓", target.relative_to(ROOT), f"({len(page['title'])} / {len(page['description'])} car.)")

    # Redirecciones
    lines = [f"{old} {url(new)} 301" for old, new in REDIRECTS.items()]
    lines.append(f"/index.php/* {url('/:splat')} 301")
    (OUT / "_redirects").write_text("\n".join(lines) + "\n")
    ht = ["ErrorDocument 404 /404.html", "RewriteEngine On"]
    for old, new in REDIRECTS.items():
        ht.append(f"RewriteRule ^{old.strip('/')}/?$ {url(new)} [R=301,L]")
    ht.append(f"RewriteRule ^index\\.php/(.*)$ {url('/')}$1 [R=301,L]")
    (OUT / ".htaccess").write_text("\n".join(ht) + "\n")

    # sitemap + robots
    urls = "\n".join(
        f"  <url><loc>{abs_url(p['out'])}</loc><lastmod>{TODAY}</lastmod><priority>{p.get('priority', '0.5')}</priority></url>"
        for p in PAGES if not p.get("noindex"))
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {CANONICAL_URL}/sitemap.xml\n")


if __name__ == "__main__":
    build()
