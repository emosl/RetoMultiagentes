using UnityEngine;

public class MetricsManager : MonoBehaviour
{
    private int totalCarsSpawned = 0;
    private int totalCarsInScene = 0;

    void Start()
    {
        // Puedes inicializar métricas aquí si es necesario
    }

    public void UpdateMetricsOnCarSpawn()
    {
        totalCarsSpawned++;
        totalCarsInScene++;
        LogMetrics();
    }

    public void UpdateMetricsOnCarArrival()
    {
        totalCarsInScene--;
        LogMetrics();
    }

    private void LogMetrics()
    {
        Debug.Log($"Total de coches spawnados: {totalCarsSpawned}");
        Debug.Log($"Coches en la escena: {totalCarsInScene}");
        // Puedes agregar más métricas aquí según sea necesario
    }
}
