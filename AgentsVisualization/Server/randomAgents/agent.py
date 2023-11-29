from mesa import Agent
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

class Car(Agent):
    """
    Agent that moves using the A* algorithm.
    """

    def __init__(self, unique_id, model, destination_pos):
        """
        Creates a new car agent.
        """
        super().__init__(unique_id, model)
        self.destination_pos = destination_pos 
        self.path = None  
        self.graph = self.create_graph()
        self.stationary_steps = 0



    def plot_graph(self, graph):
        pos = {node: (node[0], -node[1]) for node in graph.nodes}  # Flip y-axis for visualization
        nx.draw(graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_color='black')
        plt.show()

    def determine_node_type(self, cell_contents):
        node_type = ' '  

        for agent in cell_contents:
            if isinstance(agent, Obstacle):
                return '#'  
            elif isinstance(agent, Road):
                
                if agent.direction == "Right":
                    return '>'
                elif agent.direction == "Left":
                    return '<'
                elif agent.direction == "Up":
                    return '^'
                elif agent.direction == "Down":
                    return 'v'
            elif isinstance(agent, Initialization):
                return "I"
            elif isinstance(agent, Destination):
                return "D"
            elif isinstance(agent, Traffic_Light):
                if agent.unique_id.startswith("tl_S"):
                    node_type = 'S'  
                elif agent.unique_id.startswith("tl_s"):
                    node_type = 's'

        return node_type
    
    def is_within_bounds(x, y, width, height):
        return 0 <= x < width and 0 <= y < height
    
    def create_graph(self):
        grid = self.model.grid

        G = nx.DiGraph()
        rows, cols = grid.height, grid.width


        for y in range(rows):
            for x in range(cols):
                
                cell_contents = grid.get_cell_list_contents([(x, y)])
                node = self.determine_node_type(cell_contents)
                

                if node == '>':
                    # Right to s, D, >, I
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['s', 'D', '>', 'I','^' ]:
                            G.add_edge((x, y), (x + 1, y), weight = 1)

                    # Up to ^, D
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D']:
                            G.add_edge((x, y), (x, y + 1), weight = 1)

                    if y - 1 > 0:
                        up_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['v', 'D', "I"]:
                            G.add_edge((x, y), (x, y - 1), weight = 1)

                    # Up-right to >
                    if y - 1 >= 0 and x + 1 < cols:
                        up_right_cell_contents = grid.get_cell_list_contents([(x + 1, y - 1)])
                        up_right_node = self.determine_node_type(up_right_cell_contents)
                        if up_right_node == '>':
                            G.add_edge((x, y), (x + 1, y - 1), weight =  2)

                    # Up-left to >
                    if y + 1 < rows and x + 1 < cols:
                        up_left_cell_contents = grid.get_cell_list_contents([(x + 1, y + 1)])
                        up_left_node = self.determine_node_type(up_left_cell_contents)
                        if up_left_node == '>':
                            G.add_edge((x, y), (x + 1, y + 1), weight = 2)

                    
                    

                # Check for '<'
                if node == '<':
                    # Left to s, D, <, I
                    if x - 1 >= 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['s', 'D', '<', 'I', "v"]:
                            G.add_edge((x, y), (x - 1, y), weight = 1)

                    # Up to ^, D
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D']:
                            G.add_edge((x, y), (x, y + 1), weight = 1)
                    
                    if y - 1 > 0:
                        up_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['v', 'D']:
                            G.add_edge((x, y), (x, y - 1), weight = 1)

                    # Down-left to <
                    if y + 1 < rows and x - 1 > 0:
                        down_left_cell_contents = grid.get_cell_list_contents([(x - 1, y + 1)])
                        down_left_node = self.determine_node_type(down_left_cell_contents)
                        if down_left_node == '<':
                            G.add_edge((x, y), (x - 1, y + 1), weight = 2)

                    # Down-right to <
                    if y - 1 > 0 and x - 1 > 0:
                        down_right_cell_contents = grid.get_cell_list_contents([(x - 1, y - 1)])
                        down_right_node = self.determine_node_type(down_right_cell_contents)
                        if down_right_node == '<':
                            G.add_edge((x, y), (x - 1, y - 1), weight = 2)


                # Check for '^'
                if node == '^':
                    # Up to ^, D, I, S
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D', 'I', 'S', "<", ">"]:
                            G.add_edge((x, y), (x, y + 1), weight = 1)

                    # Left to D, <, I
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['D', '<', 'I']:
                            G.add_edge((x, y), (x - 1, y), weight = 2)

                    # Right to D, >, I
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['D', '>', 'I']:
                            G.add_edge((x, y), (x + 1, y), weight = 1)

                    # Up-left to ^
                    if y + 1  < rows and x + 1 < cols:
                        up_left_cell_contents = grid.get_cell_list_contents([(x + 1, y + 1)])
                        up_left_node = self.determine_node_type(up_left_cell_contents)
                        if up_left_node == '^':
                            G.add_edge((x, y), (x + 1, y + 1), weight = 2)

                    # Down-left to ^
                    if y + 1 < rows and x - 1 > 0:
                        down_left_cell_contents = grid.get_cell_list_contents([(x - 1, y + 1)])
                        down_left_node = self.determine_node_type(down_left_cell_contents)
                        if down_left_node == '^':
                            G.add_edge((x, y), (x - 1, y + 1), weight = 2)



                if node == 'v':
                    # Down to v, D, I, S
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node in ['v', 'D', 'I', 'S', ">", "<"]:
                            G.add_edge((x, y), (x, y - 1), weight = 1)

                    # Right to >, I, D
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['>', 'I', 'D']:
                            G.add_edge((x, y), (x + 1, y), weight = 1)

                    # Left to <, I, D
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['<', 'I', 'D']:
                            G.add_edge((x, y), (x - 1, y) , weight = 1)
                    
                    if y - 1 > 0 and x - 1 >= 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y-1)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == 'v':
                            G.add_edge((x, y), (x - 1, y-1), weight = 2)

                    if y - 1 > 0 and x + 1 < cols:
                        left_cell_contents = grid.get_cell_list_contents([(x + 1, y-1)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == 'v':
                            G.add_edge((x, y), (x + 1, y-1), weight = 2)


                # Check for 'S'
                if node == 'S':
                    # Down to v
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node in ['v', ">"]:
                            G.add_edge((x, y), (x, y - 1), weight = 1)

                    # Up to ^
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', "<"]:
                            G.add_edge((x, y), (x, y + 1), weight = 1)

                # Check for 's'
                if node == 's':
                    # Right to >
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['>', '^', "v"]:
                            G.add_edge((x, y), (x + 1, y), weight = 1)

                    # Left to <
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in  ['<', '^', "v"]:
                            G.add_edge((x, y), (x - 1, y), weight = 1)

                # Check for 'I'
                if node == 'I':
                    # Up to ^
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node == '^':
                            G.add_edge((x, y), (x, y + 1), weight = 1)

                    # Down to v
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node == 'v':
                            G.add_edge((x, y), (x, y - 1), weight = 1)

                    # Left to <
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == '<':
                            G.add_edge((x, y), (x - 1, y), weight = 1)

                    # Right to >
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node == '>':
                            G.add_edge((x, y), (x + 1, y), weight = 1)

        return G
    


    def print_adjacency_matrix(self, G):
        adjacency_matrix = nx.adjacency_matrix(G).todense()
        print(adjacency_matrix)

    def find_path(self, start, end):
        G = self.graph
        start_node_type = self.determine_node_type(self.model.grid.get_cell_list_contents([start]))
        end_node_type = self.determine_node_type(self.model.grid.get_cell_list_contents([end]))
        
        print("Start Node Type:", start_node_type)
        print("End Node Type:", end_node_type)
        print("Start Node:", start)
        print("End Node:", end)


        try:
            path = nx.astar_path(G, start, end, heuristic=self.heuristic)
            print(path)
            return path
        except nx.NetworkXNoPath:
            print("No path found in the graph.")
            return []

    def heuristic(self, a, b):
        # Simple Euclidean distance
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    def can_move_to(self, next_position):
        """
        Checks if the car can move to the next position. Returns True if it can, False otherwise.
        """
        cell_contents = self.model.grid.get_cell_list_contents(next_position)
        for agent in cell_contents:
            if isinstance(agent, Traffic_Light) and not agent.state:
                return False  
            
            if isinstance(agent, Car) and agent is not self:
                return False

        return True

    def arrived_at_destination(self):
        if self.pos == self.destination_pos:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            return True
        
    def get_current_road_direction(self):
        """
        Returns the direction of the Road agent on which the car is currently located.
        """
        current_cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in current_cell_contents:
            if isinstance(agent, Road):
                return agent.direction
        return None 
    
    def is_within_bounds(self, position):
        """
        Checks if the given position is within the bounds of the grid.
        """
        x, y = position
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height
    
    def can_move_diagonally(self):
        """
        Checks if the car can move diagonally based on its current direction.
        """
        current_x, current_y = self.pos
        direction = self.get_current_road_direction()
        diagonal_pos1 = None
        diagonal_pos2 = None
        side_pos1 = None
        side_pos2 = None

        if direction == "Right":
            diagonal_pos1 = (current_x + 1, current_y - 1)
            diagonal_pos2 = (current_x + 1, current_y + 1)
            side_pos1 = (current_x, current_y - 1)
            side_pos2 = (current_x, current_y + 1)
        elif direction == "Left":
            diagonal_pos1 = (current_x - 1, current_y - 1)
            diagonal_pos2 = (current_x - 1, current_y + 1)
            side_pos1 = (current_x, current_y - 1)
            side_pos2 = (current_x, current_y + 1)
        elif direction == "Up":
            diagonal_pos1 = (current_x - 1, current_y + 1)
            diagonal_pos2 = (current_x + 1, current_y + 1)
            side_pos1 = (current_x - 1, current_y)
            side_pos2 = (current_x + 1, current_y)
        elif direction == "Down":
            diagonal_pos1 = (current_x - 1, current_y - 1)
            diagonal_pos2 = (current_x + 1, current_y - 1)
            side_pos1 = (current_x - 1, current_y)
            side_pos2 = (current_x + 1, current_y)
        else:
            return False 

        if ((self.is_within_bounds(diagonal_pos1) and self.graph.has_node(diagonal_pos1) and self.can_move_to(diagonal_pos1) and
            self.is_within_bounds(side_pos1) and self.graph.has_node(side_pos1) and self.can_move_to(side_pos1)) or
            (self.is_within_bounds(diagonal_pos2) and self.graph.has_node(diagonal_pos2) and self.can_move_to(diagonal_pos2) and
            self.is_within_bounds(side_pos2) and self.graph.has_node(side_pos2) and self.can_move_to(side_pos2))):
            return True


        return False
    
    def get_diagonal_positions(self):
        """
        Returns a list of possible diagonal positions based on the current direction.
        """
        current_x, current_y = self.pos
        direction = self.get_current_road_direction()
        diagonal_positions = []

        if direction == "Right":
            diagonal_positions.append((current_x + 1, current_y - 1))
            diagonal_positions.append((current_x + 1, current_y + 1))
        elif direction == "Left":
            diagonal_positions.append((current_x - 1, current_y + 1))
            diagonal_positions.append((current_x - 1, current_y - 1))
        elif direction == "Up":
            diagonal_positions.append((current_x - 1, current_y + 1))
            diagonal_positions.append((current_x + 1, current_y + 1))
        elif direction == "Down":
            diagonal_positions.append((current_x + 1, current_y - 1))
            diagonal_positions.append((current_x - 1, current_y - 1))

        return diagonal_positions
    
    def three_cars_ahead(self):
        current_x, current_y = self.pos
        direction = self.get_current_road_direction()
        positions_to_check = []

        # Calculate the three positions ahead based on the current direction
        if direction == "Right":
            positions_to_check = [(current_x + i, current_y) for i in range(1, 3)]
        elif direction == "Left":
            positions_to_check = [(current_x - i, current_y) for i in range(1, 3)]
        elif direction == "Up":
            positions_to_check = [(current_x, current_y + i) for i in range(1, 3)]
        elif direction == "Down":
            positions_to_check = [(current_x, current_y - i) for i in range(1, 3)]

        car_count = 0  
        for position in positions_to_check:
            if not self.is_within_bounds(position):
                continue 
            cell_contents = self.model.grid.get_cell_list_contents(position)
            if any(isinstance(agent, Car) for agent in cell_contents):
                car_count += 1  # Increment counter for each car found
        print(f"Car {self.unique_id} detected {car_count} cars ahead.")
        return car_count == 2 
    
    def update_graph_weights_due_to_congestion(self):
        current_x, current_y = self.pos
        direction = self.get_current_road_direction()
        positions_to_update = []

        if direction == "Right":
            positions_to_update = [(current_x + i, current_y) for i in range(1, 3)]
        elif direction == "Left":
            positions_to_update = [(current_x - i, current_y) for i in range(1, 3)]
        elif direction == "Up":
            positions_to_update = [(current_x, current_y + i) for i in range(1, 3)]
        elif direction == "Down":
            positions_to_update = [(current_x, current_y - i) for i in range(1, 3)]

        for position in positions_to_update:
            if self.graph.has_node(position):
                for neighbor in self.graph.predecessors(position):
                    if self.graph.has_edge(neighbor, position):
                        self.graph[neighbor][position]['weight'] += 30




    def move(self):
        """
        Moves the car along the path determined by A*.
        Recalculates the path if blocked and moves diagonally if necessary.
        """
        
        if self.path is None or len(self.path) == 0:
            self.path = self.find_path(self.pos, self.destination_pos)
           
        if self.path and len(self.path) > 0:
            next_position = self.path[0]  # Get the next position
            if self.can_move_to(next_position) and not self.three_cars_ahead():
                self.model.grid.move_agent(self, next_position)
                self.path.pop(0) 
                
            else:
                self.stationary_steps += 1  
                if self.three_cars_ahead():
                    print(f"Car {self.unique_id} found 2 cars ahead, checking for diagonal move.")
                    diagonal_positions = self.get_diagonal_positions()
                    for diag_pos in diagonal_positions:
                        if self.is_within_bounds(diag_pos) and self.can_move_diagonally() and self.can_move_to(diag_pos) and self.graph.has_node(diag_pos):
                            self.update_graph_weights_due_to_congestion()
                            self.model.grid.move_agent(self, diag_pos)
                            print(f"Car {self.unique_id} moved diagonally to {diag_pos}")
                            print("PATH BEFORE", self.path)  
                            self.path = self.find_path(diag_pos, self.destination_pos)
                            print("PATH AFTER", self.path)
                            self.stationary_steps = 0  
                            break
                        else:
                            print(f"Diagonal move to {diag_pos} not possible for Car {self.unique_id}.")
                            self.path = self.find_path(self.pos, self.destination_pos)
                            if not self.path:
                                print(f"Car {self.unique_id} is unable to move and cannot find a new path.")
                            self.stationary_steps = 0   



    def step(self):
        """
        Determines the new path using A* and moves along it.
        """
        if self.pos != self.destination_pos:
            self.move()
        else:
            self.arrived_at_destination()


class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10, light_type = "S"):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.light_type = light_type
        self.timeToChange = timeToChange
        self.traffic_light_states = {'S': False, 's': True}

    def toggle_traffic_lights(self, light_type):
        previous_state = self.traffic_light_states[light_type]
        if light_type == 'S':
            self.traffic_light_states['S'] = not self.traffic_light_states['S']
            self.traffic_light_states['s'] = not self.traffic_light_states['S']
        elif light_type == 's':
            self.traffic_light_states['s'] = not self.traffic_light_states['s']
            self.traffic_light_states['S'] = not self.traffic_light_states['s']

       

    def step(self):
        if self.model.schedule.steps % self.timeToChange == 0:
            self.toggle_traffic_lights(self.light_type)
            self.state = self.traffic_light_states[self.light_type]

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Initialization(Agent):
    """
    Initialization agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
