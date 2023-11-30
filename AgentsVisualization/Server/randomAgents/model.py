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
