-- Totalt antal mätningar (räknar hur många mätningar som finns i tabellen 'measurements')
SELECT COUNT(*) FROM measurements;


-- Medeltemperatur (räknar ut den genomsnittliga temperaturen i tabellen 'measurements')
SELECT AVG(temperature) FROM measurements;


-- Hämtar alla mätningar som skapats under de senaste 24 timmarna
SELECT * FROM measurements
WHERE created_at >= NOW() - INTERVAL '24 hours';