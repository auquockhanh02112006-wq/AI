import random

GOAL = [[1,2,3],[4,5,6],[7,8,0]]

MOVES = {"UP":(-1,0),"DOWN":(1,0),"LEFT":(0,-1),"RIGHT":(0,1)}

rules = [
    ("TOP_LEFT",      "RIGHT"),
    ("TOP_LEFT",      "DOWN"),
    ("TOP_MIDDLE",    "LEFT"),
    ("TOP_MIDDLE",    "RIGHT"),
    ("TOP_MIDDLE",    "DOWN"),
    ("TOP_RIGHT",     "LEFT"),
    ("TOP_RIGHT",     "DOWN"),
    ("MIDDLE_LEFT",   "UP"),
    ("MIDDLE_LEFT",   "RIGHT"),
    ("MIDDLE_LEFT",   "DOWN"),
    ("CENTER",        "UP"),
    ("CENTER",        "LEFT"),
    ("CENTER",        "RIGHT"),
    ("CENTER",        "DOWN"),
    ("MIDDLE_RIGHT",  "UP"),
    ("MIDDLE_RIGHT",  "LEFT"),
    ("MIDDLE_RIGHT",  "DOWN"),
    ("BOTTOM_LEFT",   "UP"),
    ("BOTTOM_LEFT",   "RIGHT"),
    ("BOTTOM_MIDDLE", "UP"),
    ("BOTTOM_MIDDLE", "LEFT"),
    ("BOTTOM_MIDDLE", "RIGHT"),
    ("BOTTOM_RIGHT",  "UP"),
    ("BOTTOM_RIGHT",  "LEFT"),
]

POS = {
    (0,0):"TOP_LEFT",(0,1):"TOP_MIDDLE",(0,2):"TOP_RIGHT",
    (1,0):"MIDDLE_LEFT",(1,1):"CENTER",(1,2):"MIDDLE_RIGHT",
    (2,0):"BOTTOM_LEFT",(2,1):"BOTTOM_MIDDLE",(2,2):"BOTTOM_RIGHT",
}

def random_puzzle():
    nums = list(range(9))
    random.shuffle(nums)
    return [nums[i*3:(i+1)*3] for i in range(3)]

def interpret_input(percept):
    for i in range(3):
        for j in range(3):
            if percept[i][j] == 0:
                return POS[(i,j)]

def rule_match(state, rules):
    for rule in rules:
        if rule[0] == state:
            return rule

def apply(puzzle, action):
    dr, dc = MOVES[action]
    for i in range(3):
        for j in range(3):
            if puzzle[i][j] == 0:
                puzzle[i][j], puzzle[i+dr][j+dc] = puzzle[i+dr][j+dc], puzzle[i][j]
                return

def print_puzzle(state):
    print()
    for row in state:
        for cell in row:
            if cell==0:
                print("_",end=" ")
            else:
                print(cell,end=" ")
        print()

def SRA(percept):
    state  = interpret_input(percept)
    rule   = rule_match(state, rules)
    action = rule[1]
    return action

puzzle = random_puzzle()
print("START:");
step = 0
while puzzle != GOAL and step < 100:
    print(f"\nStep {step}:"); print_puzzle(puzzle)
    action = SRA(puzzle)
    print("ACTION =", action)
    apply(puzzle, action)
    step += 1
print(f"\nStep {step}:"); print_puzzle(puzzle)
print("GOAL REACHED in", step, "steps" if puzzle == GOAL else "NOT SOLVED")