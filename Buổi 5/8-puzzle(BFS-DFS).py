import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random

# ═══════════════════════════════════════════════════════════════
#  LOGIC THUẬT TOÁN BFS & DFS CHO 8-PUZZLE
# ═══════════════════════════════════════════════════════════════

def ACTIONS(state):
    """Trả về danh sách các hành động hợp lệ từ trạng thái hiện tại (UP, DOWN, LEFT, RIGHT).
    Thứ tự được xáo trộn ngẫu nhiên để tăng tính ngẫu nhiên khi tìm kiếm."""
    idx = state.index(0)                    # Vị trí của ô trống (0)
    row, col = idx // 3, idx % 3
    moves = []
    if row > 0: moves.append('UP')
    if row < 2: moves.append('DOWN')
    if col > 0: moves.append('LEFT')
    if col < 2: moves.append('RIGHT')
    random.shuffle(moves)                   # Xáo trộn để DFS/BFS có tính ngẫu nhiên
    return moves

def CHILD_NODE(problem_state, parent, action):
    """Tạo node con từ node cha khi thực hiện một action.
    Trả về dictionary chứa trạng thái mới, parent, action và độ sâu."""
    state = list(problem_state)
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    # Tính vị trí cần hoán đổi
    targets = {
        'UP': (row-1)*3 + col,
        'DOWN': (row+1)*3 + col,
        'LEFT': row*3 + (col-1),
        'RIGHT': row*3 + (col+1)
    }
    swap = targets[action]
    state[idx], state[swap] = state[swap], state[idx]   # Hoán đổi ô trống
    return {
        'STATE': tuple(state),
        'parent': parent,
        'action': action,
        'depth': parent['depth'] + 1
    }

def SOLUTION(node):
    """Truy vết từ node mục tiêu về node gốc để lấy đường đi giải pháp."""
    path = []
    while node is not None:
        path.append(node)
        node = node['parent']
    return list(reversed(path))                     # Đảo ngược để có thứ tự từ đầu đến cuối

def BREADTH_FIRST_SEARCH(initial_state, goal_state):
    """Thuật toán BFS - Tìm đường đi ngắn nhất theo số bước di chuyển."""
    explore_log = []
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    
    if node['STATE'] == goal_state:
        return SOLUTION(node), explore_log
    frontier = deque([node])            # Hàng đợi (FIFO)
    frontier_set = {node['STATE']}      # Dùng set để kiểm tra nhanh
    explored = set()
    while frontier:
        node = frontier.popleft()
        frontier_set.discard(node['STATE'])
        explored.add(node['STATE'])
        explore_log.append({
            'node': node,
            'frontier_size': len(frontier),
            'explored_size': len(explored)
        })
        for action in ACTIONS(node['STATE']):
            child = CHILD_NODE(node['STATE'], node, action)
            if child['STATE'] not in explored and child['STATE'] not in frontier_set:
                if child['STATE'] == goal_state:
                    return SOLUTION(child), explore_log
                
                frontier.append(child)
                frontier_set.add(child['STATE'])
    return None, explore_log

def DEPTH_FIRST_SEARCH(initial_state, goal_state, max_depth=100000):
    """Thuật toán DFS - Tìm đường đi theo chiều sâu (có giới hạn độ sâu)."""
    explore_log = []
    node = {'STATE': initial_state, 'parent': None, 'action': None, 'depth': 0}
    
    frontier = [node]                       # Stack (LIFO)
    frontier_set = {node['STATE']}
    explored = set()
    while frontier:
        node = frontier.pop()               # Lấy từ cuối
        frontier_set.discard(node['STATE'])
        
        if node['STATE'] in explored:
            continue 
        explored.add(node['STATE'])
        explore_log.append({
            'node': node,
            'frontier_size': len(frontier),
            'explored_size': len(explored)
        })
        if node['STATE'] == goal_state:
            return SOLUTION(node), explore_log
        if node['depth'] < max_depth:
            for action in ACTIONS(node['STATE']):
                child = CHILD_NODE(node['STATE'], node, action)
                if child['STATE'] not in explored and child['STATE'] not in frontier_set:
                    frontier.append(child)
                    frontier_set.add(child['STATE'])
    return None, explore_log

