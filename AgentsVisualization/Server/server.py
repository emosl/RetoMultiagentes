# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git

from flask import Flask, request, jsonify
from randomAgents.model import CityModel
print("CityModel:", CityModel)
from randomAgents.agent import Car, Traffic_Light
print("Car Agent:", Car)

# Size of the board:
number_agents = 0
# CityModel = None
currentStep = 0



app = Flask("Traffic example")

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global currentStep, randomModel, number_agents

    if request.method == 'POST':
        print("Received form data:", request.form)
        number_agents = int(request.form.get('NAgents'))
        currentStep = 0

        print(request.form)
        print(number_agents)
        print("Initializing CityModel...")
        randomModel = CityModel(number_agents)
        print("CityModel initialized successfully")
        


        return jsonify({"message":"Parameters recieved, model initiated."})
    elif request.method == 'GET':
        number_agents = 0
        currentStep = 0
        randomModel = CityModel(number_agents)

        return jsonify({"message":"Default parameters recieved, model initiated."})



@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        agentPositions = [
            {
                "id": str(agent.unique_id), 
                "x": x, 
                "y": 0, 
                "z": z,
                "hasArrived": agent.arrived_at_destination()  
            } 
            for (contents, (x, z)) in randomModel.grid.coord_iter() 
            for agent in contents if isinstance(agent, Car)
        ]

        return jsonify({'positions': agentPositions})




@app.route('/getTrafficLights', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        carPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z}
                        for a, (x, z) in randomModel.grid.coord_iter()
                        if isinstance(a, Traffic_Light)]

        return jsonify({'positions':carPositions})


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        print("STEP", currentStep)
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)
