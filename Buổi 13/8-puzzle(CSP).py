import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import heapq
import math
import itertools

# ═══════════════════════════════════════════════════════════════
#  ALGORITHM & HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def ACTIONS(state):
    """
    Xác định các hành động di chuyển hợp lệ của ô trống (số 0).
    Trả về danh sách các hướng đi: ['UP', 'DOWN', 'LEFT', 'RIGHT'] ngẫu nhiên.
    """
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    moves = []
    if row > 0: moves.append('UP')
    if row < 2: moves.append('DOWN')
    if col > 0: moves.append('LEFT')
    if col < 2: moves.append('RIGHT')
    random.shuffle(moves)
    return moves

def CHILD_NODE(problem_state, parent, action):
    """
    Sinh trạng thái con từ trạng thái cha dựa trên hành động di chuyển cụ thể.
    """
    state = list(problem_state)
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    targets = {
        'UP': (row - 1) * 3 + col,
        'DOWN': (row + 1) * 3 + col,
        'LEFT': row * 3 + (col - 1),
        'RIGHT': row * 3 + (col + 1)
    }
    swap = targets[action]
    state[idx], state[swap] = state[swap], state[idx]
    
    return {
        'STATE': tuple(state),
        'parent': parent,
        'action': action,
        'depth': parent['depth'] + 1 if parent else 0,
        'path_cost': parent['path_cost'] + 1 if parent else 0
    }

def SOLUTION(node):
    """
    Truy vết ngược từ Node đích về Node khởi đầu để trích xuất đường đi lời giải.
    """
    path = []
    while node is not None:
        path.append(node)
        node = node['parent']
    return list(reversed(path))

def MISPLACED_TILES(state, goal):
    """Hàm Heuristic h1(n): Đếm số lượng ô nằm sai vị trí."""
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])

def MANHATTAN_DISTANCE(state, goal):
    """Hàm Heuristic h2(n): Tổng khoảng cách Manhattan."""
    distance = 0
    for i in range(9):
        val = state[i]
        if val != 0:  
            goal_idx = goal.index(val)
            r1, col1 = i // 3, i % 3
            r2, col2 = goal_idx // 3, goal_idx % 3
            distance += abs(r1 - r2) + abs(col1 - col2)
    return distance

def SENSORLESS_APPLY_ACTION(state, action):
    """
    Hàm phụ trợ cho bài toán mù / không chắc chắn:
    Mô phỏng đập tường. Nếu hành động không hợp lệ (đụng biên), trạng thái đứng im.
    """
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    swap_idx = -1
    
    if action == 'UP' and row > 0: swap_idx = (row - 1) * 3 + col
    elif action == 'DOWN' and row < 2: swap_idx = (row + 1) * 3 + col
    elif action == 'LEFT' and col > 0: swap_idx = row * 3 + (col - 1)
    elif action == 'RIGHT' and col < 2: swap_idx = row * 3 + (col + 1)
    
    if swap_idx == -1: return state 
        
    new_state = list(state)
    new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
    return tuple(new_state)

def BELIEF_APPLY_ACTION(belief_state, action):
    """Áp dụng 1 hành động lên toàn bộ Belief State. Nếu hành động đập tường thì giữ nguyên state đó."""
    new_belief = set()
    for s in belief_state:
        new_belief.add(SENSORLESS_APPLY_ACTION(s, action))
    return tuple(sorted(list(new_belief)))

def GENERATE_PARTIAL_STATES(partial_tuple):
    """Sinh tất cả các trạng thái có thể từ một trạng thái nhìn thấy 1 phần (có chứa 'x')."""
    missing = set(range(9))
    known = {}
    for i, val in enumerate(partial_tuple):
        if val != 'x':
            known[i] = int(val)
            if int(val) in missing:
                missing.remove(int(val))
    
    possible_states = []
    for p in itertools.permutations(list(missing)):
        state = [0]*9
        p_idx = 0
        for i in range(9):
            if i in known:
                state[i] = known[i]
            else:
                state[i] = p[p_idx]
                p_idx += 1
        possible_states.append(tuple(state))
    return possible_states

def BREADTH_FIRST_SEARCH(initial_state, goal_state):
    explore_log = []
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}
    if node['STATE'] == goal_state: return SOLUTION(node), explore_log
    
    frontier = deque([node])
    frontier_set = {node['STATE']}
    explored = {}
    
    while frontier:
        node = frontier.popleft()
        frontier_set.discard(node['STATE'])
        explored[node['STATE']] = True
        
        for action in ACTIONS(node['STATE']):
            child = CHILD_NODE(node['STATE'], node, action)
            if child['STATE'] not in explored and child['STATE'] not in frontier_set:
                if child['STATE'] == goal_state:
                    explore_log.append({
                        'node': child,
                        'frontier_list': [(n['STATE'], n['path_cost']) for n in frontier] + [(child['STATE'], child['path_cost'])],
                        'explored_list': list(explored.keys())
                    })
                    return SOLUTION(child), explore_log
                frontier.append(child)
                frontier_set.add(child['STATE'])
                
        explore_log.append({
            'node': node,
            'frontier_list': [(n['STATE'], n['path_cost']) for n in frontier],
            'explored_list': list(explored.keys())
        })
    return None, explore_log

def DEPTH_FIRST_SEARCH(initial_state, goal_state, max_depth=1000):
    explore_log = []
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}
    frontier = [node]
    frontier_set = {node['STATE']}
    explored = {}
    
    while frontier:
        node = frontier.pop()
        frontier_set.discard(node['STATE'])
        if node['STATE'] in explored: continue
        explored[node['STATE']] = True
        
        if node['STATE'] == goal_state:
            explore_log.append({
                'node': node,
                'frontier_list': [(n['STATE'], n['path_cost']) for n in frontier],
                'explored_list': list(explored.keys())
            })
            return SOLUTION(node), explore_log
            
        if node['depth'] < max_depth:
            for action in ACTIONS(node['STATE']):
                child = CHILD_NODE(node['STATE'], node, action)
                if child['STATE'] not in explored and child['STATE'] not in frontier_set:
                    frontier.append(child)
                    frontier_set.add(child['STATE'])
                    
        explore_log.append({
            'node': node,
            'frontier_list': [(n['STATE'], n['path_cost']) for n in frontier],
            'explored_list': list(explored.keys())
        })
    return None, explore_log

def _RECURSIVE_DLS(node, goal_state, limit, explore_log, visited, current_frontier):
    if node['STATE'] == goal_state:
        explore_log.append({'node': node, 'frontier_list': list(current_frontier), 'explored_list': list(visited.keys())})
        return SOLUTION(node)
    if node['depth'] >= limit: return 'cutoff'
        
    visited[node['STATE']] = True
    cutoff_occurred = False
    children = []
    for action in ACTIONS(node['STATE']):
        child = CHILD_NODE(node['STATE'], node, action)
        if child['STATE'] not in visited: children.append(child)
            
    current_frontier.extend([(c['STATE'], c['path_cost']) for c in children])
    explore_log.append({'node': node, 'frontier_list': list(current_frontier), 'explored_list': list(visited.keys())})
    
    for child in children:
        current_frontier.remove((child['STATE'], child['path_cost']))
        result = _RECURSIVE_DLS(child, goal_state, limit, explore_log, visited, current_frontier)
        current_frontier.append((child['STATE'], child['path_cost']))
        if result == 'cutoff': cutoff_occurred = True
        elif result is not None: return result
        
    del visited[node['STATE']] 
    return 'cutoff' if cutoff_occurred else None

