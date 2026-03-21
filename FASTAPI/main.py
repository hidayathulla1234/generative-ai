from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel,Field,computed_field
from fastapi.responses import JSONResponse
from typing import Annotated,Literal,Optional

import json 

app=FastAPI()
class Patient(BaseModel):

    id: Annotated[str,Field(...,description='ID of the Patient',examples=['P001'])]
    name:Annotated[str,Field(...,description='name of the Patient')]
    city:Annotated[str,Field(...,description='city of the Patient')]
    age:Annotated[int,Field (...,gt=0,lt=120,description='age of the Patient ')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='gender of the Patient ')]
    height:Annotated[float,Field(...,gt=0,description='Heigth of the Patient in mts')]
    weight:Annotated[float,Field(...,description='Weight of the Patient in kgs')]

    @computed_field()
    @property
    def bmi(self)-> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    

    @computed_field()
    @property
    def verdict(self)-> str:
        if self.bmi<18.5:
            return 'UnderWeight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Normal'
        else:
            return "Obese"
        
class PatientUpdate(BaseModel):
    
    
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None)]
    gender:Annotated[Optional[Literal['male','female']],Field(default=None )]
    height:Annotated[Optional[float],Field(gt=0,default=None)]
    weight:Annotated[Optional[float],Field(default=None )]







def load_data():
    with open("patients.json","r") as f:
         data= json.load(f)
       
    return data 

def save_data(data):
    with open('patients.json','w') as f :
        json.dump(data,f)

           

@app.get("/")
def hello():
    return{"message":"Patient Management System API"}

@app.get("/about")
def about():
    return{'message':"A fully functonal API  to manage your Patient "}

@app.get('/view')
def view():
     data=load_data()

     return data
@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(..., description='Id of the patient in the DB',examples=['P001'])):
    #load all the patinets

    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='Patient not found ')

@app.get('/sort')
def sort_patient(sort_by: str = Query(..., description='Sort on the basis of the heighr ,weight or bmi'), order: str = Query('asc',description ='sort in ascending or descending order ')):

    
   valid_fields =['height','weight','bmi']

   if sort_by not in valid_fields:
       raise HTTPException(status_code=400,detail=f'Invalid field select from {valid_fields}')
       

   if order not in ['asc','desc']:
       raise HTTPException(status_code=400,detail=f'Invalid order selecr between asc and desc')
   

   data = load_data()

   sorted_data = sorted(
    data.values(),
    key=lambda x: x.get(sort_by, 0),
    reverse=(order == "desc")
)
   return sorted_data


@app.post('/create')
def create_patient(patient:Patient):
       
    #loading existing data 
    data=load_data()
    # check if the patient already exist
    if patient.id in data:
        raise HTTPException(status_code=400,detail='Patient already exists')
    # new patient add to the database 
    data[patient.id]=patient.model_dump(exclude=['id'])

    #save into the json file 

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'Patient created sucessfully'})

@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
  #laod  the data

    data = load_data()
    # check if patient exist or not 

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # update  the patient into the data base 

    data[patient_id] = patient_update.model_dump()

    save_data(data)

    return {"message": "Patient updated successfully", "patient_id": patient_id}
   

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update:PatientUpdate):
    

    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient Id not found')
    
    existing_patient_info=data[patient_id]

    updated_patient_info= patient_update.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value

        # existing_patient_info ->pydantic object ->updated bmi +verdict
        existing_patient_info["id"]=patient_id 
        patient_pydantic_obj=Patient(**existing_patient_info)
        # -> pydantic objct -.dict
        existing_patient_info=patient_pydantic_obj.model_dump(exclude='id')
        # add this dictionary to data
        data[patient_id]=existing_patient_info

        #save data
        save_data(data)

        return JSONResponse(status_code=200,content={'message':'Patient Updated '})


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):
    # Load existing data
    data = load_data()

    # Check if patient exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Remove the patient from the dictionary
    deleted_patient = data.pop(patient_id)

    # Save the updated data back to the JSON file
    save_data(data)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Patient deleted successfully",
            "patient_id": patient_id,
            "deleted_patient": deleted_patient
        }
    )
