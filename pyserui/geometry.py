# -*- coding: utf-8 -*-
"""
PySerUI - geometry primitives
Pure-value geometry & color helpers. No Windows dependencies so this module
is importable and testable on any platform.

Mirrors the geometry / color / bitwise helper surface of the original
SyserUI Engine (Syser Group, 2008-2012) without a dependency on the Win32
ABI.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Points / sizes / rects
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Point:
    """An immutable 2D point."""
    x: int = 0
    y: int = 0

    def offset(self, dx: int = 0, dy: int = 0) -> "Point":
        return Point(self.x + dx, self.y + dy)

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def to_tuple(self):
        return (self.x, self.y)


@dataclass(frozen=True)
class Size:
    width: int = 0
    height: int = 0

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def to_tuple(self):
        return (self.width, self.height)


@dataclass(frozen=True)
class Rect:
    """A mutable-free integer rectangle with the geometry operations used by
    the rest of the framework."""
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    # -- derived properties -------------------------------------------------
    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def x(self) -> int:
        return self.left

    @property
    def y(self) -> int:
        return self.top

    @property
    def center_x(self) -> int:
        return self.left + self.width // 2

    @property
    def center_y(self) -> int:
        return self.top + self.height // 2

    @property
    def location(self) -> Point:
        return Point(self.left, self.top)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    # -- predicates ---------------------------------------------------------
    def contains_point(self, x: int, y: int) -> bool:
        """Point-in-rect test (right/bottom exclusive, like DirectUI hit
        testing)."""
        return self.left <= x < self.right and self.top <= y < self.bottom

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.right <= other.left or self.left >= other.right or
            self.bottom <= other.top or self.top >= other.bottom
        )

    # -- derived rects ------------------------------------------------------
    def intersection(self, other: "Rect") -> "Rect | None":
        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        if right > left and bottom > top:
            return Rect(left, top, right - left, bottom - top)
        return None

    def union(self, other: "Rect") -> "Rect":
        left = min(self.left, other.left)
        top = min(self.top, other.top)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        return Rect(left, top, right - left, bottom - top)

    def inflate(self, dx: int, dy: int) -> "Rect":
        return Rect(self.left - dx, self.top - dy,
                    self.width + dx * 2, self.height + dy * 2)

    def deflate(self, dx: int, dy: int) -> "Rect":
        return Rect(self.left + dx, self.top + dy,
                    self.width - dx * 2, self.height - dy * 2)

    def offset(self, dx: int = 0, dy: int = 0) -> "Rect":
        return Rect(self.left + dx, self.top + dy, self.width, self.height)

    def to_tuple(self):
        """(left, top, right, bottom) — the order expected by Win32 APIs."""
        return (self.left, self.top, self.right, self.bottom)

    def to_box(self):
        """(left, top, width, height) — the order used by the engine API."""
        return (self.left, self.top, self.width, self.height)


@dataclass(frozen=True)
class RectF:
    """Float rectangle used when talking to GDI+ drawing APIs."""
    left: float = 0.0
    top: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def bottom(self) -> float:
        return self.top + self.height


# ---------------------------------------------------------------------------
# Color helpers (COLORREF <-> ARGB <-> components)
# ---------------------------------------------------------------------------
class ARGB:
    """An 0x:RRGGBBAA color value plus component helpers.

    Stored as a plain int so colors compare/hash naturally and can be passed
    straight to ctypes as a 0xRRGGBBAA value where required.
    """
    __slots__ = ("value",)

    def __init__(self, value: int):
        self.value = value & 0xFFFFFFFF

    # -- component access ---------------------------------------------------
    @property
    def alpha(self) -> int:
        return (self.value >> 24) & 0xFF

    @property
    def red(self) -> int:
        return (self.value >> 16) & 0xFF

    @property
    def green(self) -> int:
        return (self.value >> 8) & 0xFF

    @property
    def blue(self) -> int:
        return self.value & 0xFF

    @property
    def rgb(self) -> int:
        """COLORREF (0x00RRGGBB) — the GDI color value."""
        return self.value & 0xFFFFFF

    # -- construction -------------------------------------------------------
    @classmethod
    def from_rgba(cls, r, g, b, a=255) -> "ARGB":
        return cls(((int(a) & 0xFF) << 24) | ((int(r) & 0xFF) << 16) |
                   ((int(g) & 0xFF) << 8) | (int(b) & 0xFF))

    @classmethod
    def from_colorref(cls, colorref: int, a: int = 255) -> "ARGB":
        return cls(((int(a) & 0xFF) << 24) | (int(colorref) & 0xFFFFFF))

    @classmethod
    def from_name(cls, name: str) -> "ARGB":
        """Parse '0xRRGGBBAA' or '#RRGGBB' style strings."""
        s = name.strip()
        if s.startswith("0x") or s.startswith("0X"):
            return cls(int(s[2:], 16))
        if s.startswith("#"):
            hexval = s[1:]
            if len(hexval) == 6:
                return cls((0xFF << 24) | int(hexval, 16))
            if len(hexval) == 8:
                return cls(int(hexval, 16))
        raise ValueError(f"cannot parse color: {name!r}")

    # -- dunder -------------------------------------------------------------
    def __int__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, ARGB):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == (other & 0xFFFFFFFF)
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return (f"ARGB(0x{self.value:08X})  # a={self.alpha} "
                f"r={self.red} g={self.green} b={self.blue}")


# ---------------------------------------------------------------------------
# Geometry / color / bitwise utilities ported from the engine
# ---------------------------------------------------------------------------
def point_in_rect(x: int, y: int, rect: Rect) -> bool:
    """Port of the engine 'point-in-rect' helper."""
    return rect.contains_point(x, y)


def merge_rect(a: Rect, b: Rect) -> Rect:
    """Port of the engine 'merge rect' helper (union)."""
    return a.union(b)


def rect_from_side(left: int, top: int, right: int, bottom: int) -> Rect:
    """Build a Rect from a (left, top, right, bottom) box."""
    if right < left:
        left, right = right, left
    if bottom < top:
        top, bottom = bottom, top
    return Rect(left, top, right - left, bottom - top)


def mix_color(c1: ARGB, c2: ARGB, t: float) -> ARGB:
    """Linear blend between two colors, t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    inv = 1.0 - t
    r = int(c1.red * inv + c2.red * t)
    g = int(c1.green * inv + c2.green * t)
    b = int(c1.blue * inv + c2.blue * t)
    a = int(c1.alpha * inv + c2.alpha * t)
    return ARGB.from_rgba(r, g, b, a)


