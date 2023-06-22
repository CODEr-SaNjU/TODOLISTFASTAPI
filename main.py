from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict, List

# Database Setup
# Assuming you have already installed and configured MySQL or MongoDB

# MySQL Example
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="tododatabase"
)

app = FastAPI()

# Basic Authentication Setup
security = HTTPBasic()

# Sample Data Model
class Todo(BaseModel):
    id: int
    task: str
    completed: bool

# Authenticated User Model
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticates the user using Basic Authentication credentials.

    Args:
        credentials (HTTPBasicCredentials): Basic Authentication credentials.

    Raises:
        HTTPException: Raises 401 Unauthorized if the credentials are invalid.

    Returns:
        str: Authenticated username.
    """
    correct_username = 'admin'
    correct_password = 'admin'
    if credentials.username == correct_username and credentials.password == correct_password:
        return credentials.username
    else:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )

# MySQL Database Operations
def create_todo_mysql(todo: Todo):
    """
    Creates a new Todo .

    Args:
        todo (Todo): Todo data.

    Returns:
        dict: Success message.
    """
    mycursor = mydb.cursor()
    check_sql = "SELECT id FROM todos WHERE id = %s"
    check_val = (todo.id,)
    mycursor.execute(check_sql, check_val)
    result = mycursor.fetchone()
    if result:
        return {"message": f"Todo with ID {todo.id} already exists"}
    

    sql = "INSERT INTO todos (id, task, completed) VALUES (%s, %s, %s)"
    val = (todo.id, todo.task, todo.completed)
    mycursor.execute(sql, val)
    mydb.commit()
    return {"message": "Todo created successfully"}

def get_todo_mysql(id: int):
    """
    Retrieves a Todo from MySQL by ID.

    Args:
        id (int): Todo ID.

    Returns:
        Todo: Retrieved Todo.
    """
    mycursor = mydb.cursor()
    sql = "SELECT * FROM todos WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        todo = Todo(id=result[0], task=result[1], completed=result[2])
        return todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")

def get_all_todos_mysql():
    """
    Retrieves a list of all Todos from MySQL.

    Returns:
        List[Todo]: List of all Todos.
    """
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM todos")
    results = mycursor.fetchall()
    todos = []
    for result in results:
        todo = Todo(id=result[0], task=result[1], completed=result[2])
        todos.append(todo)
    return todos

def update_todo_mysql(id: int, todo: Todo):
    """
    Updates a Todo  by ID.

    Args:
        id (int): Todo ID.
        todo (Todo): Updated Todo data.

    Raises:
        HTTPException: Raises 404 Not Found if the Todo does not exist.

    Returns:
        dict: Success message.
    """
    mycursor = mydb.cursor()
    sql = "UPDATE todos SET task = %s, completed = %s WHERE id = %s"
    val = (todo.task, todo.completed, id)
    mycursor.execute(sql, val)
    mydb.commit()
    if mycursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo updated successfully"}

def delete_todo_mysql(id: int):
    """
    Deletes a Todo from MySQL by ID.

    Args:
        id (int): Todo ID.

    Raises:
        HTTPException: Raises 404 Not Found if the Todo does not exist.

    Returns:
        dict: Success message.
    """
    mycursor = mydb.cursor()
    sql = "DELETE FROM todos WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    mydb.commit()
    if mycursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

# In-memory Database
todos_db: Dict[int, Todo] = {}

@app.post("/todos/")
def create_todo(todo: Todo, current_user: str = Depends(get_current_user)):
    """
    Creates a new Todo.

    Args:
        todo (Todo): Todo data.
        current_user (str): Authenticated username.

    Returns:
        dict: Success message.
    """

    return create_todo_mysql(todo)

@app.get("/todos/{id}")
def get_todo(id: int, current_user: str = Depends(get_current_user)):
    """
    Retrieves a Todo by ID.

    Args:
        id (int): Todo ID.
        current_user (str): Authenticated username.

    Raises:
        HTTPException: Raises 404 Not Found if the Todo does not exist.

    Returns:
        Todo: Retrieved Todo.
    """
    
    return get_todo_mysql(id)


@app.get("/todos/")
def get_all_todos(current_user: str = Depends(get_current_user)):
    """
    Retrieves a list of all Todos.

    Args:
        current_user (str): Authenticated username.

    Returns:
        List[Todo]: List of all Todos.
    """

    return get_all_todos_mysql()

@app.put("/todos/{id}")
def update_todo(id: int, todo: Todo, current_user: str = Depends(get_current_user)):
    """
    Updates a Todo by ID.

    Args:
        id (int): Todo ID.
        todo (Todo): Updated Todo data.
        current_user (str): Authenticated username.

    Raises:
        HTTPException: Raises 404 Not Found if the Todo does not exist.

    Returns:
        dict: Success message.
    """

    return update_todo_mysql(id, todo)

@app.delete("/todos/{id}")
def delete_todo(id: int, current_user: str = Depends(get_current_user)):
    """
    Deletes a Todo by ID.

    Args:
        id (int): Todo ID.
        current_user (str): Authenticated username.

    Raises:
        HTTPException: Raises 404 Not Found if the Todo does not exist.

    Returns:
        dict: Success message.
    """

    return delete_todo_mysql(id)
