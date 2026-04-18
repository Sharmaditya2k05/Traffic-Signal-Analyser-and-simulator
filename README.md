# 🚦 Traffic Signal Waiting Time Analyzer

A complete end-to-end system demonstrating **Design & Analysis of Algorithms (DAA)** concepts through a real-world traffic intersection simulation.

---

## 📁 Project Structure

```
traffic_sim/
├── traffic_sim.cpp     ← C++ simulation engine (DAA core)
├── app.py              ← Streamlit frontend + Plotly visualizations
├── run.sh              ← One-click setup & launch script
├── stats.txt           ← Generated: algorithm stats output
├── simulation.json     ← Generated: time-series data for visualization
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Core Logic | C++ (g++, -O2, C++17) |
| Frontend | Python + Streamlit |
| Visualization | Plotly (2D + 3D interactive) |
| Data Exchange | JSON + TXT files |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Streamlit Frontend (app.py)             │
│  - Sidebar: n_lanes, arrival_rate, sim_time          │
│  - Displays: stats, charts, 3D visualization         │
└──────────────────────┬──────────────────────────────┘
                       │ subprocess.run()
                       ▼
┌─────────────────────────────────────────────────────┐
│           C++ Simulation Engine (traffic_sim)        │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────┐    │
│  │Fixed-Time│ │  Greedy  │ │  Priority Queue   │    │
│  │  O(N)    │ │  O(N²)   │ │  O(N log N)       │    │
│  └──────────┘ └──────────┘ └───────────────────┘    │
│                                                      │
│  Lane Queues → Vehicles → Metrics → Prefix Sum       │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
         stats.txt       simulation.json
```

---

## 🧩 DAA Concepts Implemented

### 1. Queue — Vehicle Modeling
Each traffic lane is a **FIFO queue** of vehicles.  
- `enqueue` → vehicle arrives: **O(1)**  
- `dequeue` → vehicle passes signal: **O(1)**

### 2. Greedy Algorithm — Signal Optimization
At each time step, scan all lanes and give green to the **lane with the most vehicles**.
- Per-step selection: **O(N)** where N = number of lanes  
- Full simulation: **O(T × N) = O(N²)**  
- Greedy choice: locally optimal (max queue gets served first)

### 3. Priority Queue — Efficient Scheduling
Lanes are scored by `queue_size × 2 + cumulative_wait`.  
A **max-heap** selects the highest-priority lane each step.  
- Heap insertion + extraction: **O(log N)**  
- Full simulation: **O(T × N log N)**

### 4. Prefix Sum — Cumulative Analysis
After simulation, compute a running total of all queue lengths:  
```
PS[i] = PS[i-1] + TotalQueue[i]
```
- Build: **O(N)**  
- Any range-sum query: **O(1)**  
Used for efficient traffic analytics over arbitrary time windows.

---

## 📊 Output Files

### `stats.txt`
```
Total Vehicles: 58

Average Waiting Time:
  Fixed:    20.55 s
  Greedy:   20.07 s
  Priority: 14.38 s

Max Waiting Time: ...

Time Complexity (Theoretical): ...
Overall Complexity: ...
Execution Time (Measured): ...

Best Algorithm: Priority
```

### `simulation.json`
```json
{
  "time": [0, 1, 2, ...],
  "fixed_lane_1": [2, 3, 5, ...],
  "greedy_lane_1": [1, 2, 4, ...],
  "priority_lane_1": [0, 1, 2, ...],
  "avg_wait": {"fixed": 20.55, "greedy": 20.07, "priority": 14.38},
  ...
}
```

---

## 🖥️ Frontend Features

| Feature | Description |
|---------|-------------|
| Sidebar controls | n_lanes, arrival_rate, sim_time, green_duration |
| Metric cards | Total vehicles, best avg wait, exec time |
| Algorithm cards | Per-algo stats with best-algorithm highlight |
| Bar charts | Avg wait comparison + execution time |
| Queue length tabs | Per-lane queue over time (Fixed / Greedy / Priority) |
| Prefix Sum chart | Cumulative queue for all algorithms |
| 3D Scatter plot | Time × Lane × Queue (interactive Plotly) |
| Complexity table | Theoretical + measured complexity |
| Raw stats viewer | Full stats.txt in expandable section |

---

## 🚀 Quick Start

### Prerequisites
```bash
sudo apt install g++ python3 python3-pip   # Ubuntu/Debian
brew install gcc python                    # macOS
```

### Run
```bash
chmod +x run.sh
./run.sh
# Then open http://localhost:8501
```

### Manual
```bash
# Compile
g++ -O2 -std=c++17 -o traffic_sim traffic_sim.cpp

# Install Python deps
pip install streamlit plotly pandas numpy

# Run simulation directly (optional)
./traffic_sim 4 3 60 10   # lanes rate time green_duration

# Launch frontend
streamlit run app.py
```

---


---

## 🪟 Windows Setup (Important)

The zip includes **source code only** — you must compile the C++ engine on your machine.

### Step 1 — Install MinGW-w64 (g++ for Windows)

1. Go to **https://winlibs.com**
2. Download the latest **Win64, UCRT** release (`.zip`)
3. Extract to `C:\mingw64`
4. Open **System Properties → Environment Variables**
5. Edit `Path` → Add `C:\mingw64\bin`
6. Open a **new** terminal and verify: `g++ --version`

### Step 2 — Run the app

```bat
:: Double-click run.bat  OR  run in terminal:
run.bat
```

The batch file will:
- Compile `traffic_sim.cpp` → `traffic_sim.exe` automatically
- Install Python dependencies
- Launch the Streamlit app at http://localhost:8501

### Troubleshooting

| Error | Fix |
|-------|-----|
| `g++ not found` | Add MinGW `bin/` to PATH, restart terminal |
| `WinError 193` | You're trying to run the Linux binary — delete `traffic_sim` (no extension), let app recompile |
| `streamlit not found` | Run `pip install streamlit plotly pandas numpy` |
| `ModuleNotFoundError` | Use `pip install --user streamlit plotly pandas numpy` |

## ⚠️ Constraints Satisfied

- ✅ Large simulation inputs handled efficiently  
- ✅ No brute-force: O(1) queue ops, O(log N) priority scheduling  
- ✅ Modular C++ design: vehicles, lanes, algorithms separated  
- ✅ JSON data exchange for frontend–backend decoupling  
- ✅ All 4 DAA concepts visually demonstrated

---

## 🧠 Algorithm Summary Table

| Algorithm | Complexity | Best For | Limitation |
|-----------|-----------|----------|------------|
| Fixed-Time | O(N) | Low traffic, predictable | Ignores queue state |
| Greedy | O(N²) | Medium traffic | Myopic, no fairness |
| Priority Queue | O(N log N) | Heavy traffic | Slightly more overhead |
| Prefix Sum | O(N) build, O(1) query | Analytics | Read-only, static array |
