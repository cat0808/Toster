#!/usr/bin/env python3
"""
ЭТОТ ФАЙЛ СДЕЛАН ПРИ ПОМОЩИИ ИИ








md2pdf.py — превращает текст от Gemini (Markdown) в аккуратный PDF.

Установка:
    pip install markdown reportlab

Использование:
    python md2pdf.py ответ.md                  -> ответ.pdf
    python md2pdf.py ответ.md -o работа.pdf
    python md2pdf.py ответ.md --strip-intro    (убрать вступление Gemini до первой "---")
    python md2pdf.py --paste                   (вставить текст в консоль, закончить Ctrl+D / Ctrl+Z+Enter)

Поддерживается: заголовки #, ##, ###, жирный/курсив, списки, таблицы, ---,
\\newpage (разрыв страницы), линии из подчёркиваний ______ (поля для ответа).
"""
import argparse
import html
import os
import re
import sys
from html.parser import HTMLParser

import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, ListFlowable, ListItem, PageBreak,
                                PageBreakIfNotEmpty,
                                Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

# ---------------------------------------------------------------- шрифты ----
FONT_CANDIDATES = [
    # (обычный, жирный, курсив, жирный курсив)
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf",
     "C:/Windows/Fonts/ariali.ttf", "C:/Windows/Fonts/arialbi.ttf"),
    ("C:/Windows/Fonts/calibri.ttf", "C:/Windows/Fonts/calibrib.ttf",
     "C:/Windows/Fonts/calibrii.ttf", "C:/Windows/Fonts/calibriz.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
     "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"),
    ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
     "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf"),
]


def _extra_font_sets():
    here = os.path.dirname(os.path.abspath(__file__))
    names = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
             "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf")
    dirs = [here, os.path.join(here, "fonts")]
    try:                      # шрифты DejaVu есть внутри matplotlib
        import matplotlib
        dirs.append(os.path.join(matplotlib.get_data_path(), "fonts", "ttf"))
    except Exception:
        pass
    return [tuple(os.path.join(d, n) for n in names) for d in dirs]


def register_fonts():
    if "Body" in pdfmetrics.getRegisteredFontNames():
        return
    for regular, bold, italic, bolditalic in FONT_CANDIDATES + _extra_font_sets():
        if all(os.path.exists(p) for p in (regular, bold, italic, bolditalic)):
            pdfmetrics.registerFont(TTFont("Body", regular))
            pdfmetrics.registerFont(TTFont("Body-Bold", bold))
            pdfmetrics.registerFont(TTFont("Body-Italic", italic))
            pdfmetrics.registerFont(TTFont("Body-BoldItalic", bolditalic))
            pdfmetrics.registerFontFamily(
                "Body", normal="Body", bold="Body-Bold",
                italic="Body-Italic", boldItalic="Body-BoldItalic")
            return
    sys.exit("Не найден шрифт с кириллицей. Положите DejaVuSans*.ttf рядом со "
             "скриптом или поправьте FONT_CANDIDATES.")


# ---------------------------------------------------------------- стили -----
def make_styles():
    base = ParagraphStyle("base", fontName="Body", fontSize=10, leading=13.2,
                          spaceAfter=2)
    return {
        "p": base,
        "h1": ParagraphStyle("h1", parent=base, fontName="Body-Bold",
                             fontSize=17, leading=21, alignment=TA_CENTER,
                             spaceBefore=4, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=base, fontName="Body-Bold",
                             fontSize=14, leading=18, spaceBefore=8,
                             spaceAfter=5, textColor=colors.HexColor("#1F3A5F")),
        "h3": ParagraphStyle("h3", parent=base, fontName="Body-Bold",
                             fontSize=11.5, leading=15, spaceBefore=6,
                             spaceAfter=3),
        "cell": ParagraphStyle("cell", parent=base, fontSize=9.5, leading=12.5,
                               spaceAfter=0),
        "cellh": ParagraphStyle("cellh", parent=base, fontName="Body-Bold",
                                fontSize=9.5, leading=12.5, spaceAfter=0),
    }


