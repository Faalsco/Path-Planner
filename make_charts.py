"""
Makes the README charts from benchmark_results.csv.
Run:  python3 make_charts.py
Saves: chart_savings.png, chart_solvable.png, chart_distance.png
"""
import pandas as pd
import matplotlib.pyplot as plt

TRIALS_PER_DENSITY = 200   # change this if you run a different number of trials

df = pd.read_csv("benchmark_results.csv")

summary = df.groupby("Density").agg(
    solved=("Trial", "count"),
    bfs_nodes=("BFS Nodes", "mean"),
    astar_nodes=("A* Nodes", "mean"),
    attempts=("Attempts", "mean"),
)
summary["savings"] = 100 * (1 - summary["astar_nodes"] / summary["bfs_nodes"])
summary["solvable_pct"] = 100 * summary["solved"] / TRIALS_PER_DENSITY
x = summary.index * 100   # density as a percentage

plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})

# Chart 1: cells explored by each algorithm, and how much A* saves
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, summary["bfs_nodes"], marker="o", linewidth=2, label="BFS")
ax.plot(x, summary["astar_nodes"], marker="o", linewidth=2, label="A*")
for xi, b, s in zip(x, summary["bfs_nodes"], summary["savings"]):
    ax.annotate(f"-{s:.0f}%", (xi, b), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=9, color="gray")
ax.set_xlabel("Obstacle density (%)")
ax.set_ylabel("Average cells explored")
ax.set_title("A* explores far fewer cells, but its advantage shrinks on crowded maps")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("chart_savings.png", dpi=150)

# Chart 2: percolation, how often a random map has a route
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, summary["solvable_pct"], marker="o", linewidth=2, color="tab:green")
ax.axvline(41, linestyle="--", color="gray")
ax.text(41.5, 10, "Percolation theory:\n~41% (very large grids)", color="gray", fontsize=10)
ax.set_xlabel("Obstacle density (%)")
ax.set_ylabel("Trials that found a solvable map (%)")
ax.set_title("Random maps stop having a route between 40% and 50% walls")
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("chart_solvable.png", dpi=150)

# Chart 3: distance between start and goal vs cells explored
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(df["Distance"], df["BFS Nodes"], s=10, alpha=0.35, label="BFS")
ax.scatter(df["Distance"], df["A* Nodes"], s=10, alpha=0.35, label="A*")
ax.set_xlabel("Distance between start and goal (cells)")
ax.set_ylabel("Cells explored")
ax.set_title("BFS work grows fast with distance; A* stays low")
ax.legend(markerscale=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("chart_distance.png", dpi=150)

print(summary.round(1))
print("Saved chart_savings.png, chart_solvable.png, chart_distance.png")
