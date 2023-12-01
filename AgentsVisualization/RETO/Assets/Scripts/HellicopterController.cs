using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HelicopterController : MonoBehaviour
{
    public float speed = 5.0f; // Velocidad de movimiento del helicóptero.
    private Vector3 destination; // Destino al que se moverá el helicóptero.

    // Propiedad pública para acceder al destino.
    public Vector3 Destination
    {
        get { return destination; } // Obtener el valor actual del destino.
        private set { destination = value; } // Asignar un nuevo destino.
    }

    // Método público para establecer un nuevo destino.
    public void SetDestination(Vector3 newDestination)
    {
        Destination = newDestination;
    }

    void Update()
    {
        // Moverse hacia el destino.
        if (Vector3.Distance(transform.position, Destination) > 0.1f) // Comprobar si estamos cerca del destino.
        {
            // Calcular la dirección hacia el destino.
            Vector3 direction = (Destination - transform.position).normalized;

            // Crear una rotación que mire en la dirección del movimiento.
            Quaternion lookRotation = Quaternion.LookRotation(direction);

            // Rotar suavemente el helicóptero hacia la rotación de destino.
            transform.rotation = Quaternion.Slerp(transform.rotation, lookRotation, Time.deltaTime * speed);

            // Mover el helicóptero hacia el destino.
            transform.position = Vector3.MoveTowards(transform.position, Destination, speed * Time.deltaTime);
        }
    }
}
