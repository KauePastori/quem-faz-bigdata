-- QUEM FAZ | 03 | GOLD (modelo dimensional)
-- Usa dados fictícios tratados da Silver e distritos reais do IBGE.
-- CREATE OR REPLACE recria as tabelas analíticas; não rode se houver edição manual nelas.

CREATE OR REPLACE TABLE workspace.quem_faz.gold_dim_categoria
USING DELTA AS
SELECT categoria_id,
       MAX(TRIM(categoria_nome)) AS categoria_nome
FROM workspace.quem_faz.silver_pedidos
WHERE categoria_id IS NOT NULL
  AND categoria_nome IS NOT NULL
  AND TRIM(categoria_nome) <> ''
GROUP BY categoria_id;

CREATE OR REPLACE TABLE workspace.quem_faz.gold_dim_distrito
USING DELTA AS
SELECT distrito_id, distrito_nome, distrito_nome_normalizado
FROM workspace.quem_faz.silver_distritos
WHERE distrito_id IS NOT NULL AND distrito_nome IS NOT NULL;

CREATE OR REPLACE TABLE workspace.quem_faz.gold_fato_pedidos
USING DELTA AS
SELECT
    SHA2(p.pedido_id, 256) AS pedido_hash,
    p.categoria_id,
    p.distrito_id,
    CAST(p.criado_em AS DATE) AS data_pedido,
    p.caminho_contratacao,
    p.status,
    p.quantidade_propostas,
    1 AS quantidade_pedidos,
    CASE WHEN p.quantidade_propostas > 0 THEN 1 ELSE 0 END AS recebeu_proposta,
    CASE WHEN p.status IN ('contratado','concluido') THEN 1 ELSE 0 END AS teve_contratacao,
    CASE WHEN p.concluido = TRUE THEN 1 ELSE 0 END AS servico_concluido,
    p.simulado
FROM workspace.quem_faz.silver_pedidos p;

-- Integridade dimensional
SELECT COUNT(*) AS total_pedidos,
       COUNT(DISTINCT f.pedido_hash) AS pedidos_unicos,
       COUNT_IF(c.categoria_id IS NULL) AS categorias_sem_correspondencia,
       COUNT_IF(d.distrito_id IS NULL) AS distritos_sem_correspondencia,
       SUM(f.quantidade_pedidos) AS total_solicitacoes,
       COUNT_IF(f.servico_concluido = 1 AND f.teve_contratacao <> 1)
           AS conclusoes_inconsistentes
FROM workspace.quem_faz.gold_fato_pedidos f
LEFT JOIN workspace.quem_faz.gold_dim_categoria c ON f.categoria_id = c.categoria_id
LEFT JOIN workspace.quem_faz.gold_dim_distrito d ON f.distrito_id = d.distrito_id;
-- Resultado observado: 200 pedidos, 200 hashes únicos, demais verificações = 0, 200 solicitações.
