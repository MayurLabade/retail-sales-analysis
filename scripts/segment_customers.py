# scripts/segment_customers.py
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def segment_customers():
    df = pd.read_csv("data/processed/cleaned.csv")

    # Snapshot date = 1 day after last order
    snapshot_date = pd.to_datetime(df["order date"]).max() + pd.Timedelta(days=1)

    # Build RFM table
    rfm = df.groupby("customer id").agg({
        "order date": lambda x: (snapshot_date - pd.to_datetime(x).max()).days,
        "order id": "nunique",
        "total sales": "sum"
    }).rename(columns={
        "order date": "recency",
        "order id": "frequency",
        "total sales": "monetary"
    }).reset_index()

    # Log transform + scale
    rfm_log = np.log1p(rfm[["recency", "frequency", "monetary"]])
    X = StandardScaler().fit_transform(rfm_log)

    # KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init="auto")
    rfm["segment"] = kmeans.fit_predict(X)

    # Ensure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    # Save segmentation results
    output_path = "outputs/customers_with_segments.csv"
    rfm.to_csv(output_path, index=False)

    print(f"✅ Segmentation saved to {output_path}")

if __name__ == "__main__":
    segment_customers()
