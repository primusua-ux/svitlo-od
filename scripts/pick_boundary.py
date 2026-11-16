#!/usr/bin/env python3
"""З GeoJSON адміністративних меж вибирає межу міста Одеса і пише її окремим файлом для osmium extract -p.
Запуск: python3 scripts/pick_boundary.py /tmp/b.geojson /tmp/odesa.geojson"""
import json, sys
src, out = sys.argv[1], sys.argv[2]
WANT = ["Одеса", "Одеська міська громада", "Одеська міська територіальна громада"]
best = None; names = []
for f in json.load(open(src, encoding="utf-8"))["features"]:
    t = f.get("properties", {}); g = f.get("geometry") or {}
    if g.get("type") not in ("Polygon", "MultiPolygon"): continue
    nm = t.get("name:uk") or t.get("name") or ""; names.append(f"{nm} (admin_level={t.get('admin_level')})")
    if nm in WANT and (best is None or WANT.index(nm) < WANT.index(best[0])): best = (nm, f)
if not best:
    print("Межу Одеси не знайдено. Є такі межі:", "; ".join(sorted(set(names)))); sys.exit(1)
json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": best[1]["geometry"]}]}, open(out, "w"))
print("межа:", best[0], "admin_level", best[1]["properties"].get("admin_level"))
