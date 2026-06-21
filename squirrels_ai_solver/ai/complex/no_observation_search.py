# ai/complex/no_observation_search.py
import time
from collections import deque
from ai.search_result import SearchResult


def no_observation_solve(start_state, rules, max_belief_states=2000, max_seconds=5.0):
    """Solves the puzzle using Searching with No Observation (Conformant Planning)."""
    start_time = time.time()
    deadline = start_time + max_seconds

    steps = [(0, "Start No-Observation Search", start_state)]
    step_num = 1
    visited_count = 0
    generated_count = 1

    # Build initial belief state
    initial_states = [start_state]
    state_cache = {start_state.encode(): start_state}

    movable_pids = [pid for pid, p in start_state.pieces.items() if p.movable]
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]

    # Add alternative states
    for pid in movable_pids:
        for d in directions:
            # Try reverse direction to generate alternative state
            rev = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}[d]
            if rules.can_move(start_state, pid, rev):
                alt = rules.apply_action(start_state, (pid, rev))
                enc = alt.encode()
                if enc not in state_cache:
                    state_cache[enc] = alt
                    initial_states.append(alt)
            if len(initial_states) >= 4:  # Keep belief state small for BFS
                break
        if len(initial_states) >= 4:
            break

    initial_belief = frozenset(state_cache[s.encode()] for s in initial_states
                                for se in [s.encode()] if se in state_cache)
    initial_belief_enc = frozenset(s.encode() for s in initial_states)

    steps.append((step_num,
                    f"Initial belief state: {len(initial_states)} possible states",
                    start_state))
    step_num += 1

    def is_belief_goal(belief_enc):
        """Check if all states in belief are goal states."""
        return all(state_cache[se].is_goal() for se in belief_enc)

    if is_belief_goal(initial_belief_enc):
        return SearchResult(
            algorithm="No Observation",
            solved=True,
            path=[],
            visited_count=1,
            generated_count=1,
            elapsed_time=time.time() - start_time,
            steps=steps
        )

    # BFS on belief state space
    queue = deque([(initial_belief_enc, [])])
    explored_beliefs = {initial_belief_enc}

    # Domain: all possible actions
    actions_domain = [(pid, d) for pid in movable_pids for d in directions]

    solution_path = []
    solved = False

    while queue and len(explored_beliefs) < max_belief_states:
        if time.time() >= deadline:
            break

        curr_belief_enc, path = queue.popleft()
        visited_count += 1

        rep_state = state_cache.get(next(iter(curr_belief_enc)), start_state)
        steps.append((step_num,
                        f"Exploring Belief State (Size={len(curr_belief_enc)}) | Step={len(path)}",
                        rep_state))
        step_num += 1

        if is_belief_goal(curr_belief_enc):
            solution_path = path
            solved = True
            break

        for act in actions_domain:
            pid, direction = act

            # Action is valid only if valid for ALL states in belief
            next_belief_enc_list = []
            valid_for_all = True

            for se in curr_belief_enc:
                s = state_cache[se]
                if rules.can_move(s, pid, direction):
                    ns = rules.apply_action(s, act)
                    nse = ns.encode()
                    if nse not in state_cache:
                        state_cache[nse] = ns
                    next_belief_enc_list.append(nse)
                else:
                    # Action is invalid for at least 1 state -> skip
                    valid_for_all = False
                    break

            if not valid_for_all:
                continue

            next_belief_enc = frozenset(next_belief_enc_list)
            generated_count += 1

            if next_belief_enc not in explored_beliefs:
                explored_beliefs.add(next_belief_enc)
                queue.append((next_belief_enc, path + [act]))

    # Log steps for visualization
    if solved:
        curr_state = start_state
        for idx, act in enumerate(solution_path):
            curr_state = rules.apply_action(curr_state, act)
            steps.append((step_num, f"Step {idx+1}: {act[0]} {act[1]}", curr_state))
            step_num += 1

    return SearchResult(
        algorithm="No Observation",
        solved=solved,
        path=solution_path,
        visited_count=visited_count,
        generated_count=generated_count,
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "belief_states_searched": len(explored_beliefs),
            "initial_belief_size": len(initial_states),
            "note": "Conformant planning: action must be valid for ALL states in belief."
        }
    )
