# -*- coding: utf-8 -*-
"""
PySerUI - GDI+ 封装模块
基于 pywin32 的 GDI+ 图形库封装
"""

import ctypes
from ctypes import wintypes
from ctypes import POINTER, c_void_p, c_float, c_int, c_uint, c_ulong
import win32gui
import win32con
from win32api import RGB

# 加载 GDI+ 库
try:
    gdiplus = ctypes.windll.gdiplus
except AttributeError:
    raise ImportError("无法加载 GDI+ 库 (gdiplus.dll)")

# GDI+ 常量定义
class GpStatus:
    """GDI+ 状态码"""
    Ok = 0
    GenericError = 1
    InvalidParameter = 2
    OutOfMemory = 3
    ObjectBusy = 4
    InsufficientBuffer = 5
    NotImplemented = 6
    Win32Error = 7
    WrongState = 8
    Aborted = 9
    FileNotFound = 10
    ValueOverflow = 11
    AccessDenied = 12
    UnknownImageFormat = 13
    FontFamilyNotFound = 14
    FontStyleNotFound = 15
    NotTrueTypeFont = 16
    UnsupportedGdiplusVersion = 17
    GdiplusNotInitialized = 18
    PropertyNotFound = 19
    PropertyNotSupported = 20

class Unit:
    """度量单位"""
    UnitWorld = 0
    UnitDisplay = 1
    UnitPixel = 2
    UnitPoint = 3
    UnitInch = 4
    UnitDocument = 5
    UnitMillimeter = 6

class SmoothingMode:
    """平滑模式"""
    SmoothingModeInvalid = -1
    SmoothingModeDefault = 0
    SmoothingModeHighSpeed = 1
    SmoothingModeHighQuality = 2
    SmoothingModeNone = 3
    SmoothingModeAntiAlias = 4

class InterpolationMode:
    """插值模式"""
    InterpolationModeInvalid = -1
    InterpolationModeDefault = 0
    InterpolationModeLowQuality = 1
    InterpolationModeHighQuality = 2
    InterpolationModeBilinear = 3
    InterpolationModeBicubic = 4
    InterpolationModeNearestNeighbor = 5
    InterpolationModeHighQualityBilinear = 6
    InterpolationModeHighQualityBicubic = 7

class CompositingQuality:
    """合成质量"""
    CompositingQualityInvalid = -1
    CompositingQualityDefault = 0
    CompositingQualityHighSpeed = 1
    CompositingQualityHighQuality = 2
    CompositingQualityGammaCorrected = 3
    CompositingQualityAssumeLinear = 4

class TextRenderingHint:
    """文本渲染模式"""
    TextRenderingHintSystemDefault = 0
    TextRenderingHintSingleBitPerPixelGridFit = 1
    TextRenderingHintSingleBitPerPixel = 2
    TextRenderingHintAntiAliasGridFit = 3
    TextRenderingHintAntiAlias = 4
    TextRenderingHintClearTypeGridFit = 5

class HatchStyle:
    """填充图案样式"""
    HatchStyleHorizontal = 0
    HatchStyleVertical = 1
    HatchStyleForwardDiagonal = 2
    HatchStyleBackwardDiagonal = 3
    HatchStyleCross = 4
    HatchStyleDiagonalCross = 5
    HatchStyle05Percent = 6
    HatchStyle10Percent = 7
    HatchStyle20Percent = 8
    HatchStyle25Percent = 9
    HatchStyle30Percent = 10
    HatchStyle40Percent = 11
    HatchStyle50Percent = 12
    HatchStyle60Percent = 13
    HatchStyle70Percent = 14
    HatchStyle75Percent = 15
    HatchStyle80Percent = 16
    HatchStyle90Percent = 17

class LinearGradientMode:
    """线性渐变模式"""
    LinearGradientModeHorizontal = 0
    LinearGradientModeVertical = 1
    LinearGradientModeForwardDiagonal = 2
    LinearGradientModeBackwardDiagonal = 3

