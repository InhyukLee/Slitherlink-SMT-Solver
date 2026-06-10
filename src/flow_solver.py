import time
from pysmt.shortcuts import Symbol, Solver, And, Or, Equals, Plus, Ite, Implies, Int, GT, GE, Not
from pysmt.typing import INT, BOOL
from src.core_constraints import (
    create_edge_variables,
    get_node_degree_constraints,
    get_clue_constraints
)
from src.iterative_solver import extract_active_edges

def solve_flow(matrix):
    """
    Solves Slitherlink using an Eager Flow-Based Encoding natively in one shot.
    """
    N = len(matrix)
    M = len(matrix[0])

    h, v = create_edge_variables(N, M)

    constraints = (
        get_node_degree_constraints(N, M, h, v) +
        get_clue_constraints(matrix, N, M, h, v)
    )

    flow_h_out = [[Symbol(f"fx_out_{i}_{j}", INT) for j in range(M)] for i in range(N + 1)]
    flow_h_in  = [[Symbol(f"fx_in_{i}_{j}", INT) for j in range(M)] for i in range(N + 1)]
    flow_v_out = [[Symbol(f"fy_out_{i}_{j}", INT) for j in range(M + 1)] for i in range(N)]
    flow_v_in  = [[Symbol(f"fy_in_{i}_{j}", INT) for j in range(M + 1)] for i in range(N)]

    for i in range(N + 1):
        for j in range(M):
            constraints.append(Implies(
                Not(h[i][j]),
                And(Equals(flow_h_out[i][j], Int(0)),
                    Equals(flow_h_in[i][j], Int(0)))
            ))
            constraints.append(And(
                GE(flow_h_out[i][j], Int(0)),
                GE(flow_h_in[i][j], Int(0))
            ))

    for i in range(N):
        for j in range(M + 1):
            constraints.append(Implies(
                Not(v[i][j]),
                And(Equals(flow_v_out[i][j], Int(0)),
                    Equals(flow_v_in[i][j], Int(0)))
            ))
            constraints.append(And(
                GE(flow_v_out[i][j], Int(0)),
                GE(flow_v_in[i][j], Int(0))
            ))

    source_flags = [[Symbol(f"source_{i}_{j}", BOOL) for j in range(M + 1)] for i in range(N + 1)]

    all_source_vars = []
    for i in range(N + 1):
        for j in range(M + 1):
            all_source_vars.append(source_flags[i][j])

    constraints.append(
        Equals(Plus([Ite(s, Int(1), Int(0)) for s in all_source_vars]), Int(1))
    )

    # First compute all visited nodes
    all_node_visits = []
    node_visited_flags = {}

    for i in range(N + 1):
        for j in range(M + 1):
            connected_edges = []

            if j > 0:
                connected_edges.append(h[i][j - 1])
            if j < M:
                connected_edges.append(h[i][j])
            if i > 0:
                connected_edges.append(v[i - 1][j])
            if i < N:
                connected_edges.append(v[i][j])

            node_visited = Or(connected_edges)
            node_visited_flags[(i, j)] = node_visited
            all_node_visits.append(Ite(node_visited, Int(1), Int(0)))

    total_visited_count = Plus(all_node_visits)

    # Flow conservation
    for i in range(N + 1):
        for j in range(M + 1):
            incoming = []
            outgoing = []

            if j > 0:
                incoming.append(flow_h_out[i][j - 1])
                outgoing.append(flow_h_in[i][j - 1])
            if j < M:
                incoming.append(flow_h_in[i][j])
                outgoing.append(flow_h_out[i][j])
            if i > 0:
                incoming.append(flow_v_out[i - 1][j])
                outgoing.append(flow_v_in[i - 1][j])
            if i < N:
                incoming.append(flow_v_in[i][j])
                outgoing.append(flow_v_out[i][j])

            sum_in = Plus(incoming) if incoming else Int(0)
            sum_out = Plus(outgoing) if outgoing else Int(0)

            node_visited = node_visited_flags[(i, j)]

            constraints.append(Implies(source_flags[i][j], node_visited))

            constraints.append(Ite(
                source_flags[i][j],
                Equals(sum_out, Plus(sum_in, total_visited_count, Int(-1))),
                Ite(
                    node_visited,
                    Equals(sum_in, Plus(sum_out, Int(1))),
                    And(Equals(sum_in, Int(0)), Equals(sum_out, Int(0)))
                )
            ))

    start_time = time.time()

    with Solver(name="z3") as solver:
        solver.add_assertion(And(constraints))

        if solver.solve():
            model = solver.get_model()
            active_h, active_v = extract_active_edges(model, N, M, h, v)
            return {
                "status": "SAT",
                "time": time.time() - start_time,
                "iterations": 1,
                "edges": (active_h, active_v)
            }

        return {
            "status": "UNSAT",
            "time": time.time() - start_time,
            "iterations": 1
        }