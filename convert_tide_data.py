#!/usr/bin/env python3
"""
Convert tide CSV data to hourly JSON format for PDF generation.

Process:
1. Read CSV file with tide extrema (up to 4 high/low tides per day)
2. Convert to hourly values using half-sine interpolation
3. Output JSON file for PDF generation

Input CSV format:
Date,Time1,Height1,Time2,Height2,Time3,Height3,Time4,Height4
2025-12-01,0107,1.1,0746,2.7,1400,1.1,2018,2.6

Output JSON format:
[
  {
    "Date": "2025-12-01",
    "00:00": 1.5,
    "01:00": 1.3,
    ...
    "23:00": 1.4
  },
  ...
]

Usage:
    python convert_tide_data.py input.csv output.json
"""

import csv
import json
import math
import sys
from datetime import datetime, timedelta

def parse_csv_to_extrema(csv_file):
    """
    Parse CSV file to list of tide extrema.

    Returns:
        List of extrema: [{"time": datetime, "height": float}, ...]
    """
    extrema = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            date_str = row['Date']

            # Skip example rows
            if date_str.startswith('EXAMPLE'):
                continue

            # Parse each extrema (up to 4 per day)
            for i in range(1, 5):
                time_key = f'Time{i}'
                height_key = f'Height{i}'

                time_val = row.get(time_key, '').strip()
                height_val = row.get(height_key, '').strip()

                if time_val and height_val:
                    # Parse time (HHMM format)
                    hour = int(time_val[:2])
                    minute = int(time_val[2:])

                    # Create datetime object
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    dt = dt.replace(hour=hour, minute=minute)

                    # Parse height
                    height = float(height_val)

                    extrema.append({
                        'time': dt,
                        'height': height
                    })

    # Sort by time
    extrema.sort(key=lambda x: x['time'])

    return extrema

def tide_height_between(t, t0, h0, t1, h1):
    """
    Half-sine interpolation between consecutive extrema.

    Args:
        t: Current time to calculate tide for
        t0: Time of previous extrema
        h0: Height at previous extrema
        t1: Time of next extrema
        h1: Height at next extrema

    Returns:
        Interpolated tide height in meters
    """
    if t <= t0:
        return h0
    if t >= t1:
        return h1

    # Calculate position between extrema (0 to 1)
    x = (t - t0).total_seconds() / (t1 - t0).total_seconds()

    # Half-sine interpolation
    s = 0.5 * (1 + math.sin(math.pi * x - math.pi / 2))

    return h0 + (h1 - h0) * s

def generate_hourly_tides(extrema):
    """
    Generate hourly tide levels from extrema data.

    Args:
        extrema: List of tide extrema with 'time' and 'height' keys

    Returns:
        List of daily tide data dictionaries
    """
    # Group by date
    daily_data = {}

    # Determine date range
    start = extrema[0]['time'].replace(hour=0, minute=0, second=0, microsecond=0)
    end = extrema[-1]['time'].replace(hour=23, minute=0, second=0, microsecond=0)

    # Generate hourly data
    t = start
    while t <= end:
        date_str = t.strftime("%Y-%m-%d")
        hour_str = t.strftime("%H:00")

        # Find the interpolated height for this hour
        for i in range(len(extrema) - 1):
            t0, h0 = extrema[i]['time'], extrema[i]['height']
            t1, h1 = extrema[i + 1]['time'], extrema[i + 1]['height']

            if t0 <= t <= t1:
                ht = tide_height_between(t, t0, h0, t1, h1)

                # Initialize day if needed
                if date_str not in daily_data:
                    daily_data[date_str] = {"Date": date_str}

                # Round to 1 decimal place
                daily_data[date_str][hour_str] = round(ht, 1)
                break

        t += timedelta(hours=1)

    # Convert to list format (sorted by date)
    return [daily_data[date] for date in sorted(daily_data.keys())]

def validate_output(daily_tides):
    """Validate the generated tide data."""
    issues = []

    for day in daily_tides:
        date = day.get("Date")

        # Check all 24 hours are present
        hours_present = len([k for k in day.keys() if k != "Date"])
        if hours_present != 24:
            issues.append(f"{date}: Only {hours_present}/24 hours present")

        # Check tide levels are in reasonable range (-0.5 to 4m for Singapore)
        for hour_str, level in day.items():
            if hour_str == "Date":
                continue
            if not (-0.5 <= level <= 4):
                issues.append(f"{date} {hour_str}: Unusual tide level {level}m")

    return issues

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_tide_data.py input.csv output.json")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_json = sys.argv[2]

    print("🌊 Tide Data Converter")
    print("=" * 60)
    print()

    # Step 1: Parse CSV to extrema
    print(f"📖 Reading CSV file: {input_csv}")
    extrema = parse_csv_to_extrema(input_csv)
    print(f"✅ Loaded {len(extrema)} tide extrema")

    if extrema:
        first_time = extrema[0]['time']
        last_time = extrema[-1]['time']
        print(f"📅 Date range: {first_time.date()} to {last_time.date()}")
        print()

    # Step 2: Generate hourly tides
    print(f"🔄 Generating hourly tide data...")
    daily_tides = generate_hourly_tides(extrema)
    print(f"✅ Generated {len(daily_tides)} days of hourly data")
    print()

    # Step 3: Validate output
    print(f"🔍 Validating output...")
    issues = validate_output(daily_tides)
    if issues:
        print(f"⚠️  Found {len(issues)} validation issues:")
        for issue in issues[:10]:
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")
    else:
        print(f"✅ Validation passed!")
    print()

    # Step 4: Write output
    print(f"💾 Writing to {output_json}...")
    with open(output_json, 'w') as f:
        json.dump(daily_tides, f, indent=2)

    print()
    print("=" * 60)
    print("🎉 SUCCESS!")
    print("=" * 60)
    print(f"📊 Generated: {len(daily_tides)} days of tide data")
    print(f"📁 Total hourly records: {len(daily_tides) * 24}")
    print(f"📄 Output file: {output_json}")
    print()
    print("📝 Next step:")
    print(f"   Run: python generate_tide_pdf.py {output_json} output.pdf")
    print()

if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
