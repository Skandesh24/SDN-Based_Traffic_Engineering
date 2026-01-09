SDN WAN TRAFFIC ENGINEERING WITH LIVE METRICS

This project implements an SDN-based WAN Traffic Engineering simulation in Python.
A centralized controller computes paths, monitors congestion, and reroutes traffic dynamically.
Live WAN metrics are exported to Prometheus and visualized using Grafana.

FILES INCLUDED
1. sde_wan_live_metrics.py  – Main SDN WAN simulation and Prometheus exporter
2. prometheus.yml           – Prometheus scrape configuration
3. README.md                – Execution guide

PREREQUISITES
- Python 3
- Prometheus
- Grafana
- Python package: prometheus-client

Install dependency:
pip install prometheus-client

EXECUTION STEPS
Follow the steps exactly in the order given below.

STEP 1: RUN THE SDN WAN SIMULATION
python3 sde_wan_live_metrics.py

This starts:
- The SDN controller
- WAN traffic flow generation
- Congestion-aware rerouting
- Prometheus metrics exporter on port 8000

Metrics endpoint:
http://localhost:8000/metrics

STEP 2: START PROMETHEUS
sudo systemctl start prometheus

Prometheus scrapes WAN metrics from the simulation.
Prometheus UI:
http://localhost:9090

STEP 3: START GRAFANA
sudo systemctl start grafana-server

Grafana UI:
http://localhost:3000

Default login:
username: admin
password: admin

Add Prometheus as a data source and visualize WAN metrics.

AVAILABLE METRICS
- wan_link_util_mbps          : Link bandwidth utilization (Mbps)
- wan_link_util_ratio         : Link utilization to capacity ratio
- wan_link_active_flows       : Active flows per link
- wan_total_active_flows      : Total active flows in the WAN
- wan_flow_reroutes_total     : Number of congestion-based reroutes

STOPPING THE SERVICES
After completing the experiment, stop the services using the commands below.

sudo systemctl stop prometheus
sudo systemctl stop grafana-server

SIMULATION BEHAVIOR
- Traffic flows are generated randomly between WAN nodes
- Paths are computed using Dijkstra’s algorithm
- Link cost includes latency and congestion penalty
- Rerouting occurs when link utilization exceeds 75 percent
- Changes are visible live in Prometheus and Grafana

ACADEMIC USE

This project demonstrates SDN WAN traffic engineering, congestion-aware routing,
and network observability. It is suitable for coursework in Software Defined Networking,
Cloud Computing, and Computer Networks.

AUTHOR
Skandesh S
