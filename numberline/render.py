"""把数轴练习纸渲染成自包含的 A4 纵向 HTML。"""

from __future__ import annotations

import html
from typing import List

from .model import NumberLine, NumberLineError, Worksheet

SVG_WIDTH_MM = 170.0
SVG_HEIGHT_MM = 22.0
TICK_LEFT_MM = 5.0
TICK_RIGHT_MM = 165.0
TICK_WIDTH_MM = TICK_RIGHT_MM - TICK_LEFT_MM
AXIS_Y_MM = 10.0
TICK_TOP_MM = 8.6
TICK_BOTTOM_MM = 11.4
ZERO_TOP_MM = 7.8
ZERO_BOTTOM_MM = 12.2
ARROW_TIP_LEFT_MM = 2.2
ARROW_TIP_RIGHT_MM = 167.8
LABEL_BASELINE_MM = 16.4
MIN_LABEL_FONT_MM = 1.2
MAX_LABEL_FONT_MM = 3.2

TIP_TEXT = "描点小提示：先在数轴上找到 0，再按刻度逐格数；正数向右，负数向左，最后用小圆点标出位置。"


def _num(value: float) -> str:
    """把毫米坐标格式化成紧凑文本，避免浮点尾数。"""
    text = "%.3f" % value
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text == "-0":
        return "0"
    return text


def tick_x_mm(line: NumberLine, index: int) -> float:
    """按整数刻度索引计算刻度横坐标，避免逐格累加误差。"""
    if not isinstance(line, NumberLine):
        raise NumberLineError("line 必须是 NumberLine 对象")
    if isinstance(index, bool) or not isinstance(index, int):
        raise NumberLineError("刻度索引必须是整数")
    if not 0 <= index < line.tick_count:
        raise NumberLineError("刻度索引超出范围：%d" % index)
    return TICK_LEFT_MM + (index * TICK_WIDTH_MM) / line.span


def label_font_mm(line: NumberLine) -> float:
    """按刻度间距与最长数字自动收缩标签字号。"""
    if not isinstance(line, NumberLine):
        raise NumberLineError("line 必须是 NumberLine 对象")
    spacing = TICK_WIDTH_MM / line.span
    longest = max(len(str(value)) for value in line.tick_values())
    size = spacing * 0.9 / (float(longest) * 0.55)
    return max(MIN_LABEL_FONT_MM, min(MAX_LABEL_FONT_MM, size))


def render_svg(line: NumberLine) -> str:
    """绘制单条数轴 SVG，坐标单位与毫米一一对应。"""
    if not isinstance(line, NumberLine):
        raise NumberLineError("line 必须是 NumberLine 对象")
    font = label_font_mm(line)
    label = "数轴，从 %d 到 %d，每格 %d" % (line.start, line.end, line.step)
    parts: List[str] = [
        '<svg class="numberline" xmlns="http://www.w3.org/2000/svg"'
        ' width="%smm" height="%smm" viewBox="0 0 %s %s"'
        ' role="img" aria-label="%s">'
        % (
            _num(SVG_WIDTH_MM),
            _num(SVG_HEIGHT_MM),
            _num(SVG_WIDTH_MM),
            _num(SVG_HEIGHT_MM),
            html.escape(label),
        ),
        '<g class="axis">',
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#0f172a"'
        ' stroke-width="0.4"/>'
        % (
            _num(TICK_LEFT_MM),
            _num(AXIS_Y_MM),
            _num(TICK_RIGHT_MM),
            _num(AXIS_Y_MM),
        ),
        '<polygon class="arrow" points="%s,%s %s,%s %s,%s" fill="#0f172a"/>'
        % (
            _num(ARROW_TIP_LEFT_MM),
            _num(AXIS_Y_MM),
            _num(TICK_LEFT_MM),
            _num(AXIS_Y_MM - 1.2),
            _num(TICK_LEFT_MM),
            _num(AXIS_Y_MM + 1.2),
        ),
        '<polygon class="arrow" points="%s,%s %s,%s %s,%s" fill="#0f172a"/>'
        % (
            _num(ARROW_TIP_RIGHT_MM),
            _num(AXIS_Y_MM),
            _num(TICK_RIGHT_MM),
            _num(AXIS_Y_MM - 1.2),
            _num(TICK_RIGHT_MM),
            _num(AXIS_Y_MM + 1.2),
        ),
        "</g>",
        '<g class="ticks">',
    ]
    for index in range(line.tick_count):
        x = _num(tick_x_mm(line, index))
        if line.is_zero(index):
            parts.append(
                '<line class="tick zero" x1="%s" y1="%s" x2="%s" y2="%s"'
                ' stroke="#0f172a" stroke-width="0.7"/>'
                % (x, _num(ZERO_TOP_MM), x, _num(ZERO_BOTTOM_MM))
            )
        else:
            parts.append(
                '<line class="tick" x1="%s" y1="%s" x2="%s" y2="%s"'
                ' stroke="#475569" stroke-width="0.35"/>'
                % (x, _num(TICK_TOP_MM), x, _num(TICK_BOTTOM_MM))
            )
    parts.append("</g>")
    parts.append('<g class="labels">')
    for index in range(line.tick_count):
        value = line.label_at(index)
        if value is None:
            continue
        x = _num(tick_x_mm(line, index))
        if line.is_zero(index):
            parts.append(
                '<text class="label zero" x="%s" y="%s" text-anchor="middle"'
                ' font-size="%s" font-weight="700" fill="#0f172a">%s</text>'
                % (x, _num(LABEL_BASELINE_MM), _num(font), html.escape(str(value)))
            )
        else:
            parts.append(
                '<text class="label" x="%s" y="%s" text-anchor="middle"'
                ' font-size="%s" fill="#0f172a">%s</text>'
                % (x, _num(LABEL_BASELINE_MM), _num(font), html.escape(str(value)))
            )
    parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def _line_block(line: NumberLine, number: int) -> str:
    return (
        '<div class="line"><span class="no">%d</span>%s</div>'
        % (number, render_svg(line))
    )


