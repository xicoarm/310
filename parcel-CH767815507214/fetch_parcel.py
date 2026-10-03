#!/usr/bin/env python3
"""Download every public record for one Aargau parcel.

Pulls the official ÖREB extract (PDF/JSON/XML) from the canton, every legal
document it links to (zoning plan, building regulations, protection zones,
...), the per-theme map images, and federal context data from geo.admin.ch
(parcel geometry, buildings from the GWR, noise, public transport, solar,
radon, hazards, elevation, aerial imagery).

Usage:  python3 fetch_parcel.py [EGRID] [E N]
Needs network access to api.geo.ag.ch, www.ag.ch, api3.geo.admin.ch,
wms.geo.admin.ch (and whatever hosts the ÖREB documents live on).
"""
import json
import pathlib
import re
import sys
import time
import urllib.parse

import requests
import xmltodict

try:  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EGRID = sys.argv[1] if len(sys.argv) > 1 else "CH767815507214"
E, N = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (2670029.816, 1246145.570)

OUT = pathlib.Path(__file__).resolve().parent
DOCS = OUT / "documents"
MAPS = OUT / "maps"
DATA = OUT / "data"
for d in (DOCS, MAPS, DATA):
    d.mkdir(exist_ok=True)

OEREB = "https://api.geo.ag.ch/v2/oereb"
GEOADMIN = "https://api3.geo.admin.ch/rest/services"
WMS = "https://wms.geo.admin.ch/"

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (parcel-research script)"
LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(msg)


def get(url, params=None, tries=3, timeout=120):
    for i in range(tries):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            log(f"  HTTP {r.status_code} for {r.url}")
            if r.status_code in (400, 403, 404, 500, 501):
                return None
        except requests.RequestException as e:
            log(f"  error {e.__class__.__name__}: {e} ({url})")
        time.sleep(2 ** (i + 1))
    return None


def slug(text, maxlen=90):
    text = re.sub(r"[^\w\-. ]+", "_", text, flags=re.UNICODE).strip(" ._")
    return re.sub(r"\s+", "_", text)[:maxlen] or "file"


def ext_from(resp, url):
    ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
    if m and "." in m.group(1):
        return pathlib.Path(urllib.parse.unquote(m.group(1))).suffix.lower()
    return {
        "application/pdf": ".pdf", "application/json": ".json", "text/html": ".html",
        "application/xml": ".xml", "text/xml": ".xml", "image/png": ".png",
        "image/jpeg": ".jpg", "application/zip": ".zip",
    }.get(ctype) or pathlib.Path(urllib.parse.urlparse(url).path).suffix.lower() or ".bin"


def strip_ns(node):
    """Drop XML namespace prefixes and xmlns attributes from xmltodict output."""
    if isinstance(node, dict):
        return {k.split(":")[-1]: strip_ns(v) for k, v in node.items() if not k.startswith("@xmlns")}
    if isinstance(node, list):
        return [strip_ns(v) for v in node]
    return node


