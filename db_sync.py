import pymysql

PRIMARY = {
    "host": "capstonedb.cf26uges24cv.eu-north-1.rds.amazonaws.com",
    "user": "admin",
    "password": "vedanthirlekar",
    "database": "capstone_db"
}

SECONDARY = {
    "host": "secondary-capstonedb.cf26uges24cv.eu-north-1.rds.amazonaws.com",
    "user": "admin",
    "password": "vedanthirlekar",
    "database": "secondary_capstonedb"
}

def get_connection(config):
    return pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

# 🔹 Fetch from primary
def fetch_data():
    conn = get_connection(PRIMARY)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, phone, created_at FROM employees")
    rows = cursor.fetchall()

    conn.close()
    return rows

# 🔹 Sync to secondary
def sync_data(rows):
    conn = get_connection(SECONDARY)
    cursor = conn.cursor()

    for row in rows:
        query = """
        INSERT INTO employees (id, name, phone, created_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            phone = VALUES(phone),
            created_at = VALUES(created_at)
        """

        cursor.execute(query, (
            row["id"],
            row["name"],
            row["phone"],
            row["created_at"]
        ))

    conn.commit()
    conn.close()
    print("✔ Sync completed successfully")

if __name__ == "__main__":
    print("🚀 Starting sync...")
    data = fetch_data()
    sync_data(data)
