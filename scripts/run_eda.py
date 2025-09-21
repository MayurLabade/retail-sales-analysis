# scripts/run_eda.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    df = pd.read_csv("data/processed/cleaned.csv", parse_dates=["order date"])

    os.makedirs("outputs/figures", exist_ok=True)

    # Revenue trend over time (monthly)
    monthly_sales = df.groupby("month")["total sales"].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(x="month", y="total sales", data=monthly_sales, marker="o")
    plt.xticks(rotation=45)
    plt.title("Monthly Revenue Trend")
    plt.tight_layout()
    plt.savefig("outputs/figures/revenue_trend.png")
    plt.close()

    # Revenue by country
    country_sales = df.groupby("country")["total sales"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=country_sales.values, y=country_sales.index)
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig("outputs/figures/country_revenue.png")
    plt.close()

    # Top products
    product_sales = df.groupby("product name")["total sales"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=product_sales.values, y=product_sales.index)
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig("outputs/figures/top_products.png")
    plt.close()

    # Top customers
    customer_sales = df.groupby("customer id")["total sales"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=customer_sales.values, y=customer_sales.index)
    plt.title("Top 10 Customers by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig("outputs/figures/top_customers.png")
    plt.close()

    print("✅ EDA figures saved to outputs/figures/")

if __name__ == "__main__":
    run_eda()
