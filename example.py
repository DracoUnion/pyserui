# -*- coding: utf-8 -*-
"""
PySerUI - 示例程序
演示如何使用 PySerUI 创建 DirectUI 界面
"""

import pyserui
from pyserui import (
    SuiWindow, SuiPanel, SuiLabel, SuiButton, SuiEdit,
    SuiCheckBox, SuiRadioButton, SuiProgressBar,
    get_application, message_box, make_color, Colors
)
import win32con


class MainWindow(SuiWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.title = "SyserUI Engine - Python Demo"
        self.width = 800
        self.height = 600

        # 创建面板作为容器
        self.panel = SuiPanel()
        self.panel.set_bounds(10, 10, 780, 580)
        self.panel.back_color = make_color(245, 245, 245)
        self.add_child(self.panel)

        # 创建标题标签
        self.title_label = SuiLabel()
        self.title_label.set_bounds(20, 20, 740, 40)
        self.title_label.text = "PySerUI - Python DirectUI Framework"
        self.title_label.font_size = 16
        self.title_label.font_bold = True
        self.title_label.text_align = 'center'
        self.panel.add_child(self.title_label)

        # 创建说明标签
        self.desc_label = SuiLabel()
        self.desc_label.set_bounds(20, 70, 740, 30)
        self.desc_label.text = "PySerUI - Python DirectUI Framework Demo"
        self.desc_label.text_align = 'center'
        self.panel.add_child(self.desc_label)

        # 创建按钮区域标签
        self.button_label = SuiLabel()
        self.button_label.set_bounds(20, 120, 200, 25)
        self.button_label.text = "按钮控件:"
        self.button_label.font_bold = True
        self.panel.add_child(self.button_label)

        # 创建普通按钮
        self.normal_btn = SuiButton()
        self.normal_btn.set_bounds(20, 150, 120, 35)
        self.normal_btn.text = "普通按钮"
        self.normal_btn.on_click += self.on_normal_button_click
        self.panel.add_child(self.normal_btn)

        # 创建带样式的按钮
        self.style_btn = SuiButton()
        self.style_btn.set_bounds(150, 150, 120, 35)
        self.style_btn.text = "彩色按钮"
        self.style_btn.back_color = make_color(100, 180, 255)
        self.style_btn.fore_color = Colors.White
        self.style_btn.on_click += self.on_style_button_click
        self.panel.add_child(self.style_btn)

        # 创建复选框
        self.checkbox_label = SuiLabel()
        self.checkbox_label.set_bounds(20, 200, 200, 25)
        self.checkbox_label.text = "复选框:"
        self.checkbox_label.font_bold = True
        self.panel.add_child(self.checkbox_label)

        self.check1 = SuiCheckBox()
        self.check1.set_bounds(20, 230, 150, 25)
        self.check1.text = "选项 1"
        self.panel.add_child(self.check1)

        self.check2 = SuiCheckBox()
        self.check2.set_bounds(180, 230, 150, 25)
        self.check2.text = "选项 2"
        self.panel.add_child(self.check2)

        # 创建单选按钮
        self.radio_label = SuiLabel()
        self.radio_label.set_bounds(20, 270, 200, 25)
        self.radio_label.text = "单选按钮:"
        self.radio_label.font_bold = True
        self.panel.add_child(self.radio_label)

        self.radio1 = SuiRadioButton()
        self.radio1.set_bounds(20, 300, 100, 25)
        self.radio1.text = "是"
        self.radio1.checked = True
        self.panel.add_child(self.radio1)

        self.radio2 = SuiRadioButton()
        self.radio2.set_bounds(130, 300, 100, 25)
        self.radio2.text = "否"
        self.panel.add_child(self.radio2)

        # 创建输入框
        self.edit_label = SuiLabel()
        self.edit_label.set_bounds(20, 350, 200, 25)
        self.edit_label.text = "输入框:"
        self.edit_label.font_bold = True
        self.panel.add_child(self.edit_label)

        self.edit = SuiEdit()
        self.edit.set_bounds(20, 380, 300, 30)
        self.edit.text = "在这里输入文本..."
        self.panel.add_child(self.edit)

        # 创建进度条
        self.progress_label = SuiLabel()
        self.progress_label.set_bounds(20, 430, 200, 25)
        self.progress_label.text = "进度条:"
        self.progress_label.font_bold = True
        self.panel.add_child(self.progress_label)

        self.progress = SuiProgressBar()
        self.progress.set_bounds(20, 460, 400, 25)
        self.progress.value = 65
        self.panel.add_child(self.progress)

        # 创建增加/减少进度的按钮
        self.dec_btn = SuiButton()
        self.dec_btn.set_bounds(430, 460, 40, 25)
        self.dec_btn.text = "-"
        self.dec_btn.on_click += self.on_decrease_progress
        self.panel.add_child(self.dec_btn)

        self.inc_btn = SuiButton()
        self.inc_btn.set_bounds(480, 460, 40, 25)
        self.inc_btn.text = "+"
        self.inc_btn.on_click += self.on_increase_progress
        self.panel.add_child(self.inc_btn)

        # 创建状态标签
        self.status_label = SuiLabel()
        self.status_label.set_bounds(20, 520, 760, 30)
        self.status_label.text = "就绪 - 点击按钮测试功能"
        self.status_label.back_color = make_color(230, 230, 230)
        self.status_label.text_align = 'center'
        self.panel.add_child(self.status_label)

        # 设置事件处理
        self.on_paint += self.on_window_paint

    def on_window_paint(self, hdc, rect):
        """窗口绘制事件"""
        # 可以在这里进行自定义绘制
        pass

    def on_normal_button_click(self, sender):
        """普通按钮点击"""
        self.status_label.text = "普通按钮被点击了！"
        message_box("你好！这是 PySerUI 的示例消息框。", "提示")

    def on_style_button_click(self, sender):
        """样式按钮点击"""
        self.status_label.text = "彩色按钮被点击了！"

    def on_increase_progress(self, sender):
        """增加进度"""
        new_value = min(100, self.progress.value + 10)
        self.progress.value = new_value
        self.status_label.text = f"进度增加到: {new_value}%"

    def on_decrease_progress(self, sender):
        """减少进度"""
        new_value = max(0, self.progress.value - 10)
        self.progress.value = new_value
        self.status_label.text = f"进度减少到: {new_value}%"


def main():
    """主函数"""
    # 初始化 PySerUI 引擎
    pyserui.initialize()

    try:
        # 创建主窗口
        window = MainWindow()
        window.create(
            title="PySerUI - Python Demo",
            width=800,
            height=600,
            style=win32con.WS_OVERLAPPEDWINDOW & ~win32con.WS_THICKFRAME
        )

        # 运行应用程序
        pyserui.run_application(window)

    finally:
        # 关闭 PySerUI 引擎
        pyserui.shutdown()


if __name__ == "__main__":
    main()
