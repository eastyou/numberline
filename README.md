# numberline

[![CI](https://github.com/eastyou/numberline/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/numberline/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给小学到初中用的数轴练习纸生成器：一条命令生成 A4 纵向、可直接打印的数轴读数与描点练习。**零第三方依赖，只用 Python 标准库，不联网。**

每条数轴按毫米精确绘制，刻度等距、两端带箭头、零刻度加粗；可以指定「每 N 个刻度隐藏一个数字」，让学生在留空处补全读数。

## 特性

- **A4 纵向排版**：每条数轴宽 170mm，一页 1~8 条，最多 10 页
- **整数参数可控**：起点/终点、步长、留空规则全部严格校验，中文报错
- **毫米级 SVG**：刻度位置按整数索引 `index × 可用宽度 / 跨度` 计算，不会累积误差
- **零刻度强调**：0 的刻度线更长、更粗，数字标签加粗
- **留空标签**：每 N 个刻度隐藏一个数字，刻度线保留，位置留白
- **负号不分离**：负数整体作为一个文本居中绘制，负号与数字不会错位
- **自适应屏幕**：窄屏下按比例缩放，不横向溢出；打印时保持真实 A4 尺寸
- **完全自包含**：HTML/CSS/SVG 内联，无图片、无脚本、无外部字体或网络请求
- **102 个单元测试**：覆盖参数边界、刻度数量、间距均匀、留空规则、零刻度、转义、退出码

## 安装

```bash
pip install numberline
```

也可以直接下载源码，在项目目录运行：

```bash
python -m numberline --help
```

要求 Python 3.9 及以上，无第三方依赖。

## 用法

生成一页 4 条、每条从 -10 到 10 的数轴，并每隔一个刻度隐藏一个数字：

```bash
python -m numberline --start -10 --end 10 --step 1 --blank-every 2 --lines 4 --pages 1 --title 数轴练习纸 -o examples/数轴练习纸.html
```

用浏览器打开生成的 HTML，按 `Ctrl/Cmd + P` 打印。

### 参数

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `--start` | 数轴起点，整数，-1000~1000 | 必填 |
| `--end` | 数轴终点，整数，-1000~1000，必须大于起点 | 必填 |
| `--step` | 刻度间隔，1~100，必须整除 `end - start` | `1` |
| `--blank-every` | 每 N 个刻度隐藏一个数字标签，0 表示全部显示，范围 0~200 | `0` |
| `--lines` | 每页数轴条数，1~8 | `4` |
| `--pages` | 页数，1~10 | `1` |
| `--title` | 页面标题，最多 40 个字符 | `数轴练习纸` |
| `--no-tip` | 不显示页脚的「描点小提示」 | 关闭 |
| `-o, --output` | 输出 HTML 路径 | `数轴练习纸.html` |

约束：

- 跨度 `end - start` 不能超过 200
- `--step` 必须能整除跨度，例如 -10 到 10、步长 3 会报错「步长 3 不能整除跨度 20」
- 退出码：参数错误 `2`，文件读写失败 `1`，成功 `0`

### 留空规则

从第一个刻度开始按顺序计数，每第 N 个刻度隐藏数字标签。例如 `--blank-every 2`：

```text
-10  ▢  -8  ▢  -6  ▢  -4  ▢  -2  ▢  0  ▢  2  ▢  4  ▢  6  ▢  8  ▢  10
```

被隐藏的位置仍保留刻度线，只是不绘制数字，方便学生补全。`--blank-every 0` 显示全部数字；`N` 大于刻度总数时不会隐藏任何标签。

## 打印

浏览器打开 HTML 后按 `Ctrl/Cmd + P`：

- 纸张：**A4 纵向**
- 边距：**无**（页面已内置 14/15/12mm 边距）
- 缩放：**100%**，不要选「适合页面」
- 勾选「背景图形」，确保标题、线条与页脚正常打印

屏幕预览会自动适应窄窗口；打印样式使用固定毫米尺寸，保证量出来的刻度间距与真实尺子一致。

## 教学用法

- **读数练习**：用 `--blank-every 2` 或 `3`，让学生补全被隐藏的数字，再圈出指定整数
- **描点练习**：口述坐标（如 -7、0、4），学生在对应刻度上画小圆点
- **正负数与方向**：从 0 出发，正数向右数、负数向左数，配合箭头理解方向
- **相反数与绝对值**：打印 `-10~10`，比较关于 0 对称的两个点
- **比较大小**：在同一数轴上标出多个整数，从左到右排序
- **课堂批量**：`--pages 4` 一次打印四页，页面底部自带页码与描点提示

小范围（跨度 20 左右、步长 1）的读数效果最好；跨度较大时建议把步长设为 2、5、10，避免标签过密。

## 项目结构

```text
numberline/
├── numberline/
│   ├── __init__.py     # 包导出与版本号
│   ├── __main__.py     # python -m numberline
│   ├── cli.py          # 命令行参数与退出码
│   ├── model.py        # 参数校验、刻度与留空规则
│   └── render.py       # 毫米级 SVG 与 A4 页面排版
├── tests/
│   ├── test_model.py   # 模型与边界校验
│   ├── test_render.py  # SVG 坐标、标签、页面结构
│   └── test_cli.py     # 命令行退出码与文件读写
├── examples/
│   └── 数轴练习纸.html  # 示例输出
├── .github/workflows/ci.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

## 开发

```bash
# 运行全部单元测试（102 个）
python3 -m unittest discover -s tests

# 生成示例
python3 -m numberline --start -10 --end 10 --step 1 --blank-every 2 --lines 4 --pages 1 --title 数轴练习纸 -o examples/数轴练习纸.html
```

CI 覆盖 Ubuntu、macOS、Windows 与 Python 3.9/3.10/3.13：先跑单元测试，再用命令行生成 HTML 并断言刻度、标签、纸张方向与标题。

## 许可证

[MIT](LICENSE) © 2026 eastyou
