#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  Traffic Signal Waiting Time Analyzer — Setup & Run Script
# ──────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "🚦  Traffic Signal Waiting Time Analyzer"
echo "    DAA-based Intersection Optimizer"
echo "────────────────────────────────────────"
echo ""

# ── 1. Compile C++ engine ────────────────────────────────────────
echo "▶ Compiling C++ simulation engine..."
g++ -O2 -std=c++17 -o traffic_sim traffic_sim.cpp
echo "  ✓ traffic_sim compiled"

# ── 2. Install Python dependencies ───────────────────────────────
echo ""
echo "▶ Installing Python dependencies..."
pip install streamlit plotly pandas numpy --break-system-packages -q \
  || pip install streamlit plotly pandas numpy -q
echo "  ✓ Dependencies installed"

# ── 3. Quick smoke test ───────────────────────────────────────────
echo ""
echo "▶ Running smoke test (4 lanes, rate=3, 60s)..."
./traffic_sim 4 3 60 10
echo "  ✓ stats.txt and simulation.json generated"
echo ""
cat stats.txt
echo ""

# ── 4. Launch Streamlit ───────────────────────────────────────────
echo "▶ Launching Streamlit frontend..."
echo "  Open http://localhost:8501 in your browser"
echo ""
streamlit run app.py --server.port 8501 --server.headless false
