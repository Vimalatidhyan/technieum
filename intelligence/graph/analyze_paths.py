"""Attack path analysis on the asset graph."""
from typing import Dict, List

try:
    import networkx as nx
    _NX_AVAILABLE = True
except ImportError:
    _NX_AVAILABLE = False


def analyze_critical_paths(graph: "nx.DiGraph", entry_points: List[str] = None) -> Dict:  # type: ignore[name-defined]
    """Find critical attack paths and single points of failure."""
    if not _NX_AVAILABLE:
        return {"error": "networkx not available"}

    results: Dict = {"critical_paths": [], "single_points_of_failure": [], "statistics": {}}
    results["statistics"] = {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "components": nx.number_weakly_connected_components(graph),
    }

    # Betweenness centrality for single points of failure
    try:
        centrality = nx.betweenness_centrality(graph, normalized=True)
        spof = [{"node": n, "centrality": round(c, 3)} for n, c in centrality.items() if c > 0.3]
        results["single_points_of_failure"] = sorted(spof, key=lambda x: -x["centrality"])[:10]
    except Exception:
        pass

    return results