def de(v):
    """Pick the German text out of an ÖREB multilingual value."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        if "Text" in v and not isinstance(v["Text"], (dict, list)):
            return v["Text"]
        for k in ("LocalisedText", "Text"):
            if k in v:
                return de(v[k])
        return ""
    if isinstance(v, list):
        for item in v:
            if isinstance(item, dict) and item.get("Language", "de") == "de":
                return de(item)
        return de(v[0]) if v else ""
    return str(v)


# --------------------------------------------------------------------------
# 1. ÖREB: EGRID lookup, extract in all formats
# --------------------------------------------------------------------------
log(f"== ÖREB extract for {EGRID}")
for fmt in ("json", "xml"):
    r = get(f"{OEREB}/getegrid/{fmt}/", {"EN": f"{E},{N}"})
    if r:
        (DATA / f"oereb_getegrid.{fmt}").write_bytes(r.content)

extract = {}
for fmt, params in (
    ("pdf", {"EGRID": EGRID, "LANG": "de"}),
    ("json", {"EGRID": EGRID, "LANG": "de", "GEOMETRY": "true", "WITHIMAGES": "true"}),
    ("xml", {"EGRID": EGRID, "LANG": "de", "GEOMETRY": "true"}),
):
    r = get(f"{OEREB}/extract/{fmt}/", params)
    if not r and fmt != "pdf":  # some servers reject the optional flags
        r = get(f"{OEREB}/extract/{fmt}/", {"EGRID": EGRID, "LANG": "de"})
    if r:
        target = OUT / f"OEREB_Auszug_{EGRID}.{fmt}"
        target.write_bytes(r.content)
        log(f"  saved {target.name} ({len(r.content):,} bytes)")
        if fmt == "json":
            extract = r.json()
        elif fmt == "xml" and not extract:
            extract = strip_ns(xmltodict.parse(r.content, process_namespaces=False))

# --------------------------------------------------------------------------
# 2. Walk the extract: restrictions, documents, map images
# --------------------------------------------------------------------------
def walk(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (k.split(":")[-1],))
    elif isinstance(node, list):
        for v in node:
            yield from walk(v, path)
    else:
        yield path, node


def find_key(node, key):
    """Yield every value stored under `key` (namespace-insensitive)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k.split(":")[-1] == key:
                yield v
            yield from find_key(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from find_key(v, key)


summary = {"egrid": EGRID, "restrictions": [], "documents": [], "real_estate": {}}
re_nodes = list(find_key(extract, "RealEstate"))
if re_nodes:
    rest = re_nodes[0] if isinstance(re_nodes[0], dict) else {}
    for k in ("Number", "IdentDN", "EGRID", "Canton", "MunicipalityName", "Municipality",
              "MunicipalityCode", "FosNr", "LandRegistryArea", "SubunitOfLandRegister"):
        for kk, vv in rest.items():
            if kk.split(":")[-1] == k:
                summary["real_estate"][k] = de(vv) if not isinstance(vv, (str, int, float)) else vv
    for kk, vv in rest.items():
        if kk.split(":")[-1] == "Type":
            summary["real_estate"]["Type"] = de(vv.get("Text") if isinstance(vv, dict) else vv)

for rol_list in find_key(extract, "RestrictionOnLandownership"):
    for rol in rol_list if isinstance(rol_list, list) else [rol_list]:
        if not isinstance(rol, dict):
            continue
        g = {k.split(":")[-1]: v for k, v in rol.items()}
        theme = g.get("Theme", {})
        theme = {k.split(":")[-1]: v for k, v in theme.items()} if isinstance(theme, dict) else {}
        subtheme = g.get("SubTheme")
        entry = {
            "theme": de(theme.get("Text")) or theme.get("Code", ""),
            "subtheme": de(subtheme.get("Text")) if isinstance(subtheme, dict) else (subtheme or ""),
            "legend": de(g.get("LegendText")),
            "type_code": g.get("TypeCode", ""),
            "lawstatus": de((g.get("Lawstatus") or {}).get("Text")) if isinstance(g.get("Lawstatus"), dict) else g.get("Lawstatus", ""),
            "area_share_m2": g.get("AreaShare"),
            "part_in_percent": g.get("PartInPercent"),
            "length_share_m": g.get("LengthShare"),
            "nr_of_points": g.get("NrOfPoints"),
            "office": de((g.get("ResponsibleOffice") or {}).get("Name")) if isinstance(g.get("ResponsibleOffice"), dict) else "",
        }
        summary["restrictions"].append(entry)

docs = {}
for doc_list in list(find_key(extract, "LegalProvisions")) + list(find_key(extract, "Document")):
    for doc in doc_list if isinstance(doc_list, list) else [doc_list]:
        if not isinstance(doc, dict):
            continue
        d = {k.split(":")[-1]: v for k, v in doc.items()}
        url = de(d.get("TextAtWeb"))
        if not url or not url.startswith("http"):
            continue
        docs.setdefault(url, {
            "url": url,
            "title": de(d.get("Title")),
            "abbreviation": de(d.get("Abbreviation")),
            "official_number": de(d.get("OfficialNumber")),
            "type": de((d.get("Type") or {}).get("Text")) if isinstance(d.get("Type"), dict) else de(d.get("Type")),
            "published_from": d.get("PublishedFromDate") or d.get("publishedFrom") or "",
        })

# Any other document-looking URL anywhere in the extract (general info, laws, ...)
for path, val in walk(extract):
    if isinstance(val, str) and val.startswith("http") and "TextAtWeb" in path and val not in docs:
        docs[val] = {"url": val, "title": "", "abbreviation": "", "official_number": "", "type": "", "published_from": ""}

log(f"== {len(summary['restrictions'])} restrictions, {len(docs)} linked documents")
for i, d in enumerate(docs.values(), 1):
    r = get(d["url"])
    if not r:
        d["saved_as"] = None
        continue
    name = slug(" ".join(x for x in (f"{i:02d}", d["abbreviation"], d["official_number"], d["title"]) if x))
    target = DOCS / (name + ext_from(r, d["url"]))
    target.write_bytes(r.content)
    d["saved_as"] = str(target.relative_to(OUT))
    log(f"  [{i}] {target.name} ({len(r.content):,} bytes)")
summary["documents"] = list(docs.values())

# Per-theme map images: embedded base64 (WITHIMAGES) or ReferenceWMS links
n_img = 0
for ref in find_key(extract, "ReferenceWMS"):
    url = de(ref)
    if url.startswith("http"):
        r = get(url)
        if r and r.headers.get("Content-Type", "").startswith("image"):
            n_img += 1
            (MAPS / f"oereb_theme_{n_img:02d}{ext_from(r, url)}").write_bytes(r.content)
log(f"  saved {n_img} ÖREB theme map images")

# --------------------------------------------------------------------------
# 3. geo.admin.ch: parcel geometry and federal context layers
# --------------------------------------------------------------------------
def identify(layers, geometry=None, gtype="esriGeometryPoint", tol=0, geom=False):
    geometry = geometry or f"{E},{N}"
    r = get(f"{GEOADMIN}/api/MapServer/identify", {
        "geometry": geometry, "geometryType": gtype, "layers": f"all:{layers}",
        "mapExtent": f"{E-500},{N-500},{E+500},{N+500}", "imageDisplay": "1000,1000,96",
        "tolerance": tol, "sr": "2056", "returnGeometry": str(geom).lower(),
        "geometryFormat": "geojson", "lang": "de",
    })
    return r.json().get("results", []) if r else []


log("== geo.admin.ch context")
fed = {}
parcel = identify("ch.kantone.cadastralwebmap-farbe", geom=True)
fed["parcel"] = parcel
ring = None
for p in parcel:
    attrs = p.get("properties") or p.get("attributes") or {}
    if attrs.get("egris_egrid") == EGRID or len(parcel) == 1:
        g = p.get("geometry") or {}
        coords = g.get("coordinates") or []
        if g.get("type") == "MultiPolygon" and coords:
            ring = coords[0][0]
        elif g.get("type") == "Polygon" and coords:
            ring = coords[0]
        elif "rings" in g:
            ring = g["rings"][0]
        break

if ring:
    xs, ys = [c[0] for c in ring], [c[1] for c in ring]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    # shoelace area, as a cross-check of the land register area
    fed["parcel_polygon_area_m2"] = round(abs(sum(
        ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1] for i in range(len(ring) - 1))) / 2, 1)
