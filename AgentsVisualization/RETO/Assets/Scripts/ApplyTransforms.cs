//Emilia Salazar e Ian Holender
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyTransforms : MonoBehaviour
{
    [SerializeField] Vector3 displacement; // Desplazamiento del objeto principal.
    [SerializeField] AXIS rotationAxis; // Eje de rotación para el objeto principal.
    [SerializeField] GameObject Wheel; // Objeto de rueda que se instanciará.
    [SerializeField] Vector3 scaling; // Escalado que se aplicará a las ruedas.

    GameObject wheel1, wheel2, wheel3, wheel4; // Referencias a las ruedas instanciadas.

    [SerializeField] float wheelRotationSpeed; // Velocidad de rotación de las ruedas.

    // Variables para manipulación de mallas y vértices.
    Mesh mesh, meshWheel1, meshWheel2, meshWheel3, meshWheel4;
    Vector3[] baseVertices, newVertices;
    Vector3[] baseVertices1, newVertices1;
    Vector3[] baseVertices2, newVertices2;
    Vector3[] baseVertices3, newVertices3;
    Vector3[] baseVertices4, newVertices4;

    // Variables para controlar la interpolación y movimiento.
    float T, currentTime = 0, motionTime = 1;
    Vector3 startPosition, endPosition;
    float angle, lastAngle;
    

    void Start()
    {
        // Instanciación de las ruedas y preparación de las mallas.
        wheel1 = Instantiate(Wheel, transform);
        wheel2 = Instantiate(Wheel, transform);       
        wheel3 = Instantiate(Wheel, transform);       
        wheel4 = Instantiate(Wheel, transform);

        // Configuración inicial de mallas y vértices.
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];

        // COnfiguración inicial de mallas y vertices para cada rueda.
        meshWheel1 = wheel1.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices1 = meshWheel1.vertices;
        newVertices1 = new Vector3[baseVertices1.Length];

        meshWheel2 = wheel2.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices2 = meshWheel2.vertices;
        newVertices2 = new Vector3[baseVertices2.Length];

        meshWheel3 = wheel3.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices3 = meshWheel3.vertices;
        newVertices3 = new Vector3[baseVertices3.Length];

        meshWheel4 = wheel4.GetComponentInChildren<MeshFilter>().mesh;
        baseVertices4 = meshWheel4.vertices;
        newVertices4 = new Vector3[baseVertices4.Length];
    }


    void Update()
    {
        // Aplicar transformaciones en cada actualización.
        DoTransform(mesh, baseVertices);
        Debug.Log($"Current startPosition: {startPosition}, endPosition: {endPosition}, currentTime: {currentTime}, T: {T}");
    }

    public void setTime(float timeToUpdate)
    {
        motionTime = timeToUpdate; // Establecer tiempo para la interpolación.
    }

    void DoTransform(Mesh mesh, Vector3[] vertices)
    {
        // Cálculo y aplicación de transformaciones.
        T = getT();
        Vector3 newPosition = PositionLerp(startPosition, endPosition, T);
        Vector3 displacement = endPosition - startPosition;
        //Cálculo de ángulo sólo si el coche está en movimiento
        if (startPosition != endPosition)
        {
            float angleRadians = Mathf.Atan2(displacement.z, displacement.x);
            angle = angleRadians * Mathf.Rad2Deg - 90;
        }

        // Creación de matrices de transformación, para mover, para rotar, para instanciar las ruedas en su pocisión, para que las ruedas giren sobre su eje, etc
        Matrix4x4 move = HW_Transforms.TranslationMat(newPosition.x, newPosition.y, newPosition.z);
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, rotationAxis);
        Matrix4x4 wheelRotate = HW_Transforms.RotateMat(Time.time * wheelRotationSpeed, AXIS.X);

        Matrix4x4 composite = move * rotate;

        // Posiciones relativas de cada rueda.
        Matrix4x4 pos1 = HW_Transforms.TranslationMat(0.142f, 0.049f, 0.261f);
        Matrix4x4 pos2 = HW_Transforms.TranslationMat(-0.142f, 0.049f, 0.261f);
        Matrix4x4 pos3 = HW_Transforms.TranslationMat(-0.142f, 0.049f, -0.216f);
        Matrix4x4 pos4 = HW_Transforms.TranslationMat(0.142f, 0.049f, -0.216f);

        Matrix4x4 sclae = HW_Transforms.ScaleMat(1.2f, 1.2f, 1.2f);
        Matrix4x4 rot = HW_Transforms.RotateMat(-180, AXIS.Y);

        // Aplicación de transformaciones al objeto principal y a las ruedas.


        for (int i = 0; i < newVertices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);
            newVertices[i] = composite * temp ;
        }

        for (int i = 0; i < newVertices1.Length; i++)
        {
            Vector4 temp1 = new Vector4(baseVertices1[i].x, baseVertices1[i].y, baseVertices1[i].z, 1);
            newVertices1[i] = composite  * pos1  * wheelRotate * sclae *  temp1 ;
        }

        for (int i = 0; i < newVertices2.Length; i++)
        {
            Vector4 temp2 = new Vector4(baseVertices2[i].x, baseVertices2[i].y, baseVertices2[i].z, 1);
            newVertices2[i] = composite  * pos2 * wheelRotate * sclae * rot * temp2;
        }

        for (int i = 0; i < newVertices3.Length; i++)
        {
            Vector4 temp3 = new Vector4(baseVertices3[i].x, baseVertices3[i].y, baseVertices3[i].z, 1);
            newVertices3[i] = composite  * pos3 * wheelRotate * sclae * temp3;
        }
        for (int i = 0; i < newVertices4.Length; i++)
        {
            Vector4 temp4 = new Vector4(baseVertices4[i].x, baseVertices4[i].y, baseVertices4[i].z, 1);
            newVertices4[i] = composite  * pos4 * wheelRotate * sclae * rot * temp4;
        }


        //Recalcular el mesh, /vértices, normales y bounds) para el coche y para cada rueda
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        

        meshWheel1.vertices = newVertices1;
        meshWheel1.RecalculateNormals();
        meshWheel1.RecalculateBounds();

        meshWheel2.vertices = newVertices2;
        meshWheel2.RecalculateNormals();
        meshWheel2.RecalculateBounds();

        meshWheel3.vertices = newVertices3;
        meshWheel3.RecalculateNormals();
        meshWheel3.RecalculateBounds();

        meshWheel4.vertices = newVertices4;
        meshWheel4.RecalculateNormals();
        meshWheel4.RecalculateBounds();

        
    }

    // Interpolación lineal de posición.
    Vector3 PositionLerp(Vector3 start, Vector3 end, float time)
    {
        return start + (end - start) * time;
    }

    float getT(){
        currentTime+=Time.deltaTime;
        T=currentTime/motionTime;
        if(T>1){
            T=1;
        }
        return T; // Cálculo del factor de interpolación.
    }

    //Update de las pocisiones, para que el coche vaya avanzando 
    public void getPosition(Vector3 newPosition){
        startPosition = endPosition;
        endPosition = newPosition;
        currentTime = 0;
        
        
        
    }

}


