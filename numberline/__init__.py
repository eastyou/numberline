"""numberline：A4 可打印数轴练习纸生成器。"""

from __future__ import annotations

from .model import (
    DEFAULT_TITLE,
    MAX_BLANK,
    MAX_LINES,
    MAX_PAGES,
    MAX_SPAN,
    MAX_STEP,
    MAX_TITLE,
    MAX_VALUE,
    MIN_LINES,
    MIN_PAGES,
    MIN_STEP,
    MIN_VALUE,
    NumberLine,
    NumberLineError,
    Worksheet,
    make_worksheet,
)
from .render import (
    SVG_HEIGHT_MM,
    SVG_WIDTH_MM,
    TICK_LEFT_MM,
    TICK_RIGHT_MM,
    TICK_WIDTH_MM,
    TIP_TEXT,
    label_font_mm,
    render_html,
    render_svg,
    tick_x_mm,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_TITLE",
    "MAX_BLANK",
    "MAX_LINES",
    "MAX_PAGES",
    "MAX_SPAN",
    "MAX_STEP",
    "MAX_TITLE",
    "MAX_VALUE",
    "MIN_LINES",
    "MIN_PAGES",
    "MIN_STEP",
    "MIN_VALUE",
    "NumberLine",
    "NumberLineError",
    "SVG_HEIGHT_MM",
    "SVG_WIDTH_MM",
    "TICK_LEFT_MM",
    "TICK_RIGHT_MM",
    "TICK_WIDTH_MM",
    "TIP_TEXT",
    "Worksheet",
    "__version__",
    "label_font_mm",
    "make_worksheet",
    "render_html",
    "render_svg",
    "tick_x_mm",
]
