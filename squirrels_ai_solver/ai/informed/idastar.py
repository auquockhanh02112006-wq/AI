# ai/informed/idastar.py
import time
from ai.utils import SearchNode, reconstruct_path
from ai.informed.heuristics import squirrel_heuristic
from ai.search_result import SearchResult
from ai.limits import SearchLimit


def idastar_solve(start_state, rules, max_nodes=20000, max_seconds=3.0):
    """Solves the puzzle using Iterative Deepening A* (IDA*)."""
    start_time = time.time()

    h_start = squirrel_heuristic(start_state)
    threshold = h_start  # Initial f-threshold = h(start)

    if start_state.is_goal():
        return SearchResult(
            algorithm="IDA*",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=[(0, f"Start (h={h_start}) - Goal reached immediately", start_state)]
        )

    steps = [(0, f"Start (IDA* with threshold={threshold})", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [1]
    limit_guard = SearchLimit(max_nodes, max_seconds)

    FOUND = "FOUND"
    CUTOFF = "CUTOFF"

    def search(node, g, threshold, path_encoded):
        visited_count[0] += 1

        if limit_guard.reached(generated_count[0]):
            return None, float('inf')

        h = squirrel_heuristic(node.state)
        f = g + h

        # Prune if f exceeds threshold
        if f > threshold:
            return CUTOFF, f

        if node.state.is_goal():
            steps.append((
                step_num[0],
                f"[OK] Goal! f={f} (g={g}, h={h})",
                node.state
            ))
            step_num[0] += 1
            return FOUND, node

        f_min_exceeded = float('inf')  # Track minimum f exceeding threshold

        for action in rules.legal_actions(node.state):
            next_state = rules.apply_action(node.state, action)
            next_encoded = next_state.encode()

            # Avoid cycles on the current path
            if next_encoded in path_encoded:
                continue

            child = SearchNode(
                state=next_state,
                parent=node,
                action=action,
                path_cost=g + 1,
                depth=node.depth + 1
            )
            generated_count[0] += 1
            h_child = squirrel_heuristic(next_state)
            f_child = (g + 1) + h_child
            steps.append((
                step_num[0],
                f"[f={f_child}] Trying {action[0]} {action[1]} (g={g+1}, h={h_child})",
                next_state
            ))
            step_num[0] += 1

            path_encoded.add(next_encoded)
            status, result = search(child, g + 1, threshold, path_encoded)
            path_encoded.discard(next_encoded)

            if status == FOUND:
                return FOUND, result
            if status == CUTOFF:
                f_min_exceeded = min(f_min_exceeded, result)

        return CUTOFF if f_min_exceeded < float('inf') else None, f_min_exceeded

    # Outer loop - increase threshold
    start_node = SearchNode(start_state)
    start_encoded = start_state.encode()

    while True:
        if limit_guard.reached(generated_count[0]):
            break

        steps.append((
            step_num[0],
            f"IDA*: Start DFS with threshold={threshold}",
            start_state
        ))
        step_num[0] += 1

        path_set = {start_encoded}
        status, result = search(start_node, 0, threshold, path_set)

        if status == FOUND:
            goal_node = result
            actions, _ = reconstruct_path(goal_node)
            steps.append((
                step_num[0],
                f"[OK] Solution found! Threshold={threshold}, Steps={len(actions)}",
                goal_node.state
            ))
            return SearchResult(
                algorithm="IDA*",
                solved=True,
                path=actions,
                visited_count=visited_count[0],
                generated_count=generated_count[0],
                elapsed_time=time.time() - start_time,
                steps=steps
            )

        new_threshold = result
        if new_threshold == float('inf') or status is None:
            break

        threshold = new_threshold

    return SearchResult(
        algorithm="IDA*",
        solved=False,
        path=[],
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps
    )
