# -*- coding: utf-8 -*-
"""Core object tree and optional Win32 window host."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Optional

from .events import Delegate
from .geometry import Point, Rect, Size

WM_SUI_BASE = 0x5000
WM_MOUSEENTER = WM_SUI_BASE + 1
WM_MOUSELEAVE = WM_SUI_BASE + 2
WM_MOUSEHOVER = WM_SUI_BASE + 3
WM_SUI_NOTIFY = WM_SUI_BASE + 10
WM_SUI_PAINT = WM_SUI_BASE + 20
WM_SUI_LAYOUT = WM_SUI_BASE + 30
WM_SUI_ANIMATION = WM_SUI_BASE + 40
TIMER_BASE = 0x1000


@dataclass(frozen=True)
class SuiMessage:
    hwnd: object
    msg: int
    wparam: int = 0
    lparam: int = 0

    @property
    def mouse_x(self): return self.lparam & 0xFFFF
    @property
    def mouse_y(self): return (self.lparam >> 16) & 0xFFFF
    @property
    def key_code(self): return self.wparam
    @property
    def control_id(self): return self.wparam & 0xFFFF
    @property
    def notify_code(self): return (self.wparam >> 16) & 0xFFFF
    def get_mouse_pos(self): return Point(self.mouse_x, self.mouse_y)


class SuiObject:
    _id_counter = 0
    _id_lock = threading.Lock()

    def __init__(self):
        with self._id_lock:
            type(self)._id_counter += 1
            self._id = type(self)._id_counter
        self._name = ""
        self._tag = None
        self._data = {}

    @property
    def id(self): return self._id
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = str(value)
    @property
    def tag(self): return self._tag
    @tag.setter
    def tag(self, value): self._tag = value
    def set_data(self, key, value): self._data[key] = value
    def get_data(self, key, default=None): return self._data.get(key, default)
    def __repr__(self): return f"{type(self).__name__}(id={self.id}, name={self.name!r})"


class SuiWindow(SuiObject):
    """A DirectUI node; a real HWND is created only when requested on Windows."""
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self._children = []
        self._rect = Rect()
        self._hwnd = None
        self._visible = True
        self._enabled = True
        self._focused = False
        self._hovered = False
        self._background_color = None
        self._alpha = 255
        for name in ('paint', 'click', 'dblclick', 'mouse_down', 'mouse_up',
                     'mouse_move', 'mouse_enter', 'mouse_leave', 'mouse_wheel',
                     'key_down', 'key_up', 'char', 'focus', 'blur', 'size',
                     'move', 'show', 'hide', 'destroy'):
            setattr(self, 'on_' + name, Delegate())
        if parent is not None:
            parent.add_child(self)

    @property
    def hwnd(self): return self._hwnd
    @property
    def parent(self): return self._parent
    @property
    def children(self): return tuple(self._children)
    @property
    def rect(self): return self._rect
    @property
    def visible(self): return self._visible
    @visible.setter
    def visible(self, value):
        self._visible = bool(value)
        (self.on_show if self._visible else self.on_hide)()
        if self._hwnd:
            self._win32_show(self._visible)
    @property
    def enabled(self): return self._enabled
    @enabled.setter
    def enabled(self, value): self._enabled = bool(value)
    @property
    def focused(self): return self._focused
    @property
    def hovered(self): return self._hovered
    def add_child(self, child):
        if child not in self._children:
            if child._parent and child in child._parent._children:
                child._parent._children.remove(child)
            child._parent = self
            self._children.append(child)
            child._do_layout()
        return child
    def remove_child(self, child):
        if child in self._children:
            self._children.remove(child); child._parent = None
    def _do_layout(self): pass
    def layout(self):
        for child in self._children: child._do_layout(); child.layout()
    def hit_test(self, x, y):
        if not self._visible or not self._enabled or not self._rect.contains_point(x, y): return None
        for child in reversed(self._children):
            hit = child.hit_test(x - self.left, y - self.top)
            if hit: return hit
        return self
    def set_bounds(self, x, y, width, height):
        self._rect = Rect(int(x), int(y), int(width), int(height)); self.on_size(width, height); return self
    def set_location(self, x, y): return self.set_bounds(x, y, self.width, self.height)
    def set_size(self, width, height): return self.set_bounds(self.left, self.top, width, height)
    @property
    def left(self): return self._rect.left
    @left.setter
    def left(self, v): self.set_location(v, self.top)
    @property
    def top(self): return self._rect.top
    @top.setter
    def top(self, v): self.set_location(self.left, v)
    @property
    def width(self): return self._rect.width
    @width.setter
    def width(self, v): self.set_size(v, self.height)
    @property
    def height(self): return self._rect.height
    @height.setter
    def height(self, v): self.set_size(self.width, v)
    def invalidate(self, rect=None, erase=True):
        if self._hwnd:
            try:
                import win32gui
                win32gui.InvalidateRect(self._hwnd, rect.to_tuple() if rect else None, erase)
            except ImportError: pass
    def set_background_color(self, color): self._background_color = color; self.invalidate()
    def set_text(self, text):
        if self._hwnd:
            import win32gui; win32gui.SetWindowText(self._hwnd, str(text))
        self._text = str(text)
    def get_text(self): return getattr(self, '_text', '')
    def _win32_show(self, visible):
        import win32gui; import win32con
        win32gui.ShowWindow(self._hwnd, win32con.SW_SHOW if visible else win32con.SW_HIDE)
    def create(self, title='', x=0, y=0, width=800, height=600, style=None, ex_style=0):
        try:
            import win32gui, win32con, win32api
        except ImportError as e: raise RuntimeError('PySerUI window support requires Windows and pywin32') from e
        if style is None: style = win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN | win32con.WS_CLIPSIBLINGS
        cls = 'SuiWindow'
        try: win32gui.RegisterClass(win32gui.WNDCLASS())
        except Exception: pass
        self._hwnd = win32gui.CreateWindowEx(ex_style, cls, title, style, x, y, width, height, 0, 0, win32api.GetModuleHandle(None), None)
        self.set_bounds(x, y, width, height); self._text = title
        return self
    def show(self, cmd_show=None): self.visible = True
    def hide(self): self.visible = False
    def close(self):
        if self._hwnd:
            import win32gui, win32con; win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
    def destroy(self):
        if self._hwnd:
            import win32gui; win32gui.DestroyWindow(self._hwnd); self._hwnd = None
        self.on_destroy()
    def set_focus(self): self._focused = True; self.on_focus()
    def get_client_rect(self): return Rect(0, 0, self.width, self.height)


class SuiApplication:
    _instance = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls); cls._instance._running = False
        return cls._instance
    def set_main_window(self, window): self._main_window = window
    def run(self):
        try:
            import win32gui
        except ImportError as e: raise RuntimeError('message loop requires Windows and pywin32') from e
        self._running = True
        while self._running:
            win32gui.PumpWaitingMessages()
        return 0
    def quit(self, exit_code=0): self._running = False
    exit = quit
    def post_message(self, hwnd, msg, wparam=0, lparam=0):
        import win32gui; return win32gui.PostMessage(hwnd, msg, wparam, lparam)
    def send_message(self, hwnd, msg, wparam=0, lparam=0):
        import win32gui; return win32gui.SendMessage(hwnd, msg, wparam, lparam)


def get_application(): return SuiApplication()

def message_box(text, caption='提示', style=0):
    try:
        import win32gui; return win32gui.MessageBox(0, str(text), str(caption), style)
    except ImportError: raise RuntimeError('message_box requires Windows and pywin32')
