from langgraph.graph import StateGraph, END
from nodes.state import AgentState
from nodes.trend_node import trend_node
from nodes.vault_node import vault_node
from nodes.patch_node import patch_node
from nodes.synthesis_node import synthesis_node

def create_advisor_graph():
    """
    Builds and compiles the StateGraph wiring the multi-signal sell-timing advisor nodes.
    
    Architecture flow:
    - Input State
    - Parallel execution: trend_node, vault_node, patch_node
    - Fan-in join: synthesis_node
    - Output State
    """
    # Initialize the graph with State schema
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("trend_analysis", trend_node)
    workflow.add_node("vault_analysis", vault_node)
    workflow.add_node("patch_analysis", patch_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry points to start parallel execution
    workflow.set_entry_point("trend_analysis") # For simple sequential workflow representation, or define parallel branches
    
    # Since we are setting up skeletons, let's represent a simple sequential piping first,
    # or wire them to execute sequentially into synthesis:
    workflow.add_edge("trend_analysis", "vault_analysis")
    workflow.add_edge("vault_analysis", "patch_analysis")
    workflow.add_edge("patch_analysis", "synthesis")
    workflow.add_edge("synthesis", END)
    
    # Compile graph
    app = workflow.compile()
    return app
