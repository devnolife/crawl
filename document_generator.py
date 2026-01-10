"""
Advanced Document Generator
Generate professional construction documents: RAB, Price Requests, Proposals, etc.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
import os


class DocumentGenerator:
    """
    Generate berbagai jenis dokumen konstruksi profesional
    - RAB (Rencana Anggaran Biaya)
    - Request Harga ke Supplier
    - Proposal Proyek
    - Server Cost Calculation
    - Comparison Reports
    """
    
    def __init__(self, output_dir="documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_rab_document(self, project_data: dict, material_data: list, 
                             labor_data: list, filename: str = None) -> str:
        """
        Generate RAB (Rencana Anggaran Biaya) document
        
        Args:
            project_data: Dict with project info
            material_data: List of material costs
            labor_data: List of labor costs
            filename: Output filename (auto-generated if None)
        """
        if filename is None:
            filename = f"RAB_{project_data.get('name', 'Project')}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        output_path = self.output_dir / filename
        
        # Create JavaScript code for docx generation
        js_code = self._generate_rab_js(project_data, material_data, labor_data, str(output_path))
        
        # Write to temp file and execute
        temp_js = self.output_dir / "temp_rab.js"
        with open(temp_js, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        try:
            result = subprocess.run(['node', str(temp_js)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✓ RAB document created: {output_path}")
                temp_js.unlink()  # Delete temp file
                return str(output_path)
            else:
                print(f"Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error generating document: {e}")
            return None
    
    def _generate_rab_js(self, project_data: dict, material_data: list, 
                        labor_data: list, output_path: str) -> str:
        """Generate JavaScript code for RAB document"""
        
        # Calculate totals
        total_material = sum(item.get('total_cost', 0) for item in material_data)
        total_labor = sum(item.get('total_cost', 0) for item in labor_data)
        overhead = (total_material + total_labor) * 0.15  # 15% overhead
        grand_total = total_material + total_labor + overhead
        
        # Format numbers
        def format_idr(amount):
            return f"Rp {amount:,.0f}".replace(',', '.')
        
        # Build material rows
        material_rows = []
        for i, item in enumerate(material_data, 1):
            qty = item.get('quantity', 0)
            unit = item.get('unit', 'unit')
            price = item.get('price', 0)
            total = item.get('total_cost', qty * price)
            
            material_rows.append(f"""
            new TableRow({{
              children: [
                new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ children: [new TextRun({{ text: "{i}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 3500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ children: [new TextRun({{ text: "{item.get('name', 'N/A')}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "{qty:,.2f} {unit}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(price)}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total)}", size: 20, bold: true }})] }})] }}),
              ]
            }})""")
        
        # Build labor rows
        labor_rows = []
        for i, item in enumerate(labor_data, 1):
            qty = item.get('quantity', 0)
            unit = item.get('unit', 'hari')
            price = item.get('daily_rate', 0)
            total = item.get('total_cost', qty * price)
            
            labor_rows.append(f"""
            new TableRow({{
              children: [
                new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ children: [new TextRun({{ text: "{i}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 3500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ children: [new TextRun({{ text: "{item.get('position', 'N/A')}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "{qty} {unit}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(price)}", size: 20 }})] }})] }}),
                new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                  children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total)}", size: 20, bold: true }})] }})] }}),
              ]
            }})""")
        
        js_template = f"""
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, WidthType, BorderStyle, ShadingType, HeadingLevel }} = require('docx');
const fs = require('fs');

const border = {{ style: BorderStyle.SINGLE, size: 1, color: "000000" }};
const borders = {{ top: border, bottom: border, left: border, right: border }};
const margins = {{ top: 80, bottom: 80, left: 120, right: 120 }};

