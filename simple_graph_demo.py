import os
import re
import json
import pickle
from pathlib import Path

import networkx as nx

# ====== 配置：你的代码仓库路径 ======
REPO_PATH = r"D:\gcg\RepoGraph-main\mini_repo"


# ====== 1. 收集所有 .py 文件 ======
repo_path = Path(REPO_PATH)
assert repo_path.exists(), f"仓库路径不存在: {repo_path}"

py_files = [p for p in repo_path.rglob("*.py")]
if not py_files:
    raise RuntimeError(f"在 {repo_path} 下没有找到任何 .py 文件")

print(f"✅ 找到 {len(py_files)} 个 Python 文件：")
for f in py_files:
    print("   ", f)

# ====== 2. 构建一个“行级代码图” ======
G = nx.DiGraph()
tags = []  # 用来保存 jsonl 的标签信息

# 记录函数定义的位置：函数名 -> 节点 id
func_defs = {}

for file_path in py_files:
    rel_path = file_path.relative_to(repo_path).as_posix()  # 相对路径更短

    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    prev_node_id = None

    for lineno, code in enumerate(lines, start=1):
        # 去掉换行符
        code_stripped = code.rstrip("\n")

        # 节点 id：相对路径 + 行号
        node_id = f"{rel_path}:{lineno}"

        # 加入图
        G.add_node(node_id, file=rel_path, lineno=lineno, code=code_stripped)

        tags.append(
            {
                "node_id": node_id,
                "file": rel_path,
                "lineno": lineno,
                "code": code_stripped,
            }
        )

        # 相邻行之间连边（模拟顺序执行）
        if prev_node_id is not None:
            G.add_edge(prev_node_id, node_id, type="next_line")

        prev_node_id = node_id

        # 粗略识别函数定义： def func_name(
        m = re.match(r"\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code_stripped)
        if m:
            func_name = m.group(1)
            func_defs.setdefault(func_name, []).append(node_id)

print(f"✅ 图构建完成：节点数 = {G.number_of_nodes()}, 边数 = {G.number_of_edges()}")

# ====== 3. 粗略添加“函数调用 -> 函数定义”的边 ======
for node_id, data in G.nodes(data=True):
    code = data.get("code", "")
    # 在每一行查找出现的函数调用： func_name(...)
    for func_name, def_nodes in func_defs.items():
        # 跳过定义本身
        if code.strip().startswith(f"def {func_name}("):
            continue
        # 简单判断是否调用：包含 "func_name("
        if f"{func_name}(" in code:
            for def_node in def_nodes:
                G.add_edge(node_id, def_node, type="call")

print(
    f"✅ 添加函数调用边后：节点数 = {G.number_of_nodes()}, 边数 = {G.number_of_edges()}"
)

# ====== 4. 保存到 repo_structures 目录，方便后续使用 ======
out_dir = Path("repo_structures")
out_dir.mkdir(exist_ok=True)

tags_path = out_dir / "tags_simple.jsonl"
pkl_path = out_dir / "simple_graph.pkl"

with tags_path.open("w", encoding="utf-8") as f:
    for t in tags:
        json.dump(t, f, ensure_ascii=False)
        f.write("\n")

with pkl_path.open("wb") as f:
    pickle.dump(G, f)

print("✅ 已保存：")
print("   标签文件:", tags_path)
print("   图文件  :", pkl_path)

# ====== 5. 做一个“子图上下文压缩”的小实验 ======

# 随便取一个目标节点（这里取第一个）
target_node = list(G.nodes)[0]
print("\n🎯 选取目标节点:", target_node, "=>", G.nodes[target_node]["code"])

# 取 2-hop 邻域子图
h = 2
sub_nodes = nx.ego_graph(G, target_node, radius=h).nodes()
subG = G.subgraph(sub_nodes).copy()

total_nodes = G.number_of_nodes()
sub_nodes_cnt = subG.number_of_nodes()
ratio = sub_nodes_cnt * 1.0 / total_nodes

print(f"\n📊 整图节点数：{total_nodes}")
print(f"📊 {h}-hop 子图节点数：{sub_nodes_cnt}")
print(f"📊 子图节点占比（≈ token 占比）：{ratio:.2%}")

print(
    "\n✅ Demo 完成：你可以在报告里写“子图仅保留了约 "
    f"{ratio:.0%} 的代码行，但保留了与目标位置相关的局部结构”。"
)
