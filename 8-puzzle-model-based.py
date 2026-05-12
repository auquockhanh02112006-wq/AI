import random

GOAL = [
    [1,2,3],
    [4,5,6],
    [7,8,0]
]

MOVES = {
    "UP":(-1,0),
    "DOWN":(1,0),
    "LEFT":(0,-1),
    "RIGHT":(0,1)
}

POS = {
    (0,0):"TOP_LEFT",
    (0,1):"TOP_MIDDLE",
    (0,2):"TOP_RIGHT",
    (1,0):"MIDDLE_LEFT",
    (1,1):"CENTER",
    (1,2):"MIDDLE_RIGHT",
    (2,0):"BOTTOM_LEFT",
    (2,1):"BOTTOM_MIDDLE",
    (2,2):"BOTTOM_RIGHT"
}

rules = [
    ("TOP_LEFT","RIGHT"),
    ("TOP_LEFT","DOWN"),
    ("TOP_MIDDLE","LEFT"),
    ("TOP_MIDDLE","RIGHT"),
    ("TOP_MIDDLE","DOWN"),
    ("TOP_RIGHT","LEFT"),
    ("TOP_RIGHT","DOWN"),
    ("MIDDLE_LEFT","UP"),
    ("MIDDLE_LEFT","RIGHT"),
    ("MIDDLE_LEFT","DOWN"),
    ("CENTER","UP"),
    ("CENTER","DOWN"),
    ("CENTER","LEFT"),
    ("CENTER","RIGHT"),
    ("MIDDLE_RIGHT","UP"),
    ("MIDDLE_RIGHT","LEFT"),
    ("MIDDLE_RIGHT","DOWN"),
    ("BOTTOM_LEFT","UP"),
    ("BOTTOM_LEFT","RIGHT"),
    ("BOTTOM_MIDDLE","UP"),
    ("BOTTOM_MIDDLE","LEFT"),
    ("BOTTOM_MIDDLE","RIGHT"),
    ("BOTTOM_RIGHT","UP"),
    ("BOTTOM_RIGHT","LEFT")
]

def random_puzzle():
    nums = [0,1,2,3,4,5,6,7,8]
    random.shuffle(nums)
    return [
        nums[0:3],
        nums[3:6],
        nums[6:9]
    ]

def find_zero(puzzle):
    for i in range(3):
        for j in range(3):
            if puzzle[i][j] == 0:
                return i, j

def P_moves(x, y):
    moves = []
    if x > 0:
        moves.append("UP")
    if x < 2:
        moves.append("DOWN")
    if y > 0:
        moves.append("LEFT")
    if y < 2:
        moves.append("RIGHT")
    return moves

def update_state(state, action, percept, model):
    puzzle, x, y = percept
    state["position"] = POS[(x,y)]
    state["x"] = x
    state["y"] = y
    state["puzzle"] = puzzle
    model["visited"].append((x,y))
    state["visited"] = model["visited"]
    if action != None:
        state["memory"].append(action)
    return state

def rule_match(state, rules):
    x = state["x"]
    y = state["y"]
    position = state["position"]
    moves = P_moves(x, y)
    possible = []
    for rule in rules:
        if rule[0] == position and rule[1] in moves:
            dx, dy = MOVES[rule[1]]
            nx = x + dx
            ny = y + dy
            if (nx, ny) not in state["visited"]:
                possible.append(rule)
    if possible == []:
        for rule in rules:
            if rule[0] == position and rule[1] in moves:
                possible.append(rule)
    return random.choice(possible)

def apply(puzzle, x, y, action):
    dx, dy = MOVES[action]
    nx = x + dx
    ny = y + dy
    puzzle[x][y], puzzle[nx][ny] = puzzle[nx][ny], puzzle[x][y]
    return nx, ny

def print_puzzle(puzzle):
    print()
    for row in puzzle:
        print(row)

def MBA(percept):
    global state
    global action
    global model
    state = update_state(state, action, percept, model)
    rule = rule_match(state, rules)
    action = rule[1]
    return action

puzzle = random_puzzle()

x, y = find_zero(puzzle)

state = {
    "position":"",
    "x":x,
    "y":y,
    "puzzle":puzzle,
    "memory":[],
    "visited":[]
}

model = {
    "visited":[]
}

action = None

step = 0

print("START")

while puzzle != GOAL and step < 1000:
    print("\nSTEP", step)
    print_puzzle(puzzle)
    action = MBA((puzzle, x, y))
    print("STATE =", state["position"])
    print("ACTION =", action)
    x, y = apply(puzzle, x, y, action)
    step += 1

print("\nFINAL")

print_puzzle(puzzle)

if puzzle == GOAL:

    print("SOLVED")
else:

    print("NOT SOLVED")