class WrapMode:
    """纹理平铺模式"""
    WrapModeTile = 0
    WrapModeTileFlipX = 1
    WrapModeTileFlipY = 2
    WrapModeTileFlipXY = 3
    WrapModeClamp = 4

class StringAlignment:
    """字符串对齐方式"""
    StringAlignmentNear = 0
    StringAlignmentCenter = 1
    StringAlignmentFar = 2

class StringFormatFlags:
    """字符串格式化标志"""
    StringFormatFlagsDirectionRightToLeft = 0x00000001
    StringFormatFlagsDirectionVertical = 0x00000002
    StringFormatFlagsNoFitBlackBox = 0x00000004
    StringFormatFlagsDisplayFormatControl = 0x00000020
    StringFormatFlagsNoFontFallback = 0x00000400
    StringFormatFlagsMeasureTrailingSpaces = 0x00000800
    StringFormatFlagsNoWrap = 0x00001000
    StringFormatFlagsLineLimit = 0x00002000
    StringFormatFlagsNoClip = 0x00004000

# GDI+ 初始化结构体
class GdiplusStartupInput(ctypes.Structure):
    """GDI+ 启动输入参数"""
    _fields_ = [
        ("GdiplusVersion", c_uint),
        ("DebugEventCallback", c_void_p),
        ("SuppressBackgroundThread", c_int),
        ("SuppressExternalCodecs", c_int)
    ]

class GdiplusStartupOutput(ctypes.Structure):
    """GDI+ 启动输出参数"""
    _fields_ = [
        ("NotificationHook", c_void_p),
        ("NotificationUnhook", c_void_p)
    ]

# GDI+ 颜色结构
class ARGB(ctypes.Structure):
    """ARGB 颜色结构"""
    _fields_ = [
        ("Blue", ctypes.c_ubyte),
        ("Green", ctypes.c_ubyte),
        ("Red", ctypes.c_ubyte),
        ("Alpha", ctypes.c_ubyte)
    ]

    def __init__(self, a=255, r=0, g=0, b=0):
        super().__init__()
        self.Alpha = a
        self.Red = r
        self.Green = g
        self.Blue = b

    @staticmethod
    def from_colorref(colorref):
        """从 COLORREF 创建 ARGB"""
        r = colorref & 0xFF
        g = (colorref >> 8) & 0xFF
        b = (colorref >> 16) & 0xFF
        return ARGB(255, r, g, b)

    @staticmethod
    def from_rgb(r, g, b, a=255):
        """从 RGB 创建 ARGB"""
        return ARGB(a, r, g, b)

# GDI+ Rect 结构
class Rect(ctypes.Structure):
    """整数矩形"""
    _fields_ = [
        ("X", c_int),
        ("Y", c_int),
        ("Width", c_int),
        ("Height", c_int)
    ]

    def __init__(self, x=0, y=0, width=0, height=0):
        super().__init__()
        self.X = x
        self.Y = y
        self.Width = width
        self.Height = height

class RectF(ctypes.Structure):
    """浮点数矩形"""
    _fields_ = [
        ("X", c_float),
        ("Y", c_float),
        ("Width", c_float),
        ("Height", c_float)
    ]

    def __init__(self, x=0.0, y=0.0, width=0.0, height=0.0):
        super().__init__()
        self.X = x
        self.Y = y
        self.Width = width
        self.Height = height

class Point(ctypes.Structure):
    """整数点"""
    _fields_ = [("X", c_int), ("Y", c_int)]

    def __init__(self, x=0, y=0):
        super().__init__()
        self.X = x
        self.Y = y

class PointF(ctypes.Structure):
    """浮点数点"""
    _fields_ = [("X", c_float), ("Y", c_float)]

    def __init__(self, x=0.0, y=0.0):
        super().__init__()
        self.X = x
        self.Y = y

class Size(ctypes.Structure):
    """整数大小"""
    _fields_ = [("Width", c_int), ("Height", c_int)]

    def __init__(self, width=0, height=0):
        super().__init__()
        self.Width = width
        self.Height = height

