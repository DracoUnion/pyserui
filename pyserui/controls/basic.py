# -*- coding: utf-8 -*-
"""Platform-neutral control state model with optional drawing hooks."""
from __future__ import annotations
from ..core import SuiWindow
from ..events import Delegate
from ..geometry import Colors, make_color

class SuiControl(SuiWindow):
    def __init__(self, parent=None):
        super().__init__(parent); self._dock=None; self._anchor=('left','top'); self._margin=(0,0,0,0); self._padding=(0,0,0,0); self._fore_color=Colors.Black; self._back_color=None; self._border_color=None; self._border_width=0; self._tooltip=''; self._font_name='微软雅黑'; self._font_size=9; self._font_bold=False
    @property
    def dock(self): return self._dock
    @dock.setter
    def dock(self,v): self._dock=v; self.layout()
    @property
    def anchor(self): return self._anchor
    @anchor.setter
    def anchor(self,v): self._anchor=tuple(v)
    @property
    def margin(self): return self._margin
    @margin.setter
    def margin(self,v): self._margin=tuple(v)
    @property
    def padding(self): return self._padding
    @padding.setter
    def padding(self,v): self._padding=tuple(v)
    @property
    def fore_color(self): return self._fore_color
    @fore_color.setter
    def fore_color(self,v): self._fore_color=v; self.invalidate()
    @property
    def back_color(self): return self._back_color
    @back_color.setter
    def back_color(self,v): self._back_color=v; self.invalidate()
    @property
    def border_color(self): return self._border_color
    @border_color.setter
    def border_color(self,v): self._border_color=v; self.invalidate()
    @property
    def border_width(self): return self._border_width
    @border_width.setter
    def border_width(self,v): self._border_width=max(0,int(v)); self.invalidate()
    @property
    def tooltip(self): return self._tooltip
    @tooltip.setter
    def tooltip(self,v): self._tooltip=str(v)
    @property
    def font_size(self): return self._font_size
    @font_size.setter
    def font_size(self,v): self._font_size=float(v); self.invalidate()
    @property
    def font_bold(self): return self._font_bold
    @font_bold.setter
    def font_bold(self,v): self._font_bold=bool(v); self.invalidate()

class SuiLabel(SuiControl):
    def __init__(self,parent=None,text=''): super().__init__(parent); self._text=str(text); self._text_align='left'; self._valign='center'
    @property
    def text(self): return self._text
    @text.setter
    def text(self,v): self._text=str(v); self.invalidate()
    @property
    def text_align(self): return self._text_align
    @text_align.setter
    def text_align(self,v): self._text_align=v; self.invalidate()

class SuiButton(SuiControl):
    def __init__(self,parent=None,text=''):
        super().__init__(parent); self._text=str(text); self._pressed=False; self._checked=False; self._checkable=False; self._hover_color=make_color(230,240,250); self._pressed_color=make_color(200,220,240)
    @property
    def text(self): return self._text
    @text.setter
    def text(self,v): self._text=str(v); self.invalidate()
    @property
    def checked(self): return self._checked
    @checked.setter
    def checked(self,v): self._checked=bool(v) if self._checkable else self._checked
    @property
    def checkable(self): return self._checkable
    @checkable.setter
    def checkable(self,v): self._checkable=bool(v)
    def click(self):
        if self._checkable: self._checked=not self._checked
        self.on_click(self)

class SuiEdit(SuiControl):
    def __init__(self,parent=None,text=''): super().__init__(parent); self._text=str(text); self._caret_pos=len(self._text); self._read_only=False; self._max_length=0; self._password_char=None
    @property
    def text(self): return self._text
    @text.setter
    def text(self,v): self._text=str(v); self._caret_pos=len(self._text); self.invalidate()
    @property
    def read_only(self): return self._read_only
    @read_only.setter
    def read_only(self,v): self._read_only=bool(v)
    @property
    def max_length(self): return self._max_length
    @max_length.setter
    def max_length(self,v): self._max_length=max(0,int(v))
    @property
    def password_char(self): return self._password_char
    @password_char.setter
    def password_char(self,v): self._password_char=v

class SuiPanel(SuiControl):
    def __init__(self,parent=None): super().__init__(parent); self._back_color=make_color(250,250,250)
    add_control=SuiControl.add_child
    remove_control=SuiControl.remove_child

class SuiProgressBar(SuiControl):
    def __init__(self,parent=None): super().__init__(parent); self._value=0; self._minimum=0; self._maximum=100; self._orientation='horizontal'
    @property
    def value(self): return self._value
    @value.setter
    def value(self,v): self._value=max(self._minimum,min(self._maximum,v)); self.invalidate()
    @property
    def minimum(self): return self._minimum
    @minimum.setter
    def minimum(self,v): self._minimum=v; self.value=self._value
    @property
    def maximum(self): return self._maximum
    @maximum.setter
    def maximum(self,v): self._maximum=v; self.value=self._value

class SuiCheckBox(SuiControl):
    def __init__(self,parent=None,text=''): super().__init__(parent); self._text=str(text); self._checked=False
    @property
    def text(self): return self._text
    @text.setter
    def text(self,v): self._text=str(v)
    @property
    def checked(self): return self._checked
    @checked.setter
    def checked(self,v): self._checked=bool(v); self.invalidate()
    def click(self): self._checked=not self._checked; self.on_click(self)

class SuiRadioButton(SuiCheckBox):
    def __init__(self,parent=None,text=''): super().__init__(parent,text); self._group_name='default'
    @property
    def group_name(self): return self._group_name
    @group_name.setter
    def group_name(self,v): self._group_name=str(v)
    @SuiCheckBox.checked.setter
    def checked(self,v):
        if v and self.parent:
            for c in self.parent.children:
                if isinstance(c,SuiRadioButton) and c is not self and c.group_name==self.group_name: c._checked=False
        self._checked=bool(v); self.invalidate()

class SuiImage(SuiControl): pass
class SuiSlider(SuiProgressBar): pass
class SuiScrollBar(SuiSlider): pass
class SuiTab(SuiPanel): pass
class SuiSwitcher(SuiControl): pass
class SuiGroupBox(SuiPanel): pass
class SuiLink(SuiLabel): pass
class SuiCustom(SuiControl): pass
