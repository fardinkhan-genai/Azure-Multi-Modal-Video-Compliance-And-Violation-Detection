from langgraph.graph import END, StateGraph

from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import index_video_node, audit_content_node


def create_graph():
    """Build the same two-step workflow: Index video -> Audit content."""
    workflow = StateGraph(VideoAuditState)

    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    workflow.set_entry_point("indexer")
    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor", END)

    return workflow.compile()


app = create_graph()
