#!/usr/bin/env python3
"""Set Citation for one ticker in analysis/companies.csv.

Usage: python3 set_citation.py TICKER "Source: URL; Source: URL"
"""
import csv
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent / "analysis" / "companies.csv"


def main():
    ticker, citation = sys.argv[1], sys.argv[2]
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    hits = [r for r in rows if r["Ticker"] == ticker]
    assert hits, f"ticker not found: {ticker}"
    hits[0]["Citation"] = citation
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"cited {ticker}")


if __name__ == "__main__":
    main()
