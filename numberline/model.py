"""数轴练习纸的数据模型与参数校验。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

MIN_VALUE = -1000
MAX_VALUE = 1000
MAX_SPAN = 200
MIN_STEP = 1
MAX_STEP = 100
MAX_BLANK = 200
MIN_LINES = 1
MAX_LINES = 8
MIN_PAGES = 1
MAX_PAGES = 10
MAX_TITLE = 40
DEFAULT_TITLE = "数轴练习纸"


class NumberLineError(ValueError):
    """数轴参数或渲染参数不合法。"""


def _require_int(value: object, name: str, minimum: int, maximum: int) -> int:
    """校验整数参数，拒绝布尔值与浮点数，并检查闭区间范围。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise NumberLineError("%s必须是整数" % name)
    if not minimum <= value <= maximum:
        raise NumberLineError(
            "%s必须在 %d~%d 之间，当前是 %d" % (name, minimum, maximum, value)
        )
    return value


@dataclass(frozen=True)
class NumberLine:
    """一条数轴：起点、终点、步长与留空间隔。"""

    start: int
    end: int
    step: int = 1
    blank_every: int = 0

    def __post_init__(self) -> None:
        start = _require_int(self.start, "起点", MIN_VALUE, MAX_VALUE)
        end = _require_int(self.end, "终点", MIN_VALUE, MAX_VALUE)
        step = _require_int(self.step, "步长", MIN_STEP, MAX_STEP)
        blank_every = _require_int(self.blank_every, "留空间隔", 0, MAX_BLANK)
        if start >= end:
            raise NumberLineError(
                "起点必须小于终点，当前起点 %d，终点 %d" % (start, end)
            )
        span = end - start
        if span > MAX_SPAN:
            raise NumberLineError(
                "跨度不能超过 %d，当前从 %d 到 %d 共 %d"
                % (MAX_SPAN, start, end, span)
            )
        if span % step != 0:
            raise NumberLineError(
                "步长 %d 不能整除跨度 %d（%d 到 %d），请选择能整除的步长"
                % (step, span, start, end)
            )
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "step", step)
        object.__setattr__(self, "blank_every", blank_every)

    @property
    def span(self) -> int:
        """起点到终点的跨度。"""
        return self.end - self.start

    @property
    def tick_count(self) -> int:
        """包含两端在内的刻度数量。"""
        return self.span // self.step + 1

    def tick_values(self) -> Tuple[int, ...]:
        """按刻度索引返回全部刻度值。"""
        return tuple(
            self.start + index * self.step for index in range(self.tick_count)
        )

    def _check_index(self, index: int) -> int:
        if isinstance(index, bool) or not isinstance(index, int):
            raise NumberLineError("刻度索引必须是整数")
        if not 0 <= index < self.tick_count:
            raise NumberLineError("刻度索引超出范围：%d" % index)
        return index

    def value_at(self, index: int) -> int:
        """取某个刻度索引对应的数值。"""
        index = self._check_index(index)
        return self.start + index * self.step

    def is_hidden(self, index: int) -> bool:
        """判断该刻度是否按「每 N 个留空」规则隐藏标签。"""
        index = self._check_index(index)
        if self.blank_every <= 0:
            return False
        return (index + 1) % self.blank_every == 0

    def label_at(self, index: int) -> Optional[int]:
        """取需要显示的数字标签，隐藏时返回 None。"""
        index = self._check_index(index)
        if self.is_hidden(index):
            return None
        return self.value_at(index)

    def zero_index(self) -> Optional[int]:
        """零点所在刻度索引；数轴不含 0 时返回 None。"""
        if not self.start <= 0 <= self.end:
            return None
        offset = -self.start
        if offset % self.step != 0:
            return None
        return offset // self.step

    def is_zero(self, index: int) -> bool:
        """判断该刻度是否为 0。"""
        return self.value_at(index) == 0


@dataclass(frozen=True)
class Worksheet:
    """一页或多页练习纸：统一的一条数轴排版参数。"""

    line: NumberLine
    lines: int = 4
    pages: int = 1
    title: str = DEFAULT_TITLE
    show_tip: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.line, NumberLine):
            raise NumberLineError("line 必须是 NumberLine 对象")
        lines = _require_int(self.lines, "每页数轴条数", MIN_LINES, MAX_LINES)
        pages = _require_int(self.pages, "页数", MIN_PAGES, MAX_PAGES)
        if not isinstance(self.show_tip, bool):
            raise NumberLineError("是否显示提示必须是布尔值")
        if not isinstance(self.title, str):
            raise NumberLineError("标题必须是文本")
        title = self.title.strip()
        if not title:
            raise NumberLineError("标题不能为空")
        if len(title) > MAX_TITLE:
            raise NumberLineError("标题最多 %d 个字符" % MAX_TITLE)
        object.__setattr__(self, "lines", lines)
        object.__setattr__(self, "pages", pages)
        object.__setattr__(self, "title", title)

    @property
    def total_lines(self) -> int:
        """所有页面的数轴总条数。"""
        return self.lines * self.pages


def make_worksheet(
    start: int,
    end: int,
    step: int = 1,
    blank_every: int = 0,
    lines: int = 4,
    pages: int = 1,
    title: str = DEFAULT_TITLE,
    show_tip: bool = True,
) -> Worksheet:
    """一次性构造练习纸配置。"""
    return Worksheet(
        line=NumberLine(
            start=start, end=end, step=step, blank_every=blank_every
        ),
        lines=lines,
        pages=pages,
        title=title,
        show_tip=show_tip,
    )
