from itertools import combinations
from collections import Counter
import pandas as pd
import ast
import networkx as nx
from pyvis.network import Network
#获取top50二元共现景点对
df = pd.read_csv('extracted_locations.csv')
df["locations"] = df["locations"].apply(ast.literal_eval)

routes = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]["locations"].tolist()

pair_counts = Counter()
for route in routes:
    for a, b in combinations(set(route), 2):
        pair_counts[tuple(sorted((a, b)))] += 1

top_pairs = pair_counts.most_common(50)

location_list = [[a, b, count] for (a, b), count in top_pairs]

#生成网络图
location_freq = Counter()
for route in routes:
    for place in set(route):  
        location_freq[place] += 1
        
G = nx.Graph()
for item in location_list:
    G.add_edge(item[0], item[1], weight = item[2])

for node in G.nodes():
    freq = location_freq.get(node, 1)
    G.nodes[node]['size'] = freq * 0.3 


for u, v, d in G.edges(data=True):
    d["value"] = d["weight"]
    d["title"] = f"共现次数: {d['weight']}/{len(routes)}"

net = Network(height="800px", width="100%", bgcolor="white")
net.from_nx(G)
net.force_atlas_2based()
net.show("network graph.html", notebook = False)
