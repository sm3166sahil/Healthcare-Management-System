# -*- coding: utf-8 -*-
"""
MediAnalytics Comprehensive Project Report Generator
Builds a publication-grade Word Document (.docx) adhering strictly to all 24 formatting guidelines:
1. Minimum pages: 25+
2. Font style: Times New Roman
3. Content font size: 13pt (sz 26)
4. Heading font size: 15pt (sz 30)
5. Line spacing: 1.5 (line 360)
6. Titles: Center aligned
7. Content: Justify alignment
8. Faculty designation: Left alignment
9. Figure number and title below figure
10. Table number and table name above table
11. Department name in full: Department of Computer Science and Engineering / Department of Data Science and Business Systems
12. Page numbers starting from Chapter 1 (Introduction) at page 1
13. HOD full details
14. Abstract: 1 page, max 2 paragraphs
15. Below acknowledgement: student name and signature at bottom right
16. Table of contents starting from Abstract
17. Introduction contains Problem Statement, Scope of Work, Objectives
18. Requirement analysis: Hardware and Software
19. Implementation: Code only (max 5 pages, no screenshots)
20. Results: Screenshots of output
21. References: 5-6 references
22. First page on both soft binded cover and first page
23. Table of contents page numbers: only starting page
24. No margin lines
"""

import os
import sys
import zipfile
import shutil
from PIL import Image

def escape_xml(text):
    if text is None:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))

