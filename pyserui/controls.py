# -*- coding: utf-8 -*-
"""
PySerUI - 控件模块
常用 UI 控件实现
"""

import win32gui
import win32con
import win32api
from win32api import RGB

from .core import SuiWindow, SuiRect, SuiPoint, SuiMessage
from .gdiplus import (
    GdiplusGraphics, GdiplusPen, GdiplusSolidBrush, GdiplusFont,
    GdiplusStringFormat, GdiplusHatchBrush, GdiplusLinearGradientBrush,
    ARGB, Rect, Point, RectF, PointF,
    SmoothingMode, TextRenderingHint, StringAlignment,
    HatchStyle, LinearGradientMode, Colors, make_color
)


class SuiControl(SuiWindow):
    """
    SUI 控件基类
    所有控件的基类
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 控件属性
        self._auto_size = False
        self._dock = None  # None, 'left', 'right', 'top', 'bottom', 'fill'
        self._anchor = ('left', 'top')  # 锚定边

        # 边距
        self._margin = (0, 0, 0, 0)  # 左、上、右、下
        self._padding = (0, 0, 0, 0)  # 内边距

        # 外观
        self._fore_color = Colors.Black
        self._back_color = None
        self._border_color = None
        self._border_width = 0

        # 字体
        self._font = None
        self._font_name = "微软雅黑"
        self._font_size = 9
        self._font_bold = False
        self._font_italic = False

        # 提示文本
        self._tooltip = ""

    def _get_font(self):
        """获取字体，延迟创建"""
        if self._font is None:
            style = 0
            if self._font_bold:
                style |= 1
            if self._font_italic:
                style |= 2
            self._font = GdiplusFont(self._font_name, self._font_size, style)
        return self._font

    def _draw(self, hdc):
        """绘制控件"""
        # 创建 GDI+ 图形对象
        graphics = GdiplusGraphics(hdc)
        graphics.set_smoothing_mode(SmoothingMode.SmoothingModeAntiAlias)
        graphics.set_text_rendering_hint(TextRenderingHint.TextRenderingHintClearTypeGridFit)

        # 绘制背景
        self._draw_background(graphics)

        # 绘制边框
        self._draw_border(graphics)

        # 绘制内容
        self._draw_content(graphics)

        # 清理
        graphics.dispose()

    def _draw_background(self, graphics):
        """绘制背景"""
        if self._back_color:
            brush = GdiplusSolidBrush(self._back_color)
            graphics.fill_rectangle(brush, 0, 0, self._rect.width, self._rect.height)
            brush.dispose()

    def _draw_border(self, graphics):
        """绘制边框"""
        if self._border_width > 0 and self._border_color:
            pen = GdiplusPen(self._border_color, self._border_width)
            # 考虑画笔宽度，调整绘制位置
            offset = self._border_width / 2
            w = self._rect.width - self._border_width
            h = self._rect.height - self._border_width
            graphics.draw_rectangle(pen, int(offset), int(offset), int(w), int(h))
            pen.dispose()

    def _draw_content(self, graphics):
        """绘制内容 - 子类重写"""
        pass

    def _do_layout(self):
        """执行布局"""
        if self._parent:
            parent_rect = self._parent.get_client_rect()

            if self._dock == 'left':
                self._rect.height = parent_rect.height
            elif self._dock == 'right':
                self._rect.height = parent_rect.height
            elif self._dock == 'top':
                self._rect.width = parent_rect.width
            elif self._dock == 'bottom':
                self._rect.width = parent_rect.width
            elif self._dock == 'fill':
                self._rect = parent_rect.copy()

    def set_bounds(self, x, y, width, height):
        """设置位置和大小"""
        self._rect.x = x
        self._rect.y = y
        self._rect.width = width
        self._rect.height = height
        if self._hwnd:
            self.set_rect(x, y, width, height)

    def set_location(self, x, y):
        """设置位置"""
        self.set_bounds(x, y, self._rect.width, self._rect.height)

    def set_size(self, width, height):
        """设置大小"""
        self.set_bounds(self._rect.x, self._rect.y, width, height)

    @property
    def left(self):
        return self._rect.x

    @left.setter
    def left(self, value):
        self.set_location(value, self._rect.y)

    @property
    def top(self):
        return self._rect.y

    @top.setter
    def top(self, value):
        self.set_location(self._rect.x, value)

    @property
    def width(self):
        return self._rect.width

    @width.setter
    def width(self, value):
        self.set_size(value, self._rect.height)

    @property
    def height(self):
        return self._rect.height

    @height.setter
    def height(self, value):
        self.set_size(self._rect.width, value)

    @property
    def dock(self):
        return self._dock

    @dock.setter
    def dock(self, value):
        self._dock = value
        if self._parent:
            self._parent._on_layout()

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, value):
        if len(value) == 4:
            self._margin = value

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value):
        if len(value) == 4:
            self._padding = value

    @property
    def fore_color(self):
        return self._fore_color

    @fore_color.setter
    def fore_color(self, value):
        self._fore_color = value
        self.invalidate()

    @property
    def back_color(self):
        return self._back_color

    @back_color.setter
    def back_color(self, value):
        self._back_color = value
        self.invalidate()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, value):
        self._border_color = value
        self.invalidate()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        self._border_width = value
        self.invalidate()

    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value):
        self._tooltip = value


class SuiLabel(SuiControl):
    """
    标签控件
    显示静态文本
    """

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self._text = text
        self._text_align = 'left'  # left, center, right
        self._valign = 'center'  # top, center, bottom
        self._auto_wrap = False
        self._transparent = True

    def _draw_content(self, graphics):
        """绘制文本"""
        if not self._text:
            return

        # 计算文本区域（考虑内边距）
        left, top, right, bottom = self._padding
        rect = RectF(left, top,
                     self._rect.width - left - right,
                     self._rect.height - top - bottom)

        # 创建画刷和格式
        brush = GdiplusSolidBrush(self._fore_color)
        format = GdiplusStringFormat()

        # 设置对齐方式
        if self._text_align == 'left':
            format.set_alignment(StringAlignment.StringAlignmentNear)
        elif self._text_align == 'center':
            format.set_alignment(StringAlignment.StringAlignmentCenter)
        elif self._text_align == 'right':
            format.set_alignment(StringAlignment.StringAlignmentFar)

        if self._valign == 'top':
            format.set_line_alignment(StringAlignment.StringAlignmentNear)
        elif self._valign == 'center':
            format.set_line_alignment(StringAlignment.StringAlignmentCenter)
        elif self._valign == 'bottom':
            format.set_line_alignment(StringAlignment.StringAlignmentFar)

        # 绘制文本
        font = self._get_font()
        graphics.draw_string(self._text, font, rect, format, brush)

        # 清理
        brush.dispose()
        format.dispose()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self.invalidate()

    @property
    def text_align(self):
        return self._text_align

    @text_align.setter
    def text_align(self, value):
        self._text_align = value
        self.invalidate()


class SuiButton(SuiControl):
    """
    按钮控件
    可点击的按钮
    """

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self._text = text
        self._pressed = False
        self._hovered = False
        self._checked = False
        self._checkable = False

        # 默认外观
        self._back_color = make_color(240, 240, 240)
        self._hover_color = make_color(230, 240, 250)
        self._pressed_color = make_color(200, 220, 240)
        self._border_color = make_color(180, 180, 180)
        self._border_width = 1

        # 事件
        self.on_click = self.on_click  # 重命名以便更清晰

    def _on_mouse_down(self, message, button):
        """鼠标按下"""
        super()._on_mouse_down(message, button)
        if button == 1:  # 左键
            self._pressed = True
            self.invalidate()

    def _on_mouse_up(self, message, button):
        """鼠标释放"""
        was_pressed = self._pressed
        super()._on_mouse_up(message, button)
        self._pressed = False

        if was_pressed and button == 1:
            if self._checkable:
                self._checked = not self._checked
            self.on_click(self)
            self.invalidate()

    def _on_mouse_enter(self):
        """鼠标进入"""
        super()._on_mouse_enter()
        self._hovered = True
        self.invalidate()

    def _on_mouse_leave(self):
        """鼠标离开"""
        super()._on_mouse_leave()
        self._hovered = False
        self._pressed = False
        self.invalidate()

    def _draw_background(self, graphics):
        """绘制按钮背景"""
        color = self._back_color

        if self._pressed:
            color = self._pressed_color
        elif self._hovered:
            color = self._hover_color

        if self._checked:
            color = self._pressed_color

        brush = GdiplusSolidBrush(color)
        graphics.fill_rectangle(brush, 0, 0, self._rect.width, self._rect.height)
        brush.dispose()

    def _draw_content(self, graphics):
        """绘制按钮文本"""
        if not self._text:
            return

        # 考虑按下状态的偏移
        offset_x = 1 if self._pressed else 0
        offset_y = 1 if self._pressed else 0

        left, top, right, bottom = self._padding
        rect = RectF(left + offset_x, top + offset_y,
                     self._rect.width - left - right,
                     self._rect.height - top - bottom)

        brush = GdiplusSolidBrush(self._fore_color)
        format = GdiplusStringFormat()
        format.set_alignment(StringAlignment.StringAlignmentCenter)
        format.set_line_alignment(StringAlignment.StringAlignmentCenter)

        font = self._get_font()
        graphics.draw_string(self._text, font, rect, format, brush)

        brush.dispose()
        format.dispose()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self.invalidate()

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        if self._checkable:
            self._checked = value
            self.invalidate()

    @property
    def checkable(self):
        return self._checkable

    @checkable.setter
    def checkable(self, value):
        self._checkable = value


class SuiEdit(SuiControl):
    """
    编辑框控件
    单行文本输入
    """

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self._text = text
        self._password_char = None
        self._max_length = 0
        self._read_only = False
        self._caret_pos = 0
        self._selection_start = 0
        self._selection_length = 0

        # 外观
        self._back_color = Colors.White
        self._border_color = make_color(180, 180, 180)
        self._border_width = 1
        self._padding = (3, 3, 3, 3)

    def _on_char(self, message):
        """字符输入"""
        if self._read_only:
            return

        char = chr(message.key_code)

        if char == '\b':  # 退格
            if self._selection_length > 0:
                self._delete_selection()
            elif self._caret_pos > 0:
                self._text = self._text[:self._caret_pos - 1] + self._text[self._caret_pos:]
                self._caret_pos -= 1
        elif char == '\r':  # 回车
            pass  # 单行编辑框忽略回车
        elif char.isprintable():
            if self._max_length == 0 or len(self._text) < self._max_length:
                if self._selection_length > 0:
                    self._delete_selection()
                self._text = self._text[:self._caret_pos] + char + self._text[self._caret_pos:]
                self._caret_pos += 1

        self.invalidate()

    def _on_key_down(self, message):
        """按键处理"""
        key = message.key_code

        if key == win32con.VK_LEFT:
            if self._caret_pos > 0:
                self._caret_pos -= 1
                self.invalidate()
        elif key == win32con.VK_RIGHT:
            if self._caret_pos < len(self._text):
                self._caret_pos += 1
                self.invalidate()
        elif key == win32con.VK_HOME:
            self._caret_pos = 0
            self.invalidate()
        elif key == win32con.VK_END:
            self._caret_pos = len(self._text)
            self.invalidate()
        elif key == win32con.VK_DELETE:
            if self._selection_length > 0:
                self._delete_selection()
            elif self._caret_pos < len(self._text):
                self._text = self._text[:self._caret_pos] + self._text[self._caret_pos + 1:]
            self.invalidate()

    def _delete_selection(self):
        """删除选中文本"""
        start = self._selection_start
        end = start + self._selection_length
        self._text = self._text[:start] + self._text[end:]
        self._caret_pos = start
        self._selection_start = 0
        self._selection_length = 0

    def _draw_content(self, graphics):
        """绘制文本和光标"""
        left, top, right, bottom = self._padding
        rect = RectF(left, top,
                     self._rect.width - left - right,
                     self._rect.height - top - bottom)

        # 绘制文本
        display_text = self._text
        if self._password_char:
            display_text = self._password_char * len(self._text)

        if display_text:
            brush = GdiplusSolidBrush(self._fore_color)
            format = GdiplusStringFormat()
            format.set_line_alignment(StringAlignment.StringAlignmentCenter)

            font = self._get_font()
            graphics.draw_string(display_text, font, rect, format, brush)

            brush.dispose()
            format.dispose()

        # 绘制光标
        if self._focused:
            # 计算光标位置
            if display_text:
                # 测量光标前的文本宽度
                sub_text = display_text[:self._caret_pos]
                bounds = graphics.measure_string(sub_text, self._get_font(), rect, format)
                caret_x = int(rect.X + bounds.Width)
            else:
                caret_x = int(rect.X)

            caret_y = int(rect.Y)
            caret_height = int(self._get_font().get_height())

            pen = GdiplusPen(Colors.Black, 1)
            graphics.draw_line(pen, caret_x, caret_y, caret_x, caret_y + caret_height)
            pen.dispose()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._caret_pos = len(self._text)
        self.invalidate()

    @property
    def password_char(self):
        return self._password_char

    @password_char.setter
    def password_char(self, value):
        self._password_char = value
        self.invalidate()

    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, value):
        self._read_only = value

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        self._max_length = value


class SuiPanel(SuiControl):
    """
    面板控件
    容器控件，用于组织其他控件
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._back_color = make_color(250, 250, 250)

    def add_control(self, control):
        """添加子控件"""
        self.add_child(control)

    def remove_control(self, control):
        """移除子控件"""
        self.remove_child(control)


