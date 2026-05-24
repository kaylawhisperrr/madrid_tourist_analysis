import pandas as pd
import ast
df = pd.read_csv('extracted_locations.csv')
df["locations"] = df["locations"].apply(ast.literal_eval)

avrg_locations_per_route = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]["locations"].apply(len).mean()

print(f'帖均地点数为{avrg_locations_per_route}')