# GDI+ 封装类
class GdiplusGraphics:
    """
    GDI+ Graphics 封装类
    封装 GDI+ 的绘图功能
    """

    def __init__(self, hdc):
        """
        从设备上下文创建 Graphics 对象
        :param hdc: 设备上下文句柄
        """
        self.graphics = c_void_p()
        self._hdc = hdc
        # GdipCreateFromHDC 创建 Graphics 对象
        status = gdiplus.GdipCreateFromHDC(hdc, ctypes.byref(self.graphics))
        if status != GpStatus.Ok:
            raise Exception(f"创建 Graphics 失败，状态码: {status}")

    def __del__(self):
        """析构函数，释放资源"""
        self.dispose()

    def dispose(self):
        """释放 Graphics 对象"""
        if self.graphics:
            gdiplus.GdipDeleteGraphics(self.graphics)
            self.graphics = None

    def set_smoothing_mode(self, mode):
        """设置平滑模式"""
        gdiplus.GdipSetSmoothingMode(self.graphics, mode)

    def set_interpolation_mode(self, mode):
        """设置插值模式"""
        gdiplus.GdipSetInterpolationMode(self.graphics, mode)

    def set_compositing_quality(self, quality):
        """设置合成质量"""
        gdiplus.GdipSetCompositingQuality(self.graphics, quality)

    def set_text_rendering_hint(self, hint):
        """设置文本渲染模式"""
        gdiplus.GdipSetTextRenderingHint(self.graphics, hint)

    def clear(self, color):
        """清空画布"""
        argb = (color.Alpha << 24) | (color.Red << 16) | (color.Green << 8) | color.Blue
        gdiplus.GdipGraphicsClear(self.graphics, argb)

    def draw_line(self, pen, x1, y1, x2, y2):
        """绘制直线"""
        gdiplus.GdipDrawLineI(self.graphics, pen.pen, x1, y1, x2, y2)

    def draw_rectangle(self, pen, x, y, width, height):
        """绘制矩形边框"""
        gdiplus.GdipDrawRectangleI(self.graphics, pen.pen, x, y, width, height)

    def fill_rectangle(self, brush, x, y, width, height):
        """填充矩形"""
        gdiplus.GdipFillRectangleI(self.graphics, brush.brush, x, y, width, height)

    def draw_ellipse(self, pen, x, y, width, height):
        """绘制椭圆边框"""
        gdiplus.GdipDrawEllipseI(self.graphics, pen.pen, x, y, width, height)

    def fill_ellipse(self, brush, x, y, width, height):
        """填充椭圆"""
        gdiplus.GdipFillEllipseI(self.graphics, brush.brush, x, y, width, height)

    def draw_arc(self, pen, x, y, width, height, start_angle, sweep_angle):
        """绘制圆弧"""
        gdiplus.GdipDrawArcI(self.graphics, pen.pen, x, y, width, height,
                             start_angle, sweep_angle)

    def draw_pie(self, pen, x, y, width, height, start_angle, sweep_angle):
        """绘制饼形边框"""
        gdiplus.GdipDrawPieI(self.graphics, pen.pen, x, y, width, height,
                            start_angle, sweep_angle)

    def fill_pie(self, brush, x, y, width, height, start_angle, sweep_angle):
        """填充饼形"""
        gdiplus.GdipFillPieI(self.graphics, brush.brush, x, y, width, height,
                            start_angle, sweep_angle)

    def draw_polygon(self, pen, points):
        """绘制多边形"""
        count = len(points)
        point_array = (Point * count)()
        for i, pt in enumerate(points):
            point_array[i] = pt
        gdiplus.GdipDrawPolygonI(self.graphics, pen.pen, point_array, count)

    def fill_polygon(self, brush, points):
        """填充多边形"""
        count = len(points)
        point_array = (Point * count)()
        for i, pt in enumerate(points):
            point_array[i] = pt
        gdiplus.GdipFillPolygonI(self.graphics, brush.brush, point_array, count, 0)

    def draw_string(self, text, font, layout_rect, format, brush):
        """绘制文本"""
        # 转换文本为宽字符
        wtext = ctypes.create_unicode_buffer(text)
        gdiplus.GdipDrawString(self.graphics, wtext, -1, font.font,
                               ctypes.byref(layout_rect), format.format, brush.brush)

    def measure_string(self, text, font, layout_rect, format):
        """测量文本尺寸"""
        wtext = ctypes.create_unicode_buffer(text)
        bounds = RectF()
        gdiplus.GdipMeasureString(self.graphics, wtext, -1, font.font,
                                  ctypes.byref(layout_rect), format.format,
                                  ctypes.byref(bounds), None, None)
        return bounds

    def draw_image(self, image, x, y, width, height):
        """绘制图像"""
        gdiplus.GdipDrawImageRectI(self.graphics, image.image, x, y, width, height)

    def draw_image_rect(self, image, dst_x, dst_y, dst_width, dst_height,
                        src_x, src_y, src_width, src_height):
        """绘制图像的一部分到指定区域"""
        gdiplus.GdipDrawImageRectRectI(self.graphics, image.image,
                                       dst_x, dst_y, dst_width, dst_height,
                                       src_x, src_y, src_width, src_height,
                                       Unit.UnitPixel, None, None, None)

    def set_clip_rect(self, x, y, width, height):
        """设置裁剪矩形"""
        rect = Rect(x, y, width, height)
        gdiplus.GdipSetClipRectI(self.graphics, x, y, width, height, 0)

    def reset_clip(self):
        """重置裁剪区域"""
        gdiplus.GdipResetClip(self.graphics)

    def translate_transform(self, dx, dy):
        """平移变换"""
        gdiplus.GdipTranslateWorldTransform(self.graphics, dx, dy, 0)

    def rotate_transform(self, angle):
        """旋转变换"""
        gdiplus.GdipRotateWorldTransform(self.graphics, angle, 0)

    def scale_transform(self, sx, sy):
        """缩放变换"""
        gdiplus.GdipScaleWorldTransform(self.graphics, sx, sy, 0)

    def reset_transform(self):
        """重置变换"""
        gdiplus.GdipResetWorldTransform(self.graphics)


