-- ── pig_processing/incidentes.pig ──

-- 1) Indicamos que el filesystem por defecto es HDFS
SET fs.defaultFS hdfs://localhost:9000;

-- 2) Cargar el CSV limpio desde HDFS
--    Asegúrate de haber hecho antes:
--      hdfs dfs -mkdir -p /incidentes
--      hdfs dfs -put -f /data/clean_incidents.csv /incidentes/clean_incidents.csv

incidentes_raw = LOAD '/incidentes/clean_incidents.csv'
    USING PigStorage(',')
    AS (
      type:chararray, 
      location:chararray, 
      timestamp:chararray, 
      description:chararray, 
      comuna:chararray
    );

-- 3) Filtrar encabezado (el CSV incluye "type,location,..." en la primera fila)
encabezado = FILTER incidentes_raw BY type == 'type';
datos_sin_encabezado = FILTER incidentes_raw BY type != 'type';

-- 4) Separar latitud y longitud (location = "lat,lon")
separado = FOREACH datos_sin_encabezado GENERATE 
    type, 
    FLATTEN(STRSPLIT(location, ',')) AS (lat:chararray, lon:chararray), 
    timestamp, 
    comuna;

-- 5) Agrupar por comuna y tipo de incidente
agrupado = GROUP separado BY (comuna, type);

-- 6) Contar ocurrencias de cada par (comuna, tipo)
conteo = FOREACH agrupado GENERATE 
    FLATTEN(group) AS (comuna, tipo), 
    COUNT(separado) AS cantidad;

-- 7) Guardar resultados en HDFS (no file:/)
STORE conteo INTO '/incidentes/output/conteo_por_comuna_tipo' USING PigStorage(',');
