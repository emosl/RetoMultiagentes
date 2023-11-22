import networkx as nx
import numpy as np
from mesa import agent


class Astar:
    def __init__(self, grid):
        self.grid = grid
    #     self.grid = self.read_grid_from_file('city_files/2022_base.txt')

    # def read_grid_from_file(self, file_path):
    #     with open(file_path, 'r') as file:
    #         grid = [list(line.strip()) for line in file if line.strip()]
    #     return grid
    
    def create_graph(self):
        G = nx.DiGraph()
        rows, cols = self.grid.height, self.grid.width
        
        for y in range(rows):
            for x in range(cols):
                # Get contents of the cell at (x, y)
                cell_contents = self.grid.get_cell_list_contents((x, y))
                
                # Determine the node type based on cell contents
                node = self.determine_node_type(cell_contents)
                
                if node == '#':
                    continue 

                # Determine valid neighbors for '>'
                if node == '>':
                    # Right to s, D, >, I
                    if x + 1 < cols and self.grid[y][x + 1] in ['s', 'D', '>', 'I']:
                        G.add_edge((x, y), (x + 1, y))
                    # Up to ^, D
                    if y - 1 >= 0 and self.grid[y - 1][x] in ['^', 'D']:
                        G.add_edge((x, y), (x, y - 1))
                    # Up-right to >
                    if y - 1 >= 0 and x + 1 < cols and self.grid[y - 1][x + 1] == '>':
                        G.add_edge((x, y), (x + 1, y - 1))
                    # Up-left to >
                    if y - 1 >= 0 and x - 1 >= 0 and self.grid[y - 1][x - 1] == '>':
                        G.add_edge((x, y), (x - 1, y - 1))

                # Determine valid neighbors for '<'
                if node == '<':
                    # Left to s, D, <, I
                    if x - 1 >= 0 and self.grid[y][x - 1] in ['s', 'D', '<', 'I']:
                        G.add_edge((x, y), (x - 1, y))
                    # Up to ^, D
                    if y - 1 >= 0 and self.grid[y - 1][x] in ['^', 'D']:
                        G.add_edge((x, y), (x, y - 1))
                    # Down-left to <
                    if y + 1 < rows and x - 1 >= 0 and self.grid[y + 1][x - 1] == '<':
                        G.add_edge((x, y), (x - 1, y + 1))
                    # Down-right to <
                    if y + 1 < rows and x + 1 < cols and self.grid[y + 1][x + 1] == '<':
                        G.add_edge((x, y), (x + 1, y + 1))

                if node == '^':
                    # Up to ^, D, I, S
                    if y - 1 >= 0 and self.grid[y - 1][x] in ['^', 'D', 'I', 'S']:
                        G.add_edge((x, y), (x, y - 1))
                    # Left to D, <, I
                    if x - 1 >= 0 and self.grid[y][x - 1] in ['D', '<', 'I']:
                        G.add_edge((x, y), (x - 1, y))
                    # Right to D, >, I
                    if x + 1 < cols and self.grid[y][x + 1] in ['D', '>', 'I']:
                        G.add_edge((x, y), (x + 1, y))
                    # Up-left to ^
                    if y - 1 >= 0 and x - 1 >= 0 and self.grid[y - 1][x - 1] == '^':
                        G.add_edge((x, y), (x - 1, y - 1))
                    # Down-left to ^
                    if y + 1 < rows and x - 1 >= 0 and self.grid[y + 1][x - 1] == '^':
                        G.add_edge((x, y), (x - 1, y + 1))

                # Rules for 'v'
                if node == 'v':
                    # Down to v, D, I, S
                    if y + 1 < rows and self.grid[y + 1][x] in ['v', 'D', 'I', 'S']:
                        G.add_edge((x, y), (x, y + 1))
                    # Right to >, I, D
                    if x + 1 < cols and self.grid[y][x + 1] in ['>', 'I', 'D']:
                        G.add_edge((x, y), (x + 1, y))
                    # Left to <, I, D
                    if x - 1 >= 0 and self.grid[y][x - 1] in ['<', 'I', 'D']:
                        G.add_edge((x, y), (x - 1, y))

                # Rules for 'S'
                if node == 'S':
                    # Down to v
                    if y + 1 < rows and self.grid[y + 1][x] == 'v':
                        G.add_edge((x, y), (x, y + 1))
                    # Up to ^
                    if y - 1 >= 0 and self.grid[y - 1][x] == '^':
                        G.add_edge((x, y), (x, y - 1))

                # Rules for 's'
                if node == 's':
                    # Right to >
                    if x + 1 < cols and self.grid[y][x + 1] == '>':
                        G.add_edge((x, y), (x + 1, y))
                    # Left to <
                    if x - 1 >= 0 and self.grid[y][x - 1] == '<':
                        G.add_edge((x, y), (x - 1, y))

                if node == 'I':
                    # Up to ^
                    if y - 1 >= 0 and self.grid[y - 1][x] == '^':
                        G.add_edge((x, y), (x, y - 1))
                    # Down to v
                    if y + 1 < rows and self.grid[y + 1][x] == 'v':
                        G.add_edge((x, y), (x, y + 1))
                    # Left to <
                    if x - 1 >= 0 and self.grid[y][x - 1] == '<':
                        G.add_edge((x, y), (x - 1, y))
                    # Right to >
                    if x + 1 < cols and self.grid[y][x + 1] == '>':
                        G.add_edge((x, y), (x + 1, y))

        return G

    def print_adjacency_matrix(self, G):
        adjacency_matrix = nx.adjacency_matrix(G).todense()
        print(adjacency_matrix)

    def find_path(self, start, end):
        G = self.create_graph()
        try:
            path = nx.astar_path(G, start, end, heuristic=self.heuristic)
            return path
        except nx.NetworkXNoPath:
            print("No path found in the graph.")
            return []

    def heuristic(self, a, b):
        # Simple Euclidean distance
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5



    # def create_graph(self):
    #     grid = self.model.grid
    #     G = nx.DiGraph()
    #     rows, cols = self.model.grid.height, self.model.grid.width
        
    #     for y in range(rows):
    #         for x in range(cols):
    #             cell_contents = self.model.grid.get_cell_list_contents((x, y))
    #             node = self.determine_node_type(cell_contents)
                
    #             if node == '#':
    #                 continue 

    #             # Determine valid neighbors for '>'
    #             if node == '>':
    #                 # Right to s, D, >, I
    #                 if x + 1 < cols and self.model.grid[y][x + 1] in ['s', 'D', '>', 'I']:
    #                     G.add_edge((x, y), (x + 1, y))
    #                 # Up to ^, D
    #                 if y - 1 >= 0 and self.model.grid[y - 1][x] in ['^', 'D']:
    #                     G.add_edge((x, y), (x, y - 1))
    #                 # Up-right to >
    #                 if y - 1 >= 0 and x + 1 < cols and self.model.grid[y - 1][x + 1] == '>':
    #                     G.add_edge((x, y), (x + 1, y - 1))
    #                 # Up-left to >
    #                 if y - 1 >= 0 and x - 1 >= 0 and self.model.grid[y - 1][x - 1] == '>':
    #                     G.add_edge((x, y), (x - 1, y - 1))

    #             # Determine valid neighbors for '<'
    #             if node == '<':
    #                 # Left to s, D, <, I
    #                 if x - 1 >= 0 and self.model.grid[y][x - 1] in ['s', 'D', '<', 'I']:
    #                     G.add_edge((x, y), (x - 1, y))
    #                 # Up to ^, D
    #                 if y - 1 >= 0 and self.model.grid[y - 1][x] in ['^', 'D']:
    #                     G.add_edge((x, y), (x, y - 1))
    #                 # Down-left to <
    #                 if y + 1 < rows and x - 1 >= 0 and self.model.grid[y + 1][x - 1] == '<':
    #                     G.add_edge((x, y), (x - 1, y + 1))
    #                 # Down-right to <
    #                 if y + 1 < rows and x + 1 < cols and self.model.grid[y + 1][x + 1] == '<':
    #                     G.add_edge((x, y), (x + 1, y + 1))

    #             if node == '^':
    #                 # Up to ^, D, I, S
    #                 if y - 1 >= 0 and self.model.grid[y - 1][x] in ['^', 'D', 'I', 'S']:
    #                     G.add_edge((x, y), (x, y - 1))
    #                 # Left to D, <, I
    #                 if x - 1 >= 0 and self.model.grid[y][x - 1] in ['D', '<', 'I']:
    #                     G.add_edge((x, y), (x - 1, y))
    #                 # Right to D, >, I
    #                 if x + 1 < cols and self.model.grid[y][x + 1] in ['D', '>', 'I']:
    #                     G.add_edge((x, y), (x + 1, y))
    #                 # Up-left to ^
    #                 if y - 1 >= 0 and x - 1 >= 0 and self.model.grid[y - 1][x - 1] == '^':
    #                     G.add_edge((x, y), (x - 1, y - 1))
    #                 # Down-left to ^
    #                 if y + 1 < rows and x - 1 >= 0 and self.model.grid[y + 1][x - 1] == '^':
    #                     G.add_edge((x, y), (x - 1, y + 1))

    #             # Rules for 'v'
    #             if node == 'v':
    #                 # Down to v, D, I, S
    #                 if y + 1 < rows and self.model.grid[y + 1][x] in ['v', 'D', 'I', 'S']:
    #                     G.add_edge((x, y), (x, y + 1))
    #                 # Right to >, I, D
    #                 if x + 1 < cols and self.model.grid[y][x + 1] in ['>', 'I', 'D']:
    #                     G.add_edge((x, y), (x + 1, y))
    #                 # Left to <, I, D
    #                 if x - 1 >= 0 and self.model.grid[y][x - 1] in ['<', 'I', 'D']:
    #                     G.add_edge((x, y), (x - 1, y))

    #             # Rules for 'S'
    #             if node == 'S':
    #                 # Down to v
    #                 if y + 1 < rows and self.model.grid[y + 1][x] == 'v':
    #                     G.add_edge((x, y), (x, y + 1))
    #                 # Up to ^
    #                 if y - 1 >= 0 and self.model.grid[y - 1][x] == '^':
    #                     G.add_edge((x, y), (x, y - 1))

    #             # Rules for 's'
    #             if node == 's':
    #                 # Right to >
    #                 if x + 1 < cols and self.model.grid[y][x + 1] == '>':
    #                     G.add_edge((x, y), (x + 1, y))
    #                 # Left to <
    #                 if x - 1 >= 0 and self.model.grid[y][x - 1] == '<':
    #                     G.add_edge((x, y), (x - 1, y))

    #             if node == 'I':
    #                 # Up to ^
    #                 if y - 1 >= 0 and self.model.grid[y - 1][x] == '^':
    #                     G.add_edge((x, y), (x, y - 1))
    #                 # Down to v
    #                 if y + 1 < rows and self.model.grid[y + 1][x] == 'v':
    #                     G.add_edge((x, y), (x, y + 1))
    #                 # Left to <
    #                 if x - 1 >= 0 and self.model.grid[y][x - 1] == '<':
    #                     G.add_edge((x, y), (x - 1, y))
    #                 # Right to >
    #                 if x + 1 < cols and self.model.grid[y][x + 1] == '>':
    #                     G.add_edge((x, y), (x + 1, y))

    #     return G