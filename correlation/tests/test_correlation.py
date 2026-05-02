"""
correlation/tests/test_correlation.py

Unit tests for correlation/graph_builder.py using a synthetic 5-node example.

Synthetic scenario
------------------
Five unique log templates (T1 .. T5) and one anomaly event are placed on a
timeline so that their co-occurrence relationships are fully determined:

    t=0   T1
    t=10  T2, anomaly_label="anomaly:if_counter"
    t=30  T3
    t=50  T4   (within 60 s window of T1 through T3)
    t=70  T5   (outside 60 s window of T1, within window of T2 .. T4)
    t=75  T1   (second occurrence)

Expected graph (default 60 s window)
-------------------------------------
Node ids (6 total)
    T1, T2, T3, T4, T5, anomaly:if_counter

Edges (co-occurrence pairs within a 60 s window)
    The sliding window algorithm pairs each new reference with all references
    currently inside [current_ts - 60, current_ts].

    Reference list (flat, timestamp-sorted):
        (0, T1), (10, T2), (10, anomaly), (30, T3), (50, T4), (70, T5), (75, T1)

    Sliding window (left pointer advances while ts < right_ts - 60):

    right=(10,T2):     window=[T1]             new pairs: T1-T2
    right=(10,anomaly):window=[T1,T2]           new pairs: T1-anomaly, T2-anomaly
    right=(30,T3):     window=[T1,T2,anomaly]   new pairs: T1-T3, T2-T3, anomaly-T3
    right=(50,T4):     window=[T1,T2,anomaly,T3]new pairs: T1-T4, T2-T4, anomaly-T4, T3-T4
    right=(70,T5):     T1@0 drops (70-0=70>60)
                       window=[T2,anomaly,T3,T4] new pairs: T2-T5, anomaly-T5, T3-T5, T4-T5
    right=(75,T1):     T2@10,anomaly@10 drop (75-10=65>60)
                       window=[T3,T4,T5]         new pairs: T3-T1, T4-T1, T5-T1

Canonical edge list (15 unique undirected edges):
    T1-T2, T1-anomaly, T2-anomaly,
    T1-T3, T2-T3, T3-anomaly,
    T1-T4, T2-T4, T4-anomaly, T3-T4,
    T2-T5, T5-anomaly, T3-T5, T4-T5,
    T1-T5

Total = 15 edges.

Co-occurrence counts
    Most pairs appear exactly once, EXCEPT T1-T3 which appears twice:
      - once at t=30 (T1@0 is still in: 30-0=30<=60)
      - once at t=75 (T1@75 paired with T3@30: 75-30=45<=60)
    Similarly T1-T4 appears twice: once at t=50 (50-0=50<=60), once at t=75
    (75-50=25<=60).

    The maximum raw co-occurrence count is 2 (both T1-T3 and T1-T4 appear
    once in the t=30/50 windows and once more in the t=75 window).
    All other edges have count=1, weight=0.5.  T1-T3 and T1-T4 get weight=1.0.
"""

import math
import sys
import os

# Allow running the test directly from the project root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest

