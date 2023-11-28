from mesa import Model
import random
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from randomAgents.agent import *
import json


class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, number_agents):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2023_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            print("Grid dimensions:", self.width, self.height)
            
            self.schedule = RandomActivation(self)
            self.I_locations = []
            self.D_locations = []
            # self.num_agents = number_agents


            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    elif col == "I":
                        agent = Initialization(f"I_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.I_locations.append((c, self.height - r - 1))

                    # elif col in ["S", "s"]:
                    #     agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                    #     self.grid.place_agent(agent, (c, self.height - r - 1))
                    #     self.schedule.add(agent)
                    #     self.traffic_lights.append(agent)

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
        
        

        


    def initialize_car(self):
        if self.I_locations and self.D_locations:
            random_I_location = random.choice(self.I_locations)
            random_D_location = random.choice(self.D_locations)
            car_agent = Car(1000 + self.num_agents, self, random_D_location)  
            self.grid.place_agent(car_agent, random_I_location)
            self.schedule.add(car_agent)
            self.num_agents += 1
            



    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1  
        # self.initialize_car()
        ("STEP MODEL", self.step_count)
        print("NUMBER OF AGENTS: ", self.num_agents)
        
        if self.step_count % 5 == 0:
            for i in range(4):
                if self.I_locations:
                    I_location = self.I_locations[i]
                    random_D_location = random.choice(self.D_locations)
                    car_agent = Car(1000 + self.num_agents, self, random_D_location)  
                    self.grid.place_agent(car_agent, I_location)
                    self.schedule.add(car_agent)
                    self.num_agents += 1
