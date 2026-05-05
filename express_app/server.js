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
   🏥 HEALTH CHECK ENDPOINT (NEW)
========================================= */
app.get("/health", async (req, res) => {
  const healthCheck = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    service: "express-app",
    version: "1.0.0",
    uptime: process.uptime(),
    checks: {
      database: "unknown",
      memory: {
        usage: process.memoryUsage(),
        heapUsed: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(process.memoryUsage().heapTotal / 1024 / 1024)} MB`
      }
    }
  };

  // Check database connectivity
  try {
    await new Promise((resolve, reject) => {
      db.query("SELECT 1", (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
    healthCheck.checks.database = "connected";
  } catch (err) {
    healthCheck.checks.database = "disconnected";
    healthCheck.status = "degraded";
    console.log("⚠️ Health check - DB connection failed:", err.message);
  }

  // Send response with appropriate status code
  const statusCode = healthCheck.status === "healthy" ? 200 : 503;
  res.status(statusCode).json(healthCheck);
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
   📊 METRICS ENDPOINT for Prometheus (OPTIONAL)
========================================= */
app.get("/metrics", (req, res) => {
  const metrics = {
    nodejs_version: process.version,
    platform: process.platform,
    memory_usage_bytes: process.memoryUsage().heapUsed,
    uptime_seconds: process.uptime(),
    total_requests: global.requestCount || 0
  };
  res.json(metrics);
});

/* =========================================
   🚀 SERVER START
========================================= */
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🚀 Express running on port ${PORT}`);
  console.log(`🏥 Health endpoint available at http://localhost:${PORT}/health`);
  console.log(`📊 Metrics endpoint available at http://localhost:${PORT}/metrics`);
});
