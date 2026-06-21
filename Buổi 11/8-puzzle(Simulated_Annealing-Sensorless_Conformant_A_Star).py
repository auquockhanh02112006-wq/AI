import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import heapq

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
        'path_cost': parent['path_cost'] if parent else 0
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
    """
    Hàm Heuristic h1(n): Đếm số lượng ô nằm sai vị trí so với trạng thái đích.
    """
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])

def MANHATTAN_DISTANCE(state, goal):
    """
    Hàm Heuristic h2(n): Tổng khoảng cách Manhattan dịch chuyển của các ô về vị trí đích.
    """
    distance = 0
    for i in range(9):
        val = state[i]
        if val != 0:  
            goal_idx = goal.index(val)
            r1, col1 = i // 3, i % 3
            r2, col2 = goal_idx // 3, goal_idx % 3
            distance += abs(r1 - r2) + abs(col1 - col2)
    return distance

def BREADTH_FIRST_SEARCH(initial_state, goal_state):
    """Tìm kiếm theo chiều rộng (BFS) - Đảm bảo tối ưu số bước đi."""
    explore_log = []
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}
    if node['STATE'] == goal_state: 
        return SOLUTION(node), explore_log
    
    frontier = deque([node])
    frontier_set = {node['STATE']}
    explored = {}
    
    while frontier:
        node = frontier.popleft()
        frontier_set.discard(node['STATE'])
        explored[node['STATE']] = True
        
        for action in ACTIONS(node['STATE']):
            child = CHILD_NODE(node['STATE'], node, action)
            child['path_cost'] = child['depth']
            
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
    """Tìm kiếm theo chiều sâu (DFS) giới hạn độ sâu tối đa nhằm tránh tràn bộ nhớ."""
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
                child['path_cost'] = child['depth']
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
    """Hàm đệ quy hỗ trợ cho Tìm kiếm giới hạn độ sâu (DLS)."""
    if node['STATE'] == goal_state:
        explore_log.append({
            'node': node,
            'frontier_list': list(current_frontier),
            'explored_list': list(visited.keys())
        })
        return SOLUTION(node)
    if node['depth'] >= limit: 
        return 'cutoff'
        
    visited[node['STATE']] = True
    cutoff_occurred = False
    children = []
    
    for action in ACTIONS(node['STATE']):
        child = CHILD_NODE(node['STATE'], node, action)
        child['path_cost'] = child['depth']
        if child['STATE'] not in visited:
            children.append(child)
            
    current_frontier.extend([(c['STATE'], c['path_cost']) for c in children])
    explore_log.append({
        'node': node,
        'frontier_list': list(current_frontier),
        'explored_list': list(visited.keys())
    })
    
    for child in children:
        current_frontier.remove((child['STATE'], child['path_cost']))
        result = _RECURSIVE_DLS(child, goal_state, limit, explore_log, visited, current_frontier)
        current_frontier.append((child['STATE'], child['path_cost']))
        if result == 'cutoff': cutoff_occurred = True
        elif result is not None: return result
        
    del visited[node['STATE']] 
    return 'cutoff' if cutoff_occurred else None

def ITERATIVE_DEEPENING_SEARCH(initial_state, goal_state, max_depth=1000):
    """Tìm kiếm sâu dần (IDS) - Kết hợp ưu điểm không gian của DFS và tính tối ưu của BFS."""
    explore_log = []
    for depth in range(max_depth + 1):
        result = _RECURSIVE_DLS({'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}, 
                                goal_state, depth, explore_log, {}, [])
        if result != 'cutoff': 
            return result, explore_log
    return None, explore_log

def UNIFORM_COST_SEARCH(initial_state, goal_state):
    """Tìm kiếm chi phí đồng nhất (UCS) mở rộng dựa trên hàm chi phí đường đi."""
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
        if node['STATE'] in frontier_dict:
            del frontier_dict[node['STATE']]
            
        if node['STATE'] == goal_state:
            explore_log.append({
                'node': node,
                'frontier_list': list(frontier_dict.items()),
                'explored_list': list(explored.keys())
            })
            return SOLUTION(node), explore_log
            
        for action in ACTIONS(node['STATE']):
            child = CHILD_NODE(node['STATE'], node, action)
            step_cost = MISPLACED_TILES(child['STATE'], goal_state)
            child['path_cost'] = node['path_cost'] + step_cost
            if child['STATE'] not in explored and child['STATE'] not in frontier_dict:
                heapq.heappush(frontier, (child['path_cost'], random.random(), child))
                frontier_dict[child['STATE']] = child['path_cost']
            elif child['STATE'] in frontier_dict and child['path_cost'] < frontier_dict[child['STATE']]:
                heapq.heappush(frontier, (child['path_cost'], random.random(), child))
                frontier_dict[child['STATE']] = child['path_cost']
                
        explore_log.append({
            'node': node,
            'frontier_list': list(frontier_dict.items()),
            'explored_list': list(explored.keys())
        })
    return None, explore_log

def GREEDY_SEARCH(initial_state, goal_state):
    """Tìm kiếm tham lam (Greedy Best-First Search) - Đánh giá thuần túy bằng h(n)."""
    explore_log = []
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(initial_state, goal_state)}
    start_node['path_cost'] = start_node['h']
    FRONTIER = [start_node]
    REACHED = {}
    
    while FRONTIER:
        min_idx = 0
        for i in range(1, len(FRONTIER)):
            if FRONTIER[i]['h'] < FRONTIER[min_idx]['h']:
                min_idx = i
        n = FRONTIER.pop(min_idx)
        
        if n['STATE'] == goal_state:
            explore_log.append({
                'node': n,
                'frontier_list': sorted([(item['STATE'], item['h']) for item in FRONTIER], key=lambda x: x[1]),
                'explored_list': list(REACHED.keys())
            })
            return SOLUTION(n), explore_log
            
        REACHED[n['STATE']] = n
        
        for action in ACTIONS(n['STATE']):
            child = CHILD_NODE(n['STATE'], n, action)
            m_state = child['STATE']
            if not any(item['STATE'] == m_state for item in FRONTIER) and m_state not in REACHED:
                child['h'] = MANHATTAN_DISTANCE(m_state, goal_state)
                child['path_cost'] = child['h']
                FRONTIER.append(child)
                
        explore_log.append({
            'node': n,
            'frontier_list': sorted([(item['STATE'], item['h']) for item in FRONTIER], key=lambda x: x[1]),
            'explored_list': list(REACHED.keys())
        })
    return None, explore_log