def _footer(page: int, pages: int, show_tip: bool) -> str:
    tip = (
        '<span class="tip">%s</span>' % html.escape(TIP_TEXT) if show_tip else ""
    )
    return (
        '<footer class="foot">%s<span class="page">第 %d 页 / 共 %d 页</span>'
        "</footer>" % (tip, page, pages)
    )


def render_html(worksheet: Worksheet) -> str:
    """生成完整 HTML：A4 纵向、每页多条数轴、页脚页码。"""
    if not isinstance(worksheet, Worksheet):
        raise NumberLineError("worksheet 必须是 Worksheet 对象")
    line = worksheet.line
    title = html.escape(worksheet.title)
    subtitle = "从 %d 到 %d · 每格 %d" % (line.start, line.end, line.step)
    if line.blank_every > 0:
        subtitle += " · 每 %d 个刻度留空" % line.blank_every
    subtitle = html.escape(subtitle)
    summary = "%d 条/页 · 共 %d 页 · %d~%d，每格 %d" % (
        worksheet.lines,
        worksheet.pages,
        line.start,
        line.end,
        line.step,
    )

    sheets: List[str] = []
    for page in range(1, worksheet.pages + 1):
        blocks = "".join(
            _line_block(line, number)
            for number in range(1, worksheet.lines + 1)
        )
        sheets.append(
            '<section class="sheet">'
            '<header class="head"><h1>%s</h1><p class="sub">%s</p></header>'
            '<div class="lines">%s</div>%s</section>'
            % (title, subtitle, blocks, _footer(page, worksheet.pages, worksheet.show_tip))
        )

    toolbar = (
        '<div class="toolbar"><strong>%s</strong><span>%s</span></div>'
        % (title, html.escape(summary))
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
        "%s\n<main>%s</main>\n</body>\n</html>\n"
        % (title, _style(), toolbar, "".join(sheets))
    )


def _style() -> str:
    return """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 7mm 4mm 9mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC",
      "Source Han Sans SC", sans-serif;
  }
  .toolbar {
    width: 210mm;
    max-width: 100%;
    margin: 0 auto 4mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 10px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    max-width: 100%;
    min-height: 297mm;
    margin: 0 auto 6mm;
    padding: 14mm 15mm 12mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
  }
  .head { text-align: center; margin-bottom: 4mm; }
  .head h1 {
    margin: 0;
    font-size: 20pt;
    font-weight: 600;
    letter-spacing: 4pt;
  }
  .head .sub {
    margin: 1.8mm 0 0;
    font-size: 9.5pt;
    color: #475569;
    letter-spacing: 0.4pt;
  }
  .lines {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
  }
  .line { position: relative; padding: 1.5mm 0; }
  .line .no {
    position: absolute;
    left: -1mm;
    top: 1.5mm;
    font-size: 8pt;
    color: #94a3b8;
  }
  .line svg {
    display: block;
    width: 170mm;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
  }
  .foot {
    margin-top: 3mm;
    padding-top: 2mm;
    border-top: 0.2mm solid #e2e8f0;
    display: flex;
    align-items: baseline;
    font-size: 8pt;
    color: #64748b;
  }
  .foot .page { margin-left: auto; }
  @media screen and (max-width: 640px) {
    body { padding: 4mm 3mm 6mm; }
    .sheet { padding: 8mm 6mm; min-height: 0; }
    .head h1 { font-size: 16pt; letter-spacing: 2pt; }
    .toolbar { flex-direction: column; gap: 2px; }
    .line .no { left: 0; }
  }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet {
      width: 210mm;
      height: 297mm;
      min-height: 0;
      max-width: none;
      margin: 0;
      box-shadow: none;
      padding: 14mm 15mm 12mm;
      page-break-after: always;
      break-after: page;
      overflow: hidden;
    }
    .sheet:last-child { page-break-after: auto; break-after: auto; }
    .line svg { width: 170mm; max-width: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""