def ITERATIVE_DEEPENING_SEARCH(initial_state, goal_state, max_depth=1000):
    explore_log = []
    for depth in range(max_depth + 1):
        result = _RECURSIVE_DLS({'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}, 
                                goal_state, depth, explore_log, {}, [])
        if result != 'cutoff': return result, explore_log
    return None, explore_log

def UNIFORM_COST_SEARCH(initial_state, goal_state):
    explore_log = []
    start_cost = MISPLACED_TILES(initial_state, goal_state)
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': start_cost}
    frontier = []
    heapq.heappush(frontier, (start_node['path_cost'], random.random(), start_node))
    frontier_dict = {initial_state: start_node['path_cost']}
    explored = {}
    
    while frontier:     
        cost, _, node = heapq.heappop(frontier)
        if node['STATE'] in explored: continue
        explored[node['STATE']] = True
        if node['STATE'] in frontier_dict: del frontier_dict[node['STATE']]
            
        if node['STATE'] == goal_state:
            explore_log.append({'node': node, 'frontier_list': list(frontier_dict.items()), 'explored_list': list(explored.keys())})
            return SOLUTION(node), explore_log
            
        for action in ACTIONS(node['STATE']):
            child = CHILD_NODE(node['STATE'], node, action)
            child['path_cost'] = node['path_cost'] + MISPLACED_TILES(child['STATE'], goal_state)
            if child['STATE'] not in explored and child['STATE'] not in frontier_dict:
                heapq.heappush(frontier, (child['path_cost'], random.random(), child))
                frontier_dict[child['STATE']] = child['path_cost']
            elif child['STATE'] in frontier_dict and child['path_cost'] < frontier_dict[child['STATE']]:
                heapq.heappush(frontier, (child['path_cost'], random.random(), child))
                frontier_dict[child['STATE']] = child['path_cost']
                
        explore_log.append({'node': node, 'frontier_list': list(frontier_dict.items()), 'explored_list': list(explored.keys())})
    return None, explore_log

def GREEDY_SEARCH(initial_state, goal_state):
    explore_log = []
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(initial_state, goal_state)}
    start_node['path_cost'] = start_node['h']
    FRONTIER = [start_node]
    REACHED = {}
    
    while FRONTIER:
        min_idx = min(range(len(FRONTIER)), key=lambda i: FRONTIER[i]['h'])
        n = FRONTIER.pop(min_idx)
        
        if n['STATE'] == goal_state:
            explore_log.append({'node': n, 'frontier_list': sorted([(item['STATE'], item['h']) for item in FRONTIER], key=lambda x: x[1]), 'explored_list': list(REACHED.keys())})
            return SOLUTION(n), explore_log
            
        REACHED[n['STATE']] = n
        
        for action in ACTIONS(n['STATE']):
            child = CHILD_NODE(n['STATE'], n, action)
            m_state = child['STATE']
            if not any(item['STATE'] == m_state for item in FRONTIER) and m_state not in REACHED:
                child['h'] = MANHATTAN_DISTANCE(m_state, goal_state)
                child['path_cost'] = child['h']
                FRONTIER.append(child)
                
        explore_log.append({'node': n, 'frontier_list': sorted([(item['STATE'], item['h']) for item in FRONTIER], key=lambda x: x[1]), 'explored_list': list(REACHED.keys())})
    return None, explore_log

def A_STAR_SEARCH(initial_state, goal_state):
    explore_log = []
    h_start = MANHATTAN_DISTANCE(initial_state, goal_state)
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'g': 0, 'h': h_start, 'f': h_start}
    start_node['path_cost'] = start_node['f']
    FRONTIER = [start_node]
    REACHED = {}
    
    while FRONTIER:
        min_idx = min(range(len(FRONTIER)), key=lambda i: FRONTIER[i]['f'])
        n = FRONTIER.pop(min_idx)
        
        if n['STATE'] == goal_state:
            explore_log.append({'node': n, 'frontier_list': sorted([(item['STATE'], item['f']) for item in FRONTIER], key=lambda x: x[1]), 'explored_list': list(REACHED.keys())})
            return SOLUTION(n), explore_log
            
        REACHED[n['STATE']] = n
        
        for action in ACTIONS(n['STATE']):
            child = CHILD_NODE(n['STATE'], n, action)
            m_state = child['STATE']
            g_new = n['g'] + 1  
            frontier_idx = next((i for i, item in enumerate(FRONTIER) if item['STATE'] == m_state), None)
            
            if m_state in REACHED:
                if g_new >= REACHED[m_state]['g']: continue
                del REACHED[m_state]
                child['g'] = g_new
                child['h'] = MANHATTAN_DISTANCE(m_state, goal_state)
                child['f'] = g_new + child['h']
                child['path_cost'] = child['f']
                FRONTIER.append(child)
            elif frontier_idx is not None:
                if g_new < FRONTIER[frontier_idx]['g']:
                    FRONTIER[frontier_idx]['g'] = g_new
                    FRONTIER[frontier_idx]['f'] = g_new + FRONTIER[frontier_idx]['h']
                    FRONTIER[frontier_idx]['parent'] = n
                    FRONTIER[frontier_idx]['action'] = action
                    FRONTIER[frontier_idx]['depth'] = n['depth'] + 1
                    FRONTIER[frontier_idx]['path_cost'] = FRONTIER[frontier_idx]['f']
            else:
                child['g'] = g_new
                child['h'] = MANHATTAN_DISTANCE(m_state, goal_state)
                child['f'] = g_new + child['h']
                child['path_cost'] = child['f']
                FRONTIER.append(child)
                
        explore_log.append({'node': n, 'frontier_list': sorted([(item['STATE'], item['f']) for item in FRONTIER], key=lambda x: x[1]), 'explored_list': list(REACHED.keys())})
    return None, explore_log

def IDA_STAR_DFS(node, goal_state, threshold, explore_log, visited):
    h = MANHATTAN_DISTANCE(node['STATE'], goal_state)
    f = node['depth'] + h
    node['g'], node['h'], node['f'], node['path_cost'] = node['depth'], h, f, f

    if f > threshold: return f
    if node['STATE'] == goal_state:
        explore_log.append({'node': node, 'frontier_list': [], 'explored_list': list(visited)})
        return node
        
    minimum = float('inf')
    visited.add(node['STATE'])
    frontier_snapshot = []
    
    for action in ACTIONS(node['STATE']):
        child = CHILD_NODE(node['STATE'], node, action)
        if child['STATE'] in visited: continue
        frontier_snapshot.append((child['STATE'], child['depth'] + MANHATTAN_DISTANCE(child['STATE'], goal_state)))
        explore_log.append({'node': node, 'frontier_list': sorted(frontier_snapshot.copy(), key=lambda x: x[1]), 'explored_list': list(visited)})
        
        result = IDA_STAR_DFS(child, goal_state, threshold, explore_log, visited)
        if isinstance(result, dict): return result
        minimum = min(minimum, result)
        
    visited.remove(node['STATE'])
    return minimum

def IDA_STAR_SEARCH(initial_state, goal_state):
    explore_log = []
    start = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    threshold = MANHATTAN_DISTANCE(initial_state, goal_state)
    while True:
        explore_log.clear() 
        result = IDA_STAR_DFS(start, goal_state, threshold, explore_log, set())
        if isinstance(result, dict): return SOLUTION(result), explore_log
        if result == float('inf'): return None, explore_log
        threshold = result

def SIMPLE_HILL_CLIMBING(initial_state, goal_state):
    explore_log, trajectory = [], []
    current = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(initial_state, goal_state)}
    current['path_cost'] = current['h']
    
    for step in range(200):
        trajectory.append(f"Bước {step}: {current['STATE']} [h={current['h']}]")
        if current['STATE'] == goal_state:
            explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
            return SOLUTION(current), explore_log
            
        improved, next_node = False, None
        neighbors_vis = []
        for action in ACTIONS(current['STATE']):
            if not improved:
                child = CHILD_NODE(current['STATE'], current, action)
                child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
                child['path_cost'] = child['h']
                if child['h'] <= current['h']:
                    neighbors_vis.append((child['STATE'], child['h'], "-> CHỌN (<= Hiện tại)")); next_node = child; improved = True
                else: neighbors_vis.append((child['STATE'], child['h'], "Kém hơn"))
            else: neighbors_vis.append(("<Chưa sinh>", "?", "Bỏ qua"))
                
        explore_log.append({'node': current, 'frontier_list': neighbors_vis, 'explored_list': list(trajectory)})
        if not improved: break
        current = next_node
    return SOLUTION(current), explore_log

def STEEPEST_ASCENT_HILL_CLIMBING(initial_state, goal_state):
    explore_log, trajectory = [], []
    current = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(initial_state, goal_state)}
    current['path_cost'] = current['h']
    
    for step in range(200):
        trajectory.append(f"Bước {step}: {current['STATE']} [h={current['h']}]")
        if current['STATE'] == goal_state:
            explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
            return SOLUTION(current), explore_log
            
        children = []
        for action in ACTIONS(current['STATE']):
            child = CHILD_NODE(current['STATE'], current, action)
            child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
            child['path_cost'] = child['h']
            children.append(child)
            
        if not children: break
        min_child_h = min(c['h'] for c in children)
        next_node, chosen = None, False
        neighbors_vis = []
        
        for child in children:
            if child['h'] == min_child_h and min_child_h <= current['h'] and not chosen:
                next_node = child; neighbors_vis.append((child['STATE'], child['h'], "-> CHỌN")); chosen = True
            else: neighbors_vis.append((child['STATE'], child['h'], "Không tối ưu bằng"))
                
        explore_log.append({'node': current, 'frontier_list': neighbors_vis, 'explored_list': list(trajectory)})
        if next_node is None: break
        current = next_node
    return SOLUTION(current), explore_log

