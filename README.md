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

## Batches

`analysis/batches/` holds working files.

- `tickers.txt` lists all 307 tickers.
- `batch_XX` files split tickers into groups.
- `csv_XX.csv` files hold results for each group.
- Merge them to build `companies.csv`.

## License

See LICENSE.
