# -*- coding: utf-8 -*-
"""
PySerUI - 核心模块
DirectUI 窗口引擎核心实现
"""

import win32gui
import win32con
import win32api
import win32ui
from win32api import RGB, MAKELONG, LOWORD, HIWORD
import ctypes
from ctypes import wintypes
from ctypes import c_void_p, c_int, c_uint, c_ulong, byref, sizeof
import threading
import time

# Windows 常量
WM_SUI_BASE = win32con.WM_USER + 0x1000

# 鼠标消息
WM_MOUSEENTER = WM_SUI_BASE + 1
WM_MOUSELEAVE = WM_SUI_BASE + 2
WM_MOUSEHOVER = WM_SUI_BASE + 3

# 控件通知消息
WM_SUI_NOTIFY = WM_SUI_BASE + 10

# 自定义绘制消息
WM_SUI_PAINT = WM_SUI_BASE + 20

# 布局消息
WM_SUI_LAYOUT = WM_SUI_BASE + 30

# 动画消息
WM_SUI_ANIMATION = WM_SUI_BASE + 40

# 定时器ID基址
TIMER_BASE = 0x1000


class RECT(ctypes.Structure):
    """Win32 RECT 结构"""
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

    def __init__(self, left=0, top=0, right=0, bottom=0):
        super().__init__()
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def to_tuple(self):
        return (self.left, self.top, self.right, self.bottom)


class POINT(ctypes.Structure):
    """Win32 POINT 结构"""
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    def __init__(self, x=0, y=0):
        super().__init__()
        self.x = x
        self.y = y


class SIZE(ctypes.Structure):
    """Win32 SIZE 结构"""
    _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    def __init__(self, cx=0, cy=0):
        super().__init__()
        self.cx = cx
        self.cy = cy


class TRACKMOUSEEVENT(ctypes.Structure):
    """鼠标跟踪事件结构"""
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("hwndTrack", ctypes.c_void_p),
        ("dwHoverTime", ctypes.c_ulong)
    ]


class SuiRect:
    """
    SUI 矩形类
    用于表示位置和大小
    """

    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def center_y(self):
        return self.y + self.height // 2

    def contains(self, x, y):
        """检查点是否在矩形内"""
        return self.left <= x < self.right and self.top <= y < self.bottom

    def intersects(self, other):
        """检查是否与其他矩形相交"""
        return not (self.right <= other.left or self.left >= other.right or
                    self.bottom <= other.top or self.top >= other.bottom)

    def intersect(self, other):
        """返回与另一个矩形的交集"""
        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        if right > left and bottom > top:
            return SuiRect(left, top, right - left, bottom - top)
        return None

    def union(self, other):
        """返回与另一个矩形的并集"""
        left = min(self.left, other.left)
        top = min(self.top, other.top)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        return SuiRect(left, top, right - left, bottom - top)

    def inflate(self, dx, dy):
        """膨胀矩形"""
        self.x -= dx
        self.y -= dy
        self.width += dx * 2
        self.height += dy * 2

    def deflate(self, dx, dy):
        """收缩矩形"""
        self.x += dx
        self.y += dy
        self.width -= dx * 2
        self.height -= dy * 2

    def offset(self, dx, dy):
        """偏移矩形"""
        self.x += dx
        self.y += dy

    def copy(self):
        """复制矩形"""
        return SuiRect(self.x, self.y, self.width, self.height)

    def to_win32_rect(self):
        """转换为 Win32 RECT"""
        return RECT(self.left, self.top, self.right, self.bottom)

    def __repr__(self):
        return f"SuiRect({self.x}, {self.y}, {self.width}, {self.height})"


