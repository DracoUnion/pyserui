# -*- coding: utf-8 -*-
"""PySerUI: a Python DirectUI-compatible framework."""
from .geometry import (Point, Size, Rect, RectF, ARGB, Colors, make_color,
                       make_color_ref, point_in_rect, merge_rect, mix_color,
                       invert_color, low_word, high_word, make_long)
from .events import Delegate, SuiDelegate
from .core import (SuiObject, SuiWindow, SuiApplication, SuiMessage,
                   get_application, message_box, WM_SUI_BASE, WM_SUI_NOTIFY,
                   WM_SUI_PAINT, WM_SUI_LAYOUT, TIMER_BASE)

# Legacy names from the first Python port.
SuiRect = Rect
SuiPoint = Point
SuiSize = Size
from .controls.basic import (SuiControl, SuiLabel, SuiButton, SuiEdit,
    SuiPanel, SuiProgressBar, SuiCheckBox, SuiRadioButton, SuiImage,
    SuiSlider, SuiScrollBar, SuiTab, SuiSwitcher, SuiGroupBox, SuiLink,
    SuiCustom)
from .resources import Resource, ResourceBundle, SDB
from .source_inventory import Declaration, inventory, summarize

__version__ = '2.0.0'

def create_window(title='SuiWindow', width=800, height=600, **kwargs):
    return SuiWindow().create(title=title, width=width, height=height, **kwargs)

def run_application(window=None):
    app = get_application()
    if window is not None:
        app.set_main_window(window); window.show()
    return app.run()

def initialize():
    """Initialize native services when running on Windows; pure model needs none."""
    return True

def shutdown():
    return None
