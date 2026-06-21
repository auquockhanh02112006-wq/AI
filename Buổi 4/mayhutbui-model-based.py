import random

GOAL = [
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,0],
    [0,0,0,0]
]

MOVES = {
    "UP":(-1,0),
    "DOWN":(1,0),
    "LEFT":(0,-1),
    "RIGHT":(0,1)
}

POS = {
    (0,0):"TOP_LEFT",
    (0,1):"TOP_MIDDLE_LEFT",
    (0,2):"TOP_MIDDLE_RIGHT",
    (0,3):"TOP_RIGHT",
    (1,0):"MIDDLE_TOP_LEFT",
    (1,1):"CENTER_TOP_LEFT",
    (1,2):"CENTER_TOP_RIGHT",
    (1,3):"MIDDLE_TOP_RIGHT",
    (2,0):"MIDDLE_BOTTOM_LEFT",
    (2,1):"CENTER_BOTTOM_LEFT",
    (2,2):"CENTER_BOTTOM_RIGHT",
    (2,3):"MIDDLE_BOTTOM_RIGHT",
    (3,0):"BOTTOM_LEFT",
    (3,1):"BOTTOM_MIDDLE_LEFT",
    (3,2):"BOTTOM_MIDDLE_RIGHT",
    (3,3):"BOTTOM_RIGHT"
}

rules = [
    ("TOP_LEFT","RIGHT"),
    ("TOP_LEFT","DOWN"),
    ("TOP_MIDDLE_LEFT","LEFT"),
    ("TOP_MIDDLE_LEFT","RIGHT"),
    ("TOP_MIDDLE_LEFT","DOWN"),
    ("TOP_MIDDLE_RIGHT","LEFT"),
    ("TOP_MIDDLE_RIGHT","RIGHT"),
    ("TOP_MIDDLE_RIGHT","DOWN"),
    ("TOP_RIGHT","LEFT"),
    ("TOP_RIGHT","DOWN"),
    ("MIDDLE_TOP_LEFT","UP"),
    ("MIDDLE_TOP_LEFT","DOWN"),
    ("MIDDLE_TOP_LEFT","RIGHT"),
    ("CENTER_TOP_LEFT","UP"),
    ("CENTER_TOP_LEFT","DOWN"),
    ("CENTER_TOP_LEFT","LEFT"),
    ("CENTER_TOP_LEFT","RIGHT"),
    ("CENTER_TOP_RIGHT","UP"),
    ("CENTER_TOP_RIGHT","DOWN"),
    ("CENTER_TOP_RIGHT","LEFT"),
    ("CENTER_TOP_RIGHT","RIGHT"),
    ("MIDDLE_TOP_RIGHT","UP"),
    ("MIDDLE_TOP_RIGHT","DOWN"),
    ("MIDDLE_TOP_RIGHT","LEFT"),
    ("MIDDLE_BOTTOM_LEFT","UP"),
    ("MIDDLE_BOTTOM_LEFT","DOWN"),
    ("MIDDLE_BOTTOM_LEFT","RIGHT"),
    ("CENTER_BOTTOM_LEFT","UP"),
    ("CENTER_BOTTOM_LEFT","DOWN"),
    ("CENTER_BOTTOM_LEFT","LEFT"),
    ("CENTER_BOTTOM_LEFT","RIGHT"),
    ("CENTER_BOTTOM_RIGHT","UP"),
    ("CENTER_BOTTOM_RIGHT","DOWN"),
    ("CENTER_BOTTOM_RIGHT","LEFT"),
    ("CENTER_BOTTOM_RIGHT","RIGHT"),
    ("MIDDLE_BOTTOM_RIGHT","UP"),
    ("MIDDLE_BOTTOM_RIGHT","DOWN"),
    ("MIDDLE_BOTTOM_RIGHT","LEFT"),
    ("BOTTOM_LEFT","UP"),
    ("BOTTOM_LEFT","RIGHT"),
    ("BOTTOM_MIDDLE_LEFT","UP"),
    ("BOTTOM_MIDDLE_LEFT","LEFT"),
    ("BOTTOM_MIDDLE_LEFT","RIGHT"),
    ("BOTTOM_MIDDLE_RIGHT","UP"),
    ("BOTTOM_MIDDLE_RIGHT","LEFT"),
    ("BOTTOM_MIDDLE_RIGHT","RIGHT"),
    ("BOTTOM_RIGHT","UP"),
    ("BOTTOM_RIGHT","LEFT")
]

def random_room():
    return [[random.randint(0,1) for j in range(4)] for i in range(4)]

def random_position():
    return random.randint(0,3), random.randint(0,3)

def P_moves(x, y):
    moves = []
    if x > 0:
        moves.append("UP")
    if x < 3:
        moves.append("DOWN")
    if y > 0:
        moves.append("LEFT")
    if y < 3:
        moves.append("RIGHT")
    return moves

def update_state(state, action, percept, model):
    room, x, y = percept
    state["position"] = POS[(x,y)]
    state["x"] = x
    state["y"] = y
    state["room"] = room
    model["visited"].append((x,y))
    state["visited"] = model["visited"]
    if action != None:
        state["memory"].append(action)
    return state

def rule_match(state, rules):
    room = state["room"]
    x = state["x"]
    y = state["y"]
    position = state["position"]
    if room[x][y] == 1:
        return ("DIRTY","CLEAN")
    moves = P_moves(x, y)
    possible = []
    for rule in rules:
        if rule[0] == position and rule[1] in moves:
            dx, dy = MOVES[rule[1]]
            nx = x + dx
            ny = y + dy
            if (nx, ny) not in model["visited"]:
                possible.append(rule)
    if possible == []:
        for rule in rules:
            if rule[0] == position and rule[1] in moves:
                possible.append(rule)
    return random.choice(possible)

def apply(room, x, y, action):
    if action == "CLEAN":
        room[x][y] = 0
        return x, y
    dx, dy = MOVES[action]
    return x + dx, y + dy

def print_room(room, rx, ry):
    print()
    for i in range(4):
        for j in range(4):
            if i == rx and j == ry:
                print("R", end=" ")
            else:
                print(room[i][j], end=" ")
        print()

def MBA(percept):
    global state
    global action
    global model
    state = update_state(state, action, percept, model)
    rule = rule_match(state, rules)
    action = rule[1]
    return action

room = random_room()

x, y = random_position()

state = {
    "position":"",
    "x":x,
    "y":y,
    "room":room,
    "memory":[],
    "visited":[]
}

model = {
    "visited":[]
}

action = None

step = 0

print("START")

while room != GOAL and step < 1000:
    print("\nSTEP", step)
    print_room(room, x, y)
    action = MBA((room, x, y))
    print("STATE =", state["position"])
    print("ACTION =", action)
    x, y = apply(room, x, y, action)
    step += 1

print("\nFINAL")

print_room(room, x, y)

if room == GOAL:
    print("ALL CLEAN")
else:
    print("NOT FINISHED")