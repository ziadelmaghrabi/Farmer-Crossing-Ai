import tkinter as tk
from collections import deque
import heapq

# =======================
# State Representation
# =======================
class State:
    def __init__(self, left, right, boat, parent=None, move=None, cost=0):
        self.left = tuple(sorted(left))
        self.right = tuple(sorted(right))
        self.boat = boat
        self.parent = parent
        self.move = move
        self.cost = cost

    def is_goal(self):
        return len(self.left) == 0

    def __eq__(self, other):
        return (self.left, self.right, self.boat) == (other.left, other.right, other.boat)

    def __hash__(self):
        return hash((self.left, self.right, self.boat))


# =======================
# Main Game Class
# =======================
class FarmerCrossingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Farmer Crossing with Search Algorithms")
        self.root.geometry("900x600")

        self.canvas = tk.Canvas(root, width=900, height=600, bg="#87CEEB")
        self.canvas.pack(fill="both", expand=True)

        # Initial State
        self.left_bank = ['farmer', 'goat', 'wolf', 'cabbage']
        self.right_bank = []
        self.boat_side = 'left'
        self.moves = 0

        self.entities = {
            'farmer': '👨‍🌾',
            'goat': '🐐',
            'wolf': '🐺',
            'cabbage': '🥬'
        }

        self.draw_ui()

    # =======================
    # UI
    # =======================
    def draw_ui(self):
        self.canvas.create_text(450, 30, text="Farmer River Crossing",
                                font=("Arial", 24, "bold"))

        self.msg = self.canvas.create_text(450, 70,
                                           text="Choose a search algorithm",
                                           font=("Arial", 14))

        # Buttons
        self.make_button(50, 500, 200, 550, "BFS", self.run_bfs)
        self.make_button(250, 500, 400, 550, "DFS", self.run_dfs)
        self.make_button(450, 500, 600, 550, "A*", self.run_astar)
        self.make_button(650, 500, 850, 550, "RESET", self.reset)

        self.update_display()

    def make_button(self, x1, y1, x2, y2, text, cmd):
        btn = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#3498DB")
        txt = self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                      text=text, fill="white",
                                      font=("Arial", 14, "bold"))
        self.canvas.tag_bind(btn, "<Button-1>", lambda e: cmd())
        self.canvas.tag_bind(txt, "<Button-1>", lambda e: cmd())

    # =======================
    # Logic Helpers
    # =======================
    def is_safe(self, bank):
        if 'farmer' not in bank:
            if 'wolf' in bank and 'goat' in bank:
                return False
            if 'goat' in bank and 'cabbage' in bank:
                return False
        return True

    def get_successors(self, state):
        successors = []
        current = list(state.left if state.boat == 'left' else state.right)

        moves = [['farmer'],
                 ['farmer', 'goat'],
                 ['farmer', 'wolf'],
                 ['farmer', 'cabbage']]

        for move in moves:
            if all(x in current for x in move):
                if state.boat == 'left':
                    new_left = list(state.left)
                    new_right = list(state.right)
                    for x in move:
                        new_left.remove(x)
                        new_right.append(x)
                    new_boat = 'right'
                else:
                    new_left = list(state.left)
                    new_right = list(state.right)
                    for x in move:
                        new_right.remove(x)
                        new_left.append(x)
                    new_boat = 'left'

                if self.is_safe(new_left) and self.is_safe(new_right):
                    successors.append(State(new_left, new_right, new_boat,
                                            state, move, state.cost + 1))
        return successors

    # =======================
    # BFS
    # =======================
    def bfs(self):
        start = State(self.left_bank, self.right_bank, self.boat_side)
        queue = deque([start])
        visited = set()

        while queue:
            s = queue.popleft()
            if s in visited:
                continue
            visited.add(s)

            if s.is_goal():
                return s

            for n in self.get_successors(s):
                queue.append(n)

    # =======================
    # DFS
    # =======================
    def dfs(self):
        start = State(self.left_bank, self.right_bank, self.boat_side)
        stack = [start]
        visited = set()

        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)

            if s.is_goal():
                return s

            for n in reversed(self.get_successors(s)):
                stack.append(n)

    # =======================
    # A*
    # =======================
    def heuristic(self, state):
        # Heuristic: number of items left on the left bank
        return len(state.left)

    def astar(self):
        start = State(self.left_bank, self.right_bank, self.boat_side)
        pq = []
        counter = 0
        heapq.heappush(pq, (0, counter, start))
        visited = set()

        while pq:
            _, _, s = heapq.heappop(pq)

            if s in visited:
                continue
            visited.add(s)

            if s.is_goal():
                return s

            for n in self.get_successors(s):
                counter += 1
                f = n.cost + self.heuristic(n)
                heapq.heappush(pq, (f, counter, n))

    # =======================
    # Run & Animate Solution
    # =======================
    def play_solution(self, goal):
        path = []
        while goal.parent:
            path.append(goal)
            goal = goal.parent
        path.reverse()

        def step(i=0):
            if i >= len(path):
                self.canvas.itemconfig(self.msg,
                                       text=f"Finished in {i} moves")
                return
            s = path[i]
            self.left_bank = list(s.left)
            self.right_bank = list(s.right)
            self.boat_side = s.boat
            self.moves = i
            self.update_display()
            self.root.after(1000, lambda: step(i+1))

        step()

    # =======================
    # Button Actions
    # =======================
    def run_bfs(self):
        self.canvas.itemconfig(self.msg, text="Solving using BFS...")
        self.play_solution(self.bfs())

    def run_dfs(self):
        self.canvas.itemconfig(self.msg, text="Solving using DFS...")
        self.play_solution(self.dfs())

    def run_astar(self):
        self.canvas.itemconfig(self.msg, text="Solving using A*...")
        self.play_solution(self.astar())

    def reset(self):
        self.left_bank = ['farmer', 'goat', 'wolf', 'cabbage']
        self.right_bank = []
        self.boat_side = 'left'
        self.moves = 0
        self.update_display()
        self.canvas.itemconfig(self.msg, text="Choose a search algorithm")

    # =======================
    # Display
    # =======================
    def update_display(self):
        self.canvas.delete("entity")

        self.canvas.create_rectangle(50, 150, 300, 400, fill="#90EE90")
        self.canvas.create_rectangle(600, 150, 850, 400, fill="#90EE90")
        self.canvas.create_rectangle(300, 150, 600, 400, fill="#1E90FF")

        self.canvas.create_text(175, 130, text="LEFT BANK")
        self.canvas.create_text(725, 130, text="RIGHT BANK")

        y = 200
        for e in self.left_bank:
            self.canvas.create_text(175, y, text=self.entities[e],
                                    font=("Arial", 40), tags="entity")
            y += 60

        y = 200
        for e in self.right_bank:
            self.canvas.create_text(725, y, text=self.entities[e],
                                    font=("Arial", 40), tags="entity")
            y += 60

        boat_text = "🚣‍♂️" if self.boat_side == 'left' else "🚣‍♂️"
        x = 350 if self.boat_side == 'left' else 550
        self.canvas.create_text(x, 280, text=boat_text,
                                font=("Arial", 40), tags="entity")


# =======================
# Run App
# =======================
if __name__ == "__main__":
    root = tk.Tk()
    FarmerCrossingGame(root)
    root.mainloop()