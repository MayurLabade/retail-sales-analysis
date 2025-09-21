{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f6a68a62",
   "metadata": {
    "vscode": {
     "languageId": "plaintext"
    }
   },
   "outputs": [],
   "source": [
    "# 01_data_cleaning.ipynb\n",
    "\n",
    "import pandas as pd\n",
    "import os\n",
    "\n",
    "# Paths\n",
    "RAW_PATH = \"../data/raw/superstore.xlsx\"\n",
    "PROCESSED_PATH = \"../data/processed/cleaned.csv\"\n",
    "\n",
    "# Load Excel\n",
    "df = pd.read_excel(RAW_PATH)\n",
    "\n",
    "print(\"Raw shape:\", df.shape)\n",
    "print(df.head())\n",
    "print(df.columns)\n",
    "\n",
    "# Drop duplicates\n",
    "df = df.drop_duplicates()\n",
    "\n",
    "# Handle missing values\n",
    "df = df.dropna(subset=['Customer ID', 'Sales'])\n",
    "\n",
    "# Convert dates\n",
    "df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')\n",
    "df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')\n",
    "\n",
    "# Ensure numeric fields\n",
    "df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')\n",
    "df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')\n",
    "df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')\n",
    "\n",
    "# Create Total Sales (with discount)\n",
    "df['Total Sales'] = df['Sales'] * (1 - df['Discount'])\n",
    "\n",
    "# Save processed data\n",
    "os.makedirs(\"../data/processed\", exist_ok=True)\n",
    "df.to_csv(PROCESSED_PATH, index=False)\n",
    "\n",
    "print(\"Cleaned data saved to:\", PROCESSED_PATH)\n",
    "print(\"Cleaned shape:\", df.shape)\n"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
