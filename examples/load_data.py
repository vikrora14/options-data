# Example: Load and analyze options data
import polars as pl

# Load SPY options directly from URL (or local file)
URL = "https://static.philippdubach.com/data/options/spy/options.parquet"
# df = pl.read_parquet(URL)  # Remote
df = pl.read_parquet("data/spy/options.parquet")  # Local

print(f"Loaded {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Columns: {df.columns}")

# Example: Average IV by expiration for calls
avg_iv = (
    df.filter(pl.col("type") == "call")
    .group_by("expiration")
    .agg(pl.col("implied_volatility").mean().alias("avg_iv"))
    .sort("expiration")
)
print("\nAverage IV by expiration (calls):")
print(avg_iv.head(10))
