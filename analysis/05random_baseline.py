import random
import pandas as pd
import ast
import matplotlib.pyplot as plt

df = pd.read_csv('extracted_locations.csv')
df["locations"] = df["locations"].apply(ast.literal_eval)
df = df[(df["locations"].apply(len) > 1) & (df["locations"].apply(len) < 12)]

all_locations = list(set(df.explode("locations")["locations"]))
pentagon = ['丽池公园', '太阳门广场', '普拉多博物馆', '马德里王宫', '马约尔广场']

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
print(f"模拟结果均值: {sum(sim_results)/len(sim_results):.4f}")  

observed_value = 0.2147

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
n, bins, patches = ax.hist(sim_results, bins=30, alpha=0.7, 
                            color='#1E88E5',  
                            edgecolor='white', linewidth=0.5,
                            label='Random Simulation')
ax.axvline(observed_value, 
           linestyle='--', 
           linewidth=3,
           color='#FF8C00',   
           alpha=0.9,
           label=f'Observed Value ({observed_value:.4f})')
ax.set_xlabel("Proportion of Routes Containing All 5 Pentagon Sites", 
              fontsize=12, fontweight='semibold')
ax.set_ylabel("Frequency (out of 1,000 simulations)", 
              fontsize=12, fontweight='semibold')
ax.set_title("Random Simulation vs Observed Data\nPentagon Sites Co-occurrence", 
             fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left', framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)
ax.tick_params(axis='both', labelsize=10)
y_max = ax.get_ylim()[1]
ax.set_ylim(0, y_max * 1.1)
plt.tight_layout()
plt.show()



