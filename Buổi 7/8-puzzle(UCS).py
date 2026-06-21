import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import heapq

# ═══════════════════════════════════════════════════════════════
#  ALGORITHM & HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def ACTIONS(state):
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
    path = []
    while node is not None:
        path.append(node)
        node = node['parent']
    return list(reversed(path))

def MISPLACED_TILES(state, goal):
    return sum(1 for i in range(9) if state[i] != goal[i])

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

def DEPTH_LIMITED_SEARCH(initial_state, goal_state, limit, explore_log):
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0, 'path_cost': 0}
    return _RECURSIVE_DLS(node, goal_state, limit, explore_log, {}, [])

def _RECURSIVE_DLS(node, goal_state, limit, explore_log, visited, current_frontier):
    if node['STATE'] == goal_state:
        explore_log.append({
            'node': node,
            'frontier_list': list(current_frontier),
            'explored_list': list(visited.keys())
        })
        return SOLUTION(node)
    if node['depth'] >= limit: return 'cutoff'
        
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
    explore_log = []
    for depth in range(max_depth + 1):
        result = DEPTH_LIMITED_SEARCH(initial_state, goal_state, depth, explore_log)
        if result != 'cutoff': 
            return result, explore_log
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


# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver OCD Edition")

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
        # [TẦNG 1] KHUNG ĐIỀU KHIỂN TRÊN CÙNG 
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
        
        self.algo_cb = ttk.Combobox(ctrl_grid, textvariable=self.algo_var, values=["BFS", "DFS", "IDS", "UCS"], 
                                    state="readonly", width=8, font=('Consolas', 11))
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

        # [TẦNG 2] BĂNG CHUYỀN HIỂN THỊ ĐƯỜNG ĐI ĐẾN ĐÍCH TRỰC QUAN (Canvas 3x3)
        solution_frame = tk.Frame(self.root, bg='white', bd=1, relief='solid')
        solution_frame.pack(fill='x', padx=10, pady=(0, 10))
        tk.Label(solution_frame, text="ĐƯỜNG ĐI ĐẾN GOAL (SOLUTION PATH)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        
        canvas_container = tk.Frame(solution_frame, bg='white')
        canvas_container.pack(fill='x', padx=5, pady=5)
        
        self.sol_canvas = tk.Canvas(canvas_container, bg='#fafafa', height=120, highlightthickness=0)
        self.sol_scrollbar = tk.Scrollbar(canvas_container, orient="horizontal", command=self.sol_canvas.xview)
        self.sol_canvas.configure(xscrollcommand=self.sol_scrollbar.set)
        
        self.sol_canvas.pack(side="top", fill="x", expand=True)
        self.sol_scrollbar.pack(side="bottom", fill="x")

        # [TẦNG 3] MAIN BODY: NODE TỪ FRONTIER & LOG SEARCH
        main_body = tk.Frame(self.root, bg='white')
        main_body.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Cột Trái: Trạng thái Bàn cờ đang xét (Node từ Frontier)
        left_col = tk.Frame(main_body, bg='white', bd=1, relief='solid', width=320)
        left_col.pack(side='left', fill='y', padx=(0, 5))
        left_col.pack_propagate(False)

        tk.Label(left_col, text="NODE LẤY RA TỪ FRONTIER", bg='white', font=('Consolas', 10, 'bold')).pack(pady=10)
        
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

        # Nút điều hướng
        ctrl_frame2 = tk.Frame(left_col, bg='white')
        ctrl_frame2.pack(pady=10)
        btn_opts = {'bg': 'white', 'activebackground': '#f0f0f0', 'bd': 1, 'relief': 'solid', 'width': 8, 'font': ('Consolas', 10)}
        self.btn_prev = tk.Button(ctrl_frame2, text="Prev", command=self._go_prev, state='disabled', **btn_opts)
        self.btn_prev.pack(side='left', padx=5)
        self.btn_play = tk.Button(ctrl_frame2, text="Play", command=self._toggle_play, state='disabled', **btn_opts)
        self.btn_play.pack(side='left', padx=5)
        self.btn_next = tk.Button(ctrl_frame2, text="Next", command=self._go_next, state='disabled', **btn_opts)
        self.btn_next.pack(side='left', padx=5)

        # Thông số 
        info_frame = tk.Frame(left_col, bg='white', bd=1, relief='solid')
        info_frame.pack(pady=10, fill='x', padx=10)
        lbl_opts = {'bg': 'white', 'font': ('Consolas', 10)}
        
        self.info_step_lbl = tk.Label(info_frame, text="Step: 0 / 0", **lbl_opts)
        self.info_step_lbl.grid(row=0, column=0, sticky='w', padx=15, pady=3)
        
        self.info_cost_lbl = tk.Label(info_frame, text="Path-Cost: 0", **lbl_opts)
        self.info_cost_lbl.grid(row=1, column=0, sticky='w', padx=15, pady=3)
        
        self.info_depth_lbl = tk.Label(info_frame, text="Depth: 0", **lbl_opts)
        self.info_depth_lbl.grid(row=2, column=0, sticky='w', padx=15, pady=3)
        
        self.info_nodes_lbl = tk.Label(info_frame, text="Nodes Generated: 0", **lbl_opts)
        self.info_nodes_lbl.grid(row=3, column=0, sticky='w', padx=15, pady=3)

        # Cột Phải: Danh sách Frontier & Explored
        right_col = tk.Frame(main_body, bg='white')
        right_col.pack(side='left', fill='both', expand=True)
        list_opts = {'bg': '#fafafa', 'fg': 'black', 'bd': 0, 'highlightthickness': 0, 
                    'font': ('Consolas', 10), 'selectbackground': '#d9d9d9', 'selectforeground': 'black'}

        # Khung Frontier
        frontier_frame = tk.Frame(right_col, bg='white', bd=1, relief='solid')
        frontier_frame.pack(side='left', fill='both', expand=True, padx=(5, 5))
        tk.Label(frontier_frame, text="FRONTIER (Hàng đợi/Ngăn xếp)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
        f_list_container = tk.Frame(frontier_frame, bg='white', bd=1, relief='solid')
        f_list_container.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        self.list_frontier = tk.Listbox(f_list_container, **list_opts)
        scroll_f = tk.Scrollbar(f_list_container, command=self.list_frontier.yview, bd=1, bg='white')
        self.list_frontier.config(yscrollcommand=scroll_f.set)
        self.list_frontier.pack(side='left', fill='both', expand=True, padx=2, pady=2)
        scroll_f.pack(side='right', fill='y')

        # Khung Explored
        explored_frame = tk.Frame(right_col, bg='white', bd=1, relief='solid')
        explored_frame.pack(side='right', fill='both', expand=True, padx=(0, 0))
        tk.Label(explored_frame, text="EXPLORED (Theo thứ tự xét)", bg='white', font=('Consolas', 10, 'bold')).pack(pady=5)
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
            self.info_depth_lbl.grid() 
        else:
            self.depth_title_lbl.grid_remove()
            self.depth_ctrl_frame.grid_remove()
            self.info_depth_lbl.grid_remove() 

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

        if algo == 'BFS':
            sol, log = BREADTH_FIRST_SEARCH(init, goal)
        elif algo == 'DFS':
            sol, log = DEPTH_FIRST_SEARCH(init, goal, max_depth=m_depth)
        elif algo == 'IDS':
            sol, log = ITERATIVE_DEEPENING_SEARCH(init, goal, max_depth=m_depth)
        elif algo == 'UCS':
            sol, log = UNIFORM_COST_SEARCH(init, goal)

        if sol is None:
            messagebox.showinfo("Kết quả", "Không tìm thấy đường đi tới đích!")
            return

        self.solution_path = sol
        self.explore_log = log
        self.current_step = 0
        
        self._draw_solution_canvas()

        for b in [self.btn_prev, self.btn_play, self.btn_next]:
            b.config(state='normal')
            
        self._refresh_display()

    def _draw_solution_canvas(self):
        self.sol_canvas.delete("all")
        if not self.solution_path: return
        
        cell_size = 28
        grid_size = cell_size * 3
        arrow_space = 60
        y_offset = 15
        x_offset = 20
        
        for i, node in enumerate(self.solution_path):
            state = node['STATE']
            for row in range(3):
                for col in range(3):
                    val = state[row*3 + col]
                    x1 = x_offset + col * cell_size
                    y1 = y_offset + row * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    bg_color = '#90EE90' if (val == self.target_goal[row*3+col] and val != 0) else 'white'
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
                is_correct = (val == self.target_goal[i*3+j] and val != 0)
                bg_color = '#90EE90' if is_correct else 'white'
                self.board_labels[i][j].config(text=str(val) if val else "", bg=bg_color)
                
        self.info_step_lbl.config(text=f"Step: {self.current_step + 1} / {len(self.explore_log)}")
        self.info_cost_lbl.config(text=f"Path-Cost: {current_node['path_cost']}")
        
        if self.algo_var.get() in ['DFS', 'IDS']:
            self.info_depth_lbl.config(text=f"Depth: {current_node['depth']}")
            
        self.info_nodes_lbl.config(text=f"Nodes Generated: {len(step_data['explored_list']) + len(step_data['frontier_list'])}")

        self.list_frontier.delete(0, tk.END)
        for idx, item in enumerate(step_data['frontier_list'], 1):
            if isinstance(item, tuple) and len(item) == 2:
                s, cost = item
                self.list_frontier.insert(tk.END, f" {idx:02d}. {s} [Cost: {cost}]")
            else:
                self.list_frontier.insert(tk.END, f" {idx:02d}. {item}")
            
        self.list_explored.delete(0, tk.END)
        for idx, s in enumerate(step_data['explored_list'], 1):
            self.list_explored.insert(tk.END, f" {idx:02d}. {s}")

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