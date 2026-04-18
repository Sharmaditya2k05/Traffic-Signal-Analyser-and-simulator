import streamlit as st
import subprocess
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
import re

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Traffic Signal Analyzer",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

/* ── Root theme ── */
:root {
  --bg:         #0a0e17;
  --surface:    #111827;
  --surface2:   #1a2233;
  --border:     #1e3a5f;
  --accent:     #00d4ff;
  --accent2:    #ff6b35;
  --accent3:    #39ff14;
  --text:       #e2e8f0;
  --muted:      #64748b;
  --red:        #ff4444;
  --yellow:     #ffd700;
  --green:      #39ff14;
}

.stApp { background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }
.stApp > header { background: transparent !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0d1520 0%, #111827 100%);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stMarkdown h2 { color: var(--accent); font-family: 'Rajdhani', sans-serif; letter-spacing: 2px; }

/* Headers */
h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 1px; }
h1 { color: var(--accent) !important; text-shadow: 0 0 20px rgba(0,212,255,0.4); }

/* Metric cards */
.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 3px solid var(--accent);
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin: 0.4rem 0;
  position: relative;
  overflow: hidden;
}
.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  animation: scan 3s linear infinite;
}
@keyframes scan { 0%{opacity:0} 50%{opacity:1} 100%{opacity:0} }
.metric-label { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 2px; }
.metric-value { font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; font-weight: 700; color: var(--accent); line-height: 1.1; }
.metric-sub   { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }

/* Algo cards */
.algo-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  margin: 0.4rem 0;
}
.algo-card.best { border-color: var(--green); box-shadow: 0 0 12px rgba(57,255,20,0.15); }
.algo-name { font-family: 'Rajdhani', sans-serif; font-size: 1.2rem; font-weight: 700; color: var(--text); }
.algo-badge { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; padding: 2px 8px; border-radius: 3px; background: rgba(0,212,255,0.1); color: var(--accent); border: 1px solid var(--accent); }
.algo-badge.best-badge { background: rgba(57,255,20,0.1); color: var(--green); border-color: var(--green); }

/* Complexity table */
.complexity-table { width: 100%; border-collapse: collapse; font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; }
.complexity-table th { background: var(--surface2); color: var(--accent); padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); }
.complexity-table td { padding: 7px 12px; border-bottom: 1px solid rgba(30,58,95,0.5); color: var(--text); }
.complexity-table tr:hover td { background: rgba(0,212,255,0.04); }
.o-n2  { color: var(--red); }
.o-nlogn { color: var(--yellow); }
.o-n   { color: #60a5fa; }
.o-1   { color: var(--green); }

/* Signal animation */
.signal-container { display: flex; gap: 8px; align-items: center; justify-content: center; padding: 12px; }
.signal-dot { width: 14px; height: 14px; border-radius: 50%; }
.signal-red    { background: var(--red);    box-shadow: 0 0 8px var(--red); }
.signal-yellow { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); }
.signal-green  { background: var(--green);  box-shadow: 0 0 8px var(--green); animation: pulse-green 1.5s ease-in-out infinite; }
@keyframes pulse-green { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Section headers */
.section-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 3px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
  margin: 1.2rem 0 0.8rem;
}