def invert_color(color: ARGB) -> ARGB:
    return ARGB.from_rgba(255 - color.red, 255 - color.green,
                          255 - color.blue, color.alpha)


def make_color(r: int, g: int, b: int, a: int = 255) -> ARGB:
    """Create an ARGB color from components (compatibility helper)."""
    return ARGB.from_rgba(r, g, b, a)


def make_color_ref(colorref: int, alpha: int = 255) -> ARGB:
    """Create an ARGB color from a GDI COLORREF."""
    return ARGB.from_colorref(colorref, alpha)


# ---------------------------------------------------------------------------
# Bitwise helpers (MAKELONG / LOWORD / HIWORD etc.)
# ---------------------------------------------------------------------------
def low_word(value: int) -> int:
    return value & 0xFFFF


def high_word(value: int) -> int:
    return (value >> 16) & 0xFFFF


def make_long(low: int, high: int) -> int:
    return (low & 0xFFFF) | ((high & 0xFFFF) << 16)


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


class Colors:
    """Common named colors, matching the previous public API."""
    Transparent = ARGB.from_rgba(0, 0, 0, 0)
    Black = ARGB.from_rgba(0, 0, 0)
    White = ARGB.from_rgba(255, 255, 255)
    Red = ARGB.from_rgba(255, 0, 0)
    Green = ARGB.from_rgba(0, 255, 0)
    Blue = ARGB.from_rgba(0, 0, 255)
    Yellow = ARGB.from_rgba(255, 255, 0)
    Cyan = ARGB.from_rgba(0, 255, 255)
    Magenta = ARGB.from_rgba(255, 0, 255)
    Gray = ARGB.from_rgba(128, 128, 128)
    DarkGray = ARGB.from_rgba(64, 64, 64)
    LightGray = ARGB.from_rgba(192, 192, 192)