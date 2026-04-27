*This project has been created as part of the 42 curriculum by serromer*

# Fly-in: Drone Routing System

---

## Description

**Fly-in** is a drone fleet management and routing simulator written in Python 3.10+.
The primary objective is to navigate a fleet of drones from a starting hub (`start_hub`)
to a destination hub (`end_hub`) in the **minimum number of simulation turns**, while
respecting zone capacities, movement costs, connection limits, and prohibited areas.

The system is built entirely from scratch — no external graph libraries are used.
Every algorithm, data structure, and simulation mechanic is implemented manually.

---

## Project Structure

```
42_Fly-in/
├── main.py                  ← Entry point
├── Makefile                 ← Automation rules
├── requirements.txt         ← Python dependencies
├── LICENSE
├── README.md
├── docs/
│   ├── en.subject.pdf       ← Original subject
│   └── ES/
│       ├── flyin_plan.html          ← Development plan
│       ├── fly_in_study_guide.md    ← Peer review study guide
│       └── challenger_guide.md     ← Challenger notes
├── maps/
│   ├── easy/                ← 3 easy maps (2–4 drones)
│   ├── medium/              ← 3 medium maps (4–6 drones)
│   ├── hard/                ← 3 hard maps (8–15 drones)
│   ├── challenger/          ← 1 optional extreme map (25 drones)
│   └── edge_cases/          ← Custom maps for parser edge case testing
├── models/
│   ├── zone.py              ← Zone class (node)
│   ├── connection.py        ← Connection class (edge)
│   └── graph.py             ← Graph class (full network)
├── parser/
│   └── map_parser.py        ← Parses .txt map files into Graph objects
├── pathfinder/
│   └── pathfinder.py        ← Dijkstra + DFS + bottleneck detection
├── simulator/
│   ├── drone.py             ← Drone class (state machine)
│   └── simulator.py         ← Turn-by-turn simulation engine
└── visualizer/
    ├── terminal.py          ← ANSI colored terminal output
    └── graph_display.py     ← Matplotlib graphical interface
```

---

## Requirements

- Python 3.10 or higher
- `flake8` — code style enforcement
- `mypy` — static type checking
- `matplotlib` — graphical visualization

---

## Installation & Usage

### Setup

```bash
make install
```

This creates a virtual environment and installs all dependencies automatically.

### Run a simulation

**Using Makefile:**
```bash
make run MAP=maps/easy/01_linear_path.txt
make run MAP=maps/medium/02_circular_loop.txt
make run MAP=maps/hard/01_maze_nightmare.txt
```

**Using Python directly:**
```bash
python3 main.py maps/easy/01_linear_path.txt
python3 main.py maps/hard/03_ultimate_challenge.txt
```

### Run quality checks

```bash
make lint
```

### Debug mode

```bash
make debug MAP=maps/easy/01_linear_path.txt
```

### Clean temporary files

```bash
make clean
```

---

## Map Format

