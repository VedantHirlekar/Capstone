from fastapi import FastAPI, Request
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import time
import os
import psutil
from datetime import datetime
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
    
    # Track request count for metrics
    if not hasattr(app, "request_count"):
        app.request_count = 0
    app.request_count += 1

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

# Database connection pool (improved for health checks)
db_connection = None

def get_connection():
    global db_connection
    try:
        if db_connection is None or not db_connection.is_connected():
            db_connection = mysql.connector.connect(**DB_CONFIG)
            print("✅ FastAPI connected to DB")
        return db_connection
    except Exception as e:
        print("❌ DB connection error:", e)
        raise e

# ============================================
# 🏥 HEALTH CHECK ENDPOINT (NEW)
# ============================================
@app.get("/health")
async def health_check():
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "fastapi-app",
        "version": "1.0.0",
        "uptime_seconds": time.time() - app.start_time if hasattr(app, "start_time") else 0,
        "checks": {
            "database": "unknown",
            "memory": {
                "usage_percent": psutil.virtual_memory().percent,
                "available_mb": psutil.virtual_memory().available // (1024 * 1024),
                "used_mb": psutil.virtual_memory().used // (1024 * 1024)
            },
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count()
            }
        },
        "request_stats": {
            "total_requests": getattr(app, "request_count", 0)
        }
    }
    
    # Check database connectivity
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        health_info["checks"]["database"] = "connected"
    except Exception as e:
        health_info["checks"]["database"] = "disconnected"
        health_info["status"] = "degraded"
        health_info["error"] = str(e)
        print(f"⚠️ Health check - DB connection failed: {e}")
    
    # Set status code based on health
    status_code = 200 if health_info["status"] == "healthy" else 503
    return health_info, status_code

# ============================================
# 📊 METRICS ENDPOINT for Prometheus (OPTIONAL)
# ============================================
@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, REGISTRY, Counter, Histogram, Gauge
    
    # Define metrics if not already defined
    if not hasattr(app, "metrics_initialized"):
        app.request_counter = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
        app.request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
        app.active_connections = Gauge('active_connections', 'Active connections')
        app.metrics_initialized = True
    
    # Update metrics
    app.active_connections.set(len(app.state.__dict__.get("connections", [])))
    
    return generate_latest(REGISTRY)

# Store start time on app startup
@app.on_event("startup")
async def startup_event():
    app.start_time = time.time()
    print("🚀 FastAPI application started")
    print(f"🏥 Health endpoint available at /health")
    print(f"📊 Metrics endpoint available at /metrics")
    
    # Initialize DB connection
    try:
        get_connection()
    except Exception as e:
        print(f"⚠️ Initial DB connection failed: {e}")

# ============================================
# ORIGINAL ROUTES
# ============================================

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

# Root endpoint (optional)
@app.get("/")
async def root():
    return {
        "message": "FastAPI Employee Service",
        "service": "fastapi-app",
        "endpoints": ["/employees", "/health", "/metrics"]
    }
