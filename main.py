from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy carrots", "done": False},
    {"id": 2, "title": "Clean the garden", "done": True},
    {"id": 3, "title": "Call the plumber", "done": True},
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    # if didn't find the task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task {task_id} not found"}
    )