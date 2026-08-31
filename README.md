# indian-ipos

Study of recent Indian IPOs. Covers 307 listed companies.

## Data

`analysis/companies.csv` holds the full dataset. One row per company.

Columns:

- Ticker
- Company
- BusinessModel
- RevenueStreams
- Expenses
- TAM
- PL_Top3_Contributors

Some fields say "data not found". Sources lacked those numbers.

## Browse

Open [`analysis/companies.md`](analysis/companies.md) to read all companies
as tables. GitHub renders it. A table of contents at the top jumps to each
letter. Each ticker links to a full report under `analysis/reports/`.

Script `make_docs.py` builds that file from `companies.csv`. Run:

    python3 make_docs.py

Edit the CSV, then rebuild. Do not edit the Markdown file by hand.

## License

See LICENSE.
