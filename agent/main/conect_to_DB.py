
import psycopg2

def conect_to_DB():
  try:
    # Connect to PostgreSQL
    connection = psycopg2.connect(
       dbname="Evolution",
       user="ev",
       password="Temp@123",
       host="192.168.4.51",  
       port="5432" 
    )
    print("Connection established successfully!")
    return connection
  except Exception as e:
    print(f"Error: {e}")
    return None

 