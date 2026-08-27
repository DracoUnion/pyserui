# -*- coding: utf-8 -*-
"""Thread-safe event delegates used by PySerUI."""
from __future__ import annotations

import inspect
import threading
from typing import Callable, List


class Delegate:
    """Multicast callback supporting ``+=`` and ``-=``.

    Handlers are invoked from a snapshot, so handlers may safely subscribe or
    unsubscribe during dispatch. Exceptions are re-raised by default; this
    makes UI callback failures visible instead of silently losing them.
    """
    def __init__(self, *, swallow_exceptions: bool = False):
        self._handlers: List[Callable] = []
        self._lock = threading.RLock()
        self.swallow_exceptions = swallow_exceptions

    @property
    def handlers(self):
        with self._lock:
            return tuple(self._handlers)

    def add(self, handler):
        if not callable(handler):
            raise TypeError("event handler must be callable")
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)
        return self

    def remove(self, handler):
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)
        return self

    def clear(self):
        with self._lock:
            self._handlers.clear()

    def invoke(self, *args, **kwargs):
        for handler in self.handlers:
            try:
                handler(*args, **kwargs)
            except Exception:
                if not self.swallow_exceptions:
                    raise

    __call__ = invoke

    def __iadd__(self, handler):
        return self.add(handler)

    def __isub__(self, handler):
        return self.remove(handler)

    def __len__(self):
        return len(self.handlers)


# Name retained for source compatibility with the original port.
SuiDelegate = Delegate


def invoke_compatible(handler, *args):
    """Invoke old callbacks that accept fewer positional arguments.

    This is intentionally opt-in and only used at compatibility boundaries;
    normal delegates still surface incorrect callback signatures.
    """
    try:
        return handler(*args)
    except TypeError as error:
        try:
            signature = inspect.signature(handler)
        except (TypeError, ValueError):
            raise error
        positional = [p for p in signature.parameters.values()
                      if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        if not any(p.kind == p.VAR_POSITIONAL for p in signature.parameters.values()):
            return handler(*args[:len(positional)])
        raise
