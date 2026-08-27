"""SDB-compatible in-memory resource bundle."""
from __future__ import annotations
import binascii
from dataclasses import dataclass

@dataclass
class Resource:
    name: str
    data: bytes
    type: str = 'data'
    resource_id: int | None = None

class ResourceBundle:
    def __init__(self): self._resources={}; self.password=None
    def add(self,name,data,resource_type='data',resource_id=None):
        self._resources[str(name)] = Resource(str(name), bytes(data), resource_type, resource_id); return self._resources[str(name)]
    def delete(self,name): return self._resources.pop(str(name),None) is not None
    def get(self,name,default=None):
        item=self._resources.get(str(name)); return item.data if item else default
    def names(self): return tuple(self._resources)
    def items(self): return tuple(self._resources.values())
    def crc32(self,name):
        data=self.get(name)
        if data is None: raise KeyError(name)
        return binascii.crc32(data) & 0xffffffff
    def clear(self): self._resources.clear()

SDB = ResourceBundle
