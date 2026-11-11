-- QUEM FAZ | 02 | SILVER (Databricks SQL)
-- Reexecutável: aplica MERGE sem inserir novas linhas para chaves existentes.

CREATE TABLE IF NOT EXISTS workspace.quem_faz.silver_distritos (
    distrito_id BIGINT,
    distrito_nome STRING,
    distrito_nome_normalizado STRING
) USING DELTA;

MERGE INTO workspace.quem_faz.silver_distritos AS destino
USING (
    SELECT CAST(id AS BIGINT) AS distrito_id,
           TRIM(nome) AS distrito_nome,
           UPPER(TRIM(nome)) AS distrito_nome_normalizado
    FROM (
        SELECT id, nome,
               ROW_NUMBER() OVER (PARTITION BY id ORDER BY nome) AS rn
        FROM workspace.quem_faz.bronze_distritos
        WHERE id IS NOT NULL AND nome IS NOT NULL AND TRIM(nome) <> ''
    ) base
    WHERE rn = 1
) AS origem
ON destino.distrito_id = origem.distrito_id
WHEN MATCHED AND (
    destino.distrito_nome <> origem.distrito_nome OR
    destino.distrito_nome_normalizado <> origem.distrito_nome_normalizado
) THEN UPDATE SET
    distrito_nome = origem.distrito_nome,
    distrito_nome_normalizado = origem.distrito_nome_normalizado
WHEN NOT MATCHED THEN INSERT (distrito_id, distrito_nome, distrito_nome_normalizado)
VALUES (origem.distrito_id, origem.distrito_nome, origem.distrito_nome_normalizado);

CREATE TABLE IF NOT EXISTS workspace.quem_faz.silver_pedidos (
    pedido_id STRING,
    criado_em TIMESTAMP,
    municipio_ibge_id BIGINT,
    distrito_id BIGINT,
    distrito_nome STRING,
    categoria_id INT,
    categoria_nome STRING,
    caminho_contratacao STRING,
    status STRING,
    quantidade_propostas INT,
    concluido BOOLEAN,
    origem STRING,
    simulado BOOLEAN
) USING DELTA;

MERGE INTO workspace.quem_faz.silver_pedidos AS destino
USING (
    SELECT
        TRIM(p.pedido_id) AS pedido_id,
        TRY_TO_TIMESTAMP(p.criado_em) AS criado_em,
        TRY_CAST(p.municipio_ibge_id AS BIGINT) AS municipio_ibge_id,
        d.distrito_id, d.distrito_nome,
        TRY_CAST(p.categoria_id AS INT) AS categoria_id,
        TRIM(p.categoria_nome) AS categoria_nome,
        p.caminho_contratacao, p.status,
        TRY_CAST(p.quantidade_propostas AS INT) AS quantidade_propostas,
        TRY_CAST(p.concluido AS BOOLEAN) AS concluido,
        p.origem, TRY_CAST(p.simulado AS BOOLEAN) AS simulado
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY pedido_id ORDER BY criado_em DESC) AS rn
        FROM workspace.quem_faz.bronze_pedidos
    ) p
    INNER JOIN workspace.quem_faz.silver_distritos d
        ON UPPER(TRIM(p.distrito_nome)) = d.distrito_nome_normalizado
    WHERE p.rn = 1
      AND p.pedido_id IS NOT NULL AND TRIM(p.pedido_id) <> ''
      AND TRY_TO_TIMESTAMP(p.criado_em) IS NOT NULL
      AND TRY_CAST(p.municipio_ibge_id AS BIGINT) = 3550308
      AND TRY_CAST(p.categoria_id AS INT) IS NOT NULL
      AND TRIM(COALESCE(p.categoria_nome, '')) <> ''
      AND p.status IN ('publicado','com_propostas','contratado','concluido','cancelado')
      AND TRY_CAST(p.quantidade_propostas AS INT) >= 0
      AND NOT (p.status = 'publicado' AND TRY_CAST(p.quantidade_propostas AS INT) <> 0)
      AND NOT (p.status IN ('com_propostas','contratado','concluido')
               AND TRY_CAST(p.quantidade_propostas AS INT) < 1)
      AND TRY_CAST(p.concluido AS BOOLEAN) = (p.status = 'concluido')
      AND p.caminho_contratacao IN ('explorar_categoria','publicar_pedido')
      AND TRY_CAST(p.simulado AS BOOLEAN) = TRUE
) AS origem
ON destino.pedido_id = origem.pedido_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

SELECT 'silver_pedidos' AS tabela,
       COUNT(*) AS total_registros, COUNT(DISTINCT pedido_id) AS chaves_unicas
FROM workspace.quem_faz.silver_pedidos
UNION ALL
SELECT 'silver_distritos', COUNT(*), COUNT(DISTINCT distrito_id)
FROM workspace.quem_faz.silver_distritos;
-- Resultado observado: silver_pedidos 200/200; silver_distritos 96/96.
