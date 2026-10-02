import networkx as nx
from typing import Dict, List, Set, Any, Tuple
from sqlalchemy.orm import Session as DBSession
from app.models.models import Dependency, Venue, Session as EventSession, Task, Resource, VolunteerShift

class DependencyGraphEngine:
    def __init__(self, db: DBSession, event_id: str):
        self.db = db
        self.event_id = event_id
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Constructs a directed graph containing explicit dependencies and operational linkages."""
        self.graph.clear()

        # 1. Fetch explicit dependencies
        deps = self.db.query(Dependency).filter(Dependency.event_id == self.event_id).all()
        for dep in deps:
            self.graph.add_node(
                dep.source_id,
                type=dep.source_type,
                id=dep.source_id,
                label=f"{dep.source_type}:{dep.source_id}"
            )
            self.graph.add_node(
                dep.target_id,
                type=dep.target_type,
                id=dep.target_id,
                label=f"{dep.target_type}:{dep.target_id}"
            )
            self.graph.add_edge(
                dep.source_id,
                dep.target_id,
                id=dep.id,
                criticality=dep.criticality,
                dependency_type=dep.dependency_type
            )

        # 2. Enrich nodes with actual human-readable labels from database
        venues = self.db.query(Venue).filter(Venue.event_id == self.event_id).all()
        for v in venues:
            if v.id in self.graph:
                self.graph.nodes[v.id]["label"] = v.name
                self.graph.nodes[v.id]["type"] = "VENUE"
                self.graph.nodes[v.id]["data"] = {
                    "capacity": v.capacity,
                    "location": v.location,
                    "available": v.availability
                }
            else:
                self.graph.add_node(
                    v.id,
                    type="VENUE",
                    id=v.id,
                    label=v.name,
                    data={"capacity": v.capacity, "location": v.location, "available": v.availability}
                )

        sessions = self.db.query(EventSession).filter(EventSession.event_id == self.event_id).all()
        for s in sessions:
            if s.id in self.graph:
                self.graph.nodes[s.id]["label"] = s.title
                self.graph.nodes[s.id]["type"] = "SESSION"
                self.graph.nodes[s.id]["data"] = {
                    "speaker": s.speaker_name,
                    "status": s.status,
                    "attendees": s.expected_attendees
                }
            else:
                self.graph.add_node(
                    s.id,
                    type="SESSION",
                    id=s.id,
                    label=s.title,
                    data={"speaker": s.speaker_name, "status": s.status, "attendees": s.expected_attendees}
                )

            # Link Venue -> Session if assigned
            if s.venue_id and s.venue_id in self.graph:
                if not self.graph.has_edge(s.venue_id, s.id):
                    self.graph.add_edge(
                        s.venue_id,
                        s.id,
                        id=f"auto-{s.venue_id}-{s.id}",
                        criticality="CRITICAL",
                        dependency_type="HOSTS"
                    )

        tasks = self.db.query(Task).filter(Task.event_id == self.event_id).all()
        for t in tasks:
            if t.id in self.graph:
                self.graph.nodes[t.id]["label"] = t.title
                self.graph.nodes[t.id]["type"] = "TASK"
                self.graph.nodes[t.id]["data"] = {
                    "status": t.status,
                    "priority": t.priority,
                    "owner": t.owner_name
                }
            else:
                self.graph.add_node(
                    t.id,
                    type="TASK",
                    id=t.id,
                    label=t.title,
                    data={"status": t.status, "priority": t.priority, "owner": t.owner_name}
                )

        resources = self.db.query(Resource).filter(Resource.event_id == self.event_id).all()
        for r in resources:
            if r.id in self.graph:
                self.graph.nodes[r.id]["label"] = r.name
                self.graph.nodes[r.id]["type"] = "RESOURCE"
                self.graph.nodes[r.id]["data"] = {"category": r.category, "available": r.availability}
            else:
                self.graph.add_node(
                    r.id,
                    type="RESOURCE",
                    id=r.id,
                    label=r.name,
                    data={"category": r.category, "available": r.availability}
                )
            if r.assigned_venue_id and r.assigned_venue_id in self.graph:
                if not self.graph.has_edge(r.id, r.assigned_venue_id):
                    self.graph.add_edge(
                        r.id,
                        r.assigned_venue_id,
                        id=f"auto-res-{r.id}-{r.assigned_venue_id}",
                        criticality="HIGH",
                        dependency_type="DEPLOYED_AT"
                    )

    def get_downstream_impact(self, node_id: str) -> List[Dict[str, Any]]:
        """Traverses downstream to find all directly and transitively affected operational records."""
        if node_id not in self.graph:
            return []

        descendants = nx.descendants(self.graph, node_id)
        impacted = []
        for desc_id in descendants:
            node_data = self.graph.nodes.get(desc_id, {})
            # Calculate shortest path distance to determine ripple level
            try:
                distance = nx.shortest_path_length(self.graph, node_id, desc_id)
            except Exception:
                distance = 1

            impacted.append({
                "id": desc_id,
                "label": node_data.get("label", desc_id),
                "type": node_data.get("type", "UNKNOWN"),
                "ripple_level": distance,
                "data": node_data.get("data", {})
            })

        # Sort by ripple level
        impacted.sort(key=lambda x: x["ripple_level"])
        return impacted

    def get_upstream_dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        """Finds all prerequisite records that this node depends on."""
        if node_id not in self.graph:
            return []

        ancestors = nx.ancestors(self.graph, node_id)
        deps = []
        for anc_id in ancestors:
            node_data = self.graph.nodes.get(anc_id, {})
            deps.append({
                "id": anc_id,
                "label": node_data.get("label", anc_id),
                "type": node_data.get("type", "UNKNOWN"),
                "data": node_data.get("data", {})
            })
        return deps

    def detect_cycles(self) -> Tuple[bool, List[List[str]]]:
        """Detects circular dependency loops that could deadlock operations."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return len(cycles) > 0, cycles
        except Exception:
            return False, []

    def get_critical_paths(self) -> List[List[str]]:
        """Identifies longest continuous chains of critical dependencies."""
        if not nx.is_directed_acyclic_graph(self.graph):
            return []

        try:
            longest_path = nx.dag_longest_path(self.graph)
            return [longest_path] if longest_path else []
        except Exception:
            return []

    def export_graph_for_visualization(self) -> Dict[str, Any]:
        """Formats graph into React Flow compatible nodes & edges."""
        nodes_list = []
        edges_list = []

        has_cycles, cycles = self.detect_cycles()
        critical_paths = self.get_critical_paths()

        # Map nodes
        for node_id, attrs in self.graph.nodes(data=True):
            nodes_list.append({
                "id": node_id,
                "label": attrs.get("label", node_id),
                "type": attrs.get("type", "TASK"),
                "status": "NORMAL",
                "data": attrs.get("data", {})
            })

        # Map edges
        for u, v, data in self.graph.edges(data=True):
            edges_list.append({
                "id": data.get("id", f"{u}->{v}"),
                "source": u,
                "target": v,
                "label": data.get("dependency_type", "REQUIRES"),
                "criticality": data.get("criticality", "HIGH"),
                "dependency_type": data.get("dependency_type", "REQUIRES")
            })

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "has_cycles": has_cycles,
            "critical_paths": critical_paths,
            "total_nodes": len(nodes_list),
            "total_edges": len(edges_list)
        }
