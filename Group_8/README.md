# Graph Planarity Check - Week 9 Homework
**Informatics ITS Graph Theory class Group 8**

## Group Members
1. Aqilah Ibrahim - 5025251260
2. Rizqi Arya Kuskhilbyano - 5025251161
3. Athar Rozy Rasyidan - 5025251009
4. Wafi Fawwaz Sutisna - 5025251017

---

## Algorithms Implemented

This repository implements two planarity checking algorithms (separate from Kuratowski's theorem and Narsingh Deo's reduction):

### 1. Demoucron-Malgrange-Pertuiset (DMP) Algorithm (`dmp.py`)
- **Type:** Path addition / face expansion.
- **How it works:**
  1. Finds a cycle in the graph. This cycle divides the plane into 2 faces (interior and exterior).
  2. The remaining edges form pieces called fragments (or bridges).
  3. For each fragment, the algorithm checks which faces can contain it without crossing edges.
  4. If any fragment cannot fit in any face, the graph is **Non-Planar**.
  5. If a fragment can only fit in one face, it is drawn there, splitting that face into two smaller faces.
  6. The process repeats until all edges are drawn (**Planar**) or a fragment gets stuck (**Non-Planar**).

### 2. Left-Right Planarity Test (`left_right.py`)
- **Type:** Hopcroft-Tarjan / DFS tree edge partitioning.
- **How it works:**
  1. Builds a Depth-First Search (DFS) spanning tree of the graph.
  2. The remaining edges are back-edges returning from descendants to ancestors.
  3. For a graph to be planar, every back-edge must be placed either on the **Left** side or **Right** side of the DFS tree path without crossing.
  4. The algorithm tracks crossings between back-edges using a conflict stack.
  5. If there is a crossing conflict that cannot be resolved (an edge cannot go on the Left or Right), the graph is **Non-Planar**. Otherwise, it is **Planar**.

---

## Prerequisites
- Python 3 (Python 3.8 or newer).
- Uses only built-in standard Python libraries (no `pip install` needed).

---

## Instructions to Run the Code

Each algorithm is in its own file and can be run independently.

### Running Algorithm 1 (DMP):
```bash
python dmp.py
```
You will be prompted:
- Press **1** to run the built-in sample graph (3D Cube).
- Press **2** to type edges manually (format: `u v`).

Or pass a file directly:
```bash
python dmp.py sample_input.txt
```

---

### Running Algorithm 2 (Left-Right / Hopcroft-Tarjan):
```bash
python left_right.py
```
You will be prompted:
- Press **1** to run the built-in sample graph (3D Cube).
- Press **2** to type edges manually (format: `u v`).

Or pass a file directly:
```bash
python left_right.py sample_input.txt
```

---

## Result of Sample Run

### Test 1: Planar Graph (3D Cube from `sample_input.txt`)
- **Input:** 8 vertices, 12 edges.
- **Output (`dmp.py`):**
  ```text
  Source:   Sample Graph (3D Cube)
  Vertices: 8
  Edges:    12
  ------------------------------------------------------------
  Result: PLANAR
  Reason: All edges successfully embedded into planar faces without crossing.
  ```
- **Output (`left_right.py`):**
  ```text
  Source:   Sample Graph (3D Cube)
  Vertices: 8
  Edges:    12
  ------------------------------------------------------------
  Result: PLANAR
  Reason: Valid Left-Right embedding exists without edge crossings.
  ```

### Test 2: Non-Planar Graph (Manual Input: Complete Bipartite $K_{3,3}$)
- **Input:** 6 vertices, 9 edges (edges: `0 3`, `0 4`, `0 5`, `1 3`, `1 4`, `1 5`, `2 3`, `2 4`, `2 5`).
- **Output (`dmp.py`):**
  ```text
  Result: NON-PLANAR
  Reason: Fragment with attachments {1, 5} cannot fit into any current face.
  ```
- **Output (`left_right.py`):**
  ```text
  Result: NON-PLANAR
  Reason: Crossing conflict detected (edges cannot be placed Left/Right).
  ```

---

## AI Tools Usage Disclosure

https://share.gemini.google/V6HdjQ7KVqIV
