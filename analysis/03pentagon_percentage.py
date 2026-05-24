import pandas as pd
import ast
df = pd.read_csv('extracted_locations.csv')
df["locations"] = df["locations"].apply(ast.literal_eval)

clean_route_count = 0

for x in df['location_count']:
    if x > 1 and x < 12:
        clean_route_count += 1

pentagon = ['丽池公园', '太阳门广场', '普拉多博物馆', '马德里王宫', '马约尔广场']

coverage_5 = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]["locations"].apply(
    lambda x: set(pentagon).issubset(set(x))
).mean()

coverage_1 = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]["locations"].apply(
    lambda x: bool(set(x) & set(pentagon))
).mean()


print(f'清洗后有{clean_route_count}条路线，pentagon中五点覆盖率为{coverage_5}，一点覆盖率为{coverage_1}')