class SuiPoint:
    """SUI 点类"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def distance_to(self, other):
        """计算到另一点的距离"""
        import math
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def offset(self, dx, dy):
        """偏移"""
        self.x += dx
        self.y += dy

    def copy(self):
        """复制"""
        return SuiPoint(self.x, self.y)

    def __repr__(self):
        return f"SuiPoint({self.x}, {self.y})"


class SuiSize:
    """SUI 大小类"""

    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def is_empty(self):
        """检查是否为空"""
        return self.width <= 0 or self.height <= 0

    def copy(self):
        """复制"""
        return SuiSize(self.width, self.height)

    def __repr__(self):
        return f"SuiSize({self.width}, {self.height})"


class SuiMessage:
    """
    SUI 消息类
    封装 Windows 消息
    """

    def __init__(self, hwnd, msg, wparam, lparam):
        self.hwnd = hwnd
        self.msg = msg
        self.wparam = wparam
        self.lparam = lparam

    @property
    def mouse_x(self):
        """鼠标 X 坐标"""
        return LOWORD(self.lparam)

    @property
    def mouse_y(self):
        """鼠标 Y 坐标"""
        return HIWORD(self.lparam)

    def get_mouse_pos(self):
        """获取鼠标位置"""
        return SuiPoint(self.mouse_x, self.mouse_y)

    @property
    def key_code(self):
        """按键代码"""
        return self.wparam

    @property
    def control_id(self):
        """控件ID"""
        return LOWORD(self.wparam)

    @property
    def notify_code(self):
        """通知代码"""
        return HIWORD(self.wparam)


class SuiDelegate:
    """
    SUI 委托类
    用于事件处理
    """

    def __init__(self):
        self._handlers = []

    def add(self, handler):
        """添加处理器"""
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove(self, handler):
        """移除处理器"""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def clear(self):
        """清空处理器"""
        self._handlers.clear()

    def invoke(self, *args, **kwargs):
        """调用所有处理器"""
        for handler in self._handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"事件处理错误: {e}")

    def __call__(self, *args, **kwargs):
        self.invoke(*args, **kwargs)

    def __iadd__(self, handler):
        self.add(handler)
        return self

    def __isub__(self, handler):
        self.remove(handler)
        return self


class SuiObject:
    """
    SUI 对象基类
    所有 SUI 对象的基类
    """

    _id_counter = 0
    _id_lock = threading.Lock()

    def __init__(self):
        with SuiObject._id_lock:
            SuiObject._id_counter += 1
            self._id = SuiObject._id_counter

        self._name = ""
        self._tag = None
        self._data = {}

    @property
    def id(self):
        """获取对象ID"""
        return self._id

    @property
    def name(self):
        """获取名称"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def tag(self):
        """获取标签"""
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def set_data(self, key, value):
        """设置数据"""
        self._data[key] = value

    def get_data(self, key, default=None):
        """获取数据"""
        return self._data.get(key, default)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id}, name='{self._name}')"