def A_STAR_SEARCH(initial_state, goal_state):
    """Tìm kiếm A* - Kết hợp chi phí đường đi g(n) và hàm ước lượng h(n)."""
    explore_log = []
    h_start = MANHATTAN_DISTANCE(initial_state, goal_state)
    start_node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'g': 0, 'h': h_start, 'f': h_start}
    start_node['path_cost'] = start_node['f']
    FRONTIER = [start_node]
    REACHED = {}
    
    while FRONTIER:
        min_idx = 0
        for i in range(1, len(FRONTIER)):
            if FRONTIER[i]['f'] < FRONTIER[min_idx]['f']:
                min_idx = i
        n = FRONTIER.pop(min_idx)
        
        if n['STATE'] == goal_state:
            explore_log.append({
                'node': n,
                'frontier_list': sorted([(item['STATE'], item['f']) for item in FRONTIER], key=lambda x: x[1]),
                'explored_list': list(REACHED.keys())
            })
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
                
        explore_log.append({
            'node': n,
            'frontier_list': sorted([(item['STATE'], item['f']) for item in FRONTIER], key=lambda x: x[1]),
            'explored_list': list(REACHED.keys())
        })
    return None, explore_log

def IDA_STAR_DFS(node, goal_state, threshold, explore_log, visited):
    """Hàm đệ quy hỗ trợ cho thuật toán IDA*."""
    h = MANHATTAN_DISTANCE(node['STATE'], goal_state)
    g = node['depth']
    f = g + h
    node['g'], node['h'], node['f'], node['path_cost'], node['threshold'] = g, h, f, f, threshold

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
            
        child_h = MANHATTAN_DISTANCE(child['STATE'], goal_state)
        frontier_snapshot.append((child['STATE'], child['depth'] + child_h))
        
        explore_log.append({
            'node': node,
            'frontier_list': sorted(frontier_snapshot.copy(), key=lambda x: x[1]),
            'explored_list': list(visited)
        })
        
        result = IDA_STAR_DFS(child, goal_state, threshold, explore_log, visited)
        if isinstance(result, dict): return result
        minimum = min(minimum, result)
        
    visited.remove(node['STATE'])
    return minimum

def IDA_STAR_SEARCH(initial_state, goal_state):
    """Tìm kiếm A* sâu dần (IDA*) - Tiết kiệm tối đa bộ nhớ lưu trữ các Node."""
    explore_log = []
    start = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    threshold = MANHATTAN_DISTANCE(initial_state, goal_state)
    
    while True:
        visited = set()
        explore_log.clear() 
        result = IDA_STAR_DFS(start, goal_state, threshold, explore_log, visited)
        if isinstance(result, dict): return SOLUTION(result), explore_log
        if result == float('inf'): return None, explore_log
        threshold = result

