using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ApplyTransforms : MonoBehaviour
{
    [SerializeField] Vector3 displacement;
    // [SerializeField] float angle;
    [SerializeField] AXIS rotationAxis;
    [SerializeField] GameObject Wheel;
    [SerializeField] Vector3 scaling; // Add this line near the top of your class


    GameObject wheel1;
    GameObject wheel2;
    GameObject wheel3;
    GameObject wheel4;

    [SerializeField] float wheelRotationSpeed;



    Mesh mesh;
    Mesh meshWheel1;
    Mesh meshWheel2;
    Mesh meshWheel3;
    Mesh meshWheel4;

    Vector3[] baseVertices;
    Vector3[] newVertices;

    Vector3[] baseVertices1;
    Vector3[] newVertices1;

    Vector3[] baseVertices2;
    Vector3[] newVertices2;

    Vector3[] baseVertices3;
    Vector3[] newVertices3;

    Vector3[] baseVertices4;
    Vector3[] newVertices4;

    float T;
    float currentTime=0;
    float motionTime=1;
    Vector3 startPosition;
    Vector3 endPosition;
    


    void Start()
    {
        

        wheel1 = Instantiate(Wheel, transform);
        wheel2 = Instantiate(Wheel, transform);       
        wheel3 = Instantiate(Wheel, transform);       
        wheel4 = Instantiate(Wheel, transform);
        

        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVertices = new Vector3[baseVertices.Length];

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
        DoTransform(mesh, baseVertices);
        Debug.Log($"Current startPosition: {startPosition}, endPosition: {endPosition}, currentTime: {currentTime}, T: {T}");
        
    }

    public void setTime(float timeToUpdate){
        motionTime = timeToUpdate;
    }




   void DoTransform(Mesh mesh, Vector3[] vertices)
    {
        
        T=getT();
        Vector3 newposition=PositionLerp(startPosition, endPosition, T);

        float angleRadians = Mathf.Atan2(newposition.z, newposition.x);

        float angle = angleRadians * Mathf.Rad2Deg - 90;

        
        Matrix4x4 move= HW_Transforms.TranslationMat(newposition.x , newposition.y, newposition.z);

        Matrix4x4 moveOrigin= HW_Transforms.TranslationMat(-displacement.x, -displacement.y, -displacement.z);

        // Matrix4x4 moveObject= HW_Transforms.TranslationMat(displacement.x, displacement.y, displacement.z);

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle , rotationAxis );
        Matrix4x4 wheelRotate = HW_Transforms.RotateMat(Time.time * wheelRotationSpeed, AXIS.X);
        

        Matrix4x4 composite = move * rotate;
        

        Matrix4x4 pos1 = HW_Transforms.TranslationMat(0.142f, 0.049f, 0.261f );
        Matrix4x4 pos2 = HW_Transforms.TranslationMat(-0.142f, 0.049f, 0.261f );
        Matrix4x4 pos3 = HW_Transforms.TranslationMat(-0.142f, 0.049f, -0.216f );
        Matrix4x4 pos4 = HW_Transforms.TranslationMat(0.142f, 0.049f, -0.216f );

        Matrix4x4 sclae = HW_Transforms.ScaleMat(1.2f,1.2f,1.2f);

        Matrix4x4 rot = HW_Transforms.RotateMat(-180, AXIS.Y);


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



        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
        

        meshWheel1.vertices = newVertices1;
        meshWheel1.RecalculateNormals();

        meshWheel2.vertices = newVertices2;
        meshWheel2.RecalculateNormals();

        meshWheel3.vertices = newVertices3;
        meshWheel3.RecalculateNormals();

        meshWheel4.vertices = newVertices4;
        meshWheel4.RecalculateNormals();

        
    }

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
        return T;
    }

    public void getPosition(Vector3 newPosition){
        startPosition = endPosition;
        endPosition = newPosition;
        currentTime = 0;
        
    }

}


