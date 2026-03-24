# US Equity Options Dataset

Historical options chain data for 104 major US equities and ETFs, from 2008 to December 2025.

## Download

Data is hosted on Cloudflare R2 and available for free download.

**Base URL:** `https://static.philippdubach.com/data/options/`

### Quick Download (Python)

```python
import urllib.request

ticker = "spy"  # lowercase
urllib.request.urlretrieve(
    f"https://static.philippdubach.com/data/options/{ticker}/options.parquet",
    f"{ticker}_options.parquet"
)
```

### Download All (Shell)

```bash
# Download script included in this repo
./download.sh

# Or download a single ticker
curl -O "https://static.philippdubach.com/data/options/spy/options.parquet"
```

### Download All (Python, with parallel workers)

```bash
# Download all 104 tickers sequentially (default)
python download.py

# Download all 104 tickers using 8 parallel workers (~8× faster)
python download.py --parallel 8

# Download specific tickers in parallel
python download.py -p 4 spy qqq tsla aapl nvda

# List available tickers
python download.py --list
```

### Direct URLs

Each ticker has two files:
- `https://static.philippdubach.com/data/options/<ticker>/options.parquet` - Options chain data
- `https://static.philippdubach.com/data/options/<ticker>/underlying.parquet` - Underlying price data

## Available Tickers

104 symbols covering major US equities and ETFs:

```
aapl  abbv  abt   acn   adbe  aig   amd   amgn  amt   amzn
avgo  axp   ba    bac   bk    bkng  blk   bmy   brk.b c
cat   cl    cmcsa cof   cop   cost  crm   csco  cvs   cvx
de    dhr   dis   duk   emr   fdx   gd    ge    gild  gm
goog  googl gs    hd    hon   ibm   intu  isrg  iwm   jnj
jpm   ko    lin   lly   lmt   low   ma    mcd   mdlz  mdt
met   meta  mmm   mo    mrk   ms    msft  nee   nflx  nke
now   nvda  orcl  pep   pfe   pg    pltr  pm    pypl  qcom
qqq   rtx   sbux  schw  so    spg   spy   t     tgt   tmo
tmus  tsla  txn   uber  unh   unp   ups   usb   v     vix
vz    wfc   wmt   xom
```

## Data Format

### options.parquet

| Column | Type | Description |
|--------|------|-------------|
| `contract_id` | string | Unique contract identifier |
| `symbol` | string | Underlying ticker |
| `expiration` | date | Option expiration date |
| `strike` | float | Strike price |
| `type` | string | `call` or `put` |
| `last` | float | Last traded price |
| `mark` | float | Mid price (bid+ask)/2 |
| `bid` | float | Bid price |
| `bid_size` | int | Bid size |
| `ask` | float | Ask price |
| `ask_size` | int | Ask size |
| `volume` | int | Daily volume |
| `open_interest` | int | Open interest |
| `date` | date | Quote date |
| `implied_volatility` | float | IV |
| `delta` | float | Delta |
| `gamma` | float | Gamma |
| `theta` | float | Theta |
| `vega` | float | Vega |
| `rho` | float | Rho |
| `in_the_money` | bool | ITM flag |

### underlying.parquet

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | string | Ticker |
| `date` | date | Trading date |
| `open` | float | Open price |
| `high` | float | High price |
| `low` | float | Low price |
| `close` | float | Close price |
| `adjusted_close` | float | Adjusted close |
| `volume` | int | Volume |
| `dividend_amount` | float | Dividend |
| `split_coefficient` | float | Split factor |

## Usage Examples

### Python (polars) – fetch all tickers at once

```python
# examples/fetch_all_data.py demonstrates two approaches:

# 1. Remote – no download needed
from examples.fetch_all_data import fetch_all_remote
lf = fetch_all_remote()                          # all 104 tickers
lf_subset = fetch_all_remote(["spy", "qqq"])     # specific tickers

# 2. Local – after running download.py
from examples.fetch_all_data import fetch_all_local
lf = fetch_all_local(data_dir="./data")

# Both return a polars LazyFrame – filter before collecting to save memory
df = lf.filter(pl.col("date") == "2025-12-16").collect()
```

### Python (pandas)

```python
import pandas as pd

# Load options data
df = pd.read_parquet("spy_options.parquet")

# Filter to calls expiring in 30 days
from datetime import datetime, timedelta
target_exp = datetime.now() + timedelta(days=30)
calls = df[(df['type'] == 'call') & (df['expiration'] <= target_exp)]
```

### Python (polars)

```python
import polars as pl

# Load directly from URL
df = pl.read_parquet("https://static.philippdubach.com/data/options/spy/options.parquet")

# Compute average IV by expiration
df.group_by("expiration").agg(pl.col("implied_volatility").mean())
```

### DuckDB

```sql
-- Query directly from URL
SELECT expiration, AVG(implied_volatility) as avg_iv
FROM 'https://static.philippdubach.com/data/options/spy/options.parquet'
WHERE type = 'call'
GROUP BY expiration
ORDER BY expiration;
```

## Data Size

| Ticker | Options Size | Rows |
|--------|-------------|------|
| SPY | 608 MB | 24.7M |
| QQQ | 384 MB | ~15M |
| TSLA | 289 MB | ~12M |
| Total | ~9.4 GB | ~200M |

## Date Coverage

- **Start:** January 2, 2008
- **End:** December 16, 2025

## License

This dataset is provided for educational and research purposes. The underlying data is sourced from public market data.

## Acknowledgments

Data processed and hosted by [Philipp Dubach](https://philippdubach.com).
