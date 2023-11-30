using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HelicopterController : MonoBehaviour
{
    public float speed = 5.0f;
    private Vector3 destination;

    // Public property to access the destination
    public Vector3 Destination
    {
        get { return destination; }
        private set { destination = value; }
    }

    public void SetDestination(Vector3 newDestination)
    {
        Destination = newDestination;
    }

    void Update()
    {
        // Move towards the destination
        if (Vector3.Distance(transform.position, Destination) > 0.1f)
        {
            // Calculate the direction of movement
            Vector3 direction = (Destination - transform.position).normalized;

            // Create a rotation that looks along the direction of movement
            Quaternion lookRotation = Quaternion.LookRotation(direction);

            // Smoothly rotate the helicopter towards the look rotation
            transform.rotation = Quaternion.Slerp(transform.rotation, lookRotation, Time.deltaTime * speed);

            // Move towards the destination
            transform.position = Vector3.MoveTowards(transform.position, Destination, speed * Time.deltaTime);
        }
    }
}
