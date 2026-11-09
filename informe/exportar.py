"""Genera informe_PAI3-ST5.pdf e informe_PAI3-ST5.docx a partir de informe.md.

Uso:  uv run --with markdown --with playwright --with pymupdf --with pypandoc_binary python informe/exportar.py

PDF: dos pasadas; la primera calcula en qué página cae cada sección y la
segunda escribe el índice con esos números. Al final dice cuántas páginas
cuentan para el límite de 15 (todo lo anterior a "Referencias").
DOCX: con pandoc; el índice es un campo de Word que se actualiza al abrirlo.
"""
import html
import re
import sys
import zipfile
from pathlib import Path

from urllib.parse import unquote

import markdown
import pymupdf
import pypandoc
from playwright.sync_api import sync_playwright

DIR = Path(__file__).resolve().parent
MD = DIR / "informe.md"
HTML = DIR / "_informe.html"
PDF = DIR / "informe_PAI3-ST5.pdf"
DOCX = DIR / "informe_PAI3-ST5.docx"
SALTO_WORD = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'
LIMITE = 15

CSS = """
@page { size: A4; margin: 2cm 2cm 2.2cm 2cm; }
body { font-family: "Calibri", "Carlito", Arial, sans-serif; font-size: 11pt; line-height: 1.35; color: #111; }
h1, h2, h3, h4 { color: #7a0026; margin: 1em 0 .4em; line-height: 1.2; }
h2 { font-size: 16pt; border-bottom: 1px solid #7a0026; padding-bottom: 2px; }
h3 { font-size: 13pt; }
h4 { font-size: 11.5pt; }
p, li { text-align: justify; margin: .35em 0; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f2f2f2; padding: 0 2px; }
table { border-collapse: collapse; width: 100%; margin: .5em 0; font-size: 9pt; page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #eee; }
td code { font-size: 8.5pt; }
img { max-width: 100%; max-height: 11cm; display: block; margin: .3em auto 1em; border: 1px solid #ccc; }
.portada { height: 25cm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always; }
.portada h1 { font-size: 24pt; border: 0; }
.portada p { text-align: center; font-size: 13pt; margin: .3em 0; }
.indice { page-break-after: always; }
.indice ul { list-style: none; padding-left: 0; }
.indice li { display: flex; text-align: left; margin: .25em 0; }
.indice li.n3 { padding-left: 1.5em; font-size: 10.5pt; }
.indice .t { flex: 1; border-bottom: 1px dotted #888; margin-right: .4em; }
.salto { page-break-before: always; }
.fig { page-break-inside: avoid; }
"""

FOOTER = ('<div style="font-size:8pt;width:100%;text-align:center;color:#666;">'
          '<span class="pageNumber"></span></div>')


def partes(md_text):
    """Separa título, línea de portada y cuerpo (desde Resumen ejecutivo)."""
    titulo = re.search(r"^# (.+)$", md_text, re.M).group(1)
    portada = re.search(r"## Portada\s+(.+?)\n\s*\n", md_text, re.S).group(1).strip()
    cuerpo = md_text[md_text.index("## Resumen ejecutivo"):]
    return titulo, portada, cuerpo


def secciones(cuerpo):
    """Encabezados ## y ### del cuerpo, en orden, para el índice."""
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r"^(##|###) (.+)$", cuerpo, re.M)]


def html_doc(titulo, portada, cuerpo, paginas):
    # Los trozos de la línea de portada que ya están en el título no se repiten.
    trozos = [t.strip() for t in portada.split("·") if t.strip() not in titulo]
    portada_html = (f'<div class="portada"><h1>{html.escape(titulo)}</h1>'
                    + "".join(f"<p>{html.escape(t)}</p>" for t in trozos) + "</div>")
    items = "".join(
        f'<li class="n{n}"><span class="t">{html.escape(t)}</span>'
        f'<span>{paginas.get(t, "")}</span></li>'
        for n, t in secciones(cuerpo))
    indice = f'<div class="indice"><h2>Índice</h2><ul>{items}</ul></div>'

    cuerpo_html = markdown.markdown(cuerpo, extensions=["tables", "fenced_code"])
    # Referencias y Anexos empiezan en página nueva.
    cuerpo_html = cuerpo_html.replace("<h2>Referencias</h2>", '<h2 class="salto">Referencias</h2>')
    cuerpo_html = cuerpo_html.replace("<h2>Anexos</h2>", '<h2 class="salto">Anexos</h2>')
    # Cada figura del anexo (título + imagen) no se parte entre páginas.
    cuerpo_html = re.sub(r'(<p><strong>Figura \d+\.</strong>.*?</p>\s*<p><img[^>]*></p>)',
                         r'<div class="fig">\1</div>', cuerpo_html, flags=re.S)
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f"<title>{html.escape(titulo)}</title><style>{CSS}</style></head>"
            f"<body>{portada_html}{indice}{cuerpo_html}</body></html>")