# ------------------------------------------- подготовка текста от Gemini ----
def _strip_code_fence(text):
    """Gemini иногда оборачивает весь ответ в ```markdown ... ```."""
    m = re.match(r"^\s*```[a-zA-Z]*\n(.*?)\n```\s*$", text, flags=re.S)
    return m.group(1) if m else text


def _strip_intro(text):
    """Убирает вводную фразу Gemini ("Вот готовый макет...") перед первой '---'.
    Вырезается только короткий кусок без заголовков — основной текст не страдает."""
    m = re.search(r"\n[ \t]*-{3,}[ \t]*\n", text)
    if not m:
        return text
    head = text[:m.start()]
    if (head.strip() and len(head) < 800
            and not re.search(r"^\s*#", head, flags=re.M)
            and not re.search(r"^\s*\|", head, flags=re.M)):
        return text[m.end():]
    return text


def preprocess(text, strip_intro="auto"):
    text = text.replace("\r\n", "\n")
    text = _strip_code_fence(text)
    # разрыв страницы в любом виде: \newpage, \\newpage, \pagebreak, \clearpage, <div style="page-break...">
    text = re.sub(r"\\+(?:newpage|pagebreak|clearpage)|<div[^>]*page-break[^>]*>\s*</div>",
                  "\n\n[[PAGEBREAK]]\n\n", text, flags=re.I)
    text = text.replace("\\_", "_")

    if strip_intro:          # True или "auto"
        text = _strip_intro(text)

    # строки-«поля для ответа» из подчёркиваний.
    # Длинная строка (>=40) = новая линия; короткие обрывки после неё — остаток переноса.
    out, in_line = [], False
    for ln in text.split("\n"):
        if re.fullmatch(r"\s*_+\s*", ln):
            n = len(ln.strip())
            if n >= 40 or (n >= 5 and not in_line):
                out.append("[[LINE]]")
                in_line = True
                continue
            if in_line:
                continue
        in_line = False
        out.append(ln)
    text = "\n".join(out)

    # Gemini часто пишет "текст:  \n" с пробелами-переносами — оставим как есть,
    # а перед таблицей и списком гарантируем пустую строку
    text = re.sub(r"([^\n|])\n(\|)", r"\1\n\n\2", text)
    text = re.sub(r"([^\n\-*\d])\n([-*] |\d+\. )", r"\1\n\n\2", text)

    # после таблицы обязательна пустая строка, иначе следующий абзац станет строкой таблицы
    text = re.sub(r"(^\|.*\|[ \t]*)\n(?!\||[ \t]*\n)", r"\1\n\n", text, flags=re.M)

    # строки-поля внутри текста (_____) не должны превращаться в курсив/линию
    text = re.sub(r"_{2,}", lambda m: "&#95;" * len(m.group(0)), text)

    # '---' должна быть отделена пустыми строками, иначе это заголовок
    text = re.sub(r"^[ \t]*-{3,}[ \t]*$", "\n---\n", text, flags=re.M)

    # маркеры, чтобы их не съел markdown
    text = text.replace("[[PAGEBREAK]]", "<div class='pagebreak'></div>")
    text = text.replace("[[LINE]]", "<div class='answerline'></div>")
    return text


