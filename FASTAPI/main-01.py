from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel,Field,computed_field 
from fastapi.responses import JSONResponse
from typing import Annotated,Literal
import json

app=FastAPI()

class Patient(BaseModel):

    id:Annotated[str,Field(...,description='ID of the Patient')]
    name:Annotated[str,Field(...,description='name of the Patient')]
    city:Annotated[str,Field(...,description='city of the Patient')]
    age:Annotated[int,Field (...,gt=0,lt=120,description='age of the Patient ')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='gender of the Patient ')]
    height:Annotated[float,Field(...,gt=0,description='Heigth of the Patient in mts')]
    weight:Annotated[float,Field(...,description='Weight of the Patient in kgs')]

    @computed_field()
    @property
    def bmi(self)->float:
      bmi=(self.weight/(self.height**2))
      return bmi

    @computed_field()
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return 'Underweight'
        elif self.bmi<25:
            return 'Normal'
        elif self.bmi<30:
            return 'Normal'
        else:
            return 'Obese'




def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get('/')  
def hello():
    return 'message: Patient Managemnet System API'

@app.get('/about')
def about():
    return 'message : A fully functional API to manage Your Patient'

@app.get('/view')
def view():
    data=load_data()
    return data


## path parameter
@app.get('/patient/{patient_id}')
def view_patient(patient_id:str=Path(...,description='Id of the Patient in the DataBase',examples=['P001'])):


    #load all the Patients
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='patient not found ')

@app.get('/sort')
def sort_patient(sort_by:str=Query(...,description='Sort on the basis of height,weight and bmi'),order:str=Query('asc',description='sort in ascending or descending order ')):
    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=404,detail=f'Invalid select from {valid_fields}')
    
    if order not in['asc','desc']:
        raise HTTPException(status_code=404,detail=f'Invalid select from asc and desc')
   

    data=load_data()
      

    sorted_data=sorted(
        data.values(),
        key=lambda x:x.get(sort_by,0),
        reverse=(order == 'desc')
    )
    return sorted_data
    

    #creating Patient

@app.post('/create')
def create_patient(patient:Patient):

    #loaing existing data
    data=load_data()

    # check if the patient already exist 
    if patient.id in data:
        raise HTTPException(status_code=404,detail='patient already found ')
    
    #new patient add to the database
    data[patient.id]=patient.model_dump(exclude=['id'])


    #save into the json file 
    save_data(data)

    return JSONResponse(status_code=201,content={'message':'created sucessfully '})
    