class GdiplusPen:
    """GDI+ 画笔封装"""

    def __init__(self, color, width=1.0):
        """
        创建画笔
        :param color: ARGB 颜色
        :param width: 画笔宽度
        """
        self.pen = c_void_p()
        argb = (color.Alpha << 24) | (color.Red << 16) | (color.Green << 8) | color.Blue
        gdiplus.GdipCreatePen1(argb, width, Unit.UnitPixel, ctypes.byref(self.pen))

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放画笔"""
        if self.pen:
            gdiplus.GdipDeletePen(self.pen)
            self.pen = None

    def set_width(self, width):
        """设置画笔宽度"""
        gdiplus.GdipSetPenWidth(self.pen, width)

    def set_color(self, color):
        """设置画笔颜色"""
        argb = (color.Alpha << 24) | (color.Red << 16) | (color.Green << 8) | color.Blue
        gdiplus.GdipSetPenColor(self.pen, argb)


class GdiplusSolidBrush:
    """GDI+ 纯色画刷封装"""

    def __init__(self, color):
        """
        创建纯色画刷
        :param color: ARGB 颜色
        """
        self.brush = c_void_p()
        argb = (color.Alpha << 24) | (color.Red << 16) | (color.Green << 8) | color.Blue
        gdiplus.GdipCreateSolidFill(argb, ctypes.byref(self.brush))

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放画刷"""
        if self.brush:
            gdiplus.GdipDeleteBrush(self.brush)
            self.brush = None

    def set_color(self, color):
        """设置颜色"""
        argb = (color.Alpha << 24) | (color.Red << 16) | (color.Green << 8) | color.Blue
        gdiplus.GdipSetSolidFillColor(self.brush, argb)