from correlation.graph_builder import (
    CorrelationGraph,
    GraphEdge,
    GraphNode,
    LogEvent,
    build_graph,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ANOMALY_LABEL = "anomaly:if_counter"

SYNTHETIC_EVENTS = [
    LogEvent(timestamp=0,  template="T1"),
    LogEvent(timestamp=10, template="T2", is_anomaly=True, anomaly_label=ANOMALY_LABEL),
    LogEvent(timestamp=30, template="T3"),
    LogEvent(timestamp=50, template="T4"),
    LogEvent(timestamp=70, template="T5"),
    LogEvent(timestamp=75, template="T1"),  # second occurrence of T1
]

EXPECTED_NODE_IDS = {"T1", "T2", "T3", "T4", "T5", ANOMALY_LABEL}
EXPECTED_EDGE_COUNT = 15


@pytest.fixture
def graph() -> CorrelationGraph:
    return build_graph(SYNTHETIC_EVENTS, time_window_seconds=60)


# ---------------------------------------------------------------------------
# Node tests
# ---------------------------------------------------------------------------

class TestNodes:
    def test_node_count(self, graph: CorrelationGraph):
        """Graph must contain exactly 6 nodes: 5 templates + 1 anomaly."""
        assert len(graph.nodes) == 6

    def test_node_ids_present(self, graph: CorrelationGraph):
        """All expected node ids must appear in the graph."""
        assert set(graph.nodes.keys()) == EXPECTED_NODE_IDS

    def test_node_types_log_template(self, graph: CorrelationGraph):
        """T1 through T5 must have node_type='log_template'."""
        for tid in ("T1", "T2", "T3", "T4", "T5"):
            assert graph.nodes[tid].node_type == "log_template", (
                f"{tid} should have node_type='log_template'"
            )

    def test_anomaly_node_type(self, graph: CorrelationGraph):
        """The anomaly node must have node_type='anomaly'."""
        assert graph.nodes[ANOMALY_LABEL].node_type == "anomaly"

    def test_node_counts(self, graph: CorrelationGraph):
        """T1 appears twice; all others appear once."""
        assert graph.nodes["T1"].count == 2
        for tid in ("T2", "T3", "T4", "T5"):
            assert graph.nodes[tid].count == 1, f"{tid} count should be 1"
        # Anomaly node fires once (the single anomaly event).
        assert graph.nodes[ANOMALY_LABEL].count == 1

    def test_node_schema(self, graph: CorrelationGraph):
        """Every node must be a GraphNode with the required attributes."""
        for node in graph.nodes.values():
            assert isinstance(node, GraphNode)
            assert hasattr(node, "id")
            assert hasattr(node, "node_type")
            assert hasattr(node, "count")
            assert node.node_type in ("log_template", "anomaly")
            assert node.count > 0


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------

class TestEdges:
    def test_edge_count(self, graph: CorrelationGraph):
        """Graph must contain exactly 16 edges."""
        assert len(graph.edges) == EXPECTED_EDGE_COUNT

    def test_edge_schema(self, graph: CorrelationGraph):
        """Every edge must be a GraphEdge with correct attribute types."""
        for edge in graph.edges.values():
            assert isinstance(edge, GraphEdge)
            assert isinstance(edge.source, str)
            assert isinstance(edge.target, str)
            assert isinstance(edge.co_occurrences, int)
            assert edge.co_occurrences >= 1
            assert isinstance(edge.weight, float)
            assert 0.0 < edge.weight <= 1.0

    def test_max_weight_is_one(self, graph: CorrelationGraph):
        """The highest weight in the graph must be exactly 1.0."""
        max_w = max(e.weight for e in graph.edges.values())
        assert math.isclose(max_w, 1.0), f"Expected max weight 1.0, got {max_w}"

    def test_weights_in_range(self, graph: CorrelationGraph):
        """All weights must be in (0, 1]."""
        for edge in graph.edges.values():
            assert 0.0 < edge.weight <= 1.0, (
                f"Edge {edge.source}-{edge.target} weight {edge.weight} out of range"
            )

    def test_highest_weight_edges(self, graph: CorrelationGraph):
        """T1-T3 and T1-T4 both appear twice and must have weight=1.0."""
        def get_edge(a: str, b: str) -> GraphEdge:
            key = (a, b) if a <= b else (b, a)
            assert key in graph.edges, f"Edge {a}-{b} not found"
            return graph.edges[key]

        e_t1_t3 = get_edge("T1", "T3")
        e_t1_t4 = get_edge("T1", "T4")
        assert e_t1_t3.co_occurrences == 2
        assert e_t1_t4.co_occurrences == 2
        assert math.isclose(e_t1_t3.weight, 1.0)
        assert math.isclose(e_t1_t4.weight, 1.0)

    def test_single_occurrence_edges_weight(self, graph: CorrelationGraph):
        """Edges with co_occurrences=1 must have weight=0.5 (1/max=1/2)."""
        for edge in graph.edges.values():
            if edge.co_occurrences == 1:
                assert math.isclose(edge.weight, 0.5, rel_tol=1e-5), (
                    f"Edge {edge.source}-{edge.target}: expected 0.5, got {edge.weight}"
                )

    def test_anomaly_node_has_edges(self, graph: CorrelationGraph):
        """The anomaly node must be connected to at least one other node."""
        anomaly_edges = [
            e for e in graph.edges.values()
            if e.source == ANOMALY_LABEL or e.target == ANOMALY_LABEL
        ]
        assert len(anomaly_edges) > 0, "Anomaly node has no edges"

    def test_anomaly_connected_to_template_nodes(self, graph: CorrelationGraph):
        """The anomaly node must be directly connected to its co-occurring templates."""
        # T2 event is at t=10 and is flagged as anomaly; T1@t=0, T3@t=30,
        # T4@t=50 all co-occur within 60 s.  T5@t=70 also co-occurs (70-10=60).
        expected_neighbors = {"T1", "T2", "T3", "T4", "T5"}
        actual_neighbors = set()
        for (src, tgt), edge in graph.edges.items():
            if src == ANOMALY_LABEL:
                actual_neighbors.add(tgt)
            elif tgt == ANOMALY_LABEL:
                actual_neighbors.add(src)
        assert expected_neighbors == actual_neighbors, (
            f"Anomaly neighbors mismatch: expected {expected_neighbors}, "
            f"got {actual_neighbors}"
        )

    def test_no_self_loops(self, graph: CorrelationGraph):
        """No edge may connect a node to itself."""
        for src, tgt in graph.edges.keys():
            assert src != tgt, f"Self-loop found on node {src}"

    def test_canonical_key_order(self, graph: CorrelationGraph):
        """All edge keys must satisfy source <= target (canonical ordering)."""
        for src, tgt in graph.edges.keys():
            assert src <= tgt, (
                f"Non-canonical edge key ({src}, {tgt}): expected source <= target"
            )


# ---------------------------------------------------------------------------
# Graph-level metadata tests
# ---------------------------------------------------------------------------

class TestGraphMetadata:
    def test_time_window_stored(self, graph: CorrelationGraph):
        """The graph must record the time window used during construction."""
        assert graph.time_window_seconds == 60

    def test_time_window_override(self):
        """A custom time_window_seconds must be respected and stored."""
        g = build_graph(SYNTHETIC_EVENTS, time_window_seconds=20)
        assert g.time_window_seconds == 20

    def test_narrow_window_fewer_edges(self):
        """A very narrow window should produce fewer edges than the default."""
        g_narrow = build_graph(SYNTHETIC_EVENTS, time_window_seconds=5)
        g_default = build_graph(SYNTHETIC_EVENTS, time_window_seconds=60)
        assert len(g_narrow.edges) < len(g_default.edges)

    def test_max_nodes_cap(self):
        """Setting max_nodes=3 must cap template nodes at 3."""
        g = build_graph(SYNTHETIC_EVENTS, time_window_seconds=60, max_nodes=3)
        template_nodes = [
            n for n in g.nodes.values() if n.node_type == "log_template"
        ]
        assert len(template_nodes) <= 3

    def test_anomaly_node_admitted_regardless_of_cap(self):
        """Anomaly nodes must always appear, even when max_nodes=1."""
        g = build_graph(SYNTHETIC_EVENTS, time_window_seconds=60, max_nodes=1)
        assert ANOMALY_LABEL in g.nodes

    def test_empty_input(self):
        """An empty event list should return an empty graph without errors."""
        g = build_graph([], time_window_seconds=60)
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_single_event_no_edges(self):
        """A single event can have a node but must not produce any edges."""
        g = build_graph([LogEvent(timestamp=0, template="T1")], time_window_seconds=60)
        assert "T1" in g.nodes
        assert len(g.edges) == 0
