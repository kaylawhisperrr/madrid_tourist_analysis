import streamlit as st
import pandas as pd
import ast
import plotly.express as px
import random
from collections import Counter
from itertools import combinations
import streamlit.components.v1 as components
import plotly.graph_objects as go

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Madrid Tourism Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# Load Data
# =========================
df = pd.read_csv("extracted_locations.csv")

df["locations"] = df["locations"].apply(ast.literal_eval)
df["location_count"] = df["location_count"].astype(int)
df_1 = df.copy()
df = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)].copy()

# flatten all locations
all_locations = list(set(df.explode("locations")["locations"]))

# =========================
# Core Metrics
# =========================
avg_locations = df["locations"].apply(len).mean()

pentagon = [
    '丽池公园', '太阳门广场', '普拉多博物馆',
    '马德里王宫', '马约尔广场'
]

coverage_5 = df["locations"].apply(lambda x: set(pentagon).issubset(set(x))).mean()

coverage_1 = df["locations"].apply(lambda x: bool(set(x) & set(pentagon))).mean()

all_locations = list(set(df.explode("locations")["locations"]))

sim_results = []

for _ in range(1000):
    contain_count = 0
    for n in df["location_count"]:
        sampled = random.sample(
            all_locations,
            n
        )
        if set(pentagon).issubset(set(sampled)):
            contain_count += 1
    sim_rate = contain_count / len(df)
    sim_results.append(sim_rate)

sim_result = sum(sim_results)/len(sim_results)
# =========================
# UI HEADER
# =========================
st.title("Understanding Tourist Destination Concentration in UGC Travel Content")

st.write(
    "A behavioral analysis of 300+ Xiaohongshu travel posts in Madrid. ")

st.divider()

# =========================
# KPI SECTION
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Posts analyzed", "300+")
col2.metric("Average locations per trip", f"{avg_locations:.2f}")
col3.metric("Pentagon coverage", f"{coverage_5*100:.2f}%")
col4.metric("Random baseline", f"{sim_result*100:.2f}%")

# =========================
# SECTION 2: Trip Length Distribution
# =========================
st.divider()

st.header("Trip Length Distribution")

counts = df_1[df_1["location_count"] > 0]["locations"].apply(len)

mean_val = counts[(counts > 1) & (counts < 12)].mean()

# frequency table
freq = counts.value_counts().sort_index()

x_vals = freq.index.tolist()
y_vals = freq.values.tolist()

# coloring rule
colors = []

for x in x_vals:
    if x == 1 or x > 11:
        colors.append("rgba(180,180,180,0.75)")   # excluded → gray
    else:
        colors.append("rgba(31,119,180,0.75)")    # kept → blue

# figure
fig1 = go.Figure()

fig1.add_trace(go.Bar(
    x=x_vals,
    y=y_vals,
    marker_color=colors,
    name="Posts"
))

# mean line
fig1.add_vline(
    x=mean_val,
    line_width=3,
    line_dash="dash",
    line_color="#FF8C00",
    annotation_text=f"Mean (2–11): {mean_val:.2f}",
    annotation_position="top right"
)

fig1.add_vline(
    x=1.5,
    line_width=2,
    line_dash="dot",
    line_color="rgba(120,120,120,0.45)"
)

fig1.add_vline(
    x=11.5,
    line_width=2,
    line_dash="dot",
    line_color="rgba(120,120,120,0.45)"
)

fig1.update_layout(
    title="Route Length Distribution",
    xaxis_title="Number of Locations",
    yaxis_title="Frequency",
    bargap=0.15,
    xaxis=dict(
        tickmode='linear',
        dtick=1
    ),
    showlegend=False
)

st.plotly_chart(fig1, use_container_width=True)

st.write(
    "Gray bars indicate route lengths excluded from subsequent analyses "
    "(single-location posts and routes longer than 11 destinations). "
    "The remaining sample was used for structural mobility analysis."
)

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Original posts","312")
col2.metric("Filtered sample","216")
col3.metric("Rule","1 < location_count < 12")

st.write("Subsequent analyses were conducted based on the filtered sample.")

