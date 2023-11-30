// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;
    public bool hasArrived;
    public bool state;
    


    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        
    }
}


[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;
    List<string> activeAgentIds = new List<string>();

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
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getTrafficLightEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, trafficLights;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;
    private Dictionary<string, GameObject> trafficLightObjects;

    bool updated = false, started = false;

    public GameObject trafficLightsPrefab; 
    public float timeToUpdate = 1.0f;
    private float timer, dt;
    private int NAgents = 0;
    public GameObject[] carPrefabs;
    public GameObject helicopterPrefab;
    private HelicopterController helicopterController;



    void Start()
    {
        agentsData = new AgentsData();
        trafficLights = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        trafficLightObjects = new Dictionary<string, GameObject>();

        GameObject helicopterObj = Instantiate(helicopterPrefab, RandomGridPosition(), Quaternion.identity);
        helicopterController = helicopterObj.GetComponent<HelicopterController>();

        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
        Debug.Log("Starting AgentController and sending configuration to server.");
    }



    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions.
            // The positions are interpolated between the previous and current positions.
            RemoveArrivedAgents();
            float t = (timer / timeToUpdate);
            dt = t * t * ( 3f - 2f*t);
            if (helicopterController != null && Vector3.Distance(helicopterController.transform.position, helicopterController.Destination) < 0.1f)
            {
                // If the helicopter is at or very close to the destination, set a new random destination
                helicopterController.SetDestination(RandomGridPosition());
            }
        }
    }
 
    IEnumerator UpdateSimulation()
    {
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
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();
        Debug.Log("Sending NAgents: " + NAgents);
        form.AddField("NAgents", NAgents.ToString());
        // form.AddField("width", width.ToString());
        // form.AddField("height", height.ToString());

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

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficLightsData());
        }
    }

IEnumerator GetAgentsData() 
{
    
    UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
    yield return www.SendWebRequest();

    if (www.result != UnityWebRequest.Result.Success)
    {
        Debug.Log(www.error);
    }
    else 
    {
        
        agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
        string jsonResponse = www.downloadHandler.text;
        foreach(AgentData agent in agentsData.positions)
    {
        Debug.Log($"Agent ID: {agent.id}, Position: ({agent.x}, {agent.y}, {agent.z}), HasArrived: {agent.hasArrived}");
        if (agent.hasArrived) continue;  

        Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
        Vector3 initialPos = new Vector3(0,0,0);
        if (!agents.ContainsKey(agent.id))
        {
            // Instantiate new agent if it doesn't exist
            // GameObject newAgent = Instantiate(agentPrefab, initialPos, Quaternion.identity);
            GameObject selectedCarPrefab = carPrefabs[UnityEngine.Random.Range(0, carPrefabs.Length)];
            GameObject newAgent = Instantiate(selectedCarPrefab, initialPos, Quaternion.identity);
            agents[agent.id] = newAgent;
            ApplyTransforms applyTransforms = newAgent.GetComponentInChildren<ApplyTransforms>();
            applyTransforms.getPosition(newAgentPosition);
            applyTransforms.getPosition(newAgentPosition);
            applyTransforms.setTime(timeToUpdate);
            
        }
        else
        {
            // Update position of existing agent
            ApplyTransforms applyTransforms = agents[agent.id].GetComponentInChildren<ApplyTransforms>();
            applyTransforms.getPosition(newAgentPosition);
        }

        
    }


        updated = true;
        if(!started) started = true;
    }
}



    IEnumerator GetTrafficLightsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            trafficLights = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(trafficLights.positions);

            foreach(AgentData trafficLight in trafficLights.positions)
        {
            GameObject lightObj = null;
            if (!trafficLightObjects.TryGetValue(trafficLight.id, out lightObj))
            {
                // Instantiate and store the traffic light object if it doesn't exist
                lightObj = Instantiate(trafficLightsPrefab, new Vector3(trafficLight.x, trafficLight.y, trafficLight.z), Quaternion.identity);
                trafficLightObjects[trafficLight.id] = lightObj;
            }

            // Update the state of the traffic light
            Light greenLight = lightObj.transform.Find("green_light").GetComponent<Light>();
            Light redLight = lightObj.transform.Find("red_light").GetComponent<Light>();

            greenLight.enabled = trafficLight.state;  // Green light on if state is true
            redLight.enabled = !trafficLight.state;   // Red light on if state is false
        }
        }
    }

    Vector3 RandomGridPosition()
{
    // Define the boundaries of the grid
    float minX = 0f;  // Minimum X coordinate
    float maxX = 24f; // Maximum X coordinate
    float minY = 10f;  // Minimum Y coordinate (if you want varying heights)
    float maxY = 10f; // Maximum Y coordinate (for different heights)
    float minZ = 0f;  // Minimum Z coordinate
    float maxZ = 24f; // Maximum Z coordinate

    // Generate random x, y, and z coordinates within the grid boundaries
    float randomX = UnityEngine.Random.Range(minX, maxX);
    float randomY = UnityEngine.Random.Range(minY, maxY);
    float randomZ = UnityEngine.Random.Range(minZ, maxZ);

    // Return the new random position
    return new Vector3(randomX, randomY, randomZ);
}



   void RemoveArrivedAgents()
{
    List<string> agentsToRemove = new List<string>();
    Debug.Log($"Agents count before removal: {agents.Count}");


    // Check which agents have arrived and need to be removed
    foreach (var agentData in agentsData.positions)
    {
        if (agentData.hasArrived)
        {
            Debug.Log($"Agent ID {agentData.id} marked for removal");
            agentsToRemove.Add(agentData.id);
        }
    }

    // Remove the agents from the dictionary and scene
    foreach (var agentId in agentsToRemove)
    {
        if (agents.TryGetValue(agentId, out GameObject agentObj))
        {
            Debug.Log($"Attempting to remove agent ID: {agentId}");

            try
            {
                // Try to destroy the agent and catch any potential exceptions
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
    Debug.Log($"Agents count after removal: {agents.Count}");

}
}