else:
    bbox = (E - 40, N - 40, E + 40, N + 40)
fed["bbox"] = bbox


def inside(x, y, poly):
    hit = False
    for i in range(len(poly) - 1):
        (x1, y1), (x2, y2) = poly[i][:2], poly[i + 1][:2]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


env = ",".join(f"{v:.2f}" for v in bbox)
buildings = identify("ch.bfs.gebaeude_wohnungs_register", env, "esriGeometryEnvelope", geom=True)
on_parcel = []
for b in buildings:
    g = b.get("geometry") or {}
    c = g.get("coordinates") or [None, None]
    if ring is None or (c[0] is not None and inside(c[0], c[1], ring)):
        on_parcel.append(b)
fed["gwr_buildings_on_parcel"] = on_parcel
fed["gwr_buildings_in_bbox"] = buildings
for b in on_parcel:
    egid = (b.get("properties") or b.get("attributes") or {}).get("egid") or b.get("featureId") or b.get("id")
    r = get(f"{GEOADMIN}/api/MapServer/ch.bfs.gebaeude_wohnungs_register/{b.get('featureId') or b.get('id')}",
            {"lang": "de", "geometryFormat": "geojson"})
    if r:
        (DATA / f"gwr_building_{egid}.json").write_bytes(r.content)

