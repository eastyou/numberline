"""命令行入口单元测试。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple

from numberline.cli import build_parser, main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.target = self.root / "numberline.html"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> Tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def base_args(self) -> List[str]:
        return [
            "--start",
            "-10",
            "--end",
            "10",
            "-o",
            str(self.target),
        ]

    def test_generate(self) -> None:
        code, out, _ = self.run_cli(self.base_args())
        self.assertEqual(code, 0)
        self.assertTrue(self.target.exists())
        self.assertIn("已生成", out)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("数轴练习纸", page)
        self.assertEqual(page.count("<svg "), 4)

    def test_custom_title_and_pages(self) -> None:
        args = self.base_args() + [
            "--title",
            "整数学轴",
            "--pages",
            "2",
            "--lines",
            "2",
        ]
        code, _, _ = self.run_cli(args)
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("<h1>整数学轴</h1>", page)
        self.assertEqual(page.count('<section class="sheet">'), 2)
        self.assertEqual(page.count("<svg "), 4)
        self.assertIn("第 2 页 / 共 2 页", page)

    def test_parser_defaults(self) -> None:
        args = build_parser().parse_args(["--start", "-10", "--end", "10"])
        self.assertEqual(args.step, 1)
        self.assertEqual(args.blank_every, 0)
        self.assertEqual(args.lines, 4)
        self.assertEqual(args.pages, 1)
        self.assertEqual(args.title, "数轴练习纸")
        self.assertFalse(args.no_tip)
        self.assertEqual(args.output, "数轴练习纸.html")

    def test_blank_every_hides_labels(self) -> None:
        args = self.base_args() + ["--blank-every", "2"]
        code, _, _ = self.run_cli(args)
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count("<text "), 44)

    def test_no_tip(self) -> None:
        args = self.base_args() + ["--no-tip"]
        code, _, _ = self.run_cli(args)
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertNotIn("描点小提示", page)

    def test_step_not_divisible(self) -> None:
        code, _, err = self.run_cli(self.base_args() + ["--step", "3"])
        self.assertEqual(code, 2)
        self.assertIn("步长", err)
        self.assertFalse(self.target.exists())

    def test_span_too_large(self) -> None:
        args = [
            "--start",
            "-500",
            "--end",
            "-299",
            "-o",
            str(self.target),
        ]
        code, _, err = self.run_cli(args)
        self.assertEqual(code, 2)
        self.assertIn("跨度", err)

    def test_start_not_less_than_end(self) -> None:
        args = ["--start", "10", "--end", "10", "-o", str(self.target)]
        code, _, err = self.run_cli(args)
        self.assertEqual(code, 2)
        self.assertIn("起点必须小于终点", err)

    def test_lines_out_of_range(self) -> None:
        code, _, _ = self.run_cli(self.base_args() + ["--lines", "0"])
        self.assertEqual(code, 2)
        self.assertFalse(self.target.exists())

    def test_pages_out_of_range(self) -> None:
        code, _, _ = self.run_cli(self.base_args() + ["--pages", "11"])
        self.assertEqual(code, 2)

    def test_blank_negative(self) -> None:
        code, _, _ = self.run_cli(self.base_args() + ["--blank-every", "-1"])
        self.assertEqual(code, 2)

    def test_output_is_directory(self) -> None:
        code, _, err = self.run_cli(
            ["--start", "-10", "--end", "10", "-o", str(self.root)]
        )
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_output_parent_missing(self) -> None:
        target = self.root / "missing" / "numberline.html"
        code, _, err = self.run_cli(
            ["--start", "-10", "--end", "10", "-o", str(target)]
        )
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", err)

    def test_missing_required_argument(self) -> None:
        err = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(err):
                main(["--start", "-10", "-o", str(self.target)])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("缺少必填参数", err.getvalue())

    def test_non_integer_argument(self) -> None:
        err = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(err):
                main(["--start", "abc", "--end", "10"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("必须是整数", err.getvalue())

    def test_unrecognized_argument(self) -> None:
        err = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(err):
                main(self.base_args() + ["--unknown"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("无法识别的参数", err.getvalue())

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_version(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--version"])
        self.assertEqual(ctx.exception.code, 0)

    def test_negative_start_range(self) -> None:
        args = [
            "--start",
            "-1000",
            "--end",
            "-900",
            "--step",
            "50",
            "-o",
            str(self.target),
        ]
        code, _, _ = self.run_cli(args)
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn(">-1000</text>", page)


if __name__ == "__main__":
    unittest.main()
