import os
from src.data_loader import load_puzzles
from src.iterative_solver import solve_iterative
from src.flow_solver import solve_flow

def run_batch_evaluation():
    # 1. Load absolutely all available benchmark instances from your dataset directory
    # By omitting filters, it defaults to returning your entire 240-file suite
    puzzles_dataset = load_puzzles()
    
    total_puzzles = len(puzzles_dataset)
    if total_puzzles == 0:
        print("Error: No puzzle instances found in the data folder. Check your paths.")
        return

    print(f"============================================================")
    print(f" Starting Batch Evaluation on {total_puzzles} Slitherlink Puzzles")
    print(f"============================================================")
    print(f"{'Filename':<35} | {'Ver A (Iterative)':<25} | {'Ver B (Flow)':<20}")
    print("-" * 90)

    # Core performance tracking accumulators
    iterative_total_time = 0.0
    flow_total_time = 0.0
    iterative_total_invocations = 0
    flow_total_invocations = 0
    
    # Sort files alphabetically so your output looks clean and structured
    for filename in sorted(puzzles_dataset.keys()):
        matrix = puzzles_dataset[filename]
        
        # --- Version A: Run Lazy/Iterative Sub-loop Elimination ---
        res_a = solve_iterative(matrix)
        status_a = res_a['status']
        time_a = res_a['time']
        invocations_a = res_a['iterations']
        
        # --- Version B: Run Eager/Flow-Based One-Shot Encoding ---
        res_b = solve_flow(matrix)
        status_b = res_b['status']
        time_b = res_b['time']
        invocations_b = res_b['iterations'] # Always 1 for flow-based single shot

        # Update metrics tracking
        iterative_total_time += time_a
        flow_total_time += time_b
        iterative_total_invocations += invocations_a
        flow_total_invocations += invocations_b

        # Print detailed per-puzzle performance rows
        summary_a = f"{status_a} ({invocations_a} inv, {time_a:.3f}s)"
        summary_b = f"{status_b} ({time_b:.3f}s)"
        print(f"{filename:<35} | {summary_a:<25} | {summary_b:<20}")

    # --- Final Statistical Analytics Discussion Output ---
    print("=" * 90)
    print(" EVALUATION MATRIX PERFORMANCE SUMMARY")
    print("=" * 90)
    print(f"Total Instances Processed     : {total_puzzles}")
    print(f"Iterative Variant Total Time   : {iterative_total_time:.4f} seconds")
    print(f"Flow-Based Variant Total Time  : {flow_total_time:.4f} seconds")
    print(f"Iterative Solver Invocations   : {iterative_total_invocations} total calls")
    print(f"Flow Solver Invocations        : {flow_total_invocations} total calls (Fixed 1 per puzzle)")
    
    # Calculate percentage cost overhead metric for report documentation
    if iterative_total_time > 0:
        cost_diff_percentage = ((flow_total_time - iterative_total_time) / iterative_total_time) * 100
        print("-" * 90)
        if cost_diff_percentage > 0:
            print(f"👉 Native flow-based one-shot handling was {cost_diff_percentage:.2f}% MORE EXPENSIVE than iterative elimination.")
        else:
            print(f"👉 Native flow-based one-shot handling was {abs(cost_diff_percentage):.2f}% FASTER than iterative elimination.")
    print("=" * 90)

if __name__ == "__main__":
    run_batch_evaluation()