import json
import os
import redis

client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


def get_latest_from_cache(device_id):
    # TODO M2:
    # Läs senaste mätvärdet från Redis.

    # skapa en nyckel för sensorns senaste mätning
    cache_key = f"latest:{device_id}"
    # hämta den senaste mätningen från Redis
    cached_measurement = client.get(cache_key)
    # om mätningen inte finns i Redis returnera None
    if cached_measurement is None:
        return None
    # gör om JSON från Redis till Python data
    return json.loads(cached_measurement)


def set_latest_in_cache(device_id, latest_measurement):
    # TODO M2:
    # spara senaste mätvärdet i Redis.

    # skapa samma nyckel som används för att hämta mätningen
    cache_key = f"latest:{device_id}"
    # spara mätningen som JSON i Redis med en nyckel för att kunna hitta den senare
    client.set(cache_key, json.dumps(latest_measurement))
