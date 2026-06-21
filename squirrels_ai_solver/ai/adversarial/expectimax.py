# ai/adversarial/expectimax.py
import time
from ai.search_result import SearchResult
from ai.informed.heuristics import squirrel_heuristic


def expectimax_solve(start_state, rules, max_depth=3):
    """Solves the puzzle using Expectimax Search (Adversarial Mode)."""
    start_time = time.time()
    steps = [(0, "Start Expectimax", start_state)]
    step_num = [1]
    visited_count = [0]
    generated_count = [0]

    def get_max_actions(state):
        actions = []
        for pid, p in state.pieces.items():
            if p.type == "squirrel" and p.movable:
                for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    if rules.can_move(state, pid, d):
                        actions.append((pid, d))
        return actions

    def get_chance_actions(state):
        result_actions = []
        if "flower" in state.pieces:
            cloned = state.clone()
            cloned.pieces["flower"].movable = True
            for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
                if rules.can_move(cloned, "flower", d):
                    result_actions.append(("flower", d))
        if not result_actions:
            result_actions.append(None)  # Pass turn nếu không có hành động
        return result_actions

    def apply_chance_action(state, action):
        if action is None:
            return state
        cloned = state.clone()
        cloned.pieces["flower"].movable = True
        next_st = rules.apply_action(cloned, action)
        if "flower" in next_st.pieces:
            next_st.pieces["flower"].movable = False
        return next_st

    def utility(state):
        if state.is_goal():
            return 1000
        return -squirrel_heuristic(state)

    def expectimax_decision(state, depth, is_max_turn):
        visited_count[0] += 1

        if depth == 0 or state.is_goal():
            return utility(state), None

        if is_max_turn:
            best_val = -float('inf')
            best_act = None
            actions = get_max_actions(state)
            if not actions:
                return utility(state), None

            for act in actions:
                generated_count[0] += 1
                next_state = rules.apply_action(state, act)
                val, _ = expectimax_decision(next_state, depth - 1, False)
                if val > best_val:
                    best_val = val
                    best_act = act

            return best_val, best_act

        else:
            actions = get_chance_actions(state)
            if not actions:
                return utility(state), None

            total_val = 0.0
            for act in actions:
                generated_count[0] += 1
                if act is None:
                    ns = state
                else:
                    ns = apply_chance_action(state, act)
                val, _ = expectimax_decision(ns, depth - 1, True)
                total_val += val

            expected_val = total_val / len(actions)
            return expected_val, None

    current_state = start_state
    sim_path = []

    for move_idx in range(10):
        if current_state.is_goal():
            break

        _, best_max_act = expectimax_decision(current_state, max_depth, True)
        if not best_max_act:
            break
        current_state = rules.apply_action(current_state, best_max_act)
        sim_path.append(best_max_act)
        steps.append((step_num[0],
                        f"MAX: Squirrel {best_max_act[0]} slides {best_max_act[1]}",
                        current_state))
        step_num[0] += 1

        if current_state.is_goal():
            break

        chance_actions = get_chance_actions(current_state)
        best_chance_act = chance_actions[0] if chance_actions else None
        if best_chance_act:
            next_state = apply_chance_action(current_state, best_chance_act)
            current_state = next_state
            sim_path.append(best_chance_act)
            steps.append((step_num[0],
                            f"CHANCE: Random flower {best_chance_act[0]} {best_chance_act[1]}",
                            current_state))
            step_num[0] += 1

    solved = current_state.is_goal()

    return SearchResult(
        algorithm="Expectimax",
        solved=solved,
        path=sim_path,
        visited_count=visited_count[0],
        generated_count=generated_count[0],
        elapsed_time=time.time() - start_time,
        steps=steps,
        extra={
            "note": "Expectimax: CHANCE node computes expected value instead of MIN."
        }
    )
