#!/usr/bin/env python3
"""
Generate printable hourly tide table PDF from JSON data.

Automatically detects single month or multi-month data and formats accordingly.
- Single month: 1 page
- Multiple months: 1 page per month

Usage:
    python generate_tide_pdf.py input.json output.pdf [location]

Arguments:
    input.json  - JSON file from convert_tide_data.py
    output.pdf  - Output PDF filename
    location    - Optional location name (default: "TANJONG PAGAR")
"""

import json
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def load_tide_data(filename):
    """Load tide data from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def group_by_month(tide_data):
    """Group tide data by year-month."""
    months = {}
    for day in tide_data:
        date = day['Date']
        year_month = date[:7]  # YYYY-MM
        if year_month not in months:
            months[year_month] = []
        months[year_month].append(day)
    return months

def create_month_table(month_data):
    """Create a table for one month."""
    # Header row: Day, then hours 00-23
    header = ['Day'] + [f'{h:02d}' for h in range(24)]

    # Data rows
    data = [header]

    for day_data in month_data:
        date = day_data['Date']
        day = int(date.split('-')[2])

        # Row: day number, then tide levels for each hour
        row = [str(day)]
        for h in range(24):
            hour_key = f'{h:02d}:00'
            tide_level = day_data.get(hour_key, '')

            if tide_level != '':
                # Format: 1 decimal place
                row.append(f'{float(tide_level):.1f}')
            else:
                row.append('')

        data.append(row)

    return data

def generate_pdf(tide_data, output_file, location="TANJONG PAGAR"):
    """Generate PDF with tide tables."""

    # Use portrait A4
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        topMargin=8*mm,
        bottomMargin=5*mm,
        leftMargin=5*mm,
        rightMargin=5*mm
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=3,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    elements = []

    # Group data by month
    months_data = group_by_month(tide_data)
    month_names = {
        '01': 'JANUARY', '02': 'FEBRUARY', '03': 'MARCH', '04': 'APRIL',
        '05': 'MAY', '06': 'JUNE', '07': 'JULY', '08': 'AUGUST',
        '09': 'SEPTEMBER', '10': 'OCTOBER', '11': 'NOVEMBER', '12': 'DECEMBER'
    }

    # Generate tables for each month
    for i, (year_month, month_data) in enumerate(sorted(months_data.items())):
        year, month = year_month.split('-')
        month_name = month_names[month]

        # Title
        title = Paragraph(f'HOURLY TIDAL HEIGHTS', title_style)
        subtitle = Paragraph(f'{location}<br/>{month_name} {year}', subtitle_style)

        elements.append(title)
        elements.append(subtitle)

        # Create table data
        table_data = create_month_table(month_data)

        # Calculate column widths for portrait A4
        page_width = A4[0] - 10*mm  # Total width minus margins
        day_col_width = 8*mm
        hour_col_width = (page_width - day_col_width) / 24

        col_widths = [day_col_width] + [hour_col_width] * 24

        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Table styling
        style_commands = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 6.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
            ('TOPPADDING', (0, 0), (-1, 0), 1),

            # Day column
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 6),

            # Data cells
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 6),
            ('TOPPADDING', (1, 1), (-1, -1), 0.8),
            ('BOTTOMPADDING', (1, 1), (-1, -1), 0.8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 0.8, colors.black),
            ('LINEAFTER', (0, 0), (0, -1), 0.8, colors.black),
        ]

        table.setStyle(TableStyle(style_commands))

        elements.append(table)

        # Add footer note
        footer_text = Paragraph(
            f'Tide heights in meters relative to chart datum. '
            f'Generated from official tide predictions.',
            ParagraphStyle('Footer', fontSize=6.5, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(Spacer(1, 3*mm))
        elements.append(footer_text)

        # Add page break after each month except the last
        if i < len(months_data) - 1:
            elements.append(PageBreak())

        print(f'✅ Generated {month_name} {year}')

    # Build PDF
    doc.build(elements)

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_tide_pdf.py input.json output.pdf [location]")
        sys.exit(1)

    input_json = sys.argv[1]
    output_pdf = sys.argv[2]
    location = sys.argv[3] if len(sys.argv) > 3 else "TANJONG PAGAR"

    print('📊 Generating Tide Table PDF...\n')

    try:
        # Load data
        tide_data = load_tide_data(input_json)
        print(f'📈 Loaded {len(tide_data)} days of tide data\n')

        # Generate PDF
        print('🔄 Generating tide tables...\n')
        generate_pdf(tide_data, output_pdf, location)

        # Count months
        months = len(set(day['Date'][:7] for day in tide_data))

        print('\n🎉 PDF created successfully!')
        print(f'   📁 File: {output_pdf}')
        print(f'   📄 Pages: {months}')
        print(f'   🖨️  Ready to print!')
        print()

    except FileNotFoundError:
        print(f"❌ Error: {input_json} not found")
        print(f"\n📝 Please run conversion script first:")
        print(f"   python convert_tide_data.py input.csv {input_json}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