# ═══════════════════════════════════════════════════════════════
#  GIAO DIỆN NGƯỜI DÙNG
# ═══════════════════════════════════════════════════════════════

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Custom Goal Solver")
        self.root.geometry("900x680")
        self.root.configure(bg='#ffffff')
        # Trạng thái ứng dụng
        self.solution_path = []      # Danh sách các node trên đường giải pháp
        self.explore_log = []        # Log quá trình khám phá của thuật toán
        self.current_step = 0        # Bước hiện tại đang hiển thị
        self.is_playing = False      # Đang tự động chạy không?
        self.play_job = None         # ID của after() để cancel
        self.target_goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)  # Mục tiêu mặc định
        # Tốc độ animation (ms)
        self.speed_var = tk.IntVar(value=500)
        self._build_ui()

    def _build_ui(self):
        """Xây dựng toàn bộ giao diện."""
        # --- Header ---
        header = tk.Frame(self.root, bg='#ffffff', bd=1, relief='solid')
        header.pack(fill='x', padx=10, pady=5)
        tk.Label(header, text="8-PUZZLE SOLVER (BFS & DFS)", 
                font=('Consolas', 14, 'bold'), bg='#ffffff').pack(pady=5)
        main_body = tk.Frame(self.root, bg='#ffffff')
        main_body.pack(fill='both', expand=True, padx=10)
        # === PANEL TRÁI: Cài đặt ===
        left = tk.Frame(main_body, bg='#f0f0f0', width=260, bd=1, relief='solid')
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        tk.Label(left, text="INITIAL STATE", font=('Consolas', 9, 'bold'), bg='#f0f0f0').pack(pady=(10, 0))
        self.init_cells = self._create_grid(left, [1, 2, 3, 4, 0, 6, 7, 5, 8])
        tk.Label(left, text="GOAL STATE", font=('Consolas', 9, 'bold'), bg='#f0f0f0').pack(pady=(15, 0))
        self.goal_cells = self._create_grid(left, [1, 2, 3, 4, 5, 6, 7, 8, 0])
        tk.Label(left, text="ALGORITHM", font=('Consolas', 9, 'bold'), bg='#f0f0f0').pack(pady=(15, 0))
        self.algo_var = tk.StringVar(value='BFS')
        tk.Radiobutton(left, text="BFS (Breadth-First)", variable=self.algo_var, 
                    value='BFS', bg='#f0f0f0', font=('Consolas', 9)).pack(anchor='w', padx=20)
        tk.Radiobutton(left, text="DFS (Depth-First)", variable=self.algo_var, 
                    value='DFS', bg='#f0f0f0', font=('Consolas', 9)).pack(anchor='w', padx=20)
        # Thanh trượt tốc độ
        tk.Label(left, text="SPEED (ms)", font=('Consolas', 9, 'bold'), bg='#f0f0f0').pack(pady=(15, 0))
        self.speed_scale = tk.Scale(left, from_=50, to=2000, orient='horizontal', 
                                    variable=self.speed_var, bg='#f0f0f0', highlightthickness=0)
        self.speed_scale.pack(fill='x', padx=20)
        tk.Button(left, text="SOLVE", command=self._solve, 
                bg='#ffffff', font=('Consolas', 11, 'bold'), relief='solid', bd=1)\
                .pack(fill='x', padx=20, pady=20)
        self.stats_lbl = tk.Label(left, text="Ready", bg='#f0f0f0', font=('Consolas', 8), justify='left')
        self.stats_lbl.pack(anchor='w', padx=20)
        # === PANEL PHẢI: Hiển thị và Điều khiển ===
        right = tk.Frame(main_body, bg='#ffffff')
        right.pack(side='left', fill='both', expand=True)
        # Chọn chế độ hiển thị
        self.mode_var = tk.StringVar(value='solution')
        m_frame = tk.Frame(right, bg='#ffffff')
        m_frame.pack(fill='x')
        tk.Radiobutton(m_frame, text="Solution Path", variable=self.mode_var, 
                    value='solution', command=self._refresh_display, bg='#ffffff').pack(side='left')
        tk.Radiobutton(m_frame, text="Exploration Log", variable=self.mode_var, 
                    value='explore', command=self._refresh_display, bg='#ffffff').pack(side='left')
        # Bảng 3x3 hiển thị
        disp_frame = tk.Frame(right, bg='#f0f0f0', bd=1, relief='solid', pady=20)
        disp_frame.pack(fill='x', pady=10)
        self.board_labels = []
        grid_res = tk.Frame(disp_frame, bg='#f0f0f0')
        grid_res.pack()
        for i in range(3):
            row_l = []
            for j in range(3):
                l = tk.Label(grid_res, text="", width=5, height=2, 
                            font=('Consolas', 20, 'bold'), bg='#ffffff', bd=1, relief='solid')
                l.grid(row=i, column=j, padx=4, pady=4)
                row_l.append(l)
            self.board_labels.append(row_l)
        self.info_lbl = tk.Label(disp_frame, text="Step: -", bg='#f0f0f0', font=('Consolas', 10))
        self.info_lbl.pack(pady=5)
        # Nút điều khiển
        ctrl = tk.Frame(right, bg='#ffffff')
        ctrl.pack(fill='x')
        self.btn_prev = tk.Button(ctrl, text="Prev", command=self._go_prev, state='disabled')
        self.btn_prev.pack(side='left', padx=5)
        self.btn_play = tk.Button(ctrl, text="Play", command=self._toggle_play, state='disabled')
        self.btn_play.pack(side='left', padx=5)
        self.btn_next = tk.Button(ctrl, text="Next", command=self._go_next, state='disabled')
        self.btn_next.pack(side='left', padx=5)
        self.log_box = tk.Text(right, height=10, font=('Consolas', 8), bd=1, relief='solid')
        self.log_box.pack(fill='both', expand=True, pady=10)

    def _create_grid(self, parent, defaults):
        """Tạo bảng nhập liệu 3x3 cho Initial hoặc Goal state."""
        f = tk.Frame(parent, bg='#f0f0f0')
        f.pack(pady=5)
        cells = []
        for i in range(3):
            row = []
            for j in range(3):
                e = tk.Entry(f, width=3, font=('Consolas', 12, 'bold'), 
                            justify='center', bd=1, relief='solid')
                e.grid(row=i, column=j, padx=2, pady=2)
                e.insert(0, str(defaults[i*3+j]))
                row.append(e)
            cells.append(row)
        return cells

    def _read_grid(self, cells):
        """Đọc dữ liệu từ các Entry và kiểm tra tính hợp lệ."""
        try:
            res = []
            for r in cells:
                for c in r:
                    res.append(int(c.get().strip()))
            if sorted(res) != list(range(9)):
                raise ValueError
            return tuple(res)
        except:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng các số từ 0 đến 8 (không trùng lặp).")
            return None

    def _solve(self):
        """Thực hiện giải bài toán theo thuật toán đã chọn."""
        self._stop_play()
        init = self._read_grid(self.init_cells)
        goal = self._read_grid(self.goal_cells)
        if not init or not goal:
            return
        self.target_goal = goal
        algo = self.algo_var.get()
        self.log_box.delete('1.0', 'end')
        self.log_box.insert('end', f"Solving {algo}...\nFrom: {init}\nTo  : {goal}\n")
        self.root.update()
        if algo == 'BFS':
            sol, log = BREADTH_FIRST_SEARCH(init, goal)
        else:
            sol, log = DEPTH_FIRST_SEARCH(init, goal)
        self.solution_path = sol or []
        self.explore_log = log
        self.current_step = 0
        if sol:
            self.stats_lbl.config(text=f"✓ Success!\nSteps: {len(sol)-1}\nNodes: {len(log)}")
            for b in [self.btn_prev, self.btn_play, self.btn_next]:
                b.config(state='normal')
        else:
            self.stats_lbl.config(text=f"✕ No solution found\nNodes: {len(log)}")
            messagebox.showwarning("Kết quả", "Không tìm thấy đường đi giữa hai trạng thái này.")
        self._refresh_display()

    def _refresh_display(self):
        """Cập nhật giao diện bảng và thông tin theo bước hiện tại."""
        lst = self.solution_path if self.mode_var.get() == 'solution' else self.explore_log
        if not lst:
            return
        self.current_step = max(0, min(self.current_step, len(lst)-1))
        node = lst[self.current_step]
        if isinstance(node, dict) and 'node' in node:
            node = node['node']
        state = node['STATE']
        for i in range(3):
            for j in range(3):
                val = state[i*3 + j]
                # Highlight ô đúng vị trí so với goal
                is_correct = (val == self.target_goal[i*3 + j] and val != 0)
                self.board_labels[i][j].config(
                    text=str(val) if val else "",
                    bg='#e0e0e0' if is_correct else ('#999999' if val == 0 else '#ffffff')
                )
        self.info_lbl.config(text=f"Step {self.current_step} / {len(lst)-1} | "
                                f"Action: {node['action'] or 'START'}")

    def _go_prev(self):
        """Quay lại bước trước."""
        if self.current_step > 0:
            self.current_step -= 1
            self._refresh_display()

    def _go_next(self):
        """Chuyển sang bước tiếp theo."""
        lst = self.solution_path if self.mode_var.get() == 'solution' else self.explore_log
        if self.current_step < len(lst) - 1:
            self.current_step += 1
            self._refresh_display()

    def _toggle_play(self):
        """Bật/Tắt chế độ tự động chạy."""
        self.is_playing = not self.is_playing
        self.btn_play.config(text="Stop" if self.is_playing else "Play")
        if self.is_playing:
            self._auto_run()

    def _auto_run(self):
        """Tự động chạy animation theo tốc độ từ thanh trượt."""
        if not self.is_playing:
            return
            
        lst = self.solution_path if self.mode_var.get() == 'solution' else self.explore_log
        if self.current_step < len(lst) - 1:
            self._go_next()
            delay = self.speed_var.get()          # Lấy giá trị từ thanh Scale
            self.play_job = self.root.after(delay, self._auto_run)
        else:
            self._stop_play()

    def _stop_play(self):
        """Dừng animation."""
        self.is_playing = False
        self.btn_play.config(text="Play")
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None

if __name__ == '__main__':
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()