def render(doc, browser):
    HTML.write_text(doc, encoding="utf-8")
    page = browser.new_page()
    page.goto(HTML.as_uri())
    page.wait_for_load_state("networkidle")
    page.pdf(path=str(PDF), format="A4", print_background=True,
             display_header_footer=True, header_template="<div></div>",
             footer_template=FOOTER,
             margin={"top": "2cm", "bottom": "2.2cm", "left": "2cm", "right": "2cm"})
    page.close()


def localizar(cuerpo):
    """Página (1-based) donde aparece cada encabezado, saltando portada e índice."""
    pdf = pymupdf.open(PDF)
    paginas, desde = {}, 2
    for _, t in secciones(cuerpo):
        for i in range(desde, len(pdf)):
            if t in " ".join(pdf[i].get_text().split()):
                paginas[t], desde = i + 1, i
                break
    total = len(pdf)
    pdf.close()
    return paginas, total


def docx(titulo, portada, cuerpo):
    trozos = [t.strip() for t in portada.split("·") if t.strip() not in titulo]
    # Rutas de imagen sin %23: pandoc busca el fichero tal cual.
    cuerpo = re.sub(r"\]\((\.\./[^)]+)\)", lambda m: f"]({unquote(m.group(1))})", cuerpo)
    for h in ("## Resumen ejecutivo", "## Referencias", "## Anexos"):
        cuerpo = cuerpo.replace(h, SALTO_WORD + h, 1)
    pypandoc.convert_text(
        cuerpo, "docx", format="markdown-implicit_figures", outputfile=str(DOCX),
        extra_args=["--toc", "--toc-depth=2", f"--resource-path={DIR}",
                    "-M", f"title={titulo}", "-M", f"subtitle={' · '.join(trozos)}",
                    "-M", "toc-title=Índice", "-M", "lang=es-ES"])
    # pandoc usa tamaño Carta: se pasa a A4 con márgenes de 2 cm.
    with zipfile.ZipFile(DOCX) as z:
        ficheros = {n: z.read(n) for n in z.namelist()}
    xml = ficheros["word/document.xml"].decode("utf-8")
    # Bordes finos en las tablas (van antes de tblLayout por el orden del esquema).
    borde = '{}w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
    bordes = "<w:tblBorders>" + "".join(
        borde.format(f"<w:{b} ") for b in ("top", "left", "bottom", "right", "insideH", "insideV")
    ) + "</w:tblBorders>"
    xml = re.sub(r"(<w:tblLayout )", bordes + r"\1", xml)
    xml = re.sub(r"<w:pgSz[^>]*/>|<w:pgMar[^>]*/>", "", xml)
    xml = xml.replace("</w:sectPr>", '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" '
                      'w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" '
                      'w:gutter="0"/></w:sectPr>')
    ficheros["word/document.xml"] = xml.encode("utf-8")
    tipos = ficheros["[Content_Types].xml"].decode("utf-8")
    if 'Extension="png"' not in tipos:
        tipos = tipos.replace('<Default Extension="xml"',
                              '<Default Extension="png" ContentType="image/png" /><Default Extension="xml"', 1)
    ficheros["[Content_Types].xml"] = tipos.encode("utf-8")
    with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as z:
        for n, datos in ficheros.items():
            z.writestr(n, datos)


def main():
    titulo, portada, cuerpo = partes(MD.read_text(encoding="utf-8"))
    docx(titulo, portada, cuerpo)
    print(f"{DOCX.name}: generado")
    with sync_playwright() as p:
        # Usa el chromium-headless-shell ya instalado, sea cual sea su build.
        shells = sorted(Path.home().glob("AppData/Local/ms-playwright/chromium_headless_shell-*/"
                                         "chrome-headless-shell-win64/chrome-headless-shell.exe"))
        browser = p.chromium.launch(executable_path=str(shells[-1]) if shells else None)
        render(html_doc(titulo, portada, cuerpo, {}), browser)
        paginas, _ = localizar(cuerpo)
        render(html_doc(titulo, portada, cuerpo, paginas), browser)
        paginas, total = localizar(cuerpo)
        browser.close()
    HTML.unlink()
    cuentan = paginas["Referencias"] - 1
    print(f"{PDF.name}: {total} páginas; cuentan para el límite {cuentan}/{LIMITE}")
    for t, n in paginas.items():
        print(f"  p.{n:>2}  {t}")
    sys.exit(0 if cuentan <= LIMITE else 1)


if __name__ == "__main__":
    main()
