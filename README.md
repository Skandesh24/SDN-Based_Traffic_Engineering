# SDN WAN Traffic Engineering with Live Metrics

A Python-based simulation demonstrating SDN WAN traffic engineering with live observability. A centralized controller computes paths, monitors link congestion, and reroutes traffic dynamically. Metrics are exported to Prometheus and can be visualized in Grafana.

---

## Features
- Centralized SDN-like controller that computes shortest paths (Dijkstra) with congestion-aware costs
- Dynamic traffic generation and congestion-triggered rerouting
- Live metrics exported to Prometheus for monitoring
- Visualize WAN behavior and reroutes in Grafana dashboards
- Simple configuration and local execution for experimentation and coursework

---

## Repository contents
- `sde_wan_live_metrics.py` — Main simulation, controller logic, and Prometheus exporter
- `prometheus.yml` — Example Prometheus scrape configuration
- `README.md` — This execution guide and project overview

---

## Prerequisites
- Python 3.8+ (3.x)
- Prometheus
- Grafana
- Python package: `prometheus-client`

Install the Python dependency:
```bash
pip install prometheus-client
```

---

## Quickstart — Run the simulation and view metrics

1. Start the SDN WAN simulation (this launches the controller, traffic generation, and Prometheus exporter):
```bash
python3 sde_wan_live_metrics.py
```
By default the Prometheus metrics endpoint will be available at:
```
http://localhost:8000/metrics
```

2. Start Prometheus (systemd example; adapt for your environment):
```bash
sudo systemctl start prometheus
```
Prometheus UI:
```
http://localhost:9090
```

3. Start Grafana:
```bash
sudo systemctl start grafana-server
```
Grafana UI:
```
http://localhost:3000
```
Default Grafana login:
- username: `admin`
- password: `admin`

Add Prometheus as a data source in Grafana (URL: `http://localhost:9090`) and build dashboards using the metrics listed below.

---

## Example Prometheus scrape config
Use (or adapt) the included `prometheus.yml` and ensure it scrapes the simulation on port 8000:
```yaml
scrape_configs:
  - job_name: 'sde_wan_sim'
    static_configs:
      - targets: ['localhost:8000']
```

---

## Available metrics
Exported metric names (examples):
- `wan_link_util_mbps` — Link bandwidth utilization (Mbps)
- `wan_link_util_ratio` — Link utilization to capacity ratio (0..1)
- `wan_link_active_flows` — Active flows on each link
- `wan_total_active_flows` — Total active flows in the WAN
- `wan_flow_reroutes_total` — Total number of congestion-triggered reroutes

Use these in Grafana to plot link utilization, flow counts, and to create alerts (e.g., when utilization > 0.75).

---

## Simulation behavior and algorithmic details
- Traffic flows are generated randomly between WAN nodes.
- Paths are computed using Dijkstra’s algorithm.
- Link cost = latency + congestion penalty (so congested links are less likely to be chosen).
- Rerouting is triggered when link utilization exceeds 75% (configurable inside the script).
- Metrics reflect live changes and reroutes, enabling real-time visualization.

---

## Configuration and tuning
- Edit the main script to change:
  - link capacities and latencies,
  - flow generation rate,
  - reroute threshold (default: 75% utilization),
  - Prometheus port (default: 8000).
- For larger topologies or different experiments, update the topology data structures or provide a loader for topology files.

---

## Development & contribution
- Clone the repo
- Run the simulation locally with Python
- Suggested improvements:
  - Add unit tests for path computation and rerouting logic
  - Add a CLI for configuration (topology, thresholds, ports)
  - Export additional metrics (per-flow RTT, per-path latency)
- Contributions are welcome — open an issue or submit a pull request.

---

## Troubleshooting
- Metrics not visible in Prometheus:
  - Confirm the simulation is running and listening on port 8000
  - Confirm `prometheus.yml` has the correct target and Prometheus has been reloaded
- Grafana shows no data:
  - Ensure Prometheus data source is correctly added and communicates with `http://localhost:9090`
  - Check time range and refresh interval in Grafana panels

---

## Use cases
- Coursework and demos for Software-Defined Networking (SDN), Cloud Networking, or Traffic Engineering classes
- Prototyping policies for congestion-aware routing and network observability
- Hands-on exercises with Prometheus + Grafana integration

---

## License & Author
Author: Skandesh S  
(Include a LICENSE file if you wish to specify open-source terms.)

---

If you want, I can:
- shorten this to a one-page quickstart,
- add example Grafana queries/panel JSON,
- or prepare a small topology diagram and sample config file. Tell me which of those you'd like next.
