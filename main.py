from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy carrots", "done": False},
    {"id": 2, "title": "Clean the garden", "done": True},
    {"id": 3, "title": "Call the plumber", "done": True},
]

@app.get("/", summary="API root endpoint", description="Returns basic information about the API")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check endpoint", description="Returns the health status of the API")
def read_health():
    return {"status": "ok"}

@app.get("/tasks", summary="Get all tasks", description="Returns a list of all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", summary="Get a task by ID", description="Returns the task with the specified ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    # if didn't find the task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Create task", description="Creates a new task")
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = None

    if not isinstance(body, dict) or "title" not in body or not str(body["title"]).strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required and must be non-empty"}
        )

    next_id = max(task["id"] for task in tasks) + 1 if tasks else 1

    new_task = {
        "id": next_id,
        "title": str(body["title"]).strip(),
        "done": False
    }

    tasks.append(new_task)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=new_task
    )

@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, summary="Update task", description="Updates an existing task's title or completion")
async def update_task(task_id: int, request: Request):
    task = next((task for task in tasks if task["id"] == task_id), None)

    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )

    try:
        body = await request.json()
    except Exception:
        body = None

    if not isinstance(body, dict) or not body:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid request body"}
        )

    if "title" in body:
        if not str(body["title"]).strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Title must be non-empty"}
            )

        task["title"] = str(body["title"]).strip()

    if "done" in body:
        if not isinstance(body["done"], bool):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Done must be a boolean"}
            )

        task["done"] = body["done"]

    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete task", description="Deletes a task by ID")
def delete_task(task_id: int):
    global tasks
    task = next((task for task in tasks if task["id"] == task_id), None)

    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )

    tasks = [task for task in tasks if task["id"] != task_id]

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
