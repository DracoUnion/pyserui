# -*- coding: utf-8 -*-
"""Optional native rendering facade. Pure state remains importable anywhere."""
try:
    from pyserui.gdiplus import *
except ImportError:
    class GdiplusUnavailable(RuntimeError): pass
    def gdiplus_startup(): raise GdiplusUnavailable('GDI+ requires Windows')
