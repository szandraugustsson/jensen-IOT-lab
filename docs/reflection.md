# Reflektionsdokument – obligatorisk leverabel

1. Varför ska sensorerna kommunicera med ett API i stället för direkt med PostgreSQL?
2. Varför ska felaktig sensordata stoppas innan den sparas?
3. Varför passar PostgreSQL för historiska mätvärden?
4. Vad händer med lösningen om Redis försvinner?
5. Vad händer med lösningen om PostgreSQL försvinner?
6. Varför används Docker Compose lokalt?
7. Vad automatiserar din CI-pipeline?
8. Vad observerade du när du tog bort en Kubernetes Pod?
9. Varför kan flera repliker ge högre tillgänglighet?
10. När hade Kubernetes varit overkill för en lösning?

M2/2. Förklara varför historik lagras i PostgreSQL medan senaste mätningen lämpar sig för cache, och vad som händer om respektive tjänst försvinner.

Historik lagras i PostgreSQL eftersom alla mätningar behöver finnas kvar permanent och kunna hämtas när som helst. Om Redis försvinner finns historiken fortfarande kvar i PostgreSQL, och API:t kan hämta den senaste mätningen från PostgreSQL igen. API:t behöver ofta bara den senaste mätningen, och eftersom Redis lagrar data i minnet går det snabbare att hämta den därifrån än att fråga PostgreSQL. Om PostgreSQL försvinner kan man inte hämta historiken och spara nya mätningar.