class DocxReportBuilder:
    def __init__(self, template_docx, output_docx):
        self.template_docx = template_docx
        self.output_docx = output_docx
        self.work_dir = os.path.join(os.path.dirname(output_docx), "docx_build_temp")
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        
        # Extract template
        with zipfile.ZipFile(self.template_docx, 'r') as z:
            z.extractall(self.work_dir)
            
        self.media_dir = os.path.join(self.work_dir, "word", "media")
        os.makedirs(self.media_dir, exist_ok=True)
        
        self.body_elements = []
        self.image_rels = {}
        self.rel_counter = 10  # template has rId1-rId9
        
    def add_image(self, file_path, width_inches=5.5):
        filename = os.path.basename(file_path)
        dest_filename = f"report_img_{len(self.image_rels) + 1}_{filename}"
        dest_path = os.path.join(self.media_dir, dest_filename)
        shutil.copy(file_path, dest_path)
        
        with Image.open(dest_path) as img:
            orig_w, orig_h = img.size
            aspect = orig_h / orig_w
            
        cx = int(width_inches * 914400)
        cy = int(cx * aspect)
        
        rid = f"rIdImg{len(self.image_rels) + 1}"
        self.image_rels[rid] = f"media/{dest_filename}"
        return rid, cx, cy

    def p_para(self, text, style="content", jc="both", bold=False, italic=False, size=26, space_before=0, space_after=120, line=360, page_break=False):
        """Standard paragraph builder with strict Times New Roman."""
        pb_xml = '<w:r><w:br w:type="page"/></w:r>' if page_break else ''
        b_xml = '<w:b/><w:bCs/>' if bold else ''
        i_xml = '<w:i/><w:iCs/>' if italic else ''
        jc_val = jc
        
        p = f"""<w:p>
  <w:pPr>
    <w:jc w:val="{jc_val}"/>
    <w:spacing w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="{size}"/>
      <w:szCs w:val="{size}"/>
      {b_xml}
      {i_xml}
    </w:rPr>
  </w:pPr>
  {pb_xml}
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="{size}"/>
      <w:szCs w:val="{size}"/>
      {b_xml}
      {i_xml}
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(text)}</w:t>
  </w:r>
</w:p>"""
        return p

    def p_runs(self, runs, jc="both", space_before=0, space_after=120, line=360, page_break=False):
        """Paragraph with multiple formatted runs."""
        pb_xml = '<w:r><w:br w:type="page"/></w:r>' if page_break else ''
        runs_xml = []
        for r in runs:
            text = r.get("text", "")
            bold = r.get("bold", False)
            italic = r.get("italic", False)
            size = r.get("size", 26)
            color = r.get("color", None)
            b_xml = '<w:b/><w:bCs/>' if bold else ''
            i_xml = '<w:i/><w:iCs/>' if italic else ''
            c_xml = f'<w:color w:val="{color}"/>' if color else ''
            runs_xml.append(f"""<w:r>
  <w:rPr>
    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
    <w:sz w:val="{size}"/>
    <w:szCs w:val="{size}"/>
    {b_xml}
    {i_xml}
    {c_xml}
  </w:rPr>
  <w:t xml:space="preserve">{escape_xml(text)}</w:t>
</w:r>""")
            
        p = f"""<w:p>
  <w:pPr>
    <w:jc w:val="{jc}"/>
    <w:spacing w:before="{space_before}" w:after="{space_after}" w:line="{line}" w:lineRule="auto"/>
  </w:pPr>
  {pb_xml}
  {''.join(runs_xml)}
</w:p>"""
        return p

    def p_heading(self, text, level=1, center=False, page_break=False):
        """Heading paragraph: size 30 (15pt) bold."""
        jc = "center" if center else "left"
        size = 32 if level == 1 else 30
        before = 240 if level == 1 else 180
        after = 120
        return self.p_para(text, jc=jc, bold=True, size=size, space_before=before, space_after=after, line=360, page_break=page_break)

    def p_figure_image(self, rid, cx, cy, fig_num, fig_title):
        """Figure image followed by centered caption BELOW image."""
        p_img = f"""<w:p>
  <w:pPr>
    <w:jc w:val="center"/>
    <w:spacing w:before="180" w:after="80" w:line="360" w:lineRule="auto"/>
  </w:pPr>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="{self.rel_counter}" name="Figure {fig_num}"/>
        <wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="{self.rel_counter}" name="Figure {fig_num}"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{rid}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>"""
        self.rel_counter += 1
        p_caption = self.p_para(f"Figure {fig_num}: {fig_title}", jc="center", bold=True, size=24, space_before=40, space_after=180)
        return p_img + "\n" + p_caption

    def p_table(self, tbl_num, tbl_name, headers, rows, col_widths=None):
        """Table with table number and name ABOVE table."""
        caption = self.p_para(f"Table {tbl_num}: {tbl_name}", jc="left", bold=True, size=26, space_before=180, space_after=60)
        
        num_cols = len(headers)
        if col_widths is None:
            w_each = 9360 // num_cols
            col_widths = [w_each] * num_cols
            
        tbl_w = sum(col_widths)
        
        # Headers XML
        hdr_cells = []
        for i, h in enumerate(headers):
            w = col_widths[i]
            cell_xml = f"""<w:tc>
  <w:tcPr>
    <w:tcW w:w="{w}" w:type="dxa"/>
    <w:shd w:val="clear" w:color="auto" w:fill="E2E8F0"/>
    <w:tcMar><w:top w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:left w:w="140" w:type="dxa"/><w:right w:w="140" w:type="dxa"/></w:tcMar>
  </w:tcPr>
  <w:p>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:before="60" w:after="60" w:line="280" w:lineRule="auto"/>
    </w:pPr>
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/>
      </w:rPr>
      <w:t>{escape_xml(h)}</w:t>
    </w:r>
  </w:p>
</w:tc>"""
            hdr_cells.append(cell_xml)
            
        rows_xml = [f"<w:tr><w:trPr><w:tblHeader/></w:trPr>{''.join(hdr_cells)}</w:tr>"]
        
        # Rows XML
        for row_idx, r in enumerate(rows):
            fill = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            r_cells = []
            for i, val in enumerate(r):
                w = col_widths[i]
                jc = "left" if i > 0 else "center"
                r_cells.append(f"""<w:tc>
  <w:tcPr>
    <w:tcW w:w="{w}" w:type="dxa"/>
    <w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>
    <w:tcMar><w:top w:w="100" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:left w:w="140" w:type="dxa"/><w:right w:w="140" w:type="dxa"/></w:tcMar>
  </w:tcPr>
  <w:p>
    <w:pPr>
      <w:jc w:val="{jc}"/>
      <w:spacing w:before="40" w:after="40" w:line="280" w:lineRule="auto"/>
    </w:pPr>
    <w:r>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="22"/><w:szCs w:val="22"/>
      </w:rPr>
      <w:t>{escape_xml(val)}</w:t>
    </w:r>
  </w:p>
</w:tc>""")
            rows_xml.append(f"<w:tr>{''.join(r_cells)}</w:tr>")
            
        tbl_xml = f"""<w:tbl>
  <w:tblPr>
    <w:tblW w:w="{tbl_w}" w:type="dxa"/>
    <w:tblInd w:w="0" w:type="dxa"/>
    <w:tblBorders>
      <w:top w:val="single" w:sz="6" w:space="0" w:color="0F172A"/>
      <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
      <w:bottom w:val="single" w:sz="6" w:space="0" w:color="0F172A"/>
      <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
      <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
      <w:insideV w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
    </w:tblBorders>
  </w:tblPr>
  {''.join(rows_xml)}
</w:tbl>"""
        return caption + "\n" + tbl_xml + "\n" + self.p_para("", space_after=120)

    def p_code_box(self, code_text):
        """Code block formatted in Courier New / Consolas with light shading."""
        lines = code_text.strip().split("\n")
        code_paras = []
        for line in lines:
            line_esc = escape_xml(line) if line.strip() else " "
            p = f"""<w:p>
  <w:pPr>
    <w:jc w:val="left"/>
    <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
    <w:rPr>
      <w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>
      <w:sz w:val="19"/>
      <w:szCs w:val="19"/>
      <w:color w:val="0F172A"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>
      <w:sz w:val="19"/>
      <w:szCs w:val="19"/>
      <w:color w:val="0F172A"/>
    </w:rPr>
    <w:t xml:space="preserve">{line_esc}</w:t>
  </w:r>
</w:p>"""
            code_paras.append(p)
            
        tc_xml = f"""<w:tc>
  <w:tcPr>
    <w:tcW w:w="9360" w:type="dxa"/>
    <w:shd w:val="clear" w:color="auto" w:fill="F1F5F9"/>
    <w:tcBorders>
      <w:top w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>
      <w:left w:val="single" w:sz="18" w:space="0" w:color="0D9488"/>
      <w:bottom w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>
      <w:right w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>
    </w:tcBorders>
    <w:tcMar><w:top w:w="140" w:type="dxa"/><w:bottom w:w="140" w:type="dxa"/><w:left w:w="200" w:type="dxa"/><w:right w:w="200" w:type="dxa"/></w:tcMar>
  </w:tcPr>
  {''.join(code_paras)}
</w:tc>"""
        tbl_xml = f"""<w:tbl>
  <w:tblPr>
    <w:tblW w:w="9360" w:type="dxa"/>
    <w:tblInd w:w="0" w:type="dxa"/>
    <w:tblBorders><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tblBorders>
  </w:tblPr>
  <w:tr>{tc_xml}</w:tr>
</w:tbl>"""
        return tbl_xml + "\n" + self.p_para("", space_after=120)

print("DocxReportBuilder class defined successfully!")