def SIMPLE_HILL_CLIMBING(initial_state, goal_state):
    """
    Leo đồi cơ bản (Simple Hill Climbing).
    Logic chọn: Khảo sát tuần tự, chấp nhận trạng thái đầu tiên có h(n) TỐT HƠN HOẶC BẰNG (<=).
    Trực quan: Reached hiển thị chính xác lộ trình các node đã chọn di chuyển qua.
    """
    explore_log = []
    current = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    current['h'] = MANHATTAN_DISTANCE(initial_state, goal_state)
    current['path_cost'] = current['h']
    
    trajectory = []
    max_steps = 200
    step_count = 0
    
    while step_count < max_steps:
        trajectory.append(f"Bước {len(trajectory)}: {current['STATE']} [h={current['h']}]")
        
        if current['STATE'] == goal_state:
            explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
            return SOLUTION(current), explore_log
            
        neighbors_vis = []
        improved = False
        next_node = None
        
        for action in ACTIONS(current['STATE']):
            if not improved:
                child = CHILD_NODE(current['STATE'], current, action)
                child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
                child['path_cost'] = child['h']
                
                if child['h'] <= current['h']:
                    neighbors_vis.append((child['STATE'], child['h'], "-> CHỌN (<= Hiện tại)"))
                    next_node = child
                    improved = True
                else:
                    neighbors_vis.append((child['STATE'], child['h'], "Kém hơn (Bỏ qua)"))
            else:
                neighbors_vis.append(("<Chưa sinh>", "?", "Bỏ qua vì đã chốt sớm"))
                
        explore_log.append({
            'node': current,
            'frontier_list': neighbors_vis,
            'explored_list': list(trajectory)
        })
        
        if not improved: break
        current = next_node
        step_count += 1
        
    return SOLUTION(current), explore_log

def STEEPEST_ASCENT_HILL_CLIMBING(initial_state, goal_state):
    """
    Leo đồi dốc nhất (Steepest-Ascent Hill Climbing).
    Logic chọn: Sinh tất cả lân cận, chọn lân cận TỐT NHẤT trong tập nếu nó TỐT HƠN HOẶC BẰNG (<=).
    """
    explore_log = []
    current = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    current['h'] = MANHATTAN_DISTANCE(initial_state, goal_state)
    current['path_cost'] = current['h']
    
    trajectory = []
    max_steps = 200
    step_count = 0
    
    while step_count < max_steps:
        trajectory.append(f"Bước {len(trajectory)}: {current['STATE']} [h={current['h']}]")
        
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
        neighbors_vis = []
        next_node = None
        chosen = False
        
        for child in children:
            if child['h'] == min_child_h and min_child_h <= current['h'] and not chosen:
                next_node = child
                neighbors_vis.append((child['STATE'], child['h'], "-> CHỌN (Dốc nhất & <= Hiện tại)"))
                chosen = True
            else:
                neighbors_vis.append((child['STATE'], child['h'], "Không tối ưu bằng"))
                
        explore_log.append({
            'node': current,
            'frontier_list': neighbors_vis,
            'explored_list': list(trajectory)
        })
        
        if next_node is None: break
        current = next_node
        step_count += 1
        
    return SOLUTION(current), explore_log

def Stochastic_Hill_Climbing(Start, goal_state):
    """
    Leo đồi ngẫu nhiên (Stochastic Hill Climbing).
    Logic chọn: Chọn ngẫu nhiên một trạng thái từ tập các lân cận TỐT HƠN HOẶC BẰNG (<=).
    """
    explore_log = []
    start_node = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
    start_node['path_cost'] = start_node['h']
    current = start_node
    
    trajectory = []
    max_steps = 200
    step_count = 0
    
    while step_count < max_steps:
        trajectory.append(f"Bước {len(trajectory)}: {current['STATE']} [h={current['h']}]")
        
        if current['STATE'] == goal_state:
            explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
            return SOLUTION(current), explore_log
            
        all_children = []
        better_or_equal = []
        
        for action in ACTIONS(current['STATE']):
            child = CHILD_NODE(current['STATE'], current, action)
            child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
            child['path_cost'] = child['h']
            all_children.append(child)
            if child['h'] <= current['h']:
                better_or_equal.append(child)
                
        if not better_or_equal:
            frontier_vis = [(c['STATE'], c['h'], "Kém hơn") for c in all_children]
            explore_log.append({'node': current, 'frontier_list': frontier_vis, 'explored_list': list(trajectory)})
            break
            
        next_node = random.choice(better_or_equal)
        frontier_vis = []
        for child in all_children:
            if child == next_node:
                frontier_vis.append((child['STATE'], child['h'], "-> CHỌN NGẪU NHIÊN"))
            elif child in better_or_equal:
                frontier_vis.append((child['STATE'], child['h'], "Hợp lệ (<= Hiện tại)"))
            else:
                frontier_vis.append((child['STATE'], child['h'], "Kém hơn"))
                
        explore_log.append({
            'node': current,
            'frontier_list': frontier_vis,
            'explored_list': list(trajectory)
        })
        
        current = next_node
        step_count += 1
        
    return SOLUTION(current), explore_log

