// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable] // Asegura que la clase pueda ser serializada por Unity para almacenamiento y transferencia.
public class AgentData
{
    // Definición de campos públicos para almacenar los datos del agente.
    public string id; // Identificador único del agente.
    public float x, y, z; // Posición del agente en el espacio 3D.
    public bool hasArrived; // Indica si el agente ha llegado a su destino.
    public bool state; // Estado adicional del agente

    // Constructor de la clase para inicializar un agente con datos específicos.
    public AgentData(string id, float x, float y, float z)
    {
        this.id = id; // Asigna el identificador.
        this.x = x; // Asigna la posición en el eje X.
        this.y = y; // Asigna la posición en el eje Y.
        this.z = z; // Asigna la posición en el eje Z.
    }
}

[Serializable] // Asegura que la clase pueda ser serializada por Unity.
public class AgentsData
{
    /*
    La clase AgentsData se utiliza para almacenar los datos de todos los agentes.

    Atributos:
        positions (list): Una lista de objetos AgentData.
    */
    public List<AgentData> positions; // Lista para almacenar los datos de varios agentes.
    List<string> activeAgentIds = new List<string>(); // Lista para almacenar los identificadores de agentes activos.

    // Constructor de la clase que inicializa la lista de posiciones de los agentes.
    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    // Definición de variables para la comunicación con el servidor.
string serverUrl = "http://localhost:8585"; // URL del servidor Flask.
string getAgentsEndpoint = "/getAgents"; // Endpoint para obtener datos de los agentes.
string getTrafficLightEndpoint = "/getTrafficLights"; // Endpoint para obtener datos de los semáforos.
string sendConfigEndpoint = "/init"; // Endpoint para enviar la configuración inicial.
string updateEndpoint = "/update"; // Endpoint para actualizar la simulación.

// Variables para almacenar datos de agentes y semáforos.
AgentsData agentsData, trafficLights; 
Dictionary<string, GameObject> agents; // Diccionario para mapear agentes a objetos de Unity.
Dictionary<string, Vector3> prevPositions, currPositions; // Diccionarios para posiciones anteriores y actuales de agentes.
private Dictionary<string, GameObject> trafficLightObjects; // Diccionario para los objetos de semáforos en Unity.

// Variables para la gestión de cámaras en Unity.
public List<GameObject> cameras; 
private int currentCameraIndex = 0; // Índice de la cámara actual.
private float cameraSwitchInterval = 6f; // Intervalo para cambiar de cámara.
private float cameraSwitchTimer = 0f; // Temporizador para el cambio de cámara.

// Variables de control para la actualización de la simulación.
bool updated = false, started = false;

// Prefabs y variables relacionadas con la simulación.
public GameObject trafficLightsPrefab; // Prefab para los semáforos.
public float timeToUpdate = 1.0f; // Tiempo para la actualización de la simulación.
private float timer, dt; // Temporizadores para controlar la actualización.
private int NAgents = 0; // Número de agentes en la simulación.
public GameObject[] carPrefabs; // Array de prefabs de coches.
public GameObject helicopterPrefab; // Prefab de helicóptero.
private HelicopterController helicopterController; // Controlador del helicóptero.

void Start()
{
    // Inicialización de variables y estructuras de datos.
    agentsData = new AgentsData();
    trafficLights = new AgentsData();

    prevPositions = new Dictionary<string, Vector3>();
    currPositions = new Dictionary<string, Vector3>();

    agents = new Dictionary<string, GameObject>();
    trafficLightObjects = new Dictionary<string, GameObject>();

    // Creación e inicialización del helicóptero.
    GameObject helicopterObj = Instantiate(helicopterPrefab, RandomGridPosition(), Quaternion.identity);
    helicopterController = helicopterObj.GetComponent<HelicopterController>();
    helicopterController.SetDestination(RandomGridPosition());

    // Configuración inicial de temporizadores y cámaras.
    timer = timeToUpdate;
    foreach (GameObject camera in cameras)
    {
        camera.SetActive(false);
    }
    if (cameras.Count > 0)
    {
        cameras[0].SetActive(true);
    }

    // Inicia la corutina para enviar la configuración al servidor.
    StartCoroutine(SendConfiguration());
    Debug.Log("Starting AgentController and sending configuration to server.");
}

private void Update() 
{
    // Controla la actualización regular de la simulación.
    if(timer < 0)
    {
        timer = timeToUpdate;
        updated = false;
        StartCoroutine(UpdateSimulation());
    }

    // Realiza acciones si la simulación ha sido actualizada.
    if (updated)
    {
        timer -= Time.deltaTime;
        dt = 1.0f - (timer / timeToUpdate);
        cameraSwitchTimer += Time.deltaTime;
        if (cameraSwitchTimer >= cameraSwitchInterval)
        {
            SwitchCamera();
            cameraSwitchTimer = 0f;
        }

        // Actualiza las posiciones de los agentes y controla el helicóptero. Borra las instancias de los agentes si ya llegaron a su destino
        RemoveArrivedAgents();
        float t = (timer / timeToUpdate);
        dt = t * t * ( 3f - 2f*t);
        if (helicopterController != null && Vector3.Distance(helicopterController.transform.position, helicopterController.Destination) < 0.1f)
        {
            helicopterController.SetDestination(RandomGridPosition());
        }
    }
}

void SwitchCamera()
{
    // Cambia la cámara activa en la lista de cámaras.
    if (cameras.Count > 0)
    {
        cameras[currentCameraIndex].SetActive(false);
        currentCameraIndex = (currentCameraIndex + 1) % cameras.Count;
        cameras[currentCameraIndex].SetActive(true);
    }
}

IEnumerator UpdateSimulation()
{
    // Corutina para actualizar la simulación mediante una solicitud al servidor.
    UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
    yield return www.SendWebRequest();

    if (www.result != UnityWebRequest.Result.Success)
        Debug.Log(www.error);
    else 
    {
        StartCoroutine(GetAgentsData());
        StartCoroutine(GetTrafficLightsData());
    }
}

IEnumerator SendConfiguration()
{
    // Corutina para enviar la configuración inicial al servidor.
    WWWForm form = new WWWForm();
    Debug.Log("Sending NAgents: " + NAgents);
    form.AddField("NAgents", NAgents.ToString());

    UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
    www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    yield return www.SendWebRequest();

    if (www.result != UnityWebRequest.Result.Success)
    {
        Debug.Log(www.error);
    }
    else
    {
        Debug.Log("Configuration upload complete!");
        Debug.Log("Getting Agents positions");

        StartCoroutine(GetAgentsData());
        StartCoroutine(GetTrafficLightsData());
    }
}


IEnumerator GetAgentsData() 
{
    // Envía una solicitud GET al servidor para obtener datos de los agentes.
    UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
    yield return www.SendWebRequest(); // Espera hasta que la solicitud esté completa.

    if (www.result != UnityWebRequest.Result.Success)
    {
        // Si hay un error en la solicitud, lo muestra en el registro.
        Debug.Log(www.error);
    }
    else 
    {
        // Si la solicitud es exitosa, procesa la respuesta.
        
        // Deserializa los datos JSON recibidos en un objeto AgentsData.
        agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
        string jsonResponse = www.downloadHandler.text; // Almacena la respuesta JSON como string.

        // Itera sobre cada agente recibido en los datos.
        foreach(AgentData agent in agentsData.positions)
        {
            // Registra los datos del agente, como ID y posición.
            Debug.Log($"Agent ID: {agent.id}, Position: ({agent.x}, {agent.y}, {agent.z}), HasArrived: {agent.hasArrived}");
            
            if (agent.hasArrived) continue;  // Si el agente ha llegado a su destino, lo ignora.

            // Convierte las coordenadas del agente en un Vector3.
            Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
            Vector3 initialPos = new Vector3(0,0,0); // Posición inicial por defecto.

            if (!agents.ContainsKey(agent.id))
            {
                // Si el agente no existe en el diccionario, lo crea y lo añade.

                // Selecciona un prefab de coche al azar y lo instancia.
                GameObject selectedCarPrefab = carPrefabs[UnityEngine.Random.Range(0, carPrefabs.Length)];
                GameObject newAgent = Instantiate(selectedCarPrefab, initialPos, Quaternion.identity);
                agents[agent.id] = newAgent;

                // Obtiene y configura el script ApplyTransforms del agente.
                ApplyTransforms applyTransforms = newAgent.GetComponentInChildren<ApplyTransforms>();
                applyTransforms.getPosition(newAgentPosition); // Establece la posición del agente.
                applyTransforms.getPosition(newAgentPosition);
                applyTransforms.setTime(timeToUpdate); // Establece el tiempo de actualización.
            }
            else
            {
                // Si el agente ya existe, actualiza su posición.

                ApplyTransforms applyTransforms = agents[agent.id].GetComponentInChildren<ApplyTransforms>();
                applyTransforms.getPosition(newAgentPosition); // Actualiza la posición del agente.
            }
        }

        updated = true; // Indica que los datos de los agentes han sido actualizados.
        if(!started) started = true; // Marca que la simulación ha comenzado si aún no había empezado.
    }
}



