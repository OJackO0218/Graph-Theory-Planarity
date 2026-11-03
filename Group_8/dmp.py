"""
Demoucron-Malgrange-Pertuiset (DMP) Planarity Check (1964)
Informatics ITS - Graph Theory
"""

import sys
from collections import defaultdict, deque

# Sample Planar Graph: 3D Cube (8 vertices, 12 edges)
SAMPLE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
    (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
    (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical edges
]


# turns the edge list into nodes, edges and an adjacency list
def build_graph(edge_list):
    adj = defaultdict(set)
    edges = set()
    nodes = set()
    for u, v in edge_list:
        if u != v:
            u, v = min(u, v), max(u, v)
            adj[u].add(v)
            adj[v].add(u)
            edges.add((u, v))
            nodes.update([u, v])
    return nodes, edges, adj


# finds any cycle using DFS, we need it as the starting point
def find_cycle(nodes, adj):
    visited, parent = {}, {}
    for start in nodes:
        if start in visited:
            continue
        stack = [(start, -1)]
        while stack:
            u, p = stack.pop()
            if u not in visited:
                visited[u] = True
                parent[u] = p
                for v in adj[u]:
                    if v == p:
                        continue
                    if v in visited:
                        path = [v]
                        curr = u
                        while curr != v and curr != -1:
                            path.append(curr)
                            curr = parent.get(curr, -1)
                        if len(path) >= 3:
                            return path
                    else:
                        stack.append((v, u))
    return []


# puts a path from u to v inside a face, which splits it into two faces
def split_face(face, u, v, path):
    iu, iv = face.index(u), face.index(v)
    n = len(face)

    # Subpath 1: u -> v along face boundary
    s1, curr = [], iu
    while True:
        s1.append(face[curr])
        if curr == iv:
            break
        curr = (curr + 1) % n

    # Subpath 2: v -> u along face boundary
    s2, curr = [], iv
    while True:
        s2.append(face[curr])
        if curr == iu:
            break
        curr = (curr + 1) % n

    inner = path[1:-1]
    f1 = s1[:-1] + [v] + list(reversed(inner))
    f2 = s2[:-1] + [u] + inner
    return f1, f2


# main DMP test: keep adding fragments into faces until all edges are placed
def is_planar_dmp(nodes, edges, adj):
    n, m = len(nodes), len(edges)
    if n <= 4:
        return True, "Graph has 4 or fewer vertices (always planar)."
    if m > 3 * n - 6:
        return False, f"Fails Euler's formula: {m} edges > 3*{n}-6 = {3*n-6}."

    cycle = find_cycle(nodes, adj)
    if not cycle:
        return True, "Graph contains no cycles (tree structure)."

    # Start with initial cycle forming 2 faces
    h_nodes = set(cycle)
    h_edges = set((min(cycle[i], cycle[(i + 1) % len(cycle)]), 
                   max(cycle[i], cycle[(i + 1) % len(cycle)])) for i in range(len(cycle)))
    faces = [list(cycle), list(reversed(cycle))]

    while len(h_edges) < len(edges):
        rem_edges = edges - h_edges
        fragments = []

        # 1. Chords
        for u, v in rem_edges:
            if u in h_nodes and v in h_nodes:
                fragments.append({"edges": {(u, v)}, "att": {u, v}, "int": set()})

        # 2. Components in G - H
        seen_nodes = set()
        for node in nodes - h_nodes:
            if node in seen_nodes:
                continue
            comp_nodes, comp_edges, att = set(), set(), set()
            q = deque([node])
            seen_nodes.add(node)
            while q:
                curr = q.popleft()
                comp_nodes.add(curr)
                for nxt in adj[curr]:
                    e = (min(curr, nxt), max(curr, nxt))
                    if e in rem_edges:
                        comp_edges.add(e)
                    if nxt in h_nodes:
                        att.add(nxt)
                    elif nxt not in seen_nodes:
                        seen_nodes.add(nxt)
                        q.append(nxt)
            fragments.append({"edges": comp_edges, "att": att, "int": comp_nodes})

        # Check admissible faces
        adm_faces = []
        for frag in fragments:
            valid = [f for f in faces if frag["att"].issubset(set(f))]
            if not valid:
                return False, f"Fragment with attachments {frag['att']} cannot fit into any current face."
            adm_faces.append(valid)

        # Pick fragment: pick forced one (|valid| == 1) if any
        pick = 0
        for i, val in enumerate(adm_faces):
            if len(val) == 1:
                pick = i
                break

        target = fragments[pick]
        face = adm_faces[pick][0]
        atts = [v for v in face if v in target["att"]]
        u, v = atts[0], atts[1]

        # Find path between u and v
        if not target["int"]:
            path = [u, v]
        else:
            t_adj = defaultdict(set)
            for a, b in target["edges"]:
                t_adj[a].add(b)
                t_adj[b].add(a)
            parent = {}
            q = deque([u])
            while q:
                curr = q.popleft()
                if curr == v:
                    break
                for nxt in t_adj[curr]:
                    if nxt == v or (nxt in target["int"] and nxt not in parent):
                        parent[nxt] = curr
                        q.append(nxt)
            path = [v]
            curr = v
            while curr != u:
                curr = parent[curr]
                path.append(curr)
            path.reverse()

        f1, f2 = split_face(face, u, v, path)
        faces.remove(face)
        faces.extend([f1, f2])
        for i in range(len(path) - 1):
            h_edges.add((min(path[i], path[i + 1]), max(path[i], path[i + 1])))
        h_nodes.update(path)

    return True, "All edges successfully embedded into planar faces without crossing."


# reads edges typed in by the user
def read_manual_input():
    print("Enter edges line by line (format: 'u v'). Type 'done' or press Enter on an empty line to finish:")
    edge_list = []
    while True:
        try:
            line = input().strip()
            if not line or line.lower() == "done":
                break
            parts = line.split()
            if len(parts) >= 2:
                edge_list.append((int(parts[0]), int(parts[1])))
        except (EOFError, KeyboardInterrupt):
            break
    return edge_list


# reads edges from a file, one "u v" per line (# lines are skipped)
def read_file(path):
    edge_list = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                edge_list.append((int(parts[0]), int(parts[1])))
    return edge_list


if __name__ == "__main__":
    print("=" * 60)
    print("DEMOUCRON-MALGRANGE-PERTUISET (DMP) PLANARITY TEST")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Load from file passed as argument
        edge_list = read_file(sys.argv[1])
        source = sys.argv[1]
    else:
        print("Choose input mode:")
        print("1. Run sample graph (3D Cube)")
        print("2. Enter edges manually")
        choice = input("Select [1 or 2] (default 1): ").strip()

        if choice == "2":
            edge_list = read_manual_input()
            source = "Manual Input"
        else:
            edge_list = SAMPLE_EDGES
            source = "Sample Graph (3D Cube)"

    nodes, edges, adj = build_graph(edge_list)
    print("-" * 60)
    print(f"Source:   {source}")
    print(f"Vertices: {len(nodes)}")
    print(f"Edges:    {len(edges)}")
    print("-" * 60)

    is_planar, reason = is_planar_dmp(nodes, edges, adj)
    verdict = "PLANAR" if is_planar else "NON-PLANAR"
    print(f"Result: {verdict}")
    print(f"Reason: {reason}")
    print("=" * 60)
