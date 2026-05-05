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
