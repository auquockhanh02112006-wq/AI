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

def interpret_input(percept):
    room, x, y = percept
    state = POS[(x,y)]
    rules = P_moves(x, y)
    if room[x][y] == 1:
        rules.append("CLEAN")
    return state, rules

def rule_match(state, rules):
    return state, random.choice(rules)

def apply(room, x, y, action):
    if action == "CLEAN":
        room[x][y] = 0
        return x, y
    dx, dy = MOVES[action]
    nx = x + dx
    ny = y + dy
    return nx, ny

def print_room(room, rx, ry):
    print()
    for i in range(4):
        for j in range(4):
            if i == rx and j == ry:
                print("R", end=" ")
            else:
                print(room[i][j], end=" ")
        print()

def SRA(percept):
    state, rules = interpret_input(percept)
    rule   = rule_match(state, rules)
    action = rule[1]
    return action

room = random_room()

x, y = random_position()

print("START")

step = 0

while room != GOAL and step < 1000:
    print("\nSTEP", step)
    print_room(room, x, y)
    action = SRA((room, x, y))
    print("ACTION =", action)
    x, y = apply(room, x, y, action)
    step += 1

print("\nFINAL")

print_room(room, x, y)

if room == GOAL:
    print("ALL CLEAN")
else:
    print("NOT FINISHED")