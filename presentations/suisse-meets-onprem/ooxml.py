"""Tiny OOXML (.pptx) writer using only the Python standard library."""
import zipfile
from xml.sax.saxutils import escape

EMU = 914400
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FONT = "Arial"


def e(v):
    return int(round(v * EMU))


def fill_xml(color):
    return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>' if color else "<a:noFill/>"


def ln_xml(color=None, w=0.75, dash=None, tail=None):
    if not color:
        return "<a:ln><a:noFill/></a:ln>"
    d = f'<a:prstDash val="{dash}"/>' if dash else ""
    t = f'<a:tailEnd type="{tail}" w="med" len="med"/>' if tail else ""
    return f'<a:ln w="{int(w * 12700)}">{fill_xml(color)}{d}{t}</a:ln>'


def run(text, sz=14, color="000000", b=False, i=False, spc=None):
    attrs = f'lang="en-US" sz="{int(sz * 100)}"'
    if b:
        attrs += ' b="1"'
    if i:
        attrs += ' i="1"'
    if spc:
        attrs += f' spc="{spc}"'
    return (f'<a:r><a:rPr {attrs} dirty="0">{fill_xml(color)}'
            f'<a:latin typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr>'
            f'<a:t>{escape(text)}</a:t></a:r>')


def para(runs, algn="l", after=0, before=0, line=None, bullet=None, bullet_color=None, indent=0.18):
    if isinstance(runs, str):
        runs = [runs]
    ppr_attrs = f'algn="{algn}"'
    inner = ""
    if line:
        inner += f'<a:lnSpc><a:spcPct val="{int(line * 1000)}"/></a:lnSpc>'
    if before:
        inner += f'<a:spcBef><a:spcPts val="{int(before * 100)}"/></a:spcBef>'
    inner += f'<a:spcAft><a:spcPts val="{int(after * 100)}"/></a:spcAft>'
    if bullet:
        ppr_attrs += f' marL="{e(indent)}" indent="{-e(indent)}"'
        if bullet_color:
            inner += f'<a:buClr><a:srgbClr val="{bullet_color}"/></a:buClr>'
        inner += f'<a:buFont typeface="{FONT}"/><a:buChar char="{escape(bullet)}"/>'
    else:
        inner += "<a:buNone/>"
    # end-paragraph props keep empty-line heights sane
    return f'<a:p><a:pPr {ppr_attrs}>{inner}</a:pPr>{"".join(runs)}</a:p>'


class Slide:
    def __init__(self, bg="FFFFFF"):
        self.bg = bg
        self.shapes = []
        self.next_id = 2

    def _id(self):
        self.next_id += 1
        return self.next_id

    def shape(self, x, y, w, h, fill=None, line=None, line_w=0.75, dash=None, geom="rect",
              radius=None, paras=None, anchor="t", inset=(0, 0, 0, 0), name="Shape", textbox=False):
        sid = self._id()
        av = f'<a:gd name="adj" fmla="val {radius}"/>' if radius is not None else ""
        body = ""
        if paras is not None:
            l, t, r, b = inset
            body = (f'<p:txBody><a:bodyPr wrap="square" lIns="{e(l)}" tIns="{e(t)}" rIns="{e(r)}" '
                    f'bIns="{e(b)}" rtlCol="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr>'
                    f'<a:lstStyle/>{"".join(paras)}</p:txBody>')
        tb = ' txBox="1"' if textbox else ""
        self.shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{escape(name)} {sid}"/><p:cNvSpPr{tb}/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst>{av}</a:avLst></a:prstGeom>'
            f'{fill_xml(fill)}{ln_xml(line, line_w, dash)}</p:spPr>{body}</p:sp>')

    def text(self, x, y, w, h, paras, anchor="t", inset=(0, 0, 0, 0), name="Text"):
        self.shape(x, y, w, h, paras=paras, anchor=anchor, inset=inset, name=name, textbox=True)

    def arrow(self, x1, y1, x2, y2, color="888888", w=1.5, tail="triangle"):
        sid = self._id()
        flip = ""
        if x2 < x1:
            flip += ' flipH="1"'
        if y2 < y1:
            flip += ' flipV="1"'
        x, y = min(x1, x2), min(y1, y2)
        cx, cy = abs(x2 - x1), abs(y2 - y1)
        self.shapes.append(
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="Connector {sid}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flip}><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(cx)}" cy="{e(cy)}"/></a:xfrm>'
            f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>{ln_xml(color, w, None, tail)}</p:spPr></p:cxnSp>')

    def xml(self):
        return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:sld {NS}><p:cSld>'
                f'<p:bg><p:bgPr>{fill_xml(self.bg)}<a:effectLst/></p:bgPr></p:bg><p:spTree>'
                '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
                '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                + "".join(self.shapes) +
                '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def theme_xml(colors):
    c = colors
    def clr(name, val):
        return f'<a:{name}><a:srgbClr val="{val}"/></a:{name}>'
    scheme = (clr("dk1", c["dk1"]) + clr("lt1", "FFFFFF") + clr("dk2", c["dk2"]) + clr("lt2", c["lt2"]) +
              "".join(clr(f"accent{i + 1}", v) for i, v in enumerate(c["accents"])) +
              clr("hlink", c["accents"][0]) + clr("folHlink", c["accents"][1]))
    fonts = f'<a:latin typeface="{FONT}"/><a:ea typeface=""/><a:cs typeface=""/>'
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    ln = f'<a:ln w="9525" cap="flat" cmpd="sng" algn="ctr">{solid}<a:prstDash val="solid"/></a:ln>'
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="{c["name"]}">'
            f'<a:themeElements><a:clrScheme name="{c["name"]}">{scheme}</a:clrScheme>'
            f'<a:fontScheme name="{c["name"]}"><a:majorFont>{fonts}</a:majorFont><a:minorFont>{fonts}</a:minorFont></a:fontScheme>'
            f'<a:fmtScheme name="{c["name"]}"><a:fillStyleLst>{solid * 3}</a:fillStyleLst>'
            f'<a:lnStyleLst>{ln * 3}</a:lnStyleLst>'
            f'<a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>" * 3}</a:effectStyleLst>'
            f'<a:bgFillStyleLst>{solid * 3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements>'
            '<a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')


