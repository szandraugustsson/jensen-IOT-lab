**1. Varför ska sensorerna kommunicera med ett API i stället för direkt med PostgreSQL?**

Sensorerna ska kommunicera med ett API eftersom API:t kan kontrollera om mätvärden är korrekta innan de sparas. Sensorerna behöver inte veta något om databasen, det räcker att de känner till API:t.

**2. Varför ska felaktig sensordata stoppas innan den sparas?**

Sensordata ska stoppas innan den sparas eftersom man annars kan få problem senare när man behöver använda mätningarna. I vår labb kan till exempel ett felaktigt temperaturvärde göra att medeltemperaturen blir fel och påverkar även statistiken. Det är därför API kontrollerar datan innan den sparas i databasen.

**3. Varför passar PostgreSQL för historiska mätvärden?**

Historik lagras i PostgreSQL eftersom alla mätningar behöver finnas kvar permanent och kunna hämtas när som helst. PostgreSQL passar bra eftersom man kan lagra många mätningar och sedan söka och sortera dem, till exempel efter sensor eller datum. I vår labb kan man till exempel hämta hela historiken för en sensor och se de senaste mätningarna.

**4. Vad händer med lösningen om Redis försvinner?**

Om Redis försvinner försvinner de senaste mätvärdena som låg i cachen. Historiken finns fortfarande kvar i PostgreSQL, och API:t kan hämta den senaste mätningen från PostgreSQL och lägga tillbaka den i Redis när cachen fungerar igen.

**5. Vad händer med lösningen om PostgreSQL försvinner?**
 
 Om PostgreSQL försvinner kan man inte hämta historiken och spara nya mätningar. Redis har bara den senaste mätningen och kan därför inte ersätta PostgreSQL och återställa hela databasen.

**6. Varför används Docker Compose lokalt?**

Docker Compose används lokalt för att man ska kunna köra alla delar av projektet tillsammans. I vår labb startar Docker Compose API, PostgreSQL, Redis och simulatorn och gör så att de kan kommunicera med varandra. Då behöver man inte starta och konfigurera varje del separat på datorn, och alla som jobbar med projektet kan använda samma konfiguration.

**7. Vad automatiserar din CI-pipeline?**

CI-pipelinen gör automatiskt flera steg som man annars hade behövt göra själv. När man pushar kod eller gör en pull request startar pipelinen. Den hämtar först koden med 'actions/checkout@v4', installerar Python 3.12 och paketen från 'api/requirements.txt'. Sedan kör den testerna med 'python -m pytest tests -q' och bygger API:ts Docker-image med 'docker build -t jensen-iot-api:ci ./api'.

Skillnaden mot att köra testerna själv i terminalen är att CI gör detta automatiskt på GitHub och i en annan miljö. Då behöver man inte komma ihåg att köra testerna varje gång man pushar ny kod.

**8. Vad observerade du när du tog bort en Kubernetes Pod?**

När jag tog bort en Kubernetes Pod såg jag att den terminerades. Deploymenten hade tre repliker som önskat tillstånd, så den upptäckte att det bara fanns två kvar och skapade automatiskt en ny Pod. Det är self-healing, eftersom Kubernetes försöker återställa det önskade tillståndet utan att man behöver skapa en ny Pod manuellt.

**9. Varför kan flera repliker ge högre tillgänglighet?**

Flera repliker kan ge högre tillgänglighet eftersom en Pod kan sluta fungera eller få problem. Om man bara har en Pod kan tjänsten sluta fungera. Med flera Pods kan de andra fortsätta att svara medan en Pod startas om eller ersätts. Det minskar risken för downtime.

**10. När hade Kubernetes varit overkill för en lösning?**

Kubernetes kan vara overkill för en enkel applikation, till exempel en liten webbsida med få användare där det inte finns stort behov av skalning eller hög tillgänglighet. Kubernetes är mer komplicerat och kräver mer resurser. I vår labb hade Docker Compose räckt bra för att köra hela lösningen.