def Stochastic_Hill_Climbing(Start, goal_state):
    explore_log, trajectory = [], []
    current = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
    current['path_cost'] = current['h']
    
    for step in range(200):
        trajectory.append(f"Bước {step}: {current['STATE']} [h={current['h']}]")
        if current['STATE'] == goal_state:
            explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
            return SOLUTION(current), explore_log
            
        all_children, better = [], []
        for action in ACTIONS(current['STATE']):
            child = CHILD_NODE(current['STATE'], current, action)
            child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
            child['path_cost'] = child['h']
            all_children.append(child)
            if child['h'] <= current['h']: better.append(child)
                
        if not better:
            explore_log.append({'node': current, 'frontier_list': [(c['STATE'], c['h'], "Kém hơn") for c in all_children], 'explored_list': list(trajectory)})
            break
            
        next_node = random.choice(better)
        frontier_vis = []
        for child in all_children:
            if child == next_node: frontier_vis.append((child['STATE'], child['h'], "-> CHỌN NGẪU NHIÊN"))
            elif child in better: frontier_vis.append((child['STATE'], child['h'], "Hợp lệ"))
            else: frontier_vis.append((child['STATE'], child['h'], "Kém hơn"))
                
        explore_log.append({'node': current, 'frontier_list': frontier_vis, 'explored_list': list(trajectory)})
        current = next_node
    return SOLUTION(current), explore_log

def Random_Restart_Hill_Climbing(Start, goal_state):
    explore_log, trajectory = [], []
    for i in range(1, 16):
        current = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
        current['path_cost'] = current['h']
        trajectory.append(f"--- LƯỢT RESTART THỨ {i} ---")
        
        for step in range(50):
            trajectory.append(f"R{i}-STT {step}: {current['STATE']} [h={current['h']}]")
            if current['STATE'] == goal_state:
                explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
                return SOLUTION(current), explore_log
                
            all_children, better = [], []
            for action in ACTIONS(current['STATE']):
                child = CHILD_NODE(current['STATE'], current, action)
                child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
                child['path_cost'] = child['h']
                all_children.append(child)
                if child['h'] <= current['h']: better.append(child)
                    
            if not better:
                explore_log.append({'node': current, 'frontier_list': [(c['STATE'], c['h'], "Kém hơn") for c in all_children], 'explored_list': list(trajectory)})
                break
                
            next_node = random.choice(better)
            frontier_vis = []
            for child in all_children:
                if child == next_node: frontier_vis.append((child['STATE'], child['h'], "-> CHỌN NGẪU NHIÊN"))
                elif child in better: frontier_vis.append((child['STATE'], child['h'], "Hợp lệ"))
                else: frontier_vis.append((child['STATE'], child['h'], "Kém hơn"))
                    
            explore_log.append({'node': current, 'frontier_list': frontier_vis, 'explored_list': list(trajectory)})
            current = next_node
    return None, explore_log 

def Local_Beam_Search(Start, goal_state, k=2):
    explore_log = []
    start_node = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
    start_node['path_cost'] = start_node['h']
    Current_State_set = [start_node]
    
    while len(Current_State_set) < k:
        curr_state = Start
        for _ in range(random.randint(1, 4)):
            acts = ACTIONS(curr_state)
            if acts: curr_state = CHILD_NODE(curr_state, None, acts[0])['STATE']
        if not any(n['STATE'] == curr_state for n in Current_State_set):
            node = {'STATE': curr_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(curr_state, goal_state)}
            node['path_cost'] = node['h']
            Current_State_set.append(node)
            
    for step in range(100):
        beam_vis = [f"Chùm hiện tại (bước {step}):"]
        for i, n in enumerate(Current_State_set): beam_vis.append(f" T.Viên {i+1}: {n['STATE']} [h={n['h']}]")
            
        Neighbor_States = []
        for State in Current_State_set:
            for action in ACTIONS(State['STATE']):
                child = CHILD_NODE(State['STATE'], State, action)
                child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
                child['path_cost'] = child['h']
                Neighbor_States.append(child)
                
        if not Neighbor_States: break
        Neighbor_States.sort(key=lambda x: x['h'])
        
        for Neighbor in Neighbor_States:
            if Neighbor['STATE'] == goal_state:
                explore_log.append({'node': Neighbor, 'frontier_list': [(n['STATE'], n['h'], "ĐÍCH!") for n in Neighbor_States[:k+2]], 'explored_list': beam_vis})
                return SOLUTION(Neighbor), explore_log
                
        if Neighbor_States[0]['h'] > Current_State_set[0]['h']:
            explore_log.append({'node': Current_State_set[0], 'frontier_list': [(n['STATE'], n['h'], "Tệ hơn chùm cũ") for n in Neighbor_States[:k+3]], 'explored_list': beam_vis})
            break
            
        Next_State_set = Neighbor_States[:k]
        frontier_vis = []
        for i, n in enumerate(Neighbor_States):
            if i < k: frontier_vis.append((n['STATE'], n['h'], "-> CHỌN (Vào top k)"))
            elif i < k + 4: frontier_vis.append((n['STATE'], n['h'], "Bị loại khỏi chùm"))
                
        explore_log.append({'node': Current_State_set[0], 'frontier_list': frontier_vis, 'explored_list': beam_vis})
        Current_State_set = Next_State_set
    return None, explore_log

def Simulated_Annealing(start, goal):
    explore_log, trajectory = [], []
    T, Tmin, alpha = 100.0, 0.01, 0.95
    current_state = {'STATE': start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(start, goal)}
    current_state['path_cost'] = current_state['h']
    steps = 0

    while T > Tmin and steps < 2000:
        trajectory.append(f"T={T:.2f}: {current_state['STATE']} [h={current_state['h']}]")
        if current_state['STATE'] == goal:
            explore_log.append({'node': current_state, 'frontier_list': ["Đã tìm thấy đích!"], 'explored_list': list(trajectory)})
            return SOLUTION(current_state), explore_log
            
        next_state = CHILD_NODE(current_state['STATE'], current_state, random.choice(ACTIONS(current_state['STATE'])))
        next_state['h'] = MANHATTAN_DISTANCE(next_state['STATE'], goal)
        next_state['path_cost'] = next_state['h']
        
        Delta = next_state['h'] - current_state['h']
        accepted = False
        
        if Delta < 0:
            current_state, accepted = next_state, True
        else:
            p = math.exp(-Delta / T)
            if random.random() < p: current_state, accepted = next_state, True

        log_msg = "Chấp nhận (Tốt hơn)" if Delta < 0 else (f"Chấp nhận ngẫu nhiên (p={p:.3f})" if accepted else f"Từ chối (p={p:.3f})")
        explore_log.append({
            'node': current_state,
            'frontier_list': [f"Neighbor: {next_state['STATE']} | h={next_state['h']} -> {log_msg}"],
            'explored_list': list(trajectory)[-40:]
        })
        T *= alpha; steps += 1
        
    explore_log.append({'node': current_state, 'frontier_list': ["Hết nhiệt độ dừng lặp!"], 'explored_list': list(trajectory)})
    return (SOLUTION(current_state), explore_log) if current_state['STATE'] == goal else (None, explore_log)

