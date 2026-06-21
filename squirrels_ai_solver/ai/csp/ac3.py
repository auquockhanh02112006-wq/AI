# ai/csp/ac3.py
import time
from collections import deque
from ai.search_result import SearchResult
from ai.limits import SearchLimit


def ac3_solve(start_state, rules, max_depth=15, max_nodes=20000, max_seconds=3.0):
    """Solves the puzzle using AC-3 (Arc Consistency Algorithm 3) + Backtracking."""
    start_time = time.time()
    steps = [(0, "Start AC-3 + Backtracking", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    limit = SearchLimit(max_nodes, max_seconds)

    if start_state.is_goal():
        return SearchResult(
            algorithm="AC-3",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    def ac3_filter(state, depth_remaining):
        if depth_remaining <= 0:
            return False  # No remaining depth -> cannot progress to goal

        legal = rules.legal_actions(state)
        if not legal:
            return False  # Dead-end: no actions -> prune

        for action in legal:
            ns = rules.apply_action(state, action)
            if ns.is_goal():
                return True  # Found goal successor -> consistent
            if rules.legal_actions(ns):
                return True  # Successor has next actions -> consistent

        return False  # All successors are dead-ends -> prune

    # Backtracking integrated with AC-3
    visited_states = {start_state.encode()}

    def backtrack(state, path):
        visited_count[0] += 1
        if limit.reached(generated_count[0]):
            return None

        if state.is_goal():
            return path

        if len(path) >= max_depth:
            return None

        legal_actions = rules.legal_actions(state)

        for action in legal_actions:
            next_state = rules.apply_action(state, action)
            next_encoded = next_state.encode()

            if next_encoded in visited_states:
                continue

            generated_count[0] += 1

            # --- AC-3 Constraint Propagation ---
            remaining_depth = max_depth - len(path) - 1
            if not next_state.is_goal() and not ac3_filter(next_state, remaining_depth):
                steps.append((step_num[0],
                                f"[AC-3 Prune] {action[0]} {action[1]} -> dead-end, pruning",
                                next_state))
                step_num[0] += 1
                continue

            steps.append((step_num[0],
                            f"Trying {action[0]} {action[1]} (step {len(path)+1}/{max_depth})",
                            next_state))
            step_num[0] += 1

            visited_states.add(next_encoded)
            sol = backtrack(next_state, path + [action])
            if sol is not None:
                return sol

            # Backtrack
            visited_states.remove(next_encoded)
            steps.append((step_num[0],
                            f"Backtracking {action[0]} {action[1]}",
                            state))
            step_num[0] += 1

        return None

    solution_path = backtrack(start_state, [])
    solved = solution_path is not None

    return SearchResult(
        algorithm="AC-3",
        solved=solved,
        path=solution_path or [],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "note": "AC-3 filters dead-end states before each backtracking step."
        }
    )