# =========================
# SECTION 3: Tourist Pentagon
# =========================
st.divider()

st.header("The Tourist Pentagon (Core Structure)")

left, right = st.columns([2, 1])

with left:
    st.write(
        """
        The Tourist Pentagon consists of five highly central destinations:

        - 丽池公园
        - 太阳门广场
        - 普拉多博物馆
        - 马德里王宫
        - 马约尔广场

        More than 9 out of 10 travel posts include at least one destination from the pentagon, 
        suggesting the emergence of a shared tourist cognitive core.
        """
    )

with right:
    st.metric("5-point coverage", f"{coverage_5*100:.2f}%")
    st.metric("1-point coverage", f"{coverage_1*100:.2f}%")

# =========================
# SECTION 4: Co-occurrence Network
# =========================
st.divider()
import plotly.graph_objects as go
import networkx as nx

st.header("Co-occurrence Network")

routes = df["locations"].tolist()

pair_counts = Counter()
for route in routes:
    for a, b in combinations(set(route), 2):
        pair_counts[tuple(sorted((a, b)))] += 1

top_pairs = pair_counts.most_common(50)

location_list = [[a, b, count] for (a, b), count in top_pairs]

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

import streamlit.components.v1 as components
from pyvis.network import Network

net = Network(
    height="650px",
    width="100%",
    bgcolor="white",
    font_color="#1f1f1f",
    notebook=False,
    cdn_resources="remote"  
)

net.from_nx(G)

net.force_atlas_2based(
    gravity=-50,
    central_gravity=0.01,
    spring_length=120,
    spring_strength=0.08,
    damping=0.4
)

html_file = "network_graph.html"
net.write_html(html_file)

with open(html_file, "r", encoding="utf-8") as f:
    html_data = f.read()

components.html(
    html_data,
    height=650,
    scrolling=False
)


st.write("Node size represents destination frequency and edge width represents co-occurrence strength. Hover over edges to inspect counts and drag nodes to explore local structure.")

st.write("The co-occurrence network reveals a densely connected core structure centered around five highly recurring destinations.")
# =========================
# SECTION 5: Simulation Baseline
# =========================
st.divider()

st.header("Simulation Baseline (Random Expectation)")

# Monte Carlo simulation (light version for dashboard speed)
sim_results = []

for _ in range(500):  # reduced for streamlit speed
    contain_count = 0
    for n in df["location_count"]:
        sampled = random.sample(all_locations, min(n, len(all_locations)))
        if set(pentagon).issubset(set(sampled)):
            contain_count += 1
    sim_results.append(contain_count / len(df))

observed_value = coverage_5

sim_mean = sum(sim_results) / len(sim_results)

fig2 = go.Figure()

# histogram
fig2.add_trace(go.Histogram(
    x=sim_results,
    nbinsx=18,
    name="Null Model (Monte Carlo, n=500)",
    marker=dict(color="rgba(31,119,180,0.7)")
))

# observed line (legend-friendly)
fig2.add_trace(go.Scatter(
    x=[observed_value, observed_value],
    y=[0, 400],  
    mode="lines",
    name="Observed Value",
    line=dict(width=2, color="#FF8C00", dash="dash"),
    marker=dict(
        size=3,
        color="#FF8C00",
        symbol="circle"
    )
))

fig2.update_yaxes(rangemode="tozero")

fig2.update_xaxes(range=[-0.005, 0.23])

# layout
fig2.update_layout(
    title="Random Simulation vs Observed Concentration",
    xaxis_title="Pentagon Coverage Rate",
    yaxis_title="Frequency",
    showlegend=True,
    barmode="overlay"
)

st.plotly_chart(fig2, use_container_width=True)

st.write(
    f"Observed concentration is approximately "
    f"{observed_value / max(sum(sim_results)/len(sim_results), 1e-6):.1f}× higher than random expectation,indicating a strongly non-random mobility structure. ")

st.divider()
st.write(
    "Based on Xiaohongshu UGC travel posts about Madrid, this analysis identifies a strong non-random concentration pattern in tourist destination choices."
)