class GdiplusHatchBrush:
    """GDI+ 阴影画刷封装"""

    def __init__(self, hatch_style, fore_color, back_color):
        """
        创建阴影画刷
        :param hatch_style: 阴影样式
        :param fore_color: 前景色
        :param back_color: 背景色
        """
        self.brush = c_void_p()
        fore_argb = (fore_color.Alpha << 24) | (fore_color.Red << 16) | \
                    (fore_color.Green << 8) | fore_color.Blue
        back_argb = (back_color.Alpha << 24) | (back_color.Red << 16) | \
                    (back_color.Green << 8) | back_color.Blue
        gdiplus.GdipCreateHatchBrush(hatch_style, fore_argb, back_argb,
                                      ctypes.byref(self.brush))

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放画刷"""
        if self.brush:
            gdiplus.GdipDeleteBrush(self.brush)
            self.brush = None


class GdiplusLinearGradientBrush:
    """GDI+ 线性渐变画刷封装"""

    def __init__(self, rect, color1, color2, mode):
        """
        创建线性渐变画刷
        :param rect: 渐变区域
        :param color1: 起始颜色
        :param color2: 结束颜色
        :param mode: 渐变模式
        """
        self.brush = c_void_p()
        argb1 = (color1.Alpha << 24) | (color1.Red << 16) | \
                (color1.Green << 8) | color1.Blue
        argb2 = (color2.Alpha << 24) | (color2.Red << 16) | \
                (color2.Green << 8) | color2.Blue
        gdiplus.GdipCreateLineBrushFromRectI(
            ctypes.byref(rect), argb1, argb2, mode, 0, ctypes.byref(self.brush)
        )

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放画刷"""
        if self.brush:
            gdiplus.GdipDeleteBrush(self.brush)
            self.brush = None

    def set_gamma_correction(self, use_gamma):
        """设置伽马校正"""
        gdiplus.GdipSetLineGammaCorrection(self.brush, 1 if use_gamma else 0)


class GdiplusFont:
    """GDI+ 字体封装"""

    def __init__(self, family_name, size, style=0, unit=Unit.UnitPoint):
        """
        创建字体
        :param family_name: 字体名称
        :param size: 字体大小
        :param style: 字体样式 (0=正常, 1=粗体, 2=斜体, 4=下划线, 8=删除线)
        :param unit: 字体单位
        """
        self.font = c_void_p()
        family = c_void_p()

        # 创建字体家族
        wname = ctypes.create_unicode_buffer(family_name)
        gdiplus.GdipCreateFontFamilyFromName(wname, None, ctypes.byref(family))

        # 创建字体
        gdiplus.GdipCreateFont(family, size, style, unit, ctypes.byref(self.font))

        # 释放字体家族
        gdiplus.GdipDeleteFontFamily(family)

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放字体"""
        if self.font:
            gdiplus.GdipDeleteFont(self.font)
            self.font = None

    def get_height(self, graphics=None):
        """获取字体高度"""
        height = c_float()
        if graphics:
            gdiplus.GdipGetFontHeight(self.font, graphics.graphics, ctypes.byref(height))
        else:
            gdiplus.GdipGetFontHeightGivenDPI(self.font, 96.0, ctypes.byref(height))
        return height.value


class GdiplusStringFormat:
    """GDI+ 字符串格式封装"""

    def __init__(self, flags=0, lang=0):
        """
        创建字符串格式
        :param flags: 格式化标志
        :param lang: 语言标识符
        """
        self.format = c_void_p()
        gdiplus.GdipCreateStringFormat(flags, lang, ctypes.byref(self.format))

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放格式对象"""
        if self.format:
            gdiplus.GdipDeleteStringFormat(self.format)
            self.format = None

    def set_alignment(self, align):
        """设置水平对齐"""
        gdiplus.GdipSetStringFormatAlign(self.format, align)

    def set_line_alignment(self, align):
        """设置垂直对齐"""
        gdiplus.GdipSetStringFormatLineAlign(self.format, align)

    def set_trimming(self, trimming):
        """设置裁剪方式"""
        gdiplus.GdipSetStringFormatTrimming(self.format, trimming)

    def set_format_flags(self, flags):
        """设置格式标志"""
        gdiplus.GdipSetStringFormatFlags(self.format, flags)


