import pandas as pd

INPUT_FILE = "xhs正文数据集.xlsx"
OUTPUT_FILE = "xhs正文数据集_cleaned.xlsx"

print("开始读取数据...")

df = pd.read_excel(INPUT_FILE)

print(f"原始数据量: {len(df)}")

df_cleaned = df.drop_duplicates(
    subset='id',
    keep='first'
)

print(f"去重后数据量: {len(df_cleaned)}")

print(f"删除重复记录: {len(df)-len(df_cleaned)}")


df_cleaned.to_excel(OUTPUT_FILE, index=False)

print(f"清洗完成，已保存至: {OUTPUT_FILE}")