const doc = new Document({{
  styles: {{
    default: {{ document: {{ run: {{ font: "Arial", size: 24 }} }} }},
    paragraphStyles: [
      {{ id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        run: {{ size: 32, bold: true, font: "Arial" }},
        paragraph: {{ spacing: {{ before: 240, after: 120 }}, alignment: AlignmentType.CENTER }} }},
      {{ id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        run: {{ size: 28, bold: true, font: "Arial" }},
        paragraph: {{ spacing: {{ before: 180, after: 120 }} }} }},
    ]
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 12240, height: 15840 }},
        margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
      }}
    }},
    children: [
      // Header
      new Paragraph({{ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("RENCANA ANGGARAN BIAYA (RAB)")]
      }}),
      
      new Paragraph({{ 
        spacing: {{ after: 240 }},
        alignment: AlignmentType.CENTER,
        children: [new TextRun({{ text: "Proyek: {project_data.get('name', 'N/A')}", size: 24 }})]
      }}),
      
      // Project Info
      new Paragraph({{ children: [new TextRun({{ text: "INFORMASI PROYEK", bold: true, size: 24 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "Nama Proyek: {project_data.get('name', 'N/A')}", size: 22 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "Lokasi: {project_data.get('location', 'N/A')}", size: 22 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "Luas Bangunan: {project_data.get('building_area', 0)} m²", size: 22 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "Tanggal: {datetime.now().strftime('%d %B %Y')}", size: 22 }})] }}),
      new Paragraph({{ spacing: {{ after: 240 }}, children: [new TextRun("")] }}),
      
      // Material Section
      new Paragraph({{ 
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("A. BIAYA MATERIAL")]
      }}),
      
      new Table({{
        width: {{ size: 100, type: WidthType.PERCENTAGE }},
        columnWidths: [800, 3500, 1500, 1500, 2060],
        rows: [
          // Header row
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "No", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 3500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Uraian", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Volume", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Harga Satuan", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Jumlah Harga", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
            ]
          }}),
          
          // Material rows
          {','.join(material_rows)},
          
          // Subtotal row
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins, columnSpan: 4,
                shading: {{ fill: "E6E6E6", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "SUBTOTAL MATERIAL:", bold: true, size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "E6E6E6", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total_material)}", bold: true, size: 20 }})] }})] }}),
            ]
          }}),
        ]
      }}),
      
      new Paragraph({{ spacing: {{ after: 240 }}, children: [new TextRun("")] }}),
      
      // Labor Section
      new Paragraph({{ 
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("B. BIAYA TENAGA KERJA")]
      }}),
      
      new Table({{
        width: {{ size: 100, type: WidthType.PERCENTAGE }},
        columnWidths: [800, 3500, 1500, 1500, 2060],
        rows: [
          // Header row
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "No", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 3500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Jenis Pekerjaan", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Volume", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 1500, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Upah/Hari", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "0066CC", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.CENTER, children: [new TextRun({{ text: "Jumlah", bold: true, color: "FFFFFF", size: 20 }})] }})] }}),
            ]
          }}),
          
          // Labor rows
          {','.join(labor_rows)},
          
          // Subtotal row
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 800, type: WidthType.DXA }}, borders, margins, columnSpan: 4,
                shading: {{ fill: "E6E6E6", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "SUBTOTAL TENAGA KERJA:", bold: true, size: 20 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "E6E6E6", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total_labor)}", bold: true, size: 20 }})] }})] }}),
            ]
          }}),
        ]
      }}),
      
      new Paragraph({{ spacing: {{ after: 240 }}, children: [new TextRun("")] }}),
      
      // Summary
      new Paragraph({{ 
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("C. REKAPITULASI")]
      }}),
      
      new Table({{
        width: {{ size: 100, type: WidthType.PERCENTAGE }},
        columnWidths: [7300, 2060],
        rows: [
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 7300, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ children: [new TextRun({{ text: "Total Material", size: 22 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total_material)}", size: 22 }})] }})] }}),
            ]
          }}),
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 7300, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ children: [new TextRun({{ text: "Total Tenaga Kerja", size: 22 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(total_labor)}", size: 22 }})] }})] }}),
            ]
          }}),
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 7300, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ children: [new TextRun({{ text: "Overhead & Profit (15%)", size: 22 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(overhead)}", size: 22 }})] }})] }}),
            ]
          }}),
          new TableRow({{
            children: [
              new TableCell({{ width: {{ size: 7300, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "FFD700", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ children: [new TextRun({{ text: "TOTAL ANGGARAN", bold: true, size: 24 }})] }})] }}),
              new TableCell({{ width: {{ size: 2060, type: WidthType.DXA }}, borders, margins,
                shading: {{ fill: "FFD700", type: ShadingType.CLEAR }},
                children: [new Paragraph({{ alignment: AlignmentType.RIGHT, children: [new TextRun({{ text: "{format_idr(grand_total)}", bold: true, size: 24 }})] }})] }}),
            ]
          }}),
        ]
      }}),
      
      new Paragraph({{ spacing: {{ before: 480, after: 120 }}, children: [new TextRun("")] }}),
      
      // Footer notes
      new Paragraph({{ children: [new TextRun({{ text: "Catatan:", bold: true, size: 22 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "1. Harga dapat berubah sewaktu-waktu sesuai kondisi pasar", size: 20 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "2. Estimasi ini belum termasuk PPN dan biaya tak terduga lainnya", size: 20 }})] }}),
      new Paragraph({{ children: [new TextRun({{ text: "3. Untuk perhitungan final, mohon konfirmasi harga dengan supplier", size: 20 }})] }}),
      
      new Paragraph({{ spacing: {{ before: 480 }}, children: [new TextRun("")] }}),
      
      new Paragraph({{ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({{ text: "{project_data.get('location', 'Lokasi')}, {datetime.now().strftime('%d %B %Y')}", size: 22 }})]
      }}),
      new Paragraph({{ 
        spacing: {{ after: 960 }},
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({{ text: "Hormat kami,", size: 22 }})]
      }}),
      new Paragraph({{ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({{ text: "({project_data.get('prepared_by', 'Tim Estimator')})", size: 22, bold: true }})]
      }}),
    ]
  }}]
}});

Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync("{output_path}", buffer);
  console.log("Document created successfully");
}}).catch(err => {{
  console.error("Error:", err);
  process.exit(1);
}});
"""
        
        return js_template

# Continuing in next file due to length...