for key, layer in {
    "bauzonen_ch": "ch.are.bauzonen",
    "gemeinde": "ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill",
    "oev_gueteklasse": "ch.are.gueteklassen_oev",
    "strassenlaerm_tag": "ch.bafu.laerm-strassenlaerm_tag",
    "strassenlaerm_nacht": "ch.bafu.laerm-strassenlaerm_nacht",
    "bahnlaerm_tag": "ch.bafu.laerm-bahnlaerm_tag",
    "fluglaerm": "ch.bazl.laermbelastungskataster-zivilflugplaetze",
    "solar_daecher": "ch.bfe.solarenergie-eignung-daecher",
    "solar_fassaden": "ch.bfe.solarenergie-eignung-fassaden",
    "radon": "ch.bag.radonkarte",
    "oberflaechenabfluss": "ch.bafu.gefaehrdungskarte-oberflaechenabfluss",
    "hochwasser_showme": "ch.bafu.showme-gemeinden_hochwasser",
    "erdbeben_baugrundklassen": "ch.bafu.gefahren-baugrundklassen",
    "grundwasserschutz": "ch.bafu.grundwasserschutzzonen",
    "kbs_belastete_standorte": "ch.bafu.altlasten-kataster",
    "denkmal_isos": "ch.bak.bundesinventar-schuetzenswerte-ortsbilder",
    "mobilfunk": "ch.bakom.mobil-antennenstandorte-5g",
    "glasfaser": "ch.bakom.verfuegbarkeit-hochbreitband",
    "fernwaerme": "ch.bfe.thermische-netze",
    "waldreservate": "ch.bafu.waldreservate",
}.items():
    tol = 30 if key in ("solar_daecher", "solar_fassaden", "strassenlaerm_tag", "strassenlaerm_nacht", "bahnlaerm_tag") else 0
    fed[key] = identify(layer, tol=tol)
    log(f"  {key}: {len(fed[key])} hit(s)")

r = get(f"{GEOADMIN}/height", {"easting": E, "northing": N, "sr": 2056})
fed["height_m"] = r.json() if r else None

(DATA / "geoadmin_context.json").write_text(json.dumps(fed, ensure_ascii=False, indent=1), encoding="utf-8")

# Aerial photo, cadastral plan, national map and zoning around the parcel
pad = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) * 0.6 + 30
cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
views = {
    "near": (cx - pad, cy - pad, cx + pad, cy + pad),
    "wide": (cx - 600, cy - 600, cx + 600, cy + 600),
}
for name, layers in {
    "orthofoto": "ch.swisstopo.swissimage",
    "kataster": "ch.kantone.cadastralwebmap-farbe",
    "landeskarte": "ch.swisstopo.pixelkarte-farbe",
    "bauzonen": "ch.are.bauzonen",
}.items():
    for view, (x0, y0, x1, y1) in views.items():
        if name == "landeskarte" and view == "near":
            continue
        r = get(WMS, {
            "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetMap", "LAYERS": layers,
            "STYLES": "", "CRS": "EPSG:2056", "BBOX": f"{x0},{y0},{x1},{y1}",
            "WIDTH": 1400, "HEIGHT": 1400, "FORMAT": "image/png", "TRANSPARENT": "false",
        })
        if r and r.headers.get("Content-Type", "").startswith("image"):
            (MAPS / f"{name}_{view}.png").write_bytes(r.content)
            log(f"  map {name}_{view}.png")
(DATA / "map_views_bbox_lv95.json").write_text(json.dumps(views, indent=1), encoding="utf-8")
if ring:
    (DATA / "parcel_polygon_lv95.json").write_text(json.dumps(ring), encoding="utf-8")

# --------------------------------------------------------------------------
# 4. Extra public documents worth keeping next to the extract
# --------------------------------------------------------------------------
EXTRA = {
    "Widen_BNO_Stand_2014.pdf": "https://www.widen.ch/public/upload/assets/261/BNO_2014.pdf",
    "Widen_BNO_2011-07-12.pdf": "https://www.widen.ch/public/upload/assets/148/BNO_20110712.pdf",
    "Widen_BNO_Synopse_2011.pdf": "https://www.widen.ch/public/upload/assets/149/BNO_Synopse_20110712.pdf",
    "Kandidat_Verkaufsdoku_Pflanzerbachstrasse_88_Widen.pdf":
        "https://media2.homegate.ch/listings/v2/hgonif/4001955097/document/64ccfbcc15730a7058be2daa64b61fad.pdf",
}
extra_dir = OUT / "extra"
extra_dir.mkdir(exist_ok=True)
for name, url in EXTRA.items():
    r = get(url)
    if r:
        (extra_dir / name).write_bytes(r.content)
        log(f"  extra {name} ({len(r.content):,} bytes)")

# --------------------------------------------------------------------------
# 5. Manifest
# --------------------------------------------------------------------------
summary["federal"] = {
    "parcel_polygon_area_m2": fed.get("parcel_polygon_area_m2"),
    "n_buildings_on_parcel": len(on_parcel),
    "height": fed.get("height_m"),
}
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "fetch_log.txt").write_text("\n".join(LOG), encoding="utf-8")
log("== done")