def Sensorless_Conformant_A_Star(start_state, goal_state):
    explore_log = []
    belief_set = {start_state}
    temp_state = start_state
    for _ in range(2): 
        temp_state = SENSORLESS_APPLY_ACTION(temp_state, random.choice(ACTIONS(temp_state)))
        belief_set.add(temp_state)
    initial_belief = tuple(sorted(list(belief_set)))
    
    def BELIEF_HEURISTIC(b_state): return max(MANHATTAN_DISTANCE(s, goal_state) for s in b_state)

    h_start = BELIEF_HEURISTIC(initial_belief)
    start_node = {'BELIEF_STATE': initial_belief, 'STATE': initial_belief[0], 'parent': None, 'action': None, 'depth': 0, 'g': 0, 'h': h_start, 'f': h_start}
    start_node['path_cost'] = start_node['f']
    FRONTIER = [start_node]
    REACHED = {}

    while FRONTIER:
        min_idx = min(range(len(FRONTIER)), key=lambda i: FRONTIER[i]['f'])
        n = FRONTIER.pop(min_idx)
        
        if len(n['BELIEF_STATE']) == 1 and n['BELIEF_STATE'][0] == goal_state:
            explore_log.append({'node': n, 'frontier_list': ["Hội tụ thành công!"], 'explored_list': [f"Kích thước Belief cuối cùng: {len(n['BELIEF_STATE'])}"]})
            return SOLUTION(n), explore_log
            
        REACHED[n['BELIEF_STATE']] = n
        for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            child_belief = BELIEF_APPLY_ACTION(n['BELIEF_STATE'], action)
            g_new = n['g'] + 1
            
            frontier_idx = next((i for i, item in enumerate(FRONTIER) if item['BELIEF_STATE'] == child_belief), None)
            child_node = {'BELIEF_STATE': child_belief, 'STATE': child_belief[0], 'parent': n, 'action': action, 'depth': n['depth'] + 1, 'g': g_new, 'h': BELIEF_HEURISTIC(child_belief)}
            child_node['f'] = child_node['g'] + child_node['h']
            child_node['path_cost'] = child_node['f']
            
            if child_belief in REACHED:
                if g_new < REACHED[child_belief]['g']: del REACHED[child_belief]; FRONTIER.append(child_node)
            elif frontier_idx is not None:
                if g_new < FRONTIER[frontier_idx]['g']: FRONTIER[frontier_idx] = child_node
            else: FRONTIER.append(child_node)
                
        f_vis = [f"Belief {len(item['BELIEF_STATE'])} trạng thái | f={item['f']} (Act: {item['action']})" for item in FRONTIER]
        e_vis = [f"Đã duyệt tập Belief kích thước: {len(k)} phần tử\n  Chi tiết: {k}" for k in list(REACHED.keys())[-10:]]
        explore_log.append({'node': n, 'frontier_list': f_vis, 'explored_list': e_vis})
        if n['depth'] > 40: break
    return None, explore_log

def COMPLETELY_BLIND_BFS(common_goals):
    """
    Thuật toán TÌM KIẾM HOÀN TOÀN MÙ (Sensorless Completely Blind).
    Hiển thị trực quan tập Belief bằng cách liệt kê kích thước tập hợp và trạng thái đại diện.
    """
    explore_log = []
    
    # Khởi tạo Belief Start
    base_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    belief_start_set = {base_state}
    for _ in range(3):
        s = base_state
        for _ in range(8):
            s = SENSORLESS_APPLY_ACTION(s, random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT']))
        belief_start_set.add(s)
    
    belief_start = tuple(sorted(list(belief_start_set)))
    start_node = {
        'BELIEF_STATE': belief_start, 
        'STATE': belief_start[0], 
        'parent': None, 'action': None, 'depth': 0, 'path_cost': 0
    }
    
    frontier = deque([start_node])
    explored = {} # Dùng dict để lưu vết kèm theo độ sâu
    
    while frontier:
        node = frontier.popleft()
        explored[node['BELIEF_STATE']] = node['depth']
        
        # Kiểm tra Goal
        if all(s in common_goals for s in node['BELIEF_STATE']):
            explore_log.append({
                'node': node,
                'frontier_list': [">>> ĐÍCH ĐÃ ĐƯỢC HỘI TỤ (Belief Size=1) <<<"],
                'explored_list': [f"Final State: {node['STATE']}"]
            })
            return SOLUTION(node), explore_log
            
        for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            new_b_state = BELIEF_APPLY_ACTION(node['BELIEF_STATE'], action)
            
            if new_b_state == node['BELIEF_STATE'] or new_b_state in explored:
                continue
                
            if not any(n['BELIEF_STATE'] == new_b_state for n in frontier):
                child_node = {
                    'BELIEF_STATE': new_b_state,
                    'STATE': new_b_state[0],
                    'parent': node,
                    'action': action,
                    'depth': node['depth'] + 1,
                    'path_cost': node['depth'] + 1
                }
                frontier.append(child_node)
        
        f_display = [f"BSize: {len(n['BELIEF_STATE'])} | Via: {n['action']} | Rep: {n['STATE']}" for n in frontier]
        e_display = [f"Depth {d}: BSize {len(bs)} | Rep: {bs[0]}" for bs, d in explored.items()]
        
        explore_log.append({
            'node': node,
            'frontier_list': f_display,
            'explored_list': e_display
        })
        
        if len(explored) > 200: break
    return None, explore_log

def PARTIALLY_OBSERVABLE_BFS(start_partial, goal_partial):
    """
    Thuật toán QUAN SÁT 1 PHẦN.
    Hiển thị trực quan theo dạng so sánh giữa các trạng thái có thể xảy ra.
    """
    explore_log = []
    start_states = GENERATE_PARTIAL_STATES(start_partial)
    goal_states = set(GENERATE_PARTIAL_STATES(goal_partial))
    
    belief_start = tuple(sorted(start_states))
    start_node = {
        'BELIEF_STATE': belief_start, 
        'STATE': belief_start[0], 
        'parent': None, 'action': None, 'depth': 0, 'path_cost': 0
    }
    
    frontier = deque([start_node])
    explored = {}

    while frontier:
        node = frontier.popleft()
        explored[node['BELIEF_STATE']] = node['depth']
        
        if all(s in goal_states for s in node['BELIEF_STATE']):
            explore_log.append({'node': node, 'frontier_list': [">>> MỤC TIÊU ĐÃ XÁC ĐỊNH RÕ RÀNG <<<"], 'explored_list': []})
            return SOLUTION(node), explore_log

        for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            new_b_state = BELIEF_APPLY_ACTION(node['BELIEF_STATE'], action)
            if new_b_state == node['BELIEF_STATE'] or new_b_state in explored: continue
                
            if not any(n['BELIEF_STATE'] == new_b_state for n in frontier):
                child_node = {
                    'BELIEF_STATE': new_b_state,
                    'STATE': new_b_state[0],
                    'parent': node, 'action': action, 'depth': node['depth'] + 1, 'path_cost': node['depth'] + 1
                }
                frontier.append(child_node)
                
        f_display = [f"BSize: {len(n['BELIEF_STATE'])} | Move: {n['action']} | Rep: {n['STATE']}" for n in frontier]
        e_display = [f"Depth {d}: |BSize|={len(bs)}" for bs, d in explored.items()]
        
        explore_log.append({
            'node': node,
            'frontier_list': f_display,
            'explored_list': e_display
        })
        
        if len(explored) > 200: break
            
    return None, explore_log

def AND_OR_GRAPH_SEARCH(initial_state, goal_state):
    """
    Thuật toán AND-OR GRAPH SEARCH (Môi trường Không xác định / Erratic).
    Hành động có thể thành công hoặc thất bại (kẹt tại chỗ).
    """
    explore_log = []
    
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}
    frontier_or = [start_node]
    explored = set()
    
    step = 0
    while frontier_or and step < 200:
        step += 1
        node = frontier_or.pop(0)
        
        if node['STATE'] == goal_state:
            explore_log.append({'node': node, 'frontier_list': ["Đã tìm thấy ĐÍCH trên nhánh điều kiện này!"], 'explored_list': list(explored)})
            return SOLUTION(node), explore_log
            
        explored.add(node['STATE'])
        frontier_log_visual = []
        
        # Expand OR Node -> Choose actions
        for action in ACTIONS(node['STATE']):
            child_success = CHILD_NODE(node['STATE'], node, action)
            
            # Kết quả AND Node Outcomes (2 khả năng: Thành công rẽ hướng, Thất bại ở lại chỗ cũ)
            outcomes = [child_success['STATE'], node['STATE']]
            
            frontier_log_visual.append(f"OR-Act [{action}] -> AND-Outcomes: {outcomes[0]} & {outcomes[1]}(kẹt)")
            
            if child_success['STATE'] not in explored and not any(n['STATE'] == child_success['STATE'] for n in frontier_or):
                frontier_or.append(child_success)
                
        # Trực quan các nhánh trên giao diện Frontier
        explore_log.append({
            'node': node,
            'frontier_list': frontier_log_visual,
            'explored_list': [str(s) for s in list(explored)[-20:]]
        })
        
    return None, explore_log

def _find_optimal_length(start, goal):
    sol, _ = A_STAR_SEARCH(start, goal)
    if sol: return len(sol) - 1
    return -1

