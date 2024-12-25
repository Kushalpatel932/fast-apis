from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId


app = FastAPI()


MONGO_URI = "mongodb://localhost:27017"  # Update this if needed
client = AsyncIOMotorClient(MONGO_URI)
db = client.student_data  # Database name
student_collection = db.students


class Student(BaseModel):
    name:str
    age:int
    father_name : str

class StudentResponse(Student):
    id:str = Field(alias="_id")

def student_serializer(datas) -> dict:
    return {**datas, "_id": str(datas["_id"])}


@app.get("/students/",response_model = List[StudentResponse],status_code =200)
async def students():
    studentdatas = student_collection.find()
    data = await studentdatas.to_list(length =100)
    return [student_serializer(datas) for datas in data ]



@app.put("/student/",response_model = StudentResponse,status_code =201)
async def createstudent(student:Student):
    student = student.dict()
    reslut = await student_collection.insert_one(student)
    student["_id"]= reslut.inserted_id
    return student_serializer(student)

@app.delete("/studnetdelete/{student_id}",status_code = 200)
async def delete_student(student_id:str):
    user_delete = student_collection.delete_one({"_id":ObjectId(student_id)})
    if user_delete.deleted_count == 0:
        raise HTTPException(status_code=404, detail="student  not found")
    return {"message": "student is remove"}


