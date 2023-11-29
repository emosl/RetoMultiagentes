using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject[] buildingPrefab;
    [SerializeField] GameObject semaphorePrefab;
    [SerializeField] int tileSize;
    [SerializeField] GameObject metricsPrefab; // Asigna el prefab del letrero aquí

    private GameObject metricsPanel;
    private Text metricsText;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
        CreateMetricsPanel();
    }

    // Update is called once per frame
    void Update()
    {
        UpdateMetrics();
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        int y = tiles.Split('\n').Length - 1;

        Vector3 position;
        GameObject tile;

        for (int i = 0; i < tiles.Length; i++)
        {
            if (tiles[i] == '>' || tiles[i] == '<')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'v' || tiles[i] == '^')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 's')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'S')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'D')
            {
                int rand = Random.Range(0, buildingPrefab.Length);
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.Euler(0, 90, 0));
                tile.GetComponent<Renderer>().materials[0].color = Color.red;
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'I')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;

                Debug.Log($"Building ('I') created at x: {x}, y: {y}, position: {position}");

                x += 1;
            }
            else if (tiles[i] == '#')
            {
                int rand = Random.Range(0, buildingPrefab.Length);
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.identity);
                tile.transform.localScale = new Vector3(1, Random.Range(0.5f, 2.0f), 1);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '\n')
            {
                x = 0;
                y -= 1;
            }
        }
    }

    void CreateMetricsPanel()
    {
        metricsPanel = Instantiate(metricsPrefab, new Vector3(10, 5, 10), Quaternion.identity);
        metricsText = metricsPanel.GetComponentInChildren<Text>();
    }

    void UpdateMetrics()
    {
        metricsText.text = $"Cars in Scene: {CountCarsInScene()}\nTotal Cars Generated: {CountTotalCarsGenerated()}";
    }

    int CountCarsInScene()
    {
        return GameObject.FindGameObjectsWithTag("Car").Length;
    }

    int CountTotalCarsGenerated()
    {
        // Implementa la lógica para contar los coches generados en total
        // Puedes llevar un contador en el script o utilizar eventos como se mencionó anteriormente
        // En este ejemplo, simplemente devolvemos un valor fijo para mostrar el concepto
        return 10;
    }
}
