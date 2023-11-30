#Emilia Salazar e Ian Holender
from mesa import Agent
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random



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
        self.threshold = random.uniform(0, 5)
        

    #Esta función se utiliza para asignar el símbolo a la dirección de la calle para poder hacer nuestro grafo correctamente
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
    
    #Esta función regresa si unas coordenadas están dentro del rango de el grid
    def is_within_bounds(x, y, width, height):
        return 0 <= x < width and 0 <= y < height
    

    #Esta función crea el grafo manualmente. Dependiendo de la dirección de la calle o el símbolo, los nodos pueden estar dirigidos a otros nodos. Se dirigen las diagonales y los lados. Igualmente se agrega el peso, para las diagonales 2 y para los lados 1
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

    #Esta función encuentra el camino más corto utilizando A* y el grafo dirigido, dependiendo un punto de inicio y un punto de fin
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

    #Esta función calcula la heurística para A* que en este caso es la distancia euclidiana
    def heuristic(self, a, b):
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    #Esta función determine si un coche se puede mover a una celda. Regresa falso si no se puede mover porque hay un semáforo en rojo o hay un coche en esa celda, y regresa verdadero si si se puede mover. 
    def can_move_to(self, next_position):
        cell_contents = self.model.grid.get_cell_list_contents(next_position)
        for agent in cell_contents:
            if isinstance(agent, Traffic_Light) and not agent.state:
                return False  
            
            if isinstance(agent, Car) and agent is not self:
                return False

        return True

    #Esta función compara la pocisión del coche con la del destino, si son la misma, quita a el agente de la simulación
    def arrived_at_destination(self):
        if self.pos == self.destination_pos:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.CarsReached += 1
            return True

    #Esta función regresa la dirección de un agente de calle en específico 
    def get_current_road_direction(self):
        current_cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in current_cell_contents:
            if isinstance(agent, Road):
                return agent.direction
        return None 
    
    def is_within_bounds(self, position):
        x, y = position
        return 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height
    

    #Esta función determina si un agente se puede mover diagonalmente. Lo que hace es, dependiendo la la dirección de la celda, si a lado no hay coche y en la diagonal no hay coche, se puede mover. Calcula que las diagonales sean nodos y estén dentro de el grid.
    def can_move_diagonally(self):
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
    

    #Esta función regresa cuáles son las posibles diagonales a las que se puede mover un coche
    def get_diagonal_positions(self):
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
    
    #Esta función, dependiendo la dirección del coche ve dos pocisiones adelante. Si es que encuentra en las tres pocisiones un agente coche al mismo tiempo, regresa verdadero. 
    def two_cars_ahead(self):
        current_x, current_y = self.pos
        direction = self.get_current_road_direction()
        positions_to_check = []

        
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
    

    #Esta función, dependiendo de la dirección de la calle, busca los nodos que debe actualizar y les suma el peso. Estos nodos en el caso de la simulación son las pocisiones de los dos coches en frente, esto es para que si es necesario recalcular A*, lo haga sin volver al camino anterior
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

    
    #Esta función, dependiendo de la dirección de la calle, regresa si es que hay un coche a lado del agente
    def get_adjacent_cars(self):
        direction = self.get_current_road_direction()
        current_x, current_y = self.pos
        adjacent_positions = []

        if direction == "Right":
            adjacent_positions = [(current_x, current_y - 1), (current_x, current_y + 1)]
        elif direction == "Left":
            adjacent_positions = [(current_x, current_y - 1), (current_x, current_y + 1)]
        elif direction == "Up":
            adjacent_positions = [(current_x - 1, current_y), (current_x + 1, current_y)]
        elif direction == "Down":
            adjacent_positions = [(current_x - 1, current_y), (current_x + 1, current_y)]

        adjacent_cars = []
        for position in adjacent_positions:
            if self.is_within_bounds(position):
                cell_contents = self.model.grid.get_cell_list_contents(position)
                for agent in cell_contents:
                    if isinstance(agent, Car):
                        adjacent_cars.append(agent)

        return adjacent_cars

    
    #Esta pocisión regresa el siguiente movimiento planeado de un agente
    def get_next_move(self):
        if self.path and len(self.path) > 0:
            return self.path[0]
        return None
    
    #Esta función regresa la posible siguiente diagonal de un agente
    def get_next_diagonal_move(self):
        direction = self.get_current_road_direction()
        current_x, current_y = self.pos
        if direction == "Right":
            return (current_x + 1, current_y + 1), (current_x + 1, current_y - 1)
        elif direction == "Left":
            return (current_x - 1, current_y + 1), (current_x - 1, current_y - 1)
        elif direction == "Up":
            return (current_x + 1, current_y + 1), (current_x - 1, current_y + 1)
        elif direction == "Down":
            return (current_x - 1, current_y - 1), (current_x + 1, current_y - 1)

        return []
    
    #Esta funcipon regresa la pocisión de enfrente de un agente
    def get_next_front_move(self):
        direction = self.get_current_road_direction()
        current_x, current_y = self.pos

        if direction == "Right":
            return (current_x + 1, current_y)
        elif direction == "Left":
            return (current_x - 1, current_y)
        elif direction == "Up":
            return (current_x, current_y + 1)
        elif direction == "Down":
            return (current_x, current_y - 1)

        return None
    
    #Esta función regresa si es que un agente a lado de mi planea moverse a mi diagoal y yo planeo moverme a su diagonal
    def is_diagonal_intersection(self, adjacent_car):
        my_next_diagonal_moves = self.get_next_diagonal_move() or []
        their_next_diagonal_moves = adjacent_car.get_next_diagonal_move() or []

        my_current_front_position = self.get_next_front_move() or None
        their_current_front_position = adjacent_car.get_next_front_move() or None

        if my_current_front_position and their_current_front_position:
            if my_current_front_position in their_next_diagonal_moves and their_current_front_position in my_next_diagonal_moves:
                return True

        return False


    
    def move(self):
        #Si estas en una congestión de tráfico y haz estado parado durante 11 pasos, tomas cualquier celda vacía que tu nodo esté direccionado a ella y recalculas A*, esto es para liberar las congestiones de tráfico.
        if self.stationary_steps >= 11:
            for neighbor in self.graph.neighbors(self.pos):
                if (self.can_move_to(neighbor) and
                    self.is_within_bounds(neighbor) and
                    self.graph.has_edge(self.pos, neighbor)):
                    self.model.grid.move_agent(self, neighbor)
                    self.path = self.find_path(neighbor, self.destination_pos)
                    self.stationary_steps = 0  
                    return
        if self.path is None or len(self.path) == 0:
            self.path = self.find_path(self.pos, self.destination_pos)

        if self.path and len(self.path) > 0:
            next_position = self.path[0]
            #Si te puedes mover y no tienes dos coches en frente, buscas si tienes un coche a lado. Si si lo tienes y van a tener una intersección de diagonales, buscas si tu threshold que es un número random del 1 al 5 inicializado al principio es menor que el del otro agente. Si es menor te esperas a que el se mueva, si es mayor tú te mueves. Si tienen el mismo threshold el que se inicializó primero avanza primero. Esto es para que los agentes no se crucen entre ellos
            if self.can_move_to(next_position) and not self.two_cars_ahead():
                adjacent_cars = self.get_adjacent_cars()
                for adjacent_car in adjacent_cars:
                    if self.is_diagonal_intersection(adjacent_car):
                        if self.threshold < adjacent_car.threshold:
                            return  
                        elif self.threshold == adjacent_car.threshold:
                            if self.unique_id < adjacent_car.unique_id:
                                self.model.grid.move_agent(self, next_position)
                                self.path.pop(0)
                                return 
                            else:
                                self.stationary_steps += 1
                                self.path = self.find_path(self.pos, self.destination_pos)
                                return 
                #Si no tienes un agente a lado con el que vas a tener una intersección diagonal, avanzas normalmente
                self.model.grid.move_agent(self, next_position)
                self.path.pop(0)
                self.stationary_steps = 0  
 
            else:
                self.stationary_steps += 1
                #Si tienes dos coches a delante, buscas moverte a una diagonal que sea un nodo dentro del grafo y estés conectado a esa diagonal, esto es para evitar que la diagonal sea en sentido contrario o a un nodo no dirigido. Si es que si te puedes mover a la diagonal, actualizas los pesos del grafo agregando 30 puntos a los nodos de las dos pocisiones en frente de ti y después te mueves a la diagonal. una vez en la diagonal recalculas A*
                if self.two_cars_ahead():
                    print(f"Car {self.unique_id} found 2 cars ahead, checking for diagonal move.")
                    diagonal_positions = self.get_diagonal_positions()
                    for diag_pos in diagonal_positions:
                        if self.is_within_bounds(diag_pos) and self.can_move_diagonally() and self.can_move_to(diag_pos) and self.graph.has_node(diag_pos) and self.graph.has_edge(self.pos, diag_pos):
                            self.update_graph_weights_due_to_congestion()
                            self.model.grid.move_agent(self, diag_pos)
                            print(f"Car {self.unique_id} moved diagonally to {diag_pos}")
                            self.path = self.find_path(diag_pos, self.destination_pos)
                            self.stationary_steps = 0
                            break
                        else:
                            print(f"Diagonal move to {diag_pos} not possible for Car {self.unique_id}.")
                            self.path = self.find_path(self.pos, self.destination_pos)
                            self.stationary_steps = 0   



    #Aquí te mueves 
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

    #Dependiendo de tu símbolo de semáforo, si uno es verdadero el otro es falso y viceversa
    def toggle_traffic_lights(self, light_type):
        previous_state = self.traffic_light_states[light_type]
        if light_type == 'S':
            self.traffic_light_states['S'] = not self.traffic_light_states['S']
            self.traffic_light_states['s'] = not self.traffic_light_states['S']
        elif light_type == 's':
            self.traffic_light_states['s'] = not self.traffic_light_states['s']
            self.traffic_light_states['S'] = not self.traffic_light_states['s']

       

    def step(self):
        #Cambia cada tiempo determinado
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
