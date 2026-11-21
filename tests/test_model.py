"""数轴数据模型单元测试。"""

from __future__ import annotations

import dataclasses
import unittest

from numberline.model import (
    MAX_LINES,
    MAX_PAGES,
    MAX_TITLE,
    NumberLine,
    NumberLineError,
    Worksheet,
    make_worksheet,
)


class NumberLineTest(unittest.TestCase):
    def test_tick_count(self) -> None:
        line = NumberLine(-10, 10, 1)
        self.assertEqual(line.span, 20)
        self.assertEqual(line.tick_count, 21)

    def test_tick_values_endpoints(self) -> None:
        values = NumberLine(-10, 10, 2).tick_values()
        self.assertEqual(values[0], -10)
        self.assertEqual(values[-1], 10)
        self.assertEqual(len(values), 11)

    def test_tick_values_with_step(self) -> None:
        line = NumberLine(0, 12, 3)
        self.assertEqual(line.tick_values(), (0, 3, 6, 9, 12))

    def test_tick_count_max_span(self) -> None:
        line = NumberLine(-1000, -800, 1)
        self.assertEqual(line.span, 200)
        self.assertEqual(line.tick_count, 201)

    def test_tick_count_matches_values(self) -> None:
        line = NumberLine(-9, 15, 3)
        self.assertEqual(len(line.tick_values()), line.tick_count)

    def test_labels_all_shown_by_default(self) -> None:
        line = NumberLine(-3, 3, 1)
        for index in range(line.tick_count):
            self.assertFalse(line.is_hidden(index))
            self.assertEqual(line.label_at(index), line.value_at(index))

    def test_blank_every_two_hides_alternate(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=2)
        hidden = [index for index in range(line.tick_count) if line.is_hidden(index)]
        self.assertEqual(hidden, list(range(1, 20, 2)))
        self.assertEqual(line.label_at(0), -10)
        self.assertIsNone(line.label_at(1))
        self.assertEqual(line.label_at(20), 10)

    def test_blank_every_one_hides_all(self) -> None:
        line = NumberLine(-2, 2, 1, blank_every=1)
        self.assertTrue(all(line.is_hidden(index) for index in range(5)))

    def test_blank_larger_than_tick_count_hides_none(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=50)
        self.assertFalse(any(line.is_hidden(index) for index in range(21)))

    def test_blank_three_hides_every_third(self) -> None:
        line = NumberLine(0, 12, 1, blank_every=3)
        hidden = [index for index in range(line.tick_count) if line.is_hidden(index)]
        self.assertEqual(hidden, [2, 5, 8, 11])

    def test_zero_index(self) -> None:
        line = NumberLine(-10, 10, 1)
        self.assertEqual(line.zero_index(), 10)
        self.assertEqual(line.value_at(10), 0)

    def test_zero_index_absent(self) -> None:
        line = NumberLine(-3, 5, 2)
        self.assertIsNone(line.zero_index())
        self.assertFalse(any(line.is_zero(index) for index in range(line.tick_count)))

    def test_zero_index_positive_line(self) -> None:
        self.assertIsNone(NumberLine(2, 6, 1).zero_index())

    def test_zero_label_and_flag(self) -> None:
        line = NumberLine(-5, 5, 1)
        index = line.zero_index()
        self.assertIsNotNone(index)
        assert index is not None
        self.assertTrue(line.is_zero(index))
        self.assertEqual(line.label_at(index), 0)

    def test_zero_label_can_be_hidden(self) -> None:
        line = NumberLine(-10, 10, 1, blank_every=11)
        self.assertIsNone(line.label_at(10))
        self.assertTrue(line.is_zero(10))

    def test_start_equals_end(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(5, 5)

    def test_start_greater_than_end(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(6, 2)

    def test_start_too_small(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-1001, 0)

    def test_end_too_large(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(0, 1001)

    def test_span_too_large(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-1000, -799)

    def test_span_exact_limit(self) -> None:
        self.assertEqual(NumberLine(-1000, -800).span, 200)

    def test_step_zero(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-1, 1, 0)

    def test_step_too_large(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(0, 200, 101)

    def test_step_not_divisible(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-10, 10, 3)

    def test_step_bool_rejected(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2, True)

    def test_start_float_rejected(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-1.5, 2)  # type: ignore[arg-type]

    def test_end_bool_rejected(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(0, True)  # type: ignore[arg-type]

    def test_blank_negative(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2, 1, -1)

    def test_blank_too_large(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2, 1, 201)

    def test_index_out_of_range(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2).value_at(10)

    def test_index_negative(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2).label_at(-1)

    def test_index_bool_rejected(self) -> None:
        with self.assertRaises(NumberLineError):
            NumberLine(-2, 2).is_hidden(True)

    def test_error_is_value_error(self) -> None:
        self.assertTrue(issubclass(NumberLineError, ValueError))

    def test_frozen_dataclass(self) -> None:
        line = NumberLine(-2, 2)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            line.step = 2  # type: ignore[misc]


class WorksheetTest(unittest.TestCase):
    def test_defaults(self) -> None:
        sheet = Worksheet(NumberLine(-10, 10))
        self.assertEqual(sheet.lines, 4)
        self.assertEqual(sheet.pages, 1)
        self.assertEqual(sheet.title, "数轴练习纸")
        self.assertTrue(sheet.show_tip)
        self.assertEqual(sheet.total_lines, 4)

    def test_total_lines(self) -> None:
        sheet = Worksheet(NumberLine(-10, 10), lines=3, pages=2)
        self.assertEqual(sheet.total_lines, 6)

    def test_lines_lower_bound(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), lines=0)

    def test_lines_upper_bound(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), lines=MAX_LINES + 1)

    def test_pages_lower_bound(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), pages=0)

    def test_pages_upper_bound(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), pages=MAX_PAGES + 1)

    def test_lines_bool_rejected(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), lines=True)

    def test_title_empty(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), title="   ")

    def test_title_too_long(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), title="题" * (MAX_TITLE + 1))

    def test_title_non_text(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), title=1)  # type: ignore[arg-type]

    def test_title_stripped(self) -> None:
        sheet = Worksheet(NumberLine(-10, 10), title="  数轴练习  ")
        self.assertEqual(sheet.title, "数轴练习")

    def test_show_tip_non_bool(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet(NumberLine(-10, 10), show_tip=1)  # type: ignore[arg-type]

    def test_line_type(self) -> None:
        with self.assertRaises(NumberLineError):
            Worksheet("line")  # type: ignore[arg-type]

    def test_make_worksheet(self) -> None:
        sheet = make_worksheet(-4, 4, step=2, blank_every=2, lines=2, pages=3)
        self.assertEqual(sheet.line.step, 2)
        self.assertEqual(sheet.line.blank_every, 2)
        self.assertEqual(sheet.lines, 2)
        self.assertEqual(sheet.pages, 3)
        self.assertEqual(sheet.total_lines, 6)


if __name__ == "__main__":
    unittest.main()