    IEnumerator GetTrafficLightsData() 
{
    // Realiza una solicitud GET para obtener datos de los semáforos.
    UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightEndpoint);
    yield return www.SendWebRequest(); // Espera hasta que la solicitud esté completa.

    if (www.result != UnityWebRequest.Result.Success)
    {
        // Si hay un error en la solicitud, muestra un mensaje de error.
        Debug.Log(www.error);
    }
    else 
    {
        // Si la solicitud es exitosa, procesa los datos recibidos.
        
        // Deserializa los datos JSON recibidos en un objeto AgentsData.
        trafficLights = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

        // Itera sobre cada semáforo recibido en los datos.
        foreach(AgentData trafficLight in trafficLights.positions)
        {
            GameObject lightObj = null;

            // Verifica si el semáforo ya existe; si no, lo crea y lo añade.
            if (!trafficLightObjects.TryGetValue(trafficLight.id, out lightObj))
            {
                lightObj = Instantiate(trafficLightsPrefab, new Vector3(trafficLight.x, trafficLight.y, trafficLight.z), Quaternion.identity);
                trafficLightObjects[trafficLight.id] = lightObj;
            }

            // Obtiene y actualiza los estados de las luces de cada semáforo.
            Light greenLight = lightObj.transform.Find("green_light").GetComponent<Light>();
            Light redLight = lightObj.transform.Find("red_light").GetComponent<Light>();

            greenLight.enabled = trafficLight.state;  
            redLight.enabled = !trafficLight.state;   
        }
    }
}

