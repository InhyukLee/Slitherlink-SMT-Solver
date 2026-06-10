from pysmt.shortcuts import Symbol, Or, Equals, Plus, Ite, And, Not, Int
from pysmt.typing import BOOL, INT

def create_edge_variables(N, M):
    """
    Creates the Boolean variables for horizontal and vertical edges.
    """
    # h[i][j]: horizontal edge above cell (i,j). Shape: (N+1) x M
    h = [[Symbol(f"h_{i}_{j}", BOOL) for j in range(M)] for i in range(N + 1)]
    # v[i][j]: vertical edge to the left of cell (i,j). Shape: N x (M+1)
    v = [[Symbol(f"v_{i}_{j}", BOOL) for j in range(M + 1)] for i in range(N)]
    return h, v

def get_node_degree_constraints(N, M, h, v):
    """
    Enforces that every node has an incident degree of either 0 or 2.
    Handles boundaries properly.
    """
    constraints = []
    for i in range(N + 1):
        for j in range(M + 1):
            connected_edges = []
            
            if j > 0:      # Left edge exists
                connected_edges.append(h[i][j-1])
            if j < M:      # Right edge exists
                connected_edges.append(h[i][j])
            if i > 0:      # Upper edge exists
                connected_edges.append(v[i-1][j])
            if i < N:      # Lower edge exists
                connected_edges.append(v[i][j])

            # Sum up the active edges meeting at this node intersection
            sum_edges = Plus([Ite(edge, Int(1), Int(0)) for edge in connected_edges])
            
            # Every node, including boundaries, must be passed through (2) or ignored (0)
            constraints.append(Or(Equals(sum_edges, Int(0)), Equals(sum_edges, Int(2))))
    return constraints

def get_clue_constraints(matrix, N, M, h, v):
    """
    Enforces that the number of active edges around a cell matches its clue.
    """
    constraints = []
    for i in range(N):
        for j in range(M):
            clue = matrix[i][j]
            if clue != -1:  # -1 means no clue/empty cell
                surrounding_edges = [
                    h[i][j],     # Top
                    h[i+1][j],   # Bottom
                    v[i][j],     # Left
                    v[i][j+1]    # Right
                ]
                sum_edges = Plus([Ite(edge, Int(1), Int(0)) for edge in surrounding_edges])
                constraints.append(Equals(sum_edges, Int(clue)))
    return constraints

def get_anti_2x2_constraints(N, M, h, v):
    """
    Corrected: Prevents a true 2x2 grid block of four adjacent 1x1 cells 
    from forming an isolated internal sub-loop box.
    """
    constraints = []
    # Loop bounds stop 1 short of the edge to safely look ahead and form a 2x2 block
    for i in range(N - 1):
        for j in range(M - 1):
            # A true 2x2 cell block is bounded by these outer perimeter segments:
            constraints.append(Not(And([
                h[i][j], h[i][j+1],         # Top border of the 2x2 area
                h[i+2][j], h[i+2][j+1],     # Bottom border of the 2x2 area
                v[i][j], v[i+1][j],         # Left border of the 2x2 area
                v[i][j+2], v[i+1][j+2]      # Right border of the 2x2 area
            ])))
    return constraints