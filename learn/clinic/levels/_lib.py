"""Lets a level use your code from earlier levels: from _lib import level; book = level(3).book"""
import importlib.util, os, glob
_HERE = os.path.dirname(os.path.abspath(__file__)); _cache = {}
def level(n):
    if n not in _cache:
        d = glob.glob(os.path.join(_HERE, f"L{n:02d}_*"))[0]
        spec = importlib.util.spec_from_file_location(f"lvl{n}", os.path.join(d, "quest.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); _cache[n] = m
    return _cache[n]