# --------------------------------------------- HTML -> flowables reportlab ----
class Builder(HTMLParser):
    def __init__(self, styles, width):
        super().__init__(convert_charrefs=True)
        self.s = styles
        self.width = width
        self.flow = []
        self.stack = []          # контейнеры: список flowables
        self.buf = None          # накопитель inline-текста
        self.block = None        # текущий блок-тег (p/h1/li/td...)
        self.lists = []          # стек списков: ["ul"|"ol", [items]]
        self.table = None
        self.cell_header = False
        self.skip_p = 0

    # --- helpers
    def _target(self):
        return self.stack[-1] if self.stack else self.flow

    def _start_block(self, tag):
        self.block, self.buf = tag, []

    def _end_block(self):
        text = "".join(self.buf or []).strip()
        tag = self.block
        self.block, self.buf = None, None
        if not text and tag != "td":
            return None
        return text

    # --- parser callbacks
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "p" and self.block in ("li", "td"):
            if "".join(self.buf or []).strip():
                self.buf.append("<br/>")
            self.skip_p += 1
        elif tag in ("p", "h1", "h2", "h3", "h4"):
            self._start_block(tag)
        elif tag in ("strong", "b", "em", "i", "u"):
            if self.buf is not None:
                self.buf.append(f"<{'b' if tag == 'strong' else 'i' if tag == 'em' else tag}>")
        elif tag == "code":
            if self.buf is not None:
                self.buf.append("<font face='Courier'>")
        elif tag == "br":
            if self.buf is not None:
                self.buf.append("<br/>")
        elif tag in ("ul", "ol"):
            self.lists.append([tag, []])
        elif tag == "li":
            self._start_block("li")
        elif tag == "hr":
            self._target().append(HRFlowable(width="100%", thickness=0.7,
                                             color=colors.grey,
                                             spaceBefore=4, spaceAfter=6))
        elif tag == "div":
            cls = a.get("class", "")
            if cls == "pagebreak":
                self._target().append(PageBreakIfNotEmpty())
            elif cls == "answerline":
                self._target().append(Spacer(1, 7 * mm))
                self._target().append(HRFlowable(width="100%", thickness=0.5,
                                                 color=colors.black))
        elif tag == "table":
            self.table = {"rows": [], "head_rows": 0}
        elif tag == "tr":
            self.table["cur"] = []
        elif tag in ("th", "td"):
            self.cell_header = tag == "th"
            self._start_block("td")
            self.table["align"] = a.get("style", "")

    def handle_endtag(self, tag):
        if tag == "p" and self.skip_p:
            self.skip_p -= 1
        elif tag in ("p", "h1", "h2", "h3", "h4"):
            text = self._end_block()
            if text:
                style = self.s.get(tag, self.s["h3"] if tag == "h4" else self.s["p"])
                self._target().append(Paragraph(text, style))
        elif tag in ("strong", "b", "em", "i", "u"):
            if self.buf is not None:
                self.buf.append(f"</{'b' if tag == 'strong' else 'i' if tag == 'em' else tag}>")
        elif tag == "code":
            if self.buf is not None:
                self.buf.append("</font>")
        elif tag == "li":
            text = self._end_block() or ""
            self.lists[-1][1].append(Paragraph(text, self.s["p"]))
        elif tag in ("ul", "ol"):
            kind, items = self.lists.pop()
            lf = ListFlowable(
                [ListItem(i, leftIndent=14) for i in items],
                bulletType="bullet" if kind == "ul" else "1",
                bulletFontName="Body", start="•" if kind == "ul" else None,
                leftIndent=14, bulletFontSize=9)
            self._target().append(lf)
        elif tag in ("th", "td"):
            text = self._end_block() or ""
            style = self.s["cellh"] if self.cell_header else self.s["cell"]
            para_style = ParagraphStyle("c", parent=style)
            if "center" in self.table.get("align", ""):
                para_style.alignment = TA_CENTER
            self.table["cur"].append(Paragraph(text, para_style))
            if self.cell_header:
                self.table["head_rows"] = 1
        elif tag == "tr":
            self.table["rows"].append(self.table.pop("cur"))
        elif tag == "table":
            self._flush_table()

    def handle_data(self, data):
        if self.buf is not None:
            self.buf.append(html.escape(data, quote=False))

    # --- tables
    def _flush_table(self):
        rows = self.table["rows"]
        self.table = None
        if not rows:
            return
        ncols = max(len(r) for r in rows)
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        col_w = (self.width / ncols)
        # при 2 колонках "Понятие | Определение" даём правой больше места
        widths = [col_w] * ncols
        if ncols == 2:
            widths = [self.width * 0.32, self.width * 0.68]
        heights = []
        for r in rows:
            empty = all(isinstance(c, str) or not c.getPlainText().strip() for c in r)
            heights.append(10 * mm if empty else None)
        t = Table(rows, colWidths=widths, rowHeights=heights, repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8A8A8A")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF6")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        self._target().append(Spacer(1, 2))
        self._target().append(t)
        self._target().append(Spacer(1, 6))


