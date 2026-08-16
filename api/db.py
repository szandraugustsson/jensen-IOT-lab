import os
from decimal import Decimal
import psycopg2
import psycopg2.extras

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "jensen_iot"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )

def _json_ready(row):
    if row is None:
        return None
    result = dict(row)
    for key in ("temperature", "humidity"):
        if isinstance(result.get(key), Decimal):
            result[key] = float(result[key])
    if result.get("created_at") is not None:
        result["created_at"] = result["created_at"].isoformat()
    return result

def get_devices():
    query = """
        SELECT id, device_id, location, device_type
        FROM devices
        ORDER BY device_id;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]

def get_measurements():
    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        ORDER BY created_at DESC
        LIMIT 100;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return [_json_ready(row) for row in cur.fetchall()]

def device_exists(device_id):
    # TODO M1:
    # Kontrollera om 'device_id' finns i tabellen 'devices'.
    # Returnera True eller False.

    # returnerar '1' för de rader som uppfyller WHERE villkoret
    # %s är platshållare för värdet

    query = """
        SELECT 1
        FROM devices
        WHERE device_id = %s;
    """
    # anslut till PostgreSQL databasen, spara anslutningen i 'conn'
    with get_connection() as conn:
    # skapa en cursor för att skicka SQL frågan till databasen
        # conn = kontakten med databasen
        # cur  = verktyget vi använder för att skicka SQL
        with conn.cursor() as cur:
    # kör SQL frågan och använd device_id som värdet för '%s'
            cur.execute(query, (device_id,))
    # hämta den första raden av resultatet
            row = cur.fetchone()
    # om en rad finns returnera True, annars False
            return row is not None
    
def get_latest_measurement(device_id):
    # TODO M1:docker compose exec api python -m pytest -q
    # Implementera senaste mätvärdet för en sensor.

    # SQL frågan letar efter rätt sensor
    # sorterar mätningarna från nyast till äldst
    # tar den senaste

    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        WHERE device_id = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """
    with get_connection() as conn:
        # 'RealDictCursor' gör att resultatet kommer tillbaka som en dictionary
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (device_id,))
            # gör raden kompatibel med JSON
            return _json_ready(cur.fetchone())

def get_measurements_for_device(device_id):
    # TODO M1:
    # Implementera historik för en sensor.

    query = """
        SELECT id, device_id, temperature, humidity, battery, created_at
        FROM measurements
        WHERE device_id = %s
        ORDER BY created_at DESC
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (device_id,))
            return [_json_ready(row) for row in cur.fetchall()]

def insert_measurement(data):
    # TODO M1:
    # Spara ett validerat mätvärde i PostgreSQL.

    query = """
        INSERT INTO measurements
        (device_id, temperature, humidity, battery)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            values = (data["deviceId"], data["temperature"], data["humidity"], data["battery"])
            cur.execute(query, values)
            return _json_ready(cur.fetchone())