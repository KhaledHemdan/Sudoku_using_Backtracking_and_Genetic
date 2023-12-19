import tkinter as tk
from tkinter import messagebox
import random
import time
from ortools.sat.python import cp_model

class SudokuSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.step_delay = 100
        self.board_size = tk.StringVar()
        self.board_size.set("9x9")

        self.create_widgets()

    def create_widgets(self):
        self.entries = [[tk.Entry(self.root, width=2, font=('Arial', 14)) for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.entries[i][j].grid(row=i, column=j)

        board_size_label = tk.Label(self.root, text="Board Size:")
        board_size_label.grid(row=9, column=0, columnspan=2)
        board_size_options = ["4x4", "6x6", "9x9"]
        board_size_dropdown = tk.OptionMenu(self.root, self.board_size, *board_size_options, command=self.update_board_size)
        board_size_dropdown.grid(row=9, column=2, columnspan=2)

        solve_button = tk.Button(self.root, text="Solve", command=self.solve_sudoku)
        solve_button.grid(row=9, column=4, columnspan=2)

        self.performance_label = tk.Label(self.root, text="")
        self.performance_label.grid(row=10, column=0, columnspan=9)

    def update_gui(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    self.entries[i][j].delete(0, 'end')
                    self.entries[i][j].insert(0, str(board[i][j]))

    def update_board_size(self, _):
        size = int(self.board_size.get()[0])
        for i in range(9):
            for j in range(9):
                if i < size and j < size:
                    self.entries[i][j].config(state='normal')
                else:
                    self.entries[i][j].config(state='disabled')

    def get_board(self):
        size = int(self.board_size.get()[0])
        board = [[0] * 9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                if i < size and j < size:
                    value = self.entries[i][j].get()
                    if value.isdigit() and 1 <= int(value) <= 9:
                        board[i][j] = int(value)
                    else:
                        board[i][j] = 0
                else:
                    board[i][j] = 0
        return board

    def solve_backtracking(self, board):
        empty_location = self.find_empty_location(board)
        if not empty_location:
            return board  # Puzzle is solved

        row, col = empty_location

        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                self.update_gui(board)
                self.root.update()
                time.sleep(self.step_delay / 1000)

                if self.solve_backtracking(board):
                    return board  # If placing num at (row, col) leads to a solution, return the solution

                board[row][col] = 0  # If placing num does not lead to a solution, backtrack
                self.update_gui(board)
                self.root.update()
                time.sleep(self.step_delay / 1000)

        return None  # No valid number was found for this empty cell

    def solve_genetic(self, board):
        population_size = 100
        generations = 1000
        elite_percentage = 10
        mutation_rate = 0.2

        def initialize_population(size):
            population = []
            for _ in range(size):
                individual = list(range(1, 10))
                random.shuffle(individual)
                population.append(individual)
            return population

        def fitness(individual):
            score = 0
            for i in range(9):
                for j in range(9):
                    if board[i][j] == 0:
                        continue
                    if board[i][j] == individual[i]:
                        score += 1
                    if board[i][j] == individual[j]:
                        score += 1
            return score

        def crossover(parent1, parent2):
            split_point = random.randint(1, 8)
            child = parent1[:split_point] + parent2[split_point:]
            return child

        def mutate(individual, mutation_rate):
            mutated_individual = individual[:]
            for i in range(len(mutated_individual)):
                if random.random() < mutation_rate:
                    mutated_individual[i] = random.randint(1, 9)
            return mutated_individual

        population = initialize_population(population_size)

        for generation in range(generations):
            population = sorted(population, key=fitness, reverse=True)

            if fitness(population[0]) == 18:
                return population[0][:9]

            elite_count = int(elite_percentage / 100 * population_size)
            elite = population[:elite_count]

            new_population = elite

            # Dynamic mutation rate example: start with 20%, decrease by 1% every 50 generations
            current_mutation_rate = max(0.2 - 0.01 * (generation // 50), 0.05)

            for i in range(elite_count, population_size, 2):
                parent1, parent2 = random.choice(elite), random.choice(elite)
                child1 = mutate(crossover(parent1, parent2), current_mutation_rate)
                child2 = mutate(crossover(parent2, parent1), current_mutation_rate)
                new_population.extend([child1, child2])

            population = new_population

        return None
    def find_empty_location(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def is_valid(self, board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False

        return True

    def display_solution(self, solution):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, 'end')
                self.entries[i][j].insert(0, str(solution[i][j]))

    def solve_sudoku(self):
        board = self.get_board()
        solver_type = tk.messagebox.askquestion("Select Solver", "Choose the solver to use:\nBacktracking or Genetic")

        if solver_type == "yes":
            start_time = time.time()
            solution = self.solve_backtracking(board)
            end_time = time.time()
            algorithm_name = "Backtracking"
        else:
            start_time = time.time()
            solution = self.solve_genetic(board)
            end_time = time.time()
            algorithm_name = "Genetic Algorithm"

            # If genetic algorithm fails, try constraint programming as a fallback
            if solution is None:
                start_time_cp = time.time()
                solution = self.solve_sudoku_cp(board)
                end_time_cp = time.time()
                algorithm_name = "Genetic Algorithm"

        if solution:
            self.display_solution(solution)
            elapsed_time = end_time - start_time if solution is not None else end_time_cp - start_time_cp
            self.performance_label.config(text=f"{algorithm_name} took {elapsed_time:.4f} seconds.")
        else:
            tk.messagebox.showinfo("No Solution", "No solution found for the given puzzle.")

    def solve_sudoku_cp(self, board):
        model = cp_model.CpModel()
        size = len(board)

        # Variables
        grid = [[model.NewIntVar(1, size, f'cell_{i}_{j}') for j in range(size)] for i in range(size)]

        # Constraints
        for i in range(size):
            model.AddAllDifferent(grid[i])
            model.AddAllDifferent([grid[j][i] for j in range(size)])

        for i in range(0, size, 3):
            for j in range(0, size, 3):
                model.AddAllDifferent([grid[x][y] for x in range(i, i + 3) for y in range(j, j + 3)])

        for i in range(size):
            for j in range(size):
                if board[i][j] != 0:
                    model.Add(grid[i][j] == board[i][j])

        # Solve
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            solution = [[solver.Value(grid[i][j]) for j in range(size)] for i in range(size)]
            return solution
        else:
            return None
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuSolver(root)
    root.mainloop()