class GdiplusImage:
    """GDI+ 图像封装"""

    def __init__(self, filename=None, stream=None):
        """
        从文件或流创建图像
        :param filename: 图像文件路径
        :param stream: 图像数据流
        """
        self.image = c_void_p()

        if filename:
            wfilename = ctypes.create_unicode_buffer(filename)
            status = gdiplus.GdipLoadImageFromFile(wfilename, ctypes.byref(self.image))
            if status != GpStatus.Ok:
                raise Exception(f"加载图像失败: {filename}, 状态码: {status}")
        elif stream:
            # 从流加载需要更复杂的实现
            raise NotImplementedError("从流加载图像暂未实现")

    def __del__(self):
        self.dispose()

    def dispose(self):
        """释放图像"""
        if self.image:
            gdiplus.GdipDisposeImage(self.image)
            self.image = None

    def get_width(self):
        """获取图像宽度"""
        width = c_uint()
        gdiplus.GdipGetImageWidth(self.image, ctypes.byref(width))
        return width.value

    def get_height(self):
        """获取图像高度"""
        height = c_uint()
        gdiplus.GdipGetImageHeight(self.image, ctypes.byref(height))
        return height.value

    def get_size(self):
        """获取图像尺寸"""
        return Size(self.get_width(), self.get_height())

    def rotate_flip(self, rotate_flip_type):
        """旋转/翻转图像"""
        gdiplus.GdipImageRotateFlip(self.image, rotate_flip_type)

    def save(self, filename, clsid_encoder=None, params=None):
        """保存图像"""
        wfilename = ctypes.create_unicode_buffer(filename)
        if clsid_encoder:
            gdiplus.GdipSaveImageToFile(self.image, wfilename, clsid_encoder, params)
        else:
            # 默认使用 PNG 编码器
            # 这里简化处理，实际需要获取编码器 CLSID
            gdiplus.GdipSaveImageToFile(self.image, wfilename, None, None)


# GDI+ 初始化/清理
def gdiplus_startup():
    """初始化 GDI+"""
    token = c_ulong()
    input_params = GdiplusStartupInput()
    input_params.GdiplusVersion = 1
    input_params.DebugEventCallback = 0
    input_params.SuppressBackgroundThread = 0
    input_params.SuppressExternalCodecs = 0

    output_params = GdiplusStartupOutput()

    status = gdiplus.GdiplusStartup(ctypes.byref(token), ctypes.byref(input_params),
                                     ctypes.byref(output_params))
    if status != GpStatus.Ok:
        raise Exception(f"GDI+ 初始化失败，状态码: {status}")

    return token


def gdiplus_shutdown(token):
    """关闭 GDI+"""
    gdiplus.GdiplusShutdown(token)


# 便捷函数
def make_color(r, g, b, a=255):
    """创建 ARGB 颜色"""
    return ARGB(a, r, g, b)


def make_color_ref(colorref, alpha=255):
    """从 COLORREF 创建 ARGB"""
    r = colorref & 0xFF
    g = (colorref >> 8) & 0xFF
    b = (colorref >> 16) & 0xFF
    return ARGB(alpha, r, g, b)


# 预定义颜色
class Colors:
    """常用颜色"""
    Transparent = ARGB(0, 0, 0, 0)
    Black = ARGB(255, 0, 0, 0)
    White = ARGB(255, 255, 255, 255)
    Red = ARGB(255, 255, 0, 0)
    Green = ARGB(255, 0, 255, 0)
    Blue = ARGB(255, 0, 0, 255)
    Yellow = ARGB(255, 255, 255, 0)
    Cyan = ARGB(255, 0, 255, 255)
    Magenta = ARGB(255, 255, 0, 255)
    Gray = ARGB(255, 128, 128, 128)
    DarkGray = ARGB(255, 64, 64, 64)
    LightGray = ARGB(255, 192, 192, 192)
