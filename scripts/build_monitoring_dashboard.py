"""Missing packaging capability only: print metadata, links and a same-view PDF.

Workbook values, formulas, styles and native chart are authored by artifact-tool.
No independent report content is authored for the PDF.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "reports/generated/monitoring_build"
XLSX = ROOT / "reports/strategy_dashboard.xlsx"
PDF = ROOT / "reports/strategy_dashboard.pdf"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("", NS)
ET.register_namespace("r", REL)


def xml(name: str) -> str:
    return f"{{{NS}}}{name}"


def source_rows():
    with (ROOT / "data/public/company_quarterly_metrics.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["metric_id"] == "M001"]
    return sorted(rows, key=lambda r: r["period_start"])


def cell_payload(sheet):
    return {c.attrib["r"]: (c.attrib.get("t"), c.findtext(xml("f")), c.findtext(xml("v")))
            for c in sheet.findall(f".//{xml('c')}")}


def prepare():
    """Set known OOXML print/link metadata without changing any cell content."""
    with zipfile.ZipFile(XLSX) as source:
        members = {name: source.read(name) for name in source.namelist()}
    before = {}
    rows = source_rows()
    for index, area in enumerate(["$B$2:$I$40", "$B$2:$I$30"], 1):
        name = f"xl/worksheets/sheet{index}.xml"
        sheet = ET.fromstring(members[name])
        before[name] = cell_payload(sheet)
        sheet_pr = sheet.find(xml("sheetPr"))
        if sheet_pr is None:
            sheet_pr = ET.Element(xml("sheetPr")); sheet.insert(0, sheet_pr)
        setup_pr = sheet_pr.find(xml("pageSetUpPr"))
        if setup_pr is None:
            setup_pr = ET.SubElement(sheet_pr, xml("pageSetUpPr"))
        setup_pr.set("fitToPage", "1")
        for child in list(sheet):
            if child.tag in [xml("printOptions"), xml("pageMargins"), xml("pageSetup")]:
                sheet.remove(child)
        insert_at = next((i for i, c in enumerate(list(sheet)) if c.tag in [xml("headerFooter"), xml("rowBreaks"), xml("colBreaks"), xml("drawing"), xml("legacyDrawing"), xml("extLst")]), len(sheet))
        print_options = ET.Element(xml("printOptions"), horizontalCentered="1", headings="0", gridLines="0")
        margins = ET.Element(xml("pageMargins"), left="0.25", right="0.25", top="0.22", bottom="0.28", header="0.1", footer="0.1")
        page_setup = ET.Element(xml("pageSetup"), paperSize="9", orientation="landscape", fitToWidth="1", fitToHeight="1")
        for offset, element in enumerate([print_options, margins, page_setup]):
            sheet.insert(insert_at + offset, element)
        if index == 1:
            links = sheet.find(xml("hyperlinks"))
            if links is None:
                links = ET.Element(xml("hyperlinks"))
                sheet.insert(list(sheet).index(print_options), links)
            rel_name = "xl/worksheets/_rels/sheet1.xml.rels"
            relationships = ET.fromstring(members[rel_name])
            for old in list(links):
                if old.attrib.get(f"{{{REL}}}id", "").startswith("rIdMonitoringSource"):
                    links.remove(old)
            for old in list(relationships):
                if old.attrib.get("Id", "").startswith("rIdMonitoringSource"):
                    relationships.remove(old)
            for i, row in enumerate(rows):
                rel_id = f"rIdMonitoringSource{i+1}"
                ET.SubElement(links, xml("hyperlink"), {"ref": f"D{24+i}", f"{{{REL}}}id": rel_id, "display": row["source_id"]})
                ET.SubElement(relationships, f"{{{PKG}}}Relationship", {"Id": rel_id, "Type": f"{REL}/hyperlink", "Target": row["source_url"], "TargetMode": "External"})
            members[rel_name] = ET.tostring(relationships, encoding="utf-8", xml_declaration=True)
        if cell_payload(sheet) != before[name]:
            raise ValueError("Print/link metadata changed worksheet values or formulas")
        members[name] = ET.tostring(sheet, encoding="utf-8", xml_declaration=True)
    book = ET.fromstring(members["xl/workbook.xml"])
    defined = book.find(xml("definedNames"))
    if defined is None:
        defined = ET.Element(xml("definedNames"))
        index = next((i for i, c in enumerate(list(book)) if c.tag == xml("calcPr")), len(book))
        book.insert(index, defined)
    for i, (sheet_name, area) in enumerate([("证据与就绪", "$B$2:$I$40"), ("未来KPI", "$B$2:$I$30")]):
        for element in list(defined):
            if element.attrib.get("name") == "_xlnm.Print_Area" and element.attrib.get("localSheetId") == str(i):
                defined.remove(element)
        item = ET.SubElement(defined, xml("definedName"), name="_xlnm.Print_Area", localSheetId=str(i))
        item.text = f"'{sheet_name}'!{area}"
    members["xl/workbook.xml"] = ET.tostring(book, encoding="utf-8", xml_declaration=True)
    tmp = QA / "monitoring_prepared.xlsx"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as target:
        for name, data in members.items():
            target.writestr(name, data)
    os.replace(tmp, XLSX)
    receipt = {"operation": "OOXML print metadata and hyperlinks only", "values_formulas_preserved": True,
               "print_areas": ["B2:I40", "B2:I30"], "source_hyperlinks": 8,
               "xlsx_sha256": hashlib.sha256(XLSX.read_bytes()).hexdigest()}
    (QA / "monitoring_packaging_qa.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Prepared 2 one-page print areas and 8 source links; cell content preserved.")


def make_pdf():
    from PIL import Image
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import A4, landscape
    from pypdf import PdfReader
    page_width, page_height = landscape(A4)
    canvas = Canvas(str(PDF), pagesize=(page_width, page_height), pageCompression=1)
    canvas.setTitle("Speaking / Video Call monitoring design v1.0")
    canvas.setAuthor("External public evidence analysis")
    images = [QA / "monitoring_evidence.png", QA / "monitoring_kpi.png"]
    image_info = []
    for index, image in enumerate(images):
        with Image.open(image) as content:
            width, height = content.size
        scale = min((page_width - 24) / width, (page_height - 24) / height)
        draw_width, draw_height = width * scale, height * scale
        left, bottom = (page_width - draw_width) / 2, (page_height - draw_height) / 2
        canvas.drawImage(str(image), left, bottom, width=draw_width, height=draw_height)
        if index == 0:
            # Link rectangles use the actual authoring pixel dimensions and row heights.
            with zipfile.ZipFile(XLSX) as book:
                sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
            row_heights = {int(r.attrib["r"]): float(r.attrib.get("ht", 13.5)) * 96 / 72
                           for r in sheet.findall(f".//{xml('row')}")}
            render_scale = width / 908  # A/J gutters 14px; B:I eight 110px columns.
            for i, row in enumerate(source_rows()):
                r = 24+i
                top_px = sum(row_heights.get(k, 18) for k in range(1, r)) * render_scale
                bottom_px = top_px + row_heights.get(r, 18) * render_scale
                x0 = left + 234 * render_scale * scale
                x1 = left + 344 * render_scale * scale
                y0 = bottom + (height - bottom_px) * scale
                y1 = bottom + (height - top_px) * scale
                canvas.linkURL(row["source_url"], (x0, y0, x1, y1), relative=0, thickness=0)
        canvas.showPage()
        image_info.append({"sheet": ["证据与就绪", "未来KPI"][index], "render_path": str(image.relative_to(ROOT)), "pixel_size": [width,height], "sha256": hashlib.sha256(image.read_bytes()).hexdigest()})
    canvas.save()
    pdf = PdfReader(PDF)
    if len(pdf.pages) != 2:
        raise ValueError("PDF must contain exactly two pages")
    with zipfile.ZipFile(XLSX) as book:
        s1 = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
        s2 = ET.fromstring(book.read("xl/worksheets/sheet2.xml"))
        s1_cells, s2_cells = cell_payload(s1), cell_payload(s2)
        for i,row in enumerate(source_rows()):
            if float(s1_cells[f"C{24+i}"][2]) != float(row["value"]):
                raise ValueError("DAU in final workbook differs from authoritative CSV")
        for address in ['D8','H8','D9','H9','D10','H10','D11','H11','D12','H12','D13','H13','D14','H14','D15','H15']:
            if s2_cells.get(address, (None,None,None))[2] is not None:
                raise ValueError(f"Final unknown planning input became populated: {address}")
        if len([n for n in book.namelist() if '/charts/chart' in n and n.endswith('.xml')]) != 1:
            raise ValueError('Native editable chart missing')
    receipt = {"pdf_pages": 2, "pdf_format": "A4 landscape", "pdf_creation_engine": "ReportLab wrapping actual final-XLSX artifact-tool sheet renders",
               "same_view_source": "Final saved XLSX reimported by artifact-tool; one full render per sheet",
               "images": image_info, "native_editable_chart_count": 1, "authoritative_dau_reconciled": 8,
               "all_16_planning_inputs_blank": True, "pdf_source_annotations": len(pdf.pages[0].get('/Annots', [])),
               "xlsx_sha256": hashlib.sha256(XLSX.read_bytes()).hexdigest(), "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
               "limitations": ["PDF is a raster snapshot; text/chart edits are performed in XLSX, not PDF.", "Excel native Save and PDF export were refused by the expired Office license; not claimed as successful."]}
    (QA / "monitoring_pdf_qa.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PDF verified: 2 pages, 8 actuals reconciled, all 16 planning inputs blank, native chart preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()
    QA.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare()
    if args.pdf:
        make_pdf()
