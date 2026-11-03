"""
Left-Right (LR) Planarity Test (Brandes 2009 / Hopcroft-Tarjan)
Informatics ITS - Graph Theory
"""

import sys
from collections import defaultdict

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


# a range of back edges (low to high), None means empty
class Interval:
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high

    def empty(self):
        return self.low is None and self.high is None

    def conflicting(self, b, lowpt):
        return (not self.empty()) and (lowpt[self.high] > lowpt[b])


# a left interval and a right interval, edges in one interval share the same side
class ConflictPair:
    def __init__(self, left=None, right=None):
        self.left = left if left is not None else Interval()
        self.right = right if right is not None else Interval()

    def swap(self):
        self.left, self.right = self.right, self.left

    def lowest(self, lowpt):
        if self.left.empty():
            return lowpt[self.right.low]
        if self.right.empty():
            return lowpt[self.left.low]
        return min(lowpt[self.left.low], lowpt[self.right.low])


# main LR test: first DFS gets lowpt values, second DFS checks for left/right conflicts
def is_planar_lr(nodes, edges, adj):
    n, m = len(nodes), len(edges)
    if n <= 4:
        return True, "Graph has 4 or fewer vertices (always planar)."
    if m > 3 * n - 6:
        return False, f"Fails Euler's formula: {m} edges > 3*{n}-6 = {3*n-6}."

    node_list = list(nodes)
    height, lowpt, lowpt2, nesting, parent_edge = {}, {}, {}, {}, {}
    dg_adj = defaultdict(list)
    dg_edges = set()

    # Step 1: DFS orientation
    # directs every edge and computes lowpt, lowpt2 and nesting depth
    def dfs_orient(v):
        e = parent_edge.get(v)
        for w in adj[v]:
            vw, wv = (v, w), (w, v)
            if vw in dg_edges or wv in dg_edges:
                continue
            dg_edges.add(vw)
            dg_adj[v].append(w)
            lowpt[vw] = height[v]
            lowpt2[vw] = height[v]

            if w not in height:
                parent_edge[w] = vw
                height[w] = height[v] + 1
                dfs_orient(w)
            else:
                lowpt[vw] = height[w]

            nesting[vw] = 2 * lowpt[vw] + (1 if lowpt2[vw] < height[v] else 0)

            if e:
                if lowpt[vw] < lowpt[e]:
                    lowpt2[e] = min(lowpt[e], lowpt2[vw])
                    lowpt[e] = lowpt[vw]
                elif lowpt[vw] > lowpt[e]:
                    lowpt2[e] = min(lowpt2[e], lowpt[vw])
                else:
                    lowpt2[e] = min(lowpt2[e], lowpt2[vw])

    roots = []
    for v in node_list:
        if v not in height:
            height[v] = 0
            roots.append(v)
            dfs_orient(v)

    # Order edges by nesting depth
    ordered_adj = {v: sorted(dg_adj[v], key=lambda w: nesting[(v, w)]) for v in node_list}

    # Step 2: Conflict resolution using stack
    S = []
    stack_bottom = {}
    lowpt_edge = {}
    ref = {}
    side = defaultdict(lambda: 1)

    def top():
        return S[-1] if S else None

    # merges conflict pairs, returns False if two edges can't be on any side
    def add_constraints(ei, e):
        P = ConflictPair()
        while True:
            Q = S.pop()
            if not Q.left.empty():
                Q.swap()
            if not Q.left.empty():
                return False
            if lowpt[Q.right.low] > lowpt[e]:
                if P.right.empty():
                    P.right = Interval(Q.right.low, Q.right.high)
                else:
                    ref[P.right.low] = Q.right.high
                P.right.low = Q.right.low
            else:
                ref[Q.right.low] = lowpt_edge[e]
            if top() == stack_bottom[ei]:
                break

        while top() and (top().left.conflicting(ei, lowpt) or top().right.conflicting(ei, lowpt)):
            Q = S.pop()
            if Q.right.conflicting(ei, lowpt):
                Q.swap()
            if Q.right.conflicting(ei, lowpt):
                return False
            ref[P.right.low] = Q.right.high
            if Q.right.low is not None:
                P.right.low = Q.right.low
            if P.left.empty():
                P.left = Interval(Q.left.low, Q.left.high)
            else:
                ref[P.left.low] = Q.left.high
            P.left.low = Q.left.low

        if not (P.left.empty() and P.right.empty()):
            S.append(P)
        return True

    # removes back edges that end at the parent vertex since they are done
    def remove_back_edges(e):
        u = e[0]
        while S and top().lowest(lowpt) == height[u]:
            P = S.pop()
            if P.left.low is not None:
                side[P.left.low] = -1
        if S:
            P = S.pop()
            while P.left.high is not None and P.left.high[1] == u:
                P.left.high = ref.get(P.left.high)
            if P.left.high is None and P.left.low is not None:
                ref[P.left.low] = P.right.low
                side[P.left.low] = -1
                P.left.low = None
            while P.right.high is not None and P.right.high[1] == u:
                P.right.high = ref.get(P.right.high)
            if P.right.high is None and P.right.low is not None:
                ref[P.right.low] = P.left.low
                side[P.right.low] = -1
                P.right.low = None
            S.append(P)

    # second DFS, returns False when a conflict is found
    def dfs_test(v):
        e = parent_edge.get(v)
        for w in ordered_adj[v]:
            ei = (v, w)
            stack_bottom[ei] = top()
            if ei == parent_edge.get(w):
                if not dfs_test(w):
                    return False
            else:
                lowpt_edge[ei] = ei
                S.append(ConflictPair(right=Interval(ei, ei)))

            if lowpt[ei] < height[v]:
                if w == ordered_adj[v][0]:
                    lowpt_edge[e] = lowpt_edge[ei]
                else:
                    if not add_constraints(ei, e):
                        return False
        if e:
            remove_back_edges(e)
        return True

    for r in roots:
        if not dfs_test(r):
            return False, "Crossing conflict detected (edges cannot be placed Left/Right)."

    return True, "Valid Left-Right embedding exists without edge crossings."


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
    print("LEFT-RIGHT (HOPCROFT-TARJAN) PLANARITY TEST")
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

    is_planar, reason = is_planar_lr(nodes, edges, adj)
    verdict = "PLANAR" if is_planar else "NON-PLANAR"
    print(f"Result: {verdict}")
    print(f"Reason: {reason}")
    print("=" * 60)