def Random_Restart_Hill_Climbing(Start, goal_state):
    """
    Leo đồi khởi chạy lại ngẫu nhiên (Random Restart Hill Climbing).
    Chạy lặp Stochastic Hill Climbing, nếu kẹt thì ghi nhận Best-Node rồi Restart từ đầu.
    """
    explore_log = []
    MAX_RESTART = 15
    global_best_node = None
    trajectory = []
    
    for i in range(1, MAX_RESTART + 1):
        current = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
        current['path_cost'] = current['h']
        
        trajectory.append(f"--- LƯỢT RESTART THỨ {i} ---")
        step_count = 0
        
        while step_count < 50:
            trajectory.append(f"R{i}-STT {step_count}: {current['STATE']} [h={current['h']}]")
            
            if current['STATE'] == goal_state:
                explore_log.append({'node': current, 'frontier_list': [], 'explored_list': list(trajectory)})
                return SOLUTION(current), explore_log
                
            all_children = []
            better_or_equal = []
            
            for action in ACTIONS(current['STATE']):
                child = CHILD_NODE(current['STATE'], current, action)
                child['h'] = MANHATTAN_DISTANCE(child['STATE'], goal_state)
                child['path_cost'] = child['h']
                all_children.append(child)
                if child['h'] <= current['h']:
                    better_or_equal.append(child)
                    
            if not better_or_equal:
                frontier_vis = [(c['STATE'], c['h'], "Kém hơn") for c in all_children]
                explore_log.append({'node': current, 'frontier_list': frontier_vis, 'explored_list': list(trajectory)})
                if global_best_node is None or current['h'] < global_best_node['h']:
                    global_best_node = current
                break
                
            next_node = random.choice(better_or_equal)
            frontier_vis = []
            for child in all_children:
                if child == next_node:
                    frontier_vis.append((child['STATE'], child['h'], "-> CHỌN NGẪU NHIÊN"))
                elif child in better_or_equal:
                    frontier_vis.append((child['STATE'], child['h'], "Hợp lệ"))
                else:
                    frontier_vis.append((child['STATE'], child['h'], "Kém hơn"))
                    
            explore_log.append({
                'node': current,
                'frontier_list': frontier_vis,
                'explored_list': list(trajectory)
            })
            current = next_node
            step_count += 1
            
    return None, explore_log 

def Local_Beam_Search(Start, goal_state, k=2):
    """
    Tìm kiếm chùm cục bộ (Local Beam Search).
    Trực quan: Reached lưu giữ thông tin chính xác của K trạng thái tạo thành chùm (Beam) hiện tại.
    Logic dừng: Khi Node tốt nhất thế hệ sau tệ hơn Node tốt nhất chùm cũ.
    """
    explore_log = []
    start_node = {'STATE': Start, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(Start, goal_state)}
    start_node['path_cost'] = start_node['h']
    
    Current_State_set = [start_node]
    attempts = 0
    while len(Current_State_set) < k and attempts < 100:
        attempts += 1
        curr_state = Start
        for _ in range(random.randint(1, 4)):
            acts = ACTIONS(curr_state)
            if acts:
                temp_node = CHILD_NODE(curr_state, None, acts[0])
                curr_state = temp_node['STATE']
        if not any(n['STATE'] == curr_state for n in Current_State_set):
            node = {'STATE': curr_state, 'parent': None, 'action': None, 'depth': 0, 'h': MANHATTAN_DISTANCE(curr_state, goal_state)}
            node['path_cost'] = node['h']
            Current_State_set.append(node)
            
    max_iter = 100
    for step in range(max_iter):
        beam_vis = [f"Chùm hiện tại (bước {step}):"]
        for i, n in enumerate(Current_State_set):
            beam_vis.append(f" T.Viên {i+1}: {n['STATE']} [h={n['h']}]")
            
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
                frontier_vis = [(n['STATE'], n['h'], "ĐÍCH!") for n in Neighbor_States[:k+2]]
                explore_log.append({'node': Neighbor, 'frontier_list': frontier_vis, 'explored_list': beam_vis})
                return SOLUTION(Neighbor), explore_log
                
        if Neighbor_States[0]['h'] > Current_State_set[0]['h']:
            frontier_vis = [(n['STATE'], n['h'], "Tệ hơn chùm cũ (Hủy)") for n in Neighbor_States[:k+3]]
            explore_log.append({'node': Current_State_set[0], 'frontier_list': frontier_vis, 'explored_list': beam_vis})
            break
            
        Next_State_set = Neighbor_States[:k]
        frontier_vis = []
        for i, n in enumerate(Neighbor_States):
            if i < k:
                frontier_vis.append((n['STATE'], n['h'], "-> CHỌN (Vào top k)"))
            elif i < k + 4:
                frontier_vis.append((n['STATE'], n['h'], "Bị loại khỏi chùm"))
                
        explore_log.append({
            'node': Current_State_set[0],
            'frontier_list': frontier_vis,
            'explored_list': beam_vis
        })
        Current_State_set = Next_State_set
        
    return None, explore_log

