# geneos.coop.ar — sitio estático

Versión en HTML, CSS y JS del sitio de **GENEOS Cooperativa de Software Libre**, migrada desde WordPress + Elementor.
Sin base de datos, sin PHP, sin plugins: se sirve desde cualquier hosting estático.

## Estructura

```
templates/          Páginas (Jinja2). Header, footer y bloques reutilizables en partials/
  icons/            Íconos SVG que se insertan inline
static/assets/      CSS, JS, imágenes (.webp optimizadas) y descargas
build.py            Genera el sitio en public/
public/             ⇦ Sitio listo para publicar (generado, también versionado)
```

## Editar y publicar

```bash
pip install jinja2
python build.py          # regenera public/
cd public && python -m http.server 8000   # vista previa en http://localhost:8000
```

- Datos de contacto, redes y endpoint del formulario: diccionario `SITE` en `build.py`.
- Páginas, títulos y descripciones SEO: lista `PAGES` en `build.py`.
- Precios (GERP y GEMA): `templates/software-de-gestion.html` y `templates/gema.html`.
- Estilos: `static/assets/css/styles.css` (colores en las variables de `:root`).

Si se publica en una subcarpeta (p. ej. GitHub Pages de proyecto): `BASE_PATH=/geneos python build.py`.

## Formulario de contacto

Usa [FormSubmit](https://formsubmit.co) → reenvía los mensajes a `info@geneos.com.ar` sin backend.
La **primera vez** que alguien envíe el formulario llega un mail de activación a esa casilla: hay que confirmarlo una sola vez.
Para usar otro servicio (Formspree, un endpoint en Django, etc.) cambiar `SITE["form_action"]`.

## URLs y redirecciones

Se mantienen los slugs de WordPress sin el `/index.php/` (p. ej. `/quienes-somos/`).
`public/_redirects` (Netlify / Cloudflare Pages) y `public/.htaccess` (Apache) redirigen con 301
las URLs viejas `/index.php/...` y las páginas duplicadas. También se generan `sitemap.xml` y `robots.txt`.

## Deploy

Publicar el contenido de `public/` en el hosting elegido:
- **Netlify / Cloudflare Pages**: build command `pip install jinja2 && python build.py`, output `public`.
- **Apache / Nginx propio**: subir `public/` (en Nginx, replicar las reglas de `.htaccess`).
- **GitHub Pages**: publicar la carpeta `public/` (por ejemplo con una GitHub Action).
