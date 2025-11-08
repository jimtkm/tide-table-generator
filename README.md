# Tide Table Generator

A Python tool for generating printable hourly tide tables from daily tide prediction data. Converts CSV tide extrema to interpolated hourly values and produces professional PDF tables.

## Features

- 📊 **Converts tide prediction data** from CSV format (daily high/low tide times) to hourly interpolated values
- 📄 **Generates printable PDFs** formatted for A4 paper with professional layout
- 🌊 **Half-sine interpolation** between tide extrema for accurate hourly predictions
- ✅ **Data validation** to ensure tide levels are within reasonable ranges
- 📅 **Auto-detects time period** - handles single month or multi-month data automatically
- 🖨️ **Print-ready format** optimized for easy reading

## Requirements

```bash
pip install reportlab
```

Python 3.6+ required (uses standard library for other dependencies)

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare your CSV file

Create a CSV file with tide prediction data:

```csv
Date,Time1,Height1,Time2,Height2,Time3,Height3,Time4,Height4
EXAMPLE-2025-12-01,0545,2.1,1215,0.7,1830,2.8,,
EXAMPLE-2025-12-02,0015,0.6,0630,2.2,1300,0.8,1915,2.7
2025-12-01,0107,1.1,0746,2.7,1400,1.1,2018,2.6
2025-12-02,0213,1.2,0826,2.8,1452,0.8,2128,2.7
```

**Format details:**
- `Date`: YYYY-MM-DD format
- `Time1-4`: High/low tide times in HHMM format (e.g., 0545 = 05:45)
- `Height1-4`: Tide heights in meters
- Example rows (starting with "EXAMPLE-") are ignored
- Empty columns for days with fewer than 4 tide extrema

### 3. Convert to hourly JSON

```bash
python convert_tide_data.py your_data.csv tide_data.json
```

This will:
- Read your CSV file
- Interpolate hourly tide levels using half-sine curves
- Validate the data
- Output JSON with 24 hourly values per day

### 4. Generate PDF

```bash
python generate_tide_pdf.py tide_data.json tide_table.pdf
```

Or specify a custom location:

```bash
python generate_tide_pdf.py tide_data.json tide_table.pdf "SENTOSA ISLAND"
```

This creates a print-ready PDF with:
- One month per page (portrait A4 layout)
- Day rows and hourly columns (00-23)
- Professional formatting optimized for readability
- Automatic detection of single or multi-month data

## How It Works

### 1. CSV Parsing
The converter reads daily tide extrema (high and low tides) from your CSV file.

### 2. Half-Sine Interpolation
Between consecutive tide extrema, the tool uses half-sine interpolation to estimate hourly tide levels:

```
s = 0.5 * (1 + sin(π * x - π / 2))
height = h0 + (h1 - h0) * s
```

Where:
- `x` is the position between extrema (0 to 1)
- `h0` is the height at the previous extremum
- `h1` is the height at the next extremum
- `s` is the interpolation factor

This method provides smooth, realistic tide curves between known high and low points.

### 3. Validation
The tool validates:
- All 24 hours are present for each day
- Tide levels are within reasonable range (-0.5m to 4m)
- Data continuity across days

### 4. PDF Generation
Uses ReportLab to create professional tables with:
- Compact font sizing (6-6.5pt) to fit all data on one page
- Grid lines and section separators for readability
- Minimal margins to maximize data density
- Automatic pagination for multi-month datasets

## Example Output

The generated PDF includes:
- **Header**: Location name and month/year
- **Table**: Day numbers (rows) × Hours 00-23 (columns)
- **Footer**: Data source information

Single month data generates 1 page. Multi-month data generates 1 page per month.

## Data Sources

This tool works with tide prediction data from official sources such as:
- National hydrographic offices
- Port authorities
- Maritime and Port Authority of Singapore (MPA)
- NOAA (US)
- UK Hydrographic Office

**Note**: Always use official tide predictions for operational planning. This tool is for formatting and presentation only.

## File Structure

```
tide-table-generator/
├── README.md                  # This file
├── convert_tide_data.py       # CSV to JSON converter
├── generate_tide_pdf.py       # JSON to PDF generator
├── template_example.csv       # Sample CSV format
├── requirements.txt           # Python dependencies
└── .gitignore                # Git ignore rules
```

## Command Line Arguments

### convert_tide_data.py
```bash
python convert_tide_data.py <input.csv> <output.json>
```

### generate_tide_pdf.py
```bash
python generate_tide_pdf.py <input.json> <output.pdf> [location]
```
- `location` is optional (default: "TANJONG PAGAR")

## Tips

- Use consistent date formats (YYYY-MM-DD) in your CSV
- Include example rows at the top of your CSV for reference
- Tide times should be in 24-hour HHMM format (e.g., 1430 not 2:30 PM)
- The tool automatically handles missing tide extrema (days with 2-4 tides)
- Output PDFs are optimized for A4 paper size

## License

MIT License - Free to use for personal and commercial purposes.

## Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your use cases

## Author

Created for marine operations and coastal management workflows.

## Acknowledgments

- ReportLab library for PDF generation
- Half-sine interpolation method commonly used in tidal analysis