def Simulated_Annealing(start, goal):
    """
    Thuật toán Mô phỏng luyện kim (Simulated Annealing).
    Đặt tên biến và cấu trúc logic bám sát 100% theo ảnh Pseudocode yêu cầu.
    Sử dụng khoảng cách Manhattan làm hàm Heuristic đánh giá.
    """
    import math  # Cần thiết để tính hàm mũ ngẫu nhiên exp(-Δ/T)
    explore_log = []
    
    # Khởi tạo các tham số nhiệt độ ban đầu theo đặc tả giải thuật
    T0 = 100.0      # Nhiệt độ bắt đầu
    Tmin = 0.01     # Nhiệt độ ngưỡng dừng
    alpha = 0.95    # Hệ số làm mát hình học (Cooling rate α)

    # current_state = start
    current_state = {
        'STATE': start, 
        'parent': None, 
        'action': None, 
        'depth': 0
    }
    current_state['h'] = MANHATTAN_DISTANCE(start, goal)
    current_state['path_cost'] = current_state['h']

    T = T0
    trajectory = []  # Lưu lại quỹ đạo các trạng thái đã đi qua để hiển thị Reached List
    max_steps = 2000 # Giới hạn vòng lặp an toàn tránh treo UI
    steps = 0

    # while T > Tmin:
    while T > Tmin and steps < max_steps:
        trajectory.append(f"T={T:.2f}: {current_state['STATE']} [h={current_state['h']}]")
        
        # if current_state == goal: return current_state
        if current_state['STATE'] == goal:
            explore_log.append({
                'node': current_state, 
                'frontier_list': ["Đã tìm thấy đích tại mức nhiệt này!"], 
                'explored_list': list(trajectory)
            })
            # Hàm SOLUTION() có sẵn trong file của bạn sẽ tự truy vết ngược đường đi
            # Tuy nhiên, do SA có thể nhảy ngẫu nhiên, ta trả về danh sách các Node liên tục
            return SOLUTION(current_state), explore_log
            
        # next_state = RandomNeighbor(current_state)
        actions = ACTIONS(current_state['STATE'])
        random_action = random.choice(actions) # Chọn ngẫu nhiên một hành động lân cận
        next_state = CHILD_NODE(current_state['STATE'], current_state, random_action)
        next_state['h'] = MANHATTAN_DISTANCE(next_state['STATE'], goal)
        next_state['path_cost'] = next_state['h']
        
        # Delta = h(next_state) - h(current_state)
        # Vì bài toán tìm kiếm đường đi hướng tới cực tiểu hóa h(n),
        # nên Delta < 0 tức là trạng thái tiếp theo tốt hơn (năng lượng thấp hơn).
        Delta = next_state['h'] - current_state['h']
        
        accepted = False
        # if Delta < 0: current_state = next_state
        if Delta < 0:
            current_state = next_state
            accepted = True
        else:
            # else: p = exp(-Delta / T)
            p = math.exp(-Delta / T)
            # if Random(0,1) < p: current_state = next_state
            if random.random() < p:
                current_state = next_state
                accepted = True

        # Ghi log chi tiết để đồng bộ hiển thị lên hai danh sách Frontier và Reached của UI
        log_msg = "Chấp nhận (Tốt hơn)" if Delta < 0 else (f"Chấp nhận ngẫu nhiên (p={p:.3f})" if accepted else f"Từ chối (p={p:.3f})")
        frontier_vis = [f"Neighbor thử nghiệm: {next_state['STATE']} | h={next_state['h']} -> {log_msg}"]
        
        explore_log.append({
            'node': current_state,
            'frontier_list': frontier_vis,
            'explored_list': list(trajectory)[-40:]  # Chỉ giữ 40 dòng gần nhất để UI chạy mượt mà
        })
        
        # T = alpha * T (Làm mát nhiệt độ sau mỗi bước lặp)
        T = alpha * T
        steps += 1
        
    # Trả về kết quả cuối cùng dù đạt đích hay dừng do cạn nhiệt độ
    explore_log.append({'node': current_state, 'frontier_list': ["Hết nhiệt độ dừng lặp!"], 'explored_list': list(trajectory)})
    if current_state['STATE'] == goal:
        return SOLUTION(current_state), explore_log
    return None, explore_log

