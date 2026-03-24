"""
Download US Equity Options Dataset

Usage:
    python download.py                           # Download all tickers (sequential)
    python download.py spy aapl tsla             # Download specific tickers
    python download.py --output ./my_data        # Custom output directory
    python download.py --parallel 8              # Download with 8 parallel workers
    python download.py -p 4 spy aapl tsla        # Download 3 tickers with 4 workers
"""

import argparse
import os
import urllib.request
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://static.philippdubach.com/data/options"

ALL_TICKERS = [
    "aapl", "abbv", "abt", "acn", "adbe", "aig", "amd", "amgn", "amt", "amzn",
    "avgo", "axp", "ba", "bac", "bk", "bkng", "blk", "bmy", "brk.b", "c",
    "cat", "cl", "cmcsa", "cof", "cop", "cost", "crm", "csco", "cvs", "cvx",
    "de", "dhr", "dis", "duk", "emr", "fdx", "gd", "ge", "gild", "gm",
    "goog", "googl", "gs", "hd", "hon", "ibm", "intu", "isrg", "iwm", "jnj",
    "jpm", "ko", "lin", "lly", "lmt", "low", "ma", "mcd", "mdlz", "mdt",
    "met", "meta", "mmm", "mo", "mrk", "ms", "msft", "nee", "nflx", "nke",
    "now", "nvda", "orcl", "pep", "pfe", "pg", "pltr", "pm", "pypl", "qcom",
    "qqq", "rtx", "sbux", "schw", "so", "spg", "spy", "t", "tgt", "tmo",
    "tmus", "tsla", "txn", "uber", "unh", "unp", "ups", "usb", "v", "vix",
    "vz", "wfc", "wmt", "xom",
]


def download_file(url: str, dest: str) -> bool:
    """Download a file with progress indicator."""
    try:
        def progress(block_num, block_size, total_size):
            if total_size > 0:
                pct = min(100, block_num * block_size * 100 // total_size)
                print(f"\r  Progress: {pct}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, dest, reporthook=progress)
        print()  # newline after progress
        return True
    except Exception as e:
        print(f"\n  Error: {e}")
        return False


def download_ticker(ticker: str, output_dir: str) -> None:
    """Download options and underlying data for a ticker."""
    ticker = ticker.lower()
    ticker_dir = os.path.join(output_dir, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    
    for filename in ["options.parquet", "underlying.parquet"]:
        dest = os.path.join(ticker_dir, filename)
        if os.path.exists(dest):
            print(f"[{ticker}] {filename} already exists, skipping")
            continue
        
        url = f"{BASE_URL}/{ticker}/{filename}"
        print(f"[{ticker}] Downloading {filename}...")
        
        if download_file(url, dest):
            print(f"[{ticker}] {filename} done")
        else:
            print(f"[{ticker}] {filename} failed")
            if os.path.exists(dest):
                os.remove(dest)


def download_ticker_parallel(args):
    """Wrapper for download_ticker used in parallel execution."""
    ticker, output_dir = args
    download_ticker(ticker, output_dir)


def main():
    parser = argparse.ArgumentParser(description="Download US Equity Options Dataset")
    parser.add_argument("tickers", nargs="*", help="Tickers to download (default: all)")
    parser.add_argument("--output", "-o", default="./data", help="Output directory")
    parser.add_argument("--list", "-l", action="store_true", help="List available tickers")
    parser.add_argument(
        "--parallel", "-p",
        type=int,
        default=1,
        metavar="WORKERS",
        help="Number of parallel download workers (default: 1, sequential)",
    )
    args = parser.parse_args()

    if args.list:
        print("Available tickers:")
        for i, t in enumerate(ALL_TICKERS):
            print(f"  {t:8}", end="" if (i + 1) % 10 else "\n")
        print()
        return

    tickers = args.tickers if args.tickers else ALL_TICKERS
    valid_tickers = [t for t in tickers if t.lower() in ALL_TICKERS]
    skipped = [t for t in tickers if t.lower() not in ALL_TICKERS]

    for t in skipped:
        print(f"[{t}] Unknown ticker, skipping")

    print(f"Downloading {len(valid_tickers)} tickers to {args.output}")
    print("=" * 50)

    os.makedirs(args.output, exist_ok=True)

    if args.parallel > 1:
        print(f"Using {args.parallel} parallel workers")
        print()
        worker_args = [(t, args.output) for t in valid_tickers]
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            futures = {
                executor.submit(download_ticker_parallel, a): a[0]
                for a in worker_args
            }
            for future in as_completed(futures):
                future.result()  # propagate any unexpected exceptions
    else:
        for ticker in valid_tickers:
            download_ticker(ticker, args.output)

    print("\nDownload complete!")


if __name__ == "__main__":
    main()
