#!/usr/bin/env bash
set -euo pipefail

# Download US Equity Options Dataset
# Usage: ./download.sh [output_dir] [ticker1 ticker2 ...]
#
# Examples:
#   ./download.sh                    # Download all to ./data/
#   ./download.sh ./my_data          # Download all to ./my_data/
#   ./download.sh ./data spy aapl    # Download only SPY and AAPL

BASE_URL="https://static.philippdubach.com/data/options"

ALL_TICKERS=(
  aapl abbv abt acn adbe aig amd amgn amt amzn
  avgo axp ba bac bk bkng blk bmy brk.b c
  cat cl cmcsa cof cop cost crm csco cvs cvx
  de dhr dis duk emr fdx gd ge gild gm
  goog googl gs hd hon ibm intu isrg iwm jnj
  jpm ko lin lly lmt low ma mcd mdlz mdt
  met meta mmm mo mrk ms msft nee nflx nke
  now nvda orcl pep pfe pg pltr pm pypl qcom
  qqq rtx sbux schw so spg spy t tgt tmo
  tmus tsla txn uber unh unp ups usb v vix
  vz wfc wmt xom
)

# Parse arguments
output_dir="${1:-./data}"
shift || true

if [[ $# -gt 0 ]]; then
  tickers=("$@")
else
  tickers=("${ALL_TICKERS[@]}")
fi

echo "Downloading ${#tickers[@]} tickers to $output_dir"
echo "================================================"

mkdir -p "$output_dir"

for ticker in "${tickers[@]}"; do
  ticker_lower=$(echo "$ticker" | tr '[:upper:]' '[:lower:]')
  ticker_dir="$output_dir/$ticker_lower"
  mkdir -p "$ticker_dir"
  
  for file in options.parquet underlying.parquet; do
    url="$BASE_URL/$ticker_lower/$file"
    dest="$ticker_dir/$file"
    
    if [[ -f "$dest" ]]; then
      echo "[$ticker_lower] $file already exists, skipping"
      continue
    fi
    
    echo "[$ticker_lower] Downloading $file..."
    if curl -fSL --progress-bar "$url" -o "$dest"; then
      echo "[$ticker_lower] $file done"
    else
      echo "[$ticker_lower] $file failed (may not exist)"
      rm -f "$dest"
    fi
  done
done

echo ""
echo "Download complete!"
echo "Total size: $(du -sh "$output_dir" | cut -f1)"