class SuiProgressBar(SuiControl):
    """
    进度条控件
    显示进度
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._minimum = 0
        self._maximum = 100
        self._orientation = 'horizontal'  # horizontal, vertical

        # 外观
        self._back_color = make_color(230, 230, 230)
        self._progress_color = make_color(0, 120, 215)
        self._border_color = make_color(180, 180, 180)
        self._border_width = 1

    def _draw_background(self, graphics):
        """绘制背景"""
        super()._draw_background(graphics)

        # 绘制进度
        if self._maximum > self._minimum:
            ratio = (self._value - self._minimum) / (self._maximum - self._minimum)
            ratio = max(0, min(1, ratio))

            brush = GdiplusSolidBrush(self._progress_color)

            if self._orientation == 'horizontal':
                width = int(self._rect.width * ratio)
                graphics.fill_rectangle(brush, 0, 0, width, self._rect.height)
            else:
                height = int(self._rect.height * ratio)
                y = self._rect.height - height
                graphics.fill_rectangle(brush, 0, y, self._rect.width, height)

            brush.dispose()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = max(self._minimum, min(self._maximum, val))
        self.invalidate()

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, val):
        self._minimum = val
        if self._value < val:
            self._value = val
        self.invalidate()

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, val):
        self._maximum = val
        if self._value > val:
            self._value = val
        self.invalidate()


class SuiCheckBox(SuiControl):
    """
    复选框控件
    """

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self._text = text
        self._checked = False
        self._box_size = 16

        # 外观
        self._check_color = make_color(0, 120, 215)
        self._border_color = make_color(100, 100, 100)

    def _on_mouse_up(self, message, button):
        """鼠标释放"""
        super()._on_mouse_up(message, button)
        if button == 1:
            # 检查是否点击在复选框上
            if self._rect.contains(message.mouse_x, message.mouse_y):
                self._checked = not self._checked
                self.invalidate()

    def _draw_content(self, graphics):
        """绘制复选框"""
        # 绘制复选框
        box_x = self._padding[0]
        box_y = (self._rect.height - self._box_size) // 2

        # 复选框背景
        brush = GdiplusSolidBrush(Colors.White)
        graphics.fill_rectangle(brush, box_x, box_y, self._box_size, self._box_size)
        brush.dispose()

        # 复选框边框
        pen = GdiplusPen(self._border_color, 1)
        graphics.draw_rectangle(pen, box_x, box_y, self._box_size - 1, self._box_size - 1)
        pen.dispose()

        # 绘制勾选标记
        if self._checked:
            check_padding = 3
            brush = GdiplusSolidBrush(self._check_color)
            graphics.fill_rectangle(
                brush,
                box_x + check_padding,
                box_y + check_padding,
                self._box_size - check_padding * 2,
                self._box_size - check_padding * 2
            )
            brush.dispose()

        # 绘制文本
        if self._text:
            text_x = box_x + self._box_size + 5
            text_y = self._padding[1]
            rect = RectF(text_x, text_y,
                         self._rect.width - text_x - self._padding[2],
                         self._rect.height - self._padding[1] - self._padding[3])

            brush = GdiplusSolidBrush(self._fore_color)
            format = GdiplusStringFormat()
            format.set_line_alignment(StringAlignment.StringAlignmentCenter)

            font = self._get_font()
            graphics.draw_string(self._text, font, rect, format, brush)

            brush.dispose()
            format.dispose()

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self.invalidate()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self.invalidate()


class SuiRadioButton(SuiControl):
    """
    单选按钮控件
    """

    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self._text = text
        self._checked = False
        self._group_name = "default"
        self._circle_size = 16

        # 外观
        self._check_color = make_color(0, 120, 215)
        self._border_color = make_color(100, 100, 100)

    def _on_mouse_up(self, message, button):
        """鼠标释放"""
        super()._on_mouse_up(message, button)
        if button == 1:
            if self._rect.contains(message.mouse_x, message.mouse_y):
                self._check_group()

    def _check_group(self):
        """检查组内其他单选按钮"""
        if self._parent:
            for child in self._parent._children:
                if isinstance(child, SuiRadioButton) and child != self:
                    if child._group_name == self._group_name:
                        child._checked = False
                        child.invalidate()

        self._checked = True
        self.invalidate()

    def _draw_content(self, graphics):
        """绘制单选按钮"""
        # 绘制圆圈
        circle_x = self._padding[0]
        circle_y = (self._rect.height - self._circle_size) // 2

        # 圆圈背景
        brush = GdiplusSolidBrush(Colors.White)
        graphics.fill_ellipse(brush, circle_x, circle_y, self._circle_size, self._circle_size)
        brush.dispose()

        # 圆圈边框
        pen = GdiplusPen(self._border_color, 1)
        graphics.draw_ellipse(pen, circle_x, circle_y, self._circle_size - 1, self._circle_size - 1)
        pen.dispose()

        # 绘制选中点
        if self._checked:
            dot_padding = 4
            brush = GdiplusSolidBrush(self._check_color)
            graphics.fill_ellipse(
                brush,
                circle_x + dot_padding,
                circle_y + dot_padding,
                self._circle_size - dot_padding * 2,
                self._circle_size - dot_padding * 2
            )
            brush.dispose()

        # 绘制文本
        if self._text:
            text_x = circle_x + self._circle_size + 5
            text_y = self._padding[1]
            rect = RectF(text_x, text_y,
                         self._rect.width - text_x - self._padding[2],
                         self._rect.height - self._padding[1] - self._padding[3])

            brush = GdiplusSolidBrush(self._fore_color)
            format = GdiplusStringFormat()
            format.set_line_alignment(StringAlignment.StringAlignmentCenter)

            font = self._get_font()
            graphics.draw_string(self._text, font, rect, format, brush)

            brush.dispose()
            format.dispose()

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        if value and not self._checked:
            self._check_group()
        else:
            self._checked = value
            self.invalidate()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self.invalidate()

    @property
    def group_name(self):
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        self._group_name = value
