-- QUEM FAZ | 01 | BRONZE (Databricks SQL)
-- Execute somente depois do upload dos arquivos nos Volumes.
-- Idempotente por arquivo: COPY INTO sem FORCE não reprocessa arquivos já ingeridos.
-- Os quatro arquivos abaixo já foram coletados pelo Airflow em 10 e 11/11/2026.

CREATE TABLE IF NOT EXISTS workspace.quem_faz.bronze_pedidos;
CREATE TABLE IF NOT EXISTS workspace.quem_faz.bronze_distritos;

-- LOTE 01 — 10/11/2026
COPY INTO workspace.quem_faz.bronze_pedidos
FROM '/Volumes/workspace/quem_faz/volume_entrada/lote_01/'
FILEFORMAT = JSON
FILES = ('pedidos_2026-11-10.jsonl')
FORMAT_OPTIONS ('inferSchema' = 'true', 'multiLine' = 'false')
COPY_OPTIONS ('mergeSchema' = 'true');

COPY INTO workspace.quem_faz.bronze_distritos
FROM '/Volumes/workspace/quem_faz/volume_entrada/lote_01/'
FILEFORMAT = JSON
FILES = ('distritos_ibge_2026-11-10.jsonl')
FORMAT_OPTIONS ('inferSchema' = 'true', 'multiLine' = 'false')
COPY_OPTIONS ('mergeSchema' = 'true');

-- LOTE 02 — 11/11/2026
COPY INTO workspace.quem_faz.bronze_pedidos
FROM '/Volumes/workspace/quem_faz/volume_entrada/lote_02/'
FILEFORMAT = JSON
FILES = ('pedidos_2026-11-11.jsonl')
FORMAT_OPTIONS ('inferSchema' = 'true', 'multiLine' = 'false')
COPY_OPTIONS ('mergeSchema' = 'true');

COPY INTO workspace.quem_faz.bronze_distritos
FROM '/Volumes/workspace/quem_faz/volume_entrada/lote_02/'
FILEFORMAT = JSON
FILES = ('distritos_ibge_2026-11-11.jsonl')
FORMAT_OPTIONS ('inferSchema' = 'true', 'multiLine' = 'false')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Conferência final do ambiente demonstrado
SELECT 'pedidos' AS fonte, COUNT(*) AS registros, COUNT(DISTINCT pedido_id) AS chaves_unicas
FROM workspace.quem_faz.bronze_pedidos
UNION ALL
SELECT 'distritos_ibge', COUNT(*), COUNT(DISTINCT id)
FROM workspace.quem_faz.bronze_distritos;
-- Resultado observado: pedidos = 200 / 200; IBGE = 192 / 96.
