#!/usr/bin/env python3
"""База ДТЕК Одеські електромережі (data/dtek_odesa.json: вулиця -> будинок -> черги) ->
data/rem/1.json та data/index.json у форматі, який читає сторінка і build_points.py.
Запуск: python3 scripts/build_addresses.py data/dtek_odesa.json data"""
import json, os, re, sys
from collections import defaultdict
src, out = sys.argv[1], sys.argv[2]
os.makedirs(f"{out}/rem", exist_ok=True)
d = json.load(open(src, encoding="utf-8"))
CITY = d.get("city", "м. Одеса")

# частини будинку (приміщення, квартира, офіс, секція, гараж): графік показуємо за будинком у цілому
SUB = re.compile(r"[/,\s]*(?:прим|при|пр|пом|квартира|кв|офіс|оф|секція|секц|сек|гараж|гар|каб|ком|літ|кафе|тп)\b\.?.*$", re.I)
KORP = re.compile(r"[/,\s]*(?:корпус|корп|кор|ко)\b\.?\s*(?=\d)", re.I)

def house(h):
    h = h.strip()
    if not h or h.lower() in ("б/н", "null", ".", "-"): return None
    h = SUB.sub("", h)
    h = KORP.sub(" корп.", h)
    h = re.sub(r"\s*[,;]\s*", "/", h)                  # коми не можна: ними розділено перелік будинків
    h = re.sub(r"/+", "/", h).strip("/ ")
    h = re.sub(r"^(\d+)[-/]([А-ЯІЇЄҐа-яіїєґA-Za-z])$", r"\1\2", h)
    h = re.sub(r"\s+", " ", h).upper().replace(" КОРП.", " корп.")
    return h or None

def hsort(h):
    m = re.match(r"\d+", h); return (0, int(m.group()), h) if m else (1, 0, h)

tree = defaultdict(lambda: defaultdict(set)); skipped = 0
for st, hs in d["streets"].items():
    st = re.sub(r"\s+", " ", st).strip()
    if not st or st.lower() == "без вулиці": skipped += len(hs); continue
    for h, groups in hs.items():
        h = house(h)
        if not h: skipped += 1; continue
        for g in groups.split(","):
            if re.fullmatch(r"\d\.\d", g): tree[st][g].add(h)
data = {CITY: {st: {g: ",".join(sorted(v, key=hsort)) for g, v in sorted(gs.items())} for st, gs in sorted(tree.items())}}
json.dump(data, open(f"{out}/rem/1.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump({"Одеса": {"file": "rem/1.json", "settlements": [CITY], "updated": d.get("collected", "")[:10]}},
          open(f"{out}/index.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
n = len({(st, h) for st, gs in tree.items() for v in gs.values() for h in v})
print(f"вулиць: {len(tree)}; будинків: {n}; пропущено записів: {skipped}")
