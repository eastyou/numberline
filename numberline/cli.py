"""命令行入口：生成 A4 可打印数轴练习纸。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    DEFAULT_TITLE,
    MAX_LINES,
    MAX_PAGES,
    MAX_STEP,
    MAX_VALUE,
    MIN_LINES,
    MIN_PAGES,
    MIN_STEP,
    MIN_VALUE,
    NumberLine,
    NumberLineError,
    Worksheet,
)
from .render import render_html


def _int_arg(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("必须是整数：%s" % text)


class _ChineseArgumentParser(argparse.ArgumentParser):
    """把 argparse 的常见英文错误提示转成中文。"""

    def error(self, message: str) -> None:
        translated = message
        if message.startswith("the following arguments are required:"):
            translated = "缺少必填参数：%s" % message.split(":", 1)[1].strip()
        elif message.startswith("unrecognized arguments:"):
            translated = "无法识别的参数：%s" % message.split(":", 1)[1].strip()
        elif message.startswith("argument "):
            translated = message.replace("argument ", "参数 ", 1)
        self.print_usage(sys.stderr)
        self.exit(2, "错误: %s\n" % translated)


def build_parser() -> argparse.ArgumentParser:
    parser = _ChineseArgumentParser(
        prog="numberline",
        description="数轴练习纸：一键生成 A4 可打印的数轴读数与描点练习",
    )
    parser.add_argument("--version", action="version", version="numberline 0.1.0")
    parser.add_argument(
        "--start",
        type=_int_arg,
        required=True,
        help="数轴起点（整数，%d~%d）" % (MIN_VALUE, MAX_VALUE),
    )
    parser.add_argument(
        "--end",
        type=_int_arg,
        required=True,
        help="数轴终点（整数，%d~%d，必须大于起点）" % (MIN_VALUE, MAX_VALUE),
    )
    parser.add_argument(
        "--step",
        type=_int_arg,
        default=1,
        help="刻度间隔（%d~%d，必须整除跨度，默认 1）" % (MIN_STEP, MAX_STEP),
    )
    parser.add_argument(
        "--blank-every",
        type=_int_arg,
        default=0,
        help="每 N 个刻度隐藏一个数字标签，0 表示全部显示（默认 0）",
    )
    parser.add_argument(
        "--lines",
        type=_int_arg,
        default=4,
        help="每页数轴条数（%d~%d，默认 4）" % (MIN_LINES, MAX_LINES),
    )
    parser.add_argument(
        "--pages",
        type=_int_arg,
        default=1,
        help="页数（%d~%d，默认 1）" % (MIN_PAGES, MAX_PAGES),
    )
    parser.add_argument("--title", default=DEFAULT_TITLE, help="页面标题")
    parser.add_argument(
        "--no-tip", action="store_true", help="不显示页脚的「描点小提示」"
    )
    parser.add_argument(
        "-o", "--output", default="数轴练习纸.html", help="输出 HTML 路径"
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        worksheet = Worksheet(
            line=NumberLine(
                start=args.start,
                end=args.end,
                step=args.step,
                blank_every=args.blank_every,
            ),
            lines=args.lines,
            pages=args.pages,
            title=args.title,
            show_tip=not args.no_tip,
        )
        page = render_html(worksheet)
    except NumberLineError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 条/页 × %d 页，数轴 %d~%d，每格 %d"
        % (
            args.output,
            worksheet.lines,
            worksheet.pages,
            worksheet.line.start,
            worksheet.line.end,
            worksheet.line.step,
        )
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向、边距选「无」即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