class SuiWindow(SuiObject):
    """
    SUI 窗口基类
    DirectUI 窗口基础实现
    """

    _class_registered = False
    _class_name = "SuiWindow"
    _windows = {}  # hwnd -> SuiWindow 映射

    def __init__(self, parent=None):
        super().__init__()

        self._hwnd = None
        self._parent = parent
        self._children = []
        self._visible = True
        self._enabled = True
        self._focused = False
        self._hovered = False
        self._capture = False

        # 位置和大小
        self._rect = SuiRect()
        self._client_rect = SuiRect()

        # 样式
        self._background_color = None
        self._transparent = False
        self._alpha = 255

        # 事件委托
        self.on_paint = SuiDelegate()
        self.on_click = SuiDelegate()
        self.on_dblclick = SuiDelegate()
        self.on_mouse_down = SuiDelegate()
        self.on_mouse_up = SuiDelegate()
        self.on_mouse_move = SuiDelegate()
        self.on_mouse_enter = SuiDelegate()
        self.on_mouse_leave = SuiDelegate()
        self.on_mouse_wheel = SuiDelegate()
        self.on_key_down = SuiDelegate()
        self.on_key_up = SuiDelegate()
        self.on_char = SuiDelegate()
        self.on_focus = SuiDelegate()
        self.on_blur = SuiDelegate()
        self.on_size = SuiDelegate()
        self.on_move = SuiDelegate()
        self.on_show = SuiDelegate()
        self.on_hide = SuiDelegate()
        self.on_destroy = SuiDelegate()

        # 注册窗口类
        self._register_class()

    def _register_class(self):
        """注册窗口类"""
        if not SuiWindow._class_registered:
            wc = win32gui.WNDCLASS()
            wc.hInstance = win32api.GetModuleHandle(None)
            wc.lpszClassName = SuiWindow._class_name
            wc.lpfnWndProc = self._wnd_proc
            wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
            wc.hbrBackground = win32con.COLOR_BTNFACE + 1
            wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW

            try:
                win32gui.RegisterClass(wc)
                SuiWindow._class_registered = True
            except Exception as e:
                # 类可能已注册
                pass

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """窗口过程"""
        # 获取窗口对象
        window = SuiWindow._windows.get(hwnd)

        if window:
            result = window._process_message(msg, wparam, lparam)
            if result is not None:
                return result

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _process_message(self, msg, wparam, lparam):
        """处理消息"""
        message = SuiMessage(self._hwnd, msg, wparam, lparam)

        if msg == win32con.WM_PAINT:
            return self._on_paint()

        elif msg == win32con.WM_ERASEBKGND:
            return 1  # 防止背景擦除闪烁

        elif msg == win32con.WM_SIZE:
            width = LOWORD(lparam)
            height = HIWORD(lparam)
            self._rect.width = width
            self._rect.height = height
            self._update_client_rect()
            self.on_size(width, height)
            self._on_layout()
            return 0

        elif msg == win32con.WM_MOVE:
            x = LOWORD(lparam)
            y = HIWORD(lparam)
            self._rect.x = x
            self._rect.y = y
            self._update_client_rect()
            self.on_move(x, y)
            return 0

        elif msg == win32con.WM_LBUTTONDOWN:
            self._on_mouse_down(message, 1)  # 左键
            return 0

        elif msg == win32con.WM_LBUTTONUP:
            self._on_mouse_up(message, 1)
            return 0

        elif msg == win32con.WM_LBUTTONDBLCLK:
            self._on_dblclick(message)
            return 0

        elif msg == win32con.WM_RBUTTONDOWN:
            self._on_mouse_down(message, 2)  # 右键
            return 0

        elif msg == win32con.WM_RBUTTONUP:
            self._on_mouse_up(message, 2)
            return 0

        elif msg == win32con.WM_MBUTTONDOWN:
            self._on_mouse_down(message, 4)  # 中键
            return 0

        elif msg == win32con.WM_MBUTTONUP:
            self._on_mouse_up(message, 4)
            return 0

        elif msg == win32con.WM_MOUSEMOVE:
            self._on_mouse_move(message)
            return 0

        elif msg == win32con.WM_MOUSEWHEEL:
            delta = wparam >> 16
            self._on_mouse_wheel(message, delta)
            return 0

        elif msg == win32con.WM_MOUSELEAVE:
            self._on_mouse_leave()
            return 0

        elif msg == win32con.WM_KEYDOWN:
            self._on_key_down(message)
            return 0

        elif msg == win32con.WM_KEYUP:
            self._on_key_up(message)
            return 0

        elif msg == win32con.WM_CHAR:
            self._on_char(message)
            return 0

        elif msg == win32con.WM_SETFOCUS:
            self._focused = True
            self.on_focus()
            return 0

        elif msg == win32con.WM_KILLFOCUS:
            self._focused = False
            self.on_blur()
            return 0

        elif msg == win32con.WM_SHOWWINDOW:
            if wparam:
                self._visible = True
                self.on_show()
            else:
                self._visible = False
                self.on_hide()
            return 0

        elif msg == win32con.WM_DESTROY:
            self.on_destroy()
            if self._hwnd in SuiWindow._windows:
                del SuiWindow._windows[self._hwnd]
            return 0

        elif msg == win32con.WM_NCHITTEST:
            # 非客户区命中测试
            return win32con.HTCLIENT

        return None

    def _on_paint(self):
        """绘制处理"""
        ps = win32gui.PAINTSTRUCT()
        hdc = win32gui.BeginPaint(self._hwnd, ps)

        # 创建内存DC进行双缓冲绘制
        mem_dc = win32gui.CreateCompatibleDC(hdc)
        mem_bitmap = win32gui.CreateCompatibleBitmap(hdc, self._rect.width, self._rect.height)
        win32gui.SelectObject(mem_dc, mem_bitmap)

        # 绘制背景
        self._draw_background(mem_dc)

        # 触发绘制事件
        self.on_paint(mem_dc, self._client_rect)

        # 绘制子控件
        self._draw_children(mem_dc)

        # 复制到屏幕
        win32gui.BitBlt(hdc, 0, 0, self._rect.width, self._rect.height,
                        mem_dc, 0, 0, win32con.SRCCOPY)

        # 清理
        win32gui.DeleteObject(mem_bitmap)
        win32gui.DeleteDC(mem_dc)
        win32gui.EndPaint(self._hwnd, ps)

        return 0

    def _draw_background(self, hdc):
        """绘制背景"""
        if self._background_color is not None:
            brush = win32gui.CreateSolidBrush(self._background_color)
            rect = self._rect.to_win32_rect()
            win32gui.FillRect(hdc, rect.to_tuple(), brush)
            win32gui.DeleteObject(brush)

    def _draw_children(self, hdc):
        """绘制子控件"""
        for child in self._children:
            if child._visible:
                child._draw(hdc)

    def _draw(self, hdc):
        """绘制自身"""
        # 子类重写此方法实现自定义绘制
        pass

    def _on_layout(self):
        """布局处理"""
        for child in self._children:
            child._do_layout()

    def _do_layout(self):
        """执行布局"""
        pass

    def _on_mouse_down(self, message, button):
        """鼠标按下"""
        self._capture = True
        win32gui.SetCapture(self._hwnd)
        self.on_mouse_down(message.mouse_x, message.mouse_y, button)

    def _on_mouse_up(self, message, button):
        """鼠标释放"""
        if self._capture:
            self._capture = False
            win32gui.ReleaseCapture()
        self.on_mouse_up(message.mouse_x, message.mouse_y, button)

        # 检查是否在窗口内，触发点击
        if self._rect.contains(message.mouse_x, message.mouse_y):
            self.on_click(message.mouse_x, message.mouse_y, button)

    def _on_dblclick(self, message):
        """鼠标双击"""
        self.on_dblclick(message.mouse_x, message.mouse_y)

    def _on_mouse_move(self, message):
        """鼠标移动"""
        x, y = message.mouse_x, message.mouse_y

        if not self._hovered:
            self._hovered = True
            self._on_mouse_enter()
            # 设置鼠标跟踪以接收 WM_MOUSELEAVE
            self._track_mouse_event()

        self.on_mouse_move(x, y)

    def _track_mouse_event(self):
        """设置鼠标跟踪"""
        tme = TRACKMOUSEEVENT()
        tme.cbSize = sizeof(tme)
        tme.dwFlags = win32con.TME_LEAVE
        tme.hwndTrack = self._hwnd
        tme.dwHoverTime = win32con.HOVER_DEFAULT

        # 调用 TrackMouseEvent API
        ctypes.windll.user32.TrackMouseEvent(byref(tme))

    def _on_mouse_enter(self):
        """鼠标进入"""
        self.on_mouse_enter()

    def _on_mouse_leave(self):
        """鼠标离开"""
        self._hovered = False
        self.on_mouse_leave()

    def _on_mouse_wheel(self, message, delta):
        """鼠标滚轮"""
        self.on_mouse_wheel(message.mouse_x, message.mouse_y, delta)

    def _on_key_down(self, message):
        """按键按下"""
        self.on_key_down(message.key_code)

    def _on_key_up(self, message):
        """按键释放"""
        self.on_key_up(message.key_code)

    def _on_char(self, message):
        """字符输入"""
        self.on_char(chr(message.key_code))

    def _update_client_rect(self):
        """更新客户区矩形"""
        if self._hwnd:
            left, top, right, bottom = win32gui.GetClientRect(self._hwnd)
            self._client_rect = SuiRect(0, 0, right - left, bottom - top)

    def create(self, title="", x=0, y=0, width=800, height=600,
               style=None, ex_style=0):
        """
        创建窗口
        :param title: 窗口标题
        :param x: 窗口X位置
        :param y: 窗口Y位置
        :param width: 窗口宽度
        :param height: 窗口高度
        :param style: 窗口样式
        :param ex_style: 扩展窗口样式
        """
        if style is None:
            style = (win32con.WS_OVERLAPPEDWINDOW |
                     win32con.WS_CLIPCHILDREN |
                     win32con.WS_CLIPSIBLINGS)

        hwnd = win32gui.CreateWindowEx(
            ex_style,
            SuiWindow._class_name,
            title,
            style,
            x, y, width, height,
            self._parent._hwnd if self._parent else None,
            0,
            win32api.GetModuleHandle(None),
            None
        )

        if not hwnd:
            raise Exception(f"创建窗口失败: {win32gui.GetLastError()}")

        self._hwnd = hwnd
        self._rect = SuiRect(x, y, width, height)
        self._update_client_rect()

        # 保存窗口引用
        SuiWindow._windows[hwnd] = self

        # 设置用户数据以便在窗口过程中查找
        win32gui.SetWindowLong(hwnd, win32con.GWL_USERDATA, id(self))

        return self

    def show(self, cmd_show=win32con.SW_SHOW):
        """显示窗口"""
        if self._hwnd:
            win32gui.ShowWindow(self._hwnd, cmd_show)
            win32gui.UpdateWindow(self._hwnd)

    def hide(self):
        """隐藏窗口"""
        if self._hwnd:
            win32gui.ShowWindow(self._hwnd, win32con.SW_HIDE)

    def close(self):
        """关闭窗口"""
        if self._hwnd:
            win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)

    def destroy(self):
        """销毁窗口"""
        if self._hwnd:
            win32gui.DestroyWindow(self._hwnd)
            self._hwnd = None

    def invalidate(self, rect=None, erase=True):
        """使区域无效，触发重绘"""
        if self._hwnd:
            if rect:
                win32rect = rect.to_win32_rect()
                win32gui.InvalidateRect(self._hwnd, win32rect.to_tuple(), erase)
            else:
                win32gui.InvalidateRect(self._hwnd, None, erase)

    def update(self):
        """立即更新窗口"""
        if self._hwnd:
            win32gui.UpdateWindow(self._hwnd)

    def set_position(self, x, y):
        """设置位置"""
        if self._hwnd:
            win32gui.SetWindowPos(self._hwnd, 0, x, y, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

    def set_size(self, width, height):
        """设置大小"""
        if self._hwnd:
            win32gui.SetWindowPos(self._hwnd, 0, 0, 0, width, height,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOZORDER)

    def set_rect(self, x, y, width, height):
        """设置矩形"""
        if self._hwnd:
            win32gui.SetWindowPos(self._hwnd, 0, x, y, width, height,
                                  win32con.SWP_NOZORDER)

    def get_rect(self):
        """获取窗口矩形（屏幕坐标）"""
        if self._hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
            return SuiRect(left, top, right - left, bottom - top)
        return self._rect.copy()

    def get_client_rect(self):
        """获取客户区矩形"""
        return self._client_rect.copy()

    def client_to_screen(self, x, y):
        """客户区坐标转屏幕坐标"""
        if self._hwnd:
            pt = POINT(x, y)
            ctypes.windll.user32.ClientToScreen(self._hwnd, byref(pt))
            return (pt.x, pt.y)
        return (x, y)

    def screen_to_client(self, x, y):
        """屏幕坐标转客户区坐标"""
        if self._hwnd:
            pt = POINT(x, y)
            ctypes.windll.user32.ScreenToClient(self._hwnd, byref(pt))
            return (pt.x, pt.y)
        return (x, y)

    def set_text(self, text):
        """设置窗口文本"""
        if self._hwnd:
            win32gui.SetWindowText(self._hwnd, text)

    def get_text(self):
        """获取窗口文本"""
        if self._hwnd:
            return win32gui.GetWindowText(self._hwnd)
        return ""

    def set_background_color(self, color):
        """设置背景色"""
        self._background_color = color
        self.invalidate()

    def set_transparent(self, transparent, alpha=255):
        """设置透明"""
        self._transparent = transparent
        self._alpha = alpha

        if self._hwnd:
            if transparent:
                ex_style = win32gui.GetWindowLong(self._hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(self._hwnd, win32con.GWL_EXSTYLE,
                                       ex_style | win32con.WS_EX_LAYERED)
                ctypes.windll.user32.SetLayeredWindowAttributes(
                    self._hwnd, 0, alpha, win32con.LWA_ALPHA)
            else:
                ex_style = win32gui.GetWindowLong(self._hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(self._hwnd, win32con.GWL_EXSTYLE,
                                       ex_style & ~win32con.WS_EX_LAYERED)
            self.invalidate()

    def add_child(self, child):
        """添加子控件"""
        if child not in self._children:
            self._children.append(child)
            child._parent = self

    def remove_child(self, child):
        """移除子控件"""
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def set_focus(self):
        """设置焦点"""
        if self._hwnd:
            win32gui.SetFocus(self._hwnd)

    def is_focused(self):
        """检查是否有焦点"""
        if self._hwnd:
            return win32gui.GetFocus() == self._hwnd
        return False

    @property
    def hwnd(self):
        """获取窗口句柄"""
        return self._hwnd

    @property
    def parent(self):
        """获取父窗口"""
        return self._parent

    @property
    def children(self):
        """获取子控件列表"""
        return self._children[:]

    @property
    def visible(self):
        """获取可见性"""
        return self._visible

    @visible.setter
    def visible(self, value):
        if value:
            self.show()
        else:
            self.hide()

    @property
    def enabled(self):
        """获取启用状态"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._hwnd:
            win32gui.EnableWindow(self._hwnd, value)

    @property
    def hovered(self):
        """获取鼠标悬停状态"""
        return self._hovered


class SuiApplication:
    """
    SUI 应用程序类
    管理应用程序生命周期
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._running = False
        self._main_window = None
        self._message_handlers = {}

        # 初始化 COM
        ctypes.windll.ole32.OleInitialize(None)

    def set_main_window(self, window):
        """设置主窗口"""
        self._main_window = window

    def run(self):
        """运行消息循环"""
        self._running = True

        msg = wintypes.MSG()

        while self._running:
            # 使用 PeekMessage 以便可以处理空闲时间
            ret = ctypes.windll.user32.PeekMessageW(
                byref(msg), 0, 0, 0, win32con.PM_REMOVE)

            if ret:
                if msg.message == win32con.WM_QUIT:
                    self._running = False
                    break

                ctypes.windll.user32.TranslateMessage(byref(msg))
                ctypes.windll.user32.DispatchMessageW(byref(msg))
            else:
                # 空闲时间处理
                self._on_idle()
                # 短暂休眠以减少CPU使用
                time.sleep(0.001)

        return msg.wParam

    def _on_idle(self):
        """空闲处理"""
        pass

    def quit(self, exit_code=0):
        """退出应用程序"""
        self._running = False
        ctypes.windll.user32.PostQuitMessage(exit_code)

    def exit(self, exit_code=0):
        """退出应用程序（同 quit）"""
        self.quit(exit_code)

    def post_message(self, hwnd, msg, wparam=0, lparam=0):
        """投递消息"""
        win32gui.PostMessage(hwnd, msg, wparam, lparam)

    def send_message(self, hwnd, msg, wparam=0, lparam=0):
        """发送消息"""
        return win32gui.SendMessage(hwnd, msg, wparam, lparam)


def get_application():
    """获取应用程序实例"""
    return SuiApplication()


def message_box(text, caption="提示", style=win32con.MB_OK):
    """显示消息框"""
    return win32gui.MessageBox(0, text, caption, style)
