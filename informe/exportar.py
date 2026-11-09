"""Genera informe_PAI3-ST5.pdf e informe_PAI3-ST5.docx a partir de informe.md.

Uso:  uv run --with markdown --with playwright --with pymupdf --with pypandoc_binary python informe/exportar.py

Estilo de la memoria del PAI-1: Carta con márgenes de 2,54 cm, Calibri 10 pt
justificada, títulos en negrita y negro, título subrayado arriba de la primera
página, tablas en Arial pequeña y pie de figura debajo de la imagen.

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
LIMITE = 15
SALTO_WORD = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'

CSS = """
@page { size: Letter; margin: 2.54cm; }
body { font-family: Calibri, Carlito, sans-serif; font-size: 10pt; line-height: 1.15; color: #000; }
h1 { font-size: 28pt; font-weight: normal; text-decoration: underline; text-align: center; margin: 0 0 .5em; }
h2 { font-size: 13pt; font-weight: bold; margin: 1.3em 0 .5em; }
h3 { font-size: 12pt; font-weight: bold; margin: 1.1em 0 .4em; }
h4 { font-size: 11pt; font-weight: bold; margin: 1em 0 .4em; }
h2, h3, h4 { page-break-after: avoid; }
p, li { text-align: justify; margin: 0 0 .8em; }
li { margin-bottom: .25em; }
code { font-family: inherit; font-weight: bold; }
a { color: #0563c1; }
table { border-collapse: collapse; width: 100%; margin: .3em 0 1em; page-break-inside: avoid;
        font-family: Arial, sans-serif; font-size: 8pt; line-height: 1.25; }
th, td { border: 1px solid #bfbfbf; padding: 3px 5px; vertical-align: top; text-align: left; }
th { font-weight: bold; }
td p, td li { text-align: left; }
img { max-width: 100%; max-height: 10.5cm; display: block; margin: .3em auto .4em; }
.cabecera p { text-align: left; margin: 0 0 .3em; font-size: 11pt; }
.indice { page-break-after: always; margin-top: 1.5em; }
.indice ul { list-style: none; padding-left: 0; }
.indice li { display: flex; text-align: left; margin: .2em 0; }
.indice li.n3 { padding-left: 1.5em; }
.indice .t { flex: 1; border-bottom: 1px dotted #888; margin-right: .4em; }
.salto { page-break-before: always; }
.fig { page-break-inside: avoid; margin-bottom: 1em; }
"""

FOOTER = ('<div style="font-family:Calibri,sans-serif;font-size:8pt;width:100%;'
          'text-align:center;color:#666;"><span class="pageNumber"></span></div>')


def partes(md_text):
    """Separa título, datos de portada y cuerpo (desde Resumen ejecutivo)."""
    titulo = re.search(r"^# (.+)$", md_text, re.M).group(1)
    portada = re.search(r"## Portada\s+(.+?)\n\s*\n", md_text, re.S).group(1).strip()
    # "Security Team 5 · Integrantes: X · Fecha: Y" -> [("Grupo", ...), ("Integrantes", X), ...]
    datos = []
    for t in (t.strip() for t in portada.split("·")):
        if t in titulo:
            continue
        clave, _, valor = t.partition(":")
        datos.append((clave.strip(), valor.strip()) if valor else ("Grupo", t))
    cuerpo = md_text[md_text.index("## Resumen ejecutivo"):]
    # Pie de figura debajo de la imagen y con dos puntos, como en la memoria del PAI-1.
    cuerpo = re.sub(r"\*\*Figura (\d+)\.\*\* (.+?)\n\n(!\[[^\]]*\]\([^)]+\))",
                    r"\3\n\n**Figura \1**: \2", cuerpo)
    return titulo, datos, cuerpo


def secciones(cuerpo):
    """Encabezados ## y ### del cuerpo, en orden, para el índice."""
    return [(len(m.group(1)), m.group(2).strip())
            for m in re.finditer(r"^(##|###) (.+)$", cuerpo, re.M)]


def html_doc(titulo, datos, cuerpo, paginas):
    cabecera = (f"<h1>{html.escape(titulo)}</h1><div class=\"cabecera\">"
                + "".join(f"<p><strong>{html.escape(k)}</strong>: {html.escape(v)}</p>"
                          for k, v in datos) + "</div>")
    items = "".join(
        f'<li class="n{n}"><span class="t">{html.escape(t)}</span>'
        f'<span>{paginas.get(t, "")}</span></li>'
        for n, t in secciones(cuerpo))
    indice = f'<div class="indice"><h2>Índice</h2><ul>{items}</ul></div>'

    cuerpo_html = markdown.markdown(cuerpo, extensions=["tables", "fenced_code"])
    # Referencias y Anexos empiezan en página nueva.
    cuerpo_html = cuerpo_html.replace("<h2>Referencias</h2>", '<h2 class="salto">Referencias</h2>')
    cuerpo_html = cuerpo_html.replace("<h2>Anexos</h2>", '<h2 class="salto">Anexos</h2>')
    # Cada figura del anexo (imagen + pie) no se parte entre páginas.
    cuerpo_html = re.sub(r'(<p><img[^>]*></p>\s*<p><strong>Figura \d+</strong>.*?</p>)',
                         r'<div class="fig">\1</div>', cuerpo_html, flags=re.S)
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f"<title>{html.escape(titulo)}</title><style>{CSS}</style></head>"
            f"<body>{cabecera}{indice}{cuerpo_html}</body></html>")


def render(doc, browser):
    HTML.write_text(doc, encoding="utf-8")
    page = browser.new_page()
    page.goto(HTML.as_uri())
    page.wait_for_load_state("networkidle")
    page.pdf(path=str(PDF), format="Letter", print_background=True,
             display_header_footer=True, header_template="<div></div>",
             footer_template=FOOTER,
             margin={"top": "2.54cm", "bottom": "2.54cm", "left": "2.54cm", "right": "2.54cm"})
    page.close()


def localizar(cuerpo):
    """Página (1-based) donde aparece cada encabezado, saltando la página del índice."""
    pdf = pymupdf.open(PDF)
    paginas, desde = {}, 1
    for _, t in secciones(cuerpo):
        for i in range(desde, len(pdf)):
            if t in " ".join(pdf[i].get_text().split()):
                paginas[t], desde = i + 1, i
                break
    total = len(pdf)
    pdf.close()
    return paginas, total


# --- DOCX ------------------------------------------------------------------

def _estilo(sid, tipo, nombre, ppr="", rpr="", extra=""):
    return (f'<w:style w:type="{tipo}" w:styleId="{sid}"><w:name w:val="{nombre}"/>{extra}'
            f"<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>"
            if tipo == "paragraph" else
            f'<w:style w:type="{tipo}" w:styleId="{sid}"><w:name w:val="{nombre}"/>{extra}'
            f"<w:rPr>{rpr}</w:rPr></w:style>")


CALIBRI = '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri" w:eastAsia="Calibri"/>'
NEGRO = '<w:color w:val="000000"/>'


def _titulo(nivel, pt, antes):
    return _estilo(f"Heading{nivel}", "paragraph", f"heading {nivel}",
                   f'<w:keepNext/><w:keepLines/><w:spacing w:before="{antes}" w:after="100"/>'
                   f'<w:outlineLvl w:val="{nivel - 1}"/>',
                   f"{CALIBRI}<w:b/>{NEGRO}<w:sz w:val=\"{pt * 2}\"/>",
                   '<w:basedOn w:val="Normal"/><w:next w:val="BodyText"/><w:qFormat/>')


ESTILOS = {
    "Title": _estilo("Title", "paragraph", "Title",
                     '<w:spacing w:after="160"/><w:jc w:val="center"/>',
                     f'{CALIBRI}{NEGRO}<w:sz w:val="56"/><w:u w:val="single"/>',
                     '<w:basedOn w:val="Normal"/><w:next w:val="BodyText"/><w:qFormat/>'),
    "Author": _estilo("Author", "paragraph", "Author", '<w:spacing w:after="60"/>',
                      '<w:sz w:val="22"/>', '<w:basedOn w:val="Normal"/>'),
    "BodyText": _estilo("BodyText", "paragraph", "Body Text",
                        '<w:spacing w:before="0" w:after="160"/><w:jc w:val="both"/>', "",
                        '<w:basedOn w:val="Normal"/><w:qFormat/>'),
    # Celdas de tabla y listas: alineadas a la izquierda, sin el justificado del cuerpo.
    "Compact": _estilo("Compact", "paragraph", "Compact",
                       '<w:spacing w:before="20" w:after="20"/><w:jc w:val="left"/>', "",
                       '<w:basedOn w:val="BodyText"/><w:qFormat/>'),
    "Heading1": _titulo(1, 13, 280),
    "Heading2": _titulo(2, 12, 220),
    "Heading3": _titulo(3, 11, 200),
    "TOCHeading": _estilo("TOCHeading", "paragraph", "TOC Heading",
                          '<w:spacing w:before="240" w:after="100"/><w:outlineLvl w:val="9"/>',
                          f'{CALIBRI}<w:b/>{NEGRO}<w:sz w:val="26"/>',
                          '<w:basedOn w:val="Normal"/><w:next w:val="BodyText"/>'),
    "VerbatimChar": _estilo("VerbatimChar", "character", "Verbatim Char", rpr="<w:b/>"),
    "Hyperlink": _estilo("Hyperlink", "character", "Hyperlink",
                         rpr='<w:color w:val="0563C1"/><w:u w:val="single"/>'),
    "Table": ('<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/>'
              '<w:basedOn w:val="TableNormal"/><w:pPr><w:spacing w:before="0" w:after="0"/>'
              '<w:jc w:val="left"/></w:pPr>'
              '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="16"/></w:rPr>'
              '<w:tblPr><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
              '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
              '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/></w:rPr></w:tblStylePr></w:style>'),
}


def _retocar_docx():
    with zipfile.ZipFile(DOCX) as z:
        ficheros = {n: z.read(n) for n in z.namelist()}

    estilos = ficheros["word/styles.xml"].decode("utf-8")
    estilos = re.sub(r"<w:rPrDefault>.*?</w:rPrDefault>",
                     f'<w:rPrDefault><w:rPr>{CALIBRI}<w:sz w:val="20"/><w:szCs w:val="20"/>'
                     '<w:lang w:val="es-ES"/></w:rPr></w:rPrDefault>', estilos, flags=re.S)
    estilos = re.sub(r"<w:pPrDefault>.*?</w:pPrDefault>",
                     '<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="264" w:lineRule="auto"/>'
                     "</w:pPr></w:pPrDefault>", estilos, flags=re.S)
    for sid, nuevo in ESTILOS.items():
        patron = rf'<w:style\b[^>]*w:styleId="{sid}"[^>]*>.*?</w:style>'
        if re.search(patron, estilos, flags=re.S):
            estilos = re.sub(patron, lambda _: nuevo, estilos, count=1, flags=re.S)
        else:
            estilos = estilos.replace("</w:styles>", nuevo + "</w:styles>")
    ficheros["word/styles.xml"] = estilos.encode("utf-8")

    xml = ficheros["word/document.xml"].decode("utf-8")
    # Bordes grises finos en las tablas (van antes de tblLayout por el orden del esquema).
    bordes = "<w:tblBorders>" + "".join(
        f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
        for b in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"
    xml = re.sub(r"(<w:tblLayout )", bordes + r"\1", xml)
    # Carta con márgenes de 2,54 cm, como la memoria del PAI-1.
    xml = re.sub(r"<w:pgSz[^>]*/>|<w:pgMar[^>]*/>", "", xml)
    xml = xml.replace("</w:sectPr>", '<w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" '
                      'w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" '
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


def docx(titulo, datos, cuerpo):
    # Rutas de imagen sin %23: pandoc busca el fichero tal cual.
    cuerpo = re.sub(r"\]\((\.\./[^)]+)\)", lambda m: f"]({unquote(m.group(1))})", cuerpo)
    for h in ("## Resumen ejecutivo", "## Referencias", "## Anexos"):
        cuerpo = cuerpo.replace(h, SALTO_WORD + h, 1)
    # Cabecera YAML: pandoc interpreta el Markdown de los autores (negrita en la etiqueta).
    comillas = lambda s: '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    yaml = ("---\n" f"title: {comillas(titulo)}\n" "author:\n"
            + "".join(f"  - {comillas(f'**{k}**: {v}')}\n" for k, v in datos)
            + "toc-title: Índice\nlang: es-ES\n---\n\n")
    pypandoc.convert_text(
        yaml + cuerpo, "docx", format="markdown-implicit_figures", outputfile=str(DOCX),
        # El cuerpo empieza en "##": se sube un nivel para que sea "Heading 1" en Word.
        extra_args=["--toc", "--toc-depth=2", "--shift-heading-level-by=-1",
                    f"--resource-path={DIR}"])
    _retocar_docx()


def main():
    titulo, datos, cuerpo = partes(MD.read_text(encoding="utf-8"))
    docx(titulo, datos, cuerpo)
    print(f"{DOCX.name}: generado")
    with sync_playwright() as p:
        # Usa el chromium-headless-shell ya instalado, sea cual sea su build.
        shells = sorted(Path.home().glob("AppData/Local/ms-playwright/chromium_headless_shell-*/"
                                         "chrome-headless-shell-win64/chrome-headless-shell.exe"))
        browser = p.chromium.launch(executable_path=str(shells[-1]) if shells else None)
        render(html_doc(titulo, datos, cuerpo, {}), browser)
        paginas, _ = localizar(cuerpo)
        render(html_doc(titulo, datos, cuerpo, paginas), browser)
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
