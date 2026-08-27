# Compatibility aliases for the original SyserUI naming conventions.
from .geometry import *
from .events import Delegate as SuiDelegate

SUI_STATUS_SUCCESS = 0
SUI_STATUS_FAILED = -1

# Common E-language spellings used by ports.
LOWORD = low_word
HIWORD = high_word
MAKELONG = make_long
PointInRect = point_in_rect
MergeRect = merge_rect
MixColor = mix_color