def SENSORLESS_APPLY_ACTION(state, action):
    """
    Hàm phụ trợ cho bài toán Sensorless (Không nhìn thấy trạng thái):
    Mô phỏng hành động tác động lên một trạng thái ẩn. Nếu hành động đập vào tường
    (ví dụ ô trống ở dòng 0 mà chọn UP), trạng thái sẽ không thay đổi nhưng hành động vẫn thực thi.
    """
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    swap_idx = -1
    
    if action == 'UP' and row > 0: swap_idx = (row - 1) * 3 + col
    elif action == 'DOWN' and row < 2: swap_idx = (row + 1) * 3 + col
    elif action == 'LEFT' and col > 0: swap_idx = row * 3 + (col - 1)
    elif action == 'RIGHT' and col < 2: swap_idx = row * 3 + (col + 1)
    
    if swap_idx == -1: 
        return state  # Đụng tường -> Đứng im tại chỗ
        
    new_state = list(state)
    new_state[idx], new_state[swap_idx] = new_state[swap_idx], new_state[idx]
    return tuple(new_state)


def Sensorless_Conformant_A_Star(start_state, goal_state):
    """
    Thuật toán đại diện cho lớp Không nhìn thấy trạng thái ban đầu (Sensorless / Unobservable).
    Xây dựng Belief State (Tập niềm tin) chứa >= 2 trạng thái ban đầu.
    Áp dụng thuật toán A* Search để tìm chuỗi hành động ép buộc (Conformant) đưa mọi khả năng về đích.
    
    *Lưu ý lập trình viên: Nếu lấy toàn bộ không gian 9! (362,880 trạng thái) làm tập ban đầu, 
    máy tính sẽ bị tràn bộ nhớ RAM ngay lập tức. Để UI hoạt động và hiển thị được cơ chế "gom tụ" (coalescence),
    thuật toán này khởi tạo Belief State gồm trạng thái gốc và các biến thể xáo trộn ngẫu nhiên liền kề.
    """
    explore_log = []
    
    # 1. KHỞI TẠO TẬP NIỀM TIN BAN ĐẦU (Belief State chứa >= 2 trạng thái)
    # Lấy trạng thái hiện tại làm gốc, sau đó dịch chuyển ngẫu nhiên để tạo thêm các trạng thái nhiễu ẩn.
    belief_set = {start_state}
    temp_state = start_state
    for _ in range(2): 
        valid_moves = ACTIONS(temp_state)
        temp_state = SENSORLESS_APPLY_ACTION(temp_state, random.choice(valid_moves))
        belief_set.add(temp_state)
    
    # Chuyển đổi sang tuple được sắp xếp để tạo thuộc tính băm duy nhất (Hashable) quản lý tập hợp trong Python
    initial_belief = tuple(sorted(list(belief_set)))
    
    # Hàm Heuristic tính toán trên một Belief State: Lấy giá trị Manhattan lớn nhất trong tập làm đại diện
    def BELIEF_HEURISTIC(b_state):
        return max(MANHATTAN_DISTANCE(s, goal_state) for s in b_state)

    h_start = BELIEF_HEURISTIC(initial_belief)
    
    # Cấu trúc Node đặc biệt cho không gian Belief State
    # Gán trường 'STATE' bằng phần tử đầu tiên để đánh lừa bộ dựng Grid của UI cũ không bị lỗi Crash dữ liệu.
    start_node = {
        'BELIEF_STATE': initial_belief, 
        'STATE': initial_belief[0], 
        'parent': None, 
        'action': None, 
        'depth': 0, 
        'g': 0, 
        'h': h_start, 
        'f': h_start
    }
    start_node['path_cost'] = start_node['f']
    
    FRONTIER = [start_node]
    REACHED = {}

    while FRONTIER:
        # Chọn lựa Node có hàm đánh giá f tổng hợp thấp nhất (A* Search chiến lược)
        min_idx = min(range(len(FRONTIER)), key=lambda i: FRONTIER[i]['f'])
        n = FRONTIER.pop(min_idx)
        
        # ĐIỀU KIỆN ĐÍCH: Tập niềm tin co cụm lại chỉ còn DUY NHẤT 1 trạng thái và trạng thái đó trùng khớp với Goal
        if len(n['BELIEF_STATE']) == 1 and n['BELIEF_STATE'][0] == goal_state:
            explore_log.append({
                'node': n, 
                'frontier_list': ["Hội tụ thành công! Trạng thái đích đã được xác định duy nhất."], 
                'explored_list': [f"Kích thước Belief cuối cùng: {len(n['BELIEF_STATE'])}"]
            })
            return SOLUTION(n), explore_log
            
        REACHED[n['BELIEF_STATE']] = n
        
        # Vì tác nhân bị mù (Sensorless), nó chỉ có thể thử nghiệm đập mù quáng cả 4 hướng cơ bản 
        all_possible_blind_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        for action in all_possible_blind_actions:
            # Ứng với mỗi hành động, TẤT CẢ các trạng thái giả định trong tập Belief đồng loạt dịch chuyển
            new_belief_set = set()
            for s in n['BELIEF_STATE']:
                new_belief_set.add(SENSORLESS_APPLY_ACTION(s, action))
            
            child_belief = tuple(sorted(list(new_belief_set)))
            g_new = n['g'] + 1
            
            # Kiểm tra xem tổ hợp tập niềm tin này từng xuất hiện trong hàng đợi chưa
            frontier_idx = next((i for i, item in enumerate(FRONTIER) if item['BELIEF_STATE'] == child_belief), None)
            
            child_node = {
                'BELIEF_STATE': child_belief, 
                'STATE': child_belief[0], 
                'parent': n, 
                'action': action, 
                'depth': n['depth'] + 1,
                'g': g_new, 
                'h': BELIEF_HEURISTIC(child_belief)
            }
            child_node['f'] = child_node['g'] + child_node['h']
            child_node['path_cost'] = child_node['f']
            
            if child_belief in REACHED:
                if g_new < REACHED[child_belief]['g']:
                    del REACHED[child_belief]
                    FRONTIER.append(child_node)
            elif frontier_idx is not None:
                if g_new < FRONTIER[frontier_idx]['g']:
                    FRONTIER[frontier_idx] = child_node
            else:
                FRONTIER.append(child_node)
                
        # Cập nhật danh sách hiển thị tiến trình biến đổi của cấu trúc tập niềm tin lên UI panel
        f_vis = [f"Belief hiện tại có {len(item['BELIEF_STATE'])} trạng thái | f(n)={item['f']} qua h.động [{item['action']}]" for item in FRONTIER]
        e_vis = [f"Đã duyệt tập Belief kích thước: {len(k)} phần tử" for k in REACHED.keys()]
        
        explore_log.append({
            'node': n,
            'frontier_list': f_vis,
            'explored_list': e_vis[-40:]
        })
        
        # Điểm ngắt an toàn đề phòng không gian tìm kiếm bùng nổ quá sâu khi thử nghiệm
        if n['depth'] > 40: 
            break
            
    return None, explore_log

# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Professional Edition")
        self.root.geometry("1050x720")
        self.root.minsize(900, 600)
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
        
        self.algo_cb = ttk.Combobox(ctrl_grid, textvariable=self.algo_var, 
                                    values=["BFS", "DFS", "IDS", "UCS", "Greedy_Search", "A*", "IDA*", 
                                            "Simple_Hill_Climbing", "Steepest_Ascent_Hill_Climbing", 
                                            "Stochastic_Hill_Climbing", "Random_Restart_Hill_Climbing", 
                                            "Local_Beam_Search", "Simulated_Annealing", "Sensorless_Conformant_A*"],
                                    state="readonly", width=30, font=('Consolas', 11))
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
        tk.Label(frontier_frame, text="FRONTIER / NEIGHBORS (Hàng đợi / Lân cận)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        f_list_container = tk.Frame(frontier_frame, bg='white', bd=1, relief='solid')
        f_list_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.list_frontier = tk.Listbox(f_list_container, **list_opts)
        scroll_f = tk.Scrollbar(f_list_container, command=self.list_frontier.yview, bd=1, bg='white')
        self.list_frontier.config(yscrollcommand=scroll_f.set)
        self.list_frontier.pack(side='left', fill='both', expand=True, padx=2, pady=2)
        scroll_f.pack(side='right', fill='y')

        explored_frame = tk.Frame(right_col, bg='white', bd=1, relief='solid')
        explored_frame.pack(side='right', fill='both', expand=True, padx=(0, 0))
        tk.Label(explored_frame, text="REACHED / CHÙM TRẠNG THÁI (Đã duyệt)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        e_list_container = tk.Frame(explored_frame, bg='white', bd=1, relief='solid')
        e_list_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.list_explored = tk.Listbox(e_list_container, **list_opts)
        scroll_e = tk.Scrollbar(e_list_container, command=self.list_explored.yview, bd=1, bg='white')
        self.list_explored.config(yscrollcommand=scroll_e.set)
        self.list_explored.pack(side='left', fill='both', expand=True, padx=2, pady=2)
        scroll_e.pack(side='right', fill='y')
        
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

    def _read_grid(self, cells):
        try:
            res = [int(c.get().strip()) for r in cells for c in r]
            if sorted(res) != list(range(9)): raise ValueError
            return tuple(res)
        except:
            return None

    def _toggle_depth_visibility(self, event=None):
        algo = self.algo_var.get()
        if algo in ['DFS', 'IDS']:
            self.depth_title_lbl.grid()
            self.depth_ctrl_frame.grid()
        else:
            self.depth_title_lbl.grid_remove()
            self.depth_ctrl_frame.grid_remove()

    def _solve(self):
        self._stop_play()
        init = self._read_grid(self.init_cells)
        goal = self._read_grid(self.goal_cells)
        
        if not init or not goal: 
            messagebox.showerror("Lỗi", "Vui lòng nhập đủ các số từ 0 đến 8 không trùng lặp.")
            return
            
        self.target_goal = goal
        algo = self.algo_var.get()
        m_depth = self.max_depth_var.get()

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

        self.solution_path = sol if sol else []
        self.explore_log = log
        self.current_step = 0
        
        self._draw_solution_canvas()

        for b in [self.btn_prev, self.btn_play, self.btn_next]:
            b.config(state='normal' if log else 'disabled')
            
        self._refresh_display()
        
        if sol is None:
            msg = f"THUẬT TOÁN THẤT BẠI!\n\n- Thuật toán: {algo}\n- Không thể tìm thấy đích."
            messagebox.showwarning("Không tìm thấy đường", msg)
        else:
            final_state = sol[-1]['STATE']
            if final_state != self.target_goal and algo not in ['Sensorless_Conformant_A*']:
                msg = f"THUẬT TOÁN BỊ KẸT CỰC ĐẠI CỤC BỘ!\n\n- Thuật toán: {algo}\n- Đã dừng tại bước kẹt để khảo sát."
                messagebox.showwarning("Cực đại cục bộ", msg)
            else:
                msg = f"GIẢI THÀNH CÔNG!\n\n- Thuật toán: {algo}\n- Độ dài đường đi: {len(sol)-1} bước"
                messagebox.showinfo("Thống kê", msg)

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
                    bg_color = '#90EE90' if (val == self.target_goal[row*3+col] and val != 0) else 'white'
                    if i == len(self.solution_path)-1 and state != self.target_goal: bg_color = '#FFCCCB'
                    
                    self.sol_canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline='black')
                    if val != 0:
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
        
        for i in range(3):
            for j in range(3):
                val = state[i*3+j]
                bg_color = '#90EE90' if (val == self.target_goal[i*3+j] and val != 0) else 'white'
                self.board_labels[i][j].config(text=str(val) if val else "", bg=bg_color)
                
        self.info_step_lbl.config(text=f"Step Log: {self.current_step + 1} / {len(self.explore_log)}")
        
        algo = self.algo_var.get()
        if algo in ['Greedy_Search', 'Simple_Hill_Climbing', 'Steepest_Ascent_Hill_Climbing', 
                    'Stochastic_Hill_Climbing', 'Random_Restart_Hill_Climbing', 'Local_Beam_Search', 'Simulated_Annealing']:
            self.info_cost_lbl.config(text=f"Heuristic h(n) = Manhattan: {current_node.get('h', 0)}")
            self.info_depth_lbl.config(text=f"Depth: {current_node['depth']}")
        elif algo in ['A*', 'IDA*', 'Sensorless_Conformant_A*']:
            self.info_cost_lbl.config(text=f"f(n) = g+h: {current_node.get('f', 0)} (g={current_node.get('g', 0)}, h={current_node.get('h', 0)})")
            self.info_depth_lbl.config(text=f"Depth: {current_node['depth']}")
        else:
            self.info_cost_lbl.config(text=f"Path-Cost: {current_node['path_cost']}")
            self.info_depth_lbl.config(text=f"Depth: {current_node['depth']}")
            
        self.info_nodes_lbl.config(text=f"List Records: Frontier={len(step_data['frontier_list'])} / Reached={len(step_data['explored_list'])}")

        self.list_frontier.delete(0, tk.END)
        for idx, item in enumerate(step_data['frontier_list'], 1):
            if isinstance(item, tuple):
                if len(item) == 3:
                    s, score, note = item
                    self.list_frontier.insert(tk.END, f" {idx:02d}. {s} [h={score}] : {note}")
                elif len(item) == 2:
                    s, score = item
                    label_char = 'h' if algo == 'Greedy_Search' else ('f' if algo in ['A*', 'IDA*', 'Sensorless_Conformant_A*'] else 'Cost')
                    self.list_frontier.insert(tk.END, f" {idx:02d}. {s} [{label_char}={score}]")
            else:
                self.list_frontier.insert(tk.END, f" {idx:02d}. {item}")
            
        self.list_explored.delete(0, tk.END)
        for idx, s in enumerate(step_data['explored_list'], 1):
            self.list_explored.insert(tk.END, f" {s}")

    def _go_prev(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._refresh_display()

    def _go_next(self):
        if self.current_step < len(self.explore_log) - 1:
            self.current_step += 1
            self._refresh_display()

    def _toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.config(text="Stop" if self.is_playing else "Play")
        if self.is_playing: self._auto_run()

    def _auto_run(self):
        if not self.is_playing: return
        if self.current_step < len(self.explore_log) - 1:
            self._go_next()
            self.play_job = self.root.after(self.speed_var.get(), self._auto_run)
        else:
            self._stop_play()

    def _stop_play(self):
        self.is_playing = False
        self.btn_play.config(text="Play")
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None

if __name__ == '__main__':
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()