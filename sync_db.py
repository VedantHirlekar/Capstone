import os
import subprocess
import pymysql

# ======================
# CONFIGURATION
# ======================
PRIMARY_HOST = "capstonedb.cf26uges24cv.eu-north-1.rds.amazonaws.com"
SECONDARY_HOST = "secondary-capstone.cf26uges24cv.eu-north-1.rds.amazonaws.com"

DB_USER = "admin"
DB_PASS = "vedanthirlekar"
DB_NAME = "capstone_db"

DUMP_FILE = "/tmp/db_dump.sql"

# ======================
# STEP 1: EXPORT PRIMARY DB
# ======================
def export_db():
    print("Exporting primary DB...")

    command = f"""
    mysqldump -h {PRIMARY_HOST} -u {DB_USER} -p{DB_PASS} {DB_NAME} > {DUMP_FILE}
    """

    os.system(command)
    print("Export completed")

# ======================
# STEP 2: IMPORT INTO SECONDARY DB
# ======================
def import_db():
    print("Importing to secondary DB...")

    command = f"""
    mysql -h {SECONDARY_HOST} -u {DB_USER} -p{DB_PASS} {DB_NAME} < {DUMP_FILE}
    """

    os.system(command)
    print("Import completed")

# ======================
# RUN SYNC
# ======================
if __name__ == "__main__":
    export_db()
    import_db()
    print("DB Sync Completed Successfully")
