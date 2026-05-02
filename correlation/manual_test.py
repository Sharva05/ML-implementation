"""
correlation/manual_test.py

Run this from the project root to inspect the correlation graph interactively:

    python -m correlation.manual_test

It uses the same 5-node synthetic scenario as the unit tests so you can
cross-check the output against the expected values in test_correlation.py.
"""

from correlation.graph_builder import LogEvent, build_graph

# ---------------------------------------------------------------------------
# Same synthetic events as the unit tests
# ---------------------------------------------------------------------------

events = [
    LogEvent(timestamp=0,  template="T1"),
    LogEvent(timestamp=10, template="T2", is_anomaly=True, anomaly_label="anomaly:if_counter"),
    LogEvent(timestamp=30, template="T3"),
    LogEvent(timestamp=50, template="T4"),
    LogEvent(timestamp=70, template="T5"),
    LogEvent(timestamp=75, template="T1"),   # second occurrence
]

graph = build_graph(events, time_window_seconds=60)

# ---------------------------------------------------------------------------
# Print nodes
# ---------------------------------------------------------------------------

print("=" * 60)
print(f"NODES  ({len(graph.nodes)} total)")
print("=" * 60)
print(f"  {'ID':<30} {'TYPE':<14} COUNT")
print(f"  {'-'*30} {'-'*14} -----")
for node in sorted(graph.nodes.values(), key=lambda n: n.id):
    print(f"  {node.id:<30} {node.node_type:<14} {node.count}")

# ---------------------------------------------------------------------------
# Print edges sorted by weight descending
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print(f"EDGES  ({len(graph.edges)} total,  window={graph.time_window_seconds}s)")
print("=" * 60)
print(f"  {'SOURCE':<25} {'TARGET':<25} {'CO-OCC':>6}  {'WEIGHT':>7}")
print(f"  {'-'*25} {'-'*25} {'-'*6}  {'-'*7}")
for edge in sorted(graph.edges.values(), key=lambda e: (-e.weight, e.source, e.target)):
    print(f"  {edge.source:<25} {edge.target:<25} {edge.co_occurrences:>6}  {edge.weight:>7.4f}")

# ---------------------------------------------------------------------------
# Connectivity summary
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("CONNECTIVITY SUMMARY")
print("=" * 60)
from collections import defaultdict
neighbors: dict = defaultdict(set)
for src, tgt in graph.edges:
    neighbors[src].add(tgt)
    neighbors[tgt].add(src)

for nid in sorted(neighbors):
    conns = sorted(neighbors[nid])
    print(f"  {nid}")
    for c in conns:
        key = (nid, c) if nid <= c else (c, nid)
        w = graph.edges[key].weight
        print(f"    -> {c:<28} weight={w:.4f}")

print()
print("Done.")
