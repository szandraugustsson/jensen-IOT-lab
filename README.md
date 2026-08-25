# Jensen IoT Platform

En IoT-plattform för att ta emot, validera, lagra och läsa sensormätningar.

Systemet använder Docker Compose för att köra följande tjänster:

* **API** – Flask-applikation som hanterar REST-endpoints, validering och kommunikation med databasen och Redis
* **PostgreSQL** – permanent lagring av sensorer och mätningar
* **Redis** – cache för den senaste mätningen kopplad till varje sensor
* **Simulator** – simulerar tre IoT-sensorer och skickar mätningar till API:t

Projektet innehåller även:

* **CI** – GitHub Actions som kör tester och bygger API:ts Docker-image vid push och pull request
* **Kubernetes** – en introducerande Kubernetes-konfiguration för att köra API:t med Minikube

Projektets arkitektur beskrivs separat i [`docs/architecture.md`](docs/architecture.md).

## Förutsättningar

Installera innan du börjar:

* Git och ett GitHub-konto
* Docker Desktop (Windows/macOS) eller Docker Engine med Docker Compose-plugin (Linux)
* En valfri kodeditor, exempelvis Visual Studio Code
* kubectl och Minikube för Kubernetes-delen

Python behöver inte installeras lokalt eftersom Python och projektets beroenden finns i containrarna. Kontrollera installationerna i PowerShell, Terminal eller ett Linux-skal:

```bash
git --version
docker --version
docker compose version
kubectl version --client
minikube version
```

## Bygga och starta

### 1. Klona repositoryt och gå till projektets rot:

```bash
git clone <REPOSITORY-URL>
cd jensen-IOT-lab
```

### 2. Kontrollera Docker

Starta Docker Desktop på Windows/macOS eller Docker Engine på Linux. Kontrollera sedan installationen:

```bash
docker info
docker compose version
```

### 3. Bygg och starta miljön:

```bash
docker compose up --build -d
docker compose ps
```

`docker compose ps` ska visa tjänsterna `api`, `simulator`, `db` och `redis`. Databasen ska efter en kort stund visa `healthy`. Om någon tjänst fortfarande startar, vänta några sekunder och kör statuskommandot igen.

## API-endpoints

### `GET /`

Visar API:ets startsida.

```text
http://localhost:5001/
```

### `GET /health`

Kontrollerar API:ets status.

```text
http://localhost:5001/health
```

### `GET /devices`

Returnerar registrerade sensorer från PostgreSQL.

```text
http://localhost:5001/devices
```

### `GET /measurements`

Returnerar de senaste mätningarna från PostgreSQL.

```text
http://localhost:5001/measurements
```

### `GET /devices/<device_id>/latest`

Returnerar den senaste mätningen för en sensor.

Exempel:

```text
http://localhost:5001/devices/sensor-001/latest
```

Returnerar `404` om sensorn inte finns eller om sensorn saknar mätningar.

Endpointen använder Redis som cache. Vid cache hit returneras mätningen direkt från Redis. Vid cache miss hämtas mätningen från PostgreSQL och sparas i Redis.

### `GET /devices/<device_id>/measurements`

Returnerar historiken för en sensor.

Exempel:

```text
http://localhost:5001/devices/sensor-001/measurements
```

En känd sensor utan mätningar returnerar:

```json
[]
```

### `POST /measurements`

Tar emot en ny sensormätning.

Exempel:

```json
{
  "deviceId": "sensor-001",
  "temperature": 21.5,
  "humidity": 45.0,
  "battery": 90
}
```
Vid en giltig mätning returneras `201`.
Vid valideringsfel eller om `deviceId` inte finns returneras `400`.

## Kontroll och testning

### PostgreSQL

```bash
docker compose exec db psql -U student -d jensen_iot
```

SQL-frågor för att kontrollera databasen finns i:

```text
database/sql_queries.sql
```
### Redis cache miss

Töm Redis:

```bash
docker compose exec redis redis-cli FLUSHDB
```

Öppna:

http://localhost:5001/devices/sensor-001/latest

Kontrollera att mätningen har sparats i Redis:

