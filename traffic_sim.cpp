#include <iostream>
#include <fstream>
#include <queue>
#include <vector>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <sstream>
#include <cmath>
#include <random>
#include <iomanip>

using namespace std;
using namespace chrono;

// ─── Vehicle ───────────────────────────────────────────────────────────────
struct Vehicle {
    int id;
    int arrival_time;
    int lane;
};

// ─── Lane (Queue-based) ────────────────────────────────────────────────────
struct Lane {
    queue<Vehicle> vehicles;
    int total_waiting = 0;
    int max_waiting   = 0;
    int processed     = 0;

    void add(Vehicle v) { vehicles.push(v); }

    // serve one vehicle, return waiting time
    int serve(int current_time) {
        if (vehicles.empty()) return 0;
        Vehicle v = vehicles.front();
        vehicles.pop();
        int wait = current_time - v.arrival_time;
        total_waiting += wait;
        if (wait > max_waiting) max_waiting = wait;
        processed++;
        return wait;
    }

    int size() const { return (int)vehicles.size(); }
};

// ─── Helpers ───────────────────────────────────────────────────────────────
vector<Vehicle> generate_vehicles(int n_lanes, int arrival_rate, int sim_time, int seed = 42) {
    mt19937 rng(seed);
    uniform_real_distribution<> prob(0.0, 1.0);
    uniform_int_distribution<>  lane_pick(0, n_lanes - 1);
    vector<Vehicle> all;
    int id = 0;
    for (int t = 0; t < sim_time; t++) {
        // Poisson-like: each time unit produces 'arrival_rate' vehicles on average
        for (int k = 0; k < arrival_rate * 2; k++) {
            if (prob(rng) < 0.5) {
                all.push_back({id++, t, lane_pick(rng)});
            }
        }
    }
    return all;
}

// ─── Algorithm A: Fixed-Time ──────────────────────────────────────────────
struct Result {
    double avg_wait;
    double max_wait;
    int    total_proc;
    double exec_ms;
    vector<vector<int>> queue_lengths; // [time][lane]
};

Result fixed_time(int n_lanes, int arrival_rate, int sim_time, int green_duration) {
    auto t0 = high_resolution_clock::now();

    vector<Lane> lanes(n_lanes);
    auto vehicles = generate_vehicles(n_lanes, arrival_rate, sim_time);

    int total_w = 0, max_w = 0, proc = 0;
    vector<vector<int>> ql(sim_time, vector<int>(n_lanes, 0));

    for (int t = 0; t < sim_time; t++) {
        // Arrivals
        for (auto& v : vehicles)
            if (v.arrival_time == t)
                lanes[v.lane].add(v);

        // Which lane gets green (round-robin fixed)
        int green_lane = (t / green_duration) % n_lanes;
        int w = lanes[green_lane].serve(t);
        if (w > 0) { total_w += w; if (w > max_w) max_w = w; proc++; }

        for (int l = 0; l < n_lanes; l++) ql[t][l] = lanes[l].size();
    }

    auto t1 = high_resolution_clock::now();
    double exec = duration<double, milli>(t1 - t0).count();

    double avg = proc > 0 ? (double)total_w / proc : 0;
    return {avg, (double)max_w, proc, exec, ql};
}

// ─── Algorithm B: Greedy ──────────────────────────────────────────────────
Result greedy(int n_lanes, int arrival_rate, int sim_time) {
    auto t0 = high_resolution_clock::now();

    vector<Lane> lanes(n_lanes);
    auto vehicles = generate_vehicles(n_lanes, arrival_rate, sim_time);

    int total_w = 0, max_w = 0, proc = 0;
    vector<vector<int>> ql(sim_time, vector<int>(n_lanes, 0));

    for (int t = 0; t < sim_time; t++) {
        for (auto& v : vehicles)
            if (v.arrival_time == t)
                lanes[v.lane].add(v);

        // Greedy: pick lane with max queue — O(N)
        int best = 0;
        for (int l = 1; l < n_lanes; l++)
            if (lanes[l].size() > lanes[best].size()) best = l;

        int w = lanes[best].serve(t);
        if (w > 0) { total_w += w; if (w > max_w) max_w = w; proc++; }

        for (int l = 0; l < n_lanes; l++) ql[t][l] = lanes[l].size();
    }

    auto t1 = high_resolution_clock::now();
    double exec = duration<double, milli>(t1 - t0).count();

    double avg = proc > 0 ? (double)total_w / proc : 0;
    return {avg, (double)max_w, proc, exec, ql};
}

