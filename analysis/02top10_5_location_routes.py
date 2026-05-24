from itertools import combinations
from collections import Counter
import pandas as pd
import ast


df = pd.read_csv('extracted_locations.csv')
df["locations"] = df["locations"].apply(ast.literal_eval)

five_combos = Counter()

for route in df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]["locations"]:
    if len(route) >= 5:
        for combo in combinations(set(route), 5):
            five_combos[tuple(sorted(combo))] += 1

top10 = five_combos.most_common(10)
print(top10)