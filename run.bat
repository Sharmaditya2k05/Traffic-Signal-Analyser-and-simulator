@echo off
:: ──────────────────────────────────────────────────────────────────
::  Traffic Signal Waiting Time Analyzer — Windows Setup & Run
:: ──────────────────────────────────────────────────────────────────

echo.
echo  Traffic Signal Waiting Time Analyzer
echo  DAA-based Intersection Optimizer
echo  ----------------------------------------
echo.

:: ── 1. Check for g++ ─────────────────────────────────────────────
where g++ >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  ERROR: g++ not found in PATH.
    echo.
    echo  Install MinGW-w64:
    echo    1. Go to https://winlibs.com
    echo    2. Download Win64 UCRT release zip
    echo    3. Extract to C:\mingw64
    echo    4. Add C:\mingw64\bin to System PATH
    echo    5. Close this window, reopen, and run again.
    echo.
    pause
    exit /b 1
)

echo  [1/3] Compiling C++ simulation engine...
g++ -O2 -std=c++17 -o traffic_sim.exe traffic_sim.cpp
if %ERRORLEVEL% NEQ 0 (
    echo  ERROR: Compilation failed. Check the error above.
    pause
    exit /b 1
)
echo       traffic_sim.exe compiled OK

:: ── 2. Install Python deps ────────────────────────────────────────
echo.
echo  [2/3] Installing Python dependencies...
pip install streamlit plotly pandas numpy -q
if %ERRORLEVEL% NEQ 0 (
    echo  WARNING: pip install failed. Trying with --user flag...
    pip install streamlit plotly pandas numpy --user -q
)
echo       Dependencies ready

:: ── 3. Launch Streamlit ───────────────────────────────────────────
echo.
echo  [3/3] Launching Streamlit app...
echo        Open http://localhost:8501 in your browser
echo.
streamlit run app.py --server.port 8501
