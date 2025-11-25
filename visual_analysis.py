import pickle
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

# ======= 参数配置 =======
repo_id = "simple_graph"        # 如果你的 pkl 叫 manual.pkl，就改成 "manual"
h = 2                           # 子图邻域半径
base = Path("repo_structures")
pkl_path = base / f"{repo_id}.pkl"

# ======= 读取图 =======
with open(pkl_path, "rb") as f:
    G = pickle.load(f)

print("==== 可视化分析 ====")
print(f"整图节点数: {G.number_of_nodes()}")
print(f"整图边数  : {G.number_of_edges()}")

# ======= 子图提取 =======
target_node = list(G.nodes)[0]
subG = nx.ego_graph(G, target_node, radius=h)
ratio = subG.number_of_nodes() / G.number_of_nodes() * 100
print(f"{h}-hop 子图节点数: {subG.number_of_nodes()}  占比: {ratio:.2f}%")

# ======= 可视化 1：节点度分布 =======
deg = [d for _, d in G.degree()]
plt.figure(figsize=(6,4))
plt.hist(deg, bins=20, edgecolor="black")
plt.title(f"Degree Distribution – {repo_id}", fontsize=12)
plt.xlabel("Degree")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(f"{repo_id}_degree_distribution.png", dpi=300)
plt.show()

# ======= 可视化 2：子图结构 =======
plt.figure(figsize=(6,6))
pos = nx.spring_layout(subG, seed=42)
nx.draw_networkx_nodes(subG, pos, node_size=60)
nx.draw_networkx_edges(subG, pos, alpha=0.3)
nx.draw_networkx_labels(
    subG, pos,
    {n: n.split(':')[-1] for n in list(subG.nodes)[:15]},  # 只标前15个节点
    font_size=7
)
plt.title(f"{h}-hop Subgraph around {target_node}", fontsize=10)
plt.axis("off")
plt.tight_layout()
plt.savefig(f"{repo_id}_subgraph.png", dpi=300)
plt.show()

print("\n✅ 输出完成：生成两张图：")
print(f"  - {repo_id}_degree_distribution.png")
print(f"  - {repo_id}_subgraph.png")
