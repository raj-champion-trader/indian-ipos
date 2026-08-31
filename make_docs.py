#!/usr/bin/env python3
"""Build analysis/companies.md from analysis/companies.csv.

companies.csv stays the single source of truth. Never edit the Markdown
file by hand — rerun this script after changing the CSV.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "analysis" / "companies.csv"
OUT_PATH = ROOT / "analysis" / "companies.md"

COLUMNS = [
    ("Ticker", "Ticker"),
    ("Company", "Company"),
    ("BusinessModel", "Business model"),
    ("RevenueStreams", "Revenue streams"),
    ("Expenses", "Expenses"),
    ("TAM", "TAM"),
    ("PL_Top3_Contributors", "Top 3 P&L contributors"),
]


def cell(text):
    # ponytail: pipe/newline escape only; GitHub tables need nothing fancier
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def ticker_cell(ticker):
    report = ROOT / "analysis" / "reports" / f"{ticker}.md"
    return f"[{ticker}](reports/{ticker}.md)" if report.exists() else ticker


def main():
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    groups = defaultdict(list)
    for row in rows:
        groups[(row["Ticker"] or "?")[0].upper()].append(row)

    lines = [
        "# Indian IPOs — Company Notes",
        "",
        f"{len(rows)} companies. Generated from `companies.csv` — do not edit by hand.",
        "Run `python3 make_docs.py` to rebuild.",
        "",
        "## Contents",
        "",
    ]
    lines += [f"- [{letter}](#{letter.lower()})" for letter in sorted(groups)]
    lines.append("")

    for letter in sorted(groups):
        lines.append(f"## {letter}")
        lines.append("")
        lines.append("| " + " | ".join(head for _, head in COLUMNS) + " |")
        lines.append("|" + "|".join([" --- "] * len(COLUMNS)) + "|")
        for row in groups[letter]:
            values = [ticker_cell(row["Ticker"])] + [
                cell(row[key]) for key, _ in COLUMNS[1:]
            ]
            lines.append("| " + " | ".join(values) + " |")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    assert sum(len(g) for g in groups.values()) == len(rows), "grouping lost rows"
    print(f"wrote {OUT_PATH.name}: {len(rows)} rows, {len(groups)} sections")


if __name__ == "__main__":
    main()
