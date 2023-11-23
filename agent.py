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
        self.destination_pos = destination_pos  # The destination position for the car  
        self.path = None  # This will store the path the car needs to follow
        # G = self.create_graph()

        # self.plot_graph(G)

    def plot_graph(self, graph):
        pos = {node: (node[0], -node[1]) for node in graph.nodes}  # Flip y-axis for visualization
        nx.draw(graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_color='black')
        plt.show()

    def determine_node_type(self, cell_contents):
        node_type = ' '  # Default node type (empty or non-blocking)

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
                            G.add_edge((x, y), (x + 1, y))

                    # Up to ^, D
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D']:
                            G.add_edge((x, y), (x, y + 1))

                    if y - 1 > 0:
                        up_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['v', 'D', "I"]:
                            G.add_edge((x, y), (x, y - 1))

                    # Up-right to >
                    if y - 1 >= 0 and x + 1 < cols:
                        up_right_cell_contents = grid.get_cell_list_contents([(x + 1, y - 1)])
                        up_right_node = self.determine_node_type(up_right_cell_contents)
                        if up_right_node == '>':
                            G.add_edge((x, y), (x + 1, y - 1))

                    # Up-left to >
                    if y + 1 < rows and x + 1 < cols:
                        up_left_cell_contents = grid.get_cell_list_contents([(x + 1, y + 1)])
                        up_left_node = self.determine_node_type(up_left_cell_contents)
                        if up_left_node == '>':
                            G.add_edge((x, y), (x + 1, y + 1))

                    
                    

                # Check for '<'
                if node == '<':
                    # Left to s, D, <, I
                    if x - 1 >= 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['s', 'D', '<', 'I', "v"]:
                            G.add_edge((x, y), (x - 1, y))

                    # Up to ^, D
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D']:
                            G.add_edge((x, y), (x, y + 1))
                    
                    if y - 1 > 0:
                        up_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['v', 'D']:
                            G.add_edge((x, y), (x, y - 1))

                    # Down-left to <
                    if y + 1 < rows and x - 1 > 0:
                        down_left_cell_contents = grid.get_cell_list_contents([(x - 1, y + 1)])
                        down_left_node = self.determine_node_type(down_left_cell_contents)
                        if down_left_node == '<':
                            G.add_edge((x, y), (x - 1, y + 1))

                    # Down-right to <
                    if y - 1 > 0 and x - 1 > 0:
                        down_right_cell_contents = grid.get_cell_list_contents([(x - 1, y - 1)])
                        down_right_node = self.determine_node_type(down_right_cell_contents)
                        if down_right_node == '<':
                            G.add_edge((x, y), (x - 1, y - 1))


                # Check for '^'
                if node == '^':
                    # Up to ^, D, I, S
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', 'D', 'I', 'S', "<", ">"]:
                            G.add_edge((x, y), (x, y + 1))

                    # Left to D, <, I
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['D', '<', 'I']:
                            G.add_edge((x, y), (x - 1, y))

                    # Right to D, >, I
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['D', '>', 'I']:
                            G.add_edge((x, y), (x + 1, y))

                    # Up-left to ^
                    if y + 1  < rows and x + 1 < cols:
                        up_left_cell_contents = grid.get_cell_list_contents([(x + 1, y + 1)])
                        up_left_node = self.determine_node_type(up_left_cell_contents)
                        if up_left_node == '^':
                            G.add_edge((x, y), (x + 1, y + 1))

                    # Down-left to ^
                    if y + 1 < rows and x - 1 > 0:
                        down_left_cell_contents = grid.get_cell_list_contents([(x - 1, y + 1)])
                        down_left_node = self.determine_node_type(down_left_cell_contents)
                        if down_left_node == '^':
                            G.add_edge((x, y), (x - 1, y + 1))



                if node == 'v':
                    # Down to v, D, I, S
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node in ['v', 'D', 'I', 'S', ">", "<"]:
                            G.add_edge((x, y), (x, y - 1))

                    # Right to >, I, D
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['>', 'I', 'D']:
                            G.add_edge((x, y), (x + 1, y))

                    # Left to <, I, D
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in ['<', 'I', 'D']:
                            G.add_edge((x, y), (x - 1, y))
                    
                    if y - 1 > 0 and x - 1 >= 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y-1)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == 'v':
                            G.add_edge((x, y), (x - 1, y-1))

                    if y - 1 > 0 and x + 1 < cols:
                        left_cell_contents = grid.get_cell_list_contents([(x + 1, y-1)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == 'v':
                            G.add_edge((x, y), (x + 1, y-1))


                # Check for 'S'
                if node == 'S':
                    # Down to v
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node in ['v', ">"]:
                            G.add_edge((x, y), (x, y - 1))

                    # Up to ^
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node in ['^', "<"]:
                            G.add_edge((x, y), (x, y + 1))

                # Check for 's'
                if node == 's':
                    # Right to >
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node in ['>', '^', "v"]:
                            G.add_edge((x, y), (x + 1, y))

                    # Left to <
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node in  ['<', '^', "v"]:
                            G.add_edge((x, y), (x - 1, y))

                # Check for 'I'
                if node == 'I':
                    # Up to ^
                    if y + 1 < rows:
                        up_cell_contents = grid.get_cell_list_contents([(x, y + 1)])
                        up_node = self.determine_node_type(up_cell_contents)
                        if up_node == '^':
                            G.add_edge((x, y), (x, y + 1))

                    # Down to v
                    if y - 1 > 0:
                        down_cell_contents = grid.get_cell_list_contents([(x, y - 1)])
                        down_node = self.determine_node_type(down_cell_contents)
                        if down_node == 'v':
                            G.add_edge((x, y), (x, y - 1))

                    # Left to <
                    if x - 1 > 0:
                        left_cell_contents = grid.get_cell_list_contents([(x - 1, y)])
                        left_node = self.determine_node_type(left_cell_contents)
                        if left_node == '<':
                            G.add_edge((x, y), (x - 1, y))

                    # Right to >
                    if x + 1 < cols:
                        right_cell_contents = grid.get_cell_list_contents([(x + 1, y)])
                        right_node = self.determine_node_type(right_cell_contents)
                        if right_node == '>':
                            G.add_edge((x, y), (x + 1, y))

        return G
    


    def print_adjacency_matrix(self, G):
        adjacency_matrix = nx.adjacency_matrix(G).todense()
        print(adjacency_matrix)

    def find_path(self, start, end):
        G = self.create_graph()
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
                return False  # Cannot move if there's a red traffic light
            
            if isinstance(agent, Car) and agent is not self:
                print(f"Car {self.unique_id} at {self.pos}: Encountered another Car at {next_position}")
                return False

        return True

    
    def arrived_at_destination(self):
        if self.pos == self.destination_pos:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


    def move(self):
        """
        Moves the car along the path determined by A*.
        """
        if self.path is None or len(self.path) == 0:
            self.path = self.find_path(self.pos, self.destination_pos)

        if self.path and len(self.path) > 0:
            next_position = self.path[0]  # Get the next position
            if self.can_move_to(next_position):
                self.path.pop(0)  # Remove the next position from the path
                self.model.grid.move_agent(self, next_position)

    def step(self):
        """
        Determines the new path using A* and moves along it.
        """
        
        # G = self.create_graph()

        # # Print the directed edges
        # for edge in G.edges():
        #     source, target = edge
        #     print(f"Node {source} directed to Node {target}")
        
        
        
        if self.pos == self.destination_pos:
            self.arrived_at_destination()
        else:
            self.move()


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
        # Toggle the state of the specified light type
        previous_state = self.traffic_light_states[light_type]
        if light_type == 'S':
            self.traffic_light_states['S'] = not self.traffic_light_states['S']
            self.traffic_light_states['s'] = not self.traffic_light_states['S']
        elif light_type == 's':
            self.traffic_light_states['s'] = not self.traffic_light_states['s']
            self.traffic_light_states['S'] = not self.traffic_light_states['s']

        # print(f"Traffic Light '{light_type}' state changed from {previous_state} to {self.traffic_light_states[light_type]}")
        # print(f"Current States - S: {self.traffic_light_states['S']}, s: {self.traffic_light_states['s']}")
        

    def step(self):
        if self.model.schedule.steps % self.timeToChange == 0:
            # Toggle the state of this type of light
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