def _build_path_from_actions(initial_state, actions):
    path = [{'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}]
    curr = initial_state
    for a in actions:
        child = CHILD_NODE(curr, path[-1], a)
        path.append(child)
        curr = child['STATE']
    return path

# ───BACKTRACKING SEARCH ─────────────────────────────────────

def BACKTRACKING_SEARCH(initial_state, goal_state):
    """
    Mô hình hóa 8-puzzle như một bài toán CSP Lập kế hoạch (Planning CSP).
    Biến: A_0, A_1, ..., A_{L-1} (các hành động di chuyển).
    Miền giá trị: {UP, DOWN, LEFT, RIGHT}.
    Ràng buộc: Áp dụng chuỗi hành động từ initial_state phải dẫn đến goal_state.
    """
    explore_log = []
    L = _find_optimal_length(initial_state, goal_state)
    if L <= 0: return None, explore_log
    
    assignment = []
    
    def backtrack(state, depth):
        if depth == L:
            return assignment if state == goal_state else None
        if len(explore_log) > 3000: return 'timeout'
            
        for action in ACTIONS(state):
            child = CHILD_NODE(state, None, action)
            assignment.append(action)
            
            explore_log.append({
                'node': {'STATE': child['STATE'], 'depth': depth+1, 'path_cost': depth+1, 'action': f"Gán A{depth} = {action}"},
                'frontier_list': [f"Biến hiện tại: A{depth}", f"Giá trị thử: {action}"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
            
            res = backtrack(child['STATE'], depth + 1)
            if res == 'timeout': return 'timeout'
            if res: return res
            
            assignment.pop()
            explore_log.append({
                'node': {'STATE': state, 'depth': depth, 'path_cost': depth, 'action': f"QUAY LUI (Backtrack) A{depth}"},
                'frontier_list': [f"Biến hiện tại: A{depth}", "Thất bại, thử giá trị khác"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
        return None
        
    res = backtrack(initial_state, 0)
    if isinstance(res, list): return _build_path_from_actions(initial_state, res), explore_log
    return None, explore_log


# ───FORWARD CHECKING ────────────────────────────────────────

def FORWARD_CHECKING_SEARCH(initial_state, goal_state):
    """
    Forward Checking trên Planning CSP:
    Giống Backtracking, nhưng sau mỗi phép gán, kiểm tra xem khoảng cách Manhattan 
    có vượt quá số bước còn lại hay không. Nếu có -> cắt tỉa nhánh ngay lập tức.
    """
    explore_log = []
    L = _find_optimal_length(initial_state, goal_state)
    if L <= 0: return None, explore_log
    
    assignment = []
    
    def backtrack(state, depth):
        if depth == L: return assignment if state == goal_state else None
        if len(explore_log) > 3000: return 'timeout'
            
        for action in ACTIONS(state):
            child = CHILD_NODE(state, None, action)
            h = MANHATTAN_DISTANCE(child['STATE'], goal_state)
            
            # Forward Checking Pruning (Kiểm tra trước)
            if h > L - depth - 1:
                explore_log.append({
                    'node': {'STATE': child['STATE'], 'depth': depth+1, 'path_cost': depth+1, 'action': f"FC_PRUNE A{depth}={action}"},
                    'frontier_list': [f"CẮT TỈA: A{depth}={action}", f"Lý do: h={h} > {L - depth - 1} bước còn lại"],
                    'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
                })
                continue
                
            assignment.append(action)
            explore_log.append({
                'node': {'STATE': child['STATE'], 'depth': depth+1, 'path_cost': depth+1, 'action': f"Gán A{depth} = {action}"},
                'frontier_list': [f"Biến hiện tại: A{depth}", f"Đã vượt qua FC (h={h})"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
            
            res = backtrack(child['STATE'], depth + 1)
            if res == 'timeout': return 'timeout'
            if res: return res
            
            assignment.pop()
            explore_log.append({
                'node': {'STATE': state, 'depth': depth, 'path_cost': depth, 'action': f"QUAY LUI A{depth}"},
                'frontier_list': [f"Trở lại biến A{depth}"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
        return None
        
    res = backtrack(initial_state, 0)
    if isinstance(res, list): return _build_path_from_actions(initial_state, res), explore_log
    return None, explore_log


# ───AC-3 (Arc Consistency Algorithm 3) ──────────────────────

def AC3_SEARCH(initial_state, goal_state):
    """
    AC-3 trên Planning CSP:
    Áp dụng thuật toán AC-3 để loại bỏ các cặp hành động đối nghịch liên tiếp 
    (ví dụ: UP rồi DOWN) trước khi bắt đầu tìm kiếm.
    """
    explore_log = []
    L = _find_optimal_length(initial_state, goal_state)
    if L <= 0: return None, explore_log
    
    domains = {i: ['UP', 'DOWN', 'LEFT', 'RIGHT'] for i in range(L)}
    opposites = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    queue = [(i, i+1) for i in range(L-1)] + [(i+1, i) for i in range(L-1)]
    
    step = 0
    while queue and step < 1000:
        step += 1
        i, j = queue.pop(0)
        revised = False
        to_remove = []
        for x in domains[i]:
            if len(domains[j]) == 1 and domains[j][0] == opposites[x]:
                to_remove.append(x)
                revised = True
        for x in to_remove: domains[i].remove(x)
            
        explore_log.append({
            'node': {'STATE': initial_state, 'depth': step, 'path_cost': step, 'action': f"AC3 Cung ({i},{j}) {'-> THU HẸP' if revised else '-> HỢP LỆ'}"},
            'frontier_list': [f"A{k} domain: {domains[k]}" for k in range(L)],
            'explored_list': [f"Đã duyệt cung ({i},{j})"]
        })
        
        if revised:
            for k in range(L):
                if k != i and abs(k - i) == 1 and k != j: queue.append((k, i))
                    
    # Tiến hành FC Search trên Domain đã thu hẹp
    assignment = []
    def backtrack(state, depth):
        if depth == L: return assignment if state == goal_state else None
        if len(explore_log) > 4000: return 'timeout'
        
        for action in domains[depth]:
            if action not in ACTIONS(state): continue
            child = CHILD_NODE(state, None, action)
            h = MANHATTAN_DISTANCE(child['STATE'], goal_state)
            if h > L - depth - 1: continue
            
            assignment.append(action)
            explore_log.append({
                'node': {'STATE': child['STATE'], 'depth': depth+1, 'path_cost': depth+1, 'action': f"Gán A{depth} = {action}"},
                'frontier_list': [f"Domain A{depth}: {domains[depth]}"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
            
            res = backtrack(child['STATE'], depth + 1)
            if res == 'timeout': return 'timeout'
            if res: return res
            
            assignment.pop()
    
    res = backtrack(initial_state, 0)
    if isinstance(res, list): return _build_path_from_actions(initial_state, res), explore_log
    return None, explore_log


# ───MIN-CONFLICTS ───────────────────────────────────────────

def MIN_CONFLICTS_SEARCH(initial_state, goal_state, max_steps=2000):
    """
    Min-Conflicts trên Planning CSP:
    Khởi tạo ngẫu nhiên một chuỗi hành động L bước.
    Liên tục chọn ngẫu nhiên 1 biến (1 bước) và thay đổi nó sao cho
    khoảng cách đến đích của trạng thái cuối là nhỏ nhất.
    """
    explore_log = []
    L = _find_optimal_length(initial_state, goal_state)
    if L <= 0: return None, explore_log
    
    assignment = [random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT']) for _ in range(L)]
    
    def evaluate(assign):
        state = initial_state
        for a in assign: state = SENSORLESS_APPLY_ACTION(state, a)
        return MANHATTAN_DISTANCE(state, goal_state)
        
    for step in range(max_steps):
        conflicts = evaluate(assignment)
        
        state_end = initial_state
        for a in assignment: state_end = SENSORLESS_APPLY_ACTION(state_end, a)
        
        if state_end == goal_state:
            explore_log.append({
                'node': {'STATE': state_end, 'depth': step, 'path_cost': step, 'action': "GIẢI XONG MIN-CONFLICTS!"},
                'frontier_list': [f"Số xung đột (Khoảng cách): 0"],
                'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
            })
            return _build_path_from_actions(initial_state, assignment), explore_log
            
        var = random.randint(0, L-1)
        min_c = conflicts
        best_vals = [assignment[var]]
        
        for val in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if val == assignment[var]: continue
            old = assignment[var]
            assignment[var] = val
            c = evaluate(assignment)
            if c < min_c:
                min_c = c
                best_vals = [val]
            elif c == min_c:
                best_vals.append(val)
            assignment[var] = old
            
        chosen_val = random.choice(best_vals)
        old_val = assignment[var]
        assignment[var] = chosen_val
        
        # Visualize state at modified variable
        state_at_var = initial_state
        for i in range(var+1): state_at_var = SENSORLESS_APPLY_ACTION(state_at_var, assignment[i])
        
        explore_log.append({
            'node': {'STATE': state_at_var, 'depth': step, 'path_cost': step, 'action': f"Chọn biến A{var}: {old_val} -> {chosen_val}"},
            'frontier_list': [f"Số xung đột tổng: {min_c}"],
            'explored_list': [f"A{i}={a}" for i, a in enumerate(assignment)]
        })
        
    return None, explore_log


# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Professional Edition")
        self.root.geometry("1100x750")
        self.root.minsize(950, 600)
        self.root.configure(bg='white')
        
        self.solution_path = []
        self.explore_log = []
        self.current_step = 0
        self.is_playing = False
        self.play_job = None
        self.target_goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        
        self.algo_var = tk.StringVar(value='BFS')
        self.speed_var = tk.IntVar(value=300)
        self.max_depth_var = tk.IntVar(value=50)
        
        # Default Belief Goals hay dùng
        self.common_goals = [
            (1, 2, 3, 4, 5, 6, 7, 8, 0),
            (1, 2, 3, 8, 0, 4, 7, 6, 5),
            (8, 7, 6, 1, 0, 5, 2, 3, 4)
        ]
        
        self._build_ui()

    def _build_ui(self):
        top_frame = tk.Frame(self.root, bg='white', bd=1, relief='solid')
        top_frame.pack(fill='x', padx=10, pady=10)

        ctrl_grid = tk.Frame(top_frame, bg='white')
        ctrl_grid.pack(pady=5)
        title_font = ('Consolas', 10, 'bold')

        tk.Label(ctrl_grid, text="INITIAL STATE", bg='white', font=title_font).grid(row=0, column=0, padx=10, sticky='s', pady=(0, 2))
        tk.Label(ctrl_grid, text="GOAL STATE", bg='white', font=title_font).grid(row=0, column=1, padx=10, sticky='s', pady=(0, 2))
        tk.Label(ctrl_grid, text="ALGORITHM", bg='white', font=title_font).grid(row=0, column=2, padx=10, sticky='s', pady=(0, 2))
        tk.Label(ctrl_grid, text="SPEED (ms)", bg='white', font=title_font).grid(row=0, column=3, padx=10, sticky='s', pady=(0, 2))
        
        self.depth_title_lbl = tk.Label(ctrl_grid, text="MAX DEPTH", bg='white', font=title_font)
        self.depth_title_lbl.grid(row=0, column=4, padx=10, sticky='s', pady=(0, 2))

        init_f = tk.Frame(ctrl_grid, bg='white')
        init_f.grid(row=1, column=0, padx=10, sticky='n')
        self.init_cells = self._create_grid(init_f, [1, 2, 3, 4, 0, 6, 7, 5, 8])

        goal_f = tk.Frame(ctrl_grid, bg='white')
        goal_f.grid(row=1, column=1, padx=10, sticky='n')
        self.goal_cells = self._create_grid(goal_f, [1, 2, 3, 4, 5, 6, 7, 8, 0])

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="white", background="white")
        
        algorithms = [
            "BFS", "DFS", "IDS", "UCS", "Greedy_Search", "A*", "IDA*",
            "Simple_Hill_Climbing", "Steepest_Ascent_Hill_Climbing",
            "Stochastic_Hill_Climbing", "Random_Restart_Hill_Climbing",
            "Local_Beam_Search", "Simulated_Annealing", "Sensorless_Conformant_A*",
            "Completely_Blind_BFS", "Partially_Observable_BFS", "AND_OR_GRAPH_SEARCH",
            "Backtracking_Search", "Forward_Checking", "AC3", "Min_Conflicts"
        ]
        
        self.algo_cb = ttk.Combobox(ctrl_grid, textvariable=self.algo_var, 
                                    values=algorithms, state="readonly", width=32, font=('Consolas', 11))
        self.algo_cb.grid(row=1, column=2, padx=10, sticky='n', pady=20)
        self.algo_cb.bind("<<ComboboxSelected>>", self._toggle_depth_visibility)

        speed_ctrl = tk.Frame(ctrl_grid, bg='white')
        speed_ctrl.grid(row=1, column=3, padx=10, sticky='n', pady=20)
        tk.Scale(speed_ctrl, from_=50, to=1500, orient='horizontal', variable=self.speed_var, 
                bg='white', bd=0, highlightthickness=0, showvalue=False, length=100).pack(side='left')
        tk.Entry(speed_ctrl, textvariable=self.speed_var, width=5, justify='center', font=('Consolas', 10), 
                bg='white', bd=1, relief='solid').pack(side='left', padx=(5,0))

        self.depth_ctrl_frame = tk.Frame(ctrl_grid, bg='white')
        self.depth_ctrl_frame.grid(row=1, column=4, padx=10, sticky='n', pady=20)
        tk.Scale(self.depth_ctrl_frame, from_=1, to=1000, orient='horizontal', variable=self.max_depth_var, 
                bg='white', bd=0, highlightthickness=0, showvalue=False, length=80).pack(side='left')
        tk.Entry(self.depth_ctrl_frame, textvariable=self.max_depth_var, width=6, justify='center', font=('Consolas', 10), 
                bg='white', bd=1, relief='solid').pack(side='left', padx=(5,0))

        btn_f = tk.Frame(ctrl_grid, bg='white')
        btn_f.grid(row=0, column=5, rowspan=2, padx=(20, 0))
        tk.Button(btn_f, text="SOLVE", command=self._solve, bg='white', activebackground='#f0f0f0',
                font=('Consolas', 12, 'bold'), bd=1, relief='solid', width=12).pack()

        solution_frame = tk.Frame(self.root, bg='white', bd=1, relief='solid')
        solution_frame.pack(fill='x', padx=10, pady=(0, 10))
        tk.Label(solution_frame, text="ĐƯỜNG ĐI (SOLUTION PATH)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        
        canvas_container = tk.Frame(solution_frame, bg='white')
        canvas_container.pack(fill='x', padx=5, pady=5)
        
        self.sol_canvas = tk.Canvas(canvas_container, bg='#fafafa', height=120, highlightthickness=0)
        self.sol_scrollbar = tk.Scrollbar(canvas_container, orient="horizontal", command=self.sol_canvas.xview)
        self.sol_canvas.configure(xscrollcommand=self.sol_scrollbar.set)
        
        self.sol_canvas.pack(side="top", fill="x", expand=True)
        self.sol_scrollbar.pack(side="bottom", fill="x")

        main_body = tk.Frame(self.root, bg='white')
        main_body.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        left_col = tk.Frame(main_body, bg='white', bd=1, relief='solid', width=320)
        left_col.pack(side='left', fill='y', padx=(0, 5))
        left_col.pack_propagate(False)

        tk.Label(left_col, text="NODE ĐANG KHẢO SÁT", bg='white', font=('Consolas', 10, 'bold')).pack(pady=10)
        
        self.board_labels = []
        puzzle_grid = tk.Frame(left_col, bg='white', bd=1, relief='solid')
        puzzle_grid.pack(pady=5)
        for i in range(3):
            row_l = []
            for j in range(3):
                lbl = tk.Label(puzzle_grid, text="", width=4, height=2, font=('Consolas', 22, 'bold'),
                            bg='white', bd=1, relief='solid', fg='black')
                lbl.grid(row=i, column=j, padx=2, pady=2)
                row_l.append(lbl)
            self.board_labels.append(row_l)

        ctrl_frame2 = tk.Frame(left_col, bg='white')
        ctrl_frame2.pack(pady=10)
        btn_opts = {'bg': 'white', 'activebackground': '#f0f0f0', 'bd': 1, 'relief': 'solid', 'width': 8, 'font': ('Consolas', 10)}
        self.btn_prev = tk.Button(ctrl_frame2, text="Prev", command=self._go_prev, state='disabled', **btn_opts)
        self.btn_prev.pack(side='left', padx=5)
        self.btn_play = tk.Button(ctrl_frame2, text="Play", command=self._toggle_play, state='disabled', **btn_opts)
        self.btn_play.pack(side='left', padx=5)
        self.btn_next = tk.Button(ctrl_frame2, text="Next", command=self._go_next, state='disabled', **btn_opts)
        self.btn_next.pack(side='left', padx=5)

        info_frame = tk.Frame(left_col, bg='white', bd=1, relief='solid')
        info_frame.pack(pady=10, fill='x', padx=10)
        lbl_opts = {'bg': 'white', 'font': ('Consolas', 10)}
        
        self.info_step_lbl = tk.Label(info_frame, text="Step: 0 / 0", **lbl_opts)
        self.info_step_lbl.grid(row=0, column=0, sticky='w', padx=15, pady=3)
        
        self.info_cost_lbl = tk.Label(info_frame, text="Cost / Evaluation: 0", **lbl_opts)
        self.info_cost_lbl.grid(row=1, column=0, sticky='w', padx=15, pady=3)
        
        self.info_depth_lbl = tk.Label(info_frame, text="Depth: 0", **lbl_opts)
        self.info_depth_lbl.grid(row=2, column=0, sticky='w', padx=15, pady=3)
        
        self.info_nodes_lbl = tk.Label(info_frame, text="Nodes Generated: 0", **lbl_opts)
        self.info_nodes_lbl.grid(row=3, column=0, sticky='w', padx=15, pady=3)

        right_col = tk.Frame(main_body, bg='white')
        right_col.pack(side='left', fill='both', expand=True)
        list_opts = {'bg': '#fafafa', 'fg': 'black', 'bd': 0, 'highlightthickness': 0, 
                    'font': ('Consolas', 10), 'selectbackground': '#d9d9d9', 'selectforeground': 'black'}

        frontier_frame = tk.Frame(right_col, bg='white', bd=1, relief='solid')
        frontier_frame.pack(side='left', fill='both', expand=True, padx=(5, 5))
        tk.Label(frontier_frame, text="FRONTIER / NEIGHBORS (Hàng đợi)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        
        f_list_container = tk.Frame(frontier_frame, bg='white', bd=1, relief='solid')
        f_list_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        scroll_f_y = tk.Scrollbar(f_list_container, orient=tk.VERTICAL, bd=1, bg='white')
        scroll_f_x = tk.Scrollbar(f_list_container, orient=tk.HORIZONTAL, bd=1, bg='white')
        
        self.list_frontier = tk.Listbox(f_list_container, yscrollcommand=scroll_f_y.set, xscrollcommand=scroll_f_x.set, **list_opts)
        scroll_f_y.config(command=self.list_frontier.yview)
        scroll_f_x.config(command=self.list_frontier.xview)
        
        scroll_f_y.pack(side='right', fill='y')
        scroll_f_x.pack(side='bottom', fill='x')
        self.list_frontier.pack(side='left', fill='both', expand=True)

        explored_frame = tk.Frame(right_col, bg='white', bd=1, relief='solid')
        explored_frame.pack(side='right', fill='both', expand=True, padx=(0, 0))
        tk.Label(explored_frame, text="REACHED / TRẠNG THÁI (Đã duyệt)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        
        e_list_container = tk.Frame(explored_frame, bg='white', bd=1, relief='solid')
        e_list_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        scroll_e_y = tk.Scrollbar(e_list_container, orient=tk.VERTICAL, bd=1, bg='white')
        scroll_e_x = tk.Scrollbar(e_list_container, orient=tk.HORIZONTAL, bd=1, bg='white')
        
        self.list_explored = tk.Listbox(e_list_container, yscrollcommand=scroll_e_y.set, xscrollcommand=scroll_e_x.set, **list_opts)
        scroll_e_y.config(command=self.list_explored.yview)
        scroll_e_x.config(command=self.list_explored.xview)
        
        scroll_e_y.pack(side='right', fill='y')
        scroll_e_x.pack(side='bottom', fill='x')
        self.list_explored.pack(side='left', fill='both', expand=True)
        
        self._toggle_depth_visibility()

    def _create_grid(self, parent, defaults):
        cells = []
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(parent, width=2, justify='center', font=('Consolas', 12, 'bold'), bg='white', bd=1, relief='solid')
                e.grid(row=i, column=j, padx=1, pady=1)
                e.insert(0, str(defaults[i*3+j]))
                row.append(e)
            cells.append(row)
        return cells

    def _read_grid(self, cells, allow_x=False):
        """Hỗ trợ đọc lưới chữ 'x' nếu dùng thuật toán Partially Observable."""
        try:
            res = []
            for r in cells:
                for c in r:
                    val = c.get().strip().lower()
                    if allow_x and val == 'x':
                        res.append('x')
                    else:
                        res.append(int(val))
            
            if not allow_x and sorted(res) != list(range(9)): 
                raise ValueError
            return tuple(res)
        except:
            return None

    def _toggle_depth_visibility(self, event=None):
        """Điều khiển việc ẩn/hiện độ sâu và Khóa/Mở Khóa ô nhập liệu Start/Goal."""
        algo = self.algo_var.get()
        if algo in ['DFS', 'IDS']:
            self.depth_title_lbl.grid()
            self.depth_ctrl_frame.grid()
        else:
            self.depth_title_lbl.grid_remove()
            self.depth_ctrl_frame.grid_remove()
            
        # Kiểm soát ô nhập (Mù hoàn toàn -> Khóa; Khác -> Mở)
        if algo == 'Completely_Blind_BFS':
            for r in self.init_cells:
                for c in r: c.config(state='disabled')
            for r in self.goal_cells:
                for c in r: c.config(state='disabled')
        else:
            for r in self.init_cells:
                for c in r: c.config(state='normal')
            for r in self.goal_cells:
                for c in r: c.config(state='normal')

    def _solve(self):
        self._stop_play()
        algo = self.algo_var.get()
        allow_x = (algo == 'Partially_Observable_BFS')
        m_depth = self.max_depth_var.get()
        
        init, goal = None, None
        
        # Nếu không phải tìm kiếm mù, đọc giá trị mảng
        if algo != 'Completely_Blind_BFS':
            init = self._read_grid(self.init_cells, allow_x)
            goal = self._read_grid(self.goal_cells, allow_x)
            
            if not init or not goal: 
                msg = "Vui lòng nhập đủ các số từ 0 đến 8 không trùng lặp." if not allow_x else "Vui lòng nhập ký tự số và 'x' hợp lệ."
                messagebox.showerror("Lỗi", msg)
                return
            
            if not allow_x: self.target_goal = goal

        if algo == 'BFS': sol, log = BREADTH_FIRST_SEARCH(init, goal)
        elif algo == 'DFS': sol, log = DEPTH_FIRST_SEARCH(init, goal, max_depth=m_depth)
        elif algo == 'IDS': sol, log = ITERATIVE_DEEPENING_SEARCH(init, goal, max_depth=m_depth)
        elif algo == 'UCS': sol, log = UNIFORM_COST_SEARCH(init, goal)
        elif algo == 'Greedy_Search': sol, log = GREEDY_SEARCH(init, goal)
        elif algo == 'A*': sol, log = A_STAR_SEARCH(init, goal)
        elif algo == 'IDA*': sol, log = IDA_STAR_SEARCH(init, goal)
        elif algo == 'Simple_Hill_Climbing': sol, log = SIMPLE_HILL_CLIMBING(init, goal)
        elif algo == 'Steepest_Ascent_Hill_Climbing': sol, log = STEEPEST_ASCENT_HILL_CLIMBING(init, goal)
        elif algo == 'Stochastic_Hill_Climbing': sol, log = Stochastic_Hill_Climbing(init, goal)
        elif algo == 'Random_Restart_Hill_Climbing': sol, log = Random_Restart_Hill_Climbing(init, goal)
        elif algo == 'Local_Beam_Search': sol, log = Local_Beam_Search(init, goal)
        elif algo == 'Simulated_Annealing': sol, log = Simulated_Annealing(init, goal)
        elif algo == 'Sensorless_Conformant_A*': sol, log = Sensorless_Conformant_A_Star(init, goal)
        elif algo == 'Completely_Blind_BFS': sol, log = COMPLETELY_BLIND_BFS(self.common_goals)
        elif algo == 'Partially_Observable_BFS': sol, log = PARTIALLY_OBSERVABLE_BFS(init, goal)
        elif algo == 'AND_OR_GRAPH_SEARCH':       sol, log = AND_OR_GRAPH_SEARCH(init, goal)
        elif algo == 'Backtracking_Search': sol, log = BACKTRACKING_SEARCH(init, goal)
        elif algo == 'Forward_Checking':    sol, log = FORWARD_CHECKING_SEARCH(init, goal)
        elif algo == 'AC3':                 sol, log = AC3_SEARCH(init, goal)
        elif algo == 'Min_Conflicts':       sol, log = MIN_CONFLICTS_SEARCH(init, goal)

        self.solution_path = sol if sol else []
        self.explore_log = log
        self.current_step = 0
        
        self._draw_solution_canvas()

        for b in [self.btn_prev, self.btn_play, self.btn_next]:
            b.config(state='normal' if log else 'disabled')
            
        self._refresh_display()
        
        if sol is None:
            messagebox.showwarning("Không tìm thấy đường", f"THUẬT TOÁN THẤT BẠI!\n\n- Thuật toán: {algo}\n- Không thể tìm thấy đích.")
        else:
            final_state = sol[-1]['STATE']
            if algo not in [
                'Sensorless_Conformant_A*', 'Completely_Blind_BFS',
                'Partially_Observable_BFS', 'AND_OR_GRAPH_SEARCH',
                # CSP: kết quả là goal_state, không phải bước trung gian
                'Backtracking_Search', 'Forward_Checking', 'AC3', 'Min_Conflicts'
            ] and final_state != self.target_goal:
                messagebox.showwarning("Cực đại cục bộ", f"THUẬT TOÁN BỊ KẸT!\n\n- Thuật toán: {algo}\n- Dừng tại bước khảo sát.")
            else:
                messagebox.showinfo("Thống kê", f"GIẢI THÀNH CÔNG!\n\n- Thuật toán: {algo}\n- Độ dài đường đi: {len(sol)-1} bước")

    def _draw_solution_canvas(self):
        self.sol_canvas.delete("all")
        if not self.solution_path: return
        
        cell_size, arrow_space, y_offset, x_offset = 28, 60, 15, 20
        grid_size = cell_size * 3
        
        for i, node in enumerate(self.solution_path):
            state = node['STATE']
            for row in range(3):
                for col in range(3):
                    val = state[row*3 + col]
                    x1 = x_offset + col * cell_size
                    y1 = y_offset + row * cell_size
                    x2, y2 = x1 + cell_size, y1 + cell_size
                    
                    bg_color = 'white'
                    if isinstance(val, int) and hasattr(self, 'target_goal'):
                        if val == self.target_goal[row*3+col] and val != 0: bg_color = '#90EE90'
                    
                    self.sol_canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline='black')
                    if val != 0 and val != 'x':
                        self.sol_canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, text=str(val), font=('Consolas', 10, 'bold'))
            
            self.sol_canvas.create_text(x_offset + grid_size/2, y_offset - 8, text=f"Step {i}", font=('Consolas', 8, 'bold'), fill='blue')

            if i < len(self.solution_path) - 1:
                next_action = self.solution_path[i+1]['action']
                arrow_start_x = x_offset + grid_size + 10
                arrow_end_x = arrow_start_x + arrow_space - 20
                arrow_y = y_offset + grid_size / 2
                
                self.sol_canvas.create_line(arrow_start_x, arrow_y, arrow_end_x, arrow_y, arrow=tk.LAST, width=2)
                self.sol_canvas.create_text((arrow_start_x + arrow_end_x)/2, arrow_y - 12, text=f"[{next_action}]", font=('Consolas', 9, 'bold'), fill='red')
                
            x_offset += grid_size + arrow_space
        self.sol_canvas.config(scrollregion=self.sol_canvas.bbox("all"))

    def _refresh_display(self):
        if not self.explore_log: return
        self.current_step = max(0, min(self.current_step, len(self.explore_log)-1))
        
        step_data = self.explore_log[self.current_step]
        current_node = step_data['node']
        state = current_node['STATE']
        algo = self.algo_var.get()
        
        for i in range(3):
            for j in range(3):
                val = state[i*3+j]
                bg_color = 'white'
                if hasattr(self, 'target_goal') and algo not in ['Completely_Blind_BFS', 'Partially_Observable_BFS']:
                    if val == self.target_goal[i*3+j] and val != 0: bg_color = '#90EE90'
                
                # Hiệu ứng UI đặc biệt cho CSP Models
                is_csp = algo in ['Backtracking_Search', 'Forward_Checking', 'AC3', 'Min_Conflicts']
                if is_csp and 'action' in current_node:
                    act_str = current_node['action']
                    if "PRUNE" in act_str or "QUAY LUI" in act_str:
                        bg_color = '#FFCCCC' # Đỏ nhạt báo hiệu prune/backtrack
                    elif "Gán" in act_str or "Chọn biến" in act_str:
                        bg_color = '#FFFF99' # Vàng báo hiệu đang gán thử
                
                self.board_labels[i][j].config(text=str(val) if (val != 0 and val != 'x') else "", bg=bg_color)
                
        self.info_step_lbl.config(text=f"Step Log: {self.current_step + 1} / {len(self.explore_log)}")
        
        if algo in ['Greedy_Search', 'Simple_Hill_Climbing', 'Steepest_Ascent_Hill_Climbing',
                    'Stochastic_Hill_Climbing', 'Random_Restart_Hill_Climbing', 'Local_Beam_Search', 'Simulated_Annealing']:
            self.info_cost_lbl.config(text=f"Heuristic h(n) = Manhattan: {current_node.get('h', 0)}")
        elif algo in ['A*', 'IDA*', 'Sensorless_Conformant_A*']:
            self.info_cost_lbl.config(text=f"f(n) = g+h: {current_node.get('f', 0)} (g={current_node.get('g', 0)}, h={current_node.get('h', 0)})")
        elif algo in ['Backtracking_Search', 'Forward_Checking', 'AC3', 'Min_Conflicts']:
            self.info_cost_lbl.config(text=f"Hành động CSP: {current_node.get('action', '')}")
        else:
            self.info_cost_lbl.config(text=f"Path-Cost: {current_node['path_cost']}")
            
        self.info_depth_lbl.config(text=f"Depth / Bước: {current_node.get('depth', 0)}")
        
        if algo in ['Backtracking_Search', 'Forward_Checking', 'AC3']:
            self.info_nodes_lbl.config(text=f"CSP: Thử/Cắt tỉa domain")
        elif algo == 'Min_Conflicts':
            self.info_nodes_lbl.config(text=f"CSP: Tìm kiếm cục bộ (Local Search)")
        else:
            self.info_nodes_lbl.config(text=f"List Records: Frontier={len(step_data['frontier_list'])} / Reached={len(step_data['explored_list'])}")

        self.list_frontier.delete(0, tk.END)

        is_csp_algo = algo in ['Backtracking_Search', 'Forward_Checking', 'AC3', 'Min_Conflicts']

        for idx, item in enumerate(step_data['frontier_list'], 1):
            if isinstance(item, tuple):
                if len(item) == 3:
                    s, score, note = item
                    self.list_frontier.insert(tk.END, f" {idx:02d}. {s} [h={score}] : {note}")
                elif len(item) == 2:
                    s, score = item
                    label_char = 'h' if algo == 'Greedy_Search' \
                        else ('f' if algo in ['A*', 'IDA*', 'Sensorless_Conformant_A*'] else 'Cost')
                    self.list_frontier.insert(tk.END, f" {idx:02d}. {s} [{label_char}={score}]")
            else:
                prefix = "🧩" if is_csp_algo else "  "
                self.list_frontier.insert(tk.END, f" {prefix} {item}")
            
        self.list_explored.delete(0, tk.END)
        for idx, s in enumerate(step_data['explored_list'], 1):
            prefix = "✔" if is_csp_algo else " "
            self.list_explored.insert(tk.END, f" {prefix} {s}")

    def _go_prev(self):
        if self.current_step > 0: self.current_step -= 1; self._refresh_display()

    def _go_next(self):
        if self.current_step < len(self.explore_log) - 1: self.current_step += 1; self._refresh_display()

    def _toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.config(text="Stop" if self.is_playing else "Play")
        if self.is_playing: self._auto_run()

    def _auto_run(self):
        if not self.is_playing: return
        if self.current_step < len(self.explore_log) - 1:
            self._go_next()
            self.play_job = self.root.after(self.speed_var.get(), self._auto_run)
        else: self._stop_play()

    def _stop_play(self):
        self.is_playing = False
        self.btn_play.config(text="Play")
        if self.play_job: self.root.after_cancel(self.play_job); self.play_job = None

if __name__ == '__main__':
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()