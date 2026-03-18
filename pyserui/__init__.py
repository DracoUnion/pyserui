# -*- coding: utf-8 -*-
"""
PySerUI - Python DirectUI Framework

一个 DirectUI 引擎的 Python 实现
基于 pywin32 库，仅支持 Windows 平台

特性:
- DirectUI 架构，无原生控件句柄
- GDI+ 图形加速
- 丰富的控件库
- 灵活的布局系统
- 自定义绘制支持

原项目: SyserUI Engine (易语言版本)
作者: Baby (Syser Group)
Copyright: 2008-2012
Python 重写版本
"""

__version__ = "1.0.0"
__author__ = "Baby (Syser Group) -> Python rewrite"

# 导入核心模块
from .core import (
    SuiWindow, SuiApplication, SuiObject,
    SuiRect, SuiPoint, SuiSize, SuiMessage, SuiDelegate,
    get_application, message_box,
    WM_SUI_BASE, WM_SUI_NOTIFY, WM_SUI_PAINT, WM_SUI_LAYOUT,
    TIMER_BASE
)

# 导入 GDI+ 模块
from .gdiplus import (
    GdiplusGraphics, GdiplusPen, GdiplusSolidBrush,
    GdiplusHatchBrush, GdiplusLinearGradientBrush,
    GdiplusFont, GdiplusStringFormat, GdiplusImage,
    ARGB, Rect, RectF, Point, PointF, Size,
    make_color, make_color_ref, Colors,
    SmoothingMode, InterpolationMode, CompositingQuality,
    TextRenderingHint, HatchStyle, LinearGradientMode,
    WrapMode, StringAlignment, StringFormatFlags,
    gdiplus_startup, gdiplus_shutdown
)

# 导入控件模块
from .controls import (
    SuiControl, SuiLabel, SuiButton, SuiEdit,
    SuiPanel, SuiProgressBar, SuiCheckBox, SuiRadioButton
)

# 便捷函数
def create_window(title="SuiWindow", width=800, height=600):
    """
    快速创建窗口

    参数:
        title: 窗口标题
        width: 窗口宽度
        height: 窗口高度

    返回:
        SuiWindow 实例
    """
    window = SuiWindow()
    window.create(title=title, width=width, height=height)
    return window


def run_application(window=None):
    """
    运行应用程序消息循环

    参数:
        window: 主窗口，如果提供会自动显示
    """
    app = get_application()

    if window:
        app.set_main_window(window)
        window.show()

    return app.run()


# 初始化 GDI+ 标记
_gdiplus_initialized = False
_gdiplus_token = None


def initialize():
    """
    初始化 PySerUI 引擎
    在使用任何 GDI+ 功能之前调用
    """
    global _gdiplus_initialized, _gdiplus_token

    if not _gdiplus_initialized:
        _gdiplus_token = gdiplus_startup()
        _gdiplus_initialized = True


def shutdown():
    """
    关闭 PySerUI 引擎
    在程序退出前调用以清理资源
    """
    global _gdiplus_initialized, _gdiplus_token

    if _gdiplus_initialized and _gdiplus_token:
        gdiplus_shutdown(_gdiplus_token)
        _gdiplus_initialized = False
        _gdiplus_token = None