// ─── Algorithm C: Priority Queue Scheduling ───────────────────────────────
struct LanePrio {
    int lane, score;
    bool operator<(const LanePrio& o) const { return score < o.score; }
};

Result priority_sched(int n_lanes, int arrival_rate, int sim_time) {
    auto t0 = high_resolution_clock::now();

    vector<Lane> lanes(n_lanes);
    auto vehicles = generate_vehicles(n_lanes, arrival_rate, sim_time);

    int total_w = 0, max_w = 0, proc = 0;
    vector<vector<int>> ql(sim_time, vector<int>(n_lanes, 0));

    for (int t = 0; t < sim_time; t++) {
        for (auto& v : vehicles)
            if (v.arrival_time == t)
                lanes[v.lane].add(v);

        // Priority queue: score = queue_size * 2 + avg_wait — O(N log N)
        priority_queue<LanePrio> pq;
        for (int l = 0; l < n_lanes; l++) {
            int sz  = lanes[l].size();
            int score = sz * 2 + (sz > 0 ? lanes[l].total_waiting : 0);
            pq.push({l, score});
        }

        int best = pq.top().lane;
        int w = lanes[best].serve(t);
        if (w > 0) { total_w += w; if (w > max_w) max_w = w; proc++; }

        for (int l = 0; l < n_lanes; l++) ql[t][l] = lanes[l].size();
    }

    auto t1 = high_resolution_clock::now();
    double exec = duration<double, milli>(t1 - t0).count();

    double avg = proc > 0 ? (double)total_w / proc : 0;
    return {avg, (double)max_w, proc, exec, ql};
}

// ─── Prefix Sum Analysis ──────────────────────────────────────────────────
vector<int> prefix_sum(const vector<int>& arr) {
    vector<int> ps(arr.size() + 1, 0);
    for (int i = 0; i < (int)arr.size(); i++)
        ps[i + 1] = ps[i] + arr[i];
    return ps;
}

// ─── Write stats.txt ─────────────────────────────────────────────────────
void write_stats(const Result& rf, const Result& rg, const Result& rp,
                 int n_lanes, int arrival_rate, int sim_time) {
    ofstream f("stats.txt");
    int total = max({rf.total_proc, rg.total_proc, rp.total_proc});

    f << "Total Vehicles: " << total << "\n\n";
    f << "Average Waiting Time:\n";
    f << "  Fixed:    " << fixed << setprecision(2) << rf.avg_wait << " s\n";
    f << "  Greedy:   " << rg.avg_wait << " s\n";
    f << "  Priority: " << rp.avg_wait << " s\n\n";
    f << "Max Waiting Time:\n";
    f << "  Fixed:    " << rf.max_wait << " s\n";
    f << "  Greedy:   " << rg.max_wait << " s\n";
    f << "  Priority: " << rp.max_wait << " s\n\n";
    f << "Time Complexity (Theoretical):\n";
    f << "  Queue Operations: O(1)\n";
    f << "  Greedy Selection: O(N)\n";
    f << "  Priority Queue:   O(log N)\n";
    f << "  Prefix Sum:       O(N)\n\n";
    f << "Overall Complexity:\n";
    f << "  Fixed:    O(N)\n";
    f << "  Greedy:   O(N^2)\n";
    f << "  Priority: O(N log N)\n\n";
    f << "Execution Time (Measured):\n";
    f << "  Fixed:    " << fixed << setprecision(3) << rf.exec_ms << " ms\n";
    f << "  Greedy:   " << rg.exec_ms << " ms\n";
    f << "  Priority: " << rp.exec_ms << " ms\n";

    // Determine best
    string best = "Fixed";
    double bv = rf.avg_wait;
    if (rg.avg_wait < bv) { bv = rg.avg_wait; best = "Greedy"; }
    if (rp.avg_wait < bv) { best = "Priority"; }
    f << "\nBest Algorithm: " << best << "\n";
    f.close();
}

