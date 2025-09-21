# scripts/clean_data.py
import pandas as pd
import os

def clean_data():
    # Load Excel
    file_path = "data/raw/online_retail_II.xlsx"
    df = pd.read_excel(file_path, sheet_name=0)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    print("✅ Columns found:", df.columns.tolist())

    # Rename to consistent names
    df = df.rename(columns={
        "invoice": "order id",
        "invoicedate": "order date",
        "customer id": "customer id",
        "stockcode": "product id",
        "description": "product name",
        "price": "price",
        "quantity": "quantity",
        "country": "country"
    })

    # Drop missing customers
    df = df.dropna(subset=["customer id"])

    # Convert types
    df["order date"] = pd.to_datetime(df["order date"], errors="coerce")
    df["customer id"] = df["customer id"].astype(str)

    # Remove cancellations (invoices that start with 'C')
    df = df[~df["order id"].astype(str).str.startswith("C")]

    # Remove negative or zero quantities/prices
    df = df[(df["quantity"] > 0) & (df["price"] > 0)]

    # Create total sales column
    df["total sales"] = df["quantity"] * df["price"]

    # Add year & month
    df["year"] = df["order date"].dt.year
    df["month"] = df["order date"].dt.to_period("M").astype(str)

    # Ensure processed folder exists
    os.makedirs("data/processed", exist_ok=True)

    # Save cleaned file
    output_path = "data/processed/cleaned.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to {output_path}")

if __name__ == "__main__":
    clean_data()
