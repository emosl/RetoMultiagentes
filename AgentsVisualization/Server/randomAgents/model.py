from mesa import Model
import random
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from randomAgents.agent import *
import json
import requests



class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, number_agents):


        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []


        with open('city_files/2023_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            print("Grid dimensions:", self.width, self.height)
            
            self.schedule = RandomActivation(self)
            self.I_locations = []
            self.D_locations = []
            self.CarsReached = 0
        


            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    elif col == "I":
                        agent = Initialization(f"I_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.I_locations.append((c, self.height - r - 1))


                    elif col == "S":
                        agent = Traffic_Light(f"tl_S{r*self.width+c}", self, False, int(dataDictionary[col]), "S")
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)
                    elif col == "s":
                        agent = Traffic_Light(f"tl_s{r*self.width+c}", self, True, int(dataDictionary[col]), "s")
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.D_locations.append((c, self.height - r - 1))
        
        
        self.num_agents = 0
        self.running = True
        self.step_count = 0
        self.initialize_car()
        
    def is_grid_filled(self):
        car_count = 0

        for contents in self.grid.coord_iter():
            cell_contents = contents[0]
            if any(isinstance(agent, Car) for agent in cell_contents):
                car_count += 1

        return car_count == 367

            
    def is_cell_occupied(self, pos):
        """
        Check if a given cell in the grid is occupied by a Car.
        """
        this_cell = self.grid.get_cell_list_contents(pos)
        return any(isinstance(agent, Car) for agent in this_cell)

        


    def initialize_car(self):
        if self.I_locations and self.D_locations:
            available_I_locations = [loc for loc in self.I_locations if not self.is_cell_occupied(loc)]
            if available_I_locations:
                random_I_location = random.choice(available_I_locations)
                random_D_location = random.choice(self.D_locations)
                car_agent = Car(1000 + self.num_agents, self, random_D_location)  
                self.grid.place_agent(car_agent, random_I_location)
                self.schedule.add(car_agent)
                self.num_agents += 1
            else:
                print("No available initialization locations.")
            



    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1  
        ("STEP MODEL", self.step_count)
        print("NUMBER OF AGENTS: ", self.num_agents)
        
        if self.step_count % 3 == 0:
            for i in range(min(4, len(self.I_locations))):
                available_I_locations = [loc for loc in self.I_locations if not self.is_cell_occupied(loc)]
                if available_I_locations:
                    I_location = random.choice(available_I_locations)
                    random_D_location = random.choice(self.D_locations)
                    car_agent = Car(1000 + self.num_agents, self, random_D_location)  
                    self.grid.place_agent(car_agent, I_location)
                    self.schedule.add(car_agent)
                    self.num_agents += 1
                else:
                    print("No available initialization locations for new cars.")

        if self.is_grid_filled():
            self.running = False
            print("Simulation stopped: Grid is filled.")
            return

            

        if(self.schedule.steps%100 == 0):
            ##mandar coches al api

            url = "http://52.1.3.19:8585/api/"
            endpoint = "validate_attempt"


            data = {
                "year" : 2023,
                "classroom" : 302,
                "name" : "Equipo 6",
                "num_cars": self.CarsReached
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)
            print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
            # print("Response:", response.text())
            print("mandar coches")
            # if self.shedule.steps % 100== 0:
            #     ##Mandar los coches al api
            #     print("mandar coches")
