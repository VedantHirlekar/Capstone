from fastapi import FastAPI, Request
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 GLOBAL REQUEST LOGGER
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    print(f"🔥 FASTAPI HIT → {request.method} {request.url}")

    # For POST/PUT, log body
    if request.method in ["POST", "PUT"]:
        body = await request.body()
        print(f"📦 Body: {body.decode('utf-8')}")

    response = await call_next(request)

    duration = round((time.time() - start_time) * 1000, 2)

    print(
        f"✅ FASTAPI RESPONSE → {request.method} {request.url} | {response.status_code} | {duration}ms"
    )

    return response


# ENV CONFIG
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT"))
}

# DB connection retry
def get_connection():
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            print("✅ FastAPI connected to DB")
            return conn
        except Exception as e:
            print("❌ DB retrying...", e)
            time.sleep(3)

# Model
class Employee(BaseModel):
    name: str
    phone: str

# GET
@app.get("/employees")
def get_employees():
    print("📥 FASTAPI → GET /employees")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees")
    data = cursor.fetchall()

    conn.close()
    return data

# POST
@app.post("/employees")
def add_employee(emp: Employee):
    print("📥 FASTAPI → POST /employees")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO employees (name, phone) VALUES (%s, %s)",
        (emp.name, emp.phone)
    )

    conn.commit()
    conn.close()

    return {"message": "Employee added"}