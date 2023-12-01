# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Servidor Python Flask para interactuar con Unity. Basado en el código proporcionado por Sergio Ruiz.
# Octavio Navarro. Octubre 2023

#Emilia Salazar e Ian holender
from flask import Flask, request, jsonify
from randomAgents.model import CityModel
print("CityModel:", CityModel)
from randomAgents.agent import Car, Traffic_Light
print("Car Agent:", Car)

# Tamaño del tablero:
number_agents = 0
currentStep = 0

app = Flask("Traffic example") # Creación de la aplicación Flask.

@app.route('/init', methods=['GET', 'POST'])
def initModel():
    global currentStep, randomModel, number_agents

    if request.method == 'POST':
        # Inicialización del modelo con datos recibidos mediante POST.
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
        # Inicialización del modelo con parámetros por defecto.
        number_agents = 0
        currentStep = 0
        randomModel = CityModel(number_agents)

        return jsonify({"message":"Default parameters recieved, model initiated."})



@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        # Obtención de la posición de los agentes (coches) en el modelo y del estado de llegada
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
def getTrafficLights():
    global randomModel

    if request.method == 'GET':
        # Obtención de la posición de los semáforos en el modelo y del estado actual.
        agentPositions = [
            {
                "id": str(agent.unique_id), 
                "x": x, 
                "y": 0, 
                "z": z,
                "state": agent.state 
            } 
            for (contents, (x, z)) in randomModel.grid.coord_iter() 
            for agent in contents if isinstance(agent, Traffic_Light)
        ]

        return jsonify({'positions': agentPositions})


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        # Actualización del modelo en cada paso.
        randomModel.step()
        currentStep += 1
        print("STEP", currentStep)
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True) # Iniciar el servidor Flask.