// ─── Write simulation.json ────────────────────────────────────────────────
void write_json(const Result& rf, const Result& rg, const Result& rp,
                int n_lanes, int sim_time) {
    ofstream f("simulation.json");
    f << "{\n";

    // time array
    f << "  \"time\": [";
    for (int t = 0; t < sim_time; t++) f << t << (t < sim_time-1 ? "," : "");
    f << "],\n";

    // lane queues (fixed)
    for (int l = 0; l < n_lanes; l++) {
        f << "  \"fixed_lane_" << (l+1) << "\": [";
        for (int t = 0; t < sim_time; t++)
            f << rf.queue_lengths[t][l] << (t < sim_time-1 ? "," : "");
        f << (l < n_lanes-1 ? "],\n" : "]\n");
    }

    // greedy lane queues
    f << ",\n";
    for (int l = 0; l < n_lanes; l++) {
        f << "  \"greedy_lane_" << (l+1) << "\": [";
        for (int t = 0; t < sim_time; t++)
            f << rg.queue_lengths[t][l] << (t < sim_time-1 ? "," : "");
        f << (l < n_lanes-1 ? "],\n" : "]\n");
    }

    // priority lane queues
    f << ",\n";
    for (int l = 0; l < n_lanes; l++) {
        f << "  \"priority_lane_" << (l+1) << "\": [";
        for (int t = 0; t < sim_time; t++)
            f << rp.queue_lengths[t][l] << (t < sim_time-1 ? "," : "");
        f << (l < n_lanes-1 ? "],\n" : "]\n");
    }

    // summary stats
    f << ",\n";
    f << "  \"avg_wait\": {\"fixed\": " << fixed << setprecision(2) << rf.avg_wait
      << ", \"greedy\": " << rg.avg_wait << ", \"priority\": " << rp.avg_wait << "},\n";
    f << "  \"max_wait\": {\"fixed\": " << rf.max_wait
      << ", \"greedy\": " << rg.max_wait << ", \"priority\": " << rp.max_wait << "},\n";
    f << "  \"exec_ms\": {\"fixed\": " << rf.exec_ms
      << ", \"greedy\": " << rg.exec_ms << ", \"priority\": " << rp.exec_ms << "},\n";
    f << "  \"n_lanes\": " << n_lanes << ",\n";
    f << "  \"sim_time\": " << sim_time << "\n";
    f << "}\n";
    f.close();
}

// ─── Main ─────────────────────────────────────────────────────────────────
int main(int argc, char* argv[]) {
    int n_lanes      = 4;
    int arrival_rate = 3;
    int sim_time     = 60;
    int green_dur    = 10;

    if (argc >= 4) {
        n_lanes      = atoi(argv[1]);
        arrival_rate = atoi(argv[2]);
        sim_time     = atoi(argv[3]);
    }
    if (argc >= 5) green_dur = atoi(argv[4]);

    cerr << "Running simulation: lanes=" << n_lanes
         << " rate=" << arrival_rate << " time=" << sim_time << "\n";

    Result rf = fixed_time(n_lanes, arrival_rate, sim_time, green_dur);
    Result rg = greedy(n_lanes, arrival_rate, sim_time);
    Result rp = priority_sched(n_lanes, arrival_rate, sim_time);

    write_stats(rf, rg, rp, n_lanes, arrival_rate, sim_time);
    write_json(rf, rg, rp, n_lanes, sim_time);

    cerr << "Done. Files written: stats.txt, simulation.json\n";
    return 0;
}