/* Run button */
.stButton > button {
  background: linear-gradient(135deg, #003d5c 0%, #00d4ff 100%) !important;
  color: #000 !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  letter-spacing: 2px !important;
  border: none !important;
  border-radius: 6px !important;
  padding: 0.6rem 2rem !important;
  width: 100% !important;
  text-transform: uppercase;
  transition: all 0.2s;
}
.stButton > button:hover { box-shadow: 0 0 20px rgba(0,212,255,0.5) !important; transform: translateY(-1px); }

/* Plotly bg fix */
.js-plotly-plot { border-radius: 8px; border: 1px solid var(--border); }

/* Slider label */
.stSlider label { color: var(--muted) !important; font-size: 0.8rem; }

/* Info box */
.info-box {
  background: rgba(0,212,255,0.05);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  padding: 0.8rem 1rem;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.78rem;
  color: var(--muted);
}

/* status bar */
.status-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
      <div style="font-family:'Rajdhani',sans-serif; font-size:1.8rem; font-weight:700; color:#00d4ff; letter-spacing:3px;">🚦 TRAFFIC</div>
      <div style="font-family:'Rajdhani',sans-serif; font-size:1rem; color:#64748b; letter-spacing:5px;">ANALYZER</div>
      <div class="signal-container">
        <div class="signal-dot signal-red"></div>
        <div class="signal-dot signal-yellow"></div>
        <div class="signal-dot signal-green"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚙ Simulation Parameters</div>', unsafe_allow_html=True)

    n_lanes = st.slider("Number of Lanes", min_value=2, max_value=8, value=4, help="Lanes at the intersection")
    arrival_rate = st.slider("Vehicle Arrival Rate (per unit)", min_value=1, max_value=10, value=3, help="Average vehicles arriving per time unit")
    sim_time = st.slider("Simulation Duration (s)", min_value=30, max_value=300, value=60, step=10)
    green_duration = st.slider("Fixed Green Duration (s)", min_value=2, max_value=30, value=10, help="Used only for Fixed-Time algorithm")

    st.markdown('<div class="section-title">📐 DAA Concepts</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
      <b style="color:#00d4ff">Queue</b> → Vehicle modeling<br>
      <b style="color:#ffd700">Greedy</b> → Max-queue selection<br>
      <b style="color:#ff6b35">Priority Q</b> → Weighted scheduling<br>
      <b style="color:#39ff14">Prefix Sum</b> → Cumulative wait
    </div>
    """, unsafe_allow_html=True)

    run_btn = st.button("▶  RUN SIMULATION")

# ── Main header ───────────────────────────────────────────────────────────────
st.markdown('<h1 style="margin-bottom:0">Traffic Signal Waiting Time Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b; font-family:\'Share Tech Mono\',monospace; font-size:0.8rem; margin-top:0">DAA-based multi-lane intersection optimizer · C++ Engine · Real-time Visualization</p>', unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
import platform
IS_WINDOWS = platform.system() == "Windows"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# On Windows the compiled binary is traffic_sim.exe
BIN_NAME   = "traffic_sim.exe" if IS_WINDOWS else "traffic_sim"
CPP_BIN    = os.path.join(SCRIPT_DIR, BIN_NAME)
CPP_SRC    = os.path.join(SCRIPT_DIR, "traffic_sim.cpp")

def find_compiler():
    """Find g++ or cl.exe on Windows; return (compiler, extra_args) or None."""
    import shutil
    for compiler in ["g++", "g++.exe", "c++"]:
        if shutil.which(compiler):
            return compiler, ["-O2", "-std=c++17", "-o", CPP_BIN, CPP_SRC]
    # MSVC fallback
    if IS_WINDOWS:
        cl = shutil.which("cl")
        if cl:
            return cl, [f"/Fe:{CPP_BIN}", CPP_SRC, "/EHsc", "/O2"]
    return None, None

def compile_cpp():
    """Compile traffic_sim.cpp → native binary for the current OS."""
    compiler, args = find_compiler()
    if compiler is None:
        return False, (
            "❌ No C++ compiler found!\n\n"
            "**Windows:** Install MinGW-w64 and add to PATH:\n"
            "  https://winlibs.com  →  download → extract → add `bin/` to PATH\n\n"
            "Then restart your terminal and re-run `streamlit run app.py`."
        )
    cmd = [compiler] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRIPT_DIR)
    if result.returncode != 0:
        return False, result.stderr or result.stdout
    return True, ""

def needs_compile():
    """True if binary is missing OR source is newer than binary."""
    if not os.path.exists(CPP_BIN):
        return True
    return os.path.getmtime(CPP_SRC) > os.path.getmtime(CPP_BIN)

def run_simulation(n_lanes, arrival_rate, sim_time, green_dur):
    if needs_compile():
        ok, err = compile_cpp()
        if not ok:
            return False, err
    result = subprocess.run(
        [CPP_BIN, str(n_lanes), str(arrival_rate), str(sim_time), str(green_dur)],
        capture_output=True, text=True, cwd=SCRIPT_DIR
    )
    return result.returncode == 0, (result.stderr or result.stdout)

def parse_stats(path):
    stats = {}
    try:
        with open(path) as f:
            text = f.read()
        stats['raw'] = text
        # total vehicles
        m = re.search(r'Total Vehicles: (\d+)', text)
        if m: stats['total'] = int(m.group(1))
        # avg wait
        for algo in ['Fixed', 'Greedy', 'Priority']:
            m = re.search(rf'{algo}:\s+([\d.]+) s', text)
            if m: stats[f'avg_{algo.lower()}'] = float(m.group(1))
        # max wait
        for algo in ['Fixed', 'Greedy', 'Priority']:
            m = re.search(rf'{algo}:\s+([\d.]+) s', text)
        # exec time
        for algo in ['Fixed', 'Greedy', 'Priority']:
            m = re.search(rf'{algo}:\s+([\d.]+) ms', text)
            if m: stats[f'exec_{algo.lower()}'] = float(m.group(1))
        # best
        m = re.search(r'Best Algorithm: (\w+)', text)
        if m: stats['best'] = m.group(1)

        # re-parse more carefully
        lines = text.split('\n')
        section = None
        for line in lines:
            line = line.strip()
            if 'Average Waiting Time' in line: section = 'avg'
            elif 'Max Waiting Time' in line: section = 'max'
            elif 'Execution Time' in line: section = 'exec'
            elif line.startswith('Fixed:'):
                val = float(re.search(r'[\d.]+', line).group())
                if section == 'avg': stats['avg_fixed'] = val
                elif section == 'max': stats['max_fixed'] = val
                elif section == 'exec': stats['exec_fixed'] = val
            elif line.startswith('Greedy:'):
                val = float(re.search(r'[\d.]+', line).group())
                if section == 'avg': stats['avg_greedy'] = val
                elif section == 'max': stats['max_greedy'] = val
                elif section == 'exec': stats['exec_greedy'] = val
            elif line.startswith('Priority:'):
                val = float(re.search(r'[\d.]+', line).group())
                if section == 'avg': stats['avg_priority'] = val
                elif section == 'max': stats['max_priority'] = val
                elif section == 'exec': stats['exec_priority'] = val
    except Exception as e:
        stats['error'] = str(e)
    return stats

def load_json(path):
    with open(path) as f:
        return json.load(f)

COLORS = {
    'fixed':    '#60a5fa',
    'greedy':   '#ffd700',
    'priority': '#39ff14',
}
ALGO_NAMES = {'fixed': 'Fixed-Time', 'greedy': 'Greedy', 'priority': 'Priority Q'}

def plotly_theme():
    return dict(
        paper_bgcolor='rgba(17,24,39,0)',
        plot_bgcolor='rgba(17,24,39,0.6)',
        font=dict(family='Share Tech Mono', color='#94a3b8', size=11),
        xaxis=dict(gridcolor='rgba(30,58,95,0.5)', linecolor='#1e3a5f'),
        yaxis=dict(gridcolor='rgba(30,58,95,0.5)', linecolor='#1e3a5f'),
        margin=dict(l=40, r=20, t=40, b=40),
    )

# ── Run simulation ─────────────────────────────────────────────────────────
stats_path = os.path.join(SCRIPT_DIR, "stats.txt")
json_path  = os.path.join(SCRIPT_DIR, "simulation.json")

if run_btn:
    # Step 1: compile if needed
    if needs_compile():
        compiler, _ = find_compiler()
        if compiler is None:
            st.error(
                "**No C++ compiler found.**\n\n"
                "**Windows (MinGW-w64):** Download from https://winlibs.com → extract → "
                "add `bin\\` folder to System PATH → restart terminal.\n\n"
                "**macOS:** `xcode-select --install`  |  **Linux:** `sudo apt install g++`"
            )
            st.stop()
        with st.spinner(f"🔧 Compiling C++ engine with {compiler}..."):
            ok, err = compile_cpp()
        if not ok:
            st.error(f"**Compilation failed:**\n```\n{err}\n```")
            st.stop()

    prog = st.progress(0, text="Initializing simulation...")
    for i in range(40):
        time.sleep(0.015)
        prog.progress(i + 1, text="Running C++ simulation engine...")

    ok, err = run_simulation(n_lanes, arrival_rate, sim_time, green_duration)

    for i in range(40, 100):
        time.sleep(0.01)
        prog.progress(i + 1, text="Processing results...")

    prog.empty()

    if not ok:
        st.error(f"Simulation failed: {err}")
        st.stop()

    st.success("✅ Simulation complete!")

# ── Display results if files exist ────────────────────────────────────────────
if os.path.exists(stats_path) and os.path.exists(json_path):
    stats = parse_stats(stats_path)
    data  = load_json(json_path)
    times = data['time']
    n_l   = data.get('n_lanes', 4)
    best  = stats.get('best', 'Priority')

    # ── Status bar ──
    st.markdown(f"""
    <div class="status-bar">
      <span>🟢 SIMULATION COMPLETE</span>
      <span>LANES: {n_l} &nbsp;|&nbsp; VEHICLES: {stats.get('total','—')} &nbsp;|&nbsp; DURATION: {data.get('sim_time','—')}s</span>
      <span>BEST: {best.upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric cards ──
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Total Vehicles</div>
          <div class="metric-value">{stats.get('total','—')}</div>
          <div class="metric-sub">processed in simulation</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        best_avg = min(stats.get('avg_fixed',99), stats.get('avg_greedy',99), stats.get('avg_priority',99))
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Best Avg Wait</div>
          <div class="metric-value">{best_avg:.1f}s</div>
          <div class="metric-sub">algorithm: {best}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Lanes Modeled</div>
          <div class="metric-value">{n_l}</div>
          <div class="metric-sub">queue structures</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        total_exec = sum([stats.get('exec_fixed',0), stats.get('exec_greedy',0), stats.get('exec_priority',0)])
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Total Exec Time</div>
          <div class="metric-value">{total_exec:.2f}<span style="font-size:1rem">ms</span></div>
          <div class="metric-sub">all 3 algorithms</div>
        </div>""", unsafe_allow_html=True)

    # ── Algorithm comparison ──
    st.markdown('<div class="section-title">🏆 Algorithm Comparison</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)
    algo_data = [
        ('fixed',    ca, 'O(N)',       'Round-robin fixed green time'),
        ('greedy',   cb, 'O(N²)',      'Max queue gets green each step'),
        ('priority', cc, 'O(N log N)', 'Weighted queue + wait scoring'),
    ]
    for algo, col, complexity, desc in algo_data:
        is_best = algo.capitalize() == best or algo == best.lower()
        avg = stats.get(f'avg_{algo}', 0)
        exc = stats.get(f'exec_{algo}', 0)
        badge_cls = "best-badge" if is_best else ""
        card_cls  = "algo-card best" if is_best else "algo-card"
        with col:
            st.markdown(f"""
            <div class="{card_cls}">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
                <span class="algo-name">{ALGO_NAMES[algo]}</span>
                <span class="algo-badge {badge_cls}">{'★ BEST' if is_best else complexity}</span>
              </div>
              <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#64748b; margin-bottom:8px">{desc}</div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px">
                <div>
                  <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase">Avg Wait</div>
                  <div style="font-size:1.3rem; font-family:'Rajdhani',sans-serif; font-weight:700; color:{COLORS[algo]}">{avg:.2f}s</div>
                </div>
                <div>
                  <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase">Exec Time</div>
                  <div style="font-size:1.3rem; font-family:'Rajdhani',sans-serif; font-weight:700; color:#94a3b8">{exc:.3f}ms</div>
                </div>
              </div>
              <div style="margin-top:8px; background:rgba(0,0,0,0.3); border-radius:4px; overflow:hidden; height:4px">
                <div style="width:{min(100, avg/max(stats.get('avg_fixed',1),stats.get('avg_greedy',1),stats.get('avg_priority',1))*100):.0f}%; height:4px; background:{COLORS[algo]}; border-radius:4px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Charts row 1: bar chart + execution time ──
    st.markdown('<div class="section-title">📈 Visualizations</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns(2)

    with ch1:
        fig_bar = go.Figure()
        algos = ['Fixed-Time', 'Greedy', 'Priority Q']
        avgs  = [stats.get('avg_fixed',0), stats.get('avg_greedy',0), stats.get('avg_priority',0)]
        clrs  = [COLORS['fixed'], COLORS['greedy'], COLORS['priority']]
        fig_bar.add_trace(go.Bar(
            x=algos, y=avgs,
            marker=dict(color=clrs, line=dict(width=0)),
            text=[f'{v:.2f}s' for v in avgs],
            textposition='outside',
            textfont=dict(family='Share Tech Mono', size=11, color='#e2e8f0'),
        ))
        best_idx = avgs.index(min(avgs))
        fig_bar.add_annotation(x=algos[best_idx], y=avgs[best_idx]+1,
            text="★ BEST", showarrow=False,
            font=dict(family='Share Tech Mono', size=10, color='#39ff14'))
        fig_bar.update_layout(
            title=dict(text='Average Waiting Time by Algorithm', font=dict(family='Rajdhani', size=14, color='#00d4ff')),
            yaxis_title='Avg Wait (s)',
            showlegend=False, height=320,
            **plotly_theme()
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with ch2:
        execs = [stats.get('exec_fixed',0), stats.get('exec_greedy',0), stats.get('exec_priority',0)]
        fig_exec = go.Figure(go.Bar(
            x=algos, y=execs,
            marker=dict(color=clrs, opacity=0.85),
            text=[f'{v:.3f}ms' for v in execs],
            textposition='outside',
            textfont=dict(family='Share Tech Mono', size=11, color='#e2e8f0'),
        ))
        fig_exec.update_layout(
            title=dict(text='Execution Time (ms) — C++ Measured', font=dict(family='Rajdhani', size=14, color='#00d4ff')),
            yaxis_title='Time (ms)',
            showlegend=False, height=320,
            **plotly_theme()
        )
        st.plotly_chart(fig_exec, use_container_width=True)

    # ── Queue lengths over time ──
    st.markdown("**Queue Length vs Time — Per Algorithm**")
    tab1, tab2, tab3 = st.tabs(["🔵 Fixed-Time", "🟡 Greedy", "🟢 Priority Queue"])

    def queue_fig(prefix, color, title):
        fig = go.Figure()
        for l in range(1, n_l + 1):
            key = f'{prefix}_lane_{l}'
            if key in data:
                alpha = 1.0 if l == 1 else max(0.4, 1.0 - l * 0.15)
                fig.add_trace(go.Scatter(
                    x=times, y=data[key], name=f'Lane {l}',
                    mode='lines',
                    line=dict(width=2, color=color),
                    opacity=alpha,
                    fill='tozeroy' if l == 1 else 'none',
                    fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.05)' if l == 1 else None,
                ))
        fig.update_layout(
            title=dict(text=title, font=dict(family='Rajdhani', size=14, color='#00d4ff')),
            xaxis_title='Time (s)', yaxis_title='Queue Length',
            height=320, **plotly_theme()
        )
        return fig

    with tab1:
        st.plotly_chart(queue_fig('fixed',    '#60a5fa', 'Fixed-Time: Queue Length per Lane'),    use_container_width=True)
    with tab2:
        st.plotly_chart(queue_fig('greedy',   '#ffd700', 'Greedy: Queue Length per Lane'),         use_container_width=True)
    with tab3:
        st.plotly_chart(queue_fig('priority', '#39ff14', 'Priority Q: Queue Length per Lane'),     use_container_width=True)

    # ── Prefix Sum ──
    st.markdown('<div class="section-title">∑ Prefix Sum Analysis</div>', unsafe_allow_html=True)
    psc1, psc2 = st.columns(2)
    with psc1:
        fig_ps = go.Figure()
        for algo, clr in COLORS.items():
            prefix = algo
            total_q = [0] * len(times)
            for l in range(1, n_l + 1):
                key = f'{prefix}_lane_{l}'
                if key in data:
                    total_q = [total_q[i] + data[key][i] for i in range(len(times))]
            # prefix sum
            ps = [0] * (len(total_q) + 1)
            for i, v in enumerate(total_q): ps[i+1] = ps[i] + v
            fig_ps.add_trace(go.Scatter(
                x=times, y=ps[1:], name=ALGO_NAMES[algo],
                mode='lines', line=dict(color=clr, width=2)
            ))
        fig_ps.update_layout(
            title=dict(text='Cumulative Total Queue (Prefix Sum)', font=dict(family='Rajdhani', size=14, color='#00d4ff')),
            xaxis_title='Time (s)', yaxis_title='Cumulative Queue',
            height=300, **plotly_theme()
        )
        st.plotly_chart(fig_ps, use_container_width=True)

    with psc2:
        st.markdown("""
        <div style="padding: 1rem 0">
        <div class="algo-name" style="margin-bottom:0.5rem">Prefix Sum Formula</div>
        <div class="info-box" style="margin-bottom:0.6rem">
          PS[i] = PS[i-1] + Q[i]<br>
          Range query: Σ Q[l..r] = PS[r+1] − PS[l]<br><br>
          <span style="color:#39ff14">Time:  O(N) build · O(1) query</span><br>
          <span style="color:#60a5fa">Space: O(N)</span>
        </div>
        <div class="info-box">
          Used to efficiently compute cumulative waiting time
          over any time window without re-iterating the array.
          Essential for large-scale traffic analytics.
        </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 3D Visualization ──
    st.markdown('<div class="section-title">🌐 3D Queue Visualization (Bonus)</div>', unsafe_allow_html=True)

    algo_3d = st.selectbox("Select algorithm for 3D view",
                            ['Fixed-Time', 'Greedy', 'Priority Queue'],
                            index=2)
    prefix_map = {'Fixed-Time': 'fixed', 'Greedy': 'greedy', 'Priority Queue': 'priority'}
    prefix_3d = prefix_map[algo_3d]
    color_3d  = COLORS[prefix_3d]

    X, Y, Z = [], [], []
    for l in range(1, n_l + 1):
        key = f'{prefix_3d}_lane_{l}'
        if key in data:
            for t, q in zip(times, data[key]):
                X.append(t)
                Y.append(l)
                Z.append(q)

    fig_3d = go.Figure(data=[go.Scatter3d(
        x=X, y=Y, z=Z,
        mode='markers',
        marker=dict(
            size=3,
            color=Z,
            colorscale=[[0,'#0a0e17'],[0.3, color_3d],[1,'#ffffff']],
            opacity=0.8,
            colorbar=dict(title='Queue Len', tickfont=dict(family='Share Tech Mono', color='#94a3b8', size=9)),
        )
    )])
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(title='Time (s)', backgroundcolor='#111827', gridcolor='#1e3a5f', color='#94a3b8'),
            yaxis=dict(title='Lane',     backgroundcolor='#111827', gridcolor='#1e3a5f', color='#94a3b8'),
            zaxis=dict(title='Queue',    backgroundcolor='#111827', gridcolor='#1e3a5f', color='#94a3b8'),
            bgcolor='#111827',
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Share Tech Mono', color='#94a3b8'),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        title=dict(text=f'3D Queue Landscape — {algo_3d}', font=dict(family='Rajdhani', size=15, color='#00d4ff')),
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    # ── Complexity Table ──
    st.markdown('<div class="section-title">⚡ Time Complexity Analysis</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="complexity-table">
      <tr><th>Operation</th><th>Algorithm</th><th>Theoretical</th><th>DAA Concept</th></tr>
      <tr><td>Enqueue / Dequeue</td><td>All</td><td class="o-1">O(1)</td><td>Queue</td></tr>
      <tr><td>Full Simulation</td><td>Fixed-Time</td><td class="o-n">O(N)</td><td>Linear scan</td></tr>
      <tr><td>Full Simulation</td><td>Greedy</td><td class="o-n2">O(N²)</td><td>Greedy selection per step</td></tr>
      <tr><td>Full Simulation</td><td>Priority Queue</td><td class="o-nlogn">O(N log N)</td><td>Heap-based scheduling</td></tr>
      <tr><td>Prefix Sum Build</td><td>All</td><td class="o-n">O(N)</td><td>Prefix Sum</td></tr>
      <tr><td>Prefix Sum Query</td><td>All</td><td class="o-1">O(1)</td><td>Prefix Sum</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # ── Raw stats ──
    with st.expander("📄 Raw stats.txt output"):
        st.code(stats.get('raw', ''), language='text')

else:
    # ── Welcome screen ──
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; background:rgba(17,24,39,0.5); border:1px solid #1e3a5f; border-radius:12px; margin-top:2rem">
      <div style="font-size:4rem; margin-bottom:1rem">🚦</div>
      <div style="font-family:'Rajdhani',sans-serif; font-size:2rem; color:#00d4ff; letter-spacing:2px; margin-bottom:0.5rem">READY TO SIMULATE</div>
      <div style="color:#64748b; font-family:'Share Tech Mono',monospace; font-size:0.85rem">
        Configure parameters in the sidebar and click <b style="color:#00d4ff">RUN SIMULATION</b>
      </div>
      <div style="margin-top:2rem; display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; max-width:600px; margin-left:auto; margin-right:auto">
        <div style="background:#1a2233; border:1px solid #1e3a5f; border-radius:8px; padding:1rem">
          <div style="font-size:1.5rem">🗂</div>
          <div style="font-family:'Rajdhani',sans-serif; color:#60a5fa; font-size:0.9rem">Queue</div>
          <div style="font-size:0.7rem; color:#64748b">Vehicle modeling</div>
        </div>
        <div style="background:#1a2233; border:1px solid #1e3a5f; border-radius:8px; padding:1rem">
          <div style="font-size:1.5rem">⚡</div>
          <div style="font-family:'Rajdhani',sans-serif; color:#ffd700; font-size:0.9rem">Greedy</div>
          <div style="font-size:0.7rem; color:#64748b">Max-queue green</div>
        </div>
        <div style="background:#1a2233; border:1px solid #1e3a5f; border-radius:8px; padding:1rem">
          <div style="font-size:1.5rem">🏆</div>
          <div style="font-family:'Rajdhani',sans-serif; color:#ff6b35; font-size:0.9rem">Priority Q</div>
          <div style="font-size:0.7rem; color:#64748b">Heap scheduling</div>
        </div>
        <div style="background:#1a2233; border:1px solid #1e3a5f; border-radius:8px; padding:1rem">
          <div style="font-size:1.5rem">∑</div>
          <div style="font-family:'Rajdhani',sans-serif; color:#39ff14; font-size:0.9rem">Prefix Sum</div>
          <div style="font-size:0.7rem; color:#64748b">Fast analytics</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
