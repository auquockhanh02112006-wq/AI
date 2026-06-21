# ai/local_search/local_beam.py
import time
import random
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult


def local_beam_solve(start_state, rules, k=5, max_iterations=200):
    """Solves the puzzle using Local Beam Search."""
    start_time = time.time()

    steps = [(0, f"Start (Local Beam Search: k={k}, max_iter={max_iterations})", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1

    if start_state.is_goal():
        return SearchResult(
            algorithm="Local Beam",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    # Initialize beam
    def make_node(state, parent=None, action=None, cost=0, depth=0):
        return SearchNode(state=state, parent=parent, action=action, path_cost=cost, depth=depth)

    # Create initial beam: take k best successors from start_state
    initial_successors = []
    for action in rules.legal_actions(start_state):
        ns = rules.apply_action(start_state, action)
        child = make_node(ns, parent=make_node(start_state), action=action, cost=1, depth=1)
        val = -squirrel_heuristic(ns)
        initial_successors.append((val, child))
        generated_count += 1

    initial_successors.sort(key=lambda x: x[0], reverse=True)

    if not initial_successors:
        # No valid actions from start state
        return SearchResult(
            algorithm="Local Beam",
            solved=False,
            path=[],
            visited_count=0,
            generated_count=generated_count,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    # Take up to k best beams
    beam = [child for _, child in initial_successors[:k]]

    steps.append((step_num, f"Initialized beam with {len(beam)} states", beam[0].state))
    step_num += 1

    # Main loop
    for iteration in range(1, max_iterations + 1):
        visited_count += len(beam)

        # --- Check goal in current beam ---
        for node in beam:
            if node.state.is_goal():
                actions, _ = reconstruct_path(node)
                steps.append((step_num, f"[OK] Goal found at iteration {iteration}!", node.state))
                return SearchResult(
                    algorithm="Local Beam",
                    solved=True,
                    path=actions,
                    visited_count=visited_count,
                    generated_count=generated_count,
                    elapsed_time=time.time() - start_time,
                    steps=steps
                )

        # --- Generate all successors for the entire beam ---
        all_successors = []  # List of (value, child_node)

        for beam_node in beam:
            for action in rules.legal_actions(beam_node.state):
                ns = rules.apply_action(beam_node.state, action)
                child = make_node(
                    ns,
                    parent=beam_node,
                    action=action,
                    cost=beam_node.path_cost + 1,
                    depth=beam_node.depth + 1
                )
                val = -squirrel_heuristic(ns)
                all_successors.append((val, child))
                generated_count += 1

                # Early goal check
                if ns.is_goal():
                    actions, _ = reconstruct_path(child)
                    steps.append((step_num, f"[OK] Goal found in successor! Iteration {iteration}", ns))
                    return SearchResult(
                        algorithm="Local Beam",
                        solved=True,
                        path=actions,
                        visited_count=visited_count,
                        generated_count=generated_count,
                        elapsed_time=time.time() - start_time,
                        steps=steps
                    )

        if not all_successors:
            steps.append((step_num, f"[X] No successors left at iteration {iteration}", beam[0].state))
            step_num += 1
            break

        # --- Select best k successors from all beams ---
        all_successors.sort(key=lambda x: x[0], reverse=True)
        best_k = all_successors[:k]

        best_val = best_k[0][0]
        steps.append((step_num, f"Iteration {iteration}: Best value={best_val}, Beam size={len(best_k)}", best_k[0][1].state))
        step_num += 1

        # Update beam
        new_beam = [child for _, child in best_k]

        # Detect unchanged beam (stuck in local maxima)
        old_encoded = {node.state.encode() for node in beam}
        new_encoded = {node.state.encode() for node in new_beam}
        if old_encoded == new_encoded:
            steps.append((step_num, f"[X] Beam unchanged - stuck at local maxima (value={best_val})", new_beam[0].state))
            step_num += 1
            break

        beam = new_beam

    # Stopped without finding goal
    return SearchResult(
        algorithm="Local Beam",
        solved=False,
        path=[],
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps
    )
