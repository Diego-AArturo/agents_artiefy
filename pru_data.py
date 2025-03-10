import psycopg2

# Configura tu conexión a PostgreSQL
DB_URI = "postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

try:
    conn = psycopg2.connect(DB_URI)
    cursor = conn.cursor()

    # Verificar si la tabla `lessons` tiene datos
    cursor.execute("SELECT * FROM lessons LIMIT 5;")
    rows = cursor.fetchall()

    print("Datos de lessons:")
    for row in rows:
        print(row)

    # Verificar si la tabla `courses` tiene datos
    cursor.execute("SELECT * FROM courses LIMIT 5;")
    rows = cursor.fetchall()

    print("Datos de courses:")
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print("Error al conectar con la base de datos:", e)
