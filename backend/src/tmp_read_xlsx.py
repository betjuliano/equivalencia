import pandas as pd
import sys

try:
    file_path = r"c:\Users\pccli\Documents\EQUIVALENCIA\backend\data\matriz_curricular_editavel.xlsx"
    df = pd.read_excel(file_path, sheet_name=0)
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")
