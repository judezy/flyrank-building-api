import sqlite3
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()

DB_FILE = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL DEFAULT 0)
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Buy apples", 0),
                    ("Clean pears", 1),
                    ("Call the doctors", 0),
                ]
            )

        conn.commit()

init_db()

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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()

        return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

@app.get("/tasks/{task_id}", summary="Get a task by ID", description="Returns the task with the specified ID")
def get_task(task_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

        if not row:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Task {task_id} not found"}
            )

        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

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

    title = str(body["title"]).strip()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
        conn.commit()
        task_id = cursor.lastrowid

    new_task = {
        "id": task_id,
        "title": title,
        "done": False
    }

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
