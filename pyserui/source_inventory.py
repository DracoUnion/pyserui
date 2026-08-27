"""Inventory parser for the UTF-8 exported 易语言 source.

It deliberately extracts declarations only; it never executes source text.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass(frozen=True)
class Declaration:
    kind: str
    name: str
    signature: str
    line: int
    public: bool = False

_MARKERS = {'常量': 'constant', '全局变量': 'global', 'DLL命令': 'dll',
            '程序集': 'scope', '子程序': 'procedure'}

def load_source(path):
    return Path(path).read_text(encoding='utf-8-sig')

def inventory(path):
    result=[]
    for number, line in enumerate(load_source(path).splitlines(), 1):
        match=re.match(r'^\.(常量|全局变量|DLL命令|程序集|子程序)\s+([^,\s]+)(.*)$', line)
        if match:
            chinese, name, rest=match.groups()
            kind=_MARKERS[chinese]
            result.append(Declaration(kind,name,rest.strip(),number,'公开' in rest))
    return tuple(result)

def summarize(path):
    declarations=inventory(path)
    counts={kind: sum(d.kind==kind for d in declarations)
            for kind in set(d.kind for d in declarations)}
    return {'path': str(path), 'total': len(declarations), 'counts': counts,
            'public_procedures': tuple(d.name for d in declarations
                                       if d.kind=='procedure' and d.public)}
