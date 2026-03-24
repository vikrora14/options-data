# Example: Fetch and combine options data for all tickers
#
# This script shows two approaches:
#   1. Remote  – read every ticker directly from the hosted Parquet URLs
#      (no prior download needed, but requires an internet connection for each query)
#   2. Local   – load all files that were already downloaded with download.py / download.sh
#
# The two approaches use identical column schemas so you can swap one for the other
# without changing any downstream analysis code.

import os
import polars as pl

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


# ---------------------------------------------------------------------------
# Approach 1: read all options data directly from remote URLs
# ---------------------------------------------------------------------------

def fetch_all_remote(tickers=None, file="options.parquet"):
    """
    Return a single LazyFrame over every ticker's Parquet file on the CDN.

    Parameters
    ----------
    tickers : list[str] | None
        Subset of tickers to load.  Defaults to all tickers in ALL_TICKERS.
    file : str
        ``"options.parquet"`` (default) or ``"underlying.parquet"``.

    Returns
    -------
    polars.LazyFrame

    Notes
    -----
    Errors (e.g., 404, connection timeout) surface as Polars exceptions at
    ``.collect()`` time.  If a ticker fails, check the URL manually::

        https://static.philippdubach.com/data/options/<ticker>/<file>
    """
    tickers = tickers or ALL_TICKERS
    frames = []
    for t in tickers:
        url = f"{BASE_URL}/{t}/{file}"
        try:
            frames.append(pl.scan_parquet(url))
        except Exception as exc:
            raise RuntimeError(f"Failed to open remote data for ticker '{t}': {exc}") from exc
    return pl.concat(frames)


# ---------------------------------------------------------------------------
# Approach 2: load all locally-downloaded files (after running download.py)
# ---------------------------------------------------------------------------

def fetch_all_local(data_dir="./data", tickers=None, file="options.parquet"):
    """
    Return a single LazyFrame over every locally-downloaded Parquet file.

    Parameters
    ----------
    data_dir : str
        Root directory produced by ``download.py`` / ``download.sh``.
        Defaults to ``"./data"``.
    tickers : list[str] | None
        Subset of tickers to load.  ``None`` loads every ticker found on disk.
    file : str
        ``"options.parquet"`` (default) or ``"underlying.parquet"``.

    Returns
    -------
    polars.LazyFrame
    """
    tickers = tickers or ALL_TICKERS
    paths = [
        os.path.join(data_dir, t, file)
        for t in tickers
        if os.path.exists(os.path.join(data_dir, t, file))
    ]
    if not paths:
        raise FileNotFoundError(
            f"No '{file}' files found under '{data_dir}'. "
            "Run download.py first, or use fetch_all_remote()."
        )
    return pl.scan_parquet(paths)


# ---------------------------------------------------------------------------
# Demo – run this file directly to see a quick summary
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Pick a small sample so the demo finishes quickly
    sample = ["spy", "qqq", "tsla", "aapl", "nvda"]

    print("=== Remote fetch (sample: spy, qqq, tsla, aapl, nvda) ===")
    lf = fetch_all_remote(tickers=sample)

    # Lazy aggregation – only the final .collect() triggers network I/O
    summary = (
        lf.group_by("symbol")
        .agg(
            pl.len().alias("rows"),
            pl.col("date").min().alias("first_date"),
            pl.col("date").max().alias("last_date"),
        )
        .sort("symbol")
        .collect()
    )
    print(summary)

    print("\n=== Local fetch (all tickers present in ./data) ===")
    try:
        lf_local = fetch_all_local(data_dir="./data")
        count = lf_local.select(pl.len()).collect().item()
        print(f"Total rows across all local files: {count:,}")
    except FileNotFoundError as exc:
        print(f"Skipped – {exc}")
