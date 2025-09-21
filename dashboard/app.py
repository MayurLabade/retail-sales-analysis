# dashboard/app.py
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date

# ⚡ Must be the first Streamlit command
st.set_page_config(page_title="Online Retail Dashboard", layout="wide")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned.csv", parse_dates=["order date"])

df = load_data()

# Add month and week columns for trend analysis
df["month"] = df["order date"].dt.to_period("M").astype(str)
df["week"] = df["order date"].dt.to_period("W").astype(str)
df["day"] = df["order date"].dt.date

# Date filter
min_date_dt = df["order date"].min().date()
max_date_dt = df["order date"].max().date()

date_range = st.sidebar.slider(
    "Select Date Range", 
    min_value=min_date_dt, 
    max_value=max_date_dt, 
    value=(min_date_dt, max_date_dt)
)

# Filter dataframe by selected date range
df_filtered = df[(df["order date"].dt.date >= date_range[0]) & 
                 (df["order date"].dt.date <= date_range[1])]

# Country filter
countries = df_filtered["country"].unique().tolist()
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries)
df_filtered = df_filtered[df_filtered["country"].isin(selected_countries)]

# Top N products filter
top_n = st.sidebar.slider("Top N Products", 5, 20, 10)

# Trend granularity
trend_option = st.sidebar.radio("Trend Granularity", ["Monthly", "Weekly", "Daily"])

# --- Main Dashboard ---
st.title("🛒 Online Retail - Sales Dashboard")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["KPIs & Trends", "Products", "Customers", "Category Insights", "Geography"])

# --- Tab 1: KPIs & Trends ---
with tab1:
    # KPIs
    total_revenue = df_filtered["total sales"].sum()
    total_orders = df_filtered["order id"].nunique()
    avg_order = total_revenue / total_orders if total_orders else 0
    repeat_customers = df_filtered["customer id"].duplicated().sum()
    repeat_customer_pct = (repeat_customers / df_filtered["customer id"].nunique()) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Avg Order Value", f"${avg_order:,.2f}")
    col4.metric("Repeat Customers %", f"{repeat_customer_pct:.1f}%")

    # Revenue Trend
    if trend_option == "Monthly":
        trend_df = df_filtered.groupby("month")["total sales"].sum().reset_index()
        trend_x = "month"
    elif trend_option == "Weekly":
        trend_df = df_filtered.groupby("week")["total sales"].sum().reset_index()
        trend_x = "week"
    else:
        trend_df = df_filtered.groupby("day")["total sales"].sum().reset_index()
        trend_x = "day"

    fig_trend = px.line(trend_df, x=trend_x, y="total sales", title=f"{trend_option} Revenue Trend")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Revenue vs Orders Scatter
    scatter_df = df_filtered.groupby("month").agg({"total sales":"sum", "order id":"nunique"}).reset_index()
    fig_scatter = px.scatter(scatter_df, x="order id", y="total sales", size="total sales", color="month",
                             title="Revenue vs Orders")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Tab 2: Products ---
with tab2:
    # Top Products
    top_products = df_filtered.groupby("product name")["total sales"].sum().nlargest(top_n).reset_index()
    fig3 = px.bar(
        top_products, 
        x="total sales", 
        y="product name", 
        orientation="h", 
        title=f"Top {top_n} Products by Revenue"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Top N Products by Country
    country_product = st.selectbox("Select Country for Top Products", countries)
    df_country = df_filtered[df_filtered["country"]==country_product]
    top_products_country = df_country.groupby("product name")["total sales"].sum().nlargest(top_n).reset_index()
    fig_country_prod = px.bar(
        top_products_country,
        x="total sales",
        y="product name",
        orientation="h",
        title=f"Top {top_n} Products in {country_product}"
    )
    st.plotly_chart(fig_country_prod, use_container_width=True)

# --- Tab 3: Customers ---
with tab3:
    try:
        rfm = pd.read_csv("outputs/customers_with_segments.csv")
        seg_summary = rfm.groupby("segment")[["recency","frequency","monetary"]].median().reset_index()

        st.subheader("Customer Segments Insights")
        col_r, col_f, col_m = st.columns(3)
        col_r.bar_chart(seg_summary.set_index("segment")["recency"], use_container_width=True)
        col_f.bar_chart(seg_summary.set_index("segment")["frequency"], use_container_width=True)
        col_m.bar_chart(seg_summary.set_index("segment")["monetary"], use_container_width=True)

        # RFM Segment Pie
        seg_count = rfm["segment"].value_counts().reset_index()
        seg_count.columns = ["segment","count"]
        fig_seg_pie = px.pie(seg_count, names="segment", values="count", title="RFM Segment Distribution")
        st.plotly_chart(fig_seg_pie, use_container_width=True)

    except FileNotFoundError:
        st.warning("Run segmentation first to see customer segments.")

# --- Tab 4: Category Insights ---
with tab4:
    if "category" in df_filtered.columns and "sub-category" in df_filtered.columns:
        st.subheader("📦 Category & Sub-Category Insights")

        categories = df_filtered["category"].unique().tolist()
        selected_category = st.selectbox("Select Category", categories)

        sub_df = df_filtered[df_filtered["category"] == selected_category]

        # Top sub-categories
        top_sub_n = st.slider("Top N Sub-Categories", 3, 10, 5)
        top_subcategories = sub_df.groupby("sub-category")["total sales"].sum().nlargest(top_sub_n).reset_index()
        fig_sub = px.bar(
            top_subcategories,
            x="total sales",
            y="sub-category",
            orientation="h",
            title=f"Top {top_sub_n} Sub-Categories in {selected_category}"
        )
        st.plotly_chart(fig_sub, use_container_width=True)

        # Drill-down: Sub-Category Revenue vs Quantity
        st.subheader(f"🔍 Sub-Category Drill-Down for {selected_category}")
        sub_drill_df = sub_df.groupby("sub-category").agg({"total sales": "sum", "quantity": "sum"}).reset_index()
        fig_drill = px.scatter(
            sub_drill_df, 
            x="quantity", 
            y="total sales", 
            size="total sales", 
            color="sub-category",
            title=f"{selected_category}: Quantity vs Revenue by Sub-Category",
            hover_data=["sub-category"]
        )
        st.plotly_chart(fig_drill, use_container_width=True)

        # Stacked bar: Monthly Revenue by Sub-Category
        stacked_df = sub_df.groupby(["month","sub-category"])["total sales"].sum().reset_index()
        fig_stack = px.bar(
            stacked_df,
            x="month",
            y="total sales",
            color="sub-category",
            title=f"Monthly Revenue by Sub-Category ({selected_category})"
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    else:
        st.warning("No 'category' or 'sub-category' columns found in the dataset. Skipping Category Insights.")

# --- Tab 5: Geography ---
with tab5:
    country_sales = df_filtered.groupby("country")["total sales"].sum().reset_index()
    fig_map = px.choropleth(
        country_sales,
        locations="country",
        locationmode="country names",
        color="total sales",
        title="Revenue by Country",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- Download Filtered Data ---
st.subheader("Download Filtered Data")
st.write("You can download the filtered dataset for further analysis.")
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)
