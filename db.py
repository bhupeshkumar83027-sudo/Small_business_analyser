import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="host.docker.internal",
        user="root",
        password="Bhupesh@83027",
        database="business_ai"
    )