# ------------------------------------------------------------- основной код --
def convert(text, out_path=None, strip_intro="auto", title=None):
    """Markdown-текст -> PDF.

    out_path: путь к PDF-файлу; если None — PDF возвращается как bytes.
    Возвращает путь к файлу (или bytes, если out_path=None).
    """
    import io
    register_fonts()
    styles = make_styles()
    md = markdown.Markdown(extensions=["tables", "sane_lists", "nl2br"])
    html_text = md.convert(preprocess(text, strip_intro))

    buffer = io.BytesIO() if out_path is None else None
    if title is None:
        title = (detect_title(text)
                 or (os.path.splitext(os.path.basename(out_path))[0]
                     if out_path else "Документ"))

    doc = SimpleDocTemplate(buffer if buffer is not None else out_path,
                            pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            title=title)
    builder = Builder(styles, A4[0] - 36 * mm)
    builder.feed(html_text)
    builder.close()

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont("Body", 8.5)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f"— {d.page} —")
        canvas.restoreState()

    # лишние разрывы подряд / в начале документа не должны давать пустые страницы
    flow, prev_break = [], True
    for f in builder.flow:
        is_break = isinstance(f, (PageBreak, PageBreakIfNotEmpty))
        if is_break and prev_break:
            continue
        flow.append(f)
        prev_break = is_break
    while flow and isinstance(flow[-1], (PageBreak, PageBreakIfNotEmpty)):
        flow.pop()

    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue() if buffer is not None else out_path


def detect_title(text):
    """Название по первому заголовку '# ...' в тексте (или None)."""
    m = re.search(r"^\s*#\s+(.+?)\s*$", text, flags=re.M)
    return re.sub(r"[*_`]", "", m.group(1)).strip() if m else None


def safe_filename(title, default="document"):
    """'Контрольная: Римская империя' -> 'Контрольная_Римская_империя.pdf'"""
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", title or "").strip(" .")
    name = re.sub(r"\s+", "_", name)[:60] or default
    return name if name.lower().endswith(".pdf") else name + ".pdf"


def md_to_pdf(text, out_path=None, title=None, strip_intro="auto"):
    """Сохраняет PDF в файл (out_path) или возвращает bytes, если out_path=None."""
    return convert(text, out_path, strip_intro, title)


def make_pdf(text, title=None, filename=None, strip_intro="auto"):
    """Для ботов. Возвращает (bytes, имя_файла).

    title    — название внутри PDF (если не задано — берётся из первого '# ...')
    filename — имя файла, которое увидит пользователь в Telegram
               (если не задано — делается из title)
    """
    title = title or detect_title(text) or "Документ"
    data = convert(text, None, strip_intro, title)
    return data, safe_filename(filename or title)


def make_pdf_io(text, title=None, filename=None, strip_intro="auto"):
    """BytesIO с атрибутом .name — для python-telegram-bot и pyTelegramBotAPI."""
    import io
    data, name = make_pdf(text, title, filename, strip_intro)
    bio = io.BytesIO(data)
    bio.name = name
    return bio


async def make_pdf_async(text, title=None, filename=None, strip_intro="auto"):
    """Асинхронная обёртка (aiogram и др.): сборка PDF идёт в отдельном потоке,
    чтобы бот не «зависал» на время генерации. Возвращает (bytes, имя_файла)."""
    import asyncio
    return await asyncio.to_thread(make_pdf, text, title, filename, strip_intro)


def main():
    ap = argparse.ArgumentParser(description="Gemini Markdown -> PDF")
    ap.add_argument("input", nargs="?", help="файл .md/.txt с текстом от Gemini")
    ap.add_argument("-o", "--output", help="имя PDF (по умолчанию как у входного)")
    ap.add_argument("--keep-intro", action="store_true",
                    help="не вырезать вступление Gemini (по умолчанию оно убирается само)")
    ap.add_argument("--paste", action="store_true",
                    help="читать текст из консоли вместо файла")
    args = ap.parse_args()

    if args.paste or not args.input:
        print("Вставьте текст и завершите ввод (Ctrl+D, на Windows Ctrl+Z и Enter):")
        text = sys.stdin.read()
        out = args.output or "output.pdf"
    else:
        with open(args.input, encoding="utf-8") as f:
            text = f.read()
        out = args.output or os.path.splitext(args.input)[0] + ".pdf"

    convert(text, out, False if args.keep_intro else "auto")
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()