Maps are plain `.txt` files with the following structure:

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
connection: hub-roof1
connection: corridorA-goal [max_link_capacity=2]
# This is a comment
```

**Zone types:**
| Type | Movement Cost | Description |
|------|--------------|-------------|
| `normal` | 1 turn | Standard zone |
| `priority` | 1 turn | Preferred in pathfinding |
| `restricted` | 2 turns | Dangerous/sensitive zone |
| `blocked` | ∞ | Inaccessible — never entered |

---

## Algorithm & Implementation

### Pathfinding — Weighted Dijkstra

The `PathFinder` class implements **Dijkstra's algorithm from scratch** using Python's
`heapq` module as a priority queue. No external graph libraries are used (networkx,
graphlib, etc. are strictly forbidden by the project constraints).

Each zone type has a movement cost:
- `normal` / `priority` → **1 turn**
- `restricted` → **2 turns**
- `blocked` → **∞ (unreachable)**

The algorithm always expands the cheapest node first, guaranteeing the optimal path.
A tie-breaking counter prevents comparison errors between Zone objects in the heap.

**Complexity:** `O((V + E) log V)` where V = zones, E = connections.

---

### Multi-path Discovery — DFS with Backtracking

The `find_all_paths` method uses **Depth-First Search with backtracking** to enumerate
all valid paths between start and end. This allows the simulator to distribute drones
across multiple routes simultaneously.

**Why not just Dijkstra for all paths?**
Dijkstra finds the single optimal path. To find ALL paths, we need DFS — it explores
every branch and backtracks when it reaches a dead end or the goal.

---

### Route Assignment — Greedy Scheduling + Bottleneck Detection

Once all paths are found, the simulator applies a two-step strategy:

**Step 1 — Bottleneck Detection:**
The simulator automatically identifies the most critical bottleneck zones — zones with
`max_drones=1` that appear most frequently across all paths. Using a `Counter`, it
finds the top 3 bottlenecks and selects the shortest path that passes through each one.
This ensures drones are distributed across parallel routes instead of all competing
for the same zone.

**Step 2 — Greedy Assignment:**
1. Sort all paths by length (shortest first)
2. Filter out paths longer than `shortest + 2`
3. Assign each drone to the path with the fewest drones currently assigned

---

### Simulation Engine — Turn-by-turn

The `Simulator` class runs a discrete turn-based loop:

1. **Compute occupancy** — count drones per zone
2. **For each drone** — check if next zone has capacity
3. **Move or wait** — update position, decrement old zone, increment new zone
4. **Print output** — format `D<ID>-<zone>` per turn

**Key rule:** Drones leaving a zone free up capacity **on that same turn**.
This is implemented by decrementing the occupancy of the current zone immediately
when a drone moves, allowing following drones to enter in the same turn.

---

### Challenger — The Impossible Dream (39 turns)

The challenger map has 25 drones and 6454 possible paths. The critical bottleneck
is that all paths converge through `micro_gate1`, `micro_gate2` or `micro_gate3`
— each with `max_drones=1`.

Without optimization, all drones flood through `micro_gate1`, creating an impossible
bottleneck. The bottleneck detection algorithm automatically identifies the 3 micro_gates
as the most critical zones and assigns drones evenly across all three:

```
3 micro_gates × 1 drone/turn = 3 drones/turn throughput
25 drones ÷ 3 = ~9 turns minimum to pass all drones
Result: 39 turns — beats the reference record of 45 turns
```

---

## Performance Results

| Map | Drones | Target | Result | Status |
|-----|--------|--------|--------|--------|
| Easy 1 — Linear path | 2 | ≤ 6 | 4 | SI |
| Easy 2 — Simple fork | 3 | ≤ 6 | 4 | SI |
| Easy 3 — Basic capacity | 4 | ≤ 8 | 4 | SI |
| Medium 1 — Dead end trap | 5 | ≤ 15 | 8 | SI |
| Medium 2 — Circular loop | 6 | ≤ 20 | 13 | SI |
| Medium 3 — Priority puzzle | 4 | ≤ 12 | 6 | SI |
| Hard 1 — Maze nightmare | 8 | ≤ 45 | 15 | SI |
| Hard 2 — Capacity hell | 12 | ≤ 60 | 20 | SI |
| Hard 3 — Ultimate challenge | 15 | ≤ 35 | 28 | SI BONUS |
| Challenger — Impossible Dream | 25 | ≤ 45 | 39 | SI BONUS |

---

## Visual Representation

### Terminal Output (ANSI Colors)

Each simulation turn is printed with colored output based on the zone's color metadata:

```
Turn 1: D1-waypoint1 D2-corridorA
Turn 2: D1-waypoint2 D2-tunnelB
Turn 3: D1-goal D2-goal
```

Each drone movement is colored according to the destination zone's color defined in
the map file (green, red, blue, orange, cyan, etc.).

### Graphical Interface (Matplotlib)

Before the simulation starts, a graphical window displays the full network:
- **Nodes** — each zone drawn as a colored circle at its (x, y) coordinates
- **Edges** — connections drawn as black lines between zones
- **Labels** — zone names displayed above each node

This gives an instant visual overview of the map topology before the simulation runs.

---

## Peer Review Preparation

**Q: Why not use networkx?**
Because the project explicitly forbids any library that helps with graph logic.
networkx provides Dijkstra, BFS, path finding — all of which we implement manually.
This forces a deep understanding of graph algorithms.

**Q: What is the complexity of your Dijkstra?**
`O((V + E) log V)` — V nodes and E edges, with log V factor from the heap operations.

**Q: How do you prevent two drones from occupying the same zone?**
Before moving a drone, we check `occupancy.get(next_zone, 0) < next_zone.max_drones`.
The occupancy dictionary is updated immediately when a drone moves, so subsequent
drones in the same turn see the updated state.

**Q: What happens if there is no valid path?**
`find_path` returns an empty list `[]`. The simulator would detect this and the
drones would never move — in practice, all provided maps have valid paths.

**Q: What is `path_index` used for?**
Instead of modifying the path list (which would be destructive), each drone tracks
its current position in the path with an index. This is safer and preserves the
full route for inspection.

---

## Resources

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Matplotlib documentation](https://matplotlib.org/stable/index.html)
- [Depth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)

### AI Usage

In accordance with project guidelines (Chapter II), AI was used for:
- **Concept clarification** — explaining Dijkstra, DFS backtracking, and heapq behavior
- **Debugging guidance** — identifying logic errors in path reconstruction and occupancy tracking
- **Documentation** — structuring Google-style docstrings and README sections
- **No code was copy-pasted** — all implementations were written and understood by the author