```bash
docker compose exec redis redis-cli KEYS 'latest:*'
```

## Tester

Kör testerna med:

```bash
docker compose exec api python -m pytest -q
```

Efter kodändringar kan hela API-imagen byggas om och testerna köras igen:

```bash
docker compose up --build -d
docker compose exec api python -m pytest -q
```

## Loggar

API:

```bash
docker compose logs --tail=50 api
```

Simulator:

```bash
docker compose logs --tail=50 simulator
```

Följ simulatorns loggar kontinuerligt:

```bash
docker compose logs -f simulator
```

Alla tjänster:

```bash
docker compose logs --tail=50
```

## Stoppa miljön

```bash
docker compose down
```

Databasen sparas i en Docker-volym och finns kvar till nästa start. Använd endast följande kommando om du avsiktligt vill radera all lokal databasdata för labben:

```text
docker compose down -v
```

## CI-pipeline

CI-workflowen finns i:

```text
.github/workflows/ci.yml
```
Workflowen körs vid push och pull request och:

- installerar projektets Python-beroenden
- kör testerna
- bygger API:ts Docker-image

CI-resultatet kan kontrolleras under Actions på GitHub.

Testerna kan även köras lokalt med:

```bash
docker compose exec api python -m pytest -q
```

## Kubernetes

Kubernetes-delen körs med Minikube:

```bash
minikube start --driver=docker
minikube status
minikube image build -t jensen-iot-api:lab ./api
```

Distribuera API:t:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Kontrollera Pods:

```bash
kubectl get pods
```

Nå tjänsten:

```bash
minikube service jensen-iot-api
```

Kubernetes-delen används för att testa:

- flera repliker av API:t
- self-healing när en Pod tas bort
- scaling genom att ändra antalet repliker

Skala API:t till fem repliker:

```bash
kubectl scale deployment jensen-iot-api --replicas=5
kubectl get pods
```

Skala tillbaka till tre:

```bash
kubectl scale deployment jensen-iot-api --replicas=3
kubectl get pods
```

När Kubernetes-testet är klart:

```bash
minikube stop
```

## Kända begränsningar

* Simulatorn använder genererade mätvärden i stället för data från riktiga IoT-sensorer.
* PostgreSQL använder `student` som standardanvändare och `student` som standardlösenord för anslutning.
* API:t kontrollerar att `deviceId` finns i databasen, men verifierar inte att den som skickar mätningen faktiskt är den registrerade sensorn.
* Om Redis inte är tillgängligt misslyckas API-anrop som hämtar den senaste mätningen.

## Dokumentation

* [`docs/architecture.md`](docs/architecture.md)
* [`docs/reflection.md`](docs/reflection.md)
* [`database/sql_queries.sql`](database/sql_queries.sql)

## Fördjupning

### Extra SQL-frågor

Projektet innehåller två extra SQL-frågor som fördjupning. 

Den första frågan hittar sensorn som har högst medeltemperatur. AVG räknar ut medeltemperaturen och GROUP BY grupperar mätningarna efter sensor (`device_id`). DESC sorterar från högst till lägst och LIMIT 1 visar bara den sensor som har högst medeltemperatur.

Den andra frågan hittar sensorn som har flest mätningar. COUNT räknar hur många mätningar varje sensor har och GROUP BY grupperar mätningarna efter sensor (`device_id`). DESC sorterar från flest till minst och LIMIT 1 visar den sensor som har flest mätningar.

### Automatiserade integrationstester

Projektet har även tre automatiserade integrationstester.
Testerna använder Flask Test Client och pytest för att skicka HTTP-anrop till API:ts endpoints.

Testerna kontrollerar:

- att en giltig mätning kan skickas med `POST /measurements` och ger `201`
- att en ogiltig mätning nekas med `POST /measurements` och ger `400`
- att `GET /devices` fungerar och ger `200`

Testerna finns i:

```text
api/tests/test_integration.py
```

Testerna körs med:

```bash
docker compose exec api python -m pytest -q
```

Integrationstesterna använder PostgreSQL och Redis. Därför har även CI konfigurerats med dessa tjänster, så att testerna kan köras både lokalt och i GitHub Actions.