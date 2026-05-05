Vedant Hirlekar <vedant.hirlekar@tudip.com>
	
2:35 PM (1 hour ago)
	
	
to me
FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3001

CMD ["node", "server.js"]



require("dotenv").config(); // 👈 MUST be at top

const express = require("express");
const mysql = require("mysql2");
//const cors = require("cors");

const app = express();

//app.use(cors());
app.use(express.json());

/* =========================================
   🔥 GLOBAL REQUEST LOGGER (VERY IMPORTANT)
========================================= */
app.use((req, res, next) => {
  const start = Date.now();

  // Log incoming request
  console.log(`🔥 EXPRESS HIT → ${req.method} ${req.url}`);

  // Log request body for POST/PUT
  if (req.method === "POST" || req.method === "PUT") {
    console.log("📦 Body:", req.body);
  }

  // Log response after it finishes
  res.on("finish", () => {
    console.log(
      `✅ EXPRESS RESPONSE → ${req.method} ${req.url} | ${res.statusCode} | ${Date.now() - start}ms`
    );
  });

  next();
});

/* =========================================
   🗄️ MySQL CONFIG
========================================= */
const dbConfig = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT
};

let db;

function handleDisconnect() {
  db = mysql.createConnection(dbConfig);

  db.connect((err) => {
    if (err) {
      console.log("❌ DB connection failed. Retrying in 3s...", err.message);
      setTimeout(handleDisconnect, 3000);
    } else {
      console.log("✅ Connected to MySQL");
    }
  });

  db.on("error", (err) => {
    console.log("❌ DB error:", err.message);

    if (err.code === "PROTOCOL_CONNECTION_LOST") {
      handleDisconnect();
    }
  });
}

handleDisconnect();

/* =========================================
   📡 ROUTES
========================================= */

// GET employees
app.get("/employees", (req, res) => {
  db.query("SELECT * FROM employees", (err, result) => {
    if (err) {
      console.log("❌ DB SELECT ERROR:", err.message);
      return res.status(500).json({ error: "DB error" });
    }
    res.json(result);
  });
});

// POST employee
app.post("/employees", (req, res) => {
  const { name, phone } = req.body;

  db.query(
    "INSERT INTO employees (name, phone) VALUES (?, ?)",
    [name, phone],
    (err) => {
      if (err) {
        console.log("❌ DB INSERT ERROR:", err.message);
        return res.status(500).json({ error: "Insert failed" });
      }
      res.json({ message: "Employee added" });
    }
  );
});

/* =========================================
   🚀 SERVER START
========================================= */
app.listen(process.env.PORT, () => {
  console.log(`🚀 Express running on port ${process.env.PORT}`);
});




FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]




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
