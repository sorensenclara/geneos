#!/usr/bin/env python3
"""Genera el sitio estático de GENEOS en ./public a partir de ./templates y ./static.

Uso:
    pip install jinja2
    python build.py                 # sitio servido desde la raíz del dominio
    BASE_PATH=/geneos python build.py   # p. ej. GitHub Pages de proyecto

Después: servir ./public con cualquier hosting estático.
"""
import os
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "public"
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://geneos.coop.ar").rstrip("/")

SITE = {
    "name": "GENEOS",
    "whatsapp": "5492494521418",
    "whatsapp_label": "+549 2494 521418",
    "email": "info@geneos.com.ar",
    "address": "Alem 1015 - Tandil",
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

# (plantilla, ruta de salida, título, descripción)
PAGES = [
    ("index.html", "", "GENEOS | Soluciones Informáticas",
     "Somos una cooperativa que desarrolla y acompaña a cada cliente en el diseño, desarrollo e implementación de soluciones informáticas."),
    ("servicios.html", "servicios/", "Servicios | GENEOS",
     "Soluciones informáticas basadas en software libre: software de gestión, staff augmentation, sitios web y apps, e-learning y diseño."),
    ("software-de-gestion.html", "software-de-gestion-completo/", "Software de Gestión GERP | GENEOS",
     "GERP: el sistema de gestión online, ágil e integral basado en Odoo Community, configurado y listo para usar."),
    ("gema.html", "software-gestion-matafuegos-extintores/", "Software de Gestión Integral de Matafuegos o Extintores | GEMA",
     "Software de Gestión Integral de Matafuegos o Extintores permite llevar el control online e integral de los servicios brindados a sus clientes."),
    ("staff-augmentation.html", "staff-augmentation/", "Staff Augmentation | GENEOS",
     "Potenciá a tu equipo con desarrolladores, DevOps, analistas funcionales, gestores de proyecto y diseñadores UX/UI de GENEOS."),
    ("apps-y-webs.html", "desarrollo-apps-sitios-web-cooperativos/", "Desarrollo de Apps y Sitios Web Cooperativos | GENEOS",
     "En Geneos nos especializamos en desarrollo de apps y sitios web acorde a las necesidades del cliente, con WordPress, Odoo, Django, etc."),
    ("e-learning.html", "plataformas-e-learning-lms-moodle/", "Plataformas E-learning - LMS - Moodle | GENEOS",
     "Creamos plataformas de aprendizaje o sistema de gestión de aprendizaje (LMS) diseñado para ayudar a los educadores."),
    ("diseno.html", "diseno-sitios-web-identidades/", "Diseño de Sitios Web e Identidades | GENEOS",
     "Diseño de sitios web e identidades visuales combinando funcionalidad y comunicación para potenciar tu proyecto digital."),
    ("quienes-somos.html", "quienes-somos/", "Desarrolladores de Soluciones Tecnológicas | GENEOS",
     "Conocé el equipo de Geneos, cooperativa de desarrolladores de soluciones tecnológicas, software de gestión, sitios webs o proyectos a medida."),
    ("recursos-graficos.html", "recursos-graficos/", "Recursos Gráficos | GENEOS",
     "Isologotipos, manual de marca y recursos gráficos de GENEOS y GERP para descargar."),
    ("contacto.html", "contacto-geneos/", "Contacto | GENEOS",
     "Contacto para descubrir soluciones digitales con tecnologías libres: Odoo, WordPress, Moodle y más. ¡Escribinos!"),
    ("404.html", "404.html", "Página no encontrada | GENEOS", "La página que buscás no existe."),
]

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


_icon_cache = {}


def icon(name, cls="icon"):
    if name not in _icon_cache:
        _icon_cache[name] = (ROOT / "templates" / "icons" / f"{name}.svg").read_text()
    svg = _icon_cache[name].replace("<svg ", f'<svg class="{cls}" ', 1)
    return Markup(svg)


def wa(text=""):
    from urllib.parse import quote
    return f"https://wa.me/{SITE['whatsapp']}" + (f"?text={quote(text)}" if text else "")


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.globals.update(site=SITE, url=url, asset=asset, img=img, icon=icon, wa=wa,
                       year=date.today().year, site_url=SITE_URL)

    for tpl, out, title, desc in PAGES:
        target = OUT / out if out.endswith(".html") else OUT / out / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        html = env.get_template(tpl).render(title=title, description=desc,
                                             path="/" + (out if not out.endswith(".html") else ""),
                                             canonical=f"{SITE_URL}/{out}" if not out.endswith(".html") else None)
        target.write_text(html)
        print("✓", target.relative_to(ROOT))

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
    urls = "\n".join(f"  <url><loc>{SITE_URL}/{out}</loc></url>" for _, out, *_ in PAGES if not out.endswith(".html"))
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


if __name__ == "__main__":
    build()
