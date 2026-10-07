#!/usr/bin/env python3
# Uso: python tools/geagro_import.py "<carpeta GEAGRO WEB 2026>" .
"""Importa la landing de GEAGRO (index.html + CSS) dentro del sitio de GENEOS,
aislando estilos: todas las clases pasan a tener prefijo ga- y todas las reglas
quedan bajo .geagro-scope."""
import re, sys, os, shutil
SRC = sys.argv[1]          # carpeta con index.html y assets/
DST = sys.argv[2]          # repo geneos
OUT_ASSETS = os.path.join(DST, 'static/assets/geagro-landing')

def ren_classes(sel):
    return re.sub(r'\.(-?[A-Za-z_][\w-]*)', r'.ga-\1', sel)

def scope_selector(s):
    s = s.strip()
    if not s:
        return s
    s = ren_classes(s)
    m = re.match(r'^(:root|html|body)\b(.*)$', s)
    if m:
        return '.geagro-scope' + m.group(2)
    return '.geagro-scope ' + s

def process(css):
    out, i, n = [], 0, len(css)
    while i < n:
        # comentarios
        if css.startswith('/*', i):
            j = css.find('*/', i) + 2
            out.append(css[i:j]); i = j; continue
        if css[i].isspace():
            out.append(css[i]); i += 1; continue
        # bloque: buscar '{' o ';'
        j = i
        while j < n and css[j] not in '{;}':
            if css.startswith('/*', j):
                j = css.find('*/', j) + 2
            else:
                j += 1
        if j >= n:
            out.append(css[i:]); break
        head = css[i:j]
        if css[j] == ';':          # @import / @charset
            out.append(css[i:j+1]); i = j + 1; continue
        if css[j] == '}':
            out.append(css[i:j+1]); i = j + 1; continue
        # encontrar el cierre del bloque
        depth, k = 0, j
        while k < n:
            if css[k] == '{': depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        body = css[j+1:k]
        h = head.strip()
        if h.startswith('@font-face'):
            pass  # usamos Titillium de Google Fonts del sitio
        elif h.startswith('@media') or h.startswith('@supports') or h.startswith('@container'):
            out.append(head + '{' + process(body) + '}')
        elif h.startswith('@'):
            out.append(head + '{' + body + '}')   # @keyframes, etc.
        else:
            sels = ', '.join(scope_selector(s) for s in h.split(','))
            out.append(sels + ' {' + body + '}')
        i = k + 1
    return ''.join(out)

css = open(os.path.join(SRC, 'assets/css/geagro-landing.css')).read()
scoped = process(css)
# :root con variables -> también tienen que verse dentro del scope (ya mapeado)
os.makedirs(os.path.join(OUT_ASSETS, 'css'), exist_ok=True)
open(os.path.join(OUT_ASSETS, 'css/geagro.css'), 'w').write(
    '/* Estilos de la landing de GEAGRO (geagro.ar), aislados bajo .geagro-scope y con clases ga-*.\n'
    '   Generado por tools/geagro_import.py: no editar a mano, re-importar. */\n' + scoped)

for sub in ('icons', 'images'):
    d = os.path.join(OUT_ASSETS, sub)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(SRC, 'assets', sub), d,
                    ignore=shutil.ignore_patterns('.DS_Store', 'favicon', 'og-*.jpg'))

html = open(os.path.join(SRC, 'index.html')).read()
main = re.search(r'<main[^>]*>(.*)</main>', html, re.S).group(1)

def ren_attr(m):
    return 'class="' + ' '.join('ga-' + c for c in m.group(1).split()) + '"'
main = re.sub(r'class="([^"]*)"', ren_attr, main)
main = main.replace('assets/docs/', 'https://geagro.ar/assets/docs/')
main = re.sub(r'(["\s(])assets/', r'\1/assets/geagro-landing/', main)
main = re.sub(r'href="(cereales|vid)/"', r'href="https://geagro.ar/\1/" target="_blank" rel="noopener"', main)
main = re.sub(r'href="\./"', 'href="https://geagro.ar/" target="_blank" rel="noopener"', main)
# Dentro del sitio de GENEOS el hero muestra el logo de GEAGRO (en geagro.ar dice "by GENEOS")
main = re.sub(r'<p class="[^"]*ga-hero-by[^"]*">.*?</p>',
              '<img class="ga-hero-logo" src="{{ img(\'geagro/logo-geagro-white.svg\') }}" alt="GEAGRO, software de gestión agropecuaria" width="300" height="64">',
              main, count=1, flags=re.S)
# rutas absolutas -> helper de BASE_PATH
main = re.sub(r'"/assets/geagro-landing/([^"]+)"', lambda m: '"{{ asset(\'geagro-landing/' + m.group(1) + '\') }}"', main)
open(os.path.join(DST, 'templates/partials/geagro-landing.html'), 'w').write(
    '{# Contenido de la portada de geagro.ar, importado con tools/geagro_import.py #}\n' + main.strip() + '\n')
print('ok', len(scoped), len(main))