EMPTY_TREE = ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
              '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree>')


def write_pptx(path, slides, colors, title="Presentation", author=""):
    n = len(slides)
    hdr = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    ct = (hdr + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
          '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
          '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
          '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
          + "".join(f'<Override PartName="/ppt/slides/slide{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(n))
          + '</Types>')
    rels_root = (hdr + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="ppt/presentation.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                 f'<Relationship Id="rId3" Type="{REL}/extended-properties" Target="docProps/app.xml"/>'
                 '</Relationships>')
    core = (hdr + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{escape(title)}</dc:title><dc:creator>{escape(author)}</dc:creator>'
            '</cp:coreProperties>')
    app = (hdr + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           f'<Application>Microsoft Office PowerPoint</Application><Slides>{n}</Slides></Properties>')
    pres = (hdr + f'<p:presentation {NS} saveSubsetFonts="1">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
            '<p:sldIdLst>' + "".join(f'<p:sldId id="{256 + i}" r:id="rId{10 + i}"/>' for i in range(n)) + '</p:sldIdLst>'
            '<p:sldSz cx="12192000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>'
            '<p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>'
            '</p:presentation>')
    pres_rels = (hdr + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 f'<Relationship Id="rId1" Type="{REL}/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
                 f'<Relationship Id="rId2" Type="{REL}/theme" Target="theme/theme1.xml"/>'
                 f'<Relationship Id="rId3" Type="{REL}/presProps" Target="presProps.xml"/>'
                 f'<Relationship Id="rId4" Type="{REL}/viewProps" Target="viewProps.xml"/>'
                 f'<Relationship Id="rId5" Type="{REL}/tableStyles" Target="tableStyles.xml"/>'
                 + "".join(f'<Relationship Id="rId{10 + i}" Type="{REL}/slide" Target="slides/slide{i + 1}.xml"/>' for i in range(n))
                 + '</Relationships>')
    master = (hdr + f'<p:sldMaster {NS}><p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>'
              f'{EMPTY_TREE}</p:cSld>'
              '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
              'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
              '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
              '<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
    master_rels = (hdr + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   f'<Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                   f'<Relationship Id="rId2" Type="{REL}/theme" Target="../theme/theme1.xml"/></Relationships>')
    layout = (hdr + f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank">{EMPTY_TREE}</p:cSld>'
              '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
    layout_rels = (hdr + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   f'<Relationship Id="rId1" Type="{REL}/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
    slide_rels = (hdr + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  f'<Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')
    pres_props = hdr + f'<p:presentationPr {NS}/>'
    view_props = (hdr + f'<p:viewPr {NS}><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/>'
                  '</p:normalViewPr><p:gridSpacing cx="76200" cy="76200"/></p:viewPr>')
    table_styles = (hdr + '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                    'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels_root)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        z.writestr("ppt/slideMasters/slideMaster1.xml", master)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
        z.writestr("ppt/theme/theme1.xml", theme_xml(colors))
        z.writestr("ppt/presProps.xml", pres_props)
        z.writestr("ppt/viewProps.xml", view_props)
        z.writestr("ppt/tableStyles.xml", table_styles)
        for i, s in enumerate(slides):
            z.writestr(f"ppt/slides/slide{i + 1}.xml", s.xml())
            z.writestr(f"ppt/slides/_rels/slide{i + 1}.xml.rels", slide_rels)
