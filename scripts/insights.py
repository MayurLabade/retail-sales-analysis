# scripts/insights.py
import pandas as pd

def generate_insights():
    df = pd.read_csv("outputs/customers_with_segments.csv")

    total_rev = df["monetary"].sum()
    top20 = df.sort_values("monetary", ascending=False).head(int(0.2 * len(df)))
    top20_share = top20["monetary"].sum() / total_rev

    print("📊 BUSINESS INSIGHTS")
    print("-" * 40)
    print(f"Total Revenue: ${total_rev:,.0f}")
    print(f"Top 20% of customers generate {top20_share*100:.1f}% of revenue")
    print("\nSegment summary (median values):")
    print(df.groupby("segment")[["recency", "frequency", "monetary"]].median())

if __name__ == "__main__":
    generate_insights()
