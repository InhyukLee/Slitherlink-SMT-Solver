import time
import networkx as nx
from pysmt.shortcuts import Solver, And, Not
from src.core_constraints import (
    create_edge_variables,
    get_node_degree_constraints,
    get_clue_constraints,
    get_anti_2x2_constraints
)

def extract_active_edges(model, N, M, h, v):
    """
    Parses the SMT model assignment and extracts edges evaluated to True.
    """
    active_h = []
    active_v = []
    for i in range(N + 1):
        for j in range(M):
            if model.get_value(h[i][j]).is_true():
                active_h.append((i, j))
    for i in range(N):
        for j in range(M + 1):
            if model.get_value(v[i][j]).is_true():
                active_v.append((i, j))
    return active_h, active_v

def build_graph(active_h, active_v):
    """
    Constructs a NetworkX graph using grid coordinates as nodes.
    """
    G = nx.Graph()
    for i, j in active_h:
        G.add_edge((i, j), (i, j+1))
    for i, j in active_v:
        G.add_edge((i, j), (i+1, j))
    return G

def solve_iterative(matrix):
    """
    Solves Slitherlink using Iterative Sub-loop Elimination (Lazy Constraints).
    """
    N = len(matrix)
    M = len(matrix[0])
    
    h, v = create_edge_variables(N, M)
    
    # Base local rules
    base_constraints = (
        get_node_degree_constraints(N, M, h, v) +
        get_clue_constraints(matrix, N, M, h, v) +
        get_anti_2x2_constraints(N, M, h, v)
    )
    
    start_time = time.time()
    iterations = 0
    blocking_clauses = []
    
    with Solver(name='z3') as solver:
        solver.add_assertion(And(base_constraints))
        
        while True:
            iterations += 1
            
            # Apply cumulative dynamic blocking rules
            if blocking_clauses:
                solver.add_assertion(And(blocking_clauses))
                
            if not solver.solve():
                return {"status": "UNSAT", "time": time.time() - start_time, "iterations": iterations}
            
            model = solver.get_model()
            active_h, active_v = extract_active_edges(model, N, M, h, v)
            
            # If no lines are drawn, check if that satisfies an empty grid requirement
            if not active_h and not active_v:
                return {"status": "SAT", "time": time.time() - start_time, "iterations": iterations, "edges": (active_h, active_v)}
            
            # Run graph structure connectivity checks
            G = build_graph(active_h, active_v)
            components = list(nx.connected_components(G))
            
            if len(components) == 1:
                # Success: Exactly one large loop found
                return {"status": "SAT", "time": time.time() - start_time, "iterations": iterations, "edges": (active_h, active_v)}
            
            # Multi-loop failure: construct blocking clause out of the smallest subloop
            smallest_component = min(components, key=len)
            
            subloop_literals = []
            # Find horizontal edges matching the subloop component vertices
            for i in range(N + 1):
                for j in range(M):
                    if ((i, j) in smallest_component) and ((i, j+1) in smallest_component):
                        if (i, j) in active_h:
                            subloop_literals.append(h[i][j])
            # Find vertical edges matching the subloop component vertices
            for i in range(N):
                for j in range(M + 1):
                    if ((i, j) in smallest_component) and ((i+1, j) in smallest_component):
                        if (i, j) in active_v:
                            subloop_literals.append(v[i][j])
            
            # Add clause: It cannot be that ALL these edges are True simultaneously
            blocking_clauses.append(Not(And(subloop_literals)))