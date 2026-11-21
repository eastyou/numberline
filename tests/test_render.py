"""数轴渲染单元测试。"""

from __future__ import annotations

import re
import unittest

from numberline.model import NumberLine, NumberLineError, Worksheet
from numberline.render import (
    LABEL_BASELINE_MM,
    MAX_LABEL_FONT_MM,
    MIN_LABEL_FONT_MM,
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

TICK_X_RE = re.compile(r'class="tick(?: zero)?" x1="(-?[0-9.]+)"')


class SvgTest(unittest.TestCase):
    def setUp(self) -> None:
        self.line = NumberLine(-10, 10, 1)
        self.svg = render_svg(self.line)

    def test_svg_size(self) -> None:
        self.assertIn('width="170mm"', self.svg)
        self.assertIn('height="22mm"', self.svg)
        self.assertIn('viewBox="0 0 170 22"', self.svg)
        self.assertEqual(SVG_WIDTH_MM, 170.0)
        self.assertEqual(SVG_HEIGHT_MM, 22.0)

    def test_tick_count(self) -> None:
        positions = TICK_X_RE.findall(self.svg)
        self.assertEqual(len(positions), self.line.tick_count)

    def test_tick_positions_uniform(self) -> None:
        positions = [float(value) for value in TICK_X_RE.findall(self.svg)]
        gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
        expected = TICK_WIDTH_MM / self.line.span
        for gap in gaps:
            self.assertAlmostEqual(gap, expected, delta=0.01)

    def test_tick_positions_endpoints(self) -> None:
        positions = [float(value) for value in TICK_X_RE.findall(self.svg)]
        self.assertAlmostEqual(positions[0], TICK_LEFT_MM, places=3)
        self.assertAlmostEqual(positions[-1], TICK_RIGHT_MM, places=3)

    def test_tick_x_mm_by_index(self) -> None:
        self.assertAlmostEqual(tick_x_mm(self.line, 0), 5.0, places=6)
        self.assertAlmostEqual(tick_x_mm(self.line, 10), 85.0, places=6)
        self.assertAlmostEqual(tick_x_mm(self.line, 20), 165.0, places=6)

    def test_tick_x_mm_invalid_index(self) -> None:
        with self.assertRaises(NumberLineError):
            tick_x_mm(self.line, 21)
        with self.assertRaises(NumberLineError):
            tick_x_mm(self.line, -1)
        with self.assertRaises(NumberLineError):
            tick_x_mm("line", 0)  # type: ignore[arg-type]

    def test_all_labels(self) -> None:
        self.assertEqual(self.svg.count("<text "), self.line.tick_count)
        self.assertIn(">-10</text>", self.svg)
        self.assertIn(">10</text>", self.svg)

    def test_negative_label_is_single_text(self) -> None:
        self.assertIn(">-10</text>", self.svg)
        self.assertNotIn(">-</text>", self.svg)

    def test_zero_tick_is_bold(self) -> None:
        self.assertEqual(self.svg.count('class="tick zero"'), 1)
        zero_line = re.search(r'class="tick zero"[^>]*', self.svg)
        self.assertIsNotNone(zero_line)
        assert zero_line is not None
        self.assertIn('stroke-width="0.7"', zero_line.group(0))
        self.assertIn('x1="85"', zero_line.group(0))

    def test_zero_label_is_bold(self) -> None:
        self.assertEqual(self.svg.count('class="label zero"'), 1)
        self.assertIn('font-weight="700"', self.svg)

    def test_arrows(self) -> None:
        self.assertEqual(self.svg.count('class="arrow"'), 2)

    def test_labels_within_viewbox(self) -> None:
        for x_text in re.findall(r'<text class="label(?: zero)?" x="(-?[0-9.]+)"', self.svg):
            x = float(x_text)
            self.assertGreaterEqual(x, 0.0)
            self.assertLessEqual(x, SVG_WIDTH_MM)
        self.assertLess(LABEL_BASELINE_MM, SVG_HEIGHT_MM)

    def test_label_font_bounds(self) -> None:
        self.assertAlmostEqual(label_font_mm(self.line), MAX_LABEL_FONT_MM)
        dense = NumberLine(-1000, -800, 1)
        self.assertAlmostEqual(label_font_mm(dense), MIN_LABEL_FONT_MM)

    def test_hidden_labels_leave_gaps(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=2)
        svg = render_svg(line)
        self.assertEqual(svg.count("<text "), 11)
        self.assertIn(">-10</text>", svg)
        self.assertIn(">10</text>", svg)
        self.assertIn(">0</text>", svg)
        self.assertNotIn(">-9</text>", svg)
        self.assertNotIn(">1</text>", svg)

    def test_hidden_labels_keep_ticks(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=2)
        svg = render_svg(line)
        self.assertEqual(len(TICK_X_RE.findall(svg)), 21)
        self.assertIn(">0</text>", render_svg(NumberLine(-10, 10, 1)))

    def test_zero_label_can_be_hidden(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=11)
        svg = render_svg(line)
        self.assertNotIn(">0</text>", svg)
        self.assertEqual(svg.count('class="tick zero"'), 1)

    def test_line_without_zero(self) -> None:
        svg = render_svg(NumberLine(-3, 5, 2))
        self.assertNotIn('class="tick zero"', svg)
        self.assertNotIn('class="label zero"', svg)

    def test_no_external_resources(self) -> None:
        page = render_html(Worksheet(self.line))
        self.assertNotIn("<link", page)
        self.assertNotIn("@import", page)
        self.assertNotIn('src="http', page)
        self.assertNotIn('href="http', page)
        self.assertNotIn("<script", page)

    def test_render_svg_invalid_line(self) -> None:
        with self.assertRaises(NumberLineError):
            render_svg("line")  # type: ignore[arg-type]


class HtmlTest(unittest.TestCase):
    def test_document(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10)))
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn('<html lang="zh-CN">', page)
        self.assertIn('charset="utf-8"', page)

    def test_a4_print_css(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10)))
        self.assertIn("@page { size: A4 portrait; margin: 0; }", page)
        self.assertIn("width: 210mm", page)
        self.assertIn("height: 297mm", page)

    def test_page_count(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), pages=3))
        self.assertEqual(page.count('<section class="sheet">'), 3)

    def test_lines_per_page(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), lines=3, pages=2))
        self.assertEqual(page.count("<svg "), 6)
        sections = page.split('<section class="sheet">')[1:]
        self.assertEqual(len(sections), 2)
        for section in sections:
            self.assertEqual(section.count("<svg "), 3)

    def test_page_numbers(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), pages=2))
        self.assertIn("第 1 页 / 共 2 页", page)
        self.assertIn("第 2 页 / 共 2 页", page)

    def test_custom_title(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), title="整数学轴"))
        self.assertIn("<h1>整数学轴</h1>", page)
        self.assertIn("<title>整数学轴</title>", page)

    def test_title_escaped(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), title="<数轴>"))
        self.assertIn("&lt;数轴&gt;", page)
        self.assertNotIn("<h1><数轴></h1>", page)

    def test_title_on_every_page(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), title="数轴", pages=2))
        self.assertEqual(page.count("<h1>数轴</h1>"), 2)

    def test_subtitle(self) -> None:
        page = render_html(
            Worksheet(NumberLine(-10, 10, 2, blank_every=2), title="数轴")
        )
        self.assertIn("从 -10 到 10 · 每格 2 · 每 2 个刻度留空", page)

    def test_subtitle_without_blank(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10)))
        self.assertIn("从 -10 到 10 · 每格 1", page)
        self.assertNotIn("留空", page)

    def test_tip_default(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10)))
        self.assertIn(TIP_TEXT, page)

    def test_no_tip(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10), show_tip=False))
        self.assertNotIn(TIP_TEXT, page)
        self.assertIn("第 1 页 / 共 1 页", page)

    def test_blank_every_affects_all_lines(self) -> None:
        page = render_html(
            Worksheet(NumberLine(-10, 10, 1, blank_every=2), lines=2)
        )
        self.assertEqual(page.count("<text "), 22)

    def test_negative_range(self) -> None:
        page = render_html(Worksheet(NumberLine(-1000, -800, 50), lines=2))
        self.assertIn(">-1000</text>", page)
        self.assertIn(">-800</text>", page)

    def test_invalid_worksheet(self) -> None:
        with self.assertRaises(NumberLineError):
            render_html("worksheet")  # type: ignore[arg-type]

    def test_screen_scaling_rules(self) -> None:
        page = render_html(Worksheet(NumberLine(-10, 10)))
        self.assertIn("max-width: 100%", page)
        self.assertIn("@media screen and (max-width: 640px)", page)
        self.assertIn("@media print", page)


if __name__ == "__main__":
    unittest.main()
