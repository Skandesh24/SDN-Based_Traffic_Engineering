"""
SDN WAN Traffic Engineering simulation with:
 - Live metrics for Prometheus
 - Congestion-aware rerouting
 - Flow generation and teardown
"""

import threading
import heapq
import random
import time
from prometheus_client import Gauge, Counter, start_http_server
from collections import defaultdict, namedtuple

RANDOM_SEED = 42
SIM_DURATION = 600
MONITOR_INTERVAL = 1.0
FLOW_GEN_INTERVAL = 0.6
FLOW_MIN_BW = 1.0
FLOW_MAX_BW = 10.0
FLOW_MIN_DUR = 6.0
FLOW_MAX_DUR = 20.0

TOPOLOGY_EDGES = [
    ("A", "B", 50, 20),
    ("A", "C", 30, 40),
    ("B", "C", 40, 10),
    ("B", "D", 20, 50),
    ("C", "E", 30, 30),
    ("D", "E", 60, 20),
    ("D", "F", 40, 25),
    ("E", "F", 50, 15),
]

HOSTS = ["A", "B", "C", "D", "E", "F"]

Link = namedtuple("Link", ["u", "v", "capacity", "latency"])
Flow = namedtuple("Flow", ["id", "src", "dst", "bw", "start_time", "end_time"])

random.seed(RANDOM_SEED)

wan_util_mbps = Gauge("wan_link_util_mbps", "Link utilization in Mbps", ["u", "v"])
wan_util_ratio = Gauge("wan_link_util_ratio", "Link utilization ratio", ["u", "v"])
wan_flow_count = Gauge("wan_link_active_flows", "Active flows on a link", ["u", "v"])
wan_active_flows = Gauge("wan_total_active_flows", "Total live flows in WAN")
wan_reroutes = Counter("wan_flow_reroutes_total", "Total congestion reroutes")

class Network:
    def __init__(self, edges):
        self.adj = defaultdict(list)
        self.links = {}
        for u, v, cap, lat in edges:
            link = Link(u, v, cap, lat)
            self.adj[u].append((v, link))
            self.adj[v].append((u, link))
            self.links[self._k(u, v)] = {"link": link, "util": 0.0, "flows": set()}

    def _k(self, a, b):
        return tuple(sorted((a, b)))

    def add(self, fid, path, bw):
        for i in range(len(path) - 1):
            k = self._k(path[i], path[i + 1])
            self.links[k]["util"] += bw
            self.links[k]["flows"].add(fid)

    def remove(self, fid, path, bw):
        for i in range(len(path) - 1):
            k = self._k(path[i], path[i + 1])
            self.links[k]["util"] = max(0.0, self.links[k]["util"] - bw)
            self.links[k]["flows"].discard(fid)

class Controller:
    def __init__(self, net):
        self.net = net
        self.paths = {}
        self.info = {}

    def path(self, src, dst):
        alpha = 300.0
        dist = {src: 0.0}
        prev = {}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == dst:
                break
            for v, link in self.net.adj[u]:
                k = self.net._k(u, v)
                util = self.net.links[k]["util"]
                cap = self.net.links[k]["link"].capacity
                nd = d + link.latency + alpha * (util / cap)
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        if dst not in dist:
            return None
        out = []
        cur = dst
        while cur != src:
            out.append(cur)
            cur = prev[cur]
        out.append(src)
        return out[::-1]

    def install(self, flow):
        p = self.path(flow.src, flow.dst)
        if not p:
            return False
        self.net.add(flow.id, p, flow.bw)
        self.paths[flow.id] = p
        self.info[flow.id] = flow
        return True

    def remove(self, fid):
        if fid not in self.paths:
            return
        f = self.info[fid]
        self.net.remove(fid, self.paths[fid], f.bw)
        del self.paths[fid]
        del self.info[fid]

    def optimize(self):
        items = sorted(
            [(info["util"] / info["link"].capacity, k, info)
             for k, info in self.net.links.items()],
            reverse=True
        )
        if not items:
            return
        ratio, key, info = items[0]
        if ratio < 0.75:
            return
        heavy = sorted(list(info["flows"]),
                       key=lambda f: self.info[f].bw,
                       reverse=True)
        for fid in heavy:
            flow = self.info[fid]
            old = self.paths[fid]
            self.net.remove(fid, old, flow.bw)
            new = self.path(flow.src, flow.dst)
            if new and new != old:
                wan_reroutes.inc()
                self.net.add(fid, new, flow.bw)
                self.paths[fid] = new
            else:
                self.net.add(fid, old, flow.bw)
            if (self.net.links[key]["util"] /
                self.net.links[key]["link"].capacity) < 0.75:
                break

class Traffic(threading.Thread):
    def __init__(self, c, stop):
        super().__init__(daemon=True)
        self.c = c
        self.stop = stop
        self.seq = 1

    def run(self):
        while not self.stop.is_set():
            time.sleep(random.expovariate(1.0 / FLOW_GEN_INTERVAL))
            src, dst = random.sample(HOSTS, 2)
            bw = random.uniform(FLOW_MIN_BW, FLOW_MAX_BW)
            dur = random.uniform(FLOW_MIN_DUR, FLOW_MAX_DUR)
            fid = f"f{self.seq}"
            self.seq += 1
            f = Flow(fid, src, dst, bw, time.time(), time.time() + dur)
            if self.c.install(f):
                threading.Timer(dur, self.c.remove, args=(fid,)).start()

def metrics(net):
    wan_active_flows.set(len(c.paths))
    for k, info in net.links.items():
        u, v = k
        util = info["util"]
        cap = info["link"].capacity
        wan_util_mbps.labels(u=u, v=v).set(util)
        wan_util_ratio.labels(u=u, v=v).set(util / cap)
        wan_flow_count.labels(u=u, v=v).set(len(info["flows"]))

if __name__ == "__main__":
    net = Network(TOPOLOGY_EDGES)
    c = Controller(net)

    start_http_server(8000)
    stop = threading.Event()
    Traffic(c, stop).start()

    start = time.time()
    while time.time() - start < SIM_DURATION:
        c.optimize()
        metrics(net)
        time.sleep(MONITOR_INTERVAL)
