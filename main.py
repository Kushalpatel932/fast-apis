from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

# MongoDB Connection
""" 
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    docker run -d --name mongodb -p 27017:27017 mongo

"""
MONGO_URI = "mongodb://localhost:27017"  # Update this if needed
client = AsyncIOMotorClient(MONGO_URI)
db = client.todo_app  # Database name
todos_collection = db.todos  # Collection name

app = FastAPI()

# Pydantic Models (Schemas)
class ToDo(BaseModel):
    task: str
    is_completed: Optional[bool] = False

class ToDoResponse(ToDo):
    id: str = Field(alias="_id")  # Map MongoDB `_id` to `id`

# Helper Function
def todo_serializer(todo) -> dict:
    return {**todo, "_id": str(todo["_id"])}

# CRUD Endpoints
@app.post("/todos/", response_model=ToDoResponse, status_code=201)
async def create_todo(todo: ToDo):
    todo_data = todo.dict()
    result = await todos_collection.insert_one(todo_data)
    todo_data["_id"] = result.inserted_id
    return todo_serializer(todo_data)

@app.get("/todos/", response_model=List[ToDoResponse])
async def get_todos():
    todos_cursor = todos_collection.find()
    todos = await todos_cursor.to_list(length=100)
    return [todo_serializer(todo) for todo in todos]

@app.delete("/todos/{todo_id}", status_code=200)
async def delete_todo(todo_id: str):
    result = await todos_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="To-Do not found")
    return {"message": "To-Do deleted successfully"}