Vector3 RandomGridPosition()
{
    // Genera una posición aleatoria dentro de un rango especificado.
    float minX = 0f, maxX = 24f; 
    float minY = 8f, maxY = 10f; 
    float minZ = 0f, maxZ = 24f; 

    float randomX = UnityEngine.Random.Range(minX, maxX);
    float randomY = UnityEngine.Random.Range(minY, maxY);
    float randomZ = UnityEngine.Random.Range(minZ, maxZ);

    return new Vector3(randomX, randomY, randomZ);
}

void RemoveArrivedAgents()
{
    // Identifica y elimina los agentes que han llegado a su destino.
    List<string> agentsToRemove = new List<string>();

    // Recorre los agentes y agrega a la lista aquellos que han llegado.
    foreach (var agentData in agentsData.positions)
    {
        if (agentData.hasArrived)
        {
            agentsToRemove.Add(agentData.id);
        }
    }

    // Elimina los agentes de la lista y de la simulación.
    foreach (var agentId in agentsToRemove)
    {
        if (agents.TryGetValue(agentId, out GameObject agentObj))
        {
            Debug.Log($"Attempting to remove agent ID: {agentId}");
            try
            {
                Destroy(agentObj);
                Debug.Log($"Agent ID: {agentId} destroyed successfully.");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error while destroying agent ID: {agentId}: {ex.Message}");
            }

            agents.Remove(agentId);
            prevPositions.Remove(agentId);
            currPositions.Remove(agentId);
        }
    }
}
}