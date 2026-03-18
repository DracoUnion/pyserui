# PySerUI

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows/)

PySerUI 是一个基于 `pywin32` 的 Python DirectUI 框架，专为 Windows 平台设计。

原项目 [SyserUI Engine](https://github.com/wizardforcel/syser-ui-engine) 是由 Baby (Syser Group) 于 2008-2012 年间使用易语言开发的 DirectUI 引擎，本项目是其 Python 重写版本。

## 特性

- **DirectUI 架构** - 无原生控件句柄，所有控件自绘制，轻量且高度可定制
- **GDI+ 图形加速** - 使用 GDI+ 进行高质量图形渲染，支持抗锯齿和透明效果
- **丰富的控件库** - 提供标签、按钮、编辑框、面板、进度条、复选框、单选按钮等常用控件
- **灵活的布局系统** - 支持 Dock 停靠和 Anchor 锚定布局
- **事件驱动** - 基于委托（Delegate）的事件处理机制
- **自定义绘制** - 支持控件自定义绘制，轻松实现个性化界面

## 安装

### 环境要求

- Windows 操作系统
- Python 3.7 或更高版本

### 通过 pip 安装

```bash
pip install pyserui
```

### 从源码安装

```bash
git clone https://github.com/wizardforcel/pyserui.git
cd pyserui
pip install -e .
```

## 快速开始

```python
import pyserui
from pyserui import SuiWindow, SuiLabel, SuiButton
import win32con

# 定义主窗口
class MainWindow(SuiWindow):
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 600

        # 创建标签
        self.label = SuiLabel()
        self.label.set_bounds(20, 20, 200, 30)
        self.label.text = "Hello, PySerUI!"
        self.add_child(self.label)

        # 创建按钮
        self.button = SuiButton()
        self.button.set_bounds(20, 60, 120, 35)
        self.button.text = "点击我"
        self.button.on_click += self.on_button_click
        self.add_child(self.button)

    def on_button_click(self, sender):
        self.label.text = "按钮被点击了！"

def main():
    # 初始化引擎
    pyserui.initialize()

    try:
        # 创建并显示窗口
        window = MainWindow()
        window.create(title="PySerUI Demo", width=800, height=600)

        # 运行应用
        pyserui.run_application(window)
    finally:
        # 关闭引擎
        pyserui.shutdown()

if __name__ == "__main__":
    main()
```

## 核心概念

### 应用程序生命周期

```python
import pyserui

# 初始化 GDI+ 和内部资源
pyserui.initialize()

# ... 创建窗口和控件 ...

# 运行消息循环
pyserui.run_application(window)

# 清理资源
pyserui.shutdown()
```

### 窗口 (SuiWindow)

`SuiWindow` 是所有窗口和控件的基类，提供基本的消息处理和绘制功能。

```python
from pyserui import SuiWindow

window = SuiWindow()
window.create(title="我的窗口", x=100, y=100, width=800, height=600)
window.show()
```

### 控件 (SuiControl)

控件是放置在窗口中的可交互元素。

```python
from pyserui import SuiLabel, SuiButton, SuiEdit, SuiPanel

# 标签
label = SuiLabel()
label.text = "这是一个标签"
label.set_bounds(10, 10, 200, 25)

# 按钮
button = SuiButton()
button.text = "确定"
button.set_bounds(10, 40, 80, 30)

# 编辑框
edit = SuiEdit()
edit.text = "输入文本..."
edit.set_bounds(10, 80, 200, 25)

# 面板（容器）
panel = SuiPanel()
panel.set_bounds(10, 120, 300, 200)
panel.back_color = make_color(240, 240, 240)
```

### 事件处理

使用 `+=` 运算符订阅事件，使用 `-=` 取消订阅。

```python
def on_click(sender):
    print(f"按钮 {sender.text} 被点击")

button.on_click += on_click

# 所有控件支持的事件
button.on_mouse_down += lambda x, y, btn: print(f"鼠标按下: ({x}, {y}), 按钮: {btn}")
button.on_mouse_up += lambda x, y, btn: print(f"鼠标释放")
button.on_mouse_enter += lambda: print("鼠标进入")
button.on_mouse_leave += lambda: print("鼠标离开")
```

### 颜色和样式

```python
from pyserui import make_color, Colors

# 使用预定义颜色
button.back_color = Colors.White
button.fore_color = Colors.Black

# 自定义颜色（RGB）
button.back_color = make_color(100, 150, 255)  # 蓝色

# 可用的预定义颜色
# Colors.Black, Colors.White, Colors.Red, Colors.Green, Colors.Blue
# Colors.Yellow, Colors.Cyan, Colors.Magenta, Colors.Gray
```

## 控件列表

| 控件 | 类名 | 说明 |
|------|------|------|
| 标签 | `SuiLabel` | 显示静态文本 |
| 按钮 | `SuiButton` | 可点击按钮，支持悬停和按下效果 |
| 编辑框 | `SuiEdit` | 单行文本输入 |
| 面板 | `SuiPanel` | 容器控件，用于组织其他控件 |
| 进度条 | `SuiProgressBar` | 显示进度百分比 |
| 复选框 | `SuiCheckBox` | 多选控件 |
| 单选按钮 | `SuiRadioButton` | 单选控件，自动分组 |

## 完整示例

```python
import pyserui
from pyserui import (
    SuiWindow, SuiPanel, SuiLabel, SuiButton, SuiEdit,
    SuiCheckBox, SuiRadioButton, SuiProgressBar,
    make_color, Colors
)

class DemoWindow(SuiWindow):
    def __init__(self):
        super().__init__()
        self.width = 600
        self.height = 400

        # 主面板
        panel = SuiPanel()
        panel.set_bounds(10, 10, 580, 380)
        panel.back_color = make_color(245, 245, 245)
        self.add_child(panel)

        # 标题
        title = SuiLabel()
        title.set_bounds(20, 20, 540, 40)
        title.text = "PySerUI 控件演示"
        title.font_size = 16
        title.font_bold = True
        title.text_align = 'center'
        panel.add_child(title)

        # 输入框
        self.edit = SuiEdit()
        self.edit.set_bounds(20, 80, 250, 30)
        self.edit.text = "在这里输入..."
        panel.add_child(self.edit)

        # 提交按钮
        submit_btn = SuiButton()
        submit_btn.set_bounds(280, 80, 80, 30)
        submit_btn.text = "提交"
        submit_btn.back_color = make_color(0, 120, 215)
        submit_btn.fore_color = Colors.White
        submit_btn.on_click += self.on_submit
        panel.add_child(submit_btn)

        # 复选框
        self.check = SuiCheckBox()
        self.check.set_bounds(20, 130, 150, 25)
        self.check.text = "启用选项"
        panel.add_child(self.check)

        # 进度条
        self.progress = SuiProgressBar()
        self.progress.set_bounds(20, 180, 300, 20)
        self.progress.value = 50
        panel.add_child(self.progress)

        # 状态标签
        self.status = SuiLabel()
        self.status.set_bounds(20, 230, 540, 30)
        self.status.back_color = make_color(230, 230, 230)
        self.status.text_align = 'center'
        self.status.text = "准备就绪"
        panel.add_child(self.status)

    def on_submit(self, sender):
        text = self.edit.text
        checked = "已选中" if self.check.checked else "未选中"
        self.status.text = f"输入: {text}, 选项: {checked}"
        self.progress.value = min(100, self.progress.value + 10)

def main():
    pyserui.initialize()
    try:
        window = DemoWindow()
        window.create(title="PySerUI Demo", width=600, height=400)
        pyserui.run_application(window)
    finally:
        pyserui.shutdown()

if __name__ == "__main__":
    main()
```

## API 文档

### 核心类

#### SuiWindow
- `create(title, x, y, width, height, style, ex_style)` - 创建窗口
- `show(cmd_show)` - 显示窗口
- `hide()` - 隐藏窗口
- `close()` - 关闭窗口
- `add_child(child)` - 添加子控件
- `remove_child(child)` - 移除子控件
- `invalidate(rect, erase)` - 触发重绘

#### SuiControl (所有控件基类)
- `set_bounds(x, y, width, height)` - 设置位置和大小
- `set_location(x, y)` - 设置位置
- `set_size(width, height)` - 设置大小
- 属性: `left`, `top`, `width`, `height`, `visible`, `enabled`
- 样式属性: `back_color`, `fore_color`, `border_color`, `border_width`

### 事件

所有控件支持以下事件：
- `on_paint(hdc, rect)` - 绘制事件
- `on_click(x, y, button)` - 点击事件
- `on_mouse_down(x, y, button)` - 鼠标按下
- `on_mouse_up(x, y, button)` - 鼠标释放
- `on_mouse_move(x, y)` - 鼠标移动
- `on_mouse_enter()` - 鼠标进入
- `on_mouse_leave()` - 鼠标离开
- `on_key_down(key_code)` - 按键按下
- `on_key_up(key_code)` - 按键释放

## 项目结构

```
pyserui/
├── __init__.py      # 包入口，导出主要类和函数
├── core.py          # 核心模块：窗口、消息循环、基础类
├── controls.py      # 控件实现
└── gdiplus.py       # GDI+ 图形封装
```

## 依赖

- `pywin32>=227` - Windows API 访问

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 致谢

- 原作者：Baby (Syser Group)
- 原项目：SyserUI Engine (2008-2012)
- Python 重写版本

## 相关项目

- [SyserUI Engine](https://github.com/wizardforcel/syser-ui-engine) - 原始易语言版本
