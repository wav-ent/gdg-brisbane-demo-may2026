"""
Code for a quick demo
"""
# %% Import Fuctions

import datetime
import math
import os
import sys
import pandas as pd
import numpy as np

#### 

# %% Task 1


def print_statement(text: str) -> None:
    print(f"{text}!\n" * 5)

print_statement("This is a demo")
# %%


for _ in range(5):
    print("Hello")

# %% Task 2

def read_and_prep_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype={"date": str})
    df["date"] = pd.to_datetime(df["date"])
    return df



# %% Task 4

# The table Price_data contains nulls for the column "Price". These are data errors and should be filtered out
    
price_file_path = ""
price_df = pd.read_csv(price_file_path)
price_df = price_df.dropna(subset=["Price"])

# %% Task 4
# Aggregate Price and Tax into a new column for the dataframe 

price_file_path = ""
price_df = pd.read_csv(price_file_path)
price_df = price_df.dropna(subset=["Price"])
price_df["Total_Price"] = price_df["Price"] + price_df["Tax"]

# %% Task 5

# Combine Price Table with Cost Data based on the keys 'SKU'


price_file_path = ""
price_df = pd.read_csv(price_file_path)
price_df = price_df.dropna(subset=["Price"])
price_df["Total_Price"] = price_df["Price"] + price_df["Tax"]


cost_file_path = ""
cost_df = pd.read_csv(cost_file_path)
combined_df = pd.merge(price_df, cost_df, on="SKU", how="left")
